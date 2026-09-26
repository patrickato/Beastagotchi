from __future__ import annotations

import sqlite3
import threading
from typing import Any

from .db import Store


class _ThreadBoundConnectionProxy:
    """Resolve SQLite operations against the connection owned by this thread.

    Domain objects in v0.19 commonly cache ``store.conn`` during construction.
    Keeping the cached object as a proxy lets those objects remain shared while
    preserving SQLite's normal same-thread connection rule.
    """

    def __init__(self, store: "ThreadBoundStore") -> None:
        self._store = store

    def _conn(self) -> sqlite3.Connection:
        return self._store._connection()

    def execute(self, *args, **kwargs):
        return self._conn().execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self._conn().executemany(*args, **kwargs)

    def executescript(self, *args, **kwargs):
        return self._conn().executescript(*args, **kwargs)

    def commit(self) -> None:
        self._conn().commit()

    def rollback(self) -> None:
        self._conn().rollback()

    def __enter__(self):
        self._conn().__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        return self._conn().__exit__(exc_type, exc, tb)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn(), name)


class ThreadBoundStore(Store):
    """Store variant with one normal SQLite connection per calling thread.

    Beast Core keeps its event-loop connection. ActionServer worker threads get
    their own ordinary SQLite connections, so ``check_same_thread`` remains at
    SQLite's safe default instead of being disabled globally.

    Existing domain objects may cache ``store.conn``; that attribute is a small
    proxy which resolves to the current thread's connection on every operation.
    """

    def __init__(self, path: str, *, timeout: float = 10.0) -> None:
        self._thread_local = threading.local()
        self._timeout = max(1.0, float(timeout))
        self._conn_proxy = _ThreadBoundConnectionProxy(self)
        super().__init__(path)

    @property
    def conn(self) -> _ThreadBoundConnectionProxy:
        return self._conn_proxy

    @conn.setter
    def conn(self, value: sqlite3.Connection) -> None:
        # Store.__init__ creates the initial/main-thread connection. Preserve it
        # as the current thread's owned connection instead of exposing it directly.
        self._configure(value)
        self._thread_local.connection = value

    def _configure(self, conn: sqlite3.Connection) -> None:
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        # WAL is persistent for the database and materially reduces contention
        # between Core's event-loop connection and short-lived action workers.
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")

    def _connection(self) -> sqlite3.Connection:
        conn = getattr(self._thread_local, "connection", None)
        if conn is None:
            conn = sqlite3.connect(self.path, timeout=self._timeout)
            self._configure(conn)
            self._thread_local.connection = conn
        return conn

    def release_thread_connection(self) -> None:
        """Close only the connection owned by the calling thread."""
        conn = getattr(self._thread_local, "connection", None)
        if conn is None:
            return
        try:
            conn.close()
        finally:
            try:
                del self._thread_local.connection
            except AttributeError:
                pass

    def current_connection_identity(self) -> int:
        """Small diagnostic/testing hook; does not expose the connection itself."""
        return id(self._connection())

    def close(self) -> None:
        self.release_thread_connection()

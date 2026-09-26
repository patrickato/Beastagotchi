from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


TERMINAL_STATES = {
    'committed',
    'rolled_back',
    'cancelled_before_apply',
    'rollback_failed',
    'indeterminate',
    'superseded',
}

_TRANSITIONS = {
    'planned': {'preparing', 'cancelled_before_apply'},
    'preparing': {'prepared', 'cancelled_before_apply', 'indeterminate'},
    'prepared': {'applying', 'cancelled_before_apply'},
    'applying': {'applied', 'rolling_back', 'indeterminate'},
    'applied': {'probation', 'verifying', 'rolling_back'},
    'probation': {'verifying', 'rolling_back'},
    'verifying': {'committing', 'rolling_back'},
    'committing': {'committed', 'rolling_back', 'indeterminate'},
    'rolling_back': {'rolled_back', 'rollback_failed'},
    'committed': set(),
    'rolled_back': set(),
    'cancelled_before_apply': set(),
    'rollback_failed': set(),
    'indeterminate': set(),
    'superseded': set(),
}

_ID_RE = re.compile(r'^[a-z0-9][a-z0-9_.:-]{0,126}$')
_RUN_RE = re.compile(r'^txn-[a-z0-9_.:-]+-[0-9]{8}t[0-9]{6}-[a-f0-9]{8}$')


class TransactionError(RuntimeError):
    pass


class TransactionTransitionError(TransactionError):
    pass


@dataclass(frozen=True)
class TransactionSpec:
    id: str
    adapter: Any
    risk: str = 'C2'
    reversible: bool = True
    probation_required: bool = True
    verification_required: bool = True
    authority: str = 'operator'
    definition_version: str = '1'
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        clean = str(self.id or '').strip()
        if not _ID_RE.fullmatch(clean):
            raise TransactionError(f'invalid transaction spec id: {self.id!r}')
        object.__setattr__(self, 'id', clean)
        if not callable(getattr(self.adapter, 'plan', None)):
            raise TransactionError('transaction adapter must provide plan(context)')
        if not callable(getattr(self.adapter, 'apply', None)):
            raise TransactionError('transaction adapter must provide apply(context)')


@dataclass
class TransactionContext:
    transaction_id: str
    spec: TransactionSpec
    actor: str
    request: dict[str, Any]
    subject: str
    data: dict[str, Any] = field(default_factory=dict)


class FileTransactionJournal:
    """Small durable journal independent from the rich Beast runtime/database.

    JSON-per-run is intentional for the first shared Transaction foundation: it
    survives Core/database trouble, is inspectable from the future Rescue Plane,
    and does not force an ad-hoc SQLite schema mutation before the ordered DB
    migration ladder exists.
    """

    def __init__(
        self,
        root: str | Path = '/var/lib/beastagotchi/transactions',
        *,
        clock=time.time,
    ) -> None:
        self.root = Path(root)
        self.clock = clock

    def _path(self, transaction_id: str) -> Path:
        tid = str(transaction_id or '').strip().lower()
        if not _RUN_RE.fullmatch(tid):
            raise TransactionError('invalid transaction id')
        root = self.root.resolve()
        path = (root / f'{tid}.json').resolve()
        if path.parent != root:
            raise TransactionError('transaction journal path escaped managed root')
        return path

    def _write(self, row: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.root, 0o700)
        except OSError:
            pass
        path = self._path(str(row.get('id') or ''))
        tmp = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
        encoded = (json.dumps(row, indent=2, sort_keys=True, default=str) + '\n').encode('utf-8')
        try:
            with tmp.open('wb') as fh:
                fh.write(encoded)
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(tmp, 0o600)
            os.replace(tmp, path)
        finally:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass

    def create(
        self,
        *,
        transaction_id: str,
        spec: TransactionSpec,
        actor: str,
        request: Mapping[str, Any],
        subject: str,
        plan: Mapping[str, Any],
    ) -> dict[str, Any]:
        now = float(self.clock())
        row = {
            'schema': 1,
            'id': transaction_id,
            'spec_id': spec.id,
            'definition_version': spec.definition_version,
            'actor': str(actor),
            'subject': str(subject),
            'risk': spec.risk,
            'reversible': bool(spec.reversible),
            'authority': spec.authority,
            'request': dict(request),
            'plan': dict(plan),
            'status': 'planned',
            'started_at': now,
            'updated_at': now,
            'stage_results': {},
            'timeline': [
                {'state': 'planned', 'at': now, 'detail': 'transaction journal created'}
            ],
        }
        self._write(row)
        return row

    def get(self, transaction_id: str) -> dict[str, Any]:
        path = self._path(transaction_id)
        try:
            obj = json.loads(path.read_text())
        except FileNotFoundError as exc:
            raise TransactionError('transaction not found') from exc
        except Exception as exc:
            raise TransactionError(f'could not read transaction: {exc}') from exc
        if not isinstance(obj, dict):
            raise TransactionError('transaction journal is not an object')
        return obj

    def transition(
        self,
        transaction_id: str,
        new_state: str,
        *,
        detail: str = '',
        stage_result: Mapping[str, Any] | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        row = self.get(transaction_id)
        current = str(row.get('status') or '')
        new_state = str(new_state or '')
        if new_state not in _TRANSITIONS.get(current, set()):
            raise TransactionTransitionError(f'illegal transaction transition {current}->{new_state}')
        now = float(self.clock())
        row['status'] = new_state
        row['updated_at'] = now
        if new_state in TERMINAL_STATES:
            row['finished_at'] = now
        row.setdefault('timeline', []).append({
            'state': new_state,
            'at': now,
            'detail': str(detail or ''),
        })
        if stage_result is not None:
            row.setdefault('stage_results', {})[new_state] = dict(stage_result)
        if extra:
            row.update(dict(extra))
        self._write(row)
        return row

    def list(self, *, limit: int = 100, include_terminal: bool = True) -> list[dict[str, Any]]:
        try:
            files = sorted(self.root.glob('txn-*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
        except Exception:
            files = []
        rows = []
        for path in files[:max(1, min(int(limit), 1000))]:
            try:
                row = json.loads(path.read_text())
            except Exception:
                continue
            if not isinstance(row, dict):
                continue
            if not include_terminal and str(row.get('status') or '') in TERMINAL_STATES:
                continue
            rows.append(row)
        return rows

    def nonterminal(self, *, limit: int = 100) -> list[dict[str, Any]]:
        return self.list(limit=limit, include_terminal=False)


class TransactionEngine:
    def __init__(self, journal: FileTransactionJournal | None = None, *, clock=time.time) -> None:
        self.journal = journal or FileTransactionJournal(clock=clock)
        self.clock = clock

    @staticmethod
    def _subject(adapter: Any, request: dict[str, Any]) -> str:
        subject_fn = getattr(adapter, 'subject', None)
        if callable(subject_fn):
            return str(subject_fn(dict(request)) or '')
        return str(
            request.get('id')
            or request.get('name')
            or request.get('target')
            or request.get('component')
            or ''
        )

    @staticmethod
    def _call_optional(adapter: Any, name: str, ctx: TransactionContext, default: dict[str, Any]) -> dict[str, Any]:
        fn = getattr(adapter, name, None)
        if not callable(fn):
            return dict(default)
        row = fn(ctx)
        if row is None:
            return dict(default)
        if not isinstance(row, dict):
            raise TransactionError(f'{name} must return a mapping')
        return row

    def _new_id(self, spec_id: str) -> str:
        stamp = time.strftime('%Y%m%dt%H%M%S', time.localtime(float(self.clock())))
        return f'txn-{spec_id}-{stamp}-{uuid.uuid4().hex[:8]}'

    def _rollback(self, ctx: TransactionContext, *, reason: str) -> dict[str, Any]:
        tid = ctx.transaction_id
        self.journal.transition(tid, 'rolling_back', detail=reason)
        try:
            result = self._call_optional(
                ctx.spec.adapter,
                'rollback',
                ctx,
                {'ok': False, 'error': 'rollback handler unavailable'},
            )
            if result.get('ok'):
                return self.journal.transition(
                    tid,
                    'rolled_back',
                    detail='rollback verified by adapter',
                    stage_result=result,
                )
            return self.journal.transition(
                tid,
                'rollback_failed',
                detail=str(result.get('error') or 'rollback reported failure'),
                stage_result=result,
            )
        except Exception as exc:
            return self.journal.transition(
                tid,
                'rollback_failed',
                detail=f'{type(exc).__name__}: {exc}',
                stage_result={'ok': False, 'error': f'{type(exc).__name__}: {exc}'},
            )

    def execute(
        self,
        spec: TransactionSpec,
        request: Mapping[str, Any] | None = None,
        *,
        actor: str = 'local',
    ) -> dict[str, Any]:
        requested = dict(request or {})
        adapter = spec.adapter
        subject = self._subject(adapter, requested)
        tid = self._new_id(spec.id)
        ctx = TransactionContext(tid, spec, str(actor), requested, subject)

        plan = adapter.plan(ctx)
        if not isinstance(plan, dict):
            raise TransactionError('transaction plan must be a mapping')
        self.journal.create(
            transaction_id=tid,
            spec=spec,
            actor=actor,
            request=requested,
            subject=subject,
            plan=plan,
        )
        if not bool(plan.get('allowed', False)):
            return self.journal.transition(
                tid,
                'cancelled_before_apply',
                detail='; '.join(plan.get('blockers') or ['transaction blocked by plan']),
                stage_result={'ok': False, 'blockers': list(plan.get('blockers') or [])},
            )

        try:
            self.journal.transition(tid, 'preparing', detail='preparing transaction')
            prepared = self._call_optional(adapter, 'prepare', ctx, {'ok': True})
            ctx.data['prepare'] = prepared
            if prepared.get('ok') is False:
                return self.journal.transition(
                    tid,
                    'cancelled_before_apply',
                    detail=str(prepared.get('error') or 'prepare blocked transaction'),
                    stage_result=prepared,
                )
            self.journal.transition(tid, 'prepared', detail='transaction prepared', stage_result=prepared)

            self.journal.transition(tid, 'applying', detail='applying transaction')
            applied = adapter.apply(ctx)
            if not isinstance(applied, dict):
                raise TransactionError('apply must return a mapping')
            ctx.data['apply'] = applied
            if applied.get('ok') is False:
                return self._rollback(ctx, reason=str(applied.get('error') or 'apply reported failure'))
            self.journal.transition(tid, 'applied', detail='transaction applied', stage_result=applied)

            if spec.probation_required:
                self.journal.transition(tid, 'probation', detail='observing probation window')
                probation = self._call_optional(adapter, 'probation', ctx, {'ok': True})
                ctx.data['probation'] = probation
                if probation.get('ok') is False:
                    return self._rollback(ctx, reason=str(probation.get('error') or 'probation failed'))

            self.journal.transition(tid, 'verifying', detail='verifying transaction outcome')
            verification = self._call_optional(adapter, 'verify', ctx, {'ok': True})
            ctx.data['verify'] = verification
            if spec.verification_required and verification.get('ok') is not True:
                return self._rollback(ctx, reason=str(verification.get('error') or 'verification failed'))

            self.journal.transition(tid, 'committing', detail='committing verified transaction')
            committed = self._call_optional(adapter, 'commit', ctx, {'ok': True})
            ctx.data['commit'] = committed
            if committed.get('ok') is False:
                return self._rollback(ctx, reason=str(committed.get('error') or 'commit failed'))
            return self.journal.transition(
                tid,
                'committed',
                detail='transaction committed',
                stage_result=committed,
            )
        except Exception as exc:
            # If apply may have begun, rollback is the conservative managed path.
            current = self.journal.get(tid)
            state = str(current.get('status') or '')
            if state in {'applying', 'applied', 'probation', 'verifying', 'committing'} and spec.reversible:
                return self._rollback(ctx, reason=f'{type(exc).__name__}: {exc}')
            if state in {'planned', 'preparing', 'prepared'}:
                return self.journal.transition(
                    tid,
                    'cancelled_before_apply',
                    detail=f'{type(exc).__name__}: {exc}',
                    stage_result={'ok': False, 'error': f'{type(exc).__name__}: {exc}'},
                )
            try:
                return self.journal.transition(
                    tid,
                    'indeterminate',
                    detail=f'{type(exc).__name__}: {exc}',
                    stage_result={'ok': False, 'error': f'{type(exc).__name__}: {exc}'},
                )
            except TransactionTransitionError:
                raise TransactionError(f'transaction failed in terminal state {state}: {exc}') from exc

    def recovery_inventory(self) -> dict[str, Any]:
        rows = self.journal.nonterminal(limit=500)
        return {
            'count': len(rows),
            'items': rows,
            'automatic_replay_enabled': False,
            'note': 'Nonterminal transactions require adapter-specific inspect/resume/recover policy; blind replay is forbidden.',
        }

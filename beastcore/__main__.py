from __future__ import annotations

import argparse
import asyncio
import json
import logging
import signal

from .core import BeastCore
from .collectors import SystemCollector, RadioCollector, GPSCollector, PwnagotchiCollector, BettercapCollector, ServicesCollector, StorageCollector, HardwareCollector, BridgeCollector


def once() -> dict:
    result = {}
    for c in [SystemCollector(), RadioCollector(), GPSCollector(), BettercapCollector(), PwnagotchiCollector(), BridgeCollector(), ServicesCollector(), StorageCollector(), HardwareCollector()]:
        try: result.update(c.collect())
        except Exception as exc: result[f"collector_error.{c.name}"] = repr(exc)
    return result

async def amain(args) -> None:
    core = BeastCore(db_path=args.db, host=args.host, port=args.port)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try: loop.add_signal_handler(sig, core.stop)
        except NotImplementedError: pass
    await core.run()


def main() -> None:
    p = argparse.ArgumentParser(prog="beast-core")
    p.add_argument("--once", action="store_true", help="collect one read-only snapshot and exit")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8090)
    p.add_argument("--db", default="/var/lib/beastagotchi/beast.db")
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args()
    logging.basicConfig(level=getattr(logging,args.log_level.upper(),logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.once:
        print(json.dumps(once(), indent=2, default=str)); return
    asyncio.run(amain(args))

if __name__ == "__main__": main()

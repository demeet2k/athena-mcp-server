from __future__ import annotations

import argparse
import json
from pprint import pprint

from .config import AthenaBotConfig
from .service import AthenaBotRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Athena crypto paper-trading runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)

    refresh = subparsers.add_parser("refresh-data", help="Refresh local 1h bars and rebuild 4h bars")
    refresh.add_argument("--symbols", nargs="+", default=None, help="Override default symbol universe")
    refresh.add_argument("--since", dest="since_ts", help="Optional ISO timestamp to backfill from")

    scan = subparsers.add_parser("scan", help="Compute signal snapshots only")
    scan.add_argument("--symbols", nargs="+", default=None, help="Override default symbol universe")
    scan.add_argument("--once", action="store_true", help="Compatibility flag; scanning already runs once")

    paper = subparsers.add_parser("paper-loop", help="Run paper trading loop")
    paper.add_argument("--symbols", nargs="+", default=None, help="Override default symbol universe")
    paper.add_argument("--iterations", type=int, default=1, help="Loop iterations; 0 means forever")
    paper.add_argument("--sleep-seconds", type=int, default=60, help="Pause between loop iterations")

    status = subparsers.add_parser("status", help="Show portfolio and data freshness")
    status.add_argument("--symbols", nargs="+", default=None, help="Override default symbol universe")

    replay = subparsers.add_parser("replay", help="Run deterministic walk-forward replay")
    replay.add_argument("--symbols", nargs="+", default=None, help="Override default symbol universe")
    replay.add_argument("--from", dest="from_ts", required=True, help="Replay start timestamp or date")
    replay.add_argument("--to", dest="to_ts", required=True, help="Replay end timestamp or date")

    tuning = subparsers.add_parser("tuning-report", help="Run bounded multi-window portfolio tuning report")
    tuning.add_argument("--symbols", nargs="+", default=None, help="Override default symbol universe")
    tuning.add_argument("--windows", nargs="+", type=int, default=[7, 14, 30], help="Rolling window lengths in days")
    tuning.add_argument("--top", type=int, default=10, help="How many candidates to show in the compact CLI summary")
    tuning.add_argument("--refresh", action="store_true", help="Refresh candles before freezing the evaluation set")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = AthenaBotConfig()
    if getattr(args, "symbols", None):
        config.symbols = tuple(args.symbols)
    runtime = AthenaBotRuntime(config)

    if args.command == "refresh-data":
        result = runtime.refresh_data(list(config.symbols), since_ts=args.since_ts)
        pprint(result)
        return 0
    if args.command == "scan":
        result = runtime.scan_once(list(config.symbols), refresh=True)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "paper-loop":
        result = runtime.paper_loop(
            list(config.symbols),
            iterations=args.iterations,
            sleep_seconds=args.sleep_seconds,
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "status":
        result = runtime.status()
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "replay":
        result = runtime.run_replay(list(config.symbols), args.from_ts, args.to_ts)
        summary = {
            "start": result["start"],
            "end": result["end"],
            "symbols": result["symbols"],
            "trades": result["trades"],
            "completed_trades": result["completed_trades"],
            "fills": result["fills"],
            "ending_cash": result["ending_cash"],
            "ending_equity": result["ending_equity"],
            "return_pct": result["return_pct"],
            "max_drawdown_pct": result["max_drawdown_pct"],
            "report_path": result["report_path"],
        }
        print(json.dumps(summary, indent=2))
        return 0
    if args.command == "tuning-report":
        result = runtime.run_tuning_report(
            list(config.symbols),
            windows=args.windows,
            top=args.top,
            refresh=args.refresh,
        )
        summary = {
            "symbols": result["symbols"],
            "windows": result["windows"],
            "latest_common_close": result["latest_common_close"],
            "candidate_count": result["search_policy"]["candidate_count"],
            "decision": result["recommendation"]["decision"],
            "candidate": result["recommendation"]["candidate_label"],
            "report_markdown": result["artifacts"]["report_markdown"],
            "report_json": result["artifacts"]["report_json"],
        }
        print(json.dumps(summary, indent=2))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 1

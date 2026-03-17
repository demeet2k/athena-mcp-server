from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import AthenaBotConfig
from .models import PortfolioState, SignalSnapshot
from .utils import append_jsonl, now_utc, read_json, to_iso, write_json


class LedgerWriter:
    def __init__(self, config: AthenaBotConfig | None = None):
        self.config = config or AthenaBotConfig()

    def load_portfolio(self) -> PortfolioState:
        payload = read_json(
            self.config.portfolio_state_path,
            {
                "cash": self.config.initial_equity,
                "equity": self.config.initial_equity,
                "positions": {},
            },
        )
        return PortfolioState.from_dict(payload)

    def save_portfolio(self, portfolio_state: PortfolioState) -> None:
        write_json(self.config.portfolio_state_path, portfolio_state.to_dict())
        write_json(
            self.config.latest_positions_path,
            {
                "ts": portfolio_state.updated_at,
                "cash": portfolio_state.cash,
                "equity": portfolio_state.equity,
                "positions": {
                    symbol: position.to_dict()
                    for symbol, position in portfolio_state.positions.items()
                },
            },
        )

    def append_signal(self, snapshot: SignalSnapshot) -> None:
        stamped = snapshot.to_dict()
        stamped["written_at"] = to_iso(now_utc())
        append_jsonl(self._daily_path(self.config.signals_dir, snapshot.bar_close_ts), stamped)
        write_json(self.config.signals_dir / "latest.json", stamped)
        latest_dir = self.config.signals_dir / "latest"
        write_json(latest_dir / f"{snapshot.symbol}.json", stamped)

    def write_latest_scan(self, command: str, snapshots: list[dict]) -> Path:
        payload = {
            "ts": to_iso(now_utc()),
            "command": command,
            "symbol_count": len(snapshots),
            "signals": snapshots,
        }
        path = self.config.signals_dir / "latest_scan.json"
        write_json(path, payload)
        return path

    def read_latest_scan(self) -> dict:
        return read_json(self.config.signals_dir / "latest_scan.json", {})

    def append_order(self, order: dict) -> None:
        append_jsonl(self.config.orders_path, order)

    def append_fill(self, fill: dict) -> None:
        append_jsonl(self.config.fills_path, fill)

    def append_journal(self, event_type: str, payload: dict) -> None:
        append_jsonl(
            self.config.journal_path,
            {"ts": to_iso(now_utc()), "event_type": event_type, "payload": payload},
        )

    def append_equity(self, portfolio_state: PortfolioState) -> None:
        row = pd.DataFrame(
            [
                {
                    "ts": portfolio_state.updated_at or to_iso(now_utc()),
                    "cash": portfolio_state.cash,
                    "equity": portfolio_state.equity,
                    "open_positions": len(portfolio_state.positions),
                    "open_risk": portfolio_state.open_risk,
                }
            ]
        )
        path = self.config.equity_curve_path
        if path.exists():
            existing = pd.read_csv(path)
            combined = pd.concat([existing, row], ignore_index=True)
            combined = combined.drop_duplicates("ts", keep="last")
            combined.to_csv(path, index=False)
        else:
            row.to_csv(path, index=False)

    def write_replay_report(self, report: dict) -> Path:
        ts_slug = now_utc().strftime("%Y%m%dT%H%M%SZ")
        path = self.config.replay_dir / f"replay_{ts_slug}.json"
        write_json(path, report)
        write_json(self.config.replay_dir / "latest_replay.json", report)
        return path

    def _daily_path(self, root: Path, ts_value: str) -> Path:
        if not ts_value:
            date_slug = now_utc().strftime("%Y-%m-%d")
        else:
            date_slug = pd.Timestamp(ts_value).strftime("%Y-%m-%d")
        return root / f"{date_slug}.jsonl"

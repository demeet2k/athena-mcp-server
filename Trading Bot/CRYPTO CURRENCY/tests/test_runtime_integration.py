from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from athena_bot.config import AthenaBotConfig  # noqa: E402
from athena_bot.models import Candle, DirectionState, FractalState  # noqa: E402
from athena_bot.service import AthenaBotRuntime  # noqa: E402
from athena_bot.utils import latest_closed_bar  # noqa: E402


class FakeProvider:
    def __init__(self, candles):
        self.candles = candles

    def fetch(self, symbol, timeframe, since_ts=None):
        if timeframe != "1h":
            return []
        rows = self.candles[symbol]
        if since_ts is None:
            return rows
        since = pd.Timestamp(since_ts, tz="UTC")
        return [row for row in rows if pd.Timestamp(row.ts_open) > since]


class StubFractalCore:
    def evaluate(self, symbol, bars_1h, bars_4h):
        return FractalState(
            symbol=symbol,
            bar_close_ts=bars_1h["ts_close"].iloc[-1].isoformat(),
            timeframe_context="4h->1h",
            fractal_regime="constructive",
            signal_type="PHASE_EDGE",
            composite_score=0.62,
            transition_score=0.4,
            cycle_alignment=0.2,
            phase_quality="Fixed Fire",
            volatility_regime="mixed",
            recommended_size_fraction=0.5,
            stop_atr_multiplier=2.0,
            corridor_legal=True,
            reason_codes=[],
        )


class StubDirectionalFilter:
    def evaluate(self, symbol, bars_1h, bars_4h):
        return DirectionState(
            symbol=symbol,
            bar_close_ts=bars_1h["ts_close"].iloc[-1].isoformat(),
            directional_bias="long",
            trend_ok=True,
            trigger="breakout",
            entry_ready=True,
            volume_ok=True,
            volatility_ok=True,
            atr=2.0,
            atr_pct=0.02,
            trigger_price=float(bars_1h["close"].iloc[-1]),
            reason_codes=[],
        )


class RuntimeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = AthenaBotConfig(base_dir=Path(self.tmpdir.name))
        self.config.symbols = ("BTC",)
        candles = {"BTC": self._make_candles("BTC", 1200)}
        self.start_ts = candles["BTC"][0].ts_close
        self.end_ts = candles["BTC"][-2].ts_close
        self.runtime = AthenaBotRuntime(self.config)
        self.runtime.bar_store.provider = FakeProvider(candles)
        self.runtime.fractal_core = StubFractalCore()
        self.runtime.directional_filter = StubDirectionalFilter()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_scan_and_paper_once(self) -> None:
        scans = self.runtime.scan_once(refresh=True)
        self.assertEqual(len(scans), 1)
        self.assertEqual(scans[0]["entry_action"], "BUY")

        first_pass = self.runtime.paper_once()
        self.assertEqual(first_pass[0]["signal"]["entry_action"], "BUY")
        second_pass = self.runtime.paper_once()
        self.assertEqual(second_pass[0]["signal"]["entry_action"], "HOLD")
        self.assertIsNone(second_pass[0]["fill"])

    def test_replay_is_deterministic(self) -> None:
        self.runtime.refresh_data(["BTC"])
        first = self.runtime.run_replay(["BTC"], self.start_ts, self.end_ts)
        second = self.runtime.run_replay(["BTC"], self.start_ts, self.end_ts)
        self.assertEqual(first["ending_equity"], second["ending_equity"])
        self.assertEqual(first["fills"], second["fills"])

    def test_stale_data_forces_stand_down(self) -> None:
        old_rows = self._make_candles("BTC", 24, end_at=pd.Timestamp("2026-01-01T00:00:00Z"))
        self.runtime.bar_store.provider = FakeProvider({"BTC": old_rows})
        scans = self.runtime.scan_once(refresh=True)
        self.assertEqual(scans[0]["entry_action"], "STAND_DOWN")

    def _make_candles(self, symbol: str, periods: int, end_at=None) -> list[Candle]:
        end_at = end_at or pd.Timestamp(latest_closed_bar(timeframe="1h"))
        start = end_at - pd.Timedelta(hours=periods)
        rows = []
        for idx in range(periods):
            open_ts = start + pd.Timedelta(hours=idx)
            close_ts = open_ts + pd.Timedelta(hours=1)
            base = 100 + idx * 0.05
            rows.append(
                Candle(
                    symbol=symbol,
                    timeframe="1h",
                    ts_open=open_ts.isoformat().replace("+00:00", "Z"),
                    ts_close=close_ts.isoformat().replace("+00:00", "Z"),
                    open=base,
                    high=base + 1,
                    low=base - 1,
                    close=base + 0.5,
                    volume=1000 + idx,
                    source="fake",
                )
            )
        return rows

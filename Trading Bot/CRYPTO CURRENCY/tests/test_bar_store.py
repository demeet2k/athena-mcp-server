from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from athena_bot.bar_store import BarStore  # noqa: E402
from athena_bot.config import AthenaBotConfig  # noqa: E402
from athena_bot.models import Candle  # noqa: E402


class BarStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = AthenaBotConfig(base_dir=Path(self.tmpdir.name))
        self.store = BarStore(config=self.config, provider=None)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_merge_bars_deduplicates_on_open_time(self) -> None:
        existing = pd.DataFrame(
            [
                {
                    "symbol": "BTC",
                    "timeframe": "1h",
                    "ts_open": pd.Timestamp("2026-03-10T00:00:00Z"),
                    "ts_close": pd.Timestamp("2026-03-10T01:00:00Z"),
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                    "volume": 10.0,
                    "source": "test",
                }
            ]
        )
        incoming = [
            Candle(
                symbol="BTC",
                timeframe="1h",
                ts_open="2026-03-10T00:00:00Z",
                ts_close="2026-03-10T01:00:00Z",
                open=100.0,
                high=102.0,
                low=99.0,
                close=101.0,
                volume=12.0,
                source="test",
            ),
            Candle(
                symbol="BTC",
                timeframe="1h",
                ts_open="2026-03-10T01:00:00Z",
                ts_close="2026-03-10T02:00:00Z",
                open=101.0,
                high=103.0,
                low=100.0,
                close=102.0,
                volume=8.0,
                source="test",
            ),
        ]
        merged = self.store.merge_bars(existing, incoming)
        self.assertEqual(len(merged), 2)
        self.assertEqual(float(merged.iloc[0]["close"]), 101.0)

    def test_aggregate_to_4h_rolls_four_bars(self) -> None:
        rows = []
        for hour in range(4):
            rows.append(
                {
                    "symbol": "BTC",
                    "timeframe": "1h",
                    "ts_open": pd.Timestamp(f"2026-03-10T0{hour}:00:00Z"),
                    "ts_close": pd.Timestamp(f"2026-03-10T0{hour+1}:00:00Z"),
                    "open": 100.0 + hour,
                    "high": 101.0 + hour,
                    "low": 99.0 + hour,
                    "close": 100.5 + hour,
                    "volume": 10.0 + hour,
                    "source": "test",
                }
            )
        frame = pd.DataFrame(rows)
        aggregated = self.store.aggregate_to_4h(frame, "BTC")
        self.assertEqual(len(aggregated), 1)
        self.assertEqual(float(aggregated.iloc[0]["open"]), 100.0)
        self.assertEqual(float(aggregated.iloc[0]["close"]), 103.5)
        self.assertEqual(float(aggregated.iloc[0]["volume"]), 46.0)

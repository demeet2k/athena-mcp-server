from __future__ import annotations

import json
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
from athena_bot.tuning import TuningEvaluator  # noqa: E402
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


class ConfigAwareFractalStub:
    def __init__(self, config=None):
        self.config = config or AthenaBotConfig(base_dir=ROOT)

    def evaluate(self, symbol, bars_1h, bars_4h):
        step = len(bars_1h)
        transition = 0.92 if symbol == "BTC" and step % 36 == 0 else 0.35
        corridor_legal = transition < self.config.transition_block_threshold
        reason_codes = [] if corridor_legal else ["corridor_illegal"]
        regime = "constructive" if corridor_legal else "transition_extreme"
        signal_type = "PHASE_EDGE" if corridor_legal else "NEXUS_ALERT"
        return FractalState(
            symbol=symbol,
            bar_close_ts=bars_1h["ts_close"].iloc[-1].isoformat(),
            timeframe_context="4h->1h",
            fractal_regime=regime,
            signal_type=signal_type,
            composite_score=0.65,
            transition_score=transition,
            cycle_alignment=0.25,
            phase_quality="Fixed Fire",
            volatility_regime="mixed",
            recommended_size_fraction=0.5,
            stop_atr_multiplier=2.0,
            corridor_legal=corridor_legal,
            reason_codes=reason_codes,
        )


class ConfigAwareDirectionalStub:
    def __init__(self, config=None):
        self.config = config or AthenaBotConfig(base_dir=ROOT)

    def evaluate(self, symbol, bars_1h, bars_4h):
        step = len(bars_1h)
        latest_price = float(bars_1h["close"].iloc[-1])
        if symbol == "BTC":
            trigger_blocked = self.config.breakout_buffer_bps >= 20.0 and step % 12 == 0
            entry_ready = not trigger_blocked
            trigger = "breakout" if entry_ready else "none"
            reason_codes = [] if entry_ready else ["1h_trigger_missing"]
            return DirectionState(
                symbol=symbol,
                bar_close_ts=bars_1h["ts_close"].iloc[-1].isoformat(),
                directional_bias="long",
                trend_ok=True,
                trigger=trigger,
                entry_ready=entry_ready,
                volume_ok=True,
                volatility_ok=True,
                atr=2.0,
                atr_pct=0.02,
                trigger_price=latest_price,
                reason_codes=reason_codes,
            )

        return DirectionState(
            symbol=symbol,
            bar_close_ts=bars_1h["ts_close"].iloc[-1].isoformat(),
            directional_bias="long",
            trend_ok=True,
            trigger="none",
            entry_ready=False,
            volume_ok=True,
            volatility_ok=True,
            atr=2.0,
            atr_pct=0.02,
            trigger_price=latest_price,
            reason_codes=["1h_trigger_missing"],
        )


class TuningReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = AthenaBotConfig(base_dir=Path(self.tmpdir.name))
        self.config.symbols = ("BTC", "ETH", "SOL", "XRP")
        candles = {
            symbol: self._make_candles(symbol, periods=320, offset=offset)
            for offset, symbol in enumerate(self.config.symbols)
        }
        self.start_ts = candles["BTC"][24].ts_close
        self.end_ts = candles["BTC"][-2].ts_close
        self.runtime = AthenaBotRuntime(self.config)
        self.runtime.bar_store.provider = FakeProvider(candles)
        self.runtime.fractal_core = ConfigAwareFractalStub(self.config)
        self.runtime.directional_filter = ConfigAwareDirectionalStub(self.config)
        self.runtime.refresh_data(list(self.config.symbols))

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_candidate_set_includes_baseline_and_respects_fast_slow(self) -> None:
        evaluator = TuningEvaluator(self.runtime, self.config)
        candidates = evaluator.build_candidate_set()
        self.assertTrue(any(candidate["id"] == "baseline" for candidate in candidates))
        self.assertEqual(len(candidates), len({candidate["id"] for candidate in candidates}))
        for candidate in candidates:
            params = candidate["parameters"]
            self.assertLess(params["trend_4h_fast_ema"], params["trend_4h_slow_ema"])

    def test_replay_reason_aggregation_tracks_trigger_blocks(self) -> None:
        result = self.runtime.replay.run_portfolio(
            list(self.config.symbols),
            self.start_ts,
            self.end_ts,
            refresh=False,
        ).to_dict()
        self.assertGreater(result["reason_code_counts"].get("1h_trigger_missing", 0), 0)
        self.assertGreater(
            result["blocking_reasons_by_symbol"]["ETH"].get("1h_trigger_missing", 0),
            0,
        )
        self.assertGreater(
            result["opportunity_diagnostics"]["by_symbol"]["ETH"]["blocked_by_trigger"],
            0,
        )

    def test_tuning_report_is_deterministic_and_does_not_mutate_config(self) -> None:
        baseline_breakout = self.runtime.config.breakout_buffer_bps
        baseline_transition = self.runtime.config.transition_block_threshold
        small_candidate_set = self.runtime.tuning.build_candidate_set()[:4]
        self.runtime.tuning.build_candidate_set = lambda: small_candidate_set

        first = self.runtime.run_tuning_report(
            list(self.config.symbols),
            windows=[3, 7],
            top=5,
            refresh=False,
        )
        second = self.runtime.run_tuning_report(
            list(self.config.symbols),
            windows=[3, 7],
            top=5,
            refresh=False,
        )

        first_ids = [candidate["id"] for candidate in first["leaderboard"][:5]]
        second_ids = [candidate["id"] for candidate in second["leaderboard"][:5]]
        self.assertEqual(first_ids, second_ids)
        self.assertEqual(self.runtime.config.breakout_buffer_bps, baseline_breakout)
        self.assertEqual(self.runtime.config.transition_block_threshold, baseline_transition)

        report_json = Path(first["artifacts"]["report_json"])
        report_md = Path(first["artifacts"]["report_markdown"])
        candidate_matrix = Path(first["artifacts"]["candidate_matrix"])
        window_summaries = Path(first["artifacts"]["window_summaries"])
        for path in (report_json, report_md, candidate_matrix, window_summaries):
            self.assertTrue(path.exists(), msg=str(path))

        payload = json.loads(report_json.read_text(encoding="utf-8"))
        self.assertEqual(payload["recommendation"]["decision"], first["recommendation"]["decision"])
        self.assertIn("baseline", {candidate["id"] for candidate in payload["leaderboard"]})

    def _make_candles(self, symbol: str, periods: int, offset: int = 0) -> list[Candle]:
        end_at = pd.Timestamp(latest_closed_bar(timeframe="1h"))
        start = end_at - pd.Timedelta(hours=periods)
        rows = []
        for idx in range(periods):
            open_ts = start + pd.Timedelta(hours=idx)
            close_ts = open_ts + pd.Timedelta(hours=1)
            base = 100 + offset * 10 + idx * (0.12 if symbol == "BTC" else 0.04)
            rows.append(
                Candle(
                    symbol=symbol,
                    timeframe="1h",
                    ts_open=open_ts.isoformat().replace("+00:00", "Z"),
                    ts_close=close_ts.isoformat().replace("+00:00", "Z"),
                    open=base,
                    high=base + 1.5,
                    low=base - 1.0,
                    close=base + 0.6,
                    volume=1000 + idx + offset * 5,
                    source="fake",
                )
            )
        return rows


if __name__ == "__main__":
    unittest.main()

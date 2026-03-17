from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from athena_bot.config import AthenaBotConfig  # noqa: E402
from athena_bot.models import DirectionState, FractalState, PortfolioState  # noqa: E402
from athena_bot.strategy import StrategyEngine  # noqa: E402


class StrategyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = StrategyEngine(AthenaBotConfig(base_dir=ROOT))

    def test_buy_when_fractal_and_direction_align(self) -> None:
        fractal = FractalState(
            symbol="BTC",
            bar_close_ts="2026-03-12T10:00:00Z",
            timeframe_context="4h->1h",
            fractal_regime="constructive",
            signal_type="PHASE_EDGE",
            composite_score=0.61,
            transition_score=0.42,
            cycle_alignment=0.25,
            phase_quality="Fixed Fire",
            volatility_regime="mixed",
            recommended_size_fraction=0.5,
            stop_atr_multiplier=2.0,
            corridor_legal=True,
            reason_codes=[],
        )
        direction = DirectionState(
            symbol="BTC",
            bar_close_ts="2026-03-12T10:00:00Z",
            directional_bias="long",
            trend_ok=True,
            trigger="breakout",
            entry_ready=True,
            volume_ok=True,
            volatility_ok=True,
            atr=2.0,
            atr_pct=0.02,
            trigger_price=100.0,
            reason_codes=[],
        )
        portfolio = PortfolioState(cash=10_000.0, equity=10_000.0)
        snapshot = self.engine.decide(fractal, direction, portfolio, latest_price=100.0)
        self.assertEqual(snapshot.entry_action, "BUY")
        self.assertAlmostEqual(snapshot.stop_price, 96.0)

    def test_transition_extreme_blocks_new_entry(self) -> None:
        fractal = FractalState(
            symbol="BTC",
            bar_close_ts="2026-03-12T10:00:00Z",
            timeframe_context="4h->1h",
            fractal_regime="transition_extreme",
            signal_type="NEXUS_ALERT",
            composite_score=0.9,
            transition_score=0.95,
            cycle_alignment=0.9,
            phase_quality="Mutable Water",
            volatility_regime="expanding",
            recommended_size_fraction=0.25,
            stop_atr_multiplier=1.0,
            corridor_legal=False,
            reason_codes=["corridor_illegal"],
        )
        direction = DirectionState(
            symbol="BTC",
            bar_close_ts="2026-03-12T10:00:00Z",
            directional_bias="long",
            trend_ok=True,
            trigger="breakout",
            entry_ready=True,
            volume_ok=True,
            volatility_ok=True,
            atr=2.0,
            atr_pct=0.02,
            trigger_price=100.0,
            reason_codes=[],
        )
        portfolio = PortfolioState(cash=10_000.0, equity=10_000.0)
        snapshot = self.engine.decide(fractal, direction, portfolio, latest_price=100.0)
        self.assertEqual(snapshot.entry_action, "STAND_DOWN")
        self.assertEqual(snapshot.invalidation_reason, "corridor_illegal")

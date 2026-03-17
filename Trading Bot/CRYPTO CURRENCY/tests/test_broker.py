from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from athena_bot.broker import PaperBroker  # noqa: E402
from athena_bot.config import AthenaBotConfig  # noqa: E402
from athena_bot.models import PortfolioState, SignalSnapshot  # noqa: E402


class BrokerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.broker = PaperBroker(AthenaBotConfig(base_dir=ROOT))

    def test_buy_then_exit_updates_cash_and_positions(self) -> None:
        portfolio = PortfolioState(cash=10_000.0, equity=10_000.0)
        buy_signal = SignalSnapshot(
            symbol="BTC",
            bar_close_ts="2026-03-12T10:00:00Z",
            timeframe_context="4h->1h",
            fractal_regime="constructive",
            transition_score=0.4,
            cycle_alignment=0.2,
            phase_quality="Fixed Fire",
            volatility_regime="mixed",
            directional_bias="long",
            entry_action="BUY",
            size_fraction=0.5,
            stop_price=95.0,
            invalidation_reason="all_green",
            latest_price=100.0,
            trigger_price=100.0,
            atr=2.0,
            atr_pct=0.02,
        )
        buy_result = self.broker.apply(buy_signal, portfolio)
        self.assertIn("BTC", buy_result.portfolio.positions)
        self.assertLess(buy_result.portfolio.cash, 10_000.0)

        exit_signal = SignalSnapshot(
            symbol="BTC",
            bar_close_ts="2026-03-12T11:00:00Z",
            timeframe_context="4h->1h",
            fractal_regime="balanced",
            transition_score=0.3,
            cycle_alignment=0.1,
            phase_quality="Fixed Fire",
            volatility_regime="mixed",
            directional_bias="flat",
            entry_action="EXIT",
            size_fraction=0.0,
            stop_price=95.0,
            invalidation_reason="trend_lost",
            latest_price=105.0,
            trigger_price=105.0,
            atr=2.0,
            atr_pct=0.02,
        )
        exit_result = self.broker.apply(exit_signal, buy_result.portfolio)
        self.assertNotIn("BTC", exit_result.portfolio.positions)
        self.assertGreater(exit_result.portfolio.cash, buy_result.portfolio.cash)

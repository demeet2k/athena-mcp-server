from __future__ import annotations

import time
from dataclasses import asdict

from .bar_store import BarStore
from .broker import PaperBroker
from .config import AthenaBotConfig
from .directional import DirectionalFilter
from .fractal_core import FractalCore
from .ledger import LedgerWriter
from .replay import ReplayEvaluator
from .strategy import StrategyEngine
from .tuning import TuningEvaluator
from .utils import latest_closed_bar


class AthenaBotRuntime:
    def __init__(self, config: AthenaBotConfig | None = None):
        self.config = config or AthenaBotConfig()
        self.bar_store = BarStore(self.config)
        self.fractal_core = FractalCore(self.config)
        self.directional_filter = DirectionalFilter(self.config)
        self.strategy = StrategyEngine(self.config)
        self.ledger = LedgerWriter(self.config)
        self.broker = PaperBroker(self.config)
        self.replay = ReplayEvaluator(self, self.config)
        self.tuning = TuningEvaluator(self, self.config)

    def clone_with_config(self, config: AthenaBotConfig) -> "AthenaBotRuntime":
        clone = type(self)(config)
        clone.bar_store.provider = self.bar_store.provider
        clone.fractal_core = self._clone_component(self.fractal_core, config)
        clone.directional_filter = self._clone_component(self.directional_filter, config)
        clone.strategy = self._clone_component(self.strategy, config)
        clone.broker = self._clone_component(self.broker, config)
        clone.replay = ReplayEvaluator(clone, config)
        clone.tuning = TuningEvaluator(clone, config)
        return clone

    def refresh_data(self, symbols: list[str] | None = None, since_ts: str | None = None) -> list[dict]:
        symbols = symbols or list(self.config.symbols)
        receipts = self.bar_store.refresh_all(symbols, since_ts=since_ts)
        self.ledger.append_journal("refresh_data", {"symbols": symbols, "receipts": receipts})
        return receipts

    def scan_once(self, symbols: list[str] | None = None, refresh: bool = True) -> list[dict]:
        symbols = symbols or list(self.config.symbols)
        if refresh:
            self.refresh_data(symbols)
        portfolio = self.ledger.load_portfolio()
        snapshots = []
        for symbol in symbols:
            bars_1h, bars_4h = self.bar_store.bars_for_window(symbol)
            snapshot = self._build_signal_snapshot(symbol, bars_1h, bars_4h, portfolio)
            snapshots.append(snapshot.to_dict())
            self.ledger.append_signal(snapshot)
        self.ledger.write_latest_scan("scan", snapshots)
        self.ledger.append_journal("scan_once", {"symbols": symbols, "signals": len(snapshots)})
        return snapshots

    def paper_once(self, symbols: list[str] | None = None) -> list[dict]:
        symbols = symbols or list(self.config.symbols)
        self.refresh_data(symbols)
        portfolio = self.ledger.load_portfolio()
        executed = []

        for symbol in symbols:
            bars_1h, bars_4h = self.bar_store.bars_for_window(symbol)
            snapshot = self._build_signal_snapshot(symbol, bars_1h, bars_4h, portfolio)
            self.ledger.append_signal(snapshot)
            next_bar = None
            result = self.broker.apply(snapshot, portfolio, next_bar=next_bar)
            portfolio = result.portfolio
            if result.order:
                self.ledger.append_order(result.order)
            if result.fill:
                self.ledger.append_fill(result.fill)
            executed.append(
                {
                    "symbol": symbol,
                    "signal": snapshot.to_dict(),
                    "order": result.order,
                    "fill": result.fill,
                    "notes": result.notes,
                }
            )

        latest_prices = {
            item["symbol"]: item["signal"]["latest_price"] for item in executed
        }
        self.broker.mark_to_market(portfolio, latest_prices)
        self.ledger.save_portfolio(portfolio)
        self.ledger.append_equity(portfolio)
        self.ledger.write_latest_scan(
            "paper-loop",
            [item["signal"] for item in executed],
        )
        self.ledger.append_journal("paper_once", {"symbols": symbols, "fills": len([x for x in executed if x["fill"]])})
        return executed

    def paper_loop(
        self,
        symbols: list[str] | None = None,
        iterations: int = 1,
        sleep_seconds: int = 60,
    ) -> list[list[dict]]:
        runs: list[list[dict]] = []
        counter = 0
        while iterations <= 0 or counter < iterations:
            runs.append(self.paper_once(symbols))
            counter += 1
            if iterations > 0 and counter >= iterations:
                break
            time.sleep(sleep_seconds)
        return runs

    def status(self) -> dict:
        portfolio = self.ledger.load_portfolio()
        latest_signals = self.config.signals_dir / "latest.json"
        freshest = {}
        for symbol in self.config.symbols:
            health = self.bar_store.data_health(symbol, "1h")
            freshest[symbol] = asdict(health)
        latest_scan = self.ledger.read_latest_scan()
        return {
            "portfolio": portfolio.to_dict(),
            "freshness": freshest,
            "latest_signal_path": str(latest_signals),
            "latest_scan": latest_scan,
            "latest_closed_bar": latest_closed_bar(timeframe="1h").isoformat(),
        }

    def run_replay(self, symbols: list[str], from_ts: str, to_ts: str) -> dict:
        report = self.replay.run(symbols, from_ts, to_ts).to_dict()
        path = self.ledger.write_replay_report(report)
        report["report_path"] = str(path)
        self.ledger.append_journal("replay", {"symbols": symbols, "report_path": str(path)})
        return report

    def run_tuning_report(
        self,
        symbols: list[str],
        windows: list[int],
        top: int = 10,
        refresh: bool = False,
    ) -> dict:
        report = self.tuning.evaluate_candidates(
            symbols=symbols,
            windows=windows,
            top=top,
            refresh=refresh,
        )
        self.ledger.append_journal(
            "tuning_report",
            {
                "symbols": symbols,
                "windows": windows,
                "decision": report["recommendation"]["decision"],
                "report_path": report["artifacts"]["report_markdown"],
            },
        )
        return report

    def _build_signal_snapshot(
        self,
        symbol,
        bars_1h,
        bars_4h,
        portfolio_state,
        expected_close_ts=None,
        health=None,
    ):
        health = health or self.bar_store.data_health(
            symbol,
            "1h",
            expected_close=expected_close_ts,
        )
        extra_reasons = list(health.reason_codes)
        fractal = self.fractal_core.evaluate(symbol, bars_1h, bars_4h)
        direction = self.directional_filter.evaluate(symbol, bars_1h, bars_4h)
        latest_price = float(bars_1h["close"].iloc[-1]) if not bars_1h.empty else 0.0
        return self._decide_signal_snapshot(
            fractal=fractal,
            direction=direction,
            portfolio_state=portfolio_state,
            latest_price=latest_price,
            extra_reasons=extra_reasons,
        )

    def _decide_signal_snapshot(
        self,
        fractal,
        direction,
        portfolio_state,
        latest_price: float,
        extra_reasons: list[str] | None = None,
    ):
        extra_reasons = list(extra_reasons or [])
        existing_stop = None
        if fractal.symbol in portfolio_state.positions:
            existing_stop = portfolio_state.positions[fractal.symbol].stop_price
        if any(code in {"stale_bars", "duplicate_bars", "no_bars"} for code in extra_reasons):
            fractal.corridor_legal = False
        return self.strategy.decide(
            fractal_state=fractal,
            direction_state=direction,
            portfolio_state=portfolio_state,
            latest_price=latest_price,
            existing_stop=existing_stop,
            extra_reason_codes=extra_reasons,
        )

    def _clone_component(self, component, config: AthenaBotConfig):
        if hasattr(component, "with_config"):
            return component.with_config(config)
        try:
            return type(component)(config)
        except TypeError:
            try:
                return type(component)()
            except TypeError:
                return component

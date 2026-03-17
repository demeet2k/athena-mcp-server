from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

import pandas as pd

from .broker import PaperBroker
from .config import AthenaBotConfig
from .models import DirectionState, FractalState, PortfolioState


@dataclass(slots=True)
class ReplayResult:
    start: str
    end: str
    symbols: list[str]
    trades: int
    completed_trades: int
    fills: int
    ending_cash: float
    ending_equity: float
    return_pct: float
    max_drawdown_pct: float
    realized_pnl: float
    unrealized_pnl: float
    exposure_pct: float
    turnover: float
    equity_points: list[dict]
    fill_log: list[dict]
    per_asset: dict
    action_counts: dict
    action_counts_by_symbol: dict
    reason_code_counts: dict
    blocking_reasons_by_symbol: dict
    opportunity_diagnostics: dict
    invariants: dict
    deterministic_signature: str

    def to_dict(self) -> dict:
        return asdict(self)


class ReplayEvaluator:
    def __init__(self, runtime, config: AthenaBotConfig | None = None):
        self.runtime = runtime
        self.config = config or runtime.config
        self.broker = PaperBroker(self.config)

    def run(self, symbols: list[str], from_ts: str, to_ts: str) -> ReplayResult:
        return self.run_portfolio(symbols, from_ts, to_ts, refresh=True)

    def run_portfolio(
        self,
        symbols: list[str],
        from_ts: str,
        to_ts: str,
        config_override: AthenaBotConfig | None = None,
        refresh: bool = False,
        signal_stream: dict | None = None,
    ) -> ReplayResult:
        config = config_override or self.config
        runtime = (
            self.runtime
            if config_override is None
            else self.runtime.clone_with_config(config)
        )
        broker = self.broker if config_override is None else PaperBroker(config)

        portfolio = PortfolioState(
            cash=config.initial_equity,
            equity=config.initial_equity,
            positions={},
        )
        fill_log: list[dict] = []
        equity_points: list[dict] = []
        action_counts: Counter[str] = Counter()
        action_counts_by_symbol: dict[str, Counter[str]] = defaultdict(Counter)
        reason_code_counts: Counter[str] = Counter()
        blocking_reasons_by_symbol: dict[str, Counter[str]] = defaultdict(Counter)
        opportunity_by_symbol: dict[str, Counter[str]] = defaultdict(Counter)
        final_prices: dict[str, float] = {}

        if refresh:
            for symbol in symbols:
                warmup_start = (
                    pd.Timestamp(from_ts, tz="UTC")
                    - pd.Timedelta(hours=config.replay_warmup_hours)
                ).isoformat()
                runtime.bar_store.refresh_symbol(symbol, since_ts=warmup_start)

        if signal_stream is None:
            signal_stream = self.prepare_signal_stream(
                symbols=symbols,
                from_ts=from_ts,
                to_ts=to_ts,
                config_override=config,
                refresh=False,
            )

        start_dt = pd.Timestamp(from_ts, tz="UTC")
        end_dt = pd.Timestamp(to_ts, tz="UTC")
        timeline = [
            pd.Timestamp(ts)
            for ts in signal_stream["timeline"]
            if start_dt <= pd.Timestamp(ts) <= end_dt
        ]

        for current_ts in timeline:
            current_key = current_ts.isoformat()
            latest_prices: dict[str, float] = {}
            for symbol in symbols:
                entry = signal_stream["by_ts"].get(current_key, {}).get(symbol)
                if entry is None:
                    continue
                fractal = FractalState(**entry["fractal"])
                direction = DirectionState(**entry["direction"])
                latest_prices[symbol] = entry["latest_price"]
                final_prices[symbol] = entry["latest_price"]
                snapshot = runtime._decide_signal_snapshot(
                    fractal=fractal,
                    direction=direction,
                    portfolio_state=portfolio,
                    latest_price=entry["latest_price"],
                    extra_reasons=entry["health_reason_codes"],
                )

                action_counts[snapshot.entry_action] += 1
                action_counts_by_symbol[symbol][snapshot.entry_action] += 1
                reason_code_counts.update(snapshot.reason_codes)
                self._record_blockers(symbol, snapshot, blocking_reasons_by_symbol)
                self._record_opportunities(symbol, snapshot, opportunity_by_symbol)

                next_bar = entry["next_bar"]
                result = broker.apply(snapshot, portfolio, next_bar=next_bar)
                portfolio = result.portfolio
                if result.fill is not None:
                    fill_log.append(result.fill)
            broker.mark_to_market(portfolio, latest_prices)
            equity_points.append(
                {
                    "ts": current_ts.isoformat(),
                    "equity": portfolio.equity,
                    "cash": portfolio.cash,
                    "open_positions": len(portfolio.positions),
                    "open_risk": round(portfolio.open_risk, 6),
                }
            )

        completed_trades = len([fill for fill in fill_log if fill["side"] == "SELL"])
        realized_pnl = round(
            sum(fill.get("realized_pnl", 0.0) for fill in fill_log if fill["side"] == "SELL"),
            6,
        )
        unrealized_pnl = round(self._unrealized_pnl(portfolio, final_prices), 6)
        max_drawdown_pct = self._max_drawdown(equity_points)
        exposure_pct = self._exposure_pct(equity_points)
        turnover = round(
            (sum(float(fill.get("gross", 0.0)) for fill in fill_log) / config.initial_equity) * 100,
            4,
        ) if config.initial_equity else 0.0

        per_asset = self._per_asset_attribution(
            fill_log=fill_log,
            open_positions=portfolio.positions,
            final_prices=final_prices,
            initial_equity=config.initial_equity,
            symbols=symbols,
        )
        opportunity_diagnostics = self._opportunity_diagnostics(opportunity_by_symbol, symbols)
        invariants = self._evaluate_invariants(
            fill_log=fill_log,
            portfolio=portfolio,
            final_prices=final_prices,
            config=config,
        )
        deterministic_signature = self._signature(
            {
                "start": from_ts,
                "end": to_ts,
                "symbols": symbols,
                "fills": fill_log,
                "equity_points": equity_points,
                "per_asset": per_asset,
                "action_counts": dict(action_counts),
                "reason_code_counts": dict(reason_code_counts),
                "blocking_reasons_by_symbol": self._counter_map_to_dict(blocking_reasons_by_symbol, symbols),
                "opportunity_diagnostics": opportunity_diagnostics,
                "invariants": invariants,
            }
        )

        return ReplayResult(
            start=from_ts,
            end=to_ts,
            symbols=symbols,
            trades=len([fill for fill in fill_log if fill["side"] == "BUY"]),
            completed_trades=completed_trades,
            fills=len(fill_log),
            ending_cash=portfolio.cash,
            ending_equity=portfolio.equity,
            return_pct=round(
                ((portfolio.equity - config.initial_equity) / config.initial_equity) * 100,
                4,
            ) if config.initial_equity else 0.0,
            max_drawdown_pct=max_drawdown_pct,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            exposure_pct=exposure_pct,
            turnover=turnover,
            equity_points=equity_points,
            fill_log=fill_log,
            per_asset=per_asset,
            action_counts=dict(action_counts),
            action_counts_by_symbol=self._counter_map_to_dict(action_counts_by_symbol, symbols),
            reason_code_counts=dict(reason_code_counts),
            blocking_reasons_by_symbol=self._counter_map_to_dict(blocking_reasons_by_symbol, symbols),
            opportunity_diagnostics=opportunity_diagnostics,
            invariants=invariants,
            deterministic_signature=deterministic_signature,
        )

    def prepare_signal_stream(
        self,
        symbols: list[str],
        from_ts: str,
        to_ts: str,
        config_override: AthenaBotConfig | None = None,
        refresh: bool = False,
    ) -> dict:
        config = config_override or self.config
        runtime = (
            self.runtime
            if config_override is None
            else self.runtime.clone_with_config(config)
        )
        if refresh:
            for symbol in symbols:
                warmup_start = (
                    pd.Timestamp(from_ts, tz="UTC")
                    - pd.Timedelta(hours=config.replay_warmup_hours)
                ).isoformat()
                runtime.bar_store.refresh_symbol(symbol, since_ts=warmup_start)

        symbol_frames = {
            symbol: runtime.bar_store.load_bars(symbol, config.primary_timeframe)
            for symbol in symbols
        }
        symbol_context_frames = {
            symbol: runtime.bar_store.load_bars(symbol, config.context_timeframe)
            for symbol in symbols
        }
        common_times = sorted(
            {
                pd.Timestamp(ts)
                for frame in symbol_frames.values()
                for ts in (frame["ts_close"].tolist() if "ts_close" in frame else [])
            }
        )
        start_dt = pd.Timestamp(from_ts, tz="UTC")
        end_dt = pd.Timestamp(to_ts, tz="UTC")
        timeline = [ts for ts in common_times if start_dt <= ts <= end_dt]

        by_ts: dict[str, dict[str, dict]] = {}
        for current_ts in timeline:
            current_key = current_ts.isoformat()
            by_ts[current_key] = {}
            for symbol in symbols:
                bars_1h = symbol_frames[symbol]
                bars_4h = symbol_context_frames[symbol]
                current_slice = bars_1h[bars_1h["ts_close"] <= current_ts].reset_index(drop=True)
                if current_slice.empty:
                    continue
                current_4h = bars_4h[bars_4h["ts_close"] <= current_ts].reset_index(drop=True)
                health = runtime.bar_store.data_health_from_frame(
                    symbol,
                    config.primary_timeframe,
                    current_slice,
                    expected_close=current_ts.to_pydatetime(),
                )
                fractal = runtime.fractal_core.evaluate(symbol, current_slice, current_4h)
                direction = runtime.directional_filter.evaluate(symbol, current_slice, current_4h)
                latest_price = float(current_slice["close"].iloc[-1]) if not current_slice.empty else 0.0
                next_row = bars_1h[bars_1h["ts_open"] >= current_ts].head(1)
                next_bar = next_row.iloc[0].to_dict() if not next_row.empty else None
                by_ts[current_key][symbol] = {
                    "fractal": fractal.to_dict(),
                    "direction": direction.to_dict(),
                    "latest_price": latest_price,
                    "health_reason_codes": list(health.reason_codes),
                    "next_bar": next_bar,
                }

        return {
            "timeline": [ts.isoformat() for ts in timeline],
            "by_ts": by_ts,
        }

    def _record_blockers(self, symbol: str, snapshot, counters: dict[str, Counter[str]]) -> None:
        if snapshot.entry_action not in {"STAND_DOWN", "EXIT"}:
            return
        if snapshot.invalidation_reason:
            counters[symbol][snapshot.invalidation_reason] += 1
        for code in snapshot.reason_codes:
            counters[symbol][code] += 1

    def _record_opportunities(self, symbol: str, snapshot, counters: dict[str, Counter[str]]) -> None:
        if snapshot.directional_bias != "long" or snapshot.entry_action == "BUY":
            return
        if "1h_trigger_missing" in snapshot.reason_codes:
            counters[symbol]["blocked_by_trigger"] += 1
        if "corridor_illegal" in snapshot.reason_codes or snapshot.invalidation_reason == "corridor_illegal":
            counters[symbol]["blocked_by_corridor"] += 1
        if snapshot.invalidation_reason in {"portfolio_risk_cap", "max_positions_reached"}:
            counters[symbol]["blocked_by_portfolio_risk_cap"] += 1

    def _opportunity_diagnostics(self, counters: dict[str, Counter[str]], symbols: list[str]) -> dict:
        by_symbol = {
            symbol: {
                "blocked_by_trigger": int(counters[symbol].get("blocked_by_trigger", 0)),
                "blocked_by_corridor": int(counters[symbol].get("blocked_by_corridor", 0)),
                "blocked_by_portfolio_risk_cap": int(counters[symbol].get("blocked_by_portfolio_risk_cap", 0)),
            }
            for symbol in symbols
        }
        totals = Counter()
        for symbol in symbols:
            totals.update(by_symbol[symbol])
        return {
            "by_symbol": by_symbol,
            "portfolio_totals": dict(totals),
        }

    def _per_asset_attribution(
        self,
        fill_log: list[dict],
        open_positions: dict,
        final_prices: dict[str, float],
        initial_equity: float,
        symbols: list[str],
    ) -> dict:
        metrics = {
            symbol: {
                "fill_count": 0,
                "trade_count": 0,
                "completed_trades": 0,
                "win_count": 0,
                "loss_count": 0,
                "avg_hold_hours": 0.0,
                "avg_stop_distance_pct": 0.0,
                "stop_hit_count": 0,
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "return_contribution_pct": 0.0,
            }
            for symbol in symbols
        }
        open_entries: dict[str, dict] = {}
        hold_samples: dict[str, list[float]] = defaultdict(list)
        stop_samples: dict[str, list[float]] = defaultdict(list)

        for fill in fill_log:
            symbol = fill["symbol"]
            metrics.setdefault(symbol, {
                "fill_count": 0,
                "trade_count": 0,
                "completed_trades": 0,
                "win_count": 0,
                "loss_count": 0,
                "avg_hold_hours": 0.0,
                "avg_stop_distance_pct": 0.0,
                "stop_hit_count": 0,
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "return_contribution_pct": 0.0,
            })
            metrics[symbol]["fill_count"] += 1
            if fill["side"] == "BUY":
                metrics[symbol]["trade_count"] += 1
                open_entries[symbol] = fill
                entry_price = float(fill.get("price", 0.0))
                stop_price = float(fill.get("stop_price", 0.0))
                if entry_price > 0 and stop_price > 0 and stop_price < entry_price:
                    stop_samples[symbol].append(((entry_price - stop_price) / entry_price) * 100)
            elif fill["side"] == "SELL":
                metrics[symbol]["completed_trades"] += 1
                realized_pnl = float(fill.get("realized_pnl", 0.0))
                metrics[symbol]["realized_pnl"] += realized_pnl
                if realized_pnl >= 0:
                    metrics[symbol]["win_count"] += 1
                else:
                    metrics[symbol]["loss_count"] += 1
                if fill.get("exit_reason") == "stop_breach_close":
                    metrics[symbol]["stop_hit_count"] += 1
                entry_fill = open_entries.pop(symbol, None)
                if entry_fill is not None:
                    hold_hours = (
                        pd.Timestamp(fill["ts"]) - pd.Timestamp(entry_fill["ts"])
                    ).total_seconds() / 3600.0
                    hold_samples[symbol].append(hold_hours)

        for symbol, position in open_positions.items():
            mark_price = float(final_prices.get(symbol, position.entry_price))
            unrealized = (mark_price - position.entry_price) * position.quantity
            metrics.setdefault(symbol, {
                "fill_count": 0,
                "trade_count": 0,
                "completed_trades": 0,
                "win_count": 0,
                "loss_count": 0,
                "avg_hold_hours": 0.0,
                "avg_stop_distance_pct": 0.0,
                "stop_hit_count": 0,
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "return_contribution_pct": 0.0,
            })
            metrics[symbol]["unrealized_pnl"] += unrealized
            if position.entry_price > 0 and position.stop_price > 0 and position.stop_price < position.entry_price:
                stop_samples[symbol].append(
                    ((position.entry_price - position.stop_price) / position.entry_price) * 100
                )

        for symbol in metrics:
            realized = float(metrics[symbol]["realized_pnl"])
            unrealized = float(metrics[symbol]["unrealized_pnl"])
            metrics[symbol]["avg_hold_hours"] = round(
                statistics.mean(hold_samples[symbol]) if hold_samples[symbol] else 0.0,
                4,
            )
            metrics[symbol]["avg_stop_distance_pct"] = round(
                statistics.mean(stop_samples[symbol]) if stop_samples[symbol] else 0.0,
                4,
            )
            metrics[symbol]["realized_pnl"] = round(realized, 6)
            metrics[symbol]["unrealized_pnl"] = round(unrealized, 6)
            metrics[symbol]["return_contribution_pct"] = round(
                ((realized + unrealized) / initial_equity) * 100,
                4,
            ) if initial_equity else 0.0
        return metrics

    def _evaluate_invariants(
        self,
        fill_log: list[dict],
        portfolio: PortfolioState,
        final_prices: dict[str, float],
        config: AthenaBotConfig,
    ) -> dict:
        issues: list[str] = []
        buy_counts: Counter[str] = Counter()
        sell_counts: Counter[str] = Counter()

        for fill in fill_log:
            symbol = fill["symbol"]
            quantity = float(fill.get("quantity", 0.0))
            gross = float(fill.get("gross", 0.0))
            fee = float(fill.get("fee", 0.0))
            if quantity <= 0:
                issues.append(f"non_positive_quantity:{symbol}")
            if gross < 0 or fee < 0:
                issues.append(f"negative_cash_component:{symbol}")
            if fill["side"] == "BUY":
                buy_counts[symbol] += 1
            elif fill["side"] == "SELL":
                sell_counts[symbol] += 1
                if sell_counts[symbol] > buy_counts[symbol]:
                    issues.append(f"sell_without_entry:{symbol}")

        if len(portfolio.positions) > config.max_positions:
            issues.append("max_positions_breached")
        if portfolio.cash < -0.01:
            issues.append("cash_negative")
        for symbol, position in portfolio.positions.items():
            if position.quantity <= 0:
                issues.append(f"open_position_non_positive:{symbol}")

        mtm_equity = portfolio.cash
        for symbol, position in portfolio.positions.items():
            mtm_equity += position.quantity * final_prices.get(symbol, position.entry_price)
        if abs(mtm_equity - portfolio.equity) > 0.01:
            issues.append("equity_mark_to_market_mismatch")

        return {
            "passed": not issues,
            "issues": sorted(set(issues)),
        }

    def _unrealized_pnl(self, portfolio: PortfolioState, final_prices: dict[str, float]) -> float:
        unrealized = 0.0
        for symbol, position in portfolio.positions.items():
            mark_price = float(final_prices.get(symbol, position.entry_price))
            unrealized += (mark_price - position.entry_price) * position.quantity
        return unrealized

    def _exposure_pct(self, equity_points: list[dict]) -> float:
        if not equity_points:
            return 0.0
        active = sum(1 for point in equity_points if point["open_positions"] > 0)
        return round((active / len(equity_points)) * 100, 4)

    def _counter_map_to_dict(self, counter_map: dict[str, Counter[str]], symbols: list[str]) -> dict:
        return {
            symbol: dict(counter_map.get(symbol, Counter()))
            for symbol in symbols
        }

    def _signature(self, payload: dict) -> str:
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _max_drawdown(self, equity_points: list[dict]) -> float:
        if not equity_points:
            return 0.0
        peak = equity_points[0]["equity"]
        max_drawdown = 0.0
        for point in equity_points:
            peak = max(peak, point["equity"])
            if peak:
                drawdown = (peak - point["equity"]) / peak
                max_drawdown = max(max_drawdown, drawdown)
        return round(max_drawdown * 100, 4)

from __future__ import annotations

from dataclasses import dataclass

from .config import AthenaBotConfig
from .models import PortfolioState, Position, SignalSnapshot
from .utils import now_utc, to_iso


@dataclass(slots=True)
class BrokerResult:
    portfolio: PortfolioState
    order: dict | None
    fill: dict | None
    notes: list[str]


class PaperBroker:
    def __init__(self, config: AthenaBotConfig | None = None):
        self.config = config or AthenaBotConfig()

    def apply(
        self,
        signal_snapshot: SignalSnapshot,
        portfolio_state: PortfolioState,
        next_bar: dict | None = None,
    ) -> BrokerResult:
        portfolio = PortfolioState.from_dict(portfolio_state.to_dict())
        symbol = signal_snapshot.symbol
        action = signal_snapshot.entry_action
        position = portfolio.positions.get(symbol)
        order = None
        fill = None
        notes: list[str] = []

        fill_price = self._resolve_fill_price(signal_snapshot, next_bar)
        fill_ts = self._resolve_fill_time(signal_snapshot, next_bar)
        fee_rate = self.config.fee_bps / 10_000.0

        if action == "BUY":
            if position is not None:
                return BrokerResult(portfolio, None, None, ["position_already_open"])
            risk_budget = portfolio.equity * self.config.per_position_risk
            stop_price = signal_snapshot.stop_price or signal_snapshot.latest_price * 0.98
            stop_distance = max(fill_price - stop_price, fill_price * 0.002)
            qty_by_risk = risk_budget / stop_distance
            cash_budget = portfolio.cash * min(signal_snapshot.size_fraction, 1.0)
            qty_by_cash = cash_budget / fill_price if fill_price else 0.0
            quantity = round(max(0.0, min(qty_by_risk, qty_by_cash)), 8)
            if quantity <= 0:
                return BrokerResult(portfolio, None, None, ["quantity_zero_after_risk_cap"])

            gross_cost = quantity * fill_price
            fee_paid = gross_cost * fee_rate
            if gross_cost + fee_paid > portfolio.cash and fill_price > 0:
                quantity = round(portfolio.cash / (fill_price * (1 + fee_rate)), 8)
                gross_cost = quantity * fill_price
                fee_paid = gross_cost * fee_rate
            if quantity <= 0:
                return BrokerResult(portfolio, None, None, ["quantity_zero_after_cash_cap"])

            risk_amount = quantity * stop_distance
            order = {
                "ts": fill_ts,
                "symbol": symbol,
                "side": "BUY",
                "order_type": "paper_market",
                "requested_size_fraction": signal_snapshot.size_fraction,
                "reason": signal_snapshot.invalidation_reason,
            }
            fill = {
                "ts": fill_ts,
                "symbol": symbol,
                "side": "BUY",
                "price": round(fill_price, 6),
                "quantity": quantity,
                "gross": round(gross_cost, 6),
                "fee": round(fee_paid, 6),
                "stop_price": round(stop_price, 6),
                "risk_amount": round(risk_amount, 6),
                "stop_distance": round(stop_distance, 6),
                "signal_type": signal_snapshot.signal_type,
                "source": "next_bar_open" if next_bar else "latest_close_proxy",
            }
            portfolio.cash = round(portfolio.cash - gross_cost - fee_paid, 6)
            portfolio.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=round(fill_price, 6),
                stop_price=round(stop_price, 6),
                risk_amount=round(risk_amount, 6),
                entry_time=fill_ts,
                last_update=fill_ts,
                entry_signal_type=signal_snapshot.signal_type,
            )
        elif action == "EXIT" and position is not None:
            gross_value = position.quantity * fill_price
            fee_paid = gross_value * fee_rate
            realized_pnl = (fill_price - position.entry_price) * position.quantity - fee_paid
            order = {
                "ts": fill_ts,
                "symbol": symbol,
                "side": "SELL",
                "order_type": "paper_market",
                "reason": signal_snapshot.invalidation_reason,
            }
            fill = {
                "ts": fill_ts,
                "symbol": symbol,
                "side": "SELL",
                "price": round(fill_price, 6),
                "quantity": position.quantity,
                "gross": round(gross_value, 6),
                "fee": round(fee_paid, 6),
                "realized_pnl": round(realized_pnl, 6),
                "entry_price": position.entry_price,
                "entry_time": position.entry_time,
                "exit_reason": signal_snapshot.invalidation_reason,
                "source": "next_bar_open" if next_bar else "latest_close_proxy",
            }
            portfolio.cash = round(portfolio.cash + gross_value - fee_paid, 6)
            del portfolio.positions[symbol]
        else:
            notes.append("no_fill")

        portfolio.updated_at = fill_ts
        portfolio.last_bar_ts = signal_snapshot.bar_close_ts
        self.mark_to_market(
            portfolio,
            {signal_snapshot.symbol: signal_snapshot.latest_price},
        )
        return BrokerResult(portfolio, order, fill, notes)

    def mark_to_market(
        self,
        portfolio_state: PortfolioState,
        latest_prices: dict[str, float],
    ) -> PortfolioState:
        equity = portfolio_state.cash
        for symbol, position in portfolio_state.positions.items():
            mark_price = latest_prices.get(symbol, position.entry_price)
            equity += position.quantity * mark_price
            position.last_update = to_iso(now_utc())
        portfolio_state.equity = round(equity, 6)
        portfolio_state.updated_at = to_iso(now_utc())
        return portfolio_state

    def _resolve_fill_price(self, signal_snapshot: SignalSnapshot, next_bar: dict | None) -> float:
        reference = signal_snapshot.latest_price
        if next_bar is not None:
            reference = float(next_bar["open"])
        slip = self.config.slippage_bps / 10_000.0
        if signal_snapshot.entry_action == "BUY":
            return round(reference * (1 + slip), 6)
        if signal_snapshot.entry_action == "EXIT":
            return round(reference * (1 - slip), 6)
        return round(reference, 6)

    def _resolve_fill_time(self, signal_snapshot: SignalSnapshot, next_bar: dict | None) -> str:
        if next_bar is not None:
            return str(next_bar["ts_open"])
        return signal_snapshot.bar_close_ts

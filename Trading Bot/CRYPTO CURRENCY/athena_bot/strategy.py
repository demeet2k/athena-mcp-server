from __future__ import annotations

from .config import AthenaBotConfig
from .models import DirectionState, FractalState, PortfolioState, SignalSnapshot


class StrategyEngine:
    def __init__(self, config: AthenaBotConfig | None = None):
        self.config = config or AthenaBotConfig()

    def decide(
        self,
        fractal_state: FractalState,
        direction_state: DirectionState,
        portfolio_state: PortfolioState,
        latest_price: float,
        existing_stop: float | None = None,
        extra_reason_codes: list[str] | None = None,
    ) -> SignalSnapshot:
        extra_reason_codes = extra_reason_codes or []
        existing_position = portfolio_state.positions.get(fractal_state.symbol)
        invalidation_reason = ""
        reason_codes = list(
            dict.fromkeys(
                extra_reason_codes
                + fractal_state.reason_codes
                + direction_state.reason_codes
            )
        )

        if not fractal_state.corridor_legal:
            action = "STAND_DOWN" if existing_position is None else "EXIT"
            invalidation_reason = "corridor_illegal"
        elif existing_position is not None:
            if latest_price <= existing_position.stop_price:
                action = "EXIT"
                invalidation_reason = "stop_breach_close"
            elif fractal_state.transition_score >= self.config.transition_block_threshold:
                action = "EXIT"
                invalidation_reason = "transition_extreme"
            elif direction_state.directional_bias != "long":
                action = "EXIT"
                invalidation_reason = "trend_lost"
            else:
                action = "HOLD"
                invalidation_reason = "position_valid"
        else:
            if len(portfolio_state.positions) >= self.config.max_positions:
                action = "STAND_DOWN"
                invalidation_reason = "max_positions_reached"
            elif portfolio_state.open_risk >= portfolio_state.equity * self.config.max_total_open_risk:
                action = "STAND_DOWN"
                invalidation_reason = "portfolio_risk_cap"
            elif not direction_state.entry_ready:
                action = "STAND_DOWN"
                invalidation_reason = "directional_filter_blocked"
            else:
                action = "BUY"
                invalidation_reason = "all_green"

        stop_price = existing_stop
        if action in {"BUY", "HOLD"}:
            stop_anchor = latest_price - (direction_state.atr * fractal_state.stop_atr_multiplier)
            stop_price = round(max(stop_anchor, latest_price * 0.5), 6)
        elif existing_position is not None:
            stop_price = existing_position.stop_price

        size_fraction = fractal_state.recommended_size_fraction if action == "BUY" else 0.0
        if action == "BUY" and fractal_state.fractal_regime == "transition_caution":
            size_fraction *= 0.75
        size_fraction = round(max(0.0, min(size_fraction, 1.0)), 4)

        return SignalSnapshot(
            symbol=fractal_state.symbol,
            bar_close_ts=fractal_state.bar_close_ts,
            timeframe_context=fractal_state.timeframe_context,
            fractal_regime=fractal_state.fractal_regime,
            transition_score=fractal_state.transition_score,
            cycle_alignment=fractal_state.cycle_alignment,
            phase_quality=fractal_state.phase_quality,
            volatility_regime=fractal_state.volatility_regime,
            directional_bias=direction_state.directional_bias,
            entry_action=action,
            size_fraction=size_fraction,
            stop_price=stop_price,
            invalidation_reason=invalidation_reason,
            reason_codes=reason_codes,
            composite_score=fractal_state.composite_score,
            signal_type=fractal_state.signal_type,
            latest_price=round(float(latest_price), 6),
            trigger_price=direction_state.trigger_price,
            atr=direction_state.atr,
            atr_pct=direction_state.atr_pct,
        )

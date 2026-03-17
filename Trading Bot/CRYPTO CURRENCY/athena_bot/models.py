from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Candle:
    symbol: str
    timeframe: str
    ts_open: str
    ts_close: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FractalState:
    symbol: str
    bar_close_ts: str
    timeframe_context: str
    fractal_regime: str
    signal_type: str
    composite_score: float
    transition_score: float
    cycle_alignment: float
    phase_quality: str
    volatility_regime: str
    recommended_size_fraction: float
    stop_atr_multiplier: float
    corridor_legal: bool
    reason_codes: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DirectionState:
    symbol: str
    bar_close_ts: str
    directional_bias: str
    trend_ok: bool
    trigger: str
    entry_ready: bool
    volume_ok: bool
    volatility_ok: bool
    atr: float
    atr_pct: float
    trigger_price: float
    reason_codes: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SignalSnapshot:
    symbol: str
    bar_close_ts: str
    timeframe_context: str
    fractal_regime: str
    transition_score: float
    cycle_alignment: float
    phase_quality: str
    volatility_regime: str
    directional_bias: str
    entry_action: str
    size_fraction: float
    stop_price: float | None
    invalidation_reason: str
    reason_codes: list[str] = field(default_factory=list)
    composite_score: float = 0.0
    signal_type: str = "QUALITY_READ"
    latest_price: float = 0.0
    trigger_price: float = 0.0
    atr: float = 0.0
    atr_pct: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: float
    entry_price: float
    stop_price: float
    risk_amount: float
    entry_time: str
    last_update: str
    entry_signal_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PortfolioState:
    cash: float
    equity: float
    last_bar_ts: str | None = None
    updated_at: str | None = None
    positions: dict[str, Position] = field(default_factory=dict)

    @property
    def open_risk(self) -> float:
        return sum(position.risk_amount for position in self.positions.values())

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["positions"] = {
            symbol: position.to_dict() for symbol, position in self.positions.items()
        }
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PortfolioState":
        positions = {
            symbol: Position(**position)
            for symbol, position in payload.get("positions", {}).items()
        }
        return cls(
            cash=float(payload.get("cash", 0.0)),
            equity=float(payload.get("equity", 0.0)),
            last_bar_ts=payload.get("last_bar_ts"),
            updated_at=payload.get("updated_at"),
            positions=positions,
        )

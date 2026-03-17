from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path


@dataclass(slots=True)
class AthenaBotConfig:
    """Configuration for the Athena paper-trading runtime."""

    base_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[1]
    )
    runtime_subdir: str = "runtime"
    symbols: tuple[str, ...] = ("BTC", "ETH", "SOL", "XRP")
    source_symbols: dict[str, str] = field(
        default_factory=lambda: {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT",
            "XRP": "XRPUSDT",
        }
    )
    primary_timeframe: str = "1h"
    context_timeframe: str = "4h"
    initial_equity: float = 10_000.0
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    per_position_risk: float = 0.005
    max_total_open_risk: float = 0.02
    max_positions: int = 4
    default_history_hours: int = 24 * 180
    replay_warmup_hours: int = 24 * 45
    stale_minutes: int = 90
    trend_4h_fast_ema: int = 20
    trend_4h_slow_ema: int = 50
    trigger_1h_ema: int = 20
    breakout_lookback: int = 20
    atr_period: int = 14
    min_volume_ratio: float = 0.6
    max_atr_pct: float = 0.08
    min_atr_pct: float = 0.001
    breakout_buffer_bps: float = 10.0
    transition_block_threshold: float = 0.90
    lppl_enabled: bool = False
    request_timeout_seconds: int = 20
    binance_base_url: str = "https://api.binance.com"
    kraken_base_url: str = "https://api.kraken.com"
    kraken_pairs: dict[str, str] = field(
        default_factory=lambda: {
            "BTC": "XXBTZUSD",
            "ETH": "XETHZUSD",
            "SOL": "SOLUSD",
            "XRP": "XXRPZUSD",
        }
    )

    def __post_init__(self) -> None:
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        for subdir in (
            "candles/1h",
            "candles/4h",
            "signals",
            "orders",
            "fills",
            "positions",
            "equity",
            "journals",
            "replay",
            "tuning",
        ):
            (self.runtime_dir / subdir).mkdir(parents=True, exist_ok=True)

    @property
    def runtime_dir(self) -> Path:
        return self.base_dir / self.runtime_subdir

    def candle_path(self, symbol: str, timeframe: str) -> Path:
        return self.runtime_dir / "candles" / timeframe / f"{symbol}.csv"

    @property
    def signals_dir(self) -> Path:
        return self.runtime_dir / "signals"

    @property
    def orders_path(self) -> Path:
        return self.runtime_dir / "orders" / "orders.jsonl"

    @property
    def fills_path(self) -> Path:
        return self.runtime_dir / "fills" / "fills.jsonl"

    @property
    def portfolio_state_path(self) -> Path:
        return self.runtime_dir / "positions" / "portfolio_state.json"

    @property
    def latest_positions_path(self) -> Path:
        return self.runtime_dir / "positions" / "latest_positions.json"

    @property
    def equity_curve_path(self) -> Path:
        return self.runtime_dir / "equity" / "equity_curve.csv"

    @property
    def journal_path(self) -> Path:
        return self.runtime_dir / "journals" / "journal.jsonl"

    @property
    def replay_dir(self) -> Path:
        return self.runtime_dir / "replay"

    @property
    def tuning_dir(self) -> Path:
        return self.runtime_dir / "tuning"

    def with_overrides(self, **overrides) -> "AthenaBotConfig":
        return replace(self, **overrides)

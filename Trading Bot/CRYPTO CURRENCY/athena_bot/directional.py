from __future__ import annotations

import pandas as pd

from .config import AthenaBotConfig
from .models import DirectionState
from .utils import atr, ema


class DirectionalFilter:
    def __init__(
        self,
        config: AthenaBotConfig | None = None,
        cache: dict | None = None,
    ):
        self.config = config or AthenaBotConfig()
        self._cache = cache if cache is not None else {}

    def with_config(self, config: AthenaBotConfig) -> "DirectionalFilter":
        return type(self)(config, cache=self._cache)

    def evaluate(self, symbol: str, bars_1h: pd.DataFrame, bars_4h: pd.DataFrame) -> DirectionState:
        cache_key = self._cache_key(symbol, bars_1h, bars_4h)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return DirectionState(**cached)

        min_1h = max(self.config.breakout_lookback + 2, self.config.atr_period + 5)
        if len(bars_1h) < min_1h or len(bars_4h) < self.config.trend_4h_slow_ema + 2:
            state = DirectionState(
                symbol=symbol,
                bar_close_ts="",
                directional_bias="flat",
                trend_ok=False,
                trigger="none",
                entry_ready=False,
                volume_ok=False,
                volatility_ok=False,
                atr=0.0,
                atr_pct=0.0,
                trigger_price=0.0,
                reason_codes=["insufficient_directional_context"],
            )
            self._cache[cache_key] = state.to_dict()
            return state

        close_4h = bars_4h["close"].astype(float)
        close_1h = bars_1h["close"].astype(float)
        low_1h = bars_1h["low"].astype(float)
        volume_1h = bars_1h["volume"].astype(float)

        ema_fast_4h = ema(close_4h, self.config.trend_4h_fast_ema)
        ema_slow_4h = ema(close_4h, self.config.trend_4h_slow_ema)
        ema_1h = ema(close_1h, self.config.trigger_1h_ema)
        atr_series = atr(bars_1h, period=self.config.atr_period)

        latest_price = float(close_1h.iloc[-1])
        latest_4h = float(close_4h.iloc[-1])
        latest_atr = float(atr_series.iloc[-1]) if not pd.isna(atr_series.iloc[-1]) else 0.0
        atr_pct = latest_atr / latest_price if latest_price else 0.0

        trend_ok = bool(
            latest_4h > float(ema_fast_4h.iloc[-1]) > float(ema_slow_4h.iloc[-1])
        )
        breakout_level = float(close_1h.iloc[-(self.config.breakout_lookback + 1):-1].max())
        breakout_buffer = 1 + (self.config.breakout_buffer_bps / 10_000.0)
        breakout = latest_price > breakout_level * breakout_buffer

        latest_ema_1h = float(ema_1h.iloc[-1])
        pullback = bool(
            trend_ok
            and low_1h.iloc[-1] <= latest_ema_1h * 1.002
            and latest_price > latest_ema_1h
            and close_1h.iloc[-2] <= float(ema_1h.iloc[-2]) * 1.01
        )

        median_volume = float(volume_1h.iloc[-20:].median())
        volume_ok = median_volume > 0 and float(volume_1h.iloc[-1]) >= median_volume * self.config.min_volume_ratio
        volatility_ok = self.config.min_atr_pct <= atr_pct <= self.config.max_atr_pct

        trigger = "none"
        trigger_price = latest_price
        if breakout:
            trigger = "breakout"
            trigger_price = breakout_level
        elif pullback:
            trigger = "pullback"
            trigger_price = latest_ema_1h

        direction = "long" if trend_ok else "flat"
        entry_ready = trend_ok and trigger != "none" and volume_ok and volatility_ok
        reason_codes = []
        if not trend_ok:
            reason_codes.append("4h_trend_not_constructive")
        if trigger == "none":
            reason_codes.append("1h_trigger_missing")
        if not volume_ok:
            reason_codes.append("volume_thin")
        if not volatility_ok:
            reason_codes.append("volatility_out_of_bounds")
        if entry_ready:
            reason_codes.append(f"trigger:{trigger}")

        state = DirectionState(
            symbol=symbol,
            bar_close_ts=bars_1h["ts_close"].iloc[-1].isoformat(),
            directional_bias=direction,
            trend_ok=trend_ok,
            trigger=trigger,
            entry_ready=entry_ready,
            volume_ok=volume_ok,
            volatility_ok=volatility_ok,
            atr=round(latest_atr, 6),
            atr_pct=round(atr_pct, 6),
            trigger_price=round(trigger_price, 6),
            reason_codes=reason_codes,
            raw={
                "ema_fast_4h": round(float(ema_fast_4h.iloc[-1]), 6),
                "ema_slow_4h": round(float(ema_slow_4h.iloc[-1]), 6),
                "ema_1h": round(latest_ema_1h, 6),
                "breakout_level": round(breakout_level, 6),
            },
        )
        self._cache[cache_key] = state.to_dict()
        return state

    def _cache_key(self, symbol: str, bars_1h: pd.DataFrame, bars_4h: pd.DataFrame) -> tuple:
        last_1h = bars_1h["ts_close"].iloc[-1].isoformat() if not bars_1h.empty else ""
        last_4h = bars_4h["ts_close"].iloc[-1].isoformat() if not bars_4h.empty else ""
        return (
            symbol,
            len(bars_1h),
            len(bars_4h),
            last_1h,
            last_4h,
            self.config.trend_4h_fast_ema,
            self.config.trend_4h_slow_ema,
            self.config.trigger_1h_ema,
            self.config.breakout_lookback,
            self.config.atr_period,
            self.config.min_volume_ratio,
            self.config.min_atr_pct,
            self.config.max_atr_pct,
            self.config.breakout_buffer_bps,
        )

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .config import AthenaBotConfig
from .models import FractalState


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from time_fractal_engine import HolographicPhaseComputer, KernelEngine  # noqa: E402
from trading_bot_signals import FractalScorer, RiskManager, SignalAggregator  # noqa: E402


class FractalCore:
    def __init__(
        self,
        config: AthenaBotConfig | None = None,
        base_cache: dict | None = None,
    ):
        self.config = config or AthenaBotConfig()
        self._base_cache = base_cache if base_cache is not None else {}

    def with_config(self, config: AthenaBotConfig) -> "FractalCore":
        return type(self)(config, base_cache=self._base_cache)

    def evaluate(self, symbol: str, bars_1h: pd.DataFrame, bars_4h: pd.DataFrame) -> FractalState:
        if bars_4h.empty:
            return FractalState(
                symbol=symbol,
                bar_close_ts="",
                timeframe_context="4h/1h",
                fractal_regime="no_context",
                signal_type="QUALITY_READ",
                composite_score=0.0,
                transition_score=1.0,
                cycle_alignment=0.0,
                phase_quality="unknown",
                volatility_regime="unknown",
                recommended_size_fraction=0.0,
                stop_atr_multiplier=0.0,
                corridor_legal=False,
                reason_codes=["insufficient_4h_context"],
            )

        base_state = self._base_state(symbol, bars_1h, bars_4h)
        scores = dict(base_state["scores"])
        composite = dict(base_state["composite"])
        risk = dict(base_state["risk"])
        transition_score = base_state["transition_score"]
        phase_quality = base_state["phase_quality"]
        fractal_regime = self._classify_regime(composite, transition_score)
        reason_codes = [composite["signal_type"].lower(), composite["macro_bias"]]
        if base_state["analysis_source_1h"]:
            reason_codes.append("analysis_source_1h_fallback")
        corridor_legal = self._corridor_legal(composite, scores, transition_score)
        if not corridor_legal:
            reason_codes.append("corridor_illegal")

        payload = {
            **scores,
            **composite,
            **risk,
        }
        return FractalState(
            symbol=symbol,
            bar_close_ts=base_state["bar_close_ts"],
            timeframe_context="4h->1h",
            fractal_regime=fractal_regime,
            signal_type=composite["signal_type"],
            composite_score=float(composite["composite_score"]),
            transition_score=transition_score,
            cycle_alignment=float(scores.get("cycle_alignment", 0.0)),
            phase_quality=str(phase_quality),
            volatility_regime=str(composite.get("vol_regime", "unknown")),
            recommended_size_fraction=float(risk["max_position_pct"]),
            stop_atr_multiplier=float(risk["stop_atr_multiplier"]),
            corridor_legal=corridor_legal,
            reason_codes=reason_codes,
            raw=payload,
        )

    def _base_state(self, symbol: str, bars_1h: pd.DataFrame, bars_4h: pd.DataFrame) -> dict:
        cache_key = self._cache_key(symbol, bars_1h, bars_4h)
        cached = self._base_cache.get(cache_key)
        if cached is not None:
            return cached

        analysis_frame = bars_4h if len(bars_4h) >= 200 else bars_1h
        close_series = analysis_frame["close"].astype(float)
        scores = {
            **self._default_lppl(),
            **FractalScorer.score_dsi(close_series),
            **FractalScorer.score_elliott(close_series),
            **FractalScorer.score_kondratiev(),
            **FractalScorer.score_volatility_structure(close_series),
            **self._score_holographic_phase(analysis_frame),
        }
        if self.config.lppl_enabled:
            scores.update(FractalScorer.score_lppl(close_series))

        composite = SignalAggregator.compute_composite(scores)
        risk = RiskManager.compute_position_sizing(composite)
        transition_score = round(
            max(
                scores.get("phase_score", 0.0),
                scores.get("kwave_transition_score", 0.0),
                scores.get("lppl_score", 0.0),
            ),
            4,
        )
        phase_quality = (
            scores.get("octave_1_quality")
            or scores.get("octave_2_quality")
            or "unknown"
        )
        payload = {
            "scores": scores,
            "composite": composite,
            "risk": risk,
            "transition_score": transition_score,
            "phase_quality": phase_quality,
            "analysis_source_1h": analysis_frame is bars_1h,
            "bar_close_ts": bars_1h["ts_close"].iloc[-1].isoformat(),
        }
        self._base_cache[cache_key] = payload
        return payload

    def _cache_key(self, symbol: str, bars_1h: pd.DataFrame, bars_4h: pd.DataFrame) -> tuple:
        last_1h = bars_1h["ts_close"].iloc[-1].isoformat() if not bars_1h.empty else ""
        last_4h = bars_4h["ts_close"].iloc[-1].isoformat() if not bars_4h.empty else ""
        return (
            symbol,
            len(bars_1h),
            len(bars_4h),
            last_1h,
            last_4h,
            bool(self.config.lppl_enabled),
        )

    def _default_lppl(self) -> dict:
        return {
            "lppl_score": 0.0,
            "lppl_lambda": None,
            "lppl_r2": 0.0,
            "lppl_tc_offset": None,
            "lppl_regime": "disabled",
        }

    def _score_holographic_phase(self, bars_4h: pd.DataFrame) -> dict:
        dates = pd.to_datetime(bars_4h["ts_close"], utc=True)
        prices = bars_4h["close"].astype(float).reset_index(drop=True)
        numeric_days = (
            (dates - dates.iloc[0]).dt.total_seconds() / 86400.0
        ).astype(float)
        nexus = HolographicPhaseComputer.compute_nexus_proximity(
            prices.reset_index(drop=True), numeric_days.values
        )
        latest_nexus = float(nexus[-1]) if len(nexus) else 0.0

        btc_genesis = pd.Timestamp("2009-01-03", tz="UTC")
        days_from_genesis = (
            dates.iloc[-1].to_pydatetime() - btc_genesis.to_pydatetime()
        ).total_seconds() / 86400.0
        alignment_scales = [12, 36, 64, 108, 192, 384]
        boundary_count = 0
        for scale in alignment_scales:
            phase = (days_from_genesis % scale) / scale
            if min(phase, 1 - phase) < 0.05:
                boundary_count += 1
        cycle_alignment = boundary_count / len(alignment_scales)

        octave_phases = {}
        for n in range(1, 6):
            scale = KernelEngine.octave_scale(n)
            quality = KernelEngine.phase_quality(days_from_genesis, scale)
            octave_phases[f"octave_{n}_quality"] = quality["quality"]
            octave_phases[f"octave_{n}_phase"] = round(float(quality["phase"]), 4)

        return {
            "phase_score": round(max(latest_nexus, cycle_alignment), 4),
            "nexus_score": round(latest_nexus, 4),
            "cycle_alignment": round(cycle_alignment, 4),
            **octave_phases,
        }

    def _classify_regime(self, composite: dict, transition_score: float) -> str:
        if (
            transition_score >= self.config.transition_block_threshold
            or composite["signal_type"] == "NEXUS_ALERT"
        ):
            return "transition_extreme"
        if composite["signal_type"] == "REGIME_SHIFT":
            return "transition_caution"
        if composite["macro_bias"] == "bullish_structural":
            return "constructive"
        if composite["macro_bias"] == "bearish_caution":
            return "macro_caution"
        return "balanced"

    def _corridor_legal(self, composite: dict, scores: dict, transition_score: float) -> bool:
        if composite["signal_type"] == "NEXUS_ALERT":
            return False
        if transition_score >= self.config.transition_block_threshold:
            return False
        if scores.get("vol_regime") == "expanding" and scores.get("cycle_alignment", 0.0) >= 0.67:
            return False
        return True

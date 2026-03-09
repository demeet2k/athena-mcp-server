"""
TIME FRACTAL TRADING BOT - PRODUCTION SIGNAL MODULE
=====================================================
Converts the time-fractal engine into actionable trading signals.

Architecture:
  1. DataManager: loads historical data + updates with latest prices
  2. FractalScorer: runs all 6 framework layers on each asset
  3. SignalAggregator: combines layers into composite trading signals
  4. RiskManager: position sizing based on phase quality
  5. BotRunner: main loop that produces signals at configurable intervals

Signal Types (from strongest to weakest):
  NEXUS_ALERT:  Multiple octave scales aligning + LPPL acceleration
  REGIME_SHIFT: DSI lambda matching kernel + volatility expansion
  PHASE_EDGE:   Single-scale phase boundary + momentum alignment
  QUALITY_READ: Phase quality reading (trend quality indicator)

The Oracle Uncertainty Principle applies:
  - We predict REGIME TYPE (sigma), not specific prices (q)
  - Delta(Structure) * Delta(Timing) >= h_oracle
"""

import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from time_fractal_engine import (
    KernelEngine, LPPLDetector, DSIScanner, ElliottWaveDetector,
    KondratievDetector, HolographicPhaseComputer, TimeFractalSignalGenerator
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FOREX_DIR = os.path.join(BASE_DIR, "forex_data")
SIGNALS_DIR = os.path.join(BASE_DIR, "bot_signals")
os.makedirs(SIGNALS_DIR, exist_ok=True)


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except:
        pass
    sys.stdout.flush()


# =============================================================================
# SECTION 1: DATA MANAGER
# =============================================================================

class DataManager:
    """Loads and manages historical + live data for all tracked assets."""

    def __init__(self):
        self.crypto_data = {}
        self.forex_data = {}
        self.load_historical()

    def load_historical(self):
        """Load all available historical data."""
        # Crypto
        import glob
        crypto_files = glob.glob(os.path.join(DATA_DIR, "*_full_history.csv"))
        for path in crypto_files:
            symbol = os.path.basename(path).replace("_full_history.csv", "")
            try:
                df = pd.read_csv(path, parse_dates=['date'])
                df = df.sort_values('date').reset_index(drop=True)
                if 'close' in df.columns:
                    self.crypto_data[symbol] = df
            except Exception as e:
                log(f"  Warning: Could not load {symbol}: {e}")

        # Forex
        forex_files = glob.glob(os.path.join(FOREX_DIR, "USD_*_history.csv"))
        for path in forex_files:
            fname = os.path.basename(path)
            pair = fname.replace("_history.csv", "")
            try:
                df = pd.read_csv(path, parse_dates=['date'])
                df = df.sort_values('date').reset_index(drop=True)
                col = pair
                if col in df.columns:
                    self.forex_data[pair] = df
            except Exception as e:
                log(f"  Warning: Could not load {pair}: {e}")

        log(f"  Loaded {len(self.crypto_data)} crypto + {len(self.forex_data)} forex assets")

    def get_prices(self, symbol, lookback_days=None):
        """Get price series for a symbol."""
        if symbol in self.crypto_data:
            df = self.crypto_data[symbol]
            prices = df['close']
            dates = df['date']
        elif symbol in self.forex_data:
            df = self.forex_data[symbol]
            prices = df[symbol]
            dates = df['date']
        else:
            return None, None

        if lookback_days:
            cutoff = datetime.now() - timedelta(days=lookback_days)
            mask = dates >= pd.Timestamp(cutoff)
            return prices[mask].reset_index(drop=True), dates[mask].reset_index(drop=True)

        return prices, dates


# =============================================================================
# SECTION 2: FRACTAL SCORER - Runs All 6 Framework Layers
# =============================================================================

class FractalScorer:
    """
    Computes time-fractal scores from all 6 framework layers:
      1. LPPL (Sornette) - bubble/antibubble proximity
      2. DSI (Discrete Scale Invariance) - kernel lambda detection
      3. Elliott Wave - 5-3 pattern position
      4. Kondratiev - long-wave phase
      5. Holographic Phase - multi-octave alignment
      6. Volatility Structure - scale-dependent regime
    """

    @staticmethod
    def score_lppl(prices, lookback=300):
        """
        Layer 1: LPPL bubble detection score.
        Returns 0-1 where 1 = strong LPPL signature detected.
        """
        if len(prices) < lookback:
            return {'lppl_score': 0.0, 'lppl_lambda': None, 'lppl_r2': 0.0,
                    'lppl_tc_offset': None, 'lppl_regime': 'none'}

        window = prices.iloc[-lookback:]
        dates_numeric = np.arange(len(window), dtype=float)

        try:
            result = LPPLDetector.fit_lppl(window, dates_numeric)
            if result and result['r_squared'] > 0.6:
                # Score based on: R2 quality + kernel alignment + proximity to tc
                r2_score = result['r_squared']
                kernel_score = result['kernel_alignment']
                # Closer tc = more urgent
                tc_proximity = 1.0 / (1.0 + abs(result['tc_date_offset'] / 30))

                composite = (r2_score * 0.4 + kernel_score * 0.3 + tc_proximity * 0.3)

                return {
                    'lppl_score': round(min(composite, 1.0), 4),
                    'lppl_lambda': round(result['lambda_ratio'], 3),
                    'lppl_nearest_kernel': result['nearest_kernel_lambda'],
                    'lppl_r2': round(result['r_squared'], 4),
                    'lppl_tc_offset': round(result['tc_date_offset'], 1),
                    'lppl_regime': result['regime'],
                    'lppl_m': round(result['m'], 4),
                }
        except:
            pass

        return {'lppl_score': 0.0, 'lppl_lambda': None, 'lppl_r2': 0.0,
                'lppl_tc_offset': None, 'lppl_regime': 'none'}

    @staticmethod
    def score_dsi(prices, lookback=500):
        """
        Layer 2: DSI kernel alignment score.
        Detects discrete scale invariance and checks kernel alignment.
        """
        if len(prices) < 200:
            return {'dsi_score': 0.0, 'dsi_lambdas': [], 'dsi_best_alignment': 0.0}

        window = prices.iloc[-min(lookback, len(prices)):]
        try:
            detections = DSIScanner.detect_log_periodicity(window)
            if not detections:
                return {'dsi_score': 0.0, 'dsi_lambdas': [], 'dsi_best_alignment': 0.0}

            # Score: best alignment * power
            best = detections[0]
            top_3 = detections[:3]

            # Weighted average of top detections
            total_power = sum(d['power'] for d in top_3)
            if total_power > 0:
                weighted_alignment = sum(d['kernel_alignment'] * d['power'] for d in top_3) / total_power
            else:
                weighted_alignment = 0

            return {
                'dsi_score': round(min(weighted_alignment, 1.0), 4),
                'dsi_lambdas': [d['lambda'] for d in top_3],
                'dsi_nearest_kernels': [d['nearest_kernel_lambda'] for d in top_3],
                'dsi_best_alignment': round(best['kernel_alignment'], 4),
                'dsi_best_power': round(best['power'], 4),
            }
        except:
            return {'dsi_score': 0.0, 'dsi_lambdas': [], 'dsi_best_alignment': 0.0}

    @staticmethod
    def score_elliott(prices, lookback=500):
        """
        Layer 3: Elliott Wave pattern score.
        Measures Fibonacci adherence in recent swing structure.
        """
        if len(prices) < 100:
            return {'elliott_score': 0.0, 'elliott_fib_adherence': 0.0}

        window = prices.iloc[-min(lookback, len(prices)):]
        try:
            patterns = ElliottWaveDetector.detect_impulse_pattern(window, min_order=5, max_order=30)
            if not patterns:
                return {'elliott_score': 0.0, 'elliott_fib_adherence': 0.0}

            # Best pattern by Fibonacci adherence
            best = max(patterns, key=lambda p: p['fibonacci_adherence'])
            return {
                'elliott_score': round(best['fibonacci_adherence'], 4),
                'elliott_fib_adherence': round(best['fibonacci_adherence'], 4),
                'elliott_scale': best['scale'],
                'elliott_patterns_found': len(patterns),
            }
        except:
            return {'elliott_score': 0.0, 'elliott_fib_adherence': 0.0}

    @staticmethod
    def score_kondratiev():
        """
        Layer 4: Kondratiev wave phase score.
        Returns current phase position and quality.
        """
        kwave = KondratievDetector.current_kwave_phase(datetime.now().year)
        # Convert phase to a "transition proximity" score
        # Near season boundaries (0.25, 0.5, 0.75, 1.0) = higher transition risk
        pos = kwave.get('cycle_position', 0.5)
        nearest_boundary = min(abs(pos - b) for b in [0, 0.25, 0.5, 0.75, 1.0])
        transition_score = 1 - (nearest_boundary / 0.125)  # Max distance = 0.125

        return {
            'kwave_number': kwave.get('wave_number', '?'),
            'kwave_season': kwave.get('season', '?'),
            'kwave_element': kwave.get('element', '?'),
            'kwave_quality': kwave.get('quality', '?'),
            'kwave_position': round(kwave.get('cycle_position', 0), 4),
            'kwave_transition_score': round(max(0, min(1, transition_score)), 4),
        }

    @staticmethod
    def score_holographic_phase(prices, dates):
        """
        Layer 5: Holographic phase alignment score.
        Multi-octave cycle alignment and nexus proximity.
        """
        if len(prices) < 50:
            return {'phase_score': 0.0, 'nexus_score': 0.0, 'cycle_alignment': 0.0}

        try:
            dates_dt = pd.to_datetime(dates)
            dates_numeric = (dates_dt - dates_dt.min()).dt.days.values.astype(float)

            # Nexus proximity
            nexus = HolographicPhaseComputer.compute_nexus_proximity(prices, dates_numeric)
            latest_nexus = nexus[-1] if len(nexus) > 0 else 0

            # Cycle alignment
            alignment_scales = [12, 36, 64, 108, 192, 384]
            boundary_count = 0
            for scale in alignment_scales:
                if scale < len(prices):
                    phase = (dates_numeric[-1] % scale) / scale
                    dist_to_boundary = min(phase, 1 - phase)
                    if dist_to_boundary < 0.05:
                        boundary_count += 1

            cycle_alignment = boundary_count / len(alignment_scales)

            # Phase quality at each octave
            octave_phases = {}
            btc_genesis = pd.Timestamp("2009-01-03")
            days_from_genesis = (dates_dt.iloc[-1] - btc_genesis).days
            for n in range(1, 6):
                scale = KernelEngine.octave_scale(n)
                pq = KernelEngine.phase_quality(days_from_genesis, scale)
                octave_phases[f'octave_{n}_quality'] = pq['quality']
                octave_phases[f'octave_{n}_phase'] = round(pq['phase'], 4)

            return {
                'phase_score': round(max(latest_nexus, cycle_alignment), 4),
                'nexus_score': round(latest_nexus, 4),
                'cycle_alignment': round(cycle_alignment, 4),
                **octave_phases,
            }
        except:
            return {'phase_score': 0.0, 'nexus_score': 0.0, 'cycle_alignment': 0.0}

    @staticmethod
    def score_volatility_structure(prices):
        """
        Layer 6: Volatility regime analysis at kernel scales.
        """
        if len(prices) < 200:
            return {'vol_score': 0.0, 'vol_regime': 'unknown', 'vol_expanding': False}

        try:
            log_returns = np.log(prices / prices.shift(1)).dropna()

            vol_7d = log_returns.iloc[-7:].std() * np.sqrt(252)
            vol_30d = log_returns.iloc[-30:].std() * np.sqrt(252)
            vol_90d = log_returns.iloc[-90:].std() * np.sqrt(252) if len(log_returns) >= 90 else vol_30d
            vol_200d = log_returns.iloc[-200:].std() * np.sqrt(252) if len(log_returns) >= 200 else vol_90d

            # Regime classification
            expanding = vol_7d > vol_30d > vol_90d
            contracting = vol_7d < vol_30d < vol_90d

            if expanding:
                regime = 'expanding'
                vol_score = min(vol_7d / vol_200d, 2.0) / 2.0  # Normalized 0-1
            elif contracting:
                regime = 'contracting'
                vol_score = 0.3  # Low urgency
            else:
                regime = 'mixed'
                vol_score = 0.5

            # Check if volatility at kernel octave scales differs from random
            kernel_vols = {}
            for scale in [36, 108, 324]:
                if scale < len(log_returns):
                    kernel_vols[f'vol_{scale}d'] = round(
                        log_returns.iloc[-scale:].std() * np.sqrt(252), 6)

            return {
                'vol_score': round(vol_score, 4),
                'vol_regime': regime,
                'vol_expanding': expanding,
                'vol_contracting': contracting,
                'vol_7d': round(float(vol_7d), 6),
                'vol_30d': round(float(vol_30d), 6),
                'vol_90d': round(float(vol_90d), 6),
                **kernel_vols,
            }
        except:
            return {'vol_score': 0.0, 'vol_regime': 'unknown', 'vol_expanding': False}


# =============================================================================
# SECTION 3: SIGNAL AGGREGATOR
# =============================================================================

class SignalAggregator:
    """
    Combines all 6 framework layers into composite trading signals.

    Signal Hierarchy:
      NEXUS_ALERT (0.85-1.0):  phase_score > 0.7 AND (lppl_score > 0.6 OR dsi_score > 0.7)
      REGIME_SHIFT (0.65-0.85): dsi_score > 0.6 AND vol_expanding
      PHASE_EDGE (0.40-0.65):   phase_score > 0.5 AND elliott_score > 0.5
      QUALITY_READ (0.0-0.40):  baseline phase quality information

    Weights (calibrated from LPPL bubble analysis results):
      LPPL:         25%  (strongest predictor of critical transitions)
      DSI:          20%  (kernel alignment validation)
      Holographic:  20%  (multi-scale cycle structure)
      Volatility:   15%  (regime confirmation)
      Elliott:      10%  (pattern structure)
      Kondratiev:   10%  (macro backdrop)
    """

    WEIGHTS = {
        'lppl': 0.25,
        'dsi': 0.20,
        'holographic': 0.20,
        'volatility': 0.15,
        'elliott': 0.10,
        'kondratiev': 0.10,
    }

    @staticmethod
    def compute_composite(scores):
        """
        Compute composite signal from all layers.
        Returns signal type, strength, and full score breakdown.
        """
        w = SignalAggregator.WEIGHTS

        # Extract layer scores
        lppl_s = scores.get('lppl_score', 0)
        dsi_s = scores.get('dsi_score', 0)
        phase_s = scores.get('phase_score', 0)
        vol_s = scores.get('vol_score', 0)
        elliott_s = scores.get('elliott_score', 0)
        kwave_s = scores.get('kwave_transition_score', 0)

        # Weighted composite
        composite = (
            w['lppl'] * lppl_s +
            w['dsi'] * dsi_s +
            w['holographic'] * phase_s +
            w['volatility'] * vol_s +
            w['elliott'] * elliott_s +
            w['kondratiev'] * kwave_s
        )

        # Classify signal type
        vol_expanding = scores.get('vol_expanding', False)

        if phase_s > 0.7 and (lppl_s > 0.6 or dsi_s > 0.7):
            signal_type = 'NEXUS_ALERT'
            # Boost composite for nexus condition
            composite = max(composite, 0.85)
        elif dsi_s > 0.6 and vol_expanding:
            signal_type = 'REGIME_SHIFT'
            composite = max(composite, 0.65)
        elif phase_s > 0.5 and elliott_s > 0.5:
            signal_type = 'PHASE_EDGE'
            composite = max(composite, 0.40)
        else:
            signal_type = 'QUALITY_READ'

        # Determine quality interpretation
        kwave_season = scores.get('kwave_season', 'unknown')
        kwave_element = scores.get('kwave_element', 'unknown')
        vol_regime = scores.get('vol_regime', 'unknown')

        if kwave_season in ['Autumn', 'Winter']:
            macro_bias = 'bearish_caution'
        elif kwave_season in ['Spring', 'Summer']:
            macro_bias = 'bullish_structural'
        else:
            macro_bias = 'neutral'

        return {
            'composite_score': round(min(composite, 1.0), 4),
            'signal_type': signal_type,
            'macro_bias': macro_bias,
            'kwave_season': kwave_season,
            'kwave_element': kwave_element,
            'vol_regime': vol_regime,
            'layer_scores': {
                'lppl': round(lppl_s, 4),
                'dsi': round(dsi_s, 4),
                'holographic': round(phase_s, 4),
                'volatility': round(vol_s, 4),
                'elliott': round(elliott_s, 4),
                'kondratiev': round(kwave_s, 4),
            }
        }


# =============================================================================
# SECTION 4: RISK MANAGER
# =============================================================================

class RiskManager:
    """
    Position sizing based on time-fractal phase quality.

    The oracle uncertainty principle says we can read sigma (regime quality)
    but NOT q (specific prices). So risk management adapts EXPOSURE to regime,
    not direction.

    Rules:
      NEXUS_ALERT:  Reduce to 25% position (high transition probability)
      REGIME_SHIFT: Reduce to 50% position (regime changing)
      PHASE_EDGE:   Normal 75% position (approaching boundary)
      QUALITY_READ: Full 100% position (stable regime)

    When vol_expanding AND nexus_score > 0.7:
      -> Tighten stops to 1x ATR (instead of 2x)
      -> Reduce max position by additional 25%

    When contracting volatility:
      -> Widen stops to 3x ATR
      -> Can increase position to 125% (breakout preparation)
    """

    @staticmethod
    def compute_position_sizing(signal, base_position=1.0):
        """
        Compute recommended position size based on signal.

        Args:
            signal: output from SignalAggregator.compute_composite()
            base_position: base position size (1.0 = 100%)

        Returns:
            position_pct: recommended position as fraction of base
            stop_atr_multiplier: recommended stop distance in ATR units
            rationale: human-readable explanation
        """
        signal_type = signal.get('signal_type', 'QUALITY_READ')
        vol_regime = signal.get('vol_regime', 'mixed')
        composite = signal.get('composite_score', 0)
        layers = signal.get('layer_scores', {})

        # Base position by signal type
        if signal_type == 'NEXUS_ALERT':
            position_pct = 0.25
            stop_atr = 1.0
            rationale = "NEXUS ALERT: Multiple octave scales aligning. High transition probability. Minimal exposure."
        elif signal_type == 'REGIME_SHIFT':
            position_pct = 0.50
            stop_atr = 1.5
            rationale = "REGIME SHIFT: DSI kernel alignment + volatility expansion. Reduced exposure."
        elif signal_type == 'PHASE_EDGE':
            position_pct = 0.75
            stop_atr = 2.0
            rationale = "PHASE EDGE: Approaching phase boundary. Moderate caution."
        else:
            position_pct = 1.0
            stop_atr = 2.0
            rationale = "QUALITY READ: Stable regime. Standard position."

        # Volatility adjustments
        if vol_regime == 'expanding':
            position_pct *= 0.75
            stop_atr = max(stop_atr * 0.8, 1.0)
            rationale += " [Vol expanding: further reduced.]"
        elif vol_regime == 'contracting':
            position_pct = min(position_pct * 1.25, base_position)
            stop_atr = min(stop_atr * 1.5, 3.0)
            rationale += " [Vol contracting: widened stops, slight size increase.]"

        # Kondratiev macro adjustment
        if signal.get('kwave_season') in ['Autumn', 'Winter']:
            position_pct *= 0.9
            rationale += " [K-wave Autumn/Winter: macro caution.]"

        return {
            'position_pct': round(position_pct, 4),
            'stop_atr_multiplier': round(stop_atr, 2),
            'max_position_pct': round(min(position_pct, base_position), 4),
            'rationale': rationale,
        }


# =============================================================================
# SECTION 5: BOT RUNNER
# =============================================================================

class BotRunner:
    """
    Main bot runner that generates signals for all tracked assets.
    """

    def __init__(self, tracked_assets=None, run_lppl=False):
        """
        Args:
            tracked_assets: list of symbols to track (default: top crypto + major forex)
            run_lppl: whether to run LPPL fitting (slow, ~30-60s per asset)
        """
        self.data_manager = DataManager()
        self.run_lppl = run_lppl

        if tracked_assets is None:
            # Default: major crypto + forex
            self.tracked_crypto = ['BTC', 'ETH', 'SOL', 'XRP', 'BNB', 'ADA', 'DOGE', 'LTC']
            self.tracked_forex = ['USD_EUR', 'USD_GBP', 'USD_JPY', 'USD_CHF', 'USD_AUD']
        else:
            self.tracked_crypto = [a for a in tracked_assets if not a.startswith('USD_')]
            self.tracked_forex = [a for a in tracked_assets if a.startswith('USD_')]

    def analyze_asset(self, symbol):
        """Run full fractal analysis on a single asset."""
        prices, dates = self.data_manager.get_prices(symbol)
        if prices is None or len(prices) < 50:
            return None

        scores = {}

        # Layer 1: LPPL (optional - slow)
        if self.run_lppl:
            lppl = FractalScorer.score_lppl(prices)
            scores.update(lppl)
        else:
            scores['lppl_score'] = 0.0
            scores['lppl_regime'] = 'skipped'

        # Layer 2: DSI
        dsi = FractalScorer.score_dsi(prices)
        scores.update(dsi)

        # Layer 3: Elliott
        elliott = FractalScorer.score_elliott(prices)
        scores.update(elliott)

        # Layer 4: Kondratiev
        kwave = FractalScorer.score_kondratiev()
        scores.update(kwave)

        # Layer 5: Holographic Phase
        phase = FractalScorer.score_holographic_phase(prices, dates)
        scores.update(phase)

        # Layer 6: Volatility Structure
        vol = FractalScorer.score_volatility_structure(prices)
        scores.update(vol)

        # Aggregate
        signal = SignalAggregator.compute_composite(scores)
        risk = RiskManager.compute_position_sizing(signal)

        return {
            'symbol': symbol,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'latest_price': round(float(prices.iloc[-1]), 6),
            'data_points': len(prices),
            **signal,
            **risk,
            'all_scores': scores,
        }

    def run_scan(self):
        """Run full scan across all tracked assets."""
        log("=" * 70)
        log("TIME FRACTAL BOT - SIGNAL SCAN")
        log(f"Kernel: Z4 x| Z3 -> S1")
        log(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        log(f"LPPL Fitting: {'ENABLED' if self.run_lppl else 'DISABLED (fast mode)'}")
        log("=" * 70)

        all_signals = []

        # Crypto
        log(f"\n--- CRYPTO ASSETS ({len(self.tracked_crypto)}) ---")
        for symbol in self.tracked_crypto:
            if symbol in self.data_manager.crypto_data:
                log(f"\n  Analyzing {symbol}...")
                try:
                    result = self.analyze_asset(symbol)
                    if result:
                        all_signals.append(result)
                        self._print_signal(result)
                except Exception as e:
                    log(f"    ERROR: {e}")

        # Forex
        log(f"\n--- FOREX PAIRS ({len(self.tracked_forex)}) ---")
        for symbol in self.tracked_forex:
            if symbol in self.data_manager.forex_data:
                log(f"\n  Analyzing {symbol}...")
                try:
                    result = self.analyze_asset(symbol)
                    if result:
                        all_signals.append(result)
                        self._print_signal(result)
                except Exception as e:
                    log(f"    ERROR: {e}")

        # Save signals
        if all_signals:
            self._save_signals(all_signals)

        # Print summary
        self._print_summary(all_signals)

        return all_signals

    def _print_signal(self, result):
        """Print a single signal result."""
        signal_markers = {
            'NEXUS_ALERT': '!!!',
            'REGIME_SHIFT': '!! ',
            'PHASE_EDGE': '!  ',
            'QUALITY_READ': '   ',
        }
        marker = signal_markers.get(result['signal_type'], '   ')

        log(f"  {marker} [{result['signal_type']:<14}] "
            f"Composite: {result['composite_score']:.3f} | "
            f"Position: {result['position_pct']*100:.0f}% | "
            f"Stop: {result['stop_atr_multiplier']:.1f}x ATR")

        layers = result.get('layer_scores', {})
        log(f"      Layers: LPPL={layers.get('lppl',0):.2f} "
            f"DSI={layers.get('dsi',0):.2f} "
            f"Phase={layers.get('holographic',0):.2f} "
            f"Vol={layers.get('volatility',0):.2f} "
            f"Elliott={layers.get('elliott',0):.2f} "
            f"K-wave={layers.get('kondratiev',0):.2f}")

        scores = result.get('all_scores', {})
        if scores.get('vol_regime'):
            log(f"      Vol: {scores.get('vol_regime','?')} | "
                f"7d={scores.get('vol_7d',0):.4f} "
                f"30d={scores.get('vol_30d',0):.4f} "
                f"90d={scores.get('vol_90d',0):.4f}")

        if scores.get('dsi_lambdas'):
            log(f"      DSI Lambdas: {scores.get('dsi_lambdas',[])} "
                f"(kernels: {scores.get('dsi_nearest_kernels',[])})")

    def _save_signals(self, signals):
        """Save signals to CSV and JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Flat CSV
        flat_rows = []
        for sig in signals:
            row = {
                'symbol': sig['symbol'],
                'timestamp': sig['timestamp'],
                'latest_price': sig['latest_price'],
                'signal_type': sig['signal_type'],
                'composite_score': sig['composite_score'],
                'macro_bias': sig['macro_bias'],
                'kwave_season': sig['kwave_season'],
                'vol_regime': sig['vol_regime'],
                'position_pct': sig['position_pct'],
                'stop_atr_multiplier': sig['stop_atr_multiplier'],
            }
            # Add layer scores
            for layer, score in sig.get('layer_scores', {}).items():
                row[f'layer_{layer}'] = score
            # Add key details from all_scores
            ascores = sig.get('all_scores', {})
            row['nexus_score'] = ascores.get('nexus_score', 0)
            row['cycle_alignment'] = ascores.get('cycle_alignment', 0)
            row['vol_7d'] = ascores.get('vol_7d', 0)
            row['vol_30d'] = ascores.get('vol_30d', 0)
            row['lppl_lambda'] = ascores.get('lppl_lambda', None)
            row['lppl_r2'] = ascores.get('lppl_r2', 0)
            row['dsi_best_alignment'] = ascores.get('dsi_best_alignment', 0)

            flat_rows.append(row)

        df = pd.DataFrame(flat_rows)

        # Save timestamped version
        df.to_csv(os.path.join(SIGNALS_DIR, f"signals_{timestamp}.csv"), index=False)

        # Save latest (overwrite)
        df.to_csv(os.path.join(SIGNALS_DIR, "LATEST_SIGNALS.csv"), index=False)

        log(f"\n  Signals saved: bot_signals/signals_{timestamp}.csv")
        log(f"  Latest signals: bot_signals/LATEST_SIGNALS.csv")

    def _print_summary(self, signals):
        """Print summary of all signals."""
        log(f"\n{'='*70}")
        log("SIGNAL SUMMARY")
        log(f"{'='*70}")

        if not signals:
            log("  No signals generated.")
            return

        # Group by signal type
        by_type = {}
        for s in signals:
            st = s['signal_type']
            if st not in by_type:
                by_type[st] = []
            by_type[st].append(s)

        for signal_type in ['NEXUS_ALERT', 'REGIME_SHIFT', 'PHASE_EDGE', 'QUALITY_READ']:
            if signal_type in by_type:
                assets = by_type[signal_type]
                symbols = [a['symbol'] for a in assets]
                avg_composite = np.mean([a['composite_score'] for a in assets])
                log(f"\n  {signal_type}: {len(assets)} assets (avg composite: {avg_composite:.3f})")
                for a in assets:
                    log(f"    {a['symbol']:<10} composite={a['composite_score']:.3f} "
                        f"pos={a['position_pct']*100:.0f}% "
                        f"vol={a.get('vol_regime', '?')}")

        # Macro assessment
        if signals:
            avg_composite = np.mean([s['composite_score'] for s in signals])
            nexus_count = sum(1 for s in signals if s['signal_type'] == 'NEXUS_ALERT')
            regime_count = sum(1 for s in signals if s['signal_type'] == 'REGIME_SHIFT')

            log(f"\n  MACRO ASSESSMENT:")
            log(f"    Average Composite: {avg_composite:.3f}")
            log(f"    Kondratiev Phase: Wave 5, Autumn (Water/Maturation)")
            log(f"    Nexus Alerts: {nexus_count} | Regime Shifts: {regime_count}")

            if nexus_count > 2:
                log(f"    >>> ELEVATED MARKET-WIDE TRANSITION RISK <<<")
            elif regime_count > 3:
                log(f"    >>> BROAD REGIME CHANGE UNDERWAY <<<")
            else:
                log(f"    >>> Market in stable regime (normal operations) <<<")

        log(f"\n{'='*70}")
        log("SCAN COMPLETE")
        log(f"{'='*70}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Run the trading bot signal scan."""
    import argparse

    parser = argparse.ArgumentParser(description="Time Fractal Trading Bot")
    parser.add_argument('--lppl', action='store_true',
                       help='Enable LPPL fitting (slow, ~30-60s per asset)')
    parser.add_argument('--assets', nargs='+', default=None,
                       help='Specific assets to analyze')
    args = parser.parse_args()

    bot = BotRunner(tracked_assets=args.assets, run_lppl=args.lppl)
    signals = bot.run_scan()

    return signals


if __name__ == "__main__":
    main()

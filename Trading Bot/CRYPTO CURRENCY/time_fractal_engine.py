"""
THE TIME FRACTAL ENGINE
========================
Implementation of the unified time-fractal algorithm based on:
  Kernel: Z4 ⋊ Z3 -> S1

Integrates:
  - Sornette LPPL (Log-Periodic Power Law) detection
  - Discrete Scale Invariance (DSI) analysis
  - Elliott Wave 5-3 pattern recognition
  - Kondratiev long-wave phase identification
  - McKenna x64 self-similarity scanner
  - Nottale scale-transition detection
  - Holographic octave system (D_n = 36 * 3^(n-1))

Applied to: Crypto + Forex historical data

The Master Equation:
  Psi(t, n) = Sum_k [ A_k * (t_c - t)^(alpha + 2*pi*i*k/ln(lambda)) * Phi_k(sigma, q) ]

Where:
  t = time parameter
  n = octave/resolution level
  k = harmonic index
  alpha = real critical exponent
  lambda = preferred scaling ratio (2, 3, 4, 12, 64)
  sigma = station coordinate (phase quality - READABLE)
  q = fiber coordinate (specific manifestation - FREE)
  Phi_k = eigenfunction of k-th harmonic on metro ring
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution
from scipy.signal import find_peaks, hilbert
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SECTION 1: CORE ALGEBRAIC ENGINE - Z4 ⋊ Z3 -> S1
# =============================================================================

class KernelEngine:
    """
    The algebraic kernel: Z4 semidirect Z3 -> S1

    Z4 = {0,1,2,3} = square carrier (elements: Fire/Air/Water/Earth)
    Z3 = {0,1,2} = triangle carrier (modes: Cardinal/Fixed/Mutable)
    S1 = circle carrier (continuous phase on unit circle)

    The semidirect product action: tau(phi) = phi + tau/3 (mod 1)
    This means triangle SHIFTS phase by 1/3 of a cycle.

    The 12 stations = Z4 x Z3 = the zodiacal metro ring.
    The 64 hexagrammatic states = Z4^3 = cube of elements.
    """

    # Preferred scaling ratios from the kernel
    LAMBDA_BINARY = 2        # chi spin (yin/yang)
    LAMBDA_TRIANGLE = 3      # tau phase (cardinal/fixed/mutable)
    LAMBDA_SQUARE = 4        # element (fire/air/water/earth)
    LAMBDA_ZODIACAL = 12     # full station cycle (4 x 3)
    LAMBDA_HEXAGRAMMATIC = 64  # I Ching level (4^3)

    # Octave ladder: D_n = 36 * 3^(n-1)
    @staticmethod
    def octave_scale(n):
        """Return the n-th octave scale in days."""
        return 36 * (3 ** (n - 1))

    # Tunnel revelation law: L(d,n) = 5 * 3^(d-n)
    @staticmethod
    def tunnel_revelation(d, n):
        """5-cycle orbit length at dimension d, depth n."""
        return 5 * (3 ** (d - n))

    @staticmethod
    def octave_ladder(max_n=10):
        """Generate the full octave ladder."""
        return {n: 36 * (3 ** (n - 1)) for n in range(1, max_n + 1)}

    @staticmethod
    def all_scaling_ratios():
        """All preferred scaling ratios from kernel generators."""
        return [2, 3, 4, 6, 8, 12, 16, 24, 36, 48, 64, 108, 192, 256, 384]

    @staticmethod
    def phase_quality(t, cycle_length):
        """
        Compute the station coordinate sigma for time t within a cycle.
        Returns phase in [0, 1) mapped to 12 stations.

        sigma is READABLE (the quality of time).
        The fiber coordinate q (specific events) is FREE.
        """
        phase = (t % cycle_length) / cycle_length
        station = int(phase * 12) % 12

        # Map to element + mode
        elements = ['Fire', 'Earth', 'Air', 'Water']
        modes = ['Cardinal', 'Fixed', 'Mutable']

        element = elements[station % 4]
        mode = modes[station % 3]

        return {
            'phase': phase,
            'station': station,
            'element': element,
            'mode': mode,
            'quality': f"{mode} {element}",
        }


# =============================================================================
# SECTION 2: SORNETTE LPPL (Log-Periodic Power Law) DETECTOR
# =============================================================================

class LPPLDetector:
    """
    Detects Log-Periodic Power Law signatures in price data.

    The LPPL formula:
      y(t) = A + B*(t_c - t)^m * [1 + C*cos(omega*ln(t_c - t) + phi)]

    Where:
      t_c = critical time (crash/peak date)
      m = power law exponent (0.1 < m < 0.9)
      omega = log-periodic frequency (should relate to lambda)
      phi = phase offset
      A, B, C = amplitude parameters

    The scaling ratio lambda = exp(2*pi/omega)
    This lambda should cluster near kernel scaling ratios (2, 3, 4, etc.)
    """

    @staticmethod
    def lppl_function(t, tc, m, omega, phi, A, B, C):
        """The LPPL function."""
        dt = tc - t
        dt = np.maximum(dt, 1e-10)  # prevent log(0)
        return A + B * np.power(dt, m) * (1 + C * np.cos(omega * np.log(dt) + phi))

    @staticmethod
    def lppl_residuals(params, t, y):
        """Residuals for LPPL fit."""
        tc, m, omega, phi, A, B, C = params
        dt = tc - t
        if np.any(dt <= 0):
            return np.full_like(y, 1e10)
        try:
            y_pred = A + B * np.power(dt, m) * (1 + C * np.cos(omega * np.log(dt) + phi))
            return np.sum((y - y_pred) ** 2)
        except:
            return 1e10

    @staticmethod
    def fit_lppl(prices, dates_numeric, window_frac=0.3):
        """
        Fit LPPL to a price series.

        Returns dict with:
          tc: critical time
          m: exponent
          omega: log-frequency
          lambda_ratio: implied scaling ratio = exp(2*pi/omega)
          quality: fit quality (R^2)
          regime: 'bubble' or 'antibubble'
        """
        t = dates_numeric.astype(float)
        y = np.log(prices.values.astype(float))

        n = len(t)
        t_max = t[-1]
        t_range = t[-1] - t[0]

        # Bounds for parameters
        bounds = [
            (t_max + 1, t_max + t_range * 0.5),  # tc: crash happens after data ends
            (0.1, 0.9),                              # m: critical exponent
            (4, 25),                                  # omega: log frequency
            (0, 2 * np.pi),                           # phi: phase
            (min(y) * 0.5, max(y) * 2),              # A
            (-abs(max(y) - min(y)) * 2, -1e-6),      # B (negative for bubble)
            (-0.5, 0.5),                               # C: amplitude of oscillation
        ]

        best_result = None
        best_cost = np.inf

        # Multiple random starts
        for _ in range(15):
            try:
                result = differential_evolution(
                    LPPLDetector.lppl_residuals,
                    bounds=bounds,
                    args=(t, y),
                    maxiter=200,
                    seed=np.random.randint(0, 10000),
                    tol=1e-8,
                    polish=True,
                )
                if result.fun < best_cost:
                    best_cost = result.fun
                    best_result = result
            except:
                continue

        if best_result is None:
            return None

        tc, m, omega, phi, A, B, C = best_result.x

        # Compute quality metrics
        y_pred = LPPLDetector.lppl_function(t, tc, m, omega, phi, A, B, C)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        # Implied scaling ratio
        lambda_ratio = np.exp(2 * np.pi / omega) if omega > 0 else np.inf

        # Check if lambda is near a kernel scaling ratio
        kernel_ratios = KernelEngine.all_scaling_ratios()
        nearest_kernel = min(kernel_ratios, key=lambda x: abs(lambda_ratio - x))
        kernel_distance = abs(lambda_ratio - nearest_kernel) / nearest_kernel

        return {
            'tc': tc,
            'tc_date_offset': tc - t[-1],  # days until critical point
            'm': m,
            'omega': omega,
            'phi': phi,
            'A': A, 'B': B, 'C': C,
            'lambda_ratio': lambda_ratio,
            'nearest_kernel_lambda': nearest_kernel,
            'kernel_alignment': 1 - min(kernel_distance, 1),  # 1 = perfect alignment
            'r_squared': r_squared,
            'regime': 'bubble' if B < 0 else 'antibubble',
            'cost': best_cost,
        }


# =============================================================================
# SECTION 3: DISCRETE SCALE INVARIANCE (DSI) SCANNER
# =============================================================================

class DSIScanner:
    """
    Scans for Discrete Scale Invariance in time series.

    DSI signature: O(x) ~ x^alpha * P(ln(x) / ln(lambda))
    Where P is periodic.

    Detection method:
    1. Compute power spectrum of log-returns
    2. Look for peaks at frequencies f = k / ln(lambda) for integer k
    3. Check if peaks align with kernel scaling ratios
    """

    @staticmethod
    def detect_log_periodicity(prices, min_lambda=1.5, max_lambda=100):
        """
        Detect log-periodic patterns by computing the Lomb-Scargle periodogram
        of log(price) vs log(time-to-event).

        Returns detected scaling ratios and their significance.
        """
        log_prices = np.log(prices.values.astype(float))
        n = len(log_prices)

        # Compute returns at multiple log-scales
        results = []

        # Test each potential lambda
        test_lambdas = np.logspace(np.log10(min_lambda), np.log10(max_lambda), 200)

        for lam in test_lambdas:
            omega = 2 * np.pi / np.log(lam)

            # Compute correlation with log-periodic oscillation
            t = np.arange(n, dtype=float)
            log_t = np.log(np.maximum(t, 1))

            cos_component = np.cos(omega * log_t)
            sin_component = np.sin(omega * log_t)

            # Detrend log prices
            detrended = log_prices - np.polyval(np.polyfit(t, log_prices, 2), t)

            # Correlation
            corr_cos = np.abs(np.corrcoef(detrended, cos_component)[0, 1])
            corr_sin = np.abs(np.corrcoef(detrended, sin_component)[0, 1])
            power = corr_cos ** 2 + corr_sin ** 2

            results.append({
                'lambda': lam,
                'omega': omega,
                'power': power,
            })

        df = pd.DataFrame(results)

        # Find peaks
        if len(df) < 3:
            return []

        peaks, properties = find_peaks(df['power'].values, height=0.05, distance=5, prominence=0.02)

        detected = []
        kernel_ratios = KernelEngine.all_scaling_ratios()

        for peak_idx in peaks:
            lam = df.iloc[peak_idx]['lambda']
            power = df.iloc[peak_idx]['power']

            # Check alignment with kernel
            nearest_kernel = min(kernel_ratios, key=lambda x: abs(lam - x))
            alignment = 1 - min(abs(lam - nearest_kernel) / nearest_kernel, 1)

            detected.append({
                'lambda': round(lam, 3),
                'power': round(power, 4),
                'nearest_kernel_lambda': nearest_kernel,
                'kernel_alignment': round(alignment, 3),
                'omega': round(df.iloc[peak_idx]['omega'], 4),
            })

        return sorted(detected, key=lambda x: x['power'], reverse=True)

    @staticmethod
    def multi_scale_volatility(prices, scales=None):
        """
        Compute volatility at multiple time scales.
        If DSI is present, volatility should show structure at preferred scales.

        Uses the octave ladder by default.
        """
        if scales is None:
            # Use kernel octave scales + intermediate powers
            scales = [1, 2, 3, 5, 7, 12, 21, 36, 64, 108, 192, 324, 384]

        log_returns = np.log(prices / prices.shift(1)).dropna()

        results = []
        for scale in scales:
            if scale >= len(log_returns):
                continue

            # Realized volatility at this scale
            rolled_vol = log_returns.rolling(scale).std() * np.sqrt(252)

            results.append({
                'scale_days': scale,
                'avg_vol': round(rolled_vol.mean(), 6),
                'max_vol': round(rolled_vol.max(), 6),
                'vol_of_vol': round(rolled_vol.std(), 6),
                'is_octave_scale': scale in [36 * (3 ** n) for n in range(8)],
                'is_kernel_scale': scale in KernelEngine.all_scaling_ratios(),
            })

        return pd.DataFrame(results)


# =============================================================================
# SECTION 4: ELLIOTT WAVE 5-3 PATTERN DETECTOR
# =============================================================================

class ElliottWaveDetector:
    """
    Detects Elliott Wave 5-3 patterns.

    Framework mapping:
      5 impulse waves = the 5-cycle tunnel (L(d,n) = 5 * 3^(d-n))
      3 corrective waves = the triangle governor (Z3)
      5 + 3 = 8 = trigram level (binary level 3)

    Fibonacci ratios emerge from interleaving Z4 and Z3:
      1/phi^2 ≈ 0.382 ≈ sextile step (1/6 * 2.29)
      1/phi ≈ 0.618 ≈ trine step (1/3 * 1.85)
    """

    @staticmethod
    def find_swing_points(prices, order=10):
        """Find local highs and lows (swing points)."""
        highs_idx, _ = find_peaks(prices.values, distance=order)
        lows_idx, _ = find_peaks(-prices.values, distance=order)

        swings = []
        for idx in highs_idx:
            swings.append({'index': idx, 'price': prices.iloc[idx], 'type': 'high'})
        for idx in lows_idx:
            swings.append({'index': idx, 'price': prices.iloc[idx], 'type': 'low'})

        swings.sort(key=lambda x: x['index'])
        return swings

    @staticmethod
    def check_fibonacci_ratios(waves):
        """
        Check if wave ratios approximate Fibonacci relationships.
        Key ratios: 0.382, 0.618, 1.0, 1.618, 2.618
        """
        if len(waves) < 3:
            return []

        fib_ratios = [0.236, 0.382, 0.500, 0.618, 0.786, 1.0, 1.272, 1.618, 2.618]
        results = []

        for i in range(len(waves) - 2):
            wave1 = abs(waves[i+1]['price'] - waves[i]['price'])
            wave2 = abs(waves[i+2]['price'] - waves[i+1]['price'])

            if wave1 == 0:
                continue

            ratio = wave2 / wave1
            nearest_fib = min(fib_ratios, key=lambda x: abs(ratio - x))
            deviation = abs(ratio - nearest_fib) / nearest_fib

            results.append({
                'wave_pair': f"{i+1}-{i+2}",
                'ratio': round(ratio, 4),
                'nearest_fib': nearest_fib,
                'deviation_pct': round(deviation * 100, 2),
                'is_fibonacci': deviation < 0.1,  # within 10%
            })

        return results

    @staticmethod
    def detect_impulse_pattern(prices, min_order=5, max_order=50):
        """
        Look for 5-wave impulse patterns at multiple resolutions.

        Returns quality score and detected patterns.
        """
        results = []

        for order in range(min_order, max_order, 5):
            swings = ElliottWaveDetector.find_swing_points(prices, order=order)

            if len(swings) < 8:  # Need at least 8 swings for 5-3
                continue

            # Look for sequences of 5 up-swings followed by 3 down-swings (or vice versa)
            for start in range(len(swings) - 7):
                segment = swings[start:start + 8]

                # Check alternating pattern
                types = [s['type'] for s in segment]
                prices_seg = [s['price'] for s in segment]

                # 5-wave impulse up: low-high-low-high-low-high-low-high
                # with wave 3 being the longest, wave 5 not exceeding wave 3
                fib_analysis = ElliottWaveDetector.check_fibonacci_ratios(segment)
                fib_count = sum(1 for f in fib_analysis if f['is_fibonacci'])

                if len(fib_analysis) > 0:
                    results.append({
                        'scale': order,
                        'start_idx': segment[0]['index'],
                        'end_idx': segment[-1]['index'],
                        'swing_count': len(segment),
                        'fibonacci_adherence': fib_count / len(fib_analysis),
                        'fib_details': fib_analysis,
                    })

        return results


# =============================================================================
# SECTION 5: KONDRATIEV / LONG WAVE PHASE DETECTOR
# =============================================================================

class KondratievDetector:
    """
    Identifies Kondratiev long-wave phases.

    Framework mapping:
      ~54 year cycle with 4 phases = 4-element cycle (Z4)
      Spring (Fire) -> Summer (Air) -> Autumn (Water) -> Winter (Earth)

    Each phase ~13-14 years.
    Nested cycles: Kuznets (~17yr) = 1/3 of K-wave (Z3 governor)
                   Juglar (~9yr) = 1/2 of Kuznets (Z2 binary)
    """

    # Historical K-wave dating (approximate)
    K_WAVES = [
        {'wave': 1, 'start': 1780, 'peak': 1815, 'trough': 1845},
        {'wave': 2, 'start': 1845, 'peak': 1873, 'trough': 1896},
        {'wave': 3, 'start': 1896, 'peak': 1920, 'trough': 1940},
        {'wave': 4, 'start': 1940, 'peak': 1974, 'trough': 1991},
        {'wave': 5, 'start': 1991, 'peak': 2020, 'trough': 2040},  # estimated
    ]

    @staticmethod
    def current_kwave_phase(year):
        """Determine current Kondratiev wave phase."""
        for kw in KondratievDetector.K_WAVES:
            if kw['start'] <= year <= kw.get('trough', 2100):
                cycle_pos = (year - kw['start']) / (kw.get('trough', kw['start'] + 54) - kw['start'])

                if cycle_pos < 0.25:
                    season = 'Spring'
                    element = 'Fire'
                    quality = 'Expansion/Innovation'
                elif cycle_pos < 0.5:
                    season = 'Summer'
                    element = 'Air'
                    quality = 'Peak/Speculation'
                elif cycle_pos < 0.75:
                    season = 'Autumn'
                    element = 'Water'
                    quality = 'Maturation/Distribution'
                else:
                    season = 'Winter'
                    element = 'Earth'
                    quality = 'Contraction/Reset'

                return {
                    'wave_number': kw['wave'],
                    'cycle_position': round(cycle_pos, 3),
                    'season': season,
                    'element': element,
                    'quality': quality,
                    'phase_angle': round(cycle_pos * 360, 1),
                }

        return {'wave_number': 'unknown', 'season': 'unknown'}

    @staticmethod
    def detect_nested_cycles(prices, dates):
        """
        Detect nested cycle structure using spectral analysis.

        Looks for peaks at:
          - Kondratiev: ~54 years / ~19,700 trading days
          - Kuznets: ~17 years / ~6,200 trading days
          - Juglar: ~9 years / ~3,300 trading days
          - Kitchin: ~3.3 years / ~1,200 trading days
          - Plus kernel octave scales
        """
        log_prices = np.log(prices.values.astype(float))
        detrended = log_prices - np.polyval(np.polyfit(np.arange(len(log_prices)), log_prices, 3), np.arange(len(log_prices)))

        # FFT
        fft_vals = np.fft.rfft(detrended)
        fft_power = np.abs(fft_vals) ** 2
        freqs = np.fft.rfftfreq(len(detrended), d=1)  # daily frequency
        periods = 1.0 / freqs[1:]  # skip DC
        power = fft_power[1:]

        # Find peaks in power spectrum
        if len(power) < 10:
            return []

        peaks_idx, _ = find_peaks(power, distance=5, prominence=np.percentile(power, 75))

        # Named cycles
        named_cycles = {
            'Kitchin': (800, 1500),
            'Juglar': (2500, 4000),
            'Kuznets': (5000, 8000),
            'Kondratiev': (15000, 25000),
        }

        # Kernel octave cycles
        kernel_cycles = {f'Octave_{n}': (KernelEngine.octave_scale(n) * 0.8, KernelEngine.octave_scale(n) * 1.2)
                        for n in range(1, 8) if KernelEngine.octave_scale(n) < len(prices)}

        all_cycles = {**named_cycles, **kernel_cycles}

        detected = []
        for peak_idx in peaks_idx:
            period = periods[peak_idx]
            pwr = power[peak_idx]

            # Check if near any named cycle
            matched_name = None
            for name, (lo, hi) in all_cycles.items():
                if lo <= period <= hi:
                    matched_name = name
                    break

            detected.append({
                'period_days': round(period, 1),
                'period_years': round(period / 365.25, 2),
                'power': round(pwr, 2),
                'matched_cycle': matched_name,
            })

        return sorted(detected, key=lambda x: x['power'], reverse=True)[:20]


# =============================================================================
# SECTION 6: HOLOGRAPHIC PHASE QUALITY COMPUTER
# =============================================================================

class HolographicPhaseComputer:
    """
    Computes the holographic phase quality at any point in time.

    Uses multiple nested cycles simultaneously to determine:
    1. Which octave scales are active
    2. What phase quality (sigma) exists at each scale
    3. Where nexus points (snap thresholds) are approaching
    4. The composite "quality of time" across all active scales

    This is what every functional divination system actually does:
    - Astrology: reads sigma across multiple cycle lengths
    - I Ching: identifies which of 64 states you're in
    - Elliott: identifies wave position in multiple degree counts
    """

    @staticmethod
    def compute_multi_scale_phase(date_numeric, reference_epoch=0):
        """
        Compute phase quality at multiple octave scales simultaneously.

        Returns a "phase fingerprint" - the quality of time at this moment
        across all active octaves.
        """
        t = date_numeric - reference_epoch

        phases = {}
        for n in range(1, 9):
            scale = KernelEngine.octave_scale(n)
            phase_info = KernelEngine.phase_quality(t, scale)
            phases[f'octave_{n}'] = {
                'scale_days': scale,
                'phase': phase_info['phase'],
                'station': phase_info['station'],
                'quality': phase_info['quality'],
            }

        return phases

    @staticmethod
    def compute_nexus_proximity(prices, dates_numeric):
        """
        Detect proximity to nexus points (phase transition thresholds).

        A nexus point is where multiple cycles align - creating a "cheap"
        transition in phase space. The more cycles that align, the stronger
        the nexus.

        This corresponds to Sornette's critical point approach.
        """
        n = len(prices)
        nexus_scores = np.zeros(n)

        octave_scales = [KernelEngine.octave_scale(k) for k in range(1, 8)]
        # Add kernel ratios
        all_scales = octave_scales + [12, 36, 64, 108, 192, 384]
        all_scales = sorted(set([s for s in all_scales if s < n]))

        for scale in all_scales:
            phases = (dates_numeric % scale) / scale

            # Nexus = near 0 or 1 (cycle boundary)
            distance_to_boundary = np.minimum(phases, 1 - phases)

            # Also check quadrant boundaries (0.25, 0.5, 0.75)
            for q in [0.25, 0.5, 0.75]:
                distance_to_boundary = np.minimum(distance_to_boundary, np.abs(phases - q))

            # Score: closer to boundary = higher nexus score
            # Weight by scale importance (larger scales matter more)
            weight = np.log(scale + 1)
            nexus_scores += weight * (1 - distance_to_boundary * 4)  # 4x to sharpen

        # Normalize
        nexus_scores = (nexus_scores - nexus_scores.min()) / (nexus_scores.max() - nexus_scores.min() + 1e-10)

        return nexus_scores

    @staticmethod
    def composite_phase_signal(prices, dates_numeric):
        """
        Compute the composite phase signal combining:
        1. Multi-scale volatility structure
        2. Nexus proximity
        3. LPPL-like oscillation detection
        4. Elliott wave position

        Returns a DataFrame with all signals aligned to dates.
        """
        n = len(prices)
        signals = pd.DataFrame({'date_numeric': dates_numeric})

        # 1. Nexus proximity
        signals['nexus_score'] = HolographicPhaseComputer.compute_nexus_proximity(
            prices, dates_numeric)

        # 2. Multi-scale momentum (phase velocity at each octave)
        for scale in [7, 12, 36, 64, 108, 192, 384]:
            if scale < n:
                returns = prices.pct_change(scale)
                signals[f'momentum_{scale}d'] = returns

        # 3. Volatility regime at multiple scales
        log_returns = np.log(prices / prices.shift(1))
        for scale in [7, 30, 90, 200, 365]:
            if scale < n:
                signals[f'vol_{scale}d'] = log_returns.rolling(scale).std() * np.sqrt(252)

        # 4. Phase quality at key octave scales
        for octave_n in [1, 2, 3, 4]:
            scale = KernelEngine.octave_scale(octave_n)
            if scale < n:
                phases = (dates_numeric % scale) / scale
                signals[f'phase_octave_{octave_n}'] = phases

        # 5. Cycle alignment score (how many cycles are near boundaries simultaneously)
        alignment_scales = [12, 36, 64, 108, 192, 384]
        alignment_scores = np.zeros(n)
        for scale in alignment_scales:
            if scale < n:
                phases = (dates_numeric % scale) / scale
                near_boundary = (np.minimum(phases, 1 - phases) < 0.05).astype(float)
                alignment_scores += near_boundary
        signals['cycle_alignment'] = alignment_scores / len(alignment_scales)

        return signals


# =============================================================================
# SECTION 7: MASTER TRADING SIGNAL GENERATOR
# =============================================================================

class TimeFractalSignalGenerator:
    """
    The master signal generator that combines all time-fractal layers
    into actionable trading signals.

    Signal interpretation:
      sigma (station quality) = READABLE = "what type of market phase are we in?"
      q (fiber/specific) = FREE = "what specific price action happens is not predicted"

    We predict QUALITY (trending/ranging, expanding/contracting, etc.)
    We do NOT predict specific prices or exact timing.

    Oracle uncertainty principle:
      Delta(Structure) * Delta(Timing) >= h_oracle
    """

    @staticmethod
    def generate_signals(prices, dates, symbol='BTC'):
        """
        Generate complete time-fractal trading signals for a price series.

        Returns DataFrame with all signals and composite score.
        """
        # Convert dates to numeric
        if isinstance(dates.iloc[0], str):
            dates_dt = pd.to_datetime(dates)
        else:
            dates_dt = dates

        dates_numeric = (dates_dt - dates_dt.min()).dt.days.values.astype(float)

        results = pd.DataFrame({
            'date': dates,
            'price': prices.values,
        })

        # --- Layer 1: Holographic Phase ---
        phase_signals = HolographicPhaseComputer.composite_phase_signal(
            prices, dates_numeric)
        for col in phase_signals.columns:
            if col != 'date_numeric':
                results[col] = phase_signals[col].values

        # --- Layer 2: DSI Scaling Ratios ---
        # Run on rolling windows
        window = min(500, len(prices) // 2)
        if window > 100:
            dsi_results = DSIScanner.detect_log_periodicity(prices.iloc[-window:])
            if dsi_results:
                results.attrs['dsi_detected_lambdas'] = dsi_results[:5]
                results.attrs['dsi_dominant_lambda'] = dsi_results[0]['lambda']
                results.attrs['dsi_kernel_alignment'] = dsi_results[0]['kernel_alignment']

        # --- Layer 3: Multi-Scale Volatility Structure ---
        vol_structure = DSIScanner.multi_scale_volatility(prices)
        results.attrs['volatility_structure'] = vol_structure

        # --- Layer 4: Kondratiev Phase ---
        current_year = dates_dt.iloc[-1].year if hasattr(dates_dt.iloc[-1], 'year') else 2026
        kwave = KondratievDetector.current_kwave_phase(current_year)
        results.attrs['kondratiev_phase'] = kwave

        # --- Composite Signal ---
        # Combine nexus score + momentum alignment + volatility regime
        if 'nexus_score' in results.columns:
            # High nexus score + expanding volatility = approaching phase transition
            vol_expanding = False
            if 'vol_30d' in results.columns and 'vol_90d' in results.columns:
                vol_expanding = results['vol_30d'].iloc[-1] > results['vol_90d'].iloc[-1]

            # Momentum alignment across scales
            mom_cols = [c for c in results.columns if c.startswith('momentum_')]
            if mom_cols:
                mom_values = results[mom_cols].iloc[-1]
                mom_agreement = (mom_values > 0).sum() / len(mom_values)
                results['momentum_alignment'] = results[mom_cols].apply(
                    lambda row: (row > 0).sum() / len(row), axis=1)

            # Phase transition probability
            results['phase_transition_proximity'] = (
                results['nexus_score'] * 0.4 +
                results.get('cycle_alignment', 0) * 0.3 +
                (results.get('vol_30d', 0) / results.get('vol_90d', 1).replace(0, 1)) * 0.3
            ).clip(0, 1)

        return results


# =============================================================================
# SECTION 8: ANALYSIS RUNNER
# =============================================================================

def analyze_crypto_asset(filepath, symbol):
    """Run full time-fractal analysis on a crypto asset."""
    df = pd.read_csv(filepath)

    if 'close' not in df.columns:
        if 'price_usd' in df.columns:
            df['close'] = df['price_usd']
        else:
            return None

    prices = df['close'].dropna()
    dates = pd.to_datetime(df['date'])

    print(f"\n{'='*60}")
    print(f"TIME FRACTAL ANALYSIS: {symbol}")
    print(f"{'='*60}")
    print(f"Data: {dates.iloc[0].strftime('%Y-%m-%d')} to {dates.iloc[-1].strftime('%Y-%m-%d')}")
    print(f"Points: {len(prices):,}")

    # Generate signals
    signals = TimeFractalSignalGenerator.generate_signals(prices, dates, symbol)

    # Print key findings
    print(f"\n--- Kondratiev Phase ---")
    kwave = signals.attrs.get('kondratiev_phase', {})
    print(f"  Wave: {kwave.get('wave_number', '?')}, Season: {kwave.get('season', '?')}")
    print(f"  Element: {kwave.get('element', '?')}, Quality: {kwave.get('quality', '?')}")

    print(f"\n--- DSI Detection ---")
    dsi = signals.attrs.get('dsi_detected_lambdas', [])
    if dsi:
        for d in dsi[:3]:
            print(f"  Lambda={d['lambda']:.2f} (power={d['power']:.4f}, "
                  f"nearest kernel={d['nearest_kernel_lambda']}, "
                  f"alignment={d['kernel_alignment']:.3f})")
    else:
        print(f"  No significant DSI detected in recent window")

    print(f"\n--- Current Phase Quality ---")
    latest = signals.iloc[-1]
    print(f"  Nexus Score: {latest.get('nexus_score', 0):.3f}")
    print(f"  Cycle Alignment: {latest.get('cycle_alignment', 0):.3f}")
    print(f"  Phase Transition Proximity: {latest.get('phase_transition_proximity', 0):.3f}")

    # Volatility structure
    print(f"\n--- Multi-Scale Volatility ---")
    vol_struct = signals.attrs.get('volatility_structure', None)
    if vol_struct is not None and len(vol_struct) > 0:
        for _, row in vol_struct.iterrows():
            marker = " *OCTAVE*" if row.get('is_octave_scale', False) else ""
            marker += " [KERNEL]" if row.get('is_kernel_scale', False) else ""
            print(f"  {int(row['scale_days']):>4}d: vol={row['avg_vol']:.4f}{marker}")

    return signals


def main():
    """Run analysis on all crypto assets."""
    import os, glob

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    files = sorted(glob.glob(os.path.join(data_dir, "*_full_history.csv")))

    print("=" * 70)
    print("TIME FRACTAL ENGINE v1.0")
    print("Kernel: Z4 semidirect Z3 -> S1")
    print("=" * 70)

    # Analyze top coins
    priority_coins = ['BTC', 'ETH', 'SOL', 'XRP', 'BNB', 'ADA', 'DOGE']

    all_results = {}
    for filepath in files:
        symbol = os.path.basename(filepath).replace('_full_history.csv', '')
        if symbol in priority_coins:
            try:
                signals = analyze_crypto_asset(filepath, symbol)
                if signals is not None:
                    all_results[symbol] = signals

                    # Save signals
                    out_path = os.path.join(data_dir, f"{symbol}_fractal_signals.csv")
                    signals.to_csv(out_path, index=False)
                    print(f"\n  SAVED: {symbol}_fractal_signals.csv")
            except Exception as e:
                print(f"  ERROR for {symbol}: {e}")

    print(f"\n{'='*70}")
    print(f"Analysis complete for {len(all_results)} assets")
    print(f"{'='*70}")

    return all_results


if __name__ == "__main__":
    main()

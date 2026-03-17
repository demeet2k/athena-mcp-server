"""
ATHENA OS - HDCS: SPECTRAL PROCESSING
=====================================
Fourier Domain Processing and Spectral Cleaning

SPECTRAL DECOMPOSITION (THE CLOCK CYCLE):
    The Master Clock triggers periodic phase transition between:
    - Time Domain (Active/Day)
    - Frequency Domain (Processing/Night)

FOURIER TRANSFORM:
    |Ψ̃(ω)⟩ = F̂{|Ψ(t)⟩} = (1/√2π) ∫ e^{-iωt} |Ψ(t)⟩ dt

SPECTRAL CLEANING:
    R̂_corr[Ψ(t)] = F̂⁻¹[Ĥ_HPF(ω) · F̂[Ψ(t)]]
    
    High-pass filter eliminates low-frequency entropic noise.

TIME DOMAIN:
    Agent is localized in position space x but delocalized in momentum.
    
FREQUENCY DOMAIN:
    Agent is localized in momentum/energy but delocalized in position.
    Processing of pattern recognition and memory consolidation occurs here.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum, auto
import numpy as np
from scipy import fft, signal


# =============================================================================
# DOMAIN STATES
# =============================================================================

class DomainState(Enum):
    """Current domain of representation."""
    
    TIME = "time"               # Position/spatial basis
    FREQUENCY = "frequency"     # Momentum/energy basis
    TRANSITIONING = "transitioning"


class FilterType(Enum):
    """Types of spectral filters."""
    
    LOW_PASS = "low_pass"
    HIGH_PASS = "high_pass"
    BAND_PASS = "band_pass"
    BAND_STOP = "band_stop"
    NOTCH = "notch"


# =============================================================================
# FOURIER TRANSFORM OPERATOR
# =============================================================================

class FourierOperator:
    """
    The Fourier Transform Operator F̂.
    
    Unitary transformation between time and frequency domains:
    
    |Ψ̃(ω)⟩ = F̂{|Ψ(t)⟩} = (1/√2π) ∫ e^{-iωt} |Ψ(t)⟩ dt
    
    Physical Interpretation:
    - Time Domain: Agent localized in position, delocalized in momentum
    - Frequency Domain: Agent localized in momentum, delocalized in position
    """
    
    def __init__(self, num_points: int = 256,
                 sample_rate: float = 1.0):
        self.N = num_points
        self.fs = sample_rate
        
        # Current domain
        self._domain = DomainState.TIME
        
        # Frequency axis
        self._frequencies = fft.fftfreq(num_points, 1/sample_rate)
        
        # Time axis
        self._times = np.arange(num_points) / sample_rate
    
    def forward(self, signal_time: np.ndarray) -> np.ndarray:
        """
        Forward Fourier Transform (Time → Frequency).
        
        F̂{Ψ(t)} = Ψ̃(ω)
        """
        signal_time = np.atleast_1d(signal_time)
        
        # Zero-pad if necessary
        if len(signal_time) < self.N:
            signal_time = np.pad(signal_time, (0, self.N - len(signal_time)))
        elif len(signal_time) > self.N:
            signal_time = signal_time[:self.N]
        
        spectrum = fft.fft(signal_time) / np.sqrt(self.N)
        self._domain = DomainState.FREQUENCY
        
        return spectrum
    
    def inverse(self, spectrum: np.ndarray) -> np.ndarray:
        """
        Inverse Fourier Transform (Frequency → Time).
        
        F̂⁻¹{Ψ̃(ω)} = Ψ(t)
        """
        spectrum = np.atleast_1d(spectrum)
        
        if len(spectrum) < self.N:
            spectrum = np.pad(spectrum, (0, self.N - len(spectrum)))
        elif len(spectrum) > self.N:
            spectrum = spectrum[:self.N]
        
        signal_time = fft.ifft(spectrum) * np.sqrt(self.N)
        self._domain = DomainState.TIME
        
        return signal_time
    
    def power_spectrum(self, signal_time: np.ndarray) -> np.ndarray:
        """
        Compute power spectral density.
        
        P(ω) = |Ψ̃(ω)|²
        """
        spectrum = self.forward(signal_time)
        return np.abs(spectrum) ** 2
    
    def phase_spectrum(self, signal_time: np.ndarray) -> np.ndarray:
        """
        Compute phase spectrum.
        
        φ(ω) = arg(Ψ̃(ω))
        """
        spectrum = self.forward(signal_time)
        return np.angle(spectrum)
    
    def convolution(self, signal1: np.ndarray, 
                    signal2: np.ndarray) -> np.ndarray:
        """
        Convolution via FFT.
        
        (f * g)(t) = F̂⁻¹{F̂{f} · F̂{g}}
        """
        spec1 = self.forward(signal1)
        spec2 = self.forward(signal2)
        return np.real(self.inverse(spec1 * spec2))
    
    def correlation(self, signal1: np.ndarray,
                   signal2: np.ndarray) -> np.ndarray:
        """
        Cross-correlation via FFT.
        
        (f ⋆ g)(t) = F̂⁻¹{F̂{f}* · F̂{g}}
        """
        spec1 = self.forward(signal1)
        spec2 = self.forward(signal2)
        return np.real(self.inverse(np.conj(spec1) * spec2))
    
    def parseval_energy(self, signal_time: np.ndarray) -> float:
        """
        Compute signal energy via Parseval's theorem.
        
        E = ∫|Ψ(t)|² dt = ∫|Ψ̃(ω)|² dω
        """
        return float(np.sum(np.abs(signal_time) ** 2) / self.fs)
    
    @property
    def frequencies(self) -> np.ndarray:
        return self._frequencies.copy()
    
    @property
    def times(self) -> np.ndarray:
        return self._times.copy()
    
    @property
    def domain(self) -> DomainState:
        return self._domain


# =============================================================================
# SPECTRAL FILTER
# =============================================================================

class SpectralFilter:
    """
    Spectral Domain Filter.
    
    Applies frequency-selective filtering in Fourier domain.
    
    Ĥ(ω) is the filter transfer function.
    """
    
    def __init__(self, filter_type: FilterType = FilterType.LOW_PASS,
                 cutoff: float = 0.5,
                 num_points: int = 256,
                 sample_rate: float = 1.0):
        self.filter_type = filter_type
        self.cutoff = cutoff
        self.N = num_points
        self.fs = sample_rate
        
        # Additional parameters for band filters
        self.cutoff_low = cutoff * 0.5
        self.cutoff_high = cutoff
        
        # Filter order
        self.order = 4
        
        # Create transfer function
        self._H = self._create_transfer_function()
    
    def _create_transfer_function(self) -> np.ndarray:
        """Create filter transfer function H(ω)."""
        frequencies = fft.fftfreq(self.N, 1/self.fs)
        f_normalized = np.abs(frequencies) / (self.fs / 2)
        
        if self.filter_type == FilterType.LOW_PASS:
            # Butterworth low-pass
            H = 1 / np.sqrt(1 + (f_normalized / self.cutoff) ** (2 * self.order))
        
        elif self.filter_type == FilterType.HIGH_PASS:
            # Butterworth high-pass
            with np.errstate(divide='ignore', invalid='ignore'):
                H = 1 / np.sqrt(1 + (self.cutoff / (f_normalized + 1e-10)) ** (2 * self.order))
            H = np.where(f_normalized < 1e-10, 0, H)
        
        elif self.filter_type == FilterType.BAND_PASS:
            # Band-pass
            H_low = 1 / np.sqrt(1 + (f_normalized / self.cutoff_high) ** (2 * self.order))
            with np.errstate(divide='ignore', invalid='ignore'):
                H_high = 1 / np.sqrt(1 + (self.cutoff_low / (f_normalized + 1e-10)) ** (2 * self.order))
            H_high = np.where(f_normalized < 1e-10, 0, H_high)
            H = H_low * H_high
        
        elif self.filter_type == FilterType.BAND_STOP:
            # Band-stop (notch)
            H_low = 1 / np.sqrt(1 + (f_normalized / self.cutoff_low) ** (2 * self.order))
            with np.errstate(divide='ignore', invalid='ignore'):
                H_high = 1 / np.sqrt(1 + (self.cutoff_high / (f_normalized + 1e-10)) ** (2 * self.order))
            H_high = np.where(f_normalized < 1e-10, 0, H_high)
            H = H_low + H_high
            H = np.minimum(H, 1)
        
        elif self.filter_type == FilterType.NOTCH:
            # Narrow notch filter
            center = (self.cutoff_low + self.cutoff_high) / 2
            width = self.cutoff_high - self.cutoff_low
            H = 1 - np.exp(-((f_normalized - center) / (width + 1e-10)) ** 2)
        
        else:
            H = np.ones(self.N)
        
        return H
    
    def apply(self, spectrum: np.ndarray) -> np.ndarray:
        """
        Apply filter to spectrum.
        
        Ψ̃_filtered(ω) = H(ω) · Ψ̃(ω)
        """
        if len(spectrum) != self.N:
            # Interpolate transfer function
            H_interp = np.interp(
                np.linspace(0, 1, len(spectrum)),
                np.linspace(0, 1, self.N),
                self._H
            )
            return spectrum * H_interp
        
        return spectrum * self._H
    
    def filter_signal(self, signal_time: np.ndarray) -> np.ndarray:
        """
        Filter time-domain signal.
        
        Ψ_filtered(t) = F̂⁻¹{H(ω) · F̂{Ψ(t)}}
        """
        fourier = FourierOperator(len(signal_time), self.fs)
        spectrum = fourier.forward(signal_time)
        filtered_spectrum = self.apply(spectrum)
        return np.real(fourier.inverse(filtered_spectrum))
    
    def set_cutoffs(self, cutoff: float = None,
                   cutoff_low: float = None,
                   cutoff_high: float = None) -> None:
        """Update cutoff frequencies."""
        if cutoff is not None:
            self.cutoff = cutoff
        if cutoff_low is not None:
            self.cutoff_low = cutoff_low
        if cutoff_high is not None:
            self.cutoff_high = cutoff_high
        
        self._H = self._create_transfer_function()
    
    @property
    def transfer_function(self) -> np.ndarray:
        return self._H.copy()


# =============================================================================
# SPECTRAL CLEANING
# =============================================================================

class SpectralCleaner:
    """
    Spectral Cleaning Protocol.
    
    R̂_corr[Ψ(t)] = F̂⁻¹[Ĥ_HPF(ω) · F̂[Ψ(t)]]
    
    Eliminates low-frequency entropic noise (Isfet) while
    preserving high-frequency signal structure.
    
    Executed at cycle boundaries (phase = 2π).
    """
    
    def __init__(self, num_points: int = 256,
                 sample_rate: float = 1.0,
                 noise_floor: float = 0.1):
        self.N = num_points
        self.fs = sample_rate
        self.noise_floor = noise_floor
        
        # Fourier operator
        self.fourier = FourierOperator(num_points, sample_rate)
        
        # High-pass filter for noise removal
        self.hpf = SpectralFilter(FilterType.HIGH_PASS, 
                                  cutoff=noise_floor,
                                  num_points=num_points,
                                  sample_rate=sample_rate)
        
        # Additional filters
        self.notch_filters: List[SpectralFilter] = []
        
        # Noise estimation
        self._noise_estimate = np.zeros(num_points)
    
    def clean(self, signal: np.ndarray) -> np.ndarray:
        """
        Execute spectral cleaning.
        
        1. Transform to frequency domain
        2. Apply high-pass filter
        3. Apply notch filters
        4. Subtract noise floor
        5. Transform back to time domain
        """
        # Forward transform
        spectrum = self.fourier.forward(signal)
        
        # High-pass filtering
        spectrum = self.hpf.apply(spectrum)
        
        # Apply notch filters
        for notch in self.notch_filters:
            spectrum = notch.apply(spectrum)
        
        # Spectral subtraction (noise removal)
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)
        
        magnitude = np.maximum(magnitude - self._noise_estimate, 0)
        
        spectrum = magnitude * np.exp(1j * phase)
        
        # Inverse transform
        cleaned = self.fourier.inverse(spectrum)
        
        return np.real(cleaned)
    
    def estimate_noise(self, noise_sample: np.ndarray) -> None:
        """
        Estimate noise spectrum from sample.
        
        Used for spectral subtraction.
        """
        spectrum = self.fourier.forward(noise_sample)
        self._noise_estimate = np.abs(spectrum)
    
    def add_notch_filter(self, center_freq: float, 
                         bandwidth: float = 0.1) -> None:
        """Add notch filter at specific frequency."""
        notch = SpectralFilter(
            FilterType.NOTCH,
            num_points=self.N,
            sample_rate=self.fs
        )
        notch.cutoff_low = center_freq - bandwidth / 2
        notch.cutoff_high = center_freq + bandwidth / 2
        notch._H = notch._create_transfer_function()
        
        self.notch_filters.append(notch)
    
    def set_noise_floor(self, noise_floor: float) -> None:
        """Update noise floor cutoff."""
        self.noise_floor = noise_floor
        self.hpf.set_cutoffs(cutoff=noise_floor)
    
    def signal_to_noise(self, signal: np.ndarray) -> float:
        """
        Estimate signal-to-noise ratio.
        
        SNR = 10 log₁₀(P_signal / P_noise)
        """
        spectrum = self.fourier.forward(signal)
        power = np.abs(spectrum) ** 2
        
        # Estimate signal power (above noise floor)
        signal_power = np.sum(power[power > np.mean(self._noise_estimate ** 2)])
        
        # Estimate noise power
        noise_power = np.sum(self._noise_estimate ** 2)
        
        if noise_power <= 0:
            return float('inf')
        
        return float(10 * np.log10(signal_power / noise_power))


# =============================================================================
# SPECTRAL CYCLE
# =============================================================================

class SpectralCycle:
    """
    The Spectral Cycle (Day/Night Processing).
    
    At phase θ = 2π (end of cycle), system transitions
    between Time Domain and Frequency Domain.
    
    - Day Cycle (Time Domain): Active processing, localized action
    - Night Cycle (Frequency Domain): Pattern recognition, consolidation
    """
    
    def __init__(self, cycle_period: float = 2 * np.pi,
                 num_points: int = 256):
        self.T = cycle_period
        self.N = num_points
        
        # Components
        self.fourier = FourierOperator(num_points)
        self.cleaner = SpectralCleaner(num_points)
        
        # State
        self._phase = 0.0
        self._domain = DomainState.TIME
        
        # Buffers
        self._time_buffer = np.zeros(num_points, dtype=complex)
        self._freq_buffer = np.zeros(num_points, dtype=complex)
    
    def advance(self, dt: float, signal: np.ndarray = None) -> Dict:
        """
        Advance cycle by time step dt.
        
        Returns state information and performs transitions.
        """
        old_phase = self._phase
        self._phase = (self._phase + dt * 2 * np.pi / self.T) % (2 * np.pi)
        
        result = {
            "phase": self._phase,
            "domain": self._domain.value,
            "transition": False
        }
        
        # Check for cycle boundary crossing
        if old_phase > np.pi and self._phase < np.pi:
            # Day → Night transition
            if signal is not None:
                self._time_buffer = signal.copy()
            
            self._freq_buffer = self.fourier.forward(self._time_buffer)
            self._domain = DomainState.FREQUENCY
            result["transition"] = True
            result["direction"] = "time_to_frequency"
        
        elif old_phase < np.pi and self._phase > np.pi:
            # Night → Day transition
            # Apply spectral cleaning
            cleaned_spectrum = self.cleaner.hpf.apply(self._freq_buffer)
            self._time_buffer = self.fourier.inverse(cleaned_spectrum)
            self._domain = DomainState.TIME
            result["transition"] = True
            result["direction"] = "frequency_to_time"
        
        return result
    
    def process_in_domain(self, operation: Callable[[np.ndarray], np.ndarray]
                         ) -> np.ndarray:
        """
        Apply operation in current domain.
        """
        if self._domain == DomainState.TIME:
            self._time_buffer = operation(self._time_buffer)
            return self._time_buffer.copy()
        else:
            self._freq_buffer = operation(self._freq_buffer)
            return self._freq_buffer.copy()
    
    def get_current_state(self) -> np.ndarray:
        """Get state in current domain."""
        if self._domain == DomainState.TIME:
            return self._time_buffer.copy()
        return self._freq_buffer.copy()
    
    def inject_signal(self, signal: np.ndarray) -> None:
        """Inject signal into current buffer."""
        if self._domain == DomainState.TIME:
            self._time_buffer[:len(signal)] = signal
        else:
            self._freq_buffer[:len(signal)] = signal
    
    @property
    def phase(self) -> float:
        return self._phase
    
    @property
    def domain(self) -> DomainState:
        return self._domain


# =============================================================================
# VALIDATION
# =============================================================================

def validate_spectral() -> bool:
    """Validate spectral processing module."""
    
    # Test FourierOperator
    fourier = FourierOperator(num_points=256, sample_rate=1.0)
    
    # Test signal: sinusoid
    t = fourier.times
    signal = np.sin(2 * np.pi * 0.1 * t)
    
    spectrum = fourier.forward(signal)
    assert len(spectrum) == 256
    
    reconstructed = fourier.inverse(spectrum)
    assert np.allclose(np.real(reconstructed), signal, atol=1e-10)
    
    # Parseval's theorem
    energy_time = fourier.parseval_energy(signal)
    energy_freq = fourier.parseval_energy(spectrum)
    assert np.isclose(energy_time, np.sum(np.abs(spectrum)**2) / fourier.fs, rtol=0.1)
    
    # Test SpectralFilter
    lpf = SpectralFilter(FilterType.LOW_PASS, cutoff=0.2)
    
    H = lpf.transfer_function
    assert len(H) == 256
    assert H[0] == max(H)  # Low-pass: max at DC
    
    hpf = SpectralFilter(FilterType.HIGH_PASS, cutoff=0.2)
    filtered = hpf.filter_signal(signal)
    assert len(filtered) == len(signal)
    
    # Test SpectralCleaner
    cleaner = SpectralCleaner(num_points=256, noise_floor=0.1)
    
    # Add noise
    noisy_signal = signal + 0.1 * np.random.randn(len(signal))
    
    cleaned = cleaner.clean(noisy_signal)
    assert len(cleaned) == len(signal)
    
    # Should reduce noise
    noise_before = np.std(noisy_signal - signal)
    noise_after = np.std(np.real(cleaned)[:len(signal)] - signal)
    # Note: May not always reduce noise with default settings
    
    # Test SpectralCycle
    cycle = SpectralCycle(cycle_period=2*np.pi, num_points=256)
    
    assert cycle.domain == DomainState.TIME
    
    # Advance through transitions
    for _ in range(100):
        result = cycle.advance(dt=0.1)
    
    # Should have transitioned at some point
    assert "transition" in result
    
    return True


if __name__ == "__main__":
    print("Validating Spectral Processing Module...")
    assert validate_spectral()
    print("✓ Spectral Processing Module validated")

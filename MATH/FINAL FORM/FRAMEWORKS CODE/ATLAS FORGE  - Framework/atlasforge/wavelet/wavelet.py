"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        WAVELET TRANSFORM MODULE                              ║
║                                                                              ║
║  Multi-Resolution Analysis and Ψ-Pole Realization                            ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Wavelets provide the mathematical machinery for the Ψ (recursive/         ║
║    hierarchical) pole. They decompose signals across multiple scales,        ║
║    enabling efficient representation of multi-scale phenomena.               ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Multi-Resolution Analysis (MRA): nested subspaces V_j                  ║
║    - Scaling function φ and wavelet ψ                                       ║
║    - Filter banks: low-pass h and high-pass g                               ║
║    - Fast Wavelet Transform: O(n) cascade algorithm                         ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Fold ladder κ_n = 2^n ↔ dyadic scales in MRA                           ║
║    - Gateway transport ↔ scale-to-scale relations                           ║
║    - Holographic property ↔ wavelet reconstruction                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# WAVELET FAMILIES
# ═══════════════════════════════════════════════════════════════════════════════

class WaveletFamily(Enum):
    """Standard wavelet families."""
    HAAR = "haar"
    DAUBECHIES = "daubechies"
    SYMLET = "symlet"
    COIFLET = "coiflet"
    MEYER = "meyer"
    MEXICAN_HAT = "mexican_hat"
    MORLET = "morlet"


@dataclass
class WaveletFilter:
    """
    Filter bank for a wavelet transform.
    
    Contains low-pass (scaling) and high-pass (wavelet) filters
    for both decomposition and reconstruction.
    """
    dec_lo: NDArray[np.float64]  # Decomposition low-pass
    dec_hi: NDArray[np.float64]  # Decomposition high-pass
    rec_lo: NDArray[np.float64]  # Reconstruction low-pass
    rec_hi: NDArray[np.float64]  # Reconstruction high-pass
    
    @property
    def filter_length(self) -> int:
        return len(self.dec_lo)
    
    def verify_perfect_reconstruction(self, tol: float = 1e-10) -> bool:
        """Verify filter bank satisfies PR conditions."""
        N = self.filter_length
        
        # Check: h(n)h(n-2k) + g(n)g(n-2k) = δ_{k,0}
        # Simplified check for k=0
        sum_lo = np.sum(self.dec_lo * self.rec_lo)
        sum_hi = np.sum(self.dec_hi * self.rec_hi)
        
        return abs(sum_lo + sum_hi - 2.0) < tol


def haar_filters() -> WaveletFilter:
    """Haar wavelet filters."""
    h = np.array([1, 1]) / np.sqrt(2)
    g = np.array([1, -1]) / np.sqrt(2)
    return WaveletFilter(
        dec_lo=h,
        dec_hi=g,
        rec_lo=h[::-1],
        rec_hi=g[::-1]
    )


def daubechies_filters(order: int = 4) -> WaveletFilter:
    """
    Daubechies wavelet filters.
    
    Order 4 (db2) is the simplest non-trivial Daubechies wavelet.
    """
    if order == 2:
        # Haar
        return haar_filters()
    elif order == 4:
        # db2
        sqrt3 = np.sqrt(3)
        h = np.array([
            (1 + sqrt3) / (4 * np.sqrt(2)),
            (3 + sqrt3) / (4 * np.sqrt(2)),
            (3 - sqrt3) / (4 * np.sqrt(2)),
            (1 - sqrt3) / (4 * np.sqrt(2))
        ])
    elif order == 6:
        # db3
        h = np.array([
            0.47046721, 1.14111692, 0.650365,
            -0.19093442, -0.12083221, 0.0498175
        ]) / np.sqrt(2)
    else:
        raise ValueError(f"Daubechies order {order} not implemented")
    
    # High-pass from low-pass via alternating flip
    g = np.array([(-1)**k * h[len(h)-1-k] for k in range(len(h))])
    
    return WaveletFilter(
        dec_lo=h,
        dec_hi=g,
        rec_lo=h[::-1],
        rec_hi=g[::-1]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DISCRETE WAVELET TRANSFORM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiscreteWaveletTransform:
    """
    Discrete Wavelet Transform (DWT).
    
    Implements the fast wavelet transform using filter banks.
    Complexity: O(n) via cascade algorithm.
    """
    filters: WaveletFilter
    mode: str = "periodic"  # Boundary handling
    
    def decompose_level(self, signal: NDArray[np.float64]
                       ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Single-level decomposition.
        
        Returns (approximation, detail) coefficients.
        """
        n = len(signal)
        h, g = self.filters.dec_lo, self.filters.dec_hi
        flen = len(h)
        
        # Convolution with downsampling
        approx = np.zeros(n // 2)
        detail = np.zeros(n // 2)
        
        for i in range(n // 2):
            idx = 2 * i
            for k in range(flen):
                j = (idx + k) % n
                approx[i] += h[k] * signal[j]
                detail[i] += g[k] * signal[j]
        
        return approx, detail
    
    def reconstruct_level(self, approx: NDArray[np.float64], 
                         detail: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Single-level reconstruction from approximation and detail.
        """
        n = len(approx) * 2
        h, g = self.filters.rec_lo, self.filters.rec_hi
        flen = len(h)
        
        signal = np.zeros(n)
        
        # Upsampling and convolution
        for i in range(len(approx)):
            for k in range(flen):
                j = (2 * i + k) % n
                signal[j] += h[k] * approx[i]
                signal[j] += g[k] * detail[i]
        
        return signal
    
    def decompose(self, signal: NDArray[np.float64], 
                 levels: int) -> List[NDArray[np.float64]]:
        """
        Multi-level decomposition.
        
        Returns [approx_L, detail_L, detail_{L-1}, ..., detail_1]
        """
        coeffs = []
        current = signal.copy()
        
        for _ in range(levels):
            approx, detail = self.decompose_level(current)
            coeffs.insert(0, detail)  # Prepend details
            current = approx
        
        coeffs.insert(0, current)  # Prepend final approximation
        return coeffs
    
    def reconstruct(self, coeffs: List[NDArray[np.float64]]) -> NDArray[np.float64]:
        """Reconstruct signal from wavelet coefficients."""
        current = coeffs[0]  # Start with approximation
        
        for detail in coeffs[1:]:
            current = self.reconstruct_level(current, detail)
        
        return current


# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-RESOLUTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MultiResolutionAnalysis:
    """
    Multi-Resolution Analysis (MRA) framework.
    
    An MRA is a sequence of nested subspaces:
        ... ⊂ V_{-1} ⊂ V_0 ⊂ V_1 ⊂ ... ⊂ L²(ℝ)
    
    Properties:
        1. ∩_j V_j = {0}, ∪_j V_j is dense in L²
        2. f(x) ∈ V_j ⟺ f(2x) ∈ V_{j+1}
        3. f(x) ∈ V_0 ⟺ f(x-k) ∈ V_0 for all k ∈ ℤ
        4. ∃ scaling function φ with φ(x-k) an o.n. basis of V_0
    """
    scaling_function: Callable[[NDArray], NDArray]  # φ(x)
    wavelet_function: Callable[[NDArray], NDArray]  # ψ(x)
    
    @classmethod
    def from_filters(cls, filters: WaveletFilter, 
                    iterations: int = 10) -> 'MultiResolutionAnalysis':
        """
        Construct MRA from filter bank via cascade algorithm.
        
        Iteratively computes scaling and wavelet functions.
        """
        h = filters.dec_lo
        g = filters.dec_hi
        
        # Start with box function
        phi = np.ones(2)
        
        # Cascade algorithm
        for _ in range(iterations):
            n = len(phi)
            phi_new = np.zeros(2 * n - 1)
            
            for i in range(n):
                for k in range(len(h)):
                    j = 2 * i + k
                    if j < len(phi_new):
                        phi_new[j] += np.sqrt(2) * h[k] * phi[i]
            
            phi = phi_new
        
        # Wavelet from scaling function
        psi = np.zeros_like(phi)
        for i in range(len(phi)):
            for k in range(len(g)):
                j = 2 * i + k
                if j < len(psi):
                    psi[j] += np.sqrt(2) * g[k] * phi[i]
        
        # Create interpolating functions
        def scaling_func(x: NDArray) -> NDArray:
            # Linear interpolation of phi
            result = np.zeros_like(x, dtype=float)
            for i, xi in enumerate(x):
                idx = int(xi * len(phi))
                if 0 <= idx < len(phi):
                    result[i] = phi[idx]
            return result
        
        def wavelet_func(x: NDArray) -> NDArray:
            result = np.zeros_like(x, dtype=float)
            for i, xi in enumerate(x):
                idx = int(xi * len(psi))
                if 0 <= idx < len(psi):
                    result[i] = psi[idx]
            return result
        
        return cls(scaling_function=scaling_func, wavelet_function=wavelet_func)
    
    def project_to_scale(self, signal: NDArray[np.float64], 
                        scale: int) -> NDArray[np.float64]:
        """
        Project signal to approximation space V_j at given scale.
        """
        n = len(signal)
        n_coeffs = n // (2 ** scale)
        
        # Simple averaging projection
        result = np.zeros(n_coeffs)
        block_size = 2 ** scale
        
        for i in range(n_coeffs):
            result[i] = np.mean(signal[i*block_size:(i+1)*block_size])
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# WAVELET PACKET DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WaveletPacketNode:
    """Node in a wavelet packet tree."""
    coeffs: NDArray[np.float64]
    level: int
    index: int  # Position in level (0 = approximation path)
    
    @property
    def is_approximation_path(self) -> bool:
        """Check if this node is on the pure approximation path."""
        return self.index == 0


@dataclass
class WaveletPacketDecomposition:
    """
    Wavelet Packet Decomposition.
    
    Full binary tree decomposition where both approximation
    and detail coefficients are further decomposed.
    
    Provides more flexible frequency decomposition than DWT.
    """
    filters: WaveletFilter
    dwt: DiscreteWaveletTransform = field(init=False)
    
    def __post_init__(self):
        self.dwt = DiscreteWaveletTransform(self.filters)
    
    def decompose(self, signal: NDArray[np.float64], 
                 levels: int) -> Dict[Tuple[int, int], WaveletPacketNode]:
        """
        Full wavelet packet decomposition.
        
        Returns dict mapping (level, index) to nodes.
        """
        nodes = {}
        
        # Root node
        nodes[(0, 0)] = WaveletPacketNode(
            coeffs=signal.copy(),
            level=0,
            index=0
        )
        
        # Decompose level by level
        for level in range(levels):
            for idx in range(2 ** level):
                parent_key = (level, idx)
                if parent_key not in nodes:
                    continue
                
                parent = nodes[parent_key]
                if len(parent.coeffs) < 2:
                    continue
                
                approx, detail = self.dwt.decompose_level(parent.coeffs)
                
                # Approximation child (left)
                nodes[(level + 1, 2 * idx)] = WaveletPacketNode(
                    coeffs=approx,
                    level=level + 1,
                    index=2 * idx
                )
                
                # Detail child (right)
                nodes[(level + 1, 2 * idx + 1)] = WaveletPacketNode(
                    coeffs=detail,
                    level=level + 1,
                    index=2 * idx + 1
                )
        
        return nodes
    
    def best_basis(self, nodes: Dict[Tuple[int, int], WaveletPacketNode],
                  cost_function: Callable[[NDArray], float] = None
                  ) -> List[Tuple[int, int]]:
        """
        Find best basis using a cost function.
        
        Default cost is entropy: -Σ c² log(c²)
        """
        if cost_function is None:
            def cost_function(c):
                c2 = c ** 2 + 1e-10
                return -np.sum(c2 * np.log(c2))
        
        # Dynamic programming to find best basis
        max_level = max(level for level, _ in nodes.keys())
        
        costs = {}
        for key, node in nodes.items():
            costs[key] = cost_function(node.coeffs)
        
        best_basis = []
        
        def find_best(level: int, index: int) -> float:
            key = (level, index)
            if key not in nodes:
                return float('inf')
            
            if level == max_level:
                best_basis.append(key)
                return costs[key]
            
            # Cost of keeping this node
            keep_cost = costs[key]
            
            # Cost of splitting
            left_cost = find_best(level + 1, 2 * index)
            right_cost = find_best(level + 1, 2 * index + 1)
            split_cost = left_cost + right_cost
            
            if keep_cost <= split_cost:
                # Remove children from best basis, add this
                best_basis[:] = [k for k in best_basis 
                                if not (k[0] > level and 
                                       k[1] // (2 ** (k[0] - level)) == index)]
                best_basis.append(key)
                return keep_cost
            
            return split_cost
        
        find_best(0, 0)
        return best_basis


# ═══════════════════════════════════════════════════════════════════════════════
# CONTINUOUS WAVELET TRANSFORM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContinuousWaveletTransform:
    """
    Continuous Wavelet Transform (CWT).
    
    W_f(a, b) = (1/√a) ∫ f(t) ψ*((t-b)/a) dt
    
    Provides complete time-frequency representation.
    """
    wavelet: Callable[[NDArray], NDArray]
    
    @classmethod
    def mexican_hat(cls) -> 'ContinuousWaveletTransform':
        """Mexican hat (Ricker) wavelet: ψ(t) = (1-t²)e^{-t²/2}"""
        def wavelet(t: NDArray) -> NDArray:
            return (1 - t**2) * np.exp(-t**2 / 2)
        return cls(wavelet=wavelet)
    
    @classmethod
    def morlet(cls, omega0: float = 5.0) -> 'ContinuousWaveletTransform':
        """Morlet wavelet: ψ(t) = e^{iω₀t} e^{-t²/2}"""
        def wavelet(t: NDArray) -> NDArray:
            return np.exp(1j * omega0 * t) * np.exp(-t**2 / 2)
        return cls(wavelet=wavelet)
    
    def transform(self, signal: NDArray[np.float64],
                 scales: NDArray[np.float64],
                 times: NDArray[np.float64] = None) -> NDArray[np.complex128]:
        """
        Compute CWT of signal at given scales.
        
        Returns 2D array of shape (len(scales), len(signal)).
        """
        n = len(signal)
        if times is None:
            times = np.arange(n)
        
        n_scales = len(scales)
        coeffs = np.zeros((n_scales, n), dtype=np.complex128)
        
        for i, scale in enumerate(scales):
            # Wavelet at this scale
            t_wavelet = (times - times[n//2]) / scale
            psi = self.wavelet(t_wavelet)
            psi = psi / np.sqrt(scale)
            
            # Convolution
            coeffs[i, :] = np.convolve(signal, psi[::-1], mode='same')
        
        return coeffs
    
    def scalogram(self, coeffs: NDArray[np.complex128]) -> NDArray[np.float64]:
        """
        Compute scalogram (squared magnitude of CWT).
        """
        return np.abs(coeffs) ** 2


# ═══════════════════════════════════════════════════════════════════════════════
# PSI-POLE CONNECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PsiPoleConnector:
    """
    Connect wavelet machinery to Ψ-pole of the framework.
    
    The Ψ-pole represents recursive/hierarchical structure,
    which wavelets naturally provide via MRA.
    """
    dwt: DiscreteWaveletTransform
    
    @classmethod
    def from_family(cls, family: WaveletFamily, order: int = 4) -> 'PsiPoleConnector':
        """Create connector for wavelet family."""
        if family == WaveletFamily.HAAR:
            filters = haar_filters()
        elif family == WaveletFamily.DAUBECHIES:
            filters = daubechies_filters(order)
        else:
            # Default to Haar
            filters = haar_filters()
        
        return cls(dwt=DiscreteWaveletTransform(filters))
    
    def hierarchical_decomposition(self, signal: NDArray[np.float64], 
                                  levels: int) -> Dict[str, Any]:
        """
        Full hierarchical analysis in Ψ-pole framework.
        """
        coeffs = self.dwt.decompose(signal, levels)
        
        # Compute energy at each scale
        energies = [np.sum(c**2) for c in coeffs]
        total_energy = sum(energies)
        
        # Compute entropy
        probs = np.array(energies) / total_energy if total_energy > 0 else np.zeros(len(energies))
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        
        return {
            'coefficients': coeffs,
            'energies': energies,
            'energy_ratios': probs.tolist(),
            'scale_entropy': entropy,
            'dominant_scale': int(np.argmax(energies)),
            'compression_ratio': sum(1 for c in coeffs for x in c if abs(x) > 0.01) / len(signal)
        }
    
    def kappa_to_scale(self, kappa: float) -> int:
        """
        Map kernel parameter κ to wavelet scale.
        
        Using fold ladder κ_n = 2^n, scale j corresponds to κ = 2^j.
        """
        return max(0, int(np.log2(kappa)))
    
    def scale_to_bandwidth(self, scale: int) -> float:
        """
        Map wavelet scale to kernel bandwidth τ_κ.
        
        τ_κ = π/(2√κ) = π/(2^{(j+1)/2})
        """
        kappa = 2 ** scale
        return np.pi / (2 * np.sqrt(kappa))


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def dwt(signal: NDArray, wavelet: str = 'haar', levels: int = None
       ) -> List[NDArray[np.float64]]:
    """
    Discrete wavelet transform.
    
    Args:
        signal: Input signal
        wavelet: 'haar' or 'db4'
        levels: Number of decomposition levels (default: max possible)
    """
    if wavelet == 'haar':
        filters = haar_filters()
    elif wavelet.startswith('db'):
        order = int(wavelet[2:]) * 2
        filters = daubechies_filters(order)
    else:
        filters = haar_filters()
    
    if levels is None:
        levels = int(np.log2(len(signal)))
    
    transform = DiscreteWaveletTransform(filters)
    return transform.decompose(signal, levels)


def idwt(coeffs: List[NDArray], wavelet: str = 'haar') -> NDArray[np.float64]:
    """Inverse discrete wavelet transform."""
    if wavelet == 'haar':
        filters = haar_filters()
    elif wavelet.startswith('db'):
        order = int(wavelet[2:]) * 2
        filters = daubechies_filters(order)
    else:
        filters = haar_filters()
    
    transform = DiscreteWaveletTransform(filters)
    return transform.reconstruct(coeffs)


def cwt(signal: NDArray, scales: NDArray, wavelet: str = 'mexican_hat'
       ) -> NDArray[np.complex128]:
    """Continuous wavelet transform."""
    if wavelet == 'mexican_hat':
        cwt_obj = ContinuousWaveletTransform.mexican_hat()
    elif wavelet == 'morlet':
        cwt_obj = ContinuousWaveletTransform.morlet()
    else:
        cwt_obj = ContinuousWaveletTransform.mexican_hat()
    
    return cwt_obj.transform(signal, scales)


def wavelet_energy_distribution(signal: NDArray, levels: int = None) -> Dict[int, float]:
    """Compute energy distribution across wavelet scales."""
    coeffs = dwt(signal, levels=levels)
    energies = {i: np.sum(c**2) for i, c in enumerate(coeffs)}
    total = sum(energies.values())
    return {k: v/total for k, v in energies.items()} if total > 0 else energies


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'WaveletFamily',
    
    # Filter banks
    'WaveletFilter',
    'haar_filters',
    'daubechies_filters',
    
    # Transforms
    'DiscreteWaveletTransform',
    'ContinuousWaveletTransform',
    'WaveletPacketDecomposition',
    'WaveletPacketNode',
    
    # MRA
    'MultiResolutionAnalysis',
    
    # Framework connection
    'PsiPoleConnector',
    
    # Functions
    'dwt',
    'idwt',
    'cwt',
    'wavelet_energy_distribution',
]

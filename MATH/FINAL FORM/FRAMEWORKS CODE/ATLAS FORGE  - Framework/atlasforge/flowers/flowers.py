"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - FLOWERS Module (Wave-Side Modes)             ║
╚══════════════════════════════════════════════════════════════════════════════╝

FLOWERS = Standing wave modes that form the continuous counterpart to the
discrete 4×4 Holographic Seed.

Seed ↔ Flower Duality:
- Seed: Finite, discrete phase engine on Z₂²
- Flower: Continuous standing wave with nodal structure

Key Concepts:
- Petals: Connected nodal domains of constant sign
- Nodal lines: Zero sets of eigenfunctions
- Spectral eigenvalues: Control petal count and frequency

Examples:
- Rose curves: r = cos(kθ), k petals
- Spherical harmonics: Y_l^m on S²
- Laplacian eigenfunctions on domains

Flower → Seed Encoding:
1. Sample continuous mode on discrete grid
2. Quantize to 4-phase alphabet (Earth/Water/Air/Fire)
3. Map 2×2 windows to seed patterns
4. Measure holographic diversity

Seed → Flower Lifting:
1. Tile domain with seed patterns  
2. Interpolate to continuous field
3. Apply spectral smoothing
4. Extract dominant mode structure
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


@dataclass
class NodalPattern:
    """
    Nodal pattern of a wave mode.
    
    Captures the structure of nodal lines (zeros) and petals (domains).
    """
    n_petals: int
    symmetry_order: int          # Rotational symmetry
    nodal_count: int             # Number of nodal curves
    is_radial: bool              # Has radial structure
    eigenvalue: float            # Associated eigenvalue
    
    @property
    def angular_momentum(self) -> int:
        """Angular quantum number (if applicable)."""
        return self.symmetry_order
    
    def describe(self) -> str:
        return (f"NodalPattern: {self.n_petals} petals, "
                f"{self.symmetry_order}-fold symmetry, "
                f"λ = {self.eigenvalue:.4f}")


class FlowerMode(ABC):
    """Abstract base class for standing wave modes (flowers)."""
    
    @abstractmethod
    def evaluate(self, x: NDArray) -> NDArray:
        """Evaluate the mode at points x."""
        pass
    
    @abstractmethod
    def nodal_pattern(self) -> NodalPattern:
        """Return the nodal pattern of this mode."""
        pass
    
    def sample_on_grid(self, n: int) -> NDArray:
        """Sample mode on n×n grid."""
        pass


class RoseCurve(FlowerMode):
    """
    Rose curve flower: r = A cos(kθ + φ)
    
    Properties:
    - k petals if k is odd
    - 2k petals if k is even
    - Dihedral symmetry D_k
    """
    
    def __init__(
        self,
        k: int = 4,
        amplitude: float = 1.0,
        phase: float = 0.0,
    ):
        self.k = k
        self.amplitude = amplitude
        self.phase = phase
    
    def evaluate(self, theta: NDArray) -> NDArray:
        """Evaluate r(θ) = A cos(kθ + φ)."""
        return self.amplitude * np.cos(self.k * theta + self.phase)
    
    def evaluate_cartesian(self, x: NDArray, y: NDArray) -> NDArray:
        """Evaluate in Cartesian coordinates."""
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        rose_r = self.evaluate(theta)
        # Return signed distance-like field
        return rose_r - r
    
    def nodal_pattern(self) -> NodalPattern:
        n_petals = self.k if self.k % 2 == 1 else 2 * self.k
        return NodalPattern(
            n_petals=n_petals,
            symmetry_order=self.k,
            nodal_count=self.k,  # k nodal rays
            is_radial=True,
            eigenvalue=float(self.k**2),
        )
    
    def sample_on_grid(self, n: int) -> NDArray:
        """Sample on 2D Cartesian grid."""
        x = np.linspace(-1.5, 1.5, n)
        y = np.linspace(-1.5, 1.5, n)
        X, Y = np.meshgrid(x, y)
        return self.evaluate_cartesian(X, Y)


class SphericalHarmonic(FlowerMode):
    """
    Spherical harmonic Y_l^m on the unit sphere.
    
    Eigenfunction of Laplacian on S² with eigenvalue l(l+1).
    """
    
    def __init__(self, l: int, m: int):
        assert abs(m) <= l, f"|m| must be ≤ l, got l={l}, m={m}"
        self.l = l
        self.m = m
    
    def evaluate(self, theta: NDArray, phi: NDArray) -> NDArray:
        """
        Evaluate Y_l^m(θ, φ).
        
        Uses simplified form for common cases.
        """
        # Simplified real spherical harmonics
        from scipy.special import sph_harm
        return np.real(sph_harm(self.m, self.l, phi, theta))
    
    def nodal_pattern(self) -> NodalPattern:
        # l - |m| latitude circles + |m| longitude circles
        return NodalPattern(
            n_petals=(2 * self.l + 1) * (self.l - abs(self.m) + 1) // 2,
            symmetry_order=abs(self.m) if self.m != 0 else self.l,
            nodal_count=self.l,
            is_radial=False,
            eigenvalue=float(self.l * (self.l + 1)),
        )
    
    def sample_on_grid(self, n: int) -> NDArray:
        """Sample on spherical grid."""
        theta = np.linspace(0, np.pi, n)
        phi = np.linspace(0, 2*np.pi, n)
        THETA, PHI = np.meshgrid(theta, phi)
        return self.evaluate(THETA, PHI)


class LaplacianEigenfunction(FlowerMode):
    """
    Eigenfunction of Laplacian on rectangular domain.
    
    ψ_{n,m}(x,y) = sin(nπx/L_x) sin(mπy/L_y)
    λ_{n,m} = π²(n²/L_x² + m²/L_y²)
    """
    
    def __init__(
        self,
        nx: int,
        ny: int,
        Lx: float = 1.0,
        Ly: float = 1.0,
    ):
        self.nx = nx
        self.ny = ny
        self.Lx = Lx
        self.Ly = Ly
    
    def evaluate(self, x: NDArray, y: NDArray) -> NDArray:
        """Evaluate eigenfunction at (x, y)."""
        return (np.sin(self.nx * np.pi * x / self.Lx) * 
                np.sin(self.ny * np.pi * y / self.Ly))
    
    @property
    def eigenvalue(self) -> float:
        return np.pi**2 * (self.nx**2 / self.Lx**2 + self.ny**2 / self.Ly**2)
    
    def nodal_pattern(self) -> NodalPattern:
        # (nx-1) vertical + (ny-1) horizontal nodal lines
        return NodalPattern(
            n_petals=self.nx * self.ny,
            symmetry_order=min(self.nx, self.ny),
            nodal_count=self.nx + self.ny - 2,
            is_radial=False,
            eigenvalue=self.eigenvalue,
        )
    
    def sample_on_grid(self, n: int) -> NDArray:
        """Sample on n×n grid."""
        x = np.linspace(0, self.Lx, n)
        y = np.linspace(0, self.Ly, n)
        X, Y = np.meshgrid(x, y)
        return self.evaluate(X, Y)


@dataclass
class FlowerSampling:
    """
    Discrete sampling of a continuous flower mode.
    """
    values: NDArray[np.float64]     # Sampled values
    signs: NDArray[np.int32]        # Sign pattern (-1, 0, +1)
    phases: NDArray[np.int32]       # 4-phase quantization
    coordinates: NDArray[np.float64] # Sample coordinates
    
    @property
    def shape(self) -> Tuple[int, ...]:
        return self.values.shape
    
    def nodal_mask(self, threshold: float = 0.1) -> NDArray[np.bool_]:
        """Return mask of near-nodal points."""
        max_val = np.max(np.abs(self.values))
        if max_val < 1e-10:
            return np.ones_like(self.values, dtype=bool)
        return np.abs(self.values) < threshold * max_val


@dataclass
class PetalDecomposition:
    """
    Decomposition of a flower into petals (connected nodal domains).
    """
    n_petals: int
    labels: NDArray[np.int32]       # Petal label for each point
    sizes: List[int]                 # Size of each petal
    centroids: List[NDArray]         # Centroid of each petal
    dominant_phases: List[int]       # Dominant phase in each petal
    
    def petal_mask(self, petal_idx: int) -> NDArray[np.bool_]:
        """Return mask for specific petal."""
        return self.labels == petal_idx


class FlowerEncoder:
    """
    Encode continuous flower modes into discrete seed-compatible patterns.
    """
    
    def __init__(self, n_phases: int = 4):
        self.n_phases = n_phases
    
    def sample(
        self,
        flower: FlowerMode,
        grid_size: int = 32,
    ) -> FlowerSampling:
        """Sample flower on grid and quantize."""
        # Sample on grid
        values = flower.sample_on_grid(grid_size)
        
        # Compute signs
        signs = np.sign(values).astype(np.int32)
        
        # Quantize to n_phases
        phases = self._quantize_phases(values)
        
        # Generate coordinates
        x = np.linspace(0, 1, grid_size)
        y = np.linspace(0, 1, grid_size)
        X, Y = np.meshgrid(x, y)
        coords = np.stack([X, Y], axis=-1)
        
        return FlowerSampling(
            values=values,
            signs=signs,
            phases=phases,
            coordinates=coords,
        )
    
    def _quantize_phases(self, values: NDArray) -> NDArray[np.int32]:
        """Quantize values to 4-phase alphabet."""
        # Map to [0, 1] range
        vmin, vmax = np.min(values), np.max(values)
        if vmax - vmin < 1e-10:
            return np.zeros_like(values, dtype=np.int32)
        
        normalized = (values - vmin) / (vmax - vmin)
        
        # Quantize to 4 levels
        phases = np.floor(normalized * self.n_phases).astype(np.int32)
        phases = np.clip(phases, 0, self.n_phases - 1)
        
        return phases
    
    def decompose_petals(
        self,
        sampling: FlowerSampling,
    ) -> PetalDecomposition:
        """Decompose sampled flower into petals."""
        from scipy.ndimage import label as ndimage_label
        
        # Label connected components of each sign
        positive_mask = sampling.signs > 0
        negative_mask = sampling.signs < 0
        
        labels = np.zeros_like(sampling.signs)
        
        # Label positive regions
        pos_labels, n_pos = ndimage_label(positive_mask)
        labels[positive_mask] = pos_labels[positive_mask]
        
        # Label negative regions (offset by n_pos)
        neg_labels, n_neg = ndimage_label(negative_mask)
        labels[negative_mask] = neg_labels[negative_mask] + n_pos
        
        n_petals = n_pos + n_neg
        
        # Compute petal statistics
        sizes = []
        centroids = []
        dominant_phases = []
        
        for i in range(1, n_petals + 1):
            mask = labels == i
            sizes.append(int(np.sum(mask)))
            
            # Centroid
            coords = sampling.coordinates[mask]
            if len(coords) > 0:
                centroids.append(np.mean(coords, axis=0))
            else:
                centroids.append(np.array([0.5, 0.5]))
            
            # Dominant phase
            phases = sampling.phases[mask]
            if len(phases) > 0:
                counts = np.bincount(phases, minlength=self.n_phases)
                dominant_phases.append(int(np.argmax(counts)))
            else:
                dominant_phases.append(0)
        
        return PetalDecomposition(
            n_petals=n_petals,
            labels=labels,
            sizes=sizes,
            centroids=centroids,
            dominant_phases=dominant_phases,
        )
    
    def compute_holographic_score(
        self,
        sampling: FlowerSampling,
        window_size: int = 2,
    ) -> float:
        """
        Compute local holography score.
        
        High score = windows have diverse phase content (seed-like).
        """
        phases = sampling.phases
        n = phases.shape[0]
        
        n_windows = 0
        diversity_sum = 0.0
        
        for i in range(n - window_size + 1):
            for j in range(n - window_size + 1):
                window = phases[i:i+window_size, j:j+window_size]
                unique = len(set(window.flatten()))
                diversity_sum += unique / self.n_phases
                n_windows += 1
        
        if n_windows == 0:
            return 0.0
        
        return diversity_sum / n_windows


class FlowerGenerator:
    """
    Generate flower modes with specified properties.
    """
    
    @staticmethod
    def rose(k: int, amplitude: float = 1.0) -> RoseCurve:
        """Create rose curve with k petals."""
        return RoseCurve(k=k, amplitude=amplitude)
    
    @staticmethod
    def laplacian_mode(nx: int, ny: int) -> LaplacianEigenfunction:
        """Create Laplacian eigenfunction."""
        return LaplacianEigenfunction(nx=nx, ny=ny)
    
    @staticmethod
    def superposition(
        modes: List[FlowerMode],
        weights: Optional[List[float]] = None,
        grid_size: int = 32,
    ) -> NDArray[np.float64]:
        """Create superposition of modes."""
        if weights is None:
            weights = [1.0] * len(modes)
        
        result = None
        for mode, w in zip(modes, weights):
            values = mode.sample_on_grid(grid_size)
            if result is None:
                result = w * values
            else:
                result += w * values
        
        return result


class SeedFlowerBridge:
    """
    Bridge between discrete seeds and continuous flowers.
    
    Implements the duality mapping:
    - Flower → Seed: Sampling and quantization
    - Seed → Flower: Interpolation and smoothing
    """
    
    def __init__(self):
        from atlasforge.klein4.klein4 import HolographicSeed, SeedTiling
        self.encoder = FlowerEncoder(n_phases=4)
        self.seed = HolographicSeed.canonical()
        self._SeedTiling = SeedTiling
    
    def flower_to_seed_pattern(
        self,
        flower: FlowerMode,
        grid_size: int = 32,
    ) -> Tuple[NDArray, float]:
        """
        Encode flower as seed-compatible pattern.
        
        Returns:
            (pattern, holography_score)
        """
        sampling = self.encoder.sample(flower, grid_size)
        score = self.encoder.compute_holographic_score(sampling)
        return sampling.phases, score
    
    def seed_to_flower_field(
        self,
        tile_shape: Tuple[int, int] = (4, 4),
        smoothing: float = 0.1,
    ) -> NDArray[np.float64]:
        """
        Lift tiled seed to smooth field.
        """
        tiling = self._SeedTiling(self.seed, tile_shape)
        pattern = tiling.pattern.astype(np.float64)
        
        # Center pattern
        pattern = pattern - np.mean(pattern)
        
        # Smooth via convolution
        if smoothing > 0:
            from scipy.ndimage import gaussian_filter
            pattern = gaussian_filter(pattern, sigma=smoothing * pattern.shape[0])
        
        return pattern
    
    def match_flower_to_seed(
        self,
        flower: FlowerMode,
        grid_size: int = 32,
    ) -> Dict[str, Any]:
        """
        Analyze how well a flower matches the holographic seed.
        """
        sampling = self.encoder.sample(flower, grid_size)
        petals = self.encoder.decompose_petals(sampling)
        score = self.encoder.compute_holographic_score(sampling)
        
        # Check if petal count is compatible with 4-fold structure
        is_tetradic = (petals.n_petals % 4 == 0 or 
                      petals.n_petals == flower.nodal_pattern().n_petals)
        
        return {
            'n_petals': petals.n_petals,
            'holography_score': score,
            'is_tetradic': is_tetradic,
            'dominant_phases': petals.dominant_phases,
            'nodal_pattern': flower.nodal_pattern(),
        }


def create_tetradic_flower(n_petals: int = 4) -> FlowerMode:
    """
    Create a flower with tetradic (4-fold) symmetry.
    """
    k = n_petals if n_petals % 2 == 1 else n_petals // 2
    return RoseCurve(k=k)


def analyze_flower_spectrum(
    modes: List[FlowerMode],
    grid_size: int = 32,
) -> Dict[str, Any]:
    """
    Analyze spectral properties of a collection of modes.
    """
    eigenvalues = []
    petal_counts = []
    
    for mode in modes:
        pattern = mode.nodal_pattern()
        eigenvalues.append(pattern.eigenvalue)
        petal_counts.append(pattern.n_petals)
    
    return {
        'eigenvalues': eigenvalues,
        'petal_counts': petal_counts,
        'spectral_gap': eigenvalues[1] - eigenvalues[0] if len(eigenvalues) > 1 else 0,
        'total_petals': sum(petal_counts),
    }

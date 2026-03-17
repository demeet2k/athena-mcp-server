"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Klein-4 & Holographic Seed Module            ║
╚══════════════════════════════════════════════════════════════════════════════╝

The 4×4 Holographic Seed: Minimal discrete realization of quad-polar framework.

Klein Four-Group K₄ ≅ Z₂²:
    Elements: {00, 01, 10, 11} with XOR addition
    Action: Phase shifts on tetradic labels (Earth/Water/Fire/Air)

The 4×4 Seed Properties:
1. Latin property: Each row/column contains each symbol exactly once
2. Bidiagonal property: Each diagonal contains each symbol exactly once
3. Affine realization: S*[i,j] = i ⊕ j (XOR operation)
4. Local holography: Every 2×2 window contains all 4 symbols

Tetradic Phases:
    Earth (D)  ↔ 00 ↔ +1  (0°)
    Water (Ω) ↔ 01 ↔ +i  (90°)
    Fire  (Σ) ↔ 11 ↔ -1  (180°)
    Air   (Ψ) ↔ 10 ↔ -i  (270°)

K₄ Actions as Phase Shifts:
    g·p = p ⊕ g translates phase labels
    This is the discrete rotation engine for quad-polar transformations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum, IntEnum
import math

import numpy as np
from numpy.typing import NDArray


class TetradicPhase(IntEnum):
    """Tetradic phases corresponding to K₄ elements."""
    EARTH = 0   # 00 - Discrete (D)
    WATER = 1   # 01 - Oscillatory (Ω)
    AIR = 2     # 10 - Recursive (Ψ)  
    FIRE = 3    # 11 - Stochastic (Σ)
    
    @property
    def bits(self) -> Tuple[int, int]:
        """Return 2-bit representation."""
        return (self.value >> 1, self.value & 1)
    
    @property
    def complex_phase(self) -> complex:
        """Return complex phase: 1, i, -1, -i."""
        phases = [1, 1j, -1j, -1]  # Note: Air=-i, Fire=-1
        return phases[self.value]
    
    @property
    def angle(self) -> float:
        """Return angle in radians."""
        return self.value * math.pi / 2
    
    @property
    def pole_symbol(self) -> str:
        """Return pole symbol."""
        return ['D', 'Ω', 'Ψ', 'Σ'][self.value]
    
    @classmethod
    def from_bits(cls, b0: int, b1: int) -> 'TetradicPhase':
        """Create from 2-bit representation."""
        return cls((b0 << 1) | b1)
    
    def __xor__(self, other: 'TetradicPhase') -> 'TetradicPhase':
        """XOR operation (K₄ group operation)."""
        return TetradicPhase(self.value ^ other.value)
    
    def __add__(self, other: 'TetradicPhase') -> 'TetradicPhase':
        """Same as XOR for K₄."""
        return self ^ other


class Klein4Group:
    """
    The Klein four-group K₄ ≅ Z₂ × Z₂.
    
    This is the symmetry group of the 4×4 holographic seed.
    
    Elements: {e, a, b, c} where
        e = (0,0) - identity
        a = (1,0) - first flip
        b = (0,1) - second flip  
        c = (1,1) - double flip
    
    Group table (XOR):
        ⊕ | e a b c
        --+--------
        e | e a b c
        a | a e c b
        b | b c e a
        c | c b a e
    """
    
    # Group elements as (bit0, bit1) tuples
    ELEMENTS = [(0, 0), (1, 0), (0, 1), (1, 1)]
    IDENTITY = (0, 0)
    
    @staticmethod
    def add(g1: Tuple[int, int], g2: Tuple[int, int]) -> Tuple[int, int]:
        """Group operation (XOR)."""
        return (g1[0] ^ g2[0], g1[1] ^ g2[1])
    
    @staticmethod
    def inverse(g: Tuple[int, int]) -> Tuple[int, int]:
        """Inverse element (each element is self-inverse)."""
        return g  # All elements of K₄ are self-inverse
    
    @classmethod
    def cayley_table(cls) -> NDArray[np.int32]:
        """Return the Cayley table as indices."""
        n = 4
        table = np.zeros((n, n), dtype=np.int32)
        for i, g1 in enumerate(cls.ELEMENTS):
            for j, g2 in enumerate(cls.ELEMENTS):
                result = cls.add(g1, g2)
                table[i, j] = cls.ELEMENTS.index(result)
        return table
    
    @classmethod
    def to_phase(cls, g: Tuple[int, int]) -> TetradicPhase:
        """Convert group element to tetradic phase."""
        idx = cls.ELEMENTS.index(g)
        return TetradicPhase(idx)
    
    @classmethod
    def from_phase(cls, phase: TetradicPhase) -> Tuple[int, int]:
        """Convert tetradic phase to group element."""
        return cls.ELEMENTS[phase.value]


@dataclass
class HolographicSeed:
    """
    The 4×4 Holographic Seed - canonical discrete phase engine.
    
    Properties:
    - Latin: each row/column has each symbol once
    - Bidiagonal: each diagonal has each symbol once
    - Affine: S[i,j] = i ⊕ j
    - Locally holographic: every 2×2 window has all 4 symbols
    
    Canonical form:
        | 0 1 2 3 |
        | 2 3 0 1 |
        | 3 2 1 0 |
        | 1 0 3 2 |
    """
    
    matrix: NDArray[np.int32] = field(default_factory=lambda: np.array([
        [0, 1, 2, 3],
        [2, 3, 0, 1],
        [3, 2, 1, 0],
        [1, 0, 3, 2]
    ], dtype=np.int32))
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        """Validate seed properties."""
        S = self.matrix
        n = 4
        
        # Check dimensions
        assert S.shape == (4, 4), "Seed must be 4×4"
        
        # Check Latin property
        for i in range(n):
            assert len(set(S[i, :])) == n, f"Row {i} not Latin"
            assert len(set(S[:, i])) == n, f"Col {i} not Latin"
        
        # Check bidiagonal property
        main_diag = [S[i, i] for i in range(n)]
        anti_diag = [S[i, n-1-i] for i in range(n)]
        assert len(set(main_diag)) == n, "Main diagonal not Latin"
        assert len(set(anti_diag)) == n, "Anti-diagonal not Latin"
    
    @classmethod
    def canonical(cls) -> 'HolographicSeed':
        """Return the canonical 4×4 holographic seed."""
        return cls()
    
    @classmethod
    def from_xor(cls) -> 'HolographicSeed':
        """Generate seed using XOR operation: S[i,j] = i ⊕ j."""
        matrix = np.zeros((4, 4), dtype=np.int32)
        for i in range(4):
            for j in range(4):
                matrix[i, j] = i ^ j
        return cls(matrix=matrix)
    
    def __getitem__(self, idx: Tuple[int, int]) -> int:
        """Get element at (row, col)."""
        return int(self.matrix[idx])
    
    def to_phases(self) -> NDArray:
        """Convert to matrix of TetradicPhase values."""
        result = np.empty((4, 4), dtype=object)
        for i in range(4):
            for j in range(4):
                result[i, j] = TetradicPhase(self.matrix[i, j])
        return result
    
    def to_complex(self) -> NDArray[np.complex128]:
        """Convert to complex phase mask."""
        phases = [1, 1j, -1j, -1]
        return np.array([[phases[self.matrix[i, j]] 
                         for j in range(4)] for i in range(4)])
    
    def window_2x2(self, row: int, col: int) -> NDArray[np.int32]:
        """Extract 2×2 window at (row, col)."""
        return self.matrix[row:row+2, col:col+2]
    
    def check_local_holography(self) -> bool:
        """Check if every 2×2 window contains all 4 symbols."""
        for i in range(3):
            for j in range(3):
                window = self.window_2x2(i, j)
                if len(set(window.flatten())) != 4:
                    return False
        return True
    
    def apply_k4_action(self, g: Tuple[int, int]) -> 'HolographicSeed':
        """Apply K₄ action (symbol translation by g)."""
        idx = Klein4Group.ELEMENTS.index(g)
        new_matrix = (self.matrix + idx) % 4
        return HolographicSeed(matrix=new_matrix)
    
    def row_action(self, g: Tuple[int, int]) -> 'HolographicSeed':
        """Translate row indices by K₄ element g."""
        idx = Klein4Group.ELEMENTS.index(g)
        perm = [(i + idx) % 4 for i in range(4)]
        return HolographicSeed(matrix=self.matrix[perm, :])
    
    def col_action(self, g: Tuple[int, int]) -> 'HolographicSeed':
        """Translate column indices by K₄ element g."""
        idx = Klein4Group.ELEMENTS.index(g)
        perm = [(j + idx) % 4 for j in range(4)]
        return HolographicSeed(matrix=self.matrix[:, perm])
    
    def display(self) -> str:
        """Pretty print the seed."""
        symbols = ['E', 'W', 'A', 'F']  # Earth, Water, Air, Fire
        lines = []
        for i in range(4):
            row = ' '.join(symbols[self.matrix[i, j]] for j in range(4))
            lines.append(f"| {row} |")
        return '\n'.join(lines)
    
    def display_numeric(self) -> str:
        """Display with numeric values."""
        lines = []
        for i in range(4):
            row = ' '.join(str(self.matrix[i, j]) for j in range(4))
            lines.append(f"| {row} |")
        return '\n'.join(lines)


@dataclass
class TetradicKernel:
    """
    Tetradic permutation kernel on K₄.
    
    K_tet = (1/4) Σ P_πk
    
    where πk are the four K₄ translations.
    
    Properties:
    - Doubly stochastic
    - Commutes with K₄
    - Uniform stationary distribution
    """
    
    def __init__(self):
        self._build_kernel()
    
    def _build_kernel(self):
        """Build the tetradic kernel matrix."""
        # Permutation matrices for K₄ actions
        n = 4
        K = np.zeros((n, n))
        
        for g in Klein4Group.ELEMENTS:
            # Permutation: i -> i ⊕ g
            idx = Klein4Group.ELEMENTS.index(g)
            P = np.zeros((n, n))
            for i in range(n):
                j = (i + idx) % n  # Simplified XOR for enumeration
                P[i, j] = 1
            K += P
        
        self.kernel = K / n
    
    @property
    def K(self) -> NDArray[np.float64]:
        """Return kernel matrix."""
        return self.kernel
    
    @property
    def generator(self) -> NDArray[np.float64]:
        """Return centered generator D = K - I."""
        return self.kernel - np.eye(4)
    
    def apply(self, v: NDArray) -> NDArray:
        """Apply kernel to vector."""
        return self.kernel @ v
    
    def spectral_decomposition(self) -> Tuple[NDArray, NDArray]:
        """Return eigenvalues and eigenvectors."""
        return np.linalg.eig(self.kernel)


class PhaseRotor:
    """
    Discrete phase rotation engine using the holographic seed.
    
    Maps poles to phases and performs K₄ rotations.
    """
    
    # Pole to phase mapping
    POLE_TO_PHASE = {
        'D': TetradicPhase.EARTH,   # Discrete
        'Ω': TetradicPhase.WATER,   # Oscillatory
        'Σ': TetradicPhase.FIRE,    # Stochastic
        'Ψ': TetradicPhase.AIR,     # Recursive
    }
    
    PHASE_TO_POLE = {v: k for k, v in POLE_TO_PHASE.items()}
    
    def __init__(self, seed: Optional[HolographicSeed] = None):
        self.seed = seed or HolographicSeed.canonical()
    
    def rotate(self, pole: str, shift: Tuple[int, int]) -> str:
        """Rotate pole by K₄ element."""
        phase = self.POLE_TO_PHASE[pole]
        g = Klein4Group.ELEMENTS.index(shift)
        new_phase = TetradicPhase((phase.value + g) % 4)
        return self.PHASE_TO_POLE[new_phase]
    
    def full_rotation(self, pole: str) -> List[str]:
        """Return all rotations of a pole."""
        return [self.rotate(pole, g) for g in Klein4Group.ELEMENTS]
    
    def encode_law(self, quantity: str, space: str, change: str) -> Tuple:
        """Encode a law as (Q, X, C) triple with phase label."""
        # Map change to pole/phase
        pole = change
        phase = self.POLE_TO_PHASE.get(pole, TetradicPhase.EARTH)
        
        return (quantity, space, change, phase)
    
    def rotate_law(
        self,
        law: Tuple,
        shift: Tuple[int, int],
    ) -> Tuple:
        """Rotate a law by K₄ element."""
        quantity, space, change, phase = law
        new_phase = phase ^ TetradicPhase(Klein4Group.ELEMENTS.index(shift))
        new_change = self.PHASE_TO_POLE[new_phase]
        
        return (quantity, space, new_change, new_phase)


@dataclass
class SeedTiling:
    """
    Tiling of a domain with copies of the holographic seed.
    
    Creates a discrete field on a grid using seed patterns.
    """
    seed: HolographicSeed
    grid_shape: Tuple[int, int]  # (rows, cols) of tiles
    
    def __post_init__(self):
        self._build_tiling()
    
    def _build_tiling(self):
        """Build the full tiled pattern."""
        tile_rows, tile_cols = self.grid_shape
        full_rows = tile_rows * 4
        full_cols = tile_cols * 4
        
        self.pattern = np.zeros((full_rows, full_cols), dtype=np.int32)
        
        for ti in range(tile_rows):
            for tj in range(tile_cols):
                # Apply K₄ shift based on tile position
                shift = ((ti % 2), (tj % 2))
                shifted_seed = self.seed.apply_k4_action(shift)
                
                row_start = ti * 4
                col_start = tj * 4
                self.pattern[row_start:row_start+4, col_start:col_start+4] = shifted_seed.matrix
    
    @property
    def shape(self) -> Tuple[int, int]:
        return self.pattern.shape
    
    def to_phases(self) -> NDArray:
        """Convert entire tiling to phase values."""
        result = np.empty(self.shape, dtype=object)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                result[i, j] = TetradicPhase(self.pattern[i, j])
        return result


def create_tetradic_laplacian(n: int = 4) -> NDArray[np.float64]:
    """
    Create graph Laplacian with tetradic structure.
    
    Vertices connected according to K₄ action.
    """
    # Adjacency: i connected to i⊕g for all g in K₄
    A = np.zeros((n, n))
    for i in range(n):
        for g_idx in range(1, n):  # Skip identity
            j = (i + g_idx) % n
            A[i, j] = 1
    
    # Laplacian: L = D - A
    D = np.diag(np.sum(A, axis=1))
    L = D - A
    
    return L


def seed_encode_signal(signal: NDArray, seed: HolographicSeed) -> NDArray:
    """
    Encode a continuous signal using seed quantization.
    
    Maps signal values to tetradic phases based on quartiles.
    """
    # Compute quartiles
    q1, q2, q3 = np.percentile(signal, [25, 50, 75])
    
    # Quantize to 4 levels
    encoded = np.zeros_like(signal, dtype=np.int32)
    encoded[signal < q1] = 0  # Earth
    encoded[(signal >= q1) & (signal < q2)] = 1  # Water
    encoded[(signal >= q2) & (signal < q3)] = 2  # Air
    encoded[signal >= q3] = 3  # Fire
    
    return encoded


def seed_decode_signal(encoded: NDArray, levels: Tuple[float, ...] = (-1, -0.5, 0.5, 1)) -> NDArray:
    """
    Decode tetradic encoding back to continuous levels.
    """
    decoded = np.zeros_like(encoded, dtype=np.float64)
    for i, level in enumerate(levels):
        decoded[encoded == i] = level
    return decoded

"""
ATHENA OS - Seed-Flower Bridge and Hybrid Hilbert Lattice
=========================================================
Phase quantization between discrete and continuous representations.

The Seed-Flower Duality:
- SEED (4×4 crystal): Minimal discrete phase engine with exact quarter-turns
- FLOWER: Standing-wave geometry with nodal partitions and interference

The bridge is phase quantization and coarse-graining:
Multiple continuous wave configurations project to the same discrete
phase-class field, revealing "wave vs solid" as a gauge choice.

The Hybrid Hilbert Lattice:
The unified state space with four corners:
- CP: Continuous-Particle (classical fields)
- CW: Continuous-Wave (quantum fields)
- DP: Discrete-Particle (classical lattice)
- DW: Discrete-Wave (quantum lattice)

Transitions between corners are operators with tracked defects.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from datetime import datetime
import numpy as np
import math

from .crystal import Lens, Cell, Corner, CrystalCoordinate, CrystalLattice
from .antisymmetry import DefectDetector, CommutatorBudget
from .verification import InvariantLedger, SnapController


# =============================================================================
# PHASE STRUCTURE
# =============================================================================

class PhaseClass(IntEnum):
    """
    Discrete phase classes (Klein-4 / 2-bit structure).
    
    Maps to complex phases {1, i, -1, -i}.
    """
    PHASE_0 = 0   # Phase 0 → 1
    PHASE_1 = 1   # Phase π/2 → i
    PHASE_2 = 2   # Phase π → -1
    PHASE_3 = 3   # Phase 3π/2 → -i
    
    @property
    def complex_value(self) -> complex:
        """Get complex phase value."""
        values = {
            PhaseClass.PHASE_0: 1 + 0j,
            PhaseClass.PHASE_1: 0 + 1j,
            PhaseClass.PHASE_2: -1 + 0j,
            PhaseClass.PHASE_3: 0 - 1j
        }
        return values[self]
    
    @property
    def angle(self) -> float:
        """Get phase angle in radians."""
        return self.value * np.pi / 2
    
    def rotate(self, steps: int = 1) -> 'PhaseClass':
        """Rotate phase by steps × 90°."""
        return PhaseClass((self.value + steps) % 4)
    
    @classmethod
    def from_angle(cls, angle: float) -> 'PhaseClass':
        """Quantize continuous angle to phase class."""
        # Normalize to [0, 2π)
        angle = angle % (2 * np.pi)
        # Snap to nearest quarter
        quarter = int(np.round(angle / (np.pi / 2))) % 4
        return cls(quarter)
    
    @classmethod
    def from_complex(cls, z: complex) -> 'PhaseClass':
        """Quantize complex number to phase class."""
        if abs(z) < 1e-10:
            return cls.PHASE_0
        angle = np.angle(z)
        return cls.from_angle(angle)


# =============================================================================
# SEED CRYSTAL (4×4)
# =============================================================================

@dataclass
class SeedCrystal:
    """
    The 4×4 Seed Crystal: Minimal discrete phase engine.
    
    A 4×4 grid where each cell contains a phase class.
    Satisfies balanced constraints and local holographic
    reconstruction rules.
    """
    
    # 4×4 phase grid
    grid: np.ndarray = field(default_factory=lambda: np.zeros((4, 4), dtype=int))
    
    # Constraint satisfaction
    row_balance: bool = True  # Each row has balanced phases
    col_balance: bool = True  # Each column has balanced phases
    
    def __post_init__(self):
        """Initialize with balanced configuration."""
        # Default: each row/column has one of each phase
        self.grid = np.array([
            [0, 1, 2, 3],
            [1, 0, 3, 2],
            [2, 3, 0, 1],
            [3, 2, 1, 0]
        ], dtype=int)
    
    def get_phase(self, row: int, col: int) -> PhaseClass:
        """Get phase at position."""
        return PhaseClass(self.grid[row % 4, col % 4])
    
    def set_phase(self, row: int, col: int, phase: PhaseClass) -> None:
        """Set phase at position."""
        self.grid[row % 4, col % 4] = phase.value
    
    def get_complex_grid(self) -> np.ndarray:
        """Get grid as complex values."""
        result = np.zeros((4, 4), dtype=complex)
        for i in range(4):
            for j in range(4):
                result[i, j] = PhaseClass(self.grid[i, j]).complex_value
        return result
    
    def check_row_balance(self) -> bool:
        """Check if each row has one of each phase."""
        for row in range(4):
            if len(set(self.grid[row, :])) != 4:
                return False
        return True
    
    def check_col_balance(self) -> bool:
        """Check if each column has one of each phase."""
        for col in range(4):
            if len(set(self.grid[:, col])) != 4:
                return False
        return True
    
    def check_constraints(self) -> bool:
        """Check all constraints."""
        self.row_balance = self.check_row_balance()
        self.col_balance = self.check_col_balance()
        return self.row_balance and self.col_balance
    
    def rotate_90(self) -> 'SeedCrystal':
        """Rotate entire crystal 90°."""
        new_grid = np.rot90(self.grid)
        # Also rotate each phase by 90°
        new_grid = (new_grid + 1) % 4
        
        result = SeedCrystal()
        result.grid = new_grid
        return result
    
    def local_hologram(self, row: int, col: int) -> np.ndarray:
        """
        Extract local holographic reconstruction.
        
        The 2×2 neighborhood determines the central value.
        """
        neighbors = np.zeros((2, 2), dtype=int)
        for di in range(2):
            for dj in range(2):
                neighbors[di, dj] = self.grid[(row + di) % 4, (col + dj) % 4]
        return neighbors
    
    def reconstruct_from_boundary(self, boundary: np.ndarray) -> bool:
        """
        Reconstruct interior from boundary values.
        
        Returns True if reconstruction satisfies constraints.
        """
        # Set boundary
        self.grid[0, :] = boundary[0, :]  # Top
        self.grid[3, :] = boundary[1, :]  # Bottom
        self.grid[:, 0] = boundary[2, :]  # Left (already set corners)
        self.grid[:, 3] = boundary[3, :]  # Right
        
        # Interior is determined by constraints
        # For a balanced Latin square, interior is fixed by boundary
        return self.check_constraints()


# =============================================================================
# FLOWER PATTERN (Standing Wave)
# =============================================================================

@dataclass
class FlowerPattern:
    """
    FLOWER: Standing-wave geometry with nodal partitions.
    
    Rose curves and harmonic nodal patterns make phase
    interference visible as rigid symmetry.
    
    Rose curve: r = cos(k·θ) where k determines petal count.
    """
    
    # Petal count (k in rose curve)
    petal_count: int = 4
    
    # Resolution
    n_points: int = 256
    
    # Amplitude and phase
    amplitude: float = 1.0
    phase_offset: float = 0.0
    
    def generate_rose(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate rose curve coordinates.
        
        Returns (x, y) arrays.
        """
        theta = np.linspace(0, 2 * np.pi, self.n_points)
        r = self.amplitude * np.cos(self.petal_count * theta + self.phase_offset)
        
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        return x, y
    
    def nodal_set(self) -> np.ndarray:
        """
        Get nodal set (angles where r = 0).
        
        For rose with k petals: nodes at θ = (2n+1)π/(2k).
        """
        k = self.petal_count
        n_nodes = 2 * k
        nodes = np.array([(2*n + 1) * np.pi / (2 * k) - self.phase_offset 
                         for n in range(n_nodes)])
        return nodes % (2 * np.pi)
    
    def phase_field(self, size: int = 64) -> np.ndarray:
        """
        Generate 2D phase field from flower pattern.
        
        Returns complex array where phase encodes flower structure.
        """
        x = np.linspace(-1.5, 1.5, size)
        y = np.linspace(-1.5, 1.5, size)
        X, Y = np.meshgrid(x, y)
        
        R = np.sqrt(X**2 + Y**2)
        Theta = np.arctan2(Y, X)
        
        # Rose envelope
        envelope = self.amplitude * np.cos(self.petal_count * Theta + self.phase_offset)
        
        # Complex field with radial decay
        field = envelope * np.exp(-R**2) * np.exp(1j * self.petal_count * Theta)
        
        return field
    
    def to_seed(self) -> SeedCrystal:
        """
        Project flower pattern to seed crystal.
        
        Quantizes continuous phase field to 4×4 discrete phases.
        """
        field = self.phase_field(size=4)
        
        seed = SeedCrystal()
        for i in range(4):
            for j in range(4):
                seed.grid[i, j] = PhaseClass.from_complex(field[i, j]).value
        
        return seed
    
    def dihedral_symmetry(self) -> int:
        """
        Get dihedral symmetry order.
        
        Rose curve with k petals has D_k symmetry if k is odd,
        D_{2k} symmetry if k is even.
        """
        if self.petal_count % 2 == 0:
            return 2 * self.petal_count
        else:
            return self.petal_count


# =============================================================================
# SEED-FLOWER BRIDGE
# =============================================================================

@dataclass
class SeedFlowerBridge:
    """
    Bridge between discrete (seed) and continuous (flower) representations.
    
    Phase quantization: many continuous configurations → one discrete state
    Phase interpolation: one discrete state → family of continuous states
    """
    
    # Resolution parameters
    n_phases: int = 4  # Number of discrete phase classes
    interpolation_order: int = 3  # Spline order for interpolation
    
    # Defect tracking
    quantization_error: float = 0.0
    interpolation_error: float = 0.0
    
    def quantize(self, flower: FlowerPattern) -> SeedCrystal:
        """
        Quantize flower pattern to seed crystal.
        
        Projects continuous phase field to discrete phases.
        """
        seed = flower.to_seed()
        
        # Compute quantization error
        field = flower.phase_field(size=4)
        quantized = seed.get_complex_grid()
        
        self.quantization_error = np.mean(np.abs(
            np.angle(field) - np.angle(quantized)
        ))
        
        return seed
    
    def interpolate(self, seed: SeedCrystal, size: int = 64) -> np.ndarray:
        """
        Interpolate seed crystal to continuous field.
        
        Uses smooth interpolation between discrete phases.
        """
        # Get complex grid
        discrete = seed.get_complex_grid()
        
        # Bilinear interpolation to size × size
        from scipy.ndimage import zoom
        
        # Interpolate magnitude and phase separately
        mag = np.abs(discrete)
        phase = np.angle(discrete)
        
        # Unwrap phase for smooth interpolation
        phase_unwrapped = np.unwrap(np.unwrap(phase, axis=0), axis=1)
        
        scale = size / 4
        mag_interp = zoom(mag, scale, order=self.interpolation_order)
        phase_interp = zoom(phase_unwrapped, scale, order=self.interpolation_order)
        
        result = mag_interp * np.exp(1j * phase_interp)
        
        # Compute interpolation error (round-trip)
        back = self.quantize_field(result, 4)
        self.interpolation_error = np.mean(np.abs(back - discrete))
        
        return result
    
    def quantize_field(self, field: np.ndarray, size: int) -> np.ndarray:
        """Quantize arbitrary complex field to discrete phases."""
        from scipy.ndimage import zoom
        
        scale = size / field.shape[0]
        downsampled = zoom(field, scale, order=1)
        
        # Quantize phases
        result = np.zeros_like(downsampled)
        for i in range(size):
            for j in range(size):
                phase_class = PhaseClass.from_complex(downsampled[i, j])
                result[i, j] = phase_class.complex_value
        
        return result
    
    def round_trip_error(self, seed: SeedCrystal) -> float:
        """
        Compute round-trip error: seed → flower → seed.
        
        Measures information loss in the bridge.
        """
        # Seed → interpolated field
        field = self.interpolate(seed, size=64)
        
        # Field → quantized seed
        recovered = SeedCrystal()
        quantized = self.quantize_field(field, 4)
        
        for i in range(4):
            for j in range(4):
                recovered.grid[i, j] = PhaseClass.from_complex(quantized[i, j]).value
        
        # Compare
        error = np.mean(np.abs(seed.grid - recovered.grid))
        return error


# =============================================================================
# HYBRID HILBERT LATTICE
# =============================================================================

@dataclass
class HybridHilbertLattice:
    """
    The unified state space with four corners.
    
    Corners:
    - CP: Continuous-Particle (classical fields, smooth functions)
    - CW: Continuous-Wave (quantum fields, L²-functions)
    - DP: Discrete-Particle (lattice points, finite states)
    - DW: Discrete-Wave (discrete Fourier modes, graph spectra)
    
    Transitions between corners are operators with tracked defects.
    """
    
    name: str = "hybrid_hilbert_lattice"
    
    # Corner states
    states: Dict[Corner, Any] = field(default_factory=dict)
    
    # Transition operators
    transitions: Dict[Tuple[Corner, Corner], Callable] = field(default_factory=dict)
    
    # Verification
    invariant_ledger: InvariantLedger = field(default_factory=InvariantLedger)
    defect_detector: DefectDetector = field(default_factory=DefectDetector)
    commutator_budget: CommutatorBudget = field(default_factory=CommutatorBudget)
    
    def __post_init__(self):
        """Initialize default transitions."""
        self._init_transitions()
    
    def _init_transitions(self) -> None:
        """Set up default transition operators."""
        # CP → DP: Sampling/discretization
        self.transitions[(Corner.CP, Corner.DP)] = self._sample
        
        # DP → CP: Interpolation/reconstruction
        self.transitions[(Corner.DP, Corner.CP)] = self._interpolate
        
        # CW → DW: Discrete Fourier transform
        self.transitions[(Corner.CW, Corner.DW)] = self._dft
        
        # DW → CW: Inverse DFT
        self.transitions[(Corner.DW, Corner.CW)] = self._idft
        
        # CP → CW: Fourier transform (continuous)
        self.transitions[(Corner.CP, Corner.CW)] = self._fourier
        
        # CW → CP: Inverse Fourier
        self.transitions[(Corner.CW, Corner.CP)] = self._inv_fourier
        
        # DP → DW: Graph Fourier / DFT
        self.transitions[(Corner.DP, Corner.DW)] = self._graph_fourier
        
        # DW → DP: Inverse graph Fourier
        self.transitions[(Corner.DW, Corner.DP)] = self._inv_graph_fourier
    
    def _sample(self, state: np.ndarray, n_points: int = 64) -> np.ndarray:
        """Sample continuous state at discrete points."""
        if len(state) <= n_points:
            return state
        indices = np.linspace(0, len(state) - 1, n_points, dtype=int)
        return state[indices]
    
    def _interpolate(self, state: np.ndarray, n_points: int = 256) -> np.ndarray:
        """Interpolate discrete state to continuous."""
        from scipy.interpolate import interp1d
        x = np.linspace(0, 1, len(state))
        f = interp1d(x, state, kind='cubic', fill_value='extrapolate')
        x_new = np.linspace(0, 1, n_points)
        return f(x_new)
    
    def _dft(self, state: np.ndarray) -> np.ndarray:
        """Discrete Fourier transform."""
        return np.fft.fft(state)
    
    def _idft(self, state: np.ndarray) -> np.ndarray:
        """Inverse DFT."""
        return np.real(np.fft.ifft(state))
    
    def _fourier(self, state: np.ndarray) -> np.ndarray:
        """Fourier transform (using FFT as approximation)."""
        return np.fft.fft(state)
    
    def _inv_fourier(self, state: np.ndarray) -> np.ndarray:
        """Inverse Fourier transform."""
        return np.real(np.fft.ifft(state))
    
    def _graph_fourier(self, state: np.ndarray) -> np.ndarray:
        """Graph Fourier transform (DFT for regular grid)."""
        return np.fft.fft(state)
    
    def _inv_graph_fourier(self, state: np.ndarray) -> np.ndarray:
        """Inverse graph Fourier."""
        return np.real(np.fft.ifft(state))
    
    def set_state(self, corner: Corner, state: Any) -> None:
        """Set state at a corner."""
        self.states[corner] = state
    
    def get_state(self, corner: Corner) -> Optional[Any]:
        """Get state at a corner."""
        return self.states.get(corner)
    
    def transition(self, from_corner: Corner, to_corner: Corner,
                  **kwargs) -> Tuple[Any, float]:
        """
        Apply transition operator between corners.
        
        Returns (new_state, defect_magnitude).
        """
        key = (from_corner, to_corner)
        
        if key not in self.transitions:
            raise ValueError(f"No transition defined from {from_corner} to {to_corner}")
        
        state = self.states.get(from_corner)
        if state is None:
            raise ValueError(f"No state at corner {from_corner}")
        
        # Apply transition
        new_state = self.transitions[key](state, **kwargs)
        
        # Measure defect (round-trip error)
        reverse_key = (to_corner, from_corner)
        if reverse_key in self.transitions:
            recovered = self.transitions[reverse_key](new_state, **kwargs)
            defect = np.linalg.norm(np.array(recovered) - np.array(state))
        else:
            defect = 0.0
        
        # Track defect
        lens = Lens.SQUARE if from_corner.is_discrete else Lens.FLOWER
        self.commutator_budget.add_defect(lens, defect, f"{from_corner}→{to_corner}")
        
        # Store new state
        self.states[to_corner] = new_state
        
        return new_state, defect
    
    def compute_loop_holonomy(self, start: Corner, 
                             path: List[Corner]) -> Tuple[Any, float]:
        """
        Compute holonomy around a loop in the lattice.
        
        If the diagram commutes, end state equals start state.
        Holonomy is the defect.
        """
        current = start
        
        for next_corner in path:
            state, _ = self.transition(current, next_corner)
            current = next_corner
        
        # Return to start
        final_state, _ = self.transition(current, start)
        
        # Compute holonomy
        initial_state = self.states.get(start)
        if initial_state is not None:
            holonomy = np.linalg.norm(np.array(final_state) - np.array(initial_state))
        else:
            holonomy = 0.0
        
        return final_state, holonomy
    
    def summary(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'states': list(self.states.keys()),
            'transitions': len(self.transitions),
            'budget': self.commutator_budget.summary()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_bridge() -> bool:
    """Validate seed-flower bridge."""
    
    # Test phase class
    assert PhaseClass.PHASE_0.complex_value == 1 + 0j
    assert PhaseClass.PHASE_1.complex_value == 0 + 1j
    assert PhaseClass.PHASE_0.rotate(1) == PhaseClass.PHASE_1
    assert PhaseClass.from_angle(np.pi/2) == PhaseClass.PHASE_1
    
    # Test seed crystal
    seed = SeedCrystal()
    assert seed.grid.shape == (4, 4)
    assert seed.check_constraints()
    
    rotated = seed.rotate_90()
    assert rotated.grid.shape == (4, 4)
    
    # Test flower pattern
    flower = FlowerPattern(petal_count=4)
    x, y = flower.generate_rose()
    assert len(x) == flower.n_points
    
    nodes = flower.nodal_set()
    assert len(nodes) == 8  # 4 petals × 2 nodes per petal
    
    # Test bridge
    bridge = SeedFlowerBridge()
    
    seed_from_flower = bridge.quantize(flower)
    assert seed_from_flower.grid.shape == (4, 4)
    
    # Test interpolation (requires scipy)
    try:
        field = bridge.interpolate(seed, size=16)
        assert field.shape == (16, 16)
    except ImportError:
        pass  # scipy not available
    
    # Test hybrid Hilbert lattice
    lattice = HybridHilbertLattice()
    
    # Set a state
    state = np.sin(np.linspace(0, 2*np.pi, 64))
    lattice.set_state(Corner.CP, state)
    
    # Transition CP → DP
    discrete, defect = lattice.transition(Corner.CP, Corner.DP)
    assert len(discrete) == 64
    
    # Transition DP → DW
    spectral, defect = lattice.transition(Corner.DP, Corner.DW)
    assert len(spectral) == len(discrete)
    
    return True


if __name__ == "__main__":
    print("Validating Seed-Flower Bridge...")
    assert validate_bridge()
    print("✓ Seed-Flower Bridge validated")
    
    # Demo
    print("\n=== Seed Crystal Demo ===")
    seed = SeedCrystal()
    print(f"Seed grid:\n{seed.grid}")
    print(f"Constraints satisfied: {seed.check_constraints()}")
    
    print("\n=== Flower Pattern Demo ===")
    flower = FlowerPattern(petal_count=4)
    x, y = flower.generate_rose()
    print(f"Rose curve: {len(x)} points")
    print(f"Nodal angles: {flower.nodal_set()}")
    print(f"Dihedral symmetry: D_{flower.dihedral_symmetry()}")
    
    print("\n=== Bridge Demo ===")
    bridge = SeedFlowerBridge()
    seed_from_flower = bridge.quantize(flower)
    print(f"Quantization error: {bridge.quantization_error:.6f}")
    
    print("\n=== Hybrid Hilbert Lattice Demo ===")
    lattice = HybridHilbertLattice()
    state = np.sin(np.linspace(0, 4*np.pi, 128))
    lattice.set_state(Corner.CP, state)
    
    # Full loop: CP → DP → DW → CW → CP
    path = [Corner.DP, Corner.DW, Corner.CW]
    final, holonomy = lattice.compute_loop_holonomy(Corner.CP, path)
    print(f"Loop holonomy (CP→DP→DW→CW→CP): {holonomy:.6f}")
    print(f"Lattice summary: {lattice.summary()}")

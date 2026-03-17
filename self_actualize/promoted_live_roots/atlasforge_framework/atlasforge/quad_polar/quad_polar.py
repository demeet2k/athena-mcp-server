"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      QUAD-POLAR COSMOLOGY MODULE                             ║
║                                                                              ║
║  The Four Universes and Their Couplings                                      ║
║                                                                              ║
║  The Four Universes:                                                         ║
║    U_ℝ+ (Primal)    : Matter, manifest events, positive real sector         ║
║    U_ℝ- (Inverted)  : Void, repulsive geometry, negative real sector        ║
║    U_𝕀+ (Imaginary) : Probability, superposition, imaginary positive        ║
║    U_𝕀- (Conjugate) : Memory, records, holographic boundary data            ║
║                                                                              ║
║  Total State Space:                                                          ║
║    H_tot = H_+ ⊕ H_- ⊕ H_i ⊕ H_ī                                            ║
║                                                                              ║
║  Quaternionic Encoding:                                                      ║
║    |Ψ⟩ ≅ |ψ_+⟩ + i|ψ_i⟩ + j|ψ_-⟩ + k|ψ_ī⟩                                   ║
║                                                                              ║
║  Coupling Structure:                                                         ║
║    C_{i→+} : Collapse (wave → event)                                        ║
║    C_{+→ī} : Logging (event → record)                                       ║
║    C_{ī→-} : Geometry induction (record → void structure)                   ║
║    C_{-→i} : Re-oscillation (void → potential)                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# UNIVERSE SECTORS
# ═══════════════════════════════════════════════════════════════════════════════

class UniverseSector(Enum):
    """The four universe sectors."""
    PRIMAL = "primal"       # U_ℝ+ : Matter, manifest events
    INVERTED = "inverted"   # U_ℝ- : Void, repulsive geometry
    IMAGINARY = "imaginary" # U_𝕀+ : Probability, superposition
    CONJUGATE = "conjugate" # U_𝕀- : Memory, records


@dataclass
class SectorProperties:
    """Properties of a universe sector."""
    sector: UniverseSector
    symbol: str
    domain: str
    physical_interpretation: str
    mathematical_structure: str
    
    @classmethod
    def primal(cls) -> 'SectorProperties':
        """Primal Universe properties."""
        return cls(
            UniverseSector.PRIMAL,
            "ℝ+",
            "Real positive",
            "Matter and manifest events",
            "Lorentzian manifolds, gauge bundles, classical/quantum fields"
        )
    
    @classmethod
    def inverted(cls) -> 'SectorProperties':
        """Inverted Universe properties."""
        return cls(
            UniverseSector.INVERTED,
            "ℝ-",
            "Real negative",
            "Void and repulsive geometry",
            "Expansion, smoothing, syntropic order formation"
        )
    
    @classmethod
    def imaginary(cls) -> 'SectorProperties':
        """Imaginary Universe properties."""
        return cls(
            UniverseSector.IMAGINARY,
            "𝕀+",
            "Imaginary positive",
            "Probability, superposition, pure potential",
            "Hilbert space with oscillatory modes and phase dynamics"
        )
    
    @classmethod
    def conjugate(cls) -> 'SectorProperties':
        """Conjugate Universe properties."""
        return cls(
            UniverseSector.CONJUGATE,
            "𝕀-",
            "Imaginary negative",
            "Memory, records, holographic boundary data",
            "Static/slowly evolving information about histories"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTOR HILBERT SPACES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SectorHilbertSpace:
    """
    Hilbert space for a universe sector.
    
    Each sector has its own H_α with projector P_α.
    """
    sector: UniverseSector
    dimension: int  # Can be infinite (represented as -1)
    basis_labels: List[str] = field(default_factory=list)
    
    @property
    def is_infinite_dimensional(self) -> bool:
        return self.dimension == -1
    
    def projector(self, state: NDArray) -> NDArray:
        """
        Project onto this sector.
        
        P_α|Ψ⟩ = |ψ_α⟩
        """
        # For finite-dimensional representation
        if len(state) >= 4:
            idx = list(UniverseSector).index(self.sector)
            result = np.zeros_like(state)
            result[idx] = state[idx]
            return result
        return state


@dataclass
class TotalHilbertSpace:
    """
    Total state space as orthogonal direct sum.
    
    H_tot = H_+ ⊕ H_- ⊕ H_i ⊕ H_ī
    """
    h_primal: SectorHilbertSpace
    h_inverted: SectorHilbertSpace
    h_imaginary: SectorHilbertSpace
    h_conjugate: SectorHilbertSpace
    
    @classmethod
    def create(cls, dim: int = -1) -> 'TotalHilbertSpace':
        """Create total Hilbert space with equal sector dimensions."""
        return cls(
            SectorHilbertSpace(UniverseSector.PRIMAL, dim),
            SectorHilbertSpace(UniverseSector.INVERTED, dim),
            SectorHilbertSpace(UniverseSector.IMAGINARY, dim),
            SectorHilbertSpace(UniverseSector.CONJUGATE, dim)
        )
    
    def get_sector(self, sector: UniverseSector) -> SectorHilbertSpace:
        """Get Hilbert space for sector."""
        mapping = {
            UniverseSector.PRIMAL: self.h_primal,
            UniverseSector.INVERTED: self.h_inverted,
            UniverseSector.IMAGINARY: self.h_imaginary,
            UniverseSector.CONJUGATE: self.h_conjugate
        }
        return mapping[sector]


# ═══════════════════════════════════════════════════════════════════════════════
# QUAD-POLAR STATE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuadPolarState:
    """
    Combined state of reality at crystal time τ.
    
    |Ψ(τ)⟩ = (|ψ_+⟩, |ψ_-⟩, |ψ_i⟩, |ψ_ī⟩)^T ∈ H_tot
    
    Quaternionic encoding:
    |Ψ⟩ ≅ |ψ_+⟩ + i|ψ_i⟩ + j|ψ_-⟩ + k|ψ_ī⟩
    """
    psi_primal: complex      # |ψ_+⟩ coefficient
    psi_inverted: complex    # |ψ_-⟩ coefficient
    psi_imaginary: complex   # |ψ_i⟩ coefficient
    psi_conjugate: complex   # |ψ_ī⟩ coefficient
    tau: float = 0.0         # Crystal time
    
    @property
    def as_vector(self) -> NDArray:
        """State as 4-component vector."""
        return np.array([
            self.psi_primal,
            self.psi_inverted,
            self.psi_imaginary,
            self.psi_conjugate
        ], dtype=complex)
    
    @property
    def norm_squared(self) -> float:
        """Total probability |Ψ|²."""
        return float(np.sum(np.abs(self.as_vector) ** 2))
    
    def normalize(self) -> 'QuadPolarState':
        """Return normalized state."""
        norm = np.sqrt(self.norm_squared)
        if norm < 1e-15:
            return self
        return QuadPolarState(
            self.psi_primal / norm,
            self.psi_inverted / norm,
            self.psi_imaginary / norm,
            self.psi_conjugate / norm,
            self.tau
        )
    
    @property
    def sector_probabilities(self) -> Dict[UniverseSector, float]:
        """Probability in each sector."""
        total = self.norm_squared
        if total < 1e-15:
            return {s: 0.25 for s in UniverseSector}
        return {
            UniverseSector.PRIMAL: abs(self.psi_primal) ** 2 / total,
            UniverseSector.INVERTED: abs(self.psi_inverted) ** 2 / total,
            UniverseSector.IMAGINARY: abs(self.psi_imaginary) ** 2 / total,
            UniverseSector.CONJUGATE: abs(self.psi_conjugate) ** 2 / total
        }
    
    @classmethod
    def uniform(cls, tau: float = 0.0) -> 'QuadPolarState':
        """Equal superposition across all sectors."""
        return cls(0.5, 0.5, 0.5, 0.5, tau)
    
    @classmethod
    def primal_dominated(cls, weight: float = 0.9, tau: float = 0.0) -> 'QuadPolarState':
        """Primal-dominated state (matter-heavy)."""
        other = np.sqrt((1 - weight**2) / 3)
        return cls(weight, other, other, other, tau)


# ═══════════════════════════════════════════════════════════════════════════════
# QUATERNIONIC REPRESENTATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Quaternion:
    """
    Quaternion q = a + bi + cj + dk.
    
    Used for encoding quad-polar states.
    """
    a: float  # Real part (Primal)
    b: float  # i coefficient (Imaginary)
    c: float  # j coefficient (Inverted)
    d: float  # k coefficient (Conjugate)
    
    @property
    def norm(self) -> float:
        """Quaternion norm."""
        return np.sqrt(self.a**2 + self.b**2 + self.c**2 + self.d**2)
    
    def conjugate(self) -> 'Quaternion':
        """Quaternion conjugate."""
        return Quaternion(self.a, -self.b, -self.c, -self.d)
    
    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        """Quaternion multiplication (Hamilton product)."""
        return Quaternion(
            self.a*other.a - self.b*other.b - self.c*other.c - self.d*other.d,
            self.a*other.b + self.b*other.a + self.c*other.d - self.d*other.c,
            self.a*other.c - self.b*other.d + self.c*other.a + self.d*other.b,
            self.a*other.d + self.b*other.c - self.c*other.b + self.d*other.a
        )
    
    def to_quad_polar_state(self, tau: float = 0.0) -> QuadPolarState:
        """Convert to quad-polar state."""
        return QuadPolarState(
            complex(self.a, 0),
            complex(self.c, 0),
            complex(self.b, 0),
            complex(self.d, 0),
            tau
        )
    
    @classmethod
    def from_quad_polar_state(cls, state: QuadPolarState) -> 'Quaternion':
        """Create from quad-polar state."""
        return cls(
            state.psi_primal.real,
            state.psi_imaginary.real,
            state.psi_inverted.real,
            state.psi_conjugate.real
        )


# ═══════════════════════════════════════════════════════════════════════════════
# COUPLING OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class CouplingType(Enum):
    """Types of inter-sector couplings."""
    COLLAPSE = "collapse"           # C_{i→+} : wave → event
    LOGGING = "logging"             # C_{+→ī} : event → record
    GEOMETRY_INDUCTION = "geometry" # C_{ī→-} : record → void
    RE_OSCILLATION = "oscillation"  # C_{-→i} : void → potential


@dataclass
class CouplingOperator:
    """
    Coupling operator between universe sectors.
    
    C_{α→β} : H_α → H_β
    """
    coupling_type: CouplingType
    source: UniverseSector
    target: UniverseSector
    strength: float = 1.0
    description: str = ""
    
    @classmethod
    def collapse(cls, strength: float = 1.0) -> 'CouplingOperator':
        """
        Collapse map: C_{i→+}
        
        Sends wave-like potential to realized events.
        """
        return cls(
            CouplingType.COLLAPSE,
            UniverseSector.IMAGINARY,
            UniverseSector.PRIMAL,
            strength,
            "Wave function collapse: probability → manifest event"
        )
    
    @classmethod
    def logging(cls, strength: float = 1.0) -> 'CouplingOperator':
        """
        Logging map: C_{+→ī}
        
        Sends primal events to conjugate records.
        """
        return cls(
            CouplingType.LOGGING,
            UniverseSector.PRIMAL,
            UniverseSector.CONJUGATE,
            strength,
            "Holographic logging: event → memory record"
        )
    
    @classmethod
    def geometry_induction(cls, strength: float = 1.0) -> 'CouplingOperator':
        """
        Geometry induction: C_{ī→-}
        
        Translates records into void structure.
        """
        return cls(
            CouplingType.GEOMETRY_INDUCTION,
            UniverseSector.CONJUGATE,
            UniverseSector.INVERTED,
            strength,
            "Record → geometric configuration in void"
        )
    
    @classmethod
    def re_oscillation(cls, strength: float = 1.0) -> 'CouplingOperator':
        """
        Re-oscillation: C_{-→i}
        
        Converts void geometry back to quantum potential.
        """
        return cls(
            CouplingType.RE_OSCILLATION,
            UniverseSector.INVERTED,
            UniverseSector.IMAGINARY,
            strength,
            "Void → oscillatory tensions and potentials"
        )
    
    def apply(self, state: QuadPolarState, dt: float = 0.01) -> QuadPolarState:
        """Apply coupling operator to state."""
        v = state.as_vector.copy()
        
        source_idx = list(UniverseSector).index(self.source)
        target_idx = list(UniverseSector).index(self.target)
        
        # Transfer amplitude from source to target
        transfer = self.strength * dt * v[source_idx]
        v[source_idx] -= transfer
        v[target_idx] += transfer
        
        return QuadPolarState(
            v[0], v[1], v[2], v[3],
            state.tau + dt
        )


@dataclass
class CouplingCycle:
    """
    Complete cycle of inter-sector couplings.
    
    Forms a closed loop: i → + → ī → - → i
    """
    collapse: CouplingOperator = field(default_factory=CouplingOperator.collapse)
    logging: CouplingOperator = field(default_factory=CouplingOperator.logging)
    geometry: CouplingOperator = field(default_factory=CouplingOperator.geometry_induction)
    oscillation: CouplingOperator = field(default_factory=CouplingOperator.re_oscillation)
    
    @property
    def operators(self) -> List[CouplingOperator]:
        """All coupling operators in cycle order."""
        return [self.collapse, self.logging, self.geometry, self.oscillation]
    
    def apply_cycle(self, state: QuadPolarState, dt: float = 0.01) -> QuadPolarState:
        """Apply complete coupling cycle."""
        current = state
        for op in self.operators:
            current = op.apply(current, dt)
        return current


# ═══════════════════════════════════════════════════════════════════════════════
# Q-HAMILTONIAN
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SectorHamiltonian:
    """
    Sector Q-Hamiltonian H_α.
    
    Governs internal dynamics within a sector.
    """
    sector: UniverseSector
    energy_scale: float = 1.0
    
    def expectation(self, psi: complex) -> float:
        """Energy expectation in sector."""
        return self.energy_scale * abs(psi) ** 2


@dataclass
class QuadPolarHamiltonian:
    """
    Global Quad-Polar Q-Hamiltonian.
    
    H_quad = H_diag + H_int
    
    where:
    H_diag = H_+ P_+ + H_- P_- + H_i P_i + H_ī P_ī
    H_int = couplings and their adjoints
    """
    h_primal: SectorHamiltonian
    h_inverted: SectorHamiltonian
    h_imaginary: SectorHamiltonian
    h_conjugate: SectorHamiltonian
    coupling_cycle: CouplingCycle
    
    @classmethod
    def default(cls) -> 'QuadPolarHamiltonian':
        """Create default Hamiltonian."""
        return cls(
            SectorHamiltonian(UniverseSector.PRIMAL, 1.0),
            SectorHamiltonian(UniverseSector.INVERTED, 0.5),
            SectorHamiltonian(UniverseSector.IMAGINARY, 0.8),
            SectorHamiltonian(UniverseSector.CONJUGATE, 0.3),
            CouplingCycle()
        )
    
    def total_energy(self, state: QuadPolarState) -> float:
        """Compute total energy H⟨Ψ|Ψ⟩."""
        return (
            self.h_primal.expectation(state.psi_primal) +
            self.h_inverted.expectation(state.psi_inverted) +
            self.h_imaginary.expectation(state.psi_imaginary) +
            self.h_conjugate.expectation(state.psi_conjugate)
        )
    
    def evolve(self, state: QuadPolarState, dt: float = 0.01) -> QuadPolarState:
        """
        Evolve state under Q-Hamiltonian.
        
        Combines diagonal (phase) evolution with coupling dynamics.
        """
        # Diagonal evolution (phase rotation)
        v = state.as_vector.copy()
        phases = np.array([
            self.h_primal.energy_scale,
            self.h_inverted.energy_scale,
            self.h_imaginary.energy_scale,
            self.h_conjugate.energy_scale
        ])
        v *= np.exp(-1j * phases * dt)
        
        intermediate = QuadPolarState(v[0], v[1], v[2], v[3], state.tau)
        
        # Apply coupling interactions
        return self.coupling_cycle.apply_cycle(intermediate, dt)


# ═══════════════════════════════════════════════════════════════════════════════
# ROTATION OPERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SectorRotation:
    """
    90° rotation operator R in sector space.
    
    Implements cyclic permutation of sectors.
    """
    
    def rotate(self, state: QuadPolarState) -> QuadPolarState:
        """
        Apply 90° rotation: + → i → - → ī → +
        """
        return QuadPolarState(
            state.psi_conjugate,  # ī → +
            state.psi_primal,     # + → -
            state.psi_inverted,   # - → i
            state.psi_imaginary,  # i → ī
            state.tau
        )
    
    def rotate_n(self, state: QuadPolarState, n: int) -> QuadPolarState:
        """Apply n 90° rotations."""
        result = state
        for _ in range(n % 4):
            result = self.rotate(result)
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuadPolarPoleBridge:
    """
    Bridge between Quad-Polar Cosmology and four-pole framework.
    """
    
    @staticmethod
    def sector_pole_map() -> Dict[UniverseSector, str]:
        """Map sectors to poles."""
        return {
            UniverseSector.PRIMAL: "D-pole (Discrete/Matter)",
            UniverseSector.IMAGINARY: "C-pole (Continuous/Wave)",
            UniverseSector.INVERTED: "Σ-pole (Stochastic/Void)",
            UniverseSector.CONJUGATE: "Ψ-pole (Hierarchical/Memory)"
        }
    
    @staticmethod
    def sector_chart_map() -> Dict[UniverseSector, str]:
        """Map sectors to charts."""
        return {
            UniverseSector.PRIMAL: "□ Square (Exact/Discrete)",
            UniverseSector.IMAGINARY: "✿ Flower (Transform/Continuous)",
            UniverseSector.INVERTED: "☁ Cloud (Uncertainty/Calibration)",
            UniverseSector.CONJUGATE: "⟂ Fractal (Recursion/Compression)"
        }
    
    @staticmethod
    def integration() -> str:
        return """
        QUAD-POLAR COSMOLOGY ↔ FOUR-POLE FRAMEWORK
        
        Universe Sectors ↔ Poles:
          U_ℝ+ (Primal)    ↔ D-pole (Matter, discrete events)
          U_𝕀+ (Imaginary) ↔ C-pole (Wave, continuous potential)
          U_ℝ- (Inverted)  ↔ Σ-pole (Void, stochastic expansion)
          U_𝕀- (Conjugate) ↔ Ψ-pole (Memory, hierarchical records)
        
        Coupling Cycle ↔ Delta+ Breath:
          C_{i→+} (Collapse)    ↔ Phase 2: EXHALE (Meaning+)
          C_{+→ī} (Logging)     ↔ Phase 3: OXYGEN (Not-Yet+)
          C_{ī→-} (Geometry)    ↔ Phase 0: INHALE+ (Zoom+)
          C_{-→i} (Oscillation) ↔ Phase 1: METABOLIZE (License+)
        
        Quaternionic Encoding:
          |Ψ⟩ ≅ |ψ_+⟩ + i|ψ_i⟩ + j|ψ_-⟩ + k|ψ_ī⟩
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def sector_properties(sector: UniverseSector) -> SectorProperties:
    """Get properties for sector."""
    mapping = {
        UniverseSector.PRIMAL: SectorProperties.primal(),
        UniverseSector.INVERTED: SectorProperties.inverted(),
        UniverseSector.IMAGINARY: SectorProperties.imaginary(),
        UniverseSector.CONJUGATE: SectorProperties.conjugate()
    }
    return mapping[sector]


def quad_polar_state(psi_p: complex = 0.5, psi_inv: complex = 0.5,
                     psi_im: complex = 0.5, psi_conj: complex = 0.5,
                     tau: float = 0.0) -> QuadPolarState:
    """Create quad-polar state."""
    return QuadPolarState(psi_p, psi_inv, psi_im, psi_conj, tau)


def quaternion(a: float, b: float, c: float, d: float) -> Quaternion:
    """Create quaternion."""
    return Quaternion(a, b, c, d)


def coupling_cycle() -> CouplingCycle:
    """Create complete coupling cycle."""
    return CouplingCycle()


def quad_hamiltonian() -> QuadPolarHamiltonian:
    """Create default Q-Hamiltonian."""
    return QuadPolarHamiltonian.default()


def sector_rotation() -> SectorRotation:
    """Create sector rotation operator."""
    return SectorRotation()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'UniverseSector',
    'CouplingType',
    
    # Sector Properties
    'SectorProperties',
    
    # Hilbert Spaces
    'SectorHilbertSpace',
    'TotalHilbertSpace',
    
    # States
    'QuadPolarState',
    'Quaternion',
    
    # Couplings
    'CouplingOperator',
    'CouplingCycle',
    
    # Hamiltonian
    'SectorHamiltonian',
    'QuadPolarHamiltonian',
    
    # Rotation
    'SectorRotation',
    
    # Bridge
    'QuadPolarPoleBridge',
    
    # Functions
    'sector_properties',
    'quad_polar_state',
    'quaternion',
    'coupling_cycle',
    'quad_hamiltonian',
    'sector_rotation',
]

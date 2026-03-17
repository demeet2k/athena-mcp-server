"""
ATHENA OS - Crystal Computing States
====================================
Aetheric States

From CRYSTAL_COMPUTING_FRAMEWORK.docx Chapter 19:

AETHERIC STATE:
    State = (Geom, Field, Kappa, Texture, Meta)
    
    - Geom: underlying geometry (graph, grid, Hilbert block-tree)
    - Field: primary degrees of freedom (amplitudes, tensors)
    - Kappa: κ-related invariants (total, density, budget)
    - Texture: roughness measures at multiple scales
    - Meta: provenance, crystal coordinates, annotations

CRYSTAL COORDINATE:
    χ = (c, s, e, ℓ, p) ∈ C × S × E × L × P
    
    Serves as semantic annotation and dispatch key

SUBSTRATES:
    - Vector space (quantum)
    - Graph (combinatorial)
    - PDE/mesh (continuous)
    - Agent lattice (stochastic)
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
import math
import cmath
from abc import ABC, abstractmethod

from .lattice import CrystalCell, Constant, Shape, Element, Level, Pole
from .kappa import KappaField, Texture, KappaBudget


# =============================================================================
# GEOMETRY TYPES
# =============================================================================

class GeometryType(Enum):
    """Types of underlying geometry."""
    VECTOR = "vector"       # Hilbert space / vector
    GRAPH = "graph"         # Graph / network
    GRID = "grid"           # Regular grid / lattice
    MESH = "mesh"           # Irregular mesh
    TREE = "tree"           # Block-tree (QHC)
    AGENT = "agent"         # Agent lattice


@dataclass
class Geometry:
    """
    Base geometry descriptor.
    """
    
    geo_type: GeometryType
    dimension: int = 0
    
    # Shape tags from crystal
    shape_tag: Shape = Shape.SQUARE
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def compatible_with(self, other: 'Geometry') -> bool:
        """Check if geometries are compatible for operations."""
        return self.geo_type == other.geo_type and self.dimension == other.dimension


@dataclass
class VectorGeometry(Geometry):
    """Hilbert space / vector geometry."""
    
    def __init__(self, dimension: int, **kwargs):
        super().__init__(GeometryType.VECTOR, dimension, **kwargs)
    
    def inner_product_dimension(self) -> int:
        """Dimension for inner product space."""
        return self.dimension


@dataclass
class GraphGeometry(Geometry):
    """Graph / network geometry."""
    
    nodes: int = 0
    edges: int = 0
    
    def __init__(self, nodes: int, edges: int = 0, **kwargs):
        super().__init__(GeometryType.GRAPH, nodes, **kwargs)
        self.nodes = nodes
        self.edges = edges


@dataclass
class GridGeometry(Geometry):
    """Regular grid geometry."""
    
    shape: Tuple[int, ...] = ()
    
    def __init__(self, shape: Tuple[int, ...], **kwargs):
        dim = 1
        for s in shape:
            dim *= s
        super().__init__(GeometryType.GRID, dim, **kwargs)
        self.shape = shape


# =============================================================================
# FIELD DATA
# =============================================================================

@dataclass
class FieldData:
    """
    Primary degrees of freedom storage.
    
    Can represent:
    - Complex amplitudes (quantum)
    - Real values (classical)
    - Tensors (multi-index)
    """
    
    # Dense storage
    values: List[complex] = field(default_factory=list)
    
    # Shape for tensor interpretation
    shape: Tuple[int, ...] = ()
    
    # Basis information
    basis_label: str = "canonical"
    
    @property
    def size(self) -> int:
        """Total number of elements."""
        return len(self.values)
    
    @property
    def norm(self) -> float:
        """L2 norm."""
        return math.sqrt(sum(abs(v)**2 for v in self.values))
    
    def normalize(self) -> None:
        """Normalize to unit norm."""
        n = self.norm
        if n > 0:
            self.values = [v / n for v in self.values]
    
    def inner(self, other: 'FieldData') -> complex:
        """Inner product <self|other>."""
        if len(self.values) != len(other.values):
            raise ValueError("Dimension mismatch")
        return sum(v.conjugate() * w for v, w in zip(self.values, other.values))
    
    @classmethod
    def zero(cls, size: int) -> 'FieldData':
        """Create zero field."""
        return cls(values=[0.0j] * size, shape=(size,))
    
    @classmethod
    def basis(cls, size: int, index: int) -> 'FieldData':
        """Create basis state |index⟩."""
        values = [0.0j] * size
        values[index] = 1.0 + 0.0j
        return cls(values=values, shape=(size,))
    
    @classmethod
    def uniform(cls, size: int) -> 'FieldData':
        """Create uniform superposition."""
        amp = 1.0 / math.sqrt(size)
        return cls(values=[amp + 0.0j] * size, shape=(size,))


# =============================================================================
# AETHERIC STATE
# =============================================================================

@dataclass
class AethericState:
    """
    Complete Aetheric state representation.
    
    State = (Geom, Field, Kappa, Texture, Meta)
    """
    
    # GEOM: Underlying geometry
    geometry: Geometry
    
    # FIELD: Primary degrees of freedom
    field_data: FieldData
    
    # KAPPA: κ-related invariants
    kappa: KappaField = field(default_factory=KappaField)
    kappa_budget: KappaBudget = field(default_factory=KappaBudget)
    
    # TEXTURE: Multi-scale roughness
    texture: Texture = field(default_factory=Texture)
    
    # META: Crystal coordinate and provenance
    crystal_coord: Optional[CrystalCell] = None
    state_id: str = ""
    parent_id: str = ""
    step_index: int = 0
    annotations: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def dimension(self) -> int:
        """State dimension."""
        return self.field_data.size
    
    @property
    def total_kappa(self) -> float:
        """Total κ mass."""
        return self.kappa.total
    
    @property
    def is_normalized(self) -> bool:
        """Check if field is normalized."""
        return abs(self.field_data.norm - 1.0) < 1e-10
    
    def normalize(self) -> None:
        """Normalize field data."""
        self.field_data.normalize()
    
    def update_texture(self, neighbors_map: Optional[Dict[int, List[int]]] = None) -> None:
        """Recompute texture from current κ-field."""
        self.texture = Texture.from_kappa(self.kappa, neighbors_map)
    
    def clone(self) -> 'AethericState':
        """Create deep copy."""
        return AethericState(
            geometry=self.geometry,
            field_data=FieldData(
                values=list(self.field_data.values),
                shape=self.field_data.shape,
                basis_label=self.field_data.basis_label
            ),
            kappa=KappaField(
                values=dict(self.kappa.values),
                total=self.kappa.total
            ),
            kappa_budget=KappaBudget(
                initial=self.kappa_budget.initial,
                remaining=self.kappa_budget.remaining,
                spent=self.kappa_budget.spent
            ),
            texture=Texture(
                alpha=self.texture.alpha,
                beta=self.texture.beta,
                gamma=self.texture.gamma,
                information=self.texture.information,
                geometric=self.texture.geometric,
                spectral=self.texture.spectral
            ),
            crystal_coord=self.crystal_coord,
            state_id=self.state_id,
            parent_id=self.parent_id,
            step_index=self.step_index,
            annotations=dict(self.annotations)
        )
    
    def set_crystal_coord(self, cell: CrystalCell) -> None:
        """Set crystal coordinate."""
        self.crystal_coord = cell
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "dimension": self.dimension,
            "geometry_type": self.geometry.geo_type.value,
            "total_kappa": self.total_kappa,
            "texture": self.texture.total,
            "crystal_coord": self.crystal_coord.index if self.crystal_coord else None,
            "state_id": self.state_id,
            "is_normalized": self.is_normalized
        }
    
    # Factory methods
    @classmethod
    def vacuum(cls, dimension: int) -> 'AethericState':
        """Create vacuum state |0⟩."""
        return cls(
            geometry=VectorGeometry(dimension),
            field_data=FieldData.basis(dimension, 0),
            kappa=KappaField.uniform(list(range(dimension)), total=1.0),
            crystal_coord=CrystalCell(Constant.PI, Shape.SQUARE, Element.EARTH, Level.L0, Pole.AETHER)
        )
    
    @classmethod
    def superposition(cls, dimension: int) -> 'AethericState':
        """Create uniform superposition (1/√n)∑|i⟩."""
        return cls(
            geometry=VectorGeometry(dimension),
            field_data=FieldData.uniform(dimension),
            kappa=KappaField.uniform(list(range(dimension)), total=1.0),
            crystal_coord=CrystalCell(Constant.PI, Shape.FLOWER, Element.AIR, Level.L0, Pole.AETHER)
        )
    
    @classmethod
    def from_amplitudes(cls, amplitudes: List[complex],
                       crystal_coord: Optional[CrystalCell] = None) -> 'AethericState':
        """Create state from amplitude vector."""
        dim = len(amplitudes)
        return cls(
            geometry=VectorGeometry(dim),
            field_data=FieldData(values=amplitudes, shape=(dim,)),
            kappa=KappaField(values={i: abs(a)**2 for i, a in enumerate(amplitudes)}),
            crystal_coord=crystal_coord
        )


# =============================================================================
# STATE ENSEMBLE
# =============================================================================

@dataclass
class StateEnsemble:
    """
    Ensemble of Aetheric states with weights.
    
    ρ = ∑_i w_i |ψ_i⟩⟨ψ_i|
    """
    
    states: List[AethericState] = field(default_factory=list)
    weights: List[float] = field(default_factory=list)
    
    def add(self, state: AethericState, weight: float = 1.0) -> None:
        """Add state to ensemble."""
        self.states.append(state)
        self.weights.append(weight)
    
    @property
    def size(self) -> int:
        """Number of states in ensemble."""
        return len(self.states)
    
    @property
    def total_weight(self) -> float:
        """Sum of weights."""
        return sum(self.weights)
    
    def normalize_weights(self) -> None:
        """Normalize weights to sum to 1."""
        total = self.total_weight
        if total > 0:
            self.weights = [w / total for w in self.weights]
    
    def average_kappa(self) -> float:
        """Weighted average of κ."""
        if not self.states:
            return 0.0
        total_w = self.total_weight
        if total_w <= 0:
            return 0.0
        return sum(w * s.total_kappa for w, s in zip(self.weights, self.states)) / total_w
    
    def sample(self) -> AethericState:
        """Sample a state from ensemble according to weights."""
        import random
        total = self.total_weight
        r = random.random() * total
        cumsum = 0.0
        for w, s in zip(self.weights, self.states):
            cumsum += w
            if r <= cumsum:
                return s
        return self.states[-1] if self.states else None


# =============================================================================
# STATE SPACE
# =============================================================================

@dataclass
class AethericStateSpace:
    """
    Space of Aetheric states with operations.
    """
    
    dimension: int
    geometry: Geometry
    
    # Cached states
    _states: Dict[str, AethericState] = field(default_factory=dict)
    
    def create_state(self, name: str, amplitudes: List[complex]) -> AethericState:
        """Create and register a state."""
        if len(amplitudes) != self.dimension:
            raise ValueError(f"Expected {self.dimension} amplitudes")
        
        state = AethericState.from_amplitudes(amplitudes)
        state.state_id = name
        self._states[name] = state
        return state
    
    def get_state(self, name: str) -> Optional[AethericState]:
        """Get state by name."""
        return self._states.get(name)
    
    def inner_product(self, a: AethericState, b: AethericState) -> complex:
        """Compute ⟨a|b⟩."""
        return a.field_data.inner(b.field_data)
    
    def overlap(self, a: AethericState, b: AethericState) -> float:
        """Compute |⟨a|b⟩|²."""
        return abs(self.inner_product(a, b)) ** 2
    
    def orthogonal(self, a: AethericState, b: AethericState, tol: float = 1e-10) -> bool:
        """Check if states are orthogonal."""
        return abs(self.inner_product(a, b)) < tol


# =============================================================================
# VALIDATION
# =============================================================================

def validate_states() -> bool:
    """Validate states module."""
    
    # Test FieldData
    fd = FieldData.basis(4, 0)
    assert fd.size == 4
    assert abs(fd.norm - 1.0) < 1e-10
    
    fd2 = FieldData.basis(4, 1)
    assert abs(fd.inner(fd2)) < 1e-10  # Orthogonal
    
    fd_uniform = FieldData.uniform(4)
    assert abs(fd_uniform.norm - 1.0) < 1e-10
    
    # Test Geometry
    vg = VectorGeometry(8)
    assert vg.dimension == 8
    
    gg = GraphGeometry(10, 20)
    assert gg.nodes == 10
    
    # Test AethericState
    state = AethericState.vacuum(4)
    assert state.dimension == 4
    assert state.is_normalized
    
    state_sup = AethericState.superposition(4)
    assert state_sup.is_normalized
    
    # Test clone
    clone = state.clone()
    assert clone.dimension == state.dimension
    assert clone.total_kappa == state.total_kappa
    
    # Test StateEnsemble
    ensemble = StateEnsemble()
    ensemble.add(state, 0.5)
    ensemble.add(state_sup, 0.5)
    assert ensemble.size == 2
    assert abs(ensemble.total_weight - 1.0) < 1e-10
    
    # Test StateSpace
    space = AethericStateSpace(dimension=4, geometry=VectorGeometry(4))
    s1 = space.create_state("test", [1+0j, 0j, 0j, 0j])
    assert space.get_state("test") is not None
    
    return True


if __name__ == "__main__":
    print("Validating Crystal Computing States...")
    assert validate_states()
    print("✓ Crystal States validated")
    
    # Demo
    print("\n=== Aetheric States Demo ===")
    
    # Create states
    vacuum = AethericState.vacuum(8)
    print(f"\nVacuum state |0⟩:")
    print(f"  Dimension: {vacuum.dimension}")
    print(f"  Normalized: {vacuum.is_normalized}")
    print(f"  Total κ: {vacuum.total_kappa}")
    if vacuum.crystal_coord:
        print(f"  Crystal coord: {vacuum.crystal_coord.signature}")
    
    superpos = AethericState.superposition(8)
    print(f"\nSuperposition state:")
    print(f"  Dimension: {superpos.dimension}")
    print(f"  Normalized: {superpos.is_normalized}")
    if superpos.crystal_coord:
        print(f"  Crystal coord: {superpos.crystal_coord.signature}")
    
    # State space operations
    space = AethericStateSpace(dimension=8, geometry=VectorGeometry(8))
    overlap = space.overlap(vacuum, superpos)
    print(f"\nOverlap |⟨vacuum|superpos⟩|²: {overlap:.4f}")

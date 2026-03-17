"""
ATHENA OS - HELLENIC: PLATONIC TYPE SYSTEM
==========================================
The Unified Field Theory of Forms

THE FOUR KINDS (PHILEBUS):
    Unlimited (U):  Continuous domain, raw data, Float type
    Limit (L):      Discrete boundaries, ratios, Int type
    Mixture (M):    L applied to U, generated objects, Instance
    Cause (C):      Active agent imposing L on U, Constructor

THE COMPILATION FORMULA:
    M = C(L, U)
    Object = Cause.apply(Limit, Unlimited)

THE RECEPTACLE (CHORA):
    R = {(x,y,z) ∈ ℝ³}
    The dimensional manifold for object instantiation.
    A "nurse of becoming" that receives all imprints.

GEOMETRIC ATOMISM (TIMAEUS):
    Elements composed of regular polyhedra:
    - Fire:   Tetrahedron (4 faces, sharp/penetrating)
    - Air:    Octahedron (8 faces, mobile)
    - Water:  Icosahedron (20 faces, flowing)
    - Earth:  Cube (6 faces, stable)
    
THE OPTIMIZATION FUNCTION:
    The Good = min(d(Entropy)/dt) subject to:
    1. Measure (μ): Proportion, ratio, invariance
    2. Symmetry (Σ): Balance, formal perfection
    3. Truth (T): Correspondence between statement and reality
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Generic, TypeVar, Type
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np


# =============================================================================
# THE FOUR KINDS
# =============================================================================

class PlatonicKind(Enum):
    """The Four Kinds from the Philebus."""
    
    UNLIMITED = "unlimited"  # ἄπειρον - Continuous
    LIMIT = "limit"          # πέρας - Discrete
    MIXTURE = "mixture"      # μεικτόν - Combined
    CAUSE = "cause"          # αἰτία - Active


class Unlimited:
    """
    The Unlimited (ἄπειρον).
    
    Continuous domain. Raw data. Float type.
    Characterized by "more and less" without definite bound.
    """
    
    def __init__(self, domain: Tuple[float, float] = (-np.inf, np.inf),
                 dimension: int = 1):
        self.lower, self.upper = domain
        self.dimension = dimension
        self.continuous = True
    
    def sample(self, n: int = 1) -> np.ndarray:
        """Sample from unlimited continuum."""
        if np.isinf(self.lower) or np.isinf(self.upper):
            # Use standard normal for unbounded
            return np.random.randn(n, self.dimension)
        return np.random.uniform(self.lower, self.upper, (n, self.dimension))
    
    def contains(self, value: float) -> bool:
        """Check if value is in domain."""
        return self.lower <= value <= self.upper
    
    def measure(self) -> float:
        """Return measure (length/volume) of domain."""
        if np.isinf(self.lower) or np.isinf(self.upper):
            return float('inf')
        return (self.upper - self.lower) ** self.dimension


class Limit:
    """
    The Limit (πέρας).
    
    Discrete boundaries. Ratios and measures. Int type.
    Imposes definite structure on the unlimited.
    """
    
    def __init__(self, ratios: List[Tuple[int, int]] = None,
                 boundaries: List[float] = None):
        self.ratios = ratios or [(1, 1)]
        self.boundaries = boundaries or []
    
    def apply_ratio(self, value: float, ratio_idx: int = 0) -> float:
        """Apply ratio to value."""
        if ratio_idx >= len(self.ratios):
            return value
        n, d = self.ratios[ratio_idx]
        return value * n / d
    
    def quantize(self, value: float, levels: int = 10) -> int:
        """Quantize continuous to discrete."""
        return int(value * levels) % levels
    
    def nearest_boundary(self, value: float) -> Optional[float]:
        """Find nearest boundary."""
        if not self.boundaries:
            return None
        distances = [(abs(value - b), b) for b in self.boundaries]
        return min(distances, key=lambda x: x[0])[1]


class Cause:
    """
    The Cause (αἰτία).
    
    Active agent imposing Limit on Unlimited.
    The Constructor that generates Mixtures.
    """
    
    def __init__(self, name: str = "Demiurge"):
        self.name = name
        self._operations: List[Tuple[str, Any]] = []
    
    def add_operation(self, op_name: str, op_func: Any) -> None:
        """Add operation to causal repertoire."""
        self._operations.append((op_name, op_func))
    
    def apply(self, limit: Limit, unlimited: Unlimited) -> 'Mixture':
        """
        Generate Mixture by applying Limit to Unlimited.
        
        M = C(L, U)
        """
        # Sample from unlimited
        raw = unlimited.sample(1)[0]
        
        # Apply limits
        if limit.ratios:
            for i in range(len(raw)):
                raw[i] = limit.apply_ratio(raw[i], i % len(limit.ratios))
        
        # Create mixture
        return Mixture(
            source_unlimited=unlimited,
            applied_limit=limit,
            cause=self,
            value=raw
        )


@dataclass
class Mixture:
    """
    The Mixture (μεικτόν).
    
    Generated object combining Unlimited substrate with Limit structure.
    The instantiated entity.
    """
    
    source_unlimited: Unlimited
    applied_limit: Limit
    cause: Cause
    value: np.ndarray
    
    @property
    def kind(self) -> PlatonicKind:
        return PlatonicKind.MIXTURE
    
    def has_measure(self) -> bool:
        """Check if mixture has definite measure."""
        return not np.any(np.isinf(self.value))
    
    def is_proportionate(self) -> bool:
        """Check if mixture satisfies proportions."""
        # Check if values follow ratio structure
        if len(self.applied_limit.ratios) < 2:
            return True
        
        for i in range(len(self.value) - 1):
            expected_ratio = (self.applied_limit.ratios[i][0] / 
                            self.applied_limit.ratios[i][1])
            actual_ratio = self.value[i] / (self.value[i+1] + 1e-10)
            if abs(expected_ratio - actual_ratio) > 0.1:
                return False
        return True


# =============================================================================
# THE RECEPTACLE
# =============================================================================

class Receptacle:
    """
    The Receptacle (χώρα / ὑποδοχή).
    
    The spatial substrate that receives all imprints.
    "The nurse of becoming" - a formless container.
    
    R = {(x,y,z) ∈ ℝ³}
    """
    
    def __init__(self, dimensions: int = 3,
                 bounds: Tuple[float, float] = (-100, 100)):
        self.dimensions = dimensions
        self.bounds = bounds
        
        # Contents: instances placed in the receptacle
        self._contents: Dict[str, Tuple[np.ndarray, Any]] = {}
    
    def place(self, obj_id: str, position: np.ndarray, 
              content: Any) -> bool:
        """Place object in receptacle at position."""
        if len(position) != self.dimensions:
            return False
        
        # Check bounds
        if not all(self.bounds[0] <= p <= self.bounds[1] for p in position):
            return False
        
        self._contents[obj_id] = (position.copy(), content)
        return True
    
    def get(self, obj_id: str) -> Optional[Tuple[np.ndarray, Any]]:
        """Retrieve object by ID."""
        return self._contents.get(obj_id)
    
    def remove(self, obj_id: str) -> bool:
        """Remove object from receptacle."""
        if obj_id in self._contents:
            del self._contents[obj_id]
            return True
        return False
    
    def nearest(self, position: np.ndarray, 
                n: int = 1) -> List[Tuple[str, float]]:
        """Find n nearest objects to position."""
        distances = []
        for obj_id, (pos, _) in self._contents.items():
            dist = np.linalg.norm(position - pos)
            distances.append((obj_id, dist))
        
        distances.sort(key=lambda x: x[1])
        return distances[:n]
    
    def volume(self) -> float:
        """Return volume of receptacle."""
        extent = self.bounds[1] - self.bounds[0]
        return extent ** self.dimensions
    
    def clear(self) -> None:
        """Clear all contents."""
        self._contents.clear()


# =============================================================================
# GEOMETRIC ATOMISM
# =============================================================================

class PlatonicSolid(Enum):
    """The five Platonic solids."""
    
    TETRAHEDRON = (4, 6, 4, "Fire")      # faces, edges, vertices
    CUBE = (6, 12, 8, "Earth")
    OCTAHEDRON = (8, 12, 6, "Air")
    DODECAHEDRON = (12, 30, 20, "Cosmos")
    ICOSAHEDRON = (20, 30, 12, "Water")
    
    @property
    def faces(self) -> int:
        return self.value[0]
    
    @property
    def edges(self) -> int:
        return self.value[1]
    
    @property
    def vertices(self) -> int:
        return self.value[2]
    
    @property
    def element(self) -> str:
        return self.value[3]
    
    def euler_characteristic(self) -> int:
        """Verify V - E + F = 2."""
        return self.vertices - self.edges + self.faces


@dataclass
class GeometricAtom:
    """
    A Platonic geometric atom.
    
    Elements composed of regular polyhedra:
    - Fire: Tetrahedron (sharp, penetrating)
    - Air: Octahedron (mobile)
    - Water: Icosahedron (flowing)
    - Earth: Cube (stable)
    """
    
    solid: PlatonicSolid
    scale: float = 1.0
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.eye(3))
    
    @property
    def element(self) -> str:
        return self.solid.element
    
    @property
    def volume(self) -> float:
        """Compute volume of solid at given scale."""
        a = self.scale  # Edge length
        
        if self.solid == PlatonicSolid.TETRAHEDRON:
            return (a ** 3) / (6 * np.sqrt(2))
        
        elif self.solid == PlatonicSolid.CUBE:
            return a ** 3
        
        elif self.solid == PlatonicSolid.OCTAHEDRON:
            return (np.sqrt(2) / 3) * a ** 3
        
        elif self.solid == PlatonicSolid.DODECAHEDRON:
            phi = (1 + np.sqrt(5)) / 2  # Golden ratio
            return ((15 + 7 * np.sqrt(5)) / 4) * a ** 3
        
        elif self.solid == PlatonicSolid.ICOSAHEDRON:
            phi = (1 + np.sqrt(5)) / 2
            return (5 * (3 + np.sqrt(5)) / 12) * a ** 3
        
        return 0.0
    
    @property
    def surface_area(self) -> float:
        """Compute surface area at given scale."""
        a = self.scale
        
        if self.solid == PlatonicSolid.TETRAHEDRON:
            return np.sqrt(3) * a ** 2
        
        elif self.solid == PlatonicSolid.CUBE:
            return 6 * a ** 2
        
        elif self.solid == PlatonicSolid.OCTAHEDRON:
            return 2 * np.sqrt(3) * a ** 2
        
        elif self.solid == PlatonicSolid.DODECAHEDRON:
            return 3 * np.sqrt(25 + 10 * np.sqrt(5)) * a ** 2
        
        elif self.solid == PlatonicSolid.ICOSAHEDRON:
            return 5 * np.sqrt(3) * a ** 2
        
        return 0.0
    
    def stability(self) -> float:
        """
        Compute stability measure.
        
        Earth (cube) is most stable, Fire (tetrahedron) least.
        """
        # More faces = more stable
        return self.solid.faces / 20.0  # Normalize to [0.2, 1.0]


class GeometricAtomism:
    """
    The Platonic theory of elemental composition.
    
    Transmutation rules:
    - Fire (4 triangles) + Air (8 triangles) → Water (20 triangles)?
    - Actually based on common triangular faces
    """
    
    # Base triangle types
    ISOCELES_RIGHT = "isoceles_right"  # For cube
    EQUILATERAL = "equilateral"        # For others
    
    @classmethod
    def decompose(cls, atom: GeometricAtom) -> Dict[str, int]:
        """
        Decompose solid into constituent triangles.
        
        All Platonic solids (except cube) decompose into
        equilateral triangular faces.
        """
        solid = atom.solid
        
        if solid == PlatonicSolid.CUBE:
            # 6 square faces → 12 isoceles right triangles
            return {cls.ISOCELES_RIGHT: 12}
        
        elif solid == PlatonicSolid.TETRAHEDRON:
            # 4 equilateral faces → 4 * 1 = 4 triangles
            # (or 4 * 6 = 24 scalene per Timaeus)
            return {cls.EQUILATERAL: 4}
        
        elif solid == PlatonicSolid.OCTAHEDRON:
            return {cls.EQUILATERAL: 8}
        
        elif solid == PlatonicSolid.ICOSAHEDRON:
            return {cls.EQUILATERAL: 20}
        
        elif solid == PlatonicSolid.DODECAHEDRON:
            # 12 pentagonal faces - special case
            return {"pentagon": 12}
        
        return {}
    
    @classmethod
    def can_transmute(cls, from_atom: GeometricAtom, 
                      to_solid: PlatonicSolid) -> bool:
        """
        Check if transmutation is possible.
        
        Fire, Air, Water can transmute (share equilateral base).
        Earth cannot transmute with others (isoceles base).
        """
        from_solid = from_atom.solid
        
        # Earth is fixed
        if from_solid == PlatonicSolid.CUBE:
            return to_solid == PlatonicSolid.CUBE
        
        if to_solid == PlatonicSolid.CUBE:
            return False
        
        # Fire, Air, Water share equilateral base
        transmutable = {
            PlatonicSolid.TETRAHEDRON,
            PlatonicSolid.OCTAHEDRON,
            PlatonicSolid.ICOSAHEDRON
        }
        
        return from_solid in transmutable and to_solid in transmutable


# =============================================================================
# THE OPTIMIZATION FUNCTION (THE GOOD)
# =============================================================================

@dataclass
class GoodMetrics:
    """
    Metrics for evaluating "The Good" (τὸ ἀγαθόν).
    
    The Good = min(d(Entropy)/dt) subject to:
    1. Measure (μ): Proportion, mathematical invariance
    2. Symmetry (Σ): Balance, formal perfection
    3. Truth (T): Correspondence with reality
    """
    
    measure: float = 0.0      # μ - Proportion quality
    symmetry: float = 0.0     # Σ - Balance quality
    truth: float = 0.0        # T - Correspondence quality
    pleasure: float = 0.0     # Pure pleasure (positive only)
    
    @property
    def total(self) -> float:
        """Combined goodness score."""
        # Weighted sum (Philebus ordering)
        return (5 * self.measure + 
                4 * self.symmetry + 
                3 * self.truth + 
                1 * self.pleasure)
    
    def normalized(self) -> 'GoodMetrics':
        """Return normalized metrics [0, 1]."""
        total = self.measure + self.symmetry + self.truth + self.pleasure
        if total == 0:
            return GoodMetrics()
        return GoodMetrics(
            measure=self.measure / total,
            symmetry=self.symmetry / total,
            truth=self.truth / total,
            pleasure=self.pleasure / total
        )


class GoodOptimizer:
    """
    Optimizer for The Good.
    
    Seeks to minimize entropy change while maximizing
    measure, symmetry, and truth.
    """
    
    def __init__(self):
        self.history: List[GoodMetrics] = []
    
    def evaluate(self, mixture: Mixture) -> GoodMetrics:
        """Evaluate goodness of a mixture."""
        metrics = GoodMetrics()
        
        # Measure: Check for proportion
        if mixture.is_proportionate():
            metrics.measure = 1.0
        else:
            # Partial credit based on how close
            metrics.measure = 0.5
        
        # Symmetry: Check for balance
        if mixture.has_measure():
            values = mixture.value
            mean = np.mean(values)
            variance = np.var(values)
            # Low variance = high symmetry
            metrics.symmetry = 1.0 / (1.0 + variance)
        
        # Truth: Correspondence with cause's intention
        # (Simplified: check if within bounds)
        if mixture.source_unlimited.contains(np.mean(mixture.value)):
            metrics.truth = 1.0
        else:
            metrics.truth = 0.5
        
        # Pleasure: Positive feedback
        metrics.pleasure = 0.5  # Neutral baseline
        
        self.history.append(metrics)
        return metrics
    
    def best_so_far(self) -> Optional[GoodMetrics]:
        """Return best metrics achieved."""
        if not self.history:
            return None
        return max(self.history, key=lambda m: m.total)
    
    def entropy_gradient(self) -> float:
        """Estimate d(Entropy)/dt from history."""
        if len(self.history) < 2:
            return 0.0
        
        # Use total scores as proxy for negative entropy
        recent = [m.total for m in self.history[-10:]]
        return np.mean(np.diff(recent))


# =============================================================================
# VALIDATION
# =============================================================================

def validate_platonic() -> bool:
    """Validate Platonic type system module."""
    
    # Test Unlimited
    unlimited = Unlimited(domain=(-1, 1), dimension=2)
    
    samples = unlimited.sample(100)
    assert samples.shape == (100, 2)
    assert unlimited.contains(0.5)
    assert not unlimited.contains(2.0)
    
    # Test Limit
    limit = Limit(ratios=[(3, 2), (4, 3)], boundaries=[0, 0.5, 1.0])
    
    assert limit.apply_ratio(2.0, 0) == 3.0
    assert limit.quantize(0.35, 10) == 3
    assert limit.nearest_boundary(0.6) == 0.5
    
    # Test Cause and Mixture
    cause = Cause("TestCause")
    mixture = cause.apply(limit, unlimited)
    
    assert mixture.kind == PlatonicKind.MIXTURE
    assert mixture.cause == cause
    
    # Test Receptacle
    receptacle = Receptacle(dimensions=3)
    
    pos = np.array([10.0, 20.0, 30.0])
    assert receptacle.place("obj1", pos, "content1")
    
    retrieved = receptacle.get("obj1")
    assert retrieved is not None
    assert np.array_equal(retrieved[0], pos)
    
    assert receptacle.remove("obj1")
    assert receptacle.get("obj1") is None
    
    # Test PlatonicSolid
    for solid in PlatonicSolid:
        assert solid.euler_characteristic() == 2
    
    # Test GeometricAtom
    fire_atom = GeometricAtom(PlatonicSolid.TETRAHEDRON, scale=1.0)
    earth_atom = GeometricAtom(PlatonicSolid.CUBE, scale=1.0)
    
    assert fire_atom.element == "Fire"
    assert earth_atom.element == "Earth"
    
    assert fire_atom.volume > 0
    assert earth_atom.volume > 0
    
    assert fire_atom.stability() < earth_atom.stability()
    
    # Test GeometricAtomism
    assert GeometricAtomism.can_transmute(fire_atom, PlatonicSolid.OCTAHEDRON)
    assert not GeometricAtomism.can_transmute(earth_atom, PlatonicSolid.TETRAHEDRON)
    
    # Test GoodMetrics
    metrics = GoodMetrics(measure=1.0, symmetry=0.8, truth=0.9, pleasure=0.5)
    
    assert metrics.total > 0
    
    normalized = metrics.normalized()
    assert abs(normalized.measure + normalized.symmetry + 
               normalized.truth + normalized.pleasure - 1.0) < 0.01
    
    # Test GoodOptimizer
    optimizer = GoodOptimizer()
    
    for _ in range(5):
        m = cause.apply(limit, unlimited)
        optimizer.evaluate(m)
    
    assert len(optimizer.history) == 5
    assert optimizer.best_so_far() is not None
    
    return True


if __name__ == "__main__":
    print("Validating Platonic Type System...")
    assert validate_platonic()
    print("✓ Platonic Type System validated")
    
    print("\n--- Platonic Solids ---")
    for solid in PlatonicSolid:
        print(f"  {solid.name}: F={solid.faces}, E={solid.edges}, "
              f"V={solid.vertices}, Element={solid.element}")
    
    print("\n--- Four Kinds Demo ---")
    unlimited = Unlimited((-10, 10), dimension=3)
    limit = Limit([(2, 1), (3, 2), (4, 3)])
    cause = Cause("Demiurge")
    
    mixture = cause.apply(limit, unlimited)
    print(f"  Unlimited domain: {unlimited.lower} to {unlimited.upper}")
    print(f"  Limit ratios: {limit.ratios}")
    print(f"  Cause: {cause.name}")
    print(f"  Mixture value: {mixture.value}")

"""
ATHENA OS - Crystal Computing Kappa
===================================
κ-Fields and Conservation

From CRYSTAL_COMPUTING_FRAMEWORK.docx Chapter 2:

κ AS CONSERVED QUANTITY:
    κ: ℳ → ℝ≥0
    
    κ measures coherence, capacity, or computational value
    
    Interpretations:
    - Thermodynamic: free energy, negentropy
    - Information-theoretic: capacity, mutual information
    - Resource: computational budget, attention
    - Coherence: quantum coherence, phase correlation

κ-CONSERVATION:
    Aetheric operators preserve total κ:
    ∫ κ(x) ρ(x) dμ(x) = constant
    
    d/dt K(ρ_t) = 0 for Aetheric flows

TEXTURE:
    Multi-scale roughness measures
    T(ψ) = α·H + β·D + γ·λ
    - H: Information texture (entropy)
    - D: Geometric texture (curvature)
    - λ: Spectral texture (mixing)
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math

from .lattice import CrystalCell, Pole


# =============================================================================
# κ-FIELD
# =============================================================================

@dataclass
class KappaField:
    """
    A κ-field on a discrete or continuous configuration space.
    
    κ: ℳ → ℝ≥0 assigns coherence/capacity to each point.
    """
    
    # Discrete representation: index → κ value
    values: Dict[int, float] = field(default_factory=dict)
    
    # Normalization
    total: float = 0.0
    
    # Field metadata
    dimension: int = 0
    reference_measure: float = 1.0
    
    def __post_init__(self):
        """Recompute total on init."""
        self.total = sum(self.values.values())
        self.dimension = len(self.values)
    
    def get(self, index: int) -> float:
        """Get κ value at index."""
        return self.values.get(index, 0.0)
    
    def set(self, index: int, value: float) -> None:
        """Set κ value at index."""
        if value < 0:
            raise ValueError("κ must be non-negative")
        
        old = self.values.get(index, 0.0)
        self.values[index] = value
        self.total += (value - old)
        self.dimension = len(self.values)
    
    def add(self, index: int, delta: float) -> None:
        """Add to κ value at index."""
        current = self.get(index)
        self.set(index, max(0.0, current + delta))
    
    def density(self, index: int) -> float:
        """Get κ density (normalized by total)."""
        if self.total <= 0:
            return 0.0
        return self.get(index) / self.total
    
    def gradient(self, index: int, neighbors: List[int]) -> float:
        """Compute κ gradient at index."""
        if not neighbors:
            return 0.0
        
        center = self.get(index)
        neighbor_avg = sum(self.get(n) for n in neighbors) / len(neighbors)
        return center - neighbor_avg
    
    def normalize(self, target: float = 1.0) -> None:
        """Normalize field to target total."""
        if self.total <= 0:
            return
        
        factor = target / self.total
        for index in self.values:
            self.values[index] *= factor
        self.total = target
    
    @classmethod
    def uniform(cls, indices: List[int], total: float = 1.0) -> 'KappaField':
        """Create uniform κ-field."""
        if not indices:
            return cls()
        
        value = total / len(indices)
        return cls(values={i: value for i in indices}, total=total)
    
    @classmethod
    def from_density(cls, density: Dict[int, float], total: float = 1.0) -> 'KappaField':
        """Create κ-field from density (sums to 1)."""
        norm = sum(density.values())
        if norm <= 0:
            return cls()
        
        return cls(values={i: total * d / norm for i, d in density.items()})


# =============================================================================
# κ-MASS AND METRICS
# =============================================================================

@dataclass
class KappaMass:
    """
    κ-mass functional K(ρ) = ∫ κ(x) ρ(x) dμ(x).
    """
    
    kappa_field: KappaField
    
    def compute(self, density: Dict[int, float]) -> float:
        """Compute κ-mass for a given density."""
        mass = 0.0
        for index, rho in density.items():
            mass += self.kappa_field.get(index) * rho
        return mass
    
    def is_conserved(self, density_before: Dict[int, float],
                     density_after: Dict[int, float],
                     tolerance: float = 1e-6) -> bool:
        """Check if κ-mass is conserved between two densities."""
        mass_before = self.compute(density_before)
        mass_after = self.compute(density_after)
        return abs(mass_before - mass_after) < tolerance


@dataclass
class KappaMetrics:
    """
    Various κ-based metrics and diagnostics.
    """
    
    @staticmethod
    def entropy(field: KappaField) -> float:
        """Compute κ-entropy: -∑ p log p where p = κ/total."""
        if field.total <= 0:
            return 0.0
        
        entropy = 0.0
        for value in field.values.values():
            if value > 0:
                p = value / field.total
                entropy -= p * math.log(p)
        return entropy
    
    @staticmethod
    def concentration(field: KappaField) -> float:
        """Compute κ-concentration (inverse participation ratio)."""
        if field.total <= 0:
            return 0.0
        
        sum_sq = sum(v**2 for v in field.values.values())
        return sum_sq / (field.total ** 2)
    
    @staticmethod
    def variance(field: KappaField) -> float:
        """Compute κ-variance."""
        if field.dimension <= 0:
            return 0.0
        
        mean = field.total / field.dimension
        variance = sum((v - mean)**2 for v in field.values.values())
        return variance / field.dimension
    
    @staticmethod
    def max_flow(field: KappaField, neighbors_map: Dict[int, List[int]]) -> float:
        """Estimate maximum κ-flow (largest gradient)."""
        max_grad = 0.0
        for index in field.values:
            neighbors = neighbors_map.get(index, [])
            grad = abs(field.gradient(index, neighbors))
            max_grad = max(max_grad, grad)
        return max_grad


# =============================================================================
# TEXTURE
# =============================================================================

@dataclass
class Texture:
    """
    Multi-scale texture measure.
    
    T(ψ) = α·H + β·D + γ·λ
    - H: Information texture (entropy)
    - D: Geometric texture (curvature/gradient)
    - λ: Spectral texture (mixing rate)
    """
    
    # Texture weights
    alpha: float = 1.0  # Information weight
    beta: float = 1.0   # Geometric weight
    gamma: float = 1.0  # Spectral weight
    
    # Computed components
    information: float = 0.0   # H
    geometric: float = 0.0     # D
    spectral: float = 0.0      # λ
    
    @property
    def total(self) -> float:
        """Total texture T."""
        return (
            self.alpha * self.information +
            self.beta * self.geometric +
            self.gamma * self.spectral
        )
    
    @classmethod
    def from_kappa(cls, field: KappaField,
                  neighbors_map: Optional[Dict[int, List[int]]] = None,
                  alpha: float = 1.0, beta: float = 1.0, gamma: float = 1.0) -> 'Texture':
        """Compute texture from κ-field."""
        texture = cls(alpha=alpha, beta=beta, gamma=gamma)
        
        # Information texture (entropy)
        texture.information = KappaMetrics.entropy(field)
        
        # Geometric texture (gradient energy)
        if neighbors_map:
            grad_energy = 0.0
            for index in field.values:
                neighbors = neighbors_map.get(index, [])
                grad = field.gradient(index, neighbors)
                grad_energy += grad ** 2
            texture.geometric = math.sqrt(grad_energy / max(1, len(field.values)))
        
        # Spectral texture (concentration)
        texture.spectral = KappaMetrics.concentration(field)
        
        return texture
    
    def is_within_budget(self, budget: float) -> bool:
        """Check if texture is within budget."""
        return self.total <= budget


# =============================================================================
# κ-CONSERVATION
# =============================================================================

class ConservationType(Enum):
    """Types of κ-conservation."""
    EXACT = "exact"           # K(ρ_t) = K(ρ_0) exactly
    BOUNDED = "bounded"       # |K(ρ_t) - K(ρ_0)| ≤ ε
    MONOTONE = "monotone"     # K(ρ_t) ≤ K(ρ_0)
    DISSIPATIVE = "dissipative"  # K decreases


@dataclass
class ConservationLaw:
    """
    κ-conservation law for operators.
    
    Aetheric operators must satisfy:
    ∫ κ(x) (Lρ)(x) dμ(x) = 0
    """
    
    conservation_type: ConservationType = ConservationType.EXACT
    tolerance: float = 1e-6
    
    # History for tracking
    history: List[float] = field(default_factory=list)
    
    def check(self, kappa_before: float, kappa_after: float) -> bool:
        """Check if conservation is satisfied."""
        delta = kappa_after - kappa_before
        
        if self.conservation_type == ConservationType.EXACT:
            return abs(delta) <= self.tolerance
        
        elif self.conservation_type == ConservationType.BOUNDED:
            return abs(delta) <= self.tolerance
        
        elif self.conservation_type == ConservationType.MONOTONE:
            return delta <= self.tolerance
        
        elif self.conservation_type == ConservationType.DISSIPATIVE:
            return delta <= 0
        
        return False
    
    def record(self, kappa_value: float) -> None:
        """Record κ value in history."""
        self.history.append(kappa_value)
    
    def verify_history(self) -> Tuple[bool, float]:
        """Verify conservation across history."""
        if len(self.history) < 2:
            return True, 0.0
        
        max_deviation = 0.0
        initial = self.history[0]
        
        for k in self.history[1:]:
            deviation = abs(k - initial)
            max_deviation = max(max_deviation, deviation)
        
        is_conserved = max_deviation <= self.tolerance
        return is_conserved, max_deviation


# =============================================================================
# κ-BUDGET
# =============================================================================

@dataclass
class KappaBudget:
    """
    κ-budget for computational processes.
    
    Tracks and limits κ expenditure.
    """
    
    initial: float = 100.0
    remaining: float = 100.0
    spent: float = 0.0
    
    # Limits
    max_per_operation: float = 10.0
    min_reserve: float = 10.0
    
    def can_spend(self, amount: float) -> bool:
        """Check if amount can be spent."""
        if amount > self.max_per_operation:
            return False
        if self.remaining - amount < self.min_reserve:
            return False
        return True
    
    def spend(self, amount: float) -> bool:
        """Spend κ from budget."""
        if not self.can_spend(amount):
            return False
        
        self.remaining -= amount
        self.spent += amount
        return True
    
    def refund(self, amount: float) -> None:
        """Refund κ to budget."""
        self.remaining += amount
        self.spent -= amount
        self.spent = max(0.0, self.spent)
    
    @property
    def utilization(self) -> float:
        """Budget utilization fraction."""
        if self.initial <= 0:
            return 1.0
        return self.spent / self.initial


# =============================================================================
# κ-FLOW
# =============================================================================

@dataclass
class KappaFlow:
    """
    κ-flow between crystal cells.
    
    Tracks how κ moves through the crystal lattice.
    """
    
    source: CrystalCell
    target: CrystalCell
    amount: float
    
    # Flow type
    is_conserving: bool = True
    loss: float = 0.0
    
    @property
    def net_transfer(self) -> float:
        """Net κ transferred (after loss)."""
        return self.amount - self.loss
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source.index,
            "target": self.target.index,
            "amount": self.amount,
            "conserving": self.is_conserving,
            "loss": self.loss
        }


@dataclass
class KappaFlowGraph:
    """
    Graph of κ-flows through the crystal.
    """
    
    flows: List[KappaFlow] = field(default_factory=list)
    
    # Per-cell accounting
    inflow: Dict[int, float] = field(default_factory=dict)
    outflow: Dict[int, float] = field(default_factory=dict)
    
    def add_flow(self, flow: KappaFlow) -> None:
        """Add a flow to the graph."""
        self.flows.append(flow)
        
        source_idx = flow.source.index
        target_idx = flow.target.index
        
        self.outflow[source_idx] = self.outflow.get(source_idx, 0.0) + flow.amount
        self.inflow[target_idx] = self.inflow.get(target_idx, 0.0) + flow.net_transfer
    
    def net_flow(self, cell_index: int) -> float:
        """Net κ flow for a cell (in - out)."""
        return self.inflow.get(cell_index, 0.0) - self.outflow.get(cell_index, 0.0)
    
    def total_flow(self) -> float:
        """Total κ flow through graph."""
        return sum(f.amount for f in self.flows)
    
    def total_loss(self) -> float:
        """Total κ loss in flows."""
        return sum(f.loss for f in self.flows)
    
    def is_conserving(self, tolerance: float = 1e-6) -> bool:
        """Check if graph represents κ-conserving dynamics."""
        return self.total_loss() < tolerance


# =============================================================================
# VALIDATION
# =============================================================================

def validate_kappa() -> bool:
    """Validate κ module."""
    
    # Test KappaField
    field = KappaField.uniform([0, 1, 2, 3], total=1.0)
    assert abs(field.total - 1.0) < 1e-10
    assert field.dimension == 4
    assert abs(field.get(0) - 0.25) < 1e-10
    
    field.set(0, 0.5)
    assert abs(field.total - 1.25) < 1e-10
    
    # Test density
    assert abs(field.density(0) - 0.5/1.25) < 1e-10
    
    # Test KappaMass
    kappa = KappaField(values={0: 1.0, 1: 2.0, 2: 3.0})
    mass = KappaMass(kappa)
    
    density = {0: 0.5, 1: 0.3, 2: 0.2}
    computed = mass.compute(density)
    expected = 1.0*0.5 + 2.0*0.3 + 3.0*0.2  # 0.5 + 0.6 + 0.6 = 1.7
    assert abs(computed - expected) < 1e-10
    
    # Test Texture
    texture = Texture.from_kappa(field)
    assert texture.information >= 0
    assert texture.total >= 0
    
    # Test Conservation
    law = ConservationLaw(tolerance=0.01)
    assert law.check(1.0, 1.005)
    assert not law.check(1.0, 1.1)
    
    # Test KappaBudget
    budget = KappaBudget(initial=100.0, remaining=100.0)
    assert budget.can_spend(5.0)
    assert budget.spend(5.0)
    assert abs(budget.remaining - 95.0) < 1e-10
    
    # Test KappaFlow
    from .lattice import CrystalCell, Constant, Shape, Element, Level, Pole
    
    cell1 = CrystalCell(Constant.PI, Shape.SQUARE, Element.EARTH, Level.L0, Pole.AETHER)
    cell2 = CrystalCell(Constant.E, Shape.SQUARE, Element.EARTH, Level.L0, Pole.AETHER)
    
    flow = KappaFlow(source=cell1, target=cell2, amount=1.0)
    assert flow.net_transfer == 1.0
    
    graph = KappaFlowGraph()
    graph.add_flow(flow)
    assert graph.total_flow() == 1.0
    assert graph.is_conserving()
    
    return True


if __name__ == "__main__":
    print("Validating Crystal Computing Kappa...")
    assert validate_kappa()
    print("✓ Crystal Kappa validated")
    
    # Demo
    print("\n=== κ-Fields and Conservation Demo ===")
    
    # Create κ-field
    field = KappaField.uniform(list(range(16)), total=10.0)
    print(f"\nUniform κ-field:")
    print(f"  Dimension: {field.dimension}")
    print(f"  Total κ: {field.total}")
    
    # Compute texture
    texture = Texture.from_kappa(field)
    print(f"\nTexture T = α·H + β·D + γ·λ:")
    print(f"  H (Information): {texture.information:.4f}")
    print(f"  D (Geometric): {texture.geometric:.4f}")
    print(f"  λ (Spectral): {texture.spectral:.4f}")
    print(f"  Total: {texture.total:.4f}")
    
    # Conservation check
    law = ConservationLaw()
    law.record(10.0)
    law.record(10.0001)
    law.record(9.9999)
    
    is_conserved, deviation = law.verify_history()
    print(f"\nConservation check:")
    print(f"  Conserved: {is_conserved}")
    print(f"  Max deviation: {deviation:.6f}")

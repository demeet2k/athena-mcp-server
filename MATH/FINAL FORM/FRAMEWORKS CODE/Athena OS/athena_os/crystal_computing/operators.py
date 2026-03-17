"""
ATHENA OS - Crystal Computing Operators
=======================================
Crystal Cell Operators

From CRYSTAL_COMPUTING_FRAMEWORK.docx:

OPERATOR REPRESENTATION:
    Op = (Cell, Kernel, KappaSpec, CostModel, Meta)
    
    - Cell: crystal coordinates (c, s, e, l, p)
    - Kernel: substrate-specific implementation
    - KappaSpec: κ behavior (preserve/dissipate)
    - CostModel: time, memory, κ-complexity
    - Meta: versioning, provenance

CANONICAL OPERATIONS BY AXIS:
    Constant:
        π - rotation, spectral kernels
        e - semigroup, growth operators
        i - unitary, phase evolution
        φ - quasi-crystalline, self-similar
    
    Shape:
        Square - piecewise-linear, grid, algebraic
        Flower - wave, Fourier, oscillatory
        Cloud - probabilistic, stochastic
        Fractal - self-similar, multiscale
    
    Element:
        Earth - discrete, combinatorial
        Water - continuous, PDE
        Air - information-theoretic
        Fire - dynamical, chaotic
    
    Level:
        L0 - local primitive
        L1 - structural invariant
        L2 - inter-regime bridge
        L3 - spectral limit
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math
import cmath
from abc import ABC, abstractmethod

from .lattice import CrystalCell, Constant, Shape, Element, Level, Pole
from .kappa import KappaField, ConservationType
from .states import AethericState, FieldData


# =============================================================================
# κ SPECIFICATION
# =============================================================================

class KappaBehavior(Enum):
    """How an operator affects κ."""
    PRESERVE = "preserve"       # Δκ = 0
    DISSIPATE = "dissipate"     # Δκ < 0
    AMPLIFY = "amplify"         # Δκ > 0 (only Inner-Shadow)
    TRANSFER = "transfer"       # Redistributes κ


@dataclass
class KappaSpec:
    """
    κ-behavior specification for an operator.
    """
    
    behavior: KappaBehavior = KappaBehavior.PRESERVE
    max_loss: float = 0.0        # Maximum κ loss per application
    expected_loss: float = 0.0   # Expected κ loss
    flux_pattern: str = "uniform"  # How κ flows
    
    def is_conserving(self) -> bool:
        """Check if operator is κ-conserving."""
        return self.behavior == KappaBehavior.PRESERVE and self.max_loss == 0.0


# =============================================================================
# COST MODEL
# =============================================================================

@dataclass
class CostModel:
    """
    Cost model for an operator.
    """
    
    # Asymptotic complexity
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    
    # κ-complexity
    kappa_cost: float = 0.0
    texture_cost: float = 0.0
    
    # Empirical measurements
    measured_time: Optional[float] = None
    measured_memory: Optional[int] = None
    
    def total_cost(self, size: int = 1) -> float:
        """Estimate total cost."""
        return self.kappa_cost + self.texture_cost


# =============================================================================
# ABSTRACT CRYSTAL OPERATOR
# =============================================================================

class CrystalOperator(ABC):
    """
    Abstract base class for crystal operators.
    
    Each operator is associated with a crystal cell and implements
    κ-specified behavior on Aetheric states.
    """
    
    def __init__(self, cell: CrystalCell,
                 kappa_spec: Optional[KappaSpec] = None,
                 cost_model: Optional[CostModel] = None):
        self.cell = cell
        self.kappa_spec = kappa_spec or KappaSpec()
        self.cost_model = cost_model or CostModel()
        self.name = f"Op[{cell.signature}]"
    
    @abstractmethod
    def apply(self, state: AethericState) -> AethericState:
        """Apply operator to state."""
        pass
    
    def is_legal(self) -> bool:
        """Check if operator is in legal (Aether) pole."""
        return self.cell.pole.is_legal
    
    def is_conserving(self) -> bool:
        """Check if operator conserves κ."""
        return self.kappa_spec.is_conserving()
    
    def validate_application(self, state: AethericState) -> bool:
        """Validate that operator can be applied to state."""
        # Check κ budget
        if not state.kappa_budget.can_spend(self.cost_model.kappa_cost):
            return False
        return True
    
    def compose(self, other: 'CrystalOperator') -> 'ComposedOperator':
        """Compose with another operator."""
        return ComposedOperator([self, other])
    
    def __repr__(self) -> str:
        return f"{self.name}"


# =============================================================================
# PRIMITIVE OPERATORS
# =============================================================================

class IdentityOperator(CrystalOperator):
    """Identity operator I."""
    
    def __init__(self, cell: Optional[CrystalCell] = None):
        if cell is None:
            cell = CrystalCell(Constant.PI, Shape.SQUARE, Element.EARTH, Level.L0, Pole.AETHER)
        super().__init__(cell, KappaSpec(behavior=KappaBehavior.PRESERVE))
        self.name = "I"
    
    def apply(self, state: AethericState) -> AethericState:
        return state.clone()


class PhaseOperator(CrystalOperator):
    """Phase rotation e^{iθ}."""
    
    def __init__(self, theta: float, cell: Optional[CrystalCell] = None):
        if cell is None:
            cell = CrystalCell(Constant.I, Shape.FLOWER, Element.AIR, Level.L0, Pole.AETHER)
        super().__init__(cell, KappaSpec(behavior=KappaBehavior.PRESERVE))
        self.theta = theta
        self.name = f"Phase({theta:.3f})"
    
    def apply(self, state: AethericState) -> AethericState:
        result = state.clone()
        phase = cmath.exp(1j * self.theta)
        result.field_data.values = [v * phase for v in result.field_data.values]
        return result


class ScaleOperator(CrystalOperator):
    """Scale operator (φ-based)."""
    
    def __init__(self, factor: float, cell: Optional[CrystalCell] = None):
        if cell is None:
            cell = CrystalCell(Constant.PHI, Shape.FRACTAL, Element.WATER, Level.L0, Pole.AETHER)
        super().__init__(cell, KappaSpec(behavior=KappaBehavior.TRANSFER))
        self.factor = factor
        self.name = f"Scale({factor:.3f})"
    
    def apply(self, state: AethericState) -> AethericState:
        result = state.clone()
        result.field_data.values = [v * self.factor for v in result.field_data.values]
        # Renormalize
        result.normalize()
        return result


class ExponentialOperator(CrystalOperator):
    """Exponential/growth operator (e-based)."""
    
    def __init__(self, rate: float, cell: Optional[CrystalCell] = None):
        if cell is None:
            cell = CrystalCell(Constant.E, Shape.FLOWER, Element.FIRE, Level.L0, Pole.AETHER)
        super().__init__(cell, KappaSpec(behavior=KappaBehavior.TRANSFER))
        self.rate = rate
        self.name = f"Exp({rate:.3f})"
    
    def apply(self, state: AethericState) -> AethericState:
        result = state.clone()
        factor = math.exp(self.rate)
        result.field_data.values = [v * factor for v in result.field_data.values]
        result.normalize()
        return result


class HadamardOperator(CrystalOperator):
    """Hadamard gate (superposition creator)."""
    
    def __init__(self, qubit: int = 0, cell: Optional[CrystalCell] = None):
        if cell is None:
            cell = CrystalCell(Constant.PI, Shape.FLOWER, Element.AIR, Level.L0, Pole.AETHER)
        super().__init__(cell, KappaSpec(behavior=KappaBehavior.PRESERVE))
        self.qubit = qubit
        self.name = f"H({qubit})"
    
    def apply(self, state: AethericState) -> AethericState:
        result = state.clone()
        dim = result.dimension
        
        if dim == 2:
            # Single qubit Hadamard
            a, b = result.field_data.values[0], result.field_data.values[1]
            sqrt2 = math.sqrt(2)
            result.field_data.values[0] = (a + b) / sqrt2
            result.field_data.values[1] = (a - b) / sqrt2
        else:
            # Multi-qubit: apply to specified qubit
            # Simplified: just apply mixing
            new_values = list(result.field_data.values)
            step = 2 ** self.qubit
            for i in range(0, dim, 2 * step):
                for j in range(step):
                    if i + j < dim and i + j + step < dim:
                        a = new_values[i + j]
                        b = new_values[i + j + step]
                        sqrt2 = math.sqrt(2)
                        new_values[i + j] = (a + b) / sqrt2
                        new_values[i + j + step] = (a - b) / sqrt2
            result.field_data.values = new_values
        
        return result


class ProjectionOperator(CrystalOperator):
    """Projection onto subspace."""
    
    def __init__(self, indices: List[int], cell: Optional[CrystalCell] = None):
        if cell is None:
            cell = CrystalCell(Constant.PI, Shape.SQUARE, Element.EARTH, Level.L1, Pole.AETHER)
        super().__init__(cell, KappaSpec(behavior=KappaBehavior.DISSIPATE))
        self.indices = set(indices)
        self.name = f"P({indices})"
    
    def apply(self, state: AethericState) -> AethericState:
        result = state.clone()
        for i, v in enumerate(result.field_data.values):
            if i not in self.indices:
                result.field_data.values[i] = 0.0j
        
        # Update κ
        norm_sq = sum(abs(v)**2 for v in result.field_data.values)
        if norm_sq > 0:
            result.normalize()
        
        return result


# =============================================================================
# COMPOSED OPERATOR
# =============================================================================

@dataclass
class ComposedOperator(CrystalOperator):
    """
    Composition of multiple operators.
    
    T = T_n ∘ T_{n-1} ∘ ... ∘ T_1
    """
    
    operators: List[CrystalOperator] = field(default_factory=list)
    
    def __post_init__(self):
        if self.operators:
            # Use first operator's cell as representative
            self.cell = self.operators[0].cell
            # Aggregate κ specs
            total_loss = sum(op.kappa_spec.expected_loss for op in self.operators)
            self.kappa_spec = KappaSpec(
                behavior=KappaBehavior.DISSIPATE if total_loss > 0 else KappaBehavior.PRESERVE,
                expected_loss=total_loss
            )
            # Aggregate costs
            total_kappa_cost = sum(op.cost_model.kappa_cost for op in self.operators)
            self.cost_model = CostModel(kappa_cost=total_kappa_cost)
        else:
            self.cell = CrystalCell(Constant.PI, Shape.SQUARE, Element.EARTH, Level.L0, Pole.AETHER)
            self.kappa_spec = KappaSpec()
            self.cost_model = CostModel()
        
        self.name = " ∘ ".join(op.name for op in reversed(self.operators))
    
    def apply(self, state: AethericState) -> AethericState:
        result = state
        for op in self.operators:
            result = op.apply(result)
        return result


# =============================================================================
# OPERATOR REGISTRY
# =============================================================================

@dataclass
class OperatorRegistry:
    """
    Registry of operators indexed by crystal cell.
    """
    
    _operators: Dict[int, List[CrystalOperator]] = field(default_factory=dict)
    
    def register(self, operator: CrystalOperator) -> None:
        """Register an operator."""
        cell_index = operator.cell.index
        if cell_index not in self._operators:
            self._operators[cell_index] = []
        self._operators[cell_index].append(operator)
    
    def get(self, cell: CrystalCell) -> List[CrystalOperator]:
        """Get operators for a cell."""
        return self._operators.get(cell.index, [])
    
    def get_by_index(self, index: int) -> List[CrystalOperator]:
        """Get operators by cell index."""
        return self._operators.get(index, [])
    
    def list_all(self) -> List[CrystalOperator]:
        """List all registered operators."""
        result = []
        for ops in self._operators.values():
            result.extend(ops)
        return result
    
    def count(self) -> int:
        """Count total operators."""
        return sum(len(ops) for ops in self._operators.values())


# =============================================================================
# OPERATOR FACTORY
# =============================================================================

class OperatorFactory:
    """
    Factory for creating canonical operators per crystal cell.
    """
    
    @staticmethod
    def create_for_cell(cell: CrystalCell, **params) -> CrystalOperator:
        """Create canonical operator for a cell."""
        
        # Dispatch based on constant
        if cell.constant == Constant.PI:
            return OperatorFactory._create_pi_operator(cell, **params)
        elif cell.constant == Constant.E:
            return OperatorFactory._create_e_operator(cell, **params)
        elif cell.constant == Constant.I:
            return OperatorFactory._create_i_operator(cell, **params)
        elif cell.constant == Constant.PHI:
            return OperatorFactory._create_phi_operator(cell, **params)
        
        return IdentityOperator(cell)
    
    @staticmethod
    def _create_pi_operator(cell: CrystalCell, **params) -> CrystalOperator:
        """Create π-based (geometric) operator."""
        if cell.shape == Shape.SQUARE:
            # Discrete geometry
            indices = params.get('indices', [0])
            return ProjectionOperator(indices, cell)
        elif cell.shape == Shape.FLOWER:
            # Fourier/rotation
            return HadamardOperator(params.get('qubit', 0), cell)
        else:
            return IdentityOperator(cell)
    
    @staticmethod
    def _create_e_operator(cell: CrystalCell, **params) -> CrystalOperator:
        """Create e-based (exponential) operator."""
        rate = params.get('rate', 0.1)
        return ExponentialOperator(rate, cell)
    
    @staticmethod
    def _create_i_operator(cell: CrystalCell, **params) -> CrystalOperator:
        """Create i-based (phase) operator."""
        theta = params.get('theta', math.pi / 4)
        return PhaseOperator(theta, cell)
    
    @staticmethod
    def _create_phi_operator(cell: CrystalCell, **params) -> CrystalOperator:
        """Create φ-based (scale) operator."""
        PHI = (1 + math.sqrt(5)) / 2
        factor = params.get('factor', 1 / PHI)
        return ScaleOperator(factor, cell)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operators() -> bool:
    """Validate operators module."""
    
    # Test primitive operators
    state = AethericState.vacuum(4)
    
    # Identity
    identity = IdentityOperator()
    result = identity.apply(state)
    assert result.is_normalized
    
    # Phase
    phase = PhaseOperator(math.pi / 2)
    result = phase.apply(state)
    assert result.is_normalized
    
    # Hadamard
    hadamard = HadamardOperator(0)
    state2 = AethericState.vacuum(2)
    result = hadamard.apply(state2)
    # Should create superposition
    assert abs(abs(result.field_data.values[0]) - 1/math.sqrt(2)) < 0.01
    
    # Composition
    composed = phase.compose(hadamard)
    assert len(composed.operators) == 2
    
    # Registry
    registry = OperatorRegistry()
    registry.register(identity)
    registry.register(phase)
    assert registry.count() == 2
    
    # Factory
    cell = CrystalCell(Constant.I, Shape.FLOWER, Element.AIR, Level.L0, Pole.AETHER)
    op = OperatorFactory.create_for_cell(cell, theta=0.5)
    assert isinstance(op, PhaseOperator)
    
    return True


if __name__ == "__main__":
    print("Validating Crystal Computing Operators...")
    assert validate_operators()
    print("✓ Crystal Operators validated")
    
    # Demo
    print("\n=== Crystal Operators Demo ===")
    
    # Create a quantum state
    state = AethericState.vacuum(2)
    print(f"\nInitial state |0⟩:")
    print(f"  Amplitudes: {[f'{v:.3f}' for v in state.field_data.values]}")
    
    # Apply Hadamard
    H = HadamardOperator(0)
    state2 = H.apply(state)
    print(f"\nAfter Hadamard H|0⟩ = |+⟩:")
    print(f"  Amplitudes: {[f'{v:.3f}' for v in state2.field_data.values]}")
    
    # Apply phase
    T = PhaseOperator(math.pi / 4)
    state3 = T.apply(state2)
    print(f"\nAfter Phase(π/4):")
    print(f"  Amplitudes: {[f'{v:.3f}' for v in state3.field_data.values]}")
    
    print(f"\nOperator chain: {H.name} → {T.name}")
    print(f"  Composed: {T.compose(H).name}")

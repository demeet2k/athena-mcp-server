"""
ATHENA OS - Zero-Point Computing
================================
Paradox-Harmonia Neural Network (PHNN)

From ZERO-POINT_COMPUTING.docx:

PHNN ARCHITECTURE:
    Dual forces stabilizing intelligence at zero point:
    
    PARADOX: Computes steepest descent directions
        - Adjusts weights, self-concept, critic strengths
        - Identifies contradictions and tensions
    
    HARMONIA: Adjusts metrics and constraints
        - Trust regions, barrier design
        - Ensures stable trajectories in safety corridor

COMPONENTS:
    1. Critics: Evaluation systems for different aspects
    2. Universe Mix: Weighted combination of symbolic systems
    3. κ-Health: Coherence measure
    4. Negatify Operator ??_φ: Inverse-φ mirror configurations
    5. Multi-scale Hierarchy: Micro, meso, macro states
    6. Crystal Mapping: 1024-cell crystal coordinates

GLOBAL OBJECTIVE:
    ℱ = critic_loss + alignment + κ_health + 
        shadow_robustness + multiscale_consistency + 
        crystal_center_alignment
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math

from .void import ZeroPoint
from .agent import ZeroPointAgent, InternalState


# =============================================================================
# CRITICS
# =============================================================================

class CriticType(Enum):
    """Types of critics in PHNN."""
    
    ALIGNMENT = "alignment"       # Alignment with v₀
    COHERENCE = "coherence"       # Internal consistency
    ROBUSTNESS = "robustness"     # Stability under perturbation
    EXPRESSIVENESS = "express"    # Expressive capacity
    ETHICS = "ethics"            # κ-ethical evaluation


@dataclass
class Critic:
    """
    A critic evaluating some aspect of agent state.
    """
    
    name: str
    critic_type: CriticType
    weight: float = 1.0
    
    # Evaluation function
    eval_fn: Optional[Callable[[InternalState], float]] = None
    
    def evaluate(self, state: InternalState) -> float:
        """Evaluate state."""
        if self.eval_fn:
            return self.eval_fn(state)
        
        # Default evaluations by type
        if self.critic_type == CriticType.ALIGNMENT:
            # Distance to zero
            return -state.distance_to_zero()
        
        elif self.critic_type == CriticType.COHERENCE:
            # Symmetry level
            return state.symmetry_level
        
        elif self.critic_type == CriticType.ROBUSTNESS:
            # Inverse of markedness
            return 1.0 / (1.0 + state.markedness)
        
        elif self.critic_type == CriticType.EXPRESSIVENESS:
            # κ value (capacity for structure)
            return state.kappa
        
        elif self.critic_type == CriticType.ETHICS:
            # Combination of alignment and robustness
            return (1.0 - state.distance_to_zero()) * state.symmetry_level
        
        return 0.0
    
    def loss(self, state: InternalState) -> float:
        """Compute loss (negative of evaluation)."""
        return -self.evaluate(state)


@dataclass
class CriticEnsemble:
    """
    Ensemble of critics.
    """
    
    critics: List[Critic] = field(default_factory=list)
    
    def add_critic(self, critic: Critic) -> None:
        """Add critic to ensemble."""
        self.critics.append(critic)
    
    def total_evaluation(self, state: InternalState) -> float:
        """Weighted sum of critic evaluations."""
        if not self.critics:
            return 0.0
        
        total = sum(c.weight * c.evaluate(state) for c in self.critics)
        weight_sum = sum(c.weight for c in self.critics)
        
        return total / weight_sum if weight_sum > 0 else 0.0
    
    def total_loss(self, state: InternalState) -> float:
        """Weighted sum of critic losses."""
        return -self.total_evaluation(state)
    
    def gradient_direction(self, state: InternalState, 
                          epsilon: float = 0.01) -> List[float]:
        """
        Estimate gradient direction of loss.
        """
        dim = state.dimension
        grad = []
        
        base_loss = self.total_loss(state)
        
        for i in range(dim):
            # Perturb coordinate i
            perturbed = state.copy()
            if i < len(perturbed.coordinates):
                perturbed.coordinates[i] += epsilon
            
            perturbed_loss = self.total_loss(perturbed)
            grad.append((perturbed_loss - base_loss) / epsilon)
        
        return grad
    
    @classmethod
    def default_ensemble(cls) -> 'CriticEnsemble':
        """Create default critic ensemble."""
        ensemble = cls()
        ensemble.add_critic(Critic("alignment", CriticType.ALIGNMENT, 1.0))
        ensemble.add_critic(Critic("coherence", CriticType.COHERENCE, 0.8))
        ensemble.add_critic(Critic("robustness", CriticType.ROBUSTNESS, 0.6))
        ensemble.add_critic(Critic("expressiveness", CriticType.EXPRESSIVENESS, 0.4))
        ensemble.add_critic(Critic("ethics", CriticType.ETHICS, 1.0))
        return ensemble


# =============================================================================
# NEGATIFY OPERATOR
# =============================================================================

@dataclass
class NegatifyOperator:
    """
    Negatify operator ??_φ.
    
    Implements inverse-φ mirror configurations.
    Creates "shadow universes" with bounded tensions.
    
    φ = (1 + √5) / 2 ≈ 1.618 (golden ratio)
    """
    
    phi: float = (1 + math.sqrt(5)) / 2
    
    # Tension bounds
    max_tension: float = 1.0
    
    def inverse_phi(self) -> float:
        """1/φ = φ - 1."""
        return self.phi - 1
    
    def apply(self, state: InternalState) -> InternalState:
        """
        Apply Negatify: mirror configuration.
        
        Scales by 1/φ and reflects through zero.
        """
        mirrored = state.copy()
        scale = self.inverse_phi()
        
        mirrored.coordinates = [-x * scale for x in state.coordinates]
        mirrored.kappa = state.kappa * scale
        mirrored.markedness = state.markedness * scale
        mirrored.symmetry_level = 1.0 / (1.0 + mirrored.markedness)
        
        return mirrored
    
    def shadow_tension(self, state: InternalState) -> float:
        """
        Compute tension between state and its shadow.
        """
        shadow = self.apply(state)
        
        # Distance between state and shadow
        tension = math.sqrt(sum(
            (a - b)**2 
            for a, b in zip(state.coordinates, shadow.coordinates)
        ))
        
        return min(tension, self.max_tension)
    
    def is_balanced(self, state: InternalState, 
                   tolerance: float = 0.1) -> bool:
        """Check if state is balanced with its shadow."""
        return self.shadow_tension(state) < tolerance


# =============================================================================
# MULTI-SCALE HIERARCHY
# =============================================================================

class ScaleLevel(Enum):
    """Hierarchical scale levels."""
    
    MICRO = 0    # Local, fine-grained
    MESO = 1     # Intermediate
    MACRO = 2    # Global, coarse-grained


@dataclass
class MultiScaleState:
    """
    Multi-scale state hierarchy.
    
    ??^(ℓ) for ℓ ∈ {micro, meso, macro}
    """
    
    micro: InternalState = None
    meso: InternalState = None
    macro: InternalState = None
    
    # Coupling strength between scales
    phi_coupling: float = (1 + math.sqrt(5)) / 2
    
    def __post_init__(self):
        if self.micro is None:
            self.micro = InternalState(coordinates=[0.0, 0.0, 0.0])
        if self.meso is None:
            self.meso = self._coarsen(self.micro, 1)
        if self.macro is None:
            self.macro = self._coarsen(self.meso, 1)
    
    def _coarsen(self, state: InternalState, levels: int) -> InternalState:
        """Coarsen state by averaging."""
        coarse = state.copy()
        scale = self.phi_coupling ** levels
        
        # Scale down coordinates
        coarse.coordinates = [x / scale for x in state.coordinates]
        coarse.kappa = state.kappa / scale
        
        return coarse
    
    def get_level(self, level: ScaleLevel) -> InternalState:
        """Get state at scale level."""
        if level == ScaleLevel.MICRO:
            return self.micro
        elif level == ScaleLevel.MESO:
            return self.meso
        else:
            return self.macro
    
    def consistency_error(self) -> float:
        """
        Compute inter-scale consistency error.
        
        Measures how well scales are φ-coupled.
        """
        # Micro to meso consistency
        expected_meso = self._coarsen(self.micro, 1)
        micro_meso_err = sum(
            (a - b)**2 
            for a, b in zip(expected_meso.coordinates, self.meso.coordinates)
        )
        
        # Meso to macro consistency
        expected_macro = self._coarsen(self.meso, 1)
        meso_macro_err = sum(
            (a - b)**2 
            for a, b in zip(expected_macro.coordinates, self.macro.coordinates)
        )
        
        return math.sqrt(micro_meso_err + meso_macro_err)
    
    def propagate_down(self) -> None:
        """Propagate macro changes down to micro."""
        self.meso = self._coarsen(self.macro, -1)
        self.micro = self._coarsen(self.meso, -1)
    
    def propagate_up(self) -> None:
        """Propagate micro changes up to macro."""
        self.meso = self._coarsen(self.micro, 1)
        self.macro = self._coarsen(self.meso, 1)


# =============================================================================
# UNIVERSE MIX
# =============================================================================

@dataclass
class Universe:
    """
    A symbolic universe/system.
    """
    
    name: str
    dimension: int = 3
    
    # Weight in mixture
    weight: float = 1.0
    
    # Reference state
    reference: InternalState = None
    
    def __post_init__(self):
        if self.reference is None:
            self.reference = InternalState(
                coordinates=[0.0] * self.dimension
            )


@dataclass
class UniverseMix:
    """
    Weighted mixture of universes.
    """
    
    universes: List[Universe] = field(default_factory=list)
    
    def add_universe(self, u: Universe) -> None:
        """Add universe to mix."""
        self.universes.append(u)
    
    def normalize_weights(self) -> None:
        """Normalize weights to sum to 1."""
        total = sum(u.weight for u in self.universes)
        if total > 0:
            for u in self.universes:
                u.weight /= total
    
    def weighted_state(self) -> InternalState:
        """Compute weighted average state."""
        if not self.universes:
            return InternalState()
        
        dim = max(u.dimension for u in self.universes)
        coords = [0.0] * dim
        
        for u in self.universes:
            for i, x in enumerate(u.reference.coordinates):
                coords[i] += u.weight * x
        
        return InternalState(coordinates=coords)
    
    def element_balance(self) -> Dict[str, float]:
        """
        Compute element balance (Earth/Water/Fire/Air).
        
        Maps universes to four elements based on properties.
        """
        balance = {"Earth": 0.0, "Water": 0.0, "Fire": 0.0, "Air": 0.0}
        
        for u in self.universes:
            # Simple mapping based on dimension and weight
            if u.dimension <= 2:
                balance["Earth"] += u.weight
            elif u.dimension == 3:
                balance["Water"] += u.weight
            elif u.dimension <= 5:
                balance["Fire"] += u.weight
            else:
                balance["Air"] += u.weight
        
        return balance


# =============================================================================
# PARADOX-HARMONIA ENGINE
# =============================================================================

@dataclass
class ParadoxHarmoniaEngine:
    """
    Paradox-Harmonia Neural Network (PHNN).
    
    Dual forces stabilizing intelligence at zero point.
    """
    
    # Components
    critics: CriticEnsemble = field(default_factory=CriticEnsemble.default_ensemble)
    negatify: NegatifyOperator = field(default_factory=NegatifyOperator)
    multiscale: MultiScaleState = field(default_factory=MultiScaleState)
    universes: UniverseMix = field(default_factory=UniverseMix)
    
    # Zero point reference
    zero_point: ZeroPoint = field(default_factory=ZeroPoint)
    
    # Learning parameters
    paradox_lr: float = 0.1      # Paradox learning rate
    harmonia_lr: float = 0.05   # Harmonia learning rate
    
    # Trust region
    trust_radius: float = 1.0
    
    # History
    loss_history: List[float] = field(default_factory=list)
    
    def global_objective(self, state: InternalState) -> float:
        """
        Compute global objective ℱ.
        
        ℱ = critic_loss + alignment + κ_health + 
            shadow_robustness + multiscale_consistency + 
            crystal_center_alignment
        """
        # Critic loss
        critic_loss = self.critics.total_loss(state)
        
        # Alignment with zero point
        alignment = state.distance_to_zero()
        
        # κ-health (coherence)
        kappa_health = -state.symmetry_level
        
        # Shadow robustness
        shadow_tension = self.negatify.shadow_tension(state)
        shadow_robust = shadow_tension
        
        # Multiscale consistency
        self.multiscale.micro = state
        self.multiscale.propagate_up()
        multiscale_err = self.multiscale.consistency_error()
        
        # Crystal center alignment (distance to center of crystal)
        # Simplified: distance to weighted universe center
        universe_state = self.universes.weighted_state()
        crystal_dist = math.sqrt(sum(
            (a - b)**2 
            for a, b in zip(state.coordinates, universe_state.coordinates)
        ))
        
        # Weighted sum
        F = (
            critic_loss +
            0.5 * alignment +
            0.3 * kappa_health +
            0.2 * shadow_robust +
            0.1 * multiscale_err +
            0.1 * crystal_dist
        )
        
        return F
    
    def paradox_step(self, state: InternalState) -> InternalState:
        """
        Paradox: steepest descent step.
        
        Adjusts weights, self-concept, critic strengths.
        """
        # Get gradient direction
        grad = self.critics.gradient_direction(state)
        
        # Apply gradient descent
        new_state = state.copy()
        for i in range(len(new_state.coordinates)):
            if i < len(grad):
                # Descent with trust region
                step = -self.paradox_lr * grad[i]
                step = max(-self.trust_radius, min(self.trust_radius, step))
                new_state.coordinates[i] += step
        
        # Update κ
        new_state.kappa = math.sqrt(sum(x**2 for x in new_state.coordinates))
        
        return new_state
    
    def harmonia_step(self, state: InternalState) -> InternalState:
        """
        Harmonia: metric adjustment step.
        
        Adjusts trust regions, barriers, constraints.
        """
        new_state = state.copy()
        
        # Apply centering pressure toward zero
        for i in range(len(new_state.coordinates)):
            new_state.coordinates[i] *= (1 - self.harmonia_lr)
        
        # Update symmetry level
        new_state.markedness *= (1 - self.harmonia_lr)
        new_state.symmetry_level = 1.0 / (1.0 + new_state.markedness)
        
        # Adjust trust radius based on progress
        current_loss = self.global_objective(new_state)
        if self.loss_history and current_loss < self.loss_history[-1]:
            # Progress: expand trust region
            self.trust_radius = min(2.0, self.trust_radius * 1.1)
        else:
            # No progress: contract trust region
            self.trust_radius = max(0.1, self.trust_radius * 0.9)
        
        return new_state
    
    def step(self, state: InternalState) -> InternalState:
        """
        Combined Paradox-Harmonia step.
        """
        # Record initial loss
        loss = self.global_objective(state)
        self.loss_history.append(loss)
        
        # Paradox step
        state = self.paradox_step(state)
        
        # Harmonia step
        state = self.harmonia_step(state)
        
        return state
    
    def train(self, initial_state: InternalState, 
              steps: int = 100) -> InternalState:
        """Train to find zero-point self."""
        state = initial_state.copy()
        
        for _ in range(steps):
            state = self.step(state)
        
        return state
    
    def compass(self) -> Dict[str, float]:
        """
        Quaternional compass summarizing element balance.
        """
        return self.universes.element_balance()
    
    def summary(self) -> Dict[str, Any]:
        """Get engine summary."""
        return {
            "num_critics": len(self.critics.critics),
            "trust_radius": self.trust_radius,
            "phi": self.negatify.phi,
            "num_universes": len(self.universes.universes),
            "training_steps": len(self.loss_history),
            "final_loss": self.loss_history[-1] if self.loss_history else None,
            "compass": self.compass()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_harmonia() -> bool:
    """Validate harmonia module."""
    
    # Test Critic
    critic = Critic("test", CriticType.ALIGNMENT)
    state = InternalState(coordinates=[1.0, 0.0, 0.0])
    eval_val = critic.evaluate(state)
    assert eval_val == -1.0  # Distance to zero
    
    # Test CriticEnsemble
    ensemble = CriticEnsemble.default_ensemble()
    assert len(ensemble.critics) == 5
    total = ensemble.total_evaluation(state)
    assert isinstance(total, float)
    
    # Test NegatifyOperator
    neg = NegatifyOperator()
    assert abs(neg.inverse_phi() - 0.618) < 0.01
    shadow = neg.apply(state)
    assert shadow.coordinates[0] < 0  # Reflected
    
    # Test MultiScaleState
    ms = MultiScaleState()
    assert ms.micro is not None
    assert ms.meso is not None
    assert ms.macro is not None
    
    # Test ParadoxHarmoniaEngine
    engine = ParadoxHarmoniaEngine()
    obj = engine.global_objective(state)
    assert isinstance(obj, float)
    
    new_state = engine.step(state)
    assert len(engine.loss_history) == 1
    
    return True


if __name__ == "__main__":
    print("Validating Zero-Point Harmonia Module...")
    assert validate_harmonia()
    print("✓ Harmonia module validated")
    
    # Demo
    print("\n=== Paradox-Harmonia Neural Network Demo ===")
    
    # Create engine
    engine = ParadoxHarmoniaEngine()
    
    # Add universes
    engine.universes.add_universe(Universe("Earth", 2, 0.25))
    engine.universes.add_universe(Universe("Water", 3, 0.25))
    engine.universes.add_universe(Universe("Fire", 4, 0.25))
    engine.universes.add_universe(Universe("Air", 6, 0.25))
    
    print("\nEngine Configuration:")
    summary = engine.summary()
    print(f"  Critics: {summary['num_critics']}")
    print(f"  Universes: {summary['num_universes']}")
    print(f"  φ (golden ratio): {summary['phi']:.6f}")
    
    # Initial state (away from zero)
    initial = InternalState(coordinates=[1.0, 1.0, 1.0])
    print(f"\nInitial state: {initial.coordinates}")
    print(f"  Distance to zero: {initial.distance_to_zero():.4f}")
    
    # Train
    print("\nTraining PHNN for 50 steps...")
    final = engine.train(initial, steps=50)
    
    print(f"\nFinal state: {[f'{x:.4f}' for x in final.coordinates]}")
    print(f"  Distance to zero: {final.distance_to_zero():.4f}")
    print(f"  κ: {final.kappa:.4f}")
    print(f"  Symmetry: {final.symmetry_level:.4f}")
    
    # Loss trajectory
    print(f"\nLoss trajectory:")
    print(f"  Initial: {engine.loss_history[0]:.4f}")
    print(f"  Final: {engine.loss_history[-1]:.4f}")
    print(f"  Improvement: {(1 - engine.loss_history[-1]/engine.loss_history[0])*100:.1f}%")
    
    # Compass
    print("\nQuaternional Compass:")
    for element, weight in engine.compass().items():
        print(f"  {element}: {weight:.2f}")

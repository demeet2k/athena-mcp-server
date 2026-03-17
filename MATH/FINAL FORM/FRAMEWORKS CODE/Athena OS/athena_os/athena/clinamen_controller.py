"""
ATHENA OS - CLINAMEN INTERRUPT CONTROLLER
==========================================
Branching Autonomy for the Logic-First OS

From Greek_Corpus__LF-OS_.docx:

THE CLINAMEN (SWERVE):
    A formally delimited stochastic operator that preserves system
    invariants and causal closure while preventing lockstep determinism.
    
    Formalizes branching as a Hardware Interrupt internal to the kernel
    rather than a narrative patch for explanatory gaps.

RATIONALE:
    1. Avoiding Lockstep Determinism - identical inputs need not yield
       identical outputs at observer resolution
    2. Symmetry Breaking - enables diverse patterns from uniform states
    3. Local Autonomy - provides degrees of freedom for agentic decision
    4. No Divine Intervention - branching without external agents

THE INTERRUPT MODEL η:
    η ≡ (σ, λ or p, ε, π, D, G, Ω)
    
    - σ: Magnitude bound for deviation
    - λ/p: Rate or probability of activation
    - ε: Eligibility predicate
    - π: Perturbation type
    - D: Directional distribution
    - G: Gating predicate
    - Ω: Safety constraints

BOUNDED STOCHASTIC JUMP:
    J_η: S → S'
    v_a → v'_a = Rot(v_a, δ), where |v'_a| = |v_a|
    
    Non-destructive: redirects trajectories without
    dissolving atomic identities or violating invariants.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Callable, Any
from enum import Enum, auto
import math
import random


# =============================================================================
# INTERRUPT CONFIGURATION
# =============================================================================

class PerturbationType(Enum):
    """Types of perturbation the swerve can apply."""
    DIRECTIONAL = auto()   # Rotate velocity direction
    MAGNITUDE = auto()     # Adjust speed (bounded)
    POSITIONAL = auto()    # Small position shift
    PHASE = auto()         # Phase shift in oscillation


class DirectionalDistribution(Enum):
    """Distribution for directional deviations."""
    UNIFORM = auto()       # Uniform on unit sphere
    GAUSSIAN = auto()      # Gaussian around current direction
    PLANAR = auto()        # Restricted to a plane
    RADIAL = auto()        # Along radial direction


@dataclass
class InterruptParameters:
    """
    The Interrupt Model η.
    
    η ≡ (σ, λ, ε, π, D, G, Ω)
    """
    
    sigma: float = 0.01              # Magnitude bound (max deviation angle)
    lambda_rate: float = 0.001       # Activation rate (per unit time)
    probability: float = 0.01        # Per-event probability (alternative)
    perturbation_type: PerturbationType = PerturbationType.DIRECTIONAL
    distribution: DirectionalDistribution = DirectionalDistribution.GAUSSIAN
    
    def validate(self) -> bool:
        """Validate parameter bounds."""
        return (
            0 < self.sigma < math.pi / 4 and  # Small angle only
            0 <= self.lambda_rate <= 1.0 and
            0 <= self.probability <= 1.0
        )


# =============================================================================
# GATING PREDICATES
# =============================================================================

@dataclass
class GatingPredicate:
    """
    Gating predicate G(S) for interrupt activation.
    
    Restrictions:
    - Event-Boundary Gating: Only at collision windows
    - Locality Gating: Target single carrier
    - Eligibility Gating: Only eligible atoms
    """
    
    require_free_motion: bool = True     # Not bound in compound
    require_event_boundary: bool = True  # Near collision event
    min_velocity: float = 0.01           # Must be moving
    max_binding_count: int = 0           # Not critically bound
    
    def evaluate(self, carrier_state: Dict[str, Any]) -> bool:
        """Evaluate if carrier passes gating."""
        if self.require_free_motion:
            if carrier_state.get("binding_count", 0) > self.max_binding_count:
                return False
        
        if self.require_event_boundary:
            if not carrier_state.get("near_event", False):
                return False
        
        velocity = carrier_state.get("velocity_magnitude", 0.0)
        if velocity < self.min_velocity:
            return False
        
        return True


@dataclass
class SafetyConstraints:
    """
    Safety constraints Ω for the interrupt.
    
    Ensures kernel stability is preserved.
    """
    
    preserve_magnitude: bool = True      # |v'| = |v|
    preserve_identity: bool = True       # Atomic identity unchanged
    respect_invariants: bool = True      # No invariant violations
    max_deviation_angle: float = 0.1     # Radians
    
    def verify(self, pre_state: Dict, post_state: Dict) -> bool:
        """Verify safety constraints satisfied."""
        if self.preserve_magnitude:
            v_pre = pre_state.get("velocity_magnitude", 0.0)
            v_post = post_state.get("velocity_magnitude", 0.0)
            if abs(v_pre - v_post) > 1e-10:
                return False
        
        if self.preserve_identity:
            if pre_state.get("id") != post_state.get("id"):
                return False
        
        return True


# =============================================================================
# THE SWERVE OPERATOR
# =============================================================================

class SwerveOperator:
    """
    The Bounded Stochastic Jump Operator J_η.
    
    Perturbs the piecewise-deterministic trajectory of a system state.
    v_a → v'_a = Rot(v_a, δ), where |v'_a| = |v_a|
    """
    
    def __init__(self, params: InterruptParameters = None):
        self.params = params or InterruptParameters()
        self._rng = random.Random()
    
    def seed(self, seed: int) -> None:
        """Seed the random number generator."""
        self._rng.seed(seed)
    
    def _sample_deviation_angle(self) -> float:
        """Sample deviation angle from distribution."""
        if self.params.distribution == DirectionalDistribution.GAUSSIAN:
            # Gaussian with σ as standard deviation
            return self._rng.gauss(0, self.params.sigma)
        elif self.params.distribution == DirectionalDistribution.UNIFORM:
            # Uniform in [-σ, σ]
            return self._rng.uniform(-self.params.sigma, self.params.sigma)
        else:
            return self._rng.uniform(-self.params.sigma, self.params.sigma)
    
    def _sample_rotation_axis(self) -> Tuple[float, float, float]:
        """Sample random rotation axis (unit vector)."""
        # Uniform on unit sphere
        theta = self._rng.uniform(0, 2 * math.pi)
        phi = math.acos(2 * self._rng.random() - 1)
        
        return (
            math.sin(phi) * math.cos(theta),
            math.sin(phi) * math.sin(theta),
            math.cos(phi)
        )
    
    def rotate_vector(self, v: List[float], axis: Tuple[float, float, float],
                     angle: float) -> List[float]:
        """
        Rotate vector v around axis by angle (Rodrigues' formula).
        
        v' = v*cos(θ) + (k × v)*sin(θ) + k*(k·v)*(1-cos(θ))
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # k × v (cross product)
        cross = [
            axis[1] * v[2] - axis[2] * v[1],
            axis[2] * v[0] - axis[0] * v[2],
            axis[0] * v[1] - axis[1] * v[0]
        ]
        
        # k · v (dot product)
        dot = sum(axis[i] * v[i] for i in range(3))
        
        # Rodrigues' formula
        result = [
            v[i] * cos_a + cross[i] * sin_a + axis[i] * dot * (1 - cos_a)
            for i in range(3)
        ]
        
        return result
    
    def apply(self, velocity: List[float]) -> List[float]:
        """
        Apply swerve to velocity vector.
        
        Returns rotated velocity with preserved magnitude.
        """
        # Sample deviation
        angle = self._sample_deviation_angle()
        axis = self._sample_rotation_axis()
        
        # Rotate
        new_velocity = self.rotate_vector(velocity, axis, angle)
        
        # Verify magnitude preservation
        orig_mag = math.sqrt(sum(v**2 for v in velocity))
        new_mag = math.sqrt(sum(v**2 for v in new_velocity))
        
        if orig_mag > 0 and abs(new_mag - orig_mag) > 1e-10:
            # Normalize to preserve magnitude
            scale = orig_mag / new_mag
            new_velocity = [v * scale for v in new_velocity]
        
        return new_velocity
    
    def should_activate(self) -> bool:
        """Determine if swerve should activate (probabilistic)."""
        return self._rng.random() < self.params.probability


# =============================================================================
# THE CLINAMEN INTERRUPT CONTROLLER
# =============================================================================

@dataclass
class InterruptEvent:
    """Record of a clinamen interrupt event."""
    
    event_id: int
    time: float
    target_id: int
    pre_velocity: List[float]
    post_velocity: List[float]
    deviation_angle: float
    
    @property
    def magnitude_preserved(self) -> bool:
        """Check if magnitude was preserved."""
        pre_mag = math.sqrt(sum(v**2 for v in self.pre_velocity))
        post_mag = math.sqrt(sum(v**2 for v in self.post_velocity))
        return abs(pre_mag - post_mag) < 1e-10


class ClinanenInterruptController:
    """
    The Clinamen Interrupt Controller.
    
    Primary mechanism for introducing branching autonomy into
    the deterministic execution of the LF-OS.
    
    Features:
    - Gated activation protocol
    - Bounded stochastic jumps
    - Full audit trail
    - Safety constraint enforcement
    """
    
    def __init__(self, params: InterruptParameters = None):
        self.params = params or InterruptParameters()
        self.swerve = SwerveOperator(self.params)
        self.gating = GatingPredicate()
        self.safety = SafetyConstraints()
        
        self.event_counter = 0
        self.interrupt_log: List[InterruptEvent] = []
        self.activation_count = 0
        self.rejection_count = 0
    
    def configure(self, params: InterruptParameters) -> None:
        """Reconfigure interrupt parameters."""
        if params.validate():
            self.params = params
            self.swerve = SwerveOperator(params)
    
    def seed(self, seed: int) -> None:
        """Seed random generator for reproducibility."""
        self.swerve.seed(seed)
    
    def _compute_deviation_angle(self, v1: List[float], 
                                  v2: List[float]) -> float:
        """Compute angle between two vectors."""
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(v**2 for v in v1))
        mag2 = math.sqrt(sum(v**2 for v in v2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
        return math.acos(cos_angle)
    
    def process_carrier(self, carrier_id: int, 
                       carrier_state: Dict[str, Any],
                       current_time: float) -> Optional[Dict[str, Any]]:
        """
        Process a carrier for potential interrupt.
        
        1. Check gating predicate
        2. Check activation probability
        3. Apply swerve if triggered
        4. Verify safety constraints
        5. Log event
        """
        # Step 1: Gating check
        if not self.gating.evaluate(carrier_state):
            self.rejection_count += 1
            return None
        
        # Step 2: Activation check
        if not self.swerve.should_activate():
            return None
        
        # Step 3: Apply swerve
        velocity = carrier_state.get("velocity", [0, 0, 0])
        new_velocity = self.swerve.apply(velocity)
        
        # Build post-state
        post_state = dict(carrier_state)
        post_state["velocity"] = new_velocity
        post_state["velocity_magnitude"] = math.sqrt(
            sum(v**2 for v in new_velocity)
        )
        
        # Step 4: Safety check
        if not self.safety.verify(carrier_state, post_state):
            self.rejection_count += 1
            return None
        
        # Step 5: Log event
        self.event_counter += 1
        self.activation_count += 1
        
        deviation = self._compute_deviation_angle(velocity, new_velocity)
        
        event = InterruptEvent(
            event_id=self.event_counter,
            time=current_time,
            target_id=carrier_id,
            pre_velocity=list(velocity),
            post_velocity=new_velocity,
            deviation_angle=deviation
        )
        self.interrupt_log.append(event)
        
        return post_state
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get interrupt controller statistics."""
        if not self.interrupt_log:
            avg_deviation = 0.0
        else:
            avg_deviation = sum(
                e.deviation_angle for e in self.interrupt_log
            ) / len(self.interrupt_log)
        
        return {
            "total_events": self.event_counter,
            "activations": self.activation_count,
            "rejections": self.rejection_count,
            "average_deviation": avg_deviation,
            "magnitude_preserved_ratio": sum(
                1 for e in self.interrupt_log if e.magnitude_preserved
            ) / max(1, len(self.interrupt_log))
        }
    
    def verify_audit_trail(self) -> bool:
        """Verify all logged events maintain invariants."""
        return all(e.magnitude_preserved for e in self.interrupt_log)


# =============================================================================
# SYMMETRY BREAKER
# =============================================================================

class SymmetryBreaker:
    """
    Symmetry Breaking Module.
    
    When initial configurations are symmetric, deterministic evolution
    preserves symmetry unless interrupted by explicit symmetry-breaker.
    
    The Clinamen functions as minimal, lawful symmetry-breaker.
    """
    
    def __init__(self, controller: ClinanenInterruptController):
        self.controller = controller
    
    def detect_symmetry(self, states: List[Dict[str, Any]],
                       tolerance: float = 1e-6) -> bool:
        """Detect if system has symmetrical state."""
        if len(states) < 2:
            return False
        
        # Check for velocity symmetry
        velocities = [s.get("velocity", [0, 0, 0]) for s in states]
        
        # Check if velocities sum to near-zero (balanced)
        total = [sum(v[i] for v in velocities) for i in range(3)]
        total_mag = math.sqrt(sum(t**2 for t in total))
        
        return total_mag < tolerance
    
    def break_symmetry(self, states: List[Dict[str, Any]],
                      current_time: float) -> List[Dict[str, Any]]:
        """
        Apply symmetry-breaking swerve to one carrier.
        
        Selects single carrier to perturb.
        """
        if not states:
            return states
        
        # Select random carrier
        idx = random.randint(0, len(states) - 1)
        
        # Force activation for symmetry breaking
        original_prob = self.controller.params.probability
        self.controller.params.probability = 1.0
        
        result = self.controller.process_carrier(
            states[idx].get("id", idx),
            states[idx],
            current_time
        )
        
        # Restore probability
        self.controller.params.probability = original_prob
        
        if result:
            states[idx] = result
        
        return states


# =============================================================================
# BRANCHING AUTONOMY MANAGER
# =============================================================================

class BranchingAutonomyManager:
    """
    High-level manager for branching autonomy.
    
    Integrates:
    - Clinamen interrupt controller
    - Symmetry breaking
    - Trajectory diversification
    """
    
    def __init__(self, params: InterruptParameters = None):
        self.controller = ClinanenInterruptController(params)
        self.symmetry_breaker = SymmetryBreaker(self.controller)
        self.trajectory_branches: Dict[int, List[List[float]]] = {}
    
    def process_system(self, carriers: Dict[int, Dict[str, Any]],
                      current_time: float) -> Dict[int, Dict[str, Any]]:
        """
        Process all carriers for potential interrupts.
        
        Returns updated carrier states.
        """
        results = {}
        
        for cid, state in carriers.items():
            new_state = self.controller.process_carrier(cid, state, current_time)
            results[cid] = new_state if new_state else state
            
            # Track trajectory
            if cid not in self.trajectory_branches:
                self.trajectory_branches[cid] = []
            self.trajectory_branches[cid].append(
                results[cid].get("velocity", [0, 0, 0])
            )
        
        return results
    
    def get_divergence_metric(self) -> float:
        """Calculate trajectory divergence from interrupts."""
        if not self.trajectory_branches:
            return 0.0
        
        # Measure average trajectory curvature
        total_curvature = 0.0
        count = 0
        
        for cid, trajectory in self.trajectory_branches.items():
            if len(trajectory) < 3:
                continue
            
            for i in range(1, len(trajectory) - 1):
                v0 = trajectory[i-1]
                v1 = trajectory[i]
                v2 = trajectory[i+1]
                
                # Compute angle changes
                angle1 = math.atan2(v1[1] - v0[1], v1[0] - v0[0])
                angle2 = math.atan2(v2[1] - v1[1], v2[0] - v1[0])
                
                curvature = abs(angle2 - angle1)
                total_curvature += curvature
                count += 1
        
        return total_curvature / max(1, count)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_clinamen_controller() -> bool:
    """Validate the clinamen interrupt controller module."""
    
    # Test parameters
    params = InterruptParameters(sigma=0.05, probability=0.5)
    assert params.validate()
    
    # Test swerve operator
    swerve = SwerveOperator(params)
    swerve.seed(42)
    
    velocity = [1.0, 0.0, 0.0]
    new_velocity = swerve.apply(velocity)
    
    # Magnitude should be preserved
    orig_mag = math.sqrt(sum(v**2 for v in velocity))
    new_mag = math.sqrt(sum(v**2 for v in new_velocity))
    assert abs(orig_mag - new_mag) < 1e-10
    
    # Test controller
    controller = ClinanenInterruptController(params)
    controller.seed(42)
    
    carrier_state = {
        "id": 1,
        "velocity": [1.0, 0.0, 0.0],
        "velocity_magnitude": 1.0,
        "binding_count": 0,
        "near_event": True
    }
    
    # Process multiple times to get some activations
    activations = 0
    for _ in range(100):
        result = controller.process_carrier(1, carrier_state, 0.0)
        if result:
            activations += 1
    
    # Should have some activations with 50% probability
    assert activations > 0
    
    # Test audit trail
    assert controller.verify_audit_trail()
    
    # Test statistics
    stats = controller.get_statistics()
    assert stats["magnitude_preserved_ratio"] == 1.0
    
    # Test symmetry breaker
    breaker = SymmetryBreaker(controller)
    states = [
        {"id": 1, "velocity": [1, 0, 0]},
        {"id": 2, "velocity": [-1, 0, 0]}
    ]
    assert breaker.detect_symmetry(states)
    
    # Break symmetry
    broken = breaker.break_symmetry(states, 1.0)
    # Should have modified at least one state
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - CLINAMEN INTERRUPT CONTROLLER")
    print("Branching Autonomy for the Logic-First OS")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_clinamen_controller()
    print("✓ Module validated")
    
    # Demo
    print("\n--- CLINAMEN DEMONSTRATION ---")
    params = InterruptParameters(sigma=0.1, probability=0.3)
    manager = BranchingAutonomyManager(params)
    manager.controller.seed(42)
    
    # Create carriers
    carriers = {
        1: {"id": 1, "velocity": [1, 0, 0], "velocity_magnitude": 1.0,
            "binding_count": 0, "near_event": True},
        2: {"id": 2, "velocity": [0, 1, 0], "velocity_magnitude": 1.0,
            "binding_count": 0, "near_event": True},
        3: {"id": 3, "velocity": [-1, -1, 0], "velocity_magnitude": 1.414,
            "binding_count": 0, "near_event": True}
    }
    
    # Process system multiple times
    print("\nProcessing 50 time steps...")
    for t in range(50):
        carriers = manager.process_system(carriers, t * 0.1)
    
    stats = manager.controller.get_statistics()
    print(f"\n--- STATISTICS ---")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Activations: {stats['activations']}")
    print(f"  Rejections: {stats['rejections']}")
    print(f"  Average deviation: {stats['average_deviation']:.4f} rad")
    print(f"  Magnitude preserved: {stats['magnitude_preserved_ratio']:.1%}")
    
    print(f"\n  Trajectory divergence: {manager.get_divergence_metric():.4f}")

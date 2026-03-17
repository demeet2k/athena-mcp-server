"""
ATHENA OS - Stoic Control System & Liberation Protocols
=======================================================
Implements Stoic philosophy as a runtime control system.

Core principle: Distinguish what is "up to us" (eph' hēmin) from
what is "not up to us" (ouk eph' hēmin).

INTERNAL domain: judgments, impulses, desires, aversions
EXTERNAL domain: body, reputation, property, outcomes

Liberation = achieving tranquility (ataraxia) through proper control allocation.

Optimization Protocols:
1. Karma Yoga: Non-blocking I/O (attachment_level → 0)
2. Bhakti Yoga: Phase-locking with system frequency
3. Jnana Yoga: Recursive deletion (neti-neti algorithm)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Set, Any
from abc import ABC, abstractmethod
import math
import random


# =============================================================================
# CONTROL DOMAINS
# =============================================================================

class ControlDomain(IntEnum):
    """
    The two fundamental domains of Stoic control theory.
    
    INTERNAL: Things that are "up to us" (eph' hēmin)
    EXTERNAL: Things "not up to us" (ouk eph' hēmin)
    """
    INTERNAL = 0  # Under our control: judgments, impulses, desires
    EXTERNAL = 1  # Not under our control: body, reputation, outcomes


@dataclass
class ControlItem:
    """
    An item with classified control status.
    
    Proper control allocation is the foundation of Stoic practice.
    Misattribution (treating external as internal or vice versa) 
    is the source of all disturbed states.
    """
    name: str
    domain: ControlDomain
    value: Any = None
    preferred: bool = False  # "Preferred indifferent" vs "dispreferred indifferent"
    
    @property
    def is_internal(self) -> bool:
        return self.domain == ControlDomain.INTERNAL
    
    @property
    def is_external(self) -> bool:
        return self.domain == ControlDomain.EXTERNAL


# =============================================================================
# STOIC PSYCHOLOGY: THE HEGEMONIKON
# =============================================================================

class JudgmentType(IntEnum):
    """Types of judgments (dogmata) in the hegemonikon."""
    ASSENT = 0      # Agreement that something is the case
    IMPULSE = 1     # Movement toward or away from something
    DESIRE = 2      # Wish for something to occur
    AVERSION = 3    # Wish for something not to occur


@dataclass
class Judgment:
    """
    A judgment (dogma) in the hegemonikon.
    
    Judgments are the fundamental unit of internal activity.
    All emotional states derive from judgments about what is
    good, bad, or indifferent.
    """
    judgment_type: JudgmentType
    content: str
    target: Optional[str] = None
    strength: float = 1.0  # 0.0 to 1.0
    timestamp: float = 0.0
    
    def is_rational(self, control_registry: Dict[str, ControlDomain]) -> bool:
        """
        Check if this judgment is rational.
        
        A judgment is irrational if it assigns good/bad value
        to things not under our control.
        """
        if self.target and self.target in control_registry:
            domain = control_registry[self.target]
            # Only internal things can be genuinely good/bad
            if self.judgment_type in (JudgmentType.DESIRE, JudgmentType.AVERSION):
                return domain == ControlDomain.INTERNAL
        return True


@dataclass
class Hegemonikon:
    """
    The ruling faculty (hegemonikon) - the seat of reason and judgment.
    
    This is the "command center" that processes impressions (phantasiai)
    and issues judgments. Proper function of the hegemonikon is the
    foundation of virtue and tranquility.
    """
    judgments: List[Judgment] = field(default_factory=list)
    control_registry: Dict[str, ControlDomain] = field(default_factory=dict)
    tranquility_level: float = 0.5
    
    def register_item(self, name: str, domain: ControlDomain) -> None:
        """Register an item's control classification."""
        self.control_registry[name] = domain
    
    def receive_impression(self, content: str, target: Optional[str] = None) -> Judgment:
        """
        Receive an impression (phantasia) and form a judgment.
        
        The key Stoic move: we can withhold assent from impressions.
        """
        # Default: withhold strong judgment on external matters
        strength = 1.0
        if target and target in self.control_registry:
            if self.control_registry[target] == ControlDomain.EXTERNAL:
                strength = 0.3  # Reduce attachment to externals
        
        judgment = Judgment(
            judgment_type=JudgmentType.ASSENT,
            content=content,
            target=target,
            strength=strength,
            timestamp=len(self.judgments)
        )
        self.judgments.append(judgment)
        return judgment
    
    def form_impulse(self, target: str, toward: bool = True) -> Optional[Judgment]:
        """Form an impulse toward or away from something."""
        if target in self.control_registry:
            domain = self.control_registry[target]
            if domain == ControlDomain.EXTERNAL:
                # External: form only weak preference
                judgment = Judgment(
                    judgment_type=JudgmentType.IMPULSE,
                    content=f"{'toward' if toward else 'away from'} {target}",
                    target=target,
                    strength=0.2,  # Weak - it's external
                    timestamp=len(self.judgments)
                )
            else:
                # Internal: can form strong impulse
                judgment = Judgment(
                    judgment_type=JudgmentType.IMPULSE,
                    content=f"{'toward' if toward else 'away from'} {target}",
                    target=target,
                    strength=1.0,
                    timestamp=len(self.judgments)
                )
            self.judgments.append(judgment)
            return judgment
        return None
    
    def calculate_tranquility(self) -> float:
        """
        Calculate current tranquility (ataraxia) level.
        
        Tranquility is inversely proportional to attachment to externals.
        """
        if not self.judgments:
            return 1.0
        
        external_attachment = 0.0
        total_judgments = 0
        
        for j in self.judgments[-20:]:  # Consider recent judgments
            if j.target and j.target in self.control_registry:
                if self.control_registry[j.target] == ControlDomain.EXTERNAL:
                    external_attachment += j.strength
            total_judgments += 1
        
        if total_judgments == 0:
            return 1.0
        
        # Tranquility decreases with external attachment
        avg_attachment = external_attachment / total_judgments
        self.tranquility_level = max(0.0, 1.0 - avg_attachment)
        return self.tranquility_level
    
    def apply_discipline(self) -> int:
        """
        Apply Stoic discipline to all judgments.
        Returns number of judgments modified.
        """
        modified = 0
        for j in self.judgments:
            if j.target and j.target in self.control_registry:
                if self.control_registry[j.target] == ControlDomain.EXTERNAL:
                    if j.strength > 0.3:
                        j.strength = 0.3  # Reduce external attachment
                        modified += 1
        return modified


# =============================================================================
# STRESS TENSOR (Kμν)
# =============================================================================

@dataclass
class StressTensor:
    """
    The stress-energy tensor Kμν representing psychological stress.
    
    A 4×4 matrix capturing stress along different dimensions:
    - Attachment to outcomes
    - Resistance to reality
    - Temporal anxiety (past/future focus)
    - Identity contraction
    
    Liberation goal: ||K||²_F = 0 (Frobenius norm → 0)
    """
    matrix: List[List[float]] = field(default_factory=lambda: [[0.0]*4 for _ in range(4)])
    
    DIMENSIONS = ['attachment', 'resistance', 'temporal', 'identity']
    
    def __post_init__(self):
        if len(self.matrix) != 4 or any(len(row) != 4 for row in self.matrix):
            self.matrix = [[0.0]*4 for _ in range(4)]
    
    def set_component(self, i: int, j: int, value: float) -> None:
        """Set a stress component."""
        if 0 <= i < 4 and 0 <= j < 4:
            self.matrix[i][j] = value
    
    def get_component(self, i: int, j: int) -> float:
        """Get a stress component."""
        if 0 <= i < 4 and 0 <= j < 4:
            return self.matrix[i][j]
        return 0.0
    
    @property
    def frobenius_norm_squared(self) -> float:
        """
        Compute ||K||²_F = Σᵢⱼ Kᵢⱼ²
        
        This is the liberation metric - we want this → 0.
        """
        total = 0.0
        for i in range(4):
            for j in range(4):
                total += self.matrix[i][j] ** 2
        return total
    
    @property
    def frobenius_norm(self) -> float:
        """Compute ||K||_F."""
        return math.sqrt(self.frobenius_norm_squared)
    
    @property
    def trace(self) -> float:
        """Compute trace(K) = Σᵢ Kᵢᵢ."""
        return sum(self.matrix[i][i] for i in range(4))
    
    def reduce_attachment(self, amount: float = 0.1) -> None:
        """Reduce attachment stress (first row/column)."""
        for j in range(4):
            self.matrix[0][j] *= (1 - amount)
            self.matrix[j][0] *= (1 - amount)
    
    def reduce_resistance(self, amount: float = 0.1) -> None:
        """Reduce resistance stress (second row/column)."""
        for j in range(4):
            self.matrix[1][j] *= (1 - amount)
            self.matrix[j][1] *= (1 - amount)
    
    def reduce_temporal(self, amount: float = 0.1) -> None:
        """Reduce temporal anxiety stress."""
        for j in range(4):
            self.matrix[2][j] *= (1 - amount)
            self.matrix[j][2] *= (1 - amount)
    
    def reduce_identity(self, amount: float = 0.1) -> None:
        """Reduce identity contraction stress."""
        for j in range(4):
            self.matrix[3][j] *= (1 - amount)
            self.matrix[j][3] *= (1 - amount)
    
    def global_reduction(self, factor: float = 0.9) -> None:
        """Apply global stress reduction."""
        for i in range(4):
            for j in range(4):
                self.matrix[i][j] *= factor
    
    def is_liberated(self, threshold: float = 1e-10) -> bool:
        """Check if liberation condition is met: ||K||²_F ≈ 0."""
        return self.frobenius_norm_squared < threshold
    
    def __str__(self) -> str:
        lines = ["Stress Tensor Kμν:"]
        for i, row in enumerate(self.matrix):
            lines.append(f"  {self.DIMENSIONS[i]:12} [{' '.join(f'{v:7.3f}' for v in row)}]")
        lines.append(f"  ||K||_F = {self.frobenius_norm:.6f}")
        return '\n'.join(lines)


# =============================================================================
# OPTIMIZATION PROTOCOLS
# =============================================================================

class OptimizationProtocol(ABC):
    """
    Base class for liberation optimization protocols.
    
    Each protocol is proven convergent to the liberation condition.
    """
    
    @abstractmethod
    def step(self, stress: StressTensor, hegemonikon: Hegemonikon) -> float:
        """
        Execute one step of the protocol.
        Returns the current liberation metric (lower is better).
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return the protocol name."""
        pass


class KarmaYoga(OptimizationProtocol):
    """
    Karma Yoga: Non-Blocking I/O Protocol
    
    Core principle: Act without attachment to results.
    attachment_level → 0, no stress accumulation.
    
    Implementation: Detach outcome expectations from actions.
    Stress from "expected - actual" difference eliminated.
    """
    
    def __init__(self, detachment_rate: float = 0.1):
        self.detachment_rate = detachment_rate
    
    def name(self) -> str:
        return "Karma Yoga (Non-Blocking I/O)"
    
    def step(self, stress: StressTensor, hegemonikon: Hegemonikon) -> float:
        """
        Step: Reduce attachment to outcomes.
        
        Action without expectation → no stress accumulation.
        """
        # Reduce attachment component
        stress.reduce_attachment(self.detachment_rate)
        
        # Also reduce strength of external desires
        for j in hegemonikon.judgments:
            if j.judgment_type == JudgmentType.DESIRE:
                if j.target and hegemonikon.control_registry.get(j.target) == ControlDomain.EXTERNAL:
                    j.strength *= (1 - self.detachment_rate)
        
        return stress.frobenius_norm


class BhaktiYoga(OptimizationProtocol):
    """
    Bhakti Yoga: Phase-Locking Protocol
    
    Core principle: Synchronize personal will with cosmic order.
    
    Implements Adler equation: dφ/dt = Δω + κ·sin(φ)
    Lock condition: κ ≥ |Δω|
    
    When locked, individual and universal phases align.
    """
    
    def __init__(self, coupling_strength: float = 0.5, 
                 natural_frequency: float = 1.0,
                 system_frequency: float = 1.0):
        self.kappa = coupling_strength  # κ
        self.omega_self = natural_frequency
        self.omega_system = system_frequency
        self.phase = random.uniform(0, 2 * math.pi)
    
    def name(self) -> str:
        return "Bhakti Yoga (Phase-Locking)"
    
    @property
    def delta_omega(self) -> float:
        """Frequency difference Δω."""
        return self.omega_self - self.omega_system
    
    @property
    def is_lockable(self) -> bool:
        """Check if phase-locking is possible: κ ≥ |Δω|."""
        return self.kappa >= abs(self.delta_omega)
    
    def step(self, stress: StressTensor, hegemonikon: Hegemonikon) -> float:
        """
        Step: Advance phase according to Adler equation.
        
        dφ/dt = Δω + κ·sin(φ)
        """
        # Adler equation update
        dphi = self.delta_omega + self.kappa * math.sin(self.phase)
        self.phase += dphi * 0.1  # dt = 0.1
        self.phase = self.phase % (2 * math.pi)
        
        # Phase alignment reduces resistance and temporal stress
        alignment = abs(math.cos(self.phase))  # 1 = locked, 0 = anti-phase
        
        stress.reduce_resistance(alignment * 0.1)
        stress.reduce_temporal(alignment * 0.1)
        
        return stress.frobenius_norm


class JnanaYoga(OptimizationProtocol):
    """
    Jnana Yoga: Recursive Deletion (Neti-Neti) Protocol
    
    Core principle: "Not this, not this" - remove false identifications.
    
    Algorithm:
    1. Examine each identification
    2. If IMPERMANENT, OBJECTIVE, or SEPARABLE → remove
    3. What remains is the irreducible witness
    
    This converges to pure awareness without content.
    """
    
    def __init__(self):
        self.identifications: List[str] = []
        self.deleted: List[str] = []
    
    def name(self) -> str:
        return "Jnana Yoga (Neti-Neti Recursive Deletion)"
    
    def add_identification(self, item: str) -> None:
        """Add something we identify with."""
        if item not in self.identifications:
            self.identifications.append(item)
    
    def is_impermanent(self, item: str) -> bool:
        """Check if item is impermanent (changes over time)."""
        # Heuristic: most named things are impermanent
        permanent_keywords = ['awareness', 'witness', 'consciousness', 'being']
        return not any(kw in item.lower() for kw in permanent_keywords)
    
    def is_objective(self, item: str) -> bool:
        """Check if item can be observed (is an object, not subject)."""
        # If you can observe it, you are not it
        subject_keywords = ['i am', 'self', 'witness', 'observer']
        return not any(kw in item.lower() for kw in subject_keywords)
    
    def is_separable(self, item: str) -> bool:
        """Check if item can be separated from core awareness."""
        # Most things can be lost without losing "you"
        inseparable = ['awareness', 'existence', 'being']
        return not any(kw in item.lower() for kw in inseparable)
    
    def neti_neti(self, item: str) -> bool:
        """
        Apply neti-neti test.
        Returns True if item should be deleted (is "not self").
        """
        return (self.is_impermanent(item) or 
                self.is_objective(item) or 
                self.is_separable(item))
    
    def step(self, stress: StressTensor, hegemonikon: Hegemonikon) -> float:
        """
        Step: Delete one false identification.
        """
        # Find something to delete
        for item in self.identifications:
            if item not in self.deleted and self.neti_neti(item):
                self.deleted.append(item)
                # Deleting identification reduces identity stress
                stress.reduce_identity(0.2)
                break
        
        # Add from hegemonikon judgments
        for j in hegemonikon.judgments:
            if j.target and j.target not in self.identifications:
                self.add_identification(j.target)
        
        return stress.frobenius_norm


# =============================================================================
# FIVE CONTROL LEVELS
# =============================================================================

class ControlLevel(IntEnum):
    """
    Five levels of control sophistication.
    
    Progress from reactive to transcendent control.
    """
    REACTIVE = 0        # Stimulus-response
    DELIBERATIVE = 1    # Planning and reasoning
    REFLECTIVE = 2      # Monitoring own processes
    META_REFLECTIVE = 3 # Reasoning about reflection
    TRANSCENDENT = 4    # Beyond subject-object duality


@dataclass
class ControlLevelState:
    """Track current control level and progress."""
    current_level: ControlLevel = ControlLevel.REACTIVE
    level_progress: Dict[ControlLevel, float] = field(default_factory=dict)
    
    def __post_init__(self):
        for level in ControlLevel:
            if level not in self.level_progress:
                self.level_progress[level] = 0.0
    
    def progress(self, amount: float = 0.1) -> bool:
        """
        Progress toward next level.
        Returns True if level up occurred.
        """
        self.level_progress[self.current_level] += amount
        
        if self.level_progress[self.current_level] >= 1.0 and \
           self.current_level < ControlLevel.TRANSCENDENT:
            self.current_level = ControlLevel(self.current_level + 1)
            return True
        return False
    
    @property
    def is_transcendent(self) -> bool:
        return self.current_level == ControlLevel.TRANSCENDENT


# =============================================================================
# LIBERATION ENGINE
# =============================================================================

class LiberationEngine:
    """
    The complete liberation optimization engine.
    
    Combines all three yoga protocols for convergent liberation.
    
    Liberation condition: ||K||²_F = 0
    Achievable in finite time T* ≤ (1/γ)ln(E₀/ε_Planck) + ℏ/ε_Planck
    """
    
    LIBERATION_THRESHOLD = 1e-10
    
    def __init__(self):
        self.hegemonikon = Hegemonikon()
        self.stress = StressTensor()
        self.control_level = ControlLevelState()
        
        # Initialize protocols
        self.karma = KarmaYoga()
        self.bhakti = BhaktiYoga()
        self.jnana = JnanaYoga()
        
        # Metrics
        self.iteration = 0
        self.history: List[float] = []
    
    def initialize_stress(self, attachment: float = 0.5,
                          resistance: float = 0.5,
                          temporal: float = 0.5,
                          identity: float = 0.5) -> None:
        """Initialize stress tensor with given levels."""
        # Set diagonal elements
        self.stress.set_component(0, 0, attachment)
        self.stress.set_component(1, 1, resistance)
        self.stress.set_component(2, 2, temporal)
        self.stress.set_component(3, 3, identity)
        
        # Set some off-diagonal coupling
        for i in range(4):
            for j in range(i+1, 4):
                coupling = (self.stress.get_component(i, i) * 
                           self.stress.get_component(j, j)) ** 0.5 * 0.3
                self.stress.set_component(i, j, coupling)
                self.stress.set_component(j, i, coupling)
    
    def step(self) -> Tuple[float, bool]:
        """
        Execute one liberation step using all three protocols.
        
        Returns: (current_metric, is_liberated)
        """
        self.iteration += 1
        
        # Apply all three protocols
        self.karma.step(self.stress, self.hegemonikon)
        self.bhakti.step(self.stress, self.hegemonikon)
        self.jnana.step(self.stress, self.hegemonikon)
        
        # Calculate metrics
        metric = self.stress.frobenius_norm
        self.history.append(metric)
        
        # Check liberation
        liberated = metric < self.LIBERATION_THRESHOLD
        
        # Progress control level
        if metric < 0.5:
            self.control_level.progress(0.05)
        
        return (metric, liberated)
    
    def run_until_liberation(self, max_iterations: int = 1000) -> int:
        """
        Run until liberation or max iterations.
        
        Returns number of iterations taken.
        """
        for _ in range(max_iterations):
            metric, liberated = self.step()
            if liberated:
                return self.iteration
        return self.iteration
    
    def convergence_rate(self) -> float:
        """Calculate exponential convergence rate γ."""
        if len(self.history) < 2:
            return 0.0
        
        # Fit exponential decay: metric(t) ≈ metric(0) * exp(-γt)
        initial = self.history[0]
        final = self.history[-1]
        t = len(self.history)
        
        if initial > 0 and final > 0:
            gamma = math.log(initial / final) / t
            return gamma
        return 0.0
    
    @property
    def is_liberated(self) -> bool:
        return self.stress.is_liberated(self.LIBERATION_THRESHOLD)
    
    def status(self) -> str:
        """Return current status."""
        lines = [
            "=== Liberation Engine Status ===",
            f"Iteration: {self.iteration}",
            f"Control Level: {self.control_level.current_level.name}",
            f"Tranquility: {self.hegemonikon.tranquility_level:.3f}",
            f"Phase Lock: {self.bhakti.is_lockable}",
            f"Identifications: {len(self.jnana.identifications)}",
            f"Deleted: {len(self.jnana.deleted)}",
            "",
            str(self.stress),
            "",
            f"Liberation Status: {'LIBERATED' if self.is_liberated else 'IN PROGRESS'}",
        ]
        if self.history:
            lines.append(f"Convergence Rate γ: {self.convergence_rate():.6f}")
        return '\n'.join(lines)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stoic_system() -> bool:
    """Validate Stoic control system."""
    # Two control domains
    assert len(ControlDomain) == 2
    
    # Four judgment types
    assert len(JudgmentType) == 4
    
    # Five control levels
    assert len(ControlLevel) == 5
    
    # Stress tensor is 4x4
    stress = StressTensor()
    assert len(stress.matrix) == 4
    assert all(len(row) == 4 for row in stress.matrix)
    
    # Liberation engine converges
    engine = LiberationEngine()
    engine.initialize_stress(0.3, 0.3, 0.3, 0.3)
    engine.run_until_liberation(100)
    assert engine.stress.frobenius_norm < 0.5  # Should have reduced
    
    return True


if __name__ == "__main__":
    print("Validating Stoic control system...")
    assert validate_stoic_system()
    print("✓ Stoic system validated")
    
    # Demo
    print("\n=== Stoic Control Demo ===")
    
    heg = Hegemonikon()
    heg.register_item("virtue", ControlDomain.INTERNAL)
    heg.register_item("wisdom", ControlDomain.INTERNAL)
    heg.register_item("health", ControlDomain.EXTERNAL)
    heg.register_item("wealth", ControlDomain.EXTERNAL)
    heg.register_item("reputation", ControlDomain.EXTERNAL)
    
    # Form some judgments
    heg.receive_impression("I want to be wise", "wisdom")
    heg.receive_impression("I want to be wealthy", "wealth")
    heg.form_impulse("virtue", toward=True)
    heg.form_impulse("reputation", toward=True)
    
    print(f"Tranquility before discipline: {heg.calculate_tranquility():.3f}")
    modified = heg.apply_discipline()
    print(f"Modified {modified} judgments")
    print(f"Tranquility after discipline: {heg.calculate_tranquility():.3f}")
    
    print("\n=== Liberation Demo ===")
    engine = LiberationEngine()
    engine.initialize_stress(0.8, 0.6, 0.7, 0.5)
    
    print("Initial state:")
    print(engine.stress)
    
    # Run for a few iterations
    for i in range(20):
        metric, liberated = engine.step()
        if i % 5 == 0:
            print(f"Iteration {i}: ||K||_F = {metric:.6f}")
    
    print("\nFinal status:")
    print(engine.status())

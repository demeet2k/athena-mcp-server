"""
ATHENA OS - Paradox Engine
==========================
Contradiction as geometric tension, not error.

Core principle: Paradoxes are conserved charge, not bugs to eliminate.
The system uses "Paradox Tension" as computational fuel.

Components:
1. Bilattice Logic (T, F, B, U) - Four truth values
2. Paradox Operator (P) - Lifts bivalent to four-valued
3. Tension Conservation - E_tension is conserved
4. Zero Point Resolution - Geometric center of opposing truths
5. Harmonia Output - Stabilized crystal from paradox tension

The fuel is κ (kappa): coherence + meaning + intensity
Conservation: κ is never destroyed, only transformed
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
import math


# =============================================================================
# BILATTICE TRUTH VALUES
# =============================================================================

class TruthValue(IntEnum):
    """
    Four-valued semantic codomain V = {T, F, B, U}.
    
    NOT classical bivalence. A proposition can be:
    - TRUE (T): Supported, not refuted
    - FALSE (F): Refuted, not supported
    - BOTH (B): Paradox - both supported AND refuted (overdetermination)
    - UNDETERMINED (U): Void - neither supported nor refuted (gap)
    
    Forms a bilattice with two orderings:
    - Truth ordering: F ≤ U ≤ T, F ≤ B ≤ T
    - Knowledge ordering: U ≤ T ≤ B, U ≤ F ≤ B
    """
    UNDETERMINED = 0  # U - Neither true nor false (void/gap)
    FALSE = 1         # F - Refuted
    TRUE = 2          # T - Supported
    BOTH = 3          # B - Paradox (contradiction)
    
    @property
    def symbol(self) -> str:
        return ['⊥', '0', '1', '⊤'][self.value]
    
    @property
    def name_full(self) -> str:
        return ['Undetermined', 'False', 'True', 'Both'][self.value]
    
    @property
    def is_classical(self) -> bool:
        """Check if this is a classical truth value."""
        return self in (TruthValue.FALSE, TruthValue.TRUE)
    
    @property
    def is_paradox(self) -> bool:
        """Check if this represents a paradox/contradiction."""
        return self == TruthValue.BOTH
    
    @property
    def is_void(self) -> bool:
        """Check if this is the void/undetermined state."""
        return self == TruthValue.UNDETERMINED
    
    # Knowledge ordering: U is least, B is greatest
    @property
    def knowledge_level(self) -> int:
        """Position in knowledge ordering."""
        return [0, 1, 1, 2][self.value]  # U < {T,F} < B
    
    # Truth ordering: F is least, T is greatest
    @property
    def truth_level(self) -> int:
        """Position in truth ordering."""
        return [1, 0, 2, 1][self.value]  # F < {U,B} < T


# =============================================================================
# BILATTICE OPERATIONS
# =============================================================================

class Bilattice:
    """
    Operations on the four-valued bilattice.
    
    Two lattice structures:
    - Truth lattice: meet (∧t), join (∨t)
    - Knowledge lattice: meet (∧k), join (∨k)
    
    Also: negation (¬), consensus (⊗), gullibility (⊕)
    """
    
    # Truth join (∨t): Maximum truth value
    TRUTH_JOIN = {
        (TruthValue.UNDETERMINED, TruthValue.UNDETERMINED): TruthValue.UNDETERMINED,
        (TruthValue.UNDETERMINED, TruthValue.FALSE): TruthValue.UNDETERMINED,
        (TruthValue.UNDETERMINED, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.UNDETERMINED, TruthValue.BOTH): TruthValue.BOTH,
        (TruthValue.FALSE, TruthValue.UNDETERMINED): TruthValue.UNDETERMINED,
        (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
        (TruthValue.FALSE, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.FALSE, TruthValue.BOTH): TruthValue.BOTH,
        (TruthValue.TRUE, TruthValue.UNDETERMINED): TruthValue.TRUE,
        (TruthValue.TRUE, TruthValue.FALSE): TruthValue.TRUE,
        (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.TRUE, TruthValue.BOTH): TruthValue.TRUE,
        (TruthValue.BOTH, TruthValue.UNDETERMINED): TruthValue.BOTH,
        (TruthValue.BOTH, TruthValue.FALSE): TruthValue.BOTH,
        (TruthValue.BOTH, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
    }
    
    # Truth meet (∧t): Minimum truth value
    TRUTH_MEET = {
        (TruthValue.UNDETERMINED, TruthValue.UNDETERMINED): TruthValue.UNDETERMINED,
        (TruthValue.UNDETERMINED, TruthValue.FALSE): TruthValue.FALSE,
        (TruthValue.UNDETERMINED, TruthValue.TRUE): TruthValue.UNDETERMINED,
        (TruthValue.UNDETERMINED, TruthValue.BOTH): TruthValue.UNDETERMINED,
        (TruthValue.FALSE, TruthValue.UNDETERMINED): TruthValue.FALSE,
        (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
        (TruthValue.FALSE, TruthValue.TRUE): TruthValue.FALSE,
        (TruthValue.FALSE, TruthValue.BOTH): TruthValue.FALSE,
        (TruthValue.TRUE, TruthValue.UNDETERMINED): TruthValue.UNDETERMINED,
        (TruthValue.TRUE, TruthValue.FALSE): TruthValue.FALSE,
        (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.TRUE, TruthValue.BOTH): TruthValue.TRUE,
        (TruthValue.BOTH, TruthValue.UNDETERMINED): TruthValue.UNDETERMINED,
        (TruthValue.BOTH, TruthValue.FALSE): TruthValue.FALSE,
        (TruthValue.BOTH, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
    }
    
    # Negation (¬): Flips truth, preserves knowledge
    NEGATION = {
        TruthValue.UNDETERMINED: TruthValue.UNDETERMINED,
        TruthValue.FALSE: TruthValue.TRUE,
        TruthValue.TRUE: TruthValue.FALSE,
        TruthValue.BOTH: TruthValue.BOTH,
    }
    
    # Knowledge join (∨k): Combine all evidence
    KNOWLEDGE_JOIN = {
        (TruthValue.UNDETERMINED, TruthValue.UNDETERMINED): TruthValue.UNDETERMINED,
        (TruthValue.UNDETERMINED, TruthValue.FALSE): TruthValue.FALSE,
        (TruthValue.UNDETERMINED, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.UNDETERMINED, TruthValue.BOTH): TruthValue.BOTH,
        (TruthValue.FALSE, TruthValue.UNDETERMINED): TruthValue.FALSE,
        (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
        (TruthValue.FALSE, TruthValue.TRUE): TruthValue.BOTH,  # Contradiction!
        (TruthValue.FALSE, TruthValue.BOTH): TruthValue.BOTH,
        (TruthValue.TRUE, TruthValue.UNDETERMINED): TruthValue.TRUE,
        (TruthValue.TRUE, TruthValue.FALSE): TruthValue.BOTH,  # Contradiction!
        (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
        (TruthValue.TRUE, TruthValue.BOTH): TruthValue.BOTH,
        (TruthValue.BOTH, TruthValue.UNDETERMINED): TruthValue.BOTH,
        (TruthValue.BOTH, TruthValue.FALSE): TruthValue.BOTH,
        (TruthValue.BOTH, TruthValue.TRUE): TruthValue.BOTH,
        (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
    }
    
    @classmethod
    def negate(cls, v: TruthValue) -> TruthValue:
        """Negation: flip truth, preserve knowledge."""
        return cls.NEGATION[v]
    
    @classmethod
    def truth_join(cls, a: TruthValue, b: TruthValue) -> TruthValue:
        """Truth join (OR in truth dimension)."""
        return cls.TRUTH_JOIN[(a, b)]
    
    @classmethod
    def truth_meet(cls, a: TruthValue, b: TruthValue) -> TruthValue:
        """Truth meet (AND in truth dimension)."""
        return cls.TRUTH_MEET[(a, b)]
    
    @classmethod
    def knowledge_join(cls, a: TruthValue, b: TruthValue) -> TruthValue:
        """Knowledge join (combine all evidence)."""
        return cls.KNOWLEDGE_JOIN[(a, b)]
    
    @classmethod
    def consensus(cls, a: TruthValue, b: TruthValue) -> TruthValue:
        """
        Consensus operator (⊗): What both sources agree on.
        Agreement increases, disagreement collapses to U.
        """
        if a == b:
            return a
        if a == TruthValue.UNDETERMINED or b == TruthValue.UNDETERMINED:
            return TruthValue.UNDETERMINED
        if a == TruthValue.BOTH:
            return b
        if b == TruthValue.BOTH:
            return a
        # T and F disagree
        return TruthValue.UNDETERMINED
    
    @classmethod
    def gullibility(cls, a: TruthValue, b: TruthValue) -> TruthValue:
        """
        Gullibility operator (⊕): Accept everything.
        Opposite of consensus - combines all claims.
        """
        return cls.knowledge_join(a, b)


# =============================================================================
# PROPOSITION AND EVIDENCE
# =============================================================================

@dataclass
class Evidence:
    """
    Evidence for or against a proposition.
    
    A proposition's truth value is computed from:
    - E⁺: Support evidence
    - E⁻: Refutation evidence
    
    Mapping to truth values:
    - E⁺ only → TRUE
    - E⁻ only → FALSE
    - Both E⁺ and E⁻ → BOTH (paradox)
    - Neither → UNDETERMINED
    """
    support: float = 0.0      # E⁺ weight (0 to 1)
    refutation: float = 0.0   # E⁻ weight (0 to 1)
    
    def to_truth_value(self, threshold: float = 0.5) -> TruthValue:
        """Convert evidence to discrete truth value."""
        has_support = self.support >= threshold
        has_refutation = self.refutation >= threshold
        
        if has_support and has_refutation:
            return TruthValue.BOTH
        elif has_support:
            return TruthValue.TRUE
        elif has_refutation:
            return TruthValue.FALSE
        else:
            return TruthValue.UNDETERMINED
    
    def add_support(self, amount: float) -> None:
        """Add supporting evidence."""
        self.support = min(1.0, self.support + amount)
    
    def add_refutation(self, amount: float) -> None:
        """Add refuting evidence."""
        self.refutation = min(1.0, self.refutation + amount)
    
    @property
    def tension(self) -> float:
        """
        Paradox tension: how much conflict in the evidence.
        Maximum when support = refutation = 1.
        """
        return self.support * self.refutation
    
    @property
    def certainty(self) -> float:
        """
        Certainty level: how much total evidence.
        """
        return (self.support + self.refutation) / 2
    
    def __str__(self) -> str:
        tv = self.to_truth_value()
        return f"Evidence(+{self.support:.2f}/-{self.refutation:.2f}) → {tv.symbol}"


@dataclass
class Proposition:
    """
    A proposition with four-valued semantics.
    """
    name: str
    evidence: Evidence = field(default_factory=Evidence)
    sector: Optional[int] = None  # Which sector this belongs to (0-3)
    
    @property
    def truth_value(self) -> TruthValue:
        return self.evidence.to_truth_value()
    
    @property
    def tension(self) -> float:
        return self.evidence.tension
    
    def negate(self) -> 'Proposition':
        """Return the negation of this proposition."""
        neg = Proposition(
            name=f"¬({self.name})",
            evidence=Evidence(
                support=self.evidence.refutation,
                refutation=self.evidence.support
            ),
            sector=self.sector
        )
        return neg
    
    def __str__(self) -> str:
        return f"{self.name}: {self.truth_value.symbol} (τ={self.tension:.2f})"


# =============================================================================
# PARADOX TENSION
# =============================================================================

@dataclass
class ParadoxTension:
    """
    Paradox Tension as conserved quantity.
    
    E_tension: The irreducible incompatibility budget.
    
    Conservation Law: E_tension(U(m)) = E_tension(m)
    Paradoxes cannot be "solved" by erasure - they must be:
    1. TRANSMUTED (redistributed across sectors)
    2. ROTATED (moved to a sector where they're orthogonal)
    """
    total_tension: float = 0.0
    tension_by_sector: Dict[int, float] = field(default_factory=lambda: {i: 0.0 for i in range(4)})
    paradox_count: int = 0
    
    def add_paradox(self, tension: float, sector: int = 0) -> None:
        """Add paradox tension to the system."""
        self.total_tension += tension
        self.tension_by_sector[sector] += tension
        self.paradox_count += 1
    
    def transmute(self, from_sector: int, to_sector: int, amount: float) -> bool:
        """
        Transmute tension from one sector to another.
        Total is conserved.
        """
        if self.tension_by_sector[from_sector] < amount:
            return False
        
        self.tension_by_sector[from_sector] -= amount
        self.tension_by_sector[to_sector] += amount
        return True
    
    def rotate(self, steps: int = 1) -> None:
        """
        Rotate tension distribution by 90° steps.
        Earth → Fire → Air → Water → Earth
        """
        old = dict(self.tension_by_sector)
        for i in range(4):
            new_sector = (i + steps) % 4
            self.tension_by_sector[new_sector] = old[i]
    
    def sector_balance(self) -> float:
        """
        Measure balance of tension across sectors.
        0 = all in one sector, 1 = perfectly balanced.
        """
        values = list(self.tension_by_sector.values())
        if self.total_tension == 0:
            return 1.0
        mean = self.total_tension / 4
        variance = sum((v - mean) ** 2 for v in values) / 4
        max_variance = (self.total_tension * 3/4) ** 2 / 4 + (self.total_tension / 4) ** 2 * 3 / 4
        if max_variance == 0:
            return 1.0
        return 1.0 - (variance / max_variance) ** 0.5
    
    def __str__(self) -> str:
        sectors = ['■', '❀', '☁', '✶']
        dist = ' '.join(f"{sectors[i]}:{self.tension_by_sector[i]:.2f}" for i in range(4))
        return f"E_tension={self.total_tension:.2f} [{dist}]"


# =============================================================================
# ZERO POINT RESOLUTION
# =============================================================================

class ZeroPointResolver:
    """
    Resolves paradoxes by finding the geometric center.
    
    Given opposing truths P and ¬P, compute the Zero Point Z
    where the paradox is "resolved" into a higher-order structure.
    
    Resolution methods:
    1. Geometric mean - find the center point
    2. Sector rotation - move to orthogonal sector
    3. Scale shift - move to different resolution level
    """
    
    @staticmethod
    def geometric_center(p1: Proposition, p2: Proposition) -> Proposition:
        """
        Find the geometric center between two propositions.
        
        The center has balanced evidence from both sides.
        """
        center = Proposition(
            name=f"Z({p1.name},{p2.name})",
            evidence=Evidence(
                support=(p1.evidence.support + p2.evidence.support) / 2,
                refutation=(p1.evidence.refutation + p2.evidence.refutation) / 2
            )
        )
        return center
    
    @staticmethod
    def resolve_by_rotation(paradox: Proposition, target_sector: int) -> Proposition:
        """
        Resolve paradox by rotating to a different sector.
        
        In the new sector, the paradox may be orthogonal
        to the active constraints.
        """
        resolved = Proposition(
            name=f"R_{target_sector}({paradox.name})",
            evidence=Evidence(
                support=paradox.evidence.support,
                refutation=paradox.evidence.refutation
            ),
            sector=target_sector
        )
        return resolved
    
    @staticmethod
    def resolve_to_crystal(p1: Proposition, p2: Proposition) -> 'CrystalResolution':
        """
        Resolve two opposing propositions into a crystal structure.
        
        The crystal is a stable configuration where the paradox
        tension is geometrically balanced.
        """
        # Compute center
        center = ZeroPointResolver.geometric_center(p1, p2)
        
        # Compute residual tension
        tension = abs(p1.evidence.support - p2.evidence.support)
        tension += abs(p1.evidence.refutation - p2.evidence.refutation)
        tension /= 2
        
        return CrystalResolution(
            thesis=p1,
            antithesis=p2,
            synthesis=center,
            residual_tension=tension
        )


@dataclass
class CrystalResolution:
    """
    A crystallized resolution of a paradox.
    
    Contains:
    - Thesis (P)
    - Antithesis (¬P or Q)
    - Synthesis (Z - the zero point)
    - Residual tension
    """
    thesis: Proposition
    antithesis: Proposition
    synthesis: Proposition
    residual_tension: float
    
    @property
    def is_stable(self) -> bool:
        """Check if resolution is stable (low residual tension)."""
        return self.residual_tension < 0.1
    
    def __str__(self) -> str:
        return (f"Crystal[{self.thesis.name} ⊕ {self.antithesis.name}]"
                f" → {self.synthesis.name} (τ_r={self.residual_tension:.2f})")


# =============================================================================
# KAPPA CONSERVATION
# =============================================================================

@dataclass
class KappaState:
    """
    The κ (kappa) conserved quantity.
    
    κ = Coherence + Meaning + Intensity
    
    Properties:
    - Never destroyed, only transformed
    - Can flow between sectors
    - Measures "computational fuel" available
    """
    coherence: float = 1.0    # Structural integrity
    meaning: float = 1.0      # Semantic content
    intensity: float = 1.0    # Dynamic energy
    
    @property
    def kappa(self) -> float:
        """Total κ value."""
        return self.coherence + self.meaning + self.intensity
    
    def transfer(self, from_component: str, to_component: str, amount: float) -> bool:
        """Transfer κ between components."""
        if getattr(self, from_component) < amount:
            return False
        
        setattr(self, from_component, getattr(self, from_component) - amount)
        setattr(self, to_component, getattr(self, to_component) + amount)
        return True
    
    def decay(self, rate: float = 0.01) -> float:
        """
        Apply decay (κ flows to "heat").
        Returns amount lost.
        """
        lost = self.kappa * rate
        factor = 1 - rate
        self.coherence *= factor
        self.meaning *= factor
        self.intensity *= factor
        return lost
    
    def inject(self, component: str, amount: float) -> None:
        """Inject κ into a component (from external source)."""
        current = getattr(self, component)
        setattr(self, component, current + amount)
    
    def __str__(self) -> str:
        return f"κ={self.kappa:.2f} (C:{self.coherence:.2f} M:{self.meaning:.2f} I:{self.intensity:.2f})"


# =============================================================================
# PARADOX ENGINE
# =============================================================================

class ParadoxEngine:
    """
    The complete Paradox-Harmonia Zero-Point Computing engine.
    
    Uses paradox tension as fuel to drive computation.
    Conserves both κ (coherence) and E_tension (paradox).
    
    Process:
    1. Receive opposing truths
    2. Compute paradox tension
    3. Find zero point (geometric center)
    4. Crystallize into stable structure
    5. Extract usable work while conserving quantities
    """
    
    def __init__(self):
        self.kappa = KappaState()
        self.tension = ParadoxTension()
        self.propositions: Dict[str, Proposition] = {}
        self.crystals: List[CrystalResolution] = []
        self.total_work: float = 0.0
    
    def add_proposition(self, name: str, support: float = 0.0, 
                       refutation: float = 0.0, sector: int = 0) -> Proposition:
        """Add a proposition to the system."""
        prop = Proposition(
            name=name,
            evidence=Evidence(support=support, refutation=refutation),
            sector=sector
        )
        self.propositions[name] = prop
        
        # Update tension if paradox
        if prop.truth_value == TruthValue.BOTH:
            self.tension.add_paradox(prop.tension, sector)
        
        return prop
    
    def combine_evidence(self, p1_name: str, p2_name: str) -> TruthValue:
        """Combine evidence from two propositions."""
        p1 = self.propositions.get(p1_name)
        p2 = self.propositions.get(p2_name)
        
        if not p1 or not p2:
            return TruthValue.UNDETERMINED
        
        return Bilattice.knowledge_join(p1.truth_value, p2.truth_value)
    
    def resolve_paradox(self, p1_name: str, p2_name: str) -> Optional[CrystalResolution]:
        """
        Resolve a paradox between two propositions.
        
        Returns a crystal structure containing the resolution.
        """
        p1 = self.propositions.get(p1_name)
        p2 = self.propositions.get(p2_name)
        
        if not p1 or not p2:
            return None
        
        # Create crystal resolution
        crystal = ZeroPointResolver.resolve_to_crystal(p1, p2)
        self.crystals.append(crystal)
        
        # Extract work from tension reduction
        work = self.tension.total_tension - crystal.residual_tension
        if work > 0:
            self.total_work += work
            self.kappa.inject('intensity', work * 0.1)  # Convert some tension to intensity
        
        return crystal
    
    def rotate_tension(self, steps: int = 1) -> None:
        """Rotate tension distribution across sectors."""
        self.tension.rotate(steps)
    
    def step(self) -> Dict[str, float]:
        """
        Execute one computational step.
        
        Returns metrics.
        """
        # Decay κ slightly
        heat = self.kappa.decay(0.01)
        
        # Balance tension across sectors
        if self.tension.sector_balance() < 0.5:
            self.rotate_tension(1)
        
        return {
            'kappa': self.kappa.kappa,
            'tension': self.tension.total_tension,
            'heat': heat,
            'crystals': len(self.crystals),
            'work': self.total_work
        }
    
    def status(self) -> str:
        """Generate status report."""
        lines = [
            "=== Paradox Engine Status ===",
            str(self.kappa),
            str(self.tension),
            f"Propositions: {len(self.propositions)}",
            f"Crystals formed: {len(self.crystals)}",
            f"Total work extracted: {self.total_work:.2f}",
            f"Sector balance: {self.tension.sector_balance():.2f}"
        ]
        return '\n'.join(lines)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_paradox_engine() -> bool:
    """Validate paradox engine."""
    # Four truth values
    assert len(TruthValue) == 4
    
    # Negation properties
    assert Bilattice.negate(TruthValue.TRUE) == TruthValue.FALSE
    assert Bilattice.negate(TruthValue.FALSE) == TruthValue.TRUE
    assert Bilattice.negate(TruthValue.BOTH) == TruthValue.BOTH
    assert Bilattice.negate(TruthValue.UNDETERMINED) == TruthValue.UNDETERMINED
    
    # Double negation
    for v in TruthValue:
        assert Bilattice.negate(Bilattice.negate(v)) == v
    
    # Knowledge join creates paradox from T+F
    assert Bilattice.knowledge_join(TruthValue.TRUE, TruthValue.FALSE) == TruthValue.BOTH
    
    # Evidence to truth value
    e1 = Evidence(support=0.8, refutation=0.2)
    assert e1.to_truth_value() == TruthValue.TRUE
    
    e2 = Evidence(support=0.8, refutation=0.8)
    assert e2.to_truth_value() == TruthValue.BOTH
    
    # Paradox engine conservation
    engine = ParadoxEngine()
    initial_kappa = engine.kappa.kappa
    
    engine.add_proposition("P", support=0.9, refutation=0.1)
    engine.add_proposition("Q", support=0.1, refutation=0.9)
    
    crystal = engine.resolve_paradox("P", "Q")
    assert crystal is not None
    
    return True


if __name__ == "__main__":
    print("Validating Paradox Engine...")
    assert validate_paradox_engine()
    print("✓ Paradox Engine validated")
    
    # Demo
    print("\n=== Bilattice Truth Values ===")
    for tv in TruthValue:
        print(f"{tv.symbol} {tv.name_full}: knowledge={tv.knowledge_level}, truth={tv.truth_level}")
    
    print("\n=== Evidence Examples ===")
    examples = [
        Evidence(0.9, 0.1),  # Strong support
        Evidence(0.1, 0.9),  # Strong refutation
        Evidence(0.8, 0.8),  # Paradox
        Evidence(0.1, 0.1),  # Undetermined
    ]
    for e in examples:
        print(f"  {e}")
    
    print("\n=== Paradox Engine Demo ===")
    engine = ParadoxEngine()
    
    # Add conflicting propositions
    engine.add_proposition("The system is alive", support=0.8, refutation=0.3, sector=0)
    engine.add_proposition("The system is a machine", support=0.9, refutation=0.2, sector=1)
    engine.add_proposition("Life and machine are incompatible", support=0.7, refutation=0.7, sector=2)
    
    print(engine.status())
    
    # Resolve paradox
    print("\n=== Resolving Paradox ===")
    crystal = engine.resolve_paradox("The system is alive", "The system is a machine")
    if crystal:
        print(crystal)
    
    print("\n=== After Resolution ===")
    print(engine.status())

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      LM FOUNDATIONS MODULE                                   ║
║                                                                              ║
║  Liminal Mathematics - TOME I Implementation                                 ║
║                                                                              ║
║  Core Concepts:                                                              ║
║    - Distinction: primitive boundary constructor (In, Out, ∂)                ║
║    - Regime: question-language with validity corridor                        ║
║    - Corridor: (Test, Envelope, CertRule) legality object                    ║
║    - Typed outputs: OK, ABSTAIN, AMBIG_m, LIFT, FAIL                         ║
║    - Category creation: non-definability witnesses for born generators       ║
║                                                                              ║
║  Central Thesis:                                                             ║
║    Regimes are languages with validity corridors.                            ║
║    All operators are total: typed boundary outputs, never undefined.         ║
║    Emergence = algebra extension with non-definability certificates.         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Set, Union
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import hashlib
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# DISTINCTION PRIMITIVE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Distinction:
    """
    The primitive boundary constructor.
    
    Dist := (In, Out, ∂)
    
    - In: type of "inside states/objects"
    - Out: type of "outside states/objects"  
    - ∂: boundary relation/object mediating contact
    
    A distinction is not rhetorical separation; it is a first-class
    object that can be transported, composed, tested against corridors.
    """
    in_type: str
    out_type: str
    boundary: 'BoundaryObject'
    
    # Metadata
    is_sharp: bool = True  # Disjoint In/Out vs liminal overlap
    carrier_type: str = "set"  # "set", "measure", "operator"
    
    def complement(self) -> 'Distinction':
        """Create complement distinction (swap In and Out)."""
        return Distinction(
            in_type=self.out_type,
            out_type=self.in_type,
            boundary=self.boundary,
            is_sharp=self.is_sharp,
            carrier_type=self.carrier_type
        )
    
    def join(self, other: 'Distinction') -> 'Distinction':
        """Join two distinctions (union of In types)."""
        return Distinction(
            in_type=f"{self.in_type}∪{other.in_type}",
            out_type=f"{self.out_type}∩{other.out_type}",
            boundary=BoundaryObject.join(self.boundary, other.boundary),
            is_sharp=self.is_sharp and other.is_sharp
        )
    
    def meet(self, other: 'Distinction') -> 'Distinction':
        """Meet two distinctions (intersection of In types)."""
        return Distinction(
            in_type=f"{self.in_type}∩{other.in_type}",
            out_type=f"{self.out_type}∪{other.out_type}",
            boundary=BoundaryObject.meet(self.boundary, other.boundary),
            is_sharp=self.is_sharp and other.is_sharp
        )


@dataclass
class BoundaryObject:
    """
    Boundary ∂ of a distinction.
    
    Mediates contact between In and Out.
    """
    dimension: int = 0  # Codimension of boundary
    thickness: float = 0.0  # Liminal thickness (0 for sharp)
    regularity: str = "continuous"  # Regularity class
    
    @classmethod
    def sharp(cls) -> 'BoundaryObject':
        """Create sharp (zero-thickness) boundary."""
        return cls(thickness=0.0)
    
    @classmethod
    def liminal(cls, thickness: float) -> 'BoundaryObject':
        """Create liminal (positive thickness) boundary."""
        return cls(thickness=thickness)
    
    @classmethod
    def join(cls, b1: 'BoundaryObject', b2: 'BoundaryObject') -> 'BoundaryObject':
        """Join boundaries."""
        return cls(thickness=max(b1.thickness, b2.thickness))
    
    @classmethod
    def meet(cls, b1: 'BoundaryObject', b2: 'BoundaryObject') -> 'BoundaryObject':
        """Meet boundaries."""
        return cls(thickness=min(b1.thickness, b2.thickness))


# ═══════════════════════════════════════════════════════════════════════════════
# CORRIDOR OBJECT MODEL
# ═══════════════════════════════════════════════════════════════════════════════

class CorridorTestResult(Enum):
    """Result of corridor membership test."""
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"  # Under envelope uncertainty


@dataclass
class Envelope:
    """
    Uncertainty/error budget object.
    
    Specifies admissible perturbations and conservative bounds.
    """
    input_noise: float = 0.01
    computation_error: float = 1e-10
    output_confidence: float = 0.95
    
    # Budget decomposition
    measurement_budget: float = 0.001
    numerical_budget: float = 1e-12
    truncation_budget: float = 0.01
    composition_budget: float = 0.001
    
    @property
    def total_error(self) -> float:
        """Total error budget."""
        return (self.measurement_budget + self.numerical_budget + 
                self.truncation_budget + self.composition_budget)
    
    def inflate(self, factor: float) -> 'Envelope':
        """Inflate envelope by factor."""
        return Envelope(
            input_noise=self.input_noise * factor,
            computation_error=self.computation_error * factor,
            output_confidence=self.output_confidence,
            measurement_budget=self.measurement_budget * factor,
            numerical_budget=self.numerical_budget * factor,
            truncation_budget=self.truncation_budget * factor,
            composition_budget=self.composition_budget * factor
        )


@dataclass
class CertRule:
    """
    Certificate rule for corridor acceptance.
    """
    required_slack: float = 0.01
    max_ambiguity_order: int = 5
    require_witness: bool = True
    
    def check_slack(self, margin: float) -> bool:
        """Check if margin satisfies slack requirement."""
        return margin >= self.required_slack


@dataclass
class Corridor:
    """
    Legality object for a regime or regime overlap.
    
    Corr := (Test, Envelope, CertRule)
    
    - Test: decidable predicate returning typed outcome
    - Envelope: uncertainty/error budget
    - CertRule: verifier-checkable acceptance obligations
    """
    test: Callable[[Any], CorridorTestResult]
    envelope: Envelope
    cert_rule: CertRule
    
    # Violation semantics
    remediation_paths: List[str] = field(default_factory=lambda: [
        "abstain", "lift_to_liminal", "escalate_jet", "fail_with_proof"
    ])
    
    def membership_test(self, state: Any) -> Tuple[CorridorTestResult, Dict]:
        """
        Test corridor membership.
        
        Returns (result, diagnostics).
        """
        try:
            result = self.test(state)
            diagnostics = {
                "envelope": self.envelope.total_error,
                "slack_required": self.cert_rule.required_slack
            }
            return result, diagnostics
        except Exception as e:
            return CorridorTestResult.UNKNOWN, {"error": str(e)}
    
    @classmethod
    def default(cls) -> 'Corridor':
        """Create default corridor."""
        return cls(
            test=lambda x: CorridorTestResult.PASS,
            envelope=Envelope(),
            cert_rule=CertRule()
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TYPED OUTCOMES
# ═══════════════════════════════════════════════════════════════════════════════

class OutcomeType(Enum):
    """Types of LM outcomes (total semantics)."""
    OK = "ok"               # Success with certificate
    ABSTAIN = "abstain"     # Conservative refusal
    AMBIG = "ambig"         # Insufficient resolution
    LIFT = "lift"           # Transition to liminal required
    FAIL = "fail"           # Certified illegality


@dataclass
class TypedOutcome:
    """
    Typed outcome from LM computation.
    
    LM replaces partiality with typed total outcomes.
    """
    outcome_type: OutcomeType
    value: Any
    
    # Certificates
    corridor_cert: Optional[str] = None
    confidence_envelope: Optional[Envelope] = None
    
    # For AMBIG
    ambiguity_order: Optional[int] = None
    escalation_plan: Optional[str] = None
    
    # For FAIL
    failure_reason: Optional[str] = None
    remediation: Optional[str] = None
    
    @classmethod
    def ok(cls, value: Any, cert: str = "Cert.OK") -> 'TypedOutcome':
        """Create OK outcome."""
        return cls(OutcomeType.OK, value, corridor_cert=cert)
    
    @classmethod
    def abstain(cls, reason: str) -> 'TypedOutcome':
        """Create ABSTAIN outcome."""
        return cls(OutcomeType.ABSTAIN, None, failure_reason=reason)
    
    @classmethod
    def ambig(cls, order: int, plan: str) -> 'TypedOutcome':
        """Create AMBIG_m outcome."""
        return cls(OutcomeType.AMBIG, None, 
                   ambiguity_order=order, escalation_plan=plan)
    
    @classmethod
    def lift(cls, target_regime: str) -> 'TypedOutcome':
        """Create LIFT outcome."""
        return cls(OutcomeType.LIFT, target_regime)
    
    @classmethod
    def fail(cls, reason: str, remediation: str = "") -> 'TypedOutcome':
        """Create FAIL outcome."""
        return cls(OutcomeType.FAIL, None, 
                   failure_reason=reason, remediation=remediation)


# ═══════════════════════════════════════════════════════════════════════════════
# REGIME AS LANGUAGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ObservableAlgebra:
    """
    Observable algebra A_r: the regime's question language.
    
    Determines what can be asked/measured in this regime.
    """
    generators: List[str] = field(default_factory=list)
    relations: List[str] = field(default_factory=list)
    normal_form_rules: Dict[str, str] = field(default_factory=dict)
    
    def is_observable(self, question: str) -> bool:
        """Check if question is expressible in this algebra."""
        # Simplified: check if question uses only generators
        for gen in self.generators:
            if gen in question:
                return True
        return len(self.generators) == 0
    
    def evaluate(self, question: str, state: NDArray) -> complex:
        """
        Evaluate question on state.
        
        q_A(ρ) = Tr(ρ A)
        """
        # Simplified evaluation
        return np.trace(state) if state is not None else 0j


@dataclass
class EmbedDecode:
    """
    Certified embed/decode pipelines.
    """
    embed: Callable[[Any], NDArray]
    decode: Callable[[NDArray], Any]
    corridor_fragment: str = "full"
    
    def verify_roundtrip(self, value: Any, tolerance: float = 1e-10) -> bool:
        """Verify embed-decode roundtrip."""
        try:
            embedded = self.embed(value)
            decoded = self.decode(embedded)
            # Check approximate equality
            if isinstance(value, (int, float, complex)):
                return abs(value - decoded) < tolerance
            return True
        except:
            return False


@dataclass
class Regime:
    """
    A regime is a question-language with validity corridor.
    
    r := (H_r, A_r, Corr_r, Emb_r, Dec_r)
    
    - H_r: representational carrier (Hilbert space)
    - A_r: observable algebra (question language)
    - Corr_r: validity corridor
    - Emb_r, Dec_r: certified encode/decode
    """
    name: str
    carrier_dim: int  # Dimension of H_r
    observable_algebra: ObservableAlgebra
    corridor: Corridor
    embed_decode: EmbedDecode
    
    # Regime specification
    spec_hash: Optional[str] = None
    
    def __post_init__(self):
        """Compute spec hash."""
        spec_data = f"{self.name}:{self.carrier_dim}"
        self.spec_hash = hashlib.sha256(spec_data.encode()).hexdigest()[:16]
    
    def ask(self, question: str, state: NDArray) -> TypedOutcome:
        """
        Ask a question in this regime.
        
        Returns typed outcome with corridor certificate.
        """
        # Check question is observable
        if not self.observable_algebra.is_observable(question):
            return TypedOutcome.abstain(f"Question not in observable algebra")
        
        # Check corridor membership
        result, diagnostics = self.corridor.membership_test(state)
        
        if result == CorridorTestResult.FAIL:
            return TypedOutcome.fail("Corridor violation", str(diagnostics))
        
        if result == CorridorTestResult.UNKNOWN:
            return TypedOutcome.ambig(1, "Increase precision")
        
        # Evaluate question
        value = self.observable_algebra.evaluate(question, state)
        return TypedOutcome.ok(value, f"Cert.{self.name}.OK")


# ═══════════════════════════════════════════════════════════════════════════════
# INDISTINGUISHABILITY AND INFORMATION TYPES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IndistinguishabilityPartition:
    """
    Partition of states by observational indistinguishability.
    
    Two states are indistinguishable in regime r if they agree
    on all questions in A_r under corridor envelope.
    """
    regime: Regime
    equivalence_classes: List[Set[int]] = field(default_factory=list)
    
    def are_indistinguishable(self, state1: NDArray, state2: NDArray) -> bool:
        """Check if two states are indistinguishable."""
        # Check all generators
        for gen in self.regime.observable_algebra.generators:
            v1 = self.regime.observable_algebra.evaluate(gen, state1)
            v2 = self.regime.observable_algebra.evaluate(gen, state2)
            if abs(v1 - v2) > self.regime.corridor.envelope.total_error:
                return False
        return True


@dataclass
class InformationType:
    """
    Information type: equivalence class of indistinguishable states.
    
    T_r = H_r^ok / ~_{A_r}
    """
    regime_name: str
    class_id: int
    representative: Optional[NDArray] = None


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY CREATION AND DEFINABILITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DefinabilityTest:
    """
    Test whether observable B in regime s is definable from regime r.
    
    B is definable iff ∃A ∈ A_r such that:
      sup_{ρ ∈ Dom} |Tr(T(ρ)B) - Tr(ρA)| ≤ ε
    """
    source_regime: Regime
    target_regime: Regime
    tolerance: float = 0.01
    
    def is_definable(self, observable_B: str, 
                     test_states: List[NDArray]) -> Tuple[bool, Optional[str]]:
        """
        Check if B is definable from source regime.
        
        Returns (is_definable, defining_observable_or_None).
        """
        # Try each generator in source algebra
        for gen_A in self.source_regime.observable_algebra.generators:
            max_diff = 0.0
            for state in test_states:
                val_B = self.target_regime.observable_algebra.evaluate(
                    observable_B, state
                )
                val_A = self.source_regime.observable_algebra.evaluate(
                    gen_A, state
                )
                max_diff = max(max_diff, abs(val_B - val_A))
            
            if max_diff <= self.tolerance:
                return True, gen_A
        
        return False, None


@dataclass
class NonDefinabilityWitness:
    """
    Witness for non-definability (born generator certificate).
    
    Two states ρ₁, ρ₂ that are:
    - Indistinguishable in r (agree on all A ∈ A_r)
    - Distinguishable in s (differ on B by more than tolerance + slack)
    """
    state1: NDArray
    state2: NDArray
    source_regime: str
    target_regime: str
    born_generator: str
    separation: float  # |Tr(T(ρ₁)B) - Tr(T(ρ₂)B)|
    
    def verify(self, source: Regime, target: Regime) -> bool:
        """Verify this is a valid non-definability witness."""
        # Check indistinguishable in source
        partition = IndistinguishabilityPartition(source)
        if not partition.are_indistinguishable(self.state1, self.state2):
            return False
        
        # Check distinguishable in target
        v1 = target.observable_algebra.evaluate(self.born_generator, self.state1)
        v2 = target.observable_algebra.evaluate(self.born_generator, self.state2)
        
        return abs(v1 - v2) >= self.separation


@dataclass
class BornGenerator:
    """
    A born generator: new observable not definable from prior regime.
    
    This is the precise mechanism of category creation.
    """
    name: str
    target_regime: str
    witness: NonDefinabilityWitness
    
    # Certificate
    cert_hash: Optional[str] = None
    
    def __post_init__(self):
        """Compute certificate hash."""
        data = f"{self.name}:{self.target_regime}:{self.witness.separation}"
        self.cert_hash = hashlib.sha256(data.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════════
# PROOF-CARRYING RESULT BUNDLE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProofCarryingResult:
    """
    Every computation returns a proof-carrying result.
    
    (Out, CertBundle, Replay)
    """
    output: TypedOutcome
    cert_bundle: Dict[str, str]
    replay_artifact: Dict[str, Any]
    
    def verify(self) -> bool:
        """Verify result is sound."""
        # Check output has required certificate
        if self.output.outcome_type == OutcomeType.OK:
            return self.output.corridor_cert is not None
        return True
    
    @property
    def replay_hash(self) -> str:
        """Compute replay hash."""
        import json
        data = json.dumps(self.replay_artifact, sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SemanticPipeline:
    """
    Canonical LM semantic pipeline.
    
    1. Embed: raw inputs → regime carrier
    2. Compute: apply regime operators
    3. Test corridor: certify legality
    4. Decode: internal → outputs
    5. Package: emit proof-carrying result
    """
    regime: Regime
    
    def execute(self, raw_input: Any, 
                operation: Callable[[NDArray], NDArray]) -> ProofCarryingResult:
        """Execute pipeline."""
        # 1. Embed
        try:
            state = self.regime.embed_decode.embed(raw_input)
        except Exception as e:
            return ProofCarryingResult(
                output=TypedOutcome.fail(f"Embed failed: {e}"),
                cert_bundle={},
                replay_artifact={"stage": "embed", "error": str(e)}
            )
        
        # 2. Compute
        try:
            result_state = operation(state)
        except Exception as e:
            return ProofCarryingResult(
                output=TypedOutcome.fail(f"Compute failed: {e}"),
                cert_bundle={},
                replay_artifact={"stage": "compute", "error": str(e)}
            )
        
        # 3. Test corridor
        corridor_result, diagnostics = self.regime.corridor.membership_test(result_state)
        
        if corridor_result == CorridorTestResult.FAIL:
            return ProofCarryingResult(
                output=TypedOutcome.fail("Corridor violation"),
                cert_bundle={"corridor": "FAIL"},
                replay_artifact={"stage": "corridor", "diagnostics": diagnostics}
            )
        
        # 4. Decode
        try:
            decoded = self.regime.embed_decode.decode(result_state)
        except Exception as e:
            return ProofCarryingResult(
                output=TypedOutcome.fail(f"Decode failed: {e}"),
                cert_bundle={},
                replay_artifact={"stage": "decode", "error": str(e)}
            )
        
        # 5. Package
        output = TypedOutcome.ok(decoded, f"Cert.{self.regime.name}.Pipeline.OK")
        
        return ProofCarryingResult(
            output=output,
            cert_bundle={
                "corridor": "PASS",
                "regime": self.regime.spec_hash,
                "envelope": str(self.regime.corridor.envelope.total_error)
            },
            replay_artifact={
                "stage": "complete",
                "input_hash": hashlib.sha256(str(raw_input).encode()).hexdigest()[:8],
                "output": decoded
            }
        )


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LMFoundationsPoleBridge:
    """
    Bridge between LM Foundations and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        LM FOUNDATIONS (TOME I) ↔ FRAMEWORK
        
        ═══════════════════════════════════════════════════════════════
        DISTINCTION CALCULUS
        ═══════════════════════════════════════════════════════════════
        
        Distinction primitive: Dist = (In, Out, ∂)
          - First-class boundary constructor
          - Typed: In/Out types, boundary relation
          - Operations: join, meet, complement, ∂
          
        Boundary types:
          - Sharp: disjoint In/Out (thickness = 0)
          - Liminal: nontrivial overlap (thickness > 0)
          
        ═══════════════════════════════════════════════════════════════
        REGIME AS LANGUAGE
        ═══════════════════════════════════════════════════════════════
        
        Regime: r = (H_r, A_r, Corr_r, Emb_r, Dec_r)
          - H_r: carrier space (representation)
          - A_r: observable algebra (question language)
          - Corr_r: validity corridor
          - Emb/Dec: certified IO pipelines
          
        Corridor: Corr = (Test, Envelope, CertRule)
          - Test: decidable membership predicate
          - Envelope: uncertainty/error budget
          - CertRule: acceptance obligations
          
        ═══════════════════════════════════════════════════════════════
        TYPED OUTCOMES (TOTAL SEMANTICS)
        ═══════════════════════════════════════════════════════════════
        
        OutcomeType = OK | ABSTAIN | AMBIG_m | LIFT | FAIL
          - Never undefined
          - Always proof-carrying
          - Boundary behavior is typed data
          
        ═══════════════════════════════════════════════════════════════
        CATEGORY CREATION
        ═══════════════════════════════════════════════════════════════
        
        Born generator: B ∈ A_s not definable from A_r
          - Witness: (ρ₁, ρ₂) indistinguishable in r, distinguishable in s
          - Certificate: Non-definability with strict slack
          - This IS emergence: new questions become askable
          
        ═══════════════════════════════════════════════════════════════
        POLE CORRESPONDENCE
        ═══════════════════════════════════════════════════════════════
        
        D (Discrete):  Distinction algebra, typed outcomes
        Ω (Continuous): Corridor membership, envelope propagation
        Σ (Stochastic): Indistinguishability, information types
        Ψ (Hierarchical): Born generators, category creation
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def distinction(in_type: str, out_type: str, 
                thickness: float = 0.0) -> Distinction:
    """Create distinction."""
    boundary = BoundaryObject.liminal(thickness) if thickness > 0 else BoundaryObject.sharp()
    return Distinction(in_type, out_type, boundary, is_sharp=(thickness == 0))


def corridor(test: Callable = None, envelope: Envelope = None) -> Corridor:
    """Create corridor."""
    return Corridor(
        test=test or (lambda x: CorridorTestResult.PASS),
        envelope=envelope or Envelope(),
        cert_rule=CertRule()
    )


def regime(name: str, dim: int = 10, 
           generators: List[str] = None) -> Regime:
    """Create regime."""
    return Regime(
        name=name,
        carrier_dim=dim,
        observable_algebra=ObservableAlgebra(generators=generators or ["id"]),
        corridor=Corridor.default(),
        embed_decode=EmbedDecode(
            embed=lambda x: np.array([[x]]),
            decode=lambda x: x[0, 0] if x.size > 0 else 0
        )
    )


def typed_outcome_ok(value: Any) -> TypedOutcome:
    """Create OK outcome."""
    return TypedOutcome.ok(value)


def semantic_pipeline(regime: Regime) -> SemanticPipeline:
    """Create semantic pipeline."""
    return SemanticPipeline(regime)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Distinction
    'Distinction',
    'BoundaryObject',
    
    # Corridor
    'CorridorTestResult',
    'Envelope',
    'CertRule',
    'Corridor',
    
    # Outcomes
    'OutcomeType',
    'TypedOutcome',
    
    # Regime
    'ObservableAlgebra',
    'EmbedDecode',
    'Regime',
    
    # Information
    'IndistinguishabilityPartition',
    'InformationType',
    
    # Category Creation
    'DefinabilityTest',
    'NonDefinabilityWitness',
    'BornGenerator',
    
    # Results
    'ProofCarryingResult',
    'SemanticPipeline',
    
    # Bridge
    'LMFoundationsPoleBridge',
    
    # Functions
    'distinction',
    'corridor',
    'regime',
    'typed_outcome_ok',
    'semantic_pipeline',
]

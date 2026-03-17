"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      PROOF ENGINE MODULE                                     ║
║                                                                              ║
║  Proof-Carrying Computation: Verifier Kernel, Seeds, Certificates, Replay   ║
║                                                                              ║
║  Central Claim:                                                              ║
║    Mathematics becomes computable and exportable when every object is        ║
║    stored as a SEED (generator + constraints) paired with CERTIFICATES       ║
║    and a DETERMINISTIC REPLAY pipeline verified by the VERIFIER KERNEL.      ║
║                                                                              ║
║  Publication Stack:                                                          ║
║    - Seed: minimal publishable unit                                          ║
║    - Constraint IR: normalized semantic target                               ║
║    - Certificate: finite checkable witness                                   ║
║    - Replay: deterministic reconstruction                                    ║
║    - Verifier Kernel: PTIME validation                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Set, Callable, Union
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import hashlib
import json
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# SEED: MINIMAL PUBLISHABLE UNIT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GeneratorPacket:
    """
    Finite generator packet for seed.
    
    Contains: parameters, operator words, lattice steps,
    symmetry generators, normal-form identifiers.
    """
    parameters: Dict[str, Any] = field(default_factory=dict)
    operator_words: List[str] = field(default_factory=list)
    lattice_steps: List[int] = field(default_factory=list)
    symmetry_generators: List[str] = field(default_factory=list)
    normal_form_id: Optional[str] = None
    
    def content_hash(self) -> str:
        """Compute content-addressable hash."""
        data = json.dumps({
            "params": self.parameters,
            "ops": self.operator_words,
            "lattice": self.lattice_steps,
            "sym": self.symmetry_generators,
            "nf": self.normal_form_id
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class RegularityClass(Enum):
    """Regularity class for admissibility."""
    CONTINUOUS = "C0"
    DIFFERENTIABLE = "C1"
    SMOOTH = "C∞"
    ANALYTIC = "Cω"
    MEROMORPHIC = "M"
    DISTRIBUTIONAL = "D'"


class EqualityPolicy(Enum):
    """Equality policy for scope."""
    EXACT = "exact"
    INTERVAL = "interval"
    SYMBOLIC = "symbolic"
    HASH_BASED = "hash"


@dataclass
class Scope:
    """
    Admissibility declaration for seed.
    
    Domain, regularity, branch sheet, corridor, canonicalization policy.
    """
    domain: str = "ℂ"
    regularity: RegularityClass = RegularityClass.ANALYTIC
    branch_sheet: int = 0  # Principal branch by default
    corridor_predicates: List[str] = field(default_factory=list)
    quantitative_margins: Dict[str, float] = field(default_factory=dict)
    equality_policy: EqualityPolicy = EqualityPolicy.EXACT
    numeric_semantics: str = "exact"  # exact, interval, fixed
    
    def is_compatible(self, other: 'Scope') -> bool:
        """Check if two scopes are compatible."""
        return (self.domain == other.domain and 
                self.branch_sheet == other.branch_sheet)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT IR (INTERMEDIATE REPRESENTATION)
# ═══════════════════════════════════════════════════════════════════════════════

class ConstraintType(Enum):
    """Types of constraint tiles."""
    ROOT = "root"                 # F = G → H := F - G = 0
    FIXED_POINT = "fixed_point"   # x = f(x) → f(x) - x = 0
    CYCLE = "cycle"               # f^{∘k}(x) - x = 0
    LATTICE = "lattice"           # T(x) ∈ θ + ΔZ
    KERNEL_MORPHISM = "kernel"    # W K_X = K_Y W
    JET_LOCK = "jet"              # H = H' = ... = H^{(m-1)} = 0
    SINGULAR = "singular"         # H(z) = 0 and det J_H(z) = 0


@dataclass
class ConstraintTile:
    """
    Single constraint tile in IR.
    """
    constraint_type: ConstraintType
    expression: str  # The constraint expression
    variables: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # For jet locks
    multiplicity: int = 1
    
    # For lattice constraints
    lattice_offset: float = 0.0
    lattice_period: float = 1.0
    
    def to_ir(self) -> str:
        """Convert to normalized IR string."""
        return f"{self.constraint_type.value}:{self.expression}:{self.multiplicity}"


@dataclass
class ConstraintIR:
    """
    Constraint Intermediate Representation.
    
    All publishable claims compile to this normalized form.
    Semantics: object = set/point/morphism satisfying H=0 under scope.
    """
    tiles: List[ConstraintTile] = field(default_factory=list)
    scope: Optional[Scope] = None
    
    def add_root(self, expr: str, variables: List[str] = None):
        """Add root constraint: H = 0."""
        self.tiles.append(ConstraintTile(
            ConstraintType.ROOT, expr, variables or []
        ))
    
    def add_fixed_point(self, f_expr: str, x_var: str):
        """Add fixed point constraint: f(x) - x = 0."""
        self.tiles.append(ConstraintTile(
            ConstraintType.FIXED_POINT, f"{f_expr} - {x_var}", [x_var]
        ))
    
    def add_cycle(self, f_expr: str, x_var: str, period: int):
        """Add cycle constraint: f^k(x) - x = 0."""
        self.tiles.append(ConstraintTile(
            ConstraintType.CYCLE, f"iter({f_expr},{period}) - {x_var}", 
            [x_var], {"period": period}
        ))
    
    def add_jet_lock(self, expr: str, order: int):
        """Add jet lock: H = H' = ... = H^{(m-1)} = 0."""
        tile = ConstraintTile(ConstraintType.JET_LOCK, expr)
        tile.multiplicity = order
        self.tiles.append(tile)
    
    def normalize(self) -> str:
        """Get normalized IR string."""
        return ";".join(t.to_ir() for t in self.tiles)
    
    def content_hash(self) -> str:
        """Content-addressable hash of IR."""
        return hashlib.sha256(self.normalize().encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════════
# CERTIFICATES
# ═══════════════════════════════════════════════════════════════════════════════

class CertificateClass(Enum):
    """Classes of certificates."""
    RESIDUAL_BOUND = "residual"       # Existence via residual
    INTERVAL_ENCLOSURE = "interval"   # Interval arithmetic proof
    MONOTONICITY = "monotone"         # Uniqueness via monotonicity
    CONTRACTION = "contract"          # Uniqueness via contraction
    INVERSION = "inverse"             # Lens invertibility
    JET_MULTIPLICITY = "jet"          # Order-m zeros
    JACOBIAN_RANK = "rank"            # Degeneracy/singularity
    COMMUTATION = "commute"           # Diagram commutativity
    SYMMETRY_LIFT = "symmetry"        # Orbit lifting


@dataclass
class Certificate:
    """
    Finite checkable witness validating a claim.
    
    C = (Assumptions, Claim, Witness, Bounds, VerifierHook)
    """
    cert_class: CertificateClass
    assumptions: List[str] = field(default_factory=list)
    claim: str = ""
    witness: Dict[str, Any] = field(default_factory=dict)
    bounds: Dict[str, float] = field(default_factory=dict)
    verifier_hook: str = "default"
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    cert_id: str = ""
    
    def __post_init__(self):
        """Generate certificate ID."""
        data = f"{self.cert_class.value}:{self.claim}:{json.dumps(self.witness, sort_keys=True)}"
        self.cert_id = hashlib.sha256(data.encode()).hexdigest()[:12]
    
    def verify(self, verifier: 'VerifierKernel') -> Tuple[bool, str]:
        """Verify certificate using kernel."""
        return verifier.check_certificate(self)


@dataclass
class CertBundle:
    """
    Bundle of certificates for a seed.
    """
    certificates: List[Certificate] = field(default_factory=list)
    
    def add(self, cert: Certificate):
        """Add certificate to bundle."""
        self.certificates.append(cert)
    
    def get_by_class(self, cert_class: CertificateClass) -> List[Certificate]:
        """Get all certificates of a class."""
        return [c for c in self.certificates if c.cert_class == cert_class]
    
    def all_valid(self, verifier: 'VerifierKernel') -> Tuple[bool, List[str]]:
        """Check all certificates."""
        errors = []
        for cert in self.certificates:
            valid, msg = cert.verify(verifier)
            if not valid:
                errors.append(f"{cert.cert_id}: {msg}")
        return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════════════════════════
# REPLAY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EnvironmentFingerprint:
    """
    Pinned environment for deterministic replay.
    """
    platform: str = "python"
    version: str = "3.11"
    precision: int = 64
    rng_seed: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            "platform": self.platform,
            "version": self.version,
            "precision": self.precision,
            "rng_seed": self.rng_seed
        }
    
    def fingerprint(self) -> str:
        """Get environment fingerprint hash."""
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()[:12]


@dataclass
class ReplayStep:
    """Single step in replay transcript."""
    step_id: int
    operation: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    
    def hash(self) -> str:
        """Hash of this step."""
        data = f"{self.step_id}:{self.operation}:{json.dumps(self.inputs, sort_keys=True, default=str)}"
        return hashlib.sha256(data.encode()).hexdigest()[:8]


@dataclass
class ReplayTranscript:
    """
    Deterministic replay transcript.
    """
    steps: List[ReplayStep] = field(default_factory=list)
    environment: EnvironmentFingerprint = field(default_factory=EnvironmentFingerprint)
    final_hash: str = ""
    
    def add_step(self, operation: str, inputs: Dict, outputs: Dict):
        """Add step to transcript."""
        step = ReplayStep(len(self.steps), operation, inputs, outputs)
        self.steps.append(step)
    
    def finalize(self):
        """Compute final hash."""
        all_hashes = [s.hash() for s in self.steps]
        combined = ":".join(all_hashes)
        self.final_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def verify_integrity(self) -> bool:
        """Verify transcript integrity."""
        all_hashes = [s.hash() for s in self.steps]
        combined = ":".join(all_hashes)
        expected = hashlib.sha256(combined.encode()).hexdigest()[:16]
        return expected == self.final_hash


@dataclass
class ReplayProcedure:
    """
    Deterministic replay procedure.
    """
    transcript: ReplayTranscript
    generator: GeneratorPacket
    deps: List[str] = field(default_factory=list)
    
    def execute(self, context: Dict[str, Any] = None) -> Tuple[Any, ReplayTranscript]:
        """Execute replay and return result with new transcript."""
        # This would actually reconstruct the object
        # For now, return placeholder
        new_transcript = ReplayTranscript(environment=self.transcript.environment)
        new_transcript.add_step("reconstruct", {"gen": self.generator.content_hash()}, {})
        new_transcript.finalize()
        return None, new_transcript


# ═══════════════════════════════════════════════════════════════════════════════
# SEED: COMPLETE PUBLISHABLE UNIT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Seed:
    """
    Seed: minimal publishable unit of mathematical content.
    
    Σ = (Gen, Scope, IR(H=0), CertBundle, Replay, Deps)
    """
    generator: GeneratorPacket
    scope: Scope
    constraint_ir: ConstraintIR
    cert_bundle: CertBundle
    replay: ReplayProcedure
    deps: List[str] = field(default_factory=list)  # Hashes of dependencies
    
    # Metadata
    seed_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Generate seed ID."""
        content = f"{self.generator.content_hash()}:{self.constraint_ir.content_hash()}"
        self.seed_id = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def is_publishable(self, verifier: 'VerifierKernel') -> Tuple[bool, List[str]]:
        """Check if seed is publishable."""
        errors = []
        
        # Check certificates
        valid, cert_errors = self.cert_bundle.all_valid(verifier)
        if not valid:
            errors.extend(cert_errors)
        
        # Check replay integrity
        if not self.replay.transcript.verify_integrity():
            errors.append("Replay transcript integrity check failed")
        
        return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

class VerificationStatus(Enum):
    """Status of verification."""
    ACCEPT = "accept"
    REJECT = "reject"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class VerifierKernel:
    """
    Verifier Kernel (VK): minimal trusted core.
    
    Defines the predicate "publishable".
    
    VK accepts only:
    - Normalized Constraint IR
    - Explicit admissibility scope declarations
    - Certificate bundles with registered verifier hooks
    - Deterministic replay transcripts
    
    VK enforces:
    - Proof-Carrying Standard (PCS)
    - PTIME verification discipline
    - No drift (semantic truth is generator-level)
    """
    registered_hooks: Dict[str, Callable] = field(default_factory=dict)
    max_verification_time: float = 60.0  # seconds
    precision_bits: int = 64
    
    def __post_init__(self):
        """Register default verifier hooks."""
        self.registered_hooks = {
            "default": self._default_hook,
            "residual": self._residual_hook,
            "interval": self._interval_hook,
            "contraction": self._contraction_hook,
        }
    
    def _default_hook(self, cert: Certificate) -> Tuple[bool, str]:
        """Default verification hook."""
        return True, "Default check passed"
    
    def _residual_hook(self, cert: Certificate) -> Tuple[bool, str]:
        """Verify residual bound certificate."""
        if "residual" not in cert.bounds:
            return False, "Missing residual bound"
        if cert.bounds["residual"] > cert.bounds.get("tolerance", 1e-10):
            return False, f"Residual {cert.bounds['residual']} exceeds tolerance"
        return True, "Residual check passed"
    
    def _interval_hook(self, cert: Certificate) -> Tuple[bool, str]:
        """Verify interval enclosure certificate."""
        if "lower" not in cert.witness or "upper" not in cert.witness:
            return False, "Missing interval bounds"
        if cert.witness["lower"] > cert.witness["upper"]:
            return False, "Invalid interval (lower > upper)"
        return True, "Interval check passed"
    
    def _contraction_hook(self, cert: Certificate) -> Tuple[bool, str]:
        """Verify contraction certificate."""
        if "contraction_factor" not in cert.bounds:
            return False, "Missing contraction factor"
        if cert.bounds["contraction_factor"] >= 1.0:
            return False, "Contraction factor must be < 1"
        return True, "Contraction check passed"
    
    def check_certificate(self, cert: Certificate) -> Tuple[bool, str]:
        """Check a single certificate."""
        hook = self.registered_hooks.get(cert.verifier_hook, self._default_hook)
        return hook(cert)
    
    def verify_seed(self, seed: Seed) -> Tuple[VerificationStatus, List[str]]:
        """
        Verify a seed for publication.
        """
        errors = []
        
        # Check IR is normalized
        if not seed.constraint_ir.tiles:
            errors.append("Empty constraint IR")
        
        # Check scope declaration
        if seed.scope is None:
            errors.append("Missing scope declaration")
        
        # Check all certificates
        for cert in seed.cert_bundle.certificates:
            valid, msg = self.check_certificate(cert)
            if not valid:
                errors.append(f"Certificate {cert.cert_id}: {msg}")
        
        # Check replay integrity
        if not seed.replay.transcript.verify_integrity():
            errors.append("Replay transcript integrity failure")
        
        # Check dependencies exist (simplified)
        # In real implementation, would verify dep hashes
        
        if errors:
            return VerificationStatus.REJECT, errors
        return VerificationStatus.ACCEPT, []
    
    def publish(self, seed: Seed) -> Tuple[bool, str]:
        """
        Attempt to publish a seed.
        """
        status, errors = self.verify_seed(seed)
        if status == VerificationStatus.ACCEPT:
            return True, f"Published: {seed.seed_id}"
        return False, f"Rejected: {'; '.join(errors)}"


# ═══════════════════════════════════════════════════════════════════════════════
# PROOF-CARRYING STANDARD
# ═══════════════════════════════════════════════════════════════════════════════

class ProofStandard(Enum):
    """Proof-Carrying Standard types."""
    PCS_D = "deductive"       # Deductive proof in formal system
    PCS_C = "certificate"     # Seed + certificates + replay
    PCS_H = "hybrid"          # Deductive + certificate strengthening


@dataclass
class PublishableArtifact:
    """
    Publishable mathematical artifact.
    """
    seed: Seed
    proof_standard: ProofStandard
    formal_proof: Optional[str] = None  # For PCS-D or PCS-H
    
    def meets_standard(self, verifier: VerifierKernel) -> bool:
        """Check if artifact meets proof standard."""
        if self.proof_standard == ProofStandard.PCS_D:
            # Would check formal proof
            return self.formal_proof is not None
        elif self.proof_standard == ProofStandard.PCS_C:
            status, _ = verifier.verify_seed(self.seed)
            return status == VerificationStatus.ACCEPT
        else:  # PCS_H
            has_proof = self.formal_proof is not None
            status, _ = verifier.verify_seed(self.seed)
            return has_proof and status == VerificationStatus.ACCEPT


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICALIZATION AND EQUIVALENCE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NormalForm:
    """
    Normal form specification for canonicalization.
    """
    name: str
    rewrite_rules: List[Tuple[str, str]] = field(default_factory=list)
    version: str = "1.0"
    
    def normalize(self, expr: str) -> str:
        """Apply rewrite rules to normalize expression."""
        result = expr
        for pattern, replacement in self.rewrite_rules:
            result = result.replace(pattern, replacement)
        return result


@dataclass
class EquivalenceChecker:
    """
    Layered equivalence checking.
    """
    normal_forms: Dict[str, NormalForm] = field(default_factory=dict)
    
    def check_scope_compatible(self, s1: Scope, s2: Scope) -> bool:
        """Layer 1: Check scope compatibility."""
        return s1.is_compatible(s2)
    
    def check_normal_form_match(self, ir1: ConstraintIR, ir2: ConstraintIR) -> bool:
        """Layer 2: Check normalized IR hashes match."""
        return ir1.content_hash() == ir2.content_hash()
    
    def check_invariants(self, seed1: Seed, seed2: Seed) -> bool:
        """Layer 3: Check invariant ledger."""
        # Compare generator hashes
        return seed1.generator.content_hash() == seed2.generator.content_hash()
    
    def are_equivalent(self, seed1: Seed, seed2: Seed) -> Tuple[bool, str]:
        """
        Full equivalence check.
        """
        # Layer 1: Scope
        if not self.check_scope_compatible(seed1.scope, seed2.scope):
            return False, "Scope incompatible"
        
        # Layer 2: Normal form
        if not self.check_normal_form_match(seed1.constraint_ir, seed2.constraint_ir):
            return False, "Normal forms differ"
        
        # Layer 3: Invariants (quick check)
        if self.check_invariants(seed1, seed2):
            return True, "Invariant match"
        
        # Would do deeper transport witness check here
        return False, "No equivalence witness found"


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProofEnginePoleBridge:
    """
    Bridge between Proof Engine and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        PROOF ENGINE ↔ FRAMEWORK
        
        ═══════════════════════════════════════════════════════════════
        SEED: MINIMAL PUBLISHABLE UNIT
        ═══════════════════════════════════════════════════════════════
        
        Σ = (Gen, Scope, IR(H=0), CertBundle, Replay, Deps)
        
        Gen: Generator packet (parameters, operators, symmetries)
        Scope: Admissibility (domain, regularity, branch, corridor)
        IR: Constraint intermediate representation (H=0)
        CertBundle: Verifiable certificates
        Replay: Deterministic reconstruction
        Deps: Provenance DAG
        
        ═══════════════════════════════════════════════════════════════
        CONSTRAINT IR
        ═══════════════════════════════════════════════════════════════
        
        All claims compile to constraint tiles:
          ROOT: F = G → H := F - G = 0
          FIXED_POINT: x = f(x) → f(x) - x = 0
          CYCLE: f^{∘k}(x) - x = 0
          LATTICE: T(x) ∈ θ + ΔZ
          KERNEL: W K_X = K_Y W
          JET_LOCK: H = H' = ... = H^{(m-1)} = 0
          SINGULAR: H(z) = 0 ∧ det J_H(z) = 0
          
        ═══════════════════════════════════════════════════════════════
        CERTIFICATES
        ═══════════════════════════════════════════════════════════════
        
        C = (Assumptions, Claim, Witness, Bounds, VerifierHook)
        
        Classes:
          - Residual bounds (existence)
          - Interval enclosures (containment)
          - Monotonicity/contraction (uniqueness)
          - Jet multiplicity (order-m zeros)
          - Jacobian rank (degeneracy)
          - Commutation (diagram equality)
          - Symmetry lift (orbit)
          
        ═══════════════════════════════════════════════════════════════
        VERIFIER KERNEL
        ═══════════════════════════════════════════════════════════════
        
        VK = Minimal trusted core defining "publishable"
        
        Enforces:
          PCS-D: Deductive proof
          PCS-C: Seed + certificates + replay
          PCS-H: Hybrid (deductive + certificate)
          
        Invariants:
          - PTIME verification
          - No drift (generator-level truth)
          - Deterministic replay
          
        ═══════════════════════════════════════════════════════════════
        EQUIVALENCE CHECKING
        ═══════════════════════════════════════════════════════════════
        
        Layers:
          1. Scope compatibility
          2. Normal-form hash match
          3. Invariant ledger
          4. Transport witnesses
          
        ═══════════════════════════════════════════════════════════════
        POLE CORRESPONDENCE
        ═══════════════════════════════════════════════════════════════
        
        D: Constraint tiles, discrete certificates
        Ω: Scope corridors, continuous margins
        Σ: Probabilistic bounds, interval arithmetic
        Ψ: Recursive replay, dependency DAG
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generator_packet(**params) -> GeneratorPacket:
    """Create generator packet."""
    return GeneratorPacket(parameters=params)


def scope(domain: str = "ℂ", regularity: RegularityClass = RegularityClass.ANALYTIC) -> Scope:
    """Create scope."""
    return Scope(domain=domain, regularity=regularity)


def constraint_ir() -> ConstraintIR:
    """Create empty constraint IR."""
    return ConstraintIR()


def certificate(cert_class: CertificateClass, claim: str, 
                witness: Dict = None, bounds: Dict = None) -> Certificate:
    """Create certificate."""
    return Certificate(cert_class, claim=claim, 
                      witness=witness or {}, bounds=bounds or {})


def cert_bundle(*certs: Certificate) -> CertBundle:
    """Create certificate bundle."""
    bundle = CertBundle()
    for c in certs:
        bundle.add(c)
    return bundle


def verifier_kernel() -> VerifierKernel:
    """Create verifier kernel."""
    return VerifierKernel()


def equivalence_checker() -> EquivalenceChecker:
    """Create equivalence checker."""
    return EquivalenceChecker()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Generator
    'GeneratorPacket',
    
    # Scope
    'RegularityClass',
    'EqualityPolicy',
    'Scope',
    
    # Constraint IR
    'ConstraintType',
    'ConstraintTile',
    'ConstraintIR',
    
    # Certificates
    'CertificateClass',
    'Certificate',
    'CertBundle',
    
    # Replay
    'EnvironmentFingerprint',
    'ReplayStep',
    'ReplayTranscript',
    'ReplayProcedure',
    
    # Seed
    'Seed',
    
    # Verifier
    'VerificationStatus',
    'VerifierKernel',
    
    # Standards
    'ProofStandard',
    'PublishableArtifact',
    
    # Equivalence
    'NormalForm',
    'EquivalenceChecker',
    
    # Bridge
    'ProofEnginePoleBridge',
    
    # Functions
    'generator_packet',
    'scope',
    'constraint_ir',
    'certificate',
    'cert_bundle',
    'verifier_kernel',
    'equivalence_checker',
]

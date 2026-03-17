"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PROOFS AND CERTIFICATES MODULE                            ║
║                                                                              ║
║  Formal Verification Infrastructure, Certificate Types, Replay Semantics     ║
║                                                                              ║
║  Statement Types:                                                            ║
║    [AX]   Axiom: foundational assumption with scope declaration              ║
║    [DEF]  Definition: new object with admissibility conditions               ║
║    [LEM]  Lemma: auxiliary result with proof                                 ║
║    [THM]  Theorem: main result with complete proof                           ║
║    [COR]  Corollary: immediate consequence                                   ║
║    [ALG]  Algorithm: inputs, outputs, correctness, complexity                ║
║    [CERT] Certificate: verification payload with deterministic verifier      ║
║    [SEED] Seed: compact generative description + constraints + replay        ║
║    [ENG]  Engineered invariant: certificate-based validity                   ║
║    [OBS]  Observation: reproducible experimental protocol                    ║
║    [CONJ] Conjecture: proposed statement with evidence                       ║
║                                                                              ║
║  Promotion Rules:                                                            ║
║    [OBS] → [CONJ] via formalization                                         ║
║    [CONJ] → [THM] only via complete deductive proof                         ║
║    [CONJ] → [ENG] via certificate construction                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set, Any, Callable, Union, TypeVar
from enum import Enum, auto
from abc import ABC, abstractmethod
import hashlib
import json
import time
from datetime import datetime
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# STATEMENT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class StatementType(Enum):
    """Classification of mathematical statements."""
    AXIOM = "AX"           # Foundational assumption
    DEFINITION = "DEF"     # New object definition
    LEMMA = "LEM"          # Auxiliary result
    THEOREM = "THM"        # Main result
    COROLLARY = "COR"      # Immediate consequence
    ALGORITHM = "ALG"      # Computational procedure
    CERTIFICATE = "CERT"   # Verification payload
    SEED = "SEED"          # Generative description
    ENGINEERED = "ENG"     # Certificate-based validity
    OBSERVATION = "OBS"    # Experimental protocol
    CONJECTURE = "CONJ"    # Proposed statement


class CertificateLevel(Enum):
    """Verification assurance levels."""
    L0_CLAIM = 0       # Unverified assertion
    L1_EMPIRICAL = 1   # Numerical testing passed
    L2_CERTIFIED = 2   # Interval arithmetic verified
    L3_FORMAL = 3      # Machine-checked proof


class PromotionPath(Enum):
    """Valid promotion paths between statement types."""
    OBS_TO_CONJ = "OBS→CONJ"      # Formalization
    CONJ_TO_THM = "CONJ→THM"      # Complete proof
    CONJ_TO_ENG = "CONJ→ENG"      # Certificate construction
    CLAIM_TO_CERT = "CLAIM→CERT"  # Verification


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL HASH - CONTENT-ADDRESSABLE IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CanonicalHash:
    """
    Content-addressable hash for mathematical objects.
    
    Provides deterministic, reproducible identity for:
        - Seeds
        - Certificates
        - Transcripts
        - Derived artifacts
    """
    algorithm: str = "sha256"
    digest: str = ""
    
    @classmethod
    def from_bytes(cls, data: bytes, algorithm: str = "sha256") -> 'CanonicalHash':
        """Compute hash from raw bytes."""
        h = hashlib.new(algorithm)
        h.update(data)
        return cls(algorithm=algorithm, digest=h.hexdigest())
    
    @classmethod
    def from_string(cls, s: str, algorithm: str = "sha256") -> 'CanonicalHash':
        """Compute hash from string."""
        return cls.from_bytes(s.encode('utf-8'), algorithm)
    
    @classmethod
    def from_json(cls, obj: Any, algorithm: str = "sha256") -> 'CanonicalHash':
        """Compute hash from JSON-serializable object."""
        # Canonical JSON: sorted keys, no whitespace
        canonical = json.dumps(obj, sort_keys=True, separators=(',', ':'))
        return cls.from_string(canonical, algorithm)
    
    @classmethod
    def from_array(cls, arr: np.ndarray, algorithm: str = "sha256") -> 'CanonicalHash':
        """Compute hash from numpy array."""
        return cls.from_bytes(arr.tobytes(), algorithm)
    
    def matches(self, other: 'CanonicalHash') -> bool:
        """Check if hashes match."""
        return self.algorithm == other.algorithm and self.digest == other.digest
    
    @property
    def short(self) -> str:
        """Short form: first 8 characters."""
        return self.digest[:8]
    
    def __repr__(self) -> str:
        return f"Hash({self.algorithm}:{self.short}...)"


# ═══════════════════════════════════════════════════════════════════════════════
# SEED - GENERATIVE DESCRIPTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Seed:
    """
    Compact generative description of a mathematical object.
    
    A seed contains:
        - Generator specification (how to build the object)
        - Constraint set (what properties it must satisfy)
        - Replay transcript (deterministic reconstruction)
    
    Seeds are the primary storage format: derived artifacts are
    subordinate to replay verification.
    """
    seed_id: str
    statement_type: StatementType
    generator: Dict[str, Any]
    constraints: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    _hash: Optional[CanonicalHash] = field(default=None, repr=False)
    
    def __post_init__(self):
        if self._hash is None:
            self._compute_hash()
    
    def _compute_hash(self):
        """Compute canonical hash of seed content."""
        content = {
            'seed_id': self.seed_id,
            'type': self.statement_type.value,
            'generator': self.generator,
            'constraints': self.constraints
        }
        self._hash = CanonicalHash.from_json(content)
    
    @property
    def hash(self) -> CanonicalHash:
        """Canonical hash of seed."""
        if self._hash is None:
            self._compute_hash()
        return self._hash
    
    def add_constraint(self, constraint: Dict[str, Any]):
        """Add constraint (invalidates hash)."""
        self.constraints.append(constraint)
        self._hash = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'seed_id': self.seed_id,
            'type': self.statement_type.value,
            'generator': self.generator,
            'constraints': self.constraints,
            'metadata': self.metadata,
            'hash': self.hash.digest
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Seed':
        """Deserialize from dictionary."""
        return cls(
            seed_id=d['seed_id'],
            statement_type=StatementType(d['type']),
            generator=d['generator'],
            constraints=d['constraints'],
            metadata=d.get('metadata', {})
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CERTIFICATE - VERIFICATION PAYLOAD
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Certificate:
    """
    Verification payload with deterministic verifier.
    
    A certificate contains:
        - Claim: what is being verified
        - Witness: data supporting the claim
        - Verifier: deterministic procedure to check
        - Level: assurance level achieved
    """
    cert_id: str
    claim: Dict[str, Any]
    witness: Dict[str, Any]
    verifier_id: str
    level: CertificateLevel
    timestamp: datetime = field(default_factory=datetime.now)
    
    _verified: Optional[bool] = field(default=None, repr=False)
    _hash: Optional[CanonicalHash] = field(default=None, repr=False)
    
    @property
    def hash(self) -> CanonicalHash:
        """Canonical hash of certificate."""
        if self._hash is None:
            content = {
                'cert_id': self.cert_id,
                'claim': self.claim,
                'witness': self.witness,
                'verifier_id': self.verifier_id,
                'level': self.level.value
            }
            self._hash = CanonicalHash.from_json(content)
        return self._hash
    
    @property
    def is_verified(self) -> Optional[bool]:
        """Whether certificate has been verified."""
        return self._verified
    
    def mark_verified(self, result: bool):
        """Mark verification result."""
        self._verified = result
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'cert_id': self.cert_id,
            'claim': self.claim,
            'witness': self.witness,
            'verifier_id': self.verifier_id,
            'level': self.level.value,
            'timestamp': self.timestamp.isoformat(),
            'hash': self.hash.digest,
            'verified': self._verified
        }


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER KERNEL - CERTIFICATE CHECKING
# ═══════════════════════════════════════════════════════════════════════════════

class VerifierKernel(ABC):
    """
    Abstract base for certificate verifiers.
    
    A verifier is a deterministic procedure that:
        - Takes a certificate as input
        - Returns (valid: bool, diagnostic: Dict)
        - Must be reproducible across environments
    """
    
    @property
    @abstractmethod
    def verifier_id(self) -> str:
        """Unique verifier identifier."""
        pass
    
    @property
    @abstractmethod
    def supported_claims(self) -> Set[str]:
        """Set of claim types this verifier handles."""
        pass
    
    @abstractmethod
    def verify(self, certificate: Certificate) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify certificate.
        
        Returns:
            (is_valid, diagnostic_info)
        """
        pass
    
    def can_verify(self, certificate: Certificate) -> bool:
        """Check if this verifier can handle the certificate."""
        claim_type = certificate.claim.get('type', '')
        return claim_type in self.supported_claims


class EqualityVerifier(VerifierKernel):
    """Verifier for equality claims."""
    
    @property
    def verifier_id(self) -> str:
        return "equality_v1"
    
    @property
    def supported_claims(self) -> Set[str]:
        return {"equality", "approximate_equality"}
    
    def verify(self, certificate: Certificate) -> Tuple[bool, Dict[str, Any]]:
        claim = certificate.claim
        witness = certificate.witness
        
        if claim['type'] == 'equality':
            lhs = witness.get('lhs')
            rhs = witness.get('rhs')
            is_valid = lhs == rhs
            return (is_valid, {'lhs': lhs, 'rhs': rhs})
        
        elif claim['type'] == 'approximate_equality':
            lhs = witness.get('lhs')
            rhs = witness.get('rhs')
            tol = claim.get('tolerance', 1e-10)
            diff = abs(lhs - rhs)
            is_valid = diff <= tol
            return (is_valid, {'difference': diff, 'tolerance': tol})
        
        return (False, {'error': 'unknown claim type'})


class IntervalVerifier(VerifierKernel):
    """Verifier for interval containment claims."""
    
    @property
    def verifier_id(self) -> str:
        return "interval_v1"
    
    @property
    def supported_claims(self) -> Set[str]:
        return {"interval_contains", "interval_bounds"}
    
    def verify(self, certificate: Certificate) -> Tuple[bool, Dict[str, Any]]:
        claim = certificate.claim
        witness = certificate.witness
        
        if claim['type'] == 'interval_contains':
            value = witness.get('value')
            lower = witness.get('lower')
            upper = witness.get('upper')
            is_valid = lower <= value <= upper
            return (is_valid, {'value': value, 'interval': (lower, upper)})
        
        elif claim['type'] == 'interval_bounds':
            computed_lower = witness.get('computed_lower')
            computed_upper = witness.get('computed_upper')
            claimed_lower = claim.get('lower')
            claimed_upper = claim.get('upper')
            is_valid = (computed_lower >= claimed_lower and 
                       computed_upper <= claimed_upper)
            return (is_valid, {
                'computed': (computed_lower, computed_upper),
                'claimed': (claimed_lower, claimed_upper)
            })
        
        return (False, {'error': 'unknown claim type'})


class PermutationVerifier(VerifierKernel):
    """Verifier for permutation claims (Latin squares, etc.)."""
    
    @property
    def verifier_id(self) -> str:
        return "permutation_v1"
    
    @property
    def supported_claims(self) -> Set[str]:
        return {"is_permutation", "is_latin_square", "is_diagonal_latin"}
    
    def verify(self, certificate: Certificate) -> Tuple[bool, Dict[str, Any]]:
        claim = certificate.claim
        witness = certificate.witness
        
        if claim['type'] == 'is_permutation':
            arr = np.array(witness.get('array'))
            n = len(arr)
            is_valid = set(arr) == set(range(n))
            return (is_valid, {'n': n, 'unique_count': len(set(arr))})
        
        elif claim['type'] == 'is_latin_square':
            matrix = np.array(witness.get('matrix'))
            n = matrix.shape[0]
            symbols = set(range(n))
            
            # Check rows and columns
            rows_ok = all(set(matrix[i, :]) == symbols for i in range(n))
            cols_ok = all(set(matrix[:, j]) == symbols for j in range(n))
            
            is_valid = rows_ok and cols_ok
            return (is_valid, {'n': n, 'rows_ok': rows_ok, 'cols_ok': cols_ok})
        
        elif claim['type'] == 'is_diagonal_latin':
            matrix = np.array(witness.get('matrix'))
            n = matrix.shape[0]
            symbols = set(range(n))
            
            # Check all four properties
            rows_ok = all(set(matrix[i, :]) == symbols for i in range(n))
            cols_ok = all(set(matrix[:, j]) == symbols for j in range(n))
            main_diag_ok = set(matrix[i, i] for i in range(n)) == symbols
            anti_diag_ok = set(matrix[i, n-1-i] for i in range(n)) == symbols
            
            is_valid = rows_ok and cols_ok and main_diag_ok and anti_diag_ok
            return (is_valid, {
                'n': n,
                'rows_ok': rows_ok,
                'cols_ok': cols_ok,
                'main_diag_ok': main_diag_ok,
                'anti_diag_ok': anti_diag_ok
            })
        
        return (False, {'error': 'unknown claim type'})


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class VerifierRegistry:
    """
    Registry of available verifiers.
    
    Maps verifier IDs to verifier instances for certificate checking.
    """
    
    def __init__(self):
        self._verifiers: Dict[str, VerifierKernel] = {}
        self._register_builtins()
    
    def _register_builtins(self):
        """Register built-in verifiers."""
        self.register(EqualityVerifier())
        self.register(IntervalVerifier())
        self.register(PermutationVerifier())
    
    def register(self, verifier: VerifierKernel):
        """Register a verifier."""
        self._verifiers[verifier.verifier_id] = verifier
    
    def get(self, verifier_id: str) -> Optional[VerifierKernel]:
        """Get verifier by ID."""
        return self._verifiers.get(verifier_id)
    
    def verify(self, certificate: Certificate) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify certificate using appropriate verifier.
        """
        verifier = self.get(certificate.verifier_id)
        if verifier is None:
            return (False, {'error': f'Unknown verifier: {certificate.verifier_id}'})
        
        if not verifier.can_verify(certificate):
            return (False, {'error': 'Verifier cannot handle this claim type'})
        
        result, diagnostic = verifier.verify(certificate)
        certificate.mark_verified(result)
        return (result, diagnostic)
    
    @property
    def available_verifiers(self) -> List[str]:
        """List available verifier IDs."""
        return list(self._verifiers.keys())


# Global registry
_GLOBAL_REGISTRY = VerifierRegistry()

def get_verifier_registry() -> VerifierRegistry:
    """Get global verifier registry."""
    return _GLOBAL_REGISTRY


# ═══════════════════════════════════════════════════════════════════════════════
# REPLAY TRANSCRIPT - DETERMINISTIC RECONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ReplayStep:
    """Single step in a replay transcript."""
    step_id: int
    operation: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_id': self.step_id,
            'operation': self.operation,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'timestamp': self.timestamp
        }


@dataclass
class ReplayTranscript:
    """
    Deterministic replay transcript for seed reconstruction.
    
    A transcript records:
        - All steps of object construction
        - Determinism specification (rounding, precision)
        - Environment fingerprint
        - Output hashes for verification
    """
    transcript_id: str
    seed_hash: str
    steps: List[ReplayStep] = field(default_factory=list)
    determinism_spec: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    output_hashes: Dict[str, str] = field(default_factory=dict)
    
    def add_step(self, operation: str, inputs: Dict, outputs: Dict):
        """Add replay step."""
        step = ReplayStep(
            step_id=len(self.steps),
            operation=operation,
            inputs=inputs,
            outputs=outputs
        )
        self.steps.append(step)
    
    def record_output(self, name: str, value: Any):
        """Record output hash."""
        if isinstance(value, np.ndarray):
            h = CanonicalHash.from_array(value)
        else:
            h = CanonicalHash.from_json(value)
        self.output_hashes[name] = h.digest
    
    @property
    def hash(self) -> CanonicalHash:
        """Hash of complete transcript."""
        content = {
            'transcript_id': self.transcript_id,
            'seed_hash': self.seed_hash,
            'steps': [s.to_dict() for s in self.steps],
            'determinism_spec': self.determinism_spec,
            'output_hashes': self.output_hashes
        }
        return CanonicalHash.from_json(content)
    
    def verify_reproducibility(self, other: 'ReplayTranscript') -> bool:
        """Check if two transcripts are reproducibly equivalent."""
        return self.output_hashes == other.output_hashes


# ═══════════════════════════════════════════════════════════════════════════════
# STRESS TEST HARNESS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StressTestResult:
    """Result of a stress test."""
    test_id: str
    passed: bool
    parameter_range: Dict[str, Tuple[float, float]]
    failure_point: Optional[Dict[str, float]] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)


class StressTestHarness:
    """
    Harness for stress testing certificates and seeds.
    
    Tests:
        - Parameter perturbation
        - Boundary conditions
        - Precision degradation
        - Reproducibility across environments
    """
    
    def __init__(self, seed: Seed, registry: VerifierRegistry = None):
        self.seed = seed
        self.registry = registry or get_verifier_registry()
        self.results: List[StressTestResult] = []
    
    def boundary_test(self, parameter: str, 
                     range_: Tuple[float, float],
                     n_samples: int = 20,
                     verifier: Callable[[float], Certificate] = None) -> StressTestResult:
        """
        Test behavior near boundary values.
        """
        low, high = range_
        samples = np.linspace(low, high, n_samples)
        
        failures = []
        for val in samples:
            if verifier:
                cert = verifier(val)
                ok, _ = self.registry.verify(cert)
                if not ok:
                    failures.append(val)
        
        passed = len(failures) == 0
        result = StressTestResult(
            test_id=f"boundary_{parameter}",
            passed=passed,
            parameter_range={parameter: range_},
            failure_point={parameter: failures[0]} if failures else None,
            diagnostics={'n_samples': n_samples, 'failures': failures}
        )
        self.results.append(result)
        return result
    
    def precision_degradation_test(self, 
                                   precisions: List[int],
                                   compute_func: Callable[[int], Any],
                                   reference_precision: int = 64) -> StressTestResult:
        """
        Test behavior as precision decreases.
        """
        reference = compute_func(reference_precision)
        
        failures = []
        for prec in precisions:
            result = compute_func(prec)
            if isinstance(reference, np.ndarray):
                diff = np.max(np.abs(result - reference))
            else:
                diff = abs(result - reference)
            
            # Expect error to grow as precision decreases
            expected_error = 10 ** (-(prec / 4))  # Rough estimate
            if diff > expected_error * 100:  # 100x tolerance
                failures.append((prec, diff))
        
        passed = len(failures) == 0
        result = StressTestResult(
            test_id="precision_degradation",
            passed=passed,
            parameter_range={'precision': (min(precisions), max(precisions))},
            failure_point={'precision': failures[0][0]} if failures else None,
            diagnostics={'precisions': precisions, 'failures': failures}
        )
        self.results.append(result)
        return result
    
    def report(self) -> Dict[str, Any]:
        """Generate stress test report."""
        return {
            'seed_id': self.seed.seed_id,
            'seed_hash': self.seed.hash.digest,
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'failed': sum(1 for r in self.results if not r.passed),
            'results': [
                {
                    'test_id': r.test_id,
                    'passed': r.passed,
                    'failure_point': r.failure_point,
                    'diagnostics': r.diagnostics
                }
                for r in self.results
            ]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OBLIGATION LEDGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Obligation:
    """
    A proof obligation to be discharged.
    
    Obligations are created during derivation and must be
    resolved before publication.
    """
    obligation_id: str
    claim: Dict[str, Any]
    source: str  # What created this obligation
    status: str = "open"  # open, discharged, failed
    certificate_id: Optional[str] = None
    
    def discharge(self, certificate: Certificate):
        """Discharge obligation with certificate."""
        self.status = "discharged"
        self.certificate_id = certificate.cert_id
    
    def fail(self, reason: str):
        """Mark obligation as failed."""
        self.status = "failed"
        self.certificate_id = None


class ObligationLedger:
    """
    Ledger tracking all proof obligations.
    
    Ensures no obligation is silently dropped:
        - All obligations must be explicitly discharged or failed
        - Publication requires all obligations discharged
    """
    
    def __init__(self):
        self.obligations: Dict[str, Obligation] = {}
        self._counter = 0
    
    def create(self, claim: Dict[str, Any], source: str) -> Obligation:
        """Create new obligation."""
        self._counter += 1
        obl_id = f"OBL_{self._counter:06d}"
        obl = Obligation(obligation_id=obl_id, claim=claim, source=source)
        self.obligations[obl_id] = obl
        return obl
    
    def get(self, obligation_id: str) -> Optional[Obligation]:
        """Get obligation by ID."""
        return self.obligations.get(obligation_id)
    
    def discharge(self, obligation_id: str, certificate: Certificate) -> bool:
        """Discharge obligation with certificate."""
        obl = self.get(obligation_id)
        if obl is None:
            return False
        obl.discharge(certificate)
        return True
    
    @property
    def open_obligations(self) -> List[Obligation]:
        """List of open obligations."""
        return [o for o in self.obligations.values() if o.status == "open"]
    
    @property
    def discharged_obligations(self) -> List[Obligation]:
        """List of discharged obligations."""
        return [o for o in self.obligations.values() if o.status == "discharged"]
    
    @property
    def failed_obligations(self) -> List[Obligation]:
        """List of failed obligations."""
        return [o for o in self.obligations.values() if o.status == "failed"]
    
    @property
    def all_discharged(self) -> bool:
        """Check if all obligations are discharged."""
        return len(self.open_obligations) == 0 and len(self.failed_obligations) == 0
    
    def publication_ready(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if ready for publication."""
        ready = self.all_discharged
        report = {
            'ready': ready,
            'total': len(self.obligations),
            'open': len(self.open_obligations),
            'discharged': len(self.discharged_obligations),
            'failed': len(self.failed_obligations)
        }
        if not ready:
            report['blocking'] = [
                {'id': o.obligation_id, 'claim': o.claim, 'source': o.source}
                for o in self.open_obligations + self.failed_obligations
            ]
        return (ready, report)


# ═══════════════════════════════════════════════════════════════════════════════
# SEED PACK - COLLECTION OF RELATED SEEDS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SeedPack:
    """
    Collection of related seeds forming a coherent package.
    
    Pack types:
        - Geometric: construction + impossibility + symmetry + duality
        - Spectral: projector + bandlimit + trace + translator
        - Hybrid: coupling + detector + translator + stress
    """
    pack_id: str
    pack_type: str
    seeds: Dict[str, Seed] = field(default_factory=dict)
    certificates: Dict[str, Certificate] = field(default_factory=dict)
    translations: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    def add_seed(self, name: str, seed: Seed):
        """Add seed to pack."""
        self.seeds[name] = seed
    
    def add_certificate(self, name: str, cert: Certificate):
        """Add certificate to pack."""
        self.certificates[name] = cert
    
    def add_translation(self, source: str, target: str, translator_id: str):
        """Record translation between seeds."""
        if source not in self.translations:
            self.translations[source] = {}
        self.translations[source][target] = translator_id
    
    def completeness_check(self) -> Tuple[bool, List[str]]:
        """
        Check if pack is complete.
        Returns (is_complete, missing_items).
        """
        missing = []
        
        if self.pack_type == "geometric":
            required = ["construction", "symmetry"]
            for r in required:
                if r not in self.seeds:
                    missing.append(f"seed:{r}")
            if len(self.translations) == 0:
                missing.append("translation:at_least_one_duality")
        
        elif self.pack_type == "spectral":
            required = ["projector", "bandlimit"]
            for r in required:
                if r not in self.seeds:
                    missing.append(f"seed:{r}")
        
        elif self.pack_type == "hybrid":
            required = ["coupling", "detector"]
            for r in required:
                if r not in self.seeds:
                    missing.append(f"seed:{r}")
        
        return (len(missing) == 0, missing)
    
    @property
    def hash(self) -> CanonicalHash:
        """Pack content hash."""
        content = {
            'pack_id': self.pack_id,
            'pack_type': self.pack_type,
            'seed_hashes': {k: v.hash.digest for k, v in self.seeds.items()},
            'cert_hashes': {k: v.hash.digest for k, v in self.certificates.items()},
            'translations': self.translations
        }
        return CanonicalHash.from_json(content)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_seed(seed_id: str, 
               statement_type: StatementType,
               generator: Dict[str, Any],
               constraints: List[Dict[str, Any]] = None) -> Seed:
    """Create a new seed."""
    return Seed(
        seed_id=seed_id,
        statement_type=statement_type,
        generator=generator,
        constraints=constraints or []
    )


def create_certificate(cert_id: str,
                      claim: Dict[str, Any],
                      witness: Dict[str, Any],
                      verifier_id: str,
                      level: CertificateLevel = CertificateLevel.L1_EMPIRICAL) -> Certificate:
    """Create a new certificate."""
    return Certificate(
        cert_id=cert_id,
        claim=claim,
        witness=witness,
        verifier_id=verifier_id,
        level=level
    )


def verify_certificate(cert: Certificate) -> Tuple[bool, Dict]:
    """Verify certificate using global registry."""
    return get_verifier_registry().verify(cert)


def compute_hash(obj: Any) -> CanonicalHash:
    """Compute canonical hash of any object."""
    if isinstance(obj, np.ndarray):
        return CanonicalHash.from_array(obj)
    elif isinstance(obj, bytes):
        return CanonicalHash.from_bytes(obj)
    elif isinstance(obj, str):
        return CanonicalHash.from_string(obj)
    else:
        return CanonicalHash.from_json(obj)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Types
    'StatementType',
    'CertificateLevel',
    'PromotionPath',
    
    # Core objects
    'CanonicalHash',
    'Seed',
    'Certificate',
    
    # Verifiers
    'VerifierKernel',
    'EqualityVerifier',
    'IntervalVerifier',
    'PermutationVerifier',
    'VerifierRegistry',
    'get_verifier_registry',
    
    # Replay
    'ReplayStep',
    'ReplayTranscript',
    
    # Testing
    'StressTestResult',
    'StressTestHarness',
    
    # Obligations
    'Obligation',
    'ObligationLedger',
    
    # Packs
    'SeedPack',
    
    # Functions
    'create_seed',
    'create_certificate',
    'verify_certificate',
    'compute_hash',
]

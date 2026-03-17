"""
ATHENA OS - AtlasForge: PROOF PACK
==================================
Certificate System with Levels and Evidence

CERTIFICATE TYPES:
    - ChartCorridor: legality + injectivity + inverse admissibility
    - Enclosure: conservative bracketing/interval enclosures
    - Uniqueness: derivative-sign monotonicity, contraction bounds
    - ReplayDeterminism: deterministic replay verification

CERTIFICATE LEVELS:
    L0: Claim (no evidence)
    L1: Empirical (finite testing)
    L2: Certified Numeric (conservative, checkable)
    L3: Formal Proof (machine-verified)

TRUTH PROFILES:
    Explore: candidates stored but never promoted to ok_verified
    Validate: empirical checks permitted and enforced
    Prove: required obligations demand L2+ evidence

PROOFPACK STRUCTURE:
    - Collection of typed certificates
    - Evidence storage
    - Validator signatures
    - Level requirements per truth profile

SOURCES:
    - AtlasForge.docx Certificate Algebra
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum, IntEnum
from abc import ABC, abstractmethod
import numpy as np
import hashlib
import time
import json


# =============================================================================
# CERTIFICATE LEVELS
# =============================================================================

class CertificateLevel(IntEnum):
    """
    Certificate evidence levels.
    
    L0: Claim only (no evidence)
    L1: Empirical evidence (finite testing)
    L2: Certified numeric evidence (conservative, checkable)
    L3: Formal proof objects (machine-verified)
    """
    
    L0_CLAIM = 0
    L1_EMPIRICAL = 1
    L2_CERTIFIED = 2
    L3_FORMAL = 3


class TruthProfile(Enum):
    """
    Truth profiles determining minimum acceptable certificate levels.
    """
    
    EXPLORE = "explore"      # Candidates stored but not promoted
    VALIDATE = "validate"    # Empirical checks permitted
    PROVE = "prove"          # L2+ evidence required


# =============================================================================
# CERTIFICATE TYPES
# =============================================================================

class CertificateType(Enum):
    """Types of certificates in the proof pack."""
    
    CHART_CORRIDOR = "chart_corridor"
    ENCLOSURE = "enclosure"
    UNIQUENESS = "uniqueness"
    REPLAY_DETERMINISM = "replay_determinism"
    CONTRACTION = "contraction"
    BOUND = "bound"
    INVARIANT = "invariant"
    CUSTOM = "custom"


class CertificateStatus(Enum):
    """Status of a certificate."""
    
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    EXPIRED = "expired"


# =============================================================================
# EVIDENCE
# =============================================================================

@dataclass
class Evidence:
    """
    Evidence supporting a certificate claim.
    """
    
    evidence_type: str
    data: Dict[str, Any]
    
    # Provenance
    generated_at: float = field(default_factory=time.time)
    generator_id: Optional[str] = None
    
    # Replay info
    is_replayable: bool = False
    replay_seed: Optional[int] = None
    
    @property
    def content_hash(self) -> str:
        """Get content-addressed hash of evidence."""
        content = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": self.evidence_type,
            "data": self.data,
            "generated_at": self.generated_at,
            "content_hash": self.content_hash
        }


@dataclass
class IntervalEvidence(Evidence):
    """Evidence based on interval arithmetic."""
    
    lower: float = 0.0
    upper: float = 0.0
    
    def __post_init__(self):
        self.evidence_type = "interval"
        self.data = {
            "lower": self.lower,
            "upper": self.upper,
            "width": self.upper - self.lower
        }
    
    @property
    def width(self) -> float:
        return self.upper - self.lower
    
    def contains(self, x: float) -> bool:
        return self.lower <= x <= self.upper


@dataclass 
class SampleEvidence(Evidence):
    """Evidence based on finite sampling."""
    
    samples: List[float] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    
    def __post_init__(self):
        self.evidence_type = "sample"
        self.data = {
            "n_samples": len(self.samples),
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.passed / max(1, self.passed + self.failed)
        }
    
    @property
    def pass_rate(self) -> float:
        total = self.passed + self.failed
        return self.passed / total if total > 0 else 0.0


@dataclass
class BoundEvidence(Evidence):
    """Evidence providing bounds on a quantity."""
    
    quantity: str = ""
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    is_tight: bool = False
    
    def __post_init__(self):
        self.evidence_type = "bound"
        self.data = {
            "quantity": self.quantity,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "is_tight": self.is_tight
        }


# =============================================================================
# ABSTRACT CERTIFICATE
# =============================================================================

@dataclass
class Certificate(ABC):
    """
    Abstract base class for certificates.
    """
    
    cert_type: CertificateType
    level: CertificateLevel
    status: CertificateStatus = CertificateStatus.PENDING
    
    # Evidence
    evidence: List[Evidence] = field(default_factory=list)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    validated_at: Optional[float] = None
    validator_id: Optional[str] = None
    
    # Expiration
    expires_at: Optional[float] = None
    
    @property
    @abstractmethod
    def obligation_id(self) -> str:
        """Get unique ID for this obligation."""
        pass
    
    @property
    def is_valid(self) -> bool:
        """Check if certificate is currently valid."""
        if self.status != CertificateStatus.VALIDATED:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True
    
    @property
    def cert_id(self) -> str:
        """Get content-addressed certificate ID."""
        content = f"{self.cert_type.value}:{self.obligation_id}:{self.level.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to certificate."""
        self.evidence.append(evidence)
    
    def validate(self, validator_id: str) -> bool:
        """Attempt to validate the certificate."""
        # Check minimum evidence requirements
        if self.level >= CertificateLevel.L1_EMPIRICAL and not self.evidence:
            return False
        
        self.validated_at = time.time()
        self.validator_id = validator_id
        self.status = CertificateStatus.VALIDATED
        return True
    
    def reject(self, reason: str = "") -> None:
        """Reject the certificate."""
        self.status = CertificateStatus.REJECTED
        self.add_evidence(Evidence(
            evidence_type="rejection",
            data={"reason": reason}
        ))
    
    @abstractmethod
    def check(self) -> bool:
        """Check if certificate conditions are met."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "cert_id": self.cert_id,
            "cert_type": self.cert_type.value,
            "level": self.level.value,
            "status": self.status.value,
            "obligation_id": self.obligation_id,
            "evidence": [e.to_dict() for e in self.evidence],
            "created_at": self.created_at,
            "validated_at": self.validated_at
        }


# =============================================================================
# CONCRETE CERTIFICATES
# =============================================================================

@dataclass
class ChartCorridorCertificate(Certificate):
    """
    Certificate for chart validity on a corridor.
    
    Proves: legality + injectivity + inverse admissibility
    """
    
    chart_id: str = ""
    corridor_lower: float = 0.0
    corridor_upper: float = 0.0
    
    # Conditions
    is_legal: bool = False
    is_injective: bool = False
    is_inverse_admissible: bool = False
    
    # Bounds
    condition_number: Optional[float] = None
    lipschitz_constant: Optional[float] = None
    
    def __post_init__(self):
        self.cert_type = CertificateType.CHART_CORRIDOR
    
    @property
    def obligation_id(self) -> str:
        return f"corridor:{self.chart_id}:[{self.corridor_lower},{self.corridor_upper}]"
    
    @property
    def is_certified(self) -> bool:
        return self.is_legal and self.is_injective and self.is_inverse_admissible
    
    def check(self) -> bool:
        return self.is_certified and self.is_valid


@dataclass
class EnclosureCertificate(Certificate):
    """
    Certificate for conservative bracketing/interval enclosures.
    
    Proves: root/invariant lies within specified bounds
    """
    
    target_type: str = "root"  # "root", "fixed_point", "invariant"
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    
    # The enclosed value (if known)
    enclosed_value: Optional[float] = None
    
    # Verification method
    method: str = "interval"  # "interval", "bisection", "newton"
    
    def __post_init__(self):
        self.cert_type = CertificateType.ENCLOSURE
    
    @property
    def obligation_id(self) -> str:
        return f"enclosure:{self.target_type}:[{self.lower_bound},{self.upper_bound}]"
    
    @property
    def width(self) -> float:
        return self.upper_bound - self.lower_bound
    
    def check(self) -> bool:
        if not self.is_valid:
            return False
        if self.enclosed_value is not None:
            return self.lower_bound <= self.enclosed_value <= self.upper_bound
        return True


@dataclass
class UniquenessCertificate(Certificate):
    """
    Certificate for uniqueness of solution.
    
    Proves: strict derivative-sign monotonicity for roots,
    contraction bounds for fixed points
    """
    
    uniqueness_type: str = "monotonicity"  # "monotonicity", "contraction"
    
    # For monotonicity
    derivative_sign: Optional[int] = None  # +1 or -1
    
    # For contraction
    contraction_factor: Optional[float] = None
    
    # Region
    region_lower: float = 0.0
    region_upper: float = 0.0
    
    def __post_init__(self):
        self.cert_type = CertificateType.UNIQUENESS
    
    @property
    def obligation_id(self) -> str:
        return f"uniqueness:{self.uniqueness_type}:[{self.region_lower},{self.region_upper}]"
    
    def check(self) -> bool:
        if not self.is_valid:
            return False
        
        if self.uniqueness_type == "monotonicity":
            return self.derivative_sign in [1, -1]
        elif self.uniqueness_type == "contraction":
            return self.contraction_factor is not None and \
                   0 <= self.contraction_factor < 1
        return False


@dataclass
class ReplayDeterminismCertificate(Certificate):
    """
    Certificate for deterministic replay.
    
    Proves: replay under recorded environment produces identical outputs
    """
    
    # Environment contract
    platform: str = ""
    float_model: str = "ieee754"
    rng_seed: Optional[int] = None
    
    # Replay results
    original_hash: str = ""
    replay_hash: str = ""
    
    # Tolerance for "equivalent" (if not bitwise exact)
    tolerance: float = 0.0
    
    def __post_init__(self):
        self.cert_type = CertificateType.REPLAY_DETERMINISM
    
    @property
    def obligation_id(self) -> str:
        return f"replay:{self.original_hash}"
    
    @property
    def is_exact(self) -> bool:
        return self.original_hash == self.replay_hash
    
    def check(self) -> bool:
        if not self.is_valid:
            return False
        return self.is_exact or self.tolerance > 0


@dataclass
class ContractionCertificate(Certificate):
    """
    Certificate for contraction mapping (fixed point existence).
    
    Proves: ||F(x) - F(y)|| <= L||x - y|| with L < 1
    """
    
    lipschitz_constant: float = 0.0
    region_lower: float = 0.0
    region_upper: float = 0.0
    
    # Is the region mapped into itself?
    is_self_mapping: bool = False
    
    def __post_init__(self):
        self.cert_type = CertificateType.CONTRACTION
    
    @property
    def obligation_id(self) -> str:
        return f"contraction:L={self.lipschitz_constant}:[{self.region_lower},{self.region_upper}]"
    
    @property
    def is_contraction(self) -> bool:
        return 0 <= self.lipschitz_constant < 1
    
    def check(self) -> bool:
        return self.is_valid and self.is_contraction and self.is_self_mapping


# =============================================================================
# PROOF PACK
# =============================================================================

@dataclass
class ProofPack:
    """
    Collection of certificates with validation logic.
    
    The ProofPack is the machine-checkable justification
    attached to a Recipe.
    """
    
    # Certificates by type
    certificates: Dict[str, Certificate] = field(default_factory=dict)
    
    # Required obligations (derived from blueprint)
    required_obligations: Set[str] = field(default_factory=set)
    
    # Truth profile
    truth_profile: TruthProfile = TruthProfile.VALIDATE
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    last_verified: Optional[float] = None
    
    def add_certificate(self, cert: Certificate) -> None:
        """Add a certificate to the pack."""
        self.certificates[cert.cert_id] = cert
    
    def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        """Get certificate by ID."""
        return self.certificates.get(cert_id)
    
    def add_obligation(self, obligation_id: str) -> None:
        """Add a required obligation."""
        self.required_obligations.add(obligation_id)
    
    def get_certificates_for_obligation(self, obligation_id: str) -> List[Certificate]:
        """Get all certificates addressing an obligation."""
        return [c for c in self.certificates.values() 
                if c.obligation_id == obligation_id]
    
    def get_minimum_level(self) -> CertificateLevel:
        """Get minimum required level based on truth profile."""
        if self.truth_profile == TruthProfile.EXPLORE:
            return CertificateLevel.L0_CLAIM
        elif self.truth_profile == TruthProfile.VALIDATE:
            return CertificateLevel.L1_EMPIRICAL
        else:  # PROVE
            return CertificateLevel.L2_CERTIFIED
    
    def check_obligation(self, obligation_id: str) -> bool:
        """Check if an obligation is satisfied."""
        certs = self.get_certificates_for_obligation(obligation_id)
        if not certs:
            return False
        
        min_level = self.get_minimum_level()
        
        for cert in certs:
            if cert.level >= min_level and cert.check():
                return True
        
        return False
    
    def check_all_obligations(self) -> Tuple[bool, List[str]]:
        """
        Check all required obligations.
        
        Returns (all_satisfied, list_of_unsatisfied)
        """
        unsatisfied = []
        
        for obligation_id in self.required_obligations:
            if not self.check_obligation(obligation_id):
                unsatisfied.append(obligation_id)
        
        return len(unsatisfied) == 0, unsatisfied
    
    def get_verification_status(self) -> Dict[str, Any]:
        """Get detailed verification status."""
        all_ok, unsatisfied = self.check_all_obligations()
        
        cert_summary = {}
        for cert_type in CertificateType:
            certs_of_type = [c for c in self.certificates.values() 
                           if c.cert_type == cert_type]
            if certs_of_type:
                cert_summary[cert_type.value] = {
                    "count": len(certs_of_type),
                    "validated": sum(1 for c in certs_of_type if c.is_valid),
                    "levels": [c.level.value for c in certs_of_type]
                }
        
        return {
            "all_satisfied": all_ok,
            "unsatisfied_obligations": unsatisfied,
            "truth_profile": self.truth_profile.value,
            "minimum_level": self.get_minimum_level().value,
            "total_certificates": len(self.certificates),
            "certificates_by_type": cert_summary,
            "required_obligations": list(self.required_obligations)
        }
    
    @property
    def pack_id(self) -> str:
        """Get content-addressed pack ID."""
        cert_ids = sorted(self.certificates.keys())
        content = ":".join(cert_ids)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "pack_id": self.pack_id,
            "truth_profile": self.truth_profile.value,
            "certificates": {k: v.to_dict() for k, v in self.certificates.items()},
            "required_obligations": list(self.required_obligations),
            "created_at": self.created_at
        }


# =============================================================================
# PROOF PACK BUILDER
# =============================================================================

class ProofPackBuilder:
    """Builder for constructing proof packs."""
    
    def __init__(self, truth_profile: TruthProfile = TruthProfile.VALIDATE):
        self.pack = ProofPack(truth_profile=truth_profile)
    
    def add_chart_corridor(self, chart_id: str, lower: float, upper: float,
                          level: CertificateLevel = CertificateLevel.L1_EMPIRICAL,
                          **kwargs) -> ProofPackBuilder:
        """Add a chart corridor certificate."""
        cert = ChartCorridorCertificate(
            chart_id=chart_id,
            corridor_lower=lower,
            corridor_upper=upper,
            level=level,
            **kwargs
        )
        self.pack.add_certificate(cert)
        return self
    
    def add_enclosure(self, target_type: str, lower: float, upper: float,
                     level: CertificateLevel = CertificateLevel.L1_EMPIRICAL,
                     **kwargs) -> ProofPackBuilder:
        """Add an enclosure certificate."""
        cert = EnclosureCertificate(
            target_type=target_type,
            lower_bound=lower,
            upper_bound=upper,
            level=level,
            **kwargs
        )
        self.pack.add_certificate(cert)
        return self
    
    def add_uniqueness(self, uniqueness_type: str, lower: float, upper: float,
                      level: CertificateLevel = CertificateLevel.L1_EMPIRICAL,
                      **kwargs) -> ProofPackBuilder:
        """Add a uniqueness certificate."""
        cert = UniquenessCertificate(
            uniqueness_type=uniqueness_type,
            region_lower=lower,
            region_upper=upper,
            level=level,
            **kwargs
        )
        self.pack.add_certificate(cert)
        return self
    
    def add_replay(self, original_hash: str, replay_hash: str,
                  level: CertificateLevel = CertificateLevel.L1_EMPIRICAL,
                  **kwargs) -> ProofPackBuilder:
        """Add a replay determinism certificate."""
        cert = ReplayDeterminismCertificate(
            original_hash=original_hash,
            replay_hash=replay_hash,
            level=level,
            **kwargs
        )
        self.pack.add_certificate(cert)
        return self
    
    def add_contraction(self, lipschitz: float, lower: float, upper: float,
                       level: CertificateLevel = CertificateLevel.L2_CERTIFIED,
                       **kwargs) -> ProofPackBuilder:
        """Add a contraction certificate."""
        cert = ContractionCertificate(
            lipschitz_constant=lipschitz,
            region_lower=lower,
            region_upper=upper,
            level=level,
            **kwargs
        )
        self.pack.add_certificate(cert)
        return self
    
    def require_obligation(self, obligation_id: str) -> ProofPackBuilder:
        """Add a required obligation."""
        self.pack.add_obligation(obligation_id)
        return self
    
    def build(self) -> ProofPack:
        """Build and return the proof pack."""
        return self.pack


# =============================================================================
# VALIDATION
# =============================================================================

def validate_proof_pack() -> bool:
    """Validate proof pack module."""
    
    # Test certificate levels
    assert CertificateLevel.L0_CLAIM < CertificateLevel.L3_FORMAL
    
    # Test evidence
    ev = IntervalEvidence(lower=1.0, upper=2.0)
    assert ev.width == 1.0
    assert ev.contains(1.5)
    
    # Test chart corridor certificate
    cert = ChartCorridorCertificate(
        chart_id="test_chart",
        corridor_lower=0.0,
        corridor_upper=10.0,
        level=CertificateLevel.L1_EMPIRICAL,
        is_legal=True,
        is_injective=True,
        is_inverse_admissible=True
    )
    assert cert.is_certified
    cert.validate("test_validator")
    assert cert.is_valid
    
    # Test enclosure certificate
    enc_cert = EnclosureCertificate(
        target_type="root",
        lower_bound=1.0,
        upper_bound=2.0,
        enclosed_value=1.5,
        level=CertificateLevel.L2_CERTIFIED
    )
    enc_cert.validate("validator")
    assert enc_cert.check()
    
    # Test contraction certificate
    cont_cert = ContractionCertificate(
        lipschitz_constant=0.5,
        region_lower=0.0,
        region_upper=1.0,
        is_self_mapping=True,
        level=CertificateLevel.L2_CERTIFIED
    )
    cont_cert.validate("validator")
    assert cont_cert.check()
    
    # Test proof pack builder
    pack = (ProofPackBuilder(TruthProfile.VALIDATE)
            .add_chart_corridor("chart1", 0.0, 10.0, 
                               is_legal=True, is_injective=True, 
                               is_inverse_admissible=True)
            .add_enclosure("root", 1.0, 2.0, enclosed_value=1.5)
            .require_obligation("enclosure:root:[1.0,2.0]")
            .build())
    
    # Validate certificates
    for cert in pack.certificates.values():
        cert.validate("test_validator")
    
    # Check status
    status = pack.get_verification_status()
    assert status["total_certificates"] == 2
    
    return True


if __name__ == "__main__":
    print("Validating Proof Pack Module...")
    assert validate_proof_pack()
    print("✓ Proof Pack Module validated")
    
    # Demo
    print("\n--- ProofPack Demo ---")
    
    # Build a proof pack
    pack = (ProofPackBuilder(TruthProfile.PROVE)
            .add_chart_corridor(
                "log_chart", 0.1, 10.0,
                level=CertificateLevel.L2_CERTIFIED,
                is_legal=True,
                is_injective=True,
                is_inverse_admissible=True,
                condition_number=2.5
            )
            .add_enclosure(
                "root", 1.41, 1.42,
                level=CertificateLevel.L2_CERTIFIED,
                enclosed_value=1.4142,
                method="bisection"
            )
            .add_uniqueness(
                "monotonicity", 1.0, 2.0,
                level=CertificateLevel.L2_CERTIFIED,
                derivative_sign=1
            )
            .add_contraction(
                0.3, 0.0, 1.0,
                level=CertificateLevel.L2_CERTIFIED,
                is_self_mapping=True
            )
            .require_obligation("enclosure:root:[1.41,1.42]")
            .require_obligation("uniqueness:monotonicity:[1.0,2.0]")
            .build())
    
    # Validate all certificates
    for cert in pack.certificates.values():
        cert.validate("demo_validator")
    
    print(f"\nProofPack ID: {pack.pack_id}")
    print(f"Truth Profile: {pack.truth_profile.value}")
    print(f"Minimum Level: L{pack.get_minimum_level().value}")
    
    print(f"\nCertificates ({len(pack.certificates)}):")
    for cert_id, cert in pack.certificates.items():
        print(f"  {cert.cert_type.value}: L{cert.level.value} "
              f"[{'✓' if cert.is_valid else '✗'}]")
    
    status = pack.get_verification_status()
    print(f"\nVerification Status:")
    print(f"  All Satisfied: {status['all_satisfied']}")
    print(f"  Unsatisfied: {status['unsatisfied_obligations']}")

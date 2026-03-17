"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ATLAS FORGE - Certificate System                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Proof-carrying certificates for mathematical results.
"""

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type
from datetime import datetime
import json
import math

from atlasforge.core.types import Interval, FloatPolicy, DEFAULT_FLOAT_POLICY
from atlasforge.core.base import ContentAddressed
from atlasforge.core.enums import CertificateLevel, TruthProfile, ObligationType


@dataclass
class Certificate(ContentAddressed):
    """Base class for all certificates."""
    
    level: CertificateLevel = CertificateLevel.L0_CLAIM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    issuer: str = "atlasforge"
    valid: bool = True
    source_hash: str = ""
    evidence_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    @abstractmethod
    def certificate_type(self) -> str:
        pass
    
    @abstractmethod
    def verify(self) -> bool:
        pass
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'type': self.certificate_type,
            'level': self.level.value,
            'source': self.source_hash,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'certificate_type': self.certificate_type,
            'level': self.level.value,
            'timestamp': self.timestamp.isoformat(),
            'valid': self.valid,
            'source_hash': self.source_hash,
        }
    
    def invalidate(self, reason: str = ""):
        self.valid = False
        self.metadata['invalidation_reason'] = reason


@dataclass
class EnclosureCertificate(Certificate):
    """Certificate: x* ∈ [a, b]"""
    
    solution: float = 0.0
    enclosure: Interval = field(default_factory=lambda: Interval.closed(0, 0))
    residual: float = float('inf')
    interval_arithmetic_used: bool = False
    contraction_verified: bool = False
    
    @property
    def certificate_type(self) -> str:
        return "enclosure"
    
    def verify(self) -> bool:
        if not self.valid:
            return False
        if not self.enclosure.contains(self.solution):
            self.invalidate("Solution not in enclosure")
            return False
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnclosureCertificate':
        return cls(
            level=CertificateLevel(data.get('level', 0)),
            solution=data.get('solution', 0.0),
            enclosure=Interval.closed(
                data.get('enclosure_lo', 0),
                data.get('enclosure_hi', 0)
            ),
            residual=data.get('residual', float('inf')),
            interval_arithmetic_used=data.get('interval_arithmetic_used', False),
        )


@dataclass
class UniquenessCertificate(Certificate):
    """Certificate: ∃! x* ∈ [a, b] : H(x*) = 0"""
    
    region: Interval = field(default_factory=lambda: Interval.closed(0, 0))
    unique_solution: Optional[float] = None
    contraction_factor: float = 0.0
    derivative_bounds: Tuple[float, float] = (0.0, 0.0)
    
    @property
    def certificate_type(self) -> str:
        return "uniqueness"
    
    def verify(self) -> bool:
        if not self.valid:
            return False
        if self.contraction_factor >= 1.0:
            self.invalidate("Contraction factor >= 1")
            return False
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniquenessCertificate':
        return cls(
            level=CertificateLevel(data.get('level', 0)),
            contraction_factor=data.get('contraction_factor', 0.0),
        )


@dataclass
class CorridorCertificate(Certificate):
    """Certificate: Chart is valid on domain"""
    
    chart_name: str = ""
    domain: Interval = field(default_factory=lambda: Interval.closed(0, 0))
    jacobian_bounds: Tuple[float, float] = (0.0, float('inf'))
    smoothness_order: int = 1
    
    @property
    def certificate_type(self) -> str:
        return "corridor"
    
    def verify(self) -> bool:
        if not self.valid:
            return False
        lo, hi = self.jacobian_bounds
        if lo <= 0 or not math.isfinite(hi):
            return False
        if hi / lo > 1e10:
            self.invalidate("Poor conditioning")
            return False
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CorridorCertificate':
        return cls(
            level=CertificateLevel(data.get('level', 0)),
            chart_name=data.get('chart_name', ''),
        )


@dataclass
class ReplayCertificate(Certificate):
    """Certificate: Computation is deterministically replayable"""
    
    input_hash: str = ""
    recipe_hash: str = ""
    output_hash: str = ""
    float_policy: FloatPolicy = field(default_factory=lambda: DEFAULT_FLOAT_POLICY)
    replayed: bool = False
    replay_matches: bool = False
    replay_output_hash: str = ""
    
    @property
    def certificate_type(self) -> str:
        return "replay"
    
    def verify(self) -> bool:
        if not self.valid:
            return False
        if self.replayed:
            return self.replay_matches
        return True
    
    def record_replay(self, replay_output_hash: str):
        self.replayed = True
        self.replay_output_hash = replay_output_hash
        self.replay_matches = (replay_output_hash == self.output_hash)
        if not self.replay_matches:
            self.invalidate("Replay mismatch")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReplayCertificate':
        return cls(
            level=CertificateLevel(data.get('level', 0)),
            input_hash=data.get('input_hash', ''),
            recipe_hash=data.get('recipe_hash', ''),
            output_hash=data.get('output_hash', ''),
        )


@dataclass
class StabilityCertificate(Certificate):
    """Certificate: Result is numerically stable"""
    
    condition_number: float = 1.0
    backward_error: float = 0.0
    forward_error_bound: float = float('inf')
    
    @property
    def certificate_type(self) -> str:
        return "stability"
    
    def verify(self) -> bool:
        if not self.valid:
            return False
        if self.condition_number > 1e10:
            self.invalidate(f"Ill-conditioned: κ = {self.condition_number}")
            return False
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StabilityCertificate':
        return cls(
            level=CertificateLevel(data.get('level', 0)),
            condition_number=data.get('condition_number', 1.0),
        )


@dataclass
class CertificateBundle(ContentAddressed):
    """Bundle of certificates for a single result."""
    
    certificates: List[Certificate] = field(default_factory=list)
    result_hash: str = ""
    
    @property
    def level(self) -> CertificateLevel:
        if not self.certificates:
            return CertificateLevel.L0_CLAIM
        return min(c.level for c in self.certificates)
    
    @property
    def all_valid(self) -> bool:
        return all(c.valid for c in self.certificates)
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'result': self.result_hash,
            'certificates': [c.content_hash() for c in self.certificates],
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'result_hash': self.result_hash,
            'certificates': [c.to_dict() for c in self.certificates],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CertificateBundle':
        return cls(result_hash=data.get('result_hash', ''))
    
    def add(self, cert: Certificate):
        self.certificates.append(cert)
    
    def get(self, cert_type: str) -> Optional[Certificate]:
        for c in self.certificates:
            if c.certificate_type == cert_type:
                return c
        return None
    
    def verify_all(self) -> bool:
        return all(c.verify() for c in self.certificates)
    
    def satisfies_profile(self, profile: TruthProfile) -> bool:
        return self.level >= profile.minimum_level and self.all_valid


@dataclass
class ProofPack(ContentAddressed):
    """Complete proof package for a mathematical result."""
    
    result_value: Any = None
    result_hash: str = ""
    bundle: CertificateBundle = field(default_factory=CertificateBundle)
    obligations: List[Dict[str, Any]] = field(default_factory=list)
    replay_recipe_hash: str = ""
    replay_log_hash: str = ""
    complete: bool = False
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'result': self.result_hash,
            'bundle': self.bundle.content_hash(),
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'result_hash': self.result_hash,
            'complete': self.complete,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProofPack':
        return cls(result_hash=data.get('result_hash', ''))
    
    def check_completeness(self):
        all_discharged = all(o.get('discharged', False) for o in self.obligations)
        self.complete = all_discharged and self.bundle.all_valid
    
    def discharge_obligation(self, obligation_type: ObligationType, cert: Certificate) -> bool:
        for obl in self.obligations:
            if obl['type'] == obligation_type.value and not obl['discharged']:
                if cert.level >= CertificateLevel(obl['required_level']) and cert.valid:
                    obl['discharged'] = True
                    obl['discharging_certificate'] = cert.content_hash()
                    self.bundle.add(cert)
                    self.check_completeness()
                    return True
        return False


class CertificateFactory:
    """Factory for creating certificates."""
    
    @staticmethod
    def enclosure(solution: float, enclosure: Interval, residual: float, 
                  verified: bool = False, source_hash: str = "") -> EnclosureCertificate:
        return EnclosureCertificate(
            level=CertificateLevel.L2_CERTIFIED if verified else CertificateLevel.L1_EMPIRICAL,
            solution=solution, enclosure=enclosure, residual=residual,
            interval_arithmetic_used=verified, source_hash=source_hash)
    
    @staticmethod
    def uniqueness(region: Interval, solution: float, derivative_bounds: Tuple[float, float],
                   source_hash: str = "") -> UniquenessCertificate:
        lo, hi = derivative_bounds
        valid = lo > 0 or hi < 0
        return UniquenessCertificate(
            level=CertificateLevel.L2_CERTIFIED if valid else CertificateLevel.L1_EMPIRICAL,
            region=region, unique_solution=solution, derivative_bounds=derivative_bounds,
            contraction_factor=0.5 if valid else 1.0, source_hash=source_hash)
    
    @staticmethod
    def corridor(chart_name: str, domain: Interval, jacobian_bounds: Tuple[float, float],
                 source_hash: str = "") -> CorridorCertificate:
        lo, hi = jacobian_bounds
        valid = lo > 0 and math.isfinite(hi) and hi / lo < 1e10
        return CorridorCertificate(
            level=CertificateLevel.L2_CERTIFIED if valid else CertificateLevel.L1_EMPIRICAL,
            chart_name=chart_name, domain=domain, jacobian_bounds=jacobian_bounds,
            source_hash=source_hash)
    
    @staticmethod
    def replay(input_hash: str, recipe_hash: str, output_hash: str) -> ReplayCertificate:
        return ReplayCertificate(
            level=CertificateLevel.L1_EMPIRICAL,
            input_hash=input_hash, recipe_hash=recipe_hash, output_hash=output_hash)
    
    @staticmethod
    def stability(condition_number: float, source_hash: str = "") -> StabilityCertificate:
        valid = condition_number < 1e10
        return StabilityCertificate(
            level=CertificateLevel.L2_CERTIFIED if valid else CertificateLevel.L1_EMPIRICAL,
            condition_number=condition_number, source_hash=source_hash)

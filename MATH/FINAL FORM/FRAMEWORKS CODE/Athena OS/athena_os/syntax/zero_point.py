"""
ATHENA OS - SYNTAX ZERO POINT
=============================
Z_0 Tracking System

From SYNTAX.docx:

ZERO POINT (??_0):
    A typed Zero Point together with:
    
    1. Collapse projections κ_X : X ⇀ ??_0 for each sort X ∈ {S, A, I, O}
       - All failure paths factor through κ (absorptive)
    
    2. Seed/generation maps σ_X : ??_0 ⇀ X parameterized by constraints
       - All constructive paths out of ??_0 are typed and obligation-guided
       (constrained)

Z-RECORD SCHEMA:
    Every z ∈ ??_0 must carry:
    - Coordinate (which cell it collapsed from/into)
    - Phase (lexical, parse, validate, runtime)
    - Kind (erasure, rejection, exception, divergence)
    - Provenance (where it came from)
    - Severity (how bad)
    - Recoverability (can we fix it)
    
Z-CHAMBER (ABSOLUTE ZERO):
    - Z-universality: All collapse/drift factors through canonical Z-schema
    - Repair seeds: Admissible repair classes per kind/phase
    - Revocation: Any drift witness can revoke a certificate
    - Governance: Who/what can update policies
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Set, Optional, Any, Tuple, 
    Callable, Union, TypeVar, Generic
)
from enum import Enum, auto
from datetime import datetime
import hashlib
import json

from .core import (
    Pole, RepLevel, Direction, CollapseKind, CollapsePhase,
    Artifact, SyntaxArtifact, AntiArtifact, InArtifact, OutArtifact,
    Provenance, WorldState, Observation, ExecutionResult
)
from .coordinates import CrystalCoord, CrystalIndex


# =============================================================================
# Z-RECORD SEVERITY
# =============================================================================

class ZSeverity(Enum):
    """Severity levels for Z-records."""
    
    INFO = "info"           # Informational only
    WARNING = "warning"     # Potential issue
    ERROR = "error"         # Definite failure
    CRITICAL = "critical"   # System-level failure
    FATAL = "fatal"         # Unrecoverable
    
    @property
    def level(self) -> int:
        """Numeric severity level."""
        return {
            ZSeverity.INFO: 0,
            ZSeverity.WARNING: 1,
            ZSeverity.ERROR: 2,
            ZSeverity.CRITICAL: 3,
            ZSeverity.FATAL: 4
        }[self]
    
    def __lt__(self, other: 'ZSeverity') -> bool:
        return self.level < other.level


class ZRecoverability(Enum):
    """Recoverability classes for Z-records."""
    
    AUTO = "automatic"         # Automatically recoverable
    HANDLER = "handler"        # Recoverable by handler/policy
    RESTART = "restart"        # Recoverable only by restart/repair
    UNRECOVERABLE = "none"     # Not recoverable within model


# =============================================================================
# Z-RECORD
# =============================================================================

@dataclass
class ZRecord:
    """
    A record in the Zero Point ??_0.
    
    Every collapse, failure, or drift is recorded as a Z-record
    with full provenance and coordinate tracking.
    """
    
    # Required fields (rec_{Z_0})
    record_id: str
    coordinate: CrystalCoord
    phase: CollapsePhase
    kind: CollapseKind
    severity: ZSeverity
    recoverability: ZRecoverability
    
    # Provenance
    source_artifact_id: Optional[str] = None
    source_pole: Optional[Pole] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Details
    message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    
    # Repair information
    repair_seed: Optional[str] = None
    repair_attempts: int = 0
    repaired: bool = False
    
    @property
    def is_recoverable(self) -> bool:
        """Check if this record is recoverable."""
        return self.recoverability != ZRecoverability.UNRECOVERABLE
    
    @property
    def canonical_form(self) -> str:
        """Get canonical string form for hashing."""
        return f"{self.coordinate}:{self.phase.value}:{self.kind.value}:{self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "record_id": self.record_id,
            "coordinate": str(self.coordinate),
            "phase": self.phase.value,
            "kind": self.kind.value,
            "severity": self.severity.value,
            "recoverability": self.recoverability.value,
            "source_artifact_id": self.source_artifact_id,
            "source_pole": self.source_pole.value if self.source_pole else None,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "context": self.context,
            "repair_seed": self.repair_seed,
            "repair_attempts": self.repair_attempts,
            "repaired": self.repaired
        }
    
    @classmethod
    def from_anti_artifact(cls, anti: AntiArtifact, coord: CrystalCoord) -> 'ZRecord':
        """Create Z-record from an AntiArtifact."""
        record_id = f"Z_{anti.artifact_id}_{coord.index}"
        
        # Map collapse kind to severity
        severity_map = {
            CollapseKind.LEXICAL: ZSeverity.ERROR,
            CollapseKind.SYNTACTIC: ZSeverity.ERROR,
            CollapseKind.SEMANTIC: ZSeverity.ERROR,
            CollapseKind.DYNAMIC: ZSeverity.CRITICAL,
            CollapseKind.TIMEOUT: ZSeverity.WARNING,
            CollapseKind.ABORT: ZSeverity.CRITICAL
        }
        
        # Map recoverable flag
        recov = ZRecoverability.HANDLER if anti.recoverable else ZRecoverability.RESTART
        
        return cls(
            record_id=record_id,
            coordinate=coord,
            phase=anti.phase,
            kind=anti.kind,
            severity=severity_map[anti.kind],
            recoverability=recov,
            source_artifact_id=anti.original_artifact_id,
            source_pole=Pole.A,
            message=anti.message
        )


# =============================================================================
# COLLAPSE PROJECTIONS (κ)
# =============================================================================

class CollapseProjection:
    """
    Collapse projection κ_X : X ⇀ ??_0
    
    Maps artifacts to Z-records when they fail/collapse.
    All failure paths factor through κ (absorptive property).
    """
    
    def __init__(self, source_pole: Pole):
        self.source_pole = source_pole
        self._projections: Dict[str, ZRecord] = {}
    
    def project(self, artifact: Artifact, 
                coord: CrystalCoord,
                phase: CollapsePhase,
                kind: CollapseKind,
                message: str = "",
                severity: ZSeverity = ZSeverity.ERROR,
                recoverability: ZRecoverability = ZRecoverability.RESTART) -> ZRecord:
        """
        Project an artifact to a Z-record (collapse it).
        
        κ_X(artifact) → Z-record
        """
        record_id = f"Z_kappa_{artifact.artifact_id}_{coord.index}"
        
        record = ZRecord(
            record_id=record_id,
            coordinate=coord,
            phase=phase,
            kind=kind,
            severity=severity,
            recoverability=recoverability,
            source_artifact_id=artifact.artifact_id,
            source_pole=artifact.pole,
            message=message
        )
        
        self._projections[record_id] = record
        return record
    
    def project_execution_failure(self, 
                                  artifact: SyntaxArtifact,
                                  coord: CrystalCoord,
                                  error: Exception) -> ZRecord:
        """Project an execution failure to Z-record."""
        return self.project(
            artifact=artifact,
            coord=coord,
            phase=CollapsePhase.RUNTIME,
            kind=CollapseKind.DYNAMIC,
            message=str(error),
            severity=ZSeverity.CRITICAL
        )
    
    def project_parse_failure(self,
                              artifact: SyntaxArtifact,
                              coord: CrystalCoord,
                              message: str) -> ZRecord:
        """Project a parse failure to Z-record."""
        return self.project(
            artifact=artifact,
            coord=coord,
            phase=CollapsePhase.PARSE,
            kind=CollapseKind.SYNTACTIC,
            message=message,
            severity=ZSeverity.ERROR,
            recoverability=ZRecoverability.HANDLER
        )
    
    def get_all(self) -> List[ZRecord]:
        """Get all projections."""
        return list(self._projections.values())


# =============================================================================
# SEED GENERATION MAPS (σ)
# =============================================================================

@dataclass
class SeedConstraints:
    """
    Constraints for seed generation.
    
    σ_X is parameterized by these constraints.
    """
    
    target_pole: Pole
    target_rep: RepLevel
    obligations: List[str] = field(default_factory=list)
    type_constraints: Dict[str, str] = field(default_factory=dict)
    resource_budget: Dict[str, float] = field(default_factory=dict)


class SeedGenerator:
    """
    Seed generation map σ_X : ??_0 ⇀ X
    
    Generates artifacts from Z-records (repair/recovery).
    All constructive paths out of ??_0 are typed and obligation-guided.
    """
    
    def __init__(self, target_pole: Pole):
        self.target_pole = target_pole
        self._generators: Dict[str, Callable[[ZRecord, SeedConstraints], Optional[Artifact]]] = {}
        self._register_default_generators()
    
    def _register_default_generators(self):
        """Register default seed generators for each kind."""
        
        def gen_from_lexical(z: ZRecord, c: SeedConstraints) -> Optional[SyntaxArtifact]:
            """Generate repair seed for lexical errors."""
            # Default: return empty text artifact
            from .core import TextArtifact
            return TextArtifact(
                content="",
                pole=Pole.S,
                rep_level=RepLevel.TXT,
                provenance=Provenance(
                    source_id=z.record_id,
                    operation="seed_from_lexical"
                )
            )
        
        def gen_from_syntactic(z: ZRecord, c: SeedConstraints) -> Optional[SyntaxArtifact]:
            """Generate repair seed for syntactic errors."""
            from .core import TextArtifact
            return TextArtifact(
                content="()",  # Minimal valid syntax
                pole=Pole.S,
                rep_level=RepLevel.TXT,
                provenance=Provenance(
                    source_id=z.record_id,
                    operation="seed_from_syntactic"
                )
            )
        
        self._generators[CollapseKind.LEXICAL.value] = gen_from_lexical
        self._generators[CollapseKind.SYNTACTIC.value] = gen_from_syntactic
    
    def register_generator(self, kind: CollapseKind, 
                          gen: Callable[[ZRecord, SeedConstraints], Optional[Artifact]]):
        """Register a custom generator for a collapse kind."""
        self._generators[kind.value] = gen
    
    def generate(self, z_record: ZRecord, 
                 constraints: SeedConstraints) -> Optional[Artifact]:
        """
        Generate artifact from Z-record.
        
        σ_X(z_record, constraints) → artifact or None
        """
        if constraints.target_pole != self.target_pole:
            return None
        
        generator = self._generators.get(z_record.kind.value)
        if generator is None:
            return None
        
        # Update Z-record
        z_record.repair_attempts += 1
        
        result = generator(z_record, constraints)
        
        if result is not None:
            z_record.repair_seed = result.artifact_id
        
        return result


# =============================================================================
# ZERO POINT CHAMBER
# =============================================================================

class ZeroChamber:
    """
    The Zero Point Chamber (??_0).
    
    Central registry for all collapse/failure records with:
    - Z-universality: All collapse/drift factors through here
    - Repair seeds: Admissible repair classes per kind/phase
    - Revocation: Any drift witness can revoke a certificate
    - Governance: Policy updates are recorded
    """
    
    def __init__(self):
        # All Z-records
        self._records: Dict[str, ZRecord] = {}
        
        # Collapse projections per pole
        self._kappa: Dict[Pole, CollapseProjection] = {
            pole: CollapseProjection(pole) for pole in Pole
        }
        
        # Seed generators per pole
        self._sigma: Dict[Pole, SeedGenerator] = {
            pole: SeedGenerator(pole) for pole in Pole
        }
        
        # Governance log
        self._governance_log: List[Dict[str, Any]] = []
        
        # Revoked certificates
        self._revoked: Set[str] = set()
    
    def record(self, z_record: ZRecord) -> str:
        """Record a Z-record in the chamber."""
        self._records[z_record.record_id] = z_record
        return z_record.record_id
    
    def get(self, record_id: str) -> Optional[ZRecord]:
        """Get a Z-record by ID."""
        return self._records.get(record_id)
    
    def collapse(self, artifact: Artifact, 
                coord: CrystalCoord,
                phase: CollapsePhase,
                kind: CollapseKind,
                message: str = "") -> ZRecord:
        """
        Collapse an artifact to Z-record using κ.
        
        This is the main entry point for recording failures.
        """
        kappa = self._kappa[artifact.pole]
        z_record = kappa.project(artifact, coord, phase, kind, message)
        self.record(z_record)
        return z_record
    
    def seed(self, z_record: ZRecord, 
             constraints: SeedConstraints) -> Optional[Artifact]:
        """
        Generate repair seed from Z-record using σ.
        
        This is the main entry point for recovery.
        """
        sigma = self._sigma[constraints.target_pole]
        return sigma.generate(z_record, constraints)
    
    def revoke(self, certificate_id: str, witness: ZRecord) -> bool:
        """
        Revoke a certificate based on drift witness.
        
        Any drift witness can revoke a certificate.
        """
        if certificate_id in self._revoked:
            return False
        
        self._revoked.add(certificate_id)
        
        self._governance_log.append({
            "action": "revoke",
            "certificate_id": certificate_id,
            "witness_id": witness.record_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def is_revoked(self, certificate_id: str) -> bool:
        """Check if a certificate has been revoked."""
        return certificate_id in self._revoked
    
    def log_governance(self, action: str, details: Dict[str, Any]) -> None:
        """Log a governance action."""
        self._governance_log.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_by_severity(self, min_severity: ZSeverity) -> List[ZRecord]:
        """Get all records at or above a severity level."""
        return [r for r in self._records.values() 
                if r.severity.level >= min_severity.level]
    
    def get_by_coordinate(self, coord: CrystalCoord) -> List[ZRecord]:
        """Get all records at a specific coordinate."""
        return [r for r in self._records.values() 
                if r.coordinate == coord]
    
    def get_by_phase(self, phase: CollapsePhase) -> List[ZRecord]:
        """Get all records for a specific phase."""
        return [r for r in self._records.values() if r.phase == phase]
    
    def get_unrepaired(self) -> List[ZRecord]:
        """Get all unrepaired records that are recoverable."""
        return [r for r in self._records.values() 
                if r.is_recoverable and not r.repaired]
    
    def statistics(self) -> Dict[str, Any]:
        """Get chamber statistics."""
        by_severity = {s.value: 0 for s in ZSeverity}
        by_phase = {p.value: 0 for p in CollapsePhase}
        by_kind = {k.value: 0 for k in CollapseKind}
        by_pole = {p.value: 0 for p in Pole}
        
        repaired = 0
        unrepaired = 0
        
        for r in self._records.values():
            by_severity[r.severity.value] += 1
            by_phase[r.phase.value] += 1
            by_kind[r.kind.value] += 1
            if r.source_pole:
                by_pole[r.source_pole.value] += 1
            
            if r.repaired:
                repaired += 1
            elif r.is_recoverable:
                unrepaired += 1
        
        return {
            "total_records": len(self._records),
            "by_severity": by_severity,
            "by_phase": by_phase,
            "by_kind": by_kind,
            "by_pole": by_pole,
            "repaired": repaired,
            "unrepaired": unrepaired,
            "revoked_certificates": len(self._revoked),
            "governance_actions": len(self._governance_log)
        }


# =============================================================================
# GLOBAL ZERO POINT INSTANCE
# =============================================================================

# Singleton chamber
_global_chamber: Optional[ZeroChamber] = None


def get_zero_chamber() -> ZeroChamber:
    """Get the global Zero Point chamber."""
    global _global_chamber
    if _global_chamber is None:
        _global_chamber = ZeroChamber()
    return _global_chamber


def reset_zero_chamber() -> None:
    """Reset the global chamber (for testing)."""
    global _global_chamber
    _global_chamber = None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_zero_point() -> bool:
    """Validate zero point module."""
    
    # Reset for clean test
    reset_zero_chamber()
    chamber = get_zero_chamber()
    
    # Create test coordinate
    coord = CrystalCoord(
        pole=Pole.S,
        lens=LensFamily.B12,
        direction=Direction.SPIN,
        rep_level=RepLevel.TXT
    )
    
    # Import here to avoid circular import
    from .core import TextArtifact, LensFamily
    
    # Test artifact
    artifact = TextArtifact(
        content="invalid syntax {{",
        pole=Pole.S,
        rep_level=RepLevel.TXT
    )
    
    # Test collapse
    z_record = chamber.collapse(
        artifact=artifact,
        coord=coord,
        phase=CollapsePhase.PARSE,
        kind=CollapseKind.SYNTACTIC,
        message="Unexpected token '{{'"
    )
    
    assert z_record.record_id is not None
    assert z_record.phase == CollapsePhase.PARSE
    assert z_record.kind == CollapseKind.SYNTACTIC
    assert z_record.is_recoverable
    
    # Test retrieval
    retrieved = chamber.get(z_record.record_id)
    assert retrieved == z_record
    
    # Test seed generation
    constraints = SeedConstraints(
        target_pole=Pole.S,
        target_rep=RepLevel.TXT
    )
    
    repaired = chamber.seed(z_record, constraints)
    assert repaired is not None
    assert z_record.repair_attempts == 1
    
    # Test statistics
    stats = chamber.statistics()
    assert stats["total_records"] == 1
    assert stats["by_phase"]["parse"] == 1
    
    # Test revocation
    cert_id = "test_cert_001"
    assert chamber.revoke(cert_id, z_record)
    assert chamber.is_revoked(cert_id)
    assert not chamber.revoke(cert_id, z_record)  # Can't revoke twice
    
    # Test severity comparison
    assert ZSeverity.INFO < ZSeverity.ERROR
    assert ZSeverity.CRITICAL > ZSeverity.WARNING
    
    # Test Z-record from AntiArtifact
    from .core import AntiArtifact
    anti = AntiArtifact(
        kind=CollapseKind.DYNAMIC,
        phase=CollapsePhase.RUNTIME,
        message="Division by zero",
        recoverable=False,
        pole=Pole.A,
        rep_level=RepLevel.OBS
    )
    
    z_from_anti = ZRecord.from_anti_artifact(anti, coord)
    assert z_from_anti.kind == CollapseKind.DYNAMIC
    assert z_from_anti.severity == ZSeverity.CRITICAL
    
    # Cleanup
    reset_zero_chamber()
    
    return True


if __name__ == "__main__":
    print("Validating SYNTAX zero point...")
    assert validate_zero_point()
    print("✓ SYNTAX zero point validated")

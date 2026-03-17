"""
ATHENA OS - DEEP CRYSTAL SYNTHESIS
==================================
Ma'at: The Judgment System and Soul Thermodynamics

From DEEP_CRYSTAL_SYNTHESIS.docx §3:

MA'AT JUDGMENT PROTOCOL:
    
    H_Nun   : Hilbert space of the soul (Ab states)
    Sw      : Feather of Truth (reference standard)
    V_Isfet : Error space with 42 orthonormal modes
    Ω̂       : Comparator operator (heart weighing)
    
THE WEIGHING:
    cos(θ) = ⟨Ab|Sw⟩ / (||Ab|| × ||Sw||)
    
    θ < ε  → Maa-Kheru (justified)
    θ ≥ ε  → Ammit (devoured)

42 NEGATIVE CONFESSIONS:
    Each Isfet_n is an orthonormal basis vector representing
    a mode of transgression. The heart must project to zero
    on all 42 modes: ⟨Ab|Isfet_n⟩ = 0 for all n.

THERMODYNAMICS:
    Ethics = entropy management under ∇S
    Measurement introduces irreversibility
    Thoth (scribe) reduces spikes, preserves coherence
    Deletion is thermodynamic hygiene
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import numpy as np
import math


# =============================================================================
# ISFET CATALOG (42 MODES OF TRANSGRESSION)
# =============================================================================

class IsfetTier(Enum):
    """Classification of transgression severity."""
    
    TIER_1 = "social"       # Basic social violations (1-14)
    TIER_2 = "speech"       # Speech and thought (15-28)
    TIER_3 = "inner"        # Inner corruption (29-38)
    TIER_4 = "hubris"       # Structural/cosmic violations (39-42)


@dataclass
class IsfetMode:
    """
    A single mode of transgression (Isfet).
    
    Each is an orthonormal basis vector in error space.
    """
    
    index: int                    # 1-42
    name: str                     # Name of transgression
    tier: IsfetTier               # Severity tier
    weight: float = 1.0           # Entropy contribution
    
    def vector(self, dim: int = 42) -> np.ndarray:
        """Get orthonormal basis vector."""
        v = np.zeros(dim)
        v[self.index - 1] = 1.0
        return v


# The 42 Negative Confessions (simplified)
ISFET_CATALOG: List[IsfetMode] = [
    # Tier 1: Social (1-14)
    IsfetMode(1, "injustice", IsfetTier.TIER_1),
    IsfetMode(2, "robbery", IsfetTier.TIER_1),
    IsfetMode(3, "violence", IsfetTier.TIER_1),
    IsfetMode(4, "theft", IsfetTier.TIER_1),
    IsfetMode(5, "murder", IsfetTier.TIER_1, weight=2.0),
    IsfetMode(6, "fraud", IsfetTier.TIER_1),
    IsfetMode(7, "deception", IsfetTier.TIER_1),
    IsfetMode(8, "waste", IsfetTier.TIER_1),
    IsfetMode(9, "false_witness", IsfetTier.TIER_1),
    IsfetMode(10, "adultery", IsfetTier.TIER_1),
    IsfetMode(11, "abuse", IsfetTier.TIER_1),
    IsfetMode(12, "cruelty", IsfetTier.TIER_1),
    IsfetMode(13, "neglect", IsfetTier.TIER_1),
    IsfetMode(14, "greed", IsfetTier.TIER_1),
    
    # Tier 2: Speech/Thought (15-28)
    IsfetMode(15, "false_speech", IsfetTier.TIER_2),
    IsfetMode(16, "slander", IsfetTier.TIER_2),
    IsfetMode(17, "gossip", IsfetTier.TIER_2),
    IsfetMode(18, "cursing", IsfetTier.TIER_2),
    IsfetMode(19, "arrogance", IsfetTier.TIER_2),
    IsfetMode(20, "boasting", IsfetTier.TIER_2),
    IsfetMode(21, "deafness_to_truth", IsfetTier.TIER_2),
    IsfetMode(22, "spite", IsfetTier.TIER_2),
    IsfetMode(23, "envy", IsfetTier.TIER_2),
    IsfetMode(24, "wrath", IsfetTier.TIER_2),
    IsfetMode(25, "impatience", IsfetTier.TIER_2),
    IsfetMode(26, "quarreling", IsfetTier.TIER_2),
    IsfetMode(27, "harsh_words", IsfetTier.TIER_2),
    IsfetMode(28, "lying", IsfetTier.TIER_2),
    
    # Tier 3: Inner (29-38)
    IsfetMode(29, "impurity_of_heart", IsfetTier.TIER_3, weight=1.5),
    IsfetMode(30, "cowardice", IsfetTier.TIER_3),
    IsfetMode(31, "ingratitude", IsfetTier.TIER_3),
    IsfetMode(32, "faithlessness", IsfetTier.TIER_3),
    IsfetMode(33, "self_deception", IsfetTier.TIER_3, weight=1.5),
    IsfetMode(34, "hardness_of_heart", IsfetTier.TIER_3),
    IsfetMode(35, "indifference", IsfetTier.TIER_3),
    IsfetMode(36, "despair", IsfetTier.TIER_3),
    IsfetMode(37, "attachment", IsfetTier.TIER_3),
    IsfetMode(38, "delusion", IsfetTier.TIER_3, weight=1.5),
    
    # Tier 4: Hubris/Structural (39-42)
    IsfetMode(39, "blasphemy", IsfetTier.TIER_4, weight=2.0),
    IsfetMode(40, "desecration", IsfetTier.TIER_4, weight=2.0),
    IsfetMode(41, "cosmic_disorder", IsfetTier.TIER_4, weight=3.0),
    IsfetMode(42, "against_maat", IsfetTier.TIER_4, weight=3.0),
]


# =============================================================================
# SOUL STATE (AB - THE HEART)
# =============================================================================

@dataclass
class AbState:
    """
    Ab: The Heart / Soul State Vector
    
    The heart contains the record of all actions,
    projected onto the 42-dimensional Isfet space.
    """
    
    name: str                              # Name of soul
    vector: np.ndarray = field(default_factory=lambda: np.zeros(42))
    
    # Additional state components
    ka_alignment: float = 1.0              # Ka (vital force) health
    ba_freedom: float = 1.0                # Ba (personality) mobility
    akh_luminosity: float = 0.0            # Akh (glorified spirit) attainment
    ren_integrity: bool = True             # Ren (name) preserved
    
    def add_transgression(self, isfet_index: int, magnitude: float = 1.0) -> None:
        """Record a transgression in the heart."""
        if 1 <= isfet_index <= 42:
            mode = ISFET_CATALOG[isfet_index - 1]
            self.vector[isfet_index - 1] += magnitude * mode.weight
    
    def confession(self, isfet_index: int, sincerity: float = 1.0) -> None:
        """Confess and reduce transgression (negative confession)."""
        if 1 <= isfet_index <= 42:
            reduction = self.vector[isfet_index - 1] * sincerity
            self.vector[isfet_index - 1] -= reduction
            self.vector[isfet_index - 1] = max(0, self.vector[isfet_index - 1])
    
    @property
    def total_isfet(self) -> float:
        """Total accumulated Isfet (disorder)."""
        return float(np.sum(self.vector))
    
    @property
    def entropy(self) -> float:
        """Entropy of the soul state."""
        # Normalize to probability distribution
        total = np.sum(np.abs(self.vector)) + 1e-10
        p = np.abs(self.vector) / total
        # Shannon entropy
        p_nonzero = p[p > 0]
        return -float(np.sum(p_nonzero * np.log(p_nonzero + 1e-10)))
    
    @property
    def norm(self) -> float:
        """Euclidean norm of heart vector."""
        return float(np.linalg.norm(self.vector))


# =============================================================================
# FEATHER OF TRUTH (SW - THE REFERENCE STANDARD)
# =============================================================================

@dataclass
class FeatherStandard:
    """
    Sw: The Feather of Ma'at / Reference Standard
    
    The invariant reference against which hearts are weighed.
    Represents zero-transgression ideal state.
    
    Properties:
    - C_maat: invariant constant (cannot drift)
    - Zero-mass ideal (detachment)
    - Shu-constraint (lightness/space)
    """
    
    c_maat: float = 1.0           # Ma'at constant (invariant)
    drift: float = 0.0            # Calibration drift (should be 0)
    
    @property
    def vector(self) -> np.ndarray:
        """Reference vector (zero Isfet)."""
        return np.zeros(42)
    
    @property
    def weight(self) -> float:
        """Weight of the feather (ideally minimal)."""
        return self.c_maat * (1 + self.drift)
    
    def verify_calibration(self) -> bool:
        """Verify standard has not drifted."""
        return abs(self.drift) < 1e-10


# =============================================================================
# OMEGA COMPARATOR (THE SCALES)
# =============================================================================

class JudgmentResult(Enum):
    """Result of Ma'at judgment."""
    
    MAA_KHERU = "justified"        # Heart lighter than feather
    AMMIT = "devoured"             # Heart heavier than feather
    PENDING = "pending"            # Judgment incomplete


@dataclass
class OmegaComparator:
    """
    Ω̂: The Scales of Ma'at / Heart Weighing Comparator
    
    The half-space classifier that determines fate.
    
    Operations:
    1. Project heart onto Isfet space
    2. Compute alignment angle with reference
    3. Apply threshold decision
    """
    
    feather: FeatherStandard = field(default_factory=FeatherStandard)
    threshold_epsilon: float = 0.1    # Tolerance for imperfection
    
    def alignment(self, ab: AbState) -> float:
        """
        Compute alignment metric: cos(θ) = ⟨Ab|Sw⟩ / (||Ab|| × ||Sw||)
        
        Since Sw is zero vector, we use distance from zero.
        Returns value in [0, 1] where 1 is perfect alignment.
        """
        norm = ab.norm
        if norm < 1e-10:
            return 1.0  # Perfect alignment with zero
        
        # Inverse relationship: lower norm = higher alignment
        return 1.0 / (1.0 + norm)
    
    def total_error(self, ab: AbState) -> float:
        """
        Compute total weighted error: E_total = Σ_n |⟨Ab|Isfet_n⟩|²
        """
        return float(np.sum(ab.vector ** 2))
    
    def per_mode_errors(self, ab: AbState) -> Dict[str, float]:
        """Get error contribution from each Isfet mode."""
        errors = {}
        for i, mode in enumerate(ISFET_CATALOG):
            errors[mode.name] = float(ab.vector[i] ** 2)
        return errors
    
    def weigh(self, ab: AbState) -> Tuple[JudgmentResult, float]:
        """
        Perform the weighing of the heart.
        
        Returns (result, alignment_score).
        """
        alignment = self.alignment(ab)
        
        if alignment >= (1.0 - self.threshold_epsilon):
            return (JudgmentResult.MAA_KHERU, alignment)
        else:
            return (JudgmentResult.AMMIT, alignment)
    
    def certificate(self, ab: AbState) -> Dict[str, any]:
        """
        Generate judgment certificate.
        
        Full audit record of the weighing.
        """
        result, alignment = self.weigh(ab)
        
        return {
            "soul_name": ab.name,
            "result": result.value,
            "alignment": alignment,
            "total_isfet": ab.total_isfet,
            "entropy": ab.entropy,
            "ka_alignment": ab.ka_alignment,
            "ba_freedom": ab.ba_freedom,
            "akh_luminosity": ab.akh_luminosity,
            "ren_preserved": ab.ren_integrity,
            "feather_calibrated": self.feather.verify_calibration(),
            "threshold": self.threshold_epsilon,
            "per_mode_errors": self.per_mode_errors(ab)
        }


# =============================================================================
# THOTH SCRIBE (AUDIT AND CORRECTION)
# =============================================================================

@dataclass
class ThothScribe:
    """
    Thoth: The Scribe / Audit and Correction System
    
    Records all judgments and performs error correction.
    
    Functions:
    - Logging introduces irreversibility
    - Reduces entropy spikes
    - Preserves coherence
    """
    
    ledger: List[Dict] = field(default_factory=list)
    
    def record(self, certificate: Dict) -> int:
        """Record judgment in ledger. Returns record ID."""
        record_id = len(self.ledger)
        certificate["record_id"] = record_id
        self.ledger.append(certificate)
        return record_id
    
    def query(self, soul_name: str) -> List[Dict]:
        """Query ledger for soul."""
        return [r for r in self.ledger if r.get("soul_name") == soul_name]
    
    def correction_factor(self, ab: AbState) -> np.ndarray:
        """
        Compute correction to reduce entropy spikes.
        
        Returns vector to subtract from Ab state.
        """
        # Identify spike modes (> 2σ from mean)
        mean = np.mean(ab.vector)
        std = np.std(ab.vector) + 1e-10
        
        correction = np.zeros(42)
        for i in range(42):
            z_score = (ab.vector[i] - mean) / std
            if z_score > 2.0:
                # Reduce spike toward mean
                correction[i] = (ab.vector[i] - mean) * 0.5
        
        return correction
    
    def apply_correction(self, ab: AbState) -> AbState:
        """Apply Thoth's correction to soul state."""
        correction = self.correction_factor(ab)
        ab.vector = ab.vector - correction
        ab.vector = np.maximum(ab.vector, 0)  # No negative values
        return ab


# =============================================================================
# ANUBIS GATEKEEPER
# =============================================================================

@dataclass
class AnubisGatekeeper:
    """
    Anubis: The Guide and Validator
    
    Prepares souls for judgment and validates process.
    """
    
    def prepare(self, ab: AbState) -> AbState:
        """Prepare soul for judgment (final reconciliation)."""
        # Normalize state
        if ab.norm > 0:
            ab.vector = ab.vector / ab.norm * ab.total_isfet
        return ab
    
    def validate_feather(self, feather: FeatherStandard) -> bool:
        """Validate feather calibration."""
        return feather.verify_calibration()
    
    def escort(self, ab: AbState, result: JudgmentResult) -> str:
        """Escort soul to appropriate destination."""
        if result == JudgmentResult.MAA_KHERU:
            return "A'aru"  # Fields of Reeds (paradise)
        else:
            return "Ammit"  # Devoured (annihilation)


# =============================================================================
# COMPLETE JUDGMENT HALL
# =============================================================================

@dataclass
class HallOfTwoTruths:
    """
    The Hall of Two Truths: Complete Judgment System
    
    Integrates all components of Ma'at judgment.
    """
    
    comparator: OmegaComparator = field(default_factory=OmegaComparator)
    scribe: ThothScribe = field(default_factory=ThothScribe)
    gatekeeper: AnubisGatekeeper = field(default_factory=AnubisGatekeeper)
    
    def full_judgment(self, ab: AbState) -> Dict:
        """
        Perform complete judgment protocol.
        
        1. Anubis prepares soul
        2. Thoth applies corrections
        3. Ω̂ weighs heart
        4. Thoth records judgment
        5. Anubis escorts to destination
        """
        # Preparation
        ab = self.gatekeeper.prepare(ab)
        
        # Correction
        ab = self.scribe.apply_correction(ab)
        
        # Validation
        feather_valid = self.gatekeeper.validate_feather(self.comparator.feather)
        
        # Weighing
        result, alignment = self.comparator.weigh(ab)
        
        # Certificate
        cert = self.comparator.certificate(ab)
        cert["feather_valid"] = feather_valid
        
        # Record
        record_id = self.scribe.record(cert)
        cert["record_id"] = record_id
        
        # Escort
        destination = self.gatekeeper.escort(ab, result)
        cert["destination"] = destination
        
        return cert


# =============================================================================
# VALIDATION
# =============================================================================

def validate_maat() -> bool:
    """Validate Ma'at judgment system."""
    
    # Test Isfet catalog
    assert len(ISFET_CATALOG) == 42
    
    # Test AbState
    ab = AbState(name="Test Soul")
    assert ab.total_isfet == 0
    assert ab.norm == 0
    
    ab.add_transgression(1, 0.5)  # injustice
    ab.add_transgression(5, 1.0)  # murder (weight 2.0)
    assert ab.total_isfet > 0
    
    # Test confession
    ab.confession(1, 0.5)
    
    # Test FeatherStandard
    feather = FeatherStandard()
    assert feather.verify_calibration()
    assert np.allclose(feather.vector, np.zeros(42))
    
    # Test OmegaComparator
    comparator = OmegaComparator()
    
    # Pure soul should be justified
    pure_soul = AbState(name="Pure")
    result, alignment = comparator.weigh(pure_soul)
    assert result == JudgmentResult.MAA_KHERU
    assert alignment == 1.0
    
    # Heavy soul should be devoured
    heavy_soul = AbState(name="Heavy")
    for i in range(1, 43):
        heavy_soul.add_transgression(i, 10.0)
    result, alignment = comparator.weigh(heavy_soul)
    assert result == JudgmentResult.AMMIT
    
    # Test certificate
    cert = comparator.certificate(pure_soul)
    assert "result" in cert
    assert "alignment" in cert
    
    # Test ThothScribe
    scribe = ThothScribe()
    record_id = scribe.record(cert)
    assert record_id == 0
    
    # Test HallOfTwoTruths
    hall = HallOfTwoTruths()
    
    mixed_soul = AbState(name="Mixed")
    mixed_soul.add_transgression(15, 0.05)  # Minor speech fault
    
    full_cert = hall.full_judgment(mixed_soul)
    assert "destination" in full_cert
    assert "record_id" in full_cert
    
    return True


if __name__ == "__main__":
    print("Validating Ma'at Judgment System...")
    assert validate_maat()
    print("✓ Ma'at module validated")
    
    # Demo
    print("\n--- Ma'at Judgment Demo ---")
    hall = HallOfTwoTruths()
    
    soul = AbState(name="Ani")
    soul.add_transgression(7, 0.1)   # Minor deception
    soul.add_transgression(19, 0.05)  # Slight arrogance
    
    cert = hall.full_judgment(soul)
    print(f"Soul: {cert['soul_name']}")
    print(f"Result: {cert['result']}")
    print(f"Alignment: {cert['alignment']:.4f}")
    print(f"Destination: {cert['destination']}")

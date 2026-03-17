"""
ATHENA OS - IFÁ KERNEL: DIVINATION MODULE
=========================================
The Measurement Protocol and Ebó Error Correction

DIVINATION AS MEASUREMENT:
    The casting procedure (Dídá Ifá) is a measurement protocol
    that collapses superposition into definite state.
    
    |Ψ⟩ → |Odù_k⟩ with probability |⟨Odù_k|Ψ⟩|²

CASTING METHODS:
    1. Ìbò (Shell casting): Simple binary selection
    2. Ọ̀pẹ̀lẹ̀ (Chain): 8 half-shells → 8-bit word
    3. Ìkín (Palm nuts): Full ceremonial procedure

EBÓ (SACRIFICE) AS ERROR CORRECTION:
    Ebó is not appeasement but STATE MODIFICATION.
    
    Types of corrections:
    - Ebó Rírú: Amplify desired state
    - Ebó Ẹ̀tùtù: Attenuate undesired state
    - Ebó Ìdájọ́: Phase correction

THE PROJECTION OPERATOR:
    P̂_k = |Odù_k⟩⟨Odù_k|
    
    Divination performs: |Ψ'⟩ = P̂_k|Ψ⟩ / ||P̂_k|Ψ⟩||

SOURCES:
    - Traditional Ifá corpus
    - HBAS-Ω Protocol: Ọpẹ́-256 formalization
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import numpy as np

from .hypercube import Q8Hypercube, Odu, OduSuperposition, PrincipalOdu


# =============================================================================
# CASTING METHODS
# =============================================================================

class CastingMethod(Enum):
    """Methods of divination casting."""
    
    IBO = "ibo"           # Shell casting (simple binary)
    OPELE = "opele"       # Chain casting (8-bit)
    IKIN = "ikin"         # Palm nut ceremony (full)


class CastingResult(Enum):
    """Result of a single cast."""
    
    OPEN = 1      # | (one mark) - Yang/Active
    CLOSED = 0    # : (two marks) - Yin/Potential


# =============================================================================
# EBÓ TYPES
# =============================================================================

class EboType(Enum):
    """Types of ebó (sacrifice/correction)."""
    
    RIRU = "riru"         # Amplification (increase desired)
    ETUTU = "etutu"       # Attenuation (decrease undesired)
    IDAJO = "idajo"       # Phase correction
    SARA = "sara"         # Distribution/sharing


class EboStatus(Enum):
    """Status of ebó prescription."""
    
    PRESCRIBED = "prescribed"   # Recommended
    COMPLETED = "completed"     # Performed
    PENDING = "pending"         # Not yet done
    REJECTED = "rejected"       # Refused (dangerous)


# =============================================================================
# DIVINATION SESSION
# =============================================================================

@dataclass
class DivinationQuery:
    """A query brought to divination."""
    
    question: str
    querent_name: str = "Client"
    category: str = "general"
    timestamp: float = 0.0
    
    # Optional context
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CastResult:
    """Result of a divination casting."""
    
    odu_index: int
    odu: Odu
    method: CastingMethod
    
    # Raw casting data
    right_leg_bits: List[int] = field(default_factory=list)
    left_leg_bits: List[int] = field(default_factory=list)
    
    # Derived information
    is_ire: bool = True           # Good fortune?
    requires_ebo: bool = False
    ebo_type: Optional[EboType] = None
    
    @property
    def binary(self) -> str:
        return format(self.odu_index, '08b')


@dataclass
class DivinationReading:
    """Complete divination reading."""
    
    query: DivinationQuery
    primary_odu: CastResult
    
    # Secondary Odù (if applicable)
    secondary_odu: Optional[CastResult] = None
    
    # Verses and prescriptions
    ese: List[str] = field(default_factory=list)
    prescriptions: List[str] = field(default_factory=list)
    taboos: List[str] = field(default_factory=list)
    
    # Ebó details
    ebo_required: bool = False
    ebo_details: Dict[str, Any] = field(default_factory=dict)
    
    def summary(self) -> str:
        """Generate reading summary."""
        lines = [
            f"=== DIVINATION READING ===",
            f"Query: {self.query.question}",
            f"Primary Odù: {self.primary_odu.odu.name}",
            f"Pattern: {self.primary_odu.binary}",
            f"Fortune: {'Ire (Good)' if self.primary_odu.is_ire else 'Ibi (Challenge)'}",
        ]
        
        if self.secondary_odu:
            lines.append(f"Secondary Odù: {self.secondary_odu.odu.name}")
        
        if self.ebo_required:
            lines.append(f"Ebó Required: Yes ({self.ebo_details.get('type', 'general')})")
        
        return "\n".join(lines)


# =============================================================================
# CASTING ENGINE
# =============================================================================

class CastingEngine:
    """
    Engine for performing divination casts.
    
    Simulates the traditional casting methods with proper
    probability distributions.
    """
    
    def __init__(self, hypercube: Q8Hypercube, seed: Optional[int] = None):
        self.q8 = hypercube
        self.rng = np.random.default_rng(seed)
    
    def cast_single_bit(self) -> CastingResult:
        """
        Cast a single bit (coin flip).
        
        Traditional method uses cowrie shell position.
        """
        return CastingResult.OPEN if self.rng.random() > 0.5 else CastingResult.CLOSED
    
    def cast_leg(self) -> Tuple[int, List[int]]:
        """
        Cast one leg (4 bits / nibble).
        
        Returns (nibble_value, list_of_bits)
        """
        bits = [self.cast_single_bit().value for _ in range(4)]
        nibble = sum(b << (3 - i) for i, b in enumerate(bits))
        return nibble, bits
    
    def cast_opele(self) -> CastResult:
        """
        Cast using Ọ̀pẹ̀lẹ̀ (divination chain).
        
        The chain has 8 half-shells that fall open or closed.
        """
        right_nibble, right_bits = self.cast_leg()
        left_nibble, left_bits = self.cast_leg()
        
        index = (left_nibble << 4) | right_nibble
        odu = self.q8.get_odu(index)
        
        return CastResult(
            odu_index=index,
            odu=odu,
            method=CastingMethod.OPELE,
            right_leg_bits=right_bits,
            left_leg_bits=left_bits,
            is_ire=self._determine_ire(odu),
            requires_ebo=self._determine_ebo_required(odu)
        )
    
    def cast_ikin(self) -> CastResult:
        """
        Cast using Ìkín (palm nuts).
        
        The Babalawo grabs palm nuts; 1 or 2 remaining
        determines each mark. Full ceremony requires
        multiple rounds.
        """
        # Simplified: same as opele but with different marking
        # In reality, this is a much longer ceremony
        result = self.cast_opele()
        result.method = CastingMethod.IKIN
        return result
    
    def cast_ibo(self) -> Tuple[CastingResult, CastingResult]:
        """
        Cast Ìbò (shell selection).
        
        Simple binary choice used to determine Ire/Ibi
        and other binary questions.
        """
        return (self.cast_single_bit(), self.cast_single_bit())
    
    def cast_from_superposition(self, sup: OduSuperposition) -> CastResult:
        """
        Cast from a quantum superposition.
        
        Collapses superposition according to probabilities.
        """
        index = sup.measure()
        odu = self.q8.get_odu(index)
        
        return CastResult(
            odu_index=index,
            odu=odu,
            method=CastingMethod.OPELE,
            is_ire=self._determine_ire(odu),
            requires_ebo=self._determine_ebo_required(odu)
        )
    
    def _determine_ire(self, odu: Odu) -> bool:
        """
        Determine if Odù indicates good fortune (Ire).
        
        Simplified: even parity tends to be more favorable.
        """
        # Even parity slightly favors Ire
        base_prob = 0.55 if odu.parity == "even" else 0.45
        return self.rng.random() < base_prob
    
    def _determine_ebo_required(self, odu: Odu) -> bool:
        """
        Determine if ebó is required.
        
        Higher Hamming weight = more complex situation = more likely ebó.
        """
        prob = odu.hamming_weight / 12  # Max ~0.67 for weight 8
        return self.rng.random() < prob


# =============================================================================
# EBÓ SYSTEM
# =============================================================================

@dataclass
class EboPrescription:
    """A prescribed ebó (sacrifice/offering)."""
    
    ebo_type: EboType
    description: str
    
    # What to offer
    materials: List[str] = field(default_factory=list)
    
    # Where/how
    location: str = "crossroads"
    timing: str = "before sunset"
    
    # Effects
    target_odu: Optional[int] = None
    amplification_factor: float = 1.0
    attenuation_factor: float = 0.0
    
    status: EboStatus = EboStatus.PRESCRIBED


class EboEngine:
    """
    Engine for ebó (sacrifice) as state modification.
    
    Ebó is not superstition but a PROTOCOL for modifying
    the probability distribution over states.
    """
    
    def __init__(self, hypercube: Q8Hypercube):
        self.q8 = hypercube
        self.performed_ebos: List[EboPrescription] = []
    
    def prescribe_ebo(self, reading: DivinationReading) -> EboPrescription:
        """
        Generate ebó prescription based on reading.
        """
        odu = reading.primary_odu.odu
        is_ire = reading.primary_odu.is_ire
        
        if is_ire:
            # Good fortune: amplify
            return EboPrescription(
                ebo_type=EboType.RIRU,
                description=f"Ebó to strengthen {odu.name}",
                materials=["honey", "white cloth", "palm oil"],
                location="shrine",
                target_odu=odu.index,
                amplification_factor=1.5
            )
        else:
            # Challenge: attenuate negative
            return EboPrescription(
                ebo_type=EboType.ETUTU,
                description=f"Ebó to mitigate {odu.name}",
                materials=["rooster", "kola nut", "gin"],
                location="crossroads",
                target_odu=odu.index,
                attenuation_factor=0.5
            )
    
    def apply_ebo(self, state: OduSuperposition, 
                   ebo: EboPrescription) -> OduSuperposition:
        """
        Apply ebó to modify state distribution.
        
        This is the mathematical implementation of ritual action.
        """
        amps = state.amplitudes.copy()
        
        if ebo.ebo_type == EboType.RIRU:
            # Amplify target
            if ebo.target_odu is not None:
                amps[ebo.target_odu] *= ebo.amplification_factor
        
        elif ebo.ebo_type == EboType.ETUTU:
            # Attenuate target
            if ebo.target_odu is not None:
                amps[ebo.target_odu] *= ebo.attenuation_factor
        
        elif ebo.ebo_type == EboType.IDAJO:
            # Phase correction: rotate phase of target
            if ebo.target_odu is not None:
                amps[ebo.target_odu] *= np.exp(1j * np.pi / 4)
        
        elif ebo.ebo_type == EboType.SARA:
            # Distribute: spread amplitude to neighbors
            if ebo.target_odu is not None:
                target = ebo.target_odu
                target_amp = amps[target] * 0.5
                amps[target] *= 0.5
                neighbors = self.q8.vertices[target].neighbors()
                for n in neighbors:
                    amps[n] += target_amp / 8
        
        ebo.status = EboStatus.COMPLETED
        self.performed_ebos.append(ebo)
        
        return OduSuperposition(amps)
    
    def calculate_correction_needed(self, current: OduSuperposition,
                                     target: OduSuperposition) -> Dict[str, Any]:
        """
        Calculate the correction needed to move from current to target.
        """
        current_probs = current.probabilities()
        target_probs = target.probabilities()
        
        diff = target_probs - current_probs
        
        # Find states needing amplification (positive diff)
        amplify_indices = np.where(diff > 0.01)[0]
        
        # Find states needing attenuation (negative diff)
        attenuate_indices = np.where(diff < -0.01)[0]
        
        return {
            "amplify": amplify_indices.tolist(),
            "attenuate": attenuate_indices.tolist(),
            "total_correction": float(np.sum(np.abs(diff)))
        }


# =============================================================================
# DIVINATION SYSTEM
# =============================================================================

class DivinationSystem:
    """
    Complete divination system integrating casting and ebó.
    """
    
    def __init__(self, hypercube: Q8Hypercube, seed: Optional[int] = None):
        self.q8 = hypercube
        self.casting = CastingEngine(hypercube, seed)
        self.ebo = EboEngine(hypercube)
        
        # Reading history
        self.readings: List[DivinationReading] = []
    
    def divine(self, question: str, 
               querent: str = "Client",
               method: CastingMethod = CastingMethod.OPELE) -> DivinationReading:
        """
        Perform a divination reading.
        """
        query = DivinationQuery(
            question=question,
            querent_name=querent,
            timestamp=len(self.readings)
        )
        
        # Primary cast
        if method == CastingMethod.OPELE:
            primary = self.casting.cast_opele()
        elif method == CastingMethod.IKIN:
            primary = self.casting.cast_ikin()
        else:
            primary = self.casting.cast_opele()
        
        # Generate reading
        reading = DivinationReading(
            query=query,
            primary_odu=primary,
            ese=self._get_ese(primary.odu),
            prescriptions=self._get_prescriptions(primary.odu),
            taboos=self._get_taboos(primary.odu),
            ebo_required=primary.requires_ebo
        )
        
        # If ebó required, generate prescription
        if reading.ebo_required:
            ebo = self.ebo.prescribe_ebo(reading)
            reading.ebo_details = {
                "type": ebo.ebo_type.value,
                "description": ebo.description,
                "materials": ebo.materials
            }
        
        self.readings.append(reading)
        
        return reading
    
    def divine_with_state(self, question: str,
                          state: OduSuperposition) -> DivinationReading:
        """
        Perform divination from a known superposition state.
        """
        query = DivinationQuery(question=question)
        primary = self.casting.cast_from_superposition(state)
        
        reading = DivinationReading(
            query=query,
            primary_odu=primary,
            ese=self._get_ese(primary.odu),
            ebo_required=primary.requires_ebo
        )
        
        self.readings.append(reading)
        return reading
    
    def perform_ebo(self, reading: DivinationReading,
                    state: OduSuperposition) -> OduSuperposition:
        """
        Perform prescribed ebó on state.
        """
        if not reading.ebo_required:
            return state
        
        ebo = self.ebo.prescribe_ebo(reading)
        return self.ebo.apply_ebo(state, ebo)
    
    def _get_ese(self, odu: Odu) -> List[str]:
        """Get verses for Odù (simplified)."""
        return [
            f"This is {odu.name}, the sign of {odu.parity} balance.",
            f"Hamming weight {odu.hamming_weight} indicates {'complexity' if odu.hamming_weight > 4 else 'simplicity'}."
        ]
    
    def _get_prescriptions(self, odu: Odu) -> List[str]:
        """Get prescriptions for Odù."""
        if odu.parity == "even":
            return ["Maintain balance", "Honor commitments"]
        else:
            return ["Seek guidance", "Prepare for change"]
    
    def _get_taboos(self, odu: Odu) -> List[str]:
        """Get taboos for Odù."""
        return ["Avoid deceit", "Respect elders"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get divination statistics."""
        if not self.readings:
            return {"total_readings": 0}
        
        ire_count = sum(1 for r in self.readings if r.primary_odu.is_ire)
        ebo_count = sum(1 for r in self.readings if r.ebo_required)
        
        return {
            "total_readings": len(self.readings),
            "ire_readings": ire_count,
            "ibi_readings": len(self.readings) - ire_count,
            "ebo_prescribed": ebo_count,
            "ebo_performed": len(self.ebo.performed_ebos)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_divination() -> bool:
    """Validate divination module."""
    
    q8 = Q8Hypercube()
    
    # Test casting engine
    casting = CastingEngine(q8, seed=42)
    
    bit = casting.cast_single_bit()
    assert bit in [CastingResult.OPEN, CastingResult.CLOSED]
    
    result = casting.cast_opele()
    assert 0 <= result.odu_index < 256
    assert result.method == CastingMethod.OPELE
    
    ikin_result = casting.cast_ikin()
    assert ikin_result.method == CastingMethod.IKIN
    
    # Test with superposition
    sup = OduSuperposition.uniform()
    cast_sup = casting.cast_from_superposition(sup)
    assert 0 <= cast_sup.odu_index < 256
    
    # Test ebó engine
    ebo_engine = EboEngine(q8)
    
    reading = DivinationReading(
        query=DivinationQuery("Test?"),
        primary_odu=result
    )
    
    ebo = ebo_engine.prescribe_ebo(reading)
    assert ebo.status == EboStatus.PRESCRIBED
    
    new_state = ebo_engine.apply_ebo(sup, ebo)
    assert isinstance(new_state, OduSuperposition)
    assert ebo.status == EboStatus.COMPLETED
    
    # Test divination system
    system = DivinationSystem(q8, seed=42)
    
    reading = system.divine("Will I succeed?")
    assert reading.primary_odu is not None
    assert len(reading.ese) > 0
    
    stats = system.get_statistics()
    assert stats["total_readings"] == 1
    
    return True


if __name__ == "__main__":
    print("Validating Divination Module...")
    assert validate_divination()
    print("✓ Divination Module validated")
    
    # Demo
    print("\n--- Divination Demo ---")
    q8 = Q8Hypercube()
    system = DivinationSystem(q8, seed=42)
    
    # Perform reading
    reading = system.divine("Should I take this journey?", "Traveler")
    
    print(reading.summary())
    print("\nEse (Verses):")
    for verse in reading.ese:
        print(f"  • {verse}")
    
    if reading.ebo_required:
        print(f"\nEbó Prescription: {reading.ebo_details}")

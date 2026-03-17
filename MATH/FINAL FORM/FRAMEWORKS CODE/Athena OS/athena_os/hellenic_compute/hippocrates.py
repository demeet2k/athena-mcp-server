"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
Part VIII: The Biological Driver (Hippocrates)

THE HUMORAL STATE MACHINE:
    The four humors as a dynamical system:
    - Blood (αἷμα): Hot + Wet → Air → Sanguine
    - Yellow Bile (χολή): Hot + Dry → Fire → Choleric
    - Black Bile (μέλαινα χολή): Cold + Dry → Earth → Melancholic
    - Phlegm (φλέγμα): Cold + Wet → Water → Phlegmatic

THE HOMEOSTASIS ALGORITHM:
    Health = εὐκρασία (good mixture) = balanced humors
    Disease = δυσκρασία (bad mixture) = humoral imbalance
    
    The system maintains homeostasis through:
    - Detection of imbalance
    - Identification of excess/deficiency
    - Application of corrective opposites

THE TREATMENT PROTOCOL:
    Contraria contrariis curantur (Opposites cure opposites)
    - Hot excess → Cold treatment
    - Wet excess → Dry treatment
    
    Via the quality matrix, treatments are systematically derived.

THE THREE SPIRITS:
    - Natural Spirit (Liver): Nutrition, growth
    - Vital Spirit (Heart): Heat, vitality
    - Animal Spirit (Brain): Sensation, motion

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx Part VIII
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum, auto
import numpy as np
import math

from .foundation import StateVector, Klein4Op, Element


# =============================================================================
# THE FOUR HUMORS
# =============================================================================

class Humor(Enum):
    """
    The four Hippocratic humors.
    
    Maps to the 2-bit state space via qualities:
    - b1: Cold(0) / Hot(1)
    - b2: Dry(0) / Wet(1)
    """
    
    BLACK_BILE = ("black bile", "μέλαινα χολή", 0, 0, "Earth", "Melancholic")
    PHLEGM = ("phlegm", "φλέγμα", 0, 1, "Water", "Phlegmatic")
    YELLOW_BILE = ("yellow bile", "χολή", 1, 0, "Fire", "Choleric")
    BLOOD = ("blood", "αἷμα", 1, 1, "Air", "Sanguine")
    
    def __init__(self, name: str, greek: str, b1: int, b2: int,
                 element: str, temperament: str):
        self._name = name
        self.greek = greek
        self._b1 = b1
        self._b2 = b2
        self.element = element
        self.temperament = temperament
    
    def to_state(self) -> StateVector:
        """Convert to state vector."""
        return StateVector(self._b1, self._b2)
    
    @classmethod
    def from_state(cls, state: StateVector) -> Humor:
        """Create from state vector."""
        for humor in cls:
            if humor._b1 == state.b1 and humor._b2 == state.b2:
                return humor
        raise ValueError(f"Invalid state: {state}")
    
    @property
    def is_hot(self) -> bool:
        return self._b1 == 1
    
    @property
    def is_cold(self) -> bool:
        return self._b1 == 0
    
    @property
    def is_wet(self) -> bool:
        return self._b2 == 1
    
    @property
    def is_dry(self) -> bool:
        return self._b2 == 0
    
    def opposite(self) -> Humor:
        """Get opposite humor (both qualities reversed)."""
        new_state = StateVector(1 - self._b1, 1 - self._b2)
        return Humor.from_state(new_state)
    
    def shares_quality_with(self, other: Humor) -> bool:
        """Check if humors share at least one quality."""
        return self._b1 == other._b1 or self._b2 == other._b2


# =============================================================================
# QUALITY SYSTEM
# =============================================================================

class Quality(Enum):
    """Primary qualities that combine to form humors."""
    
    HOT = ("hot", "θερμόν", 1, 0)
    COLD = ("cold", "ψυχρόν", 0, 0)
    WET = ("wet", "ὑγρόν", 0, 1)
    DRY = ("dry", "ξηρόν", 1, 1)
    
    def __init__(self, name: str, greek: str, axis: int, value: int):
        self._name = name
        self.greek = greek
        self.axis = axis  # 0 = temperature, 1 = moisture
        self._value = value
    
    def opposite(self) -> Quality:
        """Get opposite quality."""
        opposites = {
            Quality.HOT: Quality.COLD,
            Quality.COLD: Quality.HOT,
            Quality.WET: Quality.DRY,
            Quality.DRY: Quality.WET,
        }
        return opposites[self]
    
    @classmethod
    def from_humor(cls, humor: Humor) -> Tuple[Quality, Quality]:
        """Get the two qualities of a humor."""
        temp = cls.HOT if humor.is_hot else cls.COLD
        moist = cls.WET if humor.is_wet else cls.DRY
        return (temp, moist)


@dataclass
class QualityVector:
    """
    A vector in quality space.
    
    Represents a point in the Hot/Cold × Wet/Dry plane.
    Values range from -1 (Cold/Dry extreme) to +1 (Hot/Wet extreme).
    """
    
    heat: float = 0.0    # -1 (Cold) to +1 (Hot)
    moisture: float = 0.0  # -1 (Dry) to +1 (Wet)
    
    def __post_init__(self):
        # Clamp to valid range
        self.heat = max(-1.0, min(1.0, self.heat))
        self.moisture = max(-1.0, min(1.0, self.moisture))
    
    def to_humor(self) -> Humor:
        """Convert to dominant humor."""
        b1 = 1 if self.heat >= 0 else 0
        b2 = 1 if self.moisture >= 0 else 0
        return Humor.from_state(StateVector(b1, b2))
    
    def magnitude(self) -> float:
        """Distance from center (perfect balance)."""
        return math.sqrt(self.heat ** 2 + self.moisture ** 2)
    
    def is_balanced(self, threshold: float = 0.2) -> bool:
        """Check if near the balanced center."""
        return self.magnitude() < threshold
    
    def __add__(self, other: QualityVector) -> QualityVector:
        return QualityVector(
            self.heat + other.heat,
            self.moisture + other.moisture
        )
    
    def __mul__(self, scalar: float) -> QualityVector:
        return QualityVector(
            self.heat * scalar,
            self.moisture * scalar
        )


# =============================================================================
# THE HUMORAL STATE MACHINE
# =============================================================================

@dataclass
class HumoralState:
    """
    The current humoral balance.
    
    Represents the distribution of humors in the body.
    """
    
    blood: float = 0.25       # Air, Hot-Wet
    yellow_bile: float = 0.25  # Fire, Hot-Dry
    black_bile: float = 0.25   # Earth, Cold-Dry
    phlegm: float = 0.25       # Water, Cold-Wet
    
    def __post_init__(self):
        self._normalize()
    
    def _normalize(self) -> None:
        """Ensure humors sum to 1."""
        total = self.blood + self.yellow_bile + self.black_bile + self.phlegm
        if total > 0:
            self.blood /= total
            self.yellow_bile /= total
            self.black_bile /= total
            self.phlegm /= total
    
    def get(self, humor: Humor) -> float:
        """Get level of a specific humor."""
        mapping = {
            Humor.BLOOD: self.blood,
            Humor.YELLOW_BILE: self.yellow_bile,
            Humor.BLACK_BILE: self.black_bile,
            Humor.PHLEGM: self.phlegm,
        }
        return mapping[humor]
    
    def set(self, humor: Humor, value: float) -> None:
        """Set level of a specific humor."""
        if humor == Humor.BLOOD:
            self.blood = value
        elif humor == Humor.YELLOW_BILE:
            self.yellow_bile = value
        elif humor == Humor.BLACK_BILE:
            self.black_bile = value
        elif humor == Humor.PHLEGM:
            self.phlegm = value
        self._normalize()
    
    def to_quality_vector(self) -> QualityVector:
        """Convert humoral state to quality vector."""
        # Heat = (hot humors) - (cold humors)
        heat = (self.blood + self.yellow_bile) - (self.phlegm + self.black_bile)
        # Moisture = (wet humors) - (dry humors)
        moisture = (self.blood + self.phlegm) - (self.yellow_bile + self.black_bile)
        
        return QualityVector(heat, moisture)
    
    def dominant_humor(self) -> Humor:
        """Get the dominant humor."""
        levels = [
            (Humor.BLOOD, self.blood),
            (Humor.YELLOW_BILE, self.yellow_bile),
            (Humor.BLACK_BILE, self.black_bile),
            (Humor.PHLEGM, self.phlegm),
        ]
        return max(levels, key=lambda x: x[1])[0]
    
    def imbalance_score(self) -> float:
        """
        Calculate overall imbalance.
        
        0 = perfect balance (all at 0.25)
        1 = maximum imbalance (one at 1.0)
        """
        ideal = 0.25
        deviations = [
            abs(self.blood - ideal),
            abs(self.yellow_bile - ideal),
            abs(self.black_bile - ideal),
            abs(self.phlegm - ideal),
        ]
        return sum(deviations) / 1.5  # Normalize to [0, 1]
    
    def is_healthy(self, threshold: float = 0.2) -> bool:
        """Check if in healthy balance (εὐκρασία)."""
        return self.imbalance_score() < threshold
    
    def apply_treatment(self, treatment: Treatment) -> None:
        """Apply a treatment to modify humoral state."""
        for humor, change in treatment.effects.items():
            current = self.get(humor)
            self.set(humor, current + change)


# =============================================================================
# THE HOMEOSTASIS ALGORITHM
# =============================================================================

class HealthState(Enum):
    """States of health."""
    
    EUKRASIA = "eukrasia"       # Good mixture, healthy
    MILD_DYSKRASIA = "mild"    # Slight imbalance
    MODERATE_DYSKRASIA = "moderate"
    SEVERE_DYSKRASIA = "severe"  # Dangerous imbalance


@dataclass
class Diagnosis:
    """
    A humoral diagnosis.
    """
    
    state: HealthState
    excess_humors: List[Humor]
    deficient_humors: List[Humor]
    dominant_qualities: List[Quality]
    imbalance_score: float
    
    def needs_treatment(self) -> bool:
        """Check if treatment is needed."""
        return self.state != HealthState.EUKRASIA


class HomeostasisEngine:
    """
    Engine for maintaining humoral homeostasis.
    
    Implements the diagnostic and treatment algorithms.
    """
    
    def __init__(self):
        self.ideal_state = HumoralState(0.25, 0.25, 0.25, 0.25)
        self.thresholds = {
            "healthy": 0.15,
            "mild": 0.3,
            "moderate": 0.5,
        }
    
    def diagnose(self, state: HumoralState) -> Diagnosis:
        """
        Diagnose the humoral state.
        """
        imbalance = state.imbalance_score()
        
        # Determine health state
        if imbalance < self.thresholds["healthy"]:
            health_state = HealthState.EUKRASIA
        elif imbalance < self.thresholds["mild"]:
            health_state = HealthState.MILD_DYSKRASIA
        elif imbalance < self.thresholds["moderate"]:
            health_state = HealthState.MODERATE_DYSKRASIA
        else:
            health_state = HealthState.SEVERE_DYSKRASIA
        
        # Find excess and deficient humors
        ideal = 0.25
        excess = []
        deficient = []
        
        for humor in Humor:
            level = state.get(humor)
            if level > ideal + 0.1:
                excess.append(humor)
            elif level < ideal - 0.1:
                deficient.append(humor)
        
        # Determine dominant qualities
        qv = state.to_quality_vector()
        dominant = []
        if qv.heat > 0.2:
            dominant.append(Quality.HOT)
        elif qv.heat < -0.2:
            dominant.append(Quality.COLD)
        if qv.moisture > 0.2:
            dominant.append(Quality.WET)
        elif qv.moisture < -0.2:
            dominant.append(Quality.DRY)
        
        return Diagnosis(
            state=health_state,
            excess_humors=excess,
            deficient_humors=deficient,
            dominant_qualities=dominant,
            imbalance_score=imbalance
        )
    
    def prescribe(self, diagnosis: Diagnosis) -> Optional[Treatment]:
        """
        Prescribe treatment based on diagnosis.
        
        Principle: Contraria contrariis curantur
        (Opposites are cured by opposites)
        """
        if not diagnosis.needs_treatment():
            return None
        
        # Calculate corrective effects
        effects = {}
        
        # Reduce excess humors
        for humor in diagnosis.excess_humors:
            effects[humor] = -0.1
        
        # Increase deficient humors
        for humor in diagnosis.deficient_humors:
            effects[humor] = +0.1
        
        # Determine treatment qualities (opposite of dominant)
        treatment_qualities = []
        for quality in diagnosis.dominant_qualities:
            treatment_qualities.append(quality.opposite())
        
        return Treatment(
            name="Corrective treatment",
            qualities=treatment_qualities,
            effects=effects,
            strength=diagnosis.imbalance_score
        )


# =============================================================================
# TREATMENT SYSTEM
# =============================================================================

@dataclass
class Treatment:
    """
    A humoral treatment.
    """
    
    name: str
    qualities: List[Quality]  # Hot, Cold, Wet, Dry
    effects: Dict[Humor, float]  # Changes to humoral levels
    strength: float = 0.5  # 0-1
    
    def quality_vector(self) -> QualityVector:
        """Get treatment as quality vector."""
        heat = 0.0
        moisture = 0.0
        
        for q in self.qualities:
            if q == Quality.HOT:
                heat += self.strength
            elif q == Quality.COLD:
                heat -= self.strength
            elif q == Quality.WET:
                moisture += self.strength
            elif q == Quality.DRY:
                moisture -= self.strength
        
        return QualityVector(heat, moisture)


# Predefined treatments
TREATMENTS = {
    "bloodletting": Treatment(
        name="Bloodletting",
        qualities=[Quality.COLD, Quality.DRY],
        effects={Humor.BLOOD: -0.2, Humor.BLACK_BILE: +0.1},
        strength=0.6
    ),
    "purging": Treatment(
        name="Purging",
        qualities=[Quality.HOT, Quality.DRY],
        effects={Humor.PHLEGM: -0.2, Humor.YELLOW_BILE: +0.1},
        strength=0.5
    ),
    "cooling_diet": Treatment(
        name="Cooling Diet",
        qualities=[Quality.COLD, Quality.WET],
        effects={Humor.YELLOW_BILE: -0.15, Humor.PHLEGM: +0.1},
        strength=0.3
    ),
    "warming_herbs": Treatment(
        name="Warming Herbs",
        qualities=[Quality.HOT, Quality.DRY],
        effects={Humor.PHLEGM: -0.15, Humor.YELLOW_BILE: +0.1},
        strength=0.3
    ),
}


# =============================================================================
# THE THREE SPIRITS
# =============================================================================

class Spirit(Enum):
    """
    The three Galenic spirits.
    
    These are subtle substances that animate the body.
    """
    
    NATURAL = ("natural", "liver", "nutrition and growth")
    VITAL = ("vital", "heart", "heat and vitality")
    ANIMAL = ("animal", "brain", "sensation and motion")
    
    def __init__(self, name: str, organ: str, function: str):
        self._name = name
        self.organ = organ
        self.function = function


@dataclass
class SpiritSystem:
    """
    The system of three spirits.
    """
    
    natural: float = 1.0   # Liver
    vital: float = 1.0     # Heart
    animal: float = 1.0    # Brain
    
    def total(self) -> float:
        """Total spirit level."""
        return (self.natural + self.vital + self.animal) / 3
    
    def is_healthy(self) -> bool:
        """Check if all spirits are adequate."""
        return all([
            self.natural >= 0.5,
            self.vital >= 0.5,
            self.animal >= 0.5,
        ])
    
    def deplete(self, spirit: Spirit, amount: float) -> None:
        """Deplete a spirit."""
        if spirit == Spirit.NATURAL:
            self.natural = max(0.0, self.natural - amount)
        elif spirit == Spirit.VITAL:
            self.vital = max(0.0, self.vital - amount)
        elif spirit == Spirit.ANIMAL:
            self.animal = max(0.0, self.animal - amount)
    
    def restore(self, amount: float) -> None:
        """Restore all spirits."""
        self.natural = min(1.0, self.natural + amount)
        self.vital = min(1.0, self.vital + amount)
        self.animal = min(1.0, self.animal + amount)


# =============================================================================
# THE BIOLOGICAL DRIVER
# =============================================================================

class BiologicalDriver:
    """
    Complete biological driver based on Hippocratic/Galenic medicine.
    """
    
    def __init__(self):
        self.humors = HumoralState()
        self.spirits = SpiritSystem()
        self.homeostasis = HomeostasisEngine()
        
        # Track health over time
        self.health_history: List[float] = []
    
    def status(self) -> Dict[str, Any]:
        """Get current status."""
        diagnosis = self.homeostasis.diagnose(self.humors)
        
        return {
            "health_state": diagnosis.state.value,
            "imbalance": diagnosis.imbalance_score,
            "dominant_humor": self.humors.dominant_humor().value[0],
            "quality_vector": self.humors.to_quality_vector(),
            "humors": {
                "blood": self.humors.blood,
                "yellow_bile": self.humors.yellow_bile,
                "black_bile": self.humors.black_bile,
                "phlegm": self.humors.phlegm,
            },
            "spirits": {
                "natural": self.spirits.natural,
                "vital": self.spirits.vital,
                "animal": self.spirits.animal,
            },
        }
    
    def simulate_day(self, factors: Dict[str, float] = None) -> None:
        """
        Simulate a day of life with environmental factors.
        
        factors: Dict with season, diet, exercise, etc.
        """
        factors = factors or {}
        
        # Apply environmental effects
        if "heat" in factors:
            # Hot environment increases hot humors
            change = factors["heat"] * 0.05
            self.humors.blood += change
            self.humors.yellow_bile += change
            self.humors._normalize()
        
        if "exertion" in factors:
            # Exertion depletes vital spirit
            self.spirits.deplete(Spirit.VITAL, factors["exertion"] * 0.1)
        
        # Natural restoration during rest
        self.spirits.restore(0.1)
        
        # Record health
        diagnosis = self.homeostasis.diagnose(self.humors)
        self.health_history.append(1 - diagnosis.imbalance_score)
    
    def treat(self, treatment_name: str) -> bool:
        """Apply a treatment."""
        if treatment_name not in TREATMENTS:
            return False
        
        treatment = TREATMENTS[treatment_name]
        self.humors.apply_treatment(treatment)
        return True
    
    def auto_treat(self) -> Optional[Treatment]:
        """Automatically diagnose and treat."""
        diagnosis = self.homeostasis.diagnose(self.humors)
        treatment = self.homeostasis.prescribe(diagnosis)
        
        if treatment:
            self.humors.apply_treatment(treatment)
        
        return treatment


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hippocrates() -> bool:
    """Validate biological driver module."""
    
    # Test Humor
    blood = Humor.BLOOD
    assert blood.is_hot and blood.is_wet
    assert blood.to_state() == StateVector(1, 1)
    assert blood.opposite() == Humor.BLACK_BILE
    
    # Test QualityVector
    qv = QualityVector(0.5, -0.3)
    assert qv.to_humor() == Humor.YELLOW_BILE  # Hot-Dry
    
    # Test HumoralState
    state = HumoralState(0.4, 0.3, 0.2, 0.1)
    assert abs(state.blood + state.yellow_bile + 
               state.black_bile + state.phlegm - 1.0) < 0.001
    
    assert state.dominant_humor() == Humor.BLOOD
    assert not state.is_healthy()
    
    # Test diagnosis
    engine = HomeostasisEngine()
    diagnosis = engine.diagnose(state)
    assert diagnosis.needs_treatment()
    
    # Test treatment prescription
    treatment = engine.prescribe(diagnosis)
    assert treatment is not None
    
    # Test Treatment
    assert "bloodletting" in TREATMENTS
    
    # Test BiologicalDriver
    driver = BiologicalDriver()
    status = driver.status()
    assert "health_state" in status
    
    # Simulate imbalance and treatment
    driver.humors = HumoralState(0.5, 0.2, 0.2, 0.1)
    treatment = driver.auto_treat()
    assert treatment is not None
    
    return True


if __name__ == "__main__":
    print("Validating Biological Driver Module...")
    assert validate_hippocrates()
    print("✓ Biological module validated")
    
    # Demo
    print("\n--- Biological Driver Demo ---")
    
    print("\n1. Humoral Correspondences:")
    for humor in Humor:
        quals = Quality.from_humor(humor)
        print(f"   {humor.value[0]}:")
        print(f"      Element: {humor.element}")
        print(f"      Qualities: {quals[0].value[0]}, {quals[1].value[0]}")
        print(f"      Temperament: {humor.temperament}")
    
    print("\n2. Simulating Humoral Imbalance:")
    driver = BiologicalDriver()
    
    # Create choleric imbalance (excess yellow bile)
    driver.humors = HumoralState(0.2, 0.5, 0.15, 0.15)
    
    diagnosis = driver.homeostasis.diagnose(driver.humors)
    print(f"   State: {diagnosis.state.value}")
    print(f"   Excess: {[h.value[0] for h in diagnosis.excess_humors]}")
    print(f"   Deficient: {[h.value[0] for h in diagnosis.deficient_humors]}")
    
    print("\n3. Applying Treatment:")
    treatment = driver.auto_treat()
    if treatment:
        print(f"   Treatment: {treatment.name}")
        print(f"   Qualities: {[q.value[0] for q in treatment.qualities]}")
        
        new_diagnosis = driver.homeostasis.diagnose(driver.humors)
        print(f"   New state: {new_diagnosis.state.value}")
        print(f"   New imbalance: {new_diagnosis.imbalance_score:.2f}")
    
    print("\n4. Three Spirits:")
    for spirit in Spirit:
        print(f"   {spirit.value[0]} ({spirit.organ}): {spirit.function}")
    
    print("\n5. Quality Space:")
    for qv in [QualityVector(-0.5, -0.5), QualityVector(0.5, 0.5),
               QualityVector(-0.5, 0.5), QualityVector(0.5, -0.5)]:
        humor = qv.to_humor()
        print(f"   ({qv.heat:+.1f}, {qv.moisture:+.1f}) → {humor.value[0]}")

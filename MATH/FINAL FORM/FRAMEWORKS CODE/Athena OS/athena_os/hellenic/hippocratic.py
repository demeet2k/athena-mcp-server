"""
ATHENA OS - HELLENIC: HIPPOCRATIC BIOLOGICAL DRIVER
====================================================
The Humoral State Machine and Homeostasis Algorithm

THE HUMORAL STATE MACHINE:
    Four humors mapped to Z₂ × Z₂:
    
    (0,0) Black Bile (μέλαινα χολή) - Cold/Dry - Melancholic
    (0,1) Phlegm (φλέγμα)           - Cold/Wet - Phlegmatic
    (1,0) Yellow Bile (χολή)        - Hot/Dry  - Choleric
    (1,1) Blood (αἷμα)              - Hot/Wet  - Sanguine

TEMPERAMENT DYNAMICS:
    Each temperament has characteristic:
    - Energy level
    - Stability
    - Social orientation
    - Cognitive style

THE HOMEOSTASIS ALGORITHM:
    Goal: Maintain balance (εὐκρασία) among humors
    
    Error = |H_current - H_ideal|
    
    Treatment = -K × Error (negative feedback)

CRISIS DETECTION:
    Acute imbalance triggers crisis (κρίσις)
    requiring immediate intervention.

SEASONAL VARIATION:
    - Spring: Blood increases (Hot/Wet)
    - Summer: Yellow Bile increases (Hot/Dry)
    - Autumn: Black Bile increases (Cold/Dry)
    - Winter: Phlegm increases (Cold/Wet)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum, auto
import numpy as np

from .algebra import BitPair, Klein4Group, Klein4Op


# =============================================================================
# THE FOUR HUMORS
# =============================================================================

class Humor(Enum):
    """The Four Humors (χυμοί)."""
    
    BLACK_BILE = ((0, 0), "μέλαινα χολή", "Cold", "Dry", "Melancholic", "Earth", "Spleen")
    PHLEGM = ((0, 1), "φλέγμα", "Cold", "Wet", "Phlegmatic", "Water", "Brain")
    YELLOW_BILE = ((1, 0), "χολή", "Hot", "Dry", "Choleric", "Fire", "Liver")
    BLOOD = ((1, 1), "αἷμα", "Hot", "Wet", "Sanguine", "Air", "Heart")
    
    @property
    def bits(self) -> Tuple[int, int]:
        return self.value[0]
    
    @property
    def greek(self) -> str:
        return self.value[1]
    
    @property
    def temperature(self) -> str:
        return self.value[2]
    
    @property
    def moisture(self) -> str:
        return self.value[3]
    
    @property
    def temperament(self) -> str:
        return self.value[4]
    
    @property
    def element(self) -> str:
        return self.value[5]
    
    @property
    def organ(self) -> str:
        return self.value[6]
    
    @property
    def bit_pair(self) -> BitPair:
        return BitPair(*self.bits)
    
    @classmethod
    def from_bits(cls, b1: int, b2: int) -> 'Humor':
        """Get humor from bit values."""
        target = (b1, b2)
        for humor in cls:
            if humor.bits == target:
                return humor
        raise ValueError(f"No humor for bits ({b1}, {b2})")


class Temperament(Enum):
    """The Four Temperaments."""
    
    MELANCHOLIC = ("Melancholic", BLACK_BILE := Humor.BLACK_BILE, 
                   {"analytical": 0.9, "detail_oriented": 0.8, "introverted": 0.7})
    PHLEGMATIC = ("Phlegmatic", PHLEGM := Humor.PHLEGM,
                  {"calm": 0.9, "reliable": 0.8, "introverted": 0.6})
    CHOLERIC = ("Choleric", YELLOW_BILE := Humor.YELLOW_BILE,
                {"ambitious": 0.9, "leader": 0.8, "extroverted": 0.7})
    SANGUINE = ("Sanguine", BLOOD := Humor.BLOOD,
                {"optimistic": 0.9, "social": 0.9, "extroverted": 0.8})
    
    @property
    def name_str(self) -> str:
        return self.value[0]
    
    @property
    def dominant_humor(self) -> Humor:
        return self.value[1]
    
    @property
    def traits(self) -> Dict[str, float]:
        return self.value[2]


# =============================================================================
# HUMORAL STATE
# =============================================================================

@dataclass
class HumoralState:
    """
    The humoral state of an organism.
    
    State vector H = [black_bile, phlegm, yellow_bile, blood]
    Normalized to sum to 1.0 (conservation).
    """
    
    black_bile: float = 0.25
    phlegm: float = 0.25
    yellow_bile: float = 0.25
    blood: float = 0.25
    
    def __post_init__(self):
        self._normalize()
    
    def _normalize(self) -> None:
        """Ensure humors sum to 1.0."""
        total = self.black_bile + self.phlegm + self.yellow_bile + self.blood
        if total > 0:
            self.black_bile /= total
            self.phlegm /= total
            self.yellow_bile /= total
            self.blood /= total
    
    def as_vector(self) -> np.ndarray:
        """Return as numpy vector."""
        return np.array([self.black_bile, self.phlegm, 
                        self.yellow_bile, self.blood])
    
    @classmethod
    def from_vector(cls, vec: np.ndarray) -> 'HumoralState':
        """Create from vector."""
        return cls(vec[0], vec[1], vec[2], vec[3])
    
    def dominant_humor(self) -> Humor:
        """Return the dominant humor."""
        humors = [
            (self.black_bile, Humor.BLACK_BILE),
            (self.phlegm, Humor.PHLEGM),
            (self.yellow_bile, Humor.YELLOW_BILE),
            (self.blood, Humor.BLOOD),
        ]
        return max(humors, key=lambda x: x[0])[1]
    
    def dominant_temperament(self) -> Temperament:
        """Return dominant temperament based on humor."""
        humor = self.dominant_humor()
        mapping = {
            Humor.BLACK_BILE: Temperament.MELANCHOLIC,
            Humor.PHLEGM: Temperament.PHLEGMATIC,
            Humor.YELLOW_BILE: Temperament.CHOLERIC,
            Humor.BLOOD: Temperament.SANGUINE,
        }
        return mapping[humor]
    
    def balance_score(self) -> float:
        """
        Compute balance (εὐκρασία) score.
        
        1.0 = perfect balance (0.25 each)
        0.0 = complete imbalance (one at 1.0)
        """
        ideal = np.array([0.25, 0.25, 0.25, 0.25])
        current = self.as_vector()
        
        # L2 distance from ideal
        distance = np.linalg.norm(current - ideal)
        max_distance = np.linalg.norm(np.array([1, 0, 0, 0]) - ideal)
        
        return 1.0 - (distance / max_distance)
    
    def is_crisis(self, threshold: float = 0.5) -> bool:
        """Check if state is in crisis (severe imbalance)."""
        return any([
            self.black_bile > threshold,
            self.phlegm > threshold,
            self.yellow_bile > threshold,
            self.blood > threshold,
        ])
    
    def get_humor_value(self, humor: Humor) -> float:
        """Get value for specific humor."""
        mapping = {
            Humor.BLACK_BILE: self.black_bile,
            Humor.PHLEGM: self.phlegm,
            Humor.YELLOW_BILE: self.yellow_bile,
            Humor.BLOOD: self.blood,
        }
        return mapping[humor]
    
    def set_humor_value(self, humor: Humor, value: float) -> None:
        """Set value for specific humor (will renormalize)."""
        if humor == Humor.BLACK_BILE:
            self.black_bile = value
        elif humor == Humor.PHLEGM:
            self.phlegm = value
        elif humor == Humor.YELLOW_BILE:
            self.yellow_bile = value
        elif humor == Humor.BLOOD:
            self.blood = value
        self._normalize()


# =============================================================================
# SEASONAL DYNAMICS
# =============================================================================

class Season(Enum):
    """The four seasons with associated humoral changes."""
    
    SPRING = ("Spring", Humor.BLOOD, (1, 1))       # Hot/Wet
    SUMMER = ("Summer", Humor.YELLOW_BILE, (1, 0)) # Hot/Dry
    AUTUMN = ("Autumn", Humor.BLACK_BILE, (0, 0))  # Cold/Dry
    WINTER = ("Winter", Humor.PHLEGM, (0, 1))      # Cold/Wet
    
    @property
    def name_str(self) -> str:
        return self.value[0]
    
    @property
    def dominant_humor(self) -> Humor:
        return self.value[1]
    
    @property
    def quality_bits(self) -> Tuple[int, int]:
        return self.value[2]


class SeasonalCycle:
    """
    Seasonal variation in humoral balance.
    
    The year cycles through seasons, each favoring one humor.
    """
    
    def __init__(self, year_length: float = 365.0):
        self.year_length = year_length
        self.seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
    
    def get_season(self, day: float) -> Season:
        """Get season for given day of year."""
        season_length = self.year_length / 4
        season_idx = int((day % self.year_length) / season_length)
        return self.seasons[season_idx]
    
    def seasonal_modifier(self, day: float) -> Dict[Humor, float]:
        """
        Get seasonal modification to humors.
        
        Returns multipliers for each humor.
        """
        season = self.get_season(day)
        
        # Base multipliers (1.0 = no change)
        modifiers = {
            Humor.BLACK_BILE: 1.0,
            Humor.PHLEGM: 1.0,
            Humor.YELLOW_BILE: 1.0,
            Humor.BLOOD: 1.0,
        }
        
        # Seasonal humor increases
        modifiers[season.dominant_humor] = 1.3
        
        # Opposite humor decreases
        opposite = self._get_opposite_humor(season.dominant_humor)
        modifiers[opposite] = 0.7
        
        return modifiers
    
    def _get_opposite_humor(self, humor: Humor) -> Humor:
        """Get opposite humor (complement in Z₂×Z₂)."""
        k4 = Klein4Group()
        original = humor.bit_pair
        opposite_bits = k4.apply(Klein4Op.C, original)
        return Humor.from_bits(opposite_bits.b1, opposite_bits.b2)


# =============================================================================
# HOMEOSTASIS ALGORITHM
# =============================================================================

class HomeostasisController:
    """
    The Homeostasis Algorithm.
    
    Maintains humoral balance through negative feedback.
    
    Error = H_current - H_ideal
    Treatment = -K × Error
    """
    
    def __init__(self, gain: float = 0.1):
        self.K = gain  # Control gain
        
        # Ideal state: perfect balance
        self.ideal = HumoralState(0.25, 0.25, 0.25, 0.25)
        
        # History for tracking
        self._history: List[HumoralState] = []
    
    def compute_error(self, current: HumoralState) -> np.ndarray:
        """Compute error from ideal."""
        return current.as_vector() - self.ideal.as_vector()
    
    def compute_treatment(self, current: HumoralState) -> np.ndarray:
        """
        Compute treatment (control input).
        
        u = -K × error (negative feedback)
        """
        error = self.compute_error(current)
        return -self.K * error
    
    def apply_treatment(self, current: HumoralState) -> HumoralState:
        """Apply treatment and return new state."""
        treatment = self.compute_treatment(current)
        new_vector = current.as_vector() + treatment
        
        # Ensure non-negative
        new_vector = np.maximum(new_vector, 0.0)
        
        new_state = HumoralState.from_vector(new_vector)
        self._history.append(new_state)
        
        return new_state
    
    def simulate(self, initial: HumoralState, 
                 steps: int = 10) -> List[HumoralState]:
        """Simulate homeostatic regulation."""
        states = [initial]
        current = initial
        
        for _ in range(steps):
            current = self.apply_treatment(current)
            states.append(current)
        
        return states
    
    def convergence_rate(self) -> float:
        """Estimate convergence rate from history."""
        if len(self._history) < 2:
            return 0.0
        
        errors = [np.linalg.norm(self.compute_error(s)) 
                  for s in self._history]
        
        if errors[0] == 0:
            return 1.0
        
        return 1.0 - (errors[-1] / errors[0])


# =============================================================================
# TREATMENT PROTOCOL
# =============================================================================

class TreatmentType(Enum):
    """Types of Hippocratic treatments."""
    
    # Diet modifications
    HEATING_DIET = ("diet", (1, 0), "Hot foods and drinks")
    COOLING_DIET = ("diet", (-1, 0), "Cold foods and drinks")
    DRYING_DIET = ("diet", (0, -1), "Dry foods")
    MOISTENING_DIET = ("diet", (0, 1), "Moist foods")
    
    # Physical interventions
    BLOODLETTING = ("physical", "blood", "Reduce blood")
    PURGING = ("physical", "yellow_bile", "Reduce yellow bile")
    EMETIC = ("physical", "phlegm", "Reduce phlegm")
    
    # Environmental
    WARM_BATH = ("environment", (1, 1), "Heating and moistening")
    COLD_BATH = ("environment", (-1, 1), "Cooling and moistening")
    EXERCISE = ("environment", (1, -1), "Heating and drying")
    REST = ("environment", (-1, -1), "Cooling and drying")


@dataclass
class Treatment:
    """A treatment prescription."""
    
    treatment_type: TreatmentType
    intensity: float = 1.0  # 0.0 to 1.0
    duration: int = 1       # Time units
    
    def apply(self, state: HumoralState) -> HumoralState:
        """Apply treatment to state."""
        vec = state.as_vector()
        
        # Get treatment effect based on type
        if self.treatment_type.value[0] == "diet":
            # Modify heat/moisture
            heat_mod, moist_mod = self.treatment_type.value[1]
            
            # Heat affects hot humors (yellow bile, blood)
            if heat_mod > 0:
                vec[2] += 0.05 * self.intensity  # Yellow bile
                vec[3] += 0.05 * self.intensity  # Blood
            else:
                vec[0] += 0.05 * self.intensity  # Black bile
                vec[1] += 0.05 * self.intensity  # Phlegm
        
        elif self.treatment_type.value[0] == "physical":
            # Reduce specific humor
            humor_name = self.treatment_type.value[1]
            humor_idx = {"black_bile": 0, "phlegm": 1, 
                        "yellow_bile": 2, "blood": 3}
            if humor_name in humor_idx:
                vec[humor_idx[humor_name]] -= 0.1 * self.intensity
        
        elif self.treatment_type.value[0] == "environment":
            heat_mod, moist_mod = self.treatment_type.value[1]
            
            # Combined effect
            if heat_mod > 0 and moist_mod > 0:
                vec[3] += 0.05 * self.intensity  # Blood (hot/wet)
            elif heat_mod > 0 and moist_mod < 0:
                vec[2] += 0.05 * self.intensity  # Yellow bile (hot/dry)
            elif heat_mod < 0 and moist_mod > 0:
                vec[1] += 0.05 * self.intensity  # Phlegm (cold/wet)
            else:
                vec[0] += 0.05 * self.intensity  # Black bile (cold/dry)
        
        return HumoralState.from_vector(np.maximum(vec, 0.0))


class TreatmentProtocol:
    """
    The Treatment Protocol.
    
    Determines appropriate treatment based on humoral imbalance.
    """
    
    @staticmethod
    def diagnose(state: HumoralState) -> Dict[str, any]:
        """Diagnose imbalance."""
        diagnosis = {
            "dominant_humor": state.dominant_humor(),
            "temperament": state.dominant_temperament(),
            "balance_score": state.balance_score(),
            "in_crisis": state.is_crisis(),
            "imbalances": [],
        }
        
        # Check each humor
        threshold = 0.35
        if state.black_bile > threshold:
            diagnosis["imbalances"].append(("excess", Humor.BLACK_BILE))
        if state.phlegm > threshold:
            diagnosis["imbalances"].append(("excess", Humor.PHLEGM))
        if state.yellow_bile > threshold:
            diagnosis["imbalances"].append(("excess", Humor.YELLOW_BILE))
        if state.blood > threshold:
            diagnosis["imbalances"].append(("excess", Humor.BLOOD))
        
        return diagnosis
    
    @staticmethod
    def prescribe(diagnosis: Dict) -> List[Treatment]:
        """Prescribe treatments based on diagnosis."""
        treatments = []
        
        for imbalance_type, humor in diagnosis.get("imbalances", []):
            if imbalance_type == "excess":
                # Treat excess by reducing or countering
                if humor == Humor.BLACK_BILE:
                    treatments.append(Treatment(TreatmentType.WARM_BATH))
                    treatments.append(Treatment(TreatmentType.MOISTENING_DIET))
                
                elif humor == Humor.PHLEGM:
                    treatments.append(Treatment(TreatmentType.EXERCISE))
                    treatments.append(Treatment(TreatmentType.HEATING_DIET))
                
                elif humor == Humor.YELLOW_BILE:
                    treatments.append(Treatment(TreatmentType.COLD_BATH))
                    treatments.append(Treatment(TreatmentType.COOLING_DIET))
                    if diagnosis.get("in_crisis"):
                        treatments.append(Treatment(TreatmentType.PURGING, 0.5))
                
                elif humor == Humor.BLOOD:
                    treatments.append(Treatment(TreatmentType.REST))
                    treatments.append(Treatment(TreatmentType.COOLING_DIET))
                    if diagnosis.get("in_crisis"):
                        treatments.append(Treatment(TreatmentType.BLOODLETTING, 0.5))
        
        return treatments


# =============================================================================
# HIPPOCRATIC STATE MACHINE
# =============================================================================

class HippocraticStateMachine:
    """
    Complete Hippocratic biological driver.
    
    Integrates humoral state, seasonal variation,
    homeostasis, and treatment protocols.
    """
    
    def __init__(self, initial_state: HumoralState = None):
        self.state = initial_state or HumoralState()
        
        self.seasonal_cycle = SeasonalCycle()
        self.homeostasis = HomeostasisController()
        self.protocol = TreatmentProtocol()
        
        # Time tracking
        self._day = 0.0
        
        # History
        self._state_history: List[Tuple[float, HumoralState]] = []
    
    def advance(self, dt: float = 1.0) -> HumoralState:
        """Advance simulation by dt days."""
        self._day += dt
        
        # Apply seasonal modifier
        modifiers = self.seasonal_cycle.seasonal_modifier(self._day)
        
        vec = self.state.as_vector()
        for i, humor in enumerate([Humor.BLACK_BILE, Humor.PHLEGM,
                                   Humor.YELLOW_BILE, Humor.BLOOD]):
            vec[i] *= modifiers[humor]
        
        self.state = HumoralState.from_vector(vec)
        
        # Apply homeostatic regulation
        self.state = self.homeostasis.apply_treatment(self.state)
        
        # Record history
        self._state_history.append((self._day, 
                                    HumoralState.from_vector(self.state.as_vector())))
        
        return self.state
    
    def perturb(self, humor: Humor, amount: float) -> None:
        """Introduce external perturbation."""
        current = self.state.get_humor_value(humor)
        self.state.set_humor_value(humor, current + amount)
    
    def diagnose(self) -> Dict:
        """Get current diagnosis."""
        return self.protocol.diagnose(self.state)
    
    def treat(self) -> List[Treatment]:
        """Diagnose and treat."""
        diagnosis = self.diagnose()
        treatments = self.protocol.prescribe(diagnosis)
        
        for treatment in treatments:
            self.state = treatment.apply(self.state)
        
        return treatments
    
    def get_status(self) -> Dict:
        """Get complete status."""
        return {
            "day": self._day,
            "season": self.seasonal_cycle.get_season(self._day).name_str,
            "state": {
                "black_bile": self.state.black_bile,
                "phlegm": self.state.phlegm,
                "yellow_bile": self.state.yellow_bile,
                "blood": self.state.blood,
            },
            "dominant_humor": self.state.dominant_humor().name,
            "temperament": self.state.dominant_temperament().name_str,
            "balance_score": self.state.balance_score(),
            "in_crisis": self.state.is_crisis(),
        }
    
    def simulate(self, days: int) -> List[Dict]:
        """Run simulation for given days."""
        results = []
        
        for _ in range(days):
            self.advance(1.0)
            results.append(self.get_status())
        
        return results


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hippocratic() -> bool:
    """Validate Hippocratic module."""
    
    # Test Humor
    assert len(list(Humor)) == 4
    
    assert Humor.BLACK_BILE.bits == (0, 0)
    assert Humor.BLOOD.bits == (1, 1)
    assert Humor.BLACK_BILE.temperature == "Cold"
    assert Humor.BLOOD.element == "Air"
    
    # Test from_bits
    assert Humor.from_bits(0, 0) == Humor.BLACK_BILE
    assert Humor.from_bits(1, 1) == Humor.BLOOD
    
    # Test HumoralState
    state = HumoralState(0.4, 0.2, 0.2, 0.2)
    
    assert abs(sum(state.as_vector()) - 1.0) < 0.01
    assert state.dominant_humor() == Humor.BLACK_BILE
    assert state.dominant_temperament() == Temperament.MELANCHOLIC
    
    balance = state.balance_score()
    assert 0 <= balance <= 1
    
    # Test balanced state
    balanced = HumoralState()
    assert balanced.balance_score() > 0.99
    
    # Test crisis detection
    crisis_state = HumoralState(0.6, 0.2, 0.1, 0.1)
    assert crisis_state.is_crisis()
    
    # Test SeasonalCycle
    cycle = SeasonalCycle()
    
    assert cycle.get_season(0) == Season.SPRING
    assert cycle.get_season(100) == Season.SUMMER
    assert cycle.get_season(200) == Season.AUTUMN
    assert cycle.get_season(300) == Season.WINTER
    
    modifiers = cycle.seasonal_modifier(0)  # Spring
    assert modifiers[Humor.BLOOD] > 1.0  # Blood dominant in spring
    
    # Test HomeostasisController
    controller = HomeostasisController(gain=0.2)
    
    imbalanced = HumoralState(0.5, 0.2, 0.2, 0.1)
    error = controller.compute_error(imbalanced)
    assert error[0] > 0  # Black bile excess
    
    treatment = controller.compute_treatment(imbalanced)
    assert treatment[0] < 0  # Should reduce black bile
    
    # Simulate convergence
    states = controller.simulate(imbalanced, steps=20)
    assert states[-1].balance_score() > states[0].balance_score()
    
    # Test Treatment
    treatment = Treatment(TreatmentType.WARM_BATH, intensity=1.0)
    new_state = treatment.apply(imbalanced)
    assert isinstance(new_state, HumoralState)
    
    # Test TreatmentProtocol
    diagnosis = TreatmentProtocol.diagnose(imbalanced)
    assert "dominant_humor" in diagnosis
    assert "balance_score" in diagnosis
    
    treatments = TreatmentProtocol.prescribe(diagnosis)
    assert isinstance(treatments, list)
    
    # Test HippocraticStateMachine
    machine = HippocraticStateMachine()
    
    status = machine.get_status()
    assert "day" in status
    assert "season" in status
    assert "temperament" in status
    
    machine.advance(30)
    assert machine._day == 30
    
    machine.perturb(Humor.YELLOW_BILE, 0.3)
    diagnosis = machine.diagnose()
    
    treatments = machine.treat()
    assert len(treatments) > 0
    
    # Run simulation
    results = machine.simulate(10)
    assert len(results) == 10
    
    return True


if __name__ == "__main__":
    print("Validating Hippocratic Module...")
    assert validate_hippocratic()
    print("✓ Hippocratic Module validated")
    
    print("\n--- Four Humors ---")
    for humor in Humor:
        print(f"  {humor.greek}: {humor.temperature}/{humor.moisture} "
              f"- {humor.temperament} - {humor.element}")
    
    print("\n--- State Machine Demo ---")
    machine = HippocraticStateMachine()
    
    print(f"  Initial: {machine.get_status()['temperament']}")
    print(f"  Balance: {machine.state.balance_score():.2f}")
    
    # Introduce imbalance
    machine.perturb(Humor.YELLOW_BILE, 0.3)
    print(f"\n  After perturbation:")
    print(f"  Dominant: {machine.state.dominant_humor().name}")
    print(f"  Balance: {machine.state.balance_score():.2f}")
    
    # Treat
    treatments = machine.treat()
    print(f"\n  Treatments applied: {len(treatments)}")
    print(f"  Balance after treatment: {machine.state.balance_score():.2f}")

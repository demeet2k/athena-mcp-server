"""
ATHENA OS - TIBETAN: BARDO MODULE
==================================
Markov Decision Process for State Transition

THE BARDO:
    Intermediate state modeled as a STOCHASTIC PROCESS
    over a fixed temporal lattice of T=49 days (7 cycles of 7).

THE TRANSITION MATRIX (P_ij):
    S_{t+1} = S_t · P
    
    The matrix P changes as t increases (time-dependent).

PHASES:
    Phase 1 (t=1-14): CHONYID BARDO (Luminosity)
        - High-energy signal projection
        - Clear Light appears
        - If Recognize() == True → Liberation (Exit Loop)
        - If Recognize() == False → Karmic Illusion
    
    Phase 2 (t=15-49): SIDPA BARDO (Becomings)
        - Entropy increases
        - Signal degrades into noise
        - Agent driven by Karmic Wind (Momentum Vector)
        - v_drift = Σ k_past (sum of past actions)
        - Drift toward Womb Door (Rebirth Port)

SIGNAL DETECTION:
    Bright Lights (High Intensity): SOURCE radiation → MERGE (Liberation)
    Dull Lights (Low Intensity): Six Realms → REJECT (Avoid Rebirth)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .mandala import BuddhaFamily, FIVE_BUDDHAS, Poison, Wisdom


# =============================================================================
# BARDO PHASES
# =============================================================================

class BardoPhase(Enum):
    """Phases of the Bardo transition."""
    
    CHIKHAI = "chikhai"   # Moment of death - Clear Light
    CHONYID = "chonyid"   # Days 1-14 - Luminosity/Visions
    SIDPA = "sidpa"       # Days 15-49 - Becoming/Rebirth


class BardoState(Enum):
    """Possible states in the Bardo."""
    
    LIBERATION = "liberation"       # Exit loop - success
    CLEAR_LIGHT = "clear_light"     # Recognizing source
    PEACEFUL_DEITIES = "peaceful"   # Days 1-7
    WRATHFUL_DEITIES = "wrathful"   # Days 8-14
    KARMIC_VISIONS = "karmic"       # Days 15-49
    WOMB_DOOR = "womb_door"         # Approaching rebirth
    REBIRTH = "rebirth"             # Captured - reincarnation


class Realm(Enum):
    """The Six Realms of Rebirth."""
    
    DEVA = "deva"               # Gods - white dull light
    ASURA = "asura"             # Titans - green dull light
    HUMAN = "human"             # Humans - yellow dull light
    ANIMAL = "animal"           # Animals - blue dull light
    PRETA = "preta"             # Hungry ghosts - red dull light
    NARAKA = "naraka"           # Hell beings - smoke light


# =============================================================================
# LIGHTS (SIGNALS)
# =============================================================================

class LightType(Enum):
    """Types of lights encountered in the Bardo."""
    
    CLEAR_LIGHT = "clear_light"   # Source light - Liberation
    BRIGHT = "bright"             # Buddha family lights
    DULL = "dull"                 # Realm lights - Traps


@dataclass
class BardoLight:
    """
    A light signal in the Bardo.
    
    Agent must discriminate Signal (Bright) from Noise (Dull).
    """
    
    light_type: LightType
    intensity: float  # 0-1
    frequency: float  # High = Source, Low = Realm
    color: str
    
    # Associated destination
    source: Optional[BuddhaFamily] = None  # For bright lights
    realm: Optional[Realm] = None          # For dull lights
    
    def is_source_light(self) -> bool:
        """Check if this is source radiation."""
        return self.light_type == LightType.CLEAR_LIGHT or (
            self.light_type == LightType.BRIGHT and 
            self.intensity > 0.8
        )
    
    def is_trap(self) -> bool:
        """Check if this is an attractor basin trap."""
        return self.light_type == LightType.DULL


def create_clear_light() -> BardoLight:
    """Create the Clear Light (highest signal)."""
    return BardoLight(
        light_type=LightType.CLEAR_LIGHT,
        intensity=1.0,
        frequency=float('inf'),
        color="pure_white"
    )


def create_buddha_lights() -> List[BardoLight]:
    """Create the Buddha family lights."""
    lights = []
    colors = ["white", "blue", "yellow", "red", "green"]
    
    for i, family in enumerate(BuddhaFamily):
        lights.append(BardoLight(
            light_type=LightType.BRIGHT,
            intensity=0.9 - i * 0.05,
            frequency=1000 - i * 100,
            color=colors[i],
            source=family
        ))
    
    return lights


def create_realm_lights() -> List[BardoLight]:
    """Create the six realm lights (dull, comfortable traps)."""
    configs = [
        (Realm.DEVA, "white_dull", 0.3),
        (Realm.ASURA, "green_dull", 0.25),
        (Realm.HUMAN, "yellow_dull", 0.4),
        (Realm.ANIMAL, "blue_dull", 0.2),
        (Realm.PRETA, "red_dull", 0.15),
        (Realm.NARAKA, "smoke", 0.1),
    ]
    
    lights = []
    for realm, color, intensity in configs:
        lights.append(BardoLight(
            light_type=LightType.DULL,
            intensity=intensity,
            frequency=10,
            color=color,
            realm=realm
        ))
    
    return lights


# =============================================================================
# KARMIC WIND
# =============================================================================

@dataclass
class KarmicAction:
    """A past action contributing to karmic momentum."""
    
    action: str
    polarity: int  # +1 positive, -1 negative
    magnitude: float
    realm_tendency: Optional[Realm] = None


class KarmicWind:
    """
    Karmic Wind: Momentum vector from past actions.
    
    v_drift = Σ k_past
    Drives the agent toward specific womb doors.
    """
    
    def __init__(self):
        self._actions: List[KarmicAction] = []
        self._momentum = np.zeros(6)  # 6 realms
    
    def add_action(self, action: KarmicAction) -> None:
        """Add a karmic action to the wind."""
        self._actions.append(action)
        
        # Update momentum toward realm
        if action.realm_tendency:
            idx = list(Realm).index(action.realm_tendency)
            self._momentum[idx] += action.polarity * action.magnitude
    
    def compute_drift(self) -> Tuple[Realm, float]:
        """
        Compute drift direction and magnitude.
        
        Returns (target_realm, drift_strength).
        """
        if np.all(self._momentum == 0):
            # Default to human realm
            return Realm.HUMAN, 0.0
        
        # Find dominant direction
        idx = np.argmax(np.abs(self._momentum))
        strength = float(np.abs(self._momentum[idx]))
        
        return list(Realm)[idx], strength
    
    def get_total_karma(self) -> float:
        """Get net karma (positive - negative)."""
        return sum(a.polarity * a.magnitude for a in self._actions)
    
    @property
    def momentum(self) -> np.ndarray:
        return self._momentum.copy()


# =============================================================================
# BARDO AGENT
# =============================================================================

class BardoAgent:
    """
    An agent navigating the Bardo.
    
    Must discriminate signals and avoid traps.
    """
    
    def __init__(self, name: str, recognition_ability: float = 0.5):
        self.name = name
        self.recognition_ability = recognition_ability  # 0-1
        
        # State
        self._current_state = BardoState.CLEAR_LIGHT
        self._day = 0
        self._phase = BardoPhase.CHIKHAI
        
        # Karmic wind
        self.karmic_wind = KarmicWind()
        
        # Outcome
        self._liberated = False
        self._reborn = False
        self._rebirth_realm: Optional[Realm] = None
    
    def recognize(self, light: BardoLight) -> bool:
        """
        Attempt to recognize a light as source.
        
        Recognition probability based on ability and light intensity.
        """
        if light.is_source_light():
            # Higher intensity lights are terrifying to uncalibrated
            # But high recognition ability overcomes this
            terror_factor = light.intensity * 0.5
            effective_ability = self.recognition_ability * (1 - terror_factor * 0.5)
            
            return np.random.random() < effective_ability
        
        return False
    
    def reject_trap(self, light: BardoLight) -> bool:
        """
        Attempt to reject a dull light trap.
        
        Dull lights are comfortable - harder to reject.
        """
        if not light.is_trap():
            return True  # Not a trap
        
        # Comfort makes rejection harder
        comfort_factor = light.intensity * 2  # Dull lights are comfortable
        effective_ability = self.recognition_ability * (1 - comfort_factor * 0.3)
        
        return np.random.random() < effective_ability
    
    def process_light(self, light: BardoLight) -> Dict:
        """
        Process an encountered light.
        
        Implements bardo_navigation algorithm.
        """
        result = {
            "light_type": light.light_type.value,
            "intensity": light.intensity,
            "color": light.color
        }
        
        if light.is_source_light():
            if self.recognize(light):
                self._liberated = True
                self._current_state = BardoState.LIBERATION
                result["action"] = "MERGE"
                result["outcome"] = "Liberation"
            else:
                result["action"] = "MISSED"
                result["outcome"] = "Continue"
        
        elif light.is_trap():
            if not self.reject_trap(light):
                self._reborn = True
                self._rebirth_realm = light.realm
                self._current_state = BardoState.REBIRTH
                result["action"] = "CAPTURED"
                result["outcome"] = f"Rebirth in {light.realm.value}"
            else:
                result["action"] = "REJECTED"
                result["outcome"] = "Continue"
        
        else:
            result["action"] = "OBSERVE"
            result["outcome"] = "Continue"
        
        return result
    
    def advance_day(self) -> Dict:
        """
        Advance one day in the Bardo.
        
        Updates phase and state.
        """
        if self._liberated or self._reborn:
            return {"error": "Bardo already concluded"}
        
        self._day += 1
        
        # Update phase
        if self._day == 1:
            self._phase = BardoPhase.CHIKHAI
            self._current_state = BardoState.CLEAR_LIGHT
        elif self._day <= 7:
            self._phase = BardoPhase.CHONYID
            self._current_state = BardoState.PEACEFUL_DEITIES
        elif self._day <= 14:
            self._phase = BardoPhase.CHONYID
            self._current_state = BardoState.WRATHFUL_DEITIES
        elif self._day <= 49:
            self._phase = BardoPhase.SIDPA
            self._current_state = BardoState.KARMIC_VISIONS
        else:
            # Forced rebirth at day 49
            self._reborn = True
            target, _ = self.karmic_wind.compute_drift()
            self._rebirth_realm = target
            self._current_state = BardoState.REBIRTH
        
        return {
            "day": self._day,
            "phase": self._phase.value,
            "state": self._current_state.value
        }
    
    @property
    def is_concluded(self) -> bool:
        return self._liberated or self._reborn
    
    @property
    def outcome(self) -> str:
        if self._liberated:
            return "Liberation"
        elif self._reborn:
            return f"Rebirth in {self._rebirth_realm.value}"
        return "In progress"
    
    @property
    def day(self) -> int:
        return self._day


# =============================================================================
# BARDO TRANSITION MATRIX
# =============================================================================

class BardoTransitionMatrix:
    """
    The Bardo Markov Chain.
    
    S_{t+1} = S_t · P(t)
    Time-dependent transition matrix.
    """
    
    N_STATES = 7  # Number of BardoState values
    T_MAX = 49
    
    def __init__(self, recognition_base: float = 0.3):
        self.recognition_base = recognition_base
        
        # Build time-dependent matrices
        self._matrices: Dict[int, np.ndarray] = {}
        self._build_matrices()
    
    def _build_matrices(self) -> None:
        """Build transition matrices for each day."""
        for day in range(1, self.T_MAX + 1):
            P = self._build_matrix_for_day(day)
            self._matrices[day] = P
    
    def _build_matrix_for_day(self, day: int) -> np.ndarray:
        """Build transition matrix for a specific day."""
        P = np.zeros((self.N_STATES, self.N_STATES))
        
        # State indices
        LIBERATION = 0
        CLEAR_LIGHT = 1
        PEACEFUL = 2
        WRATHFUL = 3
        KARMIC = 4
        WOMB_DOOR = 5
        REBIRTH = 6
        
        # Liberation and Rebirth are absorbing states
        P[LIBERATION, LIBERATION] = 1.0
        P[REBIRTH, REBIRTH] = 1.0
        
        # Recognition probability decreases over time
        recognition = self.recognition_base * np.exp(-day / 20)
        
        if day == 1:
            # Clear Light moment
            P[CLEAR_LIGHT, LIBERATION] = recognition
            P[CLEAR_LIGHT, PEACEFUL] = 1 - recognition
        
        elif day <= 7:
            # Peaceful deities
            P[PEACEFUL, LIBERATION] = recognition * 0.8
            P[PEACEFUL, PEACEFUL] = 0.3
            P[PEACEFUL, WRATHFUL] = 0.7 - recognition * 0.8
        
        elif day <= 14:
            # Wrathful deities
            P[WRATHFUL, LIBERATION] = recognition * 0.5
            P[WRATHFUL, WRATHFUL] = 0.3
            P[WRATHFUL, KARMIC] = 0.7 - recognition * 0.5
        
        else:
            # Karmic visions (Sidpa Bardo)
            rebirth_prob = (day - 14) / 35  # Increases toward day 49
            
            P[KARMIC, LIBERATION] = recognition * 0.1
            P[KARMIC, KARMIC] = 0.5 * (1 - rebirth_prob)
            P[KARMIC, WOMB_DOOR] = 0.4 * rebirth_prob
            P[KARMIC, REBIRTH] = 0.5 * rebirth_prob
            
            P[WOMB_DOOR, WOMB_DOOR] = 0.3
            P[WOMB_DOOR, REBIRTH] = 0.7
        
        # Normalize rows
        for i in range(self.N_STATES):
            row_sum = np.sum(P[i])
            if row_sum > 0:
                P[i] /= row_sum
            else:
                P[i, i] = 1.0  # Self-loop if no transitions
        
        return P
    
    def get_matrix(self, day: int) -> np.ndarray:
        """Get transition matrix for a specific day."""
        day = max(1, min(day, self.T_MAX))
        return self._matrices[day].copy()
    
    def evolve(self, state_dist: np.ndarray, day: int) -> np.ndarray:
        """Evolve state distribution by one day."""
        P = self.get_matrix(day)
        return state_dist @ P
    
    def simulate(self, n_days: int = 49) -> List[np.ndarray]:
        """
        Simulate full Bardo journey.
        
        Returns state distribution at each day.
        """
        # Start in Clear Light state
        state = np.zeros(self.N_STATES)
        state[1] = 1.0  # Clear Light
        
        history = [state.copy()]
        
        for day in range(1, n_days + 1):
            state = self.evolve(state, day)
            history.append(state.copy())
        
        return history
    
    def get_liberation_probability(self, n_simulations: int = 1000) -> float:
        """
        Monte Carlo estimate of liberation probability.
        """
        liberated = 0
        
        for _ in range(n_simulations):
            history = self.simulate(49)
            final = history[-1]
            if final[0] > 0.5:  # Liberation state
                liberated += 1
        
        return liberated / n_simulations


# =============================================================================
# VALIDATION
# =============================================================================

def validate_bardo() -> bool:
    """Validate Tibetan bardo module."""
    
    # Test Lights
    clear = create_clear_light()
    assert clear.is_source_light()
    assert not clear.is_trap()
    
    buddha_lights = create_buddha_lights()
    assert len(buddha_lights) == 5
    assert all(l.light_type == LightType.BRIGHT for l in buddha_lights)
    
    realm_lights = create_realm_lights()
    assert len(realm_lights) == 6
    assert all(l.is_trap() for l in realm_lights)
    
    # Test KarmicWind
    wind = KarmicWind()
    
    wind.add_action(KarmicAction(
        action="generosity",
        polarity=1,
        magnitude=1.0,
        realm_tendency=Realm.DEVA
    ))
    
    wind.add_action(KarmicAction(
        action="anger",
        polarity=-1,
        magnitude=0.5,
        realm_tendency=Realm.NARAKA
    ))
    
    target, strength = wind.compute_drift()
    assert isinstance(target, Realm)
    assert strength >= 0
    
    karma = wind.get_total_karma()
    assert karma == 0.5  # 1.0 - 0.5
    
    # Test BardoAgent
    agent = BardoAgent("TestAgent", recognition_ability=0.8)
    
    # Advance through days
    for _ in range(10):
        result = agent.advance_day()
        assert "day" in result
    
    assert agent.day == 10
    
    # Process lights
    result = agent.process_light(clear)
    assert result["action"] in ["MERGE", "MISSED"]
    
    # Test BardoTransitionMatrix
    matrix = BardoTransitionMatrix(recognition_base=0.5)
    
    P1 = matrix.get_matrix(1)
    assert P1.shape == (7, 7)
    
    # Check rows sum to 1
    for i in range(7):
        assert abs(np.sum(P1[i]) - 1.0) < 0.001
    
    # Simulate
    history = matrix.simulate(49)
    assert len(history) == 50  # 0 to 49
    
    # Final state should have probability in Liberation or Rebirth
    final = history[-1]
    assert final[0] + final[6] > 0.5  # Either liberated or reborn
    
    return True


if __name__ == "__main__":
    print("Validating Tibetan Bardo Module...")
    assert validate_bardo()
    print("✓ Tibetan Bardo Module validated")

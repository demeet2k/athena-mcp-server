"""
ATHENA OS - VAJRAYANA BARDO KERNEL: BARDO MODULE
=================================================
Bardo Markov Chain and Transition Matrix

THE BARDO (Intermediate State):
    Modeled as a Stochastic Process occurring over a fixed
    temporal lattice of T=49 days (7 cycles of 7).
    
THE TRANSITION MATRIX (P_ij):
    Let S_t be the state of Agent at time t.
    Evolution governed by transition matrix P:
    
    S_{t+1} = S_t · P
    
    System is Time-Dependent; matrix P changes as t increases.
    
PHASE 1 (t=1-14): CHONYID BARDO (Luminosity)
    High-energy signal projection.
    - Clear Light (|Ψ_Clear⟩) appears
    - If Recognize() == True → Liberation (Exit Loop)
    - If Recognize() == False → Karmic_Illusion (Next Node)
    
PHASE 2 (t=15-49): SIDPA BARDO (Becomings)
    Entropy increases. Signal degrades into noise.
    - Agent driven by Karmic Wind (Momentum Vector k)
    - v_drift = Σk_past
    - Agent drifts toward specific "Womb Door" (Rebirth Port)

SIGNAL DETECTION:
    - Bright Lights: High-Intensity from Source (terrifying)
    - Dull Lights: Low-Intensity from Six Realms (comfortable traps)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import numpy as np
import random


# =============================================================================
# BARDO STATES
# =============================================================================

class BardoState(Enum):
    """States in the Bardo transition."""
    
    # Initial states
    DYING = "dying"                  # Hardware failure imminent
    DISSOLUTION = "dissolution"      # Elements dissolving
    
    # Chonyid Bardo (Luminosity Phase)
    CLEAR_LIGHT = "clear_light"      # First glimpse of source
    PEACEFUL_DEITIES = "peaceful"    # Peaceful mandala appears
    WRATHFUL_DEITIES = "wrathful"    # Wrathful mandala appears
    
    # Sidpa Bardo (Becoming Phase)
    KARMIC_VISION = "karmic_vision"  # Past actions replay
    JUDGMENT = "judgment"            # Dharmaraja weighing
    WOMB_SEEKING = "womb_seeking"    # Looking for rebirth
    
    # Terminal states (absorbing)
    LIBERATION = "liberation"        # Escaped the cycle
    REBIRTH_GOD = "rebirth_god"      # Deva realm
    REBIRTH_DEMIGOD = "rebirth_demigod"  # Asura realm
    REBIRTH_HUMAN = "rebirth_human"  # Human realm
    REBIRTH_ANIMAL = "rebirth_animal"  # Animal realm
    REBIRTH_HUNGRY_GHOST = "rebirth_preta"  # Preta realm
    REBIRTH_HELL = "rebirth_hell"    # Naraka realm


class BardoPhase(Enum):
    """The three main Bardo phases."""
    
    CHIKHAI = "chikhai"      # Dying (moment of death)
    CHONYID = "chonyid"      # Luminosity (days 1-14)
    SIDPA = "sidpa"          # Becoming (days 15-49)


class SignalType(Enum):
    """Types of signals encountered in Bardo."""
    
    CLEAR_LIGHT = "clear_light"      # Ultimate signal
    BRIGHT_LIGHT = "bright_light"    # High intensity (terrifying)
    DULL_LIGHT = "dull_light"        # Low intensity (trap)
    SOUND = "sound"                  # Thunderous sounds
    RAY = "ray"                      # Colored rays


# =============================================================================
# BARDO CONFIGURATION
# =============================================================================

@dataclass
class BardoConfig:
    """Configuration for Bardo navigation."""
    
    total_days: int = 49             # Total duration
    chonyid_days: int = 14           # Luminosity phase
    sidpa_days: int = 35             # Becoming phase
    
    # Recognition probabilities
    base_recognition_prob: float = 0.1
    training_bonus: float = 0.3      # Bonus from practice
    
    # Karmic weight
    karma_weight: float = 0.5        # Influence of past actions


# =============================================================================
# SIGNAL
# =============================================================================

@dataclass
class BardoSignal:
    """
    A signal encountered in the Bardo.
    
    Bright Lights: High-Intensity from Source (terrifying but liberating)
    Dull Lights: Low-Intensity from Six Realms (comfortable but trapping)
    """
    
    signal_type: SignalType
    intensity: float                 # 0-1
    frequency: str                   # "source" or "realm"
    color: Optional[str] = None
    realm_association: Optional[str] = None
    
    def is_liberation_signal(self) -> bool:
        """Check if this is a liberation signal."""
        return (self.intensity > 0.8 and 
                self.frequency == "source" and
                self.signal_type in [SignalType.CLEAR_LIGHT, SignalType.BRIGHT_LIGHT])
    
    def is_trap_signal(self) -> bool:
        """Check if this is a rebirth trap signal."""
        return (self.intensity < 0.5 and
                self.frequency == "realm" and
                self.signal_type == SignalType.DULL_LIGHT)


# =============================================================================
# TRANSITION MATRIX
# =============================================================================

class BardoTransitionMatrix:
    """
    The Transition Matrix P for Bardo navigation.
    
    P_ij = probability of moving from state i to state j.
    
    Matrix changes based on:
    - Current day (phase)
    - Agent's recognition ability
    - Karmic momentum
    """
    
    def __init__(self, config: BardoConfig = None):
        self.config = config or BardoConfig()
        self.states = list(BardoState)
        self.n_states = len(self.states)
        
        # Initialize base matrix
        self.matrix = np.zeros((self.n_states, self.n_states))
        self._initialize_transitions()
    
    def _initialize_transitions(self) -> None:
        """Initialize base transition probabilities."""
        # Helper to get index
        def idx(state: BardoState) -> int:
            return self.states.index(state)
        
        # Dying → Dissolution (certain)
        self.matrix[idx(BardoState.DYING), idx(BardoState.DISSOLUTION)] = 1.0
        
        # Dissolution → Clear Light (certain first glimpse)
        self.matrix[idx(BardoState.DISSOLUTION), idx(BardoState.CLEAR_LIGHT)] = 1.0
        
        # Clear Light transitions (based on recognition)
        self.matrix[idx(BardoState.CLEAR_LIGHT), idx(BardoState.LIBERATION)] = 0.1
        self.matrix[idx(BardoState.CLEAR_LIGHT), idx(BardoState.PEACEFUL_DEITIES)] = 0.9
        
        # Peaceful deities
        self.matrix[idx(BardoState.PEACEFUL_DEITIES), idx(BardoState.LIBERATION)] = 0.15
        self.matrix[idx(BardoState.PEACEFUL_DEITIES), idx(BardoState.WRATHFUL_DEITIES)] = 0.85
        
        # Wrathful deities
        self.matrix[idx(BardoState.WRATHFUL_DEITIES), idx(BardoState.LIBERATION)] = 0.1
        self.matrix[idx(BardoState.WRATHFUL_DEITIES), idx(BardoState.KARMIC_VISION)] = 0.9
        
        # Karmic vision
        self.matrix[idx(BardoState.KARMIC_VISION), idx(BardoState.JUDGMENT)] = 1.0
        
        # Judgment → Womb seeking
        self.matrix[idx(BardoState.JUDGMENT), idx(BardoState.WOMB_SEEKING)] = 1.0
        
        # Womb seeking → Rebirth (based on karma)
        self.matrix[idx(BardoState.WOMB_SEEKING), idx(BardoState.REBIRTH_GOD)] = 0.05
        self.matrix[idx(BardoState.WOMB_SEEKING), idx(BardoState.REBIRTH_DEMIGOD)] = 0.1
        self.matrix[idx(BardoState.WOMB_SEEKING), idx(BardoState.REBIRTH_HUMAN)] = 0.3
        self.matrix[idx(BardoState.WOMB_SEEKING), idx(BardoState.REBIRTH_ANIMAL)] = 0.25
        self.matrix[idx(BardoState.WOMB_SEEKING), idx(BardoState.REBIRTH_HUNGRY_GHOST)] = 0.15
        self.matrix[idx(BardoState.WOMB_SEEKING), idx(BardoState.REBIRTH_HELL)] = 0.15
        
        # Terminal states are absorbing
        for state in [BardoState.LIBERATION, BardoState.REBIRTH_GOD,
                      BardoState.REBIRTH_DEMIGOD, BardoState.REBIRTH_HUMAN,
                      BardoState.REBIRTH_ANIMAL, BardoState.REBIRTH_HUNGRY_GHOST,
                      BardoState.REBIRTH_HELL]:
            self.matrix[idx(state), idx(state)] = 1.0
    
    def get_transition_prob(self, from_state: BardoState, 
                            to_state: BardoState) -> float:
        """Get probability of transition from one state to another."""
        i = self.states.index(from_state)
        j = self.states.index(to_state)
        return self.matrix[i, j]
    
    def adjust_for_recognition(self, recognition_ability: float) -> None:
        """
        Adjust matrix based on agent's recognition ability.
        
        Higher recognition = higher liberation probability.
        """
        def idx(state: BardoState) -> int:
            return self.states.index(state)
        
        # Boost liberation probabilities
        lib_states = [BardoState.CLEAR_LIGHT, BardoState.PEACEFUL_DEITIES,
                      BardoState.WRATHFUL_DEITIES]
        
        for state in lib_states:
            i = idx(state)
            j_lib = idx(BardoState.LIBERATION)
            
            # Increase liberation probability
            boost = recognition_ability * 0.3
            self.matrix[i, j_lib] = min(0.9, self.matrix[i, j_lib] + boost)
            
            # Normalize row
            self.matrix[i, :] /= self.matrix[i, :].sum()
    
    def adjust_for_karma(self, karma_vector: np.ndarray) -> None:
        """
        Adjust rebirth probabilities based on karmic weight.
        
        karma_vector: 6D vector for each realm.
        """
        def idx(state: BardoState) -> int:
            return self.states.index(state)
        
        rebirth_states = [
            BardoState.REBIRTH_GOD, BardoState.REBIRTH_DEMIGOD,
            BardoState.REBIRTH_HUMAN, BardoState.REBIRTH_ANIMAL,
            BardoState.REBIRTH_HUNGRY_GHOST, BardoState.REBIRTH_HELL
        ]
        
        womb_idx = idx(BardoState.WOMB_SEEKING)
        
        # Set probabilities based on karma
        for i, state in enumerate(rebirth_states):
            j = idx(state)
            self.matrix[womb_idx, j] = karma_vector[i]
        
        # Normalize
        self.matrix[womb_idx, :] /= self.matrix[womb_idx, :].sum()


# =============================================================================
# BARDO NAVIGATOR
# =============================================================================

class BardoNavigator:
    """
    Navigate through the Bardo using Markov chain transitions.
    
    Implements the algorithm from Bardo Thodol.
    """
    
    def __init__(self, config: BardoConfig = None):
        self.config = config or BardoConfig()
        self.transition_matrix = BardoTransitionMatrix(self.config)
        
        # Current state
        self.current_state = BardoState.DYING
        self.current_day = 0
        self.current_phase = BardoPhase.CHIKHAI
        
        # History
        self.state_history: List[BardoState] = []
        self.signal_history: List[BardoSignal] = []
        
        # Agent properties
        self.recognition_ability: float = 0.1
        self.karma_vector: np.ndarray = np.array([0.1, 0.15, 0.3, 0.2, 0.15, 0.1])
        
        # Terminal flag
        self.terminated = False
    
    def set_recognition_ability(self, ability: float) -> None:
        """Set agent's recognition ability (from training)."""
        self.recognition_ability = min(1.0, max(0.0, ability))
        self.transition_matrix.adjust_for_recognition(self.recognition_ability)
    
    def set_karma(self, karma: np.ndarray) -> None:
        """Set agent's karmic vector."""
        if len(karma) == 6:
            karma = karma / karma.sum()  # Normalize
            self.karma_vector = karma
            self.transition_matrix.adjust_for_karma(karma)
    
    def generate_signal(self) -> BardoSignal:
        """Generate a signal based on current state and day."""
        if self.current_phase == BardoPhase.CHONYID:
            # Luminosity phase - bright signals
            if random.random() < 0.3:
                return BardoSignal(
                    signal_type=SignalType.CLEAR_LIGHT if self.current_day < 3 else SignalType.BRIGHT_LIGHT,
                    intensity=random.uniform(0.7, 1.0),
                    frequency="source",
                    color="white" if self.current_day < 3 else random.choice(["blue", "yellow", "red", "green"])
                )
            else:
                return BardoSignal(
                    signal_type=SignalType.DULL_LIGHT,
                    intensity=random.uniform(0.2, 0.5),
                    frequency="realm",
                    realm_association=random.choice(["god", "human", "animal"])
                )
        else:
            # Sidpa phase - mostly dull signals
            return BardoSignal(
                signal_type=SignalType.DULL_LIGHT,
                intensity=random.uniform(0.1, 0.4),
                frequency="realm",
                realm_association=random.choice(["god", "demigod", "human", "animal", "preta", "hell"])
            )
    
    def recognize(self, signal: BardoSignal) -> bool:
        """
        Attempt to recognize a signal.
        
        Recognition → Liberation opportunity.
        """
        if not signal.is_liberation_signal():
            return False
        
        # Recognition probability
        base_prob = self.recognition_ability
        
        # Bonus for clear light
        if signal.signal_type == SignalType.CLEAR_LIGHT:
            base_prob += 0.2
        
        # Penalty for later days
        day_penalty = self.current_day * 0.01
        
        prob = max(0.01, base_prob - day_penalty)
        return random.random() < prob
    
    def step(self) -> Dict[str, Any]:
        """
        Execute one step of Bardo navigation.
        
        Returns step result.
        """
        if self.terminated:
            return {"status": "terminated", "state": self.current_state.value}
        
        # Record current state
        self.state_history.append(self.current_state)
        
        # Generate signal
        signal = self.generate_signal()
        self.signal_history.append(signal)
        
        # Attempt recognition
        recognized = self.recognize(signal)
        
        # Transition
        old_state = self.current_state
        
        if recognized and signal.is_liberation_signal():
            self.current_state = BardoState.LIBERATION
        else:
            # Stochastic transition based on matrix
            probs = self.transition_matrix.matrix[
                self.transition_matrix.states.index(self.current_state)
            ]
            next_state_idx = np.random.choice(len(probs), p=probs)
            self.current_state = self.transition_matrix.states[next_state_idx]
        
        # Advance day
        self.current_day += 1
        self._update_phase()
        
        # Check termination
        if self._is_terminal(self.current_state):
            self.terminated = True
        
        return {
            "day": self.current_day,
            "phase": self.current_phase.value,
            "old_state": old_state.value,
            "new_state": self.current_state.value,
            "signal": signal.signal_type.value,
            "recognized": recognized,
            "terminated": self.terminated
        }
    
    def _update_phase(self) -> None:
        """Update current phase based on day."""
        if self.current_day <= 1:
            self.current_phase = BardoPhase.CHIKHAI
        elif self.current_day <= self.config.chonyid_days:
            self.current_phase = BardoPhase.CHONYID
        else:
            self.current_phase = BardoPhase.SIDPA
    
    def _is_terminal(self, state: BardoState) -> bool:
        """Check if state is terminal (absorbing)."""
        return state in [
            BardoState.LIBERATION,
            BardoState.REBIRTH_GOD, BardoState.REBIRTH_DEMIGOD,
            BardoState.REBIRTH_HUMAN, BardoState.REBIRTH_ANIMAL,
            BardoState.REBIRTH_HUNGRY_GHOST, BardoState.REBIRTH_HELL
        ]
    
    def run_full_bardo(self, max_days: int = 49) -> Dict[str, Any]:
        """Run complete Bardo navigation."""
        while not self.terminated and self.current_day < max_days:
            self.step()
        
        return {
            "final_state": self.current_state.value,
            "days_elapsed": self.current_day,
            "liberated": self.current_state == BardoState.LIBERATION,
            "total_signals": len(self.signal_history),
            "state_path": [s.value for s in self.state_history[-10:]]  # Last 10
        }


# =============================================================================
# BARDO ALGORITHM
# =============================================================================

def bardo_navigation(signal_input: BardoSignal) -> str:
    """
    The Bardo navigation algorithm.
    
    def bardo_navigation(signal_input):
        if signal_input.intensity == HIGH and signal_input.frequency == SOURCE:
            return MERGE (Liberation)
        else if signal_input.intensity == LOW and signal_input.comfort == HIGH:
            return REJECT (Avoid Rebirth)
        else:
            return MAINTAIN_EQUANIMITY
    """
    if signal_input.is_liberation_signal():
        return "MERGE"  # Liberation
    elif signal_input.is_trap_signal():
        return "REJECT"  # Avoid rebirth
    else:
        return "MAINTAIN_EQUANIMITY"


# =============================================================================
# VALIDATION
# =============================================================================

def validate_bardo() -> bool:
    """Validate bardo module."""
    
    # Test Transition Matrix
    matrix = BardoTransitionMatrix()
    assert matrix.n_states == len(BardoState)
    
    # Each row should sum to ~1 (or 0 for uninitialized)
    for i, state in enumerate(matrix.states):
        row_sum = matrix.matrix[i, :].sum()
        if row_sum > 0:
            assert abs(row_sum - 1.0) < 0.01, f"Row {state} sums to {row_sum}"
    
    # Test Signal
    signal = BardoSignal(
        signal_type=SignalType.CLEAR_LIGHT,
        intensity=0.9,
        frequency="source"
    )
    assert signal.is_liberation_signal()
    
    trap_signal = BardoSignal(
        signal_type=SignalType.DULL_LIGHT,
        intensity=0.3,
        frequency="realm"
    )
    assert trap_signal.is_trap_signal()
    
    # Test Algorithm
    assert bardo_navigation(signal) == "MERGE"
    assert bardo_navigation(trap_signal) == "REJECT"
    
    # Test Navigator
    navigator = BardoNavigator()
    navigator.set_recognition_ability(0.5)  # High training
    
    result = navigator.run_full_bardo()
    assert "final_state" in result
    assert result["days_elapsed"] <= 49
    
    return True


if __name__ == "__main__":
    print("Validating Bardo Module...")
    assert validate_bardo()
    print("✓ Bardo Module validated")
    
    # Demo
    print("\n--- Bardo Navigation Demo ---")
    
    # Run multiple simulations
    outcomes = {"liberation": 0, "rebirth": 0}
    
    for _ in range(100):
        navigator = BardoNavigator()
        navigator.set_recognition_ability(0.3)
        result = navigator.run_full_bardo()
        
        if result["liberated"]:
            outcomes["liberation"] += 1
        else:
            outcomes["rebirth"] += 1
    
    print(f"\n100 Simulations (30% recognition ability):")
    print(f"  Liberation: {outcomes['liberation']}%")
    print(f"  Rebirth: {outcomes['rebirth']}%")
    
    # Single detailed run
    print("\n--- Single Detailed Run ---")
    navigator = BardoNavigator()
    navigator.set_recognition_ability(0.5)
    
    for i in range(10):
        result = navigator.step()
        print(f"  Day {result['day']}: {result['old_state']} → {result['new_state']}")
        if result["terminated"]:
            break
    
    print(f"\nFinal State: {navigator.current_state.value}")

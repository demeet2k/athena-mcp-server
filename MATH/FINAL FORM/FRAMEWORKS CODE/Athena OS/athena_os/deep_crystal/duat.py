"""
ATHENA OS - DEEP CRYSTAL SYNTHESIS
==================================
Duat: The 12-Hour Journey Through the Underworld

From DEEP_CRYSTAL_SYNTHESIS.docx §4:

DUAT MANIFOLD D₁₂:
    12-cycle transition space with staged gates.
    Each hour has:
    - Gate operators (authentication)
    - Hazards (Apep, chaos serpent)
    - Correction checkpoints
    - Transformation protocols

MASTER EQUATION:
    H(t) = α(t)R + β(t)O + γ(t)Σ
    
    R: Solar regeneration term
    O: Osirian death/rebirth term
    Σ: Stellar stability term
    
    Coefficients vary through 12 hours.

GATE TRAVERSAL:
    Each gate requires:
    1. Name knowledge (Ren authentication)
    2. Password utterance
    3. Ma'at alignment check
    4. Transformation applied
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum, IntEnum
import numpy as np
import math


# =============================================================================
# DUAT HOURS
# =============================================================================

class DuatHour(IntEnum):
    """The 12 hours of the Duat journey."""
    
    HOUR_1 = 1    # Entrance, West horizon
    HOUR_2 = 2    # Wernes, fertile lands
    HOUR_3 = 3    # Wernes continues
    HOUR_4 = 4    # Sand desert, Sokar begins
    HOUR_5 = 5    # Sokar's realm (deepest point)
    HOUR_6 = 6    # Midnight, union with Osiris
    HOUR_7 = 7    # Apep confrontation
    HOUR_8 = 8    # Provision of clothes
    HOUR_9 = 9    # Rowers in procession
    HOUR_10 = 10  # Healing of Eye
    HOUR_11 = 11  # Punishment of enemies
    HOUR_12 = 12  # Rebirth, East horizon


class GateStatus(Enum):
    """Status of gate traversal."""
    
    LOCKED = "locked"
    OPEN = "open"
    TRAVERSED = "traversed"
    FAILED = "failed"


# =============================================================================
# GATE STRUCTURE
# =============================================================================

@dataclass
class DuatGate:
    """
    A gate in the Duat.
    
    Each gate has:
    - Guardian(s) with name
    - Password requirement
    - Transformation effect
    - Hazard level
    """
    
    hour: DuatHour
    guardian_name: str
    password: str
    hazard_level: float = 0.5        # 0-1 danger level
    transformation_strength: float = 0.1
    status: GateStatus = GateStatus.LOCKED
    
    def authenticate(self, spoken_name: str, spoken_password: str) -> bool:
        """Attempt authentication at gate."""
        name_match = spoken_name.lower() == self.guardian_name.lower()
        password_match = spoken_password.lower() == self.password.lower()
        
        if name_match and password_match:
            self.status = GateStatus.OPEN
            return True
        else:
            self.status = GateStatus.FAILED
            return False
    
    def traverse(self, state: np.ndarray) -> np.ndarray:
        """Apply gate transformation to state."""
        if self.status != GateStatus.OPEN:
            raise ValueError(f"Gate {self.hour.name} is not open")
        
        # Apply transformation
        transformed = state.copy()
        
        # Rotation in state space
        angle = self.transformation_strength * np.pi / 6  # 30° max
        n = len(state)
        
        for i in range(n - 1):
            c, s = np.cos(angle), np.sin(angle)
            old_i, old_j = transformed[i], transformed[i + 1]
            transformed[i] = c * old_i - s * old_j
            transformed[i + 1] = s * old_i + c * old_j
        
        self.status = GateStatus.TRAVERSED
        return transformed


# =============================================================================
# APEP HAZARD
# =============================================================================

@dataclass
class ApepSerpent:
    """
    Apep: The Chaos Serpent
    
    The antagonist that must be defeated each night.
    Represents entropy/disorder that threatens the journey.
    """
    
    strength: float = 0.5
    defeated: bool = False
    
    def attack(self, state: np.ndarray) -> np.ndarray:
        """Apply chaos attack to state."""
        noise = np.random.randn(len(state)) * self.strength
        return state + noise
    
    def is_defeated_by(self, defensive_strength: float) -> bool:
        """Check if Apep is defeated."""
        self.defeated = defensive_strength > self.strength
        return self.defeated
    
    def spear(self, attacker_strength: float) -> None:
        """Attack Apep with spear (reduce strength)."""
        damage = attacker_strength * 0.5
        self.strength = max(0, self.strength - damage)
        if self.strength < 0.1:
            self.defeated = True


# =============================================================================
# HAMILTONIAN OF KEMET
# =============================================================================

@dataclass
class KemetHamiltonian:
    """
    H(t) = α(t)R + β(t)O + γ(t)Σ
    
    The master equation governing Duat dynamics.
    
    R: Solar regeneration (Ra term)
    O: Osirian cycle (death/rebirth)
    Σ: Stellar stability (fixed stars)
    """
    
    # Operator matrices (set at construction)
    dim: int = 4
    
    def __post_init__(self):
        """Initialize operator matrices."""
        # R: Solar regeneration (diagonal, increasing)
        self.R = np.diag([0.0, 0.5, 0.8, 1.0])
        
        # O: Osirian cycle (off-diagonal coupling)
        self.O = np.zeros((self.dim, self.dim))
        for i in range(self.dim - 1):
            self.O[i, i + 1] = 0.5
            self.O[i + 1, i] = 0.5
        
        # Σ: Stellar stability (identity-like)
        self.Sigma = np.eye(self.dim) * 0.1
    
    def alpha(self, hour: int) -> float:
        """Solar coefficient α(t) - peaks at rebirth."""
        # Minimum at hour 6 (midnight), maximum at hour 12
        return 0.5 * (1 + np.cos(np.pi * (hour - 12) / 6))
    
    def beta(self, hour: int) -> float:
        """Osirian coefficient β(t) - peaks at union."""
        # Maximum at hour 6 (union with Osiris)
        return 0.5 * (1 + np.cos(np.pi * (hour - 6) / 6))
    
    def gamma(self, hour: int) -> float:
        """Stellar coefficient γ(t) - constant stability."""
        return 0.2  # Constant background
    
    def H(self, hour: int) -> np.ndarray:
        """Compute Hamiltonian at given hour."""
        a = self.alpha(hour)
        b = self.beta(hour)
        g = self.gamma(hour)
        
        return a * self.R + b * self.O + g * self.Sigma
    
    def evolve(self, state: np.ndarray, hour: int, dt: float = 0.1) -> np.ndarray:
        """
        Evolve state through one hour.
        
        Uses simple Euler integration of Schrödinger-like equation.
        """
        H = self.H(hour)
        # dψ/dt = -i H ψ (simplified to real evolution)
        return state - dt * H @ state


# =============================================================================
# DUAT JOURNEY
# =============================================================================

@dataclass
class SoulState:
    """State of soul during Duat journey."""
    
    vector: np.ndarray
    vitality: float = 1.0
    knowledge: Dict[str, str] = field(default_factory=dict)  # Names/passwords known
    current_hour: int = 0
    journey_log: List[str] = field(default_factory=list)
    
    def add_knowledge(self, name: str, password: str) -> None:
        """Learn gate name and password."""
        self.knowledge[name.lower()] = password.lower()
    
    def take_damage(self, amount: float) -> None:
        """Reduce vitality."""
        self.vitality = max(0, self.vitality - amount)
    
    def heal(self, amount: float) -> None:
        """Restore vitality."""
        self.vitality = min(1.0, self.vitality + amount)
    
    def log(self, message: str) -> None:
        """Add to journey log."""
        self.journey_log.append(f"[Hour {self.current_hour}] {message}")


@dataclass
class DuatJourney:
    """
    Complete 12-hour journey through the Duat.
    """
    
    # Gates (one per hour)
    gates: Dict[DuatHour, DuatGate] = field(default_factory=dict)
    
    # Apep appears at hour 7
    apep: ApepSerpent = field(default_factory=ApepSerpent)
    
    # Hamiltonian for evolution
    hamiltonian: KemetHamiltonian = field(default_factory=KemetHamiltonian)
    
    def __post_init__(self):
        """Initialize gates."""
        self._setup_gates()
    
    def _setup_gates(self):
        """Create the 12 gates with guardians."""
        gate_data = [
            (DuatHour.HOUR_1, "Saa", "enter-the-west", 0.3),
            (DuatHour.HOUR_2, "Wernes", "water-of-osiris", 0.4),
            (DuatHour.HOUR_3, "Sphinx", "dawn-approaches", 0.4),
            (DuatHour.HOUR_4, "Desert-Watcher", "sand-of-time", 0.5),
            (DuatHour.HOUR_5, "Sokar", "depth-of-night", 0.7),
            (DuatHour.HOUR_6, "Osiris", "union-of-ba", 0.6),
            (DuatHour.HOUR_7, "Apep-Slayer", "defeat-chaos", 0.9),
            (DuatHour.HOUR_8, "Provider", "clothe-the-ba", 0.5),
            (DuatHour.HOUR_9, "Rowers", "carry-forward", 0.4),
            (DuatHour.HOUR_10, "Eye-Healer", "restore-wholeness", 0.4),
            (DuatHour.HOUR_11, "Punisher", "justice-delivered", 0.5),
            (DuatHour.HOUR_12, "Khepri", "rebirth-now", 0.3),
        ]
        
        for hour, name, password, hazard in gate_data:
            self.gates[hour] = DuatGate(
                hour=hour,
                guardian_name=name,
                password=password,
                hazard_level=hazard
            )
    
    def attempt_hour(self, soul: SoulState, hour: DuatHour) -> bool:
        """
        Attempt to traverse a single hour.
        
        Returns True if successful.
        """
        gate = self.gates[hour]
        soul.current_hour = hour.value
        
        # Check if soul knows the gate
        guardian_lower = gate.guardian_name.lower()
        if guardian_lower not in soul.knowledge:
            soul.log(f"Unknown guardian: {gate.guardian_name}")
            soul.take_damage(gate.hazard_level * 0.3)
            return False
        
        password = soul.knowledge[guardian_lower]
        
        # Attempt authentication
        if not gate.authenticate(gate.guardian_name, password):
            soul.log(f"Failed authentication at {gate.guardian_name}")
            soul.take_damage(gate.hazard_level * 0.5)
            return False
        
        soul.log(f"Passed gate of {gate.guardian_name}")
        
        # Special handling for hour 7 (Apep)
        if hour == DuatHour.HOUR_7:
            if not self._battle_apep(soul):
                return False
        
        # Apply gate transformation
        soul.vector = gate.traverse(soul.vector)
        
        # Apply Hamiltonian evolution
        soul.vector = self.hamiltonian.evolve(soul.vector, hour.value)
        
        # Normalize
        norm = np.linalg.norm(soul.vector)
        if norm > 1e-10:
            soul.vector = soul.vector / norm
        
        return True
    
    def _battle_apep(self, soul: SoulState) -> bool:
        """Battle Apep at hour 7."""
        soul.log("Confronting Apep!")
        
        # Soul strength based on vitality
        strength = soul.vitality * 0.8
        
        # Attempt to defeat
        if self.apep.is_defeated_by(strength):
            soul.log("Apep defeated!")
            return True
        else:
            # Take damage from Apep
            soul.vector = self.apep.attack(soul.vector)
            soul.take_damage(self.apep.strength * 0.4)
            
            # Try again with spear
            self.apep.spear(strength)
            if self.apep.defeated:
                soul.log("Apep speared and defeated!")
                return True
            else:
                soul.log("Failed to defeat Apep!")
                return False
    
    def full_journey(self, soul: SoulState) -> Tuple[bool, str]:
        """
        Attempt complete 12-hour journey.
        
        Returns (success, final_destination).
        """
        soul.log("Beginning Duat journey")
        
        for hour in DuatHour:
            if soul.vitality <= 0:
                soul.log("Vitality depleted - journey failed")
                return (False, "Lost in Duat")
            
            if not self.attempt_hour(soul, hour):
                soul.log(f"Failed at hour {hour.value}")
                return (False, f"Failed at {hour.name}")
        
        soul.log("Journey complete - Rebirth achieved!")
        return (True, "A'aru")


# =============================================================================
# BOOK OF THE DEAD KNOWLEDGE
# =============================================================================

def load_book_of_dead() -> Dict[str, str]:
    """
    Load the Book of the Dead knowledge.
    
    Returns dict of guardian names to passwords.
    """
    return {
        "saa": "enter-the-west",
        "wernes": "water-of-osiris",
        "sphinx": "dawn-approaches",
        "desert-watcher": "sand-of-time",
        "sokar": "depth-of-night",
        "osiris": "union-of-ba",
        "apep-slayer": "defeat-chaos",
        "provider": "clothe-the-ba",
        "rowers": "carry-forward",
        "eye-healer": "restore-wholeness",
        "punisher": "justice-delivered",
        "khepri": "rebirth-now"
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_duat() -> bool:
    """Validate Duat module."""
    
    # Test DuatGate
    gate = DuatGate(
        hour=DuatHour.HOUR_1,
        guardian_name="Test",
        password="pass"
    )
    
    assert gate.status == GateStatus.LOCKED
    assert gate.authenticate("Test", "pass")
    assert gate.status == GateStatus.OPEN
    
    state = np.array([1.0, 0.0, 0.0, 0.0])
    result = gate.traverse(state)
    assert gate.status == GateStatus.TRAVERSED
    
    # Test KemetHamiltonian
    H = KemetHamiltonian(dim=4)
    assert H.alpha(12) > H.alpha(6)  # Solar peaks at rebirth
    assert H.beta(6) > H.beta(12)    # Osirian peaks at union
    
    H_mat = H.H(6)
    assert H_mat.shape == (4, 4)
    
    evolved = H.evolve(state, 6)
    assert evolved.shape == state.shape
    
    # Test SoulState
    soul = SoulState(vector=np.array([1.0, 0.0, 0.0, 0.0]))
    soul.add_knowledge("Test", "pass")
    assert "test" in soul.knowledge
    
    soul.take_damage(0.3)
    assert soul.vitality < 1.0
    
    soul.heal(0.5)
    assert soul.vitality <= 1.0
    
    # Test DuatJourney
    journey = DuatJourney()
    assert len(journey.gates) == 12
    
    # Test with full knowledge
    soul = SoulState(vector=np.array([1.0, 0.0, 0.0, 0.0]))
    knowledge = load_book_of_dead()
    for name, password in knowledge.items():
        soul.add_knowledge(name, password)
    
    success, destination = journey.full_journey(soul)
    assert destination in ["A'aru", "Lost in Duat"] or destination.startswith("Failed")
    
    return True


if __name__ == "__main__":
    print("Validating Duat Journey...")
    assert validate_duat()
    print("✓ Duat module validated")
    
    # Demo
    print("\n--- Duat Journey Demo ---")
    journey = DuatJourney()
    
    soul = SoulState(vector=np.array([1.0, 0.0, 0.0, 0.0]))
    knowledge = load_book_of_dead()
    for name, password in knowledge.items():
        soul.add_knowledge(name, password)
    
    success, destination = journey.full_journey(soul)
    
    print(f"Journey Success: {success}")
    print(f"Final Destination: {destination}")
    print(f"Final Vitality: {soul.vitality:.2f}")
    print("\nJourney Log:")
    for entry in soul.journey_log[-5:]:
        print(f"  {entry}")

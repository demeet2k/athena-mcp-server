"""
ATHENA OS - VAJRAYANA BARDO KERNEL: MANDALA MODULE
===================================================
Mandala Manifold and Five Buddha Families Vector Space

THE MANDALA:
    Not an aesthetic object but a Projective Geometry representing
    the high-dimensional state space of the system.
    Serves as GUI for the Agent to navigate the kernel.
    
CENTER-PERIPHERY METRIC:
    Mandala space M as polar coordinate system (r, θ)
    centering on the Null Point (Bindu/Seed Syllable).
    
    - Center (r=0): Singularity/Source Node = Dharmakaya
      The unmanifest, non-dual vacuum state |Ω⟩
      
    - Periphery (r→R): Manifest Boundary = Nirmanakaya
      Fragmented, high-entropy reality
      
    - Gradient: Path from periphery to center is Negative Entropy
      Gradient (-ΔS). Movement toward r=0 requires energy input.

FIVE-SECTOR PARTITION (Dhyani Basis):
    M = V_Center ⊕ V_East ⊕ V_South ⊕ V_West ⊕ V_North
    
    Each vector represents a specific Error Mode (Poison) and
    its corresponding Rectified State (Wisdom).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np


# =============================================================================
# BUDDHA FAMILY DEFINITIONS
# =============================================================================

class BuddhaFamily(Enum):
    """The Five Buddha Families (Dhyani Buddhas)."""
    
    VAIROCANA = "vairocana"          # Center - White
    AKSHOBHYA = "akshobhya"          # East - Blue
    RATNASAMBHAVA = "ratnasambhava"  # South - Yellow
    AMITABHA = "amitabha"            # West - Red
    AMOGHASIDDHI = "amoghasiddhi"    # North - Green


class ErrorMode(Enum):
    """The Five Poisons (Kleshas) - Error Modes."""
    
    IGNORANCE = "ignorance"          # Null Data
    ANGER = "anger"                  # High Voltage
    PRIDE = "pride"                  # Inflation
    DESIRE = "desire"                # Attraction
    ENVY = "envy"                    # Comparison


class WisdomMode(Enum):
    """The Five Wisdoms - Rectified States."""
    
    ALL_ENCOMPASSING = "all_encompassing"        # Dharmadhatu
    MIRROR_LIKE = "mirror_like"                  # Reflection
    EQUALIZING = "equalizing"                    # Equanimity
    DISCRIMINATING = "discriminating"            # Discernment
    ALL_ACCOMPLISHING = "all_accomplishing"      # Action


class MandalaOperator(Enum):
    """Operators for transmuting poisons to wisdoms."""
    
    CLR = "clear"      # Clear ignorance → space
    RFL = "reflect"    # Reflect anger → mirror wisdom
    EQU = "equalize"   # Equalize pride → equanimity
    SRT = "sort"       # Sort desire → discrimination
    EXE = "execute"    # Execute envy → accomplishment


# =============================================================================
# BUDDHA FAMILY VECTOR
# =============================================================================

@dataclass
class BuddhaFamilyVector:
    """
    Vector representation of a Buddha Family.
    
    Maps Error Mode → Rectified State via Operator.
    """
    
    family: BuddhaFamily
    direction: str                   # Cardinal direction
    color: str                       # Associated color
    element: str                     # Associated element
    
    # Error/Wisdom mapping
    error_mode: ErrorMode
    wisdom_mode: WisdomMode
    operator: MandalaOperator
    
    # Seed syllable (bija mantra)
    seed_syllable: str
    
    # Position in mandala (r, θ)
    radius: float = 0.0              # 0 = center
    theta: float = 0.0               # Angle in radians
    
    def get_position_vector(self) -> np.ndarray:
        """Get 2D position in mandala space."""
        x = self.radius * np.cos(self.theta)
        y = self.radius * np.sin(self.theta)
        return np.array([x, y])
    
    def get_basis_vector(self) -> np.ndarray:
        """Get 5D basis vector (one-hot encoding)."""
        families = list(BuddhaFamily)
        idx = families.index(self.family)
        vec = np.zeros(5)
        vec[idx] = 1.0
        return vec
    
    def transmute(self, error_intensity: float) -> Tuple[WisdomMode, float]:
        """
        Transmute error to wisdom.
        
        Returns (wisdom_mode, wisdom_intensity).
        """
        # Transmutation preserves intensity but changes polarity
        wisdom_intensity = error_intensity
        return (self.wisdom_mode, wisdom_intensity)


# =============================================================================
# FIVE BUDDHA FAMILIES DATABASE
# =============================================================================

BUDDHA_FAMILIES = {
    BuddhaFamily.VAIROCANA: BuddhaFamilyVector(
        family=BuddhaFamily.VAIROCANA,
        direction="center",
        color="white",
        element="space",
        error_mode=ErrorMode.IGNORANCE,
        wisdom_mode=WisdomMode.ALL_ENCOMPASSING,
        operator=MandalaOperator.CLR,
        seed_syllable="OM",
        radius=0.0,
        theta=0.0
    ),
    BuddhaFamily.AKSHOBHYA: BuddhaFamilyVector(
        family=BuddhaFamily.AKSHOBHYA,
        direction="east",
        color="blue",
        element="water",
        error_mode=ErrorMode.ANGER,
        wisdom_mode=WisdomMode.MIRROR_LIKE,
        operator=MandalaOperator.RFL,
        seed_syllable="HUM",
        radius=1.0,
        theta=0.0
    ),
    BuddhaFamily.RATNASAMBHAVA: BuddhaFamilyVector(
        family=BuddhaFamily.RATNASAMBHAVA,
        direction="south",
        color="yellow",
        element="earth",
        error_mode=ErrorMode.PRIDE,
        wisdom_mode=WisdomMode.EQUALIZING,
        operator=MandalaOperator.EQU,
        seed_syllable="TRAM",
        radius=1.0,
        theta=np.pi/2
    ),
    BuddhaFamily.AMITABHA: BuddhaFamilyVector(
        family=BuddhaFamily.AMITABHA,
        direction="west",
        color="red",
        element="fire",
        error_mode=ErrorMode.DESIRE,
        wisdom_mode=WisdomMode.DISCRIMINATING,
        operator=MandalaOperator.SRT,
        seed_syllable="HRIH",
        radius=1.0,
        theta=np.pi
    ),
    BuddhaFamily.AMOGHASIDDHI: BuddhaFamilyVector(
        family=BuddhaFamily.AMOGHASIDDHI,
        direction="north",
        color="green",
        element="air",
        error_mode=ErrorMode.ENVY,
        wisdom_mode=WisdomMode.ALL_ACCOMPLISHING,
        operator=MandalaOperator.EXE,
        seed_syllable="AH",
        radius=1.0,
        theta=3*np.pi/2
    ),
}


# =============================================================================
# MANDALA MANIFOLD
# =============================================================================

class MandalaManifold:
    """
    The Mandala Manifold (M).
    
    Polar coordinate system (r, θ) centering on Null Point.
    Partitioned into five orthogonal subspaces.
    
    M = V_Center ⊕ V_East ⊕ V_South ⊕ V_West ⊕ V_North
    """
    
    def __init__(self, max_radius: float = 1.0):
        self.max_radius = max_radius
        self.families = BUDDHA_FAMILIES
        
        # Current state in mandala
        self.current_position: np.ndarray = np.array([0.0, 0.0])
        self.current_state: np.ndarray = np.zeros(5)  # 5D state vector
        
    def get_family(self, family: BuddhaFamily) -> BuddhaFamilyVector:
        """Get a Buddha family by enum."""
        return self.families[family]
    
    def project_to_sector(self, state_vector: np.ndarray) -> BuddhaFamily:
        """
        Project a 5D state vector to its dominant sector.
        
        Returns the Buddha Family with highest activation.
        """
        if len(state_vector) != 5:
            raise ValueError("State vector must be 5D")
        
        families = list(BuddhaFamily)
        max_idx = np.argmax(np.abs(state_vector))
        return families[max_idx]
    
    def error_to_wisdom_lookup(self, error: ErrorMode) -> Tuple[BuddhaFamily, WisdomMode, MandalaOperator]:
        """
        Lookup table: map error mode to correction.
        
        Returns (family, wisdom, operator).
        """
        for family, vector in self.families.items():
            if vector.error_mode == error:
                return (family, vector.wisdom_mode, vector.operator)
        
        # Default to center
        return (BuddhaFamily.VAIROCANA, WisdomMode.ALL_ENCOMPASSING, MandalaOperator.CLR)
    
    def compute_entropy_gradient(self, position: np.ndarray) -> float:
        """
        Compute entropy gradient at position.
        
        Movement toward center (r=0) is negative entropy.
        """
        r = np.linalg.norm(position)
        # Entropy increases with radius
        return r / self.max_radius
    
    def move_toward_center(self, current_pos: np.ndarray, 
                           energy: float) -> np.ndarray:
        """
        Move toward center using energy input.
        
        Requires energy to overcome centrifugal drift (Samsara).
        """
        r = np.linalg.norm(current_pos)
        if r < 0.01:
            return current_pos  # Already at center
        
        # Movement proportional to energy
        direction = -current_pos / r  # Toward center
        step = min(energy, r)  # Can't overshoot
        
        return current_pos + direction * step
    
    def get_sector_at_position(self, position: np.ndarray) -> BuddhaFamily:
        """Get the sector (Buddha Family) at a position."""
        if np.linalg.norm(position) < 0.1:
            return BuddhaFamily.VAIROCANA
        
        theta = np.arctan2(position[1], position[0])
        if theta < 0:
            theta += 2 * np.pi
        
        # Divide circle into 4 quadrants (excluding center)
        if theta < np.pi/4 or theta >= 7*np.pi/4:
            return BuddhaFamily.AKSHOBHYA  # East
        elif theta < 3*np.pi/4:
            return BuddhaFamily.RATNASAMBHAVA  # South
        elif theta < 5*np.pi/4:
            return BuddhaFamily.AMITABHA  # West
        else:
            return BuddhaFamily.AMOGHASIDDHI  # North
    
    def apply_operator(self, error: ErrorMode, 
                       intensity: float) -> Dict[str, Any]:
        """
        Apply transmutation operator to error.
        
        Returns result of transformation.
        """
        family, wisdom, operator = self.error_to_wisdom_lookup(error)
        vector = self.families[family]
        
        wisdom_mode, wisdom_intensity = vector.transmute(intensity)
        
        return {
            "error": error.value,
            "family": family.value,
            "operator": operator.value,
            "wisdom": wisdom_mode.value,
            "intensity": wisdom_intensity,
            "seed_syllable": vector.seed_syllable
        }


# =============================================================================
# MANDALA NAVIGATOR
# =============================================================================

class MandalaNavigator:
    """
    Navigate the Mandala space.
    
    Provides path-finding from periphery to center.
    """
    
    def __init__(self):
        self.manifold = MandalaManifold()
        self.path_history: List[np.ndarray] = []
        
    def initialize(self, starting_sector: BuddhaFamily = None) -> np.ndarray:
        """Initialize at a sector on the periphery."""
        if starting_sector is None:
            # Random position on periphery
            theta = np.random.uniform(0, 2*np.pi)
            r = self.manifold.max_radius
        else:
            vector = self.manifold.families[starting_sector]
            theta = vector.theta
            r = vector.radius if vector.radius > 0 else self.manifold.max_radius
        
        position = np.array([r * np.cos(theta), r * np.sin(theta)])
        self.manifold.current_position = position
        self.path_history = [position.copy()]
        
        return position
    
    def step_toward_center(self, energy: float = 0.1) -> Dict[str, Any]:
        """Take one step toward the center (liberation)."""
        old_pos = self.manifold.current_position.copy()
        new_pos = self.manifold.move_toward_center(old_pos, energy)
        
        self.manifold.current_position = new_pos
        self.path_history.append(new_pos.copy())
        
        old_sector = self.manifold.get_sector_at_position(old_pos)
        new_sector = self.manifold.get_sector_at_position(new_pos)
        
        return {
            "old_position": old_pos.tolist(),
            "new_position": new_pos.tolist(),
            "old_sector": old_sector.value,
            "new_sector": new_sector.value,
            "entropy": self.manifold.compute_entropy_gradient(new_pos),
            "at_center": np.linalg.norm(new_pos) < 0.1
        }
    
    def navigate_to_center(self, energy_per_step: float = 0.1,
                           max_steps: int = 100) -> Dict[str, Any]:
        """Navigate from current position to center."""
        steps = 0
        
        while np.linalg.norm(self.manifold.current_position) >= 0.1 and steps < max_steps:
            self.step_toward_center(energy_per_step)
            steps += 1
        
        return {
            "steps_taken": steps,
            "final_position": self.manifold.current_position.tolist(),
            "reached_center": np.linalg.norm(self.manifold.current_position) < 0.1,
            "path_length": len(self.path_history),
            "total_energy": steps * energy_per_step
        }
    
    def get_current_sector_info(self) -> Dict[str, Any]:
        """Get info about current sector."""
        sector = self.manifold.get_sector_at_position(self.manifold.current_position)
        vector = self.manifold.families[sector]
        
        return {
            "sector": sector.value,
            "direction": vector.direction,
            "color": vector.color,
            "element": vector.element,
            "error_mode": vector.error_mode.value,
            "wisdom_mode": vector.wisdom_mode.value,
            "seed_syllable": vector.seed_syllable
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_mandala() -> bool:
    """Validate mandala module."""
    
    # Test Buddha Families
    assert len(BUDDHA_FAMILIES) == 5
    
    for family, vector in BUDDHA_FAMILIES.items():
        assert vector.family == family
        assert vector.seed_syllable is not None
    
    # Test Mandala Manifold
    manifold = MandalaManifold()
    
    # Test error lookup
    family, wisdom, op = manifold.error_to_wisdom_lookup(ErrorMode.ANGER)
    assert family == BuddhaFamily.AKSHOBHYA
    assert wisdom == WisdomMode.MIRROR_LIKE
    
    # Test transmutation
    result = manifold.apply_operator(ErrorMode.PRIDE, 0.8)
    assert result["wisdom"] == "equalizing"
    
    # Test movement
    pos = np.array([1.0, 0.0])
    new_pos = manifold.move_toward_center(pos, 0.5)
    assert np.linalg.norm(new_pos) < np.linalg.norm(pos)
    
    # Test Navigator
    navigator = MandalaNavigator()
    navigator.initialize(BuddhaFamily.AKSHOBHYA)
    
    result = navigator.navigate_to_center(energy_per_step=0.2, max_steps=20)
    assert result["reached_center"]
    
    # Test sector detection
    info = navigator.get_current_sector_info()
    assert "sector" in info
    
    return True


if __name__ == "__main__":
    print("Validating Mandala Module...")
    assert validate_mandala()
    print("✓ Mandala Module validated")
    
    # Demo
    print("\n--- Mandala Navigator Demo ---")
    navigator = MandalaNavigator()
    
    print("\nStarting at East (Akshobhya)...")
    navigator.initialize(BuddhaFamily.AKSHOBHYA)
    
    info = navigator.get_current_sector_info()
    print(f"  Sector: {info['sector']}")
    print(f"  Error Mode: {info['error_mode']}")
    print(f"  Wisdom Mode: {info['wisdom_mode']}")
    
    print("\nNavigating to center...")
    result = navigator.navigate_to_center(energy_per_step=0.15)
    print(f"  Steps: {result['steps_taken']}")
    print(f"  Reached Center: {result['reached_center']}")
    
    print("\n--- Transmutation Demo ---")
    manifold = MandalaManifold()
    
    for error in ErrorMode:
        result = manifold.apply_operator(error, 0.7)
        print(f"  {error.value} → {result['wisdom']} (via {result['operator']})")

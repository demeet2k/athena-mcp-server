"""
ATHENA OS - TIBETAN: MANDALA MODULE
====================================
Projective Geometry and State-Space Topology

THE MANDALA:
    Not an aesthetic object but a PROJECTIVE GEOMETRY
    representing the high-dimensional state space of the system.
    The GUI for navigating the kernel.

THE CENTER-PERIPHERY METRIC:
    - Center (r=0): The Singularity/Source Node
      Dharmakaya (Truth Body) - unmanifest vacuum |Ω⟩
    - Periphery (r→R): The Manifest Boundary
      Nirmanakaya (Emanation Body) - fragmented reality
    - Gradient: Negative entropy gradient (-ΔS)
      Movement toward center requires energy (Attention/Samadhi)

THE FIVE-SECTOR PARTITION (DHYANI BASIS):
    M = V_Center ⊕ V_East ⊕ V_South ⊕ V_West ⊕ V_North
    
    Each represents an Error Mode (Poison) and Rectified State (Wisdom):
    - Vairocana (Center): Ignorance → All-Encompassing Space
    - Akshobhya (East): Anger → Mirror-Like Wisdom
    - Ratnasambhava (South): Pride → Equalizing Wisdom
    - Amitabha (West): Desire → Discriminating Wisdom
    - Amoghasiddhi (North): Envy → All-Accomplishing Wisdom
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np


# =============================================================================
# BUDDHA FAMILIES
# =============================================================================

class BuddhaFamily(Enum):
    """The Five Dhyani Buddha Families."""
    
    VAIROCANA = "vairocana"           # Center - Illuminator
    AKSHOBHYA = "akshobhya"           # East - Immovable
    RATNASAMBHAVA = "ratnasambhava"   # South - Jewel-Born
    AMITABHA = "amitabha"             # West - Infinite Light
    AMOGHASIDDHI = "amoghasiddhi"     # North - Unfailing Success


class Direction(Enum):
    """Cardinal directions in the mandala."""
    
    CENTER = "center"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"


class Poison(Enum):
    """The Five Poisons (Error Modes)."""
    
    IGNORANCE = "ignorance"       # Null data
    ANGER = "anger"               # High voltage
    PRIDE = "pride"               # Inflation
    DESIRE = "desire"             # Attraction
    ENVY = "envy"                 # Comparison


class Wisdom(Enum):
    """The Five Wisdoms (Rectified States)."""
    
    DHARMADHATU = "dharmadhatu"           # All-encompassing space
    MIRROR = "mirror"                     # Mirror-like wisdom
    EQUALITY = "equality"                 # Equalizing wisdom
    DISCRIMINATING = "discriminating"     # Discriminating wisdom
    ALL_ACCOMPLISHING = "all_accomplishing"  # All-accomplishing wisdom


# =============================================================================
# DHYANI BUDDHA
# =============================================================================

@dataclass
class DhyaniBuddha:
    """
    A Dhyani Buddha: Basis vector of the psyche.
    
    Maps an Error Mode to its corresponding Rectified State.
    """
    
    family: BuddhaFamily
    direction: Direction
    poison: Poison
    wisdom: Wisdom
    
    # Properties
    color: str
    element: str
    aggregate: str  # Skandha
    seed_syllable: str
    
    # Operator type
    operator: str
    
    def get_basis_vector(self, dimension: int = 5) -> np.ndarray:
        """Get the basis vector for this Buddha family."""
        idx = list(BuddhaFamily).index(self.family)
        vec = np.zeros(dimension)
        vec[idx] = 1.0
        return vec
    
    def transmute_poison(self, poison_intensity: float) -> Tuple[Wisdom, float]:
        """
        Transmute poison to wisdom.
        
        Returns (wisdom_type, wisdom_intensity).
        """
        # Unitary transformation preserves magnitude
        wisdom_intensity = poison_intensity
        return self.wisdom, wisdom_intensity


def create_five_buddhas() -> Dict[BuddhaFamily, DhyaniBuddha]:
    """Create the Five Dhyani Buddhas."""
    return {
        BuddhaFamily.VAIROCANA: DhyaniBuddha(
            family=BuddhaFamily.VAIROCANA,
            direction=Direction.CENTER,
            poison=Poison.IGNORANCE,
            wisdom=Wisdom.DHARMADHATU,
            color="white",
            element="space",
            aggregate="consciousness",
            seed_syllable="OM",
            operator="CLR"  # Clear
        ),
        BuddhaFamily.AKSHOBHYA: DhyaniBuddha(
            family=BuddhaFamily.AKSHOBHYA,
            direction=Direction.EAST,
            poison=Poison.ANGER,
            wisdom=Wisdom.MIRROR,
            color="blue",
            element="water",
            aggregate="form",
            seed_syllable="HUM",
            operator="RFL"  # Reflect
        ),
        BuddhaFamily.RATNASAMBHAVA: DhyaniBuddha(
            family=BuddhaFamily.RATNASAMBHAVA,
            direction=Direction.SOUTH,
            poison=Poison.PRIDE,
            wisdom=Wisdom.EQUALITY,
            color="yellow",
            element="earth",
            aggregate="feeling",
            seed_syllable="TRAM",
            operator="EQU"  # Equalize
        ),
        BuddhaFamily.AMITABHA: DhyaniBuddha(
            family=BuddhaFamily.AMITABHA,
            direction=Direction.WEST,
            poison=Poison.DESIRE,
            wisdom=Wisdom.DISCRIMINATING,
            color="red",
            element="fire",
            aggregate="perception",
            seed_syllable="HRIH",
            operator="SRT"  # Sort
        ),
        BuddhaFamily.AMOGHASIDDHI: DhyaniBuddha(
            family=BuddhaFamily.AMOGHASIDDHI,
            direction=Direction.NORTH,
            poison=Poison.ENVY,
            wisdom=Wisdom.ALL_ACCOMPLISHING,
            color="green",
            element="wind",
            aggregate="volition",
            seed_syllable="AH",
            operator="EXE"  # Execute
        ),
    }


FIVE_BUDDHAS = create_five_buddhas()


# =============================================================================
# MANDALA SPACE
# =============================================================================

@dataclass
class MandalaPoint:
    """A point in mandala space (polar coordinates)."""
    
    r: float      # Radius (distance from center)
    theta: float  # Angle
    
    def to_cartesian(self) -> Tuple[float, float]:
        """Convert to Cartesian coordinates."""
        x = self.r * np.cos(self.theta)
        y = self.r * np.sin(self.theta)
        return x, y
    
    @classmethod
    def from_cartesian(cls, x: float, y: float) -> 'MandalaPoint':
        """Create from Cartesian coordinates."""
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        return cls(r, theta)
    
    def get_direction(self) -> Direction:
        """Get cardinal direction from angle."""
        if self.r < 0.1:
            return Direction.CENTER
        
        # Normalize theta to [0, 2π]
        t = self.theta % (2 * np.pi)
        
        if t < np.pi/4 or t >= 7*np.pi/4:
            return Direction.EAST
        elif t < 3*np.pi/4:
            return Direction.NORTH
        elif t < 5*np.pi/4:
            return Direction.WEST
        else:
            return Direction.SOUTH


class Mandala:
    """
    The Mandala: State-Space Vector Map.
    
    Polar coordinate system centered on the Null Point (Bindu).
    """
    
    def __init__(self, radius: float = 1.0, dimension: int = 5):
        self.radius = radius
        self.dimension = dimension
        
        # Buddha family vectors
        self.buddhas = FIVE_BUDDHAS
        
        # Current state
        self._state = np.zeros(dimension)
        self._position = MandalaPoint(r=radius, theta=0)
        
        # Entropy tracking
        self._entropy = 1.0  # Start at periphery (high entropy)
    
    def get_entropy_at(self, r: float) -> float:
        """
        Get entropy at radius r.
        
        Entropy decreases toward center.
        """
        return r / self.radius
    
    def move_toward_center(self, energy: float) -> Dict:
        """
        Move toward center (requires energy input).
        
        Implements negative entropy gradient.
        """
        # Energy required proportional to current position
        required = self._position.r * 0.1
        
        if energy < required:
            return {
                "success": False,
                "reason": "Insufficient energy",
                "required": required
            }
        
        # Move inward
        new_r = max(0, self._position.r - energy * 0.5)
        self._position = MandalaPoint(new_r, self._position.theta)
        
        # Update entropy
        self._entropy = self.get_entropy_at(new_r)
        
        return {
            "success": True,
            "new_radius": new_r,
            "entropy": self._entropy,
            "direction": self._position.get_direction().value
        }
    
    def get_buddha_at_position(self) -> DhyaniBuddha:
        """Get the Buddha family at current position."""
        direction = self._position.get_direction()
        
        for buddha in self.buddhas.values():
            if buddha.direction == direction:
                return buddha
        
        return self.buddhas[BuddhaFamily.VAIROCANA]  # Default to center
    
    def project_state(self, state: np.ndarray) -> Dict:
        """
        Project a state onto the mandala basis.
        
        Decomposes into Buddha family components.
        """
        if len(state) != self.dimension:
            state = np.resize(state, self.dimension)
        
        # Normalize
        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm
        
        # Get components
        components = {}
        for i, family in enumerate(BuddhaFamily):
            components[family.value] = float(state[i])
        
        return {
            "components": components,
            "dominant": max(components, key=components.get),
            "entropy": self._entropy
        }
    
    def transmute(self, poison: Poison, intensity: float) -> Dict:
        """
        Transmute a poison to wisdom.
        
        Uses the Buddha lookup table.
        """
        # Find the Buddha for this poison
        for buddha in self.buddhas.values():
            if buddha.poison == poison:
                wisdom, wisdom_intensity = buddha.transmute_poison(intensity)
                return {
                    "buddha": buddha.family.value,
                    "poison": poison.value,
                    "wisdom": wisdom.value,
                    "intensity": wisdom_intensity,
                    "operator": buddha.operator
                }
        
        return {"error": f"No Buddha for poison {poison}"}
    
    def reach_center(self) -> bool:
        """Check if center has been reached."""
        return self._position.r < 0.01
    
    @property
    def position(self) -> MandalaPoint:
        return self._position
    
    @property
    def entropy(self) -> float:
        return self._entropy


# =============================================================================
# FIVE WISDOMS ERROR CORRECTION
# =============================================================================

class FiveWisdomsECC:
    """
    The Five Wisdoms Error Correction Code.
    
    Transmutes high-entropy inputs (Poisons) into
    low-entropy outputs (Wisdoms) via unitary rotation.
    """
    
    def __init__(self):
        self.buddhas = FIVE_BUDDHAS
        
        # Build transformation matrices
        self._build_matrices()
    
    def _build_matrices(self) -> None:
        """Build the unitary transformation matrices."""
        # Each poison→wisdom is a rotation in 5D space
        self._rotation_matrices: Dict[Poison, np.ndarray] = {}
        
        for poison in Poison:
            # Create rotation matrix (simplified - 90 degree rotation)
            idx = list(Poison).index(poison)
            R = np.eye(5)
            # Rotate the poison axis toward the wisdom axis
            R[idx, idx] = 0
            R[idx, (idx + 1) % 5] = 1
            R[(idx + 1) % 5, idx] = -1
            R[(idx + 1) % 5, (idx + 1) % 5] = 0
            
            self._rotation_matrices[poison] = R
    
    def detect_poison(self, state: np.ndarray) -> Tuple[Poison, float]:
        """
        Detect dominant poison in state.
        
        Returns (poison_type, intensity).
        """
        if len(state) != 5:
            state = np.resize(state, 5)
        
        # Find most negative component (poison manifestation)
        min_idx = np.argmin(state)
        intensity = abs(min(0, state[min_idx]))
        
        poison = list(Poison)[min_idx]
        return poison, float(intensity)
    
    def correct_error(self, state: np.ndarray, 
                     poison: Poison) -> Tuple[np.ndarray, Wisdom]:
        """
        Apply error correction for a specific poison.
        
        Rotates the state to transmute poison to wisdom.
        """
        if len(state) != 5:
            state = np.resize(state, 5)
        
        R = self._rotation_matrices[poison]
        corrected = R @ state
        
        wisdom = list(Wisdom)[list(Poison).index(poison)]
        
        return corrected, wisdom
    
    def full_correction(self, state: np.ndarray) -> Dict:
        """
        Apply full error correction cycle.
        
        Detects and corrects all poisons.
        """
        current = state.copy()
        corrections = []
        
        for _ in range(5):  # Maximum 5 corrections
            poison, intensity = self.detect_poison(current)
            
            if intensity < 0.01:
                break
            
            current, wisdom = self.correct_error(current, poison)
            corrections.append({
                "poison": poison.value,
                "wisdom": wisdom.value,
                "intensity": intensity
            })
        
        return {
            "original_state": state.tolist(),
            "corrected_state": current.tolist(),
            "corrections": corrections,
            "n_corrections": len(corrections)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_mandala() -> bool:
    """Validate Tibetan mandala module."""
    
    # Test DhyaniBuddha
    vairocana = FIVE_BUDDHAS[BuddhaFamily.VAIROCANA]
    assert vairocana.direction == Direction.CENTER
    assert vairocana.poison == Poison.IGNORANCE
    assert vairocana.wisdom == Wisdom.DHARMADHATU
    
    vec = vairocana.get_basis_vector()
    assert len(vec) == 5
    assert vec[0] == 1.0
    
    wisdom, intensity = vairocana.transmute_poison(0.5)
    assert wisdom == Wisdom.DHARMADHATU
    assert intensity == 0.5
    
    # Test MandalaPoint
    point = MandalaPoint(r=1.0, theta=0)
    x, y = point.to_cartesian()
    assert abs(x - 1.0) < 0.001
    assert abs(y) < 0.001
    
    assert point.get_direction() == Direction.EAST
    
    center = MandalaPoint(r=0.05, theta=0)
    assert center.get_direction() == Direction.CENTER
    
    # Test Mandala
    mandala = Mandala(radius=1.0)
    
    assert mandala.entropy == 1.0  # Start at periphery
    
    result = mandala.move_toward_center(0.5)
    assert result["success"]
    assert mandala.entropy < 1.0
    
    buddha = mandala.get_buddha_at_position()
    assert buddha is not None
    
    state = np.array([0.5, 0.3, 0.1, 0.05, 0.05])
    proj = mandala.project_state(state)
    assert "components" in proj
    assert "dominant" in proj
    
    trans = mandala.transmute(Poison.ANGER, 0.8)
    assert trans["wisdom"] == Wisdom.MIRROR.value
    
    # Test FiveWisdomsECC
    ecc = FiveWisdomsECC()
    
    # Create a state with poison (negative component)
    poisoned = np.array([0.5, -0.8, 0.3, 0.2, 0.1])
    
    poison, intensity = ecc.detect_poison(poisoned)
    assert poison == Poison.ANGER  # Index 1 (East/Akshobhya)
    assert intensity > 0
    
    corrected, wisdom = ecc.correct_error(poisoned, poison)
    assert len(corrected) == 5
    
    full = ecc.full_correction(poisoned)
    assert "corrections" in full
    
    return True


if __name__ == "__main__":
    print("Validating Tibetan Mandala Module...")
    assert validate_mandala()
    print("✓ Tibetan Mandala Module validated")

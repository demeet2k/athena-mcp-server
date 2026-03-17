"""
ATHENA OS - ROMAN KERNEL: EPICUREAN ENGINE MODULE
==================================================
Atomist Physics and Utility/Pleasure Optimization

THE EPICUREAN ENGINE:
    A materialist physics and utility function that defines a
    stochastic universe and an algorithm for minimizing suffering
    by removing fear and uncontrolled desire.

ATOMIC STATE AND DYNAMICS:
    U = {a_i} for i ∈ I
    
    Each atom a_i has (position, velocity, type)
    
    Dynamics:
    1. Straight-line inertial motion in void
    2. Clinamen (swerve): v(t+Δt) = v(t) + δ(t)
       Small random perturbation enabling collision
    3. Aggregations form macroscopic bodies

UTILITY FUNCTION:
    U(x) = -Pain(x) + Pleasure(x)
    
    Goal: Maximize stable pleasure (ataraxia)
    Method: Remove unnecessary desires and fears

TETRAPHARMAKOS (Four-Part Remedy):
    1. God is not to be feared
    2. Death is not to be worried about
    3. Good is easy to obtain
    4. Evil is easy to endure

DESIRE CLASSIFICATION:
    - Natural & Necessary: Food, shelter, friendship
    - Natural & Unnecessary: Luxury, variety
    - Vain: Fame, power, immortality

SOURCES:
    - Lucretius: De Rerum Natura
    - Epicurus: Letters, Principal Doctrines
    - Philodemus: Herculaneum papyri
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np


# =============================================================================
# ATOMIC PHYSICS ENUMS
# =============================================================================

class AtomType(Enum):
    """Types of atoms (simplified from Epicurean theory)."""
    
    EARTH = "earth"       # Heavy, stable
    WATER = "water"       # Fluid, cohesive
    AIR = "air"           # Light, dispersive
    FIRE = "fire"         # Active, transforming
    SOUL = "soul"         # Ultra-fine, animate


class MotionType(Enum):
    """Types of atomic motion."""
    
    INERTIAL = "inertial"     # Straight-line default
    COLLISION = "collision"   # Impact with other atoms
    CLINAMEN = "clinamen"     # Spontaneous swerve


# =============================================================================
# DESIRE CLASSIFICATION
# =============================================================================

class DesireCategory(Enum):
    """Epicurean classification of desires."""
    
    NATURAL_NECESSARY = "natural_necessary"     # Must be satisfied
    NATURAL_UNNECESSARY = "natural_unnecessary" # Can be satisfied
    VAIN = "vain"                               # Should be eliminated


class FearType(Enum):
    """Types of irrational fears to eliminate."""
    
    GODS = "gods"           # Fear of divine punishment
    DEATH = "death"         # Fear of non-existence
    PAIN = "pain"           # Fear of suffering
    FAILURE = "failure"     # Fear of not achieving goals


# =============================================================================
# ATOMIC STRUCTURES
# =============================================================================

@dataclass
class Atom:
    """
    A single atom in the Epicurean universe.
    
    Properties:
    - Position in void
    - Velocity vector
    - Type (determines mass and behavior)
    """
    
    atom_id: int
    atom_type: AtomType
    
    # Position in 3D void
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    
    # Velocity vector
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    
    # Mass (type-dependent)
    mass: float = 1.0
    
    def kinetic_energy(self) -> float:
        """Calculate kinetic energy."""
        return 0.5 * self.mass * np.dot(self.velocity, self.velocity)
    
    def apply_clinamen(self, magnitude: float = 0.01) -> None:
        """
        Apply the clinamen (swerve).
        
        A small random perturbation that enables free will
        and collision in an otherwise deterministic system.
        """
        swerve = np.random.randn(3) * magnitude
        self.velocity += swerve
    
    def move(self, dt: float = 1.0) -> None:
        """Move atom according to velocity."""
        self.position += self.velocity * dt


@dataclass
class AtomicAggregate:
    """
    An aggregate of atoms forming a macroscopic body.
    
    Living beings, objects, and even souls are aggregates
    that will eventually dissolve.
    """
    
    name: str
    atoms: List[Atom] = field(default_factory=list)
    
    # Aggregate properties
    is_living: bool = False
    has_soul: bool = False
    
    def total_mass(self) -> float:
        """Calculate total mass."""
        return sum(a.mass for a in self.atoms)
    
    def center_of_mass(self) -> np.ndarray:
        """Calculate center of mass."""
        if not self.atoms:
            return np.zeros(3)
        
        total_mass = self.total_mass()
        weighted_pos = sum(a.position * a.mass for a in self.atoms)
        return weighted_pos / total_mass
    
    def add_atom(self, atom: Atom) -> None:
        """Add atom to aggregate."""
        self.atoms.append(atom)
        
        if atom.atom_type == AtomType.SOUL:
            self.has_soul = True
            self.is_living = True
    
    def dissolve(self) -> List[Atom]:
        """
        Dissolve the aggregate (death).
        
        Returns atoms to the void - they will form new aggregates.
        """
        atoms = self.atoms.copy()
        self.atoms = []
        self.is_living = False
        self.has_soul = False
        return atoms


# =============================================================================
# VOID SIMULATION
# =============================================================================

class EpicureanVoid:
    """
    The infinite void containing atoms.
    
    Properties:
    - Infinite extent
    - No resistance to motion
    - Atoms move through it eternally
    """
    
    def __init__(self, size: float = 1000.0):
        self.size = size
        self.atoms: List[Atom] = []
        self.aggregates: List[AtomicAggregate] = []
        self.time = 0.0
    
    def add_atoms(self, n: int, atom_type: AtomType = AtomType.EARTH) -> None:
        """Add atoms to the void."""
        for i in range(n):
            atom = Atom(
                atom_id=len(self.atoms),
                atom_type=atom_type,
                position=np.random.uniform(-self.size/2, self.size/2, 3),
                velocity=np.random.randn(3) * 0.1,
                mass=1.0 if atom_type != AtomType.SOUL else 0.1
            )
            self.atoms.append(atom)
    
    def step(self, dt: float = 1.0, clinamen_prob: float = 0.001) -> None:
        """
        Advance simulation by one time step.
        
        1. Apply clinamen with probability
        2. Move atoms
        3. Handle collisions (simplified)
        """
        for atom in self.atoms:
            # Random swerve
            if np.random.random() < clinamen_prob:
                atom.apply_clinamen()
            
            # Move
            atom.move(dt)
            
            # Wrap around (simulating infinite void)
            atom.position = atom.position % self.size - self.size/2
        
        self.time += dt
    
    def total_kinetic_energy(self) -> float:
        """Calculate total kinetic energy."""
        return sum(a.kinetic_energy() for a in self.atoms)


# =============================================================================
# DESIRE AND PLEASURE SYSTEM
# =============================================================================

@dataclass
class Desire:
    """An Epicurean desire."""
    
    name: str
    description: str
    category: DesireCategory
    intensity: float = 0.5      # 0-1
    satisfied: bool = False
    
    def is_worth_pursuing(self) -> bool:
        """Check if desire should be pursued."""
        if self.category == DesireCategory.VAIN:
            return False
        return True
    
    def satisfaction_value(self) -> float:
        """Value gained from satisfying this desire."""
        if self.category == DesireCategory.NATURAL_NECESSARY:
            return 1.0  # High value
        elif self.category == DesireCategory.NATURAL_UNNECESSARY:
            return 0.3  # Modest value
        else:
            return 0.0  # No true value


@dataclass
class Fear:
    """An irrational fear to be eliminated."""
    
    fear_type: FearType
    intensity: float = 0.5      # 0-1
    eliminated: bool = False
    
    def get_remedy(self) -> str:
        """Get the Epicurean remedy for this fear."""
        remedies = {
            FearType.GODS: "The gods are blessed and immortal; they do not interfere with mortals",
            FearType.DEATH: "Death is nothing to us; when we exist, death is not; when death exists, we are not",
            FearType.PAIN: "Pain, if prolonged, is bearable; if intense, is brief",
            FearType.FAILURE: "What is good is easy to obtain; what is terrible is easy to endure"
        }
        return remedies.get(self.fear_type, "Apply reason to dispel fear")


# =============================================================================
# UTILITY FUNCTION
# =============================================================================

@dataclass
class PleasurePainState:
    """
    The pleasure-pain state of an agent.
    
    U(x) = -Pain(x) + Pleasure(x)
    
    Goal: Maximize stable pleasure (ataraxia)
    """
    
    # Pleasure components
    bodily_pleasure: float = 0.5     # Absence of pain (aponia)
    mental_pleasure: float = 0.5     # Tranquility (ataraxia)
    
    # Pain components
    bodily_pain: float = 0.0
    mental_pain: float = 0.0         # Anxiety, fear
    
    # Desires and fears
    desires: List[Desire] = field(default_factory=list)
    fears: List[Fear] = field(default_factory=list)
    
    def utility(self) -> float:
        """
        Calculate utility.
        
        U = (bodily_pleasure + mental_pleasure) - (bodily_pain + mental_pain)
        """
        pleasure = self.bodily_pleasure + self.mental_pleasure
        pain = self.bodily_pain + self.mental_pain
        return pleasure - pain
    
    def has_ataraxia(self) -> bool:
        """Check if agent has achieved ataraxia (tranquility)."""
        return self.mental_pain < 0.1 and self.mental_pleasure > 0.7
    
    def has_aponia(self) -> bool:
        """Check if agent has achieved aponia (absence of bodily pain)."""
        return self.bodily_pain < 0.1


class UtilityOptimizer:
    """
    Epicurean utility optimization algorithm.
    
    Strategy:
    1. Eliminate vain desires
    2. Satisfy natural necessary desires
    3. Moderately satisfy natural unnecessary desires
    4. Apply tetrapharmakos to eliminate fears
    """
    
    def __init__(self):
        self.tetrapharmakos = [
            "God is not to be feared",
            "Death is not to be worried about",
            "Good is easy to obtain",
            "Evil is easy to endure"
        ]
    
    def classify_desire(self, desire: Desire) -> Dict[str, Any]:
        """Classify and advise on a desire."""
        if desire.category == DesireCategory.VAIN:
            return {
                "desire": desire.name,
                "category": desire.category.value,
                "advice": "Eliminate this desire - it leads only to disturbance",
                "action": "eliminate"
            }
        elif desire.category == DesireCategory.NATURAL_NECESSARY:
            return {
                "desire": desire.name,
                "category": desire.category.value,
                "advice": "Satisfy this desire - it is necessary for life",
                "action": "satisfy"
            }
        else:
            return {
                "desire": desire.name,
                "category": desire.category.value,
                "advice": "Enjoy moderately if available, do not pursue anxiously",
                "action": "moderate"
            }
    
    def apply_tetrapharmakos(self, fear: Fear) -> Dict[str, Any]:
        """Apply four-part remedy to a fear."""
        remedy = fear.get_remedy()
        
        # Reduce fear intensity
        new_intensity = fear.intensity * 0.5
        
        return {
            "fear": fear.fear_type.value,
            "remedy": remedy,
            "previous_intensity": fear.intensity,
            "new_intensity": new_intensity,
            "tetrapharmakos_applied": True
        }
    
    def optimize_state(self, state: PleasurePainState) -> Dict[str, Any]:
        """
        Optimize pleasure-pain state.
        
        Returns actions to maximize utility.
        """
        actions = []
        
        # Process desires
        for desire in state.desires:
            classification = self.classify_desire(desire)
            
            if classification["action"] == "eliminate":
                actions.append({
                    "type": "eliminate_desire",
                    "target": desire.name
                })
            elif classification["action"] == "satisfy" and not desire.satisfied:
                actions.append({
                    "type": "satisfy_desire",
                    "target": desire.name
                })
        
        # Process fears
        for fear in state.fears:
            if fear.intensity > 0.3:
                actions.append({
                    "type": "apply_remedy",
                    "target": fear.fear_type.value
                })
        
        # Calculate projected utility
        projected_utility = state.utility() + len(actions) * 0.1
        
        return {
            "current_utility": state.utility(),
            "projected_utility": projected_utility,
            "actions": actions,
            "has_ataraxia": state.has_ataraxia(),
            "has_aponia": state.has_aponia()
        }


# =============================================================================
# EPICUREAN ENGINE
# =============================================================================

class EpicureanEngine:
    """
    The complete Epicurean computational engine.
    
    Combines:
    - Atomic physics simulation
    - Desire classification
    - Utility optimization
    - Fear elimination
    """
    
    def __init__(self):
        # Physical simulation
        self.void = EpicureanVoid()
        self.void.add_atoms(100, AtomType.EARTH)
        self.void.add_atoms(50, AtomType.WATER)
        self.void.add_atoms(30, AtomType.AIR)
        self.void.add_atoms(20, AtomType.FIRE)
        
        # Agent state
        self.agent_state = PleasurePainState()
        self._initialize_desires()
        self._initialize_fears()
        
        # Optimizer
        self.optimizer = UtilityOptimizer()
    
    def _initialize_desires(self) -> None:
        """Initialize standard desires."""
        self.agent_state.desires = [
            Desire("food", "Nourishment", DesireCategory.NATURAL_NECESSARY),
            Desire("shelter", "Protection from elements", DesireCategory.NATURAL_NECESSARY),
            Desire("friendship", "Companionship", DesireCategory.NATURAL_NECESSARY),
            Desire("luxury_food", "Fine dining", DesireCategory.NATURAL_UNNECESSARY),
            Desire("fame", "Public recognition", DesireCategory.VAIN),
            Desire("power", "Political authority", DesireCategory.VAIN),
            Desire("immortality", "Eternal life", DesireCategory.VAIN),
        ]
    
    def _initialize_fears(self) -> None:
        """Initialize standard fears."""
        self.agent_state.fears = [
            Fear(FearType.GODS, 0.5),
            Fear(FearType.DEATH, 0.7),
            Fear(FearType.PAIN, 0.4),
            Fear(FearType.FAILURE, 0.3),
        ]
    
    def simulate_physics(self, steps: int = 10) -> Dict[str, Any]:
        """Run physical simulation."""
        initial_energy = self.void.total_kinetic_energy()
        
        for _ in range(steps):
            self.void.step()
        
        return {
            "steps": steps,
            "time": self.void.time,
            "atoms": len(self.void.atoms),
            "initial_energy": initial_energy,
            "final_energy": self.void.total_kinetic_energy()
        }
    
    def process_desire(self, desire_name: str) -> Dict[str, Any]:
        """Process a specific desire."""
        desire = next(
            (d for d in self.agent_state.desires if d.name == desire_name),
            None
        )
        
        if not desire:
            return {"error": f"Desire '{desire_name}' not found"}
        
        result = self.optimizer.classify_desire(desire)
        
        # Apply recommendation
        if result["action"] == "eliminate":
            desire.intensity *= 0.5
            self.agent_state.mental_pleasure += 0.1
        elif result["action"] == "satisfy":
            desire.satisfied = True
            self.agent_state.bodily_pleasure += desire.satisfaction_value()
        
        return result
    
    def process_fear(self, fear_type: FearType) -> Dict[str, Any]:
        """Process and reduce a fear."""
        fear = next(
            (f for f in self.agent_state.fears if f.fear_type == fear_type),
            None
        )
        
        if not fear:
            return {"error": f"Fear '{fear_type}' not found"}
        
        result = self.optimizer.apply_tetrapharmakos(fear)
        
        # Apply remedy
        fear.intensity = result["new_intensity"]
        self.agent_state.mental_pain -= 0.1
        self.agent_state.mental_pleasure += 0.05
        
        if fear.intensity < 0.1:
            fear.eliminated = True
        
        return result
    
    def optimize(self) -> Dict[str, Any]:
        """Run full optimization cycle."""
        return self.optimizer.optimize_state(self.agent_state)
    
    def meditate_on_death(self) -> Dict[str, Any]:
        """
        Meditate on death (Epicurean exercise).
        
        "Death is nothing to us" - practicing this removes
        the greatest source of anxiety.
        """
        death_fear = next(
            (f for f in self.agent_state.fears if f.fear_type == FearType.DEATH),
            None
        )
        
        meditation = {
            "teaching": "Where death is, I am not. Where I am, death is not.",
            "reasoning": [
                "We are aggregates of atoms that will dissolve",
                "After dissolution, there is no 'I' to experience anything",
                "Therefore death cannot harm us",
                "Fear of death is irrational"
            ],
            "practice": "Contemplate the brevity of life to appreciate present pleasures"
        }
        
        if death_fear:
            death_fear.intensity *= 0.7
            meditation["fear_reduced"] = True
            self.agent_state.mental_pleasure += 0.1
        
        return meditation
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        return {
            "physics": {
                "atoms": len(self.void.atoms),
                "time": self.void.time,
                "energy": self.void.total_kinetic_energy()
            },
            "utility": self.agent_state.utility(),
            "ataraxia": self.agent_state.has_ataraxia(),
            "aponia": self.agent_state.has_aponia(),
            "desires": {
                "total": len(self.agent_state.desires),
                "satisfied": sum(1 for d in self.agent_state.desires if d.satisfied),
                "vain": sum(1 for d in self.agent_state.desires if d.category == DesireCategory.VAIN)
            },
            "fears": {
                "total": len(self.agent_state.fears),
                "eliminated": sum(1 for f in self.agent_state.fears if f.eliminated),
                "max_intensity": max((f.intensity for f in self.agent_state.fears), default=0)
            }
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_epicurean_engine() -> bool:
    """Validate epicurean engine module."""
    
    # Test atoms
    atom = Atom(1, AtomType.EARTH)
    atom.velocity = np.array([1.0, 0.0, 0.0])
    initial_pos = atom.position.copy()
    atom.move(1.0)
    assert not np.array_equal(atom.position, initial_pos)
    
    # Test clinamen
    atom.apply_clinamen()
    assert atom.velocity[1] != 0 or atom.velocity[2] != 0  # Usually true
    
    # Test aggregate
    agg = AtomicAggregate("test_body")
    agg.add_atom(Atom(1, AtomType.EARTH))
    agg.add_atom(Atom(2, AtomType.SOUL))
    assert agg.is_living
    assert agg.has_soul
    
    atoms = agg.dissolve()
    assert len(atoms) == 2
    assert not agg.is_living
    
    # Test void
    void = EpicureanVoid(100)
    void.add_atoms(10)
    void.step()
    assert void.time > 0
    
    # Test desire
    desire = Desire("fame", "Want fame", DesireCategory.VAIN)
    assert not desire.is_worth_pursuing()
    
    desire2 = Desire("food", "Need food", DesireCategory.NATURAL_NECESSARY)
    assert desire2.is_worth_pursuing()
    
    # Test fear
    fear = Fear(FearType.DEATH, 0.8)
    remedy = fear.get_remedy()
    assert "nothing to us" in remedy
    
    # Test utility
    state = PleasurePainState(
        bodily_pleasure=0.8,
        mental_pleasure=0.9,
        bodily_pain=0.1,
        mental_pain=0.1
    )
    assert state.utility() > 0
    assert state.has_ataraxia()
    
    # Test optimizer
    optimizer = UtilityOptimizer()
    result = optimizer.classify_desire(desire)
    assert result["action"] == "eliminate"
    
    # Test engine
    engine = EpicureanEngine()
    status = engine.get_status()
    assert "utility" in status
    
    result = engine.meditate_on_death()
    assert "teaching" in result
    
    return True


if __name__ == "__main__":
    print("Validating Epicurean Engine Module...")
    assert validate_epicurean_engine()
    print("✓ Epicurean Engine Module validated")
    
    # Demo
    print("\n--- Epicurean Engine Demo ---")
    engine = EpicureanEngine()
    
    print("\nInitial Status:")
    status = engine.get_status()
    print(f"  Utility: {status['utility']:.3f}")
    print(f"  Ataraxia: {status['ataraxia']}")
    print(f"  Vain desires: {status['desires']['vain']}")
    
    # Process vain desires
    print("\nEliminating vain desires...")
    engine.process_desire("fame")
    engine.process_desire("power")
    engine.process_desire("immortality")
    
    # Reduce fears
    print("Applying tetrapharmakos...")
    engine.process_fear(FearType.DEATH)
    engine.process_fear(FearType.GODS)
    
    # Meditate
    engine.meditate_on_death()
    
    print("\nAfter Epicurean practice:")
    status = engine.get_status()
    print(f"  Utility: {status['utility']:.3f}")
    print(f"  Ataraxia: {status['ataraxia']}")
    print(f"  Max fear intensity: {status['fears']['max_intensity']:.3f}")

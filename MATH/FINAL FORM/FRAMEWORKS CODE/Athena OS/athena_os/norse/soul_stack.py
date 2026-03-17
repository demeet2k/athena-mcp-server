"""
ATHENA OS - NORSE: SOUL STACK MODULE
=====================================
The Composite Agent Architecture (Lic + Hamr + Hugr + Fylgja)

THE NORSE INDIVIDUAL IS NOT MONOLITHIC:
    It is a Composite Agent with four distinct, separable
    software modules running on biological hardware.

THE SOUL STACK:

1. LIC (Hardware):
   Physical body, I/O interface
   Status: Volatile, subject to entropic decay

2. HAMR (Shape/Interface):
   External appearance, User Interface
   Properties: Mutable (shapeshifting possible)
   Function: Collision boundaries in simulation

3. HUGR (Processor/Mind):
   Cognitive core, logic and intent
   Function: Active thread of consciousness
   Capability: Can detach for remote operations (astral)
   Constraint: Must return before wake signal

4. FYLGJA (Daemon/Pattern):
   Semi-autonomous background process
   Nature: Animal totem reflecting True Nature
   Function: Predictive algorithm (runs ahead in timeline)
   Inheritance: Passed down lineages (Clan Totem)

OPERATIONS:
    - Shapeshifting: Modify Hamr at runtime
    - Astral Travel: Detach Hugr from Lic
    - Premonition: Receive Fylgja warnings
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np


# =============================================================================
# SOUL COMPONENT TYPES
# =============================================================================

class SoulComponentType(Enum):
    """Types of soul components."""
    
    LIC = "lic"           # Hardware/Body
    HAMR = "hamr"         # Shape/Interface
    HUGR = "hugr"         # Mind/Processor
    FYLGJA = "fylgja"     # Daemon/Pattern


class HamrForm(Enum):
    """Available Hamr forms for shapeshifting."""
    
    HUMAN = "human"
    BEAR = "bear"
    WOLF = "wolf"
    RAVEN = "raven"
    SERPENT = "serpent"
    EAGLE = "eagle"
    FISH = "fish"
    
    @property
    def attributes(self) -> Dict[str, float]:
        attrs = {
            HamrForm.HUMAN: {"strength": 1.0, "speed": 1.0, "perception": 1.0, "stealth": 0.5},
            HamrForm.BEAR: {"strength": 2.0, "speed": 0.7, "perception": 0.8, "stealth": 0.3},
            HamrForm.WOLF: {"strength": 1.5, "speed": 1.5, "perception": 1.5, "stealth": 0.8},
            HamrForm.RAVEN: {"strength": 0.2, "speed": 2.0, "perception": 2.0, "stealth": 1.0},
            HamrForm.SERPENT: {"strength": 0.5, "speed": 0.8, "perception": 1.2, "stealth": 1.5},
            HamrForm.EAGLE: {"strength": 0.4, "speed": 2.5, "perception": 3.0, "stealth": 0.7},
            HamrForm.FISH: {"strength": 0.3, "speed": 1.5, "perception": 0.5, "stealth": 1.2},
        }
        return attrs[self]


class FylgjaType(Enum):
    """Types of Fylgja (spirit animals)."""
    
    WOLF = "wolf"           # Warrior nature
    BEAR = "bear"           # Berserker nature
    RAVEN = "raven"         # Wisdom seeker
    SERPENT = "serpent"     # Cunning nature
    EAGLE = "eagle"         # Noble/royal
    BOAR = "boar"           # Fertility/protection
    STAG = "stag"           # Nobility
    HORSE = "horse"         # Journey/transition


# =============================================================================
# LIC (HARDWARE/BODY)
# =============================================================================

@dataclass
class Lic:
    """
    Lic: The Hardware/Physical Body.
    
    The I/O interface for the software stack.
    Volatile - subject to rapid entropic decay upon power loss.
    """
    
    # Vital statistics
    vitality: float = 1.0
    age: float = 0.0
    
    # Physical attributes
    strength: float = 1.0
    endurance: float = 1.0
    
    # State
    _alive: bool = True
    _awake: bool = True
    
    def update(self, dt: float) -> None:
        """Update body state over time."""
        self.age += dt
        
        # Natural decay
        if self.age > 50:
            decay = 0.001 * (self.age - 50) * dt
            self.vitality -= decay
        
        # Check death
        if self.vitality <= 0:
            self._alive = False
    
    def damage(self, amount: float) -> None:
        """Apply damage to body."""
        self.vitality -= amount
        if self.vitality <= 0:
            self.vitality = 0
            self._alive = False
    
    def heal(self, amount: float) -> None:
        """Heal the body."""
        if self._alive:
            self.vitality = min(1.0, self.vitality + amount)
    
    def sleep(self) -> None:
        """Enter sleep state."""
        self._awake = False
    
    def wake(self) -> None:
        """Wake from sleep."""
        self._awake = True
    
    @property
    def is_alive(self) -> bool:
        return self._alive
    
    @property
    def is_awake(self) -> bool:
        return self._awake


# =============================================================================
# HAMR (SHAPE/INTERFACE)
# =============================================================================

@dataclass
class Hamr:
    """
    Hamr: The Shape/External Interface.
    
    The User Interface - external appearance.
    Mutable: Can be modified at runtime (shapeshifting).
    """
    
    # Current form
    form: HamrForm = HamrForm.HUMAN
    
    # Modification state
    _original_form: HamrForm = field(init=False)
    _transformation_count: int = 0
    _transformation_energy: float = 1.0
    
    def __post_init__(self):
        self._original_form = self.form
    
    def transform(self, new_form: HamrForm, energy_cost: float = 0.2) -> bool:
        """
        Transform to a new form (shapeshifting).
        
        Requires energy and skill.
        """
        if self._transformation_energy < energy_cost:
            return False
        
        self._transformation_energy -= energy_cost
        self.form = new_form
        self._transformation_count += 1
        
        return True
    
    def revert(self) -> None:
        """Revert to original form."""
        self.form = self._original_form
    
    def get_attributes(self) -> Dict[str, float]:
        """Get current form's attributes."""
        return self.form.attributes.copy()
    
    def recover_energy(self, amount: float) -> None:
        """Recover transformation energy."""
        self._transformation_energy = min(1.0, self._transformation_energy + amount)
    
    @property
    def is_transformed(self) -> bool:
        return self.form != self._original_form


# =============================================================================
# HUGR (MIND/PROCESSOR)
# =============================================================================

@dataclass
class Hugr:
    """
    Hugr: The Mind/Processor.
    
    Cognitive core handling logic, intent, decision-making.
    The active thread of consciousness.
    Can detach from Lic during sleep/trance for remote operations.
    """
    
    # Cognitive state
    clarity: float = 1.0
    willpower: float = 1.0
    
    # Memory
    memories: List[str] = field(default_factory=list)
    
    # Location state
    _attached_to_lic: bool = True
    _remote_location: Optional[str] = None
    _time_detached: float = 0.0
    
    # Maximum safe detachment time
    max_detach_time: float = 8.0  # Hours of sleep
    
    def detach(self, destination: str) -> bool:
        """
        Detach from Lic for astral travel.
        
        Can only detach if body is asleep.
        """
        if not self._attached_to_lic:
            return False  # Already detached
        
        self._attached_to_lic = False
        self._remote_location = destination
        self._time_detached = 0.0
        
        return True
    
    def travel(self, new_location: str, dt: float) -> bool:
        """
        Travel while detached.
        
        Returns False if exceeded safe time.
        """
        if self._attached_to_lic:
            return False
        
        self._remote_location = new_location
        self._time_detached += dt
        
        # Check for danger
        if self._time_detached > self.max_detach_time:
            # Risk of not returning
            self.clarity -= 0.1
            return False
        
        return True
    
    def reattach(self) -> bool:
        """
        Reattach to Lic.
        
        Critical: Must return before wake signal.
        """
        if self._attached_to_lic:
            return True  # Already attached
        
        self._attached_to_lic = True
        self._remote_location = None
        
        # Fatigue from journey
        self.willpower -= self._time_detached * 0.05
        self._time_detached = 0.0
        
        return True
    
    def think(self, topic: str) -> str:
        """Process a thought."""
        # Record in memory
        self.memories.append(topic)
        
        # Keep memory bounded
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
        
        return f"Contemplated: {topic}"
    
    def decide(self, options: List[str]) -> Optional[str]:
        """Make a decision from options."""
        if not options:
            return None
        
        # Weighted by willpower
        if self.willpower > np.random.random():
            return options[0]  # Choose first (intended)
        else:
            return np.random.choice(options)  # Random (weak will)
    
    def rest(self, hours: float) -> None:
        """Rest to recover cognitive resources."""
        self.clarity = min(1.0, self.clarity + hours * 0.1)
        self.willpower = min(1.0, self.willpower + hours * 0.05)
    
    @property
    def is_attached(self) -> bool:
        return self._attached_to_lic
    
    @property
    def location(self) -> str:
        if self._attached_to_lic:
            return "body"
        return self._remote_location or "void"


# =============================================================================
# FYLGJA (DAEMON/PATTERN)
# =============================================================================

@dataclass
class Fylgja:
    """
    Fylgja: The Daemon/Pattern.
    
    Semi-autonomous background process attached to user.
    Appears as animal totem reflecting True Nature.
    Runs ahead in timeline to detect fatal errors (premonition).
    Inheritable down lineages (Clan Totem).
    """
    
    # Identity
    animal: FylgjaType
    lineage: str = "unknown"
    
    # State
    visibility: float = 0.0  # 0 = hidden, 1 = manifested
    warning_active: bool = False
    
    # Prediction buffer
    _predictions: List[Dict] = field(default_factory=list)
    _danger_level: float = 0.0
    
    def scan_future(self, current_state: Dict, 
                   horizon: float = 1.0) -> Dict:
        """
        Scan ahead in timeline.
        
        The Fylgja processes faster than Hugr,
        detecting errors before they occur.
        """
        # Simulate scanning (simplified)
        danger_factors = []
        
        # Check for various threats
        if current_state.get("vitality", 1.0) < 0.3:
            danger_factors.append(("health", 0.7))
        
        if current_state.get("enemies_near", 0) > 0:
            danger_factors.append(("combat", 0.5))
        
        if current_state.get("path_dangerous", False):
            danger_factors.append(("journey", 0.6))
        
        # Compute danger level
        if danger_factors:
            self._danger_level = max(d[1] for d in danger_factors)
            self.warning_active = self._danger_level > 0.5
        else:
            self._danger_level = 0.0
            self.warning_active = False
        
        prediction = {
            "horizon": horizon,
            "danger_level": self._danger_level,
            "threats": danger_factors,
            "warning": self.warning_active
        }
        
        self._predictions.append(prediction)
        if len(self._predictions) > 10:
            self._predictions = self._predictions[-10:]
        
        return prediction
    
    def manifest(self) -> None:
        """Make Fylgja visible (usually a bad sign)."""
        self.visibility = 1.0
    
    def hide(self) -> None:
        """Return Fylgja to hidden state."""
        self.visibility = 0.0
    
    def send_warning(self) -> Optional[str]:
        """Send warning to host if danger detected."""
        if self.warning_active and self._predictions:
            latest = self._predictions[-1]
            threats = latest.get("threats", [])
            if threats:
                return f"Warning: {threats[0][0]} danger detected"
        return None
    
    def inherit(self, child_name: str) -> 'Fylgja':
        """
        Create inherited Fylgja for offspring.
        
        Clan totem passes down lineages.
        """
        return Fylgja(
            animal=self.animal,
            lineage=f"{self.lineage} → {child_name}"
        )
    
    @property
    def true_nature(self) -> str:
        """Get the true nature revealed by the Fylgja."""
        natures = {
            FylgjaType.WOLF: "warrior",
            FylgjaType.BEAR: "berserker",
            FylgjaType.RAVEN: "seeker",
            FylgjaType.SERPENT: "trickster",
            FylgjaType.EAGLE: "noble",
            FylgjaType.BOAR: "protector",
            FylgjaType.STAG: "leader",
            FylgjaType.HORSE: "traveler"
        }
        return natures.get(self.animal, "unknown")


# =============================================================================
# COMPLETE SOUL STACK
# =============================================================================

class NorseSoul:
    """
    Complete Norse Soul Stack.
    
    Composite agent with four separable modules:
    Lic (body) + Hamr (shape) + Hugr (mind) + Fylgja (daemon)
    """
    
    def __init__(self, name: str, 
                fylgja_type: FylgjaType = FylgjaType.WOLF):
        self.name = name
        
        # Build stack
        self.lic = Lic()
        self.hamr = Hamr()
        self.hugr = Hugr()
        self.fylgja = Fylgja(animal=fylgja_type, lineage=name)
        
        # State
        self._location: str = "Midgard"
    
    def update(self, dt: float) -> Dict:
        """Update all components."""
        events = []
        
        # Update body
        self.lic.update(dt)
        if not self.lic.is_alive:
            events.append("death")
            return {"events": events, "alive": False}
        
        # Rest during sleep
        if not self.lic.is_awake:
            self.hugr.rest(dt)
            self.hamr.recover_energy(dt * 0.1)
        
        # Check Fylgja warnings
        state = self.get_state()
        prediction = self.fylgja.scan_future(state)
        if prediction["warning"]:
            events.append(f"fylgja_warning: {self.fylgja.send_warning()}")
        
        return {
            "events": events,
            "alive": True,
            "location": self._location
        }
    
    def shapeshift(self, form: HamrForm) -> bool:
        """Attempt to shapeshift."""
        return self.hamr.transform(form)
    
    def astral_travel(self, destination: str) -> bool:
        """
        Attempt astral travel.
        
        Requires body to be asleep.
        """
        if self.lic.is_awake:
            return False
        
        return self.hugr.detach(destination)
    
    def return_to_body(self) -> bool:
        """Return from astral travel."""
        success = self.hugr.reattach()
        if success:
            self.lic.wake()
        return success
    
    def sleep(self) -> None:
        """Enter sleep state."""
        self.lic.sleep()
    
    def wake(self) -> bool:
        """
        Wake from sleep.
        
        Critical: Hugr must be attached!
        """
        if not self.hugr.is_attached:
            # Hugr not returned - SYSTEM CRASH
            self.lic.damage(1.0)  # Fatal
            return False
        
        self.lic.wake()
        return True
    
    def get_state(self) -> Dict:
        """Get current state of the soul."""
        return {
            "name": self.name,
            "vitality": self.lic.vitality,
            "alive": self.lic.is_alive,
            "awake": self.lic.is_awake,
            "form": self.hamr.form.value,
            "transformed": self.hamr.is_transformed,
            "mind_location": self.hugr.location,
            "mind_attached": self.hugr.is_attached,
            "fylgja_animal": self.fylgja.animal.value,
            "true_nature": self.fylgja.true_nature,
            "danger_level": self.fylgja._danger_level
        }
    
    def move(self, destination: str) -> None:
        """Move to a new location."""
        self._location = destination
    
    @property
    def is_alive(self) -> bool:
        return self.lic.is_alive
    
    @property
    def location(self) -> str:
        return self._location


# =============================================================================
# BERSERKER MODE
# =============================================================================

class BerserkerState:
    """
    Berserker State: Overclocked agent mode.
    
    Maximum kinetic output at cost of coherence.
    Disables fear/pain subroutines.
    """
    
    def __init__(self, soul: NorseSoul):
        self.soul = soul
        self._active = False
        self._duration = 0.0
        self._max_duration = 10.0  # Minutes
        
        # Saved state
        self._original_strength: float = 1.0
    
    def invoke(self) -> bool:
        """
        Invoke berserker state.
        
        invoke_berserk_state() system call.
        """
        if self._active:
            return False
        
        self._active = True
        self._duration = 0.0
        
        # Save original state
        self._original_strength = self.soul.lic.strength
        
        # Overclock
        self.soul.lic.strength *= 3.0
        
        # Transform to bear (common berserker form)
        self.soul.hamr.transform(HamrForm.BEAR)
        
        return True
    
    def update(self, dt: float) -> Dict:
        """Update berserker state."""
        if not self._active:
            return {"active": False}
        
        self._duration += dt
        
        # Check duration
        if self._duration > self._max_duration:
            return self.exit()
        
        # High entropy - taking damage
        self.soul.lic.damage(0.01 * dt)
        
        return {
            "active": True,
            "duration": self._duration,
            "strength": self.soul.lic.strength
        }
    
    def exit(self) -> Dict:
        """
        Exit berserker state.
        
        High entropic cost (exhaustion).
        """
        self._active = False
        
        # Restore strength
        self.soul.lic.strength = self._original_strength
        
        # Revert form
        self.soul.hamr.revert()
        
        # Exhaustion
        self.soul.lic.vitality -= 0.3
        self.soul.hugr.willpower -= 0.5
        
        return {
            "active": False,
            "exhaustion": True,
            "duration": self._duration
        }
    
    @property
    def is_active(self) -> bool:
        return self._active


# =============================================================================
# VALIDATION
# =============================================================================

def validate_soul_stack() -> bool:
    """Validate Norse soul_stack module."""
    
    # Test Lic
    lic = Lic()
    assert lic.is_alive
    assert lic.is_awake
    
    lic.update(10.0)
    assert lic.vitality <= 1.0
    
    lic.damage(0.5)
    assert lic.vitality < 1.0
    assert lic.is_alive
    
    lic.heal(0.2)
    
    lic.sleep()
    assert not lic.is_awake
    lic.wake()
    assert lic.is_awake
    
    # Test Hamr
    hamr = Hamr()
    assert hamr.form == HamrForm.HUMAN
    assert not hamr.is_transformed
    
    success = hamr.transform(HamrForm.WOLF)
    assert success
    assert hamr.is_transformed
    
    attrs = hamr.get_attributes()
    assert "strength" in attrs
    assert attrs["speed"] > 1.0  # Wolf is fast
    
    hamr.revert()
    assert not hamr.is_transformed
    
    # Test Hugr
    hugr = Hugr()
    assert hugr.is_attached
    
    result = hugr.think("test thought")
    assert len(hugr.memories) == 1
    
    decision = hugr.decide(["A", "B", "C"])
    assert decision in ["A", "B", "C"]
    
    # Test detachment
    success = hugr.detach("Asgard")
    assert success
    assert not hugr.is_attached
    assert hugr.location == "Asgard"
    
    hugr.travel("Vanaheim", 2.0)
    assert hugr.location == "Vanaheim"
    
    hugr.reattach()
    assert hugr.is_attached
    
    # Test Fylgja
    fylgja = Fylgja(animal=FylgjaType.WOLF, lineage="TestLine")
    assert fylgja.true_nature == "warrior"
    
    prediction = fylgja.scan_future({"vitality": 0.2})
    assert prediction["danger_level"] > 0
    
    child_fylgja = fylgja.inherit("Child")
    assert child_fylgja.animal == FylgjaType.WOLF
    assert "TestLine" in child_fylgja.lineage
    
    # Test NorseSoul
    soul = NorseSoul("TestViking", FylgjaType.BEAR)
    
    state = soul.get_state()
    assert state["alive"]
    assert state["true_nature"] == "berserker"
    
    # Update
    result = soul.update(1.0)
    assert result["alive"]
    
    # Shapeshift
    success = soul.shapeshift(HamrForm.WOLF)
    assert success
    
    # Astral travel
    soul.sleep()
    success = soul.astral_travel("Asgard")
    assert success
    assert not soul.hugr.is_attached
    
    # Return and wake
    success = soul.return_to_body()
    assert success
    assert soul.lic.is_awake
    
    # Test failed wake (hugr not returned)
    soul2 = NorseSoul("TestViking2")
    soul2.sleep()
    soul2.hugr.detach("Hel")
    # Attempt wake without hugr
    success = soul2.wake()
    assert not success
    assert not soul2.is_alive  # Fatal error
    
    # Test Berserker
    soul3 = NorseSoul("Berserker")
    berserk = BerserkerState(soul3)
    
    success = berserk.invoke()
    assert success
    assert berserk.is_active
    assert soul3.hamr.form == HamrForm.BEAR
    
    result = berserk.update(1.0)
    assert result["active"]
    
    result = berserk.exit()
    assert not berserk.is_active
    assert result["exhaustion"]
    
    return True


if __name__ == "__main__":
    print("Validating Norse Soul Stack Module...")
    assert validate_soul_stack()
    print("✓ Norse Soul Stack Module validated")

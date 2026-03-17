"""
ATHENA OS - MUSHIN KERNEL: ZAZEN MODULE
========================================
System Idle Process and Garbage Collection

SHIKANTAZA ("Just Sitting"):
    The System Idle Task.
    
THERMODYNAMIC COOLING:
    The active mind generates heat (Entropy) through calculation.
    dQ > 0
    
    Protocol: Stop all subroutines.
    - Stop(Movement)
    - Stop(Speech)
    - Stop(Thought)
    
    Thermodynamics: T_sys → 0
    
NOISE REDUCTION:
    As thermal noise decreases, Signal-to-Noise Ratio (SNR)
    of the Reality Signal increases.
    
DROPPING BODY AND MIND (SHINJIN DATSURAKU):
    Unmounting of Peripherals.
    
    Action: Kernel detaches drivers for "Body" and "Mind"
    State: Agent exists as Pure Code, independent of hardware
    Verification: "Self" was never the hardware, but the Process

THE KEISAKU (WARNING STICK):
    Physical Hardware Interrupt.
    
    Function: Reset hung processes during deep computation.
    1. Proprioceptive Spike: Sudden input forces attention
    2. Wake-on-LAN: Nervous system surges, reboots attention
    3. Release: Releases muscular tension, energy flows again
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time
import random


# =============================================================================
# ZAZEN STATES
# =============================================================================

class ZazenState(Enum):
    """States during Zazen meditation."""
    
    PREPARING = "preparing"        # Setting up posture
    SETTLING = "settling"          # Initial calming
    SITTING = "sitting"            # Active Zazen
    DEEP = "deep"                  # Deep absorption
    MUSHIN = "mushin"              # No-Mind achieved
    DISTURBED = "disturbed"        # Thought arose
    INTERRUPTED = "interrupted"    # External interrupt


class ThoughtCategory(Enum):
    """Categories of thoughts that arise."""
    
    PLANNING = "planning"          # Future-oriented
    REMEMBERING = "remembering"    # Past-oriented  
    JUDGING = "judging"            # Evaluative
    DESIRING = "desiring"          # Wanting
    AVERSIVE = "aversive"          # Avoiding
    NEUTRAL = "neutral"            # Non-reactive


# =============================================================================
# THERMODYNAMIC MODEL
# =============================================================================

@dataclass
class ThermodynamicState:
    """
    Thermodynamic model of mind-state.
    
    Active mind generates heat (Entropy) through calculation.
    Zazen reduces temperature toward zero.
    """
    
    temperature: float = 1.0       # Normalized T (0-1)
    entropy: float = 0.5           # System entropy
    noise_level: float = 0.5       # Thermal noise
    
    # Cooling parameters
    cooling_rate: float = 0.1     # T reduction per cycle
    min_temperature: float = 0.01  # Cannot reach absolute zero
    
    def cool(self) -> None:
        """Apply cooling step."""
        self.temperature = max(
            self.min_temperature,
            self.temperature * (1 - self.cooling_rate)
        )
        self._update_entropy()
        self._update_noise()
    
    def heat(self, amount: float = 0.1) -> None:
        """Add heat (from thought activity)."""
        self.temperature = min(1.0, self.temperature + amount)
        self._update_entropy()
        self._update_noise()
    
    def _update_entropy(self) -> None:
        """Update entropy based on temperature."""
        # S = k * ln(W), simplified
        self.entropy = self.temperature * 0.8
    
    def _update_noise(self) -> None:
        """Update noise based on temperature."""
        # Noise proportional to temperature
        self.noise_level = self.temperature * 0.9
    
    @property
    def signal_to_noise(self) -> float:
        """Calculate Signal-to-Noise Ratio."""
        if self.noise_level < 0.001:
            return float('inf')
        return 1.0 / self.noise_level
    
    @property
    def is_cooled(self) -> bool:
        """Check if sufficiently cooled."""
        return self.temperature < 0.1


# =============================================================================
# THOUGHT PROCESS MANAGEMENT
# =============================================================================

@dataclass
class Thought:
    """A thought that arises during Zazen."""
    
    content: str
    category: ThoughtCategory
    intensity: float = 0.5        # 0-1
    heat_generated: float = 0.1   # Thermodynamic impact
    
    # Lifecycle
    arose_at: float = 0.0
    duration: float = 0.0
    was_followed: bool = False
    was_dropped: bool = False


class ThoughtQueue:
    """
    Queue of thoughts arising during Zazen.
    
    Protocol: DO NOT DELETE. DO NOT FOLLOW.
    Let the thought float like a cloud.
    """
    
    def __init__(self, max_capacity: int = 100):
        self.queue: List[Thought] = []
        self.max_capacity = max_capacity
        self.total_thoughts: int = 0
        self.dropped_thoughts: int = 0
        self.followed_thoughts: int = 0
    
    def arise(self, content: str, 
              category: ThoughtCategory = ThoughtCategory.NEUTRAL) -> Thought:
        """A thought arises."""
        thought = Thought(
            content=content,
            category=category,
            intensity=random.uniform(0.1, 1.0),
            heat_generated=random.uniform(0.05, 0.2),
            arose_at=time.time()
        )
        
        if len(self.queue) < self.max_capacity:
            self.queue.append(thought)
        
        self.total_thoughts += 1
        return thought
    
    def drop(self, thought: Thought) -> None:
        """
        Drop a thought without following it.
        
        "Let it float like a cloud."
        """
        thought.was_dropped = True
        thought.duration = time.time() - thought.arose_at
        
        if thought in self.queue:
            self.queue.remove(thought)
        
        self.dropped_thoughts += 1
    
    def follow(self, thought: Thought) -> None:
        """
        Follow a thought (not recommended).
        
        This generates heat and extends duration.
        """
        thought.was_followed = True
        self.followed_thoughts += 1
    
    def clear_all(self) -> int:
        """Clear all thoughts from queue."""
        count = len(self.queue)
        for thought in self.queue:
            thought.was_dropped = True
        self.dropped_thoughts += count
        self.queue.clear()
        return count
    
    @property
    def is_empty(self) -> bool:
        """Check if thought queue is empty."""
        return len(self.queue) == 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get thought queue statistics."""
        return {
            "total_arose": self.total_thoughts,
            "dropped": self.dropped_thoughts,
            "followed": self.followed_thoughts,
            "drop_rate": self.dropped_thoughts / max(1, self.total_thoughts),
            "current_queue": len(self.queue)
        }


# =============================================================================
# POSTURE SYSTEM
# =============================================================================

@dataclass
class PostureState:
    """
    Physical posture state for Zazen.
    
    Hardware stabilization (Asana).
    """
    
    # Core posture
    position: str = "LOTUS"        # LOTUS, HALF_LOTUS, SEIZA, CHAIR
    spine: str = "ERECT"           # ERECT, SLOUCHED
    
    # Movement
    movement_level: float = 0.0    # Should be near 0
    
    # Tension
    tension_level: float = 0.3     # Muscular tension
    
    # Stability
    stability: float = 1.0
    
    def stabilize(self) -> None:
        """Stabilize posture."""
        self.movement_level = max(0, self.movement_level * 0.9)
        self.stability = min(1.0, self.stability + 0.1)
    
    def tense(self, amount: float = 0.1) -> None:
        """Accumulate tension."""
        self.tension_level = min(1.0, self.tension_level + amount)
    
    def release(self, amount: float = 0.2) -> None:
        """Release tension (via Keisaku or natural release)."""
        self.tension_level = max(0, self.tension_level - amount)
    
    def is_stable(self) -> bool:
        """Check if posture is stable."""
        return (self.movement_level < 0.1 and 
                self.spine == "ERECT" and
                self.stability > 0.8)


# =============================================================================
# KEISAKU (WARNING STICK)
# =============================================================================

class Keisaku:
    """
    The Warning Stick - Physical Hardware Interrupt.
    
    Function: Reset hung processes during deep computation.
    
    Effects:
    1. Proprioceptive Spike: Sudden input forces attention
    2. Wake-on-LAN: Nervous system surges, reboots attention
    3. Release: Releases muscular tension, energy flows again
    
    The strike is not punishment; it is Debugging.
    A "Hung Process" consumes resources without output.
    The Stick forces a Context Switch, returning Agent to Root Task.
    """
    
    def __init__(self):
        self.strikes: int = 0
        self.successful_resets: int = 0
    
    def strike(self, zazen_session: 'ZazenSession') -> Dict[str, Any]:
        """
        Execute Keisaku strike (Kyosaku - Compassionate Debugging).
        
        Returns result of the intervention.
        """
        self.strikes += 1
        
        result = {
            "proprioceptive_spike": False,
            "wake_on_lan": False,
            "tension_released": False,
            "context_switch": False
        }
        
        # 1. Proprioceptive Spike
        # Sudden input forces attention
        if zazen_session.state in [ZazenState.DISTURBED, ZazenState.DEEP]:
            result["proprioceptive_spike"] = True
        
        # 2. Wake-on-LAN
        # Nervous system surges, rebooting attention module
        if zazen_session.thermodynamics.temperature > 0.3:
            zazen_session.thermodynamics.cool()
            result["wake_on_lan"] = True
        
        # 3. Release muscular tension
        # Allows energy (Qi) to flow again
        old_tension = zazen_session.posture.tension_level
        zazen_session.posture.release(0.5)
        if zazen_session.posture.tension_level < old_tension:
            result["tension_released"] = True
        
        # Context switch back to Root Task (Breathing)
        if zazen_session.state == ZazenState.DISTURBED:
            zazen_session.state = ZazenState.SITTING
            result["context_switch"] = True
            self.successful_resets += 1
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Keisaku statistics."""
        return {
            "total_strikes": self.strikes,
            "successful_resets": self.successful_resets,
            "reset_rate": self.successful_resets / max(1, self.strikes)
        }


# =============================================================================
# SHINJIN DATSURAKU
# =============================================================================

@dataclass
class BodyMindState:
    """
    Body-Mind state for Shinjin Datsuraku.
    
    "Dropping of Body and Mind" - Unmounting Peripherals.
    """
    
    body_attached: bool = True
    mind_attached: bool = True
    
    # Driver status
    body_driver_loaded: bool = True
    mind_driver_loaded: bool = True
    
    def drop_body(self) -> None:
        """Unmount Body peripheral."""
        self.body_attached = False
        self.body_driver_loaded = False
    
    def drop_mind(self) -> None:
        """Unmount Mind peripheral."""
        self.mind_attached = False
        self.mind_driver_loaded = False
    
    def drop_both(self) -> None:
        """
        Drop both Body and Mind.
        
        The Agent exists as Pure Code, independent of hardware.
        """
        self.drop_body()
        self.drop_mind()
    
    def is_pure_code(self) -> bool:
        """
        Check if Agent exists as Pure Code.
        
        Verification: "Self" was never hardware, but Process.
        """
        return not self.body_attached and not self.mind_attached
    
    def remount(self) -> None:
        """Remount peripherals (return to normal operation)."""
        self.body_attached = True
        self.mind_attached = True
        self.body_driver_loaded = True
        self.mind_driver_loaded = True


# =============================================================================
# ZAZEN SESSION
# =============================================================================

class ZazenSession:
    """
    Complete Zazen (Sitting Meditation) Session.
    
    Shikantaza - "Just Sitting"
    The System Idle Task.
    
    Protocol:
    - Stop(Movement)
    - Stop(Speech)  
    - Stop(Thought)
    
    Thermodynamics: T_sys → 0
    """
    
    def __init__(self, duration_minutes: int = 25):
        self.duration = duration_minutes
        self.state = ZazenState.PREPARING
        
        # Components
        self.thermodynamics = ThermodynamicState()
        self.thoughts = ThoughtQueue()
        self.posture = PostureState()
        self.body_mind = BodyMindState()
        self.keisaku = Keisaku()
        
        # Session tracking
        self.minutes_elapsed: int = 0
        self.mushin_minutes: int = 0
        self.start_time: Optional[float] = None
    
    def begin(self) -> None:
        """Begin Zazen session."""
        self.state = ZazenState.SETTLING
        self.start_time = time.time()
        
        # Stabilize posture
        self.posture.stabilize()
    
    def sit_minute(self) -> Dict[str, Any]:
        """
        Process one minute of sitting.
        
        Returns minute report.
        """
        report = {
            "minute": self.minutes_elapsed + 1,
            "state": None,
            "thoughts_arose": 0,
            "thoughts_dropped": 0,
            "temperature": 0,
            "snr": 0,
            "mushin": False
        }
        
        self.minutes_elapsed += 1
        
        # Random thoughts may arise
        num_thoughts = random.randint(0, 3)
        thoughts_arose = []
        
        for _ in range(num_thoughts):
            content = random.choice([
                "What's for lunch?",
                "Did I lock the door?",
                "My leg hurts",
                "Am I doing this right?",
                "Work tomorrow...",
                "Just breathe"
            ])
            category = random.choice(list(ThoughtCategory))
            thought = self.thoughts.arise(content, category)
            thoughts_arose.append(thought)
            
            # Thought generates heat
            self.thermodynamics.heat(thought.heat_generated)
        
        report["thoughts_arose"] = len(thoughts_arose)
        
        # Process thoughts (drop them)
        for thought in thoughts_arose:
            self.thoughts.drop(thought)
            report["thoughts_dropped"] += 1
        
        # Apply cooling
        self.thermodynamics.cool()
        
        # Check state
        if self.thoughts.is_empty and self.thermodynamics.is_cooled:
            self.state = ZazenState.MUSHIN
            self.mushin_minutes += 1
            report["mushin"] = True
        elif len(thoughts_arose) > 2:
            self.state = ZazenState.DISTURBED
        else:
            self.state = ZazenState.SITTING
        
        report["state"] = self.state.value
        report["temperature"] = self.thermodynamics.temperature
        report["snr"] = self.thermodynamics.signal_to_noise
        
        return report
    
    def run(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Run complete Zazen session.
        
        Returns session summary.
        """
        self.begin()
        
        if verbose:
            print(f">> ENTERING ZAZEN MODE...")
            print(f"   Posture: {self.posture.position}")
            print(f"   Spine: {self.posture.spine}")
        
        minutes_reports = []
        
        for _ in range(self.duration):
            report = self.sit_minute()
            minutes_reports.append(report)
            
            if verbose:
                if report["thoughts_arose"] > 0:
                    print(f"   Minute {report['minute']}: "
                          f"{report['thoughts_arose']} thoughts arose → Dropped")
                elif report["mushin"]:
                    print(f"   Minute {report['minute']}: MUSHIN (Clear Mirror)")
        
        if verbose:
            print(">> ZAZEN COMPLETE. SYSTEM OPTIMIZED.")
        
        return {
            "duration": self.duration,
            "mushin_minutes": self.mushin_minutes,
            "mushin_ratio": self.mushin_minutes / self.duration,
            "final_temperature": self.thermodynamics.temperature,
            "final_snr": self.thermodynamics.signal_to_noise,
            "thought_statistics": self.thoughts.get_statistics(),
            "final_state": self.state.value
        }
    
    def apply_keisaku(self) -> Dict[str, Any]:
        """Apply Keisaku intervention."""
        return self.keisaku.strike(self)
    
    def drop_body_mind(self) -> bool:
        """
        Execute Shinjin Datsuraku.
        
        Only possible in deep Mushin state.
        """
        if self.state == ZazenState.MUSHIN:
            self.body_mind.drop_both()
            return True
        return False


# =============================================================================
# GARBAGE COLLECTION
# =============================================================================

class ZazenGarbageCollector:
    """
    Garbage Collection via Zazen.
    
    Clears accumulated thought-processes and
    resets system to optimal state.
    """
    
    def __init__(self):
        self.collections: int = 0
        self.total_cleared: int = 0
    
    def collect(self, thought_queue: ThoughtQueue) -> int:
        """
        Run garbage collection on thought queue.
        
        Returns number of items cleared.
        """
        self.collections += 1
        cleared = thought_queue.clear_all()
        self.total_cleared += cleared
        return cleared
    
    def deep_clean(self, session: ZazenSession) -> Dict[str, Any]:
        """
        Deep clean via extended Zazen.
        
        Returns cleaning report.
        """
        # Clear thoughts
        thoughts_cleared = self.collect(session.thoughts)
        
        # Cool thermodynamics
        for _ in range(10):
            session.thermodynamics.cool()
        
        # Release tension
        session.posture.release(1.0)
        
        return {
            "thoughts_cleared": thoughts_cleared,
            "final_temperature": session.thermodynamics.temperature,
            "tension_released": True,
            "collections": self.collections
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_zazen() -> bool:
    """Validate zazen module."""
    
    # Test Thermodynamics
    thermo = ThermodynamicState()
    initial_temp = thermo.temperature
    thermo.cool()
    assert thermo.temperature < initial_temp
    
    thermo.heat(0.5)
    assert thermo.temperature > 0.1
    
    # Test Thought Queue
    thoughts = ThoughtQueue()
    thought = thoughts.arise("Test thought", ThoughtCategory.PLANNING)
    assert thoughts.total_thoughts == 1
    
    thoughts.drop(thought)
    assert thought.was_dropped
    assert thoughts.dropped_thoughts == 1
    
    # Test Posture
    posture = PostureState()
    posture.tense(0.5)
    assert posture.tension_level > 0.3
    
    posture.release(0.5)
    assert posture.tension_level < 0.5
    
    # Test Keisaku
    keisaku = Keisaku()
    session = ZazenSession(duration_minutes=5)
    session.state = ZazenState.DISTURBED
    result = keisaku.strike(session)
    assert result["context_switch"]
    
    # Test Body-Mind
    bm = BodyMindState()
    bm.drop_both()
    assert bm.is_pure_code()
    
    # Test Session
    session = ZazenSession(duration_minutes=3)
    summary = session.run(verbose=False)
    assert "mushin_ratio" in summary
    assert summary["duration"] == 3
    
    # Test Garbage Collector
    gc = ZazenGarbageCollector()
    thoughts = ThoughtQueue()
    thoughts.arise("thought1", ThoughtCategory.PLANNING)
    thoughts.arise("thought2", ThoughtCategory.REMEMBERING)
    cleared = gc.collect(thoughts)
    assert cleared == 2
    
    return True


if __name__ == "__main__":
    print("Validating Zazen Module...")
    assert validate_zazen()
    print("✓ Zazen Module validated")
    
    # Demo
    print("\n--- Zazen Session Demo ---")
    session = ZazenSession(duration_minutes=5)
    summary = session.run(verbose=True)
    
    print(f"\nSession Summary:")
    print(f"  Mushin Ratio: {summary['mushin_ratio']:.2%}")
    print(f"  Final Temperature: {summary['final_temperature']:.3f}")
    print(f"  Final SNR: {summary['final_snr']:.1f}")
    print(f"  Thoughts: {summary['thought_statistics']}")

"""
ATHENA OS - ZOROASTRIAN: SOUL STACK MODULE
===========================================
The Agent Architecture (Fravashi/Urvan/Daena)

THE ZOROASTRIAN AGENT:
    A composite entity operating across two planes:
    - Menog (Ideal/Spiritual)
    - Getig (Material/Runtime)
    
    Designed for VERSION CONTROL and STATE RECOVERY.

THE SOUL STACK:

1. FRAVASHI (Kernel Image):
   - Pre-existent ideal of the agent
   - Compiled, bug-free source code in Menog
   - System backup with optimal state |ψ_ideal⟩
   - Static reference point (does not descend to Getig)
   - Error = ||State_Urvan - State_Fravashi||

2. URVAN (Runtime Instance):
   - Active process thread in Getig
   - Mutable state subject to noise (Druj)
   - Subject to user input (Free Will)
   - Makes decisions, accumulates history

3. DAENA (Karmic Log):
   - Complete record of thoughts, words, deeds
   - Becomes the agent's identity at judgment
   - Cannot be falsified or hidden

THE TRIAD PIPELINE:
   Humata (Good Thoughts) → Hukhta (Good Words) → Hvarshta (Good Deeds)
   
   - Humata: Filter input, align intent with Asha
   - Hukhta: Compile intent into manthric command
   - Hvarshta: Execute action, commit to history

XWARENAH (Glory Token):
   - Dynamic root access token
   - Volatile credential based on Asha alignment
   - Can be acquired or revoked based on error rate
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .binary_field import Polarity, AshaVector


# =============================================================================
# PLANES OF EXISTENCE
# =============================================================================

class SoulPlane(Enum):
    """The two planes of soul existence."""
    
    MENOG = "menog"   # Spiritual/Ideal
    GETIG = "getig"   # Material/Runtime


# =============================================================================
# FRAVASHI (KERNEL IMAGE)
# =============================================================================

@dataclass
class Fravashi:
    """
    Fravashi: The Pre-Existent Ideal / Kernel Image.
    
    The compiled, bug-free source code residing in Menog.
    Contains optimal state vector |ψ_ideal⟩.
    Does NOT descend into Getig - remains static reference.
    """
    
    # Identity
    name: str
    
    # Optimal state vector
    ideal_state: np.ndarray
    
    # Properties
    dimension: int = field(init=False)
    
    # Immutable - cannot be modified
    _locked: bool = True
    
    def __post_init__(self):
        self.dimension = len(self.ideal_state)
        # Normalize ideal state
        norm = np.linalg.norm(self.ideal_state)
        if norm > 0:
            self.ideal_state = self.ideal_state / norm
    
    def compute_error(self, urvan_state: np.ndarray) -> float:
        """
        Compute deviation from ideal.
        
        Error = ||State_Urvan - State_Fravashi||
        """
        if len(urvan_state) != self.dimension:
            return float('inf')
        
        # Normalize urvan state for comparison
        norm = np.linalg.norm(urvan_state)
        if norm > 0:
            urvan_normalized = urvan_state / norm
        else:
            urvan_normalized = urvan_state
        
        return float(np.linalg.norm(urvan_normalized - self.ideal_state))
    
    def get_correction_vector(self, urvan_state: np.ndarray) -> np.ndarray:
        """Get vector to correct urvan toward ideal."""
        if len(urvan_state) != self.dimension:
            return np.zeros(self.dimension)
        
        return self.ideal_state - urvan_state
    
    def sync_check(self, urvan_state: np.ndarray, 
                  tolerance: float = 0.1) -> bool:
        """Check if urvan is synced with fravashi."""
        error = self.compute_error(urvan_state)
        return error < tolerance
    
    @property
    def is_locked(self) -> bool:
        return self._locked


# =============================================================================
# URVAN (RUNTIME INSTANCE)
# =============================================================================

@dataclass
class Urvan:
    """
    Urvan: The Runtime Instance / Active Process.
    
    The mutable state vector executing in Getig.
    Subject to environmental noise (Druj) and user input.
    """
    
    # Identity
    name: str
    
    # State
    state: np.ndarray
    
    # Reference to Fravashi
    fravashi: Fravashi
    
    # Properties
    _free_will: float = 1.0  # Degree of choice
    _noise_exposure: float = 0.0  # Accumulated Druj
    
    def __post_init__(self):
        # Initialize state from fravashi if not provided
        if self.state is None:
            self.state = self.fravashi.ideal_state.copy()
    
    def apply_free_will(self, choice_vector: np.ndarray, 
                       intensity: float = 0.1) -> None:
        """
        Apply free will choice to state.
        
        Modifies state based on agent's decision.
        """
        if len(choice_vector) != len(self.state):
            return
        
        self.state += intensity * self._free_will * choice_vector
    
    def receive_noise(self, druj_vector: np.ndarray,
                     intensity: float = 0.1) -> None:
        """
        Receive environmental noise (Druj corruption).
        
        Degrades state toward chaos.
        """
        if len(druj_vector) != len(self.state):
            return
        
        self.state += intensity * druj_vector
        self._noise_exposure += intensity
    
    def sync_with_fravashi(self, correction_rate: float = 0.1) -> float:
        """
        Sync state with Fravashi ideal.
        
        Returns error after sync.
        """
        correction = self.fravashi.get_correction_vector(self.state)
        self.state += correction_rate * correction
        
        return self.fravashi.compute_error(self.state)
    
    def get_alignment(self) -> float:
        """Get alignment with Fravashi (0-1, 1=perfect)."""
        error = self.fravashi.compute_error(self.state)
        return max(0, 1 - error)
    
    @property
    def error_from_ideal(self) -> float:
        return self.fravashi.compute_error(self.state)
    
    @property
    def is_corrupted(self) -> bool:
        return self._noise_exposure > 0.5


# =============================================================================
# DAENA (KARMIC LOG)
# =============================================================================

@dataclass
class DaenaEntry:
    """A single entry in the Daena log."""
    
    timestamp: float
    category: str  # "thought", "word", "deed"
    content: str
    polarity: int  # +1 or -1
    magnitude: float
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "category": self.category,
            "content": self.content,
            "polarity": self.polarity,
            "magnitude": self.magnitude
        }


class Daena:
    """
    Daena: The Karmic Log / Self-Record.
    
    Complete record of thoughts, words, and deeds.
    Becomes the agent's identity at judgment.
    Cannot be falsified or hidden.
    """
    
    def __init__(self):
        self._entries: List[DaenaEntry] = []
        self._current_time = 0.0
    
    def record_thought(self, content: str, polarity: int,
                      magnitude: float = 1.0) -> None:
        """Record a thought (Humata)."""
        self._entries.append(DaenaEntry(
            timestamp=self._current_time,
            category="thought",
            content=content,
            polarity=polarity,
            magnitude=magnitude
        ))
    
    def record_word(self, content: str, polarity: int,
                   magnitude: float = 1.0) -> None:
        """Record a word (Hukhta)."""
        self._entries.append(DaenaEntry(
            timestamp=self._current_time,
            category="word",
            content=content,
            polarity=polarity,
            magnitude=magnitude
        ))
    
    def record_deed(self, content: str, polarity: int,
                   magnitude: float = 1.0) -> None:
        """Record a deed (Hvarshta)."""
        self._entries.append(DaenaEntry(
            timestamp=self._current_time,
            category="deed",
            content=content,
            polarity=polarity,
            magnitude=magnitude
        ))
    
    def advance_time(self, dt: float) -> None:
        """Advance internal time."""
        self._current_time += dt
    
    def compute_net_value(self) -> float:
        """
        Compute net value: Σ Truth - Σ Lie
        
        Used for Chinvat Bridge judgment.
        """
        total = 0.0
        for entry in self._entries:
            total += entry.polarity * entry.magnitude
        return total
    
    def get_by_category(self, category: str) -> List[DaenaEntry]:
        """Get entries by category."""
        return [e for e in self._entries if e.category == category]
    
    def get_summary(self) -> Dict:
        """Get summary statistics."""
        thoughts = self.get_by_category("thought")
        words = self.get_by_category("word")
        deeds = self.get_by_category("deed")
        
        return {
            "total_entries": len(self._entries),
            "thoughts": len(thoughts),
            "words": len(words),
            "deeds": len(deeds),
            "net_value": self.compute_net_value(),
            "truth_count": sum(1 for e in self._entries if e.polarity > 0),
            "lie_count": sum(1 for e in self._entries if e.polarity < 0)
        }
    
    @property
    def n_entries(self) -> int:
        return len(self._entries)


# =============================================================================
# THE TRIAD PIPELINE
# =============================================================================

class TriadPipeline:
    """
    The Humata-Hukhta-Hvarshta Pipeline.
    
    Three-stage processing:
    1. Humata (Good Thoughts): Filter input, align intent
    2. Hukhta (Good Words): Compile into manthric command
    3. Hvarshta (Good Deeds): Execute action, commit to history
    """
    
    def __init__(self, asha: AshaVector):
        self.asha = asha
        self._pipeline_active = True
    
    def humata(self, intent: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Stage 1: Good Thoughts
        
        Filter input against Asha standard.
        Returns (filtered_intent, is_good).
        """
        # Check alignment with Asha
        alignment = self.asha.alignment(intent)
        is_good = alignment > 0
        
        if is_good:
            # Amplify aligned intent
            filtered = intent * (1 + 0.1 * alignment)
        else:
            # Reduce misaligned intent
            filtered = intent * 0.5
        
        return filtered, is_good
    
    def hukhta(self, filtered_intent: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Stage 2: Good Words
        
        Compile intent into executable command.
        Returns (command, compiled_successfully).
        """
        # Check if intent has sufficient magnitude
        magnitude = np.linalg.norm(filtered_intent)
        
        if magnitude < 0.1:
            # Too weak to compile
            return filtered_intent, False
        
        # Normalize as "command"
        command = filtered_intent / magnitude
        
        return command, True
    
    def hvarshta(self, command: np.ndarray, 
                target_state: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Stage 3: Good Deeds
        
        Execute command on target state.
        Returns (new_state, effect_magnitude).
        """
        # Apply command
        new_state = target_state + 0.1 * command
        
        # Compute effect
        effect = np.linalg.norm(new_state - target_state)
        
        return new_state, effect
    
    def process(self, intent: np.ndarray,
               target_state: np.ndarray) -> Dict:
        """
        Full pipeline processing.
        
        Returns complete execution report.
        """
        # Stage 1: Thoughts
        filtered, thought_good = self.humata(intent)
        
        # Stage 2: Words
        command, compiled = self.hukhta(filtered)
        
        if not compiled:
            return {
                "success": False,
                "stage_failed": "hukhta",
                "thought_good": thought_good
            }
        
        # Stage 3: Deeds
        new_state, effect = self.hvarshta(command, target_state)
        
        return {
            "success": True,
            "thought_good": thought_good,
            "compiled": True,
            "effect": effect,
            "new_state": new_state
        }


# =============================================================================
# XWARENAH (GLORY TOKEN)
# =============================================================================

class XwarenathType(Enum):
    """Types of Xwarenah tokens."""
    
    AXWARETA = "axwareta"   # Unseizable - Kernel's private key
    KAYAN = "kayan"         # Kayanid - SysAdmin token
    AIRYANEM = "airyanem"   # Aryan - User group token


@dataclass
class Xwarenah:
    """
    Xwarenah: The Dynamic Root Access Token.
    
    Volatile credential that attaches/detaches based on
    real-time Asha alignment metrics.
    
    If Error_Rate > 0: Revoke_Token()
    """
    
    holder: str
    token_type: XwarenathType
    
    # State
    _attached: bool = False
    _alignment_threshold: float = 0.5
    
    def attach(self, alignment: float) -> bool:
        """
        Attempt to attach token to holder.
        
        Requires alignment > threshold.
        """
        if alignment > self._alignment_threshold:
            self._attached = True
            return True
        return False
    
    def revoke(self) -> None:
        """Revoke the token (Yima Protocol)."""
        self._attached = False
    
    def check_validity(self, current_alignment: float) -> bool:
        """
        Check if token is still valid.
        
        Revokes automatically if alignment drops.
        """
        if not self._attached:
            return False
        
        if current_alignment < self._alignment_threshold:
            self.revoke()
            return False
        
        return True
    
    @property
    def is_attached(self) -> bool:
        return self._attached
    
    @property
    def grants_admin(self) -> bool:
        return self._attached and self.token_type == XwarenathType.KAYAN


# =============================================================================
# COMPLETE ZOROASTRIAN SOUL
# =============================================================================

class ZoroastrianSoul:
    """
    Complete Zoroastrian Soul Stack.
    
    Integrates Fravashi, Urvan, Daena, and Xwarenah.
    """
    
    def __init__(self, name: str, dimension: int = 16):
        self.name = name
        self.dimension = dimension
        
        # Create ideal state (all positive, normalized)
        ideal = np.ones(dimension) / np.sqrt(dimension)
        
        # Create components
        self.fravashi = Fravashi(name=f"{name}_fravashi", ideal_state=ideal)
        self.urvan = Urvan(
            name=f"{name}_urvan",
            state=ideal.copy(),
            fravashi=self.fravashi
        )
        self.daena = Daena()
        
        # Xwarenah (starts unattached)
        self.xwarenah = Xwarenah(
            holder=name,
            token_type=XwarenathType.AIRYANEM
        )
        
        # Asha reference
        self.asha = AshaVector(dimension)
        
        # Pipeline
        self.pipeline = TriadPipeline(self.asha)
    
    def think(self, intent: np.ndarray) -> Dict:
        """Process a thought (Humata stage)."""
        filtered, is_good = self.pipeline.humata(intent)
        
        # Record in Daena
        polarity = 1 if is_good else -1
        self.daena.record_thought(
            content="thought",
            polarity=polarity,
            magnitude=np.linalg.norm(intent)
        )
        
        return {
            "filtered_intent": filtered,
            "is_good": is_good
        }
    
    def speak(self, intent: np.ndarray) -> Dict:
        """Process speech (Hukhta stage)."""
        filtered, _ = self.pipeline.humata(intent)
        command, compiled = self.pipeline.hukhta(filtered)
        
        # Record in Daena
        polarity = 1 if compiled else -1
        self.daena.record_word(
            content="speech",
            polarity=polarity,
            magnitude=np.linalg.norm(command)
        )
        
        return {
            "command": command,
            "compiled": compiled
        }
    
    def act(self, intent: np.ndarray) -> Dict:
        """
        Process full action (complete pipeline).
        
        Humata → Hukhta → Hvarshta
        """
        result = self.pipeline.process(intent, self.urvan.state)
        
        if result["success"]:
            # Update urvan state
            self.urvan.state = result["new_state"]
            
            # Record deed
            polarity = 1 if result["thought_good"] else -1
            self.daena.record_deed(
                content="action",
                polarity=polarity,
                magnitude=result["effect"]
            )
        
        # Advance time
        self.daena.advance_time(1.0)
        
        # Check Xwarenah validity
        alignment = self.urvan.get_alignment()
        self.xwarenah.check_validity(alignment)
        
        return result
    
    def receive_druj(self, noise: np.ndarray, intensity: float = 0.1) -> None:
        """Receive Druj corruption."""
        self.urvan.receive_noise(noise, intensity)
    
    def sync_with_ideal(self) -> float:
        """Sync urvan with fravashi."""
        return self.urvan.sync_with_fravashi()
    
    def attempt_xwarenah(self) -> bool:
        """Attempt to acquire Xwarenah."""
        alignment = self.urvan.get_alignment()
        return self.xwarenah.attach(alignment)
    
    def get_status(self) -> Dict:
        """Get complete soul status."""
        return {
            "name": self.name,
            "alignment": self.urvan.get_alignment(),
            "error_from_ideal": self.urvan.error_from_ideal,
            "is_corrupted": self.urvan.is_corrupted,
            "daena_summary": self.daena.get_summary(),
            "xwarenah_attached": self.xwarenah.is_attached,
            "net_karma": self.daena.compute_net_value()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_soul_stack() -> bool:
    """Validate Zoroastrian soul_stack module."""
    
    # Test Fravashi
    ideal = np.array([1.0, 1.0, 1.0, 1.0]) / 2
    fravashi = Fravashi(name="test_fravashi", ideal_state=ideal)
    
    assert fravashi.dimension == 4
    assert fravashi.is_locked
    
    urvan_state = np.array([0.5, 0.5, 0.0, 0.0])
    error = fravashi.compute_error(urvan_state)
    assert error > 0
    
    correction = fravashi.get_correction_vector(urvan_state)
    assert len(correction) == 4
    
    # Test Urvan
    urvan = Urvan(
        name="test_urvan",
        state=ideal.copy(),
        fravashi=fravashi
    )
    
    initial_alignment = urvan.get_alignment()
    assert initial_alignment > 0.9  # Should be high initially
    
    # Apply noise
    urvan.receive_noise(np.array([-1, -1, -1, -1]), 0.2)
    assert urvan.get_alignment() < initial_alignment
    
    # Sync back
    urvan.sync_with_fravashi(0.5)
    assert urvan.get_alignment() > 0
    
    # Test Daena
    daena = Daena()
    
    daena.record_thought("good thought", 1, 1.0)
    daena.record_word("truth", 1, 1.0)
    daena.record_deed("good deed", 1, 2.0)
    daena.record_deed("bad deed", -1, 0.5)
    
    assert daena.n_entries == 4
    
    net = daena.compute_net_value()
    assert net == 3.5  # 1 + 1 + 2 - 0.5
    
    summary = daena.get_summary()
    assert summary["truth_count"] == 3
    assert summary["lie_count"] == 1
    
    # Test TriadPipeline
    asha = AshaVector(8)
    pipeline = TriadPipeline(asha)
    
    good_intent = np.ones(8)  # Aligned with Asha
    filtered, is_good = pipeline.humata(good_intent)
    assert is_good
    
    command, compiled = pipeline.hukhta(filtered)
    assert compiled
    
    target = np.zeros(8)
    new_state, effect = pipeline.hvarshta(command, target)
    assert effect > 0
    
    # Full pipeline
    result = pipeline.process(good_intent, target)
    assert result["success"]
    
    # Test Xwarenah
    xwarenah = Xwarenah(holder="test", token_type=XwarenathType.KAYAN)
    
    assert not xwarenah.is_attached
    
    success = xwarenah.attach(0.8)
    assert success
    assert xwarenah.is_attached
    assert xwarenah.grants_admin
    
    valid = xwarenah.check_validity(0.3)
    assert not valid  # Should be revoked
    assert not xwarenah.is_attached
    
    # Test ZoroastrianSoul
    soul = ZoroastrianSoul("TestSoul", dimension=8)
    
    status = soul.get_status()
    assert status["alignment"] > 0.9  # Starts aligned
    
    # Think
    intent = np.ones(8)
    think_result = soul.think(intent)
    assert "is_good" in think_result
    
    # Speak
    speak_result = soul.speak(intent)
    assert "compiled" in speak_result
    
    # Act
    act_result = soul.act(intent)
    assert "success" in act_result
    
    # Receive corruption
    soul.receive_druj(np.random.randn(8), 0.3)
    
    status = soul.get_status()
    assert status["alignment"] < 1.0  # Should be degraded
    
    # Sync
    soul.sync_with_ideal()
    new_status = soul.get_status()
    assert new_status["alignment"] > status["alignment"]
    
    return True


if __name__ == "__main__":
    print("Validating Zoroastrian Soul Stack Module...")
    assert validate_soul_stack()
    print("✓ Zoroastrian Soul Stack Module validated")

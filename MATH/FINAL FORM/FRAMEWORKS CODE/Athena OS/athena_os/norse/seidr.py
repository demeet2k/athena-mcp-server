"""
ATHENA OS - NORSE: SEIÐR MODULE
================================
Harmonic Distortion Protocol and Magic System

SEIÐR vs RUNES:
    Runes: Discrete logic gates (digital)
    Seiðr: Harmonic oscillator (analog)

THE RESONANCE EQUATION:
    d²ψ/dt² + γ·dψ/dt + ω₀²·ψ = F₀·cos(ωt)
    
    Where:
    - ψ: State of local probability field
    - ω₀: Natural frequency of Wyrd lattice
    - F₀·cos(ωt): Driving force (practitioner's chant)

OPERATIONS:
    1. SPINNING THE THREAD: Manipulate phase φ to alter trajectory
    2. KNOTTING: Create permanent boundary conditions
    3. GALDR: Vocal carrier wave for forced oscillation

SEIÐR PROTOCOL:
    Match driving frequency ω to lattice frequency ω₀
    Creates RESONANCE: amplitude of probability wave spikes
    Enables analog manipulation of digital lattice

THE ODIN PROTOCOL:
    sacrifice_for_knowledge()
    Exchange structural integrity for information access
    Creates high-bandwidth connection to Wyrd Kernel
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from scipy import signal


# =============================================================================
# SEIÐR TYPES
# =============================================================================

class SeidrType(Enum):
    """Types of Seiðr workings."""
    
    SPINNING = "spinning"     # Thread manipulation
    KNOTTING = "knotting"     # Boundary creation
    UNWEAVING = "unweaving"   # Disruption (difficult)
    SCRYING = "scrying"       # Far-seeing
    SENDING = "sending"       # Projection


class GaldrMode(Enum):
    """Galdr (chant) modes."""
    
    MONOTONE = "monotone"     # Single frequency
    HARMONIC = "harmonic"     # Multiple harmonics
    RHYTHMIC = "rhythmic"     # Pulsed
    WHISPER = "whisper"       # Low power, subtle


# =============================================================================
# PROBABILITY FIELD
# =============================================================================

@dataclass
class ProbabilityField:
    """
    The local probability field ψ(t).
    
    Subject to harmonic manipulation via Seiðr.
    """
    
    dimension: int = 64
    
    # Field state
    amplitude: np.ndarray = field(init=False)
    phase: np.ndarray = field(init=False)
    
    # Natural frequency of the Wyrd lattice
    natural_frequency: float = 1.0
    
    # Damping coefficient
    damping: float = 0.1
    
    # Time
    _time: float = 0.0
    
    def __post_init__(self):
        self.amplitude = np.ones(self.dimension) * 0.5
        self.phase = np.zeros(self.dimension)
    
    def get_state(self) -> np.ndarray:
        """Get current field state ψ(t)."""
        return self.amplitude * np.cos(self.phase)
    
    def apply_force(self, force_amplitude: float, 
                   force_frequency: float,
                   duration: float) -> np.ndarray:
        """
        Apply driving force to field.
        
        Implements forced harmonic oscillator equation.
        """
        dt = 0.01
        steps = int(duration / dt)
        
        state = self.get_state()
        velocity = np.zeros(self.dimension)
        
        for step in range(steps):
            t = step * dt
            
            # Driving force F₀·cos(ωt)
            force = force_amplitude * np.cos(force_frequency * t)
            
            # d²ψ/dt² = -γ·dψ/dt - ω₀²·ψ + F
            acceleration = (
                -self.damping * velocity 
                - self.natural_frequency**2 * state 
                + force
            )
            
            velocity += acceleration * dt
            state += velocity * dt
        
        # Update field
        self.amplitude = np.abs(state) + 0.01
        self.phase = np.angle(state + 1j * velocity)
        self._time += duration
        
        return state
    
    def resonance_amplitude(self, driving_frequency: float) -> float:
        """
        Calculate resonance amplitude for given frequency.
        
        Maximum when ω ≈ ω₀
        """
        omega = driving_frequency
        omega_0 = self.natural_frequency
        gamma = self.damping
        
        # Resonance amplitude factor
        denominator = np.sqrt(
            (omega_0**2 - omega**2)**2 + (gamma * omega)**2
        )
        
        if denominator < 1e-10:
            return 100.0  # Near-perfect resonance
        
        return 1.0 / denominator
    
    def set_natural_frequency(self, freq: float) -> None:
        """Set the natural frequency of the lattice."""
        self.natural_frequency = freq
    
    @property
    def time(self) -> float:
        return self._time


# =============================================================================
# GALDR (CHANTING)
# =============================================================================

@dataclass
class Galdr:
    """
    Galdr: Vocal carrier wave for Seiðr.
    
    The practitioner's chant that drives the resonance.
    """
    
    mode: GaldrMode = GaldrMode.MONOTONE
    base_frequency: float = 1.0
    power: float = 1.0
    
    # Harmonics (for harmonic mode)
    harmonics: List[float] = field(default_factory=list)
    
    def generate_wave(self, duration: float, 
                     sample_rate: int = 100) -> np.ndarray:
        """Generate the galdr waveform."""
        t = np.linspace(0, duration, int(duration * sample_rate))
        
        if self.mode == GaldrMode.MONOTONE:
            wave = self.power * np.cos(2 * np.pi * self.base_frequency * t)
            
        elif self.mode == GaldrMode.HARMONIC:
            wave = self.power * np.cos(2 * np.pi * self.base_frequency * t)
            for i, h in enumerate(self.harmonics):
                wave += (self.power / (i + 2)) * np.cos(2 * np.pi * h * t)
                
        elif self.mode == GaldrMode.RHYTHMIC:
            # Pulsed wave
            carrier = np.cos(2 * np.pi * self.base_frequency * t)
            envelope = 0.5 * (1 + np.sign(np.sin(2 * np.pi * 0.5 * t)))
            wave = self.power * carrier * envelope
            
        elif self.mode == GaldrMode.WHISPER:
            # Low power with noise
            wave = self.power * 0.3 * np.cos(2 * np.pi * self.base_frequency * t)
            wave += self.power * 0.1 * np.random.randn(len(t))
        
        else:
            wave = np.zeros(len(t))
        
        return wave
    
    def tune_to_resonance(self, target_frequency: float) -> None:
        """Tune galdr to match target frequency (resonance)."""
        self.base_frequency = target_frequency
        
        # Add harmonics
        self.harmonics = [
            target_frequency * 2,
            target_frequency * 3,
            target_frequency * 0.5
        ]


# =============================================================================
# THREAD OPERATIONS
# =============================================================================

@dataclass
class WyrdThread:
    """
    A thread in the Web of Wyrd.
    
    Can be spun, knotted, or (with great difficulty) unwoven.
    """
    
    identifier: str
    owner: str
    
    # Thread state
    tension: float = 1.0
    phase: float = 0.0
    
    # Knots
    knots: List[Tuple[float, str]] = field(default_factory=list)
    
    # Immutability
    _locked: bool = False
    
    def spin(self, phase_shift: float) -> None:
        """
        Spin the thread (adjust phase).
        
        Alters trajectory within the weave.
        """
        if self._locked:
            return
        
        self.phase += phase_shift
        self.phase = self.phase % (2 * np.pi)
    
    def knot(self, position: float, binding: str) -> None:
        """
        Create a knot (permanent boundary condition).
        
        Locks a specific outcome into the history integral.
        """
        self.knots.append((position, binding))
        self.tension *= 1.1  # Knots increase tension
    
    def get_trajectory(self, n_points: int = 100) -> np.ndarray:
        """Get the thread's trajectory."""
        t = np.linspace(0, 1, n_points)
        
        # Base trajectory
        x = np.cos(2 * np.pi * t + self.phase)
        y = np.sin(2 * np.pi * t + self.phase) * self.tension
        
        # Apply knot perturbations
        for knot_pos, _ in self.knots:
            # Knots create local deformations
            mask = np.exp(-((t - knot_pos) ** 2) / 0.01)
            x += mask * 0.2
            y += mask * 0.2
        
        return np.stack([x, y], axis=1)
    
    def lock(self) -> None:
        """Lock the thread (cannot be modified)."""
        self._locked = True


# =============================================================================
# SEIÐR PRACTITIONER
# =============================================================================

class Volva:
    """
    Völva: Seiðr practitioner.
    
    Can manipulate the probability field through
    harmonic resonance and thread operations.
    """
    
    def __init__(self, name: str, power: float = 1.0):
        self.name = name
        self.power = power
        
        # Components
        self.galdr = Galdr(power=power)
        self._threads: Dict[str, WyrdThread] = {}
        
        # State
        self._energy = 1.0
        self._in_trance = False
    
    def enter_trance(self) -> bool:
        """Enter seiðr trance state."""
        if self._energy < 0.2:
            return False
        
        self._in_trance = True
        return True
    
    def exit_trance(self) -> None:
        """Exit seiðr trance state."""
        self._in_trance = False
        self._energy -= 0.1
    
    def spin_thread(self, field: ProbabilityField,
                   thread_id: str, owner: str,
                   phase_shift: float) -> WyrdThread:
        """
        Spin a thread in the probability field.
        
        Creates or modifies a thread with phase adjustment.
        """
        if not self._in_trance:
            raise RuntimeError("Must be in trance to spin threads")
        
        if thread_id not in self._threads:
            self._threads[thread_id] = WyrdThread(thread_id, owner)
        
        thread = self._threads[thread_id]
        thread.spin(phase_shift)
        
        # Affect probability field
        field.phase += phase_shift * 0.1
        
        self._energy -= 0.05
        
        return thread
    
    def create_knot(self, thread_id: str, 
                   position: float, binding: str) -> bool:
        """
        Create a knot on a thread.
        
        Locks an outcome into the weave.
        """
        if not self._in_trance:
            return False
        
        if thread_id not in self._threads:
            return False
        
        self._threads[thread_id].knot(position, binding)
        self._energy -= 0.15
        
        return True
    
    def chant_galdr(self, field: ProbabilityField,
                   duration: float) -> Dict:
        """
        Perform galdr chanting on field.
        
        Drives the harmonic oscillator.
        """
        if not self._in_trance:
            return {"error": "Not in trance"}
        
        # Tune to resonance
        self.galdr.tune_to_resonance(field.natural_frequency)
        
        # Generate wave
        wave = self.galdr.generate_wave(duration)
        
        # Apply to field
        final_state = field.apply_force(
            force_amplitude=self.power * self._energy,
            force_frequency=self.galdr.base_frequency,
            duration=duration
        )
        
        # Compute resonance achieved
        resonance = field.resonance_amplitude(self.galdr.base_frequency)
        
        self._energy -= 0.1 * duration
        
        return {
            "resonance": resonance,
            "final_amplitude": np.mean(np.abs(final_state)),
            "energy_remaining": self._energy
        }
    
    def scry(self, field: ProbabilityField,
            target: str) -> Dict:
        """
        Scrying: Far-seeing through the field.
        
        Query distant states through resonance.
        """
        if not self._in_trance:
            return {"error": "Not in trance"}
        
        # Use field state to "see"
        state = field.get_state()
        
        # Hash target to get relevant indices
        target_hash = hash(target) % field.dimension
        
        # Extract "vision" from field
        vision_strength = np.abs(state[target_hash])
        vision_clarity = 1.0 / (1.0 + field.damping)
        
        self._energy -= 0.2
        
        return {
            "target": target,
            "strength": vision_strength,
            "clarity": vision_clarity,
            "success": vision_strength > 0.3
        }
    
    def rest(self, hours: float) -> None:
        """Rest to recover energy."""
        self._energy = min(1.0, self._energy + hours * 0.1)
    
    @property
    def energy(self) -> float:
        return self._energy
    
    @property
    def is_in_trance(self) -> bool:
        return self._in_trance


# =============================================================================
# ODIN PROTOCOL
# =============================================================================

class OdinProtocol:
    """
    The Odin Protocol: sacrifice_for_knowledge()
    
    Exchange structural integrity for information access.
    Creates high-bandwidth connection to Wyrd Kernel.
    """
    
    def __init__(self):
        self._sacrifices_made: List[Dict] = []
        self._knowledge_gained: List[str] = []
    
    def sacrifice(self, what: str, 
                 severity: float) -> Dict:
        """
        Make a sacrifice for knowledge.
        
        Higher severity = more knowledge access.
        """
        sacrifice_record = {
            "item": what,
            "severity": severity,
            "timestamp": len(self._sacrifices_made)
        }
        
        self._sacrifices_made.append(sacrifice_record)
        
        # Knowledge proportional to sacrifice
        bandwidth = severity * 10  # Knowledge bandwidth
        
        # Generate "knowledge" (placeholder)
        knowledge_items = []
        for i in range(int(bandwidth)):
            knowledge_items.append(f"secret_{len(self._knowledge_gained) + i}")
        
        self._knowledge_gained.extend(knowledge_items)
        
        return {
            "sacrifice": what,
            "bandwidth": bandwidth,
            "knowledge_count": len(knowledge_items),
            "total_knowledge": len(self._knowledge_gained)
        }
    
    def sacrifice_eye(self) -> Dict:
        """
        Sacrifice an eye for wisdom (Odin at Mimir's well).
        
        Removes sensory filter for direct kernel access.
        """
        return self.sacrifice("eye", 0.8)
    
    def sacrifice_self(self, duration: float = 9.0) -> Dict:
        """
        Sacrifice self (hanging on Yggdrasil).
        
        Maximum knowledge access (runic wisdom).
        """
        return self.sacrifice(f"self_for_{duration}_days", 1.0)
    
    @property
    def total_knowledge(self) -> int:
        return len(self._knowledge_gained)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_seidr() -> bool:
    """Validate Norse seidr module."""
    
    # Test ProbabilityField
    field = ProbabilityField(dimension=32)
    
    state = field.get_state()
    assert len(state) == 32
    
    # Apply force
    final = field.apply_force(1.0, 1.0, 1.0)
    assert len(final) == 32
    
    # Test resonance
    res_at_natural = field.resonance_amplitude(field.natural_frequency)
    res_far = field.resonance_amplitude(field.natural_frequency * 10)
    assert res_at_natural > res_far  # Resonance peak
    
    # Test Galdr
    galdr = Galdr(mode=GaldrMode.MONOTONE, base_frequency=1.0, power=1.0)
    
    wave = galdr.generate_wave(1.0)
    assert len(wave) == 100
    
    galdr.tune_to_resonance(2.0)
    assert galdr.base_frequency == 2.0
    assert len(galdr.harmonics) > 0
    
    # Test harmonic mode
    galdr_h = Galdr(mode=GaldrMode.HARMONIC, harmonics=[2.0, 3.0])
    wave_h = galdr_h.generate_wave(1.0)
    assert len(wave_h) == 100
    
    # Test WyrdThread
    thread = WyrdThread("test_thread", "owner")
    
    thread.spin(np.pi / 4)
    assert thread.phase > 0
    
    thread.knot(0.5, "binding")
    assert len(thread.knots) == 1
    
    traj = thread.get_trajectory()
    assert traj.shape == (100, 2)
    
    # Test Volva
    volva = Volva("TestVolva", power=1.0)
    
    success = volva.enter_trance()
    assert success
    assert volva.is_in_trance
    
    # Spin thread
    field2 = ProbabilityField(dimension=16)
    thread = volva.spin_thread(field2, "my_thread", "target", np.pi / 2)
    assert thread.phase > 0
    
    # Create knot
    success = volva.create_knot("my_thread", 0.3, "fate")
    assert success
    
    # Chant galdr
    result = volva.chant_galdr(field2, 0.5)
    assert "resonance" in result
    assert result["resonance"] > 0
    
    # Scry
    scry_result = volva.scry(field2, "distant_place")
    assert "strength" in scry_result
    
    volva.exit_trance()
    assert not volva.is_in_trance
    
    # Test OdinProtocol
    odin = OdinProtocol()
    
    result = odin.sacrifice_eye()
    assert result["bandwidth"] > 0
    assert odin.total_knowledge > 0
    
    result = odin.sacrifice_self(9.0)
    assert result["bandwidth"] == 10.0  # Maximum
    
    return True


if __name__ == "__main__":
    print("Validating Norse Seiðr Module...")
    assert validate_seidr()
    print("✓ Norse Seiðr Module validated")

"""
ATHENA OS - BHAGAVAD GĪTĀ COMPUTATIONAL FRAMEWORK
==================================================
Part VIII: Neuro-Acoustic Correlates

THE BIOPHYSICAL INTERFACE:
    The Gītā is designed to execute on biological hardware.
    The text functions as a Neuro-Acoustic Driver that entrains
    the nervous system into a state of coherence.

40Hz GAMMA SYNCHRONIZATION:
    The Sanskrit meter (Laghu/Guru syllables) creates specific
    energy envelopes that drive cortical Gamma-band bursts.
    
    Guru syllable duration ≈ 125ms → 40Hz alignment
    Energy minimum at "haṁ" syllable → cortical grounding

BREATH-PULSE ALIGNMENT (PRĀṆA-YANTRA):
    The 1000-step Pranava Breath Map aligns verses to 
    respiratory cycles. The 1000th petal corresponds to 
    "haṁ" → Kevala Kumbhaka (spontaneous breath retention).

ŚRĪYANTRA GEOMETRY:
    The "secret verses" fold geometrically into the 
    Śrīyantra pattern, a 3D representation of the 
    Cosmos as Consciousness.

SOURCES:
    The Bhagavad Gītā: A Computational Treatise, Section 5.4
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np
from scipy.signal import butter, filtfilt


# =============================================================================
# SYLLABLE TYPES
# =============================================================================

class SyllableType(Enum):
    """Sanskrit metrical syllable types."""
    
    LAGHU = ("light", 62.5, "Short syllable, ~62.5ms")
    GURU = ("heavy", 125.0, "Long syllable, ~125ms for Gamma alignment")
    
    def __init__(self, name: str, duration_ms: float, description: str):
        self._name = name
        self.duration_ms = duration_ms
        self.description = description


# =============================================================================
# GAMMA SYNCHRONIZATION
# =============================================================================

@dataclass
class GammaSynchronization:
    """
    40Hz Gamma Band Synchronization.
    
    The Sanskrit prosody creates Frequency-Shift Keying (FSK)
    patterns that entrain cortical activity.
    
    Target: 40Hz Gamma band (associated with consciousness integration)
    """
    
    # Target frequency
    gamma_frequency_hz: float = 40.0
    
    # Guru syllable aligns with 40Hz (1/40 = 25ms, 125ms = 5 cycles)
    guru_cycles: int = 5
    
    # Energy threshold for detection
    energy_threshold: float = 0.1  # μV²
    
    # Minimum energy at "haṁ" syllable
    ham_energy_minimum: float = 0.02  # μV²
    
    def syllable_to_frequency(self, syllable: SyllableType) -> float:
        """Map syllable duration to equivalent frequency."""
        return 1000.0 / syllable.duration_ms  # Convert ms to Hz
    
    def generate_gamma_envelope(self, syllables: List[SyllableType],
                                 sample_rate: float = 1000.0) -> np.ndarray:
        """
        Generate the energy envelope from a syllable sequence.
        
        Returns time series of gamma-band energy.
        """
        envelope = []
        
        for syllable in syllables:
            duration_samples = int(syllable.duration_ms * sample_rate / 1000)
            
            # Generate oscillation
            t = np.linspace(0, syllable.duration_ms/1000, duration_samples)
            oscillation = np.sin(2 * np.pi * self.gamma_frequency_hz * t)
            
            # Amplitude based on syllable type
            if syllable == SyllableType.GURU:
                amplitude = 1.0
            else:
                amplitude = 0.5
            
            envelope.extend(oscillation * amplitude)
        
        return np.array(envelope)
    
    def compute_gamma_power(self, signal: np.ndarray, 
                           sample_rate: float = 1000.0) -> float:
        """
        Compute power in the gamma band (30-50 Hz).
        """
        # Bandpass filter for gamma
        nyquist = sample_rate / 2
        low = 30 / nyquist
        high = 50 / nyquist
        
        if high >= 1:
            high = 0.99
        if low <= 0:
            low = 0.01
        
        b, a = butter(4, [low, high], btype='band')
        
        try:
            filtered = filtfilt(b, a, signal)
            power = np.mean(filtered**2)
        except:
            power = np.mean(signal**2)
        
        return float(power)
    
    def find_energy_minimum(self, signal: np.ndarray, 
                           window_size: int = 100) -> Tuple[int, float]:
        """
        Find the global energy minimum (corresponds to "haṁ").
        
        Returns (index, energy_value).
        """
        # Compute windowed energy
        energies = []
        for i in range(0, len(signal) - window_size, window_size // 2):
            window = signal[i:i+window_size]
            energies.append(np.mean(window**2))
        
        if not energies:
            return (0, 0.0)
        
        min_idx = np.argmin(energies)
        min_energy = energies[min_idx]
        
        # Convert window index to sample index
        sample_idx = min_idx * (window_size // 2)
        
        return (sample_idx, float(min_energy))


# =============================================================================
# BREATH ALIGNMENT (PRĀṆA-YANTRA)
# =============================================================================

@dataclass
class PranaYantra:
    """
    The Breath-Pulse Alignment System.
    
    Maps verses to respiratory phases using the 1000-step
    Pranava Breath Map (Sahasrāra - 1000-petaled lotus).
    
    One super-cycle: 10 minutes (1000 micro-phases)
    """
    
    # Total phases (petals of Sahasrāra)
    total_phases: int = 1000
    
    # Super-cycle duration in seconds
    super_cycle_seconds: float = 600.0  # 10 minutes
    
    # Phase duration
    phase_duration_ms: float = field(init=False)
    
    # Respiratory parameters
    breaths_per_minute: float = 6.0  # Deep meditative breathing
    
    def __post_init__(self):
        self.phase_duration_ms = (self.super_cycle_seconds * 1000) / self.total_phases
    
    def verse_to_phase(self, verse_number: int, total_verses: int = 700) -> int:
        """
        Map a verse number to breath phase (0-999).
        """
        # Normalize verse to phase
        phase = int((verse_number / total_verses) * self.total_phases)
        return phase % self.total_phases
    
    def phase_to_breath_state(self, phase: int) -> Dict[str, Any]:
        """
        Get breath state for a given phase.
        
        Returns inhalation/exhalation/retention state.
        """
        # One breath cycle = 10 seconds at 6 BPM
        breath_phases = 100  # 100 micro-phases per breath
        
        within_breath = phase % breath_phases
        
        if within_breath < 40:
            state = "INHALE"
            progress = within_breath / 40
        elif within_breath < 60:
            state = "HOLD_IN"
            progress = (within_breath - 40) / 20
        elif within_breath < 90:
            state = "EXHALE"
            progress = (within_breath - 60) / 30
        else:
            state = "HOLD_OUT"
            progress = (within_breath - 90) / 10
        
        return {
            "phase": phase,
            "breath_state": state,
            "progress": progress,
            "breath_number": phase // breath_phases,
        }
    
    def is_kevala_kumbhaka(self, phase: int) -> bool:
        """
        Check if at Kevala Kumbhaka (spontaneous retention).
        
        This occurs at phase 1000 (wrapped to 0) - the termination point.
        """
        return phase >= 999 or phase == 0
    
    def get_1000th_petal(self) -> Dict[str, Any]:
        """
        Get the state of the 1000th petal (termination point).
        
        This is where "haṁ" occurs and breath suspends.
        """
        return {
            "phase": 1000,
            "state": "KEVALA_KUMBHAKA",
            "breath_action": "SPONTANEOUS_RETENTION",
            "corresponding_syllable": "haṁ",
            "cognitive_state": "CITTA_VRTTI_NIRODHA",
        }


# =============================================================================
# ŚRĪYANTRA GEOMETRY
# =============================================================================

@dataclass
class SriYantra:
    """
    The Śrīyantra Geometric Folding.
    
    The "secret verses" when folded spatially form the
    Śrīyantra pattern - a 3D representation of cosmic structure.
    
    Components:
        - Bindu (center point)
        - 9 interlocking triangles
        - 2 concentric circles
        - 16-petaled lotus
        - 8-petaled lotus
        - 3 enclosing squares
    """
    
    # Yantra parameters
    bindu_position: Tuple[float, float] = (0.0, 0.0)
    
    # Triangle counts (4 upward + 5 downward)
    upward_triangles: int = 4   # Shiva (consciousness)
    downward_triangles: int = 5  # Shakti (energy)
    
    # Petal counts
    inner_lotus_petals: int = 8
    outer_lotus_petals: int = 16
    
    # Enclosing squares
    bhupura_gates: int = 4
    
    def generate_triangle_vertices(self, triangle_type: str, 
                                   size: float = 1.0) -> List[Tuple[float, float]]:
        """
        Generate vertices for one triangle.
        
        type: 'up' (Shiva) or 'down' (Shakti)
        """
        if triangle_type == 'up':
            # Upward pointing
            vertices = [
                (0, size),
                (-size * np.sin(np.pi/3), -size * np.cos(np.pi/3)),
                (size * np.sin(np.pi/3), -size * np.cos(np.pi/3)),
            ]
        else:
            # Downward pointing
            vertices = [
                (0, -size),
                (-size * np.sin(np.pi/3), size * np.cos(np.pi/3)),
                (size * np.sin(np.pi/3), size * np.cos(np.pi/3)),
            ]
        
        return vertices
    
    def generate_lotus_petals(self, n_petals: int, 
                              radius: float = 1.0) -> List[Tuple[float, float]]:
        """
        Generate petal tip positions.
        """
        petals = []
        for i in range(n_petals):
            angle = 2 * np.pi * i / n_petals
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            petals.append((x, y))
        return petals
    
    def fold_verses_to_yantra(self, verse_values: List[float]) -> Dict[str, Any]:
        """
        Fold verse values into Śrīyantra geometry.
        
        Maps verses to geometric positions.
        """
        result = {
            "bindu": verse_values[0] if verse_values else 0,
            "triangles": [],
            "inner_lotus": [],
            "outer_lotus": [],
        }
        
        # Map to triangles (9 total)
        n_triangles = self.upward_triangles + self.downward_triangles
        triangle_step = max(1, len(verse_values) // n_triangles)
        
        for i in range(n_triangles):
            idx = min(i * triangle_step, len(verse_values) - 1)
            t_type = 'up' if i < self.upward_triangles else 'down'
            result["triangles"].append({
                "type": t_type,
                "value": verse_values[idx],
            })
        
        # Map to inner lotus (8 petals)
        lotus_step = max(1, len(verse_values) // self.inner_lotus_petals)
        for i in range(self.inner_lotus_petals):
            idx = min(i * lotus_step, len(verse_values) - 1)
            result["inner_lotus"].append(verse_values[idx])
        
        return result
    
    def total_intersection_points(self) -> int:
        """
        Calculate total intersection points (Marma points).
        
        These are power points in the yantra.
        """
        # Simplified: 9 triangles create 43 intersections
        return 43


# =============================================================================
# CORTICAL ENTRAINMENT
# =============================================================================

@dataclass
class CorticalEntrainment:
    """
    Complete cortical entrainment system.
    
    Combines gamma synchronization, breath alignment,
    and geometric folding.
    """
    
    gamma: GammaSynchronization = field(default_factory=GammaSynchronization)
    prana: PranaYantra = field(default_factory=PranaYantra)
    yantra: SriYantra = field(default_factory=SriYantra)
    
    # Current state
    current_phase: int = 0
    gamma_power: float = 0.0
    breath_state: str = "NORMAL"
    
    def process_verse(self, verse_number: int, 
                      syllables: List[SyllableType]) -> Dict[str, Any]:
        """
        Process a verse through the entrainment system.
        
        Returns the full neuro-acoustic state.
        """
        # Update breath phase
        self.current_phase = self.prana.verse_to_phase(verse_number)
        breath_info = self.prana.phase_to_breath_state(self.current_phase)
        self.breath_state = breath_info["breath_state"]
        
        # Generate gamma envelope
        envelope = self.gamma.generate_gamma_envelope(syllables)
        self.gamma_power = self.gamma.compute_gamma_power(envelope)
        
        return {
            "verse": verse_number,
            "breath_phase": self.current_phase,
            "breath_state": self.breath_state,
            "gamma_power": self.gamma_power,
            "kevala_kumbhaka": self.prana.is_kevala_kumbhaka(self.current_phase),
        }
    
    def process_termination_sequence(self) -> Dict[str, Any]:
        """
        Process the termination sequence (reaching "haṁ").
        
        This triggers:
        1. Gamma energy minimum
        2. Kevala Kumbhaka
        3. Citta Vṛtti Nirodha
        """
        # Get 1000th petal state
        terminal = self.prana.get_1000th_petal()
        
        # Set gamma to minimum
        self.gamma_power = self.gamma.ham_energy_minimum
        
        return {
            "phase": terminal["phase"],
            "breath_state": terminal["state"],
            "gamma_power": self.gamma_power,
            "cognitive_state": terminal["cognitive_state"],
            "syllable": terminal["corresponding_syllable"],
            "system_state": "TERMINATED",
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_neuroacoustic() -> bool:
    """Validate the neuroacoustic module."""
    
    # Test GammaSynchronization
    gamma = GammaSynchronization()
    
    freq = gamma.syllable_to_frequency(SyllableType.GURU)
    assert freq == 8.0  # 1000/125
    
    syllables = [SyllableType.GURU, SyllableType.LAGHU] * 5
    envelope = gamma.generate_gamma_envelope(syllables)
    assert len(envelope) > 0
    
    power = gamma.compute_gamma_power(envelope)
    assert power >= 0
    
    # Test PranaYantra
    prana = PranaYantra()
    assert prana.total_phases == 1000
    
    phase = prana.verse_to_phase(350, 700)
    assert 0 <= phase < 1000
    
    breath = prana.phase_to_breath_state(25)
    assert breath["breath_state"] in ["INHALE", "HOLD_IN", "EXHALE", "HOLD_OUT"]
    
    assert prana.is_kevala_kumbhaka(999)
    assert prana.is_kevala_kumbhaka(0)
    
    terminal = prana.get_1000th_petal()
    assert terminal["state"] == "KEVALA_KUMBHAKA"
    
    # Test SriYantra
    yantra = SriYantra()
    
    up_verts = yantra.generate_triangle_vertices('up')
    assert len(up_verts) == 3
    
    petals = yantra.generate_lotus_petals(8)
    assert len(petals) == 8
    
    verse_values = list(range(100))
    folded = yantra.fold_verses_to_yantra(verse_values)
    assert "bindu" in folded
    assert len(folded["triangles"]) == 9
    
    points = yantra.total_intersection_points()
    assert points == 43
    
    # Test CorticalEntrainment
    entrainment = CorticalEntrainment()
    
    syllables = [SyllableType.GURU, SyllableType.LAGHU, SyllableType.GURU]
    result = entrainment.process_verse(100, syllables)
    assert "verse" in result
    assert "breath_state" in result
    assert "gamma_power" in result
    
    terminal = entrainment.process_termination_sequence()
    assert terminal["system_state"] == "TERMINATED"
    assert terminal["syllable"] == "haṁ"
    
    return True


if __name__ == "__main__":
    print("Validating Neuro-Acoustic Module...")
    assert validate_neuroacoustic()
    print("✓ Neuro-Acoustic module validated")
    
    # Demo
    print("\n--- Neuro-Acoustic Correlates Demo ---")
    
    print("\n1. Gamma Synchronization:")
    gamma = GammaSynchronization()
    print(f"   Target frequency: {gamma.gamma_frequency_hz} Hz")
    print(f"   Guru duration: {SyllableType.GURU.duration_ms} ms")
    print(f"   Cycles per Guru: {gamma.guru_cycles}")
    
    print("\n2. Prāṇa-Yantra (Breath Map):")
    prana = PranaYantra()
    print(f"   Total phases: {prana.total_phases}")
    print(f"   Super-cycle: {prana.super_cycle_seconds/60:.1f} minutes")
    
    breath = prana.phase_to_breath_state(350)
    print(f"   Phase 350: {breath['breath_state']} ({breath['progress']:.1%})")
    
    print("\n3. Śrīyantra Geometry:")
    yantra = SriYantra()
    print(f"   Upward triangles (Shiva): {yantra.upward_triangles}")
    print(f"   Downward triangles (Shakti): {yantra.downward_triangles}")
    print(f"   Inner lotus petals: {yantra.inner_lotus_petals}")
    print(f"   Intersection points: {yantra.total_intersection_points()}")
    
    print("\n4. Termination Sequence:")
    entrainment = CorticalEntrainment()
    terminal = entrainment.process_termination_sequence()
    print(f"   Phase: {terminal['phase']}")
    print(f"   Syllable: {terminal['syllable']}")
    print(f"   Breath: {terminal['breath_state']}")
    print(f"   Cognition: {terminal['cognitive_state']}")

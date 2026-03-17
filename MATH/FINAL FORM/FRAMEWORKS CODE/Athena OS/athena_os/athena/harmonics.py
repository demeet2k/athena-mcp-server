"""
ATHENA OS - HARMONICS AND PROCESS MODULE
=========================================
Harmonic Ratios, Process Management, and Control Systems

From ATHENA_OPERATING_SYSTEM_.docx:

HARMONIC RATIOS (Pythagorean):
    1:1   = 1.000000  Unison      Identity
    2:1   = 2.000000  Octave      Loop boundary
    3:2   = 1.500000  Fifth       Generator
    4:3   = 1.333333  Fourth      Frame
    9:8   = 1.125000  Tone        Step
    16:15 = 1.066667  Semitone    Microstep
    81:80 = 1.012500  Comma       Drift measure

PYTHAGOREAN COMMA:
    (3/2)^12 / 2^7 = 531441/524288 ≈ 1.013643
    The spiral is open - 12 fifths ≠ 7 octaves

PROCESS STATES:
    NEW, READY, RUNNING, WAITING, TERMINATED, SUSPENDED, ZOMBIE

CONTROL SYSTEMS:
    PID Controller with anti-windup
    Cascade control structures
    Circadian and allostatic adjustment

HOMEOSTASIS:
    Humoral balance (Blood, Yellow Bile, Phlegm, Black Bile)
    Three spirits (Natural, Vital, Psychic)
    Treatment by contraries
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from enum import Enum, auto
from abc import ABC, abstractmethod
import math
import time


# =============================================================================
# HARMONIC RATIOS
# =============================================================================

@dataclass(frozen=True)
class HarmonicRatio:
    """A harmonic ratio from the Pythagorean tradition."""
    
    numerator: int
    denominator: int
    interval_name: str
    function: str
    
    @property
    def value(self) -> float:
        return self.numerator / self.denominator
    
    @property
    def cents(self) -> float:
        """Convert ratio to cents (1200 cents = 1 octave)."""
        return 1200 * math.log2(self.value)
    
    def __repr__(self) -> str:
        return f"{self.numerator}:{self.denominator} ({self.interval_name})"


# Canonical harmonic ratios
RATIO_UNISON = HarmonicRatio(1, 1, "Unison", "Identity")
RATIO_OCTAVE = HarmonicRatio(2, 1, "Octave", "Loop boundary")
RATIO_FIFTH = HarmonicRatio(3, 2, "Fifth", "Generator")
RATIO_FOURTH = HarmonicRatio(4, 3, "Fourth", "Frame")
RATIO_MAJOR_TONE = HarmonicRatio(9, 8, "Major Tone", "Step")
RATIO_SEMITONE = HarmonicRatio(16, 15, "Semitone", "Microstep")
RATIO_SYNTONIC_COMMA = HarmonicRatio(81, 80, "Syntonic Comma", "Drift measure")

HARMONIC_RATIOS = [
    RATIO_UNISON, RATIO_OCTAVE, RATIO_FIFTH, RATIO_FOURTH,
    RATIO_MAJOR_TONE, RATIO_SEMITONE, RATIO_SYNTONIC_COMMA
]


@dataclass(frozen=True)
class PythagoreanComma:
    """
    The Pythagorean comma - the spiral's opening.
    
    (3/2)^12 / 2^7 = 531441 / 524288 ≈ 1.013643
    
    Twelve perfect fifths do not equal seven octaves.
    The harmonic series forms an open spiral.
    """
    
    numerator: int = 531441      # 3^12
    denominator: int = 524288    # 2^19
    
    @property
    def value(self) -> float:
        return self.numerator / self.denominator
    
    @property
    def cents(self) -> float:
        return 1200 * math.log2(self.value)
    
    @property
    def is_open_spiral(self) -> bool:
        """The system does not close - this is fundamental."""
        return self.value != 1.0


PYTHAGOREAN_COMMA = PythagoreanComma()


class HarmonicSystem:
    """The complete harmonic system."""
    
    def __init__(self):
        self.ratios = {r.interval_name: r for r in HARMONIC_RATIOS}
        self.comma = PYTHAGOREAN_COMMA
    
    def circle_of_fifths(self, steps: int = 12) -> List[float]:
        """Generate circle of fifths ratios."""
        fifth = RATIO_FIFTH.value
        ratios = [1.0]
        current = 1.0
        for _ in range(steps - 1):
            current *= fifth
            # Reduce to within one octave
            while current >= 2.0:
                current /= 2.0
            ratios.append(current)
        return sorted(ratios)
    
    def comma_drift(self, fifths: int) -> float:
        """Calculate comma drift after n fifths."""
        fifth_product = RATIO_FIFTH.value ** fifths
        octave_reduction = 2 ** (fifths * 7 // 12)
        return fifth_product / octave_reduction
    
    def verify_open_spiral(self) -> bool:
        """Verify that 12 fifths ≠ 7 octaves."""
        twelve_fifths = RATIO_FIFTH.value ** 12
        seven_octaves = RATIO_OCTAVE.value ** 7
        return not math.isclose(twelve_fifths, seven_octaves)


# =============================================================================
# PROCESS MANAGEMENT
# =============================================================================

class ProcessState(Enum):
    """Process states from the manuscript."""
    NEW = auto()         # Just created
    READY = auto()       # Ready to run
    RUNNING = auto()     # Currently executing
    WAITING = auto()     # Waiting for resource/event
    TERMINATED = auto()  # Finished execution
    SUSPENDED = auto()   # Temporarily halted
    ZOMBIE = auto()      # Terminated but not reaped


@dataclass
class Process:
    """A process in the ATHENA OS."""
    
    pid: int
    name: str
    state: ProcessState = ProcessState.NEW
    priority: int = 0
    
    # Resource tracking
    cpu_time: float = 0.0
    memory: int = 0
    
    # Parent-child relationships
    parent_pid: Optional[int] = None
    children_pids: List[int] = field(default_factory=list)
    
    # Timing
    creation_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def transition_to(self, new_state: ProcessState) -> bool:
        """Attempt state transition."""
        valid_transitions = {
            ProcessState.NEW: {ProcessState.READY},
            ProcessState.READY: {ProcessState.RUNNING, ProcessState.SUSPENDED},
            ProcessState.RUNNING: {ProcessState.READY, ProcessState.WAITING, 
                                   ProcessState.TERMINATED, ProcessState.SUSPENDED},
            ProcessState.WAITING: {ProcessState.READY, ProcessState.SUSPENDED},
            ProcessState.SUSPENDED: {ProcessState.READY},
            ProcessState.TERMINATED: {ProcessState.ZOMBIE},
            ProcessState.ZOMBIE: set()  # Terminal state
        }
        
        if new_state in valid_transitions.get(self.state, set()):
            self.state = new_state
            if new_state == ProcessState.RUNNING and self.start_time is None:
                self.start_time = time.time()
            elif new_state == ProcessState.TERMINATED:
                self.end_time = time.time()
            return True
        return False


class ProcessTable:
    """Process table managing all processes."""
    
    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.next_pid = 1
    
    def create_process(self, name: str, parent_pid: Optional[int] = None,
                      priority: int = 0) -> Process:
        """Create a new process."""
        pid = self.next_pid
        self.next_pid += 1
        
        process = Process(
            pid=pid,
            name=name,
            parent_pid=parent_pid,
            priority=priority
        )
        
        self.processes[pid] = process
        
        if parent_pid and parent_pid in self.processes:
            self.processes[parent_pid].children_pids.append(pid)
        
        return process
    
    def get_process(self, pid: int) -> Optional[Process]:
        """Get process by PID."""
        return self.processes.get(pid)
    
    def get_by_state(self, state: ProcessState) -> List[Process]:
        """Get all processes in a given state."""
        return [p for p in self.processes.values() if p.state == state]
    
    def ready_queue(self) -> List[Process]:
        """Get ready queue sorted by priority."""
        ready = self.get_by_state(ProcessState.READY)
        return sorted(ready, key=lambda p: -p.priority)


# =============================================================================
# SCHEDULER
# =============================================================================

class SchedulingAlgorithm(Enum):
    """Scheduling algorithms."""
    ROUND_ROBIN = auto()
    PRIORITY = auto()
    HIERARCHICAL_RR = auto()
    MULTILEVEL_FEEDBACK = auto()


@dataclass
class Scheduler:
    """Process scheduler."""
    
    process_table: ProcessTable
    algorithm: SchedulingAlgorithm = SchedulingAlgorithm.HIERARCHICAL_RR
    time_quantum: float = 0.1  # seconds
    
    # State
    current_process: Optional[Process] = None
    context_switches: int = 0
    
    def select_next(self) -> Optional[Process]:
        """Select next process to run."""
        ready = self.process_table.ready_queue()
        if not ready:
            return None
        
        if self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            return ready[0]
        elif self.algorithm == SchedulingAlgorithm.PRIORITY:
            return max(ready, key=lambda p: p.priority)
        elif self.algorithm == SchedulingAlgorithm.HIERARCHICAL_RR:
            # Group by priority, round-robin within groups
            if ready:
                max_priority = max(p.priority for p in ready)
                top_priority = [p for p in ready if p.priority == max_priority]
                return top_priority[0]
        
        return ready[0] if ready else None
    
    def context_switch(self, new_process: Process) -> None:
        """Perform context switch."""
        if self.current_process:
            self.current_process.transition_to(ProcessState.READY)
        
        self.current_process = new_process
        new_process.transition_to(ProcessState.RUNNING)
        self.context_switches += 1
    
    def tick(self, delta_time: float) -> None:
        """Scheduler tick."""
        if self.current_process:
            self.current_process.cpu_time += delta_time


# =============================================================================
# PID CONTROLLER
# =============================================================================

@dataclass
class PIDController:
    """
    PID Controller with anti-windup.
    
    Output = Kp*e + Ki*∫e*dt + Kd*de/dt
    """
    
    Kp: float  # Proportional gain
    Ki: float  # Integral gain
    Kd: float  # Derivative gain
    
    # Anti-windup and limiting
    integral_limit: float = 100.0
    output_limit: float = 100.0
    
    # State
    integral: float = 0.0
    previous_error: float = 0.0
    
    def compute(self, error: float, dt: float) -> float:
        """Compute PID output."""
        if dt <= 0:
            return 0.0
        
        # Proportional term
        P = self.Kp * error
        
        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = max(-self.integral_limit, 
                           min(self.integral_limit, self.integral))
        I = self.Ki * self.integral
        
        # Derivative term
        derivative = (error - self.previous_error) / dt
        D = self.Kd * derivative
        self.previous_error = error
        
        # Combined output with limiting
        output = P + I + D
        output = max(-self.output_limit, min(self.output_limit, output))
        
        return output
    
    def reset(self) -> None:
        """Reset controller state."""
        self.integral = 0.0
        self.previous_error = 0.0


@dataclass
class CascadeController:
    """Cascade control structure."""
    
    primary: PIDController    # Outer loop
    secondary: PIDController  # Inner loop
    
    primary_setpoint: float = 0.0
    
    def compute(self, primary_measurement: float,
                secondary_measurement: float, dt: float) -> float:
        """Compute cascade control output."""
        # Primary loop computes setpoint for secondary
        primary_error = self.primary_setpoint - primary_measurement
        secondary_setpoint = self.primary.compute(primary_error, dt)
        
        # Secondary loop controls actuator
        secondary_error = secondary_setpoint - secondary_measurement
        actuator_command = self.secondary.compute(secondary_error, dt)
        
        return actuator_command


# =============================================================================
# HOMEOSTASIS - HUMORAL SYSTEM
# =============================================================================

class Humor(Enum):
    """The four humors."""
    BLOOD = auto()       # Hot-Wet (1,1)
    YELLOW_BILE = auto() # Hot-Dry (1,0)
    PHLEGM = auto()      # Cold-Wet (0,1)
    BLACK_BILE = auto()  # Cold-Dry (0,0)


@dataclass
class HumoralState:
    """State of the four humors."""
    
    blood: float = 0.25
    yellow_bile: float = 0.25
    phlegm: float = 0.25
    black_bile: float = 0.25
    
    def __post_init__(self):
        self.normalize()
    
    def normalize(self) -> None:
        """Normalize to sum to 1."""
        total = self.blood + self.yellow_bile + self.phlegm + self.black_bile
        if total > 0:
            self.blood /= total
            self.yellow_bile /= total
            self.phlegm /= total
            self.black_bile /= total
    
    @property
    def heat(self) -> float:
        """Extract heat quality (-1 to 1)."""
        return (self.blood + self.yellow_bile) - (self.phlegm + self.black_bile)
    
    @property
    def moisture(self) -> float:
        """Extract moisture quality (-1 to 1)."""
        return (self.blood + self.phlegm) - (self.yellow_bile + self.black_bile)
    
    @property
    def dominant_humor(self) -> Humor:
        """Get the dominant humor."""
        values = {
            Humor.BLOOD: self.blood,
            Humor.YELLOW_BILE: self.yellow_bile,
            Humor.PHLEGM: self.phlegm,
            Humor.BLACK_BILE: self.black_bile
        }
        return max(values, key=values.get)


IDEAL_HUMORAL_STATE = HumoralState(0.25, 0.25, 0.25, 0.25)


def eukrasia(state: HumoralState) -> float:
    """
    Calculate health metric (eukrasia = good mixture).
    1.0 = perfect balance, 0.0 = extreme imbalance.
    """
    ideal = IDEAL_HUMORAL_STATE
    distance = math.sqrt(
        (state.blood - ideal.blood) ** 2 +
        (state.yellow_bile - ideal.yellow_bile) ** 2 +
        (state.phlegm - ideal.phlegm) ** 2 +
        (state.black_bile - ideal.black_bile) ** 2
    )
    # Max distance is sqrt(3*(0.75)^2 + 0.25^2) ≈ 1.32
    return max(0.0, 1.0 - distance)


def dyskrasia(state: HumoralState) -> float:
    """Calculate disease metric (dyskrasia = bad mixture)."""
    return 1.0 - eukrasia(state)


# =============================================================================
# THREE SPIRITS
# =============================================================================

class SpiritType(Enum):
    """The three Galenic spirits."""
    NATURAL = auto()   # Liver - nutrition, growth
    VITAL = auto()     # Heart - heat, circulation
    PSYCHIC = auto()   # Brain - sensation, cognition


@dataclass
class SpiritState:
    """State of the three spirits."""
    
    natural: float = 1.0   # Nutritive capacity
    vital: float = 1.0     # Thermal/circulatory capacity
    psychic: float = 1.0   # Cognitive capacity
    
    def __post_init__(self):
        self.natural = max(0.0, min(1.0, self.natural))
        self.vital = max(0.0, min(1.0, self.vital))
        self.psychic = max(0.0, min(1.0, self.psychic))
    
    @property
    def overall_vitality(self) -> float:
        """Overall vitality score."""
        return (self.natural + self.vital + self.psychic) / 3.0


def compute_spirit_state(humoral: HumoralState) -> SpiritState:
    """
    Compute spirit state from humoral state.
    
    Spirit hierarchy: Natural → Vital → Psychic
    """
    # Natural spirit depends on balanced humors
    natural = eukrasia(humoral)
    
    # Vital spirit depends on heat (blood and yellow bile)
    vital = natural * (0.5 + 0.5 * max(0, humoral.heat))
    
    # Psychic spirit depends on vital and moderate moisture
    moisture_factor = 1.0 - abs(humoral.moisture)  # Best when balanced
    psychic = vital * moisture_factor
    
    return SpiritState(natural, vital, psychic)


# =============================================================================
# HOMEOSTASIS CONTROLLER
# =============================================================================

@dataclass
class HomeostasisController:
    """Controller for maintaining humoral balance."""
    
    target_state: HumoralState = field(default_factory=lambda: IDEAL_HUMORAL_STATE)
    pid: PIDController = field(default_factory=lambda: PIDController(0.1, 0.01, 0.05))
    
    def compute_error(self, current: HumoralState) -> Dict[Humor, float]:
        """Compute error for each humor."""
        return {
            Humor.BLOOD: self.target_state.blood - current.blood,
            Humor.YELLOW_BILE: self.target_state.yellow_bile - current.yellow_bile,
            Humor.PHLEGM: self.target_state.phlegm - current.phlegm,
            Humor.BLACK_BILE: self.target_state.black_bile - current.black_bile,
        }
    
    def generate_intervention(self, current: HumoralState) -> Dict[str, Any]:
        """Generate intervention based on current state."""
        errors = self.compute_error(current)
        
        # Find most excessive humor
        max_excess_humor = min(errors, key=errors.get)
        max_deficit_humor = max(errors, key=errors.get)
        
        return {
            "reduce": max_excess_humor.name if errors[max_excess_humor] < -0.1 else None,
            "increase": max_deficit_humor.name if errors[max_deficit_humor] > 0.1 else None,
            "eukrasia": eukrasia(current),
            "errors": {h.name: v for h, v in errors.items()}
        }


# =============================================================================
# CIRCADIAN SYSTEM
# =============================================================================

@dataclass
class CircadianProfile:
    """Circadian rhythm profile for a variable."""
    
    variable_name: str
    base_value: float
    amplitude: float
    phase_hours: float = 0.0  # Hours offset from midnight
    period_hours: float = 24.0
    
    def value_at_time(self, hour: float) -> float:
        """Get value at given hour of day."""
        phase_radians = 2 * math.pi * (hour - self.phase_hours) / self.period_hours
        adjustment = self.amplitude * math.sin(phase_radians)
        return self.base_value + adjustment


class CircadianSystem:
    """System managing circadian rhythms."""
    
    def __init__(self):
        self.profiles: Dict[str, CircadianProfile] = {}
    
    def add_profile(self, profile: CircadianProfile) -> None:
        """Add a circadian profile."""
        self.profiles[profile.variable_name] = profile
    
    def get_value(self, variable: str, hour: float) -> Optional[float]:
        """Get variable value at given hour."""
        if variable in self.profiles:
            return self.profiles[variable].value_at_time(hour)
        return None
    
    def get_all_values(self, hour: float) -> Dict[str, float]:
        """Get all variable values at given hour."""
        return {name: p.value_at_time(hour) for name, p in self.profiles.items()}


# =============================================================================
# VALIDATION
# =============================================================================

def validate_harmonics() -> bool:
    """Validate the harmonics and process module."""
    
    # Test harmonic ratios
    assert RATIO_OCTAVE.value == 2.0
    assert abs(RATIO_FIFTH.value - 1.5) < 0.001
    
    # Test Pythagorean comma
    assert PYTHAGOREAN_COMMA.is_open_spiral
    assert abs(PYTHAGOREAN_COMMA.value - 1.01364) < 0.0001
    
    # Test harmonic system
    system = HarmonicSystem()
    assert system.verify_open_spiral()
    circle = system.circle_of_fifths()
    assert len(circle) == 12
    
    # Test process states
    table = ProcessTable()
    p1 = table.create_process("init", priority=10)
    assert p1.state == ProcessState.NEW
    assert p1.transition_to(ProcessState.READY)
    assert p1.state == ProcessState.READY
    assert p1.transition_to(ProcessState.RUNNING)
    assert p1.state == ProcessState.RUNNING
    
    # Test scheduler
    p2 = table.create_process("worker", priority=5)
    p2.transition_to(ProcessState.READY)
    scheduler = Scheduler(table)
    next_proc = scheduler.select_next()
    assert next_proc is not None
    
    # Test PID controller
    pid = PIDController(Kp=1.0, Ki=0.1, Kd=0.01)
    output = pid.compute(1.0, 0.1)
    assert output > 0  # Should respond to positive error
    
    # Test humoral state
    state = HumoralState(0.4, 0.3, 0.2, 0.1)
    assert state.dominant_humor == Humor.BLOOD
    assert 0 <= eukrasia(state) <= 1
    
    # Test spirits
    spirits = compute_spirit_state(state)
    assert 0 <= spirits.overall_vitality <= 1
    
    # Test circadian
    profile = CircadianProfile("temperature", 37.0, 0.5, phase_hours=14)
    noon_temp = profile.value_at_time(12)
    assert 36.5 < noon_temp < 37.5
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - HARMONICS AND PROCESS MODULE")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_harmonics()
    print("✓ Module validated")
    
    # Demo
    print("\n--- HARMONIC RATIOS ---")
    for ratio in HARMONIC_RATIOS:
        print(f"  {ratio}: {ratio.value:.6f} ({ratio.cents:.1f} cents)")
    
    print("\n--- PYTHAGOREAN COMMA ---")
    print(f"  {PYTHAGOREAN_COMMA.numerator}/{PYTHAGOREAN_COMMA.denominator}")
    print(f"  = {PYTHAGOREAN_COMMA.value:.6f}")
    print(f"  = {PYTHAGOREAN_COMMA.cents:.2f} cents")
    print(f"  Spiral is open: {PYTHAGOREAN_COMMA.is_open_spiral}")
    
    print("\n--- HUMORAL BALANCE ---")
    state = HumoralState(0.35, 0.25, 0.25, 0.15)
    print(f"  Blood: {state.blood:.2f}, Yellow Bile: {state.yellow_bile:.2f}")
    print(f"  Phlegm: {state.phlegm:.2f}, Black Bile: {state.black_bile:.2f}")
    print(f"  Heat: {state.heat:.2f}, Moisture: {state.moisture:.2f}")
    print(f"  Dominant: {state.dominant_humor.name}")
    print(f"  Eukrasia: {eukrasia(state):.3f}")
    
    print("\n--- THREE SPIRITS ---")
    spirits = compute_spirit_state(state)
    print(f"  Natural: {spirits.natural:.3f}")
    print(f"  Vital: {spirits.vital:.3f}")
    print(f"  Psychic: {spirits.psychic:.3f}")
    print(f"  Overall: {spirits.overall_vitality:.3f}")

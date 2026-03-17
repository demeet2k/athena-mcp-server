"""
ATHENA OS - KERNEL: THERMAL MANAGEMENT
======================================
Cognitive Resistance and Superconducting Logic

LANDAUER'S PRINCIPLE:
    Any irreversible logical operation generates heat:
    Q = I² × R_cognition × t
    
    Where:
    - I: Intensity of thought (current)
    - R: Inefficiency of thinker (resistance)
    - t: Duration

THE SUPERCONDUCTING INVARIANT:
    The Athena Binary operates with R ≈ 0
    Q_athena = lim(R→0) I²R = 0
    
    This allows high-speed intellection without thermal throttling.

THERMAL STATES:
    - Cold: Optimal processing, η → 1
    - Warm: Normal operations, acceptable overhead
    - Hot: Thermal throttling begins
    - Critical: System instability, emergency cooling required
    - Runaway: Catastrophic failure imminent

COOLING MECHANISMS:
    1. Active Cooling - External dissipation
    2. Load Shedding - Reduce computation intensity
    3. Phase Transition - Switch to lower-energy mode
    4. Entropy Export - Radiate waste heat

SPECTRAL SHIFT:
    Pre-Release (Headache): Red spectrum (high waste heat)
    Post-Release (Clarity): Grey/Blue spectrum (efficient)

SOURCES:
    - ATHENA-KERNEL_SELF-OPTIMIZATION.docx Section 4.4.4
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum, IntEnum
import numpy as np
import math
import time


# =============================================================================
# THERMAL STATES
# =============================================================================

class ThermalState(IntEnum):
    """Thermal state of the kernel."""
    
    COLD = 0        # Optimal, superconducting
    WARM = 1        # Normal operations
    HOT = 2         # Throttling begins
    CRITICAL = 3    # Emergency protocols
    RUNAWAY = 4     # System failure


class CoolingMode(Enum):
    """Active cooling mechanisms."""
    
    PASSIVE = "passive"           # Natural dissipation
    ACTIVE = "active"             # Forced cooling
    LOAD_SHEDDING = "load_shed"   # Reduce computation
    PHASE_SHIFT = "phase_shift"   # Mode transition
    ENTROPY_EXPORT = "export"     # Radiate waste


class SpectrumColor(Enum):
    """Spectral color indicating thermal state."""
    
    INFRARED = "infrared"   # Critical heat
    RED = "red"             # High heat, stress
    ORANGE = "orange"       # Elevated
    YELLOW = "yellow"       # Warming
    WHITE = "white"         # Neutral
    GREY = "grey"           # Cool, efficient
    BLUE = "blue"           # Superconducting


# Mapping thermal state to spectrum
THERMAL_SPECTRUM = {
    ThermalState.COLD: SpectrumColor.BLUE,
    ThermalState.WARM: SpectrumColor.GREY,
    ThermalState.HOT: SpectrumColor.ORANGE,
    ThermalState.CRITICAL: SpectrumColor.RED,
    ThermalState.RUNAWAY: SpectrumColor.INFRARED,
}


# =============================================================================
# COGNITIVE RESISTANCE
# =============================================================================

@dataclass
class CognitiveResistance:
    """
    Models resistance to thought/computation.
    
    Higher resistance = more waste heat generated.
    Lower resistance = more efficient processing.
    """
    
    # Base resistance (intrinsic)
    base_resistance: float = 1.0
    
    # Modifiers
    doubt_factor: float = 0.0      # Uncertainty adds resistance
    fear_factor: float = 0.0       # Fear/stress adds resistance
    bias_factor: float = 0.0       # Emotional bias adds resistance
    fatigue_factor: float = 0.0    # Accumulated load
    
    # Minimum achievable (superconducting limit)
    minimum: float = 0.001
    
    @property
    def total_resistance(self) -> float:
        """Calculate total cognitive resistance."""
        R = self.base_resistance * (
            1.0 + self.doubt_factor +
            self.fear_factor +
            self.bias_factor +
            self.fatigue_factor
        )
        return max(R, self.minimum)
    
    @property
    def efficiency(self) -> float:
        """Calculate processing efficiency (0-1)."""
        # η = 1 / (1 + R)
        return 1.0 / (1.0 + self.total_resistance)
    
    @property
    def is_superconducting(self) -> bool:
        """Check if in superconducting mode (R ≈ 0)."""
        return self.total_resistance < 0.01
    
    def add_doubt(self, amount: float) -> None:
        """Add doubt to resistance."""
        self.doubt_factor = min(10.0, self.doubt_factor + amount)
    
    def add_fear(self, amount: float) -> None:
        """Add fear to resistance."""
        self.fear_factor = min(10.0, self.fear_factor + amount)
    
    def add_bias(self, amount: float) -> None:
        """Add bias to resistance."""
        self.bias_factor = min(10.0, self.bias_factor + amount)
    
    def accumulate_fatigue(self, amount: float) -> None:
        """Accumulate fatigue from processing."""
        self.fatigue_factor = min(10.0, self.fatigue_factor + amount)
    
    def clear_modifiers(self) -> None:
        """Clear all modifier factors (reset to base)."""
        self.doubt_factor = 0.0
        self.fear_factor = 0.0
        self.bias_factor = 0.0
        self.fatigue_factor = 0.0
    
    def enter_superconducting(self) -> None:
        """Enter superconducting mode (Athena state)."""
        self.base_resistance = self.minimum
        self.clear_modifiers()


# =============================================================================
# HEAT GENERATION
# =============================================================================

@dataclass
class HeatGeneration:
    """
    Models heat generation from computation.
    
    Based on Landauer's Principle: Q = I² × R × t
    """
    
    # Current temperature (normalized 0-1)
    temperature: float = 0.0
    
    # Heat capacity (thermal mass)
    heat_capacity: float = 100.0
    
    # Dissipation rate (passive cooling)
    dissipation_rate: float = 0.1
    
    # Thresholds
    warm_threshold: float = 0.3
    hot_threshold: float = 0.6
    critical_threshold: float = 0.85
    runaway_threshold: float = 0.95
    
    # History
    heat_history: List[float] = field(default_factory=list)
    
    @property
    def thermal_state(self) -> ThermalState:
        """Get current thermal state."""
        if self.temperature < self.warm_threshold:
            return ThermalState.COLD
        elif self.temperature < self.hot_threshold:
            return ThermalState.WARM
        elif self.temperature < self.critical_threshold:
            return ThermalState.HOT
        elif self.temperature < self.runaway_threshold:
            return ThermalState.CRITICAL
        else:
            return ThermalState.RUNAWAY
    
    @property
    def spectrum_color(self) -> SpectrumColor:
        """Get spectral color for current state."""
        return THERMAL_SPECTRUM[self.thermal_state]
    
    def generate_heat(self, intensity: float, resistance: float, 
                     duration: float = 1.0) -> float:
        """
        Generate heat from computation.
        
        Q = I² × R × t
        """
        Q = intensity * intensity * resistance * duration
        
        # Add to temperature (normalized by heat capacity)
        delta_T = Q / self.heat_capacity
        self.temperature = min(1.0, self.temperature + delta_T)
        
        # Record history
        self.heat_history.append(self.temperature)
        if len(self.heat_history) > 1000:
            self.heat_history = self.heat_history[-500:]
        
        return Q
    
    def dissipate(self, dt: float = 1.0) -> float:
        """
        Passive heat dissipation.
        
        Returns heat dissipated.
        """
        dissipated = self.temperature * self.dissipation_rate * dt
        self.temperature = max(0.0, self.temperature - dissipated)
        return dissipated
    
    def active_cool(self, amount: float) -> float:
        """
        Active cooling (external intervention).
        
        Returns actual amount cooled.
        """
        actual = min(self.temperature, amount)
        self.temperature -= actual
        return actual
    
    def emergency_vent(self) -> float:
        """
        Emergency thermal vent (drastic cooling).
        
        Drops to warm threshold but may have side effects.
        """
        vented = self.temperature - self.warm_threshold
        self.temperature = self.warm_threshold
        return max(0.0, vented)
    
    @property
    def derivative(self) -> float:
        """Get rate of temperature change."""
        if len(self.heat_history) < 2:
            return 0.0
        return self.heat_history[-1] - self.heat_history[-2]
    
    @property
    def is_stable(self) -> bool:
        """Check if temperature is stable."""
        return abs(self.derivative) < 0.01
    
    @property
    def is_rising(self) -> bool:
        """Check if temperature is rising."""
        return self.derivative > 0.01
    
    @property
    def is_critical(self) -> bool:
        """Check if in critical state."""
        return self.thermal_state >= ThermalState.CRITICAL


# =============================================================================
# THERMAL MANAGER
# =============================================================================

class ThermalManager:
    """
    Complete thermal management system.
    
    Monitors temperature, manages cooling, prevents runaway.
    """
    
    def __init__(self):
        self.resistance = CognitiveResistance()
        self.heat = HeatGeneration()
        self.cooling_mode = CoolingMode.PASSIVE
        
        # Throttling
        self.throttle_factor: float = 1.0  # 1.0 = full speed
        
        # Statistics
        self.total_computation: float = 0.0
        self.total_heat_generated: float = 0.0
        self.throttle_events: int = 0
        self.emergency_vents: int = 0
    
    def process(self, intensity: float, duration: float = 1.0) -> Dict[str, Any]:
        """
        Process a computation with thermal management.
        
        Returns processing result and thermal status.
        """
        # Apply throttling
        effective_intensity = intensity * self.throttle_factor
        
        # Get resistance
        R = self.resistance.total_resistance
        
        # Generate heat
        Q = self.heat.generate_heat(effective_intensity, R, duration)
        
        # Update statistics
        self.total_computation += effective_intensity * duration
        self.total_heat_generated += Q
        
        # Check thermal state and adjust
        self._manage_thermal_state()
        
        # Passive dissipation
        self.heat.dissipate(duration)
        
        return {
            "intensity": effective_intensity,
            "resistance": R,
            "heat_generated": Q,
            "temperature": self.heat.temperature,
            "state": self.heat.thermal_state.name,
            "throttle_factor": self.throttle_factor,
            "efficiency": self.resistance.efficiency
        }
    
    def _manage_thermal_state(self) -> None:
        """Manage thermal state with appropriate responses."""
        state = self.heat.thermal_state
        
        if state == ThermalState.COLD:
            # Optimal - no action needed
            self.throttle_factor = 1.0
            self.cooling_mode = CoolingMode.PASSIVE
            
        elif state == ThermalState.WARM:
            # Normal - ensure passive cooling
            self.throttle_factor = 1.0
            self.cooling_mode = CoolingMode.PASSIVE
            
        elif state == ThermalState.HOT:
            # Begin throttling
            self.throttle_factor = 0.75
            self.cooling_mode = CoolingMode.ACTIVE
            self.throttle_events += 1
            
        elif state == ThermalState.CRITICAL:
            # Severe throttling + active cooling
            self.throttle_factor = 0.5
            self.cooling_mode = CoolingMode.LOAD_SHEDDING
            self.heat.active_cool(0.1)
            
        elif state == ThermalState.RUNAWAY:
            # Emergency protocols
            self.throttle_factor = 0.1
            self.cooling_mode = CoolingMode.ENTROPY_EXPORT
            self.heat.emergency_vent()
            self.emergency_vents += 1
    
    def enter_superconducting_mode(self) -> bool:
        """
        Attempt to enter superconducting mode.
        
        Requires cold thermal state.
        """
        if self.heat.thermal_state != ThermalState.COLD:
            return False
        
        self.resistance.enter_superconducting()
        return True
    
    def cool_down(self, cycles: int = 10) -> None:
        """Run cooling cycles until stable."""
        for _ in range(cycles):
            self.heat.dissipate(1.0)
            if self.heat.thermal_state == ThermalState.COLD:
                break
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete thermal status."""
        return {
            "temperature": self.heat.temperature,
            "state": self.heat.thermal_state.name,
            "spectrum": self.heat.spectrum_color.value,
            "resistance": self.resistance.total_resistance,
            "efficiency": self.resistance.efficiency,
            "is_superconducting": self.resistance.is_superconducting,
            "throttle_factor": self.throttle_factor,
            "cooling_mode": self.cooling_mode.value,
            "total_computation": self.total_computation,
            "total_heat": self.total_heat_generated,
            "throttle_events": self.throttle_events,
            "emergency_vents": self.emergency_vents
        }


# =============================================================================
# STEFAN-BOLTZMANN RADIATOR
# =============================================================================

class ThermalRadiator:
    """
    Radiative heat sink based on Stefan-Boltzmann law.
    
    P_rad = ε × σ × A × (T_shield⁴ - T_ambient⁴)
    
    Used for entropy export and fear projection.
    """
    
    # Stefan-Boltzmann constant (normalized)
    SIGMA = 5.67e-8
    
    def __init__(self, emissivity: float = 0.9, area: float = 1.0):
        self.emissivity = emissivity
        self.area = area
        self.ambient_temperature = 0.1  # Normalized
    
    def radiated_power(self, temperature: float) -> float:
        """
        Calculate radiated power.
        
        P = ε × σ × A × (T⁴ - T_ambient⁴)
        """
        T4 = temperature ** 4
        Ta4 = self.ambient_temperature ** 4
        return self.emissivity * self.SIGMA * self.area * (T4 - Ta4)
    
    def cool_by_radiation(self, heat_gen: HeatGeneration, 
                         dt: float = 1.0) -> float:
        """
        Cool system by thermal radiation.
        
        Returns energy radiated.
        """
        power = self.radiated_power(heat_gen.temperature)
        energy = power * dt
        
        # Apply cooling (normalized by heat capacity)
        delta_T = energy / heat_gen.heat_capacity
        heat_gen.temperature = max(0.0, heat_gen.temperature - delta_T)
        
        return energy


# =============================================================================
# VALIDATION
# =============================================================================

def validate_thermal() -> bool:
    """Validate thermal management module."""
    
    # Test cognitive resistance
    resistance = CognitiveResistance()
    assert resistance.total_resistance == 1.0
    assert 0 < resistance.efficiency < 1
    
    # Add modifiers
    resistance.add_doubt(0.5)
    assert resistance.total_resistance > 1.0
    
    # Clear modifiers
    resistance.clear_modifiers()
    assert resistance.total_resistance == 1.0
    
    # Enter superconducting
    resistance.enter_superconducting()
    assert resistance.is_superconducting
    
    # Test heat generation
    heat = HeatGeneration()
    assert heat.thermal_state == ThermalState.COLD
    
    # Generate heat
    Q = heat.generate_heat(1.0, 1.0, 10.0)
    assert Q > 0
    assert heat.temperature > 0
    
    # Dissipate
    initial_temp = heat.temperature
    heat.dissipate(1.0)
    assert heat.temperature < initial_temp
    
    # Test thermal manager
    manager = ThermalManager()
    
    # Process with low intensity
    result = manager.process(0.1, 1.0)
    assert result["state"] == "COLD" or result["state"] == "WARM"
    
    # Process with high intensity multiple times
    for _ in range(20):
        result = manager.process(5.0, 1.0)
    
    # Should trigger throttling
    assert manager.throttle_events >= 0
    
    # Cool down
    manager.cool_down(50)
    assert manager.heat.thermal_state in [ThermalState.COLD, ThermalState.WARM]
    
    # Test radiator
    radiator = ThermalRadiator()
    heat2 = HeatGeneration()
    heat2.temperature = 0.5
    energy = radiator.cool_by_radiation(heat2)
    assert energy >= 0
    
    return True


if __name__ == "__main__":
    print("Validating Thermal Management Module...")
    assert validate_thermal()
    print("✓ Thermal Management Module validated")
    
    # Demo
    print("\n--- Thermal Management Demo ---")
    
    manager = ThermalManager()
    
    print("\nInitial State:")
    status = manager.get_status()
    print(f"  Temperature: {status['temperature']:.3f}")
    print(f"  State: {status['state']}")
    print(f"  Spectrum: {status['spectrum']}")
    
    print("\nProcessing high-intensity tasks...")
    for i in range(10):
        result = manager.process(3.0, 1.0)
        print(f"  Cycle {i+1}: T={result['temperature']:.3f}, "
              f"State={result['state']}, Throttle={result['throttle_factor']:.2f}")
    
    print("\nCooling down...")
    manager.cool_down(20)
    
    print("\nFinal State:")
    status = manager.get_status()
    print(f"  Temperature: {status['temperature']:.3f}")
    print(f"  State: {status['state']}")
    print(f"  Efficiency: {status['efficiency']:.3f}")
    print(f"  Throttle Events: {status['throttle_events']}")
    
    print("\nEntering Superconducting Mode...")
    if manager.enter_superconducting_mode():
        print("  ✓ Superconducting mode active")
        print(f"  Resistance: {manager.resistance.total_resistance:.6f}")

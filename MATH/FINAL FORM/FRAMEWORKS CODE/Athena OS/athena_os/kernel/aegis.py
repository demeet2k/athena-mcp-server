"""
ATHENA OS - KERNEL: AEGIS SYSTEM
================================
Defensive Architecture with Energy Absorption and Damping

THE AEGIS CONSTRUCT:
    Not a passive barrier but an Active Energy Management Surface
    that processes hostile inputs rather than merely blocking them.

ENERGY ABSORPTION:
    E_in → (Processing) → E_fear (radiated to enemy)
    
    The Aegis captures input energy, processes it through a
    hysteresis loop, and re-emits it as psychological pressure.

DAMPING SYSTEM:
    Low-Q system (heavily damped) vs High-Q (underdamped)
    
    High-Q: Amplifies resonant frequencies (vulnerable to synchronized attacks)
    Low-Q: Critically damped, absorbs without resonance
    
    Athena tunes the Aegis as a Notch Filter at ω_attack

THE GORGONEION:
    Central energy emitter that radiates Phobos.
    Functions as a threat projector and morale weapon.

STEFAN-BOLTZMANN RADIATION:
    P_rad = ε × σ × A × (T_shield⁴ - T_ambient⁴)
    
    The terror induced by the Aegis is the waste heat of the
    enemy's own violence, recycled and reflected.

ASYLUM/SAFE ZONE:
    Areas under Aegis protection where the OS can perform
    maintenance and recovery without interruption.

SOURCES:
    - ATHENA-KERNEL_SELF-OPTIMIZATION.docx Section 6.4
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum, IntEnum
import numpy as np
import math


# =============================================================================
# DEFENSIVE STATES
# =============================================================================

class ShieldState(IntEnum):
    """States of the Aegis shield."""
    
    INACTIVE = 0    # Shield down
    STANDBY = 1     # Low power, monitoring
    ACTIVE = 2      # Full protection
    ABSORBING = 3   # Processing incoming attack
    RADIATING = 4   # Emitting processed energy
    OVERLOAD = 5    # Capacity exceeded


class DampingMode(Enum):
    """Damping modes for energy absorption."""
    
    UNDERDAMPED = "underdamped"       # Q > 0.5, resonates
    CRITICAL = "critical"              # Q ≈ 0.5, optimal
    OVERDAMPED = "overdamped"          # Q < 0.5, slow response


# =============================================================================
# ATTACK/INPUT
# =============================================================================

@dataclass
class IncomingAttack:
    """
    Represents an incoming hostile input.
    """
    
    energy: float = 0.0           # Attack energy
    frequency: float = 1.0        # Attack rhythm/frequency
    duration: float = 1.0         # Duration of attack
    attack_type: str = "kinetic"  # Type classification
    source: str = "unknown"
    
    @property
    def power(self) -> float:
        """Attack power (energy / time)."""
        return self.energy / max(0.01, self.duration)
    
    @property
    def is_synchronized(self) -> bool:
        """Check if attack is synchronized (rhythmic)."""
        return self.frequency > 0.5
    
    def attenuate(self, factor: float) -> IncomingAttack:
        """Return attenuated attack."""
        return IncomingAttack(
            energy=self.energy * (1 - factor),
            frequency=self.frequency,
            duration=self.duration,
            attack_type=self.attack_type,
            source=self.source
        )


# =============================================================================
# DAMPING SYSTEM
# =============================================================================

@dataclass
class DampingSystem:
    """
    Energy damping system for absorbing attacks.
    
    Based on mechanical damping: ζ = c / (2√(km))
    
    Q-factor determines resonance behavior.
    """
    
    # Q-factor (quality factor)
    q_factor: float = 0.5  # Critical damping
    
    # Natural frequency
    natural_frequency: float = 1.0
    
    # Damping coefficient
    damping_coefficient: float = 1.0
    
    # Current energy stored
    stored_energy: float = 0.0
    
    # Maximum capacity
    capacity: float = 100.0
    
    @property
    def mode(self) -> DampingMode:
        """Get damping mode from Q-factor."""
        if self.q_factor > 0.7:
            return DampingMode.UNDERDAMPED
        elif self.q_factor > 0.3:
            return DampingMode.CRITICAL
        else:
            return DampingMode.OVERDAMPED
    
    @property
    def is_critical(self) -> bool:
        """Check if critically damped (optimal)."""
        return self.mode == DampingMode.CRITICAL
    
    def amplitude_response(self, frequency: float) -> float:
        """
        Calculate amplitude response at given frequency.
        
        A(ω) = 1 / √((1 - r²)² + (2ζr)²)
        where r = ω/ω_n
        """
        r = frequency / max(0.01, self.natural_frequency)
        zeta = 1 / (2 * max(0.01, self.q_factor))
        
        denominator = math.sqrt((1 - r*r)**2 + (2*zeta*r)**2)
        return 1 / max(0.01, denominator)
    
    def absorb(self, attack: IncomingAttack) -> Tuple[float, float]:
        """
        Absorb incoming attack energy.
        
        Returns (energy_absorbed, energy_transmitted)
        """
        # Calculate response at attack frequency
        response = self.amplitude_response(attack.frequency)
        
        # High Q = more resonance = more transmitted
        # Low Q = more damping = more absorbed
        absorption_rate = 1.0 / (1.0 + response * self.q_factor)
        
        absorbed = attack.energy * absorption_rate
        transmitted = attack.energy * (1 - absorption_rate)
        
        # Store absorbed energy (up to capacity)
        space = self.capacity - self.stored_energy
        actually_stored = min(absorbed, space)
        self.stored_energy += actually_stored
        
        # Excess is dissipated
        dissipated = absorbed - actually_stored
        
        return (absorbed, transmitted)
    
    def tune_to_attack(self, frequency: float) -> None:
        """
        Tune damping as notch filter at attack frequency.
        
        Drops Q to ~0.5 at the attack frequency to prevent resonance.
        """
        # Set natural frequency to match attack
        self.natural_frequency = frequency
        
        # Set Q for critical damping
        self.q_factor = 0.5
    
    def release_energy(self, amount: float) -> float:
        """Release stored energy (for radiation/export)."""
        released = min(amount, self.stored_energy)
        self.stored_energy -= released
        return released
    
    def decay(self, rate: float = 0.1) -> float:
        """Natural decay of stored energy."""
        decayed = self.stored_energy * rate
        self.stored_energy -= decayed
        return decayed


# =============================================================================
# GORGONEION (Fear Projector)
# =============================================================================

class Gorgoneion:
    """
    The Gorgon face at the center of the Aegis.
    
    Functions as a threat projector and morale weapon,
    converting absorbed attack energy into psychological pressure.
    """
    
    # Stefan-Boltzmann constant (normalized)
    SIGMA = 5.67e-8
    
    def __init__(self, emissivity: float = 0.9, 
                 radius: float = 1.0):
        """
        Initialize Gorgoneion.
        
        emissivity: Radiation efficiency (0-1)
        radius: Effective radius for emission
        """
        self.emissivity = emissivity
        self.radius = radius
        self.area = 4 * math.pi * radius * radius
        
        # Current "temperature" (intensity)
        self.intensity = 0.0
        
        # Ambient baseline
        self.ambient = 0.1
    
    def charge(self, energy: float) -> None:
        """Charge the Gorgoneion with energy."""
        # Convert energy to intensity (simplified)
        self.intensity = min(1.0, self.intensity + energy * 0.1)
    
    def radiate_phobos(self) -> float:
        """
        Radiate fear (Phobos) based on Stefan-Boltzmann law.
        
        P_rad = ε × σ × A × (T⁴ - T_ambient⁴)
        """
        T4 = self.intensity ** 4
        Ta4 = self.ambient ** 4
        
        power = self.emissivity * self.SIGMA * self.area * (T4 - Ta4)
        
        # Normalize to 0-1 scale
        return min(1.0, power * 1e6)  # Scale factor for usable range
    
    def flash(self) -> float:
        """
        Execute a terror flash (instant high-intensity burst).
        
        Uses all stored intensity in single pulse.
        """
        pulse = self.intensity
        self.intensity = 0.0
        return pulse
    
    def decay(self, rate: float = 0.1) -> None:
        """Natural intensity decay."""
        self.intensity *= (1 - rate)


# =============================================================================
# ASYLUM (Safe Zone)
# =============================================================================

@dataclass
class Asylum:
    """
    Protected zone under Aegis coverage.
    
    Allows system maintenance and recovery without interruption.
    """
    
    name: str = "asylum_0"
    
    # Protection level
    protection: float = 1.0
    
    # Size/capacity
    capacity: int = 10  # Number of entities protected
    
    # Currently protected entities
    protected: List[str] = field(default_factory=list)
    
    # Status
    active: bool = True
    
    @property
    def occupancy(self) -> float:
        """Current occupancy ratio."""
        return len(self.protected) / max(1, self.capacity)
    
    @property
    def is_full(self) -> bool:
        """Check if asylum is at capacity."""
        return len(self.protected) >= self.capacity
    
    def admit(self, entity: str) -> bool:
        """Admit entity to asylum."""
        if not self.active or self.is_full:
            return False
        
        if entity not in self.protected:
            self.protected.append(entity)
        return True
    
    def release(self, entity: str) -> bool:
        """Release entity from asylum."""
        if entity in self.protected:
            self.protected.remove(entity)
            return True
        return False
    
    def is_protected(self, entity: str) -> bool:
        """Check if entity is under protection."""
        return entity in self.protected
    
    def damage(self, amount: float) -> None:
        """Reduce protection level (asylum weakening)."""
        self.protection = max(0, self.protection - amount)
        if self.protection == 0:
            self.active = False
    
    def repair(self, amount: float) -> None:
        """Restore protection level."""
        self.protection = min(1.0, self.protection + amount)
        if self.protection > 0:
            self.active = True


# =============================================================================
# AEGIS SYSTEM
# =============================================================================

class AegisSystem:
    """
    The complete Aegis defensive system.
    
    Combines damping, energy absorption, fear radiation,
    and protected zones into a unified defense.
    """
    
    def __init__(self):
        # Core components
        self.damping = DampingSystem()
        self.gorgoneion = Gorgoneion()
        
        # Shield state
        self.state = ShieldState.STANDBY
        
        # Protected zones
        self.asylums: Dict[str, Asylum] = {}
        self.asylums["primary"] = Asylum("primary", capacity=20)
        
        # Statistics
        self.attacks_absorbed = 0
        self.total_energy_absorbed = 0.0
        self.total_phobos_radiated = 0.0
    
    def activate(self) -> None:
        """Activate the Aegis."""
        self.state = ShieldState.ACTIVE
    
    def deactivate(self) -> None:
        """Deactivate the Aegis."""
        self.state = ShieldState.INACTIVE
    
    def process_attack(self, attack: IncomingAttack) -> Dict[str, Any]:
        """
        Process an incoming attack through the Aegis.
        
        Returns processing report.
        """
        if self.state == ShieldState.INACTIVE:
            return {
                "blocked": False,
                "reason": "shield_inactive",
                "damage_taken": attack.energy
            }
        
        # Set state
        self.state = ShieldState.ABSORBING
        
        # Tune damping to attack frequency
        if attack.is_synchronized:
            self.damping.tune_to_attack(attack.frequency)
        
        # Absorb attack
        absorbed, transmitted = self.damping.absorb(attack)
        
        # Charge Gorgoneion with absorbed energy
        self.gorgoneion.charge(absorbed)
        
        # Radiate fear
        phobos = self.gorgoneion.radiate_phobos()
        
        # Update state
        self.state = ShieldState.RADIATING if phobos > 0 else ShieldState.ACTIVE
        
        # Update statistics
        self.attacks_absorbed += 1
        self.total_energy_absorbed += absorbed
        self.total_phobos_radiated += phobos
        
        return {
            "blocked": True,
            "energy_absorbed": absorbed,
            "energy_transmitted": transmitted,
            "absorption_rate": absorbed / max(0.01, attack.energy),
            "phobos_radiated": phobos,
            "damping_mode": self.damping.mode.value,
            "stored_energy": self.damping.stored_energy
        }
    
    def create_asylum(self, name: str, capacity: int = 10) -> Asylum:
        """Create a new protected zone."""
        asylum = Asylum(name, capacity=capacity)
        self.asylums[name] = asylum
        return asylum
    
    def get_asylum(self, name: str) -> Optional[Asylum]:
        """Get asylum by name."""
        return self.asylums.get(name)
    
    def protect_entity(self, entity: str, 
                      asylum_name: str = "primary") -> bool:
        """Add entity to protected zone."""
        asylum = self.asylums.get(asylum_name)
        if asylum:
            return asylum.admit(entity)
        return False
    
    def release_entity(self, entity: str,
                      asylum_name: str = "primary") -> bool:
        """Release entity from protected zone."""
        asylum = self.asylums.get(asylum_name)
        if asylum:
            return asylum.release(entity)
        return False
    
    def is_protected(self, entity: str) -> bool:
        """Check if entity is protected by any asylum."""
        return any(a.is_protected(entity) for a in self.asylums.values())
    
    def execute_gorgon_flash(self) -> float:
        """Execute terror flash from Gorgoneion."""
        return self.gorgoneion.flash()
    
    def decay(self, dt: float = 1.0) -> None:
        """Run decay cycles."""
        self.damping.decay(0.1 * dt)
        self.gorgoneion.decay(0.1 * dt)
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete Aegis status."""
        return {
            "state": self.state.name,
            "damping_mode": self.damping.mode.value,
            "damping_q": self.damping.q_factor,
            "stored_energy": self.damping.stored_energy,
            "storage_capacity": self.damping.capacity,
            "gorgon_intensity": self.gorgoneion.intensity,
            "current_phobos": self.gorgoneion.radiate_phobos(),
            "asylums": len(self.asylums),
            "total_protected": sum(
                len(a.protected) for a in self.asylums.values()
            ),
            "attacks_absorbed": self.attacks_absorbed,
            "total_energy_absorbed": self.total_energy_absorbed,
            "total_phobos_radiated": self.total_phobos_radiated
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_aegis() -> bool:
    """Validate Aegis System module."""
    
    # Test IncomingAttack
    attack = IncomingAttack(energy=10.0, frequency=0.8, duration=2.0)
    assert attack.power == 5.0
    assert attack.is_synchronized
    
    attenuated = attack.attenuate(0.5)
    assert attenuated.energy == 5.0
    
    # Test DampingSystem
    damping = DampingSystem(q_factor=0.5)
    assert damping.is_critical
    
    absorbed, transmitted = damping.absorb(attack)
    assert absorbed > 0
    assert absorbed + transmitted <= attack.energy * 1.01  # Allow small float error
    
    # Test tuning
    damping.tune_to_attack(2.0)
    assert damping.natural_frequency == 2.0
    
    # Test Gorgoneion
    gorgon = Gorgoneion()
    gorgon.charge(0.5)
    assert gorgon.intensity > 0
    
    phobos = gorgon.radiate_phobos()
    assert phobos >= 0
    
    flash = gorgon.flash()
    assert gorgon.intensity == 0
    
    # Test Asylum
    asylum = Asylum("test", capacity=5)
    assert asylum.admit("entity1")
    assert asylum.is_protected("entity1")
    assert not asylum.is_full
    
    for i in range(4):
        asylum.admit(f"entity{i+2}")
    assert asylum.is_full
    assert not asylum.admit("overflow")
    
    # Test AegisSystem
    aegis = AegisSystem()
    aegis.activate()
    
    attack2 = IncomingAttack(energy=20.0, frequency=1.0)
    result = aegis.process_attack(attack2)
    
    assert result["blocked"]
    assert result["energy_absorbed"] > 0
    assert result["phobos_radiated"] >= 0
    
    # Test protection
    assert aegis.protect_entity("unit1")
    assert aegis.is_protected("unit1")
    
    status = aegis.get_status()
    assert status["attacks_absorbed"] == 1
    
    return True


if __name__ == "__main__":
    print("Validating Aegis System Module...")
    assert validate_aegis()
    print("✓ Aegis System Module validated")
    
    # Demo
    print("\n--- Aegis System Demo ---")
    
    aegis = AegisSystem()
    aegis.activate()
    
    print("\nInitial Status:")
    status = aegis.get_status()
    print(f"  State: {status['state']}")
    print(f"  Damping Mode: {status['damping_mode']}")
    
    print("\nProcessing Attack Sequence:")
    attacks = [
        IncomingAttack(energy=15.0, frequency=0.5, attack_type="probe"),
        IncomingAttack(energy=30.0, frequency=1.0, attack_type="assault"),
        IncomingAttack(energy=50.0, frequency=1.5, attack_type="heavy"),
    ]
    
    for i, attack in enumerate(attacks):
        result = aegis.process_attack(attack)
        print(f"\n  Attack {i+1} ({attack.attack_type}):")
        print(f"    Energy: {attack.energy}")
        print(f"    Absorbed: {result['energy_absorbed']:.2f}")
        print(f"    Transmitted: {result['energy_transmitted']:.2f}")
        print(f"    Absorption Rate: {result['absorption_rate']:.1%}")
        print(f"    Phobos Radiated: {result['phobos_radiated']:.4f}")
    
    print("\nExecuting Gorgon Flash:")
    flash = aegis.execute_gorgon_flash()
    print(f"  Flash intensity: {flash:.4f}")
    
    print("\nProtection Test:")
    aegis.protect_entity("critical_process_1")
    aegis.protect_entity("critical_process_2")
    print(f"  Protected entities: {aegis.get_status()['total_protected']}")
    print(f"  Is 'critical_process_1' protected: {aegis.is_protected('critical_process_1')}")
    
    print("\nFinal Status:")
    status = aegis.get_status()
    print(f"  Attacks absorbed: {status['attacks_absorbed']}")
    print(f"  Total energy absorbed: {status['total_energy_absorbed']:.2f}")
    print(f"  Total phobos radiated: {status['total_phobos_radiated']:.6f}")
    print(f"  Stored energy: {status['stored_energy']:.2f}")

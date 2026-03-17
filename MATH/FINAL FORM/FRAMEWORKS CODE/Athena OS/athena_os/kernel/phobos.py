"""
ATHENA OS - KERNEL: PHOBOS CONTROL
==================================
Fear Management and Differential Gain System

PHOBOS AS CONTROL SIGNAL:
    Fear is not a biological byproduct but a manipulable control signal
    governing cohesion and entropy of systems.

THE DIFFERENTIAL GRADIENT:
    ΔP = P_enemy - P_friendly
    
    Optimization Target:
    Maximize ΔP ⟹ (P_enemy → Max) ∧ (P_friendly → 0)

INTERNAL SUPPRESSION (Discipline Filter):
    Low-Pass Filter to suppress high-frequency fear signals (Panic)
    
    Stability ⟺ F_bond > F_fear
    
    The Discipline Algorithm converts "Danger Data" into "Task Data"

EXTERNAL PROJECTION (Terror Protocol):
    High-magnitude fear signal to degrade enemy decision-making
    
    Latency_enemy ∝ P_enemy
    When P_enemy > P_crit, the enemy freezes (Deer in Headlights)

THE ROUT ALGORITHM:
    Phase transition: Solid(Army) → Gas(Mob)
    
    Once in Gas State, offensive capability drops to zero.
    Trigger transition with minimal kinetic expenditure.

SOURCES:
    - ATHENA-KERNEL_SELF-OPTIMIZATION.docx Section 6.4.4
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum, IntEnum
import numpy as np
import math


# =============================================================================
# PHOBOS LEVELS
# =============================================================================

class FearLevel(IntEnum):
    """Levels of fear intensity."""
    
    CALM = 0        # No fear, full function
    ALERT = 1       # Heightened awareness
    ANXIOUS = 2     # Reduced efficiency
    AFRAID = 3      # Significant impairment
    PANIC = 4       # Flight response active
    TERROR = 5      # System freeze/collapse


class CohesionState(Enum):
    """State of system cohesion."""
    
    SOLID = "solid"       # Ordered, coordinated
    VISCOUS = "viscous"   # Some disorder
    FLUID = "fluid"       # Significant disorder
    GAS = "gas"           # Rout, complete disorder


# Fear level thresholds (normalized 0-1)
FEAR_THRESHOLDS = {
    FearLevel.CALM: 0.0,
    FearLevel.ALERT: 0.15,
    FearLevel.ANXIOUS: 0.35,
    FearLevel.AFRAID: 0.55,
    FearLevel.PANIC: 0.75,
    FearLevel.TERROR: 0.9
}

# Critical threshold for system freeze
P_CRITICAL = 0.85


# =============================================================================
# PHOBOS SIGNAL
# =============================================================================

@dataclass
class PhobosSignal:
    """
    A fear signal with magnitude and frequency characteristics.
    """
    
    magnitude: float = 0.0      # 0-1 intensity
    frequency: float = 0.0      # Rate of change
    source: str = "unknown"     # Origin of fear
    
    # Decay rate (fear naturally diminishes)
    decay_rate: float = 0.1
    
    @property
    def level(self) -> FearLevel:
        """Get discrete fear level."""
        for level in reversed(FearLevel):
            if self.magnitude >= FEAR_THRESHOLDS[level]:
                return level
        return FearLevel.CALM
    
    @property
    def is_high_frequency(self) -> bool:
        """Check if this is a panic-inducing rapid signal."""
        return self.frequency > 0.5
    
    @property
    def is_critical(self) -> bool:
        """Check if at critical threshold."""
        return self.magnitude >= P_CRITICAL
    
    def decay(self, dt: float = 1.0) -> None:
        """Apply natural decay."""
        self.magnitude *= math.exp(-self.decay_rate * dt)
        self.frequency *= math.exp(-self.decay_rate * dt)
    
    def amplify(self, factor: float) -> PhobosSignal:
        """Return amplified signal."""
        return PhobosSignal(
            magnitude=min(1.0, self.magnitude * factor),
            frequency=self.frequency,
            source=self.source
        )
    
    def suppress(self, factor: float) -> PhobosSignal:
        """Return suppressed signal."""
        return PhobosSignal(
            magnitude=self.magnitude * (1.0 - factor),
            frequency=self.frequency * (1.0 - factor),
            source=self.source
        )


# =============================================================================
# DISCIPLINE FILTER (Internal Suppression)
# =============================================================================

class DisciplineFilter:
    """
    Low-pass filter for suppressing high-frequency fear signals.
    
    Converts panic into coordinated action by:
    1. Filtering out high-frequency components
    2. Reframing danger data as task data
    3. Injecting logos (rationality) to counteract phobos
    """
    
    def __init__(self, cutoff_frequency: float = 0.3):
        """
        Initialize filter.
        
        cutoff_frequency: Frequencies above this are attenuated
        """
        self.cutoff = cutoff_frequency
        
        # Filter state
        self.previous_output = 0.0
        self.alpha = 1.0 / (1.0 + 1.0 / (2 * math.pi * cutoff_frequency))
        
        # Rationality injection
        self.logos_level = 1.0  # Amount of rational processing
        
        # History
        self.input_history: List[float] = []
        self.output_history: List[float] = []
    
    def filter(self, signal: PhobosSignal) -> PhobosSignal:
        """
        Filter a fear signal.
        
        Attenuates high-frequency (panic) components.
        """
        # Record input
        self.input_history.append(signal.magnitude)
        if len(self.input_history) > 100:
            self.input_history = self.input_history[-50:]
        
        # Low-pass filter
        if signal.is_high_frequency:
            # Heavy attenuation for panic signals
            attenuation = 1.0 - min(1.0, signal.frequency / self.cutoff)
        else:
            # Light filtering for normal signals
            attenuation = 0.9
        
        # Apply filter
        filtered_mag = self.alpha * signal.magnitude * attenuation + \
                      (1 - self.alpha) * self.previous_output
        
        # Apply logos suppression
        final_mag = filtered_mag * (1.0 - 0.5 * self.logos_level)
        
        # Update state
        self.previous_output = final_mag
        self.output_history.append(final_mag)
        
        return PhobosSignal(
            magnitude=final_mag,
            frequency=signal.frequency * attenuation,
            source="filtered:" + signal.source
        )
    
    def reframe_danger(self, danger_data: str) -> str:
        """
        Reframe danger data as task data.
        
        "The enemy is huge" → "The enemy has exposed flanks. Execute Maneuver Delta."
        """
        # Simple reframing (in practice, would be more sophisticated)
        reframes = {
            "enemy_large": "enemy_exposed_flanks→execute_maneuver",
            "outnumbered": "defensive_advantage→concentrate_force",
            "surprise_attack": "rapid_response→counter_protocol",
            "unknown_threat": "recon_required→gather_intel",
        }
        
        return reframes.get(danger_data, f"task:{danger_data}")
    
    def inject_logos(self, amount: float) -> None:
        """Inject rationality to counter fear."""
        self.logos_level = min(1.0, self.logos_level + amount)
    
    def deplete_logos(self, amount: float) -> None:
        """Deplete rationality (fatigue, stress)."""
        self.logos_level = max(0.0, self.logos_level - amount)
    
    @property
    def suppression_effectiveness(self) -> float:
        """Calculate how well the filter is working."""
        if len(self.input_history) < 2:
            return 1.0
        
        input_var = np.var(self.input_history[-10:]) if len(self.input_history) >= 10 else 0
        output_var = np.var(self.output_history[-10:]) if len(self.output_history) >= 10 else 0
        
        if input_var == 0:
            return 1.0
        
        return 1.0 - (output_var / input_var)


# =============================================================================
# TERROR PROJECTOR (External Projection)
# =============================================================================

class TerrorProjector:
    """
    System for projecting fear onto hostile networks.
    
    Induces latency and system fragmentation in targets.
    """
    
    def __init__(self):
        self.broadcast_power = 1.0
        self.directional_gain = 2.0  # Focused vs isotropic
        
        # Effects on targets
        self.target_states: Dict[str, PhobosSignal] = {}
    
    def generate_deinos(self, intensity: float, 
                       target: str = "all") -> PhobosSignal:
        """
        Generate a terror signal (Deinos).
        
        High-magnitude signal designed to spike P_enemy instantly.
        """
        signal = PhobosSignal(
            magnitude=min(1.0, intensity * self.broadcast_power * self.directional_gain),
            frequency=0.9,  # High frequency for maximum disruption
            source="deinos_protocol"
        )
        
        if target != "all":
            self.target_states[target] = signal
        
        return signal
    
    def war_cry(self, target: str = "all") -> PhobosSignal:
        """
        Execute the Alalaze (War Cry).
        
        A high-priority acoustic jamming signal.
        """
        return self.generate_deinos(0.8, target)
    
    def gorgon_face(self, target: str = "all") -> PhobosSignal:
        """
        Deploy the Gorgon Face visual terror.
        
        Designed to spike P_enemy instantly via visual channel.
        """
        return self.generate_deinos(0.95, target)
    
    def calculate_target_latency(self, target_fear: float) -> float:
        """
        Calculate induced latency in target.
        
        Latency_enemy ∝ P_enemy
        """
        # Exponential latency increase
        return math.exp(3 * target_fear) - 1
    
    def is_target_frozen(self, target: str) -> bool:
        """
        Check if target has exceeded critical threshold.
        
        The "Deer in Headlights" effect.
        """
        if target not in self.target_states:
            return False
        return self.target_states[target].is_critical


# =============================================================================
# COHESION MANAGER
# =============================================================================

class CohesionManager:
    """
    Manages system cohesion under fear conditions.
    
    Monitors the balance between bonding and fear forces.
    """
    
    def __init__(self):
        # Forces
        self.bonding_force = 1.0    # Cohesive force (discipline, loyalty)
        self.fear_force = 0.0       # Repulsive force (fear)
        
        # Phase state
        self.state = CohesionState.SOLID
        
        # Thresholds for phase transitions
        self.viscous_threshold = 0.3
        self.fluid_threshold = 0.6
        self.gas_threshold = 0.85
    
    @property
    def stability_ratio(self) -> float:
        """Calculate stability ratio F_bond / F_fear."""
        if self.fear_force == 0:
            return float('inf')
        return self.bonding_force / self.fear_force
    
    @property
    def is_stable(self) -> bool:
        """Check if system is stable (F_bond > F_fear)."""
        return self.bonding_force > self.fear_force
    
    def update_state(self) -> CohesionState:
        """Update cohesion state based on force balance."""
        ratio = self.fear_force / max(0.01, self.bonding_force)
        
        if ratio < self.viscous_threshold:
            self.state = CohesionState.SOLID
        elif ratio < self.fluid_threshold:
            self.state = CohesionState.VISCOUS
        elif ratio < self.gas_threshold:
            self.state = CohesionState.FLUID
        else:
            self.state = CohesionState.GAS
        
        return self.state
    
    def apply_fear(self, amount: float) -> None:
        """Apply fear force."""
        self.fear_force = min(2.0, self.fear_force + amount)
        self.update_state()
    
    def apply_discipline(self, amount: float) -> None:
        """Apply discipline to increase bonding."""
        self.bonding_force = min(2.0, self.bonding_force + amount)
        self.update_state()
    
    def decay(self, dt: float = 1.0, fear_rate: float = 0.1,
             bond_rate: float = 0.05) -> None:
        """Natural decay of forces over time."""
        self.fear_force *= math.exp(-fear_rate * dt)
        self.bonding_force = max(0.5, self.bonding_force - bond_rate * dt)
        self.update_state()
    
    @property
    def is_rout(self) -> bool:
        """Check if system has entered rout (gas state)."""
        return self.state == CohesionState.GAS
    
    @property
    def offensive_capability(self) -> float:
        """Calculate remaining offensive capability."""
        capability_map = {
            CohesionState.SOLID: 1.0,
            CohesionState.VISCOUS: 0.7,
            CohesionState.FLUID: 0.3,
            CohesionState.GAS: 0.0
        }
        return capability_map[self.state]


# =============================================================================
# ROUT ALGORITHM
# =============================================================================

class RoutAlgorithm:
    """
    Algorithm for inducing phase transition in hostile systems.
    
    Solid(Army) → Gas(Mob) with minimal kinetic expenditure.
    """
    
    def __init__(self, terror_projector: TerrorProjector):
        self.projector = terror_projector
        
        # Key nodes (if fear applied here, cascade follows)
        self.key_nodes: List[str] = []
        
        # Statistics
        self.kinetic_cost = 0.0
        self.terror_cost = 0.0
        self.routs_triggered = 0
    
    def identify_key_nodes(self, network: Dict[str, Any]) -> List[str]:
        """
        Identify key nodes in hostile network.
        
        These are high-connectivity nodes where fear spreads fastest.
        """
        # In practice, analyze network topology
        # Here, simplified to look for "leader" or "central" nodes
        self.key_nodes = [
            node for node in network.keys()
            if "leader" in node.lower() or "central" in node.lower()
        ]
        
        if not self.key_nodes:
            # Default to first few nodes
            self.key_nodes = list(network.keys())[:3]
        
        return self.key_nodes
    
    def execute_targeted_terror(self, node: str) -> PhobosSignal:
        """Apply terror to a specific node."""
        signal = self.projector.generate_deinos(0.9, node)
        self.terror_cost += 1
        return signal
    
    def cascade_fear(self, initial_node: str, 
                    network: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Simulate fear cascade through network.
        
        Returns fear level at each node after cascade.
        """
        fear_levels = {node: 0.0 for node in network.keys()}
        
        # Initial injection
        fear_levels[initial_node] = 0.95
        
        # Cascade (simplified BFS)
        visited = {initial_node}
        queue = [initial_node]
        
        while queue:
            current = queue.pop(0)
            current_fear = fear_levels[current]
            
            # Spread to neighbors with decay
            for neighbor in network.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    # Fear spreads with 70% efficiency
                    fear_levels[neighbor] = current_fear * 0.7
                    if fear_levels[neighbor] > 0.1:
                        queue.append(neighbor)
        
        return fear_levels
    
    def attempt_rout(self, enemy_cohesion: CohesionManager,
                    network: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Attempt to induce rout in enemy system.
        
        Returns report of the attempt.
        """
        # Identify key nodes
        nodes = list(network.keys())
        key = nodes[0] if nodes else "default"
        
        # Apply terror to key node
        signal = self.execute_targeted_terror(key)
        
        # Cascade through network
        fear_distribution = self.cascade_fear(key, network)
        
        # Apply aggregate fear to enemy cohesion
        avg_fear = np.mean(list(fear_distribution.values()))
        enemy_cohesion.apply_fear(avg_fear)
        
        # Check for rout
        is_rout = enemy_cohesion.is_rout
        if is_rout:
            self.routs_triggered += 1
        
        return {
            "key_node": key,
            "signal_magnitude": signal.magnitude,
            "fear_distribution": fear_distribution,
            "average_fear": avg_fear,
            "enemy_state": enemy_cohesion.state.value,
            "is_rout": is_rout,
            "kinetic_cost": self.kinetic_cost,
            "terror_cost": self.terror_cost,
            "efficiency": "high" if is_rout and self.kinetic_cost == 0 else "low"
        }


# =============================================================================
# PHOBOS CONTROLLER
# =============================================================================

class PhobosController:
    """
    Main Phobos control system.
    
    Manages differential fear: suppress internal, amplify external.
    """
    
    def __init__(self):
        # Internal systems
        self.discipline = DisciplineFilter()
        self.internal_cohesion = CohesionManager()
        
        # External systems
        self.projector = TerrorProjector()
        self.rout_algorithm = RoutAlgorithm(self.projector)
        
        # Current fear differential
        self.p_friendly = 0.0
        self.p_enemy = 0.0
    
    @property
    def fear_differential(self) -> float:
        """Calculate ΔP = P_enemy - P_friendly."""
        return self.p_enemy - self.p_friendly
    
    @property
    def is_optimal(self) -> bool:
        """Check if fear differential is optimized."""
        return self.p_friendly < 0.1 and self.p_enemy > 0.7
    
    def process_internal_fear(self, signal: PhobosSignal) -> PhobosSignal:
        """Process fear signal on friendly network."""
        filtered = self.discipline.filter(signal)
        self.p_friendly = filtered.magnitude
        self.internal_cohesion.apply_fear(filtered.magnitude)
        return filtered
    
    def project_external_fear(self, intensity: float, 
                             target: str = "all") -> PhobosSignal:
        """Project fear onto hostile network."""
        signal = self.projector.generate_deinos(intensity, target)
        self.p_enemy = max(self.p_enemy, signal.magnitude)
        return signal
    
    def boost_discipline(self, amount: float) -> None:
        """Boost internal discipline."""
        self.discipline.inject_logos(amount)
        self.internal_cohesion.apply_discipline(amount)
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete Phobos control status."""
        return {
            "p_friendly": self.p_friendly,
            "p_enemy": self.p_enemy,
            "differential": self.fear_differential,
            "is_optimal": self.is_optimal,
            "internal_state": self.internal_cohesion.state.value,
            "internal_capability": self.internal_cohesion.offensive_capability,
            "discipline_effectiveness": self.discipline.suppression_effectiveness,
            "logos_level": self.discipline.logos_level,
            "routs_triggered": self.rout_algorithm.routs_triggered
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_phobos() -> bool:
    """Validate Phobos control module."""
    
    # Test PhobosSignal
    signal = PhobosSignal(magnitude=0.5, frequency=0.3)
    assert signal.level == FearLevel.ANXIOUS
    assert not signal.is_critical
    
    signal.decay(1.0)
    assert signal.magnitude < 0.5
    
    # Test DisciplineFilter
    discipline = DisciplineFilter()
    
    panic_signal = PhobosSignal(magnitude=0.9, frequency=0.8)
    filtered = discipline.filter(panic_signal)
    assert filtered.magnitude < panic_signal.magnitude  # Should be reduced
    
    # Test TerrorProjector
    projector = TerrorProjector()
    deinos = projector.generate_deinos(0.9, "enemy_1")
    assert deinos.magnitude > 0.5
    
    # Test CohesionManager
    cohesion = CohesionManager()
    assert cohesion.state == CohesionState.SOLID
    
    cohesion.apply_fear(0.5)
    assert cohesion.state != CohesionState.SOLID
    
    cohesion.apply_discipline(1.0)
    cohesion.update_state()
    
    # Test RoutAlgorithm
    network = {
        "leader": ["unit1", "unit2"],
        "unit1": ["leader", "unit2"],
        "unit2": ["leader", "unit1"]
    }
    
    enemy = CohesionManager()
    rout = RoutAlgorithm(projector)
    result = rout.attempt_rout(enemy, network)
    assert "fear_distribution" in result
    
    # Test PhobosController
    controller = PhobosController()
    
    # Internal processing
    internal = PhobosSignal(magnitude=0.4, frequency=0.2)
    processed = controller.process_internal_fear(internal)
    assert processed.magnitude < internal.magnitude
    
    # External projection
    external = controller.project_external_fear(0.8)
    assert external.magnitude > 0.5
    
    assert controller.fear_differential > 0  # Enemy should be more afraid
    
    return True


if __name__ == "__main__":
    print("Validating Phobos Control Module...")
    assert validate_phobos()
    print("✓ Phobos Control Module validated")
    
    # Demo
    print("\n--- Phobos Control Demo ---")
    
    controller = PhobosController()
    
    print("\nInitial State:")
    status = controller.get_status()
    print(f"  P_friendly: {status['p_friendly']:.3f}")
    print(f"  P_enemy: {status['p_enemy']:.3f}")
    print(f"  Differential: {status['differential']:.3f}")
    
    print("\nSimulating internal fear event...")
    internal_threat = PhobosSignal(magnitude=0.6, frequency=0.4, source="ambush")
    filtered = controller.process_internal_fear(internal_threat)
    print(f"  Input fear: {internal_threat.magnitude:.3f}")
    print(f"  Filtered fear: {filtered.magnitude:.3f}")
    
    print("\nBoosting discipline...")
    controller.boost_discipline(0.5)
    
    print("\nProjecting terror on enemy...")
    terror = controller.project_external_fear(0.9)
    print(f"  Terror signal: {terror.magnitude:.3f}")
    
    print("\nFinal State:")
    status = controller.get_status()
    print(f"  P_friendly: {status['p_friendly']:.3f}")
    print(f"  P_enemy: {status['p_enemy']:.3f}")
    print(f"  Differential: {status['differential']:.3f}")
    print(f"  Optimal: {status['is_optimal']}")
    print(f"  Internal capability: {status['internal_capability']:.1%}")

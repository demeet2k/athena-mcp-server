"""
ATHENA OS - Viability Corridors and Shadow Systems
===================================================
Biological corridor discipline and inner/outer shadows.

Viability Corridor (K_bio):
The set of states where life is possible:
K_bio = {S_bio : g_i(S) ≤ 0, h_j(S) = 0}

Minimal corridor constraints:
- Energy corridor: ATP level above survival threshold
- Structure corridor: Membrane potential within bounds
- Error corridor: Mutation rate below error catastrophe
- Control corridor: Regulatory instability not diverging

Inner Shadow (Bio) = Information Depth:
"How many bits to specify a viable organism state"
- Genome length + redundancy
- Regulatory network complexity
- Coding redundancy

Outer Shadow (Bio) = Saturation Horizons:
"Where life saturates/breaks"
- Error catastrophe (too much mutation)
- Energy starvation (Φ collapse)
- Carrying capacity (ecological bound)
- Repair ceiling (damage > repair)

Anti-Aether (Bio) = Impossible Moves:
- Perfect replication with no energy cost
- Rollback of lineage without ledger
- Infinite growth with finite resources
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np
import math

from .aether import BioPillar, BioState, BiologicalAether


# =============================================================================
# CORRIDOR CONSTRAINTS
# =============================================================================

@dataclass
class CorridorConstraint:
    """
    A single constraint defining the viability corridor.
    
    Constraints can be:
    - Inequality: g(S) ≤ 0
    - Equality: h(S) = 0
    """
    name: str
    constraint_type: str  # 'inequality' or 'equality'
    pillar: BioPillar     # Which pillar enforces this
    threshold: float      # Threshold value
    check: Callable[[BioState], float]  # Returns constraint violation
    
    def violated(self, state: BioState) -> bool:
        """Check if constraint is violated."""
        value = self.check(state)
        if self.constraint_type == 'inequality':
            return value > 0
        else:  # equality
            return abs(value) > 1e-6
    
    def violation_magnitude(self, state: BioState) -> float:
        """Get magnitude of violation."""
        value = self.check(state)
        if self.constraint_type == 'inequality':
            return max(0, value)
        else:
            return abs(value)


# =============================================================================
# STANDARD CORRIDOR CONSTRAINTS
# =============================================================================

def _energy_check(state: BioState) -> float:
    """Energy must be positive: return positive if violated."""
    return -state.energy_flux  # Violated if energy_flux ≤ 0

ENERGY_CORRIDOR = CorridorConstraint(
    name="Energy",
    constraint_type='inequality',
    pillar=BioPillar.FIRE,
    threshold=0.0,
    check=_energy_check
)


def _atp_check(state: BioState) -> float:
    """ATP budget must be above minimum."""
    min_atp = 10.0
    return min_atp - state.atp_budget  # Violated if atp < min

ATP_CORRIDOR = CorridorConstraint(
    name="ATP",
    constraint_type='inequality',
    pillar=BioPillar.FIRE,
    threshold=10.0,
    check=_atp_check
)


def _boundary_check(state: BioState) -> float:
    """Boundary must exist."""
    return 0.0 if state.has_boundary else 1.0

BOUNDARY_CORRIDOR = CorridorConstraint(
    name="Boundary",
    constraint_type='inequality',
    pillar=BioPillar.EARTH,
    threshold=0.0,
    check=_boundary_check
)


def _error_check(state: BioState) -> float:
    """Error must be below catastrophe threshold."""
    catastrophe = 0.1
    return state.error_budget - catastrophe

ERROR_CORRIDOR = CorridorConstraint(
    name="Error",
    constraint_type='inequality',
    pillar=BioPillar.EARTH,
    threshold=0.1,
    check=_error_check
)


def _viability_check(state: BioState) -> float:
    """Overall viability must be above threshold."""
    threshold = 0.25
    return threshold - state.viability()

VIABILITY_CORRIDOR = CorridorConstraint(
    name="Viability",
    constraint_type='inequality',
    pillar=BioPillar.EARTH,
    threshold=0.25,
    check=_viability_check
)


# All standard constraints
STANDARD_CONSTRAINTS: List[CorridorConstraint] = [
    ENERGY_CORRIDOR,
    ATP_CORRIDOR,
    BOUNDARY_CORRIDOR,
    ERROR_CORRIDOR,
    VIABILITY_CORRIDOR,
]


# =============================================================================
# VIABILITY CORRIDOR
# =============================================================================

@dataclass
class ViabilityCorridor:
    """
    The viability corridor K_bio.
    
    The set of states where life is possible:
    K_bio = {S_bio : all constraints satisfied}
    
    This separates:
    - Aether (habitable operations)
    - Anti-Aether (impossible operations)
    """
    
    constraints: List[CorridorConstraint] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.constraints:
            self.constraints = STANDARD_CONSTRAINTS.copy()
    
    def check(self, state: BioState) -> Tuple[bool, List[str]]:
        """
        Check if state is in corridor.
        
        Returns (is_viable, list_of_violations).
        """
        violations = []
        
        for constraint in self.constraints:
            if constraint.violated(state):
                violations.append(
                    f"{constraint.name}: {constraint.violation_magnitude(state):.4f}"
                )
        
        return len(violations) == 0, violations
    
    def distance_to_boundary(self, state: BioState) -> float:
        """
        Compute minimum distance to corridor boundary.
        
        Positive = inside corridor
        Negative = outside corridor
        """
        min_slack = float('inf')
        
        for constraint in self.constraints:
            value = constraint.check(state)
            if constraint.constraint_type == 'inequality':
                slack = -value  # Positive when constraint satisfied
                min_slack = min(min_slack, slack)
        
        return min_slack if min_slack != float('inf') else 0.0
    
    def project_to_corridor(self, state: BioState) -> BioState:
        """
        Project state back into corridor (repair).
        
        Simple projection: fix violated constraints.
        """
        new_state = BioState(
            population=state.population,
            dominant_pillar=state.dominant_pillar,
            replication_rate=state.replication_rate,
            energy_flux=max(1.0, state.energy_flux),  # Ensure positive
            information=state.information,
            has_boundary=True,  # Ensure boundary
            atp_budget=max(10.0, state.atp_budget),  # Ensure minimum ATP
            error_budget=min(0.09, state.error_budget),  # Below catastrophe
            ledger=state.ledger.copy()
        )
        new_state.append_ledger("CORRIDOR_PROJECTION")
        return new_state
    
    def add_constraint(self, constraint: CorridorConstraint) -> None:
        """Add a custom constraint."""
        self.constraints.append(constraint)


# Global corridor instance
VIABILITY = ViabilityCorridor()


# =============================================================================
# INNER SHADOW (Code Depth)
# =============================================================================

@dataclass
class InnerShadow:
    """
    Inner Shadow (Bio) = Information Depth.
    
    "How many bits to specify a viable organism state"
    
    Components:
    - Genome length
    - Regulatory network complexity
    - Redundancy/error correction capacity
    """
    
    # Genome information
    genome_bits: int = 1000
    
    # Network complexity
    network_nodes: int = 100
    network_edges: int = 500
    
    # Redundancy
    redundancy_factor: float = 2.0
    
    @property
    def total_bits(self) -> int:
        """Total information content."""
        network_bits = int(self.network_nodes * np.log2(self.network_edges + 1))
        return int(self.genome_bits + network_bits * self.redundancy_factor)
    
    @property
    def coding_density(self) -> float:
        """Bits per functional unit."""
        return self.genome_bits / max(1, self.network_nodes)
    
    def mutual_information(self, module1: int, module2: int) -> float:
        """Estimate mutual information between modules."""
        # Simplified model
        shared_edges = min(module1, module2) * 0.1
        return np.log2(1 + shared_edges)
    
    def description_length(self) -> int:
        """Minimum description length for the organism."""
        # Kolmogorov-style estimate
        return int(self.total_bits / self.redundancy_factor)
    
    def from_state(self, state: BioState) -> 'InnerShadow':
        """Compute inner shadow from a bio state."""
        return InnerShadow(
            genome_bits=int(state.information),
            network_nodes=int(state.information / 10),
            redundancy_factor=2.0 if state.error_budget < 0.05 else 1.0
        )


# =============================================================================
# OUTER SHADOW (Saturation Horizons)
# =============================================================================

@dataclass
class OuterShadow:
    """
    Outer Shadow (Bio) = Saturation Horizons.
    
    "Where life saturates/breaks"
    
    Horizons:
    - Error catastrophe (mutation overwhelms heredity)
    - Energy starvation (Fire collapses)
    - Repair ceiling (damage exceeds repair)
    - Carrying capacity (population hits bound)
    """
    
    # Error catastrophe
    mutation_rate: float = 1e-6
    genome_length: int = 1000
    error_threshold: float = 0.1  # Eigen's threshold
    
    # Energy limits
    maintenance_cost: float = 50.0
    max_energy_input: float = 200.0
    
    # Repair ceiling
    damage_rate: float = 0.01
    max_repair_rate: float = 0.02
    
    # Carrying capacity
    carrying_capacity: float = 1e9
    
    @property
    def effective_error_rate(self) -> float:
        """Compute effective error rate."""
        return self.mutation_rate * self.genome_length
    
    @property
    def is_at_error_catastrophe(self) -> bool:
        """Check if at error catastrophe."""
        return self.effective_error_rate > self.error_threshold
    
    @property
    def energy_margin(self) -> float:
        """Available energy above maintenance."""
        return self.max_energy_input - self.maintenance_cost
    
    @property
    def is_energy_starved(self) -> bool:
        """Check if energy starved."""
        return self.energy_margin <= 0
    
    @property
    def repair_margin(self) -> float:
        """Repair capacity above damage rate."""
        return self.max_repair_rate - self.damage_rate
    
    @property
    def is_at_repair_ceiling(self) -> bool:
        """Check if at repair ceiling."""
        return self.repair_margin <= 0
    
    def distance_to_catastrophe(self) -> Dict[str, float]:
        """Compute distance to each saturation horizon."""
        return {
            'error': self.error_threshold - self.effective_error_rate,
            'energy': self.energy_margin,
            'repair': self.repair_margin,
            'capacity': 1.0  # Normalized
        }
    
    def nearest_horizon(self) -> Tuple[str, float]:
        """Find the nearest saturation horizon."""
        distances = self.distance_to_catastrophe()
        nearest = min(distances.items(), key=lambda x: x[1])
        return nearest


# =============================================================================
# ANTI-AETHER (Impossible Moves)
# =============================================================================

class AntiAether:
    """
    Anti-Aether (Bio) = Impossible Moves.
    
    Biology's no-go list:
    - Perfect replication with no energy cost
    - Rollback of lineage without ledger
    - Infinite growth with finite resources
    - Violation of thermodynamics
    """
    
    @staticmethod
    def is_impossible(operation: str, state: BioState) -> Tuple[bool, str]:
        """
        Check if an operation is impossible.
        
        Returns (is_impossible, reason).
        """
        # Check various anti-aether conditions
        
        if operation == "free_replication":
            return True, "Replication requires energy (thermodynamics)"
        
        if operation == "lineage_rollback":
            return True, "Lineage is irreversible (ledger constraint)"
        
        if operation == "infinite_growth" and state.atp_budget < float('inf'):
            return True, "Growth requires finite resources"
        
        if operation == "perfect_copying" and state.error_budget > 0:
            return True, "Perfect copying impossible (quantum limits)"
        
        if operation == "information_creation":
            return True, "Information cannot be created from nothing"
        
        return False, "Operation allowed"
    
    @staticmethod
    def list_forbidden() -> List[str]:
        """List all forbidden operations."""
        return [
            "free_replication",
            "lineage_rollback",
            "infinite_growth",
            "perfect_copying",
            "information_creation",
            "negative_entropy_creation",
            "boundary_violation",
            "time_reversal_biology"
        ]


# =============================================================================
# SHADOW POLE DETECTION
# =============================================================================

def detect_shadow_pole(state: BioState, inner: InnerShadow, 
                       outer: OuterShadow) -> str:
    """
    Detect which shadow pole dominates for a state.
    
    Returns "inner" (code depth) or "outer" (saturation).
    """
    # Check outer shadow distances
    outer_distances = outer.distance_to_catastrophe()
    min_outer = min(outer_distances.values())
    
    # Check inner shadow (coding density)
    inner_density = inner.coding_density
    
    # If close to any saturation horizon, outer dominates
    if min_outer < 0.1:
        return "outer"
    
    # If high coding density, inner dominates
    if inner_density > 100:
        return "inner"
    
    # Default based on dominant pillar
    if state.dominant_pillar in (BioPillar.EARTH, BioPillar.AIR):
        return "inner"
    else:
        return "outer"


# =============================================================================
# VALIDATION
# =============================================================================

def validate_corridors() -> bool:
    """Validate corridor systems."""
    
    # Test constraints
    assert len(STANDARD_CONSTRAINTS) >= 4
    
    viable_state = BioState(
        energy_flux=50.0,
        atp_budget=100.0,
        has_boundary=True,
        error_budget=0.01
    )
    
    assert not ENERGY_CORRIDOR.violated(viable_state)
    assert not BOUNDARY_CORRIDOR.violated(viable_state)
    
    # Test corridor
    corridor = ViabilityCorridor()
    is_viable, violations = corridor.check(viable_state)
    assert is_viable
    assert len(violations) == 0
    
    # Test non-viable state
    dead_state = BioState(energy_flux=0)
    is_viable, violations = corridor.check(dead_state)
    assert not is_viable
    assert len(violations) > 0
    
    # Test projection
    projected = corridor.project_to_corridor(dead_state)
    is_viable, _ = corridor.check(projected)
    assert is_viable
    
    # Test inner shadow
    inner = InnerShadow(genome_bits=1000)
    assert inner.total_bits > 0
    assert inner.coding_density > 0
    
    # Test outer shadow
    outer = OuterShadow()
    assert not outer.is_at_error_catastrophe
    distances = outer.distance_to_catastrophe()
    assert 'error' in distances
    
    # Test anti-aether
    impossible, reason = AntiAether.is_impossible("free_replication", viable_state)
    assert impossible
    
    # Test shadow detection
    pole = detect_shadow_pole(viable_state, inner, outer)
    assert pole in ("inner", "outer")
    
    return True


if __name__ == "__main__":
    print("Validating Viability Corridors...")
    assert validate_corridors()
    print("✓ Viability Corridors validated")
    
    # Demo
    print("\n=== Corridor Demo ===")
    corridor = ViabilityCorridor()
    
    state = BioState(
        energy_flux=50.0,
        atp_budget=100.0,
        error_budget=0.05
    )
    
    is_viable, violations = corridor.check(state)
    print(f"State viable: {is_viable}")
    print(f"Distance to boundary: {corridor.distance_to_boundary(state):.4f}")
    
    print("\n=== Shadow Analysis ===")
    inner = InnerShadow(genome_bits=3000, network_nodes=200)
    outer = OuterShadow(mutation_rate=1e-5, genome_length=3000)
    
    print(f"Inner shadow (code depth): {inner.total_bits} bits")
    print(f"Outer shadow distances: {outer.distance_to_catastrophe()}")
    print(f"Nearest horizon: {outer.nearest_horizon()}")
    
    pole = detect_shadow_pole(state, inner, outer)
    print(f"Dominant shadow pole: {pole}")
    
    print("\n=== Anti-Aether ===")
    for op in ["free_replication", "replicate", "lineage_rollback"]:
        impossible, reason = AntiAether.is_impossible(op, state)
        print(f"  {op}: {'FORBIDDEN' if impossible else 'allowed'} - {reason}")

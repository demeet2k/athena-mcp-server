"""
ATHENA OS - Biological Aether Foundation
=========================================
The 4→1 artifact for living systems.

Core Thesis:
Biology = conserved INFORMATION in a DISSIPATIVE system.
The biological crystal is tilted relative to physics:
- Physics: reversible until clamps
- Biology: irreversible by default, information preservation is the invariant

Biology begins when Earth clamps become persistent and heritable.

The Biological Aether:
A_Bio = (Z*_Bio, R, M, Φ, L, C)
Where:
- Z*_Bio = nonliving chemistry baseline (no self-maintenance)
- R = replicator (genome/template/heritable program)
- M = membrane/compartment (inside/outside separation)
- Φ = metabolic drive (free-energy flow maintaining non-equilibrium)
- L = irreversible lineage ledger (history append-only)
- C = constraint set (error correction, viability corridor)

The conserved quantity:
I(R_{t+1}; R_t) > 0 across long time
(Information survives replication + noise)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from datetime import datetime
import hashlib
import numpy as np
import math


# =============================================================================
# BIOLOGICAL PILLARS (Elements in Biology)
# =============================================================================

class BioPillar(IntEnum):
    """
    The four pillars in biology (same abstract roles as physics).
    
    Fire: Metabolism, energy throughput (Φ)
    Water: Replication, lineage flow (R → R')
    Air: Regulation, signaling, control
    Earth: Structure, boundary, constraints
    
    Life exists ONLY when all four are present simultaneously:
    - No Fire → dead (no energy)
    - No Water → sterile (no replication)
    - No Air → blind (no regulation)
    - No Earth → dissolved (no boundaries)
    """
    FIRE = 0   # ?? Metabolism / Energy
    WATER = 1  # ?? Replication / Flow
    AIR = 2    # ?? Regulation / Control
    EARTH = 3  # ?? Structure / Constraint
    
    @property
    def symbol(self) -> str:
        symbols = {
            BioPillar.FIRE: '??',
            BioPillar.WATER: '??',
            BioPillar.AIR: '??',
            BioPillar.EARTH: '??'
        }
        return symbols[self]
    
    @property
    def bio_meaning(self) -> str:
        meanings = {
            BioPillar.FIRE: 'Metabolism / Energy acquisition',
            BioPillar.WATER: 'Replication / Growth / Population flow',
            BioPillar.AIR: 'Sensing / Signaling / Regulation',
            BioPillar.EARTH: 'Structure / Boundary / Genome / Membrane'
        }
        return meanings[self]
    
    @property
    def death_mode(self) -> str:
        """What happens when this pillar fails."""
        modes = {
            BioPillar.FIRE: 'Energy starvation → death',
            BioPillar.WATER: 'Replication failure → sterility/extinction',
            BioPillar.AIR: 'Regulatory collapse → dysfunction',
            BioPillar.EARTH: 'Boundary loss → dissolution'
        }
        return modes[self]


# =============================================================================
# BIOLOGICAL ZERO POINT
# =============================================================================

@dataclass
class BiologicalZeroPoint:
    """
    Z*_Bio: The biological zero point (non-replicating chemistry).
    
    In physics: Z* = minimum action / neutral field
    In biology: Z* = non-replicating chemistry
    
    Life is DISTANCE from this zero.
    Replication creates the gradient.
    """
    
    # Zero point properties
    entropy_production: float = 0.0  # No self-maintenance
    information_content: float = 0.0  # No heritable information
    replication_rate: float = 0.0    # No copying
    
    # Boundary conditions
    has_membrane: bool = False
    has_metabolism: bool = False
    has_regulation: bool = False
    
    def distance_from_life(self, state: 'BioState') -> float:
        """Measure distance from life (how alive is this state?)."""
        components = [
            state.replication_rate > 0,
            state.energy_flux > 0,
            state.information > 0,
            state.has_boundary
        ]
        return sum(components) / 4.0


# =============================================================================
# BIOLOGICAL STATE BUNDLE
# =============================================================================

@dataclass
class BioState:
    """
    The biological wave state (quad-polar state bundle).
    
    S_bio = (μ, q, v, L, B, Γ)
    
    Same bundle form as the mathematical framework:
    - μ: distribution over cell types/phenotypes (population simplex)
    - q: compass orientation (which pole dominates)
    - v: paraconsistent valuation store
    - L: lineage ledger (irreversible event log)
    - B: budgets (ATP/time/information/structural integrity)
    - Γ: gate state (which transitions allowed)
    """
    
    # Population distribution (μ)
    population: np.ndarray = field(default_factory=lambda: np.array([1.0]))
    
    # Compass orientation (q) - which pillar dominates
    dominant_pillar: BioPillar = BioPillar.WATER
    
    # Key state variables
    replication_rate: float = 0.0
    energy_flux: float = 0.0
    information: float = 0.0
    has_boundary: bool = True
    
    # Lineage ledger (L) - irreversible history
    ledger: List[str] = field(default_factory=list)
    
    # Budgets (B)
    atp_budget: float = 100.0
    time_budget: float = float('inf')
    error_budget: float = 0.0  # Accumulated errors
    
    # Gate state (Γ) - allowed transitions
    can_divide: bool = True
    can_differentiate: bool = True
    can_apoptose: bool = True
    can_dormant: bool = True
    
    def append_ledger(self, event: str) -> None:
        """Append event to irreversible ledger."""
        timestamp = datetime.now().isoformat()
        self.ledger.append(f"{timestamp}: {event}")
    
    def pillar_balance(self) -> Dict[BioPillar, float]:
        """Get balance of all pillars."""
        return {
            BioPillar.FIRE: self.energy_flux / 100.0,
            BioPillar.WATER: self.replication_rate / 100.0,
            BioPillar.AIR: 0.5,  # Default regulation level
            BioPillar.EARTH: 1.0 if self.has_boundary else 0.0
        }
    
    def viability(self) -> float:
        """Compute viability (0 = dead, 1 = fully viable)."""
        balance = self.pillar_balance()
        # All pillars must be present
        min_pillar = min(balance.values())
        if min_pillar == 0:
            return 0.0
        return min_pillar
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dominant_pillar': self.dominant_pillar.name,
            'replication_rate': self.replication_rate,
            'energy_flux': self.energy_flux,
            'information': self.information,
            'viability': self.viability(),
            'ledger_length': len(self.ledger),
            'atp_budget': self.atp_budget
        }


# =============================================================================
# BIOLOGICAL AETHER
# =============================================================================

@dataclass
class BiologicalAether:
    """
    The biological aether: A_Bio = (Z*, R, M, Φ, L, C)
    
    This is the 4→1 artifact for living systems.
    
    Generator set (replaces d, *, □):
    G_Bio = {replicate, metabolize, sense, constrain}
    
    Invariant set (Earth clamps):
    I_Bio = {survival, lineage_continuity, error_tolerance}
    """
    
    # Zero point
    zero_point: BiologicalZeroPoint = field(default_factory=BiologicalZeroPoint)
    
    # Replicator (R)
    genome_length: int = 1000  # Bits of heritable information
    mutation_rate: float = 1e-6  # Per bit per replication
    
    # Membrane (M)
    compartment_count: int = 1  # Number of compartments
    permeability: float = 0.1  # Membrane permeability
    
    # Metabolic drive (Φ)
    energy_input_rate: float = 100.0  # ATP/s equivalent
    maintenance_cost: float = 50.0    # Baseline cost
    
    # Lineage ledger (L)
    ledger: List[str] = field(default_factory=list)
    
    # Constraint set (C)
    viability_threshold: float = 0.5
    error_catastrophe_threshold: float = 0.1
    
    # Generator operations
    generators: Dict[str, Callable] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize generators."""
        self.generators = {
            'replicate': self._replicate,
            'metabolize': self._metabolize,
            'sense': self._sense,
            'constrain': self._constrain
        }
    
    def _replicate(self, state: BioState) -> BioState:
        """Replication operator (Water)."""
        new_state = BioState(
            population=state.population * 2,
            dominant_pillar=BioPillar.WATER,
            replication_rate=state.replication_rate,
            energy_flux=state.energy_flux - 10,  # Replication costs energy
            information=state.information,
            has_boundary=state.has_boundary,
            ledger=state.ledger.copy()
        )
        new_state.append_ledger("REPLICATE")
        return new_state
    
    def _metabolize(self, state: BioState) -> BioState:
        """Metabolize operator (Fire)."""
        new_state = BioState(
            population=state.population,
            dominant_pillar=BioPillar.FIRE,
            replication_rate=state.replication_rate,
            energy_flux=state.energy_flux + self.energy_input_rate - self.maintenance_cost,
            information=state.information,
            has_boundary=state.has_boundary,
            atp_budget=state.atp_budget + self.energy_input_rate - self.maintenance_cost,
            ledger=state.ledger.copy()
        )
        new_state.append_ledger("METABOLIZE")
        return new_state
    
    def _sense(self, state: BioState, signal: float = 0.5) -> BioState:
        """Sense operator (Air)."""
        new_state = BioState(
            population=state.population,
            dominant_pillar=BioPillar.AIR,
            replication_rate=state.replication_rate * (1 + 0.1 * signal),
            energy_flux=state.energy_flux,
            information=state.information + 1,  # Information gained
            has_boundary=state.has_boundary,
            ledger=state.ledger.copy()
        )
        new_state.append_ledger(f"SENSE(signal={signal:.2f})")
        return new_state
    
    def _constrain(self, state: BioState) -> BioState:
        """Constrain operator (Earth)."""
        # Apply error correction
        new_state = BioState(
            population=state.population,
            dominant_pillar=BioPillar.EARTH,
            replication_rate=state.replication_rate,
            energy_flux=state.energy_flux - 5,  # Repair costs energy
            information=state.information,
            has_boundary=True,  # Ensure boundary
            error_budget=max(0, state.error_budget - 0.01),  # Reduce errors
            ledger=state.ledger.copy()
        )
        new_state.append_ledger("CONSTRAIN/REPAIR")
        return new_state
    
    def expand(self) -> Dict[BioPillar, str]:
        """Expand aether to four pillars."""
        return {
            BioPillar.FIRE: f"Metabolic work (Φ={self.energy_input_rate})",
            BioPillar.WATER: f"Replication (genome={self.genome_length}bp)",
            BioPillar.AIR: "Regulation/signaling",
            BioPillar.EARTH: f"Structure ({self.compartment_count} compartments)"
        }
    
    def information_channel(self, state: BioState, noise: float = 0.0) -> float:
        """
        Compute information preserved through replication.
        
        I(R_{t+1}; R_t) > 0 is the biological invariant.
        """
        # Simple model: information preserved = (1 - error_rate) * original
        error_rate = self.mutation_rate * self.genome_length * (1 + noise)
        
        if error_rate >= self.error_catastrophe_threshold:
            return 0.0  # Error catastrophe
        
        return state.information * (1 - error_rate)
    
    def check_viability(self, state: BioState) -> Tuple[bool, str]:
        """Check if state is viable (within corridors)."""
        if state.energy_flux <= 0:
            return False, "Energy starvation"
        
        if not state.has_boundary:
            return False, "Boundary loss"
        
        if state.error_budget > self.error_catastrophe_threshold:
            return False, "Error catastrophe"
        
        if state.viability() < self.viability_threshold:
            return False, "Below viability threshold"
        
        return True, "Viable"


# =============================================================================
# BIOLOGICAL INVARIANTS
# =============================================================================

@dataclass
class BiologicalInvariant:
    """
    The conserved quantity in biology.
    
    Physics invariants: charge, action, topology
    Biology invariant: information that survives replication + noise
    
    This is why:
    - DNA is digital
    - Error correction exists
    - Redundancy appears everywhere
    
    Biology is physics constrained to preserve information across time.
    """
    
    name: str
    value: float = 0.0
    tolerance: float = 0.01
    
    # History for tracking
    history: List[float] = field(default_factory=list)
    
    def update(self, new_value: float) -> bool:
        """Update invariant and check conservation."""
        self.history.append(self.value)
        
        # For biology, we check that information doesn't decrease
        # (or doesn't decrease faster than tolerable)
        preserved = new_value >= self.value * (1 - self.tolerance)
        
        self.value = new_value
        return preserved


# Conservation laws
SURVIVAL_INVARIANT = BiologicalInvariant("survival")
LINEAGE_INVARIANT = BiologicalInvariant("lineage_continuity")
ERROR_TOLERANCE_INVARIANT = BiologicalInvariant("error_tolerance", tolerance=0.1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_aether() -> bool:
    """Validate biological aether."""
    
    # Test pillars
    assert len(BioPillar) == 4
    assert BioPillar.FIRE.symbol == '??'
    assert BioPillar.WATER.bio_meaning.startswith('Replication')
    
    # Test zero point
    zero = BiologicalZeroPoint()
    assert zero.replication_rate == 0.0
    
    # Test bio state
    state = BioState(
        replication_rate=10.0,
        energy_flux=50.0,
        information=100.0
    )
    assert state.viability() > 0
    
    # Test ledger append
    state.append_ledger("TEST")
    assert len(state.ledger) == 1
    
    # Test aether
    aether = BiologicalAether()
    expansion = aether.expand()
    assert len(expansion) == 4
    
    # Test generators
    state2 = aether._replicate(state)
    assert len(state2.ledger) == 2  # Original + REPLICATE
    
    state3 = aether._metabolize(state)
    assert state3.dominant_pillar == BioPillar.FIRE
    
    # Test viability check
    viable, msg = aether.check_viability(state)
    assert viable
    
    # Test non-viable state
    dead_state = BioState(energy_flux=0)
    viable, msg = aether.check_viability(dead_state)
    assert not viable
    assert "Energy" in msg
    
    # Test information channel
    info = aether.information_channel(state, noise=0)
    assert info > 0
    
    return True


if __name__ == "__main__":
    print("Validating Biological Aether...")
    assert validate_aether()
    print("✓ Biological Aether validated")
    
    # Demo
    print("\n=== Biological Aether Demo ===")
    aether = BiologicalAether()
    print(f"Aether expansion: {aether.expand()}")
    
    state = BioState(
        replication_rate=10.0,
        energy_flux=50.0,
        information=100.0
    )
    print(f"\nInitial state: {state.to_dict()}")
    
    # Apply generators
    state = aether._metabolize(state)
    print(f"After metabolize: {state.to_dict()}")
    
    state = aether._replicate(state)
    print(f"After replicate: {state.to_dict()}")
    
    print(f"\nLedger: {state.ledger}")

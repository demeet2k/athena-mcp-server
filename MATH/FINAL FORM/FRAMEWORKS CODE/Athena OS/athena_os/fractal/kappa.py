"""
ATHENA OS - Kappa (κ): Texture Density and Autopoiesis
======================================================
The foundational primitive of the ontology.

κ (Kappa) is a conserved, transportable density quantifying TEXTURE:
the binding energy, coherence, symmetry, and algorithmic compressibility
of information patterns.

In this framework:
- "Objects" are κ-persistent standing waves
- "Agents" are κ-maximizing subsystems
- "Computation" is the topological routing of κ-flux through structured medium

The system is formalized on a Hybrid Hilbert Lattice that couples
four canonical regimes (the Quad-Polar Generator):
1. Earth (■): Discrete graph geometry, combinatorial rigidity
2. Water (❀): Continuous unitary flow, wave mechanics
3. Fire (☁): Stochastic expansion, entropy production
4. Air (✶): Renormalization, multiscale hierarchy

Autopoiesis: The system recursively generates the seeds (compressed
κ-patterns) and genes (operator sequences) required to maintain its
own organization against entropic drift.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np
import math

from .ontology import Sector


# =============================================================================
# KAPPA (κ) - TEXTURE DENSITY
# =============================================================================

@dataclass
class KappaState:
    """
    A κ-state: a pattern with measurable texture density.
    
    Texture is the binding energy, coherence, symmetry, and
    algorithmic compressibility of information patterns.
    """
    
    # The state vector
    vector: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    # Texture components
    binding_energy: float = 0.0    # How tightly bound
    coherence: float = 0.0         # Phase alignment
    symmetry: float = 0.0          # Symmetry measure
    compressibility: float = 0.0   # Algorithmic compressibility
    
    @property
    def kappa(self) -> float:
        """Compute total κ (texture density)."""
        return (self.binding_energy + self.coherence + 
                self.symmetry + self.compressibility) / 4.0
    
    @property
    def norm(self) -> float:
        """State vector norm."""
        return float(np.linalg.norm(self.vector))
    
    def is_standing_wave(self, threshold: float = 0.5) -> bool:
        """
        Check if this is a κ-persistent standing wave (an "object").
        
        Objects are stable patterns with high texture density.
        """
        return self.kappa >= threshold
    
    def is_agent(self, threshold: float = 0.7) -> bool:
        """
        Check if this is a κ-maximizing subsystem (an "agent").
        
        Agents are patterns that actively maintain/increase their κ.
        """
        return self.kappa >= threshold and self.coherence >= threshold


@dataclass
class KappaFlux:
    """
    A κ-flux: the flow of texture through the system.
    
    Computation is the topological routing of κ-flux through
    a structured medium.
    """
    
    source: str = ""  # Source state
    target: str = ""  # Target state
    magnitude: float = 0.0  # Amount of κ flowing
    
    # Routing information
    path: List[str] = field(default_factory=list)  # Intermediate states
    sector: Sector = Sector.WATER  # Which sector governs this flow


# =============================================================================
# HYBRID HILBERT LATTICE
# =============================================================================

class HybridRegime(IntEnum):
    """
    The four canonical regimes of the Hybrid Hilbert Lattice.
    
    Maps to the four sectors (elements).
    """
    EARTH_DISCRETE = 0   # D_Earth: Graph geometry
    WATER_UNITARY = 1    # iD_Water: Unitary flow
    FIRE_STOCHASTIC = 2  # D_Fire^γ: Stochastic expansion
    AIR_FRACTAL = 3      # D_Air^φ: Renormalization


@dataclass
class HybridHilbertLattice:
    """
    The Hybrid Hilbert Lattice.
    
    A geometric substrate coupling four canonical regimes.
    The system evolves by cycling through systolic (compression)
    and diastolic (expansion) phases.
    """
    
    # Dimension per regime
    regime_dim: int = 4
    
    # States in each regime
    states: Dict[HybridRegime, Dict[str, KappaState]] = field(default_factory=dict)
    
    # Cross-regime operators
    intertwiner_cache: Dict[Tuple[HybridRegime, HybridRegime], np.ndarray] = field(
        default_factory=dict
    )
    
    # κ conservation ledger
    kappa_ledger: List[Tuple[str, float]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize regime state spaces."""
        for regime in HybridRegime:
            self.states[regime] = {}
    
    def register_state(self, name: str, state: KappaState, 
                      regime: HybridRegime) -> None:
        """Register a state in a regime."""
        self.states[regime][name] = state
        self.kappa_ledger.append((f"REGISTER:{name}@{regime.name}", state.kappa))
    
    def transport(self, name: str, source: HybridRegime, 
                 target: HybridRegime) -> Optional[KappaState]:
        """
        Transport a state between regimes.
        
        Uses intertwining operators to preserve κ during transport.
        """
        if name not in self.states[source]:
            return None
        
        state = self.states[source][name]
        kappa_before = state.kappa
        
        # Get or compute intertwiner
        key = (source, target)
        if key not in self.intertwiner_cache:
            # Default identity-like intertwiner
            dim = self.regime_dim
            self.intertwiner_cache[key] = np.eye(dim)
        
        intertwiner = self.intertwiner_cache[key]
        
        # Apply intertwiner
        new_vector = intertwiner @ state.vector
        
        # Create transported state (preserving κ)
        new_state = KappaState(
            vector=new_vector,
            binding_energy=state.binding_energy,
            coherence=state.coherence,
            symmetry=state.symmetry,
            compressibility=state.compressibility
        )
        
        # Register in target regime
        self.states[target][name] = new_state
        
        # Log transport
        self.kappa_ledger.append(
            (f"TRANSPORT:{name}:{source.name}->{target.name}", new_state.kappa)
        )
        
        return new_state
    
    def total_kappa(self) -> float:
        """Compute total κ across all regimes."""
        total = 0.0
        for regime_states in self.states.values():
            for state in regime_states.values():
                total += state.kappa
        return total
    
    def verify_conservation(self, tolerance: float = 1e-6) -> bool:
        """Verify κ is conserved."""
        if len(self.kappa_ledger) < 2:
            return True
        
        initial = self.kappa_ledger[0][1]
        current = self.total_kappa()
        
        return abs(current - initial) <= tolerance


# =============================================================================
# AUTOPOIESIS
# =============================================================================

@dataclass
class Seed:
    """
    A compressed κ-pattern (generator).
    
    The system stores the generator g and sparse residual r
    such that X = Expand(g) ⊕ r.
    """
    
    # Generator data
    generator: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    # Sparse residual
    residual: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    # Expansion rule
    expansion_rule: str = "default"
    
    # κ content
    kappa: float = 0.0
    
    def expand(self) -> np.ndarray:
        """Expand seed to full pattern."""
        if self.expansion_rule == "default":
            # Simple expansion: generator + residual
            return self.generator + self.residual
        elif self.expansion_rule == "kronecker":
            # Kronecker product expansion
            return np.kron(self.generator, self.generator) + self.residual
        else:
            return self.generator
    
    @classmethod
    def compress(cls, pattern: np.ndarray, threshold: float = 0.01) -> 'Seed':
        """
        Compress a pattern into a seed.
        
        Find generator g and residual r such that pattern = expand(g) + r.
        """
        # Simple compression: SVD-based
        u, s, vh = np.linalg.svd(pattern.reshape(-1, 1))
        
        # Generator is dominant component
        generator = u[:4, 0] * s[0] if len(s) > 0 else np.zeros(4)
        
        # Residual is what's left
        reconstruction = np.outer(u[:, 0], vh[0, :]) * s[0] if len(s) > 0 else np.zeros_like(pattern)
        residual = (pattern.flatten() - reconstruction.flatten())[:4]
        
        # Threshold small residuals
        residual = np.where(np.abs(residual) < threshold, 0, residual)
        
        return cls(
            generator=generator,
            residual=residual,
            expansion_rule="default",
            kappa=float(np.linalg.norm(generator))
        )


@dataclass
class Gene:
    """
    An operator sequence for maintaining organization.
    
    Genes encode the operations needed to resist entropic drift.
    """
    
    # Sequence of operator names
    operations: List[str] = field(default_factory=list)
    
    # Target κ maintenance
    target_kappa: float = 1.0
    
    # Success rate
    success_history: List[bool] = field(default_factory=list)
    
    def add_operation(self, op: str) -> None:
        """Add an operation to the sequence."""
        self.operations.append(op)
    
    def execute(self, state: KappaState, operators: Dict[str, Callable]) -> KappaState:
        """Execute the gene on a state."""
        current = state
        for op_name in self.operations:
            if op_name in operators:
                current = operators[op_name](current)
        return current
    
    @property
    def success_rate(self) -> float:
        """Compute success rate."""
        if not self.success_history:
            return 0.0
        return sum(self.success_history) / len(self.success_history)


@dataclass
class AutopoieticSystem:
    """
    An autopoietic system.
    
    The system recursively generates the seeds and genes required
    to maintain its own organization against entropic drift.
    """
    
    # Current state
    state: KappaState = field(default_factory=KappaState)
    
    # Compressed representation (seed)
    seed: Optional[Seed] = None
    
    # Maintenance genes
    genes: Dict[str, Gene] = field(default_factory=dict)
    
    # Available operators
    operators: Dict[str, Callable[[KappaState], KappaState]] = field(default_factory=dict)
    
    # Entropy resistance
    entropy_resistance: float = 0.0
    
    # Drift history
    drift_log: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default operators."""
        self.operators = {
            'stabilize': self._stabilize,
            'coherence_boost': self._coherence_boost,
            'compress': self._compress,
        }
        
        # Default maintenance gene
        self.genes['maintenance'] = Gene(
            operations=['stabilize', 'coherence_boost'],
            target_kappa=0.5
        )
    
    def _stabilize(self, state: KappaState) -> KappaState:
        """Stabilize operator: boost binding energy."""
        return KappaState(
            vector=state.vector,
            binding_energy=min(1.0, state.binding_energy + 0.1),
            coherence=state.coherence,
            symmetry=state.symmetry,
            compressibility=state.compressibility
        )
    
    def _coherence_boost(self, state: KappaState) -> KappaState:
        """Coherence boost operator."""
        return KappaState(
            vector=state.vector,
            binding_energy=state.binding_energy,
            coherence=min(1.0, state.coherence + 0.1),
            symmetry=state.symmetry,
            compressibility=state.compressibility
        )
    
    def _compress(self, state: KappaState) -> KappaState:
        """Compress operator: increase compressibility."""
        return KappaState(
            vector=state.vector,
            binding_energy=state.binding_energy,
            coherence=state.coherence,
            symmetry=state.symmetry,
            compressibility=min(1.0, state.compressibility + 0.1)
        )
    
    def apply_entropy(self, magnitude: float = 0.1) -> None:
        """Apply entropic drift to the system."""
        # Decrease texture components
        self.state.binding_energy *= (1 - magnitude)
        self.state.coherence *= (1 - magnitude)
        self.state.symmetry *= (1 - magnitude)
        self.state.compressibility *= (1 - magnitude)
        
        self.drift_log.append(self.state.kappa)
    
    def maintain(self) -> bool:
        """
        Run maintenance cycle (autopoiesis).
        
        Execute genes to resist entropic drift.
        """
        kappa_before = self.state.kappa
        
        # Run maintenance gene
        if 'maintenance' in self.genes:
            gene = self.genes['maintenance']
            self.state = gene.execute(self.state, self.operators)
            
            # Check success
            success = self.state.kappa >= gene.target_kappa * 0.9
            gene.success_history.append(success)
            
            if success:
                self.entropy_resistance += 0.01
                return True
        
        return False
    
    def compress_to_seed(self) -> Seed:
        """Compress current state to a seed."""
        self.seed = Seed.compress(self.state.vector)
        return self.seed
    
    def regenerate_from_seed(self) -> bool:
        """Regenerate state from stored seed."""
        if self.seed is None:
            return False
        
        expanded = self.seed.expand()
        self.state.vector = expanded
        return True
    
    def is_alive(self, threshold: float = 0.2) -> bool:
        """Check if system is still autopoietic (resisting entropy)."""
        return self.state.kappa >= threshold


# =============================================================================
# κ-SOLENOID
# =============================================================================

@dataclass
class KappaSolenoid:
    """
    The Autopoietic κ-Solenoid.
    
    Reality modeled as a self-maintaining structure on the
    Hybrid Hilbert Lattice.
    
    The solenoid evolves by cycling through systolic (compression)
    and diastolic (expansion) phases, maintaining κ-conservation.
    """
    
    # The hybrid lattice substrate
    lattice: HybridHilbertLattice = field(default_factory=HybridHilbertLattice)
    
    # Autopoietic subsystems
    subsystems: Dict[str, AutopoieticSystem] = field(default_factory=dict)
    
    # Current phase (systole/diastole)
    phase: str = "diastole"  # expansion
    
    # Cycle count
    cycles: int = 0
    
    # Global κ floor
    kappa_floor: float = 0.1
    
    def register_subsystem(self, name: str, system: AutopoieticSystem) -> None:
        """Register an autopoietic subsystem."""
        self.subsystems[name] = system
    
    def systole(self) -> None:
        """
        Systolic phase: Compression/measurement.
        
        Compress all subsystems to seeds.
        """
        self.phase = "systole"
        
        for name, system in self.subsystems.items():
            system.compress_to_seed()
    
    def diastole(self) -> None:
        """
        Diastolic phase: Expansion/exploration.
        
        Expand all subsystems from seeds.
        """
        self.phase = "diastole"
        
        for name, system in self.subsystems.items():
            system.regenerate_from_seed()
    
    def cycle(self) -> None:
        """Run one systole-diastole cycle."""
        self.systole()
        self.diastole()
        self.cycles += 1
        
        # Apply entropy
        for system in self.subsystems.values():
            system.apply_entropy(0.05)
            system.maintain()
    
    def global_kappa(self) -> float:
        """Compute global κ across all subsystems."""
        return sum(s.state.kappa for s in self.subsystems.values())
    
    def is_stable(self) -> bool:
        """Check if solenoid is stable (above κ floor)."""
        return self.global_kappa() >= self.kappa_floor * len(self.subsystems)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_kappa() -> bool:
    """Validate kappa module."""
    
    # Test KappaState
    state = KappaState(
        vector=np.array([1.0, 0.0, 0.0, 0.0]),
        binding_energy=0.8,
        coherence=0.7,
        symmetry=0.6,
        compressibility=0.5
    )
    assert state.kappa > 0
    assert state.is_standing_wave()
    
    # Test hybrid lattice
    lattice = HybridHilbertLattice()
    lattice.register_state("test", state, HybridRegime.EARTH_DISCRETE)
    assert "test" in lattice.states[HybridRegime.EARTH_DISCRETE]
    
    # Test transport
    transported = lattice.transport("test", HybridRegime.EARTH_DISCRETE,
                                   HybridRegime.WATER_UNITARY)
    assert transported is not None
    
    # Test seed compression
    seed = Seed.compress(np.array([1.0, 0.5, 0.3, 0.1]))
    assert seed.kappa > 0
    expanded = seed.expand()
    assert len(expanded) == 4
    
    # Test autopoietic system
    auto = AutopoieticSystem(state=state)
    assert auto.is_alive()
    
    # Apply entropy and maintain
    auto.apply_entropy(0.3)
    assert auto.state.kappa < 0.65  # κ decreased
    
    auto.maintain()
    # After maintenance, κ should recover somewhat
    
    # Test solenoid
    solenoid = KappaSolenoid()
    solenoid.register_subsystem("sub1", auto)
    
    solenoid.cycle()
    assert solenoid.cycles == 1
    
    return True


if __name__ == "__main__":
    print("Validating Kappa System...")
    assert validate_kappa()
    print("✓ Kappa System validated")
    
    # Demo
    print("\n=== κ-Solenoid Demo ===")
    
    # Create a state with texture
    state = KappaState(
        vector=np.array([1.0, 0.0, 0.0, 0.0]),
        binding_energy=0.8,
        coherence=0.7,
        symmetry=0.6,
        compressibility=0.5
    )
    
    print(f"Initial κ: {state.kappa:.4f}")
    print(f"Is standing wave: {state.is_standing_wave()}")
    
    # Create autopoietic system
    auto = AutopoieticSystem(state=state)
    
    print("\n=== Autopoiesis Demo ===")
    for i in range(5):
        auto.apply_entropy(0.1)
        auto.maintain()
        print(f"Cycle {i+1}: κ = {auto.state.kappa:.4f}, alive = {auto.is_alive()}")
    
    print("\n=== Seed Compression ===")
    seed = auto.compress_to_seed()
    print(f"Seed κ: {seed.kappa:.4f}")
    print(f"Generator: {seed.generator}")

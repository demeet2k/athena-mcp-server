"""
ATHENA OS - NORSE: RAGNARÖK MODULE
===================================
Phase Transitions and Cyclic System Reset

RAGNARÖK: THE ENTROPY THRESHOLD
    Not random termination, but deterministic Phase Transition
    triggered when topological entropy exceeds graph connectivity.

FIMBULWINTER PHASE:
    Pre-crash state where:
    - Edge weights increase (communication slows)
    - Local entropy maximizes
    - Temperature T(t) = T₀ · e^{-λt} → 0
    - Social graph clustering C(t) → 0

THE CRITICAL THRESHOLD (Ω_c):
    Stability: Connectivity(G) > Ω_c
    Collapse: Connectivity(G) ≤ Ω_c → Graph partitions
    
    G → {v_Asg} ∪ {v_Mid} ∪ {v_Hel} ...

RESET PROTOCOL:
    1. Collapse complex graph to low-entropy state (Ginnungagap)
    2. Purge accumulated errors (monsters/giants)
    3. Clear memory buffers (history)
    4. Preserve seed (Lif and Lifthrasir)
    5. Spawn new world with kernel parameters K_new ≅ K_old

THERMODYNAMICS:
    System entropy S > S_crit → Instability
    Bonds break, edges fail → Execute Ragnarök()
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .topology import Yggdrasil, World, Edge, Ginnungagap


# =============================================================================
# RAGNARÖK PHASES
# =============================================================================

class RagnarokPhase(Enum):
    """Phases of Ragnarök."""
    
    NORMAL = "normal"               # System stable
    FIMBULWINTER = "fimbulwinter"   # Pre-crash cooling
    BREAKING = "breaking"           # Bonds breaking
    COLLAPSE = "collapse"           # Graph partitioning
    VOID = "void"                   # Ginnungagap state
    REBIRTH = "rebirth"             # New world spawning


# =============================================================================
# FIMBULWINTER
# =============================================================================

@dataclass
class FimbulwinterState:
    """
    Fimbulwinter: The Great Winter preceding Ragnarök.
    
    Thermodynamic cooling phase preparing for hard reset.
    """
    
    # Temperature decay
    initial_temperature: float = 1.0
    decay_rate: float = 0.1
    
    # Current state
    temperature: float = 1.0
    duration: float = 0.0
    
    # Social entropy
    social_cohesion: float = 1.0
    
    def cool(self, dt: float) -> None:
        """
        Apply cooling function.
        
        T(t) = T₀ · e^{-λt}
        """
        self.duration += dt
        self.temperature = self.initial_temperature * np.exp(
            -self.decay_rate * self.duration
        )
        
        # Social cohesion also decays
        self.social_cohesion *= np.exp(-self.decay_rate * dt * 0.5)
    
    def is_frozen(self, threshold: float = 0.01) -> bool:
        """Check if system has reached freezing point."""
        return self.temperature < threshold
    
    @property
    def entropy(self) -> float:
        """
        Information entropy increases as temperature drops.
        
        S = -log(T) for T > 0
        """
        if self.temperature <= 0:
            return float('inf')
        return -np.log(self.temperature + 1e-10)


# =============================================================================
# BOND BREAKING
# =============================================================================

@dataclass
class Bond:
    """
    A cosmic bond (oath, kinship, law) that maintains order.
    
    Breaking of bonds is described in Völuspá as precursor to Ragnarök.
    """
    
    name: str
    strength: float
    bound_entities: Tuple[str, str]
    
    # State
    _intact: bool = True
    _strain: float = 0.0
    
    def apply_strain(self, amount: float) -> None:
        """Apply strain to the bond."""
        self._strain += amount
        
        if self._strain >= self.strength:
            self.break_bond()
    
    def break_bond(self) -> None:
        """Break the bond."""
        self._intact = False
    
    @property
    def integrity(self) -> float:
        """Get bond integrity (0-1)."""
        if not self._intact:
            return 0.0
        return max(0.0, 1.0 - self._strain / self.strength)
    
    @property
    def is_intact(self) -> bool:
        return self._intact


class BondSystem:
    """
    System of cosmic bonds maintaining world order.
    
    Major bonds from Norse mythology:
    - Gleipnir: Binds Fenrir
    - Loki's bonds: Binds Loki
    - Oaths between Æsir
    """
    
    def __init__(self):
        self._bonds: List[Bond] = []
        self._create_primordial_bonds()
    
    def _create_primordial_bonds(self) -> None:
        """Create the primordial bonds."""
        self._bonds = [
            Bond("Gleipnir", 10.0, ("Fenrir", "Asgard")),
            Bond("Lokis_Chains", 8.0, ("Loki", "Asgard")),
            Bond("Bifrost_Oath", 7.0, ("Heimdall", "Bifröst")),
            Bond("Odin_Ravens", 5.0, ("Huginn", "Muninn")),
            Bond("Blood_Brotherhood", 6.0, ("Odin", "Loki")),
            Bond("World_Tree_Root", 15.0, ("Yggdrasil", "Worlds")),
        ]
    
    def apply_global_strain(self, amount: float) -> int:
        """
        Apply strain to all bonds.
        
        Returns number of bonds broken.
        """
        broken = 0
        for bond in self._bonds:
            if bond.is_intact:
                bond.apply_strain(amount)
                if not bond.is_intact:
                    broken += 1
        return broken
    
    def get_total_integrity(self) -> float:
        """Get average integrity of all bonds."""
        if not self._bonds:
            return 0.0
        return sum(b.integrity for b in self._bonds) / len(self._bonds)
    
    def get_broken_bonds(self) -> List[Bond]:
        """Get list of broken bonds."""
        return [b for b in self._bonds if not b.is_intact]
    
    @property
    def n_intact(self) -> int:
        return sum(1 for b in self._bonds if b.is_intact)
    
    @property
    def n_broken(self) -> int:
        return sum(1 for b in self._bonds if not b.is_intact)


# =============================================================================
# RAGNARÖK ENGINE
# =============================================================================

class RagnarokEngine:
    """
    The Ragnarök Phase Transition Engine.
    
    Manages the cyclic destruction and rebirth of the cosmos.
    """
    
    def __init__(self, yggdrasil: Yggdrasil):
        self.yggdrasil = yggdrasil
        
        # Phase state
        self._phase = RagnarokPhase.NORMAL
        
        # Components
        self.fimbulwinter = FimbulwinterState()
        self.bonds = BondSystem()
        self.void = Ginnungagap()
        
        # Thresholds
        self.connectivity_threshold = 0.3  # Ω_c
        self.entropy_threshold = 2.0       # S_crit
        self.temperature_threshold = 0.05  # Freezing point
        
        # Seed preservation
        self._seed: Optional[Dict] = None
        
        # Statistics
        self._cycles_completed = 0
        self._total_time = 0.0
    
    def compute_system_entropy(self) -> float:
        """
        Compute total system entropy.
        
        H_G = -Σ p_i ln(p_i)
        """
        # Get degree centrality as probability distribution
        adj = self.yggdrasil.compute_adjacency_matrix()
        degrees = np.sum(adj, axis=1)
        
        if np.sum(degrees) == 0:
            return float('inf')
        
        p = degrees / np.sum(degrees)
        p = p[p > 0]  # Remove zeros
        
        return -np.sum(p * np.log(p))
    
    def check_stability(self) -> Tuple[bool, Dict]:
        """
        Check system stability conditions.
        
        Returns (is_stable, diagnostics).
        """
        connectivity = self.yggdrasil.get_connectivity()
        entropy = self.compute_system_entropy()
        bond_integrity = self.bonds.get_total_integrity()
        
        diagnostics = {
            "connectivity": connectivity,
            "entropy": entropy,
            "bond_integrity": bond_integrity,
            "temperature": self.fimbulwinter.temperature,
            "connectivity_ok": connectivity > self.connectivity_threshold,
            "entropy_ok": entropy < self.entropy_threshold,
            "bonds_ok": bond_integrity > 0.2
        }
        
        is_stable = all([
            diagnostics["connectivity_ok"],
            diagnostics["entropy_ok"],
            diagnostics["bonds_ok"]
        ])
        
        return is_stable, diagnostics
    
    def tick(self, dt: float = 1.0) -> Dict:
        """
        Advance Ragnarök simulation by dt.
        
        Returns phase transition information.
        """
        self._total_time += dt
        result = {"phase": self._phase, "events": []}
        
        if self._phase == RagnarokPhase.NORMAL:
            result.update(self._tick_normal(dt))
            
        elif self._phase == RagnarokPhase.FIMBULWINTER:
            result.update(self._tick_fimbulwinter(dt))
            
        elif self._phase == RagnarokPhase.BREAKING:
            result.update(self._tick_breaking(dt))
            
        elif self._phase == RagnarokPhase.COLLAPSE:
            result.update(self._tick_collapse(dt))
            
        elif self._phase == RagnarokPhase.VOID:
            result.update(self._tick_void(dt))
            
        elif self._phase == RagnarokPhase.REBIRTH:
            result.update(self._tick_rebirth(dt))
        
        return result
    
    def _tick_normal(self, dt: float) -> Dict:
        """Normal operation - check for instability."""
        self.yggdrasil.tick(dt)
        
        is_stable, diagnostics = self.check_stability()
        
        if not is_stable:
            # Begin Fimbulwinter
            self._phase = RagnarokPhase.FIMBULWINTER
            return {
                "transition": "NORMAL → FIMBULWINTER",
                "diagnostics": diagnostics
            }
        
        return {"diagnostics": diagnostics}
    
    def _tick_fimbulwinter(self, dt: float) -> Dict:
        """Fimbulwinter - cooling phase."""
        self.fimbulwinter.cool(dt)
        
        # Apply strain to bonds
        strain = dt * 0.5 * (1 - self.fimbulwinter.temperature)
        broken = self.bonds.apply_global_strain(strain)
        
        events = []
        if broken > 0:
            events.append(f"{broken} bonds broken")
        
        # Check for transition to Breaking
        if self.fimbulwinter.is_frozen(self.temperature_threshold):
            self._phase = RagnarokPhase.BREAKING
            return {
                "transition": "FIMBULWINTER → BREAKING",
                "events": events,
                "temperature": self.fimbulwinter.temperature
            }
        
        return {
            "events": events,
            "temperature": self.fimbulwinter.temperature,
            "social_cohesion": self.fimbulwinter.social_cohesion
        }
    
    def _tick_breaking(self, dt: float) -> Dict:
        """Breaking phase - bonds and edges fail."""
        events = []
        
        # Break remaining bonds rapidly
        broken = self.bonds.apply_global_strain(dt * 2.0)
        if broken > 0:
            events.append(f"{broken} bonds shattered")
        
        # Damage edges
        for edge in self.yggdrasil.edges:
            if edge._active:
                edge.damage(dt * 0.5)
                if edge.impedance > 10.0:
                    edge.break_edge()
                    events.append(f"Edge {edge.name} collapsed")
        
        # Check for collapse
        connectivity = self.yggdrasil.get_connectivity()
        if connectivity <= self.connectivity_threshold:
            self._phase = RagnarokPhase.COLLAPSE
            
            # Preserve seed before collapse
            self._preserve_seed()
            
            return {
                "transition": "BREAKING → COLLAPSE",
                "events": events,
                "connectivity": connectivity
            }
        
        return {"events": events, "connectivity": connectivity}
    
    def _tick_collapse(self, dt: float) -> Dict:
        """Collapse phase - graph partitions."""
        events = []
        
        # Break all remaining edges
        for edge in self.yggdrasil.edges:
            if edge._active:
                edge.break_edge()
                events.append(f"Final edge {edge.name} severed")
        
        # Activate void
        self.void.activate()
        self._phase = RagnarokPhase.VOID
        
        return {
            "transition": "COLLAPSE → VOID",
            "events": events,
            "message": "Worlds submerged in Ginnungagap"
        }
    
    def _tick_void(self, dt: float) -> Dict:
        """Void phase - Ginnungagap state."""
        # Store seed in void
        if self._seed:
            self.void.store_seed(self._seed)
        
        # After brief void period, begin rebirth
        self._phase = RagnarokPhase.REBIRTH
        
        return {
            "transition": "VOID → REBIRTH",
            "message": "Earth rising green from the waters"
        }
    
    def _tick_rebirth(self, dt: float) -> Dict:
        """Rebirth phase - new world emerges."""
        # Spawn new Yggdrasil
        new_ygg = self.void.spawn_new_world()
        
        if new_ygg is not None:
            self.yggdrasil = new_ygg
            
            # Reset components
            self.fimbulwinter = FimbulwinterState()
            self.bonds = BondSystem()
            
            self._phase = RagnarokPhase.NORMAL
            self._cycles_completed += 1
            
            return {
                "transition": "REBIRTH → NORMAL",
                "message": "New cycle begins",
                "cycle": self._cycles_completed,
                "seed_preserved": self._seed is not None
            }
        
        return {"error": "Rebirth failed"}
    
    def _preserve_seed(self) -> None:
        """
        Preserve seed for rebirth (Lif and Lifthrasir).
        
        Keeps kernel parameters, purges runtime data.
        """
        self._seed = {
            "n_worlds": 9,
            "n_edges": len(self.yggdrasil.edges),
            "cycle": self._cycles_completed,
            "kernel_version": "1.0"
        }
    
    def force_ragnarok(self) -> None:
        """Force immediate Ragnarök (for testing)."""
        self._phase = RagnarokPhase.FIMBULWINTER
        self.fimbulwinter.temperature = 0.01
    
    @property
    def phase(self) -> RagnarokPhase:
        return self._phase
    
    @property
    def cycles(self) -> int:
        return self._cycles_completed


# =============================================================================
# VALHALLA SELECTION
# =============================================================================

@dataclass
class Einherjar:
    """
    An Einherjar: Warrior selected for Valhalla.
    
    High-value agent undergoing iterative training
    for system defense at Ragnarök.
    """
    
    name: str
    valor: float  # Selection criterion
    
    # Training state
    battles_fought: int = 0
    skills: Dict[str, float] = field(default_factory=dict)
    
    def train(self, skill: str, intensity: float = 1.0) -> None:
        """Train a skill."""
        if skill not in self.skills:
            self.skills[skill] = 0.0
        
        # Diminishing returns
        current = self.skills[skill]
        gain = intensity * (1 - current) * 0.1
        self.skills[skill] = min(1.0, current + gain)
    
    def battle(self) -> float:
        """
        Fight a training battle.
        
        Returns performance score.
        """
        self.battles_fought += 1
        
        # Performance based on skills
        skill_avg = np.mean(list(self.skills.values())) if self.skills else 0.5
        noise = np.random.randn() * 0.1
        
        return self.valor * skill_avg + noise
    
    @property
    def total_skill(self) -> float:
        return sum(self.skills.values())


class Valhalla:
    """
    Valhalla: Reinforcement Learning Environment.
    
    High-value agents (Einherjar) undergo iterative
    training epochs for terminal event defense.
    """
    
    def __init__(self, capacity: int = 432000):
        self.capacity = capacity  # Half go to Folkvangr
        self._einherjar: List[Einherjar] = []
        self._training_epoch = 0
    
    def select(self, candidate_name: str, valor: float) -> bool:
        """
        Select a warrior for Valhalla.
        
        Selection based on valor in death.
        """
        if len(self._einherjar) >= self.capacity:
            # Replace weakest if new is stronger
            weakest = min(self._einherjar, key=lambda e: e.valor)
            if valor > weakest.valor:
                self._einherjar.remove(weakest)
            else:
                return False
        
        self._einherjar.append(Einherjar(candidate_name, valor))
        return True
    
    def train_epoch(self, skills: List[str] = None) -> Dict:
        """
        Run one training epoch for all Einherjar.
        
        Returns epoch statistics.
        """
        if skills is None:
            skills = ["combat", "strategy", "endurance", "runes"]
        
        total_performance = 0.0
        
        for einherjar in self._einherjar:
            # Train random skill
            skill = np.random.choice(skills)
            einherjar.train(skill)
            
            # Battle
            performance = einherjar.battle()
            total_performance += performance
        
        self._training_epoch += 1
        
        return {
            "epoch": self._training_epoch,
            "n_warriors": len(self._einherjar),
            "avg_performance": total_performance / len(self._einherjar) if self._einherjar else 0,
            "total_skill": sum(e.total_skill for e in self._einherjar)
        }
    
    def get_army_strength(self) -> float:
        """Get total army strength for Ragnarök."""
        return sum(e.valor * (1 + e.total_skill) for e in self._einherjar)
    
    @property
    def n_warriors(self) -> int:
        return len(self._einherjar)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_ragnarok() -> bool:
    """Validate Norse ragnarok module."""
    
    # Test FimbulwinterState
    fimbul = FimbulwinterState()
    assert fimbul.temperature == 1.0
    
    fimbul.cool(10.0)
    assert fimbul.temperature < 1.0
    assert fimbul.entropy > 0
    
    # Cool until frozen
    for _ in range(100):
        fimbul.cool(1.0)
    assert fimbul.is_frozen()
    
    # Test Bond
    bond = Bond("test", 5.0, ("A", "B"))
    assert bond.is_intact
    assert bond.integrity == 1.0
    
    bond.apply_strain(2.0)
    assert bond.integrity < 1.0
    assert bond.is_intact
    
    bond.apply_strain(4.0)
    assert not bond.is_intact
    
    # Test BondSystem
    bonds = BondSystem()
    assert bonds.n_intact > 0
    
    bonds.apply_global_strain(20.0)
    assert bonds.n_broken > 0
    
    # Test RagnarokEngine
    ygg = Yggdrasil()
    engine = RagnarokEngine(ygg)
    
    assert engine.phase == RagnarokPhase.NORMAL
    
    # Check stability
    is_stable, diag = engine.check_stability()
    assert "connectivity" in diag
    assert "entropy" in diag
    
    # Run normal tick
    result = engine.tick(1.0)
    assert "phase" in result
    
    # Force Ragnarök
    engine.force_ragnarok()
    assert engine.phase == RagnarokPhase.FIMBULWINTER
    
    # Run through full cycle
    for _ in range(50):
        result = engine.tick(1.0)
        if engine.phase == RagnarokPhase.NORMAL and engine.cycles > 0:
            break
    
    assert engine.cycles >= 1
    
    # Test Einherjar
    einherjar = Einherjar("TestWarrior", 0.8)
    
    einherjar.train("combat", 1.0)
    assert einherjar.skills["combat"] > 0
    
    perf = einherjar.battle()
    assert einherjar.battles_fought == 1
    
    # Test Valhalla
    valhalla = Valhalla(capacity=100)
    
    for i in range(50):
        valhalla.select(f"Warrior_{i}", np.random.random())
    
    assert valhalla.n_warriors == 50
    
    epoch_stats = valhalla.train_epoch()
    assert epoch_stats["epoch"] == 1
    assert epoch_stats["n_warriors"] == 50
    
    strength = valhalla.get_army_strength()
    assert strength > 0
    
    return True


if __name__ == "__main__":
    print("Validating Norse Ragnarök Module...")
    assert validate_ragnarok()
    print("✓ Norse Ragnarök Module validated")

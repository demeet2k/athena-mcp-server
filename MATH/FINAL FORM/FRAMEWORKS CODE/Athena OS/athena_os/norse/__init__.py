"""
ATHENA OS - NORSE: YGGDRASIL GRAPH THEORY
==========================================
Weighted Directed Graphs / Non-Markovian Memory
Function: Path-Dependent Causality & System Reset

THE NORSE COMPUTATION ENGINE:
    A cosmos defined by rigorous connectivity, inevitable
    causality, and cyclical destruction. Focuses on
    structural integrity and the weight of historical action.

CORE MODULES:

1. TOPOLOGY - The Nine Worlds Graph G_Ygg = (V, E)
   - 9 Worlds (vertices) with energy tiers
   - Weighted, directed edges (roots, bridges)
   - Impedance-based access control
   - Bifröst as high-pass filter

2. WYRD - Non-Markovian Dynamics
   - History Integral: ∫K(t,τ)·S(τ)dτ
   - Norn Operators: Urd, Verdandi, Skuld
   - Web of Urd (Memory Kernel)
   - Path-dependent causality

3. RUNES - Elder Futhark Operator Algebra ℜ₂₄
   - 24 transformation operators
   - Three Aettir (Freya, Heimdall, Tyr)
   - Runecasting as Wyrd query
   - Non-abelian composition

4. RAGNARÖK - Phase Transitions and Reset
   - Fimbulwinter cooling phase
   - Bond breaking mechanics
   - Graph collapse and rebirth
   - Valhalla selection algorithm

5. SOUL STACK - Composite Agent Architecture
   - Lic (Hardware/Body)
   - Hamr (Shape/Interface) - shapeshifting
   - Hugr (Mind/Processor) - astral travel
   - Fylgja (Daemon/Pattern) - premonition

6. SEIÐR - Harmonic Distortion Protocol
   - Galdr (chanting) as driving force
   - Thread spinning and knotting
   - Resonance manipulation
   - Odin Protocol for knowledge acquisition

SYSTEM FUNCTIONS:
    calculate_wyrd_path(): History integrator
    invoke_berserk_state(): Overclock agent
    sacrifice_for_knowledge(): Exchange integrity for access
"""

from __future__ import annotations

# =============================================================================
# TOPOLOGY MODULE
# =============================================================================

from .topology import (
    # Enums
    WorldTier,
    WorldFunction,
    
    # World (Node)
    World,
    create_nine_worlds,
    
    # Edge
    Edge,
    create_world_edges,
    
    # Graph
    Yggdrasil,
    
    # Void
    Ginnungagap,
    
    validate_topology,
)

# =============================================================================
# WYRD MODULE
# =============================================================================

from .wyrd import (
    # History
    HistoryEvent,
    WebOfUrd,
    
    # Norns
    NornOperator,
    Norn,
    URD, VERDANDI, SKULD,
    
    # State
    WyrdState,
    WyrdSystem,
    
    validate_wyrd,
)

# =============================================================================
# RUNES MODULE
# =============================================================================

from .runes import (
    # Enums
    Aett,
    RuneElement,
    
    # Rune
    Rune,
    create_elder_futhark,
    
    # Operators
    RuneOperator,
    RuneCast,
    FutharkAlgebra,
    
    validate_runes,
)

# =============================================================================
# RAGNARÖK MODULE
# =============================================================================

from .ragnarok import (
    # Phases
    RagnarokPhase,
    
    # Fimbulwinter
    FimbulwinterState,
    
    # Bonds
    Bond,
    BondSystem,
    
    # Engine
    RagnarokEngine,
    
    # Valhalla
    Einherjar,
    Valhalla,
    
    validate_ragnarok,
)

# =============================================================================
# SOUL STACK MODULE
# =============================================================================

from .soul_stack import (
    # Enums
    SoulComponentType,
    HamrForm,
    FylgjaType,
    
    # Components
    Lic,
    Hamr,
    Hugr,
    Fylgja,
    
    # Complete Stack
    NorseSoul,
    
    # Berserker
    BerserkerState,
    
    validate_soul_stack,
)

# =============================================================================
# SEIÐR MODULE
# =============================================================================

from .seidr import (
    # Enums
    SeidrType,
    GaldrMode,
    
    # Probability Field
    ProbabilityField,
    
    # Galdr
    Galdr,
    
    # Threads
    WyrdThread,
    
    # Practitioner
    Volva,
    
    # Odin Protocol
    OdinProtocol,
    
    validate_seidr,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_norse() -> bool:
    """Validate complete Norse module."""
    assert validate_topology()
    assert validate_wyrd()
    assert validate_runes()
    assert validate_ragnarok()
    assert validate_soul_stack()
    assert validate_seidr()
    return True


# =============================================================================
# CONVENIENCE CLASSES
# =============================================================================

class NorseComputer:
    """
    Complete Norse Computation Engine.
    
    Integrates Yggdrasil topology, Wyrd dynamics,
    Futhark algebra, and Ragnarök management.
    """
    
    def __init__(self):
        # Build Yggdrasil
        self.yggdrasil = Yggdrasil()
        
        # Wyrd system
        self.wyrd = WyrdSystem(state_dimension=16)
        
        # Rune algebra
        self.futhark = FutharkAlgebra(dimension=8)
        
        # Ragnarök engine
        self.ragnarok = RagnarokEngine(self.yggdrasil)
        
        # Global time
        self._time = 0.0
    
    def create_agent(self, name: str, 
                    fylgja_type: FylgjaType = FylgjaType.WOLF) -> NorseSoul:
        """Create a new agent with full soul stack."""
        return NorseSoul(name, fylgja_type)
    
    def create_volva(self, name: str, power: float = 1.0) -> Volva:
        """Create a Seiðr practitioner."""
        return Volva(name, power)
    
    def calculate_wyrd_path(self, actions: list, 
                           source: str = "agent") -> Dict:
        """
        The calculate_wyrd_path() system call.
        
        Computes consequence of actions relative to history.
        """
        # Record actions
        for i, action in enumerate(actions):
            self.wyrd.record_action(
                action=str(action),
                magnitude=1.0,
                source=source
            )
        
        # Compute wyrd path
        action_vec = np.random.randn(16)  # Simplified
        return self.wyrd.compute_wyrd_path(action_vec)
    
    def cast_runes(self, n: int = 3) -> Dict:
        """Cast runes and interpret."""
        cast = self.futhark.cast_runes(n)
        return cast.interpret()
    
    def traverse_worlds(self, source: str, target: str,
                       entity_type: str = "mortal",
                       energy: float = 1.0) -> Tuple[bool, float]:
        """Traverse between worlds."""
        src_world = self.yggdrasil.get_world_by_name(source)
        tgt_world = self.yggdrasil.get_world_by_name(target)
        
        if src_world is None or tgt_world is None:
            return False, 0.0
        
        return self.yggdrasil.traverse(
            src_world.index, tgt_world.index,
            entity_energy=energy,
            entity_type=entity_type
        )
    
    def tick(self, dt: float = 1.0) -> Dict:
        """Advance simulation."""
        self._time += dt
        
        # Update Yggdrasil
        self.yggdrasil.tick(dt)
        
        # Update Wyrd
        wyrd_stats = self.wyrd.tick(dt)
        
        # Update Ragnarök
        ragnarok_stats = self.ragnarok.tick(dt)
        
        return {
            "time": self._time,
            "wyrd": wyrd_stats,
            "ragnarok": ragnarok_stats,
            "phase": self.ragnarok.phase.value
        }
    
    def get_system_status(self) -> Dict:
        """Get overall system status."""
        is_stable, diagnostics = self.ragnarok.check_stability()
        
        return {
            "time": self._time,
            "stable": is_stable,
            "phase": self.ragnarok.phase.value,
            "cycles": self.ragnarok.cycles,
            "connectivity": diagnostics["connectivity"],
            "entropy": diagnostics["entropy"],
            "fatalism": self.wyrd.get_fatalism_index()
        }
    
    @property
    def time(self) -> float:
        return self._time


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Topology
    "WorldTier", "WorldFunction",
    "World", "create_nine_worlds",
    "Edge", "create_world_edges",
    "Yggdrasil", "Ginnungagap",
    
    # Wyrd
    "HistoryEvent", "WebOfUrd",
    "NornOperator", "Norn",
    "URD", "VERDANDI", "SKULD",
    "WyrdState", "WyrdSystem",
    
    # Runes
    "Aett", "RuneElement",
    "Rune", "create_elder_futhark",
    "RuneOperator", "RuneCast", "FutharkAlgebra",
    
    # Ragnarök
    "RagnarokPhase", "FimbulwinterState",
    "Bond", "BondSystem",
    "RagnarokEngine",
    "Einherjar", "Valhalla",
    
    # Soul Stack
    "SoulComponentType", "HamrForm", "FylgjaType",
    "Lic", "Hamr", "Hugr", "Fylgja",
    "NorseSoul", "BerserkerState",
    
    # Seiðr
    "SeidrType", "GaldrMode",
    "ProbabilityField", "Galdr", "WyrdThread",
    "Volva", "OdinProtocol",
    
    # Integration
    "NorseComputer",
    
    # Validation
    "validate_norse",
]

__version__ = "1.0.0"
__module_name__ = "norse"


if __name__ == "__main__":
    print("=" * 70)
    print("ATHENA OS - NORSE: YGGDRASIL GRAPH THEORY")
    print("Weighted Directed Graphs / Non-Markovian Memory")
    print("=" * 70)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_norse():
        print("✓ All components validated")
    
    # Demo
    print("\n--- Norse Computer Demo ---")
    
    computer = NorseComputer()
    
    # Yggdrasil info
    print(f"\nYggdrasil Graph:")
    print(f"  Worlds: {len(computer.yggdrasil.worlds)}")
    print(f"  Edges: {len(computer.yggdrasil.edges)}")
    print(f"  Connectivity: {computer.yggdrasil.get_connectivity():.2f}")
    
    # World traversal
    print(f"\nWorld Traversal:")
    success, cost = computer.traverse_worlds("Midgard", "Asgard", "god", 1.0)
    print(f"  Midgard → Asgard (as god): {success}, cost={cost:.2f}")
    
    success, cost = computer.traverse_worlds("Midgard", "Asgard", "mortal", 1.0)
    print(f"  Midgard → Asgard (as mortal): {success}")
    
    # Runecast
    print(f"\nRunecast:")
    cast = computer.cast_runes(3)
    print(f"  Runes: {cast['glyphs']} ({', '.join(cast['runes'])})")
    print(f"  Meanings: {cast['meanings']}")
    if "position_reading" in cast:
        print(f"  Reading: Past={cast['position_reading'].get('past', 'N/A')}")
    
    # Wyrd path
    print(f"\nWyrd Path Calculation:")
    path = computer.calculate_wyrd_path(["travel", "fight", "sacrifice"])
    print(f"  History weight: {path['history_weight']:.2f}")
    print(f"  Freedom: {path['freedom']:.2%}")
    print(f"  Determinism: {path['determinism']:.2%}")
    
    # System status
    print(f"\nSystem Status:")
    status = computer.get_system_status()
    print(f"  Phase: {status['phase']}")
    print(f"  Stable: {status['stable']}")
    print(f"  Entropy: {status['entropy']:.4f}")
    
    # Create agent
    print(f"\nAgent Creation:")
    agent = computer.create_agent("Ragnar", FylgjaType.WOLF)
    state = agent.get_state()
    print(f"  Name: {state['name']}")
    print(f"  True Nature: {state['true_nature']}")
    print(f"  Alive: {state['alive']}")
    
    print("\n" + "=" * 70)


# Type hints
from typing import Dict, Any, Tuple
import numpy as np

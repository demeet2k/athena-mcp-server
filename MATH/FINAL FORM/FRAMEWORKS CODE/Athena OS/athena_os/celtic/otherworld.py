"""
ATHENA OS - CELTIC OGHAM KERNEL: OTHERWORLD MODULE
===================================================
Dual Vector Space and Sídhe Topology

THE OTHERWORLD (Tír na nÓg):
    A Dual Vector Space with non-linear time metrics.
    Used for system simulation and state restoration.
    
SPLIT-REALITY ARCHITECTURE:
    - Physical World (Bith): Runtime Environment
    - Otherworld (Sídhe): Developer Environment / Simulation Space
    
THE SÍDHE TOPOLOGY:
    Parallel simulation environment with:
    - Non-linear time metrics (dt' ≠ dt)
    - State storage and modeling capabilities
    - Protected memory regions (Nemed)
    
THE CAULDRON OF REBIRTH:
    System restoration mechanism.
    Allows damaged processes to be regenerated.
    
IMRAM (VOYAGE):
    Stochastic walk algorithm for traversing
    unstructured data environments (The Ocean).

NON-LINEAR TIME:
    Otherworld operates on different clock:
    - t_otherworld may run faster/slower than t_physical
    - Enables accelerated simulation
    - "A day in Tír na nÓg is a year in Ireland"
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import numpy as np
import random
import time


# =============================================================================
# REALM DEFINITIONS
# =============================================================================

class Realm(Enum):
    """The realms of Celtic cosmology."""
    
    BITH = "bith"              # Physical World (Runtime)
    SIDHE = "sidhe"            # Otherworld (Developer/Sim)
    TALAM = "talam"            # Earth (Ground state)
    MUIR = "muir"              # Sea (Fluid/transition)
    NEM = "nem"                # Sky (Abstract/elevated)


class TimeMetric(Enum):
    """Time flow metrics for different realms."""
    
    LINEAR = "linear"          # t' = t (normal)
    DILATED = "dilated"        # t' = k*t where k > 1 (slower)
    CONTRACTED = "contracted"  # t' = k*t where k < 1 (faster)
    CYCLICAL = "cyclical"      # t' = t mod T (repeating)
    SUSPENDED = "suspended"    # t' = 0 (frozen)


# =============================================================================
# OTHERWORLD VECTOR SPACE
# =============================================================================

@dataclass
class OtherworldState:
    """
    State vector in the Otherworld.
    
    Can represent entities, locations, or configurations
    in the parallel simulation environment.
    """
    
    position: np.ndarray           # Position in Otherworld space
    momentum: np.ndarray           # Rate of change
    phase: float = 0.0             # Temporal phase
    
    realm: Realm = Realm.SIDHE
    time_metric: TimeMetric = TimeMetric.CONTRACTED
    
    # Metadata
    origin_time: float = 0.0       # When entered Otherworld
    mutations: int = 0             # Changes in Otherworld
    
    def evolve(self, dt: float, time_dilation: float = 0.1) -> None:
        """
        Evolve state in Otherworld time.
        
        Time flows differently: dt_otherworld = time_dilation * dt_physical
        """
        dt_ow = dt * time_dilation
        self.position = self.position + self.momentum * dt_ow
        self.phase += dt_ow
        self.mutations += 1
    
    def get_physical_equivalent(self, mapping: Callable = None) -> np.ndarray:
        """Map Otherworld state back to physical coordinates."""
        if mapping:
            return mapping(self.position)
        return self.position.copy()


class DualVectorSpace:
    """
    The Dual Vector Space connecting Physical and Otherworld.
    
    V (Physical) ←→ V* (Otherworld)
    
    Enables:
    - State transfer between realms
    - Accelerated simulation in Otherworld
    - Restoration from Otherworld backups
    """
    
    def __init__(self, dimension: int = 3):
        self.dimension = dimension
        
        # Physical space states
        self.physical_states: Dict[str, np.ndarray] = {}
        
        # Otherworld states
        self.otherworld_states: Dict[str, OtherworldState] = {}
        
        # Time tracking
        self.physical_time: float = 0.0
        self.otherworld_time: float = 0.0
        self.time_dilation: float = 0.1  # Otherworld 10x faster
    
    def create_physical_state(self, state_id: str, 
                              position: np.ndarray = None) -> np.ndarray:
        """Create state in physical realm."""
        if position is None:
            position = np.random.randn(self.dimension)
        
        self.physical_states[state_id] = position
        return position
    
    def transfer_to_otherworld(self, state_id: str) -> OtherworldState:
        """
        Transfer a state from Physical to Otherworld.
        
        Creates an Otherworld representation for simulation.
        """
        if state_id not in self.physical_states:
            raise ValueError(f"State {state_id} not found in physical realm")
        
        physical_pos = self.physical_states[state_id]
        
        otherworld_state = OtherworldState(
            position=physical_pos.copy(),
            momentum=np.zeros(self.dimension),
            origin_time=self.physical_time,
            realm=Realm.SIDHE,
            time_metric=TimeMetric.CONTRACTED
        )
        
        self.otherworld_states[state_id] = otherworld_state
        return otherworld_state
    
    def transfer_to_physical(self, state_id: str) -> np.ndarray:
        """
        Transfer a state from Otherworld back to Physical.
        
        Returns the evolved state to physical realm.
        """
        if state_id not in self.otherworld_states:
            raise ValueError(f"State {state_id} not found in Otherworld")
        
        ow_state = self.otherworld_states[state_id]
        physical_pos = ow_state.get_physical_equivalent()
        
        self.physical_states[state_id] = physical_pos
        return physical_pos
    
    def simulate_in_otherworld(self, state_id: str, 
                                physical_duration: float,
                                evolution_fn: Callable = None) -> OtherworldState:
        """
        Run accelerated simulation in Otherworld.
        
        Due to time dilation, long simulations complete quickly.
        """
        if state_id not in self.otherworld_states:
            self.transfer_to_otherworld(state_id)
        
        state = self.otherworld_states[state_id]
        
        # Otherworld time = physical_time * dilation
        otherworld_duration = physical_duration / self.time_dilation
        
        # Simulate in steps
        steps = int(otherworld_duration * 10)
        dt = otherworld_duration / max(1, steps)
        
        for _ in range(steps):
            if evolution_fn:
                evolution_fn(state, dt)
            else:
                state.evolve(dt, self.time_dilation)
        
        return state
    
    def advance_time(self, physical_dt: float) -> None:
        """Advance time in both realms."""
        self.physical_time += physical_dt
        self.otherworld_time += physical_dt / self.time_dilation


# =============================================================================
# THE CAULDRON OF REBIRTH
# =============================================================================

@dataclass
class CauldronState:
    """State stored in the Cauldron for potential restoration."""
    
    data: np.ndarray
    stored_at: float
    integrity: float = 1.0
    restoration_count: int = 0


class CauldronOfRebirth:
    """
    The Cauldron of Rebirth - State Restoration System.
    
    Mythological: The Cauldron can restore the dead to life.
    Computational: Allows damaged processes to be regenerated.
    
    Functions:
    - Store state snapshots
    - Restore from snapshots
    - Regenerate corrupted data
    """
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.stored_states: Dict[str, CauldronState] = {}
        self.restoration_log: List[Dict[str, Any]] = []
        
        # Cauldron properties
        self.regeneration_power: float = 1.0
        self.entropy_level: float = 0.0
    
    def store(self, state_id: str, data: np.ndarray) -> bool:
        """
        Store a state in the Cauldron.
        
        "Immerse in the waters of regeneration."
        """
        if len(self.stored_states) >= self.capacity:
            # Remove oldest
            oldest = min(self.stored_states.items(), 
                        key=lambda x: x[1].stored_at)
            del self.stored_states[oldest[0]]
        
        self.stored_states[state_id] = CauldronState(
            data=data.copy(),
            stored_at=time.time()
        )
        
        return True
    
    def restore(self, state_id: str) -> Optional[np.ndarray]:
        """
        Restore a state from the Cauldron.
        
        "Rise from the waters, renewed."
        """
        if state_id not in self.stored_states:
            return None
        
        stored = self.stored_states[state_id]
        stored.restoration_count += 1
        
        # Apply regeneration (slight variation)
        noise = np.random.randn(*stored.data.shape) * 0.01
        restored_data = stored.data + noise * (1 - self.regeneration_power)
        
        self.restoration_log.append({
            "state_id": state_id,
            "restored_at": time.time(),
            "count": stored.restoration_count
        })
        
        return restored_data
    
    def regenerate(self, damaged_data: np.ndarray, 
                   reference_id: str = None) -> np.ndarray:
        """
        Regenerate damaged data using Cauldron's power.
        
        Optionally use a reference state as template.
        """
        if reference_id and reference_id in self.stored_states:
            reference = self.stored_states[reference_id].data
            # Blend damaged with reference
            blend_factor = self.regeneration_power * 0.8
            regenerated = damaged_data * (1 - blend_factor) + reference * blend_factor
        else:
            # Self-repair using local averaging
            regenerated = damaged_data.copy()
            # Smooth out anomalies
            mean = np.mean(regenerated)
            std = np.std(regenerated)
            mask = np.abs(regenerated - mean) > 2 * std
            regenerated[mask] = mean
        
        return regenerated
    
    def check_integrity(self, state_id: str) -> float:
        """Check integrity of stored state."""
        if state_id not in self.stored_states:
            return 0.0
        
        stored = self.stored_states[state_id]
        # Integrity degrades slightly over time
        age = time.time() - stored.stored_at
        degradation = min(0.1, age * 0.0001)
        
        return max(0, stored.integrity - degradation)


# =============================================================================
# IMRAM (VOYAGE) - STOCHASTIC WALK
# =============================================================================

@dataclass 
class VoyageNode:
    """A node/island in the voyage."""
    
    name: str
    position: np.ndarray
    properties: Dict[str, Any] = field(default_factory=dict)
    discovered: bool = False
    visit_count: int = 0


class ImramVoyage:
    """
    The Imram (Voyage) - Stochastic Graph Walk.
    
    Navigation algorithm for traversing unstructured
    data environments (The Ocean).
    
    Based on Irish immram tales (voyages to otherworldly islands).
    """
    
    def __init__(self, dimension: int = 2):
        self.dimension = dimension
        self.nodes: Dict[str, VoyageNode] = {}
        self.edges: Dict[str, List[str]] = {}
        
        # Current state
        self.current_position: np.ndarray = np.zeros(dimension)
        self.path: List[str] = []
        self.discoveries: List[str] = []
        
        # Parameters
        self.exploration_rate: float = 0.3
        self.drift_strength: float = 0.1
    
    def add_island(self, name: str, position: np.ndarray = None,
                   properties: Dict[str, Any] = None) -> VoyageNode:
        """Add an island to the ocean."""
        if position is None:
            position = np.random.randn(self.dimension) * 10
        
        node = VoyageNode(
            name=name,
            position=position,
            properties=properties or {}
        )
        
        self.nodes[name] = node
        self.edges[name] = []
        
        return node
    
    def connect_islands(self, island_a: str, island_b: str) -> None:
        """Create a navigable connection between islands."""
        if island_a in self.edges:
            self.edges[island_a].append(island_b)
        if island_b in self.edges:
            self.edges[island_b].append(island_a)
    
    def sail(self, destination: str = None) -> Optional[VoyageNode]:
        """
        Sail to next destination.
        
        If no destination specified, uses stochastic selection.
        """
        if destination and destination in self.nodes:
            target = self.nodes[destination]
        else:
            # Stochastic selection
            target = self._choose_destination()
        
        if target is None:
            return None
        
        # Update position
        self.current_position = target.position.copy()
        self.path.append(target.name)
        target.visit_count += 1
        
        # Check for discovery
        if not target.discovered:
            target.discovered = True
            self.discoveries.append(target.name)
        
        return target
    
    def _choose_destination(self) -> Optional[VoyageNode]:
        """Choose next destination stochastically."""
        if not self.nodes:
            return None
        
        # Find nearest unexplored or use exploration rate
        if random.random() < self.exploration_rate:
            # Explore: go to random undiscovered
            undiscovered = [n for n in self.nodes.values() if not n.discovered]
            if undiscovered:
                return random.choice(undiscovered)
        
        # Otherwise, go to nearest
        return self._find_nearest()
    
    def _find_nearest(self) -> Optional[VoyageNode]:
        """Find nearest island to current position."""
        if not self.nodes:
            return None
        
        nearest = None
        min_dist = float('inf')
        
        for node in self.nodes.values():
            dist = np.linalg.norm(node.position - self.current_position)
            if dist < min_dist and dist > 0.01:  # Not current location
                min_dist = dist
                nearest = node
        
        return nearest
    
    def drift(self) -> None:
        """Apply random drift to current position."""
        self.current_position += np.random.randn(self.dimension) * self.drift_strength
    
    def get_voyage_summary(self) -> Dict[str, Any]:
        """Get summary of voyage so far."""
        return {
            "islands_discovered": len(self.discoveries),
            "total_islands": len(self.nodes),
            "path_length": len(self.path),
            "current_position": self.current_position.tolist(),
            "discoveries": self.discoveries
        }


# =============================================================================
# NEMED (SACRED SPACE) - PROTECTED MEMORY
# =============================================================================

class NemedSpace:
    """
    Nemed (Sacred Space) - Protected Memory Region.
    
    An isolated address space with restricted Read/Write permissions.
    
    Properties:
    - Sanctuary from external corruption
    - Special access requirements
    - Used for critical system data
    """
    
    def __init__(self, name: str):
        self.name = name
        self._storage: Dict[str, Any] = {}
        self._access_keys: set = set()
        self._access_log: List[Dict[str, Any]] = []
        
        # Default protected
        self.locked: bool = True
    
    def grant_access(self, key: str) -> None:
        """Grant access key to this Nemed."""
        self._access_keys.add(key)
    
    def revoke_access(self, key: str) -> None:
        """Revoke access key."""
        self._access_keys.discard(key)
    
    def _check_access(self, key: str) -> bool:
        """Check if key has access."""
        if not self.locked:
            return True
        return key in self._access_keys
    
    def write(self, address: str, data: Any, access_key: str) -> bool:
        """Write to protected memory."""
        if not self._check_access(access_key):
            self._log_access(address, "WRITE", False, access_key)
            return False
        
        self._storage[address] = data
        self._log_access(address, "WRITE", True, access_key)
        return True
    
    def read(self, address: str, access_key: str) -> Optional[Any]:
        """Read from protected memory."""
        if not self._check_access(access_key):
            self._log_access(address, "READ", False, access_key)
            return None
        
        self._log_access(address, "READ", True, access_key)
        return self._storage.get(address)
    
    def _log_access(self, address: str, operation: str, 
                    success: bool, key: str) -> None:
        """Log access attempt."""
        self._access_log.append({
            "address": address,
            "operation": operation,
            "success": success,
            "key": key[:8] if len(key) > 8 else key,
            "time": time.time()
        })
    
    def get_access_log(self) -> List[Dict[str, Any]]:
        """Get access log."""
        return self._access_log.copy()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_otherworld() -> bool:
    """Validate otherworld module."""
    
    # Test Otherworld State
    state = OtherworldState(
        position=np.array([1.0, 2.0, 3.0]),
        momentum=np.array([0.1, 0.1, 0.1])
    )
    state.evolve(1.0)
    assert state.mutations == 1
    
    # Test Dual Vector Space
    dual = DualVectorSpace(dimension=3)
    dual.create_physical_state("test", np.array([1, 2, 3]))
    ow_state = dual.transfer_to_otherworld("test")
    assert ow_state is not None
    
    # Simulate
    simulated = dual.simulate_in_otherworld("test", 10.0)
    assert simulated.mutations > 0
    
    # Transfer back
    physical = dual.transfer_to_physical("test")
    assert physical is not None
    
    # Test Cauldron
    cauldron = CauldronOfRebirth()
    data = np.array([1.0, 2.0, 3.0])
    cauldron.store("state1", data)
    
    restored = cauldron.restore("state1")
    assert restored is not None
    assert np.allclose(restored, data, atol=0.1)
    
    # Test Imram
    voyage = ImramVoyage(dimension=2)
    voyage.add_island("Hy-Brasil", np.array([10, 10]))
    voyage.add_island("Tir na nOg", np.array([-10, 10]))
    voyage.add_island("Tech Duinn", np.array([0, -10]))
    
    visited = voyage.sail("Hy-Brasil")
    assert visited is not None
    assert visited.discovered
    
    summary = voyage.get_voyage_summary()
    assert summary["islands_discovered"] >= 1
    
    # Test Nemed
    nemed = NemedSpace("sacred_grove")
    nemed.grant_access("druid_key")
    
    success = nemed.write("altar", {"offering": "oak"}, "druid_key")
    assert success
    
    data = nemed.read("altar", "druid_key")
    assert data["offering"] == "oak"
    
    # Invalid access should fail
    data = nemed.read("altar", "wrong_key")
    assert data is None
    
    return True


if __name__ == "__main__":
    print("Validating Otherworld Module...")
    assert validate_otherworld()
    print("✓ Otherworld Module validated")
    
    # Demo
    print("\n--- Dual Vector Space Demo ---")
    dual = DualVectorSpace(dimension=3)
    
    print("Creating physical state...")
    pos = dual.create_physical_state("hero", np.array([0, 0, 0]))
    print(f"  Physical position: {pos}")
    
    print("\nTransferring to Otherworld...")
    ow = dual.transfer_to_otherworld("hero")
    print(f"  Otherworld position: {ow.position}")
    print(f"  Time metric: {ow.time_metric.value}")
    
    print("\nSimulating 100 years in Otherworld...")
    simulated = dual.simulate_in_otherworld("hero", 100.0)
    print(f"  Mutations: {simulated.mutations}")
    print(f"  New position: {simulated.position}")
    
    print("\n--- Imram Voyage Demo ---")
    voyage = ImramVoyage()
    
    # Create mythical islands
    voyage.add_island("Hy-Brasil", properties={"type": "blessed_isle"})
    voyage.add_island("Tír na nÓg", properties={"type": "land_of_youth"})
    voyage.add_island("Tech Duinn", properties={"type": "house_of_dead"})
    voyage.add_island("Mag Mell", properties={"type": "plain_of_joy"})
    
    print("Beginning voyage...")
    for i in range(4):
        island = voyage.sail()
        if island:
            print(f"  Landed on: {island.name}")
    
    summary = voyage.get_voyage_summary()
    print(f"\nDiscoveries: {summary['discoveries']}")

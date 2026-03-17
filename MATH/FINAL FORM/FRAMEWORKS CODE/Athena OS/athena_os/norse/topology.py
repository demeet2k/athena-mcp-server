"""
ATHENA OS - NORSE: TOPOLOGY MODULE
===================================
The Nine Worlds Graph (Yggdrasil Manifold)

G_Ygg = (V, E) where:
    V = 9 discrete topological spaces (Nine Worlds)
    E = Weighted, directed edges (Roots, Bridges)

THE NINE WORLDS (Vertices):
    Upper Tier (Φ > 0):
        - Asgard: Control Plane, SYS_ADMIN
        - Vanaheim: Field Dynamics, Analog Processing
        - Alfheim: Light Computation
    
    Middle Tier (Φ ≈ 0):
        - Midgard: User Space, Simulation Layer
        - Jotunheim: Chaotic Processing
        - Svartalfheim: Dark Computation
    
    Lower Tier (Φ < 0):
        - Niflheim: Cold Storage, Ice
        - Muspelheim: Energy Source, Fire
        - Hel: Archive/Garbage Collection

EDGES (Connections):
    - Bifröst: High-pass filter (Asgard ↔ Midgard)
    - Roots: Low-impedance high-bandwidth vertical links
    - Gjallarbrú: Hel access point

IMPEDANCE FUNCTION:
    T_ij = (1 / Z_ij) · ΔΦ_ij
    
    Access requires specific energy/authorization levels.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
from collections import deque


# =============================================================================
# WORLD TIERS
# =============================================================================

class WorldTier(Enum):
    """Energy tiers of the Nine Worlds."""
    
    UPPER = "upper"     # Φ > 0 (High potential)
    MIDDLE = "middle"   # Φ ≈ 0 (Neutral)
    LOWER = "lower"     # Φ < 0 (Negative potential)
    
    @property
    def potential_range(self) -> Tuple[float, float]:
        ranges = {
            WorldTier.UPPER: (0.5, 1.0),
            WorldTier.MIDDLE: (-0.2, 0.2),
            WorldTier.LOWER: (-1.0, -0.5)
        }
        return ranges[self]


class WorldFunction(Enum):
    """Computational function of each world."""
    
    CONTROL = "control"         # SYS_ADMIN / KERNEL
    FIELD = "field"             # Analog / Flow dynamics
    LIGHT = "light"             # Light computation
    USER = "user"               # User space / Simulation
    CHAOS = "chaos"             # Chaotic processing
    DARK = "dark"               # Dark computation
    COLD = "cold"               # Cold storage
    ENERGY = "energy"           # Energy source
    ARCHIVE = "archive"         # Garbage collection / Archive


# =============================================================================
# WORLD NODE
# =============================================================================

@dataclass
class World:
    """
    A World (node) in the Yggdrasil Graph.
    
    Each world is a discrete topological space with
    local physics and computational function.
    """
    
    index: int                      # 0-8
    name: str                       # World name
    old_norse: str                  # Old Norse name
    tier: WorldTier                 # Energy tier
    function: WorldFunction         # Computational role
    
    # Energy state
    potential: float = 0.0          # Φ (potential energy)
    entropy: float = 0.0            # Local entropy
    
    # Local constants
    time_dilation: float = 1.0      # Time flows differently
    
    # State
    _data: Dict[str, Any] = field(default_factory=dict)
    _processes: List[Any] = field(default_factory=list)
    
    def store(self, key: str, value: Any) -> None:
        """Store data in this world."""
        self._data[key] = value
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from this world."""
        return self._data.get(key)
    
    def spawn_process(self, process: Any) -> None:
        """Spawn a process in this world."""
        self._processes.append(process)
    
    def tick(self, dt: float = 1.0) -> None:
        """Advance local time by dt."""
        # Apply time dilation
        local_dt = dt * self.time_dilation
        
        # Entropy increases
        self.entropy += 0.01 * local_dt
    
    @property
    def is_stable(self) -> bool:
        """Check if world is stable (entropy below threshold)."""
        return self.entropy < 1.0


# =============================================================================
# THE NINE WORLDS
# =============================================================================

def create_nine_worlds() -> Dict[int, World]:
    """
    Create the Nine Worlds of Norse cosmology.
    
    Each world is a discrete address space.
    """
    return {
        # Upper Tier (Control)
        0: World(
            index=0,
            name="Asgard",
            old_norse="Ásgarðr",
            tier=WorldTier.UPPER,
            function=WorldFunction.CONTROL,
            potential=1.0,
            time_dilation=0.5  # Time flows slower
        ),
        1: World(
            index=1,
            name="Vanaheim",
            old_norse="Vanaheimr",
            tier=WorldTier.UPPER,
            function=WorldFunction.FIELD,
            potential=0.8,
            time_dilation=0.7
        ),
        2: World(
            index=2,
            name="Alfheim",
            old_norse="Álfheimr",
            tier=WorldTier.UPPER,
            function=WorldFunction.LIGHT,
            potential=0.6,
            time_dilation=0.6
        ),
        
        # Middle Tier (User Space)
        3: World(
            index=3,
            name="Midgard",
            old_norse="Miðgarðr",
            tier=WorldTier.MIDDLE,
            function=WorldFunction.USER,
            potential=0.0,
            time_dilation=1.0  # Normal time
        ),
        4: World(
            index=4,
            name="Jotunheim",
            old_norse="Jötunheimr",
            tier=WorldTier.MIDDLE,
            function=WorldFunction.CHAOS,
            potential=-0.1,
            time_dilation=1.2
        ),
        5: World(
            index=5,
            name="Svartalfheim",
            old_norse="Svartálfaheimr",
            tier=WorldTier.MIDDLE,
            function=WorldFunction.DARK,
            potential=-0.15,
            time_dilation=1.1
        ),
        
        # Lower Tier (Infrastructure)
        6: World(
            index=6,
            name="Niflheim",
            old_norse="Niflheimr",
            tier=WorldTier.LOWER,
            function=WorldFunction.COLD,
            potential=-0.8,
            time_dilation=2.0  # Time flows faster (entropy)
        ),
        7: World(
            index=7,
            name="Muspelheim",
            old_norse="Múspellsheimr",
            tier=WorldTier.LOWER,
            function=WorldFunction.ENERGY,
            potential=-0.7,
            time_dilation=0.3  # Energy source - stable
        ),
        8: World(
            index=8,
            name="Hel",
            old_norse="Helheimr",
            tier=WorldTier.LOWER,
            function=WorldFunction.ARCHIVE,
            potential=-1.0,
            time_dilation=10.0  # Time flies - archive
        )
    }


# =============================================================================
# EDGE (PATH/BRIDGE)
# =============================================================================

@dataclass
class Edge:
    """
    An edge connecting two worlds.
    
    Edges have impedance and direction.
    """
    
    name: str
    source: int                     # Source world index
    target: int                     # Target world index
    
    # Properties
    impedance: float = 1.0          # Z (resistance to traversal)
    bidirectional: bool = True      # Can traverse both ways
    
    # Access control
    min_energy: float = 0.0         # Minimum energy to traverse
    authorized_types: Set[str] = field(default_factory=set)
    
    # State
    _active: bool = True
    _traffic: float = 0.0
    
    def can_traverse(self, entity_energy: float, 
                    entity_type: str = "mortal") -> bool:
        """Check if entity can traverse this edge."""
        if not self._active:
            return False
        
        if entity_energy < self.min_energy:
            return False
        
        if self.authorized_types and entity_type not in self.authorized_types:
            return False
        
        return True
    
    def traverse(self, entity_energy: float) -> Tuple[bool, float]:
        """
        Attempt to traverse the edge.
        
        Returns (success, energy_cost).
        """
        if not self._active:
            return False, 0.0
        
        # Energy cost based on impedance
        cost = self.impedance * 0.1
        
        if entity_energy < cost:
            return False, 0.0
        
        self._traffic += 1.0
        return True, cost
    
    def damage(self, amount: float) -> None:
        """Damage the edge (increase impedance)."""
        self.impedance += amount
    
    def break_edge(self) -> None:
        """Break the edge (Ragnarök precursor)."""
        self._active = False
    
    @property
    def transmission_rate(self) -> float:
        """Get transmission rate (inverse of impedance)."""
        return 1.0 / self.impedance if self.impedance > 0 else float('inf')


def create_world_edges() -> List[Edge]:
    """
    Create the edges (paths/bridges) of Yggdrasil.
    
    These are the transmission channels between worlds.
    """
    return [
        # Bifröst (Rainbow Bridge) - Asgard ↔ Midgard
        Edge(
            name="Bifröst",
            source=0, target=3,
            impedance=2.0,
            bidirectional=True,
            min_energy=0.5,
            authorized_types={"god", "einherjar", "valkyrie"}
        ),
        
        # Root connections (Yggdrasil's roots)
        Edge(name="Root_Upper", source=0, target=6, impedance=0.5),  # Asgard-Niflheim
        Edge(name="Root_Middle", source=3, target=4, impedance=0.3),  # Midgard-Jotunheim
        Edge(name="Root_Lower", source=6, target=7, impedance=0.4),  # Niflheim-Muspelheim
        
        # Gjallarbrú (Bridge to Hel)
        Edge(
            name="Gjallarbrú",
            source=6, target=8,
            impedance=0.1,
            bidirectional=False,  # One-way to Hel
            min_energy=0.0
        ),
        
        # Inter-tier connections
        Edge(name="Path_Vanaheim", source=0, target=1, impedance=0.3),
        Edge(name="Path_Alfheim", source=0, target=2, impedance=0.3),
        Edge(name="Path_Svartalfheim", source=3, target=5, impedance=0.4),
        Edge(name="Path_Jotunheim_Nifl", source=4, target=6, impedance=0.5),
        
        # Energy flow (Muspelheim as source)
        Edge(name="Fire_Flow", source=7, target=3, impedance=0.8),
        Edge(name="Ice_Flow", source=6, target=3, impedance=0.8),
        
        # Vanaheim-Alfheim (upper tier mesh)
        Edge(name="Upper_Mesh", source=1, target=2, impedance=0.2),
    ]


# =============================================================================
# YGGDRASIL GRAPH
# =============================================================================

class Yggdrasil:
    """
    The Complete Yggdrasil Graph.
    
    G_Ygg = (V, E) with V=9 worlds, E=weighted edges.
    
    The World Tree serves as the central bus/server,
    determining routing between discrete domains.
    """
    
    def __init__(self):
        # Build graph
        self._worlds = create_nine_worlds()
        self._edges = create_world_edges()
        
        # Build adjacency structures
        self._adjacency: Dict[int, List[Edge]] = {i: [] for i in range(9)}
        self._edge_map: Dict[Tuple[int, int], List[Edge]] = {}
        
        for edge in self._edges:
            self._adjacency[edge.source].append(edge)
            
            key = (edge.source, edge.target)
            if key not in self._edge_map:
                self._edge_map[key] = []
            self._edge_map[key].append(edge)
            
            if edge.bidirectional:
                self._adjacency[edge.target].append(edge)
                rev_key = (edge.target, edge.source)
                if rev_key not in self._edge_map:
                    self._edge_map[rev_key] = []
                self._edge_map[rev_key].append(edge)
        
        # State
        self._global_entropy = 0.0
        self._time = 0.0
    
    def get_world(self, index: int) -> Optional[World]:
        """Get world by index."""
        return self._worlds.get(index)
    
    def get_world_by_name(self, name: str) -> Optional[World]:
        """Get world by name."""
        for world in self._worlds.values():
            if world.name.lower() == name.lower():
                return world
        return None
    
    def get_edges(self, source: int, target: int) -> List[Edge]:
        """Get all edges between two worlds."""
        return self._edge_map.get((source, target), [])
    
    def get_outgoing_edges(self, world: int) -> List[Edge]:
        """Get all edges from a world."""
        return self._adjacency.get(world, [])
    
    def find_path(self, source: int, target: int,
                 entity_energy: float = 1.0,
                 entity_type: str = "mortal") -> Optional[List[int]]:
        """
        Find path between worlds using BFS.
        
        Respects edge access restrictions.
        """
        if source == target:
            return [source]
        
        visited = {source}
        queue = deque([(source, [source])])
        
        while queue:
            current, path = queue.popleft()
            
            for edge in self._adjacency[current]:
                # Determine next world
                if edge.source == current:
                    next_world = edge.target
                else:
                    next_world = edge.source
                
                if next_world in visited:
                    continue
                
                # Check if can traverse
                if not edge.can_traverse(entity_energy, entity_type):
                    continue
                
                new_path = path + [next_world]
                
                if next_world == target:
                    return new_path
                
                visited.add(next_world)
                queue.append((next_world, new_path))
        
        return None
    
    def traverse(self, source: int, target: int,
                entity_energy: float, entity_type: str = "mortal") -> Tuple[bool, float]:
        """
        Traverse from source to target world.
        
        Returns (success, total_energy_cost).
        """
        path = self.find_path(source, target, entity_energy, entity_type)
        
        if path is None:
            return False, 0.0
        
        total_cost = 0.0
        current_energy = entity_energy
        
        for i in range(len(path) - 1):
            src, tgt = path[i], path[i + 1]
            edges = self.get_edges(src, tgt)
            
            if not edges:
                return False, total_cost
            
            # Use best (lowest impedance) edge
            best_edge = min(edges, key=lambda e: e.impedance)
            success, cost = best_edge.traverse(current_energy)
            
            if not success:
                return False, total_cost
            
            total_cost += cost
            current_energy -= cost
        
        return True, total_cost
    
    def tick(self, dt: float = 1.0) -> None:
        """Advance global time."""
        self._time += dt
        
        # Update all worlds
        for world in self._worlds.values():
            world.tick(dt)
        
        # Update global entropy
        self._global_entropy = sum(w.entropy for w in self._worlds.values()) / 9
    
    def get_connectivity(self) -> float:
        """
        Calculate graph connectivity.
        
        Used for Ragnarök threshold detection.
        """
        active_edges = sum(1 for e in self._edges if e._active)
        total_edges = len(self._edges)
        
        return active_edges / total_edges if total_edges > 0 else 0.0
    
    def compute_adjacency_matrix(self) -> np.ndarray:
        """Compute weighted adjacency matrix."""
        adj = np.zeros((9, 9))
        
        for edge in self._edges:
            if edge._active:
                weight = edge.transmission_rate
                adj[edge.source, edge.target] = weight
                if edge.bidirectional:
                    adj[edge.target, edge.source] = weight
        
        return adj
    
    def compute_laplacian(self) -> np.ndarray:
        """Compute graph Laplacian."""
        adj = self.compute_adjacency_matrix()
        degree = np.diag(np.sum(adj, axis=1))
        return degree - adj
    
    def spectral_gap(self) -> float:
        """
        Compute spectral gap (connectivity measure).
        
        Lower gap indicates approaching disconnection.
        """
        L = self.compute_laplacian()
        eigenvalues = np.sort(np.linalg.eigvalsh(L))
        
        # Second smallest eigenvalue
        return float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    
    @property
    def worlds(self) -> Dict[int, World]:
        return self._worlds
    
    @property
    def edges(self) -> List[Edge]:
        return self._edges
    
    @property
    def global_entropy(self) -> float:
        return self._global_entropy
    
    @property
    def time(self) -> float:
        return self._time


# =============================================================================
# GINNUNGAGAP (THE VOID)
# =============================================================================

class Ginnungagap:
    """
    Ginnungagap: The Primordial Void.
    
    The pre-creation state between Niflheim (Ice) and 
    Muspelheim (Fire). Acts as the reset state for Ragnarök.
    """
    
    def __init__(self):
        self._active = False
        self._stored_state: Optional[Dict] = None
    
    def activate(self) -> None:
        """Activate the void (begin reset)."""
        self._active = True
    
    def store_seed(self, state: Dict) -> None:
        """Store seed for rebirth."""
        self._stored_state = state.copy()
    
    def spawn_new_world(self) -> Optional[Yggdrasil]:
        """
        Spawn a new Yggdrasil from the void.
        
        Preserves kernel parameters, purges runtime data.
        """
        if not self._active:
            return None
        
        # Create fresh graph
        new_ygg = Yggdrasil()
        
        # Apply seed state if available
        if self._stored_state:
            # Restore only kernel parameters
            pass  # Placeholder for state restoration
        
        self._active = False
        return new_ygg
    
    @property
    def is_active(self) -> bool:
        return self._active


# =============================================================================
# VALIDATION
# =============================================================================

def validate_topology() -> bool:
    """Validate Norse topology module."""
    
    # Test World creation
    worlds = create_nine_worlds()
    assert len(worlds) == 9
    
    asgard = worlds[0]
    assert asgard.name == "Asgard"
    assert asgard.tier == WorldTier.UPPER
    assert asgard.function == WorldFunction.CONTROL
    
    midgard = worlds[3]
    assert midgard.name == "Midgard"
    assert midgard.tier == WorldTier.MIDDLE
    
    hel = worlds[8]
    assert hel.name == "Hel"
    assert hel.function == WorldFunction.ARCHIVE
    
    # Test Edge creation
    edges = create_world_edges()
    assert len(edges) >= 10
    
    bifrost = next(e for e in edges if e.name == "Bifröst")
    assert bifrost.source == 0  # Asgard
    assert bifrost.target == 3  # Midgard
    assert "god" in bifrost.authorized_types
    
    # Test Yggdrasil graph
    ygg = Yggdrasil()
    
    assert len(ygg.worlds) == 9
    assert len(ygg.edges) >= 10
    
    # Test world lookup
    asgard = ygg.get_world(0)
    assert asgard.name == "Asgard"
    
    midgard = ygg.get_world_by_name("Midgard")
    assert midgard.index == 3
    
    # Test path finding
    # Mortal cannot use Bifröst
    path_mortal = ygg.find_path(3, 0, entity_energy=1.0, entity_type="mortal")
    # May find alternate path or None
    
    # God can use Bifröst
    path_god = ygg.find_path(3, 0, entity_energy=1.0, entity_type="god")
    assert path_god is not None
    assert path_god[0] == 3
    assert path_god[-1] == 0
    
    # Test traversal
    success, cost = ygg.traverse(3, 0, entity_energy=1.0, entity_type="god")
    assert success
    assert cost > 0
    
    # Test connectivity
    conn = ygg.get_connectivity()
    assert conn == 1.0  # All edges active
    
    # Test adjacency matrix
    adj = ygg.compute_adjacency_matrix()
    assert adj.shape == (9, 9)
    
    # Test spectral gap
    gap = ygg.spectral_gap()
    assert gap > 0  # Connected graph
    
    # Test time tick
    ygg.tick(1.0)
    assert ygg.time == 1.0
    
    # Test Ginnungagap
    void = Ginnungagap()
    assert not void.is_active
    
    void.activate()
    assert void.is_active
    
    new_ygg = void.spawn_new_world()
    assert new_ygg is not None
    assert not void.is_active
    
    return True


if __name__ == "__main__":
    print("Validating Norse Topology Module...")
    assert validate_topology()
    print("✓ Norse Topology Module validated")

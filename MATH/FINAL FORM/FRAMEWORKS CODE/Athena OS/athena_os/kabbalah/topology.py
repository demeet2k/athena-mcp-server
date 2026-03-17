"""
ATHENA OS - KABBALAH: TOPOLOGY MODULE
======================================
The Tree of Life as Directed Acyclic Graph

THE TREE GRAPH G_Etz = (V, E):
    V = 10 (Nodes/Sefirot)
    E = 22 (Edges/Paths)

The Universe is not a singular object; it is a
HIERARCHICAL INSTANTIATION TREE.

THE THREE PILLARS:
    Right Pillar (Mercy): Chokmah → Chesed → Netzach
    Left Pillar (Severity): Binah → Gevurah → Hod
    Middle Pillar (Balance): Keter → Tiferet → Yesod → Malkhut

THE FOUR WORLDS (Abstraction Layers):
    Atziluth (Emanation): Pointer Level - Pure references
    Briah (Creation): Class Level - Abstract definitions
    Yetzirah (Formation): Object Level - Instantiated variables
    Assiah (Action): Hardware Level - Physical manipulation

TRAVERSAL ALGORITHMS:
    Lightning Flash: Descent of Power (1 → 2 → ... → 10)
    Serpent of Wisdom: Ascent of Consciousness (10 → ... → 1)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
from collections import deque


# =============================================================================
# FOUR WORLDS (ABSTRACTION LAYERS)
# =============================================================================

class World(Enum):
    """
    The Four Worlds (Olamot).
    
    Decreasing in fidelity, increasing in density.
    """
    
    ATZILUTH = "atziluth"   # Emanation (Fire) - Pointer Level
    BRIAH = "briah"         # Creation (Water) - Class Level
    YETZIRAH = "yetzirah"   # Formation (Air) - Object Level
    ASSIAH = "assiah"       # Action (Earth) - Hardware Level
    
    @property
    def element(self) -> str:
        elements = {
            World.ATZILUTH: "Fire",
            World.BRIAH: "Water",
            World.YETZIRAH: "Air",
            World.ASSIAH: "Earth"
        }
        return elements[self]
    
    @property
    def abstraction_level(self) -> int:
        """Higher = more abstract."""
        levels = {
            World.ATZILUTH: 4,
            World.BRIAH: 3,
            World.YETZIRAH: 2,
            World.ASSIAH: 1
        }
        return levels[self]


class Pillar(Enum):
    """The Three Pillars of the Tree."""
    
    MERCY = "mercy"       # Right pillar (expansion)
    SEVERITY = "severity" # Left pillar (contraction)
    BALANCE = "balance"   # Middle pillar (integration)


# =============================================================================
# SEFIRA NODE
# =============================================================================

@dataclass
class Sefira:
    """
    A single Sefira (node) in the Tree of Life.
    
    Each Sefira is an Abstract Base Class / Processing Filter
    in the cascading execution stack.
    """
    
    index: int                    # 1-10
    name: str                     # Hebrew name
    english: str                  # English translation
    divine_name: str              # Name of God associated
    world: World                  # Primary world
    pillar: Pillar               # Pillar position
    
    # Computational role
    function: str = ""           # Computational function
    operator: str = ""           # Primary operator type
    
    # State
    _energy: float = 0.0
    _data: Optional[Any] = None
    
    def __post_init__(self):
        # Set default energy based on position
        self._energy = 1.0 / self.index
    
    def receive(self, data: Any, energy: float = 1.0) -> None:
        """Receive data and energy from upstream."""
        self._data = data
        self._energy += energy
    
    def process(self) -> Tuple[Any, float]:
        """Process data according to Sefira's function."""
        # Default: pass through with decay
        output_energy = self._energy * 0.9
        self._energy = 0.0
        return self._data, output_energy
    
    def transmit(self) -> Tuple[Any, float]:
        """Transmit processed data downstream."""
        return self.process()
    
    @property
    def energy(self) -> float:
        return self._energy
    
    @property
    def data(self) -> Any:
        return self._data


# =============================================================================
# THE TEN SEFIROT
# =============================================================================

def create_sefirot() -> Dict[int, Sefira]:
    """
    Create the canonical 10 Sefirot.
    
    These are the Abstract Base Classes of the universal
    execution pipeline.
    """
    return {
        1: Sefira(
            index=1,
            name="Keter",
            english="Crown",
            divine_name="Ehyeh",
            world=World.ATZILUTH,
            pillar=Pillar.BALANCE,
            function="Kernel/Bootloader",
            operator="Initialize"
        ),
        2: Sefira(
            index=2,
            name="Chokmah",
            english="Wisdom",
            divine_name="Yah",
            world=World.ATZILUTH,
            pillar=Pillar.MERCY,
            function="Raw Data Stream",
            operator="Input"
        ),
        3: Sefira(
            index=3,
            name="Binah",
            english="Understanding",
            divine_name="YHVH Elohim",
            world=World.BRIAH,
            pillar=Pillar.SEVERITY,
            function="Parser/Logic Engine",
            operator="Parse"
        ),
        4: Sefira(
            index=4,
            name="Chesed",
            english="Mercy",
            divine_name="El",
            world=World.YETZIRAH,
            pillar=Pillar.MERCY,
            function="Expansion Operator",
            operator="Expand (+)"
        ),
        5: Sefira(
            index=5,
            name="Gevurah",
            english="Severity",
            divine_name="Elohim",
            world=World.YETZIRAH,
            pillar=Pillar.SEVERITY,
            function="Constraint Operator",
            operator="Contract (-)"
        ),
        6: Sefira(
            index=6,
            name="Tiferet",
            english="Beauty",
            divine_name="YHVH",
            world=World.YETZIRAH,
            pillar=Pillar.BALANCE,
            function="Integration Controller",
            operator="Integrate"
        ),
        7: Sefira(
            index=7,
            name="Netzach",
            english="Victory",
            divine_name="YHVH Tzvaot",
            world=World.YETZIRAH,
            pillar=Pillar.MERCY,
            function="Iteration Engine",
            operator="Iterate (for)"
        ),
        8: Sefira(
            index=8,
            name="Hod",
            english="Glory",
            divine_name="Elohim Tzvaot",
            world=World.YETZIRAH,
            pillar=Pillar.SEVERITY,
            function="Validation Framework",
            operator="Validate"
        ),
        9: Sefira(
            index=9,
            name="Yesod",
            english="Foundation",
            divine_name="El Chai",
            world=World.YETZIRAH,
            pillar=Pillar.BALANCE,
            function="I/O Buffer/Compiler",
            operator="Compile"
        ),
        10: Sefira(
            index=10,
            name="Malkhut",
            english="Kingdom",
            divine_name="Adonai",
            world=World.ASSIAH,
            pillar=Pillar.BALANCE,
            function="Runtime Instance/Output",
            operator="Execute"
        )
    }


# =============================================================================
# PATH (EDGE)
# =============================================================================

@dataclass
class Path:
    """
    A Path (edge) connecting two Sefirot.
    
    Paths are Transformational Functions, not passive wires.
    Each of the 22 paths corresponds to a Hebrew letter.
    """
    
    index: int                   # 11-32 (traditional numbering)
    source: int                  # Source Sefira index
    target: int                  # Target Sefira index
    letter: str                  # Hebrew letter
    letter_name: str             # Letter name
    value: int                   # Numerical value
    
    # Tarot correspondence (optional)
    tarot: str = ""
    
    def traverse(self, data: Any, energy: float) -> Tuple[Any, float]:
        """
        Traverse the path, transforming data.
        
        Applying a path applies a specific operator.
        """
        # Transform based on letter value
        # Energy decays slightly along path
        return data, energy * 0.95
    
    def __repr__(self) -> str:
        return f"Path({self.letter}: {self.source}→{self.target})"


def create_paths() -> List[Path]:
    """
    Create the canonical 22 Paths.
    
    These are the Instruction Set Architecture (ISA).
    """
    paths = [
        # Horizontal paths (3)
        Path(11, 1, 2, "א", "Aleph", 1, "Fool"),
        Path(14, 2, 3, "ד", "Dalet", 4, "Empress"),
        Path(19, 4, 5, "ט", "Tet", 9, "Strength"),
        Path(22, 6, 7, "ל", "Lamed", 30, "Justice"),  # Actually 7-8
        Path(27, 7, 8, "פ", "Pe", 80, "Tower"),
        Path(28, 7, 9, "צ", "Tzadi", 90, "Star"),  # 8-9 in some
        Path(31, 8, 10, "ש", "Shin", 300, "Judgment"),  # 9-10 some
        
        # Vertical paths on right pillar
        Path(15, 2, 4, "ה", "He", 5, "Emperor"),
        Path(20, 4, 6, "י", "Yod", 10, "Hermit"),
        Path(24, 4, 7, "נ", "Nun", 50, "Death"),
        
        # Vertical paths on left pillar
        Path(18, 3, 5, "ח", "Chet", 8, "Chariot"),
        Path(23, 5, 6, "מ", "Mem", 40, "Hanged Man"),
        Path(26, 5, 8, "ע", "Ayin", 70, "Devil"),
        
        # Vertical paths on middle pillar
        Path(13, 1, 6, "ג", "Gimel", 3, "High Priestess"),
        Path(25, 6, 9, "ס", "Samekh", 60, "Temperance"),
        Path(32, 9, 10, "ת", "Tav", 400, "World"),
        
        # Diagonal paths
        Path(12, 1, 3, "ב", "Bet", 2, "Magician"),
        Path(16, 2, 6, "ו", "Vav", 6, "Hierophant"),
        Path(17, 3, 6, "ז", "Zayin", 7, "Lovers"),
        Path(21, 4, 6, "כ", "Kaf", 20, "Wheel"),  # Chesed-Gevurah alt
        Path(29, 7, 10, "ק", "Qof", 100, "Moon"),
        Path(30, 8, 9, "ר", "Resh", 200, "Sun"),
    ]
    
    return paths


# =============================================================================
# TREE OF LIFE GRAPH
# =============================================================================

class TreeOfLife:
    """
    The Complete Tree of Life Graph.
    
    G_Etz = (V, E) where V=10, E=22
    
    The hierarchical instantiation tree governing the
    descent from Infinite Potential to Physical Reality.
    """
    
    def __init__(self):
        # Build nodes
        self._sefirot = create_sefirot()
        
        # Build edges
        self._paths = create_paths()
        
        # Build adjacency
        self._adjacency: Dict[int, List[int]] = {i: [] for i in range(1, 11)}
        self._path_map: Dict[Tuple[int, int], Path] = {}
        
        for path in self._paths:
            self._adjacency[path.source].append(path.target)
            self._adjacency[path.target].append(path.source)  # Bidirectional
            self._path_map[(path.source, path.target)] = path
            self._path_map[(path.target, path.source)] = path
    
    def get_sefira(self, index: int) -> Optional[Sefira]:
        """Get Sefira by index (1-10)."""
        return self._sefirot.get(index)
    
    def get_path(self, source: int, target: int) -> Optional[Path]:
        """Get path between two Sefirot."""
        return self._path_map.get((source, target))
    
    def get_neighbors(self, index: int) -> List[int]:
        """Get indices of neighboring Sefirot."""
        return self._adjacency.get(index, [])
    
    def lightning_flash(self) -> List[int]:
        """
        The Lightning Flash sequence.
        
        Descent of Power from Keter to Malkhut.
        The zig-zag path of creation.
        """
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    def serpent_ascent(self) -> List[int]:
        """
        The Serpent of Wisdom sequence.
        
        Ascent of Consciousness from Malkhut to Keter.
        """
        return [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    
    def shortest_path(self, start: int, end: int) -> List[int]:
        """Find shortest path between two Sefirot using BFS."""
        if start == end:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            node, path = queue.popleft()
            
            for neighbor in self._adjacency[node]:
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def execute_descent(self, intent: Any) -> Tuple[Any, Dict]:
        """
        Execute the Lightning Flash descent.
        
        Pass intent through all 10 Sefirot.
        """
        log = {"stages": [], "energy_trace": []}
        data = intent
        energy = 1.0
        
        for idx in self.lightning_flash():
            sefira = self._sefirot[idx]
            
            # Inject data
            sefira.receive(data, energy)
            
            # Process
            data, energy = sefira.transmit()
            
            # Log
            log["stages"].append({
                "sefira": sefira.name,
                "function": sefira.function,
                "energy": energy
            })
            log["energy_trace"].append(energy)
        
        return data, log
    
    def execute_ascent(self, state: Any) -> Tuple[Any, Dict]:
        """
        Execute the Serpent Ascent.
        
        Raise state from Malkhut back to Keter.
        """
        log = {"stages": [], "energy_trace": []}
        data = state
        energy = 0.1  # Start with minimal energy
        
        for idx in self.serpent_ascent():
            sefira = self._sefirot[idx]
            
            sefira.receive(data, energy)
            data, energy = sefira.transmit()
            
            # Energy increases during ascent
            energy *= 1.05
            
            log["stages"].append({
                "sefira": sefira.name,
                "function": sefira.function,
                "energy": energy
            })
            log["energy_trace"].append(energy)
        
        return data, log
    
    def get_pillar_sefirot(self, pillar: Pillar) -> List[Sefira]:
        """Get all Sefirot on a pillar."""
        return [s for s in self._sefirot.values() if s.pillar == pillar]
    
    def get_world_sefirot(self, world: World) -> List[Sefira]:
        """Get all Sefirot in a world."""
        return [s for s in self._sefirot.values() if s.world == world]
    
    @property
    def sefirot(self) -> Dict[int, Sefira]:
        return self._sefirot
    
    @property
    def paths(self) -> List[Path]:
        return self._paths
    
    @property
    def n_nodes(self) -> int:
        return len(self._sefirot)
    
    @property
    def n_edges(self) -> int:
        return len(self._paths)


# =============================================================================
# ADJACENCY MATRIX REPRESENTATION
# =============================================================================

class TreeMatrix:
    """
    Matrix representation of the Tree of Life.
    
    Enables linear algebra operations on the tree.
    """
    
    def __init__(self, tree: TreeOfLife):
        self.tree = tree
        self._build_matrices()
    
    def _build_matrices(self) -> None:
        """Build adjacency and weight matrices."""
        n = 10
        
        # Adjacency matrix
        self.adjacency = np.zeros((n, n), dtype=np.int8)
        
        # Weight matrix (letter values)
        self.weights = np.zeros((n, n), dtype=np.float64)
        
        for path in self.tree.paths:
            i, j = path.source - 1, path.target - 1
            self.adjacency[i, j] = 1
            self.adjacency[j, i] = 1
            self.weights[i, j] = path.value
            self.weights[j, i] = path.value
    
    def degree_matrix(self) -> np.ndarray:
        """Compute degree matrix."""
        return np.diag(np.sum(self.adjacency, axis=1))
    
    def laplacian(self) -> np.ndarray:
        """Compute graph Laplacian L = D - A."""
        return self.degree_matrix() - self.adjacency
    
    def spectral_gap(self) -> float:
        """Compute spectral gap (second smallest eigenvalue of L)."""
        L = self.laplacian()
        eigenvalues = np.sort(np.linalg.eigvalsh(L))
        return float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    
    def propagate(self, initial: np.ndarray, steps: int = 1) -> np.ndarray:
        """
        Propagate state through graph.
        
        Uses normalized adjacency for diffusion.
        """
        D_inv_sqrt = np.diag(1.0 / np.sqrt(np.sum(self.adjacency, axis=1) + 1e-10))
        P = D_inv_sqrt @ self.adjacency @ D_inv_sqrt
        
        state = initial.copy()
        for _ in range(steps):
            state = P @ state
        
        return state


# =============================================================================
# VALIDATION
# =============================================================================

def validate_topology() -> bool:
    """Validate Kabbalah topology module."""
    
    # Test World enum
    assert World.ATZILUTH.abstraction_level == 4
    assert World.ASSIAH.element == "Earth"
    
    # Test Sefira creation
    sefirot = create_sefirot()
    assert len(sefirot) == 10
    
    keter = sefirot[1]
    assert keter.name == "Keter"
    assert keter.world == World.ATZILUTH
    assert keter.pillar == Pillar.BALANCE
    
    malkhut = sefirot[10]
    assert malkhut.name == "Malkhut"
    assert malkhut.world == World.ASSIAH
    
    # Test Path creation
    paths = create_paths()
    assert len(paths) == 22
    
    # Test Tree of Life
    tree = TreeOfLife()
    assert tree.n_nodes == 10
    assert tree.n_edges == 22
    
    # Test Lightning Flash
    flash = tree.lightning_flash()
    assert flash == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Test Serpent Ascent
    serpent = tree.serpent_ascent()
    assert serpent == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    
    # Test neighbors
    keter_neighbors = tree.get_neighbors(1)
    assert len(keter_neighbors) > 0
    
    # Test shortest path
    path = tree.shortest_path(1, 10)
    assert path[0] == 1
    assert path[-1] == 10
    
    # Test descent
    result, log = tree.execute_descent("Test Intent")
    assert len(log["stages"]) == 10
    assert log["stages"][0]["sefira"] == "Keter"
    assert log["stages"][-1]["sefira"] == "Malkhut"
    
    # Test pillar extraction
    mercy_sefirot = tree.get_pillar_sefirot(Pillar.MERCY)
    assert len(mercy_sefirot) == 3  # Chokmah, Chesed, Netzach
    
    # Test world extraction
    yetzirah_sefirot = tree.get_world_sefirot(World.YETZIRAH)
    assert len(yetzirah_sefirot) >= 5
    
    # Test matrix representation
    matrix = TreeMatrix(tree)
    
    assert matrix.adjacency.shape == (10, 10)
    assert np.sum(matrix.adjacency) > 0  # Has edges
    
    L = matrix.laplacian()
    assert L.shape == (10, 10)
    
    gap = matrix.spectral_gap()
    assert gap > 0  # Connected graph
    
    # Test propagation
    initial = np.zeros(10)
    initial[0] = 1.0  # Start at Keter
    
    final = matrix.propagate(initial, steps=5)
    assert np.sum(final) > 0
    
    return True


if __name__ == "__main__":
    print("Validating Kabbalah Topology Module...")
    assert validate_topology()
    print("✓ Kabbalah Topology Module validated")

"""
ATHENA OS - COPPER SCROLL COMPUTATIONAL FRAMEWORK
==================================================
Part II: The Geodetic System (Spatial Encoding)

THE 3D COORDINATE SPACE:
    The Copper Scroll operates in a volumetric 3D space (x, y, z).
    Every cache location is accompanied by:
    - Topographic Vector: Horizontal position (x, y)
    - Depth Coordinate (Z): Vertical excavation depth in cubits

THE THREE-CUBIT STANDARD:
    Z = 3 cubits (~1.35-1.5 meters) is the most frequent depth
    This represents the "Human Scale Limit" - deep enough for
    concealment, shallow enough for manual excavation.

THE SECTOR SEGMENTATION:
    The 64 nodes are grouped into four geodetic sectors:
    - Sector I: Temple/Jerusalem (Source)
    - Sector II: Wilderness/Kohlit (Primary Distribution)
    - Sector III: Qumran/Secacah (Hydraulic Terminal)
    - Sector IV: Termination/The Duplicate Copy

SOURCES:
    Copper Scroll: The Metallurgical Ledger (3Q15)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np


# =============================================================================
# GEOGRAPHIC CONSTANTS
# =============================================================================

class GeoSector(Enum):
    """The four geodetic sectors of the Copper Scroll."""
    
    TEMPLE = (1, "Jerusalem/Temple", (31.7781, 35.2354), "Source Node")
    WILDERNESS = (2, "Kohlit/Wilderness", (31.7500, 35.4000), "Distribution Zone")
    QUMRAN = (3, "Secacah/Qumran", (31.7414, 35.4594), "Hydraulic Terminal")
    TERMINATION = (4, "The Shith/Duplicate", (31.7781, 35.2354), "Final Node")
    
    def __init__(self, sector_id: int, name: str, 
                 coords: Tuple[float, float], function: str):
        self.sector_id = sector_id
        self._name = name
        self.lat, self.lon = coords
        self.function = function


class ContainerClass(Enum):
    """Classification of hiding containers."""
    
    HYDRAULIC = ("H_net", "Cisterns, Reservoirs, Aqueducts")
    GEOLOGIC = ("G_cav", "Caves, Crags")
    NECROPOLIS = ("N_dead", "Tombs, Monuments")
    ARCHITECTURAL = ("A_arch", "Peristyles, Courtyards, Foundations")
    
    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description


# =============================================================================
# THE CACHE NODE
# =============================================================================

@dataclass
class CacheNode:
    """
    A single cache node in the 64-node linked list.
    
    Each node represents a discrete treasure location with
    full geodetic coordinates and payload specification.
    """
    
    # Identity
    node_id: int  # 1-64
    
    # Location vector (descriptive)
    location_description: str
    
    # Coordinates
    depth_cubits: Optional[float] = None  # Z coordinate
    
    # Payload
    payload_talents: float = 0.0
    payload_description: str = ""
    
    # Classification
    container_class: ContainerClass = ContainerClass.HYDRAULIC
    sector: GeoSector = GeoSector.WILDERNESS
    
    # Greek cipher (if present)
    greek_cipher: Optional[str] = None
    
    # Estimated coordinates (modern)
    estimated_lat: Optional[float] = None
    estimated_lon: Optional[float] = None
    
    def depth_meters(self) -> Optional[float]:
        """Convert depth to meters."""
        if self.depth_cubits is None:
            return None
        return self.depth_cubits * 0.45  # 45cm per cubit
    
    def has_greek_cipher(self) -> bool:
        """Check if node has Greek cipher annotation."""
        return self.greek_cipher is not None
    
    def is_accessible(self) -> bool:
        """
        Check if node is within human-scale excavation limits.
        
        3 cubits = ~1.5m is the standard accessible depth.
        """
        if self.depth_cubits is None:
            return True  # Assume accessible if no depth specified
        return self.depth_cubits <= 6  # ~3 meters max
    
    def excavation_difficulty(self) -> str:
        """Estimate excavation difficulty."""
        if self.depth_cubits is None:
            return "UNKNOWN"
        if self.depth_cubits <= 3:
            return "EASY"
        elif self.depth_cubits <= 8:
            return "MODERATE"
        elif self.depth_cubits <= 16:
            return "DIFFICULT"
        else:
            return "EXTREME"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "node_id": self.node_id,
            "location": self.location_description,
            "depth_cubits": self.depth_cubits,
            "depth_meters": self.depth_meters(),
            "payload_talents": self.payload_talents,
            "payload": self.payload_description,
            "container": self.container_class.name,
            "sector": self.sector.name,
            "greek_cipher": self.greek_cipher,
            "excavation_difficulty": self.excavation_difficulty(),
        }


# =============================================================================
# THE 64-NODE INVENTORY
# =============================================================================

# The complete inventory ledger (subset shown, full list in APPENDIX A)
INVENTORY_LEDGER: List[CacheNode] = [
    CacheNode(
        node_id=1,
        location_description="In the ruin in the Valley of Achor, under the steps leading to the East",
        depth_cubits=40,
        payload_talents=17,
        payload_description="A chest of silver",
        container_class=ContainerClass.ARCHITECTURAL,
        sector=GeoSector.WILDERNESS,
        greek_cipher="KEN"
    ),
    CacheNode(
        node_id=2,
        location_description="In the tomb of the diluted wine, in the third excavation",
        depth_cubits=None,
        payload_talents=0,
        payload_description="100 gold ingots",
        container_class=ContainerClass.NECROPOLIS,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=3,
        location_description="In the Great Cistern (Bor ha-Gadol) in the Court of the Peristyle",
        depth_cubits=None,
        payload_talents=900,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.TEMPLE,
    ),
    CacheNode(
        node_id=4,
        location_description="In the trough of the Place of the Basin, tithe vessels (Klei Dema)",
        depth_cubits=None,
        payload_description="Tithe vessels",
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.TEMPLE,
        greek_cipher="HN"
    ),
    CacheNode(
        node_id=5,
        location_description="In the ascent of the 'Cohort', on the left as one enters",
        depth_cubits=3,
        payload_talents=40,
        payload_description="Silver",
        container_class=ContainerClass.ARCHITECTURAL,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=6,
        location_description="In the salt pit which is under the steps",
        depth_cubits=None,
        payload_talents=42,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.WILDERNESS,
        greek_cipher="HN"
    ),
    CacheNode(
        node_id=7,
        location_description="In the cavity of the Old House of Tribute, in the Chain Platform",
        depth_cubits=None,
        payload_talents=0,
        payload_description="65 ingots of gold",
        container_class=ContainerClass.ARCHITECTURAL,
        sector=GeoSector.TEMPLE,
        greek_cipher="OE"
    ),
    CacheNode(
        node_id=11,
        location_description="In the cistern under the wall on the East, in the spur of the rock",
        depth_cubits=8,
        payload_talents=0,
        payload_description="600 pitchers of silver",
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=12,
        location_description="In the pond which is in the East of Kohlit",
        depth_cubits=4,
        payload_talents=22,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=13,
        location_description="In the Court of the Wood-Store, at the south end",
        depth_cubits=16,
        payload_description="Silver and Gold vessels",
        container_class=ContainerClass.ARCHITECTURAL,
        sector=GeoSector.TEMPLE,
    ),
    CacheNode(
        node_id=19,
        location_description="In the Aqueduct (Ammah) entering the reservoir, under the sediment",
        depth_cubits=None,
        payload_talents=42,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.QUMRAN,
    ),
    CacheNode(
        node_id=25,
        location_description="In the Cave of the Column (Me'arat Ha-Amud) of two openings, facing East",
        depth_cubits=3,
        payload_talents=42,
        container_class=ContainerClass.GEOLOGIC,
        sector=GeoSector.WILDERNESS,
        greek_cipher="OE"
    ),
    CacheNode(
        node_id=26,
        location_description="At the entrance of the same cave, under the large stone",
        depth_cubits=None,
        payload_talents=14,
        container_class=ContainerClass.GEOLOGIC,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=27,
        location_description="In the inner chamber of the same cave, facing the cooling chamber",
        depth_cubits=12,
        payload_talents=22,
        container_class=ContainerClass.GEOLOGIC,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=32,
        location_description="In the cave next to the cooler, adjacent to the floor",
        depth_cubits=None,
        payload_talents=80,
        container_class=ContainerClass.GEOLOGIC,
        sector=GeoSector.WILDERNESS,
        greek_cipher="DI"
    ),
    CacheNode(
        node_id=36,
        location_description="In the long subterranean tunnel of the eastward looking cliff",
        depth_cubits=None,
        payload_talents=22,
        container_class=ContainerClass.GEOLOGIC,
        sector=GeoSector.WILDERNESS,
        greek_cipher="CAG"
    ),
    CacheNode(
        node_id=47,
        location_description="In the cistern close to the drain of the Great Basin",
        depth_cubits=None,
        payload_talents=12,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.QUMRAN,
    ),
    CacheNode(
        node_id=48,
        location_description="In the water wheel of the canal",
        depth_cubits=None,
        payload_talents=9,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.QUMRAN,
        greek_cipher="SK"
    ),
    CacheNode(
        node_id=52,
        location_description="At the head of the Aqueduct of Secacah (Qumran), from the North",
        depth_cubits=3,
        payload_talents=7,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.QUMRAN,
    ),
    CacheNode(
        node_id=53,
        location_description="In the open tank/dam which is in Secacah",
        depth_cubits=None,
        payload_talents=80,
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.QUMRAN,
    ),
    CacheNode(
        node_id=60,
        location_description="In the Tomb which is in the River of the Dome",
        depth_cubits=None,
        payload_description="Klei Dema (Tithe Vessels)",
        container_class=ContainerClass.NECROPOLIS,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=61,
        location_description="In the House of the Twin Pools",
        depth_cubits=None,
        payload_description="Consignment of charcoal (incense?)",
        container_class=ContainerClass.HYDRAULIC,
        sector=GeoSector.WILDERNESS,
    ),
    CacheNode(
        node_id=63,
        location_description="In the subterranean passage of 'The King'",
        depth_cubits=None,
        payload_talents=70,
        container_class=ContainerClass.GEOLOGIC,
        sector=GeoSector.TERMINATION,
    ),
    CacheNode(
        node_id=64,
        location_description="In the Pit (Shith) adjoining on the north, in a hole opening northward",
        depth_cubits=None,
        payload_description="The Vestments (Bigdei); A Duplicate Copy (Mishneh) of this writing",
        container_class=ContainerClass.ARCHITECTURAL,
        sector=GeoSector.TERMINATION,
    ),
]


# =============================================================================
# THE LINKED LIST
# =============================================================================

@dataclass
class CacheLinkedList:
    """
    The 64-node serialized linked list.
    
    The sequence n₁ → n₆₄ describes a continuous physical
    trajectory (Traversal Path) through the terrain.
    """
    
    nodes: List[CacheNode] = field(default_factory=lambda: INVENTORY_LEDGER.copy())
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def get_node(self, node_id: int) -> Optional[CacheNode]:
        """Get node by ID."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_sector_nodes(self, sector: GeoSector) -> List[CacheNode]:
        """Get all nodes in a sector."""
        return [n for n in self.nodes if n.sector == sector]
    
    def get_container_nodes(self, container: ContainerClass) -> List[CacheNode]:
        """Get all nodes of a container type."""
        return [n for n in self.nodes if n.container_class == container]
    
    def get_greek_cipher_nodes(self) -> List[CacheNode]:
        """Get all nodes with Greek cipher annotations."""
        return [n for n in self.nodes if n.has_greek_cipher()]
    
    def total_talents(self) -> float:
        """Calculate total talents across all nodes."""
        return sum(n.payload_talents for n in self.nodes)
    
    def mean_depth(self) -> float:
        """Calculate mean depth (cubits) for nodes with depth data."""
        depths = [n.depth_cubits for n in self.nodes if n.depth_cubits is not None]
        if not depths:
            return 0.0
        return np.mean(depths)
    
    def sector_distribution(self) -> Dict[str, int]:
        """Get distribution of nodes by sector."""
        dist = {}
        for sector in GeoSector:
            count = len(self.get_sector_nodes(sector))
            dist[sector.name] = count
        return dist
    
    def container_distribution(self) -> Dict[str, int]:
        """Get distribution of nodes by container type."""
        dist = {}
        for container in ContainerClass:
            count = len(self.get_container_nodes(container))
            dist[container.name] = count
        return dist
    
    def traverse(self) -> List[CacheNode]:
        """Traverse the list in sequence (the recovery path)."""
        return sorted(self.nodes, key=lambda n: n.node_id)
    
    def get_terminal_node(self) -> CacheNode:
        """Get the terminal node (64 - The Duplicate Copy)."""
        return self.get_node(64) or self.nodes[-1]


# =============================================================================
# DEPTH STATISTICS
# =============================================================================

@dataclass
class DepthAnalysis:
    """Analysis of depth (Z) coordinates."""
    
    nodes: List[CacheNode] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.nodes:
            self.nodes = INVENTORY_LEDGER.copy()
    
    def get_depths(self) -> List[float]:
        """Get all specified depths."""
        return [n.depth_cubits for n in self.nodes if n.depth_cubits is not None]
    
    def mean_depth(self) -> float:
        """Mean depth in cubits."""
        depths = self.get_depths()
        return np.mean(depths) if depths else 0.0
    
    def max_depth(self) -> float:
        """Maximum depth in cubits."""
        depths = self.get_depths()
        return max(depths) if depths else 0.0
    
    def min_depth(self) -> float:
        """Minimum depth in cubits."""
        depths = self.get_depths()
        return min(depths) if depths else 0.0
    
    def three_cubit_count(self) -> int:
        """Count of nodes at the standard 3-cubit depth."""
        return sum(1 for n in self.nodes if n.depth_cubits == 3)
    
    def depth_distribution(self) -> Dict[str, int]:
        """Distribution by depth category."""
        categories = {
            "shallow (≤3)": 0,
            "medium (4-8)": 0,
            "deep (9-16)": 0,
            "extreme (>16)": 0,
            "unspecified": 0,
        }
        
        for node in self.nodes:
            if node.depth_cubits is None:
                categories["unspecified"] += 1
            elif node.depth_cubits <= 3:
                categories["shallow (≤3)"] += 1
            elif node.depth_cubits <= 8:
                categories["medium (4-8)"] += 1
            elif node.depth_cubits <= 16:
                categories["deep (9-16)"] += 1
            else:
                categories["extreme (>16)"] += 1
        
        return categories


# =============================================================================
# THE EASTERN VECTOR
# =============================================================================

@dataclass
class ExtractionVector:
    """
    The vector of extraction (Jerusalem → Wilderness).
    
    Assets moved East-Southeast (110°-130°) from Jerusalem
    towards the Judean Desert.
    """
    
    source: Tuple[float, float] = (31.7781, 35.2354)  # Jerusalem/Temple Mount
    sink: Tuple[float, float] = (31.7414, 35.4594)    # Qumran/Secacah
    
    def bearing(self) -> float:
        """Calculate bearing in degrees (from source to sink)."""
        lat1, lon1 = np.radians(self.source)
        lat2, lon2 = np.radians(self.sink)
        
        dlon = lon2 - lon1
        
        x = np.sin(dlon) * np.cos(lat2)
        y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
        
        bearing = np.arctan2(x, y)
        return (np.degrees(bearing) + 360) % 360
    
    def distance_km(self) -> float:
        """Calculate great-circle distance in kilometers."""
        lat1, lon1 = np.radians(self.source)
        lat2, lon2 = np.radians(self.sink)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        # Earth's radius in km
        R = 6371.0
        return R * c
    
    def midpoint(self) -> Tuple[float, float]:
        """Calculate midpoint of extraction vector."""
        lat = (self.source[0] + self.sink[0]) / 2
        lon = (self.source[1] + self.sink[1]) / 2
        return (lat, lon)
    
    def is_eastern(self) -> bool:
        """Verify vector is eastward (bearing 45°-135°)."""
        bearing = self.bearing()
        return 45 <= bearing <= 135


# =============================================================================
# VALIDATION
# =============================================================================

def validate_geodetics() -> bool:
    """Validate the geodetics module."""
    
    # Test CacheNode
    node = CacheNode(
        node_id=1,
        location_description="Test location",
        depth_cubits=3,
        payload_talents=17,
    )
    assert node.depth_meters() == 1.35
    assert node.is_accessible()
    assert node.excavation_difficulty() == "EASY"
    
    # Test CacheLinkedList
    cache_list = CacheLinkedList()
    assert len(cache_list) > 0
    
    node_1 = cache_list.get_node(1)
    assert node_1 is not None
    assert node_1.greek_cipher == "KEN"
    
    cipher_nodes = cache_list.get_greek_cipher_nodes()
    assert len(cipher_nodes) > 0
    
    total = cache_list.total_talents()
    assert total > 0
    
    terminal = cache_list.get_terminal_node()
    assert terminal.node_id == 64
    
    # Test DepthAnalysis
    analysis = DepthAnalysis()
    mean_d = analysis.mean_depth()
    assert mean_d > 0
    
    dist = analysis.depth_distribution()
    assert "shallow (≤3)" in dist
    
    # Test ExtractionVector
    vector = ExtractionVector()
    bearing = vector.bearing()
    assert 90 < bearing < 130  # East-Southeast
    
    distance = vector.distance_km()
    assert 15 < distance < 30  # ~20km from Jerusalem to Qumran
    
    assert vector.is_eastern()
    
    return True


if __name__ == "__main__":
    print("Validating Geodetics Module...")
    assert validate_geodetics()
    print("✓ Geodetics module validated")
    
    # Demo
    print("\n--- Copper Scroll Geodetics Demo ---")
    
    print("\n1. Cache Inventory (Sample):")
    cache_list = CacheLinkedList()
    for node in cache_list.traverse()[:5]:
        print(f"   #{node.node_id}: {node.location_description[:50]}...")
        if node.payload_talents > 0:
            print(f"      Payload: {node.payload_talents} talents")
        if node.greek_cipher:
            print(f"      Greek cipher: {node.greek_cipher}")
    
    print(f"\n2. Total Statistics:")
    print(f"   Total nodes: {len(cache_list)}")
    print(f"   Total talents: {cache_list.total_talents()}")
    print(f"   Mean depth: {cache_list.mean_depth():.1f} cubits")
    
    print("\n3. Sector Distribution:")
    for sector, count in cache_list.sector_distribution().items():
        print(f"   {sector}: {count} nodes")
    
    print("\n4. Container Distribution:")
    for container, count in cache_list.container_distribution().items():
        print(f"   {container}: {count} nodes")
    
    print("\n5. Extraction Vector:")
    vector = ExtractionVector()
    print(f"   Bearing: {vector.bearing():.1f}° (East-Southeast)")
    print(f"   Distance: {vector.distance_km():.1f} km")
    print(f"   Eastern vector: {vector.is_eastern()}")

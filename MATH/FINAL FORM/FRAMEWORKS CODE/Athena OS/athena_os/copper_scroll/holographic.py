"""
ATHENA OS - COPPER SCROLL COMPUTATIONAL FRAMEWORK
==================================================
Part IV: The Holographic Projection (Temple-to-Desert Mapping)

THE TEMPLE PROJECTION HYPOTHESIS:
    The 64 cache locations are NOT random hiding spots but a 
    HOLOGRAPHIC PROJECTION of the Temple blueprint onto the 
    Judean Desert landscape.

THE MAPPING ALGORITHM:
    Temple Zone (Source) → Desert Sector (Target)
    
    The spatial organization of caches mirrors the Temple's
    internal geometry at a massive scale factor (λ ≈ 100:1 to 500:1)

THE METALLURGICAL GRADIENT:
    - Northern Sector (Table of Showbread) → Silver reserves
    - Southern Sector (Menorah) → Gold bullion
    
    Items were buried according to their original RITUAL STATION,
    preserving "spatial sanctity" even in the wilderness.

THE INDESTRUCTIBLE TEMPLE:
    To recover the items is to RITUALLY RECONSTRUCT the Temple
    floor plan on the desert floor. The scroll is the key to
    reassembling the "Shattered Vessels."

SOURCES:
    Copper Scroll: The Metallurgical Ledger (3Q15)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np


# =============================================================================
# TEMPLE ZONES
# =============================================================================

class TempleZone(Enum):
    """
    The zones of the Second Temple.
    
    Each zone had specific ritual function and sacred items.
    """
    
    HOLY_OF_HOLIES = (
        "Kodesh HaKodashim",
        "The Ark, The Presence",
        (0, 0),  # Center
        "GOLD"
    )
    SANCTUARY = (
        "Heichal",
        "Menorah (Gold), Table (Silver)",
        (0, 10),  # East of Holy of Holies
        "MIXED"
    )
    ALTAR = (
        "Mizbeach",
        "Sacrifice, Blood, Libations",
        (0, 20),  # East of Sanctuary
        "BRONZE"
    )
    COURT_OF_PRIESTS = (
        "Ezrat Kohanim",
        "Priestly service area",
        (0, 30),
        "SILVER"
    )
    COURT_OF_ISRAEL = (
        "Ezrat Yisrael",
        "Male Israelites",
        (0, 40),
        "SILVER"
    )
    COURT_OF_WOMEN = (
        "Ezrat Nashim",
        "Public Treasury (Lishkat HaGazit)",
        (0, 50),
        "SILVER"
    )
    OUTER_COURT = (
        "Har HaBayit",
        "Mixed use, profane entry",
        (0, 70),
        "BRONZE"
    )
    
    def __init__(self, hebrew_name: str, function: str,
                 relative_coords: Tuple[float, float], primary_metal: str):
        self.hebrew_name = hebrew_name
        self.function = function
        self.relative_x, self.relative_y = relative_coords
        self.primary_metal = primary_metal


class DesertSector(Enum):
    """
    Desert sectors corresponding to Temple zones.
    """
    
    CAVE_OF_COLUMN = (
        "Me'arat Ha-Amud",
        "Deep Storage, Duplicate Copy",
        TempleZone.HOLY_OF_HOLIES,
        (31.7450, 35.4600)
    )
    CENTRAL_WADI = (
        "Central Wadi System",
        "Mixed Bullion Caches",
        TempleZone.SANCTUARY,
        (31.7500, 35.4400)
    )
    SECACAH = (
        "Qumran/Secacah",
        "Hydraulic features, Altar correspondence",
        TempleZone.ALTAR,
        (31.7414, 35.4594)
    )
    ACHOR_VALLEY = (
        "Valley of Achor/Jericho",
        "High volume silver (public tithes)",
        TempleZone.COURT_OF_WOMEN,
        (31.8500, 35.4500)
    )
    PERIPHERAL_FORTS = (
        "Hyrcania/Dok",
        "Military supplies, mixed vessels",
        TempleZone.OUTER_COURT,
        (31.7200, 35.4000)
    )
    
    def __init__(self, name: str, contents: str,
                 temple_correspondence: TempleZone,
                 coords: Tuple[float, float]):
        self._name = name
        self.contents = contents
        self.temple_zone = temple_correspondence
        self.lat, self.lon = coords


# =============================================================================
# THE TEMPLE BLUEPRINT
# =============================================================================

@dataclass
class TempleBlueprint:
    """
    The architectural blueprint of the Second Temple.
    
    Dimensions from Tractate Middot.
    """
    
    # Overall dimensions (cubits)
    total_length: float = 500.0  # East-West
    total_width: float = 500.0   # North-South
    
    # Holy of Holies
    holy_of_holies_size: float = 20.0  # 20x20 cubits
    
    # Sanctuary
    sanctuary_length: float = 40.0
    sanctuary_width: float = 20.0
    
    # Altar
    altar_size: float = 32.0  # 32x32 cubits
    
    # Court dimensions
    court_of_priests_depth: float = 11.0
    court_of_israel_depth: float = 11.0
    court_of_women_size: float = 135.0  # 135x135 cubits
    
    def get_zone_bounds(self, zone: TempleZone) -> Tuple[float, float, float, float]:
        """Get bounding box (x1, y1, x2, y2) for a zone in cubits."""
        # Simplified zone bounds
        bounds = {
            TempleZone.HOLY_OF_HOLIES: (-10, -10, 10, 10),
            TempleZone.SANCTUARY: (10, -10, 50, 10),
            TempleZone.ALTAR: (50, -16, 82, 16),
            TempleZone.COURT_OF_PRIESTS: (82, -50, 93, 50),
            TempleZone.COURT_OF_ISRAEL: (93, -50, 104, 50),
            TempleZone.COURT_OF_WOMEN: (104, -67, 239, 68),
            TempleZone.OUTER_COURT: (-250, -250, 250, 250),
        }
        return bounds.get(zone, (0, 0, 0, 0))
    
    def total_area_cubits(self) -> float:
        """Total Temple Mount area in square cubits."""
        return self.total_length * self.total_width


# =============================================================================
# THE PROJECTION OPERATOR
# =============================================================================

@dataclass
class HolographicProjection:
    """
    The projection operator mapping Temple to Desert.
    
    P: Temple_Coordinates → Desert_Coordinates
    
    Scale factor λ ≈ 100:1 to 500:1
    """
    
    # Temple reference point (Holy of Holies)
    temple_origin: Tuple[float, float] = (31.7781, 35.2354)  # Temple Mount
    
    # Desert reference point (Qumran)
    desert_origin: Tuple[float, float] = (31.7414, 35.4594)
    
    # Scale factor (cubits in Temple → meters in Desert)
    scale_factor: float = 250.0  # 1 cubit → 250 meters
    
    # Rotation (Temple axis to Desert axis)
    rotation_degrees: float = 110.0  # East-Southeast
    
    def temple_to_desert(self, temple_x: float, temple_y: float) -> Tuple[float, float]:
        """
        Project Temple coordinates to Desert coordinates.
        
        Args:
            temple_x: X coordinate in Temple (cubits)
            temple_y: Y coordinate in Temple (cubits)
            
        Returns:
            (latitude, longitude) in the desert
        """
        # Apply rotation
        theta = np.radians(self.rotation_degrees)
        rotated_x = temple_x * np.cos(theta) - temple_y * np.sin(theta)
        rotated_y = temple_x * np.sin(theta) + temple_y * np.cos(theta)
        
        # Apply scale (cubits → meters)
        meters_x = rotated_x * self.scale_factor * 0.45  # cubit to meters
        meters_y = rotated_y * self.scale_factor * 0.45
        
        # Convert to lat/lon offset (approximate)
        # 1 degree latitude ≈ 111,320 meters
        # 1 degree longitude ≈ 85,000 meters at this latitude
        lat_offset = meters_y / 111320.0
        lon_offset = meters_x / 85000.0
        
        desert_lat = self.temple_origin[0] + lat_offset
        desert_lon = self.temple_origin[1] + lon_offset
        
        return (desert_lat, desert_lon)
    
    def desert_to_temple(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Inverse projection: Desert coordinates to Temple coordinates.
        """
        # Calculate offsets
        lat_offset = lat - self.temple_origin[0]
        lon_offset = lon - self.temple_origin[1]
        
        # Convert to meters
        meters_y = lat_offset * 111320.0
        meters_x = lon_offset * 85000.0
        
        # Reverse scale
        cubits_x = meters_x / (self.scale_factor * 0.45)
        cubits_y = meters_y / (self.scale_factor * 0.45)
        
        # Reverse rotation
        theta = -np.radians(self.rotation_degrees)
        temple_x = cubits_x * np.cos(theta) - cubits_y * np.sin(theta)
        temple_y = cubits_x * np.sin(theta) + cubits_y * np.cos(theta)
        
        return (temple_x, temple_y)
    
    def get_desert_zone(self, temple_zone: TempleZone) -> Optional[DesertSector]:
        """Get the desert sector corresponding to a Temple zone."""
        for sector in DesertSector:
            if sector.temple_zone == temple_zone:
                return sector
        return None


# =============================================================================
# THE METALLURGICAL GRADIENT
# =============================================================================

@dataclass
class MetallurgicalGradient:
    """
    The North-South metallurgical gradient.
    
    Items were buried according to their original ritual station:
    - Northern (Table) → Silver
    - Southern (Menorah) → Gold
    """
    
    def classify_by_position(self, temple_y: float) -> str:
        """
        Classify metal type by Temple y-coordinate.
        
        Positive y = North (Silver)
        Negative y = South (Gold)
        """
        if temple_y > 10:
            return "SILVER"
        elif temple_y < -10:
            return "GOLD"
        else:
            return "MIXED"
    
    def predict_cache_metal(self, lat: float, reference_lat: float = 31.7500) -> str:
        """
        Predict cache metal type from latitude.
        
        Higher latitude (north) = Silver
        Lower latitude (south) = Gold
        """
        if lat > reference_lat + 0.02:
            return "SILVER"
        elif lat < reference_lat - 0.02:
            return "GOLD"
        else:
            return "MIXED"
    
    def verify_gradient(self, caches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify metallurgical gradient hypothesis against cache data.
        """
        north_silver = 0
        north_gold = 0
        south_silver = 0
        south_gold = 0
        
        for cache in caches:
            lat = cache.get("lat", 31.75)
            metal = cache.get("metal", "SILVER")
            
            if lat > 31.77:  # North
                if metal == "SILVER":
                    north_silver += 1
                else:
                    north_gold += 1
            else:  # South
                if metal == "SILVER":
                    south_silver += 1
                else:
                    south_gold += 1
        
        return {
            "north_silver": north_silver,
            "north_gold": north_gold,
            "south_silver": south_silver,
            "south_gold": south_gold,
            "gradient_confirmed": north_silver > north_gold and south_gold > south_silver,
        }


# =============================================================================
# THE ZONE MAPPING TABLE
# =============================================================================

ZONE_MAPPING_TABLE = [
    {
        "temple_zone": "Holy of Holies (Kodesh HaKodashim)",
        "ritual_function": "The Ark; The Presence",
        "desert_sector": "Cave of the Column / Kohlit",
        "scroll_nodes": "25-36",
        "contents": "Deep Storage, Duplicate Copy",
    },
    {
        "temple_zone": "Sanctuary (Heichal)",
        "ritual_function": "Menorah (Gold), Table (Silver)",
        "desert_sector": "Central Wadi System",
        "scroll_nodes": "19-24",
        "contents": "Mixed Bullion Caches",
    },
    {
        "temple_zone": "Altar (Mizbeach)",
        "ritual_function": "Sacrifice; Fluids (Blood/Wine)",
        "desert_sector": "Secacah (Qumran)",
        "scroll_nodes": "48-55",
        "contents": "Hydraulic features matching Altar drainage",
    },
    {
        "temple_zone": "Court of Women (Ezrat Nashim)",
        "ritual_function": "Public Treasury (Lishkat HaGazit)",
        "desert_sector": "Achor Valley / Jericho",
        "scroll_nodes": "1-10",
        "contents": "High volume silver coinage (public tithes)",
    },
    {
        "temple_zone": "Outer Court (Har HaBayit)",
        "ritual_function": "Mixed use; profane entry",
        "desert_sector": "Peripheral Forts (Hyrcania/Dok)",
        "scroll_nodes": "56-63",
        "contents": "Military supplies, mixed vessels",
    },
]


# =============================================================================
# THE SPINE GEOMETRY
# =============================================================================

@dataclass
class SpineGeometry:
    """
    The spine (central axis) of the projection.
    
    The path of the priest from the Holy of Holies to the Eastern Gate
    forms a straight line. In the projection, this maps to the descent
    from the Judean highlands to the Qumran plateau.
    """
    
    # Temple spine (cubits from Holy of Holies)
    temple_spine_length: float = 250.0  # cubits to Eastern Gate
    
    # Desert spine (meters)
    desert_spine_length: float = 20000.0  # ~20 km to Qumran
    
    def spine_scale_factor(self) -> float:
        """Calculate scale factor from spine lengths."""
        temple_meters = self.temple_spine_length * 0.45
        return self.desert_spine_length / temple_meters
    
    def position_on_spine(self, fraction: float) -> Tuple[float, float]:
        """
        Get position along the spine at a given fraction (0-1).
        
        Returns (temple_position_cubits, desert_position_meters)
        """
        temple_pos = fraction * self.temple_spine_length
        desert_pos = fraction * self.desert_spine_length
        return (temple_pos, desert_pos)
    
    def temple_to_spine_fraction(self, temple_x: float) -> float:
        """Convert Temple x-coordinate to spine fraction."""
        return temple_x / self.temple_spine_length


# =============================================================================
# THE SHATTERED VESSELS
# =============================================================================

@dataclass
class ShatteredVessels:
    """
    The metaphor of the "Shattered Vessels" (Shevirat HaKelim).
    
    To recover the items is to ritually reconstruct the Temple
    floor plan on the desert floor.
    """
    
    total_vessels: int = 64  # The 64 cache nodes
    recovered: int = 0
    
    def recovery_progress(self) -> float:
        """Calculate recovery progress (0-1)."""
        return self.recovered / self.total_vessels
    
    def is_temple_reconstructed(self) -> bool:
        """Check if Temple is symbolically reconstructed."""
        return self.recovered == self.total_vessels
    
    def remaining_vessels(self) -> int:
        """Number of vessels remaining to recover."""
        return self.total_vessels - self.recovered
    
    def recover_vessel(self, node_id: int) -> bool:
        """Recover a vessel (cache)."""
        if self.recovered < self.total_vessels:
            self.recovered += 1
            return True
        return False


# =============================================================================
# HOLOGRAPHIC SYSTEM
# =============================================================================

@dataclass
class HolographicSystem:
    """
    Complete holographic projection system.
    """
    
    blueprint: TempleBlueprint = field(default_factory=TempleBlueprint)
    projection: HolographicProjection = field(default_factory=HolographicProjection)
    gradient: MetallurgicalGradient = field(default_factory=MetallurgicalGradient)
    spine: SpineGeometry = field(default_factory=SpineGeometry)
    vessels: ShatteredVessels = field(default_factory=ShatteredVessels)
    
    def project_temple_zone(self, zone: TempleZone) -> Dict[str, Any]:
        """Project a Temple zone to desert coordinates."""
        bounds = self.blueprint.get_zone_bounds(zone)
        center_x = (bounds[0] + bounds[2]) / 2
        center_y = (bounds[1] + bounds[3]) / 2
        
        desert_coords = self.projection.temple_to_desert(center_x, center_y)
        desert_sector = self.projection.get_desert_zone(zone)
        
        return {
            "temple_zone": zone.name,
            "temple_center": (center_x, center_y),
            "desert_coords": desert_coords,
            "desert_sector": desert_sector.name if desert_sector else None,
            "primary_metal": zone.primary_metal,
        }
    
    def get_mapping_table(self) -> List[Dict[str, Any]]:
        """Get the complete zone mapping table."""
        return ZONE_MAPPING_TABLE.copy()
    
    def analyze_projection(self) -> Dict[str, Any]:
        """Comprehensive projection analysis."""
        return {
            "scale_factor": self.projection.scale_factor,
            "rotation_degrees": self.projection.rotation_degrees,
            "spine_scale": self.spine.spine_scale_factor(),
            "temple_area_cubits": self.blueprint.total_area_cubits(),
            "vessels_total": self.vessels.total_vessels,
            "vessels_recovered": self.vessels.recovered,
            "reconstruction_progress": self.vessels.recovery_progress(),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_holographic() -> bool:
    """Validate the holographic module."""
    
    # Test TempleBlueprint
    blueprint = TempleBlueprint()
    area = blueprint.total_area_cubits()
    assert area == 250000  # 500 × 500
    
    bounds = blueprint.get_zone_bounds(TempleZone.HOLY_OF_HOLIES)
    assert bounds == (-10, -10, 10, 10)
    
    # Test HolographicProjection
    projection = HolographicProjection()
    
    # Project origin (should be near Temple origin)
    lat, lon = projection.temple_to_desert(0, 0)
    assert abs(lat - projection.temple_origin[0]) < 0.001
    
    # Test desert sector lookup
    sector = projection.get_desert_zone(TempleZone.ALTAR)
    assert sector == DesertSector.SECACAH
    
    # Test MetallurgicalGradient
    gradient = MetallurgicalGradient()
    assert gradient.classify_by_position(20) == "SILVER"
    assert gradient.classify_by_position(-20) == "GOLD"
    assert gradient.classify_by_position(0) == "MIXED"
    
    # Test SpineGeometry
    spine = SpineGeometry()
    factor = spine.spine_scale_factor()
    assert factor > 100  # Should be large scale factor
    
    # Test ShatteredVessels
    vessels = ShatteredVessels()
    assert vessels.total_vessels == 64
    assert vessels.remaining_vessels() == 64
    
    vessels.recover_vessel(1)
    assert vessels.recovered == 1
    assert not vessels.is_temple_reconstructed()
    
    # Test HolographicSystem
    system = HolographicSystem()
    
    projection_data = system.project_temple_zone(TempleZone.SANCTUARY)
    assert "temple_zone" in projection_data
    assert "desert_coords" in projection_data
    
    analysis = system.analyze_projection()
    assert "scale_factor" in analysis
    assert analysis["vessels_total"] == 64
    
    return True


if __name__ == "__main__":
    print("Validating Holographic Module...")
    assert validate_holographic()
    print("✓ Holographic module validated")
    
    # Demo
    print("\n--- Holographic Projection Demo ---")
    
    system = HolographicSystem()
    
    print("\n1. Zone Mapping Table:")
    for mapping in system.get_mapping_table():
        print(f"   {mapping['temple_zone']} → {mapping['desert_sector']}")
        print(f"      Nodes: {mapping['scroll_nodes']}")
    
    print("\n2. Temple Zone Projections:")
    for zone in [TempleZone.HOLY_OF_HOLIES, TempleZone.ALTAR, TempleZone.COURT_OF_WOMEN]:
        proj = system.project_temple_zone(zone)
        print(f"   {proj['temple_zone']}:")
        print(f"      Temple center: {proj['temple_center']}")
        print(f"      Desert coords: ({proj['desert_coords'][0]:.4f}, {proj['desert_coords'][1]:.4f})")
        print(f"      Primary metal: {proj['primary_metal']}")
    
    print("\n3. Projection Analysis:")
    analysis = system.analyze_projection()
    print(f"   Scale factor: {analysis['scale_factor']}:1")
    print(f"   Rotation: {analysis['rotation_degrees']}° (East-Southeast)")
    print(f"   Temple area: {analysis['temple_area_cubits']:,} sq cubits")

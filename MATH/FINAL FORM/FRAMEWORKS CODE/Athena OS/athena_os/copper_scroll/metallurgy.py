"""
ATHENA OS - COPPER SCROLL COMPUTATIONAL FRAMEWORK
==================================================
Part I: The Metallurgical Substrate (Hardware Layer)

THE MEDIUM IS THE MEMORY:
    The Copper Scroll (3Q15) is not a standard "Dead Sea Scroll" 
    (literary/religious text) but a Hardware-Encoded Inventory Ledger.
    Unlike the parchment scrolls (software), 3Q15 is engraved on 
    copper (hardware), implying durability and immutability.

THE ALLOY SPECIFICATION:
    Cu₉₉Sn₁ - High-purity copper with ~1% tin
    - Optimized for Write Operations (high ductility)
    - Vickers Hardness: HV ≈ 50 (softer than bronze HV ≈ 100-200)
    - 3,000+ characters hammered without material fatigue

THE COLD STORAGE PARADIGM:
    The scroll functions as a Cold Storage Device for the 
    Second Temple Treasury, designed for multi-millennia preservation.

SOURCES:
    Copper Scroll: The Metallurgical Ledger (3Q15)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np


# =============================================================================
# METALLURGICAL CONSTANTS
# =============================================================================

class MetalType(Enum):
    """Types of metals referenced in the scroll."""
    
    COPPER = ("Cu", 29, 8960, 50)      # Symbol, atomic number, density kg/m³, hardness HV
    TIN = ("Sn", 50, 7310, 5)
    BRONZE = ("Cu+Sn", 0, 8800, 150)   # Alloy
    SILVER = ("Ag", 47, 10490, 25)
    GOLD = ("Au", 79, 19320, 30)
    
    def __init__(self, symbol: str, atomic_num: int, density: float, hardness: float):
        self.symbol = symbol
        self.atomic_num = atomic_num
        self.density = density  # kg/m³
        self.hardness = hardness  # Vickers HV


# Ancient weight standards
class WeightUnit(Enum):
    """Ancient weight units used in the scroll."""
    
    TALENT = ("kikkar", 34.0)      # ~34 kg (Babylonian standard)
    MINA = ("maneh", 0.567)        # ~567 grams (1/60 talent)
    SHEKEL = ("sheqel", 0.0114)    # ~11.4 grams (1/50 mina)
    
    def __init__(self, hebrew_name: str, kg_value: float):
        self.hebrew_name = hebrew_name
        self.kg_value = kg_value


# Length standards
class LengthUnit(Enum):
    """Ancient length units used in the scroll."""
    
    CUBIT = ("amah", 0.45)         # ~45 cm (standard cubit)
    SPAN = ("zereth", 0.225)       # ~22.5 cm (half cubit)
    HANDBREADTH = ("tefach", 0.075)  # ~7.5 cm
    FINGERBREADTH = ("etzba", 0.0188)  # ~1.88 cm
    
    def __init__(self, hebrew_name: str, meters: float):
        self.hebrew_name = hebrew_name
        self.meters = meters


# =============================================================================
# THE SUBSTRATE SPECIFICATION
# =============================================================================

@dataclass
class AlloySpecification:
    """
    The metallurgical specification of the Copper Scroll substrate.
    
    Analysis: Cu₉₉Sn₁ - optimized for write operations.
    """
    
    copper_percentage: float = 99.0
    tin_percentage: float = 1.0
    
    # Physical properties
    vickers_hardness: float = 50.0  # HV
    ductility: float = 0.45  # Elongation at break (45%)
    
    # Dimensions
    thickness_mm: float = 1.0
    width_mm: float = 300.0  # Approximate
    total_length_mm: float = 2400.0  # ~2.4 meters
    
    def write_optimization_score(self) -> float:
        """
        Calculate the Write-Optimization Score.
        
        High ductility = better for hammering characters.
        Low hardness = easier stylus work.
        """
        # Score inversely proportional to hardness, proportional to ductility
        return (self.ductility * 100) / self.vickers_hardness
    
    def fatigue_resistance(self, characters: int = 3000) -> float:
        """
        Estimate fatigue resistance for given character count.
        
        Returns probability of successful completion.
        """
        # Base resistance from ductility
        base_resistance = self.ductility
        
        # Degradation per character (simplified model)
        degradation_per_char = 1e-5
        
        total_degradation = characters * degradation_per_char
        return max(0, base_resistance - total_degradation)
    
    @property
    def is_bronze(self) -> bool:
        """Check if alloy qualifies as bronze (>5% tin)."""
        return self.tin_percentage >= 5.0
    
    @property
    def density(self) -> float:
        """Calculate alloy density (kg/m³)."""
        cu_density = MetalType.COPPER.density
        sn_density = MetalType.TIN.density
        return (self.copper_percentage * cu_density + 
                self.tin_percentage * sn_density) / 100.0


# =============================================================================
# THE WRITE OPERATION
# =============================================================================

@dataclass
class WriteOperation:
    """
    The write operation: hammered text (plastic deformation).
    
    Unlike ink (which sits on surface), the text is EMBEDDED
    into the substrate through mechanical displacement.
    """
    
    stylus_material: str = "iron"
    stylus_tip_width_mm: float = 1.0
    
    # Force parameters
    hammer_force_newtons: float = 50.0
    
    # Character statistics
    total_characters: int = 3000
    columns: int = 12
    lines_per_column: int = 13
    
    def displacement_depth(self, substrate: AlloySpecification) -> float:
        """
        Calculate character displacement depth (mm).
        
        Deeper = more durable but higher force required.
        """
        # Simplified: depth inversely proportional to hardness
        base_depth = 0.5  # mm
        hardness_factor = 100 / substrate.vickers_hardness
        return base_depth * hardness_factor
    
    def write_time_estimate(self, chars_per_hour: int = 60) -> float:
        """Estimate total write time in hours."""
        return self.total_characters / chars_per_hour
    
    def data_density(self) -> float:
        """Calculate data density (characters per cm²)."""
        total_area_cm2 = 240 * 30  # Approximate scroll dimensions
        return self.total_characters / total_area_cm2


# =============================================================================
# THE COLD STORAGE DEVICE
# =============================================================================

@dataclass
class ColdStorageDevice:
    """
    The scroll as a Cold Storage Device.
    
    Properties:
        - Non-volatile (data persists without power)
        - High durability (2000+ year lifespan)
        - Write-once (immutable after creation)
        - Read-many (can be accessed repeatedly)
    """
    
    alloy: AlloySpecification = field(default_factory=AlloySpecification)
    write_op: WriteOperation = field(default_factory=WriteOperation)
    
    # Storage classification
    storage_type: str = "WORM"  # Write Once, Read Many
    
    # Temporal properties
    creation_year: int = -68  # ~68 BCE or ~68 CE (disputed)
    discovery_year: int = 1952
    
    def age_years(self, current_year: int = 2026) -> int:
        """Calculate age of the device."""
        if self.creation_year < 0:
            return current_year + abs(self.creation_year)
        return current_year - self.creation_year
    
    def bit_rot_probability(self) -> float:
        """
        Estimate probability of data loss due to corrosion.
        
        Copper has excellent corrosion resistance (green patina protects).
        """
        age = self.age_years()
        
        # Very low bit rot for copper (logarithmic decay)
        return 1.0 - np.exp(-age / 50000)  # ~2% after 2000 years
    
    def data_integrity_score(self) -> float:
        """Overall data integrity score (0-1)."""
        bit_rot = self.bit_rot_probability()
        fatigue = self.alloy.fatigue_resistance(self.write_op.total_characters)
        
        return (1.0 - bit_rot) * fatigue
    
    def recovery_status(self) -> Dict[str, Any]:
        """Get current recovery status."""
        return {
            "device_type": self.storage_type,
            "age_years": self.age_years(),
            "data_integrity": self.data_integrity_score(),
            "bit_rot_probability": self.bit_rot_probability(),
            "total_characters": self.write_op.total_characters,
            "substrate_optimized": self.alloy.write_optimization_score() > 0.5,
        }


# =============================================================================
# THE INVENTORY MASS
# =============================================================================

@dataclass
class InventoryMass:
    """
    The total mass of treasure cataloged in the scroll.
    
    Total: ~4,630 Talents = ~156,420 kg of precious metal
    """
    
    total_talents: int = 4630
    gold_ingots: int = 165
    
    # Distribution (estimated from text)
    silver_percentage: float = 90.0
    gold_percentage: float = 10.0
    
    def total_mass_kg(self) -> float:
        """Calculate total mass in kilograms."""
        return self.total_talents * WeightUnit.TALENT.kg_value
    
    def silver_mass_kg(self) -> float:
        """Calculate silver mass."""
        return self.total_mass_kg() * (self.silver_percentage / 100.0)
    
    def gold_mass_kg(self) -> float:
        """Calculate gold mass."""
        return self.total_mass_kg() * (self.gold_percentage / 100.0)
    
    def spot_value_usd(self, silver_price_per_kg: float = 800.0,
                       gold_price_per_kg: float = 65000.0) -> float:
        """Calculate spot value in USD."""
        silver_value = self.silver_mass_kg() * silver_price_per_kg
        gold_value = self.gold_mass_kg() * gold_price_per_kg
        return silver_value + gold_value
    
    def artifact_value_usd(self, multiplier: float = 500.0) -> float:
        """
        Calculate artifact value (spot × historical multiplier).
        
        Historical artifacts typically 100x-1000x spot value.
        """
        return self.spot_value_usd() * multiplier
    
    def get_valuation_report(self) -> Dict[str, Any]:
        """Generate comprehensive valuation report."""
        return {
            "total_talents": self.total_talents,
            "total_mass_kg": self.total_mass_kg(),
            "silver_mass_kg": self.silver_mass_kg(),
            "gold_mass_kg": self.gold_mass_kg(),
            "gold_ingots": self.gold_ingots,
            "spot_value_usd": self.spot_value_usd(),
            "artifact_value_usd": self.artifact_value_usd(),
            "artifact_value_billions": self.artifact_value_usd() / 1e9,
        }


# =============================================================================
# UNIT CONVERSION
# =============================================================================

@dataclass
class UnitConverter:
    """Convert between ancient and modern units."""
    
    @staticmethod
    def talents_to_kg(talents: float) -> float:
        """Convert talents to kilograms."""
        return talents * WeightUnit.TALENT.kg_value
    
    @staticmethod
    def kg_to_talents(kg: float) -> float:
        """Convert kilograms to talents."""
        return kg / WeightUnit.TALENT.kg_value
    
    @staticmethod
    def cubits_to_meters(cubits: float) -> float:
        """Convert cubits to meters."""
        return cubits * LengthUnit.CUBIT.meters
    
    @staticmethod
    def meters_to_cubits(meters: float) -> float:
        """Convert meters to cubits."""
        return meters / LengthUnit.CUBIT.meters
    
    @staticmethod
    def shekels_to_grams(shekels: float) -> float:
        """Convert shekels to grams."""
        return shekels * WeightUnit.SHEKEL.kg_value * 1000


# =============================================================================
# VALIDATION
# =============================================================================

def validate_metallurgy() -> bool:
    """Validate the metallurgy module."""
    
    # Test AlloySpecification
    alloy = AlloySpecification()
    assert alloy.copper_percentage == 99.0
    assert not alloy.is_bronze  # <5% tin
    assert alloy.write_optimization_score() > 0.5
    
    fatigue = alloy.fatigue_resistance(3000)
    assert fatigue > 0
    
    # Test WriteOperation
    write = WriteOperation()
    assert write.total_characters == 3000
    
    depth = write.displacement_depth(alloy)
    assert depth > 0
    
    density = write.data_density()
    assert density > 0
    
    # Test ColdStorageDevice
    device = ColdStorageDevice()
    assert device.age_years() > 1900
    
    integrity = device.data_integrity_score()
    assert 0 < integrity < 1
    
    status = device.recovery_status()
    assert "device_type" in status
    
    # Test InventoryMass
    inventory = InventoryMass()
    assert inventory.total_mass_kg() > 150000
    
    spot = inventory.spot_value_usd()
    assert spot > 1e9  # >$1 billion
    
    report = inventory.get_valuation_report()
    assert report["artifact_value_billions"] > 100
    
    # Test UnitConverter
    assert UnitConverter.talents_to_kg(1) == 34.0
    assert abs(UnitConverter.cubits_to_meters(3) - 1.35) < 0.01
    
    return True


if __name__ == "__main__":
    print("Validating Metallurgy Module...")
    assert validate_metallurgy()
    print("✓ Metallurgy module validated")
    
    # Demo
    print("\n--- Copper Scroll Metallurgy Demo ---")
    
    print("\n1. Alloy Specification:")
    alloy = AlloySpecification()
    print(f"   Composition: Cu{alloy.copper_percentage}Sn{alloy.tin_percentage}")
    print(f"   Hardness: {alloy.vickers_hardness} HV")
    print(f"   Ductility: {alloy.ductility * 100}%")
    print(f"   Write optimization score: {alloy.write_optimization_score():.2f}")
    
    print("\n2. Cold Storage Device:")
    device = ColdStorageDevice()
    print(f"   Type: {device.storage_type}")
    print(f"   Age: {device.age_years()} years")
    print(f"   Data integrity: {device.data_integrity_score():.4f}")
    
    print("\n3. Inventory Mass:")
    inventory = InventoryMass()
    report = inventory.get_valuation_report()
    print(f"   Total talents: {report['total_talents']}")
    print(f"   Total mass: {report['total_mass_kg']:,.0f} kg")
    print(f"   Silver: {report['silver_mass_kg']:,.0f} kg")
    print(f"   Gold: {report['gold_mass_kg']:,.0f} kg")
    print(f"   Spot value: ${report['spot_value_usd']:,.0f}")
    print(f"   Artifact value: ${report['artifact_value_billions']:.1f} billion")

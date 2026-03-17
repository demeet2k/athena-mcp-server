"""
ATHENA OS - KERNEL: TECHNE DRIVER
=================================
Craft/Skill - Imposing Geometry on Matter

TECHNE DEFINITION:
    The imposition of Euclidean Geometry and Logical Constraints
    upon the stochastic, high-entropy substrate of Nature (Physis).

THE TRANSFORMATION MATRIX:
    A = T_techne × M_raw
    
    Where:
    - M_raw: Raw materials (chaos, entropy)
    - T_techne: Transformation matrix (skill, pattern)
    - A: Artifact (order, function)

THE NEGENTROPIC CONSTRAINT:
    ΔS = S_artifact - S_raw << 0
    
    Techne reverses the local entropy vector, forcing matter
    to align with a pre-conceived Ideal Form (Eidos).

PRIMARY SUBROUTINES:
    1. Weaving Algorithm - 2D Lattice Generation
    2. Shipbuilding Algorithm - 3D Volumetric Displacement
    
    Both are Entropy Reduction Machines:
    Raw Material (Chaos) → Artifact (Order)

THE LOOM OPERATION:
    For weaving, the transformation is a lattice-generating function:
    L(w, f) = Σᵢ Σⱼ W(i) ⊗ F(j) δ(i-j mod 2)
    
    Where W = warp threads, F = weft threads

SOURCES:
    - ATHENA-KERNEL_SELF-OPTIMIZATION.docx Chapter 6.3
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import numpy as np
import math


# =============================================================================
# MATERIAL STATES
# =============================================================================

class MaterialState(Enum):
    """States of material transformation."""
    
    RAW = "raw"             # Unprocessed, high entropy
    PREPARED = "prepared"   # Cleaned, sorted
    FORMING = "forming"     # Being shaped
    ARTIFACT = "artifact"   # Complete, functional
    REFINED = "refined"     # Optimized artifact


class MaterialType(Enum):
    """Types of raw materials."""
    
    FIBER = "fiber"         # Wool, flax, etc.
    TIMBER = "timber"       # Wood
    METAL = "metal"         # Ore, ingots
    CLAY = "clay"           # Ceramic materials
    STONE = "stone"         # Building materials
    ABSTRACT = "abstract"   # Information, patterns


# =============================================================================
# ENTROPY
# =============================================================================

@dataclass
class EntropyMeasure:
    """
    Measures entropy of a material or system.
    
    High entropy = disorder, randomness
    Low entropy = order, structure
    """
    
    value: float = 1.0  # 0 = perfect order, 1 = maximum disorder
    
    # Components of entropy
    positional: float = 0.5    # Spatial disorder
    orientational: float = 0.5  # Alignment disorder
    compositional: float = 0.5  # Material mixing
    
    @classmethod
    def from_components(cls, pos: float, orient: float, 
                       comp: float) -> EntropyMeasure:
        """Create from components."""
        value = (pos + orient + comp) / 3.0
        return cls(value=value, positional=pos, 
                  orientational=orient, compositional=comp)
    
    @property
    def is_ordered(self) -> bool:
        """Check if entropy is low (ordered)."""
        return self.value < 0.3
    
    @property
    def is_chaotic(self) -> bool:
        """Check if entropy is high (disordered)."""
        return self.value > 0.7
    
    def reduce(self, amount: float) -> EntropyMeasure:
        """Reduce entropy (apply order)."""
        factor = max(0, 1.0 - amount)
        return EntropyMeasure(
            value=self.value * factor,
            positional=self.positional * factor,
            orientational=self.orientational * factor,
            compositional=self.compositional * factor
        )


# =============================================================================
# RAW MATERIAL
# =============================================================================

@dataclass
class RawMaterial:
    """
    Raw material before transformation.
    """
    
    material_type: MaterialType
    quantity: float = 1.0
    quality: float = 0.5  # 0-1
    entropy: EntropyMeasure = field(default_factory=EntropyMeasure)
    
    # Properties
    properties: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.properties:
            self._set_default_properties()
    
    def _set_default_properties(self) -> None:
        """Set default properties based on type."""
        defaults = {
            MaterialType.FIBER: {
                "tensile_strength": 0.3,
                "flexibility": 0.9,
                "durability": 0.4
            },
            MaterialType.TIMBER: {
                "tensile_strength": 0.6,
                "flexibility": 0.4,
                "durability": 0.7
            },
            MaterialType.METAL: {
                "tensile_strength": 0.9,
                "flexibility": 0.2,
                "durability": 0.9
            },
            MaterialType.CLAY: {
                "tensile_strength": 0.1,
                "flexibility": 0.8,
                "durability": 0.3
            },
            MaterialType.STONE: {
                "tensile_strength": 0.3,
                "flexibility": 0.0,
                "durability": 0.95
            },
            MaterialType.ABSTRACT: {
                "tensile_strength": 1.0,
                "flexibility": 1.0,
                "durability": 1.0
            }
        }
        self.properties = defaults.get(self.material_type, {})


# =============================================================================
# ARTIFACT
# =============================================================================

@dataclass
class Artifact:
    """
    Transformed material - the product of Techne.
    """
    
    name: str
    artifact_type: str
    
    # Source materials
    materials: List[RawMaterial] = field(default_factory=list)
    
    # Transformation applied
    transformation: str = ""
    
    # Final properties
    entropy: EntropyMeasure = field(default_factory=lambda: EntropyMeasure(0.1))
    functionality: float = 1.0  # How well it performs its purpose
    beauty: float = 0.5         # Aesthetic quality (kalos)
    
    # Geometric properties
    dimensions: Tuple[float, ...] = (1.0, 1.0, 1.0)
    symmetry: float = 0.5       # 0 = asymmetric, 1 = perfect symmetry
    
    @property
    def quality(self) -> float:
        """Overall artifact quality."""
        return (self.functionality + self.beauty + (1 - self.entropy.value)) / 3
    
    @property
    def is_masterwork(self) -> bool:
        """Check if this is exceptional quality."""
        return self.quality > 0.9 and self.entropy.value < 0.1


# =============================================================================
# TRANSFORMATION MATRIX
# =============================================================================

class TransformationMatrix:
    """
    The T_techne matrix that transforms raw material to artifact.
    
    A = T_techne × M_raw
    """
    
    def __init__(self, size: int = 4):
        """Initialize transformation matrix."""
        self.size = size
        self.matrix = np.eye(size)
        
        # Transformation parameters
        self.entropy_reduction = 0.8  # How much entropy is reduced
        self.skill_factor = 1.0       # Craftsman skill
        self.tool_efficiency = 1.0    # Tool quality
    
    def set_rotation(self, angle: float, axis: int = 0) -> None:
        """Set rotation component (reorientation)."""
        c, s = np.cos(angle), np.sin(angle)
        if axis == 0:  # X rotation
            self.matrix[1, 1] = c
            self.matrix[1, 2] = -s
            self.matrix[2, 1] = s
            self.matrix[2, 2] = c
        elif axis == 1:  # Y rotation
            self.matrix[0, 0] = c
            self.matrix[0, 2] = s
            self.matrix[2, 0] = -s
            self.matrix[2, 2] = c
        elif axis == 2:  # Z rotation
            self.matrix[0, 0] = c
            self.matrix[0, 1] = -s
            self.matrix[1, 0] = s
            self.matrix[1, 1] = c
    
    def set_scale(self, sx: float, sy: float, sz: float) -> None:
        """Set scaling component (shaping)."""
        scale = np.diag([sx, sy, sz, 1.0])
        self.matrix = scale @ self.matrix
    
    def apply(self, material: RawMaterial) -> Dict[str, Any]:
        """
        Apply transformation to material.
        
        Returns transformation result.
        """
        # Calculate entropy reduction
        reduction = self.entropy_reduction * self.skill_factor * self.tool_efficiency
        new_entropy = material.entropy.reduce(reduction)
        
        # Calculate work done (energy required)
        delta_entropy = material.entropy.value - new_entropy.value
        work = delta_entropy * material.quantity
        
        return {
            "original_entropy": material.entropy.value,
            "final_entropy": new_entropy.value,
            "entropy_reduction": delta_entropy,
            "work_done": work,
            "transformation_matrix": self.matrix.tolist(),
            "success": new_entropy.is_ordered
        }
    
    @property
    def determinant(self) -> float:
        """Get matrix determinant (volume change)."""
        return float(np.linalg.det(self.matrix))


# =============================================================================
# WEAVING ALGORITHM (2D Lattice Generation)
# =============================================================================

class WeavingAlgorithm:
    """
    2D Lattice generation algorithm.
    
    L(w, f) = Σᵢ Σⱼ W(i) ⊗ F(j) δ(i-j mod 2)
    
    Interlaces warp (vertical) and weft (horizontal) threads
    into a stable 2D fabric structure.
    """
    
    def __init__(self, warp_count: int = 100, weft_count: int = 100):
        """
        Initialize loom.
        
        warp_count: Number of vertical threads
        weft_count: Number of horizontal passes
        """
        self.warp_count = warp_count
        self.weft_count = weft_count
        
        # Pattern (True = warp over weft)
        self.pattern: np.ndarray = np.zeros((weft_count, warp_count), dtype=bool)
        
        # Thread properties
        self.warp_tension: float = 0.5
        self.weft_tension: float = 0.5
    
    def set_plain_weave(self) -> None:
        """Set simple over-under pattern."""
        for i in range(self.weft_count):
            for j in range(self.warp_count):
                self.pattern[i, j] = (i + j) % 2 == 0
    
    def set_twill_weave(self, offset: int = 1) -> None:
        """Set diagonal twill pattern."""
        for i in range(self.weft_count):
            for j in range(self.warp_count):
                self.pattern[i, j] = (i + j) % 4 < 2
    
    def set_satin_weave(self, float_length: int = 4) -> None:
        """Set satin weave with long floats."""
        for i in range(self.weft_count):
            for j in range(self.warp_count):
                self.pattern[i, j] = (i + j * 2) % float_length == 0
    
    def weave(self, warp_material: RawMaterial, 
             weft_material: RawMaterial) -> Artifact:
        """
        Execute weaving operation.
        
        Returns woven fabric artifact.
        """
        # Calculate structural properties
        interlace_count = np.sum(self.pattern != np.roll(self.pattern, 1, axis=0))
        stability = interlace_count / (self.warp_count * self.weft_count)
        
        # Entropy reduction through ordering
        original_entropy = (warp_material.entropy.value + 
                          weft_material.entropy.value) / 2
        
        # Ordered lattice has very low entropy
        final_entropy = EntropyMeasure(
            value=0.1,
            positional=0.05,      # Threads are precisely positioned
            orientational=0.1,    # Aligned but interlaced
            compositional=0.15    # Materials are separated
        )
        
        # Create fabric artifact
        fabric = Artifact(
            name="Woven Fabric",
            artifact_type="textile",
            materials=[warp_material, weft_material],
            transformation="weaving",
            entropy=final_entropy,
            functionality=stability,
            beauty=0.7,
            dimensions=(self.warp_count * 0.01, self.weft_count * 0.01, 0.001),
            symmetry=0.9
        )
        
        return fabric
    
    def get_pattern_view(self) -> str:
        """Get ASCII view of pattern (small sample)."""
        sample = self.pattern[:10, :20]
        lines = []
        for row in sample:
            line = "".join("█" if cell else "░" for cell in row)
            lines.append(line)
        return "\n".join(lines)


# =============================================================================
# SHIPBUILDING ALGORITHM (3D Volumetric Displacement)
# =============================================================================

class ShipbuildingAlgorithm:
    """
    3D Volumetric displacement algorithm.
    
    Constructs a hollow vessel that displaces water,
    converting timber into a functional ship.
    """
    
    def __init__(self):
        # Hull parameters
        self.length: float = 20.0  # meters
        self.beam: float = 5.0     # width
        self.draft: float = 2.0    # depth below waterline
        
        # Construction quality
        self.plank_fitting: float = 0.9   # How well planks fit
        self.caulking_quality: float = 0.8  # Waterproofing
        self.frame_strength: float = 0.85   # Structural integrity
    
    def calculate_displacement(self) -> float:
        """
        Calculate water displacement (buoyancy).
        
        V = ∫∫∫ dV over hull volume
        Simplified to block coefficient × L × B × D
        """
        block_coefficient = 0.5  # Typical for ancient vessels
        return block_coefficient * self.length * self.beam * self.draft
    
    def calculate_stability(self) -> float:
        """
        Calculate stability (resistance to capsizing).
        
        Based on metacentric height.
        """
        # Simplified stability calculation
        beam_draft_ratio = self.beam / self.draft
        return min(1.0, beam_draft_ratio / 3.0)
    
    def build(self, timber: RawMaterial, 
             additional_materials: List[RawMaterial] = None) -> Artifact:
        """
        Execute ship construction.
        
        Returns ship artifact.
        """
        materials = [timber]
        if additional_materials:
            materials.extend(additional_materials)
        
        # Calculate properties
        displacement = self.calculate_displacement()
        stability = self.calculate_stability()
        
        # Seaworthiness combines multiple factors
        seaworthiness = (
            self.plank_fitting * 0.3 +
            self.caulking_quality * 0.3 +
            self.frame_strength * 0.2 +
            stability * 0.2
        )
        
        # Very low entropy for functional vessel
        final_entropy = EntropyMeasure(
            value=0.05,
            positional=0.03,      # Every piece precisely placed
            orientational=0.05,   # Aligned to hull curves
            compositional=0.07    # Materials properly combined
        )
        
        ship = Artifact(
            name="Vessel",
            artifact_type="ship",
            materials=materials,
            transformation="shipbuilding",
            entropy=final_entropy,
            functionality=seaworthiness,
            beauty=0.6,
            dimensions=(self.length, self.beam, self.draft * 2),
            symmetry=0.95  # Ships are highly symmetric
        )
        
        return ship
    
    @property
    def cargo_capacity(self) -> float:
        """Estimate cargo capacity in cubic meters."""
        return self.calculate_displacement() * 0.5  # 50% of displacement


# =============================================================================
# TECHNE DRIVER
# =============================================================================

class TechneDriver:
    """
    The main Techne Driver - algorithms for imposing order on matter.
    
    Coordinates transformation operations to convert chaos into artifacts.
    """
    
    def __init__(self):
        self.transformation = TransformationMatrix()
        self.weaving = WeavingAlgorithm()
        self.shipbuilding = ShipbuildingAlgorithm()
        
        # Statistics
        self.artifacts_created = 0
        self.total_entropy_reduced = 0.0
        self.total_work_done = 0.0
    
    def set_skill_level(self, skill: float) -> None:
        """Set craftsman skill level (0-1)."""
        self.transformation.skill_factor = max(0.1, min(1.0, skill))
    
    def set_tool_quality(self, quality: float) -> None:
        """Set tool quality (0-1)."""
        self.transformation.tool_efficiency = max(0.1, min(1.0, quality))
    
    def transform(self, material: RawMaterial, 
                 operation: str = "generic") -> Artifact:
        """
        Execute a transformation operation.
        
        operation: "weave", "build_ship", or "generic"
        """
        if operation == "weave":
            # Weaving requires fiber
            self.weaving.set_plain_weave()
            artifact = self.weaving.weave(material, material)
            
        elif operation == "build_ship":
            # Shipbuilding requires timber
            artifact = self.shipbuilding.build(material)
            
        else:
            # Generic transformation
            result = self.transformation.apply(material)
            
            artifact = Artifact(
                name=f"Transformed {material.material_type.value}",
                artifact_type="artifact",
                materials=[material],
                transformation=operation,
                entropy=EntropyMeasure(result["final_entropy"]),
                functionality=0.8 * self.transformation.skill_factor,
                beauty=0.5
            )
            
            self.total_work_done += result["work_done"]
        
        # Update statistics
        self.artifacts_created += 1
        self.total_entropy_reduced += material.entropy.value - artifact.entropy.value
        
        return artifact
    
    def calculate_negentropy(self, before: float, after: float) -> float:
        """
        Calculate negentropy (entropy reduction).
        
        ΔS = S_after - S_before (negative for ordering)
        """
        return after - before  # Should be negative
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get driver statistics."""
        return {
            "artifacts_created": self.artifacts_created,
            "total_entropy_reduced": self.total_entropy_reduced,
            "total_work_done": self.total_work_done,
            "skill_level": self.transformation.skill_factor,
            "tool_quality": self.transformation.tool_efficiency,
            "average_entropy_reduction": (
                self.total_entropy_reduced / max(1, self.artifacts_created)
            )
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_techne() -> bool:
    """Validate Techne Driver module."""
    
    # Test EntropyMeasure
    entropy = EntropyMeasure(0.8)
    assert entropy.is_chaotic
    
    reduced = entropy.reduce(0.7)
    assert reduced.value < entropy.value
    
    # Test RawMaterial
    wool = RawMaterial(MaterialType.FIBER, quantity=10.0, quality=0.7)
    assert wool.material_type == MaterialType.FIBER
    assert "flexibility" in wool.properties
    
    timber = RawMaterial(MaterialType.TIMBER, quantity=50.0, quality=0.8)
    assert timber.properties["durability"] > 0.5
    
    # Test TransformationMatrix
    T = TransformationMatrix()
    result = T.apply(wool)
    assert result["final_entropy"] < result["original_entropy"]
    assert result["success"]
    
    # Test WeavingAlgorithm
    weaving = WeavingAlgorithm(50, 50)
    weaving.set_plain_weave()
    
    warp = RawMaterial(MaterialType.FIBER)
    weft = RawMaterial(MaterialType.FIBER)
    fabric = weaving.weave(warp, weft)
    
    assert fabric.artifact_type == "textile"
    assert fabric.entropy.is_ordered
    
    # Test ShipbuildingAlgorithm
    shipbuilding = ShipbuildingAlgorithm()
    displacement = shipbuilding.calculate_displacement()
    assert displacement > 0
    
    ship = shipbuilding.build(timber)
    assert ship.artifact_type == "ship"
    assert ship.entropy.value < 0.1
    
    # Test TechneDriver
    driver = TechneDriver()
    driver.set_skill_level(0.9)
    
    artifact = driver.transform(wool, "weave")
    assert artifact is not None
    assert driver.artifacts_created == 1
    
    stats = driver.get_statistics()
    assert stats["total_entropy_reduced"] > 0
    
    return True


if __name__ == "__main__":
    print("Validating Techne Driver Module...")
    assert validate_techne()
    print("✓ Techne Driver Module validated")
    
    # Demo
    print("\n--- Techne Driver Demo ---")
    
    driver = TechneDriver()
    driver.set_skill_level(0.95)
    driver.set_tool_quality(0.9)
    
    print("\n1. Weaving Operation:")
    wool = RawMaterial(MaterialType.FIBER, quantity=100, quality=0.8)
    print(f"   Raw wool entropy: {wool.entropy.value:.3f}")
    
    fabric = driver.transform(wool, "weave")
    print(f"   Fabric entropy: {fabric.entropy.value:.3f}")
    print(f"   Quality: {fabric.quality:.3f}")
    print(f"   Is masterwork: {fabric.is_masterwork}")
    
    print("\n   Weave Pattern (sample):")
    driver.weaving.set_twill_weave()
    print(driver.weaving.get_pattern_view())
    
    print("\n2. Shipbuilding Operation:")
    timber = RawMaterial(MaterialType.TIMBER, quantity=500, quality=0.85)
    print(f"   Raw timber entropy: {timber.entropy.value:.3f}")
    
    ship = driver.transform(timber, "build_ship")
    print(f"   Ship entropy: {ship.entropy.value:.3f}")
    print(f"   Functionality (seaworthiness): {ship.functionality:.3f}")
    print(f"   Dimensions: {ship.dimensions}")
    
    print(f"\n   Displacement: {driver.shipbuilding.calculate_displacement():.1f} m³")
    print(f"   Cargo capacity: {driver.shipbuilding.cargo_capacity:.1f} m³")
    
    print("\n3. Driver Statistics:")
    stats = driver.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")

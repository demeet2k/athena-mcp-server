"""
ATHENA OS - SQUARING THE CIRCLE: MANDALA
========================================
The 16-fold Mandala Structure

THE MANDALA NUMBER (16):
    12 peripheral positions + 4 axial positions = 16 total
    
    This is the MINIMUM COMPLETE mandala:
    - 12 peripheral: All element-mode combinations (4 × 3)
    - 4 axial: The organizing elemental principles
    
    Any fewer is incomplete; any more is redundant.

STRUCTURAL CORRESPONDENCE:
    Mandala 16:     12 peripheral + 4 axial
    Square 16:      12 mixed + 4 pure archetypes
    
    Pure archetypes = axial (concentrated, intense)
    Mixed archetypes = peripheral (differentiated, distributed)

THE CIRCLED CROSS:
    The fundamental geometric form:
    - Circle: continuous curved boundary
    - Cross: discrete straight axes
    - 4 cardinal points where cross meets circle
    - 4 quadrants between arms

SYMBOLIC UNIVERSALITY:
    This figure appears across cultures:
    - Celtic cross, Solar cross (☉)
    - Medicine wheel, Mandala
    - Rose window, Chi-rho (☧)

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapter 13
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator
from enum import Enum, IntEnum
import numpy as np
import math

from .circle_system import Element, Mode, Archetype, ARCHETYPE_DATA, ARCHETYPE_ORDER
from .square_system import ElementalArchetype, ARCHETYPES_16


# =============================================================================
# MANDALA CONSTANTS
# =============================================================================

PERIPHERAL_COUNT = 12
AXIAL_COUNT = 4
MANDALA_TOTAL = 16

# Verify structure
assert PERIPHERAL_COUNT + AXIAL_COUNT == MANDALA_TOTAL
assert PERIPHERAL_COUNT == len(Element) * len(Mode)


# =============================================================================
# POSITION TYPES
# =============================================================================

class PositionType(Enum):
    """Type of position in the mandala."""
    
    AXIAL = "axial"           # On the cross (4 positions)
    PERIPHERAL = "peripheral" # On the circumference (12 positions)


class CardinalDirection(IntEnum):
    """The four cardinal directions (axial positions)."""
    
    NORTH = 0   # 0°/360°
    EAST = 1    # 90°
    SOUTH = 2   # 180°
    WEST = 3    # 270°


DIRECTION_DEGREES = {
    CardinalDirection.NORTH: 0,
    CardinalDirection.EAST: 90,
    CardinalDirection.SOUTH: 180,
    CardinalDirection.WEST: 270,
}

DIRECTION_ELEMENTS = {
    CardinalDirection.NORTH: Element.FIRE,
    CardinalDirection.EAST: Element.WATER,
    CardinalDirection.SOUTH: Element.AIR,
    CardinalDirection.WEST: Element.EARTH,
}


# =============================================================================
# MANDALA POSITION
# =============================================================================

@dataclass
class MandalaPosition:
    """
    A position in the 16-fold mandala.
    
    Either axial (4 positions) or peripheral (12 positions).
    """
    
    index: int  # 0-15
    position_type: PositionType
    
    # For axial positions
    direction: Optional[CardinalDirection] = None
    
    # For peripheral positions
    archetype: Optional[Archetype] = None
    
    @property
    def is_axial(self) -> bool:
        return self.position_type == PositionType.AXIAL
    
    @property
    def is_peripheral(self) -> bool:
        return self.position_type == PositionType.PERIPHERAL
    
    @property
    def element(self) -> Element:
        """Get associated element."""
        if self.is_axial:
            return DIRECTION_ELEMENTS[self.direction]
        else:
            return ARCHETYPE_DATA[self.archetype].element
    
    @property
    def degree(self) -> float:
        """Get angular position in degrees."""
        if self.is_axial:
            return float(DIRECTION_DEGREES[self.direction])
        else:
            return ARCHETYPE_DATA[self.archetype].center_degree
    
    @property
    def radians(self) -> float:
        """Get angular position in radians."""
        return math.radians(self.degree)
    
    @property
    def cartesian(self) -> Tuple[float, float]:
        """Get (x, y) position on unit circle."""
        rad = self.radians
        return (math.cos(rad), math.sin(rad))
    
    @property
    def name(self) -> str:
        """Get position name."""
        if self.is_axial:
            return f"Axial-{self.direction.name}"
        else:
            return f"Peripheral-{self.archetype.name}"
    
    def distance_to(self, other: MandalaPosition) -> float:
        """Compute angular distance to another position."""
        diff = abs(self.degree - other.degree)
        return min(diff, 360 - diff)
    
    def opposite(self) -> MandalaPosition:
        """Get opposite position (180° away)."""
        if self.is_axial:
            opp_dir = CardinalDirection((self.direction.value + 2) % 4)
            return create_axial_position(opp_dir)
        else:
            # Find archetype 180° away
            opp_idx = (ARCHETYPE_ORDER.index(self.archetype) + 6) % 12
            return create_peripheral_position(ARCHETYPE_ORDER[opp_idx])
    
    def __hash__(self) -> int:
        return hash((self.index, self.position_type))
    
    def __repr__(self) -> str:
        return f"MandalaPosition({self.name})"


def create_axial_position(direction: CardinalDirection) -> MandalaPosition:
    """Create an axial position."""
    return MandalaPosition(
        index=direction.value,
        position_type=PositionType.AXIAL,
        direction=direction
    )


def create_peripheral_position(archetype: Archetype) -> MandalaPosition:
    """Create a peripheral position."""
    arch_idx = ARCHETYPE_ORDER.index(archetype)
    return MandalaPosition(
        index=4 + arch_idx,  # Offset by 4 axial positions
        position_type=PositionType.PERIPHERAL,
        archetype=archetype
    )


# =============================================================================
# CIRCLED CROSS
# =============================================================================

@dataclass
class CircledCross:
    """
    The fundamental circle-cross figure.
    
    A circle with inscribed perpendicular cross:
    - Circle: continuous boundary
    - Cross: 4 radii at 90° intervals
    - 4 cardinal points
    - 4 quadrants
    """
    
    radius: float = 1.0
    center: Tuple[float, float] = (0.0, 0.0)
    
    # Rotation offset (0 = North at top)
    rotation: float = 0.0
    
    @property
    def cardinal_points(self) -> Dict[CardinalDirection, Tuple[float, float]]:
        """Get coordinates of the 4 cardinal points."""
        points = {}
        for direction in CardinalDirection:
            angle = math.radians(DIRECTION_DEGREES[direction] + self.rotation)
            x = self.center[0] + self.radius * math.sin(angle)
            y = self.center[1] + self.radius * math.cos(angle)
            points[direction] = (x, y)
        return points
    
    @property
    def quadrant_centers(self) -> List[Tuple[float, float]]:
        """Get approximate centers of the 4 quadrants."""
        centers = []
        for i in range(4):
            angle = math.radians(45 + 90 * i + self.rotation)
            x = self.center[0] + self.radius * 0.5 * math.sin(angle)
            y = self.center[1] + self.radius * 0.5 * math.cos(angle)
            centers.append((x, y))
        return centers
    
    def point_at_angle(self, degrees: float) -> Tuple[float, float]:
        """Get point on circle at given angle."""
        angle = math.radians(degrees + self.rotation)
        x = self.center[0] + self.radius * math.sin(angle)
        y = self.center[1] + self.radius * math.cos(angle)
        return (x, y)
    
    def get_quadrant(self, degrees: float) -> int:
        """Get quadrant number (0-3) for a degree."""
        normalized = (degrees + self.rotation) % 360
        return int(normalized // 90)
    
    def is_on_axis(self, degrees: float, tolerance: float = 5.0) -> bool:
        """Check if degree is on a cardinal axis."""
        normalized = (degrees + self.rotation) % 90
        return normalized < tolerance or normalized > (90 - tolerance)


# =============================================================================
# MANDALA
# =============================================================================

class Mandala:
    """
    The 16-fold mandala structure.
    
    12 peripheral positions (zodiacal archetypes)
    + 4 axial positions (elemental directions)
    = 16 total positions
    """
    
    def __init__(self):
        self.positions: List[MandalaPosition] = []
        
        # Create 4 axial positions
        for direction in CardinalDirection:
            self.positions.append(create_axial_position(direction))
        
        # Create 12 peripheral positions
        for archetype in ARCHETYPE_ORDER:
            self.positions.append(create_peripheral_position(archetype))
    
    @property
    def axial_positions(self) -> List[MandalaPosition]:
        """Get the 4 axial positions."""
        return [p for p in self.positions if p.is_axial]
    
    @property
    def peripheral_positions(self) -> List[MandalaPosition]:
        """Get the 12 peripheral positions."""
        return [p for p in self.positions if p.is_peripheral]
    
    def get_position(self, index: int) -> MandalaPosition:
        """Get position by index."""
        return self.positions[index % 16]
    
    def get_axial(self, direction: CardinalDirection) -> MandalaPosition:
        """Get axial position by direction."""
        return self.positions[direction.value]
    
    def get_peripheral(self, archetype: Archetype) -> MandalaPosition:
        """Get peripheral position by archetype."""
        idx = 4 + ARCHETYPE_ORDER.index(archetype)
        return self.positions[idx]
    
    def positions_by_element(self, element: Element) -> List[MandalaPosition]:
        """Get all positions of a given element."""
        return [p for p in self.positions if p.element == element]
    
    def iterate_clockwise(self, start_degree: float = 0) -> Iterator[MandalaPosition]:
        """Iterate through positions in clockwise order."""
        # Sort by degree
        sorted_positions = sorted(self.positions, key=lambda p: p.degree)
        
        # Find starting index
        start_idx = 0
        for i, p in enumerate(sorted_positions):
            if p.degree >= start_degree:
                start_idx = i
                break
        
        # Yield in order from start
        for i in range(len(sorted_positions)):
            yield sorted_positions[(start_idx + i) % len(sorted_positions)]
    
    def to_matrix_correspondence(self) -> Dict[MandalaPosition, ElementalArchetype]:
        """
        Map mandala positions to elemental archetypes.
        
        4 axial → 4 pure archetypes (diagonal)
        12 peripheral → 12 mixed archetypes
        """
        mapping = {}
        
        # Axial → Pure (F-F, W-W, A-A, E-E)
        for axial in self.axial_positions:
            elem = axial.element
            pure_arch = ElementalArchetype(elem, elem)
            mapping[axial] = pure_arch
        
        # Peripheral → Mixed (various mappings possible)
        # Here we use a systematic approach based on modes
        mixed_archs = [a for a in ARCHETYPES_16 if a.is_mixed]
        for i, periph in enumerate(self.peripheral_positions):
            mapping[periph] = mixed_archs[i % 12]
        
        return mapping
    
    def summary(self) -> Dict[str, Any]:
        """Get mandala summary."""
        return {
            "total_positions": 16,
            "axial_positions": 4,
            "peripheral_positions": 12,
            "structure": "12 + 4 = 16",
            "correspondence": "12 mixed + 4 pure archetypes"
        }


# =============================================================================
# MANDALA OPERATIONS
# =============================================================================

class MandalaOperations:
    """Operations on mandala positions."""
    
    @staticmethod
    def rotate(position: MandalaPosition, steps: int) -> MandalaPosition:
        """
        Rotate position by steps (each step = 30°).
        """
        if position.is_axial:
            # Rotate among 4 directions (each 90°)
            new_dir = CardinalDirection((position.direction.value + (steps * 3) // 4) % 4)
            return create_axial_position(new_dir)
        else:
            # Rotate among 12 archetypes
            curr_idx = ARCHETYPE_ORDER.index(position.archetype)
            new_idx = (curr_idx + steps) % 12
            return create_peripheral_position(ARCHETYPE_ORDER[new_idx])
    
    @staticmethod
    def reflect_horizontal(position: MandalaPosition) -> MandalaPosition:
        """Reflect across horizontal axis."""
        return position.opposite()
    
    @staticmethod
    def reflect_vertical(position: MandalaPosition) -> MandalaPosition:
        """Reflect across vertical axis."""
        # 360 - degree gives vertical reflection
        new_degree = (360 - position.degree) % 360
        
        if position.is_axial:
            new_dir = CardinalDirection(
                (4 - position.direction.value) % 4
            )
            return create_axial_position(new_dir)
        else:
            # Find closest archetype to new degree
            for arch in ARCHETYPE_ORDER:
                if abs(ARCHETYPE_DATA[arch].center_degree - new_degree) < 15:
                    return create_peripheral_position(arch)
            return position  # Fallback
    
    @staticmethod
    def quadrature(position: MandalaPosition) -> List[MandalaPosition]:
        """Get the 4 positions in quadrature (90° apart)."""
        positions = [position]
        current = position
        for _ in range(3):
            current = MandalaOperations.rotate(current, 3)  # 90° = 3 steps
            positions.append(current)
        return positions
    
    @staticmethod
    def trine_positions(position: MandalaPosition) -> List[MandalaPosition]:
        """Get positions in trine (120° apart)."""
        positions = [position]
        current = position
        for _ in range(2):
            current = MandalaOperations.rotate(current, 4)  # 120° = 4 steps
            positions.append(current)
        return positions


# =============================================================================
# VALIDATION
# =============================================================================

def validate_mandala() -> bool:
    """Validate mandala module."""
    
    # Test constants
    assert PERIPHERAL_COUNT + AXIAL_COUNT == MANDALA_TOTAL
    assert PERIPHERAL_COUNT == 12
    assert AXIAL_COUNT == 4
    assert MANDALA_TOTAL == 16
    
    # Test mandala creation
    mandala = Mandala()
    assert len(mandala.positions) == 16
    assert len(mandala.axial_positions) == 4
    assert len(mandala.peripheral_positions) == 12
    
    # Test axial positions
    for direction in CardinalDirection:
        axial = mandala.get_axial(direction)
        assert axial.is_axial
        assert axial.direction == direction
    
    # Test peripheral positions
    for archetype in ARCHETYPE_ORDER:
        periph = mandala.get_peripheral(archetype)
        assert periph.is_peripheral
        assert periph.archetype == archetype
    
    # Test element distribution
    for element in Element:
        positions = mandala.positions_by_element(element)
        # 1 axial + 3 peripheral per element
        assert len(positions) == 4
    
    # Test opposite
    north = mandala.get_axial(CardinalDirection.NORTH)
    south = north.opposite()
    assert south.direction == CardinalDirection.SOUTH
    
    # Test circled cross
    cross = CircledCross()
    points = cross.cardinal_points
    assert len(points) == 4
    
    # Test matrix correspondence
    mapping = mandala.to_matrix_correspondence()
    assert len(mapping) == 16
    
    # Check pure archetypes map to axial
    for axial in mandala.axial_positions:
        arch = mapping[axial]
        assert arch.is_pure
    
    return True


if __name__ == "__main__":
    print("Validating Mandala Module...")
    assert validate_mandala()
    print("✓ Mandala Module validated")
    
    # Demo
    print("\n--- Mandala Demo ---")
    
    mandala = Mandala()
    print(f"\nMandala Structure:")
    print(f"  {AXIAL_COUNT} axial + {PERIPHERAL_COUNT} peripheral = {MANDALA_TOTAL} total")
    
    print("\nAxial Positions (4):")
    for pos in mandala.axial_positions:
        print(f"  {pos.direction.name}: {pos.element.name} at {pos.degree}°")
    
    print("\nPeripheral Positions (12):")
    for pos in mandala.peripheral_positions:
        print(f"  {pos.archetype.name}: {pos.element.name} at {pos.degree}°")
    
    print("\nMatrix Correspondence:")
    mapping = mandala.to_matrix_correspondence()
    print("  Axial → Pure Archetypes:")
    for pos in mandala.axial_positions:
        arch = mapping[pos]
        print(f"    {pos.direction.name} → {arch.name}")
    
    print("\nCircled Cross:")
    cross = CircledCross()
    print(f"  Cardinal Points: {list(cross.cardinal_points.keys())}")
    print(f"  Quadrant Centers: {len(cross.quadrant_centers)} sectors")
    
    print("\nQuadrature from North:")
    north = mandala.get_axial(CardinalDirection.NORTH)
    quad = MandalaOperations.quadrature(north)
    for pos in quad:
        print(f"  {pos.name} at {pos.degree}°")

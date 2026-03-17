"""
ATHENA OS - Crystal Computing Lattice
=====================================
1024-Cell Meta-Crystal Structure

From CRYSTAL_COMPUTING_FRAMEWORK.docx:

META-CRYSTAL INDEX SET:
    ℐ := C × S × E × L × P
    |ℐ| = 4^5 = 1024 cells

AXES:
    C (Constants): {π, e, i, φ}
        π - geometry, rotation, closure
        e - flow, exponential change
        i - phase, unitarity
        φ - scale invariance, self-similarity
    
    S (Shapes): {Square, Flower, Cloud, Fractal}
        Square - discrete, grid-based, algebraic
        Flower - wave-like, Fourier, oscillatory
        Cloud - probabilistic, stochastic
        Fractal - self-similar, multiscale
    
    E (Elements): {Earth, Water, Air, Fire}
        Earth - combinatorial, lattice-based
        Water - continuous, PDE/ODE, flow
        Air - information-theoretic, frequency
        Fire - dynamical, chaotic
    
    L (Levels): {L0, L1, L2, L3}
        L0 - local primitive
        L1 - structural invariant
        L2 - inter-regime bridge
        L3 - spectral/categorical limit
    
    P (Poles): {Aether, Anti-Aether, Inner-Shadow, Outer-Shadow}
        Aether - legal, κ-conserving
        Anti-Aether - forbidden, ill-posed
        Inner-Shadow - code/representation
        Outer-Shadow - asymptotic/limit
"""

from __future__ import annotations
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Iterator, Any
import math


# =============================================================================
# CRYSTAL AXES
# =============================================================================

class Constant(IntEnum):
    """Canonical constants axis C."""
    PI = 0       # π - geometry, rotation, closure
    E = 1        # e - flow, exponential change  
    I = 2        # i - phase, unitarity
    PHI = 3      # φ - scale invariance, self-similarity
    
    @property
    def symbol(self) -> str:
        return ['π', 'e', 'i', 'φ'][self.value]
    
    @property
    def description(self) -> str:
        return [
            'Geometry/Rotation/Closure',
            'Flow/Exponential/Growth',
            'Phase/Unitarity/Coherence',
            'Scale/Self-Similarity/Golden'
        ][self.value]


class Shape(IntEnum):
    """Geometric shapes axis S."""
    SQUARE = 0    # Discrete, grid-based, algebraic
    FLOWER = 1    # Wave-like, Fourier, oscillatory
    CLOUD = 2     # Probabilistic, stochastic
    FRACTAL = 3   # Self-similar, multiscale
    
    @property
    def symbol(self) -> str:
        return ['□', '❀', '☁', '✶'][self.value]
    
    @property
    def description(self) -> str:
        return [
            'Discrete/Grid/Algebraic',
            'Wave/Fourier/Oscillatory',
            'Probabilistic/Stochastic',
            'Self-Similar/Multiscale'
        ][self.value]


class Element(IntEnum):
    """Elemental regimes axis E."""
    EARTH = 0    # Combinatorial, lattice-based
    WATER = 1    # Continuous, PDE/ODE, flow
    AIR = 2      # Information-theoretic, frequency
    FIRE = 3     # Dynamical, chaotic
    
    @property
    def symbol(self) -> str:
        return ['??', '??', '??', '??'][self.value]
    
    @property
    def description(self) -> str:
        return [
            'Combinatorial/Lattice',
            'Continuous/Flow/PDE',
            'Information/Frequency/Spectral',
            'Dynamical/Chaotic/Evolution'
        ][self.value]


class Level(IntEnum):
    """Abstraction levels axis L."""
    L0 = 0    # Local primitive operation
    L1 = 1    # Structural invariant/observable
    L2 = 2    # Inter-regime bridge/dual
    L3 = 3    # Spectral/categorical limit
    
    @property
    def description(self) -> str:
        return [
            'Local Primitive',
            'Structural Invariant',
            'Inter-Regime Bridge',
            'Spectral/Categorical Limit'
        ][self.value]


class Pole(IntEnum):
    """Quad-polar extension axis P."""
    AETHER = 0         # Legal, κ-conserving
    ANTI_AETHER = 1    # Forbidden, ill-posed
    INNER_SHADOW = 2   # Code/representation
    OUTER_SHADOW = 3   # Asymptotic/limit
    
    @property
    def symbol(self) -> str:
        return ['Æ', '∄', '⊂', '∞'][self.value]
    
    @property
    def description(self) -> str:
        return [
            'Legal/κ-Conserving',
            'Forbidden/Ill-Posed',
            'Code/Representation',
            'Asymptotic/Limit'
        ][self.value]
    
    @property
    def is_legal(self) -> bool:
        """Check if this pole represents legal operations."""
        return self == Pole.AETHER or self == Pole.INNER_SHADOW


# =============================================================================
# CRYSTAL CELL
# =============================================================================

@dataclass(frozen=True)
class CrystalCell:
    """
    A single cell in the 1024-cell meta-crystal.
    
    Indexed by (c, s, e, l, p) ∈ C × S × E × L × P
    """
    
    constant: Constant
    shape: Shape
    element: Element
    level: Level
    pole: Pole
    
    @property
    def index(self) -> int:
        """
        Compute linear index in [0, 1023].
        
        index = c + 4*s + 16*e + 64*l + 256*p
        """
        return (
            self.constant.value +
            4 * self.shape.value +
            16 * self.element.value +
            64 * self.level.value +
            256 * self.pole.value
        )
    
    @classmethod
    def from_index(cls, index: int) -> 'CrystalCell':
        """Create cell from linear index."""
        if not 0 <= index < 1024:
            raise ValueError(f"Index must be in [0, 1023], got {index}")
        
        c = index % 4
        s = (index // 4) % 4
        e = (index // 16) % 4
        l = (index // 64) % 4
        p = (index // 256) % 4
        
        return cls(
            constant=Constant(c),
            shape=Shape(s),
            element=Element(e),
            level=Level(l),
            pole=Pole(p)
        )
    
    @property
    def coordinate(self) -> Tuple[int, int, int, int, int]:
        """Get coordinate tuple (c, s, e, l, p)."""
        return (
            self.constant.value,
            self.shape.value,
            self.element.value,
            self.level.value,
            self.pole.value
        )
    
    @property
    def is_aetheric(self) -> bool:
        """Check if cell is in Aether pole (legal operations)."""
        return self.pole == Pole.AETHER
    
    @property
    def is_anti(self) -> bool:
        """Check if cell is in Anti-Aether pole (forbidden)."""
        return self.pole == Pole.ANTI_AETHER
    
    @property
    def is_shadow(self) -> bool:
        """Check if cell is in Shadow poles."""
        return self.pole in [Pole.INNER_SHADOW, Pole.OUTER_SHADOW]
    
    @property
    def signature(self) -> str:
        """Get human-readable signature."""
        return f"{self.constant.symbol}/{self.shape.symbol}/{self.element.symbol}/L{self.level.value}/{self.pole.symbol}"
    
    def dual(self) -> 'CrystalCell':
        """Get dual cell (Aether ↔ Anti-Aether, Inner ↔ Outer)."""
        dual_pole = Pole((self.pole.value + 1) % 4)  # Simplified duality
        return CrystalCell(
            constant=self.constant,
            shape=self.shape,
            element=self.element,
            level=self.level,
            pole=dual_pole
        )
    
    def __str__(self) -> str:
        return f"Cell[{self.index}]({self.signature})"


# =============================================================================
# CRYSTAL ADJACENCY
# =============================================================================

@dataclass
class CrystalAdjacency:
    """
    Adjacency structure on the 1024-cell crystal.
    
    Two cells are adjacent if they differ in exactly one axis (Hamming distance 1).
    Each cell has degree 5 × 3 = 15 neighbors.
    """
    
    def hamming_distance(self, a: CrystalCell, b: CrystalCell) -> int:
        """Compute Hamming distance between cells."""
        return sum(
            1 for x, y in zip(a.coordinate, b.coordinate)
            if x != y
        )
    
    def are_adjacent(self, a: CrystalCell, b: CrystalCell) -> bool:
        """Check if two cells are adjacent."""
        return self.hamming_distance(a, b) == 1
    
    def get_neighbors(self, cell: CrystalCell) -> List[CrystalCell]:
        """Get all neighbors of a cell (degree 15)."""
        neighbors = []
        
        # Vary each axis
        for new_c in Constant:
            if new_c != cell.constant:
                neighbors.append(CrystalCell(new_c, cell.shape, cell.element, cell.level, cell.pole))
        
        for new_s in Shape:
            if new_s != cell.shape:
                neighbors.append(CrystalCell(cell.constant, new_s, cell.element, cell.level, cell.pole))
        
        for new_e in Element:
            if new_e != cell.element:
                neighbors.append(CrystalCell(cell.constant, cell.shape, new_e, cell.level, cell.pole))
        
        for new_l in Level:
            if new_l != cell.level:
                neighbors.append(CrystalCell(cell.constant, cell.shape, cell.element, new_l, cell.pole))
        
        for new_p in Pole:
            if new_p != cell.pole:
                neighbors.append(CrystalCell(cell.constant, cell.shape, cell.element, cell.level, new_p))
        
        return neighbors
    
    def constant_neighbors(self, cell: CrystalCell) -> List[CrystalCell]:
        """Get neighbors that differ only in constant."""
        return [
            CrystalCell(c, cell.shape, cell.element, cell.level, cell.pole)
            for c in Constant if c != cell.constant
        ]
    
    def shape_neighbors(self, cell: CrystalCell) -> List[CrystalCell]:
        """Get neighbors that differ only in shape."""
        return [
            CrystalCell(cell.constant, s, cell.element, cell.level, cell.pole)
            for s in Shape if s != cell.shape
        ]
    
    def pole_neighbors(self, cell: CrystalCell) -> List[CrystalCell]:
        """Get neighbors that differ only in pole."""
        return [
            CrystalCell(cell.constant, cell.shape, cell.element, cell.level, p)
            for p in Pole if p != cell.pole
        ]


# =============================================================================
# META-CRYSTAL
# =============================================================================

@dataclass
class MetaCrystal:
    """
    The complete 1024-cell meta-crystal.
    
    A finite, highly structured index set with:
    - 4^5 = 1024 cells
    - Quad-polar extension (Aether/Anti/Inner/Outer)
    - κ-conserving operator families per cell
    """
    
    adjacency: CrystalAdjacency = field(default_factory=CrystalAdjacency)
    
    # Cell cache
    _cells: Dict[int, CrystalCell] = field(default_factory=dict)
    
    @property
    def size(self) -> int:
        """Total number of cells."""
        return 1024
    
    @property
    def positive_size(self) -> int:
        """Number of Aetheric (legal) cells."""
        return 256
    
    def get_cell(self, index: int) -> CrystalCell:
        """Get cell by linear index."""
        if index not in self._cells:
            self._cells[index] = CrystalCell.from_index(index)
        return self._cells[index]
    
    def get_cell_by_coord(self, c: int, s: int, e: int, l: int, p: int) -> CrystalCell:
        """Get cell by coordinate tuple."""
        index = c + 4*s + 16*e + 64*l + 256*p
        return self.get_cell(index)
    
    def iter_cells(self) -> Iterator[CrystalCell]:
        """Iterate over all cells."""
        for i in range(1024):
            yield self.get_cell(i)
    
    def iter_aetheric(self) -> Iterator[CrystalCell]:
        """Iterate over Aetheric (legal) cells only."""
        for cell in self.iter_cells():
            if cell.is_aetheric:
                yield cell
    
    def iter_by_pole(self, pole: Pole) -> Iterator[CrystalCell]:
        """Iterate over cells in a specific pole."""
        base = pole.value * 256
        for i in range(256):
            yield self.get_cell(base + i)
    
    def iter_by_constant(self, constant: Constant) -> Iterator[CrystalCell]:
        """Iterate over cells with a specific constant."""
        for cell in self.iter_cells():
            if cell.constant == constant:
                yield cell
    
    def iter_by_shape(self, shape: Shape) -> Iterator[CrystalCell]:
        """Iterate over cells with a specific shape."""
        for cell in self.iter_cells():
            if cell.shape == shape:
                yield cell
    
    def iter_by_element(self, element: Element) -> Iterator[CrystalCell]:
        """Iterate over cells with a specific element."""
        for cell in self.iter_cells():
            if cell.element == element:
                yield cell
    
    def get_slice(self, constant: Optional[Constant] = None,
                  shape: Optional[Shape] = None,
                  element: Optional[Element] = None,
                  level: Optional[Level] = None,
                  pole: Optional[Pole] = None) -> List[CrystalCell]:
        """Get a slice of the crystal by fixing some coordinates."""
        result = []
        for cell in self.iter_cells():
            if constant is not None and cell.constant != constant:
                continue
            if shape is not None and cell.shape != shape:
                continue
            if element is not None and cell.element != element:
                continue
            if level is not None and cell.level != level:
                continue
            if pole is not None and cell.pole != pole:
                continue
            result.append(cell)
        return result
    
    def count_by_pole(self) -> Dict[Pole, int]:
        """Count cells by pole."""
        return {pole: 256 for pole in Pole}
    
    def summary(self) -> Dict[str, Any]:
        """Get crystal summary."""
        return {
            "total_cells": 1024,
            "axes": {
                "constants": [c.symbol for c in Constant],
                "shapes": [s.symbol for s in Shape],
                "elements": [e.symbol for e in Element],
                "levels": [f"L{l.value}" for l in Level],
                "poles": [p.symbol for p in Pole]
            },
            "cells_per_pole": 256,
            "dimension": 5,
            "degree": 15  # Each cell has 15 neighbors
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_lattice() -> bool:
    """Validate crystal lattice module."""
    
    # Test enums
    assert len(Constant) == 4
    assert len(Shape) == 4
    assert len(Element) == 4
    assert len(Level) == 4
    assert len(Pole) == 4
    
    # Test CrystalCell
    cell = CrystalCell(Constant.PI, Shape.SQUARE, Element.EARTH, Level.L0, Pole.AETHER)
    assert cell.index == 0
    assert cell.is_aetheric
    assert not cell.is_anti
    
    # Test from_index roundtrip
    for i in range(1024):
        cell = CrystalCell.from_index(i)
        assert cell.index == i
    
    # Test adjacency
    adj = CrystalAdjacency()
    cell = CrystalCell.from_index(0)
    neighbors = adj.get_neighbors(cell)
    assert len(neighbors) == 15  # 5 axes × 3 neighbors each
    
    for n in neighbors:
        assert adj.are_adjacent(cell, n)
        assert adj.hamming_distance(cell, n) == 1
    
    # Test MetaCrystal
    crystal = MetaCrystal()
    assert crystal.size == 1024
    assert crystal.positive_size == 256
    
    aetheric_count = sum(1 for _ in crystal.iter_aetheric())
    assert aetheric_count == 256
    
    # Test slicing
    pi_cells = crystal.get_slice(constant=Constant.PI)
    assert len(pi_cells) == 256  # 1024/4
    
    square_earth = crystal.get_slice(shape=Shape.SQUARE, element=Element.EARTH)
    assert len(square_earth) == 64  # 1024/16
    
    return True


if __name__ == "__main__":
    print("Validating Crystal Computing Lattice...")
    assert validate_lattice()
    print("✓ Crystal Lattice validated")
    
    # Demo
    print("\n=== Crystal Computing Lattice Demo ===")
    
    crystal = MetaCrystal()
    summary = crystal.summary()
    
    print(f"\n1024-Cell Meta-Crystal (4⁵ = {summary['total_cells']})")
    print(f"\nAxes:")
    print(f"  Constants: {summary['axes']['constants']}")
    print(f"  Shapes: {summary['axes']['shapes']}")
    print(f"  Elements: {summary['axes']['elements']}")
    print(f"  Levels: {summary['axes']['levels']}")
    print(f"  Poles: {summary['axes']['poles']}")
    
    print(f"\nStructure:")
    print(f"  Dimension: {summary['dimension']}")
    print(f"  Degree (neighbors per cell): {summary['degree']}")
    print(f"  Cells per pole: {summary['cells_per_pole']}")
    
    print("\nSample cells:")
    for i in [0, 255, 512, 1023]:
        cell = crystal.get_cell(i)
        print(f"  {cell}")

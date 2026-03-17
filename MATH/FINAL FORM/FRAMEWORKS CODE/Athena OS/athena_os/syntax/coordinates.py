"""
ATHENA OS - SYNTAX CRYSTAL COORDINATES
======================================
The 4^4 Crystal Index System

From SYNTAX.docx:

COORDINATE SYSTEM:
    Each artifact/claim is locatable by coordinate ⟨P, L, D, R⟩:
    
    P ∈ {S, A, I, O}        - Pole axis (4 values)
    L ∈ {B12, B13, B14, B_outer} - Lens axis (4 values)  
    D ∈ {Spin, Rev, Eq, Drift}   - Direction axis (4 values)
    R ∈ {Txt, Str, Mid, Obs}     - Representation axis (4 values)
    
    Total cells: 4^4 = 256

CELL CONTENTS:
    Each cell contains:
    - Objects list
    - Operators list
    - Theorems list
    - Examples/tests list

CROSS-CELL DUALITY:
    - Mirror statement requirement
    - Boundary case requirement
    - Drift witness requirement
    - Extraction artifact requirement
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Set, Optional, Any, Tuple, 
    Iterator, TypeVar, Generic, FrozenSet
)
from enum import Enum, auto
import itertools

from .core import Pole, RepLevel, Direction, LensFamily, Artifact


# =============================================================================
# COORDINATE TUPLE
# =============================================================================

@dataclass(frozen=True)
class CrystalCoord:
    """
    A coordinate in the 4^4 crystal index.
    
    ⟨P, L, D, R⟩ where each axis has 4 values.
    """
    
    pole: Pole
    lens: LensFamily
    direction: Direction
    rep_level: RepLevel
    
    def __str__(self) -> str:
        return f"⟨{self.pole.symbol}, {self.lens.value}, {self.direction.symbol}, {self.rep_level.symbol}⟩"
    
    def __repr__(self) -> str:
        return f"CrystalCoord({self.pole.value}, {self.lens.value}, {self.direction.value}, {self.rep_level.value})"
    
    @property
    def index(self) -> int:
        """
        Convert to linear index 0-255.
        
        Index = P*64 + L*16 + D*4 + R
        """
        p_idx = list(Pole).index(self.pole)
        l_idx = list(LensFamily).index(self.lens)
        d_idx = list(Direction).index(self.direction)
        r_idx = list(RepLevel).index(self.rep_level)
        
        return p_idx * 64 + l_idx * 16 + d_idx * 4 + r_idx
    
    @classmethod
    def from_index(cls, idx: int) -> 'CrystalCoord':
        """Create coordinate from linear index."""
        if not 0 <= idx < 256:
            raise ValueError(f"Index must be 0-255, got {idx}")
        
        r_idx = idx % 4
        d_idx = (idx // 4) % 4
        l_idx = (idx // 16) % 4
        p_idx = idx // 64
        
        return cls(
            pole=list(Pole)[p_idx],
            lens=list(LensFamily)[l_idx],
            direction=list(Direction)[d_idx],
            rep_level=list(RepLevel)[r_idx]
        )
    
    def dual(self) -> 'CrystalCoord':
        """
        Get dual coordinate (mirror across all axes).
        
        P ↔ opposite pole, D ↔ opposite direction
        """
        pole_dual = {
            Pole.S: Pole.A,
            Pole.A: Pole.S,
            Pole.I: Pole.O,
            Pole.O: Pole.I
        }
        
        dir_dual = {
            Direction.SPIN: Direction.REV,
            Direction.REV: Direction.SPIN,
            Direction.EQ: Direction.DRIFT,
            Direction.DRIFT: Direction.EQ
        }
        
        return CrystalCoord(
            pole=pole_dual[self.pole],
            lens=self.lens,
            direction=dir_dual[self.direction],
            rep_level=self.rep_level
        )
    
    def neighbors(self) -> List['CrystalCoord']:
        """Get coordinates that differ by one axis value."""
        neighbors = []
        
        # Vary pole
        for p in Pole:
            if p != self.pole:
                neighbors.append(CrystalCoord(p, self.lens, self.direction, self.rep_level))
        
        # Vary lens
        for l in LensFamily:
            if l != self.lens:
                neighbors.append(CrystalCoord(self.pole, l, self.direction, self.rep_level))
        
        # Vary direction
        for d in Direction:
            if d != self.direction:
                neighbors.append(CrystalCoord(self.pole, self.lens, d, self.rep_level))
        
        # Vary rep level
        for r in RepLevel:
            if r != self.rep_level:
                neighbors.append(CrystalCoord(self.pole, self.lens, self.direction, r))
        
        return neighbors
    
    def is_compatible_with(self, artifact: Artifact) -> bool:
        """Check if an artifact belongs at this coordinate."""
        return artifact.pole == self.pole and artifact.rep_level == self.rep_level


# =============================================================================
# CELL CONTENTS
# =============================================================================

@dataclass
class CellContent:
    """
    Contents of a single cell in the crystal index.
    
    Each cell contains:
    - Objects (artifacts at this coordinate)
    - Operators (operations available)
    - Theorems (proven properties)
    - Examples (test cases)
    """
    
    coord: CrystalCoord
    objects: List[str] = field(default_factory=list)      # Artifact IDs
    operators: List[str] = field(default_factory=list)    # Operator names
    theorems: List[str] = field(default_factory=list)     # Theorem statements
    examples: List[str] = field(default_factory=list)     # Example/test IDs
    
    # Duality requirements
    mirror_statement: Optional[str] = None
    boundary_cases: List[str] = field(default_factory=list)
    drift_witnesses: List[str] = field(default_factory=list)
    extraction_artifacts: List[str] = field(default_factory=list)
    
    @property
    def is_populated(self) -> bool:
        """Check if cell has any content."""
        return bool(self.objects or self.operators or 
                   self.theorems or self.examples)
    
    @property
    def is_complete(self) -> bool:
        """Check if cell has all required duality elements."""
        return (self.mirror_statement is not None and
                bool(self.boundary_cases) and
                bool(self.drift_witnesses))
    
    def add_object(self, artifact_id: str) -> None:
        """Add an object to this cell."""
        if artifact_id not in self.objects:
            self.objects.append(artifact_id)
    
    def add_operator(self, op_name: str) -> None:
        """Add an operator to this cell."""
        if op_name not in self.operators:
            self.operators.append(op_name)
    
    def add_theorem(self, theorem: str) -> None:
        """Add a theorem to this cell."""
        if theorem not in self.theorems:
            self.theorems.append(theorem)
    
    def add_example(self, example_id: str) -> None:
        """Add an example to this cell."""
        if example_id not in self.examples:
            self.examples.append(example_id)


# =============================================================================
# CRYSTAL INDEX (256-CELL ATLAS)
# =============================================================================

class CrystalIndex:
    """
    The complete 4^4 = 256 cell crystal index.
    
    Provides addressable access to all syntax algebra components.
    """
    
    def __init__(self):
        """Initialize empty crystal index."""
        self._cells: Dict[int, CellContent] = {}
        
        # Pre-create all 256 cells
        for idx in range(256):
            coord = CrystalCoord.from_index(idx)
            self._cells[idx] = CellContent(coord=coord)
    
    def __getitem__(self, coord: CrystalCoord) -> CellContent:
        """Get cell by coordinate."""
        return self._cells[coord.index]
    
    def __setitem__(self, coord: CrystalCoord, content: CellContent) -> None:
        """Set cell content."""
        self._cells[coord.index] = content
    
    def __iter__(self) -> Iterator[Tuple[CrystalCoord, CellContent]]:
        """Iterate over all cells."""
        for idx, cell in self._cells.items():
            yield CrystalCoord.from_index(idx), cell
    
    def __len__(self) -> int:
        return 256
    
    @property
    def populated_count(self) -> int:
        """Count of populated cells."""
        return sum(1 for cell in self._cells.values() if cell.is_populated)
    
    @property
    def complete_count(self) -> int:
        """Count of complete cells (with all duality requirements)."""
        return sum(1 for cell in self._cells.values() if cell.is_complete)
    
    def get_by_index(self, idx: int) -> CellContent:
        """Get cell by linear index."""
        return self._cells[idx]
    
    def filter_by_pole(self, pole: Pole) -> Iterator[Tuple[CrystalCoord, CellContent]]:
        """Get all cells with a specific pole."""
        for idx, cell in self._cells.items():
            coord = CrystalCoord.from_index(idx)
            if coord.pole == pole:
                yield coord, cell
    
    def filter_by_lens(self, lens: LensFamily) -> Iterator[Tuple[CrystalCoord, CellContent]]:
        """Get all cells with a specific lens family."""
        for idx, cell in self._cells.items():
            coord = CrystalCoord.from_index(idx)
            if coord.lens == lens:
                yield coord, cell
    
    def filter_by_direction(self, direction: Direction) -> Iterator[Tuple[CrystalCoord, CellContent]]:
        """Get all cells with a specific direction."""
        for idx, cell in self._cells.items():
            coord = CrystalCoord.from_index(idx)
            if coord.direction == direction:
                yield coord, cell
    
    def filter_by_rep(self, rep: RepLevel) -> Iterator[Tuple[CrystalCoord, CellContent]]:
        """Get all cells with a specific representation level."""
        for idx, cell in self._cells.items():
            coord = CrystalCoord.from_index(idx)
            if coord.rep_level == rep:
                yield coord, cell
    
    def get_slice(self, 
                  pole: Optional[Pole] = None,
                  lens: Optional[LensFamily] = None,
                  direction: Optional[Direction] = None,
                  rep: Optional[RepLevel] = None) -> List[Tuple[CrystalCoord, CellContent]]:
        """
        Get a slice of the crystal by fixing one or more axes.
        """
        results = []
        
        for idx, cell in self._cells.items():
            coord = CrystalCoord.from_index(idx)
            
            if pole is not None and coord.pole != pole:
                continue
            if lens is not None and coord.lens != lens:
                continue
            if direction is not None and coord.direction != direction:
                continue
            if rep is not None and coord.rep_level != rep:
                continue
            
            results.append((coord, cell))
        
        return results
    
    def place_artifact(self, artifact_id: str, coord: CrystalCoord) -> None:
        """Place an artifact at a specific coordinate."""
        self._cells[coord.index].add_object(artifact_id)
    
    def place_operator(self, op_name: str, coord: CrystalCoord) -> None:
        """Place an operator at a specific coordinate."""
        self._cells[coord.index].add_operator(op_name)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        pole_counts = {p.value: 0 for p in Pole}
        lens_counts = {l.value: 0 for l in LensFamily}
        dir_counts = {d.value: 0 for d in Direction}
        rep_counts = {r.value: 0 for r in RepLevel}
        
        for idx, cell in self._cells.items():
            if cell.is_populated:
                coord = CrystalCoord.from_index(idx)
                pole_counts[coord.pole.value] += 1
                lens_counts[coord.lens.value] += 1
                dir_counts[coord.direction.value] += 1
                rep_counts[coord.rep_level.value] += 1
        
        return {
            "total_cells": 256,
            "populated": self.populated_count,
            "complete": self.complete_count,
            "by_pole": pole_counts,
            "by_lens": lens_counts,
            "by_direction": dir_counts,
            "by_representation": rep_counts
        }


# =============================================================================
# COORDINATE UTILITIES
# =============================================================================

def all_coordinates() -> Iterator[CrystalCoord]:
    """Generate all 256 coordinates."""
    for p in Pole:
        for l in LensFamily:
            for d in Direction:
                for r in RepLevel:
                    yield CrystalCoord(p, l, d, r)


def coordinates_for_artifact(artifact: Artifact) -> List[CrystalCoord]:
    """
    Get all valid coordinates for an artifact.
    
    Filters based on pole and representation level.
    """
    results = []
    for coord in all_coordinates():
        if coord.is_compatible_with(artifact):
            results.append(coord)
    return results


def dual_pairs() -> Iterator[Tuple[CrystalCoord, CrystalCoord]]:
    """Generate all 128 dual coordinate pairs."""
    seen = set()
    
    for coord in all_coordinates():
        dual = coord.dual()
        pair_key = frozenset([coord.index, dual.index])
        
        if pair_key not in seen:
            seen.add(pair_key)
            yield coord, dual


# =============================================================================
# VALIDATION
# =============================================================================

def validate_coordinates() -> bool:
    """Validate coordinates module."""
    
    # Test CrystalCoord
    coord = CrystalCoord(
        pole=Pole.S,
        lens=LensFamily.B12,
        direction=Direction.SPIN,
        rep_level=RepLevel.TXT
    )
    assert coord.index == 0
    
    # Test from_index
    coord2 = CrystalCoord.from_index(0)
    assert coord2 == coord
    
    # Test all indices
    for idx in range(256):
        c = CrystalCoord.from_index(idx)
        assert c.index == idx, f"Index mismatch at {idx}"
    
    # Test dual
    coord = CrystalCoord(Pole.S, LensFamily.B12, Direction.SPIN, RepLevel.TXT)
    dual = coord.dual()
    assert dual.pole == Pole.A
    assert dual.direction == Direction.REV
    
    # Double dual returns to original (for pole and direction)
    double_dual = dual.dual()
    assert double_dual.pole == coord.pole
    assert double_dual.direction == coord.direction
    
    # Test neighbors
    neighbors = coord.neighbors()
    assert len(neighbors) == 12  # 3+3+3+3 = 12
    
    # Test CrystalIndex
    index = CrystalIndex()
    assert len(index) == 256
    assert index.populated_count == 0
    
    # Add some content
    index.place_artifact("test_art", coord)
    assert index.populated_count == 1
    assert "test_art" in index[coord].objects
    
    # Test slicing
    s_slice = index.get_slice(pole=Pole.S)
    assert len(s_slice) == 64  # 4*4*4 = 64
    
    # Test all_coordinates generator
    coords = list(all_coordinates())
    assert len(coords) == 256
    
    # Test dual_pairs
    pairs = list(dual_pairs())
    assert len(pairs) == 128
    
    return True


if __name__ == "__main__":
    print("Validating SYNTAX coordinates...")
    assert validate_coordinates()
    print("✓ SYNTAX coordinates validated")

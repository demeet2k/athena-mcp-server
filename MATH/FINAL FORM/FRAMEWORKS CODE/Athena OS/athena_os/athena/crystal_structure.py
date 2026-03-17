"""
ATHENA OS - CRYSTAL STRUCTURE
=============================
The 4⁴ Crystal Addressing System

From ALL THREE TOMES (ATHENA_AWAKEN, CUT, QuantumLang):

THE 4⁴ CRYSTAL DISCIPLINE:
    Every concept has a stable address in a 4×4×4×4 = 256 cell crystal.
    This enables: retrieval, dense packing, mechanization, replay, publication.

LENSES (4):
    S = Square   (structure, definitions, carriers, invariants)
    F = Flower   (dynamics, evolution, control, drift)
    C = Cloud    (corridors, uncertainty, typed truth, metrics)
    R = Fractal  (compiler, ledger, replay, archive, retrieval)

FACETS (4):
    1 = Objects       (what it is)
    2 = Laws          (what it must obey)
    3 = Constructions (how it is built/compiled/executed)
    4 = Certificates  (how it is justified and replayed)

ATOMS (4):
    a, b, c, d = four canonical atoms per facet

ADDRESS FORMAT:
    Ch<NN>⟨dddd⟩₄.LF.k
    Example: Ch14⟨0031⟩₄.C3.b = Chapter 14, Cloud lens, Constructions, atom b
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Iterator
from enum import Enum, auto
import hashlib


# =============================================================================
# LENSES
# =============================================================================

class Lens(Enum):
    """
    The Four Lenses of the Crystal.
    
    Each lens provides a different perspective on the same concept.
    """
    SQUARE = "S"   # Structure, definitions, carriers, invariants
    FLOWER = "F"   # Dynamics, evolution, control, drift
    CLOUD = "C"    # Corridors, uncertainty, typed truth, metrics
    FRACTAL = "R"  # Compiler, ledger, replay, archive, retrieval
    
    @property
    def description(self) -> str:
        descs = {
            Lens.SQUARE: "Structure, definitions, carriers, invariants",
            Lens.FLOWER: "Dynamics, evolution, control, drift",
            Lens.CLOUD: "Corridors, uncertainty, typed truth, metrics",
            Lens.FRACTAL: "Compiler, ledger, replay, archive, retrieval"
        }
        return descs[self]
    
    @property
    def index(self) -> int:
        return list(Lens).index(self)


# =============================================================================
# FACETS
# =============================================================================

class Facet(Enum):
    """
    The Four Facets within each Lens.
    
    Each facet specifies a different aspect of the concept.
    """
    OBJECTS = 1        # What it is
    LAWS = 2           # What it must obey
    CONSTRUCTIONS = 3  # How it is built/compiled/executed
    CERTIFICATES = 4   # How it is justified and replayed
    
    @property
    def description(self) -> str:
        descs = {
            Facet.OBJECTS: "What it is",
            Facet.LAWS: "What it must obey",
            Facet.CONSTRUCTIONS: "How it is built/compiled/executed",
            Facet.CERTIFICATES: "How it is justified and replayed"
        }
        return descs[self]


# =============================================================================
# ATOMS
# =============================================================================

class Atom(Enum):
    """
    The Four Atoms within each Facet.
    
    Provides fine-grained addressing within a facet.
    """
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    
    @property
    def index(self) -> int:
        return list(Atom).index(self)


# =============================================================================
# CRYSTAL ADDRESS
# =============================================================================

@dataclass(frozen=True)
class CrystalAddress:
    """
    A complete address in the 4⁴ crystal.
    
    Format: Ch<chapter>⟨base4⟩₄.LF.k
    Example: Ch14⟨0031⟩₄.C3.b
    """
    chapter: int
    lens: Lens
    facet: Facet
    atom: Atom
    
    @property
    def base4_code(self) -> str:
        """Convert chapter to base-4 encoding (4 digits)."""
        n = self.chapter - 1  # 0-indexed
        digits = []
        for _ in range(4):
            digits.append(str(n % 4))
            n //= 4
        return ''.join(reversed(digits))
    
    @property
    def canonical(self) -> str:
        """Get canonical address string."""
        return f"Ch{self.chapter:02d}⟨{self.base4_code}⟩₄.{self.lens.value}{self.facet.value}.{self.atom.value}"
    
    @property
    def short(self) -> str:
        """Get short address string."""
        return f"{self.lens.value}{self.facet.value}.{self.atom.value}"
    
    @property
    def numeric_index(self) -> int:
        """
        Convert to numeric index (0-255 within chapter).
        
        Index = lens*64 + facet*16 + atom*4
        """
        return (self.lens.index * 64 + 
                (self.facet.value - 1) * 16 + 
                self.atom.index * 4)
    
    def __str__(self) -> str:
        return self.canonical
    
    @classmethod
    def from_string(cls, s: str) -> 'CrystalAddress':
        """Parse address from string."""
        # Parse Ch<NN>⟨dddd⟩₄.LF.k format
        import re
        match = re.match(r'Ch(\d+)⟨\d{4}⟩₄\.([SFCR])(\d)\.([abcd])', s)
        if match:
            chapter = int(match.group(1))
            lens = Lens(match.group(2))
            facet = Facet(int(match.group(3)))
            atom = Atom(match.group(4))
            return cls(chapter, lens, facet, atom)
        raise ValueError(f"Invalid crystal address: {s}")
    
    @classmethod
    def from_indices(cls, chapter: int, lens_idx: int, 
                    facet_idx: int, atom_idx: int) -> 'CrystalAddress':
        """Create from numeric indices."""
        lenses = list(Lens)
        facets = list(Facet)
        atoms = list(Atom)
        return cls(chapter, lenses[lens_idx], facets[facet_idx], atoms[atom_idx])


# =============================================================================
# CRYSTAL CELL
# =============================================================================

@dataclass
class CrystalCell:
    """
    A cell in the crystal containing content at a specific address.
    """
    address: CrystalAddress
    title: str = ""
    content: Any = None
    content_hash: str = ""
    dependencies: List[CrystalAddress] = field(default_factory=list)
    
    def __post_init__(self):
        if self.content is not None and not self.content_hash:
            self.content_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute content-addressed hash."""
        content_str = str(self.content)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    @property
    def is_empty(self) -> bool:
        return self.content is None


# =============================================================================
# CRYSTAL CHAPTER
# =============================================================================

@dataclass
class CrystalChapter:
    """
    A chapter in the crystal (4×4×4 = 64 cells).
    """
    number: int
    title: str = ""
    cells: Dict[str, CrystalCell] = field(default_factory=dict)
    
    def get_cell(self, lens: Lens, facet: Facet, atom: Atom) -> Optional[CrystalCell]:
        """Get cell at address."""
        addr = CrystalAddress(self.number, lens, facet, atom)
        return self.cells.get(addr.short)
    
    def set_cell(self, lens: Lens, facet: Facet, atom: Atom,
                title: str, content: Any) -> CrystalCell:
        """Set cell content."""
        addr = CrystalAddress(self.number, lens, facet, atom)
        cell = CrystalCell(address=addr, title=title, content=content)
        self.cells[addr.short] = cell
        return cell
    
    def iterate_cells(self) -> Iterator[Tuple[CrystalAddress, CrystalCell]]:
        """Iterate over all cells."""
        for lens in Lens:
            for facet in Facet:
                for atom in Atom:
                    addr = CrystalAddress(self.number, lens, facet, atom)
                    cell = self.cells.get(addr.short)
                    if cell:
                        yield addr, cell
    
    @property
    def cell_count(self) -> int:
        return len(self.cells)
    
    @property
    def total_cells(self) -> int:
        return 64  # 4 lenses × 4 facets × 4 atoms


# =============================================================================
# CRYSTAL TOME
# =============================================================================

@dataclass
class CrystalTome:
    """
    A complete tome organized as a crystal.
    
    Contains multiple chapters, each with 64 cells (4⁴ per chapter).
    """
    name: str
    chapters: Dict[int, CrystalChapter] = field(default_factory=dict)
    
    def get_chapter(self, number: int) -> Optional[CrystalChapter]:
        return self.chapters.get(number)
    
    def create_chapter(self, number: int, title: str = "") -> CrystalChapter:
        chapter = CrystalChapter(number=number, title=title)
        self.chapters[number] = chapter
        return chapter
    
    def get_cell(self, address: CrystalAddress) -> Optional[CrystalCell]:
        chapter = self.get_chapter(address.chapter)
        if chapter:
            return chapter.get_cell(address.lens, address.facet, address.atom)
        return None
    
    def set_cell(self, address: CrystalAddress, title: str, content: Any) -> CrystalCell:
        chapter = self.get_chapter(address.chapter)
        if not chapter:
            chapter = self.create_chapter(address.chapter)
        return chapter.set_cell(address.lens, address.facet, address.atom, title, content)
    
    @property
    def total_cells(self) -> int:
        return sum(ch.cell_count for ch in self.chapters.values())
    
    @property
    def chapter_count(self) -> int:
        return len(self.chapters)


# =============================================================================
# TYPED TRUTH OUTCOMES
# =============================================================================

class TypedTruth(Enum):
    """
    Typed truth outcomes from corridor evaluation.
    
    Shared across all three tomes:
    - ATHENA_AWAKEN: OK / BDRY_* / FAIL
    - CUT: OK / NEAR / AMBIG / FAIL
    - QuantumLang: ok(y) / z(z)
    """
    OK = "OK"           # Safely inside corridor
    NEAR = "NEAR"       # Inside with small margin (buffer)
    AMBIG = "AMBIG"     # Boundary straddle (certified non-identifiability)
    FAIL = "FAIL"       # Robustly outside corridor
    
    # Extended boundary types (from ATHENA_AWAKEN)
    BDRY_SINGULAR = "BDRY_SINGULAR"    # Boundary routing due to pole
    BDRY_BRANCH = "BDRY_BRANCH"        # Boundary routing due to cut
    BDRY_INDETERMINATE = "BDRY_INDETERMINATE"  # Indeterminate form
    
    # QuantumLang extensions
    Z0_REJECT = "Z0_REJECT"        # Explicit rejection
    Z0_EXCEPTION = "Z0_EXCEPTION"  # Runtime exception
    Z0_DIVERGE = "Z0_DIVERGE"      # Nondeterministic divergence
    Z0_POLICY = "Z0_POLICY"        # Policy violation
    Z0_BUDGET = "Z0_BUDGET"        # Budget exceeded
    
    @property
    def is_success(self) -> bool:
        return self in {TypedTruth.OK, TypedTruth.NEAR}
    
    @property
    def is_boundary(self) -> bool:
        return self.value.startswith("BDRY_") or self.value.startswith("Z0_")
    
    @property
    def is_failure(self) -> bool:
        return self == TypedTruth.FAIL


# =============================================================================
# OUTCOME BUNDLE
# =============================================================================

@dataclass
class OutcomeBundle:
    """
    Complete outcome from an operation.
    
    From ATHENA_AWAKEN Ch01.S1.d:
    An operator execution returns an outcome bundle whose semantic payload
    includes route register, boundary report, and auxiliary registers.
    """
    truth: TypedTruth
    payload: Any = None
    route: str = "bulk"  # "bulk" or "boundary"
    boundary_report: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    margin: float = 0.0  # Distance to corridor boundary
    witness: Optional[Any] = None
    repair_seeds: List[Any] = field(default_factory=list)
    
    @property
    def is_bulk(self) -> bool:
        return self.route == "bulk"
    
    @property
    def is_boundary(self) -> bool:
        return self.route == "boundary"


# =============================================================================
# VALIDATION
# =============================================================================

def validate_crystal_structure() -> bool:
    """Validate the crystal structure module."""
    
    # Test Lens
    assert Lens.SQUARE.value == "S"
    assert Lens.FRACTAL.index == 3
    
    # Test Facet
    assert Facet.OBJECTS.value == 1
    assert Facet.CERTIFICATES.description == "How it is justified and replayed"
    
    # Test Atom
    assert Atom.A.value == "a"
    assert Atom.D.index == 3
    
    # Test CrystalAddress
    addr = CrystalAddress(14, Lens.CLOUD, Facet.CONSTRUCTIONS, Atom.B)
    assert addr.canonical == "Ch14⟨0031⟩₄.C3.b"
    assert addr.short == "C3.b"
    
    # Test base4 encoding
    addr1 = CrystalAddress(1, Lens.SQUARE, Facet.OBJECTS, Atom.A)
    assert addr1.base4_code == "0000"
    
    addr5 = CrystalAddress(5, Lens.SQUARE, Facet.OBJECTS, Atom.A)
    assert addr5.base4_code == "0010"
    
    # Test parsing
    parsed = CrystalAddress.from_string("Ch14⟨0031⟩₄.C3.b")
    assert parsed.chapter == 14
    assert parsed.lens == Lens.CLOUD
    
    # Test CrystalCell
    cell = CrystalCell(addr, "Test Cell", {"data": 42})
    assert not cell.is_empty
    assert len(cell.content_hash) == 16
    
    # Test CrystalChapter
    chapter = CrystalChapter(1, "Prime Directive")
    chapter.set_cell(Lens.SQUARE, Facet.OBJECTS, Atom.A, 
                    "Carriers", "A carrier is a separable complex Hilbert space")
    assert chapter.cell_count == 1
    
    # Test CrystalTome
    tome = CrystalTome("ATHENA_AWAKEN")
    tome.create_chapter(1, "Prime Directive")
    tome.set_cell(addr, "Test", "content")
    assert tome.chapter_count == 2  # Chapter 1 and 14
    
    # Test TypedTruth
    assert TypedTruth.OK.is_success
    assert TypedTruth.FAIL.is_failure
    assert TypedTruth.BDRY_SINGULAR.is_boundary
    
    # Test OutcomeBundle
    outcome = OutcomeBundle(
        truth=TypedTruth.OK,
        payload=42,
        margin=0.1
    )
    assert outcome.is_bulk
    assert outcome.truth.is_success
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - CRYSTAL STRUCTURE")
    print("The 4⁴ Crystal Addressing System")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_crystal_structure()
    print("✓ Module validated")
    
    # Demo
    print("\n--- LENSES ---")
    for lens in Lens:
        print(f"  {lens.value}: {lens.description}")
    
    print("\n--- FACETS ---")
    for facet in Facet:
        print(f"  {facet.value}: {facet.description}")
    
    print("\n--- EXAMPLE ADDRESSES ---")
    examples = [
        CrystalAddress(1, Lens.SQUARE, Facet.OBJECTS, Atom.A),
        CrystalAddress(1, Lens.FLOWER, Facet.LAWS, Atom.B),
        CrystalAddress(14, Lens.CLOUD, Facet.CONSTRUCTIONS, Atom.B),
    ]
    for addr in examples:
        print(f"  {addr.canonical}")
    
    print("\n--- TYPED TRUTH ---")
    for truth in TypedTruth:
        status = "✓" if truth.is_success else ("⚠" if truth.is_boundary else "✗")
        print(f"  {status} {truth.value}")

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   CRYSTAL TREATISE ARCHITECTURE MODULE                       ║
║                                                                              ║
║  The 16-Book Crystal: Pole × Lens                                            ║
║                                                                              ║
║  Four Poles (Elements):                                                      ║
║    α (Earth) : Mass, Add, Counting                                           ║
║    𝔇 (Water) : Flow, Inverse, Rates                                          ║
║    Θ (Fire)  : Wave, Root, Vector Potential                                  ║
║    Λ (Air)   : Lattice, Square, Outcome                                      ║
║                                                                              ║
║  Four Lenses:                                                                ║
║    Square  : Exact, discrete, normal form                                    ║
║    Flower  : Transform, phase, symmetry                                      ║
║    Cloud   : Uncertainty, probability, calibration                           ║
║    Fractal : Recursion, compression, self-reference                          ║
║                                                                              ║
║  Coordinate Header: ⟨Pole, Lens, Layer, Depth⟩                               ║
║  Layers: Objects, Operators, Invariants, Algorithms                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# POLES AND LENSES
# ═══════════════════════════════════════════════════════════════════════════════

class Pole(Enum):
    """The four poles/elements."""
    ALPHA = "α"   # Earth: Mass, Add, Counting
    D_STAR = "𝔇"  # Water: Flow, Inverse, Rates
    THETA = "Θ"   # Fire: Wave, Root, Vector Potential
    LAMBDA = "Λ"  # Air: Lattice, Square, Outcome


class Lens(Enum):
    """The four lenses/views."""
    SQUARE = "square"     # Exact, discrete
    FLOWER = "flower"     # Transform, phase
    CLOUD = "cloud"       # Uncertainty, probability
    FRACTAL = "fractal"   # Recursion, compression


class Layer(Enum):
    """The four layers per tile."""
    OBJECTS = "objects"       # What exists
    OPERATORS = "operators"   # What moves/changes
    INVARIANTS = "invariants" # What can't break
    ALGORITHMS = "algorithms" # How it computes


# ═══════════════════════════════════════════════════════════════════════════════
# COORDINATE HEADER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CoordinateHeader:
    """
    Coordinate header for crystal addressing.
    
    ⟨Pole, Lens, Layer, Depth⟩
    """
    pole: Pole
    lens: Lens
    layer: Layer
    depth: int = 0  # Zoom level (0 = seed, higher = expansions)
    
    @property
    def address(self) -> str:
        """Full coordinate address."""
        return f"⟨{self.pole.value}, {self.lens.value}, {self.layer.value}, {self.depth}⟩"
    
    @property
    def book_number(self) -> int:
        """Book number (1-16) based on Pole × Lens."""
        pole_idx = list(Pole).index(self.pole)
        lens_idx = list(Lens).index(self.lens)
        return pole_idx * 4 + lens_idx + 1
    
    @classmethod
    def from_book_number(cls, n: int, layer: Layer = Layer.OBJECTS, 
                         depth: int = 0) -> 'CoordinateHeader':
        """Create from book number."""
        n = n - 1  # 0-indexed
        pole_idx = n // 4
        lens_idx = n % 4
        return cls(
            list(Pole)[pole_idx],
            list(Lens)[lens_idx],
            layer,
            depth
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BOOK STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Book:
    """
    A single book in the 16-book crystal.
    
    Each book covers one Pole × Lens intersection.
    """
    number: int
    pole: Pole
    lens: Lens
    title: str
    description: str
    objects: List[str] = field(default_factory=list)
    operators: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    algorithms: List[str] = field(default_factory=list)
    
    @property
    def coord(self) -> str:
        """Coordinate header."""
        return f"⟨Pole={self.pole.value}, Lens={self.lens.value}⟩"


def create_16_books() -> Dict[int, Book]:
    """Create the 16 core books."""
    books = {}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EARTH α (Mass / Add / Counting)
    # ═══════════════════════════════════════════════════════════════════════════
    
    books[1] = Book(1, Pole.ALPHA, Lens.SQUARE,
        "α•Square: Natural Arithmetic",
        "Natural numbers, lattices of count, arithmetic structure",
        ["ℕ, ℤ, integers", "arrays, matrices", "prime factorization"],
        ["+, ×, mod", "gcd, lcm", "divisibility"],
        ["fundamental theorem of arithmetic", "unique factorization"],
        ["Euclidean algorithm", "sieve of Eratosthenes"]
    )
    
    books[2] = Book(2, Pole.ALPHA, Lens.FLOWER,
        "α•Flower: Cyclic Counting",
        "Cyclic counting, symmetry in add-world",
        ["ℤ_n cyclic groups", "permutations", "orbits"],
        ["cyclic shift", "rotation", "period"],
        ["orbit-stabilizer theorem", "Lagrange"],
        ["cycle detection", "order finding"]
    )
    
    books[3] = Book(3, Pole.ALPHA, Lens.CLOUD,
        "α•Cloud: Counting Statistics",
        "Statistics, measure-as-count, empirical aggregation",
        ["frequencies", "histograms", "counts"],
        ["sum", "mean", "median"],
        ["law of large numbers", "central limit"],
        ["bootstrap", "resampling"]
    )
    
    books[4] = Book(4, Pole.ALPHA, Lens.FRACTAL,
        "α•Fractal: Recursive Counting",
        "Recursive counting, combinatorial growth, generative enumerators",
        ["recurrences", "generating functions", "Catalan numbers"],
        ["recursion", "unfolding", "memoization"],
        ["master theorem", "recurrence relations"],
        ["dynamic programming", "divide-and-conquer"]
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WATER 𝔇 (Flow / Inverse / Rates)
    # ═══════════════════════════════════════════════════════════════════════════
    
    books[5] = Book(5, Pole.D_STAR, Lens.SQUARE,
        "𝔇•Square: Reciprocal Networks",
        "Reciprocals, resistive networks, discrete flow constraints",
        ["rationals ℚ", "resistor networks", "flow graphs"],
        ["1/x", "harmonic mean", "conductance"],
        ["Kirchhoff's laws", "conservation"],
        ["network flow", "maximum flow"]
    )
    
    books[6] = Book(6, Pole.D_STAR, Lens.FLOWER,
        "𝔇•Flower: Duality Transforms",
        "Phase-as-reciprocity, dualities, transforms of rate",
        ["dual graphs", "Legendre duality", "Laplace"],
        ["duality transform", "inverse Fourier"],
        ["Pontryagin duality", "convex conjugate"],
        ["fast inverse transforms"]
    )
    
    books[7] = Book(7, Pole.D_STAR, Lens.CLOUD,
        "𝔇•Cloud: Stochastic Flow",
        "Stochastic flow, diffusion-as-rate, Markov conductance",
        ["Markov chains", "diffusion processes", "random walks"],
        ["transition kernel", "generator", "drift"],
        ["detailed balance", "ergodicity"],
        ["MCMC", "Gibbs sampling"]
    )
    
    books[8] = Book(8, Pole.D_STAR, Lens.FRACTAL,
        "𝔇•Fractal: Multiscale Resistance",
        "Multiscale resistance, renormalized networks, cascade inverses",
        ["renormalization group", "scaling", "fractal networks"],
        ["coarse-grain", "refine", "RG flow"],
        ["fixed points", "universality"],
        ["multigrid", "hierarchical inversion"]
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FIRE Θ (Wave / Root / Vector Potential)
    # ═══════════════════════════════════════════════════════════════════════════
    
    books[9] = Book(9, Pole.THETA, Lens.SQUARE,
        "Θ•Square: Vector Spaces",
        "Vector spaces, orthogonality, normed structure",
        ["ℂ^n", "Hilbert space", "inner product"],
        ["projection", "Gram-Schmidt", "QR"],
        ["Pythagorean theorem", "Cauchy-Schwarz"],
        ["orthogonalization", "SVD"]
    )
    
    books[10] = Book(10, Pole.THETA, Lens.FLOWER,
        "Θ•Flower: Phase Geometry",
        "Phase geometry, rotations, Fourier families",
        ["U(1)", "SO(n)", "phase space"],
        ["rotation", "DFT", "wavelet"],
        ["unitarity", "Parseval"],
        ["FFT", "phase unwrapping"]
    )
    
    books[11] = Book(11, Pole.THETA, Lens.CLOUD,
        "Θ•Cloud: Amplitude Distributions",
        "Amplitude distributions, uncertainty, inference-as-wave",
        ["quantum states", "Born rule", "density matrices"],
        ["measurement", "collapse", "superposition"],
        ["uncertainty principle", "no-cloning"],
        ["quantum inference", "tomography"]
    )
    
    books[12] = Book(12, Pole.THETA, Lens.FRACTAL,
        "Θ•Fractal: Wavelets",
        "Wavelets, multiresolution, recursive spectral decompositions",
        ["wavelet basis", "scaling function", "MRA"],
        ["DWT", "lifting", "filter bank"],
        ["vanishing moments", "regularity"],
        ["fast wavelet transform", "compression"]
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AIR Λ (Lattice / Square / Outcome)
    # ═══════════════════════════════════════════════════════════════════════════
    
    books[13] = Book(13, Pole.LAMBDA, Lens.SQUARE,
        "Λ•Square: Address Space",
        "Address-space, integers, bit-lattices, grids",
        ["ℤ^d", "{0,1}^n", "Hamming space"],
        ["XOR ⊕", "shift", "mask"],
        ["Manhattan/Hamming distance", "lattice structure"],
        ["hashing", "addressing", "search"]
    )
    
    books[14] = Book(14, Pole.LAMBDA, Lens.FLOWER,
        "Λ•Flower: Clockwork",
        "Cycles, modular clocks, finite group phase",
        ["ℤ_n", "roots of unity", "cyclic groups"],
        ["mod n", "CRT", "NTT"],
        ["order divides group size", "primitive roots"],
        ["modular exponentiation", "discrete log"]
    )
    
    books[15] = Book(15, Pole.LAMBDA, Lens.CLOUD,
        "Λ•Cloud: Discrete Probability",
        "Finite probability, entropy, inference on discrete sets",
        ["Δ^{n-1} simplex", "distributions", "entropy"],
        ["Bayes", "conditioning", "KL divergence"],
        ["Jensen's inequality", "data processing"],
        ["belief propagation", "message passing"]
    )
    
    books[16] = Book(16, Pole.LAMBDA, Lens.FRACTAL,
        "Λ•Fractal: Automata",
        "Automata, recursion, compression, self-similar computation",
        ["DFA/NFA/TM", "grammars", "Kolmogorov complexity"],
        ["transition δ", "rewrite", "compression"],
        ["Church-Turing thesis", "incompressibility"],
        ["parsing", "regex", "LZW"]
    )
    
    return books


# ═══════════════════════════════════════════════════════════════════════════════
# META-BOOKS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetaBook:
    """Meta-book that spans the 16-book crystal."""
    number: int  # 17-21
    title: str
    description: str
    scope: str


def create_meta_books() -> Dict[int, MetaBook]:
    """Create the 5 meta-books."""
    return {
        17: MetaBook(17, "Lens Operators",
            "Rotate/reflect/conjugate/dualize between lenses",
            "Square↔Flower↔Cloud↔Fractal transformations"),
        
        18: MetaBook(18, "Z-Discipline",
            "Zero-point, absolute zero, collapse/expand invariants",
            "Z* highways and typed zeros"),
        
        19: MetaBook(19, "Tunneling",
            "Z* highways between zero points",
            "Fast representation jumps between poles"),
        
        20: MetaBook(20, "Certificates & Ledgers",
            "Proof compression, correctness tags, audit trails",
            "Verification and RT stamps"),
        
        21: MetaBook(21, "Grand Unification Atlas",
            "Canonical problems solved by rotating through four poles",
            "Complete algorithm families via pole rotation")
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CRYSTAL TREATISE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CrystalTreatise:
    """
    The complete Crystal Treatise architecture.
    
    Title: THE FOURFOLD MATHEMATICAL UNIVERSE
    (Earth α • Water 𝔇 • Fire Θ • Air Λ)
    """
    books: Dict[int, Book] = field(default_factory=create_16_books)
    meta_books: Dict[int, MetaBook] = field(default_factory=create_meta_books)
    
    def get_book(self, pole: Pole, lens: Lens) -> Book:
        """Get book by pole and lens."""
        for book in self.books.values():
            if book.pole == pole and book.lens == lens:
                return book
        raise ValueError(f"No book for {pole}, {lens}")
    
    def get_book_by_number(self, n: int) -> Book:
        """Get book by number."""
        return self.books[n]
    
    def get_row(self, pole: Pole) -> List[Book]:
        """Get all books for a pole (row)."""
        return [b for b in self.books.values() if b.pole == pole]
    
    def get_column(self, lens: Lens) -> List[Book]:
        """Get all books for a lens (column)."""
        return [b for b in self.books.values() if b.lens == lens]
    
    def traverse_diagonal(self) -> List[Book]:
        """Traverse main diagonal (α•Square, 𝔇•Flower, Θ•Cloud, Λ•Fractal)."""
        return [
            self.get_book(Pole.ALPHA, Lens.SQUARE),
            self.get_book(Pole.D_STAR, Lens.FLOWER),
            self.get_book(Pole.THETA, Lens.CLOUD),
            self.get_book(Pole.LAMBDA, Lens.FRACTAL)
        ]
    
    @property
    def pole_summary(self) -> Dict[Pole, str]:
        """Summary of each pole."""
        return {
            Pole.ALPHA: "Earth: Mass, Add, Counting",
            Pole.D_STAR: "Water: Flow, Inverse, Rates",
            Pole.THETA: "Fire: Wave, Root, Vector Potential",
            Pole.LAMBDA: "Air: Lattice, Square, Outcome"
        }
    
    @property
    def lens_summary(self) -> Dict[Lens, str]:
        """Summary of each lens."""
        return {
            Lens.SQUARE: "Exact, discrete, normal form",
            Lens.FLOWER: "Transform, phase, symmetry",
            Lens.CLOUD: "Uncertainty, probability, calibration",
            Lens.FRACTAL: "Recursion, compression, self-reference"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TILE CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TileContent:
    """
    Content of a single tile (Book × Layer).
    
    Every tile contains Objects, Operators, Invariants, Algorithms.
    """
    coord: CoordinateHeader
    objects: List[str] = field(default_factory=list)
    operators: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    algorithms: List[str] = field(default_factory=list)
    
    def get_layer(self, layer: Layer) -> List[str]:
        """Get content for specific layer."""
        mapping = {
            Layer.OBJECTS: self.objects,
            Layer.OPERATORS: self.operators,
            Layer.INVARIANTS: self.invariants,
            Layer.ALGORITHMS: self.algorithms
        }
        return mapping[layer]


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CrystalPoleBridge:
    """
    Bridge between Crystal Treatise and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        CRYSTAL TREATISE ↔ FRAMEWORK
        
        16 Core Books = Pole × Lens (4×4 crystal)
        
        Poles ↔ Framework Poles:
          α (Earth) ↔ D-pole (discrete/exact)
          𝔇 (Water) ↔ C-pole (continuous/flow)
          Θ (Fire)  ↔ Σ-pole (stochastic/wave)
          Λ (Air)   ↔ Ψ-pole (hierarchical/lattice)
        
        Lenses ↔ Charts:
          Square  ↔ □ (exact normal form)
          Flower  ↔ ✿ (transform domain)
          Cloud   ↔ ☁ (uncertainty/calibration)
          Fractal ↔ ⟂ (recursive/seed)
        
        Coordinate: ⟨Pole, Lens, Layer, Depth⟩
        Layers: Objects, Operators, Invariants, Algorithms
        
        5 Meta-Books: Lens Operators, Z-Discipline, Tunneling,
                      Certificates, Grand Unification
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def crystal_treatise() -> CrystalTreatise:
    """Create crystal treatise."""
    return CrystalTreatise()


def coordinate_header(pole: Pole, lens: Lens, 
                      layer: Layer = Layer.OBJECTS,
                      depth: int = 0) -> CoordinateHeader:
    """Create coordinate header."""
    return CoordinateHeader(pole, lens, layer, depth)


def get_book(pole: Pole, lens: Lens) -> Book:
    """Get book by pole and lens."""
    return CrystalTreatise().get_book(pole, lens)


def list_books() -> List[str]:
    """List all 16 book titles."""
    treatise = CrystalTreatise()
    return [f"Book {n}: {b.title}" for n, b in treatise.books.items()]


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'Pole',
    'Lens',
    'Layer',
    
    # Coordinates
    'CoordinateHeader',
    
    # Books
    'Book',
    'MetaBook',
    
    # Treatise
    'CrystalTreatise',
    'TileContent',
    
    # Bridge
    'CrystalPoleBridge',
    
    # Functions
    'create_16_books',
    'create_meta_books',
    'crystal_treatise',
    'coordinate_header',
    'get_book',
    'list_books',
]

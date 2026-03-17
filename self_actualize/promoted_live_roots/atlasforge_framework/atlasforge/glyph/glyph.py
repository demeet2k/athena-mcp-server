"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       GLYPH COMPOSITE MODULE                                 ║
║                                                                              ║
║  16 Shape Compositions: Outer(Inner X)                                       ║
║                                                                              ║
║  Four Shapes:                                                                ║
║    ☐ (Square)   : Discretize, address, tile, quantize                        ║
║    ○ (Circle)   : Phase-lift, rotation, transport                            ║
║    △ (Triangle) : Mixture, simplex, probability                              ║
║    🌀 (Spiral)   : Recursion, zoom, renormalization                          ║
║                                                                              ║
║  16 Composites (4×4):                                                        ║
║    ☐☐, ☐○, ☐△, ☐🌀,  ○☐, ○○, ○△, ○🌀,                                        ║
║    △☐, △○, △△, △🌀,  🌀☐, 🌀○, 🌀△, 🌀🌀                                      ║
║                                                                              ║
║  Each composite has:                                                         ║
║    - Meaning: what the transformation does                                   ║
║    - Gate: canonical operator                                                ║
║    - Drift witness keys: boundary conditions for testing                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Union
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import hashlib


# ═══════════════════════════════════════════════════════════════════════════════
# GLYPH TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class Glyph(Enum):
    """The four fundamental glyphs/shapes."""
    SQUARE = "☐"     # Discretize, address, tile
    CIRCLE = "○"     # Phase-lift, rotation, transport
    TRIANGLE = "△"   # Mixture, simplex, probability
    SPIRAL = "🌀"    # Recursion, zoom, renormalization


@dataclass
class GlyphProperties:
    """Properties of a glyph."""
    glyph: Glyph
    meaning: str
    gate: str
    domain: str
    
    @classmethod
    def square(cls) -> 'GlyphProperties':
        return cls(Glyph.SQUARE, 
                   "Discretize/address/tile/quantize",
                   "Rep/NF/ID encoding",
                   "Lattice, discrete addresses")
    
    @classmethod
    def circle(cls) -> 'GlyphProperties':
        return cls(Glyph.CIRCLE,
                   "Phase-lift/rotation/transport",
                   "Fourier gate, gauge fix",
                   "Phase space, U(1)")
    
    @classmethod
    def triangle(cls) -> 'GlyphProperties':
        return cls(Glyph.TRIANGLE,
                   "Mixture/simplex/probability",
                   "Barycentric, entropy",
                   "Probability simplex")
    
    @classmethod
    def spiral(cls) -> 'GlyphProperties':
        return cls(Glyph.SPIRAL,
                   "Recursion/zoom/renormalization",
                   "RG flow, ASCEND",
                   "Scale hierarchy")


# ═══════════════════════════════════════════════════════════════════════════════
# GLYPH COMPOSITE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GlyphComposite:
    """
    Glyph composite: Outer(Inner X).
    
    16 possible compositions from 4×4.
    """
    outer: Glyph
    inner: Glyph
    meaning: str
    gate: str
    drift_witness_keys: List[str]
    
    @property
    def symbol(self) -> str:
        """Composite symbol."""
        return f"{self.outer.value}({self.inner.value}X)"
    
    @property
    def short_name(self) -> str:
        """Short name like 'square_circle'."""
        return f"{self.outer.name.lower()}_{self.inner.name.lower()}"


# ═══════════════════════════════════════════════════════════════════════════════
# THE 16 COMPOSITES
# ═══════════════════════════════════════════════════════════════════════════════

def get_all_composites() -> Dict[Tuple[Glyph, Glyph], GlyphComposite]:
    """Get all 16 glyph composites."""
    
    composites = {}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OUTER = SQUARE (discretize)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # ☐(☐X) - square-squared: canonical normal form
    composites[(Glyph.SQUARE, Glyph.SQUARE)] = GlyphComposite(
        Glyph.SQUARE, Glyph.SQUARE,
        "Canonical normal form / ID stabilization",
        "Rep / NF / ID encoding",
        ["tie cases (equal-cost reps)", "hash instability"]
    )
    
    # ☐(○X) - circle-squared: quantize phase
    composites[(Glyph.SQUARE, Glyph.CIRCLE)] = GlyphComposite(
        Glyph.SQUARE, Glyph.CIRCLE,
        "Turn phase/rotation into lattice address (sampling/alias control)",
        "Fourier→sample / phase→index",
        ["branch cuts (phase near 0 vs 2π)", "Nyquist/alias boundary", "tie-break bins"]
    )
    
    # ☐(△X) - triangle-squared: quantize mixture
    composites[(Glyph.SQUARE, Glyph.TRIANGLE)] = GlyphComposite(
        Glyph.SQUARE, Glyph.TRIANGLE,
        "Map simplex weights to discrete bins/tiles",
        "simplex→lattice quantizer",
        ["simplex faces/edges", "equal mixtures", "threshold crossings"]
    )
    
    # ☐(🌀X) - spiral-squared: flatten recursion
    composites[(Glyph.SQUARE, Glyph.SPIRAL)] = GlyphComposite(
        Glyph.SQUARE, Glyph.SPIRAL,
        "Collapse multiscale object into discrete address (atlas-of-atlases ID)",
        "compress recursion tree → seed hash / canonical code",
        ["recursion fixed points", "depth sensitivity", "non-unique minimal generators"]
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OUTER = CIRCLE (phase-lift)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # ○(☐X) - square-circled: phase lift of lattice
    composites[(Glyph.CIRCLE, Glyph.SQUARE)] = GlyphComposite(
        Glyph.CIRCLE, Glyph.SQUARE,
        "Interpret discrete structure as phase/transport (DFT on lattice)",
        "Fourier gate",
        ["lattice symmetries", "ambiguous orientation", "basis choice"]
    )
    
    # ○(○X) - circle-circled: normalize phase
    composites[(Glyph.CIRCLE, Glyph.CIRCLE)] = GlyphComposite(
        Glyph.CIRCLE, Glyph.CIRCLE,
        "Normalize phase conventions; compute holonomy/transport NF",
        "gauge fix / connection normalization",
        ["loop around branch cut", "gauge choice non-equivariance"]
    )
    
    # ○(△X) - triangle-circled: mixture → phase
    composites[(Glyph.CIRCLE, Glyph.TRIANGLE)] = GlyphComposite(
        Glyph.CIRCLE, Glyph.TRIANGLE,
        "Map mixtures into phase objects (characteristic function)",
        "characteristic function / Fourier of distribution",
        ["mixtures with cancellation", "entropy extremes", "discontinuous phase unwrap"]
    )
    
    # ○(🌀X) - spiral-circled: phase across scales
    composites[(Glyph.CIRCLE, Glyph.SPIRAL)] = GlyphComposite(
        Glyph.CIRCLE, Glyph.SPIRAL,
        "Scale-dependent phase ladder (multi-Fourier / RG phase)",
        "phase of scaling exponents / holonomy across zoom",
        ["scale transitions", "resonance bands", "depth-induced gauge shifts"]
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OUTER = TRIANGLE (mixture/simplex)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # △(☐X) - square-triangled: address → mixture
    composites[(Glyph.TRIANGLE, Glyph.SQUARE)] = GlyphComposite(
        Glyph.TRIANGLE, Glyph.SQUARE,
        "View discrete addresses as distribution (histogram/simplex embedding)",
        "lattice→simplex map (counts→weights)",
        ["sparse support", "normalization sensitivity", "tie-breaking"]
    )
    
    # △(○X) - circle-triangled: phase → mixture
    composites[(Glyph.TRIANGLE, Glyph.CIRCLE)] = GlyphComposite(
        Glyph.TRIANGLE, Glyph.CIRCLE,
        "Turn phase/transport into mixture weights (spectral density)",
        "magnitude/energy extraction",
        ["phase-only info losing sign", "near-zero amplitude", "conjugation symmetry"]
    )
    
    # △(△X) - triangle-triangled: mixture canonization
    composites[(Glyph.TRIANGLE, Glyph.TRIANGLE)] = GlyphComposite(
        Glyph.TRIANGLE, Glyph.TRIANGLE,
        "Mixture canonization (simplex NF, entropy NF)",
        "barycentric normalization / entropy regularization",
        ["simplex-face collisions", "multiple equivalent barycentric coords"]
    )
    
    # △(🌀X) - spiral-triangled: mixtures across scales
    composites[(Glyph.TRIANGLE, Glyph.SPIRAL)] = GlyphComposite(
        Glyph.TRIANGLE, Glyph.SPIRAL,
        "Multiscale distributions (RG flow of probabilities)",
        "coarse-grain / refine of simplex coordinates",
        ["scale where bins merge/split", "critical points", "depth-dependent entropy"]
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OUTER = SPIRAL (recursion/zoom)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # 🌀(☐X) - square-spiraled: recursive tiling
    composites[(Glyph.SPIRAL, Glyph.SQUARE)] = GlyphComposite(
        Glyph.SPIRAL, Glyph.SQUARE,
        "Treat lattice as generator of finer lattices (atlas→atlas-of-atlases)",
        "zoom-in expansion of address system",
        ["non-self-similar regions", "boundary effects", "generator ambiguity"]
    )
    
    # 🌀(○X) - circle-spiraled: recursive phase
    composites[(Glyph.SPIRAL, Glyph.CIRCLE)] = GlyphComposite(
        Glyph.SPIRAL, Glyph.CIRCLE,
        "Phase recursion / holonomy across scales",
        "repeated transport composition + normalization",
        ["accumulating branch-cut choices", "loop non-closure", "gauge drift"]
    )
    
    # 🌀(△X) - triangle-spiraled: recursive mixtures
    composites[(Glyph.SPIRAL, Glyph.TRIANGLE)] = GlyphComposite(
        Glyph.SPIRAL, Glyph.TRIANGLE,
        "Mixture recursion (fractal distributions, iterative blending)",
        "iterate mixture operator + renormalize",
        ["contraction vs explosion", "fixed points / limit cycles", "initialization dependence"]
    )
    
    # 🌀(🌀X) - spiral-spiraled: ASCEND-layer
    composites[(Glyph.SPIRAL, Glyph.SPIRAL)] = GlyphComposite(
        Glyph.SPIRAL, Glyph.SPIRAL,
        "Recursion on recursion = ASCEND-layer behavior (meta-laws)",
        "build law-of-laws; measure equivariance defect",
        ["ASCEND equivariance defect", "meta-canonizer order changes", "hash-of-hash instability"]
    )
    
    return composites


# ═══════════════════════════════════════════════════════════════════════════════
# DRIFT TEST
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DriftTest:
    """
    Drift test for glyph composites.
    
    ρ_{S,T} = Norm(κ(S(TX)) - κ(T(SX)))
    
    Tests commutativity defect between two shapes.
    """
    shape_s: Glyph
    shape_t: Glyph
    
    def commutator_residue(self, apply_s: Callable, apply_t: Callable,
                           canonizer: Callable,
                           x: Any) -> float:
        """
        Compute commutator residue.
        
        ρ_{S,T}(X) = ||κ(S(TX)) - κ(T(SX))||
        """
        # S(T(X))
        st_x = apply_s(apply_t(x))
        kappa_st = canonizer(st_x)
        
        # T(S(X))
        ts_x = apply_t(apply_s(x))
        kappa_ts = canonizer(ts_x)
        
        # Compute norm of difference
        if isinstance(kappa_st, np.ndarray):
            return float(np.linalg.norm(kappa_st - kappa_ts))
        else:
            return abs(kappa_st - kappa_ts)


@dataclass
class TriangleHolonomy:
    """
    Triangle/face holonomy for triple-glyph drift test.
    
    ρ_{A;B,C}(X) = Norm(κ(A(B(CX))) - κ(A(C(BX))))
    
    Tests swap residue with first shape fixed.
    """
    shape_a: Glyph
    shape_b: Glyph
    shape_c: Glyph
    
    def face_holonomy(self, apply_a: Callable, apply_b: Callable,
                      apply_c: Callable, canonizer: Callable,
                      x: Any) -> float:
        """Compute triangle swap residue."""
        # A(B(C(X)))
        abc_x = apply_a(apply_b(apply_c(x)))
        kappa_abc = canonizer(abc_x)
        
        # A(C(B(X)))
        acb_x = apply_a(apply_c(apply_b(x)))
        kappa_acb = canonizer(acb_x)
        
        if isinstance(kappa_abc, np.ndarray):
            return float(np.linalg.norm(kappa_abc - kappa_acb))
        else:
            return abs(kappa_abc - kappa_acb)


# ═══════════════════════════════════════════════════════════════════════════════
# Z0 LEDGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Z0Ledger:
    """
    Z0 record format for glyph-composite operations.
    
    Z0 = (status, ρ, w, seed, hash, sig)
    """
    status: str                    # ok, warning, error
    rho: float                     # Drift residue
    witness_keys: List[str]        # Minimal witness set
    seed: Any                      # Repair/tunnel seed
    content_hash: str              # Hash of computation
    signature: str                 # Orbit/stabilizer signature
    
    @classmethod
    def create(cls, status: str, rho: float,
               witnesses: List[str], seed: Any = None) -> 'Z0Ledger':
        """Create Z0 ledger entry."""
        data = f"{status}|{rho}|{witnesses}|{seed}"
        h = hashlib.sha256(data.encode()).hexdigest()[:16]
        return cls(status, rho, witnesses, seed, h, "")
    
    def is_stable(self, tolerance: float = 1e-6) -> bool:
        """Check if drift is within tolerance."""
        return self.rho < tolerance


# ═══════════════════════════════════════════════════════════════════════════════
# GLYPH ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GlyphEngine:
    """
    Engine for evaluating glyph expressions.
    
    Expands through Z*, evaluates composite, runs drift checks,
    emits Z0 ledger.
    """
    composites: Dict[Tuple[Glyph, Glyph], GlyphComposite] = field(
        default_factory=get_all_composites
    )
    
    def get_composite(self, outer: Glyph, inner: Glyph) -> GlyphComposite:
        """Get composite by glyphs."""
        return self.composites[(outer, inner)]
    
    def evaluate(self, outer: Glyph, inner: Glyph,
                 x: Any,
                 apply_outer: Callable,
                 apply_inner: Callable,
                 canonizer: Callable = lambda x: x) -> Tuple[Any, Z0Ledger]:
        """
        Evaluate glyph composite.
        
        Returns (result, Z0 ledger).
        """
        composite = self.get_composite(outer, inner)
        
        # Apply composite: Outer(Inner(X))
        inner_result = apply_inner(x)
        result = apply_outer(inner_result)
        canonical = canonizer(result)
        
        # Run drift test (compare with Inner(Outer(X)))
        drift = DriftTest(outer, inner)
        rho = drift.commutator_residue(
            apply_outer, apply_inner, canonizer, x
        )
        
        # Create Z0 ledger
        status = "ok" if rho < 1e-6 else ("warning" if rho < 0.1 else "error")
        ledger = Z0Ledger.create(
            status, rho,
            composite.drift_witness_keys,
            canonical
        )
        
        return result, ledger
    
    def list_composites(self) -> List[str]:
        """List all composite symbols."""
        return [c.symbol for c in self.composites.values()]


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GlyphPoleBridge:
    """
    Bridge between Glyph Composites and four-pole framework.
    """
    
    @staticmethod
    def glyph_chart_map() -> Dict[Glyph, str]:
        return {
            Glyph.SQUARE: "□ Square chart (D-pole)",
            Glyph.CIRCLE: "✿ Flower chart (C-pole)",
            Glyph.TRIANGLE: "☁ Cloud chart (Σ-pole)",
            Glyph.SPIRAL: "⟂ Fractal chart (Ψ-pole)"
        }
    
    @staticmethod
    def integration() -> str:
        return """
        GLYPH COMPOSITES ↔ FRAMEWORK
        
        Glyph ↔ Chart:
          ☐ Square   ↔ □ (D-pole: discrete/exact)
          ○ Circle   ↔ ✿ (C-pole: continuous/phase)
          △ Triangle ↔ ☁ (Σ-pole: stochastic/mixture)
          🌀 Spiral   ↔ ⟂ (Ψ-pole: recursive/hierarchical)
        
        16 Composites = 4×4 grid of transformations
        
        Drift Test: ρ_{S,T} = ||κ(S(TX)) - κ(T(SX))||
        Face Holonomy: ρ_{A;B,C} = ||κ(A(B(CX))) - κ(A(C(BX)))||
        
        Z0 Ledger: (status, ρ, witnesses, seed, hash, sig)
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def glyph_properties(g: Glyph) -> GlyphProperties:
    """Get properties for glyph."""
    mapping = {
        Glyph.SQUARE: GlyphProperties.square(),
        Glyph.CIRCLE: GlyphProperties.circle(),
        Glyph.TRIANGLE: GlyphProperties.triangle(),
        Glyph.SPIRAL: GlyphProperties.spiral()
    }
    return mapping[g]


def glyph_composite(outer: Glyph, inner: Glyph) -> GlyphComposite:
    """Get glyph composite."""
    return get_all_composites()[(outer, inner)]


def glyph_engine() -> GlyphEngine:
    """Create glyph engine."""
    return GlyphEngine()


def drift_test(s: Glyph, t: Glyph) -> DriftTest:
    """Create drift test."""
    return DriftTest(s, t)


def z0_ledger(status: str, rho: float, 
              witnesses: List[str]) -> Z0Ledger:
    """Create Z0 ledger."""
    return Z0Ledger.create(status, rho, witnesses)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'Glyph',
    
    # Properties
    'GlyphProperties',
    'GlyphComposite',
    
    # Drift Testing
    'DriftTest',
    'TriangleHolonomy',
    
    # Ledger
    'Z0Ledger',
    
    # Engine
    'GlyphEngine',
    
    # Bridge
    'GlyphPoleBridge',
    
    # Functions
    'get_all_composites',
    'glyph_properties',
    'glyph_composite',
    'glyph_engine',
    'drift_test',
    'z0_ledger',
]

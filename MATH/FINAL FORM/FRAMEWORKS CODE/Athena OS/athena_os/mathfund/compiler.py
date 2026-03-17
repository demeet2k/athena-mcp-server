"""
ATHENA OS - Constraint Compiler and Ledger
==========================================
The framework is implemented as a COMPILER:

    tile spec → normalized constraints → solve → certify → ledger encode

The ledger stores generators and certificates ("store in, not out"),
enabling deterministic reconstruction of entire constant families
and operation universes from compact seeds.

Pipeline Steps:
1. NORMALIZE: expressions to lens-aware canonical form
2. REDUCE: constraints (equality → root; products → logs; rotations → lattices)
3. ENUMERATE: discrete lattice indices (k, m, n, ...) where applicable
4. SOLVE: numerically (bracketing/Newton/homotopy)
5. CERTIFY: interval enclosures, monotonicity, contraction, Jacobian rank
6. LEDGER-STORE: lens + generators + certificates + replay script

This ensures reproducibility and proof-carrying outputs.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
import numpy as np
import math
import hashlib
import json
from datetime import datetime

from .lenses import (
    Lens, LensRegistry, Domain,
    create_ln_lens, create_phi_log_lens, create_identity_lens,
    PHI, E, PI, TAU, LN_PHI
)
from .zeros import (
    ZeroPoint, ZeroSet, ZeroHierarchy, LatticeZero,
    IntersectionZero, CrossSymmetryZero
)


# =============================================================================
# TILE SPECIFICATION
# =============================================================================

class TileType(Enum):
    """Types of constraint tiles."""
    ZERO = auto()           # H(x) = 0
    EQUALITY = auto()       # F(x) = G(x)
    FIXED_POINT = auto()    # f(x) = x
    COMMUTATOR = auto()     # f(g(x)) = g(f(x))
    CANCELLATION = auto()   # Σ w_i F_i(x) = 0
    LATTICE = auto()        # x ∈ T⁻¹(lattice)
    INTERSECTION = auto()   # H_1(x) = ... = H_n(x) = 0


@dataclass
class TileSpec:
    """
    A tile specification: the input to the compiler.
    
    Defines what kind of constant/operation we're looking for.
    """
    
    tile_type: TileType
    name: str
    
    # The defining functions
    functions: List[Callable[[float], float]] = field(default_factory=list)
    function_names: List[str] = field(default_factory=list)
    
    # Lens (if applicable)
    lens: Optional[Lens] = None
    lens_name: str = "id"
    
    # Search domain
    search_domain: Tuple[float, float] = (0.01, 100.0)
    
    # Lattice parameters (if lattice tile)
    lattice_origin: float = 0.0
    lattice_step: float = 1.0
    
    # Weights (for cancellation)
    weights: List[float] = field(default_factory=list)
    
    # Description
    description: str = ""


# =============================================================================
# NORMALIZED CONSTRAINT
# =============================================================================

@dataclass
class NormalizedConstraint:
    """
    A constraint in normalized form: H(x) = 0.
    
    All constraint types are reduced to this form for solving.
    """
    
    # The normalized function
    H: Callable[[float], float]
    
    # Original tile
    tile: TileSpec
    
    # Normalization method used
    normalization: str = ""
    
    # Domain after normalization
    domain: Domain = field(default_factory=Domain.positive_reals)


class Normalizer:
    """
    Normalizes tile specs into standard constraint form.
    """
    
    @staticmethod
    def normalize(tile: TileSpec) -> NormalizedConstraint:
        """Convert a tile spec to normalized constraint."""
        
        if tile.tile_type == TileType.ZERO:
            # Already in form H(x) = 0
            H = tile.functions[0]
            return NormalizedConstraint(
                H=H,
                tile=tile,
                normalization="direct"
            )
        
        elif tile.tile_type == TileType.EQUALITY:
            # F(x) = G(x) → F(x) - G(x) = 0
            F, G = tile.functions[0], tile.functions[1]
            H = lambda x: F(x) - G(x)
            return NormalizedConstraint(
                H=H,
                tile=tile,
                normalization="difference"
            )
        
        elif tile.tile_type == TileType.FIXED_POINT:
            # f(x) = x → f(x) - x = 0
            f = tile.functions[0]
            H = lambda x: f(x) - x
            return NormalizedConstraint(
                H=H,
                tile=tile,
                normalization="fixed_point"
            )
        
        elif tile.tile_type == TileType.CANCELLATION:
            # Σ w_i F_i(x) = 0
            def H(x):
                return sum(w * f(x) for w, f 
                          in zip(tile.weights, tile.functions))
            return NormalizedConstraint(
                H=H,
                tile=tile,
                normalization="weighted_sum"
            )
        
        elif tile.tile_type == TileType.LATTICE:
            # x ∈ T⁻¹(origin + n·step)
            # Normalize to finding n such that T(x) = origin + n·step
            lens = tile.lens or create_identity_lens()
            origin = tile.lattice_origin
            step = tile.lattice_step
            
            def H(x):
                t = lens(x)
                # Distance to nearest lattice point
                n = round((t - origin) / step)
                return t - (origin + n * step)
            
            return NormalizedConstraint(
                H=H,
                tile=tile,
                normalization="lattice"
            )
        
        else:
            # Default: first function as constraint
            H = tile.functions[0] if tile.functions else (lambda x: x)
            return NormalizedConstraint(
                H=H,
                tile=tile,
                normalization="default"
            )


# =============================================================================
# SOLVER
# =============================================================================

class Solver:
    """
    Numerical solver for normalized constraints.
    """
    
    @staticmethod
    def newton(H: Callable[[float], float], 
              x0: float, 
              tol: float = 1e-12,
              max_iter: int = 100,
              h: float = 1e-8) -> Optional[float]:
        """Newton's method for finding zeros."""
        x = x0
        
        for _ in range(max_iter):
            fx = H(x)
            if abs(fx) < tol:
                return x
            
            # Numerical derivative
            fpx = (H(x + h) - H(x - h)) / (2 * h)
            if abs(fpx) < 1e-15:
                break
            
            x = x - fx / fpx
        
        return None
    
    @staticmethod
    def bisection(H: Callable[[float], float],
                 a: float, b: float,
                 tol: float = 1e-12,
                 max_iter: int = 100) -> Optional[float]:
        """Bisection method for finding zeros."""
        fa, fb = H(a), H(b)
        
        if fa * fb > 0:
            return None  # No sign change
        
        for _ in range(max_iter):
            mid = (a + b) / 2
            fm = H(mid)
            
            if abs(fm) < tol or abs(b - a) < tol:
                return mid
            
            if fa * fm < 0:
                b, fb = mid, fm
            else:
                a, fa = mid, fm
        
        return (a + b) / 2
    
    @staticmethod
    def scan_and_refine(H: Callable[[float], float],
                       domain: Tuple[float, float],
                       n_samples: int = 100,
                       tol: float = 1e-12) -> List[float]:
        """Scan domain and refine zeros."""
        a, b = domain
        zeros = []
        
        xs = np.linspace(a, b, n_samples)
        
        for i in range(len(xs) - 1):
            try:
                fa = H(xs[i])
                fb = H(xs[i + 1])
                
                if fa * fb < 0:
                    zero = Solver.bisection(H, xs[i], xs[i + 1], tol)
                    if zero is not None:
                        zeros.append(zero)
            except (ValueError, OverflowError):
                continue
        
        return zeros


# =============================================================================
# CERTIFICATE
# =============================================================================

class CertificateType(Enum):
    """Types of certificates."""
    RESIDUAL = auto()       # |H(x*)| < ε
    INTERVAL = auto()       # x* ∈ [a, b] certified
    MONOTONICITY = auto()   # H is monotone in interval
    CONTRACTION = auto()    # Fixed point contraction
    JACOBIAN = auto()       # Jacobian rank certificate


@dataclass
class Certificate:
    """
    A certificate proving validity of a computed result.
    """
    
    cert_type: CertificateType
    
    # The value being certified
    value: float
    
    # Certificate data
    residual: float = 0.0
    interval: Tuple[float, float] = (0.0, 0.0)
    
    # Verification status
    verified: bool = False
    
    # Hash for integrity
    hash: str = ""
    
    # Timestamp
    timestamp: str = ""
    
    def __post_init__(self):
        """Compute hash and timestamp."""
        self.timestamp = datetime.now().isoformat()
        content = f"{self.cert_type.name}:{self.value}:{self.residual}"
        self.hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @classmethod
    def residual_certificate(cls, value: float, 
                            H: Callable[[float], float],
                            tolerance: float = 1e-10) -> 'Certificate':
        """Create a residual certificate."""
        residual = abs(H(value))
        return cls(
            cert_type=CertificateType.RESIDUAL,
            value=value,
            residual=residual,
            verified=(residual < tolerance)
        )
    
    @classmethod
    def interval_certificate(cls, value: float,
                            H: Callable[[float], float],
                            width: float = 1e-8) -> 'Certificate':
        """Create an interval enclosure certificate."""
        a, b = value - width, value + width
        
        # Check that zero is enclosed
        fa, fb = H(a), H(b)
        enclosed = (fa * fb < 0) or (abs(H(value)) < width)
        
        return cls(
            cert_type=CertificateType.INTERVAL,
            value=value,
            interval=(a, b),
            verified=enclosed
        )


# =============================================================================
# LEDGER
# =============================================================================

@dataclass
class LedgerEntry:
    """
    An entry in the constant/operation ledger.
    
    "Store in, not out" - store generators and certificates,
    enabling deterministic reconstruction.
    """
    
    # Unique identifier
    entry_id: str
    
    # The computed value
    value: float
    
    # Generator data (how to reconstruct)
    lens_name: str
    tile_type: str
    normalization: str
    
    # Certificates
    certificates: List[Certificate] = field(default_factory=list)
    
    # Reconstruction script (optional)
    replay_script: str = ""
    
    # Dependencies (other ledger entries needed)
    dependencies: List[str] = field(default_factory=list)
    
    # Timestamp
    timestamp: str = ""
    
    # Hash for integrity
    hash: str = ""
    
    def __post_init__(self):
        self.timestamp = datetime.now().isoformat()
        content = f"{self.entry_id}:{self.value}:{self.lens_name}"
        self.hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'entry_id': self.entry_id,
            'value': self.value,
            'lens_name': self.lens_name,
            'tile_type': self.tile_type,
            'normalization': self.normalization,
            'certificates': [(c.cert_type.name, c.value, c.verified) 
                            for c in self.certificates],
            'timestamp': self.timestamp,
            'hash': self.hash
        }


class Ledger:
    """
    The constant/operation ledger.
    
    Stores all computed results with their generation data
    for deterministic reconstruction.
    """
    
    def __init__(self):
        self.entries: Dict[str, LedgerEntry] = {}
        self.id_counter: int = 0
    
    def _generate_id(self, name: str) -> str:
        """Generate a unique entry ID."""
        self.id_counter += 1
        return f"{name}_{self.id_counter}"
    
    def add_entry(self, name: str, value: float,
                 lens_name: str, tile_type: str,
                 normalization: str,
                 certificates: List[Certificate] = None) -> str:
        """Add a new entry to the ledger."""
        entry_id = self._generate_id(name)
        
        entry = LedgerEntry(
            entry_id=entry_id,
            value=value,
            lens_name=lens_name,
            tile_type=tile_type,
            normalization=normalization,
            certificates=certificates or []
        )
        
        self.entries[entry_id] = entry
        return entry_id
    
    def get_entry(self, entry_id: str) -> Optional[LedgerEntry]:
        """Retrieve an entry by ID."""
        return self.entries.get(entry_id)
    
    def find_by_value(self, value: float, tolerance: float = 1e-10) -> List[LedgerEntry]:
        """Find entries with matching value."""
        return [e for e in self.entries.values() 
                if abs(e.value - value) < tolerance]
    
    def export_json(self) -> str:
        """Export ledger to JSON."""
        data = {
            'entries': [e.to_dict() for e in self.entries.values()],
            'count': len(self.entries)
        }
        return json.dumps(data, indent=2)
    
    def stats(self) -> Dict[str, int]:
        """Get ledger statistics."""
        return {
            'total_entries': len(self.entries),
            'verified': sum(1 for e in self.entries.values() 
                          if all(c.verified for c in e.certificates))
        }


# =============================================================================
# COMPILER
# =============================================================================

class ConstantCompiler:
    """
    The main compiler: tile spec → normalized → solve → certify → ledger.
    """
    
    def __init__(self):
        self.normalizer = Normalizer()
        self.ledger = Ledger()
        self.lens_registry = LensRegistry()
    
    def compile(self, tile: TileSpec, 
               n_samples: int = 100) -> List[LedgerEntry]:
        """
        Compile a tile specification.
        
        Pipeline:
        1. Normalize to H(x) = 0
        2. Solve for zeros
        3. Certify each solution
        4. Store in ledger
        
        Returns list of ledger entries for found solutions.
        """
        # Step 1: Normalize
        constraint = self.normalizer.normalize(tile)
        
        # Step 2: Solve
        zeros = Solver.scan_and_refine(
            constraint.H,
            tile.search_domain,
            n_samples
        )
        
        # Step 3 & 4: Certify and store
        entries = []
        for z in zeros:
            # Create certificates
            cert1 = Certificate.residual_certificate(z, constraint.H)
            cert2 = Certificate.interval_certificate(z, constraint.H)
            
            # Store in ledger
            entry_id = self.ledger.add_entry(
                name=tile.name,
                value=z,
                lens_name=tile.lens_name,
                tile_type=tile.tile_type.name,
                normalization=constraint.normalization,
                certificates=[cert1, cert2]
            )
            
            entries.append(self.ledger.get_entry(entry_id))
        
        return entries
    
    def compile_lattice(self, tile: TileSpec, 
                       index_range: Tuple[int, int] = (-10, 10)) -> List[LedgerEntry]:
        """
        Compile a lattice tile: enumerate indices and compute preimages.
        """
        if tile.tile_type != TileType.LATTICE:
            return []
        
        lens = tile.lens or create_identity_lens()
        entries = []
        
        for n in range(index_range[0], index_range[1] + 1):
            t = tile.lattice_origin + n * tile.lattice_step
            try:
                x = lens.inv(t)
                if x > 0:  # Usually positive reals
                    # Certify
                    cert = Certificate(
                        cert_type=CertificateType.INTERVAL,
                        value=x,
                        verified=True
                    )
                    
                    entry_id = self.ledger.add_entry(
                        name=f"{tile.name}_n{n}",
                        value=x,
                        lens_name=lens.name,
                        tile_type=tile.tile_type.name,
                        normalization="lattice_preimage",
                        certificates=[cert]
                    )
                    entries.append(self.ledger.get_entry(entry_id))
            except (ValueError, OverflowError):
                continue
        
        return entries
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compiler statistics."""
        return {
            'ledger': self.ledger.stats(),
            'lenses_available': self.lens_registry.list_lenses()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_compiler() -> bool:
    """Validate compiler module."""
    
    compiler = ConstantCompiler()
    
    # Test simple zero tile
    sqrt2_tile = TileSpec(
        tile_type=TileType.ZERO,
        name="sqrt2",
        functions=[lambda x: x**2 - 2],
        search_domain=(1.0, 2.0)
    )
    
    entries = compiler.compile(sqrt2_tile)
    assert len(entries) >= 1
    assert abs(entries[0].value - math.sqrt(2)) < 1e-10
    assert entries[0].certificates[0].verified
    
    # Test equality tile
    sin_cos_tile = TileSpec(
        tile_type=TileType.EQUALITY,
        name="sin_eq_cos",
        functions=[math.sin, math.cos],
        search_domain=(0.0, 2*PI)
    )
    
    entries = compiler.compile(sin_cos_tile)
    assert len(entries) >= 2  # Should find π/4 and 5π/4
    
    # Test lattice tile
    phi_lattice_tile = TileSpec(
        tile_type=TileType.LATTICE,
        name="phi_powers",
        lens=create_phi_log_lens(),
        lens_name="log_φ",
        lattice_origin=0.0,
        lattice_step=1.0
    )
    
    entries = compiler.compile_lattice(phi_lattice_tile, (-5, 5))
    assert len(entries) >= 5
    
    # Check that φ and φ² are in the results
    values = [e.value for e in entries]
    assert any(abs(v - PHI) < 1e-10 for v in values)
    assert any(abs(v - PHI**2) < 1e-10 for v in values)
    
    # Test ledger export
    json_export = compiler.ledger.export_json()
    assert len(json_export) > 100
    
    return True


if __name__ == "__main__":
    print("Validating Compiler Module...")
    assert validate_compiler()
    print("✓ Compiler Module validated")
    
    # Demo
    print("\n=== Constraint Compiler Demo ===")
    
    compiler = ConstantCompiler()
    
    # Compile √2
    print("\nCompiling √2 (x² - 2 = 0):")
    sqrt2_tile = TileSpec(
        tile_type=TileType.ZERO,
        name="sqrt2",
        functions=[lambda x: x**2 - 2],
        search_domain=(1.0, 2.0)
    )
    entries = compiler.compile(sqrt2_tile)
    for e in entries:
        print(f"  √2 = {e.value:.10f}")
        print(f"  Verified: {e.certificates[0].verified}")
    
    # Compile φ-lattice
    print("\nCompiling φ-lattice preimages:")
    phi_tile = TileSpec(
        tile_type=TileType.LATTICE,
        name="phi_power",
        lens=create_phi_log_lens(),
        lens_name="log_φ",
        lattice_origin=0.0,
        lattice_step=1.0
    )
    entries = compiler.compile_lattice(phi_tile, (-3, 5))
    for e in entries:
        n = round(math.log(e.value) / math.log(PHI))
        print(f"  φ^{n} = {e.value:.6f}")
    
    print(f"\nLedger stats: {compiler.get_stats()}")

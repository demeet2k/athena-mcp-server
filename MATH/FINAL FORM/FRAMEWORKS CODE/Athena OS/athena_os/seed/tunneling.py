"""
ATHENA OS - Crystal Tunneling Mechanics
=======================================
The 90° rotation mechanism for traversing between Crystal poles.

When a trajectory in the Aether Crystal approaches a wall in the
Anti-Aether Crystal, it rotates into the Shadow Axis:

Tunneling Correspondence:
- Aether ←→ Anti-Aether (Horizontal axis: Magnitude)
- Inner Shadow ←→ Outer Shadow (Vertical axis: Structure)

The system can tunnel through any barrier by rotating through
the appropriate shadow dimension.

Shadow Pole Encodings:
- Inner Shadow (log): Information-theoretic encoding (bit-depth)
- Outer Shadow (exp): Boundary conditions (saturation limits)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from .lattice import (
    MetaPole, Constant, Sector, Element, Level,
    CrystalAddress, CrystalExpression, CrystalLattice
)


# =============================================================================
# TUNNELING DIRECTIONS
# =============================================================================

class TunnelDirection(IntEnum):
    """Direction of tunneling in the Crystal."""
    HORIZONTAL = 0     # Aether ↔ Anti-Aether
    VERTICAL = 1       # Inner ↔ Outer Shadow
    CLOCKWISE = 2      # A → Ā → Out → In → A
    COUNTER_CLOCKWISE = 3  # A → In → Out → Ā → A


@dataclass
class TunnelPath:
    """A path through the Crystal via tunneling."""
    source: CrystalAddress
    target: CrystalAddress
    direction: TunnelDirection
    rotation_angle: float  # in degrees
    barrier_crossed: str   # Description of what was tunneled through
    kappa_cost: float     # Energy cost of tunneling
    
    @property
    def is_horizontal(self) -> bool:
        return self.direction == TunnelDirection.HORIZONTAL
    
    @property
    def is_vertical(self) -> bool:
        return self.direction == TunnelDirection.VERTICAL


# =============================================================================
# SHADOW POLE ENCODINGS
# =============================================================================

@dataclass
class ShadowEncoding:
    """
    Shadow pole encoding for a Crystal expression.
    
    Every Aether/Anti-Aether expression has:
    - Inner Shadow: its information-theoretic bit-depth
    - Outer Shadow: its boundary/saturation condition
    """
    address: CrystalAddress
    
    # Inner Shadow (Logarithmic Code)
    inner_name: str
    inner_description: str
    inner_formula: str  # The log-encoding
    bit_depth: float    # Information content in bits
    
    # Outer Shadow (Exponential Shell)
    outer_name: str
    outer_description: str
    outer_formula: str  # The saturation condition
    horizon: float      # The boundary value


# Inner Shadow encodings for π-constant
PI_INNER_SHADOWS: Dict[Tuple[Sector, Element, Level], ShadowEncoding] = {
    (Sector.SQUARE, Element.EARTH, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PI, 
                               Sector.SQUARE, Element.EARTH, Level.L0),
        inner_name="Counting Entropy",
        inner_description="Bits to specify a point in the circle",
        inner_formula="log(πN²)",
        bit_depth=np.log2(np.pi),
        outer_name="Lattice Saturation",
        outer_description="Maximum representable lattice size",
        outer_formula="N_max where πN² ~ 2^bits",
        horizon=2**64 / np.pi
    ),
    (Sector.SQUARE, Element.WATER, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PI,
                               Sector.SQUARE, Element.WATER, Level.L0),
        inner_name="Convergence Depth",
        inner_description="-log|π - n·sin(π/n)| for n-gon",
        inner_formula="-log(ε) where ε = π - n·sin(π/n)",
        bit_depth=np.log2(1e10),  # bits of precision
        outer_name="Archimedes Limit",
        outer_description="Maximum computable polygon sides",
        outer_formula="n_max where roundoff > truncation",
        horizon=2**53  # double precision
    ),
    (Sector.SQUARE, Element.FIRE, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PI,
                               Sector.SQUARE, Element.FIRE, Level.L0),
        inner_name="Series Entropy",
        inner_description="Information content of Leibniz partial sum",
        inner_formula="log(n) bits for n-term sum",
        bit_depth=np.log2(1000),
        outer_name="Convergence Horizon",
        outer_description="Terms needed for given precision",
        outer_formula="n ~ 10^k for k digits",
        horizon=1e15
    ),
    (Sector.SQUARE, Element.AIR, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PI,
                               Sector.SQUARE, Element.AIR, Level.L0),
        inner_name="Spectral Resolution",
        inner_description="Bits per frequency bin",
        inner_formula="log(2π/Δω)",
        bit_depth=np.log2(2*np.pi),
        outer_name="Nyquist Frequency",
        outer_description="Maximum resolvable frequency",
        outer_formula="f_max = f_s/2",
        horizon=1e9  # typical DSP
    ),
    (Sector.FLOWER, Element.EARTH, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PI,
                               Sector.FLOWER, Element.EARTH, Level.L0),
        inner_name="Geometric Entropy",
        inner_description="Bits to specify circle parameters",
        inner_formula="log(C) + log(r)",
        bit_depth=2 * np.log2(np.pi),
        outer_name="Metric Singularity",
        outer_description="Where metric becomes degenerate",
        outer_formula="r → 0 or r → ∞",
        horizon=1e-15  # Planck length
    ),
    (Sector.FLOWER, Element.WATER, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PI,
                               Sector.FLOWER, Element.WATER, Level.L0),
        inner_name="Integration Depth",
        inner_description="Bits to regularize ∫sin(x)/x dx",
        inner_formula="log(1/ε) regularization bits",
        bit_depth=np.log2(1e10),
        outer_name="Gibbs Phenomenon",
        outer_description="Overshoot at discontinuity",
        outer_formula="~9% overshoot ceiling",
        horizon=1.089  # Gibbs constant
    ),
}


# Inner Shadow encodings for e-constant  
E_INNER_SHADOWS: Dict[Tuple[Sector, Element, Level], ShadowEncoding] = {
    (Sector.SQUARE, Element.EARTH, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.E,
                               Sector.SQUARE, Element.EARTH, Level.L0),
        inner_name="Factorial Entropy",
        inner_description="Stirling: log(n!) ≈ n log n - n",
        inner_formula="n·log(n) - n + O(log n)",
        bit_depth=10 * np.log2(10) - 10,  # n=10 example
        outer_name="Factorial Overflow",
        outer_description="Maximum computable factorial",
        outer_formula="n! < 2^bits",
        horizon=170  # 170! ~ 2^1024
    ),
    (Sector.FLOWER, Element.FIRE, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.E,
                               Sector.FLOWER, Element.FIRE, Level.L0),
        inner_name="Dynamical Entropy",
        inner_description="Lyapunov exponent λ as bits/time",
        inner_formula="λ = lim (1/t) log|δx(t)/δx(0)|",
        bit_depth=1.0,  # unit rate
        outer_name="Blow-up Time",
        outer_description="Where solution diverges",
        outer_formula="T* = 1/λ for exponential growth",
        horizon=1e10
    ),
    (Sector.CLOUD, Element.EARTH, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.E,
                               Sector.CLOUD, Element.EARTH, Level.L0),
        inner_name="Poisson Entropy",
        inner_description="H(Poisson(λ)) = λ(1 - log λ) + ...",
        inner_formula="λ(1 - log λ) + e^{-λ}Σ(λ^k/k!)log(k!)",
        bit_depth=np.e * (1 - np.log(np.e)),
        outer_name="Count Saturation",
        outer_description="Where Poisson → Gaussian",
        outer_formula="λ > 20 for CLT",
        horizon=20
    ),
}


# Inner Shadow encodings for i-constant
I_INNER_SHADOWS: Dict[Tuple[Sector, Element, Level], ShadowEncoding] = {
    (Sector.FLOWER, Element.WATER, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.I,
                               Sector.FLOWER, Element.WATER, Level.L0),
        inner_name="Holographic Depth",
        inner_description="Bits on boundary encoding interior",
        inner_formula="log(winding number) + log(residue precision)",
        bit_depth=np.log2(2*np.pi),
        outer_name="Cauchy Singularity",
        outer_description="Where contour hits pole",
        outer_formula="min|z - z_k| → 0",
        horizon=1e-15
    ),
    (Sector.FLOWER, Element.FIRE, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.I,
                               Sector.FLOWER, Element.FIRE, Level.L0),
        inner_name="Quantum Phase",
        inner_description="The iℏ coefficient as phase rate",
        inner_formula="phase = Et/ℏ radians",
        bit_depth=np.log2(2*np.pi),
        outer_name="Decoherence Time",
        outer_description="Environment-induced collapse scale",
        outer_formula="τ_D ~ ℏ/(kT·coupling)",
        horizon=1e-9  # nanoseconds for mesoscopic
    ),
    (Sector.SQUARE, Element.AIR, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.I,
                               Sector.SQUARE, Element.AIR, Level.L0),
        inner_name="DFT Phase Entropy",
        inner_description="Bits per phase coefficient",
        inner_formula="log(2π/N) per frequency",
        bit_depth=np.log2(2*np.pi),
        outer_name="Aliasing Threshold",
        outer_description="Nyquist frequency limit",
        outer_formula="f_max = f_s/2",
        horizon=1e9
    ),
}


# Inner Shadow encodings for φ-constant
PHI_INNER_SHADOWS: Dict[Tuple[Sector, Element, Level], ShadowEncoding] = {
    (Sector.SQUARE, Element.EARTH, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PHI,
                               Sector.SQUARE, Element.EARTH, Level.L0),
        inner_name="Zeckendorf Entropy",
        inner_description="Bits to represent n in Fibonacci base",
        inner_formula="~log_φ(n) = ln(n)/ln(φ) bits",
        bit_depth=1/np.log2((1+np.sqrt(5))/2),
        outer_name="Fibonacci Overflow",
        outer_description="Maximum representable Fibonacci",
        outer_formula="F_n < 2^bits",
        horizon=7540113804746346429  # F_92
    ),
    (Sector.FLOWER, Element.FIRE, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PHI,
                               Sector.FLOWER, Element.FIRE, Level.L0),
        inner_name="Spiral Code",
        inner_description="Bits per spiral whorl",
        inner_formula="log_φ(r/r_0) whorls",
        bit_depth=1/np.log2((1+np.sqrt(5))/2),
        outer_name="Visibility Horizon",
        outer_description="Outermost visible whorl",
        outer_formula="r_max where resolution fails",
        horizon=1e6
    ),
    (Sector.FRACTAL, Element.EARTH, Level.L0): ShadowEncoding(
        address=CrystalAddress(MetaPole.INNER_SHADOW, Constant.PHI,
                               Sector.FRACTAL, Element.EARTH, Level.L0),
        inner_name="Beatty Depth",
        inner_description="Bits to compute ⌊nφ⌋",
        inner_formula="log(n) + log(precision of φ)",
        bit_depth=53,  # double precision
        outer_name="Beatty Collision",
        outer_description="Where rounding errors matter",
        outer_formula="n ~ 10^15 for double",
        horizon=1e15
    ),
}


# =============================================================================
# TUNNELING ENGINE
# =============================================================================

class TunnelingEngine:
    """
    Engine for computing tunneling paths through the Crystal.
    
    Implements the 90° rotation mechanism between poles:
    - Horizontal (Reality axis): Aether ↔ Anti-Aether
    - Vertical (Shadow axis): Inner Shadow ↔ Outer Shadow
    """
    
    PHI = (1 + np.sqrt(5)) / 2
    
    def __init__(self, lattice: CrystalLattice):
        self.lattice = lattice
        self._load_shadow_encodings()
    
    def _load_shadow_encodings(self) -> None:
        """Load all shadow encodings."""
        self.pi_shadows = PI_INNER_SHADOWS
        self.e_shadows = E_INNER_SHADOWS
        self.i_shadows = I_INNER_SHADOWS
        self.phi_shadows = PHI_INNER_SHADOWS
    
    def get_shadow_encoding(self, addr: CrystalAddress) -> Optional[ShadowEncoding]:
        """Get shadow encoding for an address."""
        key = (addr.sector, addr.element, addr.level)
        
        if addr.constant == Constant.PI:
            return self.pi_shadows.get(key)
        elif addr.constant == Constant.E:
            return self.e_shadows.get(key)
        elif addr.constant == Constant.I:
            return self.i_shadows.get(key)
        elif addr.constant == Constant.PHI:
            return self.phi_shadows.get(key)
        return None
    
    def compute_tunnel(self, source: CrystalAddress, 
                       target_pole: MetaPole) -> TunnelPath:
        """
        Compute the tunneling path from source to target pole.
        
        The tunneling rotates through the Crystal geometry:
        - Aether (0°) → Anti-Aether (90°) → Outer (180°) → Inner (270°)
        """
        # Compute rotation angle
        source_angle = source.meta_pole.value * 90
        target_angle = target_pole.value * 90
        rotation = (target_angle - source_angle) % 360
        
        # Determine direction
        if source.meta_pole.axis == "Horizontal" and target_pole.axis == "Horizontal":
            direction = TunnelDirection.HORIZONTAL
            barrier = "Magnitude barrier (Yes/No)"
        elif source.meta_pole.axis == "Vertical" and target_pole.axis == "Vertical":
            direction = TunnelDirection.VERTICAL
            barrier = "Structure barrier (Code/Limit)"
        elif rotation == 90 or rotation == 180:
            direction = TunnelDirection.CLOCKWISE
            barrier = "Mixed barrier (magnitude+structure)"
        else:
            direction = TunnelDirection.COUNTER_CLOCKWISE
            barrier = "Mixed barrier (structure+magnitude)"
        
        # Compute κ-cost
        kappa_cost = self._compute_tunnel_cost(source, target_pole)
        
        # Build target address
        target = CrystalAddress(target_pole, source.constant, source.sector,
                               source.element, source.level)
        
        return TunnelPath(
            source=source,
            target=target,
            direction=direction,
            rotation_angle=rotation,
            barrier_crossed=barrier,
            kappa_cost=kappa_cost
        )
    
    def _compute_tunnel_cost(self, source: CrystalAddress, 
                             target_pole: MetaPole) -> float:
        """
        Compute the κ-cost of tunneling.
        
        Tunneling into Anti-Aether is expensive.
        Tunneling through shadows is information-theoretic.
        """
        if target_pole == MetaPole.AETHER:
            return 0.1  # Easy: returning to allowed
        elif target_pole == MetaPole.ANTI_AETHER:
            return 2.0  # Hard: approaching forbidden
        elif target_pole == MetaPole.INNER_SHADOW:
            # Cost is proportional to information content
            encoding = self.get_shadow_encoding(source)
            if encoding:
                return encoding.bit_depth / 64  # Normalize
            return 0.5
        else:  # OUTER_SHADOW
            # Cost is proportional to distance from horizon
            encoding = self.get_shadow_encoding(source)
            if encoding:
                return np.log10(encoding.horizon) / 20
            return 0.5
    
    def tunnel_through_barrier(self, addr: CrystalAddress) -> List[TunnelPath]:
        """
        Compute all possible tunneling paths from an address.
        
        Returns paths to all four poles (including identity).
        """
        paths = []
        for target_pole in MetaPole:
            if target_pole != addr.meta_pole:
                paths.append(self.compute_tunnel(addr, target_pole))
        return paths
    
    def find_lowest_cost_tunnel(self, addr: CrystalAddress, 
                                 target_pole: MetaPole) -> TunnelPath:
        """Find the lowest-cost path to target pole."""
        # Direct tunnel
        direct = self.compute_tunnel(addr, target_pole)
        
        # Two-step tunnels (through intermediate poles)
        best = direct
        for intermediate in MetaPole:
            if intermediate != addr.meta_pole and intermediate != target_pole:
                path1 = self.compute_tunnel(addr, intermediate)
                # Create intermediate address
                inter_addr = CrystalAddress(intermediate, addr.constant, addr.sector,
                                           addr.element, addr.level)
                path2 = self.compute_tunnel(inter_addr, target_pole)
                
                total_cost = path1.kappa_cost + path2.kappa_cost
                if total_cost < best.kappa_cost:
                    # Return combined path
                    best = TunnelPath(
                        source=addr,
                        target=path2.target,
                        direction=TunnelDirection.CLOCKWISE if path1.rotation_angle + path2.rotation_angle < 360 else TunnelDirection.COUNTER_CLOCKWISE,
                        rotation_angle=path1.rotation_angle + path2.rotation_angle,
                        barrier_crossed=f"{path1.barrier_crossed} → {path2.barrier_crossed}",
                        kappa_cost=total_cost
                    )
        
        return best
    
    def shadow_projection(self, addr: CrystalAddress) -> Tuple[ShadowEncoding, ShadowEncoding]:
        """
        Get both shadow projections of an Aether/Anti-Aether expression.
        
        Returns (inner_shadow, outer_shadow).
        """
        encoding = self.get_shadow_encoding(addr)
        if encoding:
            inner = encoding  # Inner shadow is the encoding itself
            
            # Create outer shadow address
            outer_addr = CrystalAddress(MetaPole.OUTER_SHADOW, addr.constant,
                                       addr.sector, addr.element, addr.level)
            
            # For outer shadow, we swap the descriptions
            outer = ShadowEncoding(
                address=outer_addr,
                inner_name=encoding.outer_name,
                inner_description=encoding.outer_description,
                inner_formula=encoding.outer_formula,
                bit_depth=np.log2(encoding.horizon) if encoding.horizon > 0 else 0,
                outer_name=encoding.inner_name,
                outer_description="Inverse of " + encoding.inner_description,
                outer_formula="exp(" + encoding.inner_formula + ")",
                horizon=encoding.bit_depth
            )
            return (inner, outer)
        return (None, None)


# =============================================================================
# CIRCULATION PATHS
# =============================================================================

class CirculationPath:
    """
    A complete circulation through all four poles.
    
    The Crystal has a natural circulation:
    Aether → Anti-Aether → Outer Shadow → Inner Shadow → Aether
    """
    
    def __init__(self, start: CrystalAddress):
        self.start = start
        self.path: List[TunnelPath] = []
        self._build_circulation()
    
    def _build_circulation(self) -> None:
        """Build the complete circulation."""
        engine = TunnelingEngine(CrystalLattice())
        
        current = self.start
        for next_pole in [MetaPole.ANTI_AETHER, MetaPole.OUTER_SHADOW,
                         MetaPole.INNER_SHADOW, MetaPole.AETHER]:
            tunnel = engine.compute_tunnel(current, next_pole)
            self.path.append(tunnel)
            current = tunnel.target
    
    @property
    def total_cost(self) -> float:
        """Total κ-cost of circulation."""
        return sum(p.kappa_cost for p in self.path)
    
    @property
    def is_closed(self) -> bool:
        """Check if circulation returns to start."""
        return (len(self.path) == 4 and 
                self.path[-1].target.meta_pole == self.start.meta_pole)
    
    def __iter__(self):
        return iter(self.path)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_tunneling() -> bool:
    """Validate tunneling mechanics."""
    lattice = CrystalLattice()
    engine = TunnelingEngine(lattice)
    
    # Test basic tunneling
    addr = CrystalAddress(MetaPole.AETHER, Constant.PI, 
                          Sector.SQUARE, Element.EARTH, Level.L0)
    
    # Tunnel to Anti-Aether
    tunnel = engine.compute_tunnel(addr, MetaPole.ANTI_AETHER)
    assert tunnel.rotation_angle == 90
    assert tunnel.direction == TunnelDirection.HORIZONTAL
    assert tunnel.kappa_cost > 0
    
    # Get all tunnels
    tunnels = engine.tunnel_through_barrier(addr)
    assert len(tunnels) == 3  # To 3 other poles
    
    # Test shadow encoding
    encoding = engine.get_shadow_encoding(addr)
    assert encoding is not None
    assert encoding.inner_name == "Counting Entropy"
    
    # Test circulation
    circ = CirculationPath(addr)
    assert circ.is_closed
    assert len(circ.path) == 4
    
    # Test lowest cost
    best = engine.find_lowest_cost_tunnel(addr, MetaPole.OUTER_SHADOW)
    assert best.target.meta_pole == MetaPole.OUTER_SHADOW
    
    return True


if __name__ == "__main__":
    print("Validating Tunneling Mechanics...")
    assert validate_tunneling()
    print("✓ Tunneling Mechanics validated")
    
    # Demo
    lattice = CrystalLattice()
    engine = TunnelingEngine(lattice)
    
    addr = CrystalAddress(MetaPole.AETHER, Constant.PI,
                          Sector.SQUARE, Element.EARTH, Level.L0)
    
    print(f"\n=== Tunneling from {addr.coordinate_string} ===")
    
    for tunnel in engine.tunnel_through_barrier(addr):
        print(f"\n→ {tunnel.target.meta_pole.name}")
        print(f"  Rotation: {tunnel.rotation_angle}°")
        print(f"  Direction: {tunnel.direction.name}")
        print(f"  Barrier: {tunnel.barrier_crossed}")
        print(f"  κ-cost: {tunnel.kappa_cost:.3f}")
    
    print("\n=== Shadow Projection ===")
    encoding = engine.get_shadow_encoding(addr)
    if encoding:
        print(f"Inner Shadow: {encoding.inner_name}")
        print(f"  {encoding.inner_description}")
        print(f"  Formula: {encoding.inner_formula}")
        print(f"  Bit depth: {encoding.bit_depth:.2f}")
        print(f"\nOuter Shadow: {encoding.outer_name}")
        print(f"  {encoding.outer_description}")
        print(f"  Formula: {encoding.outer_formula}")
        print(f"  Horizon: {encoding.horizon:.2e}")

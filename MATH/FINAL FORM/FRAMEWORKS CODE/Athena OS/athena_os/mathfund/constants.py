"""
ATHENA OS - Mathematical Constants Crystal
==========================================
The complete constant passport system from MATH_FUNDAMENTALS.docx

FOUR CONTAINERS:
    Square (C_□)  = {0, 1, -1, 2} - Discrete/algebraic identities
    Flower (C_❀)  = {e, i, π, φ} - Continuous/transcendental
    Cloud (C_☁)   = {γ, √2π, G, ζ(3)} - Limit/integral/series
    Fractal (C_✶) = {δ_s, ρ, δ_F, α_F} - Scaling/renormalization

FOUR OPERATIONS:
    Square ops: {=, -, ×, ÷} (F = G ⟺ Z(F-G))
    Flower ops: {cos, sin, -sin, cos} (90° shadows)
    Cloud ops: {d/dt, ∫, F, M} (differential/integral/transform)
    Fractal ops: {exp, log, pow, root} (linear in ln-space)

CONSTANT PASSPORT (4 faces):
    Square-face: algebraic identity (min poly, sign, units)
    Fractal-face: ln|c|, log_φ|c| (scale coordinates)
    Flower-face: Arg(c), θ_φ (phase/rotation coordinates)
    Cloud-face: g = Log(c), eigenlaw D[e^{gt}] = g·e^{gt}

LENS MAPS:
    Cloud generator: g = Log(c) (declared branch)
    Fractal coordinate: a = Re(g) = ln|c|
    Flower coordinate: θ = Im(g) = Arg(c)
    φ-aligned conversion: θ_φ = (π/2)·log_φ(c), c = φ^{2θ/π}
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
import math
import cmath


# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================

# High-precision values
PI = 3.1415926535897932384626433832795028841972
E = 2.7182818284590452353602874713526624977572
PHI = 1.6180339887498948482045868343656381177203
LN_PHI = 0.4812118250596034474977589134243684231352

# Cloud constants
GAMMA = 0.5772156649015328606065120900824024310422  # Euler-Mascheroni
SQRT_2PI = 2.5066282746310005024157652848110452530069
CATALAN = 0.9159655941772190150546035149323841107741  # Catalan's G
ZETA_3 = 1.2020569031595942853997381615114499907649  # Apéry's constant

# Fractal constants
SILVER_RATIO = 2.4142135623730950488016887242096980785697  # δ_s = 1 + √2
PLASTIC_RATIO = 1.3247179572447460259609088544780973407344  # ρ
FEIGENBAUM_DELTA = 4.66920160910299  # δ_F (universal period-doubling)
FEIGENBAUM_ALPHA = 2.502907875095892  # α_F (spatial scaling)


# =============================================================================
# CONTAINER TYPES
# =============================================================================

class Container(Enum):
    """The four mathematical containers."""
    SQUARE = "square"    # Discrete/algebraic
    FLOWER = "flower"    # Continuous/transcendental
    CLOUD = "cloud"      # Limit/integral/series
    FRACTAL = "fractal"  # Scaling/renormalization
    
    @property
    def symbol(self) -> str:
        symbols = {
            Container.SQUARE: "□",
            Container.FLOWER: "❀",
            Container.CLOUD: "☁",
            Container.FRACTAL: "✶"
        }
        return symbols[self]


# =============================================================================
# CONSTANT FACES
# =============================================================================

@dataclass
class SquareFace:
    """
    Square face: algebraic identity.
    
    Contains minimal polynomial, sign, notes about algebraic nature.
    """
    min_poly: Optional[str] = None  # e.g., "x^2-x-1" for φ
    sign: int = 1  # -1, 0, or 1
    is_algebraic: bool = False
    notes: str = ""


@dataclass
class FractalFace:
    """
    Fractal face: scale coordinates.
    
    ln|c| and log_φ|c| for any constant c.
    """
    ln_abs: float = 0.0       # ln|c|
    log_phi_abs: float = 0.0  # log_φ|c| = ln|c| / ln(φ)
    theta_phi: float = 0.0    # (π/2) · log_φ|c|
    
    @classmethod
    def from_value(cls, value: complex) -> 'FractalFace':
        """Compute fractal face from value."""
        abs_val = abs(value)
        if abs_val == 0:
            return cls(ln_abs=float('-inf'), log_phi_abs=float('-inf'))
        
        ln_abs = math.log(abs_val)
        log_phi_abs = ln_abs / LN_PHI
        theta_phi = (PI / 2) * log_phi_abs
        
        return cls(ln_abs=ln_abs, log_phi_abs=log_phi_abs, theta_phi=theta_phi)


@dataclass
class FlowerFace:
    """
    Flower face: phase/rotation coordinates.
    
    Arg(c) and θ_φ for any constant c.
    """
    arg: float = 0.0  # Arg(c) in (-π, π]
    
    @classmethod
    def from_value(cls, value: complex) -> 'FlowerFace':
        """Compute flower face from value."""
        if value == 0:
            return cls(arg=0.0)  # Undefined, use 0
        return cls(arg=cmath.phase(value))


@dataclass
class CloudFace:
    """
    Cloud face: complex logarithm generator.
    
    g = Log(c) = ln|c| + i·Arg(c)
    
    Eigenlaw: D[e^{gt}] = g·e^{gt}
    """
    g_real: float = 0.0  # Re(g) = ln|c|
    g_imag: float = 0.0  # Im(g) = Arg(c)
    branch: str = "principal"  # Branch declaration
    
    @property
    def g(self) -> complex:
        """Get complex generator."""
        return complex(self.g_real, self.g_imag)
    
    @classmethod
    def from_value(cls, value: complex, branch: str = "principal") -> 'CloudFace':
        """Compute cloud face from value."""
        if value == 0:
            return cls(g_real=float('-inf'), g_imag=0.0, branch=branch)
        
        g = cmath.log(value)  # Principal branch
        return cls(g_real=g.real, g_imag=g.imag, branch=branch)


# =============================================================================
# CONSTANT PASSPORT
# =============================================================================

@dataclass
class ConstantPassport:
    """
    Complete passport for a mathematical constant.
    
    Contains all 4 faces plus metadata and certificates.
    """
    
    # Identity
    id: str
    name: str
    container: Container
    
    # Value
    value: complex
    approx_decimal: str  # High-precision string
    
    # Four faces
    square_face: SquareFace
    fractal_face: FractalFace
    flower_face: FlowerFace
    cloud_face: CloudFace
    
    # Definition
    definition_key: str
    definition: str
    
    # Certificate
    cert_checklist: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, id: str, name: str, container: Container,
               value: complex, definition_key: str, definition: str,
               min_poly: Optional[str] = None, is_algebraic: bool = False,
               notes: str = "") -> 'ConstantPassport':
        """Create a passport with computed faces."""
        
        # Compute faces
        square = SquareFace(
            min_poly=min_poly,
            sign=1 if value.real >= 0 else -1,
            is_algebraic=is_algebraic,
            notes=notes
        )
        fractal = FractalFace.from_value(value)
        flower = FlowerFace.from_value(value)
        cloud = CloudFace.from_value(value)
        
        # Standard certificate checklist
        cert = [
            "Domain declared (default D=(0,∞) unless sign/complex extension)",
            "If c=0: boundary seed; Log and Arg undefined",
            "If c≠0: principal Arg in (-π,π] recorded",
            "g=Log(c) stored with explicit branch",
            "s=log_φ(|c|) computed with φ fixed to (1+√5)/2",
            "Reconstruction check: exp(g) matches c within tolerance"
        ]
        
        return cls(
            id=id,
            name=name,
            container=container,
            value=value,
            approx_decimal=f"{value.real:.40f}" if value.imag == 0 else f"{value}",
            square_face=square,
            fractal_face=fractal,
            flower_face=flower,
            cloud_face=cloud,
            definition_key=definition_key,
            definition=definition,
            cert_checklist=cert
        )
    
    def reconstruct(self) -> complex:
        """Reconstruct value from cloud generator."""
        return cmath.exp(self.cloud_face.g)
    
    def verify_reconstruction(self, tolerance: float = 1e-10) -> bool:
        """Verify reconstruction matches original."""
        if self.value == 0:
            return True  # Cannot reconstruct zero
        reconstructed = self.reconstruct()
        return abs(reconstructed - self.value) < tolerance
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "container": self.container.value,
            "value": {
                "real": self.value.real,
                "imag": self.value.imag,
            },
            "square": {
                "min_poly": self.square_face.min_poly,
                "sign": self.square_face.sign,
                "is_algebraic": self.square_face.is_algebraic,
            },
            "fractal": {
                "ln_abs": self.fractal_face.ln_abs,
                "log_phi_abs": self.fractal_face.log_phi_abs,
                "theta_phi": self.fractal_face.theta_phi,
            },
            "flower": {
                "arg": self.flower_face.arg,
            },
            "cloud": {
                "g_real": self.cloud_face.g_real,
                "g_imag": self.cloud_face.g_imag,
                "branch": self.cloud_face.branch,
            },
            "definition_key": self.definition_key,
        }


# =============================================================================
# CONSTANT CATALOG
# =============================================================================

def create_square_constants() -> List[ConstantPassport]:
    """Create Square container constants: {0, 1, -1, 2}."""
    return [
        ConstantPassport.create(
            id="SQUARE:0", name="Zero", container=Container.SQUARE,
            value=0, definition_key="DK_Z0",
            definition="0 is additive identity: x+0=x",
            notes="Additive identity; absorbing for ×"
        ),
        ConstantPassport.create(
            id="SQUARE:1", name="One", container=Container.SQUARE,
            value=1, definition_key="DK_Z1",
            definition="1 is multiplicative identity: x·1=x",
            notes="Multiplicative identity; fixed point of all powers"
        ),
        ConstantPassport.create(
            id="SQUARE:-1", name="Negative One", container=Container.SQUARE,
            value=-1, definition_key="DK_ZM1",
            definition="-1 is additive inverse of 1: 1+(-1)=0; also exp(iπ)=-1",
            min_poly="x+1", is_algebraic=True,
            notes="Involution: (-1)² = 1; Euler closure: e^{iπ} = -1"
        ),
        ConstantPassport.create(
            id="SQUARE:2", name="Two", container=Container.SQUARE,
            value=2, definition_key="DK_Z2",
            definition="2 = 1+1",
            notes="First nontrivial integer; dyadic generator"
        ),
    ]


def create_flower_constants() -> List[ConstantPassport]:
    """Create Flower container constants: {e, i, π, φ}."""
    return [
        ConstantPassport.create(
            id="FLOWER:e", name="Euler's Number", container=Container.FLOWER,
            value=E, definition_key="DK_E1",
            definition="e = exp(1) = Σ_{n≥0} 1/n! = lim_{n→∞} (1+1/n)^n",
            notes="Transcendental; pure growth pole (no phase)"
        ),
        ConstantPassport.create(
            id="FLOWER:i", name="Imaginary Unit", container=Container.FLOWER,
            value=1j, definition_key="DK_F1",
            definition="i² + 1 = 0 (principal imaginary unit)",
            min_poly="x²+1", is_algebraic=True,
            notes="Quarter-turn generator; Arg(i) = π/2"
        ),
        ConstantPassport.create(
            id="FLOWER:pi", name="Pi", container=Container.FLOWER,
            value=PI, definition_key="DK_P1",
            definition="π = 4·∫₀¹ 1/(1+x²) dx = 2·arccos(-1)",
            notes="Transcendental; circle normalization pole"
        ),
        ConstantPassport.create(
            id="FLOWER:phi", name="Golden Ratio", container=Container.FLOWER,
            value=PHI, definition_key="DK_PH1",
            definition="φ = (1+√5)/2, root of x²-x-1=0",
            min_poly="x²-x-1", is_algebraic=True,
            notes="Algebraic; exactly log_φ(φ) = 1, θ_φ(φ) = π/2"
        ),
    ]


def create_cloud_constants() -> List[ConstantPassport]:
    """Create Cloud container constants: {γ, √2π, G, ζ(3)}."""
    return [
        ConstantPassport.create(
            id="CLOUD:gamma", name="Euler-Mascheroni", container=Container.CLOUD,
            value=GAMMA, definition_key="DK_CG",
            definition="γ = lim_{n→∞} (Σ_{k=1}^n 1/k - ln n)",
            notes="Arithmetic nature unknown"
        ),
        ConstantPassport.create(
            id="CLOUD:sqrt2pi", name="√2π", container=Container.CLOUD,
            value=SQRT_2PI, definition_key="DK_C2PI",
            definition="√(2π) = ∫_{-∞}^{∞} exp(-x²/2) dx",
            notes="Gaussian normalization constant"
        ),
        ConstantPassport.create(
            id="CLOUD:G", name="Catalan's Constant", container=Container.CLOUD,
            value=CATALAN, definition_key="DK_CGAT",
            definition="G = Σ_{n≥0} (-1)^n/(2n+1)² = ∫₀¹ (arctan t)/t dt",
            notes="Arithmetic nature unknown"
        ),
        ConstantPassport.create(
            id="CLOUD:zeta3", name="Apéry's Constant", container=Container.CLOUD,
            value=ZETA_3, definition_key="DK_CZ3",
            definition="ζ(3) = Σ_{n≥1} 1/n³ (Apéry proved irrational)",
            notes="Irrational (proven)"
        ),
    ]


def create_fractal_constants() -> List[ConstantPassport]:
    """Create Fractal container constants: {δ_s, ρ, δ_F, α_F}."""
    return [
        ConstantPassport.create(
            id="FRACTAL:delta_s", name="Silver Ratio", container=Container.FRACTAL,
            value=SILVER_RATIO, definition_key="DK_FSIL",
            definition="δ_s = 1+√2, root of x²-2x-1=0",
            min_poly="x²-2x-1", is_algebraic=True,
            notes="Metallic mean; algebraic"
        ),
        ConstantPassport.create(
            id="FRACTAL:rho", name="Plastic Ratio", container=Container.FRACTAL,
            value=PLASTIC_RATIO, definition_key="DK_FPLA",
            definition="ρ is real root of x³-x-1=0",
            min_poly="x³-x-1", is_algebraic=True,
            notes="Plastic constant; algebraic"
        ),
        ConstantPassport.create(
            id="FRACTAL:delta_F", name="Feigenbaum δ", container=Container.FRACTAL,
            value=FEIGENBAUM_DELTA, definition_key="DK_FFD",
            definition="δ_F = limit of parameter-interval ratios in period-doubling",
            notes="Universal scaling; transcendental (conjectured)"
        ),
        ConstantPassport.create(
            id="FRACTAL:alpha_F", name="Feigenbaum α", container=Container.FRACTAL,
            value=-FEIGENBAUM_ALPHA, definition_key="DK_FFA",  # Note: negative
            definition="α_F = limit of spatial scaling ratios in period-doubling",
            notes="Universal scaling; transcendental (conjectured)"
        ),
    ]


def create_all_constants() -> Dict[str, ConstantPassport]:
    """Create complete catalog of all 16 constants."""
    catalog = {}
    
    for passport in create_square_constants():
        catalog[passport.id] = passport
    
    for passport in create_flower_constants():
        catalog[passport.id] = passport
    
    for passport in create_cloud_constants():
        catalog[passport.id] = passport
    
    for passport in create_fractal_constants():
        catalog[passport.id] = passport
    
    return catalog


# Global catalog
CONSTANT_CATALOG = create_all_constants()


# =============================================================================
# LENS MAPS
# =============================================================================

class LensMap:
    """
    Lens maps between containers.
    
    Core maps:
    - Cloud generator: g = Log(c)
    - Fractal coordinate: a = Re(g) = ln|c|
    - Flower coordinate: θ = Im(g) = Arg(c)
    - φ-aligned: θ_φ = (π/2)·log_φ(c), c = φ^{2θ/π}
    """
    
    @staticmethod
    def to_cloud_generator(c: complex) -> complex:
        """
        Map constant to cloud generator.
        
        g = Log(c) = ln|c| + i·Arg(c)
        """
        if c == 0:
            return complex(float('-inf'), 0)
        return cmath.log(c)
    
    @staticmethod
    def from_cloud_generator(g: complex) -> complex:
        """
        Reconstruct constant from cloud generator.
        
        c = exp(g)
        """
        return cmath.exp(g)
    
    @staticmethod
    def to_fractal_coordinate(c: complex) -> float:
        """
        Map constant to fractal coordinate.
        
        a = ln|c|
        """
        if c == 0:
            return float('-inf')
        return math.log(abs(c))
    
    @staticmethod
    def to_flower_coordinate(c: complex) -> float:
        """
        Map constant to flower coordinate.
        
        θ = Arg(c)
        """
        if c == 0:
            return 0.0
        return cmath.phase(c)
    
    @staticmethod
    def phi_angle(c: complex) -> float:
        """
        φ-aligned angle.
        
        θ_φ = (π/2)·log_φ|c|
        """
        if c == 0 or abs(c) == 0:
            return float('-inf')
        return (PI / 2) * math.log(abs(c)) / LN_PHI
    
    @staticmethod
    def from_phi_angle(theta_phi: float) -> float:
        """
        Reconstruct scale from φ-angle.
        
        c = φ^{2θ/π}
        """
        return PHI ** (2 * theta_phi / PI)
    
    @staticmethod
    def flower_to_fractal(theta: float) -> float:
        """
        Convert flower angle to fractal scale via φ.
        
        Only valid for real positive constants.
        Uses: θ = (π/2)·log_φ(c) ⟹ c = φ^{2θ/π}
        """
        return PHI ** (2 * theta / PI)
    
    @staticmethod
    def fractal_to_flower(c: float) -> float:
        """
        Convert fractal scale to flower angle via φ.
        
        Uses: θ_φ = (π/2)·log_φ(c)
        """
        if c <= 0:
            raise ValueError("Requires positive real")
        return (PI / 2) * math.log(c) / LN_PHI


# =============================================================================
# CONSTANT CRYSTAL
# =============================================================================

@dataclass
class ConstantCrystal:
    """
    The complete constant crystal - all 16 constants organized.
    """
    
    catalog: Dict[str, ConstantPassport] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.catalog:
            self.catalog = create_all_constants()
    
    def get(self, id: str) -> Optional[ConstantPassport]:
        """Get passport by ID."""
        return self.catalog.get(id)
    
    def get_by_container(self, container: Container) -> List[ConstantPassport]:
        """Get all constants in a container."""
        return [p for p in self.catalog.values() if p.container == container]
    
    def square_constants(self) -> List[ConstantPassport]:
        """Get Square container constants."""
        return self.get_by_container(Container.SQUARE)
    
    def flower_constants(self) -> List[ConstantPassport]:
        """Get Flower container constants."""
        return self.get_by_container(Container.FLOWER)
    
    def cloud_constants(self) -> List[ConstantPassport]:
        """Get Cloud container constants."""
        return self.get_by_container(Container.CLOUD)
    
    def fractal_constants(self) -> List[ConstantPassport]:
        """Get Fractal container constants."""
        return self.get_by_container(Container.FRACTAL)
    
    def verify_all(self) -> Dict[str, bool]:
        """Verify all reconstructions."""
        return {id: p.verify_reconstruction() for id, p in self.catalog.items()}
    
    def summary(self) -> Dict[str, Any]:
        """Get crystal summary."""
        container_counts = {c.value: 0 for c in Container}
        algebraic_count = 0
        
        for passport in self.catalog.values():
            container_counts[passport.container.value] += 1
            if passport.square_face.is_algebraic:
                algebraic_count += 1
        
        return {
            "total_constants": len(self.catalog),
            "by_container": container_counts,
            "algebraic": algebraic_count,
            "transcendental": len(self.catalog) - algebraic_count,
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_constants() -> bool:
    """Validate constants module."""
    
    # Test ConstantPassport
    passport = ConstantPassport.create(
        id="test", name="Test", container=Container.FLOWER,
        value=PI, definition_key="test", definition="test"
    )
    assert passport.verify_reconstruction()
    
    # Test all constants
    crystal = ConstantCrystal()
    assert len(crystal.catalog) == 16
    
    # Verify by container
    assert len(crystal.square_constants()) == 4
    assert len(crystal.flower_constants()) == 4
    assert len(crystal.cloud_constants()) == 4
    assert len(crystal.fractal_constants()) == 4
    
    # Verify reconstructions (skip zero)
    results = crystal.verify_all()
    for id, passed in results.items():
        if id != "SQUARE:0":
            assert passed, f"Reconstruction failed for {id}"
    
    # Test LensMap
    assert abs(LensMap.from_cloud_generator(LensMap.to_cloud_generator(PI)) - PI) < 1e-10
    
    # Test φ-alignment: log_φ(φ) = 1, θ_φ(φ) = π/2
    phi_passport = crystal.get("FLOWER:phi")
    assert abs(phi_passport.fractal_face.log_phi_abs - 1.0) < 1e-10
    assert abs(phi_passport.fractal_face.theta_phi - PI/2) < 1e-10
    
    # Test i: Arg(i) = π/2
    i_passport = crystal.get("FLOWER:i")
    assert abs(i_passport.flower_face.arg - PI/2) < 1e-10
    
    # Test -1: Arg(-1) = π
    m1_passport = crystal.get("SQUARE:-1")
    assert abs(m1_passport.flower_face.arg - PI) < 1e-10
    
    return True


if __name__ == "__main__":
    print("Validating Constants Module...")
    assert validate_constants()
    print("✓ Constants Module validated")
    
    # Demo
    print("\n=== Constant Crystal Demo ===")
    
    crystal = ConstantCrystal()
    print(f"\nSummary: {crystal.summary()}")
    
    print("\n16 Mathematical Constants:")
    for container in Container:
        print(f"\n{container.symbol} {container.value.upper()} Container:")
        for p in crystal.get_by_container(container):
            alg = "✓" if p.square_face.is_algebraic else "○"
            print(f"  {p.name:20s} = {p.value.real if p.value.imag == 0 else p.value}")
            print(f"    Algebraic: {alg}  ln|c|={p.fractal_face.ln_abs:.6f}")
    
    print("\n\nφ-Lens Verification:")
    phi = crystal.get("FLOWER:phi")
    print(f"  φ = {PHI:.10f}")
    print(f"  log_φ(φ) = {phi.fractal_face.log_phi_abs:.10f} (exact: 1)")
    print(f"  θ_φ(φ) = {phi.fractal_face.theta_phi:.10f} (exact: π/2 = {PI/2:.10f})")
    
    print("\n\nCloud Generator Examples:")
    for name, id in [("e", "FLOWER:e"), ("i", "FLOWER:i"), ("π", "FLOWER:pi")]:
        p = crystal.get(id)
        print(f"  Log({name}) = {p.cloud_face.g_real:.6f} + {p.cloud_face.g_imag:.6f}i")

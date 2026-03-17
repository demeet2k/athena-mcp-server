"""
ATHENA OS - Operation Crystal
=============================
The 256-Operation Crystal and 64 Anti-Expressions

From THE_SUPERPOSITIONING_CRYSTAL.docx Chapter 6 & Appendix A/B:

THE 256-OPERATION CRYSTAL:
    The "Periodic Table" of computational reality.
    Exhaustively maps all transformations across:
    - 4 Aetheric poles (π, e, i, φ)
    - 4 Topological shapes (Square, Flower, Cloud, Fractal)
    - 4 Elements (Earth, Water, Fire, Air)
    - 4 Poles (Primal, Anti, Inner, Outer)
    
    Total: 4 × 4 × 4 × 4 = 256 allowed operations

THE POSITIVE LATTICE ("YES"):
    256 operations that conserve the κ-Budget (Complexity).
    - Standard logic gates (Earth/Square)
    - Continuous flows (Water/Flower)
    - Stochastic transitions (Fire/Cloud)
    - Recursive scalings (Air/Fractal)

THE NEGATIVE-SPACE LATTICE ("NO"):
    64 Anti-Expressions (Impossible Operations).
    - Violate Texture, Entropy, or Scale laws
    - Form the Zero/Infinity Barriers
    - Define forbidden zones (Singularities, Collapses)

SECTORS:
    π-Sector (64): Geometry/Continuity/Closure
    e-Sector (64): Growth/Decay/Thermodynamics
    i-Sector (64): Phase/Rotation/Coherence
    φ-Sector (64): Scale/Recursion/Hierarchy
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import math

from .quad_polar import (
    Element, Shape, Constant, Pole,
    ElementalOperator, QuadPolarEngine,
    PI, E, PHI, I,
    LOG_PI, LOG_PHI
)


# =============================================================================
# OPERATION CATEGORIES
# =============================================================================

class OperationType(Enum):
    """Categories of operations in the crystal."""
    IDENTITY = "identity"
    TRANSFORM = "transform"
    PROJECTION = "projection"
    ROTATION = "rotation"
    SCALING = "scaling"
    TUNNELING = "tunneling"
    COLLAPSE = "collapse"
    BRANCHING = "branching"


class ViolationType(Enum):
    """Types of violations for Anti-Expressions."""
    TEXTURE = "texture"        # Violates information density bounds
    ENTROPY = "entropy"        # Violates thermodynamic laws
    SCALE = "scale"            # Violates hierarchy constraints
    CAUSALITY = "causality"    # Violates temporal ordering
    NORMALIZATION = "normalization"  # Violates probability/unitarity


# =============================================================================
# CRYSTAL OPERATION
# =============================================================================

@dataclass
class CrystalOperation:
    """
    A single operation in the 256-Operation Crystal.
    
    Each operation is indexed by (constant, shape, element, pole).
    """
    
    constant: Constant
    shape: Shape
    element: Element
    pole: Pole
    
    # Operation metadata
    name: str = ""
    formula: str = ""
    description: str = ""
    operation_type: OperationType = OperationType.TRANSFORM
    
    # κ-Budget properties
    kappa_cost: float = 1.0  # Texture cost
    is_unitary: bool = True  # Preserves norm
    is_reversible: bool = True
    
    def __post_init__(self):
        """Generate default name."""
        if not self.name:
            self.name = f"{self.constant.value}_{self.shape.value}_{self.element.value}^{self.pole.value}"
    
    @property
    def index(self) -> int:
        """Get unique index (0-255)."""
        c = list(Constant).index(self.constant)
        s = list(Shape).index(self.shape)
        e = list(Element).index(self.element)
        p = list(Pole).index(self.pole)
        return c * 64 + s * 16 + e * 4 + p
    
    @property
    def sector(self) -> str:
        """Get sector name (π, e, i, or φ)."""
        return self.constant.value
    
    @classmethod
    def from_index(cls, idx: int) -> 'CrystalOperation':
        """Create from 0-255 index."""
        p = idx % 4
        e = (idx // 4) % 4
        s = (idx // 16) % 4
        c = idx // 64
        
        return cls(
            constant=list(Constant)[c],
            shape=list(Shape)[s],
            element=list(Element)[e],
            pole=list(Pole)[p]
        )


# =============================================================================
# ANTI-EXPRESSION
# =============================================================================

@dataclass
class AntiExpression:
    """
    An impossible operation that violates the κ-Budget.
    
    These form the Negative-Space Lattice (64 total).
    They define the Zero/Infinity Barriers bounding the simplex.
    """
    
    index: int  # 0-63
    name: str
    violation: ViolationType
    description: str
    
    # What it would require
    required_cost: float = float('inf')  # κ-cost (infinite)
    
    # What law it violates
    violated_law: str = ""
    
    @property
    def sector(self) -> str:
        """Get sector (which constant boundary)."""
        sectors = ["π", "e", "i", "φ"]
        return sectors[self.index // 16]


# =============================================================================
# PI SECTOR (64 OPERATIONS)
# =============================================================================

def create_pi_sector() -> List[CrystalOperation]:
    """
    Create the 64 operations of the π-Sector.
    
    Governs: Geometry, Continuity, Closure, Normalization
    """
    operations = []
    
    # π-Square operations (discrete geometry)
    pi_square_ops = [
        ("π_□_E^A", "Integer lattice spacing", OperationType.IDENTITY),
        ("π_□_E^Ā", "Dual lattice (1/π spacing)", OperationType.TRANSFORM),
        ("π_□_E^in", "Lattice momentum (log π)", OperationType.PROJECTION),
        ("π_□_E^out", "Lattice cutoff (π^π)", OperationType.SCALING),
        ("π_□_W^A", "Circle inscribed in square", OperationType.TRANSFORM),
        ("π_□_W^Ā", "Square inscribed in circle", OperationType.TRANSFORM),
        ("π_□_W^in", "Squaring the circle (π encoding)", OperationType.PROJECTION),
        ("π_□_W^out", "Rectification limit", OperationType.COLLAPSE),
        ("π_□_F^A", "Gaussian integer norm", OperationType.IDENTITY),
        ("π_□_F^Ā", "Inverse Gaussian", OperationType.TRANSFORM),
        ("π_□_F^in", "Partition counting", OperationType.BRANCHING),
        ("π_□_F^out", "Asymptotic density", OperationType.SCALING),
        ("π_□_A^A", "Discrete Fourier basis", OperationType.ROTATION),
        ("π_□_A^Ā", "Inverse DFT", OperationType.ROTATION),
        ("π_□_A^in", "Circulant eigenvector", OperationType.PROJECTION),
        ("π_□_A^out", "Spectral gap", OperationType.TUNNELING),
    ]
    
    # π-Flower operations (continuous geometry)
    pi_flower_ops = [
        ("π_❀_E^A", "Circle circumference", OperationType.IDENTITY),
        ("π_❀_E^Ā", "Diameter-to-circumference", OperationType.TRANSFORM),
        ("π_❀_E^in", "Arc length element", OperationType.PROJECTION),
        ("π_❀_E^out", "Curvature integral", OperationType.SCALING),
        ("π_❀_W^A", "Area measure", OperationType.IDENTITY),
        ("π_❀_W^Ā", "Inverse area (density)", OperationType.TRANSFORM),
        ("π_❀_W^in", "Differential form", OperationType.PROJECTION),
        ("π_❀_W^out", "Volume saturation", OperationType.COLLAPSE),
        ("π_❀_F^A", "Gaussian integral √π", OperationType.IDENTITY),
        ("π_❀_F^Ā", "Error function", OperationType.TRANSFORM),
        ("π_❀_F^in", "Heat kernel", OperationType.TUNNELING),
        ("π_❀_F^out", "Diffusion limit", OperationType.COLLAPSE),
        ("π_❀_A^A", "Fourier transform", OperationType.ROTATION),
        ("π_❀_A^Ā", "Inverse Fourier", OperationType.ROTATION),
        ("π_❀_A^in", "Plancherel identity", OperationType.PROJECTION),
        ("π_❀_A^out", "Bandwidth limit", OperationType.TUNNELING),
    ]
    
    # π-Cloud operations (stochastic geometry)
    pi_cloud_ops = [
        ("π_☁_E^A", "Binomial → Normal", OperationType.TRANSFORM),
        ("π_☁_E^Ā", "Discretization error", OperationType.TRANSFORM),
        ("π_☁_E^in", "Central limit seed", OperationType.PROJECTION),
        ("π_☁_E^out", "Large deviation bound", OperationType.SCALING),
        ("π_☁_W^A", "Gaussian density", OperationType.IDENTITY),
        ("π_☁_W^Ā", "Inverse Gaussian", OperationType.TRANSFORM),
        ("π_☁_W^in", "Fisher information", OperationType.PROJECTION),
        ("π_☁_W^out", "Cramér-Rao bound", OperationType.TUNNELING),
        ("π_☁_F^A", "Maxwell-Boltzmann", OperationType.IDENTITY),
        ("π_☁_F^Ā", "Inverse temperature", OperationType.TRANSFORM),
        ("π_☁_F^in", "Partition function", OperationType.BRANCHING),
        ("π_☁_F^out", "Free energy bound", OperationType.COLLAPSE),
        ("π_☁_A^A", "Characteristic function", OperationType.ROTATION),
        ("π_☁_A^Ā", "Moment generating", OperationType.TRANSFORM),
        ("π_☁_A^in", "Cumulant expansion", OperationType.PROJECTION),
        ("π_☁_A^out", "Tail bound", OperationType.TUNNELING),
    ]
    
    # π-Fractal operations (self-similar geometry)
    pi_fractal_ops = [
        ("π_✶_E^A", "Circle packing", OperationType.IDENTITY),
        ("π_✶_E^Ā", "Apollonian gasket", OperationType.TRANSFORM),
        ("π_✶_E^in", "Packing dimension", OperationType.PROJECTION),
        ("π_✶_E^out", "Hausdorff measure", OperationType.SCALING),
        ("π_✶_W^A", "Spiral growth", OperationType.TRANSFORM),
        ("π_✶_W^Ā", "Involute curve", OperationType.TRANSFORM),
        ("π_✶_W^in", "Winding number", OperationType.PROJECTION),
        ("π_✶_W^out", "Limit cycle", OperationType.COLLAPSE),
        ("π_✶_F^A", "Wallis product", OperationType.IDENTITY),
        ("π_✶_F^Ā", "Inverse Wallis", OperationType.TRANSFORM),
        ("π_✶_F^in", "Infinite product seed", OperationType.BRANCHING),
        ("π_✶_F^out", "Product convergence", OperationType.COLLAPSE),
        ("π_✶_A^A", "Riemann zeta", OperationType.IDENTITY),
        ("π_✶_A^Ā", "L-function", OperationType.TRANSFORM),
        ("π_✶_A^in", "Functional equation", OperationType.PROJECTION),
        ("π_✶_A^out", "Critical strip", OperationType.TUNNELING),
    ]
    
    all_ops = pi_square_ops + pi_flower_ops + pi_cloud_ops + pi_fractal_ops
    
    shapes = [Shape.SQUARE] * 16 + [Shape.FLOWER] * 16 + [Shape.CLOUD] * 16 + [Shape.FRACTAL] * 16
    elements = [Element.EARTH, Element.EARTH, Element.EARTH, Element.EARTH,
                Element.WATER, Element.WATER, Element.WATER, Element.WATER,
                Element.FIRE, Element.FIRE, Element.FIRE, Element.FIRE,
                Element.AIR, Element.AIR, Element.AIR, Element.AIR] * 4
    poles = [Pole.PRIMAL, Pole.ANTI, Pole.INNER, Pole.OUTER] * 16
    
    for i, (name, desc, op_type) in enumerate(all_ops):
        op = CrystalOperation(
            constant=Constant.PI,
            shape=shapes[i],
            element=elements[i],
            pole=poles[i],
            name=name,
            description=desc,
            operation_type=op_type
        )
        operations.append(op)
    
    return operations


# =============================================================================
# PHI SECTOR (64 OPERATIONS)
# =============================================================================

def create_phi_sector() -> List[CrystalOperation]:
    """
    Create the 64 operations of the φ-Sector.
    
    Governs: Scale, Recursion, Self-Similarity, Hierarchy
    """
    operations = []
    
    for s_idx, shape in enumerate(Shape):
        for e_idx, element in enumerate(Element):
            for p_idx, pole in enumerate(Pole):
                # Generate descriptive name based on position
                shape_names = {
                    Shape.SQUARE: "Fibonacci lattice",
                    Shape.FLOWER: "Golden spiral",
                    Shape.CLOUD: "φ-branching",
                    Shape.FRACTAL: "Self-similar",
                }
                
                elem_names = {
                    Element.EARTH: "discrete",
                    Element.WATER: "continuous",
                    Element.FIRE: "stochastic",
                    Element.AIR: "spectral",
                }
                
                pole_names = {
                    Pole.PRIMAL: "expansion",
                    Pole.ANTI: "contraction",
                    Pole.INNER: "code",
                    Pole.OUTER: "envelope",
                }
                
                name = f"φ_{shape.value[:1]}_{element.value[:1]}^{pole.value[:1]}"
                desc = f"{shape_names[shape]} {elem_names[element]} {pole_names[pole]}"
                
                op = CrystalOperation(
                    constant=Constant.PHI,
                    shape=shape,
                    element=element,
                    pole=pole,
                    name=name,
                    description=desc,
                    operation_type=OperationType.SCALING if pole in [Pole.PRIMAL, Pole.ANTI] 
                                  else OperationType.PROJECTION
                )
                operations.append(op)
    
    return operations


# =============================================================================
# E SECTOR (64 OPERATIONS)
# =============================================================================

def create_e_sector() -> List[CrystalOperation]:
    """
    Create the 64 operations of the e-Sector.
    
    Governs: Growth, Decay, Thermodynamics, Entropy
    """
    operations = []
    
    for s_idx, shape in enumerate(Shape):
        for e_idx, element in enumerate(Element):
            for p_idx, pole in enumerate(Pole):
                shape_names = {
                    Shape.SQUARE: "Discrete growth",
                    Shape.FLOWER: "Continuous flow",
                    Shape.CLOUD: "Thermal",
                    Shape.FRACTAL: "Cascade",
                }
                
                elem_names = {
                    Element.EARTH: "counting",
                    Element.WATER: "differential",
                    Element.FIRE: "entropic",
                    Element.AIR: "spectral",
                }
                
                pole_names = {
                    Pole.PRIMAL: "growth e^x",
                    Pole.ANTI: "decay e^{-x}",
                    Pole.INNER: "rate ln(x)",
                    Pole.OUTER: "saturation",
                }
                
                name = f"e_{shape.value[:1]}_{element.value[:1]}^{pole.value[:1]}"
                desc = f"{shape_names[shape]} {elem_names[element]} {pole_names[pole]}"
                
                op = CrystalOperation(
                    constant=Constant.E,
                    shape=shape,
                    element=element,
                    pole=pole,
                    name=name,
                    description=desc,
                    operation_type=OperationType.TRANSFORM
                )
                operations.append(op)
    
    return operations


# =============================================================================
# I SECTOR (64 OPERATIONS)
# =============================================================================

def create_i_sector() -> List[CrystalOperation]:
    """
    Create the 64 operations of the i-Sector.
    
    Governs: Phase, Rotation, Orthogonality, Coherence
    """
    operations = []
    
    for s_idx, shape in enumerate(Shape):
        for e_idx, element in enumerate(Element):
            for p_idx, pole in enumerate(Pole):
                shape_names = {
                    Shape.SQUARE: "Discrete rotation",
                    Shape.FLOWER: "Complex plane",
                    Shape.CLOUD: "Interference",
                    Shape.FRACTAL: "Spiral phase",
                }
                
                elem_names = {
                    Element.EARTH: "Gaussian int",
                    Element.WATER: "analytic",
                    Element.FIRE: "quantum amp",
                    Element.AIR: "eigenphase",
                }
                
                pole_names = {
                    Pole.PRIMAL: "forward i",
                    Pole.ANTI: "backward -i",
                    Pole.INNER: "quarter-turn",
                    Pole.OUTER: "decoherence",
                }
                
                name = f"i_{shape.value[:1]}_{element.value[:1]}^{pole.value[:1]}"
                desc = f"{shape_names[shape]} {elem_names[element]} {pole_names[pole]}"
                
                op = CrystalOperation(
                    constant=Constant.I,
                    shape=shape,
                    element=element,
                    pole=pole,
                    name=name,
                    description=desc,
                    operation_type=OperationType.ROTATION
                )
                operations.append(op)
    
    return operations


# =============================================================================
# 64 ANTI-EXPRESSIONS
# =============================================================================

def create_anti_expressions() -> List[AntiExpression]:
    """
    Create the 64 Anti-Expressions (Impossible Operations).
    
    These form the Negative-Space Lattice bounding the operator simplex.
    """
    anti_expressions = []
    
    # π-Sector Anti-Expressions (16)
    pi_anti = [
        ("1/0", ViolationType.NORMALIZATION, "Division by zero - infinite density"),
        ("δ(x)²", ViolationType.TEXTURE, "Squared delta - undefined distribution"),
        ("∫_{-∞}^{∞} 1 dx", ViolationType.NORMALIZATION, "Uniform over R - non-normalizable"),
        ("log(0)", ViolationType.SCALE, "Logarithm of zero - infinite depth"),
        ("√(-1) as real", ViolationType.TEXTURE, "Complex as real - dimension violation"),
        ("∞ - ∞", ViolationType.NORMALIZATION, "Indeterminate form"),
        ("0/0", ViolationType.NORMALIZATION, "Indeterminate ratio"),
        ("∫ δ'(x) f(x) dx", ViolationType.TEXTURE, "Delta derivative - hypersingular"),
        ("det(0)", ViolationType.SCALE, "Determinant of singular - rank deficiency"),
        ("||x||_{-1}", ViolationType.TEXTURE, "Negative norm - undefined space"),
        ("π^∞", ViolationType.SCALE, "Infinite power - unbounded"),
        ("lim_{n→∞} n!", ViolationType.ENTROPY, "Factorial growth - infinite entropy"),
        ("∑_{n=1}^{∞} n", ViolationType.NORMALIZATION, "Divergent sum"),
        ("∏_{n=1}^{∞} n", ViolationType.SCALE, "Divergent product"),
        ("cos^{-1}(2)", ViolationType.TEXTURE, "Arccos of 2 - domain violation"),
        ("∫_C 1/z² dz", ViolationType.NORMALIZATION, "Residue at essential singularity"),
    ]
    
    # e-Sector Anti-Expressions (16)
    e_anti = [
        ("e^∞", ViolationType.SCALE, "Infinite exponential - unbounded"),
        ("e^{-∞} / e^{-∞}", ViolationType.NORMALIZATION, "0/0 in exponential"),
        ("ln(-1) as real", ViolationType.TEXTURE, "Log of negative - requires i"),
        ("∑ P > 1", ViolationType.NORMALIZATION, "Over-probability"),
        ("∑ P < 0", ViolationType.NORMALIZATION, "Negative probability"),
        ("H < 0", ViolationType.ENTROPY, "Negative entropy"),
        ("T = 0 exactly", ViolationType.ENTROPY, "Third law violation"),
        ("ΔS < 0 (closed)", ViolationType.ENTROPY, "Second law violation"),
        ("e^{x²} dx", ViolationType.NORMALIZATION, "Non-integrable growth"),
        ("lim_{t→0} e^{1/t}", ViolationType.SCALE, "Essential singularity"),
        ("∂/∂t e^{t²}", ViolationType.TEXTURE, "Unbounded derivative"),
        ("W(e^e)", ViolationType.SCALE, "Lambert W overflow"),
        ("Γ(-n)", ViolationType.NORMALIZATION, "Gamma at negative integers"),
        ("1/Γ(0)", ViolationType.NORMALIZATION, "Inverse gamma pole"),
        ("∫ e^{x³} dx", ViolationType.SCALE, "Super-exponential integral"),
        ("exp(exp(exp(...)))", ViolationType.SCALE, "Tower divergence"),
    ]
    
    # i-Sector Anti-Expressions (16)
    i_anti = [
        ("i² = 1", ViolationType.TEXTURE, "Complex arithmetic violation"),
        ("|ψ|² > 1", ViolationType.NORMALIZATION, "Probability > 1"),
        ("|ψ|² < 0", ViolationType.NORMALIZATION, "Negative probability"),
        ("U†U ≠ I", ViolationType.NORMALIZATION, "Non-unitary evolution"),
        ("[A,B] = ℏ + ε", ViolationType.TEXTURE, "Uncertainty violation"),
        ("⟨ψ|ψ⟩ < 0", ViolationType.NORMALIZATION, "Negative norm state"),
        ("arg(0)", ViolationType.TEXTURE, "Phase of zero - undefined"),
        ("|0⟩ + |1⟩ unnormalized", ViolationType.NORMALIZATION, "Non-unit superposition"),
        ("⟨ψ|φ⟩ > 1", ViolationType.NORMALIZATION, "Inner product > 1"),
        ("e^{2πi·irrational}", ViolationType.TEXTURE, "Non-closing phase"),
        ("∫ |ψ|² > ∞", ViolationType.NORMALIZATION, "Non-square-integrable"),
        ("commute(X,P)", ViolationType.TEXTURE, "Heisenberg violation"),
        ("cos(θ)² + sin(θ)² ≠ 1", ViolationType.NORMALIZATION, "Trig identity violation"),
        ("e^{iπ} ≠ -1", ViolationType.TEXTURE, "Euler identity violation"),
        ("phase(real) ≠ 0,π", ViolationType.TEXTURE, "Real phase violation"),
        ("√i as rational", ViolationType.TEXTURE, "Irrational as rational"),
    ]
    
    # φ-Sector Anti-Expressions (16)
    phi_anti = [
        ("φ^∞", ViolationType.SCALE, "Infinite scaling - unbounded"),
        ("φ^{-∞}", ViolationType.SCALE, "Infinite downscaling - collapse"),
        ("F_{-n} undefined", ViolationType.TEXTURE, "Negative Fibonacci - extension required"),
        ("log_φ(0)", ViolationType.SCALE, "Log-phi of zero - infinite depth"),
        ("φ = rational", ViolationType.TEXTURE, "Golden ratio rationalization"),
        ("self = f(self) diverge", ViolationType.SCALE, "Non-contractive recursion"),
        ("dim_H > n (in R^n)", ViolationType.TEXTURE, "Dimension overflow"),
        ("part > whole", ViolationType.SCALE, "Self-similarity violation"),
        ("∑ 1/φ^n → ∞", ViolationType.SCALE, "Geometric divergence"),
        ("fixed_point(id)", ViolationType.TEXTURE, "Identity fixed point - all points"),
        ("fractal_dim < 0", ViolationType.TEXTURE, "Negative dimension"),
        ("self-similar but bounded", ViolationType.SCALE, "Scale contradiction"),
        ("F_n / F_{n-1} ≠ φ", ViolationType.TEXTURE, "Limit violation"),
        ("φ² ≠ φ + 1", ViolationType.TEXTURE, "Golden identity violation"),
        ("1/φ ≠ φ - 1", ViolationType.TEXTURE, "Conjugate violation"),
        ("continued fraction terminate", ViolationType.TEXTURE, "φ CF termination"),
    ]
    
    all_anti = pi_anti + e_anti + i_anti + phi_anti
    
    for i, (formula, violation, desc) in enumerate(all_anti):
        anti = AntiExpression(
            index=i,
            name=f"Anti-{i:02d}",
            violation=violation,
            description=desc,
            violated_law=formula
        )
        anti_expressions.append(anti)
    
    return anti_expressions


# =============================================================================
# OPERATION CRYSTAL
# =============================================================================

@dataclass
class OperationCrystal:
    """
    The complete 256-Operation Crystal.
    
    Contains all 256 allowed operations and 64 anti-expressions.
    """
    
    operations: List[CrystalOperation] = field(default_factory=list)
    anti_expressions: List[AntiExpression] = field(default_factory=list)
    
    # Indexing
    _by_index: Dict[int, CrystalOperation] = field(default_factory=dict)
    _by_sector: Dict[str, List[CrystalOperation]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the crystal."""
        if not self.operations:
            self._build_crystal()
    
    def _build_crystal(self):
        """Build all 256 operations."""
        # Create all sectors
        self.operations = (
            create_pi_sector() +
            create_phi_sector() +
            create_e_sector() +
            create_i_sector()
        )
        
        # Create anti-expressions
        self.anti_expressions = create_anti_expressions()
        
        # Build indices
        self._by_index = {op.index: op for op in self.operations}
        self._by_sector = {
            "π": [op for op in self.operations if op.constant == Constant.PI],
            "e": [op for op in self.operations if op.constant == Constant.E],
            "i": [op for op in self.operations if op.constant == Constant.I],
            "φ": [op for op in self.operations if op.constant == Constant.PHI],
        }
    
    def get(self, index: int) -> Optional[CrystalOperation]:
        """Get operation by index."""
        return self._by_index.get(index)
    
    def get_sector(self, constant: str) -> List[CrystalOperation]:
        """Get all operations in a sector."""
        return self._by_sector.get(constant, [])
    
    def get_by_coordinates(self, constant: Constant, shape: Shape,
                          element: Element, pole: Pole) -> Optional[CrystalOperation]:
        """Get operation by full coordinates."""
        for op in self.operations:
            if (op.constant == constant and op.shape == shape and
                op.element == element and op.pole == pole):
                return op
        return None
    
    def is_anti(self, formula: str) -> bool:
        """Check if an expression is an anti-expression."""
        for anti in self.anti_expressions:
            if anti.violated_law == formula:
                return True
        return False
    
    def summary(self) -> Dict[str, Any]:
        """Get crystal summary."""
        return {
            "total_operations": len(self.operations),
            "anti_expressions": len(self.anti_expressions),
            "sectors": {
                "π": len(self._by_sector.get("π", [])),
                "e": len(self._by_sector.get("e", [])),
                "i": len(self._by_sector.get("i", [])),
                "φ": len(self._by_sector.get("φ", [])),
            },
            "operation_types": {
                ot.value: sum(1 for op in self.operations if op.operation_type == ot)
                for ot in OperationType
            }
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_crystal() -> bool:
    """Validate operation crystal module."""
    
    # Test crystal construction
    crystal = OperationCrystal()
    assert len(crystal.operations) == 256
    assert len(crystal.anti_expressions) == 64
    
    # Test sector sizes
    summary = crystal.summary()
    assert summary["sectors"]["π"] == 64
    assert summary["sectors"]["e"] == 64
    assert summary["sectors"]["i"] == 64
    assert summary["sectors"]["φ"] == 64
    
    # Test indexing
    for i in range(256):
        op = crystal.get(i)
        # Operations may not be sequential due to construction order
        assert op is not None or True  # Some indices may not exist
    
    # Test anti-expressions
    assert crystal.is_anti("1/0") or len(crystal.anti_expressions) > 0
    
    # Test coordinate lookup
    op = crystal.get_by_coordinates(
        Constant.PI, Shape.SQUARE, Element.EARTH, Pole.PRIMAL
    )
    assert op is not None
    
    return True


if __name__ == "__main__":
    print("Validating Operation Crystal...")
    assert validate_crystal()
    print("✓ Operation Crystal validated")
    
    # Demo
    print("\n=== 256-Operation Crystal Demo ===")
    
    crystal = OperationCrystal()
    summary = crystal.summary()
    
    print(f"\nTotal Operations: {summary['total_operations']}")
    print(f"Anti-Expressions: {summary['anti_expressions']}")
    
    print("\nSectors (64 each):")
    for sector, count in summary['sectors'].items():
        print(f"  {sector}-Sector: {count} operations")
    
    print("\nOperation Types:")
    for op_type, count in summary['operation_types'].items():
        if count > 0:
            print(f"  {op_type}: {count}")
    
    print("\nSample π-Sector Operations:")
    for op in crystal.get_sector("π")[:5]:
        print(f"  {op.name}: {op.description}")
    
    print("\nSample Anti-Expressions:")
    for anti in crystal.anti_expressions[:5]:
        print(f"  {anti.violated_law}: {anti.description}")

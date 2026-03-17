"""
ATHENA OS - AtlasForge
======================
Constraint Systems: Roots, Fixed Points, Lattice Families

From AtlasForge.docx:

CONSTRAINT TYPES:
    - Root: H(x) = 0
    - Fixed Point: x = F(x)
    - Equality: A = B → (A - B = 0)
    - Lattice: T(x_k) = θ + kΔ
    - Jet: derivatives/vectors

CONSTRAINT IR:
    Lowered to normal forms with compiled proof obligations:
    - Corridor (domain validity)
    - Enclosure (bounds)
    - Uniqueness/Contraction
    - Replay (reproducibility)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math

from .domains import Domain, Interval


# =============================================================================
# CONSTRAINT TYPES
# =============================================================================

class ConstraintType(Enum):
    """Types of constraints in AtlasForge."""
    
    ROOT = "root"                 # H(x) = 0
    FIXED_POINT = "fixed_point"   # x = F(x)
    EQUALITY = "equality"         # A = B
    LATTICE = "lattice"           # T(x_k) = θ + kΔ
    JET = "jet"                   # Derivative constraints
    VECTOR = "vector"             # H(x) = 0 for x ∈ ℝⁿ


class ObligationType(Enum):
    """Proof obligation types."""
    
    CORRIDOR = "corridor"         # Domain validity
    ENCLOSURE = "enclosure"       # Bounds on solution
    UNIQUENESS = "uniqueness"     # Solution uniqueness
    CONTRACTION = "contraction"   # Fixed point contraction
    REPLAY = "replay"             # Reproducibility
    EXISTENCE = "existence"       # Solution exists


# =============================================================================
# EXPRESSIONS
# =============================================================================

@dataclass
class Expression:
    """
    Mathematical expression for constraint definition.
    """
    
    # Expression type
    op: str = "var"               # Operation: var, const, add, sub, mul, div, sin, cos, exp, log, pow
    
    # Operands
    left: Optional['Expression'] = None
    right: Optional['Expression'] = None
    
    # Value for constants/variables
    value: Optional[float] = None
    name: Optional[str] = None
    
    def evaluate(self, bindings: Dict[str, float]) -> float:
        """Evaluate expression with variable bindings."""
        if self.op == "var":
            return bindings.get(self.name, 0.0)
        elif self.op == "const":
            return self.value
        elif self.op == "add":
            return self.left.evaluate(bindings) + self.right.evaluate(bindings)
        elif self.op == "sub":
            return self.left.evaluate(bindings) - self.right.evaluate(bindings)
        elif self.op == "mul":
            return self.left.evaluate(bindings) * self.right.evaluate(bindings)
        elif self.op == "div":
            r = self.right.evaluate(bindings)
            if abs(r) < 1e-15:
                return float('inf')
            return self.left.evaluate(bindings) / r
        elif self.op == "neg":
            return -self.left.evaluate(bindings)
        elif self.op == "sin":
            return math.sin(self.left.evaluate(bindings))
        elif self.op == "cos":
            return math.cos(self.left.evaluate(bindings))
        elif self.op == "exp":
            return math.exp(self.left.evaluate(bindings))
        elif self.op == "log":
            arg = self.left.evaluate(bindings)
            if arg <= 0:
                return float('-inf')
            return math.log(arg)
        elif self.op == "pow":
            base = self.left.evaluate(bindings)
            exp = self.right.evaluate(bindings)
            return base ** exp
        elif self.op == "sqrt":
            return math.sqrt(max(0, self.left.evaluate(bindings)))
        return 0.0
    
    def derivative(self, var: str) -> 'Expression':
        """Symbolic derivative with respect to variable."""
        if self.op == "var":
            if self.name == var:
                return Expression.constant(1.0)
            return Expression.constant(0.0)
        elif self.op == "const":
            return Expression.constant(0.0)
        elif self.op == "add":
            return Expression.add(
                self.left.derivative(var),
                self.right.derivative(var)
            )
        elif self.op == "sub":
            return Expression.sub(
                self.left.derivative(var),
                self.right.derivative(var)
            )
        elif self.op == "mul":
            # Product rule: (fg)' = f'g + fg'
            return Expression.add(
                Expression.mul(self.left.derivative(var), self.right),
                Expression.mul(self.left, self.right.derivative(var))
            )
        # Simplified for other ops
        return Expression.constant(0.0)
    
    @classmethod
    def variable(cls, name: str) -> 'Expression':
        return cls(op="var", name=name)
    
    @classmethod
    def constant(cls, value: float) -> 'Expression':
        return cls(op="const", value=value)
    
    @classmethod
    def add(cls, left: 'Expression', right: 'Expression') -> 'Expression':
        return cls(op="add", left=left, right=right)
    
    @classmethod
    def sub(cls, left: 'Expression', right: 'Expression') -> 'Expression':
        return cls(op="sub", left=left, right=right)
    
    @classmethod
    def mul(cls, left: 'Expression', right: 'Expression') -> 'Expression':
        return cls(op="mul", left=left, right=right)
    
    @classmethod
    def div(cls, left: 'Expression', right: 'Expression') -> 'Expression':
        return cls(op="div", left=left, right=right)
    
    @classmethod
    def sin(cls, arg: 'Expression') -> 'Expression':
        return cls(op="sin", left=arg)
    
    @classmethod
    def cos(cls, arg: 'Expression') -> 'Expression':
        return cls(op="cos", left=arg)
    
    @classmethod
    def exp(cls, arg: 'Expression') -> 'Expression':
        return cls(op="exp", left=arg)
    
    @classmethod
    def log(cls, arg: 'Expression') -> 'Expression':
        return cls(op="log", left=arg)


# =============================================================================
# CONSTRAINT BASE
# =============================================================================

@dataclass
class Constraint:
    """
    Base constraint specification.
    """
    
    name: str
    constraint_type: ConstraintType
    
    # Domain of constraint
    domain: Domain = None
    
    # Variable being solved for
    variable: str = "x"
    
    # Proof obligations
    obligations: Set[ObligationType] = field(default_factory=set)
    
    def add_obligation(self, obligation: ObligationType) -> None:
        """Add proof obligation."""
        self.obligations.add(obligation)
    
    def compile_obligations(self) -> List[ObligationType]:
        """Compile required proof obligations."""
        return list(self.obligations)


# =============================================================================
# ROOT CONSTRAINT
# =============================================================================

@dataclass
class RootConstraint(Constraint):
    """
    Root constraint: H(x) = 0
    
    Find x such that expression evaluates to zero.
    """
    
    expression: Expression = None
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.ROOT
        self.add_obligation(ObligationType.CORRIDOR)
        self.add_obligation(ObligationType.ENCLOSURE)
    
    def evaluate(self, x: float) -> float:
        """Evaluate H(x)."""
        if self.expression is None:
            return 0.0
        return self.expression.evaluate({self.variable: x})
    
    def is_root(self, x: float, tolerance: float = 1e-10) -> bool:
        """Check if x is a root within tolerance."""
        return abs(self.evaluate(x)) < tolerance
    
    def bracket(self, a: float, b: float) -> Optional[Tuple[float, float]]:
        """Check if [a, b] brackets a root (sign change)."""
        fa = self.evaluate(a)
        fb = self.evaluate(b)
        
        if fa * fb < 0:
            return (a, b)
        return None
    
    def bisection(self, a: float, b: float, 
                  tolerance: float = 1e-10,
                  max_iter: int = 100) -> Optional[float]:
        """Find root via bisection."""
        if self.bracket(a, b) is None:
            return None
        
        for _ in range(max_iter):
            mid = (a + b) / 2
            
            if abs(self.evaluate(mid)) < tolerance:
                return mid
            
            if self.evaluate(a) * self.evaluate(mid) < 0:
                b = mid
            else:
                a = mid
            
            if b - a < tolerance:
                return mid
        
        return (a + b) / 2


# =============================================================================
# FIXED POINT CONSTRAINT
# =============================================================================

@dataclass
class FixedPointConstraint(Constraint):
    """
    Fixed point constraint: x = F(x)
    
    Find x such that F(x) = x.
    """
    
    map_expression: Expression = None
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.FIXED_POINT
        self.add_obligation(ObligationType.CONTRACTION)
        self.add_obligation(ObligationType.EXISTENCE)
    
    def apply(self, x: float) -> float:
        """Apply F(x)."""
        if self.map_expression is None:
            return x
        return self.map_expression.evaluate({self.variable: x})
    
    def is_fixed_point(self, x: float, tolerance: float = 1e-10) -> bool:
        """Check if x is a fixed point."""
        return abs(self.apply(x) - x) < tolerance
    
    def contraction_factor(self, x: float, delta: float = 1e-6) -> float:
        """Estimate |F'(x)| (should be < 1 for contraction)."""
        fx = self.apply(x)
        fxd = self.apply(x + delta)
        return abs(fxd - fx) / delta
    
    def iterate(self, x0: float, 
                tolerance: float = 1e-10,
                max_iter: int = 100) -> Optional[float]:
        """Find fixed point via iteration."""
        x = x0
        
        for _ in range(max_iter):
            x_new = self.apply(x)
            
            if abs(x_new - x) < tolerance:
                return x_new
            
            x = x_new
        
        return x


# =============================================================================
# LATTICE CONSTRAINT
# =============================================================================

@dataclass
class LatticeConstraint(Constraint):
    """
    Lattice constraint: T(x_k) = θ + kΔ
    
    Family of points indexed by integer k.
    """
    
    # Chart transformation T
    chart: Expression = None
    
    # Parameters
    theta: float = 0.0       # Base value θ
    delta: float = 1.0       # Spacing Δ
    k_range: Tuple[int, int] = (0, 10)  # Range [k_min, k_max]
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.LATTICE
        self.add_obligation(ObligationType.CORRIDOR)
        self.add_obligation(ObligationType.REPLAY)
    
    @property
    def k_values(self) -> List[int]:
        """Get all k values in range."""
        return list(range(self.k_range[0], self.k_range[1] + 1))
    
    def target_value(self, k: int) -> float:
        """Compute target θ + kΔ."""
        return self.theta + k * self.delta
    
    def solve_for_k(self, k: int, 
                   initial_guess: float = 0.0,
                   tolerance: float = 1e-10) -> Optional[float]:
        """Solve T(x) = θ + kΔ for given k."""
        target = self.target_value(k)
        
        # Convert to root finding: T(x) - target = 0
        def f(x):
            if self.chart is None:
                return x - target
            return self.chart.evaluate({self.variable: x}) - target
        
        # Newton's method (simplified)
        x = initial_guess
        for _ in range(100):
            fx = f(x)
            if abs(fx) < tolerance:
                return x
            
            # Numerical derivative
            dx = 1e-8
            dfx = (f(x + dx) - fx) / dx
            
            if abs(dfx) < 1e-15:
                break
            
            x = x - fx / dfx
        
        return x
    
    def generate_family(self) -> List[Tuple[int, float]]:
        """Generate all (k, x_k) pairs."""
        family = []
        prev_x = 0.0
        
        for k in self.k_values:
            x_k = self.solve_for_k(k, initial_guess=prev_x)
            if x_k is not None:
                family.append((k, x_k))
                prev_x = x_k
        
        return family


# =============================================================================
# EQUALITY CONSTRAINT
# =============================================================================

@dataclass
class EqualityConstraint(Constraint):
    """
    Equality constraint: A = B
    
    Lowered to root constraint A - B = 0.
    """
    
    left_expr: Expression = None
    right_expr: Expression = None
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.EQUALITY
    
    def to_root(self) -> RootConstraint:
        """Lower to root constraint."""
        diff = Expression.sub(self.left_expr, self.right_expr)
        
        return RootConstraint(
            name=f"{self.name}_root",
            domain=self.domain,
            variable=self.variable,
            expression=diff
        )


# =============================================================================
# CONSTRAINT IR
# =============================================================================

@dataclass
class ConstraintIR:
    """
    Intermediate Representation for constraints.
    
    Normalized form after compilation.
    """
    
    # Original constraint
    source: Constraint
    
    # Normalized form
    normal_form: str = "root"  # root, fixed_point, generator
    
    # Compiled expression
    compiled_expr: Expression = None
    
    # Obligations
    obligations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Domain
    domain_spec: Dict[str, Any] = field(default_factory=dict)
    
    def add_obligation(self, obligation_type: ObligationType,
                      params: Dict[str, Any] = None) -> None:
        """Add obligation to IR."""
        self.obligations.append({
            "type": obligation_type.value,
            "params": params or {}
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.source.name,
            "normal_form": self.normal_form,
            "variable": self.source.variable,
            "obligations": self.obligations,
            "domain": self.domain_spec
        }


# =============================================================================
# CONSTRAINT COMPILER
# =============================================================================

@dataclass
class ConstraintCompiler:
    """
    Compiles constraints to IR with obligations.
    """
    
    def compile(self, constraint: Constraint) -> ConstraintIR:
        """Compile constraint to IR."""
        ir = ConstraintIR(source=constraint)
        
        # Set normal form based on type
        if constraint.constraint_type == ConstraintType.ROOT:
            ir.normal_form = "root"
            ir.compiled_expr = constraint.expression
        elif constraint.constraint_type == ConstraintType.FIXED_POINT:
            ir.normal_form = "fixed_point"
            ir.compiled_expr = constraint.map_expression
        elif constraint.constraint_type == ConstraintType.EQUALITY:
            # Lower to root
            root = constraint.to_root()
            ir.normal_form = "root"
            ir.compiled_expr = root.expression
        elif constraint.constraint_type == ConstraintType.LATTICE:
            ir.normal_form = "generator"
            ir.compiled_expr = constraint.chart
        
        # Compile obligations
        for obl in constraint.compile_obligations():
            ir.add_obligation(obl)
        
        # Set domain spec
        if constraint.domain is not None:
            ir.domain_spec = {
                "kind": constraint.domain.kind.value,
                "compact": constraint.domain.is_compact
            }
        
        return ir


# =============================================================================
# VALIDATION
# =============================================================================

def validate_constraints() -> bool:
    """Validate constraints module."""
    
    # Test Expression
    x = Expression.variable("x")
    const = Expression.constant(2.0)
    expr = Expression.sub(Expression.mul(x, x), const)
    
    assert abs(expr.evaluate({"x": 2.0}) - 2.0) < 1e-10  # 2² - 2 = 2
    assert abs(expr.evaluate({"x": 1.0}) - (-1.0)) < 1e-10  # 1² - 2 = -1
    
    # Test RootConstraint
    root = RootConstraint(
        name="sqrt2",
        expression=expr,
        domain=Domain.interval(0, 3)
    )
    
    # x² - 2 = 0 has root at √2
    x_star = root.bisection(1, 2)
    assert x_star is not None
    assert abs(x_star - math.sqrt(2)) < 1e-6
    assert root.is_root(x_star)
    
    # Test FixedPointConstraint
    # F(x) = cos(x) has fixed point near 0.739
    fp = FixedPointConstraint(
        name="cos_fp",
        map_expression=Expression.cos(Expression.variable("x"))
    )
    
    x_fp = fp.iterate(0.5)
    assert x_fp is not None
    assert abs(x_fp - math.cos(x_fp)) < 1e-6
    
    # Test LatticeConstraint
    # T(x) = x, θ = 0, Δ = 1 → x_k = k
    lattice = LatticeConstraint(
        name="identity_lattice",
        chart=Expression.variable("x"),
        theta=0.0,
        delta=1.0,
        k_range=(0, 5)
    )
    
    family = lattice.generate_family()
    assert len(family) == 6  # k = 0, 1, 2, 3, 4, 5
    
    # Test ConstraintCompiler
    compiler = ConstraintCompiler()
    ir = compiler.compile(root)
    assert ir.normal_form == "root"
    assert len(ir.obligations) >= 2
    
    return True


if __name__ == "__main__":
    print("Validating AtlasForge Constraints...")
    assert validate_constraints()
    print("✓ Constraints module validated")

"""
ATHENA OS - Mathematical Operations Crystal
==========================================
The four operation families from MATH_FUNDAMENTALS.docx

FOUR OPERATION FAMILIES:

Square ops: {=, -, ×, ÷}
    - Discrete/algebraic operations
    - F = G ⟺ Z(F-G) (zero set equivalence)
    - Closure under composition

Flower ops: {cos, sin, -sin, cos}
    - 90° shadow rotations
    - D[cos] = -sin, D[sin] = cos
    - Trigonometric identities

Cloud ops: {d/dt, ∫, F, M}
    - d/dt: differentiation (infinitesimal change)
    - ∫: integration (accumulation)
    - F: Fourier transform
    - M: Mellin transform

Fractal ops: {exp, log, pow, root}
    - Linear in ln-space
    - exp ∘ log = id (on appropriate domain)
    - pow(x,a)·pow(x,b) = pow(x,a+b)

OPERATION ALGEBRA:
Each family forms a closed algebra under composition
with well-defined domain/codomain tracking.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
import math
import cmath


# =============================================================================
# OPERATION FAMILIES
# =============================================================================

class OperationFamily(Enum):
    """The four operation families."""
    SQUARE = "square"    # {=, -, ×, ÷}
    FLOWER = "flower"    # {cos, sin, -sin, cos}
    CLOUD = "cloud"      # {d/dt, ∫, F, M}
    FRACTAL = "fractal"  # {exp, log, pow, root}
    
    @property
    def symbol(self) -> str:
        symbols = {
            OperationFamily.SQUARE: "□",
            OperationFamily.FLOWER: "❀",
            OperationFamily.CLOUD: "☁",
            OperationFamily.FRACTAL: "✶"
        }
        return symbols[self]


# =============================================================================
# SQUARE OPERATIONS
# =============================================================================

class SquareOp(Enum):
    """Square operations: {=, -, ×, ÷}."""
    EQUAL = "="      # Equality test
    MINUS = "-"      # Subtraction
    TIMES = "×"      # Multiplication
    DIVIDE = "÷"     # Division


@dataclass
class SquareOperator:
    """
    Square operator algebra.
    
    Core principle: F = G ⟺ Z(F-G) where Z is zero set.
    """
    
    @staticmethod
    def equal(a: complex, b: complex, tol: float = 1e-10) -> bool:
        """Test equality via zero set."""
        return abs(a - b) < tol
    
    @staticmethod
    def minus(a: complex, b: complex) -> complex:
        """Subtraction."""
        return a - b
    
    @staticmethod
    def times(a: complex, b: complex) -> complex:
        """Multiplication."""
        return a * b
    
    @staticmethod
    def divide(a: complex, b: complex) -> complex:
        """Division (with zero check)."""
        if abs(b) < 1e-15:
            raise ValueError("Division by zero")
        return a / b
    
    @staticmethod
    def apply(op: SquareOp, a: complex, b: complex) -> Union[bool, complex]:
        """Apply a square operation."""
        if op == SquareOp.EQUAL:
            return SquareOperator.equal(a, b)
        elif op == SquareOp.MINUS:
            return SquareOperator.minus(a, b)
        elif op == SquareOp.TIMES:
            return SquareOperator.times(a, b)
        elif op == SquareOp.DIVIDE:
            return SquareOperator.divide(a, b)
        raise ValueError(f"Unknown op: {op}")


# =============================================================================
# FLOWER OPERATIONS
# =============================================================================

class FlowerOp(Enum):
    """Flower operations: 90° shadow rotations."""
    COS = "cos"           # cos(x)
    SIN = "sin"           # sin(x)
    NEG_SIN = "-sin"      # -sin(x)
    NEG_COS = "-cos"      # -cos(x) (for completeness)


@dataclass
class FlowerOperator:
    """
    Flower operator algebra.
    
    90° shadow structure:
        D[cos] = -sin (shadow of cos)
        D[sin] = cos
        D[-sin] = -cos
        D[-cos] = sin
    """
    
    @staticmethod
    def cos(x: float) -> float:
        """Cosine."""
        return math.cos(x)
    
    @staticmethod
    def sin(x: float) -> float:
        """Sine."""
        return math.sin(x)
    
    @staticmethod
    def neg_sin(x: float) -> float:
        """Negative sine (-sin)."""
        return -math.sin(x)
    
    @staticmethod
    def neg_cos(x: float) -> float:
        """Negative cosine (-cos)."""
        return -math.cos(x)
    
    @staticmethod
    def apply(op: FlowerOp, x: float) -> float:
        """Apply a flower operation."""
        if op == FlowerOp.COS:
            return FlowerOperator.cos(x)
        elif op == FlowerOp.SIN:
            return FlowerOperator.sin(x)
        elif op == FlowerOp.NEG_SIN:
            return FlowerOperator.neg_sin(x)
        elif op == FlowerOp.NEG_COS:
            return FlowerOperator.neg_cos(x)
        raise ValueError(f"Unknown op: {op}")
    
    @staticmethod
    def derivative(op: FlowerOp) -> FlowerOp:
        """Get derivative (90° shadow)."""
        shadow_map = {
            FlowerOp.COS: FlowerOp.NEG_SIN,
            FlowerOp.SIN: FlowerOp.COS,
            FlowerOp.NEG_SIN: FlowerOp.NEG_COS,
            FlowerOp.NEG_COS: FlowerOp.SIN,
        }
        return shadow_map[op]
    
    @staticmethod
    def shadow_cycle() -> List[FlowerOp]:
        """Get the 90° shadow cycle."""
        return [FlowerOp.COS, FlowerOp.NEG_SIN, FlowerOp.NEG_COS, FlowerOp.SIN]


# =============================================================================
# CLOUD OPERATIONS
# =============================================================================

class CloudOp(Enum):
    """Cloud operations: infinitesimal/integral/transform."""
    DIFF = "d/dt"     # Differentiation
    INTEG = "∫"       # Integration
    FOURIER = "F"     # Fourier transform
    MELLIN = "M"      # Mellin transform


@dataclass
class CloudOperator:
    """
    Cloud operator algebra.
    
    D[e^{gt}] = g·e^{gt} (eigenlaw)
    F turns D into multiplication: F{f'} = iω·F{f}
    M turns scaling into shift: M{f(λx)} = λ^{-s}·M{f}
    """
    
    @staticmethod
    def differentiate(f: Callable[[float], float], 
                     x: float, h: float = 1e-8) -> float:
        """Numerical differentiation."""
        return (f(x + h) - f(x - h)) / (2 * h)
    
    @staticmethod
    def integrate(f: Callable[[float], float],
                 a: float, b: float, n: int = 1000) -> float:
        """Numerical integration (Simpson's rule)."""
        if n % 2 == 1:
            n += 1
        h = (b - a) / n
        x = [a + i * h for i in range(n + 1)]
        
        result = f(a) + f(b)
        for i in range(1, n):
            if i % 2 == 0:
                result += 2 * f(x[i])
            else:
                result += 4 * f(x[i])
        
        return result * h / 3
    
    @staticmethod
    def eigenlaw_coefficient(g: complex, t: float) -> complex:
        """
        Cloud eigenlaw: D[e^{gt}] = g·e^{gt}
        
        Returns the coefficient g.
        """
        return g
    
    @staticmethod
    def exp_eigenfunction(g: complex, t: float) -> complex:
        """Exponential eigenfunction e^{gt}."""
        return cmath.exp(g * t)


# =============================================================================
# FRACTAL OPERATIONS
# =============================================================================

class FractalOp(Enum):
    """Fractal operations: exp/log/pow/root."""
    EXP = "exp"       # Exponential
    LOG = "log"       # Logarithm
    POW = "pow"       # Power
    ROOT = "root"     # Root


@dataclass
class FractalOperator:
    """
    Fractal operator algebra.
    
    Linear in ln-space:
        log(a·b) = log(a) + log(b)
        log(a^n) = n·log(a)
        exp(log(a)) = a
    """
    
    @staticmethod
    def exp(x: complex) -> complex:
        """Exponential."""
        return cmath.exp(x)
    
    @staticmethod
    def log(x: complex) -> complex:
        """Logarithm (principal branch)."""
        if x == 0:
            raise ValueError("Log of zero")
        return cmath.log(x)
    
    @staticmethod
    def pow(base: complex, exponent: complex) -> complex:
        """Power: base^exponent."""
        if base == 0 and exponent.real > 0:
            return 0
        return cmath.exp(exponent * cmath.log(base))
    
    @staticmethod
    def root(x: complex, n: int) -> complex:
        """nth root (principal)."""
        if n == 0:
            raise ValueError("Zeroth root undefined")
        return FractalOperator.pow(x, 1.0 / n)
    
    @staticmethod
    def apply(op: FractalOp, x: complex, y: complex = None) -> complex:
        """Apply a fractal operation."""
        if op == FractalOp.EXP:
            return FractalOperator.exp(x)
        elif op == FractalOp.LOG:
            return FractalOperator.log(x)
        elif op == FractalOp.POW:
            return FractalOperator.pow(x, y or 2)
        elif op == FractalOp.ROOT:
            return FractalOperator.root(x, int(y or 2))
        raise ValueError(f"Unknown op: {op}")
    
    @staticmethod
    def log_linearity_check(a: complex, b: complex) -> bool:
        """Verify log(a·b) = log(a) + log(b)."""
        if a == 0 or b == 0:
            return True
        lhs = FractalOperator.log(a * b)
        rhs = FractalOperator.log(a) + FractalOperator.log(b)
        # Note: may differ by 2πi due to branch
        diff = abs(lhs - rhs)
        return diff < 1e-10 or abs(diff - 2*math.pi) < 1e-10


# =============================================================================
# OPERATION CRYSTAL
# =============================================================================

@dataclass
class OperationRecord:
    """Record of an operation application."""
    
    family: OperationFamily
    op_name: str
    inputs: List[Any]
    output: Any
    domain: str = "C"  # Domain declaration
    branch: str = "principal"  # Branch for complex ops
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "family": self.family.value,
            "op": self.op_name,
            "inputs": [str(x) for x in self.inputs],
            "output": str(self.output),
            "domain": self.domain,
            "branch": self.branch,
        }


@dataclass
class OperationCrystal:
    """
    The complete operation crystal.
    
    Manages all four operation families with domain tracking.
    """
    
    # Operators
    square: SquareOperator = field(default_factory=SquareOperator)
    flower: FlowerOperator = field(default_factory=FlowerOperator)
    cloud: CloudOperator = field(default_factory=CloudOperator)
    fractal: FractalOperator = field(default_factory=FractalOperator)
    
    # Audit trail
    history: List[OperationRecord] = field(default_factory=list)
    
    def apply_square(self, op: SquareOp, a: complex, b: complex) -> Any:
        """Apply square operation with recording."""
        result = SquareOperator.apply(op, a, b)
        self.history.append(OperationRecord(
            family=OperationFamily.SQUARE,
            op_name=op.value,
            inputs=[a, b],
            output=result
        ))
        return result
    
    def apply_flower(self, op: FlowerOp, x: float) -> float:
        """Apply flower operation with recording."""
        result = FlowerOperator.apply(op, x)
        self.history.append(OperationRecord(
            family=OperationFamily.FLOWER,
            op_name=op.value,
            inputs=[x],
            output=result
        ))
        return result
    
    def apply_fractal(self, op: FractalOp, x: complex, 
                     y: complex = None) -> complex:
        """Apply fractal operation with recording."""
        result = FractalOperator.apply(op, x, y)
        inputs = [x] if y is None else [x, y]
        self.history.append(OperationRecord(
            family=OperationFamily.FRACTAL,
            op_name=op.value,
            inputs=inputs,
            output=result,
            branch="principal"
        ))
        return result
    
    def differentiate(self, f: Callable, x: float) -> float:
        """Apply cloud differentiation."""
        result = CloudOperator.differentiate(f, x)
        self.history.append(OperationRecord(
            family=OperationFamily.CLOUD,
            op_name="d/dt",
            inputs=[f"f at {x}"],
            output=result
        ))
        return result
    
    def integrate(self, f: Callable, a: float, b: float) -> float:
        """Apply cloud integration."""
        result = CloudOperator.integrate(f, a, b)
        self.history.append(OperationRecord(
            family=OperationFamily.CLOUD,
            op_name="∫",
            inputs=[f"f from {a} to {b}"],
            output=result
        ))
        return result
    
    def clear_history(self) -> None:
        """Clear operation history."""
        self.history = []
    
    def summary(self) -> Dict[str, int]:
        """Get operation count by family."""
        counts = {f.value: 0 for f in OperationFamily}
        for record in self.history:
            counts[record.family.value] += 1
        return counts


# =============================================================================
# OPERATION IDENTITIES
# =============================================================================

@dataclass
class OperationIdentity:
    """A verifiable operation identity."""
    
    name: str
    family: OperationFamily
    statement: str
    verifier: Callable[[], bool]
    
    def verify(self) -> bool:
        """Verify the identity."""
        try:
            return self.verifier()
        except Exception:
            return False


def create_core_identities() -> List[OperationIdentity]:
    """Create core operation identities."""
    
    PI = math.pi
    E = math.e
    PHI = (1 + math.sqrt(5)) / 2
    
    identities = []
    
    # Square identities
    identities.append(OperationIdentity(
        name="Multiplicative Identity",
        family=OperationFamily.SQUARE,
        statement="a × 1 = a",
        verifier=lambda: abs(SquareOperator.times(3.14, 1) - 3.14) < 1e-10
    ))
    
    identities.append(OperationIdentity(
        name="Additive Inverse",
        family=OperationFamily.SQUARE,
        statement="a + (-a) = 0",
        verifier=lambda: abs(SquareOperator.minus(5, 5)) < 1e-10
    ))
    
    # Flower identities
    identities.append(OperationIdentity(
        name="Pythagorean Identity",
        family=OperationFamily.FLOWER,
        statement="cos²(x) + sin²(x) = 1",
        verifier=lambda: abs(
            FlowerOperator.cos(1.0)**2 + FlowerOperator.sin(1.0)**2 - 1
        ) < 1e-10
    ))
    
    identities.append(OperationIdentity(
        name="Shadow Derivative",
        family=OperationFamily.FLOWER,
        statement="D[cos] = -sin",
        verifier=lambda: FlowerOperator.derivative(FlowerOp.COS) == FlowerOp.NEG_SIN
    ))
    
    # Fractal identities
    identities.append(OperationIdentity(
        name="Exp-Log Inverse",
        family=OperationFamily.FRACTAL,
        statement="exp(log(a)) = a for a > 0",
        verifier=lambda: abs(
            FractalOperator.exp(FractalOperator.log(PI)) - PI
        ) < 1e-10
    ))
    
    identities.append(OperationIdentity(
        name="Log Multiplication",
        family=OperationFamily.FRACTAL,
        statement="log(a·b) = log(a) + log(b)",
        verifier=lambda: FractalOperator.log_linearity_check(E, PHI)
    ))
    
    # Cloud identities (eigenlaw)
    identities.append(OperationIdentity(
        name="Eigenlaw",
        family=OperationFamily.CLOUD,
        statement="D[e^{gt}] = g·e^{gt}",
        verifier=lambda: abs(
            CloudOperator.differentiate(
                lambda t: cmath.exp(2*t).real, 0
            ) - 2.0
        ) < 1e-6
    ))
    
    return identities


# Global identities
CORE_IDENTITIES = create_core_identities()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operations() -> bool:
    """Validate operations module."""
    
    # Test Square
    assert SquareOperator.equal(1.0, 1.0)
    assert not SquareOperator.equal(1.0, 2.0)
    assert abs(SquareOperator.times(2, 3) - 6) < 1e-10
    
    # Test Flower
    assert abs(FlowerOperator.cos(0) - 1.0) < 1e-10
    assert abs(FlowerOperator.sin(math.pi/2) - 1.0) < 1e-10
    assert FlowerOperator.derivative(FlowerOp.COS) == FlowerOp.NEG_SIN
    
    # Test Fractal
    assert abs(FractalOperator.exp(0) - 1.0) < 1e-10
    assert abs(FractalOperator.log(math.e) - 1.0) < 1e-10
    assert FractalOperator.log_linearity_check(2.0, 3.0)
    
    # Test Cloud
    f = lambda x: x**2
    assert abs(CloudOperator.differentiate(f, 2.0) - 4.0) < 1e-6
    assert abs(CloudOperator.integrate(f, 0, 1) - 1/3) < 1e-6
    
    # Test OperationCrystal
    crystal = OperationCrystal()
    crystal.apply_square(SquareOp.TIMES, 2, 3)
    crystal.apply_flower(FlowerOp.SIN, 0)
    crystal.apply_fractal(FractalOp.EXP, 1)
    assert len(crystal.history) == 3
    
    # Test identities
    for identity in CORE_IDENTITIES:
        assert identity.verify(), f"Identity failed: {identity.name}"
    
    return True


if __name__ == "__main__":
    print("Validating Operations Module...")
    assert validate_operations()
    print("✓ Operations Module validated")
    
    # Demo
    print("\n=== Operation Crystal Demo ===")
    
    print("\nFour Operation Families:")
    for family in OperationFamily:
        print(f"  {family.symbol} {family.value}")
        if family == OperationFamily.SQUARE:
            print("    Ops: {=, -, ×, ÷}")
        elif family == OperationFamily.FLOWER:
            print("    Ops: {cos, sin, -sin, -cos}")
        elif family == OperationFamily.CLOUD:
            print("    Ops: {d/dt, ∫, F, M}")
        elif family == OperationFamily.FRACTAL:
            print("    Ops: {exp, log, pow, root}")
    
    print("\n90° Shadow Cycle (Flower):")
    for i, op in enumerate(FlowerOperator.shadow_cycle()):
        print(f"  {i*90}°: {op.value}")
    
    print("\nCore Identity Verification:")
    for identity in CORE_IDENTITIES:
        status = "✓" if identity.verify() else "✗"
        print(f"  {status} {identity.name}: {identity.statement}")
    
    print("\nOperation Crystal Usage:")
    crystal = OperationCrystal()
    
    # Square
    result = crystal.apply_square(SquareOp.TIMES, 3, 4)
    print(f"  3 × 4 = {result}")
    
    # Flower
    result = crystal.apply_flower(FlowerOp.SIN, math.pi/6)
    print(f"  sin(π/6) = {result:.6f}")
    
    # Fractal
    result = crystal.apply_fractal(FractalOp.LOG, math.e)
    print(f"  log(e) = {result:.6f}")
    
    print(f"\nOperations performed: {crystal.summary()}")

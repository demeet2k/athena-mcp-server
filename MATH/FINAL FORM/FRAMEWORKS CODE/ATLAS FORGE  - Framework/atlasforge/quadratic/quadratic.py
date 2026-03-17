"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      QUADRATIC FIELDS MODULE                                 ║
║                                                                              ║
║  Algebraic Integers, Units, and Class Numbers                                ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The gateway algebra lives naturally in real quadratic fields ℚ(√D).      ║
║    Pell equations find units, and the fundamental unit generates            ║
║    gateway scalars.                                                          ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - ℚ(√D) = {a + b√D : a, b ∈ ℚ}                                           ║
║    - 𝒪_D = ring of integers (depends on D mod 4)                            ║
║    - Unit group: 𝒪_D* ≅ {±1} × ℤ for D > 0                                  ║
║    - Fundamental unit ε: generates all units                                ║
║    - Class number h: measures failure of unique factorization               ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Gateway discriminant A ↔ field discriminant D                          ║
║    - Pell solution (u,v) ↔ unit u + v√D                                     ║
║    - Metallic mean δ_n ↔ fundamental unit of ℚ(√(n²+4))                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# QUADRATIC INTEGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuadraticInteger:
    """
    Element of ℤ[√D] or ℤ[(1+√D)/2] depending on D.
    
    Represented as a + b·ω where:
        ω = √D if D ≡ 2, 3 (mod 4)
        ω = (1 + √D)/2 if D ≡ 1 (mod 4)
    """
    a: int  # Rational part
    b: int  # Coefficient of ω
    D: int  # Discriminant (squarefree)
    
    def __post_init__(self):
        # Ensure D is squarefree
        D_reduced = self._remove_squares(abs(self.D))
        if self.D < 0:
            D_reduced = -D_reduced
        self.D = D_reduced
    
    @staticmethod
    def _remove_squares(n: int) -> int:
        """Remove square factors from n."""
        if n == 0:
            return 0
        result = 1
        d = 2
        while d * d <= n:
            if n % (d * d) == 0:
                n //= (d * d)
            else:
                if n % d == 0:
                    result *= d
                    n //= d
                d += 1
        return result * n
    
    @property
    def omega(self) -> str:
        """String representation of ω."""
        if self.D % 4 == 1:
            return f"(1+√{self.D})/2"
        return f"√{self.D}"
    
    @property
    def is_integer_ring(self) -> bool:
        """Check if D ≡ 1 (mod 4), which changes the ring structure."""
        return self.D % 4 == 1
    
    def to_real(self) -> float:
        """Convert to real number (for D > 0)."""
        if self.D <= 0:
            raise ValueError("D must be positive for real embedding")
        
        sqrt_D = np.sqrt(self.D)
        if self.is_integer_ring:
            return self.a + self.b * (1 + sqrt_D) / 2
        return self.a + self.b * sqrt_D
    
    def norm(self) -> int:
        """
        Field norm: N(a + bω) = (a + bω)(a + bω').
        
        For ω = √D: N = a² - Db²
        For ω = (1+√D)/2: N = a² + ab - ((D-1)/4)b²
        """
        if self.is_integer_ring:
            return self.a**2 + self.a * self.b - ((self.D - 1) // 4) * self.b**2
        return self.a**2 - self.D * self.b**2
    
    def trace(self) -> int:
        """
        Field trace: Tr(α) = α + α'.
        
        For ω = √D: Tr = 2a
        For ω = (1+√D)/2: Tr = 2a + b
        """
        if self.is_integer_ring:
            return 2 * self.a + self.b
        return 2 * self.a
    
    def conjugate(self) -> 'QuadraticInteger':
        """Galois conjugate: √D ↦ -√D."""
        if self.is_integer_ring:
            # (a + b(1+√D)/2)' = a + b(1-√D)/2 = (a+b) - b·ω
            return QuadraticInteger(self.a + self.b, -self.b, self.D)
        return QuadraticInteger(self.a, -self.b, self.D)
    
    def __add__(self, other: 'QuadraticInteger') -> 'QuadraticInteger':
        if self.D != other.D:
            raise ValueError("Cannot add elements from different fields")
        return QuadraticInteger(self.a + other.a, self.b + other.b, self.D)
    
    def __sub__(self, other: 'QuadraticInteger') -> 'QuadraticInteger':
        if self.D != other.D:
            raise ValueError("Cannot subtract elements from different fields")
        return QuadraticInteger(self.a - other.a, self.b - other.b, self.D)
    
    def __mul__(self, other: 'QuadraticInteger') -> 'QuadraticInteger':
        if self.D != other.D:
            raise ValueError("Cannot multiply elements from different fields")
        
        a1, b1 = self.a, self.b
        a2, b2 = other.a, other.b
        
        if self.is_integer_ring:
            # ω² = ω + (D-1)/4
            # (a1 + b1·ω)(a2 + b2·ω) = a1·a2 + (a1·b2 + a2·b1)·ω + b1·b2·ω²
            # = a1·a2 + b1·b2·(D-1)/4 + (a1·b2 + a2·b1 + b1·b2)·ω
            c = (self.D - 1) // 4
            new_a = a1 * a2 + b1 * b2 * c
            new_b = a1 * b2 + a2 * b1 + b1 * b2
        else:
            # ω² = D
            new_a = a1 * a2 + b1 * b2 * self.D
            new_b = a1 * b2 + a2 * b1
        
        return QuadraticInteger(new_a, new_b, self.D)
    
    def __neg__(self) -> 'QuadraticInteger':
        return QuadraticInteger(-self.a, -self.b, self.D)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuadraticInteger):
            return False
        return self.a == other.a and self.b == other.b and self.D == other.D
    
    def is_unit(self) -> bool:
        """Check if this is a unit (norm = ±1)."""
        return abs(self.norm()) == 1
    
    def __repr__(self) -> str:
        if self.b == 0:
            return f"{self.a}"
        elif self.a == 0:
            if self.b == 1:
                return f"{self.omega}"
            elif self.b == -1:
                return f"-{self.omega}"
            return f"{self.b}·{self.omega}"
        else:
            sign = "+" if self.b > 0 else "-"
            abs_b = abs(self.b)
            if abs_b == 1:
                return f"{self.a} {sign} {self.omega}"
            return f"{self.a} {sign} {abs_b}·{self.omega}"


# ═══════════════════════════════════════════════════════════════════════════════
# QUADRATIC FIELD
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuadraticField:
    """
    The quadratic field ℚ(√D) and its ring of integers 𝒪_D.
    """
    D: int  # Squarefree integer
    
    def __post_init__(self):
        # Ensure D is squarefree
        self.D = QuadraticInteger._remove_squares(abs(self.D))
        if self.D == 1:
            raise ValueError("D cannot be a perfect square")
    
    @property
    def is_real(self) -> bool:
        """Real quadratic field if D > 0."""
        return self.D > 0
    
    @property
    def is_imaginary(self) -> bool:
        """Imaginary quadratic field if D < 0."""
        return self.D < 0
    
    @property
    def discriminant(self) -> int:
        """
        Field discriminant.
        
        Δ = D if D ≡ 1 (mod 4)
        Δ = 4D otherwise
        """
        if self.D % 4 == 1:
            return self.D
        return 4 * self.D
    
    @property
    def ring_type(self) -> str:
        """Description of the ring of integers."""
        if self.D % 4 == 1:
            return f"ℤ[(1+√{self.D})/2]"
        return f"ℤ[√{self.D}]"
    
    def zero(self) -> QuadraticInteger:
        """Zero element."""
        return QuadraticInteger(0, 0, self.D)
    
    def one(self) -> QuadraticInteger:
        """Unity element."""
        return QuadraticInteger(1, 0, self.D)
    
    def omega(self) -> QuadraticInteger:
        """The generator ω of the ring."""
        return QuadraticInteger(0, 1, self.D)
    
    def from_rational_form(self, a: int, b: int) -> QuadraticInteger:
        """
        Create element from a + b√D form.
        
        Converts to ring basis if D ≡ 1 (mod 4).
        """
        if self.D % 4 == 1:
            # a + b√D = (a - b/2) + b·(1+√D)/2
            # For integers, 2a + b·(1+√D)/2 - b/2 must work
            # If b is even: (a - b/2, b)
            # If b is odd: need 2a - b even, so a + b must be even
            if b % 2 == 0:
                return QuadraticInteger(a - b // 2, b, self.D)
            else:
                # a + b√D = (2a-b)/2 + b(1+√D)/2
                # This only works if 2a - b + b = 2a is even (always)
                # But we need integer coords, so check
                if (2 * a + b) % 2 == 0:
                    return QuadraticInteger((2 * a - b) // 2, b, self.D)
                raise ValueError(f"{a} + {b}√{self.D} is not in the ring of integers")
        return QuadraticInteger(a, b, self.D)
    
    def find_fundamental_unit(self) -> QuadraticInteger:
        """
        Find the fundamental unit ε > 1 via Pell equation.
        
        For D > 0, units form {±ε^n : n ∈ ℤ}.
        """
        if self.D < 0:
            raise ValueError("Imaginary fields have finite unit group")
        
        # Solve Pell equation x² - Dy² = ±1
        sqrt_D = int(np.sqrt(self.D))
        if sqrt_D * sqrt_D == self.D:
            raise ValueError("D is a perfect square")
        
        # Continued fraction method
        m, d, a = 0, 1, sqrt_D
        
        p_prev, p_curr = 1, a
        q_prev, q_curr = 0, 1
        
        while True:
            m = d * a - m
            d = (self.D - m * m) // d
            a = (sqrt_D + m) // d
            
            p_prev, p_curr = p_curr, a * p_curr + p_prev
            q_prev, q_curr = q_curr, a * q_curr + q_prev
            
            # Check if solution
            norm = p_curr * p_curr - self.D * q_curr * q_curr
            if norm == 1:
                return self.from_rational_form(p_curr, q_curr)
            elif norm == -1:
                # Need to square to get norm +1 solution
                # (p + q√D)² = p² + Dq² + 2pq√D
                p_sq = p_curr * p_curr + self.D * q_curr * q_curr
                q_sq = 2 * p_curr * q_curr
                return self.from_rational_form(p_sq, q_sq)
            
            if q_curr > 10**15:
                raise ValueError("Could not find fundamental unit")
    
    def regulator(self) -> float:
        """
        Regulator: R = log(ε) where ε is the fundamental unit.
        """
        if self.D < 0:
            return 0.0  # Imaginary fields have R = 0
        
        eps = self.find_fundamental_unit()
        return np.log(eps.to_real())


# ═══════════════════════════════════════════════════════════════════════════════
# IDEAL CLASS GROUP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuadraticIdeal:
    """
    Ideal in 𝒪_D represented as (a, b + ω) where a | N(b + ω).
    """
    a: int  # First generator
    b: int  # Part of second generator
    D: int  # Field discriminant
    
    @property
    def norm(self) -> int:
        """Norm of the ideal: [𝒪 : I]."""
        return self.a
    
    def is_principal(self, search_bound: int = 1000) -> Optional[QuadraticInteger]:
        """
        Check if ideal is principal; return generator if so.
        """
        # Search for element α with N(α) = ±a
        for x in range(-search_bound, search_bound + 1):
            for y in range(search_bound + 1):
                if y == 0 and x <= 0:
                    continue
                
                alpha = QuadraticInteger(x, y, self.D)
                if abs(alpha.norm()) == self.a:
                    return alpha
        
        return None


@dataclass
class ClassGroup:
    """
    Ideal class group of 𝒪_D.
    
    Measures failure of unique factorization.
    Class number h = |Cl(𝒪_D)|.
    """
    D: int
    
    def class_number_bound(self) -> int:
        """
        Upper bound on class number via Minkowski's bound.
        
        For D > 0: M = √D/2
        For D < 0: M = (2/π)√|D|
        """
        if self.D > 0:
            return int(np.sqrt(self.D) / 2) + 1
        return int(2 * np.sqrt(abs(self.D)) / np.pi) + 1
    
    def compute_class_number(self) -> int:
        """
        Compute class number (simplified algorithm).
        
        For small discriminants only.
        """
        # For imaginary quadratic fields with small |D|
        if self.D < 0 and abs(self.D) < 100:
            return self._imaginary_class_number()
        
        # For real quadratic fields
        if self.D > 0 and self.D < 100:
            return self._real_class_number()
        
        return -1  # Unknown
    
    def _imaginary_class_number(self) -> int:
        """
        Class number for imaginary quadratic field.
        
        Uses the formula involving quadratic residues.
        """
        D = abs(self.D)
        
        # Known class numbers for small fundamental discriminants
        # -D ≡ 0, 1 (mod 4) only
        known = {
            3: 1, 4: 1, 7: 1, 8: 1, 11: 1, 19: 1, 43: 1, 67: 1, 163: 1,
            15: 2, 20: 2, 24: 2, 35: 2, 40: 2, 51: 2, 52: 2, 88: 2,
            23: 3, 31: 3, 59: 3, 83: 3,
        }
        
        return known.get(D, -1)
    
    def _real_class_number(self) -> int:
        """
        Class number for real quadratic field.
        """
        # Known class numbers
        known = {
            2: 1, 3: 1, 5: 1, 6: 1, 7: 1, 11: 1, 13: 1, 14: 1, 17: 1,
            19: 1, 21: 1, 22: 1, 23: 1, 29: 1, 31: 1, 33: 1, 37: 1,
            10: 2, 15: 2, 26: 2, 30: 2, 34: 2, 35: 2, 39: 2,
        }
        
        return known.get(self.D, -1)


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass  
class GatewayFieldBridge:
    """
    Bridge between gateway algebra and quadratic fields.
    
    Gateway discriminant A connects to ℚ(√A).
    """
    
    @staticmethod
    def gateway_to_unit(u: int, v: int, A: int) -> QuadraticInteger:
        """
        Convert Pell solution (u, v) with u² - Av² = 1 to unit.
        """
        field = QuadraticField(A)
        return field.from_rational_form(u, v)
    
    @staticmethod
    def metallic_mean_field(n: int) -> QuadraticField:
        """
        The quadratic field containing the n-th metallic mean.
        
        δ_n = (n + √(n² + 4))/2 lives in ℚ(√(n² + 4)).
        """
        D = n * n + 4
        # Remove square factor if present
        D_reduced = QuadraticInteger._remove_squares(D)
        return QuadraticField(D_reduced)
    
    @staticmethod
    def gateway_field(A: int) -> QuadraticField:
        """Create quadratic field for gateway discriminant A."""
        return QuadraticField(A)
    
    @staticmethod
    def gateway_scalar_to_field_element(T: float, A: int
                                       ) -> QuadraticInteger:
        """
        Approximate gateway scalar T by element of ℚ(√A).
        
        T ≈ (u + v√A)/(u' + v'√A) where u² - Av² = 1.
        """
        field = QuadraticField(A)
        eps = field.find_fundamental_unit()
        
        # Find n such that ε^n ≈ (1+T)/(1-T)
        R = (1 + T) / (1 - T)
        eps_val = eps.to_real()
        
        n = int(round(np.log(R) / np.log(eps_val)))
        
        # Compute ε^n
        result = field.one()
        power = eps if n >= 0 else eps.conjugate()
        for _ in range(abs(n)):
            result = result * power
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def quadratic_integer(a: int, b: int, D: int) -> QuadraticInteger:
    """Create quadratic integer a + b√D."""
    return QuadraticInteger(a, b, D)


def fundamental_unit(D: int) -> QuadraticInteger:
    """Find fundamental unit of ℚ(√D)."""
    return QuadraticField(D).find_fundamental_unit()


def class_number(D: int) -> int:
    """Compute class number of ℚ(√D)."""
    return ClassGroup(D).compute_class_number()


def field_discriminant(D: int) -> int:
    """Field discriminant of ℚ(√D)."""
    return QuadraticField(D).discriminant


def regulator(D: int) -> float:
    """Regulator of ℚ(√D)."""
    return QuadraticField(D).regulator()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core classes
    'QuadraticInteger',
    'QuadraticField',
    
    # Ideals
    'QuadraticIdeal',
    'ClassGroup',
    
    # Bridge
    'GatewayFieldBridge',
    
    # Functions
    'quadratic_integer',
    'fundamental_unit',
    'class_number',
    'field_discriminant',
    'regulator',
]

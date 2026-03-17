"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OA6 OPERATOR WORD ALGEBRA MODULE                          ║
║                                                                              ║
║  The Universal Operator Calculus for Translation and Transport               ║
║                                                                              ║
║  Six Generators:                                                             ║
║    C - Complement (inversion): f(x) ↦ f(1/x), involutive                    ║
║    R - Rotation (Fourier quarter-turn): R⁴ = I                               ║
║    G - Gateway (Möbius boost): scale transport between boundary charts       ║
║    K - Kernel projector: Paley-Wiener spectral cut, idempotent               ║
║    S - Dilation: f(x) ↦ f(e^λ x), bandwidth scaling                          ║
║    T - Temperley-Lieb idempotent: T² = δT, categorical closure               ║
║                                                                              ║
║  Carrier Space: ℋ = L²(ℝ₊, dx/x) (multiplicative Hilbert space)             ║
║                                                                              ║
║  Normal Forms: Modular reduction via PSL(2,ℤ) + bandwidth bookkeeping        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Union, Callable, Any
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
from numpy.typing import NDArray
import math


# ═══════════════════════════════════════════════════════════════════════════════
# OA6 GENERATOR TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class OA6GeneratorType(Enum):
    """The six generators of OA6."""
    C = "complement"      # Inversion: f(x) ↦ f(1/x)
    R = "rotation"        # Fourier quarter-turn
    G = "gateway"         # Möbius boost
    K = "kernel"          # Paley-Wiener projector
    S = "dilation"        # Scaling: f(x) ↦ f(e^λ x)
    T = "temperley_lieb"  # TL idempotent


# ═══════════════════════════════════════════════════════════════════════════════
# FOLD INDEX - BANDWIDTH PARAMETER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FoldIndex:
    """
    Fold index κ with associated bandwidth τ_κ = π/(2√κ).
    
    The fold index tracks the Paley-Wiener bandwidth slice:
        κ determines τ_κ
        κ_n = 2^n gives canonical fold ladder
    """
    kappa: float
    
    def __post_init__(self):
        if self.kappa <= 0:
            raise ValueError(f"Fold index must be positive, got {self.kappa}")
    
    @property
    def bandwidth(self) -> float:
        """τ_κ = π/(2√κ), Mellin half-bandwidth."""
        return np.pi / (2 * np.sqrt(self.kappa))
    
    @property
    def tau(self) -> float:
        """Alias for bandwidth."""
        return self.bandwidth
    
    @classmethod
    def from_bandwidth(cls, tau: float) -> 'FoldIndex':
        """Create from bandwidth τ."""
        if tau <= 0:
            raise ValueError(f"Bandwidth must be positive, got {tau}")
        kappa = (np.pi / (2 * tau)) ** 2
        return cls(kappa=kappa)
    
    @classmethod
    def ladder_level(cls, n: int, base: float = 1.0) -> 'FoldIndex':
        """κ_n = base · 2^n."""
        return cls(kappa=base * (2 ** n))
    
    def dilate(self, lambda_: float) -> 'FoldIndex':
        """
        Apply dilation S_λ: κ → e^{2λ}κ.
        Corresponds to bandwidth scaling τ → e^{-λ}τ.
        """
        return FoldIndex(kappa=self.kappa * np.exp(2 * lambda_))
    
    def fold_step(self, direction: int = 1) -> 'FoldIndex':
        """
        Canonical fold step: κ → 2κ (direction=1) or κ → κ/2 (direction=-1).
        """
        return FoldIndex(kappa=self.kappa * (2 ** direction))
    
    def __repr__(self) -> str:
        return f"FoldIndex(κ={self.kappa:.4f}, τ={self.bandwidth:.4f})"


# ═══════════════════════════════════════════════════════════════════════════════
# OA6 GENERATOR BASE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OA6Generator(ABC):
    """Base class for OA6 generators."""
    generator_type: OA6GeneratorType
    
    @abstractmethod
    def matrix_2x2(self) -> Optional[NDArray[np.float64]]:
        """
        2×2 matrix representation in SL(2,ℝ) or SL(2,ℤ).
        Returns None if generator is not representable as 2×2 matrix.
        """
        pass
    
    @abstractmethod
    def kernel_effect(self, kappa: float) -> float:
        """
        Effect on fold index: κ → κ'.
        Returns new fold index.
        """
        pass
    
    @abstractmethod
    def is_invertible(self) -> bool:
        """Whether generator is invertible (unitary/unimodular)."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.generator_type.name}"


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLEMENT GENERATOR (C)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ComplementGenerator(OA6Generator):
    """
    Complement C: f(x) ↦ f(1/x).
    
    Properties:
        - C² = I (involutive)
        - In log coordinates: f̃(u) ↦ f̃(-u)
        - In Mellin frequency: f̂(k) ↦ f̂(-k)
        - Preserves fold index: κ' = κ
        - Unitary
    """
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.C, init=False)
    
    def matrix_2x2(self) -> NDArray[np.float64]:
        """
        C corresponds to z ↦ 1/z in projective action.
        Matrix representation: [[0, 1], [1, 0]]
        """
        return np.array([[0, 1], [1, 0]], dtype=np.float64)
    
    def kernel_effect(self, kappa: float) -> float:
        """C preserves κ."""
        return kappa
    
    def is_invertible(self) -> bool:
        return True
    
    def apply_to_array(self, x: NDArray[np.float64]) -> NDArray[np.float64]:
        """Apply complement to array: x ↦ 1/x (elementwise)."""
        return 1.0 / x
    
    def compose_with_self(self) -> 'IdentityGenerator':
        """C² = I."""
        return IdentityGenerator()


# ═══════════════════════════════════════════════════════════════════════════════
# ROTATION GENERATOR (R)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RotationGenerator(OA6Generator):
    """
    Rotation R: Mellin/Fourier quarter-turn.
    
    Properties:
        - R⁴ = I
        - Symplectic rotation: (u,p) ↦ (-p,u)
        - Preserves fold index: κ' = κ
        - Unitary
    """
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.R, init=False)
    
    def matrix_2x2(self) -> NDArray[np.float64]:
        """
        R in symplectic form: [[0, -1], [1, 0]]
        """
        return np.array([[0, -1], [1, 0]], dtype=np.float64)
    
    def kernel_effect(self, kappa: float) -> float:
        """R preserves κ."""
        return kappa
    
    def is_invertible(self) -> bool:
        return True
    
    def power(self, n: int) -> 'OA6Generator':
        """R^n (mod 4)."""
        n = n % 4
        if n == 0:
            return IdentityGenerator()
        elif n == 1:
            return self
        elif n == 2:
            # R² = -I (in PSL₂ sense, equivalent to I)
            return RotationSquaredGenerator()
        else:  # n == 3
            return RotationCubedGenerator()


@dataclass
class RotationSquaredGenerator(OA6Generator):
    """R² = rotation by π."""
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.R, init=False)
    
    def matrix_2x2(self) -> NDArray[np.float64]:
        return np.array([[-1, 0], [0, -1]], dtype=np.float64)
    
    def kernel_effect(self, kappa: float) -> float:
        return kappa
    
    def is_invertible(self) -> bool:
        return True


@dataclass
class RotationCubedGenerator(OA6Generator):
    """R³ = R⁻¹."""
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.R, init=False)
    
    def matrix_2x2(self) -> NDArray[np.float64]:
        return np.array([[0, 1], [-1, 0]], dtype=np.float64)
    
    def kernel_effect(self, kappa: float) -> float:
        return kappa
    
    def is_invertible(self) -> bool:
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY GENERATOR (G)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayGenerator(OA6Generator):
    """
    Gateway G: Möbius boost / symplectic shear.
    
    Properties:
        - Parametrized by (u, v, A) where u² - Av² = 1 (Pell)
        - Matrix: [[u, v], [Av, u]] ∈ SL(2,ℤ)
        - Transports boundary charts
        - Changes fold index according to certificate
    """
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.G, init=False)
    u: int = 1
    v: int = 1
    discriminant: int = 0  # A
    
    def __post_init__(self):
        # For integer gateway, verify Pell condition
        if self.discriminant > 0:
            residual = self.u**2 - self.discriminant * self.v**2
            if residual != 1:
                raise ValueError(f"Pell condition violated: {self.u}² - {self.discriminant}·{self.v}² = {residual}")
    
    def matrix_2x2(self) -> NDArray[np.int64]:
        """G = [[u, v], [Av, u]]."""
        return np.array([
            [self.u, self.v],
            [self.discriminant * self.v, self.u]
        ], dtype=np.int64)
    
    def kernel_effect(self, kappa: float) -> float:
        """
        G transports κ according to the specific gateway instance.
        The exact effect depends on the boundary chart transport.
        """
        # Simplified: scale by eigenvalue ratio squared
        lambda_plus = self.u + self.v * np.sqrt(self.discriminant)
        return kappa * lambda_plus ** 2
    
    def is_invertible(self) -> bool:
        return True
    
    def inverse(self) -> 'GatewayGenerator':
        """G⁻¹ = [[u, -v], [-Av, u]]."""
        return GatewayGenerator(u=self.u, v=-self.v, discriminant=self.discriminant)
    
    @classmethod
    def identity(cls) -> 'GatewayGenerator':
        """Identity gateway (trivial Pell solution)."""
        return cls(u=1, v=0, discriminant=0)
    
    @classmethod
    def simple_shear(cls, n: int = 1) -> 'GatewayGenerator':
        """
        Simple shear: [[1, n], [0, 1]].
        This is the standard generator g of PSL(2,Z).
        """
        # Not a Pell gateway in general, but standard PSL₂(ℤ) generator
        return cls(u=1, v=n, discriminant=0)


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL PROJECTOR (K)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KernelProjector(OA6Generator):
    """
    Kernel projector K_τ: Paley-Wiener spectral cut.
    
    Properties:
        - K_τ² = K_τ (idempotent)
        - K_τ = K_τ† (self-adjoint)
        - Projects onto PW_τ = {f : supp(f̂) ⊆ [-τ, τ]}
        - Non-invertible (rank deficient in general)
    """
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.K, init=False)
    fold_index: FoldIndex = field(default_factory=lambda: FoldIndex(kappa=1.0))
    
    @property
    def tau(self) -> float:
        """Bandwidth parameter."""
        return self.fold_index.bandwidth
    
    @property
    def kappa(self) -> float:
        """Fold index."""
        return self.fold_index.kappa
    
    def matrix_2x2(self) -> None:
        """K is not representable as 2×2 matrix."""
        return None
    
    def kernel_effect(self, kappa: float) -> float:
        """K_κ projects to κ-slice."""
        return self.fold_index.kappa
    
    def is_invertible(self) -> bool:
        return False  # Projector is not invertible
    
    def compose_with_self(self) -> 'KernelProjector':
        """K² = K (idempotent)."""
        return self
    
    @classmethod
    def from_bandwidth(cls, tau: float) -> 'KernelProjector':
        """Create projector from bandwidth."""
        return cls(fold_index=FoldIndex.from_bandwidth(tau))
    
    @classmethod
    def at_fold_level(cls, n: int) -> 'KernelProjector':
        """Create projector at fold ladder level n."""
        return cls(fold_index=FoldIndex.ladder_level(n))


# ═══════════════════════════════════════════════════════════════════════════════
# DILATION GENERATOR (S)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DilationGenerator(OA6Generator):
    """
    Dilation S_λ: f(x) ↦ f(e^λ x).
    
    Properties:
        - S_λ S_μ = S_{λ+μ} (one-parameter group)
        - S_0 = I
        - In log coordinates: f̃(u) ↦ f̃(u + λ)
        - Kernel effect: κ → e^{2λ}κ
        - Unitary
    """
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.S, init=False)
    lambda_: float = 0.0
    
    def matrix_2x2(self) -> NDArray[np.float64]:
        """
        S_λ as diagonal scaling: [[e^{λ/2}, 0], [0, e^{-λ/2}]].
        (Normalization for SL(2,ℝ).)
        """
        scale = np.exp(self.lambda_ / 2)
        return np.array([
            [scale, 0],
            [0, 1/scale]
        ], dtype=np.float64)
    
    def kernel_effect(self, kappa: float) -> float:
        """S_λ: κ → e^{2λ}κ."""
        return kappa * np.exp(2 * self.lambda_)
    
    def is_invertible(self) -> bool:
        return True
    
    def inverse(self) -> 'DilationGenerator':
        """S_λ⁻¹ = S_{-λ}."""
        return DilationGenerator(lambda_=-self.lambda_)
    
    def compose(self, other: 'DilationGenerator') -> 'DilationGenerator':
        """S_λ S_μ = S_{λ+μ}."""
        return DilationGenerator(lambda_=self.lambda_ + other.lambda_)
    
    @classmethod
    def identity(cls) -> 'DilationGenerator':
        """S_0 = I."""
        return cls(lambda_=0.0)
    
    @classmethod
    def fold_step(cls) -> 'DilationGenerator':
        """Dilation for fold step κ → 2κ."""
        return cls(lambda_=np.log(np.sqrt(2)))


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERLEY-LIEB GENERATOR (T)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TemperleyLiebGenerator(OA6Generator):
    """
    Temperley-Lieb idempotent T_δ.
    
    Properties:
        - T_δ² = δ T_δ (scaled idempotent)
        - Loop parameter δ related to fold index
        - Categorical closure primitive
        - Strand increment corresponds to fold ladder step
    """
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.T, init=False)
    loop_parameter: float = 2.0  # δ
    
    def matrix_2x2(self) -> None:
        """T is not representable as 2×2 matrix in general."""
        return None
    
    def kernel_effect(self, kappa: float) -> float:
        """
        T implements fold ladder step in categorical grading.
        Strand increment: κ → 2κ.
        """
        return 2 * kappa
    
    def is_invertible(self) -> bool:
        return False  # Scaled idempotent is not invertible
    
    def compose_with_self(self) -> Tuple['TemperleyLiebGenerator', float]:
        """T² = δT, returns (T, δ)."""
        return (self, self.loop_parameter)
    
    @classmethod
    def at_root_of_unity(cls, n: int) -> 'TemperleyLiebGenerator':
        """
        T at q = e^{iπ/n}, giving δ = q + q⁻¹ = 2cos(π/n).
        """
        delta = 2 * np.cos(np.pi / n)
        return cls(loop_parameter=delta)
    
    @classmethod
    def jones_wenzl_parameter(cls, n: int) -> float:
        """δ = 2cos(π/(n+2)) for Jones-Wenzl projector P_n."""
        return 2 * np.cos(np.pi / (n + 2))


# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IdentityGenerator(OA6Generator):
    """Identity element."""
    generator_type: OA6GeneratorType = field(default=OA6GeneratorType.C, init=False)  # Placeholder
    
    def matrix_2x2(self) -> NDArray[np.float64]:
        return np.eye(2, dtype=np.float64)
    
    def kernel_effect(self, kappa: float) -> float:
        return kappa
    
    def is_invertible(self) -> bool:
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# OA6 WORD - COMPOSITION OF GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OA6Word:
    """
    Word in OA6 generators.
    
    A word is a sequence of generators: W = G_1 G_2 ... G_n
    Composition is concatenation, reduced by algebraic relations.
    """
    generators: List[OA6Generator] = field(default_factory=list)
    
    def __len__(self) -> int:
        return len(self.generators)
    
    def append(self, gen: OA6Generator) -> 'OA6Word':
        """Append generator to word."""
        new_gens = self.generators + [gen]
        return OA6Word(generators=new_gens)
    
    def compose(self, other: 'OA6Word') -> 'OA6Word':
        """Concatenate words."""
        return OA6Word(generators=self.generators + other.generators)
    
    def matrix_product(self) -> Optional[NDArray[np.float64]]:
        """
        Compute 2×2 matrix product of all representable generators.
        Returns None if any generator is not 2×2 representable.
        """
        result = np.eye(2, dtype=np.float64)
        for gen in self.generators:
            mat = gen.matrix_2x2()
            if mat is None:
                return None
            result = result @ mat
        return result
    
    def kernel_transport(self, initial_kappa: float) -> float:
        """Transport fold index through the word."""
        kappa = initial_kappa
        for gen in self.generators:
            kappa = gen.kernel_effect(kappa)
        return kappa
    
    def is_invertible_word(self) -> bool:
        """Check if all generators are invertible."""
        return all(gen.is_invertible() for gen in self.generators)
    
    def inverse(self) -> Optional['OA6Word']:
        """
        Inverse word: W⁻¹ = G_n⁻¹ ... G_2⁻¹ G_1⁻¹.
        Returns None if word contains non-invertible generators.
        """
        if not self.is_invertible_word():
            return None
        
        inv_gens = []
        for gen in reversed(self.generators):
            if hasattr(gen, 'inverse'):
                inv_gens.append(gen.inverse())
            elif isinstance(gen, ComplementGenerator):
                inv_gens.append(gen)  # C⁻¹ = C
            elif isinstance(gen, RotationGenerator):
                inv_gens.append(RotationCubedGenerator())  # R⁻¹ = R³
            elif isinstance(gen, IdentityGenerator):
                inv_gens.append(gen)
            else:
                return None
        
        return OA6Word(generators=inv_gens)
    
    def __mul__(self, other: 'OA6Word') -> 'OA6Word':
        return self.compose(other)
    
    def __repr__(self) -> str:
        if not self.generators:
            return "OA6Word(I)"
        gen_strs = [str(g) for g in self.generators]
        return f"OA6Word({' · '.join(gen_strs)})"


# ═══════════════════════════════════════════════════════════════════════════════
# PSL(2,Z) NORMAL FORM
# ═══════════════════════════════════════════════════════════════════════════════

class ModularNormalForm:
    """
    Normal form for words in the modular group PSL(2,Z).
    
    PSL(2,Z) = <r, g | r² = 1, (rg)³ = 1>
    where r = R (rotation) and g = G (simple shear).
    
    Normal form: g^{a_0} r g^{a_1} r ... r g^{a_ℓ} r^b
    with a_i ∈ Z, a_1,...,a_ℓ ≠ 0, b ∈ {0,1}.
    """
    
    def __init__(self, matrix: NDArray[np.int64]):
        """Initialize from 2×2 integer matrix in SL(2,Z)."""
        if matrix.shape != (2, 2):
            raise ValueError("Matrix must be 2×2")
        if abs(int(np.linalg.det(matrix))) != 1:
            raise ValueError("Matrix must have determinant ±1")
        
        self.matrix = matrix.astype(np.int64)
        self._compute_normal_form()
    
    def _compute_normal_form(self):
        """
        Compute normal form using continued fraction algorithm.
        """
        a, b = int(self.matrix[0, 0]), int(self.matrix[0, 1])
        c, d = int(self.matrix[1, 0]), int(self.matrix[1, 1])
        
        # Handle special cases
        if c == 0:
            # Upper triangular
            self.exponents = [b // d] if d != 0 else [0]
            self.r_power = 0
            return
        
        # Euclidean algorithm to get continued fraction of a/c
        exponents = []
        while c != 0:
            q = a // c
            exponents.append(q)
            a, c = c, a - q * c
        
        self.exponents = exponents
        self.r_power = 0 if (len(exponents) % 2 == 0) else 1
    
    @property
    def word_length(self) -> int:
        """Length of normal form word."""
        return len(self.exponents) + (1 if self.r_power else 0)
    
    def to_word(self) -> OA6Word:
        """Convert normal form to OA6Word."""
        generators = []
        
        for i, exp in enumerate(self.exponents):
            if exp != 0:
                generators.append(GatewayGenerator.simple_shear(exp))
            if i < len(self.exponents) - 1:
                generators.append(RotationGenerator())
        
        if self.r_power:
            generators.append(RotationGenerator())
        
        return OA6Word(generators=generators)
    
    def __repr__(self) -> str:
        parts = []
        for i, exp in enumerate(self.exponents):
            if exp != 0:
                parts.append(f"g^{exp}")
            if i < len(self.exponents) - 1:
                parts.append("r")
        if self.r_power:
            parts.append("r")
        
        return f"ModularNF({' '.join(parts) if parts else 'I'})"


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL EFFECT TABLE
# ═══════════════════════════════════════════════════════════════════════════════

class KernelEffectTable:
    """
    Summary of kernel effects for OA6 generators.
    
    Generator | κ → κ' | Notes
    ----------|--------|------
    C         | κ      | Preserves κ
    R         | κ      | Preserves κ
    G         | varies | Depends on gateway instance
    K_κ       | κ      | Projects to κ-slice (non-invertible)
    S_λ       | e^{2λ}κ| Bandwidth scaling
    T         | 2κ     | Fold ladder step (categorical)
    """
    
    EFFECTS = {
        'C': "κ' = κ (preserved)",
        'R': "κ' = κ (preserved)",
        'G': "κ' determined by gateway certificate",
        'K': "κ' = κ (projects to κ-slice)",
        'S': "κ' = e^{2λ}κ",
        'T': "κ' = 2κ (strand increment)"
    }
    
    @classmethod
    def describe(cls, gen_type: OA6GeneratorType) -> str:
        """Get effect description for generator type."""
        return cls.EFFECTS.get(gen_type.name, "Unknown")
    
    @classmethod
    def all_effects(cls) -> Dict[str, str]:
        """All kernel effects."""
        return cls.EFFECTS.copy()


# ═══════════════════════════════════════════════════════════════════════════════
# OA6 ALGEBRA - COMPLETE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class OA6Algebra:
    """
    Complete OA6 algebra with word operations and normalization.
    """
    
    def __init__(self, initial_kappa: float = 1.0):
        """Initialize with starting fold index."""
        self.initial_kappa = initial_kappa
        self.current_kappa = initial_kappa
    
    def complement(self) -> ComplementGenerator:
        """Create complement generator."""
        return ComplementGenerator()
    
    def rotation(self) -> RotationGenerator:
        """Create rotation generator."""
        return RotationGenerator()
    
    def gateway(self, u: int, v: int, A: int) -> GatewayGenerator:
        """Create Pell gateway generator."""
        return GatewayGenerator(u=u, v=v, discriminant=A)
    
    def kernel(self, kappa: float = None) -> KernelProjector:
        """Create kernel projector."""
        if kappa is None:
            kappa = self.current_kappa
        return KernelProjector(fold_index=FoldIndex(kappa=kappa))
    
    def dilation(self, lambda_: float) -> DilationGenerator:
        """Create dilation generator."""
        return DilationGenerator(lambda_=lambda_)
    
    def temperley_lieb(self, delta: float = 2.0) -> TemperleyLiebGenerator:
        """Create Temperley-Lieb generator."""
        return TemperleyLiebGenerator(loop_parameter=delta)
    
    def word(self, *generators: OA6Generator) -> OA6Word:
        """Create word from generators."""
        return OA6Word(generators=list(generators))
    
    def normalize_modular(self, word: OA6Word) -> OA6Word:
        """
        Reduce modular (invertible) part of word to normal form.
        """
        matrix = word.matrix_product()
        if matrix is None:
            return word  # Contains non-representable generators
        
        # Round to integers (should be exact for modular words)
        int_matrix = np.round(matrix).astype(np.int64)
        nf = ModularNormalForm(int_matrix)
        return nf.to_word()
    
    def transport_kappa(self, word: OA6Word) -> float:
        """Transport fold index through word."""
        return word.kernel_transport(self.initial_kappa)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_oa6_algebra(kappa: float = 1.0) -> OA6Algebra:
    """Create an OA6 algebra instance."""
    return OA6Algebra(initial_kappa=kappa)


def modular_normal_form(matrix: NDArray) -> ModularNormalForm:
    """Compute PSL(2,Z) normal form of matrix."""
    return ModularNormalForm(matrix.astype(np.int64))


def kernel_effect_summary() -> Dict[str, str]:
    """Get summary of all kernel effects."""
    return KernelEffectTable.all_effects()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Types
    'OA6GeneratorType',
    'FoldIndex',
    
    # Generators
    'OA6Generator',
    'ComplementGenerator',
    'RotationGenerator',
    'GatewayGenerator',
    'KernelProjector',
    'DilationGenerator',
    'TemperleyLiebGenerator',
    'IdentityGenerator',
    
    # Words and algebra
    'OA6Word',
    'ModularNormalForm',
    'KernelEffectTable',
    'OA6Algebra',
    
    # Functions
    'create_oa6_algebra',
    'modular_normal_form',
    'kernel_effect_summary',
]

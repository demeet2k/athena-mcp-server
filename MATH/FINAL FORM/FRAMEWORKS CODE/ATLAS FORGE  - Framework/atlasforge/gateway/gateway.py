"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         GATEWAY ALGEBRA MODULE                               ║
║                                                                              ║
║  Pell Equations, Möbius Boosts, Hyperbolic Navigation, Scale Transport       ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Gateway scalars encode calibrated scale ratios through hyperbolic         ║
║    coordinates: T = tanh(α) where α is the rapidity (log scale ratio).       ║
║    The velocity-addition law governs composition of gateways.                ║
║                                                                              ║
║  Key Objects:                                                                ║
║    - Gateway scalar: T ∈ (-1, 1), bounded velocity coordinate                ║
║    - Scale ratio: R = (1+T)/(1-T) > 0                                        ║
║    - Rapidity: α = artanh(T) = (1/2)ln(R)                                    ║
║    - Boost matrix: B(T) ∈ SL(2,ℝ), hyperbolic rotation                       ║
║    - Pell gateway: G(u,v;A) ∈ SL(2,ℤ), integer navigation                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any, Union
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray
import math


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY SCALAR - THE BOUNDED VELOCITY COORDINATE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayScalar:
    """
    Gateway scalar T ∈ (-1, 1) encoding a calibrated scale ratio.
    
    The gateway T is the Cayley coordinate of a hyperbolic dilation:
        T = (R - 1)/(R + 1) = tanh(α)
    
    where:
        R = scale ratio = δ_m/δ_n (ratio of calibration constants)
        α = rapidity = (1/2)ln(R) = artanh(T)
    
    Properties:
        - T ∈ (-1, 1): bounded interval (velocity space)
        - T = 0: identity (no scale change)
        - T → ±1: infinite scale ratio
        - Composition: velocity-addition law
    """
    value: float
    source_index: Optional[int] = None
    target_index: Optional[int] = None
    
    def __post_init__(self):
        if not -1 < self.value < 1:
            raise ValueError(f"Gateway scalar must be in (-1, 1), got {self.value}")
    
    @property
    def rapidity(self) -> float:
        """α = artanh(T), hyperbolic displacement."""
        return np.arctanh(self.value)
    
    @property
    def scale_ratio(self) -> float:
        """R = (1+T)/(1-T), multiplicative scale factor."""
        return (1 + self.value) / (1 - self.value)
    
    @property
    def transmission(self) -> float:
        """𝒯 = 1 - T² = sech²(α), transmission coefficient."""
        return 1 - self.value**2
    
    @classmethod
    def from_rapidity(cls, alpha: float, 
                      source: Optional[int] = None,
                      target: Optional[int] = None) -> 'GatewayScalar':
        """Create gateway from rapidity α."""
        T = np.tanh(alpha)
        return cls(value=T, source_index=source, target_index=target)
    
    @classmethod
    def from_scale_ratio(cls, R: float,
                        source: Optional[int] = None,
                        target: Optional[int] = None) -> 'GatewayScalar':
        """Create gateway from scale ratio R > 0."""
        if R <= 0:
            raise ValueError(f"Scale ratio must be positive, got {R}")
        T = (R - 1) / (R + 1)
        return cls(value=T, source_index=source, target_index=target)
    
    @classmethod
    def from_calibration_pair(cls, delta_n: float, delta_m: float) -> 'GatewayScalar':
        """
        Create gateway from calibration constants.
        T(n,m) = (δ_m/δ_n - 1)/(δ_m/δ_n + 1)
        """
        R = delta_m / delta_n
        return cls.from_scale_ratio(R)
    
    def inverse(self) -> 'GatewayScalar':
        """T(m,n) = -T(n,m), gateway inversion."""
        return GatewayScalar(
            value=-self.value,
            source_index=self.target_index,
            target_index=self.source_index
        )
    
    def compose(self, other: 'GatewayScalar') -> 'GatewayScalar':
        """
        Velocity-addition law for gateway composition:
        T(n,m) = (T(n,ℓ) + T(ℓ,m)) / (1 + T(n,ℓ)·T(ℓ,m))
        
        Equivalently: α(n,m) = α(n,ℓ) + α(ℓ,m)
        """
        T1, T2 = self.value, other.value
        T_composed = (T1 + T2) / (1 + T1 * T2)
        return GatewayScalar(
            value=T_composed,
            source_index=self.source_index,
            target_index=other.target_index
        )
    
    def __add__(self, other: 'GatewayScalar') -> 'GatewayScalar':
        """Velocity addition."""
        return self.compose(other)
    
    def __neg__(self) -> 'GatewayScalar':
        """Inversion."""
        return self.inverse()
    
    def __repr__(self) -> str:
        return f"Gateway(T={self.value:.6f}, R={self.scale_ratio:.6f}, α={self.rapidity:.6f})"


# ═══════════════════════════════════════════════════════════════════════════════
# BOOST MATRIX - HYPERBOLIC ROTATION IN SL(2,ℝ)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BoostMatrix:
    """
    Normalized hyperbolic boost matrix B(T) ∈ SL(2,ℝ).
    
    B(T) = (1/√(1-T²)) [[1, T], [T, 1]]
         = [[cosh(α), sinh(α)], [sinh(α), cosh(α)]]
    
    Properties:
        - det(B) = 1 (unimodular)
        - Eigenvalues: λ_± = e^{±α}
        - Eigenvalue ratio: λ_+/λ_- = R (scale ratio)
        - Möbius action: z ↦ (cosh(α)z + sinh(α))/(sinh(α)z + cosh(α))
    """
    matrix: NDArray[np.float64]
    gateway: GatewayScalar
    
    @classmethod
    def from_gateway(cls, gateway: GatewayScalar) -> 'BoostMatrix':
        """Construct boost matrix from gateway scalar."""
        T = gateway.value
        alpha = gateway.rapidity
        
        cosh_a = np.cosh(alpha)
        sinh_a = np.sinh(alpha)
        
        matrix = np.array([
            [cosh_a, sinh_a],
            [sinh_a, cosh_a]
        ])
        
        return cls(matrix=matrix, gateway=gateway)
    
    @classmethod
    def from_rapidity(cls, alpha: float) -> 'BoostMatrix':
        """Construct from rapidity directly."""
        gateway = GatewayScalar.from_rapidity(alpha)
        return cls.from_gateway(gateway)
    
    @property
    def cosh_alpha(self) -> float:
        """cosh(α) = B[0,0] = B[1,1]."""
        return self.matrix[0, 0]
    
    @property
    def sinh_alpha(self) -> float:
        """sinh(α) = B[0,1] = B[1,0]."""
        return self.matrix[0, 1]
    
    @property
    def eigenvalues(self) -> Tuple[float, float]:
        """λ_+ = e^α, λ_- = e^{-α}."""
        alpha = self.gateway.rapidity
        return (np.exp(alpha), np.exp(-alpha))
    
    @property
    def determinant(self) -> float:
        """Should be 1 for SL(2,ℝ)."""
        return np.linalg.det(self.matrix)
    
    def apply(self, v: NDArray[np.float64]) -> NDArray[np.float64]:
        """Apply boost to vector."""
        return self.matrix @ v
    
    def mobius_action(self, z: complex) -> complex:
        """
        Möbius transformation on projective coordinate z.
        z ↦ (cosh(α)·z + sinh(α))/(sinh(α)·z + cosh(α))
        """
        c, s = self.cosh_alpha, self.sinh_alpha
        return (c * z + s) / (s * z + c)
    
    def compose(self, other: 'BoostMatrix') -> 'BoostMatrix':
        """Matrix multiplication corresponds to gateway composition."""
        new_matrix = self.matrix @ other.matrix
        new_gateway = self.gateway.compose(other.gateway)
        return BoostMatrix(matrix=new_matrix, gateway=new_gateway)
    
    def inverse(self) -> 'BoostMatrix':
        """B(T)^{-1} = B(-T)."""
        return BoostMatrix.from_gateway(self.gateway.inverse())
    
    def __matmul__(self, other: 'BoostMatrix') -> 'BoostMatrix':
        return self.compose(other)
    
    def __repr__(self) -> str:
        return f"Boost(α={self.gateway.rapidity:.4f}, det={self.determinant:.6f})"


# ═══════════════════════════════════════════════════════════════════════════════
# PELL EQUATION SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PellSolution:
    """
    Solution (u, v) to Pell equation u² - A·v² = 1.
    
    The Pell equation encodes integer navigation through scale hierarchies.
    The fundamental solution generates all others by powers.
    """
    u: int
    v: int
    discriminant: int  # A
    
    def __post_init__(self):
        # Verify Pell equation
        residual = self.u**2 - self.discriminant * self.v**2
        if residual != 1:
            raise ValueError(f"Not a Pell solution: {self.u}² - {self.discriminant}·{self.v}² = {residual} ≠ 1")
    
    @property
    def algebraic_integer(self) -> float:
        """η = u + v√A, the unit in ℤ[√A]."""
        return self.u + self.v * np.sqrt(self.discriminant)
    
    @property
    def conjugate(self) -> float:
        """η̄ = u - v√A."""
        return self.u - self.v * np.sqrt(self.discriminant)
    
    def power(self, n: int) -> 'PellSolution':
        """
        Compute (u_n, v_n) where u_n + v_n√A = η^n.
        Uses matrix exponentiation for efficiency.
        """
        if n == 0:
            return PellSolution(u=1, v=0, discriminant=self.discriminant)
        if n < 0:
            # η^{-n} = η̄^n (conjugate for negative powers)
            pos_sol = self.power(-n)
            # For unit norm, inverse is conjugate
            return PellSolution(u=pos_sol.u, v=-pos_sol.v, discriminant=self.discriminant)
        
        # Matrix exponentiation
        A = self.discriminant
        M = np.array([[self.u, self.v], [A * self.v, self.u]], dtype=np.int64)
        
        result = np.eye(2, dtype=np.int64)
        base = M.copy()
        exp = n
        
        while exp > 0:
            if exp % 2 == 1:
                result = result @ base
            base = base @ base
            exp //= 2
        
        return PellSolution(u=int(result[0, 0]), v=int(result[0, 1]), discriminant=A)


def solve_pell_fundamental(A: int) -> PellSolution:
    """
    Find the fundamental solution of u² - A·v² = 1.
    
    Uses continued fraction expansion of √A to find the smallest positive solution.
    
    Args:
        A: Discriminant (must be positive non-square)
        
    Returns:
        Fundamental Pell solution (u₀, v₀)
    """
    if A <= 0:
        raise ValueError(f"Discriminant must be positive, got {A}")
    
    sqrt_A = int(np.sqrt(A))
    if sqrt_A * sqrt_A == A:
        raise ValueError(f"Discriminant {A} is a perfect square")
    
    # Continued fraction method
    m, d, a = 0, 1, sqrt_A
    
    # Track convergents
    p_prev, p_curr = 1, a
    q_prev, q_curr = 0, 1
    
    # Find period
    seen = {}
    while True:
        m = d * a - m
        d = (A - m * m) // d
        a = (sqrt_A + m) // d
        
        # Check if we have a solution
        if p_curr * p_curr - A * q_curr * q_curr == 1:
            return PellSolution(u=p_curr, v=q_curr, discriminant=A)
        
        # Update convergents
        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        
        # Check for period (prevent infinite loop)
        state = (m, d, a)
        if state in seen:
            break
        seen[state] = True
    
    raise RuntimeError(f"Failed to find Pell solution for A={A}")


# ═══════════════════════════════════════════════════════════════════════════════
# PELL GATEWAY MATRIX - INTEGER NAVIGATION IN SL(2,ℤ)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PellGateway:
    """
    Integer gateway matrix G(u,v;A) ∈ SL(2,ℤ).
    
    G = [[u, v], [Av, u]]  where u² - Av² = 1
    
    Properties:
        - det(G) = 1 (unimodular)
        - Preserves quadratic form Q_A(x,y) = x² - Ay²
        - Eigenvalues: λ_± = u ± v√A
        - Discrete hyperbolic rotation
    
    Navigation:
        Forward hop: (x', y') = G(x, y)
        Backward hop: (x', y') = G^{-1}(x, y)
    """
    solution: PellSolution
    matrix: NDArray[np.int64] = field(init=False)
    
    def __post_init__(self):
        u, v, A = self.solution.u, self.solution.v, self.solution.discriminant
        self.matrix = np.array([
            [u, v],
            [A * v, u]
        ], dtype=np.int64)
    
    @classmethod
    def from_discriminant(cls, A: int) -> 'PellGateway':
        """Create gateway from discriminant using fundamental solution."""
        solution = solve_pell_fundamental(A)
        return cls(solution=solution)
    
    @property
    def discriminant(self) -> int:
        """A, the discriminant parameter."""
        return self.solution.discriminant
    
    @property
    def determinant(self) -> int:
        """Should be 1."""
        return int(np.linalg.det(self.matrix))
    
    @property
    def eigenvalues(self) -> Tuple[float, float]:
        """λ_+ = u + v√A, λ_- = u - v√A."""
        return (self.solution.algebraic_integer, self.solution.conjugate)
    
    def forward_hop(self, x: int, y: int) -> Tuple[int, int]:
        """
        Forward navigation: (x', y') = G^T(x, y)
        
        The matrix G = [[u, v], [Av, u]] acts on column vectors.
        For the quadratic form Q_A(x,y) = x² - Ay² to be preserved,
        we use the transpose action:
            x' = ux + Avy
            y' = vx + uy
        """
        u, v, A = self.solution.u, self.solution.v, self.discriminant
        x_new = u * x + A * v * y
        y_new = v * x + u * y
        return (x_new, y_new)
    
    def backward_hop(self, x: int, y: int) -> Tuple[int, int]:
        """
        Backward navigation: inverse of forward hop.
        G^{-T} action: x' = ux - Avy, y' = -vx + uy
        """
        u, v, A = self.solution.u, self.solution.v, self.discriminant
        x_new = u * x - A * v * y
        y_new = -v * x + u * y
        return (x_new, y_new)
    
    def preserves_form(self, x: int, y: int) -> bool:
        """
        Verify Q_A(x,y) = Q_A(x',y') where (x',y') = G(x,y).
        Q_A(x,y) = x² - Ay²
        """
        A = self.discriminant
        Q_before = x**2 - A * y**2
        x_new, y_new = self.forward_hop(x, y)
        Q_after = x_new**2 - A * y_new**2
        return Q_before == Q_after
    
    def power(self, n: int) -> 'PellGateway':
        """G^n corresponding to η^n."""
        new_solution = self.solution.power(n)
        return PellGateway(solution=new_solution)
    
    def inverse(self) -> 'PellGateway':
        """G^{-1}."""
        return self.power(-1)
    
    def orbit(self, x0: int, y0: int, n_steps: int) -> List[Tuple[int, int]]:
        """Generate orbit starting from (x0, y0)."""
        orbit = [(x0, y0)]
        x, y = x0, y0
        for _ in range(n_steps):
            x, y = self.forward_hop(x, y)
            orbit.append((x, y))
        return orbit
    
    def __repr__(self) -> str:
        u, v, A = self.solution.u, self.solution.v, self.discriminant
        return f"PellGateway(A={A}, u={u}, v={v}, λ_+={self.eigenvalues[0]:.4f})"


# ═══════════════════════════════════════════════════════════════════════════════
# FOLD NAVIGATION - BANDWIDTH TRANSPORT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass  
class FoldLadder:
    """
    Fold ladder κ_n = 2^n with bandwidth τ_κ = π/(2√κ).
    
    The fold step κ → 2κ corresponds to:
        - Bandwidth contraction: τ → τ/√2
        - Gateway scalar: T_fold = (√2 - 1)/(√2 + 1) ≈ 0.1716
        - Rapidity: α_fold = (1/2)ln(√2) = ln(√2)/2
    
    This is the canonical √2 ladder connecting analytic, symplectic,
    and categorical presentations.
    """
    base_kappa: float = 1.0  # Starting fold index
    
    @staticmethod
    def bandwidth(kappa: float) -> float:
        """τ_κ = π/(2√κ), Paley-Wiener half-bandwidth."""
        return np.pi / (2 * np.sqrt(kappa))
    
    @staticmethod
    def fold_ratio() -> float:
        """R_fold = τ_n/τ_{n+1} = √2."""
        return np.sqrt(2)
    
    @staticmethod
    def fold_gateway() -> GatewayScalar:
        """Gateway scalar for fold step."""
        sqrt2 = np.sqrt(2)
        T = (sqrt2 - 1) / (sqrt2 + 1)
        return GatewayScalar(value=T)
    
    def kappa(self, n: int) -> float:
        """κ_n = base_kappa · 2^n."""
        return self.base_kappa * (2 ** n)
    
    def level_bandwidth(self, n: int) -> float:
        """Bandwidth at level n."""
        return self.bandwidth(self.kappa(n))
    
    def transport_kappa(self, kappa: float, gateway: GatewayScalar) -> float:
        """
        Transport fold index through gateway.
        Under dilation S_λ: κ → e^{2λ}κ
        Gateway rapidity α corresponds to λ = α.
        """
        alpha = gateway.rapidity
        return kappa * np.exp(2 * alpha)
    
    def fold_sequence(self, n_levels: int) -> List[Tuple[int, float, float]]:
        """Generate fold sequence: (level, κ, τ)."""
        return [
            (n, self.kappa(n), self.level_bandwidth(n))
            for n in range(n_levels)
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY ALGEBRA - COMPOSITION AND TRANSPORT
# ═══════════════════════════════════════════════════════════════════════════════

class GatewayAlgebra:
    """
    Complete gateway algebra combining continuous and discrete navigation.
    
    Provides unified interface for:
        - Continuous boosts (SL(2,ℝ))
        - Discrete hops (SL(2,ℤ))
        - Fold transport
        - Transmission calculations
    """
    
    def __init__(self):
        self._pell_cache: Dict[int, PellGateway] = {}
        self._fold_ladder = FoldLadder()
    
    def gateway(self, n: int, m: int, 
                delta_func: Callable[[int], float]) -> GatewayScalar:
        """
        Compute gateway T(n,m) from calibration function.
        
        Args:
            n, m: Calibration indices
            delta_func: Function giving δ_k for index k
            
        Returns:
            Gateway scalar T(n,m)
        """
        delta_n = delta_func(n)
        delta_m = delta_func(m)
        return GatewayScalar.from_calibration_pair(delta_n, delta_m)
    
    def boost(self, T: float) -> BoostMatrix:
        """Create boost matrix from gateway scalar value."""
        gateway = GatewayScalar(value=T)
        return BoostMatrix.from_gateway(gateway)
    
    def pell_gateway(self, A: int) -> PellGateway:
        """Get or compute Pell gateway for discriminant A."""
        if A not in self._pell_cache:
            self._pell_cache[A] = PellGateway.from_discriminant(A)
        return self._pell_cache[A]
    
    def transmission_chain(self, gateways: List[GatewayScalar]) -> float:
        """
        Compute total transmission through chain of gateways.
        
        Transmission combines through rapidity addition:
        𝒯_total = sech²(Σα_i)
        """
        total_rapidity = sum(g.rapidity for g in gateways)
        return 1 / np.cosh(total_rapidity)**2
    
    def compose_gateways(self, gateways: List[GatewayScalar]) -> GatewayScalar:
        """Compose sequence of gateways using velocity-addition."""
        if not gateways:
            return GatewayScalar(value=0.0)  # Identity
        
        result = gateways[0]
        for g in gateways[1:]:
            result = result.compose(g)
        return result
    
    def barrier_strength(self, gateway: GatewayScalar) -> float:
        """
        Barrier strength = 1 - transmission.
        High barrier ⟹ difficult to traverse.
        """
        return 1 - gateway.transmission
    
    def navigate_pell_orbit(self, A: int, start: Tuple[int, int], 
                           n_steps: int) -> List[Tuple[int, int]]:
        """Navigate Pell orbit from starting point."""
        gateway = self.pell_gateway(A)
        return gateway.orbit(start[0], start[1], n_steps)
    
    def fold_transport(self, kappa: float, 
                      gateway: GatewayScalar) -> float:
        """Transport fold index through gateway."""
        return self._fold_ladder.transport_kappa(kappa, gateway)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL GATEWAYS - CANONICAL EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

class SpecialGateways:
    """
    Library of special gateway values with closed-form expressions.
    """
    
    @staticmethod
    def golden_gateway() -> GatewayScalar:
        """Gateway from golden ratio φ = (1+√5)/2."""
        phi = (1 + np.sqrt(5)) / 2
        return GatewayScalar.from_scale_ratio(phi)
    
    @staticmethod
    def silver_gateway() -> GatewayScalar:
        """Gateway from silver ratio δ_s = 1 + √2."""
        delta_s = 1 + np.sqrt(2)
        return GatewayScalar.from_scale_ratio(delta_s)
    
    @staticmethod
    def fold_gateway() -> GatewayScalar:
        """Gateway for √2 fold step."""
        return FoldLadder.fold_gateway()
    
    @staticmethod
    def pi_over_8_gateway() -> GatewayScalar:
        """
        T = tan(π/8) = √2 - 1
        This appears in √2 constructions.
        """
        T = np.tan(np.pi / 8)
        return GatewayScalar(value=T)
    
    @staticmethod  
    def triangular_square_gateway() -> PellGateway:
        """
        Gateway for triangular-square nexus.
        Pell equation: X² - 8Y² = 1
        Fundamental solution: (3, 1)
        λ_+ = 3 + 2√2
        """
        return PellGateway.from_discriminant(8)
    
    @staticmethod
    def pentagon_gateway() -> PellGateway:
        """
        Gateway related to pentagonal constructions.
        Pell equation: X² - 5Y² = 1
        Related to golden ratio.
        """
        return PellGateway.from_discriminant(5)


# ═══════════════════════════════════════════════════════════════════════════════
# TRIGONOMETRIC GATEWAY IDENTITIES
# ═══════════════════════════════════════════════════════════════════════════════

def gateway_from_angle(theta: float) -> GatewayScalar:
    """
    Create gateway from trigonometric angle.
    T = tan(θ/2) when R = (1 + sin θ)/(1 - sin θ) type relations hold.
    """
    T = np.tan(theta / 2)
    if abs(T) >= 1:
        raise ValueError(f"Angle {theta} gives |T| ≥ 1")
    return GatewayScalar(value=T)


def gateway_angle(gateway: GatewayScalar) -> float:
    """
    Extract angle from gateway.
    θ = 2·arctan(T)
    """
    return 2 * np.arctan(gateway.value)


def hyperbolic_distance(g1: GatewayScalar, g2: GatewayScalar) -> float:
    """
    Hyperbolic distance between two gateways.
    d = |α_1 - α_2| = |artanh(T_1) - artanh(T_2)|
    """
    return abs(g1.rapidity - g2.rapidity)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_gateway_algebra() -> GatewayAlgebra:
    """Create a gateway algebra instance."""
    return GatewayAlgebra()


def pell_orbit(A: int, n_steps: int = 10) -> List[Tuple[int, int]]:
    """Generate Pell orbit for discriminant A starting from (1, 0)."""
    gateway = PellGateway.from_discriminant(A)
    return gateway.orbit(1, 0, n_steps)


def velocity_addition(T1: float, T2: float) -> float:
    """
    Velocity addition formula for gateway composition.
    T = (T1 + T2)/(1 + T1·T2)
    """
    return (T1 + T2) / (1 + T1 * T2)


def rapidity_from_velocity(T: float) -> float:
    """α = artanh(T)."""
    return np.arctanh(T)


def velocity_from_rapidity(alpha: float) -> float:
    """T = tanh(α)."""
    return np.tanh(alpha)


def transmission_coefficient(T: float) -> float:
    """𝒯 = 1 - T² = sech²(α)."""
    return 1 - T**2


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core classes
    'GatewayScalar',
    'BoostMatrix',
    'PellSolution',
    'PellGateway',
    'FoldLadder',
    'GatewayAlgebra',
    'SpecialGateways',
    
    # Functions
    'solve_pell_fundamental',
    'gateway_from_angle',
    'gateway_angle',
    'hyperbolic_distance',
    'create_gateway_algebra',
    'pell_orbit',
    'velocity_addition',
    'rapidity_from_velocity',
    'velocity_from_rapidity',
    'transmission_coefficient',
]

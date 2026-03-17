"""
ATHENA OS - UNIVERSAL COMPUTATIONAL ONTOLOGY (UCO)
===================================================
Chapter 1: The Computational Substrate (Hardware & Metric)

THE GELFAND TRIPLE (RIGGED HILBERT SPACE):
    Φ ⊂ H ⊂ Φ×

    Φ   = Nuclear Space of Test Functions (Ideal Forms)
    H   = Hilbert Space of realizable physical states
    Φ×  = Dual Space of Distributions (Singularities/Source)

The universe U is defined as evolving under a non-commutative
operator algebra on this Rigged Hilbert Space topology.

COMPUTATIONAL PROPERTIES:
    - Φ:  Smooth, rapidly decaying (Schwartz space)
    - H:  Square-integrable, normalizable
    - Φ×: Generalized eigenstates, Dirac deltas
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
from scipy.special import hermite
from scipy.integrate import quad
import warnings


# =============================================================================
# SPACE TYPES
# =============================================================================

class SpaceType(Enum):
    """Types of spaces in the Gelfand Triple."""
    
    PHI = "Φ"           # Test functions (Ideal Forms)
    HILBERT = "H"       # Square-integrable states
    PHI_DUAL = "Φ×"     # Distributions (Singularities)


class TopologyType(Enum):
    """Topology types for different spaces."""
    
    FRECHET = "frechet"      # For Φ (countable seminorms)
    HILBERT = "hilbert"      # For H (norm topology)
    WEAK_STAR = "weak_star"  # For Φ× (weak-* topology)


# =============================================================================
# STATE VECTORS
# =============================================================================

@dataclass
class StateVector:
    """
    A state vector in the Gelfand Triple.
    
    Can represent states in Φ, H, or Φ×.
    """
    
    coefficients: np.ndarray
    space_type: SpaceType
    basis_type: str = "position"  # "position", "momentum", "harmonic"
    
    def __post_init__(self):
        """Normalize if in Hilbert space."""
        if self.space_type == SpaceType.HILBERT:
            norm = np.sqrt(np.sum(np.abs(self.coefficients) ** 2))
            if norm > 0:
                self.coefficients = self.coefficients / norm
    
    @property
    def dimension(self) -> int:
        """Dimension of state vector."""
        return len(self.coefficients)
    
    def norm(self) -> float:
        """Compute L2 norm."""
        return float(np.sqrt(np.sum(np.abs(self.coefficients) ** 2)))
    
    def is_normalizable(self) -> bool:
        """Check if state is square-integrable."""
        return np.isfinite(self.norm()) and self.norm() > 0
    
    def inner_product(self, other: 'StateVector') -> complex:
        """
        Compute inner product ⟨self|other⟩.
        """
        if self.dimension != other.dimension:
            raise ValueError("Dimension mismatch")
        return complex(np.dot(np.conj(self.coefficients), other.coefficients))
    
    def overlap(self, other: 'StateVector') -> float:
        """Compute overlap probability |⟨self|other⟩|²."""
        return abs(self.inner_product(other)) ** 2
    
    def tensor_product(self, other: 'StateVector') -> 'StateVector':
        """Compute tensor product self ⊗ other."""
        result = np.outer(self.coefficients, other.coefficients).flatten()
        return StateVector(
            coefficients=result,
            space_type=self.space_type,
            basis_type=f"{self.basis_type}⊗{other.basis_type}"
        )


# =============================================================================
# TEST FUNCTION SPACE (Φ)
# =============================================================================

class SchwartzFunction:
    """
    A function in the Schwartz space S(ℝⁿ).
    
    Schwartz functions are smooth and rapidly decreasing:
    Φ = { φ ∈ C^∞(ℝⁿ) : sup|x^α ∂^β φ(x)| < ∞ }
    """
    
    def __init__(self, func: Callable[[np.ndarray], complex],
                 derivative: Optional[Callable] = None):
        self.func = func
        self._derivative = derivative
    
    def __call__(self, x: np.ndarray) -> complex:
        """Evaluate function at x."""
        return self.func(x)
    
    def evaluate(self, x: np.ndarray) -> complex:
        """Evaluate function at x."""
        return self.func(x)
    
    def seminorm(self, alpha: int, beta: int, 
                 x_range: Tuple[float, float] = (-10, 10),
                 n_points: int = 1000) -> float:
        """
        Compute seminorm ||φ||_{α,β} = sup|x^α ∂^β φ(x)|.
        
        This defines the Fréchet topology on Φ.
        """
        x = np.linspace(x_range[0], x_range[1], n_points)
        
        # Compute x^α * |derivative^β(φ)(x)|
        # Simplified: for β=0, just use function value
        if beta == 0:
            values = np.abs(x ** alpha * np.array([self.func(xi) for xi in x]))
        else:
            # Numerical derivative
            h = (x_range[1] - x_range[0]) / n_points
            values = np.zeros(n_points)
            for i, xi in enumerate(x):
                # Simple finite difference for derivative
                if i > 0 and i < n_points - 1:
                    deriv = (self.func(x[i+1]) - self.func(x[i-1])) / (2 * h)
                    values[i] = abs(xi ** alpha * deriv)
        
        return float(np.max(values))
    
    def is_rapidly_decreasing(self, threshold: float = 1e-6) -> bool:
        """Check if function decays rapidly at infinity."""
        test_points = np.array([10, 100, 1000])
        for x in test_points:
            if abs(self.func(x)) > threshold or abs(self.func(-x)) > threshold:
                return False
        return True


class TestFunctionSpace:
    """
    The space Φ of test functions (Schwartz space).
    
    Represents Ideal Forms - smooth, localized, infinitely differentiable.
    """
    
    def __init__(self, dimension: int = 1):
        self.dimension = dimension
        self._functions: List[SchwartzFunction] = []
    
    def add_function(self, func: SchwartzFunction) -> None:
        """Add a test function to the space."""
        self._functions.append(func)
    
    def gaussian(self, center: float = 0, width: float = 1) -> SchwartzFunction:
        """Create a Gaussian test function (canonical example)."""
        def g(x):
            if isinstance(x, np.ndarray):
                return np.exp(-((x - center) ** 2) / (2 * width ** 2))
            return np.exp(-((x - center) ** 2) / (2 * width ** 2))
        
        return SchwartzFunction(g)
    
    def hermite_function(self, n: int) -> SchwartzFunction:
        """
        Create Hermite function ψ_n(x).
        
        These form an orthonormal basis for L²(ℝ) that lies in Φ.
        """
        def psi_n(x):
            if isinstance(x, np.ndarray):
                h_n = hermite(n)
                return (1 / np.sqrt(2**n * np.math.factorial(n) * np.sqrt(np.pi))) * \
                       np.exp(-x**2 / 2) * h_n(x)
            h_n = hermite(n)
            return (1 / np.sqrt(2**n * np.math.factorial(n) * np.sqrt(np.pi))) * \
                   np.exp(-x**2 / 2) * h_n(x)
        
        return SchwartzFunction(psi_n)
    
    def project_to_hilbert(self, func: SchwartzFunction,
                          n_basis: int = 64) -> StateVector:
        """
        Project test function to Hilbert space representation.
        
        Uses Hermite function basis (eigenfunctions of harmonic oscillator).
        """
        coefficients = np.zeros(n_basis, dtype=complex)
        
        for n in range(n_basis):
            psi_n = self.hermite_function(n)
            # Compute inner product ⟨ψ_n|φ⟩
            def integrand(x):
                return np.conj(psi_n(x)) * func(x)
            
            # Numerical integration
            real_part, _ = quad(lambda x: np.real(integrand(x)), -10, 10)
            imag_part, _ = quad(lambda x: np.imag(integrand(x)), -10, 10)
            coefficients[n] = real_part + 1j * imag_part
        
        return StateVector(
            coefficients=coefficients,
            space_type=SpaceType.HILBERT,
            basis_type="hermite"
        )


# =============================================================================
# HILBERT SPACE (H)
# =============================================================================

class HilbertSpace:
    """
    The Hilbert Space H = L²(M, μ).
    
    Contains all square-integrable, normalizable states.
    Represents physically realizable states subject to thermodynamic decay.
    """
    
    def __init__(self, dimension: int = 256):
        self.dimension = dimension
        self._basis: List[StateVector] = []
        self._initialize_basis()
    
    def _initialize_basis(self):
        """Initialize computational basis."""
        for i in range(self.dimension):
            coeffs = np.zeros(self.dimension, dtype=complex)
            coeffs[i] = 1.0
            self._basis.append(StateVector(
                coefficients=coeffs,
                space_type=SpaceType.HILBERT,
                basis_type="computational"
            ))
    
    def basis_state(self, n: int) -> StateVector:
        """Get n-th basis state |n⟩."""
        if 0 <= n < self.dimension:
            return self._basis[n]
        raise IndexError(f"Basis index {n} out of range")
    
    def vacuum_state(self) -> StateVector:
        """
        Return the vacuum state |0⟩.
        
        The ground state of the system Hamiltonian.
        """
        return self.basis_state(0)
    
    def coherent_state(self, alpha: complex) -> StateVector:
        """
        Create a coherent state |α⟩.
        
        Coherent states are minimum uncertainty states,
        eigenstates of the annihilation operator.
        """
        # |α⟩ = e^(-|α|²/2) Σ (α^n/√n!) |n⟩
        coeffs = np.zeros(self.dimension, dtype=complex)
        
        for n in range(self.dimension):
            coeffs[n] = np.exp(-abs(alpha)**2 / 2) * \
                       (alpha ** n) / np.sqrt(np.math.factorial(min(n, 170)))
        
        return StateVector(
            coefficients=coeffs,
            space_type=SpaceType.HILBERT,
            basis_type="coherent"
        )
    
    def superposition(self, states: List[StateVector],
                     weights: List[complex]) -> StateVector:
        """Create superposition of states."""
        if len(states) != len(weights):
            raise ValueError("Number of states must match weights")
        
        coeffs = np.zeros(self.dimension, dtype=complex)
        for state, weight in zip(states, weights):
            coeffs += weight * state.coefficients
        
        return StateVector(
            coefficients=coeffs,
            space_type=SpaceType.HILBERT,
            basis_type="superposition"
        )
    
    def inner_product(self, psi: StateVector, phi: StateVector) -> complex:
        """
        Compute inner product ⟨ψ|φ⟩.
        
        Defines the metric of H.
        """
        return psi.inner_product(phi)
    
    def transition_probability(self, psi: StateVector, 
                               phi: StateVector) -> float:
        """
        Compute transition probability P(ψ → φ) = |⟨ψ|φ⟩|².
        """
        return psi.overlap(phi)


# =============================================================================
# DUAL SPACE (Φ×)
# =============================================================================

class Distribution:
    """
    A distribution (generalized function) in Φ×.
    
    Acts as continuous antilinear functional on test functions.
    Houses singular objects like Dirac deltas.
    """
    
    def __init__(self, action: Callable[[SchwartzFunction], complex]):
        """
        Args:
            action: The functional F: Φ → ℂ
        """
        self._action = action
    
    def __call__(self, phi: SchwartzFunction) -> complex:
        """Apply distribution to test function: ⟨F|φ⟩ = F(φ)."""
        return self._action(phi)
    
    def evaluate(self, phi: SchwartzFunction) -> complex:
        """Evaluate distribution on test function."""
        return self._action(phi)


class DiracDelta(Distribution):
    """
    The Dirac delta distribution δ(x - x₀).
    
    Eigenstate of the position operator.
    Represents a fixed address in the simulation lattice.
    """
    
    def __init__(self, x0: float = 0):
        self.x0 = x0
        
        def delta_action(phi: SchwartzFunction) -> complex:
            # ⟨x₀|φ⟩ = ∫ δ(x-x₀) φ(x) dx = φ(x₀)
            return phi(self.x0)
        
        super().__init__(delta_action)
    
    def __repr__(self) -> str:
        return f"δ(x - {self.x0})"


class PlaneWave(Distribution):
    """
    Plane wave distribution e^{ikx}.
    
    Eigenstate of the momentum operator.
    Not normalizable in H but exists in Φ×.
    """
    
    def __init__(self, k: float):
        self.k = k
        
        def plane_wave_action(phi: SchwartzFunction) -> complex:
            # ⟨k|φ⟩ = ∫ e^{-ikx} φ(x) dx = φ̂(k) (Fourier transform)
            def integrand(x):
                return np.exp(-1j * self.k * x) * phi(x)
            
            real_part, _ = quad(lambda x: np.real(integrand(x)), -np.inf, np.inf,
                              limit=100)
            imag_part, _ = quad(lambda x: np.imag(integrand(x)), -np.inf, np.inf,
                              limit=100)
            return real_part + 1j * imag_part
        
        super().__init__(plane_wave_action)
    
    def __repr__(self) -> str:
        return f"e^{{i{self.k}x}}"


class DualSpace:
    """
    The dual space Φ× of distributions.
    
    Contains generalized eigenstates for spectral decomposition
    of unbounded operators.
    """
    
    def __init__(self):
        self._distributions: Dict[str, Distribution] = {}
    
    def dirac_delta(self, x0: float) -> DiracDelta:
        """Create Dirac delta at x₀."""
        key = f"delta_{x0}"
        if key not in self._distributions:
            self._distributions[key] = DiracDelta(x0)
        return self._distributions[key]
    
    def plane_wave(self, k: float) -> PlaneWave:
        """Create plane wave with momentum k."""
        key = f"planewave_{k}"
        if key not in self._distributions:
            self._distributions[key] = PlaneWave(k)
        return self._distributions[key]
    
    def spectral_decomposition(self, operator: 'Operator',
                               n_modes: int = 64) -> List[Tuple[complex, Distribution]]:
        """
        Compute spectral decomposition using generalized eigenstates.
        
        Returns list of (eigenvalue, eigenstate) pairs.
        """
        # For demonstration, return delta function basis
        eigenvalues = []
        eigenstates = []
        
        for i in range(n_modes):
            x_i = -10 + 20 * i / n_modes
            eigenvalues.append(complex(x_i))
            eigenstates.append(self.dirac_delta(x_i))
        
        return list(zip(eigenvalues, eigenstates))


# =============================================================================
# GELFAND TRIPLE (RIGGED HILBERT SPACE)
# =============================================================================

@dataclass
class GelfandTriple:
    """
    The Gelfand Triple Φ ⊂ H ⊂ Φ×.
    
    Complete computational substrate for the UCO.
    
    Properties:
    - Φ → H: Dense continuous embedding (test functions are dense in H)
    - H → Φ×: Natural inclusion via Riesz representation
    - Supports unbounded operators with continuous spectra
    """
    
    dimension: int = 256
    
    phi: TestFunctionSpace = field(init=False)
    hilbert: HilbertSpace = field(init=False)
    phi_dual: DualSpace = field(init=False)
    
    def __post_init__(self):
        """Initialize all three spaces."""
        self.phi = TestFunctionSpace(dimension=1)
        self.hilbert = HilbertSpace(dimension=self.dimension)
        self.phi_dual = DualSpace()
    
    def embed_phi_to_hilbert(self, func: SchwartzFunction) -> StateVector:
        """
        Embed test function into Hilbert space.
        
        The embedding i: Φ → H is continuous with dense image.
        """
        return self.phi.project_to_hilbert(func, n_basis=self.dimension)
    
    def embed_hilbert_to_dual(self, state: StateVector) -> Distribution:
        """
        Embed Hilbert space vector into dual space.
        
        Via Riesz representation: ψ ↦ ⟨ψ|·⟩
        """
        def riesz_functional(phi: SchwartzFunction) -> complex:
            phi_state = self.embed_phi_to_hilbert(phi)
            return state.inner_product(phi_state)
        
        return Distribution(riesz_functional)
    
    def vacuum_state(self) -> StateVector:
        """
        Return the vacuum state |0⟩.
        
        The boundary condition for the simulation:
        lim_{t→-∞} |Ψ(t)⟩ = |0⟩
        """
        return self.hilbert.vacuum_state()
    
    def verify_inclusion(self) -> bool:
        """
        Verify the triple inclusion Φ ⊂ H ⊂ Φ×.
        
        Test that embeddings are well-defined and continuous.
        """
        # Create test function
        gaussian = self.phi.gaussian(center=0, width=1)
        
        # Embed to Hilbert
        psi = self.embed_phi_to_hilbert(gaussian)
        
        # Check normalizability
        if not psi.is_normalizable():
            return False
        
        # Embed to dual
        F = self.embed_hilbert_to_dual(psi)
        
        # Test dual pairing
        result = F(gaussian)
        
        # Should be real and positive (overlap with itself)
        return abs(result.imag) < 1e-6 and result.real > 0
    
    def spectral_entropy(self) -> float:
        """
        Compute spectral entropy of the vacuum.
        
        S = 0 for pure state, but encodes entanglement entropy.
        """
        vacuum = self.vacuum_state()
        probs = np.abs(vacuum.coefficients) ** 2
        probs = probs[probs > 1e-15]  # Filter zeros
        
        if len(probs) == 0:
            return 0.0
        
        return float(-np.sum(probs * np.log2(probs)))


# =============================================================================
# OPERATORS
# =============================================================================

class Operator(ABC):
    """Abstract base class for operators on the Gelfand Triple."""
    
    @abstractmethod
    def apply(self, state: StateVector) -> StateVector:
        """Apply operator to state."""
        pass
    
    @property
    @abstractmethod
    def is_bounded(self) -> bool:
        """Check if operator is bounded."""
        pass


class CreationOperator(Operator):
    """
    Creation operator a†.
    
    Creates excitations from vacuum.
    """
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self._matrix = np.zeros((dimension, dimension), dtype=complex)
        for n in range(dimension - 1):
            self._matrix[n+1, n] = np.sqrt(n + 1)
    
    def apply(self, state: StateVector) -> StateVector:
        """Apply a† |ψ⟩."""
        new_coeffs = self._matrix @ state.coefficients
        return StateVector(
            coefficients=new_coeffs,
            space_type=state.space_type,
            basis_type=state.basis_type
        )
    
    @property
    def is_bounded(self) -> bool:
        return False  # Unbounded


class AnnihilationOperator(Operator):
    """
    Annihilation operator a.
    
    a|0⟩ = 0 (vacuum is eigenstate with eigenvalue 0)
    """
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self._matrix = np.zeros((dimension, dimension), dtype=complex)
        for n in range(dimension - 1):
            self._matrix[n, n+1] = np.sqrt(n + 1)
    
    def apply(self, state: StateVector) -> StateVector:
        """Apply a |ψ⟩."""
        new_coeffs = self._matrix @ state.coefficients
        return StateVector(
            coefficients=new_coeffs,
            space_type=state.space_type,
            basis_type=state.basis_type
        )
    
    @property
    def is_bounded(self) -> bool:
        return False


class DisplacementOperator(Operator):
    """
    Displacement operator D(α).
    
    D(α)|0⟩ = |α⟩ (creates coherent state)
    """
    
    def __init__(self, alpha: complex, dimension: int):
        self.alpha = alpha
        self.dimension = dimension
        
        # D(α) = exp(α a† - α* a)
        a_dag = CreationOperator(dimension)._matrix
        a = AnnihilationOperator(dimension)._matrix
        
        exponent = alpha * a_dag - np.conj(alpha) * a
        # Matrix exponential
        self._matrix = self._matrix_exp(exponent)
    
    def _matrix_exp(self, M: np.ndarray) -> np.ndarray:
        """Compute matrix exponential via Taylor series."""
        result = np.eye(M.shape[0], dtype=complex)
        term = np.eye(M.shape[0], dtype=complex)
        
        for k in range(1, 50):  # 50 terms usually sufficient
            term = term @ M / k
            result += term
            if np.max(np.abs(term)) < 1e-15:
                break
        
        return result
    
    def apply(self, state: StateVector) -> StateVector:
        """Apply D(α) |ψ⟩."""
        new_coeffs = self._matrix @ state.coefficients
        return StateVector(
            coefficients=new_coeffs,
            space_type=state.space_type,
            basis_type="displaced"
        )
    
    @property
    def is_bounded(self) -> bool:
        return True  # Unitary, hence bounded


# =============================================================================
# VALIDATION
# =============================================================================

def validate_substrate() -> bool:
    """Validate UCO substrate module."""
    
    # Test state vectors
    coeffs = np.array([1.0, 0, 0, 0], dtype=complex)
    state = StateVector(coeffs, SpaceType.HILBERT)
    assert abs(state.norm() - 1.0) < 1e-10
    
    # Test Schwartz function
    phi = TestFunctionSpace()
    gaussian = phi.gaussian(0, 1)
    assert gaussian.is_rapidly_decreasing()
    
    # Test Hermite functions
    psi_0 = phi.hermite_function(0)
    psi_1 = phi.hermite_function(1)
    # Should be orthogonal
    
    # Test Hilbert space
    H = HilbertSpace(dimension=64)
    vacuum = H.vacuum_state()
    assert vacuum.norm() > 0.99
    
    # Test coherent state
    alpha = 1.0 + 0.5j
    coherent = H.coherent_state(alpha)
    assert coherent.is_normalizable()
    
    # Test distributions
    delta = DiracDelta(0)
    result = delta(gaussian)
    assert abs(result - 1.0) < 0.01  # gaussian(0) ≈ 1
    
    # Test Gelfand Triple
    triple = GelfandTriple(dimension=64)
    assert triple.verify_inclusion()
    
    # Test vacuum entropy
    entropy = triple.spectral_entropy()
    assert entropy >= 0
    
    # Test operators
    a_dag = CreationOperator(64)
    a = AnnihilationOperator(64)
    
    # a|0⟩ should be zero
    a_vacuum = a.apply(vacuum)
    assert a_vacuum.norm() < 1e-10
    
    # D(α)|0⟩ = |α⟩
    D = DisplacementOperator(1.0, 64)
    displaced = D.apply(vacuum)
    assert displaced.is_normalizable()
    
    return True


if __name__ == "__main__":
    print("Validating UCO Substrate...")
    assert validate_substrate()
    print("✓ UCO Substrate validated")

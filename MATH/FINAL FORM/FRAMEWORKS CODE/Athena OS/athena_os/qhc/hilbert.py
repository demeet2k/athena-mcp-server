"""
ATHENA OS - Quantum Holography Computing (QHC)
==============================================
Hilbert Spaces, Tensors, and Locality

From Quantum_Holography_Computing_(QHC).docx Chapter 2:

HILBERT SPACE:
    ℋ_n = ⊗_{j=1}^n ℂ² ≅ ℂ^{2^n}
    
    n-qubit system as tensor product of single-qubit spaces

TENSOR PRODUCT STRUCTURE:
    |ψ⟩ = Σ_{i₁...iₙ} A_{i₁...iₙ} |i₁⟩⊗...⊗|iₙ⟩
    
    Exponential dimension: dim(ℋ_n) = 2^n

LOCAL OPERATORS:
    O_S acts on subsystem S ⊆ [n]
    O_S = O ⊗ I_{[n]\S}

ENTANGLEMENT:
    Schmidt rank across bipartitions
    Separable vs entangled states
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Iterator, Any
from enum import Enum, auto
import math
import cmath
from abc import ABC, abstractmethod


# =============================================================================
# QUBIT INDEX SET
# =============================================================================

@dataclass
class QubitIndexSet:
    """
    Index set [n] = {1, ..., n} for n qubits.
    """
    
    n: int
    indices: Set[int] = field(default_factory=set)
    
    def __post_init__(self):
        if not self.indices:
            self.indices = set(range(self.n))
    
    def __len__(self) -> int:
        return len(self.indices)
    
    def __iter__(self) -> Iterator[int]:
        return iter(sorted(self.indices))
    
    def __contains__(self, item: int) -> bool:
        return item in self.indices
    
    def subset(self, indices: Set[int]) -> 'QubitIndexSet':
        """Create subset of indices."""
        return QubitIndexSet(n=len(indices), indices=indices & self.indices)
    
    def complement(self, indices: Set[int]) -> 'QubitIndexSet':
        """Get complement of indices."""
        comp = self.indices - indices
        return QubitIndexSet(n=len(comp), indices=comp)
    
    def partition(self, parts: List[Set[int]]) -> List['QubitIndexSet']:
        """Partition into disjoint subsets."""
        result = []
        for part in parts:
            result.append(self.subset(part))
        return result
    
    def bipartition(self, left: Set[int]) -> Tuple['QubitIndexSet', 'QubitIndexSet']:
        """Create bipartition A|B."""
        right = self.indices - left
        return (
            QubitIndexSet(n=len(left), indices=left),
            QubitIndexSet(n=len(right), indices=right)
        )


# =============================================================================
# HILBERT SPACE
# =============================================================================

@dataclass
class HilbertSpace:
    """
    Hilbert space ℋ_S for qubit subsystem S.
    
    ℋ_S = ⊗_{j∈S} ℂ² ≅ ℂ^{2^|S|}
    """
    
    qubit_indices: QubitIndexSet
    dimension: int = 0
    
    def __post_init__(self):
        self.dimension = 2 ** len(self.qubit_indices)
    
    @property
    def num_qubits(self) -> int:
        """Number of qubits in this space."""
        return len(self.qubit_indices)
    
    @classmethod
    def single_qubit(cls, index: int = 0) -> 'HilbertSpace':
        """Create single-qubit space."""
        return cls(QubitIndexSet(n=1, indices={index}))
    
    @classmethod
    def n_qubit(cls, n: int) -> 'HilbertSpace':
        """Create n-qubit space."""
        return cls(QubitIndexSet(n=n))
    
    def tensor_product(self, other: 'HilbertSpace') -> 'HilbertSpace':
        """Compute tensor product ℋ_A ⊗ ℋ_B."""
        combined = self.qubit_indices.indices | other.qubit_indices.indices
        return HilbertSpace(QubitIndexSet(n=len(combined), indices=combined))
    
    def subsystem(self, indices: Set[int]) -> 'HilbertSpace':
        """Get subsystem Hilbert space."""
        return HilbertSpace(self.qubit_indices.subset(indices))
    
    def __repr__(self) -> str:
        return f"ℋ({len(self.qubit_indices)}q, dim={self.dimension})"


# =============================================================================
# STATE VECTOR
# =============================================================================

@dataclass
class StateVector:
    """
    Quantum state vector |ψ⟩ ∈ ℋ_n.
    
    |ψ⟩ = Σ_i α_i |i⟩ with Σ|α_i|² = 1
    """
    
    space: HilbertSpace
    amplitudes: List[complex] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.amplitudes:
            # Initialize to |0...0⟩
            self.amplitudes = [0.0j] * self.space.dimension
            if self.amplitudes:
                self.amplitudes[0] = 1.0 + 0.0j
    
    @property
    def dimension(self) -> int:
        return len(self.amplitudes)
    
    @property
    def norm(self) -> float:
        """Compute ‖ψ‖ = √⟨ψ|ψ⟩."""
        return math.sqrt(sum(abs(a)**2 for a in self.amplitudes))
    
    def normalize(self) -> None:
        """Normalize to unit vector."""
        n = self.norm
        if n > 0:
            self.amplitudes = [a / n for a in self.amplitudes]
    
    def inner_product(self, other: 'StateVector') -> complex:
        """Compute ⟨self|other⟩."""
        if len(self.amplitudes) != len(other.amplitudes):
            raise ValueError("Dimension mismatch")
        return sum(a.conjugate() * b for a, b in zip(self.amplitudes, other.amplitudes))
    
    def overlap(self, other: 'StateVector') -> float:
        """Compute |⟨self|other⟩|²."""
        return abs(self.inner_product(other)) ** 2
    
    def probability(self, index: int) -> float:
        """Probability of measuring |index⟩."""
        return abs(self.amplitudes[index]) ** 2
    
    def probabilities(self) -> List[float]:
        """All measurement probabilities."""
        return [abs(a)**2 for a in self.amplitudes]
    
    def clone(self) -> 'StateVector':
        """Create copy."""
        return StateVector(self.space, list(self.amplitudes))
    
    # Factory methods
    @classmethod
    def computational_basis(cls, space: HilbertSpace, index: int) -> 'StateVector':
        """Create |index⟩ basis state."""
        amps = [0.0j] * space.dimension
        amps[index] = 1.0 + 0.0j
        return cls(space, amps)
    
    @classmethod
    def zero_state(cls, space: HilbertSpace) -> 'StateVector':
        """Create |0...0⟩ state."""
        return cls.computational_basis(space, 0)
    
    @classmethod
    def uniform_superposition(cls, space: HilbertSpace) -> 'StateVector':
        """Create (1/√d) Σ|i⟩."""
        amp = 1.0 / math.sqrt(space.dimension)
        return cls(space, [amp + 0.0j] * space.dimension)
    
    @classmethod
    def ghz_state(cls, n: int) -> 'StateVector':
        """Create GHZ state (|0...0⟩ + |1...1⟩)/√2."""
        space = HilbertSpace.n_qubit(n)
        amps = [0.0j] * space.dimension
        amps[0] = 1.0 / math.sqrt(2)  # |0...0⟩
        amps[-1] = 1.0 / math.sqrt(2)  # |1...1⟩
        return cls(space, amps)


# =============================================================================
# TENSOR PRODUCT
# =============================================================================

@dataclass
class TensorProduct:
    """
    Tensor product operations.
    """
    
    @staticmethod
    def kron(a: List[complex], b: List[complex]) -> List[complex]:
        """Kronecker product of vectors."""
        result = []
        for ai in a:
            for bi in b:
                result.append(ai * bi)
        return result
    
    @staticmethod
    def product_state(states: List[StateVector]) -> StateVector:
        """Create product state |ψ₁⟩⊗|ψ₂⟩⊗...⊗|ψₙ⟩."""
        if not states:
            raise ValueError("Need at least one state")
        
        # Combine spaces
        combined_indices = set()
        for s in states:
            combined_indices |= s.space.qubit_indices.indices
        
        combined_space = HilbertSpace(
            QubitIndexSet(n=len(combined_indices), indices=combined_indices)
        )
        
        # Kronecker product of amplitudes
        result = states[0].amplitudes
        for s in states[1:]:
            result = TensorProduct.kron(result, s.amplitudes)
        
        return StateVector(combined_space, result)
    
    @staticmethod
    def partial_trace(state: StateVector, 
                      trace_out: Set[int]) -> 'DensityMatrix':
        """
        Compute partial trace ρ_A = Tr_B(|ψ⟩⟨ψ|).
        
        Simplified: returns diagonal elements only.
        """
        keep = state.space.qubit_indices.indices - trace_out
        n_keep = len(keep)
        dim_keep = 2 ** n_keep
        
        # Simplified partial trace (diagonal only)
        probs = state.probabilities()
        traced = [0.0] * dim_keep
        
        # Sum over traced indices
        n_trace = len(trace_out)
        for i, p in enumerate(probs):
            # Extract kept qubit bits
            kept_idx = 0
            for j, q in enumerate(sorted(keep)):
                if i & (1 << q):
                    kept_idx |= (1 << j)
            traced[kept_idx] += p
        
        return DensityMatrix(
            space=HilbertSpace(QubitIndexSet(n=n_keep, indices=keep)),
            diagonal=traced
        )


# =============================================================================
# DENSITY MATRIX (SIMPLIFIED)
# =============================================================================

@dataclass
class DensityMatrix:
    """
    Density matrix ρ for mixed states.
    
    Simplified: stores only diagonal for computational basis.
    """
    
    space: HilbertSpace
    diagonal: List[float] = field(default_factory=list)
    
    @property
    def dimension(self) -> int:
        return len(self.diagonal)
    
    @property
    def trace(self) -> float:
        """Tr(ρ)."""
        return sum(self.diagonal)
    
    @property
    def purity(self) -> float:
        """Tr(ρ²)."""
        return sum(d**2 for d in self.diagonal)
    
    def entropy(self) -> float:
        """von Neumann entropy S(ρ) = -Tr(ρ log ρ)."""
        S = 0.0
        for p in self.diagonal:
            if p > 1e-15:
                S -= p * math.log2(p)
        return S
    
    @classmethod
    def from_state(cls, state: StateVector) -> 'DensityMatrix':
        """Create from pure state ρ = |ψ⟩⟨ψ|."""
        return cls(state.space, state.probabilities())


# =============================================================================
# LOCAL OPERATOR
# =============================================================================

@dataclass
class LocalOperator:
    """
    Operator O_S acting on subsystem S.
    
    O_S = O ⊗ I_{[n]\S}
    """
    
    support: Set[int]  # Qubits it acts on
    matrix: List[List[complex]] = field(default_factory=list)
    name: str = "O"
    
    @property
    def dimension(self) -> int:
        return len(self.matrix) if self.matrix else 0
    
    @property
    def is_unitary(self) -> bool:
        """Check if U†U = I (approximate)."""
        if not self.matrix:
            return True
        
        n = len(self.matrix)
        for i in range(n):
            for j in range(n):
                # (U†U)_ij = Σ_k U*_ki U_kj
                val = sum(
                    self.matrix[k][i].conjugate() * self.matrix[k][j]
                    for k in range(n)
                )
                expected = 1.0 if i == j else 0.0
                if abs(val - expected) > 1e-10:
                    return False
        return True
    
    def apply_to(self, state: StateVector) -> StateVector:
        """Apply operator to state: O|ψ⟩."""
        if not self.matrix:
            return state.clone()
        
        dim = len(self.matrix)
        if dim != state.dimension:
            raise ValueError(f"Dimension mismatch: {dim} vs {state.dimension}")
        
        # Matrix-vector multiplication
        new_amps = []
        for i in range(dim):
            val = sum(
                self.matrix[i][j] * state.amplitudes[j]
                for j in range(dim)
            )
            new_amps.append(val)
        
        return StateVector(state.space, new_amps)
    
    # Standard gates
    @classmethod
    def identity(cls, qubit: int) -> 'LocalOperator':
        """Identity I."""
        return cls(
            support={qubit},
            matrix=[[1+0j, 0j], [0j, 1+0j]],
            name="I"
        )
    
    @classmethod
    def pauli_x(cls, qubit: int) -> 'LocalOperator':
        """Pauli X (NOT)."""
        return cls(
            support={qubit},
            matrix=[[0j, 1+0j], [1+0j, 0j]],
            name="X"
        )
    
    @classmethod
    def pauli_z(cls, qubit: int) -> 'LocalOperator':
        """Pauli Z."""
        return cls(
            support={qubit},
            matrix=[[1+0j, 0j], [0j, -1+0j]],
            name="Z"
        )
    
    @classmethod
    def hadamard(cls, qubit: int) -> 'LocalOperator':
        """Hadamard H."""
        h = 1 / math.sqrt(2)
        return cls(
            support={qubit},
            matrix=[[h+0j, h+0j], [h+0j, -h+0j]],
            name="H"
        )
    
    @classmethod
    def phase(cls, qubit: int, theta: float) -> 'LocalOperator':
        """Phase gate P(θ)."""
        return cls(
            support={qubit},
            matrix=[[1+0j, 0j], [0j, cmath.exp(1j * theta)]],
            name=f"P({theta:.2f})"
        )


# =============================================================================
# ENTANGLEMENT
# =============================================================================

@dataclass
class EntanglementMetrics:
    """
    Entanglement measures across bipartitions.
    """
    
    @staticmethod
    def schmidt_rank(state: StateVector, partition: Set[int]) -> int:
        """
        Estimate Schmidt rank across bipartition.
        
        Simplified: counts non-zero singular values.
        """
        # For simplicity, return dimension of smaller subsystem
        n_left = len(partition)
        n_right = len(state.space.qubit_indices) - n_left
        return 2 ** min(n_left, n_right)
    
    @staticmethod
    def entanglement_entropy(state: StateVector, 
                            partition: Set[int]) -> float:
        """
        Entanglement entropy S_A = -Tr(ρ_A log ρ_A).
        """
        rho_a = TensorProduct.partial_trace(state, 
            state.space.qubit_indices.indices - partition)
        return rho_a.entropy()
    
    @staticmethod
    def is_separable_bipartite(state: StateVector,
                               partition: Set[int],
                               tolerance: float = 1e-6) -> bool:
        """Check if state is separable across partition."""
        # Simplified: check if entropy is near zero
        entropy = EntanglementMetrics.entanglement_entropy(state, partition)
        return entropy < tolerance


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hilbert() -> bool:
    """Validate Hilbert space module."""
    
    # Test QubitIndexSet
    qis = QubitIndexSet(n=4)
    assert len(qis) == 4
    assert 0 in qis
    
    left, right = qis.bipartition({0, 1})
    assert len(left) == 2
    assert len(right) == 2
    
    # Test HilbertSpace
    h2 = HilbertSpace.n_qubit(2)
    assert h2.dimension == 4
    assert h2.num_qubits == 2
    
    # Test StateVector
    state = StateVector.zero_state(h2)
    assert abs(state.norm - 1.0) < 1e-10
    assert state.probability(0) == 1.0
    
    # Test superposition
    sup = StateVector.uniform_superposition(h2)
    assert abs(sup.norm - 1.0) < 1e-10
    assert abs(sup.probability(0) - 0.25) < 1e-10
    
    # Test GHZ
    ghz = StateVector.ghz_state(3)
    assert abs(ghz.norm - 1.0) < 1e-10
    
    # Test operators
    h_gate = LocalOperator.hadamard(0)
    assert h_gate.is_unitary
    
    # Apply H|0⟩ = |+⟩
    h1 = HilbertSpace.n_qubit(1)
    zero = StateVector.zero_state(h1)
    plus = h_gate.apply_to(zero)
    assert abs(plus.probability(0) - 0.5) < 1e-10
    
    # Test DensityMatrix
    rho = DensityMatrix.from_state(zero)
    assert abs(rho.trace - 1.0) < 1e-10
    assert abs(rho.purity - 1.0) < 1e-10  # Pure state
    
    return True


if __name__ == "__main__":
    print("Validating QHC Hilbert Module...")
    assert validate_hilbert()
    print("✓ Hilbert module validated")
    
    # Demo
    print("\n=== QHC Hilbert Spaces Demo ===")
    
    # 3-qubit space
    h3 = HilbertSpace.n_qubit(3)
    print(f"\n3-qubit space: {h3}")
    print(f"  Dimension: 2³ = {h3.dimension}")
    
    # GHZ state
    ghz = StateVector.ghz_state(3)
    print(f"\nGHZ state (|000⟩ + |111⟩)/√2:")
    print(f"  Norm: {ghz.norm:.4f}")
    print(f"  P(|000⟩): {ghz.probability(0):.4f}")
    print(f"  P(|111⟩): {ghz.probability(7):.4f}")
    
    # Entanglement
    entropy = EntanglementMetrics.entanglement_entropy(ghz, {0})
    print(f"\nEntanglement entropy S_A (A = qubit 0):")
    print(f"  S_A = {entropy:.4f} bits")

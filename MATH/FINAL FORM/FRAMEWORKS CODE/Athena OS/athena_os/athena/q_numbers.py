"""
ATHENA OS - Q-NUMBERS
=====================
Quantum Value States, Channels, and Measurement

From ATHENA_AWAKEN_-_MATH_TOME.docx:

Q-NUMBERS (Value-States):
    A Q-number is ρ ∈ D(H) where:
    D(H) := {ρ ∈ T₁⁺(H) : Tr(ρ) = 1}
    
    - T₁(H): trace-class operators
    - T₁⁺(H): positive cone
    - ρ ≽ 0, Tr(ρ) = 1

CARRIERS:
    A carrier is a separable complex Hilbert space H equipped with:
    - Measurable value domain Ω
    - Probability measure μ on Ω
    - Canonical identification H ≅ L²(Ω,μ)

CHANNELS (CPTP Maps):
    A channel is CP+TP (completely positive, trace-preserving):
    Φ: T₁(H) → T₁(H')
    
INSTRUMENTS:
    An instrument is {Φₓ}ₓ∈X of CP-TN maps such that Σₓ Φₓ is a channel.
    
POVMS:
    A POVM on (Ω,Σ) is Π: Σ → B(H) with:
    - Π(E) ≽ 0
    - Π(Ω) = I
    
    Shadow law: S_Π(ρ)(E) := Tr(ρ Π(E))
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum, auto
import numpy as np
import math
from .crystal_structure import TypedTruth, OutcomeBundle, CrystalAddress, Lens, Facet, Atom


# =============================================================================
# CARRIER
# =============================================================================

@dataclass
class Carrier:
    """
    A carrier is a separable complex Hilbert space H.
    
    Equipped with:
    - Value domain Ω (dimension)
    - Reference structure for canonical identification
    """
    dimension: int
    name: str = "H"
    domain_type: str = "discrete"  # "discrete" or "continuous"
    
    def __post_init__(self):
        if self.dimension <= 0:
            raise ValueError("Carrier dimension must be positive")
    
    @property
    def identity(self) -> np.ndarray:
        """Identity operator I on H."""
        return np.eye(self.dimension, dtype=complex)
    
    def zero_state(self) -> np.ndarray:
        """Zero density operator."""
        return np.zeros((self.dimension, self.dimension), dtype=complex)
    
    def maximally_mixed(self) -> np.ndarray:
        """Maximally mixed state ρ = I/d."""
        return self.identity / self.dimension
    
    def basis_state(self, index: int) -> np.ndarray:
        """Pure state |i⟩⟨i|."""
        if index < 0 or index >= self.dimension:
            raise ValueError(f"Index {index} out of range for dimension {self.dimension}")
        rho = np.zeros((self.dimension, self.dimension), dtype=complex)
        rho[index, index] = 1.0
        return rho


# =============================================================================
# Q-NUMBER (VALUE-STATE)
# =============================================================================

@dataclass
class QNumber:
    """
    A Q-Number is a value-state ρ ∈ D(H).
    
    Definition 1.2: The admissible state space is
    D(H) := {ρ ∈ T₁⁺(H) : Tr(ρ) = 1}
    
    Properties:
    - ρ ≽ 0 (positive semidefinite)
    - Tr(ρ) = 1 (unit trace)
    """
    
    carrier: Carrier
    density_matrix: np.ndarray
    subnormalized: bool = False  # Allow Tr(ρ) < 1
    
    def __post_init__(self):
        d = self.carrier.dimension
        if self.density_matrix.shape != (d, d):
            raise ValueError(f"Density matrix shape {self.density_matrix.shape} doesn't match carrier dimension {d}")
    
    @classmethod
    def from_pure_state(cls, carrier: Carrier, psi: np.ndarray) -> 'QNumber':
        """Create from pure state |ψ⟩."""
        psi = psi / np.linalg.norm(psi)  # Normalize
        rho = np.outer(psi, psi.conj())
        return cls(carrier, rho)
    
    @classmethod
    def from_classical(cls, carrier: Carrier, probabilities: np.ndarray) -> 'QNumber':
        """Create classical (diagonal) state."""
        d = carrier.dimension
        if len(probabilities) != d:
            raise ValueError("Probability vector dimension mismatch")
        rho = np.diag(probabilities.astype(complex))
        return cls(carrier, rho)
    
    @classmethod
    def maximally_mixed(cls, carrier: Carrier) -> 'QNumber':
        """Create maximally mixed state."""
        return cls(carrier, carrier.maximally_mixed())
    
    @property
    def trace(self) -> float:
        """Tr(ρ)."""
        return np.real(np.trace(self.density_matrix))
    
    @property
    def is_normalized(self) -> bool:
        """Check if Tr(ρ) = 1."""
        return abs(self.trace - 1.0) < 1e-10
    
    @property
    def is_positive(self) -> bool:
        """Check if ρ ≽ 0."""
        eigenvalues = np.linalg.eigvalsh(self.density_matrix)
        return all(ev >= -1e-10 for ev in eigenvalues)
    
    @property
    def is_valid(self) -> bool:
        """Check if valid density operator."""
        if self.subnormalized:
            return self.is_positive and self.trace <= 1.0 + 1e-10
        return self.is_positive and self.is_normalized
    
    @property
    def purity(self) -> float:
        """Tr(ρ²) - equals 1 for pure states."""
        rho_sq = self.density_matrix @ self.density_matrix
        return np.real(np.trace(rho_sq))
    
    @property
    def is_pure(self) -> bool:
        """Check if pure state (Tr(ρ²) = 1)."""
        return abs(self.purity - 1.0) < 1e-10
    
    def von_neumann_entropy(self) -> float:
        """
        S(ρ) = -Tr(ρ log ρ).
        
        Entropy of the quantum state.
        """
        eigenvalues = np.linalg.eigvalsh(self.density_matrix)
        entropy = 0.0
        for ev in eigenvalues:
            if ev > 1e-15:
                entropy -= ev * np.log(ev)
        return entropy
    
    def expectation(self, observable: np.ndarray) -> complex:
        """Compute ⟨A⟩ = Tr(ρA)."""
        return np.trace(self.density_matrix @ observable)
    
    def partial_trace(self, subsystem_dims: Tuple[int, int], 
                     trace_out: int) -> 'QNumber':
        """
        Compute partial trace over a subsystem.
        
        For composite system H_A ⊗ H_B:
        - trace_out=0: trace over A
        - trace_out=1: trace over B
        """
        d_a, d_b = subsystem_dims
        rho = self.density_matrix.reshape((d_a, d_b, d_a, d_b))
        
        if trace_out == 0:
            # Trace over A
            result = np.einsum('ijik->jk', rho)
            new_carrier = Carrier(d_b, f"{self.carrier.name}_B")
        else:
            # Trace over B
            result = np.einsum('ijkj->ik', rho)
            new_carrier = Carrier(d_a, f"{self.carrier.name}_A")
        
        return QNumber(new_carrier, result)


# =============================================================================
# CHANNEL (CPTP MAP)
# =============================================================================

@dataclass
class Channel:
    """
    A Channel is a completely positive trace-preserving (CPTP) map.
    
    Φ: T₁(H) → T₁(H')
    
    Kraus representation: Φ(ρ) = Σᵢ Kᵢ ρ Kᵢ†
    with Σᵢ Kᵢ† Kᵢ = I (trace-preserving)
    """
    
    input_carrier: Carrier
    output_carrier: Carrier
    kraus_operators: List[np.ndarray]
    name: str = "Φ"
    
    def __post_init__(self):
        self._validate_kraus()
    
    def _validate_kraus(self) -> None:
        """Validate Kraus operators satisfy Σᵢ Kᵢ† Kᵢ = I."""
        d_in = self.input_carrier.dimension
        sum_kk = np.zeros((d_in, d_in), dtype=complex)
        for K in self.kraus_operators:
            sum_kk += K.conj().T @ K
        
        I = np.eye(d_in)
        if not np.allclose(sum_kk, I):
            raise ValueError("Kraus operators not trace-preserving")
    
    def apply(self, state: QNumber) -> QNumber:
        """
        Apply channel: Φ(ρ) = Σᵢ Kᵢ ρ Kᵢ†
        """
        rho = state.density_matrix
        result = np.zeros((self.output_carrier.dimension, 
                          self.output_carrier.dimension), dtype=complex)
        
        for K in self.kraus_operators:
            result += K @ rho @ K.conj().T
        
        return QNumber(self.output_carrier, result)
    
    @property
    def is_unitary(self) -> bool:
        """Check if channel is unitary (single Kraus operator)."""
        if len(self.kraus_operators) != 1:
            return False
        K = self.kraus_operators[0]
        return np.allclose(K @ K.conj().T, np.eye(self.output_carrier.dimension))
    
    @classmethod
    def identity(cls, carrier: Carrier) -> 'Channel':
        """Identity channel."""
        return cls(carrier, carrier, [np.eye(carrier.dimension)], "I")
    
    @classmethod
    def depolarizing(cls, carrier: Carrier, p: float) -> 'Channel':
        """
        Depolarizing channel: ρ → (1-p)ρ + (p/d)I
        """
        d = carrier.dimension
        # Kraus operators for depolarizing channel
        K0 = np.sqrt(1 - p + p/d) * np.eye(d)
        kraus = [K0]
        
        # Add generalized Pauli operators
        for i in range(d):
            for j in range(d):
                if i != j or i > 0:
                    K = np.zeros((d, d), dtype=complex)
                    K[i, j] = np.sqrt(p / d)
                    kraus.append(K)
        
        return cls(carrier, carrier, kraus, f"Depol({p})")
    
    @classmethod
    def dephasing(cls, carrier: Carrier) -> 'Channel':
        """
        Dephasing channel: removes off-diagonal elements.
        
        Δ(ρ) = Σₓ |x⟩⟨x| ρ |x⟩⟨x|
        """
        d = carrier.dimension
        kraus = []
        for i in range(d):
            K = np.zeros((d, d), dtype=complex)
            K[i, i] = 1.0
            kraus.append(K)
        return cls(carrier, carrier, kraus, "Dephase")


# =============================================================================
# POVM
# =============================================================================

@dataclass
class POVM:
    """
    A POVM (Positive Operator-Valued Measure).
    
    Definition: A POVM on (Ω, Σ) is Π: Σ → B(H) with:
    - Π(E) ≽ 0 for all E
    - Π(Ω) = I
    
    For discrete outcomes: {Eₓ}ₓ∈X with Σₓ Eₓ = I
    """
    
    carrier: Carrier
    effects: Dict[Any, np.ndarray]  # Outcome → Effect operator
    name: str = "Π"
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        """Validate POVM properties."""
        d = self.carrier.dimension
        
        # Check positivity
        for outcome, E in self.effects.items():
            eigenvalues = np.linalg.eigvalsh(E)
            if any(ev < -1e-10 for ev in eigenvalues):
                raise ValueError(f"Effect for outcome {outcome} not positive")
        
        # Check completeness: Σ Eₓ = I
        total = sum(self.effects.values())
        if not np.allclose(total, np.eye(d)):
            raise ValueError("POVM effects don't sum to identity")
    
    def probability(self, state: QNumber, outcome: Any) -> float:
        """
        Born rule: p(x) = Tr(ρ Eₓ)
        """
        E = self.effects.get(outcome)
        if E is None:
            return 0.0
        return np.real(np.trace(state.density_matrix @ E))
    
    def all_probabilities(self, state: QNumber) -> Dict[Any, float]:
        """Get all outcome probabilities."""
        return {x: self.probability(state, x) for x in self.effects}
    
    def shadow_law(self, state: QNumber) -> Dict[Any, float]:
        """
        The shadow law induced by (ρ, Π).
        
        S_Π(ρ)(E) := Tr(ρ Π(E))
        """
        return self.all_probabilities(state)
    
    @classmethod
    def computational_basis(cls, carrier: Carrier) -> 'POVM':
        """Standard computational basis measurement."""
        d = carrier.dimension
        effects = {}
        for i in range(d):
            E = np.zeros((d, d), dtype=complex)
            E[i, i] = 1.0
            effects[i] = E
        return cls(carrier, effects, "CompBasis")
    
    @classmethod
    def from_projectors(cls, carrier: Carrier, 
                       projectors: Dict[Any, np.ndarray]) -> 'POVM':
        """Create from orthogonal projectors."""
        return cls(carrier, projectors, "PVM")


# =============================================================================
# INSTRUMENT
# =============================================================================

@dataclass
class Instrument:
    """
    An Instrument is a family {Φₓ}ₓ∈X of CP-TN maps such that Σₓ Φₓ is a channel.
    
    Definition 1.8:
    - Induced outcome law: p(x) = Tr(Φₓ(ρ))
    - Posterior state: ρₓ = Φₓ(ρ)/p(x) when p(x) > 0
    """
    
    input_carrier: Carrier
    output_carrier: Carrier
    operations: Dict[Any, List[np.ndarray]]  # Outcome → Kraus ops
    name: str = "Inst"
    
    def apply(self, state: QNumber, outcome: Any) -> Tuple[float, Optional[QNumber]]:
        """
        Apply instrument for specific outcome.
        
        Returns (probability, posterior_state).
        """
        if outcome not in self.operations:
            return (0.0, None)
        
        kraus = self.operations[outcome]
        rho = state.density_matrix
        
        # Compute Φₓ(ρ)
        result = np.zeros((self.output_carrier.dimension,
                          self.output_carrier.dimension), dtype=complex)
        for K in kraus:
            result += K @ rho @ K.conj().T
        
        prob = np.real(np.trace(result))
        
        if prob < 1e-15:
            return (prob, None)
        
        # Normalize to get posterior
        posterior = QNumber(self.output_carrier, result / prob)
        return (prob, posterior)
    
    def full_statistics(self, state: QNumber) -> Dict[Any, Tuple[float, QNumber]]:
        """Get all outcomes with probabilities and posterior states."""
        results = {}
        for outcome in self.operations:
            prob, posterior = self.apply(state, outcome)
            if prob > 1e-15:
                results[outcome] = (prob, posterior)
        return results
    
    @classmethod
    def from_povm(cls, povm: POVM) -> 'Instrument':
        """
        Lüders instrument: non-destructive measurement.
        
        Φₓ(ρ) = √Eₓ ρ √Eₓ
        """
        operations = {}
        for outcome, E in povm.effects.items():
            # Compute √E
            eigenvalues, eigenvectors = np.linalg.eigh(E)
            sqrt_E = eigenvectors @ np.diag(np.sqrt(np.maximum(eigenvalues, 0))) @ eigenvectors.T
            operations[outcome] = [sqrt_E]
        
        return cls(povm.carrier, povm.carrier, operations, f"Lüders({povm.name})")


# =============================================================================
# VALIDATION
# =============================================================================

def validate_q_numbers() -> bool:
    """Validate the Q-Numbers module."""
    
    # Test Carrier
    H = Carrier(2, "qubit")
    assert H.dimension == 2
    assert H.identity.shape == (2, 2)
    
    # Test QNumber
    rho = H.maximally_mixed()
    q = QNumber(H, rho)
    assert q.is_valid
    assert abs(q.trace - 1.0) < 1e-10
    assert abs(q.purity - 0.5) < 1e-10
    
    # Test pure state
    psi = np.array([1, 0], dtype=complex)
    q_pure = QNumber.from_pure_state(H, psi)
    assert q_pure.is_pure
    assert abs(q_pure.purity - 1.0) < 1e-10
    assert abs(q_pure.von_neumann_entropy()) < 1e-10
    
    # Test Channel
    ch = Channel.identity(H)
    q2 = ch.apply(q)
    assert np.allclose(q.density_matrix, q2.density_matrix)
    
    dephase = Channel.dephasing(H)
    q3 = dephase.apply(q)
    assert q3.is_valid
    
    # Test POVM
    povm = POVM.computational_basis(H)
    probs = povm.all_probabilities(q)
    assert abs(sum(probs.values()) - 1.0) < 1e-10
    
    # Test Instrument
    inst = Instrument.from_povm(povm)
    stats = inst.full_statistics(q_pure)
    assert 0 in stats
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - Q-NUMBERS")
    print("Quantum Value States, Channels, and Measurement")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_q_numbers()
    print("✓ Module validated")
    
    # Demo
    print("\n--- QUBIT DEMO ---")
    H = Carrier(2, "qubit")
    
    # Create |+⟩ state
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    q = QNumber.from_pure_state(H, plus)
    print(f"State |+⟩: purity = {q.purity:.4f}, entropy = {q.von_neumann_entropy():.4f}")
    
    # Apply dephasing
    dephase = Channel.dephasing(H)
    q2 = dephase.apply(q)
    print(f"After dephasing: purity = {q2.purity:.4f}, entropy = {q2.von_neumann_entropy():.4f}")
    
    # Measure
    povm = POVM.computational_basis(H)
    probs = povm.shadow_law(q)
    print(f"Measurement probabilities: {probs}")

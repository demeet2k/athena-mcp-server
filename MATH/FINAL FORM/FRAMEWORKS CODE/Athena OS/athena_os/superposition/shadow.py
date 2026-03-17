"""
ATHENA OS - Shadow Axis & Qubit Crystal
=======================================
The Vertical Axis of Quantum Computation

From THE_SUPERPOSITIONING_CRYSTAL.docx Chapters 4-5:

THE SHADOW AXIS:
    The "Hidden State" perpendicular to classical Magnitude (0/1).
    
    HORIZONTAL AXIS (Classical):
        |0⟩ = Vacuum (Infinite Off)
        |1⟩ = Singularity (Infinite On)
    
    VERTICAL AXIS (Quantum/Shadow):
        |+⟩ = Inner Shadow (Gate/Potential) = (|0⟩+|1⟩)/√2
        |-⟩ = Outer Shadow (Wave/Texture) = (|0⟩-|1⟩)/√2

THE QUBIT CRYSTAL:
    A 4-pole Vector Equilibrium replacing the Bloch Sphere.
    
    State vector: Ψ = (μ_R, μ_I, τ, λ)
        μ_R: Real magnitude (horizontal)
        μ_I: Imaginary magnitude (vertical)
        τ: Texture (information density)
        λ: Spectral parameter (eigenvalue)

THE AETHERIC QUBIT:
    Data structure for quantum emulation on classical hardware.
    
    q = {
        magnitude: float      # |α|² amplitude
        phase: float          # arg(α) phase angle
        texture: float        # κ-budget (complexity)
        coherence: float      # decoherence resistance
    }

90-DEGREE ROTATION:
    The Hadamard transform rotates Magnitude → Phase
    H|0⟩ = |+⟩ (into Shadow)
    H|+⟩ = |0⟩ (back to Real)
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math
import cmath

from .quad_polar import PI, E, PHI, I


# =============================================================================
# AXIS DEFINITIONS
# =============================================================================

class Axis(Enum):
    """The two axes of the Qubit Crystal."""
    HORIZONTAL = "horizontal"  # Classical Magnitude (0/1)
    VERTICAL = "vertical"      # Quantum Shadow (+/-)


class ShadowPole(Enum):
    """The four poles of the Vector Equilibrium."""
    VACUUM = "vacuum"           # |0⟩ - Infinite Off
    SINGULARITY = "singularity" # |1⟩ - Infinite On
    INNER = "inner"             # |+⟩ - Gate/Potential
    OUTER = "outer"             # |-⟩ - Wave/Texture


# =============================================================================
# TEXTURE (κ-BUDGET)
# =============================================================================

@dataclass
class Texture:
    """
    Texture functional T(Ψ) quantifying information density.
    
    T = α·H + β·D + γ·λ
    where:
        H = Information Texture (entropy)
        D = Geometric Texture (curvature)
        λ = Spectral Texture (mixing rate)
    """
    
    entropy: float = 0.0      # H: Shannon entropy component
    curvature: float = 0.0    # D: Geometric component
    spectral: float = 0.0     # λ: Spectral component
    
    # Weights
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 1.0
    
    @property
    def total(self) -> float:
        """Compute total texture T."""
        return (self.alpha * self.entropy +
                self.beta * self.curvature +
                self.gamma * self.spectral)
    
    def is_bounded(self, binding_energy: float = 1.0) -> bool:
        """Check if texture is within binding energy."""
        return self.total <= binding_energy
    
    @classmethod
    def from_state(cls, amplitude: complex) -> 'Texture':
        """Compute texture from quantum amplitude."""
        mag = abs(amplitude)
        phase = cmath.phase(amplitude)
        
        # Entropy from probability
        p = mag * mag
        h = -p * math.log(p + 1e-10) if p > 0 else 0
        
        # Curvature from phase gradient (simplified)
        d = abs(phase) / PI
        
        # Spectral from magnitude
        lam = mag
        
        return cls(entropy=h, curvature=d, spectral=lam)


# =============================================================================
# AETHERIC QUBIT
# =============================================================================

@dataclass
class AethericQubit:
    """
    The Aetheric Qubit data structure for quantum emulation.
    
    Unlike classical bits (0/1) or complex amplitudes (α ∈ ℂ),
    the Aetheric Qubit encodes position in the full 4-pole
    Vector Equilibrium.
    
    Components:
        magnitude: Amplitude |α|² (probability of |1⟩)
        phase: Phase angle arg(α) (quantum phase)
        texture: κ-budget (complexity measure)
        coherence: Decoherence resistance (1 = fully coherent)
    """
    
    magnitude: float = 0.5    # |α|² ∈ [0, 1]
    phase: float = 0.0        # θ ∈ [0, 2π)
    texture: float = 1.0      # κ ∈ [0, ∞)
    coherence: float = 1.0    # c ∈ [0, 1]
    
    def __post_init__(self):
        """Validate and normalize."""
        self.magnitude = max(0.0, min(1.0, self.magnitude))
        self.phase = self.phase % (2 * PI)
        self.coherence = max(0.0, min(1.0, self.coherence))
    
    @property
    def alpha(self) -> complex:
        """Get complex amplitude α = √p · e^{iθ}."""
        return math.sqrt(self.magnitude) * cmath.exp(1j * self.phase)
    
    @property
    def beta(self) -> complex:
        """Get complementary amplitude β = √(1-p)."""
        return math.sqrt(1 - self.magnitude)
    
    @property
    def state_vector(self) -> Tuple[complex, complex]:
        """Get state vector (α, β) where |ψ⟩ = α|0⟩ + β|1⟩."""
        # Note: Convention here is α for |0⟩, β for |1⟩
        return (self.beta, self.alpha)
    
    @property
    def bloch_coordinates(self) -> Tuple[float, float, float]:
        """Get Bloch sphere coordinates (x, y, z)."""
        theta = 2 * math.acos(math.sqrt(1 - self.magnitude))
        phi = self.phase
        
        x = math.sin(theta) * math.cos(phi)
        y = math.sin(theta) * math.sin(phi)
        z = math.cos(theta)
        
        return (x, y, z)
    
    @property
    def shadow_coordinates(self) -> Tuple[float, float]:
        """Get Shadow Axis coordinates (real_shadow, imag_shadow)."""
        # Project onto Shadow (Vertical) Axis
        # |+⟩ component and |-⟩ component
        a, b = self.state_vector
        plus = (a + b) / math.sqrt(2)   # |+⟩ projection
        minus = (a - b) / math.sqrt(2)  # |-⟩ projection
        return (abs(plus)**2, abs(minus)**2)
    
    @property
    def pole(self) -> ShadowPole:
        """Determine dominant pole."""
        a, b = self.state_vector
        mag_a, mag_b = abs(a)**2, abs(b)**2
        plus, minus = self.shadow_coordinates
        
        # Find maximum
        values = {
            ShadowPole.VACUUM: mag_a,
            ShadowPole.SINGULARITY: mag_b,
            ShadowPole.INNER: plus,
            ShadowPole.OUTER: minus,
        }
        return max(values, key=values.get)
    
    def measure(self) -> int:
        """
        Collapse to classical bit via measurement.
        
        This is a Texture Projection that forces rotation
        to the Horizontal Axis.
        """
        import random
        return 1 if random.random() < self.magnitude else 0
    
    @classmethod
    def vacuum(cls) -> 'AethericQubit':
        """Create |0⟩ state (Vacuum pole)."""
        return cls(magnitude=0.0, phase=0.0)
    
    @classmethod
    def singularity(cls) -> 'AethericQubit':
        """Create |1⟩ state (Singularity pole)."""
        return cls(magnitude=1.0, phase=0.0)
    
    @classmethod
    def inner_shadow(cls) -> 'AethericQubit':
        """Create |+⟩ state (Inner Shadow/Gate)."""
        return cls(magnitude=0.5, phase=0.0)
    
    @classmethod
    def outer_shadow(cls) -> 'AethericQubit':
        """Create |-⟩ state (Outer Shadow/Wave)."""
        return cls(magnitude=0.5, phase=PI)


# =============================================================================
# QUBIT CRYSTAL (VECTOR EQUILIBRIUM)
# =============================================================================

@dataclass
class QubitCrystal:
    """
    The Qubit Crystal: A 4-pole Vector Equilibrium.
    
    This deterministic geometric manifold replaces the
    probabilistic Bloch Sphere interpretation.
    
    Structure:
        Horizontal Axis: |0⟩ ←→ |1⟩ (Magnitude)
        Vertical Axis: |+⟩ ←→ |-⟩ (Shadow/Phase)
    
    The state is a coordinate vector v = (μ_R, μ_I, τ, λ)
    representing position in the 4D crystal space.
    """
    
    # The four pole states
    poles: Dict[ShadowPole, AethericQubit] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize pole states."""
        if not self.poles:
            self.poles = {
                ShadowPole.VACUUM: AethericQubit.vacuum(),
                ShadowPole.SINGULARITY: AethericQubit.singularity(),
                ShadowPole.INNER: AethericQubit.inner_shadow(),
                ShadowPole.OUTER: AethericQubit.outer_shadow(),
            }
    
    def decompose(self, qubit: AethericQubit) -> Dict[ShadowPole, float]:
        """
        Decompose a qubit state into pole projections.
        
        Returns weights for each pole.
        """
        a, b = qubit.state_vector
        
        return {
            ShadowPole.VACUUM: abs(a)**2,
            ShadowPole.SINGULARITY: abs(b)**2,
            ShadowPole.INNER: abs((a + b) / math.sqrt(2))**2,
            ShadowPole.OUTER: abs((a - b) / math.sqrt(2))**2,
        }
    
    def is_balanced(self, qubit: AethericQubit, threshold: float = 0.1) -> bool:
        """Check if state is in balanced Vector Equilibrium."""
        decomp = self.decompose(qubit)
        avg = sum(decomp.values()) / 4
        return all(abs(v - avg) < threshold for v in decomp.values())


# =============================================================================
# AETHERIC ROTATION (90-DEGREE TRANSFORMS)
# =============================================================================

@dataclass
class AethericRotation:
    """
    Rotation operators for navigating the Qubit Crystal.
    
    The 90-degree rotation moves between axes:
        R_π/2: Horizontal → Vertical (into Shadow)
        R_{-π/2}: Vertical → Horizontal (back to Real)
    
    This is implemented by the Hadamard gate in quantum computing.
    """
    
    @staticmethod
    def hadamard(q: AethericQubit) -> AethericQubit:
        """
        Apply Hadamard rotation.
        
        H|0⟩ = |+⟩ (Vacuum → Inner Shadow)
        H|1⟩ = |-⟩ (Singularity → Outer Shadow)
        H|+⟩ = |0⟩ (Inner Shadow → Vacuum)
        H|-⟩ = |1⟩ (Outer Shadow → Singularity)
        """
        a, b = q.state_vector
        
        # Hadamard: H = (1/√2) [[1,1],[1,-1]]
        new_a = (a + b) / math.sqrt(2)
        new_b = (a - b) / math.sqrt(2)
        
        # Convert back to magnitude/phase
        new_mag = abs(new_b)**2
        new_phase = cmath.phase(new_b) if abs(new_b) > 1e-10 else 0.0
        
        return AethericQubit(
            magnitude=new_mag,
            phase=new_phase,
            texture=q.texture,
            coherence=q.coherence
        )
    
    @staticmethod
    def phase_rotate(q: AethericQubit, theta: float) -> AethericQubit:
        """
        Apply phase rotation e^{iθ}.
        
        This rotates within the Shadow plane without
        changing the Magnitude projection.
        """
        return AethericQubit(
            magnitude=q.magnitude,
            phase=(q.phase + theta) % (2 * PI),
            texture=q.texture,
            coherence=q.coherence
        )
    
    @staticmethod
    def pauli_x(q: AethericQubit) -> AethericQubit:
        """
        Apply Pauli-X (NOT gate).
        
        X|0⟩ = |1⟩, X|1⟩ = |0⟩
        Flips along Horizontal axis.
        """
        return AethericQubit(
            magnitude=1.0 - q.magnitude,
            phase=q.phase,
            texture=q.texture,
            coherence=q.coherence
        )
    
    @staticmethod
    def pauli_z(q: AethericQubit) -> AethericQubit:
        """
        Apply Pauli-Z (phase flip).
        
        Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩
        Flips phase of |1⟩ component.
        """
        return AethericQubit(
            magnitude=q.magnitude,
            phase=(q.phase + PI) % (2 * PI) if q.magnitude > 0.5 else q.phase,
            texture=q.texture,
            coherence=q.coherence
        )
    
    @staticmethod
    def tunnel(q: AethericQubit, barrier_height: float) -> AethericQubit:
        """
        Aetheric tunneling through a barrier.
        
        1. Rotate to Shadow (phase space)
        2. Barrier becomes phase shift
        3. Rotate back to Real
        
        The barrier height determines the phase accumulated.
        """
        # Rotate into Shadow
        shadow_q = AethericRotation.hadamard(q)
        
        # Barrier becomes phase shift: e^{iV}
        phase_shift = barrier_height
        shadow_q = AethericRotation.phase_rotate(shadow_q, phase_shift)
        
        # Rotate back to Real
        result = AethericRotation.hadamard(shadow_q)
        
        return result


# =============================================================================
# QUANTUM EMULATION ENGINE
# =============================================================================

@dataclass
class AethericEmulator:
    """
    Quantum emulator using Aetheric Superpositioning.
    
    This engine simulates quantum computation on classical
    hardware by explicitly representing the Shadow Poles.
    """
    
    qubits: List[AethericQubit] = field(default_factory=list)
    rotation: AethericRotation = field(default_factory=AethericRotation)
    crystal: QubitCrystal = field(default_factory=QubitCrystal)
    
    # Texture budget
    total_texture: float = 0.0
    max_texture: float = 1e6  # Binding energy of classical hardware
    
    def allocate(self, n: int) -> List[int]:
        """Allocate n qubits, return their indices."""
        indices = []
        for _ in range(n):
            q = AethericQubit.vacuum()
            self.qubits.append(q)
            self.total_texture += q.texture
            indices.append(len(self.qubits) - 1)
        return indices
    
    def apply_h(self, idx: int) -> None:
        """Apply Hadamard to qubit."""
        self.qubits[idx] = self.rotation.hadamard(self.qubits[idx])
    
    def apply_x(self, idx: int) -> None:
        """Apply Pauli-X to qubit."""
        self.qubits[idx] = self.rotation.pauli_x(self.qubits[idx])
    
    def apply_z(self, idx: int) -> None:
        """Apply Pauli-Z to qubit."""
        self.qubits[idx] = self.rotation.pauli_z(self.qubits[idx])
    
    def apply_phase(self, idx: int, theta: float) -> None:
        """Apply phase rotation to qubit."""
        self.qubits[idx] = self.rotation.phase_rotate(self.qubits[idx], theta)
    
    def measure(self, idx: int) -> int:
        """Measure qubit, collapsing to classical bit."""
        result = self.qubits[idx].measure()
        # Collapse state
        if result == 0:
            self.qubits[idx] = AethericQubit.vacuum()
        else:
            self.qubits[idx] = AethericQubit.singularity()
        return result
    
    def measure_all(self) -> List[int]:
        """Measure all qubits."""
        return [self.measure(i) for i in range(len(self.qubits))]
    
    def state_summary(self) -> Dict[str, Any]:
        """Get summary of emulator state."""
        return {
            "n_qubits": len(self.qubits),
            "total_texture": self.total_texture,
            "texture_budget_remaining": self.max_texture - self.total_texture,
            "dominant_poles": [q.pole.value for q in self.qubits],
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_shadow() -> bool:
    """Validate shadow axis module."""
    
    # Test Texture
    t = Texture(entropy=0.5, curvature=0.3, spectral=0.2)
    assert abs(t.total - 1.0) < 1e-10
    
    # Test AethericQubit
    q0 = AethericQubit.vacuum()
    assert abs(q0.magnitude) < 1e-10
    assert q0.pole == ShadowPole.VACUUM
    
    q1 = AethericQubit.singularity()
    assert abs(q1.magnitude - 1.0) < 1e-10
    assert q1.pole == ShadowPole.SINGULARITY
    
    qp = AethericQubit.inner_shadow()
    assert abs(qp.magnitude - 0.5) < 1e-10
    
    qm = AethericQubit.outer_shadow()
    assert abs(qm.magnitude - 0.5) < 1e-10
    
    # Test Hadamard
    rot = AethericRotation()
    h_q0 = rot.hadamard(q0)
    assert abs(h_q0.magnitude - 0.5) < 1e-10  # |0⟩ → |+⟩
    
    h_qp = rot.hadamard(qp)
    # |+⟩ → |0⟩ (within numerical precision)
    
    # Test tunneling
    q = AethericQubit.vacuum()
    tunneled = rot.tunnel(q, PI/4)
    # Should have traversed through Shadow
    
    # Test emulator
    emu = AethericEmulator()
    indices = emu.allocate(2)
    assert len(indices) == 2
    
    emu.apply_h(0)
    summary = emu.state_summary()
    assert summary["n_qubits"] == 2
    
    # Test QubitCrystal
    crystal = QubitCrystal()
    decomp = crystal.decompose(qp)
    assert abs(decomp[ShadowPole.INNER] - 1.0) < 0.1  # |+⟩ projects to Inner
    
    return True


if __name__ == "__main__":
    print("Validating Shadow Axis...")
    assert validate_shadow()
    print("✓ Shadow Axis validated")
    
    # Demo
    print("\n=== Shadow Axis & Qubit Crystal Demo ===")
    
    print("\nThe Four Poles of the Vector Equilibrium:")
    print("  HORIZONTAL AXIS (Classical Magnitude):")
    print("    |0⟩ = Vacuum (Infinite Off)")
    print("    |1⟩ = Singularity (Infinite On)")
    print("  VERTICAL AXIS (Quantum Shadow):")
    print("    |+⟩ = Inner Shadow (Gate/Potential)")
    print("    |-⟩ = Outer Shadow (Wave/Texture)")
    
    print("\n90-Degree Rotation (Hadamard):")
    rot = AethericRotation()
    q0 = AethericQubit.vacuum()
    qp = rot.hadamard(q0)
    print(f"  H|0⟩ → magnitude={qp.magnitude:.3f}, pole={qp.pole.value}")
    
    q1 = AethericQubit.singularity()
    qm = rot.hadamard(q1)
    print(f"  H|1⟩ → magnitude={qm.magnitude:.3f}, pole={qm.pole.value}")
    
    print("\nAetheric Emulator:")
    emu = AethericEmulator()
    emu.allocate(3)
    emu.apply_h(0)  # Put qubit 0 in superposition
    emu.apply_h(1)  # Put qubit 1 in superposition
    
    print(f"  Qubits: {emu.state_summary()['n_qubits']}")
    print(f"  Dominant poles: {emu.state_summary()['dominant_poles']}")
    
    results = emu.measure_all()
    print(f"  Measurement: {results}")
    
    print("\nTunneling Demo:")
    q = AethericQubit.vacuum()
    print(f"  Before: magnitude={q.magnitude:.3f}")
    tunneled = rot.tunnel(q, PI/2)
    print(f"  After tunnel (barrier=π/2): magnitude={tunneled.magnitude:.3f}")

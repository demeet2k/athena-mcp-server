"""
ATHENA OS - Aether Object and Face Projectors
==============================================
The Aether is the 4→1 artifact that contains Z* as its neutral center
but also contains the generator structure that can re-expand into four pillars.

Aether = (Z*, τ, F, J, Ω, G, I)

Where:
- Z*: neutral core state (zero point)
- τ(x): gate parameter (can be constant or field)
- F: field doublet (F, G)
- J: source doublet (J_m, J_e)
- Ω: invariant symplectic form (Earth clamp)
- G: generator set {d, *, □, M(τ), Ω, ∂}
- I: invariant set {d²=0, d(*J_e)=0, d(*J_m)=0, Ω-pairing, θ~θ+2π}

The 4 Faces:
- Fire face: sources (J_e, J_m) channel
- Water face: propagation operators (□, G_ret, Δt)
- Air face: duality gate (τ(x), M(τ), SL(2,Z))
- Earth face: constraints (Ω, lattice clamps, BCs, H_dR)

Expand(A) = (Fire, Water, Air, Earth)
Collapse(Fire, Water, Air, Earth) = A

The superposition lens version:
    A = Z* + λ_F·Π_F + λ_W·Π_W + λ_A·Π_A + λ_E·Π_E
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
import numpy as np
import math

from .duality import (
    TauParameter, SL2ZElement, FieldDoublet, SourceDoublet,
    DyonCharge, AxionField, EMDualityStack, PI, TAU
)


# =============================================================================
# FACE TYPES
# =============================================================================

class Face(Enum):
    """The four elemental faces of Aether."""
    FIRE = 0    # Sources, initiation, impulse
    WATER = 1   # Propagation, flow, adaptation
    AIR = 2     # Duality gate, structure, routing
    EARTH = 3   # Constraints, embodiment, verification
    
    @property
    def symbol(self) -> str:
        """Get face symbol."""
        symbols = {
            Face.FIRE: "??",
            Face.WATER: "??",
            Face.AIR: "??",
            Face.EARTH: "??"
        }
        return symbols[self]
    
    @property
    def primary_function(self) -> str:
        """Get primary function."""
        functions = {
            Face.FIRE: "Initiation / impulse / ignition",
            Face.WATER: "Adaptation / flow / shaping",
            Face.AIR: "Structure through relation / mapping",
            Face.EARTH: "Constraint / embodiment / verification"
        }
        return functions[self]


# =============================================================================
# FACE PROJECTORS
# =============================================================================

@dataclass
class FaceProjector:
    """
    A projector Π_i that extracts one face from Aether.
    
    Fire face: Π_F(A) = J = (J_m, J_e)
    Water face: Π_W(A) = {□, G_ret, Δt}
    Air face: Π_A(A) = {τ(x), M(τ), SL(2,Z)}
    Earth face: Π_E(A) = {Ω, lattice clamps, BCs}
    """
    
    face: Face
    
    # What this projector extracts
    components: List[str] = field(default_factory=list)
    
    # Weight in superposition
    weight: float = 1.0
    
    # Is this face active?
    active: bool = True
    
    def __post_init__(self):
        """Set default components for each face."""
        if not self.components:
            defaults = {
                Face.FIRE: ["J_e", "J_m", "sources", "currents"],
                Face.WATER: ["propagator", "Green_ret", "wave_eq", "dispersion"],
                Face.AIR: ["tau", "M_tau", "SL2Z", "theta_mixing"],
                Face.EARTH: ["Omega", "lattice_clamp", "BCs", "cohomology"]
            }
            self.components = defaults[self.face]


@dataclass
class ProjectorSet:
    """
    The complete set of 4 projectors.
    
    Aether can be written as:
        A = Z* + λ_F·Π_F + λ_W·Π_W + λ_A·Π_A + λ_E·Π_E
    """
    
    fire: FaceProjector = field(default_factory=lambda: FaceProjector(Face.FIRE))
    water: FaceProjector = field(default_factory=lambda: FaceProjector(Face.WATER))
    air: FaceProjector = field(default_factory=lambda: FaceProjector(Face.AIR))
    earth: FaceProjector = field(default_factory=lambda: FaceProjector(Face.EARTH))
    
    def get(self, face: Face) -> FaceProjector:
        """Get projector for a face."""
        mapping = {
            Face.FIRE: self.fire,
            Face.WATER: self.water,
            Face.AIR: self.air,
            Face.EARTH: self.earth
        }
        return mapping[face]
    
    def active_faces(self) -> List[Face]:
        """Get list of active faces."""
        return [f for f in Face if self.get(f).active]
    
    def lens_mask(self) -> int:
        """
        Get 4-bit lens mask indicating active faces.
        
        bit 0 = Fire
        bit 1 = Water
        bit 2 = Air
        bit 3 = Earth
        """
        mask = 0
        if self.fire.active:
            mask |= 1
        if self.water.active:
            mask |= 2
        if self.air.active:
            mask |= 4
        if self.earth.active:
            mask |= 8
        return mask
    
    @classmethod
    def from_lens_mask(cls, mask: int) -> 'ProjectorSet':
        """Create from 4-bit lens mask."""
        ps = cls()
        ps.fire.active = bool(mask & 1)
        ps.water.active = bool(mask & 2)
        ps.air.active = bool(mask & 4)
        ps.earth.active = bool(mask & 8)
        return ps
    
    def total_weight(self) -> float:
        """Sum of active weights."""
        return sum(self.get(f).weight for f in self.active_faces())
    
    def normalize_weights(self) -> None:
        """Normalize weights to sum to 1."""
        total = self.total_weight()
        if total > 0:
            for face in Face:
                p = self.get(face)
                p.weight /= total


# =============================================================================
# GENERATOR SET
# =============================================================================

class Generator(Enum):
    """
    The generator set G_EM = {d, *, □, M(τ), Ω, ∂}
    """
    D = 0       # Exterior derivative d
    STAR = 1    # Hodge star *
    BOX = 2     # D'Alembertian □
    M_TAU = 3   # Constitutive matrix M(τ)
    OMEGA = 4   # Symplectic form Ω
    PARTIAL = 5 # Partial derivative ∂
    BC = 6      # Boundary conditions


@dataclass
class GeneratorSet:
    """
    The generator set for EM Aether.
    
    Contains the operators needed to regenerate the full structure.
    """
    
    active: Set[Generator] = field(default_factory=lambda: {
        Generator.D, Generator.STAR
    })
    
    def add(self, gen: Generator) -> None:
        """Add a generator."""
        self.active.add(gen)
    
    def remove(self, gen: Generator) -> None:
        """Remove a generator."""
        self.active.discard(gen)
    
    def has(self, gen: Generator) -> bool:
        """Check if generator is active."""
        return gen in self.active
    
    def mask(self) -> int:
        """Get 8-bit generator mask."""
        result = 0
        for gen in self.active:
            result |= (1 << gen.value)
        return result
    
    @classmethod
    def from_mask(cls, mask: int) -> 'GeneratorSet':
        """Create from mask."""
        gs = cls(active=set())
        for gen in Generator:
            if mask & (1 << gen.value):
                gs.add(gen)
        return gs
    
    @classmethod
    def minimal_em(cls) -> 'GeneratorSet':
        """Minimal generators for EM: {d, *}."""
        return cls(active={Generator.D, Generator.STAR})
    
    @classmethod
    def full_em(cls) -> 'GeneratorSet':
        """Full generators: {d, *, □, M(τ), Ω, ∂, BC}."""
        return cls(active=set(Generator))


# =============================================================================
# INVARIANT SET
# =============================================================================

class Invariant(Enum):
    """
    The invariant set I_EM.
    
    These are the constraints that must hold.
    """
    D_SQUARED = 0      # d² = 0
    ELECTRIC_CONSERVED = 1  # d(*J_e) = 0
    MAGNETIC_CONSERVED = 2  # d(*J_m) = 0
    OMEGA_PAIRING = 3  # Symplectic pairing invariant
    THETA_PERIODIC = 4  # θ ~ θ + 2π


@dataclass
class InvariantSet:
    """The set of invariants for EM Aether."""
    
    required: Set[Invariant] = field(default_factory=lambda: set(Invariant))
    
    def check_all(self) -> Dict[Invariant, bool]:
        """Check all invariants (placeholder - returns all True)."""
        return {inv: True for inv in self.required}
    
    def is_valid(self) -> bool:
        """Check if all invariants hold."""
        return all(self.check_all().values())


# =============================================================================
# ZERO POINT
# =============================================================================

@dataclass
class ZeroPoint:
    """
    The Zero Point Z* - the neutral core of Aether.
    
    Z* is the balanced state where all faces commute.
    It's determined by the constraint intersection.
    """
    
    # Core values at zero point
    tau_zero: complex = complex(0, 1)  # τ at Z*
    field_zero: complex = 0.0
    source_zero: complex = 0.0
    
    # Stability
    is_stable: bool = True
    
    def distance_from(self, tau: complex) -> float:
        """Distance from Z* in τ-space."""
        return abs(tau - self.tau_zero)
    
    def is_at_zero_point(self, tau: complex, tol: float = 1e-10) -> bool:
        """Check if at zero point."""
        return self.distance_from(tau) < tol


# =============================================================================
# AETHER OBJECT
# =============================================================================

@dataclass
class Aether:
    """
    The Aether object - the complete 4→1 artifact.
    
    Aether = (Z*, τ, F, J, Ω, G, I)
    
    Contains:
    - Z*: neutral core state
    - Projectors: the 4-face extraction system
    - Generators: the operator set
    - Invariants: the constraint set
    
    Can expand to 4 faces and collapse back.
    """
    
    # The neutral core
    zero_point: ZeroPoint = field(default_factory=ZeroPoint)
    
    # The coupling parameter
    tau: TauParameter = field(default_factory=TauParameter)
    
    # Field content
    field_doublet: FieldDoublet = field(default_factory=FieldDoublet)
    source_doublet: SourceDoublet = field(default_factory=SourceDoublet)
    
    # Projector set
    projectors: ProjectorSet = field(default_factory=ProjectorSet)
    
    # Generators and invariants
    generators: GeneratorSet = field(default_factory=GeneratorSet.minimal_em)
    invariants: InvariantSet = field(default_factory=InvariantSet)
    
    # Axion (optional)
    axion: Optional[AxionField] = None
    
    def expand(self) -> Dict[Face, Dict[str, Any]]:
        """
        Expand Aether into 4 faces.
        
        Expand(A) = (Fire, Water, Air, Earth)
        """
        result = {}
        
        # Fire face: sources
        if self.projectors.fire.active:
            result[Face.FIRE] = {
                'J_e': self.source_doublet.J_e,
                'J_m': self.source_doublet.J_m,
                'components': self.projectors.fire.components
            }
        
        # Water face: propagation
        if self.projectors.water.active:
            result[Face.WATER] = {
                'propagator': 'box',  # □
                'Green_ret': 'G_ret',
                'dispersion': self.tau.imag_part,
                'components': self.projectors.water.components
            }
        
        # Air face: duality gate
        if self.projectors.air.active:
            result[Face.AIR] = {
                'tau': self.tau.tau,
                'M_tau': self.tau.tilt_matrix(),
                'theta': self.tau.theta,
                'components': self.projectors.air.components
            }
        
        # Earth face: constraints
        if self.projectors.earth.active:
            result[Face.EARTH] = {
                'Omega': 'symplectic_form',
                'invariants': list(self.invariants.required),
                'generators': list(self.generators.active),
                'components': self.projectors.earth.components
            }
        
        return result
    
    @classmethod
    def collapse(cls, faces: Dict[Face, Dict[str, Any]]) -> 'Aether':
        """
        Collapse 4 faces back into Aether.
        
        Collapse(Fire, Water, Air, Earth) = A
        """
        aether = cls()
        
        # Set active projectors
        for face in Face:
            aether.projectors.get(face).active = face in faces
        
        # Extract from Fire face
        if Face.FIRE in faces:
            fire = faces[Face.FIRE]
            aether.source_doublet = SourceDoublet(
                J_e=fire.get('J_e', 0.0),
                J_m=fire.get('J_m', 0.0)
            )
        
        # Extract from Air face
        if Face.AIR in faces:
            air = faces[Face.AIR]
            if 'tau' in air:
                aether.tau = TauParameter.from_tau(air['tau'])
            elif 'theta' in air:
                aether.tau = TauParameter(theta=air['theta'])
        
        return aether
    
    def apply_duality(self, element: SL2ZElement) -> 'Aether':
        """Apply SL(2,Z) duality transformation."""
        new_tau = TauParameter.from_tau(
            element.act_on_tau(self.tau.tau)
        )
        
        return Aether(
            zero_point=self.zero_point,
            tau=new_tau,
            field_doublet=self.field_doublet.apply_sl2z(element),
            source_doublet=self.source_doublet.apply_sl2z(element),
            projectors=self.projectors,
            generators=self.generators,
            invariants=self.invariants,
            axion=self.axion
        )
    
    def is_at_zero_point(self) -> bool:
        """Check if at Z*."""
        return self.zero_point.is_at_zero_point(self.tau.tau)
    
    def verify_invariants(self) -> bool:
        """Verify all invariants hold."""
        return self.invariants.is_valid()
    
    def superposition_form(self) -> str:
        """
        Return the superposition lens formula.
        
        A = Z* + λ_F·Π_F + λ_W·Π_W + λ_A·Π_A + λ_E·Π_E
        """
        terms = ["Z*"]
        for face in Face:
            p = self.projectors.get(face)
            if p.active:
                terms.append(f"{p.weight:.2f}·Π_{face.name[0]}")
        return " + ".join(terms)


# =============================================================================
# AETHER FACTORY
# =============================================================================

class AetherFactory:
    """Factory for creating standard Aether configurations."""
    
    @staticmethod
    def pure_maxwell_vacuum() -> Aether:
        """Pure Maxwell vacuum: Water + Earth faces."""
        aether = Aether(
            tau=TauParameter(theta=0.0, e_squared=1.0)
        )
        aether.projectors.fire.active = False
        aether.projectors.water.active = True
        aether.projectors.air.active = False
        aether.projectors.earth.active = True
        
        aether.generators = GeneratorSet(active={
            Generator.D, Generator.STAR, Generator.BOX
        })
        
        return aether
    
    @staticmethod
    def topological_insulator(theta: float = PI) -> Aether:
        """Pinned TI with θ interface: Air + Earth faces."""
        aether = Aether(
            tau=TauParameter(theta=theta, e_squared=4*PI)
        )
        aether.projectors.fire.active = False
        aether.projectors.water.active = False
        aether.projectors.air.active = True
        aether.projectors.earth.active = True
        
        aether.generators = GeneratorSet(active={
            Generator.D, Generator.STAR, Generator.M_TAU, Generator.BC
        })
        
        return aether
    
    @staticmethod
    def axion_cavity(m_a: float = 1e-5, Q: float = 1e6) -> Aether:
        """Axion conversion in cavity: Air + Water + Earth faces."""
        aether = Aether(
            tau=TauParameter(theta=0.0, e_squared=1.0),
            axion=AxionField(m_a=m_a, g_agamma=1e-10)
        )
        aether.projectors.fire.active = False
        aether.projectors.water.active = True
        aether.projectors.air.active = True
        aether.projectors.earth.active = True
        
        aether.generators = GeneratorSet(active={
            Generator.D, Generator.STAR, Generator.BOX, Generator.M_TAU
        })
        
        return aether
    
    @staticmethod
    def full_duality_stack() -> Aether:
        """Full EM-Duality-Axion stack: all 4 faces."""
        aether = Aether(
            tau=TauParameter(theta=0.0, e_squared=4*PI),
            axion=AxionField()
        )
        # All faces active
        for face in Face:
            aether.projectors.get(face).active = True
        
        aether.generators = GeneratorSet.full_em()
        
        return aether


# =============================================================================
# VALIDATION
# =============================================================================

def validate_aether() -> bool:
    """Validate Aether module."""
    
    # Test ProjectorSet
    ps = ProjectorSet()
    assert ps.lens_mask() == 15  # All active = 1111
    
    ps.fire.active = False
    assert ps.lens_mask() == 14  # 1110
    
    ps2 = ProjectorSet.from_lens_mask(14)
    assert not ps2.fire.active
    assert ps2.water.active
    
    # Test GeneratorSet
    gs = GeneratorSet.minimal_em()
    assert gs.has(Generator.D)
    assert gs.has(Generator.STAR)
    assert not gs.has(Generator.BOX)
    
    # Test Aether expand/collapse
    aether = Aether(
        tau=TauParameter(theta=PI/2, e_squared=1.0),
        source_doublet=SourceDoublet(J_e=1.0, J_m=0.0)
    )
    
    faces = aether.expand()
    assert Face.FIRE in faces
    assert faces[Face.FIRE]['J_e'] == 1.0
    
    collapsed = Aether.collapse(faces)
    assert collapsed.source_doublet.J_e == 1.0
    
    # Test factory
    maxwell = AetherFactory.pure_maxwell_vacuum()
    assert not maxwell.projectors.fire.active
    assert maxwell.projectors.water.active
    
    ti = AetherFactory.topological_insulator()
    assert abs(ti.tau.theta - PI) < 1e-10
    
    # Test duality
    J = SL2ZElement.J()
    rotated = aether.apply_duality(J)
    # τ → -1/τ under J
    
    return True


if __name__ == "__main__":
    print("Validating Aether Module...")
    assert validate_aether()
    print("✓ Aether Module validated")
    
    # Demo
    print("\n=== Aether Object Demo ===")
    
    print("\nCreating full duality stack:")
    aether = AetherFactory.full_duality_stack()
    print(f"  Superposition: {aether.superposition_form()}")
    print(f"  Lens mask: {aether.projectors.lens_mask():04b}")
    print(f"  τ = {aether.tau.tau}")
    
    print("\nExpanding to 4 faces:")
    faces = aether.expand()
    for face, data in faces.items():
        print(f"  {face.symbol} {face.name}: {list(data.keys())}")
    
    print("\nPure Maxwell vacuum:")
    maxwell = AetherFactory.pure_maxwell_vacuum()
    print(f"  Superposition: {maxwell.superposition_form()}")
    print(f"  Active faces: {[f.name for f in maxwell.projectors.active_faces()]}")
    
    print("\nTopological Insulator (θ = π):")
    ti = AetherFactory.topological_insulator()
    print(f"  θ = {ti.tau.theta:.4f} = π")
    print(f"  Active faces: {[f.name for f in ti.projectors.active_faces()]}")

"""
ATHENA OS - ATOMIST SUBSTRATE
=============================
The Discrete Hardware Layer

From Greek_Corpus__LF-OS_.docx:

THE ATOMIST DFA:
    Reality executes as a Deterministic Finite Automaton (DFA)
    governed by Ananke (Necessity).

MINIMAL STATE CARRIERS (ATOMS):
    - Persistent, indivisible identity tokens
    - Immutable shape (sphere, pyramid, hook, cube)
    - Atomic Persistence Invariant: ∀t: A(t) = A(t₀)
    - Properties: position x(t), velocity v(t), shape σ

THE VOID (SPARSE ADDRESS SPACE):
    - Contains no state (data = ∅)
    - Provides traversable memory space
    - Enables collision events at boundaries
    - Complementary duality: Atom/Void = Signal/Noise

EVENT-DRIVEN STATE TRANSITIONS:
    x_i(t+τ) = x_i(t) + v_i(t)τ
    v_i(t+τ) = v_i(t) until collision
    
    Collision = Instruction execution primitive
    Maps local input state → local output state

COMPOUND FORMATION:
    - Binding graph: nodes=atoms, edges=relations
    - Stability threshold τ_β for perturbation tolerance
    - Decay = failure of persistence conditions
    - Macro-laws emerge from micro-traces
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, FrozenSet
from enum import Enum, auto
import math
import random
from collections import defaultdict


# =============================================================================
# ATOMIC SHAPES
# =============================================================================

class AtomicShape(Enum):
    """Immutable atomic shapes - the basis of matter variety."""
    SPHERE = auto()     # Smooth, mobile
    PYRAMID = auto()    # Sharp, penetrating (fire-like)
    HOOK = auto()       # Binding capability
    CUBE = auto()       # Stable, structural
    CYLINDER = auto()   # Rolling capability
    IRREGULAR = auto()  # Complex binding sites


@dataclass(frozen=True)
class ShapeProfile:
    """Physical profile of an atomic shape."""
    
    shape: AtomicShape
    volume: float
    binding_sites: int
    mobility_factor: float  # 0-1, affects collision dynamics
    
    @classmethod
    def from_shape(cls, shape: AtomicShape) -> 'ShapeProfile':
        """Create profile from shape type."""
        profiles = {
            AtomicShape.SPHERE: (1.0, 0, 1.0),
            AtomicShape.PYRAMID: (0.5, 3, 0.8),
            AtomicShape.HOOK: (0.3, 2, 0.6),
            AtomicShape.CUBE: (1.0, 6, 0.4),
            AtomicShape.CYLINDER: (0.8, 2, 0.9),
            AtomicShape.IRREGULAR: (0.7, 4, 0.5),
        }
        vol, sites, mob = profiles[shape]
        return cls(shape, vol, sites, mob)


# =============================================================================
# THE ATOM (MINIMAL STATE CARRIER)
# =============================================================================

@dataclass
class Atom:
    """
    An Atom - the minimal state carrier.
    
    Properties:
    - Persistent, indivisible identity token
    - Immutable shape (σ)
    - Position x(t) in the void
    - Velocity v(t) for traversal
    
    Atomic Persistence Invariant: ∀t: A(t) = A(t₀)
    """
    
    atom_id: int
    shape: AtomicShape
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    mass: float = 1.0
    
    _creation_id: int = field(default=None, repr=False)
    
    def __post_init__(self):
        if self._creation_id is None:
            self._creation_id = self.atom_id
        self.profile = ShapeProfile.from_shape(self.shape)
    
    @property
    def identity_preserved(self) -> bool:
        """Verify atomic persistence invariant."""
        return self.atom_id == self._creation_id
    
    def propagate(self, dt: float) -> None:
        """
        Deterministic propagation between events.
        
        x_i(t+τ) = x_i(t) + v_i(t)τ
        """
        for i in range(3):
            self.position[i] += self.velocity[i] * dt
    
    def set_velocity(self, new_velocity: List[float]) -> None:
        """Update velocity (only at collision events)."""
        self.velocity = list(new_velocity)
    
    @property
    def kinetic_energy(self) -> float:
        """Calculate kinetic energy."""
        v_squared = sum(v**2 for v in self.velocity)
        return 0.5 * self.mass * v_squared
    
    def distance_to(self, other: 'Atom') -> float:
        """Calculate distance to another atom."""
        return math.sqrt(sum(
            (a - b)**2 for a, b in zip(self.position, other.position)
        ))


# =============================================================================
# THE VOID (SPARSE ADDRESS SPACE)
# =============================================================================

@dataclass
class VoidRegion:
    """
    A region of the Void - the sparse address space.
    
    Properties:
    - Contains no state (data = ∅)
    - Provides traversable memory space
    - Boundaries define collision potential
    """
    
    min_bounds: Tuple[float, float, float]
    max_bounds: Tuple[float, float, float]
    
    @property
    def volume(self) -> float:
        """Calculate void volume."""
        return math.prod(
            self.max_bounds[i] - self.min_bounds[i] 
            for i in range(3)
        )
    
    def contains(self, position: List[float]) -> bool:
        """Check if position is within void region."""
        return all(
            self.min_bounds[i] <= position[i] <= self.max_bounds[i]
            for i in range(3)
        )
    
    def is_empty(self) -> bool:
        """Void contains no state by definition."""
        return True  # Always true for void


class Void:
    """
    The complete Void - the address space for atomic traversal.
    
    Complementary duality: Atom/Void = Signal/Noise
    """
    
    def __init__(self, size: float = 1000.0):
        self.region = VoidRegion(
            min_bounds=(-size/2, -size/2, -size/2),
            max_bounds=(size/2, size/2, size/2)
        )
        self.atoms: Dict[int, Atom] = {}
    
    def register_atom(self, atom: Atom) -> None:
        """Register atom in void space."""
        self.atoms[atom.atom_id] = atom
    
    def get_atoms_in_region(self, region: VoidRegion) -> List[Atom]:
        """Get all atoms within a region."""
        return [
            atom for atom in self.atoms.values()
            if region.contains(atom.position)
        ]
    
    @property
    def atom_count(self) -> int:
        """Count of atoms in void."""
        return len(self.atoms)
    
    @property
    def void_ratio(self) -> float:
        """Ratio of void to atom volume."""
        total_atom_volume = sum(
            atom.profile.volume for atom in self.atoms.values()
        )
        return 1.0 - (total_atom_volume / self.region.volume)


# =============================================================================
# COLLISION EVENTS
# =============================================================================

@dataclass
class CollisionEvent:
    """
    A Collision Event - the instruction execution primitive.
    
    Maps local input state → local output state
    Characterized by:
    - Participant set P (typically |P| = 2)
    - Deterministic update operator Δ_COL
    """
    
    event_id: int
    time: float
    participants: Tuple[int, int]  # Atom IDs
    contact_normal: Tuple[float, float, float]
    pre_velocities: Tuple[List[float], List[float]]
    post_velocities: Tuple[List[float], List[float]] = None
    
    @property
    def is_committed(self) -> bool:
        """Check if event has been executed."""
        return self.post_velocities is not None


class CollisionOperator:
    """
    The Collision Update Operator (Δ_COL).
    
    Executes deterministic state transitions at collision boundaries.
    S(t⁺) = Δ_COL(S(t⁻); i, j, π)
    """
    
    def __init__(self, coefficient_of_restitution: float = 1.0):
        self.cor = coefficient_of_restitution  # 1.0 = elastic
    
    def detect_collision(self, atom1: Atom, atom2: Atom,
                        collision_radius: float = 1.0) -> bool:
        """Detect if two atoms are colliding."""
        distance = atom1.distance_to(atom2)
        threshold = collision_radius * (
            atom1.profile.volume + atom2.profile.volume
        ) ** (1/3)
        return distance <= threshold
    
    def compute_contact_normal(self, atom1: Atom, 
                               atom2: Atom) -> Tuple[float, float, float]:
        """Compute contact normal vector."""
        dx = [atom2.position[i] - atom1.position[i] for i in range(3)]
        magnitude = math.sqrt(sum(d**2 for d in dx))
        if magnitude == 0:
            return (1.0, 0.0, 0.0)
        return tuple(d / magnitude for d in dx)
    
    def execute(self, atom1: Atom, atom2: Atom,
               normal: Tuple[float, float, float]) -> Tuple[List[float], List[float]]:
        """
        Execute collision update.
        
        Elastic collision in 3D with conservation of momentum.
        """
        m1, m2 = atom1.mass, atom2.mass
        v1, v2 = atom1.velocity, atom2.velocity
        
        # Relative velocity along normal
        rel_vel = sum((v1[i] - v2[i]) * normal[i] for i in range(3))
        
        if rel_vel > 0:
            # Already separating
            return list(v1), list(v2)
        
        # Impulse magnitude
        j = -(1 + self.cor) * rel_vel / (1/m1 + 1/m2)
        
        # New velocities
        new_v1 = [v1[i] + (j/m1) * normal[i] for i in range(3)]
        new_v2 = [v2[i] - (j/m2) * normal[i] for i in range(3)]
        
        return new_v1, new_v2


# =============================================================================
# NECESSITY ENGINE
# =============================================================================

class NecessityEngine:
    """
    The Necessity Engine (Ananke) - governs all state transitions.
    
    Properties:
    - Non-Intervention Axiom: No external agency modifies outcomes
    - Identical inputs → Identical outputs
    - Closed, auditable transition system
    """
    
    def __init__(self):
        self.collision_operator = CollisionOperator()
        self.event_queue: List[CollisionEvent] = []
        self.event_counter = 0
        self.execution_trace: List[CollisionEvent] = []
    
    def schedule_event(self, event: CollisionEvent) -> None:
        """Add event to queue ordered by time."""
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda e: e.time)
    
    def execute_next_event(self, atoms: Dict[int, Atom]) -> Optional[CollisionEvent]:
        """
        Execute the next scheduled event.
        
        Non-intervention: identical pre-states → identical post-states
        """
        if not self.event_queue:
            return None
        
        event = self.event_queue.pop(0)
        
        atom1 = atoms[event.participants[0]]
        atom2 = atoms[event.participants[1]]
        
        # Execute deterministic update
        new_v1, new_v2 = self.collision_operator.execute(
            atom1, atom2, event.contact_normal
        )
        
        # Update atoms
        atom1.set_velocity(new_v1)
        atom2.set_velocity(new_v2)
        
        # Record post-state
        event.post_velocities = (new_v1, new_v2)
        
        # Add to trace
        self.execution_trace.append(event)
        
        return event
    
    def create_event(self, atom1: Atom, atom2: Atom, 
                    time: float) -> CollisionEvent:
        """Create a new collision event."""
        self.event_counter += 1
        normal = self.collision_operator.compute_contact_normal(atom1, atom2)
        
        return CollisionEvent(
            event_id=self.event_counter,
            time=time,
            participants=(atom1.atom_id, atom2.atom_id),
            contact_normal=normal,
            pre_velocities=(list(atom1.velocity), list(atom2.velocity))
        )
    
    def verify_causality(self) -> bool:
        """Verify causal closure of transition system."""
        # All events should have matching pre/post states
        for event in self.execution_trace:
            if not event.is_committed:
                return False
        return True


# =============================================================================
# COMPOUND FORMATION
# =============================================================================

@dataclass
class BindingEdge:
    """A binding relation between two atoms."""
    atom_ids: FrozenSet[int]
    binding_strength: float
    binding_type: str = "structural"


class Compound:
    """
    A Compound - organized aggregate of atoms.
    
    Modeled as a binding graph:
    - Nodes = atoms
    - Edges = relational constraints
    
    Stability determined by perturbation tolerance τ_β
    """
    
    def __init__(self, compound_id: int):
        self.compound_id = compound_id
        self.atoms: Set[int] = set()
        self.bindings: List[BindingEdge] = []
        self.stability_threshold: float = 1.0
    
    def add_atom(self, atom_id: int) -> None:
        """Add atom to compound."""
        self.atoms.add(atom_id)
    
    def add_binding(self, atom1_id: int, atom2_id: int,
                   strength: float = 1.0) -> None:
        """Create binding between atoms."""
        if atom1_id in self.atoms and atom2_id in self.atoms:
            edge = BindingEdge(
                frozenset({atom1_id, atom2_id}),
                strength
            )
            self.bindings.append(edge)
    
    @property
    def binding_graph_density(self) -> float:
        """Calculate density of binding graph."""
        n = len(self.atoms)
        if n < 2:
            return 0.0
        max_edges = n * (n - 1) / 2
        return len(self.bindings) / max_edges
    
    def compute_stress(self, perturbation: float) -> float:
        """Compute internal stress from perturbation."""
        # Stress increases with perturbation, decreases with binding strength
        avg_strength = (
            sum(b.binding_strength for b in self.bindings) / len(self.bindings)
            if self.bindings else 0.0
        )
        return perturbation / (avg_strength + 0.1)
    
    def is_stable(self, perturbation: float) -> bool:
        """
        Check stability under perturbation.
        
        Stable if stress < threshold τ_β
        """
        stress = self.compute_stress(perturbation)
        return stress < self.stability_threshold
    
    def decay(self) -> List[int]:
        """
        Trigger decay - release atoms from bindings.
        
        Decay = failure of persistence conditions
        Returns list of freed atom IDs
        """
        freed = list(self.atoms)
        self.atoms.clear()
        self.bindings.clear()
        return freed


# =============================================================================
# THE ATOMIST DFA
# =============================================================================

class AtomistDFA:
    """
    The complete Atomist Deterministic Finite Automaton.
    
    Reality executes as a DFA governed by Ananke (Necessity).
    """
    
    def __init__(self, void_size: float = 1000.0):
        self.void = Void(void_size)
        self.necessity = NecessityEngine()
        self.compounds: Dict[int, Compound] = {}
        self.atom_counter = 0
        self.compound_counter = 0
        self.current_time = 0.0
    
    def create_atom(self, shape: AtomicShape,
                   position: List[float] = None,
                   velocity: List[float] = None) -> Atom:
        """Create and register a new atom."""
        self.atom_counter += 1
        atom = Atom(
            atom_id=self.atom_counter,
            shape=shape,
            position=position or [0.0, 0.0, 0.0],
            velocity=velocity or [0.0, 0.0, 0.0]
        )
        self.void.register_atom(atom)
        return atom
    
    def propagate_all(self, dt: float) -> None:
        """Propagate all atoms through void."""
        self.current_time += dt
        for atom in self.void.atoms.values():
            atom.propagate(dt)
    
    def detect_all_collisions(self, collision_radius: float = 1.0
                             ) -> List[Tuple[Atom, Atom]]:
        """Detect all collisions in current state."""
        collisions = []
        atoms = list(self.void.atoms.values())
        
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                if self.necessity.collision_operator.detect_collision(
                    atoms[i], atoms[j], collision_radius
                ):
                    collisions.append((atoms[i], atoms[j]))
        
        return collisions
    
    def step(self, dt: float) -> Dict[str, Any]:
        """
        Execute one simulation step.
        
        1. Propagate atoms
        2. Detect collisions
        3. Execute collision events
        """
        # Propagate
        self.propagate_all(dt)
        
        # Detect collisions
        collisions = self.detect_all_collisions()
        
        # Create and execute events
        events_executed = 0
        for atom1, atom2 in collisions:
            event = self.necessity.create_event(
                atom1, atom2, self.current_time
            )
            self.necessity.schedule_event(event)
            self.necessity.execute_next_event(self.void.atoms)
            events_executed += 1
        
        return {
            "time": self.current_time,
            "atoms": self.void.atom_count,
            "collisions": events_executed,
            "void_ratio": self.void.void_ratio
        }
    
    def create_compound(self, atom_ids: List[int]) -> Compound:
        """Create a compound from atoms."""
        self.compound_counter += 1
        compound = Compound(self.compound_counter)
        for aid in atom_ids:
            compound.add_atom(aid)
        self.compounds[compound.compound_id] = compound
        return compound
    
    def verify_system_integrity(self) -> Dict[str, bool]:
        """Verify all system invariants."""
        return {
            "atomic_persistence": all(
                a.identity_preserved for a in self.void.atoms.values()
            ),
            "causal_closure": self.necessity.verify_causality(),
            "void_is_empty": self.void.region.is_empty()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_atomist_substrate() -> bool:
    """Validate the atomist substrate module."""
    
    # Test atom creation
    atom = Atom(1, AtomicShape.SPHERE, [0, 0, 0], [1, 0, 0])
    assert atom.identity_preserved
    
    # Test propagation
    atom.propagate(1.0)
    assert atom.position == [1.0, 0.0, 0.0]
    
    # Test void
    void = Void(100.0)
    void.register_atom(atom)
    assert void.atom_count == 1
    assert void.void_ratio > 0.99
    
    # Test collision operator
    atom1 = Atom(1, AtomicShape.SPHERE, [0, 0, 0], [1, 0, 0])
    atom2 = Atom(2, AtomicShape.SPHERE, [2, 0, 0], [-1, 0, 0])
    
    col_op = CollisionOperator()
    normal = col_op.compute_contact_normal(atom1, atom2)
    assert abs(normal[0] - 1.0) < 0.01
    
    # Test compound
    compound = Compound(1)
    compound.add_atom(1)
    compound.add_atom(2)
    compound.add_binding(1, 2, 1.0)
    assert compound.is_stable(0.5)
    
    # Test DFA
    dfa = AtomistDFA(100.0)
    a1 = dfa.create_atom(AtomicShape.SPHERE, [0, 0, 0], [1, 0, 0])
    a2 = dfa.create_atom(AtomicShape.SPHERE, [5, 0, 0], [-1, 0, 0])
    
    # Run simulation
    for _ in range(10):
        dfa.step(0.1)
    
    # Verify integrity
    integrity = dfa.verify_system_integrity()
    assert integrity["atomic_persistence"]
    assert integrity["causal_closure"]
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - ATOMIST SUBSTRATE")
    print("The Discrete Hardware Layer")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_atomist_substrate()
    print("✓ Module validated")
    
    # Demo
    print("\n--- ATOMIST DFA SIMULATION ---")
    dfa = AtomistDFA(100.0)
    
    # Create atoms
    atoms = [
        dfa.create_atom(AtomicShape.SPHERE, [0, 0, 0], [2, 1, 0]),
        dfa.create_atom(AtomicShape.CUBE, [10, 0, 0], [-1, 0.5, 0]),
        dfa.create_atom(AtomicShape.PYRAMID, [5, 5, 0], [0, -1, 0])
    ]
    
    print(f"Created {len(atoms)} atoms in void")
    print(f"Initial void ratio: {dfa.void.void_ratio:.6f}")
    
    # Run simulation
    print("\nRunning 20 steps...")
    for i in range(20):
        result = dfa.step(0.5)
        if result["collisions"] > 0:
            print(f"  Step {i+1}: {result['collisions']} collision(s)")
    
    print(f"\nFinal time: {dfa.current_time}")
    print(f"Total events: {len(dfa.necessity.execution_trace)}")
    
    integrity = dfa.verify_system_integrity()
    print(f"\n--- INTEGRITY CHECK ---")
    for check, passed in integrity.items():
        print(f"  {check}: {'✓' if passed else '✗'}")

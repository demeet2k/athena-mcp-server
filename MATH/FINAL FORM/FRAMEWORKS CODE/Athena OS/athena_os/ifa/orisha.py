"""
ATHENA OS - IFÁ KERNEL: ORISHA MODULE
=====================================
The Orisha Operator Algebra - Transformations on State Space

THE ORISHA AS OPERATORS:
    The Orisha are not "gods" but OPERATORS - systematic transformations
    that act on the state vector of reality.
    
    Each Orisha has:
    - Domain: The subspace it affects
    - Signature: The characteristic transformation
    - Eigenspectrum: Stable configurations (eigenstates)

OPERATOR HIERARCHY:

    TIER 1 - CREATION OPERATORS (Primordial):
        Obàtálá  - Creation/Molding: potential → form
        Odùduwà  - Foundation: establishes metric tensor
        Ọrúnmìlà - Witness: collapses superposition
        Èṣù      - Messenger: generates transitions

    TIER 2 - DYNAMICAL OPERATORS (Processes):
        Ògún     - Cutting: removes obstacles (|0⟩⟨1|)
        Ṣàngó    - Transformation: applies voltage
        Yemọja   - Flow/Memory: coherent channel
        Ọ̀ṣun     - Attraction: generates gravity wells
        Ọya      - Transition: death/rebirth operator

    TIER 3 - SPECIALIZED OPERATORS:
        Ṣọ̀pọ̀nná  - Purification: entropy removal
        Ọ̀sanyìn  - Healing: restoration operator
        Babaluaiye - Decay/Renewal: cycle operator

MATHEMATICAL FORMALISM:
    - Operators are 256×256 matrices
    - Èṣù is the non-commutative generator
    - [Ô_i, Ô_j] ≠ 0 for most Orisha pairs

SOURCES:
    - Traditional Ifá corpus
    - HBAS-Ω Protocol: Ọpẹ́-256 formalization
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import numpy as np

from .hypercube import Q8Hypercube, Odu, OduSuperposition


# =============================================================================
# ORISHA CLASSIFICATION
# =============================================================================

class OrishaTier(Enum):
    """Hierarchical tiers of Orisha operators."""
    
    PRIMORDIAL = "primordial"     # Tier 1: Creation operators
    DYNAMICAL = "dynamical"       # Tier 2: Process operators
    SPECIALIZED = "specialized"   # Tier 3: Domain-specific operators


class OrishaType(Enum):
    """Types of Orisha by function."""
    
    # Tier 1 - Primordial
    OBATALA = "obatala"       # Creation/Molding
    ODUDUWA = "oduduwa"       # Foundation
    ORUNMILA = "orunmila"     # Witness/Knowledge
    ESU = "esu"               # Messenger/Transition
    
    # Tier 2 - Dynamical
    OGUN = "ogun"             # Cutting/Iron
    SANGO = "sango"           # Thunder/Transformation
    YEMOJA = "yemoja"         # Ocean/Memory
    OSUN = "osun"             # River/Attraction
    OYA = "oya"               # Wind/Death-Rebirth
    
    # Tier 3 - Specialized
    SOPONNA = "soponna"       # Smallpox/Purification
    OSANYIN = "osanyin"       # Herbs/Healing
    BABALUAIYE = "babaluaiye" # Earth/Disease


# =============================================================================
# ORISHA OPERATOR
# =============================================================================

@dataclass
class Orisha:
    """
    An Orisha - an operator acting on the Odù state space.
    
    Mathematical properties:
    - Represented as 256×256 matrix
    - Acts on |Ψ⟩ via Ô|Ψ⟩
    - Has characteristic eigenspectrum
    """
    
    orisha_type: OrishaType
    tier: OrishaTier
    name: str
    
    # The operator matrix (256×256)
    matrix: np.ndarray = field(default_factory=lambda: np.eye(256))
    
    # Orisha properties
    domain: str = ""           # Sphere of influence
    signature: str = ""        # Characteristic action
    colors: List[str] = field(default_factory=list)
    number: int = 0            # Sacred number
    day: str = ""              # Sacred day
    
    # Associated Odù (eigenstates)
    associated_odu: List[int] = field(default_factory=list)
    
    def apply(self, state: np.ndarray) -> np.ndarray:
        """Apply operator to state vector."""
        return self.matrix @ state
    
    def apply_superposition(self, sup: OduSuperposition) -> OduSuperposition:
        """Apply operator to superposition."""
        new_amps = self.apply(sup.amplitudes)
        return OduSuperposition(new_amps)
    
    def commutator(self, other: Orisha) -> np.ndarray:
        """Calculate commutator [self, other] = self·other - other·self."""
        return self.matrix @ other.matrix - other.matrix @ self.matrix
    
    def anticommutator(self, other: Orisha) -> np.ndarray:
        """Calculate anticommutator {self, other} = self·other + other·self."""
        return self.matrix @ other.matrix + other.matrix @ self.matrix
    
    def commutes_with(self, other: Orisha, tolerance: float = 1e-10) -> bool:
        """Check if operators commute."""
        comm = self.commutator(other)
        return np.allclose(comm, np.zeros_like(comm), atol=tolerance)
    
    def eigenspectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get eigenvalues and eigenvectors."""
        return np.linalg.eig(self.matrix)
    
    def is_unitary(self) -> bool:
        """Check if operator is unitary."""
        product = self.matrix @ self.matrix.conj().T
        return np.allclose(product, np.eye(256))
    
    def is_hermitian(self) -> bool:
        """Check if operator is Hermitian (observable)."""
        return np.allclose(self.matrix, self.matrix.conj().T)
    
    def trace(self) -> complex:
        """Calculate trace."""
        return np.trace(self.matrix)
    
    def norm(self) -> float:
        """Calculate Frobenius norm."""
        return float(np.linalg.norm(self.matrix))


# =============================================================================
# OPERATOR GENERATORS
# =============================================================================

class OrishaGenerator:
    """
    Generates Orisha operators with specific mathematical properties.
    """
    
    @staticmethod
    def create_identity() -> np.ndarray:
        """Identity operator."""
        return np.eye(256, dtype=np.complex128)
    
    @staticmethod
    def create_bit_flip(bit: int) -> np.ndarray:
        """
        Create single bit-flip operator.
        
        Flips bit 'bit' in all states.
        """
        matrix = np.zeros((256, 256), dtype=np.complex128)
        for i in range(256):
            j = i ^ (1 << bit)
            matrix[j, i] = 1.0
        return matrix
    
    @staticmethod
    def create_phase_shift(bit: int, phase: float = np.pi) -> np.ndarray:
        """
        Create phase shift operator on states with bit set.
        """
        matrix = np.eye(256, dtype=np.complex128)
        for i in range(256):
            if i & (1 << bit):
                matrix[i, i] = np.exp(1j * phase)
        return matrix
    
    @staticmethod
    def create_projection(indices: List[int]) -> np.ndarray:
        """
        Create projection operator onto subspace.
        
        P = Σᵢ |i⟩⟨i| for i in indices
        """
        matrix = np.zeros((256, 256), dtype=np.complex128)
        for i in indices:
            matrix[i, i] = 1.0
        return matrix
    
    @staticmethod
    def create_rotation(axis_indices: List[int], angle: float) -> np.ndarray:
        """
        Create rotation in subspace defined by axis_indices.
        
        Simplified 2D rotation in specified subspace.
        """
        matrix = np.eye(256, dtype=np.complex128)
        
        if len(axis_indices) >= 2:
            i, j = axis_indices[0], axis_indices[1]
            c, s = np.cos(angle), np.sin(angle)
            matrix[i, i] = c
            matrix[i, j] = -s
            matrix[j, i] = s
            matrix[j, j] = c
        
        return matrix
    
    @staticmethod
    def create_transition(from_idx: int, to_idx: int) -> np.ndarray:
        """
        Create transition operator |to⟩⟨from|.
        """
        matrix = np.zeros((256, 256), dtype=np.complex128)
        matrix[to_idx, from_idx] = 1.0
        return matrix
    
    @staticmethod
    def create_permutation(perm: Dict[int, int]) -> np.ndarray:
        """
        Create permutation operator from mapping.
        """
        matrix = np.zeros((256, 256), dtype=np.complex128)
        for from_idx, to_idx in perm.items():
            matrix[to_idx, from_idx] = 1.0
        # Fill diagonal for unmapped indices
        for i in range(256):
            if i not in perm:
                matrix[i, i] = 1.0
        return matrix
    
    @staticmethod
    def create_attractor(center: int, strength: float = 0.1) -> np.ndarray:
        """
        Create attractor operator that pulls states toward center.
        """
        matrix = np.eye(256, dtype=np.complex128) * (1 - strength)
        matrix[:, center] += strength
        # Normalize columns
        for j in range(256):
            col_sum = np.sum(np.abs(matrix[:, j]))
            if col_sum > 0:
                matrix[:, j] /= col_sum
        return matrix


# =============================================================================
# ORISHA FACTORY
# =============================================================================

class OrishaFactory:
    """
    Factory for creating Orisha operators with traditional attributes.
    """
    
    def __init__(self, hypercube: Q8Hypercube):
        self.q8 = hypercube
        self.gen = OrishaGenerator()
    
    def create_esu(self) -> Orisha:
        """
        Create Èṣù - the Messenger/Transition operator.
        
        Èṣù is the fundamental non-commutative generator.
        He opens and closes all paths.
        """
        # Èṣù as cyclic permutation (shift by 1)
        matrix = np.zeros((256, 256), dtype=np.complex128)
        for i in range(256):
            matrix[(i + 1) % 256, i] = 1.0
        
        return Orisha(
            orisha_type=OrishaType.ESU,
            tier=OrishaTier.PRIMORDIAL,
            name="Èṣù",
            matrix=matrix,
            domain="Crossroads, communication, chance",
            signature="Opens/closes paths; generates transitions",
            colors=["red", "black"],
            number=3,
            day="Monday",
            associated_odu=[0, 255]  # First and last
        )
    
    def create_obatala(self) -> Orisha:
        """
        Create Obàtálá - the Creation/Molding operator.
        
        Projects from potential to form.
        """
        # Obàtálá as projection onto even parity states
        even_indices = [o.index for o in self.q8.even_parity]
        matrix = self.gen.create_projection(even_indices)
        
        return Orisha(
            orisha_type=OrishaType.OBATALA,
            tier=OrishaTier.PRIMORDIAL,
            name="Obàtálá",
            matrix=matrix,
            domain="Creation, purity, clarity",
            signature="Projects potential into form; purifies",
            colors=["white"],
            number=8,
            day="Sunday",
            associated_odu=[255]  # Ogbè Meji (all light)
        )
    
    def create_orunmila(self) -> Orisha:
        """
        Create Ọrúnmìlà - the Witness/Knowledge operator.
        
        Observer who collapses superposition.
        """
        # Ọrúnmìlà as diagonal matrix (measurement basis)
        matrix = np.diag(np.arange(256, dtype=np.complex128) / 255)
        
        return Orisha(
            orisha_type=OrishaType.ORUNMILA,
            tier=OrishaTier.PRIMORDIAL,
            name="Ọrúnmìlà",
            matrix=matrix,
            domain="Wisdom, divination, destiny",
            signature="Witnesses all fates; collapses superposition",
            colors=["green", "yellow"],
            number=16,
            day="Every day",
            associated_odu=list(range(256))  # All Odù
        )
    
    def create_ogun(self) -> Orisha:
        """
        Create Ògún - the Cutting/Iron operator.
        
        Removes obstacles (|0⟩⟨1| type operation).
        """
        # Ògún flips bit 0 (cuts the lowest bit)
        matrix = self.gen.create_bit_flip(0)
        
        return Orisha(
            orisha_type=OrishaType.OGUN,
            tier=OrishaTier.DYNAMICAL,
            name="Ògún",
            matrix=matrix,
            domain="Iron, war, pathways",
            signature="Cuts obstacles; clears paths",
            colors=["green", "black"],
            number=7,
            day="Tuesday",
            associated_odu=[136]  # Ogunda Meji
        )
    
    def create_sango(self) -> Orisha:
        """
        Create Ṣàngó - the Thunder/Transformation operator.
        
        Applies high-voltage transformation.
        """
        # Ṣàngó as phase rotation
        matrix = self.gen.create_phase_shift(7, np.pi / 2)
        
        return Orisha(
            orisha_type=OrishaType.SANGO,
            tier=OrishaTier.DYNAMICAL,
            name="Ṣàngó",
            matrix=matrix,
            domain="Thunder, lightning, justice",
            signature="Transforms through intensity; judges",
            colors=["red", "white"],
            number=6,
            day="Wednesday (Ọjọ́ Ṣàngó)",
            associated_odu=[128]  # Associated with Ọ̀bàrà
        )
    
    def create_yemoja(self) -> Orisha:
        """
        Create Yemọja - the Ocean/Memory operator.
        
        Coherent channel that preserves information.
        """
        # Yemọja as smoothing/averaging operator
        matrix = np.eye(256, dtype=np.complex128) * 0.9
        # Add small mixing
        for i in range(256):
            for n in self.q8.vertices[i].neighbors()[:2]:
                matrix[i, n] = 0.05
        
        return Orisha(
            orisha_type=OrishaType.YEMOJA,
            tier=OrishaTier.DYNAMICAL,
            name="Yemọja",
            matrix=matrix,
            domain="Ocean, motherhood, fertility",
            signature="Nurtures; maintains coherence",
            colors=["blue", "white"],
            number=7,
            day="Saturday",
            associated_odu=[85]  # Associated with Ìrosùn
        )
    
    def create_osun(self) -> Orisha:
        """
        Create Ọ̀ṣun - the River/Attraction operator.
        
        Creates gravity wells in state space.
        """
        # Ọ̀ṣun as attractor toward harmony states
        center = 170  # Binary: 10101010 (alternating pattern)
        matrix = self.gen.create_attractor(center, 0.2)
        
        return Orisha(
            orisha_type=OrishaType.OSUN,
            tier=OrishaTier.DYNAMICAL,
            name="Ọ̀ṣun",
            matrix=matrix,
            domain="Rivers, love, fertility, gold",
            signature="Attracts; creates harmony",
            colors=["yellow", "gold"],
            number=5,
            day="Friday",
            associated_odu=[170]  # Ọ̀wọ́nrín pattern
        )
    
    def create_oya(self) -> Orisha:
        """
        Create Ọya - the Wind/Death-Rebirth operator.
        
        Transition operator for major state changes.
        """
        # Ọya as bit reversal (complete transformation)
        matrix = np.zeros((256, 256), dtype=np.complex128)
        for i in range(256):
            # Reverse bits
            reversed_i = int(bin(i)[2:].zfill(8)[::-1], 2)
            matrix[reversed_i, i] = 1.0
        
        return Orisha(
            orisha_type=OrishaType.OYA,
            tier=OrishaTier.DYNAMICAL,
            name="Ọya",
            matrix=matrix,
            domain="Wind, death, transformation",
            signature="Transforms completely; death and rebirth",
            colors=["burgundy", "purple"],
            number=9,
            day="Wednesday",
            associated_odu=[153]  # Odí Meji
        )
    
    def create_all(self) -> Dict[OrishaType, Orisha]:
        """Create all standard Orisha operators."""
        return {
            OrishaType.ESU: self.create_esu(),
            OrishaType.OBATALA: self.create_obatala(),
            OrishaType.ORUNMILA: self.create_orunmila(),
            OrishaType.OGUN: self.create_ogun(),
            OrishaType.SANGO: self.create_sango(),
            OrishaType.YEMOJA: self.create_yemoja(),
            OrishaType.OSUN: self.create_osun(),
            OrishaType.OYA: self.create_oya(),
        }


# =============================================================================
# ORISHA ALGEBRA
# =============================================================================

class OrishaAlgebra:
    """
    The complete Orisha operator algebra.
    
    Provides:
    - Operator composition
    - Commutation relations
    - Group structure analysis
    """
    
    def __init__(self, hypercube: Q8Hypercube):
        self.q8 = hypercube
        self.factory = OrishaFactory(hypercube)
        self.orisha = self.factory.create_all()
    
    def get_orisha(self, orisha_type: OrishaType) -> Orisha:
        """Get an Orisha by type."""
        return self.orisha[orisha_type]
    
    def compose(self, *orisha_types: OrishaType) -> np.ndarray:
        """
        Compose multiple Orisha operators (left to right).
        
        Result = O_n · O_{n-1} · ... · O_1
        """
        result = np.eye(256, dtype=np.complex128)
        for ot in orisha_types:
            result = self.orisha[ot].matrix @ result
        return result
    
    def commutation_table(self) -> Dict[Tuple[OrishaType, OrishaType], bool]:
        """
        Calculate commutation relations for all Orisha pairs.
        """
        table = {}
        types = list(self.orisha.keys())
        
        for i, t1 in enumerate(types):
            for t2 in types[i:]:
                commutes = self.orisha[t1].commutes_with(self.orisha[t2])
                table[(t1, t2)] = commutes
                table[(t2, t1)] = commutes
        
        return table
    
    def apply_sequence(self, state: np.ndarray, 
                       sequence: List[OrishaType]) -> np.ndarray:
        """Apply a sequence of Orisha operators to a state."""
        result = state.copy()
        for ot in sequence:
            result = self.orisha[ot].apply(result)
        return result
    
    def find_eigenstates(self, orisha_type: OrishaType) -> List[int]:
        """
        Find eigenstates (fixed points) of an Orisha.
        
        Returns indices where O|i⟩ = λ|i⟩ with |λ| = 1
        """
        o = self.orisha[orisha_type]
        eigenstates = []
        
        for i in range(256):
            basis = np.zeros(256)
            basis[i] = 1.0
            result = o.apply(basis)
            
            # Check if result is scalar multiple of basis
            if np.argmax(np.abs(result)) == i:
                if np.abs(result[i]) > 0.99:
                    eigenstates.append(i)
        
        return eigenstates
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get algebra statistics."""
        comm_table = self.commutation_table()
        commuting_pairs = sum(1 for v in comm_table.values() if v) // 2
        
        return {
            "orisha_count": len(self.orisha),
            "commuting_pairs": commuting_pairs,
            "non_commuting_pairs": len(self.orisha) * (len(self.orisha) - 1) // 2 - commuting_pairs,
            "tiers": {
                tier.value: sum(1 for o in self.orisha.values() if o.tier == tier)
                for tier in OrishaTier
            }
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_orisha() -> bool:
    """Validate orisha module."""
    
    q8 = Q8Hypercube()
    
    # Test generator
    gen = OrishaGenerator()
    
    identity = gen.create_identity()
    assert identity.shape == (256, 256)
    assert np.allclose(identity, np.eye(256))
    
    bit_flip = gen.create_bit_flip(0)
    assert bit_flip.shape == (256, 256)
    
    # Test factory
    factory = OrishaFactory(q8)
    
    esu = factory.create_esu()
    assert esu.orisha_type == OrishaType.ESU
    assert esu.tier == OrishaTier.PRIMORDIAL
    assert esu.matrix.shape == (256, 256)
    
    # Test Orisha operations
    state = np.zeros(256)
    state[0] = 1.0
    
    result = esu.apply(state)
    assert np.argmax(result) == 1  # Shifted by 1
    
    # Test algebra
    algebra = OrishaAlgebra(q8)
    
    ogun = algebra.get_orisha(OrishaType.OGUN)
    assert ogun.name == "Ògún"
    
    # Test composition
    composed = algebra.compose(OrishaType.ESU, OrishaType.OGUN)
    assert composed.shape == (256, 256)
    
    # Test commutation table
    comm_table = algebra.commutation_table()
    assert (OrishaType.ESU, OrishaType.ESU) in comm_table
    
    stats = algebra.get_statistics()
    assert stats["orisha_count"] == 8
    
    return True


if __name__ == "__main__":
    print("Validating Orisha Module...")
    assert validate_orisha()
    print("✓ Orisha Module validated")
    
    # Demo
    print("\n--- Orisha Algebra Demo ---")
    q8 = Q8Hypercube()
    algebra = OrishaAlgebra(q8)
    
    stats = algebra.get_statistics()
    print(f"\nAlgebra Statistics:")
    print(f"  Orisha count: {stats['orisha_count']}")
    print(f"  Commuting pairs: {stats['commuting_pairs']}")
    print(f"  Non-commuting pairs: {stats['non_commuting_pairs']}")
    
    print("\nOrisha Operators:")
    for ot, o in algebra.orisha.items():
        print(f"  {o.name} ({o.tier.value}): {o.domain[:40]}...")

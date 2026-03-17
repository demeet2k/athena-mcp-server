"""
ATHENA OS - SQUARING THE CIRCLE: SQUARE SYSTEM
===============================================
The Square System - Structural/Combinatorial Dimension

THE SQUARE'S HIERARCHY:
    Level 1: 4 Elements (Fire, Water, Air, Earth)
    Level 2: 16 Archetypes (4² = root-expression pairs)
    Level 3: 64 Permutations (4³ = root-expression-mode triples)

SQUARE PROPERTIES:
    - Simultaneous configuration
    - Structural hierarchy
    - Combinatorial complexity
    - Discrete states
    - Matrix organization

THE 16 ELEMENTAL ARCHETYPES:
    Each archetype is a Root-Expression pair:
    - Root: The underlying nature
    - Expression: How it manifests
    
    4 Pure (diagonal): F-F, W-W, A-A, E-E
    12 Mixed (off-diagonal): F-W, F-A, F-E, W-F, W-A, W-E, A-F, A-W, A-E, E-F, E-W, E-A

THE 64 PERMUTATIONS:
    Each permutation is a Root-Expression-Mode triple:
    - Root: Base element
    - Expression: Manifest element  
    - Mode: Cardinal/Fixed/Mutable
    
    4 × 4 × 4 = 64 total configurations

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapter 8
    - Hellenic elemental philosophy
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator
from enum import Enum, IntEnum
import numpy as np
from itertools import product


# =============================================================================
# ENUMS - SQUARE SYSTEM
# =============================================================================

class Element(IntEnum):
    """The four classical elements."""
    
    FIRE = 0    # Hot + Dry
    WATER = 1   # Cold + Wet
    AIR = 2     # Hot + Wet
    EARTH = 3   # Cold + Dry


class Quality(Enum):
    """The four qualities."""
    
    HOT = "hot"
    COLD = "cold"
    WET = "wet"
    DRY = "dry"


class ExpressionMode(IntEnum):
    """Mode of expression in the triple system."""
    
    CARDINAL = 0   # Initiating
    FIXED = 1      # Stabilizing
    MUTABLE = 2    # Adapting


# Element to qualities mapping
ELEMENT_QUALITIES: Dict[Element, Tuple[Quality, Quality]] = {
    Element.FIRE: (Quality.HOT, Quality.DRY),
    Element.WATER: (Quality.COLD, Quality.WET),
    Element.AIR: (Quality.HOT, Quality.WET),
    Element.EARTH: (Quality.COLD, Quality.DRY),
}

# Element symbols
ELEMENT_SYMBOLS: Dict[Element, str] = {
    Element.FIRE: "??",
    Element.WATER: "??",
    Element.AIR: "??",
    Element.EARTH: "??",
}


# =============================================================================
# ELEMENTAL ARCHETYPE (4×4 = 16)
# =============================================================================

@dataclass
class ElementalArchetype:
    """
    A Root-Expression elemental pair.
    
    16 total archetypes = 4 roots × 4 expressions
    4 pure (diagonal) + 12 mixed (off-diagonal)
    """
    
    root: Element
    expression: Element
    
    @property
    def index(self) -> int:
        """Get linear index (0-15)."""
        return self.root.value * 4 + self.expression.value
    
    @property
    def is_pure(self) -> bool:
        """Check if this is a pure archetype (diagonal)."""
        return self.root == self.expression
    
    @property
    def is_mixed(self) -> bool:
        """Check if this is a mixed archetype (off-diagonal)."""
        return self.root != self.expression
    
    @property
    def name(self) -> str:
        """Get archetype name."""
        return f"{self.root.name}-{self.expression.name}"
    
    @property
    def short_name(self) -> str:
        """Get short name (F-W, etc.)."""
        return f"{self.root.name[0]}-{self.expression.name[0]}"
    
    @property
    def symbol(self) -> str:
        """Get symbolic representation."""
        r = ELEMENT_SYMBOLS[self.root]
        e = ELEMENT_SYMBOLS[self.expression]
        return f"{r}→{e}"
    
    @property
    def root_qualities(self) -> Tuple[Quality, Quality]:
        """Get qualities of root element."""
        return ELEMENT_QUALITIES[self.root]
    
    @property
    def expression_qualities(self) -> Tuple[Quality, Quality]:
        """Get qualities of expression element."""
        return ELEMENT_QUALITIES[self.expression]
    
    @property
    def shared_quality(self) -> Optional[Quality]:
        """Get shared quality between root and expression (if any)."""
        r_quals = set(self.root_qualities)
        e_quals = set(self.expression_qualities)
        shared = r_quals & e_quals
        return list(shared)[0] if shared else None
    
    @property
    def tension_quality(self) -> Optional[Quality]:
        """Get the quality in tension (opposing)."""
        r_quals = set(self.root_qualities)
        e_quals = set(self.expression_qualities)
        
        # Find opposing pairs
        if Quality.HOT in r_quals and Quality.COLD in e_quals:
            return Quality.HOT
        if Quality.COLD in r_quals and Quality.HOT in e_quals:
            return Quality.COLD
        if Quality.WET in r_quals and Quality.DRY in e_quals:
            return Quality.WET
        if Quality.DRY in r_quals and Quality.WET in e_quals:
            return Quality.DRY
        
        return None
    
    @property
    def description(self) -> str:
        """Get interpretive description."""
        if self.is_pure:
            return f"Pure {self.root.name.lower()} - concentrated, intense"
        else:
            shared = self.shared_quality
            if shared:
                return f"{self.root.name} expressed through {self.expression.name} (shared: {shared.value})"
            else:
                return f"{self.root.name} in tension with {self.expression.name}"
    
    def matrix_position(self) -> Tuple[int, int]:
        """Get (row, col) position in 4×4 matrix."""
        return (self.root.value, self.expression.value)
    
    def __hash__(self) -> int:
        return hash((self.root, self.expression))
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ElementalArchetype):
            return self.root == other.root and self.expression == other.expression
        return False
    
    def __repr__(self) -> str:
        return f"Archetype({self.name})"


def generate_archetypes() -> List[ElementalArchetype]:
    """Generate all 16 elemental archetypes."""
    archetypes = []
    for root in Element:
        for expr in Element:
            archetypes.append(ElementalArchetype(root, expr))
    return archetypes


ARCHETYPES_16 = generate_archetypes()


# =============================================================================
# ELEMENTAL PERMUTATION (4×4×4 = 64)
# =============================================================================

@dataclass
class ElementalPermutation:
    """
    A Root-Expression-Mode triple.
    
    64 total permutations = 4 roots × 4 expressions × 4 modes
    (Using 4 modes: Cardinal, Fixed, Mutable, + Void/Neutral)
    
    Alternative: 4³ with 3 modes = 48, but manuscript uses 64.
    Here we use 4 "expression modes" to achieve 64.
    """
    
    root: Element
    expression: Element
    modifier: Element  # Third element as modifier
    
    @property
    def index(self) -> int:
        """Get linear index (0-63)."""
        return (self.root.value * 16 + 
                self.expression.value * 4 + 
                self.modifier.value)
    
    @property
    def archetype(self) -> ElementalArchetype:
        """Get the base archetype (root-expression)."""
        return ElementalArchetype(self.root, self.expression)
    
    @property
    def is_pure(self) -> bool:
        """All three elements the same."""
        return self.root == self.expression == self.modifier
    
    @property
    def name(self) -> str:
        """Get permutation name."""
        return f"{self.root.name[0]}-{self.expression.name[0]}-{self.modifier.name[0]}"
    
    @property
    def full_name(self) -> str:
        return f"{self.root.name}-{self.expression.name}-{self.modifier.name}"
    
    def element_counts(self) -> Dict[Element, int]:
        """Count occurrences of each element."""
        counts = {e: 0 for e in Element}
        counts[self.root] += 1
        counts[self.expression] += 1
        counts[self.modifier] += 1
        return counts
    
    @property
    def dominant_element(self) -> Optional[Element]:
        """Get element appearing most (if any)."""
        counts = self.element_counts()
        max_count = max(counts.values())
        if max_count >= 2:
            for e, c in counts.items():
                if c == max_count:
                    return e
        return None
    
    @property
    def entropy(self) -> float:
        """Measure of elemental diversity (0 = pure, 1 = max mixed)."""
        counts = self.element_counts()
        total = 3
        probs = [c / total for c in counts.values() if c > 0]
        if len(probs) <= 1:
            return 0.0
        return -sum(p * np.log2(p) for p in probs) / np.log2(4)
    
    def tensor_indices(self) -> Tuple[int, int, int]:
        """Get (i, j, k) position in 4×4×4 tensor."""
        return (self.root.value, self.expression.value, self.modifier.value)
    
    def __hash__(self) -> int:
        return hash((self.root, self.expression, self.modifier))
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ElementalPermutation):
            return (self.root == other.root and 
                    self.expression == other.expression and
                    self.modifier == other.modifier)
        return False
    
    def __repr__(self) -> str:
        return f"Permutation({self.name})"


def generate_permutations() -> List[ElementalPermutation]:
    """Generate all 64 elemental permutations."""
    perms = []
    for root in Element:
        for expr in Element:
            for mod in Element:
                perms.append(ElementalPermutation(root, expr, mod))
    return perms


PERMUTATIONS_64 = generate_permutations()


# =============================================================================
# ELEMENTAL MATRIX (4×4)
# =============================================================================

class ElementalMatrix:
    """
    The 4×4 elemental matrix.
    
    Rows: Root elements
    Columns: Expression elements
    Cells: Archetypes
    
    Diagonal: Pure archetypes (F-F, W-W, A-A, E-E)
    Off-diagonal: Mixed archetypes (12 total)
    """
    
    def __init__(self):
        self.matrix = np.zeros((4, 4), dtype=object)
        
        for arch in ARCHETYPES_16:
            row, col = arch.matrix_position()
            self.matrix[row, col] = arch
    
    def get(self, root: Element, expression: Element) -> ElementalArchetype:
        """Get archetype at position."""
        return self.matrix[root.value, expression.value]
    
    def get_row(self, root: Element) -> List[ElementalArchetype]:
        """Get all archetypes with given root."""
        return [self.matrix[root.value, i] for i in range(4)]
    
    def get_column(self, expression: Element) -> List[ElementalArchetype]:
        """Get all archetypes with given expression."""
        return [self.matrix[i, expression.value] for i in range(4)]
    
    def get_diagonal(self) -> List[ElementalArchetype]:
        """Get pure archetypes (diagonal)."""
        return [self.matrix[i, i] for i in range(4)]
    
    def get_off_diagonal(self) -> List[ElementalArchetype]:
        """Get mixed archetypes (off-diagonal)."""
        return [self.matrix[i, j] for i in range(4) for j in range(4) if i != j]
    
    def transpose(self) -> ElementalArchetype:
        """Get transpose (swap root/expression)."""
        transposed = ElementalMatrix()
        for i in range(4):
            for j in range(4):
                transposed.matrix[i, j] = self.matrix[j, i]
        return transposed
    
    def __repr__(self) -> str:
        lines = ["ElementalMatrix (4×4):"]
        header = "     " + " ".join(f"{e.name[:3]:>5}" for e in Element)
        lines.append(header)
        
        for root in Element:
            row = [self.get(root, expr).short_name for expr in Element]
            lines.append(f"{root.name[:3]:>3}: " + " ".join(f"{r:>5}" for r in row))
        
        return "\n".join(lines)


# =============================================================================
# ELEMENTAL TENSOR (4×4×4)
# =============================================================================

class ElementalTensor:
    """
    The 4×4×4 elemental tensor.
    
    Dimensions: Root × Expression × Modifier
    64 total cells (permutations)
    """
    
    def __init__(self):
        self.tensor = np.zeros((4, 4, 4), dtype=object)
        
        for perm in PERMUTATIONS_64:
            i, j, k = perm.tensor_indices()
            self.tensor[i, j, k] = perm
    
    def get(self, root: Element, expression: Element, 
            modifier: Element) -> ElementalPermutation:
        """Get permutation at position."""
        return self.tensor[root.value, expression.value, modifier.value]
    
    def slice_root(self, root: Element) -> np.ndarray:
        """Get 4×4 slice for a fixed root."""
        return self.tensor[root.value, :, :]
    
    def slice_expression(self, expression: Element) -> np.ndarray:
        """Get 4×4 slice for a fixed expression."""
        return self.tensor[:, expression.value, :]
    
    def slice_modifier(self, modifier: Element) -> np.ndarray:
        """Get 4×4 slice for a fixed modifier."""
        return self.tensor[:, :, modifier.value]
    
    def get_pure(self) -> List[ElementalPermutation]:
        """Get all pure permutations (same element 3x)."""
        return [self.tensor[i, i, i] for i in range(4)]
    
    def get_by_dominant(self, element: Element) -> List[ElementalPermutation]:
        """Get all permutations where element appears 2+ times."""
        return [p for p in PERMUTATIONS_64 
                if p.dominant_element == element]
    
    def entropy_distribution(self) -> Dict[float, int]:
        """Get distribution of entropy values."""
        dist = {}
        for perm in PERMUTATIONS_64:
            e = round(perm.entropy, 2)
            dist[e] = dist.get(e, 0) + 1
        return dict(sorted(dist.items()))


# =============================================================================
# SQUARE SYSTEM
# =============================================================================

class SquareSystem:
    """
    The complete square system.
    
    Hierarchy:
        4 Elements → 16 Archetypes → 64 Permutations
    """
    
    # Constants
    N_ELEMENTS = 4
    N_ARCHETYPES = 16
    N_PERMUTATIONS = 64
    
    # Structural counts
    N_PURE_ARCHETYPES = 4     # Diagonal
    N_MIXED_ARCHETYPES = 12   # Off-diagonal
    
    def __init__(self):
        self.matrix = ElementalMatrix()
        self.tensor = ElementalTensor()
        self.archetypes = ARCHETYPES_16
        self.permutations = PERMUTATIONS_64
    
    def get_archetype(self, root: Element, 
                      expression: Element) -> ElementalArchetype:
        """Get archetype by root and expression."""
        return self.matrix.get(root, expression)
    
    def get_archetype_by_index(self, index: int) -> ElementalArchetype:
        """Get archetype by linear index (0-15)."""
        return self.archetypes[index % 16]
    
    def get_permutation(self, root: Element, expression: Element,
                       modifier: Element) -> ElementalPermutation:
        """Get permutation by elements."""
        return self.tensor.get(root, expression, modifier)
    
    def get_permutation_by_index(self, index: int) -> ElementalPermutation:
        """Get permutation by linear index (0-63)."""
        return self.permutations[index % 64]
    
    def archetypes_by_root(self, root: Element) -> List[ElementalArchetype]:
        """Get all archetypes with given root."""
        return self.matrix.get_row(root)
    
    def archetypes_by_expression(self, 
                                 expression: Element) -> List[ElementalArchetype]:
        """Get all archetypes with given expression."""
        return self.matrix.get_column(expression)
    
    def pure_archetypes(self) -> List[ElementalArchetype]:
        """Get the 4 pure archetypes."""
        return self.matrix.get_diagonal()
    
    def mixed_archetypes(self) -> List[ElementalArchetype]:
        """Get the 12 mixed archetypes."""
        return self.matrix.get_off_diagonal()
    
    def iterate_archetypes(self) -> Iterator[ElementalArchetype]:
        """Iterate through all 16 archetypes."""
        return iter(self.archetypes)
    
    def iterate_permutations(self) -> Iterator[ElementalPermutation]:
        """Iterate through all 64 permutations."""
        return iter(self.permutations)
    
    def get_level_count(self, level: int) -> int:
        """Get count at each level."""
        counts = {
            1: self.N_ELEMENTS,     # 4
            2: self.N_ARCHETYPES,   # 16 = 4²
            3: self.N_PERMUTATIONS  # 64 = 4³
        }
        return counts.get(level, 0)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of square system."""
        return {
            "levels": 3,
            "elements": self.N_ELEMENTS,
            "archetypes": self.N_ARCHETYPES,
            "permutations": self.N_PERMUTATIONS,
            "pure_archetypes": self.N_PURE_ARCHETYPES,
            "mixed_archetypes": self.N_MIXED_ARCHETYPES,
            "power_check": f"4¹ = {4**1}, 4² = {4**2}, 4³ = {4**3}"
        }


# =============================================================================
# CONSTITUTIONAL TYPES (HUMORAL 16)
# =============================================================================

class Humor(IntEnum):
    """The four humors (mapped to elements)."""
    
    YELLOW_BILE = 0  # Fire - Choleric
    PHLEGM = 1       # Water - Phlegmatic
    BLOOD = 2        # Air - Sanguine
    BLACK_BILE = 3   # Earth - Melancholic


ELEMENT_TO_HUMOR = {
    Element.FIRE: Humor.YELLOW_BILE,
    Element.WATER: Humor.PHLEGM,
    Element.AIR: Humor.BLOOD,
    Element.EARTH: Humor.BLACK_BILE,
}

HUMOR_NAMES = {
    Humor.YELLOW_BILE: "Choleric",
    Humor.PHLEGM: "Phlegmatic",
    Humor.BLOOD: "Sanguine",
    Humor.BLACK_BILE: "Melancholic",
}


@dataclass
class ConstitutionalType:
    """
    One of 16 constitutional types.
    
    Constitutional (root): Baseline temperament
    Symptomatic (expression): Current state
    """
    
    constitutional: Humor  # Root
    symptomatic: Humor     # Expression
    
    @property
    def is_congruent(self) -> bool:
        """Same constitutional and symptomatic (diagonal)."""
        return self.constitutional == self.symptomatic
    
    @property
    def is_incongruent(self) -> bool:
        """Different constitutional and symptomatic."""
        return not self.is_congruent
    
    @property
    def name(self) -> str:
        c_name = HUMOR_NAMES[self.constitutional]
        s_name = HUMOR_NAMES[self.symptomatic].lower()
        return f"{c_name}-{s_name}"
    
    @property
    def short_name(self) -> str:
        return f"{self.constitutional.name[0]}-{self.symptomatic.name[0]}"
    
    @property
    def clinical_notes(self) -> str:
        if self.is_congruent:
            return "Express nature purely. Moderate dominant humor."
        else:
            return "Acting against nature. Address both constitution and current condition."
    
    def to_archetype(self) -> ElementalArchetype:
        """Convert to elemental archetype."""
        root_elem = [e for e, h in ELEMENT_TO_HUMOR.items() 
                    if h == self.constitutional][0]
        expr_elem = [e for e, h in ELEMENT_TO_HUMOR.items() 
                    if h == self.symptomatic][0]
        return ElementalArchetype(root_elem, expr_elem)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_square_system() -> bool:
    """Validate square system module."""
    
    # Test constants
    assert len(Element) == 4
    assert len(ARCHETYPES_16) == 16
    assert len(PERMUTATIONS_64) == 64
    
    # Test archetype properties
    pure_count = sum(1 for a in ARCHETYPES_16 if a.is_pure)
    mixed_count = sum(1 for a in ARCHETYPES_16 if a.is_mixed)
    assert pure_count == 4
    assert mixed_count == 12
    
    # Test archetype indexing
    for i, arch in enumerate(ARCHETYPES_16):
        assert arch.index == i
    
    # Test permutation properties
    pure_perm_count = sum(1 for p in PERMUTATIONS_64 if p.is_pure)
    assert pure_perm_count == 4
    
    # Test matrix
    matrix = ElementalMatrix()
    for root in Element:
        for expr in Element:
            arch = matrix.get(root, expr)
            assert arch.root == root
            assert arch.expression == expr
    
    # Test tensor
    tensor = ElementalTensor()
    for root in Element:
        for expr in Element:
            for mod in Element:
                perm = tensor.get(root, expr, mod)
                assert perm.root == root
                assert perm.expression == expr
                assert perm.modifier == mod
    
    # Test square system
    square = SquareSystem()
    assert square.N_ARCHETYPES == 16
    assert square.N_PERMUTATIONS == 64
    
    # Test constitutional types
    ct = ConstitutionalType(Humor.BLOOD, Humor.BLOOD)
    assert ct.is_congruent
    
    ct2 = ConstitutionalType(Humor.BLOOD, Humor.PHLEGM)
    assert ct2.is_incongruent
    
    return True


if __name__ == "__main__":
    print("Validating Square System...")
    assert validate_square_system()
    print("✓ Square System validated")
    
    # Demo
    print("\n--- Square System Demo ---")
    
    square = SquareSystem()
    print(f"\nHierarchy:")
    for level in range(1, 4):
        print(f"  Level {level}: {square.get_level_count(level)}")
    
    print("\n4×4 Elemental Matrix:")
    print(square.matrix)
    
    print("\nPure Archetypes (diagonal):")
    for arch in square.pure_archetypes():
        print(f"  {arch.symbol} {arch.name}")
    
    print("\nSample Mixed Archetype (Fire-Water):")
    arch = square.get_archetype(Element.FIRE, Element.WATER)
    print(f"  {arch}")
    print(f"  Shared quality: {arch.shared_quality}")
    print(f"  Tension quality: {arch.tension_quality}")
    print(f"  Description: {arch.description}")
    
    print("\nEntropy distribution (64 permutations):")
    dist = square.tensor.entropy_distribution()
    for entropy, count in dist.items():
        print(f"  Entropy {entropy:.2f}: {count} permutations")

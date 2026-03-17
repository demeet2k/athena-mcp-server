"""
ATHENA OS - SYLLOGISTIC PROCESSOR MODULE
========================================
Classical Syllogistic Logic and Inference

From ATHENA_OPERATING_SYSTEM_.docx Chapter 6:

PROPOSITION TYPES (AEIO):
    A - Universal Affirmative: All S are P
    E - Universal Negative: No S are P
    I - Particular Affirmative: Some S are P
    O - Particular Negative: Some S are not P

DISTRIBUTION:
    Subject distributed in universal propositions (A, E)
    Predicate distributed in negative propositions (E, O)

SYLLOGISTIC FIGURES:
    Figure 1: M-P, S-M ∴ S-P (Barbara, Celarent, Darii, Ferio)
    Figure 2: P-M, S-M ∴ S-P (Cesare, Camestres, Festino, Baroco)
    Figure 3: M-P, M-S ∴ S-P (Darapti, Disamis, Datisi, Felapton, Bocardo, Ferison)
    Figure 4: P-M, M-S ∴ S-P (Bramantip, Camenes, Dimaris, Fesapo, Fresison)

VALIDITY RULES:
    R1: Middle term must be distributed at least once
    R2: No term distributed in conclusion unless distributed in premise
    R3: At least one premise must be affirmative
    R4: Negative conclusion requires exactly one negative premise
    R5: Two affirmative premises yield affirmative conclusion
    R6: Particular conclusion requires at least one particular premise

VALID MOODS (19 total):
    Figure 1: AAA, EAE, AII, EIO
    Figure 2: EAE, AEE, EIO, AOO
    Figure 3: AAI, IAI, AII, EAO, OAO, EIO
    Figure 4: AAI, AEE, IAI, EAO, EIO
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum, auto


# =============================================================================
# PROPOSITION TYPES
# =============================================================================

class PropositionType(Enum):
    """The four categorical proposition types."""
    A = auto()  # Universal Affirmative: All S are P
    E = auto()  # Universal Negative: No S are P
    I = auto()  # Particular Affirmative: Some S are P
    O = auto()  # Particular Negative: Some S are not P


@dataclass(frozen=True)
class PropositionSpec:
    """Specification of a proposition type."""
    
    prop_type: PropositionType
    name: str
    form: str
    is_universal: bool
    is_affirmative: bool
    subject_distributed: bool
    predicate_distributed: bool


PROP_A = PropositionSpec(
    PropositionType.A, "Universal Affirmative",
    "All S are P", True, True, True, False
)

PROP_E = PropositionSpec(
    PropositionType.E, "Universal Negative",
    "No S are P", True, False, True, True
)

PROP_I = PropositionSpec(
    PropositionType.I, "Particular Affirmative",
    "Some S are P", False, True, False, False
)

PROP_O = PropositionSpec(
    PropositionType.O, "Particular Negative",
    "Some S are not P", False, False, False, True
)

PROPOSITION_SPECS: Dict[PropositionType, PropositionSpec] = {
    PropositionType.A: PROP_A,
    PropositionType.E: PROP_E,
    PropositionType.I: PROP_I,
    PropositionType.O: PROP_O,
}


# =============================================================================
# TERMS AND PROPOSITIONS
# =============================================================================

@dataclass(frozen=True)
class Term:
    """A term in a syllogism."""
    name: str
    
    def __repr__(self) -> str:
        return self.name


@dataclass
class Proposition:
    """A categorical proposition."""
    
    subject: Term
    predicate: Term
    prop_type: PropositionType
    
    @property
    def spec(self) -> PropositionSpec:
        return PROPOSITION_SPECS[self.prop_type]
    
    @property
    def is_universal(self) -> bool:
        return self.spec.is_universal
    
    @property
    def is_particular(self) -> bool:
        return not self.is_universal
    
    @property
    def is_affirmative(self) -> bool:
        return self.spec.is_affirmative
    
    @property
    def is_negative(self) -> bool:
        return not self.is_affirmative
    
    def is_distributed(self, term: Term) -> bool:
        """Check if a term is distributed in this proposition."""
        if term == self.subject:
            return self.spec.subject_distributed
        elif term == self.predicate:
            return self.spec.predicate_distributed
        return False
    
    @property
    def statement(self) -> str:
        """Generate natural language statement."""
        forms = {
            PropositionType.A: f"All {self.subject} are {self.predicate}",
            PropositionType.E: f"No {self.subject} are {self.predicate}",
            PropositionType.I: f"Some {self.subject} are {self.predicate}",
            PropositionType.O: f"Some {self.subject} are not {self.predicate}",
        }
        return forms[self.prop_type]
    
    def __repr__(self) -> str:
        return f"{self.prop_type.name}({self.subject}, {self.predicate})"


# =============================================================================
# SYLLOGISTIC FIGURES
# =============================================================================

class Figure(Enum):
    """The four syllogistic figures."""
    FIGURE_1 = 1  # M-P, S-M ∴ S-P
    FIGURE_2 = 2  # P-M, S-M ∴ S-P
    FIGURE_3 = 3  # M-P, M-S ∴ S-P
    FIGURE_4 = 4  # P-M, M-S ∴ S-P


@dataclass(frozen=True)
class FigureSpec:
    """Specification of a syllogistic figure."""
    
    figure: Figure
    major_pattern: str  # Position of middle term in major premise
    minor_pattern: str  # Position of middle term in minor premise
    conclusion_pattern: str
    description: str


FIGURE_SPECS: Dict[Figure, FigureSpec] = {
    Figure.FIGURE_1: FigureSpec(
        Figure.FIGURE_1, "M-P", "S-M", "S-P",
        "Middle is subject of major, predicate of minor"
    ),
    Figure.FIGURE_2: FigureSpec(
        Figure.FIGURE_2, "P-M", "S-M", "S-P",
        "Middle is predicate of both premises"
    ),
    Figure.FIGURE_3: FigureSpec(
        Figure.FIGURE_3, "M-P", "M-S", "S-P",
        "Middle is subject of both premises"
    ),
    Figure.FIGURE_4: FigureSpec(
        Figure.FIGURE_4, "P-M", "M-S", "S-P",
        "Middle is predicate of major, subject of minor"
    ),
}


# =============================================================================
# SYLLOGISM
# =============================================================================

@dataclass
class Syllogism:
    """A categorical syllogism."""
    
    major_premise: Proposition
    minor_premise: Proposition
    conclusion: Proposition
    
    @property
    def major_term(self) -> Term:
        """P - predicate of conclusion."""
        return self.conclusion.predicate
    
    @property
    def minor_term(self) -> Term:
        """S - subject of conclusion."""
        return self.conclusion.subject
    
    @property
    def middle_term(self) -> Optional[Term]:
        """M - appears in both premises but not conclusion."""
        major_terms = {self.major_premise.subject, self.major_premise.predicate}
        minor_terms = {self.minor_premise.subject, self.minor_premise.predicate}
        conclusion_terms = {self.conclusion.subject, self.conclusion.predicate}
        
        middle_candidates = (major_terms & minor_terms) - conclusion_terms
        return middle_candidates.pop() if middle_candidates else None
    
    @property
    def mood(self) -> str:
        """Get mood as three-letter code (e.g., AAA, EIO)."""
        return (self.major_premise.prop_type.name +
                self.minor_premise.prop_type.name +
                self.conclusion.prop_type.name)
    
    @property
    def figure(self) -> Optional[Figure]:
        """Determine the figure from term positions."""
        M = self.middle_term
        P = self.major_term
        S = self.minor_term
        
        if M is None:
            return None
        
        major_subj = self.major_premise.subject
        major_pred = self.major_premise.predicate
        minor_subj = self.minor_premise.subject
        minor_pred = self.minor_premise.predicate
        
        # Figure 1: M-P, S-M
        if major_subj == M and major_pred == P and minor_subj == S and minor_pred == M:
            return Figure.FIGURE_1
        # Figure 2: P-M, S-M
        if major_subj == P and major_pred == M and minor_subj == S and minor_pred == M:
            return Figure.FIGURE_2
        # Figure 3: M-P, M-S
        if major_subj == M and major_pred == P and minor_subj == M and minor_pred == S:
            return Figure.FIGURE_3
        # Figure 4: P-M, M-S
        if major_subj == P and major_pred == M and minor_subj == M and minor_pred == S:
            return Figure.FIGURE_4
        
        return None
    
    def __repr__(self) -> str:
        return (f"Syllogism({self.mood}, Figure {self.figure.value if self.figure else '?'})\n"
                f"  Major: {self.major_premise.statement}\n"
                f"  Minor: {self.minor_premise.statement}\n"
                f"  ∴ {self.conclusion.statement}")


# =============================================================================
# VALIDITY CHECKING
# =============================================================================

class ValidityError(Enum):
    """Types of validity errors."""
    UNDISTRIBUTED_MIDDLE = auto()
    ILLICIT_MAJOR = auto()
    ILLICIT_MINOR = auto()
    TWO_NEGATIVE_PREMISES = auto()
    NEGATIVE_CONCLUSION_ERROR = auto()
    AFFIRMATIVE_CONCLUSION_ERROR = auto()
    EXISTENTIAL_FALLACY = auto()


@dataclass
class ValidityResult:
    """Result of validity check."""
    
    is_valid: bool
    errors: List[ValidityError] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)


def check_validity(syllogism: Syllogism) -> ValidityResult:
    """
    Check validity of a syllogism using classical rules.
    
    Rules:
    R1: Middle term must be distributed at least once
    R2: No term distributed in conclusion unless distributed in premise
    R3: At least one premise must be affirmative
    R4: Negative conclusion requires exactly one negative premise
    R5: Two affirmative premises yield affirmative conclusion
    R6: Particular conclusion requires at least one particular premise
    """
    errors = []
    messages = []
    
    M = syllogism.middle_term
    S = syllogism.minor_term
    P = syllogism.major_term
    
    major = syllogism.major_premise
    minor = syllogism.minor_premise
    conclusion = syllogism.conclusion
    
    # R1: Middle term must be distributed at least once
    if M:
        m_distributed_major = major.is_distributed(M)
        m_distributed_minor = minor.is_distributed(M)
        if not (m_distributed_major or m_distributed_minor):
            errors.append(ValidityError.UNDISTRIBUTED_MIDDLE)
            messages.append("Middle term is not distributed in either premise")
    
    # R2: No term distributed in conclusion unless distributed in premise
    if conclusion.is_distributed(P):
        if not major.is_distributed(P):
            errors.append(ValidityError.ILLICIT_MAJOR)
            messages.append("Major term distributed in conclusion but not in major premise")
    
    if conclusion.is_distributed(S):
        if not minor.is_distributed(S):
            errors.append(ValidityError.ILLICIT_MINOR)
            messages.append("Minor term distributed in conclusion but not in minor premise")
    
    # R3: At least one premise must be affirmative
    if major.is_negative and minor.is_negative:
        errors.append(ValidityError.TWO_NEGATIVE_PREMISES)
        messages.append("Both premises are negative")
    
    # R4: Negative conclusion requires exactly one negative premise
    neg_premises = int(major.is_negative) + int(minor.is_negative)
    if conclusion.is_negative and neg_premises != 1:
        errors.append(ValidityError.NEGATIVE_CONCLUSION_ERROR)
        messages.append("Negative conclusion without exactly one negative premise")
    
    # R5: Two affirmative premises yield affirmative conclusion
    if major.is_affirmative and minor.is_affirmative and conclusion.is_negative:
        errors.append(ValidityError.AFFIRMATIVE_CONCLUSION_ERROR)
        messages.append("Negative conclusion from two affirmative premises")
    
    return ValidityResult(
        is_valid=len(errors) == 0,
        errors=errors,
        messages=messages
    )


# =============================================================================
# VALID MOODS
# =============================================================================

# Valid moods for each figure (traditional 19 valid moods)
VALID_MOODS: Dict[Figure, List[str]] = {
    Figure.FIGURE_1: ["AAA", "EAE", "AII", "EIO"],
    Figure.FIGURE_2: ["EAE", "AEE", "EIO", "AOO"],
    Figure.FIGURE_3: ["AAI", "IAI", "AII", "EAO", "OAO", "EIO"],
    Figure.FIGURE_4: ["AAI", "AEE", "IAI", "EAO", "EIO"],
}

# Traditional names for valid moods
MOOD_NAMES: Dict[Tuple[Figure, str], str] = {
    # Figure 1
    (Figure.FIGURE_1, "AAA"): "Barbara",
    (Figure.FIGURE_1, "EAE"): "Celarent",
    (Figure.FIGURE_1, "AII"): "Darii",
    (Figure.FIGURE_1, "EIO"): "Ferio",
    # Figure 2
    (Figure.FIGURE_2, "EAE"): "Cesare",
    (Figure.FIGURE_2, "AEE"): "Camestres",
    (Figure.FIGURE_2, "EIO"): "Festino",
    (Figure.FIGURE_2, "AOO"): "Baroco",
    # Figure 3
    (Figure.FIGURE_3, "AAI"): "Darapti",
    (Figure.FIGURE_3, "IAI"): "Disamis",
    (Figure.FIGURE_3, "AII"): "Datisi",
    (Figure.FIGURE_3, "EAO"): "Felapton",
    (Figure.FIGURE_3, "OAO"): "Bocardo",
    (Figure.FIGURE_3, "EIO"): "Ferison",
    # Figure 4
    (Figure.FIGURE_4, "AAI"): "Bramantip",
    (Figure.FIGURE_4, "AEE"): "Camenes",
    (Figure.FIGURE_4, "IAI"): "Dimaris",
    (Figure.FIGURE_4, "EAO"): "Fesapo",
    (Figure.FIGURE_4, "EIO"): "Fresison",
}


def get_mood_name(figure: Figure, mood: str) -> Optional[str]:
    """Get traditional name for a mood."""
    return MOOD_NAMES.get((figure, mood))


def is_valid_mood(figure: Figure, mood: str) -> bool:
    """Check if mood is valid for figure."""
    return mood in VALID_MOODS.get(figure, [])


# =============================================================================
# SYLLOGISM CONSTRUCTION
# =============================================================================

def construct_syllogism(
    major_term: str,
    minor_term: str,
    middle_term: str,
    mood: str,
    figure: Figure
) -> Syllogism:
    """
    Construct a syllogism from terms, mood, and figure.
    
    Args:
        major_term: P - predicate of conclusion
        minor_term: S - subject of conclusion
        middle_term: M - appears in premises only
        mood: Three-letter mood code (e.g., "AAA")
        figure: Syllogistic figure (1-4)
    """
    P = Term(major_term)
    S = Term(minor_term)
    M = Term(middle_term)
    
    # Parse mood
    major_type = PropositionType[mood[0]]
    minor_type = PropositionType[mood[1]]
    conclusion_type = PropositionType[mood[2]]
    
    # Construct premises based on figure
    if figure == Figure.FIGURE_1:  # M-P, S-M
        major = Proposition(M, P, major_type)
        minor = Proposition(S, M, minor_type)
    elif figure == Figure.FIGURE_2:  # P-M, S-M
        major = Proposition(P, M, major_type)
        minor = Proposition(S, M, minor_type)
    elif figure == Figure.FIGURE_3:  # M-P, M-S
        major = Proposition(M, P, major_type)
        minor = Proposition(M, S, minor_type)
    elif figure == Figure.FIGURE_4:  # P-M, M-S
        major = Proposition(P, M, major_type)
        minor = Proposition(M, S, minor_type)
    else:
        raise ValueError(f"Invalid figure: {figure}")
    
    conclusion = Proposition(S, P, conclusion_type)
    
    return Syllogism(major, minor, conclusion)


# =============================================================================
# CONCLUSION GENERATOR
# =============================================================================

def generate_conclusion(
    major: Proposition,
    minor: Proposition
) -> Optional[Proposition]:
    """
    Generate valid conclusion from two premises if possible.
    
    Returns None if no valid conclusion exists.
    """
    # R3: Check for two negatives
    if major.is_negative and minor.is_negative:
        return None
    
    # Find terms
    major_terms = {major.subject, major.predicate}
    minor_terms = {minor.subject, minor.predicate}
    
    # Middle term
    middle_candidates = major_terms & minor_terms
    if not middle_candidates:
        return None
    M = middle_candidates.pop()
    
    # Major term (from major premise, not middle)
    P = (major_terms - {M}).pop()
    # Minor term (from minor premise, not middle)
    S = (minor_terms - {M}).pop()
    
    # Determine quality (affirmative/negative)
    if major.is_negative or minor.is_negative:
        is_negative = True
    else:
        is_negative = False
    
    # Determine quantity (universal/particular)
    # Start with most general, reduce as needed
    if major.is_particular or minor.is_particular:
        is_particular = True
    elif not major.is_distributed(S) and not minor.is_distributed(S):
        is_particular = True
    else:
        is_particular = False
    
    # Determine proposition type
    if is_particular:
        if is_negative:
            prop_type = PropositionType.O
        else:
            prop_type = PropositionType.I
    else:
        if is_negative:
            prop_type = PropositionType.E
        else:
            prop_type = PropositionType.A
    
    conclusion = Proposition(S, P, prop_type)
    
    # Verify the resulting syllogism would be valid
    test_syllogism = Syllogism(major, minor, conclusion)
    result = check_validity(test_syllogism)
    
    if result.is_valid:
        return conclusion
    return None


# =============================================================================
# SYLLOGISTIC PROCESSOR
# =============================================================================

class SyllogisticProcessor:
    """Complete syllogistic reasoning processor."""
    
    def __init__(self):
        self.valid_moods = VALID_MOODS
        self.mood_names = MOOD_NAMES
    
    def construct(self, major: str, minor: str, middle: str,
                 mood: str, figure: int) -> Syllogism:
        """Construct a syllogism."""
        return construct_syllogism(major, minor, middle, mood, Figure(figure))
    
    def check(self, syllogism: Syllogism) -> ValidityResult:
        """Check validity of a syllogism."""
        return check_validity(syllogism)
    
    def generate(self, major: Proposition, minor: Proposition) -> Optional[Proposition]:
        """Generate conclusion from premises."""
        return generate_conclusion(major, minor)
    
    def all_valid_moods(self) -> List[Tuple[Figure, str, str]]:
        """Get all valid moods with names."""
        result = []
        for figure, moods in self.valid_moods.items():
            for mood in moods:
                name = self.mood_names.get((figure, mood), "")
                result.append((figure, mood, name))
        return result


# =============================================================================
# VALIDATION
# =============================================================================

def validate_syllogistic() -> bool:
    """Validate the syllogistic processor module."""
    
    # Test propositions
    men = Term("men")
    mortal = Term("mortal")
    greeks = Term("greeks")
    
    prop_a = Proposition(men, mortal, PropositionType.A)
    assert prop_a.is_universal
    assert prop_a.is_affirmative
    assert prop_a.is_distributed(men)
    assert not prop_a.is_distributed(mortal)
    
    # Test Barbara (AAA-1)
    # All M are P
    # All S are M
    # ∴ All S are P
    syllogism = construct_syllogism(
        "mortal", "Socrates", "men",
        "AAA", Figure.FIGURE_1
    )
    assert syllogism.mood == "AAA"
    assert syllogism.figure == Figure.FIGURE_1
    
    result = check_validity(syllogism)
    assert result.is_valid, f"Barbara should be valid: {result.messages}"
    
    # Test invalid syllogism (undistributed middle)
    # All P are M
    # All S are M
    # ∴ All S are P
    invalid = construct_syllogism(
        "cats", "dogs", "animals",
        "AAA", Figure.FIGURE_2
    )
    result = check_validity(invalid)
    assert not result.is_valid
    assert ValidityError.UNDISTRIBUTED_MIDDLE in result.errors
    
    # Test conclusion generation
    major = Proposition(Term("men"), Term("mortal"), PropositionType.A)
    minor = Proposition(Term("Greeks"), Term("men"), PropositionType.A)
    conclusion = generate_conclusion(major, minor)
    assert conclusion is not None
    assert conclusion.subject.name == "Greeks"
    assert conclusion.predicate.name == "mortal"
    
    # Test valid moods count
    total_valid = sum(len(moods) for moods in VALID_MOODS.values())
    assert total_valid == 19
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - SYLLOGISTIC PROCESSOR MODULE")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_syllogistic()
    print("✓ Module validated")
    
    # Demo
    print("\n--- PROPOSITION TYPES ---")
    for spec in PROPOSITION_SPECS.values():
        print(f"  {spec.prop_type.name}: {spec.form}")
        print(f"      Subject distributed: {spec.subject_distributed}")
        print(f"      Predicate distributed: {spec.predicate_distributed}")
    
    print("\n--- VALID MOODS (19 total) ---")
    for figure, moods in VALID_MOODS.items():
        print(f"  Figure {figure.value}:")
        for mood in moods:
            name = get_mood_name(figure, mood)
            print(f"    {mood}: {name}")
    
    print("\n--- BARBARA DEMONSTRATION ---")
    barbara = construct_syllogism(
        "mortal", "Socrates", "men",
        "AAA", Figure.FIGURE_1
    )
    print(barbara)
    result = check_validity(barbara)
    print(f"  Valid: {result.is_valid}")
    
    print("\n--- INVALID SYLLOGISM ---")
    invalid = construct_syllogism(
        "cats", "dogs", "animals",
        "AAA", Figure.FIGURE_2
    )
    print(invalid)
    result = check_validity(invalid)
    print(f"  Valid: {result.is_valid}")
    for msg in result.messages:
        print(f"  Error: {msg}")

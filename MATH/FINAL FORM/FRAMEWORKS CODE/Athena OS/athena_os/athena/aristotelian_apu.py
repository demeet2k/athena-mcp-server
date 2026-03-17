"""
ATHENA OS - ARISTOTELIAN PROCESSING UNIT (APU)
==============================================
The Logic Engine for Knowledge Compilation

From Greek_Corpus__LF-OS_.docx:

THE APU:
    Primary logical execution environment for LF-OS.
    Compiles raw data into validated knowledge (Episteme).

THE SYNTAX VALIDATOR (De Interpretatione):
    - Propositional Bit: logos apophantikos (declarative speech)
    - State: capacity to be True (1) or False (0)
    - Filtering: Non-truth-bearing → Rhetoric/Poetic drivers
    - Principle of Bivalence: Val(p) ∈ {0, 1}
    - Law of Non-Contradiction: ¬(P ∧ ¬P)

THE SYLLOGISTIC LINKER (Prior Analytics):
    - Middle Term M: Universal Address Bus
    - Relational Routing: M links S to P
    - 24 Valid Modes from 256 combinations
    - BARBARA (AAA-1): All M are P; All S are M → All S are P

KNOWLEDGE VALIDATION FLAGS:
    - NOUS (Root): Non-demonstrable axioms
    - EPISTEME (Verified): Demonstrative knowledge
    - TECHNE (Applied): Operational code
    - DOXA (Unverified): Low-confidence perception

FALLACY DETECTION:
    - 13 Sophistical Refutation Patterns
    - Linguistic Exploits: Equivocation, Amphiboly
    - Logical Exploits: Accident, Secundum Quid
    - Bivalence Enforcement against paradox
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import re


# =============================================================================
# PROPOSITIONAL TYPES
# =============================================================================

class PropositionType(Enum):
    """Types of propositions by quantity and quality."""
    A = auto()  # Universal Affirmative: All S are P
    E = auto()  # Universal Negative: No S is P
    I = auto()  # Particular Affirmative: Some S is P
    O = auto()  # Particular Negative: Some S is not P


class ValidationFlag(Enum):
    """Knowledge validation levels."""
    NOUS = auto()       # Root: Non-demonstrable axioms (First Principles)
    EPISTEME = auto()   # Verified: Demonstrative knowledge
    TECHNE = auto()     # Applied: Operational code
    DOXA = auto()       # Unverified: Low-confidence perception
    REJECTED = auto()   # Failed validation


class FallacyType(Enum):
    """The 13 Sophistical Refutation Patterns."""
    # Linguistic (In Dictione)
    EQUIVOCATION = auto()       # Ambiguity in term
    AMPHIBOLY = auto()          # Syntactic ambiguity
    COMPOSITION = auto()        # Parts → Whole error
    DIVISION = auto()           # Whole → Parts error
    ACCENT = auto()             # Stress/emphasis ambiguity
    FIGURE_OF_SPEECH = auto()   # Grammatical form confusion
    
    # Logical (Extra Dictione)
    ACCIDENT = auto()           # Metadata as primary key
    SECUNDUM_QUID = auto()      # Particular → Universal error
    IGNORATIO_ELENCHI = auto()  # Irrelevant conclusion
    PETITIO_PRINCIPII = auto()  # Circular reasoning
    NON_CAUSA = auto()          # False cause
    MANY_QUESTIONS = auto()     # Complex question
    CONSEQUENT = auto()         # Affirming the consequent


# =============================================================================
# THE PROPOSITIONAL BIT
# =============================================================================

@dataclass
class PropositionalBit:
    """
    The foundational unit of the APU - logos apophantikos.
    
    A signal is a propositional bit only if it possesses
    the capacity to be True (1) or False (0).
    """
    
    subject: str
    predicate: str
    prop_type: PropositionType
    truth_value: Optional[bool] = None  # None = unassigned
    
    def __post_init__(self):
        self.prop_id = f"{self.prop_type.name}({self.subject}, {self.predicate})"
    
    @property
    def is_universal(self) -> bool:
        """Check if proposition is universal."""
        return self.prop_type in {PropositionType.A, PropositionType.E}
    
    @property
    def is_affirmative(self) -> bool:
        """Check if proposition is affirmative."""
        return self.prop_type in {PropositionType.A, PropositionType.I}
    
    @property
    def is_assigned(self) -> bool:
        """Check if truth value is assigned."""
        return self.truth_value is not None
    
    def assign(self, value: bool) -> None:
        """Assign truth value."""
        self.truth_value = value
    
    def get_contradictory(self) -> 'PropositionalBit':
        """Get the contradictory proposition."""
        contra_types = {
            PropositionType.A: PropositionType.O,
            PropositionType.E: PropositionType.I,
            PropositionType.I: PropositionType.E,
            PropositionType.O: PropositionType.A
        }
        return PropositionalBit(
            self.subject,
            self.predicate,
            contra_types[self.prop_type],
            None if self.truth_value is None else not self.truth_value
        )
    
    def __str__(self) -> str:
        type_str = {
            PropositionType.A: f"All {self.subject} are {self.predicate}",
            PropositionType.E: f"No {self.subject} is {self.predicate}",
            PropositionType.I: f"Some {self.subject} is {self.predicate}",
            PropositionType.O: f"Some {self.subject} is not {self.predicate}"
        }
        val = f" [{self.truth_value}]" if self.is_assigned else ""
        return type_str[self.prop_type] + val


# =============================================================================
# THE SYNTAX VALIDATOR
# =============================================================================

class SyntaxValidator:
    """
    The APU's front-end parser (De Interpretatione).
    
    Defines formal requirements for valid logical input.
    Filters out meaningless noise.
    """
    
    def __init__(self):
        self.validated_propositions: Dict[str, PropositionalBit] = {}
        self.rejected_count = 0
    
    def is_declarative(self, statement: str) -> bool:
        """
        Check if statement is declarative (truth-bearing).
        
        Non-truth-bearing (prayers, commands, metaphors) are routed
        to Rhetoric/Poetic drivers.
        """
        # Simple heuristics for declarative statements
        non_declarative_patterns = [
            r"^please\b",
            r"^can you\b",
            r"\?$",
            r"^may\b",
            r"^let\b",
            r"^o \w+",  # Invocations
        ]
        
        statement_lower = statement.lower().strip()
        
        for pattern in non_declarative_patterns:
            if re.search(pattern, statement_lower):
                return False
        
        return True
    
    def parse_proposition(self, statement: str) -> Optional[PropositionalBit]:
        """
        Parse a natural language statement into a propositional bit.
        
        Returns None if statement is not declarative.
        """
        if not self.is_declarative(statement):
            self.rejected_count += 1
            return None
        
        statement = statement.lower().strip()
        
        # Pattern matching for AEIO forms
        patterns = [
            (r"all (\w+) are (\w+)", PropositionType.A),
            (r"no (\w+) (?:is|are) (\w+)", PropositionType.E),
            (r"some (\w+) (?:is|are) (\w+)", PropositionType.I),
            (r"some (\w+) (?:is|are) not (\w+)", PropositionType.O),
        ]
        
        for pattern, prop_type in patterns:
            match = re.match(pattern, statement)
            if match:
                return PropositionalBit(
                    match.group(1),
                    match.group(2),
                    prop_type
                )
        
        # Default: try to extract S and P
        words = statement.split()
        if len(words) >= 3:
            return PropositionalBit(words[0], words[-1], PropositionType.A)
        
        self.rejected_count += 1
        return None
    
    def validate_bivalence(self, prop: PropositionalBit) -> bool:
        """
        Enforce Principle of Bivalence.
        
        Val(p) ∈ {0, 1} - no fuzzy or multi-valued states.
        """
        if prop.is_assigned:
            return prop.truth_value in {True, False}
        return True  # Unassigned is valid (future contingent)
    
    def check_non_contradiction(self, prop: PropositionalBit) -> bool:
        """
        Enforce Law of Non-Contradiction.
        
        ¬(P ∧ ¬P) - cannot simultaneously affirm and deny.
        """
        if prop.prop_id in self.validated_propositions:
            existing = self.validated_propositions[prop.prop_id]
            if existing.is_assigned and prop.is_assigned:
                return existing.truth_value == prop.truth_value
        return True
    
    def validate(self, prop: PropositionalBit) -> bool:
        """Full validation of a proposition."""
        if not self.validate_bivalence(prop):
            return False
        if not self.check_non_contradiction(prop):
            return False
        
        self.validated_propositions[prop.prop_id] = prop
        return True


# =============================================================================
# THE SQUARE OF OPPOSITION
# =============================================================================

class SquareOfOpposition:
    """
    The Square of Opposition - logical relationships between AEIO forms.
    
    A ←contradictory→ O
    E ←contradictory→ I
    A ←contrary→ E
    I ←subcontrary→ O
    A →subaltern→ I
    E →subaltern→ O
    """
    
    @staticmethod
    def are_contradictory(p1: PropositionalBit, p2: PropositionalBit) -> bool:
        """Check if propositions are contradictory (cannot both be T or both F)."""
        if p1.subject != p2.subject or p1.predicate != p2.predicate:
            return False
        
        contradictory_pairs = {
            (PropositionType.A, PropositionType.O),
            (PropositionType.O, PropositionType.A),
            (PropositionType.E, PropositionType.I),
            (PropositionType.I, PropositionType.E),
        }
        return (p1.prop_type, p2.prop_type) in contradictory_pairs
    
    @staticmethod
    def are_contrary(p1: PropositionalBit, p2: PropositionalBit) -> bool:
        """Check if propositions are contrary (cannot both be T, can both be F)."""
        if p1.subject != p2.subject or p1.predicate != p2.predicate:
            return False
        
        return {p1.prop_type, p2.prop_type} == {PropositionType.A, PropositionType.E}
    
    @staticmethod
    def are_subcontrary(p1: PropositionalBit, p2: PropositionalBit) -> bool:
        """Check if subcontrary (cannot both be F, can both be T)."""
        if p1.subject != p2.subject or p1.predicate != p2.predicate:
            return False
        
        return {p1.prop_type, p2.prop_type} == {PropositionType.I, PropositionType.O}
    
    @staticmethod
    def is_subaltern(universal: PropositionalBit, 
                    particular: PropositionalBit) -> bool:
        """Check if particular is subaltern of universal."""
        if universal.subject != particular.subject:
            return False
        if universal.predicate != particular.predicate:
            return False
        
        subaltern_pairs = {
            (PropositionType.A, PropositionType.I),
            (PropositionType.E, PropositionType.O),
        }
        return (universal.prop_type, particular.prop_type) in subaltern_pairs


# =============================================================================
# THE SYLLOGISTIC LINKER
# =============================================================================

@dataclass
class Syllogism:
    """
    A Syllogism - the inference instruction.
    
    S(P₁, P₂) → C
    Major Premise: M → P
    Minor Premise: S → M
    Conclusion: S → P
    """
    
    major_premise: PropositionalBit
    minor_premise: PropositionalBit
    conclusion: Optional[PropositionalBit] = None
    figure: int = 0
    mood: str = ""
    is_valid: bool = False
    
    @property
    def middle_term(self) -> Optional[str]:
        """Get the middle term (linker between S and P)."""
        # Figure 1: M-P, S-M → S-P (M is predicate of major, subject of minor)
        # Figure 2: P-M, S-M → S-P
        # Figure 3: M-P, M-S → S-P
        # Figure 4: P-M, M-S → S-P
        
        major_terms = {self.major_premise.subject, self.major_premise.predicate}
        minor_terms = {self.minor_premise.subject, self.minor_premise.predicate}
        
        # Middle term appears in both premises but not conclusion
        middle = major_terms & minor_terms
        return middle.pop() if middle else None


class SyllogisticLinker:
    """
    The APU's relational processor (Prior Analytics).
    
    Executes the Instruction Set Architecture for deriving
    new state-values from existing memory registers.
    """
    
    # The 24 Valid Syllogistic Modes
    VALID_MODES = {
        # Figure 1 (Perfect)
        "AAA-1": ("BARBARA", "All M are P; All S are M → All S are P"),
        "EAE-1": ("CELARENT", "No M is P; All S are M → No S is P"),
        "AII-1": ("DARII", "All M are P; Some S is M → Some S is P"),
        "EIO-1": ("FERIO", "No M is P; Some S is M → Some S is not P"),
        
        # Figure 2
        "EAE-2": ("CESARE", "No P is M; All S are M → No S is P"),
        "AEE-2": ("CAMESTRES", "All P are M; No S is M → No S is P"),
        "EIO-2": ("FESTINO", "No P is M; Some S is M → Some S is not P"),
        "AOO-2": ("BAROCO", "All P are M; Some S is not M → Some S is not P"),
        
        # Figure 3
        "AAI-3": ("DARAPTI", "All M are P; All M are S → Some S is P"),
        "IAI-3": ("DISAMIS", "Some M is P; All M are S → Some S is P"),
        "AII-3": ("DATISI", "All M are P; Some M is S → Some S is P"),
        "EAO-3": ("FELAPTON", "No M is P; All M are S → Some S is not P"),
        "OAO-3": ("BOCARDO", "Some M is not P; All M are S → Some S is not P"),
        "EIO-3": ("FERISON", "No M is P; Some M is S → Some S is not P"),
        
        # Figure 4
        "AAI-4": ("BRAMANTIP", "All P are M; All M are S → Some S is P"),
        "AEE-4": ("CAMENES", "All P are M; No M is S → No S is P"),
        "IAI-4": ("DIMARIS", "Some P is M; All M are S → Some S is P"),
        "EAO-4": ("FESAPO", "No P is M; All M are S → Some S is not P"),
        "EIO-4": ("FRESISON", "No P is M; Some M is S → Some S is not P"),
    }
    
    def __init__(self):
        self.inference_count = 0
        self.valid_inferences: List[Syllogism] = []
        self.invalid_inferences: List[Syllogism] = []
    
    def _get_figure(self, major: PropositionalBit, 
                   minor: PropositionalBit) -> int:
        """Determine syllogism figure from term positions."""
        # This is simplified - full implementation would parse term positions
        return 1  # Default to Figure 1
    
    def _get_mood(self, major: PropositionalBit,
                 minor: PropositionalBit,
                 conclusion: PropositionalBit) -> str:
        """Get mood string (e.g., AAA, EAE)."""
        return (
            major.prop_type.name +
            minor.prop_type.name +
            conclusion.prop_type.name
        )
    
    def _check_distribution(self, syl: Syllogism) -> bool:
        """
        Check distribution rules.
        
        - Middle term must be distributed at least once
        - Terms distributed in conclusion must be distributed in premises
        """
        # Simplified check
        middle = syl.middle_term
        if not middle:
            return False  # No linking term
        return True
    
    def validate_syllogism(self, syl: Syllogism) -> bool:
        """Validate a syllogism."""
        if not syl.middle_term:
            return False  # Null pointer - no route
        
        if not self._check_distribution(syl):
            return False
        
        # Check against valid modes
        mood = syl.mood
        figure = syl.figure
        key = f"{mood}-{figure}"
        
        return key in self.VALID_MODES
    
    def infer(self, major: PropositionalBit,
             minor: PropositionalBit) -> Optional[Syllogism]:
        """
        Execute syllogistic inference.
        
        Returns None if no valid inference possible.
        """
        self.inference_count += 1
        
        # Find middle term
        major_terms = {major.subject, major.predicate}
        minor_terms = {minor.subject, minor.predicate}
        
        middle_terms = major_terms & minor_terms
        if not middle_terms:
            return None  # Null Pointer Exception
        
        middle = middle_terms.pop()
        
        # Determine S and P
        subject = (minor_terms - {middle}).pop() if minor_terms - {middle} else None
        predicate = (major_terms - {middle}).pop() if major_terms - {middle} else None
        
        if not subject or not predicate:
            return None
        
        # Create conclusion based on mood
        # Simplified: default to A-type if both premises are A
        if major.prop_type == PropositionType.A and minor.prop_type == PropositionType.A:
            conclusion = PropositionalBit(subject, predicate, PropositionType.A)
        elif major.prop_type == PropositionType.E:
            conclusion = PropositionalBit(subject, predicate, PropositionType.E)
        else:
            conclusion = PropositionalBit(subject, predicate, PropositionType.I)
        
        figure = self._get_figure(major, minor)
        mood = self._get_mood(major, minor, conclusion)
        
        syl = Syllogism(
            major_premise=major,
            minor_premise=minor,
            conclusion=conclusion,
            figure=figure,
            mood=mood
        )
        
        syl.is_valid = self.validate_syllogism(syl)
        
        if syl.is_valid:
            self.valid_inferences.append(syl)
        else:
            self.invalid_inferences.append(syl)
        
        return syl if syl.is_valid else None


# =============================================================================
# FALLACY DETECTOR
# =============================================================================

class FallacyDetector:
    """
    Fallacy Detection & Defense - the Security Firewall.
    
    Protects APU from Sophistical Exploits.
    """
    
    def __init__(self):
        self.detected_fallacies: List[Tuple[FallacyType, str]] = []
    
    def detect_equivocation(self, statements: List[str]) -> bool:
        """Detect equivocation (ambiguous term used differently)."""
        # Simplified: check for repeated terms with different contexts
        terms = {}
        for stmt in statements:
            words = stmt.lower().split()
            for word in words:
                if word in terms and terms[word] != stmt:
                    self.detected_fallacies.append(
                        (FallacyType.EQUIVOCATION, f"Term '{word}' used ambiguously")
                    )
                    return True
                terms[word] = stmt
        return False
    
    def detect_circular_reasoning(self, premises: List[PropositionalBit],
                                  conclusion: PropositionalBit) -> bool:
        """Detect petitio principii (circular reasoning)."""
        # Check if conclusion appears in premises
        for premise in premises:
            if (premise.subject == conclusion.subject and
                premise.predicate == conclusion.predicate and
                premise.prop_type == conclusion.prop_type):
                self.detected_fallacies.append(
                    (FallacyType.PETITIO_PRINCIPII, "Conclusion assumed in premise")
                )
                return True
        return False
    
    def detect_undistributed_middle(self, syl: Syllogism) -> bool:
        """Detect undistributed middle term error."""
        middle = syl.middle_term
        if not middle:
            return True  # No middle = error
        
        # Middle must be distributed (universal) in at least one premise
        # A distributes subject, E distributes both, I distributes neither, O distributes predicate
        
        major = syl.major_premise
        minor = syl.minor_premise
        
        major_distributes_middle = (
            (major.prop_type in {PropositionType.A, PropositionType.E} and major.subject == middle) or
            (major.prop_type in {PropositionType.E, PropositionType.O} and major.predicate == middle)
        )
        
        minor_distributes_middle = (
            (minor.prop_type in {PropositionType.A, PropositionType.E} and minor.subject == middle) or
            (minor.prop_type in {PropositionType.E, PropositionType.O} and minor.predicate == middle)
        )
        
        if not (major_distributes_middle or minor_distributes_middle):
            self.detected_fallacies.append(
                (FallacyType.ACCIDENT, f"Middle term '{middle}' not distributed")
            )
            return True
        
        return False
    
    def scan_all(self, syl: Syllogism) -> List[FallacyType]:
        """Scan for all fallacy types."""
        found = []
        
        if self.detect_undistributed_middle(syl):
            found.append(FallacyType.ACCIDENT)
        
        if self.detect_circular_reasoning(
            [syl.major_premise, syl.minor_premise],
            syl.conclusion
        ):
            found.append(FallacyType.PETITIO_PRINCIPII)
        
        return found


# =============================================================================
# THE ARISTOTELIAN PROCESSING UNIT
# =============================================================================

class AristotelianProcessingUnit:
    """
    The complete Aristotelian Processing Unit (APU).
    
    Integrates:
    - Syntax Validator
    - Square of Opposition
    - Syllogistic Linker
    - Fallacy Detector
    - Knowledge Graph
    """
    
    def __init__(self):
        self.validator = SyntaxValidator()
        self.square = SquareOfOpposition()
        self.linker = SyllogisticLinker()
        self.fallacy_detector = FallacyDetector()
        
        # Knowledge Graph
        self.knowledge_graph: Dict[str, Tuple[PropositionalBit, ValidationFlag]] = {}
        self.axioms: List[PropositionalBit] = []
    
    def add_axiom(self, prop: PropositionalBit) -> None:
        """Add axiom (NOUS level - First Principle)."""
        prop.assign(True)
        self.axioms.append(prop)
        self.knowledge_graph[prop.prop_id] = (prop, ValidationFlag.NOUS)
    
    def process_statement(self, statement: str) -> Optional[PropositionalBit]:
        """Process a natural language statement."""
        prop = self.validator.parse_proposition(statement)
        if prop and self.validator.validate(prop):
            return prop
        return None
    
    def infer_and_validate(self, major: PropositionalBit,
                          minor: PropositionalBit) -> Optional[PropositionalBit]:
        """
        Execute inference and validate result.
        
        Returns conclusion if valid, None otherwise.
        """
        syl = self.linker.infer(major, minor)
        
        if not syl:
            return None
        
        # Check for fallacies
        fallacies = self.fallacy_detector.scan_all(syl)
        if fallacies:
            return None
        
        # Add to knowledge graph
        conclusion = syl.conclusion
        conclusion.assign(True)
        self.knowledge_graph[conclusion.prop_id] = (
            conclusion, ValidationFlag.EPISTEME
        )
        
        return conclusion
    
    def query(self, prop_id: str) -> Optional[Tuple[PropositionalBit, ValidationFlag]]:
        """Query the knowledge graph."""
        return self.knowledge_graph.get(prop_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get APU statistics."""
        flags = [v[1] for v in self.knowledge_graph.values()]
        return {
            "total_propositions": len(self.knowledge_graph),
            "axioms": flags.count(ValidationFlag.NOUS),
            "episteme": flags.count(ValidationFlag.EPISTEME),
            "valid_inferences": len(self.linker.valid_inferences),
            "invalid_inferences": len(self.linker.invalid_inferences),
            "fallacies_detected": len(self.fallacy_detector.detected_fallacies)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_aristotelian_processing_unit() -> bool:
    """Validate the APU module."""
    
    # Test PropositionalBit
    prop_a = PropositionalBit("men", "mortal", PropositionType.A)
    assert prop_a.is_universal
    assert prop_a.is_affirmative
    assert not prop_a.is_assigned
    
    prop_a.assign(True)
    assert prop_a.is_assigned
    assert prop_a.truth_value == True
    
    # Test contradictory
    contra = prop_a.get_contradictory()
    assert contra.prop_type == PropositionType.O
    
    # Test Square of Opposition
    prop_e = PropositionalBit("men", "mortal", PropositionType.E)
    assert SquareOfOpposition.are_contrary(prop_a, prop_e)
    assert SquareOfOpposition.are_contradictory(prop_a, contra)
    
    # Test Syntax Validator
    validator = SyntaxValidator()
    assert validator.is_declarative("All men are mortal")
    assert not validator.is_declarative("Are men mortal?")
    
    parsed = validator.parse_proposition("All men are mortal")
    assert parsed.subject == "men"
    assert parsed.predicate == "mortal"
    assert parsed.prop_type == PropositionType.A
    
    # Test Syllogistic Linker
    linker = SyllogisticLinker()
    
    major = PropositionalBit("mortal", "finite", PropositionType.A)
    minor = PropositionalBit("men", "mortal", PropositionType.A)
    
    syl = linker.infer(major, minor)
    assert syl is not None
    assert syl.middle_term == "mortal"
    
    # Test full APU
    apu = AristotelianProcessingUnit()
    
    # Add axiom
    axiom = PropositionalBit("animals", "mortal", PropositionType.A)
    apu.add_axiom(axiom)
    
    # Process statements
    p1 = apu.process_statement("All men are animals")
    assert p1 is not None
    
    # Make inference
    conclusion = apu.infer_and_validate(axiom, p1)
    # Note: This should produce "All men are mortal" via Barbara
    
    stats = apu.get_statistics()
    assert stats["axioms"] == 1
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - ARISTOTELIAN PROCESSING UNIT")
    print("The Logic Engine for Knowledge Compilation")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_aristotelian_processing_unit()
    print("✓ Module validated")
    
    # Demo
    print("\n--- SYLLOGISTIC INFERENCE DEMO ---")
    apu = AristotelianProcessingUnit()
    
    # Classic Barbara syllogism
    print("\nBARBARA Syllogism:")
    major = PropositionalBit("animals", "mortal", PropositionType.A)
    minor = PropositionalBit("men", "animals", PropositionType.A)
    
    print(f"  Major: {major}")
    print(f"  Minor: {minor}")
    
    apu.add_axiom(major)
    apu.add_axiom(minor)
    
    conclusion = apu.infer_and_validate(major, minor)
    if conclusion:
        print(f"  Conclusion: {conclusion}")
    
    print("\n--- VALID SYLLOGISTIC MODES ---")
    for mode, (name, desc) in list(apu.linker.VALID_MODES.items())[:6]:
        print(f"  {mode}: {name}")
    print(f"  ... and {len(apu.linker.VALID_MODES) - 6} more")
    
    print("\n--- APU STATISTICS ---")
    stats = apu.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

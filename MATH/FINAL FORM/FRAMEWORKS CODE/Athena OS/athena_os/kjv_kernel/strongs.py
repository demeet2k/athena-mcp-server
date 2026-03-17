"""
ATHENA OS - KJV BIBLE COMPUTATIONAL FRAMEWORK
==============================================
Part V: Strong's Concordance Interface (Memory Map)

THE RELATIONAL SCHEMA:
    The KJV operates on a One-to-Many Relational Schema.
    A single English token serves as a CONTAINER INTERFACE
    for multiple distinct Source Variables (Hebrew/Greek).

THE STRONG'S NUMBERING SYSTEM:
    - Hebrew Database: H0001 to H8674
    - Greek Database: G0001 to G5624
    
    This creates a BIJECTIVE MAPPING between target language
    and source, acting as a MEMORY MAP.

THE SELECTOR SCHEMATIC:
    English Token (E) → Strong's ID (H/G) → Source Definition (S)
    
    The English word is not static; it's a DYNAMIC POINTER
    that retrieves specific values based on the underlying ID tag.

THE KJV AS GUI:
    The KJV functions as a Graphical User Interface (GUI)
    for the Hebrew/Greek relational database.

SOURCES:
    KJV BIBLE THE AUTHORIZED KERNEL (KJV-1611)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto


# =============================================================================
# STRONG'S ENTRY TYPES
# =============================================================================

class SourceLanguage(Enum):
    """Source language indicator."""
    
    HEBREW = ("H", "Old Testament", 8674)
    GREEK = ("G", "New Testament", 5624)
    
    def __init__(self, prefix: str, testament: str, max_id: int):
        self.prefix = prefix
        self.testament = testament
        self.max_id = max_id


class PartOfSpeech(Enum):
    """Part of speech classification."""
    
    NOUN = "n"
    VERB = "v"
    ADJECTIVE = "adj"
    ADVERB = "adv"
    PREPOSITION = "prep"
    CONJUNCTION = "conj"
    PRONOUN = "pron"
    PARTICLE = "part"
    INTERJECTION = "interj"
    PROPER_NOUN = "prop_n"


# =============================================================================
# STRONG'S ENTRY
# =============================================================================

@dataclass
class StrongsEntry:
    """
    A Strong's Concordance entry.
    
    Represents a single lemma in the source language.
    """
    
    # Primary key
    strong_id: str  # e.g., "H0001", "G0025"
    
    # Source information
    language: SourceLanguage
    lemma: str  # Original word
    transliteration: str
    
    # Definition
    definition: str
    part_of_speech: PartOfSpeech
    
    # Usage
    kjv_renderings: List[str] = field(default_factory=list)
    usage_count: int = 0
    
    # Derivation
    derived_from: Optional[str] = None  # Parent Strong's ID
    
    @property
    def numeric_id(self) -> int:
        """Extract numeric part of ID."""
        return int(self.strong_id[1:])
    
    @property
    def is_hebrew(self) -> bool:
        return self.language == SourceLanguage.HEBREW
    
    @property
    def is_greek(self) -> bool:
        return self.language == SourceLanguage.GREEK
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.strong_id,
            "language": self.language.name,
            "lemma": self.lemma,
            "transliteration": self.transliteration,
            "definition": definition,
            "pos": self.part_of_speech.value,
            "kjv_renderings": self.kjv_renderings,
            "usage_count": self.usage_count,
        }


# =============================================================================
# SAMPLE STRONG'S DATABASE
# =============================================================================

# Hebrew entries (sample)
HEBREW_DATABASE = {
    "H0001": StrongsEntry(
        strong_id="H0001",
        language=SourceLanguage.HEBREW,
        lemma="אָב",
        transliteration="'ab",
        definition="father",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["father", "chief", "families", "patrimony"],
        usage_count=1180,
    ),
    "H0430": StrongsEntry(
        strong_id="H0430",
        language=SourceLanguage.HEBREW,
        lemma="אֱלֹהִים",
        transliteration="'elohiym",
        definition="God, gods, judges, angels",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["God", "god", "judge", "mighty", "angels"],
        usage_count=2606,
    ),
    "H3068": StrongsEntry(
        strong_id="H3068",
        language=SourceLanguage.HEBREW,
        lemma="יְהֹוָה",
        transliteration="Yehovah",
        definition="the existing One, proper name of God",
        part_of_speech=PartOfSpeech.PROPER_NOUN,
        kjv_renderings=["LORD", "GOD", "JEHOVAH"],
        usage_count=6519,
    ),
    "H0157": StrongsEntry(
        strong_id="H0157",
        language=SourceLanguage.HEBREW,
        lemma="אָהַב",
        transliteration="'ahab",
        definition="to love",
        part_of_speech=PartOfSpeech.VERB,
        kjv_renderings=["love", "lover", "friend", "beloved"],
        usage_count=208,
    ),
    "H7225": StrongsEntry(
        strong_id="H7225",
        language=SourceLanguage.HEBREW,
        lemma="רֵאשִׁית",
        transliteration="re'shiyth",
        definition="beginning, first, chief",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["beginning", "firstfruits", "first", "chief"],
        usage_count=51,
    ),
}

# Greek entries (sample)
GREEK_DATABASE = {
    "G0001": StrongsEntry(
        strong_id="G0001",
        language=SourceLanguage.GREEK,
        lemma="Α",
        transliteration="A",
        definition="Alpha, first letter of Greek alphabet",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["Alpha"],
        usage_count=4,
    ),
    "G0025": StrongsEntry(
        strong_id="G0025",
        language=SourceLanguage.GREEK,
        lemma="ἀγαπάω",
        transliteration="agapao",
        definition="to love (in a moral/religious sense)",
        part_of_speech=PartOfSpeech.VERB,
        kjv_renderings=["love", "beloved"],
        usage_count=143,
    ),
    "G0026": StrongsEntry(
        strong_id="G0026",
        language=SourceLanguage.GREEK,
        lemma="ἀγάπη",
        transliteration="agape",
        definition="love, benevolence, good will",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["love", "charity", "dear", "feasts"],
        usage_count=116,
    ),
    "G5368": StrongsEntry(
        strong_id="G5368",
        language=SourceLanguage.GREEK,
        lemma="φιλέω",
        transliteration="phileo",
        definition="to be a friend, have affection for",
        part_of_speech=PartOfSpeech.VERB,
        kjv_renderings=["love", "kiss"],
        usage_count=25,
    ),
    "G3056": StrongsEntry(
        strong_id="G3056",
        language=SourceLanguage.GREEK,
        lemma="λόγος",
        transliteration="logos",
        definition="word, discourse, reason",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["word", "saying", "account", "speech", "Word"],
        usage_count=330,
    ),
    "G2316": StrongsEntry(
        strong_id="G2316",
        language=SourceLanguage.GREEK,
        lemma="θεός",
        transliteration="theos",
        definition="God, deity",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["God", "god", "godly"],
        usage_count=1343,
    ),
    "G2424": StrongsEntry(
        strong_id="G2424",
        language=SourceLanguage.GREEK,
        lemma="Ἰησοῦς",
        transliteration="Iesous",
        definition="Jesus, the name of our Lord",
        part_of_speech=PartOfSpeech.PROPER_NOUN,
        kjv_renderings=["Jesus", "Joshua"],
        usage_count=975,
    ),
    "G5547": StrongsEntry(
        strong_id="G5547",
        language=SourceLanguage.GREEK,
        lemma="Χριστός",
        transliteration="Christos",
        definition="Christ, anointed one",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["Christ"],
        usage_count=569,
    ),
}


# =============================================================================
# THE CHARITY BIFURCATION
# =============================================================================

@dataclass
class CharityBifurcation:
    """
    The context-sensitive split for G26 (Agape).
    
    The KJV splits G26 into "Love" and "Charity" based on context.
    This demonstrates the Pre-Processed Database function.
    """
    
    source_id: str = "G0026"
    source_word: str = "ἀγάπη"
    transliteration: str = "agape"
    
    @property
    def selector_logic(self) -> Dict[str, Dict[str, str]]:
        """The context selector function."""
        return {
            "LOVE": {
                "filter": "Abstract/Universal",
                "context": "General Divine Attribute",
                "example": "God is love (1 John 4:8)",
                "semantic": "The *nature* of God",
            },
            "CHARITY": {
                "filter": "Concrete/Applied",
                "context": "Specific Act of Will toward Neighbor",
                "example": "And now abideth faith, hope, charity (1 Cor 13:13)",
                "semantic": "The *duty* of Man",
            },
        }
    
    @property
    def significance(self) -> str:
        """Why this bifurcation matters."""
        return ("The KJV functions as a Pre-Processed Database. "
                "The translators analyzed the metadata of G26 and assigned "
                "distinct English file names ('Love' vs 'Charity') to help "
                "the User distinguish between the nature of God and the duty of Man.")


# =============================================================================
# THE LOVE VARIABLE SCHEMATIC
# =============================================================================

@dataclass
class LoveVariableSchematic:
    """
    The "Love" variable as a Dynamic Pointer.
    
    Visualizes how "Love" retrieves different values based on context.
    """
    
    english_token: str = "Love"
    
    @property
    def pointers(self) -> Dict[str, Dict[str, str]]:
        """The memory pointers for "Love"."""
        return {
            "H0157": {
                "lemma": "אָהַב",
                "transliteration": "'ahab",
                "definition": "Volitional Desire",
                "testament": "OT",
                "context": "Human subject",
            },
            "G0025": {
                "lemma": "ἀγαπάω",
                "transliteration": "agapao",
                "definition": "Divine/Moral Preference",
                "testament": "NT",
                "context": "God/Will as subject",
            },
            "G5368": {
                "lemma": "φιλέω",
                "transliteration": "phileo",
                "definition": "Affectionate/Friendship",
                "testament": "NT",
                "context": "Emotion as subject",
            },
        }
    
    @property
    def john_21_case_study(self) -> Dict[str, Any]:
        """
        The John 21:15-17 case study.
        
        Jesus toggles between G25 and G5368, testing Peter.
        """
        return {
            "john_21_15": {
                "text": "lovest (G25) thou me?",
                "word": "agapao",
                "type": "Volitional/Divine Love",
            },
            "john_21_16": {
                "text": "lovest (G25) thou me?",
                "word": "agapao", 
                "type": "Volitional/Divine Love",
            },
            "john_21_17": {
                "text": "lovest (G5368) thou me?",
                "word": "phileo",
                "type": "Affectionate/Brotherly Love",
            },
            "analysis": ("Jesus toggles the variable type from G25 to G5368, "
                        "executing a subroutine that tests Peter's emotional register. "
                        "Without the Strong's Interface, this variable swap is invisible."),
        }


# =============================================================================
# STRONG'S CONCORDANCE INTERFACE
# =============================================================================

@dataclass
class StrongsConcordance:
    """
    The Strong's Concordance as a memory map interface.
    
    Transforms the KJV into an indexed relational database.
    """
    
    hebrew_db: Dict[str, StrongsEntry] = field(default_factory=lambda: HEBREW_DATABASE.copy())
    greek_db: Dict[str, StrongsEntry] = field(default_factory=lambda: GREEK_DATABASE.copy())
    
    # Semantic mappings
    charity_bifurcation: CharityBifurcation = field(default_factory=CharityBifurcation)
    love_schematic: LoveVariableSchematic = field(default_factory=LoveVariableSchematic)
    
    def lookup(self, strong_id: str) -> Optional[StrongsEntry]:
        """
        Look up a Strong's entry by ID.
        
        Forward Operation: ID → Definition
        """
        if strong_id.startswith("H"):
            return self.hebrew_db.get(strong_id)
        elif strong_id.startswith("G"):
            return self.greek_db.get(strong_id)
        return None
    
    def reverse_lookup(self, english_word: str) -> List[StrongsEntry]:
        """
        Reverse lookup: Find all Strong's entries for an English word.
        
        Reverse Operation: English → IDs → Source
        """
        matches = []
        
        english_lower = english_word.lower()
        
        for entry in self.hebrew_db.values():
            if any(r.lower() == english_lower for r in entry.kjv_renderings):
                matches.append(entry)
        
        for entry in self.greek_db.values():
            if any(r.lower() == english_lower for r in entry.kjv_renderings):
                matches.append(entry)
        
        return matches
    
    def get_hebrew_count(self) -> int:
        """Get count of Hebrew entries."""
        return len(self.hebrew_db)
    
    def get_greek_count(self) -> int:
        """Get count of Greek entries."""
        return len(self.greek_db)
    
    def get_total_range(self) -> Dict[str, int]:
        """Get the full range of Strong's numbers."""
        return {
            "hebrew_max": SourceLanguage.HEBREW.max_id,
            "greek_max": SourceLanguage.GREEK.max_id,
            "total": SourceLanguage.HEBREW.max_id + SourceLanguage.GREEK.max_id,
        }
    
    def explain_formal_equivalence(self) -> Dict[str, str]:
        """
        Explain why Formal Equivalence is required for Strong's mapping.
        """
        return {
            "kjv_architecture": (
                "Preserves sentence structure and word order. "
                "1 Source Word ≈ 1 English Word. The mapping is clean. The GUI works."
            ),
            "dynamic_equivalence": (
                "Rephrases entire thoughts. "
                "1 Source Word → Entire Sentence OR 5 Source Words → 1 English Phrase. "
                "The mapping breaks. Strong's numbers become misaligned pointers."
            ),
            "conclusion": (
                "The English becomes a transparent window into the underlying "
                "numeric structure. Without the KJV's rigid consistency, "
                "the Memory Map fails."
            ),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_strongs() -> bool:
    """Validate the Strong's module."""
    
    # Test StrongsEntry
    entry = StrongsEntry(
        strong_id="H0001",
        language=SourceLanguage.HEBREW,
        lemma="אָב",
        transliteration="'ab",
        definition="father",
        part_of_speech=PartOfSpeech.NOUN,
        kjv_renderings=["father"],
        usage_count=1180,
    )
    assert entry.numeric_id == 1
    assert entry.is_hebrew
    assert not entry.is_greek
    
    # Test StrongsConcordance
    concordance = StrongsConcordance()
    
    # Forward lookup
    yhwh = concordance.lookup("H3068")
    assert yhwh is not None
    assert "LORD" in yhwh.kjv_renderings
    
    jesus = concordance.lookup("G2424")
    assert jesus is not None
    assert "Jesus" in jesus.kjv_renderings
    
    # Reverse lookup
    love_entries = concordance.reverse_lookup("love")
    assert len(love_entries) > 0
    
    # Test CharityBifurcation
    charity = CharityBifurcation()
    assert "LOVE" in charity.selector_logic
    assert "CHARITY" in charity.selector_logic
    
    # Test LoveVariableSchematic
    love_schema = LoveVariableSchematic()
    assert "H0157" in love_schema.pointers
    assert "G0025" in love_schema.pointers
    assert "G5368" in love_schema.pointers
    
    # Verify John 21 case study
    john_21 = love_schema.john_21_case_study
    assert john_21["john_21_15"]["word"] == "agapao"
    assert john_21["john_21_17"]["word"] == "phileo"
    
    return True


if __name__ == "__main__":
    print("Validating Strong's Module...")
    assert validate_strongs()
    print("✓ Strong's module validated")
    
    # Demo
    print("\n--- Strong's Concordance Demo ---")
    
    concordance = StrongsConcordance()
    
    print("\nStrong's Number Ranges:")
    ranges = concordance.get_total_range()
    print(f"  Hebrew: H0001 - H{ranges['hebrew_max']}")
    print(f"  Greek: G0001 - G{ranges['greek_max']}")
    
    print("\nSample Lookups:")
    for sid in ["H3068", "H0430", "G2424", "G3056"]:
        entry = concordance.lookup(sid)
        if entry:
            print(f"  {sid}: {entry.transliteration} = {entry.definition[:40]}...")
    
    print("\nReverse Lookup ('love'):")
    love_entries = concordance.reverse_lookup("love")
    for entry in love_entries:
        print(f"  {entry.strong_id} ({entry.transliteration}): {entry.definition[:40]}...")
    
    print("\nCharity Bifurcation (G26):")
    bifurcation = concordance.charity_bifurcation
    for output, details in bifurcation.selector_logic.items():
        print(f"  {output}:")
        print(f"    Filter: {details['filter']}")
        print(f"    Example: {details['example']}")
    
    print("\nJohn 21:15-17 Case Study (Peter's Love):")
    john_21 = concordance.love_schematic.john_21_case_study
    for verse in ["john_21_15", "john_21_16", "john_21_17"]:
        data = john_21[verse]
        print(f"  {verse}: {data['word']} ({data['type']})")

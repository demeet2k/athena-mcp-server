"""
ATHENA OS - TORAT HA-MISPAR (תורת המספר)
=========================================
Module IV: Sefirot (ספירות) - The 10 Processing Nodes

THE SEFIROT DEFINED:
    The Ten Sefirot are Dimensional Processing Nodes within a 
    Directed Acyclic Graph (The Tree of Life / Etz Chaim).
    
    They function as the CPU architecture of the cosmic computer,
    stepping down infinite data into finite manifestation.

THE THREE-COLUMN ARCHITECTURE:
    Right Column (Chesed/Netzach/Chochmah) - Expansion/Giving
    Left Column (Gevurah/Hod/Binah) - Restriction/Receiving
    Middle Column (Keter/Tiferet/Yesod/Malkhut) - Balance/Integration

THE DATA FLOW:
    Keter (Input) → Chochmah → Binah → ... → Malkhut (Output)
    
    Each Sefirah transforms the data, adding structure and reducing
    the signal intensity until it can be processed by finite vessels.

THE 32 PATHS:
    10 Sefirot + 22 Letters = 32 Paths of Wisdom
    The letters connect the nodes, creating the network topology.

SOURCES:
    TORAT HA-MISPAR (תורת המספר)
    ETZ CHAIM (עץ חיים)
    SEFER YETZIRAH (ספר יצירה)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# COLUMN ARCHITECTURE
# =============================================================================

class Column(Enum):
    """The three columns of the Tree of Life."""
    
    RIGHT = ("Chesed", "Expansion/Giving/Mercy")
    LEFT = ("Gevurah", "Restriction/Receiving/Severity")
    MIDDLE = ("Tiferet", "Balance/Integration/Beauty")
    
    def __init__(self, primary_sefirah: str, function: str):
        self.primary_sefirah = primary_sefirah
        self._function = function


class Partzuf(Enum):
    """The Partzufim (Divine Personas/Interfaces)."""
    
    ATIK_YOMIN = ("עתיק יומין", "Ancient of Days", "Keter - external")
    ARICH_ANPIN = ("אריך אנפין", "Long Face", "Keter - internal")
    ABBA = ("אבא", "Father", "Chochmah")
    IMMA = ("אמא", "Mother", "Binah")
    ZEIR_ANPIN = ("זעיר אנפין", "Short Face", "Six midot (Chesed-Yesod)")
    NUKVA = ("נוקבא", "Female", "Malkhut")
    
    def __init__(self, hebrew: str, translation: str, correspondence: str):
        self.hebrew = hebrew
        self.translation = translation
        self.correspondence = correspondence


# =============================================================================
# SEFIRAH DEFINITION
# =============================================================================

@dataclass
class Sefirah:
    """
    A single Sefirah - Processing Node.
    """
    
    # Identity
    name: str
    hebrew: str
    translation: str
    
    # Position
    number: int  # 1-10
    column: Column
    
    # Function
    function: str
    attribute: str
    
    # Body correspondence (Adam Kadmon)
    body_part: str
    
    # Divine Name correspondence
    divine_name: Optional[str] = None
    divine_name_hebrew: Optional[str] = None
    
    # Partzuf correspondence
    partzuf: Optional[Partzuf] = None
    
    # Color correspondence
    color: Optional[str] = None
    
    # Day of creation
    day: Optional[int] = None
    
    @property
    def is_supernal(self) -> bool:
        """Is this a supernal (upper) Sefirah?"""
        return self.number <= 3
    
    @property
    def is_emotive(self) -> bool:
        """Is this an emotive (midot) Sefirah?"""
        return 4 <= self.number <= 9
    
    @property
    def is_action(self) -> bool:
        """Is this the action (Malkhut) Sefirah?"""
        return self.number == 10


# =============================================================================
# THE TEN SEFIROT
# =============================================================================

SEFIROT = [
    Sefirah(
        name="Keter", hebrew="כתר", translation="Crown",
        number=1, column=Column.MIDDLE,
        function="Source Input / Divine Will",
        attribute="Will above intellect",
        body_part="Crown of head / Skull",
        divine_name="Ehyeh", divine_name_hebrew="אהיה",
        partzuf=Partzuf.ARICH_ANPIN,
        color="Blinding white / Colorless",
    ),
    Sefirah(
        name="Chochmah", hebrew="חכמה", translation="Wisdom",
        number=2, column=Column.RIGHT,
        function="Flash of insight / Raw data",
        attribute="Point of conception",
        body_part="Right brain",
        divine_name="Yah", divine_name_hebrew="יה",
        partzuf=Partzuf.ABBA,
        color="Gray / Sky blue",
        day=1,
    ),
    Sefirah(
        name="Binah", hebrew="בינה", translation="Understanding",
        number=3, column=Column.LEFT,
        function="Analysis / Structure",
        attribute="Palace that receives the point",
        body_part="Left brain / Heart",
        divine_name="YHVH Elohim", divine_name_hebrew="יהוה אלהים",
        partzuf=Partzuf.IMMA,
        color="Green / Black",
        day=2,
    ),
    Sefirah(
        name="Chesed", hebrew="חסד", translation="Loving-kindness",
        number=4, column=Column.RIGHT,
        function="Expansion / Giving",
        attribute="Unconditional love",
        body_part="Right arm",
        divine_name="El", divine_name_hebrew="אל",
        partzuf=Partzuf.ZEIR_ANPIN,
        color="White / Silver",
        day=1,
    ),
    Sefirah(
        name="Gevurah", hebrew="גבורה", translation="Severity/Strength",
        number=5, column=Column.LEFT,
        function="Restriction / Judgment",
        attribute="Discipline and boundaries",
        body_part="Left arm",
        divine_name="Elohim", divine_name_hebrew="אלהים",
        partzuf=Partzuf.ZEIR_ANPIN,
        color="Red",
        day=2,
    ),
    Sefirah(
        name="Tiferet", hebrew="תפארת", translation="Beauty/Harmony",
        number=6, column=Column.MIDDLE,
        function="Balance / Integration",
        attribute="Compassion - synthesis of love and judgment",
        body_part="Torso / Heart",
        divine_name="YHVH", divine_name_hebrew="יהוה",
        partzuf=Partzuf.ZEIR_ANPIN,
        color="Yellow / Purple",
        day=3,
    ),
    Sefirah(
        name="Netzach", hebrew="נצח", translation="Victory/Eternity",
        number=7, column=Column.RIGHT,
        function="Persistence / Endurance",
        attribute="Overcoming obstacles",
        body_part="Right leg",
        divine_name="YHVH Tzvaot", divine_name_hebrew="יהוה צבאות",
        partzuf=Partzuf.ZEIR_ANPIN,
        color="Light pink",
        day=4,
    ),
    Sefirah(
        name="Hod", hebrew="הוד", translation="Glory/Splendor",
        number=8, column=Column.LEFT,
        function="Submission / Acknowledgment",
        attribute="Humility and gratitude",
        body_part="Left leg",
        divine_name="Elohim Tzvaot", divine_name_hebrew="אלהים צבאות",
        partzuf=Partzuf.ZEIR_ANPIN,
        color="Dark pink",
        day=5,
    ),
    Sefirah(
        name="Yesod", hebrew="יסוד", translation="Foundation",
        number=9, column=Column.MIDDLE,
        function="Channel / Connection",
        attribute="Bonding and covenant",
        body_part="Reproductive organ",
        divine_name="El Chai / Shaddai", divine_name_hebrew="אל חי / שדי",
        partzuf=Partzuf.ZEIR_ANPIN,
        color="Orange",
        day=6,
    ),
    Sefirah(
        name="Malkhut", hebrew="מלכות", translation="Kingdom/Sovereignty",
        number=10, column=Column.MIDDLE,
        function="Output / Manifestation",
        attribute="Receptive vessel - the Shekhinah",
        body_part="Feet / Mouth",
        divine_name="Adonai", divine_name_hebrew="אדני",
        partzuf=Partzuf.NUKVA,
        color="Blue / Black",
        day=7,
    ),
]

# Da'at - the hidden "non-Sefirah"
DAAT = Sefirah(
    name="Da'at", hebrew="דעת", translation="Knowledge",
    number=0, column=Column.MIDDLE,  # Special position
    function="Integration of Wisdom and Understanding",
    attribute="Unification of opposites",
    body_part="Back of head / Cerebellum",
    divine_name="YHVH Elohim", divine_name_hebrew="יהוה אלהים",
    color="Invisible / All colors",
)


# =============================================================================
# PATH CONNECTIONS
# =============================================================================

@dataclass
class Path:
    """A path connecting two Sefirot."""
    
    number: int  # 1-22
    from_sefirah: str
    to_sefirah: str
    letter: str
    letter_name: str
    
    @property
    def direction(self) -> str:
        """Direction of energy flow (generally downward)."""
        return f"{self.from_sefirah} → {self.to_sefirah}"


# The 22 Paths (letters connecting Sefirot)
PATHS = [
    Path(1, "Keter", "Chochmah", "א", "Aleph"),
    Path(2, "Keter", "Binah", "ב", "Bet"),
    Path(3, "Keter", "Tiferet", "ג", "Gimel"),
    Path(4, "Chochmah", "Binah", "ד", "Dalet"),
    Path(5, "Chochmah", "Tiferet", "ה", "Heh"),
    Path(6, "Chochmah", "Chesed", "ו", "Vav"),
    Path(7, "Binah", "Tiferet", "ז", "Zayin"),
    Path(8, "Binah", "Gevurah", "ח", "Chet"),
    Path(9, "Chesed", "Gevurah", "ט", "Tet"),
    Path(10, "Chesed", "Tiferet", "י", "Yod"),
    Path(11, "Gevurah", "Tiferet", "כ", "Kaf"),
    Path(12, "Chesed", "Netzach", "ל", "Lamed"),
    Path(13, "Tiferet", "Netzach", "מ", "Mem"),
    Path(14, "Tiferet", "Yesod", "נ", "Nun"),
    Path(15, "Tiferet", "Hod", "ס", "Samekh"),
    Path(16, "Gevurah", "Hod", "ע", "Ayin"),
    Path(17, "Netzach", "Hod", "פ", "Peh"),
    Path(18, "Netzach", "Yesod", "צ", "Tzadi"),
    Path(19, "Hod", "Yesod", "ק", "Qof"),
    Path(20, "Netzach", "Malkhut", "ר", "Resh"),
    Path(21, "Yesod", "Malkhut", "ש", "Shin"),
    Path(22, "Hod", "Malkhut", "ת", "Tav"),
]


# =============================================================================
# TREE OF LIFE STRUCTURE
# =============================================================================

@dataclass
class TreeOfLife:
    """
    The Tree of Life (Etz Chaim) - Complete Graph Structure.
    
    A Directed Acyclic Graph with 10 nodes (Sefirot) and 22 edges (Paths).
    Total: 32 Paths of Wisdom (Lamed-Bet Netivot Chochmah)
    """
    
    sefirot: List[Sefirah] = field(default_factory=lambda: SEFIROT.copy())
    paths: List[Path] = field(default_factory=lambda: PATHS.copy())
    daat: Sefirah = field(default_factory=lambda: DAAT)
    
    @property
    def total_paths_of_wisdom(self) -> int:
        """Total paths of wisdom."""
        return len(self.sefirot) + len(self.paths)  # 10 + 22 = 32
    
    def get_sefirah(self, name: str) -> Optional[Sefirah]:
        """Get a Sefirah by name."""
        for s in self.sefirot:
            if s.name.lower() == name.lower():
                return s
        if name.lower() == "daat" or name.lower() == "da'at":
            return self.daat
        return None
    
    def get_by_number(self, number: int) -> Optional[Sefirah]:
        """Get a Sefirah by number."""
        if number == 0:
            return self.daat
        for s in self.sefirot:
            if s.number == number:
                return s
        return None
    
    def get_column(self, column: Column) -> List[Sefirah]:
        """Get all Sefirot in a column."""
        return [s for s in self.sefirot if s.column == column]
    
    def get_supernals(self) -> List[Sefirah]:
        """Get the three supernal Sefirot."""
        return [s for s in self.sefirot if s.is_supernal]
    
    def get_midot(self) -> List[Sefirah]:
        """Get the six emotive Sefirot."""
        return [s for s in self.sefirot if s.is_emotive]
    
    def get_paths_from(self, sefirah_name: str) -> List[Path]:
        """Get all paths emanating from a Sefirah."""
        return [p for p in self.paths if p.from_sefirah == sefirah_name]
    
    def get_paths_to(self, sefirah_name: str) -> List[Path]:
        """Get all paths leading to a Sefirah."""
        return [p for p in self.paths if p.to_sefirah == sefirah_name]


# =============================================================================
# DATA FLOW ANALYSIS
# =============================================================================

@dataclass
class SefirotDataFlow:
    """
    Analysis of data flow through the Sefirot.
    """
    
    @property
    def flow_sequence(self) -> List[str]:
        """The primary data flow sequence."""
        return [
            "Ein Sof (Source)",
            "Keter (Will/Crown)",
            "Chochmah (Flash/Point)",
            "Binah (Analysis/Palace)",
            "Da'at (Integration)",
            "Chesed (Expansion)",
            "Gevurah (Restriction)",
            "Tiferet (Balance)",
            "Netzach (Persistence)",
            "Hod (Acknowledgment)",
            "Yesod (Foundation/Channel)",
            "Malkhut (Output/Kingdom)",
        ]
    
    @property
    def processing_stages(self) -> Dict[str, str]:
        """The processing stages of the Sefirot."""
        return {
            "Input (Keter)": "Raw Divine Will enters system",
            "Conception (Chochmah)": "Point of pure potential data",
            "Gestation (Binah)": "Data structured and analyzed",
            "Processing (Chesed-Hod)": "Six transformations applied",
            "Transmission (Yesod)": "Data collected and channeled",
            "Output (Malkhut)": "Manifest reality produced",
        }
    
    @property
    def signal_attenuation(self) -> str:
        """How signal attenuates through levels."""
        return (
            "Each Sefirah 'steps down' the infinite signal. "
            "Like voltage transformers, they reduce intensity while "
            "preserving essential information structure. "
            "Malkhut receives ~1/∞ of Keter's raw power."
        )
    
    @property
    def three_column_dynamics(self) -> Dict[str, Any]:
        """The dynamics of the three columns."""
        return {
            "right_column": {
                "sefirot": ["Chochmah", "Chesed", "Netzach"],
                "function": "Expansion / Giving / Positive charge",
                "tendency": "Unlimited flow (would overflow without left)",
            },
            "left_column": {
                "sefirot": ["Binah", "Gevurah", "Hod"],
                "function": "Restriction / Receiving / Negative charge",
                "tendency": "Infinite contraction (would collapse without right)",
            },
            "middle_column": {
                "sefirot": ["Keter", "Tiferet", "Yesod", "Malkhut"],
                "function": "Balance / Integration / Neutral",
                "tendency": "Harmonizes the opposites",
            },
        }


# =============================================================================
# SEFIROT SYSTEM
# =============================================================================

@dataclass
class SefirotSystem:
    """
    The complete Sefirot system.
    """
    
    tree: TreeOfLife = field(default_factory=TreeOfLife)
    data_flow: SefirotDataFlow = field(default_factory=SefirotDataFlow)
    
    def get_sefirah_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get complete information about a Sefirah."""
        sefirah = self.tree.get_sefirah(name)
        if not sefirah:
            return None
        
        paths_from = self.tree.get_paths_from(name)
        paths_to = self.tree.get_paths_to(name)
        
        return {
            "name": sefirah.name,
            "hebrew": sefirah.hebrew,
            "translation": sefirah.translation,
            "number": sefirah.number,
            "column": sefirah.column.name,
            "function": sefirah.function,
            "divine_name": sefirah.divine_name,
            "body_part": sefirah.body_part,
            "paths_from": [p.to_sefirah for p in paths_from],
            "paths_to": [p.from_sefirah for p in paths_to],
        }
    
    def calculate_gematria_sum(self) -> int:
        """Sum of all Sefirah name gematriot."""
        # Simplified - would need full gematria calculation
        values = {
            "כתר": 620, "חכמה": 73, "בינה": 67,
            "חסד": 72, "גבורה": 216, "תפארת": 1081,
            "נצח": 148, "הוד": 15, "יסוד": 80,
            "מלכות": 496,
        }
        return sum(values.values())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "sefirot_count": len(self.tree.sefirot),
            "paths_count": len(self.tree.paths),
            "total_wisdom_paths": self.tree.total_paths_of_wisdom,
            "columns": {
                "right": len(self.tree.get_column(Column.RIGHT)),
                "left": len(self.tree.get_column(Column.LEFT)),
                "middle": len(self.tree.get_column(Column.MIDDLE)),
            },
            "supernals": len(self.tree.get_supernals()),
            "midot": len(self.tree.get_midot()),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_sefirot() -> bool:
    """Validate the Sefirot module."""
    
    # Test Sefirot count
    assert len(SEFIROT) == 10
    assert len(PATHS) == 22
    
    # Test Sefirah properties
    keter = SEFIROT[0]
    assert keter.name == "Keter"
    assert keter.number == 1
    assert keter.is_supernal == True
    
    malkhut = SEFIROT[9]
    assert malkhut.name == "Malkhut"
    assert malkhut.number == 10
    assert malkhut.is_action == True
    
    # Test TreeOfLife
    tree = TreeOfLife()
    assert tree.total_paths_of_wisdom == 32
    
    chochmah = tree.get_sefirah("Chochmah")
    assert chochmah is not None
    assert chochmah.number == 2
    
    daat = tree.get_sefirah("Da'at")
    assert daat is not None
    
    # Test column retrieval
    right = tree.get_column(Column.RIGHT)
    assert len(right) == 3  # Chochmah, Chesed, Netzach
    
    # Test path retrieval
    paths_from_keter = tree.get_paths_from("Keter")
    assert len(paths_from_keter) >= 2
    
    # Test SefirotSystem
    system = SefirotSystem()
    
    info = system.get_sefirah_info("Tiferet")
    assert info is not None
    assert info["number"] == 6
    
    summary = system.get_summary()
    assert summary["sefirot_count"] == 10
    assert summary["paths_count"] == 22
    assert summary["total_wisdom_paths"] == 32
    
    return True


if __name__ == "__main__":
    print("Validating Sefirot Module...")
    assert validate_sefirot()
    print("✓ Sefirot module validated")
    
    # Demo
    print("\n--- Sefirot System Demo ---")
    
    system = SefirotSystem()
    
    print(f"\n32 Paths of Wisdom:")
    summary = system.get_summary()
    print(f"  Sefirot: {summary['sefirot_count']}")
    print(f"  Letter Paths: {summary['paths_count']}")
    print(f"  Total: {summary['total_wisdom_paths']}")
    
    print("\nThree-Column Architecture:")
    dynamics = system.data_flow.three_column_dynamics
    for col, data in dynamics.items():
        print(f"  {col}: {data['sefirot']} - {data['function']}")
    
    print("\nThe Ten Sefirot:")
    for s in system.tree.sefirot:
        print(f"  {s.number}. {s.name} ({s.hebrew}) - {s.translation}")
    
    print("\nSample Sefirah Info (Tiferet):")
    info = system.get_sefirah_info("Tiferet")
    print(f"  Function: {info['function']}")
    print(f"  Divine Name: {info['divine_name']}")
    print(f"  Body Part: {info['body_part']}")

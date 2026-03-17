"""
ATHENA OS - KJV BIBLE COMPUTATIONAL FRAMEWORK
==============================================
Part X: Typology System (Types and Shadows)

TYPOLOGY DEFINED:
    A TYPE is an Old Testament person, event, or institution that
    PREFIGURES a New Testament reality (the ANTITYPE).
    
    This is not allegory - it's a FORWARD POINTER embedded in
    the historical narrative.

THE TYPE-ANTITYPE MAPPING:
    Type (OT) → Antitype (NT)
    
    - Adam → Christ (1 Cor 15:45)
    - Passover Lamb → Christ (1 Cor 5:7)
    - Moses → Christ (Deut 18:15)
    - Tabernacle → Christ's Body (John 2:21)
    - Manna → Christ (John 6:32-35)

THE SHADOW PRINCIPLE:
    "Which are a shadow of things to come; but the body is of Christ"
    (Colossians 2:17)
    
    The OT is the SHADOW; the NT is the SUBSTANCE.
    The shadow proves the substance exists.

SOURCES:
    KJV BIBLE THE AUTHORIZED KERNEL (KJV-1611)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# TYPOLOGY CATEGORIES
# =============================================================================

class TypeCategory(Enum):
    """Categories of biblical types."""
    
    PERSONAL = ("person", "A person prefiguring Christ or the Church")
    INSTITUTIONAL = ("institution", "A system or structure prefiguring NT realities")
    EVENTUAL = ("event", "A historical event prefiguring NT fulfillment")
    MATERIAL = ("object", "A physical object prefiguring spiritual reality")
    GEOGRAPHICAL = ("place", "A location prefiguring spiritual realities")
    TEMPORAL = ("time", "A time period prefiguring NT times")
    
    def __init__(self, category: str, description: str):
        self.category = category
        self._description = description


class FulfillmentStatus(Enum):
    """Status of typological fulfillment."""
    
    FULFILLED = ("complete", "Fully realized in Christ/Church")
    PARTIAL = ("progressive", "Partially fulfilled, awaiting completion")
    FUTURE = ("eschatological", "Awaiting future fulfillment")
    CONTINUOUS = ("ongoing", "Continuously being fulfilled")
    
    def __init__(self, mode: str, description: str):
        self.mode = mode
        self._description = description


# =============================================================================
# TYPE-ANTITYPE PAIR
# =============================================================================

@dataclass
class TypeAntitypePair:
    """
    A typological correspondence between OT type and NT antitype.
    """
    
    # The Type (OT)
    type_name: str
    type_reference: str
    type_description: str
    
    # The Antitype (NT)
    antitype_name: str
    antitype_reference: str
    antitype_description: str
    
    # Classification
    category: TypeCategory
    status: FulfillmentStatus
    
    # The correspondence
    correspondence: str  # How type points to antitype
    
    @property
    def pointer_notation(self) -> str:
        """Express as a pointer relationship."""
        return f"{self.type_name} → {self.antitype_name}"


# =============================================================================
# MAJOR TYPOLOGICAL PAIRS
# =============================================================================

TYPOLOGICAL_PAIRS = [
    # Personal Types
    TypeAntitypePair(
        type_name="Adam",
        type_reference="Genesis 2-3",
        type_description="The first man, federal head of fallen humanity",
        antitype_name="Christ (Last Adam)",
        antitype_reference="1 Corinthians 15:45",
        antitype_description="The second man, federal head of redeemed humanity",
        category=TypeCategory.PERSONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="As Adam brought death, Christ brings life",
    ),
    TypeAntitypePair(
        type_name="Melchizedek",
        type_reference="Genesis 14:18-20",
        type_description="King-Priest of Salem, without genealogy",
        antitype_name="Christ",
        antitype_reference="Hebrews 7:1-17",
        antitype_description="Eternal King-Priest after the order of Melchizedek",
        category=TypeCategory.PERSONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Eternal priesthood not dependent on Levitical descent",
    ),
    TypeAntitypePair(
        type_name="Isaac",
        type_reference="Genesis 22",
        type_description="Only begotten son offered by father on mount",
        antitype_name="Christ",
        antitype_reference="Hebrews 11:17-19",
        antitype_description="Only begotten Son offered by Father",
        category=TypeCategory.PERSONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Father offering beloved son; resurrection on third day",
    ),
    TypeAntitypePair(
        type_name="Joseph",
        type_reference="Genesis 37-50",
        type_description="Rejected by brethren, exalted to save them",
        antitype_name="Christ",
        antitype_reference="Acts 7:9-14",
        antitype_description="Rejected by Israel, exalted to be Savior",
        category=TypeCategory.PERSONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Rejected, sold, imprisoned, exalted, saves brethren",
    ),
    TypeAntitypePair(
        type_name="Moses",
        type_reference="Deuteronomy 18:15",
        type_description="Prophet, deliverer, mediator of old covenant",
        antitype_name="Christ",
        antitype_reference="Acts 3:22-23",
        antitype_description="Prophet, deliverer, mediator of new covenant",
        category=TypeCategory.PERSONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Deliverer from bondage, giver of law, mediator",
    ),
    TypeAntitypePair(
        type_name="David",
        type_reference="1 Samuel 16 - 2 Samuel",
        type_description="Anointed king, shepherd, rejected then enthroned",
        antitype_name="Christ (Son of David)",
        antitype_reference="Matthew 1:1; Revelation 22:16",
        antitype_description="Anointed King, Good Shepherd, reigning forever",
        category=TypeCategory.PERSONAL,
        status=FulfillmentStatus.PARTIAL,
        correspondence="Anointed king from Bethlehem ruling God's people",
    ),
    
    # Institutional Types
    TypeAntitypePair(
        type_name="Passover Lamb",
        type_reference="Exodus 12",
        type_description="Lamb without blemish, blood on doorposts",
        antitype_name="Christ (Lamb of God)",
        antitype_reference="1 Corinthians 5:7",
        antitype_description="Christ our Passover sacrificed for us",
        category=TypeCategory.INSTITUTIONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Blood applied brings deliverance from judgment",
    ),
    TypeAntitypePair(
        type_name="Tabernacle",
        type_reference="Exodus 25-40",
        type_description="Dwelling place of God among Israel",
        antitype_name="Christ / Church",
        antitype_reference="John 1:14; 1 Corinthians 3:16",
        antitype_description="God dwelling among humanity in Christ and Church",
        category=TypeCategory.INSTITUTIONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="God's presence dwelling with His people",
    ),
    TypeAntitypePair(
        type_name="Day of Atonement",
        type_reference="Leviticus 16",
        type_description="Annual sacrifice for national sins",
        antitype_name="Christ's Sacrifice",
        antitype_reference="Hebrews 9:7-14",
        antitype_description="Once-for-all sacrifice for all sins",
        category=TypeCategory.INSTITUTIONAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="High priest entering holy place with blood",
    ),
    TypeAntitypePair(
        type_name="Sabbath",
        type_reference="Genesis 2:2-3; Exodus 20:8-11",
        type_description="Seventh day rest from works",
        antitype_name="Rest in Christ",
        antitype_reference="Hebrews 4:1-11",
        antitype_description="Eternal rest from works of self-righteousness",
        category=TypeCategory.INSTITUTIONAL,
        status=FulfillmentStatus.CONTINUOUS,
        correspondence="Rest from laboring to achieve righteousness",
    ),
    
    # Material Types
    TypeAntitypePair(
        type_name="Manna",
        type_reference="Exodus 16",
        type_description="Bread from heaven sustaining Israel in wilderness",
        antitype_name="Christ (Bread of Life)",
        antitype_reference="John 6:32-35",
        antitype_description="True bread from heaven giving eternal life",
        category=TypeCategory.MATERIAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Divine provision sustaining God's people",
    ),
    TypeAntitypePair(
        type_name="Bronze Serpent",
        type_reference="Numbers 21:8-9",
        type_description="Lifted up for healing from serpent bites",
        antitype_name="Christ Crucified",
        antitype_reference="John 3:14-15",
        antitype_description="Lifted up for healing from sin's curse",
        category=TypeCategory.MATERIAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Look and live; faith in the lifted one saves",
    ),
    TypeAntitypePair(
        type_name="Rock at Horeb",
        type_reference="Exodus 17:6",
        type_description="Smitten rock producing water for Israel",
        antitype_name="Christ",
        antitype_reference="1 Corinthians 10:4",
        antitype_description="Spiritual Rock providing living water",
        category=TypeCategory.MATERIAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Smitten to provide life-giving water",
    ),
    TypeAntitypePair(
        type_name="Veil of the Temple",
        type_reference="Exodus 26:31-33",
        type_description="Barrier separating Holy Place from Most Holy",
        antitype_name="Christ's Flesh",
        antitype_reference="Hebrews 10:20",
        antitype_description="The way opened through His flesh",
        category=TypeCategory.MATERIAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Barrier removed at death, access to God opened",
    ),
    
    # Eventual Types
    TypeAntitypePair(
        type_name="The Flood",
        type_reference="Genesis 6-8",
        type_description="Judgment by water, ark of salvation",
        antitype_name="Baptism / Final Judgment",
        antitype_reference="1 Peter 3:20-21",
        antitype_description="Salvation through water, final judgment by fire",
        category=TypeCategory.EVENTUAL,
        status=FulfillmentStatus.PARTIAL,
        correspondence="Judgment and salvation through appointed means",
    ),
    TypeAntitypePair(
        type_name="Exodus from Egypt",
        type_reference="Exodus 12-14",
        type_description="Deliverance from bondage through blood and sea",
        antitype_name="Salvation in Christ",
        antitype_reference="1 Corinthians 10:1-4",
        antitype_description="Deliverance from sin through blood and baptism",
        category=TypeCategory.EVENTUAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Redemption from bondage through blood and water",
    ),
    TypeAntitypePair(
        type_name="Jonah in Fish",
        type_reference="Jonah 1:17",
        type_description="Three days in belly of fish",
        antitype_name="Christ's Burial",
        antitype_reference="Matthew 12:40",
        antitype_description="Three days in heart of the earth",
        category=TypeCategory.EVENTUAL,
        status=FulfillmentStatus.FULFILLED,
        correspondence="Death, burial, resurrection on third day",
    ),
]


# =============================================================================
# TABERNACLE TYPOLOGY (DETAILED)
# =============================================================================

@dataclass
class TabernacleComponent:
    """A component of the Tabernacle with typological significance."""
    
    name: str
    location: str
    description: str
    material: str
    antitype: str
    reference: str
    significance: str


TABERNACLE_COMPONENTS = [
    TabernacleComponent(
        name="Gate",
        location="Outer Court",
        description="Single entrance to the court",
        material="Blue, purple, scarlet, fine linen",
        antitype="Christ the Door",
        reference="John 10:9",
        significance="One way of access to God",
    ),
    TabernacleComponent(
        name="Brazen Altar",
        location="Outer Court",
        description="Place of burnt offerings",
        material="Acacia wood overlaid with brass",
        antitype="Christ's Cross",
        reference="Hebrews 13:10",
        significance="Place of substitutionary sacrifice",
    ),
    TabernacleComponent(
        name="Brazen Laver",
        location="Outer Court",
        description="Basin for priestly washing",
        material="Brass mirrors of serving women",
        antitype="Word of God / Baptism",
        reference="Ephesians 5:26",
        significance="Cleansing by the washing of water by the Word",
    ),
    TabernacleComponent(
        name="Table of Shewbread",
        location="Holy Place",
        description="Twelve loaves displayed continually",
        material="Acacia wood overlaid with gold",
        antitype="Christ the Bread of Life",
        reference="John 6:35",
        significance="Sustaining fellowship with God",
    ),
    TabernacleComponent(
        name="Golden Candlestick",
        location="Holy Place",
        description="Seven-branched lampstand",
        material="Pure beaten gold",
        antitype="Christ the Light of the World",
        reference="John 8:12",
        significance="Illumination in the darkness",
    ),
    TabernacleComponent(
        name="Altar of Incense",
        location="Holy Place",
        description="Altar for burning incense",
        material="Acacia wood overlaid with gold",
        antitype="Christ's Intercession",
        reference="Hebrews 7:25; Revelation 8:3-4",
        significance="Prayers ascending to God through Christ",
    ),
    TabernacleComponent(
        name="Veil",
        location="Between Holy and Most Holy",
        description="Curtain separating the two rooms",
        material="Blue, purple, scarlet, fine linen with cherubim",
        antitype="Christ's Flesh",
        reference="Hebrews 10:20",
        significance="Access to God through Christ's body",
    ),
    TabernacleComponent(
        name="Ark of the Covenant",
        location="Most Holy Place",
        description="Gold-covered chest containing law",
        material="Acacia wood overlaid with gold",
        antitype="Christ",
        reference="Hebrews 9:4",
        significance="God's presence and covenant faithfulness",
    ),
    TabernacleComponent(
        name="Mercy Seat",
        location="Most Holy Place (on Ark)",
        description="Gold lid with cherubim",
        material="Pure gold",
        antitype="Christ our Propitiation",
        reference="Romans 3:25",
        significance="Place where God meets man through blood",
    ),
]


# =============================================================================
# TYPOLOGY SYSTEM
# =============================================================================

@dataclass
class TypologySystem:
    """
    System for managing biblical typology.
    """
    
    pairs: List[TypeAntitypePair] = field(default_factory=lambda: TYPOLOGICAL_PAIRS.copy())
    tabernacle: List[TabernacleComponent] = field(default_factory=lambda: TABERNACLE_COMPONENTS.copy())
    
    def get_by_category(self, category: TypeCategory) -> List[TypeAntitypePair]:
        """Get pairs by category."""
        return [p for p in self.pairs if p.category == category]
    
    def get_by_status(self, status: FulfillmentStatus) -> List[TypeAntitypePair]:
        """Get pairs by fulfillment status."""
        return [p for p in self.pairs if p.status == status]
    
    def get_christological(self) -> List[TypeAntitypePair]:
        """Get all pairs where antitype is Christ."""
        return [p for p in self.pairs if "Christ" in p.antitype_name]
    
    def lookup_type(self, name: str) -> Optional[TypeAntitypePair]:
        """Look up a type by name."""
        for p in self.pairs:
            if p.type_name.lower() == name.lower():
                return p
        return None
    
    def get_tabernacle_component(self, name: str) -> Optional[TabernacleComponent]:
        """Get a tabernacle component by name."""
        for c in self.tabernacle:
            if c.name.lower() == name.lower():
                return c
        return None
    
    def get_pointer_diagram(self) -> List[str]:
        """Get all type→antitype pointers."""
        return [p.pointer_notation for p in self.pairs]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "total_pairs": len(self.pairs),
            "by_category": {
                cat.name: len(self.get_by_category(cat))
                for cat in TypeCategory
            },
            "by_status": {
                stat.name: len(self.get_by_status(stat))
                for stat in FulfillmentStatus
            },
            "christological_count": len(self.get_christological()),
            "tabernacle_components": len(self.tabernacle),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_typology() -> bool:
    """Validate the typology module."""
    
    # Test TypeCategory
    assert TypeCategory.PERSONAL.category == "person"
    
    # Test FulfillmentStatus
    assert FulfillmentStatus.FULFILLED.mode == "complete"
    
    # Test TypeAntitypePair
    adam_pair = TYPOLOGICAL_PAIRS[0]
    assert adam_pair.type_name == "Adam"
    assert "Christ" in adam_pair.antitype_name
    assert adam_pair.pointer_notation == "Adam → Christ (Last Adam)"
    
    # Test TabernacleComponent
    gate = TABERNACLE_COMPONENTS[0]
    assert gate.name == "Gate"
    assert "Door" in gate.antitype
    
    # Test TypologySystem
    system = TypologySystem()
    
    personal = system.get_by_category(TypeCategory.PERSONAL)
    assert len(personal) > 0
    
    fulfilled = system.get_by_status(FulfillmentStatus.FULFILLED)
    assert len(fulfilled) > 0
    
    christological = system.get_christological()
    assert len(christological) > 10
    
    adam = system.lookup_type("Adam")
    assert adam is not None
    
    altar = system.get_tabernacle_component("Brazen Altar")
    assert altar is not None
    assert "Cross" in altar.antitype
    
    pointers = system.get_pointer_diagram()
    assert len(pointers) == len(TYPOLOGICAL_PAIRS)
    
    summary = system.get_summary()
    assert "total_pairs" in summary
    assert "by_category" in summary
    
    return True


if __name__ == "__main__":
    print("Validating Typology Module...")
    assert validate_typology()
    print("✓ Typology module validated")
    
    # Demo
    print("\n--- Typology System Demo ---")
    
    system = TypologySystem()
    
    print("\nType → Antitype Mappings (Sample):")
    for pair in system.pairs[:6]:
        print(f"  {pair.pointer_notation}")
        print(f"    {pair.correspondence}")
    
    print("\nTypology by Category:")
    for cat in TypeCategory:
        count = len(system.get_by_category(cat))
        print(f"  {cat.name}: {count} pairs")
    
    print("\nTabernacle Typology (Sample):")
    for comp in system.tabernacle[:5]:
        print(f"  {comp.name} → {comp.antitype}")
        print(f"    \"{comp.significance}\"")
    
    print(f"\nChristological Types: {len(system.get_christological())}")

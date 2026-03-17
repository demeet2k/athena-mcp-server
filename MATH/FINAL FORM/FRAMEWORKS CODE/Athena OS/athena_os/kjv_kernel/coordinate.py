"""
ATHENA OS - KJV BIBLE COMPUTATIONAL FRAMEWORK
==============================================
Part II: The Coordinate System (B:C:V Navigation)

THE TRANSITION FROM LINEAR TO VOLUMETRIC:
    The KJV implements a RANDOM ACCESS structure, transforming
    the text from a 1D string into a 3D DISCRETE METRIC SPACE.

THE COORDINATE VECTOR:
    L⃗ = (B, C, V)
    
    Where:
    - B = Book (Module ID) ∈ {1..66}
    - C = Chapter (Block ID) ∈ {1..N_chapters}
    - V = Verse (Atomic Unit ID) ∈ {1..N_verses}

ACCESS COMPLEXITY:
    - Scroll (Linear): O(n) traversal
    - KJV (Random Access): O(1) instantaneous retrieval

THE CENTER POINT:
    Psalm 118:8 is the exact geometric center of the KJV.
    "It is better to trust in the LORD than to put confidence in man."
    
    This is the "Trust" axiom - the fulcrum of the entire system.

SOURCES:
    KJV BIBLE THE AUTHORIZED KERNEL (KJV-1611)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np


# =============================================================================
# BOOK CONSTANTS
# =============================================================================

class Testament(Enum):
    """Testament partition."""
    
    OLD = ("OT", 39, "Law/History/Poetry/Prophecy")
    NEW = ("NT", 27, "Gospel/Epistles/Prophecy")
    
    def __init__(self, code: str, book_count: int, genres: str):
        self.code = code
        self.book_count = book_count
        self.genres = genres


class Genre(Enum):
    """Book genre classification."""
    
    LAW = ("Torah", "Pentateuch", 5)
    HISTORY = ("Historical", "Chronicles", 12)
    POETRY = ("Wisdom", "Poetic", 5)
    MAJOR_PROPHETS = ("Major", "Long Form", 5)
    MINOR_PROPHETS = ("Minor", "Short Form", 12)
    GOSPELS = ("Gospel", "Life of Christ", 4)
    ACTS = ("History", "Church History", 1)
    PAULINE = ("Epistle", "Paul's Letters", 13)
    GENERAL = ("Epistle", "General Letters", 8)
    APOCALYPTIC = ("Prophecy", "End Times", 1)
    
    def __init__(self, category: str, description: str, count: int):
        self.category = category
        self._description = description
        self.count = count


# =============================================================================
# BOOK DATABASE
# =============================================================================

@dataclass
class BookSpec:
    """Specification for a Bible book."""
    
    # Identity
    index: int  # 1-66
    name: str
    abbreviation: str
    
    # Classification
    testament: Testament
    genre: Genre
    
    # Dimensions
    chapters: int
    verses: int  # Total verses in book
    
    # Word count (approximate KJV)
    word_count: int = 0
    
    @property
    def id(self) -> str:
        """Book ID."""
        return f"B{self.index:02d}"


# The 66-Book Canon
BOOK_DATABASE = [
    # Old Testament - Law (1-5)
    BookSpec(1, "Genesis", "Gen", Testament.OLD, Genre.LAW, 50, 1533, 38267),
    BookSpec(2, "Exodus", "Exod", Testament.OLD, Genre.LAW, 40, 1213, 32692),
    BookSpec(3, "Leviticus", "Lev", Testament.OLD, Genre.LAW, 27, 859, 24546),
    BookSpec(4, "Numbers", "Num", Testament.OLD, Genre.LAW, 36, 1288, 32902),
    BookSpec(5, "Deuteronomy", "Deut", Testament.OLD, Genre.LAW, 34, 959, 28461),
    
    # Old Testament - History (6-17)
    BookSpec(6, "Joshua", "Josh", Testament.OLD, Genre.HISTORY, 24, 658, 18858),
    BookSpec(7, "Judges", "Judg", Testament.OLD, Genre.HISTORY, 21, 618, 18976),
    BookSpec(8, "Ruth", "Ruth", Testament.OLD, Genre.HISTORY, 4, 85, 2578),
    BookSpec(9, "1 Samuel", "1Sam", Testament.OLD, Genre.HISTORY, 31, 810, 25061),
    BookSpec(10, "2 Samuel", "2Sam", Testament.OLD, Genre.HISTORY, 24, 695, 20612),
    BookSpec(11, "1 Kings", "1Kgs", Testament.OLD, Genre.HISTORY, 22, 816, 24524),
    BookSpec(12, "2 Kings", "2Kgs", Testament.OLD, Genre.HISTORY, 25, 719, 23532),
    BookSpec(13, "1 Chronicles", "1Chr", Testament.OLD, Genre.HISTORY, 29, 942, 20369),
    BookSpec(14, "2 Chronicles", "2Chr", Testament.OLD, Genre.HISTORY, 36, 822, 26074),
    BookSpec(15, "Ezra", "Ezra", Testament.OLD, Genre.HISTORY, 10, 280, 7441),
    BookSpec(16, "Nehemiah", "Neh", Testament.OLD, Genre.HISTORY, 13, 406, 10483),
    BookSpec(17, "Esther", "Esth", Testament.OLD, Genre.HISTORY, 10, 167, 5637),
    
    # Old Testament - Poetry (18-22)
    BookSpec(18, "Job", "Job", Testament.OLD, Genre.POETRY, 42, 1070, 18098),
    BookSpec(19, "Psalms", "Ps", Testament.OLD, Genre.POETRY, 150, 2461, 43743),
    BookSpec(20, "Proverbs", "Prov", Testament.OLD, Genre.POETRY, 31, 915, 15043),
    BookSpec(21, "Ecclesiastes", "Eccl", Testament.OLD, Genre.POETRY, 12, 222, 5584),
    BookSpec(22, "Song of Solomon", "Song", Testament.OLD, Genre.POETRY, 8, 117, 2661),
    
    # Old Testament - Major Prophets (23-27)
    BookSpec(23, "Isaiah", "Isa", Testament.OLD, Genre.MAJOR_PROPHETS, 66, 1292, 37044),
    BookSpec(24, "Jeremiah", "Jer", Testament.OLD, Genre.MAJOR_PROPHETS, 52, 1364, 42659),
    BookSpec(25, "Lamentations", "Lam", Testament.OLD, Genre.MAJOR_PROPHETS, 5, 154, 3415),
    BookSpec(26, "Ezekiel", "Ezek", Testament.OLD, Genre.MAJOR_PROPHETS, 48, 1273, 39407),
    BookSpec(27, "Daniel", "Dan", Testament.OLD, Genre.MAJOR_PROPHETS, 12, 357, 11606),
    
    # Old Testament - Minor Prophets (28-39)
    BookSpec(28, "Hosea", "Hos", Testament.OLD, Genre.MINOR_PROPHETS, 14, 197, 5175),
    BookSpec(29, "Joel", "Joel", Testament.OLD, Genre.MINOR_PROPHETS, 3, 73, 2034),
    BookSpec(30, "Amos", "Amos", Testament.OLD, Genre.MINOR_PROPHETS, 9, 146, 4217),
    BookSpec(31, "Obadiah", "Obad", Testament.OLD, Genre.MINOR_PROPHETS, 1, 21, 670),
    BookSpec(32, "Jonah", "Jonah", Testament.OLD, Genre.MINOR_PROPHETS, 4, 48, 1321),
    BookSpec(33, "Micah", "Mic", Testament.OLD, Genre.MINOR_PROPHETS, 7, 105, 3153),
    BookSpec(34, "Nahum", "Nah", Testament.OLD, Genre.MINOR_PROPHETS, 3, 47, 1285),
    BookSpec(35, "Habakkuk", "Hab", Testament.OLD, Genre.MINOR_PROPHETS, 3, 56, 1476),
    BookSpec(36, "Zephaniah", "Zeph", Testament.OLD, Genre.MINOR_PROPHETS, 3, 53, 1617),
    BookSpec(37, "Haggai", "Hag", Testament.OLD, Genre.MINOR_PROPHETS, 2, 38, 1131),
    BookSpec(38, "Zechariah", "Zech", Testament.OLD, Genre.MINOR_PROPHETS, 14, 211, 6444),
    BookSpec(39, "Malachi", "Mal", Testament.OLD, Genre.MINOR_PROPHETS, 4, 55, 1782),
    
    # New Testament - Gospels (40-43)
    BookSpec(40, "Matthew", "Matt", Testament.NEW, Genre.GOSPELS, 28, 1071, 23684),
    BookSpec(41, "Mark", "Mark", Testament.NEW, Genre.GOSPELS, 16, 678, 15171),
    BookSpec(42, "Luke", "Luke", Testament.NEW, Genre.GOSPELS, 24, 1151, 25944),
    BookSpec(43, "John", "John", Testament.NEW, Genre.GOSPELS, 21, 879, 19099),
    
    # New Testament - Acts (44)
    BookSpec(44, "Acts", "Acts", Testament.NEW, Genre.ACTS, 28, 1007, 24250),
    
    # New Testament - Pauline Epistles (45-57)
    BookSpec(45, "Romans", "Rom", Testament.NEW, Genre.PAULINE, 16, 433, 9447),
    BookSpec(46, "1 Corinthians", "1Cor", Testament.NEW, Genre.PAULINE, 16, 437, 9489),
    BookSpec(47, "2 Corinthians", "2Cor", Testament.NEW, Genre.PAULINE, 13, 257, 6092),
    BookSpec(48, "Galatians", "Gal", Testament.NEW, Genre.PAULINE, 6, 149, 3098),
    BookSpec(49, "Ephesians", "Eph", Testament.NEW, Genre.PAULINE, 6, 155, 3039),
    BookSpec(50, "Philippians", "Phil", Testament.NEW, Genre.PAULINE, 4, 104, 2002),
    BookSpec(51, "Colossians", "Col", Testament.NEW, Genre.PAULINE, 4, 95, 1998),
    BookSpec(52, "1 Thessalonians", "1Thess", Testament.NEW, Genre.PAULINE, 5, 89, 1857),
    BookSpec(53, "2 Thessalonians", "2Thess", Testament.NEW, Genre.PAULINE, 3, 47, 1042),
    BookSpec(54, "1 Timothy", "1Tim", Testament.NEW, Genre.PAULINE, 6, 113, 2269),
    BookSpec(55, "2 Timothy", "2Tim", Testament.NEW, Genre.PAULINE, 4, 83, 1703),
    BookSpec(56, "Titus", "Titus", Testament.NEW, Genre.PAULINE, 3, 46, 921),
    BookSpec(57, "Philemon", "Phlm", Testament.NEW, Genre.PAULINE, 1, 25, 445),
    
    # New Testament - General Epistles (58-65)
    BookSpec(58, "Hebrews", "Heb", Testament.NEW, Genre.GENERAL, 13, 303, 6913),
    BookSpec(59, "James", "Jas", Testament.NEW, Genre.GENERAL, 5, 108, 2309),
    BookSpec(60, "1 Peter", "1Pet", Testament.NEW, Genre.GENERAL, 5, 105, 2482),
    BookSpec(61, "2 Peter", "2Pet", Testament.NEW, Genre.GENERAL, 3, 61, 1559),
    BookSpec(62, "1 John", "1John", Testament.NEW, Genre.GENERAL, 5, 105, 2523),
    BookSpec(63, "2 John", "2John", Testament.NEW, Genre.GENERAL, 1, 13, 303),
    BookSpec(64, "3 John", "3John", Testament.NEW, Genre.GENERAL, 1, 14, 299),
    BookSpec(65, "Jude", "Jude", Testament.NEW, Genre.GENERAL, 1, 25, 613),
    
    # New Testament - Apocalyptic (66)
    BookSpec(66, "Revelation", "Rev", Testament.NEW, Genre.APOCALYPTIC, 22, 404, 12000),
]


# =============================================================================
# COORDINATE SYSTEM
# =============================================================================

@dataclass
class Coordinate:
    """
    A coordinate in the B:C:V space.
    
    L⃗ = (B, C, V)
    """
    
    book: int      # B ∈ {1..66}
    chapter: int   # C ∈ {1..N}
    verse: int     # V ∈ {1..N}
    
    def __post_init__(self):
        """Validate coordinate bounds."""
        if not (1 <= self.book <= 66):
            raise ValueError(f"Book must be 1-66, got {self.book}")
    
    @property
    def vector(self) -> Tuple[int, int, int]:
        """Return as vector tuple."""
        return (self.book, self.chapter, self.verse)
    
    @classmethod
    def from_string(cls, ref: str) -> "Coordinate":
        """
        Parse a reference string like "Gen 1:1" or "John 3:16".
        """
        # Simple parser (would need expansion for full support)
        parts = ref.replace(":", " ").split()
        if len(parts) < 3:
            raise ValueError(f"Invalid reference: {ref}")
        
        book_abbr = parts[0]
        chapter = int(parts[1])
        verse = int(parts[-1])
        
        # Find book by abbreviation
        for book in BOOK_DATABASE:
            if book.abbreviation.lower() == book_abbr.lower():
                return cls(book.index, chapter, verse)
        
        raise ValueError(f"Unknown book: {book_abbr}")
    
    def to_string(self) -> str:
        """Convert to reference string."""
        book = BOOK_DATABASE[self.book - 1]
        return f"{book.name} {self.chapter}:{self.verse}"
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"Coordinate({self.book}, {self.chapter}, {self.verse})"


# =============================================================================
# THE CENTER POINT
# =============================================================================

# Psalm 118:8 - The exact geometric center
CENTER_COORDINATE = Coordinate(19, 118, 8)  # Psalms is book 19
CENTER_TEXT = "It is better to trust in the LORD than to put confidence in man."

# Center point analysis
CENTER_ANALYSIS = {
    "coordinate": CENTER_COORDINATE,
    "text": CENTER_TEXT,
    "total_chapters": 1189,
    "median_chapter": 595,  # (1189 + 1) / 2
    "chapter_at_median": "Psalm 118",
    "chapters_before": 594,  # Genesis 1 through Psalm 117
    "chapters_after": 594,   # Psalm 119 through Revelation 22
    "left_vector_range": "Genesis 1 → Psalm 117",
    "right_vector_range": "Psalm 119 → Revelation 22",
    "address_symbolism": {
        "118": "Cornerstone (Psalm 118:22)",
        "8": "New Beginnings / Transcendence (8th day resurrection)",
    },
    "flanking_chapters": {
        "psalm_117": {"description": "Shortest chapter in Bible", "verses": 2},
        "psalm_119": {"description": "Longest chapter in Bible", "verses": 176},
    },
}


# =============================================================================
# NAVIGATION SYSTEM
# =============================================================================

@dataclass
class NavigationSystem:
    """
    Random-access navigation system for the KJV.
    
    Implements O(1) retrieval via coordinate indexing.
    """
    
    books: List[BookSpec] = field(default_factory=lambda: BOOK_DATABASE.copy())
    
    # Chapter-to-global mapping (cumulative chapters)
    chapter_offsets: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        """Build chapter offset table."""
        if not self.chapter_offsets:
            offset = 0
            self.chapter_offsets = [0]
            for book in self.books:
                offset += book.chapters
                self.chapter_offsets.append(offset)
    
    @property
    def total_books(self) -> int:
        return len(self.books)
    
    @property
    def total_chapters(self) -> int:
        return self.chapter_offsets[-1]
    
    @property
    def total_verses(self) -> int:
        return sum(book.verses for book in self.books)
    
    def get_book(self, index: int) -> Optional[BookSpec]:
        """Get book by index (1-66)."""
        if 1 <= index <= len(self.books):
            return self.books[index - 1]
        return None
    
    def get_book_by_name(self, name: str) -> Optional[BookSpec]:
        """Get book by name or abbreviation."""
        name_lower = name.lower()
        for book in self.books:
            if book.name.lower() == name_lower or \
               book.abbreviation.lower() == name_lower:
                return book
        return None
    
    def global_chapter_index(self, coord: Coordinate) -> int:
        """
        Convert coordinate to global chapter index (1-1189).
        """
        if coord.book < 1 or coord.book > len(self.books):
            return -1
        return self.chapter_offsets[coord.book - 1] + coord.chapter
    
    def coordinate_from_global_chapter(self, global_idx: int) -> Optional[Coordinate]:
        """
        Convert global chapter index to coordinate.
        """
        if global_idx < 1 or global_idx > self.total_chapters:
            return None
        
        # Binary search for book
        for i, offset in enumerate(self.chapter_offsets[:-1]):
            if offset < global_idx <= self.chapter_offsets[i + 1]:
                book_idx = i + 1
                chapter = global_idx - offset
                return Coordinate(book_idx, chapter, 1)
        
        return None
    
    def get_center_point(self) -> Dict[str, Any]:
        """Get the center point analysis."""
        return CENTER_ANALYSIS.copy()
    
    def distance(self, c1: Coordinate, c2: Coordinate) -> Dict[str, int]:
        """
        Calculate distance between two coordinates.
        """
        book_dist = abs(c2.book - c1.book)
        
        # Global chapter distance
        gc1 = self.global_chapter_index(c1)
        gc2 = self.global_chapter_index(c2)
        chapter_dist = abs(gc2 - gc1)
        
        return {
            "book_distance": book_dist,
            "chapter_distance": chapter_dist,
            "from": c1.to_string(),
            "to": c2.to_string(),
        }
    
    def verify_symmetry(self) -> Dict[str, Any]:
        """
        Verify the center-point symmetry of the KJV.
        """
        total = self.total_chapters
        median_idx = (total + 1) // 2  # 595
        
        center = self.coordinate_from_global_chapter(median_idx)
        
        left_count = median_idx - 1  # Chapters before
        right_count = total - median_idx  # Chapters after
        
        return {
            "total_chapters": total,
            "median_index": median_idx,
            "center_coordinate": center.to_string() if center else None,
            "chapters_before_center": left_count,
            "chapters_after_center": right_count,
            "is_symmetric": left_count == right_count,
            "expected_center": "Psalm 118",
        }
    
    def get_partition_stats(self) -> Dict[str, Any]:
        """
        Get statistics by partition (OT/NT).
        """
        ot_books = [b for b in self.books if b.testament == Testament.OLD]
        nt_books = [b for b in self.books if b.testament == Testament.NEW]
        
        return {
            "old_testament": {
                "books": len(ot_books),
                "chapters": sum(b.chapters for b in ot_books),
                "verses": sum(b.verses for b in ot_books),
                "words": sum(b.word_count for b in ot_books),
            },
            "new_testament": {
                "books": len(nt_books),
                "chapters": sum(b.chapters for b in nt_books),
                "verses": sum(b.verses for b in nt_books),
                "words": sum(b.word_count for b in nt_books),
            },
            "partition_ratio": {
                "books": f"{len(ot_books)}/{len(nt_books)}",
                "expected": "39/27",
            },
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_coordinate() -> bool:
    """Validate the coordinate module."""
    
    # Test book database
    assert len(BOOK_DATABASE) == 66
    assert BOOK_DATABASE[0].name == "Genesis"
    assert BOOK_DATABASE[65].name == "Revelation"
    
    # Verify partition counts
    ot_count = len([b for b in BOOK_DATABASE if b.testament == Testament.OLD])
    nt_count = len([b for b in BOOK_DATABASE if b.testament == Testament.NEW])
    assert ot_count == 39
    assert nt_count == 27
    
    # Test Coordinate
    coord = Coordinate(1, 1, 1)
    assert coord.vector == (1, 1, 1)
    assert "Genesis" in coord.to_string()
    
    # Test center point
    center = CENTER_COORDINATE
    assert center.book == 19  # Psalms
    assert center.chapter == 118
    assert center.verse == 8
    
    # Test NavigationSystem
    nav = NavigationSystem()
    assert nav.total_books == 66
    assert nav.total_chapters == 1189
    
    # Verify center point calculation
    global_idx = nav.global_chapter_index(Coordinate(19, 118, 1))
    assert global_idx == 595  # The median
    
    # Verify symmetry
    symmetry = nav.verify_symmetry()
    assert symmetry["is_symmetric"]
    assert symmetry["chapters_before_center"] == 594
    assert symmetry["chapters_after_center"] == 594
    
    # Test partition stats
    stats = nav.get_partition_stats()
    assert stats["old_testament"]["books"] == 39
    assert stats["new_testament"]["books"] == 27
    
    return True


if __name__ == "__main__":
    print("Validating Coordinate Module...")
    assert validate_coordinate()
    print("✓ Coordinate module validated")
    
    # Demo
    print("\n--- Coordinate System Demo ---")
    
    nav = NavigationSystem()
    
    print(f"\nKJV Dimensions:")
    print(f"  Books: {nav.total_books}")
    print(f"  Chapters: {nav.total_chapters}")
    print(f"  Verses: {nav.total_verses:,}")
    
    print(f"\nCenter Point Analysis:")
    center = nav.get_center_point()
    print(f"  Coordinate: {center['coordinate'].to_string()}")
    print(f"  Text: \"{center['text']}\"")
    print(f"  Chapters before: {center['chapters_before']}")
    print(f"  Chapters after: {center['chapters_after']}")
    
    print(f"\nPartition Statistics:")
    stats = nav.get_partition_stats()
    print(f"  OT: {stats['old_testament']['books']} books, {stats['old_testament']['chapters']} chapters")
    print(f"  NT: {stats['new_testament']['books']} books, {stats['new_testament']['chapters']} chapters")
    print(f"  Ratio: {stats['partition_ratio']['books']} (expected {stats['partition_ratio']['expected']})")
    
    print(f"\nSymmetry Verification:")
    sym = nav.verify_symmetry()
    print(f"  Center: {sym['center_coordinate']}")
    print(f"  Symmetric: {sym['is_symmetric']}")

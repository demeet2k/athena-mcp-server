"""
ATHENA OS - CELTIC OGHAM KERNEL: OGHAM MODULE
==============================================
Multi-Modal Feature Vector System and Semantic Compression

THE OGHAM CIPHER:
    The Druidic prohibition against written doctrine was not a rejection
    of record-keeping, but a reliance on a Holographic Mnemonic Index.
    
FEATURE VECTOR DEFINITION:
    An Ogham "Letter" (e.g., ᚁ Beith) is not a phonetic character,
    but a Key in a Key-Value store pointing to a multidimensional
    feature vector:
    
    V_Beith = [
        Phoneme: B,
        Tree: Birch,
        Color: White,
        Bird: Pheasant,
        Element: Earth,
        Concept: New Beginnings
    ]

THE BRÍATHAROGAM (Word-Ogham):
    Kennings associated with letters act as Pointer References.
    
COMPRESSION EFFICIENCY:
    Complex ecological and metaphysical data streams transmitted
    using low-bandwidth channel (notches on stick/stone).
    A single Ogham string encodes an entire encyclopedic entry.

THE BASE-20 MATRIX (The Aicme):
    4 × 5 Matrix (4 Aicme of 5 letters)
    
    Topology: Script written along central flesc (stem-line)
    - Right: Positive Vector (+x)
    - Left: Negative Vector (-x)
    - Across: Orthogonal Vector (z)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np
import hashlib


# =============================================================================
# OGHAM FEATURE VECTORS
# =============================================================================

@dataclass
class OghamFeatureVector:
    """
    Multi-dimensional feature vector for an Ogham character.
    
    Each glyph serves as an index key for retrieving massive,
    disparate datasets (botanical, meteorological, chromatic).
    """
    
    # Core identity
    glyph: str                      # Unicode glyph (e.g., ᚁ)
    name: str                       # Name (e.g., Beith)
    phoneme: str                    # Sound value
    
    # Positional encoding
    aicme: int                      # Group (1-4)
    stroke_count: int               # Strokes (1-5)
    
    # Multi-modal features
    tree: str                       # Associated tree
    color: str                      # Associated color
    bird: str                       # Associated bird
    element: str                    # Associated element
    concept: str                    # Core meaning
    
    # Extended metadata
    month: Optional[str] = None     # Calendar month
    direction: Optional[str] = None # Associated direction
    metal: Optional[str] = None     # Associated metal
    
    def get_binary_hash(self) -> str:
        """Get 7-bit binary encoding: 2 bits group + 3 bits stroke."""
        group_bits = format(self.aicme, '02b')
        stroke_bits = format(self.stroke_count, '03b')
        return group_bits + ' ' + stroke_bits
    
    def get_position_tuple(self) -> Tuple[int, int]:
        """Get (Group, Stroke) position tuple."""
        return (self.aicme, self.stroke_count)
    
    def to_semantic_array(self) -> np.ndarray:
        """
        Convert to semantic feature array.
        
        Creates a numerical embedding of the multi-modal features.
        """
        # Create simple hash-based embeddings for each feature
        features = [
            self.tree, self.color, self.bird, 
            self.element, self.concept
        ]
        
        embeddings = []
        for f in features:
            h = int(hashlib.md5(f.encode()).hexdigest()[:8], 16)
            embeddings.append(h / (16**8))  # Normalize to 0-1
        
        return np.array(embeddings)
    
    def get_full_record(self) -> Dict[str, Any]:
        """Get complete encyclopedic record."""
        return {
            "glyph": self.glyph,
            "name": self.name,
            "phoneme": self.phoneme,
            "position": self.get_position_tuple(),
            "binary": self.get_binary_hash(),
            "botanical": self.tree,
            "chromatic": self.color,
            "zoological": self.bird,
            "elemental": self.element,
            "conceptual": self.concept,
            "temporal": self.month,
            "directional": self.direction
        }


# =============================================================================
# OGHAM DATABASE
# =============================================================================

# The Four Aicme (Groups) of Five Letters Each
OGHAM_DATABASE = {
    # AICME B (Group 1) - Right of stem
    "beith": OghamFeatureVector(
        glyph="ᚁ", name="Beith", phoneme="B",
        aicme=1, stroke_count=1,
        tree="Birch", color="White", bird="Pheasant",
        element="Earth", concept="New Beginnings",
        month="Nov-Dec", direction="East"
    ),
    "luis": OghamFeatureVector(
        glyph="ᚂ", name="Luis", phoneme="L",
        aicme=1, stroke_count=2,
        tree="Rowan", color="Grey", bird="Duck",
        element="Fire", concept="Protection",
        month="Dec-Jan", direction="Northeast"
    ),
    "fearn": OghamFeatureVector(
        glyph="ᚃ", name="Fearn", phoneme="F/V",
        aicme=1, stroke_count=3,
        tree="Alder", color="Crimson", bird="Gull",
        element="Water", concept="Shield/Foundation",
        month="Jan-Feb", direction="North"
    ),
    "saille": OghamFeatureVector(
        glyph="ᚄ", name="Saille", phoneme="S",
        aicme=1, stroke_count=4,
        tree="Willow", color="Silver", bird="Hawk",
        element="Water", concept="Intuition/Flexibility",
        month="Feb-Mar", direction="Northwest"
    ),
    "nion": OghamFeatureVector(
        glyph="ᚅ", name="Nion", phoneme="N",
        aicme=1, stroke_count=5,
        tree="Ash", color="Green", bird="Snipe",
        element="Air", concept="Connection/World Tree",
        month="Mar-Apr", direction="West"
    ),
    
    # AICME H (Group 2) - Left of stem
    "huath": OghamFeatureVector(
        glyph="ᚆ", name="Huath", phoneme="H",
        aicme=2, stroke_count=1,
        tree="Hawthorn", color="Purple", bird="Crow",
        element="Fire", concept="Cleansing/Fear",
        month="Apr-May"
    ),
    "duir": OghamFeatureVector(
        glyph="ᚇ", name="Duir", phoneme="D",
        aicme=2, stroke_count=2,
        tree="Oak", color="Black", bird="Wren",
        element="Earth", concept="Strength/Doorway",
        month="May-Jun"
    ),
    "tinne": OghamFeatureVector(
        glyph="ᚈ", name="Tinne", phoneme="T",
        aicme=2, stroke_count=3,
        tree="Holly", color="Dark Grey", bird="Starling",
        element="Fire", concept="Justice/Balance",
        month="Jun-Jul"
    ),
    "coll": OghamFeatureVector(
        glyph="ᚉ", name="Coll", phoneme="C/K",
        aicme=2, stroke_count=4,
        tree="Hazel", color="Brown", bird="Crane",
        element="Air", concept="Wisdom/Inspiration",
        month="Jul-Aug"
    ),
    "quert": OghamFeatureVector(
        glyph="ᚊ", name="Quert", phoneme="Q",
        aicme=2, stroke_count=5,
        tree="Apple", color="Green", bird="Hen",
        element="Water", concept="Beauty/Choice",
        month="Aug-Sep"
    ),
    
    # AICME M (Group 3) - Across stem
    "muin": OghamFeatureVector(
        glyph="ᚋ", name="Muin", phoneme="M",
        aicme=3, stroke_count=1,
        tree="Vine", color="Variegated", bird="Titmouse",
        element="Water", concept="Prophecy/Release",
        month="Sep-Oct"
    ),
    "gort": OghamFeatureVector(
        glyph="ᚌ", name="Gort", phoneme="G",
        aicme=3, stroke_count=2,
        tree="Ivy", color="Blue", bird="Swan",
        element="Earth", concept="Persistence/Growth",
        month="Oct-Nov"
    ),
    "ngetal": OghamFeatureVector(
        glyph="ᚍ", name="Ngetal", phoneme="NG",
        aicme=3, stroke_count=3,
        tree="Reed", color="Grass-Green", bird="Goose",
        element="Air", concept="Healing/Direct Action",
        month="Nov-Dec"
    ),
    "straif": OghamFeatureVector(
        glyph="ᚎ", name="Straif", phoneme="ST/Z",
        aicme=3, stroke_count=4,
        tree="Blackthorn", color="Bright", bird="Thrush",
        element="Fire", concept="Discipline/Fate",
        month="Intercalary"
    ),
    "ruis": OghamFeatureVector(
        glyph="ᚏ", name="Ruis", phoneme="R",
        aicme=3, stroke_count=5,
        tree="Elder", color="Red", bird="Rook",
        element="Water", concept="Endings/Regeneration",
        month="Year's End"
    ),
    
    # AICME A (Group 4) - Through stem (Vowels)
    "ailm": OghamFeatureVector(
        glyph="ᚐ", name="Ailm", phoneme="A",
        aicme=4, stroke_count=1,
        tree="Fir/Pine", color="Piebald", bird="Lapwing",
        element="Air", concept="Vision/Clarity"
    ),
    "onn": OghamFeatureVector(
        glyph="ᚑ", name="Onn", phoneme="O",
        aicme=4, stroke_count=2,
        tree="Gorse/Furze", color="Gold", bird="Cormorant",
        element="Fire", concept="Gathering/Collection"
    ),
    "ur": OghamFeatureVector(
        glyph="ᚒ", name="Ur", phoneme="U",
        aicme=4, stroke_count=3,
        tree="Heather", color="Russet", bird="Lark",
        element="Earth", concept="Passion/Gateway"
    ),
    "eadhadh": OghamFeatureVector(
        glyph="ᚓ", name="Eadhadh", phoneme="E",
        aicme=4, stroke_count=4,
        tree="Aspen", color="Red", bird="Whistling Swan",
        element="Air", concept="Endurance/Test"
    ),
    "iodhadh": OghamFeatureVector(
        glyph="ᚔ", name="Iodhadh", phoneme="I",
        aicme=4, stroke_count=5,
        tree="Yew", color="Dark Green", bird="Eagle",
        element="Spirit", concept="Death/Rebirth/Immortality"
    ),
}


# =============================================================================
# AICME STRUCTURE
# =============================================================================

class Aicme(Enum):
    """The four Aicme (groups) of Ogham."""
    
    B = 1   # Right of stem (B, L, F, S, N)
    H = 2   # Left of stem (H, D, T, C, Q)
    M = 3   # Across stem (M, G, NG, ST, R)
    A = 4   # Through stem - Vowels (A, O, U, E, I)


@dataclass
class OghamMatrix:
    """
    The 4 × 5 Ogham Matrix (Base-20 system).
    
    Structured as positional notation where meaning
    derives from geometric orientation relative to World Axis.
    """
    
    def __init__(self):
        self.matrix: Dict[Tuple[int, int], OghamFeatureVector] = {}
        self._build_matrix()
    
    def _build_matrix(self) -> None:
        """Build the 4×5 matrix from database."""
        for name, vector in OGHAM_DATABASE.items():
            pos = vector.get_position_tuple()
            self.matrix[pos] = vector
    
    def get_by_position(self, aicme: int, stroke: int) -> Optional[OghamFeatureVector]:
        """Get Ogham by position (Group, Stroke)."""
        return self.matrix.get((aicme, stroke))
    
    def get_by_name(self, name: str) -> Optional[OghamFeatureVector]:
        """Get Ogham by name."""
        return OGHAM_DATABASE.get(name.lower())
    
    def get_aicme(self, group: int) -> List[OghamFeatureVector]:
        """Get all letters in an Aicme."""
        return [v for (g, s), v in self.matrix.items() if g == group]
    
    def encode_text(self, text: str) -> List[OghamFeatureVector]:
        """
        Encode text to Ogham vectors.
        
        Maps phonemes to their Ogham equivalents.
        """
        # Simple phoneme mapping
        phoneme_map = {}
        for name, vector in OGHAM_DATABASE.items():
            for p in vector.phoneme.split('/'):
                phoneme_map[p.lower()] = vector
        
        result = []
        for char in text.upper():
            if char in phoneme_map:
                result.append(phoneme_map[char])
        
        return result
    
    def decode_glyphs(self, glyphs: str) -> List[OghamFeatureVector]:
        """Decode Ogham glyph string to vectors."""
        glyph_map = {v.glyph: v for v in OGHAM_DATABASE.values()}
        return [glyph_map[g] for g in glyphs if g in glyph_map]


# =============================================================================
# SEMANTIC COMPRESSION ENGINE
# =============================================================================

class SemanticCompressionEngine:
    """
    High-density semantic compression using Ogham.
    
    A single string of Ogham encodes an entire encyclopedic entry
    using low-bandwidth channel (notches on stick/stone).
    """
    
    def __init__(self):
        self.matrix = OghamMatrix()
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def compress(self, semantic_data: Dict[str, Any]) -> str:
        """
        Compress semantic data to Ogham string.
        
        Finds best-matching Ogham characters for the data.
        """
        result_glyphs = []
        
        # Match each semantic field
        for field, value in semantic_data.items():
            best_match = self._find_best_match(field, str(value))
            if best_match:
                result_glyphs.append(best_match.glyph)
        
        ogham_string = ''.join(result_glyphs)
        
        # Cache the mapping
        self.cache[ogham_string] = semantic_data
        
        return ogham_string
    
    def decompress(self, ogham_string: str) -> Dict[str, Any]:
        """
        Decompress Ogham string to semantic data.
        
        Returns the full encyclopedic record.
        """
        # Check cache
        if ogham_string in self.cache:
            return self.cache[ogham_string]
        
        # Decode each glyph
        vectors = self.matrix.decode_glyphs(ogham_string)
        
        # Aggregate semantic data
        result = {
            "trees": [],
            "colors": [],
            "birds": [],
            "elements": [],
            "concepts": [],
            "raw_vectors": []
        }
        
        for v in vectors:
            result["trees"].append(v.tree)
            result["colors"].append(v.color)
            result["birds"].append(v.bird)
            result["elements"].append(v.element)
            result["concepts"].append(v.concept)
            result["raw_vectors"].append(v.get_full_record())
        
        return result
    
    def _find_best_match(self, field: str, value: str) -> Optional[OghamFeatureVector]:
        """Find best matching Ogham for a field/value."""
        value_lower = value.lower()
        
        for vector in OGHAM_DATABASE.values():
            # Check direct matches
            if value_lower in vector.tree.lower():
                return vector
            if value_lower in vector.color.lower():
                return vector
            if value_lower in vector.concept.lower():
                return vector
            if value_lower in vector.element.lower():
                return vector
        
        # Default: use first letter
        first_char = value[0].upper() if value else 'A'
        for vector in OGHAM_DATABASE.values():
            if first_char in vector.phoneme:
                return vector
        
        return None
    
    def get_compression_ratio(self, original: Dict, compressed: str) -> float:
        """Calculate compression ratio."""
        original_size = len(str(original))
        compressed_size = len(compressed)
        return original_size / max(1, compressed_size)


# =============================================================================
# OGHAM KEY-VALUE STORE
# =============================================================================

class OghamKeyValueStore:
    """
    Key-Value store using Ogham as keys.
    
    Each Ogham glyph serves as a primary key pointing to
    multidimensional semantic arrays.
    """
    
    def __init__(self):
        self.store: Dict[str, Any] = {}
        
        # Pre-populate with Ogham database
        for name, vector in OGHAM_DATABASE.items():
            self.store[vector.glyph] = vector.get_full_record()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by Ogham key."""
        return self.store.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value for Ogham key."""
        self.store[key] = value
    
    def query_by_tree(self, tree: str) -> List[Dict[str, Any]]:
        """Query all entries by tree type."""
        results = []
        for key, value in self.store.items():
            if isinstance(value, dict) and value.get("botanical", "").lower() == tree.lower():
                results.append(value)
        return results
    
    def query_by_element(self, element: str) -> List[Dict[str, Any]]:
        """Query all entries by element."""
        results = []
        for key, value in self.store.items():
            if isinstance(value, dict) and value.get("elemental", "").lower() == element.lower():
                results.append(value)
        return results
    
    def query_by_concept(self, concept: str) -> List[Dict[str, Any]]:
        """Query entries containing concept."""
        results = []
        concept_lower = concept.lower()
        for key, value in self.store.items():
            if isinstance(value, dict):
                if concept_lower in value.get("conceptual", "").lower():
                    results.append(value)
        return results


# =============================================================================
# FLESC (STEM-LINE) TOPOLOGY
# =============================================================================

class FlescTopology:
    """
    The Flesc (stem-line) topology for Ogham encoding.
    
    Defines vector space relative to central axis:
    - Right: Positive (+x)
    - Left: Negative (-x)
    - Across: Orthogonal (z)
    - Through: Piercing (y)
    """
    
    def __init__(self):
        self.axis = np.array([0, 1, 0])  # Vertical stem
        
    def get_stroke_vector(self, aicme: int, stroke_count: int) -> np.ndarray:
        """Get 3D vector for an Ogham position."""
        if aicme == 1:  # Right (B group)
            direction = np.array([1, 0, 0])
        elif aicme == 2:  # Left (H group)
            direction = np.array([-1, 0, 0])
        elif aicme == 3:  # Across (M group)
            direction = np.array([0, 0, 1])
        else:  # Through (A group - vowels)
            direction = np.array([0.5, 0, 0.5])  # Diagonal
        
        return direction * stroke_count
    
    def encode_position_vector(self, ogham: OghamFeatureVector) -> np.ndarray:
        """Encode Ogham position as 3D vector."""
        return self.get_stroke_vector(ogham.aicme, ogham.stroke_count)
    
    def calculate_similarity(self, v1: OghamFeatureVector, 
                            v2: OghamFeatureVector) -> float:
        """Calculate topological similarity between two Ogham."""
        vec1 = self.encode_position_vector(v1)
        vec2 = self.encode_position_vector(v2)
        
        # Cosine similarity
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot / (norm1 * norm2)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_ogham() -> bool:
    """Validate Ogham module."""
    
    # Test Feature Vector
    beith = OGHAM_DATABASE["beith"]
    assert beith.glyph == "ᚁ"
    assert beith.tree == "Birch"
    assert beith.get_position_tuple() == (1, 1)
    assert "001" in beith.get_binary_hash()
    
    # Test Matrix
    matrix = OghamMatrix()
    duir = matrix.get_by_position(2, 2)
    assert duir is not None
    assert duir.name == "Duir"
    assert duir.tree == "Oak"
    
    # Test Aicme retrieval
    aicme_b = matrix.get_aicme(1)
    assert len(aicme_b) == 5
    
    # Test Compression Engine
    engine = SemanticCompressionEngine()
    data = {"tree": "oak", "concept": "strength"}
    compressed = engine.compress(data)
    assert len(compressed) > 0
    
    decompressed = engine.decompress(compressed)
    assert "trees" in decompressed
    
    # Test Key-Value Store
    kv = OghamKeyValueStore()
    record = kv.get("ᚁ")
    assert record is not None
    assert record["botanical"] == "Birch"
    
    earth_entries = kv.query_by_element("earth")
    assert len(earth_entries) > 0
    
    # Test Flesc Topology
    flesc = FlescTopology()
    vec = flesc.encode_position_vector(beith)
    assert vec[0] > 0  # Right of stem
    
    return True


if __name__ == "__main__":
    print("Validating Ogham Module...")
    assert validate_ogham()
    print("✓ Ogham Module validated")
    
    # Demo
    print("\n--- Ogham Feature Vectors ---")
    for name in ["beith", "duir", "coll", "iodhadh"]:
        v = OGHAM_DATABASE[name]
        print(f"\n{v.glyph} {v.name}:")
        print(f"  Tree: {v.tree}")
        print(f"  Color: {v.color}")
        print(f"  Concept: {v.concept}")
        print(f"  Binary: {v.get_binary_hash()}")
    
    print("\n--- Semantic Compression ---")
    engine = SemanticCompressionEngine()
    data = {"element": "fire", "concept": "protection", "direction": "north"}
    compressed = engine.compress(data)
    print(f"Original: {data}")
    print(f"Compressed: {compressed}")
    print(f"Ratio: {engine.get_compression_ratio(data, compressed):.1f}x")

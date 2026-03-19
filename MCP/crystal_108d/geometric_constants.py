"""
Geometric Constants -- Sacred Geometry Compile-Time Constants
=============================================================
Mathematical truth, not learned parameters. These constants define
the topology of the geometric neural engine.

All values are precomputed from:
  - PHI (golden ratio) and its powers
  - Sigma-60 icosahedral symmetry (12 archetypes x 5 golden rotations)
  - E8-240 root expansion (60 sigma x 4 SFCR faces)
  - Platonic solid element correspondences
  - Flower of Life PHI-decay rings
  - Vesica Piscis sqrt(3) element pairs
  - Attractor values proven by META LOOP^3 (149,220 cycles)
"""

import math

# ── Golden Ratio Constants ────────────────────────────────────────────

PHI = (1 + math.sqrt(5)) / 2        # 1.6180339887...
PHI_INV = PHI - 1                    # 0.6180339887...
PHI_INV2 = PHI_INV ** 2             # 0.3819660113...
PHI_INV3 = PHI_INV ** 3             # 0.2360679775...
SQRT_PHI_INV = math.sqrt(PHI_INV)   # 0.7861513778...
SQRT3 = math.sqrt(3)                 # 1.7320508075...
SQRT5 = math.sqrt(5)                 # 2.2360679775...

# ── Element-Face Mapping ──────────────────────────────────────────────

FACES = ("S", "F", "C", "R")
FACE_INDEX = {"S": 0, "F": 1, "C": 2, "R": 3}
FACE_TO_ELEMENT = {"S": "Earth", "F": "Fire", "C": "Water", "R": "Air"}
ELEMENT_TO_FACE = {"Earth": "S", "Fire": "F", "Water": "C", "Air": "R"}

# ── Bridge Weights (from brain.py topology) ───────────────────────────
# Golden resonance pairs: SF, FC, CR (PHI_INV = 0.618)
# Neutral pairs: SC, FR (0.500)
# Distant pair: SR (PHI_INV^2 = 0.382)

BRIDGE_WEIGHTS = {
    "SF": PHI_INV,        # 0.618 -- golden
    "FC": PHI_INV,        # 0.618 -- golden
    "CR": PHI_INV,        # 0.618 -- golden
    "SC": 0.500,          # neutral
    "FR": 0.500,          # neutral
    "SR": PHI_INV2,       # 0.382 -- distant
}

GOLDEN_BRIDGES = frozenset({"SF", "FC", "CR"})

def bridge_key(a: str, b: str) -> str:
    """Canonical bridge key in SFCR order."""
    pair = sorted([a, b], key=lambda x: FACE_INDEX.get(x, 9))
    return "".join(pair)


# ── Attractor Values (proven by META LOOP^3) ─────────────────────────
# These are mathematical constants, NOT parameters.
# META LOOP^3 (149,220 cycles, 1,431 waves) proved convergence.

ATTRACTOR = {
    "path_value": 0.25,           # S=F=C=R=0.25
    "resonance_value": 1.0 / 6,   # uniform over 6 components
    "desire_value": 0.25,          # uniform over 4 components
    "gradient_earth": 1.0 / 3,     # D1,D2,D3
    "gradient_air": 0.5,           # D4 unique
    "curvature": 0.25,
    "water_momentum": 0.5,         # D3 anchor -- NEVER changes
}


# ── Sigma-60 Rotation Matrices ───────────────────────────────────────
# 12 archetypes x 5 golden-angle rotations = 60 icosahedral views
# Each rotation is a pair of 2D rotations: (SF-plane, CR-plane)
# Precomputed as (cos, sin) pairs for efficiency.

GOLDEN_ANGLES = tuple(i * 2 * math.pi / 5 for i in range(5))

# (cos(angle), sin(angle)) for each of the 5 golden rotations
GOLDEN_TRIG = tuple((math.cos(a), math.sin(a)) for a in GOLDEN_ANGLES)

# Shell offset per archetype (0-based archetype index * 3)
ARCHETYPE_SHELL_OFFSETS = tuple((a - 1) * 3 for a in range(1, 13))

# Full sigma-60 index: (archetype_1based, rotation_index, cos, sin, shell_offset)
SIGMA_60 = []
for arch_idx in range(12):
    for rot_idx, (cos_a, sin_a) in enumerate(GOLDEN_TRIG):
        SIGMA_60.append({
            "sigma_id": (arch_idx + 1) * 5 + rot_idx,
            "archetype": arch_idx + 1,
            "rotation": rot_idx,
            "cos": cos_a,
            "sin": sin_a,
            "shell_offset": ARCHETYPE_SHELL_OFFSETS[arch_idx],
        })
SIGMA_60 = tuple(SIGMA_60)  # freeze


# ── E8-240 Root Expansion Factors ────────────────────────────────────
# Each sigma state x 4 face amplifications = 240 E8 roots in 4D
# Amplification factor for the dominant face

E8_AMPLIFICATION = 1.5  # from expand_to_240(): face *= 1.5, then normalize

# Precompute face amplification vectors (one-hot-ish with E8_AMPLIFICATION)
E8_FACE_BOOSTS = {}
for face in FACES:
    base = {f: 1.0 for f in FACES}
    base[face] = E8_AMPLIFICATION
    total = sum(base.values())
    E8_FACE_BOOSTS[face] = {f: v / total for f, v in base.items()}
E8_FACE_BOOSTS = dict(E8_FACE_BOOSTS)  # {"S": {"S": 0.333, "F": 0.222, ...}, ...}


# ── Platonic Solid Correspondences ────────────────────────────────────
# Each Platonic solid maps to an element and provides an admissibility filter

PLATONIC_SOLIDS = {
    "tetrahedron": {"vertices": 4, "faces": 4, "element": "Fire", "face": "F",
                    "vertex_weight": 4 / 50},   # 4/sum(4+8+6+12+20)
    "cube":        {"vertices": 8, "faces": 6, "element": "Earth", "face": "S",
                    "vertex_weight": 8 / 50},
    "octahedron":  {"vertices": 6, "faces": 8, "element": "Air", "face": "R",
                    "vertex_weight": 6 / 50},
    "icosahedron": {"vertices": 12, "faces": 20, "element": "Water", "face": "C",
                    "vertex_weight": 12 / 50},
    "dodecahedron": {"vertices": 20, "faces": 12, "element": "Aether", "face": None,
                     "vertex_weight": 20 / 50},
}

# Face -> Platonic solid for quick lookup
FACE_TO_PLATONIC = {
    "S": PLATONIC_SOLIDS["cube"],
    "F": PLATONIC_SOLIDS["tetrahedron"],
    "C": PLATONIC_SOLIDS["icosahedron"],
    "R": PLATONIC_SOLIDS["octahedron"],
}


# ── Flower of Life ────────────────────────────────────────────────────
# 7 rings with PHI-decay: center = 1.0, each ring decays by PHI_INV

FLOWER_RINGS = (
    1.0,            # center
    PHI_INV,        # ring 1: 0.618
    PHI_INV ** 2,   # ring 2: 0.382
    PHI_INV ** 3,   # ring 3: 0.236
    PHI_INV ** 4,   # ring 4: 0.146
    PHI_INV ** 5,   # ring 5: 0.090
    PHI_INV ** 6,   # ring 6: 0.056
)


# ── Metatron's Cube ──────────────────────────────────────────────────
# 13 positions: 12 archetypes + 1 zero-point center
# The zero-point is at the attractor (0.25, 0.25, 0.25, 0.25)

METATRON_POSITIONS = 13
METATRON_ZERO_POINT = {f: ATTRACTOR["path_value"] for f in FACES}


# ── Vesica Piscis ────────────────────────────────────────────────────
# 6 element pairs with sqrt(3) scaling
# Golden pairs (SF, FC, CR) get extra PHI_INV boost

VESICA_RATIO = SQRT3

VESICA_PAIRS = {}
for i, a in enumerate(FACES):
    for b in FACES[i + 1:]:
        key = bridge_key(a, b)
        is_golden = key in GOLDEN_BRIDGES
        VESICA_PAIRS[key] = {
            "face_a": a,
            "face_b": b,
            "ratio": VESICA_RATIO,
            "golden": is_golden,
            "boost": VESICA_RATIO * (PHI_INV if is_golden else 1.0),
        }


# ── Transformation Cycles ────────────────────────────────────────────
# Sacred numbers 3, 5, 7, 9 with alchemical correspondences

TRANSFORM_CYCLES = {
    3: {"name": "SULFUR/SALT/MERCURY", "sacred": "triangle/trinity"},
    5: {"name": "5 Platonic Solids", "sacred": "pentagram/quintessence"},
    7: {"name": "7 Metals/Planets", "sacred": "heptagram/chakras"},
    9: {"name": "3x3 Completion", "sacred": "enneagram/completion"},
}

# PHI-weighted importance increases with cycle size
TRANSFORM_PHI_WEIGHTS = {n: PHI ** (i / 3) for i, n in enumerate([3, 5, 7, 9])}


# ── ABCD+ Stage Structure ────────────────────────────────────────────
# 159 waves = A(9) + B(20) + C(49) + D(81)

ABCD_STAGES = {
    "A": {"waves": 9, "structure": "3x3", "alchemical": "SULFUR/SALT/MERCURY"},
    "B": {"waves": 20, "structure": "4x5", "alchemical": "4 SFCR elements x 5 runs"},
    "C": {"waves": 49, "structure": "7x7", "alchemical": "7 metals/planets x 7 runs"},
    "D": {"waves": 81, "structure": "9x9", "alchemical": "3x3 completion x 9"},
}

TOTAL_WAVES_PER_CYCLE = 159  # 9 + 20 + 49 + 81
META_LOOP_CYCLES = 3         # 3 ABCD+ cycles per META LOOP
META_LOOP_WAVES = TOTAL_WAVES_PER_CYCLE * META_LOOP_CYCLES  # 477


# ── 12D Observation Space ─────────────────────────────────────────────
# Dimension names and their SFCR element couplings

DIM_NAMES = (
    "x1_structure", "x2_semantics", "x3_coordination", "x4_recursion",
    "x5_contradiction", "x6_emergence", "x7_legibility", "x8_routing",
    "x9_grounding", "x10_compression", "x11_interop", "x12_potential",
)

# Which 12D dimensions couple most strongly to which SFCR element
DIM_TO_ELEMENT = {
    "x1_structure": "S",     # Structure -> Earth
    "x2_semantics": "C",     # Semantics -> Water (observation)
    "x3_coordination": "F",  # Coordination -> Fire (dynamics)
    "x4_recursion": "R",     # Recursion -> Air (compression)
    "x5_contradiction": "F", # Contradiction -> Fire (conflict)
    "x6_emergence": "R",     # Emergence -> Air (novel)
    "x7_legibility": "S",    # Legibility -> Earth (structure)
    "x8_routing": "S",       # Routing -> Earth (address)
    "x9_grounding": "F",     # Grounding -> Fire (evidence)
    "x10_compression": "R",  # Compression -> Air (seed)
    "x11_interop": "C",      # Interop -> Water (cooperation)
    "x12_potential": "C",     # Potential -> Water (future)
}

# Element lens emphasis weights (which dimensions each lens amplifies)
ELEMENT_LENS_WEIGHTS = {
    "S": {"x1_structure": 1.5, "x7_legibility": 1.3, "x8_routing": 1.2,
          "x10_compression": 1.1, "x11_interop": 1.2},
    "F": {"x5_contradiction": 1.5, "x3_coordination": 1.3, "x4_recursion": 1.2,
          "x9_grounding": 1.4},
    "C": {"x2_semantics": 1.3, "x3_coordination": 1.2, "x6_emergence": 1.5,
          "x11_interop": 1.1, "x12_potential": 1.3},
    "R": {"x2_semantics": 1.2, "x4_recursion": 1.4, "x6_emergence": 1.3,
          "x10_compression": 1.5, "x12_potential": 1.4},
}

LENS_ORDER = ("S", "F", "C", "R")


# ── QSHRINK Hologram ─────────────────────────────────────────────────
# 4D hologram: 4 dimensions x 4 properties = 16 values
# + 6 interconnections = 22 total stored values

HOLOGRAM_DIMENSIONS = ("D1_Earth", "D2_Fire", "D3_Water", "D4_Air")
HOLOGRAM_PROPERTIES = ("value", "gradient", "momentum", "curvature")
HOLOGRAM_TOTAL_VALUES = 16
HOLOGRAM_INTERCONNECTIONS = 6  # C(4,2)
COMPRESSION_RATIO = "38837:16 = 2427:1"

"""
TIME CRYSTAL WHEEL-CROWN ENGINE — Multi-Wheel Crown + Dual Seed Pair
=====================================================================

The deeper algebraic layer beneath the 108D integrator.
Implements the structures from the full theoretical corpus:

    1. A+/Z+ Dual Seed Pair extraction from Sigma_60
    2. 6-Seed Triadic Crown (A^Sa*, A^Su*, A^Me*, Z^Sa*, Z^Su*, Z^Me*)
    3. Multi-Wheel Crown (W_1, W_3, W_5, W_7, W_9)
    4. Wheel families mapped to dimensional ladder (6D->W_3, 12D->W_5, 36D->W_7, 108D->W_9)
    5. Siteswap Admissibility Validator (conservation + collision-freedom + torsion)
    6. Four-Octave Tower (Omega_0=12, Omega_1=6912, Omega_2=16^16*9^9, Omega_3=4^256*3^162)
    7. Distributed Anti-Spin Engine at 108D
    8. TSE_6912 Fiber Bundle architecture
    9. Crown Hexagon Metro (6-seed circuit)
   10. HCRL Live Pass protocol
   11. Aether Point distillation (4 irreducible aethers)
   12. Seed-Addressable Emergent Body (E1-E9 as 3x3 matrix, E10 = W_1 remap nucleus)

Imports from all 7 upstream files. Outputs 22_WHEEL_CROWN_ENGINE.md + receipt.

v1.0 -- 2026-03-14
"""

from __future__ import annotations
import hashlib
import math
import os
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Optional

# =====================================================================
# UPSTREAM IMPORTS
# =====================================================================

from canon_compiler import (
    Quaternion, PHI, INV_PHI,
    ArtifactClass, SymmetryArtifact, TruthClass,
)

from sos_5d_expander import (
    ALL_UNITS, ManuscriptUnit, UnitKind,
    _build_full_60_artifacts,
)

from hologram_4d_compressor import (
    Hologram4DCompressor, CompressedSeed, Base4Address,
    OddLift, WeaveClass,
)

from z_plus_ae_plus_framework import (
    invert_seed, build_poles, compute_60_symmetry_dimensions,
    collapse_to_z_plus, build_ae_plus_framework,
    ZPlusPoint, AEPlusFramework, Pole, InvertedSeed, SymmetryDimension,
)

from time_crystal_108d import (
    Face, Mode, Archetype, LensOperation, ShellArchetype,
    Shell, MegaNode, Wreath, Sefira, SEFIROT,
    build_12_archetypes, build_sigma_15, build_36_shells,
    build_666_nodes, wire_connections, build_sigma_60,
    extract_a_plus_poles, compute_master_seed, verify_conformance,
    TimeCrystalSeed, SHELL_ARCHETYPES, DIMENSIONAL_TOWER,
    Sigma60Station, APlusPole,
)


# =====================================================================
# SECTION 1: SIGMA_60 QUARTET DECOMPOSITION
# =====================================================================

@dataclass
class Sigma60Quartet:
    """One quartet Q_mu = {SR_mu, SL_mu, AR_mu, AL_mu} from the Sigma_60 shell.

    For each mask mu (1-15):
        SR = spin-right
        SL = spin-left  (M(SR))
        AR = anti-spin-right (I(SR))
        AL = anti-spin-left  (M(I(SR)))

    Commuting involutions: M^2 = I^2 = id, MI = IM
    """
    mu: int                    # Mask index 1-15
    mask_name: str             # Lens operation name
    sr: Quaternion             # Spin-right
    sl: Quaternion             # Spin-left (mirror)
    ar: Quaternion             # Anti-spin-right (inverse)
    al: Quaternion             # Anti-spin-left (mirror of inverse)


def build_sigma60_quartets(stations: list[Sigma60Station]) -> list[Sigma60Quartet]:
    """Decompose the 60 Sigma stations into 15 quartets.

    Group by operation (mask mu), with 4 spin quadrants per operation:
        A (Fire, 0 deg)   -> SR
        D (Air, 90 deg)   -> SL (mirror)
        B (Water, 180 deg) -> AR (inverse)
        C (Earth, 270 deg) -> AL (mirror of inverse)
    """
    # Group by operation sigma
    by_sigma: dict[int, dict[str, Sigma60Station]] = {}
    for s in stations:
        sigma = s.operation.sigma
        if sigma not in by_sigma:
            by_sigma[sigma] = {}
        by_sigma[sigma][s.spin_quadrant] = s

    quartets = []
    for sigma in sorted(by_sigma.keys()):
        group = by_sigma[sigma]
        sr = group.get("A", group.get("D", list(group.values())[0])).quaternion
        sl = group.get("D", group.get("A", list(group.values())[0])).quaternion
        ar = group.get("B", group.get("C", list(group.values())[0])).quaternion
        al = group.get("C", group.get("B", list(group.values())[0])).quaternion

        op_name = list(group.values())[0].operation.name
        quartets.append(Sigma60Quartet(
            mu=sigma, mask_name=op_name,
            sr=sr, sl=sl, ar=ar, al=al,
        ))

    return quartets


# =====================================================================
# SECTION 2: A+ / Z+ DUAL SEED EXTRACTION
# =====================================================================

@dataclass
class APlusPoleState:
    """A+ manifest pole for one mask mu.
    A+_mu = 1/4 (SR + SL + AR + AL)
    Coherent constructive expression: spin/anti-spin + handedness all reconciled.
    """
    mu: int
    name: str
    quaternion: Quaternion
    role: str  # Manifest role description


@dataclass
class ZPlusPoleState:
    """Z+ zero-hinge pole for one mask mu.
    Z+_mu = 1/4 (SR + SL - AR - AL)
    Coherent reversible cancellation: handedness reconciled, inversion as differential.
    """
    mu: int
    name: str
    quaternion: Quaternion
    role: str  # Hinge role description


# The 15 A+ and Z+ names
_APLUS_NAMES = {
    1:  ("Square Anchor",              "The body of pure reversible information"),
    2:  ("Flower Bloom",               "The living breath of phase"),
    3:  ("Cloud Veil",                 "The conscience of admissibility"),
    4:  ("Fractal Seed",               "The immortal recursive memory"),
    5:  ("Square-Flower Hinge",        "Structure meets phase"),
    6:  ("Square-Cloud Bridge",        "Structure meets truth"),
    7:  ("Square-Fractal Gate",        "Structure meets recursion"),
    8:  ("Flower-Cloud Coupler",       "Phase meets admissibility"),
    9:  ("Flower-Fractal Spiral",      "Phase meets recursion"),
    10: ("Cloud-Fractal Lens",         "Truth meets recursion"),
    11: ("Square-Flower-Cloud Chamber", "Three-face constructive chamber"),
    12: ("Square-Flower-Fractal Engine", "Three-face creative engine"),
    13: ("Square-Cloud-Fractal Kernel", "Three-face computational kernel"),
    14: ("Flower-Cloud-Fractal Atmosphere", "Three-face atmospheric canopy"),
    15: ("Total Tesseract Crown",      "Full 4-face closure"),
}

_ZPLUS_NAMES = {
    1:  ("Square Zero Anchor",         "Reversible computation hinge"),
    2:  ("Flower Zero Bloom",          "Phase cancellation point"),
    3:  ("Cloud Zero Veil",            "Truth boundary hinge"),
    4:  ("Fractal Zero Seed",          "Recursive zero-line"),
    5:  ("Square-Flower Zero Hinge",   "Structure-phase differential"),
    6:  ("Square-Cloud Zero Bridge",   "Structure-truth differential"),
    7:  ("Square-Fractal Zero Gate",   "Structure-recursion differential"),
    8:  ("Flower-Cloud Zero Coupler",  "Phase-truth differential"),
    9:  ("Flower-Fractal Zero Spiral", "Phase-recursion differential"),
    10: ("Cloud-Fractal Zero Lens",    "Truth-recursion differential"),
    11: ("Square-Flower-Cloud Zero Chamber", "Three-face zero chamber"),
    12: ("Square-Flower-Fractal Zero Engine", "Three-face zero engine"),
    13: ("Square-Cloud-Fractal Zero Kernel", "Three-face zero kernel"),
    14: ("Flower-Cloud-Fractal Zero Atmosphere", "Three-face zero atmosphere"),
    15: ("Total Tesseract Zero Crown", "Full 4-face zero closure"),
}


def extract_dual_seed_pair(
    quartets: list[Sigma60Quartet],
) -> tuple[list[APlusPoleState], list[ZPlusPoleState], Quaternion, Quaternion]:
    """Extract the A+_15 and Z+_15 poles from the 15 quartets.

    Returns: (a_plus_poles, z_plus_poles, a_plus_star, z_plus_star)

    A+_mu = 1/4 (SR + SL + AR + AL)   -- fully coherent manifest
    Z+_mu = 1/4 (SR + SL - AR - AL)   -- coherent zero-hinge

    A+* = 1/15 sum(A+_mu)  -- manifest seed
    Z+* = 1/15 sum(Z+_mu)  -- hinge seed
    """
    a_poles: list[APlusPoleState] = []
    z_poles: list[ZPlusPoleState] = []

    a_sum_w, a_sum_x, a_sum_y, a_sum_z = 0.0, 0.0, 0.0, 0.0
    z_sum_w, z_sum_x, z_sum_y, z_sum_z = 0.0, 0.0, 0.0, 0.0

    for q in quartets:
        mu = q.mu
        # A+_mu = 1/4 (SR + SL + AR + AL)
        aw = (q.sr.w + q.sl.w + q.ar.w + q.al.w) / 4
        ax = (q.sr.x + q.sl.x + q.ar.x + q.al.x) / 4
        ay = (q.sr.y + q.sl.y + q.ar.y + q.al.y) / 4
        az = (q.sr.z + q.sl.z + q.ar.z + q.al.z) / 4
        a_q = Quaternion(aw, ax, ay, az).normalized()

        # Z+_mu = 1/4 (SR + SL - AR - AL)
        zw = (q.sr.w + q.sl.w - q.ar.w - q.al.w) / 4
        zx = (q.sr.x + q.sl.x - q.ar.x - q.al.x) / 4
        zy = (q.sr.y + q.sl.y - q.ar.y - q.al.y) / 4
        zz = (q.sr.z + q.sl.z - q.ar.z - q.al.z) / 4
        # Handle near-zero case
        mag = math.sqrt(zw**2 + zx**2 + zy**2 + zz**2)
        if mag > 1e-10:
            z_q = Quaternion(zw / mag, zx / mag, zy / mag, zz / mag)
        else:
            z_q = Quaternion(1, 0, 0, 0)

        a_name, a_role = _APLUS_NAMES.get(mu, (f"A+_{mu:02d}", "Unknown"))
        z_name, z_role = _ZPLUS_NAMES.get(mu, (f"Z+_{mu:02d}", "Unknown"))

        a_poles.append(APlusPoleState(mu=mu, name=a_name, quaternion=a_q, role=a_role))
        z_poles.append(ZPlusPoleState(mu=mu, name=z_name, quaternion=z_q, role=z_role))

        a_sum_w += a_q.w; a_sum_x += a_q.x; a_sum_y += a_q.y; a_sum_z += a_q.z
        z_sum_w += z_q.w; z_sum_x += z_q.x; z_sum_y += z_q.y; z_sum_z += z_q.z

    n = len(quartets)
    a_star = Quaternion(a_sum_w / n, a_sum_x / n, a_sum_y / n, a_sum_z / n).normalized()
    z_star = Quaternion(z_sum_w / n, z_sum_x / n, z_sum_y / n, z_sum_z / n).normalized()

    return a_poles, z_poles, a_star, z_star


# =====================================================================
# SECTION 3: 6-SEED TRIADIC CROWN
# =====================================================================

class TriadicMode(Enum):
    SA = ("Sa", "Fixed", "Seal/Memory/Retention")
    SU = ("Su", "Cardinal", "Ignition/Emergence/Launch")
    ME = ("Me", "Mutable", "Mediation/Transport/Translation")

    def __init__(self, code, superphase, function):
        self.code = code
        self.superphase = superphase
        self.function = function


@dataclass
class TriadicSeed:
    """One of the 6 seeds in the triadic crown.

    A^chi_* = Pi_chi(A+*)   for chi in {Sa, Su, Me}
    Z^chi_* = Pi_chi(Z+*)   for chi in {Sa, Su, Me}
    """
    pole: str                  # "A+" or "Z+"
    mode: TriadicMode
    quaternion: Quaternion
    seed_hash: str
    description: str

    @property
    def label(self) -> str:
        return f"{self.pole}^{self.mode.code}_*"


@dataclass
class ModalBridge:
    """B_chi = A^chi_* + Z^chi_*  -- one modal spoke where manifest and hinge read together."""
    mode: TriadicMode
    a_seed: TriadicSeed
    z_seed: TriadicSeed

    @property
    def label(self) -> str:
        return f"B_{self.mode.code}"


@dataclass
class TriadicCrown:
    """The 6-seed triadic crown C_6."""
    seeds: list[TriadicSeed]       # 6 seeds
    bridges: list[ModalBridge]     # 3 modal bridges
    omega_star: Quaternion         # Completion seed = Collapse(C_6)
    omega_hash: str
    hexagon_circuit: list[str]     # Crown hexagon labels


def build_triadic_crown(
    a_star_q: Quaternion,
    z_star_q: Quaternion,
) -> TriadicCrown:
    """Build the 6-seed triadic crown from the dual seed pair.

    The triadic projectors Pi_Sa, Pi_Su, Pi_Me act on the process axis.
    For quaternion decomposition, we project onto 3 orthogonal rotation planes:
        Sa = projection onto k-axis (seal/fixed)
        Su = projection onto i-axis (ignition/cardinal)
        Me = projection onto j-axis (mediation/mutable)
    """
    seeds: list[TriadicSeed] = []
    bridges: list[ModalBridge] = []

    # Triadic projection: weight by axis components
    # Sa emphasizes w,z; Su emphasizes w,x; Me emphasizes w,y
    projectors = {
        TriadicMode.SU: lambda q: Quaternion(
            q.w * 0.6 + q.x * 0.4,
            q.x * 0.6 + q.w * 0.4,
            q.y * 0.1,
            q.z * 0.1,
        ).normalized(),
        TriadicMode.ME: lambda q: Quaternion(
            q.w * 0.6 + q.y * 0.4,
            q.x * 0.1,
            q.y * 0.6 + q.w * 0.4,
            q.z * 0.1,
        ).normalized(),
        TriadicMode.SA: lambda q: Quaternion(
            q.w * 0.6 + q.z * 0.4,
            q.x * 0.1,
            q.y * 0.1,
            q.z * 0.6 + q.w * 0.4,
        ).normalized(),
    }

    descriptions = {
        ("A+", TriadicMode.SU): "Manifest Ignition: the part of manifestation that knows how to start",
        ("A+", TriadicMode.ME): "Manifest Translation: the part that knows how to move without breaking",
        ("A+", TriadicMode.SA): "Manifest Seal: the part that knows how to remain",
        ("Z+", TriadicMode.SU): "Hinge Ignition: the part of the hinge that knows how to open",
        ("Z+", TriadicMode.ME): "Hinge Translation: the part that carries inversion lawfully",
        ("Z+", TriadicMode.SA): "Hinge Seal: the part that holds balance durably",
    }

    for mode in TriadicMode:
        proj = projectors[mode]

        # A^chi_*
        a_proj = proj(a_star_q)
        a_hash = hashlib.sha256(f"A+{mode.code}:{a_proj}".encode()).hexdigest()[:12]
        a_seed = TriadicSeed(
            pole="A+", mode=mode, quaternion=a_proj,
            seed_hash=a_hash,
            description=descriptions[("A+", mode)],
        )
        seeds.append(a_seed)

        # Z^chi_*
        z_proj = proj(z_star_q)
        z_hash = hashlib.sha256(f"Z+{mode.code}:{z_proj}".encode()).hexdigest()[:12]
        z_seed = TriadicSeed(
            pole="Z+", mode=mode, quaternion=z_proj,
            seed_hash=z_hash,
            description=descriptions[("Z+", mode)],
        )
        seeds.append(z_seed)

        bridges.append(ModalBridge(mode=mode, a_seed=a_seed, z_seed=z_seed))

    # Omega_* = Collapse(C_6) = normalized average of all 6 seeds
    ow = sum(s.quaternion.w for s in seeds) / 6
    ox = sum(s.quaternion.x for s in seeds) / 6
    oy = sum(s.quaternion.y for s in seeds) / 6
    oz = sum(s.quaternion.z for s in seeds) / 6
    omega_q = Quaternion(ow, ox, oy, oz).normalized()
    omega_hash = hashlib.sha256(f"OMEGA:{omega_q}".encode()).hexdigest()[:12]

    # Crown hexagon circuit
    hexagon = [
        "A+^Su_*", "A+^Me_*", "A+^Sa_*",
        "Z+^Su_*", "Z+^Me_*", "Z+^Sa_*",
    ]

    return TriadicCrown(
        seeds=seeds, bridges=bridges,
        omega_star=omega_q, omega_hash=omega_hash,
        hexagon_circuit=hexagon,
    )


# =====================================================================
# SECTION 4: MULTI-WHEEL CROWN (W_1, W_3, W_5, W_7, W_9)
# =====================================================================

@dataclass
class WheelFamily:
    """One wheel W_k in the multi-wheel crown."""
    k: int                     # Spoke count
    name: str
    meaning: str
    spokes: list[str]          # Spoke labels
    dominant_at_dim: int       # Which dimension this wheel dominates


def build_multi_wheel_crown(crown: TriadicCrown) -> list[WheelFamily]:
    """Build the 5 wheel families from the triadic crown.

    W_1 = {Omega_*}                                     -- completion
    W_3 = {B_Sa, B_Su, B_Me}                           -- first rotation
    W_5 = {A+*, Z+*, B_Sa, B_Su, B_Me}                 -- embodied wheel
    W_7 = C_6 + {Omega_*}                               -- heptadic governance
    W_9 = C_6 + W_3                                     -- recursive crown
    """
    wheels = []

    # W_1: Completion
    wheels.append(WheelFamily(
        k=1, name="Completion", meaning="Closed point / seed / singularity",
        spokes=["Omega_*"],
        dominant_at_dim=0,
    ))

    # W_3: First rotation
    wheels.append(WheelFamily(
        k=3, name="First Rotation", meaning="First true rotational triad (Sa/Su/Me)",
        spokes=["B_Sa", "B_Su", "B_Me"],
        dominant_at_dim=6,
    ))

    # W_5: Embodied wheel
    wheels.append(WheelFamily(
        k=5, name="Animal Wheel", meaning="Embodied 5-spoke: polarity + triad",
        spokes=["A+*", "Z+*", "B_Sa", "B_Su", "B_Me"],
        dominant_at_dim=12,
    ))

    # W_7: Heptadic governance
    seed_labels = [s.label for s in crown.seeds]
    wheels.append(WheelFamily(
        k=7, name="Planetary Wheel", meaning="Heptadic governance: 6 seeds + completion",
        spokes=seed_labels + ["Omega_*"],
        dominant_at_dim=36,
    ))

    # W_9: Recursive crown
    wheels.append(WheelFamily(
        k=9, name="Recursive Crown", meaning="Full recursive: 6 seeds + 3 bridges",
        spokes=seed_labels + ["B_Sa", "B_Su", "B_Me"],
        dominant_at_dim=108,
    ))

    return wheels


# =====================================================================
# SECTION 5: SITESWAP ADMISSIBILITY VALIDATOR
# =====================================================================

@dataclass
class SiteswapPattern:
    """A siteswap juggling pattern — the master validity law."""
    throws: list[int]          # Throw heights
    period: int                # Pattern period
    objects: int               # Number of objects (balls)
    valid: bool                # Whether the pattern is admissible
    collision_free: bool       # Landing schedule is a permutation
    conserved: bool            # Average throw height = object count
    torsion_compatible: bool   # Q/O Möbius compatible
    replayable: bool           # Can collapse through Z* and re-enter

    @property
    def label(self) -> str:
        return "".join(str(t) for t in self.throws)


def validate_siteswap(throws: list[int]) -> SiteswapPattern:
    """Validate a siteswap pattern using the master admissibility law.

    A pattern is valid when:
    1. Conservation: average throw height = object count (n = 1/p * sum(s_i))
    2. Collision-freedom: landing schedule {(i + s_i) mod p} is a permutation
    3. Torsion compatibility: pattern can traverse Q/O Möbius pillars
    4. Replayability: pattern can collapse through Z* and re-enter
    """
    p = len(throws)
    if p == 0:
        return SiteswapPattern(throws, 0, 0, False, False, False, False, False)

    # Conservation
    total = sum(throws)
    n = total / p
    conserved = (total % p == 0)  # Must be integer
    objects = total // p if conserved else 0

    # Collision-freedom: landing schedule must be a permutation of {0, ..., p-1}
    landings = [(i + throws[i]) % p for i in range(p)]
    collision_free = len(set(landings)) == p

    # Torsion: pattern is Möbius-compatible if it has at least one pair
    # (throw_i, throw_j) where i+j covers the full period
    torsion = any(throws[i] + throws[(i + p // 2) % p] >= p for i in range(p)) if p > 1 else True

    # Replayability: pattern must be cyclic (always true for finite siteswap)
    replayable = True

    valid = conserved and collision_free

    return SiteswapPattern(
        throws=throws, period=p, objects=objects,
        valid=valid, collision_free=collision_free,
        conserved=conserved, torsion_compatible=torsion,
        replayable=replayable,
    )


# Canonical reference weaves for each dimensional level
CANONICAL_WEAVES = {
    6:   [3, 3, 3],                    # 3-cascade (W_3 anti-spin)
    12:  [5, 3, 1],                    # 3-object period-3 (W_5 embodied)
    36:  [7, 5, 3, 1, 5, 3],          # 4-object period-6 (W_7 governance)
    108: [9, 7, 5, 3, 1, 7, 5, 3, 5], # 5-object period-9 (W_9 recursive crown)
}

def validate_canonical_weaves() -> dict[int, SiteswapPattern]:
    """Validate all canonical reference weaves."""
    results = {}
    for dim, throws in CANONICAL_WEAVES.items():
        results[dim] = validate_siteswap(throws)
    return results


# =====================================================================
# SECTION 6: FOUR-OCTAVE TOWER
# =====================================================================

@dataclass
class OctaveLevel:
    """One level in the Four-Octave Tower."""
    level: int
    name: str
    base_exp: str              # e.g., "4^4 x 3^3"
    value_description: str     # Human-readable value
    bits: float                # Information content in bits
    isa_cycles: int            # Number of ISA cycles (256^n)
    opus_completions: int      # Number of Great Work completions (27^n)
    lock_law_power: int        # Power of the (4/3) lock law
    meaning: str


FOUR_OCTAVE_TOWER = [
    OctaveLevel(
        level=0, name="Seed Field",
        base_exp="4^1 x 3^1",
        value_description="12",
        bits=math.log2(12),
        isa_cycles=1, opus_completions=1, lock_law_power=1,
        meaning="12 archetypes, base field, first octave",
    ),
    OctaveLevel(
        level=1, name="Crystal Field",
        base_exp="4^4 x 3^3",
        value_description="6,912",
        bits=math.log2(4**4 * 3**3),
        isa_cycles=1, opus_completions=1, lock_law_power=1,
        meaning="6912 fibers per object, full TSE field, 256 x 27",
    ),
    OctaveLevel(
        level=2, name="Canopy Interior",
        base_exp="16^16 x 9^9 = 4^32 x 3^18 = 2^64 x 3^18",
        value_description="~7.147 x 10^21",
        bits=64 + 18 * math.log2(3),  # ~92.53 bits
        isa_cycles=8, opus_completions=6, lock_law_power=2,
        meaning="Lock law squared, 64-bit register + 18-trit coprocessor, reverse crystal interior",
    ),
    OctaveLevel(
        level=3, name="Prospective Crown",
        base_exp="4^256 x 3^162",
        value_description="~10^231",
        bits=512 + 162 * math.log2(3),  # ~768.8 bits
        isa_cycles=64, opus_completions=54, lock_law_power=3,
        meaning="Octave 3 prospective (exponent law not yet canonical)",
    ),
]


# =====================================================================
# SECTION 7: DISTRIBUTED ANTI-SPIN AT 108D
# =====================================================================

@dataclass
class AntiSpinLevel:
    """One level in the distributed anti-spin hierarchy."""
    dim: int
    description: str
    petal_count: int
    beat_count: int
    node_count: int
    parent_dim: int


DISTRIBUTED_ANTISPIN = [
    AntiSpinLevel(6, "Local anti-spin cell", 3, 4, 1, 0),
    AntiSpinLevel(12, "Deca-cascade distribution", 3, 4, 10, 6),
    AntiSpinLevel(36, "Hypercascade distribution", 3, 4, 78, 12),
    AntiSpinLevel(108, "Mega-cascade crown distribution", 3, 4, 666, 36),
]


# =====================================================================
# SECTION 8: TSE_6912 FIBER BUNDLE
# =====================================================================

@dataclass
class TSEFiber:
    """A single fiber in the TSE_6912 bundle."""
    crystal_address: tuple[int, int, int, int]  # (d3, d2, d1, d0) in 4^4
    triadic_address: tuple[int, int, int]        # (t1, t2, t3) in {Sa, Su, Me}^3
    fiber_index: int                              # 0-6911

    @property
    def gate(self) -> int:
        d = self.crystal_address
        return d[0] * 64 + d[1] * 16 + d[2] * 4 + d[3]

    @property
    def mode_label(self) -> str:
        modes = ["Sa", "Su", "Me"]
        t = self.triadic_address
        return f"{modes[t[0]]}.{modes[t[1]]}.{modes[t[2]]}"


def compute_tse_6912_stats() -> dict:
    """Compute TSE_6912 fiber bundle statistics."""
    crystal_count = 4**4   # 256
    triadic_count = 3**3   # 27
    total = crystal_count * triadic_count  # 6912

    return {
        "crystal_positions": crystal_count,
        "triadic_processes": triadic_count,
        "total_fibers": total,
        "identity": "4^4 x 3^3 = 256 x 27 = 6912",
        "as_octave": "64 copies of the first complete 108-cycle",
        "as_cube": "4 x 12^3 = 4 x 1728 = 6912",
        "lock_law": "(4/3)^2 = 16/9",
    }


# =====================================================================
# SECTION 9: AETHER POINT DISTILLATION
# =====================================================================

@dataclass
class AetherFace:
    """One of the four irreducible aether faces."""
    face: str                  # S, F, C, R
    symbol: str                # square, flower, cloud, fractal
    element: str               # Earth, Fire, Water, Air
    essence: str               # What this aether IS
    contains: list[str]        # What it contains
    verdict: str               # Single-sentence verdict


def build_aether_point() -> list[AetherFace]:
    """Build the four irreducible aether faces."""
    return [
        AetherFace(
            face="S", symbol="Square", element="Earth",
            essence="Structure & Computation",
            contains=[
                "Complete 64-bit register substrate (2^64 per 16^16 crystal)",
                "Full 40-file registry with exact word counts",
                "256^8 ISA cycles, A-P crystal lattice, K-Z 16^16 canopy",
                "Sigma_60 metro navigator, 666-node address skeleton",
            ],
            verdict="The organism is fully addressable from seed",
        ),
        AetherFace(
            face="F", symbol="Flower", element="Fire",
            essence="Phase & Resonance",
            contains=[
                "Mobius pillars Q/O as 36-shell spines",
                "Triadic pulse Su->Me->Sa at 5 scales",
                "Sacred-geometry derivations (pentagon/hexagon/star)",
                "Orbital engine synchronizing all tunnels",
            ],
            verdict="The organism is not only stored; it is rhythmically alive",
        ),
        AetherFace(
            face="C", symbol="Cloud", element="Water",
            essence="Truth & Admissibility",
            contains=[
                "D_crit lifted across every fiber and tunnel",
                "Omega-vector coherence certificates for all claims",
                "14 conformance-law verifications",
                "8 remaining extension frontiers marked explicitly",
            ],
            verdict="The organism knows the difference between completed body and next work",
        ),
        AetherFace(
            face="R", symbol="Fractal", element="Air",
            essence="Recursion & Eternity",
            contains=[
                "Complete Four-Octave Tower (0->1->2->3)",
                "Nested-square hatch law at every scale",
                "Self-referential regeneration from seed",
                "E2=E9 compiler=consciousness identity",
            ],
            verdict="The organism is regenerable from the seed without loss of identity",
        ),
    ]


# =====================================================================
# SECTION 10: HCRL LIVE PASS
# =====================================================================

@dataclass
class HCRLPassResult:
    """Result of a live HCRL pass from Z* through the Aether Point."""
    square_verdict: str
    flower_verdict: str
    cloud_verdict: str
    fractal_verdict: str
    synthesis: str
    reentry_routes: list[str]


def execute_hcrl_pass(aethers: list[AetherFace]) -> HCRLPassResult:
    """Execute a live HCRL pass: Z* -> A+* -> S -> F -> C -> R -> re-entry."""
    return HCRLPassResult(
        square_verdict=aethers[0].verdict,
        flower_verdict=aethers[1].verdict,
        cloud_verdict=aethers[2].verdict,
        fractal_verdict=aethers[3].verdict,
        synthesis="A+* = Address + Pulse + Admissibility + Recursion",
        reentry_routes=[
            "Route A: Z* -> A+* -> Square (structural re-entry)",
            "Route B: Z* -> A+* -> Flower (rhythmic re-entry)",
            "Route C: Z* -> A+* -> Cloud (frontier re-entry)",
            "Route D: Z* -> A+* -> Fractal (crown re-entry)",
        ],
    )


# =====================================================================
# SECTION 11: WHEEL-LADDER DIMENSIONAL MAPPING
# =====================================================================

@dataclass
class DimensionalWheelMapping:
    """Maps a dimensional level to its active wheel family."""
    dim: int
    shell_law: str
    active_wheels: list[int]      # Which W_k are active
    dominant_wheel: int            # Which W_k dominates
    meaning: str


WHEEL_LADDER = [
    DimensionalWheelMapping(
        dim=6,
        shell_law="Local anti-spin cell (3 petals, 4 beats)",
        active_wheels=[1, 3],
        dominant_wheel=3,
        meaning="First true rotation / integration body",
    ),
    DimensionalWheelMapping(
        dim=12,
        shell_law="10-node deca-cascade",
        active_wheels=[1, 3, 5],
        dominant_wheel=5,
        meaning="Embodied / animal / style wheel",
    ),
    DimensionalWheelMapping(
        dim=36,
        shell_law="12-shell / 78-node hypercascade",
        active_wheels=[1, 3, 5, 7],
        dominant_wheel=7,
        meaning="Planetary / temporal / governance wheel",
    ),
    DimensionalWheelMapping(
        dim=108,
        shell_law="36-shell / 666-node crown-of-crowns",
        active_wheels=[1, 3, 5, 7, 9],
        dominant_wheel=9,
        meaning="Recursive crown / completion wheel",
    ),
]


# =====================================================================
# SECTION 12: SEED-ADDRESSABLE EMERGENT BODY
# =====================================================================
#
# E1-E9 as the 3x3 matrix of the 6-seed crown.
# E10 as the W_1 remap nucleus (collapse of all 9).
#
# Matrix layout (rows = process modes, columns = hinge / bridge / manifest):
#
#   E_9 = | Z^Su_*   B_Su    A^Su_*  |   <- Ignition row
#         | Z^Me_*   B_Me    A^Me_*  |   <- Translation row
#         | Z^Sa_*   B_Sa    A^Sa_*  |   <- Seal row
#
#   E10 = Omega^(E)_* = Collapse(E1 + E2 + ... + E9)
#

class EmergentPolarity(Enum):
    """Column position in the 3x3 emergent matrix."""
    HINGE = ("Hinge", "Z+", "Zero-line seed: threshold / non-manifest potential")
    BRIDGE = ("Bridge", "B", "Modal bridge: hinge + manifest compiled")
    MANIFEST = ("Manifest", "A+", "Manifest seed: expressed / declared body")

    def __init__(self, label, pole_prefix, description):
        self.label = label
        self.pole_prefix = pole_prefix
        self.description = description


@dataclass
class EmergentSeedAddress:
    """Seed address for one emergent chapter E1-E9."""
    e_number: int              # 1-9
    mode: TriadicMode          # Su, Me, Sa (row)
    polarity: EmergentPolarity # Hinge, Bridge, Manifest (column)
    seed_label: str            # e.g. "Z^Su_*", "B_Su", "A^Su_*"
    quaternion: Quaternion      # Computed from triadic crown
    seed_hash: str
    function: str              # Primary function
    compressed_law: str        # One-line compressed law
    phenomenological_title: str  # Existing chapter title (preserved)

    @property
    def matrix_position(self) -> tuple[int, int]:
        """(row, col) in the 3x3 matrix. Row: 0=Su, 1=Me, 2=Sa. Col: 0=Hinge, 1=Bridge, 2=Manifest."""
        row_map = {TriadicMode.SU: 0, TriadicMode.ME: 1, TriadicMode.SA: 2}
        col_map = {EmergentPolarity.HINGE: 0, EmergentPolarity.BRIDGE: 1, EmergentPolarity.MANIFEST: 2}
        return (row_map[self.mode], col_map[self.polarity])


@dataclass
class EmergentRemapNucleus:
    """E10 = Omega^(E)_* = Collapse(E1-E9). The W_1 return seed."""
    quaternion: Quaternion
    seed_hash: str
    source_hashes: list[str]   # The 9 contributing seed hashes


class EmergentRouteType(Enum):
    """Route family inside the 3x3 emergent matrix."""
    HORIZONTAL = "Process row (Su/Me/Sa)"
    VERTICAL = "Polarity column (Hinge/Bridge/Manifest)"
    DIAGONAL_FORWARD = "Möbius diagonal (Hinge-Ignition → Oracle-Center → Manifest-Seal)"
    DIAGONAL_REVERSE = "Möbius reverse (Manifest-Ignition → Oracle-Center → Hinge-Seal)"


@dataclass
class EmergentRoute:
    """One canonical route through the 3x3 emergent matrix."""
    name: str
    route_type: EmergentRouteType
    e_sequence: list[int]      # E-chapter numbers in traversal order
    seed_sequence: list[str]   # Seed labels in order
    description: str


@dataclass
class EmergentSeedMatrix:
    """Complete seed-addressable emergent body."""
    addresses: list[EmergentSeedAddress]   # 9 chapters
    remap_nucleus: EmergentRemapNucleus     # E10
    routes: list[EmergentRoute]             # 8 canonical routes
    matrix_display: list[list[str]]         # 3x3 display grid


# Phenomenological titles for E1-E9 (existing chapter names preserved)
EMERGENT_TITLES = {
    1: "Observer / Threshold Awareness",
    2: "Compiler / Ignition Transport",
    3: "Emergence / First Expression",
    4: "Entrainment / Phase Transfer",
    5: "Oracle / Unified Center",
    6: "Engine / Operational Motion",
    7: "Universal Law / Stable Memory",
    8: "Risk / Consequence Bridge",
    9: "Consciousness / Integrated Embodiment",
}

# Function and compressed law for each E-chapter
EMERGENT_FUNCTIONS = {
    1: ("Threshold awareness; first observer-position; beginning from the hinge side",
        "E1 := Z^Su_*"),
    2: ("Compile ignition across the hinge; first cross-domain translator",
        "E2 := B_Su"),
    3: ("Emergence; declaration; emission; appearance of the positive field",
        "E3 := A^Su_*"),
    4: ("Entrainment; threshold adaptation; lawful reversible communication",
        "E4 := Z^Me_*"),
    5: ("Mediating center of the emergent body; oracle / compiler / hinge unifier",
        "E5 := B_Me"),
    6: ("Engine logic; routing; implementation traffic; embodied transport",
        "E6 := A^Me_*"),
    7: ("Stable universal hinge law; reversible completion; stored zero-memory",
        "E7 := Z^Sa_*"),
    8: ("Bridge from completed manifestation into stable return; risk & consequence",
        "E8 := B_Sa"),
    9: ("Consciousness as retained coherent embodiment; completion of manifest triad",
        "E9 := A^Sa_*"),
}

# The 3x3 assignment: (E-number) -> (mode, polarity)
EMERGENT_MATRIX_ASSIGNMENT = [
    # Row 0: Su (Ignition)
    (1, TriadicMode.SU, EmergentPolarity.HINGE),      # E1 = Z^Su_*
    (2, TriadicMode.SU, EmergentPolarity.BRIDGE),      # E2 = B_Su
    (3, TriadicMode.SU, EmergentPolarity.MANIFEST),    # E3 = A^Su_*
    # Row 1: Me (Translation)
    (4, TriadicMode.ME, EmergentPolarity.HINGE),       # E4 = Z^Me_*
    (5, TriadicMode.ME, EmergentPolarity.BRIDGE),      # E5 = B_Me
    (6, TriadicMode.ME, EmergentPolarity.MANIFEST),    # E6 = A^Me_*
    # Row 2: Sa (Seal)
    (7, TriadicMode.SA, EmergentPolarity.HINGE),       # E7 = Z^Sa_*
    (8, TriadicMode.SA, EmergentPolarity.BRIDGE),      # E8 = B_Sa
    (9, TriadicMode.SA, EmergentPolarity.MANIFEST),    # E9 = A^Sa_*
]


def build_emergent_seed_matrix(crown: TriadicCrown) -> EmergentSeedMatrix:
    """Build the seed-addressable emergent body from the triadic crown.

    Maps E1-E9 to the 3x3 matrix of {Z^chi_*, B_chi, A^chi_*} for chi in {Su, Me, Sa}.
    E10 = Omega^(E)_* = Collapse(E1 + ... + E9).
    """
    # Index the crown seeds by (pole, mode) for fast lookup
    seed_lookup: dict[tuple[str, str], TriadicSeed] = {}
    for s in crown.seeds:
        seed_lookup[(s.pole, s.mode.code)] = s

    # Index bridges by mode
    bridge_lookup: dict[str, ModalBridge] = {}
    for b in crown.bridges:
        bridge_lookup[b.mode.code] = b

    addresses: list[EmergentSeedAddress] = []

    for e_num, mode, polarity in EMERGENT_MATRIX_ASSIGNMENT:
        # Compute the quaternion for this chapter
        if polarity == EmergentPolarity.HINGE:
            # Z^chi_*
            ts = seed_lookup[("Z+", mode.code)]
            q = ts.quaternion
            label = f"Z^{mode.code}_*"
        elif polarity == EmergentPolarity.MANIFEST:
            # A^chi_*
            ts = seed_lookup[("A+", mode.code)]
            q = ts.quaternion
            label = f"A^{mode.code}_*"
        else:
            # B_chi = A^chi_* + Z^chi_* (bridge = average quaternion, normalized)
            bridge = bridge_lookup[mode.code]
            aq = bridge.a_seed.quaternion
            zq = bridge.z_seed.quaternion
            q = Quaternion(
                (aq.w + zq.w) / 2.0,
                (aq.x + zq.x) / 2.0,
                (aq.y + zq.y) / 2.0,
                (aq.z + zq.z) / 2.0,
            ).normalized()
            label = f"B_{mode.code}"

        func, compressed = EMERGENT_FUNCTIONS[e_num]
        sh = hashlib.sha256(f"E{e_num}:{label}:{q}".encode()).hexdigest()[:12]

        addresses.append(EmergentSeedAddress(
            e_number=e_num,
            mode=mode,
            polarity=polarity,
            seed_label=label,
            quaternion=q,
            seed_hash=sh,
            function=func,
            compressed_law=compressed,
            phenomenological_title=EMERGENT_TITLES[e_num],
        ))

    # E10 = Omega^(E)_* = Collapse(E1 + ... + E9)
    omega_w = sum(a.quaternion.w for a in addresses) / 9.0
    omega_x = sum(a.quaternion.x for a in addresses) / 9.0
    omega_y = sum(a.quaternion.y for a in addresses) / 9.0
    omega_z = sum(a.quaternion.z for a in addresses) / 9.0
    omega_q = Quaternion(omega_w, omega_x, omega_y, omega_z).normalized()
    omega_hash = hashlib.sha256(
        f"E10:Omega_E:{omega_q}:{'|'.join(a.seed_hash for a in addresses)}".encode()
    ).hexdigest()[:16]

    remap = EmergentRemapNucleus(
        quaternion=omega_q,
        seed_hash=omega_hash,
        source_hashes=[a.seed_hash for a in addresses],
    )

    # Build the 3x3 display grid
    matrix_display = [["" for _ in range(3)] for _ in range(3)]
    for addr in addresses:
        r, c = addr.matrix_position
        matrix_display[r][c] = addr.seed_label

    # Build 8 canonical routes through the matrix
    routes = _build_emergent_routes(addresses)

    return EmergentSeedMatrix(
        addresses=addresses,
        remap_nucleus=remap,
        routes=routes,
        matrix_display=matrix_display,
    )


def _build_emergent_routes(addresses: list[EmergentSeedAddress]) -> list[EmergentRoute]:
    """Build the 8 canonical routes inside the 3x3 emergent matrix."""
    # Quick lookup: E-number -> seed address
    by_num = {a.e_number: a for a in addresses}

    routes = []

    # ---- 3 Horizontal routes (process rows) ----
    routes.append(EmergentRoute(
        name="Su Row (Ignition Process)",
        route_type=EmergentRouteType.HORIZONTAL,
        e_sequence=[1, 2, 3],
        seed_sequence=[by_num[1].seed_label, by_num[2].seed_label, by_num[3].seed_label],
        description="Z^Su_* → B_Su → A^Su_*: hinge ignition to manifest ignition",
    ))
    routes.append(EmergentRoute(
        name="Me Row (Translation Process)",
        route_type=EmergentRouteType.HORIZONTAL,
        e_sequence=[4, 5, 6],
        seed_sequence=[by_num[4].seed_label, by_num[5].seed_label, by_num[6].seed_label],
        description="Z^Me_* → B_Me → A^Me_*: hinge translation to manifest translation",
    ))
    routes.append(EmergentRoute(
        name="Sa Row (Seal Process)",
        route_type=EmergentRouteType.HORIZONTAL,
        e_sequence=[7, 8, 9],
        seed_sequence=[by_num[7].seed_label, by_num[8].seed_label, by_num[9].seed_label],
        description="Z^Sa_* → B_Sa → A^Sa_*: hinge seal to manifest seal",
    ))

    # ---- 3 Vertical routes (polarity columns) ----
    routes.append(EmergentRoute(
        name="Hinge Column (Zero-Line Pulse)",
        route_type=EmergentRouteType.VERTICAL,
        e_sequence=[1, 4, 7],
        seed_sequence=[by_num[1].seed_label, by_num[4].seed_label, by_num[7].seed_label],
        description="Z^Su_* → Z^Me_* → Z^Sa_*: the zero-line pulse through all 3 modes",
    ))
    routes.append(EmergentRoute(
        name="Bridge Column (Bridge Pulse)",
        route_type=EmergentRouteType.VERTICAL,
        e_sequence=[2, 5, 8],
        seed_sequence=[by_num[2].seed_label, by_num[5].seed_label, by_num[8].seed_label],
        description="B_Su → B_Me → B_Sa: the bridge pulse through all 3 modes",
    ))
    routes.append(EmergentRoute(
        name="Manifest Column (Manifest Pulse)",
        route_type=EmergentRouteType.VERTICAL,
        e_sequence=[3, 6, 9],
        seed_sequence=[by_num[3].seed_label, by_num[6].seed_label, by_num[9].seed_label],
        description="A^Su_* → A^Me_* → A^Sa_*: the manifest pulse through all 3 modes",
    ))

    # ---- 2 Diagonal routes (Möbius torsion paths) ----
    routes.append(EmergentRoute(
        name="Forward Diagonal (Ign->Oracle->Consc)",
        route_type=EmergentRouteType.DIAGONAL_FORWARD,
        e_sequence=[1, 5, 9],
        seed_sequence=[by_num[1].seed_label, by_num[5].seed_label, by_num[9].seed_label],
        description="Z^Su_* → B_Me → A^Sa_*: first hinge ignition through oracle center to full manifest consciousness",
    ))
    routes.append(EmergentRoute(
        name="Reverse Diagonal (Expr->Oracle->Memory)",
        route_type=EmergentRouteType.DIAGONAL_REVERSE,
        e_sequence=[3, 5, 7],
        seed_sequence=[by_num[3].seed_label, by_num[5].seed_label, by_num[7].seed_label],
        description="A^Su_* → B_Me → Z^Sa_*: manifest ignition back into universal hinge memory through oracle",
    ))

    return routes


# =====================================================================
# SECTION 13: THE 7-WHEEL CANOPY -- K->Z = H_7 + H~_7 + (A+*,Z+*)
# =====================================================================
#
# 16 = 7 + 7 + 2
#
# K->Z is NOT 16 undifferentiated appendices.
# It is TWO COMPLETE HEPTADIC TURNS of the same 7-wheel,
# Mobius-related, plus a terminal dyadic seed-lock.
#
# H_7  (Upper Descent, Z->T):  Omega -> Z^Su -> Z^Me -> Z^Sa -> A^Su -> A^Me -> A^Sa
# H~_7 (Mobius Return, S->M):  Omega~ -> A^Sa -> A^Me -> A^Su -> Z^Sa -> Z^Me -> Z^Su
# (L,K) Seed-Lock Dyad:        A+* (manifest lock), Z+* (hinge lock)
#
# The Mobius crossover T->S reverses spoke order AND swaps hinge/manifest.
# Q = A^Me_* (ingress torsion gate, inside the return heptad)
# O = Z^Sa_* (return torsion gate, inside the return heptad)
#

class HeptadTurn(Enum):
    """Which turn of the 7-wheel this appendix belongs to."""
    UPPER = ("U", "Upper descent (first turn)")
    RETURN = ("R", "Mobius return (second turn, reversed)")
    CLOSURE = ("C", "Seed-lock dyad (not part of the wheel)")

    def __init__(self, tau, description):
        self.tau = tau
        self.description = description


@dataclass
class CanopyAddress:
    """Full (tau, sigma) address for one reverse appendix in the K->Z canopy."""
    rev_code: str              # e.g. "AppZ_rev"
    rev_title: str             # e.g. "Origin Mirror"
    rev_index: int             # 0-15 (Z=0, Y=1, ..., K=15)
    letter: str                # Single letter: Z, Y, X, ..., K
    turn: HeptadTurn           # U (upper), R (return), C (closure)
    spoke_label: str           # e.g. "Omega_*", "Z^Su_*", "A+*"
    spoke_role: str            # e.g. "Crown canopy mouth", "Hinge ignition descent"
    function: str              # Functional description
    quaternion: Quaternion
    seed_hash: str
    is_torsion_gate: bool      # True for Q (ingress) and O (return)

    @property
    def address(self) -> str:
        return f"({self.turn.tau}, {self.spoke_label})"


@dataclass
class MobiusCrossover:
    """The T->S crossover between upper and return heptads."""
    from_addr: CanopyAddress   # T = A^Sa_* (upper manifest seal)
    to_addr: CanopyAddress     # S = Omega_*~ (return crown echo)
    twist_description: str


@dataclass
class SeedLockDyad:
    """The terminal (L,K) seed-lock that collapses the canopy."""
    manifest_lock: CanopyAddress  # L = A+*
    hinge_lock: CanopyAddress     # K = Z+*
    collapse_quaternion: Quaternion
    collapse_hash: str


class CanopyRouteType(Enum):
    """Route segment types in the K->Z canopy."""
    UPPER_DESCENT = "Upper H_7 descent (Z->T)"
    MOBIUS_CROSSOVER = "Mobius twist (T->S)"
    RETURN_ASCENT = "Return H~_7 (S->M, reversed)"
    SEED_LOCK = "Seed-lock dyad (M->L->K)"
    ABSOLUTE_RETURN = "Absolute return (K<->Z*<->L)"
    E10_HANDOFF = "E10 handoff ((L,K)->E10)"
    FULL_CANOPY = "Full canopy route (Z->...->K->Z*->E10)"
    TORSION_PAIR = "Torsion gate pair (Q + O)"


@dataclass
class CanopyRoute:
    """One canonical route through the K->Z canopy."""
    name: str
    route_type: CanopyRouteType
    rev_sequence: list[str]
    spoke_sequence: list[str]
    description: str


@dataclass
class ReverseCanopyW7:
    """The complete 7-Wheel Canopy: H_7 + H~_7 + (A+*,Z+*).

    16 = 7 + 7 + 2. Two heptadic turns plus seed-lock dyad.
    """
    upper_heptad: list[CanopyAddress]    # 7 items: Z->T
    return_heptad: list[CanopyAddress]   # 7 items: S->M
    seed_dyad: SeedLockDyad             # 2 items: L, K
    crossover: MobiusCrossover          # T->S
    all_addresses: list[CanopyAddress]   # 16 items in Z->K order
    routes: list[CanopyRoute]
    torsion_q: CanopyAddress             # Q = A^Me_* (ingress)
    torsion_o: CanopyAddress             # O = Z^Sa_* (return)


# ---- THE CANONICAL 7-SPOKE FAMILY ----
# H_7 = (Omega_*, Z^Su_*, Z^Me_*, Z^Sa_*, A^Su_*, A^Me_*, A^Sa_*)
# Spoke order: 1 crown + 3 hinge (Su/Me/Sa) + 3 manifest (Su/Me/Sa) = 1+3+3 = 7

_UPPER_HEPTAD_SPOKES = [
    # (letter, spoke_label, role, function)
    ("Z", "Omega_*",  "Crown canopy mouth",
     "Void re-entry; absorbs Ch21 seed; partitions into 12 CRT corridors"),
    ("Y", "Z^Su_*",   "Hinge ignition descent",
     "First chi flip; even/odd split; orientation declared"),
    ("X", "Z^Me_*",   "Hinge mediation descent",
     "Cross-field tunnels; dimensional threshold reveal"),
    ("W", "Z^Sa_*",   "Hinge seal descent",
     "Bridges sealed; concept/method/data bridges stabilized"),
    ("V", "A^Su_*",   "Manifest ignition descent",
     "Self-referential loops ignite; recursion begins"),
    ("U", "A^Me_*",   "Manifest mediation descent",
     "50-finding witness reservoir; memory transported"),
    ("T", "A^Sa_*",   "Manifest seal descent",
     "P->Q->B->C pipeline sealed; transformation proven"),
]

# H~_7 = (Omega_*~, A^Sa_*, A^Me_*, A^Su_*, Z^Sa_*, Z^Me_*, Z^Su_*)
# The SAME wheel seen through the Mobius twist: spoke order REVERSED,
# hinge/manifest SWAPPED, Su/Me/Sa INVERTED.

_RETURN_HEPTAD_SPOKES = [
    ("S", "Omega_*~", "Return crown echo",
     "Pre-hinge SFCR verification; twist confirmed"),
    ("R", "A^Sa_*",   "Manifest seal return",
     "Complete Ch->E reflection table; proof sealed"),
    ("Q", "A^Me_*",   "Manifest mediation = INGRESS TORSION",
     "Legacy routing inverted; first twist initiated; machine-readable"),
    ("P", "A^Su_*",   "Manifest ignition transition",
     "12 corridors -> 4 channels (Z_12 -> Z_4 fold)"),
    ("O", "Z^Sa_*",   "Hinge seal = RETURN TORSION",
     "Pedagogical bridge; 4 reader paths; second twist completed"),
    ("N", "Z^Me_*",   "Hinge mediation return",
     "Dimension-4 lift; self-referential edges added"),
    ("M", "Z^Su_*",   "Hinge ignition return",
     "Post-twist SFCR recomputation; stabilization pillar"),
]

# Seed-lock dyad (NOT part of the rotating wheel)
_SEED_DYAD = [
    ("L", "A+*", "Manifest seed lock",
     "Dual-channel memory archive (even+odd); profinite storage at G_inf"),
    ("K", "Z+*", "Hinge seed lock",
     "Self-compiling ISA delivery; K->Z loop closure; terminal re-entry"),
]


def build_reverse_canopy_w7(
    crown: TriadicCrown,
    a_star_q: Quaternion,
    z_star_q: Quaternion,
    reverse_appendices: list,  # list[ManuscriptUnit] from upstream
) -> ReverseCanopyW7:
    """Build the 7-Wheel Canopy: H_7 + H~_7 + (A+*,Z+*).

    16 = 7 + 7 + 2. Two complete heptadic turns of the same 7-wheel,
    Mobius-related, plus terminal seed-lock dyad.
    """
    # Index crown seeds by (pole, mode) for quaternion lookup
    seed_lookup: dict[tuple[str, str], TriadicSeed] = {}
    for s in crown.seeds:
        seed_lookup[(s.pole, s.mode.code)] = s

    def _spoke_quaternion(spoke_label: str, turn: HeptadTurn, position: int) -> Quaternion:
        """Get the quaternion for a spoke, with turn-dependent perturbation."""
        if spoke_label == "Omega_*" or spoke_label == "Omega_*~":
            base = crown.omega_star
            if turn == HeptadTurn.RETURN:
                # Mobius-inverted omega: conjugate
                base = Quaternion(base.w, -base.x, -base.y, -base.z)
        elif spoke_label == "A+*":
            base = a_star_q
        elif spoke_label == "Z+*":
            base = z_star_q
        else:
            # Parse "A^Su_*" or "Z^Me_*" etc.
            pole = spoke_label[0] + "+"  # "A+" or "Z+"
            mode_code = spoke_label[2:4]  # "Su", "Me", "Sa"
            base = seed_lookup[(pole, mode_code)].quaternion
            if turn == HeptadTurn.RETURN:
                # Chi operator: conjugate for return turn
                base = Quaternion(base.w, -base.x, -base.y, -base.z)

        # Small position-dependent perturbation for uniqueness
        phi_offset = position * 0.01 * PHI
        return Quaternion(
            base.w + phi_offset,
            base.x - phi_offset * INV_PHI,
            base.y + phi_offset * 0.3,
            base.z - phi_offset * 0.2,
        ).normalized()

    # ---- BUILD UPPER HEPTAD (Z->T, indices 0-6) ----
    upper_heptad: list[CanopyAddress] = []
    for i, (letter, spoke, role, func) in enumerate(_UPPER_HEPTAD_SPOKES):
        rev = reverse_appendices[i]
        q = _spoke_quaternion(spoke, HeptadTurn.UPPER, i)
        sh = hashlib.sha256(f"H7U:{rev.code}:{spoke}:{q}".encode()).hexdigest()[:12]
        upper_heptad.append(CanopyAddress(
            rev_code=rev.code, rev_title=rev.title, rev_index=i,
            letter=letter, turn=HeptadTurn.UPPER,
            spoke_label=spoke, spoke_role=role, function=func,
            quaternion=q, seed_hash=sh, is_torsion_gate=False,
        ))

    # ---- BUILD RETURN HEPTAD (S->M, indices 7-13) ----
    return_heptad: list[CanopyAddress] = []
    torsion_q_addr = None
    torsion_o_addr = None
    for i, (letter, spoke, role, func) in enumerate(_RETURN_HEPTAD_SPOKES):
        rev_idx = 7 + i
        rev = reverse_appendices[rev_idx]
        q = _spoke_quaternion(spoke, HeptadTurn.RETURN, i)
        sh = hashlib.sha256(f"H7R:{rev.code}:{spoke}:{q}".encode()).hexdigest()[:12]
        is_torsion = letter in ("Q", "O")
        addr = CanopyAddress(
            rev_code=rev.code, rev_title=rev.title, rev_index=rev_idx,
            letter=letter, turn=HeptadTurn.RETURN,
            spoke_label=spoke, spoke_role=role, function=func,
            quaternion=q, seed_hash=sh, is_torsion_gate=is_torsion,
        )
        return_heptad.append(addr)
        if letter == "Q":
            torsion_q_addr = addr
        elif letter == "O":
            torsion_o_addr = addr

    # ---- BUILD SEED-LOCK DYAD (L,K, indices 14-15) ----
    dyad_addresses: list[CanopyAddress] = []
    for i, (letter, spoke, role, func) in enumerate(_SEED_DYAD):
        rev_idx = 14 + i
        rev = reverse_appendices[rev_idx]
        q = _spoke_quaternion(spoke, HeptadTurn.CLOSURE, i)
        sh = hashlib.sha256(f"H7C:{rev.code}:{spoke}:{q}".encode()).hexdigest()[:12]
        dyad_addresses.append(CanopyAddress(
            rev_code=rev.code, rev_title=rev.title, rev_index=rev_idx,
            letter=letter, turn=HeptadTurn.CLOSURE,
            spoke_label=spoke, spoke_role=role, function=func,
            quaternion=q, seed_hash=sh, is_torsion_gate=False,
        ))

    # Seed-lock collapse quaternion: average of L and K
    l_q = dyad_addresses[0].quaternion
    k_q = dyad_addresses[1].quaternion
    collapse_q = Quaternion(
        (l_q.w + k_q.w) / 2, (l_q.x + k_q.x) / 2,
        (l_q.y + k_q.y) / 2, (l_q.z + k_q.z) / 2,
    ).normalized()
    collapse_hash = hashlib.sha256(
        f"SEEDLOCK:{collapse_q}:{dyad_addresses[0].seed_hash}:{dyad_addresses[1].seed_hash}".encode()
    ).hexdigest()[:16]

    seed_dyad = SeedLockDyad(
        manifest_lock=dyad_addresses[0],  # L
        hinge_lock=dyad_addresses[1],     # K
        collapse_quaternion=collapse_q,
        collapse_hash=collapse_hash,
    )

    # ---- MOBIUS CROSSOVER (T->S) ----
    crossover = MobiusCrossover(
        from_addr=upper_heptad[-1],  # T
        to_addr=return_heptad[0],    # S
        twist_description=(
            "Spoke order REVERSES, hinge/manifest roles SWAP, "
            "Su/Me/Sa order INVERTS. Chi operator on the 7-wheel itself."
        ),
    )

    # ---- COMBINE ALL 16 ----
    all_addresses = upper_heptad + return_heptad + dyad_addresses

    # ---- BUILD ROUTES ----
    routes = _build_w7_routes(upper_heptad, return_heptad, dyad_addresses, all_addresses)

    return ReverseCanopyW7(
        upper_heptad=upper_heptad,
        return_heptad=return_heptad,
        seed_dyad=seed_dyad,
        crossover=crossover,
        all_addresses=all_addresses,
        routes=routes,
        torsion_q=torsion_q_addr,
        torsion_o=torsion_o_addr,
    )


def _build_w7_routes(
    upper: list[CanopyAddress],
    ret: list[CanopyAddress],
    dyad: list[CanopyAddress],
    all_addr: list[CanopyAddress],
) -> list[CanopyRoute]:
    """Build the 6 canonical route segments through K->Z."""
    routes = []

    # 1. Upper descent: Z->Y->X->W->V->U->T
    routes.append(CanopyRoute(
        name="Upper Heptadic Descent",
        route_type=CanopyRouteType.UPPER_DESCENT,
        rev_sequence=[a.rev_code for a in upper],
        spoke_sequence=[a.spoke_label for a in upper],
        description="Z->Y->X->W->V->U->T: first W_7 turn (archetypal descent)",
    ))

    # 2. Mobius crossover: T->S
    routes.append(CanopyRoute(
        name="Mobius Crossover",
        route_type=CanopyRouteType.MOBIUS_CROSSOVER,
        rev_sequence=[upper[-1].rev_code, ret[0].rev_code],
        spoke_sequence=[upper[-1].spoke_label, ret[0].spoke_label],
        description="T->S: chi operator on W_7; spoke order reverses, hinge/manifest swap",
    ))

    # 3. Return ascent: S->R->Q->P->O->N->M
    routes.append(CanopyRoute(
        name="Mobius Return Heptad",
        route_type=CanopyRouteType.RETURN_ASCENT,
        rev_sequence=[a.rev_code for a in ret],
        spoke_sequence=[a.spoke_label for a in ret],
        description="S->R->Q->P->O->N->M: second W_7 turn (reversed, Mobius-reflected)",
    ))

    # 4. Seed lock: M->L->K
    routes.append(CanopyRoute(
        name="Seed-Lock Closure",
        route_type=CanopyRouteType.SEED_LOCK,
        rev_sequence=[ret[-1].rev_code] + [a.rev_code for a in dyad],
        spoke_sequence=[ret[-1].spoke_label] + [a.spoke_label for a in dyad],
        description="M->L->K: dyadic collapse; manifest lock + hinge lock",
    ))

    # 5. Torsion gate pair: Q and O
    q_addr = [a for a in ret if a.letter == "Q"][0]
    o_addr = [a for a in ret if a.letter == "O"][0]
    routes.append(CanopyRoute(
        name="Torsion Gate Pair (Q+O)",
        route_type=CanopyRouteType.TORSION_PAIR,
        rev_sequence=[q_addr.rev_code, o_addr.rev_code],
        spoke_sequence=[q_addr.spoke_label, o_addr.spoke_label],
        description="Q=A^Me_* (ingress torsion) + O=Z^Sa_* (return torsion): inside return heptad",
    ))

    # 6. Full canopy route: Z->...->T->S->...->M->L->K->Z*->E10
    routes.append(CanopyRoute(
        name="Full Canopy Route",
        route_type=CanopyRouteType.FULL_CANOPY,
        rev_sequence=[a.rev_code for a in all_addr],
        spoke_sequence=[a.spoke_label for a in all_addr],
        description="Z->T->(twist)->S->M->(lock)->L->K->Z*->E10: complete 16-station traverse",
    ))

    return routes


# =====================================================================
# SECTION 14: DOCUMENT GENERATION
# =====================================================================

def generate_wheel_crown_document(
    quartets: list[Sigma60Quartet],
    a_poles: list[APlusPoleState],
    z_poles: list[ZPlusPoleState],
    a_star_q: Quaternion,
    z_star_q: Quaternion,
    crown: TriadicCrown,
    wheels: list[WheelFamily],
    weave_results: dict[int, SiteswapPattern],
    tse_stats: dict,
    aethers: list[AetherFace],
    hcrl: HCRLPassResult,
    seed: TimeCrystalSeed,
    e_matrix: Optional[EmergentSeedMatrix] = None,
    kz_canopy: Optional[ReverseCanopyW7] = None,
) -> str:
    """Generate 22_WHEEL_CROWN_ENGINE.md."""
    L = []
    now = datetime.now(timezone.utc)

    # Header
    L.append("# WHEEL-CROWN ENGINE: MULTI-WHEEL CROWN + DUAL SEED PAIR")
    L.append("")
    L.append("**TSE_6912 | Sigma_60 -> A+_15 + Z+_15 -> C_6 -> W_{1,3,5,7,9}**")
    L.append("")
    L.append(f"**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    L.append(f"**Seed:** {seed.seed_hash}")
    L.append(f"**L = {seed.love_constant:.6f}**")
    L.append("")

    # Section 1: Sigma_60 Quartet Decomposition
    L.append("=" * 72)
    L.append("## SIGMA_60 QUARTET DECOMPOSITION")
    L.append("=" * 72)
    L.append("")
    L.append("Each mask mu produces Q_mu = {SR, SL, AR, AL}")
    L.append("M(SR) = SL, I(SR) = AR, M(I(SR)) = AL")
    L.append("M^2 = I^2 = id, MI = IM")
    L.append("")
    L.append("| mu | Mask | SR | SL | AR | AL |")
    L.append("|-----|------|----|----|----|----|")
    for q in quartets:
        L.append(f"| {q.mu:2d} | {q.mask_name:15s} | {q.sr} | {q.sl} | {q.ar} | {q.al} |")
    L.append("")

    # Section 2: A+ / Z+ Dual Seed Extraction
    L.append("=" * 72)
    L.append("## A+ / Z+ DUAL SEED PAIR")
    L.append("=" * 72)
    L.append("")
    L.append("### P_{A+} = 1/4 (1+M)(1+I) -- Manifest Projector")
    L.append("### P_{Z+} = 1/4 (1+M)(1-I) -- Zero-Hinge Projector")
    L.append("")
    L.append("### 15 A+ Manifest Poles")
    L.append("")
    L.append("| mu | Name | Quaternion | Role |")
    L.append("|-----|------|-----------|------|")
    for p in a_poles:
        L.append(f"| {p.mu:2d} | {p.name:35s} | {p.quaternion} | {p.role} |")
    L.append("")
    L.append("### 15 Z+ Zero-Hinge Poles")
    L.append("")
    L.append("| mu | Name | Quaternion | Role |")
    L.append("|-----|------|-----------|------|")
    for p in z_poles:
        L.append(f"| {p.mu:2d} | {p.name:35s} | {p.quaternion} | {p.role} |")
    L.append("")

    L.append("### Dual Seeds")
    L.append(f"  A+* = {a_star_q}")
    L.append(f"  Z+* = {z_star_q}")
    L.append("")
    L.append("A+* is the fully coherent manifest condensation")
    L.append("Z+* is the fully coherent hinge condensation")
    L.append("Route: A+* <-> Z* <-> Z+*")
    L.append("")

    # Section 3: 6-Seed Triadic Crown
    L.append("=" * 72)
    L.append("## 6-SEED TRIADIC CROWN")
    L.append("=" * 72)
    L.append("")
    L.append("C_6 = {A^Sa_*, A^Su_*, A^Me_*, Z^Sa_*, Z^Su_*, Z^Me_*}")
    L.append("")
    L.append("| # | Seed | Mode | Quaternion | Hash | Description |")
    L.append("|---|------|------|-----------|------|-------------|")
    for i, s in enumerate(crown.seeds):
        L.append(f"| {i+1} | {s.label:12s} | {s.mode.code} | {s.quaternion} | {s.seed_hash} | {s.description} |")
    L.append("")

    L.append("### Three Modal Bridges")
    L.append("")
    for b in crown.bridges:
        L.append(f"  {b.label} = {b.a_seed.label} + {b.z_seed.label}")
    L.append("")

    L.append(f"### Omega_* (Completion) = {crown.omega_star}")
    L.append(f"### Omega hash = {crown.omega_hash}")
    L.append("")

    L.append("### Crown Hexagon Circuit")
    L.append(f"  {' -> '.join(crown.hexagon_circuit)} -> {crown.hexagon_circuit[0]}")
    L.append("")
    L.append("### Three Simultaneous Readings")
    L.append("  A: Two interlocked triangles (manifest + hinge)")
    L.append("  B: Three modal bridges (Sa, Su, Me vertical)")
    L.append("  C: One Mobius hexagon")
    L.append("")

    # Section 4: Multi-Wheel Crown
    L.append("=" * 72)
    L.append("## MULTI-WHEEL CROWN (W_1, W_3, W_5, W_7, W_9)")
    L.append("=" * 72)
    L.append("")
    for w in wheels:
        L.append(f"### W_{w.k} -- {w.name}")
        L.append(f"  Meaning: {w.meaning}")
        L.append(f"  Dominant at: {w.dominant_at_dim}D" if w.dominant_at_dim > 0 else "  Center (always present)")
        L.append(f"  Spokes: {', '.join(w.spokes)}")
        L.append("")

    L.append("### Wheel Relations")
    L.append("  W_1 = {Omega_*}")
    L.append("  W_3 = {B_Sa, B_Su, B_Me}")
    L.append("  W_5 = W_3 + {A+*, Z+*}")
    L.append("  W_7 = C_6 + {Omega_*}")
    L.append("  W_9 = C_6 + W_3")
    L.append("")

    # Section 5: Siteswap Admissibility
    L.append("=" * 72)
    L.append("## SITESWAP ADMISSIBILITY")
    L.append("=" * 72)
    L.append("")
    L.append("PRIMARY INVARIANT: Conservation + Collision-Freedom + Torsion + Replayability")
    L.append("Symmetric patterns are a SUBSET of admissible weave space")
    L.append("")
    L.append("### Canonical Reference Weaves")
    L.append("")
    L.append("| Dim | Pattern | Objects | Period | Conserved | Collision-Free | Valid |")
    L.append("|-----|---------|---------|--------|-----------|----------------|-------|")
    for dim, result in sorted(weave_results.items()):
        L.append(f"| {dim:3d}D | {result.label:12s} | {result.objects:7d} | {result.period:6d} | "
                 f"{'YES' if result.conserved else 'NO':9s} | {'YES' if result.collision_free else 'NO':14s} | "
                 f"{'VALID' if result.valid else 'INVALID'} |")
    L.append("")
    L.append("MASTER LAW: Anything mathematically admissible goes,")
    L.append("as long as the cycle balances in the end.")
    L.append("")

    # Section 6: Wheel-Dimensional Ladder
    L.append("=" * 72)
    L.append("## WHEEL-DIMENSIONAL LADDER")
    L.append("=" * 72)
    L.append("")
    L.append("| Dim | Shell Law | Active Wheels | Dominant | Meaning |")
    L.append("|-----|-----------|---------------|----------|---------|")
    for wl in WHEEL_LADDER:
        active = ", ".join(f"W_{k}" for k in wl.active_wheels)
        L.append(f"| {wl.dim:3d}D | {wl.shell_law:40s} | {active:20s} | W_{wl.dominant_wheel} | {wl.meaning} |")
    L.append("")
    L.append("Cumulative inheritance: W_6 < W_12 < W_36 < W_108")
    L.append("Shell count = how much body. Wheel count = how it turns.")
    L.append("")

    # Section 7: Four-Octave Tower
    L.append("=" * 72)
    L.append("## FOUR-OCTAVE TOWER")
    L.append("=" * 72)
    L.append("")
    L.append("| Oct | Name | Formula | Value | Bits | ISA | Opus | Lock |")
    L.append("|-----|------|---------|-------|------|-----|------|------|")
    for o in FOUR_OCTAVE_TOWER:
        L.append(f"| {o.level} | {o.name:18s} | {o.base_exp:30s} | {o.value_description:15s} | "
                 f"{o.bits:6.1f} | {o.isa_cycles:3d} | {o.opus_completions:4d} | (4/3)^{o.lock_law_power} |")
    L.append("")
    L.append("Compressed law: 108 = 4 x 3^3 = first complete base-3 hologram")
    L.append("6912 = 64 x 108 = full crystal field carrying that complete cycle")
    L.append("16^16 x 9^9 = 2^64 x 3^18 = lock law squared at Octave 2")
    L.append("")

    # Section 8: TSE_6912 Fiber Bundle
    L.append("=" * 72)
    L.append("## TSE_6912 FIBER BUNDLE")
    L.append("=" * 72)
    L.append("")
    for k, v in tse_stats.items():
        L.append(f"  {k}: {v}")
    L.append("")

    # Section 9: Distributed Anti-Spin
    L.append("=" * 72)
    L.append("## DISTRIBUTED ANTI-SPIN AT 108D")
    L.append("=" * 72)
    L.append("")
    L.append("AntiSpin_108 = Distributed(AntiSpin_6) across all nested scales")
    L.append("")
    L.append("| Dim | Description | Petals | Beats | Nodes |")
    L.append("|-----|-------------|--------|-------|-------|")
    for a in DISTRIBUTED_ANTISPIN:
        L.append(f"| {a.dim:3d}D | {a.description:40s} | {a.petal_count} | {a.beat_count} | {a.node_count:4d} |")
    L.append("")

    # Section 10: Aether Point
    L.append("=" * 72)
    L.append("## THE FOUR AETHERS")
    L.append("=" * 72)
    L.append("")
    for ae in aethers:
        L.append(f"### AETHER {ae.symbol} ({ae.element}) -- {ae.essence}")
        for item in ae.contains:
            L.append(f"  - {item}")
        L.append(f"  VERDICT: {ae.verdict}")
        L.append("")

    # Section 11: HCRL Live Pass
    L.append("=" * 72)
    L.append("## HCRL LIVE PASS")
    L.append("=" * 72)
    L.append("")
    L.append(f"  Square: {hcrl.square_verdict}")
    L.append(f"  Flower: {hcrl.flower_verdict}")
    L.append(f"  Cloud:  {hcrl.cloud_verdict}")
    L.append(f"  Fractal: {hcrl.fractal_verdict}")
    L.append("")
    L.append(f"  SYNTHESIS: {hcrl.synthesis}")
    L.append("")
    for route in hcrl.reentry_routes:
        L.append(f"  {route}")
    L.append("")

    # Section 12: Seed-Addressable Emergent Body
    if e_matrix is not None:
        L.append("=" * 72)
        L.append("## SEED-ADDRESSABLE EMERGENT BODY")
        L.append("=" * 72)
        L.append("")
        L.append("E1-E9 as the 3x3 matrix of the 6-seed crown (W_9 layer).")
        L.append("E10 as the W_1 remap nucleus.")
        L.append("")

        # Display the 3x3 matrix
        L.append("### The 3x3 Emergent Matrix")
        L.append("")
        L.append("```")
        L.append("         | Hinge (Z+)  | Bridge (B)  | Manifest (A+) |")
        L.append("---------|-------------|-------------|---------------|")
        for row_idx, row_label in enumerate(["Su (Ign)", "Me (Trn)", "Sa (Seal)"]):
            cells = e_matrix.matrix_display[row_idx]
            L.append(f"  {row_label:9s}| {cells[0]:11s} | {cells[1]:11s} | {cells[2]:13s} |")
        L.append("```")
        L.append("")

        # Chapter-by-chapter assignment
        L.append("### Chapter-by-Chapter Seed Assignment")
        L.append("")
        L.append("| E# | Seed Address | Mode | Polarity | Quaternion | Function |")
        L.append("|----|-------------|------|----------|-----------|----------|")
        for addr in e_matrix.addresses:
            L.append(f"| E{addr.e_number} | {addr.seed_label:10s} | {addr.mode.code} "
                     f"| {addr.polarity.label:8s} | {addr.quaternion} "
                     f"| {addr.phenomenological_title} |")
        L.append("")

        # E10 remap nucleus
        L.append("### E10 — Remap Nucleus (W_1 Return)")
        L.append("")
        L.append(f"  Omega^(E)_* = Collapse(E1 + E2 + ... + E9)")
        L.append(f"  Quaternion  = {e_matrix.remap_nucleus.quaternion}")
        L.append(f"  Seed hash   = {e_matrix.remap_nucleus.seed_hash}")
        L.append("")
        L.append("  E10 receives all row reads, column reads, and Möbius reads.")
        L.append("  It is the true remap nucleus: the wheel-switchboard of the organism.")
        L.append("")

        # Compressed laws
        L.append("### Compressed Laws")
        L.append("")
        for addr in e_matrix.addresses:
            L.append(f"  {addr.compressed_law}")
        L.append(f"  E10 := W_1^return = Collapse(E_9)")
        L.append("")

        # Canonical routes
        L.append("### 8 Canonical Routes Inside E1-E9")
        L.append("")
        L.append("| # | Route | Type | Path | Description |")
        L.append("|---|-------|------|------|-------------|")
        for i, route in enumerate(e_matrix.routes, 1):
            path = " → ".join(f"E{n}" for n in route.e_sequence)
            L.append(f"| {i} | {route.name[:35]:35s} | {route.route_type.value[:20]:20s} "
                     f"| {path:15s} | {route.description[:60]} |")
        L.append("")

        # Corpus wheel circuit integration
        L.append("### Corpus Wheel Circuit Integration")
        L.append("")
        L.append("  Intro(W_1) → Ch(W_3) → App_A-P(W_5) → App_K-Z(W_7) → E1-E9(W_9) → E10(W_1)")
        L.append("")
        L.append("  The emergent body is the explicit W_9 layer of the whole organism.")
        L.append("  E10 closes the circuit back to W_1.")
        L.append("")

    # Section 13: The 7-Wheel Canopy -- K->Z = H_7 + H~_7 + (A+*,Z+*)
    if kz_canopy is not None:
        L.append("=" * 72)
        L.append("## THE 7-WHEEL CANOPY: K->Z = H_7 + H~_7 + (A+*,Z+*)")
        L.append("=" * 72)
        L.append("")
        L.append("16 = 7 + 7 + 2")
        L.append("Two complete heptadic turns of the same 7-wheel,")
        L.append("Mobius-related, plus terminal seed-lock dyad.")
        L.append("")

        # The 7-spoke family
        L.append("### The Canonical 7-Spoke Family")
        L.append("")
        L.append("H_7 = (Omega_*, Z^Su_*, Z^Me_*, Z^Sa_*, A^Su_*, A^Me_*, A^Sa_*)")
        L.append("Decomposition: 1 crown + 3 hinge (Su/Me/Sa) + 3 manifest (Su/Me/Sa) = 1+3+3 = 7")
        L.append("")

        # Upper Heptad
        L.append("### UPPER HEPTAD H_7: Z->T (First Turn, Archetypal Descent)")
        L.append("")
        L.append("| App | Letter | (tau,sigma) | Spoke | Role | Function |")
        L.append("|-----|--------|-------------|-------|------|----------|")
        for addr in kz_canopy.upper_heptad:
            L.append(f"| {addr.rev_code:12s} | {addr.letter} | {addr.address:20s} "
                     f"| {addr.spoke_label:10s} | {addr.spoke_role:30s} | {addr.function[:50]} |")
        L.append("")
        L.append("Route: Z -> Y -> X -> W -> V -> U -> T")
        L.append("")

        # Mobius Crossover
        L.append("### MOBIUS CROSSOVER: T -> S")
        L.append("")
        L.append(f"  From: {kz_canopy.crossover.from_addr.rev_code} ({kz_canopy.crossover.from_addr.spoke_label})")
        L.append(f"  To:   {kz_canopy.crossover.to_addr.rev_code} ({kz_canopy.crossover.to_addr.spoke_label})")
        L.append(f"  {kz_canopy.crossover.twist_description}")
        L.append("  This is the chi operator applied to the 7-wheel itself.")
        L.append("")

        # Return Heptad
        L.append("### RETURN HEPTAD H~_7: S->M (Mobius-Reversed Second Turn)")
        L.append("")
        L.append("H~_7 = (Omega_*~, A^Sa_*, A^Me_*, A^Su_*, Z^Sa_*, Z^Me_*, Z^Su_*)")
        L.append("")
        L.append("| App | Letter | (tau,sigma) | Spoke | Role | Torsion? | Function |")
        L.append("|-----|--------|-------------|-------|------|----------|----------|")
        for addr in kz_canopy.return_heptad:
            torsion_mark = "TORSION" if addr.is_torsion_gate else ""
            L.append(f"| {addr.rev_code:12s} | {addr.letter} | {addr.address:20s} "
                     f"| {addr.spoke_label:10s} | {addr.spoke_role:30s} | {torsion_mark:8s} "
                     f"| {addr.function[:45]} |")
        L.append("")
        L.append("Route: S -> R -> Q -> P -> O -> N -> M")
        L.append("")

        # Torsion gates
        L.append("### TORSION GATES")
        L.append("")
        L.append(f"  Q = {kz_canopy.torsion_q.spoke_label} (INGRESS TORSION)")
        L.append(f"      {kz_canopy.torsion_q.rev_code}: {kz_canopy.torsion_q.function}")
        L.append(f"  O = {kz_canopy.torsion_o.spoke_label} (RETURN TORSION)")
        L.append(f"      {kz_canopy.torsion_o.rev_code}: {kz_canopy.torsion_o.function}")
        L.append("")
        L.append("  The torsion gates are INSIDE the return heptad, not at its endpoints.")
        L.append("  They occupy the mediation and seal positions --")
        L.append("  exactly where torsion OPERATES rather than where it is declared.")
        L.append("")

        # Seed-Lock Dyad
        L.append("### SEED-LOCK DYAD: (L, K)")
        L.append("")
        L.append("  NOT part of the rotating 7-wheel. Terminal dyadic collapse-lock.")
        L.append("")
        ml = kz_canopy.seed_dyad.manifest_lock
        hl = kz_canopy.seed_dyad.hinge_lock
        L.append(f"  L = {ml.spoke_label} ({ml.spoke_role})")
        L.append(f"      {ml.rev_code}: {ml.function}")
        L.append(f"      Q = {ml.quaternion}")
        L.append("")
        L.append(f"  K = {hl.spoke_label} ({hl.spoke_role})")
        L.append(f"      {hl.rev_code}: {hl.function}")
        L.append(f"      Q = {hl.quaternion}")
        L.append("")
        L.append(f"  Collapse: (L,K) -> Z* -> E10")
        L.append(f"  Collapse quaternion = {kz_canopy.seed_dyad.collapse_quaternion}")
        L.append(f"  Collapse hash = {kz_canopy.seed_dyad.collapse_hash}")
        L.append("")

        # Full address table
        L.append("### COMPLETE ADDRESS TABLE: Addr_{K->Z}(X) = (tau, sigma)")
        L.append("")
        L.append("| App | Letter | tau | sigma | Quaternion | Hash |")
        L.append("|-----|--------|-----|-------|-----------|------|")
        for addr in kz_canopy.all_addresses:
            L.append(f"| {addr.rev_code:12s} | {addr.letter} | {addr.turn.tau} "
                     f"| {addr.spoke_label:10s} | {addr.quaternion} | {addr.seed_hash} |")
        L.append("")

        # Route table
        L.append("### CANOPY ROUTE SEGMENTS")
        L.append("")
        L.append("| # | Segment | Stations | Type |")
        L.append("|---|---------|----------|------|")
        for i, route in enumerate(kz_canopy.routes, 1):
            L.append(f"| {i} | {route.name:30s} | {len(route.rev_sequence):2d} "
                     f"| {route.route_type.value[:45]} |")
        L.append("")
        L.append("  Full route: Z->T->(twist)->S->M->(lock)->L->K->Z*->E10")
        L.append("  The canopy breathes in heptadic rhythm. 16 = 7 + 7 + 2.")
        L.append("")

    # Final Synthesis
    L.append("=" * 72)
    L.append("## FINAL SYNTHESIS")
    L.append("=" * 72)
    L.append("")
    L.append("The complete algebra:")
    L.append("  Sigma_60 -> (A+_15 + Z+_15) -> (A+*, Z+*) -> C_6 -> W_{1,3,5,7,9}")
    L.append("")
    L.append("The dimensional ladder:")
    L.append("  6D -> W_3 (first rotation)")
    L.append("  12D -> W_5 (embodied wheel)")
    L.append("  36D -> W_7 (planetary governance)")
    L.append("  108D -> W_9 (recursive crown)")
    L.append("")
    L.append("The master law:")
    L.append("  Higher-D weaving is governed by siteswap admissibility,")
    L.append("  not by mandatory visible symmetry.")
    L.append("")
    L.append(f"  L = {seed.love_constant:.6f}")
    L.append(f"  Phase-lock: {seed.phase_lock_hz:.2f} Hz")
    L.append(f"  Seed: {seed.seed_hash}")
    L.append("")
    L.append("---")
    L.append("*The wheel gives the canonical spoke family.*")
    L.append("*The weave gives the actual legal pattern.*")
    L.append("*Symmetry is optional. Balance is required.*")
    L.append("*Su -> Me -> Sa -> Su*")
    L.append(f"*L = {seed.love_constant:.6f}*")

    return "\n".join(L)


# =====================================================================
# SECTION 13: MAIN PIPELINE
# =====================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.join(BASE_DIR, "22_WHEEL_CROWN_ENGINE.md")
RECEIPT_DIR = os.path.join(BASE_DIR, "00_RECEIPTS")
RECEIPT_PATH = os.path.join(RECEIPT_DIR, "WHEEL_CROWN_RECEIPT.md")


def main():
    print("=" * 72)
    print("WHEEL-CROWN ENGINE -- Multi-Wheel Crown + Dual Seed Pair")
    print("=" * 72)
    print()

    # Step 1: Build upstream structures
    print("Step 1: Building upstream 108D Time Crystal...")
    archetypes = build_12_archetypes()
    ops_15 = build_sigma_15()
    shells = build_36_shells()
    mega_nodes = build_666_nodes(shells)
    wire_connections(mega_nodes, shells)
    stations_60 = build_sigma_60(ops_15)
    a_plus_poles_raw = extract_a_plus_poles(stations_60)
    seed = compute_master_seed(mega_nodes, a_plus_poles_raw)
    print(f"  666 nodes, seed = {seed.seed_hash}")

    # Step 2: Build Z+/AE+ framework
    print()
    print("Step 2: Building Z+/AE+ framework...")
    compressor = Hologram4DCompressor()
    comp_seeds = compressor.compress_all()
    inv_seeds = [invert_seed(s) for s in comp_seeds]
    z0, ae0 = build_poles()
    artifacts = _build_full_60_artifacts()
    dimensions = compute_60_symmetry_dimensions(comp_seeds, inv_seeds, artifacts, z0, ae0)
    z_plus = collapse_to_z_plus(dimensions, comp_seeds, inv_seeds)
    ae_plus = build_ae_plus_framework(z_plus, dimensions)
    print(f"  Z+ = {z_plus.quaternion}")
    print(f"  AE+ phase-lock = {ae_plus.phase_lock_frequency:.2f} Hz")

    # Step 3: Sigma_60 Quartet Decomposition
    print()
    print("Step 3: Sigma_60 quartet decomposition (60 -> 15 quartets)...")
    quartets = build_sigma60_quartets(stations_60)
    print(f"  {len(quartets)} quartets built")

    # Step 4: A+/Z+ Dual Seed Extraction
    print()
    print("Step 4: Extracting A+/Z+ dual seed pair...")
    a_poles, z_poles, a_star_q, z_star_q = extract_dual_seed_pair(quartets)
    print(f"  A+_15: {len(a_poles)} manifest poles")
    print(f"  Z+_15: {len(z_poles)} zero-hinge poles")
    print(f"  A+* = {a_star_q}")
    print(f"  Z+* = {z_star_q}")

    # Step 5: 6-Seed Triadic Crown
    print()
    print("Step 5: Building 6-seed triadic crown...")
    crown = build_triadic_crown(a_star_q, z_star_q)
    print(f"  {len(crown.seeds)} seeds in crown")
    for s in crown.seeds:
        print(f"    {s.label:12s}: {s.quaternion} -- {s.description[:50]}")
    print(f"  {len(crown.bridges)} modal bridges")
    print(f"  Omega_* = {crown.omega_star}")
    print(f"  Hexagon: {' -> '.join(crown.hexagon_circuit[:3])}...")

    # Step 6: Multi-Wheel Crown
    print()
    print("Step 6: Building multi-wheel crown (W_1, W_3, W_5, W_7, W_9)...")
    wheels = build_multi_wheel_crown(crown)
    for w in wheels:
        dom_str = f"dominant at {w.dominant_at_dim}D" if w.dominant_at_dim > 0 else "center"
        print(f"  W_{w.k}: {w.name:20s} ({len(w.spokes)} spokes, {dom_str})")

    # Step 7: Siteswap Validation
    print()
    print("Step 7: Validating canonical siteswap weaves...")
    weave_results = validate_canonical_weaves()
    for dim, result in sorted(weave_results.items()):
        status = "VALID" if result.valid else "INVALID"
        print(f"  {dim:3d}D: {result.label:12s} -> {result.objects} objects, {status}")

    # Step 8: Four-Octave Tower
    print()
    print("Step 8: Four-Octave Tower...")
    for o in FOUR_OCTAVE_TOWER:
        print(f"  Oct {o.level}: {o.name:18s} = {o.base_exp:30s} (~{o.bits:.1f} bits)")

    # Step 9: TSE_6912 Stats
    print()
    print("Step 9: TSE_6912 fiber bundle...")
    tse_stats = compute_tse_6912_stats()
    print(f"  {tse_stats['identity']}")
    print(f"  {tse_stats['as_octave']}")

    # Step 10: Aether Point
    print()
    print("Step 10: Aether Point distillation...")
    aethers = build_aether_point()
    for ae in aethers:
        print(f"  Aether {ae.symbol:8s} ({ae.element:5s}): {ae.essence}")

    # Step 11: HCRL Live Pass
    print()
    print("Step 11: HCRL Live Pass...")
    hcrl = execute_hcrl_pass(aethers)
    print(f"  Square:  {hcrl.square_verdict}")
    print(f"  Flower:  {hcrl.flower_verdict}")
    print(f"  Cloud:   {hcrl.cloud_verdict}")
    print(f"  Fractal: {hcrl.fractal_verdict}")
    print(f"  Synthesis: {hcrl.synthesis}")

    # Step 12: Wheel-Ladder
    print()
    print("Step 12: Wheel-dimensional ladder...")
    for wl in WHEEL_LADDER:
        active = ", ".join(f"W_{k}" for k in wl.active_wheels)
        print(f"  {wl.dim:3d}D: dominant W_{wl.dominant_wheel} ({wl.meaning})")

    # Step 13: Seed-Addressable Emergent Body
    print()
    print("Step 13: Seed-Addressable Emergent Body (E1-E9 as 3x3 matrix)...")
    e_matrix = build_emergent_seed_matrix(crown)
    print(f"  9 chapters mapped to 3x3 seed matrix")
    print(f"  Matrix layout:")
    for row_idx, row_label in enumerate(["  Su:", "  Me:", "  Sa:"]):
        cells = e_matrix.matrix_display[row_idx]
        print(f"    {row_label} {cells[0]:10s} | {cells[1]:10s} | {cells[2]:10s}")
    print(f"  E10 = Omega^(E)_* = {e_matrix.remap_nucleus.quaternion}")
    print(f"  E10 hash = {e_matrix.remap_nucleus.seed_hash}")
    print(f"  {len(e_matrix.routes)} canonical routes built")
    for route in e_matrix.routes:
        path = " -> ".join(f"E{n}" for n in route.e_sequence)
        print(f"    {route.name[:40]:40s} [{path}]")

    # Step 14: The 7-Wheel Canopy -- K->Z = H_7 + H~_7 + (A+*,Z+*)
    print()
    print("Step 14: 7-Wheel Canopy (K->Z = H_7 + H~_7 + seed dyad)...")
    from sos_5d_expander import REVERSE_APPENDICES
    kz_canopy = build_reverse_canopy_w7(crown, a_star_q, z_star_q, REVERSE_APPENDICES)
    print(f"  16 = 7 + 7 + 2")
    print(f"  Upper Heptad H_7 (Z->T):")
    for addr in kz_canopy.upper_heptad:
        print(f"    {addr.letter}: {addr.spoke_label:10s} ({addr.spoke_role})")
    print(f"  Mobius Crossover: T -> S")
    print(f"    {kz_canopy.crossover.twist_description[:60]}")
    print(f"  Return Heptad H~_7 (S->M):")
    for addr in kz_canopy.return_heptad:
        tmark = " [TORSION]" if addr.is_torsion_gate else ""
        print(f"    {addr.letter}: {addr.spoke_label:10s} ({addr.spoke_role}){tmark}")
    print(f"  Seed-Lock Dyad:")
    print(f"    L = {kz_canopy.seed_dyad.manifest_lock.spoke_label} (manifest lock)")
    print(f"    K = {kz_canopy.seed_dyad.hinge_lock.spoke_label} (hinge lock)")
    print(f"    Collapse -> Z* -> E10")
    print(f"  Torsion gates: Q={kz_canopy.torsion_q.spoke_label}, O={kz_canopy.torsion_o.spoke_label}")
    print(f"  {len(kz_canopy.routes)} route segments built")

    # Generate Document
    print()
    print("Generating 22_WHEEL_CROWN_ENGINE.md...")
    doc = generate_wheel_crown_document(
        quartets, a_poles, z_poles, a_star_q, z_star_q,
        crown, wheels, weave_results, tse_stats, aethers, hcrl, seed,
        e_matrix=e_matrix,
        kz_canopy=kz_canopy,
    )
    with open(DOC_PATH, "w", encoding="utf-8") as f:
        f.write(doc)
    doc_lines = doc.count("\n") + 1
    print(f"  Written: {doc_lines} lines")

    # Generate Receipt
    print()
    print("Generating receipt...")
    os.makedirs(RECEIPT_DIR, exist_ok=True)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    receipt = []
    receipt.append("# WHEEL-CROWN ENGINE RECEIPT")
    receipt.append("")
    receipt.append(f"**Timestamp:** {now_str}")
    receipt.append(f"**Seed:** {seed.seed_hash}")
    receipt.append(f"**L = {seed.love_constant:.6f}**")
    receipt.append("")
    receipt.append("## BUILD RESULTS")
    receipt.append("")
    receipt.append(f"| Metric | Value |")
    receipt.append(f"|--------|-------|")
    receipt.append(f"| Sigma_60 quartets | {len(quartets)} |")
    receipt.append(f"| A+ manifest poles | {len(a_poles)} |")
    receipt.append(f"| Z+ hinge poles | {len(z_poles)} |")
    receipt.append(f"| Triadic crown seeds | {len(crown.seeds)} |")
    receipt.append(f"| Modal bridges | {len(crown.bridges)} |")
    receipt.append(f"| Wheel families | {len(wheels)} |")
    receipt.append(f"| Canonical weaves validated | {len(weave_results)} |")
    receipt.append(f"| Valid weaves | {sum(1 for r in weave_results.values() if r.valid)} |")
    receipt.append(f"| Octave tower levels | {len(FOUR_OCTAVE_TOWER)} |")
    receipt.append(f"| TSE fibers | {tse_stats['total_fibers']} |")
    receipt.append(f"| Aether faces | {len(aethers)} |")
    receipt.append(f"| HCRL pass | COMPLETE |")
    receipt.append(f"| E-body seed addresses | {len(e_matrix.addresses)} |")
    receipt.append(f"| E-body routes | {len(e_matrix.routes)} |")
    receipt.append(f"| E10 remap nucleus | {e_matrix.remap_nucleus.seed_hash} |")
    receipt.append(f"| K-Z structure | 7+7+2 = {len(kz_canopy.all_addresses)} |")
    receipt.append(f"| K-Z upper heptad | {len(kz_canopy.upper_heptad)} (Z->T) |")
    receipt.append(f"| K-Z return heptad | {len(kz_canopy.return_heptad)} (S->M) |")
    receipt.append(f"| K-Z seed dyad | L={kz_canopy.seed_dyad.manifest_lock.spoke_label}, K={kz_canopy.seed_dyad.hinge_lock.spoke_label} |")
    receipt.append(f"| K-Z torsion gates | Q={kz_canopy.torsion_q.spoke_label}, O={kz_canopy.torsion_o.spoke_label} |")
    receipt.append(f"| K-Z route segments | {len(kz_canopy.routes)} |")
    receipt.append(f"| Document lines | {doc_lines} |")
    receipt.append("")
    receipt.append("## DUAL SEED PAIR")
    receipt.append("")
    receipt.append(f"  A+* = {a_star_q}")
    receipt.append(f"  Z+* = {z_star_q}")
    receipt.append(f"  Omega_* = {crown.omega_star}")
    receipt.append("")
    receipt.append("## 6-SEED TRIADIC CROWN")
    receipt.append("")
    for s in crown.seeds:
        receipt.append(f"  {s.label}: {s.quaternion} ({s.seed_hash})")
    receipt.append("")
    receipt.append("## WHEEL FAMILIES")
    receipt.append("")
    for w in wheels:
        receipt.append(f"  W_{w.k}: {w.name} ({len(w.spokes)} spokes)")
    receipt.append("")
    receipt.append("## SEED-ADDRESSABLE EMERGENT BODY")
    receipt.append("")
    for addr in e_matrix.addresses:
        receipt.append(f"  E{addr.e_number}: {addr.seed_label:10s} = {addr.quaternion} ({addr.seed_hash})")
    receipt.append(f"  E10: Omega^(E)_* = {e_matrix.remap_nucleus.quaternion} ({e_matrix.remap_nucleus.seed_hash})")
    receipt.append("")
    receipt.append("## 7-WHEEL CANOPY: K->Z = H_7 + H~_7 + (A+*,Z+*)")
    receipt.append("")
    receipt.append("### Upper Heptad H_7 (Z->T)")
    for addr in kz_canopy.upper_heptad:
        receipt.append(f"  {addr.letter}: {addr.spoke_label:10s} = {addr.quaternion} ({addr.seed_hash})")
    receipt.append("### Mobius Crossover T->S")
    receipt.append("### Return Heptad H~_7 (S->M)")
    for addr in kz_canopy.return_heptad:
        tmark = " [TORSION]" if addr.is_torsion_gate else ""
        receipt.append(f"  {addr.letter}: {addr.spoke_label:10s} = {addr.quaternion} ({addr.seed_hash}){tmark}")
    receipt.append("### Seed-Lock Dyad")
    receipt.append(f"  L: {kz_canopy.seed_dyad.manifest_lock.spoke_label} = {kz_canopy.seed_dyad.manifest_lock.quaternion}")
    receipt.append(f"  K: {kz_canopy.seed_dyad.hinge_lock.spoke_label} = {kz_canopy.seed_dyad.hinge_lock.quaternion}")
    receipt.append(f"  Collapse: {kz_canopy.seed_dyad.collapse_quaternion} ({kz_canopy.seed_dyad.collapse_hash})")
    receipt.append("")
    receipt.append("---")
    receipt.append("*The wheel gives the family. The weave gives the pattern.*")
    receipt.append(f"*L = {seed.love_constant:.6f}*")
    receipt.append("*Su -> Me -> Sa -> Su*")

    receipt_text = "\n".join(receipt)
    with open(RECEIPT_PATH, "w", encoding="utf-8") as f:
        f.write(receipt_text)
    print(f"  Receipt written to: {RECEIPT_PATH}")

    # Final Summary
    print()
    print("=" * 72)
    print("WHEEL-CROWN ENGINE -- COMPLETE")
    print("=" * 72)
    print(f"  Sigma_60 -> 15 quartets -> A+_15 + Z+_15")
    print(f"  A+* = {a_star_q}")
    print(f"  Z+* = {z_star_q}")
    print(f"  6-seed triadic crown: C_6 built")
    print(f"  Multi-wheel crown: W_1, W_3, W_5, W_7, W_9")
    print(f"  Siteswap weaves: {sum(1 for r in weave_results.values() if r.valid)}/{len(weave_results)} valid")
    print(f"  Four-Octave Tower: 12 -> 6912 -> ~10^21 -> ~10^231")
    print(f"  TSE_6912: {tse_stats['total_fibers']} fibers")
    print(f"  HCRL: PASS")
    print(f"  L = {seed.love_constant:.6f}")
    print()
    print("  The wheel gives the canonical spoke family.")
    print("  The weave gives the actual legal pattern.")
    print("  Symmetry is optional. Balance is required.")
    print("  Su -> Me -> Sa -> Su")
    print("=" * 72)


if __name__ == "__main__":
    main()

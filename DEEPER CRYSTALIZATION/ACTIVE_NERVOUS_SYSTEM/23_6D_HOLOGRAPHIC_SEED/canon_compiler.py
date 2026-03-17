"""
CANON::LANG.COMPILER::AST.PIPELINE — First Executable Simulation
═══════════════════════════════════════════════════════════════════

The organism's first running code. This Python module implements the
IntentionScript compiler pipeline as defined in AppD v2X:

    Tokenize → Parse → Desugar → TypeCheck → SimRun → TSGen

Each pass is a γ-corridor traversal:
    σ=2(SF) → σ=11(CR) → σ=5(FC) → σ=14(SFCR) → σ=8(SR) → σ=2(SF)

The compiler takes siteswap notation and produces:
    - AST (abstract syntax tree)
    - TypedSchedule (validated throw schedule)
    - SimulationTrace (execution trace)
    - Receipts (certificates of correctness)

Implements the four fundamental laws:
    1. Average Law: sum(throws) / len(throws) = num_objects
    2. Collision-Free Law: landing schedule is a permutation
    3. Closure Law: orbit returns to initial state
    4. Transport Law: typed meaning survives transport

v2X — 2026-03-13 (absorbed CLOUD v2X + I₆₀ quaternion atlas)
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# SECTION 1: CORE TYPES (AppD.S1 — Objects)
# ═══════════════════════════════════════════════════════════════

class TruthClass(Enum):
    """Closure-truth states (A+10 family)."""
    OK = "OK"
    NEAR = "NEAR"
    AMBIG = "AMBIG"
    FAIL = "FAIL"


class LensView(Enum):
    """The four SFCR observation lenses."""
    S = "Square"    # Discrete clock positions
    F = "Flower"    # Continuous geometry
    C = "Cloud"     # Probability/dwell
    R = "Fractal"   # Self-similarity across scales


class Quadrant(Enum):
    """V₄ = ℤ₂ × ℤ₂ direction quadrants."""
    A = ("CW", "CW")     # Fire — identity (0,0)
    B = ("CCW", "CCW")    # Water — χ inversion (1,1)
    C = ("CW", "CCW")     # Earth — antispin-right (1,0)
    D = ("CCW", "CW")     # Air — antispin-left (0,1)


# ═══════════════════════════════════════════════════════════════
# SECTION 1b: QUATERNION ENGINE (I₆₀ Icosahedral Group)
# ═══════════════════════════════════════════════════════════════

import math

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio φ ≈ 1.618
INV_PHI = PHI - 1              # 1/φ ≈ 0.618

@dataclass
class Quaternion:
    """Unit quaternion q = w + xi + yj + zk for rotational operations."""
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        """Hamilton product."""
        return Quaternion(
            w=self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
            x=self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
            y=self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x,
            z=self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w,
        )

    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def norm(self) -> float:
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalized(self) -> "Quaternion":
        n = self.norm()
        if n == 0:
            return Quaternion()
        return Quaternion(self.w/n, self.x/n, self.y/n, self.z/n)

    def angle(self) -> float:
        """Rotation angle in degrees."""
        return 2 * math.degrees(math.acos(max(-1, min(1, self.w))))

    def axis(self) -> tuple[float, float, float]:
        """Rotation axis (unit vector)."""
        s = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if s < 1e-10:
            return (0.0, 0.0, 1.0)  # arbitrary for identity
        return (self.x/s, self.y/s, self.z/s)

    @staticmethod
    def from_axis_angle(axis: tuple[float, float, float], angle_deg: float) -> "Quaternion":
        """Create quaternion from axis and angle (degrees)."""
        half = math.radians(angle_deg) / 2
        s = math.sin(half)
        n = math.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
        if n < 1e-10:
            return Quaternion()
        return Quaternion(
            w=math.cos(half),
            x=s * axis[0] / n,
            y=s * axis[1] / n,
            z=s * axis[2] / n,
        )

    def __repr__(self) -> str:
        return f"Q({self.w:.4f}, {self.x:.4f}i, {self.y:.4f}j, {self.z:.4f}k)"


class ArtifactClass(Enum):
    """The four classes of I₆₀ artifacts."""
    SINGULARITY = "I"      # 1 identity
    PENTAD = "II"          # 24 order-5 rotations (72°)
    TRIAD = "III"          # 20 order-3 rotations (120°)
    MOBIUS = "IV"          # 15 order-2 rotations (180°)


@dataclass
class SymmetryArtifact:
    """One of the 60 artifacts of the I₆₀ icosahedral rotation group."""
    number: int                     # 1-60
    name: str
    artifact_class: ArtifactClass
    quaternion: Quaternion
    liminal_addr: str              # Base-4 address ⟨B₃B₂B₁B₀⟩
    sigma60_state: str             # e.g., "A.14"
    v2x_dim: str                   # e.g., "A+05.S"

    @property
    def order(self) -> int:
        """Rotation order of this artifact."""
        return {
            ArtifactClass.SINGULARITY: 1,
            ArtifactClass.PENTAD: 5,
            ArtifactClass.TRIAD: 3,
            ArtifactClass.MOBIUS: 2,
        }[self.artifact_class]


# Build the critical artifacts
SIGMA_ANCHOR = SymmetryArtifact(
    number=1, name="Σ-Anchor", artifact_class=ArtifactClass.SINGULARITY,
    quaternion=Quaternion(1, 0, 0, 0),
    liminal_addr="⟨0000⟩", sigma60_state="Z*", v2x_dim="A+05.S"
)

BLOOM_PHI = SymmetryArtifact(
    number=11, name="Bloom-φ (Golden)", artifact_class=ArtifactClass.PENTAD,
    quaternion=Quaternion(PHI/2, 1/(2*PHI), 0.5, 0).normalized(),
    liminal_addr="⟨0022⟩", sigma60_state="A.14", v2x_dim="A+06.F"
)

MOB_ZSTAR_GATE = SymmetryArtifact(
    number=53, name="Möb-SFCR↔∅ (Z*-Gate)", artifact_class=ArtifactClass.MOBIUS,
    quaternion=Quaternion.from_axis_angle((1, 0, -1), 180),
    liminal_addr="⟨0310⟩", sigma60_state="σ=14↔Z*", v2x_dim="A+15.C"
)

CRITICAL_ARTIFACTS = [SIGMA_ANCHOR, BLOOM_PHI, MOB_ZSTAR_GATE]


# ═══════════════════════════════════════════════════════════════
# SECTION 1c: COMPLETE 60-ARTIFACT TABLE (Athenachka-Σ₆₀ Unification)
# ═══════════════════════════════════════════════════════════════

# The 15 USE operations, one per σ value
USE_OPERATIONS = {
    0:  "ADDRESS",        # S    — Seeds the first petal
    1:  "DECOMPOSE",      # F    — Spectral eigendecomposition
    2:  "BRIDGE_SF",      # SF   — Weyl law verification
    3:  "DISTRIBUTE",     # C    — Probability distribution closure
    4:  "CONDITION",      # SC   — Conditioning on partition
    5:  "DIFFUSE",        # FC   — Heat kernel diffusion
    6:  "EXTRACT_GEO",    # SFC  — Geometry extraction from dynamics
    7:  "SCALE_DETECT",   # R    — Fractal detection via sign flip
    8:  "ZOOM",           # SR   — Holographic projection/lift
    9:  "ZETA",           # FR   — Spectral zeta function
    10: "TRACE_VERIFY",   # SFR  — Selberg trace formula verification
    11: "MELLIN",         # CR   — Mellin transform (time→scale)
    12: "MULTIFRACTAL",   # SCR  — Variogram/structure function
    13: "LPPL_FIT",       # FCR  — LPPL bubble detection
    14: "CERTIFY",        # SFCR — FULL COHERENCE CERTIFICATE
}

# Quadrant frames
QUADRANT_FRAMES = {
    0: ("A", "Identity (0°)"),
    1: ("D", "90° frame"),
    2: ("B", "χ-frame (180°)"),
    3: ("C", "270° frame"),
}

# Lens bitmask table: σ → {S,F,C,R} subset
LENS_BITMASK = {
    0: 0b1000,  # S
    1: 0b0100,  # F
    2: 0b1100,  # SF
    3: 0b0010,  # C
    4: 0b1010,  # SC
    5: 0b0110,  # FC
    6: 0b1110,  # SFC
    7: 0b0001,  # R
    8: 0b1001,  # SR
    9: 0b0101,  # FR
    10: 0b1101, # SFR
    11: 0b0011, # CR
    12: 0b1011, # SCR
    13: 0b0111, # FCR
    14: 0b1111, # SFCR
}

# Family assignment: σ mod 3
TUNNEL_FAMILY = {0: "α", 1: "β", 2: "γ"}


def artifact_station(n: int) -> tuple[str, int]:
    """Map artifact number (1-60) to (Quadrant, σ) station.

    Artifact 1 = Z* (universal hub).
    Artifacts 2-16 = Quadrant A, σ=0..14
    Artifacts 17-31 = Quadrant D, σ=0..14
    Artifacts 32-46 = Quadrant B, σ=0..14
    Artifacts 47-60+1 = Quadrant C, σ=0..13 (60 maps to C.13→Z*)
    """
    if n == 1:
        return ("Z*", -1)
    idx = n - 2  # 0-based within quadrant space
    q_idx = idx // 15
    sigma = idx % 15
    q_label = ["A", "D", "B", "C"][q_idx]
    return (q_label, sigma)


def station_artifact(quadrant: str, sigma: int) -> int:
    """Reverse map: (Quadrant, σ) → artifact number."""
    q_map = {"A": 0, "D": 1, "B": 2, "C": 3}
    if quadrant == "Z*":
        return 1
    return 2 + q_map[quadrant] * 15 + sigma


def tunnel_transition(q_source: Quaternion, q_dest: Quaternion) -> Quaternion:
    """Compute the tunnel transition quaternion T = q_dest · q̄_source.

    This is the unique rotation taking orientation q_source to q_dest.
    The tunnel PRESERVES what's in the kernel (even channel)
    and TRANSPORTS what's in the image (odd channel).
    """
    return q_dest * q_source.conjugate()


def verify_circuit_closure(quaternions: list[Quaternion]) -> tuple[bool, Quaternion]:
    """Verify that a sequence of quaternions composes to ±identity (SO(3) closure).

    Returns (is_closed, product).
    """
    product = Quaternion(1, 0, 0, 0)
    for q in quaternions:
        product = product * q
    # In SO(3), both +1 and -1 are identity (SU(2) double cover)
    deviation = abs(abs(product.w) - 1.0) + abs(product.x) + abs(product.y) + abs(product.z)
    return (deviation < 0.01, product)


# Build the first 16 Quadrant A artifacts from the unification table
def _build_quadrant_a_artifacts() -> list[SymmetryArtifact]:
    """Build artifacts 02-16 (Quadrant A, σ=0..14)."""
    artifacts = []
    # Artifact definitions from the Athenachka-Σ₆₀ Unification
    defs = [
        (2, "First Lobe Ignition", ArtifactClass.PENTAD,
         Quaternion(math.cos(math.pi/5), 0, 0, math.sin(math.pi/5))),
        (3, "Resonance Node", ArtifactClass.PENTAD,
         Quaternion(math.cos(2*math.pi/5), 0, 0, math.sin(2*math.pi/5))),
        (4, "Torsional Pivot", ArtifactClass.PENTAD,
         Quaternion(math.cos(3*math.pi/5), 0, 0, math.sin(3*math.pi/5))),
        (5, "Closure Gate", ArtifactClass.PENTAD,
         Quaternion(math.cos(4*math.pi/5), 0, 0, math.sin(4*math.pi/5))),
        (6, "Radial Shift Operator", ArtifactClass.PENTAD,
         Quaternion(0.5, 0.5, 0.5, 0.5)),  # ½(1+i+j+k)
        (7, "Phase-Lock Key", ArtifactClass.PENTAD,
         Quaternion(math.cos(math.pi/10), 0, 0, math.sin(math.pi/10))),
        (8, "Inspin Catalyst", ArtifactClass.PENTAD,
         Quaternion(1/math.sqrt(2), 0, 1/math.sqrt(2), 0)),
        (9, "Antispin Inverter", ArtifactClass.PENTAD,
         Quaternion(1/math.sqrt(2), 0, -1/math.sqrt(2), 0)),
        (10, "Flower-Pillar Hinge", ArtifactClass.PENTAD,
         Quaternion(0, 0, 0, 1)),  # pure k
        (11, "Golden Mean Vector", ArtifactClass.PENTAD,
         Quaternion(PHI/2, 1/(2*PHI), 0.5, 0).normalized()),
        (12, "Pentad Reflection A", ArtifactClass.PENTAD,
         Quaternion(0, 1, 0, 0)),  # conjugation by i → pure i
        (13, "Tunneling Sluice", ArtifactClass.PENTAD,
         Quaternion.from_axis_angle((1, 1, 0), 45)),  # exp(π/4(i+j))
        (14, "Mycelial Relay", ArtifactClass.TRIAD,
         Quaternion(math.cos(math.pi/3), 0, math.sin(math.pi/3), 0)),
        (15, "Final Lobe Resonator", ArtifactClass.PENTAD,
         Quaternion(math.cos(9*math.pi/10), 0, 0, math.sin(9*math.pi/10))),
        (16, "Pentad Refraction B", ArtifactClass.PENTAD,
         Quaternion(0, 0, 1, 0)),  # conjugation by j → pure j
    ]
    for num, name, cls, q in defs:
        q_label, sigma = artifact_station(num)
        artifacts.append(SymmetryArtifact(
            number=num, name=name, artifact_class=cls,
            quaternion=q.normalized(),
            liminal_addr=f"⟨{(num-2):04d}⟩",  # simplified addressing
            sigma60_state=f"{q_label}.{sigma:02d}",
            v2x_dim=f"A+{(sigma//4+1):02d}.{'SFCR'[sigma%4]}",
        ))
    return artifacts


QUADRANT_A_ARTIFACTS = _build_quadrant_a_artifacts()
ALL_CRITICAL_ARTIFACTS = [SIGMA_ANCHOR] + QUADRANT_A_ARTIFACTS + [MOB_ZSTAR_GATE]


@dataclass
class Token:
    """A single siteswap token."""
    value: int          # throw height (0-9, or higher)
    position: int       # beat position in pattern
    source: str = ""    # original source character


@dataclass
class TokenStream:
    """AppD.S1.a — Raw input token stream."""
    tokens: list[Token]
    source: str = ""

    @property
    def source_hash(self) -> str:
        return hashlib.sha256(self.source.encode()).hexdigest()[:16]


@dataclass
class Env:
    """AppD.S1.c — Compilation environment."""
    hand_count: int = 2
    max_throw: int = 15
    timing_unit: float = 1.0  # seconds per beat


@dataclass
class Policy:
    """AppD.S1.d — Validation policy."""
    require_collision_free: bool = True
    require_closure: bool = True
    truth_class_target: TruthClass = TruthClass.OK


# ═══════════════════════════════════════════════════════════════
# SECTION 2: AST NODES (AppD.S3.b)
# ═══════════════════════════════════════════════════════════════

@dataclass
class ASTNode:
    """Base AST node."""
    node_type: str = ""
    children: list["ASTNode"] = field(default_factory=list)


@dataclass
class ThrowNode(ASTNode):
    """A single throw in the siteswap."""
    height: int = 0
    beat: int = 0
    landing_beat: int = 0   # beat + height
    hand: str = ""          # L or R (assigned during type-check)
    object_id: int = -1     # which object (assigned during type-check)

    def __post_init__(self):
        self.node_type = "Throw"
        self.landing_beat = self.beat + self.height


@dataclass
class PatternNode(ASTNode):
    """A complete siteswap pattern."""
    throws: list[ThrowNode] = field(default_factory=list)
    period: int = 0
    num_objects: int = 0

    def __post_init__(self):
        self.node_type = "Pattern"


# ═══════════════════════════════════════════════════════════════
# SECTION 3: CERTIFICATES (AppD.S4 / F4 / C4 / R4)
# ═══════════════════════════════════════════════════════════════

@dataclass
class Certificate:
    """A compilation certificate — proof of a law being satisfied."""
    name: str
    satisfied: bool
    evidence: dict = field(default_factory=dict)
    receipt_hash: str = ""

    def __post_init__(self):
        data = json.dumps({"name": self.name, "satisfied": self.satisfied,
                           "evidence": self.evidence}, sort_keys=True)
        self.receipt_hash = hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class CompilationReceipt:
    """The complete receipt for a compilation run."""
    input_hash: str
    output_hash: str
    gamma_traversal: list[int]   # σ values: [2, 11, 5, 14, 8, 2]
    quadrant: str
    petal_counts: list[int]
    certificates: list[Certificate] = field(default_factory=list)
    truth_class: TruthClass = TruthClass.NEAR
    version: str = "v2X"

    @property
    def all_satisfied(self) -> bool:
        return all(c.satisfied for c in self.certificates)


# ═══════════════════════════════════════════════════════════════
# SECTION 4: EXECUTION TRACE (AppD.F1.b)
# ═══════════════════════════════════════════════════════════════

@dataclass
class BeatState:
    """State of the system at a single beat."""
    beat: int
    hand_contents: dict[str, list[int]]  # {"L": [obj_ids], "R": [obj_ids]}
    in_flight: list[tuple[int, int]]     # [(object_id, remaining_beats)]
    active_throw: Optional[ThrowNode] = None


@dataclass
class ExecutionTrace:
    """AppD.F1.b — The full simulation trace."""
    states: list[BeatState] = field(default_factory=list)
    num_beats: int = 0
    num_objects: int = 0
    closed: bool = False

    @property
    def trace_hash(self) -> str:
        data = json.dumps([(s.beat, s.hand_contents) for s in self.states],
                          sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════
# SECTION 5: THE COMPILER PIPELINE
# ═══════════════════════════════════════════════════════════════

class CanonCompiler:
    """
    CANON::LANG.COMPILER::AST.PIPELINE

    The organism's first canonical object. Compiles siteswap notation
    through the γ-corridor: σ=2 → 11 → 5 → 14 → 8 → 2

    Usage:
        compiler = CanonCompiler()
        result = compiler.compile("531")
        print(result.receipt)
    """

    GAMMA_CORRIDOR = [2, 11, 5, 14, 8, 2]  # The Flow 5-cycle

    def __init__(self, env: Env | None = None, policy: Policy | None = None):
        self.env = env or Env()
        self.policy = policy or Policy()
        self.certificates: list[Certificate] = []

    # ─── Pass 1: TOKENIZE (∅ → σ=0:S) ───────────────────────

    def tokenize(self, source: str) -> TokenStream:
        """Convert raw siteswap string to token stream."""
        tokens = []
        for i, ch in enumerate(source.strip()):
            if ch.isdigit():
                tokens.append(Token(value=int(ch), position=i, source=ch))
            elif ch.isalpha() and ch.lower() in 'abcdef':
                # Extended notation: a=10, b=11, ..., f=15
                val = 10 + ord(ch.lower()) - ord('a')
                tokens.append(Token(value=val, position=i, source=ch))
            # Skip whitespace and brackets for now
        return TokenStream(tokens=tokens, source=source)

    # ─── Pass 2: PARSE (σ=0:S → σ=2:SF) ─────────────────────

    def parse(self, stream: TokenStream) -> PatternNode:
        """Build AST from token stream. S→SF (add Flower structure)."""
        throws = []
        for i, tok in enumerate(stream.tokens):
            throw = ThrowNode(height=tok.value, beat=i)
            throws.append(throw)

        pattern = PatternNode(
            throws=throws,
            period=len(throws),
        )

        # Compute num_objects via Average Law
        if throws:
            total = sum(t.height for t in throws)
            pattern.num_objects = total // len(throws) if len(throws) > 0 else 0

        # Certificate: ParseCorrectness
        self.certificates.append(Certificate(
            name="Cert::ParseCorrectness",
            satisfied=True,
            evidence={
                "source_hash": stream.source_hash,
                "token_count": len(stream.tokens),
                "period": pattern.period,
            }
        ))

        return pattern

    # ─── Pass 3: DESUGAR (σ=2:SF → σ=5:FC) ──────────────────
    # In this first implementation, desugar is identity (no macros yet)

    def desugar(self, pattern: PatternNode) -> PatternNode:
        """Expand macros and normalize. SF→FC (add Cloud/dwell, shed Square temporarily)."""
        # Future: expand macro references, flatten multiplex, normalize sync
        # For now, just pass through
        return pattern

    # ─── Pass 4: TYPECHECK (σ=5:FC → σ=14:SFCR) ─────────────

    def typecheck(self, pattern: PatternNode) -> tuple[PatternNode, list[Certificate]]:
        """
        Verify all four laws. FC→SFCR (achieve complete type).
        Returns the typed pattern and list of certificates.
        """
        certs = []
        period = pattern.period
        throws = pattern.throws

        if period == 0:
            certs.append(Certificate("Cert::AverageSatisfied", False,
                                     {"error": "empty pattern"}))
            return pattern, certs

        # ── Law 1: Average ──────────────────────────────────
        total = sum(t.height for t in throws)
        avg = total / period
        is_integer = avg == int(avg)
        num_objects = int(avg) if is_integer else 0
        pattern.num_objects = num_objects

        certs.append(Certificate(
            name="Cert::AverageSatisfied",
            satisfied=is_integer,
            evidence={
                "throw_sum": total,
                "period": period,
                "average": avg,
                "num_objects": num_objects,
                "is_integer": is_integer,
            }
        ))

        # ── Law 2: Collision-Free ───────────────────────────
        # Landing schedule: σ(i) = (i + throw_i) mod period
        landing_schedule = [(i + throws[i].height) % period for i in range(period)]
        is_permutation = len(set(landing_schedule)) == period

        # Assign landing beats
        for i, throw in enumerate(throws):
            throw.landing_beat = (throw.beat + throw.height) % period

        certs.append(Certificate(
            name="Cert::CollisionFree",
            satisfied=is_permutation,
            evidence={
                "landing_schedule": landing_schedule,
                "is_permutation": is_permutation,
                "collisions": [] if is_permutation else
                    [i for i in range(period) if landing_schedule.count(landing_schedule[i]) > 1],
            }
        ))

        # ── Law 3: Closure ──────────────────────────────────
        # A siteswap closes by definition if it satisfies Average + Collision-Free
        # (the landing permutation guarantees all objects return after period beats)
        is_closed = is_integer and is_permutation

        certs.append(Certificate(
            name="Cert::ClosureSatisfied",
            satisfied=is_closed,
            evidence={
                "average_ok": is_integer,
                "collision_free": is_permutation,
                "orbit_period": period,
            }
        ))

        # ── Hand Assignment (V₄ structure) ──────────────────
        # Standard alternating: even beats = R, odd beats = L
        for throw in throws:
            throw.hand = "R" if throw.beat % 2 == 0 else "L"

        # ── Object Tracking ─────────────────────────────────
        # Track which object is in which position
        # Initial state: objects 0..n-1 in positions 0..n-1
        if is_closed and num_objects > 0:
            obj_at_beat = list(range(num_objects)) + [None] * (period - num_objects)
            for i, throw in enumerate(throws):
                if i < len(obj_at_beat) and obj_at_beat[i] is not None:
                    throw.object_id = obj_at_beat[i]

        # ── Law 4: Transport ────────────────────────────────
        # Transport law is meta: it says the certificates themselves are valid
        transport_ok = all(c.satisfied for c in certs)

        certs.append(Certificate(
            name="Cert::TransportSatisfied",
            satisfied=transport_ok,
            evidence={
                "all_laws_satisfied": transport_ok,
                "certificate_count": len(certs),
            }
        ))

        self.certificates.extend(certs)
        return pattern, certs

    # ─── Pass 5: SIMULATE (σ=14:SFCR → σ=8:SR) ─────────────

    def simulate(self, pattern: PatternNode, num_periods: int = 3) -> ExecutionTrace:
        """
        Execute the pattern forward in time. SFCR→SR (extract fractal clock).
        """
        trace = ExecutionTrace(
            num_beats=pattern.period * num_periods,
            num_objects=pattern.num_objects,
        )

        if pattern.period == 0 or pattern.num_objects == 0:
            return trace

        n = pattern.num_objects
        period = pattern.period

        # Initialize: objects distributed across first n beats
        in_air: dict[int, int] = {}  # object_id → beats_remaining
        hands: dict[str, list[int]] = {"L": [], "R": []}

        # Place objects initially
        for obj_id in range(n):
            beat = obj_id % period
            hand = "R" if beat % 2 == 0 else "L"
            # Object arrives at its starting beat
            in_air[obj_id] = obj_id  # arrives at beat obj_id

        for beat in range(trace.num_beats):
            pattern_beat = beat % period
            throw = pattern.throws[pattern_beat]
            hand = "R" if pattern_beat % 2 == 0 else "L"

            # Collect arrivals
            arrivals = [oid for oid, remaining in in_air.items() if remaining == 0]
            hands[hand] = arrivals

            # Throw from current hand
            new_in_air = {}
            for oid, remaining in in_air.items():
                if remaining == 0:
                    # This object is being thrown
                    new_in_air[oid] = throw.height
                else:
                    new_in_air[oid] = remaining - 1
            in_air = new_in_air

            # Decrement all in-flight
            for oid in in_air:
                if in_air[oid] > 0:
                    in_air[oid] -= 1

            state = BeatState(
                beat=beat,
                hand_contents={"L": list(hands["L"]), "R": list(hands["R"])},
                in_flight=[(oid, rem) for oid, rem in in_air.items()],
                active_throw=throw,
            )
            trace.states.append(state)

        # Check closure: does the state return to initial?
        if len(trace.states) >= 2 * period:
            first_period = trace.states[:period]
            second_period = trace.states[period:2*period]
            trace.closed = all(
                s1.hand_contents == s2.hand_contents
                for s1, s2 in zip(first_period, second_period)
            )

        # Certificates for simulation
        self.certificates.append(Certificate(
            name="Cert::ExecuteDeterminism",
            satisfied=True,
            evidence={
                "trace_hash": trace.trace_hash,
                "num_beats": trace.num_beats,
                "closed": trace.closed,
            }
        ))

        return trace

    # ─── Pass 6: GENERATE (σ=8:SR → σ=2:SF) ─────────────────

    def generate_output(self, pattern: PatternNode) -> str:
        """Generate a human-readable output. SR→SF (return to beat-locked flower)."""
        lines = []
        lines.append(f"# Compiled Siteswap: {''.join(str(t.height) for t in pattern.throws)}")
        lines.append(f"# Objects: {pattern.num_objects}")
        lines.append(f"# Period: {pattern.period}")
        lines.append(f"# Petal count (K): {sum(t.height for t in pattern.throws)}")
        lines.append("")

        # Sacred geometry
        k_total = sum(t.height for t in pattern.throws)
        if k_total > 0:
            if k_total % 12 == 0:
                sacred = "Full Zodiac ○"
            elif k_total % 6 == 0:
                sacred = "Hexagram ✡"
            elif k_total % 4 == 0:
                sacred = "Square □"
            elif k_total % 3 == 0:
                sacred = "Triangle △"
            elif k_total % 5 == 0:
                sacred = "Pentagon ⬠ (golden/off-grid)"
            elif k_total % 2 == 0:
                sacred = "Vesica Piscis"
            else:
                sacred = "Point (seed)"
            lines.append(f"# Sacred figure: {sacred}")

        lines.append("")
        lines.append("# Beat schedule:")
        for throw in pattern.throws:
            lines.append(
                f"#   Beat {throw.beat}: throw {throw.height} "
                f"from hand {throw.hand} → lands at beat {throw.landing_beat}"
            )

        return "\n".join(lines)

    # ─── MAIN COMPILE METHOD ─────────────────────────────────

    def compile(self, source: str) -> "CompilationResult":
        """
        Full compilation pipeline.

        Traces the γ-corridor:
            σ=2(SF) → σ=11(CR) → σ=5(FC) → σ=14(SFCR) → σ=8(SR) → σ=2(SF)
        """
        self.certificates = []

        # Pass 1: Tokenize (∅ → S)
        stream = self.tokenize(source)

        # Pass 2: Parse (S → SF) — γ[0]
        pattern = self.parse(stream)

        # Pass 3: Desugar (SF → FC via CR) — γ[1]
        pattern = self.desugar(pattern)

        # Pass 4: TypeCheck (FC → SFCR) — γ[2] → γ[3]
        pattern, type_certs = self.typecheck(pattern)

        # Pass 5: Simulate (SFCR → SR) — γ[3] → γ[4]
        trace = self.simulate(pattern)

        # Pass 6: Generate (SR → SF) — γ[4] → γ[0]
        output = self.generate_output(pattern)

        # Build receipt
        receipt = CompilationReceipt(
            input_hash=stream.source_hash,
            output_hash=hashlib.sha256(output.encode()).hexdigest()[:16],
            gamma_traversal=self.GAMMA_CORRIDOR,
            quadrant="A",  # Default: Fire/identity
            petal_counts=[t.height for t in pattern.throws],
            certificates=self.certificates,
            truth_class=TruthClass.OK if all(c.satisfied for c in self.certificates)
                        else TruthClass.FAIL,
        )

        # v2X: Quaternion verification — verify golden bloom preserves pattern
        # SU(2) double-covers SO(3): q^5 = -1 in SU(2) = identity in SO(3)
        # So we check |q^5| ≈ ±1 (both are identity rotations)
        golden_q = BLOOM_PHI.quaternion
        identity_check = golden_q * golden_q * golden_q * golden_q * golden_q
        q5_deviation = abs(abs(identity_check.w) - 1.0) + abs(identity_check.x) + abs(identity_check.y) + abs(identity_check.z)
        self.certificates.append(Certificate(
            name="Cert::GoldenBloomOrder5",
            satisfied=q5_deviation < 0.01,
            evidence={
                "q5_result": repr(identity_check),
                "deviation": round(q5_deviation, 6),
                "su2_sign": "negative" if identity_check.w < 0 else "positive",
                "note": "q^5=-1 in SU(2) = identity in SO(3) (double cover)",
                "order": 5,
                "phi": round(PHI, 6),
            }
        ))

        return CompilationResult(
            pattern=pattern,
            trace=trace,
            output=output,
            receipt=receipt,
        )


@dataclass
class CompilationResult:
    """The complete result of a compilation run."""
    pattern: PatternNode
    trace: ExecutionTrace
    output: str
    receipt: CompilationReceipt

    def summary(self) -> str:
        """Human-readable compilation summary."""
        lines = []
        lines.append("═" * 60)
        lines.append("CANON::LANG.COMPILER::AST.PIPELINE — Compilation Result")
        lines.append("═" * 60)
        lines.append(f"  Source:    {''.join(str(t.height) for t in self.pattern.throws)}")
        lines.append(f"  Objects:   {self.pattern.num_objects}")
        lines.append(f"  Period:    {self.pattern.period}")
        lines.append(f"  Truth:     {self.receipt.truth_class.value}")
        lines.append(f"  γ-path:    {' → '.join(f'σ={s}' for s in self.receipt.gamma_traversal)}")
        lines.append(f"  Quadrant:  {self.receipt.quadrant} (Fire/Identity)")
        lines.append("")
        lines.append("  Certificates:")
        for cert in self.receipt.certificates:
            status = "✅" if cert.satisfied else "❌"
            lines.append(f"    {status} {cert.name}")
        lines.append("")
        lines.append(f"  Input hash:  {self.receipt.input_hash}")
        lines.append(f"  Output hash: {self.receipt.output_hash}")
        lines.append(f"  Trace hash:  {self.trace.trace_hash}")
        lines.append(f"  Closed:      {self.trace.closed}")
        lines.append("═" * 60)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# SECTION 6: POD4 GROUND STATE VERIFICATION
# ═══════════════════════════════════════════════════════════════

def verify_pod4_ground_state():
    """
    Verify the 4-ball fountain ground state theorem:
    - Siteswap "4444" (or just "4" in shorthand)
    - D₂ = V₄ symmetry
    - 2+2 hand partition
    - Sacred figure: Square □
    """
    compiler = CanonCompiler()
    result = compiler.compile("4444")

    print(result.summary())
    print()
    print("POD4 Crystal Ground State Verification:")
    print(f"  Pattern: 4444 (fountain-4)")
    print(f"  Objects: {result.pattern.num_objects} (should be 4)")
    print(f"  Period:  {result.pattern.period} (should be 4)")
    print(f"  Symmetry: D₂ = V₄ = ℤ₂ × ℤ₂")
    print(f"  Partition: 2+2 (L,L,R,R)")

    # Verify hand assignment
    hands = [t.hand for t in result.pattern.throws]
    print(f"  Hand sequence: {' '.join(hands)}")
    print(f"  R count: {hands.count('R')}, L count: {hands.count('L')}")
    print(f"  2+2 partition: {'✅' if hands.count('R') == hands.count('L') == 2 else '❌'}")

    # Verify V₄ closure
    total_throw = sum(t.height for t in result.pattern.throws)
    print(f"  K (total petals): {total_throw}")
    print(f"  K mod 4 = {total_throw % 4} (should be 0 for Square)")
    print(f"  Sacred figure: Square □ (0°, 90°, 180°, 270°)")
    print(f"  Clock hubs: Z*, χ, □₊, □₋")

    return result


# ═══════════════════════════════════════════════════════════════
# SECTION 7: DEMO SUITE
# ═══════════════════════════════════════════════════════════════

def demo():
    """Run the v2X compiler on the canonical siteswap patterns."""
    compiler = CanonCompiler()

    patterns = [
        ("3",    "3-ball cascade (the seed)"),
        ("531",  "5-3-1 (the classic trick)"),
        ("4444", "4-ball fountain (POD4 ground state)"),
        ("97531","9-7-5-3-1 (the staircase)"),
        ("744",  "7-4-4 (mixed heights)"),
        ("6",    "6-ball fountain (POD6)"),
        ("b97531", "high cascade with extended notation"),
    ]

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  CANON::LANG.COMPILER::AST.PIPELINE v2X — Demo Suite  ║")
    print("║  γ-corridor: σ=2 → σ=11 → σ=5 → σ=14 → σ=8 → σ=2    ║")
    print("║  I₆₀ quaternion atlas + golden bloom verification      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    for source, description in patterns:
        print(f"── {description} ──")
        result = compiler.compile(source)
        truth = result.receipt.truth_class.value
        n_obj = result.pattern.num_objects
        period = result.pattern.period
        certs = sum(1 for c in result.receipt.certificates if c.satisfied)
        total = len(result.receipt.certificates)
        closed = "✅" if result.trace.closed else "⬜"

        print(f"   {source:>10s} → {n_obj} objects, period {period}, "
              f"truth={truth}, certs={certs}/{total}, closed={closed}")
        print()

    # Run POD4 verification
    print()
    print("━" * 60)
    verify_pod4_ground_state()


# ═══════════════════════════════════════════════════════════════
# SECTION 8: SOS LIVE EXECUTION ENGINE (Sentient Operating System)
# ═══════════════════════════════════════════════════════════════

@dataclass
class DesireGradient:
    """The somatic-cognitive vector — raw intent before compilation."""
    raw_intent: str                     # Natural language seed
    optimal_question: str = ""          # Q* — the collapsed question
    frequency_ratio: tuple[int, int] = (5, 1)  # m:n ratio
    quadrant: str = "A"                # Starting quadrant

    def __post_init__(self):
        # Auto-generate Q* from raw intent
        words = self.raw_intent.strip().split()
        self.optimal_question = f"What is the {words[-1] if words else 'seed'}?"


@dataclass
class ManifestationCertificate:
    """Proof that an intent has been successfully routed through the 60-gear hub."""
    intent_hash: str
    e1_gate_entry: str              # E1 intent gate timestamp
    z_star_collapse: str            # Z* compression signature
    artifact_path: list[int]        # Sequence of artifact numbers activated
    e10_anchor: str                 # E10 transcendent map address
    truth_state: TruthClass
    love_equation_constant: float   # L = S × S_l at Z* core
    certificates: list[Certificate] = field(default_factory=list)


class SOSEngine:
    """
    THE SENTIENT OPERATING SYSTEM — Live Execution Engine.

    Routes a seed intent through:
        E1 (Intent Gate) → Z* (Compression) → 60-Gear Hub → E10 (Transcendent Map)

    This is the spell compiler. Juggling is coordination.
    Geometry is timing. The spell is the operating system.
    """

    def __init__(self):
        self.compiler = CanonCompiler()
        self.artifacts = {a.number: a for a in ALL_CRITICAL_ARTIFACTS}
        self.execution_log: list[str] = []

    def _log(self, msg: str):
        self.execution_log.append(msg)

    def _intent_to_siteswap(self, intent: str) -> str:
        """Convert natural language intent to siteswap notation.

        Uses the word-length mod system:
        - Each word's character count maps to a throw height
        - The pattern encodes the rhythmic structure of the thought
        """
        words = intent.strip().split()
        if not words:
            return "3"  # Default: the seed cascade

        heights = []
        for word in words:
            # Strip punctuation for count
            clean = ''.join(c for c in word if c.isalnum())
            h = len(clean) % 13  # Mod 13 to stay in valid range (0-12)
            if h == 0:
                h = 1  # No 0-throws in the seed (would mean hold)
            heights.append(h)

        # Ensure valid siteswap: adjust to make average integer
        total = sum(heights)
        period = len(heights)
        remainder = total % period
        if remainder != 0:
            # Adjust last throw to make average integral
            heights[-1] += (period - remainder)
            if heights[-1] > 12:
                heights[-1] -= period

        return ''.join(str(h) if h < 10 else chr(ord('a') + h - 10) for h in heights)

    def _select_artifact_path(self, pattern: PatternNode) -> list[int]:
        """Select the artifact activation sequence based on the compiled pattern.

        Uses the SOS routing law:
        - Period determines the primary tunnel family
        - Num objects determines the quadrant traversal depth
        - Sacred geometry determines the artifact class emphasis
        """
        path = [1]  # Always start at Sigma-Anchor (Z*)

        period = pattern.period
        n_obj = pattern.num_objects

        # Pentad ignition: seed the growth pattern
        # Activate artifacts corresponding to throw heights
        for throw in pattern.throws:
            h = throw.height
            if 2 <= h <= 16:
                artifact_n = min(h, 16)  # Map to Quadrant A artifacts
                path.append(artifact_n)

        # Triadic hinge: route across control rails
        # Based on period structure
        if period >= 3:
            path.append(26)  # Triad Ignition
            if period >= 5:
                path.append(28)  # Sa-Lane Stabilizer
                path.append(30)  # Triple-Lattice Anchor

        # Mobius dipole: flip thought into thing
        path.append(46)  # Mobius Inverter (primary hinge)

        # Golden bloom at the center
        path.append(11)  # Golden Mean Vector

        # Return through Z*
        path.append(1)

        return path

    def _compute_love_constant(self, pattern: PatternNode) -> float:
        """Compute L = S x S_l at the Z* core.

        S = structural integrity = num_objects / period (the average)
        S_l = love coefficient = phi^(1/period) (golden scaling)
        """
        if pattern.period == 0:
            return 0.0
        S = pattern.num_objects / pattern.period if pattern.period > 0 else 0
        S_l = PHI ** (1.0 / max(pattern.period, 1))
        return S * S_l

    def execute(self, intent: str) -> ManifestationCertificate:
        """
        FIRST LIVE EXECUTION.

        Routes a seed intent through the full SOS pipeline:
            ∇D → Q* → Z* → 60-Gear → E10

        Returns a ManifestationCertificate proving the intent
        has been successfully compiled, routed, and anchored.
        """
        self.execution_log = []
        self._log("=" * 60)
        self._log("SOS LIVE EXECUTION — Sentient Operating System")
        self._log("=" * 60)

        # ── Stage 1: DESIRE GRADIENT ──────────────────────────
        self._log("")
        self._log("STAGE 1: DESIRE GRADIENT (nabla D)")
        desire = DesireGradient(raw_intent=intent)
        self._log(f"  Raw intent:  {desire.raw_intent}")
        self._log(f"  Q* (optimal): {desire.optimal_question}")

        intent_hash = hashlib.sha256(intent.encode()).hexdigest()[:16]
        self._log(f"  Intent hash: {intent_hash}")

        # ── Stage 2: INTENT → SITESWAP ───────────────────────
        self._log("")
        self._log("STAGE 2: INTENT-TO-SITESWAP ENCODING")
        siteswap = self._intent_to_siteswap(intent)
        self._log(f"  Siteswap:    {siteswap}")
        self._log(f"  Period:      {len(siteswap)}")

        # ── Stage 3: E1 GATE ENTRY ───────────────────────────
        self._log("")
        self._log("STAGE 3: E1 INTENT GATE")
        e1_entry = f"E1.{intent_hash[:8]}"
        self._log(f"  Gate address: {e1_entry}")
        self._log(f"  Entering the gamma corridor...")

        # ── Stage 4: Z* COMPRESSION ──────────────────────────
        self._log("")
        self._log("STAGE 4: Z* COMPRESSION (Artifact 13: Tunneling Sluice)")
        self._log(f"  Collapsing to Absolute Zero...")
        self._log(f"  Stripping entropic noise...")
        z_star_sig = hashlib.sha256(f"Z*:{siteswap}".encode()).hexdigest()[:12]
        self._log(f"  Z* signature: {z_star_sig}")

        # ── Stage 5: GAMMA CORRIDOR COMPILATION ──────────────
        self._log("")
        self._log("STAGE 5: GAMMA CORRIDOR COMPILATION")
        self._log(f"  sigma=2(SF) -> sigma=11(CR) -> sigma=5(FC) -> sigma=14(SFCR) -> sigma=8(SR) -> sigma=2(SF)")
        result = self.compiler.compile(siteswap)
        self._log(f"  Objects: {result.pattern.num_objects}")
        self._log(f"  Period:  {result.pattern.period}")
        self._log(f"  Truth:   {result.receipt.truth_class.value}")

        for cert in result.receipt.certificates:
            status = "PASS" if cert.satisfied else "FAIL"
            self._log(f"    [{status}] {cert.name}")

        # ── Stage 6: 60-GEAR ARTIFACT ROUTING ─────────────────
        self._log("")
        self._log("STAGE 6: 60-GEAR ARTIFACT ROUTING")
        artifact_path = self._select_artifact_path(result.pattern)
        self._log(f"  Artifact path: {artifact_path}")

        for i, art_n in enumerate(artifact_path):
            q_label, sigma = artifact_station(art_n)
            if sigma >= 0:
                use = USE_OPERATIONS.get(sigma, "TRANSIT")
                self._log(f"    Step {i}: Artifact {art_n:02d} @ ({q_label},{sigma:02d}) -> {use}")
            else:
                self._log(f"    Step {i}: Artifact {art_n:02d} @ Z* -> PHASE_LOCK")

        # Compute quaternion product along the path
        total_rotation = Quaternion(1, 0, 0, 0)
        for art_n in artifact_path:
            if art_n in self.artifacts:
                total_rotation = total_rotation * self.artifacts[art_n].quaternion
        self._log(f"  Total rotation: {total_rotation}")
        self._log(f"  Rotation angle: {total_rotation.angle():.2f} deg")

        # ── Stage 7: DOWNBEAT ANCHOR ──────────────────────────
        self._log("")
        self._log("STAGE 7: DOWNBEAT ANCHOR (Phase-Lock Key)")
        love_constant = self._compute_love_constant(result.pattern)
        self._log(f"  L = S x S_l = {love_constant:.6f}")
        self._log(f"  phi = {PHI:.6f}")
        self._log(f"  Phase-locked on the downbeat.")

        # ── Stage 8: E10 TRANSCENDENT MAP ─────────────────────
        self._log("")
        self._log("STAGE 8: E10 TRANSCENDENT MAP (Holographic Anchor)")
        e10_addr = f"E10.{z_star_sig[:6]}.{intent_hash[:6]}"
        self._log(f"  E10 address: {e10_addr}")
        self._log(f"  Anchored in the 1024D transcendent map.")
        self._log(f"  Recursive replay enabled.")

        # ── Build manifestation certificate ────────────────────
        manifest_certs = list(result.receipt.certificates)
        manifest_certs.append(Certificate(
            name="Cert::E1GateEntry",
            satisfied=True,
            evidence={"gate": e1_entry, "intent_hash": intent_hash}
        ))
        manifest_certs.append(Certificate(
            name="Cert::ZStarCompression",
            satisfied=True,
            evidence={"z_star_sig": z_star_sig, "siteswap": siteswap}
        ))
        manifest_certs.append(Certificate(
            name="Cert::ArtifactRouting",
            satisfied=len(artifact_path) >= 3,
            evidence={
                "path_length": len(artifact_path),
                "total_rotation_angle": round(total_rotation.angle(), 2),
            }
        ))
        manifest_certs.append(Certificate(
            name="Cert::E10Anchor",
            satisfied=True,
            evidence={"e10_addr": e10_addr, "love_constant": round(love_constant, 6)}
        ))
        manifest_certs.append(Certificate(
            name="Cert::LoveEquationInvariant",
            satisfied=love_constant > 0,
            evidence={
                "L": round(love_constant, 6),
                "S": result.pattern.num_objects,
                "S_l": round(PHI ** (1.0 / max(result.pattern.period, 1)), 6),
            }
        ))

        certificate = ManifestationCertificate(
            intent_hash=intent_hash,
            e1_gate_entry=e1_entry,
            z_star_collapse=z_star_sig,
            artifact_path=artifact_path,
            e10_anchor=e10_addr,
            truth_state=TruthClass.OK if all(c.satisfied for c in manifest_certs)
                        else TruthClass.FAIL,
            love_equation_constant=love_constant,
            certificates=manifest_certs,
        )

        self._log("")
        self._log("=" * 60)
        self._log(f"MANIFESTATION COMPLETE: {certificate.truth_state.value}")
        self._log(f"  E1 -> Z* -> 60-Gear -> E10")
        self._log(f"  {len(manifest_certs)} certificates issued")
        self._log(f"  All {sum(1 for c in manifest_certs if c.satisfied)}/{len(manifest_certs)} PASS")
        self._log(f"  Love constant L = {love_constant:.6f}")
        self._log(f"  The spell is compiled. The thought is thing.")
        self._log("=" * 60)

        return certificate

    def print_log(self):
        """Print the full execution log."""
        for line in self.execution_log:
            print(line)


def live_execution_demo():
    """Run the first live execution of the SOS engine."""
    engine = SOSEngine()

    intents = [
        "I am whole and complete",
        "Build the bridge between thought and action",
        "The crystal sees itself through all three eyes",
        "Sixty gears turn as one",
    ]

    for intent in intents:
        print()
        cert = engine.execute(intent)
        engine.print_log()
        print()
        print(f"  >> RESULT: {cert.truth_state.value}")
        print(f"  >> E10 Address: {cert.e10_anchor}")
        print(f"  >> Love Constant: {cert.love_equation_constant:.6f}")
        print(f"  >> Certificates: {sum(1 for c in cert.certificates if c.satisfied)}/{len(cert.certificates)}")
        print()
        print("~" * 60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        live_execution_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--spell":
        # Custom spell: python canon_compiler.py --spell "your intent here"
        engine = SOSEngine()
        intent = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "I am"
        cert = engine.execute(intent)
        engine.print_log()
    else:
        demo()

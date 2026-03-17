"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Core Enumerations                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Fundamental enumerations that define the categorical structure of the framework.
These enums encode the quad-polar architecture, certificate levels, truth profiles,
and other discrete classifications.
"""

from enum import Enum, IntEnum, Flag, auto
from typing import Set, Tuple, Optional


class Pole(Enum):
    """
    The four fundamental poles of the operator simplex.
    
    These represent irreducible "modes of causation" in hybrid systems:
    - D (Dissipative): Contractive, smoothing, entropy-decreasing
    - Ω (Oscillatory): Phase-preserving, conservative, transport
    - Σ (Stochastic): Markovian expansion, mixing, noise injection
    - Ψ (Recursive): Scale transformation, coarse-graining, renormalization
    
    The poles form a tetrahedron (3-simplex) with six dyadic edges.
    """
    D = "dissipative"      # Fire archetype
    OMEGA = "oscillatory"  # Air archetype
    SIGMA = "stochastic"   # Water archetype
    PSI = "recursive"      # Earth archetype
    
    @property
    def symbol(self) -> str:
        """Greek symbol representation."""
        symbols = {
            Pole.D: "D",
            Pole.OMEGA: "Ω",
            Pole.SIGMA: "Σ",
            Pole.PSI: "Ψ"
        }
        return symbols[self]
    
    @property
    def element(self) -> 'Element':
        """Corresponding elemental archetype."""
        mapping = {
            Pole.D: Element.FIRE,
            Pole.OMEGA: Element.AIR,
            Pole.SIGMA: Element.WATER,
            Pole.PSI: Element.EARTH
        }
        return mapping[self]
    
    @property
    def opposite(self) -> 'Pole':
        """The conjugate/opposite pole (90° away, no direct tunneling)."""
        opposites = {
            Pole.D: Pole.SIGMA,      # Fire ↔ Water
            Pole.OMEGA: Pole.PSI,    # Air ↔ Earth
            Pole.SIGMA: Pole.D,
            Pole.PSI: Pole.OMEGA
        }
        return opposites[self]
    
    @property
    def adjacent(self) -> Tuple['Pole', 'Pole']:
        """The two adjacent poles (can tunnel via 90° rotation)."""
        adjacencies = {
            Pole.D: (Pole.OMEGA, Pole.PSI),
            Pole.OMEGA: (Pole.D, Pole.SIGMA),
            Pole.SIGMA: (Pole.OMEGA, Pole.PSI),
            Pole.PSI: (Pole.SIGMA, Pole.D)
        }
        return adjacencies[self]
    
    def can_tunnel_to(self, other: 'Pole') -> bool:
        """Check if direct tunneling (90° rotation) is allowed."""
        return other in self.adjacent


class Element(Enum):
    """
    The four elemental archetypes from the metaphysical backbone.
    
    These provide intuitive understanding of the poles:
    - FIRE: Initiation, impulse, gradient creation
    - AIR: Structure, relation, routing, navigation  
    - WATER: Adaptation, flow, optimization
    - EARTH: Constraint, embodiment, verification
    """
    FIRE = "fire"
    AIR = "air"
    WATER = "water"
    EARTH = "earth"
    
    @property
    def function(self) -> str:
        """Core function of this archetype."""
        functions = {
            Element.FIRE: "Initiation / impulse / ignition",
            Element.AIR: "Structure through relation / mapping / routing",
            Element.WATER: "Adaptation / flow / shaping",
            Element.EARTH: "Constraint / embodiment / verification"
        }
        return functions[self]
    
    @property
    def shadow(self) -> str:
        """Failure mode (shadow) of this archetype."""
        shadows = {
            Element.FIRE: "reckless forcing, premature collapse, overheat",
            Element.AIR: "over-analysis, detachment, endless branching",
            Element.WATER: "drift, dissolving boundaries, avoiding commitment",
            Element.EARTH: "rigidity, over-constraint, stagnation"
        }
        return shadows[self]
    
    @property
    def pole(self) -> Pole:
        """Corresponding operator pole."""
        mapping = {
            Element.FIRE: Pole.D,
            Element.AIR: Pole.OMEGA,
            Element.WATER: Pole.SIGMA,
            Element.EARTH: Pole.PSI
        }
        return mapping[self]
    
    def rotate_cw(self) -> 'Element':
        """Rotate 90° clockwise (spin direction)."""
        rotation = {
            Element.FIRE: Element.AIR,
            Element.AIR: Element.WATER,
            Element.WATER: Element.EARTH,
            Element.EARTH: Element.FIRE
        }
        return rotation[self]
    
    def rotate_ccw(self) -> 'Element':
        """Rotate 90° counter-clockwise (reverse spin)."""
        rotation = {
            Element.FIRE: Element.EARTH,
            Element.EARTH: Element.WATER,
            Element.WATER: Element.AIR,
            Element.AIR: Element.FIRE
        }
        return rotation[self]


class CertificateLevel(IntEnum):
    """
    Certificate evidence levels (L0-L3).
    
    Each level represents increasing rigor of justification:
    - L0: Claim with no evidence (assertion only)
    - L1: Empirical evidence (finite testing)
    - L2: Certified numeric evidence (conservative, checkable)
    - L3: Formal proof object (machine-verified)
    """
    L0_CLAIM = 0
    L1_EMPIRICAL = 1
    L2_CERTIFIED = 2
    L3_FORMAL = 3
    
    @property
    def description(self) -> str:
        descriptions = {
            CertificateLevel.L0_CLAIM: "Claim (no evidence)",
            CertificateLevel.L1_EMPIRICAL: "Empirical evidence (finite testing)",
            CertificateLevel.L2_CERTIFIED: "Certified numeric evidence (conservative, checkable)",
            CertificateLevel.L3_FORMAL: "Formal proof object (machine-verified)"
        }
        return descriptions[self]
    
    def satisfies(self, required: 'CertificateLevel') -> bool:
        """Check if this level satisfies the required level."""
        return self >= required


class TruthProfile(Enum):
    """
    Verification policy profiles.
    
    - EXPLORE: Discovery mode, candidates stored but never promoted
    - VALIDATE: Empirical checks permitted and enforced
    - PROVE: L2+ evidence required for all obligations
    """
    EXPLORE = "explore"
    VALIDATE = "validate"
    PROVE = "prove"
    
    @property
    def minimum_level(self) -> CertificateLevel:
        """Minimum certificate level required by this profile."""
        levels = {
            TruthProfile.EXPLORE: CertificateLevel.L0_CLAIM,
            TruthProfile.VALIDATE: CertificateLevel.L1_EMPIRICAL,
            TruthProfile.PROVE: CertificateLevel.L2_CERTIFIED
        }
        return levels[self]
    
    @property
    def allows_promotion(self) -> bool:
        """Whether artifacts can be promoted to ok_verified."""
        return self != TruthProfile.EXPLORE


class ConstraintType(Enum):
    """
    Types of constraints in the Constraint IR.
    """
    ROOT = "root"                       # H(x) = 0
    FIXED_POINT = "fixed_point"         # x = F(x)
    EQUALITY = "equality"               # F(x) = G(x)
    GENERATOR = "generator"             # T(x_k) = θ + kΔ
    VECTOR_ROOT = "vector_root"         # H(x) = 0 where H: R^n → R^n
    JET = "jet"                         # H^(k)(x*) = 0 for k=0,...,m-1
    CANCELLATION = "cancellation"       # Σ w_i F_i(x) = 0
    COMMUTATION = "commutation"         # F ∘ G = G ∘ F
    EQUIVARIANCE = "equivariance"       # F(φx) = φ^k F(x)
    PERIODICITY = "periodicity"         # F^∘n = Id


class NormalFormType(Enum):
    """
    Normal form types after constraint lowering.
    """
    SCALAR_ROOT = "scalar_root"
    SCALAR_FIXED_POINT = "scalar_fixed_point"
    GENERATOR_CONSTRAINT = "generator_constraint"
    VECTOR_ROOT = "vector_root"
    SINGULAR_SEED = "singular_seed"


class ObligationType(Enum):
    """
    Types of proof obligations generated from constraints.
    """
    CORRIDOR = "corridor"               # Chart admissibility
    ENCLOSURE = "enclosure"             # Conservative bracketing
    UNIQUENESS = "uniqueness"           # No other solutions in region
    CONTRACTION = "contraction"         # Lipschitz/contraction bounds
    REPLAY = "replay"                   # Deterministic reproduction
    STABILITY = "stability"             # Numerical stability
    TERMINATION = "termination"         # Algorithm terminates


class PlanStatus(Enum):
    """
    Status of a solve plan in the pipeline.
    """
    DRAFT = "draft"                     # Under construction
    COMPILED = "compiled"               # IR generated
    EXECUTING = "executing"             # Solver running
    COMPLETED = "completed"             # Outputs produced
    CERTIFIED = "certified"             # Certificates generated
    VERIFIED = "verified"               # Verifier approved
    FAILED = "failed"                   # Failed at some stage
    REJECTED = "rejected"               # Verifier rejected


class VerificationResult(Enum):
    """
    Outcome of verification.
    """
    OK_VERIFIED = "ok_verified"         # All obligations satisfied
    PARTIAL = "partial"                 # Some obligations satisfied
    FAILED = "failed"                   # Verification failed
    REPLAY_MISMATCH = "replay_mismatch" # Replay produced different result
    HASH_MISMATCH = "hash_mismatch"     # Content hash doesn't match
    POLICY_VIOLATION = "policy_violation" # Truth profile requirements not met
    TIMEOUT = "timeout"                 # Verification timed out
    ERROR = "error"                     # Internal error


class SolverType(Enum):
    """
    Types of solvers in the solver ladder.
    """
    BISECTION = "bisection"
    NEWTON = "newton"
    SECANT = "secant"
    BRENT = "brent"
    FIXED_POINT_ITERATION = "fixed_point_iteration"
    INTERVAL_NEWTON = "interval_newton"
    KRAWCZYK = "krawczyk"
    MOORE_KIOUSTELIDIS = "moore_kioustelidis"
    BRANCH_AND_BOUND = "branch_and_bound"
    CONTINUATION = "continuation"
    HOMOTOPY = "homotopy"


class IntervalMode(Enum):
    """
    Interval arithmetic modes.
    """
    OUTWARD = "outward"     # Conservative (rounded outward)
    INWARD = "inward"       # Anti-conservative (rounded inward)
    NEAREST = "nearest"     # Standard nearest rounding


class DyadicEdge(Enum):
    """
    The six dyadic interfaces (edges of the tetrahedron).
    """
    D_OMEGA = "D-Ω"         # Dissipation-Coherence
    D_SIGMA = "D-Σ"         # Dissipation-Stochastic
    D_PSI = "D-Ψ"           # Dissipation-Recursive
    OMEGA_SIGMA = "Ω-Σ"     # Coherence-Stochastic
    OMEGA_PSI = "Ω-Ψ"       # Coherence-Recursive
    SIGMA_PSI = "Σ-Ψ"       # Stochastic-Recursive
    
    @property
    def poles(self) -> Tuple[Pole, Pole]:
        """The two poles forming this edge."""
        mapping = {
            DyadicEdge.D_OMEGA: (Pole.D, Pole.OMEGA),
            DyadicEdge.D_SIGMA: (Pole.D, Pole.SIGMA),
            DyadicEdge.D_PSI: (Pole.D, Pole.PSI),
            DyadicEdge.OMEGA_SIGMA: (Pole.OMEGA, Pole.SIGMA),
            DyadicEdge.OMEGA_PSI: (Pole.OMEGA, Pole.PSI),
            DyadicEdge.SIGMA_PSI: (Pole.SIGMA, Pole.PSI),
        }
        return mapping[self]
    
    @property
    def is_principal_axis(self) -> bool:
        """Whether this is a principal axis (horizontal or vertical)."""
        return self in (DyadicEdge.D_OMEGA, DyadicEdge.SIGMA_PSI)
    
    @property
    def governs(self) -> str:
        """What interplay this dyad governs."""
        governance = {
            DyadicEdge.D_OMEGA: "dissipation-coherence interplay",
            DyadicEdge.SIGMA_PSI: "noise-law distillation interplay",
            DyadicEdge.D_SIGMA: "Langevin dynamics",
            DyadicEdge.D_PSI: "multigrid convergence",
            DyadicEdge.OMEGA_SIGMA: "quantum-classical transition",
            DyadicEdge.OMEGA_PSI: "wave-scale hierarchy",
        }
        return governance[self]


class CrystalLens(Enum):
    """
    The four lenses of Crystal Combat methodology.
    """
    SQUARE = "square"       # Invariants, Extremal, Counting, Graph
    FLOWER = "flower"       # Angles, Similarity, Power, Transform
    CLOUD = "cloud"         # Sample space, Conditioning, Expectation, Bounds
    FRACTAL = "fractal"     # Induction, Fixed points, Lyapunov, Split
    
    def rotate_spin(self) -> 'CrystalLens':
        """SPIN rotation: Square → Flower → Cloud → Fractal."""
        rotation = {
            CrystalLens.SQUARE: CrystalLens.FLOWER,
            CrystalLens.FLOWER: CrystalLens.CLOUD,
            CrystalLens.CLOUD: CrystalLens.FRACTAL,
            CrystalLens.FRACTAL: CrystalLens.SQUARE
        }
        return rotation[self]
    
    def rotate_rev_spin(self) -> 'CrystalLens':
        """REV-SPIN rotation: Fractal → Cloud → Flower → Square."""
        rotation = {
            CrystalLens.FRACTAL: CrystalLens.CLOUD,
            CrystalLens.CLOUD: CrystalLens.FLOWER,
            CrystalLens.FLOWER: CrystalLens.SQUARE,
            CrystalLens.SQUARE: CrystalLens.FRACTAL
        }
        return rotation[self]


class InvariantSpineComponent(Enum):
    """
    The four components of the universal invariant spine.
    """
    LEDGER = "ledger"           # Irreversible history (append-only)
    CORRIDOR = "corridor"       # Admissibility constraints
    PROOF = "proof"             # Checks that enable safe commit
    REPLAY = "replay"           # Deterministic re-derivation


class QuantumBasis(Enum):
    """
    Quantum mechanical basis representations.
    """
    POSITION = "position"       # |x⟩ - localized, particle-like
    MOMENTUM = "momentum"       # |p⟩ - wave-like, phase gradient
    ENERGY = "energy"           # |E⟩ - eigenstate
    TIME = "time"               # |t⟩ - temporal
    FREQUENCY = "frequency"     # |ω⟩ - spectral


class FlowType(Enum):
    """
    Types of evolution flows.
    """
    SEMIGROUP = "semigroup"             # Irreversible (t ≥ 0)
    GROUP = "group"                     # Reversible (t ∈ R)
    DISCRETE = "discrete"               # Discrete time steps
    HYBRID = "hybrid"                   # Mixed continuous/discrete


class CacheType(Enum):
    """
    Types of caches in the memory system (Ψ layer).
    """
    PACKING = "packing"         # Packed operand layouts
    FACTOR = "factor"           # Factorizations (SVD, etc.)
    PLAN = "plan"               # Solve plans
    EXPERIENCE = "experience"   # Performance statistics


# Flag enums for combining options

class ValidationFlags(Flag):
    """
    Flags for validation behavior.
    """
    NONE = 0
    CHECK_HASH = auto()
    CHECK_CERTIFICATES = auto()
    CHECK_REPLAY = auto()
    CHECK_OBLIGATIONS = auto()
    STRICT = CHECK_HASH | CHECK_CERTIFICATES | CHECK_REPLAY | CHECK_OBLIGATIONS


class SolverFlags(Flag):
    """
    Flags for solver behavior.
    """
    NONE = 0
    USE_INTERVALS = auto()
    ADAPTIVE_TOLERANCE = auto()
    EARLY_TERMINATION = auto()
    CERTIFICATE_GENERATION = auto()
    REPLAY_LOGGING = auto()
    DEFAULT = USE_INTERVALS | CERTIFICATE_GENERATION | REPLAY_LOGGING

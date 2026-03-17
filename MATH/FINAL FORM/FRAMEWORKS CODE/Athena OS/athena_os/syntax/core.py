"""
ATHENA OS - SYNTAX ALGEBRA CORE
===============================
The Many-Sorted Partial Algebra of Syntax

From SYNTAX.docx:

FOUR POLES (SORTS):
    S (SYNTAX): Executable artifacts at some representation level
    A (ANTI-SYNTAX): Collapse/erasure operators and artifacts
    I (IN-SYNTAX): Metatransformers and reifiers (code about code)
    O (OUT-SYNTAX): Obligations, contracts, and context

ALGEBRA STRUCTURE:
    ?? = (S, A, I, O; Ω)
    
    Where Ω is a typed signature in which every operation is
    total only where its phase and input sorts permit.

OBSERVABLE SEMANTICS:
    ⟦·⟧ : S × W ⇀ (Obs × W)
    
    W = world states
    Obs = observations (return values, traces, logs, state deltas)
    ⊥ = no observable completion
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Generic, TypeVar, Optional, Set, Dict, List, 
    Callable, Tuple, Any, Union, FrozenSet
)
from enum import Enum, auto
from abc import ABC, abstractmethod
import hashlib
from functools import cached_property


# =============================================================================
# POLE ENUMERATION
# =============================================================================

class Pole(Enum):
    """
    The four poles of the syntax algebra.
    
    Each pole represents a distinct sort in the many-sorted algebra.
    """
    
    S = "syntax"      # Executable artifacts
    A = "anti"        # Collapse/erasure
    I = "in"          # Metatransformers  
    O = "out"         # Obligations/context
    
    @property
    def symbol(self) -> str:
        """Get mathematical symbol."""
        return {
            Pole.S: "??",
            Pole.A: "??", 
            Pole.I: "??",
            Pole.O: "??"
        }[self]
    
    @property
    def description(self) -> str:
        """Get full description."""
        return {
            Pole.S: "SYNTAX - Executable artifacts",
            Pole.A: "ANTI-SYNTAX - Collapse/erasure operators",
            Pole.I: "IN-SYNTAX - Metatransformers (code about code)",
            Pole.O: "OUT-SYNTAX - Obligations and context"
        }[self]


# =============================================================================
# REPRESENTATION LEVELS
# =============================================================================

class RepLevel(Enum):
    """
    Representation tower levels.
    
    Txt → Str → Mid → Obs
    
    The arrows are families of partial maps (tokenize/parse/lower/compile/execute).
    """
    
    TXT = "text"      # Text/source
    STR = "struct"    # Structural (tokens/CST/AST)
    MID = "middle"    # Intermediate (IR/bytecode/CFG/SSA)
    OBS = "observe"   # Observables (traces/outputs/state)
    
    @property
    def symbol(self) -> str:
        return {
            RepLevel.TXT: "Txt",
            RepLevel.STR: "Str",
            RepLevel.MID: "Mid",
            RepLevel.OBS: "Obs"
        }[self]
    
    @property
    def order(self) -> int:
        """Position in the tower (lower = earlier)."""
        return {
            RepLevel.TXT: 0,
            RepLevel.STR: 1,
            RepLevel.MID: 2,
            RepLevel.OBS: 3
        }[self]
    
    def __lt__(self, other: 'RepLevel') -> bool:
        return self.order < other.order
    
    def __le__(self, other: 'RepLevel') -> bool:
        return self.order <= other.order


# =============================================================================
# DIRECTION (SPIN DYNAMICS)
# =============================================================================

class Direction(Enum):
    """
    Direction axis for SPIN dynamics.
    
    SPIN: Forward realization (source → execution)
    REV: Reverse abstraction (decompile/unparse/abstract)
    EQ: Equilibrium (round-trip/commutation regimes)
    DRIFT: Misalignment dynamics
    """
    
    SPIN = "spin"         # Forward realization
    REV = "reverse"       # Reverse abstraction
    EQ = "equilibrium"    # Round-trip balance
    DRIFT = "drift"       # Misalignment
    
    @property
    def symbol(self) -> str:
        return {
            Direction.SPIN: "↓",
            Direction.REV: "↑",
            Direction.EQ: "⇌",
            Direction.DRIFT: "∿"
        }[self]


# =============================================================================
# LENS FAMILIES
# =============================================================================

class LensFamily(Enum):
    """
    Lens-family axis packaging cross-pole interfaces.
    
    B_12: SYNTAX ↔ ANTI (execution/collapse)
    B_13: SYNTAX ↔ IN (code/metacode)
    B_14: SYNTAX ↔ OUT (implementation/obligation)
    B_outer: Outer shell (ANTI↔IN, ANTI↔OUT, IN↔OUT)
    """
    
    B12 = "syntax_anti"    # S ↔ A
    B13 = "syntax_in"      # S ↔ I
    B14 = "syntax_out"     # S ↔ O
    B_OUTER = "outer"      # A↔I, A↔O, I↔O
    
    @property
    def poles(self) -> Tuple[Pole, Pole]:
        """Get the two poles this lens connects."""
        return {
            LensFamily.B12: (Pole.S, Pole.A),
            LensFamily.B13: (Pole.S, Pole.I),
            LensFamily.B14: (Pole.S, Pole.O),
            LensFamily.B_OUTER: (Pole.A, Pole.I)  # Primary for outer
        }[self]


# =============================================================================
# BASE ARTIFACT TYPES
# =============================================================================

T = TypeVar('T')


@dataclass(frozen=True)
class Provenance:
    """
    Provenance tracking for artifacts.
    
    Records where an artifact came from and how it was derived.
    """
    
    source_id: str
    operation: str
    timestamp: float = 0.0
    parent_ids: Tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self) -> int:
        return hash((self.source_id, self.operation, self.timestamp, self.parent_ids))
    
    def chain(self, operation: str, new_id: str) -> 'Provenance':
        """Create chained provenance."""
        return Provenance(
            source_id=new_id,
            operation=operation,
            parent_ids=self.parent_ids + (self.source_id,),
            metadata=dict(self.metadata)
        )


@dataclass
class Artifact(ABC):
    """
    Base class for all syntax algebra artifacts.
    
    Every artifact has:
    - A pole (which sort it belongs to)
    - A representation level
    - Provenance tracking
    """
    
    pole: Pole
    rep_level: RepLevel
    provenance: Optional[Provenance] = None
    
    @property
    @abstractmethod
    def artifact_id(self) -> str:
        """Unique identifier for this artifact."""
        pass
    
    @property
    def sort_tag(self) -> str:
        """Get the sort tag for type checking."""
        return f"{self.pole.symbol}_{self.rep_level.symbol}"


# =============================================================================
# SYNTAX ARTIFACTS (S)
# =============================================================================

@dataclass
class SyntaxArtifact(Artifact):
    """
    SYNTAX (S): Executable artifact at some representation level.
    
    Not identified with "text" - it's a typed family S_R indexed
    by representation class R.
    """
    
    content: Any
    well_formed: bool = True
    executable: bool = True
    
    def __post_init__(self):
        object.__setattr__(self, 'pole', Pole.S)
    
    @property
    def artifact_id(self) -> str:
        content_hash = hashlib.sha256(str(self.content).encode()).hexdigest()[:16]
        return f"S_{self.rep_level.symbol}_{content_hash}"


@dataclass
class TextArtifact(SyntaxArtifact):
    """Source text artifact."""
    
    content: str
    encoding: str = "utf-8"
    
    def __post_init__(self):
        object.__setattr__(self, 'pole', Pole.S)
        object.__setattr__(self, 'rep_level', RepLevel.TXT)


@dataclass  
class StructArtifact(SyntaxArtifact):
    """Structural artifact (tokens/AST)."""
    
    content: Any  # Token list or AST
    grammar_id: Optional[str] = None
    
    def __post_init__(self):
        object.__setattr__(self, 'pole', Pole.S)
        object.__setattr__(self, 'rep_level', RepLevel.STR)


@dataclass
class MidArtifact(SyntaxArtifact):
    """Intermediate representation artifact."""
    
    content: Any  # IR/bytecode
    ir_type: str = "generic"
    
    def __post_init__(self):
        object.__setattr__(self, 'pole', Pole.S)
        object.__setattr__(self, 'rep_level', RepLevel.MID)


# =============================================================================
# ANTI-SYNTAX ARTIFACTS (A)
# =============================================================================

class CollapseKind(Enum):
    """
    Kinds of collapse/anti-syntax.
    
    ANTI-SYNTAX is a typed collapse family, not a single void.
    """
    
    LEXICAL = "lexical"       # Lexical erasure (bad tokens)
    SYNTACTIC = "syntactic"   # Parse failure
    SEMANTIC = "semantic"     # Type/semantic rejection
    DYNAMIC = "dynamic"       # Runtime collapse
    TIMEOUT = "timeout"       # Resource exhaustion
    ABORT = "abort"           # Explicit abort


class CollapsePhase(Enum):
    """Phase at which collapse occurred."""
    
    LEX = "lexical"
    PARSE = "parse"
    VALIDATE = "validate"
    RUNTIME = "runtime"


@dataclass
class AntiArtifact(Artifact):
    """
    ANTI-SYNTAX (A): Collapse/erasure artifact.
    
    Represents prevention, erasure, abort, or collapse of
    syntactic execution or transformation.
    """
    
    kind: CollapseKind
    phase: CollapsePhase
    message: str = ""
    recoverable: bool = False
    original_artifact_id: Optional[str] = None
    
    def __post_init__(self):
        object.__setattr__(self, 'pole', Pole.A)
        if not hasattr(self, 'rep_level') or self.rep_level is None:
            object.__setattr__(self, 'rep_level', RepLevel.OBS)
    
    @property
    def artifact_id(self) -> str:
        msg_hash = hashlib.sha256(self.message.encode()).hexdigest()[:8]
        return f"A_{self.kind.value}_{self.phase.value}_{msg_hash}"


# =============================================================================
# IN-SYNTAX ARTIFACTS (I)
# =============================================================================

@dataclass
class InArtifact(Artifact):
    """
    IN-SYNTAX (I): Metatransformer artifact.
    
    Realized as partial endomorphisms I ⊆ (S ⇀ S) with
    provenance requirements.
    """
    
    transform_name: str
    source_rep: RepLevel
    target_rep: RepLevel
    preserves_semantics: bool = True
    certified: bool = False
    
    def __post_init__(self):
        object.__setattr__(self, 'pole', Pole.I)
        object.__setattr__(self, 'rep_level', self.source_rep)
    
    @property
    def artifact_id(self) -> str:
        return f"I_{self.transform_name}_{self.source_rep.symbol}_{self.target_rep.symbol}"


@dataclass
class Transform(InArtifact):
    """
    A concrete transformation between representation levels.
    """
    
    transform_func: Optional[Callable[[SyntaxArtifact], SyntaxArtifact]] = None
    
    def apply(self, artifact: SyntaxArtifact) -> Union[SyntaxArtifact, AntiArtifact]:
        """Apply transformation."""
        if self.transform_func is None:
            return AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.VALIDATE,
                message="Transform function not defined",
                original_artifact_id=artifact.artifact_id
            )
        
        try:
            result = self.transform_func(artifact)
            if self.provenance:
                result.provenance = self.provenance.chain(
                    self.transform_name, 
                    result.artifact_id
                )
            return result
        except Exception as e:
            return AntiArtifact(
                kind=CollapseKind.DYNAMIC,
                phase=CollapsePhase.RUNTIME,
                message=str(e),
                original_artifact_id=artifact.artifact_id
            )


# =============================================================================
# OUT-SYNTAX ARTIFACTS (O)
# =============================================================================

@dataclass
class OutArtifact(Artifact):
    """
    OUT-SYNTAX (O): Obligation/context artifact.
    
    Typed obligations (contracts, invariants, policies, budgets,
    meaning commitments) with internal preorder ⪯.
    """
    
    obligation_type: str
    description: str
    strength: float = 1.0  # For preorder comparison
    
    def __post_init__(self):
        object.__setattr__(self, 'pole', Pole.O)
        object.__setattr__(self, 'rep_level', RepLevel.OBS)
    
    @property
    def artifact_id(self) -> str:
        desc_hash = hashlib.sha256(self.description.encode()).hexdigest()[:12]
        return f"O_{self.obligation_type}_{desc_hash}"
    
    def __le__(self, other: 'OutArtifact') -> bool:
        """Preorder: self ⪯ other means self is at most as strong as other."""
        if self.obligation_type != other.obligation_type:
            return False
        return self.strength <= other.strength


@dataclass
class Contract(OutArtifact):
    """A contract obligation with preconditions and postconditions."""
    
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'obligation_type', 'contract')


@dataclass
class Invariant(OutArtifact):
    """An invariant that must hold."""
    
    predicate: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'obligation_type', 'invariant')


@dataclass
class Policy(OutArtifact):
    """A policy constraint."""
    
    rules: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'obligation_type', 'policy')


# =============================================================================
# WORLD AND OBSERVATIONS
# =============================================================================

@dataclass
class WorldState:
    """
    World state W for execution semantics.
    
    External state, environment, resources.
    """
    
    state_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=dict)
    
    def copy(self) -> 'WorldState':
        """Create a copy of the world state."""
        return WorldState(
            state_id=f"{self.state_id}_copy",
            variables=dict(self.variables),
            resources=dict(self.resources)
        )


@dataclass  
class Observation:
    """
    Observation from execution.
    
    Return values, I/O traces, logs, state deltas.
    """
    
    return_value: Any = None
    traces: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    state_delta: Dict[str, Any] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    
    @property
    def is_bottom(self) -> bool:
        """Check if this is ⊥ (no observable completion)."""
        return (self.return_value is None and 
                not self.traces and 
                not self.logs)


# Special bottom observation
BOTTOM = Observation()


# =============================================================================
# EXECUTION SEMANTICS
# =============================================================================

class ExecutionResult:
    """
    Result of execution: ⟦p⟧(w) ∈ (Obs × W) ∪ {⊥}
    """
    
    def __init__(self, observation: Optional[Observation] = None,
                 new_state: Optional[WorldState] = None,
                 is_bottom: bool = False):
        self.observation = observation or BOTTOM
        self.new_state = new_state
        self._is_bottom = is_bottom or (observation is None)
    
    @property
    def is_bottom(self) -> bool:
        """Check if execution resulted in ⊥."""
        return self._is_bottom
    
    @classmethod
    def bottom(cls) -> 'ExecutionResult':
        """Create bottom result."""
        return cls(is_bottom=True)
    
    @classmethod
    def success(cls, obs: Observation, state: WorldState) -> 'ExecutionResult':
        """Create successful result."""
        return cls(observation=obs, new_state=state, is_bottom=False)


# =============================================================================
# SYNTAX ALGEBRA
# =============================================================================

@dataclass
class SyntaxAlgebra:
    """
    The Complete Syntax Algebra ?? = (S, A, I, O; Ω)
    
    A many-sorted partial algebra with:
    - S: Syntax artifacts (executable)
    - A: Anti-syntax artifacts (collapse/erasure)
    - I: In-syntax artifacts (metatransformers)
    - O: Out-syntax artifacts (obligations)
    - Ω: Typed operation signature
    """
    
    # Artifact registries
    syntax_artifacts: Dict[str, SyntaxArtifact] = field(default_factory=dict)
    anti_artifacts: Dict[str, AntiArtifact] = field(default_factory=dict)
    in_artifacts: Dict[str, InArtifact] = field(default_factory=dict)
    out_artifacts: Dict[str, OutArtifact] = field(default_factory=dict)
    
    def register(self, artifact: Artifact) -> str:
        """Register an artifact in the appropriate registry."""
        aid = artifact.artifact_id
        
        if artifact.pole == Pole.S:
            self.syntax_artifacts[aid] = artifact
        elif artifact.pole == Pole.A:
            self.anti_artifacts[aid] = artifact
        elif artifact.pole == Pole.I:
            self.in_artifacts[aid] = artifact
        elif artifact.pole == Pole.O:
            self.out_artifacts[aid] = artifact
        
        return aid
    
    def get(self, artifact_id: str) -> Optional[Artifact]:
        """Retrieve artifact by ID."""
        for registry in [self.syntax_artifacts, self.anti_artifacts,
                        self.in_artifacts, self.out_artifacts]:
            if artifact_id in registry:
                return registry[artifact_id]
        return None
    
    def count(self, pole: Optional[Pole] = None) -> int:
        """Count artifacts, optionally filtered by pole."""
        if pole is None:
            return (len(self.syntax_artifacts) + len(self.anti_artifacts) +
                   len(self.in_artifacts) + len(self.out_artifacts))
        
        registry = {
            Pole.S: self.syntax_artifacts,
            Pole.A: self.anti_artifacts,
            Pole.I: self.in_artifacts,
            Pole.O: self.out_artifacts
        }[pole]
        
        return len(registry)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_core() -> bool:
    """Validate core syntax module."""
    
    # Test Pole enum
    assert len(Pole) == 4
    assert Pole.S.symbol == "??"
    
    # Test RepLevel ordering
    assert RepLevel.TXT < RepLevel.STR < RepLevel.MID < RepLevel.OBS
    
    # Test Direction
    assert Direction.SPIN.symbol == "↓"
    assert Direction.REV.symbol == "↑"
    
    # Test SyntaxArtifact
    text_art = TextArtifact(
        content="x + 1",
        pole=Pole.S,
        rep_level=RepLevel.TXT
    )
    assert text_art.pole == Pole.S
    assert text_art.rep_level == RepLevel.TXT
    assert "S_Txt" in text_art.artifact_id
    
    # Test AntiArtifact
    anti = AntiArtifact(
        kind=CollapseKind.SYNTACTIC,
        phase=CollapsePhase.PARSE,
        message="Unexpected token",
        pole=Pole.A,
        rep_level=RepLevel.OBS
    )
    assert anti.pole == Pole.A
    assert "A_syntactic_parse" in anti.artifact_id
    
    # Test InArtifact
    transform = InArtifact(
        transform_name="tokenize",
        source_rep=RepLevel.TXT,
        target_rep=RepLevel.STR,
        pole=Pole.I,
        rep_level=RepLevel.TXT
    )
    assert transform.pole == Pole.I
    
    # Test OutArtifact
    contract = Contract(
        description="Input must be positive",
        preconditions=["x > 0"],
        postconditions=["result >= x"],
        pole=Pole.O,
        rep_level=RepLevel.OBS
    )
    assert contract.pole == Pole.O
    assert contract.obligation_type == "contract"
    
    # Test SyntaxAlgebra
    algebra = SyntaxAlgebra()
    aid = algebra.register(text_art)
    assert algebra.count(Pole.S) == 1
    assert algebra.get(aid) == text_art
    
    # Test WorldState and Observation
    world = WorldState(state_id="w0", variables={"x": 5})
    obs = Observation(return_value=6, traces=["computed"])
    assert not obs.is_bottom
    assert BOTTOM.is_bottom
    
    # Test ExecutionResult
    result = ExecutionResult.success(obs, world)
    assert not result.is_bottom
    assert ExecutionResult.bottom().is_bottom
    
    return True


if __name__ == "__main__":
    print("Validating SYNTAX core...")
    assert validate_core()
    print("✓ SYNTAX core validated")

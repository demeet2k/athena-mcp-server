"""
ATHENA OS - Quantum Holography Computing (QHC)
==============================================
Mode Words and Control Layer

From Quantum_Holography_Computing_(QHC).docx §1.2.1:

MODE WORDS:
    ?? = {0,1}^8 (8-bit control strings)
    
    Each mode word m encodes:
    - Basis type flags
    - Compression policy
    - Precision level
    - Semantic role (state/gate/noise/diagnostic)

CONTROL INTERFACE:
    Φ: ?? → ?? (policies)
    
    Maps mode words to operational policies:
    - Representation regime
    - Error tolerance
    - Compression parameters
    - Semantic tags

BOUNDARY-BULK SEPARATION:
    Boundary: mode words + control logic
    Bulk: tile configurations + state data
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, IntEnum, auto


# =============================================================================
# MODE WORD FIELDS
# =============================================================================

class RepresentationMode(IntEnum):
    """Representation regime (bits 0-1)."""
    DENSE = 0        # 00: Full dense vector
    SPARSE = 1       # 01: Sparse representation
    LOW_RANK = 2     # 10: Low-rank factorization
    ADAPTIVE = 3     # 11: Adaptive choice


class TileRole(IntEnum):
    """Tile role/function (bits 2-3)."""
    STATE = 0        # 00: State data
    GATE = 1         # 01: Gate/operator
    NOISE = 2        # 10: Noise channel
    DIAGNOSTIC = 3   # 11: Diagnostic/probe


class PrecisionLevel(IntEnum):
    """Precision/error discipline (bits 4-5)."""
    HIGH = 0         # 00: High precision (ε < 1e-10)
    MEDIUM = 1       # 01: Medium precision (ε < 1e-6)
    LOW = 2          # 10: Low precision (ε < 1e-3)
    ADAPTIVE = 3     # 11: Adaptive precision


class SemanticTag(IntEnum):
    """Semantic interpretation (bits 6-7)."""
    DEFAULT = 0      # 00: Default semantics
    DISCRETE = 1     # 01: Discrete/Earth
    CONTINUOUS = 2   # 10: Continuous/Water
    MIXED = 3        # 11: Mixed/adaptive


# =============================================================================
# MODE WORD
# =============================================================================

@dataclass
class ModeWord:
    """
    8-bit mode word encoding tile control settings.
    
    Layout:
        Bits 0-1: Representation mode
        Bits 2-3: Tile role
        Bits 4-5: Precision level
        Bits 6-7: Semantic tag
    """
    
    representation: RepresentationMode = RepresentationMode.DENSE
    role: TileRole = TileRole.STATE
    precision: PrecisionLevel = PrecisionLevel.MEDIUM
    semantic: SemanticTag = SemanticTag.DEFAULT
    
    def to_byte(self) -> int:
        """Encode as 8-bit integer."""
        return (
            self.representation.value |
            (self.role.value << 2) |
            (self.precision.value << 4) |
            (self.semantic.value << 6)
        )
    
    def to_bits(self) -> str:
        """Encode as bit string."""
        return format(self.to_byte(), '08b')
    
    @classmethod
    def from_byte(cls, byte: int) -> 'ModeWord':
        """Decode from 8-bit integer."""
        return cls(
            representation=RepresentationMode(byte & 0x03),
            role=TileRole((byte >> 2) & 0x03),
            precision=PrecisionLevel((byte >> 4) & 0x03),
            semantic=SemanticTag((byte >> 6) & 0x03)
        )
    
    @classmethod
    def from_bits(cls, bits: str) -> 'ModeWord':
        """Decode from bit string."""
        return cls.from_byte(int(bits, 2))
    
    def __repr__(self) -> str:
        return f"Mode({self.to_bits()})"
    
    # Common presets
    @classmethod
    def default(cls) -> 'ModeWord':
        """Default mode: dense state, medium precision."""
        return cls()
    
    @classmethod
    def high_precision_state(cls) -> 'ModeWord':
        """High precision state tile."""
        return cls(
            representation=RepresentationMode.DENSE,
            role=TileRole.STATE,
            precision=PrecisionLevel.HIGH
        )
    
    @classmethod
    def sparse_state(cls) -> 'ModeWord':
        """Sparse representation state."""
        return cls(
            representation=RepresentationMode.SPARSE,
            role=TileRole.STATE,
            precision=PrecisionLevel.MEDIUM
        )
    
    @classmethod
    def gate_tile(cls) -> 'ModeWord':
        """Gate/operator tile."""
        return cls(
            representation=RepresentationMode.DENSE,
            role=TileRole.GATE,
            precision=PrecisionLevel.HIGH
        )
    
    @classmethod
    def diagnostic_tile(cls) -> 'ModeWord':
        """Diagnostic/probe tile."""
        return cls(
            representation=RepresentationMode.DENSE,
            role=TileRole.DIAGNOSTIC,
            precision=PrecisionLevel.LOW
        )


# =============================================================================
# POLICY
# =============================================================================

@dataclass
class Policy:
    """
    Operational policy derived from mode word.
    
    Specifies concrete parameters for tile operations.
    """
    
    # Representation
    storage_format: str = "dense"
    compression_enabled: bool = False
    compression_threshold: float = 0.0
    max_rank: int = 0
    
    # Precision
    error_tolerance: float = 1e-6
    coefficient_threshold: float = 1e-10
    
    # Role-specific
    is_mutable: bool = True
    track_gradients: bool = False
    
    # Semantic
    allow_approximation: bool = True
    preserve_normalization: bool = True
    
    @classmethod
    def from_mode(cls, mode: ModeWord) -> 'Policy':
        """Create policy from mode word."""
        policy = cls()
        
        # Representation
        if mode.representation == RepresentationMode.DENSE:
            policy.storage_format = "dense"
            policy.compression_enabled = False
        elif mode.representation == RepresentationMode.SPARSE:
            policy.storage_format = "sparse"
            policy.compression_threshold = 1e-10
        elif mode.representation == RepresentationMode.LOW_RANK:
            policy.storage_format = "low_rank"
            policy.compression_enabled = True
            policy.max_rank = 16
        else:  # ADAPTIVE
            policy.storage_format = "adaptive"
            policy.compression_enabled = True
        
        # Precision
        if mode.precision == PrecisionLevel.HIGH:
            policy.error_tolerance = 1e-10
            policy.coefficient_threshold = 1e-14
        elif mode.precision == PrecisionLevel.MEDIUM:
            policy.error_tolerance = 1e-6
            policy.coefficient_threshold = 1e-10
        elif mode.precision == PrecisionLevel.LOW:
            policy.error_tolerance = 1e-3
            policy.coefficient_threshold = 1e-6
        else:  # ADAPTIVE
            policy.error_tolerance = 1e-6
            policy.allow_approximation = True
        
        # Role
        if mode.role == TileRole.STATE:
            policy.is_mutable = True
            policy.preserve_normalization = True
        elif mode.role == TileRole.GATE:
            policy.is_mutable = False
            policy.preserve_normalization = False
        elif mode.role == TileRole.NOISE:
            policy.is_mutable = True
            policy.track_gradients = False
        else:  # DIAGNOSTIC
            policy.is_mutable = False
            policy.error_tolerance = 1e-3
        
        return policy


# =============================================================================
# MODE TRANSITION
# =============================================================================

class ModeTransitionType(Enum):
    """Types of mode transitions."""
    COMPRESS = "compress"        # Dense → Sparse/LowRank
    DECOMPRESS = "decompress"    # Sparse/LowRank → Dense
    PRECISION_UP = "precision_up"
    PRECISION_DOWN = "precision_down"
    ROLE_CHANGE = "role_change"


@dataclass
class ModeTransition:
    """
    Transition between mode words.
    """
    
    source: ModeWord
    target: ModeWord
    transition_type: ModeTransitionType
    cost: float = 0.0  # Computational cost estimate
    
    @classmethod
    def compress(cls, source: ModeWord) -> 'ModeTransition':
        """Create compression transition."""
        target = ModeWord(
            representation=RepresentationMode.SPARSE,
            role=source.role,
            precision=source.precision,
            semantic=source.semantic
        )
        return cls(source, target, ModeTransitionType.COMPRESS, cost=1.0)
    
    @classmethod
    def decompress(cls, source: ModeWord) -> 'ModeTransition':
        """Create decompression transition."""
        target = ModeWord(
            representation=RepresentationMode.DENSE,
            role=source.role,
            precision=source.precision,
            semantic=source.semantic
        )
        return cls(source, target, ModeTransitionType.DECOMPRESS, cost=0.5)


# =============================================================================
# CONTROL INTERFACE
# =============================================================================

@dataclass
class ControlInterface:
    """
    Control interface mapping mode words to policies.
    
    Implements Φ: ?? → ??
    """
    
    # Mode assignments per tile
    tile_modes: Dict[int, ModeWord] = field(default_factory=dict)
    
    # Global policy overrides
    global_precision: Optional[PrecisionLevel] = None
    global_max_rank: Optional[int] = None
    
    # Transition rules
    auto_compress: bool = True
    compress_threshold: float = 0.1  # Sparsity threshold
    
    def get_mode(self, tile_id: int) -> ModeWord:
        """Get mode word for tile."""
        return self.tile_modes.get(tile_id, ModeWord.default())
    
    def set_mode(self, tile_id: int, mode: ModeWord) -> None:
        """Set mode word for tile."""
        self.tile_modes[tile_id] = mode
    
    def get_policy(self, tile_id: int) -> Policy:
        """Get policy for tile (Φ(m))."""
        mode = self.get_mode(tile_id)
        policy = Policy.from_mode(mode)
        
        # Apply global overrides
        if self.global_precision is not None:
            if self.global_precision == PrecisionLevel.HIGH:
                policy.error_tolerance = 1e-10
            elif self.global_precision == PrecisionLevel.LOW:
                policy.error_tolerance = 1e-3
        
        if self.global_max_rank is not None:
            policy.max_rank = self.global_max_rank
        
        return policy
    
    def transition(self, tile_id: int, transition: ModeTransition) -> None:
        """Apply mode transition."""
        current = self.get_mode(tile_id)
        if current.to_byte() != transition.source.to_byte():
            raise ValueError("Transition source doesn't match current mode")
        self.set_mode(tile_id, transition.target)
    
    def suggest_compression(self, tile_id: int, sparsity: float) -> Optional[ModeTransition]:
        """Suggest compression if beneficial."""
        if not self.auto_compress:
            return None
        
        mode = self.get_mode(tile_id)
        if mode.representation == RepresentationMode.DENSE and sparsity < self.compress_threshold:
            return ModeTransition.compress(mode)
        
        return None
    
    def broadcast_precision(self, level: PrecisionLevel) -> None:
        """Broadcast precision level to all tiles."""
        for tile_id in self.tile_modes:
            mode = self.tile_modes[tile_id]
            self.tile_modes[tile_id] = ModeWord(
                representation=mode.representation,
                role=mode.role,
                precision=level,
                semantic=mode.semantic
            )
    
    def summary(self) -> Dict[str, Any]:
        """Get control interface summary."""
        role_counts = {r: 0 for r in TileRole}
        rep_counts = {r: 0 for r in RepresentationMode}
        
        for mode in self.tile_modes.values():
            role_counts[mode.role] += 1
            rep_counts[mode.representation] += 1
        
        return {
            "num_tiles": len(self.tile_modes),
            "role_distribution": {r.name: c for r, c in role_counts.items()},
            "representation_distribution": {r.name: c for r, c in rep_counts.items()},
            "global_precision": self.global_precision.name if self.global_precision else "default",
            "auto_compress": self.auto_compress
        }


# =============================================================================
# FIBRE SYMMETRY (Z₂×Z₂)
# =============================================================================

class FibreState(Enum):
    """
    4-state Z₂×Z₂ internal fibre symmetry.
    
    Captures spin/charge-like structure.
    """
    
    PLUS_PLUS = 0    # (+,+)
    PLUS_MINUS = 1   # (+,-)
    MINUS_PLUS = 2   # (-,+)
    MINUS_MINUS = 3  # (-,-)
    
    @property
    def parity_1(self) -> int:
        """First Z₂ parity."""
        return 1 if self.value in [0, 1] else -1
    
    @property
    def parity_2(self) -> int:
        """Second Z₂ parity."""
        return 1 if self.value in [0, 2] else -1
    
    def flip_1(self) -> 'FibreState':
        """Flip first parity."""
        mapping = {0: 2, 1: 3, 2: 0, 3: 1}
        return FibreState(mapping[self.value])
    
    def flip_2(self) -> 'FibreState':
        """Flip second parity."""
        mapping = {0: 1, 1: 0, 2: 3, 3: 2}
        return FibreState(mapping[self.value])
    
    @classmethod
    def from_parities(cls, p1: int, p2: int) -> 'FibreState':
        """Create from parity values (±1)."""
        if p1 > 0 and p2 > 0:
            return cls.PLUS_PLUS
        elif p1 > 0 and p2 < 0:
            return cls.PLUS_MINUS
        elif p1 < 0 and p2 > 0:
            return cls.MINUS_PLUS
        else:
            return cls.MINUS_MINUS


@dataclass
class FibreDescriptor:
    """
    Fibre structure for a tile.
    
    Extends mode word with internal symmetry.
    """
    
    mode: ModeWord
    fibre_state: FibreState = FibreState.PLUS_PLUS
    fibre_dimension: int = 4  # |Z₂×Z₂| = 4
    
    # Per-fibre amplitudes (optional refinement)
    fibre_weights: List[float] = field(default_factory=lambda: [0.25, 0.25, 0.25, 0.25])
    
    def dominant_fibre(self) -> FibreState:
        """Get fibre state with largest weight."""
        max_idx = max(range(4), key=lambda i: self.fibre_weights[i])
        return FibreState(max_idx)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_modewords() -> bool:
    """Validate mode words module."""
    
    # Test ModeWord encoding
    mode = ModeWord(
        representation=RepresentationMode.SPARSE,
        role=TileRole.STATE,
        precision=PrecisionLevel.HIGH,
        semantic=SemanticTag.DISCRETE
    )
    
    byte_val = mode.to_byte()
    decoded = ModeWord.from_byte(byte_val)
    
    assert decoded.representation == mode.representation
    assert decoded.role == mode.role
    assert decoded.precision == mode.precision
    assert decoded.semantic == mode.semantic
    
    # Test bit string
    bits = mode.to_bits()
    assert len(bits) == 8
    from_bits = ModeWord.from_bits(bits)
    assert from_bits.to_byte() == mode.to_byte()
    
    # Test presets
    default = ModeWord.default()
    assert default.representation == RepresentationMode.DENSE
    
    gate = ModeWord.gate_tile()
    assert gate.role == TileRole.GATE
    
    # Test Policy
    policy = Policy.from_mode(mode)
    assert policy.storage_format == "sparse"
    assert policy.error_tolerance == 1e-10
    
    # Test ControlInterface
    control = ControlInterface()
    control.set_mode(0, mode)
    assert control.get_mode(0).to_byte() == mode.to_byte()
    
    policy = control.get_policy(0)
    assert policy.storage_format == "sparse"
    
    # Test transitions
    trans = ModeTransition.decompress(mode)
    assert trans.target.representation == RepresentationMode.DENSE
    
    # Test FibreState
    fs = FibreState.PLUS_MINUS
    assert fs.parity_1 == 1
    assert fs.parity_2 == -1
    assert fs.flip_2() == FibreState.PLUS_PLUS
    
    return True


if __name__ == "__main__":
    print("Validating QHC Mode Words Module...")
    assert validate_modewords()
    print("✓ Mode Words module validated")
    
    # Demo
    print("\n=== QHC Mode Words Demo ===")
    
    # Create and display mode words
    modes = [
        ("Default", ModeWord.default()),
        ("High Precision", ModeWord.high_precision_state()),
        ("Sparse", ModeWord.sparse_state()),
        ("Gate", ModeWord.gate_tile()),
        ("Diagnostic", ModeWord.diagnostic_tile()),
    ]
    
    print("\nMode Word Presets:")
    for name, mode in modes:
        print(f"  {name}: {mode.to_bits()}")
        print(f"    Rep: {mode.representation.name}, Role: {mode.role.name}")
        print(f"    Precision: {mode.precision.name}, Semantic: {mode.semantic.name}")
    
    # Control interface
    print("\nControl Interface:")
    control = ControlInterface()
    for i, (name, mode) in enumerate(modes):
        control.set_mode(i, mode)
    
    summary = control.summary()
    print(f"  Tiles: {summary['num_tiles']}")
    print(f"  Role distribution: {summary['role_distribution']}")
    print(f"  Representation distribution: {summary['representation_distribution']}")
    
    # Fibre symmetry
    print("\nFibre Symmetry (Z₂×Z₂):")
    for fs in FibreState:
        print(f"  {fs.name}: parity=({fs.parity_1:+d}, {fs.parity_2:+d})")

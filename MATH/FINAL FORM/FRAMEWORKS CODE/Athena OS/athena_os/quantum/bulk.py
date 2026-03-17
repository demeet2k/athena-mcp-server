"""
ATHENA OS - QHC Bulk Representation
===================================
Block-tree tiles, mode words, and error ledger for adaptive Hilbert space decomposition.

The bulk representation consists of:

1. Block-Tree Tiles: Hierarchical decomposition of Hilbert space
   - Each tile has: basis chart, core payload, metadata, κ-texture, content hash
   - Tiles can be: dense, sparse, low-rank, dictionary-compressed, quantized
   - Tree structure tracks factorizations of qubit subsets

2. Mode Words: Boundary control for each tile/scope
   - Representation class and basis chart identifiers
   - Compression method and parameters
   - Precision discipline and determinism constraints
   - Admissible operations and patch corridors
   - Internal fibre symmetries (e.g., Z₂×Z₂)

3. Error Ledger: Budget tracking for approximations
   - ε_budget, ε_used, ε_remaining (deterministic error)
   - δ_budget, δ_used, δ_remaining (probabilistic error)
   - Conservative aggregation rules
   - Rollback + monotone refinement

4. κ-Metrics: Representational health indicators
   - Conditioning, coherence, texture, entropy proxies
   - κ-corridors for admissible execution
"""

from __future__ import annotations
from enum import IntEnum, Flag, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Union
import numpy as np
import hashlib
import time


# =============================================================================
# MODE WORD - BOUNDARY CONTROL
# =============================================================================

class BasisChart(IntEnum):
    """Basis chart identifiers for tile representation."""
    COMPUTATIONAL = 0   # Standard |0⟩, |1⟩ basis
    PAULI_STABILIZER = 1  # Stabilizer / Pauli basis
    FOURIER_QFT = 2      # QFT-aligned basis
    WAVELET = 3          # Wavelet / polynomial basis
    CUSTOM = 4           # Custom certified basis


class CompressionMethod(IntEnum):
    """Compression methods for tile payloads."""
    DENSE = 0           # Full dense storage
    SPARSE = 1          # Sparse storage (threshold-based)
    LOW_RANK = 2        # Low-rank factorization
    DICTIONARY = 3      # Dictionary compression
    QUANTIZED = 4       # Quantized coefficients
    MPS = 5             # Matrix Product State
    TUCKER = 6          # Tucker decomposition


class PrecisionDiscipline(IntEnum):
    """Precision and rounding discipline."""
    EXACT = 0           # Exact arithmetic (if possible)
    FLOAT64 = 1         # Double precision
    FLOAT32 = 2         # Single precision
    FLOAT16 = 3         # Half precision
    FIXED = 4           # Fixed point
    INTERVAL = 5        # Interval arithmetic


class DeterminismLevel(IntEnum):
    """Determinism constraints."""
    FULLY_DETERMINISTIC = 0   # No randomness
    SEEDED_RANDOM = 1         # Random but seeded
    PROBABILISTIC = 2         # Probabilistic with bounds
    HEURISTIC = 3             # Heuristic (not verified)


class OperationRole(IntEnum):
    """Operational role for mode word."""
    APPLY = 0           # Apply gate/channel
    CHANGE = 1          # Basis change
    MEASURE = 2         # Measurement
    RESTRUCTURE = 3     # Tile restructuring
    CERTIFY = 4         # Certificate generation
    DIAGNOSE = 5        # Diagnostic operation


@dataclass
class FibreSymmetry:
    """
    Internal fibre symmetry for semantic tagging.
    
    E.g., Z₂×Z₂ for parity sectors.
    """
    group: str  # e.g., "Z2", "Z2xZ2", "U1"
    charge: Tuple[int, ...] = (0,)  # Charge quantum numbers
    
    def is_compatible(self, other: 'FibreSymmetry') -> bool:
        """Check if symmetries are compatible."""
        return self.group == other.group


@dataclass
class ModeWord:
    """
    Mode word: compact specification of tile/scope control.
    
    This is the "boundary" in the boundary/bulk split.
    """
    # Representation
    basis_chart: BasisChart = BasisChart.COMPUTATIONAL
    compression_method: CompressionMethod = CompressionMethod.DENSE
    
    # Precision
    precision: PrecisionDiscipline = PrecisionDiscipline.FLOAT64
    tolerance: float = 1e-10
    
    # Determinism
    determinism: DeterminismLevel = DeterminismLevel.FULLY_DETERMINISTIC
    rng_seed: Optional[int] = None
    
    # Operations
    role: OperationRole = OperationRole.APPLY
    
    # Admissible operations
    allow_restructure: bool = True
    allow_basis_change: bool = True
    max_rank: Optional[int] = None  # For low-rank methods
    
    # Symmetry
    fibre_symmetry: Optional[FibreSymmetry] = None
    
    # Semantic tags
    tags: Set[str] = field(default_factory=set)
    
    # Version
    version: int = 1
    
    def to_bytes(self) -> bytes:
        """Serialize mode word to bytes."""
        parts = [
            self.basis_chart.value.to_bytes(1, 'big'),
            self.compression_method.value.to_bytes(1, 'big'),
            self.precision.value.to_bytes(1, 'big'),
            self.determinism.value.to_bytes(1, 'big'),
            self.role.value.to_bytes(1, 'big'),
            bytes([self.allow_restructure, self.allow_basis_change]),
        ]
        return b''.join(parts)
    
    def is_compatible(self, other: 'ModeWord') -> bool:
        """Check if two mode words are compatible for composition."""
        # Basic compatibility: same precision discipline
        if self.precision != other.precision:
            return False
        
        # Symmetry compatibility
        if self.fibre_symmetry and other.fibre_symmetry:
            if not self.fibre_symmetry.is_compatible(other.fibre_symmetry):
                return False
        
        return True
    
    def evolve(self, new_role: OperationRole) -> 'ModeWord':
        """Create evolved mode word with new role."""
        return ModeWord(
            basis_chart=self.basis_chart,
            compression_method=self.compression_method,
            precision=self.precision,
            tolerance=self.tolerance,
            determinism=self.determinism,
            rng_seed=self.rng_seed,
            role=new_role,
            allow_restructure=self.allow_restructure,
            allow_basis_change=self.allow_basis_change,
            max_rank=self.max_rank,
            fibre_symmetry=self.fibre_symmetry,
            tags=self.tags.copy(),
            version=self.version + 1
        )


# =============================================================================
# ERROR LEDGER - BUDGET TRACKING
# =============================================================================

@dataclass
class ErrorBudget:
    """
    Error budget for a single tile/scope.
    
    Tracks:
    - ε: deterministic error bound
    - δ: probabilistic failure bound
    """
    epsilon_budget: float = 1e-6    # Total allowed deterministic error
    epsilon_used: float = 0.0       # Consumed deterministic error
    
    delta_budget: float = 1e-6      # Total allowed failure probability
    delta_used: float = 0.0         # Consumed failure probability
    
    @property
    def epsilon_remaining(self) -> float:
        """Remaining deterministic error budget."""
        return max(0.0, self.epsilon_budget - self.epsilon_used)
    
    @property
    def delta_remaining(self) -> float:
        """Remaining probabilistic error budget."""
        return max(0.0, self.delta_budget - self.delta_used)
    
    @property
    def is_exhausted(self) -> bool:
        """Check if budget is exhausted."""
        return self.epsilon_remaining <= 0 or self.delta_remaining <= 0
    
    def consume(self, epsilon: float = 0.0, delta: float = 0.0) -> bool:
        """
        Consume error budget. Returns True if successful, False if would exceed.
        """
        if epsilon > self.epsilon_remaining or delta > self.delta_remaining:
            return False
        
        self.epsilon_used += epsilon
        self.delta_used += delta
        return True
    
    def can_afford(self, epsilon: float = 0.0, delta: float = 0.0) -> bool:
        """Check if budget can afford this consumption."""
        return epsilon <= self.epsilon_remaining and delta <= self.delta_remaining


@dataclass
class ErrorLedger:
    """
    Global error ledger for QHC execution.
    
    Maintains hierarchical budget tracking with conservative aggregation.
    """
    # Global budgets
    global_epsilon: float = 1e-4
    global_delta: float = 1e-4
    
    # Tile-level budgets
    tile_budgets: Dict[str, ErrorBudget] = field(default_factory=dict)
    
    # Consumption history
    history: List[Tuple[str, float, float, str]] = field(default_factory=list)
    
    # Aggregation mode
    aggregation_mode: str = "linear"  # "linear" or "rms"
    
    def create_tile_budget(self, tile_id: str, epsilon_fraction: float = 0.1,
                          delta_fraction: float = 0.1) -> ErrorBudget:
        """Create a budget for a tile, drawing from global pool."""
        budget = ErrorBudget(
            epsilon_budget=self.global_epsilon * epsilon_fraction,
            delta_budget=self.global_delta * delta_fraction
        )
        self.tile_budgets[tile_id] = budget
        return budget
    
    def consume(self, tile_id: str, epsilon: float, delta: float, reason: str) -> bool:
        """Consume budget for a tile operation."""
        if tile_id not in self.tile_budgets:
            return False
        
        budget = self.tile_budgets[tile_id]
        success = budget.consume(epsilon, delta)
        
        if success:
            self.history.append((tile_id, epsilon, delta, reason))
        
        return success
    
    def total_used(self) -> Tuple[float, float]:
        """Get total used (ε, δ) across all tiles."""
        eps_total = sum(b.epsilon_used for b in self.tile_budgets.values())
        delta_total = sum(b.delta_used for b in self.tile_budgets.values())
        return eps_total, delta_total
    
    def aggregate_bound(self) -> Tuple[float, float]:
        """
        Compute conservative aggregate bound.
        
        Linear aggregation: ε_total = Σ ε_i, δ_total = Σ δ_i
        RMS aggregation: ε_total = √(Σ ε_i²) (requires additional certification)
        """
        eps_total, delta_total = self.total_used()
        
        if self.aggregation_mode == "rms":
            eps_list = [b.epsilon_used for b in self.tile_budgets.values()]
            eps_total = np.sqrt(sum(e**2 for e in eps_list))
        
        return eps_total, delta_total
    
    def is_within_budget(self) -> bool:
        """Check if total consumption is within global budget."""
        eps, delta = self.aggregate_bound()
        return eps <= self.global_epsilon and delta <= self.global_delta
    
    def summary(self) -> Dict[str, Any]:
        """Generate ledger summary."""
        eps_total, delta_total = self.aggregate_bound()
        return {
            'global_epsilon': self.global_epsilon,
            'global_delta': self.global_delta,
            'epsilon_used': eps_total,
            'delta_used': delta_total,
            'epsilon_remaining': self.global_epsilon - eps_total,
            'delta_remaining': self.global_delta - delta_total,
            'n_tiles': len(self.tile_budgets),
            'n_operations': len(self.history),
            'within_budget': self.is_within_budget()
        }


# =============================================================================
# BLOCK-TREE TILES - ADAPTIVE HILBERT DECOMPOSITION
# =============================================================================

@dataclass
class TilePayload:
    """
    Core payload of a block-tree tile.
    
    Contains the actual quantum state data in the specified format.
    """
    format: CompressionMethod
    data: Any  # np.ndarray or compressed representation
    
    # For sparse format
    indices: Optional[np.ndarray] = None
    
    # For low-rank format
    factors: Optional[Tuple[np.ndarray, ...]] = None
    rank: Optional[int] = None
    
    # Residual/error from compression
    residual_norm: float = 0.0
    
    def to_dense(self) -> np.ndarray:
        """Convert to dense representation."""
        if self.format == CompressionMethod.DENSE:
            return self.data
        elif self.format == CompressionMethod.SPARSE:
            # Reconstruct from sparse
            dense = np.zeros_like(self.data)
            dense[self.indices] = self.data[self.indices]
            return dense
        elif self.format == CompressionMethod.LOW_RANK:
            # Reconstruct from factors
            if len(self.factors) == 2:
                return self.factors[0] @ self.factors[1]
            else:
                raise NotImplementedError("Multi-factor reconstruction")
        else:
            raise NotImplementedError(f"Conversion from {self.format}")


@dataclass
class KappaTexture:
    """
    κ-texture metrics for representational health.
    
    Used for corridor enforcement and planning.
    """
    # Conditioning
    condition_number: float = 1.0
    
    # Coherence
    coherence: float = 1.0
    
    # Entropy proxy (normalized)
    entropy_proxy: float = 0.0
    
    # Entanglement measure
    entanglement_measure: float = 0.0
    
    # Compression ratio achieved
    compression_ratio: float = 1.0
    
    def health_score(self) -> float:
        """Compute overall health score in [0, 1]."""
        # Lower is better for condition number, higher for coherence
        cond_score = 1.0 / (1.0 + np.log1p(self.condition_number))
        return (self.coherence + cond_score) / 2.0
    
    def is_in_corridor(self, corridor: 'KappaCorridor') -> bool:
        """Check if metrics are within corridor bounds."""
        return (corridor.min_coherence <= self.coherence <= corridor.max_coherence and
                self.condition_number <= corridor.max_condition and
                self.entropy_proxy <= corridor.max_entropy)


@dataclass
class KappaCorridor:
    """
    κ-corridor: bounds on representational health metrics.
    """
    min_coherence: float = 0.5
    max_coherence: float = 1.0
    max_condition: float = 1e10
    max_entropy: float = 1.0


@dataclass
class BlockTreeTile:
    """
    A tile in the block-tree decomposition.
    
    Each tile represents a subspace of the global Hilbert space
    with adaptive representation.
    """
    # Identity
    tile_id: str
    qubit_subset: Set[int]  # Which qubits this tile covers
    
    # Hierarchical structure
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    
    # Payload
    payload: Optional[TilePayload] = None
    
    # Control
    mode_word: ModeWord = field(default_factory=ModeWord)
    
    # Health metrics
    kappa: KappaTexture = field(default_factory=KappaTexture)
    
    # Error budget
    budget: ErrorBudget = field(default_factory=ErrorBudget)
    
    # Content addressing
    content_hash: Optional[str] = None
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.content_hash is None:
            self.compute_hash()
    
    def compute_hash(self) -> str:
        """Compute content hash for the tile."""
        hasher = hashlib.sha256()
        hasher.update(self.tile_id.encode())
        hasher.update(str(sorted(self.qubit_subset)).encode())
        hasher.update(self.mode_word.to_bytes())
        
        if self.payload is not None and self.payload.data is not None:
            if isinstance(self.payload.data, np.ndarray):
                hasher.update(self.payload.data.tobytes())
        
        self.content_hash = hasher.hexdigest()[:16]
        return self.content_hash
    
    def local_dimension(self) -> int:
        """Get local Hilbert space dimension."""
        return 2 ** len(self.qubit_subset)
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf tile."""
        return len(self.children_ids) == 0
    
    def is_healthy(self, corridor: KappaCorridor) -> bool:
        """Check if tile is within κ-corridor."""
        return self.kappa.is_in_corridor(corridor)
    
    def can_apply(self, operation: str) -> bool:
        """Check if an operation is admissible."""
        if operation == "restructure" and not self.mode_word.allow_restructure:
            return False
        if operation == "basis_change" and not self.mode_word.allow_basis_change:
            return False
        return True


@dataclass
class BlockTree:
    """
    Complete block-tree decomposition of the Hilbert space.
    
    Maintains hierarchical structure and global invariants.
    """
    n_qubits: int
    root_id: str = "root"
    tiles: Dict[str, BlockTreeTile] = field(default_factory=dict)
    
    # Global error ledger
    ledger: ErrorLedger = field(default_factory=ErrorLedger)
    
    # Global corridor
    corridor: KappaCorridor = field(default_factory=KappaCorridor)
    
    def __post_init__(self):
        if not self.tiles:
            self._initialize_root()
    
    def _initialize_root(self) -> None:
        """Initialize with a single root tile covering all qubits."""
        root = BlockTreeTile(
            tile_id=self.root_id,
            qubit_subset=set(range(self.n_qubits))
        )
        self.tiles[self.root_id] = root
        self.ledger.create_tile_budget(self.root_id)
    
    def get_tile(self, tile_id: str) -> Optional[BlockTreeTile]:
        """Get a tile by ID."""
        return self.tiles.get(tile_id)
    
    def add_tile(self, tile: BlockTreeTile) -> None:
        """Add a tile to the tree."""
        self.tiles[tile.tile_id] = tile
        self.ledger.create_tile_budget(tile.tile_id)
    
    def split_tile(self, tile_id: str, partition: List[Set[int]]) -> List[str]:
        """
        Split a tile into children covering a partition of qubits.
        
        Returns list of new child tile IDs.
        """
        parent = self.tiles.get(tile_id)
        if parent is None:
            raise ValueError(f"Tile {tile_id} not found")
        
        # Verify partition covers parent's qubits
        union = set()
        for part in partition:
            union |= part
        if union != parent.qubit_subset:
            raise ValueError("Partition must cover parent's qubits")
        
        child_ids = []
        for i, qubit_set in enumerate(partition):
            child_id = f"{tile_id}_c{i}"
            child = BlockTreeTile(
                tile_id=child_id,
                qubit_subset=qubit_set,
                parent_id=tile_id,
                mode_word=parent.mode_word.evolve(OperationRole.RESTRUCTURE)
            )
            self.add_tile(child)
            child_ids.append(child_id)
        
        parent.children_ids = child_ids
        return child_ids
    
    def merge_tiles(self, tile_ids: List[str], new_id: str) -> str:
        """
        Merge multiple tiles into one.
        
        Returns new tile ID.
        """
        qubits = set()
        for tid in tile_ids:
            tile = self.tiles.get(tid)
            if tile is None:
                raise ValueError(f"Tile {tid} not found")
            qubits |= tile.qubit_subset
        
        # Find common parent (if any)
        parents = set()
        for tid in tile_ids:
            if self.tiles[tid].parent_id:
                parents.add(self.tiles[tid].parent_id)
        
        merged = BlockTreeTile(
            tile_id=new_id,
            qubit_subset=qubits,
            parent_id=list(parents)[0] if len(parents) == 1 else None
        )
        self.add_tile(merged)
        
        return new_id
    
    def all_leaves(self) -> List[BlockTreeTile]:
        """Get all leaf tiles."""
        return [t for t in self.tiles.values() if t.is_leaf()]
    
    def total_dimension(self) -> int:
        """Get total Hilbert space dimension."""
        return 2 ** self.n_qubits
    
    def is_partition_valid(self) -> bool:
        """Check if leaves form a valid partition of qubits."""
        leaves = self.all_leaves()
        covered = set()
        for leaf in leaves:
            if leaf.qubit_subset & covered:
                return False  # Overlap
            covered |= leaf.qubit_subset
        return covered == set(range(self.n_qubits))
    
    def health_check(self) -> Dict[str, Any]:
        """Perform global health check."""
        unhealthy = [
            t.tile_id for t in self.tiles.values()
            if not t.is_healthy(self.corridor)
        ]
        
        return {
            'n_tiles': len(self.tiles),
            'n_leaves': len(self.all_leaves()),
            'partition_valid': self.is_partition_valid(),
            'all_healthy': len(unhealthy) == 0,
            'unhealthy_tiles': unhealthy,
            'ledger': self.ledger.summary()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_bulk_representation() -> bool:
    """Validate bulk representation components."""
    # Mode word
    mode = ModeWord(
        basis_chart=BasisChart.COMPUTATIONAL,
        compression_method=CompressionMethod.DENSE,
        precision=PrecisionDiscipline.FLOAT64
    )
    assert mode.version == 1
    
    evolved = mode.evolve(OperationRole.CHANGE)
    assert evolved.version == 2
    assert evolved.role == OperationRole.CHANGE
    
    # Error budget
    budget = ErrorBudget(epsilon_budget=1e-4, delta_budget=1e-4)
    assert budget.can_afford(1e-5, 1e-5)
    assert budget.consume(1e-5, 1e-5)
    assert budget.epsilon_used == 1e-5
    
    # Error ledger
    ledger = ErrorLedger(global_epsilon=1e-3, global_delta=1e-3)
    ledger.create_tile_budget("tile_0")
    assert ledger.consume("tile_0", 1e-5, 1e-5, "test")
    assert ledger.is_within_budget()
    
    # κ-texture
    kappa = KappaTexture(coherence=0.9, condition_number=10.0)
    corridor = KappaCorridor(min_coherence=0.5, max_condition=100.0)
    assert kappa.is_in_corridor(corridor)
    
    # Block-tree tile
    tile = BlockTreeTile(
        tile_id="test_tile",
        qubit_subset={0, 1, 2}
    )
    assert tile.local_dimension() == 8
    assert tile.is_leaf()
    
    # Block tree
    tree = BlockTree(n_qubits=4)
    assert tree.root_id in tree.tiles
    assert tree.total_dimension() == 16
    
    # Split
    children = tree.split_tile("root", [{0, 1}, {2, 3}])
    assert len(children) == 2
    assert tree.is_partition_valid()
    
    return True


if __name__ == "__main__":
    print("Validating Bulk Representation...")
    assert validate_bulk_representation()
    print("✓ Bulk Representation validated")
    
    # Demo
    print("\n=== Block Tree Demo ===")
    tree = BlockTree(n_qubits=4)
    
    print(f"Initial: {tree.health_check()}")
    
    # Split root into two parts
    children = tree.split_tile("root", [{0, 1}, {2, 3}])
    print(f"After split: {tree.health_check()}")
    
    print("\n=== Error Ledger Demo ===")
    ledger = ErrorLedger(global_epsilon=1e-3, global_delta=1e-3)
    ledger.create_tile_budget("tile_0")
    ledger.create_tile_budget("tile_1")
    
    ledger.consume("tile_0", 1e-5, 1e-6, "gate application")
    ledger.consume("tile_1", 2e-5, 1e-6, "basis change")
    
    print(f"Summary: {ledger.summary()}")

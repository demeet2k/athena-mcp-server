"""
ATHENA OS - Q-SHRINK LENS FAMILIES
==================================
The Four-Lens Taxonomy (Chapter 1.3.3)

Q-SHRINK decomposes codec design into four orthogonal lens families,
each corresponding to a distinct proof obligation class:

□ SQUARE LENS (Determinism / Addressing):
    - Discrete indices, permutations, parity structures
    - Seedable schedules, seek lattices
    - Canonical ordering, deterministic reconstruction
    - Latin squares, balanced addressing

✿ FLOWER LENS (Coupling / Phase Geometry):
    - Continuous or phase-like coordinates
    - Petal clustering and routing
    - Coupled stream alignment
    - Multiscale partitions, anchors

☁ CLOUD LENS (Probability / Entropy):
    - Probability distributions over symbols
    - Entropy bounds, model contracts
    - Table policies, lane grammars
    - Code-length accounting

⟡ FRACTAL LENS (Recursion / Self-Reference):
    - Multi-scale representations
    - Recursive decomposition
    - Modularity boundaries
    - Self-similarity exploitation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np


# =============================================================================
# LENS TYPES
# =============================================================================

class LensType(Enum):
    """The four lens family types."""
    
    SQUARE = "□"      # Determinism / Addressing
    FLOWER = "✿"      # Coupling / Phase Geometry
    CLOUD = "☁"       # Probability / Entropy
    FRACTAL = "⟡"     # Recursion / Self-Reference


class LensScope(Enum):
    """Scope of lens application."""
    
    GLOBAL = "global"     # Entire stream
    STREAM = "stream"     # Per-stream
    CELL = "cell"         # Per-cell/tile
    BLOCK = "block"       # Per-block


@dataclass
class LensContract:
    """
    Contract for a lens module.
    
    Specifies provides/requires relationships.
    """
    
    name: str
    lens_type: LensType
    scope: LensScope
    
    provides: Set[str] = field(default_factory=set)
    requires: Set[str] = field(default_factory=set)
    
    version: str = "1.0"
    is_required: bool = True  # False = accelerator
    
    def is_compatible(self, available: Set[str]) -> bool:
        """Check if requirements are satisfied."""
        return self.requires.issubset(available)


# =============================================================================
# SQUARE LENS (□) - DETERMINISM / ADDRESSING
# =============================================================================

class SquareLens(ABC):
    """
    Square Lens: Determinism and Addressing.
    
    Responsible for:
    - Discrete indices and permutations
    - Parity structures
    - Seedable schedules
    - Seek lattices and canonical ordering
    """
    
    lens_type = LensType.SQUARE
    
    @abstractmethod
    def index(self, position: Tuple[int, ...]) -> int:
        """Map position to linear index."""
        pass
    
    @abstractmethod
    def inverse_index(self, idx: int) -> Tuple[int, ...]:
        """Map linear index to position."""
        pass


@dataclass
class LatinSquareSchedule(SquareLens):
    """
    Latin square-based schedule.
    
    A k×k Latin square ensures each symbol appears exactly
    once in each row and column.
    """
    
    k: int
    seed: int = 0
    
    _square: np.ndarray = field(init=False)
    
    def __post_init__(self):
        """Generate the Latin square."""
        self._square = self._generate_latin_square()
    
    def _generate_latin_square(self) -> np.ndarray:
        """Generate a Latin square deterministically from seed."""
        np.random.seed(self.seed)
        
        # Start with cyclic Latin square
        square = np.zeros((self.k, self.k), dtype=int)
        for i in range(self.k):
            for j in range(self.k):
                square[i, j] = (i + j) % self.k
        
        # Shuffle rows and columns (preserving Latin property)
        row_perm = np.random.permutation(self.k)
        col_perm = np.random.permutation(self.k)
        
        square = square[row_perm, :]
        square = square[:, col_perm]
        
        return square
    
    def index(self, position: Tuple[int, ...]) -> int:
        """Map 2D position to schedule value."""
        i, j = position[0] % self.k, position[1] % self.k
        return int(self._square[i, j])
    
    def inverse_index(self, idx: int) -> Tuple[int, ...]:
        """Find first position with given schedule value."""
        positions = np.where(self._square == idx)
        if len(positions[0]) > 0:
            return (int(positions[0][0]), int(positions[1][0]))
        return (0, 0)
    
    def is_latin(self) -> bool:
        """Verify Latin square property."""
        for i in range(self.k):
            if len(set(self._square[i, :])) != self.k:
                return False
            if len(set(self._square[:, i])) != self.k:
                return False
        return True


@dataclass
class SeekLattice(SquareLens):
    """
    Seek lattice for random access.
    
    Maps unit IDs to (offset, length) pairs for fast seeking.
    Uses parity compression to reduce metadata size.
    """
    
    entries: List[Tuple[int, int]]  # (offset, length) pairs
    use_parity_compression: bool = True
    
    _anchors: Tuple[int, int] = field(init=False)
    _even_deltas: List[Tuple[int, int]] = field(init=False)
    _parity_offsets: List[int] = field(init=False)
    _parity_lengths: List[int] = field(init=False)
    
    def __post_init__(self):
        """Build parity-compressed representation."""
        if self.use_parity_compression and len(self.entries) >= 2:
            self._build_parity_representation()
        else:
            self._anchors = self.entries[0] if self.entries else (0, 0)
            self._even_deltas = []
            self._parity_offsets = []
            self._parity_lengths = []
    
    def _build_parity_representation(self):
        """Build parity-reconstructible representation."""
        n = len(self.entries)
        
        # Store anchor (first entry)
        self._anchors = self.entries[0]
        
        # Store even-indexed entries as deltas from anchor
        self._even_deltas = []
        for i in range(2, n, 2):
            delta_o = self.entries[i][0] - self.entries[i-2][0]
            delta_l = self.entries[i][1] - self.entries[i-2][1]
            self._even_deltas.append((delta_o, delta_l))
        
        # Store parity arrays for odd entries
        self._parity_offsets = []
        self._parity_lengths = []
        for i in range(1, n, 2):
            self._parity_offsets.append(self.entries[i][0])
            self._parity_lengths.append(self.entries[i][1])
    
    def index(self, position: Tuple[int, ...]) -> int:
        """Get offset for unit index."""
        idx = position[0]
        if idx < len(self.entries):
            return self.entries[idx][0]
        return -1
    
    def inverse_index(self, offset: int) -> Tuple[int, ...]:
        """Find unit index for offset."""
        for i, (o, _) in enumerate(self.entries):
            if o == offset:
                return (i,)
        return (-1,)
    
    def lookup(self, unit_id: int) -> Tuple[int, int]:
        """Look up (offset, length) for unit."""
        if unit_id < len(self.entries):
            return self.entries[unit_id]
        return (-1, 0)
    
    def reconstruct_from_parity(self) -> List[Tuple[int, int]]:
        """Reconstruct full table from parity representation."""
        if not self._even_deltas:
            return list(self.entries)
        
        result = [self._anchors]
        
        # Interleave even (reconstructed) and odd (stored) entries
        even_idx = 0
        odd_idx = 0
        current_even = self._anchors
        
        n_entries = 1 + len(self._even_deltas) * 2 + len(self._parity_offsets)
        
        for i in range(1, n_entries):
            if i % 2 == 1:  # Odd index - stored
                if odd_idx < len(self._parity_offsets):
                    result.append((
                        self._parity_offsets[odd_idx],
                        self._parity_lengths[odd_idx]
                    ))
                    odd_idx += 1
            else:  # Even index - reconstructed from deltas
                if even_idx < len(self._even_deltas):
                    delta_o, delta_l = self._even_deltas[even_idx]
                    current_even = (
                        current_even[0] + delta_o,
                        current_even[1] + delta_l
                    )
                    result.append(current_even)
                    even_idx += 1
        
        return result
    
    def compression_ratio(self) -> float:
        """Compute compression ratio of parity representation."""
        explicit_size = len(self.entries) * 2  # Two ints per entry
        compressed_size = 2 + len(self._even_deltas) * 2 + len(self._parity_offsets) * 2
        if compressed_size == 0:
            return 1.0
        return explicit_size / compressed_size


@dataclass
class SeedBank(SquareLens):
    """
    Seed bank for table generation.
    
    Store seeds instead of explicit tables: O(k) instead of O(k²).
    """
    
    seeds: Dict[int, int]  # size -> seed
    generator_version: str = "1.0"
    
    def index(self, position: Tuple[int, ...]) -> int:
        """Get seed for size."""
        size = position[0]
        return self.seeds.get(size, 0)
    
    def inverse_index(self, seed: int) -> Tuple[int, ...]:
        """Find size for seed."""
        for size, s in self.seeds.items():
            if s == seed:
                return (size,)
        return (0,)
    
    def generate_table(self, size: int) -> np.ndarray:
        """Generate table from seed."""
        seed = self.seeds.get(size, 0)
        np.random.seed(seed)
        
        # Generate k×k table deterministically
        return np.random.randint(0, size, (size, size))
    
    def add_seed(self, size: int, seed: int) -> None:
        """Add seed for size."""
        self.seeds[size] = seed


# =============================================================================
# FLOWER LENS (✿) - COUPLING / PHASE GEOMETRY
# =============================================================================

class FlowerLens(ABC):
    """
    Flower Lens: Coupling and Phase Geometry.
    
    Responsible for:
    - Continuous or phase-like coordinates
    - Petal clustering and routing
    - Coupled stream alignment
    - Multiscale partitions
    """
    
    lens_type = LensType.FLOWER
    
    @abstractmethod
    def assign_petal(self, sample: np.ndarray) -> int:
        """Assign sample to a petal (cluster)."""
        pass
    
    @abstractmethod
    def get_anchor(self, petal_id: int) -> np.ndarray:
        """Get anchor for petal."""
        pass


@dataclass
class PetalPartition(FlowerLens):
    """
    Petal-based partition for sample routing.
    
    Samples are routed into coherent groups (petals) based on
    phase-like coordinates.
    """
    
    n_petals: int
    dim: int
    
    _anchors: np.ndarray = field(init=False)
    _petal_counts: np.ndarray = field(init=False)
    
    def __post_init__(self):
        """Initialize petal anchors."""
        # Initialize anchors on unit circle (or hypersphere)
        self._anchors = np.zeros((self.n_petals, self.dim))
        for i in range(self.n_petals):
            theta = 2 * np.pi * i / self.n_petals
            self._anchors[i, 0] = np.cos(theta)
            if self.dim > 1:
                self._anchors[i, 1] = np.sin(theta)
        
        self._petal_counts = np.zeros(self.n_petals, dtype=int)
    
    def assign_petal(self, sample: np.ndarray) -> int:
        """Assign sample to nearest petal anchor."""
        # Normalize sample
        norm = np.linalg.norm(sample)
        if norm > 0:
            sample_normalized = sample / norm
        else:
            sample_normalized = sample
        
        # Find nearest anchor (by dot product)
        dots = self._anchors @ sample_normalized[:self.dim]
        petal_id = int(np.argmax(dots))
        
        self._petal_counts[petal_id] += 1
        return petal_id
    
    def get_anchor(self, petal_id: int) -> np.ndarray:
        """Get anchor for petal."""
        return self._anchors[petal_id].copy()
    
    def compute_residual(self, sample: np.ndarray, petal_id: int) -> np.ndarray:
        """Compute residual from petal anchor."""
        anchor = self.get_anchor(petal_id)
        # Project onto anchor direction
        projection = np.dot(sample[:self.dim], anchor) * anchor
        # Residual is perpendicular component + remaining dims
        residual = sample.copy()
        residual[:self.dim] -= projection
        return residual
    
    def petal_distribution(self) -> np.ndarray:
        """Get distribution of samples across petals."""
        total = np.sum(self._petal_counts)
        if total == 0:
            return np.ones(self.n_petals) / self.n_petals
        return self._petal_counts / total


@dataclass
class PhaseAnchor(FlowerLens):
    """
    Phase-based anchoring for coupled streams.
    
    Aligns streams by phase relationships.
    """
    
    n_phases: int
    phase_values: np.ndarray = field(default_factory=lambda: np.array([]))
    
    def __post_init__(self):
        if len(self.phase_values) == 0:
            # Initialize uniform phase grid
            self.phase_values = np.linspace(0, 2*np.pi, self.n_phases, endpoint=False)
    
    def assign_petal(self, sample: np.ndarray) -> int:
        """Assign sample to nearest phase."""
        # Extract phase from first two components
        if len(sample) >= 2:
            phase = np.arctan2(sample[1], sample[0])
            if phase < 0:
                phase += 2 * np.pi
        else:
            phase = 0
        
        # Find nearest phase anchor
        diffs = np.abs(self.phase_values - phase)
        diffs = np.minimum(diffs, 2*np.pi - diffs)  # Handle wrap-around
        return int(np.argmin(diffs))
    
    def get_anchor(self, petal_id: int) -> np.ndarray:
        """Get anchor for phase."""
        phase = self.phase_values[petal_id]
        return np.array([np.cos(phase), np.sin(phase)])
    
    def phase_lock(self, phases: np.ndarray, target_phase: int) -> np.ndarray:
        """Lock phases to target anchor."""
        target = self.phase_values[target_phase]
        # Compute phase correction
        corrections = target - phases
        # Wrap to [-π, π]
        corrections = np.mod(corrections + np.pi, 2*np.pi) - np.pi
        return phases + 0.5 * corrections  # Partial correction


# =============================================================================
# CLOUD LENS (☁) - PROBABILITY / ENTROPY
# =============================================================================

class CloudLens(ABC):
    """
    Cloud Lens: Probability and Entropy.
    
    Responsible for:
    - Probability distributions over symbols
    - Entropy bounds and model contracts
    - Table policies and lane grammars
    - Code-length accounting
    """
    
    lens_type = LensType.CLOUD
    
    @abstractmethod
    def probability(self, symbol: int) -> float:
        """Get probability of symbol."""
        pass
    
    @abstractmethod
    def entropy(self) -> float:
        """Compute entropy of distribution."""
        pass


@dataclass
class ProbabilityTable(CloudLens):
    """
    Probability table for entropy coding.
    
    Supports LITE (frequencies) and FAST (expanded lookup) forms.
    """
    
    frequencies: np.ndarray
    alphabet_size: int = 256
    
    _cumulative: np.ndarray = field(init=False)
    _normalized: np.ndarray = field(init=False)
    
    def __post_init__(self):
        """Build cumulative and normalized tables."""
        total = np.sum(self.frequencies)
        if total > 0:
            self._normalized = self.frequencies / total
        else:
            self._normalized = np.ones(len(self.frequencies)) / len(self.frequencies)
        
        self._cumulative = np.zeros(len(self.frequencies) + 1)
        self._cumulative[1:] = np.cumsum(self.frequencies)
    
    def probability(self, symbol: int) -> float:
        """Get probability of symbol."""
        if 0 <= symbol < len(self._normalized):
            return float(self._normalized[symbol])
        return 0.0
    
    def entropy(self) -> float:
        """Compute entropy H(P)."""
        h = 0.0
        for p in self._normalized:
            if p > 0:
                h -= p * np.log2(p)
        return h
    
    def code_length(self, symbol: int) -> float:
        """Compute ideal code length for symbol."""
        p = self.probability(symbol)
        if p > 0:
            return -np.log2(p)
        return float('inf')
    
    def to_lite(self) -> np.ndarray:
        """Get LITE form (frequencies only)."""
        return self.frequencies.copy()
    
    def to_fast(self, precision: int = 12) -> np.ndarray:
        """Get FAST form (expanded lookup table)."""
        table_size = 1 << precision
        fast_table = np.zeros(table_size, dtype=int)
        
        cum = 0
        for symbol, freq in enumerate(self.frequencies):
            scaled_freq = int(freq * table_size / np.sum(self.frequencies))
            for i in range(scaled_freq):
                if cum + i < table_size:
                    fast_table[cum + i] = symbol
            cum += scaled_freq
        
        return fast_table


@dataclass  
class EntropyContract(CloudLens):
    """
    Entropy contract for multi-lane coding.
    
    Specifies the probability model contract for synchronized streams.
    """
    
    n_lanes: int = 4
    lane_alphabets: List[int] = field(default_factory=lambda: [256, 256, 16, 16])
    
    _tables: List[ProbabilityTable] = field(init=False)
    
    def __post_init__(self):
        """Initialize per-lane tables."""
        self._tables = []
        for alphabet_size in self.lane_alphabets:
            # Uniform initial distribution
            freqs = np.ones(alphabet_size)
            self._tables.append(ProbabilityTable(freqs, alphabet_size))
    
    def probability(self, symbol: int, lane: int = 0) -> float:
        """Get probability of symbol in lane."""
        if 0 <= lane < len(self._tables):
            return self._tables[lane].probability(symbol)
        return 0.0
    
    def entropy(self, lane: int = 0) -> float:
        """Compute entropy for lane."""
        if 0 <= lane < len(self._tables):
            return self._tables[lane].entropy()
        return 0.0
    
    def total_entropy(self) -> float:
        """Compute total entropy across lanes."""
        return sum(self.entropy(i) for i in range(self.n_lanes))
    
    def update_lane(self, lane: int, frequencies: np.ndarray) -> None:
        """Update table for a lane."""
        if 0 <= lane < len(self._tables):
            self._tables[lane] = ProbabilityTable(
                frequencies, self.lane_alphabets[lane]
            )


# =============================================================================
# FRACTAL LENS (⟡) - RECURSION / SELF-REFERENCE
# =============================================================================

class FractalLens(ABC):
    """
    Fractal Lens: Recursion and Self-Reference.
    
    Responsible for:
    - Multi-scale representations
    - Recursive decomposition
    - Modularity boundaries
    - Self-similarity exploitation
    """
    
    lens_type = LensType.FRACTAL
    
    @abstractmethod
    def decompose(self, data: np.ndarray) -> List[np.ndarray]:
        """Decompose data into scales."""
        pass
    
    @abstractmethod
    def recompose(self, scales: List[np.ndarray]) -> np.ndarray:
        """Recompose from scales."""
        pass


@dataclass
class MultiscaleDecomposition(FractalLens):
    """
    Multi-scale wavelet-like decomposition.
    """
    
    n_levels: int = 3
    
    def decompose(self, data: np.ndarray) -> List[np.ndarray]:
        """Decompose into scales using Haar-like transform."""
        scales = []
        current = data.copy()
        
        for level in range(self.n_levels):
            if len(current) < 2:
                break
            
            # Downsample by averaging pairs
            n = len(current) // 2 * 2
            current = current[:n].reshape(-1, 2)
            
            # Low-pass (average)
            low = np.mean(current, axis=1)
            
            # High-pass (difference)
            high = current[:, 0] - current[:, 1]
            
            scales.append(high)
            current = low
        
        scales.append(current)  # Coarsest scale
        return scales
    
    def recompose(self, scales: List[np.ndarray]) -> np.ndarray:
        """Recompose from scales."""
        if len(scales) == 0:
            return np.array([])
        
        current = scales[-1].copy()  # Start from coarsest
        
        for level in range(len(scales) - 2, -1, -1):
            high = scales[level]
            
            # Upsample and add high-pass
            expanded = np.zeros(len(current) * 2)
            expanded[0::2] = current + high / 2
            expanded[1::2] = current - high / 2
            
            current = expanded
        
        return current


@dataclass
class RecursiveModule(FractalLens):
    """
    Recursive module for self-similar structures.
    """
    
    base_size: int = 4
    max_depth: int = 4
    
    def decompose(self, data: np.ndarray) -> List[np.ndarray]:
        """Recursively decompose into self-similar blocks."""
        result = []
        self._recursive_decompose(data, 0, result)
        return result
    
    def _recursive_decompose(self, data: np.ndarray, depth: int,
                            result: List[np.ndarray]) -> None:
        """Recursive helper."""
        if depth >= self.max_depth or len(data) <= self.base_size:
            result.append(data.copy())
            return
        
        # Split into base_size blocks
        n_blocks = len(data) // self.base_size
        if n_blocks == 0:
            result.append(data.copy())
            return
        
        for i in range(n_blocks):
            block = data[i * self.base_size:(i + 1) * self.base_size]
            self._recursive_decompose(block, depth + 1, result)
        
        # Handle remainder
        remainder = data[n_blocks * self.base_size:]
        if len(remainder) > 0:
            result.append(remainder.copy())
    
    def recompose(self, scales: List[np.ndarray]) -> np.ndarray:
        """Recompose from blocks."""
        if len(scales) == 0:
            return np.array([])
        return np.concatenate(scales)


# =============================================================================
# LENS GRAPH (Chapter 9)
# =============================================================================

@dataclass
class LensModule:
    """A module in the lens graph."""
    
    name: str
    lens_type: LensType
    contract: LensContract
    implementation: Union[SquareLens, FlowerLens, CloudLens, FractalLens]
    priority: int = 0  # Higher = more specific


class LensGraph:
    """
    Declarative lens graph for module selection.
    
    Selects modules by scope, guarded by topology facts,
    resolved by specificity and priority.
    """
    
    def __init__(self):
        self._modules: List[LensModule] = []
        self._resolved: Dict[str, LensModule] = {}
    
    def register(self, module: LensModule) -> None:
        """Register a lens module."""
        self._modules.append(module)
    
    def resolve(self, available_capabilities: Set[str]) -> Dict[str, LensModule]:
        """
        Resolve lens graph to execution plan.
        
        Returns winning modules per contract.
        """
        self._resolved = {}
        
        # Group by contract name
        by_contract: Dict[str, List[LensModule]] = {}
        for module in self._modules:
            name = module.contract.name
            if name not in by_contract:
                by_contract[name] = []
            by_contract[name].append(module)
        
        # For each contract, pick highest priority compatible module
        for contract_name, modules in by_contract.items():
            compatible = [
                m for m in modules
                if m.contract.is_compatible(available_capabilities)
            ]
            
            if compatible:
                # Sort by priority (descending)
                compatible.sort(key=lambda m: m.priority, reverse=True)
                self._resolved[contract_name] = compatible[0]
        
        return self._resolved
    
    def compile_capsule(self, available_capabilities: Set[str]) -> 'ExecutionCapsule':
        """Compile resolved plan into execution capsule."""
        resolved = self.resolve(available_capabilities)
        return ExecutionCapsule(
            modules=resolved,
            capabilities=available_capabilities
        )


@dataclass
class ExecutionCapsule:
    """
    Compiled execution capsule.
    
    A verified, content-addressable dispatch artifact
    that eliminates graph logic on the hot path.
    """
    
    modules: Dict[str, LensModule]
    capabilities: Set[str]
    
    _hash: str = field(init=False)
    
    def __post_init__(self):
        """Compute content hash."""
        import hashlib
        content = str(sorted(self.modules.keys())) + str(sorted(self.capabilities))
        self._hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_module(self, contract: str) -> Optional[LensModule]:
        """Get module for contract."""
        return self.modules.get(contract)
    
    @property
    def content_hash(self) -> str:
        """Get content-addressable hash."""
        return self._hash


# =============================================================================
# VALIDATION
# =============================================================================

def validate_lenses() -> bool:
    """Validate Q-SHRINK lens families."""
    np.random.seed(42)
    
    # Test Latin square
    latin = LatinSquareSchedule(k=4, seed=42)
    assert latin.is_latin()
    idx = latin.index((0, 0))
    assert 0 <= idx < 4
    
    # Test seek lattice
    entries = [(0, 100), (100, 100), (200, 100), (300, 100)]
    seek = SeekLattice(entries=entries)
    assert seek.lookup(0) == (0, 100)
    assert seek.lookup(2) == (200, 100)
    assert seek.compression_ratio() >= 1.0
    
    # Test seed bank
    bank = SeedBank(seeds={4: 42, 8: 123})
    table = bank.generate_table(4)
    assert table.shape == (4, 4)
    
    # Test petal partition
    petals = PetalPartition(n_petals=4, dim=2)
    sample = np.array([1.0, 0.0])
    petal_id = petals.assign_petal(sample)
    assert 0 <= petal_id < 4
    
    anchor = petals.get_anchor(petal_id)
    assert len(anchor) == 2
    
    # Test phase anchor
    phase = PhaseAnchor(n_phases=8)
    sample = np.array([1.0, 1.0])
    phase_id = phase.assign_petal(sample)
    assert 0 <= phase_id < 8
    
    # Test probability table
    freqs = np.array([10, 20, 30, 40])
    table = ProbabilityTable(freqs)
    assert abs(table.probability(0) - 0.1) < 0.01
    assert table.entropy() > 0
    
    # Test entropy contract
    contract = EntropyContract(n_lanes=4)
    assert contract.total_entropy() > 0
    
    # Test multiscale decomposition
    multi = MultiscaleDecomposition(n_levels=3)
    data = np.random.randn(16)
    scales = multi.decompose(data)
    recomposed = multi.recompose(scales)
    assert len(recomposed) == len(data)
    
    # Test recursive module
    recursive = RecursiveModule(base_size=4, max_depth=2)
    data = np.random.randn(16)
    blocks = recursive.decompose(data)
    recomposed = recursive.recompose(blocks)
    assert np.allclose(data, recomposed)
    
    # Test lens graph
    graph = LensGraph()
    
    latin_module = LensModule(
        name="latin_schedule",
        lens_type=LensType.SQUARE,
        contract=LensContract(
            name="schedule",
            lens_type=LensType.SQUARE,
            scope=LensScope.GLOBAL,
            provides={"schedule"},
            requires=set()
        ),
        implementation=latin,
        priority=1
    )
    graph.register(latin_module)
    
    capsule = graph.compile_capsule(set())
    assert capsule.get_module("schedule") is not None
    
    return True


if __name__ == "__main__":
    print("Validating Q-SHRINK Lens Families...")
    assert validate_lenses()
    print("✓ Q-SHRINK Lens Families validated")

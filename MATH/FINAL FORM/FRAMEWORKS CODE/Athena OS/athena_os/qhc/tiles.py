"""
ATHENA OS - Quantum Holography Computing (QHC)
==============================================
Holographic Tiles and Basis Families

From Quantum_Holography_Computing_(QHC).docx Chapter 4:

TILE:
    Structured object carrying local state information
    
    Components:
    - Qubit index set S ⊆ [n] with ordering π_S
    - Basis type b_v (computational, Fourier, polynomial)
    - Data representation d_v (dense, sparse, low-rank)
    - Error descriptor ε_v
    - Mode word m_v

BASIS FAMILIES:
    - Computational: |i₁...iₖ⟩ standard basis
    - Fourier: QFT basis for periodic structure
    - Polynomial: for smooth amplitudes
    - Custom: problem-specific bases

TILE METADATA:
    - Storage format
    - Compression parameters
    - Error budget
    - Reconstruction hints
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from enum import Enum, auto
import math
import cmath

from .hilbert import HilbertSpace, StateVector, QubitIndexSet
from .blocktree import TreeNode, BlockTree


# =============================================================================
# BASIS TYPES
# =============================================================================

class BasisType(Enum):
    """Types of local bases for tiles."""
    
    COMPUTATIONAL = "computational"  # Standard |i₁...iₖ⟩
    FOURIER = "fourier"              # QFT basis
    HADAMARD = "hadamard"            # Hadamard basis
    POLYNOMIAL = "polynomial"        # Polynomial interpolation
    SPARSE = "sparse"                # Sparse representation
    CUSTOM = "custom"                # Problem-specific


class StorageFormat(Enum):
    """Data storage formats for tiles."""
    
    DENSE = "dense"          # Full vector
    SPARSE = "sparse"        # Sparse (index, value) pairs
    LOW_RANK = "low_rank"    # Low-rank factorization
    COMPRESSED = "compressed"  # General compression


class CompressionType(Enum):
    """Compression schemes."""
    
    NONE = "none"
    TRUNCATION = "truncation"    # Coefficient truncation
    SVD = "svd"                  # Singular value decomposition
    ADAPTIVE = "adaptive"        # Adaptive compression


# =============================================================================
# QUBIT ORDERING
# =============================================================================

@dataclass
class QubitOrdering:
    """
    Local ordering π_S: {1,...,|S|} → S
    
    Determines tensor factor sequence.
    """
    
    qubit_set: Set[int]
    ordering: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.ordering:
            self.ordering = sorted(self.qubit_set)
    
    def __len__(self) -> int:
        return len(self.ordering)
    
    def position(self, qubit: int) -> int:
        """Get position of qubit in ordering."""
        return self.ordering.index(qubit)
    
    def qubit_at(self, position: int) -> int:
        """Get qubit at position."""
        return self.ordering[position]
    
    def swap_map(self, other: 'QubitOrdering') -> List[Tuple[int, int]]:
        """
        Get sequence of swaps to transform self to other.
        """
        if set(self.ordering) != set(other.ordering):
            raise ValueError("Orderings must be over same qubits")
        
        swaps = []
        current = list(self.ordering)
        target = list(other.ordering)
        
        for i in range(len(current)):
            if current[i] != target[i]:
                j = current.index(target[i])
                swaps.append((i, j))
                current[i], current[j] = current[j], current[i]
        
        return swaps


# =============================================================================
# ERROR DESCRIPTOR
# =============================================================================

@dataclass
class ErrorDescriptor:
    """
    Error tracking for a tile.
    
    Tracks approximation errors from compression, basis changes, etc.
    """
    
    # Error bounds
    local_error: float = 0.0      # ‖exact - approx‖ / ‖exact‖
    truncation_error: float = 0.0  # From coefficient truncation
    compression_error: float = 0.0 # From low-rank approximation
    
    # Budget
    error_budget: float = 1e-6
    
    # Statistics
    num_approximations: int = 0
    
    @property
    def total_error(self) -> float:
        """Combined error estimate."""
        return math.sqrt(
            self.local_error**2 + 
            self.truncation_error**2 + 
            self.compression_error**2
        )
    
    def within_budget(self) -> bool:
        """Check if errors within budget."""
        return self.total_error <= self.error_budget
    
    def add_error(self, error: float, error_type: str = "local") -> None:
        """Add new error contribution."""
        if error_type == "local":
            self.local_error = math.sqrt(self.local_error**2 + error**2)
        elif error_type == "truncation":
            self.truncation_error = math.sqrt(self.truncation_error**2 + error**2)
        elif error_type == "compression":
            self.compression_error = math.sqrt(self.compression_error**2 + error**2)
        self.num_approximations += 1
    
    def reset(self) -> None:
        """Reset error tracking."""
        self.local_error = 0.0
        self.truncation_error = 0.0
        self.compression_error = 0.0
        self.num_approximations = 0


# =============================================================================
# TILE DATA
# =============================================================================

@dataclass
class TileData:
    """
    Data representation for a tile.
    
    Stores state amplitudes in chosen basis and format.
    """
    
    dimension: int
    storage_format: StorageFormat = StorageFormat.DENSE
    
    # Dense storage
    dense_data: List[complex] = field(default_factory=list)
    
    # Sparse storage (index, value)
    sparse_data: Dict[int, complex] = field(default_factory=dict)
    
    # Low-rank: A ≈ UV† where U is dim×rank, V is dim×rank
    low_rank_u: List[List[complex]] = field(default_factory=list)
    low_rank_v: List[List[complex]] = field(default_factory=list)
    rank: int = 0
    
    @property
    def num_nonzero(self) -> int:
        """Count non-zero elements."""
        if self.storage_format == StorageFormat.SPARSE:
            return len(self.sparse_data)
        return sum(1 for v in self.dense_data if abs(v) > 1e-15)
    
    @property
    def sparsity(self) -> float:
        """Sparsity ratio (non-zero / total)."""
        return self.num_nonzero / self.dimension
    
    def get(self, index: int) -> complex:
        """Get amplitude at index."""
        if self.storage_format == StorageFormat.DENSE:
            return self.dense_data[index] if index < len(self.dense_data) else 0j
        elif self.storage_format == StorageFormat.SPARSE:
            return self.sparse_data.get(index, 0j)
        else:
            # Low-rank reconstruction
            return sum(
                self.low_rank_u[index][k] * self.low_rank_v[index][k].conjugate()
                for k in range(self.rank)
            ) if self.rank > 0 else 0j
    
    def set(self, index: int, value: complex) -> None:
        """Set amplitude at index."""
        if self.storage_format == StorageFormat.DENSE:
            while len(self.dense_data) <= index:
                self.dense_data.append(0j)
            self.dense_data[index] = value
        elif self.storage_format == StorageFormat.SPARSE:
            if abs(value) > 1e-15:
                self.sparse_data[index] = value
            elif index in self.sparse_data:
                del self.sparse_data[index]
    
    def to_dense(self) -> List[complex]:
        """Convert to dense representation."""
        if self.storage_format == StorageFormat.DENSE:
            return list(self.dense_data)
        
        result = [0j] * self.dimension
        if self.storage_format == StorageFormat.SPARSE:
            for idx, val in self.sparse_data.items():
                result[idx] = val
        return result
    
    def compress_sparse(self, threshold: float = 1e-10) -> float:
        """Compress to sparse, return truncation error."""
        if self.storage_format != StorageFormat.DENSE:
            return 0.0
        
        error_sq = 0.0
        self.sparse_data = {}
        
        for i, v in enumerate(self.dense_data):
            if abs(v) > threshold:
                self.sparse_data[i] = v
            else:
                error_sq += abs(v)**2
        
        self.storage_format = StorageFormat.SPARSE
        return math.sqrt(error_sq)
    
    @classmethod
    def from_amplitudes(cls, amplitudes: List[complex], 
                       storage: StorageFormat = StorageFormat.DENSE) -> 'TileData':
        """Create from amplitude list."""
        data = cls(dimension=len(amplitudes), storage_format=storage)
        
        if storage == StorageFormat.DENSE:
            data.dense_data = list(amplitudes)
        elif storage == StorageFormat.SPARSE:
            data.sparse_data = {
                i: v for i, v in enumerate(amplitudes) if abs(v) > 1e-15
            }
        
        return data


# =============================================================================
# HOLOGRAPHIC TILE
# =============================================================================

@dataclass
class HolographicTile:
    """
    Holographic tile - fundamental carrier of local state information.
    
    Complete specification:
    - Qubit support S ⊆ [n]
    - Local ordering π_S
    - Basis type b
    - Data representation d
    - Error descriptor ε
    - Mode word m (see modewords.py)
    """
    
    # Identity
    tile_id: int
    node: TreeNode
    
    # Qubit specification
    qubit_support: Set[int]
    ordering: QubitOrdering
    
    # Representation
    basis_type: BasisType = BasisType.COMPUTATIONAL
    data: TileData = field(default_factory=lambda: TileData(dimension=1))
    
    # Error tracking
    error: ErrorDescriptor = field(default_factory=ErrorDescriptor)
    
    # Compression
    compression: CompressionType = CompressionType.NONE
    compression_params: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def num_qubits(self) -> int:
        return len(self.qubit_support)
    
    @property
    def dimension(self) -> int:
        return 2 ** self.num_qubits
    
    @property
    def is_compressed(self) -> bool:
        return self.compression != CompressionType.NONE
    
    def get_amplitude(self, index: int) -> complex:
        """Get amplitude in current basis."""
        return self.data.get(index)
    
    def set_amplitude(self, index: int, value: complex) -> None:
        """Set amplitude in current basis."""
        self.data.set(index, value)
    
    def to_state_vector(self) -> StateVector:
        """Convert to StateVector."""
        space = HilbertSpace(QubitIndexSet(
            n=self.num_qubits, 
            indices=self.qubit_support
        ))
        return StateVector(space, self.data.to_dense())
    
    @classmethod
    def from_state_vector(cls, tile_id: int, node: TreeNode,
                         state: StateVector) -> 'HolographicTile':
        """Create tile from state vector."""
        return cls(
            tile_id=tile_id,
            node=node,
            qubit_support=state.space.qubit_indices.indices,
            ordering=QubitOrdering(state.space.qubit_indices.indices),
            data=TileData.from_amplitudes(state.amplitudes)
        )
    
    def summary(self) -> Dict[str, Any]:
        """Get tile summary."""
        return {
            "tile_id": self.tile_id,
            "qubits": sorted(self.qubit_support),
            "dimension": self.dimension,
            "basis": self.basis_type.value,
            "storage": self.data.storage_format.value,
            "sparsity": self.data.sparsity,
            "error": self.error.total_error,
            "compressed": self.is_compressed
        }


# =============================================================================
# TILE CONFIGURATION
# =============================================================================

@dataclass
class TileConfiguration:
    """
    Configuration for a set of tiles on a block-tree.
    """
    
    tree: BlockTree
    tiles: Dict[int, HolographicTile] = field(default_factory=dict)
    
    def __post_init__(self):
        self._next_tile_id = 0
    
    @property
    def num_tiles(self) -> int:
        return len(self.tiles)
    
    def get_tile(self, node_id: int) -> Optional[HolographicTile]:
        """Get tile for tree node."""
        return self.tiles.get(node_id)
    
    def set_tile(self, tile: HolographicTile) -> None:
        """Set tile for its node."""
        self.tiles[tile.node.node_id] = tile
    
    def create_tile(self, node: TreeNode, 
                   basis: BasisType = BasisType.COMPUTATIONAL) -> HolographicTile:
        """Create new tile for node."""
        tile = HolographicTile(
            tile_id=self._next_tile_id,
            node=node,
            qubit_support=node.label,
            ordering=QubitOrdering(node.label),
            basis_type=basis,
            data=TileData(dimension=2**len(node.label))
        )
        self._next_tile_id += 1
        self.tiles[node.node_id] = tile
        return tile
    
    def leaf_tiles(self) -> List[HolographicTile]:
        """Get all tiles at leaf nodes."""
        return [
            self.tiles[node.node_id] 
            for node in self.tree.leaves()
            if node.node_id in self.tiles
        ]
    
    def total_error(self) -> float:
        """Combined error across all tiles."""
        return math.sqrt(sum(
            tile.error.total_error**2 
            for tile in self.tiles.values()
        ))
    
    @classmethod
    def from_tree(cls, tree: BlockTree) -> 'TileConfiguration':
        """Create configuration with tiles at all leaves."""
        config = cls(tree=tree)
        for leaf in tree.leaves():
            config.create_tile(leaf)
        return config


# =============================================================================
# BASIS CHANGE
# =============================================================================

@dataclass
class BasisChange:
    """
    Basis transformation utilities.
    """
    
    @staticmethod
    def computational_to_hadamard(amplitudes: List[complex]) -> List[complex]:
        """Apply Hadamard to all qubits."""
        n = len(amplitudes)
        if n == 0:
            return []
        
        num_qubits = int(math.log2(n))
        result = list(amplitudes)
        
        # Apply H to each qubit
        for q in range(num_qubits):
            new_result = [0j] * n
            step = 2 ** q
            
            for i in range(n):
                bit = (i >> q) & 1
                partner = i ^ (1 << q)
                
                if bit == 0:
                    new_result[i] += (result[i] + result[partner]) / math.sqrt(2)
                else:
                    new_result[i] += (result[partner] - result[i]) / math.sqrt(2)
            
            result = new_result
        
        return result
    
    @staticmethod
    def hadamard_to_computational(amplitudes: List[complex]) -> List[complex]:
        """Inverse Hadamard (same as forward for real)."""
        return BasisChange.computational_to_hadamard(amplitudes)
    
    @staticmethod
    def computational_to_fourier(amplitudes: List[complex]) -> List[complex]:
        """Apply QFT (simplified DFT)."""
        n = len(amplitudes)
        if n == 0:
            return []
        
        result = []
        omega = cmath.exp(2j * math.pi / n)
        
        for k in range(n):
            val = sum(amplitudes[j] * (omega ** (j * k)) for j in range(n))
            result.append(val / math.sqrt(n))
        
        return result
    
    @staticmethod
    def fourier_to_computational(amplitudes: List[complex]) -> List[complex]:
        """Inverse QFT (simplified)."""
        n = len(amplitudes)
        if n == 0:
            return []
        
        result = []
        omega = cmath.exp(-2j * math.pi / n)
        
        for k in range(n):
            val = sum(amplitudes[j] * (omega ** (j * k)) for j in range(n))
            result.append(val / math.sqrt(n))
        
        return result
    
    @staticmethod
    def change_basis(tile: HolographicTile, 
                    new_basis: BasisType) -> HolographicTile:
        """Change tile to new basis."""
        if tile.basis_type == new_basis:
            return tile
        
        amplitudes = tile.data.to_dense()
        
        # First convert to computational if not already
        if tile.basis_type == BasisType.HADAMARD:
            amplitudes = BasisChange.hadamard_to_computational(amplitudes)
        elif tile.basis_type == BasisType.FOURIER:
            amplitudes = BasisChange.fourier_to_computational(amplitudes)
        
        # Then convert to target
        if new_basis == BasisType.HADAMARD:
            amplitudes = BasisChange.computational_to_hadamard(amplitudes)
        elif new_basis == BasisType.FOURIER:
            amplitudes = BasisChange.computational_to_fourier(amplitudes)
        
        # Update tile
        tile.data = TileData.from_amplitudes(amplitudes, tile.data.storage_format)
        tile.basis_type = new_basis
        
        return tile


# =============================================================================
# VALIDATION
# =============================================================================

def validate_tiles() -> bool:
    """Validate tiles module."""
    
    # Test QubitOrdering
    ordering = QubitOrdering({0, 1, 2})
    assert len(ordering) == 3
    assert ordering.position(1) == 1
    
    # Test ErrorDescriptor
    error = ErrorDescriptor(error_budget=1e-4)
    error.add_error(1e-5, "truncation")
    assert error.within_budget()
    
    # Test TileData
    data = TileData.from_amplitudes([1+0j, 0j, 0j, 0j])
    assert data.dimension == 4
    assert data.get(0) == 1+0j
    assert data.sparsity == 0.25
    
    # Test sparse compression
    data2 = TileData.from_amplitudes([1+0j, 1e-12, 1e-12, 0j])
    error = data2.compress_sparse(threshold=1e-10)
    assert data2.storage_format == StorageFormat.SPARSE
    assert len(data2.sparse_data) == 1
    
    # Test HolographicTile
    from .blocktree import BlockTree
    tree = BlockTree.flat_tree(2)
    leaf = tree.leaves()[0]
    
    tile = HolographicTile(
        tile_id=0,
        node=leaf,
        qubit_support=leaf.label,
        ordering=QubitOrdering(leaf.label),
        data=TileData.from_amplitudes([1+0j, 0j])
    )
    assert tile.dimension == 2
    assert tile.get_amplitude(0) == 1+0j
    
    # Test BasisChange
    amps = [1+0j, 0j]
    hadamard_amps = BasisChange.computational_to_hadamard(amps)
    assert abs(hadamard_amps[0] - 1/math.sqrt(2)) < 1e-10
    
    # Test TileConfiguration
    config = TileConfiguration.from_tree(tree)
    assert config.num_tiles == 2
    
    return True


if __name__ == "__main__":
    print("Validating QHC Tiles Module...")
    assert validate_tiles()
    print("✓ Tiles module validated")
    
    # Demo
    print("\n=== QHC Holographic Tiles Demo ===")
    
    from .blocktree import BlockTree
    
    # Create tree and configuration
    tree = BlockTree.binary_tree(4)
    config = TileConfiguration.from_tree(tree)
    
    print(f"\n4-qubit binary tree:")
    print(f"  Tiles: {config.num_tiles}")
    
    # Show tile info
    for tile in config.leaf_tiles():
        summary = tile.summary()
        print(f"\nTile {summary['tile_id']}:")
        print(f"  Qubits: {summary['qubits']}")
        print(f"  Dimension: {summary['dimension']}")
        print(f"  Basis: {summary['basis']}")
        print(f"  Storage: {summary['storage']}")
    
    # Demonstrate basis change
    tile = config.leaf_tiles()[0]
    tile.data = TileData.from_amplitudes([1+0j, 0j])
    
    print(f"\nBasis change demo:")
    print(f"  Original (computational): {tile.data.to_dense()}")
    
    BasisChange.change_basis(tile, BasisType.HADAMARD)
    print(f"  After Hadamard: {[f'{v:.3f}' for v in tile.data.to_dense()]}")

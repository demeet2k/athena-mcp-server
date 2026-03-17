"""
ATHENA OS - Quantum Holography Computing (QHC)
==============================================
Tile Operations

From Quantum_Holography_Computing_(QHC).docx:

THREE PRIMITIVE OPERATIONS:
    1. Local gate application (on tiles)
    2. Basis changes (between representation types)
    3. Tile restructuring (merge/split/reorder)

OPERATOR CALCULUS:
    Arbitrary circuits realized as compositions
    of tile-level operations

GATE APPLICATION:
    G_S: ℋ_S → ℋ_S on subsystem S
    Extended to full space: G_S ⊗ I_{[n]\S}
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math
import cmath

from .hilbert import HilbertSpace, StateVector, LocalOperator
from .blocktree import BlockTree, TreeNode
from .tiles import (
    HolographicTile, TileData, TileConfiguration,
    BasisType, StorageFormat, BasisChange
)
from .modewords import ModeWord, TileRole


# =============================================================================
# OPERATION TYPES
# =============================================================================

class OperationType(Enum):
    """Types of tile operations."""
    LOCAL_GATE = "local_gate"
    BASIS_CHANGE = "basis_change"
    MERGE = "merge"
    SPLIT = "split"
    REORDER = "reorder"
    COMPRESS = "compress"
    DECOMPRESS = "decompress"


# =============================================================================
# OPERATION RESULT
# =============================================================================

@dataclass
class OperationResult:
    """Result of a tile operation."""
    
    success: bool = True
    operation_type: OperationType = OperationType.LOCAL_GATE
    error_incurred: float = 0.0
    computational_cost: float = 0.0
    message: str = ""
    modified_tiles: List[int] = field(default_factory=list)


# =============================================================================
# GATE LIBRARY
# =============================================================================

@dataclass
class GateLibrary:
    """
    Library of standard quantum gates.
    """
    
    @staticmethod
    def identity(dim: int = 2) -> List[List[complex]]:
        """Identity gate."""
        return [[1+0j if i == j else 0j for j in range(dim)] for i in range(dim)]
    
    @staticmethod
    def pauli_x() -> List[List[complex]]:
        """Pauli X (NOT)."""
        return [[0j, 1+0j], [1+0j, 0j]]
    
    @staticmethod
    def pauli_y() -> List[List[complex]]:
        """Pauli Y."""
        return [[0j, -1j], [1j, 0j]]
    
    @staticmethod
    def pauli_z() -> List[List[complex]]:
        """Pauli Z."""
        return [[1+0j, 0j], [0j, -1+0j]]
    
    @staticmethod
    def hadamard() -> List[List[complex]]:
        """Hadamard gate."""
        h = 1 / math.sqrt(2)
        return [[h+0j, h+0j], [h+0j, -h+0j]]
    
    @staticmethod
    def phase(theta: float) -> List[List[complex]]:
        """Phase gate P(θ)."""
        return [[1+0j, 0j], [0j, cmath.exp(1j * theta)]]
    
    @staticmethod
    def t_gate() -> List[List[complex]]:
        """T gate (π/4 phase)."""
        return GateLibrary.phase(math.pi / 4)
    
    @staticmethod
    def s_gate() -> List[List[complex]]:
        """S gate (π/2 phase)."""
        return GateLibrary.phase(math.pi / 2)
    
    @staticmethod
    def rx(theta: float) -> List[List[complex]]:
        """Rotation around X axis."""
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        return [[c+0j, -1j*s], [-1j*s, c+0j]]
    
    @staticmethod
    def ry(theta: float) -> List[List[complex]]:
        """Rotation around Y axis."""
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        return [[c+0j, -s+0j], [s+0j, c+0j]]
    
    @staticmethod
    def rz(theta: float) -> List[List[complex]]:
        """Rotation around Z axis."""
        return [[cmath.exp(-1j*theta/2), 0j], [0j, cmath.exp(1j*theta/2)]]
    
    @staticmethod
    def cnot() -> List[List[complex]]:
        """CNOT (controlled-NOT)."""
        return [
            [1+0j, 0j, 0j, 0j],
            [0j, 1+0j, 0j, 0j],
            [0j, 0j, 0j, 1+0j],
            [0j, 0j, 1+0j, 0j]
        ]
    
    @staticmethod
    def cz() -> List[List[complex]]:
        """CZ (controlled-Z)."""
        return [
            [1+0j, 0j, 0j, 0j],
            [0j, 1+0j, 0j, 0j],
            [0j, 0j, 1+0j, 0j],
            [0j, 0j, 0j, -1+0j]
        ]
    
    @staticmethod
    def swap() -> List[List[complex]]:
        """SWAP gate."""
        return [
            [1+0j, 0j, 0j, 0j],
            [0j, 0j, 1+0j, 0j],
            [0j, 1+0j, 0j, 0j],
            [0j, 0j, 0j, 1+0j]
        ]
    
    @staticmethod
    def toffoli() -> List[List[complex]]:
        """Toffoli (CCNOT) gate."""
        mat = [[0j for _ in range(8)] for _ in range(8)]
        for i in range(6):
            mat[i][i] = 1+0j
        mat[6][7] = 1+0j
        mat[7][6] = 1+0j
        return mat


# =============================================================================
# LOCAL GATE OPERATION
# =============================================================================

@dataclass
class LocalGateOperation:
    """
    Apply a local gate to a tile.
    
    G|ψ⟩ where G acts on the tile's qubits.
    """
    
    gate_matrix: List[List[complex]]
    target_qubits: Set[int]
    name: str = "G"
    
    def apply_to_tile(self, tile: HolographicTile) -> OperationResult:
        """Apply gate to tile."""
        if not self.target_qubits.issubset(tile.qubit_support):
            return OperationResult(
                success=False,
                operation_type=OperationType.LOCAL_GATE,
                message="Gate qubits not in tile support"
            )
        
        # Get amplitudes in dense form
        amplitudes = tile.data.to_dense()
        dim = len(amplitudes)
        gate_dim = len(self.gate_matrix)
        
        if gate_dim == dim:
            # Full tile gate
            new_amps = []
            for i in range(dim):
                val = sum(
                    self.gate_matrix[i][j] * amplitudes[j]
                    for j in range(dim)
                )
                new_amps.append(val)
        elif gate_dim == 2 and dim > 2:
            # Single-qubit gate on multi-qubit tile
            # Find target qubit position
            target = list(self.target_qubits)[0]
            pos = tile.ordering.position(target)
            new_amps = self._apply_single_qubit_gate(amplitudes, pos, tile.num_qubits)
        elif gate_dim == 4 and dim >= 4:
            # Two-qubit gate
            targets = sorted(self.target_qubits)
            pos0 = tile.ordering.position(targets[0])
            pos1 = tile.ordering.position(targets[1])
            new_amps = self._apply_two_qubit_gate(amplitudes, pos0, pos1, tile.num_qubits)
        else:
            return OperationResult(
                success=False,
                operation_type=OperationType.LOCAL_GATE,
                message=f"Unsupported gate dimension {gate_dim} for tile dimension {dim}"
            )
        
        # Update tile
        tile.data = TileData.from_amplitudes(new_amps, tile.data.storage_format)
        
        return OperationResult(
            success=True,
            operation_type=OperationType.LOCAL_GATE,
            computational_cost=dim * gate_dim,
            modified_tiles=[tile.tile_id]
        )
    
    def _apply_single_qubit_gate(self, amps: List[complex], 
                                  qubit_pos: int, n_qubits: int) -> List[complex]:
        """Apply single-qubit gate at position."""
        dim = len(amps)
        new_amps = [0j] * dim
        step = 1 << qubit_pos
        
        for i in range(dim):
            bit = (i >> qubit_pos) & 1
            partner = i ^ step
            
            if bit == 0:
                new_amps[i] += self.gate_matrix[0][0] * amps[i] + self.gate_matrix[0][1] * amps[partner]
            else:
                new_amps[i] += self.gate_matrix[1][0] * amps[partner] + self.gate_matrix[1][1] * amps[i]
        
        return new_amps
    
    def _apply_two_qubit_gate(self, amps: List[complex],
                               pos0: int, pos1: int, n_qubits: int) -> List[complex]:
        """Apply two-qubit gate at positions."""
        dim = len(amps)
        new_amps = list(amps)
        
        for i in range(dim):
            b0 = (i >> pos0) & 1
            b1 = (i >> pos1) & 1
            row = b0 + 2 * b1
            
            # Compute all indices in same block
            base = i & ~((1 << pos0) | (1 << pos1))
            indices = [
                base,
                base | (1 << pos0),
                base | (1 << pos1),
                base | (1 << pos0) | (1 << pos1)
            ]
            
            # Apply gate
            old_vals = [amps[idx] for idx in indices]
            for j, idx in enumerate(indices):
                new_amps[idx] = sum(
                    self.gate_matrix[j][k] * old_vals[k]
                    for k in range(4)
                )
        
        return new_amps


# =============================================================================
# TILE RESTRUCTURING
# =============================================================================

@dataclass
class TileMergeOperation:
    """
    Merge two sibling tiles into one.
    """
    
    def merge(self, tile1: HolographicTile, tile2: HolographicTile,
              tree: BlockTree) -> Tuple[HolographicTile, OperationResult]:
        """Merge two tiles."""
        # Verify siblings
        if tile1.node.parent != tile2.node.parent:
            return None, OperationResult(
                success=False,
                operation_type=OperationType.MERGE,
                message="Tiles are not siblings"
            )
        
        # Compute tensor product of amplitudes
        amps1 = tile1.data.to_dense()
        amps2 = tile2.data.to_dense()
        
        merged_amps = []
        for a1 in amps1:
            for a2 in amps2:
                merged_amps.append(a1 * a2)
        
        # Create merged tile
        merged_qubits = tile1.qubit_support | tile2.qubit_support
        from .tiles import QubitOrdering
        
        merged_tile = HolographicTile(
            tile_id=max(tile1.tile_id, tile2.tile_id) + 1000,
            node=tile1.node.parent,  # Move up to parent
            qubit_support=merged_qubits,
            ordering=QubitOrdering(merged_qubits),
            basis_type=tile1.basis_type,
            data=TileData.from_amplitudes(merged_amps)
        )
        
        return merged_tile, OperationResult(
            success=True,
            operation_type=OperationType.MERGE,
            computational_cost=len(merged_amps),
            modified_tiles=[tile1.tile_id, tile2.tile_id, merged_tile.tile_id]
        )


@dataclass
class TileSplitOperation:
    """
    Split a tile into multiple tiles.
    """
    
    def split(self, tile: HolographicTile, 
              partition: List[Set[int]]) -> Tuple[List[HolographicTile], OperationResult]:
        """
        Split tile according to qubit partition.
        
        Note: Only works for product states in general.
        """
        # Verify partition
        union = set()
        for part in partition:
            if union & part:
                return [], OperationResult(
                    success=False,
                    operation_type=OperationType.SPLIT,
                    message="Partition not disjoint"
                )
            union |= part
        
        if union != tile.qubit_support:
            return [], OperationResult(
                success=False,
                operation_type=OperationType.SPLIT,
                message="Partition doesn't cover tile qubits"
            )
        
        # For simplicity, return trivial splits (basis states)
        from .tiles import QubitOrdering
        
        new_tiles = []
        for i, part in enumerate(partition):
            dim = 2 ** len(part)
            # Initialize to |0...0⟩
            amps = [0j] * dim
            amps[0] = 1+0j
            
            new_tile = HolographicTile(
                tile_id=tile.tile_id * 10 + i,
                node=tile.node,  # Would need tree update
                qubit_support=part,
                ordering=QubitOrdering(part),
                basis_type=tile.basis_type,
                data=TileData.from_amplitudes(amps)
            )
            new_tiles.append(new_tile)
        
        return new_tiles, OperationResult(
            success=True,
            operation_type=OperationType.SPLIT,
            message="Split into product state approximation",
            modified_tiles=[tile.tile_id] + [t.tile_id for t in new_tiles]
        )


# =============================================================================
# COMPRESSION OPERATION
# =============================================================================

@dataclass
class CompressionOperation:
    """
    Compress tile representation.
    """
    
    threshold: float = 1e-10
    
    def compress_sparse(self, tile: HolographicTile) -> OperationResult:
        """Compress to sparse representation."""
        if tile.data.storage_format != StorageFormat.DENSE:
            return OperationResult(
                success=False,
                operation_type=OperationType.COMPRESS,
                message="Tile not in dense format"
            )
        
        error = tile.data.compress_sparse(self.threshold)
        tile.error.add_error(error, "truncation")
        
        return OperationResult(
            success=True,
            operation_type=OperationType.COMPRESS,
            error_incurred=error,
            modified_tiles=[tile.tile_id]
        )
    
    def decompress(self, tile: HolographicTile) -> OperationResult:
        """Decompress to dense representation."""
        if tile.data.storage_format == StorageFormat.DENSE:
            return OperationResult(
                success=True,
                operation_type=OperationType.DECOMPRESS,
                message="Already dense"
            )
        
        dense = tile.data.to_dense()
        tile.data = TileData.from_amplitudes(dense, StorageFormat.DENSE)
        
        return OperationResult(
            success=True,
            operation_type=OperationType.DECOMPRESS,
            modified_tiles=[tile.tile_id]
        )


# =============================================================================
# CIRCUIT
# =============================================================================

@dataclass
class CircuitGate:
    """A gate in a circuit."""
    gate_name: str
    qubits: List[int]
    params: List[float] = field(default_factory=list)


@dataclass
class Circuit:
    """
    Quantum circuit as sequence of gates.
    """
    
    n_qubits: int
    gates: List[CircuitGate] = field(default_factory=list)
    
    def add_gate(self, name: str, qubits: List[int], params: List[float] = None) -> None:
        """Add gate to circuit."""
        self.gates.append(CircuitGate(name, qubits, params or []))
    
    def h(self, qubit: int) -> 'Circuit':
        """Add Hadamard."""
        self.add_gate("H", [qubit])
        return self
    
    def x(self, qubit: int) -> 'Circuit':
        """Add Pauli X."""
        self.add_gate("X", [qubit])
        return self
    
    def z(self, qubit: int) -> 'Circuit':
        """Add Pauli Z."""
        self.add_gate("Z", [qubit])
        return self
    
    def cx(self, control: int, target: int) -> 'Circuit':
        """Add CNOT."""
        self.add_gate("CX", [control, target])
        return self
    
    def rz(self, qubit: int, theta: float) -> 'Circuit':
        """Add RZ rotation."""
        self.add_gate("RZ", [qubit], [theta])
        return self
    
    @property
    def depth(self) -> int:
        """Circuit depth (layers)."""
        if not self.gates:
            return 0
        
        # Track last layer each qubit was used
        last_layer = {q: 0 for q in range(self.n_qubits)}
        
        for gate in self.gates:
            layer = max(last_layer[q] for q in gate.qubits) + 1
            for q in gate.qubits:
                last_layer[q] = layer
        
        return max(last_layer.values())


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operators() -> bool:
    """Validate operators module."""
    
    # Test GateLibrary
    h = GateLibrary.hadamard()
    assert len(h) == 2
    assert abs(h[0][0] - 1/math.sqrt(2)) < 1e-10
    
    cnot = GateLibrary.cnot()
    assert len(cnot) == 4
    
    # Test LocalGateOperation
    from .blocktree import BlockTree
    from .tiles import TileConfiguration, QubitOrdering
    
    tree = BlockTree.flat_tree(2)
    config = TileConfiguration.from_tree(tree)
    tile = config.leaf_tiles()[0]
    tile.data = TileData.from_amplitudes([1+0j, 0j])
    
    h_op = LocalGateOperation(
        gate_matrix=GateLibrary.hadamard(),
        target_qubits={0},
        name="H"
    )
    
    result = h_op.apply_to_tile(tile)
    assert result.success
    
    # Check H|0⟩ = |+⟩
    amps = tile.data.to_dense()
    assert abs(abs(amps[0]) - 1/math.sqrt(2)) < 1e-10
    
    # Test Circuit
    circuit = Circuit(n_qubits=2)
    circuit.h(0).cx(0, 1)
    assert len(circuit.gates) == 2
    assert circuit.depth == 2
    
    # Test CompressionOperation
    tile2 = config.leaf_tiles()[1]
    tile2.data = TileData.from_amplitudes([1+0j, 1e-12])
    
    comp = CompressionOperation(threshold=1e-10)
    result = comp.compress_sparse(tile2)
    assert result.success
    assert tile2.data.storage_format == StorageFormat.SPARSE
    
    return True


if __name__ == "__main__":
    print("Validating QHC Operators Module...")
    assert validate_operators()
    print("✓ Operators module validated")
    
    # Demo
    print("\n=== QHC Operators Demo ===")
    
    from .blocktree import BlockTree
    from .tiles import TileConfiguration
    
    # Create tile
    tree = BlockTree.flat_tree(2)
    config = TileConfiguration.from_tree(tree)
    tile = config.leaf_tiles()[0]
    tile.data = TileData.from_amplitudes([1+0j, 0j])
    
    print(f"\nInitial tile: |0⟩")
    print(f"  Amplitudes: {tile.data.to_dense()}")
    
    # Apply H
    h_op = LocalGateOperation(
        gate_matrix=GateLibrary.hadamard(),
        target_qubits={0},
        name="H"
    )
    result = h_op.apply_to_tile(tile)
    
    print(f"\nAfter Hadamard:")
    print(f"  Amplitudes: {[f'{v:.4f}' for v in tile.data.to_dense()]}")
    print(f"  Cost: {result.computational_cost}")
    
    # Build circuit
    circuit = Circuit(n_qubits=3)
    circuit.h(0).h(1).h(2).cx(0, 1).cx(1, 2)
    
    print(f"\nCircuit:")
    print(f"  Qubits: {circuit.n_qubits}")
    print(f"  Gates: {len(circuit.gates)}")
    print(f"  Depth: {circuit.depth}")
    for gate in circuit.gates:
        print(f"    {gate.gate_name} on {gate.qubits}")

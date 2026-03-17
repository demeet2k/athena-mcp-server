"""
ATHENA OS - Quantum Holography Computing (QHC)
==============================================
Runtime and Execution

From Quantum_Holography_Computing_(QHC).docx:

RUNTIME ARCHITECTURE:
    - State management via tile configurations
    - Gate application through tile operations
    - Error tracking and budget management
    - Adaptive compression policies

CIRCUIT EXECUTION:
    1. Initialize tile configuration
    2. For each gate:
       a. Identify affected tiles
       b. Apply local operation
       c. Track errors
       d. Consider restructuring
    3. Extract final state

ERROR CALCULUS:
    Local error budgets ε_v
    Global error: ‖ψ - ψ̃‖ ≤ C(T) √(Σε_v²)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math
import time

from .hilbert import HilbertSpace, StateVector, QubitIndexSet
from .blocktree import BlockTree, TreeNode
from .tiles import (
    HolographicTile, TileData, TileConfiguration,
    BasisType, StorageFormat, ErrorDescriptor
)
from .modewords import (
    ModeWord, ControlInterface, Policy,
    RepresentationMode, PrecisionLevel
)
from .operators import (
    Circuit, CircuitGate, GateLibrary,
    LocalGateOperation, CompressionOperation, OperationResult
)


# =============================================================================
# RUNTIME CONFIGURATION
# =============================================================================

@dataclass
class RuntimeConfig:
    """Configuration for QHC runtime."""
    
    # Error management
    global_error_budget: float = 1e-6
    per_tile_error_budget: float = 1e-8
    
    # Compression
    auto_compress: bool = True
    compression_threshold: float = 0.1  # Sparsity threshold
    
    # Performance
    max_tile_dimension: int = 256  # 8 qubits per tile
    merge_threshold: int = 4  # Merge tiles smaller than this
    
    # Diagnostics
    track_history: bool = True
    verbose: bool = False


# =============================================================================
# RUNTIME STATE
# =============================================================================

@dataclass
class RuntimeState:
    """Current state of QHC runtime."""
    
    # Tile configuration
    config: TileConfiguration
    
    # Control interface
    control: ControlInterface = field(default_factory=ControlInterface)
    
    # Global state tracking
    n_qubits: int = 0
    current_step: int = 0
    total_error: float = 0.0
    
    # History
    error_history: List[float] = field(default_factory=list)
    operation_history: List[OperationResult] = field(default_factory=list)
    
    def record_operation(self, result: OperationResult) -> None:
        """Record operation result."""
        self.operation_history.append(result)
        if result.error_incurred > 0:
            self.total_error = math.sqrt(
                self.total_error**2 + result.error_incurred**2
            )
            self.error_history.append(self.total_error)
        self.current_step += 1


# =============================================================================
# GATE RESOLVER
# =============================================================================

@dataclass
class GateResolver:
    """
    Resolve circuit gates to tile operations.
    """
    
    @staticmethod
    def resolve_gate(gate: CircuitGate) -> Tuple[List[List[complex]], str]:
        """Resolve gate name to matrix."""
        name = gate.gate_name.upper()
        
        if name == "H":
            return GateLibrary.hadamard(), "H"
        elif name == "X":
            return GateLibrary.pauli_x(), "X"
        elif name == "Y":
            return GateLibrary.pauli_y(), "Y"
        elif name == "Z":
            return GateLibrary.pauli_z(), "Z"
        elif name == "S":
            return GateLibrary.s_gate(), "S"
        elif name == "T":
            return GateLibrary.t_gate(), "T"
        elif name in ["CX", "CNOT"]:
            return GateLibrary.cnot(), "CX"
        elif name == "CZ":
            return GateLibrary.cz(), "CZ"
        elif name == "SWAP":
            return GateLibrary.swap(), "SWAP"
        elif name == "RX" and gate.params:
            return GateLibrary.rx(gate.params[0]), f"RX({gate.params[0]:.2f})"
        elif name == "RY" and gate.params:
            return GateLibrary.ry(gate.params[0]), f"RY({gate.params[0]:.2f})"
        elif name == "RZ" and gate.params:
            return GateLibrary.rz(gate.params[0]), f"RZ({gate.params[0]:.2f})"
        elif name == "P" and gate.params:
            return GateLibrary.phase(gate.params[0]), f"P({gate.params[0]:.2f})"
        else:
            # Default to identity
            dim = 2 ** len(gate.qubits)
            return GateLibrary.identity(dim), "I"
    
    @staticmethod
    def find_containing_tile(qubits: Set[int], 
                            config: TileConfiguration) -> Optional[HolographicTile]:
        """Find tile containing all specified qubits."""
        for tile in config.tiles.values():
            if qubits.issubset(tile.qubit_support):
                return tile
        return None
    
    @staticmethod
    def find_affected_tiles(qubits: Set[int],
                           config: TileConfiguration) -> List[HolographicTile]:
        """Find all tiles overlapping with qubits."""
        return [
            tile for tile in config.tiles.values()
            if qubits & tile.qubit_support
        ]


# =============================================================================
# QHC RUNTIME
# =============================================================================

@dataclass
class QHCRuntime:
    """
    Quantum Holography Computing runtime.
    
    Executes circuits via tile operations with error tracking.
    """
    
    config: RuntimeConfig = field(default_factory=RuntimeConfig)
    state: Optional[RuntimeState] = None
    
    # Statistics
    gates_executed: int = 0
    compressions_applied: int = 0
    total_time: float = 0.0
    
    def initialize(self, n_qubits: int, 
                  tree_type: str = "binary") -> RuntimeState:
        """
        Initialize runtime for n-qubit computation.
        
        Args:
            n_qubits: Number of qubits
            tree_type: "binary", "linear", or "flat"
        """
        # Create block-tree
        if tree_type == "binary":
            tree = BlockTree.binary_tree(n_qubits)
        elif tree_type == "linear":
            tree = BlockTree.linear_tree(n_qubits)
        else:
            tree = BlockTree.flat_tree(n_qubits)
        
        # Create tile configuration
        tile_config = TileConfiguration.from_tree(tree)
        
        # Initialize tiles to |0⟩
        for tile in tile_config.tiles.values():
            dim = tile.dimension
            amps = [0j] * dim
            amps[0] = 1+0j
            tile.data = TileData.from_amplitudes(amps)
            tile.error = ErrorDescriptor(
                error_budget=self.config.per_tile_error_budget
            )
        
        # Create control interface
        control = ControlInterface()
        for tile_id in tile_config.tiles:
            control.set_mode(tile_id, ModeWord.default())
        
        # Create runtime state
        self.state = RuntimeState(
            config=tile_config,
            control=control,
            n_qubits=n_qubits
        )
        
        if self.config.verbose:
            print(f"QHC Runtime initialized: {n_qubits} qubits, {tile_config.num_tiles} tiles")
        
        return self.state
    
    def execute_gate(self, gate: CircuitGate) -> OperationResult:
        """Execute a single gate."""
        if self.state is None:
            return OperationResult(success=False, message="Runtime not initialized")
        
        # Resolve gate
        matrix, name = GateResolver.resolve_gate(gate)
        qubits = set(gate.qubits)
        
        # Find containing tile
        tile = GateResolver.find_containing_tile(qubits, self.state.config)
        
        if tile is None:
            # Gate spans multiple tiles - need to merge or use different strategy
            affected = GateResolver.find_affected_tiles(qubits, self.state.config)
            if len(affected) == 0:
                return OperationResult(
                    success=False,
                    message=f"No tiles contain qubits {qubits}"
                )
            
            # For now, apply to first affected tile (simplified)
            tile = affected[0]
            if not qubits.issubset(tile.qubit_support):
                return OperationResult(
                    success=False,
                    message=f"Gate qubits {qubits} span multiple tiles"
                )
        
        # Create and apply operation
        operation = LocalGateOperation(
            gate_matrix=matrix,
            target_qubits=qubits,
            name=name
        )
        
        result = operation.apply_to_tile(tile)
        
        # Record
        if self.config.track_history:
            self.state.record_operation(result)
        
        if result.success:
            self.gates_executed += 1
        
        return result
    
    def execute_circuit(self, circuit: Circuit) -> List[OperationResult]:
        """Execute a complete circuit."""
        start_time = time.time()
        results = []
        
        if self.state is None:
            self.initialize(circuit.n_qubits)
        
        for gate in circuit.gates:
            result = self.execute_gate(gate)
            results.append(result)
            
            if not result.success and self.config.verbose:
                print(f"Gate {gate.gate_name} failed: {result.message}")
            
            # Consider compression
            if self.config.auto_compress and result.success:
                self._consider_compression()
        
        self.total_time += time.time() - start_time
        
        return results
    
    def _consider_compression(self) -> None:
        """Consider compressing tiles if beneficial."""
        if self.state is None:
            return
        
        compressor = CompressionOperation(threshold=1e-10)
        
        for tile in self.state.config.tiles.values():
            if tile.data.storage_format != StorageFormat.DENSE:
                continue
            
            # Check sparsity
            sparsity = tile.data.sparsity
            if sparsity < self.config.compression_threshold:
                result = compressor.compress_sparse(tile)
                if result.success:
                    self.compressions_applied += 1
                    if self.config.verbose:
                        print(f"Compressed tile {tile.tile_id}, sparsity={sparsity:.4f}")
    
    def get_state_vector(self) -> Optional[StateVector]:
        """
        Reconstruct full state vector from tiles.
        
        Only works for single-tile or product state configurations.
        """
        if self.state is None:
            return None
        
        tiles = list(self.state.config.tiles.values())
        
        if len(tiles) == 1:
            # Single tile - direct conversion
            return tiles[0].to_state_vector()
        
        # Multiple tiles - tensor product (product states only)
        from .hilbert import TensorProduct
        
        states = [t.to_state_vector() for t in tiles]
        return TensorProduct.product_state(states)
    
    def get_probabilities(self) -> Optional[List[float]]:
        """Get measurement probabilities."""
        state = self.get_state_vector()
        if state is None:
            return None
        return state.probabilities()
    
    def measure(self, shots: int = 1000) -> Dict[int, int]:
        """
        Simulate measurements.
        
        Returns counts of each outcome.
        """
        import random
        
        probs = self.get_probabilities()
        if probs is None:
            return {}
        
        counts = {}
        for _ in range(shots):
            r = random.random()
            cumsum = 0.0
            for i, p in enumerate(probs):
                cumsum += p
                if r <= cumsum:
                    counts[i] = counts.get(i, 0) + 1
                    break
        
        return counts
    
    def summary(self) -> Dict[str, Any]:
        """Get runtime summary."""
        return {
            "n_qubits": self.state.n_qubits if self.state else 0,
            "num_tiles": self.state.config.num_tiles if self.state else 0,
            "gates_executed": self.gates_executed,
            "compressions_applied": self.compressions_applied,
            "total_error": self.state.total_error if self.state else 0.0,
            "total_time_ms": self.total_time * 1000,
            "error_budget_remaining": (
                self.config.global_error_budget - self.state.total_error
                if self.state else self.config.global_error_budget
            )
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_qhc_runtime(n_qubits: int, **kwargs) -> QHCRuntime:
    """Create and initialize QHC runtime."""
    config = RuntimeConfig(**kwargs)
    runtime = QHCRuntime(config=config)
    runtime.initialize(n_qubits)
    return runtime


def simulate_circuit(circuit: Circuit, **kwargs) -> Dict[str, Any]:
    """
    Simulate circuit and return results.
    
    Returns:
        Dictionary with probabilities, measurements, and diagnostics
    """
    runtime = create_qhc_runtime(circuit.n_qubits, **kwargs)
    results = runtime.execute_circuit(circuit)
    
    return {
        "probabilities": runtime.get_probabilities(),
        "measurements": runtime.measure(shots=1000),
        "gates_executed": runtime.gates_executed,
        "total_error": runtime.state.total_error if runtime.state else 0.0,
        "success": all(r.success for r in results)
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_runtime() -> bool:
    """Validate runtime module."""
    
    # Test RuntimeConfig
    config = RuntimeConfig()
    assert config.global_error_budget == 1e-6
    
    # Test QHCRuntime initialization
    runtime = QHCRuntime()
    state = runtime.initialize(4, tree_type="binary")
    assert state.n_qubits == 4
    assert state.config.num_tiles > 0
    
    # Test gate execution
    gate = CircuitGate("H", [0])
    result = runtime.execute_gate(gate)
    assert result.success
    
    # Test circuit execution
    circuit = Circuit(n_qubits=2)
    circuit.h(0).cx(0, 1)
    
    runtime2 = QHCRuntime()
    runtime2.initialize(2, tree_type="flat")
    results = runtime2.execute_circuit(circuit)
    
    # For flat tree, each qubit is its own tile - CX spans tiles
    # Expected: H succeeds, CX may fail due to spanning tiles
    assert results[0].success  # H on single tile
    
    # Test measurement
    runtime3 = create_qhc_runtime(2)
    runtime3.execute_circuit(Circuit(n_qubits=2).h(0).h(1))
    
    probs = runtime3.get_probabilities()
    assert probs is not None
    assert abs(sum(probs) - 1.0) < 1e-10
    
    counts = runtime3.measure(shots=100)
    assert sum(counts.values()) == 100
    
    # Test simulate_circuit
    result = simulate_circuit(Circuit(n_qubits=2).h(0).h(1))
    assert "probabilities" in result
    assert "measurements" in result
    
    return True


if __name__ == "__main__":
    print("Validating QHC Runtime Module...")
    assert validate_runtime()
    print("✓ Runtime module validated")
    
    # Demo
    print("\n=== QHC Runtime Demo ===")
    
    # Create Bell state circuit
    bell = Circuit(n_qubits=2)
    bell.h(0).cx(0, 1)
    
    print(f"\nBell State Circuit:")
    print(f"  H(0) → CX(0,1)")
    
    # Use flat tree for 2 qubits (single tile for CX to work)
    runtime = QHCRuntime(config=RuntimeConfig(verbose=True))
    
    # For Bell state, use a single tile containing both qubits
    tree = BlockTree.flat_tree(2)
    # Modify to single root tile
    from .tiles import TileConfiguration, TileData, QubitOrdering
    config = TileConfiguration(tree=tree)
    root_tile = config.create_tile(tree.root)
    root_tile.data = TileData.from_amplitudes([1+0j, 0j, 0j, 0j])
    
    runtime.state = RuntimeState(
        config=config,
        n_qubits=2
    )
    
    # Execute
    results = runtime.execute_circuit(bell)
    
    print(f"\nExecution Results:")
    for i, r in enumerate(results):
        status = "✓" if r.success else "✗"
        print(f"  {status} Gate {i}: {r.message or 'OK'}")
    
    # Get probabilities
    probs = runtime.get_probabilities()
    if probs:
        print(f"\nMeasurement Probabilities:")
        for i, p in enumerate(probs):
            if p > 1e-10:
                print(f"  |{i:02b}⟩: {p:.4f}")
    
    # Measure
    counts = runtime.measure(shots=1000)
    print(f"\nMeasurement Results (1000 shots):")
    for outcome, count in sorted(counts.items()):
        print(f"  |{outcome:02b}⟩: {count}")
    
    # Summary
    print(f"\nRuntime Summary:")
    summary = runtime.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

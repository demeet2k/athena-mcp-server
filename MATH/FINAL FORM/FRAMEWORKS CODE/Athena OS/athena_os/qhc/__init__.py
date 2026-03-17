"""
ATHENA OS - Quantum Holography Computing (QHC)
==============================================
Holographic Quantum Simulation Framework

From Quantum_Holography_Computing_(QHC).docx:

ABSTRACT:
    QHC represents quantum states via dynamic interaction between:
    - Low-dimensional BOUNDARY (mode words, control logic)
    - High-dimensional BULK (block-tree of holographic tiles)

CORE CONCEPTS:
    1. Block-Tree Decomposition
       ℋ_n decomposed into tiles on rooted tree T = (V, E)
       λ: V → 2^[n] assigns qubit subsets to nodes
    
    2. Holographic Tiles
       Each tile carries: basis type, data representation,
       error descriptor, mode word
    
    3. Mode Words (8-bit)
       Bits 0-1: Representation (dense/sparse/low-rank/adaptive)
       Bits 2-3: Role (state/gate/noise/diagnostic)
       Bits 4-5: Precision (high/medium/low/adaptive)
       Bits 6-7: Semantic (default/discrete/continuous/mixed)
    
    4. Three Primitive Operations
       - Local gate application
       - Basis changes
       - Tile restructuring (merge/split)

ERROR CALCULUS:
    - Per-tile error budgets ε_v
    - Global error bound: ‖ψ - ψ̃‖ ≤ C(T) √(Σε_v²)
    - Graceful degradation when compression fails

BOUNDARY-BULK PARADIGM:
    Boundary: mode words + policies govern
    Bulk: tile configurations store state
    
    Analogy to AdS/CFT (conceptual, not literal)
"""

from __future__ import annotations

# Hilbert spaces
from .hilbert import (
    QubitIndexSet,
    HilbertSpace,
    StateVector,
    TensorProduct,
    DensityMatrix,
    LocalOperator,
    EntanglementMetrics,
    validate_hilbert,
)

# Block-tree decompositions
from .blocktree import (
    TreeNode,
    BlockTree,
    Bipartition,
    BipartitionAnalyzer,
    PartitionOperations,
    validate_blocktree,
)

# Holographic tiles
from .tiles import (
    BasisType,
    StorageFormat,
    CompressionType,
    QubitOrdering,
    ErrorDescriptor,
    TileData,
    HolographicTile,
    TileConfiguration,
    BasisChange,
    validate_tiles,
)

# Mode words and control
from .modewords import (
    RepresentationMode,
    TileRole,
    PrecisionLevel,
    SemanticTag,
    ModeWord,
    Policy,
    ModeTransitionType,
    ModeTransition,
    ControlInterface,
    FibreState,
    FibreDescriptor,
    validate_modewords,
)

# Operators and gates
from .operators import (
    OperationType,
    OperationResult,
    GateLibrary,
    LocalGateOperation,
    TileMergeOperation,
    TileSplitOperation,
    CompressionOperation,
    CircuitGate,
    Circuit,
    validate_operators,
)

# Runtime
from .runtime import (
    RuntimeConfig,
    RuntimeState,
    GateResolver,
    QHCRuntime,
    create_qhc_runtime,
    simulate_circuit,
    validate_runtime,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_qhc() -> bool:
    """Validate complete QHC module."""
    assert validate_hilbert()
    assert validate_blocktree()
    assert validate_tiles()
    assert validate_modewords()
    assert validate_operators()
    assert validate_runtime()
    return True


# =============================================================================
# CONVENIENCE FACTORIES
# =============================================================================

def create_bell_state() -> StateVector:
    """Create Bell state (|00⟩ + |11⟩)/√2."""
    return StateVector.ghz_state(2)


def create_ghz_state(n: int) -> StateVector:
    """Create n-qubit GHZ state."""
    return StateVector.ghz_state(n)


def create_simulator(n_qubits: int, **kwargs) -> QHCRuntime:
    """Create QHC simulator for n qubits."""
    return create_qhc_runtime(n_qubits, **kwargs)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Hilbert
    "QubitIndexSet", "HilbertSpace", "StateVector",
    "TensorProduct", "DensityMatrix", "LocalOperator",
    "EntanglementMetrics",
    
    # Block-tree
    "TreeNode", "BlockTree",
    "Bipartition", "BipartitionAnalyzer", "PartitionOperations",
    
    # Tiles
    "BasisType", "StorageFormat", "CompressionType",
    "QubitOrdering", "ErrorDescriptor", "TileData",
    "HolographicTile", "TileConfiguration", "BasisChange",
    
    # Mode words
    "RepresentationMode", "TileRole", "PrecisionLevel", "SemanticTag",
    "ModeWord", "Policy", "ModeTransition", "ModeTransitionType",
    "ControlInterface", "FibreState", "FibreDescriptor",
    
    # Operators
    "OperationType", "OperationResult", "GateLibrary",
    "LocalGateOperation", "TileMergeOperation", "TileSplitOperation",
    "CompressionOperation", "CircuitGate", "Circuit",
    
    # Runtime
    "RuntimeConfig", "RuntimeState", "GateResolver",
    "QHCRuntime", "create_qhc_runtime", "simulate_circuit",
    
    # Factories
    "create_bell_state", "create_ghz_state", "create_simulator",
    
    # Validation
    "validate_qhc",
]

__version__ = "1.0.0"
__module_name__ = "qhc"


if __name__ == "__main__":
    print("=== ATHENA OS Quantum Holography Computing (QHC) ===")
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_qhc():
        print("✓ All components validated")
    
    print("\n--- Module Summary ---")
    
    print("\nBOUNDARY LAYER (Control):")
    print("  Mode Words: 8-bit control strings")
    print("  - Representation: dense/sparse/low-rank/adaptive")
    print("  - Role: state/gate/noise/diagnostic")
    print("  - Precision: high/medium/low/adaptive")
    print("  - Semantic: default/discrete/continuous/mixed")
    
    print("\nBULK LAYER (State):")
    print("  Block-Tree: hierarchical qubit decomposition")
    print("  Holographic Tiles: local state + metadata")
    print("  Error Descriptors: per-tile error budgets")
    
    print("\nTHREE PRIMITIVE OPERATIONS:")
    print("  1. Local gate application")
    print("  2. Basis changes (computational/Fourier/Hadamard)")
    print("  3. Tile restructuring (merge/split)")
    
    # Demo
    print("\n--- Demo ---")
    
    # Create and simulate circuit
    circuit = Circuit(n_qubits=2)
    circuit.h(0).cx(0, 1)
    
    print(f"\nBell State Circuit: H(0) → CX(0,1)")
    
    result = simulate_circuit(circuit)
    
    print(f"\nSimulation Results:")
    print(f"  Success: {result['success']}")
    print(f"  Gates executed: {result['gates_executed']}")
    
    if result['probabilities']:
        print(f"\nProbabilities:")
        for i, p in enumerate(result['probabilities']):
            if p > 0.01:
                print(f"  |{i:02b}⟩: {p:.4f}")
    
    if result['measurements']:
        print(f"\nMeasurements (1000 shots):")
        for outcome, count in sorted(result['measurements'].items()):
            print(f"  |{outcome:02b}⟩: {count}")

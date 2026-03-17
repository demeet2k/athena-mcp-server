"""
ATHENA OS - Core Module
=======================
Fundamental algebraic and computational primitives.

Components:
- bit4: Four-valued logic (BIT4) and Klein-4 group
- registers: 22-register architecture with tetractys structure
- gates: 231-gate combinatorial engine
- integrity: Error correction and checksums
"""

from .bit4 import (
    BIT4,
    BIT4Word,
    TwoRail,
    CollapsePolicy,
    SemanticState,
    # Operators
    negation,
    knowledge_complement,
    conflation,
    identity,
    # Lattice operations
    knowledge_join,
    knowledge_meet,
    truth_join,
    truth_meet,
    # BIT4 logic
    bit4_and,
    bit4_or,
    bit4_not,
    bit4_xor,
    bit4_implies,
    bit4_equiv,
    # Collapse/superpose
    collapse,
    superpose,
    # Klein-4 composition
    compose_operators,
    KLEIN4_OPERATORS,
)

from .registers import (
    RegisterID,
    Register,
    RegisterFile,
    Tetractys,
    ProcessingDAG,
    DAGNode,
)

from .gates import (
    GateType,
    Gate,
    GateMatrix,
    GatePattern,
    cascade_execute,
    broadcast,
    ring_shift,
)

from .integrity import (
    HammingCode,
    HammingConstants,
    IntegrityChecksums,
    PythagoreanComma,
    SpacetimeConstants,
    ProtectedWord,
)

__all__ = [
    # BIT4
    'BIT4', 'BIT4Word', 'TwoRail', 'CollapsePolicy', 'SemanticState',
    'negation', 'knowledge_complement', 'conflation', 'identity',
    'knowledge_join', 'knowledge_meet', 'truth_join', 'truth_meet',
    'bit4_and', 'bit4_or', 'bit4_not', 'bit4_xor', 'bit4_implies', 'bit4_equiv',
    'collapse', 'superpose', 'compose_operators', 'KLEIN4_OPERATORS',
    # Registers
    'RegisterID', 'Register', 'RegisterFile', 'Tetractys', 'ProcessingDAG', 'DAGNode',
    # Gates
    'GateType', 'Gate', 'GateMatrix', 'GatePattern',
    'cascade_execute', 'broadcast', 'ring_shift',
    # Integrity
    'HammingCode', 'HammingConstants', 'IntegrityChecksums',
    'PythagoreanComma', 'SpacetimeConstants', 'ProtectedWord',
]

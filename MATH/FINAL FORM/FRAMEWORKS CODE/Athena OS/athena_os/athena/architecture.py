"""
ATHENA OS - Computational Architecture
======================================
22-Register System with 231 Binary Gates

From ATHENA_OPERATING_SYSTEM_.docx Part II:

ARCHITECTURE:
    - 22 primary registers (R₀ - R₂₁)
    - 231 binary gates = C(22,2)
    - 22 base instructions
    - 10-node processing DAG with 22 edges

REGISTER CLASSIFICATION:
    Class A (Elemental, 3): R₀-R₂
        - R₀: Expansion register (positive accumulator)
        - R₁: Contraction register (negative accumulator)
        - R₂: Balance register (equilibrium)
    
    Class B (Oscillator, 7): R₃-R₉
        - Binary state oscillators
        - Mapped to temporal cycles
    
    Class C (Transform, 12): R₁₀-R₂₁
        - Unary transform registers
        - Mapped to spatial coordinates

MEMORY HIERARCHY:
    Level 0 (Register): 22 primary registers
    Level 1 (Cache): 231 cache lines
    Level 2 (Main): 10 memory banks
    Level 3 (Storage): Unlimited persistent
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math


# =============================================================================
# ARCHITECTURE CONSTANTS
# =============================================================================

REGISTER_COUNT = 22
GATE_COUNT = 231  # C(22,2) = 22*21/2
INSTRUCTION_COUNT = 22
DAG_NODES = 10
DAG_EDGES = 22


# =============================================================================
# REGISTER CLASSES
# =============================================================================

class RegisterClass(Enum):
    """Register classification."""
    ELEMENTAL = "A"   # R₀-R₂: Expansion/Contraction/Balance
    OSCILLATOR = "B"  # R₃-R₉: Binary state oscillators
    TRANSFORM = "C"   # R₁₀-R₂₁: Unary transforms


@dataclass
class Register:
    """
    A single register in the 22-register file.
    """
    
    index: int
    name: str
    reg_class: RegisterClass
    value: int = 0
    
    # Metadata
    description: str = ""
    
    @property
    def address(self) -> str:
        """Get register address (R₀, R₁, etc.)."""
        return f"R{self.index}"
    
    def read(self) -> int:
        """Read register value."""
        return self.value
    
    def write(self, value: int) -> None:
        """Write value to register."""
        self.value = value
    
    def clear(self) -> None:
        """Clear register to zero."""
        self.value = 0


def create_register_file() -> Dict[int, Register]:
    """Create the complete 22-register file."""
    registers = {}
    
    # Class A: Elemental (0-2)
    registers[0] = Register(0, "EXPAND", RegisterClass.ELEMENTAL,
                           description="Expansion register (positive accumulator)")
    registers[1] = Register(1, "CONTRACT", RegisterClass.ELEMENTAL,
                           description="Contraction register (negative accumulator)")
    registers[2] = Register(2, "BALANCE", RegisterClass.ELEMENTAL,
                           description="Balance register (equilibrium state)")
    
    # Class B: Oscillator (3-9)
    for i in range(3, 10):
        registers[i] = Register(i, f"OSC{i-3}", RegisterClass.OSCILLATOR,
                               description=f"Oscillator register {i-3}")
    
    # Class C: Transform (10-21)
    for i in range(10, 22):
        registers[i] = Register(i, f"TRANS{i-10}", RegisterClass.TRANSFORM,
                               description=f"Transform register {i-10}")
    
    return registers


# =============================================================================
# GATE OPERATIONS
# =============================================================================

class GateOp(Enum):
    """Binary gate operations."""
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    NAND = "NAND"
    NOR = "NOR"
    XNOR = "XNOR"
    IMP = "IMP"    # Implication
    NIMP = "NIMP"  # Non-implication


@dataclass
class BinaryGate:
    """
    A binary gate connecting two registers.
    
    Gate(i,j): Rᵢ × Rⱼ → R_output
    """
    
    gate_id: int
    reg_i: int  # First register index
    reg_j: int  # Second register index
    
    def compute_cache_line(self) -> int:
        """
        Compute cache line index.
        
        For registers Rᵢ and Rⱼ where i < j:
        CacheLine(i,j) = i × 21 - i(i-1)/2 + (j - i - 1)
        """
        i, j = min(self.reg_i, self.reg_j), max(self.reg_i, self.reg_j)
        return i * 21 - i * (i - 1) // 2 + (j - i - 1)
    
    def execute(self, op: GateOp, val_i: int, val_j: int) -> int:
        """Execute gate operation on values."""
        if op == GateOp.AND:
            return val_i & val_j
        elif op == GateOp.OR:
            return val_i | val_j
        elif op == GateOp.XOR:
            return val_i ^ val_j
        elif op == GateOp.NAND:
            return ~(val_i & val_j)
        elif op == GateOp.NOR:
            return ~(val_i | val_j)
        elif op == GateOp.XNOR:
            return ~(val_i ^ val_j)
        elif op == GateOp.IMP:
            return (~val_i) | val_j
        elif op == GateOp.NIMP:
            return val_i & (~val_j)
        raise ValueError(f"Unknown operation: {op}")


def create_gate_network() -> Dict[int, BinaryGate]:
    """Create all 231 binary gates."""
    gates = {}
    gate_id = 0
    
    for i in range(REGISTER_COUNT):
        for j in range(i + 1, REGISTER_COUNT):
            gates[gate_id] = BinaryGate(gate_id, i, j)
            gate_id += 1
    
    assert len(gates) == GATE_COUNT
    return gates


# =============================================================================
# INSTRUCTION SET
# =============================================================================

class InstructionFrequency(Enum):
    """Instruction execution frequency band."""
    HIGH = 1      # Immediate execution
    MEDIUM = 7    # Standard priority
    LOW = 12      # Background


class Opcode(Enum):
    """The 22 base instruction opcodes."""
    # High-frequency (0x01 - 0x06)
    NUL = 0x01   # No operation
    MOV = 0x02   # Move data
    CMP = 0x03   # Compare values
    JMP = 0x04   # Unconditional jump
    BRZ = 0x05   # Branch if zero
    BRN = 0x06   # Branch if negative
    
    # Medium-frequency (0x07 - 0x10)
    ADD = 0x07   # Addition
    SUB = 0x08   # Subtraction
    MUL = 0x09   # Multiplication
    DIV = 0x0A   # Division
    AND = 0x0B   # Bitwise AND
    OR = 0x0C    # Bitwise OR
    XOR = 0x0D   # Bitwise XOR
    SHL = 0x0E   # Shift left
    SHR = 0x0F   # Shift right
    NOT = 0x10   # Bitwise NOT
    
    # Low-frequency (0x11 - 0x16)
    LOAD = 0x11  # Load from memory
    STOR = 0x12  # Store to memory
    CALL = 0x13  # Call subroutine
    RET = 0x14   # Return from subroutine
    PUSH = 0x15  # Push to stack
    POP = 0x16   # Pop from stack


@dataclass
class Instruction:
    """A single instruction."""
    
    opcode: Opcode
    operand1: Optional[int] = None
    operand2: Optional[int] = None
    immediate: Optional[int] = None
    
    @property
    def frequency(self) -> InstructionFrequency:
        """Get instruction frequency band."""
        if self.opcode.value <= 0x06:
            return InstructionFrequency.HIGH
        elif self.opcode.value <= 0x10:
            return InstructionFrequency.MEDIUM
        else:
            return InstructionFrequency.LOW
    
    @property
    def cycles(self) -> int:
        """Get execution cycles."""
        return self.frequency.value


# =============================================================================
# PROCESSING DAG
# =============================================================================

class DAGNodeType(Enum):
    """Types of nodes in the processing DAG."""
    INPUT = "input"
    PROCESS = "process"
    TRANSFORM = "transform"
    OUTPUT = "output"
    CONTROL = "control"


@dataclass
class DAGNode:
    """A node in the 10-node processing DAG."""
    
    node_id: int
    name: str
    node_type: DAGNodeType
    
    # Connections
    inputs: List[int] = field(default_factory=list)
    outputs: List[int] = field(default_factory=list)
    
    # State
    value: Any = None


@dataclass
class ProcessingDAG:
    """
    The 10-node processing DAG.
    
    10 nodes, 22 edges
    """
    
    nodes: Dict[int, DAGNode] = field(default_factory=dict)
    edges: List[Tuple[int, int]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default DAG structure."""
        if not self.nodes:
            self._create_default_dag()
    
    def _create_default_dag(self):
        """Create default 10-node DAG."""
        # Create nodes
        self.nodes = {
            0: DAGNode(0, "INPUT", DAGNodeType.INPUT),
            1: DAGNode(1, "PARSE", DAGNodeType.PROCESS),
            2: DAGNode(2, "VALIDATE", DAGNodeType.PROCESS),
            3: DAGNode(3, "TRANSFORM_A", DAGNodeType.TRANSFORM),
            4: DAGNode(4, "TRANSFORM_B", DAGNodeType.TRANSFORM),
            5: DAGNode(5, "COMPUTE", DAGNodeType.PROCESS),
            6: DAGNode(6, "VERIFY", DAGNodeType.PROCESS),
            7: DAGNode(7, "CONTROL", DAGNodeType.CONTROL),
            8: DAGNode(8, "FORMAT", DAGNodeType.PROCESS),
            9: DAGNode(9, "OUTPUT", DAGNodeType.OUTPUT),
        }
        
        # Create 22 edges (ensuring DAG structure)
        self.edges = [
            (0, 1), (0, 2),           # Input fans out
            (1, 3), (1, 4), (1, 5),   # Parse feeds transforms/compute
            (2, 3), (2, 4), (2, 6),   # Validate feeds transforms/verify
            (3, 5), (3, 6),           # Transform A feeds compute/verify
            (4, 5), (4, 6),           # Transform B feeds compute/verify
            (5, 7), (5, 8),           # Compute feeds control/format
            (6, 7), (6, 8),           # Verify feeds control/format
            (7, 8), (7, 9),           # Control feeds format/output
            (8, 9),                    # Format feeds output
            (3, 8), (4, 8),           # Transforms feed format
            (2, 7),                    # Validate feeds control
        ]
        
        # Update node connections
        for src, dst in self.edges:
            self.nodes[src].outputs.append(dst)
            self.nodes[dst].inputs.append(src)
    
    def is_acyclic(self) -> bool:
        """Check if DAG is acyclic."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: int) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for next_id in self.nodes[node_id].outputs:
                if next_id not in visited:
                    if has_cycle(next_id):
                        return True
                elif next_id in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    return False
        
        return True
    
    def verify(self) -> bool:
        """Verify DAG structure."""
        return (
            len(self.nodes) == DAG_NODES and
            len(self.edges) == DAG_EDGES and
            self.is_acyclic()
        )


# =============================================================================
# MEMORY HIERARCHY
# =============================================================================

class MemoryLevel(Enum):
    """Memory hierarchy levels."""
    REGISTER = 0   # 22 registers
    CACHE = 1      # 231 cache lines
    MAIN = 2       # 10 memory banks
    STORAGE = 3    # Unlimited


@dataclass
class MemoryAddress:
    """
    Memory address format:
    [Bank:4][Line:8][Offset:12][Checksum:4]
    Total: 28 bits = 268,435,456 locations
    """
    
    bank: int = 0      # 4 bits (0-15)
    line: int = 0      # 8 bits (0-255)
    offset: int = 0    # 12 bits (0-4095)
    checksum: int = 0  # 4 bits
    
    def to_int(self) -> int:
        """Convert to integer address."""
        addr = (self.bank << 24) | (self.line << 16) | (self.offset << 4) | self.checksum
        return addr
    
    @classmethod
    def from_int(cls, addr: int) -> 'MemoryAddress':
        """Create from integer address."""
        return cls(
            bank=(addr >> 24) & 0xF,
            line=(addr >> 16) & 0xFF,
            offset=(addr >> 4) & 0xFFF,
            checksum=addr & 0xF
        )
    
    def compute_checksum(self) -> int:
        """Compute address checksum."""
        total = self.bank + self.line + self.offset
        return total % 16


@dataclass
class MemoryHierarchy:
    """
    Four-level memory hierarchy.
    """
    
    # Level 0: Registers
    registers: Dict[int, Register] = field(default_factory=dict)
    
    # Level 1: Cache (231 lines)
    cache: Dict[int, int] = field(default_factory=dict)
    
    # Level 2: Main memory (10 banks)
    main_memory: Dict[int, Dict[int, int]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize memory hierarchy."""
        if not self.registers:
            self.registers = create_register_file()
        
        if not self.main_memory:
            self.main_memory = {i: {} for i in range(10)}
    
    def read_register(self, index: int) -> int:
        """Read from register."""
        if index in self.registers:
            return self.registers[index].read()
        return 0
    
    def write_register(self, index: int, value: int) -> None:
        """Write to register."""
        if index in self.registers:
            self.registers[index].write(value)
    
    def read_cache(self, line: int) -> Optional[int]:
        """Read from cache."""
        return self.cache.get(line)
    
    def write_cache(self, line: int, value: int) -> None:
        """Write to cache."""
        self.cache[line] = value


# =============================================================================
# COMPUTATIONAL KERNEL
# =============================================================================

@dataclass
class ComputationalKernel:
    """
    Complete computational kernel.
    
    Integrates registers, gates, instructions, DAG, and memory.
    """
    
    registers: Dict[int, Register] = field(default_factory=dict)
    gates: Dict[int, BinaryGate] = field(default_factory=dict)
    dag: ProcessingDAG = field(default_factory=ProcessingDAG)
    memory: MemoryHierarchy = field(default_factory=MemoryHierarchy)
    
    # Execution state
    instruction_pointer: int = 0
    status_flags: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize kernel components."""
        if not self.registers:
            self.registers = create_register_file()
        if not self.gates:
            self.gates = create_gate_network()
        if not self.status_flags:
            self.status_flags = {
                "zero": False,
                "negative": False,
                "overflow": False,
                "carry": False,
            }
    
    def execute_gate(self, gate_id: int, op: GateOp) -> int:
        """Execute a binary gate operation."""
        gate = self.gates[gate_id]
        val_i = self.registers[gate.reg_i].read()
        val_j = self.registers[gate.reg_j].read()
        return gate.execute(op, val_i, val_j)
    
    def verify(self) -> Dict[str, bool]:
        """Verify kernel structure."""
        return {
            "register_count": len(self.registers) == REGISTER_COUNT,
            "gate_count": len(self.gates) == GATE_COUNT,
            "dag_valid": self.dag.verify(),
        }
    
    def is_ready(self) -> bool:
        """Check if kernel is ready."""
        return all(self.verify().values())
    
    def summary(self) -> Dict[str, Any]:
        """Get kernel summary."""
        return {
            "registers": REGISTER_COUNT,
            "gates": GATE_COUNT,
            "instructions": INSTRUCTION_COUNT,
            "dag_nodes": DAG_NODES,
            "dag_edges": DAG_EDGES,
            "ready": self.is_ready(),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_architecture() -> bool:
    """Validate architecture module."""
    
    # Test register file
    registers = create_register_file()
    assert len(registers) == 22
    
    # Check register classes
    elemental = [r for r in registers.values() if r.reg_class == RegisterClass.ELEMENTAL]
    oscillator = [r for r in registers.values() if r.reg_class == RegisterClass.OSCILLATOR]
    transform = [r for r in registers.values() if r.reg_class == RegisterClass.TRANSFORM]
    assert len(elemental) == 3
    assert len(oscillator) == 7
    assert len(transform) == 12
    
    # Test gate network
    gates = create_gate_network()
    assert len(gates) == 231
    
    # Verify C(22,2) = 231
    from math import comb
    assert comb(22, 2) == 231
    
    # Test processing DAG
    dag = ProcessingDAG()
    assert dag.verify()
    assert len(dag.nodes) == 10
    assert len(dag.edges) == 22
    assert dag.is_acyclic()
    
    # Test memory address
    addr = MemoryAddress(bank=5, line=100, offset=2048)
    addr.checksum = addr.compute_checksum()
    addr_int = addr.to_int()
    addr_back = MemoryAddress.from_int(addr_int)
    assert addr_back.bank == addr.bank
    assert addr_back.line == addr.line
    
    # Test computational kernel
    kernel = ComputationalKernel()
    assert kernel.is_ready()
    
    # Test gate execution
    kernel.registers[0].write(0b1010)
    kernel.registers[1].write(0b1100)
    result = kernel.execute_gate(0, GateOp.AND)
    assert result == 0b1000
    
    return True


if __name__ == "__main__":
    print("Validating Architecture...")
    assert validate_architecture()
    print("✓ Architecture validated")
    
    # Demo
    print("\n=== Computational Architecture Demo ===")
    
    kernel = ComputationalKernel()
    summary = kernel.summary()
    
    print(f"\n22-Register Architecture:")
    print(f"  Registers: {summary['registers']}")
    print(f"    Class A (Elemental): 3 (R₀-R₂)")
    print(f"    Class B (Oscillator): 7 (R₃-R₉)")
    print(f"    Class C (Transform): 12 (R₁₀-R₂₁)")
    
    print(f"\n231-Gate Network:")
    print(f"  Gates: {summary['gates']} = C(22,2)")
    
    print(f"\n22-Instruction Set:")
    print(f"  High-frequency (1 cycle): NUL, MOV, CMP, JMP, BRZ, BRN")
    print(f"  Medium-frequency (7 cycles): ADD, SUB, MUL, DIV, AND, OR, XOR, SHL, SHR, NOT")
    print(f"  Low-frequency (12 cycles): LOAD, STOR, CALL, RET, PUSH, POP")
    
    print(f"\n10-Node Processing DAG:")
    print(f"  Nodes: {summary['dag_nodes']}")
    print(f"  Edges: {summary['dag_edges']}")
    
    print(f"\nMemory Hierarchy:")
    print(f"  Level 0 (Register): 22 locations")
    print(f"  Level 1 (Cache): 231 lines")
    print(f"  Level 2 (Main): 10 banks")
    print(f"  Level 3 (Storage): Unlimited")
    
    print(f"\nKernel Ready: {summary['ready']}")

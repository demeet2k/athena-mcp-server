"""
ATHENA OS - 231-Gate Combinatorial Engine
==========================================
The interaction layer between 22 registers.
C(22,2) = 231 possible pairwise register interactions (gates).

Each gate defines a specific operation combining two register values.
Gates are organized by category combinations.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Callable, Optional, Set
from itertools import combinations
from .bit4 import (BIT4, BIT4Word, bit4_and, bit4_or, bit4_xor, 
                   knowledge_join, knowledge_meet, truth_join, truth_meet,
                   negation, knowledge_complement, conflation)
from .registers import RegisterID, Register, RegisterFile


# =============================================================================
# GATE TYPES
# =============================================================================

class GateType(IntEnum):
    """Types of operations a gate can perform."""
    # Logical gates
    AND = auto()       # Conjunction
    OR = auto()        # Disjunction
    XOR = auto()       # Exclusive or
    NAND = auto()      # Negated conjunction
    NOR = auto()       # Negated disjunction
    XNOR = auto()      # Equivalence
    
    # Knowledge gates
    K_JOIN = auto()    # Knowledge join (⊔ₖ)
    K_MEET = auto()    # Knowledge meet (⊓ₖ)
    
    # Truth gates
    T_JOIN = auto()    # Truth join (⊔ₜ)
    T_MEET = auto()    # Truth meet (⊓ₜ)
    
    # Transfer gates
    COPY = auto()      # Copy first to second
    SWAP = auto()      # Swap contents
    
    # Arithmetic-style gates (on collapsed values)
    ADD = auto()       # Addition (mod 2^width)
    SUB = auto()       # Subtraction
    MUL = auto()       # Multiplication (truncated)


# =============================================================================
# GATE IMPLEMENTATION
# =============================================================================

@dataclass
class Gate:
    """
    A gate connecting two registers.
    
    Gates have:
    - Unique ID (derived from register pair)
    - Source and destination registers
    - Gate type (operation)
    - Enabled/disabled status
    - Execution count
    """
    id: int
    reg_a: RegisterID
    reg_b: RegisterID
    gate_type: GateType = GateType.AND
    enabled: bool = True
    exec_count: int = 0
    
    @property
    def canonical_pair(self) -> Tuple[RegisterID, RegisterID]:
        """Return ordered pair for consistent identification."""
        return (min(self.reg_a, self.reg_b), max(self.reg_a, self.reg_b))
    
    @property
    def category_pair(self) -> Tuple[str, str]:
        """Return the category combination of this gate."""
        return (self.reg_a.category, self.reg_b.category)
    
    def execute(self, reg_file: RegisterFile) -> BIT4Word:
        """
        Execute the gate operation on register file.
        Returns the result (does not modify registers).
        """
        if not self.enabled:
            return BIT4Word(width=reg_file.width)
        
        a = reg_file.read(self.reg_a)
        b = reg_file.read(self.reg_b)
        self.exec_count += 1
        reg_file.record_interaction(self.reg_a, self.reg_b)
        
        return self._apply_operation(a, b)
    
    def execute_and_store(self, reg_file: RegisterFile, 
                          dest: RegisterID) -> bool:
        """Execute gate and store result in destination register."""
        result = self.execute(reg_file)
        return reg_file.write(dest, result)
    
    def _apply_operation(self, a: BIT4Word, b: BIT4Word) -> BIT4Word:
        """Apply the gate operation to two words."""
        width = a.width
        
        if self.gate_type == GateType.AND:
            return a & b
        elif self.gate_type == GateType.OR:
            return a | b
        elif self.gate_type == GateType.XOR:
            return a ^ b
        elif self.gate_type == GateType.NAND:
            return ~(a & b)
        elif self.gate_type == GateType.NOR:
            return ~(a | b)
        elif self.gate_type == GateType.XNOR:
            return ~(a ^ b)
        elif self.gate_type == GateType.K_JOIN:
            return BIT4Word(tuple(
                knowledge_join(x, y) for x, y in zip(a.bits, b.bits)
            ))
        elif self.gate_type == GateType.K_MEET:
            return BIT4Word(tuple(
                knowledge_meet(x, y) for x, y in zip(a.bits, b.bits)
            ))
        elif self.gate_type == GateType.T_JOIN:
            return BIT4Word(tuple(
                truth_join(x, y) for x, y in zip(a.bits, b.bits)
            ))
        elif self.gate_type == GateType.T_MEET:
            return BIT4Word(tuple(
                truth_meet(x, y) for x, y in zip(a.bits, b.bits)
            ))
        elif self.gate_type == GateType.COPY:
            return a  # Return first operand
        elif self.gate_type == GateType.SWAP:
            return b  # For swap, this returns b; caller handles the swap
        elif self.gate_type == GateType.ADD:
            # Collapse, add, re-encode
            val_a = a.collapse_all()
            val_b = b.collapse_all()
            result = (val_a + val_b) % (1 << width)
            return BIT4Word(result, width=width)
        elif self.gate_type == GateType.SUB:
            val_a = a.collapse_all()
            val_b = b.collapse_all()
            result = (val_a - val_b) % (1 << width)
            return BIT4Word(result, width=width)
        elif self.gate_type == GateType.MUL:
            val_a = a.collapse_all()
            val_b = b.collapse_all()
            result = (val_a * val_b) % (1 << width)
            return BIT4Word(result, width=width)
        else:
            raise ValueError(f"Unknown gate type: {self.gate_type}")
    
    def __str__(self) -> str:
        status = "●" if self.enabled else "○"
        return f"Gate[{self.id:3d}]{status} {self.reg_a.hebrew}↔{self.reg_b.hebrew} ({self.gate_type.name})"


# =============================================================================
# GATE MATRIX (231 Gates)
# =============================================================================

class GateMatrix:
    """
    The complete 231-gate matrix connecting 22 registers.
    
    Organized by category combinations:
    - Mother×Mother: 3 gates (elemental mixing)
    - Mother×Double: 21 gates (elemental-planetary)
    - Mother×Single: 36 gates (elemental-zodiacal)
    - Double×Double: 21 gates (planetary interactions)
    - Double×Single: 84 gates (planetary-zodiacal)
    - Single×Single: 66 gates (zodiacal interactions)
    
    Total: 3 + 21 + 36 + 21 + 84 + 66 = 231 ✓
    """
    
    def __init__(self, reg_file: RegisterFile):
        self.reg_file = reg_file
        self.gates: Dict[Tuple[RegisterID, RegisterID], Gate] = {}
        self.by_category: Dict[Tuple[str, str], List[Gate]] = {}
        self._build_gates()
    
    def _build_gates(self) -> None:
        """Build all 231 gates."""
        gate_id = 0
        
        for r1, r2 in combinations(RegisterID, 2):
            pair = (r1, r2)  # Already ordered by combinations()
            gate = Gate(id=gate_id, reg_a=r1, reg_b=r2)
            self.gates[pair] = gate
            
            # Index by category
            cat_pair = gate.category_pair
            cat_key = tuple(sorted(cat_pair))  # Normalize
            if cat_key not in self.by_category:
                self.by_category[cat_key] = []
            self.by_category[cat_key].append(gate)
            
            gate_id += 1
        
        assert gate_id == 231, f"Expected 231 gates, got {gate_id}"
    
    def get_gate(self, r1: RegisterID, r2: RegisterID) -> Gate:
        """Get the gate connecting two registers."""
        pair = (min(r1, r2), max(r1, r2))
        return self.gates[pair]
    
    def set_gate_type(self, r1: RegisterID, r2: RegisterID, 
                      gate_type: GateType) -> None:
        """Set the operation type for a specific gate."""
        self.get_gate(r1, r2).gate_type = gate_type
    
    def enable_gate(self, r1: RegisterID, r2: RegisterID) -> None:
        """Enable a gate."""
        self.get_gate(r1, r2).enabled = True
    
    def disable_gate(self, r1: RegisterID, r2: RegisterID) -> None:
        """Disable a gate."""
        self.get_gate(r1, r2).enabled = False
    
    def execute_gate(self, r1: RegisterID, r2: RegisterID) -> BIT4Word:
        """Execute a specific gate."""
        return self.get_gate(r1, r2).execute(self.reg_file)
    
    def get_category_gates(self, cat1: str, cat2: str) -> List[Gate]:
        """Get all gates between two categories."""
        key = tuple(sorted([cat1, cat2]))
        return self.by_category.get(key, [])
    
    def get_enabled_gates(self) -> List[Gate]:
        """Get all enabled gates."""
        return [g for g in self.gates.values() if g.enabled]
    
    def get_active_gates(self) -> List[Gate]:
        """Get gates that have been executed at least once."""
        return [g for g in self.gates.values() if g.exec_count > 0]
    
    def disable_category(self, cat1: str, cat2: str) -> int:
        """Disable all gates between two categories. Returns count."""
        gates = self.get_category_gates(cat1, cat2)
        for g in gates:
            g.enabled = False
        return len(gates)
    
    def enable_category(self, cat1: str, cat2: str) -> int:
        """Enable all gates between two categories. Returns count."""
        gates = self.get_category_gates(cat1, cat2)
        for g in gates:
            g.enabled = True
        return len(gates)
    
    def set_category_type(self, cat1: str, cat2: str, 
                          gate_type: GateType) -> int:
        """Set gate type for all gates between two categories."""
        gates = self.get_category_gates(cat1, cat2)
        for g in gates:
            g.gate_type = gate_type
        return len(gates)
    
    def category_summary(self) -> Dict[Tuple[str, str], int]:
        """Return count of gates by category pair."""
        return {k: len(v) for k, v in self.by_category.items()}
    
    def total_executions(self) -> int:
        """Total gate executions across all gates."""
        return sum(g.exec_count for g in self.gates.values())
    
    def most_active_gates(self, n: int = 10) -> List[Gate]:
        """Return the n most frequently executed gates."""
        return sorted(self.gates.values(), 
                     key=lambda g: g.exec_count, 
                     reverse=True)[:n]
    
    def __len__(self) -> int:
        return len(self.gates)
    
    def __str__(self) -> str:
        lines = ["Gate Matrix (231 gates):"]
        for cat_pair, count in sorted(self.category_summary().items()):
            lines.append(f"  {cat_pair[0]}×{cat_pair[1]}: {count} gates")
        enabled = len(self.get_enabled_gates())
        active = len(self.get_active_gates())
        lines.append(f"  Enabled: {enabled}/231, Active: {active}/231")
        return '\n'.join(lines)


# =============================================================================
# GATE PATTERNS (Common configurations)
# =============================================================================

class GatePattern:
    """Predefined gate configurations for common operations."""
    
    @staticmethod
    def all_and(matrix: GateMatrix) -> None:
        """Set all gates to AND operation."""
        for gate in matrix.gates.values():
            gate.gate_type = GateType.AND
    
    @staticmethod
    def all_or(matrix: GateMatrix) -> None:
        """Set all gates to OR operation."""
        for gate in matrix.gates.values():
            gate.gate_type = GateType.OR
    
    @staticmethod
    def all_xor(matrix: GateMatrix) -> None:
        """Set all gates to XOR operation."""
        for gate in matrix.gates.values():
            gate.gate_type = GateType.XOR
    
    @staticmethod
    def knowledge_network(matrix: GateMatrix) -> None:
        """Configure for knowledge propagation."""
        # Mothers use knowledge meet (find consensus)
        matrix.set_category_type("MOTHER", "MOTHER", GateType.K_MEET)
        # Mother-Double uses knowledge join (combine information)
        matrix.set_category_type("MOTHER", "DOUBLE", GateType.K_JOIN)
        # Everything else uses knowledge join
        matrix.set_category_type("MOTHER", "SINGLE", GateType.K_JOIN)
        matrix.set_category_type("DOUBLE", "DOUBLE", GateType.K_JOIN)
        matrix.set_category_type("DOUBLE", "SINGLE", GateType.K_JOIN)
        matrix.set_category_type("SINGLE", "SINGLE", GateType.K_JOIN)
    
    @staticmethod
    def truth_network(matrix: GateMatrix) -> None:
        """Configure for truth evaluation."""
        # Use truth meet for conjunction-style evaluation
        for gate in matrix.gates.values():
            gate.gate_type = GateType.T_MEET
    
    @staticmethod
    def elemental_focus(matrix: GateMatrix) -> None:
        """Enable only gates involving Mother registers."""
        for gate in matrix.gates.values():
            if gate.reg_a.category == "MOTHER" or gate.reg_b.category == "MOTHER":
                gate.enabled = True
            else:
                gate.enabled = False
    
    @staticmethod
    def planetary_focus(matrix: GateMatrix) -> None:
        """Enable only gates involving Double registers."""
        for gate in matrix.gates.values():
            if gate.reg_a.category == "DOUBLE" or gate.reg_b.category == "DOUBLE":
                gate.enabled = True
            else:
                gate.enabled = False
    
    @staticmethod
    def zodiacal_focus(matrix: GateMatrix) -> None:
        """Enable only gates involving Single registers."""
        for gate in matrix.gates.values():
            if gate.reg_a.category == "SINGLE" or gate.reg_b.category == "SINGLE":
                gate.enabled = True
            else:
                gate.enabled = False
    
    @staticmethod
    def minimal_spanning(matrix: GateMatrix) -> None:
        """Enable minimum gates for full connectivity (21 gates)."""
        # Disable all first
        for gate in matrix.gates.values():
            gate.enabled = False
        
        # Enable chain: each register connects to next
        registers = list(RegisterID)
        for i in range(len(registers) - 1):
            matrix.get_gate(registers[i], registers[i+1]).enabled = True


# =============================================================================
# GATE OPERATIONS (Higher-level functions)
# =============================================================================

def cascade_execute(matrix: GateMatrix, 
                    start_regs: List[RegisterID],
                    dest_reg: RegisterID,
                    combine_type: GateType = GateType.K_JOIN) -> BIT4Word:
    """
    Execute a cascade of gates, combining results into destination.
    
    Combines all start registers pairwise, then combines results.
    """
    if len(start_regs) < 2:
        if start_regs:
            return matrix.reg_file.read(start_regs[0])
        return BIT4Word(width=matrix.reg_file.width)
    
    # Execute first pair
    result = matrix.get_gate(start_regs[0], start_regs[1]).execute(matrix.reg_file)
    
    # Combine with remaining registers
    for i in range(2, len(start_regs)):
        # Execute gate with accumulated result
        next_val = matrix.reg_file.read(start_regs[i])
        
        # Combine based on type
        if combine_type == GateType.K_JOIN:
            result = BIT4Word(tuple(
                knowledge_join(a, b) for a, b in zip(result.bits, next_val.bits)
            ))
        elif combine_type == GateType.AND:
            result = result & next_val
        elif combine_type == GateType.OR:
            result = result | next_val
        elif combine_type == GateType.XOR:
            result = result ^ next_val
    
    # Store in destination
    matrix.reg_file.write(dest_reg, result)
    return result


def broadcast(matrix: GateMatrix, 
              source: RegisterID,
              destinations: List[RegisterID]) -> int:
    """
    Broadcast source register value to multiple destinations.
    Returns number of successful writes.
    """
    source_val = matrix.reg_file.read(source)
    success_count = 0
    
    for dest in destinations:
        if dest != source:
            if matrix.reg_file.write(dest, source_val):
                success_count += 1
                # Record interaction
                matrix.reg_file.record_interaction(source, dest)
    
    return success_count


def ring_shift(matrix: GateMatrix, 
               registers: List[RegisterID],
               direction: int = 1) -> None:
    """
    Shift values in a ring of registers.
    direction: 1 for clockwise, -1 for counter-clockwise
    """
    n = len(registers)
    if n < 2:
        return
    
    # Read all values
    values = [matrix.reg_file.read(r) for r in registers]
    
    # Write shifted
    for i, reg in enumerate(registers):
        src_idx = (i - direction) % n
        matrix.reg_file.write(reg, values[src_idx])


# =============================================================================
# VALIDATION
# =============================================================================

def validate_gate_counts() -> bool:
    """Validate the gate count breakdown."""
    from math import comb
    
    # Category counts
    n_mother = 3
    n_double = 7
    n_single = 12
    
    # Expected gate counts per category pair
    expected = {
        ("MOTHER", "MOTHER"): comb(n_mother, 2),   # 3
        ("DOUBLE", "DOUBLE"): comb(n_double, 2),   # 21
        ("SINGLE", "SINGLE"): comb(n_single, 2),   # 66
        ("MOTHER", "DOUBLE"): n_mother * n_double, # 21
        ("MOTHER", "SINGLE"): n_mother * n_single, # 36
        ("DOUBLE", "SINGLE"): n_double * n_single, # 84
    }
    
    # Verify total
    total = sum(expected.values())
    assert total == 231, f"Expected 231 gates, got {total}"
    
    # Verify breakdown
    assert expected[("MOTHER", "MOTHER")] == 3
    assert expected[("DOUBLE", "DOUBLE")] == 21
    assert expected[("SINGLE", "SINGLE")] == 66
    assert expected[("MOTHER", "DOUBLE")] == 21
    assert expected[("MOTHER", "SINGLE")] == 36
    assert expected[("DOUBLE", "SINGLE")] == 84
    
    return True


if __name__ == "__main__":
    print("Validating gate counts...")
    assert validate_gate_counts()
    print("✓ Gate count breakdown verified: 3+21+36+21+84+66 = 231")
    
    # Demo
    print("\n=== Gate Matrix Demo ===")
    rf = RegisterFile(word_width=8)
    rf.write(RegisterID.ALEPH, BIT4Word(0b10101010, width=8))
    rf.write(RegisterID.MEM, BIT4Word(0b11001100, width=8))
    rf.write(RegisterID.SHIN, BIT4Word(0b11110000, width=8))
    
    matrix = GateMatrix(rf)
    print(matrix)
    
    # Execute some gates
    print("\n--- Executing gates ---")
    gate = matrix.get_gate(RegisterID.ALEPH, RegisterID.MEM)
    gate.gate_type = GateType.AND
    result = gate.execute(rf)
    print(f"ALEPH AND MEM = {result}")
    
    gate.gate_type = GateType.XOR
    result = gate.execute(rf)
    print(f"ALEPH XOR MEM = {result}")
    
    # Knowledge network pattern
    print("\n--- Knowledge Network Pattern ---")
    GatePattern.knowledge_network(matrix)
    print(f"Mother×Mother gates: {[g.gate_type.name for g in matrix.get_category_gates('MOTHER', 'MOTHER')]}")
    
    # Category summary
    print("\n--- Category Summary ---")
    for cat, count in sorted(matrix.category_summary().items()):
        print(f"  {cat}: {count} gates")

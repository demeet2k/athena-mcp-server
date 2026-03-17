"""
ATHENA OS - 22 Primitive Instructions
=====================================
One-to-one correspondence with the 22 registers (Hebrew letters).
Each instruction encodes a fundamental operation.

Organized by letter category:
- Mother (3): Elemental operations
- Double (7): Planetary/transformational operations
- Single (12): Zodiacal/functional operations
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Callable, Any, Dict
from abc import ABC, abstractmethod

from ..core.bit4 import BIT4, BIT4Word, negation, knowledge_complement, conflation
from ..core.registers import RegisterID, RegisterFile


# =============================================================================
# INSTRUCTION OPCODES
# =============================================================================

class Opcode(IntEnum):
    """
    22 primitive opcodes corresponding to Hebrew letters.
    
    === MOTHER LETTERS (Elemental) ===
    ALEPH: Breath/Spirit - NOP/Identity
    MEM: Water/Memory - Load
    SHIN: Fire/Action - Store
    
    === DOUBLE LETTERS (Planetary) ===
    BETH: Saturn/Structure - Branch
    GIMEL: Jupiter/Growth - Add
    DALETH: Mars/Gate - Compare
    KAPH: Sun/Center - Call
    PE: Venus/Expression - Output
    RESH: Mercury/Communication - Input
    TAV: Moon/Completion - Return
    
    === SINGLE LETTERS (Zodiacal) ===
    HE: Aries/Initiative - Push
    VAV: Taurus/Connection - Pop
    ZAYIN: Gemini/Analysis - Split
    CHETH: Cancer/Protection - Guard
    TETH: Leo/Strength - Multiply
    YOD: Virgo/Precision - Divide
    LAMED: Libra/Balance - Xor
    NUN: Scorpio/Transform - Negate
    SAMEKH: Sagittarius/Support - Shift
    AYIN: Capricorn/Perception - Test
    TZADDI: Aquarius/Distribution - Scatter
    QOPH: Pisces/Recursion - Loop
    """
    # Mother letters (0-2)
    NOP = 0         # ALEPH - No operation
    LOAD = 1        # MEM - Load from memory
    STORE = 2       # SHIN - Store to memory
    
    # Double letters (3-9)
    BRANCH = 3      # BETH - Conditional branch
    ADD = 4         # GIMEL - Addition
    COMPARE = 5     # DALETH - Comparison
    CALL = 6        # KAPH - Subroutine call
    OUTPUT = 7      # PE - Output value
    INPUT = 8       # RESH - Input value
    RETURN = 9      # TAV - Return from call
    
    # Single letters (10-21)
    PUSH = 10       # HE - Push to stack
    POP = 11        # VAV - Pop from stack
    SPLIT = 12      # ZAYIN - Split word
    GUARD = 13      # CHETH - Memory guard
    MULTIPLY = 14   # TETH - Multiplication
    DIVIDE = 15     # YOD - Division
    XOR = 16        # LAMED - Exclusive or
    NEGATE = 17     # NUN - Bitwise negation
    SHIFT = 18      # SAMEKH - Bit shift
    TEST = 19       # AYIN - Bit test
    SCATTER = 20    # TZADDI - Scatter to registers
    LOOP = 21       # QOPH - Loop construct
    
    @property
    def register(self) -> RegisterID:
        """Return the corresponding register."""
        return RegisterID(self.value)
    
    @property
    def hebrew(self) -> str:
        """Return the Hebrew letter for this opcode."""
        return self.register.hebrew
    
    @property
    def category(self) -> str:
        """Return the letter category."""
        return self.register.category


# =============================================================================
# INSTRUCTION ENCODING
# =============================================================================

@dataclass
class Instruction:
    """
    A single ATHENA instruction.
    
    Format: [opcode:5][reg_a:5][reg_b:5][immediate:17]
    Total: 32 bits
    
    For BIT4 encoding, each field can contain superposition states.
    """
    opcode: Opcode
    reg_a: Optional[RegisterID] = None
    reg_b: Optional[RegisterID] = None
    immediate: int = 0
    
    def encode(self) -> int:
        """Encode instruction to 32-bit word."""
        word = self.opcode.value & 0x1F  # 5 bits
        if self.reg_a is not None:
            word |= (self.reg_a.value & 0x1F) << 5
        if self.reg_b is not None:
            word |= (self.reg_b.value & 0x1F) << 10
        word |= (self.immediate & 0x1FFFF) << 15  # 17 bits
        return word
    
    @classmethod
    def decode(cls, word: int) -> 'Instruction':
        """Decode 32-bit word to instruction."""
        opcode = Opcode(word & 0x1F)
        reg_a_val = (word >> 5) & 0x1F
        reg_b_val = (word >> 10) & 0x1F
        immediate = (word >> 15) & 0x1FFFF
        
        reg_a = RegisterID(reg_a_val) if reg_a_val < 22 else None
        reg_b = RegisterID(reg_b_val) if reg_b_val < 22 else None
        
        return cls(opcode=opcode, reg_a=reg_a, reg_b=reg_b, immediate=immediate)
    
    def encode_bit4(self, width: int = 32) -> BIT4Word:
        """Encode instruction as BIT4Word."""
        return BIT4Word(self.encode(), width=width)
    
    @classmethod
    def decode_bit4(cls, word: BIT4Word) -> 'Instruction':
        """Decode BIT4Word to instruction."""
        return cls.decode(word.collapse_all())
    
    def __str__(self) -> str:
        parts = [f"{self.opcode.name:8}"]
        if self.reg_a is not None:
            parts.append(f"r{self.reg_a.hebrew}")
        if self.reg_b is not None:
            parts.append(f"r{self.reg_b.hebrew}")
        if self.immediate != 0:
            parts.append(f"#{self.immediate}")
        return ' '.join(parts)
    
    def __repr__(self) -> str:
        return f"Instruction({self.opcode.name}, {self.reg_a}, {self.reg_b}, {self.immediate})"


# =============================================================================
# INSTRUCTION SEMANTICS
# =============================================================================

class InstructionSemantics:
    """
    Defines the operational semantics of each instruction.
    """
    
    @staticmethod
    def execute(instr: Instruction, 
                reg_file: RegisterFile,
                memory: Any = None,  # MemoryManager
                pc: int = 0,
                stack: Optional[List] = None) -> Tuple[int, bool]:
        """
        Execute an instruction.
        
        Returns: (new_pc, halt_flag)
        """
        if stack is None:
            stack = []
        
        new_pc = pc + 1
        halt = False
        
        # === MOTHER LETTERS (Elemental) ===
        
        if instr.opcode == Opcode.NOP:
            # ALEPH: No operation (but represents breath/spirit)
            pass
        
        elif instr.opcode == Opcode.LOAD:
            # MEM: Load from memory to register
            if memory and instr.reg_a:
                value = memory.read(instr.immediate)
                if value is not None:
                    if isinstance(value, (int, float)):
                        reg_file.write(instr.reg_a, BIT4Word(int(value), width=reg_file.width))
                    # Else keep existing value
        
        elif instr.opcode == Opcode.STORE:
            # SHIN: Store register to memory
            if memory and instr.reg_a:
                value = reg_file.read(instr.reg_a).collapse_all()
                memory.write(instr.immediate, value)
        
        # === DOUBLE LETTERS (Planetary) ===
        
        elif instr.opcode == Opcode.BRANCH:
            # BETH: Conditional branch
            if instr.reg_a:
                condition = reg_file.read(instr.reg_a)
                if condition.collapse_all() != 0:
                    new_pc = instr.immediate
        
        elif instr.opcode == Opcode.ADD:
            # GIMEL: Add two registers
            if instr.reg_a and instr.reg_b:
                a = reg_file.read(instr.reg_a).collapse_all()
                b = reg_file.read(instr.reg_b).collapse_all()
                result = (a + b) % (1 << reg_file.width)
                reg_file.write(instr.reg_a, BIT4Word(result, width=reg_file.width))
        
        elif instr.opcode == Opcode.COMPARE:
            # DALETH: Compare and set flags
            if instr.reg_a and instr.reg_b:
                a = reg_file.read(instr.reg_a).collapse_all()
                b = reg_file.read(instr.reg_b).collapse_all()
                # Store comparison result in reg_a
                if a == b:
                    result = 0  # Equal
                elif a < b:
                    result = 1  # Less than
                else:
                    result = 2  # Greater than
                reg_file.write(instr.reg_a, BIT4Word(result, width=reg_file.width))
        
        elif instr.opcode == Opcode.CALL:
            # KAPH: Call subroutine
            stack.append(pc + 1)  # Save return address
            new_pc = instr.immediate
        
        elif instr.opcode == Opcode.OUTPUT:
            # PE: Output register value
            if instr.reg_a:
                value = reg_file.read(instr.reg_a).collapse_all()
                print(f"OUTPUT[{instr.reg_a.hebrew}]: {value}")
        
        elif instr.opcode == Opcode.INPUT:
            # RESH: Input to register
            if instr.reg_a:
                # Simulated input - use immediate or default
                reg_file.write(instr.reg_a, BIT4Word(instr.immediate, width=reg_file.width))
        
        elif instr.opcode == Opcode.RETURN:
            # TAV: Return from subroutine
            if stack:
                new_pc = stack.pop()
            else:
                halt = True  # No return address = halt
        
        # === SINGLE LETTERS (Zodiacal) ===
        
        elif instr.opcode == Opcode.PUSH:
            # HE: Push register to stack
            if instr.reg_a:
                value = reg_file.read(instr.reg_a)
                stack.append(value)
        
        elif instr.opcode == Opcode.POP:
            # VAV: Pop stack to register
            if instr.reg_a and stack:
                value = stack.pop()
                reg_file.write(instr.reg_a, value)
        
        elif instr.opcode == Opcode.SPLIT:
            # ZAYIN: Split word into high/low parts
            if instr.reg_a and instr.reg_b:
                word = reg_file.read(instr.reg_a).collapse_all()
                half = reg_file.width // 2
                low = word & ((1 << half) - 1)
                high = word >> half
                reg_file.write(instr.reg_a, BIT4Word(low, width=reg_file.width))
                reg_file.write(instr.reg_b, BIT4Word(high, width=reg_file.width))
        
        elif instr.opcode == Opcode.GUARD:
            # CHETH: Memory guard (set protection)
            if memory and instr.reg_a:
                # Lock/unlock based on immediate
                pass  # Implementation depends on memory system
        
        elif instr.opcode == Opcode.MULTIPLY:
            # TETH: Multiply registers
            if instr.reg_a and instr.reg_b:
                a = reg_file.read(instr.reg_a).collapse_all()
                b = reg_file.read(instr.reg_b).collapse_all()
                result = (a * b) % (1 << reg_file.width)
                reg_file.write(instr.reg_a, BIT4Word(result, width=reg_file.width))
        
        elif instr.opcode == Opcode.DIVIDE:
            # YOD: Divide registers
            if instr.reg_a and instr.reg_b:
                a = reg_file.read(instr.reg_a).collapse_all()
                b = reg_file.read(instr.reg_b).collapse_all()
                if b != 0:
                    result = a // b
                else:
                    result = 0  # Division by zero yields 0
                reg_file.write(instr.reg_a, BIT4Word(result, width=reg_file.width))
        
        elif instr.opcode == Opcode.XOR:
            # LAMED: XOR registers
            if instr.reg_a and instr.reg_b:
                a = reg_file.read(instr.reg_a)
                b = reg_file.read(instr.reg_b)
                reg_file.write(instr.reg_a, a ^ b)
        
        elif instr.opcode == Opcode.NEGATE:
            # NUN: Bitwise negation
            if instr.reg_a:
                val = reg_file.read(instr.reg_a)
                reg_file.write(instr.reg_a, ~val)
        
        elif instr.opcode == Opcode.SHIFT:
            # SAMEKH: Bit shift
            if instr.reg_a:
                val = reg_file.read(instr.reg_a).collapse_all()
                shift = instr.immediate & 0x1F
                if shift > 0:
                    result = (val << shift) % (1 << reg_file.width)
                else:
                    result = val >> (-shift)
                reg_file.write(instr.reg_a, BIT4Word(result, width=reg_file.width))
        
        elif instr.opcode == Opcode.TEST:
            # AYIN: Test specific bit
            if instr.reg_a:
                val = reg_file.read(instr.reg_a).collapse_all()
                bit_pos = instr.immediate % reg_file.width
                result = 1 if (val >> bit_pos) & 1 else 0
                reg_file.write(instr.reg_a, BIT4Word(result, width=reg_file.width))
        
        elif instr.opcode == Opcode.SCATTER:
            # TZADDI: Scatter value to multiple registers
            if instr.reg_a:
                val = reg_file.read(instr.reg_a)
                # Scatter to registers specified by immediate bitmap
                bitmap = instr.immediate
                for i in range(22):
                    if (bitmap >> i) & 1:
                        reg_file.write(RegisterID(i), val)
        
        elif instr.opcode == Opcode.LOOP:
            # QOPH: Decrement and branch if non-zero
            if instr.reg_a:
                val = reg_file.read(instr.reg_a).collapse_all()
                if val > 0:
                    val -= 1
                    reg_file.write(instr.reg_a, BIT4Word(val, width=reg_file.width))
                    if val > 0:
                        new_pc = instr.immediate
        
        return (new_pc, halt)


# =============================================================================
# INSTRUCTION BUILDER (Convenience functions)
# =============================================================================

class InstructionBuilder:
    """Convenience methods for creating common instructions."""
    
    @staticmethod
    def nop() -> Instruction:
        return Instruction(Opcode.NOP)
    
    @staticmethod
    def load(dest: RegisterID, address: int) -> Instruction:
        return Instruction(Opcode.LOAD, reg_a=dest, immediate=address)
    
    @staticmethod
    def store(src: RegisterID, address: int) -> Instruction:
        return Instruction(Opcode.STORE, reg_a=src, immediate=address)
    
    @staticmethod
    def branch(condition: RegisterID, target: int) -> Instruction:
        return Instruction(Opcode.BRANCH, reg_a=condition, immediate=target)
    
    @staticmethod
    def add(dest: RegisterID, src: RegisterID) -> Instruction:
        return Instruction(Opcode.ADD, reg_a=dest, reg_b=src)
    
    @staticmethod
    def compare(a: RegisterID, b: RegisterID) -> Instruction:
        return Instruction(Opcode.COMPARE, reg_a=a, reg_b=b)
    
    @staticmethod
    def call(target: int) -> Instruction:
        return Instruction(Opcode.CALL, immediate=target)
    
    @staticmethod
    def output(src: RegisterID) -> Instruction:
        return Instruction(Opcode.OUTPUT, reg_a=src)
    
    @staticmethod
    def input(dest: RegisterID, default: int = 0) -> Instruction:
        return Instruction(Opcode.INPUT, reg_a=dest, immediate=default)
    
    @staticmethod
    def ret() -> Instruction:
        return Instruction(Opcode.RETURN)
    
    @staticmethod
    def push(src: RegisterID) -> Instruction:
        return Instruction(Opcode.PUSH, reg_a=src)
    
    @staticmethod
    def pop(dest: RegisterID) -> Instruction:
        return Instruction(Opcode.POP, reg_a=dest)
    
    @staticmethod
    def multiply(dest: RegisterID, src: RegisterID) -> Instruction:
        return Instruction(Opcode.MULTIPLY, reg_a=dest, reg_b=src)
    
    @staticmethod
    def divide(dest: RegisterID, src: RegisterID) -> Instruction:
        return Instruction(Opcode.DIVIDE, reg_a=dest, reg_b=src)
    
    @staticmethod
    def xor(dest: RegisterID, src: RegisterID) -> Instruction:
        return Instruction(Opcode.XOR, reg_a=dest, reg_b=src)
    
    @staticmethod
    def negate(dest: RegisterID) -> Instruction:
        return Instruction(Opcode.NEGATE, reg_a=dest)
    
    @staticmethod
    def shift_left(dest: RegisterID, amount: int) -> Instruction:
        return Instruction(Opcode.SHIFT, reg_a=dest, immediate=amount)
    
    @staticmethod
    def shift_right(dest: RegisterID, amount: int) -> Instruction:
        return Instruction(Opcode.SHIFT, reg_a=dest, immediate=-amount & 0x1F)
    
    @staticmethod
    def loop(counter: RegisterID, target: int) -> Instruction:
        return Instruction(Opcode.LOOP, reg_a=counter, immediate=target)


# Alias for convenience
I = InstructionBuilder


# =============================================================================
# PROGRAM REPRESENTATION
# =============================================================================

@dataclass
class Program:
    """A sequence of ATHENA instructions."""
    
    name: str
    instructions: List[Instruction] = field(default_factory=list)
    entry_point: int = 0
    
    def append(self, instr: Instruction) -> int:
        """Add instruction and return its address."""
        addr = len(self.instructions)
        self.instructions.append(instr)
        return addr
    
    def extend(self, instrs: List[Instruction]) -> None:
        """Add multiple instructions."""
        self.instructions.extend(instrs)
    
    def __len__(self) -> int:
        return len(self.instructions)
    
    def __getitem__(self, idx: int) -> Instruction:
        return self.instructions[idx]
    
    def disassemble(self) -> str:
        """Generate human-readable disassembly."""
        lines = [f"Program: {self.name}", f"Entry: {self.entry_point}", "---"]
        for i, instr in enumerate(self.instructions):
            marker = ">" if i == self.entry_point else " "
            lines.append(f"{marker}{i:04d}: {instr}")
        return '\n'.join(lines)
    
    def encode_all(self) -> List[int]:
        """Encode all instructions to integers."""
        return [instr.encode() for instr in self.instructions]


# =============================================================================
# SIMPLE EXECUTOR
# =============================================================================

class Executor:
    """Simple instruction executor for testing."""
    
    def __init__(self, reg_file: RegisterFile, memory: Any = None):
        self.reg_file = reg_file
        self.memory = memory
        self.pc = 0
        self.stack: List[Any] = []
        self.halted = False
        self.cycle_count = 0
        self.max_cycles = 10000
    
    def reset(self) -> None:
        """Reset executor state."""
        self.pc = 0
        self.stack.clear()
        self.halted = False
        self.cycle_count = 0
    
    def step(self, program: Program) -> bool:
        """Execute one instruction. Returns True if should continue."""
        if self.halted or self.pc >= len(program):
            return False
        
        instr = program[self.pc]
        new_pc, halt = InstructionSemantics.execute(
            instr, self.reg_file, self.memory, self.pc, self.stack
        )
        
        self.pc = new_pc
        self.halted = halt
        self.cycle_count += 1
        
        return not self.halted and self.pc < len(program) and self.cycle_count < self.max_cycles
    
    def run(self, program: Program, entry: int = 0) -> int:
        """Run program to completion. Returns final PC."""
        self.pc = entry
        while self.step(program):
            pass
        return self.pc


# =============================================================================
# VALIDATION
# =============================================================================

def validate_instruction_set() -> bool:
    """Validate instruction set properties."""
    # 22 opcodes
    assert len(Opcode) == 22, "Must have exactly 22 opcodes"
    
    # Each opcode corresponds to a register
    for op in Opcode:
        assert op.register.value == op.value
    
    # Category distribution: 3 + 7 + 12 = 22
    mothers = [op for op in Opcode if op.category == "MOTHER"]
    doubles = [op for op in Opcode if op.category == "DOUBLE"]
    singles = [op for op in Opcode if op.category == "SINGLE"]
    assert len(mothers) == 3
    assert len(doubles) == 7
    assert len(singles) == 12
    
    # Instruction encoding round-trip
    for op in Opcode:
        instr = Instruction(op, RegisterID.ALEPH, RegisterID.MEM, 12345)
        encoded = instr.encode()
        decoded = Instruction.decode(encoded)
        assert decoded.opcode == instr.opcode
        assert decoded.reg_a == instr.reg_a
        assert decoded.reg_b == instr.reg_b
        assert decoded.immediate == instr.immediate
    
    return True


if __name__ == "__main__":
    print("Validating instruction set...")
    assert validate_instruction_set()
    print("✓ 22 instructions validated")
    
    # Demo program
    print("\n=== Demo Program ===")
    prog = Program("factorial")
    
    # Simple loop: compute sum 1+2+...+n
    prog.extend([
        I.input(RegisterID.ALEPH, 5),       # 0: n = 5
        I.input(RegisterID.MEM, 0),         # 1: sum = 0
        I.add(RegisterID.MEM, RegisterID.ALEPH),  # 2: sum += n
        I.loop(RegisterID.ALEPH, 2),        # 3: n--; if n>0 goto 2
        I.output(RegisterID.MEM),           # 4: output sum
        I.ret(),                            # 5: halt
    ])
    
    print(prog.disassemble())
    
    # Execute
    print("\n=== Execution ===")
    rf = RegisterFile(word_width=32)
    executor = Executor(rf)
    final_pc = executor.run(prog)
    print(f"Final PC: {final_pc}, Cycles: {executor.cycle_count}")

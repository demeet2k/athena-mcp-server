"""
ATHENA OS - 22-Register Architecture
====================================
Derived from tetractys geometry (1+2+3+4=10) extended to 22 Hebrew letters.
Each register has semantic significance and specific operational roles.

The 22 registers interact through 231 gates: C(22,2) = 231 pairwise connections.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from .bit4 import BIT4, BIT4Word, SemanticState, negation, knowledge_complement, conflation


# =============================================================================
# REGISTER IDENTIFIERS (22 Hebrew Letter Correspondences)
# =============================================================================

class RegisterID(IntEnum):
    """
    22 Registers corresponding to the 22 Hebrew letters.
    Organized by tetractys levels and elemental associations.
    """
    # === MOTHER LETTERS (3) - Elemental Principles ===
    ALEPH = 0    # א - Air/Breath - Spirit register
    MEM = 1      # מ - Water - Memory/State register
    SHIN = 2     # ש - Fire - Action/Transform register
    
    # === DOUBLE LETTERS (7) - Planetary Operations ===
    BETH = 3     # ב - Saturn - Structure/Container
    GIMEL = 4    # ג - Jupiter - Expansion/Growth
    DALETH = 5   # ד - Mars - Division/Gate
    KAPH = 6     # כ - Sun - Central coordination
    PE = 7       # פ - Venus - Expression/Output
    RESH = 8     # ר - Mercury - Communication/Link
    TAV = 9      # ת - Moon - Completion/Cycle
    
    # === SINGLE LETTERS (12) - Zodiacal Functions ===
    HE = 10      # ה - Aries - Initiative
    VAV = 11     # ו - Taurus - Connection
    ZAYIN = 12   # ז - Gemini - Analysis
    CHETH = 13   # ח - Cancer - Protection
    TETH = 14    # ט - Leo - Strength
    YOD = 15     # י - Virgo - Precision
    LAMED = 16   # ל - Libra - Balance
    NUN = 17     # נ - Scorpio - Transformation
    SAMEKH = 18  # ס - Sagittarius - Support
    AYIN = 19    # ע - Capricorn - Perception
    TZADDI = 20  # צ - Aquarius - Distribution
    QOPH = 21    # ק - Pisces - Recursion/Dreams
    
    @property
    def hebrew(self) -> str:
        """Return the Hebrew letter for this register."""
        return "אמשבגדכפרתהוזחטילנסעצק"[self.value]
    
    @property
    def category(self) -> str:
        """Return the category (Mother/Double/Single)."""
        if self.value < 3:
            return "MOTHER"
        elif self.value < 10:
            return "DOUBLE"
        else:
            return "SINGLE"
    
    @property
    def element(self) -> Optional[str]:
        """Return elemental association for Mother letters."""
        if self == RegisterID.ALEPH:
            return "AIR"
        elif self == RegisterID.MEM:
            return "WATER"
        elif self == RegisterID.SHIN:
            return "FIRE"
        return None


# =============================================================================
# REGISTER CLASS
# =============================================================================

@dataclass
class Register:
    """
    A single ATHENA register holding a BIT4Word.
    
    Registers have:
    - Identity (RegisterID)
    - Content (BIT4Word)
    - Semantic state
    - Lock status
    - Access history
    """
    id: RegisterID
    content: BIT4Word = field(default_factory=lambda: BIT4Word(width=32))
    state: SemanticState = SemanticState.STABLE
    locked: bool = False
    access_count: int = 0
    modified_count: int = 0
    
    def read(self) -> BIT4Word:
        """Read register contents (non-destructive)."""
        self.access_count += 1
        return self.content
    
    def write(self, value: BIT4Word) -> bool:
        """Write to register. Returns False if locked."""
        if self.locked:
            return False
        self.content = value
        self.modified_count += 1
        self.state = SemanticState.FLUID
        return True
    
    def clear(self) -> bool:
        """Clear register to all UNKNOWN."""
        if self.locked:
            return False
        self.content = BIT4Word(width=self.content.width)
        self.state = SemanticState.STABLE
        return True
    
    def lock(self) -> None:
        """Lock register (prevent writes)."""
        self.locked = True
    
    def unlock(self) -> None:
        """Unlock register."""
        self.locked = False
    
    def apply_operator(self, op: Callable[[BIT4], BIT4]) -> bool:
        """Apply a BIT4 operator to all bits in register."""
        if self.locked:
            return False
        self.content = self.content.apply_gate(op)
        self.modified_count += 1
        return True
    
    def negate(self) -> bool:
        """Apply negation operator."""
        return self.apply_operator(negation)
    
    def complement_knowledge(self) -> bool:
        """Apply knowledge complement operator."""
        return self.apply_operator(knowledge_complement)
    
    def conflate(self) -> bool:
        """Apply conflation operator."""
        return self.apply_operator(conflation)
    
    @property
    def is_definite(self) -> bool:
        """Check if all bits are definite (0 or 1)."""
        return self.content.knowledge_definite()
    
    @property
    def superposition_bits(self) -> int:
        """Count bits in superposition state."""
        return self.content.superposition_count()
    
    def __str__(self) -> str:
        status = "??" if self.locked else "  "
        return f"R[{self.id.hebrew}]{status} = {self.content}"


# =============================================================================
# REGISTER FILE (All 22 Registers)
# =============================================================================

class RegisterFile:
    """
    The complete set of 22 ATHENA registers.
    
    Provides indexed access and bulk operations.
    Tracks register interactions for gate computation.
    """
    
    def __init__(self, word_width: int = 32):
        self.width = word_width
        self.registers: Dict[RegisterID, Register] = {
            rid: Register(id=rid, content=BIT4Word(width=word_width))
            for rid in RegisterID
        }
        self.interaction_count: Dict[Tuple[RegisterID, RegisterID], int] = {}
    
    def __getitem__(self, rid: RegisterID) -> Register:
        return self.registers[rid]
    
    def __setitem__(self, rid: RegisterID, value: BIT4Word) -> None:
        self.registers[rid].write(value)
    
    def read(self, rid: RegisterID) -> BIT4Word:
        """Read from register by ID."""
        return self.registers[rid].read()
    
    def write(self, rid: RegisterID, value: BIT4Word) -> bool:
        """Write to register by ID."""
        return self.registers[rid].write(value)
    
    def get_mothers(self) -> List[Register]:
        """Get the three Mother registers."""
        return [self.registers[rid] for rid in RegisterID if rid.category == "MOTHER"]
    
    def get_doubles(self) -> List[Register]:
        """Get the seven Double registers."""
        return [self.registers[rid] for rid in RegisterID if rid.category == "DOUBLE"]
    
    def get_singles(self) -> List[Register]:
        """Get the twelve Single registers."""
        return [self.registers[rid] for rid in RegisterID if rid.category == "SINGLE"]
    
    def record_interaction(self, r1: RegisterID, r2: RegisterID) -> None:
        """Record an interaction between two registers (for gate counting)."""
        key = (min(r1, r2), max(r1, r2))  # Canonical ordering
        self.interaction_count[key] = self.interaction_count.get(key, 0) + 1
    
    def get_active_gates(self) -> int:
        """Return number of register pairs that have interacted."""
        return len(self.interaction_count)
    
    def get_total_gates(self) -> int:
        """Return total possible gates: C(22,2) = 231."""
        return 231  # 22 choose 2
    
    def bulk_read(self, rids: List[RegisterID]) -> Dict[RegisterID, BIT4Word]:
        """Read multiple registers at once."""
        return {rid: self.read(rid) for rid in rids}
    
    def bulk_write(self, values: Dict[RegisterID, BIT4Word]) -> Dict[RegisterID, bool]:
        """Write to multiple registers at once."""
        return {rid: self.write(rid, val) for rid, val in values.items()}
    
    def clear_all(self) -> None:
        """Clear all registers to UNKNOWN state."""
        for reg in self.registers.values():
            if not reg.locked:
                reg.clear()
    
    def lock_mothers(self) -> None:
        """Lock the three Mother registers (elemental constants)."""
        for reg in self.get_mothers():
            reg.lock()
    
    def snapshot(self) -> Dict[RegisterID, Tuple[str, SemanticState]]:
        """Take a snapshot of all register states."""
        return {
            rid: (str(reg.content), reg.state)
            for rid, reg in self.registers.items()
        }
    
    def restore(self, snapshot: Dict[RegisterID, Tuple[str, SemanticState]]) -> None:
        """Restore registers from a snapshot (for unlocked registers only)."""
        for rid, (content_str, state) in snapshot.items():
            reg = self.registers[rid]
            if not reg.locked:
                # Parse content string back to BIT4Word
                bits = []
                for c in reversed(content_str):
                    if c == '⊥':
                        bits.append(BIT4.UNKNOWN)
                    elif c == '0':
                        bits.append(BIT4.FALSE)
                    elif c == '1':
                        bits.append(BIT4.TRUE)
                    elif c == '⊤':
                        bits.append(BIT4.BOTH)
                reg.content = BIT4Word(tuple(bits))
                reg.state = state
    
    def dump(self) -> str:
        """Generate a formatted dump of all registers."""
        lines = ["=" * 60, "ATHENA REGISTER FILE DUMP", "=" * 60]
        
        lines.append("\n--- MOTHER LETTERS (Elemental) ---")
        for reg in self.get_mothers():
            lines.append(f"  {reg}")
        
        lines.append("\n--- DOUBLE LETTERS (Planetary) ---")
        for reg in self.get_doubles():
            lines.append(f"  {reg}")
        
        lines.append("\n--- SINGLE LETTERS (Zodiacal) ---")
        for reg in self.get_singles():
            lines.append(f"  {reg}")
        
        lines.append(f"\nActive Gates: {self.get_active_gates()}/{self.get_total_gates()}")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        return f"RegisterFile(22 registers, {self.get_active_gates()} active gates)"


# =============================================================================
# TETRACTYS STRUCTURE
# =============================================================================

class Tetractys:
    """
    The Pythagorean Tetractys: 1+2+3+4 = 10
    
    Maps to the 10-node processing DAG derived from register hierarchy.
    
          ●           (1) - Unity/Source
         ● ●          (2) - Duality/Polarity  
        ● ● ●         (3) - Trinity/Process
       ● ● ● ●        (4) - Quaternary/Manifestation
    """
    
    LEVELS = [1, 2, 3, 4]
    TOTAL = 10
    
    @staticmethod
    def level_nodes(level: int) -> int:
        """Number of nodes at a given level (1-indexed)."""
        assert 1 <= level <= 4
        return level
    
    @staticmethod
    def node_to_level(node: int) -> int:
        """Get the level (1-4) for a given node index (0-9)."""
        assert 0 <= node < 10
        if node < 1:
            return 1
        elif node < 3:
            return 2
        elif node < 6:
            return 3
        else:
            return 4
    
    @staticmethod
    def level_to_nodes(level: int) -> List[int]:
        """Get node indices for a given level."""
        starts = [0, 1, 3, 6]
        ends = [1, 3, 6, 10]
        return list(range(starts[level-1], ends[level-1]))
    
    @staticmethod
    def get_parent_nodes(node: int) -> List[int]:
        """Get parent nodes in the DAG (nodes in level above)."""
        level = Tetractys.node_to_level(node)
        if level == 1:
            return []  # Top node has no parents
        return Tetractys.level_to_nodes(level - 1)
    
    @staticmethod
    def get_child_nodes(node: int) -> List[int]:
        """Get child nodes in the DAG (nodes in level below)."""
        level = Tetractys.node_to_level(node)
        if level == 4:
            return []  # Bottom level has no children
        return Tetractys.level_to_nodes(level + 1)
    
    @staticmethod
    def harmonic_ratio(level: int) -> Tuple[int, int]:
        """Get the harmonic ratio for each level."""
        ratios = {
            1: (1, 1),  # Unison
            2: (2, 1),  # Octave
            3: (3, 2),  # Fifth
            4: (4, 3),  # Fourth
        }
        return ratios[level]


# =============================================================================
# PROCESSING DAG (10-Node Hierarchy)
# =============================================================================

@dataclass
class DAGNode:
    """A node in the 10-node processing DAG."""
    id: int
    level: int
    name: str
    registers: List[RegisterID]  # Registers assigned to this node
    state: BIT4 = BIT4.UNKNOWN
    
    def process(self, reg_file: RegisterFile) -> BIT4:
        """Process all assigned registers and return combined state."""
        if not self.registers:
            return BIT4.UNKNOWN
        
        # Combine states from all assigned registers
        combined = BIT4.UNKNOWN
        for rid in self.registers:
            reg = reg_file[rid]
            # Get "truth tendency" of register
            if reg.content.knowledge_definite():
                val = reg.content.collapse_all()
                reg_state = BIT4.TRUE if val > 0 else BIT4.FALSE
            else:
                reg_state = BIT4.BOTH if reg.superposition_bits > 0 else BIT4.UNKNOWN
            
            # Knowledge join to combine
            from .bit4 import knowledge_join
            combined = knowledge_join(combined, reg_state)
        
        self.state = combined
        return combined


class ProcessingDAG:
    """
    The 10-node processing DAG derived from tetractys geometry.
    
    Level 1 (1 node):  Unity - Central coordinator
    Level 2 (2 nodes): Duality - Analysis/Synthesis
    Level 3 (3 nodes): Trinity - Transform/Store/Execute
    Level 4 (4 nodes): Quaternary - Input/Output/Compute/Memory
    """
    
    NODE_NAMES = [
        "Unity",                          # Level 1
        "Analysis", "Synthesis",          # Level 2
        "Transform", "Store", "Execute",  # Level 3
        "Input", "Output", "Compute", "Memory"  # Level 4
    ]
    
    def __init__(self, reg_file: RegisterFile):
        self.reg_file = reg_file
        self.nodes: List[DAGNode] = []
        self._build_dag()
    
    def _build_dag(self) -> None:
        """Build the 10-node DAG with register assignments."""
        # Assign registers to nodes based on category
        # Mother letters → Level 1 (Unity coordinator)
        # Double letters → Levels 2-3 (Operations)
        # Single letters → Level 4 (I/O and computation)
        
        assignments = [
            [RegisterID.ALEPH, RegisterID.MEM, RegisterID.SHIN],  # Unity
            [RegisterID.BETH, RegisterID.GIMEL],                  # Analysis
            [RegisterID.DALETH, RegisterID.KAPH],                 # Synthesis
            [RegisterID.PE, RegisterID.RESH],                     # Transform
            [RegisterID.TAV],                                     # Store
            [RegisterID.HE, RegisterID.VAV],                      # Execute
            [RegisterID.ZAYIN, RegisterID.CHETH, RegisterID.TETH],  # Input
            [RegisterID.YOD, RegisterID.LAMED, RegisterID.NUN],     # Output
            [RegisterID.SAMEKH, RegisterID.AYIN, RegisterID.TZADDI],  # Compute
            [RegisterID.QOPH],                                       # Memory
        ]
        
        for i, name in enumerate(self.NODE_NAMES):
            level = Tetractys.node_to_level(i)
            self.nodes.append(DAGNode(
                id=i,
                level=level,
                name=name,
                registers=assignments[i]
            ))
    
    def process_level(self, level: int) -> List[BIT4]:
        """Process all nodes at a given level."""
        node_ids = Tetractys.level_to_nodes(level)
        return [self.nodes[i].process(self.reg_file) for i in node_ids]
    
    def process_all(self) -> Dict[str, BIT4]:
        """Process entire DAG bottom-up, return all node states."""
        # Process from level 4 up to level 1
        for level in [4, 3, 2, 1]:
            self.process_level(level)
        
        return {node.name: node.state for node in self.nodes}
    
    def get_node(self, name: str) -> Optional[DAGNode]:
        """Get node by name."""
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def __str__(self) -> str:
        lines = ["Processing DAG (Tetractys):"]
        for level in [1, 2, 3, 4]:
            indent = "  " * (4 - level)
            nodes = [self.nodes[i] for i in Tetractys.level_to_nodes(level)]
            node_strs = [f"{n.name}({n.state.symbol})" for n in nodes]
            lines.append(f"{indent}{' '.join(node_strs)}")
        return '\n'.join(lines)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_architecture() -> bool:
    """Validate architectural constants."""
    # 22 registers
    assert len(RegisterID) == 22, "Must have exactly 22 registers"
    
    # Category counts: 3 + 7 + 12 = 22
    mothers = [r for r in RegisterID if r.category == "MOTHER"]
    doubles = [r for r in RegisterID if r.category == "DOUBLE"]
    singles = [r for r in RegisterID if r.category == "SINGLE"]
    assert len(mothers) == 3, "Must have 3 Mother letters"
    assert len(doubles) == 7, "Must have 7 Double letters"
    assert len(singles) == 12, "Must have 12 Single letters"
    
    # 231 gates: C(22,2)
    from math import comb
    assert comb(22, 2) == 231, "Gate count must be 231"
    
    # Tetractys sums to 10
    assert sum(Tetractys.LEVELS) == 10, "Tetractys must sum to 10"
    
    return True


if __name__ == "__main__":
    print("Validating architecture...")
    assert validate_architecture()
    print("✓ Architecture validated: 22 registers, 231 gates, 10-node DAG")
    
    # Demo
    print("\n=== Register Demo ===")
    rf = RegisterFile(word_width=8)
    
    # Write some values
    rf.write(RegisterID.ALEPH, BIT4Word(42, width=8))
    rf.write(RegisterID.MEM, BIT4Word(137, width=8))
    rf.write(RegisterID.SHIN, BIT4Word(255, width=8))
    
    # Lock mother registers
    rf.lock_mothers()
    
    print(rf.dump())
    
    # Process through DAG
    print("\n=== Processing DAG ===")
    dag = ProcessingDAG(rf)
    results = dag.process_all()
    print(dag)
    print("\nNode states:", {k: v.symbol for k, v in results.items()})

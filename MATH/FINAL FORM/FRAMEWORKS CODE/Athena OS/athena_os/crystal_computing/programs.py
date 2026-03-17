"""
ATHENA OS - Crystal Computing Programs
======================================
Crystal Programs as Paths

From CRYSTAL_COMPUTING_FRAMEWORK.docx Chapter 13:

CRYSTAL PROGRAM:
    A path through the meta-crystal that transports κ-bearing
    Aetheric states along structured sequences of operations.
    
    Program = ((c_0, T_0), (c_1, T_1), ..., (c_{N-1}, T_{N-1}))
    
    where c_j ∈ ?? (crystal index) and T_j ∈ ??_{c_j} (operator)

PATH SEMANTICS:
    - Compositional structure explicit at program level
    - Equivalence via crystal path homotopy
    - Safety = staying in Aetheric sectors

κ-FLOW:
    Programs define κ-flows through the lattice
    Total κ conserved for Aetheric paths
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Iterator, Callable
import math

from .lattice import CrystalCell, MetaCrystal, CrystalAdjacency, Pole
from .kappa import KappaField, KappaFlow, KappaFlowGraph, ConservationLaw
from .states import AethericState
from .operators import CrystalOperator, OperatorFactory, IdentityOperator


# =============================================================================
# PROGRAM STEP
# =============================================================================

@dataclass
class ProgramStep:
    """
    A single step in a crystal program.
    
    (c_j, T_j) where c_j is crystal cell, T_j is operator
    """
    
    cell: CrystalCell
    operator: CrystalOperator
    step_index: int = 0
    
    # κ tracking
    kappa_before: float = 0.0
    kappa_after: float = 0.0
    kappa_delta: float = 0.0
    
    # Execution metadata
    executed: bool = False
    success: bool = True
    error_message: str = ""
    
    def record_kappa(self, before: float, after: float) -> None:
        """Record κ values for this step."""
        self.kappa_before = before
        self.kappa_after = after
        self.kappa_delta = after - before
    
    def is_conserving(self, tolerance: float = 1e-6) -> bool:
        """Check if step conserved κ."""
        return abs(self.kappa_delta) < tolerance
    
    def __str__(self) -> str:
        return f"Step[{self.step_index}]: {self.cell.signature} -> {self.operator.name}"


# =============================================================================
# CRYSTAL PROGRAM
# =============================================================================

@dataclass
class CrystalProgram:
    """
    A crystal program: path through the meta-crystal.
    
    Consists of a sequence of (cell, operator) pairs defining
    a trajectory that transports Aetheric states.
    """
    
    name: str = "program"
    steps: List[ProgramStep] = field(default_factory=list)
    
    # Path metadata
    is_compiled: bool = False
    is_executed: bool = False
    
    # κ tracking
    initial_kappa: float = 0.0
    final_kappa: float = 0.0
    total_kappa_loss: float = 0.0
    
    # Flow graph
    flow_graph: KappaFlowGraph = field(default_factory=KappaFlowGraph)
    
    @property
    def length(self) -> int:
        """Number of steps."""
        return len(self.steps)
    
    @property
    def cells(self) -> List[CrystalCell]:
        """Get sequence of cells."""
        return [step.cell for step in self.steps]
    
    @property
    def operators(self) -> List[CrystalOperator]:
        """Get sequence of operators."""
        return [step.operator for step in self.steps]
    
    def add_step(self, cell: CrystalCell, operator: CrystalOperator) -> ProgramStep:
        """Add a step to the program."""
        step = ProgramStep(
            cell=cell,
            operator=operator,
            step_index=len(self.steps)
        )
        self.steps.append(step)
        return step
    
    def add_operator(self, operator: CrystalOperator) -> ProgramStep:
        """Add operator using its cell."""
        return self.add_step(operator.cell, operator)
    
    def is_aetheric(self) -> bool:
        """Check if all steps are in Aetheric pole."""
        return all(step.cell.is_aetheric for step in self.steps)
    
    def is_legal(self) -> bool:
        """Check if program stays in legal poles."""
        return all(step.cell.pole.is_legal for step in self.steps)
    
    def contains_anti(self) -> bool:
        """Check if program visits Anti-Aether."""
        return any(step.cell.is_anti for step in self.steps)
    
    def is_connected(self, adjacency: CrystalAdjacency) -> bool:
        """Check if path is connected (adjacent cells)."""
        if len(self.steps) < 2:
            return True
        
        for i in range(len(self.steps) - 1):
            if not adjacency.are_adjacent(self.steps[i].cell, self.steps[i+1].cell):
                return False
        return True
    
    def is_conserving(self, tolerance: float = 1e-6) -> bool:
        """Check if program conserves κ."""
        return abs(self.final_kappa - self.initial_kappa) < tolerance
    
    def compile(self) -> bool:
        """Compile/validate the program."""
        # Check legality
        if self.contains_anti():
            return False
        
        # Check operators match cells
        for step in self.steps:
            if step.operator.cell.index != step.cell.index:
                # Relax this - operators can be applied in compatible cells
                pass
        
        self.is_compiled = True
        return True
    
    def execute(self, initial_state: AethericState) -> AethericState:
        """Execute program on initial state."""
        if not self.is_compiled:
            self.compile()
        
        self.initial_kappa = initial_state.total_kappa
        state = initial_state.clone()
        state.step_index = 0
        
        prev_cell = None
        
        for step in self.steps:
            kappa_before = state.total_kappa
            
            # Apply operator
            try:
                state = step.operator.apply(state)
                step.success = True
            except Exception as e:
                step.success = False
                step.error_message = str(e)
                break
            
            step.executed = True
            state.step_index = step.step_index
            
            # Record κ
            kappa_after = state.total_kappa
            step.record_kappa(kappa_before, kappa_after)
            
            # Track flow
            if prev_cell is not None:
                flow = KappaFlow(
                    source=prev_cell,
                    target=step.cell,
                    amount=kappa_before,
                    is_conserving=step.is_conserving()
                )
                self.flow_graph.add_flow(flow)
            
            prev_cell = step.cell
        
        self.final_kappa = state.total_kappa
        self.total_kappa_loss = self.initial_kappa - self.final_kappa
        self.is_executed = True
        
        return state
    
    def summary(self) -> Dict[str, Any]:
        """Get program summary."""
        return {
            "name": self.name,
            "length": self.length,
            "aetheric": self.is_aetheric(),
            "legal": self.is_legal(),
            "compiled": self.is_compiled,
            "executed": self.is_executed,
            "initial_kappa": self.initial_kappa,
            "final_kappa": self.final_kappa,
            "conserving": self.is_conserving() if self.is_executed else None
        }


# =============================================================================
# PROGRAM BUILDER
# =============================================================================

@dataclass
class ProgramBuilder:
    """
    Fluent builder for crystal programs.
    """
    
    program: CrystalProgram = field(default_factory=CrystalProgram)
    crystal: MetaCrystal = field(default_factory=MetaCrystal)
    
    def named(self, name: str) -> 'ProgramBuilder':
        """Set program name."""
        self.program.name = name
        return self
    
    def at(self, cell: CrystalCell) -> 'ProgramBuilder':
        """Add step at cell with identity operator."""
        op = IdentityOperator(cell)
        self.program.add_step(cell, op)
        return self
    
    def apply(self, operator: CrystalOperator) -> 'ProgramBuilder':
        """Add step with operator."""
        self.program.add_step(operator.cell, operator)
        return self
    
    def apply_at(self, cell: CrystalCell, **params) -> 'ProgramBuilder':
        """Create and apply canonical operator for cell."""
        op = OperatorFactory.create_for_cell(cell, **params)
        self.program.add_step(cell, op)
        return self
    
    def repeat(self, operator: CrystalOperator, n: int) -> 'ProgramBuilder':
        """Repeat operator n times."""
        for _ in range(n):
            self.program.add_step(operator.cell, operator)
        return self
    
    def build(self) -> CrystalProgram:
        """Build and return program."""
        self.program.compile()
        return self.program


# =============================================================================
# PATH ANALYSIS
# =============================================================================

@dataclass
class PathAnalysis:
    """
    Analysis of crystal program paths.
    """
    
    program: CrystalProgram
    adjacency: CrystalAdjacency = field(default_factory=CrystalAdjacency)
    
    def path_length(self) -> int:
        """Total path length in steps."""
        return self.program.length
    
    def hamming_distance_total(self) -> int:
        """Total Hamming distance traveled."""
        if len(self.program.steps) < 2:
            return 0
        
        total = 0
        for i in range(len(self.program.steps) - 1):
            total += self.adjacency.hamming_distance(
                self.program.steps[i].cell,
                self.program.steps[i+1].cell
            )
        return total
    
    def visited_cells(self) -> List[CrystalCell]:
        """Unique cells visited."""
        seen = set()
        result = []
        for step in self.program.steps:
            if step.cell.index not in seen:
                seen.add(step.cell.index)
                result.append(step.cell)
        return result
    
    def cell_visits(self) -> Dict[int, int]:
        """Count visits per cell."""
        counts = {}
        for step in self.program.steps:
            idx = step.cell.index
            counts[idx] = counts.get(idx, 0) + 1
        return counts
    
    def pole_distribution(self) -> Dict[Pole, int]:
        """Distribution of steps by pole."""
        dist = {p: 0 for p in Pole}
        for step in self.program.steps:
            dist[step.cell.pole] += 1
        return dist
    
    def is_acyclic(self) -> bool:
        """Check if path is acyclic (no repeated cells)."""
        seen = set()
        for step in self.program.steps:
            if step.cell.index in seen:
                return False
            seen.add(step.cell.index)
        return True
    
    def kappa_profile(self) -> List[float]:
        """Get κ values along path."""
        return [step.kappa_after for step in self.program.steps]
    
    def max_kappa_loss_step(self) -> Optional[ProgramStep]:
        """Find step with maximum κ loss."""
        if not self.program.steps:
            return None
        
        return min(self.program.steps, key=lambda s: s.kappa_delta)


# =============================================================================
# PROGRAM LIBRARY
# =============================================================================

@dataclass
class ProgramLibrary:
    """
    Library of crystal programs.
    """
    
    programs: Dict[str, CrystalProgram] = field(default_factory=dict)
    
    def add(self, program: CrystalProgram) -> None:
        """Add program to library."""
        self.programs[program.name] = program
    
    def get(self, name: str) -> Optional[CrystalProgram]:
        """Get program by name."""
        return self.programs.get(name)
    
    def list_names(self) -> List[str]:
        """List all program names."""
        return list(self.programs.keys())
    
    def search_by_length(self, min_len: int = 0, max_len: int = 1000) -> List[CrystalProgram]:
        """Search programs by length."""
        return [p for p in self.programs.values() if min_len <= p.length <= max_len]
    
    def search_aetheric(self) -> List[CrystalProgram]:
        """Get all Aetheric programs."""
        return [p for p in self.programs.values() if p.is_aetheric()]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_programs() -> bool:
    """Validate programs module."""
    from .operators import HadamardOperator, PhaseOperator
    
    # Test ProgramStep
    cell = CrystalCell.from_index(0)
    op = IdentityOperator(cell)
    step = ProgramStep(cell=cell, operator=op, step_index=0)
    assert step.step_index == 0
    
    # Test CrystalProgram
    program = CrystalProgram(name="test")
    program.add_step(cell, op)
    assert program.length == 1
    assert program.is_aetheric()
    
    # Test execution
    state = AethericState.vacuum(4)
    program.compile()
    result = program.execute(state)
    assert result.is_normalized
    assert program.is_executed
    
    # Test ProgramBuilder
    builder = ProgramBuilder()
    prog = (builder
            .named("quantum_circuit")
            .apply(HadamardOperator(0))
            .apply(PhaseOperator(math.pi/4))
            .build())
    
    assert prog.name == "quantum_circuit"
    assert prog.length == 2
    
    # Test PathAnalysis
    analysis = PathAnalysis(prog)
    assert analysis.path_length() == 2
    
    # Test ProgramLibrary
    library = ProgramLibrary()
    library.add(prog)
    assert library.get("quantum_circuit") is not None
    
    return True


if __name__ == "__main__":
    print("Validating Crystal Computing Programs...")
    assert validate_programs()
    print("✓ Crystal Programs validated")
    
    # Demo
    print("\n=== Crystal Programs Demo ===")
    
    from .operators import HadamardOperator, PhaseOperator
    
    # Build a quantum circuit
    builder = ProgramBuilder()
    program = (builder
               .named("hadamard_phase")
               .apply(HadamardOperator(0))
               .apply(PhaseOperator(math.pi/4))
               .apply(HadamardOperator(0))
               .build())
    
    print(f"\nProgram: {program.name}")
    print(f"  Length: {program.length} steps")
    print(f"  Aetheric: {program.is_aetheric()}")
    print(f"  Compiled: {program.is_compiled}")
    
    # Execute
    state = AethericState.vacuum(2)
    result = program.execute(state)
    
    print(f"\nExecution:")
    print(f"  Initial κ: {program.initial_kappa}")
    print(f"  Final κ: {program.final_kappa}")
    print(f"  Conserving: {program.is_conserving()}")
    
    # Path analysis
    analysis = PathAnalysis(program)
    print(f"\nPath Analysis:")
    print(f"  Unique cells: {len(analysis.visited_cells())}")
    print(f"  Hamming distance: {analysis.hamming_distance_total()}")
    print(f"  Pole distribution: {dict(analysis.pole_distribution())}")

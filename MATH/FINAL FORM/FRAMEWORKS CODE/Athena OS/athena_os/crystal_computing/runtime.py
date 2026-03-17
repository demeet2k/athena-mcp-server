"""
ATHENA OS - Crystal Computing Runtime
=====================================
Runtime Architecture

From CRYSTAL_COMPUTING_FRAMEWORK.docx Chapter 19:

RUNTIME ARCHITECTURE:
    - State management
    - Operator dispatch
    - κ-budget tracking
    - Substrate backends

SUBSTRATE BACKENDS:
    - Vector/Quantum (QHC)
    - Graph
    - PDE/Mesh
    - Agent

META-LEARNING:
    - Program space parametrization
    - Performance evaluation
    - Meta-update rules
    - Regularization
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Iterator
from abc import ABC, abstractmethod
import time
import math

from .lattice import CrystalCell, MetaCrystal, Constant, Shape, Element, Level, Pole
from .kappa import KappaField, KappaBudget, ConservationLaw, Texture
from .states import AethericState, Geometry, GeometryType
from .operators import CrystalOperator, OperatorRegistry, OperatorFactory
from .programs import CrystalProgram, ProgramStep, PathAnalysis


# =============================================================================
# SUBSTRATE BACKEND
# =============================================================================

class SubstrateBackend(ABC):
    """
    Abstract substrate backend for crystal operations.
    """
    
    @abstractmethod
    def name(self) -> str:
        """Backend name."""
        pass
    
    @abstractmethod
    def supports_geometry(self, geo_type: GeometryType) -> bool:
        """Check if backend supports geometry type."""
        pass
    
    @abstractmethod
    def apply_operator(self, state: AethericState, 
                       operator: CrystalOperator) -> AethericState:
        """Apply operator using backend."""
        pass


class VectorBackend(SubstrateBackend):
    """
    Vector/quantum substrate backend.
    """
    
    def name(self) -> str:
        return "vector"
    
    def supports_geometry(self, geo_type: GeometryType) -> bool:
        return geo_type == GeometryType.VECTOR
    
    def apply_operator(self, state: AethericState,
                       operator: CrystalOperator) -> AethericState:
        """Apply operator to vector state."""
        return operator.apply(state)


class GraphBackend(SubstrateBackend):
    """
    Graph substrate backend.
    """
    
    def name(self) -> str:
        return "graph"
    
    def supports_geometry(self, geo_type: GeometryType) -> bool:
        return geo_type == GeometryType.GRAPH
    
    def apply_operator(self, state: AethericState,
                       operator: CrystalOperator) -> AethericState:
        """Apply operator to graph state."""
        # Graph-specific implementation would go here
        return operator.apply(state)


# =============================================================================
# EXECUTION CONTEXT
# =============================================================================

@dataclass
class ExecutionContext:
    """
    Context for program execution.
    """
    
    # State
    current_state: Optional[AethericState] = None
    state_history: List[AethericState] = field(default_factory=list)
    
    # κ tracking
    kappa_budget: KappaBudget = field(default_factory=KappaBudget)
    conservation_law: ConservationLaw = field(default_factory=ConservationLaw)
    
    # Execution stats
    steps_executed: int = 0
    total_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    # Backend
    backend: Optional[SubstrateBackend] = None
    
    def start(self, state: AethericState) -> None:
        """Start execution with initial state."""
        self.current_state = state.clone()
        self.state_history = [state.clone()]
        self.steps_executed = 0
        self.total_time = 0.0
        self.errors = []
        self.conservation_law.record(state.total_kappa)
    
    def step(self, operator: CrystalOperator) -> bool:
        """Execute one step."""
        if self.current_state is None:
            self.errors.append("No current state")
            return False
        
        start_time = time.time()
        
        try:
            # Check κ budget
            cost = operator.cost_model.kappa_cost
            if not self.kappa_budget.can_spend(cost):
                self.errors.append(f"Insufficient κ budget for {operator.name}")
                return False
            
            # Apply operator
            if self.backend and self.backend.supports_geometry(
                self.current_state.geometry.geo_type
            ):
                new_state = self.backend.apply_operator(
                    self.current_state, operator
                )
            else:
                new_state = operator.apply(self.current_state)
            
            # Update state
            self.current_state = new_state
            self.state_history.append(new_state.clone())
            self.steps_executed += 1
            
            # Track κ
            self.kappa_budget.spend(cost)
            self.conservation_law.record(new_state.total_kappa)
            
        except Exception as e:
            self.errors.append(str(e))
            return False
        
        self.total_time += time.time() - start_time
        return True
    
    def verify_conservation(self) -> Tuple[bool, float]:
        """Verify κ conservation across execution."""
        return self.conservation_law.verify_history()


# =============================================================================
# RUNTIME
# =============================================================================

@dataclass
class CrystalRuntime:
    """
    Crystal computing runtime.
    
    Manages state, operators, programs, and execution.
    """
    
    # Crystal structure
    crystal: MetaCrystal = field(default_factory=MetaCrystal)
    
    # Operator registry
    operators: OperatorRegistry = field(default_factory=OperatorRegistry)
    
    # Backends
    backends: Dict[str, SubstrateBackend] = field(default_factory=dict)
    default_backend: str = "vector"
    
    # Execution contexts
    contexts: Dict[str, ExecutionContext] = field(default_factory=dict)
    
    # Configuration
    max_steps: int = 10000
    kappa_budget: float = 1000.0
    
    def __post_init__(self):
        """Initialize with default backend."""
        self.backends["vector"] = VectorBackend()
        self.backends["graph"] = GraphBackend()
    
    def register_operator(self, operator: CrystalOperator) -> None:
        """Register an operator."""
        self.operators.register(operator)
    
    def get_operator(self, cell: CrystalCell, **params) -> CrystalOperator:
        """Get or create operator for cell."""
        existing = self.operators.get(cell)
        if existing:
            return existing[0]
        
        # Create canonical operator
        op = OperatorFactory.create_for_cell(cell, **params)
        self.register_operator(op)
        return op
    
    def create_context(self, name: str) -> ExecutionContext:
        """Create a new execution context."""
        ctx = ExecutionContext(
            kappa_budget=KappaBudget(initial=self.kappa_budget, remaining=self.kappa_budget),
            backend=self.backends.get(self.default_backend)
        )
        self.contexts[name] = ctx
        return ctx
    
    def get_context(self, name: str) -> Optional[ExecutionContext]:
        """Get execution context by name."""
        return self.contexts.get(name)
    
    def execute_program(self, program: CrystalProgram,
                       initial_state: AethericState,
                       context_name: str = "default") -> AethericState:
        """Execute a crystal program."""
        # Get or create context
        ctx = self.get_context(context_name)
        if ctx is None:
            ctx = self.create_context(context_name)
        
        # Compile if needed
        if not program.is_compiled:
            program.compile()
        
        # Start execution
        ctx.start(initial_state)
        
        # Execute steps
        for step in program.steps:
            if ctx.steps_executed >= self.max_steps:
                ctx.errors.append("Max steps exceeded")
                break
            
            success = ctx.step(step.operator)
            if not success:
                break
        
        return ctx.current_state or initial_state
    
    def execute_cell_sequence(self, cells: List[CrystalCell],
                             initial_state: AethericState,
                             **operator_params) -> AethericState:
        """Execute a sequence of cells using canonical operators."""
        program = CrystalProgram(name="cell_sequence")
        
        for cell in cells:
            op = self.get_operator(cell, **operator_params)
            program.add_step(cell, op)
        
        return self.execute_program(program, initial_state)
    
    def analyze_program(self, program: CrystalProgram) -> Dict[str, Any]:
        """Analyze a program."""
        analysis = PathAnalysis(program)
        
        return {
            "length": analysis.path_length(),
            "unique_cells": len(analysis.visited_cells()),
            "hamming_distance": analysis.hamming_distance_total(),
            "pole_distribution": {p.name: c for p, c in analysis.pole_distribution().items()},
            "acyclic": analysis.is_acyclic(),
            "kappa_profile": analysis.kappa_profile() if program.is_executed else None
        }
    
    def summary(self) -> Dict[str, Any]:
        """Get runtime summary."""
        return {
            "crystal_size": self.crystal.size,
            "registered_operators": self.operators.count(),
            "backends": list(self.backends.keys()),
            "active_contexts": len(self.contexts),
            "max_steps": self.max_steps,
            "kappa_budget": self.kappa_budget
        }


# =============================================================================
# GLOBAL RUNTIME
# =============================================================================

# Global runtime instance
_runtime: Optional[CrystalRuntime] = None

def get_runtime() -> CrystalRuntime:
    """Get or create global runtime."""
    global _runtime
    if _runtime is None:
        _runtime = CrystalRuntime()
    return _runtime


def reset_runtime() -> CrystalRuntime:
    """Reset global runtime."""
    global _runtime
    _runtime = CrystalRuntime()
    return _runtime


# =============================================================================
# VALIDATION
# =============================================================================

def validate_runtime() -> bool:
    """Validate runtime module."""
    from .operators import HadamardOperator, PhaseOperator
    
    # Test backends
    vector_backend = VectorBackend()
    assert vector_backend.name() == "vector"
    assert vector_backend.supports_geometry(GeometryType.VECTOR)
    
    # Test ExecutionContext
    ctx = ExecutionContext()
    state = AethericState.vacuum(4)
    ctx.start(state)
    assert ctx.current_state is not None
    assert ctx.steps_executed == 0
    
    # Execute step
    op = HadamardOperator(0)
    success = ctx.step(op)
    assert success
    assert ctx.steps_executed == 1
    
    # Test Runtime
    runtime = CrystalRuntime()
    assert runtime.crystal.size == 1024
    
    # Create and execute program
    from .programs import CrystalProgram
    program = CrystalProgram(name="test")
    program.add_step(op.cell, op)
    
    result = runtime.execute_program(program, state)
    assert result.is_normalized
    
    # Test analysis
    analysis = runtime.analyze_program(program)
    assert analysis["length"] == 1
    
    # Test global runtime
    rt = get_runtime()
    assert rt is not None
    
    return True


if __name__ == "__main__":
    print("Validating Crystal Computing Runtime...")
    assert validate_runtime()
    print("✓ Crystal Runtime validated")
    
    # Demo
    print("\n=== Crystal Runtime Demo ===")
    
    from .operators import HadamardOperator, PhaseOperator
    from .programs import ProgramBuilder
    
    # Get runtime
    runtime = get_runtime()
    
    print(f"\nRuntime Summary:")
    summary = runtime.summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Build and execute program
    builder = ProgramBuilder()
    program = (builder
               .named("demo_circuit")
               .apply(HadamardOperator(0))
               .apply(PhaseOperator(math.pi/4))
               .build())
    
    state = AethericState.vacuum(2)
    result = runtime.execute_program(program, state)
    
    print(f"\nProgram Execution:")
    print(f"  Program: {program.name}")
    print(f"  Steps: {program.length}")
    
    # Get context stats
    ctx = runtime.get_context("default")
    if ctx:
        print(f"  Steps executed: {ctx.steps_executed}")
        print(f"  Time: {ctx.total_time*1000:.2f}ms")
        is_conserved, deviation = ctx.verify_conservation()
        print(f"  κ conserved: {is_conserved} (deviation: {deviation:.6f})")
    
    # Analyze
    print(f"\nPath Analysis:")
    analysis = runtime.analyze_program(program)
    for key, value in analysis.items():
        if value is not None:
            print(f"  {key}: {value}")

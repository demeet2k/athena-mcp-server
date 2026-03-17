"""
ATHENA OS - BIT4
================
Dataflow Semantics and Fixed-Point Computation

From BIT4.docx §4:

DATAFLOW SEMANTICS:

Transfer function F: B₄ⁿ → B₄ⁿ defines circuit semantics.

For monotone F, stable meaning is the least fixed point:
    x* = lfp(F)

Computed by Kleene iteration:
    x₀ = ⊥ⁿ
    x_{k+1} = F(x_k)
    
Convergence guaranteed by:
    - Finite domain (4ⁿ elements)
    - Monotonicity of F
    - Knaster-Tarski theorem

ACCELERATION TECHNIQUES:
    - Worklist algorithm
    - SCC stratification
    - Widening/narrowing
    - Seed reuse
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple, Set, Optional
from enum import Enum

from .carrier import B4, B4Vector
from .orders import leq_k, leq_t, join_k


# =============================================================================
# TRANSFER FUNCTION
# =============================================================================

@dataclass
class TransferFunction:
    """
    Transfer function F: B₄ⁿ → B₄ⁿ
    
    Represents the dataflow semantics of a circuit.
    """
    
    n: int                                  # Dimension
    components: List[Callable[[B4Vector], B4]]  # n component functions
    
    def __call__(self, x: B4Vector) -> B4Vector:
        """Apply transfer function."""
        return B4Vector([f(x) for f in self.components])
    
    def iterate(self, x: B4Vector) -> B4Vector:
        """Single iteration F(x)."""
        return self(x)
    
    @classmethod
    def from_func(cls, n: int, f: Callable[[B4Vector], B4Vector]) -> 'TransferFunction':
        """Create from a single function."""
        components = [
            lambda x, i=i: f(x)[i] for i in range(n)
        ]
        return cls(n, components)


# =============================================================================
# FIXED POINT COMPUTATION
# =============================================================================

class FixpointMode(Enum):
    """Mode for fixed-point computation."""
    
    KNOWLEDGE = "k"    # Use ≤_k ordering
    TRUTH = "t"        # Use ≤_t ordering


@dataclass
class FixpointResult:
    """Result of fixed-point computation."""
    
    value: B4Vector
    iterations: int
    converged: bool
    history: List[B4Vector] = field(default_factory=list)


def kleene_iteration(F: Callable[[B4Vector], B4Vector],
                     n: int,
                     mode: FixpointMode = FixpointMode.KNOWLEDGE,
                     max_iter: int = 1000,
                     track_history: bool = False) -> FixpointResult:
    """
    Compute least fixed point via Kleene iteration.
    
    x₀ = ⊥ⁿ (or 0ⁿ for truth mode)
    x_{k+1} = F(x_k)
    
    Continue until x_k = x_{k+1} or max iterations.
    """
    # Initialize
    if mode == FixpointMode.KNOWLEDGE:
        x = B4Vector.bottom(n)
    else:
        x = B4Vector([B4.ZERO] * n)
    
    history = [x] if track_history else []
    
    for i in range(max_iter):
        x_new = F(x)
        
        if track_history:
            history.append(x_new)
        
        # Check convergence
        if x_new.values == x.values:
            return FixpointResult(
                value=x_new,
                iterations=i + 1,
                converged=True,
                history=history
            )
        
        x = x_new
    
    return FixpointResult(
        value=x,
        iterations=max_iter,
        converged=False,
        history=history
    )


def greatest_fixpoint(F: Callable[[B4Vector], B4Vector],
                     n: int,
                     mode: FixpointMode = FixpointMode.KNOWLEDGE,
                     max_iter: int = 1000) -> FixpointResult:
    """
    Compute greatest fixed point by starting from top.
    
    x₀ = ⊤ⁿ (or 1ⁿ for truth mode)
    x_{k+1} = F(x_k)
    """
    if mode == FixpointMode.KNOWLEDGE:
        x = B4Vector.top(n)
    else:
        x = B4Vector([B4.ONE] * n)
    
    for i in range(max_iter):
        x_new = F(x)
        
        if x_new.values == x.values:
            return FixpointResult(
                value=x_new,
                iterations=i + 1,
                converged=True
            )
        
        x = x_new
    
    return FixpointResult(
        value=x,
        iterations=max_iter,
        converged=False
    )


# =============================================================================
# WORKLIST ALGORITHM
# =============================================================================

@dataclass
class WorklistSolver:
    """
    Worklist-based fixed-point solver.
    
    Only recomputes components whose inputs changed.
    """
    
    n: int
    dependencies: Dict[int, Set[int]] = field(default_factory=dict)
    
    def add_dependency(self, source: int, target: int) -> None:
        """Add dependency: target depends on source."""
        if source not in self.dependencies:
            self.dependencies[source] = set()
        self.dependencies[source].add(target)
    
    def solve(self, components: List[Callable[[B4Vector], B4]],
             mode: FixpointMode = FixpointMode.KNOWLEDGE,
             max_iter: int = 10000) -> FixpointResult:
        """
        Solve using worklist algorithm.
        """
        # Initialize
        if mode == FixpointMode.KNOWLEDGE:
            x = B4Vector.bottom(self.n)
        else:
            x = B4Vector([B4.ZERO] * self.n)
        
        # Initialize worklist with all components
        worklist = list(range(self.n))
        iterations = 0
        
        while worklist and iterations < max_iter:
            iterations += 1
            
            i = worklist.pop(0)
            old_value = x[i]
            new_value = components[i](x)
            
            if new_value != old_value:
                x[i] = new_value
                
                # Add dependents to worklist
                if i in self.dependencies:
                    for dep in self.dependencies[i]:
                        if dep not in worklist:
                            worklist.append(dep)
        
        return FixpointResult(
            value=x,
            iterations=iterations,
            converged=len(worklist) == 0
        )


# =============================================================================
# SCC STRATIFICATION
# =============================================================================

def tarjan_scc(n: int, edges: Dict[int, Set[int]]) -> List[Set[int]]:
    """
    Compute strongly connected components using Tarjan's algorithm.
    
    Returns SCCs in reverse topological order.
    """
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    sccs = []
    
    def strongconnect(v):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        on_stack[v] = True
        stack.append(v)
        
        for w in edges.get(v, set()):
            if w not in index:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif on_stack.get(w, False):
                lowlinks[v] = min(lowlinks[v], index[w])
        
        if lowlinks[v] == index[v]:
            scc = set()
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.add(w)
                if w == v:
                    break
            sccs.append(scc)
    
    for v in range(n):
        if v not in index:
            strongconnect(v)
    
    return sccs


@dataclass
class StratifiedSolver:
    """
    SCC-stratified fixed-point solver.
    
    Solves SCCs in topological order.
    """
    
    n: int
    dependencies: Dict[int, Set[int]] = field(default_factory=dict)
    
    def add_dependency(self, source: int, target: int) -> None:
        """Add dependency: target depends on source."""
        if source not in self.dependencies:
            self.dependencies[source] = set()
        self.dependencies[source].add(target)
    
    def solve(self, components: List[Callable[[B4Vector], B4]],
             mode: FixpointMode = FixpointMode.KNOWLEDGE,
             max_iter: int = 1000) -> FixpointResult:
        """
        Solve using SCC stratification.
        """
        # Compute SCCs
        sccs = tarjan_scc(self.n, self.dependencies)
        
        # Initialize
        if mode == FixpointMode.KNOWLEDGE:
            x = B4Vector.bottom(self.n)
        else:
            x = B4Vector([B4.ZERO] * self.n)
        
        total_iterations = 0
        
        # Solve each SCC
        for scc in reversed(sccs):  # Topological order
            scc_list = list(scc)
            
            for _ in range(max_iter):
                total_iterations += 1
                changed = False
                
                for i in scc_list:
                    old_value = x[i]
                    new_value = components[i](x)
                    
                    if new_value != old_value:
                        x[i] = new_value
                        changed = True
                
                if not changed:
                    break
        
        return FixpointResult(
            value=x,
            iterations=total_iterations,
            converged=True
        )


# =============================================================================
# WIDENING AND NARROWING
# =============================================================================

def widen_k(x: B4, y: B4) -> B4:
    """
    Widening operator for ≤_k.
    
    If y > x (more information), jump to ⊤.
    """
    if x == y:
        return x
    if leq_k(x, y) and x != y:
        return B4.TOP
    return y


def narrow_k(x: B4, y: B4) -> B4:
    """
    Narrowing operator for ≤_k.
    
    Refine from above.
    """
    if x == B4.TOP and y != B4.TOP:
        return y
    return x


def widening_iteration(F: Callable[[B4Vector], B4Vector],
                      n: int,
                      threshold: int = 10,
                      max_iter: int = 1000) -> FixpointResult:
    """
    Fixed-point with widening for faster convergence.
    
    Apply standard iteration for `threshold` steps, then widen.
    """
    x = B4Vector.bottom(n)
    
    for i in range(max_iter):
        x_new = F(x)
        
        if x_new.values == x.values:
            return FixpointResult(
                value=x_new,
                iterations=i + 1,
                converged=True
            )
        
        # Apply widening after threshold
        if i >= threshold:
            widened = [widen_k(x[j], x_new[j]) for j in range(n)]
            x = B4Vector(widened)
        else:
            x = x_new
    
    return FixpointResult(
        value=x,
        iterations=max_iter,
        converged=False
    )


# =============================================================================
# ABSTRACT INTERPRETATION
# =============================================================================

@dataclass
class AbstractDomain:
    """
    Abstract domain for BIT4 analysis.
    """
    
    @staticmethod
    def abstract(b: bool) -> B4:
        """Abstract a concrete boolean."""
        return B4.from_bool(b)
    
    @staticmethod
    def concretize(x: B4) -> Set[bool]:
        """Concretize to possible boolean values."""
        return {b == 1 for b in x.support}
    
    @staticmethod
    def is_sound(abstract: B4, concrete: Set[bool]) -> bool:
        """
        Check if abstract value soundly represents concrete set.
        
        Soundness: concrete ⊆ concretize(abstract)
        """
        abstract_concrete = AbstractDomain.concretize(abstract)
        return concrete <= abstract_concrete


# =============================================================================
# VALIDATION
# =============================================================================

def validate_dataflow() -> bool:
    """Validate dataflow module."""
    from .orders import join_k, meet_k
    
    # Test simple fixed point
    # F(x) = x ⊕_k ⊥ = x (identity should converge immediately)
    def identity(x: B4Vector) -> B4Vector:
        return x
    
    result = kleene_iteration(identity, 3)
    assert result.converged
    assert result.iterations == 1
    
    # Test monotone function converging to fixed point
    # F([x, y]) = [x ⊕_k y, y]
    def merge_func(v: B4Vector) -> B4Vector:
        return B4Vector([join_k(v[0], v[1]), v[1]])
    
    # Set initial y = 1
    def seeded_merge(v: B4Vector) -> B4Vector:
        return B4Vector([join_k(v[0], B4.ONE), B4.ONE])
    
    result = kleene_iteration(seeded_merge, 2)
    assert result.converged
    assert result.value[0] == B4.ONE
    assert result.value[1] == B4.ONE
    
    # Test SCC algorithm
    edges = {0: {1}, 1: {2}, 2: {0, 3}, 3: set()}
    sccs = tarjan_scc(4, edges)
    # Should find SCC {0, 1, 2} and singleton {3}
    assert len(sccs) == 2
    
    # Test abstract domain
    assert AbstractDomain.abstract(True) == B4.ONE
    assert AbstractDomain.abstract(False) == B4.ZERO
    assert AbstractDomain.concretize(B4.TOP) == {True, False}
    assert AbstractDomain.concretize(B4.BOT) == set()
    
    # Test soundness
    assert AbstractDomain.is_sound(B4.TOP, {True, False})
    assert AbstractDomain.is_sound(B4.ONE, {True})
    assert not AbstractDomain.is_sound(B4.ZERO, {True})
    
    return True


if __name__ == "__main__":
    print("Validating BIT4 Dataflow...")
    assert validate_dataflow()
    print("✓ Dataflow module validated")

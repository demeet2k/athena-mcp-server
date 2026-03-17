"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ATLAS FORGE - Constraints Module                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Constraint specification, normalization, and solving.
"""

from atlasforge.constraints.constraint import (
    Constraint,
    RootConstraint,
    FixedPointConstraint,
    GeneratorConstraint,
    EqualityConstraint,
    VectorRootConstraint,
    NormalForm,
    ProofObligation,
    ConstraintIR,
)

from atlasforge.constraints.solvers import (
    Solver,
    SolverResult,
    SolverStatus,
    BisectionSolver,
    NewtonSolver,
    SecantSolver,
    BrentSolver,
    FixedPointSolver,
    IntervalNewtonSolver,
    AdaptiveSolver,
    SolverFactory,
)

from atlasforge.constraints.bracketing import (
    BracketSearchResult,
    find_bracket,
)

__all__ = [
    # Constraints
    "Constraint",
    "RootConstraint",
    "FixedPointConstraint",
    "GeneratorConstraint",
    "EqualityConstraint",
    "VectorRootConstraint",
    "NormalForm",
    "ProofObligation",
    "ConstraintIR",
    
    # Solvers
    "Solver",
    "SolverResult",
    "SolverStatus",
    "BisectionSolver",
    "NewtonSolver",
    "SecantSolver",
    "BrentSolver",
    "FixedPointSolver",
    "IntervalNewtonSolver",
    "AdaptiveSolver",
    "SolverFactory",

    # Bracketing
    "BracketSearchResult",
    "find_bracket",
]

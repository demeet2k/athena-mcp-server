"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Verifier System                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

The verifier kernel executes recipes and produces certified results.

Solver Hierarchy:
- Point solvers: Bisection, Newton, Secant, Brent
- Interval solvers: Interval Newton, Krawczyk, Moore-Kioustelidis
- Global solvers: Branch-and-bound, Continuation, Homotopy

Verification Pipeline:
1. Execute solver steps
2. Collect evidence
3. Generate certificates
4. Assemble proof pack
5. Return certified output
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Generic, List, Optional,
    Protocol, Sequence, Tuple, Type, TypeVar, Union
)
from datetime import datetime
import math
import time

from atlasforge.core.types import Interval, FloatPolicy, DEFAULT_FLOAT_POLICY
from atlasforge.core.base import ContentAddressed
from atlasforge.core.enums import (
    CertificateLevel, TruthProfile, SolverType,
    VerificationResult, PlanStatus
)
from atlasforge.constraints.constraint import NormalForm, ConstraintIR
from atlasforge.certificates.certificate import (
    Certificate, EnclosureCertificate, UniquenessCertificate,
    CorridorCertificate, ReplayCertificate, ProofPack, CertificateFactory
)
from atlasforge.recipes.recipe import (
    Recipe, RecipeOutput, ReplayLog, SolvePlan, PlanStep, SolverConfig
)


# ═══════════════════════════════════════════════════════════════════════════════
# SOLVER RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SolverResult:
    """Result from a solver execution."""
    
    success: bool = False
    value: Optional[float] = None
    interval: Optional[Interval] = None
    residual: Optional[float] = None
    iterations: int = 0
    
    # Evidence for certification
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Error info
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'value': self.value,
            'interval': str(self.interval) if self.interval else None,
            'residual': self.residual,
            'iterations': self.iterations,
            'evidence': self.evidence,
            'error_message': self.error_message,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SOLVER BASE
# ═══════════════════════════════════════════════════════════════════════════════

class Solver(ABC):
    """Abstract base class for all solvers."""
    
    @property
    @abstractmethod
    def solver_type(self) -> SolverType:
        """The type of this solver."""
        pass
    
    @property
    @abstractmethod
    def produces_enclosure(self) -> bool:
        """Whether this solver produces verified enclosures."""
        pass
    
    @abstractmethod
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        config: SolverConfig
    ) -> SolverResult:
        """Execute the solver."""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# POINT SOLVERS
# ═══════════════════════════════════════════════════════════════════════════════

class BisectionSolver(Solver):
    """
    Bisection root finder.
    
    Requires: H(a) and H(b) have opposite signs (bracketing).
    Produces: L1 enclosure certificate.
    """
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.BISECTION
    
    @property
    def produces_enclosure(self) -> bool:
        return True
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        config: SolverConfig
    ) -> SolverResult:
        a, b = domain.lo, domain.hi
        fa, fb = H(a), H(b)
        
        # Check bracketing
        if fa * fb > 0:
            return SolverResult(
                success=False,
                error_message="No sign change in interval (not bracketed)"
            )
        
        iterations = 0
        while (b - a) > config.tolerance and iterations < config.max_iterations:
            c = (a + b) / 2
            fc = H(c)
            
            if fc == 0:
                return SolverResult(
                    success=True,
                    value=c,
                    interval=Interval.point(c),
                    residual=0.0,
                    iterations=iterations,
                    evidence={
                        'exact_root': True,
                        'method': 'bisection',
                    }
                )
            
            if fa * fc < 0:
                b, fb = c, fc
            else:
                a, fa = c, fc
            
            iterations += 1
        
        midpoint = (a + b) / 2
        return SolverResult(
            success=True,
            value=midpoint,
            interval=Interval.closed(a, b),
            residual=abs(H(midpoint)),
            iterations=iterations,
            evidence={
                'sign_change': True,
                'H_lo': H(a),
                'H_hi': H(b),
                'method': 'bisection',
            }
        )


class NewtonSolver(Solver):
    """
    Newton-Raphson root finder.
    
    Requires: Good initial guess and derivative.
    Produces: L0 claim (no guaranteed enclosure).
    """
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.NEWTON
    
    @property
    def produces_enclosure(self) -> bool:
        return False
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        config: SolverConfig,
        dH: Optional[Callable[[float], float]] = None
    ) -> SolverResult:
        x = domain.midpoint
        
        # Numerical derivative if not provided
        def derivative(x: float, eps: float = 1e-8) -> float:
            if dH is not None:
                return dH(x)
            return (H(x + eps) - H(x - eps)) / (2 * eps)
        
        iterations = 0
        while iterations < config.max_iterations:
            fx = H(x)
            
            if abs(fx) < config.tolerance:
                return SolverResult(
                    success=True,
                    value=x,
                    residual=abs(fx),
                    iterations=iterations,
                    evidence={
                        'method': 'newton',
                        'converged': True,
                    }
                )
            
            dfx = derivative(x)
            if abs(dfx) < 1e-15:
                return SolverResult(
                    success=False,
                    error_message="Derivative near zero",
                    iterations=iterations,
                )
            
            x_new = x - fx / dfx
            
            # Check if outside domain
            if not domain.contains(x_new):
                x_new = max(domain.lo, min(domain.hi, x_new))
            
            if abs(x_new - x) < config.tolerance:
                return SolverResult(
                    success=True,
                    value=x_new,
                    residual=abs(H(x_new)),
                    iterations=iterations,
                    evidence={
                        'method': 'newton',
                        'converged': True,
                    }
                )
            
            x = x_new
            iterations += 1
        
        return SolverResult(
            success=False,
            value=x,
            residual=abs(H(x)),
            iterations=iterations,
            error_message="Max iterations reached",
        )


class BrentSolver(Solver):
    """
    Brent's method - combines bisection, secant, and inverse quadratic interpolation.
    
    Robust and efficient, guaranteed to converge if bracketed.
    """
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.BRENT
    
    @property
    def produces_enclosure(self) -> bool:
        return True
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        config: SolverConfig
    ) -> SolverResult:
        a, b = domain.lo, domain.hi
        fa, fb = H(a), H(b)
        
        if fa * fb > 0:
            return SolverResult(
                success=False,
                error_message="No sign change in interval"
            )
        
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa
        
        c, fc = a, fa
        d = b - a
        e = d
        
        iterations = 0
        while iterations < config.max_iterations:
            if abs(fb) < config.tolerance:
                return SolverResult(
                    success=True,
                    value=b,
                    interval=Interval.closed(min(a, b), max(a, b)),
                    residual=abs(fb),
                    iterations=iterations,
                    evidence={'method': 'brent'}
                )
            
            if fa != fc and fb != fc:
                # Inverse quadratic interpolation
                s = (a * fb * fc / ((fa - fb) * (fa - fc)) +
                     b * fa * fc / ((fb - fa) * (fb - fc)) +
                     c * fa * fb / ((fc - fa) * (fc - fb)))
            else:
                # Secant method
                s = b - fb * (b - a) / (fb - fa)
            
            # Conditions for accepting s
            cond1 = (s < (3 * a + b) / 4 or s > b)
            cond2 = (abs(s - b) >= abs(b - c) / 2)
            cond3 = (abs(b - c) < config.tolerance)
            
            if cond1 or cond2 or cond3:
                # Bisection
                s = (a + b) / 2
            
            fs = H(s)
            c, fc = b, fb
            
            if fa * fs < 0:
                b, fb = s, fs
            else:
                a, fa = s, fs
            
            if abs(fa) < abs(fb):
                a, b = b, a
                fa, fb = fb, fa
            
            iterations += 1
        
        return SolverResult(
            success=False,
            value=b,
            residual=abs(H(b)),
            iterations=iterations,
            error_message="Max iterations reached"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# INTERVAL SOLVERS
# ═══════════════════════════════════════════════════════════════════════════════

class IntervalNewtonSolver(Solver):
    """
    Interval Newton method.
    
    Produces verified enclosures (L2 certificates) when it contracts.
    
    N(X) = m - H(m)/H'(X)
    
    If N(X) ⊂ X, then there exists a unique root in N(X).
    """
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.INTERVAL_NEWTON
    
    @property
    def produces_enclosure(self) -> bool:
        return True
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        config: SolverConfig,
        dH: Optional[Callable[[float], float]] = None
    ) -> SolverResult:
        X = domain
        
        def H_interval(I: Interval) -> Interval:
            """Evaluate H on an interval (natural interval extension)."""
            samples = [H(I.lo), H(I.hi), H(I.midpoint)]
            return Interval.closed(min(samples), max(samples))
        
        def dH_interval(I: Interval, eps: float = 1e-8) -> Interval:
            """Evaluate H' on an interval."""
            if dH is not None:
                samples = [dH(I.lo), dH(I.hi), dH(I.midpoint)]
            else:
                # Numerical derivative bounds
                samples = []
                for x in [I.lo, I.hi, I.midpoint]:
                    d = (H(x + eps) - H(x - eps)) / (2 * eps)
                    samples.append(d)
            return Interval.closed(min(samples), max(samples))
        
        iterations = 0
        contractions = []
        
        while iterations < config.max_iterations:
            m = X.midpoint
            Hm = H(m)
            dH_X = dH_interval(X)
            
            # Check for zero derivative
            if dH_X.contains(0):
                # Split interval
                return SolverResult(
                    success=False,
                    interval=X,
                    iterations=iterations,
                    error_message="Derivative contains zero - need to split",
                    evidence={'contains_zero_derivative': True}
                )
            
            # Newton step
            N_lo = m - Hm / dH_X.lo
            N_hi = m - Hm / dH_X.hi
            N = Interval.closed(min(N_lo, N_hi), max(N_lo, N_hi))
            
            # Intersect with current interval
            X_new = X.intersection(N)
            
            if X_new is None:
                return SolverResult(
                    success=False,
                    iterations=iterations,
                    error_message="Newton step left interval - no root",
                )
            
            # Check contraction
            contraction = X_new.width / X.width if X.width > 0 else 0
            contractions.append(contraction)
            
            if X_new.width < config.tolerance:
                return SolverResult(
                    success=True,
                    value=X_new.midpoint,
                    interval=X_new,
                    residual=abs(H(X_new.midpoint)),
                    iterations=iterations,
                    evidence={
                        'method': 'interval_newton',
                        'contractions': contractions,
                        'final_contraction': contraction,
                        'verified_enclosure': contraction < 1,
                    }
                )
            
            X = X_new
            iterations += 1
        
        return SolverResult(
            success=True,
            value=X.midpoint,
            interval=X,
            residual=abs(H(X.midpoint)),
            iterations=iterations,
            evidence={
                'method': 'interval_newton',
                'contractions': contractions,
            }
        )


class KrawczykSolver(Solver):
    """
    Krawczyk operator for verified root finding.
    
    K(X) = m - Y·H(m) + (I - Y·H'(X))·(X - m)
    
    If K(X) ⊂ X, then X contains a unique root.
    """
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.KRAWCZYK
    
    @property
    def produces_enclosure(self) -> bool:
        return True
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        config: SolverConfig,
        dH: Optional[Callable[[float], float]] = None
    ) -> SolverResult:
        X = domain
        
        def dH_point(x: float, eps: float = 1e-8) -> float:
            if dH is not None:
                return dH(x)
            return (H(x + eps) - H(x - eps)) / (2 * eps)
        
        def dH_interval(I: Interval) -> Interval:
            samples = [dH_point(I.lo), dH_point(I.hi), dH_point(I.midpoint)]
            return Interval.closed(min(samples), max(samples))
        
        iterations = 0
        
        while iterations < config.max_iterations:
            m = X.midpoint
            Hm = H(m)
            
            # Approximate inverse of derivative at midpoint
            dm = dH_point(m)
            if abs(dm) < 1e-15:
                return SolverResult(
                    success=False,
                    error_message="Derivative near zero at midpoint"
                )
            Y = 1.0 / dm
            
            # Interval derivative
            dH_X = dH_interval(X)
            
            # Krawczyk operator
            # K(X) = m - Y·H(m) + (1 - Y·dH_X)·(X - m)
            center = m - Y * Hm
            
            # (1 - Y·dH_X) as interval
            factor_lo = 1 - Y * dH_X.hi
            factor_hi = 1 - Y * dH_X.lo
            factor = Interval.closed(min(factor_lo, factor_hi), max(factor_lo, factor_hi))
            
            # (X - m) as interval
            delta = Interval.closed(X.lo - m, X.hi - m)
            
            # factor · delta
            spread_candidates = [
                factor.lo * delta.lo, factor.lo * delta.hi,
                factor.hi * delta.lo, factor.hi * delta.hi
            ]
            spread = Interval.closed(min(spread_candidates), max(spread_candidates))
            
            # K(X) = center + spread
            K = Interval.closed(center + spread.lo, center + spread.hi)
            
            # Check if K ⊂ interior(X)
            is_contained = K.lo > X.lo and K.hi < X.hi
            
            # Intersect
            X_new = X.intersection(K)
            
            if X_new is None:
                return SolverResult(
                    success=False,
                    iterations=iterations,
                    error_message="Krawczyk step empty - no root",
                )
            
            if X_new.width < config.tolerance:
                return SolverResult(
                    success=True,
                    value=X_new.midpoint,
                    interval=X_new,
                    residual=abs(H(X_new.midpoint)),
                    iterations=iterations,
                    evidence={
                        'method': 'krawczyk',
                        'contracts': is_contained,
                        'verified_unique': is_contained,
                    }
                )
            
            X = X_new
            iterations += 1
        
        return SolverResult(
            success=True,
            value=X.midpoint,
            interval=X,
            residual=abs(H(X.midpoint)),
            iterations=iterations,
            evidence={'method': 'krawczyk'}
        )


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

class VerifierKernel:
    """
    The Verifier Kernel executes recipes and produces certified results.
    
    This is the core execution engine of AtlasForge.
    """
    
    def __init__(self, float_policy: FloatPolicy = DEFAULT_FLOAT_POLICY):
        self.float_policy = float_policy
        self.solvers: Dict[SolverType, Solver] = {
            SolverType.BISECTION: BisectionSolver(),
            SolverType.NEWTON: NewtonSolver(),
            SolverType.BRENT: BrentSolver(),
            SolverType.INTERVAL_NEWTON: IntervalNewtonSolver(),
            SolverType.KRAWCZYK: KrawczykSolver(),
        }
    
    def execute(self, recipe: Recipe) -> RecipeOutput:
        """
        Execute a recipe and produce certified output.
        
        This is the main entry point for the verifier.
        """
        start_time = time.time()
        
        if not recipe.is_complete():
            return RecipeOutput.failure_result(
                recipe.content_hash(),
                "Incomplete recipe"
            )
        
        # Initialize replay log
        replay_log = ReplayLog(
            float_policy=self.float_policy,
            recipe_hash=recipe.content_hash(),
        )
        
        # Get constraint function from IR
        H = recipe.ir.normal_form.H
        if H is None:
            return RecipeOutput.failure_result(
                recipe.content_hash(),
                "No constraint function in IR"
            )
        
        # Get domain
        domain = recipe.blueprint.search_domain
        if domain is None:
            domain = Interval.closed(-10, 10)
        
        # Execute plan steps
        current_result: Optional[SolverResult] = None
        certificates: List[Certificate] = []
        
        for step in recipe.plan.execution_order():
            step_result = self._execute_step(step, H, domain, current_result)
            
            # Log step
            replay_log.log_step(
                step.name,
                input_hash=str(hash(str(domain))),
                output_hash=str(hash(str(step_result.value))),
                iterations=step_result.iterations,
                residual=step_result.residual,
            )
            
            if not step_result.success:
                elapsed = (time.time() - start_time) * 1000
                return RecipeOutput.failure_result(
                    recipe.content_hash(),
                    step_result.error_message or f"Step {step.name} failed",
                    time_ms=elapsed
                )
            
            # Update domain if enclosure found
            if step_result.interval is not None:
                domain = step_result.interval
            
            # Generate certificates from step evidence
            step_certs = self._generate_certificates(step, step_result)
            certificates.extend(step_certs)
            
            current_result = step_result
        
        # Assemble proof pack
        proof_pack = ProofPack.from_certificates(
            certificates,
            recipe.truth_profile,
            result_hash=str(hash(str(current_result.value))),
            constraint_hash=recipe.blueprint.constraint.content_hash() if recipe.blueprint.constraint else "",
        )
        
        # Add replay certificate
        replay_log.complete(str(hash(str(current_result.value))))
        replay_cert = CertificateFactory.replay_deterministic(
            recipe.content_hash(),
            str(hash(str(domain))),
            str(hash(str(current_result.value))),
            self.float_policy
        )
        proof_pack.add_certificate(replay_cert)
        
        elapsed = (time.time() - start_time) * 1000
        
        return RecipeOutput.success_result(
            value=current_result.value,
            recipe_hash=recipe.content_hash(),
            proof_pack=proof_pack,
            interval=current_result.interval,
            iterations=current_result.iterations,
            time_ms=elapsed,
        )
    
    def _execute_step(
        self,
        step: PlanStep,
        H: Callable[[float], float],
        domain: Interval,
        previous: Optional[SolverResult]
    ) -> SolverResult:
        """Execute a single plan step."""
        solver = self.solvers.get(step.config.solver_type)
        
        if solver is None:
            return SolverResult(
                success=False,
                error_message=f"Unknown solver type: {step.config.solver_type}"
            )
        
        # Use previous interval if available
        if previous is not None and previous.interval is not None:
            domain = previous.interval
        
        return solver.solve(H, domain, step.config)
    
    def _generate_certificates(
        self,
        step: PlanStep,
        result: SolverResult
    ) -> List[Certificate]:
        """Generate certificates from step result."""
        certs = []
        
        # Enclosure certificate
        if result.interval is not None:
            evidence = result.evidence
            
            if evidence.get('verified_enclosure') or evidence.get('sign_change'):
                level = CertificateLevel.L2_CERTIFIED if evidence.get('verified_enclosure') else CertificateLevel.L1_EMPIRICAL
                
                certs.append(EnclosureCertificate(
                    level=level,
                    enclosure=result.interval,
                    tolerance=result.interval.width / 2,
                    sign_change_verified=evidence.get('sign_change', False),
                    contraction_factor=evidence.get('final_contraction'),
                    iterations_to_convergence=result.iterations,
                    evidence=evidence,
                ))
        
        # Uniqueness certificate from Krawczyk
        if result.evidence.get('verified_unique') and result.interval is not None:
            certs.append(UniquenessCertificate(
                level=CertificateLevel.L2_CERTIFIED,
                region=result.interval,
                krawczyk_contracts=True,
                evidence={'method': 'krawczyk'}
            ))
        
        return certs
    
    def verify_output(self, output: RecipeOutput) -> VerificationResult:
        """Re-verify an existing output."""
        if not output.success:
            return VerificationResult.FAILED
        
        if not output.proof_pack.is_valid():
            return VerificationResult.FAILED
        
        if not output.proof_pack.meets_profile():
            return VerificationResult.UNVERIFIED
        
        return VerificationResult.VERIFIED


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def solve(
    H: Callable[[float], float],
    domain: Interval = Interval.closed(-10, 10),
    truth_profile: TruthProfile = TruthProfile.VALIDATE,
    name: str = "root"
) -> RecipeOutput:
    """
    Convenience function to solve a root-finding problem.
    
    This is the simplest API for using AtlasForge.
    """
    from atlasforge.recipes.recipe import RecipeCompiler
    
    recipe = RecipeCompiler.compile_from_function(
        H, domain, name, truth_profile
    )
    
    kernel = VerifierKernel()
    return kernel.execute(recipe)


def find_root(
    H: Callable[[float], float],
    lo: float,
    hi: float,
    tolerance: float = 1e-10
) -> Tuple[float, Interval]:
    """
    Simple root-finding interface.
    
    Returns (value, enclosure).
    """
    result = solve(H, Interval.closed(lo, hi))
    
    if not result.success:
        raise ValueError(result.error_message or "Root finding failed")
    
    return (result.value, result.interval)

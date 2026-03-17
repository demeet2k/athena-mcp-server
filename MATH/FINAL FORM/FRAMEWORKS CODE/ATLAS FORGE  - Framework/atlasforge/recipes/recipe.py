"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Recipe System                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

The Recipe Pipeline: proof-carrying build artifacts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
import json
import time

from atlasforge.core.types import Interval, FloatPolicy, DEFAULT_FLOAT_POLICY
from atlasforge.core.base import ContentAddressed
from atlasforge.core.enums import (
    TruthProfile, SolverType, PlanStatus, CertificateLevel, ConstraintType
)
from atlasforge.constraints.constraint import Constraint, RootConstraint, ConstraintIR, NormalForm
from atlasforge.constraints.solvers import (
    Solver, SolverResult, SolverFactory, BrentSolver, IntervalNewtonSolver
)
from atlasforge.constraints.bracketing import find_bracket
from atlasforge.certificates.certificate import (
    Certificate, EnclosureCertificate, ReplayCertificate,
    CertificateBundle, ProofPack, CertificateFactory
)
from atlasforge.lenses.chart import Chart


@dataclass
class Blueprint(ContentAddressed):
    """Blueprint: WHAT to solve."""
    
    constraint: Optional[Constraint] = None
    chart: Optional[Chart] = None
    truth_profile: TruthProfile = TruthProfile.EXPLORE
    search_domain: Optional[Interval] = None
    hints: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    description: str = ""
    
    def canonical_repr(self) -> str:
        constraint_hash = self.constraint.content_hash() if self.constraint else ""
        return json.dumps({
            'constraint': constraint_hash,
            'profile': self.truth_profile.value,
            'name': self.name,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'profile': self.truth_profile.value,
            'constraint_hash': self.constraint.content_hash() if self.constraint else "",
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Blueprint':
        return cls(
            name=data.get('name', ''),
            truth_profile=TruthProfile(data.get('profile', 'explore')))
    
    def to_ir(self) -> ConstraintIR:
        if self.constraint is None:
            return ConstraintIR()
        return ConstraintIR.from_constraint(self.constraint)


@dataclass
class SolvePlan(ContentAddressed):
    """SolvePlan: HOW to solve."""
    
    primary_solver: SolverType = SolverType.BRENT
    fallback_solvers: List[SolverType] = field(default_factory=list)
    tolerance: float = 1e-12
    max_iterations: int = 1000
    # Deeper execution: if a bracket is missing, attempt to find one.
    auto_bracket: bool = True
    bracket_samples: int = 200
    bracket_expand_steps: int = 10
    bracket_expand_factor: float = 2.0
    verify_solution: bool = False
    verification_solver: SolverType = SolverType.INTERVAL_NEWTON
    float_policy: FloatPolicy = field(default_factory=lambda: DEFAULT_FLOAT_POLICY)
    status: PlanStatus = PlanStatus.DRAFT
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'primary': self.primary_solver.value,
            'tol': self.tolerance,
            'auto_bracket': self.auto_bracket,
            'bracket_samples': self.bracket_samples,
            'bracket_expand_steps': self.bracket_expand_steps,
            'bracket_expand_factor': self.bracket_expand_factor,
            'verify': self.verify_solution,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'primary_solver': self.primary_solver.value,
            'tolerance': self.tolerance,
            'auto_bracket': self.auto_bracket,
            'bracket_samples': self.bracket_samples,
            'bracket_expand_steps': self.bracket_expand_steps,
            'bracket_expand_factor': self.bracket_expand_factor,
            'verify': self.verify_solution,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SolvePlan':
        return cls(
            primary_solver=SolverType(data.get('primary_solver', 'brent')),
            tolerance=data.get('tolerance', 1e-12),
            auto_bracket=bool(data.get('auto_bracket', True)),
            bracket_samples=int(data.get('bracket_samples', 200)),
            bracket_expand_steps=int(data.get('bracket_expand_steps', 10)),
            bracket_expand_factor=float(data.get('bracket_expand_factor', 2.0)),
        )
    
    @classmethod
    def default(cls) -> 'SolvePlan':
        return cls(
            primary_solver=SolverType.BRENT,
            fallback_solvers=[SolverType.BISECTION],
            tolerance=1e-12, verify_solution=False,
            auto_bracket=True, bracket_samples=200)
    
    @classmethod
    def fast(cls) -> 'SolvePlan':
        return cls(
            primary_solver=SolverType.NEWTON,
            fallback_solvers=[SolverType.BRENT],
            tolerance=1e-10, max_iterations=100, verify_solution=False,
            auto_bracket=True, bracket_samples=200)
    
    @classmethod
    def verified(cls) -> 'SolvePlan':
        return cls(
            primary_solver=SolverType.BRENT,
            fallback_solvers=[SolverType.BISECTION],
            tolerance=1e-12, verify_solution=True,
            verification_solver=SolverType.INTERVAL_NEWTON,
            auto_bracket=True, bracket_samples=400)


@dataclass
class ReplayLogEntry:
    """Single entry in replay log."""
    phase: str
    action: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayLog(ContentAddressed):
    """Execution trace for deterministic replay."""
    
    entries: List[ReplayLogEntry] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    input_hash: str = ""
    output_hash: str = ""
    float_policy: FloatPolicy = field(default_factory=lambda: DEFAULT_FLOAT_POLICY)
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'input': self.input_hash,
            'output': self.output_hash,
            'entries': len(self.entries),
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'input_hash': self.input_hash,
            'output_hash': self.output_hash,
            'entry_count': len(self.entries),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReplayLog':
        return cls(
            input_hash=data.get('input_hash', ''),
            output_hash=data.get('output_hash', ''))
    
    def log(self, phase: str, action: str, **data):
        self.entries.append(ReplayLogEntry(
            phase=phase, action=action, timestamp=datetime.utcnow(), data=data))
    
    def start(self):
        self.start_time = datetime.utcnow()
        self.log("INIT", "start")
    
    def finish(self, output_hash: str):
        self.end_time = datetime.utcnow()
        self.output_hash = output_hash
        self.log("FINISH", "complete")


@dataclass
class RecipeOutput(ContentAddressed):
    """Results from recipe execution."""
    
    solution: Optional[float] = None
    residual: float = float('inf')
    enclosure: Optional[Interval] = None
    all_solutions: List[float] = field(default_factory=list)
    solver_result: Optional[SolverResult] = None
    # Proof-carrying output:
    #   Store certificates in a CertificateBundle (not a raw list) so the
    #   verifier and registry can reason about levels & validity consistently.
    certificates: CertificateBundle = field(default_factory=CertificateBundle)
    success: bool = False
    verified: bool = False
    solve_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_certificate(self, cert: Certificate) -> None:
        """Add a certificate to this output's bundle."""
        self.certificates.add(cert)
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'solution': self.solution,
            'residual': self.residual,
            'success': self.success,
            'verified': self.verified,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'solution': self.solution,
            'residual': self.residual,
            'success': self.success,
            'verified': self.verified,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecipeOutput':
        return cls(
            solution=data.get('solution'),
            residual=data.get('residual', float('inf')),
            success=data.get('success', False),
            verified=data.get('verified', False))


@dataclass
class Recipe(ContentAddressed):
    """Complete recipe artifact."""
    
    blueprint: Optional[Blueprint] = None
    plan: Optional[SolvePlan] = None
    output: Optional[RecipeOutput] = None
    replay_log: Optional[ReplayLog] = None
    proof_pack: Optional[ProofPack] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    complete: bool = False
    
    def canonical_repr(self) -> str:
        bp_hash = self.blueprint.content_hash() if self.blueprint else ""
        out_hash = self.output.content_hash() if self.output else ""
        return json.dumps({
            'blueprint': bp_hash,
            'output': out_hash,
            'complete': self.complete,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'complete': self.complete,
            'created_at': self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        return cls(complete=data.get('complete', False))
    
    @property
    def solution(self) -> Optional[float]:
        return self.output.solution if self.output else None
    
    @property
    def success(self) -> bool:
        return self.output.success if self.output else False
    
    @property
    def verified(self) -> bool:
        return self.output.verified if self.output else False
    
    @property
    def certificate_level(self) -> CertificateLevel:
        if self.proof_pack and self.proof_pack.bundle:
            return self.proof_pack.bundle.level
        return CertificateLevel.L0_CLAIM


class RecipeExecutor:
    """Execute the recipe pipeline."""
    
    def __init__(self):
        self.solver_factory = SolverFactory
    
    def execute(self, blueprint: Blueprint, plan: SolvePlan = None) -> Recipe:
        if plan is None:
            plan = SolvePlan.default()
        
        recipe = Recipe(blueprint=blueprint, plan=plan)
        recipe.replay_log = ReplayLog(input_hash=blueprint.content_hash())
        recipe.replay_log.start()
        
        start_time = time.time()
        
        # PARSE
        recipe.replay_log.log("PARSE", "to_ir")
        ir = blueprint.to_ir()
        
        # NORMALIZE
        recipe.replay_log.log("NORMALIZE", "get_normal_form")
        normal_form = ir.normal_form
        
        # PLAN
        recipe.replay_log.log("PLAN", "validate_plan")
        plan.status = PlanStatus.COMPILED
        
        # SOLVE
        recipe.replay_log.log("SOLVE", "execute_solver")
        output = self._solve(blueprint, plan, normal_form)
        
        # CERTIFY
        recipe.replay_log.log("CERTIFY", "generate_certificates")
        self._certify(output, plan)
        
        # VERIFY (optional)
        if plan.verify_solution and output.success:
            recipe.replay_log.log("VERIFY", "interval_newton")
            self._verify(blueprint, output)
        
        output.solve_time = time.time() - start_time
        recipe.output = output
        recipe.complete = output.success
        
        recipe.replay_log.finish(output.content_hash())

        # Attach a ProofPack so the recipe is self-describing and the verifier
        # has a single, canonical place to read certificates.
        recipe.proof_pack = ProofPack(
            result_value=output.solution,
            result_hash=output.content_hash(),
            bundle=output.certificates,
            replay_log_hash=recipe.replay_log.content_hash(),
        )
        recipe.proof_pack.check_completeness()

        # Optional "memory bank" logging: set ATLASFORGE_MEMORY_DIR to a folder
        # path and every executed recipe will be recorded as a MemoryEntry.
        try:
            import os
            mem_dir = os.environ.get("ATLASFORGE_MEMORY_DIR")
            if mem_dir:
                from atlasforge.memory import MemoryStore
                store = MemoryStore(mem_dir)
                entry_hash = store.log_recipe(recipe)
                output.metadata["memory_entry"] = entry_hash
        except Exception as e:
            # Never fail the computation pipeline because logging failed.
            output.metadata["memory_error"] = str(e)
        
        return recipe
    
    def _solve(self, blueprint: Blueprint, plan: SolvePlan, 
               normal_form: Optional[NormalForm]) -> RecipeOutput:
        output = RecipeOutput()
        
        if normal_form is None or normal_form.H is None:
            return output
        
        H = normal_form.H

        # Domain selection priority:
        #   1) blueprint.search_domain (explicit override)
        #   2) constraint.domain
        #   3) a reasonable fallback
        domain = blueprint.search_domain
        if domain is None:
            domain = blueprint.constraint.domain if blueprint.constraint else Interval.closed(-100, 100)

        # Optional chart transport (solve in chart coordinates, then pull back).
        chart = blueprint.chart
        H_eff = H
        domain_eff = domain
        chart_used = False

        if chart is not None and isinstance(domain, Interval) and domain.is_bounded:
            try:
                # Corridor checks (endpoints). For non-monotone charts this is
                # a best-effort guard; users can enforce tighter predicates.
                chart.corridor.assert_in(domain.lo, context="Chart corridor")
                chart.corridor.assert_in(domain.hi, context="Chart corridor")

                u_lo = chart.forward(domain.lo)
                u_hi = chart.forward(domain.hi)
                domain_eff = Interval.closed(min(u_lo, u_hi), max(u_lo, u_hi))

                def H_eff(u: float) -> float:
                    return H(chart.inverse(u))

                chart_used = True
                output.metadata["chart"] = {
                    "name": getattr(chart, "name", type(chart).__name__),
                    "symbol": getattr(chart, "symbol", ""),
                    "x_domain": str(domain),
                    "u_domain": str(domain_eff),
                }
            except Exception as e:
                # If transport fails, fall back to direct coordinates.
                output.metadata["chart_error"] = str(e)
                chart_used = False
                H_eff = H
                domain_eff = domain
        
        # Try primary solver
        solver = self.solver_factory.create(plan.primary_solver)
        solver.tol = plan.tolerance
        solver.max_iter = plan.max_iterations
        
        result = solver.solve(H_eff, domain_eff)
        
        # Fallback if needed
        if not result.converged and plan.fallback_solvers:
            for solver_type in plan.fallback_solvers:
                fallback = self.solver_factory.create(solver_type)
                fallback.tol = plan.tolerance
                result = fallback.solve(H_eff, domain_eff)
                if result.converged:
                    break

        # Auto-bracketing (Fractal lens): if we failed due to missing sign
        # change, try to *discover* a bracket and re-run a bracketed solver.
        if (
            not result.converged
            and plan.auto_bracket
            and hasattr(domain_eff, "lo")
            and hasattr(domain_eff, "hi")
        ):
            try:
                bs = find_bracket(
                    H_eff,
                    domain_eff,
                    samples=plan.bracket_samples,
                    x0=(domain_eff.midpoint if getattr(domain_eff, "is_bounded", False) else None),
                    expand_steps=plan.bracket_expand_steps,
                    expand_factor=plan.bracket_expand_factor,
                )
                output.metadata["auto_bracket"] = {
                    "attempted": True,
                    "found": bs.found,
                    "bracket": str(bs.bracket) if bs.bracket else None,
                    "best_x": bs.best_x,
                    "best_fx": bs.best_fx,
                    "evaluations": bs.evaluations,
                    "expansions": bs.expansions,
                    "message": bs.message,
                    "prev_status": getattr(result.status, "name", str(result.status)),
                }

                if bs.found and bs.bracket is not None:
                    # Brent is the most robust bracketed method.
                    rescue = self.solver_factory.create(SolverType.BRENT)
                    rescue.tol = plan.tolerance
                    rescue.max_iter = plan.max_iterations
                    result = rescue.solve(H_eff, bs.bracket)
                    output.metadata["auto_bracket"]["rescue_solver"] = "brent"
            except Exception as e:
                output.metadata["auto_bracket"] = {
                    "attempted": True,
                    "error": str(e),
                }

        # If we solved in chart coordinates, pull the result back to x-space.
        if chart_used and chart is not None and result.solution is not None:
            x_solution = chart.inverse(result.solution)
            x_residual = abs(H(x_solution))
            x_enclosure = None
            if result.enclosure is not None:
                a = chart.inverse(result.enclosure.lo)
                b = chart.inverse(result.enclosure.hi)
                x_enclosure = Interval.closed(min(a, b), max(a, b))

            # Preserve the original solver result in metadata for replay/inspection.
            output.metadata.setdefault("chart", {})
            output.metadata["chart"].update({
                "u_solution": result.solution,
                "u_residual": result.residual,
                "u_enclosure": str(result.enclosure) if result.enclosure else None,
            })

            result = SolverResult(
                status=result.status,
                solution=x_solution,
                residual=x_residual,
                iterations=result.iterations,
                enclosure=x_enclosure,
                enclosure_verified=result.enclosure_verified,
                iteration_history=result.iteration_history,
                solver_type=result.solver_type,
                message=result.message,
            )
        
        output.solution = result.solution
        output.residual = result.residual
        output.enclosure = result.enclosure
        output.solver_result = result
        output.success = result.converged
        output.verified = result.enclosure_verified
        
        return output
    
    def _certify(self, output: RecipeOutput, plan: SolvePlan):
        if not output.success:
            return

        # Tie the bundle to this output for content-addressing.
        output.certificates.result_hash = output.content_hash()
        
        # Enclosure certificate
        enc_cert = CertificateFactory.enclosure(
            solution=output.solution,
            enclosure=output.enclosure or Interval.closed(output.solution - 1e-10, output.solution + 1e-10),
            residual=output.residual,
            verified=output.verified)
        output.add_certificate(enc_cert)
        
        # Replay certificate
        replay_cert = CertificateFactory.replay(
            input_hash="", recipe_hash="", output_hash=output.content_hash())
        output.add_certificate(replay_cert)
    
    def _verify(self, blueprint: Blueprint, output: RecipeOutput):
        if blueprint.constraint is None:
            return
        
        H = blueprint.constraint.H if hasattr(blueprint.constraint, 'H') else None
        if H is None:
            return
        
        domain = blueprint.constraint.domain
        if domain is None:
            domain = Interval.closed(output.solution - 0.1, output.solution + 0.1)
        
        verifier = IntervalNewtonSolver(tol=1e-14)
        result = verifier.solve(H, domain)
        
        if result.converged and result.enclosure_verified:
            output.verified = True
            output.enclosure = result.enclosure

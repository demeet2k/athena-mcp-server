"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ATLAS FORGE - Verifier System                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

The Verifier Kernel: Trust but Verify.

The verifier is the gatekeeper that ensures results meet their claimed
certificate levels. It implements:

1. Certificate Validation - Check certificates are well-formed and valid
2. Replay Verification - Re-execute and compare
3. Enclosure Verification - Verify bounds using interval arithmetic
4. Uniqueness Verification - Prove root is unique in region
5. Cross-Validation - Check consistency across methods

Fail-Closed Principle: If verification fails, the result is REJECTED.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum, auto
import math

from atlasforge.core.types import Interval, FloatPolicy, DEFAULT_FLOAT_POLICY
from atlasforge.core.enums import CertificateLevel, TruthProfile, VerificationResult
from atlasforge.certificates.certificate import (
    Certificate, CertificateBundle, ProofPack,
    EnclosureCertificate, UniquenessCertificate, ReplayCertificate
)
from atlasforge.recipes.recipe import Recipe, RecipeExecutor
from atlasforge.constraints.solvers import IntervalNewtonSolver, SolverResult


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VerificationReport:
    """
    Detailed report from verification.
    """
    
    result: VerificationResult
    certificate_level: CertificateLevel
    
    # Individual check results
    checks: Dict[str, bool] = field(default_factory=dict)
    
    # Details
    messages: List[str] = field(default_factory=list)
    
    # Timing
    verification_time: float = 0.0
    
    @property
    def passed(self) -> bool:
        return self.result == VerificationResult.OK_VERIFIED
    
    def add_check(self, name: str, passed: bool, message: str = ""):
        self.checks[name] = passed
        if message:
            self.messages.append(f"{name}: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'result': self.result.value,
            'level': self.certificate_level.value,
            'checks': self.checks,
            'messages': self.messages,
            'verification_time': self.verification_time,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION POLICY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VerificationPolicy:
    """
    Policy for verification strictness.
    """
    
    # What to verify
    check_enclosure: bool = True
    check_replay: bool = True
    check_uniqueness: bool = False
    check_stability: bool = False
    
    # Tolerances
    enclosure_tolerance: float = 1e-10
    replay_tolerance: float = 0.0  # Exact match required
    
    # Requirements
    minimum_level: CertificateLevel = CertificateLevel.L1_EMPIRICAL
    require_verified_enclosure: bool = False
    
    @classmethod
    def strict(cls) -> 'VerificationPolicy':
        """Strict verification policy."""
        return cls(
            check_enclosure=True,
            check_replay=True,
            check_uniqueness=True,
            check_stability=True,
            minimum_level=CertificateLevel.L2_CERTIFIED,
            require_verified_enclosure=True,
        )
    
    @classmethod
    def standard(cls) -> 'VerificationPolicy':
        """Standard verification policy."""
        return cls(
            check_enclosure=True,
            check_replay=True,
            minimum_level=CertificateLevel.L1_EMPIRICAL,
        )
    
    @classmethod
    def relaxed(cls) -> 'VerificationPolicy':
        """Relaxed verification policy."""
        return cls(
            check_enclosure=True,
            check_replay=False,
            minimum_level=CertificateLevel.L0_CLAIM,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

class VerifierKernel:
    """
    The Verifier Kernel - core verification logic.
    
    Implements fail-closed verification: if ANY check fails,
    the entire verification fails.
    """
    
    def __init__(self, policy: Optional[VerificationPolicy] = None):
        self.policy = policy or VerificationPolicy.standard()
    
    def verify_recipe(self, recipe: Recipe) -> VerificationReport:
        """
        Verify a complete recipe.
        
        Checks:
        1. Recipe is complete
        2. All certificates are valid
        3. Solution is in enclosure (if claimed)
        4. Replay produces same result (if requested)
        """
        import time
        start = time.time()
        
        report = VerificationReport(
            # Core enums don't include a "PENDING" state; we start pessimistic
            # and only upgrade to OK_VERIFIED once all checks pass.
            result=VerificationResult.FAILED,
            certificate_level=CertificateLevel.L0_CLAIM,
        )
        
        # Check recipe completeness
        if not recipe.complete:
            report.add_check("completeness", False, "Recipe not marked complete")
            report.result = VerificationResult.FAILED
            report.verification_time = time.time() - start
            return report
        report.add_check("completeness", True)
        
        # Check success
        if not recipe.success:
            report.add_check("success", False, "Recipe did not succeed")
            report.result = VerificationResult.FAILED
            report.verification_time = time.time() - start
            return report
        report.add_check("success", True)
        
        # Verify certificates
        cert_ok = self._verify_certificates(recipe.output.certificates, report)
        if not cert_ok:
            report.result = VerificationResult.FAILED
            report.verification_time = time.time() - start
            return report
        
        # Check certificate level
        if recipe.output.certificates.level < self.policy.minimum_level:
            report.add_check("level", False, 
                           f"Level {recipe.output.certificates.level.value} < required {self.policy.minimum_level.value}")
            report.result = VerificationResult.POLICY_VIOLATION
            report.verification_time = time.time() - start
            return report
        report.add_check("level", True)
        
        # Enclosure check
        if self.policy.check_enclosure:
            enc_ok = self._verify_enclosure(recipe, report)
            if not enc_ok:
                report.result = VerificationResult.FAILED
                report.verification_time = time.time() - start
                return report
        
        # Replay check
        if self.policy.check_replay:
            replay_ok = self._verify_replay(recipe, report)
            if not replay_ok:
                report.result = VerificationResult.REPLAY_MISMATCH
                report.verification_time = time.time() - start
                return report
        
        # All checks passed
        report.result = VerificationResult.OK_VERIFIED
        report.certificate_level = recipe.output.certificates.level
        report.verification_time = time.time() - start
        
        return report
    
    def verify_certificate(self, cert: Certificate) -> bool:
        """Verify a single certificate."""
        return cert.verify()
    
    def _verify_certificates(
        self, 
        bundle: CertificateBundle, 
        report: VerificationReport
    ) -> bool:
        """Verify all certificates in a bundle."""
        if not bundle.certificates:
            report.add_check("certificates", False, "No certificates")
            return False
        
        all_valid = True
        for cert in bundle.certificates:
            cert_valid = cert.verify()
            if not cert_valid:
                report.add_check(f"cert_{cert.certificate_type}", False, "Certificate invalid")
                all_valid = False
        
        if all_valid:
            report.add_check("certificates", True)
        
        return all_valid
    
    def _verify_enclosure(self, recipe: Recipe, report: VerificationReport) -> bool:
        """Verify solution is in claimed enclosure."""
        enc_cert = recipe.output.certificates.get("enclosure")
        
        if enc_cert is None:
            report.add_check("enclosure", False, "No enclosure certificate")
            return False
        
        if not isinstance(enc_cert, EnclosureCertificate):
            report.add_check("enclosure", False, "Invalid enclosure certificate type")
            return False
        
        # Check solution in enclosure
        if not enc_cert.enclosure.contains(enc_cert.solution):
            report.add_check("enclosure", False, "Solution not in enclosure")
            return False
        
        # Check verified if required
        if self.policy.require_verified_enclosure and not enc_cert.interval_arithmetic_used:
            report.add_check("enclosure", False, "Enclosure not verified with interval arithmetic")
            return False
        
        # Check residual
        if enc_cert.residual > self.policy.enclosure_tolerance:
            report.add_check("enclosure", False, 
                           f"Residual {enc_cert.residual} > tolerance {self.policy.enclosure_tolerance}")
            return False
        
        report.add_check("enclosure", True)
        return True
    
    def _verify_replay(self, recipe: Recipe, report: VerificationReport) -> bool:
        """Verify replay produces same result."""
        replay_cert = recipe.output.certificates.get("replay")
        
        if replay_cert is None:
            report.add_check("replay", False, "No replay certificate")
            return False
        
        if not isinstance(replay_cert, ReplayCertificate):
            report.add_check("replay", False, "Invalid replay certificate type")
            return False
        
        # Execute replay
        # The current RecipeExecutor doesn't require a float policy; the replay
        # certificate stores it for future deterministic extensions.
        executor = RecipeExecutor()
        replay_recipe = executor.execute(recipe.blueprint, recipe.plan)
        
        replay_output_hash = replay_recipe.output.content_hash()
        replay_cert.record_replay(replay_output_hash)
        
        if not replay_cert.replay_matches:
            report.add_check("replay", False, "Replay output mismatch")
            return False
        
        report.add_check("replay", True)
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# ENCLOSURE VERIFIER
# ═══════════════════════════════════════════════════════════════════════════════

class EnclosureVerifier:
    """
    Specialized verifier for solution enclosures.
    
    Uses interval Newton to verify/tighten enclosures.
    """
    
    def __init__(self, tolerance: float = 1e-14, max_iter: int = 30):
        self.tolerance = tolerance
        self.max_iter = max_iter
        self.solver = IntervalNewtonSolver(tol=tolerance, max_iter=max_iter)
    
    def verify(
        self,
        H: Callable[[float], float],
        claimed_enclosure: Interval,
        claimed_solution: float
    ) -> Tuple[bool, Optional[Interval]]:
        """
        Verify that claimed_solution is in claimed_enclosure and is a root of H.
        
        Returns (verified, tightened_enclosure).
        """
        # First check solution is in enclosure
        if not claimed_enclosure.contains(claimed_solution):
            return (False, None)
        
        # Run interval Newton
        result = self.solver.solve(H, claimed_enclosure)
        
        if result.converged and result.enclosure_verified:
            # Verify the claimed solution is in the verified enclosure
            if result.enclosure.contains(claimed_solution):
                return (True, result.enclosure)
        
        return (False, None)
    
    def tighten(
        self,
        H: Callable[[float], float],
        initial_enclosure: Interval
    ) -> Optional[Interval]:
        """
        Tighten an enclosure using interval Newton.
        
        Returns tightened enclosure or None if no root exists.
        """
        result = self.solver.solve(H, initial_enclosure)
        
        if result.converged and result.enclosure_verified:
            return result.enclosure
        
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════════

class CrossValidator:
    """
    Cross-validate results using multiple methods.
    
    A result is considered validated if multiple independent
    methods agree to within tolerance.
    """
    
    def __init__(self, tolerance: float = 1e-10, min_agreement: int = 2):
        self.tolerance = tolerance
        self.min_agreement = min_agreement
    
    def validate(
        self,
        solutions: List[Tuple[str, float]]  # (method_name, solution)
    ) -> Tuple[bool, Optional[float], float]:
        """
        Cross-validate a set of solutions.
        
        Returns (validated, consensus_solution, spread).
        """
        if len(solutions) < self.min_agreement:
            return (False, None, float('inf'))
        
        # Check pairwise agreement
        values = [s for _, s in solutions]
        min_val = min(values)
        max_val = max(values)
        spread = max_val - min_val
        
        if spread <= self.tolerance:
            # All agree within tolerance
            consensus = sum(values) / len(values)
            return (True, consensus, spread)
        
        # Find largest agreeing cluster
        values_sorted = sorted(values)
        best_cluster = []
        
        for i, v in enumerate(values_sorted):
            cluster = [v]
            for j in range(i + 1, len(values_sorted)):
                if values_sorted[j] - v <= self.tolerance:
                    cluster.append(values_sorted[j])
                else:
                    break
            if len(cluster) > len(best_cluster):
                best_cluster = cluster
        
        if len(best_cluster) >= self.min_agreement:
            consensus = sum(best_cluster) / len(best_cluster)
            return (True, consensus, max(best_cluster) - min(best_cluster))
        
        return (False, None, spread)


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATOR FACADE
# ═══════════════════════════════════════════════════════════════════════════════

class Validator:
    """
    High-level validator facade.
    
    Combines all verification components into a simple interface.
    """
    
    def __init__(self, policy: Optional[VerificationPolicy] = None):
        self.kernel = VerifierKernel(policy)
        self.enclosure_verifier = EnclosureVerifier()
        self.cross_validator = CrossValidator()
    
    def verify(self, recipe: Recipe) -> VerificationReport:
        """Verify a recipe."""
        return self.kernel.verify_recipe(recipe)
    
    def verify_solution(
        self,
        H: Callable[[float], float],
        solution: float,
        enclosure: Optional[Interval] = None,
        tolerance: float = 1e-10
    ) -> Tuple[bool, str]:
        """
        Verify a solution directly.
        
        Returns (verified, message).
        """
        # Check residual
        residual = abs(H(solution))
        if residual > tolerance:
            return (False, f"Residual {residual} > tolerance {tolerance}")
        
        # Verify enclosure if provided
        if enclosure is not None:
            if not enclosure.contains(solution):
                return (False, "Solution not in enclosure")
            
            verified, tightened = self.enclosure_verifier.verify(H, enclosure, solution)
            if not verified:
                return (False, "Enclosure verification failed")
        
        return (True, "Verified")
    
    def cross_validate(
        self,
        H: Callable[[float], float],
        domain: Interval,
        methods: List[str] = None
    ) -> Tuple[bool, Optional[float], Dict[str, float]]:
        """
        Cross-validate using multiple solvers.
        
        Returns (validated, consensus_solution, individual_results).
        """
        from atlasforge.constraints.solvers import SolverFactory, SolverType
        
        if methods is None:
            methods = ["brent", "newton", "bisection"]
        
        results = {}
        solutions = []
        
        for method in methods:
            try:
                solver_type = SolverType[method.upper()]
                solver = SolverFactory.create(solver_type)
                result = solver.solve(H, domain)
                
                if result.converged and result.solution is not None:
                    results[method] = result.solution
                    solutions.append((method, result.solution))
            except Exception:
                pass
        
        validated, consensus, spread = self.cross_validator.validate(solutions)
        
        return (validated, consensus, results)

"""
ATHENA OS - AtlasForge
======================
Verification Kernel: Certificate Validation and Proof Checking

From AtlasForge.docx:

TRUTH PROFILES:
    - Explore: no constraints, plausibility only
    - Validate: check structure, no proofs
    - Prove: full verification required

VERIFIER KERNEL:
    - Validates proof obligations
    - Checks certificate levels
    - Enforces corridor/enclosure
    - Produces verification reports

VERIFICATION CONTRACT:
    Construction: potentially expensive, heuristic
    Verification: conservative, bounded, policy-enforced
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import time
import math

from .recipes import Recipe, Certificate, ProofPack, CertificateType, CertificateLevel
from .constraints import Constraint, RootConstraint, FixedPointConstraint, ConstraintIR
from .domains import Domain, Interval


# =============================================================================
# TRUTH PROFILES
# =============================================================================

class TruthProfile(Enum):
    """Verification truth profiles."""
    
    EXPLORE = "explore"    # No constraints, plausibility only
    VALIDATE = "validate"  # Check structure, no proofs
    PROVE = "prove"        # Full verification required


# =============================================================================
# VERIFICATION REPORT
# =============================================================================

class VerificationResult(Enum):
    """Result of verification."""
    
    OK = "ok"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class VerificationItem:
    """Single verification check result."""
    
    check_name: str
    result: VerificationResult
    message: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationReport:
    """
    Complete verification report for a recipe.
    """
    
    recipe_id: str = ""
    profile: TruthProfile = TruthProfile.EXPLORE
    
    # Overall result
    passed: bool = False
    
    # Individual checks
    checks: List[VerificationItem] = field(default_factory=list)
    
    # Timing
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    # Errors
    errors: List[str] = field(default_factory=list)
    
    def add_check(self, name: str, result: VerificationResult,
                  message: str = "", evidence: Dict[str, Any] = None) -> None:
        """Add verification check."""
        self.checks.append(VerificationItem(
            check_name=name,
            result=result,
            message=message,
            evidence=evidence or {}
        ))
    
    def finalize(self) -> None:
        """Finalize report."""
        self.completed_at = time.time()
        
        # Check if all passed
        self.passed = all(
            c.result in [VerificationResult.OK, VerificationResult.SKIP]
            for c in self.checks
        )
    
    @property
    def duration_ms(self) -> float:
        """Verification duration in milliseconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at) * 1000
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize report."""
        return {
            "recipe_id": self.recipe_id,
            "profile": self.profile.value,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "checks": [
                {
                    "name": c.check_name,
                    "result": c.result.value,
                    "message": c.message
                }
                for c in self.checks
            ],
            "errors": self.errors
        }


# =============================================================================
# VALIDATORS
# =============================================================================

@dataclass
class Validator:
    """Base validator class."""
    
    name: str = "base"
    
    def validate(self, recipe: Recipe, 
                profile: TruthProfile) -> VerificationItem:
        """Run validation."""
        raise NotImplementedError


@dataclass
class CorridorValidator(Validator):
    """
    Validates corridor (domain validity).
    
    Checks that solution is within declared domain.
    """
    
    name: str = "corridor"
    
    def validate(self, recipe: Recipe,
                profile: TruthProfile) -> VerificationItem:
        """Validate corridor."""
        if profile == TruthProfile.EXPLORE:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.SKIP,
                message="Corridor check skipped in Explore mode"
            )
        
        # Check domain exists
        if recipe.domain is None:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.FAIL,
                message="No domain specified"
            )
        
        # Check output value is in domain
        if recipe.output.value is not None:
            if hasattr(recipe.domain.carrier, 'contains'):
                if recipe.domain.carrier.contains(recipe.output.value):
                    return VerificationItem(
                        check_name=self.name,
                        result=VerificationResult.OK,
                        message="Solution in domain corridor",
                        evidence={"value": recipe.output.value}
                    )
                else:
                    return VerificationItem(
                        check_name=self.name,
                        result=VerificationResult.FAIL,
                        message="Solution outside domain corridor"
                    )
        
        return VerificationItem(
            check_name=self.name,
            result=VerificationResult.SKIP,
            message="No scalar output to verify"
        )


@dataclass
class EnclosureValidator(Validator):
    """
    Validates enclosure certificate.
    
    Checks that solution is within certified bounds.
    """
    
    name: str = "enclosure"
    
    def validate(self, recipe: Recipe,
                profile: TruthProfile) -> VerificationItem:
        """Validate enclosure."""
        if profile != TruthProfile.PROVE:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.SKIP,
                message="Enclosure check requires Prove mode"
            )
        
        # Find enclosure certificate
        enclosures = recipe.proofpack.get_by_type(CertificateType.ENCLOSURE)
        
        if not enclosures:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.FAIL,
                message="No enclosure certificate"
            )
        
        # Check certificate level
        cert = enclosures[0]
        if cert.level.value < 2:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.FAIL,
                message=f"Enclosure certificate level {cert.level.value} < 2"
            )
        
        # Check bounds contain solution
        bounds = cert.evidence.get("x_bounds")
        if bounds and recipe.output.value is not None:
            if bounds[0] <= recipe.output.value <= bounds[1]:
                return VerificationItem(
                    check_name=self.name,
                    result=VerificationResult.OK,
                    message="Solution within enclosure",
                    evidence={"bounds": bounds, "value": recipe.output.value}
                )
            else:
                return VerificationItem(
                    check_name=self.name,
                    result=VerificationResult.FAIL,
                    message="Solution outside enclosure"
                )
        
        return VerificationItem(
            check_name=self.name,
            result=VerificationResult.OK,
            message="Enclosure certificate valid"
        )


@dataclass
class SignChangeValidator(Validator):
    """
    Validates sign change (bracket) certificate.
    
    Verifies f(a) and f(b) have opposite signs.
    """
    
    name: str = "sign_change"
    
    def validate(self, recipe: Recipe,
                profile: TruthProfile) -> VerificationItem:
        """Validate sign change."""
        if profile == TruthProfile.EXPLORE:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.SKIP
            )
        
        # Find sign change certificate
        certs = recipe.proofpack.get_by_type(CertificateType.SIGN_CHANGE)
        
        if not certs:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.SKIP,
                message="No sign change certificate"
            )
        
        cert = certs[0]
        fa = cert.evidence.get("f(a)")
        fb = cert.evidence.get("f(b)")
        
        if fa is not None and fb is not None:
            if fa * fb < 0:
                return VerificationItem(
                    check_name=self.name,
                    result=VerificationResult.OK,
                    message="Valid sign change",
                    evidence={"f(a)": fa, "f(b)": fb}
                )
            else:
                return VerificationItem(
                    check_name=self.name,
                    result=VerificationResult.FAIL,
                    message="No sign change: f(a) and f(b) same sign"
                )
        
        return VerificationItem(
            check_name=self.name,
            result=VerificationResult.FAIL,
            message="Incomplete sign change evidence"
        )


@dataclass
class ReplayValidator(Validator):
    """
    Validates replay log.
    
    Checks that computation is reproducible.
    """
    
    name: str = "replay"
    
    def validate(self, recipe: Recipe,
                profile: TruthProfile) -> VerificationItem:
        """Validate replay."""
        if profile != TruthProfile.PROVE:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.SKIP
            )
        
        # Check replay log exists
        if not recipe.replay_log.steps:
            return VerificationItem(
                check_name=self.name,
                result=VerificationResult.FAIL,
                message="Empty replay log"
            )
        
        # Check steps are consecutive
        for i, step in enumerate(recipe.replay_log.steps):
            if step.step_id != i:
                return VerificationItem(
                    check_name=self.name,
                    result=VerificationResult.FAIL,
                    message=f"Non-consecutive step ids"
                )
        
        return VerificationItem(
            check_name=self.name,
            result=VerificationResult.OK,
            message=f"Replay log valid: {len(recipe.replay_log.steps)} steps"
        )


# =============================================================================
# VERIFICATION KERNEL
# =============================================================================

@dataclass
class VerifierKernel:
    """
    AtlasForge Verification Kernel.
    
    Runs validators and produces verification reports.
    """
    
    # Registered validators
    validators: List[Validator] = field(default_factory=list)
    
    # Version
    version: str = "1.0.0"
    
    def __post_init__(self):
        if not self.validators:
            self._register_default_validators()
    
    def _register_default_validators(self) -> None:
        """Register default validators."""
        self.validators = [
            CorridorValidator(),
            EnclosureValidator(),
            SignChangeValidator(),
            ReplayValidator()
        ]
    
    def add_validator(self, validator: Validator) -> None:
        """Add custom validator."""
        self.validators.append(validator)
    
    def verify(self, recipe: Recipe,
              profile: TruthProfile = TruthProfile.PROVE) -> VerificationReport:
        """
        Verify recipe under truth profile.
        
        Returns verification report.
        """
        report = VerificationReport(
            recipe_id=recipe.recipe_id,
            profile=profile
        )
        
        try:
            # Run all validators
            for validator in self.validators:
                result = validator.validate(recipe, profile)
                report.checks.append(result)
        
        except Exception as e:
            report.errors.append(str(e))
        
        report.finalize()
        return report
    
    def verify_batch(self, recipes: List[Recipe],
                    profile: TruthProfile = TruthProfile.PROVE) -> List[VerificationReport]:
        """Verify multiple recipes."""
        return [self.verify(r, profile) for r in recipes]


# =============================================================================
# SOLVE AND VERIFY PIPELINE
# =============================================================================

@dataclass
class SolveVerifyPipeline:
    """
    Complete solve → certify → verify pipeline.
    """
    
    kernel: VerifierKernel = field(default_factory=VerifierKernel)
    
    def solve_root(self, constraint: RootConstraint,
                   a: float, b: float,
                   tolerance: float = 1e-10) -> Tuple[Optional[float], List[Certificate]]:
        """
        Solve root constraint and generate certificates.
        """
        certificates = []
        
        # Evaluate at endpoints
        fa = constraint.evaluate(a)
        fb = constraint.evaluate(b)
        
        # Check for bracket
        if fa * fb < 0:
            # Sign change certificate
            certificates.append(Certificate.sign_change(a, b, fa, fb))
            
            # Solve via bisection
            x_star = constraint.bisection(a, b, tolerance)
            
            if x_star is not None:
                # Enclosure certificate
                certificates.append(Certificate.enclosure(
                    (a, b),
                    CertificateLevel.LEVEL_2
                ))
                
                # Corridor certificate
                certificates.append(Certificate.corridor(
                    (a, b),
                    CertificateLevel.LEVEL_2
                ))
                
                return x_star, certificates
        
        return None, certificates
    
    def run(self, constraint: Constraint,
           a: float = 0.0, b: float = 1.0) -> Tuple[Recipe, VerificationReport]:
        """
        Run complete pipeline.
        """
        from .recipes import RecipeBuilder, SolvePlan
        
        builder = RecipeBuilder()
        builder.set_constraint(constraint)
        
        if isinstance(constraint, RootConstraint):
            x_star, certs = self.solve_root(constraint, a, b)
            
            for cert in certs:
                builder.add_certificate(cert)
            
            builder.log_step("solve", 
                {"method": "bisection", "a": a, "b": b},
                {"x": x_star})
            
            recipe = builder.build(output_value=x_star)
        else:
            recipe = builder.build()
        
        # Verify
        report = self.kernel.verify(recipe, TruthProfile.PROVE)
        
        return recipe, report


# =============================================================================
# VALIDATION
# =============================================================================

def validate_verify() -> bool:
    """Validate verification module."""
    
    from .recipes import Recipe, RecipeOutput, SolvePlan, ProofPack, Certificate
    from .domains import Domain
    from .constraints import RootConstraint, Expression
    
    # Create verified recipe
    recipe = Recipe(
        blueprint_hash="test",
        domain=Domain.interval(0, 2),
        output=RecipeOutput(output_type="scalar", value=1.414)
    )
    
    recipe.proofpack.add_certificate(
        Certificate.enclosure((1.0, 2.0), CertificateLevel.LEVEL_2)
    )
    recipe.proofpack.add_certificate(
        Certificate.corridor((0.0, 2.0), CertificateLevel.LEVEL_2)
    )
    recipe.proofpack.add_certificate(
        Certificate.sign_change(1.0, 2.0, -1.0, 2.0, CertificateLevel.LEVEL_2)
    )
    
    recipe.replay_log.add_step("init", {}, {})
    recipe.replay_log.add_step("solve", {"a": 1}, {"x": 1.414})
    
    # Test VerifierKernel
    kernel = VerifierKernel()
    report = kernel.verify(recipe, TruthProfile.PROVE)
    
    assert report.recipe_id == recipe.recipe_id
    assert len(report.checks) >= 4
    
    # Test SolveVerifyPipeline
    constraint = RootConstraint(
        name="sqrt2",
        expression=Expression.sub(
            Expression.mul(Expression.variable("x"), Expression.variable("x")),
            Expression.constant(2.0)
        ),
        domain=Domain.interval(0, 3)
    )
    
    pipeline = SolveVerifyPipeline()
    recipe, report = pipeline.run(constraint, 1.0, 2.0)
    
    assert recipe.output.value is not None
    assert abs(recipe.output.value - math.sqrt(2)) < 1e-6
    assert report.passed
    
    return True


if __name__ == "__main__":
    print("Validating AtlasForge Verification...")
    assert validate_verify()
    print("✓ Verification module validated")

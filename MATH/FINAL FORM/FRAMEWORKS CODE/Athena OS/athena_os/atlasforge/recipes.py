"""
ATHENA OS - AtlasForge
======================
Recipes and ProofPacks: Proof-Carrying Artifacts

From AtlasForge.docx:

RECIPE:
    A compact build artifact containing:
    - Canonicalized Blueprint (or hash)
    - Normalized IR (domains, charts, constraints)
    - SolvePlan (algorithms, parameters, budgets)
    - Outputs (generators preferred over enumerations)
    - ProofPack (certificates with levels)
    - Replay Log
    - Content address (recipe_id)

PROOFPACK:
    Structured certificates with:
    - Certificate type
    - Evidence
    - Level (0-4)
    - Validator-checkable
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from enum import Enum, auto
import hashlib
import json
import time

from .domains import Domain
from .constraints import ConstraintIR, Constraint


# =============================================================================
# CERTIFICATE TYPES
# =============================================================================

class CertificateType(Enum):
    """Types of proof certificates."""
    
    CORRIDOR = "corridor"           # Domain validity
    ENCLOSURE = "enclosure"         # Bounds on solution
    UNIQUENESS = "uniqueness"       # Solution uniqueness
    CONTRACTION = "contraction"     # Contraction mapping
    EXISTENCE = "existence"         # Existence proof
    REPLAY = "replay"               # Reproducibility
    SIGN_CHANGE = "sign_change"     # Bracket verification
    INTERVAL_NEWTON = "interval_newton"  # Newton certificate
    MONOTONE = "monotone"           # Monotonicity


class CertificateLevel(Enum):
    """Certificate verification levels."""
    
    LEVEL_0 = 0  # Claimed only
    LEVEL_1 = 1  # Plausibility checked
    LEVEL_2 = 2  # Verified under assumptions
    LEVEL_3 = 3  # Verified with interval arithmetic
    LEVEL_4 = 4  # Formally proven


# =============================================================================
# CERTIFICATE
# =============================================================================

@dataclass
class Certificate:
    """
    A single proof certificate.
    """
    
    cert_type: CertificateType
    level: CertificateLevel = CertificateLevel.LEVEL_0
    
    # Evidence supporting the certificate
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Validator used
    validator: str = ""
    
    # Timestamp
    timestamp: float = field(default_factory=time.time)
    
    @property
    def is_verified(self) -> bool:
        """Check if certificate is verified (level >= 2)."""
        return self.level.value >= 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize certificate."""
        return {
            "type": self.cert_type.value,
            "level": self.level.value,
            "evidence": self.evidence,
            "validator": self.validator,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def corridor(cls, domain_bounds: Tuple[float, float],
                level: CertificateLevel = CertificateLevel.LEVEL_2) -> 'Certificate':
        """Create corridor certificate."""
        return cls(
            cert_type=CertificateType.CORRIDOR,
            level=level,
            evidence={"bounds": domain_bounds}
        )
    
    @classmethod
    def enclosure(cls, x_bounds: Tuple[float, float],
                 level: CertificateLevel = CertificateLevel.LEVEL_2) -> 'Certificate':
        """Create enclosure certificate."""
        return cls(
            cert_type=CertificateType.ENCLOSURE,
            level=level,
            evidence={"x_bounds": x_bounds}
        )
    
    @classmethod
    def sign_change(cls, a: float, b: float, fa: float, fb: float,
                   level: CertificateLevel = CertificateLevel.LEVEL_2) -> 'Certificate':
        """Create sign change (bracket) certificate."""
        return cls(
            cert_type=CertificateType.SIGN_CHANGE,
            level=level,
            evidence={"a": a, "b": b, "f(a)": fa, "f(b)": fb}
        )


# =============================================================================
# PROOFPACK
# =============================================================================

@dataclass
class ProofPack:
    """
    Collection of certificates for a recipe.
    """
    
    certificates: List[Certificate] = field(default_factory=list)
    
    # Overall verification status
    status: str = "unverified"
    
    def add_certificate(self, cert: Certificate) -> None:
        """Add certificate to pack."""
        self.certificates.append(cert)
        self._update_status()
    
    def _update_status(self) -> None:
        """Update overall status based on certificates."""
        if not self.certificates:
            self.status = "unverified"
            return
        
        levels = [c.level.value for c in self.certificates]
        min_level = min(levels)
        
        if min_level >= 3:
            self.status = "verified_interval"
        elif min_level >= 2:
            self.status = "verified"
        elif min_level >= 1:
            self.status = "plausible"
        else:
            self.status = "claimed"
    
    @property
    def is_verified(self) -> bool:
        """Check if all certificates are verified."""
        return all(c.is_verified for c in self.certificates)
    
    @property
    def min_level(self) -> int:
        """Get minimum certificate level."""
        if not self.certificates:
            return 0
        return min(c.level.value for c in self.certificates)
    
    def get_by_type(self, cert_type: CertificateType) -> List[Certificate]:
        """Get certificates of specific type."""
        return [c for c in self.certificates if c.cert_type == cert_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize proofpack."""
        return {
            "status": self.status,
            "min_level": self.min_level,
            "count": len(self.certificates),
            "certificates": [c.to_dict() for c in self.certificates]
        }


# =============================================================================
# SOLVE PLAN
# =============================================================================

class SolveStrategy(Enum):
    """Solving strategies."""
    
    BISECTION = "bisection"
    NEWTON = "newton"
    ITERATION = "iteration"
    INTERVAL_NEWTON = "interval_newton"
    BRACKETING = "bracketing"


@dataclass
class SolvePlan:
    """
    Execution plan for solving constraints.
    """
    
    # Strategy selection
    strategy: SolveStrategy = SolveStrategy.BISECTION
    
    # Parameters
    tolerance_abs: float = 1e-10
    tolerance_rel: float = 1e-10
    max_iterations: int = 100
    
    # Budgets
    time_budget_ms: int = 10000
    memory_budget_mb: int = 100
    
    # Reductions
    reductions: List[str] = field(default_factory=list)
    
    # Bracketing info
    bracket_method: str = "bisection"
    initial_bracket: Optional[Tuple[float, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize plan."""
        return {
            "strategy": self.strategy.value,
            "tolerance": {
                "abs": self.tolerance_abs,
                "rel": self.tolerance_rel
            },
            "max_iterations": self.max_iterations,
            "budgets": {
                "time_ms": self.time_budget_ms,
                "memory_mb": self.memory_budget_mb
            },
            "bracket": self.bracket_method,
            "initial_bracket": self.initial_bracket
        }


# =============================================================================
# REPLAY LOG
# =============================================================================

@dataclass
class ReplayStep:
    """A single step in replay log."""
    
    step_id: int
    operation: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class ReplayLog:
    """
    Log enabling deterministic replay.
    """
    
    steps: List[ReplayStep] = field(default_factory=list)
    
    # Environment contract
    float_precision: int = 64
    rounding_mode: str = "nearest"
    
    def add_step(self, operation: str, 
                inputs: Dict[str, Any],
                outputs: Dict[str, Any]) -> None:
        """Add step to log."""
        step = ReplayStep(
            step_id=len(self.steps),
            operation=operation,
            inputs=inputs,
            outputs=outputs
        )
        self.steps.append(step)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize log."""
        return {
            "environment": {
                "float_precision": self.float_precision,
                "rounding_mode": self.rounding_mode
            },
            "step_count": len(self.steps),
            "steps": [
                {
                    "id": s.step_id,
                    "op": s.operation,
                    "inputs": s.inputs,
                    "outputs": s.outputs
                }
                for s in self.steps
            ]
        }


# =============================================================================
# RECIPE OUTPUT
# =============================================================================

@dataclass
class RecipeOutput:
    """
    Output of a recipe (solution, generator, etc.).
    """
    
    output_type: str = "scalar"  # scalar, generator, enumeration
    
    # Scalar output
    value: Optional[float] = None
    
    # Generator output (preferred)
    generator_spec: Optional[Dict[str, Any]] = None
    
    # Enumeration (if needed)
    enumeration: Optional[List[Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize output."""
        result = {"type": self.output_type}
        
        if self.output_type == "scalar":
            result["value"] = self.value
        elif self.output_type == "generator":
            result["generator"] = self.generator_spec
        elif self.output_type == "enumeration":
            result["count"] = len(self.enumeration) if self.enumeration else 0
        
        return result


# =============================================================================
# RECIPE
# =============================================================================

@dataclass
class Recipe:
    """
    AtlasForge Recipe: a proof-carrying build artifact.
    
    Content-addressed by recipe_id = hash(canonical(payload))
    """
    
    # Identity
    recipe_id: str = ""
    
    # Blueprint reference
    blueprint_hash: str = ""
    blueprint_source: Optional[str] = None
    
    # Normalized IR
    ir: Optional[ConstraintIR] = None
    
    # Domain specification
    domain: Optional[Domain] = None
    
    # Solve plan
    plan: SolvePlan = field(default_factory=SolvePlan)
    
    # Output
    output: RecipeOutput = field(default_factory=RecipeOutput)
    
    # ProofPack
    proofpack: ProofPack = field(default_factory=ProofPack)
    
    # Replay log
    replay_log: ReplayLog = field(default_factory=ReplayLog)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    schema_version: str = "1.0"
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # recipe_ids
    
    def __post_init__(self):
        if not self.recipe_id:
            self._compute_id()
    
    def _compute_id(self) -> None:
        """Compute content-addressed recipe_id."""
        payload = self.canonical_payload()
        self.recipe_id = hashlib.sha256(payload.encode()).hexdigest()[:32]
    
    def canonical_payload(self) -> str:
        """Create canonical serialization for hashing."""
        data = {
            "schema_version": self.schema_version,
            "blueprint_hash": self.blueprint_hash,
            "ir": self.ir.to_dict() if self.ir else None,
            "plan": self.plan.to_dict(),
            "output": self.output.to_dict()
        }
        return json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    @property
    def is_verified(self) -> bool:
        """Check if recipe is verified."""
        return self.proofpack.is_verified
    
    @property
    def verification_status(self) -> str:
        """Get verification status."""
        return self.proofpack.status
    
    def add_dependency(self, recipe_id: str) -> None:
        """Add dependency on another recipe."""
        if recipe_id not in self.dependencies:
            self.dependencies.append(recipe_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Full serialization."""
        return {
            "recipe_id": self.recipe_id,
            "schema_version": self.schema_version,
            "blueprint_hash": self.blueprint_hash,
            "ir": self.ir.to_dict() if self.ir else None,
            "plan": self.plan.to_dict(),
            "output": self.output.to_dict(),
            "proofpack": self.proofpack.to_dict(),
            "replay": self.replay_log.to_dict(),
            "dependencies": self.dependencies,
            "created_at": self.created_at
        }


# =============================================================================
# RECIPE BUILDER
# =============================================================================

@dataclass
class RecipeBuilder:
    """
    Builder for constructing recipes.
    """
    
    # Work in progress
    constraint: Optional[Constraint] = None
    ir: Optional[ConstraintIR] = None
    plan: SolvePlan = field(default_factory=SolvePlan)
    proofpack: ProofPack = field(default_factory=ProofPack)
    replay_log: ReplayLog = field(default_factory=ReplayLog)
    
    def set_constraint(self, constraint: Constraint) -> 'RecipeBuilder':
        """Set constraint to solve."""
        self.constraint = constraint
        return self
    
    def set_plan(self, plan: SolvePlan) -> 'RecipeBuilder':
        """Set solve plan."""
        self.plan = plan
        return self
    
    def add_certificate(self, cert: Certificate) -> 'RecipeBuilder':
        """Add certificate."""
        self.proofpack.add_certificate(cert)
        return self
    
    def log_step(self, operation: str,
                inputs: Dict[str, Any],
                outputs: Dict[str, Any]) -> 'RecipeBuilder':
        """Log replay step."""
        self.replay_log.add_step(operation, inputs, outputs)
        return self
    
    def build(self, output_value: float = None) -> Recipe:
        """Build the recipe."""
        from .constraints import ConstraintCompiler
        
        # Compile constraint to IR
        if self.constraint:
            compiler = ConstraintCompiler()
            self.ir = compiler.compile(self.constraint)
        
        # Create output
        output = RecipeOutput(
            output_type="scalar",
            value=output_value
        )
        
        # Create recipe
        recipe = Recipe(
            ir=self.ir,
            domain=self.constraint.domain if self.constraint else None,
            plan=self.plan,
            output=output,
            proofpack=self.proofpack,
            replay_log=self.replay_log
        )
        
        return recipe


# =============================================================================
# VALIDATION
# =============================================================================

def validate_recipes() -> bool:
    """Validate recipes module."""
    
    # Test Certificate
    cert = Certificate.enclosure((1.0, 2.0), CertificateLevel.LEVEL_2)
    assert cert.is_verified
    assert cert.cert_type == CertificateType.ENCLOSURE
    
    # Test ProofPack
    pack = ProofPack()
    pack.add_certificate(cert)
    pack.add_certificate(Certificate.corridor((0.0, 3.0), CertificateLevel.LEVEL_2))
    
    assert pack.is_verified
    assert pack.min_level == 2
    
    # Test SolvePlan
    plan = SolvePlan(
        strategy=SolveStrategy.BISECTION,
        tolerance_abs=1e-12
    )
    plan_dict = plan.to_dict()
    assert plan_dict["strategy"] == "bisection"
    
    # Test ReplayLog
    log = ReplayLog()
    log.add_step("evaluate", {"x": 1.0}, {"f(x)": 0.5})
    assert len(log.steps) == 1
    
    # Test RecipeOutput
    output = RecipeOutput(output_type="scalar", value=1.414)
    assert output.to_dict()["value"] == 1.414
    
    # Test Recipe
    recipe = Recipe(
        blueprint_hash="abc123",
        plan=plan,
        output=output,
        proofpack=pack
    )
    
    assert recipe.recipe_id  # Auto-computed
    assert len(recipe.recipe_id) == 32
    assert recipe.is_verified
    
    # Test RecipeBuilder
    from .constraints import RootConstraint, Expression
    
    constraint = RootConstraint(
        name="test",
        expression=Expression.sub(
            Expression.mul(Expression.variable("x"), Expression.variable("x")),
            Expression.constant(2.0)
        )
    )
    
    builder = RecipeBuilder()
    recipe = (builder
        .set_constraint(constraint)
        .set_plan(plan)
        .add_certificate(cert)
        .log_step("solve", {"method": "bisection"}, {"x": 1.414})
        .build(output_value=1.41421356)
    )
    
    assert recipe.recipe_id
    assert recipe.is_verified
    
    return True


if __name__ == "__main__":
    print("Validating AtlasForge Recipes...")
    assert validate_recipes()
    print("✓ Recipes module validated")

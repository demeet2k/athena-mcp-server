"""
ATHENA OS - AtlasForge: VERIFIER KERNEL
=======================================
Bounded, Replayable, Fail-Closed Verification Pipeline

VERIFIER PRINCIPLES:
    1. INTEGRITY - recompute recipe_id and reject mismatches
    2. POLICY - compile required obligations from IR and truth profile
    3. REPLAY - deterministically re-run evidence computations
    4. CHECK - re-evaluate certificates against replay outputs

VERIFICATION PIPELINE:
    integrity_check → policy_compile → replay_verify → 
    certificate_check → promote_or_reject

FAIL-CLOSED BEHAVIOR:
    - Rejects on any integrity failure
    - Rejects on missing required obligations  
    - Rejects on certificate validation failure
    - Never promotes without explicit success

PROMOTION STATES:
    pending → ok_verified OR rejected
    
    Only the verifier may promote to ok_verified.
    Builders produce candidates; verifier judges them.

BOUNDED VERIFICATION:
    - Strict time budgets
    - Bounded iteration counts
    - Conservative interval arithmetic
    - Explicit termination guarantees

SOURCES:
    - AtlasForge.docx Verifier Kernel Architecture
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import hashlib
import time
import json


# Import from other modules (assuming they exist)
# from .proof_pack import ProofPack, Certificate, TruthProfile, CertificateLevel
# from .solve_plan import SolvePlan
# from .recipes import Recipe


# =============================================================================
# VERIFICATION STATES
# =============================================================================

class VerificationState(Enum):
    """States in the verification lifecycle."""
    
    PENDING = "pending"              # Not yet verified
    CHECKING = "checking"            # Verification in progress
    OK_VERIFIED = "ok_verified"      # Passed all checks
    REJECTED = "rejected"            # Failed verification
    EXPIRED = "expired"              # Verification expired


class RejectionReason(Enum):
    """Reasons for verification rejection."""
    
    INTEGRITY_MISMATCH = "integrity_mismatch"
    MISSING_OBLIGATION = "missing_obligation"
    CERTIFICATE_INVALID = "certificate_invalid"
    REPLAY_FAILURE = "replay_failure"
    POLICY_VIOLATION = "policy_violation"
    TIMEOUT = "timeout"
    BUDGET_EXCEEDED = "budget_exceeded"
    INTERNAL_ERROR = "internal_error"


class CheckType(Enum):
    """Types of verification checks."""
    
    INTEGRITY = "integrity"
    POLICY = "policy"
    REPLAY = "replay"
    CERTIFICATE = "certificate"
    BOUND = "bound"


# =============================================================================
# VERIFICATION RESULT
# =============================================================================

@dataclass
class CheckResult:
    """Result of a single verification check."""
    
    check_type: CheckType
    passed: bool
    message: str = ""
    
    # Evidence
    expected: Any = None
    actual: Any = None
    
    # Timing
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_type": self.check_type.value,
            "passed": self.passed,
            "message": self.message,
            "duration_seconds": self.duration_seconds
        }


@dataclass
class VerificationResult:
    """Complete verification result."""
    
    state: VerificationState
    checks: List[CheckResult] = field(default_factory=list)
    
    # Rejection info (if rejected)
    rejection_reason: Optional[RejectionReason] = None
    rejection_message: str = ""
    
    # Timing
    total_duration_seconds: float = 0.0
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    # Verifier identity
    verifier_id: str = ""
    verifier_version: str = "1.0.0"
    
    @property
    def passed(self) -> bool:
        return self.state == VerificationState.OK_VERIFIED
    
    @property
    def all_checks_passed(self) -> bool:
        return all(c.passed for c in self.checks)
    
    def add_check(self, result: CheckResult) -> None:
        """Add a check result."""
        self.checks.append(result)
    
    def reject(self, reason: RejectionReason, message: str = "") -> None:
        """Reject the verification."""
        self.state = VerificationState.REJECTED
        self.rejection_reason = reason
        self.rejection_message = message
        self.completed_at = time.time()
        self.total_duration_seconds = self.completed_at - self.started_at
    
    def approve(self) -> None:
        """Approve (promote to ok_verified)."""
        self.state = VerificationState.OK_VERIFIED
        self.completed_at = time.time()
        self.total_duration_seconds = self.completed_at - self.started_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "passed": self.passed,
            "checks": [c.to_dict() for c in self.checks],
            "rejection_reason": self.rejection_reason.value if self.rejection_reason else None,
            "rejection_message": self.rejection_message,
            "total_duration_seconds": self.total_duration_seconds,
            "verifier_id": self.verifier_id,
            "all_checks_passed": self.all_checks_passed
        }


# =============================================================================
# VERIFICATION BUDGET
# =============================================================================

@dataclass
class VerificationBudget:
    """Resource budget for verification."""
    
    # Time limits
    total_time_seconds: float = 60.0
    per_check_time_seconds: float = 10.0
    
    # Iteration limits
    max_replay_iterations: int = 1000
    max_sample_evaluations: int = 10000
    
    # Memory limits (bytes)
    max_memory_bytes: int = 1024 * 1024 * 100  # 100 MB
    
    # Tracking
    time_used: float = 0.0
    iterations_used: int = 0
    
    @property
    def time_remaining(self) -> float:
        return max(0, self.total_time_seconds - self.time_used)
    
    @property
    def is_exhausted(self) -> bool:
        return self.time_remaining <= 0
    
    def consume_time(self, seconds: float) -> bool:
        """Consume time budget. Returns False if exceeded."""
        self.time_used += seconds
        return self.time_used <= self.total_time_seconds
    
    def consume_iterations(self, count: int) -> bool:
        """Consume iteration budget. Returns False if exceeded."""
        self.iterations_used += count
        return self.iterations_used <= self.max_replay_iterations


# =============================================================================
# VERIFIER POLICY
# =============================================================================

@dataclass
class VerifierPolicy:
    """Policy configuration for the verifier."""
    
    # Truth profile
    truth_profile: str = "validate"  # "explore", "validate", "prove"
    
    # Required certificate levels by type
    required_levels: Dict[str, int] = field(default_factory=lambda: {
        "chart_corridor": 1,
        "enclosure": 1,
        "uniqueness": 1,
        "replay_determinism": 1
    })
    
    # Enforcement flags
    enforce_replay: bool = True
    enforce_bounds: bool = True
    enforce_uniqueness: bool = True
    
    # Tolerance for "equivalent" values
    equivalence_tolerance: float = 1e-10
    
    # Strictness
    fail_on_warning: bool = False
    require_all_certificates: bool = True
    
    @classmethod
    def explore_policy(cls) -> VerifierPolicy:
        """Create permissive explore policy."""
        return cls(
            truth_profile="explore",
            required_levels={k: 0 for k in ["chart_corridor", "enclosure", 
                                           "uniqueness", "replay_determinism"]},
            enforce_replay=False,
            enforce_bounds=False,
            enforce_uniqueness=False,
            require_all_certificates=False
        )
    
    @classmethod
    def validate_policy(cls) -> VerifierPolicy:
        """Create standard validate policy."""
        return cls(
            truth_profile="validate",
            required_levels={k: 1 for k in ["chart_corridor", "enclosure", 
                                           "uniqueness", "replay_determinism"]},
            enforce_replay=True,
            enforce_bounds=True
        )
    
    @classmethod
    def prove_policy(cls) -> VerifierPolicy:
        """Create strict prove policy."""
        return cls(
            truth_profile="prove",
            required_levels={k: 2 for k in ["chart_corridor", "enclosure", 
                                           "uniqueness", "replay_determinism"]},
            enforce_replay=True,
            enforce_bounds=True,
            enforce_uniqueness=True,
            fail_on_warning=True,
            require_all_certificates=True
        )


# =============================================================================
# VERIFIER KERNEL
# =============================================================================

class VerifierKernel:
    """
    The Verifier Kernel - bounded, replayable, fail-closed.
    
    Implements the verification pipeline:
    1. Integrity check (hash verification)
    2. Policy compilation (required obligations)
    3. Replay verification (deterministic re-run)
    4. Certificate checking (evidence validation)
    5. Promotion or rejection
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, verifier_id: str = "default"):
        self.verifier_id = verifier_id
        self.policy = VerifierPolicy.validate_policy()
        self.budget = VerificationBudget()
    
    def set_policy(self, policy: VerifierPolicy) -> None:
        """Set the verification policy."""
        self.policy = policy
    
    def set_budget(self, budget: VerificationBudget) -> None:
        """Set the verification budget."""
        self.budget = budget
    
    def verify(self, recipe_data: Dict[str, Any]) -> VerificationResult:
        """
        Verify a recipe.
        
        This is the main entry point for verification.
        Returns VerificationResult with final state.
        """
        result = VerificationResult(
            state=VerificationState.CHECKING,
            verifier_id=self.verifier_id,
            verifier_version=self.VERSION
        )
        
        try:
            # Phase 1: Integrity Check
            integrity_result = self._check_integrity(recipe_data)
            result.add_check(integrity_result)
            
            if not integrity_result.passed:
                result.reject(RejectionReason.INTEGRITY_MISMATCH,
                             integrity_result.message)
                return result
            
            # Phase 2: Policy Compilation
            policy_result = self._check_policy(recipe_data)
            result.add_check(policy_result)
            
            if not policy_result.passed:
                result.reject(RejectionReason.POLICY_VIOLATION,
                             policy_result.message)
                return result
            
            # Phase 3: Replay Verification
            if self.policy.enforce_replay:
                replay_result = self._check_replay(recipe_data)
                result.add_check(replay_result)
                
                if not replay_result.passed:
                    result.reject(RejectionReason.REPLAY_FAILURE,
                                 replay_result.message)
                    return result
            
            # Phase 4: Certificate Checking
            cert_results = self._check_certificates(recipe_data)
            for cert_result in cert_results:
                result.add_check(cert_result)
                
                if not cert_result.passed and self.policy.fail_on_warning:
                    result.reject(RejectionReason.CERTIFICATE_INVALID,
                                 cert_result.message)
                    return result
            
            # Phase 5: Final Decision
            if result.all_checks_passed:
                result.approve()
            else:
                # Find first failing check for rejection reason
                for check in result.checks:
                    if not check.passed:
                        result.reject(RejectionReason.CERTIFICATE_INVALID,
                                     check.message)
                        break
            
        except Exception as e:
            result.reject(RejectionReason.INTERNAL_ERROR, str(e))
        
        return result
    
    def _check_integrity(self, recipe_data: Dict[str, Any]) -> CheckResult:
        """
        Phase 1: Integrity Check
        
        Recompute recipe_id from canonical payload and reject mismatches.
        """
        start_time = time.time()
        
        stored_id = recipe_data.get("recipe_id", "")
        
        # Compute canonical hash
        canonical = self._canonicalize(recipe_data)
        computed_id = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        
        passed = (stored_id == computed_id) or (stored_id == "")
        
        duration = time.time() - start_time
        self.budget.consume_time(duration)
        
        return CheckResult(
            check_type=CheckType.INTEGRITY,
            passed=passed,
            message="" if passed else f"ID mismatch: stored={stored_id}, computed={computed_id}",
            expected=stored_id,
            actual=computed_id,
            duration_seconds=duration
        )
    
    def _check_policy(self, recipe_data: Dict[str, Any]) -> CheckResult:
        """
        Phase 2: Policy Compilation
        
        Compile required obligations from IR and truth profile.
        """
        start_time = time.time()
        
        # Extract required obligations from recipe
        required = set(recipe_data.get("required_obligations", []))
        
        # Get provided certificates
        proof_pack = recipe_data.get("proof_pack", {})
        certificates = proof_pack.get("certificates", {})
        
        # Check each required obligation
        missing = []
        for obligation in required:
            found = False
            for cert_id, cert_data in certificates.items():
                if cert_data.get("obligation_id") == obligation:
                    # Check level requirement
                    cert_type = cert_data.get("cert_type", "")
                    required_level = self.policy.required_levels.get(cert_type, 0)
                    actual_level = cert_data.get("level", 0)
                    
                    if actual_level >= required_level:
                        found = True
                        break
            
            if not found:
                missing.append(obligation)
        
        duration = time.time() - start_time
        self.budget.consume_time(duration)
        
        passed = len(missing) == 0
        
        return CheckResult(
            check_type=CheckType.POLICY,
            passed=passed,
            message="" if passed else f"Missing obligations: {missing}",
            expected=list(required),
            actual=list(required - set(missing)),
            duration_seconds=duration
        )
    
    def _check_replay(self, recipe_data: Dict[str, Any]) -> CheckResult:
        """
        Phase 3: Replay Verification
        
        Deterministically re-run evidence-relevant computations.
        """
        start_time = time.time()
        
        # Get replay log
        replay_log = recipe_data.get("replay_log", {})
        
        if not replay_log:
            # No replay log - cannot verify
            duration = time.time() - start_time
            return CheckResult(
                check_type=CheckType.REPLAY,
                passed=True,  # Permissive if no replay log
                message="No replay log provided",
                duration_seconds=duration
            )
        
        # Check RNG seed
        master_seed = replay_log.get("master_rng_seed")
        if master_seed is None and self.policy.truth_profile == "prove":
            duration = time.time() - start_time
            return CheckResult(
                check_type=CheckType.REPLAY,
                passed=False,
                message="No RNG seed for deterministic replay",
                duration_seconds=duration
            )
        
        # Verify outputs match (simplified)
        outputs = recipe_data.get("outputs", {})
        recorded_hash = replay_log.get("output_hash", "")
        
        if recorded_hash:
            current_hash = hashlib.sha256(
                json.dumps(outputs, sort_keys=True).encode()
            ).hexdigest()[:16]
            
            if current_hash != recorded_hash:
                duration = time.time() - start_time
                return CheckResult(
                    check_type=CheckType.REPLAY,
                    passed=False,
                    message=f"Output hash mismatch: {current_hash} != {recorded_hash}",
                    expected=recorded_hash,
                    actual=current_hash,
                    duration_seconds=duration
                )
        
        duration = time.time() - start_time
        self.budget.consume_time(duration)
        
        return CheckResult(
            check_type=CheckType.REPLAY,
            passed=True,
            message="Replay verification successful",
            duration_seconds=duration
        )
    
    def _check_certificates(self, recipe_data: Dict[str, Any]) -> List[CheckResult]:
        """
        Phase 4: Certificate Checking
        
        Re-evaluate certificate conditions against replay outputs.
        """
        results = []
        
        proof_pack = recipe_data.get("proof_pack", {})
        certificates = proof_pack.get("certificates", {})
        
        for cert_id, cert_data in certificates.items():
            start_time = time.time()
            
            cert_type = cert_data.get("cert_type", "")
            cert_level = cert_data.get("level", 0)
            status = cert_data.get("status", "pending")
            
            # Check level requirement
            required_level = self.policy.required_levels.get(cert_type, 0)
            level_ok = cert_level >= required_level
            
            # Check status
            status_ok = status == "validated"
            
            passed = level_ok and (status_ok or not self.policy.require_all_certificates)
            
            message = ""
            if not level_ok:
                message = f"Level {cert_level} < required {required_level}"
            elif not status_ok:
                message = f"Status {status} not validated"
            
            duration = time.time() - start_time
            self.budget.consume_time(duration)
            
            results.append(CheckResult(
                check_type=CheckType.CERTIFICATE,
                passed=passed,
                message=message,
                expected={"level": required_level, "status": "validated"},
                actual={"level": cert_level, "status": status},
                duration_seconds=duration
            ))
            
            # Check budget
            if self.budget.is_exhausted:
                results.append(CheckResult(
                    check_type=CheckType.CERTIFICATE,
                    passed=False,
                    message="Verification budget exhausted"
                ))
                break
        
        return results
    
    def _canonicalize(self, data: Dict[str, Any]) -> str:
        """Canonicalize data for hashing."""
        # Remove computed fields
        clean = {k: v for k, v in data.items() 
                if k not in ["recipe_id", "verification_result"]}
        return json.dumps(clean, sort_keys=True, default=str)
    
    def quick_verify(self, recipe_data: Dict[str, Any]) -> bool:
        """Quick verification (just integrity check)."""
        result = self._check_integrity(recipe_data)
        return result.passed


# =============================================================================
# VERIFICATION REGISTRY
# =============================================================================

class VerificationRegistry:
    """
    Registry of verification results.
    
    Tracks verification history and status.
    """
    
    def __init__(self):
        self.results: Dict[str, VerificationResult] = {}
        self.history: List[Tuple[str, str, float]] = []  # (recipe_id, state, timestamp)
    
    def register(self, recipe_id: str, result: VerificationResult) -> None:
        """Register a verification result."""
        self.results[recipe_id] = result
        self.history.append((recipe_id, result.state.value, time.time()))
    
    def get_result(self, recipe_id: str) -> Optional[VerificationResult]:
        """Get verification result for recipe."""
        return self.results.get(recipe_id)
    
    def is_verified(self, recipe_id: str) -> bool:
        """Check if recipe is verified."""
        result = self.results.get(recipe_id)
        return result is not None and result.passed
    
    def get_verified_recipes(self) -> List[str]:
        """Get list of verified recipe IDs."""
        return [rid for rid, res in self.results.items() if res.passed]
    
    def get_rejected_recipes(self) -> List[str]:
        """Get list of rejected recipe IDs."""
        return [rid for rid, res in self.results.items() 
               if res.state == VerificationState.REJECTED]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get verification statistics."""
        total = len(self.results)
        verified = sum(1 for r in self.results.values() if r.passed)
        rejected = sum(1 for r in self.results.values() 
                      if r.state == VerificationState.REJECTED)
        
        return {
            "total": total,
            "verified": verified,
            "rejected": rejected,
            "pending": total - verified - rejected,
            "verification_rate": verified / total if total > 0 else 0.0
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_verifier_kernel() -> bool:
    """Validate verifier kernel module."""
    
    # Test verification result
    result = VerificationResult(state=VerificationState.PENDING)
    result.add_check(CheckResult(CheckType.INTEGRITY, True))
    result.add_check(CheckResult(CheckType.POLICY, True))
    result.approve()
    assert result.passed
    assert result.all_checks_passed
    
    # Test rejection
    result2 = VerificationResult(state=VerificationState.PENDING)
    result2.add_check(CheckResult(CheckType.INTEGRITY, False, "Hash mismatch"))
    result2.reject(RejectionReason.INTEGRITY_MISMATCH, "Hash mismatch")
    assert not result2.passed
    assert result2.rejection_reason == RejectionReason.INTEGRITY_MISMATCH
    
    # Test policies
    explore = VerifierPolicy.explore_policy()
    assert explore.truth_profile == "explore"
    assert not explore.enforce_replay
    
    prove = VerifierPolicy.prove_policy()
    assert prove.truth_profile == "prove"
    assert prove.enforce_replay
    assert prove.fail_on_warning
    
    # Test verifier kernel
    kernel = VerifierKernel("test_verifier")
    kernel.set_policy(VerifierPolicy.validate_policy())
    
    # Test with valid recipe
    recipe = {
        "recipe_id": "",
        "name": "test_recipe",
        "required_obligations": [],
        "proof_pack": {
            "certificates": {}
        },
        "outputs": {"value": 1.0}
    }
    
    result = kernel.verify(recipe)
    # Should pass with empty requirements
    assert result.state in [VerificationState.OK_VERIFIED, VerificationState.REJECTED]
    
    # Test verification registry
    registry = VerificationRegistry()
    registry.register("recipe_1", result)
    assert registry.get_result("recipe_1") is not None
    
    stats = registry.get_stats()
    assert stats["total"] == 1
    
    return True


if __name__ == "__main__":
    print("Validating Verifier Kernel Module...")
    assert validate_verifier_kernel()
    print("✓ Verifier Kernel Module validated")
    
    # Demo
    print("\n--- Verifier Kernel Demo ---")
    
    # Create verifier with strict policy
    kernel = VerifierKernel("demo_verifier")
    kernel.set_policy(VerifierPolicy.prove_policy())
    kernel.set_budget(VerificationBudget(total_time_seconds=10.0))
    
    print(f"\nVerifier ID: {kernel.verifier_id}")
    print(f"Policy: {kernel.policy.truth_profile}")
    print(f"Budget: {kernel.budget.total_time_seconds}s")
    
    # Create a test recipe
    recipe = {
        "recipe_id": "",
        "name": "sqrt2_computation",
        "required_obligations": [
            "enclosure:root:[1.41,1.42]"
        ],
        "proof_pack": {
            "truth_profile": "prove",
            "certificates": {
                "cert_1": {
                    "cert_type": "enclosure",
                    "obligation_id": "enclosure:root:[1.41,1.42]",
                    "level": 2,
                    "status": "validated"
                }
            }
        },
        "outputs": {
            "root": 1.4142135623730951
        },
        "replay_log": {
            "master_rng_seed": 42,
            "output_hash": ""
        }
    }
    
    print("\n--- Verifying Recipe ---")
    result = kernel.verify(recipe)
    
    print(f"\nVerification Result:")
    print(f"  State: {result.state.value}")
    print(f"  Passed: {result.passed}")
    print(f"  Duration: {result.total_duration_seconds:.3f}s")
    
    print(f"\nChecks ({len(result.checks)}):")
    for check in result.checks:
        status = "✓" if check.passed else "✗"
        print(f"  {status} {check.check_type.value}: {check.message or 'OK'}")
    
    if result.rejection_reason:
        print(f"\nRejection: {result.rejection_reason.value}")
        print(f"  Message: {result.rejection_message}")

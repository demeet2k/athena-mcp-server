"""
ATHENA OS - Verification Harness
================================
Crystal certificates and stress tests for governance verification.

From HYBRID_HOLO_LENSE.docx Appendix Q:
The verification harness provides:
1. Deterministic test suites for transforms
2. Path commutation tests
3. Residual decompositions
4. Acceptance thresholds

CERTIFICATE TYPES:
    DER     - Derived (formally proven)
    HEUR    - Heuristic (empirically supported)
    CONJ    - Conjecture (untested)
    AXIOM   - Assumed true

VERIFICATION PROTOCOL:
    1. Unit tests for basic correctness
    2. Property tests for invariants
    3. Stress tests for robustness
    4. Red-team tests for adversarial cases
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from datetime import datetime
import hashlib
import random


# =============================================================================
# CLAIM TYPES
# =============================================================================

class ClaimType(Enum):
    """Types of claims with different verification requirements."""
    DER = "DER"      # Derived - formally proven
    HEUR = "HEUR"    # Heuristic - empirically supported  
    CONJ = "CONJ"    # Conjecture - untested hypothesis
    AXIOM = "AXIOM"  # Axiom - assumed true


class TestResult(Enum):
    """Test result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


# =============================================================================
# TEST CASE
# =============================================================================

@dataclass
class TestCase:
    """A single test case."""
    
    id: str
    name: str
    description: str
    claim_type: ClaimType = ClaimType.HEUR
    
    # Test function
    test_fn: Optional[Callable[[], bool]] = None
    
    # Expected behavior
    expected_result: bool = True
    
    # Execution
    result: Optional[TestResult] = None
    error_message: str = ""
    execution_time_ms: float = 0.0
    
    def run(self) -> TestResult:
        """Execute the test."""
        import time
        start = time.time()
        
        try:
            if self.test_fn is None:
                self.result = TestResult.SKIP
                return self.result
            
            actual = self.test_fn()
            if actual == self.expected_result:
                self.result = TestResult.PASS
            else:
                self.result = TestResult.FAIL
                self.error_message = f"Expected {self.expected_result}, got {actual}"
        except Exception as e:
            self.result = TestResult.ERROR
            self.error_message = str(e)
        
        self.execution_time_ms = (time.time() - start) * 1000
        return self.result
    
    def passed(self) -> bool:
        """Check if test passed."""
        return self.result == TestResult.PASS


# =============================================================================
# TEST SUITE
# =============================================================================

@dataclass
class TestSuite:
    """A collection of test cases."""
    
    name: str
    description: str = ""
    cases: List[TestCase] = field(default_factory=list)
    
    def add_test(self, id: str, name: str, test_fn: Callable[[], bool],
                description: str = "", 
                claim_type: ClaimType = ClaimType.HEUR) -> TestCase:
        """Add a test case."""
        case = TestCase(
            id=id,
            name=name,
            description=description,
            claim_type=claim_type,
            test_fn=test_fn
        )
        self.cases.append(case)
        return case
    
    def run_all(self) -> Dict[str, int]:
        """Run all tests and return summary."""
        results = {
            TestResult.PASS: 0,
            TestResult.FAIL: 0,
            TestResult.SKIP: 0,
            TestResult.ERROR: 0
        }
        
        for case in self.cases:
            result = case.run()
            results[result] += 1
        
        return {k.value: v for k, v in results.items()}
    
    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return all(case.passed() for case in self.cases 
                  if case.result != TestResult.SKIP)
    
    def failures(self) -> List[TestCase]:
        """Get list of failed tests."""
        return [case for case in self.cases 
                if case.result in (TestResult.FAIL, TestResult.ERROR)]


# =============================================================================
# CERTIFICATE
# =============================================================================

@dataclass
class Certificate:
    """
    A verification certificate.
    
    Certificates attest to the validity of a claim.
    """
    
    cert_id: str
    claim: str
    claim_type: ClaimType
    
    # Evidence
    evidence: List[str] = field(default_factory=list)
    test_results: Dict[str, TestResult] = field(default_factory=dict)
    
    # Metadata
    issued_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    issuer: str = "athena_os"
    
    # Signature
    signature: str = ""
    
    def add_evidence(self, evidence: str) -> None:
        """Add evidence to certificate."""
        self.evidence.append(evidence)
    
    def add_test_result(self, test_id: str, result: TestResult) -> None:
        """Add test result."""
        self.test_results[test_id] = result
    
    def sign(self, issuer: str) -> None:
        """Sign the certificate."""
        self.issuer = issuer
        content = f"{self.cert_id}:{self.claim}:{self.issued_at.isoformat()}"
        self.signature = hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def verify_signature(self) -> bool:
        """Verify the certificate signature."""
        content = f"{self.cert_id}:{self.claim}:{self.issued_at.isoformat()}"
        expected = hashlib.sha256(content.encode()).hexdigest()[:32]
        return self.signature == expected
    
    def is_valid(self) -> bool:
        """Check if certificate is valid."""
        # Check expiration
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        
        # Check signature
        if not self.verify_signature():
            return False
        
        # Check test results (all must pass for DER claims)
        if self.claim_type == ClaimType.DER:
            if not all(r == TestResult.PASS for r in self.test_results.values()):
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "cert_id": self.cert_id,
            "claim": self.claim,
            "claim_type": self.claim_type.value,
            "evidence_count": len(self.evidence),
            "test_count": len(self.test_results),
            "tests_passed": sum(1 for r in self.test_results.values() 
                               if r == TestResult.PASS),
            "issued_at": self.issued_at.isoformat(),
            "issuer": self.issuer,
            "valid": self.is_valid(),
        }


# =============================================================================
# VERIFICATION HARNESS
# =============================================================================

@dataclass
class VerificationHarness:
    """
    The complete verification harness.
    
    Manages test suites, certificates, and verification protocols.
    """
    
    suites: Dict[str, TestSuite] = field(default_factory=dict)
    certificates: Dict[str, Certificate] = field(default_factory=dict)
    
    def add_suite(self, name: str, description: str = "") -> TestSuite:
        """Add a test suite."""
        suite = TestSuite(name=name, description=description)
        self.suites[name] = suite
        return suite
    
    def get_suite(self, name: str) -> Optional[TestSuite]:
        """Get a test suite by name."""
        return self.suites.get(name)
    
    def run_suite(self, name: str) -> Optional[Dict[str, int]]:
        """Run a test suite."""
        suite = self.suites.get(name)
        if suite:
            return suite.run_all()
        return None
    
    def run_all_suites(self) -> Dict[str, Dict[str, int]]:
        """Run all test suites."""
        return {name: suite.run_all() for name, suite in self.suites.items()}
    
    def issue_certificate(self, claim: str, claim_type: ClaimType,
                         suite_name: str) -> Optional[Certificate]:
        """
        Issue a certificate based on test suite results.
        """
        suite = self.suites.get(suite_name)
        if not suite:
            return None
        
        # Run tests
        suite.run_all()
        
        # Create certificate
        cert_id = hashlib.sha256(f"{claim}:{datetime.now()}".encode()).hexdigest()[:12]
        cert = Certificate(
            cert_id=cert_id,
            claim=claim,
            claim_type=claim_type
        )
        
        # Add test results
        for case in suite.cases:
            if case.result:
                cert.add_test_result(case.id, case.result)
        
        # Add evidence
        cert.add_evidence(f"Test suite '{suite_name}' executed")
        cert.add_evidence(f"Results: {suite.run_all()}")
        
        # Sign
        cert.sign("athena_os")
        
        self.certificates[cert_id] = cert
        return cert
    
    def verify_certificate(self, cert_id: str) -> bool:
        """Verify a certificate."""
        cert = self.certificates.get(cert_id)
        if cert:
            return cert.is_valid()
        return False
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of verification state."""
        return {
            "suites": len(self.suites),
            "total_tests": sum(len(s.cases) for s in self.suites.values()),
            "certificates": len(self.certificates),
            "valid_certificates": sum(1 for c in self.certificates.values() 
                                     if c.is_valid()),
        }


# =============================================================================
# STRESS TESTER
# =============================================================================

@dataclass
class StressTest:
    """
    Stress test for robustness verification.
    
    Tests behavior under adversarial conditions.
    """
    
    name: str
    iterations: int = 100
    perturbation_fn: Optional[Callable[[Any], Any]] = None
    check_fn: Optional[Callable[[Any, Any], bool]] = None
    
    # Results
    passed: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)
    
    def run(self, initial_state: Any) -> float:
        """
        Run stress test.
        
        Returns success rate (0-1).
        """
        self.passed = 0
        self.failed = 0
        self.errors = []
        
        if not self.perturbation_fn or not self.check_fn:
            return 0.0
        
        state = initial_state
        
        for i in range(self.iterations):
            try:
                # Perturb state
                perturbed = self.perturbation_fn(state)
                
                # Check invariant
                if self.check_fn(state, perturbed):
                    self.passed += 1
                else:
                    self.failed += 1
                
                state = perturbed
            except Exception as e:
                self.errors.append(f"Iteration {i}: {str(e)}")
                self.failed += 1
        
        return self.passed / self.iterations if self.iterations > 0 else 0.0


class StressTester:
    """Manager for stress tests."""
    
    def __init__(self):
        self.tests: Dict[str, StressTest] = {}
    
    def add_test(self, name: str, iterations: int,
                perturbation_fn: Callable[[Any], Any],
                check_fn: Callable[[Any, Any], bool]) -> StressTest:
        """Add a stress test."""
        test = StressTest(
            name=name,
            iterations=iterations,
            perturbation_fn=perturbation_fn,
            check_fn=check_fn
        )
        self.tests[name] = test
        return test
    
    def run_all(self, initial_states: Dict[str, Any]) -> Dict[str, float]:
        """Run all stress tests."""
        results = {}
        for name, test in self.tests.items():
            if name in initial_states:
                results[name] = test.run(initial_states[name])
        return results


# =============================================================================
# INVARIANT CHECKER
# =============================================================================

@dataclass
class Invariant:
    """An invariant that must hold."""
    
    name: str
    description: str
    check_fn: Callable[[Any], bool]
    
    def check(self, state: Any) -> bool:
        """Check if invariant holds."""
        try:
            return self.check_fn(state)
        except Exception:
            return False


class InvariantChecker:
    """Checks a set of invariants."""
    
    def __init__(self):
        self.invariants: List[Invariant] = []
    
    def add(self, name: str, description: str,
           check_fn: Callable[[Any], bool]) -> Invariant:
        """Add an invariant."""
        inv = Invariant(name=name, description=description, check_fn=check_fn)
        self.invariants.append(inv)
        return inv
    
    def check_all(self, state: Any) -> Dict[str, bool]:
        """Check all invariants."""
        return {inv.name: inv.check(state) for inv in self.invariants}
    
    def all_hold(self, state: Any) -> bool:
        """Check if all invariants hold."""
        return all(inv.check(state) for inv in self.invariants)
    
    def violations(self, state: Any) -> List[str]:
        """Get list of violated invariants."""
        return [inv.name for inv in self.invariants if not inv.check(state)]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_harness() -> bool:
    """Validate verification harness module."""
    
    # Test TestCase
    case = TestCase(
        id="test1",
        name="Always passes",
        description="A test that always passes",
        test_fn=lambda: True
    )
    assert case.run() == TestResult.PASS
    assert case.passed()
    
    # Test TestSuite
    suite = TestSuite(name="Test Suite")
    suite.add_test("t1", "Test 1", lambda: True)
    suite.add_test("t2", "Test 2", lambda: True)
    suite.add_test("t3", "Test 3", lambda: False, claim_type=ClaimType.HEUR)
    
    results = suite.run_all()
    assert results["PASS"] == 2
    assert results["FAIL"] == 1
    assert not suite.all_passed()
    assert len(suite.failures()) == 1
    
    # Test Certificate
    cert = Certificate(
        cert_id="cert1",
        claim="Test claim",
        claim_type=ClaimType.HEUR
    )
    cert.add_evidence("Test evidence")
    cert.add_test_result("t1", TestResult.PASS)
    cert.sign("test_issuer")
    
    assert cert.verify_signature()
    assert cert.is_valid()
    
    # Test VerificationHarness
    harness = VerificationHarness()
    suite = harness.add_suite("unit_tests", "Unit tests")
    suite.add_test("u1", "Unit 1", lambda: True)
    suite.add_test("u2", "Unit 2", lambda: True)
    
    results = harness.run_suite("unit_tests")
    assert results["PASS"] == 2
    
    cert = harness.issue_certificate("All tests pass", ClaimType.DER, "unit_tests")
    assert cert is not None
    assert harness.verify_certificate(cert.cert_id)
    
    # Test InvariantChecker
    checker = InvariantChecker()
    checker.add("positive", "Value must be positive", lambda x: x > 0)
    checker.add("bounded", "Value must be < 100", lambda x: x < 100)
    
    assert checker.all_hold(50)
    assert not checker.all_hold(-1)
    assert checker.violations(-1) == ["positive"]
    
    return True


if __name__ == "__main__":
    print("Validating Harness Module...")
    assert validate_harness()
    print("✓ Harness Module validated")
    
    # Demo
    print("\n=== Verification Harness Demo ===")
    
    harness = VerificationHarness()
    
    # Create test suite
    suite = harness.add_suite("pcp_validation", "PCP validation tests")
    suite.add_test("spec_valid", "Spec is valid", lambda: True)
    suite.add_test("evidence_complete", "Evidence complete", lambda: True)
    suite.add_test("proof_verified", "Proof verified", lambda: True)
    suite.add_test("audit_chain", "Audit chain intact", lambda: True)
    
    print("\nRunning test suite:")
    results = harness.run_suite("pcp_validation")
    print(f"  Results: {results}")
    
    print("\nIssuing certificate:")
    cert = harness.issue_certificate(
        "PCP validation complete",
        ClaimType.DER,
        "pcp_validation"
    )
    print(f"  Certificate ID: {cert.cert_id}")
    print(f"  Valid: {cert.is_valid()}")
    print(f"  Summary: {cert.to_dict()}")
    
    print("\nHarness summary:")
    print(f"  {harness.summary()}")

from __future__ import annotations

import dataclasses
import json
import unittest

from kc144_v7_runtime import AttemptStatus, ModelProfile
from kc144_v8_navigation import register_kc144_v8
from kc144_v8_runtime import (
    Answerability,
    CandidateClaim,
    CircuitBreaker,
    CircuitState,
    ClaimMatrixCompiler,
    ClaimMode,
    ConjugateAuditor,
    ControlledFallbackRouter,
    EvidenceMaturity,
    GateState,
    PullRequestReviewCompiler,
    ReleaseGateCompiler,
    ReleaseGateInput,
    RepairBudget,
    SourceSpan,
    default_v8_release_gates,
)


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorator


class ClaimMatrixTests(unittest.TestCase):
    def setUp(self):
        self.span = SourceSpan("source", "S1", "L1", "evidence", 0.9)
        self.compiler = ClaimMatrixCompiler()

    def test_direct_supported_is_exact(self):
        matrix = self.compiler.compile(
            [self.span],
            [CandidateClaim("C1", "Claim", ClaimMode.DIRECT, ("S1",))],
        )
        self.assertEqual(matrix.answerability, Answerability.ANSWER)
        self.assertEqual(matrix.rows[0].evidence_maturity, EvidenceMaturity.EXACT)

    def test_direct_unsourced_is_qualified(self):
        matrix = self.compiler.compile(
            [self.span],
            [CandidateClaim("C1", "Claim", ClaimMode.DIRECT)],
        )
        self.assertEqual(matrix.answerability, Answerability.ANSWER_QUALIFIED)
        self.assertIn("DIRECT_CLAIM_UNSOURCED", matrix.rows[0].defects)

    def test_contradiction_is_preserved(self):
        conflict = SourceSpan("source2", "S2", "L2", "counter", 0.9, True)
        matrix = self.compiler.compile(
            [self.span, conflict],
            [CandidateClaim("C1", "Claim", ClaimMode.DIRECT, ("S1",), ("S2",))],
        )
        self.assertEqual(matrix.answerability, Answerability.CONFLICT_REPORT)
        self.assertIn("CONTRADICTION_OPEN", matrix.rows[0].defects)

    def test_echo_does_not_inflate_lineages(self):
        echo = dataclasses.replace(self.span, span_id="S2")
        matrix = self.compiler.compile(
            [self.span, echo],
            [CandidateClaim("C1", "Claim", ClaimMode.DIRECT, ("S1", "S2"))],
        )
        self.assertEqual(matrix.rows[0].independent_lineages, 1)

    def test_generated_claim_is_unsupported_without_source(self):
        matrix = self.compiler.compile(
            [self.span],
            [CandidateClaim("C1", "Generated", ClaimMode.GENERATED)],
        )
        self.assertEqual(matrix.rows[0].evidence_maturity, EvidenceMaturity.UNSUPPORTED)


class AuditTests(unittest.TestCase):
    def test_audit_accepts_exact_and_rejects_unsourced_direct(self):
        compiler = ClaimMatrixCompiler()
        span = SourceSpan("s", "S1", "L1", "x", 1.0)
        matrix = compiler.compile(
            [span],
            [
                CandidateClaim("good", "Good", ClaimMode.DIRECT, ("S1",)),
                CandidateClaim("bad", "Bad", ClaimMode.DIRECT),
            ],
        )
        receipt = ConjugateAuditor().audit(matrix)
        self.assertIn("good", receipt.accepted_claim_ids)
        self.assertIn("bad", receipt.rejected_claim_ids)
        self.assertTrue(receipt.return_required)
        self.assertEqual(receipt.authority_effect, "NONE")

    def test_audit_detects_lineage_echo(self):
        compiler = ClaimMatrixCompiler()
        spans = [
            SourceSpan("s", "S1", "L1", "x", 1.0),
            SourceSpan("s-copy", "S2", "L1", "x", 1.0),
        ]
        matrix = compiler.compile(
            spans,
            [CandidateClaim("C", "Claim", ClaimMode.DIRECT, ("S1", "S2"))],
        )
        receipt = ConjugateAuditor().audit(matrix)
        self.assertIn("SOURCE_LINEAGE_ECHO", receipt.defects)


class ControlTests(unittest.TestCase):
    def test_budget_limits_per_model(self):
        budget = RepairBudget(per_model_limit=1, total_limit=3)
        budget, first = budget.consume("m")
        budget, second = budget.consume("m")
        self.assertTrue(first)
        self.assertFalse(second)

    def test_budget_limits_total(self):
        budget = RepairBudget(per_model_limit=2, total_limit=1)
        budget, first = budget.consume("a")
        budget, second = budget.consume("b")
        self.assertTrue(first)
        self.assertFalse(second)

    def test_circuit_opens(self):
        breaker = CircuitBreaker(failure_threshold=2)
        breaker = breaker.failure(0)
        breaker = breaker.failure(1)
        self.assertEqual(breaker.state, CircuitState.OPEN)

    def test_circuit_half_opens(self):
        breaker = CircuitBreaker(failure_threshold=1, cooldown_seconds=5).failure(0)
        breaker, allowed = breaker.allow(6)
        self.assertTrue(allowed)
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)

    def test_controlled_fallback_records_failure(self):
        profiles = (
            ModelProfile("bad", "provider", 0.01, 10, 1.0, ("typed",)),
            ModelProfile("good", "provider", 0.02, 20, 0.9, ("typed",)),
        )
        router = ControlledFallbackRouter(profiles)
        router.bind("bad", lambda fn, args: {"authority_effect": "NONE"})
        router.bind(
            "good",
            lambda fn, args: {
                "query_id": "Q",
                "literal": "x",
                "intents": [],
                "exact_addresses": [],
                "requires_sources": False,
                "requires_execution": False,
                "requires_audit": False,
                "route_budget": 1,
                "claim_ceiling": "RESEARCH_ONLY",
                "authority_effect": "NONE",
            },
        )
        receipt, output = router.route("CompileQueryContract", {}, ("typed",))
        self.assertEqual(receipt.fallback.selected_model_id, "good")
        self.assertEqual(receipt.fallback.attempts[0].status, AttemptStatus.VALIDATION_ERROR)
        self.assertEqual(output["query_id"], "Q")
        self.assertEqual(receipt.authority_effect, "NONE")


class GateTests(unittest.TestCase):
    def test_required_passes_make_promotable_not_promoted(self):
        receipt = ReleaseGateCompiler().compile(
            (
                ReleaseGateInput("A", GateState.PASS, True, "a"),
                ReleaseGateInput("B", GateState.PASS, True, "b"),
                ReleaseGateInput("I10", GateState.HOLD, False, "external"),
            )
        )
        self.assertEqual(receipt.release_state, GateState.PASS)
        self.assertTrue(receipt.promotable)
        self.assertFalse(receipt.promoted)

    def test_required_hold_holds_release(self):
        receipt = ReleaseGateCompiler().compile(
            (ReleaseGateInput("A", GateState.HOLD, True, "a"),)
        )
        self.assertEqual(receipt.release_state, GateState.HOLD)
        self.assertIn("A", receipt.hold_gate_ids)

    def test_required_failure_fails_release(self):
        receipt = ReleaseGateCompiler().compile(
            (ReleaseGateInput("A", GateState.FAIL, True, "a"),)
        )
        self.assertEqual(receipt.release_state, GateState.FAIL)
        self.assertIn("A", receipt.blocking_gate_ids)

    def test_default_gates_keep_authority_holds_nonblocking(self):
        receipt = default_v8_release_gates(
            repository_tests=GateState.PASS,
            kc144_tests=GateState.PASS,
            recorded_evals=GateState.PASS,
            revision_journal=GateState.PASS,
            secret_redaction=GateState.PASS,
            baml_native_generate=GateState.HOLD,
            review_state=GateState.HOLD,
        )
        self.assertEqual(receipt.release_state, GateState.PASS)
        self.assertTrue(receipt.promotable)
        self.assertFalse(receipt.promoted)

    def test_pr_review_receipt_is_hash_bound(self):
        gate = default_v8_release_gates(
            repository_tests=GateState.PASS,
            kc144_tests=GateState.PASS,
            recorded_evals=GateState.PASS,
            revision_journal=GateState.PASS,
            secret_redaction=GateState.PASS,
            baml_native_generate=GateState.HOLD,
            review_state=GateState.HOLD,
        )
        receipt = PullRequestReviewCompiler().compile(
            repository="demeet2k/athena-mcp-server",
            pr_number=21,
            head_sha="abc",
            draft=True,
            mergeable=True,
            review_count=0,
            unresolved_threads=0,
            ci_state=GateState.PASS,
            release_gate=gate,
        )
        self.assertEqual(len(receipt.digest), 64)
        self.assertEqual(receipt.authority_effect, "NONE")


class MCPTests(unittest.TestCase):
    def test_registration(self):
        fake = FakeMCP()
        register_kc144_v8(fake)
        self.assertEqual(
            set(fake.tools),
            {
                "kc144_v8_claim_matrix",
                "kc144_v8_conjugate_audit",
                "kc144_v8_release_gate",
            },
        )

    def test_release_tool_holds_until_ci(self):
        fake = FakeMCP()
        register_kc144_v8(fake)
        result = json.loads(fake.tools["kc144_v8_release_gate"]())
        self.assertEqual(result["release_state"], "HOLD")
        self.assertFalse(result["promoted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

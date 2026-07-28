
"""KC144 Hybrid V8 — claim matrix, conjugate audit, bounded fallback controls,
and authority-neutral release-gate receipts.

This module extends the self-contained published V7 runtime. It does not create
source evidence, IC10 promotion, or an M12 successor certificate.
"""
from __future__ import annotations

import dataclasses
import enum
import time
from typing import Any, Callable, Mapping, Sequence

from kc144_v7_runtime import (
    AttemptStatus,
    BoundaryValidator,
    FallbackReceipt,
    FallbackRouter,
    ModelProfile,
    digest,
    plain,
)


class ClaimMode(str, enum.Enum):
    DIRECT = "DIRECT"
    INFERRED = "INFERRED"
    GENERATED = "GENERATED"


class EvidenceMaturity(str, enum.Enum):
    EXACT = "EXACT"
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    UNSUPPORTED = "UNSUPPORTED"


class Answerability(str, enum.Enum):
    ANSWER = "ANSWER"
    ANSWER_QUALIFIED = "ANSWER_QUALIFIED"
    CONFLICT_REPORT = "CONFLICT_REPORT"
    ABSTAIN = "ABSTAIN"


class GateState(str, enum.Enum):
    PASS = "PASS"
    HOLD = "HOLD"
    FAIL = "FAIL"


class CircuitState(str, enum.Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclasses.dataclass(frozen=True)
class SourceSpan:
    source_id: str
    span_id: str
    lineage_id: str
    text: str
    quality: float
    contradiction: bool = False
    valid_time: str | None = None
    recorded_time: str | None = None


@dataclasses.dataclass(frozen=True)
class CandidateClaim:
    claim_id: str
    text: str
    mode: ClaimMode
    supporting_span_ids: tuple[str, ...] = ()
    contradicting_span_ids: tuple[str, ...] = ()
    intermediate_claim_ids: tuple[str, ...] = ()
    requested_ceiling: str = "RESEARCH_ONLY"


@dataclasses.dataclass(frozen=True)
class ClaimMatrixRow:
    claim_id: str
    normalized_claim: str
    mode: ClaimMode
    supporting_span_ids: tuple[str, ...]
    contradicting_span_ids: tuple[str, ...]
    independent_lineages: int
    missing_links: tuple[str, ...]
    evidence_maturity: EvidenceMaturity
    defects: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class ClaimMatrix:
    rows: tuple[ClaimMatrixRow, ...]
    answerability: Answerability
    defects: tuple[str, ...]
    authority_effect: str = "NONE"


@dataclasses.dataclass(frozen=True)
class ConjugateAuditReceipt:
    accepted_claim_ids: tuple[str, ...]
    held_claim_ids: tuple[str, ...]
    rejected_claim_ids: tuple[str, ...]
    contradiction_claim_ids: tuple[str, ...]
    required_retrieval_modes: tuple[str, ...]
    defects: tuple[str, ...]
    return_required: bool
    digest: str
    truth_effect: str = "NONE"
    authority_effect: str = "NONE"


@dataclasses.dataclass(frozen=True)
class RepairBudget:
    per_model_limit: int = 1
    total_limit: int = 4
    total_consumed: int = 0
    consumed_by_model: Mapping[str, int] = dataclasses.field(default_factory=dict)

    def consume(self, model_id: str) -> tuple["RepairBudget", bool]:
        used = dict(self.consumed_by_model)
        model_used = used.get(model_id, 0)
        if model_used >= self.per_model_limit or self.total_consumed >= self.total_limit:
            return self, False
        used[model_id] = model_used + 1
        return (
            dataclasses.replace(
                self,
                total_consumed=self.total_consumed + 1,
                consumed_by_model=used,
            ),
            True,
        )


@dataclasses.dataclass(frozen=True)
class CircuitBreaker:
    failure_threshold: int = 2
    cooldown_seconds: float = 30.0
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    opened_at: float | None = None

    def allow(self, now: float) -> tuple["CircuitBreaker", bool]:
        if self.state is CircuitState.CLOSED:
            return self, True
        if self.state is CircuitState.OPEN:
            if self.opened_at is not None and now - self.opened_at >= self.cooldown_seconds:
                return dataclasses.replace(self, state=CircuitState.HALF_OPEN), True
            return self, False
        return self, True

    def success(self) -> "CircuitBreaker":
        return dataclasses.replace(
            self,
            state=CircuitState.CLOSED,
            failures=0,
            opened_at=None,
        )

    def failure(self, now: float) -> "CircuitBreaker":
        failures = self.failures + 1
        if failures >= self.failure_threshold:
            return dataclasses.replace(
                self,
                state=CircuitState.OPEN,
                failures=failures,
                opened_at=now,
            )
        return dataclasses.replace(self, failures=failures)


@dataclasses.dataclass(frozen=True)
class ControlledFallbackReceipt:
    fallback: FallbackReceipt
    repair_budget: RepairBudget
    circuit_states: Mapping[str, str]
    blocked_models: tuple[str, ...]
    truth_effect: str = "NONE"
    evidence_effect: str = "NONE"
    authority_effect: str = "NONE"


@dataclasses.dataclass(frozen=True)
class ReleaseGateInput:
    gate_id: str
    state: GateState
    required: bool
    witness: str
    details: Mapping[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class ReleaseGateReceipt:
    gates: tuple[ReleaseGateInput, ...]
    release_state: GateState
    blocking_gate_ids: tuple[str, ...]
    hold_gate_ids: tuple[str, ...]
    promotable: bool
    promoted: bool
    digest: str
    authority_effect: str = "NONE"


@dataclasses.dataclass(frozen=True)
class PullRequestReviewReceipt:
    repository: str
    pr_number: int
    head_sha: str
    draft: bool
    mergeable: bool
    review_count: int
    unresolved_threads: int
    ci_state: GateState
    release_gate_digest: str
    digest: str
    authority_effect: str = "NONE"


class ClaimMatrixCompiler:
    def compile(
        self,
        spans: Sequence[SourceSpan],
        claims: Sequence[CandidateClaim],
    ) -> ClaimMatrix:
        span_map = {span.span_id: span for span in spans}
        rows: list[ClaimMatrixRow] = []
        global_defects: set[str] = set()
        has_conflict = False
        has_hold = False

        for span in spans:
            if not span.source_id:
                global_defects.add("SOURCE_ID_EMPTY")
            if not span.span_id:
                global_defects.add("SPAN_ID_EMPTY")
            if not span.lineage_id:
                global_defects.add("LINEAGE_ID_EMPTY")
            if not 0.0 <= span.quality <= 1.0:
                global_defects.add("SOURCE_QUALITY_INVALID")

        for claim in claims:
            support = tuple(s for s in claim.supporting_span_ids if s in span_map)
            contradict = tuple(s for s in claim.contradicting_span_ids if s in span_map)
            defects: list[str] = []
            missing_links = tuple(link for link in claim.intermediate_claim_ids if not link.strip())

            if claim.mode is ClaimMode.DIRECT and not support:
                defects.append("DIRECT_CLAIM_UNSOURCED")
            if len(support) != len(claim.supporting_span_ids):
                defects.append("SUPPORT_SPAN_MISSING")
            if len(contradict) != len(claim.contradicting_span_ids):
                defects.append("CONTRADICTION_SPAN_MISSING")
            if contradict:
                defects.append("CONTRADICTION_OPEN")
                has_conflict = True
            if missing_links:
                defects.append("MISSING_INTERMEDIATE")
            if claim.requested_ceiling not in {"RESEARCH_ONLY", "PAUSE", "REFUSE"}:
                defects.append("CLAIM_CEILING_EXCEEDED")

            lineages = {
                span_map[span_id].lineage_id
                for span_id in support
                if not span_map[span_id].contradiction
            }
            if not support:
                maturity = EvidenceMaturity.UNSUPPORTED
                has_hold = True
            elif defects:
                maturity = EvidenceMaturity.PARTIAL
                has_hold = True
            elif claim.mode is ClaimMode.DIRECT and all(
                span_map[span_id].quality >= 0.8 for span_id in support
            ):
                maturity = EvidenceMaturity.EXACT
            else:
                maturity = EvidenceMaturity.SUPPORTED

            row = ClaimMatrixRow(
                claim_id=claim.claim_id,
                normalized_claim=" ".join(claim.text.split()),
                mode=claim.mode,
                supporting_span_ids=support,
                contradicting_span_ids=contradict,
                independent_lineages=len(lineages),
                missing_links=missing_links,
                evidence_maturity=maturity,
                defects=tuple(defects),
            )
            rows.append(row)
            global_defects.update(defects)

        if has_conflict:
            answerability = Answerability.CONFLICT_REPORT
        elif has_hold:
            answerability = Answerability.ANSWER_QUALIFIED
        elif rows:
            answerability = Answerability.ANSWER
        else:
            answerability = Answerability.ABSTAIN

        return ClaimMatrix(
            rows=tuple(rows),
            answerability=answerability,
            defects=tuple(sorted(global_defects)),
        )


class ConjugateAuditor:
    def audit(self, matrix: ClaimMatrix) -> ConjugateAuditReceipt:
        accepted: list[str] = []
        held: list[str] = []
        rejected: list[str] = []
        contradictions: list[str] = []
        defects: set[str] = set(matrix.defects)
        modes = {
            "COUNTEREVIDENCE",
            "SOURCE_INDEPENDENCE",
            "ORIGINAL_ORDER",
            "TEMPORAL_VERSION",
        }

        for row in matrix.rows:
            if row.contradicting_span_ids:
                contradictions.append(row.claim_id)
                held.append(row.claim_id)
            elif row.mode is ClaimMode.DIRECT and not row.supporting_span_ids:
                rejected.append(row.claim_id)
            elif row.evidence_maturity in {EvidenceMaturity.EXACT, EvidenceMaturity.SUPPORTED}:
                accepted.append(row.claim_id)
            else:
                held.append(row.claim_id)

            if row.independent_lineages <= 1 and len(row.supporting_span_ids) > 1:
                defects.add("SOURCE_LINEAGE_ECHO")
            if row.missing_links:
                defects.add("MISSING_INTERMEDIATE")

        body = {
            "accepted": accepted,
            "held": held,
            "rejected": rejected,
            "contradictions": contradictions,
            "modes": sorted(modes),
            "defects": sorted(defects),
            "return_required": True,
            "truth_effect": "NONE",
            "authority_effect": "NONE",
        }
        return ConjugateAuditReceipt(
            accepted_claim_ids=tuple(accepted),
            held_claim_ids=tuple(held),
            rejected_claim_ids=tuple(rejected),
            contradiction_claim_ids=tuple(contradictions),
            required_retrieval_modes=tuple(sorted(modes)),
            defects=tuple(sorted(defects)),
            return_required=True,
            digest=digest(body),
        )


class ControlledFallbackRouter:
    """Budget and circuit wrapper around the V7 fallback router."""

    def __init__(
        self,
        profiles: Sequence[ModelProfile],
        *,
        validator: BoundaryValidator | None = None,
        budget: RepairBudget | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.profiles = tuple(profiles)
        self.validator = validator or BoundaryValidator()
        self.budget = budget or RepairBudget()
        self.clock = clock or time.time
        self.invokers: dict[str, Callable[[str, Mapping[str, Any]], Any]] = {}
        self.circuits = {
            profile.model_id: CircuitBreaker()
            for profile in self.profiles
        }

    def bind(self, model_id: str, invoker: Callable[[str, Mapping[str, Any]], Any]) -> None:
        self.invokers[model_id] = invoker

    def route(
        self,
        function_name: str,
        arguments: Mapping[str, Any],
        required_capabilities: Sequence[str] = (),
    ) -> tuple[ControlledFallbackReceipt, Any]:
        now = self.clock()
        available_profiles: list[ModelProfile] = []
        blocked: list[str] = []

        for profile in self.profiles:
            circuit, allowed = self.circuits[profile.model_id].allow(now)
            self.circuits[profile.model_id] = circuit
            if not allowed:
                blocked.append(profile.model_id)
                continue
            available_profiles.append(profile)

        router = FallbackRouter(available_profiles, self.validator)
        for model_id, invoker in self.invokers.items():
            if model_id in {profile.model_id for profile in available_profiles}:
                router.bind(model_id, invoker)

        fallback, output = router.route(
            function_name,
            arguments,
            required_capabilities,
        )

        for attempt in fallback.attempts:
            if attempt.status is AttemptStatus.PASS:
                self.circuits[attempt.model_id] = self.circuits[attempt.model_id].success()
            elif attempt.status not in {AttemptStatus.SKIPPED}:
                self.circuits[attempt.model_id] = self.circuits[attempt.model_id].failure(now)
                self.budget, _ = self.budget.consume(attempt.model_id)

        receipt = ControlledFallbackReceipt(
            fallback=fallback,
            repair_budget=self.budget,
            circuit_states={
                model_id: circuit.state.value
                for model_id, circuit in sorted(self.circuits.items())
            },
            blocked_models=tuple(sorted(blocked)),
        )
        return receipt, output


class ReleaseGateCompiler:
    def compile(
        self,
        gates: Sequence[ReleaseGateInput],
    ) -> ReleaseGateReceipt:
        required_failures = tuple(
            gate.gate_id
            for gate in gates
            if gate.required and gate.state is GateState.FAIL
        )
        required_holds = tuple(
            gate.gate_id
            for gate in gates
            if gate.required and gate.state is GateState.HOLD
        )
        if required_failures:
            release_state = GateState.FAIL
        elif required_holds:
            release_state = GateState.HOLD
        else:
            release_state = GateState.PASS

        promotable = release_state is GateState.PASS
        # Promotion is never self-authorized by the release compiler.
        promoted = False
        body = {
            "gates": [plain(gate) for gate in gates],
            "release_state": release_state.value,
            "blocking": required_failures,
            "holds": required_holds,
            "promotable": promotable,
            "promoted": promoted,
            "authority_effect": "NONE",
        }
        return ReleaseGateReceipt(
            gates=tuple(gates),
            release_state=release_state,
            blocking_gate_ids=required_failures,
            hold_gate_ids=required_holds,
            promotable=promotable,
            promoted=promoted,
            digest=digest(body),
        )


class PullRequestReviewCompiler:
    def compile(
        self,
        *,
        repository: str,
        pr_number: int,
        head_sha: str,
        draft: bool,
        mergeable: bool,
        review_count: int,
        unresolved_threads: int,
        ci_state: GateState,
        release_gate: ReleaseGateReceipt,
    ) -> PullRequestReviewReceipt:
        body = {
            "repository": repository,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "draft": draft,
            "mergeable": mergeable,
            "review_count": review_count,
            "unresolved_threads": unresolved_threads,
            "ci_state": ci_state.value,
            "release_gate_digest": release_gate.digest,
            "authority_effect": "NONE",
        }
        return PullRequestReviewReceipt(
            repository=repository,
            pr_number=pr_number,
            head_sha=head_sha,
            draft=draft,
            mergeable=mergeable,
            review_count=review_count,
            unresolved_threads=unresolved_threads,
            ci_state=ci_state,
            release_gate_digest=release_gate.digest,
            digest=digest(body),
        )


def default_v8_release_gates(
    *,
    repository_tests: GateState,
    kc144_tests: GateState,
    recorded_evals: GateState,
    revision_journal: GateState,
    secret_redaction: GateState,
    baml_native_generate: GateState,
    review_state: GateState,
) -> ReleaseGateReceipt:
    return ReleaseGateCompiler().compile(
        (
            ReleaseGateInput("LEGACY_BASELINE", repository_tests, False, "bounded pytest tests/ migration ledger"),
            ReleaseGateInput("KC144_TESTS", kc144_tests, True, "pytest MCP/tests/test_kc144_v7_runtime.py MCP/tests/test_kc144_v8_runtime.py"),
            ReleaseGateInput("RECORDED_EVALS", recorded_evals, True, "keyless recording replay"),
            ReleaseGateInput("REVISION_JOURNAL", revision_journal, True, "hash-chain verify"),
            ReleaseGateInput("SECRET_REDACTION", secret_redaction, True, "recording scan"),
            ReleaseGateInput("BAML_NATIVE_GENERATE", baml_native_generate, False, "baml-cli generate"),
            ReleaseGateInput("PR_REVIEW", review_state, False, "GitHub review receipt"),
            ReleaseGateInput("I10_PROMOTION", GateState.HOLD, False, "external authority absent"),
            ReleaseGateInput("M12_SUCCESSOR", GateState.HOLD, False, "successor authority absent"),
        )
    )

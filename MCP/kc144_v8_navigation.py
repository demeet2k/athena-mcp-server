"""FastMCP adapter for KC144 Hybrid V8."""
from __future__ import annotations

import json
from typing import Any

from kc144_v7_runtime import plain
from kc144_v8_runtime import (
    CandidateClaim,
    ClaimMatrixCompiler,
    ClaimMode,
    ConjugateAuditor,
    GateState,
    SourceSpan,
    default_v8_release_gates,
)

_REGISTERED: set[int] = set()


def _dump(value: Any) -> str:
    return json.dumps(plain(value), indent=2, sort_keys=True, ensure_ascii=False)


def register_kc144_v8(mcp: Any) -> Any:
    identity = id(mcp)
    if identity in _REGISTERED:
        return mcp
    _REGISTERED.add(identity)

    @mcp.tool()
    def kc144_v8_claim_matrix(spans_json: str, claims_json: str) -> str:
        spans = [SourceSpan(**item) for item in json.loads(spans_json)]
        claims = [
            CandidateClaim(
                claim_id=item["claim_id"],
                text=item["text"],
                mode=ClaimMode(item["mode"]),
                supporting_span_ids=tuple(item.get("supporting_span_ids", [])),
                contradicting_span_ids=tuple(item.get("contradicting_span_ids", [])),
                intermediate_claim_ids=tuple(item.get("intermediate_claim_ids", [])),
                requested_ceiling=item.get("requested_ceiling", "RESEARCH_ONLY"),
            )
            for item in json.loads(claims_json)
        ]
        return _dump(ClaimMatrixCompiler().compile(spans, claims))

    @mcp.tool()
    def kc144_v8_conjugate_audit(spans_json: str, claims_json: str) -> str:
        spans = [SourceSpan(**item) for item in json.loads(spans_json)]
        claims = [
            CandidateClaim(
                claim_id=item["claim_id"],
                text=item["text"],
                mode=ClaimMode(item["mode"]),
                supporting_span_ids=tuple(item.get("supporting_span_ids", [])),
                contradicting_span_ids=tuple(item.get("contradicting_span_ids", [])),
                intermediate_claim_ids=tuple(item.get("intermediate_claim_ids", [])),
                requested_ceiling=item.get("requested_ceiling", "RESEARCH_ONLY"),
            )
            for item in json.loads(claims_json)
        ]
        matrix = ClaimMatrixCompiler().compile(spans, claims)
        return _dump(ConjugateAuditor().audit(matrix))

    @mcp.tool()
    def kc144_v8_release_gate(
        repository_tests: str = "HOLD",
        kc144_tests: str = "HOLD",
        recorded_evals: str = "PASS",
        revision_journal: str = "PASS",
        secret_redaction: str = "PASS",
        baml_native_generate: str = "HOLD",
        review_state: str = "HOLD",
    ) -> str:
        receipt = default_v8_release_gates(
            repository_tests=GateState(repository_tests),
            kc144_tests=GateState(kc144_tests),
            recorded_evals=GateState(recorded_evals),
            revision_journal=GateState(revision_journal),
            secret_redaction=GateState(secret_redaction),
            baml_native_generate=GateState(baml_native_generate),
            review_state=GateState(review_state),
        )
        return _dump(receipt)

    return mcp

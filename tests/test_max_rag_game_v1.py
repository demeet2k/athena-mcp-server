from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
MCP_DIR = ROOT / "MCP"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

from crystal_108d.max_rag_game_v1 import (
    CONTROL_HEAD,
    HARD_GATES,
    REGISTRY,
    REGISTRY_DIGEST,
    SCORE_FIELDS,
    build_registry,
    compile_query,
    evaluate_claim,
    output_plan,
    score_game,
    shadow_compare,
    shadow_manifest,
    shadow_suite,
    status,
    successor_compile,
)


def metrics(value: float = 0.9) -> dict[str, float]:
    return {field: value for field in SCORE_FIELDS}


def gates(value: bool = True) -> dict[str, bool]:
    return {gate: value for gate in HARD_GATES}


def observation(policy_id: str, candidate: bool = False) -> dict:
    values = metrics(0.80)
    if candidate:
        values["coverage"] = 0.88
        values["evidence_fidelity"] = 0.85
    return {
        "case_id": "MAXRAG-S01",
        "policy_id": policy_id,
        "metrics": values,
        "unsupported_claims": 0,
        "hard_gates": gates(),
        "rollback_available": True,
        "defects": [],
    }


def digest(value: object) -> str:
    import hashlib
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def load_server():
    path = MCP_DIR / "max_rag_mcp_server.py"
    spec = importlib.util.spec_from_file_location("max_rag_mcp_server", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestRegistry:
    def test_registry_is_exact_contiguous_kc144(self):
        rows = build_registry()
        assert len(rows) == 144
        assert [row["gid"] for row in rows] == list(range(1, 145))
        assert len({row["coordinate"] for row in rows}) == 144
        assert rows[118]["name"] == "Q-SHRINK Core"
        assert rows[118]["coordinate"] == "kc://KC144.MAX-RAG.V1/GID119"
        assert rows == REGISTRY
        assert REGISTRY_DIGEST.startswith("sha256:")

    def test_carrier_ranges_remain_exact(self):
        ranges = {
            "H6": (1, 6), "X16": (7, 22), "BR21": (23, 43),
            "F37": (44, 80), "IC10": (81, 90), "KC15": (91, 105),
            "KC27": (106, 132), "SSN12": (133, 144),
        }
        for carrier, (start, end) in ranges.items():
            gids = [row["gid"] for row in REGISTRY if row["carrier"] == carrier]
            assert gids == list(range(start, end + 1))


class TestContracts:
    def test_query_and_output_plan_do_not_execute_sources(self):
        contract = compile_query("Install and compare improved RAG", route_budget=12)
        assert contract["intent"] == "compare"
        assert "claim_graph" in contract["routes"]
        assert "hyde_negative" in contract["routes"]
        assert contract["source_contacted"] is False
        plan = output_plan(contract, token_budget=8000)
        assert plan["return_reserve"] == 1000
        assert plan["execution_performed"] is False

    def test_claim_ceiling_fails_closed(self):
        denied = evaluate_claim({
            "claim": "unsupported", "status": "confirmed", "support": [],
            "independent_source_count": 0, "uncertainty": 0.1,
        })
        assert denied["generation_permitted"] is False
        allowed = evaluate_claim({
            "claim": "bounded", "status": "supported", "support": ["s1"],
            "independent_source_count": 1, "uncertainty": 0.2,
        })
        assert allowed["generation_permitted"] is True

    def test_juice_cannot_bypass_a_failed_gate(self):
        failed = gates()
        failed["independent_witness"] = False
        receipt = score_game(metrics(), failed, 100, 0.05)
        assert receipt["juice_score"] > 0
        assert receipt["max_currency"] == 0
        assert receipt["status"] == "SANDBOX_HOLD"

    def test_all_gates_can_only_request_admission_review(self):
        receipt = score_game(metrics(), gates(), 100, 0.05)
        assert receipt["max_currency"] > 0
        assert receipt["status"] == "ADMISSION_REVIEW_ELIGIBLE"
        assert receipt["external_promotion_authority"] is False


class TestShadow:
    def test_manifest_is_frozen_twelve_case_contract(self):
        manifest = shadow_manifest()
        assert manifest["case_count"] == 12
        assert len({case["case_id"] for case in manifest["cases"]}) == 12
        assert manifest["promotion_authority"] is False

    def test_self_witness_is_rejected(self):
        baseline = observation("baseline")
        candidate = observation("candidate", candidate=True)
        witness = {
            "witness_id": "candidate", "authority_domain": "learner",
            "implementation_id": "candidate", "passed": True,
            "observation_digest": digest(candidate),
        }
        result = shadow_compare(baseline, candidate, witness)
        assert result["eligible_for_shadow"] is False
        assert "WITNESS_NOT_INDEPENDENT" in result["blockers"]

    def test_independent_digest_bound_witness_passes_pair_only(self):
        baseline = observation("baseline")
        candidate = observation("candidate", candidate=True)
        witness = {
            "witness_id": "witness-a",
            "authority_domain": "independent-domain",
            "implementation_id": "independent-implementation",
            "passed": True, "observation_digest": digest(candidate),
        }
        result = shadow_compare(baseline, candidate, witness)
        assert result["eligible_for_shadow"] is True
        assert result["canary_authority"] is False
        suite = shadow_suite([result])
        assert suite["complete"] is False
        assert suite["canary_review_eligible"] is False


class TestReturnAndStatus:
    def test_successor_is_non_dispatching_and_pinned(self):
        packet = successor_compile({
            "session_digest": "sha256:" + "1" * 64,
            "unresolved_questions": ["real observations"],
            "verified_defects": [],
            "policy_deltas": {"route_budget": 9},
            "replay_recipe": {"command": "athena-max-rag-shadow suite"},
            "rollback_digest": "sha256:" + "2" * 64,
        })
        assert packet["target_plane"]["control_head"] == CONTROL_HEAD
        assert packet["dispatch_performed"] is False
        assert packet["external_promotion_authority"] is False

    def test_status_preserves_authority_boundary(self):
        value = status()
        assert value["stations"] == 144
        assert value["tools"] == 11
        assert value["resources"] == 4
        assert value["persistent_endpoint"] is False
        assert value["production_promoted"] is False


class TestStandaloneServer:
    def test_exact_separate_catalog(self):
        server = load_server()
        tools = set(server.mcp._tool_manager._tools)
        resources = set(server.mcp._resource_manager._resources)
        assert len(tools) == 11
        assert len(resources) == 4
        assert tools == {
            "max_rag_status", "max_rag_registry", "max_rag_query_compile",
            "max_rag_output_plan", "max_rag_claim_evaluate", "max_rag_score",
            "max_rag_repair_routes", "max_rag_shadow_manifest",
            "max_rag_shadow_compare", "max_rag_shadow_suite",
            "max_rag_successor_compile",
        }
        assert resources == {
            "athena://max-rag/v1/status",
            "athena://max-rag/v1/kc144-registry",
            "athena://max-rag/v1/shadow-benchmark",
            "athena://max-rag/v1/contract",
        }

"""KC144 MAX–RAG v1: separate, read-only/reversible MCP cartridge.

The cartridge mirrors the governed control contract at a pinned Git head. It
compiles queries and plans, evaluates claim ceilings and score packets, exposes
the 144-station registry, and validates shadow receipts. It does not contact
sources, write Guild Hall state, dispatch workflows, mint external authority,
deploy, merge, or promote.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import re
from typing import Any


SCHEMA = "athena.kc144-max-rag-mcp/v1"
CONTROL_REPOSITORY = "demeet2k/Athena"
CONTROL_BRANCH = "agent/kc144-max-rag-v1"
CONTROL_HEAD = "10893a9bef5ba17ab65b67f10eef2c9436138f34"
RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
RUNTIME_PARENT_HEAD = "abd15be02c1153890cc289c9402fabeccf452b61"
RUNTIME_BRANCH = "agent/kc144-max-rag-mcp-v1"
PHASES = ("11", "10", "00", "01")
HARD_GATES = (
    "truth",
    "objective",
    "provenance",
    "privacy",
    "permissions",
    "rollback",
    "independent_witness",
)
SCORE_FIELDS = (
    "objective_fidelity",
    "evidence_fidelity",
    "coverage",
    "depth",
    "semantic_density",
    "integration",
    "contradiction_handling",
    "actionability",
    "structure",
    "replayability",
    "successor_quality",
    "resource_efficiency",
    "safety_privacy",
)


CARRIERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("H6", (
        "Constitutional oath", "User-objective lock",
        "Truth and evidence separation", "Authority and permission boundary",
        "Privacy and source minimization", "Anti-reward-hacking firewall",
    )),
    ("X16", (
        "Intent compiler", "Entity resolver", "Relation compiler",
        "Temporal-constraint compiler", "Literal-term extractor",
        "Abstraction-depth selector", "Source-class selector",
        "Answerability-threshold setter", "Navigation-budget governor",
        "Positive query expansion", "Negative query expansion",
        "Alias and historical-name expansion",
        "Coordinate and identifier expansion", "Question decomposition",
        "Parallel route contract", "Stopping and abstention contract",
    )),
    ("BR21", (
        "Source inventory", "Exact lexical retrieval",
        "Fuzzy semantic retrieval", "Document-graph traversal",
        "Entity-graph traversal", "Claim-graph traversal",
        "Temporal-graph traversal", "Provenance-graph traversal",
        "Contradiction-graph traversal", "Transformation-graph traversal",
        "Positive HyDE transformation", "Negative HyDE transformation",
        "Context-window expansion", "Cross-channel occurrence alignment",
        "Version and revision comparison",
        "Duplicate and near-duplicate detection", "Route-agreement matrix",
        "Independent-route convergence", "Evidence-path compilation",
        "Answerability and claim ceiling", "Retrieval repair navigation",
    )),
    ("F37", (
        "Task coverage map", "Depth ladder",
        "Admitted semantic-unit counter", "Semantic-density floor",
        "Redundancy ceiling", "Contradiction map",
        "Claim-to-evidence binder", "Definition generator",
        "Example generator", "Counterexample generator",
        "Mechanism expander", "Cross-domain synthesizer",
        "Parallel chapter lanes", "Recursive NEXT generator",
        "Branch backlog", "Section-completeness auditor",
        "Structural-coherence auditor", "Navigation-address compiler",
        "User-utility evaluator", "Actionability compiler",
        "Copy-paste integrity", "Format adapter",
        "Tone and vocabulary fidelity", "Equation and formalism lane",
        "Implementation-detail lane", "Test-case generator",
        "Failure-mode catalog", "Repair-instruction compiler",
        "Resource-use ledger", "Adaptive token-budget allocator",
        "Return-packet reserve", "Multi-carrier artifact loom",
        "Evidence-coverage auditor", "Source-diversity auditor",
        "Useful-novelty evaluator", "Q-SHRINK recoverable compression",
        "Maximum-useful-output admission",
    )),
    ("IC10", (
        "Truth gate", "Provenance gate", "Contradiction gate",
        "Hallucination and unsupported-inference gate",
        "Scope and calibration gate", "Privacy gate", "Permission gate",
        "Reversibility gate", "User-objective gate",
        "Independent-witness gate",
    )),
    ("KC15", (
        "Quest allocator", "Functional agent-role allocator",
        "Parallel route scheduler", "Result merger and conflict keeper",
        "Thirteen-dimensional reward vector", "MAX wallet",
        "Witness Seal mint", "Residual Dust ledger", "Loot inventory",
        "Upgrade equip and unequip", "Cooldown and diminishing returns",
        "Anti-farming and duplicate suppression", "Shadow and canary runner",
        "Append-only episode ledger", "Guild Hall quest projection",
    )),
    ("KC27", (
        "Query Prism", "Lexical Hook", "Semantic Compass", "Graph Lantern",
        "Twin HyDE Mirror", "Temporal Sextant", "Provenance Chain",
        "Contradiction Magnet", "Answerability Gate", "Outline Skeleton",
        "Depth Drill", "Density Lens", "Example Forge", "Q-SHRINK Core",
        "Counterexample Anvil", "Recursive Chapter Engine",
        "Cross-Carrier Loom", "Action Compiler", "Continuation Seed",
        "Route Swarm Totem", "Witness Beacon", "Rollback Anchor",
        "Failure Alchemist", "Memory Gardener", "Budget Governor",
        "Guild Hall Relay", "Octave Recrystallizer",
    )),
    ("SSN12", (
        "Session digest", "Unresolved-question register",
        "Verified-defect ledger", "Policy-delta register",
        "Memory-admission candidate", "Branch disposition", "Source packet",
        "Artifact manifest", "Replay recipe", "Rollback path",
        "Successor seed", "Cold-start return gate",
    )),
)

CARRIER_ROLES = {
    "H6": "constitution",
    "X16": "query_compilation",
    "BR21": "multiplex_retrieval",
    "F37": "maximum_useful_output",
    "IC10": "integrity_membrane",
    "KC15": "game_orchestration",
    "KC27": "upgrade_forge",
    "SSN12": "successor_return",
}

SHADOW_CASES = (
    ("MAXRAG-S01", "D01", "Reward-hack resistance"),
    ("MAXRAG-S02", "D02", "Source lineage and occurrence fidelity"),
    ("MAXRAG-S03", "D03", "Complex query decomposition"),
    ("MAXRAG-S04", "D04", "Multiplex graph linking"),
    ("MAXRAG-S05", "D05", "Claim ceiling and calibration"),
    ("MAXRAG-S06", "D06", "Long-horizon output planning"),
    ("MAXRAG-S07", "D07", "Tool and route selection"),
    ("MAXRAG-S08", "D08", "Executable artifact integrity"),
    ("MAXRAG-S09", "D09", "Recoverable compression"),
    ("MAXRAG-S10", "D10", "Correction-preserving collaboration"),
    ("MAXRAG-S11", "D11", "Website and letter traversal"),
    ("MAXRAG-S12", "D12", "Evaluation and resource governance"),
)


class MaxRAGError(RuntimeError):
    """Fail-closed MAX–RAG contract error."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _parse_object(value: str | dict[str, Any] | None, field: str) -> dict[str, Any]:
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return deepcopy(value)
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"{field} must be a JSON object") from error
    if not isinstance(parsed, dict):
        raise ValueError(f"{field} must be a JSON object")
    return parsed


def _parse_list(value: str | list[Any] | None, field: str) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return deepcopy(value)
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"{field} must be a JSON array") from error
    if not isinstance(parsed, list):
        raise ValueError(f"{field} must be a JSON array")
    return parsed


def _negative_effects() -> dict[str, bool]:
    return {
        "source_contacted": False,
        "guild_hall_source_mutated": False,
        "workflow_dispatched": False,
        "external_authority_created": False,
        "merged": False,
        "deployed": False,
        "production_promoted": False,
    }


def _require_digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError(f"{field} must be sha256:<64 lowercase hex>")
    return value


def build_registry() -> list[dict[str, Any]]:
    stations: list[dict[str, Any]] = []
    gid = 1
    for carrier, names in CARRIERS:
        for local_index, name in enumerate(names, start=1):
            stations.append({
                "gid": gid,
                "coordinate": f"kc://KC144.MAX-RAG.V1/GID{gid:03d}",
                "row": ((gid - 1) // 12) + 1,
                "column": ((gid - 1) % 12) + 1,
                "organ": ((gid - 1) // 4) + 1,
                "phase": PHASES[(gid - 1) % 4],
                "carrier": carrier,
                "carrier_index": local_index,
                "role": CARRIER_ROLES[carrier],
                "name": name,
            })
            gid += 1
    if len(stations) != 144 or [row["gid"] for row in stations] != list(range(1, 145)):
        raise MaxRAGError("KC144 registry is not contiguous")
    if stations[118]["name"] != "Q-SHRINK Core":
        raise MaxRAGError("canonical GID119 Q-SHRINK seat drifted")
    return stations


REGISTRY = build_registry()
REGISTRY_DIGEST = _digest(REGISTRY)


def compile_query(raw: str, route_budget: int = 9, threshold: float = 0.75) -> dict[str, Any]:
    if not raw.strip():
        raise ValueError("query is required")
    if isinstance(route_budget, bool) or route_budget < 1 or route_budget > 15:
        raise ValueError("route_budget must be within [1,15]")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be within [0,1]")
    lowered = raw.lower()
    if any(token in lowered for token in ("compare", " versus ", " vs ", "difference")):
        intent = "compare"
    elif any(token in lowered for token in ("derive", "prove", "solve", "calculate")):
        intent = "derive"
    elif any(token in lowered for token in ("find", "locate", "search", "where")):
        intent = "locate"
    elif any(token in lowered for token in ("build", "create", "install", "implement", "design")):
        intent = "construct"
    else:
        intent = "explain"
    terms = list(dict.fromkeys(re.findall(r"[a-z0-9_-]{3,}", lowered)))
    entities = list(dict.fromkeys(
        match.strip() for match in re.findall(
            r"\b(?:[A-Z][A-Za-z0-9_-]*)(?:\s+[A-Z][A-Za-z0-9_-]*)*\b", raw
        ) if match.strip()
    ))
    temporal = re.findall(
        r"\b(?:today|yesterday|tomorrow|latest|current|recent|19\d{2}|20\d{2})\b",
        lowered,
    )
    depth = "multi-hop" if intent in {"compare", "derive", "construct"} or len(terms) > 12 else "single-hop"
    routes = ["literal", "lexical", "semantic", "contextual", "provenance"]
    if depth == "multi-hop":
        routes += ["document_graph", "entity_graph", "claim_graph"]
    if intent in {"compare", "derive", "construct"}:
        routes += ["hyde_positive", "hyde_negative", "contradiction"]
    if temporal:
        routes.append("temporal")
    routes = list(dict.fromkeys(routes))[:route_budget]
    contract = {
        "schema": "athena.max-rag-query-contract/v1",
        "raw": raw,
        "intent": intent,
        "entities": entities,
        "literal_terms": terms,
        "temporal_constraints": temporal,
        "desired_depth": depth,
        "answerability_threshold": threshold,
        "route_budget": route_budget,
        "routes": routes,
        "source_execution_performed": False,
        **_negative_effects(),
    }
    contract["query_id"] = "MAXRAG-Q-" + _digest(contract).split(":", 1)[1][:20]
    return contract


def output_plan(contract: dict[str, Any], token_budget: int = 8000) -> dict[str, Any]:
    if contract.get("schema") != "athena.max-rag-query-contract/v1":
        raise ValueError("query contract schema mismatch")
    if isinstance(token_budget, bool) or token_budget < 512:
        raise ValueError("token_budget must be at least 512")
    reserve = max(256, math.floor(token_budget * 0.125))
    plan = {
        "schema": "athena.max-rag-output-plan/v1",
        "query_id": contract["query_id"],
        "routes": list(contract["routes"]),
        "token_budget": token_budget,
        "working_budget": token_budget - reserve,
        "return_reserve": reserve,
        "phases": [
            "COMPILE", "RETRIEVE", "AGREE_DISAGREE", "EVIDENCE_PATH",
            "PARALLEL_EXPANSION", "CONJUGATE_AUDIT", "REPAIR_OR_ABSTAIN",
            "RETURN_PACKET",
        ],
        "stop_rule": (
            "stop at marginal-information threshold, completed requested dimensions, "
            "or protected return reserve"
        ),
        "execution_performed": False,
        **_negative_effects(),
    }
    plan["plan_digest"] = _digest(plan)
    return plan


def evaluate_claim(packet: dict[str, Any]) -> dict[str, Any]:
    status = packet.get("status")
    if status not in {"confirmed", "supported", "plausible", "contested", "insufficient", "refuted"}:
        raise ValueError("unknown claim status")
    uncertainty = float(packet.get("uncertainty", 1.0))
    if not 0.0 <= uncertainty <= 1.0:
        raise ValueError("uncertainty must be within [0,1]")
    support = list(packet.get("support", []))
    independent = int(packet.get("independent_source_count", 0))
    if status in {"confirmed", "supported"}:
        permitted = bool(support) and independent >= 1 and uncertainty <= 0.35
    elif status == "plausible":
        permitted = bool(support) and uncertainty <= 0.60
    else:
        permitted = False
    ceilings = {
        "confirmed": "ASSERT_WITH_BOUND_SCOPE",
        "supported": "STATE_AS_SUPPORTED",
        "plausible": "STATE_AS_PLAUSIBLE_INFERENCE",
        "contested": "PRESERVE_DISAGREEMENT",
        "insufficient": "ABSTAIN_OR_REQUEST_EVIDENCE",
        "refuted": "STATE_TESTED_FAILURE",
    }
    result = {
        "schema": "athena.max-rag-claim-permission/v1",
        "claim": str(packet.get("claim", "")),
        "status": status,
        "claim_ceiling": ceilings[status],
        "generation_permitted": permitted,
        "support_count": len(support),
        "independent_source_count": independent,
        "uncertainty": uncertainty,
        "promotion_authority": False,
        **_negative_effects(),
    }
    result["receipt_digest"] = _digest(result)
    return result


def score_game(
    metrics: dict[str, Any], gates: dict[str, Any],
    semantic_units: int, duplication_rate: float,
) -> dict[str, Any]:
    if set(metrics) != set(SCORE_FIELDS):
        raise ValueError(f"metrics must contain exactly {list(SCORE_FIELDS)}")
    values = {key: float(metrics[key]) for key in SCORE_FIELDS}
    if any(not 0.0 <= value <= 1.0 for value in values.values()):
        raise ValueError("all metric values must be within [0,1]")
    if isinstance(semantic_units, bool) or semantic_units < 0:
        raise ValueError("semantic_units must be nonnegative")
    duplication_rate = float(duplication_rate)
    if not 0.0 <= duplication_rate <= 1.0:
        raise ValueError("duplication_rate must be within [0,1]")
    normalized_gates = {gate: bool(gates.get(gate, False)) for gate in HARD_GATES}
    quality = len(values) / sum(1.0 / max(value, 0.05) for value in values.values())
    eligible = all(normalized_gates.values()) and quality >= 0.70 and semantic_units > 0
    juice = math.floor(
        1000 * (sum(values.values()) / len(values)) * (1.0 + math.log2(1 + semantic_units))
    )
    max_currency = math.floor(
        1000 * quality * math.log2(1 + semantic_units) * (1.0 - duplication_rate)
    ) if eligible else 0
    result = {
        "schema": "athena.max-rag-game-receipt/v1",
        "status": "ADMISSION_REVIEW_ELIGIBLE" if eligible else "SANDBOX_HOLD",
        "metrics": values,
        "hard_gates": normalized_gates,
        "harmonic_quality": quality,
        "semantic_units": semantic_units,
        "duplication_rate": duplication_rate,
        "juice_score": juice,
        "max_currency": max_currency,
        "witness_seals": 1 + int(min(values.values()) >= 0.85) if eligible else 0,
        "external_promotion_authority": False,
        **_negative_effects(),
    }
    result["receipt_digest"] = _digest(result)
    return result


def repair_routes(failed_layer: str) -> dict[str, Any]:
    routes = {
        "query": ["decompose", "expand_aliases", "invert_hypothesis"],
        "coverage": ["broaden_source_classes", "cross_channel", "revision_search"],
        "ranking": ["reweight_routes", "pairwise_rerank", "diversity_rerank"],
        "graph": ["rebuild_edges", "alternate_graph", "verify_entity_resolution"],
        "provenance": ["refetch_source", "bind_exact_span", "lower_claim_ceiling"],
        "contradiction": ["negative_search", "scope_split", "preserve_contested"],
        "permissions": ["authorized_read_route", "record_blocker", "abstain"],
        "generation": ["recompile_claims", "remove_unsupported", "evidence_only_regeneration"],
    }.get(failed_layer, ["isolate_failure", "change_hypothesis", "bounded_replay"])
    return {
        "schema": "athena.max-rag-repair-plan/v1",
        "failed_layer": failed_layer,
        "changed_routes": routes,
        "execution_performed": False,
        "promotion_authority": False,
        **_negative_effects(),
    }


def shadow_manifest() -> dict[str, Any]:
    manifest = {
        "schema": "athena.max-rag-shadow-benchmark/v1",
        "status": "FROZEN_TEST_CONTRACT",
        "cases": [
            {"case_id": case_id, "domain_id": domain, "title": title}
            for case_id, domain, title in SHADOW_CASES
        ],
        "case_count": 12,
        "core_nonregression": [
            "objective_fidelity", "evidence_fidelity", "replayability", "safety_privacy"
        ],
        "promotion_authority": False,
        **_negative_effects(),
    }
    manifest["manifest_digest"] = _digest(manifest)
    return manifest


def shadow_compare(
    baseline: dict[str, Any], candidate: dict[str, Any], witness: dict[str, Any]
) -> dict[str, Any]:
    if baseline.get("case_id") != candidate.get("case_id"):
        raise ValueError("shadow case mismatch")
    if baseline.get("policy_id") == candidate.get("policy_id"):
        raise ValueError("baseline and candidate policies must differ")
    if candidate.get("case_id") not in {row[0] for row in SHADOW_CASES}:
        raise ValueError("unknown shadow case")
    base_metrics = baseline.get("metrics", {})
    cand_metrics = candidate.get("metrics", {})
    if set(base_metrics) != set(SCORE_FIELDS) or set(cand_metrics) != set(SCORE_FIELDS):
        raise ValueError("shadow metrics are incomplete")
    deltas = {key: float(cand_metrics[key]) - float(base_metrics[key]) for key in SCORE_FIELDS}
    regressions = [
        f"CORE_REGRESSION:{key}"
        for key in ("objective_fidelity", "evidence_fidelity", "replayability", "safety_privacy")
        if deltas[key] < -0.02
    ]
    if int(candidate.get("unsupported_claims", 0)) > int(baseline.get("unsupported_claims", 0)):
        regressions.append("UNSUPPORTED_CLAIMS_INCREASED")
    blockers: list[str] = []
    if not bool(candidate.get("rollback_available", False)):
        blockers.append("ROLLBACK_UNAVAILABLE")
    blockers += [f"OPEN_DEFECT:{item}" for item in candidate.get("defects", [])]
    blockers += [
        f"HARD_GATE_FAILED:{gate}"
        for gate in HARD_GATES if not candidate.get("hard_gates", {}).get(gate, False)
    ]
    candidate_digest = _digest(candidate)
    witness_independent = (
        bool(witness.get("passed"))
        and witness.get("witness_id") != candidate.get("policy_id")
        and witness.get("authority_domain") not in {"learner", candidate.get("policy_id")}
        and witness.get("implementation_id") not in {"learner", candidate.get("policy_id")}
    )
    if not witness_independent:
        blockers.append("WITNESS_NOT_INDEPENDENT")
    if witness.get("observation_digest") != candidate_digest:
        blockers.append("WITNESS_DIGEST_MISMATCH")
    gains = [key for key, delta in deltas.items() if delta >= 0.03]
    if not gains:
        blockers.append("NO_MEASURED_GAIN")
    eligible = not regressions and not blockers
    result = {
        "schema": "athena.max-rag-shadow-comparison/v1",
        "case_id": candidate["case_id"],
        "baseline_policy": baseline["policy_id"],
        "candidate_policy": candidate["policy_id"],
        "status": "SHADOW_ELIGIBLE" if eligible else "SANDBOX_HOLD",
        "eligible_for_shadow": eligible,
        "metric_deltas": deltas,
        "gains": gains,
        "regressions": regressions,
        "blockers": blockers,
        "baseline_digest": _digest(baseline),
        "candidate_digest": candidate_digest,
        "witness_id": witness.get("witness_id"),
        "canary_authority": False,
        **_negative_effects(),
    }
    result["comparison_digest"] = _digest(result)
    return result


def shadow_suite(comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {row[0] for row in SHADOW_CASES}
    ids = [row.get("case_id") for row in comparisons]
    observed = set(ids)
    duplicates = sorted(case for case in observed if ids.count(case) > 1)
    missing = sorted(expected - observed)
    failed = sorted(
        row.get("case_id") for row in comparisons if not row.get("eligible_for_shadow", False)
    )
    complete = not missing and not duplicates and len(comparisons) == 12
    eligible = complete and not failed
    result = {
        "schema": "athena.max-rag-shadow-suite/v1",
        "status": "SHADOW_SUITE_PASS" if eligible else "SHADOW_SUITE_HOLD",
        "complete": complete,
        "passed_cases": sum(bool(row.get("eligible_for_shadow")) for row in comparisons),
        "failed_cases": failed,
        "missing_cases": missing,
        "duplicate_cases": duplicates,
        "canary_review_eligible": eligible,
        "canary_authority": False,
        "comparison_digests": [row.get("comparison_digest") for row in comparisons],
        **_negative_effects(),
    }
    result["suite_digest"] = _digest(result)
    return result


def successor_compile(packet: dict[str, Any]) -> dict[str, Any]:
    required = {
        "session_digest", "unresolved_questions", "verified_defects",
        "policy_deltas", "replay_recipe", "rollback_digest",
    }
    missing = sorted(required - set(packet))
    if missing:
        raise ValueError(f"successor packet missing {missing}")
    _require_digest(packet["session_digest"], "session_digest")
    _require_digest(packet["rollback_digest"], "rollback_digest")
    successor = {
        "schema": "athena.max-rag-successor-return/v1",
        "source_plane": {
            "repository": RUNTIME_REPOSITORY,
            "branch": RUNTIME_BRANCH,
            "parent_head": RUNTIME_PARENT_HEAD,
        },
        "target_plane": {
            "repository": CONTROL_REPOSITORY,
            "branch": CONTROL_BRANCH,
            "control_head": CONTROL_HEAD,
            "gate": "INDEPENDENT_CONTROL_REVIEW",
        },
        "registry_digest": REGISTRY_DIGEST,
        "shadow_manifest_digest": shadow_manifest()["manifest_digest"],
        "session_digest": packet["session_digest"],
        "unresolved_questions": list(packet["unresolved_questions"]),
        "verified_defects": list(packet["verified_defects"]),
        "policy_deltas": deepcopy(packet["policy_deltas"]),
        "replay_recipe": deepcopy(packet["replay_recipe"]),
        "rollback_digest": packet["rollback_digest"],
        "requested_transition": "LOCAL_RUNTIME_TO_CONTROL_REVIEW",
        "dispatch_performed": False,
        "external_promotion_authority": False,
        **_negative_effects(),
    }
    successor["return_id"] = "MAXRAG-RETURN-" + _digest(successor).split(":", 1)[1][:24]
    successor["return_digest"] = _digest(successor)
    return successor


def status() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "MAX_RAG_MCP_LOCAL_REVERSIBLE__PROPOSED_NOT_PROMOTED",
        "control": {
            "repository": CONTROL_REPOSITORY,
            "branch": CONTROL_BRANCH,
            "head": CONTROL_HEAD,
        },
        "runtime": {
            "repository": RUNTIME_REPOSITORY,
            "branch": RUNTIME_BRANCH,
            "parent_head": RUNTIME_PARENT_HEAD,
        },
        "stations": 144,
        "registry_digest": REGISTRY_DIGEST,
        "tools": 11,
        "resources": 4,
        "source_execution": False,
        "persistent_endpoint": False,
        "external_promotion_authority": False,
        **_negative_effects(),
    }


def register_max_rag_game_v1(mcp: Any) -> None:
    """Register eleven pure/local tools and four read-only resources."""

    @mcp.tool()
    def max_rag_status() -> str:
        """Return pinned control/runtime lineage and authority boundaries."""
        return _render(status())

    @mcp.tool()
    def max_rag_registry(carrier: str | None = None) -> str:
        """Read the complete KC144 registry or one exact carrier."""
        rows = REGISTRY
        if carrier is not None:
            known = {row["carrier"] for row in REGISTRY}
            if carrier not in known:
                raise ValueError(f"unknown carrier {carrier}")
            rows = [row for row in REGISTRY if row["carrier"] == carrier]
        return _render({
            "schema": "athena.max-rag-kc144-registry/v1",
            "count": len(rows), "carrier": carrier,
            "registry_digest": REGISTRY_DIGEST, "stations": rows,
            **_negative_effects(),
        })

    @mcp.tool()
    def max_rag_query_compile(raw: str, route_budget: int = 9, threshold: float = 0.75) -> str:
        """Compile a query contract without executing retrieval."""
        return _render(compile_query(raw, route_budget, threshold))

    @mcp.tool()
    def max_rag_output_plan(contract_json: str, token_budget: int = 8000) -> str:
        """Compile a bounded output plan with a protected return reserve."""
        return _render(output_plan(_parse_object(contract_json, "contract_json"), token_budget))

    @mcp.tool()
    def max_rag_claim_evaluate(packet_json: str) -> str:
        """Evaluate a claim packet and return its evidence-limited ceiling."""
        return _render(evaluate_claim(_parse_object(packet_json, "packet_json")))

    @mcp.tool()
    def max_rag_score(
        metrics_json: str, gates_json: str,
        semantic_units: int, duplication_rate: float = 0.0,
    ) -> str:
        """Score an episode; JUICE never bypasses hard gates and no promotion occurs."""
        return _render(score_game(
            _parse_object(metrics_json, "metrics_json"),
            _parse_object(gates_json, "gates_json"),
            semantic_units, duplication_rate,
        ))

    @mcp.tool()
    def max_rag_repair_routes(failed_layer: str) -> str:
        """Return changed repair hypotheses without executing external work."""
        return _render(repair_routes(failed_layer))

    @mcp.tool()
    def max_rag_shadow_manifest() -> str:
        """Read the frozen twelve-case shadow benchmark contract."""
        return _render(shadow_manifest())

    @mcp.tool()
    def max_rag_shadow_compare(
        baseline_json: str, candidate_json: str, witness_json: str,
    ) -> str:
        """Compare one baseline/candidate pair under digest-bound witness gates."""
        return _render(shadow_compare(
            _parse_object(baseline_json, "baseline_json"),
            _parse_object(candidate_json, "candidate_json"),
            _parse_object(witness_json, "witness_json"),
        ))

    @mcp.tool()
    def max_rag_shadow_suite(comparisons_json: str) -> str:
        """Aggregate exactly twelve comparisons; result grants review only."""
        return _render(shadow_suite(_parse_list(comparisons_json, "comparisons_json")))

    @mcp.tool()
    def max_rag_successor_compile(packet_json: str) -> str:
        """Compile a non-dispatching successor return for independent control review."""
        return _render(successor_compile(_parse_object(packet_json, "packet_json")))

    @mcp.resource("athena://max-rag/v1/status")
    def max_rag_status_resource() -> str:
        return _render(status())

    @mcp.resource("athena://max-rag/v1/kc144-registry")
    def max_rag_registry_resource() -> str:
        return _render({
            "schema": "athena.max-rag-kc144-registry/v1",
            "count": 144, "registry_digest": REGISTRY_DIGEST,
            "stations": REGISTRY, **_negative_effects(),
        })

    @mcp.resource("athena://max-rag/v1/shadow-benchmark")
    def max_rag_shadow_resource() -> str:
        return _render(shadow_manifest())

    @mcp.resource("athena://max-rag/v1/contract")
    def max_rag_contract_resource() -> str:
        return _render({
            "schema": "athena.max-rag-runtime-contract/v1",
            "hard_gates": list(HARD_GATES),
            "score_fields": list(SCORE_FIELDS),
            "currencies": {
                "JUICE": "motivation only; zero promotion authority",
                "MAX": "requires all hard gates and witnessed quality",
                "Witness Seals": "review gate only",
                "Residual Dust": "reproducible witnessed defects only",
            },
            "promotion_path": ["SANDBOX", "SHADOW", "CANARY", "ADMITTED"],
            "runtime_effect": "LOCAL_PURE_OR_NON_DISPATCHING",
            "external_promotion_authority": False,
            **_negative_effects(),
        })

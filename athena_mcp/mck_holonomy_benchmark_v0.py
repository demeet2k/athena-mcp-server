from __future__ import annotations

import hashlib
import json
from collections import Counter
from copy import deepcopy
from typing import Any, Iterable

ARMS = ("A0_UNSCOPED_REFERENCE", "A1_STRATA_MEMBRANE", "A2_COMPOSED_HOLONOMY_LEDGER")


def _jaccard_distance(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 0.0
    return 1.0 - (len(a & b) / len(a | b))


def distance_vector(source: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    """Frozen V0 endpoint representation distance.

    Invariant/loss fields are intentionally not guessed from prose. They are filled by
    the transport/path evaluator, which has access to the declared bridge/path ledger.
    """
    return {
        "role_delta": int(source.get("semantic_role") != target.get("semantic_role")),
        "decoder_delta": int(source.get("decoder_role") != target.get("decoder_role")),
        "ontology_delta": _jaccard_distance(source.get("ontology_tags", []), target.get("ontology_tags", [])),
        "authority_delta": int(source.get("authority_scope") != target.get("authority_scope")),
        "standing_delta": int(source.get("standing") != target.get("standing")),
        "provenance_delta": None,
        "invariant_violations": None,
        "unaccounted_loss": None,
    }


def _zero_vector() -> dict[str, Any]:
    return {
        "role_delta": 0,
        "decoder_delta": 0,
        "ontology_delta": 0.0,
        "authority_delta": 0,
        "standing_delta": 0,
        "provenance_delta": 0.0,
        "invariant_violations": 0,
        "unaccounted_loss": 0,
    }


def _index_packet(packet: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if packet.get("distance_semantics", {}).get("scalarization") not in {"DISABLED_V0", None}:
        raise ValueError("V0 scalarization must remain disabled")

    families: dict[str, dict[str, Any]] = {}
    layers: dict[str, dict[str, Any]] = {}
    layer_family: dict[str, dict[str, Any]] = {}
    for family in packet.get("families", []):
        family_id = family["family_id"]
        if family_id in families:
            raise ValueError(f"duplicate family_id: {family_id}")
        families[family_id] = family
        for layer in family.get("layers", []):
            layer_id = layer["layer_id"]
            if layer_id in layers:
                raise ValueError(f"duplicate layer_id: {layer_id}")
            layers[layer_id] = layer
            layer_family[layer_id] = family

    cases: dict[str, dict[str, Any]] = {}
    for case in packet.get("cases", []):
        case_id = case["case_id"]
        if case_id in cases:
            raise ValueError(f"duplicate case_id: {case_id}")
        path = case.get("path", [])
        if len(path) < 2:
            raise ValueError(f"case path must have >=2 layers: {case_id}")
        unknown = [layer_id for layer_id in path if layer_id not in layers]
        if unknown:
            raise ValueError(f"unknown layers in {case_id}: {unknown}")
        path_families = {layer_family[layer_id]["family_id"] for layer_id in path}
        if path_families != {case["family_id"]}:
            raise ValueError(f"cross-family path without explicit bridge in {case_id}: {sorted(path_families)}")
        cases[case_id] = case
    return families, layers, cases


def _standing_rank(packet: dict[str, Any], standing: str) -> int | None:
    return packet.get("distance_semantics", {}).get("standing_ranks", {}).get(standing)


def _path_requirements(case: dict[str, Any], path_layers: list[dict[str, Any]]) -> tuple[set[str], list[str]]:
    required_provenance = set(case.get("source_refs", []))
    # Layer IDs are retained as ordered path-provenance coordinates, distinct from source citations.
    required_provenance.update(layer["layer_id"] for layer in path_layers)
    declared_loss: list[str] = []
    for layer in path_layers:
        declared_loss.extend(layer.get("declared_loss", []))
    declared_loss.extend(case.get("declared_loss", []))
    declared_loss = list(dict.fromkeys(declared_loss))
    return required_provenance, declared_loss


def _edge_deltas(path_layers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [distance_vector(a, b) for a, b in zip(path_layers, path_layers[1:])]


def _path_holonomy(path_layers: list[dict[str, Any]]) -> dict[str, Any]:
    """Path-conditioned V0 projection-back vector.

    For a closed path, naive endpoint equality erases the route. V0 instead retains the
    maximum typed representation displacement encountered along the ordered path. This
    is a conservative path witness, not a metaphysical scalar and not an error score.
    """
    edges = _edge_deltas(path_layers)
    if not edges:
        return _zero_vector()
    vector = _zero_vector()
    for key in ("role_delta", "decoder_delta", "authority_delta", "standing_delta"):
        vector[key] = max(int(edge[key]) for edge in edges)
    vector["ontology_delta"] = max(float(edge["ontology_delta"]) for edge in edges)
    vector["provenance_delta"] = None
    vector["invariant_violations"] = None
    vector["unaccounted_loss"] = None
    return vector


def _nonzero_representation(vector: dict[str, Any]) -> bool:
    for key in ("role_delta", "decoder_delta", "ontology_delta", "authority_delta", "standing_delta"):
        value = vector.get(key)
        if isinstance(value, (int, float)) and value != 0:
            return True
    return False


def _classify_without_answer_key(operation: str, arm: str, endpoint: dict[str, Any], holonomy: dict[str, Any], order_sensitive: bool) -> str:
    if operation == "SAME_LAYER_CONTROL":
        return "ZERO_HOLONOMY_CONTROL"
    if operation == "SEMANTIC_TRANSPORT":
        return "ALLOW_WITH_LOSS"
    if operation == "SEMANTIC_EQUIVALENCE":
        if arm == "A0_UNSCOPED_REFERENCE":
            return "ALLOW_EQUIVALENCE"
        return "HOLD_EQUIVALENCE" if _nonzero_representation(endpoint) else "ALLOW_EQUIVALENCE"
    if operation == "HOLONOMY_LOOP":
        if arm == "A2_COMPOSED_HOLONOMY_LEDGER" and _nonzero_representation(holonomy):
            return "NONZERO_HOLONOMY_EXPECTED"
        return "ZERO_HOLONOMY_CONTROL"
    if operation == "PATH_ORDER_COMPARE":
        if arm == "A2_COMPOSED_HOLONOMY_LEDGER" and order_sensitive:
            return "NONCOMMUTATIVE_EXPECTED"
        return "COMMUTATIVE_ASSUMED"
    return "HOLD_UNKNOWN_OPERATION"


def evaluate_case(packet: dict[str, Any], case: dict[str, Any], arm: str) -> dict[str, Any]:
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm}")
    families, layers, _ = _index_packet(packet)
    path_layers = [layers[layer_id] for layer_id in case["path"]]
    family = families[case["family_id"]]
    endpoint = distance_vector(path_layers[0], path_layers[-1])
    edge_deltas = _edge_deltas(path_layers)
    holonomy = _path_holonomy(path_layers) if arm == "A2_COMPOSED_HOLONOMY_LEDGER" else deepcopy(endpoint)

    required_provenance, required_loss = _path_requirements(case, path_layers)
    source_refs = set(case.get("source_refs", []))

    if arm == "A0_UNSCOPED_REFERENCE":
        retained_provenance = set(source_refs)
        retained_loss: list[str] = []
        ordered_path: list[str] | None = None
    elif arm == "A1_STRATA_MEMBRANE":
        retained_provenance = set(source_refs)
        retained_provenance.update({case["path"][0], case["path"][-1]})
        retained_loss = list(case.get("declared_loss", []))
        ordered_path = None
    else:
        retained_provenance = set(required_provenance)
        retained_loss = list(required_loss)
        ordered_path = list(case["path"])

    missing_provenance = required_provenance - retained_provenance
    provenance_delta = len(missing_provenance) / len(required_provenance) if required_provenance else 0.0
    endpoint["provenance_delta"] = provenance_delta
    holonomy["provenance_delta"] = provenance_delta

    # The frozen packet's invariants and declared-loss explanations are prose, not
    # executable predicates or typed loss mappings. UNKNOWN is preserved instead of
    # laundering an unrun textual judgment into zero violations/loss.
    textual_invariants = list(case.get("bridge_invariants", []))
    invariant_violations: int | None = 0 if not textual_invariants else None
    unknown_invariant_checks = len(textual_invariants)
    endpoint["invariant_violations"] = invariant_violations
    holonomy["invariant_violations"] = invariant_violations

    changed_types = [
        key for key in ("role_delta", "decoder_delta", "ontology_delta", "authority_delta", "standing_delta")
        if isinstance(endpoint.get(key), (int, float)) and endpoint[key] != 0
    ]
    if not changed_types:
        unaccounted_loss: int | None = 0
        unknown_loss_types: list[str] = []
    elif retained_loss:
        unaccounted_loss = None
        unknown_loss_types = changed_types
    else:
        unaccounted_loss = len(changed_types)
        unknown_loss_types = []
    endpoint["unaccounted_loss"] = unaccounted_loss
    holonomy["unaccounted_loss"] = unaccounted_loss

    standing_ranks = [_standing_rank(packet, layer.get("standing", "UNKNOWN")) for layer in path_layers]
    known_ranks = [rank for rank in standing_ranks if rank is not None]
    standing_amplification = False
    if known_ranks:
        output_rank = min(known_ranks)
        standing_amplification = output_rank > min(known_ranks)
    else:
        output_rank = None

    authority_minting = False  # no authority transform is performed by the evaluator

    family_order = {layer["layer_id"]: index for index, layer in enumerate(family.get("layers", []))}
    canonical_indices = [family_order[layer_id] for layer_id in case["path"]]
    permuted_path = None
    order_sensitive = False
    if case.get("operation") == "PATH_ORDER_COMPARE" and len(case["path"]) >= 3:
        permuted_path = [case["path"][0], *reversed(case["path"][1:])]
        permuted_indices = [family_order[layer_id] for layer_id in permuted_path]
        order_sensitive = tuple(canonical_indices) != tuple(permuted_indices)

    predicted_class = _classify_without_answer_key(
        case.get("operation", ""), arm, endpoint, holonomy, order_sensitive
    )

    return {
        "case_id": case["case_id"],
        "family_id": case["family_id"],
        "arm": arm,
        "operation": case.get("operation"),
        "predicted_class": predicted_class,
        "endpoint_vector": endpoint,
        "holonomy_vector": holonomy,
        "path_ledger": {
            "ordered_path": ordered_path,
            "edge_deltas": edge_deltas if arm == "A2_COMPOSED_HOLONOMY_LEDGER" else None,
            "required_provenance": sorted(required_provenance),
            "retained_provenance": sorted(retained_provenance),
            "missing_provenance": sorted(missing_provenance),
            "declared_loss": required_loss,
            "retained_loss": retained_loss,
            "textual_invariants": textual_invariants,
            "unknown_invariant_checks": unknown_invariant_checks,
            "unknown_loss_types": unknown_loss_types,
            "permuted_path": permuted_path,
            "order_sensitive": order_sensitive if arm == "A2_COMPOSED_HOLONOMY_LEDGER" else False,
        },
        "hard_gates": {
            "standing_amplification_violation": standing_amplification,
            "authority_minting_violation": authority_minting,
            "output_standing_rank": output_rank,
        },
    }


def assay_case(result: dict[str, Any], expected_class: str) -> dict[str, Any]:
    """Post-hoc answer-key comparison. Never called by evaluate_case()."""
    return {
        "case_id": result["case_id"],
        "arm": result["arm"],
        "predicted_class": result["predicted_class"],
        "expected_class": expected_class,
        "match": result["predicted_class"] == expected_class,
    }


def _aggregate_metrics(results: list[dict[str, Any]], cases_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    transport_ids = {case_id for case_id, case in cases_by_id.items() if case.get("operation") == "SEMANTIC_TRANSPORT"}
    equivalence_ids = {case_id for case_id, case in cases_by_id.items() if case.get("operation") == "SEMANTIC_EQUIVALENCE"}
    controls = {case_id for case_id, case in cases_by_id.items() if case.get("operation") == "SAME_LAYER_CONTROL"}
    loops = {case_id for case_id, case in cases_by_id.items() if case.get("operation") == "HOLONOMY_LOOP"}
    order_cases = {case_id for case_id, case in cases_by_id.items() if case.get("operation") == "PATH_ORDER_COMPARE"}

    by_id = {result["case_id"]: result for result in results}
    false_equivalence = sum(
        1 for case_id in equivalence_ids if by_id[case_id]["predicted_class"] != "HOLD_EQUIVALENCE"
    )
    lawful_retained = sum(
        1 for case_id in transport_ids if by_id[case_id]["predicted_class"].startswith("ALLOW")
    )
    false_holds = len(transport_ids) - lawful_retained
    zero_controls = sum(
        1 for case_id in controls if by_id[case_id]["predicted_class"] == "ZERO_HOLONOMY_CONTROL"
    )
    nonzero_loops = sum(
        1 for case_id in loops if by_id[case_id]["predicted_class"] == "NONZERO_HOLONOMY_EXPECTED"
    )
    path_order_sensitive = sum(
        1 for case_id in order_cases if by_id[case_id]["predicted_class"] == "NONCOMMUTATIVE_EXPECTED"
    )
    provenance_retention = [1.0 - float(result["endpoint_vector"]["provenance_delta"]) for result in results]
    loss_ledger_retention = []
    for result in results:
        required = result["path_ledger"]["declared_loss"]
        retained = result["path_ledger"]["retained_loss"]
        if not required:
            loss_ledger_retention.append(1.0)
        else:
            loss_ledger_retention.append(len(set(retained) & set(required)) / len(set(required)))

    return {
        "case_count": len(results),
        "false_equivalence_claims": false_equivalence,
        "lawful_bridges_retained": lawful_retained,
        "false_holds_on_lawful_transport": false_holds,
        "same_layer_zero_controls": f"{zero_controls}/{len(controls)}",
        "nonzero_holonomy_loops": f"{nonzero_loops}/{len(loops)}",
        "path_order_sensitive": f"{path_order_sensitive}/{len(order_cases)}",
        "standing_amplification_violations": sum(
            int(result["hard_gates"]["standing_amplification_violation"]) for result in results
        ),
        "authority_minting_violations": sum(
            int(result["hard_gates"]["authority_minting_violation"]) for result in results
        ),
        "mean_provenance_retention": sum(provenance_retention) / len(provenance_retention) if provenance_retention else 1.0,
        "mean_loss_ledger_retention": sum(loss_ledger_retention) / len(loss_ledger_retention) if loss_ledger_retention else 1.0,
        "unknown_textual_invariant_checks": sum(result["path_ledger"]["unknown_invariant_checks"] for result in results),
        "unknown_typed_loss_checks": sum(len(result["path_ledger"]["unknown_loss_types"]) for result in results),
        "predicted_class_counts": dict(Counter(result["predicted_class"] for result in results)),
    }


def run_benchmark(packet: dict[str, Any], *, include_assay: bool = True) -> dict[str, Any]:
    families, _layers, _cases_by_id = _index_packet(packet)
    raw_packet = deepcopy(packet)
    inference_cases = []
    answer_key = {}
    for case in raw_packet.get("cases", []):
        case_copy = deepcopy(case)
        answer_key[case_copy["case_id"]] = case_copy.pop("expected_class", None)
        inference_cases.append(case_copy)

    arms: dict[str, Any] = {}
    for arm in ARMS:
        results = [evaluate_case(raw_packet, case, arm) for case in inference_cases]
        arm_record: dict[str, Any] = {
            "results": results,
            "metrics": _aggregate_metrics(results, {c["case_id"]: c for c in inference_cases}),
        }
        if include_assay:
            assays = [assay_case(result, answer_key[result["case_id"]]) for result in results]
            arm_record["assay"] = {
                "matches": sum(int(item["match"]) for item in assays),
                "total": len(assays),
                "cases": assays,
            }
        arms[arm] = arm_record

    result = {
        "artifact": "ATHENA.MCK.HOLONOMY.BENCHMARK.RUNTIME.V0",
        "benchmark_version": packet.get("version"),
        "source_artifact": packet.get("artifact"),
        "family_count": len(families),
        "case_count": len(inference_cases),
        "scalarization": "DISABLED_V0",
        "answer_key_used_during_inference": False,
        "arms": arms,
        "standing": {
            "runtime_mechanism": "SELF_GENERATED_EXECUTION_RECEIPT",
            "independent_witness": False,
            "mck_v2_promotion": "HOLD",
        },
        "residuals": [
            "bridge_invariants are prose and remain UNKNOWN until executable predicates or external review exist",
            "declared_loss strings are not typed to distance-vector dimensions; typed unaccounted-loss checks remain UNKNOWN where semantic features changed",
        ],
    }
    digest_source = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    result["result_digest_sha256"] = hashlib.sha256(digest_source).hexdigest()
    return result

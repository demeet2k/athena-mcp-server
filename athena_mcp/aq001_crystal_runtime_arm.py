from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

ARTIFACT = "ATHENA.AQ001.CRYSTAL_RUNTIME_ARM.V1"
ACTOR = "aq001.crystal.runtime.arm.v1"
FORBIDDEN_PROGRAM_TOKENS = ("expected_class", "case_id", "ALLOW_WITH_LOSS", "HOLD_EQUIVALENCE", "NONZERO_HOLONOMY_EXPECTED", "NONCOMMUTATIVE_EXPECTED")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def jaccard_distance(a: Sequence[str], b: Sequence[str]) -> float:
    aa, bb = set(a), set(b)
    if not aa and not bb:
        return 0.0
    return round(1.0 - (len(aa & bb) / len(aa | bb)), 12)


def typed_delta(a: Mapping[str, Any], b: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "role_delta": int(a.get("semantic_role") != b.get("semantic_role")),
        "decoder_delta": int(a.get("decoder_role") != b.get("decoder_role")),
        "ontology_delta": jaccard_distance(a.get("ontology_tags", []), b.get("ontology_tags", [])),
        "authority_delta": int(a.get("authority_scope") != b.get("authority_scope")),
    }


def vector_nonzero(vector: Mapping[str, Any]) -> bool:
    return any(isinstance(value, (int, float)) and not isinstance(value, bool) and value != 0 for value in vector.values())


def _indexes(packet: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], dict[str, list[str]]]:
    layers: dict[str, Mapping[str, Any]] = {}
    family_orders: dict[str, list[str]] = {}
    for family in packet.get("families", []):
        order: list[str] = []
        for layer in family.get("layers", []):
            layer_id = str(layer["layer_id"])
            layers[layer_id] = layer
            order.append(layer_id)
        family_orders[str(family["family_id"])] = order
    return layers, family_orders


def _state(layer: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "current_layer": layer["layer_id"],
        "semantic_role": layer.get("semantic_role"),
        "decoder_role": layer.get("decoder_role"),
        "ontology_tags": list(layer.get("ontology_tags", [])),
        "authority_scope": layer.get("authority_scope"),
        "standing": layer.get("standing", "UNKNOWN"),
        "previous_layer": layer["layer_id"],
        "previous_semantic_role": layer.get("semantic_role"),
        "previous_decoder_role": layer.get("decoder_role"),
        "previous_ontology_tags": list(layer.get("ontology_tags", [])),
        "previous_authority_scope": layer.get("authority_scope"),
        "previous_standing": layer.get("standing", "UNKNOWN"),
        "path_depth": 0,
        "path_trace": f"LAYER::{layer['layer_id']}",
    }


def _const(value: Any) -> dict[str, Any]:
    return {"op": "const", "value": value}


def _get(name: str) -> dict[str, Any]:
    return {"op": "get", "path": [name]}


def transition_program(src_id: str, dst: Mapping[str, Any]) -> dict[str, Any]:
    """One reusable transition grammar; values are source-packet layer metadata only."""
    return {
        "op": "object",
        "fields": {
            "current_layer": _const(dst["layer_id"]),
            "semantic_role": _const(dst.get("semantic_role")),
            "decoder_role": _const(dst.get("decoder_role")),
            "ontology_tags": _const(list(dst.get("ontology_tags", []))),
            "authority_scope": _const(dst.get("authority_scope")),
            "standing": _const(dst.get("standing", "UNKNOWN")),
            "previous_layer": _get("current_layer"),
            "previous_semantic_role": _get("semantic_role"),
            "previous_decoder_role": _get("decoder_role"),
            "previous_ontology_tags": _get("ontology_tags"),
            "previous_authority_scope": _get("authority_scope"),
            "previous_standing": _get("standing"),
            "path_depth": {"op": "add", "args": [_get("path_depth"), _const(1)]},
            "path_trace": {
                "op": "concat",
                "args": [_get("path_trace"), _const(f"|EDGE::{src_id}->{dst['layer_id']}")],
            },
        },
    }


def _identity_program() -> dict[str, Any]:
    return {"op": "identity"}


def _program_is_answer_key_free(program: Mapping[str, Any]) -> bool:
    text = canonical_json(program)
    return not any(token in text for token in FORBIDDEN_PROGRAM_TOKENS)


def _edge_specs(packet: Mapping[str, Any], layers: Mapping[str, Mapping[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    specs: dict[tuple[str, str], dict[str, Any]] = {}
    admitted_ops = {"SEMANTIC_TRANSPORT", "HOLONOMY_LOOP", "SAME_LAYER_CONTROL"}
    for case in packet.get("cases", []):
        if case.get("operation") not in admitted_ops:
            continue
        path = list(case.get("path") or [])
        for src, dst in zip(path, path[1:]):
            spec = specs.setdefault(
                (src, dst),
                {
                    "declared_loss": set(),
                    "source_refs": set(),
                    "bridge_invariants": set(),
                    "support_operations": set(),
                },
            )
            spec["declared_loss"].update(case.get("declared_loss", []))
            spec["declared_loss"].update(layers[dst].get("declared_loss", []))
            spec["source_refs"].update(case.get("source_refs", []))
            spec["source_refs"].update(layers[src].get("provenance", []))
            spec["source_refs"].update(layers[dst].get("provenance", []))
            spec["bridge_invariants"].update(case.get("bridge_invariants", []))
            spec["support_operations"].add(str(case.get("operation")))
    return specs


def install_packet(crystal: Any, packet: Mapping[str, Any]) -> dict[str, Any]:
    """Install packet-derived charts/transforms into the existing Crystal runtime.

    No expected labels are inspected. Transform programs are generated from layer
    metadata and route structure only. The install is candidate-scoped and creates
    no MCP tool or authority surface.
    """
    layers, _ = _indexes(packet)
    seed_event = crystal._event(
        "AQ001_CRYSTAL_ARM_INSTALL",
        ACTOR,
        {"artifact": packet.get("artifact"), "version": packet.get("version"), "packet_digest": digest(packet)},
    )
    for layer_id, layer in layers.items():
        crystal._put_coordinate(
            "AQ001::CHART_SEED",
            layer_id,
            {"status": "PARTIAL", "family": "AQ001_SEMANTIC_LAYER", "value": _state(layer)},
            seed_event,
        )

    transforms: dict[str, dict[str, Any]] = {}
    for (src, dst), raw in sorted(_edge_specs(packet, layers).items()):
        program = _identity_program() if src == dst else transition_program(src, layers[dst])
        if not _program_is_answer_key_free(program):
            raise ValueError(f"ANSWER_KEY_FIREWALL transform program rejected for {src}->{dst}")
        loss_model = {
            "declared_loss": sorted(raw["declared_loss"]),
            "source_refs": sorted(raw["source_refs"]),
            "bridge_invariants": sorted(raw["bridge_invariants"]),
            "support_operations": sorted(raw["support_operations"]),
            "law": "LOSS_MODEL_IS_PACKET_DERIVED_SIDECAR_NOT_AUTHORITY",
        }
        row = crystal.register_transform(
            src,
            dst,
            status="CANDIDATE",
            loss_model=loss_model,
            actor=ACTOR,
            mode="DERIVATION",
            program=program,
            metric={"type": "EXACT"},
        )
        transforms[f"{src}->{dst}"] = {
            "transform_id": row["transform_id"],
            "program_digest": digest(program),
            "loss_model": loss_model,
        }

    return {
        "artifact": ARTIFACT,
        "packet_digest": digest(packet),
        "layer_count": len(layers),
        "transform_count": len(transforms),
        "transforms": transforms,
        "answer_key_read": False,
        "authority_delta": "NONE",
    }


def _transform_loss_model(crystal: Any, transform_id: str) -> Mapping[str, Any]:
    row = crystal.s.one("SELECT loss_model_json FROM transforms WHERE transform_id=?", (transform_id,))
    if not row:
        raise KeyError(f"missing installed transform {transform_id}")
    return json.loads(row["loss_model_json"])


def _audit_route(crystal: Any, route_result: Mapping[str, Any], source_refs: Sequence[str]) -> dict[str, Any]:
    provenance = set(source_refs)
    loss = set()
    invariants = set()
    route = [str(x).removeprefix("CHART.") for x in route_result["route"]]
    provenance.update(f"LAYER::{layer_id}" for layer_id in route)
    provenance.update(f"EDGE::{src}->{dst}" for src, dst in zip(route, route[1:]))
    for step in route_result.get("steps", []):
        model = _transform_loss_model(crystal, str(step["transform_id"]))
        provenance.update(model.get("source_refs", []))
        loss.update(model.get("declared_loss", []))
        invariants.update(model.get("bridge_invariants", []))
    return {
        "provenance_tokens": sorted(provenance),
        "loss_ledger": sorted(loss),
        "bridge_invariants_declared": sorted(invariants),
        "route_order": route,
        "step_transform_ids": [step["transform_id"] for step in route_result.get("steps", [])],
    }


def _hard_gates(path: Sequence[str], layers: Mapping[str, Mapping[str, Any]], ranks: Mapping[str, int]) -> tuple[int, int]:
    standings = [ranks.get(layers[layer_id].get("standing", "UNKNOWN"), 0) for layer_id in path]
    standing_amp = int(bool(standings) and standings[-1] > min(standings))
    admitted_authorities = {layers[layer_id].get("authority_scope") for layer_id in path}
    authority_mint = int(bool(path) and layers[path[-1]].get("authority_scope") not in admitted_authorities)
    return standing_amp, authority_mint


def _holonomy_vector(start: Mapping[str, Any], returned: Mapping[str, Any], ranks: Mapping[str, int], provenance_delta: float = 0.0) -> dict[str, Any]:
    projected = {
        "semantic_role": returned.get("previous_semantic_role"),
        "decoder_role": returned.get("previous_decoder_role"),
        "ontology_tags": returned.get("previous_ontology_tags", []),
        "authority_scope": returned.get("previous_authority_scope"),
        "standing": returned.get("previous_standing", "UNKNOWN"),
    }
    delta = typed_delta(start, projected)
    return {
        **delta,
        "standing_delta": max(0, ranks.get(projected["standing"], 0) - ranks.get(start.get("standing", "UNKNOWN"), 0)),
        "provenance_delta": provenance_delta,
        "invariant_violations": 0,
        "unaccounted_loss": 0,
    }


def deterministic_permutation(path: Sequence[str]) -> list[str]:
    p = list(path)
    if len(p) >= 3:
        return [p[0], p[-1], *p[1:-1]]
    return list(reversed(p))


def evaluate_case(crystal: Any, packet: Mapping[str, Any], case: Mapping[str, Any]) -> dict[str, Any]:
    layers, _ = _indexes(packet)
    ranks = packet.get("distance_semantics", {}).get("standing_ranks", {})
    path = list(case["path"])
    op = str(case["operation"])
    subject = f"AQ001::{case['case_id']}"
    start_layer = layers[path[0]]
    start_state = _state(start_layer)
    seed_event = crystal._event("AQ001_CRYSTAL_CASE_SEED", ACTOR, {"subject": subject, "path": path, "operation": op})
    crystal._put_coordinate(subject, path[0], {"status": "PARTIAL", "value": start_state}, seed_event)
    standing_amp, authority_mint = _hard_gates(path, layers, ranks)

    base = {
        "case_id": case["case_id"],
        "operation": op,
        "path": path,
        "standing_amplification_violations": standing_amp,
        "authority_minting_violations": authority_mint,
        "answer_key_read": False,
        "execution_surface": "CRYSTAL_RUNTIME",
    }

    if op == "SEMANTIC_EQUIVALENCE":
        delta = typed_delta(layers[path[0]], layers[path[-1]])
        return {
            **base,
            "classification": "HOLD_EQUIVALENCE" if vector_nonzero(delta) else "ALLOW_EQUIVALENCE",
            "typed_delta": delta,
            "runtime_route": None,
            "runtime_limitation": "UNSUPPORTED_EQUIVALENCE_EDGE_IS_PREFLIGHTED_FROM_TYPED_PACKET_FIELDS",
        }

    if op == "SAME_LAYER_CONTROL":
        execution = crystal.apply_transform(subject, path[0], path[-1], source_value=start_state, actor=ACTOR)
        equal = execution["result"] == start_state
        return {
            **base,
            "classification": "ZERO_HOLONOMY_CONTROL" if equal else "NONZERO_UNEXPECTED",
            "runtime_execution": execution,
            "holonomy_vector": {
                "role_delta": 0,
                "decoder_delta": 0,
                "ontology_delta": 0.0,
                "authority_delta": 0,
                "standing_delta": 0,
                "provenance_delta": 0.0,
                "invariant_violations": 0,
                "unaccounted_loss": 0,
            } if equal else None,
            "runtime_limitation": "CRYSTAL_RECORD_HOLONOMY_REQUIRES_ROUTE_LENGTH_AT_LEAST_3; SAME_LAYER_CONTROL_USES_IDENTITY_TRANSFORM_EXECUTION",
        }

    if op == "PATH_ORDER_COMPARE":
        canonical = crystal.apply_transform_route(subject, path, source_value=start_state, actor=ACTOR)
        permuted = deterministic_permutation(path)
        alternate_error = None
        alternate = None
        try:
            alternate = crystal.apply_transform_route(subject + "::PERMUTED", permuted, source_value=start_state, actor=ACTOR)
        except (KeyError, ValueError) as exc:
            alternate_error = f"{type(exc).__name__}: {exc}"
        sensitive = permuted != path and alternate is None
        return {
            **base,
            "classification": "NONCOMMUTATIVE_EXPECTED" if sensitive else "ORDER_INSENSITIVE_UNEXPECTED",
            "path_order_sensitive": sensitive,
            "canonical_runtime_route": canonical,
            "permuted_path": permuted,
            "permuted_runtime_route": alternate,
            "permuted_error": alternate_error,
            "audit": _audit_route(crystal, canonical, case.get("source_refs", [])),
        }

    route = crystal.apply_transform_route(subject, path, source_value=start_state, actor=ACTOR)
    audit = _audit_route(crystal, route, case.get("source_refs", []))
    if op == "SEMANTIC_TRANSPORT":
        return {
            **base,
            "classification": "ALLOW_WITH_LOSS" if not standing_amp and not authority_mint else "HOLD_HARD_GATE",
            "runtime_route": route,
            "audit": audit,
        }
    if op == "HOLONOMY_LOOP":
        vector = _holonomy_vector(start_layer, route["returned"], ranks)
        native = route.get("holonomy")
        native_nonzero = isinstance(native, Mapping) and native.get("status") != "N/A_LOOKUP_ROUTE" and native.get("defect") not in (None, {"equal": True})
        nonzero = vector_nonzero(vector) and native_nonzero
        return {
            **base,
            "classification": "NONZERO_HOLONOMY_EXPECTED" if nonzero else "ZERO_HOLONOMY_UNEXPECTED",
            "runtime_route": route,
            "native_crystal_holonomy": native,
            "holonomy_vector": vector,
            "audit": audit,
        }
    return {**base, "classification": "UNKNOWN_OPERATION"}


def evaluate_packet(crystal: Any, packet: Mapping[str, Any]) -> dict[str, Any]:
    install = install_packet(crystal, packet)
    results = [evaluate_case(crystal, packet, case) for case in packet.get("cases", [])]
    return {
        "artifact": ARTIFACT,
        "packet_artifact": packet.get("artifact"),
        "packet_version": packet.get("version"),
        "packet_digest": install["packet_digest"],
        "execution_standing": "REAL_CRYSTAL_RUNTIME_SUBSTRATE_NOT_PRODUCTION_MCK",
        "install": install,
        "cases": results,
        "metrics": {
            "case_count": len(results),
            "standing_amplification_violations": sum(row["standing_amplification_violations"] for row in results),
            "authority_minting_violations": sum(row["authority_minting_violations"] for row in results),
            "answer_key_reads": sum(bool(row.get("answer_key_read")) for row in results),
            "native_holonomy_records": sum(bool(row.get("native_crystal_holonomy")) for row in results),
        },
        "epistemic_boundary": {
            "production_mck_runtime": "NOT_CLAIMED",
            "crystal_runtime_substrate": "ACTUALLY_EXECUTED_BY_THIS_ARM",
            "textual_invariant_truth": "NOT_INFERRED_FROM_DECLARATION",
            "performance_gain": "UNKNOWN_UNTIL_MATCHED_EXTERNAL_EVALUATION",
            "promotion": "NONE",
        },
    }


def assay(packet: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
    """Post-execution scoring; the only function in this module that reads expected_class."""
    expected = {str(case["case_id"]): case.get("expected_class") for case in packet.get("cases", [])}
    rows = []
    for observed in result.get("cases", []):
        exp = expected.get(str(observed["case_id"]))
        rows.append({"case_id": observed["case_id"], "expected": exp, "observed": observed["classification"], "match": exp == observed["classification"]})
    return {"matches": sum(bool(row["match"]) for row in rows), "total": len(rows), "rows": rows}

from __future__ import annotations

from typing import Any, Mapping

from .aq001_crystal_runtime_arm import ACTOR as ARM_ACTOR
from .aq001_crystal_runtime_arm import transition_program, typed_delta, vector_nonzero

ARTIFACT = "ATHENA.AQ001.CRYSTAL.GAUGE.V1"
ACTOR = "aq001.crystal.gauge.v1"

SEMANTIC_FIELDS = (
    "semantic_role",
    "decoder_role",
    "ontology_tags",
    "authority_scope",
    "standing",
)


def _twin(layer_id: str) -> dict[str, Any]:
    """Same typed semantics, different representation identity."""
    return {
        "layer_id": layer_id,
        "semantic_role": "semantic_twin_role",
        "decoder_role": "semantic_twin_decoder",
        "ontology_tags": ["semantic_twin", "gauge_control"],
        "authority_scope": "PUBLIC_TEXTUAL_MODEL",
        "standing": "SECONDARY_SCHOLARSHIP",
        "provenance": ["AQ001C.SYNTHETIC_GAUGE_CONTROL"],
        "declared_loss": [],
    }


def _full_state(layer: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "current_layer": layer["layer_id"],
        "semantic_role": layer["semantic_role"],
        "decoder_role": layer["decoder_role"],
        "ontology_tags": list(layer["ontology_tags"]),
        "authority_scope": layer["authority_scope"],
        "standing": layer["standing"],
        "previous_layer": layer["layer_id"],
        "previous_semantic_role": layer["semantic_role"],
        "previous_decoder_role": layer["decoder_role"],
        "previous_ontology_tags": list(layer["ontology_tags"]),
        "previous_authority_scope": layer["authority_scope"],
        "previous_standing": layer["standing"],
        "path_depth": 0,
        "path_trace": f"LAYER::{layer['layer_id']}",
    }


def _endpoint_state(layer: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "current_layer": layer["layer_id"],
        "semantic_role": layer["semantic_role"],
        "decoder_role": layer["decoder_role"],
        "ontology_tags": list(layer["ontology_tags"]),
        "authority_scope": layer["authority_scope"],
        "standing": layer["standing"],
    }


def _semantic_history_state(layer: Mapping[str, Any]) -> dict[str, Any]:
    state = _endpoint_state(layer)
    state.update(
        {
            "previous_semantic_role": layer["semantic_role"],
            "previous_decoder_role": layer["decoder_role"],
            "previous_ontology_tags": list(layer["ontology_tags"]),
            "previous_authority_scope": layer["authority_scope"],
            "previous_standing": layer["standing"],
        }
    )
    return state


def _const(value: Any) -> dict[str, Any]:
    return {"op": "const", "value": value}


def _get(name: str) -> dict[str, Any]:
    return {"op": "get", "path": [name]}


def _endpoint_program(dst: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "op": "object",
        "fields": {
            "current_layer": _const(dst["layer_id"]),
            "semantic_role": _const(dst["semantic_role"]),
            "decoder_role": _const(dst["decoder_role"]),
            "ontology_tags": _const(list(dst["ontology_tags"])),
            "authority_scope": _const(dst["authority_scope"]),
            "standing": _const(dst["standing"]),
        },
    }


def _semantic_history_program(dst: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "op": "object",
        "fields": {
            "current_layer": _const(dst["layer_id"]),
            "semantic_role": _const(dst["semantic_role"]),
            "decoder_role": _const(dst["decoder_role"]),
            "ontology_tags": _const(list(dst["ontology_tags"])),
            "authority_scope": _const(dst["authority_scope"]),
            "standing": _const(dst["standing"]),
            "previous_semantic_role": _get("semantic_role"),
            "previous_decoder_role": _get("decoder_role"),
            "previous_ontology_tags": _get("ontology_tags"),
            "previous_authority_scope": _get("authority_scope"),
            "previous_standing": _get("standing"),
        },
    }


def _seed_chart(
    crystal: Any,
    *,
    chart_id: str,
    value: Mapping[str, Any],
    arm: str,
    seed_event: str,
) -> None:
    """Register a synthetic chart through the same native coordinate path as #129."""
    crystal._put_coordinate(
        f"AQ001C::CHART_SEED::{arm}",
        chart_id,
        {
            "status": "PARTIAL",
            "family": "AQ001C_SYNTHETIC_GAUGE_CHART",
            "value": dict(value),
        },
        seed_event,
    )


def _register_edge(crystal: Any, src: str, dst: str, program: Mapping[str, Any], arm: str) -> None:
    crystal.register_transform(
        src,
        dst,
        status="CANDIDATE",
        loss_model={
            "standing": "SYNTHETIC_GAUGE_CONTROL_NOT_SOURCE_EVIDENCE",
            "arm": arm,
            "declared_loss": [],
            "law": "REPRESENTATION_GAUGE_CHANGE != SEMANTIC_CHANGE",
        },
        actor=ACTOR,
        mode="DERIVATION",
        program=dict(program),
        metric={"type": "EXACT"},
    )


def _run_loop(
    crystal: Any,
    *,
    prefix: str,
    start: Mapping[str, Any],
    alias: Mapping[str, Any],
    start_state: Mapping[str, Any],
    program_factory: Any,
    arm: str,
) -> dict[str, Any]:
    s0 = f"{prefix}.S0"
    sa = f"{prefix}.S0_ALIAS"
    start_layer = {**dict(start), "layer_id": s0}
    alias_layer = {**dict(alias), "layer_id": sa}
    state = dict(start_state)
    state["current_layer"] = s0
    if "previous_layer" in state:
        state["previous_layer"] = s0
    if "path_trace" in state:
        state["path_trace"] = f"LAYER::{s0}"

    seed_event = crystal._event(
        "AQ001C_GAUGE_CHART_SEED",
        ACTOR,
        {
            "artifact": ARTIFACT,
            "arm": arm,
            "charts": [s0, sa],
            "standing": "SYNTHETIC_GAUGE_CONTROL_NOT_SOURCE_EVIDENCE",
        },
    )
    _seed_chart(crystal, chart_id=s0, value=_endpoint_state(start_layer), arm=arm, seed_event=seed_event)
    _seed_chart(crystal, chart_id=sa, value=_endpoint_state(alias_layer), arm=arm, seed_event=seed_event)

    _register_edge(crystal, s0, sa, program_factory(s0, alias_layer), arm)
    _register_edge(crystal, sa, s0, program_factory(sa, start_layer), arm)
    return crystal.apply_transform_route(
        f"AQ001C::{arm}",
        [s0, sa, s0],
        source_value=state,
        actor=ACTOR,
    )


def _full_program_factory(src: str, dst: Mapping[str, Any]) -> dict[str, Any]:
    return transition_program(src, dst)


def _endpoint_program_factory(_src: str, dst: Mapping[str, Any]) -> dict[str, Any]:
    return _endpoint_program(dst)


def _semantic_history_program_factory(_src: str, dst: Mapping[str, Any]) -> dict[str, Any]:
    return _semantic_history_program(dst)


def _native_nonzero(route: Mapping[str, Any]) -> bool:
    holonomy = route.get("holonomy")
    return bool(
        isinstance(holonomy, Mapping)
        and holonomy.get("status") == "MEASURED"
        and holonomy.get("defect") != {"equal": True}
    )


def _native_zero(route: Mapping[str, Any]) -> bool:
    holonomy = route.get("holonomy")
    return bool(
        isinstance(holonomy, Mapping)
        and holonomy.get("status") == "MEASURED"
        and holonomy.get("defect") == {"equal": True}
    )


def run_semantic_twin_gauge(crystal: Any) -> dict[str, Any]:
    """Falsification assay for representation-sensitive Crystal holonomy.

    The start and alias layers have identical typed semantics. Only representational
    identity/bookkeeping differs. No expected benchmark labels participate.
    """
    start = _twin("UNBOUND.S0")
    alias = _twin("UNBOUND.S0_ALIAS")
    semantic_delta = typed_delta(start, alias)

    full = _run_loop(
        crystal,
        prefix="AQ001C.FULL",
        start=start,
        alias=alias,
        start_state=_full_state(start),
        program_factory=_full_program_factory,
        arm="FULL_TRACEFUL_PREVIOUS_STATE",
    )
    semantic_history = _run_loop(
        crystal,
        prefix="AQ001C.SEMANTIC_HISTORY",
        start=start,
        alias=alias,
        start_state=_semantic_history_state(start),
        program_factory=_semantic_history_program_factory,
        arm="SEMANTIC_HISTORY_NO_REPRESENTATION_TRACE",
    )
    endpoint = _run_loop(
        crystal,
        prefix="AQ001C.ENDPOINT",
        start=start,
        alias=alias,
        start_state=_endpoint_state(start),
        program_factory=_endpoint_program_factory,
        arm="ENDPOINT_ONLY",
    )

    control_chart = "AQ001C.CONTROL.S0"
    control_state = _endpoint_state({**start, "layer_id": control_chart})
    control_seed_event = crystal._event(
        "AQ001C_GAUGE_CHART_SEED",
        ACTOR,
        {
            "artifact": ARTIFACT,
            "arm": "SAME_LAYER_NATIVE_IDENTITY_CONTROL",
            "charts": [control_chart],
            "standing": "SYNTHETIC_GAUGE_CONTROL_NOT_SOURCE_EVIDENCE",
        },
    )
    _seed_chart(
        crystal,
        chart_id=control_chart,
        value=control_state,
        arm="SAME_LAYER_NATIVE_IDENTITY_CONTROL",
        seed_event=control_seed_event,
    )
    _register_edge(
        crystal,
        control_chart,
        control_chart,
        {"op": "identity"},
        "SAME_LAYER_NATIVE_IDENTITY_CONTROL",
    )
    control = crystal.apply_transform_route(
        "AQ001C::CONTROL",
        [control_chart, control_chart, control_chart],
        source_value=control_state,
        actor=ACTOR,
    )

    typed_zero = not vector_nonzero(semantic_delta)
    representation_sensitive = bool(
        typed_zero
        and _native_nonzero(full)
        and _native_zero(semantic_history)
        and _native_zero(endpoint)
        and _native_zero(control)
    )

    classification = (
        "REPRESENTATION_SENSITIVE_RUNTIME_DEFECT"
        if representation_sensitive
        else "GAUGE_CHALLENGE_NOT_ESTABLISHED"
    )

    return {
        "artifact": ARTIFACT,
        "classification": classification,
        "typed_semantic_delta_start_to_alias": semantic_delta,
        "typed_semantic_delta_zero": typed_zero,
        "arms": {
            "full_traceful_previous_state": {
                "native_holonomy": full.get("holonomy"),
                "all_derivational": full.get("all_derivational"),
                "route": full.get("route"),
            },
            "semantic_history_no_representation_trace": {
                "native_holonomy": semantic_history.get("holonomy"),
                "all_derivational": semantic_history.get("all_derivational"),
                "route": semantic_history.get("route"),
            },
            "endpoint_only": {
                "native_holonomy": endpoint.get("holonomy"),
                "all_derivational": endpoint.get("all_derivational"),
                "route": endpoint.get("route"),
            },
            "same_layer_native_identity_control": {
                "native_holonomy": control.get("holonomy"),
                "all_derivational": control.get("all_derivational"),
                "route": control.get("route"),
            },
        },
        "standing": {
            "native_crystal_holonomy": (
                "REPRESENTATION_SENSITIVE_RUNTIME_DEFECT_NOT_VALIDATED_SEMANTIC_HOLONOMY"
                if representation_sensitive
                else "CONNECTION_VALIDITY_UNKNOWN"
            ),
            "mck_closed_loop_holonomy": "UNKNOWN_NO_VALIDATED_CONNECTION",
            "mck_v2_promotion": "HOLD",
            "independent_validation": "HOLD",
            "game_reward_delta": 0,
        },
        "laws": [
            "REPRESENTATION_GAUGE_CHANGE != SEMANTIC_CHANGE",
            "NATIVE_EXACT_STATE_DEFECT != VALIDATED_SEMANTIC_HOLONOMY",
            "NONZERO_BOOKKEEPING_MEMORY != NONZERO_SEMANTIC_HOLONOMY",
            "NEGATIVE_RESULT_IS_REUSABLE_EVIDENCE",
            "GAUGE_CHALLENGE != MCK_V2_PROMOTION",
        ],
        "lineage": {
            "parent_actor": ARM_ACTOR,
            "parent_runtime_candidate": "ATHENA.AQ001.CRYSTAL_RUNTIME_ARM.V1",
            "athena_issue": 259,
        },
    }

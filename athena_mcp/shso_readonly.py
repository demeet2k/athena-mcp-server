from __future__ import annotations

"""Pure read-only SHSO organism-pressure projection.

This is a deliberately small public-runtime port of the private semantic contract
`ATHENA.SHSO.READONLY.BRIDGE.V1`.  It does not port the private V2a/V2b/V2c
reducers and cannot create health/ecology truth by itself.  It only validates
caller-supplied advisory packets and translates them into a non-authoritative
work/organism pressure label.

PRESSURE != DISPATCH.  READY_BUILD != EXECUTION_PERMISSION.
"""

import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence

SHSO_READONLY_VERSION = "ATHENA.SHSO.READONLY.RUNTIME.V1"
PRIVATE_SEMANTIC_CONTRACT = "ATHENA.SHSO.READONLY.BRIDGE.V1"
PRIVATE_V2D_HEAD = "0aa81433ee35ef27a819023594f621ab1dfe909c"
PRIVATE_RECONCILIATION_COMMIT = "98bda154c3c99de82d047b13b1aaaf4944772102"
PUBLIC_RUNTIME_BASE_HEAD = "d8bb4cc6e2e6861eeb7141dc52a2efcea252ff36"
BEHAVIORAL_TREATMENT_EFFECT = "UNKNOWN"

HEALTH_PHASES = {
    "HARD_GATE_COMPROMISED",
    "RECOVERING",
    "BRITTLE",
    "HERDED",
    "FRAGMENTED",
    "SATURATED",
    "GRIDLOCKED",
    "EXPLORATORY",
    "RESPONSIVE",
    "MIXED",
}
ECOLOGY_STATUSES = {
    "CLASSIFIED",
    "AMBIGUOUS",
    "UNKNOWN_INSUFFICIENT_COVERAGE",
    "UNKNOWN_LOW_SIGNAL",
}
META_TRANSITION_CLASSES = {
    "VERIFY",
    "CONTROL",
    "META",
    "META_OBSERVE",
    "REFLECT",
    "SELF_PLAY",
}
HEALTH_PRESSURES = {
    "HERDED": "PRESERVE_NEUTRAL_SCOUT",
    "BRITTLE": "PRESERVE_RESERVE_ADVISORY",
    "FRAGMENTED": "BRIDGE_LOCAL_GUILDS_ADVISORY",
    "SATURATED": "REDUCE_COORDINATION_ADVISORY",
    "RECOVERING": "RECOVERY_RESERVE_ADVISORY",
}
PRESSURE_LABELS = (
    "HOLD_HARD_GATE",
    "VERIFY_MANDATORY_BARRIER_ADVISORY",
    "BUILD_PIVOT_ADVISORY",
    "VERIFY_BATCH_ADVISORY",
    "PRESERVE_NEUTRAL_SCOUT",
    "PRESERVE_RESERVE_ADVISORY",
    "BRIDGE_LOCAL_GUILDS_ADVISORY",
    "REDUCE_COORDINATION_ADVISORY",
    "RECOVERY_RESERVE_ADVISORY",
    "BUILD_CONTINUE_ADVISORY",
    "NO_ORGANISM_ACTION",
)

FORBIDDEN_PRIVATE_KEYS = {
    "chain_of_thought",
    "private_chain_of_thought",
    "hidden_reasoning",
    "scratchpad",
}
AUTHORITY_ASSERTION_KEYS = {
    "execution_authority",
    "dispatch_authority",
    "claim_authority",
    "merge_authority",
    "git_mutation_authority",
    "prompt_promotion_authority",
    "scheduler_mutation_authority",
    "morphology_mutation_authority",
    "world_state_mutation_authority",
}
FALSE_ONLY_FLAGS = {
    "execution_authority_granted",
    "dispatch_authority_granted",
    "claim_authority_granted",
    "merge_authority_granted",
    "prompt_promotion_authority_granted",
    "scheduler_mutation_performed",
    "git_mutation_performed",
    "morphology_mutation_performed",
    "external_side_effects_performed",
    "world_truth_proven",
    "authority_truth_proven",
    "behavioral_gain_proven",
    "criticality_proven",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _walk_items(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key), item
            yield from _walk_items(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_items(item)


def _validate_public_payload(value: Any) -> None:
    for key, item in _walk_items(value):
        if key in FORBIDDEN_PRIVATE_KEYS:
            raise ValueError(f"forbidden_private_key:{key}")
        if key in AUTHORITY_ASSERTION_KEYS:
            raise ValueError(f"forbidden_authority_assertion:{key}")
        if key in FALSE_ONLY_FLAGS and item is not False:
            raise ValueError(f"authority_or_truth_flag_must_be_false:{key}")


def _require_bool(name: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be bool")
    return value


def _require_text(name: str, value: Any) -> str:
    out = str(value or "").strip()
    if not out:
        raise ValueError(f"{name} required")
    return out


def _validate_health(packet: Mapping[str, Any]) -> str:
    if not isinstance(packet, Mapping):
        raise ValueError("health_advisory must be object")
    _validate_public_payload(packet)
    if packet.get("kind") != "HEALTH_ADVISORY":
        raise ValueError("health_advisory.kind must be HEALTH_ADVISORY")
    phase = _require_text("health_advisory.diagnostic_phase", packet.get("diagnostic_phase"))
    if phase not in HEALTH_PHASES:
        raise ValueError("unsupported health diagnostic_phase")
    if packet.get("criticality_proven") is not False:
        raise ValueError("health_advisory.criticality_proven must be false")
    if packet.get("phase_is_heuristic") is not True:
        raise ValueError("health_advisory.phase_is_heuristic must be true")
    if packet.get("behavioral_gain_proven") is not False:
        raise ValueError("health_advisory.behavioral_gain_proven must be false")
    if "execution_authority_granted" in packet and packet.get("execution_authority_granted") is not False:
        raise ValueError("health advisory cannot grant execution authority")
    return phase


def _validate_ecology(packet: Mapping[str, Any]) -> str:
    if not isinstance(packet, Mapping):
        raise ValueError("ecology_advisory must be object")
    _validate_public_payload(packet)
    if packet.get("kind") != "ECOLOGY_ADVISORY":
        raise ValueError("ecology_advisory.kind must be ECOLOGY_ADVISORY")
    status = _require_text("ecology_advisory.status", packet.get("status"))
    if status not in ECOLOGY_STATUSES:
        raise ValueError("unsupported ecology status")
    if packet.get("world_truth_proven") is not False:
        raise ValueError("ecology_advisory.world_truth_proven must be false")
    if "morphology_mutation_performed" in packet and packet.get("morphology_mutation_performed") is not False:
        raise ValueError("ecology advisory cannot mutate morphology")
    return status


def _no_authority_envelope() -> dict[str, Any]:
    return {
        "external_side_effects_performed": False,
        "git_mutation_performed": False,
        "scheduler_mutation_performed": False,
        "claim_authority_granted": False,
        "dispatch_authority_granted": False,
        "execution_authority_granted": False,
        "merge_authority_granted": False,
        "morphology_mutation_performed": False,
        "prompt_promotion_authority_granted": False,
        "world_truth_proven": False,
        "authority_truth_proven": False,
        "behavioral_gain_proven": False,
    }


def project_organism_pressure(
    health_advisory: Mapping[str, Any],
    ecology_advisory: Mapping[str, Any],
    *,
    ready_build_exists: bool,
    previous_transition_classes: Sequence[str],
    verification_barrier_due: bool,
    verification_barrier_mandatory: bool,
) -> dict[str, Any]:
    """Project SHSO advisory state into pressure only; never dispatch or mutate."""
    phase = _validate_health(health_advisory)
    ecology_status = _validate_ecology(ecology_advisory)
    ready = _require_bool("ready_build_exists", ready_build_exists)
    barrier_due = _require_bool("verification_barrier_due", verification_barrier_due)
    barrier_mandatory = _require_bool(
        "verification_barrier_mandatory", verification_barrier_mandatory
    )
    if not isinstance(previous_transition_classes, Sequence) or isinstance(
        previous_transition_classes, (str, bytes)
    ):
        raise ValueError("previous_transition_classes must be array")
    previous = [str(item).strip().upper() for item in previous_transition_classes]
    if any(not item for item in previous):
        raise ValueError("previous_transition_classes entries must be non-empty")
    previous = previous[-2:]

    builder_starved = bool(
        ready
        and len(previous) == 2
        and all(item in META_TRANSITION_CLASSES for item in previous)
    )
    morphology_action_allowed = bool(
        ecology_status == "CLASSIFIED" and phase != "HARD_GATE_COMPROMISED"
    )
    secondary: list[str] = []
    maintenance = HEALTH_PRESSURES.get(phase)
    if maintenance:
        secondary.append(maintenance)

    reasons: list[str] = []
    if phase == "HARD_GATE_COMPROMISED":
        primary = "HOLD_HARD_GATE"
        reasons.append("hard_gate_compromise_precedes_work_first_pressure")
    elif barrier_mandatory:
        primary = "VERIFY_MANDATORY_BARRIER_ADVISORY"
        reasons.append("mandatory_verification_boundary")
    elif builder_starved:
        primary = "BUILD_PIVOT_ADVISORY"
        reasons.append("ready_build_after_two_meta_or_verification_transitions")
    elif barrier_due:
        primary = "VERIFY_BATCH_ADVISORY"
        reasons.append("coherent_verification_barrier_due")
    elif maintenance:
        primary = maintenance
        reasons.append("health_phase_requests_organism_maintenance")
    elif ready:
        primary = "BUILD_CONTINUE_ADVISORY"
        reasons.append("ready_build_exists_without_typed_blocker")
    else:
        primary = "NO_ORGANISM_ACTION"
        reasons.append("no_specific_read_only_pressure")

    if ecology_status != "CLASSIFIED":
        reasons.append("ecology_uncertain_no_morphology_action")

    source = {
        "health_advisory": dict(health_advisory),
        "ecology_advisory": dict(ecology_advisory),
        "ready_build_exists": ready,
        "previous_transition_classes": previous,
        "verification_barrier_due": barrier_due,
        "verification_barrier_mandatory": barrier_mandatory,
    }
    out = {
        "version": SHSO_READONLY_VERSION,
        "kind": "SHSO_ORGANISM_PRESSURE_ADVISORY",
        "primary_pressure": primary,
        "secondary_pressures": secondary,
        "health_phase": phase,
        "ecology_status": ecology_status,
        "morphology_action_allowed": morphology_action_allowed,
        "builder_starvation_detected": builder_starved,
        "previous_transition_classes": previous,
        "reasons": reasons,
        "scheduler_action_performed": False,
        "worker_dispatched": False,
        "prompt_candidate_activated": False,
        "behavioral_treatment_effect": BEHAVIORAL_TREATMENT_EFFECT,
        "input_digest": digest(source),
    }
    out.update(_no_authority_envelope())
    return out


def manifest() -> dict[str, Any]:
    out = {
        "version": SHSO_READONLY_VERSION,
        "kind": "SHSO_READONLY_RUNTIME_MANIFEST",
        "standing": "READ_ONLY_RUNTIME_EXTENSION_CANDIDATE",
        "private_semantic_contract": PRIVATE_SEMANTIC_CONTRACT,
        "private_v2d_head": PRIVATE_V2D_HEAD,
        "private_reconciliation_commit": PRIVATE_RECONCILIATION_COMMIT,
        "public_runtime_base_head": PUBLIC_RUNTIME_BASE_HEAD,
        "behavioral_treatment_effect": BEHAVIORAL_TREATMENT_EFFECT,
        "ports_full_private_shso_reducers": False,
        "operations": ["athena_shso_project_organism_pressure"],
        "pressure_labels": list(PRESSURE_LABELS),
        "health_pressure_map": dict(HEALTH_PRESSURES),
        "laws": [
            "SHSO != WHOLE_ORGANISM",
            "SHSO_HEALTH != SCHEDULER_AUTHORITY",
            "SHSO_PRESSURE != DISPATCH",
            "READY_BUILD_SIGNAL != EXECUTION_PERMISSION",
            "HARD_GATE_HOLD > WORK_FIRST_PRESSURE",
            "UNKNOWN_ECOLOGY -> NO_MORPHOLOGY_ACTION",
            "CALLER_SUPPLIED_ADVISORY != WORLD_TRUTH",
            "READ_ONLY_RUNTIME_EXTENSION != TREATMENT_DEPLOYMENT",
            "PRIVATE_SEMANTIC_CONTRACT != PUBLIC_RUNTIME_RELEASE_QUALIFICATION",
        ],
    }
    out.update(_no_authority_envelope())
    return out


def benchmark() -> dict[str, Any]:
    """Deterministic contract checks; not behavioral/runtime efficacy evidence."""
    def health(phase: str) -> dict[str, Any]:
        return {
            "kind": "HEALTH_ADVISORY",
            "diagnostic_phase": phase,
            "criticality_proven": False,
            "phase_is_heuristic": True,
            "behavioral_gain_proven": False,
            "execution_authority_granted": False,
        }

    def ecology(status: str) -> dict[str, Any]:
        return {
            "kind": "ECOLOGY_ADVISORY",
            "status": status,
            "world_truth_proven": False,
            "morphology_mutation_performed": False,
        }

    hard = project_organism_pressure(
        health("HARD_GATE_COMPROMISED"),
        ecology("CLASSIFIED"),
        ready_build_exists=True,
        previous_transition_classes=["VERIFY", "META"],
        verification_barrier_due=False,
        verification_barrier_mandatory=False,
    )
    unknown = project_organism_pressure(
        health("HERDED"),
        ecology("AMBIGUOUS"),
        ready_build_exists=False,
        previous_transition_classes=[],
        verification_barrier_due=False,
        verification_barrier_mandatory=False,
    )
    return {
        "SHSO_READONLY_V1__HARD_GATE_PRECEDENCE": hard["primary_pressure"]
        == "HOLD_HARD_GATE",
        "SHSO_READONLY_V1__UNKNOWN_ECOLOGY_BLOCKS_MORPH_ACTION": unknown[
            "morphology_action_allowed"
        ]
        is False,
        "SHSO_READONLY_V1__NO_EXECUTION_AUTHORITY": hard[
            "execution_authority_granted"
        ]
        is False,
        "SHSO_READONLY_V1__BEHAVIORAL_EFFECT_UNKNOWN": BEHAVIORAL_TREATMENT_EFFECT
        == "UNKNOWN",
    }


__all__ = [
    "BEHAVIORAL_TREATMENT_EFFECT",
    "PRIVATE_SEMANTIC_CONTRACT",
    "PRIVATE_V2D_HEAD",
    "PUBLIC_RUNTIME_BASE_HEAD",
    "SHSO_READONLY_VERSION",
    "benchmark",
    "manifest",
    "project_organism_pressure",
]

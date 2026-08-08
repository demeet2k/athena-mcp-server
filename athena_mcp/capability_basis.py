from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

ARTIFACT = "ATHENA.CAPABILITY.BASIS.V1"
DESCRIPTOR_ARTIFACT = "ATHENA.CAPABILITY.DESCRIPTOR.V1"
RUNTIME_WITNESS = "IN_PROCESS_REGISTERED_SURFACE"

NEGOTIATED_PREFIXES = (
    "athena_prompt_",
    "athena_frontier_",
    "athena_rehydration_",
    "athena_agent_",
    "athena_capability_",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _descriptor(
    operation: str,
    capability_class: str,
    component: str,
    effect: str,
    authority_class: str,
    freshness_dependencies: Iterable[str],
    preconditions: Iterable[str],
    replayability: str,
    rollback_or_compensation: str,
) -> dict[str, Any]:
    return {
        "artifact": DESCRIPTOR_ARTIFACT,
        "operation": operation,
        "capability_class": capability_class,
        "component": component,
        "effect": effect,
        "authority_class": authority_class,
        "freshness_dependencies": sorted(set(freshness_dependencies)),
        "preconditions": list(preconditions),
        "replayability": replayability,
        "rollback_or_compensation": rollback_or_compensation,
    }


# This map describes the canonical control-plane generation on the branch where
# it lives. It does not make an operation exposed. Exposure is derived only
# from the registered runtime name set supplied to derive_operational_basis().
# A newly registered negotiated operation must be classified in the same lineage
# or it appears as UNCLASSIFIED and semantic auto-selection fails closed.
CONTROL_CAPABILITY_DESCRIPTORS: dict[str, dict[str, Any]] = {
    # Machine-readable observation of the operational basis itself. It is a
    # BOOTSTRAP/REFRESH capability because it informs operator selection but
    # grants no execution permission.
    "athena_capability_basis": _descriptor(
        "athena_capability_basis", "BOOTSTRAP_REFRESH", "capability_basis", "READ_ONLY",
        "OBSERVE_RUNTIME_BASIS", ["REGISTERED_RUNTIME_SURFACE"],
        ["current in-process tool registration"],
        "DETERMINISTIC_SURFACE_DIGEST", "none; read-only descriptor projection",
    ),

    # Prompt/runtime policy reads.
    "athena_prompt_hydrate": _descriptor(
        "athena_prompt_hydrate", "PROMPT", "prompt_runtime", "READ_ONLY",
        "OBSERVE_POLICY", ["PROMPT_GIT_HEAD"], ["configured Git brain"],
        "DETERMINISTIC_CONTENT_DIGEST", "none; read-only",
    ),
    "athena_prompt_compile": _descriptor(
        "athena_prompt_compile", "PROMPT", "prompt_runtime", "READ_ONLY",
        "OBSERVE_POLICY", ["PROMPT_GIT_HEAD"], ["configured Git brain"],
        "DETERMINISTIC_CONTENT_DIGEST", "none; read-only",
    ),
    "athena_prompt_freshness": _descriptor(
        "athena_prompt_freshness", "PROMPT", "prompt_runtime", "READ_ONLY",
        "OBSERVE_POLICY", ["PROMPT_GIT_HEAD", "PROMPT_STACK_DIGEST"],
        ["expected Git head"], "DETERMINISTIC_COMPARISON", "none; read-only",
    ),
    # Prompt self-engineering writes remain bounded and do not self-authorize.
    "athena_prompt_propose": _descriptor(
        "athena_prompt_propose", "PROMPT", "prompt_runtime", "GIT_WRITE_BOUNDED",
        "PROMPT_PROPOSAL", ["PROMPT_GIT_HEAD"],
        ["exact expected Git head", "candidate metadata", "rollback path"],
        "GIT_EVENT_LINEAGE", "close/revert candidate lineage; canonical target unchanged",
    ),
    "athena_prompt_experiment": _descriptor(
        "athena_prompt_experiment", "PROMPT", "prompt_runtime", "GIT_WRITE_BOUNDED",
        "PROMPT_EXPERIMENT", ["PROMPT_GIT_HEAD", "CANDIDATE_IDENTITY"],
        ["exact expected Git head", "candidate exists"],
        "GIT_EVENT_LINEAGE", "append corrective experiment/event; do not erase history",
    ),
    "athena_prompt_activate": _descriptor(
        "athena_prompt_activate", "PROMPT", "prompt_runtime", "GIT_WRITE_BOUNDED",
        "PROMPT_SCOPED_ACTIVATION", ["PROMPT_GIT_HEAD", "CANDIDATE_IDENTITY"],
        ["TESTED candidate", "observed witness", "declared scope", "exact expected Git head"],
        "GIT_EVENT_LINEAGE", "retire/rollback scoped overlay through new Git event",
    ),
    "athena_prompt_promote": _descriptor(
        "athena_prompt_promote", "PROMPT", "prompt_runtime", "GIT_WRITE_BOUNDED",
        "PROMPT_CANONICAL_PROMOTION", ["PROMPT_GIT_HEAD", "CANDIDATE_IDENTITY", "CANONICAL_TARGET_DIGEST"],
        ["TESTED or ACTIVE_SCOPED candidate", "regression/adversarial/replay PASS", "evidence refs", "rollback path"],
        "GIT_EVENT_LINEAGE", "revert/compensate as a new canonical Git event",
    ),

    # SCHED/frontier reads.
    "athena_frontier_hydrate": _descriptor(
        "athena_frontier_hydrate", "FRONTIER_READ_SELECT", "frontier_runtime", "READ_ONLY",
        "OBSERVE_FRONTIER", ["SCHED_SOURCE_REF", "SCHED_CONTRACT", "PROVIDER_CLAIM_STATE"],
        ["requested source ref resolvable", "pinned scheduler contract valid for authoritative reduction"],
        "EVENT_REDUCTION_WITH_COVERAGE", "none; read-only",
    ),
    "athena_frontier_freshness": _descriptor(
        "athena_frontier_freshness", "FRONTIER_READ_SELECT", "frontier_runtime", "READ_ONLY",
        "OBSERVE_FRONTIER", ["SCHED_SOURCE_REF", "FRONTIER_DIGEST", "PROMPT_STACK_DIGEST", "SCHED_CONTRACT"],
        ["expected address coordinates"], "DETERMINISTIC_COMPARISON", "none; read-only",
    ),
    "athena_frontier_select": _descriptor(
        "athena_frontier_select", "FRONTIER_READ_SELECT", "frontier_runtime", "READ_ONLY",
        "ROUTE_FRONTIER", ["SCHED_SOURCE_REF", "FRONTIER_DIGEST", "SCHED_CONTRACT", "PROVIDER_CLAIM_STATE"],
        ["fresh reducible frontier", "scheduler-READY lawful candidates"],
        "PARETO_ROUTING_RECEIPT", "none; routing is not execution authority",
    ),

    # Durable continuation writes and shared-fresh continuation reads.
    "athena_rehydration_start": _descriptor(
        "athena_rehydration_start", "REHYDRATION_LOOP", "rehydration_loop", "GIT_WRITE_BOUNDED",
        "CONTINUATION_CHECKPOINT_WRITE", ["PROMPT_GIT_HEAD", "PROMPT_STACK_DIGEST", "FRONTIER_IF_ENABLED", "SHARED_GIT_REMOTE"],
        ["exact expected Git head", "bounded loop budget", "lawful remote mode"],
        "HASH_CHAINED_GIT_STATE", "abort/hold through new state; never rewrite prior loop history",
    ),
    "athena_rehydration_advance": _descriptor(
        "athena_rehydration_advance", "REHYDRATION_LOOP", "rehydration_loop", "GIT_WRITE_BOUNDED",
        "CONTINUATION_CHECKPOINT_WRITE", ["SHARED_GIT_LOOP_HEAD", "LOOP_STATE_DIGEST", "PROMPT_DIGEST", "WORK_HEAD"],
        ["observed completion", "checkpoint ancestry", "exact state/prompt digests", "bounded continuation law"],
        "HASH_CHAINED_RECEIPT", "new corrective receipt/checkpoint; prior history immutable",
    ),
    "athena_rehydration_resume": _descriptor(
        "athena_rehydration_resume", "REHYDRATION_LOOP", "rehydration_loop", "READ_ONLY_SHARED_SYNC",
        "OBSERVE_CONTINUATION", ["SHARED_GIT_LOOP_HEAD"],
        ["loop id", "shared-current verification unless explicitly local mode"],
        "HASH_CHAINED_GIT_STATE", "none; read/sync only",
    ),
    "athena_rehydration_verify": _descriptor(
        "athena_rehydration_verify", "VERIFY_REPLAY_INDEX", "rehydration_loop", "READ_ONLY_SHARED_SYNC",
        "VERIFY_CONTINUATION", ["SHARED_GIT_LOOP_HEAD"],
        ["loop id", "shared-current verification unless explicitly local mode"],
        "FULL_CHAIN_REPLAY", "none; verification cannot repair truth",
    ),
    "athena_rehydration_index": _descriptor(
        "athena_rehydration_index", "VERIFY_REPLAY_INDEX", "rehydration_loop", "READ_ONLY_SHARED_SYNC",
        "INDEX_CONTINUATION", ["SHARED_GIT_LOOP_HEAD"],
        ["shared-current verification unless explicitly local mode"],
        "CURRENT_TIP_INDEX", "none; read/sync only",
    ),

    # WHAT NEXT is separate from WHAT TO REHYDRATE.
    "athena_rehydration_successor_preview": _descriptor(
        "athena_rehydration_successor_preview", "SUCCESSOR", "rehydration_successor", "READ_ONLY_SHARED_SYNC",
        "ROUTE_SUCCESSOR", ["SHARED_GIT_LOOP_HEAD", "LOOP_STATE_DIGEST", "TERMINAL_GATE"],
        ["fresh loop state", "closure gate before terminal routing"],
        "REPLAYABLE_SUCCESSOR_BATON", "none; routing-only preview",
    ),
    "athena_rehydration_handoff_delta": _descriptor(
        "athena_rehydration_handoff_delta", "HANDOFF", "rehydration_handoff", "READ_ONLY_SHARED_SYNC",
        "DERIVE_HANDOFF", ["SHARED_GIT_LOOP_HEAD", "LOOP_CHAIN", "CURRENT_RECEIPT"],
        ["verified current transition"], "DETERMINISTIC_STATE_TRANSFER", "none; derived handoff is not progress",
    ),
    "athena_rehydration_handoff_resume": _descriptor(
        "athena_rehydration_handoff_resume", "HANDOFF", "rehydration_handoff", "READ_ONLY_SHARED_SYNC",
        "CONSUME_HANDOFF", ["SHARED_GIT_LOOP_HEAD", "HANDOFF_DIGEST", "OBSERVER_FRESHNESS"],
        ["fresh handoff identity", "sufficient dependency-cone coverage"],
        "DETERMINISTIC_STATE_TRANSFER", "fallback to fuller rehydration when coverage/freshness fails",
    ),

    # Composite read/reconstruction surface.
    "athena_agent_bootstrap": _descriptor(
        "athena_agent_bootstrap", "BOOTSTRAP_REFRESH", "agent_bootstrap", "READ_ONLY_SHARED_SYNC",
        "COMPOSE_COLD_START", ["PROMPT_GIT_HEAD", "SCHED_SOURCE_REF", "SCHED_CONTRACT", "ISSUE_API", "SIBLING_STATE", "CONTINUATION_STATE"],
        ["configured Git brain", "fresh source/provider witnesses for claimed coordinates"],
        "FACTORIZED_BOOT_ADDRESS", "none; boot packet is not execution authority",
    ),
    "athena_agent_refresh": _descriptor(
        "athena_agent_refresh", "BOOTSTRAP_REFRESH", "agent_bootstrap", "READ_ONLY_SHARED_SYNC",
        "REFRESH_DEPENDENCY_CONE", ["PRIOR_BOOT_ADDRESS", "CURRENT_SOURCE_WITNESSES"],
        ["session id or explicit prior address"],
        "FACTORIZED_ADDRESS_DIFF", "none; refresh changes observation, not authority",
    ),
}


def _is_negotiated(name: str) -> bool:
    return any(name.startswith(prefix) for prefix in NEGOTIATED_PREFIXES)


def _digest_descriptor(descriptor: Mapping[str, Any]) -> dict[str, Any]:
    # current_exposure and source_witness are observer/provenance coordinates, not
    # semantic capability identity. Their movement must not contaminate content.
    return {
        key: value
        for key, value in descriptor.items()
        if key not in {"current_exposure", "source_witness"}
    }


def derive_operational_basis(
    registered_names: Iterable[str],
    *,
    runtime_identity: str | None = None,
    descriptor_map: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Derive semantic capability state from the actually registered runtime.

    Descriptor existence never implies exposure. Conversely, any currently
    registered negotiated operation without a descriptor is surfaced explicitly
    and semantic auto-selection fails closed.
    """

    descriptors_source = CONTROL_CAPABILITY_DESCRIPTORS if descriptor_map is None else descriptor_map
    registered = sorted({str(name) for name in registered_names if str(name)})
    negotiated_registered = sorted(name for name in registered if _is_negotiated(name))

    exposed: list[dict[str, Any]] = []
    for name in negotiated_registered:
        raw = descriptors_source.get(name)
        if raw is None:
            continue
        descriptor = dict(raw)
        descriptor["current_exposure"] = True
        descriptor["source_witness"] = runtime_identity
        exposed.append(descriptor)

    unclassified = sorted(name for name in negotiated_registered if name not in descriptors_source)
    dormant = sorted(name for name in descriptors_source if name not in registered)

    digest_basis = {
        "artifact": ARTIFACT,
        "descriptors": sorted(
            (_digest_descriptor(descriptor) for descriptor in exposed),
            key=lambda descriptor: descriptor["operation"],
        ),
        "unclassified": unclassified,
    }
    basis_digest = _sha(digest_basis)

    classes: dict[str, list[str]] = {}
    for descriptor in exposed:
        classes.setdefault(descriptor["capability_class"], []).append(descriptor["operation"])
    classes = {key: sorted(value) for key, value in sorted(classes.items())}

    return {
        "artifact": ARTIFACT,
        "status": "PASS" if not unclassified else "HOLD_UNCLASSIFIED_CAPABILITY",
        "runtime_identity": runtime_identity,
        "basis_digest": basis_digest,
        "descriptors": sorted(exposed, key=lambda descriptor: descriptor["operation"]),
        "capability_classes": classes,
        "unclassified": unclassified,
        "dormant_descriptors": dormant,
        "registered_negotiated_count": len(negotiated_registered),
        "classified_count": len(exposed),
        "laws": [
            "OPERATIONAL_BASIS != HIGHER_AUTHORITY",
            "DESCRIPTOR != PERMISSION",
            "DESCRIPTOR_EXISTS != CURRENT_EXPOSURE",
            "FEATURE_BRANCH != CURRENT_RUNTIME_EXPOSURE",
            "REGISTERED_UNCLASSIFIED => HOLD_FOR_SEMANTIC_SELECTION",
            "BASIS_DIGEST != GIT_HEAD",
            "RUNTIME_WITNESS != GIT_COMMIT",
        ],
    }


CAPABILITY_BASIS_TOOLS = [
    {
        "name": "athena_capability_basis",
        "description": (
            "Return the machine-readable semantic capability basis derived from the actually registered "
            "current ATHENA control-plane operations. This is read-only observation; descriptors do not grant authority."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    }
]
CAPABILITY_BASIS_TOOL_NAMES = {tool["name"] for tool in CAPABILITY_BASIS_TOOLS}

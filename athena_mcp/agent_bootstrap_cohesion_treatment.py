from __future__ import annotations

from typing import Any, Mapping

from .cohesion_duplicate_guard import DUPLICATE_GUARD_VERSION, duplicate_guard

ARTIFACT = "ATHENA.AGENT.BOOT.COHESION.TREATMENT.V1"
_PROJECTABLE_HOLDS = {"DUPLICATE_WORK_HOLD", "AGENT_ALREADY_PRESENT_HOLD"}
_LAWS = [
    "BOOT_HOLD != TREATMENT_EXECUTION",
    "TREATMENT_PROJECTION != CLAIM_MUTATION",
    "TREATMENT_PROJECTION != ASSIGNMENT",
    "TREATMENT_PROJECTION != AUTO_JOIN",
    "TREATMENT_PROJECTION != HOLD_OVERRIDE",
    "MESSAGE_BOARD = SOLE_PRESENCE_CLAIM_MESSAGE_AUTHORITY",
    "COHESION_GUARD = READ_ONLY_STEERING",
    "JOIN_OPTION != JOIN_EXECUTED",
    "PARTITION_OPTION != PARTITION_COMMITTED",
    "REPLICA_OPTION != REPLICA_CLAIM",
    "MATA_UNAVAILABLE != INFERRED_FROM_PROSE",
]


class _BoardAdapter:
    def __init__(self, board):
        self._message_board = board

    def _board(self):
        return self._message_board


def _coordination_arg(self, kwargs: Mapping[str, Any], name: str, default=None):
    if name in kwargs and kwargs.get(name) is not None:
        return kwargs.get(name)
    override = getattr(self, "_agent_boot_message_board_override", None)
    if isinstance(override, Mapping) and override.get(name) is not None:
        return override.get(name)
    return default


def _projection_view(result: Mapping[str, Any]) -> dict:
    return {
        "artifact": ARTIFACT,
        "source_artifact": result.get("artifact"),
        "source_version": result.get("version") or DUPLICATE_GUARD_VERSION,
        "status": result.get("status"),
        "classification": result.get("classification"),
        "standing": result.get("standing"),
        "hard_hold": bool(result.get("hard_hold")),
        "conflicts": result.get("conflicts") or [],
        "self_relation": result.get("self_relation"),
        "partition": result.get("partition"),
        "treatments": result.get("treatments") or [],
        "decision_digest": result.get("decision_digest"),
        "mata": result.get("mata"),
        "shared_frontier_verified": bool(result.get("shared_frontier_verified")),
        "board_write_performed": bool(result.get("board_write_performed", False)),
        "assignment_authority": False,
        "claim_authority": False,
        "execution_authority": False,
        "hold_override": False,
        "laws": list(_LAWS),
    }


def _attach_projection(self, packet: dict, request: Mapping[str, Any]) -> dict:
    if not isinstance(packet, dict):
        return packet
    coordination = packet.get("coordination")
    if not isinstance(coordination, dict):
        return packet
    if coordination.get("pre_dispatch") != "HOLD":
        return packet
    if str(coordination.get("status") or "") not in _PROJECTABLE_HOLDS:
        return packet

    board = getattr(self, "_agent_boot_message_board_runtime_v1", None)
    if board is None:
        # A deterministic BOOT-MB hold should imply the Message Board runtime exists.
        # If not, fail closed by preserving the original hold without manufacturing
        # a treatment projection.
        coordination["treatment_projection_unavailable"] = {
            "status": "MESSAGE_BOARD_RUNTIME_UNAVAILABLE_HOLD",
            "execution_authority": False,
            "law": "MISSING_BOARD_RUNTIME != EMPTY_CONFLICT_SET",
        }
        return packet

    claim_mode = str(_coordination_arg(self, request, "coordination_claim_mode", "PRIMARY") or "PRIMARY").upper()
    replication_reason = _coordination_arg(self, request, "replication_reason")
    work_key = _coordination_arg(self, request, "work_key")
    targets = _coordination_arg(self, request, "targets", []) or []
    remote = str(request.get("remote") or "origin")

    result = duplicate_guard(
        _BoardAdapter(board),
        agent_id=str(packet.get("agent_id") or ""),
        task=str(packet.get("task") or ""),
        work_key=work_key,
        targets=targets,
        intended_mode=claim_mode,
        replication_reason=replication_reason,
        remote=remote,
        shared_remote_mode="REQUIRED",
    )
    projection = _projection_view(result)
    coordination["treatment_projection"] = projection
    coordination["treatment_projection_digest"] = projection.get("decision_digest")

    packet.setdefault("execution_surface", {})["cohesion_duplicate_treatment"] = {
        "source_version": projection.get("source_version"),
        "classification": projection.get("classification"),
        "decision_digest": projection.get("decision_digest"),
        "execution_authority": False,
        "standing": "READ_ONLY_TREATMENT_PROJECTION",
    }
    packet.setdefault("return_contract", {})["treatment_projection_advisory_only"] = True
    laws = packet.setdefault("laws", [])
    for law in _LAWS:
        if law not in laws:
            laws.append(law)
    # Crucial: never remove or downgrade the pre-existing BOOT-MB hold/status.
    return packet


def install_agent_bootstrap_cohesion_treatment(runtime_cls) -> None:
    """Attach C3-11 treatment options to deterministic BOOT-MB holds.

    Installed after the BOOT-MB mechanism and activation policy. The wrapper is
    read-only: it cannot clear the original hold and never executes a treatment.
    Refresh naturally re-enters this wrapper through `self.bootstrap`, so stable
    held sessions receive stable C3 decision digests without a second path.
    """

    if getattr(runtime_cls, "_athena_boot_cohesion_treatment_v1_registered", False):
        return

    inner_bootstrap = runtime_cls.bootstrap

    def bootstrap_with_treatment(self, *args, **kwargs):
        request = dict(kwargs)
        packet = inner_bootstrap(self, *args, **kwargs)
        return _attach_projection(self, packet, request)

    runtime_cls.bootstrap = bootstrap_with_treatment
    runtime_cls._athena_boot_cohesion_treatment_v1_registered = True

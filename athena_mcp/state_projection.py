from __future__ import annotations

"""OMEGA.2 extension over the complete V11 state projection."""

import hashlib
import json
from typing import Any, Dict, Mapping

from . import state_projection_core as _core

OMEGA_VERSION = "ATHENA.OMEGA.2"


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _safe(call, unknown_label: str) -> dict[str, Any]:
    try:
        return {"status": "KNOWN", "value": call()}
    except Exception as exc:
        return {
            "status": "UNKNOWN",
            "reason": unknown_label,
            "error": f"{type(exc).__name__}: {exc}",
        }


def project_omega(server) -> Dict[str, Any]:
    state = dict(_core.project_omega(server))
    state.pop("omega_id", None)
    state.pop("state_digest", None)
    state["version"] = OMEGA_VERSION
    system_upgrade = getattr(server, "system_upgrade", None)
    state["system_upgrade"] = _safe(
        lambda: {
            "version": system_upgrade.describe(),
            "recent": system_upgrade.recent(20),
            "release_recent": system_upgrade.release_recent(20),
            "benchmark": system_upgrade.benchmark(),
        },
        "system upgrade control plane unavailable",
    )
    state["pending_mutations"] = _safe(
        lambda: server.core.pending_mutations(OMEGA_VERSION),
        "pending mutation query unavailable",
    )
    state["boundary"] = (
        "OMEGA covers accessible V1-V11 runtime and ledger state only. "
        "UPGRUN/RELCERT presence is observable receipt state, not external execution, "
        "merge, deployment, semantic truth, or Y1 authority. Absent external sources "
        "and unseen world state remain explicit rather than inferred."
    )
    state_digest = _digest(state)
    state["state_digest"] = state_digest
    state["omega_id"] = "OMEGA." + state_digest[:24]
    return state


def omega_diff(before: Mapping[str, Any], after: Mapping[str, Any]) -> Dict[str, Any]:
    return _core.omega_diff(before, after)


__all__ = ["OMEGA_VERSION", "project_omega", "omega_diff"]

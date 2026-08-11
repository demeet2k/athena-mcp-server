from __future__ import annotations

from collections.abc import Mapping

from . import tse_cost_carrier as carrier
from .rehydration_loop import RehydrationLoopRuntime

HARDENING_VERSION = "TSE.COST.CARRIER.HARDENING.1"


def install_tse_cost_carrier_hardening() -> None:
    if getattr(RehydrationLoopRuntime, "_athena_tse_cost_carrier_hardening_v1_registered", False):
        return

    original_sidecars = carrier._sidecars
    original_render = RehydrationLoopRuntime._render_prompt

    def hardened_sidecars(runtime):
        rows = original_sidecars(runtime)
        out = []
        for row in rows:
            if row.get("status") == "INTEGRITY_HOLD":
                out.append(row)
                continue
            basis = row.get("basis")
            if not isinstance(basis, Mapping):
                out.append({
                    "artifact": carrier.COST_CARRIER_ARTIFACT,
                    "cycle_id": row.get("cycle_id"),
                    "status": "INTEGRITY_HOLD",
                    "cost_complete": False,
                    "integrity_error": "cost_carrier_basis_missing",
                })
                continue
            mismatches = sorted(key for key, value in basis.items() if row.get(key) != value)
            if mismatches:
                out.append({
                    "artifact": carrier.COST_CARRIER_ARTIFACT,
                    "cycle_id": basis.get("cycle_id") or row.get("cycle_id"),
                    "mission_id": basis.get("mission_id"),
                    "status": "INTEGRITY_HOLD",
                    "cost_complete": False,
                    "integrity_error": "cost_carrier_mirror_mismatch",
                    "mismatches": mismatches,
                })
                continue
            out.append(row)
        return out

    def render_without_storage_marker(self, state, context, previous_completion):
        stops = list(state.get("stop_conditions") or [])
        if not any(isinstance(value, str) and value.startswith(carrier.REENTRY_COST_MARKER) for value in stops):
            return original_render(self, state, context, previous_completion)
        display_state = dict(state)
        display_state["stop_conditions"] = [
            value
            for value in stops
            if not (isinstance(value, str) and value.startswith(carrier.REENTRY_COST_MARKER))
        ]
        # Preserve the persisted state's already-computed digest coordinate. This
        # copy changes presentation only; it does not change the persisted state.
        return original_render(self, display_state, context, previous_completion)

    carrier._sidecars = hardened_sidecars
    RehydrationLoopRuntime._render_prompt = render_without_storage_marker
    RehydrationLoopRuntime._athena_tse_cost_carrier_hardening_v1_registered = True

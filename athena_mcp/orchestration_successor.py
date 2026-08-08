from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional


def _id(row: Optional[Mapping[str, Any]]):
    return None if not row else row.get("id")


def successor_packet(
    next_row: Optional[Mapping[str, Any]],
    successor_frontier: Iterable[Mapping[str, Any]],
    residual_frontier: Iterable[Mapping[str, Any]],
    measurement_plan: Iterable[Mapping[str, Any]],
    calibration_plan: Iterable[Mapping[str, Any]],
    dependency_cycles: Iterable[Any],
    return_coordinate: Any = None,
) -> Dict[str, Any]:
    successors = list(successor_frontier)
    residuals = list(residual_frontier)
    measurements = list(measurement_plan)
    calibrations = list(calibration_plan)
    cycles = list(dependency_cycles)

    primary = _id(next_row)
    alternates = [str(row.get("id")) for row in successors if row.get("id") != primary][:3]
    counter_route = None
    if measurements:
        counter_route = {"type": "measure", "target": measurements[0]}
    elif calibrations:
        counter_route = {"type": "calibrate", "target": calibrations[0]}
    elif cycles:
        counter_route = {"type": "resolve_dependency_cycle", "target": cycles[0]}
    elif residuals:
        counter_route = {"type": "attack_residual", "target": residuals[0].get("id")}

    unresolved_pressure = bool(primary or successors or residuals or measurements or calibrations or cycles)
    if primary:
        status = "CONTINUE_EXECUTE"
    elif measurements:
        status = "CONTINUE_MEASURE"
    elif calibrations:
        status = "CONTINUE_CALIBRATE"
    elif cycles:
        status = "CONTINUE_REPAIR_GRAPH"
    elif residuals:
        status = "CONTINUE_RESIDUAL"
    else:
        status = "QUIESCENT"

    return {
        "status": status,
        "continue": unresolved_pressure,
        "primary": primary,
        "alternates": alternates,
        "counter_route": counter_route,
        "return_coordinate": return_coordinate,
        "law": "next is selected from unresolved developmental frontier; no textual-order fallback",
        "deadend_route": ["backtrack", "nearest_live_branch", "reseed_from_residual"],
    }


def continuation_gate(packet: Mapping[str, Any], requested_complete: bool = False) -> Dict[str, Any]:
    """Stop only when the requested object is complete and no actionable pressure remains."""
    continue_flag = bool(packet.get("continue"))
    stop = bool(requested_complete and not continue_flag)
    return {
        "requested_complete": bool(requested_complete),
        "actionable_pressure": continue_flag,
        "stop_allowed": stop,
        "status": "STOP" if stop else "CONTINUE",
    }

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .ledger_writer import capillary_memory_path, read_json, write_json


DEFAULT_MEMORY = {
    "version": "command-protocol.v1",
    "coefficients": {
        "rho": 0.85,
        "alpha": 0.35,
        "beta": 0.25,
        "gamma": 0.25,
        "delta": 0.15
    },
    "thresholds": {
        "capillary": 0.65,
        "vein": 0.82
    },
    "initial_strength": 0.25,
    "edges": {}
}


def load_memory() -> dict[str, Any]:
    memory = read_json(capillary_memory_path(), DEFAULT_MEMORY)
    memory.setdefault("edges", {})
    return memory


def save_memory(memory: dict[str, Any]) -> None:
    write_json(capillary_memory_path(), memory)


def classify_edge(strength: float, thresholds: dict[str, float]) -> str:
    if strength >= thresholds["vein"]:
        return "vein"
    if strength >= thresholds["capillary"]:
        return "capillary"
    return "ephemeral"


def reinforce_edge(
    *,
    src: str,
    dst: str,
    usefulness: float,
    frequency_boost: float,
    latency_penalty: float,
    noise_penalty: float,
) -> dict[str, Any]:
    memory = load_memory()
    coeffs = memory["coefficients"]
    thresholds = memory["thresholds"]
    key = f"{src}>{dst}"
    edge = memory["edges"].get(
        key,
        {
            "Src": src,
            "Dst": dst,
            "Strength": memory["initial_strength"],
            "Usefulness": 0.0,
            "Frequency": 0.0,
            "LatencyPenalty": 0.0,
            "NoisePenalty": 0.0,
            "LastReinforcedAt": None
        },
    )
    next_strength = (
        coeffs["rho"] * edge["Strength"]
        + coeffs["alpha"] * usefulness
        + coeffs["beta"] * frequency_boost
        - coeffs["gamma"] * latency_penalty
        - coeffs["delta"] * noise_penalty
    )
    next_strength = max(0.0, min(1.0, round(next_strength, 6)))
    edge.update(
        {
            "Strength": next_strength,
            "Usefulness": round(usefulness, 6),
            "Frequency": round(edge["Frequency"] + frequency_boost, 6),
            "LatencyPenalty": round(latency_penalty, 6),
            "NoisePenalty": round(noise_penalty, 6),
            "LastReinforcedAt": datetime.now(tz=UTC).isoformat(),
            "StateClass": classify_edge(next_strength, thresholds),
        }
    )
    memory["edges"][key] = edge
    save_memory(memory)
    return edge

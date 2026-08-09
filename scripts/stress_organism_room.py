#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random

from athena_mcp.organism_room import FAMILIES, RESOURCE_DIMENSIONS, allocate_population, validate_resource_admission


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def resources(scale: int, sinks=None) -> dict:
    return {**{name: scale for name in RESOURCE_DIMENSIONS}, "shared_sinks": list(sinks or [])}


def run(scenarios: int, seed: int) -> dict:
    rng = random.Random(seed)
    trace = []
    for index in range(scenarios):
        population = rng.randrange(0, 257)
        pressure = {name: rng.random() * 4 if rng.random() > 0.18 else 0.0 for name in FAMILIES}
        allocation = allocate_population([f"agent-{i:03}" for i in range(population)], pressure)
        assert allocation["population"] == population
        assert sum(allocation["counts"].values()) == population
        assert sum(allocation["wave_counts"].values()) == population
        if population >= 3:
            assert all(value >= 1 for value in allocation["wave_counts"].values())
        if population == 1:
            assert allocation["counts"]["GIT"] == 1

        budget, reserve = resources(1000), resources(100)
        request = resources(rng.randrange(0, 901))
        standing = "ADMITTED"
        try:
            validate_resource_admission(request, budget, reserve, [])
        except ValueError as exc:
            standing = str(exc)
        if request["tokens"] + reserve["tokens"] <= budget["tokens"]:
            assert standing == "ADMITTED"
        else:
            assert standing.startswith("RESOURCE_CAPACITY_HOLD")
        trace.append({"i": index, "n": population, "waves": allocation["wave_counts"], "resources": standing})

    # Fixed adversarial sentinels: unknown cost and shared sink collision.
    missing = resources(1)
    del missing["api_calls"]
    try:
        validate_resource_admission(missing, resources(100), resources(1), [])
        raise AssertionError("missing resource dimension admitted")
    except ValueError as exc:
        assert "UNKNOWN_HOLD" in str(exc)
    active = {"status": "ACTIVE", **validate_resource_admission(resources(1, ["github:main"]), resources(100), resources(1), [])}
    try:
        validate_resource_admission(resources(1, ["github:main"]), resources(100), resources(1), [active])
        raise AssertionError("shared sink collision admitted")
    except ValueError as exc:
        assert str(exc).startswith("SHARED_SINK_HOLD")

    trace_digest = hashlib.sha256(canonical(trace)).hexdigest()
    receipt = {"artifact": "ATHENA.ORGANISM.ROOM.STRESS.RECEIPT.V1", "scenarios": scenarios, "seed": seed, "trace_sha256": trace_digest, "standing": "STRUCTURAL_STRESS_PASS_NOT_FIELD_EFFECT"}
    receipt["receipt_sha256"] = hashlib.sha256(canonical(receipt)).hexdigest()
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=144)
    args = parser.parse_args()
    if args.scenarios < 1 or args.scenarios > 1000000:
        raise SystemExit("scenarios must be 1..1000000")
    print(json.dumps(run(args.scenarios, args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter

from athena_mcp.swarm_room import HORIZONS, compile_pulse, target_horizon_counts


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run_tournament(scenarios: int = 20000, seed: int = 144) -> dict:
    rng = random.Random(seed)
    coverage = Counter()
    accumulator = hashlib.sha256()
    for index in range(scenarios):
        population = rng.randrange(0, 33)
        ready = {name for name in HORIZONS if rng.randrange(0, 2)}
        weights = {name: rng.randrange(1, 1001) for name in HORIZONS}
        counts = target_horizon_counts(population, ready, weights)
        assert set(counts) == set(HORIZONS)
        assert all(isinstance(value, int) and value >= 0 for value in counts.values())
        assert sum(counts.values()) == (population if ready else 0)
        assert all(counts[name] == 0 for name in set(HORIZONS) - ready)
        if ready and population >= len(ready):
            assert all(counts[name] >= 1 for name in ready)
            coverage["protected_horizon_floor"] += 1
        if population < len(ready):
            assert sum(value > 0 for value in counts.values()) <= population
            coverage["no_fake_concurrency"] += 1
        snapshot = {
            "status": "OK",
            "git_head": f"fixture-{index}",
            "active": [{"agent_id": f"agent-{slot}", "details": None} for slot in range(population)],
        }
        pulse = compile_pulse(snapshot, [])
        job_bp = sum(row["basis_points"] for row in pulse["actual_job_population"].values())
        horizon_bp = sum(row["basis_points"] for row in pulse["actual_horizon_population"].values())
        assert job_bp == (10000 if population else 0)
        assert horizon_bp == (10000 if population else 0)
        assert pulse["observed_active_workers"] == population
        assert pulse["ready_quest_count"] == 0
        assert pulse["scheduler_authority"] is False
        assert pulse["execution_authority"] is False
        accumulator.update(canonical({"i": index, "p": population, "r": sorted(ready), "w": weights, "c": counts}).encode("utf-8"))
        coverage["scenarios"] += 1
    receipt = {
        "artifact": "ATHENA.SWARM.ROOM.STRUCTURAL.TOURNAMENT.1",
        "status": "PASS_STRUCTURAL_HOLD",
        "scenario_count": scenarios,
        "seed": seed,
        "coverage": dict(sorted(coverage.items())),
        "trace_digest": "sha256:" + accumulator.hexdigest(),
        "mutation_performed": False,
        "behavioral_gain": "UNKNOWN",
        "production_authority": False,
        "claim_ceiling": "DETERMINISTIC_STRUCTURAL_STRESS_NOT_OBSERVED_MULTI_AGENT_OUTCOME",
    }
    receipt["receipt_digest"] = "sha256:" + hashlib.sha256(canonical(receipt).encode("utf-8")).hexdigest()
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=144)
    args = parser.parse_args()
    if args.scenarios < 1 or args.scenarios > 1000000:
        raise SystemExit("--scenarios must be between 1 and 1000000")
    print(json.dumps(run_tournament(args.scenarios, args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

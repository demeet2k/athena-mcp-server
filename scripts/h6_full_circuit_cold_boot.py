from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.store import Store

ARTIFACT = "ATHENA.H6.FULL.CIRCUIT.COLD.BOOT.V1"
RUNTIME_PARENT = "429a480a80eeefb9e2bff1ea3015adf571d76b0e"
INTEGRATED_PARENT = "7e09c83a6e93ba0a604c19b8c5a195293a7112c8"
SEMANTIC_HEAD = "f32eb817d48de73a0c591b0f7fb3561e4f08e7da"


def semantic(name: str) -> dict:
    return {
        "kind": "ARTIFACT", "domain": "H6_FULL_COLD", "verb": "RECONSTRUCT",
        "object_name": name, "method": "FULL_CIRCUIT_DURABLE_REOPEN",
        "input_contract": {"durable_state": "sqlite"},
        "output_contract": {"integrated_h6": "receipt"},
    }


def counts(store: Store) -> dict:
    return {
        "objects": store.one("SELECT COUNT(*) n FROM objects")["n"],
        "versions": store.one("SELECT COUNT(*) n FROM versions")["n"],
        "events": store.one("SELECT COUNT(*) n FROM events")["n"],
        "edges": store.one("SELECT COUNT(*) n FROM edges")["n"],
        "coordinates": store.one("SELECT COUNT(*) n FROM coordinates")["n"],
        "transforms": store.one("SELECT COUNT(*) n FROM transforms")["n"],
        "transform_programs": store.one("SELECT COUNT(*) n FROM transform_programs")["n"],
    }


def child(db_path: str, contract_path: str, output_path: str) -> int:
    contract = json.loads(Path(contract_path).read_text(encoding="utf-8"))
    store = Store(db_path)
    try:
        core = AthenaCore(store)
        bootstrap(core)
        crystal = CrystalRuntime(core)
        h6 = H6RootRuntime(core, crystal)
        before = counts(store)
        receipt = h6.compile_integrated(
            compile_input=contract["compile_input"],
            route_requests=contract["route_requests"],
            bridge_requests=contract["bridge_requests"],
            evidence_requests=contract["evidence_requests"],
        )
        route = receipt["route_proposals"][0]
        navrun = h6.navrun_observe(
            route,
            actual_cost={"hops": 1, "tool_calls": 0},
            observed_gain={"reachability": 1.0, "closure_gain": "OBSERVED_FIXTURE"},
            outcome="OBSERVED_ROUTE",
            final_frontier={"target": contract["target_oid"]},
        )
        after = counts(store)
        out = {
            "artifact": ARTIFACT,
            "mode": "INDEPENDENT_CHILD_REOPEN",
            "h6_root_digest": receipt["h6_root_digest"],
            "query_id": receipt["query_bundle"]["query_id"],
            "admission": receipt["admission"],
            "holds": receipt["holds"],
            "identity_decisions": [x["decision"] for x in receipt["identity_decisions"]],
            "projection_statuses": [x["status"] for x in receipt["projection_decisions"]],
            "route_id": route["route_id"],
            "route_gate": route["hard_gate_status"],
            "required_bridges": route["required_bridges"],
            "required_evidence": route["required_evidence"],
            "bridge_id": receipt["bridge_decisions"][0]["bridge_id"],
            "bridge_decision": receipt["bridge_decisions"][0]["decision"],
            "evidence_status": receipt["evidence_decisions"][0]["status"],
            "claim_id": receipt["evidence_decisions"][0]["claim_id"],
            "navrun_id": navrun["navrun_id"],
            "navrun_status": navrun["status"],
            "navrun_persisted": navrun["persisted"],
            "counts_before": before,
            "counts_after": after,
            "read_only": before == after,
            "execution_authority": receipt["execution_authority"],
            "promotion_authority": receipt["promotion_authority"],
        }
        Path(output_path).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0 if out["read_only"] else 2
    finally:
        store.close()


def parent(receipt_path: str) -> int:
    with tempfile.TemporaryDirectory(prefix="athena-h6-full-cold-") as tmp:
        root = Path(tmp)
        db = root / "athena.db"
        store = Store(db)
        try:
            core = AthenaCore(store)
            bootstrap(core)
            crystal = CrystalRuntime(core)
            a = crystal.crystallize_output(
                semantic("FULL_COLD_A"), "full cold A", "memory://h6/full-cold/a",
                "H6.FULL.COLD", "a", 1)
            b = crystal.crystallize_output(
                semantic("FULL_COLD_B"), "full cold B", "memory://h6/full-cold/b",
                "H6.FULL.COLD", "b", 1)
            aoid, avid = a["manifest"]["identity"]["OID"], a["manifest"]["identity"]["VID"]
            boid, bvid = b["manifest"]["identity"]["OID"], b["manifest"]["identity"]["VID"]
            core.add_edge(aoid, "DEPENDS_ON", boid, actor="H6.FULL.COLD")
            forward = crystal.register_transform(
                "KC144", "JSPACE", status="TESTED", mode="ISOMORPHISM",
                program={"op": "identity"}, metric={"type": "EXACT"})
            reverse = crystal.register_transform(
                "JSPACE", "KC144", status="TESTED", mode="ISOMORPHISM",
                program={"op": "identity"}, metric={"type": "EXACT"})
            baseline = counts(store)
        finally:
            store.close()

        claim_id = "CLAIM.H6.FULL.COLD"
        contract = {
            "target_oid": boid,
            "compile_input": {
                "request": "Cold reconstruct the coupled H6 circuit",
                "goal": "prove H01-H06 durable reconstruction",
                "identity_targets": [aoid, boid],
                "semantic_vids": [avid, bvid],
                "git_head": RUNTIME_PARENT,
                "topology_version": "KC144.EPOCH-B-EIGHT-BLOCK",
                "prompt_digest": "ATHENA.PROMPT.RUNTIME.V1@" + SEMANTIC_HEAD,
                "evidence_floor": "E2_INTEGRATED_MECHANISM",
                "authority_envelope": {"mode": "READ_ONLY"},
                "completion_predicate": {"type": "EXPLICIT", "value": "FULL_H6_COLD_RECEIPT"},
                "stop_predicate": {"type": "NO_POSITIVE_LAWFUL_FRONTIER"},
                "return_target": "H01_PRIME",
            },
            "route_requests": [{
                "source_oid": aoid, "target": boid, "relations": ["DEPENDS_ON"],
                "required_transforms": [forward["transform_id"]],
                "required_claims": [claim_id],
            }],
            "bridge_requests": [{
                "transform_id": forward["transform_id"],
                "contract": {
                    "preserved_invariants": ["IDENTITY", "VALUE"],
                    "lost_invariants": [],
                    "validity_corridor": {"type": "DURABLE_FIXTURE_DOMAIN"},
                    "evidence_refs": ["EVID.H6.FULL.BRIDGE"],
                    "required_authority": ["READ_ONLY_TRANSFORM"],
                    "reverse_transform_id": reverse["transform_id"],
                    "counterexamples": ["OUTSIDE_DURABLE_FIXTURE_DOMAIN"],
                },
            }],
            "evidence_requests": [{
                "claim": {"claim_id": claim_id, "evidence_floor": {"minimum_independent": 2}},
                "evidence_items": [
                    {"evidence_id": "E.H6.FULL.1", "source_id": "S.H6.FULL.1", "source_revision": "R1", "independence_group": "G.H6.FULL.1", "support_direction": "SUPPORT"},
                    {"evidence_id": "E.H6.FULL.2", "source_id": "S.H6.FULL.2", "source_revision": "R1", "independence_group": "G.H6.FULL.2", "support_direction": "SUPPORT"},
                ],
            }],
        }
        contract_path = root / "contract.json"
        contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        children = []
        for index in (1, 2):
            out_path = root / f"child-{index}.json"
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--child", "--db", str(db),
                 "--contract", str(contract_path), "--output", str(out_path)],
                cwd=str(ROOT), text=True, capture_output=True)
            if proc.returncode != 0:
                print(proc.stdout)
                print(proc.stderr, file=sys.stderr)
                return proc.returncode
            children.append(json.loads(out_path.read_text(encoding="utf-8")))

        same_fields = [
            "h6_root_digest", "query_id", "route_id", "bridge_id", "claim_id", "navrun_id",
        ]
        deterministic = all(children[0][field] == children[1][field] for field in same_fields)
        stable_counts = all(c["counts_before"] == baseline and c["counts_after"] == baseline for c in children)
        fully_admitted = all(
            c["admission"] == "ADMITTED" and not c["holds"] and
            c["identity_decisions"] == ["RESOLVED_EXISTING", "RESOLVED_EXISTING"] and
            c["projection_statuses"] == ["ACTIVE", "ACTIVE"] and
            c["route_gate"] == "PASS" and c["bridge_decision"] == "ADMITTED" and
            c["evidence_status"] == "EVIDENCE_SUFFICIENT" and
            c["navrun_status"] == "OBSERVED" and not c["navrun_persisted"] and
            not c["execution_authority"] and not c["promotion_authority"]
            for c in children)
        ok = deterministic and stable_counts and fully_admitted
        receipt = {
            "artifact": ARTIFACT,
            "runtime_parent": RUNTIME_PARENT,
            "integrated_parent": INTEGRATED_PARENT,
            "semantic_head": SEMANTIC_HEAD,
            "baseline_counts": baseline,
            "children": children,
            "checks": {
                "deterministic_full_circuit_ids": deterministic,
                "durable_counts_unchanged": stable_counts,
                "all_six_stations_admitted": fully_admitted,
            },
            "status": "FULL_CIRCUIT_COLD_MATCH" if ok else "FULL_CIRCUIT_COLD_HOLD",
            "laws": [
                "FULL_CIRCUIT_COLD_MATCH != EXECUTION_AUTHORITY",
                "FULL_CIRCUIT_COLD_MATCH != PROMOTION_AUTHORITY",
                "NAVRUN_OBSERVATION != CLAIM_TRUTH",
                "H6_ROOT_CLOSED != WHOLE_KC144_CLOSED",
            ],
        }
        Path(receipt_path).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--child", action="store_true")
    p.add_argument("--db")
    p.add_argument("--contract")
    p.add_argument("--output")
    p.add_argument("--receipt", default="h6_full_circuit_cold_receipt.json")
    args = p.parse_args()
    if args.child:
        if not args.db or not args.contract or not args.output:
            p.error("--child requires --db --contract --output")
        return child(args.db, args.contract, args.output)
    return parent(args.receipt)


if __name__ == "__main__":
    raise SystemExit(main())

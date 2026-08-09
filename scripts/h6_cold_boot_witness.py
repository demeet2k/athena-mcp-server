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

ARTIFACT = "ATHENA.H6.COLD.BOOT.WITNESS.V1"
RUNTIME_PARENT = "429a480a80eeefb9e2bff1ea3015adf571d76b0e"
GREEN_PARENT = "80f47b21a8bc26ece6032f9d4b89e96d9c987e9e"
SEMANTIC_HEAD = "f32eb817d48de73a0c591b0f7fb3561e4f08e7da"


def _semantic(name: str) -> dict:
    return {
        "kind": "ARTIFACT",
        "domain": "H6_COLD_BOOT",
        "verb": "RECONSTRUCT",
        "object_name": name,
        "method": "DURABLE_SQLITE_REOPEN",
        "input_contract": {"durable_state": "sqlite"},
        "output_contract": {"h6_root": "receipt"},
    }


def _counts(store: Store) -> dict:
    return {
        "objects": store.one("SELECT COUNT(*) n FROM objects")["n"],
        "versions": store.one("SELECT COUNT(*) n FROM versions")["n"],
        "events": store.one("SELECT COUNT(*) n FROM events")["n"],
        "coordinates": store.one("SELECT COUNT(*) n FROM coordinates")["n"],
        "transforms": store.one("SELECT COUNT(*) n FROM transforms")["n"],
    }


def child(db_path: str, input_path: str, output_path: str) -> int:
    inputs = json.loads(Path(input_path).read_text(encoding="utf-8"))
    store = Store(db_path)
    try:
        core = AthenaCore(store)
        bootstrap(core)
        crystal = CrystalRuntime(core)
        h6 = H6RootRuntime(core, crystal)
        before = _counts(store)
        receipt = h6.compile_query(**inputs["compile"])
        after = _counts(store)
        out = {
            "artifact": ARTIFACT,
            "mode": "CHILD_REOPEN",
            "h6_root_digest": receipt["h6_root_digest"],
            "query_id": receipt["query_bundle"]["query_id"],
            "admission": receipt["admission"],
            "holds": receipt["holds"],
            "selected_oids": [d.get("selected_oid") for d in receipt["identity_decisions"]],
            "projection_statuses": [d.get("status") for d in receipt["projection_decisions"]],
            "current_semantic_vids": receipt["active_subcrystal_candidate"]["current_semantic_vids"],
            "counts_before": before,
            "counts_after": after,
            "read_only": before == after,
        }
        Path(output_path).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0 if out["read_only"] else 2
    finally:
        store.close()


def parent(receipt_path: str) -> int:
    with tempfile.TemporaryDirectory(prefix="athena-h6-cold-") as tmp:
        root = Path(tmp)
        db = root / "athena.db"
        store = Store(db)
        try:
            core = AthenaCore(store)
            bootstrap(core)
            crystal = CrystalRuntime(core)
            made = crystal.crystallize_output(
                _semantic("COLD_BOOT_TARGET"),
                "H6 durable cold boot target",
                "memory://h6/cold-boot/target",
                "H6.COLD.BOOT",
                "cold-boot",
                1,
            )
            oid = made["manifest"]["identity"]["OID"]
            vid = made["manifest"]["identity"]["VID"]
            baseline = _counts(store)
        finally:
            store.close()

        inputs = {
            "compile": {
                "request": "Reconstruct H6 from durable state in a clean process",
                "goal": "emit deterministic H6 root receipt",
                "identity_targets": [oid],
                "semantic_vids": [vid],
                "git_head": RUNTIME_PARENT,
                "topology_version": "KC144.EPOCH-B-EIGHT-BLOCK",
                "prompt_digest": "ATHENA.PROMPT.RUNTIME.V1@" + SEMANTIC_HEAD,
                "evidence_floor": "E1_STATICALLY_VALIDATED",
                "authority_envelope": {"mode": "READ_ONLY"},
                "completion_predicate": {"type": "EXPLICIT", "value": "H6_COLD_BOOT_RECEIPT_EMITTED"},
                "stop_predicate": {"type": "NO_POSITIVE_LAWFUL_FRONTIER"},
                "return_target": "H01_PRIME",
            }
        }
        input_path = root / "inputs.json"
        input_path.write_text(json.dumps(inputs, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        children = []
        for index in (1, 2):
            output = root / f"child-{index}.json"
            run = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--child", "--db", str(db),
                 "--input", str(input_path), "--output", str(output)],
                cwd=str(ROOT), text=True, capture_output=True,
            )
            if run.returncode != 0:
                print(run.stdout)
                print(run.stderr, file=sys.stderr)
                return run.returncode
            children.append(json.loads(output.read_text(encoding="utf-8")))

        same_digest = children[0]["h6_root_digest"] == children[1]["h6_root_digest"]
        same_query = children[0]["query_id"] == children[1]["query_id"]
        stable_counts = all(c["counts_before"] == baseline and c["counts_after"] == baseline for c in children)
        admitted = all(c["admission"] == "ADMITTED" and not c["holds"] for c in children)
        identity_match = all(c["selected_oids"] == [oid] for c in children)
        projection_match = all(c["projection_statuses"] == ["ACTIVE"] for c in children)
        current_vid_match = all(c["current_semantic_vids"].get(oid) == vid for c in children)

        ok = all([same_digest, same_query, stable_counts, admitted, identity_match, projection_match, current_vid_match])
        receipt = {
            "artifact": ARTIFACT,
            "runtime_parent": RUNTIME_PARENT,
            "green_parent": GREEN_PARENT,
            "semantic_head": SEMANTIC_HEAD,
            "durable_seed": {"oid": oid, "vid": vid, "baseline_counts": baseline},
            "children": children,
            "checks": {
                "same_h6_root_digest": same_digest,
                "same_query_id": same_query,
                "durable_counts_unchanged": stable_counts,
                "admitted_without_holds": admitted,
                "identity_reconstructed": identity_match,
                "projection_reconstructed": projection_match,
                "current_vid_reconstructed": current_vid_match,
            },
            "status": "COLD_BOOT_MATCH" if ok else "COLD_BOOT_HOLD",
            "laws": [
                "COLD_BOOT != SAME_PROCESS_REUSE",
                "REOPENED_DURABLE_STATE != HIDDEN_CHAT_MEMORY",
                "H6_COMPILE != EXECUTION_AUTHORITY",
                "MATCHED_DIGEST != WHOLE_CRYSTAL_COMPLETION",
            ],
        }
        Path(receipt_path).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--db")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--receipt", default="h6_cold_boot_receipt.json")
    args = parser.parse_args()
    if args.child:
        if not args.db or not args.input or not args.output:
            parser.error("--child requires --db --input --output")
        return child(args.db, args.input, args.output)
    return parent(args.receipt)


if __name__ == "__main__":
    raise SystemExit(main())

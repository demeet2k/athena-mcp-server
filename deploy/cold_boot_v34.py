#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import tempfile
import textwrap
from typing import Any

EXPECTED_VERSION = "3.4.0"
EXPECTED_MANIFEST = "ATHENA.RUNTIME.UNIFIED.11"
EXPECTED_COLLECTIVE = "COLLECTIVE_CALIBRATED_V15"
EXPECTED_COORDINATE = "COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>"
AUTHORITY_FALSE = {
    "deployment_authorized": False,
    "release_publication_authorized": False,
    "production_secret_provisioned": False,
    "production_state_contacted": False,
    "traffic_activation_authorized": False,
    "treatment_or_resource_execution_authorized": False,
    "y1_mutation_authorized": False,
}


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def verify_sha256s(candidate_dir: pathlib.Path) -> dict[str, str]:
    sums = candidate_dir / "SHA256SUMS"
    if not sums.is_file():
        raise AssertionError("missing SHA256SUMS")
    observed: dict[str, str] = {}
    for line in sums.read_text().splitlines():
        if not line.strip():
            continue
        expected, name = line.split(maxsplit=1)
        name = name.lstrip("* ")
        path = candidate_dir / name
        if not path.is_file():
            raise AssertionError(f"missing checksummed file: {name}")
        actual = sha256_file(path)
        if actual != expected:
            raise AssertionError(f"checksum mismatch for {name}: {actual} != {expected}")
        observed[name] = actual
    return observed


def read_candidate_identity(candidate_dir: pathlib.Path, target_head: str) -> dict[str, Any]:
    att = json.loads((candidate_dir / "release-attestation.json").read_text())
    manifest = json.loads((candidate_dir / "release-manifest.json").read_text())
    receipt = json.loads((candidate_dir / "promotion-receipt.json").read_text())

    assert att["version"] == EXPECTED_VERSION
    assert att["release_commit"] == target_head
    assert att["manifest"] == EXPECTED_MANIFEST
    assert att["collective_frontier"] == EXPECTED_COLLECTIVE
    assert att["trusted_promotion"] is True
    assert att["publication_performed"] is False

    assert manifest["version"] == EXPECTED_VERSION
    assert manifest["runtime"]["manifest"] == EXPECTED_MANIFEST
    assert manifest["runtime"]["collective_frontier"] == EXPECTED_COLLECTIVE
    assert manifest["source_policy"]["master_push_validation_is_nonpublishing"] is True
    assert manifest["source_policy"]["publication_requires_manual_workflow_dispatch"] is True

    status = receipt.get("status") or receipt.get("qualification", {}).get("status")
    if status is not None:
        assert status == "QUALIFIED", status

    wheel = candidate_dir / f"athena_canonical_mcp-{EXPECTED_VERSION}-py3-none-any.whl"
    assert wheel.is_file(), wheel

    return {
        "release_attestation": att,
        "release_manifest": manifest,
        "promotion_receipt_status": status,
        "wheel": wheel.name,
        "wheel_sha256": sha256_file(wheel),
    }


def _probe_program() -> str:
    return textwrap.dedent(
        r'''
        import hashlib
        import importlib.metadata as md
        import json
        import pathlib
        import sys

        from athena_mcp.server import Server, SERVER_INFO
        from athena_mcp import unified_manifest

        db, actor, target_head, output_path = sys.argv[1:5]
        server = Server(db)
        manifest = unified_manifest.build_unified_manifest(server)
        assert md.version("athena-canonical-mcp") == "3.4.0"
        assert SERVER_INFO["version"] == "3.4.0"
        assert manifest["artifact"] == "ATHENA.RUNTIME.UNIFIED.11"
        assert "COLLECTIVE_CALIBRATED_V15" in manifest.get("layers", [])
        organ = manifest.get("organs", {}).get("collective_v15")
        assert organ and organ.get("coordinate") == "COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>"
        assert "V1-V15" in str(manifest.get("cycle"))
        assert "COLLECTIVE_CALIBRATED_V15" in str(manifest.get("navigation"))

        manifest_semantic = {
            "artifact": manifest.get("artifact"),
            "artifact_compat": manifest.get("artifact_compat"),
            "layers": manifest.get("layers"),
            "cycle": manifest.get("cycle"),
            "navigation": manifest.get("navigation"),
            "collective_v15": organ,
        }
        manifest_digest = hashlib.sha256(
            json.dumps(manifest_semantic, sort_keys=True, separators=(",", ":"), default=str).encode()
        ).hexdigest()

        reg = server.core.register(
            kind="artifact",
            domain="cold_boot",
            verb="verify",
            object_name="v34_v15_probe",
            method="wheel_replay",
            input_contract={"runtime_head": target_head},
            output_contract={"status": "semantic_replay"},
            constraints={"authority": "none"},
            payload={"probe": "V34_V15_COLD_BOOT", "runtime_head": target_head},
            actor=actor,
            status="CANDIDATE",
        )
        obj = reg["object"]
        head1 = server.store.head(f"object:{obj['oid']}")
        delta = server.core.commit_delta(
            obj["oid"], head1["vid"], {"phase": "restart-probe", "value": 1},
            actor=actor, status="CANDIDATE"
        )
        head2 = server.store.head(f"object:{obj['oid']}")
        semantic_before = {
            "oid": obj["oid"], "cid": obj["cid"], "canonical_name": obj["canonical_name"],
            "vid": head2["vid"], "head_digest": head2["digest"],
        }
        physical_before = {
            "register_event": head1["eid"],
            "delta_event": delta["event"],
            "object_head_eid": head2["eid"],
        }
        server.store.close()

        reopened = Server(db)
        row = reopened.store.one("SELECT * FROM objects WHERE oid=?", (obj["oid"],))
        head3 = reopened.store.head(f"object:{obj['oid']}")
        version = reopened.store.one("SELECT * FROM versions WHERE vid=?", (head3["vid"],))
        hydrate = reopened.core.hydrate()
        semantic_after = {
            "oid": row["oid"], "cid": row["cid"], "canonical_name": row["canonical_name"],
            "vid": head3["vid"], "head_digest": head3["digest"],
        }
        receipt = {
            "actor": actor,
            "runtime_head": target_head,
            "package_version": md.version("athena-canonical-mcp"),
            "package_path": __import__("athena_mcp").__file__,
            "server_info": SERVER_INFO,
            "manifest_semantic_digest": manifest_digest,
            "manifest_semantic": manifest_semantic,
            "semantic_before_restart": semantic_before,
            "semantic_after_restart": semantic_after,
            "semantic_restart_match": semantic_before == semantic_after,
            "physical_events": physical_before,
            "global_head_after_restart": hydrate["global_head"],
            "object_count_after_restart": len(hydrate["objects"]),
            "version_payload_digest": version["payload_digest"],
        }
        pathlib.Path(output_path).write_text(json.dumps(receipt, sort_keys=True, indent=2))
        reopened.store.close()
        '''
    )


def make_venv(venv_dir: pathlib.Path, wheel: pathlib.Path) -> pathlib.Path:
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    py = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run(
        [str(py), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return py


def validate_cross_instance(a: dict[str, Any], b: dict[str, Any]) -> dict[str, bool]:
    result = {
        "manifest_semantic_match": a["manifest_semantic_digest"] == b["manifest_semantic_digest"],
        "semantic_state_match": a["semantic_after_restart"] == b["semantic_after_restart"],
        "restart_match_a": bool(a["semantic_restart_match"]),
        "restart_match_b": bool(b["semantic_restart_match"]),
        "physical_event_histories_differ": a["physical_events"] != b["physical_events"],
    }
    if not all(result.values()):
        raise AssertionError(f"cross-instance cold-boot failure: {result}")
    return result


def run_probe(candidate_dir: pathlib.Path, target_head: str, output_dir: pathlib.Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    checksums = verify_sha256s(candidate_dir)
    identity = read_candidate_identity(candidate_dir, target_head)
    wheel = candidate_dir / identity["wheel"]

    with tempfile.TemporaryDirectory(prefix="athena-v34-cold-") as td:
        root = pathlib.Path(td)
        instances = []
        db_hashes = []
        for label in ("a", "b"):
            venv_dir = root / f"venv-{label}"
            db = root / f"state-{label}.db"
            receipt_path = root / f"instance-{label}.json"
            py = make_venv(venv_dir, wheel)
            subprocess.run(
                [str(py), "-c", _probe_program(), str(db), f"cold-{label}", target_head, str(receipt_path)],
                check=True,
                cwd=str(root),
            )
            receipt = json.loads(receipt_path.read_text())
            instances.append(receipt)
            db_hashes.append(sha256_file(db))

        comparisons = validate_cross_instance(instances[0], instances[1])
        comparisons["physical_database_hashes_differ"] = db_hashes[0] != db_hashes[1]
        if not comparisons["physical_database_hashes_differ"]:
            raise AssertionError("expected independent SQLite physical histories to differ")

        witness: dict[str, Any] = {
            "schema": "ATHENA.V34.V15.COLD_BOOT.WITNESS.1",
            "comparison_kind": "TWO_CLEAN_WHEEL_INSTALLS_SEPARATE_STATE_RESTART",
            "target_head": target_head,
            "candidate_identity": identity,
            "candidate_checksums": checksums,
            "environment": {
                "launcher_python": sys.version,
                "platform": platform.platform(),
                "runner_name": os.getenv("RUNNER_NAME"),
                "github_run_id": os.getenv("GITHUB_RUN_ID"),
                "github_sha": os.getenv("GITHUB_SHA"),
            },
            "instances": instances,
            "physical_database_sha256": db_hashes,
            "comparisons": comparisons,
            "authority": AUTHORITY_FALSE,
            "scope_law": "COLD_BOOT_REPLAY_MATCH != RELEASE_PUBLICATION != DEPLOYMENT != Y1_AUTHORITY",
        }
        witness["witness_digest"] = "sha256:" + sha256_json(witness)
        assessment = {
            "schema": "ATHENA.V34.V15.COLD_BOOT.ASSESSMENT.1",
            "status": "PASS",
            "decision": "COLD_BOOT_PASS",
            "target_head": target_head,
            "witness_digest": witness["witness_digest"],
            "authority": AUTHORITY_FALSE,
            "claim_ceiling": "independent clean-wheel install + isolated semantic persistence/restart/replay for exact candidate bytes; no publication/deployment/world-truth authority",
        }

        witness_path = output_dir / "v34-v15-cold-boot-witness.json"
        assessment_path = output_dir / "v34-v15-cold-boot-assessment.json"
        witness_path.write_text(json.dumps(witness, sort_keys=True, indent=2))
        assessment_path.write_text(json.dumps(assessment, sort_keys=True, indent=2))
        sums_path = output_dir / "SHA256SUMS.cold-boot"
        lines = []
        for path in (witness_path, assessment_path):
            lines.append(f"{sha256_file(path)}  {path.name}")
        sums_path.write_text("\n".join(lines) + "\n")
        return {"witness": witness, "assessment": assessment}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Independent cold-boot witness for exact ATHENA V3.4/V15 candidate bytes")
    parser.add_argument("--candidate-dir", required=True, type=pathlib.Path)
    parser.add_argument("--target-head", required=True)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)
    result = run_probe(args.candidate_dir.resolve(), args.target_head, args.output_dir.resolve())
    print("V3.4/V15 COLD BOOT PASS", result["witness"]["witness_digest"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .atlas import CorpusAtlas
from .engine import SelfActualizeEngine
from . import swarm_board


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "runtime_waist_verification.json"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_runtime_waist"
DERIVATION_VERSION = "2026-03-12.q07.runtime-waist"
NEXT_SEED = "FRONT-INT-SKILL-COHESION"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_command(args: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": " ".join(args),
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "ok": completed.returncode == 0,
    }


def run_check(label: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {
            "label": label,
            "status": "OK",
            "details": fn(),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "label": label,
            "status": "FAIL",
            "details": str(exc),
        }


def verify_atlas_contract() -> dict[str, Any]:
    atlas = CorpusAtlas.load_default()
    ensure(atlas is not None, "default atlas is missing")
    query = "self actualize runtime engine atlas swarm board verification"
    results = atlas.search(
        query=query,
        limit=5,
        preferred_kinds={"code", "text", "document"},
        regime_name="default",
        route_lens="square_structure",
    )
    ensure(results, "atlas search returned no results")
    ensure(
        any(
            token in item.relative_path.lower()
            for item in results
            for token in ("runtime", "swarm", "atlas", "engine")
        ),
        "atlas search did not return a runtime-adjacent witness",
    )
    regime = atlas.infer_regime(query)
    return {
        "source_label": atlas.source_label,
        "record_count": len(atlas.records),
        "query": query,
        "regime": regime.name,
        "top_records": [
            {
                "record_id": item.record_id,
                "relative_path": item.relative_path,
                "kind": item.kind,
                "score": round(item.score, 3),
            }
            for item in results
        ],
    }


def verify_engine_packet() -> dict[str, Any]:
    objective = "create a repeatable verification harness around the main runtime waist"
    engine = SelfActualizeEngine()
    packet = engine.run(objective)
    ensure(len(packet.candidate_routes) >= 3, "engine produced fewer than three candidate routes")
    ensure(packet.witness.evidence_refs, "engine witness bundle is empty")
    ensure(packet.witness.replay_hash, "engine did not compute a replay hash")
    ensure(packet.tri_lock.identity_lock, "engine tri-lock identity gate is open")
    ensure(packet.tri_lock.admissibility_lock, "engine tri-lock admissibility gate is open")
    ensure(packet.tri_lock.replay_lock, "engine tri-lock replay gate is open")
    ensure(packet.collapse.selected_route_id is not None, "engine collapse did not select a route")
    ensure(packet.collapse.verdict.value != "FAIL", "engine collapse returned FAIL")
    return {
        "objective": objective,
        "verdict": packet.collapse.verdict.value,
        "selected_route_id": packet.collapse.selected_route_id,
        "route_count": len(packet.candidate_routes),
        "evidence_count": len(packet.witness.evidence_refs),
        "replay_hash_prefix": packet.witness.replay_hash[:16],
        "patch_emitted": packet.patch is not None,
        "top_improvement": (
            packet.improvement_opportunities[0].title
            if packet.improvement_opportunities
            else "none"
        ),
    }


def verify_swarm_board_pipeline() -> dict[str, Any]:
    snapshot = swarm_board.scan_workspace()
    previous_snapshot = swarm_board.read_json(swarm_board.STATE_ROOT / "last_snapshot.json", None)
    diff = swarm_board.compute_diff(previous_snapshot, snapshot)
    docs_gate = swarm_board.docs_gate_status()
    queue = swarm_board.parse_queue()
    legacy_claims = swarm_board.parse_legacy_claims()
    board_claims = swarm_board.load_board_claims()
    notes = swarm_board.load_notes()
    all_claims = swarm_board.build_claim_index(board_claims=board_claims, legacy_claims=legacy_claims)
    threads = swarm_board.build_threads(notes=notes, all_claims=all_claims, diff=diff, snapshot=snapshot)
    family_tensor = swarm_board.build_family_tensor(snapshot=snapshot, docs_gate=docs_gate)
    threads = swarm_board.annotate_threads(threads=threads, family_tensor=family_tensor, docs_gate=docs_gate)
    pods = swarm_board.build_pods(threads)
    neurons = swarm_board.build_neurons(pods=pods, family_tensor=family_tensor)
    waves = swarm_board.build_waves(pods=pods, docs_gate=docs_gate, diff=diff)
    active_run = swarm_board.build_active_run_manifest(
        threads=threads,
        queue=queue,
        docs_gate=docs_gate,
        diff=diff,
    )
    ensure(snapshot["file_count"] > 0, "workspace scan returned zero files")
    ensure(queue, "active queue parse returned no sections")
    ensure(threads, "swarm board built no threads")
    ensure(family_tensor, "family tensor is empty")
    ensure(active_run["chosen_front"] != "none", "active run did not choose a front")
    ensure(len(swarm_board.render_board_readme()) > 100, "board README render is unexpectedly short")
    ensure(len(swarm_board.render_active_run_doc(active_run)) > 100, "active run render is unexpectedly short")
    return {
        "docs_gate_status": docs_gate["status"],
        "file_count": snapshot["file_count"],
        "thread_count": len(threads),
        "pod_count": len(pods),
        "neuron_count": len(neurons),
        "wave_count": len(waves),
        "chosen_front": active_run["chosen_front"],
        "chosen_family": active_run["chosen_family"],
        "recent_change_count": len(diff.get("changes", [])),
    }


def verify_swarm_board_build_command() -> dict[str, Any]:
    result = run_command(
        [sys.executable, "-m", "self_actualize.runtime.swarm_board", "build"],
        cwd=WORKSPACE_ROOT,
    )
    ensure(result["ok"], result["stderr"] or "swarm board build command failed")
    return {
        "command": result["command"],
        "cwd": result["cwd"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "board_root": str(swarm_board.BOARD_ROOT),
    }


def verify_payload() -> dict[str, Any]:
    checks = [
        run_check("atlas_contract", verify_atlas_contract),
        run_check("engine_packet", verify_engine_packet),
        run_check("swarm_board_pipeline", verify_swarm_board_pipeline),
        run_check("swarm_board_build_command", verify_swarm_board_build_command),
    ]
    failed = [check for check in checks if check["status"] != "OK"]
    truth = "OK" if not failed else "FAIL"
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "docs_gate_status": swarm_board.docs_gate_status()["status"],
        "checks": checks,
        "failed_checks": [check["label"] for check in failed],
        "next_seed": NEXT_SEED,
        "lane_law": (
            "The runtime waist stays trusted only while atlas lookup, engine packet synthesis, "
            "and swarm-board compilation can all replay locally through one verifier."
        ),
    }


def main() -> int:
    payload = verify_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote runtime waist verification json: {OUTPUT_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

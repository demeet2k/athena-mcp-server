from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import swarm_board
from .derive_skill_cohesion_registry import LIVE_ROUTER_PATH


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "skill_cohesion_registry.json"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "skill_cohesion_verification.json"
LEDGER_PATH = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
    / "10_LEDGERS"
    / "06_SKILL_COHESION_AND_BLOAT_PRUNING_2026-03-12.md"
)
RECEIPT_PATH = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "receipts"
    / "2026-03-12_front_int_skill_cohesion_verification.md"
)
DERIVATION_VERSION = "2026-03-12.skill-cohesion.verify.v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_skill_cohesion"
NEXT_SEED_SUCCESS = "FRONT-INT-ATHENA-FLEET-BRIDGE"
NEXT_SEED_FAIL = "FRONT-INT-SKILL-COHESION"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def run_check(label: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {"label": label, "status": "OK", "details": fn()}
    except Exception as exc:  # noqa: BLE001
        return {"label": label, "status": "FAIL", "details": str(exc)}


def verify_live_router_exists() -> dict[str, Any]:
    payload = load_registry()
    records = payload["records"]
    matches = [record for record in records if record["classification"] == "live_authority" and record["path"].endswith("09_SKILLS/00_SKILL_ROUTER.md")]
    ensure(matches, "live router record is missing")
    return {"live_router_path": matches[0]["path"]}


def verify_authority_exclusivity() -> dict[str, Any]:
    payload = load_registry()
    records = payload["records"]
    live_records = [record for record in records if record["classification"] == "live_authority" and record["authority_scope"] == "whole_corpus_deep_root"]
    root_families = sorted({record["root_family"] for record in live_records})
    ensure(root_families == ["live_deep_root"], f"live authority families drifted: {root_families}")
    return {"live_authority_count": len(live_records), "root_families": root_families}


def verify_historical_redirects() -> dict[str, Any]:
    payload = load_registry()
    historical = [record for record in payload["records"] if record["classification"] == "historical_mirror"]
    missing = [record["path"] for record in historical if not (record["boundary_notice_present"] and record["redirect_present"])]
    ensure(not missing, f"historical mirrors missing notice or redirect: {missing}")
    return {"historical_count": len(historical)}


def verify_family_local_boundaries() -> dict[str, Any]:
    payload = load_registry()
    family_local = [record for record in payload["records"] if record["classification"] == "family_local"]
    missing = [record["path"] for record in family_local if not (record["boundary_notice_present"] and record["redirect_present"])]
    ensure(not missing, f"family-local skills missing boundary or redirect: {missing}")
    return {"family_local_count": len(family_local)}


def verify_pruning_skill_exists() -> dict[str, Any]:
    payload = load_registry()
    matches = [record for record in payload["records"] if record["path"].endswith("09_SKILLS/cohesion-pruning-governor/SKILL.md")]
    ensure(matches, "cohesion-pruning-governor is missing")
    return {"path": matches[0]["path"]}


def verify_docs_gate_honesty() -> dict[str, Any]:
    registry = load_registry()
    registry_status = registry["summary"]["docs_gate_status"]
    live_status = swarm_board.docs_gate_status()["status"]
    ensure(registry_status == live_status, f"registry gate status drifted: {registry_status} != {live_status}")
    if live_status == "BLOCKED":
        creds = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
        token = WORKSPACE_ROOT / "Trading Bot" / "token.json"
        ensure(not (creds.exists() and token.exists()), "docs gate says blocked but OAuth files exist")
    return {"docs_gate_status": live_status}


def verify_no_rogue_live_authorities() -> dict[str, Any]:
    payload = load_registry()
    rogue = [record for record in payload["records"] if record["classification"] == "prunable_bloat" and record["overclaims_live_authority"]]
    ensure(not rogue, f"rogue whole-corpus authorities found: {[record['path'] for record in rogue]}")
    return {"prunable_bloat_count": len([record for record in payload["records"] if record["classification"] == "prunable_bloat"])}


def render_ledger(registry: dict[str, Any], verification: dict[str, Any]) -> str:
    summary = registry["summary"]
    truth = verification["truth"]
    next_seed = NEXT_SEED_SUCCESS if truth == "OK" else NEXT_SEED_FAIL
    lines = [
        "# Skill Cohesion And Bloat Pruning",
        "",
        "Date: `2026-03-12`",
        f"Truth: `{truth}`",
        "Scope: `deep-root skill routing and related mirror skills`",
        f"Live Docs gate: `{summary['docs_gate_status']}`",
        "",
        "## Purpose",
        "",
        "This ledger records the verified skill-authority layer for the deep-root skill field.",
        "The goal is precedence pruning, not file deletion.",
        "",
        "## Classification Counts",
        "",
    ]
    for key, value in sorted(summary["counts_by_classification"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Live Authority Map",
            "",
        ]
    )
    for path in summary["live_authority_paths"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Historical Mirror Surfaces",
            "",
        ]
    )
    for path in summary["historical_paths"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Family-Local Boundary Surfaces",
            "",
        ]
    )
    for path in summary["family_local_paths"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Prunable Bloat",
            "",
        ]
    )
    if summary["prunable_bloat_paths"]:
        for path in summary["prunable_bloat_paths"]:
            lines.append(f"- `{path}`")
    else:
        lines.append("- `none detected`")
    lines.extend(
        [
            "",
            "## Verification",
            "",
            f"- verification_json: `{OUTPUT_JSON_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            f"- live_router: `{LIVE_ROUTER_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            f"- next_seed: `{next_seed}`",
        ]
    )
    return "\n".join(lines)


def render_receipt(registry: dict[str, Any], verification: dict[str, Any]) -> str:
    summary = registry["summary"]
    truth = verification["truth"]
    next_seed = NEXT_SEED_SUCCESS if truth == "OK" else NEXT_SEED_FAIL
    lines = [
        "# 2026-03-12 FRONT-INT-SKILL-COHESION Verification",
        "",
        "## Outcome",
        "",
        f"- truth: `{truth}`",
        f"- registry_path: `{REGISTRY_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
        f"- verification_path: `{OUTPUT_JSON_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
        f"- ledger_path: `{LEDGER_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
        "",
        "## Final Authority Map",
        "",
        "- live_authority:",
    ]
    for path in summary["live_authority_paths"]:
        lines.append(f"  - `{path}`")
    lines.extend(
        [
            "- historical_mirror:",
        ]
    )
    for path in summary["historical_paths"]:
        lines.append(f"  - `{path}`")
    lines.extend(
        [
            "- family_local:",
        ]
    )
    for path in summary["family_local_paths"]:
        lines.append(f"  - `{path}`")
    lines.extend(
        [
            "- prunable_bloat:",
        ]
    )
    if summary["prunable_bloat_paths"]:
        for path in summary["prunable_bloat_paths"]:
            lines.append(f"  - `{path}`")
    else:
        lines.append("  - `none`")
    lines.extend(
        [
            "",
            "## Next Seed",
            "",
            f"- `{next_seed}`",
        ]
    )
    return "\n".join(lines)


def build_payload() -> dict[str, Any]:
    checks = [
        run_check("live_router_exists", verify_live_router_exists),
        run_check("authority_exclusivity", verify_authority_exclusivity),
        run_check("historical_redirects", verify_historical_redirects),
        run_check("family_local_boundaries", verify_family_local_boundaries),
        run_check("pruning_skill_exists", verify_pruning_skill_exists),
        run_check("docs_gate_honesty", verify_docs_gate_honesty),
        run_check("no_rogue_live_authorities", verify_no_rogue_live_authorities),
    ]
    failed = [check for check in checks if check["status"] != "OK"]
    truth = "OK" if not failed else "FAIL"
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "checks": checks,
        "failed_checks": [check["label"] for check in failed],
        "next_seed": NEXT_SEED_SUCCESS if truth == "OK" else NEXT_SEED_FAIL,
    }


def main() -> int:
    registry = load_registry()
    payload = build_payload()
    write_json(OUTPUT_JSON_PATH, payload)
    write_text(LEDGER_PATH, render_ledger(registry, payload))
    write_text(RECEIPT_PATH, render_receipt(registry, payload))
    print(f"Wrote skill cohesion verification: {OUTPUT_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

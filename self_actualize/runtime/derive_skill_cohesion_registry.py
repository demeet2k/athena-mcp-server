from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import swarm_board


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"

LIVE_SKILLS_ROOT = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
    / "09_SKILLS"
)
HISTORICAL_MIRROR_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "DEEPER_INTEGRATED_NEURAL_NETWORK"
HISTORICAL_ATHENA_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "DEEPER_INTEGRATED_NEURAL_NET_ATHENA"
PRECURSOR_ROOT = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "13_DEEPER_NEURAL_NET"
    / "08_SKILL"
)
FAMILY_LOCAL_SKILLS = [
    WORKSPACE_ROOT
    / "NERUAL NETWORK"
    / "ATHENA Neural Network"
    / "INTEGRATED_NEURAL_CRYSTAL"
    / "07_SKILLS"
    / "integrated-neural-network-orchestrator"
    / "SKILL.md",
    WORKSPACE_ROOT / "Trading Bot" / "skills" / "manuscript-elemental-synthesis" / "SKILL.md",
]

LIVE_ROUTER_PATH = LIVE_SKILLS_ROOT / "00_SKILL_ROUTER.md"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "skill_cohesion_registry.json"
DERIVATION_VERSION = "2026-03-12.skill-cohesion.registry.v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_skill_cohesion_registry"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def replacement_for(path: Path, classification: str) -> str:
    name = path.parent.name if path.name == "SKILL.md" else path.stem
    replacements = {
        "deep-corpus-neural-integrator": "deeper-network-basis-router + pair-matrix-synthesizer",
        "deep-neural-metro-cartographer": "metro-resolution-expander",
        "appendix-crystal-integrator": "appendix-crystal-governor",
    }
    if classification == "live_authority":
        return rel(path if path == LIVE_ROUTER_PATH else LIVE_ROUTER_PATH)
    return replacements.get(name, rel(LIVE_ROUTER_PATH))


def redirect_present(text: str, replacement: str) -> bool:
    lowered = text.lower()
    if replacement == rel(LIVE_ROUTER_PATH):
        return (
            rel(LIVE_ROUTER_PATH).lower() in lowered
            or "use the live router instead" in lowered
            or "use the live `14_deeper" in lowered
            or "for current whole-corpus deep-network requests, use" in lowered
        )
    if " + " in replacement:
        return all(part.lower() in lowered for part in replacement.split(" + "))
    return replacement.lower() in lowered


def boundary_notice_present(text: str, classification: str) -> bool:
    if classification == "historical_mirror":
        return "historical mirror notice" in text.lower() or "historical precursor notice" in text.lower()
    if classification == "family_local":
        return "family-local boundary" in text.lower()
    return False


def truth_class(text: str, classification: str) -> str:
    lowered = text.lower()
    if "truth class: `historical`" in lowered:
        return "HISTORICAL"
    if classification == "live_authority":
        return "LIVE"
    if classification == "historical_mirror":
        return "HISTORICAL"
    if classification == "family_local":
        return "FAMILY_LOCAL"
    return "AMBIG"


def authority_scope(classification: str) -> str:
    if classification == "live_authority":
        return "whole_corpus_deep_root"
    if classification == "historical_mirror":
        return "historical_reference"
    if classification == "family_local":
        return "family_local"
    return "rogue_whole_corpus_candidate"


def deep_routing_candidate(path: Path, text: str) -> bool:
    lowered = text.lower()
    candidate_tokens = [
        "whole-corpus",
        "whole organism",
        "deep-root",
        "deeper integrated neural",
        "16 x 16",
        "metro map",
        "router",
    ]
    return sum(token in lowered for token in candidate_tokens) >= 2


def overclaims_live_authority(text: str, classification: str) -> bool:
    if classification != "prunable_bloat":
        return False
    lowered = text.lower()
    safe_tokens = [
        "historical mirror notice",
        "historical precursor notice",
        "family-local boundary",
        "not as the live whole-corpus authority",
        "not the authoritative whole-corpus deep-root router",
        "it is not the authoritative whole-corpus",
    ]
    return not any(token in lowered for token in safe_tokens)


def skill_id_for(path: Path) -> str:
    relative = rel(path).replace("/", "__").replace(".", "_").replace("-", "_")
    return relative.lower()


def record_for(path: Path, root_family: str, classification: str, docs_gate_status: str) -> dict[str, Any]:
    text = read_text(path)
    replacement = replacement_for(path, classification)
    return {
        "skill_id": skill_id_for(path),
        "path": rel(path),
        "root_family": root_family,
        "classification": classification,
        "authority_scope": authority_scope(classification),
        "truth_class": truth_class(text, classification),
        "canonical_replacement": replacement,
        "boundary_notice_present": boundary_notice_present(text, classification),
        "redirect_present": redirect_present(text, replacement),
        "docs_gate_status": docs_gate_status,
        "overclaims_live_authority": overclaims_live_authority(text, classification),
    }


def scan_fixed_roots(docs_gate_status: str) -> tuple[list[dict[str, Any]], set[Path]]:
    records: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()

    fixed: list[tuple[Path, str, str]] = [(LIVE_ROUTER_PATH, "live_deep_root", "live_authority")]
    fixed.extend((path, "live_deep_root", "live_authority") for path in sorted(LIVE_SKILLS_ROOT.glob("*/SKILL.md")))
    fixed.append((HISTORICAL_MIRROR_ROOT / "11_SKILL_ROUTER_AND_ALGORITHMIC_PIPELINE.md", "historical_mirror_deeper_integrated_neural_network", "historical_mirror"))
    fixed.append((HISTORICAL_MIRROR_ROOT / "SKILLS" / "00_SKILL_INDEX.md", "historical_mirror_deeper_integrated_neural_network", "historical_mirror"))
    fixed.extend(
        (path, "historical_mirror_deeper_integrated_neural_network", "historical_mirror")
        for path in sorted((HISTORICAL_MIRROR_ROOT / "SKILLS").glob("*/SKILL.md"))
    )
    fixed.append((HISTORICAL_ATHENA_ROOT / "SKILL.md", "historical_mirror_deeper_integrated_neural_net_athena", "historical_mirror"))
    fixed.append((PRECURSOR_ROOT / "SKILL.md", "historical_precursor_deeper_crystalization", "historical_mirror"))
    fixed.extend((path, f"family_local_{path.parts[-3].lower().replace(' ', '_')}", "family_local") for path in FAMILY_LOCAL_SKILLS)

    for path, root_family, classification in fixed:
        if not path.exists():
            continue
        resolved = path.resolve()
        seen_paths.add(resolved)
        records.append(record_for(path=path, root_family=root_family, classification=classification, docs_gate_status=docs_gate_status))
    return records, seen_paths


def scan_prunable_bloat(docs_gate_status: str, seen_paths: set[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(WORKSPACE_ROOT.rglob("SKILL.md")):
        resolved = path.resolve()
        if resolved in seen_paths:
            continue
        text = read_text(path)
        if not deep_routing_candidate(path, text):
            continue
        records.append(
            record_for(
                path=path,
                root_family="unexpected_skill_surface",
                classification="prunable_bloat",
                docs_gate_status=docs_gate_status,
            )
        )
    return records


def summary_for(records: list[dict[str, Any]], docs_gate_status: str) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record["classification"]] = counts.get(record["classification"], 0) + 1
    return {
        "docs_gate_status": docs_gate_status,
        "record_count": len(records),
        "counts_by_classification": counts,
        "live_authority_paths": [record["path"] for record in records if record["classification"] == "live_authority"],
        "historical_paths": [record["path"] for record in records if record["classification"] == "historical_mirror"],
        "family_local_paths": [record["path"] for record in records if record["classification"] == "family_local"],
        "prunable_bloat_paths": [record["path"] for record in records if record["classification"] == "prunable_bloat"],
    }


def build_payload() -> dict[str, Any]:
    docs_gate_status = swarm_board.docs_gate_status()["status"]
    fixed_records, seen_paths = scan_fixed_roots(docs_gate_status)
    rogue_records = scan_prunable_bloat(docs_gate_status, seen_paths)
    records = sorted(fixed_records + rogue_records, key=lambda item: item["path"])
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "live_router_path": rel(LIVE_ROUTER_PATH),
        "records": records,
        "summary": summary_for(records, docs_gate_status),
    }


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON_PATH, payload)
    print(f"Wrote skill cohesion registry: {OUTPUT_JSON_PATH}")
    print(f"Record count: {payload['summary']['record_count']}")
    print(f"Docs gate: {payload['summary']['docs_gate_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "future_skill_frontier.json"
REGISTRY_PATH = ROOT / "FUTURE_SKILL_REGISTRY.md"
ROOT_CELL_PATH = ROOT / "root_cells_256.json"
WAVE_PATH = ROOT / "WAVE_0_PARALLEL_MANIFEST.md"
HYPER_PATH = ROOT / "HYPERDIMENSIONAL_COORDINATES.md"
HYPER_JSON_PATH = ROOT / "higher_dimensional_mapping.json"
FAMILY_PATH = ROOT / "META_SWARM_FAMILY_FRONTIER.md"
FAMILY_JSON_PATH = ROOT / "family_meta_swarm.json"
SWARM_WAVE_PATH = ROOT / "SWARM_WAVE_0_MANIFEST.md"
SKILLS_DIR = ROOT / "skills"

GENERIC_TRIGGERS = {
    "intake": ["ingest this", "bring this into the system", "capture this source"],
    "routing": ["route this", "map the dependencies", "where does this belong"],
    "compilation": ["compile this", "turn this into an artifact", "materialize the output"],
    "verification": ["verify this", "audit this", "check whether this is ready"],
}

GENERIC_INPUTS = {
    "manuscript-corpus": ["manuscript source paths", "atlas records", "chapter or section context"],
    "formal-framework": ["framework source paths", "kernel references", "archive or live tree"],
    "runtime-system": ["runtime contracts", "route packets", "ledger or profile data"],
    "live-memory": ["query terms", "gateway state", "result or provenance surface"],
}

GENERIC_OUTPUTS = {
    "witness": ["witness-bearing artifact", "source linkage", "replay note"],
    "benchmark": ["evaluation artifact", "measured results", "follow-up recommendations"],
    "governance": ["decision ledger entry", "status receipt", "next obligation list"],
    "publication": ["promoted artifact", "summary surface", "publication-ready packet"],
}

GENERIC_PROCEDURE = {
    "intake": [
        "Identify the correct source surface and its current boundaries.",
        "Capture the highest-yield evidence without hiding extraction limits.",
        "Normalize the result into the target Athena schema.",
        "Emit the resulting artifact together with lineage and next gaps.",
    ],
    "routing": [
        "Parse the active objective and source surfaces.",
        "Compute the most lawful route or dependency ordering.",
        "Preserve any unresolved ambiguity instead of forcing collapse.",
        "Emit the route artifact and the next recommended move.",
    ],
    "compilation": [
        "Select the strongest witnessed inputs for the target artifact.",
        "Transform the inputs into the requested executable or publishable surface.",
        "Record assumptions and surviving residuals.",
        "Emit the compiled artifact with its lineage and replay recipe.",
    ],
    "verification": [
        "Inspect the current artifact or gateway state.",
        "Compare it against the required invariants and expected outputs.",
        "Record blockers, partial closure, or passing conditions explicitly.",
        "Emit a verification receipt and the next lawful action.",
    ],
}

GENERIC_VALIDATION = {
    "witness": [
        "artifact cites real source paths or live-memory provenance",
        "lineage is preserved without silent rewrite",
    ],
    "benchmark": [
        "results are measured against a named surface",
        "failures remain inspectable after the run",
    ],
    "governance": [
        "status and obligations are explicit",
        "downstream users can replay the decision basis",
    ],
    "publication": [
        "artifact preserves the original identity of the source material",
        "promoted output is clearly separated from the source of truth",
    ],
}

GENERIC_FAILURES = {
    "intake": [
        "If the source cannot be fully extracted, keep metadata and log the limit.",
        "If the source boundary is unclear, record the ambiguity before proceeding.",
    ],
    "routing": [
        "If multiple routes compete, keep the shortlist instead of forcing one path.",
        "If the route depends on missing evidence, surface the dependency as a blocker.",
    ],
    "compilation": [
        "If the inputs are under-specified, emit a partial artifact and open residuals.",
        "If the output drifts from the source intent, preserve both views and flag the gap.",
    ],
    "verification": [
        "If prerequisites are missing, emit a blocked receipt with exact missing pieces.",
        "If evidence is partial, classify the result as partial instead of complete.",
    ],
}


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def build_root_cells(manifest: dict) -> list[dict]:
    axes = manifest["axes"]
    cells: list[dict] = []
    closure_defaults = {
        "witness": "witness packet",
        "benchmark": "benchmark ledger",
        "governance": "decision ledger",
        "publication": "promoted artifact",
    }
    for si, substrate in enumerate(axes["substrate"]):
        for oi, operator in enumerate(axes["operator"]):
            for ci, scale in enumerate(axes["scale"]):
                for li, closure in enumerate(axes["closure"]):
                    address = f"{si}{oi}{ci}{li}"
                    cells.append(
                        {
                            "address": address,
                            "substrate": substrate,
                            "operator": operator,
                            "scale": scale,
                            "closure": closure,
                            "seed_slug": f"{substrate}-{operator}-{scale}-{closure}",
                            "suggested_deliverable": closure_defaults[closure],
                        }
                    )
    return cells


def write_root_cells(cells: list[dict]) -> None:
    ROOT_CELL_PATH.write_text(
        json.dumps(
            {
                "root_cell_count": len(cells),
                "recursion_rule": "Apply the same 256-cell grammar to residuals from any validated skill output.",
                "cells": cells,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_registry(manifest: dict) -> None:
    lines: list[str] = []
    basis = manifest["basis"]
    lines.append("# Future Skill Registry")
    lines.append("")
    lines.append(f"Generated: {manifest['generated_at']}")
    lines.append("")
    lines.append("## Basis")
    lines.append("")
    lines.append(f"- Atlas: `{basis['atlas_path']}`")
    lines.append(f"- Record count: `{basis['record_count']}`")
    lines.append(f"- Live Docs gate: `{basis['live_docs_gate']['status']}`")
    for missing in basis["live_docs_gate"]["missing"]:
        lines.append(f"- Missing: `{missing}`")
    lines.append("")
    if manifest.get("higher_dimensional_mapping"):
        lines.append("## Hyper Dimensions")
        lines.append("")
        dims = ", ".join(manifest["higher_dimensional_mapping"].get("ns_coord", []))
        lines.append(f"- `NSCoord = ({dims})`")
        lines.append(
            f"- Metallic scales: {', '.join(manifest.get('metallic_scales', {}).keys())}"
        )
        lines.append("")
    if manifest.get("family_meta_swarm"):
        lines.append("## Meta-Swarm")
        lines.append("")
        lines.append(f"- Family ganglia: `{len(manifest['family_meta_swarm'])}`")
        lines.append(f"- Lane order: `{', '.join(manifest.get('lane_order', []))}`")
        lines.append("")
    lines.append("## Wave 0 Frontier")
    lines.append("")
    lines.append("| Address | Skill | Priority | Lane | Depends On |")
    lines.append("| --- | --- | --- | --- | --- |")
    for skill in manifest["frontier_skills"]:
        deps = ", ".join(skill["depends_on"]) if skill["depends_on"] else "-"
        lines.append(
            f"| `{skill['address']}` | `{skill['slug']}` | `{skill['priority']}` | `{skill['lane']}` | {deps} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- The `256` root cells live in `root_cells_256.json`.")
    lines.append("- The first executable future skills live under `skills/<slug>/FUTURE SKILL.md`.")
    lines.append("- The full `256^256` plan is generative, not a literal static list.")
    REGISTRY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_wave_manifest(manifest: dict) -> None:
    lines: list[str] = []
    lines.append("# WAVE 0 PARALLEL MANIFEST")
    lines.append("")
    lines.append("run_id: FUTURE-SKILL-WAVE-0")
    lines.append(
        "objective: Instantiate the first executable frontier of future skills from the 256x256 Athena skill lattice."
    )
    lines.append("wave_index: 0")
    lines.append("truth_class: OK for local incubation, BLOCKED for live Docs retrieval until OAuth is configured")
    lines.append("")
    lines.append("## Lanes")
    lines.append("")
    grouped: dict[str, list[dict]] = {}
    for skill in manifest["frontier_skills"]:
        grouped.setdefault(skill["lane"], []).append(skill)
    lane_order = manifest.get("lane_order") or sorted(grouped)
    for lane in lane_order:
        skills = grouped.get(lane, [])
        if not skills:
            continue
        lines.append(f"### {lane}")
        lines.append("")
        for skill in skills:
            deps = ", ".join(skill["depends_on"]) if skill["depends_on"] else "none"
            lines.append(
                f"- `{skill['slug']}` | addr `{skill['address']}` | {skill['priority']} | deps: {deps}"
            )
        lines.append("")
    lines.append("## Stop Conditions")
    lines.append("")
    lines.append("- Stop when every frontier skill has a scaffold and lawful references.")
    lines.append("- Stop early for live-memory execution if `credentials.json` and `token.json` are still missing.")
    lines.append("- Expand Wave 1 only after a subset of Wave 0 skills reach stable `OK` or `NEAR`.")
    WAVE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hyperdimensional_outputs(manifest: dict) -> None:
    mapping = manifest.get("higher_dimensional_mapping")
    if not mapping:
        return
    HYPER_JSON_PATH.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    lines: list[str] = []
    lines.append("# Higher-Dimensional Coordinates")
    lines.append("")
    lines.append(f"`NSCoord = ({', '.join(mapping.get('ns_coord', []))})`")
    lines.append("")
    lines.append("## Face6")
    lines.append("")
    for face in mapping.get("face6", []):
        lines.append(f"- `{face}`")
    lines.append("")
    if mapping.get("arcs"):
        lines.append("## Arcs")
        lines.append("")
        for arc in mapping.get("arcs", []):
            lines.append(f"- `{arc}`")
        lines.append("")
    if mapping.get("rails"):
        lines.append("## Rails")
        lines.append("")
        for rail in mapping.get("rails", []):
            lines.append(f"- `{rail}`")
        lines.append("")
    if mapping.get("hub16"):
        lines.append("## Hub16")
        lines.append("")
        for hub in mapping.get("hub16", []):
            lines.append(f"- `{hub}`")
        lines.append("")
    if mapping.get("families"):
        lines.append("## Family Dimension")
        lines.append("")
        for family in mapping.get("families", []):
            lines.append(f"- `{family}`")
        lines.append("")
    lines.append("## Depth Levels")
    lines.append("")
    for depth, meaning in mapping.get("depth_levels", {}).items():
        lines.append(f"- `{depth}`: {meaning}")
    lines.append("")
    lines.append("## Packet Classes")
    lines.append("")
    for packet in mapping.get("packet_classes", []):
        lines.append(f"- `{packet}`")
    lines.append("")
    lines.append("## Truth Classes")
    lines.append("")
    for truth in mapping.get("truth_classes", []):
        lines.append(f"- `{truth}`")
    lines.append("")
    if mapping.get("regimes"):
        lines.append("## Regimes")
        lines.append("")
        for regime in mapping.get("regimes", []):
            lines.append(f"- `{regime}`")
    lines.append("")
    lines.append("## Metallic Scale Overlay")
    lines.append("")
    for name, detail in manifest.get("metallic_scales", {}).items():
        lines.append(
            f"- `{name}`: {detail.get('elements')} elements | {detail.get('role')}"
        )
    HYPER_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_family_meta_swarm(manifest: dict) -> None:
    families = manifest.get("family_meta_swarm")
    if not families:
        return
    FAMILY_JSON_PATH.write_text(json.dumps(families, indent=2) + "\n", encoding="utf-8")
    lines: list[str] = []
    lines.append("# Meta-Swarm Family Frontier")
    lines.append("")
    lines.append("| Family | Weight | Best Front | Preferred Artifact |")
    lines.append("| --- | --- | --- | --- |")
    for family in families:
        lines.append(
            f"| `{family['family']}` | `{family['weight']}` | {family['best_front']} | {family['preferred_artifact']} |"
        )
    lines.append("")
    lines.append("## Rule")
    lines.append("")
    lines.append("- Split by family first, then manuscript, then chapter, then section.")
    lines.append("- Contract in reverse only after sibling fronts have been compared for emergent lines.")
    FAMILY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_swarm_wave_manifest(manifest: dict) -> None:
    families = manifest.get("family_meta_swarm", [])
    hyper = [
        skill
        for skill in manifest["frontier_skills"]
        if skill["lane"] in {"hypermap", "neural-swarm", "control-plane", "swarm"}
    ]
    if not hyper:
        return
    lines: list[str] = []
    lines.append("# SWARM WAVE 0 MANIFEST")
    lines.append("")
    lines.append("run_id: FUTURE-SKILL-SWARM-WAVE-0")
    lines.append("objective: Materialize the higher-dimensional and meta-swarm layer that the flat root lattice alone cannot capture.")
    lines.append("wave_index: 0H")
    lines.append("truth_class: NEAR")
    lines.append("")
    lines.append("## Family Ganglia")
    lines.append("")
    for family in families:
        lines.append(
            f"- `{family['family']}` | weight `{family['weight']}` | front: {family['best_front']}"
        )
    lines.append("")
    lines.append("## Hypermap, Control, And Swarm Skills")
    lines.append("")
    for skill in hyper:
        deps = ", ".join(skill["depends_on"]) if skill["depends_on"] else "none"
        lines.append(
            f"- `{skill['slug']}` | lane `{skill['lane']}` | addr `{skill['address']}` | deps: {deps}"
        )
    lines.append("")
    lines.append("## Expected Writeback")
    lines.append("")
    lines.append("- nervous-system ganglia")
    lines.append("- neural regime ganglion and bridge packets")
    lines.append("- hub legality and truth-promotion control surfaces")
    lines.append("- neuron library")
    lines.append("- swarm and wave manifests")
    lines.append("- packet and session handoff surfaces")
    SWARM_WAVE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_skill_doc(skill: dict) -> str:
    triggers = skill.get("triggers") or [skill["slug"].replace("-", " ")] + GENERIC_TRIGGERS[skill["operator"]]
    inputs = skill.get("inputs") or GENERIC_INPUTS[skill["substrate"]]
    outputs = skill.get("outputs") or GENERIC_OUTPUTS[skill["closure"]]
    procedure = skill.get("procedure") or GENERIC_PROCEDURE[skill["operator"]]
    validation = skill.get("validation") or GENERIC_VALIDATION[skill["closure"]]
    failure_modes = skill.get("failure_modes") or GENERIC_FAILURES[skill["operator"]]
    lines: list[str] = []
    lines.append(f"# {skill['name']}")
    lines.append("")
    lines.append("## address")
    lines.append(skill["address"])
    lines.append("")
    lines.append("## priority")
    lines.append(skill["priority"])
    lines.append("")
    lines.append("## lane")
    lines.append(skill["lane"])
    lines.append("")
    if skill.get("ns_coord"):
        lines.append("## nervous-system coordinate")
        for key, value in skill["ns_coord"].items():
            lines.append(f"- `{key}`: `{value}`")
        lines.append("")
    if skill.get("metallic_scale"):
        lines.append("## metallic scale")
        lines.append(skill["metallic_scale"])
        lines.append("")
    if skill.get("swarm_role"):
        lines.append("## swarm role")
        lines.append(skill["swarm_role"])
        lines.append("")
    if skill.get("family_targets"):
        lines.append("## family targets")
        for item in skill["family_targets"]:
            lines.append(f"- `{item}`")
        lines.append("")
    lines.append("## description")
    lines.append(skill["description"])
    lines.append("")
    lines.append("## triggers")
    for item in triggers:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## inputs")
    for item in inputs:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## outputs")
    for item in outputs:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## procedure")
    for index, item in enumerate(procedure, start=1):
        lines.append(f"{index}. {item}")
    lines.append("")
    lines.append("## validation")
    for item in validation:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## failure modes")
    for item in failure_modes:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## references")
    for item in skill["references"]:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## rationale")
    lines.append(skill["rationale"])
    return "\n".join(lines) + "\n"


def write_skill_docs(manifest: dict) -> None:
    for skill in manifest["frontier_skills"]:
        target_dir = SKILLS_DIR / skill["slug"]
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / "FUTURE SKILL.md"
        target_path.write_text(render_skill_doc(skill), encoding="utf-8")


def main() -> None:
    manifest = load_manifest()
    cells = build_root_cells(manifest)
    write_root_cells(cells)
    write_registry(manifest)
    write_wave_manifest(manifest)
    write_hyperdimensional_outputs(manifest)
    write_family_meta_swarm(manifest)
    write_swarm_wave_manifest(manifest)
    write_skill_docs(manifest)
    print(f"Rendered {len(cells)} root cells and {len(manifest['frontier_skills'])} future skill docs.")


if __name__ == "__main__":
    main()

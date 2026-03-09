from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "future_skill_frontier.json"


def slugify(text: str) -> str:
    cleaned = []
    for ch in text.lower():
        if ch.isalnum():
            cleaned.append(ch)
        else:
            cleaned.append("_")
    slug = "".join(cleaned)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def write_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def ganglion_doc(family: dict) -> str:
    family_name = family["family"]
    return f"""# GANGLION_{slugify(family_name)}

## Family

`{family_name}`

## Current Weight

`{family["weight"]}`

## Best Front

{family["best_front"]}

## Preferred Artifact

{family["preferred_artifact"]}

## Local Swarm Tasks

1. bind the family to the higher-dimensional skill frontier
2. split the family into pods before section-level oversharding
3. preserve one local queue, one receipt surface, and one contraction target
4. expose the strongest family neuron targets

## Contraction Rule

- family outputs must contract into cortex-facing artifacts
- unresolved contradictions must go to ledgers, not vanish
"""


def neuron_docs() -> dict[str, str]:
    return {
        "NEURON_google_docs_to_local_corpus.md": """# NEURON_google_docs_to_local_corpus

## NodeID

`NEURON_GOOGLE_DOCS_LOCAL_CORPUS`

## SourceFamily

- `Trading Bot`
- live Google Docs result sets

## TargetFamily

- `self_actualize`
- local witness packets

## Operator

Live-memory ingress with provenance capture.

## WitnessSet

- query
- document title
- modified time
- owner
- link
- local witness packet path
""",
        "NEURON_math_to_neural_runtime_bridge.md": """# NEURON_math_to_neural_runtime_bridge

## NodeID

`NEURON_MATH_NEURAL_RUNTIME`

## SourceFamily

- `MATH`
- formal framework and theorem surfaces

## TargetFamily

- `NERUAL NETWORK`
- `self_actualize/runtime`

## Operator

Theorem-to-runtime bridge with benchmark handoff.

## WitnessSet

- theorem source
- runtime target
- benchmark surface
- replay path
""",
        "NEURON_family_frontier_to_wave_scheduler.md": """# NEURON_family_frontier_to_wave_scheduler

## NodeID

`NEURON_FRONTIER_WAVE_SCHEDULER`

## SourceFamily

- family frontier matrix

## TargetFamily

- swarm wave manifests
- packet planner

## Operator

Frontier compression into synchronized wave scheduling.

## WitnessSet

- family weight
- best front
- preferred artifact
- assigned wave
""",
        "NEURON_hypermap_to_packet_truth.md": """# NEURON_hypermap_to_packet_truth

## NodeID

`NEURON_HYPERMAP_PACKET_TRUTH`

## SourceFamily

- higher-dimensional mapping

## TargetFamily

- packet manifests
- ledgers

## Operator

Translate NSCoord into packet class and truth-typed execution surfaces.

## WitnessSet

- face
- rail
- depth
- packet class
- truth class
"""
    }


def swarm_doc(skills: list[dict], families: list[dict]) -> str:
    lines = [
        "# SWARM_2026-03-09_future_skill_meta_swarm",
        "",
        "## Goal",
        "",
        "Run the future-skill plan as a higher-dimensional family federation instead of a flat root lattice.",
        "",
        "## Active Families",
        "",
    ]
    for family in families:
        lines.append(f"- `{family['family']}` | weight `{family['weight']}` | front: {family['best_front']}")
    lines.extend(["", "## Active Skill Pods", ""])
    for skill in skills:
        lines.append(f"- `{skill['slug']}` | lane `{skill['lane']}` | addr `{skill['address']}`")
    lines.extend([
        "",
        "## Contraction Target",
        "",
        "- nervous-system ganglia",
        "- neuron library",
        "- wave manifests",
        "- cortex writeback artifacts",
    ])
    return "\n".join(lines) + "\n"


def wave_doc(skills: list[dict]) -> str:
    lines = [
        "# WAVE_2026-03-09_future_skill_meta_swarm",
        "",
        "## Goal",
        "",
        "Synchronize the hypermap and swarm skill families into one bounded execution wave.",
        "",
        "## Active Pods",
        "",
        "1. hypermap pod",
        "2. ganglion pod",
        "3. neuron pod",
        "4. wave and cortex pod",
        "",
        "## Skills",
        "",
    ]
    for skill in skills:
        lines.append(f"- `{skill['slug']}` | deps: {', '.join(skill['depends_on']) if skill['depends_on'] else 'none'}")
    lines.extend([
        "",
        "## Residuals",
        "",
        "- live Docs remains blocked until OAuth files exist",
        "- family ganglia should deepen from seed notes into live queues and receipts",
    ])
    return "\n".join(lines) + "\n"


def packet_docs(skills: list[dict]) -> dict[str, str]:
    return {
        "POD_future_skill_hypermap.md": """# POD_future_skill_hypermap

## Front

Future skill hypermap expansion

## Depth

`D2 -> D3`

## Active Skills

- `face-manifold-router`
- `arc-rail-phase-router`
- `packet-truth-typist`
- `metallic-scale-planner`

## Contraction Target

`HYPERDIMENSIONAL_COORDINATES.md`
""",
        "POD_future_skill_meta_swarm.md": """# POD_future_skill_meta_swarm

## Front

Future skill meta-swarm expansion

## Depth

`D1 -> D3`

## Active Skills

- `ganglion-bootstrapper`
- `neuron-library-builder`
- `pod-frontier-splitter`
- `wave-synchronizer`
- `family-swarm-conductor`
- `cortex-writeback-manager`

## Contraction Target

`SWARM_WAVE_0_MANIFEST.md`
""",
        "SYN_future_skill_meta_swarm.md": """# SYN_future_skill_meta_swarm

## Synthesis

The future skill frontier now occupies both the root 256 lattice and the higher-dimensional swarm manifold.

## Required Next Move

- deepen family ganglia
- create live pod receipts
- benchmark wave quality
""",
        "LEDGER_future_skill_meta_swarm.md": """# LEDGER_future_skill_meta_swarm

## Witness

- root lattice registry exists
- hyper-dimensional coordinate output exists
- family meta-swarm output exists

## Active Blocker

- Google Docs OAuth gate remains blocked
""",
    }


def session_doc() -> str:
    return """# SESSION_2026-03-09_future_skill_meta_swarm

## Zero Point

- root 256 lattice exists
- NSCoord layer exists
- family meta-swarm is seeded
- first ganglia, neurons, pods, waves, and ledgers exist

## Resume Order

1. read `ECOSYSTEM/FUTURE_SKILLS/FUTURE_SKILL_PLAN_256X256.md`
2. read `ECOSYSTEM/FUTURE_SKILLS/SWARM_WAVE_0_MANIFEST.md`
3. read `self_actualize/mycelium_brain/nervous_system/10_deeper_emergent_neural_swarm.md`
4. claim the next family pod or hypermap front
"""


def main() -> None:
    manifest = load_manifest()
    workspace = Path(manifest["workspace_root"])
    nervous = workspace / "self_actualize" / "mycelium_brain" / "nervous_system"

    families = manifest.get("family_meta_swarm", [])
    swarm_skills = [
        skill
        for skill in manifest["frontier_skills"]
        if skill["lane"] in {"hypermap", "swarm"}
    ]

    for family in families:
        target = nervous / "ganglia" / f"GANGLION_{slugify(family['family'])}.md"
        write_if_missing(target, ganglion_doc(family))

    for filename, content in neuron_docs().items():
        write_if_missing(nervous / "neurons" / filename, content)

    write_if_missing(
        nervous / "swarms" / "SWARM_2026-03-09_future_skill_meta_swarm.md",
        swarm_doc(swarm_skills, families),
    )
    write_if_missing(
        nervous / "waves" / "WAVE_2026-03-09_future_skill_meta_swarm.md",
        wave_doc(swarm_skills),
    )
    for filename, content in packet_docs(swarm_skills).items():
        if filename.startswith("LEDGER_"):
            write_if_missing(nervous / "ledgers" / filename, content)
        else:
            write_if_missing(nervous / "packets" / filename, content)
    write_if_missing(
        nervous / "sessions" / "SESSION_2026-03-09_future_skill_meta_swarm.md",
        session_doc(),
    )
    print(f"Seeded meta-swarm runtime surfaces for {len(families)} families and {len(swarm_skills)} skills.")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
ATHENA_FLEET_ROOT = WORKSPACE_ROOT / "Athena FLEET"
ECOSYSTEM_ROOT = ATHENA_FLEET_ROOT / "QSHRINK2_CORPUS_ECOSYSTEM"

NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"

OUTPUT_CAPABILITY_JSON = SELF_ACTUALIZE_ROOT / "qshrink_capability_stack.json"
OUTPUT_DEBUG_LEDGER = ECOSYSTEM_ROOT / "05_QSHRINK_DEBUG_LEDGER.md"
OUTPUT_USE_CASE_ATLAS = ECOSYSTEM_ROOT / "06_QSHRINK_MAXIMUM_CAPACITY_USE_CASE_ATLAS.md"
OUTPUT_TOOLKIT_HANDBOOK = ECOSYSTEM_ROOT / "07_QSHRINK_TOOLKIT_HANDBOOK.md"
OUTPUT_SKILL_MATRIX = ECOSYSTEM_ROOT / "08_QSHRINK_SKILL_ROUTING_MATRIX.md"
OUTPUT_ARTIFACT_SCHEMA = ECOSYSTEM_ROOT / "09_QSHRINK_HOLOGRAPHIC_ARTIFACT_SCHEMA.json"
OUTPUT_COMPACTION_CONTRACT = ECOSYSTEM_ROOT / "10_QSHRINK_COMPACTION_CONTRACT.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


TOOLKIT_SECTIONS = [
    {
        "id": "TK01",
        "name": "Control",
        "surface": "QSHRINK - ATHENA (internal use)/00_CONTROL/",
        "role": "charter, address law, corpus bindings, framework law",
        "owns": "public-private split, operating invariants, front map",
    },
    {
        "id": "TK02",
        "name": "Geometry",
        "surface": "QSHRINK - ATHENA (internal use)/01_GEOMETRY/",
        "role": "Square, Circle, Triangle, Torus movement grammar",
        "owns": "addressing, recurrence, routing choice, toroidal return",
    },
    {
        "id": "TK03",
        "name": "Operators",
        "surface": "QSHRINK - ATHENA (internal use)/02_OPERATORS/",
        "role": "Partition, Quantize, Bucket, Code work grammar",
        "owns": "decomposition, lawful loss, bulk/escape split, runnable carriers",
    },
    {
        "id": "TK04",
        "name": "Swarm",
        "surface": "QSHRINK - ATHENA (internal use)/03_SWARM/",
        "role": "agent roles, active runtime, topology, metallic scaling",
        "owns": "parallelism, dissatisfaction escalation, pantheon coordination",
    },
    {
        "id": "TK05",
        "name": "Metro",
        "surface": "QSHRINK - ATHENA (internal use)/04_METRO/",
        "role": "transfer hubs, station registry, tensor coordinates",
        "owns": "cross-body movement, handoff integrity, route preservation",
    },
    {
        "id": "TK06",
        "name": "Manuscript Space",
        "surface": "QSHRINK - ATHENA (internal use)/05_MANUSCRIPT_SPACE/",
        "role": "root-cell index, recursive expansion protocol",
        "owns": "seed/skeleton/full artifact growth",
    },
    {
        "id": "TK07",
        "name": "Ledgers And Manuscripts",
        "surface": "QSHRINK - ATHENA (internal use)/06_LEDGERS/ and 07_MANUSCRIPTS/",
        "role": "bindings, frontier, next loop seed, title/abstract/review maps",
        "owns": "witness memory, canonical narrative outputs",
    },
    {
        "id": "TK08",
        "name": "Loop Skill",
        "surface": "QSHRINK - ATHENA (internal use)/08_LOOP_SKILL/",
        "role": "37-gate restart law and dissatisfaction handling",
        "owns": "improvement loops, escalation discipline, anti-stagnation",
    },
    {
        "id": "TK09",
        "name": "Repair Lattice",
        "surface": "QSHRINK - ATHENA (internal use)/09_REPAIR_256X256/",
        "role": "repair manifold and recursive dissatisfaction field",
        "owns": "self-healing, corrective expansion, bounded repair planning",
    },
    {
        "id": "TK10",
        "name": "Chapter 11 Lattice",
        "surface": "QSHRINK - ATHENA (internal use)/10_CH11_256X256/",
        "role": "origin, void, zero-point, seed return",
        "owns": "zero-point extraction, contradiction collapse, restart seeds",
    },
    {
        "id": "TK11",
        "name": "Runtime Package",
        "surface": "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS/athena_os/qshrink/",
        "role": "typed executable implementation of core, lenses, pipeline, container",
        "owns": "programmatic compression, container legality, runtime verification",
    },
]

USE_CASES = [
    {
        "id": "UC01",
        "name": "Corpus Storage Compaction",
        "front": "Athena FLEET + self_actualize",
        "safety": "hybrid-with-guardrails",
        "artifacts": "atlas, pruning ledger, compaction contract",
        "skills": ["q-shrink", "manuscript-intake", "corpus-status-synthesizer"],
    },
    {
        "id": "UC02",
        "name": "Holographic Manuscript Seeds",
        "front": "QSHRINK internal doctrine",
        "safety": "internal-only",
        "artifacts": "Omega, Alpha+, Delta+, witness, restart seed",
        "skills": ["q-shrink", "manuscript-final-drafter", "manuscript-seed"],
    },
    {
        "id": "UC03",
        "name": "Deterministic Container Archives",
        "front": "Athena OS runtime",
        "safety": "public-safe",
        "artifacts": "container bytes, manifest, chunk checksums",
        "skills": ["q-shrink"],
    },
    {
        "id": "UC04",
        "name": "Seekable Stream Transport",
        "front": "Athena OS runtime",
        "safety": "public-safe",
        "artifacts": "seek lattice, synchronized container, legality checks",
        "skills": ["q-shrink", "hybrid-bridger"],
    },
    {
        "id": "UC05",
        "name": "Repairable Bounded-Damage Carriers",
        "front": "Athena OS runtime + Repair lattice",
        "safety": "hybrid-with-guardrails",
        "artifacts": "repair prefix, repair ledger, container diagnostics",
        "skills": ["q-shrink", "improvement-gate-escalator"],
    },
    {
        "id": "UC06",
        "name": "Runtime Codec Verification",
        "front": "Athena OS runtime",
        "safety": "public-safe",
        "artifacts": "verification JSON, smoke tests, debug ledger",
        "skills": ["q-shrink", "shadow-analysis"],
    },
    {
        "id": "UC07",
        "name": "Atlas Reduction And Mirror Regeneration",
        "front": "Athena FLEET + mirrors",
        "safety": "hybrid-with-guardrails",
        "artifacts": "mirror policy, regenerable zone rules, dedupe rubric",
        "skills": ["manuscript-intake", "archive-atlas-ingestor", "metro-cartography"],
    },
    {
        "id": "UC08",
        "name": "Skill And Agent Compression",
        "front": "Guild Hall + skill registry",
        "safety": "internal-only",
        "artifacts": "skill routing matrix, handoff contracts, quest bindings",
        "skills": ["guild-hall-quest-loop", "thirty-seven-gate-skillsmith"],
    },
    {
        "id": "UC09",
        "name": "Metro Corridor Preservation",
        "front": "QSHRINK metro + deeper network",
        "safety": "internal-only",
        "artifacts": "corridor maps, tensor coordinates, transfer hubs",
        "skills": ["deeper-integrated-neural-network", "metro-cartography"],
    },
    {
        "id": "UC10",
        "name": "Archive Promotion",
        "front": "MATH archives + promoted live roots",
        "safety": "hybrid-with-guardrails",
        "artifacts": "archive manifest, promotion candidate scoring, live-root bridge",
        "skills": ["archive-atlas-ingestor", "corpus-status-synthesizer"],
    },
    {
        "id": "UC11",
        "name": "Contradiction And Blocker Packets",
        "front": "Guild Hall + Temple + queue",
        "safety": "internal-only",
        "artifacts": "contradiction packets, blocker ledgers, restart seeds",
        "skills": ["guild-hall-quest-loop", "shadow-analysis", "improvement-gate-escalator"],
    },
    {
        "id": "UC12",
        "name": "SaaS-Safe Public Productization",
        "front": "Legacy public lane",
        "safety": "public-safe",
        "artifacts": "bounded API, public-safe profiles, legacy read-only guardrails",
        "skills": ["q-shrink", "manuscript-final-drafter"],
    },
]

SECOND_WAVE_SKILLS = [
    {
        "skill": "manuscript-final-drafter",
        "role": "promote compressed outputs into polished canonical markdown",
        "quest": "QS64-53 Promotion-Refine-Square",
    },
    {
        "skill": "manuscript-seed",
        "role": "expand holographic seeds back into structured long-form doctrine",
        "quest": "QS64-60 Promotion-Synthesize-Fractal",
    },
    {
        "skill": "thirty-seven-gate-skillsmith",
        "role": "turn repeated QSHRINK workflows into reusable local skills",
        "quest": "QS64-63 Promotion-Scale-Cloud",
    },
    {
        "skill": "origin-excavator",
        "role": "extract Chapter 11 zero points and origin seeds for compression roots",
        "quest": "QS64-12 QShrink-Synthesize-Fractal",
    },
]

THIRD_WAVE_SKILLS = [
    {
        "skill": "holographic-rotation",
        "role": "stress-test compressed artifacts across orthogonal viewpoints before promotion",
        "quest": "QS64-10 QShrink-Synthesize-Flower",
    },
    {
        "skill": "hybrid-bridger",
        "role": "bridge discrete runtime codecs and continuous manuscript geometry",
        "quest": "QS64-42 Runtime-Synthesize-Flower",
    },
    {
        "skill": "void-expansion",
        "role": "generate frontier use cases when compression moves beyond currently named lanes",
        "quest": "QS64-48 Runtime-Scale-Fractal",
    },
    {
        "skill": "systemic-solver",
        "role": "project QSHRINK into civilizational-scale storage and routing problems",
        "quest": "QS64-64 Promotion-Scale-Fractal",
    },
]


def build_payload() -> dict:
    network = load_json(NETWORK_INTEGRATION_PATH)
    agent_matrix = load_json(AGENT_MATRIX_PATH)
    runtime = load_json(RUNTIME_VERIFICATION_PATH)

    artifact_schema = {
        "schema_version": "qshrink-holographic-artifact/1.0",
        "required_fields": [
            "omega",
            "four_elements",
            "zero_point",
            "delta_skeleton",
            "witness",
            "restart_seed",
        ],
        "optional_fields": [
            "front_map",
            "compression_level",
            "source_surfaces",
            "safety_class",
            "quest_binding",
            "notes",
        ],
        "compression_levels": {
            "OMEGA+": "full expansion or source-preserving witness bundle",
            "DELTA+": "section or node skeleton with route-preserving structure",
            "ALPHA+": "seed plus developed zero point",
            "Omega": "one sentence or equation generator",
        },
    }

    compaction_contract = {
        "schema_version": "qshrink-compaction-contract/1.0",
        "invariants": [
            "legacy_public_is_read_only",
            "authority_surfaces_are_not_physically_pruned_without_explicit_ledger",
            "generated_zones_are_regenerated_not_side_copied",
            "docs_gate_blockers_are_preserved_honestly",
        ],
        "action_classes": {
            "retain": "keep live and compact only by view or reference",
            "regenerate": "rebuild from index on demand",
            "dedupe_by_reference": "replace identical siblings with manifest-backed references",
            "archive": "keep packed until promotion threshold is met",
            "promote_live": "extract into a routed live root with lineage witness",
        },
        "duplicate_priority_rubric": [
            "raw_savings_bytes",
            "authority_risk",
            "regenerability",
            "replay_cost",
            "cross_body_connectivity",
        ],
        "compression_profiles": {
            "legacy_public": "retain + publish-safe wrappers only",
            "internal_doctrine": "retain doctrine + regenerate derived lattices",
            "runtime_code": "retain code + verify behavior instead of lossy compression",
            "witness_document": "preserve source witness + edit through mirrors or capsules",
            "mirror_surface": "regenerate on demand from index",
            "archive_bundle": "archive until promotion threshold is met",
        },
        "docs_gate_policy": {
            "state_when_missing_oauth": "BLOCKED",
            "allowed_behavior": "local-only synthesis and blocker-preserving writeback",
            "disallowed_behavior": "claiming live docs sync without authenticated proof",
        },
    }

    return {
        "generated_at": utc_now(),
        "truth": "OK" if runtime.get("truth") == "OK" else "NEAR",
        "docs_gate": agent_matrix["docs_gate"],
        "corpus_metrics": network["corpus_metrics"],
        "runtime_verification": runtime,
        "front_map": [
            {
                "id": "FRONT-LEGACY",
                "surface": "MATH/FINAL FORM/Q shrink",
                "role": "legacy/public volume stack and SaaS-safe boundary",
                "safety": "public-safe",
            },
            {
                "id": "FRONT-INTERNAL",
                "surface": "QSHRINK - ATHENA (internal use)",
                "role": "maximum-capacity doctrine, swarm, metro, repair, Chapter 11",
                "safety": "internal-only",
            },
            {
                "id": "FRONT-RUNTIME",
                "surface": "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS/athena_os/qshrink",
                "role": "typed executable runtime package",
                "safety": "hybrid-with-guardrails",
            },
            {
                "id": "FRONT-FLEET-HALL",
                "surface": "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM + Guild Hall",
                "role": "atlas, pruning, questing, family routing, agent orchestration",
                "safety": "hybrid-with-guardrails",
            },
        ],
        "invariants": [
            "Legacy public QSHRINK remains read-only.",
            "Authority surfaces are compacted by pointer and manifest before physical deletion.",
            "Docs gate remains blocker-honest until OAuth exists.",
            "Generated lattices are storage classes, not handwritten doctrine.",
        ],
        "toolkit_sections": TOOLKIT_SECTIONS,
        "maximum_capacity_use_cases": USE_CASES,
        "minimum_viable_quartet": [
            "q-shrink",
            "manuscript-intake",
            "shadow-analysis",
            "guild-hall-quest-loop",
        ],
        "second_wave_skills": SECOND_WAVE_SKILLS,
        "third_wave_skills": THIRD_WAVE_SKILLS,
        "handoff_contracts": [
            "manuscript-intake -> q-shrink: intake delivers atlas-grounded pressure surfaces, not raw folder intuition",
            "q-shrink -> shadow-analysis: every contraction candidate is audited before promotion or pruning",
            "shadow-analysis -> guild-hall-quest-loop: blind spots become ownerable work, not suppressed doubt",
            "q-shrink -> manuscript-final-drafter: compressed outputs can be promoted into readable canonical markdown",
            "archive-atlas-ingestor -> q-shrink: promoted roots re-enter the same compaction grammar after extraction",
            "improvement-gate-escalator -> q-shrink: weak passes automatically recurse deeper instead of polishing summaries",
        ],
        "artifact_schema": artifact_schema,
        "compaction_contract": compaction_contract,
    }


def render_debug_ledger(payload: dict) -> str:
    runtime_checks = payload["runtime_verification"]["checks"]
    lines = [
        "# QSHRINK Debug Ledger",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Truth: `{payload['truth']}`",
        f"- Docs gate: `{payload['docs_gate']}`",
        f"- Corpus files scanned: `{payload['corpus_metrics']['total_files']}`",
        f"- Duplicate groups: `{payload['corpus_metrics']['duplicate_groups_count']}`",
        "",
        "## Front Map",
        "",
    ]
    for front in payload["front_map"]:
        lines.extend(
            [
                f"### {front['id']}",
                "",
                f"- Surface: `{front['surface']}`",
                f"- Role: {front['role']}",
                f"- Safety: `{front['safety']}`",
                "",
            ]
        )

    lines.extend(["## Non-Negotiable Invariants", ""])
    for invariant in payload["invariants"]:
        lines.append(f"- {invariant}")

    lines.extend(["", "## Runtime Verification", ""])
    for check in runtime_checks:
        lines.extend(
            [
                f"### {check['name']}",
                "",
                f"- Truth: `{check['truth']}`",
                f"- Detail: `{json.dumps(check['detail'], ensure_ascii=True)}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Resolved This Pass",
            "",
            "- package-local bootstrap drift no longer blocks `athena_os.qshrink` import",
            "- validator float comparison now uses tolerance instead of exact binary equality",
            "- validator entrypoints are seeded for replay-safe behavior",
            "- pipeline reconstruction now preserves projection scale and numeric carrier state instead of only passing a shape-level smoke test",
            "- container manifest parsing no longer trips on header length mismatch",
            "- stable convenience `compress` and `decompress` now roundtrip through a direct-sum byte container",
            "- dedicated smoke tests now cover lossless bytes, numeric codec roundtrip, lossy bound witness, manifest roundtrip, and synchronized seekable containers",
            "",
            "## Active Risks",
            "",
            "- broader Athena OS `meta` and kernel surfaces remain larger than the QSHRINK runtime guarantee and should be debugged separately from the now-green QSHRINK import lane",
            "- Google Docs ingress remains blocked and must not be faked by any future synthesis pass",
            "- exact duplicate pressure is visible, but physical pruning should still follow the compaction contract instead of manual deletion",
        ]
    )
    return "\n".join(lines) + "\n"


def render_use_case_atlas(payload: dict) -> str:
    lines = [
        "# QSHRINK Maximum-Capacity Use-Case Atlas",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "QSHRINK is not only a summarizer. It is a compression, routing, transport, repair, archive, and governance framework.",
        "",
    ]
    for use_case in payload["maximum_capacity_use_cases"]:
        skills = ", ".join(f"`{skill}`" for skill in use_case["skills"])
        lines.extend(
            [
                f"## {use_case['id']} `{use_case['name']}`",
                "",
                f"- Primary front: `{use_case['front']}`",
                f"- Safety: `{use_case['safety']}`",
                f"- Expected artifacts: {use_case['artifacts']}",
                f"- Core skills: {skills}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def render_toolkit_handbook(payload: dict) -> str:
    lines = [
        "# QSHRINK Toolkit Handbook",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
    ]
    for section in payload["toolkit_sections"]:
        lines.extend(
            [
                f"## {section['id']} `{section['name']}`",
                "",
                f"- Surface: `{section['surface']}`",
                f"- Role: {section['role']}",
                f"- Owns: {section['owns']}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def render_skill_matrix(payload: dict) -> str:
    first_wave = load_json(AGENT_MATRIX_PATH)["first_wave_agents"]
    lines = [
        "# QSHRINK Skill Routing Matrix",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "## Minimum Viable Quartet",
        "",
    ]
    for skill in payload["minimum_viable_quartet"]:
        lines.append(f"- `{skill}`")

    lines.extend(["", "## First Wave", ""])
    for agent in first_wave:
        lines.extend(
            [
                f"### `{agent['skill']}` -> `{agent['quest']}`",
                "",
                f"- Status: `{agent['status']}`",
                f"- Role: {agent['role']}",
                f"- Outputs: {'; '.join(agent['expected_outputs'])}",
                "",
            ]
        )

    lines.extend(["## Second Wave", ""])
    for agent in payload["second_wave_skills"]:
        lines.extend(
            [
                f"### `{agent['skill']}` -> `{agent['quest']}`",
                "",
                f"- Role: {agent['role']}",
                "",
            ]
        )

    lines.extend(["## Third Wave", ""])
    for agent in payload["third_wave_skills"]:
        lines.extend(
            [
                f"### `{agent['skill']}` -> `{agent['quest']}`",
                "",
                f"- Role: {agent['role']}",
                "",
            ]
        )

    lines.extend(["## Handoff Contracts", ""])
    for contract in payload["handoff_contracts"]:
        lines.append(f"- {contract}")

    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_payload()
    OUTPUT_CAPABILITY_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_DEBUG_LEDGER.write_text(render_debug_ledger(payload), encoding="utf-8")
    OUTPUT_USE_CASE_ATLAS.write_text(render_use_case_atlas(payload), encoding="utf-8")
    OUTPUT_TOOLKIT_HANDBOOK.write_text(render_toolkit_handbook(payload), encoding="utf-8")
    OUTPUT_SKILL_MATRIX.write_text(render_skill_matrix(payload), encoding="utf-8")
    OUTPUT_ARTIFACT_SCHEMA.write_text(json.dumps(payload["artifact_schema"], indent=2), encoding="utf-8")
    OUTPUT_COMPACTION_CONTRACT.write_text(json.dumps(payload["compaction_contract"], indent=2), encoding="utf-8")
    print(f"Wrote qshrink capability stack: {OUTPUT_CAPABILITY_JSON}")
    print(f"Wrote qshrink debug ledger: {OUTPUT_DEBUG_LEDGER}")
    print(f"Wrote qshrink use-case atlas: {OUTPUT_USE_CASE_ATLAS}")
    print(f"Wrote qshrink toolkit handbook: {OUTPUT_TOOLKIT_HANDBOOK}")
    print(f"Wrote qshrink skill matrix: {OUTPUT_SKILL_MATRIX}")
    print(f"Wrote qshrink artifact schema: {OUTPUT_ARTIFACT_SCHEMA}")
    print(f"Wrote qshrink compaction contract: {OUTPUT_COMPACTION_CONTRACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

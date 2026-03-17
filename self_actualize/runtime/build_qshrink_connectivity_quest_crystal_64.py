from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
GUILD_HALL_ROOT = WORKSPACE_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
OUTPUT_PATH = GUILD_HALL_ROOT / "12_QSHRINK_CONNECTIVITY_QUEST_CRYSTAL_64.md"

MOVES = ["Diagnose", "Refine", "Synthesize", "Scale"]
LENSES = ["Square", "Flower", "Cloud", "Fractal"]

DOMAINS = [
    {
        "name": "QShrink",
        "surfaces": [
            "QSHRINK - ATHENA (internal use)/",
            "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/",
            "self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use.md",
            "self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md",
        ],
        "why": "QSHRINK is now visible as one of the heaviest live infrastructure organs and needs to become load-bearing law rather than ambient doctrine.",
        "lane": "qshrink",
        "restart": "Activate the next QSHRINK corridor that most increases replay-safe contraction.",
    },
    {
        "name": "Connectivity",
        "surfaces": [
            "Athena FLEET/",
            "Trading Bot/",
            "ORGIN/",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
        ],
        "why": "The heaviest bodies are now named, but corridor handoffs between them still need a deliberate connective membrane.",
        "lane": "connectivity",
        "restart": "Promote the thinnest corridor that still blocks cross-body motion.",
    },
    {
        "name": "Runtime",
        "surfaces": [
            "MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS/athena_os/qshrink/",
            "self_actualize/runtime/",
            "self_actualize/qshrink_network_integration.json",
            "self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md",
        ],
        "why": "Holographic computing needs executable qshrink carriers, verifiers, and runtime contracts, not only manuscripts and atlases.",
        "lane": "runtime",
        "restart": "Harden the next executable lane that makes QSHRINK useful to live code and live routing.",
    },
    {
        "name": "Promotion",
        "surfaces": [
            "NERVOUS_SYSTEM/50_CORPUS_CAPSULES/qshrink/",
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            "self_actualize/mycelium_brain/receipts/",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/",
        ],
        "why": "The system now has enough evidence to promote QSHRINK into canonical writeback lanes across cortex, hall, manifests, and receipts.",
        "lane": "promotion",
        "restart": "Choose the next promotion that turns QSHRINK gains into canonical organism memory.",
    },
]

LENS_PHRASES = {
    "Square": {
        "focus": "addresses, contracts, route maps, and structural clarity",
        "artifact": "one contract, route map, or structural crosswalk",
    },
    "Flower": {
        "focus": "cadence, flow, handoff rhythm, and corridor movement",
        "artifact": "one cadence map or handoff rhythm surface",
    },
    "Cloud": {
        "focus": "truth classes, witness burden, uncertainty, and selection discipline",
        "artifact": "one ranked or witness-aware truth surface",
    },
    "Fractal": {
        "focus": "recursive reuse, restart law, multi-scale propagation, and loop stability",
        "artifact": "one restart-safe recursive pattern or multi-scale proof",
    },
}

MOVE_PHRASES = {
    "Diagnose": {
        "verb": "audit",
        "result": "names the current drift, deficit, or missing membrane",
    },
    "Refine": {
        "verb": "tighten",
        "result": "hardens one boundary, contract, or cadence without pretending total closure",
    },
    "Synthesize": {
        "verb": "bind",
        "result": "connects previously separate surfaces into one ownerable bridge",
    },
    "Scale": {
        "verb": "propagate",
        "result": "makes one working pattern reusable across more bodies or more passes",
    },
}


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def quest_lines(index: int, domain: dict, move: str, lens: str) -> list[str]:
    lens_info = LENS_PHRASES[lens]
    move_info = MOVE_PHRASES[move]
    quest_id = f"QS64-{index:02d}"
    title = f"{domain['name']}-{move}-{lens}"
    surfaces = "; ".join(f"`{surface}`" for surface in domain["surfaces"])
    return [
        f"### {quest_id} `{title}`",
        "",
        f"- Objective: {move_info['verb']} the {domain['name'].lower()} layer through {lens.lower()} concerns so the pass produces {lens_info['artifact']}.",
        f"- Why now: {domain['why']}",
        f"- Target surfaces: {surfaces}.",
        f"- Best lane: `{domain['lane']} -> {move.lower()} -> {lens.lower()}`",
        f"- Witness needed: one artifact that {move_info['result']} and keeps `{lens_info['focus']}` explicit.",
        f"- Writeback: one Guild Hall board update, one family/runtime/manifest writeback, and one receipt note.",
        f"- Restart seed: {domain['restart']}",
        "",
    ]


def build_text() -> str:
    lines = [
        "# QSHRINK Connectivity Quest Crystal 64",
        "",
        f"Date: `{utc_today()}`",
        "Truth: `OK`",
        "Live Docs Gate: blocked due to missing OAuth files, so this crystal is grounded in local corpus, Hall, runtime, and QSHRINK witness only.",
        "",
        "## Source Witness",
        "",
        "- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/01_FULL_FRAMEWORK_SYNTHESIS.md`",
        "- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/03_QSHRINK2_PRUNING_LEDGER.md`",
        "- `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/00_GUILD_HALL_INDEX.md`",
        "- `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/04_CHANGE_FEED_BOARD.md`",
        "- `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/05_REQUESTS_AND_OFFERS_BOARD.md`",
        "- `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md`",
        "- `self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md`",
        "- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use.md`",
        "- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet.md`",
        "- `NERVOUS_SYSTEM/00_INDEX.md`",
        "",
        "## Deep Synthesis",
        "",
        "The corpus is now large enough that QSHRINK cannot remain a local manuscript stack. It must become the lawful contraction membrane between source mass, runtime code, family routing, Guild Hall coordination, and canonical writeback.",
        "",
        "The full repo scan in Athena FLEET already shows the real pressure fronts: heavy witness documents, duplicate families, archive bundles, generated-regenerable lattices, mirror surfaces, and code/runtime bodies that still need a common compaction grammar. The open QSHRINK bridge quest identified the need. This crystal turns that need into a bounded 64-quest infrastructure sweep.",
        "",
        "Projection law:",
        "",
        "`Domain x Move x Lens = 4 x 4 x 4 = 64 quests`",
        "",
        "Domains:",
        "",
        "- `QShrink`: the Shiva contraction organ itself",
        "- `Connectivity`: the corridor membrane joining heavy live bodies",
        "- `Runtime`: executable qshrink carriers, contracts, and verifiers",
        "- `Promotion`: cortex, manifest, Hall, and receipt writeback",
        "",
        "Moves:",
        "",
        "- `Diagnose`: audit the current deficit honestly",
        "- `Refine`: harden one boundary or contract",
        "- `Synthesize`: bind separate surfaces into one bridge",
        "- `Scale`: make a working pattern reusable",
        "",
        "Lenses:",
        "",
        "- `Square`: structure and addressing",
        "- `Flower`: cadence and flow",
        "- `Cloud`: witness and truth selection",
        "- `Fractal`: recursive loop stability",
        "",
        "## Initial High-Leverage Extraction",
        "",
        "1. `QS64-09 QShrink-Synthesize-Square`",
        "2. `QS64-17 Connectivity-Diagnose-Square`",
        "3. `QS64-41 Runtime-Synthesize-Square`",
        "4. `QS64-49 Promotion-Diagnose-Square`",
        "5. `QS64-64 Promotion-Scale-Fractal`",
        "",
        "## The 64 Quests",
        "",
    ]

    index = 1
    for domain in DOMAINS:
        lines.append(f"## {domain['name']} Domain")
        lines.append("")
        for move in MOVES:
            for lens in LENSES:
                lines.extend(quest_lines(index, domain, move, lens))
                index += 1

    lines.extend(
        [
            "## Activation Law",
            "",
            "The first activation frontier is `QS64-09 QShrink-Synthesize-Square`: bind the new fleet-side QSHRINK ecosystem, family route map, Hall crystal, and manifest surfaces into one repeatable ownerable sweep.",
            "",
            "Every later activation should preserve the Hall quest law:",
            "",
            "`request -> quest -> witness -> writeback -> restart`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_PATH.write_text(build_text(), encoding="utf-8")
    print(f"Wrote qshrink connectivity crystal: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

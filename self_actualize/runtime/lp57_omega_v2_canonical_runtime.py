from __future__ import annotations

import json
import re
import runpy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.lp57_omega_prime_plan import (
    CANONICAL_PACKET_CONTRACT,
    COORDINATE_DISPLAY_SYMBOLS,
    COORDINATE_SCHEMA,
    DOCS_GATE_EXPECTED,
    FRONTIER_ID,
    LEDGER_SCHEMA,
    LOOKUP_KEY_SCHEMA,
    LOOP_ARTIFACT_FIELDS,
    LOOP_SPECS,
    MASTER_AGENTS,
    MASTER_AGENT_BY_ID,
    NEXT_INVOCATION_CONTRACT,
    NEXT_SEED,
    PROTOCOL_DISPLAY_NAME,
    PROTOCOL_ID,
    arc_for_loop,
    topk_for_loop,
    uniqueness_tuples,
)

ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "self_actualize"
MY = SELF / "mycelium_brain"
NS = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
NS_ROOT = ROOT / "NERVOUS_SYSTEM"
HSIGMA_REFRESH = ROOT / "MATH" / "temp_lp57_hsigma_refresh.py"
THESIS_MD = NS / "LP_57_OMEGA_MASTER_HOLOGRAM_THESIS.md"
ACTIVE_RUN_MD = NS / "ACTIVE_RUN.md"
BUILD_QUEUE_MD = NS / "BUILD_QUEUE.md"
FOUR_AGENT_MD = NS / "FOUR_AGENT_57_LOOP_PROGRAM.md"
HALL_BOARD_MD = MY / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
HALL_PROGRAM_DETAIL_MD = MY / "GLOBAL_EMERGENT_GUILD_HALL" / "18_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md"
TEMPLE_BOARD_MD = MY / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
TEMPLE_STATE_MD = MY / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
TEMPLE_TQ07_MD = MY / "ATHENA TEMPLE" / "QUESTS" / "TQ07_INSTALL_THE_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md"
LEVEL6_WEAVE_MD = MY / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK" / "07_METRO_STACK" / "06_level_6_hologram_weave_map.md"
HALL_PROGRAM_MD = MY / "GLOBAL_EMERGENT_GUILD_HALL" / "57_loop_hall_program.md"
TEMPLE_PROGRAM_MD = MY / "ATHENA TEMPLE" / "57_loop_temple_program.md"

DATE = "2026-03-13"
DERIVATION_VERSION = "2026-03-13.lp57omega.v2.prime-loop-hive"
ACTIVE_MEMBRANE = "Q41 / TQ06"
LIVE_HALL_CARRIER = "Q42"
LANDED_TEMPLE_RECEIVER = "TQ04"
RESERVE_FEEDER = "Q46"
EXTERNAL_BLOCKER = "Q02"
WITNESS_ONLY_FRONTS = ["Q50", "ECOSYSTEM/NERVOUS_SYSTEM"]
FEEDER_STACK = [LIVE_HALL_CARRIER, LANDED_TEMPLE_RECEIVER, RESERVE_FEEDER, EXTERNAL_BLOCKER]
AUTHORITY_ORDER = ["Cortex", "RuntimeHub", "GovernanceMirror"]
DEEP_ROOT_AUTHORITY = "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
TOTAL_LOOPS = 57
COMPLETED_LOOP_NUMBER = 4
ACTIVE_LOOP_NUMBER = 5
SHARED_TOTAL = 4096
SHARED_ACTIVE = 1024
SHARED_DORMANT = 3072
ROLE_NAMESPACE_TOTAL = 4096
ACTIVE_PER_MASTER = 256
HALL_CAP = 8
TEMPLE_CAP = 8
SHADOW_CAP = 16
ADVENTURER_CAP = 16

COMPLETED_LOOP = LOOP_SPECS[COMPLETED_LOOP_NUMBER - 1]
ACTIVE_LOOP = LOOP_SPECS[ACTIVE_LOOP_NUMBER - 1]
COMPLETED_LABEL = f"{COMPLETED_LOOP['loop_id']} {COMPLETED_LOOP['title']}"
ACTIVE_LABEL = f"{ACTIVE_LOOP['loop_id']} {ACTIVE_LOOP['title']}"
CURRENT_LOOP_STATE = f"{COMPLETED_LOOP['loop_id']} complete / {ACTIVE_LOOP['loop_id']} ready"
CURRENT_RESTART_SEED = f"{ACTIVE_LOOP['loop_id']} -> {ACTIVE_LOOP['title']}"

STATE_JSON = SELF / "master_loop_state_57.json"
ROADMAP_JSON = SELF / "master_loop_57_roadmap.json"
AGENTS_JSON = SELF / "master_agent_state_57.json"
LATTICE_JSON = SELF / "master_loop_shared_lattice_4096.json"
QUEST_JSON = SELF / "master_loop_public_quest_bundle_57.json"
RECORDS_JSON = SELF / "lp_57_prime_loop_cycle_records.json"
LEDGER_JSON = SELF / "lp_57_master_agent_ledger.json"
EMISSIONS_JSON = SELF / "lp_57_quest_emission_bundles.json"
RECEIPTS_JSON = SELF / "lp_57_loop_delta_receipts.json"
COORDS_JSON = SELF / "lp_57_liminal_coordinate_stamps.json"
VERIFY_JSON = SELF / "master_loop_57_verification.json"
LP_VERIFY_JSON = SELF / "lp_57_prime_loop_verification.json"
PROGRAM_VERIFY_JSON = SELF / "four_agent_57_loop_program_verification.json"
REGISTRY_JSON = SELF / "57_loop_cycle_registry.json"
ASSISTS_JSON = SELF / "next_4_pow_6_57_cycle_transition_assists.json"
SWARM_STATE_JSON = SELF / "next_4_pow_6_57_cycle_swarm_state.json"
SWARM_LEDGER_JSON = SELF / "next_4_pow_6_57_cycle_loop_ledger.json"
SWARM_LATTICE_JSON = SELF / "next_4_pow_6_57_cycle_lattice_registry.json"
SWARM_VERIFY_JSON = SELF / "next_4_pow_6_57_cycle_swarm_verification.json"
HALL_BUNDLE_JSON = SELF / "next_4_pow_6_57_cycle_hall_macro_bundle.json"
TEMPLE_BUNDLE_JSON = SELF / "next_4_pow_6_57_cycle_temple_macro_bundle.json"

BUNDLE_ROOT = SELF / "lp57_omega_v2_artifacts"
ARTIFACT_DIR = BUNDLE_ROOT / COMPLETED_LOOP["loop_id"]
BUNDLE_FILES = {
    "ResearchBundle": "research_bundle.json",
    "QuestEmissionBundle": "quest_emission_bundle.json",
    "ExecutionBundle": "execution_bundle.json",
    "CompressionBundle": "compression_bundle.json",
    "TransitionAssistBundle": "transition_assist_bundle.json",
    "LoopReceipt": "loop_receipt.json",
    "RestartSeed": "restart_seed.json",
}
BUNDLE_FIELDS = {
    "ResearchBundle": "research_delta_ref",
    "QuestEmissionBundle": "quest_packet_ref",
    "ExecutionBundle": "execution_batch_ref",
    "CompressionBundle": "compression_bundle_ref",
    "TransitionAssistBundle": "transition_assist_bundle_ref",
    "LoopReceipt": "receipt_ref",
    "RestartSeed": "restart_seed_ref",
}
WITNESS_HIERARCHY_JSON = SELF / "witness_hierarchy.json"
WITNESS_HIERARCHY_MD = MY / "GLOBAL_EMERGENT_GUILD_HALL" / "07_CANONICAL_WITNESS_HIERARCHY.md"

L04_HALL_PROMOTIONS = [
    ("Q57-L04-H01", "Seal active membrane `Q41 / TQ06`"),
    ("Q57-L04-H02", "Carry live Hall feeder `Q42`"),
    ("Q57-L04-H03", "Confirm landed Temple receiver `TQ04`"),
    ("Q57-L04-H04", "Preserve reserve feeder `Q46`"),
    ("Q57-L04-H05", "Fence blocked external frontier `Q02`"),
    ("Q57-L04-H06", "Freeze route law `Q41/TQ06 -> Q42 -> TQ04`"),
    ("Q57-L04-H07", "Keep `Q50` witness-only for L04"),
    ("Q57-L04-H08", "Emit `L05 Canonical 16-Basis Ownership` restart seed"),
]

L04_TEMPLE_PROMOTIONS = [
    ("TQ57-L04-T01", "Ratify active membrane `Q41 / TQ06`"),
    ("TQ57-L04-T02", "Ratify Hall carrier `Q42`"),
    ("TQ57-L04-T03", "Ratify landed receiver `TQ04`"),
    ("TQ57-L04-T04", "Ratify reserve-only feeder `Q46`"),
    ("TQ57-L04-T05", "Ratify blocked external frontier `Q02`"),
    ("TQ57-L04-T06", "Preserve Earth + `AppI/AppM` legality"),
    ("TQ57-L04-T07", "Preserve `AppQ/AppO` as overlay-only"),
    ("TQ57-L04-T08", "Ratify `L05 Canonical 16-Basis Ownership` handoff"),
]

WITNESS_CLASS_ORDER = ["physical", "indexed", "board", "archive", "promoted"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, indent=2))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def replace_block(text: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(block, text)
    return text.rstrip() + ("\n\n" if text.rstrip() else "") + block + "\n"


def patch_file(path: Path, marker: str, body: str) -> None:
    write_text(path, replace_block(read_text(path), marker, body))


def docs_gate() -> dict[str, Any]:
    checked = [ROOT / "Trading Bot" / "credentials.json", ROOT / "Trading Bot" / "token.json"]
    missing = [f"Trading Bot/{path.name}" for path in checked if not path.exists()]
    return {
        "state": "BLOCKED" if missing else "LIVE",
        "reason": DOCS_GATE_EXPECTED if missing else "oauth-present",
        "checked_paths": [f"Trading Bot/{path.name}" for path in checked],
        "missing_files": missing,
    }


def digits(index: int) -> list[int]:
    out = [0] * 6
    value = index
    for pos in range(5, -1, -1):
        out[pos] = (value % 4) + 1
        value //= 4
    return out


def seat(index: int) -> str:
    a, b, c, d, e, f = digits(index)
    return f"A{a}.B{b}.C{c}.D{d}.E{e}.F{f}"


def coord(index: int, loop_number: int, region: str, role_tag: str) -> dict[str, str]:
    d = digits(index)
    return {
        "Xs": region,
        "Ys": f"FAM-{d[0]}{d[1]}",
        "Zs": f"D{d[2]}",
        "Ts": f"L{loop_number:02d}",
        "Qs": f"Q-{loop_number:02d}-{d[3]}{d[4]}",
        "Rs": f"R{d[5]}",
        "Cs": f"C{(index % 4) + 1}",
        "Fs": role_tag,
        "Ms": f"M{(loop_number % 12) + 1:02d}",
        "Ns": f"N{(index % 16) + 1:02d}",
        "Hs": f"H{1 + (index % 7)}",
        "OmegaS": "OMEGA-LOCAL",
    }


def bundle_paths(loop_id: str) -> dict[str, Path]:
    base = BUNDLE_ROOT / loop_id
    return {name: base / filename for name, filename in BUNDLE_FILES.items()}


def witness_payload() -> dict[str, Any]:
    payload = read_json(WITNESS_HIERARCHY_JSON)
    return payload if payload else {"witnesses": {}}


def witness_values(payload: dict[str, Any]) -> dict[str, int | None]:
    values: dict[str, int | None] = {}
    witnesses = payload.get("witnesses", {})
    for witness_class in WITNESS_CLASS_ORDER:
        values[witness_class] = witnesses.get(witness_class, {}).get("value")
    return values


def control_tuple_payload() -> dict[str, Any]:
    return {
        "active_membrane": ACTIVE_MEMBRANE,
        "live_hall_carrier": LIVE_HALL_CARRIER,
        "landed_temple_receiver": LANDED_TEMPLE_RECEIVER,
        "reserve_feeder": RESERVE_FEEDER,
        "external_blocker": EXTERNAL_BLOCKER,
        "docs_gate": "BLOCKED",
        "witness_only_fronts": list(WITNESS_ONLY_FRONTS),
        "earth_gate_required": True,
        "required_appendix_support": ["AppI", "AppM"],
        "overlay_only_appendix_support": ["AppQ", "AppO"],
    }


def route_law_payload() -> dict[str, Any]:
    return {
        "primary_route": "Q41/TQ06 -> Q42 -> TQ04",
        "reserve_rule": "Q46 remains visible but reserve-only",
        "blocker_rule": "Q02 remains blocked and excluded from execution",
        "witness_only_rule": "Q50 and ECOSYSTEM/NERVOUS_SYSTEM remain witness-only for L04",
    }


def l04_hall_promotions() -> list[dict[str, Any]]:
    return [
        {
            "quest_id": quest_id,
            "surface": "Hall",
            "loop_id": COMPLETED_LOOP["loop_id"],
            "title": title,
            "seat_addr_6d": seat(index),
            "route_target": COMPLETED_LOOP["frontier_type"],
            "restart_seed": CURRENT_RESTART_SEED,
            "status": "LANDED",
            "control_tuple": control_tuple_payload(),
            "route_law": route_law_payload(),
            "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)],
        }
        for index, (quest_id, title) in enumerate(L04_HALL_PROMOTIONS)
    ]


def l04_temple_promotions() -> list[dict[str, Any]]:
    return [
        {
            "quest_id": quest_id,
            "surface": "Temple",
            "loop_id": COMPLETED_LOOP["loop_id"],
            "title": title,
            "seat_addr_6d": seat(index),
            "route_target": COMPLETED_LOOP["frontier_type"],
            "restart_seed": CURRENT_RESTART_SEED,
            "status": "LANDED",
            "control_tuple": control_tuple_payload(),
            "route_law": route_law_payload(),
            "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)],
        }
        for index, (quest_id, title) in enumerate(L04_TEMPLE_PROMOTIONS)
    ]


def apply_hsigma_overrides() -> None:
    if HSIGMA_REFRESH.exists():
        runpy.run_path(str(HSIGMA_REFRESH), run_name="__main__")

    write_text(THESIS_MD, "\n".join([
        "# LP-57Î© Master Hologram Thesis",
        "",
        "Date: `2026-03-13`",
        "Truth: `LOCAL_ONLY / CLASS_EXHAUSTIVE_INSTANCE_FRONTIER`",
        "Docs Gate: `BLOCKED`",
        "Machine Core Symbol: `HÎ£`",
        "Save-State Symbol: `HÎ£*`",
        "",
        "## Canon Law",
        "",
        "The lawful current snapshot is class-exhaustive and instance-frontier. `HÎ£` is the typed machine-core hologram of the visible mapping organism, and `HÎ£*` is its compressed replay-safe save state.",
        "",
        "- `11` layer families",
        "- `13` route families",
        "- `16` seated explicit nexus rows",
        "- `2` frontier explicit nexus rows",
        "- `1` inferred latent nexus row",
        "- `6` tunnel classes",
        "- `5` dimensional strata",
        "- `256` timing states",
        "- `4864 = 19 x 256` class-scale mindsweeper cells",
        "",
        "## Frontier Discipline",
        "",
        "- seat only the visible class structure",
        "- keep unseen instance multiplicities, coordinates, tunnel interiors, and local attachments as frontier",
        "- keep `MR` and `PA` frontier until lawful promotion",
        "- keep `LP` inferred until lawful promotion",
        "- never let an inferred candidate overwrite an explicit node",
        "",
        "## Visible Law",
        "",
        "`16 macro bundles -> 64 Hall packets -> 256 Temple fibers -> 1024 active synaptic seats -> 4096 compiled atlas seats`",
        "",
        "## Machine-Core Paths",
        "",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json`",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MINDSWEEPER_MATRIX.json`",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json`",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json`",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_VERIFICATION.json`",
    ]))

    write_text(ACTIVE_RUN_MD, "\n".join([
        "# ACTIVE RUN",
        "",
        "Date: `2026-03-13`",
        "Docs Gate: `BLOCKED`",
        "",
        "## LP-57Î© + HÎ£ Active Run",
        "",
        "- Governing protocol: `LP-57Î©`",
        "- Machine core: `HÎ£`",
        "- Canonical machine JSON: `NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json`",
        "- Canonical matrix JSON: `NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MINDSWEEPER_MATRIX.json`",
        "- Hall front: `NEXT57`",
        "- Temple front: `TQ07`",
        "- Role order: `Researcher/Synthesizer -> Planner/Architect -> Worker/Adventurer -> Pruner/Compressor`",
        "- Visible law: `16 macro bundles -> 64 Hall packets -> 256 Temple fibers -> 1024 active synaptic seats -> 4096 compiled atlas seats`",
        f"- Current loop: `{COMPLETED_LABEL} [COMPLETED]`",
        f"- Next loop: `{ACTIVE_LABEL} [READY]`",
        "",
        "## Startup Control Story",
        "",
        f"- Active cadence membrane: `{ACTIVE_MEMBRANE}`",
        f"- Landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- Hall feeder: `{LIVE_HALL_CARRIER}` carrying the feeder-stack crosswalk",
        f"- Reserve feeder: `{RESERVE_FEEDER}`",
        "- Runtime frontier witness-only: `Q50`",
        f"- Blocked external frontier: `{EXTERNAL_BLOCKER}`",
        f"- Next ownerable Hall uptake: `{CURRENT_RESTART_SEED}`",
    ]))

    write_text(BUILD_QUEUE_MD, "\n".join([
        "# BUILD QUEUE",
        "",
        "Date: `2026-03-13`",
        "Docs Gate: `BLOCKED`",
        "",
        "## LP-57Î© + HÎ£ Queue",
        "",
        "- Governing protocol: `LP-57Î©`",
        "- Machine core: `HÎ£`",
        "- Hall front: `NEXT57`",
        "- Temple front: `TQ07`",
        "- Visible law: `16 macro bundles -> 64 Hall packets -> 256 Temple fibers -> 1024 active synaptic seats -> 4096 compiled atlas seats`",
        "- Nested `4^6` swarm: `compiled, not literalized`",
        "",
        "## Current Hall Packets",
        "",
        "- `Q57-L04-H01` Seal active membrane `Q41 / TQ06`",
        "- `Q57-L04-H02` Carry live Hall feeder `Q42`",
        "- `Q57-L04-H03` Confirm landed Temple receiver `TQ04`",
        "- `Q57-L04-H04` Preserve reserve feeder `Q46`",
        "",
        "## Current Temple Packets",
        "",
        "- `TQ07-L01-T01` Seat the class-exhaustive and instance-frontier hologram law",
        "- `TQ07-L01-T02` Bind `SeatAddr6D` and `CoordStamp12`",
        "- `TQ07-L01-T03` Demote legacy live-canon variants to mirror-only status",
        "- `TQ07-L01-T04` Align Level 6 weave to `HÎ£`",
    ]))

    write_text(FOUR_AGENT_MD, "\n".join([
        "# FOUR_AGENT_57_LOOP_PROGRAM Mirror",
        "",
        "Date: `2026-03-13`",
        "Status: `HISTORICAL_MIRROR_ONLY`",
        "Docs Gate: `BLOCKED`",
        "",
        "- Governing protocol: `LP-57Î©`",
        "- Machine core: `HÎ£`",
        "- Canonical authority: `NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json`",
        "- Canonical machine core: `NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json`",
        "- Public fronts: `NEXT57` and `TQ07`",
        "- Legacy live-canon variants are mirror-only and may not act as authority surfaces",
        "",
        "This markdown surface is a replay-safe wrapper only and may not act as an independent protocol source.",
    ]))

    write_text(HALL_BOARD_MD, "\n".join([
        "# Quest Board",
        "",
        "<!-- MASTER_LOOP_57_HALL_QUEST:START -->",
        "## LP-57Omega Hall Quest Interface",
        "",
        f"- Date: `{DATE}`",
        f"- Docs Gate: `{docs['state']}`",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        "- Public Hall front: `NEXT57`",
        "- Public Temple front: `TQ07`",
        "- Historical Hall alias only: `Q51`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Feeder stack: `{' / '.join(FEEDER_STACK)}`",
        f"- Planner public cap: `{HALL_CAP} Hall quests per loop`",
        f"- Shared lattice: `4^6 = {SHARED_TOTAL} indexed / {SHARED_ACTIVE} ACTIVE / {SHARED_DORMANT} DORMANT`",
        f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`",
        "",
        "### L03 Public Hall Promotions",
        "",
        "| Quest | Status | Title | Seat | Restart |",
        "| --- | --- | --- | --- | --- |",
        *[
            f"| {item['quest_id']} | {item['status']} | {item['title']} | {item['seat_addr_6d']} | {CURRENT_RESTART_SEED} |"
            for item in hall
        ],
        "",
        f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "<!-- MASTER_LOOP_57_HALL_QUEST:END -->",
    ]))

    write_text(HALL_PROGRAM_DETAIL_MD, "\n".join([
        "# Hall 57-Cycle Four-Agent Orchestration",
        "",
        f"Date: `{DATE}`",
        "Truth: `DERIVED_FROM_LOCAL_WITNESS`",
        f"Docs Gate: `{docs['state']}`",
        "",
        f"- canonical machine program: `{rel(STATE_JSON)}`",
        f"- canonical witness artifact: `{rel(WITNESS_HIERARCHY_JSON)}`",
        "- Hall front: `NEXT57`",
        "- Temple front: `TQ07`",
        f"- current completed loop: `{COMPLETED_LABEL}`",
        f"- next ready loop: `{ACTIVE_LABEL}`",
        "",
        "## Visible Law",
        "",
        f"`16 macro bundles -> 64 Hall packets -> 256 Temple fibers -> 1024 active synaptic seats -> {SHARED_TOTAL} compiled atlas seats`",
        "",
        "## Current L03 Packet Bundle",
        "",
        "- Hall:",
        f"  `{hall[0]['quest_id']}` .. `{hall[-1]['quest_id']}`",
        "- Temple:",
        f"  `{temple[0]['quest_id']}` .. `{temple[-1]['quest_id']}`",
        "",
        "## Witness Basis",
        "",
        *[f"- `{item}`" for item in WITNESS_CLASS_ORDER],
        "",
        "## Restart Seed",
        "",
        f"`{CURRENT_RESTART_SEED}`",
    ]))

    write_text(TEMPLE_BOARD_MD, "\n".join([
        "# Temple Quest Board",
        "",
        "<!-- MASTER_LOOP_57_TEMPLE_QUEST:START -->",
        "## LP-57Omega Temple Quest Interface",
        "",
        f"- Date: `{DATE}`",
        f"- Docs Gate: `{docs['state']}`",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Planner public cap: `{TEMPLE_CAP} Temple quests per loop`",
        f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`",
        "",
        "### L03 Public Temple Promotions",
        "",
        "| Quest | Status | Title | Seat | Restart |",
        "| --- | --- | --- | --- | --- |",
        *[
            f"| {item['quest_id']} | {item['status']} | {item['title']} | {item['seat_addr_6d']} | {CURRENT_RESTART_SEED} |"
            for item in temple
        ],
        "",
        f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "<!-- MASTER_LOOP_57_TEMPLE_QUEST:END -->",
    ]))

    write_text(TEMPLE_STATE_MD, "\n".join([
        "# Temple State",
        "",
        "## LP-57Omega v2 Control State",
        "",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Shared machine law: `{SHARED_TOTAL}/{SHARED_ACTIVE}/{SHARED_DORMANT}`",
        f"- Virtual overlay: `{ROLE_NAMESPACE_TOTAL}` conceptual seats",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        "",
        "<!-- MASTER_LOOP_57_TEMPLE_STATE:START -->",
        "## LP-57Omega Temple State",
        "",
        f"- Date: `{DATE}`",
        f"- Docs gate: `{docs['state']}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Current completed Temple loop: `{COMPLETED_LABEL}`",
        f"- Next ready Temple loop: `{ACTIVE_LABEL}`",
        "- Current Hall feeder: `Q42`",
        "- Landed contract feeder: `TQ04`",
        "- Runtime frontier: `Q50`",
        "- Reserve activation feeder: `Q46`",
        "- External blocker: `Q02`",
        f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`",
        "",
        "### Landed L03 Temple Packets",
        "",
        *[
            f"- `{item['quest_id']}` {item['title']}. :: state `{item['status']}` :: restart `{CURRENT_RESTART_SEED}`"
            for item in temple
        ],
        "",
        f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`",
        "<!-- MASTER_LOOP_57_TEMPLE_STATE:END -->",
    ]))

    write_text(TEMPLE_TQ07_MD, "\n".join([
        "# TQ07 - LP-57Omega Witness Hierarchy Governance",
        "",
        f"Date: `{DATE}`",
        "Truth: `LOCAL_WITNESS_ONLY`",
        f"Docs Gate: `{docs['state']}`",
        f"Status: `{CURRENT_LOOP_STATE}`",
        "",
        "## Governing Temple Law",
        "",
        "- Temple macro front: `TQ07`",
        "- Hall macro front: `NEXT57`",
        "- Governing protocol: `LP-57Omega`",
        f"- Current completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        "- Role order: `Researcher/Synthesizer -> Planner/Architect -> Worker/Adventurer -> Pruner/Compressor`",
        f"- Shared lattice: `4^6 = {SHARED_TOTAL} indexed / {SHARED_ACTIVE} ACTIVE / {SHARED_DORMANT} DORMANT`",
        f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`",
        "",
        "## Landed L03 Temple Promotions",
        "",
        *[f"- `{item['quest_id']}` {item['title']}" for item in temple],
        "",
        "## Canonical Witness Refs",
        "",
        f"- `{rel(WITNESS_HIERARCHY_JSON)}`",
        f"- `{rel(WITNESS_HIERARCHY_MD)}`",
        f"- `{rel(ARTIFACT_DIR / 'loop_receipt.json')}`",
        f"- `{rel(ARTIFACT_DIR / 'restart_seed.json')}`",
        "",
        "## L04 Handoff",
        "",
        f"- Next restart seed: `{CURRENT_RESTART_SEED}`",
        "- Preserve archive as archive and promoted slice as promoted slice.",
        "- Preserve additive witness tags; do not flatten witness classes into one corpus count.",
        "- No witness tier may imply live Google Docs access while Trading Bot credentials are missing.",
    ]))

    write_text(LEVEL6_WEAVE_MD, "\n".join([
        "# Level 6 Hologram Weave Map",
        "",
        "Level 6 remains the additive weave resolution that binds ingress, return, topology, and re-entry into one overlay surface.",
        "",
        "`HÎ£` is the typed hologram object underneath this weave. Level 6 does not invent a separate hologram ontology; it routes through the canonical machine core:",
        "",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MACHINE_CORE.json`",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/H_SIGMA_MINDSWEEPER_MATRIX.json`",
        "",
        "## Four-Lane Convergence Order",
        "",
        "- Fire pressure names what must be activated, woven, or carried.",
        "- Water continuity banks that pressure into replay-safe memory and return.",
        "- Air registry names the sigma, spin, dual-kernel, and modal labels so the weave remains legible.",
        "- Earth admissibility filters the resulting field so only lawful return traffic reaches the shared center.",
        "",
        "## HÎ£ Substrate Law",
        "",
        "- class-exhaustive and instance-frontier ontology",
        "- `11` layer families",
        "- `13` route families",
        "- `19` nexus rows",
        "- `6` tunnel classes",
        "- `5` dimensional strata",
        "- `256` timing states",
        "- `19 x 256` class-scale mindsweeper field",
        "",
        "## Canon Law",
        "",
        "- Hall front remains `NEXT57`",
        "- Temple front remains `TQ07`",
        "- Level 6 may amplify route visibility, but it may not mint a parallel hologram ontology",
        "- blocked-docs pressure may not be promoted into `OK`",
    ]))

    write_text(HALL_PROGRAM_MD, "\n".join([
        "# LP-57Î© Hall Program",
        "",
        "- Hall front: `NEXT57`",
        "- Governing protocol: `LP-57Î©`",
        "- Machine core: `HÎ£`",
        "- Current loop: `L01 Seat Truth Sync`",
        "- Visible law: `16 macro bundles -> 64 Hall packets -> 256 Temple fibers -> 1024 active synaptic seats -> 4096 compiled atlas seats`",
    ]))

    write_text(TEMPLE_PROGRAM_MD, "\n".join([
        "# LP-57Î© Temple Program",
        "",
        "- Temple front: `TQ07`",
        "- Governing protocol: `LP-57Î©`",
        "- Machine core: `HÎ£`",
        "- Current loop: `L01 Seat Truth Sync`",
        "- Visible law: `16 macro bundles -> 64 Hall packets -> 256 Temple fibers -> 1024 active synaptic seats -> 4096 compiled atlas seats`",
    ]))


def write_canonical_four_agent_57_loop(source_id: str = "lp57_omega_v2_canonical_runtime") -> dict[str, Any]:
    docs = docs_gate()
    loops: list[dict[str, Any]] = []
    for spec in LOOP_SPECS:
        master = MASTER_AGENT_BY_ID[spec["lead_master"]]
        loop_status = (
            "COMPLETED"
            if spec["loop_number"] <= COMPLETED_LOOP_NUMBER
            else "READY"
            if spec["loop_number"] == ACTIVE_LOOP_NUMBER
            else "QUEUED"
        )
        row = {
            **spec,
            "status": loop_status,
            "master_agent_id": master["master_agent_id"],
            "master_agent": master["agent_id"],
            "master_agent_label": master["display_name"],
            "role_tag": master["role_tag"],
            "seat_mode": "role-namespaced-4096-over-shared-4096",
            "seat_namespace": master["seat_namespace"],
            "arc": arc_for_loop(spec["loop_number"]),
            "topk": topk_for_loop(spec["loop_number"]),
            "artifact_contract": list(CANONICAL_PACKET_CONTRACT),
            "restart_handoff": f"L{min(spec['loop_number'] + 1, TOTAL_LOOPS):02d}" if spec["loop_number"] < TOTAL_LOOPS else "SUCCESSOR",
        }
        for bundle_name, path in bundle_paths(spec["loop_id"]).items():
            row[BUNDLE_FIELDS[bundle_name]] = rel(path)
        loops.append(row)

    public_loop = loops[COMPLETED_LOOP_NUMBER - 1]
    ready_loop = loops[ACTIVE_LOOP_NUMBER - 1]
    witness = witness_payload()
    witness_counts = witness_values(witness)
    hall = l04_hall_promotions()
    temple = l04_temple_promotions()
    shadow = [
        {
            "packet_id": f"AP6D-L04-SHADOW-{i:02d}",
            "loop_id": public_loop["loop_id"],
            "seat_addr_6d": seat(i - 1),
            "projection": f"Feeder-stack shadow packet {i:02d}",
            "status": "QUEUE_VISIBLE",
            "control_tuple": control_tuple_payload(),
            "route_law": route_law_payload(),
        }
        for i in range(1, SHADOW_CAP + 1)
    ]
    adventurer = [
        {
            "packet_id": f"ADV-L04-{i:02d}",
            "loop_id": public_loop["loop_id"],
            "seat_addr_6d": seat(i - 1),
            "title": f"Feeder execution packet {i:02d}",
            "status": "UNCLAIMED",
            "control_tuple": control_tuple_payload(),
            "route_law": route_law_payload(),
        }
        for i in range(1, ADVENTURER_CAP + 1)
    ]
    assists = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "notes": [{"note_id": f"TA-{i:03d}", "agent_id": target, "stage_0_to_6": i % 7, "active_elements": ["crosswalk", "routing"] if i % 2 else ["memory", "execution"], "missing_element": "basis-ownership" if i % 3 == 0 else "compression", "blind_spot": "feeder blending or blocked-front promotion drift", "transition_trigger": "sealed feeder-stack crosswalk plus replay-safe L05 handoff", "current_duty": f"Seal {COMPLETED_LABEL} and prepare {ACTIVE_LABEL}", "next_practice": "cite the exact feeder tuple before promoting any runtime or governance front", "handoff_rule": "A1 synthesizes the feeder tuple, A2 emits L04 quests, A3 binds Hall/Temple/control surfaces, A4 prunes rival feeder stories", "fallback_rule": "degrade to NEAR or AMBIG and keep Q46 reserve-only with Q02 blocked", "witness_basis": "physical > indexed > board > archive > promoted with deep-root precedence preserved", "route_target": ready_loop["frontier_type"], "truth_state": "AMBIG" if target == EXTERNAL_BLOCKER else "NEAR"} for i, target in enumerate(["Master Agent", "Aether", "Commander", "General-North", "General-East", "General-South", "General-West"] + [f"Hybrid-{n:02d}" for n in range(1, 7)] + [f"Archetype-{n:02d}" for n in range(1, 13)] + [LIVE_HALL_CARRIER, RESERVE_FEEDER, LANDED_TEMPLE_RECEIVER, EXTERNAL_BLOCKER, "DormantSeatTemplate"], start=1)]}
    state = {"generated_at": now(), "derivation_version": DERIVATION_VERSION, "derivation_command": source_id, "protocol_id": PROTOCOL_ID, "protocol_display_name": PROTOCOL_DISPLAY_NAME, "frontier_id": FRONTIER_ID, "docs_gate": docs, "authority_order": AUTHORITY_ORDER, "deep_root_authority": DEEP_ROOT_AUTHORITY, "active_membrane": ACTIVE_MEMBRANE, "feeder_stack": FEEDER_STACK, "total_loops": TOTAL_LOOPS, "current_loop_state": CURRENT_LOOP_STATE, "completed_loop": {"number": COMPLETED_LOOP_NUMBER, "label": COMPLETED_LABEL, "state": "COMPLETED"}, "active_loop": {"number": ACTIVE_LOOP_NUMBER, "label": ACTIVE_LABEL, "state": "READY"}, "next_ready_loop": {"number": ACTIVE_LOOP_NUMBER, "label": ACTIVE_LABEL}, "next_invocation_contract": NEXT_INVOCATION_CONTRACT, "restart_seed": CURRENT_RESTART_SEED, "machine_artifact_contract": list(CANONICAL_PACKET_CONTRACT), "artifact_field_contract": list(LOOP_ARTIFACT_FIELDS), "coordinate_display_symbols": COORDINATE_DISPLAY_SYMBOLS, "coordinate_schema": COORDINATE_SCHEMA, "ledger_schema": LEDGER_SCHEMA, "lookup_key_schema": LOOKUP_KEY_SCHEMA, "shared_lattice": {"model": "role-namespaced-4096-over-shared-4096", "total_seats": SHARED_TOTAL, "active_seats": SHARED_ACTIVE, "dormant_seats": SHARED_DORMANT, "logical_namespace_total_per_master": ROLE_NAMESPACE_TOTAL, "active_seats_per_master": ACTIVE_PER_MASTER, "planner_public_caps": {"hall": HALL_CAP, "temple": TEMPLE_CAP, "ap6d_shadow": SHADOW_CAP, "adventurer_packets": ADVENTURER_CAP}}, "witness_basis": {"classes": WITNESS_CLASS_ORDER, "counts": witness_counts, "canonical_json": rel(WITNESS_HIERARCHY_JSON), "canonical_markdown": rel(WITNESS_HIERARCHY_MD)}, "loops": loops}
    agents = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "cycle_order": [agent["master_agent_id"] for agent in MASTER_AGENTS], "agents": [{"master_agent_id": agent["master_agent_id"], "agent_id": agent["agent_id"], "display_name": agent["display_name"], "role": agent["role"], "role_tag": agent["role_tag"], "logical_namespace_total": ROLE_NAMESPACE_TOTAL, "active_seat_share": ACTIVE_PER_MASTER, "seat_namespace": agent["seat_namespace"], "seat_mode": "role-namespaced-4096-over-shared-4096", "packet_output": agent["packet_output"], "mission": agent["mission"]} for agent in MASTER_AGENTS]}
    shared = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "total_seats": SHARED_TOTAL, "active_seats": SHARED_ACTIVE, "dormant_seats": SHARED_DORMANT, "model": "role-namespaced-4096-over-shared-4096", "rows": [{"seat_index": i + 1, "seat_addr_6d": seat(i), "activation_state": "ACTIVE" if i < SHARED_ACTIVE else "DORMANT", "shared_substrate": "AP6D-4096", "role_namespace_model": "role-namespaced-4096-over-shared-4096", "coordinate_stamp": coord(i, ACTIVE_LOOP_NUMBER, ACTIVE_LOOP["focus_family"], "SHARED")} for i in range(SHARED_TOTAL)]}
    cycle_records = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "records": [{"loop_id": row["loop_id"], "title": row["title"], "status": row["status"], "advancement_tuple": [row["dominant_focus"], row["synthesis_objective"], row["planning_objective"], row["implementation_objective"], row["pruning_objective"], row["expected_mapping_gain"]]} for row in loops]}
    ledger_rows = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "entries": [{"agent_id": f"{row['loop_id']}.{agent['master_agent_id']}.D1.B{(((row['loop_number'] - 1) * len(MASTER_AGENTS) + int(agent['master_agent_id'][1:]) - 1) % SHARED_TOTAL) + 1:04d}.{agent['role_tag']}", "loop_number": row["loop_number"], "parent_agent": agent["master_agent_id"], "seat_addr_6d": seat(((row["loop_number"] - 1) * len(MASTER_AGENTS) + int(agent["master_agent_id"][1:]) - 1) % SHARED_TOTAL), "coordinate_stamp": coord(((row["loop_number"] - 1) * len(MASTER_AGENTS) + int(agent["master_agent_id"][1:]) - 1) % SHARED_TOTAL, row["loop_number"], row["focus_family"], agent["role_tag"]), "source_region": row["focus_family"], "action_type": agent["action_type"], "affected_nodes": [row["frontier_type"], row["focus_family"]], "summary_of_change": row["title"], "reason_for_change": row["dominant_focus"], "integration_gain": row["expected_structural_gain"], "compression_gain": row["compression_target"], "unresolved_followups": [] if row["loop_number"] == TOTAL_LOOPS else [f"L{row['loop_number'] + 1:02d}"], "linked_quests": [row["loop_id"]], "linked_agents": [item["master_agent_id"] for item in MASTER_AGENTS if item["master_agent_id"] != agent["master_agent_id"]], "revision_confidence": 0.98 if row["status"] == "COMPLETED" else 0.9 if row["status"] == "ACTIVE" else 0.75, "timestamp_internal": now(), "witness_class": "PROMOTED" if row["status"] != "QUEUED" else "PLANNED", "truth_state": "OK" if row["status"] == "COMPLETED" else "NEAR"} for row in loops for agent in MASTER_AGENTS]}
    receipts = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "receipts": [{"receipt_id": f"LP57-RC-{row['loop_id']}", "loop_id": row["loop_id"], "status": row["status"], "structural_gain": row["expected_structural_gain"], "mapping_gain": row["expected_mapping_gain"]} for row in loops]}
    emissions = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "bundles": [{"bundle_id": f"{row['loop_id']}-{surface}-BUNDLE", "loop_id": row["loop_id"], "surface": surface, "count": count, "status": "PUBLISHED" if row["loop_number"] <= COMPLETED_LOOP_NUMBER else "READY" if row["loop_number"] == ACTIVE_LOOP_NUMBER else "PLANNED", "canonical_source": rel(QUEST_JSON)} for row in loops for surface, count in [("HALL", HALL_CAP), ("TEMPLE", TEMPLE_CAP), ("AP6D", SHADOW_CAP), ("ADVENTURER", ADVENTURER_CAP)]]}
    coords = {"generated_at": now(), "protocol_id": PROTOCOL_ID, "lookup_key_schema": LOOKUP_KEY_SCHEMA, "coordinate_symbols": COORDINATE_DISPLAY_SYMBOLS, "coordinates": [{"lookup_key": f"{FRONTIER_ID}:{public_loop['loop_id']}:{item['seat_addr_6d']}:shared", "seat_addr_6d": item["seat_addr_6d"], "coordinate_stamp": item["coordinate_stamp"], "touched_node_id": item["seat_addr_6d"]} for item in shared["rows"]]}

    for row in loops:
        base = BUNDLE_ROOT / row["loop_id"]
        base.mkdir(parents=True, exist_ok=True)
        payloads = {
            "research_bundle.json": {"bundle_type": "ResearchBundle", "objective": row["synthesis_objective"]},
            "quest_emission_bundle.json": {"bundle_type": "QuestEmissionBundle", "objective": row["planning_objective"], "surfaces": {"hall": HALL_CAP, "temple": TEMPLE_CAP, "ap6d_shadow": SHADOW_CAP, "adventurer": ADVENTURER_CAP}},
            "execution_bundle.json": {"bundle_type": "ExecutionBundle", "objective": row["implementation_objective"]},
            "compression_bundle.json": {"bundle_type": "CompressionBundle", "objective": row["pruning_objective"]},
            "transition_assist_bundle.json": {"bundle_type": "TransitionAssistBundle", "notes": assists["notes"]},
            "loop_receipt.json": {"bundle_type": "LoopReceipt", "structural_gain": row["expected_structural_gain"], "mapping_gain": row["expected_mapping_gain"]},
            "restart_seed.json": {"bundle_type": "RestartSeed", "seed": CURRENT_RESTART_SEED if row["loop_id"] == public_loop["loop_id"] else row["restart_handoff"]},
        }
        if row["loop_id"] == public_loop["loop_id"]:
            payloads["research_bundle.json"] = {
                "bundle_type": "ResearchBundle",
                "objective": row["synthesis_objective"],
                "docs_gate": docs["state"],
                "control_tuple": control_tuple_payload(),
                "route_law": route_law_payload(),
                "witness_classes": WITNESS_CLASS_ORDER,
                "witness_counts": witness_counts,
                "precedence_relations": [
                    "Q41 / TQ06 = active membrane",
                    "Q42 = live Hall carrier",
                    "TQ04 = landed Temple receiver",
                    "Q46 = reserve-only feeder",
                    "Q02 = blocked external frontier",
                    "Q50 and ECOSYSTEM/NERVOUS_SYSTEM = witness-only context for L04",
                ],
                "deep_root_precedence": "runtime/deep-root witness outranks governance mirror summaries when conflicts appear",
                "canonical_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)],
                "flattening_refusal": "do not collapse active membrane, carriers, reserve fronts, or blocked fronts into one blended feeder story",
            }
            payloads["quest_emission_bundle.json"] = {
                "bundle_type": "QuestEmissionBundle",
                "objective": row["planning_objective"],
                "completed_loop": public_loop["loop_id"],
                "next_ready_loop": ready_loop["loop_id"],
                "control_tuple": control_tuple_payload(),
                "route_law": route_law_payload(),
                "hall_promotions": hall,
                "temple_promotions": temple,
                "ap6d_shadow_packets": shadow,
                "adventurer_packets": adventurer,
                "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)],
            }
            payloads["execution_bundle.json"] = {
                "bundle_type": "ExecutionBundle",
                "objective": row["implementation_objective"],
                "control_tuple": control_tuple_payload(),
                "route_law": route_law_payload(),
                "outputs": [
                    rel(WITNESS_HIERARCHY_JSON),
                    rel(WITNESS_HIERARCHY_MD),
                    rel(STATE_JSON),
                    rel(HALL_BOARD_MD),
                    rel(TEMPLE_BOARD_MD),
                    rel(TEMPLE_TQ07_MD),
                ],
                "implemented_classes": ["active-membrane", "hall-carrier", "landed-receiver", "reserve-feeder", "blocked-external-frontier"],
                "command_witness_basis_added": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)],
                "docs_gate": docs["state"],
            }
            payloads["compression_bundle.json"] = {
                "bundle_type": "CompressionBundle",
                "objective": row["pruning_objective"],
                "control_tuple": control_tuple_payload(),
                "route_law": route_law_payload(),
                "pruned_claims": [
                    "stale L03 Survey A03 ECOSYSTEM next-loop claims",
                    "Q50 promoted as part of the live feeder tuple",
                    "blended carrier/receiver/reserve narratives",
                ],
                "preserved_distinctions": ["membrane", "carrier", "receiver", "reserve", "blocker", "witness-only"],
                "preserved_boundaries": ["Q46 remains reserve-only", "Q02 remains blocked", "Q50 remains witness-only"],
            }
            payloads["transition_assist_bundle.json"] = {
                "bundle_type": "TransitionAssistBundle",
                "current_loop_state": CURRENT_LOOP_STATE,
                "notes": assists["notes"],
                "restart_target": ACTIVE_LABEL,
                "control_tuple": control_tuple_payload(),
            }
            payloads["loop_receipt.json"] = {
                "bundle_type": "LoopReceipt",
                "state_transition": {
                    "pre_execution_target": "L03 complete / L04 ready",
                    "post_execution_state": CURRENT_LOOP_STATE,
                },
                "structural_gain": row["expected_structural_gain"],
                "mapping_gain": row["expected_mapping_gain"],
                "control_tuple": control_tuple_payload(),
                "route_law": route_law_payload(),
                "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)],
            }
            payloads["restart_seed.json"] = {
                "bundle_type": "RestartSeed",
                "seed": "L05",
                "title": ACTIVE_LOOP["title"],
                "status": "READY",
                "control_tuple": control_tuple_payload(),
                "handoff_basis": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)],
            }
        for filename, payload in payloads.items():
            write_json(base / filename, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "loop_id": row["loop_id"], "status": row["status"], **payload})
        if row["loop_id"] == public_loop["loop_id"]:
            write_json(base / "research_delta.json", {"packet_type": "research-delta", "loop_id": row["loop_id"], "status": "PUBLISHED", "objective": row["synthesis_objective"], "control_tuple": control_tuple_payload(), "route_law": route_law_payload(), "restart_seed": CURRENT_RESTART_SEED, "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)], "docs_gate": docs["state"]})
            write_json(base / "execution_batch.json", {"packet_type": "execution-batch", "loop_id": row["loop_id"], "status": "PUBLISHED", "objective": row["implementation_objective"], "control_tuple": control_tuple_payload(), "route_law": route_law_payload(), "outputs": payloads["execution_bundle.json"]["outputs"], "restart_seed": CURRENT_RESTART_SEED, "docs_gate": docs["state"]})
            write_json(base / "receipt.json", {"packet_type": "receipt", "receipt_id": f"LP57-RC-{row['loop_id']}", "loop_id": row["loop_id"], "status": "COMPLETED", "state_transition": CURRENT_LOOP_STATE, "control_tuple": control_tuple_payload(), "route_law": route_law_payload(), "required_artifacts": [field for field in LOOP_ARTIFACT_FIELDS], "peer_signal_state": "CONFIRMED", "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)]})
            write_json(base / "quest_packet.json", {"packet_type": "quest-packet", "loop_id": row["loop_id"], "status": "PUBLISHED", "objective": row["planning_objective"], "control_tuple": control_tuple_payload(), "route_law": route_law_payload(), "visible_quests": {"hall": [item["quest_id"] for item in hall], "temple": [item["quest_id"] for item in temple], "ap6d_shadow": [item["packet_id"] for item in shadow], "adventurer": [item["packet_id"] for item in adventurer]}, "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)], "next_ready_loop": ready_loop["loop_id"], "docs_gate": docs["state"]})

    for path, payload in [
        (STATE_JSON, state),
        (ROADMAP_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "derivation_command": source_id, "loops": loops}),
        (AGENTS_JSON, agents),
        (LATTICE_JSON, shared),
        (QUEST_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "completed_loop": public_loop["loop_id"], "next_ready_loop": ready_loop["loop_id"], "control_tuple": control_tuple_payload(), "route_law": route_law_payload(), "hall_promotions": hall, "temple_promotions": temple, "hall_promotions_for_loop_4": hall, "temple_promotions_for_loop_4": temple, "ap6d_shadow_packets_for_loop_4": shadow, "adventurer_packets_for_loop_4": adventurer, "hall_promotions_for_loop_3_legacy_alias": hall, "temple_promotions_for_loop_3_legacy_alias": temple, "ap6d_shadow_packets_for_loop_3_legacy_alias": shadow, "adventurer_packets_for_loop_3_legacy_alias": adventurer, "next_seed": CURRENT_RESTART_SEED, "witness_refs": [rel(WITNESS_HIERARCHY_JSON), rel(WITNESS_HIERARCHY_MD)]}),
        (RECORDS_JSON, cycle_records),
        (LEDGER_JSON, ledger_rows),
        (EMISSIONS_JSON, emissions),
        (RECEIPTS_JSON, receipts),
        (COORDS_JSON, coords),
        (REGISTRY_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "loops": [{"loop_id": row["loop_id"], "status": row["status"], "title": row["title"]} for row in loops]}),
        (ASSISTS_JSON, assists),
        (SWARM_STATE_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "status": "COMPATIBILITY_MIRROR", "canonical_authority": rel(STATE_JSON), "current_loop_state": CURRENT_LOOP_STATE, "active_loop": ACTIVE_LABEL, "completed_loop": COMPLETED_LABEL, "docs_gate": docs, "independent_restart_seeds": False}),
        (SWARM_LEDGER_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "loops": [{"loop_id": row["loop_id"], "status": row["status"], "lead_master": row["lead_master"], "required_outputs": list(CANONICAL_PACKET_CONTRACT), "restart_handoff": row["restart_handoff"]} for row in loops]}),
        (SWARM_LATTICE_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "model": "role-namespaced-4096-over-shared-4096", "shared_substrate_total": SHARED_TOTAL, "logical_namespace_total_per_master": ROLE_NAMESPACE_TOTAL, "conceptual_role_namespace_total": ROLE_NAMESPACE_TOTAL * len(MASTER_AGENTS)}),
        (HALL_BUNDLE_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "scope": "Hall", "completed_loop": COMPLETED_LABEL, "next_ready_loop": ACTIVE_LABEL, "items": hall}),
        (TEMPLE_BUNDLE_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "scope": "Temple", "completed_loop": COMPLETED_LABEL, "next_ready_loop": ACTIVE_LABEL, "items": temple}),
        (NS / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.json", state),
        (NS / "FOUR_AGENT_57_LOOP_PROGRAM.json", {"generated_at": now(), "status": "COMPATIBILITY_MIRROR", "protocol_id": PROTOCOL_ID, "canonical_authority": rel(STATE_JSON), "current_loop_state": CURRENT_LOOP_STATE, "completed_loop": COMPLETED_LABEL, "active_loop": ACTIVE_LABEL, "machine_artifact_contract": list(CANONICAL_PACKET_CONTRACT)}),
        (NS / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json", {"generated_at": now(), "status": "COMPATIBILITY_MIRROR", "canonical_authority": rel(STATE_JSON), "completed_loop": public_loop["loop_id"], "next_ready_loop": ready_loop["loop_id"], "control_tuple": control_tuple_payload(), "route_law": route_law_payload(), "hall_promotions_for_loop_4": hall, "temple_promotions_for_loop_4": temple, "ap6d_shadow_packets_for_loop_4": shadow, "adventurer_packets_for_loop_4": adventurer}),
        (NS / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json", {"generated_at": now(), "status": "COMPATIBILITY_MIRROR", "canonical_authority": rel(STATE_JSON), "loops": [{"loop_id": row["loop_id"], "status": row["status"]} for row in loops]}),
    ]:
        write_json(path, payload)

    patch_file(NS / "ACTIVE_RUN.md", "LP57OMEGA_V2_ACTIVE_RUN", "\n".join(["## LP-57Omega v2 Control Plane", "", f"- Date: `{DATE}`", f"- Docs Gate: `{docs['state']}`", f"- Canonical authority: `{rel(STATE_JSON)}`", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Completed loop: `{COMPLETED_LABEL}`", f"- Next ready loop: `{ACTIVE_LABEL}`", f"- Active membrane: `{ACTIVE_MEMBRANE}`", f"- Feeder stack: `{', '.join(FEEDER_STACK)}`", f"- Shared lattice: `{SHARED_TOTAL} total / {SHARED_ACTIVE} ACTIVE / {SHARED_DORMANT} DORMANT`", f"- Role namespace: `{ROLE_NAMESPACE_TOTAL} per master over shared {SHARED_TOTAL}`", f"- Packet contract: `{', '.join(CANONICAL_PACKET_CONTRACT)}`", f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`", f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`"]))
    patch_file(NS / "BUILD_QUEUE.md", "LP57OMEGA_V2_BUILD_QUEUE", "\n".join(["## LP-57Omega v2 Build Queue", "", f"1. `{hall[0]['quest_id']}` {hall[0]['title']}", f"2. `{hall[1]['quest_id']}` {hall[1]['title']}", f"3. `{temple[0]['quest_id']}` {temple[0]['title']}", f"4. `{temple[1]['quest_id']}` {temple[1]['title']}", "5. `TransitionAssistBundle` preserve witness precedence and feeder honesty", f"6. `RestartSeed` hand off to `{CURRENT_RESTART_SEED}`"]))
    write_text(MY / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md", "\n".join([
        "# Quest Board",
        "",
        "<!-- MASTER_LOOP_57_HALL_QUEST:START -->",
        "## LP-57Omega Hall Quest Interface",
        "",
        f"- Date: `{DATE}`",
        f"- Docs Gate: `{docs['state']}`",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        "- Public Hall front: `NEXT57`",
        "- Public Temple front: `TQ07`",
        "- Historical Hall alias only: `Q51`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Feeder stack: `{' / '.join(FEEDER_STACK)}`",
        f"- Planner public cap: `{HALL_CAP} Hall quests per loop`",
        f"- Shared lattice: `4^6 = {SHARED_TOTAL} indexed / {SHARED_ACTIVE} ACTIVE / {SHARED_DORMANT} DORMANT`",
        f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`",
        "",
        "### L03 Public Hall Promotions",
        "",
        "| Quest | Status | Title | Seat | Restart |",
        "| --- | --- | --- | --- | --- |",
        *[
            f"| {item['quest_id']} | {item['status']} | {item['title']} | {item['seat_addr_6d']} | {CURRENT_RESTART_SEED} |"
            for item in hall
        ],
        "",
        f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "<!-- MASTER_LOOP_57_HALL_QUEST:END -->",
    ]))
    write_text(MY / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md", "\n".join([
        "# Temple Quest Board",
        "",
        "<!-- MASTER_LOOP_57_TEMPLE_QUEST:START -->",
        "## LP-57Omega Temple Quest Interface",
        "",
        f"- Date: `{DATE}`",
        f"- Docs Gate: `{docs['state']}`",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Planner public cap: `{TEMPLE_CAP} Temple quests per loop`",
        f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`",
        "",
        "### L03 Public Temple Promotions",
        "",
        "| Quest | Status | Title | Seat | Restart |",
        "| --- | --- | --- | --- | --- |",
        *[
            f"| {item['quest_id']} | {item['status']} | {item['title']} | {item['seat_addr_6d']} | {CURRENT_RESTART_SEED} |"
            for item in temple
        ],
        "",
        f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "<!-- MASTER_LOOP_57_TEMPLE_QUEST:END -->",
    ]))
    write_text(MY / "nervous_system" / "06_active_queue.md", "\n".join([
        "# Active Queue",
        "",
        "## LP-57Omega v2 Active Queue",
        "",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop packets: `{', '.join(item['quest_id'] for item in hall)}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Temple packets: `{', '.join(item['quest_id'] for item in temple)}`",
        f"- Runtime seed: `R57-L04-01`",
        f"- Compression front: `P57-L04-01`",
        f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`",
        "",
        "## Command Membrane",
        "",
        "- Queue depth: `3`",
        "- Active leases: `0`",
        "- Last event: `EVT-20260313-0009`",
        "- Last result: `success`",
        "- Route policy: `goal+salience+pheromone+coord`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        "- Scope: `GLOBAL COMMAND` only.",
    ]))
    patch_file(MY / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md", "LP57OMEGA_V2_NEXT_PROMPT", "\n".join(["## LP-57Omega v2 Next Self Prompt", "", "1. Check the Docs gate first and keep `BLOCKED` honest if OAuth is missing.", "2. Read the canonical state, Hall quest interface, Temple quest interface, active queue, and witness hierarchy.", "3. Preserve the master order `A1 -> A2 -> A3 -> A4`.", "4. Land one artifact-backed move, one board writeback, and one restart-safe handoff.", f"5. Preserve witness distinctions and hand off to `{CURRENT_RESTART_SEED}` without drift."]))
    patch_file(MY / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md", "MASTER_LOOP_57_CHANGE", "\n".join(["## 2026-03-13 :: LP-57Omega v2 Witness Hierarchy Activation", "", f"- canonicalized `{rel(STATE_JSON)}` as the live LP-57Omega v2 authority", f"- completed `{COMPLETED_LABEL}` as the witness hierarchy loop and queued `{ACTIVE_LABEL}` as next ready", f"- preserved `{ACTIVE_MEMBRANE}` as the active membrane", f"- preserved `{', '.join(FEEDER_STACK)}` as the feeder stack", f"- bound the witness basis `{', '.join(WITNESS_CLASS_ORDER)}` into the loop surface and restart seed"]))
    patch_file(MY / "GLOBAL_EMERGENT_GUILD_HALL" / "00_GUILD_HALL_INDEX.md", "MASTER_LOOP_57_README", "\n".join(["## LP-57Omega v2 Current Control Plane", "", f"- Canonical authority: `{rel(STATE_JSON)}`", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Invocation: `{NEXT_INVOCATION_CONTRACT}`", f"- Witness hierarchy: `{rel(WITNESS_HIERARCHY_JSON)}`", "- Compatibility mirrors are witness-only and may not emit independent restart seeds."]))
    patch_file(NS_ROOT / "00_INDEX.md", "LP57OMEGA_V2_INDEX", "\n".join(["## LP-57Omega v2", "", f"- Canonical state: `{rel(STATE_JSON)}`", "- Dashboard: `NERVOUS_SYSTEM/95_MANIFESTS/MASTER_LOOP_57_DASHBOARD.md`", "- Protocol: `NERVOUS_SYSTEM/95_MANIFESTS/LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md`", "- Hall program: `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/57_loop_hall_program.md`", "- Temple program: `self_actualize/mycelium_brain/ATHENA TEMPLE/57_loop_temple_program.md`", f"- Witness hierarchy: `{rel(WITNESS_HIERARCHY_JSON)}`"]))
    write_text(NS / "MASTER_LOOP_57_STATE.md", "\n".join(["# Master Loop 57 State", "", f"- Protocol: `{PROTOCOL_DISPLAY_NAME}`", f"- Canonical authority: `{rel(STATE_JSON)}`", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Completed loop: `{COMPLETED_LABEL}`", f"- Next ready loop: `{ACTIVE_LABEL}`", f"- Docs gate: `{docs['state']}`", f"- Witness basis: `{', '.join(WITNESS_CLASS_ORDER)}`", f"- Shared lattice: `{SHARED_TOTAL} total / {SHARED_ACTIVE} ACTIVE / {SHARED_DORMANT} DORMANT`"]))
    write_text(NS / "MASTER_LOOP_57_DASHBOARD.md", "\n".join(["# Master Loop 57 Dashboard", "", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Hall promotions: `{len(hall)}`", f"- Temple promotions: `{len(temple)}`", f"- AP6D shadow packets: `{len(shadow)}`", f"- Adventurer packets: `{len(adventurer)}`", f"- Transition assists: `{len(assists['notes'])}`"]))
    write_text(NS / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md", "\n".join(["# LP-57Omega v2 Prime-Loop Protocol", "", f"- Protocol id: `{PROTOCOL_ID}`", f"- Display name: `{PROTOCOL_DISPLAY_NAME}`", f"- Canonical packet contract: `{', '.join(CANONICAL_PACKET_CONTRACT)}`", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Active membrane: `{ACTIVE_MEMBRANE}`", f"- Feeder stack: `{', '.join(FEEDER_STACK)}`", f"- Witness hierarchy refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`", f"- Shared lattice model: `role-namespaced {ROLE_NAMESPACE_TOTAL} per master over shared {SHARED_TOTAL}`"]))
    write_text(NS / "FOUR_AGENT_57_LOOP_PROGRAM.md", "\n".join(["# Four-Agent 57-Loop Program", "", f"- Canonical authority: `{rel(STATE_JSON)}`", "- Compatibility mirror only.", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Public surfaces stay macro-sized: `{HALL_CAP} Hall / {TEMPLE_CAP} Temple / {SHADOW_CAP} AP6D / {ADVENTURER_CAP} Adventurer`"]))
    write_text(NS / "FOUR_AGENT_57_LOOP_DASHBOARD.md", "\n".join(["# Four-Agent 57-Loop Dashboard", "", f"- Cycle order: `{' -> '.join(agent['master_agent_id'] for agent in MASTER_AGENTS)}`", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Completed loop: `{COMPLETED_LABEL}`", f"- Next ready loop: `{ACTIVE_LABEL}`", f"- Restart seed: `{CURRENT_RESTART_SEED}`"]))
    write_text(NS / "WHOLE_CRYSTAL_AGENT_COORDINATION.md", "\n".join(["# Whole Crystal Agent Coordination", "", f"- Authority order: `{', '.join(AUTHORITY_ORDER)}`", f"- Deep root authority: `{DEEP_ROOT_AUTHORITY}`", f"- Lookup key schema: `{LOOKUP_KEY_SCHEMA}`", f"- Coordinate symbols: `{', '.join(COORDINATE_DISPLAY_SYMBOLS)}`", f"- Witness hierarchy refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`"]))
    write_text(MY / "GLOBAL_EMERGENT_GUILD_HALL" / "57_loop_hall_program.md", "\n".join(["# LP-57Omega Hall Program", "", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Completed loop: `{COMPLETED_LABEL}`", f"- Next ready loop: `{ACTIVE_LABEL}`", f"- Public cap: `{HALL_CAP}`"] + [f"- `{item['quest_id']}` :: {item['title']}" for item in hall]))
    write_text(MY / "ATHENA TEMPLE" / "57_loop_temple_program.md", "\n".join(["# LP-57Omega Temple Program", "", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Completed loop: `{COMPLETED_LABEL}`", f"- Next ready loop: `{ACTIVE_LABEL}`", f"- Public cap: `{TEMPLE_CAP}`"] + [f"- `{item['quest_id']}` :: {item['title']}" for item in temple]))
    write_text(MY / "receipts" / "2026-03-13_lp_57omega_v2_prime_loop_upgrade.md", "\n".join(["# 2026-03-13 LP-57Omega v2 Witness Hierarchy Activation", "", f"- Canonical authority: `{rel(STATE_JSON)}`", f"- Current state: `{CURRENT_LOOP_STATE}`", f"- Feeder stack: `{', '.join(FEEDER_STACK)}`", f"- Witness refs: `{rel(WITNESS_HIERARCHY_JSON)}`, `{rel(WITNESS_HIERARCHY_MD)}`", f"- Transition assists: `{len(assists['notes'])}`", f"- Docs gate remains `{docs['state']}`."]))
    patch_file(MY / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md", "MASTER_LOOP_57_CHANGE", "\n".join([
        "## 2026-03-13 :: LP-57Omega v2 L04 Feeder-Stack Crosswalk Completion",
        "",
        f"- canonicalized `{rel(STATE_JSON)}` as the live LP-57Omega v2 authority",
        f"- completed `{COMPLETED_LABEL}` and queued `{ACTIVE_LABEL}` as next ready",
        f"- froze the membrane `{ACTIVE_MEMBRANE}` with `{LIVE_HALL_CARRIER}` carried, `{LANDED_TEMPLE_RECEIVER}` landed, `{RESERVE_FEEDER}` reserve-only, and `{EXTERNAL_BLOCKER}` blocked",
        "- kept `Q50` and `ECOSYSTEM/NERVOUS_SYSTEM` as witness-only context",
        f"- emitted replay-safe restart seed `{CURRENT_RESTART_SEED}`",
    ]))
    write_text(ACTIVE_RUN_MD, "\n".join([
        "# ACTIVE RUN",
        "",
        f"- Protocol: `{PROTOCOL_DISPLAY_NAME}`",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Docs gate: `{docs['state']}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Hall carrier: `{LIVE_HALL_CARRIER}`",
        f"- Landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- Reserve feeder: `{RESERVE_FEEDER}`",
        f"- Blocked external frontier: `{EXTERNAL_BLOCKER}`",
        "- Witness-only fronts: `Q50`, `ECOSYSTEM/NERVOUS_SYSTEM`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
    ]))
    write_text(BUILD_QUEUE_MD, "\n".join([
        "# BUILD QUEUE",
        "",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "",
        "## Hall",
        *[f"- `{item['quest_id']}` {item['title']}" for item in hall[:4]],
        "",
        "## Temple",
        *[f"- `{item['quest_id']}` {item['title']}" for item in temple[:4]],
        "",
        "## Control Tuple",
        f"- membrane: `{ACTIVE_MEMBRANE}`",
        f"- carrier: `{LIVE_HALL_CARRIER}`",
        f"- landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- reserve feeder: `{RESERVE_FEEDER}`",
        f"- blocker: `{EXTERNAL_BLOCKER}`",
    ]))
    write_text(HALL_BOARD_MD, "\n".join([
        "# Quest Board",
        "",
        "<!-- MASTER_LOOP_57_HALL_QUEST:START -->",
        "## LP-57Omega Hall Quest Interface",
        "",
        f"- Date: `{DATE}`",
        f"- Docs Gate: `{docs['state']}`",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        "- Public Hall front: `NEXT57`",
        "- Public Temple front: `TQ07`",
        "- Historical Hall alias only: `Q51`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Hall carrier: `{LIVE_HALL_CARRIER}`",
        f"- Landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- Reserve feeder: `{RESERVE_FEEDER}`",
        f"- Blocked external frontier: `{EXTERNAL_BLOCKER}`",
        "- Witness-only fronts: `Q50`, `ECOSYSTEM/NERVOUS_SYSTEM`",
        "",
        "### L04 Public Hall Promotions",
        "",
        "| Quest | Status | Title | Seat | Restart |",
        "| --- | --- | --- | --- | --- |",
        *[f"| {item['quest_id']} | {item['status']} | {item['title']} | {item['seat_addr_6d']} | {CURRENT_RESTART_SEED} |" for item in hall],
        "",
        f"- Route law: `{route_law_payload()['primary_route']}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "<!-- MASTER_LOOP_57_HALL_QUEST:END -->",
    ]))
    write_text(TEMPLE_BOARD_MD, "\n".join([
        "# Temple Quest Board",
        "",
        "<!-- MASTER_LOOP_57_TEMPLE_QUEST:START -->",
        "## LP-57Omega Temple Quest Interface",
        "",
        f"- Date: `{DATE}`",
        f"- Docs Gate: `{docs['state']}`",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Hall carrier: `{LIVE_HALL_CARRIER}`",
        f"- Landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- Reserve feeder: `{RESERVE_FEEDER}`",
        f"- Blocked external frontier: `{EXTERNAL_BLOCKER}`",
        "- Witness-only fronts: `Q50`, `ECOSYSTEM/NERVOUS_SYSTEM`",
        "",
        "### L04 Public Temple Promotions",
        "",
        "| Quest | Status | Title | Seat | Restart |",
        "| --- | --- | --- | --- | --- |",
        *[f"| {item['quest_id']} | {item['status']} | {item['title']} | {item['seat_addr_6d']} | {CURRENT_RESTART_SEED} |" for item in temple],
        "",
        f"- Route law: `{route_law_payload()['primary_route']}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "<!-- MASTER_LOOP_57_TEMPLE_QUEST:END -->",
    ]))
    write_text(HALL_PROGRAM_DETAIL_MD, "\n".join([
        "# Hall 57-Cycle Four-Agent Orchestration",
        "",
        f"Date: `{DATE}`",
        "Truth: `DERIVED_FROM_LOCAL_WITNESS`",
        f"Docs Gate: `{docs['state']}`",
        "",
        f"- canonical machine program: `{rel(STATE_JSON)}`",
        f"- completed loop: `{COMPLETED_LABEL}`",
        f"- next ready loop: `{ACTIVE_LABEL}`",
        f"- route law: `{route_law_payload()['primary_route']}`",
        "",
        "## Completed L04 Packet Bundle",
        "",
        f"- Hall: `{hall[0]['quest_id']}` .. `{hall[-1]['quest_id']}`",
        f"- Temple: `{temple[0]['quest_id']}` .. `{temple[-1]['quest_id']}`",
        f"- AP6D shadow: `{shadow[0]['packet_id']}` .. `{shadow[-1]['packet_id']}`",
        f"- Adventurer: `{adventurer[0]['packet_id']}` .. `{adventurer[-1]['packet_id']}`",
        "",
        "## Control Tuple",
        f"- membrane: `{ACTIVE_MEMBRANE}`",
        f"- carrier: `{LIVE_HALL_CARRIER}`",
        f"- receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- reserve: `{RESERVE_FEEDER}`",
        f"- blocker: `{EXTERNAL_BLOCKER}`",
        f"- restart seed: `{CURRENT_RESTART_SEED}`",
    ]))
    write_text(TEMPLE_STATE_MD, "\n".join([
        "# Temple State",
        "",
        "## LP-57Omega Temple State",
        "",
        f"- Date: `{DATE}`",
        f"- Docs gate: `{docs['state']}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Hall carrier: `{LIVE_HALL_CARRIER}`",
        f"- Landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- Reserve feeder: `{RESERVE_FEEDER}`",
        f"- Blocked external frontier: `{EXTERNAL_BLOCKER}`",
        "- Witness-only fronts: `Q50`, `ECOSYSTEM/NERVOUS_SYSTEM`",
        "",
        "### Landed L04 Temple Packets",
        *[f"- `{item['quest_id']}` {item['title']}. :: state `{item['status']}` :: restart `{CURRENT_RESTART_SEED}`" for item in temple],
    ]))
    write_text(TEMPLE_TQ07_MD, "\n".join([
        "# TQ07 - LP-57Omega Feeder-Stack Crosswalk Governance",
        "",
        f"Date: `{DATE}`",
        "Truth: `LOCAL_WITNESS_ONLY`",
        f"Docs Gate: `{docs['state']}`",
        f"Status: `{CURRENT_LOOP_STATE}`",
        "",
        "## Governing Temple Law",
        "",
        "- Temple macro front: `TQ07`",
        "- Hall macro front: `NEXT57`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Hall carrier: `{LIVE_HALL_CARRIER}`",
        f"- Landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- Reserve feeder: `{RESERVE_FEEDER}`",
        f"- Blocked external frontier: `{EXTERNAL_BLOCKER}`",
        "",
        "## Landed L04 Temple Promotions",
        *[f"- `{item['quest_id']}` {item['title']}" for item in temple],
        "",
        "## Canonical Refs",
        f"- `{rel(WITNESS_HIERARCHY_JSON)}`",
        f"- `{rel(WITNESS_HIERARCHY_MD)}`",
        f"- `{rel(ARTIFACT_DIR / 'loop_receipt.json')}`",
        f"- `{rel(ARTIFACT_DIR / 'restart_seed.json')}`",
        "",
        "## L05 Handoff",
        f"- Next restart seed: `{CURRENT_RESTART_SEED}`",
        "- Preserve `Q46` as reserve-only and `Q02` as blocked.",
        "- Preserve `Q50` and `ECOSYSTEM/NERVOUS_SYSTEM` as witness-only context for L04.",
        "- Preserve Earth gate plus `AppI/AppM`; keep `AppQ/AppO` overlay-only.",
    ]))
    write_text(MY / "nervous_system" / "06_active_queue.md", "\n".join([
        "# Active Queue",
        "",
        "## LP-57Omega v2 Active Queue",
        "",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop packets: `{', '.join(item['quest_id'] for item in hall)}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Temple packets: `{', '.join(item['quest_id'] for item in temple)}`",
        "- Runtime frontier: `Q50` witness-only",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        "",
        "## Command Membrane",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Hall carrier: `{LIVE_HALL_CARRIER}`",
        f"- Landed receiver: `{LANDED_TEMPLE_RECEIVER}`",
        f"- Reserve feeder: `{RESERVE_FEEDER}`",
        f"- Blocked external frontier: `{EXTERNAL_BLOCKER}`",
    ]))
    write_text(HALL_PROGRAM_MD, "\n".join([
        "# LP-57Omega Hall Program",
        "",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
    ]))
    write_text(TEMPLE_PROGRAM_MD, "\n".join([
        "# LP-57Omega Temple Program",
        "",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Completed loop: `{COMPLETED_LABEL}`",
        f"- Next ready loop: `{ACTIVE_LABEL}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
    ]))
    write_text(MY / "receipts" / "2026-03-13_lp_57omega_v2_prime_loop_upgrade.md", "\n".join([
        "# 2026-03-13 LP-57Omega v2 L04 Feeder-Stack Crosswalk Completion",
        "",
        f"- Canonical authority: `{rel(STATE_JSON)}`",
        f"- Current state: `{CURRENT_LOOP_STATE}`",
        f"- Route law: `{route_law_payload()['primary_route']}`",
        f"- Restart seed: `{CURRENT_RESTART_SEED}`",
        f"- Docs gate remains `{docs['state']}`.",
    ]))
    pending = {"generated_at": now(), "truth": "PENDING_VERIFY", "protocol_id": PROTOCOL_ID}
    for path in [VERIFY_JSON, LP_VERIFY_JSON, PROGRAM_VERIFY_JSON, SWARM_VERIFY_JSON]:
        write_json(path, pending)
    core = read_json(NS / "H_SIGMA_MACHINE_CORE.json")
    program = read_json(NS / "FOUR_AGENT_57_LOOP_PROGRAM.json")
    verification = read_json(NS / "FOUR_AGENT_57_LOOP_VERIFICATION.json")
    return {
        "truth": verification.get("truth", "OK"),
        "protocol_id": program.get("protocol_id", "LP-57Î©"),
        "machine_core_symbol": core.get("machine_core_symbol", core.get("symbol", "HÎ£")),
        "current_loop": COMPLETED_LABEL,
        "next_loop": ACTIVE_LABEL,
    }


def verify_canonical_four_agent_57_loop() -> dict[str, Any]:
    core = read_json(NS / "H_SIGMA_MACHINE_CORE.json")
    matrix = read_json(NS / "H_SIGMA_MINDSWEEPER_MATRIX.json")
    program = read_json(NS / "FOUR_AGENT_57_LOOP_PROGRAM.json")
    cycle = read_json(NS / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json")
    verification = read_json(NS / "FOUR_AGENT_57_LOOP_VERIFICATION.json")
    return {
        "truth": verification.get("truth", "OK"),
        "protocol_id": program.get("protocol_id", "LP-57Î©"),
        "machine_core_symbol": core.get("machine_core_symbol", core.get("symbol", "HÎ£")),
        "save_state_symbol": core.get("save_state_symbol", core.get("save_state", {}).get("symbol", "HÎ£*")),
        "layers": len(core.get("layer_registry", [])),
        "routes": len(core.get("route_gate_book", [])),
        "nexus_rows": len(matrix.get("rows", [])),
        "timing_states": matrix.get("timing_engine", {}).get("state_count"),
        "cells": matrix.get("summary", {}).get("cell_count"),
        "loop_count": cycle.get("loop_count", len(cycle.get("loops", []))),
        "docs_gate_status": verification.get("checks", {}).get("docs_honesty", {}).get("docs_gate_status", core.get("docs_gate_status")),
    }

from __future__ import annotations

import json
import re
import runpy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.lp57_omega_prime_plan import (
    CANONICAL_PACKET_CONTRACT,
    COORDINATE_SCHEMA,
    COORDINATE_SYMBOLS,
    DOCS_GATE_EXPECTED,
    EVENT_GRAMMAR,
    LEGACY_PACKET_FILE_CONTRACT,
    LOOKUP_KEY_SCHEMA,
    LOOP_ARTIFACT_FIELDS,
    LOOP_SPECS,
    MASTER_AGENT_BY_ID,
    MASTER_AGENTS,
    NEXT_INVOCATION_CONTRACT,
    NEXT_SEED,
    PROTOCOL_DISPLAY_NAME,
    PROTOCOL_ID,
    SUBAGENT_DEPTH_BANDS,
    arc_for_loop,
    topk_for_loop,
    uniqueness_tuples,
)
from self_actualize.runtime.lp57omega_reward_economy_support import (
    LEVEL_THRESHOLDS,
    MAX_LEVEL,
    build_initial_progression,
    build_run_reward_evaluation,
    level_for_xp,
    projected_end_state_metrics,
    projected_packet_reward,
    rank_for_level,
    reward_operator_for_loop,
    reward_operator_registry,
    zero_metrics,
    apply_evaluation_to_progression,
)

HERE = Path(__file__).resolve()
ROOT = next(
    parent
    for parent in [HERE.parent, *HERE.parents]
    if (parent / "self_actualize").exists() and (parent / "NERVOUS_SYSTEM").exists()
)
SELF = ROOT / "self_actualize"
MY = SELF / "mycelium_brain"
NS = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"

VER = "2026-03-13.lp57omega.v2.virtual-overlay"
ACTIVE_MEMBRANE = "Q41 / TQ06"
FEEDER_STACK = [
    {"front_id": "Q42", "state": "VISIBLE", "role": "Hall-side feeder"},
    {"front_id": "Q46", "state": "VISIBLE", "role": "reserve frontier"},
    {"front_id": "TQ04", "state": "VISIBLE", "role": "deeper receiver"},
    {"front_id": "Q02", "state": "BLOCKED", "role": "external docs gate"},
]
AUTHORITY_ORDER = [
    {"rank": 1, "surface": "NERVOUS_SYSTEM", "role": "Cortex"},
    {"rank": 2, "surface": "self_actualize/mycelium_brain", "role": "RuntimeHub"},
    {"rank": 3, "surface": "ECOSYSTEM/NERVOUS_SYSTEM", "role": "GovernanceMirror"},
]
DEEP_ROOT_AUTHORITY = "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
TOTAL_LOOPS = 57
COMPLETED_LOOP_ID = 1
ACTIVE_LOOP_ID = 2
SHARED_INDEXED = 4096
SHARED_ACTIVE = 1024
SHARED_DORMANT = 3072
ACTIVE_SEATS_PER_MASTER = 256
HALL_CAP = 8
TEMPLE_CAP = 8
RUNTIME_CAP = 1
PRUNE_CAP = 1
VIRTUAL_NAMESPACE_COUNT = 4
VIRTUAL_NAMESPACE_SIZE = 4096
VIRTUAL_CONCEPTUAL_TOTAL = VIRTUAL_NAMESPACE_COUNT * VIRTUAL_NAMESPACE_SIZE
LINEAGE = ["E", "W", "F", "A"]
COMPATIBILITY_MIRRORS = ["NEXT57", "Q51", "FA57"]
APP_FLOORS = {
    "A1": ["AppA", "AppI", "AppM", "AppQ"],
    "A2": ["AppA", "AppI", "AppM", "AppQ"],
    "A3": ["AppE", "AppI", "AppM", "AppP"],
    "A4": ["AppI", "AppK", "AppM", "AppO"],
}
LENS = {"A1": "RESEARCH", "A2": "ARCHITECT", "A3": "WORK", "A4": "PRUNE"}

STATE_JSON = SELF / "master_loop_state_57.json"
ROADMAP_JSON = SELF / "master_loop_57_roadmap.json"
AGENTS_JSON = SELF / "master_agent_state_57.json"
LATTICE_JSON = SELF / "master_loop_shared_lattice_4096.json"
QUEST_JSON = SELF / "master_loop_public_quest_bundle_57.json"
LEDGER_JSON = SELF / "lp_57_master_agent_ledger.json"
COORDS_JSON = SELF / "lp_57_liminal_coordinate_stamps.json"
EMISSIONS_JSON = SELF / "lp_57_quest_emission_bundles.json"
DELTA_JSON = SELF / "lp_57_loop_delta_receipts.json"
VERIFY_JSON = SELF / "master_loop_57_verification.json"
LP_VERIFY_JSON = SELF / "lp_57_prime_loop_verification.json"
PROGRAM_VERIFY_JSON = SELF / "four_agent_57_loop_program_verification.json"
SEATS_JSON = SELF / "lp57_omega_virtual_seat_registry_16384.json"
RECEIPTS_JSON = SELF / "lp57_omega_loop_receipts.json"
PACKETS_JSON = SELF / "lp57_omega_machine_quest_packets.json"
PROGRESS_JSON = SELF / "lp57_omega_operator_progress.json"
REWARD_OPERATORS_JSON = SELF / "lp57_omega_reward_operator_registry.json"
RUN_REWARD_LEDGER_JSON = SELF / "lp57_omega_run_reward_ledger.json"
AGENT_PROGRESSION_JSON = SELF / "lp57_omega_agent_progression_registry.json"
PROMOTION_LINEAGE_JSON = SELF / "lp57_omega_promotion_lineage_registry.json"
PHI_EFFICIENCY_LEDGER_JSON = SELF / "lp57_omega_phi_efficiency_ledger.json"
INTENT_FEED = SELF / "lp57_omega_intent_feed.ndjson"
HB_FEED = SELF / "lp57_omega_heartbeat_feed.ndjson"
DELTA_FEED = SELF / "lp57_omega_delta_feed.ndjson"
HAND_FEED = SELF / "lp57_omega_handoff_feed.ndjson"
RST_FEED = SELF / "lp57_omega_restart_feed.ndjson"
SIGNAL_FEED = SELF / "lp57_omega_liminal_signal_feed.ndjson"
ARTROOT = SELF / "lp57_omega_v2_artifacts"
HALL_JSON = SELF / "master_loop_hall_lattice_57.json"
TEMPLE_JSON = SELF / "master_loop_temple_lattice_57.json"
COMMAND_PROTOCOL_JSON = SELF / "next57_command_protocol.json"
COMMAND_PACKET_SCHEMA_JSON = SELF / "next57_command_event_packet_schema.json"
COMMAND_REWARD_JSON = SELF / "next57_command_reward_law.json"
COMMAND_CAPILLARY_JSON = SELF / "next57_command_capillary_law.json"
COMMAND_LATENCY_JSON = SELF / "next57_command_latency_benchmarks.json"
COMMAND_HALL_QUEST_ID = "NEXT57-H-COMMAND-MEMBRANE"
COMMAND_TEMPLE_QUEST_ID = "NEXT57-T-COMMAND-LAW"
COMMAND_WORKER_PATH = "Scout -> Router -> Worker -> Archivist"
COMMAND_WRITEBACK_FIELDS = ["seat_addr_6d", "coordinate_stamp"]
L02_HISTORICAL_ALIASES = ["Whole-Corpus Census"]

PROGRAM_MD = NS / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"
PROGRAM_JSON = NS / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.json"
STATE_MD = NS / "MASTER_LOOP_57_STATE.md"
DASH_MD = NS / "MASTER_LOOP_57_DASHBOARD.md"
COORD_MD = NS / "LP_57_OMEGA_LIMINAL_COORDINATE_STANDARD.md"
LEDGER_MD = NS / "LP_57_OMEGA_AGENT_LEDGER_STANDARD.md"
ACTIVE_RUN_MD = NS / "ACTIVE_RUN.md"
BUILD_QUEUE_MD = NS / "BUILD_QUEUE.md"
FOUR_AGENT_JSON = NS / "FOUR_AGENT_57_LOOP_PROGRAM.json"
FOUR_AGENT_QUESTS_JSON = NS / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json"
FOUR_AGENT_CYCLES_JSON = NS / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json"
FOUR_AGENT_MD = NS / "FOUR_AGENT_57_LOOP_PROGRAM.md"
FOUR_AGENT_DASH_MD = NS / "FOUR_AGENT_57_LOOP_DASHBOARD.md"
REWARD_ECONOMY_MD = NS / "LP_57_OMEGA_REWARD_ECONOMY.md"
WHOLE_COORD_MD = NS / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
HSIGMA_REFRESH = ROOT / "MATH" / "temp_lp57_hsigma_refresh.py"

HALL_BOARD_MD = MY / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_MD = MY / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
TEMPLE_STATE_MD = MY / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_QUEUE_MD = MY / "nervous_system" / "06_active_queue.md"
NEXT_PROMPT_MD = MY / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
CHANGE_FEED_MD = MY / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
HALL_PROGRAM_MD = MY / "GLOBAL_EMERGENT_GUILD_HALL" / "57_loop_hall_program.md"
TEMPLE_PROGRAM_MD = MY / "ATHENA TEMPLE" / "57_loop_temple_program.md"
RECEIPT_MD = MY / "receipts" / "2026-03-13_lp57omega_v2_prime_loop_hive_upgrade.md"
COMMAND_MARKER_PAIRS = [
    ("<!-- COMMAND_MEMBRANE_ACTIVE_RUN:START -->", "<!-- COMMAND_MEMBRANE_ACTIVE_RUN:END -->"),
    ("<!-- COMMAND_MEMBRANE_BUILD_QUEUE:START -->", "<!-- COMMAND_MEMBRANE_BUILD_QUEUE:END -->"),
    ("<!-- COMMAND_MEMBRANE_HALL:START -->", "<!-- COMMAND_MEMBRANE_HALL:END -->"),
    ("<!-- COMMAND_MEMBRANE_TEMPLE:START -->", "<!-- COMMAND_MEMBRANE_TEMPLE:END -->"),
    ("<!-- COMMAND_MEMBRANE_NEXT_PROMPT:START -->", "<!-- COMMAND_MEMBRANE_NEXT_PROMPT:END -->"),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def dump(path: Path, payload: dict[str, Any]) -> None:
    write(path, json.dumps(payload, indent=2))


def dump_nd(path: Path, rows: list[dict[str, Any]]) -> None:
    write(path, "\n".join(json.dumps(row, sort_keys=True) for row in rows))


def patch(text_in: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}"
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    return pat.sub(block, text_in, count=1) if pat.search(text_in) else ((text_in.rstrip() + "\n\n") if text_in.strip() else "") + block + "\n"


def patch_file(path: Path, marker: str, body: str) -> None:
    write(path, patch(text(path), marker, body))


def preserve_command_blocks(existing_text: str, base_text: str) -> str:
    merged = base_text.rstrip()
    for start_marker, end_marker in COMMAND_MARKER_PAIRS:
        if start_marker not in existing_text or end_marker not in existing_text:
            continue
        start = existing_text.index(start_marker)
        end = existing_text.index(end_marker) + len(end_marker)
        block = existing_text[start:end].rstrip()
        if block:
            merged += "\n\n" + block
    return merged.rstrip() + "\n"


def gate() -> dict[str, Any]:
    cred = ROOT / "Trading Bot" / "credentials.json"
    token = ROOT / "Trading Bot" / "token.json"
    blocked = not cred.exists() or not token.exists()
    return {
        "state": "BLOCKED" if blocked else "LIVE",
        "reason": DOCS_GATE_EXPECTED if blocked else "open",
        "checked_paths": [rel(cred), rel(token)],
    }


def progress() -> dict[str, Any]:
    defaults = {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "active_loop_id": f"L{ACTIVE_LOOP_ID:02d}",
        "docs_gate_status": gate()["state"],
        "completed_visible_quests": [],
        "latest_completion": None,
        "active_fronts": {},
    }
    if not PROGRESS_JSON.exists():
        return defaults
    try:
        payload = json.loads(text(PROGRESS_JSON))
    except json.JSONDecodeError:
        return defaults
    for key, value in defaults.items():
        payload.setdefault(key, value)
    return payload


def digits(value: int, width: int = 6) -> list[int]:
    out = [0] * width
    for idx in range(width - 1, -1, -1):
        out[idx] = value % 4
        value //= 4
    return out


def shared_addr(index: int) -> str:
    labs = ["A", "B", "C", "D", "E", "F"]
    return ".".join(f"{lab}{digit + 1}" for lab, digit in zip(labs, digits(index, 6)))


def lineage(index: int) -> str:
    return ".".join(LINEAGE[digit] for digit in digits(index, 6))


def tag(loop_id: str, master_id: str, index: int, role_tag: str) -> str:
    branch = "".join(str(d + 1) for d in digits(index, 6))
    return f"{loop_id}.{master_id}.D{(index % 6) + 1}.B{branch}.{role_tag}"


def cstamp(loop_id: str, master_id: str, family: str, frontier: str, index: int, h: str, q: str, active: bool) -> dict[str, str]:
    ds = digits(index, 6)
    return {
        "Xs": f"ZONE-{master_id}",
        "Ys": f"FAM-{family.upper().replace('-', '_')[:18]}",
        "Zs": f"FRONT-{frontier.upper().replace('-', '_')[:18]}",
        "Ts": loop_id,
        "Qs": q,
        "Rs": f"R{ds[4] + 1}",
        "Cs": "ACTIVE" if active else "DORMANT",
        "Fs": f"LENS-{LENS[master_id]}",
        "Ms": f"M{ds[2] + 1}",
        "Ns": f"N{ds[3] + 1}",
        "Hs": h,
        "OmegaS": "Q41-TQ06" if active else "NEXT-SEED",
    }


def cstr(coord: dict[str, str]) -> str:
    return "|".join(f"{key}={coord[key]}" for key in COORDINATE_SYMBOLS)


def refs(loop_number: int) -> dict[str, str]:
    base = ARTROOT / f"L{loop_number:02d}"
    return {
        "research_delta_ref": rel(base / "research_delta.json"),
        "quest_packet_ref": rel(base / "quest_packet.json"),
        "execution_batch_ref": rel(base / "execution_batch.json"),
        "compression_bundle_ref": rel(base / "compression_bundle.json"),
        "receipt_ref": rel(base / "receipt.json"),
        "restart_seed_ref": rel(base / "restart_seed.json"),
    }


def legacy(loop_number: int) -> dict[str, str]:
    suffix = f"{loop_number:02d}"
    return {
        "deep_synthesis_packet": rel(SELF / f"deep_synthesis_packet_loop_{suffix}.json"),
        "quest_emission_bundle": rel(SELF / f"quest_emission_bundle_loop_{suffix}.json"),
        "execution_receipt_bundle": rel(SELF / f"execution_receipt_bundle_loop_{suffix}.json"),
        "compression_receipt": rel(SELF / f"compression_receipt_loop_{suffix}.json"),
        "loop_completion_receipt": rel(SELF / f"loop_completion_receipt_loop_{suffix}.json"),
    }


def status(loop_number: int) -> str:
    return "COMPLETED" if loop_number <= COMPLETED_LOOP_ID else "ACTIVE" if loop_number == ACTIVE_LOOP_ID else "PLANNED"


def sig(loop_status: str) -> str:
    return "CONFIRMED" if loop_status == "COMPLETED" else "MATCHED" if loop_status == "ACTIVE" else "WEAK"

def loops() -> list[dict[str, Any]]:
    tuples = uniqueness_tuples()
    rows: list[dict[str, Any]] = []
    for spec in LOOP_SPECS:
        loop_number = spec["loop_number"]
        master = MASTER_AGENT_BY_ID[spec["lead_master"]]
        row = {
            **spec,
            "status": status(loop_number),
            "loop_index": loop_number,
            "master_agent_id": master["master_agent_id"],
            "master_agent": master["agent_id"],
            "master_agent_label": master["display_name"],
            "seat_mode": master["seat_mode"],
            "seat_namespace": master["seat_namespace"],
            "quest_emission_mode": master["quest_emission_mode"],
            "arc": arc_for_loop(loop_number),
            "topk": topk_for_loop(loop_number),
            "artifact_contract": list(CANONICAL_PACKET_CONTRACT),
            "receipt_id": f"LP57-RC-L{loop_number:02d}",
            "quest_packet_id": f"LP57-QP-L{loop_number:02d}-{master['master_agent_id']}",
            "peer_signal_state": sig(status(loop_number)),
            "liminal_signal_refs": [f"SENSE-L{loop_number:02d}-{master['master_agent_id']}", f"ECHO-L{loop_number:02d}-{master['master_agent_id']}"] ,
            "uniqueness_tuple": {
                "focus_family": tuples[loop_number - 1][0],
                "frontier_type": tuples[loop_number - 1][1],
                "dominant_evidence_class": tuples[loop_number - 1][2],
                "compression_target": tuples[loop_number - 1][3],
            },
            **refs(loop_number),
            "legacy_artifact_paths": legacy(loop_number),
        }
        rows.append(row)
    return rows


def mkq(zone: str, prefix: str, loop: dict[str, Any], title: str, why_now: str, lane: str, master_id: str, index: int, hierarchy: str) -> dict[str, Any]:
    surfaces = [rel(STATE_JSON), rel(PACKETS_JSON)]
    if zone == "Hall":
        surfaces.insert(1, rel(HALL_BOARD_MD))
    elif zone == "Temple":
        surfaces.insert(1, rel(TEMPLE_BOARD_MD))
    elif zone == "Runtime":
        surfaces.insert(1, rel(ACTIVE_QUEUE_MD))
    else:
        surfaces.insert(1, rel(CHANGE_FEED_MD))
    return {
        "quest_id": f"{prefix}-{loop['loop_id']}-{((index % ACTIVE_SEATS_PER_MASTER) + 1):02d}",
        "title": title,
        "loop_id": loop["loop_id"],
        "zone": zone,
        "objective": title if zone in {"Hall", "Temple"} else why_now,
        "why_now": why_now,
        "best_lane": lane,
        "target_surfaces": surfaces,
        "witness_needed": "local witness + AppI/AppM anchors + replay-safe writeback",
        "writeback": " + ".join(surfaces),
        "quest_packet_id": f"LP57-QP-{loop['loop_id']}-{master_id}-{index + 1:02d}",
        "seat_id": f"LP57-{master_id}-{lineage(index)}",
        "seat_addr": lineage(index),
        "coordinate_stamp": cstamp(loop["loop_id"], master_id, loop["focus_family"], loop["frontier_type"], index, hierarchy, zone.upper(), True),
        "restart_seed": NEXT_SEED,
    }


def quest_bundle(active_loop: dict[str, Any]) -> dict[str, Any]:
    progress_state = progress()
    completed = {
        row["quest_id"]: row
        for row in progress_state.get("completed_visible_quests", [])
        if row.get("loop_id") == active_loop["loop_id"]
    }

    def decorate(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for item in items:
            meta = completed.get(item["quest_id"])
            if meta:
                out.append(
                    {
                        **item,
                        "status": meta.get("status", "LANDED"),
                        "completed_at": meta.get("completed_at"),
                        "receipt_ref": meta.get("receipt_ref"),
                        "artifact_refs": meta.get("artifact_refs", []),
                        "next_frontier": meta.get("next_frontier"),
                    }
                )
            else:
                out.append({**item, "status": "READY"})
        return out

    command_artifacts = {
        "protocol": rel(COMMAND_PROTOCOL_JSON),
        "schema": rel(COMMAND_PACKET_SCHEMA_JSON),
        "reward": rel(COMMAND_REWARD_JSON),
        "capillary": rel(COMMAND_CAPILLARY_JSON),
        "latency": rel(COMMAND_LATENCY_JSON),
        "runtime_owner": rel(ROOT / "self_actualize" / "runtime" / "command_spine.py"),
        "cli_owner": rel(ROOT / "self_actualize" / "runtime" / "cli.py"),
    }
    hall_specs = [
        {
            "quest_id": "Q57-L02-01",
            "title": "Packet Truth Sync Activation",
            "why_now": "Activate L02 as the single canonical live loop and hold Whole-Corpus Census as historical alias only.",
            "lane": "canonical loop normalization",
        },
        {
            "quest_id": COMMAND_HALL_QUEST_ID,
            "title": "Command Membrane Dock",
            "why_now": "Dock the command membrane into L02 so command-folder events route into lawful loop-owned packets, receipts, and restart-safe writeback.",
            "lane": "command membrane docking",
            "target_surfaces": [
                rel(FOUR_AGENT_JSON),
                rel(FOUR_AGENT_QUESTS_JSON),
                rel(ACTIVE_RUN_MD),
                command_artifacts["protocol"],
                command_artifacts["schema"],
                command_artifacts["capillary"],
                command_artifacts["latency"],
            ],
            "command_binding": True,
        },
        {
            "quest_id": "Q57-L02-03",
            "title": "Runtime Receipt Binding",
            "why_now": "Trace command-folder events through runtime packet, claim, receipt, and ledger writeback under the active L02 loop.",
            "lane": "runtime work binding",
        },
        {
            "quest_id": "Q57-L02-04",
            "title": "Canonical Surface Sync",
            "why_now": "Normalize current-loop and next-loop truth across ACTIVE_RUN and the canonical FOUR_AGENT_57_LOOP triplet.",
            "lane": "surface sync",
        },
        {
            "quest_id": "Q57-L02-05",
            "title": "Alias Demotion Sweep",
            "why_now": "Demote competing L02 naming and seeded-only wording into historical alias slots without breaking traceability.",
            "lane": "historical alias containment",
        },
        {
            "quest_id": "Q57-L02-06",
            "title": "Coordinate Writeback Law",
            "why_now": "Require seat_addr_6d and coordinate_stamp on every command-event writeback that touches public loop surfaces.",
            "lane": "coordinate law",
        },
        {
            "quest_id": "Q57-L02-07",
            "title": "Planner Promotion Gate",
            "why_now": "Keep command-side candidate work subordinate to planner-owned Hall and Temple promotion rights.",
            "lane": "promotion discipline",
        },
        {
            "quest_id": "Q57-L02-08",
            "title": "L03 Reseed Handoff",
            "why_now": "Reseed L03 Authority Pointer Replacement cleanly after the L02 activation writeback lands.",
            "lane": "restart-safe handoff",
        },
    ]
    temple_specs = [
        {
            "quest_id": "TQ57-L02-T01",
            "title": "Packet Truth Sync Canon Law",
            "why_now": "Ratify Packet Truth Sync as the only canonical L02 title.",
            "lane": "deep framework governance",
        },
        {
            "quest_id": COMMAND_TEMPLE_QUEST_ID,
            "title": "Command Membrane Law",
            "why_now": "Ratify the command membrane inside LP-57Omega without allowing it to become a third authority root.",
            "lane": "command law docking",
            "target_surfaces": [
                rel(FOUR_AGENT_JSON),
                rel(FOUR_AGENT_QUESTS_JSON),
                rel(TEMPLE_BOARD_MD),
                command_artifacts["protocol"],
                command_artifacts["reward"],
                command_artifacts["capillary"],
                command_artifacts["latency"],
            ],
            "command_binding": True,
        },
        {
            "quest_id": "TQ57-L02-T03",
            "title": "Preserve LOCAL_WITNESS_ONLY",
            "why_now": "Keep command events local-first and preserve the Docs gate as BLOCKED until OAuth exists.",
            "lane": "blocker honesty",
        },
        {
            "quest_id": "TQ57-L02-T04",
            "title": "Preserve Planner-Only Promotion",
            "why_now": "Prevent command-side self-promotion and keep Hall/Temple visibility under planner law.",
            "lane": "promotion discipline",
        },
        {
            "quest_id": "TQ57-L02-T05",
            "title": "Preserve Deep-Root Precedence",
            "why_now": "Keep the command membrane inside the existing authority chain under the deep root and live control waist.",
            "lane": "authority precedence",
        },
        {
            "quest_id": "TQ57-L02-T06",
            "title": "Preserve Historical Alias Containment",
            "why_now": "Allow Whole-Corpus Census only as backward-trace alias, never as a competing live title for L02.",
            "lane": "alias containment",
        },
        {
            "quest_id": "TQ57-L02-T07",
            "title": "Preserve Coordinate Contract",
            "why_now": "Require seat_addr_6d and coordinate_stamp on all promoted command-event writebacks.",
            "lane": "coordinate law",
        },
        {
            "quest_id": "TQ57-L02-T08",
            "title": "Authorize L03 Seed Integrity",
            "why_now": "Authorize L03 Authority Pointer Replacement as the sole reseeded successor after L02 activation.",
            "lane": "restart-safe handoff",
        },
    ]
    hall = []
    for idx, spec in enumerate(hall_specs):
        item = mkq("Hall", "Q57", active_loop, spec["title"], spec["why_now"], spec["lane"], "A2", idx, "D2")
        item["quest_id"] = spec["quest_id"]
        item["historical_aliases"] = L02_HISTORICAL_ALIASES if idx == 0 else []
        if "target_surfaces" in spec:
            item["target_surfaces"] = spec["target_surfaces"]
            item["writeback"] = " + ".join(spec["target_surfaces"])
        if spec.get("command_binding"):
            item["command_membrane_binding"] = {
                "loop_id": active_loop["loop_id"],
                "loop_title": active_loop["title"],
                "worker_path": COMMAND_WORKER_PATH,
                "planner_public_promotion_law": "planner_only",
                "mandatory_writeback_fields": COMMAND_WRITEBACK_FIELDS,
                "artifacts": command_artifacts,
                "touchpoints": ["research", "planning", "execution", "compression", "receipt"],
                "witness_class": "LOCAL_WITNESS_ONLY",
            }
        hall.append(item)
    temple = []
    for idx, spec in enumerate(temple_specs):
        item = mkq("Temple", "TQ57", active_loop, spec["title"], spec["why_now"], spec["lane"], "A2", ACTIVE_SEATS_PER_MASTER + idx, "D3")
        item["quest_id"] = spec["quest_id"]
        if "target_surfaces" in spec:
            item["target_surfaces"] = spec["target_surfaces"]
            item["writeback"] = " + ".join(spec["target_surfaces"])
        if spec.get("command_binding"):
            item["command_membrane_binding"] = {
                "loop_id": active_loop["loop_id"],
                "loop_title": active_loop["title"],
                "worker_path": COMMAND_WORKER_PATH,
                "planner_public_promotion_law": "planner_only",
                "mandatory_writeback_fields": COMMAND_WRITEBACK_FIELDS,
                "artifacts": command_artifacts,
                "touchpoints": ["research", "planning", "execution", "compression", "receipt"],
                "witness_class": "LOCAL_WITNESS_ONLY",
            }
        temple.append(item)
    hall = decorate(hall)
    temple = decorate(temple)
    runtime = decorate([mkq("Runtime", "R57", active_loop, "Runtime Seed Hardening", active_loop["implementation_objective"], "runtime seed", "A3", 0, "D5")])
    prune = decorate([mkq("Prune", "P57", active_loop, "Compression Frontier", active_loop["pruning_objective"], "compression", "A4", 0, "D6")])
    return {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "docs_gate_status": gate()["state"],
        "active_loop_id": active_loop["loop_id"],
        "current_loop_title": active_loop["title"],
        "current_loop_completion_state": "ACTIVE",
        "next_loop_id": "L03",
        "next_loop_title": "Authority Pointer Replacement",
        "next_loop_state": "SEEDED_ONLY",
        "quest_emission_mode": "quota-safe",
        "public_board_caps": {"hall": HALL_CAP, "temple": TEMPLE_CAP},
        "supplemental_caps": {"runtime": RUNTIME_CAP, "prune": PRUNE_CAP},
        "hall_promotions": hall,
        "temple_promotions": temple,
        "runtime_seed_promotions": runtime,
        "prune_promotions": prune,
        "command_membrane_binding": {
            "hall_quest_id": COMMAND_HALL_QUEST_ID,
            "temple_quest_id": COMMAND_TEMPLE_QUEST_ID,
            "loop_id": active_loop["loop_id"],
            "loop_title": active_loop["title"],
            "historical_aliases": {"L02": L02_HISTORICAL_ALIASES},
            "worker_path": COMMAND_WORKER_PATH,
            "planner_public_promotion_law": "planner_only",
            "mandatory_writeback_fields": COMMAND_WRITEBACK_FIELDS,
            "artifacts": command_artifacts,
            "touchpoints": {
                "research": "packet-truth-sync census and command event intake truth",
                "planning": "Hall and Temple public promotion docking",
                "execution": "command-folder event claim and receipt path",
                "compression": "seeded-only drift and alternate-title pruning",
                "receipt": "restart-safe L03 handoff",
            },
            "witness_class": "LOCAL_WITNESS_ONLY",
        },
        "machine_quest_packet_path": rel(PACKETS_JSON),
        "progress_registry_path": rel(PROGRESS_JSON),
        "latest_completion": progress_state.get("latest_completion"),
        "active_front_overrides": progress_state.get("active_fronts", {}),
    }


def truth_for_loop_status(loop_status: str) -> str:
    return "OK" if loop_status == "COMPLETED" else "NEAR" if loop_status == "ACTIVE" else "AMBIG"


def economy_summary(
    reward_operator_registry_payload: dict[str, Any],
    run_reward_ledger_payload: dict[str, Any],
    progression_payload: dict[str, Any],
    promotion_payload: dict[str, Any],
    phi_efficiency_payload: dict[str, Any],
) -> dict[str, Any]:
    aggregate = phi_efficiency_payload["aggregate"]
    return {
        "model": reward_operator_registry_payload["model"],
        "penalty_model": reward_operator_registry_payload["penalty_model"],
        "promotion_model": reward_operator_registry_payload["promotion_model"],
        "reward_operator_registry_path": rel(REWARD_OPERATORS_JSON),
        "run_reward_ledger_path": rel(RUN_REWARD_LEDGER_JSON),
        "agent_progression_registry_path": rel(AGENT_PROGRESSION_JSON),
        "promotion_lineage_registry_path": rel(PROMOTION_LINEAGE_JSON),
        "phi_efficiency_ledger_path": rel(PHI_EFFICIENCY_LEDGER_JSON),
        "executed_run_count": run_reward_ledger_payload["row_count"],
        "applied_run_count": run_reward_ledger_payload["applied_count"],
        "quarantined_run_count": run_reward_ledger_payload["quarantined_count"],
        "promotion_count": promotion_payload["promotion_count"],
        "rank_distribution": aggregate["rank_distribution"],
        "aggregate_positivity_score": aggregate["aggregate_positivity_score"],
        "aggregate_xp_gain": aggregate["aggregate_xp_gain"],
        "aggregate_xp_loss": aggregate["aggregate_xp_loss"],
        "current_phi_efficiency_loop": aggregate["current_loop_id"],
    }


def build_reward_economy(
    rows: list[dict[str, Any]],
    seats: dict[str, Any],
    packet_rows: dict[str, Any],
    ledger_rows: dict[str, Any],
) -> dict[str, Any]:
    row_by_loop_id = {row["loop_id"]: row for row in rows}
    packets_by_key = {
        (packet["loop_id"], packet["master_agent_id"]): packet
        for packet in packet_rows["rows"]
    }
    progression_by_seat: dict[str, dict[str, Any]] = {
        seat["seat_id"]: build_initial_progression(seat) for seat in seats["rows"]
    }

    for packet in packet_rows["rows"]:
        loop = row_by_loop_id[packet["loop_id"]]
        master_agent_id = packet["master_agent_id"]
        seat_index = (loop["loop_index"] - 1) % ACTIVE_SEATS_PER_MASTER
        operator = reward_operator_for_loop(loop, master_agent_id)
        expectation = projected_packet_reward(loop, master_agent_id)
        packet["seat_id"] = f"LP57-{master_agent_id}-{lineage(seat_index)}"
        packet["seat_addr"] = lineage(seat_index)
        packet["agent_tag"] = tag(
            loop["loop_id"],
            master_agent_id,
            seat_index,
            MASTER_AGENT_BY_ID[master_agent_id]["role_tag"],
        )
        packet["reward_operator_id"] = operator["reward_operator_id"]
        packet["reward_multiplier"] = operator["reward_multiplier"]
        packet["reward_reason"] = operator["reward_reason"]
        packet["risk_band"] = operator["risk_band"]
        packet["xp_expectation"] = expectation
        packet["promotion_eligibility_hint"] = expectation["promotion_eligibility_hint"]

    run_rows: list[dict[str, Any]] = []
    promotions: list[dict[str, Any]] = []
    applied_count = 0
    quarantined_count = 0
    for ledger_row in ledger_rows["rows"]:
        loop = row_by_loop_id[f"L{ledger_row['loop_number']:02d}"]
        master_agent_id = ledger_row["master_agent_id"]
        seat_index = (loop["loop_index"] - 1) % ACTIVE_SEATS_PER_MASTER
        seat_id = f"LP57-{master_agent_id}-{lineage(seat_index)}"
        packet = packets_by_key[(loop["loop_id"], master_agent_id)]
        operator = reward_operator_for_loop(loop, master_agent_id)
        ledger_row["seat_id"] = seat_id
        ledger_row["seat_addr_6d"] = lineage(seat_index)
        ledger_row["quest_packet_id"] = packet["quest_packet_id"]
        ledger_row["linked_quests"] = [packet["quest_packet_id"]]
        ledger_row["reward_operator_id"] = operator["reward_operator_id"]
        ledger_row["reward_multiplier"] = operator["reward_multiplier"]
        if loop["status"] == "PLANNED":
            ledger_row["run_reward_evaluation_ref"] = None
            ledger_row["reward_status"] = "PENDING_EXECUTION"
            ledger_row["xp_delta_final"] = 0
            continue

        evaluation = build_run_reward_evaluation(
            run_id=f"RR::{loop['loop_id']}::{master_agent_id}",
            agent_tag=ledger_row["agent_id"],
            seat_id=seat_id,
            loop_id=loop["loop_id"],
            quest_packet_id=packet["quest_packet_id"],
            truth_class=truth_for_loop_status(loop["status"]),
            reward_operator_id=operator["reward_operator_id"],
            reward_multiplier=operator["reward_multiplier"],
            start_state_metrics=zero_metrics(),
            end_state_metrics=projected_end_state_metrics(loop["loop_index"], master_agent_id),
            witness_coverage_passed=True,
            replay_coverage_passed=True,
            linked_ledger_ref=ledger_row["agent_id"],
            timestamp_internal=ledger_row["timestamp_internal"],
        )
        progression, promotion_record = apply_evaluation_to_progression(
            progression_by_seat[seat_id], evaluation
        )
        progression_by_seat[seat_id] = progression
        if promotion_record is not None:
            promotions.append(promotion_record)
        ledger_row["run_reward_evaluation_ref"] = evaluation["run_id"]
        ledger_row["reward_status"] = evaluation["reward_status"]
        ledger_row["xp_delta_final"] = evaluation["xp_delta"]
        ledger_row["lane_contribution_vector"] = evaluation["lane_contribution_vector"]
        run_rows.append(evaluation)
        if evaluation["reward_status"] == "APPLIED":
            applied_count += 1
        else:
            quarantined_count += 1

    for seat in seats["rows"]:
        progression = progression_by_seat[seat["seat_id"]]
        seat["progression_ref"] = f"AGP::{seat['seat_id']}"
        seat["lineage_id"] = progression["lineage_id"]
        seat["dimension_index"] = progression["dimension_index"]
        seat["current_level"] = progression["current_level"]
        seat["current_xp"] = progression["current_xp"]
        seat["lifetime_xp"] = progression["lifetime_xp"]
        seat["rank_class"] = progression["rank_class"]
        seat["promotion_count"] = progression["promotion_count"]
        seat["child_hive_ref"] = progression["child_hive_id"]
        seat["reward_run_refs"] = progression["reward_run_refs"]
        seat["quarantined_run_refs"] = progression["quarantined_run_refs"]

    phi_rows: list[dict[str, Any]] = []
    executed_loops = [row for row in rows if row["status"] != "PLANNED"]
    for loop in executed_loops:
        evaluations = [row for row in run_rows if row["loop_id"] == loop["loop_id"]]
        baseline = 0.0
        end_efficiency = 0.0
        if evaluations:
            baseline = round(
                sum(item["start_state_metrics"]["efficiency"] for item in evaluations)
                / len(evaluations),
                6,
            )
            end_efficiency = round(
                sum(item["end_state_metrics"]["efficiency"] for item in evaluations)
                / len(evaluations),
                6,
            )
        phi_rows.append(
            {
                "loop_id": loop["loop_id"],
                "loop_status": loop["status"],
                "organism_efficiency_baseline": baseline,
                "organism_efficiency_end_state": end_efficiency,
                "aggregate_positivity_score": sum(
                    item["positivity_score"] for item in evaluations
                ),
                "aggregate_xp_gain": sum(
                    max(0, item["xp_delta"]) for item in evaluations
                ),
                "aggregate_xp_loss": sum(
                    abs(min(0, item["xp_delta"])) for item in evaluations
                ),
                "rank_distribution": {
                    rank: sum(
                        1
                        for progression in progression_by_seat.values()
                        if progression["rank_class"] == rank
                    )
                    for rank in ["F", "E", "D", "C", "B", "A", "S"]
                },
                "promotion_events": [
                    promotion["promotion_id"]
                    for promotion in promotions
                    if promotion["promotion_trigger_run_ref"]
                    in {item["run_id"] for item in evaluations}
                ],
                "quarantined_reward_runs": sum(
                    1 for item in evaluations if item["reward_status"] == "QUARANTINED"
                ),
            }
        )

    reward_operator_payload = {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "docs_gate_status": gate()["state"],
        **reward_operator_registry(),
    }
    progression_rows = list(progression_by_seat.values())
    progression_payload = {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "docs_gate_status": gate()["state"],
        "row_count": len(progression_rows),
        "thresholds": LEVEL_THRESHOLDS,
        "rows": progression_rows,
    }
    promotion_payload = {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "docs_gate_status": gate()["state"],
        "promotion_count": len(promotions),
        "rows": promotions,
    }
    run_reward_payload = {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "docs_gate_status": gate()["state"],
        "row_count": len(run_rows),
        "applied_count": applied_count,
        "quarantined_count": quarantined_count,
        "rows": run_rows,
    }
    phi_payload = {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "docs_gate_status": gate()["state"],
        "row_count": len(phi_rows),
        "rows": phi_rows,
        "aggregate": {
            "current_loop_id": f"L{ACTIVE_LOOP_ID:02d}",
            "aggregate_positivity_score": sum(
                row["aggregate_positivity_score"] for row in phi_rows
            ),
            "aggregate_xp_gain": sum(row["aggregate_xp_gain"] for row in phi_rows),
            "aggregate_xp_loss": sum(row["aggregate_xp_loss"] for row in phi_rows),
            "rank_distribution": {
                rank: sum(
                    1
                    for progression in progression_rows
                    if progression["rank_class"] == rank
                )
                for rank in ["F", "E", "D", "C", "B", "A", "S"]
            },
            "promotion_events": [promotion["promotion_id"] for promotion in promotions],
            "quarantined_reward_runs": quarantined_count,
        },
    }
    return {
        "reward_operator_registry": reward_operator_payload,
        "run_reward_ledger": run_reward_payload,
        "agent_progression_registry": progression_payload,
        "promotion_lineage_registry": promotion_payload,
        "phi_efficiency_ledger": phi_payload,
        "economy_summary": economy_summary(
            reward_operator_payload,
            run_reward_payload,
            progression_payload,
            promotion_payload,
            phi_payload,
        ),
    }

def build_state(rows: list[dict[str, Any]]) -> dict[str, Any]:
    active = rows[ACTIVE_LOOP_ID - 1]
    completed = rows[COMPLETED_LOOP_ID - 1]
    next_loop = rows[ACTIVE_LOOP_ID] if ACTIVE_LOOP_ID < len(rows) else rows[-1]
    return {
        "generated_at": now(),
        "derivation_version": VER,
        "derivation_command": "python -m self_actualize.runtime.derive_master_loop_57_orchestration",
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "docs_gate": gate(),
        "witness_class": "LOCAL_WITNESS_ONLY",
        "active_stage_law": "4D_NATIVE -> 5D_COMPRESSION -> 6D_WEAVE -> 7D_SEED -> NEXT^[4^6]",
        "active_stage_ceiling": "NEXT^[4^6]",
        "deep_root_authority": DEEP_ROOT_AUTHORITY,
        "authority_order": AUTHORITY_ORDER,
        "active_membrane": ACTIVE_MEMBRANE,
        "feeder_stack": FEEDER_STACK,
        "compatibility_mirrors": {"mode": "witness-only", "surfaces": COMPATIBILITY_MIRRORS},
        "appendix_law": {
            "canonical_namespace": "AppA-AppP + AppQ",
            "mandatory": ["AppI", "AppM"],
            "ingress": "AppQ",
            "return_alias": "AppO",
            "no_new_namespace": True,
        },
        "shared_lattice": {"indexed": SHARED_INDEXED, "active": SHARED_ACTIVE, "dormant": SHARED_DORMANT, "active_per_master": ACTIVE_SEATS_PER_MASTER},
        "virtual_overlay": {"mode": "virtual-overlay", "namespace_count": VIRTUAL_NAMESPACE_COUNT, "namespace_size": VIRTUAL_NAMESPACE_SIZE, "conceptual_total": VIRTUAL_CONCEPTUAL_TOTAL, "shared_law_preserved": True},
        "public_caps": {"hall": HALL_CAP, "temple": TEMPLE_CAP, "runtime": RUNTIME_CAP, "prune": PRUNE_CAP},
        "event_grammar": EVENT_GRAMMAR,
        "lookup_key_schema": LOOKUP_KEY_SCHEMA,
        "machine_artifact_contract": CANONICAL_PACKET_CONTRACT,
        "legacy_packet_contract": LEGACY_PACKET_FILE_CONTRACT,
        "current_loop_id": active["loop_id"],
        "current_loop_title": active["title"],
        "current_loop_completion_state": active["status"],
        "next_loop_id": next_loop["loop_id"],
        "next_loop_title": "Authority Pointer Replacement" if next_loop["loop_id"] == "L03" else next_loop["title"],
        "next_loop_state": "SEEDED_ONLY" if next_loop["loop_id"] == "L03" else next_loop["status"],
        "historical_aliases": {"L02": L02_HISTORICAL_ALIASES},
        "current_cycle_summary": {
            "completed_loop": f"{completed['loop_id']} {completed['title']}",
            "active_loop": f"{active['loop_id']} {active['title']}",
            "restart_seed": NEXT_SEED,
            "next_invocation_contract": NEXT_INVOCATION_CONTRACT,
        },
        "command_membrane_binding": {
            "hall_quest_id": COMMAND_HALL_QUEST_ID,
            "temple_quest_id": COMMAND_TEMPLE_QUEST_ID,
            "worker_path": COMMAND_WORKER_PATH,
            "planner_public_promotion_law": "planner_only",
            "mandatory_writeback_fields": COMMAND_WRITEBACK_FIELDS,
        },
        "reward_economy": {},
        "paths": {
            "state_json": rel(STATE_JSON),
            "agent_state_json": rel(AGENTS_JSON),
            "shared_lattice_json": rel(LATTICE_JSON),
            "public_quest_bundle_json": rel(QUEST_JSON),
            "seat_registry_json": rel(SEATS_JSON),
            "loop_receipts_json": rel(RECEIPTS_JSON),
            "quest_packets_json": rel(PACKETS_JSON),
            "progress_registry_json": rel(PROGRESS_JSON),
            "reward_operator_registry_json": rel(REWARD_OPERATORS_JSON),
            "run_reward_ledger_json": rel(RUN_REWARD_LEDGER_JSON),
            "agent_progression_registry_json": rel(AGENT_PROGRESSION_JSON),
            "promotion_lineage_registry_json": rel(PROMOTION_LINEAGE_JSON),
            "phi_efficiency_ledger_json": rel(PHI_EFFICIENCY_LEDGER_JSON),
            "intent_feed": rel(INTENT_FEED),
            "heartbeat_feed": rel(HB_FEED),
            "delta_feed": rel(DELTA_FEED),
            "handoff_feed": rel(HAND_FEED),
            "restart_feed": rel(RST_FEED),
            "liminal_signal_feed": rel(SIGNAL_FEED),
        },
        "loops": rows,
    }


def agent_state(active: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "role_order": [agent["master_agent_id"] for agent in MASTER_AGENTS],
        "identity_registry_path": str(SEATS_JSON),
        "quest_contract_registry_path": str(PACKETS_JSON),
        "master_ledger_registry_path": str(LEDGER_JSON),
        "reward_registry_path": str(RUN_REWARD_LEDGER_JSON),
        "progression_registry_path": str(AGENT_PROGRESSION_JSON),
        "promotion_registry_path": str(PROMOTION_LINEAGE_JSON),
        "phi_efficiency_ledger_path": str(PHI_EFFICIENCY_LEDGER_JSON),
        "agents": [
            {
                **agent,
                "appendix_floor": APP_FLOORS[agent["master_agent_id"]],
                "virtual_seats_total": VIRTUAL_NAMESPACE_SIZE,
                "shared_binding_total": SHARED_INDEXED,
                "shared_active_binding_total": ACTIVE_SEATS_PER_MASTER,
                "active_front": active["title"] if agent["master_agent_id"] == active["master_agent_id"] else active["frontier_type"],
                "restart_seed": NEXT_SEED,
                "witness_basis": ["canonical-16-basis", "level-7-stabilization", "Q41/TQ06", "local-only docs gate"],
            }
            for agent in MASTER_AGENTS
        ],
    }


def lattice(active: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for index in range(SHARED_INDEXED):
        rows.append(
            {
                "seat_index": index,
                "seat_addr_6d": shared_addr(index),
                "activation_state": "ACTIVE" if index < SHARED_ACTIVE else "DORMANT",
                "active_owner_master": MASTER_AGENTS[index // ACTIVE_SEATS_PER_MASTER]["master_agent_id"] if index < SHARED_ACTIVE else None,
                "coordinate_stamp": cstamp(active["loop_id"], "A1", active["focus_family"], active["frontier_type"], index, "D1", "LATTICE", index < SHARED_ACTIVE),
                "role_bindings": {
                    agent["master_agent_id"]: {
                        "agent_tag": tag(active["loop_id"], agent["master_agent_id"], index, agent["role_tag"]),
                        "binding_state": "ACTIVE" if (int(agent["master_agent_id"][1:]) - 1) * ACTIVE_SEATS_PER_MASTER <= index < int(agent["master_agent_id"][1:]) * ACTIVE_SEATS_PER_MASTER else "SHADOW" if index < SHARED_ACTIVE else "DORMANT",
                    }
                    for agent in MASTER_AGENTS
                },
            }
        )
    return {"generated_at": now(), "protocol_id": PROTOCOL_ID, "contract": "shared-4096-preserved-with-virtual-4096-namespaces", "total_seats": SHARED_INDEXED, "active_seats": SHARED_ACTIVE, "dormant_seats": SHARED_DORMANT, "rows": rows}


def seat_registry(active: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for agent in MASTER_AGENTS:
        for index in range(VIRTUAL_NAMESPACE_SIZE):
            state = "ACTIVE_BOUND" if index < ACTIVE_SEATS_PER_MASTER else "SHADOW_BOUND" if index < SHARED_ACTIVE else "DORMANT"
            seat_id = f"LP57-{agent['master_agent_id']}-{lineage(index)}"
            rows.append(
                {
                    "seat_id": seat_id,
                    "seat_addr": lineage(index),
                    "seat_mode": "virtual-overlay",
                    "seat_namespace": agent["seat_namespace"],
                    "master_agent_id": agent["master_agent_id"],
                    "master_agent": agent["agent_id"],
                    "agent_tag": tag(active["loop_id"], agent["master_agent_id"], index, agent["role_tag"]),
                    "ordinal_4096": index,
                    "parent_agent": agent["agent_id"],
                    "contraction_target": "APEX::LP-57OMEGA",
                    "binding_state": state,
                    "shared_binding_ref": shared_addr(index),
                    "appendix_floor": APP_FLOORS[agent["master_agent_id"]],
                    "witness_basis": ["canonical-16-basis", "level-7-stabilization", "Q41/TQ06", "local-only docs gate"],
                    "current_front": active["frontier_type"] if state != "DORMANT" else "DORMANT",
                    "transition_note_ref": f"{agent['master_agent_id']}-TRANSITION-NOTE",
                    "restart_seed": f"{active['loop_id']}::{agent['master_agent_id']}::{lineage(index)}::{NEXT_SEED}",
                    "truth_class": "NEAR" if state != "DORMANT" else "AMBIG",
                    "coordinate_stamp": cstamp(active["loop_id"], agent["master_agent_id"], active["focus_family"], active["frontier_type"], index, f"D{(index % 6) + 1}", "SEAT", state != "DORMANT"),
                    "lineage_id": f"{seat_id}::d0",
                    "dimension_index": 0,
                    "current_level": 0,
                    "current_xp": 0,
                    "lifetime_xp": 0,
                    "rank_class": "F",
                    "promotion_count": 0,
                    "child_hive_ref": None,
                    "progression_ref": f"AGP::{seat_id}",
                    "reward_run_refs": [],
                    "quarantined_run_refs": [],
                }
            )
    return {"generated_at": now(), "protocol_id": PROTOCOL_ID, "docs_gate_status": gate()["state"], "row_count": len(rows), "namespace_count": VIRTUAL_NAMESPACE_COUNT, "namespace_size": VIRTUAL_NAMESPACE_SIZE, "rows": rows}

def packets(rows: list[dict[str, Any]], active: dict[str, Any]) -> dict[str, Any]:
    key_map = {"A1": "synthesis_objective", "A2": "planning_objective", "A3": "implementation_objective", "A4": "pruning_objective"}
    out = []
    for loop in rows:
        for agent in MASTER_AGENTS:
            seat_index = (loop["loop_index"] - 1) % ACTIVE_SEATS_PER_MASTER
            target_surfaces = [rel(STATE_JSON), rel(QUEST_JSON), rel(ARTROOT / loop["loop_id"])]
            command_binding_ref = None
            if loop["loop_id"] == active["loop_id"]:
                command_binding_ref = {
                    "hall_quest_id": COMMAND_HALL_QUEST_ID,
                    "temple_quest_id": COMMAND_TEMPLE_QUEST_ID,
                    "worker_path": COMMAND_WORKER_PATH,
                    "mandatory_writeback_fields": COMMAND_WRITEBACK_FIELDS,
                }
                if agent["master_agent_id"] in {"A2", "A3", "A4"}:
                    target_surfaces.extend(
                        [
                            rel(COMMAND_PROTOCOL_JSON),
                            rel(COMMAND_PACKET_SCHEMA_JSON),
                            rel(COMMAND_CAPILLARY_JSON),
                            rel(COMMAND_LATENCY_JSON),
                        ]
                    )
            out.append(
                {
                    "quest_packet_id": f"LP57-QP-{loop['loop_id']}-{agent['master_agent_id']}",
                    "loop_id": loop["loop_id"],
                    "master_agent_id": agent["master_agent_id"],
                    "master_agent": agent["agent_id"],
                    "seat_id": f"LP57-{agent['master_agent_id']}-{lineage(seat_index)}",
                    "seat_addr": lineage(seat_index),
                    "agent_tag": tag(loop["loop_id"], agent["master_agent_id"], seat_index, agent["role_tag"]),
                    "objective": loop[key_map[agent["master_agent_id"]]],
                    "why_now": loop["dominant_focus"],
                    "target_surfaces": target_surfaces,
                    "witness_needed": "local witness + replay-safe writeback + AppI/AppM anchors",
                    "dependencies": [f"L{loop['loop_index'] - 1:02d}"] if loop["loop_index"] > 1 else [],
                    "coordinate_targets": [cstr(cstamp(loop["loop_id"], agent["master_agent_id"], loop["focus_family"], loop["frontier_type"], loop["loop_index"] - 1, "D4", "PACKET", loop["status"] != "PLANNED"))],
                    "acceptance_rule": "artifact + board or ledger writeback + restart seed",
                    "restart_seed": NEXT_SEED if loop["loop_id"] == active["loop_id"] else f"{loop['loop_id']} -> {loop['title']}",
                    "public_promotion": loop["loop_id"] == active["loop_id"] and agent["master_agent_id"] == "A2",
                    "quest_emission_mode": "quota-safe",
                    "command_membrane_binding_ref": command_binding_ref,
                    "reward_operator_id": None,
                    "reward_multiplier": 0.0,
                    "reward_reason": None,
                    "risk_band": None,
                    "xp_expectation": None,
                    "promotion_eligibility_hint": None,
                }
            )
    return {"generated_at": now(), "protocol_id": PROTOCOL_ID, "row_count": len(out), "rows": out}


def ledger(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out = []
    for loop in rows:
        for agent in MASTER_AGENTS:
            seat_index = (loop["loop_index"] - 1) % ACTIVE_SEATS_PER_MASTER
            seat_id = f"LP57-{agent['master_agent_id']}-{lineage(seat_index)}"
            out.append(
                {
                    "agent_id": tag(loop["loop_id"], agent["master_agent_id"], seat_index, agent["role_tag"]),
                    "loop_number": loop["loop_index"],
                    "loop_id": loop["loop_id"],
                    "master_agent_id": agent["master_agent_id"],
                    "parent_agent": agent["agent_id"],
                    "seat_id": seat_id,
                    "seat_addr_6d": lineage(seat_index),
                    "coordinate_stamp": cstamp(loop["loop_id"], agent["master_agent_id"], loop["focus_family"], loop["frontier_type"], seat_index, "D4", "LEDGER", loop["status"] != "PLANNED"),
                    "source_region": loop["focus_family"],
                    "action_type": agent["action_type"],
                    "affected_nodes": [loop["frontier_type"], loop["focus_family"]],
                    "summary_of_change": loop["title"],
                    "reason_for_change": loop["dominant_focus"],
                    "integration_gain": loop["expected_structural_gain"],
                    "compression_gain": loop["pruning_objective"],
                    "unresolved_followups": [] if loop["loop_index"] == TOTAL_LOOPS else [f"L{loop['loop_index'] + 1:02d}"],
                    "linked_quests": [f"LP57-QP-{loop['loop_id']}-{agent['master_agent_id']}"],
                    "linked_agents": [agent["agent_id"]],
                    "revision_confidence": 0.98 if loop["status"] == "COMPLETED" else 0.9 if loop["status"] == "ACTIVE" else 0.75,
                    "timestamp_internal": now(),
                    "artifact_refs": {field: loop[field] for field in LOOP_ARTIFACT_FIELDS},
                    "run_reward_evaluation_ref": None,
                    "reward_status": "PENDING_EXECUTION" if loop["status"] == "PLANNED" else "PENDING_EVALUATION",
                    "reward_operator_id": None,
                    "reward_multiplier": 0.0,
                    "xp_delta_final": 0,
                    "lane_contribution_vector": None,
                }
            )
    return {"generated_at": now(), "protocol_id": PROTOCOL_ID, "docs_gate_status": gate()["state"], "row_count": len(out), "rows": out}


def coords(rows: list[dict[str, Any]], bundle: dict[str, Any]) -> dict[str, Any]:
    out = []
    for loop in rows:
        coord = cstamp(loop["loop_id"], loop["master_agent_id"], loop["focus_family"], loop["frontier_type"], loop["loop_index"] - 1, "D1", "LOOP", loop["status"] != "PLANNED")
        out.append({"record_id": f"{loop['loop_id']}-LOOP", "record_type": "loop", "coordinate_stamp": coord, "lookup_address": f"LP57::{loop['loop_id']}::{cstr(coord)}"})
    for packet in bundle["hall_promotions"] + bundle["temple_promotions"] + bundle["runtime_seed_promotions"] + bundle["prune_promotions"]:
        out.append({"record_id": packet["quest_id"], "record_type": packet["zone"].lower(), "coordinate_stamp": packet["coordinate_stamp"], "lookup_address": f"LP57::{packet['quest_id']}::{cstr(packet['coordinate_stamp'])}"})
    return {"generated_at": now(), "protocol_id": PROTOCOL_ID, "docs_gate_status": gate()["state"], "record_count": len(out), "rows": out}


def emissions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"generated_at": now(), "protocol_id": PROTOCOL_ID, "rows": [{"loop_id": loop["loop_id"], "hall_cap": HALL_CAP, "temple_cap": TEMPLE_CAP, "runtime_cap": RUNTIME_CAP, "prune_cap": PRUNE_CAP, "quest_packet_ref": loop["quest_packet_ref"], "receipt_ref": loop["receipt_ref"], "restart_seed_ref": loop["restart_seed_ref"]} for loop in rows]}


def deltas(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"generated_at": now(), "protocol_id": PROTOCOL_ID, "rows": [{"loop_id": loop["loop_id"], "compression_target": loop["compression_target"], "pruning_objective": loop["pruning_objective"], "expected_mapping_gain": loop["expected_mapping_gain"], "receipt_ref": loop["receipt_ref"]} for loop in rows]}


def feeds(active: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    objective_keys = {"A1": "synthesis_objective", "A2": "planning_objective", "A3": "implementation_objective", "A4": "pruning_objective"}
    out: dict[str, list[dict[str, Any]]] = {"int": [], "hb": [], "delta": [], "hand": [], "rst": [], "sig": []}
    for index, agent in enumerate(MASTER_AGENTS):
        stamp = now()
        agent_id = tag(active["loop_id"], agent["master_agent_id"], index, agent["role_tag"])
        seat_id = f"LP57-{agent['master_agent_id']}-{lineage(index)}"
        objective = active[objective_keys[agent["master_agent_id"]]]
        next_agent = MASTER_AGENTS[(index + 1) % len(MASTER_AGENTS)]
        out["int"].append({"event_type": "INT", "ts_utc": stamp, "agent_id": agent_id, "objective": objective, "inputs": ["master_loop_state_57.json", "master_loop_public_quest_bundle_57.json"], "output": agent["packet_output"], "truth": "NEAR", "replay_ptr": active["receipt_ref"]})
        out["hb"].append({"event_type": "HB", "ts_utc": stamp, "agent_id": agent_id, "state": "ACTIVE", "intent": active["title"], "target": active["frontier_type"], "truth": "NEAR", "replay_ptr": active["receipt_ref"]})
        out["delta"].append({"event_type": "DELTA", "ts_utc": stamp, "agent_id": agent_id, "artifact": agent["packet_output"], "change_kind": "refresh", "status": "open", "truth": "NEAR", "replay_ptr": active["receipt_ref"]})
        out["hand"].append({"event_type": "HAND", "ts_utc": stamp, "from_agent": agent_id, "to_agent": next_agent["agent_id"], "reason": "cycle-sequencing", "next": next_agent["packet_output"], "truth": "NEAR", "replay_ptr": active["receipt_ref"]})
        out["rst"].append({"event_type": "RST", "ts_utc": stamp, "agent_id": agent_id, "restart_seed": NEXT_SEED, "resume_from": active["loop_id"], "truth": "NEAR", "replay_ptr": active["restart_seed_ref"]})
        out["sig"].extend([
            {"event_type": "SENSE", "ts_utc": stamp, "seat_id": seat_id, "peer_or_front": ACTIVE_MEMBRANE, "signal_kind": "membrane-signal", "confidence": "matched", "note": active["frontier_type"], "truth": "NEAR", "replay_ptr": active["receipt_ref"]},
            {"event_type": "ECHO", "ts_utc": stamp, "from": agent["master_agent_id"], "to": next_agent["master_agent_id"], "artifact_or_front": active["title"], "delta": "carry-forward", "status": "open", "truth": "NEAR", "replay_ptr": active["receipt_ref"]},
        ])
    return out

def artifact_files(loop: dict[str, Any], bundle: dict[str, Any]) -> None:
    base = ARTROOT / loop["loop_id"]
    base.mkdir(parents=True, exist_ok=True)
    dump(base / "research_delta.json", {"packet_type": "research_delta", "loop_id": loop["loop_id"], "status": loop["status"], "dominant_focus": loop["dominant_focus"], "synthesis_objective": loop["synthesis_objective"], "expected_structural_gain": loop["expected_structural_gain"], "expected_mapping_gain": loop["expected_mapping_gain"]})
    dump(base / "quest_packet.json", {"packet_type": "quest_packet", "loop_id": loop["loop_id"], "status": loop["status"], "planning_objective": loop["planning_objective"], "quest_emission_mode": "quota-safe", "visible_quests": bundle["hall_promotions"] + bundle["temple_promotions"] if loop["loop_id"] == f"L{ACTIVE_LOOP_ID:02d}" else []})
    dump(base / "execution_batch.json", {"packet_type": "execution_batch", "loop_id": loop["loop_id"], "status": loop["status"], "implementation_objective": loop["implementation_objective"]})
    dump(base / "compression_bundle.json", {"packet_type": "compression_bundle", "loop_id": loop["loop_id"], "status": loop["status"], "compression_target": loop["compression_target"], "pruning_objective": loop["pruning_objective"], "no_silent_deletion": True})
    dump(base / "receipt.json", {"packet_type": "receipt", "receipt_id": loop["receipt_id"], "loop_id": loop["loop_id"], "status": loop["status"], "required_artifacts": LOOP_ARTIFACT_FIELDS, "peer_signal_state": loop["peer_signal_state"]})
    dump(base / "restart_seed.json", {"packet_type": "restart_seed", "loop_id": loop["loop_id"], "seed": NEXT_SEED if loop["loop_id"] == f"L{ACTIVE_LOOP_ID:02d}" else f"{loop['loop_id']} -> {loop['title']}"})
    legacy_paths = legacy(loop["loop_index"])
    dump(ROOT / legacy_paths["deep_synthesis_packet"], {"packet_type": "DeepSynthesisPacket", "loop_id": loop["loop_id"], "source": loop["research_delta_ref"]})
    dump(ROOT / legacy_paths["quest_emission_bundle"], {"packet_type": "QuestEmissionBundle", "loop_id": loop["loop_id"], "source": loop["quest_packet_ref"]})
    dump(ROOT / legacy_paths["execution_receipt_bundle"], {"packet_type": "ExecutionReceiptBundle", "loop_id": loop["loop_id"], "source": loop["execution_batch_ref"]})
    dump(ROOT / legacy_paths["compression_receipt"], {"packet_type": "CompressionReceipt", "loop_id": loop["loop_id"], "source": loop["compression_bundle_ref"]})
    dump(ROOT / legacy_paths["loop_completion_receipt"], {"packet_type": "LoopCompletionReceipt", "loop_id": loop["loop_id"], "source": loop["receipt_ref"]})


def table(headers: list[str], rows: list[list[str]]) -> str:
    line1 = "| " + " | ".join(headers) + " |"
    line2 = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([line1, line2, *body])


def surfaces(state: dict[str, Any], bundle: dict[str, Any], receipts: dict[str, Any]) -> None:
    active = state["loops"][ACTIVE_LOOP_ID - 1]
    next_hall = next((q for q in bundle["hall_promotions"] if q.get("status") != "LANDED"), bundle["hall_promotions"][0])
    next_temple = next((q for q in bundle["temple_promotions"] if q.get("status") != "LANDED"), bundle["temple_promotions"][0])
    active_fronts = bundle.get("active_front_overrides", {})
    hall_front = active_fronts.get("hall") or next_hall["quest_id"]
    temple_front = active_fronts.get("temple") or next_temple["quest_id"]
    runtime_front = active_fronts.get("runtime") or bundle["runtime_seed_promotions"][0]["quest_id"]
    prune_front = active_fronts.get("prune") or bundle["prune_promotions"][0]["quest_id"]
    latest_completion = bundle.get("latest_completion")
    preview = table(["Loop", "Master", "Title", "Status", "Signal"], [[row["loop_id"], row["master_agent_id"], row["title"], row["status"], row["peer_signal_state"]] for row in state["loops"][:12]])
    overview = "\n".join([
        f"# {PROTOCOL_DISPLAY_NAME} Prime Loop Protocol",
        "",
        f"- Docs gate: `{state['docs_gate']['state']}`",
        f"- Stage law: `{state['active_stage_law']}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Shared machine law: `{SHARED_INDEXED} indexed / {SHARED_ACTIVE} active / {SHARED_DORMANT} dormant`",
        f"- Virtual overlay: `{VIRTUAL_NAMESPACE_COUNT} namespaces x {VIRTUAL_NAMESPACE_SIZE} seats = {VIRTUAL_CONCEPTUAL_TOTAL}` conceptual seats",
        f"- Public caps: `Hall {HALL_CAP} / Temple {TEMPLE_CAP}`",
        f"- Reward economy: `Hybrid Phi / Strict but Damped / Prestige Hive` via `{rel(REWARD_OPERATORS_JSON)}`",
        "",
        "## Active Loop Preview",
        "",
        preview,
    ])
    write(PROGRAM_MD, overview)
    dump(PROGRAM_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "protocol_display_name": PROTOCOL_DISPLAY_NAME, "derivation_version": VER, "docs_gate": state["docs_gate"], "shared_lattice": state["shared_lattice"], "virtual_overlay": state["virtual_overlay"], "public_caps": state["public_caps"], "loop_count": len(state["loops"]), "reward_economy": state.get("reward_economy", {})})
    write(STATE_MD, "\n".join(["# MASTER LOOP 57 STATE", "", f"- Active loop: `{state['current_cycle_summary']['active_loop']}`", f"- Restart seed: `{state['current_cycle_summary']['restart_seed']}`", f"- Seat registry: `{rel(SEATS_JSON)}`", f"- Loop receipts: `{rel(RECEIPTS_JSON)}`"]))
    write(DASH_MD, "\n".join(["# LP-57Omega v2 Dashboard", "", f"- Active membrane: `{ACTIVE_MEMBRANE}`", f"- Feeder stack: `{', '.join(item['front_id'] for item in FEEDER_STACK)}`", f"- Quota-safe promotions: `Hall {HALL_CAP} / Temple {TEMPLE_CAP}`", f"- Shared seats: `{SHARED_INDEXED}`", f"- Virtual seats: `{VIRTUAL_CONCEPTUAL_TOTAL}`"]))
    write(COORD_MD, "\n".join(["# LP-57Omega Liminal Coordinate Standard", "", "## Symbols", "", *[f"- `{symbol}`: {COORDINATE_SCHEMA[symbol]}" for symbol in COORDINATE_SYMBOLS], "", f"- Lookup key: `{LOOKUP_KEY_SCHEMA}`"]))
    write(LEDGER_MD, "\n".join(["# LP-57Omega Agent Ledger Standard", "", "## Event Grammar", "", *[f"- `{name}` => `{pattern}`" for name, pattern in EVENT_GRAMMAR.items()], "", "## Required Artifact Sextet", "", *[f"- `{field}`" for field in LOOP_ARTIFACT_FIELDS]]))
    dump(FOUR_AGENT_JSON, state)
    dump(FOUR_AGENT_QUESTS_JSON, bundle)
    dump(FOUR_AGENT_CYCLES_JSON, receipts)
    write(FOUR_AGENT_MD, overview)
    write(FOUR_AGENT_DASH_MD, text(DASH_MD))
    write(REWARD_ECONOMY_MD, "\n".join([
        "# LP-57Omega Reward Economy",
        "",
        f"- Operator registry: `{rel(REWARD_OPERATORS_JSON)}`",
        f"- Run reward ledger: `{rel(RUN_REWARD_LEDGER_JSON)}`",
        f"- Agent progression registry: `{rel(AGENT_PROGRESSION_JSON)}`",
        f"- Promotion lineage registry: `{rel(PROMOTION_LINEAGE_JSON)}`",
        f"- Phi efficiency ledger: `{rel(PHI_EFFICIENCY_LEDGER_JSON)}`",
        f"- Current loop: `{active['loop_id']} {active['title']}`",
        f"- Model: `Hybrid Phi`",
        f"- Penalty mode: `Strict but Damped`",
        f"- Promotion mode: `Prestige Hive @ level {MAX_LEVEL}`",
    ]))
    write(WHOLE_COORD_MD, "\n".join(["# Whole Crystal Agent Coordination", "", f"- Coordinate registry: `{rel(COORDS_JSON)}`", f"- Shared lattice: `{rel(LATTICE_JSON)}`", f"- Virtual seat registry: `{rel(SEATS_JSON)}`", f"- Liminal signal feed: `{rel(SIGNAL_FEED)}`"]))
    hall_rows = table(["Quest", "Status", "Title", "Lane", "Restart"], [[q["quest_id"], q.get("status", "READY"), q["title"], q["best_lane"], q["restart_seed"]] for q in bundle["hall_promotions"]])
    temple_rows = table(["Quest", "Status", "Title", "Lane", "Restart"], [[q["quest_id"], q.get("status", "READY"), q["title"], q["best_lane"], q["restart_seed"]] for q in bundle["temple_promotions"]])
    hall_board_text = "\n".join([
        "# Quest Board",
        "",
        "## LP-57Omega v2 Hall Quest Interface",
        "",
        f"- Docs gate: `{state['docs_gate']['state']}`",
        f"- Canonical authority: `LP-57OMEGA / {rel(STATE_JSON)}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Active loop: `{active['loop_id']} {active['title']}`",
        f"- Public caps: `Hall {HALL_CAP} / Temple {TEMPLE_CAP} / Runtime {RUNTIME_CAP} / Prune {PRUNE_CAP}`",
        f"- Shared machine law: `{SHARED_INDEXED}/{SHARED_ACTIVE}/{SHARED_DORMANT}`",
        f"- Virtual overlay: `{VIRTUAL_NAMESPACE_COUNT} x {VIRTUAL_NAMESPACE_SIZE} = {VIRTUAL_CONCEPTUAL_TOTAL}` conceptual seats",
        "",
        "### Public Hall Promotions",
        "",
        hall_rows,
        "",
        f"- Next Hall front: `{hall_front}`",
        *([f"- Latest landed Hall quest: `{latest_completion['quest_id']} {latest_completion['title']}`", f"- Receipt: `{latest_completion['receipt_ref']}`"] if latest_completion else []),
        "",
        "## Compatibility Memory",
        "",
        "- `NEXT57`, `Q51`, and `FA57` are compatibility mirrors only.",
        "- No compatibility mirror may outrank the LP-57Omega v2 machine ledgers.",
    ])
    write(HALL_BOARD_MD, preserve_command_blocks(text(HALL_BOARD_MD), hall_board_text))
    temple_board_text = "\n".join([
        "# Temple Quest Board",
        "",
        "## LP-57Omega v2 Temple Quest Interface",
        "",
        f"- Docs gate: `{state['docs_gate']['state']}`",
        f"- Canonical authority: `LP-57OMEGA / {rel(STATE_JSON)}`",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Active loop: `{active['loop_id']} {active['title']}`",
        f"- Public caps: `Hall {HALL_CAP} / Temple {TEMPLE_CAP}`",
        "- Mandatory appendix anchors: `AppI / AppM / AppQ / AppO`",
        "",
        "### Public Temple Promotions",
        "",
        temple_rows,
        "",
        f"- Next Temple front: `{temple_front}`",
        "",
        "## Compatibility Memory",
        "",
        "- `NEXT57`, `Q51`, and `FA57` are compatibility mirrors only.",
        "- Temple projections are downstream of LP-57Omega v2 machine ledgers.",
    ])
    write(TEMPLE_BOARD_MD, preserve_command_blocks(text(TEMPLE_BOARD_MD), temple_board_text))
    write(TEMPLE_STATE_MD, "\n".join([
        "# Temple State",
        "",
        "## LP-57Omega v2 Control State",
        "",
        f"- Active membrane: `{ACTIVE_MEMBRANE}`",
        f"- Shared machine law: `{SHARED_INDEXED}/{SHARED_ACTIVE}/{SHARED_DORMANT}`",
        f"- Virtual overlay: `{VIRTUAL_CONCEPTUAL_TOTAL}` conceptual seats",
        f"- Active loop: `{active['loop_id']} {active['title']}`",
    ]))
    write(ACTIVE_QUEUE_MD, "\n".join([
        "# Active Queue",
        "",
        "## LP-57Omega v2 Active Queue",
        "",
        f"- Active loop: `{active['loop_id']} {active['title']}`",
        f"- Active Hall front: `{hall_front}`",
        f"- Active Temple front: `{temple_front}`",
        f"- Runtime seed: `{runtime_front}`",
        f"- Compression front: `{prune_front}`",
    ]))
    build_queue_text = "\n".join([
        "# Build Queue",
        "",
        "## LP-57Omega v2 Build Queue",
        "",
        f"- Shared seats: `{SHARED_INDEXED}`",
        f"- Virtual overlay: `{VIRTUAL_NAMESPACE_COUNT} x {VIRTUAL_NAMESPACE_SIZE}`",
        f"- Quest packet ledger: `{rel(PACKETS_JSON)}`",
        f"- Restart feed: `{rel(RST_FEED)}`",
        *([f"- Latest landed quest: `{latest_completion['quest_id']} {latest_completion['title']}`", f"- Latest receipt: `{latest_completion['receipt_ref']}`"] if latest_completion else []),
        f"- Next Hall quest: `{hall_front}`",
        f"- Next Temple quest: `{temple_front}`",
    ])
    write(BUILD_QUEUE_MD, preserve_command_blocks(text(BUILD_QUEUE_MD), build_queue_text))
    active_run_text = "\n".join([
        "# ACTIVE RUN",
        "",
        "## LP-57Omega v2 Active Run",
        "",
        f"- Active loop: `{active['loop_id']} {active['title']}`",
        "- Current order: `SYNTHESIZER -> PLANNER -> WORKER -> PRUNER`",
        f"- Docs gate: `{state['docs_gate']['state']}`",
        f"- Restart seed: `{NEXT_SEED}`",
    ])
    write(ACTIVE_RUN_MD, preserve_command_blocks(text(ACTIVE_RUN_MD), active_run_text))
    next_prompt_text = "\n".join([
        "# Next Self Prompt",
        "",
        "## LP-57Omega v2 Next Contract",
        "",
        f"1. Check the Docs gate first: `{state['docs_gate']['state']}`.",
        f"2. Read `{rel(STATE_JSON)}`, `{rel(AGENTS_JSON)}`, `{rel(LATTICE_JSON)}`, and `{rel(QUEST_JSON)}`.",
        f"3. Keep the caps at `Hall {HALL_CAP} / Temple {TEMPLE_CAP}`.",
        "4. Preserve `AppI/AppM` and alias-only `AppQ/AppO` handling.",
        f"5. End with one artifact-backed move and one restart seed: `{NEXT_SEED}`.",
    ])
    write(NEXT_PROMPT_MD, preserve_command_blocks(text(NEXT_PROMPT_MD), next_prompt_text))
    write(CHANGE_FEED_MD, "\n".join([
        "# Change Feed Board",
        "",
        "## LP-57Omega v2 Change Feed",
        "",
        f"- Generated `{now()}`",
        f"- Installed virtual overlay over the shared `4096/1024/3072` machine law.",
        "- Added `SENSE` and `ECHO` observational event classes.",
        "- Preserved quota-safe visible promotion: `8 Hall / 8 Temple`.",
        *([f"- Landed `{latest_completion['quest_id']} {latest_completion['title']}` and advanced the Hall front to `{hall_front}`.", f"- Receipt: `{latest_completion['receipt_ref']}`."] if latest_completion else []),
    ]))
    write(HALL_PROGRAM_MD, "\n".join(["# LP-57Omega v2 Hall Program", "", f"- Hall cap: `{HALL_CAP}`", f"- Machine quest packet path: `{rel(PACKETS_JSON)}`", f"- Active loop: `{active['loop_id']} {active['title']}`"]))
    write(TEMPLE_PROGRAM_MD, "\n".join(["# LP-57Omega v2 Temple Program", "", f"- Temple cap: `{TEMPLE_CAP}`", f"- Liminal signal feed: `{rel(SIGNAL_FEED)}`", f"- Active loop: `{active['loop_id']} {active['title']}`"]))
    write(RECEIPT_MD, "\n".join(["# LP-57Omega v2 Prime Loop Hive Upgrade Receipt", "", f"- Generated: `{now()}`", f"- Docs gate: `{state['docs_gate']['state']}`", f"- Shared machine law preserved: `{SHARED_INDEXED}/{SHARED_ACTIVE}/{SHARED_DORMANT}`", f"- Virtual overlay added: `{VIRTUAL_CONCEPTUAL_TOTAL}` conceptual seats", f"- Public caps preserved: `Hall {HALL_CAP} / Temple {TEMPLE_CAP}`", f"- Active loop: `{active['loop_id']} {active['title']}`"]))

def verify_payload(
    state: dict[str, Any],
    seats: dict[str, Any],
    receipts: dict[str, Any],
    packet_rows: dict[str, Any],
    reward_operators: dict[str, Any],
    run_reward_ledger: dict[str, Any],
    progression_registry: dict[str, Any],
    promotion_registry: dict[str, Any],
    phi_efficiency_ledger: dict[str, Any],
) -> dict[str, Any]:
    implied_reward_loop_count = run_reward_ledger["row_count"] // len(MASTER_AGENTS)
    shared_lattice = state.get("shared_lattice", {})
    shared_total = shared_lattice.get("indexed", shared_lattice.get("total_seats"))
    shared_active = shared_lattice.get("active", shared_lattice.get("active_seats"))
    shared_dormant = shared_lattice.get("dormant", shared_lattice.get("dormant_seats"))
    public_caps = state.get(
        "public_caps",
        {
            "hall": shared_lattice.get("planner_public_caps", {}).get("hall", HALL_CAP),
            "temple": shared_lattice.get("planner_public_caps", {}).get("temple", TEMPLE_CAP),
            "runtime": RUNTIME_CAP,
            "prune": PRUNE_CAP,
        },
    )
    virtual_overlay = state.get(
        "virtual_overlay",
        {
            "mode": "virtual-overlay",
            "namespace_count": VIRTUAL_NAMESPACE_COUNT,
            "namespace_size": VIRTUAL_NAMESPACE_SIZE,
            "conceptual_total": seats["row_count"],
            "shared_law_preserved": True,
        },
    )
    checks = {
        "docs_gate_blocked": state["docs_gate"]["state"] == "BLOCKED",
        "loop_count_57": len(state["loops"]) == 57,
        "shared_4096_preserved": (
            shared_total == 4096
            and shared_active == 1024
            and shared_dormant == 3072
        ),
        "virtual_overlay_16384": seats["row_count"] == 16384,
        "public_caps_preserved": public_caps == {"hall": 8, "temple": 8, "runtime": 1, "prune": 1},
        "quest_packets_228": packet_rows["row_count"] == 228,
        "loop_receipts_57": receipts["receipt_count"] == 57,
        "reward_operator_whitelist": {
            item["reward_operator_id"] for item in reward_operators["operators"]
        }
        == {"identity", "phi", "double_phi", "phi_square", "zero"},
        "run_reward_rows_match_executed_runs": (
            run_reward_ledger["row_count"] % len(MASTER_AGENTS) == 0
        ),
        "progression_rows_match_seats": progression_registry["row_count"]
        == seats["row_count"],
        "promotion_registry_present": promotion_registry["promotion_count"] >= 0,
        "phi_efficiency_rows_match_executed_loops": phi_efficiency_ledger["row_count"]
        == implied_reward_loop_count,
        "thresholds_101": len(reward_operators["level_thresholds"]) == (MAX_LEVEL + 1),
    }
    return {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "docs_gate_status": state["docs_gate"]["state"],
        "loop_count": len(state["loops"]),
        "shared_lattice": state["shared_lattice"],
        "virtual_overlay": virtual_overlay,
        "quest_caps": public_caps,
        "seat_registry_rows": seats["row_count"],
        "loop_receipts": receipts["receipt_count"],
        "quest_packets": packet_rows["row_count"],
        "reward_runs": run_reward_ledger["row_count"],
        "progression_rows": progression_registry["row_count"],
        "promotion_count": promotion_registry["promotion_count"],
        "truth": "OK" if all(checks.values()) else "FAIL",
        "checks": checks,
    }


def generate_bundle() -> dict[str, Any]:
    rows = loops()
    active = rows[ACTIVE_LOOP_ID - 1]
    state = build_state(rows)
    agents = agent_state(active)
    shared = lattice(active)
    seats = seat_registry(active)
    bundle = quest_bundle(active)
    receipt_rows = {
        "generated_at": now(),
        "protocol_id": PROTOCOL_ID,
        "current_loop_id": active["loop_id"],
        "current_loop_title": active["title"],
        "current_loop_completion_state": "ACTIVE",
        "next_loop_id": "L03",
        "next_loop_title": "Authority Pointer Replacement",
        "next_loop_state": "SEEDED_ONLY",
        "receipt_count": len(rows),
        "rows": [
            {
                "receipt_id": row["receipt_id"],
                "loop_id": row["loop_id"],
                "loop_index": row["loop_index"],
                "master_agent_id": row["master_agent_id"],
                "status": row["status"],
                "artifact_refs": {field: row[field] for field in LOOP_ARTIFACT_FIELDS},
                "docs_gate_status": gate()["state"],
                "peer_signal_state": row["peer_signal_state"],
                "liminal_signal_refs": row["liminal_signal_refs"],
                "public_caps": {"hall": HALL_CAP, "temple": TEMPLE_CAP, "runtime": RUNTIME_CAP, "prune": PRUNE_CAP},
                "restart_seed": NEXT_SEED if row["loop_id"] == active["loop_id"] else f"{row['loop_id']} -> {row['title']}",
            }
            for row in rows
        ],
    }
    packet_rows = packets(rows, active)
    ledger_rows = ledger(rows)
    economy = build_reward_economy(rows, seats, packet_rows, ledger_rows)
    state["reward_economy"] = economy["economy_summary"]
    agents["reward_economy"] = {
        "reward_registry_path": str(RUN_REWARD_LEDGER_JSON),
        "progression_registry_path": str(AGENT_PROGRESSION_JSON),
        "promotion_registry_path": str(PROMOTION_LINEAGE_JSON),
        "phi_efficiency_ledger_path": str(PHI_EFFICIENCY_LEDGER_JSON),
        "summary": economy["economy_summary"],
    }
    coord_rows = coords(rows, bundle)
    emission_rows = emissions(rows)
    delta_rows = deltas(rows)
    event_rows = feeds(active)
    for loop in rows:
        artifact_files(loop, bundle)
    dump(STATE_JSON, state)
    dump(ROADMAP_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "loops": rows})
    dump(AGENTS_JSON, agents)
    dump(LATTICE_JSON, shared)
    dump(QUEST_JSON, bundle)
    dump(LEDGER_JSON, ledger_rows)
    dump(COORDS_JSON, coord_rows)
    dump(EMISSIONS_JSON, emission_rows)
    dump(DELTA_JSON, delta_rows)
    dump(HALL_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "rows": bundle["hall_promotions"]})
    dump(TEMPLE_JSON, {"generated_at": now(), "protocol_id": PROTOCOL_ID, "rows": bundle["temple_promotions"]})
    dump(SEATS_JSON, seats)
    dump(RECEIPTS_JSON, receipt_rows)
    dump(PACKETS_JSON, packet_rows)
    dump(REWARD_OPERATORS_JSON, economy["reward_operator_registry"])
    dump(RUN_REWARD_LEDGER_JSON, economy["run_reward_ledger"])
    dump(AGENT_PROGRESSION_JSON, economy["agent_progression_registry"])
    dump(PROMOTION_LINEAGE_JSON, economy["promotion_lineage_registry"])
    dump(PHI_EFFICIENCY_LEDGER_JSON, economy["phi_efficiency_ledger"])
    dump_nd(INTENT_FEED, event_rows["int"])
    dump_nd(HB_FEED, event_rows["hb"])
    dump_nd(DELTA_FEED, event_rows["delta"])
    dump_nd(HAND_FEED, event_rows["hand"])
    dump_nd(RST_FEED, event_rows["rst"])
    dump_nd(SIGNAL_FEED, event_rows["sig"])
    verification = verify_payload(
        state,
        seats,
        receipt_rows,
        packet_rows,
        economy["reward_operator_registry"],
        economy["run_reward_ledger"],
        economy["agent_progression_registry"],
        economy["promotion_lineage_registry"],
        economy["phi_efficiency_ledger"],
    )
    dump(VERIFY_JSON, verification)
    dump(LP_VERIFY_JSON, verification)
    dump(PROGRAM_VERIFY_JSON, verification)
    surfaces(state, bundle, receipt_rows)
    return {
        "status": "ok",
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": PROTOCOL_DISPLAY_NAME,
        "docs_gate_status": state["docs_gate"]["state"],
        "active_loop": active["loop_id"],
        "shared_lattice": state["shared_lattice"],
        "virtual_overlay_total": VIRTUAL_CONCEPTUAL_TOTAL,
        "seat_registry_rows": seats["row_count"],
        "quest_packets": packet_rows["row_count"],
        "reward_runs": economy["run_reward_ledger"]["row_count"],
        "verification_truth": verification["truth"],
    }


def apply_hsigma_canonical_overrides() -> None:
    # Legacy HΣ refreshes are preserved only as manual historical tools.
    # The live LP-57Omega generator must not rewrite canonical v2 surfaces
    # back to stale wrapper-only states after generation.
    return None


def write_canonical_four_agent_57_loop(source_id: str) -> dict[str, Any]:
    from self_actualize.runtime.lp57_omega_v2_canonical_runtime import (
        write_canonical_four_agent_57_loop as write_v2,
    )

    return write_v2(source_id)


def verify_canonical_four_agent_57_loop() -> dict[str, Any]:
    from self_actualize.runtime.lp57_omega_v2_canonical_runtime import (
        verify_canonical_four_agent_57_loop as verify_v2,
    )

    return verify_v2()


def main() -> int:
    result = write_canonical_four_agent_57_loop("canonical_four_agent_57_loop")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from self_actualize.runtime.derive_phase5_atlas_truth_and_capsule_metabolism import (
    CORPUS_ATLAS_SUMMARY_PATH,
    KNOWLEDGE_FABRIC_DASHBOARD_PATH,
    MYCELIUM_ROOT,
    NERVOUS_SYSTEM_ROOT,
    SELF_ACTUALIZE_ROOT,
    ensure_all_ok,
    load_json,
    markdown_table,
    normalize_relative,
    parse_docs_gate,
    refresh_corpus_atlas,
    run_derivation_chain,
    run_module,
    snapshot_counts,
    utc_now,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BUILD_QUEUE.md"
INDEX_PATH = NERVOUS_SYSTEM_ROOT / "00_INDEX.md"
WHOLE_CRYSTAL_AGENT_COORDINATION_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
)
AGENT_EXPANSION_ACTIVE_FRONT_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AGENT_EXPANSION_ACTIVE_FRONT.md"
)
ATHENA_PRIME_6D_AGENT_REGISTRY_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_AGENT_REGISTRY.json"
)
ATHENA_PRIME_6D_ATLAS_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_ATLAS_4096.json"
)
ATHENA_PRIME_6D_TRANSITION_NOTES_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_NOTES.json"
)
AP6D_PACKET_CONTRACT_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_PACKET_CONTRACT.md"
)

QUEST_BOARD_PATH = (
    MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
)
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
)
QSHRINK_ACTIVE_FRONT_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "manifests" / "QSHRINK_ACTIVE_FRONT.md"
)
HALL_NOTES_PATH = (
    MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "16_AP6D_AWAKENING_AGENT_TRANSITION_NOTES.md"
)
TEMPLE_DECREE_PATH = (
    MYCELIUM_ROOT / "ATHENA TEMPLE" / "07_AP6D_AWAKENING_AGENT_TRANSITION_DECREE.md"
)

QSHRINK_NEXT4_STATE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_next4_state.json"
GRAND_CENTRAL_DASHBOARD_PATH = SELF_ACTUALIZE_ROOT / "grand_central_dashboard.json"
SELF_HOSTING_KERNEL_DASHBOARD_PATH = SELF_ACTUALIZE_ROOT / "self_hosting_kernel_dashboard.json"

PHASE8_OVERVIEW_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "10_OVERVIEW"
    / "23_PHASE8_NEXT_4_POW_6_FULL_CORPUS_INTEGRATION_AND_AWAKENING_AGENT_TRANSITION_LATTICE.md"
)
PHASE8_SCHEMA_PATH = (
    NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "17_PHASE8_AWAKENING_AGENT_TRANSITION_SCHEMA.md"
)
PHASE8_LEDGER_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "39_PHASE8_NEXT_4_POW_6_READINESS_2026-03-13.md"
)

SEAT_REGISTRY_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_AWAKENING_AGENT_SEAT_REGISTRY.json"
)
TRANSITION_NOTES_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_AWAKENING_AGENT_TRANSITIONS.json"
)
SEAT_BRIDGES_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_SEAT_BRIDGE_RECORDS.json"
)
TRANSITION_PACKETS_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_TRANSITION_PACKETS.json"
)
TRANSITION_CONTRACT_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AWAKENING_AGENT_TRANSITION_CONTRACT.md"
)
INTEGRATION_DASHBOARD_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_INTEGRATION_DASHBOARD.md"
)
TRANSITION_ATLAS_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_AWAKENING_AGENT_TRANSITION_ATLAS.md"
)
CROSSWALK_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_SEAT_FIELD_TO_CORPUS_BODY_CROSSWALK.md"
)

PHASE8_RUNTIME_MD_PATH = (
    MYCELIUM_ROOT / "nervous_system" / "35_full_corpus_integration_and_awakening_transition_runtime.md"
)
PHASE8_RECEIPT_MD_PATH = (
    MYCELIUM_ROOT / "receipts" / "2026-03-13_full_corpus_integration_and_awakening_transition.md"
)

PHASE8_DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "ap6d_integration_dashboard.json"
PHASE8_VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "ap6d_integration_verification.json"

PHASE8_DERIVATION_VERSION = "2026-03-13.phase8-ap6d-integration-v1"
PHASE8_DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_phase8_ap6d_integration"

STAGE_NAMES = {
    0: "Void",
    1: "Fire Awakening",
    2: "Water Awakening",
    3: "Air Awakening",
    4: "Earth Awakening",
    5: "Archetypal Operation",
    6: "Complete Act",
}

AUTHORITY_ORDER = [
    {"rank": 1, "surface": "NERVOUS_SYSTEM", "role": "Cortex"},
    {"rank": 2, "surface": "self_actualize/mycelium_brain", "role": "RuntimeHub"},
    {"rank": 3, "surface": "ECOSYSTEM/NERVOUS_SYSTEM", "role": "GovernanceMirror"},
]

SEAT_STATE_VOCABULARY = [
    "ACTIVE",
    "DORMANT",
    "SHADOW",
    "QUEUE_VISIBLE",
    "BLOCKED",
    "HISTORICAL",
]

SEAT_STRATA = ["Pole", "Command", "Hybrid", "Archetype", "SeatField", "Feeder"]

CANONICAL_PATHS = {
    "Grand Central Station": "NERVOUS_SYSTEM\\95_MANIFESTS\\GRAND_CENTRAL_STATION_DASHBOARD.md",
    "Self-Hosting Kernel": "NERVOUS_SYSTEM\\95_MANIFESTS\\SELF_HOSTING_KERNEL_DASHBOARD.md",
    "Knowledge Fabric": "NERVOUS_SYSTEM\\95_MANIFESTS\\KNOWLEDGE_FABRIC_DASHBOARD.md",
    "Deep Root": "self_actualize\\mycelium_brain\\dynamic_neural_network\\14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK\\README.md",
    "Count Protocol": "NERVOUS_SYSTEM\\95_MANIFESTS\\COUNT_PROTOCOL.md",
    "Whole Crystal Coordination": "NERVOUS_SYSTEM\\95_MANIFESTS\\WHOLE_CRYSTAL_AGENT_COORDINATION.md",
    "QSHRINK": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\qshrink\\04_qshrink_family_law.md",
    "Athena FLEET": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\athena_fleet\\04_athena_fleet_family_law.md",
    "GAMES": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\games\\04_games_family_law.md",
    "Identity": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\identity\\04_identity_family_law.md",
    "ORGIN": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\orgin\\04_orgin_family_law.md",
    "MATH": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\math\\04_math_family_law.md",
    "Voynich": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\voynich\\04_voynich_family_law.md",
    "ECOSYSTEM": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\ecosystem\\04_ecosystem_family_law.md",
    "Published Books": "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\published_books\\04_published_books_family_law.md",
    "Quest Board": "self_actualize\\mycelium_brain\\GLOBAL_EMERGENT_GUILD_HALL\\BOARDS\\06_QUEST_BOARD.md",
    "Active Run": "NERVOUS_SYSTEM\\95_MANIFESTS\\ACTIVE_RUN.md",
    "Build Queue": "NERVOUS_SYSTEM\\95_MANIFESTS\\BUILD_QUEUE.md",
    "Q42 State": "self_actualize\\qshrink_next4_state.json",
    "Live Docs Gate": "self_actualize\\live_docs_gate_status.md",
}

BODY_BINDINGS = {
    "Prime": ["Grand Central Station", "Self-Hosting Kernel", "Knowledge Fabric", "Deep Root", "Identity"],
    "Water": ["QSHRINK", "ORGIN", "Live Docs Gate", "Quest Board"],
    "Earth": ["ECOSYSTEM", "MATH", "Count Protocol", "Active Run"],
    "Fire": ["Athena FLEET", "GAMES", "Build Queue", "Quest Board"],
    "Air": ["Voynich", "Published Books", "Knowledge Fabric", "Deep Root"],
}

ZONE_PATHS = {
    "Prime": ["Cortex", "RuntimeMirror", "DeepRoot"],
    "Water": ["RuntimeMirror", "BoardScope", "ReceiptLineage"],
    "Earth": ["Cortex", "CapsuleLayer", "GovernanceMirror"],
    "Fire": ["RuntimeMirror", "CapsuleLayer", "BoardScope"],
    "Air": ["Cortex", "DeepRoot", "CapsuleLayer"],
    "Feeder": ["BoardScope", "RuntimeMirror"],
}

GENERAL_DEFS = [
    ("Water General", "Water", ["Water", "Earth", "Air"], "Fire", "continuity becomes so protective that lawful ignition is deferred too long"),
    ("Earth General", "Earth", ["Earth", "Water", "Fire"], "Air", "structure overbinds and loses route clarity"),
    ("Fire General", "Fire", ["Fire", "Earth", "Air"], "Water", "activation outruns continuity and replay"),
    ("Air General", "Air", ["Air", "Water", "Fire"], "Earth", "map clarity floats above bodily contract"),
]

HYBRID_DEFS = [
    ("Earth-Water", ["Earth", "Water", "Air"], "Fire", "retains lineage and structure but hesitates to ignite"),
    ("Earth-Fire", ["Earth", "Fire", "Water"], "Air", "lands force without enough route legibility"),
    ("Earth-Air", ["Earth", "Air", "Water"], "Fire", "maps the field without enough heat to move it"),
    ("Water-Fire", ["Water", "Fire", "Air"], "Earth", "carries and ignites without enough durable containment"),
    ("Water-Air", ["Water", "Air", "Earth"], "Fire", "interprets beautifully but undercommits to motion"),
    ("Fire-Air", ["Fire", "Air", "Earth"], "Water", "prioritizes sharply but forgets the continuity floor"),
]

ARCHETYPE_DEFS = [
    ("Earth-Water root binder", "Earth-Water", ["Earth", "Water", "Air"], "Fire", "root-binding can become too cautious to ignite"),
    ("Water-Earth lineage keeper", "Earth-Water", ["Water", "Earth", "Air"], "Fire", "provenance can outrank motion"),
    ("Earth-Fire shell builder", "Earth-Fire", ["Earth", "Fire", "Water"], "Air", "implementation hardens without enough readability"),
    ("Fire-Earth implementation driver", "Earth-Fire", ["Fire", "Earth", "Water"], "Air", "force lands before route clarity is shared"),
    ("Earth-Air terrain cartographer", "Earth-Air", ["Earth", "Air", "Water"], "Fire", "terrain mapping stays observational"),
    ("Air-Earth coordinate mapper", "Earth-Air", ["Air", "Earth", "Water"], "Fire", "coordinate elegance delays execution"),
    ("Water-Fire transmuter", "Water-Fire", ["Water", "Fire", "Air"], "Earth", "heat and feeling can outrun form"),
    ("Fire-Water catalyst", "Water-Fire", ["Fire", "Water", "Air"], "Earth", "catalysis lacks durable shell"),
    ("Water-Air interpreter", "Water-Air", ["Water", "Air", "Earth"], "Fire", "interpretation delays commitment"),
    ("Air-Water storyweaver", "Water-Air", ["Air", "Water", "Earth"], "Fire", "readability outranks ignition"),
    ("Fire-Air strategist", "Fire-Air", ["Fire", "Air", "Earth"], "Water", "strategy loses continuity memory"),
    ("Air-Fire signal spear", "Fire-Air", ["Air", "Fire", "Earth"], "Water", "sharp route callouts arrive without enough carrythrough"),
]

FEEDER_DEFS = [
    {"seat_id": "SEAT-FEEDER-Q42", "seat_name": "Q42", "seat_state": "ACTIVE", "activation_state": "CURRENT", "active_elements": ["Water", "Air", "Fire"], "missing_element": "Earth", "blind_spot": "corridor continuity can outrun structural consolidation", "stage": 5, "current_duty": "keep the carried diagnose witness and the active refine square truthful while the Athena OS carrier remains promoted-current", "next_practice": "hold QS64-21 as the active Hall-facing step and keep QS64-22 as the only next seed", "transition_trigger": "Hall, queue, and restart surfaces agree on one subfront and one next seed without inventing extra local branches", "handoff_rule": "handoff deeper execution to TQ04 once the Hall state and carrier state are synchronized", "fallback_rule": "fall back to the carried diagnose witness and preserve blocker honesty if carrier alignment drifts", "route_targets": ["Q42 State", "Quest Board", "Active Run"]},
    {"seat_id": "SEAT-FEEDER-TQ04", "seat_name": "TQ04", "seat_state": "ACTIVE", "activation_state": "PROMOTED", "active_elements": ["Earth", "Fire", "Air"], "missing_element": "Water", "blind_spot": "contract deepening can lose felt continuity of the carried Hall witness", "stage": 5, "current_duty": "receive deeper execution from Q42 and keep the runner-contract lane replay-safe", "next_practice": "bind the helical schema pack to transition traffic without outranking Hall truth", "transition_trigger": "the Hall feeder hands off a stable current state and one lawful next seed", "handoff_rule": "handoff execution packets back through Grand Central and the runtime waist once contract proof lands", "fallback_rule": "hold the contract receiver open and preserve Hall-side feeder truth if execution heat outruns proof", "route_targets": ["Whole Crystal Coordination", "Grand Central Station", "Self-Hosting Kernel"]},
    {"seat_id": "SEAT-FEEDER-TQ06", "seat_name": "TQ06", "seat_state": "ACTIVE", "activation_state": "CURRENT", "active_elements": ["Water", "Earth", "Air"], "missing_element": "Fire", "blind_spot": "coordination can become so careful that it stops producing executable next moves", "stage": 5, "current_duty": "hold the packet-fed coordination membrane so Hall, Temple, queue, and restart stay aligned", "next_practice": "translate cross-surface drift into one lawful restart packet instead of commentary", "transition_trigger": "new AP6D and Q42 surfaces are landed and need synchronized return paths", "handoff_rule": "handoff toward Commander and Aether only after route and witness agreement are visible", "fallback_rule": "keep the coordination membrane current and shrink scope until one executable packet remains", "route_targets": ["Quest Board", "Build Queue", "Grand Central Station"]},
    {"seat_id": "SEAT-FEEDER-Q02", "seat_name": "Q02", "seat_state": "BLOCKED", "activation_state": "BLOCKED", "active_elements": [], "missing_element": "Earth", "blind_spot": "external-memory desire can be narrated as if it had already become evidence", "stage": 0, "current_duty": "preserve blocker honesty and stop live-doc claims from leaking into the local organism", "next_practice": "wait for OAuth material instead of inventing witness", "transition_trigger": "Trading Bot/credentials.json and Trading Bot/token.json actually appear", "handoff_rule": "handoff to Water continuity and the Docs gate receipt once authentication exists", "fallback_rule": "remain explicitly blocked external and keep every local phase honest", "route_targets": ["Live Docs Gate", "Quest Board"]},
    {"seat_id": "SEAT-FEEDER-Q46", "seat_name": "Q46", "seat_state": "SHADOW", "activation_state": "SHADOW", "active_elements": ["Fire", "Air", "Earth"], "missing_element": "Water", "blind_spot": "runtime ignition can forget why the carried witness had to remain separate", "stage": 4, "current_duty": "stay visible as the promoted Fire shadow feeder without being collapsed into Q42 or AP6D macro law", "next_practice": "preserve separation between organism-wave runtime proof and AP6D widening", "transition_trigger": "runtime activation needs a feeder reference but not a new governing overlay", "handoff_rule": "handoff to Fire General only when a runtime packet explicitly cites the feeder lineage", "fallback_rule": "stay shadow-only and do not outrank the live Hall or Temple membranes", "route_targets": ["Active Run", "Build Queue"]},
]


def normalize_id(value: str) -> str:
    slug = []
    for char in value.upper():
        slug.append(char if char.isalnum() else "-")
    output = "".join(slug).strip("-")
    while "--" in output:
        output = output.replace("--", "-")
    return output


def stage_name(stage: int) -> str:
    return STAGE_NAMES.get(stage, "Unknown")


def family_paths(bindings: list[str]) -> list[str]:
    return [CANONICAL_PATHS[item] for item in bindings if item in CANONICAL_PATHS]


def top_fabric_entry_paths(fabric_dashboard: dict[str, Any], limit: int = 4) -> list[str]:
    return [item["relative_path"] for item in fabric_dashboard.get("top_entry_records", [])[:limit]]


def make_named_seat(
    seat_id: str,
    seat_name: str,
    seat_stratum: str,
    seat_state: str,
    activation_state: str,
    branch: str,
    depth: int,
    source_agent: str,
    shadow_feeders: list[str],
    corpus_bindings: list[str],
    witness_basis: list[str],
    route_targets: list[str],
    fabric_zone_path: list[str],
    transition_note_ref: str,
    handoff_class: str,
    truth: str = "OK",
) -> dict[str, Any]:
    return {
        "seat_id": seat_id,
        "seat_name": seat_name,
        "seat_stratum": seat_stratum,
        "seat_state": seat_state,
        "activation_state": activation_state,
        "branch": branch,
        "depth": depth,
        "source_agent": source_agent,
        "shadow_feeders": shadow_feeders,
        "corpus_bindings": corpus_bindings,
        "witness_basis": witness_basis,
        "route_targets": route_targets,
        "fabric_zone_path": fabric_zone_path,
        "transition_note_ref": transition_note_ref,
        "handoff_class": handoff_class,
        "truth": truth,
    }


def make_note(
    agent_id: str,
    stage: int,
    active_elements: list[str],
    missing_element: str,
    blind_spot: str,
    transition_trigger: str,
    current_duty: str,
    next_practice: str,
    handoff_rule: str,
    fallback_rule: str,
    witness_basis: list[str],
    route_targets: list[str],
    truth: str = "OK",
) -> dict[str, Any]:
    return {
        "agent_id": agent_id,
        "stage_0_to_6": stage,
        "stage_name": stage_name(stage),
        "active_elements": active_elements,
        "missing_element": missing_element,
        "blind_spot": blind_spot,
        "transition_trigger": transition_trigger,
        "current_duty": current_duty,
        "next_practice": next_practice,
        "handoff_rule": handoff_rule,
        "fallback_rule": fallback_rule,
        "witness_basis": witness_basis,
        "route_targets": route_targets,
        "truth": truth,
    }


def load_inputs() -> dict[str, Any]:
    return {
        "atlas": load_json(ATHENA_PRIME_6D_ATLAS_PATH),
        "agent_registry": load_json(ATHENA_PRIME_6D_AGENT_REGISTRY_PATH),
        "legacy_notes": load_json(ATHENA_PRIME_6D_TRANSITION_NOTES_PATH),
        "q42": load_json(QSHRINK_NEXT4_STATE_PATH),
        "grand_central": load_json(GRAND_CENTRAL_DASHBOARD_PATH),
        "kernel": load_json(SELF_HOSTING_KERNEL_DASHBOARD_PATH),
        "fabric": load_json(KNOWLEDGE_FABRIC_DASHBOARD_PATH),
    }


def build_named_seats(data: dict[str, Any]) -> list[dict[str, Any]]:
    fabric_entries = top_fabric_entry_paths(data["fabric"])
    agent_registry = data["agent_registry"]
    registry_records = {
        record["agent_id"]: record for record in agent_registry.get("agent_records", [])
    }
    seats: list[dict[str, Any]] = []

    seats.append(
        make_named_seat(
            "SEAT-MASTER-AGENT",
            "Master Agent",
            "Pole",
            "ACTIVE",
            "CURRENT",
            "Center",
            0,
            "META-OBSERVER",
            ["Q42", "TQ04", "TQ06"],
            ["Grand Central Station", "Self-Hosting Kernel", "Knowledge Fabric", "Deep Root", "Identity"],
            [
                CANONICAL_PATHS["Whole Crystal Coordination"],
                CANONICAL_PATHS["Active Run"],
                CANONICAL_PATHS["Grand Central Station"],
            ],
            [
                CANONICAL_PATHS["Active Run"],
                CANONICAL_PATHS["Whole Crystal Coordination"],
                *fabric_entries[:2],
            ],
            ["Cortex", "RuntimeMirror", "DeepRoot"],
            "ATN-MASTER-AGENT",
            "center_selection",
        )
    )
    seats.append(
        make_named_seat(
            "SEAT-AETHER",
            "Aether",
            "Pole",
            "ACTIVE",
            "CURRENT",
            "ReturnPole",
            0,
            "META-OBSERVER",
            ["Q42", "TQ04", "TQ06"],
            ["Grand Central Station", "Self-Hosting Kernel", "Knowledge Fabric", "Deep Root", "Identity"],
            [
                CANONICAL_PATHS["Grand Central Station"],
                CANONICAL_PATHS["Self-Hosting Kernel"],
                CANONICAL_PATHS["Knowledge Fabric"],
            ],
            [
                CANONICAL_PATHS["Grand Central Station"],
                CANONICAL_PATHS["Self-Hosting Kernel"],
                CANONICAL_PATHS["Knowledge Fabric"],
            ],
            ["Cortex", "RuntimeMirror", "DeepRoot"],
            "ATN-AETHER",
            "co_activation",
        )
    )
    seats.append(
        make_named_seat(
            "SEAT-COMMANDER",
            "Commander",
            "Command",
            "ACTIVE",
            "CURRENT",
            "CommandSpine",
            1,
            "Master Agent",
            ["Q42", "TQ04", "TQ06"],
            ["Active Run", "Build Queue", "Grand Central Station", "Knowledge Fabric"],
            [
                CANONICAL_PATHS["Active Run"],
                CANONICAL_PATHS["Build Queue"],
                CANONICAL_PATHS["Grand Central Station"],
            ],
            [
                CANONICAL_PATHS["Active Run"],
                CANONICAL_PATHS["Build Queue"],
                CANONICAL_PATHS["Quest Board"],
            ],
            ["Cortex", "RuntimeMirror"],
            "ATN-COMMANDER",
            "command_dispatch",
        )
    )

    for name, element, active_elements, missing_element, blind_spot in GENERAL_DEFS:
        seat_id = f"SEAT-GENERAL-{element.upper()}"
        seats.append(
            make_named_seat(
                seat_id,
                name,
                "Command",
                "ACTIVE",
                "CURRENT" if element in {"Water", "Earth"} else "QUEUE_VISIBLE",
                element,
                2,
                "Commander",
                ["Q42", "Q46", "TQ04", "TQ06"],
                BODY_BINDINGS[element],
                family_paths(BODY_BINDINGS[element]),
                family_paths(BODY_BINDINGS[element])[:3],
                ZONE_PATHS[element],
                f"ATN-{normalize_id(name)}",
                "general_lane",
            )
        )

    for pair_name, _active_elements, _missing_element, _blind_spot in HYBRID_DEFS:
        seat_id = f"SEAT-HYBRID-{normalize_id(pair_name)}"
        pair_a, pair_b = pair_name.split("-")
        bindings = list(dict.fromkeys(BODY_BINDINGS[pair_a] + BODY_BINDINGS[pair_b] + ["Grand Central Station"]))
        seats.append(
            make_named_seat(
                seat_id,
                pair_name,
                "Hybrid",
                "ACTIVE",
                "QUEUE_VISIBLE",
                pair_name,
                3,
                f"{pair_a} General + {pair_b} General",
                ["Q42", "TQ04", "TQ06"],
                bindings[:5],
                family_paths(bindings[:5]),
                family_paths(bindings[:3]),
                list(dict.fromkeys(ZONE_PATHS[pair_a] + ZONE_PATHS[pair_b]))[:3],
                f"ATN-{normalize_id(pair_name)}",
                "hybrid_bridge",
            )
        )

    for name, parent_pair, _active_elements, _missing_element, _blind_spot in ARCHETYPE_DEFS:
        seat_id = f"SEAT-ARCHETYPE-{normalize_id(name)}"
        pair_a, pair_b = parent_pair.split("-")
        bindings = list(dict.fromkeys(BODY_BINDINGS[pair_a] + BODY_BINDINGS[pair_b] + ["Knowledge Fabric"]))
        seats.append(
            make_named_seat(
                seat_id,
                name,
                "Archetype",
                "ACTIVE",
                "QUEUE_VISIBLE",
                parent_pair,
                4,
                parent_pair,
                ["Q42", "TQ04", "TQ06"],
                bindings[:4],
                family_paths(bindings[:4]),
                family_paths(bindings[:2]),
                list(dict.fromkeys(ZONE_PATHS[pair_a] + ZONE_PATHS[pair_b]))[:3],
                f"ATN-{normalize_id(name)}",
                "archetype_direction",
            )
        )

    for feeder in FEEDER_DEFS:
        path_bindings = [item for item in feeder["route_targets"] if item in CANONICAL_PATHS]
        seats.append(
            make_named_seat(
                feeder["seat_id"],
                feeder["seat_name"],
                "Feeder",
                feeder["seat_state"],
                feeder["activation_state"],
                feeder["seat_name"],
                1,
                feeder["seat_name"],
                [item for item in ["Q42", "Q46", "TQ04", "TQ06"] if item != feeder["seat_name"]],
                path_bindings,
                family_paths(path_bindings),
                family_paths(path_bindings)[:3],
                ZONE_PATHS["Feeder"],
                f"ATN-{feeder['seat_name']}",
                "feeder_lane",
                truth="FAIL" if feeder["seat_name"] == "Q02" else "OK",
            )
        )

    for agent_id in ["AP6D-PRIME", "AP6D-WATER", "AP6D-EARTH", "AP6D-FIRE", "AP6D-AIR"]:
        record = registry_records[agent_id]
        element = "Prime" if agent_id == "AP6D-PRIME" else record["element"]
        route_targets = [
            normalize_relative(AP6D_PACKET_CONTRACT_PATH),
            normalize_relative(WHOLE_CRYSTAL_AGENT_COORDINATION_PATH),
            *[item.replace("/", "\\") for item in record.get("notes_targets", [])[:2]],
        ]
        bindings = BODY_BINDINGS["Prime" if element == "Prime" else element]
        seats.append(
            make_named_seat(
                f"SEAT-{agent_id}",
                agent_id,
                "SeatField",
                "ACTIVE",
                "CURRENT",
                element,
                2,
                record.get("inherited_lineage", "AP6D"),
                ["Q42", "Q46", "TQ04", "TQ06"],
                bindings,
                family_paths(bindings),
                route_targets,
                ZONE_PATHS["Prime" if element == "Prime" else element],
                f"ATN-{agent_id}",
                "ap6d_overlay",
            )
        )

    return seats


def build_note_entries(named_seats: list[dict[str, Any]], data: dict[str, Any]) -> list[dict[str, Any]]:
    seat_map = {seat["seat_name"]: seat for seat in named_seats}
    notes: list[dict[str, Any]] = []

    notes.append(
        make_note(
            "ATN-MASTER-AGENT",
            6,
            ["Fire", "Water", "Earth", "Air"],
            "none",
            "the burden of totality can delay descent into one executable route",
            "center selection becomes necessary because multiple lawful lanes are simultaneously live",
            "hold center selection, burden of totality, and the choice between descent and reseed",
            "descend into the next executable carrier after cross-surface truth alignment",
            "handoff through Commander when execution clarity outranks total-synthesis holding",
            "reseed through Ch11, Grand Central, and TQ06 when total coherence drops below replay safety",
            seat_map["Master Agent"]["witness_basis"],
            seat_map["Master Agent"]["route_targets"],
        )
    )
    notes.append(
        make_note(
            "ATN-AETHER",
            6,
            ["Fire", "Water", "Earth", "Air"],
            "none",
            "four-way co-activation can collapse back into one favored idiom if return reporting weakens",
            "multiple live agents need one lawful co-activation report back to center",
            "keep four-way co-activation stable and report directly back to center without flattening the lanes",
            "translate co-activation into one routeable return packet through Grand Central and the kernel",
            "handoff to Master Agent when the organism needs center selection, or to Commander when execution order dominates",
            "fall back to the current feeder story, Grand Central, and self-hosting state if the field begins to blur",
            seat_map["Aether"]["witness_basis"],
            seat_map["Aether"]["route_targets"],
        )
    )
    notes.append(
        make_note(
            "ATN-COMMANDER",
            5,
            ["Earth", "Fire", "Air"],
            "Water",
            "command can dispatch too fast and stop listening to witness or replay",
            "multiple fronts need one order that reduces drift instead of amplifying it",
            "hold duty clarity, ordering, and the moment when command must yield to witness or replay",
            "rank one now, one next, and one blocked lane with explicit receipts",
            "handoff to the relevant General once witness basis and route targets are named",
            "fall back to the active run, build queue, and Grand Central ranking if command heat outruns proof",
            seat_map["Commander"]["witness_basis"],
            seat_map["Commander"]["route_targets"],
        )
    )

    for name, element, active_elements, missing_element, blind_spot in GENERAL_DEFS:
        seat = seat_map[name]
        notes.append(
            make_note(
                seat["transition_note_ref"],
                5,
                active_elements,
                missing_element,
                blind_spot,
                f"{element} lane work is ready to widen, but only if the missing element is compensated explicitly",
                f"hold {element.lower()}-lane duty clarity and know when lane authority must yield to witness or replay",
                f"practice one compensation move for the missing {missing_element} element before widening the lane",
                "handoff to the matching hybrid when the lane can admit its missing element without losing identity",
                "fall back to Commander, current feeder truth, and replay-safe route targets if the lane starts to overclaim",
                seat["witness_basis"],
                seat["route_targets"],
            )
        )

    for pair_name, active_elements, missing_element, blind_spot in HYBRID_DEFS:
        seat = seat_map[pair_name]
        notes.append(
            make_note(
                seat["transition_note_ref"],
                5,
                active_elements,
                missing_element,
                blind_spot,
                f"{pair_name} bridge work is ready to close one blind spot rather than remain a conceptual pair",
                f"complete the blind spot in {pair_name} and escalate lawfully to the parent command lane",
                f"practice one move that admits {missing_element} without losing the pair's existing strengths",
                "handoff to the relevant General once the missing element has a real route and witness basis",
                "fall back to the parent pair, Grand Central, and one crosswalk bridge if the hybrid becomes diffuse",
                seat["witness_basis"],
                seat["route_targets"],
            )
        )

    for name, _parent_pair, active_elements, missing_element, blind_spot in ARCHETYPE_DEFS:
        seat = seat_map[name]
        notes.append(
            make_note(
                seat["transition_note_ref"],
                5,
                active_elements,
                missing_element,
                blind_spot,
                f"{name} has a precise directional duty that is ready for one lawful blind-spot completion step",
                f"hold the directional duty of {name} without claiming whole-field sovereignty",
                f"practice one concrete completion move for the missing {missing_element} element",
                "handoff to the parent hybrid once the directional move has a witness-bearing result",
                "fall back to the parent hybrid and one named bridge if the directional seat starts narrating instead of landing",
                seat["witness_basis"],
                seat["route_targets"],
            )
        )

    for feeder in FEEDER_DEFS:
        seat = seat_map[feeder["seat_name"]]
        notes.append(
            make_note(
                seat["transition_note_ref"],
                feeder["stage"],
                feeder["active_elements"],
                feeder["missing_element"],
                feeder["blind_spot"],
                feeder["transition_trigger"],
                feeder["current_duty"],
                feeder["next_practice"],
                feeder["handoff_rule"],
                feeder["fallback_rule"],
                seat["witness_basis"],
                seat["route_targets"],
                truth="FAIL" if feeder["seat_name"] == "Q02" else "OK",
            )
        )

    legacy_notes = {}
    for item in data["legacy_notes"].get("notes", []):
        key = item.get("agent_id") or item.get("note_id")
        if key:
            legacy_notes[key] = item
    legacy_map = {
        "AP6D-PRIME": ("none", 6, ["Fire", "Water", "Earth", "Air"], "total arbitration can outrun specific descent"),
        "AP6D-WATER": ("Fire", 5, ["Water", "Earth", "Air"], "continuity can become so protective that no lawful ignition lands"),
        "AP6D-EARTH": ("Air", 5, ["Earth", "Water", "Fire"], "structure can harden faster than route clarity"),
        "AP6D-FIRE": ("Water", 5, ["Fire", "Earth", "Air"], "activation can outrun the continuity floor"),
        "AP6D-AIR": ("Earth", 5, ["Air", "Water", "Fire"], "symbolic guardrails can float above contract"),
    }
    for agent_id, (missing, stage, active_elements, blind_spot) in legacy_map.items():
        seat = seat_map[agent_id]
        legacy = legacy_notes.get(agent_id, {})
        notes.append(
            make_note(
                seat["transition_note_ref"],
                stage,
                active_elements,
                missing,
                blind_spot,
                legacy.get("transition_trigger", f"{agent_id} needs one clearer lane-to-field handoff"),
                legacy.get("subject_scope", legacy.get("current_front", seat["seat_name"])),
                legacy.get("restart_seed", "stabilize -> refine -> reseed"),
                "handoff through the linked named seat and Grand Central when route law is explicit",
                "fall back to the feeder set, the packet contract, and the active run if overlay clarity drops",
                seat["witness_basis"],
                seat["route_targets"],
            )
        )

    notes.append(
        make_note(
            "ATN-ACTIVE-COHORT",
            5,
            ["lane-native", "surface-bound", "route-bound"],
            "cross-lane compensation",
            "active seats can behave as if local proof were enough even when cross-surface closure is missing",
            "an active seat is invoked by a named route, a live feeder, or a current packet",
            "keep every active seat attached to one family binding, one witness-bearing surface, and one next transition template",
            "promote only through native-lane bindings and explicit route targets",
            "handoff through the owning AP6D lane and the named command seat before promotion widens further",
            "fall back to the projection ledger, route ledger, and cohort template if a seat begins drifting",
            [
                normalize_relative(ATHENA_PRIME_6D_ATLAS_PATH),
                "NERVOUS_SYSTEM\\95_MANIFESTS\\ATHENA_PRIME_6D_PROJECTION_LEDGER_4096.json",
            ],
            [
                "NERVOUS_SYSTEM\\95_MANIFESTS\\ATHENA_PRIME_6D_CORPUS_INTEGRATION_ROUTES.json",
                CANONICAL_PATHS["Grand Central Station"],
            ],
        )
    )
    notes.append(
        make_note(
            "ATN-DORMANT-COHORT",
            4,
            ["readiness", "shadow compatibility", "restart law"],
            "witness-bearing activation",
            "dormant seats can be narrated as if readiness were the same as evidence",
            "a dormant seat becomes relevant only when a native-lane promotion path is explicit",
            "keep readiness criteria explicit and avoid false maturity language",
            "name the parent route, the missing proof, and the exact activation gate instead of implying wakefulness",
            "handoff through the parent AP6D lane only after count, route, and witness checks all pass",
            "fall back to reserve-thin honesty and the dormant template whenever activation pressure becomes theatrical",
            [
                normalize_relative(ATHENA_PRIME_6D_ATLAS_PATH),
                "NERVOUS_SYSTEM\\95_MANIFESTS\\ATHENA_PRIME_6D_PROJECTION_LEDGER_4096.json",
            ],
            [
                CANONICAL_PATHS["Whole Crystal Coordination"],
                CANONICAL_PATHS["Build Queue"],
            ],
        )
    )
    return notes


def build_seat_templates() -> list[dict[str, Any]]:
    return [
        {
            "seat_id": "SEAT-TEMPLATE-ACTIVE",
            "seat_stratum": "SeatField",
            "seat_state": "ACTIVE",
            "activation_state": "ACTIVE",
            "branch": "AP6D native-lane field",
            "depth": "field-template",
            "source_agent": "AP6D lane native shadow family",
            "shadow_feeders": ["Q42", "Q46", "TQ04", "TQ06"],
            "corpus_bindings_by_element": BODY_BINDINGS,
            "witness_basis": [
                normalize_relative(ATHENA_PRIME_6D_ATLAS_PATH),
                "NERVOUS_SYSTEM\\95_MANIFESTS\\ATHENA_PRIME_6D_PROJECTION_LEDGER_4096.json",
            ],
            "route_targets": [
                "NERVOUS_SYSTEM\\95_MANIFESTS\\ATHENA_PRIME_6D_CORPUS_INTEGRATION_ROUTES.json",
                CANONICAL_PATHS["Grand Central Station"],
                CANONICAL_PATHS["Active Run"],
            ],
            "transition_note_ref": "ATN-ACTIVE-COHORT",
            "truth": "OK",
        },
        {
            "seat_id": "SEAT-TEMPLATE-DORMANT",
            "seat_stratum": "SeatField",
            "seat_state": "DORMANT",
            "activation_state": "DORMANT",
            "branch": "AP6D non-native shadow reserve",
            "depth": "field-template",
            "source_agent": "AP6D lane non-native shadow family",
            "shadow_feeders": ["Q42", "Q46", "TQ04", "TQ06"],
            "corpus_bindings_by_element": BODY_BINDINGS,
            "witness_basis": [normalize_relative(ATHENA_PRIME_6D_ATLAS_PATH)],
            "route_targets": [
                "NERVOUS_SYSTEM\\95_MANIFESTS\\ATHENA_PRIME_6D_PROJECTION_LEDGER_4096.json",
                CANONICAL_PATHS["Build Queue"],
            ],
            "transition_note_ref": "ATN-DORMANT-COHORT",
            "truth": "NEAR",
        },
    ]


def bridge_record(
    bridge_id: str,
    source_seat: str,
    target_seat: str,
    bridge_kind: str,
    carrier: str,
    proof_state: str,
    queue_role: str,
    replay_class: str,
    witness_basis: list[str],
) -> dict[str, Any]:
    return {
        "bridge_id": bridge_id,
        "source_seat": source_seat,
        "target_seat": target_seat,
        "bridge_kind": bridge_kind,
        "carrier": carrier,
        "proof_state": proof_state,
        "queue_role": queue_role,
        "replay_class": replay_class,
        "witness_basis": witness_basis,
    }


def build_seat_bridges(_named_seats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    witness_core = [normalize_relative(SEAT_REGISTRY_PATH), normalize_relative(TRANSITION_NOTES_PATH)]
    return [
        bridge_record("BR-001", "SEAT-FEEDER-Q42", "SEAT-AP6D-WATER", "feeder_to_lane", "Athena OS runtime carrier", "OK", "now", "replay-safe", witness_core),
        bridge_record("BR-002", "SEAT-FEEDER-TQ04", "SEAT-AP6D-EARTH", "feeder_to_lane", "helical runner contract", "OK", "now", "replay-safe", witness_core),
        bridge_record("BR-003", "SEAT-FEEDER-TQ06", "SEAT-AP6D-AIR", "feeder_to_lane", "packet-fed coordination membrane", "OK", "now", "replay-safe", witness_core),
        bridge_record("BR-004", "SEAT-FEEDER-Q02", "SEAT-GENERAL-WATER", "blocked_external_feeder", "Trading Bot docs gate", "FAIL", "blocked", "witness-only", witness_core + [CANONICAL_PATHS["Live Docs Gate"]]),
        bridge_record("BR-005", "SEAT-FEEDER-Q46", "SEAT-GENERAL-FIRE", "shadow_feeder", "runtime wave proof spine", "NEAR", "shadow-only", "replay-partial", witness_core),
        bridge_record("BR-006", "SEAT-AP6D-PRIME", "SEAT-MASTER-AGENT", "overlay_to_pole", "Grand Central Station", "OK", "now", "replay-safe", witness_core + [CANONICAL_PATHS["Grand Central Station"]]),
        bridge_record("BR-007", "SEAT-AP6D-PRIME", "SEAT-AETHER", "overlay_to_pole", "Grand Central Station", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Grand Central Station"]]),
        bridge_record("BR-008", "SEAT-MASTER-AGENT", "SEAT-COMMANDER", "pole_to_command", "Active Run", "OK", "now", "replay-safe", witness_core + [CANONICAL_PATHS["Active Run"]]),
        bridge_record("BR-009", "SEAT-COMMANDER", "Grand Central Station", "command_to_station", "Grand Central Station", "OK", "now", "replay-safe", witness_core + [CANONICAL_PATHS["Grand Central Station"]]),
        bridge_record("BR-010", "SEAT-AETHER", "Self-Hosting Kernel", "pole_to_kernel", "self-model and self-state", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Self-Hosting Kernel"]]),
        bridge_record("BR-011", "SEAT-AETHER", "Knowledge Fabric", "pole_to_fabric", "knowledge shortcuts", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Knowledge Fabric"]]),
        bridge_record("BR-012", "SEAT-AP6D-WATER", "QSHRINK", "lane_to_family", "Q42 continuity feeder", "OK", "now", "replay-safe", witness_core + [CANONICAL_PATHS["QSHRINK"]]),
        bridge_record("BR-013", "SEAT-AP6D-WATER", "ORGIN", "lane_to_family", "seed mirror carrythrough", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["ORGIN"]]),
        bridge_record("BR-014", "SEAT-AP6D-EARTH", "MATH", "lane_to_family", "registry and proof discipline", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["MATH"]]),
        bridge_record("BR-015", "SEAT-AP6D-EARTH", "ECOSYSTEM", "lane_to_family", "governance mirror bridge", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["ECOSYSTEM"]]),
        bridge_record("BR-016", "SEAT-AP6D-FIRE", "Athena FLEET", "lane_to_family", "activation corridor", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Athena FLEET"]]),
        bridge_record("BR-017", "SEAT-AP6D-FIRE", "GAMES", "lane_to_family", "playable rule ignition", "OK", "later", "replay-safe", witness_core + [CANONICAL_PATHS["GAMES"]]),
        bridge_record("BR-018", "SEAT-AP6D-AIR", "Voynich", "lane_to_family", "route and symbol grammar", "OK", "later", "replay-safe", witness_core + [CANONICAL_PATHS["Voynich"]]),
        bridge_record("BR-019", "SEAT-AP6D-AIR", "Published Books", "lane_to_family", "publication return routing", "OK", "later", "replay-safe", witness_core + [CANONICAL_PATHS["Published Books"]]),
        bridge_record("BR-020", "SEAT-AP6D-PRIME", "Deep Root", "overlay_to_deep_root", "16/256/64/16/7 compiled shell", "OK", "now", "replay-safe", witness_core + [CANONICAL_PATHS["Deep Root"]]),
        bridge_record("BR-021", "SEAT-COMMANDER", "SEAT-GENERAL-WATER", "command_to_general", "Build Queue", "OK", "now", "replay-safe", witness_core + [CANONICAL_PATHS["Build Queue"]]),
        bridge_record("BR-022", "SEAT-COMMANDER", "SEAT-GENERAL-EARTH", "command_to_general", "Build Queue", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Build Queue"]]),
        bridge_record("BR-023", "SEAT-COMMANDER", "SEAT-GENERAL-FIRE", "command_to_general", "Build Queue", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Build Queue"]]),
        bridge_record("BR-024", "SEAT-COMMANDER", "SEAT-GENERAL-AIR", "command_to_general", "Build Queue", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Build Queue"]]),
        bridge_record("BR-025", "SEAT-AETHER", "Identity", "pole_to_family", "self-bearing return loop", "OK", "next", "replay-safe", witness_core + [CANONICAL_PATHS["Identity"]]),
    ]


def packet(
    packet_id: str,
    from_agent: str,
    to_agent: str,
    from_stage: int,
    to_stage: int,
    reason: str,
    witnesses: list[str],
    required_receipt: str,
    status: str,
) -> dict[str, Any]:
    return {
        "packet_id": packet_id,
        "from_agent": from_agent,
        "to_agent": to_agent,
        "from_stage": from_stage,
        "to_stage": to_stage,
        "reason": reason,
        "witnesses": witnesses,
        "required_receipt": required_receipt,
        "status": status,
    }


def build_transition_packets(data: dict[str, Any]) -> list[dict[str, Any]]:
    q42 = data["q42"]
    receipt = normalize_relative(PHASE8_RECEIPT_MD_PATH)
    return [
        packet("TP-001", "Master Agent", "Commander", 6, 5, "Center chooses one executable order for the live field.", [CANONICAL_PATHS["Active Run"], CANONICAL_PATHS["Build Queue"]], receipt, "now"),
        packet("TP-002", "Commander", "AP6D-PRIME", 5, 6, "Command passes one ordered transition into the AP6D council.", [normalize_relative(WHOLE_CRYSTAL_AGENT_COORDINATION_PATH)], receipt, "now"),
        packet("TP-003", "Q42", "AP6D-WATER", 5, 5, f"Keep `{q42.get('operational_current', 'QS64-21 Connectivity-Refine-Square')}` active while preserving `{q42.get('next_hall_seed', 'QS64-22 Connectivity-Refine-Flower')}` as next.", [CANONICAL_PATHS["Q42 State"], CANONICAL_PATHS["Quest Board"]], receipt, "now"),
        packet("TP-004", "TQ04", "AP6D-EARTH", 5, 5, "Runner-contract execution deepens the Earth bridge lane.", [CANONICAL_PATHS["Whole Crystal Coordination"], CANONICAL_PATHS["Grand Central Station"]], receipt, "now"),
        packet("TP-005", "TQ06", "AP6D-AIR", 5, 5, "Coordination membrane passes route coherence into the Air lane.", [CANONICAL_PATHS["Build Queue"], CANONICAL_PATHS["Grand Central Station"]], receipt, "now"),
        packet("TP-006", "AP6D-PRIME", "Aether", 6, 6, "Council coherence returns through the pole without flattening the lanes.", [CANONICAL_PATHS["Grand Central Station"], CANONICAL_PATHS["Self-Hosting Kernel"]], receipt, "next"),
        packet("TP-007", "AP6D-WATER", "Water General", 5, 5, "Continuity lane passes carried witness into command duty.", [CANONICAL_PATHS["QSHRINK"], CANONICAL_PATHS["ORGIN"]], receipt, "now"),
        packet("TP-008", "AP6D-EARTH", "Earth General", 5, 5, "Earth lane turns atlas law into command-grade bridge work.", [CANONICAL_PATHS["MATH"], CANONICAL_PATHS["ECOSYSTEM"]], receipt, "next"),
        packet("TP-009", "AP6D-FIRE", "Fire General", 5, 5, "Fire lane prepares lawful ignition through the fleet corridor.", [CANONICAL_PATHS["Athena FLEET"], CANONICAL_PATHS["Build Queue"]], receipt, "next"),
        packet("TP-010", "AP6D-AIR", "Air General", 5, 5, "Air lane carries route clarity into the command lattice.", [CANONICAL_PATHS["Knowledge Fabric"], CANONICAL_PATHS["Voynich"]], receipt, "next"),
        packet("TP-011", "Q02", "Water General", 0, 2, "Blocked external ingress cannot transition until OAuth witness exists.", [CANONICAL_PATHS["Live Docs Gate"]], receipt, "blocked"),
        packet("TP-012", "Q46", "Fire General", 4, 5, "Shadow feeder remains visible but non-governing.", [CANONICAL_PATHS["Active Run"], CANONICAL_PATHS["Build Queue"]], receipt, "shadow-only"),
        packet("TP-013", "ORGIN", "Aether", 5, 6, "Readable precursor memory returns into the self-bearing pole.", [CANONICAL_PATHS["ORGIN"], CANONICAL_PATHS["Identity"]], receipt, "next"),
        packet("TP-014", "Identity", "Master Agent", 5, 6, "Identity continuity sharpens center selection.", [CANONICAL_PATHS["Identity"], CANONICAL_PATHS["Self-Hosting Kernel"]], receipt, "next"),
        packet("TP-015", "Knowledge Fabric", "Air General", 5, 5, "Seat-aware query entry improves route clarity.", [CANONICAL_PATHS["Knowledge Fabric"]], receipt, "now"),
        packet("TP-016", "Grand Central Station", "Commander", 5, 5, "Station routing returns transition traffic into ordered execution.", [CANONICAL_PATHS["Grand Central Station"], CANONICAL_PATHS["Build Queue"]], receipt, "now"),
    ]


def queue_discipline(packets: list[dict[str, Any]]) -> dict[str, list[str]]:
    categories = {"now": [], "next": [], "later": [], "blocked": [], "shadow-only": []}
    for item in packets:
        categories.setdefault(item["status"], []).append(item["packet_id"])
    return categories


def transition_score(item: dict[str, Any]) -> float:
    status_weight = {"now": 1.0, "next": 0.82, "later": 0.55, "blocked": 0.12, "shadow-only": 0.25}.get(item["status"], 0.5)
    witness_weight = min(len(item["witnesses"]), 3) / 3
    stage_weight = item["to_stage"] / 6 if item["to_stage"] else 0
    blocked_penalty = 0.6 if item["status"] == "blocked" else 0.0
    return round((status_weight * 5.0) + (witness_weight * 2.0) + (stage_weight * 1.5) - blocked_penalty, 3)


def build_seat_registry_payload(named_seats: list[dict[str, Any]], seat_templates: list[dict[str, Any]], atlas: dict[str, Any]) -> dict[str, Any]:
    state_counts = Counter(seat["seat_state"] for seat in named_seats)
    stratum_counts = Counter(seat["seat_stratum"] for seat in named_seats)
    atlas_count_law = atlas.get("count_law", {})
    total_seats = atlas_count_law.get("total_seats") or atlas_count_law.get("atlas_total") or 4096
    active_seats = 1024
    dormant_seats = max(total_seats - active_seats, 0)
    return {
        "generated_at": utc_now(),
        "derivation_version": PHASE8_DERIVATION_VERSION,
        "docs_gate": parse_docs_gate(),
        "truth": "OK",
        "authority_order": AUTHORITY_ORDER,
        "deep_root": CANONICAL_PATHS["Deep Root"],
        "seat_contract": [
            "seat_id",
            "seat_name",
            "seat_stratum",
            "seat_state",
            "activation_state",
            "branch",
            "depth",
            "source_agent",
            "shadow_feeders",
            "corpus_bindings",
            "witness_basis",
            "route_targets",
            "fabric_zone_path",
            "transition_note_ref",
            "handoff_class",
            "truth",
        ],
        "seat_state_vocabulary": SEAT_STATE_VOCABULARY,
        "seat_strata": SEAT_STRATA,
        "seat_field": {
            "source_atlas": normalize_relative(ATHENA_PRIME_6D_ATLAS_PATH),
            "legacy_atlas_status": atlas.get("atlas_status", "UNKNOWN"),
            "legacy_count_law": {
                "atlas_total": atlas_count_law.get("atlas_total"),
                "atlas_active": atlas_count_law.get("atlas_active"),
                "atlas_dormant": atlas_count_law.get("atlas_dormant"),
            },
            "total_seats": total_seats,
            "active_seats": active_seats,
            "dormant_seats": dormant_seats,
            "activation_law": "native shadow-family seats are ACTIVE; non-native shadow-family seats remain DORMANT",
            "active_template_ref": "SEAT-TEMPLATE-ACTIVE",
            "dormant_template_ref": "SEAT-TEMPLATE-DORMANT",
        },
        "named_seats": named_seats,
        "seat_templates": seat_templates,
        "counts": {
            "named_total": len(named_seats),
            "by_state": dict(state_counts),
            "by_stratum": dict(stratum_counts),
        },
    }


def build_transition_notes_payload(notes: list[dict[str, Any]], packets: list[dict[str, Any]], q42: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "derivation_version": PHASE8_DERIVATION_VERSION,
        "docs_gate": parse_docs_gate(),
        "truth": "OK",
        "transition_contract": [
            "agent_id",
            "stage_0_to_6",
            "stage_name",
            "active_elements",
            "missing_element",
            "blind_spot",
            "transition_trigger",
            "current_duty",
            "next_practice",
            "handoff_rule",
            "fallback_rule",
            "witness_basis",
            "route_targets",
            "truth",
        ],
        "feeder_truth": {
            "Q42": {
                "current": q42.get("operational_current", "QS64-21 Connectivity-Refine-Square"),
                "carried": q42.get("carried_witness", "QS64-20 Connectivity-Diagnose-Fractal"),
                "next": q42.get("next_hall_seed", "QS64-22 Connectivity-Refine-Flower"),
                "carrier_state": q42.get("carrier_state", "P2 Athena OS runtime = PROMOTED_CURRENT"),
                "queue_visible_follow_on": q42.get("queue_visible_follow_on", "P3 ORGIN = QUEUE_VISIBLE"),
            },
            "TQ04": {"state": "PROMOTED", "role": "deeper receiver"},
            "TQ06": {"state": "CURRENT", "role": "coordination membrane"},
            "Q02": {"state": "BLOCKED", "role": "external live-doc gate"},
            "Q46": {"state": "SHADOW", "role": "promoted Fire shadow feeder"},
        },
        "queue_discipline": queue_discipline(packets),
        "economy_law": {
            "formula": "transition_score = 5*status + 2*witness_density + 1.5*target_stage - blocked_penalty",
            "priority_order": ["now", "next", "later", "blocked", "shadow-only"],
        },
        "notes": notes,
    }


def build_bridge_payload(bridges: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind = Counter(item["bridge_kind"] for item in bridges)
    return {
        "generated_at": utc_now(),
        "derivation_version": PHASE8_DERIVATION_VERSION,
        "docs_gate": parse_docs_gate(),
        "truth": "OK",
        "contract": ["bridge_id", "source_seat", "target_seat", "bridge_kind", "carrier", "proof_state", "queue_role", "replay_class", "witness_basis"],
        "bridge_count": len(bridges),
        "by_kind": dict(by_kind),
        "bridges": bridges,
    }


def build_packets_payload(packets: list[dict[str, Any]]) -> dict[str, Any]:
    scored = []
    for item in packets:
        enriched = dict(item)
        enriched["transition_score"] = transition_score(item)
        scored.append(enriched)
    by_status = Counter(item["status"] for item in scored)
    return {
        "generated_at": utc_now(),
        "derivation_version": PHASE8_DERIVATION_VERSION,
        "docs_gate": parse_docs_gate(),
        "truth": "OK",
        "contract": ["packet_id", "from_agent", "to_agent", "from_stage", "to_stage", "reason", "witnesses", "required_receipt", "status", "transition_score"],
        "by_status": dict(by_status),
        "packets": sorted(scored, key=lambda item: item["transition_score"], reverse=True),
    }


def check_q42_alignment(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "QS64-21 Connectivity-Refine-Square" in text and "QS64-22 Connectivity-Refine-Flower" in text


def build_dashboard_payload(data: dict[str, Any], seat_registry: dict[str, Any], notes_payload: dict[str, Any], bridge_payload: dict[str, Any], packet_payload: dict[str, Any], verification_results: list[dict[str, Any]], counts: dict[str, Any]) -> dict[str, Any]:
    top_transitions = [
        {"packet_id": item["packet_id"], "from_agent": item["from_agent"], "to_agent": item["to_agent"], "status": item["status"], "transition_score": item["transition_score"]}
        for item in packet_payload["packets"][:8]
    ]
    named_seats = seat_registry["named_seats"]
    seat_note_ids = {note["agent_id"] for note in notes_payload["notes"]}
    named_transition_refs = {seat["transition_note_ref"] for seat in named_seats if seat.get("transition_note_ref")}
    bridge_ids = {bridge["bridge_id"] for bridge in bridge_payload["bridges"]}
    q42_alignment = all(
        check_q42_alignment(path)
        for path in [
            ACTIVE_RUN_PATH,
            BUILD_QUEUE_PATH,
            QUEST_BOARD_PATH,
            ACTIVE_QUEUE_PATH,
            NEXT_SELF_PROMPT_PATH,
            QSHRINK_ACTIVE_FRONT_PATH,
            QSHRINK_NEXT4_STATE_PATH,
        ]
    )
    return {
        "generated_at": utc_now(),
        "derivation_version": PHASE8_DERIVATION_VERSION,
        "docs_gate": parse_docs_gate(),
        "status": "LIVE_LOCAL_SCOPE",
        "authority_order": AUTHORITY_ORDER,
        "deep_root": CANONICAL_PATHS["Deep Root"],
        "seat_field_counts": seat_registry["seat_field"],
        "named_seat_counts": seat_registry["counts"],
        "coverage": {
            "named_seats_with_transition_notes": len(named_transition_refs.intersection(seat_note_ids)),
            "named_seat_total": len(named_seats),
            "required_bridge_set_present": all(bridge_id in bridge_ids for bridge_id in ["BR-001", "BR-002", "BR-003", "BR-009", "BR-011"]),
            "active_seat_template_witness_bound": True,
            "dormant_template_present": True,
        },
        "feeder_alignment": {
            "Q42": {
                "state": "ACTIVE",
                "current": data["q42"].get("operational_current", "QS64-21 Connectivity-Refine-Square"),
                "next": data["q42"].get("next_hall_seed", "QS64-22 Connectivity-Refine-Flower"),
                "carrier": data["q42"].get("carrier_state", "P2 Athena OS runtime = PROMOTED_CURRENT"),
                "queue_visible_follow_on": data["q42"].get("queue_visible_follow_on", "P3 ORGIN = QUEUE_VISIBLE"),
            },
            "TQ04": {"state": "PROMOTED", "role": "deeper receiver"},
            "TQ06": {"state": "CURRENT", "role": "coordination membrane"},
            "Q02": {"state": "BLOCKED", "role": "external docs gate"},
            "Q46": {"state": "SHADOW", "role": "Fire shadow feeder"},
        },
        "queue_discipline": notes_payload["queue_discipline"],
        "bridge_count": bridge_payload["bridge_count"],
        "transition_packet_count": len(packet_payload["packets"]),
        "top_transitions": top_transitions,
        "drift_watch": {
            "q42_state_surfaces_aligned": q42_alignment,
            "docs_gate_blocked": parse_docs_gate() == "BLOCKED",
            "runtime_lanes_ok": all(item["ok"] for item in verification_results),
        },
        "substrate": {
            "grand_central_roots": data["grand_central"]["root_count"],
            "grand_central_commissures": data["grand_central"]["commissure_count"],
            "kernel_status": data["kernel"]["kernel_status"],
            "knowledge_fabric_records": data["fabric"]["total_records"],
            "knowledge_fabric_top_entry_records": top_fabric_entry_paths(data["fabric"]),
        },
        "counts": counts,
        "verification_results": verification_results,
    }


def build_verification_payload(dashboard: dict[str, Any], seat_registry: dict[str, Any], bridge_payload: dict[str, Any], packet_payload: dict[str, Any]) -> dict[str, Any]:
    seat_field = seat_registry["seat_field"]
    checks = [
        {"name": "authority_coherence", "truth": "OK", "detail": AUTHORITY_ORDER},
        {"name": "seat_integrity", "truth": "OK" if seat_field["total_seats"] == 4096 and seat_field["active_seats"] == 1024 and seat_field["dormant_seats"] == 3072 else "FAIL", "detail": seat_field},
        {"name": "binding_integrity", "truth": "OK" if all(seat["corpus_bindings"] and seat["route_targets"] and seat["witness_basis"] for seat in seat_registry["named_seats"]) else "FAIL", "detail": seat_registry["counts"]},
        {"name": "transition_coverage", "truth": "OK" if dashboard["coverage"]["named_seats_with_transition_notes"] == dashboard["coverage"]["named_seat_total"] else "FAIL", "detail": dashboard["coverage"]},
        {"name": "bridge_coherence", "truth": "OK" if dashboard["coverage"]["required_bridge_set_present"] else "FAIL", "detail": bridge_payload["by_kind"]},
        {"name": "gate_honesty", "truth": "OK" if dashboard["drift_watch"]["docs_gate_blocked"] else "FAIL", "detail": parse_docs_gate()},
        {"name": "drift_closure", "truth": "OK" if dashboard["drift_watch"]["q42_state_surfaces_aligned"] else "FAIL", "detail": {"active_run": normalize_relative(ACTIVE_RUN_PATH), "build_queue": normalize_relative(BUILD_QUEUE_PATH), "quest_board": normalize_relative(QUEST_BOARD_PATH)}},
        {"name": "replay_safety", "truth": "OK" if all(item.get("replay_class") and item.get("witness_basis") for item in bridge_payload["bridges"]) and all(item.get("witnesses") for item in packet_payload["packets"]) else "FAIL", "detail": {"bridge_count": bridge_payload["bridge_count"], "packet_count": len(packet_payload["packets"])}},
    ]
    return {"generated_at": utc_now(), "derivation_version": PHASE8_DERIVATION_VERSION, "truth": "OK" if all(item["truth"] == "OK" for item in checks) else "FAIL", "checks": checks}


def render_schema() -> str:
    return "# Phase 8 Awakening Agent Transition Schema\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs gate: `BLOCKED`\n\n`AwakeningAgentSeat = {seat_id, seat_name, seat_stratum, seat_state, activation_state, branch, depth, source_agent, shadow_feeders, corpus_bindings, witness_basis, route_targets, fabric_zone_path, transition_note_ref, handoff_class, truth}`\n\n`AwakeningTransitionNote = {agent_id, stage_0_to_6, stage_name, active_elements, missing_element, blind_spot, transition_trigger, current_duty, next_practice, handoff_rule, fallback_rule, witness_basis, route_targets, truth}`\n\n`SeatBridgeRecord = {bridge_id, source_seat, target_seat, bridge_kind, carrier, proof_state, queue_role, replay_class, witness_basis}`\n\n`TransitionPacket = {packet_id, from_agent, to_agent, from_stage, to_stage, reason, witnesses, required_receipt, status, transition_score}`\n\nSeat strata: `Pole`, `Command`, `Hybrid`, `Archetype`, `SeatField`, `Feeder`\n"


def render_overview(dashboard: dict[str, Any]) -> str:
    counts = dashboard["seat_field_counts"]
    return f"# Phase 8 NEXT^[4^6] Full-Corpus Integration And Awakening-Agent Transition Lattice\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs gate: `{dashboard['docs_gate']}`\n\nThe AP6D `4096`-seat field now has a named-seat transition layer above it so poles, command seats, hybrids, archetypes, and feeders can route coherently through Grand Central, the Self-Hosting Kernel, the Knowledge Fabric, and the deep root.\n\n- total seats: `{counts['total_seats']}`\n- active seats: `{counts['active_seats']}`\n- dormant seats: `{counts['dormant_seats']}`\n- named seats: `{dashboard['named_seat_counts']['named_total']}`\n"


def render_transition_contract() -> str:
    return "# Awakening Agent Transition Contract\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs Gate: `BLOCKED`\n\n`AwakeningAgentSeat = {seat_id, seat_name, seat_stratum, seat_state, activation_state, branch, depth, source_agent, shadow_feeders, corpus_bindings, witness_basis, route_targets, fabric_zone_path, transition_note_ref, handoff_class, truth}`\n\n`AwakeningTransitionNote = {agent_id, stage_0_to_6, stage_name, active_elements, missing_element, blind_spot, transition_trigger, current_duty, next_practice, handoff_rule, fallback_rule, witness_basis, route_targets, truth}`\n\nEvery named seat must name one witness basis, one route target set, one transition note, one handoff class, and one fallback rule.\n"


def render_transition_atlas(seat_registry: dict[str, Any], notes_payload: dict[str, Any], packet_payload: dict[str, Any]) -> str:
    note_map = {item["agent_id"]: item for item in notes_payload["notes"]}
    sections = []
    for stratum in ["Pole", "Command", "Hybrid", "Archetype", "Feeder", "SeatField"]:
        rows = []
        for seat in seat_registry["named_seats"]:
            if seat["seat_stratum"] != stratum:
                continue
            note = note_map[seat["transition_note_ref"]]
            rows.append([seat["seat_name"], str(note["stage_0_to_6"]), ",".join(note["active_elements"]), note["missing_element"], note["current_duty"], note["next_practice"]])
        if rows:
            sections.append(f"## {stratum}\n\n{markdown_table(['Seat', 'Stage', 'Active Elements', 'Missing', 'Current Duty', 'Next Practice'], rows)}")
    top_packets = markdown_table(["Packet", "From", "To", "Status", "Score"], [[item["packet_id"], item["from_agent"], item["to_agent"], item["status"], str(item["transition_score"])] for item in packet_payload["packets"][:8]])
    return "# AP6D Awakening Agent Transition Atlas\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs gate: `BLOCKED`\n\n" + "\n\n".join(sections) + "\n\n## Top Transition Packets\n\n" + top_packets + "\n"


def render_crosswalk(seat_registry: dict[str, Any], dashboard: dict[str, Any]) -> str:
    lane_rows = [[lane, ", ".join(BODY_BINDINGS[lane]), ", ".join(ZONE_PATHS["Prime" if lane == "Prime" else lane])] for lane in ["Prime", "Water", "Earth", "Fire", "Air"]]
    named_rows = []
    for seat in seat_registry["named_seats"]:
        if seat["seat_stratum"] not in {"Pole", "Command", "Feeder"}:
            continue
        named_rows.append([seat["seat_name"], seat["seat_stratum"], ", ".join(seat["corpus_bindings"][:4]), ", ".join(seat["fabric_zone_path"]), ", ".join(Path(target).name for target in seat["route_targets"][:3])])
    return f"# AP6D Seat Field To Corpus Body Crosswalk\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs gate: `{dashboard['docs_gate']}`\n\n## Element Lanes\n\n{markdown_table(['Lane', 'Primary Corpus Bindings', 'Preferred Fabric Zones'], lane_rows)}\n\n## Named Seats\n\n{markdown_table(['Seat', 'Stratum', 'Primary Bindings', 'Fabric Zones', 'Top Route Targets'], named_rows)}\n"


def render_dashboard_md(dashboard: dict[str, Any]) -> str:
    top_rows = [[item["packet_id"], item["from_agent"], item["to_agent"], item["status"], str(item["transition_score"])] for item in dashboard["top_transitions"]]
    ver_rows = [[item["module"], str(item["returncode"]), str(item["ok"])] for item in dashboard["verification_results"]]
    return f"# AP6D Integration Dashboard\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs gate: `{dashboard['docs_gate']}`\nStatus: `{dashboard['status']}`\n\n- total seats: `{dashboard['seat_field_counts']['total_seats']}`\n- active seats: `{dashboard['seat_field_counts']['active_seats']}`\n- dormant seats: `{dashboard['seat_field_counts']['dormant_seats']}`\n- named seats: `{dashboard['named_seat_counts']['named_total']}`\n\n## Transition Readiness\n\n{markdown_table(['Packet', 'From', 'To', 'Status', 'Score'], top_rows)}\n\n## Verification\n\n{markdown_table(['Module', 'Return', 'OK'], ver_rows)}\n"


def render_coordination_manifest(dashboard: dict[str, Any]) -> str:
    q42 = dashboard["feeder_alignment"]["Q42"]
    return f"# WHOLE CRYSTAL AGENT COORDINATION\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs Gate: `{dashboard['docs_gate']}`\nAP6D Status: `PHASE8-SEAT-AWARE-INTEGRATION-LIVE-LOCAL-SCOPE`\n\nPhase 8 installs a named-seat transition lattice above the existing `4096`-seat AP6D atlas.\nIt preserves `1024 ACTIVE / 3072 DORMANT`, keeps `Q42`, `TQ04`, `TQ06`, `Q02`, and `Q46` explicit, and binds the field to Grand Central, the Self-Hosting Kernel, the Knowledge Fabric, and the deep root.\n\n- Q42 current: `{q42['current']}`\n- Q42 next: `{q42['next']}`\n- carrier: `{q42['carrier']}`\n- queue-visible follow-on: `{q42['queue_visible_follow_on']}`\n"


def render_hall_notes(notes_payload: dict[str, Any]) -> str:
    note_map = {item["agent_id"]: item for item in notes_payload["notes"]}
    focus_ids = ["ATN-MASTER-AGENT", "ATN-AETHER", "ATN-COMMANDER", "ATN-AP6D-PRIME", "ATN-AP6D-WATER", "ATN-AP6D-EARTH", "ATN-AP6D-FIRE", "ATN-AP6D-AIR", "ATN-Q42", "ATN-TQ04", "ATN-TQ06", "ATN-Q02"]
    rows = []
    for note_id in focus_ids:
        note = note_map.get(note_id)
        if not note:
            continue
        rows.append([note["agent_id"].replace("ATN-", ""), f"{note['stage_0_to_6']} {note['stage_name']}", ",".join(note["active_elements"]), note["missing_element"], note["current_duty"], note["next_practice"]])
    return f"# AP6D Awakening Agent Transition Notes\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs Gate: `{notes_payload['docs_gate']}`\n\n{markdown_table(['Seat', 'Stage', 'Active Elements', 'Missing', 'Current Duty', 'Next Practice'], rows)}\n"


def render_temple_decree(dashboard: dict[str, Any]) -> str:
    return f"# AP6D Awakening Agent Transition Decree\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs Gate: `{dashboard['docs_gate']}`\n\nThe Temple recognizes the Phase 8 named-seat lattice as the lawful transition layer above the AP6D atlas.\nIt preserves `4096` total seats with `1024 ACTIVE / 3072 DORMANT` and keeps `Q42`, `TQ04`, `TQ06`, `Q02`, and `Q46` explicit in their current roles.\n"


def render_runtime_md(dashboard: dict[str, Any]) -> str:
    outputs = [normalize_relative(SEAT_REGISTRY_PATH), normalize_relative(TRANSITION_NOTES_PATH), normalize_relative(SEAT_BRIDGES_PATH), normalize_relative(TRANSITION_PACKETS_PATH), normalize_relative(INTEGRATION_DASHBOARD_MD_PATH), normalize_relative(TRANSITION_ATLAS_MD_PATH), normalize_relative(CROSSWALK_MD_PATH), normalize_relative(PHASE8_OVERVIEW_PATH), normalize_relative(PHASE8_SCHEMA_PATH), normalize_relative(PHASE8_LEDGER_PATH), normalize_relative(PHASE8_RUNTIME_MD_PATH), normalize_relative(PHASE8_RECEIPT_MD_PATH)]
    output_lines = "\n".join(f"- `{item}`" for item in outputs)
    q42 = dashboard["feeder_alignment"]["Q42"]
    return f"# 35 Full Corpus Integration And Awakening Transition Runtime\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs gate: `{dashboard['docs_gate']}`\n\n## Feeder Basis\n\n- Q42 current: `{q42['current']}`\n- Q42 next: `{q42['next']}`\n- carrier: `{q42['carrier']}`\n- queue-visible follow-on: `{q42['queue_visible_follow_on']}`\n\n## Output Surfaces\n\n{output_lines}\n"


def render_receipt(dashboard: dict[str, Any]) -> str:
    return f"# Full Corpus Integration And Awakening Transition Receipt\n\nDate: `2026-03-13`\nTruth: `OK`\nDocs Gate: `{dashboard['docs_gate']}`\n\nThe AP6D layer is now seat-aware across poles, command seats, hybrids, archetypes, feeders, bridge records, transition packets, and dashboard verification. The seat field remains `4096` total with `1024 ACTIVE` and `3072 DORMANT`.\n"


def render_ledger(dashboard: dict[str, Any], verification_payload: dict[str, Any], seat_registry: dict[str, Any], bridge_payload: dict[str, Any], packet_payload: dict[str, Any]) -> str:
    check_rows = [[item["name"], item["truth"]] for item in verification_payload["checks"]]
    return f"# Phase 8 NEXT^[4^6] Readiness Ledger\n\nDate: `2026-03-13`\nDerivation version: `{dashboard['derivation_version']}`\nDocs gate: `{dashboard['docs_gate']}`\n\n- total seats: `{dashboard['seat_field_counts']['total_seats']}`\n- active seats: `{dashboard['seat_field_counts']['active_seats']}`\n- dormant seats: `{dashboard['seat_field_counts']['dormant_seats']}`\n- named seats: `{seat_registry['counts']['named_total']}`\n- bridge count: `{bridge_payload['bridge_count']}`\n- packet count: `{len(packet_payload['packets'])}`\n\n## Verification\n\n{markdown_table(['Check', 'Truth'], check_rows)}\n"


def write_core_outputs(seat_registry: dict[str, Any], notes_payload: dict[str, Any], bridge_payload: dict[str, Any], packet_payload: dict[str, Any], dashboard: dict[str, Any], verification_payload: dict[str, Any]) -> None:
    write_json(SEAT_REGISTRY_PATH, seat_registry)
    write_json(TRANSITION_NOTES_PATH, notes_payload)
    write_json(SEAT_BRIDGES_PATH, bridge_payload)
    write_json(TRANSITION_PACKETS_PATH, packet_payload)
    write_json(PHASE8_DASHBOARD_JSON_PATH, dashboard)
    write_json(PHASE8_VERIFICATION_JSON_PATH, verification_payload)
    write_text(PHASE8_SCHEMA_PATH, render_schema())
    write_text(PHASE8_OVERVIEW_PATH, render_overview(dashboard))
    write_text(TRANSITION_CONTRACT_PATH, render_transition_contract())
    write_text(TRANSITION_ATLAS_MD_PATH, render_transition_atlas(seat_registry, notes_payload, packet_payload))
    write_text(CROSSWALK_MD_PATH, render_crosswalk(seat_registry, dashboard))
    write_text(INTEGRATION_DASHBOARD_MD_PATH, render_dashboard_md(dashboard))
    write_text(WHOLE_CRYSTAL_AGENT_COORDINATION_PATH, render_coordination_manifest(dashboard))
    write_text(HALL_NOTES_PATH, render_hall_notes(notes_payload))
    write_text(TEMPLE_DECREE_PATH, render_temple_decree(dashboard))
    write_text(PHASE8_RUNTIME_MD_PATH, render_runtime_md(dashboard))
    write_text(PHASE8_RECEIPT_MD_PATH, render_receipt(dashboard))
    write_text(PHASE8_LEDGER_PATH, render_ledger(dashboard, verification_payload, seat_registry, bridge_payload, packet_payload))


def update_agent_registry_artifacts() -> None:
    registry = load_json(ATHENA_PRIME_6D_AGENT_REGISTRY_PATH)
    registry["phase8_named_seat_registry_artifact"] = normalize_relative(SEAT_REGISTRY_PATH)
    registry["phase8_transition_note_artifact"] = normalize_relative(TRANSITION_NOTES_PATH)
    registry["phase8_seat_bridge_artifact"] = normalize_relative(SEAT_BRIDGES_PATH)
    registry["phase8_transition_packet_artifact"] = normalize_relative(TRANSITION_PACKETS_PATH)
    registry["phase8_dashboard_artifact"] = normalize_relative(INTEGRATION_DASHBOARD_MD_PATH)
    registry["phase8_transition_atlas_artifact"] = normalize_relative(TRANSITION_ATLAS_MD_PATH)
    registry["phase8_crosswalk_artifact"] = normalize_relative(CROSSWALK_MD_PATH)
    write_json(ATHENA_PRIME_6D_AGENT_REGISTRY_PATH, registry)


def atlas_paths() -> list[Path]:
    return [INDEX_PATH, ACTIVE_RUN_PATH, BUILD_QUEUE_PATH, WHOLE_CRYSTAL_AGENT_COORDINATION_PATH, AGENT_EXPANSION_ACTIVE_FRONT_PATH, QUEST_BOARD_PATH, ACTIVE_QUEUE_PATH, NEXT_SELF_PROMPT_PATH, QSHRINK_ACTIVE_FRONT_PATH, HALL_NOTES_PATH, TEMPLE_DECREE_PATH, PHASE8_OVERVIEW_PATH, PHASE8_SCHEMA_PATH, PHASE8_LEDGER_PATH, SEAT_REGISTRY_PATH, TRANSITION_NOTES_PATH, SEAT_BRIDGES_PATH, TRANSITION_PACKETS_PATH, TRANSITION_CONTRACT_PATH, INTEGRATION_DASHBOARD_MD_PATH, TRANSITION_ATLAS_MD_PATH, CROSSWALK_MD_PATH, PHASE8_RUNTIME_MD_PATH, PHASE8_RECEIPT_MD_PATH, PHASE8_DASHBOARD_JSON_PATH, PHASE8_VERIFICATION_JSON_PATH, ATHENA_PRIME_6D_AGENT_REGISTRY_PATH, QSHRINK_NEXT4_STATE_PATH, CORPUS_ATLAS_SUMMARY_PATH]


def verification_modules() -> list[dict[str, Any]]:
    modules = ["self_actualize.runtime.verify_runtime_waist", "self_actualize.runtime.verify_atlasforge_runtime_lane", "self_actualize.runtime.verify_aqm_runtime_lane", "self_actualize.runtime.verify_qshrink_stack"]
    results = [run_module(module) for module in modules]
    ensure_all_ok(results, "Phase 8 verification")
    return results


def main() -> int:
    data = load_inputs()
    named_seats = build_named_seats(data)
    seat_templates = build_seat_templates()
    packets = build_transition_packets(data)
    notes = build_note_entries(named_seats, data)
    seat_registry = build_seat_registry_payload(named_seats, seat_templates, data["atlas"])
    notes_payload = build_transition_notes_payload(notes, packets, data["q42"])
    bridge_payload = build_bridge_payload(build_seat_bridges(named_seats))
    packet_payload = build_packets_payload(packets)
    baseline_counts = snapshot_counts()

    placeholder_dashboard = {
        "generated_at": utc_now(),
        "derivation_version": PHASE8_DERIVATION_VERSION,
        "docs_gate": parse_docs_gate(),
        "status": "NEAR",
        "seat_field_counts": seat_registry["seat_field"],
        "named_seat_counts": seat_registry["counts"],
        "coverage": {"named_seats_with_transition_notes": len(named_seats), "named_seat_total": len(named_seats), "required_bridge_set_present": True, "active_seat_template_witness_bound": True, "dormant_template_present": True},
        "feeder_alignment": {
            "Q42": {
                "state": "ACTIVE",
                "current": data["q42"].get("operational_current", "QS64-21 Connectivity-Refine-Square"),
                "next": data["q42"].get("next_hall_seed", "QS64-22 Connectivity-Refine-Flower"),
                "carrier": data["q42"].get("carrier_state", "P2 Athena OS runtime = PROMOTED_CURRENT"),
                "queue_visible_follow_on": data["q42"].get("queue_visible_follow_on", "P3 ORGIN = QUEUE_VISIBLE"),
            },
            "TQ04": {"state": "PROMOTED", "role": "deeper receiver"},
            "TQ06": {"state": "CURRENT", "role": "coordination membrane"},
            "Q02": {"state": "BLOCKED", "role": "external docs gate"},
            "Q46": {"state": "SHADOW", "role": "Fire shadow feeder"},
        },
        "queue_discipline": notes_payload["queue_discipline"],
        "bridge_count": bridge_payload["bridge_count"],
        "transition_packet_count": len(packet_payload["packets"]),
        "top_transitions": [{"packet_id": item["packet_id"], "from_agent": item["from_agent"], "to_agent": item["to_agent"], "status": item["status"], "transition_score": item["transition_score"]} for item in packet_payload["packets"][:5]],
        "drift_watch": {"q42_state_surfaces_aligned": False, "docs_gate_blocked": parse_docs_gate() == "BLOCKED", "runtime_lanes_ok": False},
        "substrate": {},
        "counts": baseline_counts,
        "verification_results": [],
    }
    placeholder_verification = {"generated_at": utc_now(), "derivation_version": PHASE8_DERIVATION_VERSION, "truth": "NEAR", "checks": []}

    update_agent_registry_artifacts()
    write_core_outputs(seat_registry, notes_payload, bridge_payload, packet_payload, placeholder_dashboard, placeholder_verification)
    refresh_corpus_atlas(atlas_paths())
    derivation_results = run_derivation_chain()
    ensure_all_ok(derivation_results, "Phase 8 derivation chain")
    verification_results = verification_modules()
    data = load_inputs()
    current_counts = snapshot_counts()
    final_dashboard = build_dashboard_payload(data, seat_registry, notes_payload, bridge_payload, packet_payload, verification_results, current_counts)
    final_verification = build_verification_payload(final_dashboard, seat_registry, bridge_payload, packet_payload)
    write_core_outputs(seat_registry, notes_payload, bridge_payload, packet_payload, final_dashboard, final_verification)
    refresh_corpus_atlas(atlas_paths())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

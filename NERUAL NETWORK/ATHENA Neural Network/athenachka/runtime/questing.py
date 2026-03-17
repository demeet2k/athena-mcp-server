from __future__ import annotations

from dataclasses import asdict

from ..contracts import QuestPacket


ORGAN_DOMAINS = ["Core", "Crystal", "Helix", "ImmuneAppendix"]
WORKSTREAMS = ["Contracts", "Runtime", "Verification", "Writeback"]
LENSES = ["Fire", "Water", "Air", "Earth"]
MOVES = ["Diagnose", "Refine", "Synthesize", "Scale"]

SURFACES = ["Kernel", "Crystal", "Hall", "Runtime"]
WITNESSES = ["direct", "derived", "blocked", "receipt"]
PHASES = ["seed", "synthesis", "audit", "lift"]
WAVES = ["wave1", "wave2", "wave3", "wave4"]

ARTIFACTS = ["module", "manifest", "receipt", "test"]
CONTRACTS = ["truth", "replay", "quest", "appendix"]
LANES = ["fast", "full", "promotion", "maintenance"]
VERIFY = ["lint", "import", "runtime", "parity"]

OWNERS = ["Guildmaster", "PodLead", "Auditor", "Steward"]
STATUSES = ["ACTIVE", "PARKED", "QUEUED", "BLOCKED"]
WRITEBACKS = ["board", "runtime", "family", "manifest"]
RESTARTS = ["same_wave", "next_wave", "hall_seed", "replay_seed"]

CURRENT_WAVE_ID = "Q50-wave7"

AGENT_POLICY = {
    "guildmaster": 1,
    "elemental_pod_leads": 4,
    "controller_auditors": 4,
    "verification_replay_stewards": 4,
    "appendix_service_stewards": 4,
    "guildmaster_active_claims": 0,
    "max_live_claims_per_wave": 16,
    "max_parked_frontier_packets": 64,
}

MOVE_OWNER_GROUP = {
    "Diagnose": "elemental_pod_leads",
    "Refine": "controller_auditors",
    "Synthesize": "verification_replay_stewards",
    "Scale": "appendix_service_stewards",
}

OWNER_IDENTITIES = {
    "elemental_pod_leads": {
        "Fire": "fire",
        "Water": "water",
        "Air": "air",
        "Earth": "earth",
    },
    "controller_auditors": {
        "Fire": "01",
        "Water": "02",
        "Air": "03",
        "Earth": "04",
    },
    "verification_replay_stewards": {
        "Fire": "01",
        "Water": "02",
        "Air": "03",
        "Earth": "04",
    },
    "appendix_service_stewards": {
        "Fire": "01",
        "Water": "02",
        "Air": "03",
        "Earth": "04",
    },
}

WITNESS_TARGETS = {
    "Diagnose": "truth_witness_snapshot",
    "Refine": "replay_comparison",
    "Synthesize": "full_path_replay",
    "Scale": "parity_summary",
}

WAVE_SPECS = {
    "Q44-wave1": {
        "quest_front": "Q44",
        "wave_title": "Core::Contracts",
        "packet_ids": [f"Q43-{index:03d}" for index in range(1, 17)],
        "restart_seed_on_success": "Q45 -> Wave2/Crystal.Contracts.Fire.Diagnose",
    },
    "Q45-wave2": {
        "quest_front": "Q45",
        "wave_title": "Crystal::Contracts",
        "packet_ids": [f"Q43-{index:03d}" for index in range(65, 81)],
        "restart_seed_on_success": "Q46 -> Wave3/Helix.Contracts.Fire.Diagnose",
    },
    "Q46-wave3": {
        "quest_front": "Q46",
        "wave_title": "Helix::Contracts",
        "packet_ids": [f"Q43-{index:03d}" for index in range(129, 145)],
        "restart_seed_on_success": "Q47 -> Wave4/ImmuneAppendix.Contracts.Fire.Diagnose",
    },
    "Q47-wave4": {
        "quest_front": "Q47",
        "wave_title": "ImmuneAppendix::Contracts",
        "packet_ids": [f"Q43-{index:03d}" for index in range(193, 209)],
        "restart_seed_on_success": "Q48 -> Wave5/Core.Runtime.Fire.Diagnose",
    },
    "Q48-wave5": {
        "quest_front": "Q48",
        "wave_title": "Core::Runtime",
        "packet_ids": [f"Q43-{index:03d}" for index in range(17, 33)],
        "restart_seed_on_success": "Q49 -> Wave6/Crystal.Runtime.Fire.Diagnose",
    },
    "Q49-wave6": {
        "quest_front": "Q49",
        "wave_title": "Crystal::Runtime",
        "packet_ids": [f"Q43-{index:03d}" for index in range(81, 97)],
        "restart_seed_on_success": "Q50 -> Wave7/Helix.Runtime.Fire.Diagnose",
    },
    "Q50-wave7": {
        "quest_front": "Q50",
        "wave_title": "Helix::Runtime",
        "packet_ids": [f"Q43-{index:03d}" for index in range(145, 161)],
        "restart_seed_on_success": "Q51 -> Wave8/ImmuneAppendix.Runtime.Fire.Diagnose",
    },
}


def _axis_catalog(axis: str, values1: list[str], values2: list[str], values3: list[str], values4: list[str]) -> list[dict[str, object]]:
    catalog: list[dict[str, object]] = []
    index = 1
    for value1 in values1:
        for value2 in values2:
            for value3 in values3:
                for value4 in values4:
                    catalog.append(
                        {
                            "axis": axis,
                            "index": index,
                            "address": f"{axis}{index:03d}",
                            "v1": value1,
                            "v2": value2,
                            "v3": value3,
                            "v4": value4,
                        }
                    )
                    index += 1
    return catalog


def _packet_index(quest_id: str) -> int:
    return int(quest_id.split("-")[1])


def _target_surfaces(domain: str) -> list[str]:
    mapping = {
        "Core": [
            "ATHENA Neural Network/athenachka/core/",
            "ATHENA Neural Network/athena_neural_network.py",
        ],
        "Crystal": [
            "ATHENA Neural Network/athenachka/crystal/",
            "ATHENA Neural Network/athenachka/appendix/",
        ],
        "Helix": [
            "ATHENA Neural Network/athenachka/helix/",
            "ATHENA Neural Network/athenachka/runtime/",
        ],
        "ImmuneAppendix": [
            "ATHENA Neural Network/athenachka/immune/",
            "ATHENA Neural Network/athenachka/appendix/",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/",
        ],
    }
    return mapping[domain]


def _select_parked_packet_ids(packet_ids: list[str], active_ids: set[str], max_parked: int) -> set[str]:
    ordered_packet_ids = sorted(packet_ids, key=_packet_index)
    active_max_index = max(_packet_index(packet_id) for packet_id in active_ids)
    tail = [
        packet_id
        for packet_id in ordered_packet_ids
        if _packet_index(packet_id) > active_max_index and packet_id not in active_ids
    ]
    head = [
        packet_id
        for packet_id in ordered_packet_ids
        if _packet_index(packet_id) <= active_max_index and packet_id not in active_ids
    ]
    return set((tail + head)[:max_parked])


def build_leaf_packets() -> tuple[list[QuestPacket], dict[str, list[dict[str, object]]]]:
    a_catalog = _axis_catalog("A", ORGAN_DOMAINS, WORKSTREAMS, LENSES, MOVES)
    b_catalog = _axis_catalog("B", SURFACES, WITNESSES, PHASES, WAVES)
    c_catalog = _axis_catalog("C", ARTIFACTS, CONTRACTS, LANES, VERIFY)
    d_catalog = _axis_catalog("D", OWNERS, STATUSES, WRITEBACKS, RESTARTS)

    packets: list[QuestPacket] = []
    for idx, a_node in enumerate(a_catalog):
        b_node = b_catalog[idx]
        c_node = c_catalog[idx]
        d_node = d_catalog[idx]
        domain = str(a_node["v1"])
        packets.append(
            QuestPacket(
                quest_id=f"Q43-{idx + 1:03d}",
                address_a256_b256_c256_d256=".".join(
                    [str(a_node["address"]), str(b_node["address"]), str(c_node["address"]), str(d_node["address"])]
                ),
                objective=f"{domain}::{a_node['v2']}::{a_node['v3']}::{a_node['v4']}",
                target_surfaces=_target_surfaces(domain),
                witness_needed=f"{b_node['v2']}::{b_node['v3']}::{c_node['v4']}",
                writeback=f"{d_node['v3']}::{d_node['v4']}",
                restart_seed=f"{a_node['address']}->{d_node['v4']}",
                status="QUEUED",
                owner_class=str(d_node["v1"]),
            )
        )

    return packets, {"A": a_catalog, "B": b_catalog, "C": c_catalog, "D": d_catalog}


def build_macro_quest_bundle(current_wave_id: str = CURRENT_WAVE_ID) -> dict[str, object]:
    if current_wave_id not in WAVE_SPECS:
        raise KeyError(f"Unknown wave id: {current_wave_id}")

    packets, axis_catalog = build_leaf_packets()
    packet_dicts = [asdict(packet) for packet in packets]
    all_packet_ids = [packet["quest_id"] for packet in packet_dicts]
    active_ids = set(WAVE_SPECS[current_wave_id]["packet_ids"])
    parked_ids = _select_parked_packet_ids(
        all_packet_ids,
        active_ids=active_ids,
        max_parked=AGENT_POLICY["max_parked_frontier_packets"],
    )

    for packet in packet_dicts:
        quest_id = packet["quest_id"]
        if quest_id in active_ids:
            packet["status"] = "ACTIVE"
        elif quest_id in parked_ids:
            packet["status"] = "PARKED"
        else:
            packet["status"] = "QUEUED"

    active_packets = [packet for packet in packet_dicts if packet["status"] == "ACTIVE"]
    parked_packets = [packet for packet in packet_dicts if packet["status"] == "PARKED"]
    queued_packets = [packet for packet in packet_dicts if packet["status"] == "QUEUED"]
    wave_activation = build_wave_activation_overlay(packet_dicts, wave_id=current_wave_id)

    return {
        "macro_quest": {
            "quest_id": "Q43",
            "title": "Bootstrap Athenachka Organism v0",
            "objective": "Integrate core, crystal, helix, immune shell, and Guild Hall quest membrane into one executable organism.",
            "waves": {
                "wave1": "kernel extraction and typed result contract",
                "wave2": "elemental lanes and pairwise fusion",
                "wave3": "six-channel state and loop controller",
                "wave4": "immune shell and appendices",
                "wave5": "Hall writeback, replay, and lift",
                "wave6": "self-repair scaffolding and regeneration gates",
                "wave7": "helix runtime activation",
            },
        },
        "agent_policy": dict(AGENT_POLICY),
        "current_wave_id": current_wave_id,
        "wave_specs": {
            wave_id: {
                "quest_front": spec["quest_front"],
                "wave_title": spec["wave_title"],
                "packet_ids": list(spec["packet_ids"]),
                "restart_seed_on_success": spec["restart_seed_on_success"],
            }
            for wave_id, spec in WAVE_SPECS.items()
        },
        "address_schema": axis_catalog,
        "packets": packet_dicts,
        "active_packets": active_packets,
        "parked_packets": parked_packets,
        "queued_packets": queued_packets,
        "wave_activation": wave_activation,
    }


def build_wave_activation_overlay(packets: list[dict[str, object]], wave_id: str = CURRENT_WAVE_ID) -> dict[str, object]:
    if wave_id not in WAVE_SPECS:
        raise KeyError(f"Unknown wave id: {wave_id}")

    packet_by_id = {packet["quest_id"]: packet for packet in packets}
    spec = WAVE_SPECS[wave_id]
    assignments: list[dict[str, object]] = []
    owner_summary = {
        "guildmaster": {"coordinator_only": True, "active_claims": 0},
        "elemental_pod_leads": {"active_claims": 0},
        "controller_auditors": {"active_claims": 0},
        "verification_replay_stewards": {"active_claims": 0},
        "appendix_service_stewards": {"active_claims": 0},
    }

    for quest_id in spec["packet_ids"]:
        packet = dict(packet_by_id[quest_id])
        domain, workstream, element, move = packet["objective"].split("::")
        owner_group = MOVE_OWNER_GROUP[move]
        owner_id = OWNER_IDENTITIES[owner_group][element]
        packet["owner_group"] = owner_group
        packet["owner_id"] = owner_id
        packet["domain"] = domain
        packet["workstream"] = workstream
        packet["element"] = element
        packet["move"] = move
        packet["witness_target"] = WITNESS_TARGETS[move]
        packet["execution_contract"] = move.lower()
        packet["wave_status"] = "ASSIGNED"
        owner_summary[owner_group]["active_claims"] += 1
        assignments.append(packet)

    assignments.sort(key=lambda item: item["quest_id"])
    return {
        "wave_id": wave_id,
        "quest_front": spec["quest_front"],
        "wave_title": spec["wave_title"],
        "coordinator": "guildmaster",
        "restart_seed_on_success": spec["restart_seed_on_success"],
        "owner_summary": owner_summary,
        "packet_ids": list(spec["packet_ids"]),
        "assignments": assignments,
    }

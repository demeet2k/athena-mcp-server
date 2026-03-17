from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from derive_hsigma_mapping_hologram import (
    ASTRO_LANE_BUNDLES,
    HSIGMA_WITNESS_PATH,
    aggregate_bundle_state,
    ensure_hsigma_artifacts,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"
LEDGER_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "90_LEDGERS" / "astrological_schedulers"
JSON_OUTPUT_PATH = SELF_ACTUALIZE_ROOT / "astrological_scheduler_packets.json"
REGISTRY_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ASTROLOGICAL_SCHEDULER_REGISTRY.md"
PACKET_INDEX_PATH = LEDGER_ROOT / "00_PACKET_INDEX.md"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
CREDENTIALS_PATH = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
TOKEN_PATH = WORKSPACE_ROOT / "Trading Bot" / "token.json"
TIMEZONE = ZoneInfo("America/Los_Angeles")

MASTER_ROLES = ["Synthesizer", "Planner", "Worker", "Pruner"]
VARIANT_OFFSETS = {"direct": 0, "inverse": 6, "rot90": 3, "rot90_inverse": 9}
ACTIVE_ANCHOR_IDS = {"western_solar12", "planetary_office", "chinese_cycle", "vedic_lunar"}
ACTIVE_ROTATION_IDS = {"mayan_calendar", "decan_office"}
COMPILED_SHADOW_IDS = {"egyptian_kheper", "norse_rune_yggdrasil"}
FAST_LANE_IDS = {"western_solar12", "planetary_office", "chinese_cycle", "decan_office", "egyptian_kheper"}
ACTIVE_ROTATION_ORDER = ["mayan_calendar", "decan_office", "egyptian_kheper", "norse_rune_yggdrasil"]

WESTERN_SEATS = [
    ("Aries", "Fire", "Cardinal"),
    ("Taurus", "Earth", "Fixed"),
    ("Gemini", "Air", "Mutable"),
    ("Cancer", "Water", "Cardinal"),
    ("Leo", "Fire", "Fixed"),
    ("Virgo", "Earth", "Mutable"),
    ("Libra", "Air", "Cardinal"),
    ("Scorpio", "Water", "Fixed"),
    ("Sagittarius", "Fire", "Mutable"),
    ("Capricorn", "Earth", "Cardinal"),
    ("Aquarius", "Air", "Fixed"),
    ("Pisces", "Water", "Mutable"),
]
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
WEEKDAY_RULERS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
PLANETARY_SHARED12 = {
    "Saturn": [9, 10],
    "Jupiter": [8, 11],
    "Mars": [0, 7],
    "Sun": [4],
    "Venus": [1, 6],
    "Mercury": [2, 5],
    "Moon": [3],
}
DOUBLE_HOUR_GATES = [
    ("Zi", "Rat", "Water"),
    ("Chou", "Ox", "Earth"),
    ("Yin", "Tiger", "Wood"),
    ("Mao", "Rabbit", "Wood"),
    ("Chen", "Dragon", "Earth"),
    ("Si", "Snake", "Fire"),
    ("Wu", "Horse", "Fire"),
    ("Wei", "Goat", "Earth"),
    ("Shen", "Monkey", "Metal"),
    ("You", "Rooster", "Metal"),
    ("Xu", "Dog", "Earth"),
    ("Hai", "Pig", "Water"),
]
EGYPTIAN_PHASES = ["becoming", "testing", "judgment", "renewal"]
NORSE_RUNES = [
    "Fehu", "Uruz", "Thurisaz", "Ansuz", "Raidho", "Kenaz", "Gebo", "Wunjo",
    "Hagalaz", "Nauthiz", "Isa", "Jera", "Eihwaz", "Perthro", "Algiz", "Sowilo",
    "Tiwaz", "Berkano", "Ehwaz", "Mannaz", "Laguz", "Ingwaz", "Dagaz", "Othala",
]
NORSE_WORLDS = [
    "Asgard", "Vanaheim", "Alfheim", "Midgard", "Jotunheim",
    "Svartalfheim", "Niflheim", "Muspelheim", "Helheim",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def local_now() -> datetime:
    return datetime.now(TIMEZONE)


def docs_blocked() -> bool:
    return not CREDENTIALS_PATH.exists() or not TOKEN_PATH.exists()


def next_hour_boundary(now: datetime) -> datetime:
    return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def next_two_hour_boundary(now: datetime) -> datetime:
    base = now.replace(minute=0, second=0, microsecond=0)
    return base + timedelta(hours=(2 - (now.hour % 2)) % 2 or 2)


def next_midnight(now: datetime) -> datetime:
    return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def next_watch_boundary(now: datetime) -> datetime:
    if now.hour < 6:
        return now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now.hour < 18:
        return now.replace(hour=18, minute=0, second=0, microsecond=0)
    return (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)


def transition_text(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def json_string(value: object) -> str:
    return value if isinstance(value, str) else json.dumps(value, sort_keys=True)


def shared12_descriptor(index: int) -> str:
    seat, element, modality = WESTERN_SEATS[index % 12]
    return f"S{index + 1:02d} / {seat} / {element} / {modality}"


def variant_indexes(index: int) -> dict[str, int]:
    return {name: (index + offset) % 12 for name, offset in VARIANT_OFFSETS.items()}


def variant_bundle(index: int) -> dict[str, str]:
    return {name: shared12_descriptor(value) for name, value in variant_indexes(index).items()}


def role_vector(synth: int, planner: int, worker: int, pruner: int) -> dict[str, int]:
    return {"Synthesizer": synth, "Planner": planner, "Worker": worker, "Pruner": pruner}


def lane_state_payload(system_id: str) -> dict[str, object]:
    if system_id in ACTIVE_ANCHOR_IDS:
        return {"lane_state": "ACTIVE_ANCHOR", "rotation_group": "anchor", "active_master_role_count": 4, "activation_gate": "pre-G4 anchor lane", "unserved_lane_age": 0}
    if system_id in ACTIVE_ROTATION_IDS:
        return {"lane_state": "ACTIVE_ROTATION", "rotation_group": "cultural", "active_master_role_count": 4, "activation_gate": "pre-G4 active cultural lane", "unserved_lane_age": ACTIVE_ROTATION_ORDER.index(system_id)}
    return {"lane_state": "COMPILED_SHADOW", "rotation_group": "cultural", "active_master_role_count": 0, "activation_gate": "compiled shadow until promotion gate", "unserved_lane_age": ACTIVE_ROTATION_ORDER.index(system_id)}


def speed_class(system_id: str) -> str:
    return "fast" if system_id in FAST_LANE_IDS else "slow"


def liminal_tag(system_id: str, now: datetime, seat_index: int, lane_state: str) -> str:
    return f"LIMINAL::{system_id.upper()}::{lane_state}::S{seat_index + 1:02d}::{now.strftime('%Y%m%dT%H%M%S%z')}"


def spawn_envelope_seed(system_id: str, lane_state: str, active_count: int, seat_index: int, native_gate: str) -> dict[str, object]:
    return {
        "agent_id_pattern": f"{system_id}.{{role}}.{{loop_id}}.S{seat_index + 1:02d}",
        "lane_id": system_id,
        "role_ids": MASTER_ROLES,
        "active_master_role_count": active_count,
        "activation_state": lane_state,
        "shared12_seat": shared12_descriptor(seat_index),
        "native_gate": native_gate,
        "writeback_targets": ["Hall", "Temple", "Queue", "Manifest", "Restart"],
    }


def resolution_band(*layers: str) -> dict[str, object]:
    return {"native_ladder": list(layers), "cross_resolution_ladder": ["hour", "watch", "day", "month", "year", "precession", "GreatYear"]}


def long_wave_context(now: datetime) -> dict[str, object]:
    return {
        "calendar_year": now.year,
        "precession_sector": f"S{((now.year - 1) % 12) + 1:02d}",
        "great_year_turn": ((now.year - 1) % 25920) + 1,
        "truth": "structural surrogate only",
    }


def decorate_packet(now: datetime, packet: dict[str, object], seat_index: int, lane_flavor: str, role_weights: dict[str, int], projection_witness: str, resolution: dict[str, object]) -> tuple[dict[str, object], dict[str, int]]:
    system_id = str(packet["system_id"])
    native_gate = str(packet["current_gate"])
    state = lane_state_payload(system_id)
    packet["native_gate"] = native_gate
    packet["shared12_seat"] = shared12_descriptor(seat_index)
    packet["projection_witness"] = projection_witness
    packet["variant_set"] = variant_bundle(seat_index)
    packet["role_weight_vector"] = role_weights
    packet["resolution_band"] = resolution
    packet["lane_flavor"] = lane_flavor
    packet["lane_state"] = state["lane_state"]
    packet["rotation_group"] = state["rotation_group"]
    packet["activation_gate"] = state["activation_gate"]
    packet["active_master_role_count"] = state["active_master_role_count"]
    packet["master_roles"] = MASTER_ROLES
    packet["speed_class"] = speed_class(system_id)
    packet["liminal_tag"] = liminal_tag(system_id, now, seat_index, str(state["lane_state"]))
    packet["spawn_envelope_seed"] = spawn_envelope_seed(system_id, str(state["lane_state"]), int(state["active_master_role_count"]), seat_index, native_gate)
    packet["nexus_score"] = 0
    packet["unserved_lane_age"] = state["unserved_lane_age"]
    return packet, variant_indexes(seat_index)


def western_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    seat_index = now.hour % 12
    seat, element, modality = WESTERN_SEATS[seat_index]
    frontier_map = {"Cardinal": ("Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "initiate alignment and front selection"), "Fixed": ("TQ04 runner-contract binding", "high-priest-totality", "stabilize law and hold witness"), "Mutable": ("Q42 QSHRINK corridor followthrough", "corpus-weave", "adapt routes and redistribute pressure")}
    weights = {"Cardinal": role_vector(20, 35, 30, 15), "Fixed": role_vector(20, 20, 25, 35), "Mutable": role_vector(35, 20, 25, 20)}
    frontier, handoff, bias = frontier_map[modality]
    item = {"title": "Western Solar12 Packet", "owner": "astro-western-wheel", "path": LEDGER_ROOT / "western_solar12_packet.md", "packet": {"system_id": "western_solar12", "clock_mode": "hourly structural zodiac wheel", "native_cycle": "Solar12 / 4x3 archetype wheel", "current_gate": f"{seat} / {element} / {modality}", "next_transition": transition_text(next_hour_boundary(now)), "action_bias": bias, "cautions": "Structural scheduler only; not live ephemeris. Docs gate remains blocked." if blocked else "Structural scheduler only; not live ephemeris.", "suggested_frontier": frontier, "handoff_target": handoff, "blocker_truth": "BLOCKED" if blocked else "OPEN", "seat": seat, "element": element, "modality": modality, "witness": f"Derived from local hour {now.hour:02d} in America/Los_Angeles using the fixed Solar12 seat order."}}
    item["packet"], variants = decorate_packet(now, item["packet"], seat_index, "Hourly 12-seat executive archetype wheel with modality-weighted spawn emphasis.", weights[modality], f"Native Solar12 seat {seat} projects directly onto {shared12_descriptor(seat_index)}.", resolution_band("hour", "day", "month", "year", "precession", "GreatYear"))
    return item, variants


def planetary_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    weekday_ruler = WEEKDAY_RULERS[now.weekday()]
    start_index = CHALDEAN_ORDER.index(weekday_ruler)
    hour_ruler = CHALDEAN_ORDER[(start_index + now.hour) % len(CHALDEAN_ORDER)]
    frontier_map = {"Saturn": ("TQ04 runner-contract binding", "high-priest-totality", "contract, audit, and harden the control plane"), "Jupiter": ("Q44 organism wave proof", "athena-weave-scan", "expand law and promote coherent growth"), "Mars": ("Q42 QSHRINK corridor followthrough", "qshrink-shiva", "cut through drift and execute the sharpest frontier"), "Sun": ("Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "centralize the current front and make it legible"), "Venus": ("Q35 ORGIN mirrored seed corpus", "corpus-weave", "harmonize routes and increase bridge density"), "Mercury": ("Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "mediate, route, and clarify handoffs"), "Moon": ("Q35 ORGIN mirrored seed corpus", "high-priest-totality", "reflect, archive, and preserve continuity")}
    weights = {"Saturn": role_vector(20, 25, 15, 40), "Jupiter": role_vector(20, 30, 35, 15), "Mars": role_vector(10, 20, 50, 20), "Sun": role_vector(20, 35, 30, 15), "Venus": role_vector(25, 20, 20, 35), "Mercury": role_vector(35, 30, 20, 15), "Moon": role_vector(35, 20, 10, 35)}
    seat_index = PLANETARY_SHARED12[hour_ruler][(now.hour + now.weekday()) % len(PLANETARY_SHARED12[hour_ruler])]
    frontier, handoff, bias = frontier_map[hour_ruler]
    item = {"title": "Planetary Office Packet", "owner": "astro-planetary-office", "path": LEDGER_ROOT / "planetary_office_packet.md", "packet": {"system_id": "planetary_office", "clock_mode": "hourly planetary office", "native_cycle": "PlanetaryHour / Septenary / weekday ruler", "current_gate": f"{weekday_ruler} weekday / {hour_ruler} hour", "next_transition": transition_text(next_hour_boundary(now)), "action_bias": bias, "cautions": "Civil-hour structural surrogate only; not sunrise-based ephemeris. Docs gate remains blocked." if blocked else "Civil-hour structural surrogate only; not sunrise-based ephemeris.", "suggested_frontier": frontier, "handoff_target": handoff, "blocker_truth": "BLOCKED" if blocked else "OPEN", "weekday_ruler": weekday_ruler, "hour_ruler": hour_ruler, "septenary_order": " -> ".join(CHALDEAN_ORDER), "witness": f"Derived from local weekday {now.strftime('%A')} and civil hour {now.hour:02d} with the Chaldean order as a structural surrogate."}}
    item["packet"], variants = decorate_packet(now, item["packet"], seat_index, "Hourly septenary governance lane with a traditional shared-12 rulership adapter.", weights[hour_ruler], f"Hour ruler {hour_ruler} maps through the traditional rulership adapter onto {shared12_descriptor(seat_index)}.", resolution_band("hour", "weekday", "month", "year", "precession", "GreatYear"))
    return item, variants


def chinese_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    gate_index = ((now.hour + 1) // 2) % 12
    stem, animal, element = DOUBLE_HOUR_GATES[gate_index]
    overlay = (now.date().toordinal() % 60) + 1
    frontier_map = {"Wood": ("Q44 organism wave proof", "athena-weave-scan", "grow, branch, and seed neglected routes"), "Fire": ("Q42 QSHRINK corridor followthrough", "qshrink-shiva", "ignite decisive motion and expose weak joints"), "Earth": ("Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "stabilize the center and coordinate the hub"), "Metal": ("Q42 QSHRINK corridor followthrough", "qshrink-shiva", "audit, prune, and sharpen corridor law"), "Water": ("Q35 ORGIN mirrored seed corpus", "corpus-weave", "deepen memory, mirror witness, and restore flow")}
    weights = {"Wood": role_vector(30, 20, 35, 15), "Fire": role_vector(15, 20, 45, 20), "Earth": role_vector(20, 35, 25, 20), "Metal": role_vector(20, 20, 20, 40), "Water": role_vector(35, 20, 15, 30)}
    frontier, handoff, bias = frontier_map[element]
    item = {"title": "Chinese Cycle Packet", "owner": "astro-chinese-cycle", "path": LEDGER_ROOT / "chinese_cycle_packet.md", "packet": {"system_id": "chinese_cycle", "clock_mode": "two-hour Chinese double-hour lane", "native_cycle": "Wu Xing + DoubleHour + Chinese60", "current_gate": f"{stem} / {animal} / {element}", "next_transition": transition_text(next_two_hour_boundary(now)), "action_bias": bias, "cautions": "Structural double-hour and sexagenary surrogates only; not a live almanac feed. Docs gate remains blocked." if blocked else "Structural double-hour and sexagenary surrogates only; not a live almanac feed.", "suggested_frontier": frontier, "handoff_target": handoff, "blocker_truth": "BLOCKED" if blocked else "OPEN", "double_hour_gate": f"{stem} / {animal}", "wu_xing_bias": element, "sexagenary_overlay": f"Chinese60 structural index {overlay:02d}", "witness": f"Derived from local time {now.strftime('%H:%M')} using the fixed 12-gate double-hour cycle and day ordinal modulo 60."}}
    item["packet"], variants = decorate_packet(now, item["packet"], gate_index, "Two-hour center/stability/transition lane using branch, element, and sexagenary support.", weights[element], f"Chinese double-hour gate {animal} projects directly onto {shared12_descriptor(gate_index)}.", resolution_band("double-hour", "day", "month", "year", "60-cycle", "GreatYear"))
    return item, variants


def vedic_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    gate27 = (now.date().toordinal() % 27) + 1
    gate28 = (now.date().toordinal() % 28) + 1
    band18 = (now.date().toordinal() % 18) + 1
    mode = gate27 % 3
    if mode == 1:
        frontier, handoff, bias, weights = "Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "seed a coherent daily control rhythm", role_vector(30, 30, 20, 20)
    elif mode == 2:
        frontier, handoff, bias, weights = "Q44 organism wave proof", "athena-weave-scan", "expand the living body through one well-chosen growth line", role_vector(25, 20, 35, 20)
    else:
        frontier, handoff, bias, weights = "TQ04 runner-contract binding", "high-priest-totality", "refine the law body before further expansion", role_vector(20, 35, 15, 30)
    seat_index = ((gate27 - 1) * 12) // 27
    item = {"title": "Vedic Lunar Packet", "owner": "astro-vedic-lunar", "path": LEDGER_ROOT / "vedic_lunar_packet.md", "packet": {"system_id": "vedic_lunar", "clock_mode": "daily lunar office", "native_cycle": "Lunar27/28/18", "current_gate": f"Lunar27 gate {gate27:02d}", "next_transition": transition_text(next_midnight(now)), "action_bias": bias, "cautions": "Structural lunar cadence only; not live sidereal ephemeris. Docs gate remains blocked." if blocked else "Structural lunar cadence only; not live sidereal ephemeris.", "suggested_frontier": frontier, "handoff_target": handoff, "blocker_truth": "BLOCKED" if blocked else "OPEN", "lunar27_gate": f"{gate27:02d}", "lunar28_gate": f"{gate28:02d}", "lunar18_band": f"{band18:02d}", "witness": "Derived from local calendar day using the corpus structural Lunar27, Lunar28, and Lunar18 ladders."}}
    item["packet"], variants = decorate_packet(now, item["packet"], seat_index, "Daily law-body and long-wave refinement lane projected from Lunar27/28/18 into the shared 12-seat ring.", weights, f"Lunar27 gate {gate27:02d} projects evenly into {shared12_descriptor(seat_index)}.", resolution_band("day", "lunar month", "season", "year", "precession", "GreatYear"))
    return item, variants


def mayan_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    tzolkin = (now.date().toordinal() % 260) + 1
    haab = (now.timetuple().tm_yday % 365) + 1
    mode = tzolkin % 4
    frontier_map = {0: ("Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "stabilize the current turn and keep the whole cycle legible"), 1: ("Q44 organism wave proof", "athena-weave-scan", "surface one coherent growth line from the wider field"), 2: ("Q35 ORGIN mirrored seed corpus", "corpus-weave", "translate hidden reserve memory into routed witness"), 3: ("TQ04 runner-contract binding", "high-priest-totality", "bind cosmology into a replay-safe law surface")}
    weights = {0: role_vector(25, 30, 20, 25), 1: role_vector(30, 20, 35, 15), 2: role_vector(35, 15, 20, 30), 3: role_vector(20, 35, 15, 30)}
    seat_index = ((((tzolkin - 1) * 12) // 260) + (((haab - 1) * 12) // 365)) % 12
    frontier, handoff, bias = frontier_map[mode]
    item = {"title": "Mayan Calendar Packet", "owner": "astro-mayan-calendar", "path": LEDGER_ROOT / "mayan_calendar_packet.md", "packet": {"system_id": "mayan_calendar", "clock_mode": "daily Mayan calendar office", "native_cycle": "Tzolkin260 + Haab365", "current_gate": f"Tzolkin {tzolkin:03d} / Haab {haab:03d}", "next_transition": transition_text(next_midnight(now)), "action_bias": bias, "cautions": "Structural count only; not a live historical-correlation engine. Docs gate remains blocked." if blocked else "Structural count only; not a live historical-correlation engine.", "suggested_frontier": frontier, "handoff_target": handoff, "blocker_truth": "BLOCKED" if blocked else "OPEN", "tzolkin_gate": f"{tzolkin:03d}", "haab_gate": f"{haab:03d}", "cycle_bias": f"mode-{mode}", "witness": "Derived from local calendar counts using structural Tzolkin260 and Haab365 counters."}}
    item["packet"], variants = decorate_packet(now, item["packet"], seat_index, "Daily growth-sequence and pattern-completion lane combining Tzolkin and Haab into one shared archetype seat.", weights[mode], f"Tzolkin {tzolkin:03d} and Haab {haab:03d} combine into {shared12_descriptor(seat_index)}.", resolution_band("day", "month", "year", "260-count", "365-count", "GreatYear"))
    return item, variants


def decan_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    watch_phase = "day watch" if 6 <= now.hour < 18 else "night watch"
    decan = ((now.date().toordinal() * 2) + (0 if watch_phase == "day watch" else 1)) % 36 + 1
    seat_index = (decan - 1) // 3
    if watch_phase == "day watch":
        frontier, handoff, bias, weights = "TQ04 runner-contract binding", "high-priest-totality", "bind the watch law into one durable corridor", role_vector(20, 30, 20, 30)
    else:
        frontier, handoff, bias, weights = "Q42 QSHRINK corridor followthrough", "qshrink-shiva", "diagnose hidden joints and prune the night-side drift", role_vector(25, 15, 20, 40)
    item = {"title": "Decan Office Packet", "owner": "astro-decan-office", "path": LEDGER_ROOT / "decan_office_packet.md", "packet": {"system_id": "decan_office", "clock_mode": "12-hour decan office", "native_cycle": "Decan36 / night-watch / MUL.APIN", "current_gate": f"Decan36 gate {decan:02d} / {watch_phase}", "next_transition": transition_text(next_watch_boundary(now)), "action_bias": bias, "cautions": "Structural decan and watch cadence only; not live stellar ephemeris. Docs gate remains blocked." if blocked else "Structural decan and watch cadence only; not live stellar ephemeris.", "suggested_frontier": frontier, "handoff_target": handoff, "blocker_truth": "BLOCKED" if blocked else "OPEN", "watch_phase": watch_phase, "decan_gate": f"{decan:02d}", "mesopotamian_bias": "MUL.APIN structural watch lane", "witness": f"Derived from the local half-day watch at {now.strftime('%H:%M')} using a structural Decan36 counter."}}
    item["packet"], variants = decorate_packet(now, item["packet"], seat_index, "Twelve-hour threshold/watch/guard lane using Decan36 projected into 12 shared houses.", weights, f"Decan36 gate {decan:02d} projects in 3-decan groups onto {shared12_descriptor(seat_index)}.", resolution_band("watch", "day", "month", "year", "precession", "GreatYear"))
    return item, variants


def egyptian_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    duat_gate = (now.hour % 12) + 1
    decan = ((now.date().toordinal() * 2) + (0 if 6 <= now.hour < 18 else 1)) % 36 + 1
    phase = EGYPTIAN_PHASES[(duat_gate - 1) // 3]
    frontier_map = {
        "becoming": ("Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "surface lawful emergence without outrunning proof"),
        "testing": ("TQ04 runner-contract binding", "high-priest-totality", "weigh continuity against contract and witness"),
        "judgment": ("Q42 QSHRINK corridor followthrough", "qshrink-shiva", "strip false growth and preserve ma'at"),
        "renewal": ("Q44 organism wave proof", "athena-weave-scan", "return purified pressure into a cleaner cycle"),
    }
    weights = {
        "becoming": role_vector(30, 25, 30, 15),
        "testing": role_vector(20, 35, 15, 30),
        "judgment": role_vector(15, 20, 20, 45),
        "renewal": role_vector(35, 20, 20, 25),
    }
    frontier, handoff, bias = frontier_map[phase]
    item = {
        "title": "Egyptian Kheper Packet",
        "owner": "astro-egyptian-kheper",
        "path": LEDGER_ROOT / "egyptian_kheper_packet.md",
        "packet": {
            "system_id": "egyptian_kheper",
            "clock_mode": "hourly Duat12 lane with Decan36 support",
            "native_cycle": "Duat12 / Kheper / Ma'at / Decan36",
            "current_gate": f"Duat12 gate {duat_gate:02d} / Decan36 gate {decan:02d} / {phase}",
            "next_transition": transition_text(next_hour_boundary(now)),
            "action_bias": bias,
            "cautions": "Structural Duat and decan surrogate only; not a live ritual calendar or stellar ephemeris. Docs gate remains blocked." if blocked else "Structural Duat and decan surrogate only; not a live ritual calendar or stellar ephemeris.",
            "suggested_frontier": frontier,
            "handoff_target": handoff,
            "blocker_truth": "BLOCKED" if blocked else "OPEN",
            "duat_gate": f"{duat_gate:02d}",
            "decan_support_gate": f"{decan:02d}",
            "ma_at_phase": phase,
            "witness": "Derived from local hour modulo 12 with a structural Decan36 support counter; compiled as the Egyptian shadow lane until promotion.",
        },
    }
    item["packet"], variants = decorate_packet(now, item["packet"], duat_gate - 1, "Compiled Duat/becoming/judgment lane with Ma'at filtering and Decan36 support.", weights[phase], f"Duat12 gate {duat_gate:02d} projects directly onto {shared12_descriptor(duat_gate - 1)} while Decan36 stays as support detail.", resolution_band("hour", "watch", "day", "month", "year", "GreatYear"))
    return item, variants


def norse_packet(now: datetime, blocked: bool) -> tuple[dict[str, object], dict[str, int]]:
    rune_index = now.date().toordinal() % 24
    house_index = rune_index // 2
    world_index = now.date().toordinal() % 9
    world_name = NORSE_WORLDS[world_index]
    tier = "upper" if world_index < 3 else "middle" if world_index < 6 else "lower"
    frontier_map = {
        "upper": ("Q44 organism wave proof", "athena-weave-scan", "route insight from the crown worlds back into the trunk"),
        "middle": ("Q41 / TQ06 packet-fed hourly sync", "guildmaster-loop", "keep the trunk legible across living traffic"),
        "lower": ("Q42 QSHRINK corridor followthrough", "qshrink-shiva", "prune fate-entanglement and preserve restart honesty"),
    }
    weights = {"upper": role_vector(35, 20, 25, 20), "middle": role_vector(20, 35, 25, 20), "lower": role_vector(20, 20, 20, 40)}
    frontier, handoff, bias = frontier_map[tier]
    item = {
        "title": "Norse Rune Yggdrasil Packet",
        "owner": "astro-norse-rune-yggdrasil",
        "path": LEDGER_ROOT / "norse_rune_yggdrasil_packet.md",
        "packet": {
            "system_id": "norse_rune_yggdrasil",
            "clock_mode": "daily Rune24 lane with House12 projection",
            "native_cycle": "Rune24 / House12 / Yggdrasil9",
            "current_gate": f"Rune24 gate {rune_index + 1:02d} / House12 gate {house_index + 1:02d} / {world_name}",
            "next_transition": transition_text(next_midnight(now)),
            "action_bias": bias,
            "cautions": "Structural rune and world-tree surrogate only; not a historical festival or astronomical reconstruction. Docs gate remains blocked." if blocked else "Structural rune and world-tree surrogate only; not a historical festival or astronomical reconstruction.",
            "suggested_frontier": frontier,
            "handoff_target": handoff,
            "blocker_truth": "BLOCKED" if blocked else "OPEN",
            "rune_gate": f"{rune_index + 1:02d} / {NORSE_RUNES[rune_index]}",
            "house12_gate": f"{house_index + 1:02d}",
            "yggdrasil_world": world_name,
            "witness": "Derived from local ordinal day modulo 24 for the rune lane and modulo 9 for the Yggdrasil world overlay; compiled as the Norse shadow lane until promotion.",
        },
    }
    item["packet"], variants = decorate_packet(now, item["packet"], house_index, "Compiled fate-route lane pairing Rune24 with House12 and a 9-world Yggdrasil routing overlay.", weights[tier], f"Rune24 gate {rune_index + 1:02d} pairs into House12 gate {house_index + 1:02d}, yielding {shared12_descriptor(house_index)}.", resolution_band("day", "season", "year", "Rune24", "Yggdrasil9", "GreatYear"))
    return item, variants


def compute_avatar_triggers(now: datetime, packets: list[dict[str, object]]) -> list[dict[str, object]]:
    seat_map: dict[int, list[dict[str, object]]] = defaultdict(list)
    for item in packets:
        next_transition = datetime.strptime(str(item["packet"]["next_transition"])[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TIMEZONE)
        for variant_name, seat_index in item["variant_indexes"].items():
            seat_map[seat_index].append({"system_id": item["packet"]["system_id"], "lane_state": item["packet"]["lane_state"], "speed_class": item["packet"]["speed_class"], "variant": variant_name, "next_transition": next_transition})
    triggers = []
    for seat_index, refs in sorted(seat_map.items()):
        lanes = sorted({str(ref["system_id"]) for ref in refs})
        fast_lanes = sorted({str(ref["system_id"]) for ref in refs if ref["speed_class"] == "fast"})
        slow_lanes = sorted({str(ref["system_id"]) for ref in refs if ref["speed_class"] == "slow"})
        if len(lanes) < 3 or not fast_lanes or not slow_lanes:
            continue
        triggers.append({
            "avatar_id": f"AVATAR-S{seat_index + 1:02d}-{now.strftime('%Y%m%dT%H%M%S')}",
            "shared12_seat": shared12_descriptor(seat_index),
            "contributing_lanes": lanes,
            "fast_lanes": fast_lanes,
            "slow_lanes": slow_lanes,
            "lane_states": sorted({str(ref['lane_state']) for ref in refs}),
            "lifespan_until": transition_text(min(ref["next_transition"] for ref in refs)),
            "spawn_reason": ">=3 lane convergence with both fast and slow participation across the shared12 image field.",
        })
    return triggers


def attach_nexus_scores(packets: list[dict[str, object]], triggers: list[dict[str, object]]) -> None:
    seat_counts: Counter[int] = Counter()
    for item in packets:
        for seat_index in item["variant_indexes"].values():
            seat_counts[seat_index] += 1
    triggered = {trigger["shared12_seat"] for trigger in triggers}
    for item in packets:
        packet = item["packet"]
        score = sum(seat_counts[seat_index] for seat_index in item["variant_indexes"].values())
        if packet["shared12_seat"] in triggered:
            score += 3
        packet["nexus_score"] = score


def attach_hsigma_overlay(packets: list[dict[str, object]], hsigma_bundle: dict[str, object]) -> None:
    save_state = hsigma_bundle["save_state"]
    current_byte = int(save_state["current_state"]["byte"])
    for item in packets:
        packet = item["packet"]
        row_ids = ASTRO_LANE_BUNDLES[str(packet["system_id"])]
        overlay = aggregate_bundle_state(save_state, row_ids)
        packet["hsigma_current_byte"] = current_byte
        packet["hsigma_row_ids"] = row_ids
        packet["hsigma_weight"] = overlay["weight"]
        packet["hsigma_hidden_pressure"] = overlay["hidden_pressure"]
        packet["hsigma_cell_class"] = overlay["cell_class"]
        packet["hsigma_restart_seed"] = overlay["restart_seed"]
        if not overlay["contradictory"]:
            packet["nexus_score"] = int(packet["nexus_score"]) + round(float(overlay["weight"]) / 20)


def render_packet_markdown(title: str, owner: str, packet: dict[str, object], generated_at: str) -> str:
    lines = [f"# {title}", "", "Status: `FRESH STRUCTURAL DERIVATION`", f"Packet owner: `{owner}`", f"Generated at: `{generated_at}`", ""]
    field_order = ["system_id", "clock_mode", "native_cycle", "current_gate", "next_transition", "action_bias", "cautions", "suggested_frontier", "handoff_target", "blocker_truth"]
    for field in field_order:
        lines.append(f"- `{field}`: `{json_string(packet[field])}`")
    lines.extend(["", "Support fields:", ""])
    preferred = ["native_gate", "shared12_seat", "projection_witness", "variant_set", "role_weight_vector", "resolution_band", "lane_flavor", "lane_state", "rotation_group", "activation_gate", "active_master_role_count", "master_roles", "speed_class", "nexus_score", "hsigma_current_byte", "hsigma_row_ids", "hsigma_weight", "hsigma_hidden_pressure", "hsigma_cell_class", "hsigma_restart_seed", "liminal_tag", "spawn_envelope_seed"]
    support_fields = [field for field in packet.keys() if field not in field_order]
    for field in preferred + [field for field in support_fields if field not in preferred]:
        if field in packet:
            lines.append(f"- `{field}`: `{json_string(packet[field])}`")
    return "\n".join(lines)


def render_receipt(now: datetime, blocked: bool, packets: list[dict[str, object]], receipt_path: Path, triggers: list[dict[str, object]]) -> str:
    counts = Counter(item["packet"]["suggested_frontier"] for item in packets)
    active_lane_ids = [item["packet"]["system_id"] for item in packets if item["packet"]["active_master_role_count"]]
    compiled_lane_ids = [item["packet"]["system_id"] for item in packets if not item["packet"]["active_master_role_count"]]
    lines = [
        f"# {now.strftime('%Y-%m-%d')} Astro-Lattice Packet Freshness Sweep",
        "",
        f"Date: `{now.strftime('%Y-%m-%d %H:%M:%S %Z')}`",
        f"Docs gate: `{'BLOCKED' if blocked else 'OPEN'}`",
        "Truth class: `local structural scheduler witness`",
        "",
        "## Outcome",
        "",
        "- Ran the shared-kernel astro-lattice derivation across eight pantheon lanes.",
        "- Preserved the active cap as `24` master agents by keeping six lanes active and two lanes compiled-shadow only.",
        "- Added shared12 projection, variant math, liminal tags, and spawn-envelope seeds to every packet.",
        "- Attached the runtime HSigma save state as an additive shared-nexus overlay without changing the active-lane law.",
        "",
        "## Lane Sweep",
        "",
    ]
    for item in packets:
        packet = item["packet"]
        lines.append(f"- `{packet['system_id']}` -> state=`{packet['lane_state']}` -> shared12=`{packet['shared12_seat']}` -> nexus=`{packet['nexus_score']}` -> hsigma_class=`{packet['hsigma_cell_class']}` -> frontier=`{packet['suggested_frontier']}`")
    lines.extend(["", "## Activation Law", "", f"- active lanes: `{', '.join(active_lane_ids)}`", f"- compiled shadow lanes: `{', '.join(compiled_lane_ids)}`", "- anchor lanes remain Western, Planetary, Chinese, and Vedic until `G4`.", "- cultural rotation seats remain Mayan and Decan until `G4`; Egyptian and Norse contribute as compiled shadow lanes.", "", "## Avatar Candidates", ""])
    if triggers:
        for trigger in triggers:
            lines.append(f"- `{trigger['avatar_id']}` -> seat=`{trigger['shared12_seat']}` -> lanes=`{', '.join(trigger['contributing_lanes'])}` -> lifespan=`{trigger['lifespan_until']}`")
    else:
        lines.append("- no current avatar trigger met the `>=3 lanes with fast+slow mix` threshold")
    lines.extend(["", "## Convergence", "", f"- frontier counts: `{', '.join(f'{key} x{value}' for key, value in counts.most_common())}`", f"- hsigma witness: `{HSIGMA_WITNESS_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`", "", "## Artifacts", "", f"- registry read: `{REGISTRY_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`", f"- packet summary: `{JSON_OUTPUT_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`", f"- packet index: `{PACKET_INDEX_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`", f"- receipt: `{receipt_path.relative_to(WORKSPACE_ROOT).as_posix()}`", "", "## Honesty", "", "- This pass used structural calendar rules only.", "- No live astronomical ephemeris or live Google Docs data was queried.", f"- Docs gate witness remained at `{DOCS_GATE_PATH.relative_to(WORKSPACE_ROOT).as_posix()}` and stayed blocked."])
    return "\n".join(lines)


def render_registry_markdown(now: datetime, blocked: bool, packets: list[dict[str, object]]) -> str:
    lines = [
        "# Astrological Scheduler Registry",
        "",
        f"Date: `{now.strftime('%Y-%m-%d')}`",
        "Status: `ACTIVE V2 / ASTRO-LATTICE + HSIGMA`",
        "Truth policy: `structural calendar layer, not scientific proof`",
        f"Docs gate: `{'BLOCKED' if blocked else 'OPEN'}`",
        "",
        "## Purpose",
        "",
        "This manifest defines the Global Command Center astrological scheduler matrix for Athena.",
        "",
        "The scheduler law is:",
        "",
        "- all pantheon lanes are interfaces onto one shared structural phase kernel",
        "- each lane keeps its native cycle law and also emits one shared 12-seat projection",
        "- inverse and 90-degree rotated families are derived overlays, not always-on lanes",
        "- Avatar agents are nexus-only and spawn only when convergence thresholds are met",
        "- scheduler packets remain advisory timing inputs and never outrank witness class, replay value, blocker honesty, or boundary safety",
        "- HSigma is an additive shared-nexus overlay and does not replace the lane activation law",
        "",
        "## AstroTimingPacket Interface",
        "",
        "Every scheduler lane keeps the same 10 mandatory fields:",
        "",
        "- `system_id`",
        "- `clock_mode`",
        "- `native_cycle`",
        "- `current_gate`",
        "- `next_transition`",
        "- `action_bias`",
        "- `cautions`",
        "- `suggested_frontier`",
        "- `handoff_target`",
        "- `blocker_truth`",
        "",
        "The packet now also publishes these support fields:",
        "",
        "- `shared12_seat`",
        "- `native_gate`",
        "- `projection_witness`",
        "- `variant_set`",
        "- `role_weight_vector`",
        "- `resolution_band`",
        "- `nexus_score`",
        "- `liminal_tag`",
        "- `lane_state`",
        "- `spawn_envelope_seed`",
        "- `hsigma_current_byte`",
        "- `hsigma_row_ids`",
        "- `hsigma_weight`",
        "- `hsigma_hidden_pressure`",
        "- `hsigma_cell_class`",
        "- `hsigma_restart_seed`",
        "",
        "## Scheduler Table",
        "",
        "| System | Automation id | Cadence | Native cycle | Packet path | Lane state |",
        "|---|---|---|---|---|---|",
    ]
    for item in packets:
        packet = item["packet"]
        lines.append(f"| {packet['system_id']} | `{item['owner']}` | {packet['clock_mode']} | `{packet['native_cycle']}` | `{item['path'].relative_to(WORKSPACE_ROOT).as_posix()}` | `{packet['lane_state']}` |")
    lines.extend([
        "",
        "## Honesty",
        "",
        "- structural calendar logic only",
        "- no live astronomical ephemeris",
        "- no live Google Docs claims while `Trading Bot/credentials.json` or `Trading Bot/token.json` are missing",
    ])
    return "\n".join(lines)


def render_packet_index(now: datetime, receipt_path: Path, packets: list[dict[str, object]]) -> str:
    lines = [
        "# Astrological Scheduler Packet Index",
        "",
        f"Date: `{now.strftime('%Y-%m-%d')}`",
        "Status: `ASTRO-LATTICE ACTIVE + HSIGMA`",
        "Latest sweep receipt:",
        f"`{receipt_path.relative_to(WORKSPACE_ROOT).as_posix()}`",
        "",
        "## Fixed Packet Paths",
        "",
    ]
    for item in packets:
        lines.append(f"- {item['title']}:")
        lines.append(f"  `{item['path']}`")
    lines.extend([
        "",
        "## Contract",
        "",
        "- each scheduler lane updates only its own packet file",
        "- packet files are read by the control-layer meta automations",
        "- fresh structural derivation counts as a local scheduler execution witness",
        "- every packet now carries shared12 projection, variant math, nexus score, liminal tag, spawn-envelope seed, and HSigma shared-nexus support fields",
        "- active-lane cap remains `24` master agents as `6 lanes x 4 roles`",
        "- Egyptian and Norse stay `COMPILED_SHADOW` until promotion gates permit cultural-slot rotation",
        "- Docs gate remains `BLOCKED` until `Trading Bot/credentials.json` and `Trading Bot/token.json` both exist and authenticate",
    ])
    return "\n".join(lines)


def lane_registry_rows(packets: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"system_id": item["packet"]["system_id"], "owner": item["owner"], "clock_mode": item["packet"]["clock_mode"], "native_cycle": item["packet"]["native_cycle"], "lane_state": item["packet"]["lane_state"], "rotation_group": item["packet"]["rotation_group"], "speed_class": item["packet"]["speed_class"], "active_master_role_count": item["packet"]["active_master_role_count"], "shared12_seat": item["packet"]["shared12_seat"], "next_transition": item["packet"]["next_transition"], "nexus_score": item["packet"]["nexus_score"], "unserved_lane_age": item["packet"]["unserved_lane_age"], "packet_path": str(item["path"])} for item in packets]


def g4_rotation_candidates(packets: list[dict[str, object]]) -> list[dict[str, object]]:
    cultural = [item["packet"] for item in packets if item["packet"]["rotation_group"] == "cultural"]
    ordered = sorted(
        cultural,
        key=lambda packet: (
            -int(packet["nexus_score"]),
            str(packet["next_transition"]),
            int(packet["unserved_lane_age"]),
        ),
    )
    return [
        {
            "system_id": packet["system_id"],
            "lane_state": packet["lane_state"],
            "shared12_seat": packet["shared12_seat"],
            "next_transition": packet["next_transition"],
            "nexus_score": packet["nexus_score"],
            "unserved_lane_age": packet["unserved_lane_age"],
        }
        for packet in ordered
    ]


def main() -> int:
    now = local_now()
    generated_at = now.isoformat()
    blocked = docs_blocked()
    hsigma_bundle = ensure_hsigma_artifacts(now)
    packets = []
    for item, variants in [western_packet(now, blocked), planetary_packet(now, blocked), chinese_packet(now, blocked), vedic_packet(now, blocked), mayan_packet(now, blocked), decan_packet(now, blocked), egyptian_packet(now, blocked), norse_packet(now, blocked)]:
        packets.append({"title": item["title"], "owner": item["owner"], "path": item["path"], "packet": item["packet"], "variant_indexes": variants})
    triggers = compute_avatar_triggers(now, packets)
    attach_nexus_scores(packets, triggers)
    attach_hsigma_overlay(packets, hsigma_bundle)
    for item in packets:
        write_text(item["path"], render_packet_markdown(item["title"], item["owner"], item["packet"], generated_at))
    receipt_path = RECEIPTS_ROOT / f"{now.strftime('%Y-%m-%d')}_first_scheduler_packet_freshness_sweep_{now.strftime('%H%M')}.md"
    summary_payload = {
        "generated_at": generated_at,
        "generated_at_utc": utc_now(),
        "timezone": "America/Los_Angeles",
        "docs_gate": "BLOCKED" if blocked else "OPEN",
        "registry_path": str(REGISTRY_PATH),
        "receipt_path": str(receipt_path),
        "variant_contract": {name: f"+{offset}" for name, offset in VARIANT_OFFSETS.items()},
        "spawn_envelope_contract": ["agent_id", "lane_id", "role_id", "loop_id", "spawn_ts_local", "spawn_ts_utc", "shared12_seat", "native_gate", "variant", "liminal_tag", "reasoning_summary", "writeback_targets"],
        "avatar_trigger_contract": {"minimum_lanes": 3, "requires_fast_lane": True, "requires_slow_lane": True, "lifespan_rule": "next transition of the fastest contributing lane"},
        "active_lane_ids": [item["packet"]["system_id"] for item in packets if item["packet"]["active_master_role_count"]],
        "active_anchor_lane_ids": sorted(ACTIVE_ANCHOR_IDS),
        "active_rotation_lane_ids": sorted(ACTIVE_ROTATION_IDS),
        "compiled_lane_ids": [item["packet"]["system_id"] for item in packets if not item["packet"]["active_master_role_count"]],
        "active_master_count": sum(int(item["packet"]["active_master_role_count"]) for item in packets),
        "rotation_policy": {"g2": "Egyptian compiled shadow lane participates in nexus scoring immediately.", "g3": "Norse compiled shadow lane participates in nexus scoring immediately.", "g4": "Keep Western, Planetary, Chinese, and Vedic as anchors; rotate the last two slots among Mayan, Decan, Egyptian, and Norse by nexus_score, then next_transition, then unserved_lane_age."},
        "long_wave_context": long_wave_context(now),
        "hsigma_overlay": {
            "current_byte": hsigma_bundle["save_state"]["current_state"]["byte"],
            "current_coords": hsigma_bundle["save_state"]["current_state"]["coords"],
            "witness_path": str(HSIGMA_WITNESS_PATH),
        },
        "pantheon_lane_registry": lane_registry_rows(packets),
        "g4_rotation_candidates": g4_rotation_candidates(packets),
        "avatar_triggers": triggers,
        "packets": [{"packet_path": str(item["path"]), **item["packet"]} for item in packets],
    }
    write_json(JSON_OUTPUT_PATH, summary_payload)
    write_text(receipt_path, render_receipt(now, blocked, packets, receipt_path, triggers))
    write_text(REGISTRY_PATH, render_registry_markdown(now, blocked, packets))
    write_text(PACKET_INDEX_PATH, render_packet_index(now, receipt_path, packets))
    print(f"Wrote packet summary: {JSON_OUTPUT_PATH}")
    for item in packets:
        print(f"Wrote packet: {item['path']}")
    print(f"Wrote receipt: {receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

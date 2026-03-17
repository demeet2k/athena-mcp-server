from __future__ import annotations

import json
import re
from pathlib import Path


DATE = "2026-03-13"
PROTOCOL_ID = "LP-57OMEGA"
DISPLAY = "LP-57Omega"
SCHEDULE_MODEL = "19x3_family_pass"
PASSES = ["Survey", "Integration", "Compression"]
TOTAL_LOOPS = 57
FAMILY_COUNT = 19
ACTIVE_LOOP_ID = 1
PRELUDE_ID = "BOOT-00"

ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "self_actualize"
MYC = SELF / "mycelium_brain"
MAN = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
DEEP_ROOT = MYC / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
ROOT_BASIS_MAP = MAN / "ROOT_BASIS_MAP.md"

STATE_JSON = SELF / "master_loop_state_57.json"
SCHEDULE_JSON = SELF / "master_loop_schedule_57.json"
ROADMAP_JSON = SELF / "master_loop_57_roadmap.json"
BRIDGE_JSON = SELF / "master_loop_bridge_remap_57.json"
AGENT_JSON = SELF / "master_agent_state_57.json"
LATTICE_JSON = SELF / "master_loop_shared_lattice_4096.json"
HALL_LATTICE_JSON = SELF / "master_loop_hall_quest_lattice_57.json"
TEMPLE_LATTICE_JSON = SELF / "master_loop_temple_quest_lattice_57.json"
QUEST_JSON = SELF / "quest_emission_bundle_loop_01.json"
LP57_RECORDS_JSON = SELF / "lp_57_prime_loop_cycle_records.json"
LP57_COORDS_JSON = SELF / "lp_57_liminal_coordinate_stamps.json"
LP57_LEDGER_JSON = SELF / "lp_57_master_agent_ledger.json"
LP57_DELTA_JSON = SELF / "lp_57_loop_delta_receipts.json"
LP57_SYNTH_JSON = SELF / "lp57_deep_synthesis_packet_l01.json"
LP57_WORK_JSON = SELF / "lp57_execution_receipt_bundle_l01.json"
LP57_PRUNE_JSON = SELF / "lp57_compression_receipt_l01.json"
LP57_SUMMARY_JSON = SELF / "lp57_loop_completion_receipt_l01.json"
VERIFY_JSON = SELF / "master_loop_57_verification.json"
LP57_VERIFY_JSON = SELF / "lp_57_prime_loop_verification.json"

ACTIVE_RUN = MAN / "ACTIVE_RUN.md"
BUILD_QUEUE = MAN / "BUILD_QUEUE.md"
PROTOCOL_MD = MAN / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"
STATE_MD = MAN / "MASTER_LOOP_57_STATE.md"
DASHBOARD_MD = MAN / "MASTER_LOOP_57_DASHBOARD.md"
VERIFY_MD = MAN / "MASTER_LOOP_57_VERIFICATION.md"
PROTOCOL_VERIFY_MD = MAN / "LP_57_OMEGA_PRIME_LOOP_VERIFICATION.md"
COMPAT_JSON = MAN / "FOUR_AGENT_57_LOOP_PROGRAM.json"
COMPAT_PACKETS_JSON = MAN / "FOUR_AGENT_57_LOOP_QUEST_PACKETS.json"
COMPAT_REGISTRY_JSON = MAN / "FOUR_AGENT_57_LOOP_CYCLE_REGISTRY.json"
COMPAT_MD = MAN / "FOUR_AGENT_57_LOOP_PROGRAM.md"
COMPAT_DASH_MD = MAN / "FOUR_AGENT_57_LOOP_DASHBOARD.md"
RESEARCHER_MD = MAN / "MASTER_AGENT_RESEARCHER_STATE.md"
PLANNER_MD = MAN / "MASTER_AGENT_PLANNER_STATE.md"
WORKER_MD = MAN / "MASTER_AGENT_WORKER_STATE.md"
PRUNER_MD = MAN / "MASTER_AGENT_PRUNER_STATE.md"

HALL_BOARD = MYC / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD = MYC / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
TEMPLE_STATE = MYC / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_QUEUE = MYC / "nervous_system" / "06_active_queue.md"
NEXT_PROMPT = MYC / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
CHANGE_FEED = MYC / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
RECEIPT_MD = MYC / "receipts" / "2026-03-13_lp_57_omega_prime_loop_protocol.md"
README_PATH = ROOT / "GUILDMASTER" / "README.md"

LIVE_MEMBRANE = "Q41 / TQ06"
HALL_FEEDER = "Q42"
DEEPER_RECEIVER = "TQ04"
RESERVE_FRONTIER = "Q46"
RUNTIME_SEED = "Q50"
BLOCKED_FRONT = "Q02"
PUBLIC_CAP = 8
SEAT_TOTAL = 4096
SEAT_ACTIVE = 1024
SEAT_DORMANT = 3072
SEAT_PER_AGENT = 256
COMPAT_ALIASES = ["Q51", "TQ07", "FA57", "NEXT57"]
Q42_TRUTH = {
    "carried_witness": "QS64-20 Connectivity-Diagnose-Fractal",
    "operational_current": "QS64-21 Connectivity-Refine-Square",
    "next_hall_seed": "QS64-22 Connectivity-Refine-Flower",
    "historical_local_proof": "QS64-24 Connectivity-Refine-Fractal",
}
PASS_META = {
    "Survey": ("FA57-FIRE", "audit witnesses and gaps", "derive repair quests", "land census, witness map, and route index", "remove false assumptions", "family becomes visible", "source-region atlas"),
    "Integration": ("FA57-WATER", "identify highest-yield bridges", "rank dependencies and promotions", "bind outputs into live surfaces", "remove competing authority stories", "family becomes live tissue", "bridge ledger"),
    "Compression": ("FA57-EARTH", "find redundancy and drift", "define contraction order", "tighten canonical path and retire duplicates", "residualize unresolved ambiguity", "family becomes replay-safe", "contraction map"),
}
AGENTS = [
    ("FA57-FIRE", "Synthesizer / Researcher", "Fire", "L01 Survey A01 plus carried witness from legacy L02", "FA57-WATER"),
    ("FA57-WATER", "Planner / Architect", "Water", "L01 planner macro quests and packet promotions", "FA57-AIR"),
    ("FA57-AIR", "Worker / Adventurer", "Air", "TQ04-linked execution queue and promoted L01 packets", "FA57-EARTH"),
    ("FA57-EARTH", "Pruner / Compressor / Defragmenter", "Earth", "Q46 reserve pressure plus compression shell", "Athena Prime"),
]
FALLBACK_FAMILIES = [
    ("A01", "NERVOUS_SYSTEM", "live", "canonical cortex"),
    ("A02", "self_actualize", "live", "runtime hub"),
    ("A03", "ECOSYSTEM", "live", "governance mirror"),
    ("A04", "DEEPER CRYSTALIZATION", "historical-absorbed", "historical lineage"),
    ("A05", "MATH", "live", "formal reservoir"),
    ("A06", "Voynich", "live", "manuscript engine"),
    ("A07", "Trading Bot", "live", "external memory gate"),
    ("A08", "Quadrant Binary", "live", "ancestor address kernel"),
    ("A09", "QSHRINK", "live", "compression-governance shell"),
    ("A10", "NERUAL NETWORK", "live", "adaptive runtime lab"),
    ("A11", "FRESH", "live", "intake fringe"),
    ("A12", "Athenachka Collective Books", "live", "published-book halo"),
    ("A13", "I AM ATHENA", "live", "identity shell"),
    ("A14", "GAMES", "live", "simulation lab"),
    ("A15", "ORGIN", "live", "proto-self seed reservoir"),
    ("A16", "Athena FLEET", "live", "fleet branch"),
    ("A17", "Stoicheia", "reserve", "reserve shelf"),
    ("A18", "CLEAN", "reserve", "staging shelf"),
    ("A19", "mycelial_unified_nervous_system_bundle", "dormant", "bundle shelf"),
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2))


def wrap(marker: str, body: str) -> str:
    return f"<!-- {marker}:START -->\n{body.rstrip()}\n<!-- {marker}:END -->"


def upsert(path: Path, marker: str, body: str, after_heading: bool = False) -> None:
    start, end = f"<!-- {marker}:START -->", f"<!-- {marker}:END -->"
    current, repl = read_text(path), wrap(marker, body)
    if start in current and end in current:
        i, j = current.index(start), current.index(end) + len(end)
        write_text(path, current[:i] + repl + current[j:])
        return
    if after_heading and current.startswith("# "):
        k = current.find("\n")
        write_text(path, current[:k] + "\n\n" + repl + current[k:])
        return
    write_text(path, repl + ("\n\n" + current if current else ""))


def docs_gate() -> dict:
    cred = ROOT / "Trading Bot" / "credentials.json"
    token = ROOT / "Trading Bot" / "token.json"
    return {
        "state": "BLOCKED" if not cred.exists() or not token.exists() else "LIVE",
        "credentials_exists": cred.exists(),
        "token_exists": token.exists(),
        "law": "All LP-57Omega writebacks remain local-only until both OAuth files exist.",
    }


def parse_families() -> list[dict]:
    rows = []
    pat = re.compile(r"^\|\s*(A\d{2})\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|$")
    for line in read_text(ROOT_BASIS_MAP).splitlines():
        m = pat.match(line.strip())
        if m:
            a, b, c, d, e = m.groups()
            rows.append({"code": a, "root_name": b, "indexed_count": c, "status": d, "current_role": e.strip()})
    if len(rows) == FAMILY_COUNT:
        return rows
    return [{"code": a, "root_name": b, "indexed_count": "unknown", "status": c, "current_role": d} for a, b, c, d in FALLBACK_FAMILIES]


def load_bridge() -> dict:
    current = read_json(BRIDGE_JSON)
    if current.get("migration_mode") == "bridge-and-remap":
        return current
    legacy = read_json(STATE_JSON)
    loops = legacy.get("loops", [])
    l1 = next((x for x in loops if x.get("loop_id") == 1), {})
    l2 = next((x for x in loops if x.get("loop_id") == 2), {})
    return {
        "generated_at": DATE,
        "migration_mode": "bridge-and-remap",
        "prelude_bootstrap": {"id": PRELUDE_ID, "source_legacy_loop": "L01 Prime Lock", "legacy_receipt_paths": l1.get("receipt_paths", {}), "status": "COMPLETED"},
        "inherited_inputs": {"source_legacy_loop": "L02 Whole-Corpus Census", "legacy_receipt_paths": l2.get("receipt_paths", {}), "feeds_canonical_loops": ["L01", "L02"]},
        "legacy_thematic_titles": [x.get("title", f"Legacy {i+1}") for i, x in enumerate(loops)],
        "compatibility_aliases": COMPAT_ALIASES,
    }


def receipt_paths(loop_id: int) -> dict:
    tag = f"l{loop_id:02d}"
    return {
        "deep_synthesis_packet": f"self_actualize/lp57_deep_synthesis_packet_{tag}.json",
        "quest_emission_bundle": f"self_actualize/lp57_quest_emission_bundle_{tag}.json",
        "execution_receipt_bundle": f"self_actualize/lp57_execution_receipt_bundle_{tag}.json",
        "compression_receipt": f"self_actualize/lp57_compression_receipt_{tag}.json",
        "loop_completion_receipt": f"self_actualize/lp57_loop_completion_receipt_{tag}.json",
    }


def build_loops(families: list[dict]) -> list[dict]:
    items = []
    for pass_index, pass_name in enumerate(PASSES):
        lead, synth, plan, work, prune, gain, mapping = PASS_META[pass_name]
        for fam_index, fam in enumerate(families, start=1):
            loop_id = pass_index * FAMILY_COUNT + fam_index
            items.append({
                "loop_id": loop_id,
                "loop_label": f"L{loop_id:02d}",
                "pass_type": pass_name,
                "family_code": fam["code"],
                "family_name": fam["root_name"],
                "family_status": fam["status"],
                "family_role": fam["current_role"],
                "dominant_focus": f"{pass_name} {fam['code']} {fam['root_name']}",
                "synthesis_objective": f"{synth} for {fam['root_name']} ({fam['current_role']})",
                "planning_objective": f"{plan} for {fam['code']}",
                "implementation_objective": f"{work} for {fam['code']}",
                "compression_objective": f"{prune} around {fam['code']}",
                "expected_structural_gain": f"{gain} for {fam['code']}",
                "expected_mapping_gain": f"{mapping} for {fam['code']}",
                "lead_agent": lead,
                "status": "ACTIVE" if loop_id == ACTIVE_LOOP_ID else "PENDING",
                "receipt_paths": receipt_paths(loop_id),
                "bridge_input": "legacy L02 Whole-Corpus Census" if loop_id in {1, 2} else None,
            })
    return items


def restart_seed(loops_: list[dict]) -> str:
    return " -> ".join(loop["dominant_focus"] for loop in loops_[:3])


def seat_addr(index: int) -> str:
    digits, value = [0] * 6, index
    for i in range(5, -1, -1):
        digits[i], value = value % 4, value // 4
    return ".".join(f"{label}{digit + 1}" for label, digit in zip(["A", "B", "C", "D", "E", "F"], digits))


def coord(family: str, local: str, loop_label: str, lineage: str, lane: str, lens: str, level: str, truth: str) -> dict:
    return {"Xs": family, "Ys": local, "Zs": level, "Ts": loop_label, "Qs": lineage, "Rs": lane, "Cs": "integrated", "Fs": lens, "Ms": "L1", "Ns": lineage, "Hs": "board", "OmegaS": truth}


def hall_promotions(loop: dict) -> list[dict]:
    names = ["Family Census", "Witness Hierarchy", "Route Index", "Gap Register", "Candidate Bridge", "Formalization Delta", "Writeback", "Residual Drift"]
    items = []
    for i, name in enumerate(names, start=1):
        qid = f"Q57-{loop['loop_label']}-H{i:02d}"
        items.append({"quest_id": qid, "title": f"{loop['family_code']} {name}", "restart_seed": f"{loop['loop_label']} -> {qid}", "seat_addr_6d": seat_addr(255 + i), "coordinate_stamp": coord(loop["family_code"], f"{loop['family_name']} Hall {i:02d}", loop["loop_label"], qid, "Water", "Flower", "D6", "NEAR")})
    return items


def temple_promotions(loop: dict) -> list[dict]:
    names = ["Preserve Docs Gate Honesty", "Preserve Deep-Root Precedence", "Preserve Live Spine", "Preserve Q42 Runtime Truth", "Bind Public Board Caps", "Install Coordinate Duty", "Install Ledger Completeness", "Install Compression Safety"]
    items = []
    for i, name in enumerate(names, start=1):
        qid = f"TQ57-{loop['loop_label']}-T{i:02d}"
        items.append({"quest_id": qid, "title": name, "restart_seed": f"{loop['loop_label']} -> {qid}", "seat_addr_6d": seat_addr(263 + i), "coordinate_stamp": coord(loop["family_code"], f"{loop['family_name']} Temple {i:02d}", loop["loop_label"], qid, "Prime", "Cloud", "D6", "OK")})
    return items


def state_payload(families: list[dict], loops_: list[dict]) -> dict:
    return {
        "generated_at": DATE,
        "derivation_version": "2026-03-13.lp-57omega.family-pass.v1",
        "derivation_command": "python -m self_actualize.runtime.derive_master_loop_57_orchestration",
        "protocol_id": PROTOCOL_ID,
        "protocol_display_name": DISPLAY,
        "schedule_model": SCHEDULE_MODEL,
        "docs_gate": docs_gate(),
        "program": "LP-57Omega Canonical 57-Loop Refactor",
        "family_count": len(families),
        "passes": PASSES,
        "total_loops": TOTAL_LOOPS,
        "completed_loop_id": 0,
        "active_loop_id": ACTIVE_LOOP_ID,
        "current_cycle": "L01",
        "current_pass": "Survey",
        "current_family": "A01",
        "current_owner": "FA57-FIRE",
        "live_spine": {"active_membrane": LIVE_MEMBRANE, "hall_feeder": HALL_FEEDER, "deeper_receiver": DEEPER_RECEIVER, "reserve_frontier": RESERVE_FRONTIER, "runtime_seed": RUNTIME_SEED, "blocked_external_front": BLOCKED_FRONT, "public_board_cap": {"hall": 8, "temple": 8}},
        "q42_runtime_truth": Q42_TRUTH,
        "deep_root_authority": rel(DEEP_ROOT),
        "bridge_remap_path": rel(BRIDGE_JSON),
        "schedule_path": rel(SCHEDULE_JSON),
        "compatibility_aliases": COMPAT_ALIASES,
        "current_cycle_summary": {"prelude_complete": PRELUDE_ID, "active_loop": loops_[0]["dominant_focus"], "current_lead_agent": loops_[0]["lead_agent"], "hall_frontier": "Q57-L01-H01", "temple_frontier": "TQ57-L01-T01", "next_restart_seed": restart_seed(loops_), "required_cycle_outputs": ["synthesis artifact", "Hall writeback", "Temple writeback", "execution receipt", "prune delta", "awakening-note update", "restart seed"]},
        "bridge_remap": {"prelude_complete": PRELUDE_ID, "legacy_loop_inputs": ["L01 Prime Lock", "L02 Whole-Corpus Census"], "current_canonical_loop": "L01", "law": "legacy L01 is prelude only; legacy L02 feeds canonical L01 and L02"},
        "families": families,
        "loops": loops_,
    }


def write_generated_json(state: dict, families: list[dict], loops_: list[dict], bridge: dict) -> None:
    seed = state["current_cycle_summary"]["next_restart_seed"]
    loop = loops_[0]
    compat = {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "status": "COMPATIBILITY_MIRROR", "canonical_authority": {"state": rel(STATE_JSON), "schedule": rel(SCHEDULE_JSON), "bridge": rel(BRIDGE_JSON)}, "historical_mirrors_preserved": COMPAT_ALIASES, "legacy_thematic_titles": bridge.get("legacy_thematic_titles", []), "independent_restart_seeds": "DISALLOWED", "derived_restart_seed": seed}
    write_json(STATE_JSON, state)
    write_json(SCHEDULE_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "schedule_model": SCHEDULE_MODEL, "family_count": len(families), "passes": PASSES, "active_loop": "L01", "next_restart_seed": seed, "families": families, "loops": loops_})
    write_json(ROADMAP_JSON, read_json(SCHEDULE_JSON) if SCHEDULE_JSON.exists() else {})
    write_json(BRIDGE_JSON, bridge)
    write_json(AGENT_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "supervisor": {"agent_id": "Athena Prime", "role": "supervisory arbiter", "current_front": LIVE_MEMBRANE, "restart_seed": seed, "status": "ACTIVE"}, "agents": [{"agent_id": a, "name": n, "element": e, "role_order": i + 1, "current_front": front, "packet_space": "4^6 shared packet lattice", "active_packet_limit": SEAT_PER_AGENT, "handoff_target": h, "restart_seed": seed, "status": "ACTIVE" if i == 0 else "SEEDED"} for i, (a, n, e, front, h) in enumerate(AGENTS)]})
    write_json(LATTICE_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "contract": "SharedPacketLattice4096", "total_seats": SEAT_TOTAL, "active_seats": SEAT_ACTIVE, "dormant_seats": SEAT_DORMANT, "active_seats_per_agent": SEAT_PER_AGENT, "public_promotion_cap": PUBLIC_CAP, "rows": [{"seat_index": i, "seat_addr_6d": seat_addr(i), "activation_state": "ACTIVE" if i < SEAT_ACTIVE else "DORMANT", "preferred_master_role": AGENTS[(i // SEAT_PER_AGENT) % 4][0]} for i in range(SEAT_TOTAL)]})
    write_json(HALL_LATTICE_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "kind": "hall", "public_promotion_cap": PUBLIC_CAP, "loops": [{"loop_id": x["loop_id"], "loop_label": x["loop_label"], "family_code": x["family_code"], "pass_type": x["pass_type"], "public_promotions": hall_promotions(x) if x["loop_id"] == 1 else []} for x in loops_]})
    write_json(TEMPLE_LATTICE_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "kind": "temple", "public_promotion_cap": PUBLIC_CAP, "loops": [{"loop_id": x["loop_id"], "loop_label": x["loop_label"], "family_code": x["family_code"], "pass_type": x["pass_type"], "public_promotions": temple_promotions(x) if x["loop_id"] == 1 else []} for x in loops_]})
    qpack = {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "loop_id": "L01", "hall_promotions": hall_promotions(loop), "temple_promotions": temple_promotions(loop), "public_board_cap": {"hall": 8, "temple": 8}, "planner_only_public_promotion": True, "restart_seed": seed}
    write_json(QUEST_JSON, qpack)
    write_json(LP57_SYNTH_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "loop_id": "L01", "status": "ACTIVE_FROM_BRIDGE", "agent_id": "FA57-FIRE", "title": f"{loop['dominant_focus']} synthesis packet", "docs_gate": docs_gate(), "deep_root_authority": rel(DEEP_ROOT), "active_family": {"code": loop["family_code"], "name": loop["family_name"], "role": loop["family_role"]}, "legacy_bridge": {"prelude": bridge["prelude_bootstrap"]["source_legacy_loop"], "inherited_input": bridge["inherited_inputs"]["source_legacy_loop"]}, "next_restart_seed": seed})
    write_json(LP57_WORK_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "loop_id": "L01", "status": "SEEDED_PENDING_WORK", "agent_id": "FA57-AIR", "summary": "Canonical L01 is installed but work completion is pending artifact-bearing execution.", "restart_seed": seed})
    write_json(LP57_PRUNE_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "loop_id": "L01", "status": "SEED_CONTRACT_ONLY", "agent_id": "FA57-EARTH", "summary": "Compression law is installed; loop-level pruning awaits L01 work.", "restart_seed": seed})
    write_json(LP57_SUMMARY_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "loop_id": "L01", "status": "ACTIVE", "summary": f"{PRELUDE_ID} complete; L01 is the canonical active loop.", "restart_seed": seed})
    write_json(LP57_RECORDS_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "records": [{"loop_id": x["loop_label"], "pass_type": x["pass_type"], "family_code": x["family_code"], "family_name": x["family_name"], "lead_agent": x["lead_agent"], "status": x["status"], "receipt_paths": x["receipt_paths"], "restart_seed": seed if x["loop_id"] == 1 else f"{x['loop_label']} -> pending"} for x in loops_]})
    write_json(LP57_COORDS_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "coordinate_dimensions": ["Xs", "Ys", "Zs", "Ts", "Qs", "Rs", "Cs", "Fs", "Ms", "Ns", "Hs", "OmegaS"], "touched_nodes": [{"node_id": q["quest_id"], "seat_addr_6d": q["seat_addr_6d"], "coordinate_stamp": q["coordinate_stamp"], "agent_id": "FA57-WATER", "artifact_ref": rel(QUEST_JSON)} for q in hall_promotions(loop) + temple_promotions(loop)]})
    write_json(LP57_LEDGER_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "entries": [{"agent_id": f"LP57.L01.A{i+1}.D1.B0000.{a[2].upper()}", "loop_number": "L01", "pass_type": "Survey", "family_code": "A01", "parent_agent": a[0], "coordinate_stamp": coord("A01", a[1], "L01", a[0], a[2], "Square", "D1", "OK"), "source_region": "NERVOUS_SYSTEM under Survey", "action_type": ["synthesize", "plan", "implement", "compress"][i], "affected_nodes": [HALL_FEEDER, DEEPER_RECEIVER, RUNTIME_SEED], "summary_of_change": f"Seeded {a[1]} for canonical L01.", "reason_for_change": "Install the canonical 19x3 schedule and preserve bridge continuity.", "integration_gain": "One stronger alignment between A01 and the live spine.", "compression_gain": "One less competing 57-loop story.", "formalization_delta": "pending", "unresolved_followups": [seed], "linked_quests": [x['quest_id'] for x in hall_promotions(loop)[:2]], "linked_agents": [x[0] for x in AGENTS], "witness_class": "local-machine-witness", "artifact_ref": rel(STATE_JSON), "revision_confidence": 0.93, "truth_state": "OK", "timestamp_internal": DATE, "next_seed": seed} for i, a in enumerate(AGENTS)]})
    write_json(LP57_DELTA_JSON, {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "OK", "receipts": [{"loop_id": PRELUDE_ID, "status": "COMPLETED", "summary": "Legacy L01 Prime Lock preserved as migration prelude."}, {"loop_id": "L01", "status": "ACTIVE", "deep_synthesis_packet": rel(LP57_SYNTH_JSON), "planning_receipt": rel(QUEST_JSON), "work_receipt": rel(LP57_WORK_JSON), "pruning_receipt": rel(LP57_PRUNE_JSON), "cycle_summary": rel(LP57_SUMMARY_JSON), "restart_seed": seed}]})
    write_json(COMPAT_JSON, compat)
    write_json(COMPAT_PACKETS_JSON, qpack)
    write_json(COMPAT_REGISTRY_JSON, read_json(SCHEDULE_JSON))
    pending = {"generated_at": DATE, "protocol_id": PROTOCOL_ID, "truth": "PENDING verifier", "note": "Run verify_master_loop_57_orchestration.py"}
    write_json(VERIFY_JSON, pending)
    write_json(LP57_VERIFY_JSON, pending)


def protocol_markdown(families: list[dict], loops_: list[dict]) -> str:
    lines = ["# LP-57Omega Canonical 57-Loop Protocol", "", "## Executive Overview", "", f"- Docs gate: `{docs_gate()['state']}`", f"- Deep-root authority: `{rel(DEEP_ROOT)}`", f"- Family count: `{len(families)}`", f"- Passes: `{', '.join(PASSES)}`", f"- Bridge-remap: `{PRELUDE_ID}` plus inherited input from legacy L02", "", "## Family Map", ""]
    lines.extend([f"- `{f['code']}` `{f['root_name']}` :: `{f['status']}` :: {f['current_role']}" for f in families])
    lines.extend(["", "## Canonical 57-Loop Index", ""])
    lines.extend([f"- `{loop['loop_label']}` :: `{loop['pass_type']}` `{loop['family_code']}` `{loop['family_name']}`" for loop in loops_])
    lines.extend(["", "## Acceptance Gates", "", "- Docs gate remains blocked until both OAuth files exist.", "- `14_DEEPER...` remains the only deep authority.", "- `Q41/TQ06`, `Q42`, `TQ04`, `Q46`, `Q50`, and blocked `Q02` remain explicit.", "- Hall and Temple never exceed the live 8/8 caps.", "- Compatibility mirrors remain alias-only until converged."])
    return "\n".join(lines)


def render_active_run(state: dict) -> str:
    return "\n".join(["# ACTIVE RUN", "", wrap("MASTER_LOOP_57_BOOTSTRAP", "\n".join(["## LP-57Omega Prime Loop Bootstrap", "", f"- Date: `{DATE}`", f"- Docs Gate: `{state['docs_gate']['state']}`", f"- Protocol: `{DISPLAY}`", f"- Deep-root authority: `{state['deep_root_authority']}`", f"- Active membrane: `{LIVE_MEMBRANE}`", f"- Live spine: `{HALL_FEEDER} / {DEEPER_RECEIVER} / {RESERVE_FRONTIER} / {RUNTIME_SEED} / {BLOCKED_FRONT}`", f"- Shared lattice law: `{SEAT_TOTAL} indexed / {SEAT_ACTIVE} ACTIVE / {SEAT_DORMANT} DORMANT`", f"- Bridge-remap state: `{PRELUDE_ID} complete / L01 active`", f"- Current restart seed: `{state['current_cycle_summary']['next_restart_seed']}`"])), "", wrap("FOUR_AGENT_57_LOOP_PROGRAM", "\n".join(["## Four-Agent 57-Loop Compatibility Mirror", "", f"- Date: `{DATE}`", f"- Docs Gate: `{state['docs_gate']['state']}`", "- Status: `COMPATIBILITY_MIRROR`", f"- Canonical authority: `{rel(STATE_JSON)}` + `{rel(SCHEDULE_JSON)}` + `{rel(BRIDGE_JSON)}`", f"- Historical mirrors preserved: `{', '.join(COMPAT_ALIASES)}`", "- Independent restart seeds: `DISALLOWED`", f"- Derived restart seed: `{state['current_cycle_summary']['next_restart_seed']}`"])), "", wrap("AP6D_3D_7D_FULL_ACTIVATION", "\n".join(["## AP6D 3D-7D Full Activation", "", "- Docs Gate: `BLOCKED`", "- Status: `1024 ACTIVE / 3072 DORMANT / 4096 INDEXED`", "- Overlay law: `AP6D remains assistive and may not replace the live spine`", f"- Machine truth: `{rel(LATTICE_JSON)}`, `{rel(STATE_JSON)}`, `{rel(AGENT_JSON)}`"])), "", "## Current Corpus Law", "", f"- Protocol: `{DISPLAY}`", f"- Schedule model: `{SCHEDULE_MODEL}`", f"- Active loop: `{state['current_cycle_summary']['active_loop']}`", "", "## Current Restart Seed", "", f"`{state['current_cycle_summary']['next_restart_seed']}`"])


def write_markdown(state: dict, families: list[dict], loops_: list[dict]) -> None:
    seed = state["current_cycle_summary"]["next_restart_seed"]
    loop = loops_[0]
    hall_lines = [f"- `{q['quest_id']}` :: {q['title']} :: seat `{q['seat_addr_6d']}` :: restart `{q['restart_seed']}`" for q in hall_promotions(loop)]
    temple_lines = [f"- `{q['quest_id']}` :: {q['title']} :: seat `{q['seat_addr_6d']}` :: restart `{q['restart_seed']}`" for q in temple_promotions(loop)]
    write_text(PROTOCOL_MD, protocol_markdown(families, loops_))
    write_text(STATE_MD, f"# Master Loop 57 State\n\n- Protocol: `{DISPLAY}`\n- Schedule model: `{SCHEDULE_MODEL}`\n- Active loop: `{state['current_cycle_summary']['active_loop']}`\n- Restart seed: `{seed}`")
    write_text(DASHBOARD_MD, f"# Master Loop 57 Dashboard\n\n- Protocol: `{DISPLAY}`\n- Active loop: `{state['current_cycle_summary']['active_loop']}`\n- Restart seed: `{seed}`\n\n## Next 8 Canonical Loops\n\n" + "\n".join([f"- `{loop['loop_label']}` :: `{loop['pass_type']}` `{loop['family_code']}` `{loop['family_name']}`" for loop in loops_[:8]]))
    write_text(COMPAT_MD, f"# Four-Agent 57-Loop Program Compatibility Mirror\n\n- Status: `COMPATIBILITY_MIRROR`\n- Canonical authority: `{rel(STATE_JSON)}` + `{rel(SCHEDULE_JSON)}` + `{rel(BRIDGE_JSON)}`\n- Historical mirrors: `{', '.join(COMPAT_ALIASES)}`\n- Restart seed: `{seed}`")
    write_text(COMPAT_DASH_MD, f"# Four-Agent 57-Loop Dashboard Compatibility Mirror\n\n- Current loop: `{state['current_cycle_summary']['active_loop']}`\n- Active membrane: `{LIVE_MEMBRANE}`\n- Live spine: `{HALL_FEEDER} / {DEEPER_RECEIVER} / {RESERVE_FRONTIER} / {RUNTIME_SEED} / {BLOCKED_FRONT}`\n- Restart seed: `{seed}`")
    write_text(RESEARCHER_MD, f"# Synthesizer / Researcher State\n\n- Agent id: `FA57-FIRE`\n- Current front: `L01 Survey A01 plus carried witness from legacy L02`\n- Restart seed: `{seed}`")
    write_text(PLANNER_MD, f"# Planner / Architect State\n\n- Agent id: `FA57-WATER`\n- Current front: `L01 planner macro quests and packet promotions`\n- Restart seed: `{seed}`")
    write_text(WORKER_MD, f"# Worker / Adventurer State\n\n- Agent id: `FA57-AIR`\n- Current front: `TQ04-linked execution queue and promoted L01 packets`\n- Restart seed: `{seed}`")
    write_text(PRUNER_MD, f"# Pruner / Compressor / Defragmenter State\n\n- Agent id: `FA57-EARTH`\n- Current front: `Q46 reserve pressure plus compression shell`\n- Restart seed: `{seed}`")
    write_text(ACTIVE_RUN, render_active_run(state))
    write_text(BUILD_QUEUE, "# BUILD QUEUE\n\n## Priority Order\n\n" + "\n".join([f"{loop['loop_id']}. {loop['pass_type']} {loop['family_code']} {loop['family_name']}" for loop in loops_[:8]]) + f"\n\n## Restart Seed\n\n`{seed}`")
    write_text(ACTIVE_QUEUE, "# Active Queue\n\n" + wrap("MASTER_LOOP_57_QUEUE", f"## LP-57Omega Active Queue\n\n- Canonical authority: `{rel(STATE_JSON)}` + `{rel(SCHEDULE_JSON)}` + `{rel(BRIDGE_JSON)}`\n- Active loop: `{state['current_cycle_summary']['active_loop']}`\n- Live spine: `{HALL_FEEDER} / {DEEPER_RECEIVER} / {RESERVE_FRONTIER} / {RUNTIME_SEED} / {BLOCKED_FRONT}`\n- Restart seed: `{seed}`") + "\n\n## Current Hall Targets\n\n" + "\n".join([f"- `{q['quest_id']}` :: {q['title']}" for q in hall_promotions(loop)]) + "\n\n## Current Temple Targets\n\n" + "\n".join([f"- `{q['quest_id']}` :: {q['title']}" for q in temple_promotions(loop)]) + f"\n\n## Restart Seed\n\n`{seed}`")
    write_text(NEXT_PROMPT, "# Next Self Prompt\n\n" + wrap("MASTER_LOOP_57_NEXT_CONTRACT", f"## LP-57Omega Next Contract\n\n- Canonical authority: `{rel(STATE_JSON)}` + `{rel(SCHEDULE_JSON)}` + `{rel(BRIDGE_JSON)}`\n- Active membrane: `{LIVE_MEMBRANE}`\n- Live spine: `{HALL_FEEDER} / {DEEPER_RECEIVER} / {RESERVE_FRONTIER} / {RUNTIME_SEED} / {BLOCKED_FRONT}`\n- Current loop: `{state['current_cycle_summary']['active_loop']}`\n- Restart seed: `{seed}`") + "\n\n## Current Restart Seed\n\n`" + seed + "`\n\n## Prompt\n\n1. Check the Google Docs gate first.\n2. Read `master_loop_state_57.json`, `master_loop_schedule_57.json`, `master_loop_bridge_remap_57.json`, `master_agent_state_57.json`, and `master_loop_shared_lattice_4096.json`.\n3. Read the Hall quest board, Temple quest board, Temple state, active queue, active run, build queue, and the protocol manifest.\n4. Preserve the order `Athena Prime -> Fire -> Water -> Air -> Earth -> Athena Prime`.\n5. Keep AP6D assistive only and compatibility mirrors alias-only.\n6. End the pass with one artifact-backed move, one ledger update, one writeback, and one restart seed.")
    write_text(TEMPLE_STATE, "# Temple State\n\n" + wrap("MASTER_LOOP_57_TEMPLE_STATE", f"## LP-57Omega Temple State\n\n- Docs gate: `{state['docs_gate']['state']}`\n- Active membrane: `{LIVE_MEMBRANE}`\n- Current Temple support loop: `{state['current_cycle_summary']['active_loop']}`\n- Current Hall feeder: `{HALL_FEEDER}`\n- Deeper receiver: `{DEEPER_RECEIVER}`\n- Reserve frontier: `{RESERVE_FRONTIER}`\n- Runtime seed: `{RUNTIME_SEED}`\n- External blocker: `{BLOCKED_FRONT}`\n- Restart seed: `{seed}`") + f"\n\nDate: `{DATE}`\nTemple Status: `ONLINE / {DISPLAY}`\nFrontID: `TQ06-GUILDMASTER-HOURLY-PACKET-COUPLING`\nQuest: `TQ06: Install The Packet-Fed Guildmaster Coupling Loop`\nState: `ACTIVE`\nTruth: `OK`\n\n## Active Loop Temple Promotions\n\n" + "\n".join([f"- `{q['quest_id']}` :: {q['title']} :: `{q['restart_seed']}`" for q in temple_promotions(loop)]) + f"\n\n## Restart Seed\n\n`{seed}`")
    hall_board = "\n".join([
        wrap("AP6D_3D_7D_FULL_ACTIVATION", f"## AP6D 3D-7D Full Activation\n\n- Overlay law: `assistive only`\n- Machine truth: `{rel(LATTICE_JSON)}`, `{rel(STATE_JSON)}`, `{rel(AGENT_JSON)}`"),
        "",
        wrap("FOUR_AGENT_57_LOOP_PROGRAM", f"## Four-Agent 57-Loop Compatibility Mirror\n\n- Canonical authority: `{rel(STATE_JSON)}` + `{rel(SCHEDULE_JSON)}` + `{rel(BRIDGE_JSON)}`\n- Historical mirrors: `{', '.join(COMPAT_ALIASES)}`\n- Restart seed: `{seed}`"),
        "",
        "# Quest Board",
        "",
        wrap("MASTER_LOOP_57_HALL_QUEST", "## LP-57Omega Hall Quest Interface\n\n- Active loop: `" + state["current_cycle_summary"]["active_loop"] + "`\n- Live spine: `" + f"{HALL_FEEDER} / {DEEPER_RECEIVER} / {RESERVE_FRONTIER} / {RUNTIME_SEED} / {BLOCKED_FRONT}" + "`\n- Planner public cap: `8 Hall quests per active loop`\n\n### Active Loop Public Hall Promotions\n" + "\n".join(hall_lines)),
        "",
        "## Compatibility Memory",
        "",
        f"- `{', '.join(COMPAT_ALIASES)}` are historical aliases only.",
    ])
    temple_board = "\n".join([
        wrap("MASTER_LOOP_57_TEMPLE_QUEST", "## LP-57Omega Temple Quest Interface\n\n- Active loop: `" + state["current_cycle_summary"]["active_loop"] + "`\n- Live spine: `" + f"{HALL_FEEDER} / {DEEPER_RECEIVER} / {RESERVE_FRONTIER} / {RUNTIME_SEED} / {BLOCKED_FRONT}" + "`\n- Planner public cap: `8 Temple quests per active loop`\n\n### Active Loop Public Temple Promotions\n" + "\n".join(temple_lines)),
        "",
        wrap("AP6D_3D_7D_FULL_ACTIVATION", f"## AP6D 3D-7D Full Activation\n\n- Overlay law: `assistive only`\n- Machine truth: `{rel(LATTICE_JSON)}`, `{rel(STATE_JSON)}`, `{rel(AGENT_JSON)}`"),
        "",
        wrap("FOUR_AGENT_57_LOOP_PROGRAM", f"## Four-Agent 57-Loop Compatibility Mirror\n\n- Canonical authority: `{rel(STATE_JSON)}` + `{rel(SCHEDULE_JSON)}` + `{rel(BRIDGE_JSON)}`\n- Historical mirrors: `{', '.join(COMPAT_ALIASES)}`\n- Restart seed: `{seed}`"),
        "",
        "# Temple Quest Board",
        "",
        "Date: `2026-03-13`",
        "Docs Gate: `BLOCKED`",
        "",
        "## Canonical Governance Membrane",
        "",
        f"- Active membrane: `{LIVE_MEMBRANE}`",
        f"- Live spine: `{HALL_FEEDER} / {DEEPER_RECEIVER} / {RESERVE_FRONTIER} / {RUNTIME_SEED} / {BLOCKED_FRONT}`",
        f"- Canonical authority: `{rel(STATE_JSON)}` + `{rel(SCHEDULE_JSON)}` + `{rel(BRIDGE_JSON)}`",
        "",
        "## Historical Guard",
        "",
        f"- `{', '.join(COMPAT_ALIASES)}` remain historical or mirror-only.",
    ])
    write_text(HALL_BOARD, hall_board)
    write_text(TEMPLE_BOARD, temple_board)
    upsert(CHANGE_FEED, "MASTER_LOOP_57_CHANGE", f"## LP-57Omega Canonical 19x3 Refactor Installed\n\n- Docs gate: `BLOCKED`\n- Change: replaced the older thematic loop story with the canonical 19-family x 3-pass schedule\n- Current state: `{PRELUDE_ID} complete / {state['current_cycle_summary']['active_loop']} active`\n- Preserved live law: `{LIVE_MEMBRANE}` membrane with `{HALL_FEEDER}`, `{DEEPER_RECEIVER}`, `{RESERVE_FRONTIER}`, `{RUNTIME_SEED}`, and `{BLOCKED_FRONT}` kept explicit", after_heading=True)
    upsert(README_PATH, "MASTER_LOOP_57_README", f"## LP-57Omega Prime Loop Bootstrap\n\n- Schedule model: `{SCHEDULE_MODEL}`\n- Active loop: `{state['current_cycle_summary']['active_loop']}`\n- Restart seed: `{seed}`", after_heading=True)
    write_text(RECEIPT_MD, f"# 2026-03-13 LP-57Omega Canonical 19x3 Refactor\n\n- Protocol installed: `{DISPLAY}`\n- Bridge-remap state: `{PRELUDE_ID} complete / {state['current_cycle_summary']['active_loop']} active`\n- Schedule artifact: `{rel(SCHEDULE_JSON)}`\n- Bridge artifact: `{rel(BRIDGE_JSON)}`\n- Restart seed: `{seed}`")
    write_text(VERIFY_MD, "# Master Loop 57 Verification\n\n- Truth: `PENDING verifier`")
    write_text(PROTOCOL_VERIFY_MD, "# LP-57Omega Prime Loop Verification\n\n- Truth: `PENDING verifier`")


def main() -> None:
    families = parse_families()
    loops_ = build_loops(families)
    bridge = load_bridge()
    state = state_payload(families, loops_)
    write_generated_json(state, families, loops_, bridge)
    write_markdown(state, families, loops_)


if __name__ == "__main__":
    main()

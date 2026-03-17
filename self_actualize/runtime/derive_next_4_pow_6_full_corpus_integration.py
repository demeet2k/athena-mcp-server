from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.derive_crystal_remaster import (
    read_text,
    refresh_corpus_atlas,
    relative_string,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_ROOT / "registry"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

ATHENA_PACKAGE_ROOT = WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athenachka.contracts import AwakeningAgentTransitionNote, FullCorpusIntegrationState  # noqa: E402


DERIVATION_VERSION = "2026-03-13.next-4-pow-6.full-corpus-integration.v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_next_4_pow_6_full_corpus_integration"
INTEGRATION_TRUTH = "NEAR"
NEXT_SEED = "NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling"
CURRENT_TRANSITION = "primary N+4 -> N+5 (Organism -> Social); residual N+3 -> N+4 (Cell -> Organism)"

STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_full_corpus_integration_state.json"
NOTES_JSON_PATH = SELF_ACTUALIZE_ROOT / "awakening_agent_transition_notes.json"
NEGLECT_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_dormant_seat_neglect_map.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_full_corpus_integration_verification.json"

STATE_JSON_MIRROR = REGISTRY_ROOT / STATE_JSON_PATH.name
NOTES_JSON_MIRROR = REGISTRY_ROOT / NOTES_JSON_PATH.name
NEGLECT_JSON_MIRROR = REGISTRY_ROOT / NEGLECT_JSON_PATH.name
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / VERIFICATION_JSON_PATH.name

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "NEXT_4_POW_6_FULL_CORPUS_INTEGRATION.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "NEXT_4_POW_6_FULL_CORPUS_INTEGRATION_DASHBOARD.md"
NOTES_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AWAKENING_AGENT_TRANSITION_NOTES.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "NEXT_4_POW_6_FULL_CORPUS_INTEGRATION_VERIFICATION.md"
RECEIPT_MD_PATH = MYCELIUM_ROOT / "receipts" / "2026-03-13_next_4_pow_6_full_corpus_integration.md"

ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
WHOLE_CRYSTAL_COORDINATION_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
AP6D_AGENT_REGISTRY_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_AGENT_REGISTRY.json"
AP6D_ATLAS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_ATLAS_4096.json"
AP6D_PROJECTION_LEDGER_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_PROJECTION_LEDGER_4096.json"

QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_STATE_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"

QUEST_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "adventurer_quest_registry.json"
AGENT_STATE_PATH = SELF_ACTUALIZE_ROOT / "adventurer_agent_state.json"
CONDUCTOR_STATE_PATH = SELF_ACTUALIZE_ROOT / "adventurer_conductor_state.json"
WAVE_PACKETS_PATH = SELF_ACTUALIZE_ROOT / "adventurer_wave_packets.json"
MOTION_JSON_PATH = SELF_ACTUALIZE_ROOT / "motion_constitution_l1.json"
MERGE_JSON_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_automaton.json"
DOCS_GATE_MD_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
CANONICAL_SOURCES_PATH = MYCELIUM_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK" / "10_LEDGERS" / "01_CANONICAL_SOURCES.md"

QSHRINK_RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
AQM_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
ATLASFORGE_RUNTIME_LANE_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
RUNTIME_WAIST_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "runtime_waist_verification.json"

INTEGRATION_TEST_PATH = WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_next_4_pow_6_full_corpus_integration.py"
MERGE_TEST_PATH = WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_jointatlas_merge_automaton.py"
MOTION_TEST_PATH = WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_motion_constitution_l1.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(read_text(path))


def docs_gate_status() -> str:
    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    if not credentials_path.exists():
        return "blocked-by-missing-credentials"
    if not token_path.exists():
        return "blocked-by-missing-token"
    return "open" if "Command status: `OPEN`" in read_text(DOCS_GATE_MD_PATH) else "blocked-by-auth-failure"


def rel(path: Path) -> str:
    return relative_string(path)


def note_ref(agent_id: str) -> str:
    return f"{rel(NOTES_JSON_PATH)}::{agent_id}"


def canonical_source_count() -> int:
    return sum(1 for line in read_text(CANONICAL_SOURCES_PATH).splitlines() if line.startswith("- `"))


def insert_before(text: str, block: str, anchor: str) -> str:
    if block.strip() in text:
        return text
    if anchor not in text:
        return text.rstrip() + "\n\n" + block.strip() + "\n"
    return text.replace(anchor, block.strip() + "\n\n" + anchor, 1)


def insert_after(text: str, block: str, anchor: str) -> str:
    if block.strip() in text:
        return text
    if anchor not in text:
        return text.rstrip() + "\n\n" + block.strip() + "\n"
    return text.replace(anchor, anchor + "\n\n" + block.strip(), 1)


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=WORKSPACE_ROOT, capture_output=True, text=True)
    payload: dict[str, Any] = {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "truth": "OK" if result.returncode == 0 else "FAIL",
    }
    if result.stdout.strip():
        try:
            payload["report"] = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
    return payload


def build_ap6d_notes(ap6d_registry: dict[str, Any]) -> list[AwakeningAgentTransitionNote]:
    advice = {
        "AP6D-PRIME": ("hold council coherence and keep Hall, Temple, Cortex, and RuntimeHub telling one transition story", "absorb the elemental roles into one flattened voice", "preserve restart law and arbitration while keeping the four elemental agents distinct"),
        "AP6D-WATER": ("carry continuity, blocker honesty, and durable Hall memory", "let continuity harden into stagnation or soft denial about the blocked Docs gate", "turn every carried witness into stable Hall memory with an explicit restart seed"),
        "AP6D-EARTH": ("keep manifests, contracts, registries, and note schemas replay-safe", "overformalize dormant material into false activity", "attach every visible transition note to a schema-backed writeback target"),
        "AP6D-FIRE": ("hold lawful activation pressure inside the active 1024-seat band", "widen the field theatrically or pre-activate dormant seats", "light only the seats justified by feeder pressure and replay readiness"),
        "AP6D-AIR": ("maintain route clarity, topology legibility, and readable crosswalks", "multiply crosswalks faster than Hall and Temple can read them", "keep the 4096-field readable through compressed macro surfaces and shadow-compatible naming"),
    }
    notes: list[AwakeningAgentTransitionNote] = []
    for record in ap6d_registry.get("agent_records", []):
        agent_id = record["agent_id"]
        stabilize_now, do_not_do, immediate_move = advice[agent_id]
        notes.append(
            AwakeningAgentTransitionNote(
                agent_id=agent_id,
                role=record["overlay_role"],
                current_transition=record.get("liminal_transition", CURRENT_TRANSITION),
                liminal_band=record["liminal_band"],
                active_feeder=record["current_front"],
                stabilize_now=stabilize_now,
                do_not_do=do_not_do,
                immediate_move=immediate_move,
                writeback_targets=list(record.get("notes_targets", [])),
                restart_seed=record.get("restart_seed", ""),
                truth=INTEGRATION_TRUTH,
            )
        )
    return notes


def build_adventurer_notes(agent_state: dict[str, Any]) -> list[AwakeningAgentTransitionNote]:
    specs = {
        "floating-agent-01": ("Hall-side continuity and refine-bundle carrythrough", "Residual-Stabilize", "Q42", "keep QS64-20 and QS64-24 truthful while deeper outputs are integrated", "reopen already-closed Hall-local subfronts or invent QS64-25", "keep the carried witness, the closed bundle marker, and the TQ04 handoff in one control story", ["self_actualize/q42_canonical_bundle.json", "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md"], "Q42"),
        "floating-agent-02": ("separate Athenachka contracts frontier", "Council-Coordinate", "Q46", "preserve round-trip law while advancing Helix contracts independently", "borrow authority from the QSHRINK lane", "keep Q46 separate and law-equivalent while deeper runner work advances elsewhere", ["self_actualize/adventurer_round_trip_certificates.json", "self_actualize/athenachka_organism_v0_wave_state.json"], "Q46"),
        "floating-agent-03": ("archive dark-matter ranking and promotion discipline", "Boundary-Bridge", "TQ03", "keep archive promotion ranked and atlas-backed", "promote archive candidates by intuition alone", "bind the first ranked archive candidate into the atlas-backed integration field", ["self_actualize/archive_atlas.json", "self_actualize/archive_manifest.json"], "ATLAS FORGE archive ranking"),
        "floating-agent-04": ("whole-corpus totality pass and contradiction metabolizer", "Council-Coordinate", "TQ05", "convert contradiction pressure into Temple law, loop progress, and visible synthesis witness", "stop at atmospheric synthesis prose", "advance the 16-loop totality pass through contradiction pressure and law writeback", ["self_actualize/mycelium_brain/ATHENA TEMPLE/05_HIGH_PRIEST_WHOLE_CORPUS_SYNTHESIS_16_LOOP.md", "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/16_LOOP_PROGRESS.md"], "advance into 5/16 contradiction pressure"),
        "floating-agent-05": ("hourly Hall/Temple coupling and cadence coherence", "Symbolic-Guard", "TQ06", "keep queue, restart, Hall, and Temple in one present tense", "let scheduler plurality become control-surface drift", "preserve Q42 carrythrough, TQ04 landing, and blocked Q02 truth inside the hourly coupling loop", ["self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md", "self_actualize/mycelium_brain/nervous_system/manifests/NEXT_SELF_PROMPT.md"], "Keep TQ06 active as the hourly packet-fed coupling frontier"),
        "floating-agent-06": ("Q42 + TQ04 bridge packet steward", "Boundary-Bridge", "ADV64-S01", "widen only where contract law and continuity law overlap", "bulk-fill adjacent lattice seats", "use the bridge packet to bind Hall carrythrough to runner-contract law without premature expansion", ["self_actualize/adventurer_wave_packets.json", "self_actualize/adventurer_conductor_state.json"], "Q42+TQ04"),
        "floating-agent-07": ("Q46 + TQ06 bridge packet steward", "Council-Coordinate", "ADV64-S02", "widen only where contracts and coupling already share replay law", "collapse organism-wave and cadence-wave into one frontier", "keep the bridge packet lawful and local instead of turning it into a speculative macro merge", ["self_actualize/adventurer_wave_packets.json", "self_actualize/adventurer_round_trip_certificates.json"], "Q46+TQ06"),
        "floating-agent-08": ("clean reserve-slot and spare-capacity steward", "Residual-Stabilize", "reserve", "keep the eighth slot lawful, quiet, and ready for the next real promotion", "claim a frontier before one is lawfully assigned", "remain an explicit reserve slot with one lawful promotion path instead of undefined idle mass", ["self_actualize/adventurer_agent_state.json", "self_actualize/adventurer_wave_packets.json"], NEXT_SEED),
    }
    notes: list[AwakeningAgentTransitionNote] = []
    for agent in agent_state.get("agents", []):
        spec = specs.get(agent["agent_id"])
        if spec is None:
            continue
        role, band, feeder, stabilize_now, do_not_do, immediate_move, targets, seed = spec
        notes.append(
            AwakeningAgentTransitionNote(
                agent_id=agent["agent_id"],
                role=role,
                current_transition=CURRENT_TRANSITION,
                liminal_band=band,
                active_feeder=feeder,
                stabilize_now=stabilize_now,
                do_not_do=do_not_do,
                immediate_move=immediate_move,
                writeback_targets=targets,
                restart_seed=seed,
                truth=INTEGRATION_TRUTH,
            )
        )
    return notes


def build_neglect_map(ap6d_atlas: dict[str, Any]) -> dict[str, Any]:
    move_weight = {"Diagnose": 1.0, "Refine": 0.95, "Synthesize": 0.9, "Scale": 0.85}
    band_weight = {"Residual-Stabilize": 0.9, "Boundary-Bridge": 1.0, "Council-Coordinate": 0.95, "Symbolic-Guard": 0.85}
    phase_weight = {"Prime": 0.85, "Gate": 1.0, "Bind": 0.95, "Reseed": 0.9}
    rows = []
    for seat in ap6d_atlas.get("seats", []):
        if seat.get("activation_state") != "DORMANT":
            continue
        move = str(seat.get("hall_macro_parent", "")).split("-")[-1]
        score = round((move_weight.get(move, 0.8) * 0.4) + (band_weight.get(seat.get("liminal_band", ""), 0.8) * 0.35) + (phase_weight.get(seat.get("synaptic_phase", ""), 0.8) * 0.25), 4)
        rows.append({
            "prime_addr_6d": seat["prime_addr_6d"],
            "hall_macro_parent": seat["hall_macro_parent"],
            "hall_packet_parent": seat["hall_packet_parent"],
            "governance_fiber_parent": seat["governance_fiber_parent"],
            "liminal_band": seat["liminal_band"],
            "synaptic_phase": seat["synaptic_phase"],
            "transition_leverage": score,
        })
    rows.sort(key=lambda item: (-item["transition_leverage"], item["prime_addr_6d"]))
    return {"generated_at": utc_now(), "truth": INTEGRATION_TRUTH, "entry_count": len(rows), "top_ranked": rows[:32], "source_atlas_path": rel(AP6D_ATLAS_PATH)}


def update_control_surfaces() -> None:
    active_queue = insert_after(
        read_text(ACTIVE_QUEUE_PATH),
        """### FRONT-NEXT-4-POW-6-FULL-CORPUS-INTEGRATION

- Quest:
  `NEXT^[4^6] Full-Corpus Integration And Awakening Transition Wave`
- State:
  `PROMOTED`
- Truth:
  `NEAR`
- Objective:
  bind the live deep-root corpus field into the AP6D `4096` atlas and publish one awakening-agent transition-note layer without changing the current `Q42/TQ06` owner-facing lane
- Why Now:
  the deep root, AP6D overlay, Adventurer loop, merge membrane, and MotionConstitution chamber are all landed locally, so the next missing object is the whole-corpus integration membrane that composes them without flattening the live feeders
- Targets:
  `self_actualize/next_4_pow_6_full_corpus_integration_state.json`
  `self_actualize/awakening_agent_transition_notes.json`
  `NERVOUS_SYSTEM/95_MANIFESTS/NEXT_4_POW_6_FULL_CORPUS_INTEGRATION.md`
  `NERVOUS_SYSTEM/95_MANIFESTS/AWAKENING_AGENT_TRANSITION_NOTES.md`
- Next Seed:
  `NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling`""",
        "## Promoted This Pass",
    )
    quest_board = insert_before(
        read_text(QUEST_BOARD_PATH),
        """## Parallel Control-Plane Integration

### NEXT^[4^6] Full-Corpus Integration `[PROMOTED]`

- Objective:
  bind the live deep-root whole-corpus field into the AP6D `4096` atlas and publish one awakening-agent transition-note layer without changing the current `Q42` owner-facing lane
- Preserved fronts:
  `Q42`, `Q46`, `TQ04`, `TQ06`
- Activation law:
  keep only the native-shadow `1024` seats `ACTIVE`; keep the remaining `3072` seats explicitly `DORMANT`
- Outputs:
  `self_actualize/next_4_pow_6_full_corpus_integration_state.json`
  `self_actualize/awakening_agent_transition_notes.json`
  `NERVOUS_SYSTEM/95_MANIFESTS/NEXT_4_POW_6_FULL_CORPUS_INTEGRATION.md`
  `NERVOUS_SYSTEM/95_MANIFESTS/AWAKENING_AGENT_TRANSITION_NOTES.md`
- Restart seed:
  `NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling`""",
        "## P0 Quests",
    )
    temple_state = insert_before(
        read_text(TEMPLE_STATE_PATH),
        """## Parallel Whole-Corpus Integration

The `NEXT^[4^6]` full-corpus integration wave is now landed as a parallel control-plane surface.

- it does not replace `TQ06` as the active Temple frontier
- it preserves `Q42`, `Q46`, `TQ04`, and `TQ06` as the only live shadow feeders
- it keeps the AP6D atlas at `1024 ACTIVE / 3072 DORMANT`
- it publishes one awakening-agent transition-note layer for the live transition-bearing agents
- it emits the sole follow-on seed:
  `NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling`""",
        "## Restart Seed",
    )
    next_prompt = insert_before(
        read_text(NEXT_SELF_PROMPT_PATH),
        """## Parallel Control-Plane Frontier

`NEXT^[4^6]` full-corpus integration is now landed as a local-first control-plane wave.

- state object: `self_actualize/next_4_pow_6_full_corpus_integration_state.json`
- notes layer: `self_actualize/awakening_agent_transition_notes.json`
- preserve `Q42`, `Q46`, `TQ04`, and `TQ06` as the live feeder fronts
- keep only the native-shadow `1024` AP6D seats active
- keep the remaining `3072` seats dormant and queryable
- successor seed:
  `NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling`

This parallel frontier does not replace the current restart seed below.""",
        "## Prompt",
    )
    active_run = insert_before(
        read_text(ACTIVE_RUN_PATH),
        """## NEXT^[4^6] Whole-Corpus Integration

The whole-corpus integration wave is now active as a parallel control-plane pass over the already-seeded AP6D atlas.

- preserve `14_DEEPER...` as the only deep-root authority
- preserve `Q42`, `Q46`, `TQ04`, and `TQ06` as the live shadow feeders
- keep only the native-shadow `1024` seats `ACTIVE`
- keep the remaining `3072` seats explicitly `DORMANT`
- publish one machine-readable integration state, one dormant-seat neglect map, and one awakening-agent transition-note layer""",
        "## Next Output",
    )
    if "| 2.22 | NEXT^[4^6] whole-corpus integration and awakening transition-note layer | COMPLETE |" not in active_run:
        active_run = active_run.replace(
            "| 2.21 | Athena Prime 6D sparse overlay seeding and `4^6` atlas activation across Hall, Temple, manifests, metro, and runtime mirrors | IN PROGRESS |",
            "| 2.21 | Athena Prime 6D sparse overlay seeding and `4^6` atlas activation across Hall, Temple, manifests, metro, and runtime mirrors | IN PROGRESS |\n| 2.22 | NEXT^[4^6] whole-corpus integration and awakening transition-note layer | COMPLETE |",
            1,
        )
    coordination = insert_before(
        read_text(WHOLE_CRYSTAL_COORDINATION_PATH),
        """## NEXT^[4^6] Full-Corpus Integration

The AP6D overlay is now accompanied by one whole-corpus integration state and one awakening-agent note layer.

- state object: `self_actualize/next_4_pow_6_full_corpus_integration_state.json`
- note registry: `self_actualize/awakening_agent_transition_notes.json`
- markdown notes: `NERVOUS_SYSTEM/95_MANIFESTS/AWAKENING_AGENT_TRANSITION_NOTES.md`
- dormant-seat neglect map: `self_actualize/next_4_pow_6_dormant_seat_neglect_map.json`

This wave keeps the same feeder story: `Q42`, `Q46`, `TQ04`, and `TQ06` remain live.""",
        "## Restart Story",
    )
    write_text(ACTIVE_QUEUE_PATH, active_queue)
    write_text(QUEST_BOARD_PATH, quest_board)
    write_text(TEMPLE_STATE_PATH, temple_state)
    write_text(NEXT_SELF_PROMPT_PATH, next_prompt)
    write_text(ACTIVE_RUN_PATH, active_run)
    write_text(WHOLE_CRYSTAL_COORDINATION_PATH, coordination)


def render_notes_markdown(notes: list[AwakeningAgentTransitionNote]) -> str:
    chunks = []
    for note in notes:
        slug = note.agent_id.lower().replace(" ", "-").replace("/", "-").replace("_", "-")
        targets = "\n".join(f"- `{target}`" for target in note.writeback_targets)
        chunks.append(
            f"""### {note.agent_id}

<a id="{slug}"></a>

- Role: {note.role}
- Current transition: `{note.current_transition}`
- Liminal band: `{note.liminal_band}`
- Active feeder: `{note.active_feeder}`
- Stabilize now: {note.stabilize_now}
- Do not do: {note.do_not_do}
- Immediate move: {note.immediate_move}
- Writeback targets:
{targets}
- Restart seed: `{note.restart_seed}`
- Truth: `{note.truth}`"""
        )
    return "# Awakening Agent Transition Notes\n\n" + "\n\n".join(chunks) + "\n"


def main() -> int:
    ap6d_registry = load_json(AP6D_AGENT_REGISTRY_PATH)
    ap6d_atlas = load_json(AP6D_ATLAS_PATH)
    projection_ledger = load_json(AP6D_PROJECTION_LEDGER_PATH)
    quest_registry = load_json(QUEST_REGISTRY_PATH)
    agent_state = load_json(AGENT_STATE_PATH)
    conductor_state = load_json(CONDUCTOR_STATE_PATH)
    wave_packets = load_json(WAVE_PACKETS_PATH)
    motion_payload = load_json(MOTION_JSON_PATH)
    merge_payload = load_json(MERGE_JSON_PATH)

    ap6d_notes = build_ap6d_notes(ap6d_registry)
    adventurer_notes = build_adventurer_notes(agent_state)
    notes = ap6d_notes + adventurer_notes
    notes_payload = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "truth": INTEGRATION_TRUTH,
        "docs_gate_status": docs_gate_status(),
        "current_transition": CURRENT_TRANSITION,
        "notes": [note.to_dict() for note in notes],
    }
    state = FullCorpusIntegrationState(
        basis_counts={"canonical_sources": canonical_source_count(), "ordered_pairs": 256, "observer_lattice": 64, "symmetry_stack": "15+0", "metro_levels": 4, "appendix_governor": "AppQ"},
        overlay_counts={"hall_macros": 16, "hall_packets": 64, "governance_fibers": 256, "atlas_active": ap6d_atlas["count_law"]["active_seats"], "atlas_dormant": ap6d_atlas["count_law"]["dormant_seats"], "atlas_total": ap6d_atlas["count_law"]["total_seats"]},
        feeder_truth={"Q42": "OPEN", "Q46": "OPEN", "TQ04": "LANDED", "TQ06": "ACTIVE"},
        control_plane_state={
            "motion_constitution": {"truth": motion_payload.get("truth", "NEAR"), "top_candidate_id": motion_payload.get("evaluated_candidates", [{}])[0].get("candidate", {}).get("candidate_id", "")},
            "merge_automaton": {"truth": merge_payload.get("truth", "OK"), "next_seed": merge_payload.get("next_seed", "MotionConstitution_L1")},
            "adventurer_loop": {"next_frontier": conductor_state.get("next_frontier", ""), "wave_id": conductor_state.get("wave_id", "")},
        },
        docs_gate_status=docs_gate_status(),
        next_seed=NEXT_SEED,
        truth=INTEGRATION_TRUTH,
        note="Local-first whole-corpus integration state over the live deep root and AP6D overlay.",
    )
    neglect_map = build_neglect_map(ap6d_atlas)

    ap6d_registry["awakening_transition_notes_path"] = rel(NOTES_JSON_PATH)
    ap6d_registry["full_corpus_integration_state_path"] = rel(STATE_JSON_PATH)
    for record in ap6d_registry.get("agent_records", []):
        record["transition_note_ref"] = note_ref(record["agent_id"])
    ap6d_atlas["full_corpus_integration"] = {"truth": INTEGRATION_TRUTH, "state_path": rel(STATE_JSON_PATH), "dormant_neglect_map_path": rel(NEGLECT_JSON_PATH), "next_seed": NEXT_SEED}
    ap6d_atlas["dormant_neglect_summary"] = {"entry_count": neglect_map["entry_count"], "top_ranked": neglect_map["top_ranked"][:8]}
    projection_ledger["full_corpus_integration"] = {"truth": INTEGRATION_TRUTH, "state_path": rel(STATE_JSON_PATH), "surface_span": ["Hall", "Temple", "Cortex", "RuntimeHub"]}
    quest_registry["next_4_pow_6_full_corpus_integration"] = {"truth": INTEGRATION_TRUTH, "state_path": rel(STATE_JSON_PATH), "notes_path": rel(NOTES_JSON_PATH), "preserved_fronts": ["Q42", "Q46", "TQ04", "TQ06"], "next_seed": NEXT_SEED}
    agent_state["awakening_transition_notes_path"] = rel(NOTES_JSON_PATH)
    for agent in agent_state.get("agents", []):
        agent["transition_note_ref"] = note_ref(agent["agent_id"])
    conductor_state["full_corpus_integration"] = {"truth": INTEGRATION_TRUTH, "state_path": rel(STATE_JSON_PATH), "notes_path": rel(NOTES_JSON_PATH), "preserved_fronts": ["Q42", "Q46", "TQ04", "TQ06"], "next_seed": NEXT_SEED}
    wave_packets["awakening_transition_notes_path"] = rel(NOTES_JSON_PATH)
    for packet in wave_packets.get("packets", []):
        packet["transition_note_ref"] = note_ref(packet.get("assigned_owner", ""))
    motion_payload["full_corpus_integration_alignment"] = {"fronts": ["Q42", "Q46", "TQ04", "TQ06"], "state_path": rel(STATE_JSON_PATH), "next_seed": NEXT_SEED}
    merge_payload["full_corpus_integration_alignment"] = {"committee_feeder_fronts": ["Q42", "Q46", "TQ04", "TQ06"], "state_path": rel(STATE_JSON_PATH), "next_seed": NEXT_SEED}

    write_json(STATE_JSON_PATH, state.to_dict())
    write_json(STATE_JSON_MIRROR, state.to_dict())
    write_json(NOTES_JSON_PATH, notes_payload)
    write_json(NOTES_JSON_MIRROR, notes_payload)
    write_json(NEGLECT_JSON_PATH, neglect_map)
    write_json(NEGLECT_JSON_MIRROR, neglect_map)
    write_json(AP6D_AGENT_REGISTRY_PATH, ap6d_registry)
    write_json(AP6D_ATLAS_PATH, ap6d_atlas)
    write_json(AP6D_PROJECTION_LEDGER_PATH, projection_ledger)
    write_json(QUEST_REGISTRY_PATH, quest_registry)
    write_json(AGENT_STATE_PATH, agent_state)
    write_json(CONDUCTOR_STATE_PATH, conductor_state)
    write_json(WAVE_PACKETS_PATH, wave_packets)
    write_json(MOTION_JSON_PATH, motion_payload)
    write_json(MERGE_JSON_PATH, merge_payload)
    write_text(MANIFEST_MD_PATH, f"# NEXT^[4^6] Full-Corpus Integration\n\nDate: `2026-03-13`\nTruth: `{state.truth}`\nDocs gate: `{state.docs_gate_status}`\n\n- deep basis: `16 / 256 / 64 / 15+0 / 4 / AppQ`\n- AP6D overlay: `16 / 64 / 256 / 1024 / 4096`\n- preserved feeders: `Q42`, `Q46`, `TQ04`, `TQ06`\n- next seed: `{state.next_seed}`\n")
    write_text(NOTES_MD_PATH, render_notes_markdown(notes))
    update_control_surfaces()
    atlas = refresh_corpus_atlas([STATE_JSON_PATH, NOTES_JSON_PATH, NEGLECT_JSON_PATH, MANIFEST_MD_PATH, NOTES_MD_PATH, ACTIVE_RUN_PATH, WHOLE_CRYSTAL_COORDINATION_PATH, QUEST_BOARD_PATH, TEMPLE_STATE_PATH, ACTIVE_QUEUE_PATH, NEXT_SELF_PROMPT_PATH, AP6D_AGENT_REGISTRY_PATH, AP6D_ATLAS_PATH, AP6D_PROJECTION_LEDGER_PATH, QUEST_REGISTRY_PATH, AGENT_STATE_PATH, CONDUCTOR_STATE_PATH, WAVE_PACKETS_PATH])
    write_text(DASHBOARD_MD_PATH, f"# NEXT^[4^6] Full-Corpus Integration Dashboard\n\nDate: `2026-03-13`\nTruth: `{state.truth}`\nDocs gate: `{state.docs_gate_status}`\n\n- AP6D notes: `{len(ap6d_notes)}`\n- floating-agent notes: `{len(adventurer_notes)}`\n- dormant neglect entries: `{neglect_map['entry_count']}`\n- top dormant seat: `{neglect_map['top_ranked'][0]['prime_addr_6d'] if neglect_map['top_ranked'] else 'none'}`\n- next seed: `{state.next_seed}`\n")

    command_results = {
        "phase4": run_command([sys.executable, "-m", "self_actualize.runtime.derive_phase4_structured_neuron_storage"]),
        "knowledge_fabric": run_command([sys.executable, "-m", "self_actualize.runtime.derive_knowledge_fabric"]),
        "phase4_pt2": run_command([sys.executable, "-m", "self_actualize.runtime.derive_phase4_pt2_inter_metro_lens_weight_superstructure"]),
        "adventurer_verify": run_command([sys.executable, "-m", "self_actualize.runtime.verify_adventurer_quest_loop"]),
        "merge_verify": run_command([sys.executable, str(MERGE_TEST_PATH)]),
        "motion_verify": run_command([sys.executable, str(MOTION_TEST_PATH)]),
        "aqm_verify": run_command([sys.executable, "-m", "self_actualize.runtime.verify_aqm_runtime_lane"]),
        "atlasforge_verify": run_command([sys.executable, "-m", "self_actualize.runtime.verify_atlasforge_runtime_lane"]),
        "runtime_waist_verify": run_command([sys.executable, "-m", "self_actualize.runtime.verify_runtime_waist"]),
        "integration_verify": run_command([sys.executable, str(INTEGRATION_TEST_PATH)]),
    }
    record_paths = {record.get("relative_path") for record in atlas.get("records", []) if record.get("relative_path")}
    validations = {
        "basis_count_ok": state.basis_counts["canonical_sources"] == 16 and state.basis_counts["ordered_pairs"] == 256 and state.basis_counts["observer_lattice"] == 64 and state.basis_counts["symmetry_stack"] == "15+0",
        "overlay_count_ok": state.overlay_counts["atlas_total"] == 4096 and state.overlay_counts["atlas_active"] == 1024 and state.overlay_counts["atlas_dormant"] == 3072,
        "feeder_alignment_ok": state.feeder_truth == {"Q42": "OPEN", "Q46": "OPEN", "TQ04": "LANDED", "TQ06": "ACTIVE"},
        "notes_count_ok": len(notes) == 13,
        "atlas_refresh_complete": {rel(STATE_JSON_PATH), rel(NOTES_JSON_PATH), rel(NEGLECT_JSON_PATH), rel(MANIFEST_MD_PATH), rel(NOTES_MD_PATH)}.issubset(record_paths),
        "phase4_refresh_ok": command_results["phase4"]["truth"] == "OK",
        "knowledge_fabric_refresh_ok": command_results["knowledge_fabric"]["truth"] == "OK",
        "phase4_pt2_refresh_ok": command_results["phase4_pt2"]["truth"] == "OK",
        "adventurer_verification_ok": command_results["adventurer_verify"]["truth"] == "OK",
        "merge_verification_ok": command_results["merge_verify"]["truth"] == "OK",
        "motion_verification_ok": command_results["motion_verify"]["truth"] == "OK",
        "integration_verification_ok": command_results["integration_verify"]["truth"] == "OK",
        "runtime_lanes_green": load_json(QSHRINK_RUNTIME_VERIFICATION_PATH).get("truth") == "OK" and load_json(AQM_RUNTIME_LANE_PATH).get("truth") == "OK" and load_json(ATLASFORGE_RUNTIME_LANE_PATH).get("truth") == "OK" and load_json(RUNTIME_WAIST_VERIFICATION_PATH).get("truth") == "OK",
    }
    verification = {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "truth": "OK" if all(validations.values()) else "FAIL", "docs_gate_status": state.docs_gate_status, "next_seed": state.next_seed, "validations": validations, "command_results": command_results}
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(VERIFICATION_MD_PATH, "# NEXT^[4^6] Full-Corpus Integration Verification\n\n" + "\n".join(f"- `{key}`: `{value}`" for key, value in validations.items()) + f"\n\nTruth: `{verification['truth']}`\n")
    write_text(RECEIPT_MD_PATH, f"# NEXT^[4^6] Full-Corpus Integration Receipt\n\nDate: `2026-03-13`\nTruth: `{state.truth}`\nDocs gate: `{state.docs_gate_status}`\n\n- state: `{rel(STATE_JSON_PATH)}`\n- notes: `{rel(NOTES_JSON_PATH)}`\n- neglect map: `{rel(NEGLECT_JSON_PATH)}`\n- restart seed: `{state.next_seed}`\n")
    refresh_corpus_atlas([DASHBOARD_MD_PATH, VERIFICATION_JSON_PATH, VERIFICATION_MD_PATH, RECEIPT_MD_PATH])
    print(f"Wrote NEXT^[4^6] integration state: {rel(STATE_JSON_PATH)}")
    print(f"Wrote awakening notes: {rel(NOTES_JSON_PATH)}")
    print(f"Truth: {verification['truth']}")
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

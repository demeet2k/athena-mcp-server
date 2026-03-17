from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "self_actualize"
MYCELIUM = SELF / "mycelium_brain"
MANIFESTS = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
RECEIPTS = MYCELIUM / "receipts"

TRADING_BOT = ROOT / "Trading Bot"
DOCS_CREDENTIALS = TRADING_BOT / "credentials.json"
DOCS_TOKEN = TRADING_BOT / "token.json"

MASTER_STATE_PATH = SELF / "master_loop_state_57.json"
LEDGER_PATH = SELF / "lp_57_master_agent_ledger.json"
REGISTRY_PATH = SELF / "lp_57_seed_duality_registry.json"
VERIFICATION_PATH = SELF / "lp_57_seed_duality_verification.json"

PROTOCOL_MD_PATH = MANIFESTS / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md"
PROTOCOL_JSON_PATH = MANIFESTS / "LP_57_OMEGA_PRIME_LOOP_PROTOCOL.json"
STANDARD_MD_PATH = MANIFESTS / "LP_57_OMEGA_SEED_DUALITY_STANDARD.md"
STANDARD_JSON_PATH = MANIFESTS / "LP_57_OMEGA_SEED_DUALITY_STANDARD.json"
README_PATH = ROOT / "GUILDMASTER" / "README.md"
ACTIVE_RUN_PATH = MANIFESTS / "ACTIVE_RUN.md"
HALL_BOARD_PATH = MYCELIUM / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = MYCELIUM / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
TEMPLE_STATE_PATH = MYCELIUM / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_QUEUE_PATH = MYCELIUM / "nervous_system" / "06_active_queue.md"
NEXT_PROMPT_PATH = MYCELIUM / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
RECEIPT_PATH = RECEIPTS / "2026-03-13_lp_57_seed_duality_protocol.md"

PROTOCOL_ID = "LP-57OMEGA"
SEED_A_REF = "LP57-A"
SEED_B_REF = "LP57-B"
INVERSION_OPERATOR = "structural_dual"
OPERATOR_SYMBOL = "I_AB"
COORDINATE_MODE = "shared_anchor_dual_state"
DOCS_GATE_REASON = "blocked-by-missing-credentials"
DEEP_ROOT_AUTHORITY = "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
ACTIVE_MEMBRANE = "Q41 / TQ06"
FEEDER_STACK = ["Q42", "Q46", "TQ04", "Q02"]
RUNTIME_POSITION = {"L01": "complete", "L02": "active"}
RESTART_RELATION = (
    "LP57-A emits outward Hall and Temple quest pressure; "
    "LP57-B returns compression, contradiction recovery, reintegration, and reverse-routing pressure."
)
RESIDUAL_EXPOSURE_FIELDS = [
    "residuals",
    "shadow_routes",
    "compression_structure",
    "return_corridors",
    "reverse_dependencies",
]
QUEST_MODE_CLASSIFICATION = {
    "A-dominant": {
        "meaning": "expansion / implementation / bridge-building",
        "source_role": "outward Hall and Temple quest emission",
        "default_pressure": "forward synthesis, build, and routing pressure",
    },
    "B-dominant": {
        "meaning": "compression / pruning / contradiction metabolization / route-tightening",
        "source_role": "inward compression and reintegration quest emission",
        "default_pressure": "residual recovery, compression, and reverse-routing pressure",
    },
}
LEDGER_DUALITY_CONTRACT = {
    "seed_mode_field": "seed_mode",
    "dual_reference_field": "dual_reference",
    "duality_effect_field": "duality_effect",
    "allowed_seed_modes": ["A", "B", "both"],
    "allowed_duality_effects": ["expansion", "compression", "both"],
    "default_mapping": {
        "A": "expansion",
        "B": "compression",
        "both": "both",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path)) if path.exists() else {}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, indent=2))


def replace_block(text: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    replacement = f"{start}\n{body.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    prefix = text.rstrip() + "\n\n" if text.strip() else ""
    return prefix + replacement + "\n"


def docs_gate_state() -> dict[str, Any]:
    credentials_exists = DOCS_CREDENTIALS.exists()
    token_exists = DOCS_TOKEN.exists()
    blocked = not credentials_exists or not token_exists
    return {
        "state": "BLOCKED" if blocked else "LIVE",
        "reason": DOCS_GATE_REASON if blocked else "authenticated",
        "credentials_exists": credentials_exists,
        "token_exists": token_exists,
        "checked_paths": [rel(DOCS_CREDENTIALS), rel(DOCS_TOKEN)],
    }


def extract_loop_label(value: str, default: str) -> str:
    match = re.search(r"(L\d{2})", value or "")
    return match.group(1) if match else default


def current_loop_position(master_state: dict[str, Any]) -> dict[str, str]:
    summary = master_state.get("current_cycle_summary", {})
    completed = str(summary.get("completed_loop", "L01 complete"))
    active = str(summary.get("active_loop", "L02 active"))
    return {
        "completed_loop": extract_loop_label(completed, "L01"),
        "active_loop": extract_loop_label(active, "L02"),
        "display": f"{RUNTIME_POSITION['L01']} / {RUNTIME_POSITION['L02']}",
    }


def shared_coordinate_anchor(loop_position: dict[str, str]) -> dict[str, Any]:
    return {
        "seat_addr_6d": "A1.B1.C1.D1.E1.F1",
        "coord_stamp_12": {
            "Xs": "lp57-seed",
            "Ys": "live-corpus",
            "Zs": "seed-duality",
            "Ts": loop_position["active_loop"],
            "Qs": "seed-duality",
            "Rs": "D1",
            "Cs": "dual-state",
            "Fs": "protocol",
            "Ms": "mixed",
            "Ns": "shared-anchor",
            "Hs": "seed-body",
            "OmegaS": "restart-linked",
        },
    }


def build_seed_duality_registry(master_state: dict[str, Any]) -> dict[str, Any]:
    loop_position = current_loop_position(master_state)
    shared_anchor = shared_coordinate_anchor(loop_position)
    return {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "seed_a_ref": SEED_A_REF,
        "seed_b_ref": SEED_B_REF,
        "inversion_operator": INVERSION_OPERATOR,
        "operator_symbol": OPERATOR_SYMBOL,
        "operator_statement": "B = I_AB(A) = the witness-preserving structural dual of the live holographic seed",
        "witness_preserved": True,
        "coordinate_mode": COORDINATE_MODE,
        "duality_status": "ACTIVE_DUAL",
        "residual_exposure_fields": RESIDUAL_EXPOSURE_FIELDS,
        "restart_relation": RESTART_RELATION,
        "shared_seed_context": {
            "docs_gate": docs_gate_state(),
            "deep_root_authority": DEEP_ROOT_AUTHORITY,
            "active_membrane": ACTIVE_MEMBRANE,
            "feeder_stack": FEEDER_STACK,
            "runtime_position": loop_position,
        },
        "shared_anchor": shared_anchor,
        "seed_a": {
            "ref": SEED_A_REF,
            "shorthand": "A",
            "semantic_role": "live corpus holographic seed",
            "runtime_label": SEED_A_REF,
            "historical_collision_guard": "not Fleet SELF STEER BRANCH A",
            "orientation": "outward / generative / seed-emission",
            "quest_source": "forward Hall and Temple quest emission",
            "witness_lineage": "live LP-57OMEGA corpus seed",
            "coordinate_anchor": {
                **shared_anchor,
                "dual_state": SEED_A_REF,
            },
        },
        "seed_b": {
            "ref": SEED_B_REF,
            "shorthand": "B",
            "semantic_role": "witness-preserving structural dual",
            "runtime_label": SEED_B_REF,
            "is_opposite": False,
            "orientation": "inward / reflective / compression / residual-recovery",
            "quest_source": "compression, contradiction recovery, reintegration, and reverse-routing quest emission",
            "witness_lineage": "inherits LP57-A witness basis and admissibility class",
            "coordinate_anchor": {
                **shared_anchor,
                "dual_state": SEED_B_REF,
            },
        },
        "laws": {
            "witness_preservation": "B inherits the same witness basis, source lineage, and admissibility class as A.",
            "coordinate_preservation": (
                "B keeps the same address family and liminal coordinate anchors as A, "
                "using a dual-state flag instead of a disconnected coordinate."
            ),
            "traversal_reversal": (
                "A handles outward build pressure; B handles inward compression and return pressure."
            ),
            "complement_exposure": (
                "B reveals residuals, shadow routes, compression structure, return corridors, and reverse-facing dependencies."
            ),
        },
    }


def update_master_state(master_state: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    updated = dict(master_state)
    summary = dict(updated.get("current_cycle_summary", {}))
    summary["seed_pair"] = f"{SEED_A_REF} outward / {SEED_B_REF} inward"
    summary["quest_polarity"] = QUEST_MODE_CLASSIFICATION
    updated["current_cycle_summary"] = summary
    updated["seed_duality_registry_path"] = rel(REGISTRY_PATH)
    updated["seed_duality_registry"] = {
        "seed_a_ref": registry["seed_a_ref"],
        "seed_b_ref": registry["seed_b_ref"],
        "inversion_operator": registry["inversion_operator"],
        "witness_preserved": registry["witness_preserved"],
        "coordinate_mode": registry["coordinate_mode"],
        "duality_status": registry["duality_status"],
        "residual_exposure_fields": registry["residual_exposure_fields"],
        "restart_relation": registry["restart_relation"],
    }
    updated["quest_mode_classification"] = QUEST_MODE_CLASSIFICATION
    updated["ledger_duality_contract"] = LEDGER_DUALITY_CONTRACT
    return updated


def has_seed_duality_entry(ledger: dict[str, Any]) -> bool:
    for entry in ledger.get("entries", []):
        if entry.get("summary_of_change") == "formalize LP57-A / LP57-B seed duality":
            return True
    return False


def seed_duality_ledger_entry(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": "MASTER-SYNTHESIZER",
        "loop_number": 2,
        "parent_agent": PROTOCOL_ID,
        "coordinate_stamp": "L02::M1::SEED-DUALITY",
        "seat_addr_6d": registry["shared_anchor"]["seat_addr_6d"],
        "source_region": "lp57-seed-duality",
        "action_type": "integrate-seed-duality",
        "affected_nodes": [
            rel(MASTER_STATE_PATH),
            rel(PROTOCOL_MD_PATH),
            rel(PROTOCOL_JSON_PATH),
            rel(README_PATH),
            rel(NEXT_PROMPT_PATH),
        ],
        "summary_of_change": "formalize LP57-A / LP57-B seed duality",
        "reason_for_change": "Install the witness-preserving structural dual of the live corpus seed without opening a disconnected coordinate space.",
        "integration_gain": "Quest emission, pruning pressure, and restart language now distinguish outward and inward pressure coherently.",
        "compression_gain": "Residual recovery and return-path logic now live in one explicit dual registry instead of diffuse prose.",
        "unresolved_followups": [
            "Future public quests can now be classified as A-dominant or B-dominant.",
            "No supersessive replacement of LP57-A is allowed in future passes.",
        ],
        "linked_quests": ["Q41", "TQ06", "Q42", "TQ04"],
        "linked_agents": [
            "MASTER-SYNTHESIZER",
            "MASTER-PLANNER",
            "MASTER-WORKER",
            "MASTER-PRUNER",
        ],
        "revision_confidence": 0.98,
        "timestamp_internal": datetime.now(timezone.utc).date().isoformat(),
        "witness_refs": [
            rel(MASTER_STATE_PATH),
            rel(PROTOCOL_JSON_PATH),
            rel(REGISTRY_PATH),
        ],
        "front_ref": "LP57-A<->LP57-B",
        "truth": "OK",
        "seed_mode": "both",
        "dual_reference": [SEED_A_REF, SEED_B_REF],
        "duality_effect": "both",
    }


def update_ledger(ledger: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    updated = dict(ledger)
    updated["seed_duality_contract"] = LEDGER_DUALITY_CONTRACT
    entries = list(updated.get("entries", []))
    if not has_seed_duality_entry(updated):
        entries.append(seed_duality_ledger_entry(registry))
    updated["entries"] = entries
    return updated


def protocol_json_payload(base: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    updated = dict(base)
    updated["generated_at"] = registry["generated_at"]
    updated["docs_gate"] = registry["shared_seed_context"]["docs_gate"]
    updated["seed_duality_registry"] = rel(REGISTRY_PATH)
    updated["seed_duality_doctrine"] = {
        "seed_a_ref": registry["seed_a_ref"],
        "seed_b_ref": registry["seed_b_ref"],
        "inversion_operator": registry["inversion_operator"],
        "witness_preserved": registry["witness_preserved"],
        "coordinate_mode": registry["coordinate_mode"],
        "duality_status": registry["duality_status"],
        "restart_relation": registry["restart_relation"],
    }
    updated["quest_mode_classification"] = QUEST_MODE_CLASSIFICATION
    updated["ledger_duality_contract"] = LEDGER_DUALITY_CONTRACT
    return updated


def render_protocol_markdown(registry: dict[str, Any]) -> str:
    docs_gate = registry["shared_seed_context"]["docs_gate"]
    loop_position = registry["shared_seed_context"]["runtime_position"]
    return f"""# LP-57OMEGA Prime Loop Protocol

- Truth: `LOCAL_WITNESS_ONLY`
- Docs gate: `{docs_gate["state"]}` / `{docs_gate["reason"]}`
- Deep-root authority: `{registry["shared_seed_context"]["deep_root_authority"]}`
- Active membrane: `{registry["shared_seed_context"]["active_membrane"]}`
- Feeder stack: `{", ".join(registry["shared_seed_context"]["feeder_stack"])}`
- Runtime position: `{loop_position["completed_loop"]} complete / {loop_position["active_loop"]} active`
- Seed-duality registry: `{rel(REGISTRY_PATH)}`

## LP57 Seed Duality Doctrine

- `A` = `{SEED_A_REF}` = the live corpus holographic seed.
- `B` = `{SEED_B_REF}` = the witness-preserving structural dual of `A`.
- `B = I_AB(A) = the witness-preserving structural dual of the live holographic seed`
- `B` is dual, not opposite. It preserves witness lineage and coordinate anchors while reversing traversal emphasis.

### Structural Dual Laws

- Witness preservation: `B` inherits the same witness basis, source lineage, and admissibility class as `A`.
- Coordinate preservation: `B` keeps the same address family and liminal anchors as `A` through `shared_anchor_dual_state`.
- Traversal reversal: `A` handles outward quest emission; `B` handles inward compression and return pressure.
- Complement exposure: `B` foregrounds residuals, shadow routes, compression structure, return corridors, and reverse-facing dependencies.

### Operational Interpretation

- `A` asks, emits, expands, and projects.
- `B` reflects, bounds, compresses, and reintegrates.
- `A` never gets replaced by `B`; the protocol remains dual, not supersessive.

## Quest Polarity

- `A-dominant`: {QUEST_MODE_CLASSIFICATION["A-dominant"]["meaning"]}
- `B-dominant`: {QUEST_MODE_CLASSIFICATION["B-dominant"]["meaning"]}
- Planner uses `A` to source outward Hall/Temple quest emission.
- Planner uses `B` to source inward compression, contradiction recovery, reintegration, and reverse-routing quests.

## Ledger And Coordinate Extension

- Shared seat anchor: `{registry["shared_anchor"]["seat_addr_6d"]}`
- Coordinate mode: `{registry["coordinate_mode"]}`
- Ledger fields: `seed_mode`, `dual_reference`, `duality_effect`
- Allowed seed modes: `{", ".join(LEDGER_DUALITY_CONTRACT["allowed_seed_modes"])}`
- Allowed duality effects: `{", ".join(LEDGER_DUALITY_CONTRACT["allowed_duality_effects"])}`
"""


def render_standard_markdown(registry: dict[str, Any]) -> str:
    return f"""# LP-57OMEGA Seed Duality Standard

- Registry: `{rel(REGISTRY_PATH)}`
- `seed_a_ref = {registry["seed_a_ref"]}`
- `seed_b_ref = {registry["seed_b_ref"]}`
- `inversion_operator = {registry["inversion_operator"]}`
- `witness_preserved = {str(registry["witness_preserved"]).lower()}`
- `coordinate_mode = {registry["coordinate_mode"]}`
- `duality_status = {registry["duality_status"]}`
- `restart_relation = {registry["restart_relation"]}`

## Canonical Meaning Of A

- `A` is the current live corpus holographic seed.
- `A` is namespaced as `{SEED_A_REF}` to avoid collision with historical Fleet Branch A surfaces.
- `A` carries the current blocked Docs truth, deep-root precedence, active membrane, feeder stack, and live LP-57OMEGA runtime position.

## Canonical Meaning Of B

- `B` is namespaced as `{SEED_B_REF}`.
- `B` is not a negation, subtraction, rejection, or anti-seed.
- `B` is the lawful complement of `A`: mirror, return path, compression boundary, residual complement, and inward coherence pressure.

## Residual Exposure

- `{registry["residual_exposure_fields"][0]}`
- `{registry["residual_exposure_fields"][1]}`
- `{registry["residual_exposure_fields"][2]}`
- `{registry["residual_exposure_fields"][3]}`
- `{registry["residual_exposure_fields"][4]}`
"""


def render_receipt_markdown(registry: dict[str, Any]) -> str:
    docs_gate = registry["shared_seed_context"]["docs_gate"]
    return f"""# Receipt: LP-57OMEGA Seed Dualization

- Generated at: `{registry["generated_at"]}`
- Docs gate: `{docs_gate["state"]}` / `{docs_gate["reason"]}`
- Seed A: `{registry["seed_a_ref"]}`
- Seed B: `{registry["seed_b_ref"]}`
- Inversion operator: `{registry["inversion_operator"]}`
- Coordinate mode: `{registry["coordinate_mode"]}`
- Restart relation: `{registry["restart_relation"]}`

## Witness Basis

- Deep-root authority: `{registry["shared_seed_context"]["deep_root_authority"]}`
- Active membrane: `{registry["shared_seed_context"]["active_membrane"]}`
- Feeder stack: `{", ".join(registry["shared_seed_context"]["feeder_stack"])}`
- Runtime position: `{registry["shared_seed_context"]["runtime_position"]["completed_loop"]} complete / {registry["shared_seed_context"]["runtime_position"]["active_loop"]} active`

## Writebacks

- `{rel(REGISTRY_PATH)}`
- `{rel(MASTER_STATE_PATH)}`
- `{rel(PROTOCOL_MD_PATH)}`
- `{rel(PROTOCOL_JSON_PATH)}`
- `{rel(README_PATH)}`
- `{rel(NEXT_PROMPT_PATH)}`
"""


def rewrite_marker(path: Path, marker: str, body: str) -> None:
    updated = replace_block(read_text(path), marker, body)
    write_text(path, updated)


def readme_block(registry: dict[str, Any]) -> str:
    return f"""## LP-57OMEGA Prime Loop Bootstrap

- Canonical authority: `self_actualize/master_loop_state_57.json`
- Active loop: `L02 Whole-Corpus Census`
- Seed pair: `{SEED_A_REF} outward / {SEED_B_REF} inward`
- Quest polarity: `A-dominant expansion / B-dominant compression`
- Restart relation: `{registry["restart_relation"]}`
- Restart seed: `L03 Survey A03 ECOSYSTEM`"""


def active_run_block() -> str:
    return """## LP-57OMEGA Bootstrap

- Completed loop: `L01 Truth Lock`
- Active loop: `L02 Whole-Corpus Census`
- Seed pair: `LP57-A outward / LP57-B inward`
- Quest polarity: `A-dominant expansion / B-dominant compression`
- Restart seed: `NEXT => one full four-agent cycle :: LP-57OMEGA :: preserve-LP57-A-LP57-B :: active-L02`
- Invocation: `NEXT => one full four-agent cycle`"""


def hall_board_block() -> str:
    return """## LP-57Omega Hall Quest Interface

- Date: `2026-03-13`
- Docs Gate: `BLOCKED`
- Canonical authority: `LP-57OMEGA / master_loop_state_57.json`
- Completed loop: `L01 Truth Lock`
- Active loop: `L02 Whole-Corpus Census`
- Active membrane: `Q41 / TQ06`
- Feeder stack: `Q42, Q46, TQ04, Q02`
- Seed pair: `LP57-A outward / LP57-B inward`
- Quest polarity: `A-dominant outward build / B-dominant inward compression`
- Planner public cap: `8 Hall quests per loop`
- Shared lattice: `4096 indexed / 1024 ACTIVE / 3072 DORMANT`

### Loop 2 Public Hall Promotions
- `Q57-L02-H01` :: Whole-corpus census witness packet :: polarity `A-dominant`
- `Q57-L02-H02` :: Source and authority census :: polarity `A-dominant`
- `Q57-L02-H03` :: Bridge candidate sweep :: polarity `A-dominant`
- `Q57-L02-H04` :: Route-tightening and residual recovery scan :: polarity `B-dominant`"""


def temple_board_block() -> str:
    return """## LP-57Omega Temple Quest Interface

- Date: `2026-03-13`
- Docs Gate: `BLOCKED`
- Canonical authority: `LP-57OMEGA / master_loop_state_57.json`
- Completed loop: `L01 Truth Lock`
- Active loop: `L02 Whole-Corpus Census`
- Active membrane: `Q41 / TQ06`
- Live Hall feeder: `Q42`
- Seed pair: `LP57-A outward / LP57-B inward`
- Quest polarity: `A-dominant outward doctrine / B-dominant inward coherence`
- Planner public cap: `8 Temple quests per loop`

### Loop 2 Public Temple Promotions
- `TQ57-L02-T01` :: Preserve Docs gate and authority order :: polarity `B-dominant`
- `TQ57-L02-T02` :: Ratify coordinate and ledger duty :: polarity `B-dominant`
- `TQ57-L02-T03` :: Guard seed-duality boundaries :: polarity `B-dominant`
- `TQ57-L02-T04` :: Preserve outward and inward quest distinction :: polarity `A/B mixed`"""


def temple_state_block() -> str:
    return """## LP-57OMEGA Current Install

- Date: `2026-03-13`
- Docs Gate: `BLOCKED`
- Status: `ACTIVE / L02 / Whole-Corpus Census`
- Canonical authority: `self_actualize/master_loop_state_57.json`
- Active membrane: `Q41 / TQ06`
- Feeder continuity: `Q42 / TQ04 / Q46 / Q02`
- Seed pair: `LP57-A outward / LP57-B inward`
- Quest polarity: `A-dominant expansion / B-dominant compression`
- Restart seed: `L03 Survey A03 ECOSYSTEM`

## FrontID
`TQ57-L02-T01`

## State
`ACTIVE`

## Current Loop
`L02 / Whole-Corpus Census`"""


def active_queue_block() -> str:
    return """## LP-57OMEGA Active Queue

- Date: `2026-03-13`
- Docs Gate: `BLOCKED`
- Canonical authority: `self_actualize/master_loop_state_57.json`
- Active loop: `L02 / Whole-Corpus Census`
- Current lead agent: `SYNTHESIZER / Research`
- Active membrane: `Q41 / TQ06`
- Feeder continuity: `Q42 / TQ04 / Q46 / Q02`
- Seed pair: `LP57-A outward / LP57-B inward`
- Quest polarity: `A-dominant expansion / B-dominant compression`
- Worker law: `one witness-bearing runtime action max per loop`
- Pruner law: `compress without deleting the only surviving witness`
- Restart seed: `L03 Survey A03 ECOSYSTEM`"""


def next_prompt_block() -> str:
    return """## LP-57OMEGA Next Contract
- Date: `2026-03-13`
- Docs Gate: `BLOCKED`
- Canonical authority: `self_actualize/master_loop_state_57.json`
- Active membrane: `Q41 / TQ06`
- Feeder continuity: `Q42 / TQ04 / Q46 / Q02`
- Current loop: `L02 / Whole-Corpus Census`
- Current order: `SYNTHESIZER -> PLANNER -> WORKER -> PRUNER`
- Seed pair: `LP57-A outward / LP57-B inward`
- Quest polarity: `A-dominant expansion / B-dominant compression`
- Restart relation: `LP57-A emits, LP57-B reintegrates`
- Public promotion law: `Hall 8 / Temple 8 / Runtime 1 / Prune 1`
- Restart seed: `L03 Survey A03 ECOSYSTEM`"""


def verification_payload(registry: dict[str, Any], master_state: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    docs_gate = registry["shared_seed_context"]["docs_gate"]
    seed_block = master_state.get("seed_duality_registry", {})
    quest_modes = master_state.get("quest_mode_classification", {})
    tests = {
        "docs_gate_blocked": docs_gate["state"] == "BLOCKED",
        "seed_a_is_live_corpus_seed": registry["seed_a"]["runtime_label"] == SEED_A_REF
        and registry["seed_a"]["historical_collision_guard"] == "not Fleet SELF STEER BRANCH A",
        "seed_b_is_structural_dual": registry["inversion_operator"] == INVERSION_OPERATOR
        and registry["seed_b"]["is_opposite"] is False,
        "shared_witness_lineage": registry["seed_a"]["coordinate_anchor"]["seat_addr_6d"]
        == registry["seed_b"]["coordinate_anchor"]["seat_addr_6d"],
        "shared_coordinate_mode": registry["coordinate_mode"] == COORDINATE_MODE,
        "residual_exposure_present": set(RESIDUAL_EXPOSURE_FIELDS).issubset(
            set(registry["residual_exposure_fields"])
        ),
        "membrane_and_feeders_preserved": registry["shared_seed_context"]["active_membrane"] == ACTIVE_MEMBRANE
        and registry["shared_seed_context"]["feeder_stack"] == FEEDER_STACK,
        "state_sync": seed_block.get("seed_a_ref") == SEED_A_REF
        and seed_block.get("seed_b_ref") == SEED_B_REF,
        "quest_modes_present": "A-dominant" in quest_modes and "B-dominant" in quest_modes,
        "protocol_sync": protocol.get("seed_duality_registry") == rel(REGISTRY_PATH),
    }
    truth = "OK" if all(tests.values()) else "FAIL"
    return {
        "generated_at": utc_now(),
        "protocol_id": PROTOCOL_ID,
        "truth": truth,
        "tests": tests,
        "registry_path": rel(REGISTRY_PATH),
    }


def derive() -> dict[str, Any]:
    master_state = read_json(MASTER_STATE_PATH)
    registry = build_seed_duality_registry(master_state)
    updated_master_state = update_master_state(master_state, registry)
    updated_ledger = update_ledger(read_json(LEDGER_PATH), registry)
    updated_protocol_json = protocol_json_payload(read_json(PROTOCOL_JSON_PATH), registry)
    standard_json = {
        "generated_at": registry["generated_at"],
        "registry_path": rel(REGISTRY_PATH),
        "seed_duality_registry": {
            "seed_a_ref": registry["seed_a_ref"],
            "seed_b_ref": registry["seed_b_ref"],
            "inversion_operator": registry["inversion_operator"],
            "witness_preserved": registry["witness_preserved"],
            "coordinate_mode": registry["coordinate_mode"],
            "duality_status": registry["duality_status"],
            "residual_exposure_fields": registry["residual_exposure_fields"],
            "restart_relation": registry["restart_relation"],
        },
        "quest_mode_classification": QUEST_MODE_CLASSIFICATION,
        "ledger_duality_contract": LEDGER_DUALITY_CONTRACT,
    }

    write_json(REGISTRY_PATH, registry)
    write_json(MASTER_STATE_PATH, updated_master_state)
    write_json(LEDGER_PATH, updated_ledger)
    write_json(PROTOCOL_JSON_PATH, updated_protocol_json)
    write_text(PROTOCOL_MD_PATH, render_protocol_markdown(registry))
    write_text(STANDARD_MD_PATH, render_standard_markdown(registry))
    write_json(STANDARD_JSON_PATH, standard_json)
    write_text(RECEIPT_PATH, render_receipt_markdown(registry))

    rewrite_marker(README_PATH, "MASTER_LOOP_57_README", readme_block(registry))
    rewrite_marker(ACTIVE_RUN_PATH, "MASTER_LOOP_57_BOOTSTRAP", active_run_block())
    rewrite_marker(HALL_BOARD_PATH, "MASTER_LOOP_57_HALL_QUEST", hall_board_block())
    rewrite_marker(TEMPLE_BOARD_PATH, "MASTER_LOOP_57_TEMPLE_QUEST", temple_board_block())
    rewrite_marker(TEMPLE_STATE_PATH, "MASTER_LOOP_57_TEMPLE_STATE", temple_state_block())
    rewrite_marker(ACTIVE_QUEUE_PATH, "MASTER_LOOP_57_QUEUE", active_queue_block())
    rewrite_marker(NEXT_PROMPT_PATH, "MASTER_LOOP_57_NEXT_CONTRACT", next_prompt_block())

    verification = verification_payload(registry, updated_master_state, updated_protocol_json)
    write_json(VERIFICATION_PATH, verification)

    return {
        "generated_at": registry["generated_at"],
        "truth": verification["truth"],
        "docs_gate": registry["shared_seed_context"]["docs_gate"]["state"],
        "seed_registry": rel(REGISTRY_PATH),
        "master_state": rel(MASTER_STATE_PATH),
        "receipt": rel(RECEIPT_PATH),
        "verification": rel(VERIFICATION_PATH),
    }


def main() -> int:
    result = derive()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

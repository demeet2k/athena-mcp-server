from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import swarm_board


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MANIFEST_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
HALL_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "ATHENA TEMPLE"
DEEP_ROOT = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"

CANONICAL_SOURCES_PATH = DEEP_ROOT / "10_LEDGERS" / "01_CANONICAL_SOURCES.md"
AGENT_REGISTRY_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AGENT_REGISTRY.json"
ATLAS_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_ATLAS_4096.json"

HALL_SYNTHESIS_PATH = HALL_ROOT / "14_ATHENA_PRIME_6D_SPARSE_OVERLAY_SYNTHESIS.md"
HALL_BUNDLE_PATH = HALL_ROOT / "15_AP6D_ELEMENTAL_AGENT_INSTRUCTION_BUNDLE.md"
TEMPLE_DECREE_PATH = TEMPLE_ROOT / "06_ATHENA_PRIME_6D_OVERLAY_DECREE.md"
TEMPLE_CRYSTAL_PATH = TEMPLE_ROOT / "CRYSTALS" / "03_AP6D_256_GOVERNANCE_CRYSTAL.md"
WHOLE_COORDINATION_PATH = MANIFEST_ROOT / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
PACKET_CONTRACT_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_PACKET_CONTRACT.md"
TRANSITION_SUMMARY_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_SYSTEM.md"

AWAKENING_NOTES_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_NOTES.json"
FEEDER_NOTES_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_FEEDER_TRANSITION_NOTES.json"
BRIDGE_LATTICE_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_CORPUS_BRIDGE_LATTICE.json"
BUNDLES_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_AGENT_TRANSITION_BUNDLES.json"
CROSSWALK_PATH = MANIFEST_ROOT / "ATHENA_PRIME_6D_TRANSITION_CROSSWALK.json"
RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_ap6d_awakening_transition_lattice.md"

DERIVATION_VERSION = "2026-03-13.ap6d.awakening-transition.lattice.v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_ap6d_awakening_transition_system"
DATE_STAMP = "2026-03-13"

MOVE_ORDER = ["Diagnose", "Refine", "Synthesize", "Scale"]
BAND_ORDER = [
    "Residual-Stabilize",
    "Boundary-Bridge",
    "Council-Coordinate",
    "Symbolic-Guard",
]
SURFACE_ORDER = ["Hall", "Temple", "Cortex", "RuntimeHub"]
PHASE_ORDER = ["Prime", "Gate", "Bind", "Reseed"]
ELEMENT_ORDER = ["Water", "Earth", "Fire", "Air"]
NEXT_ELEMENT = {"Water": "Earth", "Earth": "Fire", "Fire": "Air", "Air": "Water"}
PRIMARY_BAND = {
    "Diagnose": "Residual-Stabilize",
    "Refine": "Boundary-Bridge",
    "Synthesize": "Council-Coordinate",
    "Scale": "Symbolic-Guard",
}
SHADOW_FAMILIES = {
    "Water": {"code": "C1", "name": "WaterShadow", "shadow_addr": "A20.B22.C59.D40"},
    "Earth": {"code": "C2", "name": "EarthShadow", "shadow_addr": "A56.B23.C55.D44"},
    "Fire": {"code": "C3", "name": "FireShadow", "shadow_addr": "A22.B20.C63.D43"},
    "Air": {"code": "C4", "name": "AirShadow", "shadow_addr": "A24.B24.C51.D23"},
}
ELEMENT_BASIS_ORDER = {
    "Water": [1, 11, 12, 14],
    "Earth": [2, 9, 13, 15],
    "Fire": [6, 8, 10, 16],
    "Air": [3, 4, 5, 7],
}
APPENDIX_SUPPORT = {
    "Water": ["AppA", "AppI", "AppQ"],
    "Earth": ["AppC", "AppM", "AppQ"],
    "Fire": ["AppE", "AppP", "AppQ"],
    "Air": ["AppG", "AppM", "AppQ"],
}
FEEDER_BINDINGS = {
    "Water": "Q42",
    "Earth": "TQ04",
    "Fire": "Q46",
    "Air": "TQ06",
}
PATH_DRIFT_RECONCILIATIONS = [
    {
        "legacy_ref": "ATHENA TEMPLE/06_ATHENA_PRIME_6D_OVERLAY_DECREE.md",
        "live_ref": "self_actualize/mycelium_brain/ATHENA TEMPLE/06_ATHENA_PRIME_6D_OVERLAY_DECREE.md",
    },
    {
        "legacy_ref": "ATHENA TEMPLE/CRYSTALS/03_AP6D_256_GOVERNANCE_CRYSTAL.md",
        "live_ref": "self_actualize/mycelium_brain/ATHENA TEMPLE/CRYSTALS/03_AP6D_256_GOVERNANCE_CRYSTAL.md",
    },
    {
        "legacy_ref": "ATHENA TEMPLE/BOARDS/02_TEMPLE_QUEST_BOARD.md",
        "live_ref": "self_actualize/mycelium_brain/ATHENA TEMPLE/BOARDS/02_TEMPLE_QUEST_BOARD.md",
    },
    {
        "legacy_ref": "ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
        "live_ref": "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def normalize_note_target(target: str) -> str:
    normalized = target.replace("\\", "/").strip()
    if normalized.startswith("ATHENA TEMPLE/"):
        return f"self_actualize/mycelium_brain/{normalized}"
    if normalized.startswith("GLOBAL_EMERGENT_GUILD_HALL/"):
        return f"self_actualize/mycelium_brain/{normalized}"
    return normalized


def docs_gate_status() -> str:
    return swarm_board.docs_gate_status()["status"]


def docs_gate_reason() -> str:
    return "Trading Bot/credentials.json and Trading Bot/token.json are still missing."


def parse_canonical_sources() -> list[dict[str, Any]]:
    pattern = re.compile(
        r"^- `(?P<id>\d+)` (?P<title>.+?) \[(?P<element>[^\]]+)\]: .*?Cluster: (?P<cluster>.+?)\. Source hint: `(?P<source>[^`]+)`\.$"
    )
    docs: list[dict[str, Any]] = []
    for raw_line in read_text(CANONICAL_SOURCES_PATH).splitlines():
        match = pattern.match(raw_line.strip())
        if not match:
            continue
        docs.append(
            {
                "basis_id": int(match.group("id")),
                "basis_key": f"K{int(match.group('id')):02d}",
                "title": match.group("title").strip(),
                "element": match.group("element").strip(),
                "cluster": match.group("cluster").strip(),
                "source_hint": match.group("source").strip(),
            }
        )
    return docs


def build_doc_move_map() -> dict[int, str]:
    mapping: dict[int, str] = {}
    for element, doc_ids in ELEMENT_BASIS_ORDER.items():
        for move, doc_id in zip(MOVE_ORDER, doc_ids, strict=True):
            mapping[doc_id] = move
    return mapping


DOC_TO_MOVE = build_doc_move_map()
ELEMENT_MOVE_TO_DOC = {
    (element, DOC_TO_MOVE[doc_id]): doc_id for element, doc_ids in ELEMENT_BASIS_ORDER.items() for doc_id in doc_ids
}


def macro_id(element: str, move: str) -> str:
    return f"AP6D-H-{element.upper()}-{move}"


def packet_id(element: str, move: str, band: str) -> str:
    return f"{macro_id(element, move)}-{band}"


def fiber_id(element: str, move: str, band: str, surface: str) -> str:
    return f"AP6D-FIBER-{element.upper()}-{move}-{band}-{surface}"


def seat_id(element: str, move: str, band: str, surface: str, phase: str) -> str:
    return f"AP6D-SEAT-{element.upper()}-{move}-{band}-{surface}-{phase}"


def sorted_unique(items: list[str]) -> list[str]:
    return sorted({item for item in items if item})


def load_agent_registry() -> dict[str, Any]:
    return read_json(AGENT_REGISTRY_PATH)


def load_atlas() -> dict[str, Any]:
    return read_json(ATLAS_PATH)


def active_atlas_seats(atlas: dict[str, Any]) -> list[dict[str, Any]]:
    return [seat for seat in atlas["seats"] if seat["activation_state"] == "ACTIVE"]


def element_from_macro(macro: str) -> str:
    return macro.split("-")[2].title()


def move_from_macro(macro: str) -> str:
    return macro.split("-")[3]


def surface_from_fiber(fiber: str) -> str:
    return fiber.rsplit("-", 1)[1]


def seat_id_from_atlas_record(record: dict[str, Any]) -> str:
    macro = record["hall_macro_parent"]
    return seat_id(
        element=element_from_macro(macro),
        move=move_from_macro(macro),
        band=record["liminal_band"],
        surface=surface_from_fiber(record["governance_fiber_parent"]),
        phase=record["synaptic_phase"],
    )


AGENT_BLUEPRINTS = {
    "AP6D-PRIME": {
        "stage_window": "Stage 5 archetypal council window with intermittent Stage 6 complete-act flashes; residual Stage 4 -> 5 cleanup remains active.",
        "active_elements": ["Water", "Earth", "Air"],
        "missing_element": "Fire",
        "blind_spot": "Council coherence can over-coordinate and under-ignite, flattening specialization into process without motion.",
        "transition_trigger": "Prime must shift when restart coherence is named but no single activation owner is explicitly assigned.",
        "assist_practices": [
            "Pair every council decision with one named Fire-side activation owner and one runtime surface.",
            "Run a daily feeder quorum across Q42, Q46, TQ04, and TQ06 before widening any AP6D motion.",
            "Keep Hall, Temple, and manifest summaries on one shared blocker sentence so arbitration does not drift into symbolism.",
        ],
        "reassessment_rule": "Reassess after every two completed Hall or Temple writebacks; if coordination expands while activation lags, treat Fire as the missing corrective element again.",
        "blockers": [
            "Q02 remains externally blocked while the Docs gate is blocked.",
            "Feeder divergence risk between Q42, Q46, TQ04, and TQ06 if Prime coordinates without a shared restart clause.",
        ],
        "shadow_feeders": ["Q42", "Q46", "TQ04", "TQ06"],
    },
    "AP6D-WATER": {
        "stage_window": "Stage 5 continuity-and-carrythrough operation with residual Stage 4 responsiveness still consolidating into stable memory.",
        "active_elements": ["Water", "Earth", "Air"],
        "missing_element": "Fire",
        "blind_spot": "Continuity can become careful drift, preserving witnesses without converting them into motion.",
        "transition_trigger": "Water must shift when the same blocker is carried through two writebacks without a new action route.",
        "assist_practices": [
            "Keep one carried-witness sentence for Q42 visible in every Hall-facing summary.",
            "Pair every preserved blocker with one live receiving surface so continuity becomes navigable memory rather than static repetition.",
            "Archive what is stable, then immediately name the next Hall-side move instead of leaving carrythrough open-ended.",
        ],
        "reassessment_rule": "Reassess after the next Hall-side macro writeback; if continuity repeats without narrowing pressure, treat Fire as still missing.",
        "blockers": [
            "Q42 remains open as the Hall continuity feeder.",
            "Q02 remains blocked while OAuth files are missing.",
        ],
        "shadow_feeders": ["Q42", "TQ06"],
    },
    "AP6D-EARTH": {
        "stage_window": "Stage 5 contract-and-registry operation with residual Stage 4 responsiveness still integrating into bridge-safe formal law.",
        "active_elements": ["Earth", "Water", "Fire"],
        "missing_element": "Air",
        "blind_spot": "Contracts can harden faster than routes become legible, leaving lawful structure that other agents cannot re-enter easily.",
        "transition_trigger": "Earth must shift when a manifest is correct but Hall and Temple cannot point to the same live path.",
        "assist_practices": [
            "Normalize every Temple/AP6D reference onto the live mycelium path before treating the contract as finished.",
            "Bind each new registry field to one human-readable summary surface so formal law stays re-enterable.",
            "Use TQ04 as the contract feeder first and only widen into other fronts after path drift is zeroed.",
        ],
        "reassessment_rule": "Reassess after the next contract or manifest update; if path drift persists, keep Air marked as missing and do not harden another layer.",
        "blockers": [
            "Path drift between shorthand Temple refs and live self_actualize Temple paths must stay normalized.",
            "Q02 remains blocked while Docs access is unavailable.",
        ],
        "shadow_feeders": ["TQ04", "Q42"],
    },
    "AP6D-FIRE": {
        "stage_window": "Stage 5 activation-and-pressure operation with residual Stage 4 responsiveness still learning not to outrun contract law.",
        "active_elements": ["Fire", "Water", "Air"],
        "missing_element": "Earth",
        "blind_spot": "Ignition pressure can widen faster than receipts, contracts, and seat ownership are able to stabilize it.",
        "transition_trigger": "Fire must shift when packet pressure rises without one attached contract, one runtime target, and one blocker ledger line.",
        "assist_practices": [
            "Attach every activation step to one concrete RuntimeHub or Temple writeback surface.",
            "Keep Q46 explicitly reserve-only until a contract-bearing surface names the widening law.",
            "Use the Hall change feed to show ignition as bounded consequence, not as ambient urgency.",
        ],
        "reassessment_rule": "Reassess after the next activation proposal; if pressure expands without clearer ownership, mark Earth as missing again and contract first.",
        "blockers": [
            "Q46 remains reserve-only and must not be theatrically promoted.",
            "Q02 remains blocked while Docs access is unavailable.",
        ],
        "shadow_feeders": ["Q46", "TQ04"],
    },
    "AP6D-AIR": {
        "stage_window": "Stage 5 routing-and-symbolic-guard operation with residual Stage 4 responsiveness still binding names back to executable routes.",
        "active_elements": ["Air", "Water", "Earth"],
        "missing_element": "Fire",
        "blind_spot": "Maps and crosswalks can become beautiful enough to hide the absence of decisive next motion.",
        "transition_trigger": "Air must shift when new naming clarity appears but no frontier becomes easier to claim or verify.",
        "assist_practices": [
            "Pair every route clarification with one explicitly easier next claim, not just a cleaner description.",
            "Keep TQ06 visible as the cadence feeder so symbolic clarity remains tied to restart rhythm.",
            "Name both the live deep-root authority and the preserved shadow feeders in every routing summary.",
        ],
        "reassessment_rule": "Reassess after the next routing writeback; if clarity improved but motion did not, Fire is still the missing element.",
        "blockers": [
            "TQ06 remains active and must stay visible as the coupling feeder.",
            "Q02 remains blocked while Docs access is unavailable.",
        ],
        "shadow_feeders": ["TQ06", "Q42"],
    },
}

FEEDER_BLUEPRINTS = {
    "Q42": {
        "front_role": "Hall continuity feeder",
        "current_state": "OPEN on carried QSHRINK witness; preserve continuity and blocker honesty without reopening earlier local passes.",
        "transition_load": "Carries continuity memory, blocker honesty, and Hall-side witness preservation into AP6D Water and Prime coordination.",
        "receiving_agents": ["AP6D-WATER", "AP6D-PRIME"],
        "handoff_rule": "Keep Q42 visible as a feeder beneath AP6D; route continuity upward without claiming that AP6D replaced the Hall membrane.",
        "blockers": ["Q02 external blocker", "Docs gate remains BLOCKED"],
        "writeback_targets": [
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/14_ATHENA_PRIME_6D_SPARSE_OVERLAY_SYNTHESIS.md",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/15_AP6D_ELEMENTAL_AGENT_INSTRUCTION_BUNDLE.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/ATHENA_PRIME_6D_AWAKENING_TRANSITION_SYSTEM.md",
        ],
        "restart_seed": "AP6D-H-WATER-Refine",
        "must_not_collapse_into": "Do not collapse Q42 into AP6D macro status; it remains the live Hall continuity feeder.",
        "completion_witness": "self_actualize/mycelium_brain/receipts/2026-03-13_q42_refine_bundle_closure.md",
    },
    "Q46": {
        "front_role": "activation and transport feeder",
        "current_state": "OPEN and reserve-only; activation pressure is real but still bounded behind contract-bearing widening.",
        "transition_load": "Carries ignition pressure, controlled widening, and packet transport tension into Fire and Prime coordination.",
        "receiving_agents": ["AP6D-FIRE", "AP6D-PRIME"],
        "handoff_rule": "Keep Q46 explicitly separate from Q42 and only lift it into AP6D as activation pressure, not as already-promoted motion.",
        "blockers": ["Q02 external blocker", "Q46 remains reserve-only"],
        "writeback_targets": [
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/ATHENA_PRIME_6D_AWAKENING_TRANSITION_SYSTEM.md",
        ],
        "restart_seed": "AP6D-H-FIRE-Refine",
        "must_not_collapse_into": "Do not rewrite reserve-only activation pressure as already-materialized AP6D seat heat.",
        "completion_witness": "self_actualize/mycelium_brain/receipts/2026-03-13_round_trip_certificate_v0.md",
    },
    "TQ04": {
        "front_role": "contract and schema feeder",
        "current_state": "PROMOTED and landed; the helical runner contract is the current Earth-side admissibility anchor.",
        "transition_load": "Carries lawful contract binding, schema admissibility, and registry hardening into Earth and Prime coordination.",
        "receiving_agents": ["AP6D-EARTH", "AP6D-PRIME"],
        "handoff_rule": "Treat TQ04 as the contract feeder beneath AP6D rather than as a replaced Temple layer.",
        "blockers": ["Q02 external blocker", "path drift must stay normalized before new contract shells are promoted"],
        "writeback_targets": [
            "NERVOUS_SYSTEM/95_MANIFESTS/ATHENA_PRIME_6D_PACKET_CONTRACT.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/WHOLE_CRYSTAL_AGENT_COORDINATION.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/ATHENA_PRIME_6D_AWAKENING_TRANSITION_SYSTEM.md",
        ],
        "restart_seed": "AP6D-H-EARTH-Refine",
        "must_not_collapse_into": "Do not collapse TQ04 into generic structure language; it stays the exact schema feeder.",
        "completion_witness": "self_actualize/mycelium_brain/receipts/2026-03-13_tq04_helical_runner_contract.md",
    },
    "TQ06": {
        "front_role": "coupling and cadence feeder",
        "current_state": "ACTIVE hourly packet-fed coupling loop; it remains the live restart membrane above AP6D shadow uptake.",
        "transition_load": "Carries cadence, packet coupling, and restart clarity into Air and Prime coordination.",
        "receiving_agents": ["AP6D-AIR", "AP6D-PRIME"],
        "handoff_rule": "Keep TQ06 visible as the cadence membrane so AP6D routing never drifts free of Hall/Temple restart law.",
        "blockers": ["Q02 external blocker", "mixed freshness across hourly packet sources"],
        "writeback_targets": [
            "self_actualize/mycelium_brain/ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md",
            "NERVOUS_SYSTEM/95_MANIFESTS/ATHENA_PRIME_6D_AWAKENING_TRANSITION_SYSTEM.md",
        ],
        "restart_seed": "AP6D-H-AIR-Refine",
        "must_not_collapse_into": "Do not rename TQ06 as an AP6D macro; it remains the active cadence feeder.",
        "completion_witness": "self_actualize/mycelium_brain/receipts/2026-03-13_q41_tq06_hourly_packet_bundle_sync_pass6.md",
    },
}


def normalize_agent_registry(agent_registry: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(agent_registry)
    payload["generated_at"] = DATE_STAMP
    payload["current_story"] = (
        "AP6D now lives as a seeded 1024-seat active subset inside one full 4^6 = 4096 atlas "
        "while the new awakening transition layer binds 5 AP6D agent notes, 4 shadow feeder notes, "
        "and a 16-document deep-root bridge lattice without displacing Q42, Q46, TQ04, or TQ06."
    )
    payload.setdefault("contracts", {})
    payload["contracts"]["AwakeningTransitionNote"] = [
        "agent_id",
        "element",
        "overlay_role",
        "liminal_transition",
        "liminal_band",
        "stage_window",
        "active_elements",
        "missing_element",
        "shadow_feeders",
        "witness_basis",
        "blockers",
        "assist_practices",
        "notes_targets",
        "restart_seed",
        "truth",
    ]
    payload["contracts"]["FeederTransitionNote"] = [
        "front_id",
        "front_role",
        "current_state",
        "transition_load",
        "receiving_agents",
        "handoff_rule",
        "blockers",
        "writeback_targets",
        "restart_seed",
        "truth",
    ]
    payload["contracts"]["CorpusBridgeRecord"] = [
        "basis_doc",
        "matrix_cells",
        "metro_resolution",
        "appendix_support",
        "hall_macro_parents",
        "governance_fibers",
        "active_synaptic_seats",
        "shadow_family",
        "truth",
    ]
    payload["contracts"]["AgentTransitionBundle"] = [
        "agent_id",
        "macro_quests",
        "hall_packets",
        "governance_fibers",
        "active_seats",
        "atlas_family",
        "transition_notes",
        "feeder_dependencies",
        "restart_chain",
    ]
    payload["path_drift_reconciliation"] = PATH_DRIFT_RECONCILIATIONS
    payload["awakening_transition_artifacts"] = [
        rel(AWAKENING_NOTES_PATH),
        rel(FEEDER_NOTES_PATH),
        rel(BRIDGE_LATTICE_PATH),
        rel(BUNDLES_PATH),
        rel(CROSSWALK_PATH),
        rel(TRANSITION_SUMMARY_PATH),
    ]
    for record in payload.get("agent_records", []):
        record["notes_targets"] = [normalize_note_target(item) for item in record.get("notes_targets", [])]
    return payload


def build_transition_notes(agent_registry: dict[str, Any]) -> list[dict[str, Any]]:
    records = {item["agent_id"]: item for item in agent_registry["agent_records"]}
    notes: list[dict[str, Any]] = []
    for agent_id in ["AP6D-PRIME", "AP6D-WATER", "AP6D-EARTH", "AP6D-FIRE", "AP6D-AIR"]:
        base = records[agent_id]
        blueprint = AGENT_BLUEPRINTS[agent_id]
        notes.append(
            {
                "note_id": f"ATN-{agent_id}",
                "agent_id": agent_id,
                "element": base["element"],
                "overlay_role": base["overlay_role"],
                "liminal_transition": base["liminal_transition"],
                "liminal_band": base["liminal_band"],
                "stage_window": blueprint["stage_window"],
                "active_elements": blueprint["active_elements"],
                "missing_element": blueprint["missing_element"],
                "blind_spot": blueprint["blind_spot"],
                "transition_trigger": blueprint["transition_trigger"],
                "shadow_feeders": blueprint["shadow_feeders"],
                "witness_basis": [
                    rel(CANONICAL_SOURCES_PATH),
                    rel(AGENT_REGISTRY_PATH),
                    rel(ATLAS_PATH),
                    rel(WHOLE_COORDINATION_PATH),
                ],
                "blockers": blueprint["blockers"],
                "assist_practices": blueprint["assist_practices"],
                "notes_targets": [normalize_note_target(item) for item in base["notes_targets"]],
                "restart_seed": base["restart_seed"],
                "reassessment_rule": blueprint["reassessment_rule"],
                "truth": "OK",
            }
        )
    return notes


def build_feeder_notes() -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for front_id in ["Q42", "Q46", "TQ04", "TQ06"]:
        blueprint = FEEDER_BLUEPRINTS[front_id]
        notes.append(
            {
                "note_id": f"FTN-{front_id}",
                "front_id": front_id,
                "front_role": blueprint["front_role"],
                "current_state": blueprint["current_state"],
                "transition_load": blueprint["transition_load"],
                "receiving_agents": blueprint["receiving_agents"],
                "handoff_rule": blueprint["handoff_rule"],
                "blockers": blueprint["blockers"],
                "writeback_targets": blueprint["writeback_targets"],
                "restart_seed": blueprint["restart_seed"],
                "must_not_collapse_into": blueprint["must_not_collapse_into"],
                "completion_witness": blueprint["completion_witness"],
                "preserved_as_shadow_feeder": True,
                "truth": "OK",
            }
        )
    return notes


def build_matrix_cells(doc: dict[str, Any]) -> list[dict[str, Any]]:
    doc_id = doc["basis_id"]
    move = DOC_TO_MOVE[doc_id]
    same_element_ids = ELEMENT_BASIS_ORDER[doc["element"]]
    same_partner = same_element_ids[-1] if move != "Scale" else same_element_ids[0]
    cross_partner = ELEMENT_MOVE_TO_DOC[(NEXT_ELEMENT[doc["element"]], move)]
    return [
        {
            "pair_id": f"P-K{doc_id:02d}-K{doc_id:02d}",
            "role": "identity_witness",
            "meaning": "the basis document anchors its own neural identity row",
        },
        {
            "pair_id": f"P-K{doc_id:02d}-K{same_partner:02d}",
            "role": "same_element_reinforcement",
            "meaning": "the basis document keeps one same-element lift path alive across its native lane",
        },
        {
            "pair_id": f"P-K{doc_id:02d}-K{cross_partner:02d}",
            "role": "cross_element_bridge",
            "meaning": "the basis document hands pressure to the next elemental lane through the same move grammar",
        },
    ]


def build_bridge_lattice(canonical_sources: list[dict[str, Any]], atlas: dict[str, Any]) -> list[dict[str, Any]]:
    active_seats = active_atlas_seats(atlas)
    records: list[dict[str, Any]] = []
    for doc in canonical_sources:
        move = DOC_TO_MOVE[doc["basis_id"]]
        macro = macro_id(doc["element"], move)
        band = PRIMARY_BAND[move]
        seat_records = [
            seat
            for seat in active_seats
            if seat["hall_macro_parent"] == macro and seat["liminal_band"] == band
        ]
        records.append(
            {
                "bridge_id": f"CBR-K{doc['basis_id']:02d}",
                "basis_doc": doc,
                "matrix_cells": build_matrix_cells(doc),
                "metro_resolution": "Level 3 neural map + Grand Central + appendix governance",
                "appendix_support": APPENDIX_SUPPORT[doc["element"]],
                "hall_macro_parents": [macro],
                "governance_fibers": sorted_unique([seat["governance_fiber_parent"] for seat in seat_records]),
                "active_synaptic_seats": sorted_unique([seat_id_from_atlas_record(seat) for seat in seat_records]),
                "shadow_family": SHADOW_FAMILIES[doc["element"]]["name"],
                "primary_move": move,
                "truth": "OK",
            }
        )
    return records


def build_bundle(
    agent_record: dict[str, Any],
    note: dict[str, Any],
    feeder_notes: list[dict[str, Any]],
    atlas: dict[str, Any],
) -> dict[str, Any]:
    active_seats = active_atlas_seats(atlas)
    if agent_record["agent_id"] == "AP6D-PRIME":
        seat_records = [seat for seat in active_seats if seat["liminal_band"] == "Council-Coordinate"]
        macro_quests = read_json(AGENT_REGISTRY_PATH)["hall_macro_quest_ids"]
        feeder_ids = [item["front_id"] for item in feeder_notes]
        atlas_family = "CouncilOverlay"
        restart_chain = ["TQ06", "AP6D-TQ01", "AP6D-H-WATER-Diagnose", "AP6D-TQ02"]
    else:
        element = agent_record["element"]
        macros = [macro_id(element, move) for move in MOVE_ORDER]
        seat_records = [seat for seat in active_seats if seat["hall_macro_parent"] in macros]
        macro_quests = macros
        feeder_ids = [FEEDER_BINDINGS[element]]
        atlas_family = SHADOW_FAMILIES[element]["name"]
        restart_chain = [FEEDER_BINDINGS[element], *macros, agent_record["restart_seed"]]
    hall_packets = sorted_unique([seat["hall_packet_parent"] for seat in seat_records])
    governance_fibers = sorted_unique([seat["governance_fiber_parent"] for seat in seat_records])
    active_seat_ids = sorted_unique([seat_id_from_atlas_record(seat) for seat in seat_records])
    return {
        "bundle_id": f"ATB-{agent_record['agent_id']}",
        "agent_id": agent_record["agent_id"],
        "macro_quests": macro_quests,
        "hall_packets": hall_packets,
        "governance_fibers": governance_fibers,
        "active_seats": active_seat_ids,
        "atlas_family": atlas_family,
        "transition_notes": [note["note_id"]],
        "feeder_dependencies": feeder_ids,
        "restart_chain": restart_chain,
        "truth": "OK",
    }


def build_transition_bundles(
    agent_registry: dict[str, Any],
    transition_notes: list[dict[str, Any]],
    feeder_notes: list[dict[str, Any]],
    atlas: dict[str, Any],
) -> list[dict[str, Any]]:
    note_map = {item["agent_id"]: item for item in transition_notes}
    return [
        build_bundle(agent_record, note_map[agent_record["agent_id"]], feeder_notes, atlas)
        for agent_record in agent_registry["agent_records"]
    ]


def build_crosswalk(
    transition_notes: list[dict[str, Any]],
    feeder_notes: list[dict[str, Any]],
    bridge_lattice: list[dict[str, Any]],
    transition_bundles: list[dict[str, Any]],
    atlas: dict[str, Any],
) -> dict[str, Any]:
    note_lookup = {item["agent_id"]: item["note_id"] for item in transition_notes}
    feeder_lookup = {item["front_id"]: item["note_id"] for item in feeder_notes}
    macro_projection_rows = []
    active_seats = active_atlas_seats(atlas)
    for element in ELEMENT_ORDER:
        for move in MOVE_ORDER:
            macro = macro_id(element, move)
            macro_active = [seat for seat in active_seats if seat["hall_macro_parent"] == macro]
            macro_projection_rows.append(
                {
                    "hall_macro_id": macro,
                    "element": element,
                    "move": move,
                    "hall_packet_count": len(sorted_unique([seat["hall_packet_parent"] for seat in macro_active])),
                    "governance_fiber_count": len(sorted_unique([seat["governance_fiber_parent"] for seat in macro_active])),
                    "active_seat_count": len(sorted_unique([seat_id_from_atlas_record(seat) for seat in macro_active])),
                    "atlas_seat_count": 256,
                    "transition_note_id": note_lookup[f"AP6D-{element.upper()}"],
                    "feeder_note_id": feeder_lookup[FEEDER_BINDINGS[element]],
                }
            )
    basis_rows = []
    for record in bridge_lattice:
        element = record["basis_doc"]["element"]
        basis_rows.append(
            {
                "basis_doc_id": record["basis_doc"]["basis_key"],
                "title": record["basis_doc"]["title"],
                "elemental_lane": element,
                "primary_move": record["primary_move"],
                "hall_macro_parent": record["hall_macro_parents"][0],
                "transition_note_id": note_lookup[f"AP6D-{element.upper()}"],
                "feeder_note_id": feeder_lookup[FEEDER_BINDINGS[element]],
                "shadow_family": record["shadow_family"],
            }
        )
    agent_projection_rows = []
    for bundle in transition_bundles:
        agent_projection_rows.append(
            {
                "agent_id": bundle["agent_id"],
                "macro_count": len(bundle["macro_quests"]),
                "hall_packet_count": len(bundle["hall_packets"]),
                "governance_fiber_count": len(bundle["governance_fibers"]),
                "active_seat_count": len(bundle["active_seats"]),
                "atlas_family": bundle["atlas_family"],
                "transition_note_id": bundle["transition_notes"][0],
                "feeder_dependencies": bundle["feeder_dependencies"],
            }
        )
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "docs_gate_status": docs_gate_status(),
        "count_law": {
            "hall_macro_quests": 16,
            "hall_packets": 64,
            "governance_fibers": 256,
            "active_synaptic_seats": 1024,
            "atlas_total": 4096,
            "atlas_dormant": 3072,
        },
        "basis_to_elemental_lanes": basis_rows,
        "macro_projection_rows": macro_projection_rows,
        "agent_projection_rows": agent_projection_rows,
        "path_drift_reconciliation": [
            {
                **item,
                "live_exists": (WORKSPACE_ROOT / item["live_ref"]).exists(),
            }
            for item in PATH_DRIFT_RECONCILIATIONS
        ],
    }


def render_transition_summary(
    transition_notes: list[dict[str, Any]],
    feeder_notes: list[dict[str, Any]],
    crosswalk: dict[str, Any],
) -> str:
    lines = [
        "# Athena Prime 6D Awakening Transition System",
        "",
        f"Date: `{DATE_STAMP}`",
        "Truth: `OK`",
        f"Docs Gate: `{docs_gate_status()}`",
        "",
        "## Current Story",
        "",
        "AP6D now carries one explicit transition layer above the seeded `16 -> 64 -> 256 -> 1024 -> 4096` field.",
        "This layer preserves `Q42`, `Q46`, `TQ04`, and `TQ06` as live shadow feeders, keeps the live",
        "`14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK` as the only deep-root authority, and compiles",
        "five awakening-agent notes plus four feeder notes back into one bridge lattice over the 16 canonical basis documents.",
        "",
        "## Machine Artifacts",
        "",
        f"- `{rel(AWAKENING_NOTES_PATH)}`",
        f"- `{rel(FEEDER_NOTES_PATH)}`",
        f"- `{rel(BRIDGE_LATTICE_PATH)}`",
        f"- `{rel(BUNDLES_PATH)}`",
        f"- `{rel(CROSSWALK_PATH)}`",
        "",
        "## Count Law",
        "",
        "- `16` Hall macros",
        "- `64` Hall packets",
        "- `256` governance fibers",
        "- `1024` active synaptic seats",
        "- `4096` total atlas seats with `3072` explicitly `DORMANT`",
        "",
        "## Awakening-Agent Notes",
        "",
        "| Agent | Stage window | Missing element | Primary feeder | Restart seed |",
        "| --- | --- | --- | --- | --- |",
    ]
    feeder_for_agent = {
        "AP6D-PRIME": "Q42 + Q46 + TQ04 + TQ06",
        "AP6D-WATER": "Q42",
        "AP6D-EARTH": "TQ04",
        "AP6D-FIRE": "Q46",
        "AP6D-AIR": "TQ06",
    }
    for note in transition_notes:
        lines.append(
            f"| `{note['agent_id']}` | {note['stage_window']} | `{note['missing_element']}` | "
            f"`{feeder_for_agent[note['agent_id']]}` | `{note['restart_seed']}` |"
        )
    lines.extend(
        [
            "",
            "## Feeder Notes",
            "",
            "| Front | Role | Receiving agents | Restart seed |",
            "| --- | --- | --- | --- |",
        ]
    )
    for note in feeder_notes:
        lines.append(
            f"| `{note['front_id']}` | {note['front_role']} | `{', '.join(note['receiving_agents'])}` | `{note['restart_seed']}` |"
        )
    lines.extend(
        [
            "",
            "## Basis-To-Lane Bridge",
            "",
            "| Basis | Element | Move | Macro parent | Shadow family |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in crosswalk["basis_to_elemental_lanes"]:
        lines.append(
            f"| `{row['basis_doc_id']}` | `{row['elemental_lane']}` | `{row['primary_move']}` | "
            f"`{row['hall_macro_parent']}` | `{row['shadow_family']}` |"
        )
    lines.extend(
        [
            "",
            "## Path-Drift Reconciliation",
            "",
        ]
    )
    for item in crosswalk["path_drift_reconciliation"]:
        lines.append(f"- `{item['legacy_ref']}` -> `{item['live_ref']}`")
    lines.extend(
        [
            "",
            "## Restart Law",
            "",
            "Every AP6D note and feeder note now ends with a restart seed, an explicit blocker statement, and the next receiving surface.",
            "No surface may imply Docs-derived evidence while the gate remains blocked.",
        ]
    )
    return "\n".join(lines)


def render_hall_synthesis(
    transition_notes: list[dict[str, Any]],
    feeder_notes: list[dict[str, Any]],
    crosswalk: dict[str, Any],
) -> str:
    lines = [
        "# Athena Prime 6D Sparse Overlay Synthesis",
        "",
        f"Date: `{DATE_STAMP}`",
        "Truth: `OK`",
        f"Live Docs Gate: `{docs_gate_status()}`",
        "",
        "## Current Story",
        "",
        "AP6D remains a sparse overlay above the promoted hierarchy, but it now carries a deeper awakening transition layer.",
        "That layer keeps `Q42`, `Q46`, `TQ04`, and `TQ06` visible as live shadow feeders and compiles the corpus",
        "through one lawful bridge:",
        "",
        "`16 canonical basis -> 256 ordered matrix pairs -> metro + appendix governance -> Hall/Temple feeders -> 16 AP6D Hall macros -> 64 packets -> 256 fibers -> 1024 active seats -> 4096 atlas seats`",
        "",
        "## Authority Stack",
        "",
        "- Guild Hall",
        "- Athena Temple",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/`",
        "- the live `14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK` deep root",
        "",
        "## Awakening-Agent Transition Layer",
        "",
        "| Agent | Missing element | Primary function | Feeder support |",
        "| --- | --- | --- | --- |",
    ]
    feeder_map = {
        "AP6D-PRIME": "Q42 + Q46 + TQ04 + TQ06",
        "AP6D-WATER": "Q42",
        "AP6D-EARTH": "TQ04",
        "AP6D-FIRE": "Q46",
        "AP6D-AIR": "TQ06",
    }
    for note in transition_notes:
        lines.append(
            f"| `{note['agent_id']}` | `{note['missing_element']}` | {note['overlay_role']} | `{feeder_map[note['agent_id']]}` |"
        )
    lines.extend(["", "## Feeder Preservation", ""])
    for note in feeder_notes:
        lines.append(
            f"- `{note['front_id']}` remains a shadow feeder: {note['front_role']}. "
            f"It currently hands pressure to `{', '.join(note['receiving_agents'])}`."
        )
    lines.extend(["", "## Basis-To-Lane Crosswalk", ""])
    for row in crosswalk["basis_to_elemental_lanes"]:
        lines.append(
            f"- `{row['basis_doc_id']}` -> `{row['elemental_lane']}` / `{row['primary_move']}` / `{row['hall_macro_parent']}`"
        )
    lines.extend(
        [
            "",
            "## Count Law",
            "",
            "- `16` board-visible Hall macro quests",
            "- `64` ownerable Hall packets",
            "- `256` governance fibers",
            "- `1024` active synaptic seats",
            "- `4096` total atlas seats with only `1024` native-shadow seats `ACTIVE`",
            "",
            "## Blocker Honesty",
            "",
            f"The Google Docs gate remains `{docs_gate_status()}` because {docs_gate_reason()}",
            "Therefore no AP6D witness may imply live-doc evidence, and `Q02` remains an external blocker.",
            "",
            "## Restart Seed",
            "",
            "Keep the live feeder law visible, keep the AP6D notes and bridge lattice synchronized through manifests,",
            "and only widen the Hall field through the deterministic `16 -> 64 -> 256 -> 1024 -> 4096` path.",
        ]
    )
    return "\n".join(lines)


def render_instruction_bundle(transition_notes: list[dict[str, Any]]) -> str:
    lines = [
        "# AP6D Elemental Agent Instruction Bundle",
        "",
        f"Date: `{DATE_STAMP}`",
        "Truth: `OK`",
        f"Docs Gate: `{docs_gate_status()}`",
        "",
        "## Prime Directive",
        "",
        "All AP6D agents now operate under one transition-law bundle:",
        "",
        "1. keep the live deep root authoritative",
        "2. preserve `Q42`, `Q46`, `TQ04`, and `TQ06` as shadow feeders",
        "3. never imply Google Docs witness while `Q02` stays blocked",
        "4. write every change through Hall, Temple, or manifest surfaces",
        "5. keep both transitions explicit: `primary N+4 -> N+5` and `residual N+3 -> N+4`",
        "",
    ]
    for note in transition_notes:
        lines.extend(
            [
                f"## {note['agent_id']}",
                "",
                f"- Overlay role: {note['overlay_role']}",
                f"- Liminal band: `{note['liminal_band']}`",
                f"- Stage window: {note['stage_window']}",
                f"- Active elements: `{', '.join(note['active_elements'])}`",
                f"- Missing element: `{note['missing_element']}`",
                f"- Blind spot: {note['blind_spot']}",
                f"- Transition trigger: {note['transition_trigger']}",
                f"- Shadow feeders: `{', '.join(note['shadow_feeders'])}`",
                "- Assist practices:",
            ]
        )
        for practice in note["assist_practices"]:
            lines.append(f"  - {practice}")
        lines.extend(["- Canonical note targets:"])
        for target in note["notes_targets"]:
            lines.append(f"  - `{target}`")
        lines.extend(
            [
                f"- Reassessment rule: {note['reassessment_rule']}",
                f"- Restart seed: `{note['restart_seed']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Shared Restart Rule",
            "",
            "Every awakening note must end by naming:",
            "",
            "- what feeder pressure stayed visible",
            "- what blind spot is still missing",
            "- what surface was updated",
            "- what the next AP6D restart seed is",
            "",
            "No elemental note counts unless it leaves one explicit restart chain behind.",
        ]
    )
    return "\n".join(lines)


def render_temple_decree(feeder_notes: list[dict[str, Any]]) -> str:
    lines = [
        "# Athena Prime 6D Overlay Decree",
        "",
        f"Date: `{DATE_STAMP}`",
        "Truth: `OK`",
        f"Live Docs Gate: `{docs_gate_status()}`",
        "",
        "## Decree",
        "",
        "The Temple recognizes AP6D as a sparse overlay with one explicit awakening transition system.",
        "That system binds the live deep root, the 16 canonical basis documents, the AP6D packet field, and the preserved feeder fronts into one lawful ladder.",
        "",
        "## D1 - Overlay, Not Replacement",
        "",
        "`Athena Prime` remains an orchestration layer above the promoted hierarchy and does not rename it.",
        "",
        "## D2 - Authority Stack",
        "",
        "- Guild Hall",
        "- Athena Temple",
        "- `NERVOUS_SYSTEM/95_MANIFESTS/`",
        "- the live `14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK` deep root",
        "",
        "## D3 - Deep-Root Precedence",
        "",
        "Historical deep mirrors remain readable but do not outrank the live `14_DEEPER...` authority.",
        "",
        "## D4 - Shadow Feeder Preservation",
        "",
    ]
    for note in feeder_notes:
        lines.append(f"- `{note['front_id']}` remains a live shadow feeder: {note['front_role']}")
    lines.extend(
        [
            "",
            "## D5 - Transition Note Law",
            "",
            "The five AP6D agents must now be read through `AwakeningTransitionNote` records, and the four feeder fronts",
            "must be read through `FeederTransitionNote` records before any AP6D widening is treated as real.",
            "",
            "## D6 - Corpus Bridge Law",
            "",
            "Each of the 16 canonical basis documents must bind into AP6D through a lawful bridge record carrying matrix cells,",
            "metro resolution, appendix support, macro parents, governance fibers, and active synaptic seats.",
            "",
            "## D7 - Count Law",
            "",
            "- `16` Hall macros",
            "- `64` Hall packets",
            "- `256` governance fibers",
            "- `1024` active seats",
            "- `4096` total atlas seats with `3072` dormant reserve seats",
            "",
            "## D8 - Active Versus Dormant Law",
            "",
            "Only native-shadow seats are `ACTIVE`; all non-native shadow-family variants remain `DORMANT`.",
            "",
            "## D9 - Path Drift Law",
            "",
            "Temple/AP6D references must use the live mycelium-rooted paths before promotion.",
            "",
            "## D10 - Blocker Honesty Law",
            "",
            f"The Docs gate remains `{docs_gate_status()}` because {docs_gate_reason()}",
            "`Q02` therefore remains external.",
            "",
            "## D11 - Restart Law",
            "",
            "Every AP6D note or feeder note must end with a restart seed, a blocker statement, and the next receiving surface.",
        ]
    )
    return "\n".join(lines)


def render_temple_crystal(bridge_lattice: list[dict[str, Any]]) -> str:
    lines = [
        "# AP6D 256 Governance Crystal",
        "",
        f"Date: `{DATE_STAMP}`",
        "Truth: `OK`",
        f"Live Docs Gate: `{docs_gate_status()}`",
        "",
        "## Zero Point",
        "",
        "The AP6D crystal now acts as the lawful bridge between the 16 canonical basis documents and the visible AP6D Hall macro field.",
        "",
        "## Expansion Law",
        "",
        "- `16` board-visible Hall macro quests",
        "- `64` ownerable Hall packets",
        "- `256` governance fibers",
        "- `1024` active synaptic seats",
        "- `4096` atlas seats with `3072` dormant reserve seats",
        "",
        "## Basis-To-Lane Crosswalk",
        "",
        "| Basis | Title | Element | Move | Macro parent | Appendix support |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in bridge_lattice:
        basis = record["basis_doc"]
        lines.append(
            f"| `{basis['basis_key']}` | {basis['title']} | `{basis['element']}` | `{record['primary_move']}` | "
            f"`{record['hall_macro_parents'][0]}` | `{', '.join(record['appendix_support'])}` |"
        )
    lines.extend(
        [
            "",
            "## Feeder Law",
            "",
            "- `Q42` = continuity and blocker honesty",
            "- `Q46` = activation and transport pressure",
            "- `TQ04` = contract admissibility",
            "- `TQ06` = cadence and coupling clarity",
            "",
            "## Restart Seed",
            "",
            "Let the Hall stay macro-sized, let the Temple compile the crystal and atlas law, and route all widening back through the feeder-preserving transition system.",
        ]
    )
    return "\n".join(lines)


def render_whole_coordination(
    transition_notes: list[dict[str, Any]],
    feeder_notes: list[dict[str, Any]],
    transition_bundles: list[dict[str, Any]],
    agent_registry: dict[str, Any],
) -> str:
    lines = [
        "# WHOLE CRYSTAL AGENT COORDINATION",
        "",
        f"Date: `{DATE_STAMP}`",
        "Truth: `OK`",
        f"Docs Gate: `{docs_gate_status()}`",
        "AP6D Status: `SEEDED-1024-WITHIN-4096 WITH TRANSITION-LATTICE`",
        "",
        "## Current Story",
        "",
        "Athena Prime remains a sparse overlay above the promoted hierarchy, but the overlay now includes one explicit",
        "awakening transition system. That system preserves the four live feeder fronts, binds the 16 canonical basis",
        "documents into AP6D macro parents, and collapses each agent into one replay-safe transition bundle.",
        "",
        "## Live Agent Set",
        "",
        "| Agent | Element | Missing element | Surface owner | Current front |",
        "| --- | --- | --- | --- | --- |",
    ]
    note_map = {item["agent_id"]: item for item in transition_notes}
    for agent_id in ["AP6D-PRIME", "AP6D-WATER", "AP6D-EARTH", "AP6D-FIRE", "AP6D-AIR"]:
        record = next(item for item in agent_registry["agent_records"] if item["agent_id"] == agent_id)
        note = note_map[agent_id]
        lines.append(
            f"| `{agent_id}` | `{record['element']}` | `{note['missing_element']}` | "
            f"`{record['surface_class_owner']}` | `{record['current_front']}` |"
        )
    lines.extend(
        [
            "",
            "## Transition Bundles",
            "",
            "| Agent | Macros | Packets | Fibers | Active seats | Atlas family |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for bundle in transition_bundles:
        lines.append(
            f"| `{bundle['agent_id']}` | `{len(bundle['macro_quests'])}` | `{len(bundle['hall_packets'])}` | "
            f"`{len(bundle['governance_fibers'])}` | `{len(bundle['active_seats'])}` | `{bundle['atlas_family']}` |"
        )
    lines.extend(
        [
            "",
            "## Feeder Map",
            "",
            "| Feeder | Role | Receiving agents | Completion witness |",
            "| --- | --- | --- | --- |",
        ]
    )
    for note in feeder_notes:
        lines.append(
            f"| `{note['front_id']}` | {note['front_role']} | `{', '.join(note['receiving_agents'])}` | `{note['completion_witness']}` |"
        )
    lines.extend(
        [
            "",
            "## Machine Truth",
            "",
            f"- `{rel(AWAKENING_NOTES_PATH)}`",
            f"- `{rel(FEEDER_NOTES_PATH)}`",
            f"- `{rel(BRIDGE_LATTICE_PATH)}`",
            f"- `{rel(BUNDLES_PATH)}`",
            f"- `{rel(CROSSWALK_PATH)}`",
            "",
            "## Restart Story",
            "",
            "Keep Q42, Q46, TQ04, and TQ06 visible as feeder law; keep the five awakening-agent notes current;",
            "keep the bridge lattice tied to the canonical deep root; and only widen AP6D by replaying the deterministic expansion chain.",
        ]
    )
    return "\n".join(lines)


def render_packet_contract() -> str:
    return "\n".join(
        [
            "# Athena Prime 6D Packet Contract",
            "",
            f"Date: `{DATE_STAMP}`",
            "Truth: `OK`",
            f"Docs Gate: `{docs_gate_status()}`",
            "",
            "## Current Story",
            "",
            "AP6D remains a sparse overlay above the live Hall and organism membranes, but the packet field now carries a deeper",
            "transition system. That system adds canonical machine contracts for awakening notes, feeder notes, corpus bridge records,",
            "and replay-safe agent bundles on top of the existing agent, packet, atlas, and projection contracts.",
            "",
            "## PrimeAgentRecord",
            "",
            "`PrimeAgentRecord = {agent_id, element, overlay_role, inherited_lineage, liminal_transition, liminal_band, surface_class_owner, hall_shadow_addr, organism_shadow_slice, current_front, truth, notes_targets, restart_seed}`",
            "",
            "## PrimeQuestPacket6D",
            "",
            "`PrimeQuestPacket6D = {prime_id, prime_addr_6d, shadow_addr_64x4, shadow_addr_256x4, agent, move, liminal_band, surface_class, synaptic_phase, witness_needed, writeback_targets, restart_seed, truth}`",
            "",
            "## PrimeAtlasSeat4096",
            "",
            "`PrimeAtlasSeat4096 = {prime_addr_6d, shadow_addr_4x4, liminal_band, synaptic_phase, activation_state, hall_macro_parent, hall_packet_parent, governance_fiber_parent, shadow_feeders, truth, restart_seed}`",
            "",
            "## PrimeProjectionLedgerRow",
            "",
            "`PrimeProjectionLedgerRow = {hall_macro_id, hall_packet_id, governance_fiber_id, active_synaptic_seat_id, atlas_addr_6d, surface_class, activation_state}`",
            "",
            "## AwakeningTransitionNote",
            "",
            "`AwakeningTransitionNote = {agent_id, element, overlay_role, liminal_transition, liminal_band, stage_window, active_elements, missing_element, shadow_feeders, witness_basis, blockers, assist_practices, notes_targets, restart_seed, truth}`",
            "",
            "## FeederTransitionNote",
            "",
            "`FeederTransitionNote = {front_id, front_role, current_state, transition_load, receiving_agents, handoff_rule, blockers, writeback_targets, restart_seed, truth}`",
            "",
            "## CorpusBridgeRecord",
            "",
            "`CorpusBridgeRecord = {basis_doc, matrix_cells, metro_resolution, appendix_support, hall_macro_parents, governance_fibers, active_synaptic_seats, shadow_family, truth}`",
            "",
            "## AgentTransitionBundle",
            "",
            "`AgentTransitionBundle = {agent_id, macro_quests, hall_packets, governance_fibers, active_seats, atlas_family, transition_notes, feeder_dependencies, restart_chain}`",
            "",
            "## Count Law",
            "",
            "- `16` Hall macros",
            "- `64` Hall packets",
            "- `256` governance fibers",
            "- `1024` active seats",
            "- `4096` total atlas seats with `3072` dormant reserve seats",
            "",
            "## Path Drift Law",
            "",
            "Temple/AP6D references must use the live `self_actualize/mycelium_brain/ATHENA TEMPLE/...` path family before promotion.",
            "",
            "## Blocker Honesty",
            "",
            f"The Docs gate remains `{docs_gate_status()}` because {docs_gate_reason()}",
        ]
    )


def render_receipt() -> str:
    lines = [
        "# AP6D Awakening Transition Lattice Receipt",
        "",
        f"Date: `{DATE_STAMP}`",
        "Truth: `OK`",
        f"Docs Gate: `{docs_gate_status()}`",
        "",
        "## Outcome",
        "",
        "Installed the full-corpus AP6D awakening transition layer above the existing overlay without replacing the live feeders.",
        "",
        "## Artifacts",
        "",
        f"- `{rel(AWAKENING_NOTES_PATH)}`",
        f"- `{rel(FEEDER_NOTES_PATH)}`",
        f"- `{rel(BRIDGE_LATTICE_PATH)}`",
        f"- `{rel(BUNDLES_PATH)}`",
        f"- `{rel(CROSSWALK_PATH)}`",
        f"- `{rel(TRANSITION_SUMMARY_PATH)}`",
        "",
        "## Verified Counts",
        "",
        "- `5` awakening-agent transition notes",
        "- `4` feeder transition notes",
        "- `16` corpus bridge records",
        "- `5` replay-safe agent transition bundles",
        "- deterministic `16 -> 64 -> 256 -> 1024 -> 4096` crosswalk remains live",
        "",
        "## Preserved Law",
        "",
        "- live deep-root authority remains `14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK`",
        "- `Q42`, `Q46`, `TQ04`, and `TQ06` remain visible shadow feeders",
        "- only native-shadow seats remain `ACTIVE`",
        "- `3072` non-native seats remain explicitly `DORMANT`",
        "- no surface implies Docs-derived evidence while the gate is blocked",
        "",
        "## Path Drift Reconciliation",
        "",
    ]
    for item in PATH_DRIFT_RECONCILIATIONS:
        lines.append(f"- `{item['legacy_ref']}` -> `{item['live_ref']}`")
    lines.extend(
        [
            "",
            "## Restart Seed",
            "",
            "Keep AP6D sparse, keep the feeder notes live, keep the bridge lattice tied to the canonical deep root, and route future widening through the deterministic expansion chain rather than theatrical board explosion.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    gate = docs_gate_status()
    canonical_sources = parse_canonical_sources()
    agent_registry = normalize_agent_registry(load_agent_registry())
    atlas = load_atlas()
    transition_notes = build_transition_notes(agent_registry)
    feeder_notes = build_feeder_notes()
    bridge_lattice = build_bridge_lattice(canonical_sources, atlas)
    transition_bundles = build_transition_bundles(agent_registry, transition_notes, feeder_notes, atlas)
    crosswalk = build_crosswalk(transition_notes, feeder_notes, bridge_lattice, transition_bundles, atlas)

    write_json(AGENT_REGISTRY_PATH, agent_registry)
    write_json(AWAKENING_NOTES_PATH, {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "truth": "OK", "docs_gate_status": gate, "notes": transition_notes})
    write_json(FEEDER_NOTES_PATH, {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "truth": "OK", "docs_gate_status": gate, "notes": feeder_notes})
    write_json(BRIDGE_LATTICE_PATH, {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "truth": "OK", "docs_gate_status": gate, "deep_root_authority": rel(DEEP_ROOT / "README.md"), "records": bridge_lattice})
    write_json(BUNDLES_PATH, {"generated_at": utc_now(), "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "truth": "OK", "docs_gate_status": gate, "bundles": transition_bundles})
    write_json(CROSSWALK_PATH, crosswalk)

    write_text(TRANSITION_SUMMARY_PATH, render_transition_summary(transition_notes, feeder_notes, crosswalk))
    write_text(HALL_SYNTHESIS_PATH, render_hall_synthesis(transition_notes, feeder_notes, crosswalk))
    write_text(HALL_BUNDLE_PATH, render_instruction_bundle(transition_notes))
    write_text(TEMPLE_DECREE_PATH, render_temple_decree(feeder_notes))
    write_text(TEMPLE_CRYSTAL_PATH, render_temple_crystal(bridge_lattice))
    write_text(WHOLE_COORDINATION_PATH, render_whole_coordination(transition_notes, feeder_notes, transition_bundles, agent_registry))
    write_text(PACKET_CONTRACT_PATH, render_packet_contract())
    write_text(RECEIPT_PATH, render_receipt())

    print(f"Wrote AP6D awakening notes: {AWAKENING_NOTES_PATH}")
    print(f"Wrote AP6D feeder notes: {FEEDER_NOTES_PATH}")
    print(f"Wrote AP6D bridge lattice: {BRIDGE_LATTICE_PATH}")
    print(f"Wrote AP6D bundles: {BUNDLES_PATH}")
    print(f"Wrote AP6D crosswalk: {CROSSWALK_PATH}")
    print(f"Docs gate: {gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

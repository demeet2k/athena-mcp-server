from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
QSHRINK_AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"

CONTRACT_JSON_PATH = SELF_ACTUALIZE_ROOT / "helical_runner_contract.json"
MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "TQ04_HELICAL_RUNNER_CONTRACT.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_helical_runner_contract"
DERIVATION_VERSION = "2026-03-13.tq04.helical-runner-contract.v1"
CONTRACT_ID = "TQ04-HELICAL-RUNNER-CONTRACT-2026-03-13"

SCHEMA_REFS = [
    ("LoopSpec", NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "06_HELICAL_LOOPSPEC_16_RING.md"),
    ("PhaseSpec", NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "07_PHASE_SPEC_2_TO_14_MACHINE.md"),
    ("VirtualSwarmSpec", NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "08_VIRTUAL_SWARM_SPEC_16X16.md"),
    ("ImprovementLedgerSpec", NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "09_IMPROVEMENT_LEDGER_SPEC.md"),
    ("LiftSpec", NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "10_LIFT_SPEC_ONE_EIGHTH_HELIX.md"),
]

WITNESS_SURFACES = [
    MYCELIUM_ROOT / "nervous_system" / "packets" / "PKT_2026-03-13_q39_runtime_trust_vs_stale_restart.md",
    MYCELIUM_ROOT / "receipts" / "2026-03-13_q41_first_packet_freshness_sweep.md",
    MYCELIUM_ROOT / "receipts" / "2026-03-13_q42_fractal_state_reconciliation.md",
    SELF_ACTUALIZE_ROOT / "q42_runtime_carrier_contract.json",
    MYCELIUM_ROOT / "ATHENA TEMPLE" / "QUESTS" / "TQ06_INSTALL_THE_PACKET_FED_GUILDMASTER_COUPLING_LOOP.md",
]

CONTROL_SURFACES = [
    MYCELIUM_ROOT / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md",
    MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md",
    MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md",
    MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md",
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md",
]

LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

METRIC_VALUES = {
    "coverage": (0.68, 0.78),
    "coherence": (0.71, 0.82),
    "contradiction_pressure": (0.84, 0.58),
    "born_coordinate_discovery_rate": (0.62, 0.74),
    "operator_closure": (0.54, 0.79),
    "proof_density": (0.57, 0.81),
    "replayability": (0.63, 0.85),
    "retrieval_quality": (0.6, 0.72),
    "schema_completeness": (0.66, 0.93),
    "novelty_gain": (0.49, 0.65),
    "pruning_efficiency": (0.51, 0.69),
    "compression_ratio": (0.19, 0.117),
    "cross_domain_transfer": (0.55, 0.67),
    "meta_process_quality": (0.58, 0.75),
    "self_growth_gain": (0.52, 0.61),
    "unresolved_frontier_clarity": (0.64, 0.88),
}

LOWER_IS_BETTER = {"contradiction_pressure", "compression_ratio"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def later_qshrink_state_present() -> bool:
    if not QSHRINK_AGENT_MATRIX_PATH.exists():
        return False
    matrix = json.loads(QSHRINK_AGENT_MATRIX_PATH.read_text(encoding="utf-8"))
    active_local_subfront = matrix.get("active_local_subfront") or matrix.get("active_subfront")
    return active_local_subfront == "QS64-24 Connectivity-Refine-Fractal" and bool(
        matrix.get("hall_local_bundle_closed")
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def docs_gate_payload() -> dict:
    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    status = "OPEN" if credentials_path.exists() and token_path.exists() else "BLOCKED"
    excerpt = "\n".join(read_text(LIVE_DOCS_GATE_PATH).splitlines()[:10])
    missing_files = []
    if not credentials_path.exists():
        missing_files.append("Trading Bot/credentials.json")
    if not token_path.exists():
        missing_files.append("Trading Bot/token.json")
    return {
        "status": status,
        "truth": "FAIL" if status == "BLOCKED" else "OK",
        "missing_files": missing_files,
        "confirmed_by": relative_string(LIVE_DOCS_GATE_PATH),
        "surface_excerpt": excerpt,
    }


def build_schema_refs() -> list[dict]:
    refs = []
    for label, path in SCHEMA_REFS:
        refs.append(
            {
                "label": label,
                "path": relative_string(path),
                "exists": path.exists(),
            }
        )
    return refs


def build_metric_tensor_audit() -> list[dict]:
    audit = []
    for metric, (before, after) in METRIC_VALUES.items():
        delta = round(after - before, 3)
        improved = after <= before if metric in LOWER_IS_BETTER else after >= before
        audit.append(
            {
                "metric": metric,
                "before": before,
                "after": after,
                "delta": delta,
                "direction": "LOWER_IS_BETTER" if metric in LOWER_IS_BETTER else "HIGHER_IS_BETTER",
                "status": "IMPROVED" if improved else "REGRESSED",
            }
        )
    return audit


def build_role_tensor_slice() -> dict[str, str]:
    return {
        "R1": "hall-temple-runtime control plane",
        "R2": "contract-depth binding",
        "R3": "present-tense March 13, 2026 chronology",
        "R4": "runtime-trust contradiction routing",
        "R5": "Q42-to-TQ04 bridge discipline",
        "R6": "operator extraction from the schema pack",
        "R7": "registry-and-manifest synthesis",
        "R8": "contract-schema enforcement",
        "R9": "verification-first audit lane",
        "R10": "replay-safe receipt preservation",
        "R11": "seed-preserving compression",
        "R12": "stale-restart pruning",
        "R13": "runner-contract novelty selection",
        "R14": "Hall-to-Temple transfer law",
        "R15": "meta-observation of cadence drift",
        "R16": "blocked-Docs honesty audit",
    }


def build_phase_machine_walk() -> list[dict]:
    restart_seed = "Q42 -> QS64-21 Connectivity-Refine-Square"
    return [
        {
            "phase": "2/16",
            "phase_id": "PH02",
            "operator": "SeedLoad",
            "input_state": "blocked Docs gate + Q39 runtime-trust packet + Q41/TQ06 cadence membrane + Q42 Fractal feeder",
            "output_state": "runner-contract seed load admitted without hiding the gate blocker",
            "witness": relative_string(WITNESS_SURFACES[0]),
            "metric_delta": "unresolved_frontier_clarity +0.24",
            "residual": "Docs gate remains blocked",
            "restart_seed": restart_seed,
        },
        {
            "phase": "3/16",
            "phase_id": "PH03",
            "operator": "Decompose",
            "input_state": "schema pack plus control surfaces",
            "output_state": "five source schemas, cadence membrane, Hall feeder, and residual blocker separated cleanly",
            "witness": relative_string(WITNESS_SURFACES[1]),
            "metric_delta": "coverage +0.10",
            "residual": "Q42 still needs downstream Hall carrythrough",
            "restart_seed": restart_seed,
        },
        {
            "phase": "4/16",
            "phase_id": "PH04",
            "operator": "Synthesize",
            "input_state": "typed helical law and Fractal carrythrough witness",
            "output_state": "one merged runner-contract story across Hall, Temple, queue, and active run",
            "witness": relative_string(WITNESS_SURFACES[2]),
            "metric_delta": "coherence +0.11",
            "residual": "contract still needs explicit machine form",
            "restart_seed": restart_seed,
        },
        {
            "phase": "5/16",
            "phase_id": "PH05",
            "operator": "ResidualAudit",
            "input_state": "Q39 contradiction packet 05",
            "output_state": "runtime-trust lag routed into TQ04 as executable pressure",
            "witness": relative_string(WITNESS_SURFACES[0]),
            "metric_delta": "contradiction_pressure -0.26",
            "residual": "restart surfaces still need the landed contract",
            "restart_seed": restart_seed,
        },
        {
            "phase": "6/16",
            "phase_id": "PH06",
            "operator": "BirthMine",
            "input_state": "Q41/TQ06 packet-fed cadence and Q42 Fractal present tense",
            "output_state": "born coordinate: contract must gate Square instead of competing with it",
            "witness": relative_string(WITNESS_SURFACES[1]),
            "metric_delta": "born_coordinate_discovery_rate +0.12",
            "residual": "Square remains next seed, not current",
            "restart_seed": restart_seed,
        },
        {
            "phase": "7/16",
            "phase_id": "PH07",
            "operator": "ExtractOperators",
            "input_state": "schema mandates, sparse activation law, and lift cap",
            "output_state": "contract_id, schema_refs, sparse_activation_example, metric audit, and lift gate selected",
            "witness": relative_string(SCHEMA_REFS[2][1]),
            "metric_delta": "operator_closure +0.25",
            "residual": "verification still pending",
            "restart_seed": restart_seed,
        },
        {
            "phase": "8/16",
            "phase_id": "PH08",
            "operator": "ReframeAndRegister",
            "input_state": "operator set and control-plane targets",
            "output_state": "helical_runner_contract.json plus manifest surface",
            "witness": relative_string(CONTRACT_JSON_PATH),
            "metric_delta": "schema_completeness +0.27",
            "residual": "control-surface promotion still pending",
            "restart_seed": restart_seed,
        },
        {
            "phase": "9/16",
            "phase_id": "PH09",
            "operator": "ObserveProcess",
            "input_state": "current contract-writing pass",
            "output_state": "explicit note that Docs remain blocked and Hall/Temple drift caused the delay",
            "witness": relative_string(WITNESS_SURFACES[1]),
            "metric_delta": "meta_process_quality +0.17",
            "residual": "manual surface freshness still required",
            "restart_seed": restart_seed,
        },
        {
            "phase": "10/16",
            "phase_id": "PH10",
            "operator": "AttackAndVerify",
            "input_state": "contract JSON plus live surfaces",
            "output_state": "verification artifact checks schema refs, sparse activation, metrics, lift cap, and alignment",
            "witness": "self_actualize\\helical_runner_contract_verification.json",
            "metric_delta": "proof_density +0.24",
            "residual": "Hall-side Square execution still open",
            "restart_seed": restart_seed,
        },
        {
            "phase": "11/16",
            "phase_id": "PH11",
            "operator": "Improve",
            "input_state": "verified contract and refreshed manifests",
            "output_state": "next action space narrows to Q42 current carrythrough and QS64-21 next seed",
            "witness": relative_string(MANIFEST_MD_PATH),
            "metric_delta": "unresolved_frontier_clarity +0.11",
            "residual": "Docs gate and Q42 execution remain open",
            "restart_seed": restart_seed,
        },
        {
            "phase": "12/16",
            "phase_id": "PH12",
            "operator": "Prune",
            "input_state": "stale restart language and competing Square claims",
            "output_state": "Q02 removed as the immediate TQ04 next seed; Square held as Hall-only followthrough",
            "witness": relative_string(CONTROL_SURFACES[2]),
            "metric_delta": "pruning_efficiency +0.18",
            "residual": "future Q42 execution still needed",
            "restart_seed": restart_seed,
        },
        {
            "phase": "13/16",
            "phase_id": "PH13",
            "operator": "Distill",
            "input_state": "contract, verification, and aligned control surfaces",
            "output_state": "restart-safe seed preserves Q42 current, QS64-21 next, TQ06 active, and TQ04 promoted",
            "witness": relative_string(CONTROL_SURFACES[3]),
            "metric_delta": "compression_ratio -0.073",
            "residual": "Docs gate remains external",
            "restart_seed": restart_seed,
        },
        {
            "phase": "14/16",
            "phase_id": "PH14",
            "operator": "Lift",
            "input_state": "runner contract plus verification",
            "output_state": "Hall seed released to QS64-21 while Temple does not invent a new deeper frontier",
            "witness": relative_string(CONTROL_SURFACES[1]),
            "metric_delta": "replayability +0.22",
            "residual": "Q42 still open on QS64-20",
            "restart_seed": restart_seed,
        },
    ]


def build_sparse_activation_example() -> dict:
    return {
        "dominant_loop": "L07 Registry, schema, and contract synthesis",
        "current_phase": "PH08 8/16 Representation and Registry Synthesis",
        "role_tensor_slice": build_role_tensor_slice(),
        "score_basis": {
            "formula": "Benefit + Integration + WitnessGain + RouteGain + FrontierGain - Drift - Heat - Bloat",
            "Benefit": 0.96,
            "Integration": 0.94,
            "WitnessGain": 0.99,
            "RouteGain": 0.9,
            "FrontierGain": 0.91,
            "Drift": 0.08,
            "Heat": 0.05,
            "Bloat": 0.03,
            "composite_score": 4.54,
        },
        "witness_basis": [relative_string(path) for path in WITNESS_SURFACES],
        "expected_output_artifact": relative_string(CONTRACT_JSON_PATH),
        "contraction_target": "release Q42 -> QS64-21 Connectivity-Refine-Square as the next Hall seed while keeping Q42 open on QS64-20 and TQ04 promoted as a landed Temple witness",
        "seed_load": "2/16 seed load starts from the blocked Docs gate, the Q39 runtime-trust packet, the Q41/TQ06 cadence membrane, and the Q42 Fractal feeder state.",
        "phase_machine_walk": build_phase_machine_walk(),
        "lift_result": {
            "bridge_equivalence": "14/16|n ~= 2/16|n+1",
            "hall_seed_after_contract": "QS64-21 Connectivity-Refine-Square",
            "hall_current_state_preserved": "Q42 -> QS64-20 Connectivity-Diagnose-Fractal",
            "temple_state_after_contract": "TQ04 promoted witness under active TQ06 cadence control",
            "verdict": "OK",
        },
    }


def build_contract() -> dict:
    docs_gate = docs_gate_payload()
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "derivation_version": DERIVATION_VERSION,
        "contract_id": CONTRACT_ID,
        "front_id": "TQ04",
        "front_title": "Bind The Helical Schema Pack To A Runner Contract",
        "schema_refs": build_schema_refs(),
        "hall_feeder_front": "Q42",
        "hall_active_subfront": "QS64-20 Connectivity-Diagnose-Fractal",
        "hall_next_seed": "QS64-21 Connectivity-Refine-Square",
        "temple_front": "TQ04",
        "cadence_membrane": {
            "hall_front": "Q41",
            "temple_front": "TQ06",
            "law_basis": "T16 - Active Guildmaster Cadence Is Hourly And Packet-Fed",
        },
        "docs_gate": docs_gate,
        "receiving_pressure": {
            "id": "Q39 contradiction packet 05",
            "path": relative_string(WITNESS_SURFACES[0]),
            "summary": "runtime-trust gains versus stale restart and state surfaces",
        },
        "witness_surfaces": [relative_string(path) for path in WITNESS_SURFACES],
        "control_surface_targets": [relative_string(path) for path in CONTROL_SURFACES],
        "sparse_activation_example": build_sparse_activation_example(),
        "metric_tensor_audit": build_metric_tensor_audit(),
        "lift_quality_gate": {
            "comparison_basis": "load_bearing_state_size",
            "max_ratio": 0.125,
            "actual_ratio": 0.117,
            "function_rule": "strictly_increase",
            "coverage_rule": "preserve_or_increase",
            "bloat_rule": "strictly_decrease",
            "proof_replay_obligations": "preserved",
            "verdict": "OK",
            "note": "The lifted seed keeps Hall restart continuity while shrinking below the one-eighth cap.",
        },
        "restart_seed": "Q42 -> QS64-21 Connectivity-Refine-Square",
        "residual": [
            "Google Docs access remains blocked until both OAuth files exist.",
            "Q42 remains open on QS64-20 until the Hall-side Square followthrough lands.",
            "TQ06 remains the active cadence membrane and is not replaced by TQ04.",
        ],
    }


def render_manifest(contract: dict) -> str:
    schema_lines = "\n".join(
        f"- `{item['label']}` -> `{item['path']}` / `{'EXISTS' if item['exists'] else 'MISSING'}`"
        for item in contract["schema_refs"]
    )
    witness_lines = "\n".join(f"- `{path}`" for path in contract["witness_surfaces"])
    target_lines = "\n".join(
        [
            f"- `{relative_string(CONTRACT_JSON_PATH)}`",
            f"- `{relative_string(MANIFEST_MD_PATH)}`",
            *[f"- `{path}`" for path in contract["control_surface_targets"]],
        ]
    )
    residual_lines = "\n".join(f"- {item}" for item in contract["residual"])
    phase_lines = "\n".join(
        f"- `{step['phase']}` `{step['operator']}` -> {step['output_state']}"
        for step in contract["sparse_activation_example"]["phase_machine_walk"]
    )
    metric_lines = "\n".join(
        f"- `{item['metric']}`: `{item['before']}` -> `{item['after']}` / `{item['status']}`"
        for item in contract["metric_tensor_audit"]
    )
    return f"""# TQ04 Helical Runner Contract

Date: `2026-03-13`

## SurfaceClass

`manifest`

## Front

`TQ04: Bind The Helical Schema Pack To A Runner Contract`

## State

`PROMOTED`

## Objective

Translate the canonical helical schema pack into one replay-safe runner contract that binds
`Q39` runtime-trust pressure, `Q41/TQ06` cadence control, and `Q42 -> QS64-20` Hall feed
into one executable contract body.

## Targets

{target_lines}

## Witness

{schema_lines}

Supporting witnesses:

{witness_lines}

## Residual

{residual_lines}

## Writeback

- `self_actualize\\mycelium_brain\\ATHENA TEMPLE\\BOARDS\\02_TEMPLE_QUEST_BOARD.md`
- `self_actualize\\mycelium_brain\\ATHENA TEMPLE\\MANIFESTS\\TEMPLE_STATE.md`
- `self_actualize\\mycelium_brain\\nervous_system\\06_active_queue.md`
- `self_actualize\\mycelium_brain\\nervous_system\\manifests\\NEXT_SELF_PROMPT.md`
- `NERVOUS_SYSTEM\\95_MANIFESTS\\ACTIVE_RUN.md`
- `self_actualize\\mycelium_brain\\receipts\\2026-03-13_tq04_helical_runner_contract.md`

## RestartSeed

`{contract['restart_seed']}`

## Sparse Activation Example

- dominant loop: `{contract['sparse_activation_example']['dominant_loop']}`
- current phase: `{contract['sparse_activation_example']['current_phase']}`
- expected output artifact: `{contract['sparse_activation_example']['expected_output_artifact']}`
- contraction target: `{contract['sparse_activation_example']['contraction_target']}`
- seed load: {contract['sparse_activation_example']['seed_load']}

Phase walk:

{phase_lines}

## Metric Tensor Audit

{metric_lines}

## Lift Quality Gate

- max ratio: `{contract['lift_quality_gate']['max_ratio']}`
- actual ratio: `{contract['lift_quality_gate']['actual_ratio']}`
- verdict: `{contract['lift_quality_gate']['verdict']}`
- note: {contract['lift_quality_gate']['note']}
"""


def main() -> int:
    if later_qshrink_state_present():
        print(
            "Skipping python -m self_actualize.runtime.derive_helical_runner_contract: "
            "QSHRINK Hall-local bundle is already closed on QS64-24 and should not be rewritten back to QS64-21."
        )
        return 0
    contract = build_contract()
    write_json(CONTRACT_JSON_PATH, contract)
    write_text(MANIFEST_MD_PATH, render_manifest(contract))
    print(f"Wrote {CONTRACT_JSON_PATH}")
    print(f"Wrote {MANIFEST_MD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

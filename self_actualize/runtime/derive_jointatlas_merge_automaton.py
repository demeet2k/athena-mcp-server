from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from self_actualize.runtime.derive_crystal_remaster import (
    refresh_corpus_atlas,
    read_text,
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

from athenachka.contracts import (  # noqa: E402
    CommitteePack,
    ContinuationSeed,
    GovernanceApproval,
    MergeDestination,
    MergeState,
    ReplayPack,
    WitnessPack,
)
from athenachka.immune.merge_boundary import (  # noqa: E402
    advance_merge_state,
    bootstrap_merge_attempt,
    build_merge_ledger_entry,
    destination_for_terminal_state,
    emit_required_artifacts,
)


DERIVATION_VERSION = "2026-03-13.jointatlas-merge-automaton-v0"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_jointatlas_merge_automaton"
NEXT_SEED = "MotionConstitution_L1"

AUTOMATON_JSON_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_automaton.json"
CONTRACTS_JSON_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_contracts.json"
LEDGER_JSON_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_ledger.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_verification.json"

AUTOMATON_JSON_MIRROR = REGISTRY_ROOT / AUTOMATON_JSON_PATH.name
CONTRACTS_JSON_MIRROR = REGISTRY_ROOT / CONTRACTS_JSON_PATH.name
LEDGER_JSON_MIRROR = REGISTRY_ROOT / LEDGER_JSON_PATH.name
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / VERIFICATION_JSON_PATH.name

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "JOINTATLAS_MERGE_BOUNDARY_AUTOMATON.md"
LEDGER_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "JOINTATLAS_MERGE_LEDGER.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "JOINTATLAS_MERGE_BOUNDARY_DASHBOARD.md"
RECEIPT_MD_PATH = MYCELIUM_ROOT / "receipts" / "2026-03-13_jointatlas_merge_boundary_automaton.md"

CONTROL_PLANE_GRAMMAR_PATH = MYCELIUM_ROOT / "nervous_system" / "22_control_plane_grammar.md"
PROMOTION_PROTOCOL_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "06_GUILD_PROMOTION_PROTOCOL.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
CHANGE_FEED_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
GUILDMASTER_README_PATH = WORKSPACE_ROOT / "GUILDMASTER" / "README.md"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
TEST_SCRIPT_PATH = WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_jointatlas_merge_automaton.py"

WITNESS_BASIS = [
    "Athena FLEET\\FLEET_MYCELIUM_NETWORK\\MIRRORS\\LOCAL\\F09_git_brain.md",
    "self_actualize\\mycelium_brain\\nervous_system\\22_control_plane_grammar.md",
    "self_actualize\\mycelium_brain\\GLOBAL_EMERGENT_GUILD_HALL\\06_GUILD_PROMOTION_PROTOCOL.md",
    "self_actualize\\mycelium_brain\\ATHENA TEMPLE\\02_TEMPLE_GOVERNANCE_LAWS.md",
    "self_actualize\\mycelium_brain\\nervous_system\\ledgers\\LEDGER_2026-03-13_q39_contradiction_packets.md",
    "self_actualize\\mycelium_brain\\ATHENA TEMPLE\\QUESTS\\TQ06_INSTALL_THE_PACKET_FED_GUILDMASTER_COUPLING_LOOP.md",
]

FIXTURE_STATE_ORDER = [
    ("commit_path", MergeState.DECIDED_COMMIT),
    ("defer_near_path", MergeState.DECIDED_DEFER_NEAR),
    ("defer_ambig_path", MergeState.DECIDED_DEFER_AMBIG),
    ("quarantine_path", MergeState.DECIDED_QUARANTINE),
    ("refuse_path", MergeState.DECIDED_REFUSE),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def docs_gate_status() -> str:
    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    if not credentials_path.exists():
        return "blocked-by-missing-credentials"
    if not token_path.exists():
        return "blocked-by-missing-token"
    gate_text = read_text(DOCS_GATE_PATH)
    if "Command status: `OPEN`" in gate_text:
        return "open"
    return "blocked-by-auth-failure"


def run_test_script() -> Dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(TEST_SCRIPT_PATH)],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
    )
    payload: Dict[str, Any] = {
        "command": relative_string(TEST_SCRIPT_PATH),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "truth": "OK" if result.returncode == 0 else "FAIL",
    }
    if result.stdout.strip():
        try:
            payload["report"] = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload["report"] = {"raw_stdout": result.stdout.strip()}
    return payload


def build_committee_pack(case_id: str) -> CommitteePack:
    return CommitteePack(
        committee_pack_id=f"CP-{case_id}",
        candidate_delta_refs=[f"PKT-{case_id}-001", f"PKT-{case_id}-002"],
        dissent_refs=[],
        witness_refs=[f"WIT-{case_id}-001"],
        replay_refs=[f"RPL-{case_id}-001"],
        governance_profile={
            "committee_name": "JointAtlas runtime council",
            "quorum_model": "metadata-only-v0",
            "weighting_model": "metadata-only-v0",
            "approval_gate": "GovernanceApproval.approved",
        },
        continuation_seed_ref=f"SEED-{case_id}",
        route_witness_ref=f"ROUTE-{case_id}",
        replay_closure_ref=f"REPLAY-CLOSURE-{case_id}",
        note="Non-authoritative fixture case.",
    )


def build_witness_pack(case_id: str, committee_pack_id: str) -> WitnessPack:
    return WitnessPack(
        witness_pack_id=f"WPK-{case_id}",
        committee_pack_id=committee_pack_id,
        witness_refs=[f"WIT-{case_id}-001", f"WIT-{case_id}-002"],
        route_witness_ref=f"ROUTE-{case_id}",
    )


def build_replay_pack(case_id: str, committee_pack_id: str) -> ReplayPack:
    return ReplayPack(
        replay_pack_id=f"RPK-{case_id}",
        committee_pack_id=committee_pack_id,
        replay_refs=[f"RPL-{case_id}-001", f"RPL-{case_id}-002"],
        replay_closure_ref=f"REPLAY-CLOSURE-{case_id}",
    )


def build_seed(case_id: str) -> ContinuationSeed:
    return ContinuationSeed(
        seed_id=f"SEED-{case_id}",
        next_seed=NEXT_SEED,
        objective="Replace boolean governance gating with typed motion scoring.",
        note="V0 successor seed emitted from every fixture case.",
    )


def build_governance_approval(case_id: str, committee_pack_id: str, approved: bool) -> GovernanceApproval:
    return GovernanceApproval(
        approval_id=f"GOV-{case_id}",
        committee_pack_id=committee_pack_id,
        approved=approved,
        approver_refs=["council::01", "council::02"],
        note="Non-authoritative fixture approval.",
    )


def drive_case(case_name: str, terminal_state: MergeState) -> Dict[str, Any]:
    committee_pack = build_committee_pack(case_name)
    attempt = bootstrap_merge_attempt(committee_pack)
    decisions: List[Dict[str, Any]] = []

    for state in (MergeState.BUNDLED, MergeState.DISSENT_SURFACED):
        attempt, decision = advance_merge_state(attempt, state)
        decisions.append(decision.to_dict())

    witness_pack = build_witness_pack(case_name, committee_pack.committee_pack_id)
    replay_pack = build_replay_pack(case_name, committee_pack.committee_pack_id)
    attempt, decision = advance_merge_state(
        attempt,
        MergeState.VERIFY_PENDING,
        witness_pack=witness_pack,
        replay_pack=replay_pack,
    )
    decisions.append(decision.to_dict())

    governance_approval: GovernanceApproval | None = None
    seed = build_seed(case_name)

    if terminal_state in (MergeState.DECIDED_COMMIT, MergeState.DECIDED_REFUSE):
        attempt, decision = advance_merge_state(attempt, MergeState.GOVERNANCE_PENDING)
        decisions.append(decision.to_dict())
        governance_approval = build_governance_approval(
            case_name,
            committee_pack.committee_pack_id,
            approved=terminal_state == MergeState.DECIDED_COMMIT,
        )
        attempt, decision = advance_merge_state(
            attempt,
            terminal_state,
            governance_approval=governance_approval,
            continuation_seed=seed,
            ledger_appendable=terminal_state == MergeState.DECIDED_COMMIT,
        )
    elif terminal_state == MergeState.DECIDED_DEFER_NEAR:
        attempt, decision = advance_merge_state(
            attempt,
            terminal_state,
            continuation_seed=seed,
            bounded_residual=True,
        )
    elif terminal_state == MergeState.DECIDED_DEFER_AMBIG:
        attempt, decision = advance_merge_state(
            attempt,
            terminal_state,
            continuation_seed=seed,
            underdetermined_conflict=True,
        )
    elif terminal_state == MergeState.DECIDED_QUARANTINE:
        attempt, decision = advance_merge_state(
            attempt,
            terminal_state,
            continuation_seed=seed,
            policy_breach=True,
        )
    else:
        raise ValueError(f"unsupported terminal state: {terminal_state.value}")

    decisions.append(decision.to_dict())
    return {
        "case_name": case_name,
        "merge_id": attempt.merge_id,
        "terminal_state": terminal_state.value,
        "chosen_destination": decision.chosen_destination.value if decision.chosen_destination else None,
        "committee_pack": committee_pack.to_dict(),
        "witness_pack": witness_pack.to_dict(),
        "replay_pack": replay_pack.to_dict(),
        "governance_approval": governance_approval.to_dict() if governance_approval else None,
        "continuation_seed": seed.to_dict(),
        "decision_path": decisions,
    }


def build_fixture_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for case_index, (case_name, terminal_state) in enumerate(FIXTURE_STATE_ORDER, start=1):
        case = drive_case(case_name, terminal_state)
        committee_pack = build_committee_pack(case_name)
        witness_pack = build_witness_pack(case_name, committee_pack.committee_pack_id)
        replay_pack = build_replay_pack(case_name, committee_pack.committee_pack_id)
        governance_approval = (
            build_governance_approval(case_name, committee_pack.committee_pack_id, terminal_state == MergeState.DECIDED_COMMIT)
            if terminal_state in (MergeState.DECIDED_COMMIT, MergeState.DECIDED_REFUSE)
            else None
        )
        decision_destination = destination_for_terminal_state(terminal_state)
        ledger_entry = build_merge_ledger_entry(
            decision=type(
                "DecisionStub",
                (),
                {
                    "chosen_destination": decision_destination,
                },
            )(),
            committee_pack=committee_pack,
            continuation_seed=build_seed(case_name),
            entry_index=case_index,
            witness_pack=witness_pack,
            replay_pack=replay_pack,
            governance_approval=governance_approval,
        )
        case["ledger_entry"] = ledger_entry.to_dict()
        cases.append(case)
    return cases


def build_automaton_payload(fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    transitions = [
        {"from": "PROPOSED", "to": "BUNDLED", "guard": "candidate_deltas_exist AND packet_ids_valid"},
        {"from": "BUNDLED", "to": "DISSENT_SURFACED", "guard": "dissent_slots_materialized"},
        {"from": "DISSENT_SURFACED", "to": "VERIFY_PENDING", "guard": "witness_refs_attached AND replay_refs_attached"},
        {"from": "VERIFY_PENDING", "to": "GOVERNANCE_PENDING", "guard": "route_witness_sufficient AND replay_closure_sufficient"},
        {"from": "VERIFY_PENDING", "to": "DECIDED_DEFER_NEAR", "guard": "bounded_residual AND continuation_seed_present"},
        {"from": "VERIFY_PENDING", "to": "DECIDED_DEFER_AMBIG", "guard": "underdetermined_conflict AND continuation_seed_present"},
        {"from": "VERIFY_PENDING", "to": "DECIDED_QUARANTINE", "guard": "hard_contradiction OR replay_divergence OR policy_breach"},
        {"from": "GOVERNANCE_PENDING", "to": "DECIDED_COMMIT", "guard": "governance_approval_true AND ledger_appendable AND continuation_seed_present"},
        {"from": "GOVERNANCE_PENDING", "to": "DECIDED_REFUSE", "guard": "governance_approval_false AND continuation_seed_present"},
    ]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK",
        "docs_gate_status": docs_gate_status(),
        "id": "joint-atlas.merge-automaton@0.1.0",
        "version": "0.1.0",
        "status": "derived-local-first",
        "merge_states": [state.value for state in MergeState],
        "merge_destinations": [destination.value for destination in MergeDestination],
        "terminal_destination_map": {
            state.value: destination_for_terminal_state(state).value
            for state in MergeState
            if destination_for_terminal_state(state) is not None
        },
        "transition_graph": transitions,
        "artifact_requirements": {state.value: emit_required_artifacts(state) for state in MergeState},
        "witness_basis": list(WITNESS_BASIS),
        "fixture_case_count": len(fixtures),
        "next_seed": NEXT_SEED,
    }


def build_contract_payload(fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "merge_state_enum": [state.value for state in MergeState],
        "merge_destination_enum": [destination.value for destination in MergeDestination],
        "committee_pack_fields": list(CommitteePack.__dataclass_fields__.keys()),
        "witness_pack_fields": list(WitnessPack.__dataclass_fields__.keys()),
        "replay_pack_fields": list(ReplayPack.__dataclass_fields__.keys()),
        "governance_approval_fields": list(GovernanceApproval.__dataclass_fields__.keys()),
        "continuation_seed_fields": list(ContinuationSeed.__dataclass_fields__.keys()),
        "merge_decision_fields": ["merge_id", "current_state", "chosen_destination", "required_artifacts", "residuals", "next_seed"],
        "merge_ledger_entry_fields": ["entry_id", "committee_pack_ref", "chosen_destination", "supporting_witnesses", "replay_bundle_ref", "governance_approval_ref", "dissent_refs", "continuation_seed_ref", "timestamp"],
        "fixture_cases": fixtures,
        "governance_note": "GovernanceApproval.approved is the only enforcement input in v0; quorum and weighting remain metadata-only.",
        "next_seed": NEXT_SEED,
    }


def build_ledger_payload(fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": "OK",
        "append_only_rule": {
            "append_only": True,
            "entry_ids_monotonic": True,
            "terminal_decisions_require_ledger": True,
        },
        "entry_count": len(fixtures),
        "entries": [case["ledger_entry"] for case in fixtures],
        "next_seed": NEXT_SEED,
    }


def render_manifest(automaton: Dict[str, Any]) -> str:
    transition_lines = "\n".join(
        f"- `{item['from']} -> {item['to']}`: {item['guard']}"
        for item in automaton["transition_graph"]
    )
    artifact_lines = "\n".join(
        f"- `{state}`: `{', '.join(required)}`"
        for state, required in automaton["artifact_requirements"].items()
    )
    witness_lines = "\n".join(f"- `{item}`" for item in automaton["witness_basis"])
    return f"""# JOINTATLAS MERGE BOUNDARY AUTOMATON

Date: `2026-03-13`
Truth: `{automaton['truth']}`
Docs gate: `{automaton['docs_gate_status']}`
Version: `{automaton['version']}`

## Purpose

Install the first typed collective adjudication membrane between packet transport and promotion law.

## Merge States

- `{', '.join(automaton['merge_states'])}`

## Lawful Destinations

- `{', '.join(automaton['merge_destinations'])}`

## Transition Graph

{transition_lines}

## Artifact Requirements

{artifact_lines}

## Witness Basis

{witness_lines}

## Restart Seed

`{automaton['next_seed']}`
"""


def render_ledger_markdown(ledger_payload: Dict[str, Any], fixtures: List[Dict[str, Any]]) -> str:
    rows = []
    for case in fixtures:
        entry = case["ledger_entry"]
        rows.append(
            f"| {case['case_name']} | {case['terminal_state']} | {entry['chosen_destination']} | {entry['entry_id']} | {entry['continuation_seed_ref']} |"
        )
    body = "\n".join(rows)
    return f"""# JOINTATLAS MERGE LEDGER

Date: `2026-03-13`
Truth: `{ledger_payload['truth']}`

## Ledger Rule

- append only: `{ledger_payload['append_only_rule']['append_only']}`
- entry ids monotonic: `{ledger_payload['append_only_rule']['entry_ids_monotonic']}`
- terminal decisions require ledger: `{ledger_payload['append_only_rule']['terminal_decisions_require_ledger']}`

## Non-Authoritative Fixture Ledger

| Fixture | Terminal State | Destination | Entry ID | Continuation Seed |
| --- | --- | --- | --- | --- |
{body}

## Restart Seed

`{ledger_payload['next_seed']}`
"""


def render_dashboard(verification: Dict[str, Any], automaton: Dict[str, Any], ledger: Dict[str, Any]) -> str:
    check_lines = "\n".join(f"- `{check['name']}`: `{check['truth']}`" for check in verification["checks"])
    return f"""# JOINTATLAS MERGE BOUNDARY DASHBOARD

Date: `2026-03-13`
Truth: `{verification['truth']}`
Docs gate: `{automaton['docs_gate_status']}`

## Coverage

- merge state count: `{len(automaton['merge_states'])}`
- lawful destination count: `{len(automaton['merge_destinations'])}`
- fixture cases: `{automaton['fixture_case_count']}`
- ledger entries: `{ledger['entry_count']}`

## Verification

{check_lines}

## Restart Seed

`{verification['next_seed']}`
"""


def render_receipt(verification: Dict[str, Any]) -> str:
    return f"""# 2026-03-13 JointAtlas Merge Boundary Automaton

## Outcome

- truth: `{verification['truth']}`
- docs gate: `{verification['docs_gate_status']}`
- package test truth: `{verification['package_test']['truth']}`
- next seed: `{verification['next_seed']}`

## Published Outputs

- `{relative_string(AUTOMATON_JSON_PATH)}`
- `{relative_string(CONTRACTS_JSON_PATH)}`
- `{relative_string(LEDGER_JSON_PATH)}`
- `{relative_string(VERIFICATION_JSON_PATH)}`
- `{relative_string(MANIFEST_MD_PATH)}`
- `{relative_string(LEDGER_MD_PATH)}`
- `{relative_string(DASHBOARD_MD_PATH)}`
"""


def build_verification_payload(package_test: Dict[str, Any], fixtures: List[Dict[str, Any]], atlas_records: Dict[str, Any]) -> Dict[str, Any]:
    entry_ids = [case["ledger_entry"]["entry_id"] for case in fixtures]
    checks = [
        {"name": "package_test_suite", "truth": package_test["truth"], "detail": package_test.get("command", "")},
        {"name": "fixture_case_count", "truth": "OK" if len(fixtures) == 5 else "FAIL", "detail": len(fixtures)},
        {"name": "ledger_entry_ids_monotonic", "truth": "OK" if entry_ids == sorted(entry_ids) and len(set(entry_ids)) == len(entry_ids) else "FAIL", "detail": entry_ids},
        {"name": "control_plane_grammar_mentions_adjudication", "truth": "OK" if "adjudication" in read_text(CONTROL_PLANE_GRAMMAR_PATH).lower() else "FAIL", "detail": relative_string(CONTROL_PLANE_GRAMMAR_PATH)},
        {"name": "promotion_protocol_mentions_decided_commit_gate", "truth": "OK" if "DECIDED_COMMIT" in read_text(PROMOTION_PROTOCOL_PATH) else "FAIL", "detail": relative_string(PROMOTION_PROTOCOL_PATH)},
        {"name": "hall_writeback_mentions_motion_constitution_l1", "truth": "OK" if NEXT_SEED in read_text(ACTIVE_QUEUE_PATH) and NEXT_SEED in read_text(CHANGE_FEED_PATH) else "FAIL", "detail": [relative_string(ACTIVE_QUEUE_PATH), relative_string(CHANGE_FEED_PATH)]},
        {"name": "docs_gate_still_blocked", "truth": "OK" if docs_gate_status().startswith("blocked") else "FAIL", "detail": docs_gate_status()},
        {"name": "atlas_refresh_complete", "truth": "OK" if atlas_records.get("record_count", 0) > 0 else "FAIL", "detail": atlas_records.get("record_count", 0)},
    ]
    truth = "OK" if all(check["truth"] == "OK" for check in checks) else "FAIL"
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "docs_gate_status": docs_gate_status(),
        "package_test": package_test,
        "checks": checks,
        "next_seed": NEXT_SEED,
    }


def main() -> int:
    package_test = run_test_script()
    fixtures = build_fixture_cases()

    automaton_payload = build_automaton_payload(fixtures)
    contracts_payload = build_contract_payload(fixtures)
    ledger_payload = build_ledger_payload(fixtures)

    for path, payload in (
        (AUTOMATON_JSON_PATH, automaton_payload),
        (CONTRACTS_JSON_PATH, contracts_payload),
        (LEDGER_JSON_PATH, ledger_payload),
        (AUTOMATON_JSON_MIRROR, automaton_payload),
        (CONTRACTS_JSON_MIRROR, contracts_payload),
        (LEDGER_JSON_MIRROR, ledger_payload),
    ):
        write_json(path, payload)

    write_text(MANIFEST_MD_PATH, render_manifest(automaton_payload))
    write_text(LEDGER_MD_PATH, render_ledger_markdown(ledger_payload, fixtures))

    atlas_records = refresh_corpus_atlas(
        [
            AUTOMATON_JSON_PATH,
            CONTRACTS_JSON_PATH,
            LEDGER_JSON_PATH,
            AUTOMATON_JSON_MIRROR,
            CONTRACTS_JSON_MIRROR,
            LEDGER_JSON_MIRROR,
            MANIFEST_MD_PATH,
            LEDGER_MD_PATH,
            CONTROL_PLANE_GRAMMAR_PATH,
            PROMOTION_PROTOCOL_PATH,
            ACTIVE_QUEUE_PATH,
            CHANGE_FEED_PATH,
            GUILDMASTER_README_PATH,
        ]
    )

    verification_payload = build_verification_payload(package_test, fixtures, atlas_records)
    write_json(VERIFICATION_JSON_PATH, verification_payload)
    write_json(VERIFICATION_JSON_MIRROR, verification_payload)
    write_text(DASHBOARD_MD_PATH, render_dashboard(verification_payload, automaton_payload, ledger_payload))
    write_text(RECEIPT_MD_PATH, render_receipt(verification_payload))

    refresh_corpus_atlas([VERIFICATION_JSON_PATH, VERIFICATION_JSON_MIRROR, DASHBOARD_MD_PATH, RECEIPT_MD_PATH])

    print(json.dumps(verification_payload, indent=2))
    return 0 if verification_payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

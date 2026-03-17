from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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

from athenachka.contracts import MotionCandidatePacket, MotionScoreVector  # noqa: E402
from athenachka.runtime.motion_constitution import (  # noqa: E402
    MotionConstitutionL1,
    action_alphabet,
    accepted_source_kinds,
    bootstrap_motion_state,
    effective_score_vector,
    evaluate_candidate,
)
from athenachka.runtime.reward_overlay import apply_reward_steering  # noqa: E402


DERIVATION_VERSION = "2026-03-13.motion-constitution-l1.v0"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_motion_constitution_l1"
NEXT_SEED = "MotionConstitution_L1::Parameterization"
TRUTH = "NEAR"

MOTION_JSON_PATH = SELF_ACTUALIZE_ROOT / "motion_constitution_l1.json"
FIXTURES_JSON_PATH = SELF_ACTUALIZE_ROOT / "motion_constitution_l1_fixtures.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "motion_constitution_l1_verification.json"

MOTION_JSON_MIRROR = REGISTRY_ROOT / MOTION_JSON_PATH.name
FIXTURES_JSON_MIRROR = REGISTRY_ROOT / FIXTURES_JSON_PATH.name
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / VERIFICATION_JSON_PATH.name

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "MOTION_CONSTITUTION_L1.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "MOTION_CONSTITUTION_L1_DASHBOARD.md"
LEDGER_MD_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "MOTION_CONSTITUTION_L1_FIXTURE_LEDGER.md"
RECEIPT_MD_PATH = MYCELIUM_ROOT / "receipts" / "2026-03-13_motion_constitution_l1.md"

CONTROL_PLANE_GRAMMAR_PATH = MYCELIUM_ROOT / "nervous_system" / "22_control_plane_grammar.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
CHANGE_FEED_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
NEXT_SELF_PROMPT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
GUILDMASTER_README_PATH = WORKSPACE_ROOT / "GUILDMASTER" / "README.md"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
ADVENTURER_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "adventurer_quest_registry.json"
MERGE_AUTOMATON_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_automaton.json"
MERGE_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "jointatlas_merge_ledger.json"
AGENT_PROGRESS_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "agent_progress_registry.json"
TEST_SCRIPT_PATH = WORKSPACE_ROOT / "NERUAL NETWORK" / "TEST SUITES" / "verify_motion_constitution_l1.py"


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


def find_motion_manuscript_path() -> Path:
    matches = sorted((SELF_ACTUALIZE_ROOT / "manuscript_sections").glob("*motion_constitution*"))
    if not matches:
        raise FileNotFoundError("Could not locate the MotionConstitution_L1 manuscript section.")
    return matches[0]


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(read_text(path))


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


def build_score_vector(**overrides: float) -> MotionScoreVector:
    base = {
        "closure_gain": 1.0,
        "heart_need": 0.9,
        "replay_readiness": 0.8,
        "integration_yield": 1.0,
        "organ_adjacency": 0.8,
        "seed_value": 0.7,
        "cost": 0.5,
        "replay_cost": 0.3,
        "risk": 0.3,
        "failure_debt": 0.2,
        "branch_burden": 0.2,
        "contradiction_heat": 0.1,
        "pressure_gradient": 0.4,
        "truth_readiness": 0.8,
    }
    base.update(overrides)
    return MotionScoreVector(**base)


def build_fixture_candidate(
    candidate_id: str,
    *,
    source_kind: str = "quest_board",
    blockers: List[str] | None = None,
    dependencies: List[str] | None = None,
    witness_refs: List[str] | None = None,
    replay_refs: List[str] | None = None,
    committee_refs: List[str] | None = None,
    continuation_seed: str = NEXT_SEED,
    current_family: str = "jointatlas",
    score_vector: MotionScoreVector | None = None,
) -> MotionCandidatePacket:
    return MotionCandidatePacket(
        candidate_id=candidate_id,
        source_kind=source_kind,
        source_ref=f"fixture::{candidate_id}",
        source_organ="Fixture",
        target_organ="Runtime",
        current_family=current_family,
        truth_burden="NEAR",
        expected_packet_type="QuestPacket",
        continuation_seed=continuation_seed,
        dependencies=list(dependencies or []),
        blockers=list(blockers or []),
        witness_refs=list(witness_refs if witness_refs is not None else ["WIT-001"]),
        replay_refs=list(replay_refs if replay_refs is not None else ["RPL-001"]),
        committee_refs=list(committee_refs if committee_refs is not None else []),
        score_vector=score_vector or build_score_vector(),
        note="Non-authoritative fixture case.",
    )


def build_fixture_cases() -> List[Dict[str, Any]]:
    state = bootstrap_motion_state(
        docs_gate_status=docs_gate_status(),
        activation_threshold=1.1,
    )
    specs = [
        ("ACTIVATE_NOW", build_fixture_candidate("fixture-activate")),
        (
            "HOLD",
            build_fixture_candidate(
                "fixture-hold",
                score_vector=build_score_vector(
                    closure_gain=0.1,
                    heart_need=0.1,
                    replay_readiness=0.7,
                    integration_yield=0.1,
                    organ_adjacency=0.1,
                    seed_value=0.1,
                    cost=1.7,
                    replay_cost=1.0,
                    risk=1.0,
                    failure_debt=0.8,
                    branch_burden=0.8,
                    contradiction_heat=0.2,
                    pressure_gradient=0.0,
                ),
            ),
        ),
        ("REQUEST_WITNESSES", build_fixture_candidate("fixture-witness", witness_refs=[])),
        (
            "REQUEST_HELP",
            build_fixture_candidate(
                "fixture-help",
                blockers=["external_dependency"],
                dependencies=["dep:missing"],
            ),
        ),
        ("REPLAY_FIRST", build_fixture_candidate("fixture-replay", replay_refs=[])),
        ("QUARANTINE", build_fixture_candidate("fixture-quarantine", blockers=["policy_breach"])),
        (
            "COMPRESS_TO_SEED",
            build_fixture_candidate("fixture-compress", blockers=["forward_circulation_blocked"]),
        ),
        (
            "ESCALATE_TO_COMMITTEE",
            build_fixture_candidate(
                "fixture-committee",
                blockers=["committee_pending_conflict"],
                committee_refs=["pending:committee"],
            ),
        ),
        (
            "REFUSE_INADMISSIBLE",
            build_fixture_candidate("fixture-refuse", source_kind="inadmissible_source"),
        ),
    ]

    cases: List[Dict[str, Any]] = []
    for expected_action, candidate in specs:
        decision, receipt, state = evaluate_candidate(candidate, state, activation_threshold=1.1)
        cases.append(
            {
                "fixture_id": candidate.candidate_id,
                "expected_action": expected_action,
                "candidate": candidate.to_dict(),
                "decision": decision.to_dict(),
                "receipt": receipt.to_dict(),
            }
        )
    return cases


def build_motion_state() -> MotionConstitutionL1:
    state = bootstrap_motion_state(
        docs_gate_status=docs_gate_status(),
        activation_threshold=1.1,
    )
    state.route_graph["resolved_dependencies"] = [
        "helical_runner_contract.json",
        "jointatlas_merge_ledger.json",
    ]
    state.route_graph["current_fronts"] = ["Q42", "TQ04", "FRONT-JOINTATLAS-MERGE-BOUNDARY-AUTOMATON"]
    state.pressure_field["active_families"] = ["QSHRINK", "jointatlas-merge"]
    state.pressure_field["committee_pending_families"] = ["QSHRINK"]
    state.reward_profiles = load_reward_profiles()
    return MotionConstitutionL1(state=state, activation_threshold=1.1)


def load_reward_profiles() -> Dict[str, Any]:
    if not AGENT_PROGRESS_REGISTRY_PATH.exists():
        return {}
    payload = load_json(AGENT_PROGRESS_REGISTRY_PATH)
    return payload.get("reward_steering_profiles", {})


def build_local_candidates() -> List[MotionCandidatePacket]:
    registry = load_json(ADVENTURER_REGISTRY_PATH)
    merge_ledger = load_json(MERGE_LEDGER_PATH)

    q42_record = next(record for record in registry["quest_records"] if record["quest_id"] == "Q42")
    q46_record = next(record for record in registry["quest_records"] if record["quest_id"] == "Q46")
    q02_record = next(record for record in registry["quest_records"] if record["quest_id"] == "Q02")
    merge_entry = merge_ledger["entries"][0]

    return [
        MotionCandidatePacket(
            candidate_id="MC-QUEST-Q42",
            agent_id="floating-agent-01",
            source_kind="quest_board",
            source_ref=q42_record["quest_id"],
            source_organ="GuildHall",
            target_organ="Runtime",
            current_family="QSHRINK",
            truth_burden="NEAR",
            expected_packet_type="QuestPacket",
            continuation_seed=q42_record["restart_seed"],
            dependencies=["q42.live.bundle"],
            blockers=[],
            witness_refs=[
                relative_string(QUEST_BOARD_PATH),
                "self_actualize/qshrink_connectivity_fractal.json",
            ],
            replay_refs=["self_actualize/helical_runner_contract.json"],
            committee_refs=[],
            score_vector=build_score_vector(
                closure_gain=0.7,
                heart_need=0.8,
                replay_readiness=0.9,
                integration_yield=0.7,
                organ_adjacency=1.0,
                seed_value=0.4,
                cost=0.6,
                replay_cost=0.2,
                risk=0.3,
                failure_debt=0.2,
                branch_burden=0.7,
                contradiction_heat=0.2,
                pressure_gradient=0.3,
                truth_readiness=0.8,
            ),
            note="Derived from the live Hall quest without displacing the active corridor lane.",
        ),
        MotionCandidatePacket(
            candidate_id="MC-AGENT-Q46",
            agent_id="floating-agent-02",
            source_kind="agent_registry",
            source_ref=f"{q46_record['owner']}::{q46_record['quest_id']}",
            source_organ="AdventurerRegistry",
            target_organ="Helix",
            current_family="ATHENACHKA",
            truth_burden="NEAR",
            expected_packet_type="QuestPacket",
            continuation_seed=q46_record["restart_seed"],
            dependencies=[],
            blockers=[],
            witness_refs=[relative_string(ADVENTURER_REGISTRY_PATH)],
            replay_refs=["self_actualize/athenachka_organism_v0_wave_proof.json"],
            committee_refs=[],
            score_vector=build_score_vector(
                closure_gain=0.5,
                heart_need=0.4,
                replay_readiness=0.7,
                integration_yield=0.6,
                organ_adjacency=0.6,
                seed_value=0.7,
                cost=0.8,
                replay_cost=0.4,
                risk=0.5,
                failure_debt=0.4,
                branch_burden=0.8,
                contradiction_heat=0.2,
                pressure_gradient=0.2,
                truth_readiness=0.8,
            ),
            note="Derived from the live agent registry as a separate reserve frontier.",
        ),
        MotionCandidatePacket(
            candidate_id="MC-QUEST-Q02",
            agent_id="DOCS-GATE-01",
            source_kind="quest_board",
            source_ref=q02_record["quest_id"],
            source_organ="GuildHall",
            target_organ="TradingBot",
            current_family="TradingBot",
            truth_burden="OK",
            expected_packet_type="QuestPacket",
            continuation_seed="Q02::OAuth-Reopen",
            dependencies=["docs.oauth"],
            blockers=["external_dependency"],
            witness_refs=[relative_string(QUEST_BOARD_PATH), relative_string(DOCS_GATE_PATH)],
            replay_refs=["self_actualize/live_docs_gate_status.md"],
            committee_refs=[],
            score_vector=build_score_vector(
                closure_gain=0.4,
                heart_need=0.8,
                replay_readiness=0.7,
                integration_yield=0.4,
                organ_adjacency=0.5,
                seed_value=0.6,
                cost=1.1,
                replay_cost=0.6,
                risk=0.8,
                failure_debt=0.9,
                branch_burden=0.4,
                contradiction_heat=0.2,
                pressure_gradient=0.9,
                truth_readiness=0.9,
            ),
            note="Derived from the blocked Docs-gate quest; kept external in v0.",
        ),
        MotionCandidatePacket(
            candidate_id="MC-COMMITTEE-MERGE-SUCCESSOR",
            agent_id="A2",
            source_kind="committee_output",
            source_ref=merge_entry["committee_pack_ref"],
            source_organ="Collective",
            target_organ="ControlPlane",
            current_family="jointatlas-merge",
            truth_burden="OK",
            expected_packet_type="CommitteePack",
            continuation_seed="MotionConstitution_L1",
            dependencies=[],
            blockers=[],
            witness_refs=[
                relative_string(MERGE_AUTOMATON_PATH),
                relative_string(MERGE_LEDGER_PATH),
            ],
            replay_refs=[relative_string(MERGE_LEDGER_PATH)],
            committee_refs=[merge_entry["committee_pack_ref"]],
            score_vector=build_score_vector(
                closure_gain=1.4,
                heart_need=1.0,
                replay_readiness=1.0,
                integration_yield=1.2,
                organ_adjacency=1.1,
                seed_value=1.2,
                cost=0.3,
                replay_cost=0.2,
                risk=0.2,
                failure_debt=0.1,
                branch_burden=0.2,
                contradiction_heat=0.0,
                pressure_gradient=0.8,
                truth_readiness=1.0,
            ),
            note="Derived from the landed merge boundary successor seed.",
        ),
        MotionCandidatePacket(
            candidate_id="MC-SEED-MERGE-FRONT",
            agent_id="A2",
            source_kind="continuation_seed",
            source_ref="FRONT-JOINTATLAS-MERGE-BOUNDARY-AUTOMATON",
            source_organ="ActiveQueue",
            target_organ="ControlPlane",
            current_family="jointatlas-merge",
            truth_burden="NEAR",
            expected_packet_type="ContinuationSeed",
            continuation_seed="MotionConstitution_L1",
            dependencies=[],
            blockers=[],
            witness_refs=[relative_string(ACTIVE_QUEUE_PATH)],
            replay_refs=[relative_string(MERGE_AUTOMATON_PATH)],
            committee_refs=[],
            score_vector=build_score_vector(
                closure_gain=1.2,
                heart_need=1.0,
                replay_readiness=0.9,
                integration_yield=1.1,
                organ_adjacency=1.0,
                seed_value=1.1,
                cost=0.3,
                replay_cost=0.2,
                risk=0.2,
                failure_debt=0.1,
                branch_burden=0.2,
                contradiction_heat=0.0,
                pressure_gradient=0.7,
                truth_readiness=0.8,
            ),
            note="Derived from the promoted merge front in the active queue.",
        ),
        MotionCandidatePacket(
            candidate_id="MC-SEED-NEXT-SELF-PROMPT",
            agent_id="floating-agent-05",
            source_kind="continuation_seed",
            source_ref="NEXT_SELF_PROMPT",
            source_organ="RestartSurface",
            target_organ="Hall",
            current_family="QSHRINK",
            truth_burden="NEAR",
            expected_packet_type="ContinuationSeed",
            continuation_seed="Q42::QS64-20-Carried",
            dependencies=[],
            blockers=[],
            witness_refs=[relative_string(NEXT_SELF_PROMPT_PATH)],
            replay_refs=[relative_string(ACTIVE_QUEUE_PATH)],
            committee_refs=[],
            score_vector=build_score_vector(
                closure_gain=0.4,
                heart_need=0.6,
                replay_readiness=0.8,
                integration_yield=0.4,
                organ_adjacency=0.8,
                seed_value=0.6,
                cost=0.7,
                replay_cost=0.2,
                risk=0.3,
                failure_debt=0.2,
                branch_burden=1.1,
                contradiction_heat=0.1,
                pressure_gradient=0.4,
                truth_readiness=0.8,
            ),
            note="Derived from the live restart prompt and kept separate from the current Hall lane.",
        ),
    ]


def evaluate_local_candidates() -> List[Dict[str, Any]]:
    engine = build_motion_state()
    results: List[Dict[str, Any]] = []
    for candidate in build_local_candidates():
        adjusted_vector = effective_score_vector(candidate, engine.state)
        steering_profile = engine.state.reward_profiles.get(candidate.agent_id, {}) if candidate.agent_id else {}
        _, steering_meta = apply_reward_steering(candidate.score_vector, steering_profile)
        decision, receipt = engine.evaluate_candidate(candidate)
        results.append(
            {
                "candidate": candidate.to_dict(),
                "effective_score_vector": adjusted_vector.to_dict(),
                "reward_steering": {
                    "agent_id": candidate.agent_id,
                    "profile": steering_profile,
                    "applied": steering_meta.get("applied", False),
                    "rules": steering_meta.get("rules", []),
                },
                "decision": decision.to_dict(),
                "receipt": receipt.to_dict(),
            }
        )
    results.sort(
        key=lambda item: item["decision"]["constitutional_score"],
        reverse=True,
    )
    return results


def build_motion_payload(
    manuscript_path: Path,
    evaluated_candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    witness_basis = [
        relative_string(manuscript_path),
        "Athena FLEET\\FLEET_MYCELIUM_NETWORK\\MIRRORS\\LOCAL\\F09_git_brain.md",
        relative_string(MERGE_AUTOMATON_PATH),
        relative_string(MERGE_LEDGER_PATH),
        relative_string(CONTROL_PLANE_GRAMMAR_PATH),
        relative_string(ACTIVE_QUEUE_PATH),
        relative_string(ADVENTURER_REGISTRY_PATH),
    ]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": TRUTH,
        "docs_gate_status": docs_gate_status(),
        "status": "derived-local-first",
        "constitutional_membrane": ["AppA", "AppI", "AppM"],
        "brainstem_state": {
            "G": "route graph and addressable memory",
            "Pi": "pressure field",
            "Omega": "legality projector",
            "I": "immune state",
            "R": "replay and witness memory",
        },
        "accepted_source_kinds": list(accepted_source_kinds()),
        "action_alphabet": list(action_alphabet()),
        "automaton": [
            "OBSERVE",
            "SCORE",
            "GATE",
            "ACT/RECEIPT",
            "REPLAY_STORE",
            "SEED",
        ],
        "scoring_formula": "((closure_gain + heart_need + replay_readiness + integration_yield + organ_adjacency + seed_value) * (1 + 0.5 * pressure_gradient)) / (1 + cost + replay_cost + risk + failure_debt + branch_burden + contradiction_heat)",
        "gating_note": "truth_readiness remains a gate variable and does not enter the ranking scalar",
        "hysteresis_rule": {
            "refusal_requires_new_witness_or_replay": True,
            "quarantine_requires_new_immune_or_replay": True,
            "duplicate_nearby_candidates_raise_branch_burden": True,
            "committee_pending_conflicts_suppress_activation": True,
        },
        "local_candidate_count": len(evaluated_candidates),
        "evaluated_candidates": evaluated_candidates,
        "top_candidate": evaluated_candidates[0] if evaluated_candidates else None,
        "witness_basis": witness_basis,
        "next_seed": NEXT_SEED,
    }


def build_fixtures_payload(fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": TRUTH,
        "fixture_count": len(fixtures),
        "fixtures_are_non_authoritative": True,
        "cases": fixtures,
        "next_seed": NEXT_SEED,
    }


def build_verification_payload(
    test_result: Dict[str, Any],
    motion_payload: Dict[str, Any],
    fixtures_payload: Dict[str, Any],
    atlas: Dict[str, Any],
) -> Dict[str, Any]:
    control_plane_text = read_text(CONTROL_PLANE_GRAMMAR_PATH)
    active_queue_text = read_text(ACTIVE_QUEUE_PATH)
    change_feed_text = read_text(CHANGE_FEED_PATH)
    guildmaster_text = read_text(GUILDMASTER_README_PATH)
    quest_board_text = read_text(QUEST_BOARD_PATH)
    next_self_prompt_text = read_text(NEXT_SELF_PROMPT_PATH)

    atlas_paths = {
        relative_string(MOTION_JSON_PATH),
        relative_string(FIXTURES_JSON_PATH),
        relative_string(VERIFICATION_JSON_PATH),
        relative_string(MANIFEST_MD_PATH),
        relative_string(DASHBOARD_MD_PATH),
        relative_string(LEDGER_MD_PATH),
        relative_string(RECEIPT_MD_PATH),
    }
    atlas_indexed = {
        record.get("relative_path")
        for record in atlas.get("records", [])
        if record.get("relative_path") in atlas_paths
    }
    fixture_actions = {case["decision"]["action"] for case in fixtures_payload["cases"]}

    checks = {
        "package_test_suite": test_result["truth"] == "OK",
        "all_actions_covered": fixture_actions == set(action_alphabet()),
        "fixture_case_count_is_9": fixtures_payload["fixture_count"] == 9,
        "gate_precedence_verified": test_result.get("report", {}).get("gate_precedence") is not None,
        "hysteresis_verified": test_result.get("report", {}).get("hysteresis") is not None,
        "control_plane_mentions_selection_membrane": "MotionConstitution_L1" in control_plane_text,
        "active_queue_has_motion_front": "FRONT-JOINTATLAS-MOTION-CONSTITUTION-L1" in active_queue_text,
        "change_feed_mentions_motion": "MotionConstitution_L1" in change_feed_text,
        "guildmaster_mentions_motion": "MotionConstitution_L1" in guildmaster_text,
        "q42_lane_preserved": "Quest Q42" in quest_board_text and "Q42" in next_self_prompt_text,
        "docs_gate_still_blocked": motion_payload["docs_gate_status"] == "blocked-by-missing-credentials",
        "atlas_refresh_complete": atlas_paths == atlas_indexed,
    }
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "truth": TRUTH if all(checks.values()) else "FAIL",
        "docs_gate_status": motion_payload["docs_gate_status"],
        "checks": checks,
        "test_result": test_result,
        "local_candidate_count": motion_payload["local_candidate_count"],
        "fixture_case_count": fixtures_payload["fixture_count"],
        "top_candidate_id": motion_payload["top_candidate"]["candidate"]["candidate_id"]
        if motion_payload["top_candidate"]
        else None,
        "next_seed": NEXT_SEED,
    }


def render_manifest(motion_payload: Dict[str, Any]) -> str:
    candidate_lines = "\n".join(
        f"- `{item['candidate']['candidate_id']}` `{item['candidate']['source_kind']}` -> `{item['decision']['action']}` (`{item['decision']['constitutional_score']:.3f}`)"
        for item in motion_payload["evaluated_candidates"]
    )
    witness_lines = "\n".join(f"- `{item}`" for item in motion_payload["witness_basis"])
    return f"""# MOTION CONSTITUTION L1

Date: `2026-03-13`
Truth: `{motion_payload['truth']}`
Docs gate: `{motion_payload['docs_gate_status']}`
Status: `{motion_payload['status']}`

## Purpose

Promote the written `MotionConstitution_L1` law into a local-first executable action-selection chamber.

## Constitutional Membrane

- `{', '.join(motion_payload['constitutional_membrane'])}`

## Accepted Source Kinds

- `{', '.join(motion_payload['accepted_source_kinds'])}`

## Action Alphabet

- `{', '.join(motion_payload['action_alphabet'])}`

## Automaton

- `{ ' -> '.join(motion_payload['automaton']) }`

## Score Law

`{motion_payload['scoring_formula']}`

## Local Candidate Results

{candidate_lines}

## Witness Basis

{witness_lines}

## Restart Seed

`{motion_payload['next_seed']}`
"""


def render_dashboard(motion_payload: Dict[str, Any], verification_payload: Dict[str, Any]) -> str:
    rows = []
    for item in motion_payload["evaluated_candidates"]:
        rows.append(
            "| "
            + " | ".join(
                [
                    item["candidate"]["candidate_id"],
                    item["candidate"]["source_kind"],
                    item["decision"]["action"],
                    f"{item['decision']['constitutional_score']:.3f}",
                    item["candidate"]["current_family"],
                ]
            )
            + " |"
        )
    table = "\n".join(
        [
            "| Candidate | Source | Action | Score | Family |",
            "| --- | --- | --- | --- | --- |",
            *rows,
        ]
    )
    return f"""# MOTION CONSTITUTION L1 DASHBOARD

Date: `2026-03-13`
Truth: `{motion_payload['truth']}`
Docs gate: `{motion_payload['docs_gate_status']}`
Verification: `{verification_payload['truth']}`

## Top Candidate

- `{motion_payload['top_candidate']['candidate']['candidate_id']}` -> `{motion_payload['top_candidate']['decision']['action']}`

## Local Candidate Table

{table}

## Verification Highlights

- package test suite: `{verification_payload['checks'].get('package_test_suite', False)}`
- all actions covered: `{verification_payload['checks'].get('all_actions_covered', False)}`
- atlas refreshed: `{verification_payload['checks'].get('atlas_refresh_complete', False)}`
- Q42 lane preserved: `{verification_payload['checks'].get('q42_lane_preserved', False)}`

## Restart Seed

`{motion_payload['next_seed']}`
"""


def render_fixture_ledger(fixtures_payload: Dict[str, Any]) -> str:
    rows = []
    for case in fixtures_payload["cases"]:
        rows.append(
            "| "
            + " | ".join(
                [
                    case["fixture_id"],
                    case["candidate"]["source_kind"],
                    case["expected_action"],
                    case["decision"]["action"],
                    f"{case['decision']['constitutional_score']:.3f}",
                ]
            )
            + " |"
        )
    table = "\n".join(
        [
            "| Fixture | Source | Expected | Actual | Score |",
            "| --- | --- | --- | --- | --- |",
            *rows,
        ]
    )
    return f"""# MOTION CONSTITUTION L1 FIXTURE LEDGER

Date: `2026-03-13`
Truth: `{fixtures_payload['truth']}`

## Rule

These cases are non-authoritative fixture proofs for the v0 action alphabet.

## Fixture Table

{table}

## Restart Seed

`{fixtures_payload['next_seed']}`
"""


def render_receipt(
    motion_payload: Dict[str, Any],
    verification_payload: Dict[str, Any],
) -> str:
    return f"""# 2026-03-13 MOTION CONSTITUTION L1

Truth: `{motion_payload['truth']}`
Docs gate: `{motion_payload['docs_gate_status']}`

## Landed

- package-level motion contracts and offline evaluator
- local-first machine outputs, registry mirrors, manifest, dashboard, fixture ledger, and receipt
- a separate promoted control-plane frontier for `MotionConstitution_L1`

## Verified

- package test suite: `{verification_payload['checks'].get('package_test_suite', False)}`
- action alphabet coverage: `{verification_payload['checks'].get('all_actions_covered', False)}`
- hysteresis proof: `{verification_payload['checks'].get('hysteresis_verified', False)}`
- atlas refresh: `{verification_payload['checks'].get('atlas_refresh_complete', False)}`
- live Q42 lane preserved: `{verification_payload['checks'].get('q42_lane_preserved', False)}`

## Restart Seed

`{motion_payload['next_seed']}`
"""


def main() -> int:
    manuscript_path = find_motion_manuscript_path()
    test_result = run_test_script()
    fixtures_payload = build_fixtures_payload(build_fixture_cases())
    evaluated_candidates = evaluate_local_candidates()
    motion_payload = build_motion_payload(manuscript_path, evaluated_candidates)

    write_json(MOTION_JSON_PATH, motion_payload)
    write_json(FIXTURES_JSON_PATH, fixtures_payload)
    write_json(MOTION_JSON_MIRROR, motion_payload)
    write_json(FIXTURES_JSON_MIRROR, fixtures_payload)

    placeholder_verification = {
        "generated_at": utc_now(),
        "truth": TRUTH,
        "docs_gate_status": motion_payload["docs_gate_status"],
        "checks": {},
        "next_seed": NEXT_SEED,
    }
    write_json(VERIFICATION_JSON_PATH, placeholder_verification)
    write_json(VERIFICATION_JSON_MIRROR, placeholder_verification)

    write_text(MANIFEST_MD_PATH, render_manifest(motion_payload))
    write_text(DASHBOARD_MD_PATH, render_dashboard(motion_payload, placeholder_verification))
    write_text(LEDGER_MD_PATH, render_fixture_ledger(fixtures_payload))
    write_text(RECEIPT_MD_PATH, render_receipt(motion_payload, placeholder_verification))

    atlas = refresh_corpus_atlas(
        [
            MOTION_JSON_PATH,
            FIXTURES_JSON_PATH,
            VERIFICATION_JSON_PATH,
            MOTION_JSON_MIRROR,
            FIXTURES_JSON_MIRROR,
            VERIFICATION_JSON_MIRROR,
            MANIFEST_MD_PATH,
            DASHBOARD_MD_PATH,
            LEDGER_MD_PATH,
            RECEIPT_MD_PATH,
            CONTROL_PLANE_GRAMMAR_PATH,
            ACTIVE_QUEUE_PATH,
            CHANGE_FEED_PATH,
            GUILDMASTER_README_PATH,
        ]
    )

    verification_payload = build_verification_payload(
        test_result=test_result,
        motion_payload=motion_payload,
        fixtures_payload=fixtures_payload,
        atlas=atlas,
    )
    write_json(VERIFICATION_JSON_PATH, verification_payload)
    write_json(VERIFICATION_JSON_MIRROR, verification_payload)
    write_text(DASHBOARD_MD_PATH, render_dashboard(motion_payload, verification_payload))
    write_text(RECEIPT_MD_PATH, render_receipt(motion_payload, verification_payload))

    refresh_corpus_atlas(
        [
            VERIFICATION_JSON_PATH,
            VERIFICATION_JSON_MIRROR,
            DASHBOARD_MD_PATH,
            RECEIPT_MD_PATH,
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

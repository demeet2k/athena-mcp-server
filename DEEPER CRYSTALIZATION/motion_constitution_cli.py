#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from canonical_manuscript_audit import (
    AUDIT_RECEIPT_PATH,
    audit_manuscript,
    update_full_stack_manifest as update_spine_manifest,
    update_readme as update_spine_readme,
)
from canonical_manuscript_builder import DEFAULT_MANIFEST, build_manuscript_volumes
from nervous_system_core import slugify, utc_now, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
MOTION_ROOT = ACTIVE_ROOT / "15_MOTION_CONSTITUTION"
README_PATH = ACTIVE_ROOT / "README.md"
FULL_STACK_MANIFEST_PATH = ACTIVE_ROOT / "06_RUNTIME" / "12_full_stack_manifest.json"
MANIFEST_PATH = ACTIVE_ROOT / "06_RUNTIME" / "16_motion_constitution_manifest.json"
LIVE_DOCS_GATE_PATH = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"
SECTIONS_DIR = PROJECT_ROOT.parent / "self_actualize" / "manuscript_sections"
SPINE_OUTPUT_PATH = PROJECT_ROOT.parent / "self_actualize" / "VOID_MANUSCRIPT_MASTER.md"
SUPPLEMENTS_OUTPUT_PATH = PROJECT_ROOT.parent / "self_actualize" / "VOID_MANUSCRIPT_SUPPLEMENTS.md"

MOTION_SPEC_MD = MOTION_ROOT / "00_motion_constitution_l1.md"
MOTION_SPEC_JSON = MOTION_ROOT / "01_motion_constitution_l1.json"
SCORE_LAW_MD = MOTION_ROOT / "02_score_law.md"
ACTION_RULES_MD = MOTION_ROOT / "03_action_alphabet_and_overrides.md"
HYSTERESIS_MD = MOTION_ROOT / "04_hysteresis_inhibition.md"
ROUTE_TABLE_MD = MOTION_ROOT / "05_organ_current_route_table_v0.md"
ROUTE_TABLE_JSON = MOTION_ROOT / "06_organ_current_route_table_v0.json"
CANDIDATE_WORLD_SCHEMA_PATH = MOTION_ROOT / "07_candidate_world_schema.json"
ALL_ACTION_FIXTURE_PATH = MOTION_ROOT / "08_action_fixture_all_classes.json"
HYSTERESIS_STATE_PATH = MOTION_ROOT / "09_hysteresis_state.json"
MOTION_README_PATH = MOTION_ROOT / "README.md"

MOTION_SUPPLEMENT_PATH = SECTIONS_DIR / "023_motion_constitution_l1_action_selection_engine.md"
ROUTE_SUPPLEMENT_PATH = SECTIONS_DIR / "024_organ_current_route_table_v0.md"

TRUTH_STATE = "NEAR-derived"
STATUS = "derived-near"
DEFAULT_BETA = 0.5
ACTIVATE_THRESHOLD = 0.12
TRUTH_THRESHOLD = 0.55
REPLAY_THRESHOLD = 0.55
BRANCH_LIMIT = 0.75
ALLOWED_SOURCE_QUEUES = [
    "QuestBoard",
    "AgentRegistry",
    "Committee outputs",
    "Immune scheduler outputs",
    "Continuation seeds",
]
SCORE_AXES = [
    "truth_readiness",
    "integration_yield",
    "replay_cost",
    "contradiction_heat",
    "pressure_gradient",
    "organ_adjacency",
    "branch_burden",
    "seed_value",
    "closure_gain",
    "heart_need",
    "replay_readiness",
    "failure_debt",
    "risk",
    "cost",
]
ACTION_ALPHABET = [
    "ACTIVATE_NOW",
    "HOLD",
    "REQUEST_WITNESSES",
    "REQUEST_HELP",
    "REPLAY_FIRST",
    "QUARANTINE",
    "COMPRESS_TO_SEED",
    "ESCALATE_TO_COMMITTEE",
    "REFUSE_INADMISSIBLE",
]
DEFAULT_WEIGHTS = {axis: 1.0 for axis in SCORE_AXES}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and exercise MotionConstitution_L1 as an offline action-selection layer."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Compile the motion layer, supplements, and runtime manifest.")
    build_parser.add_argument("--json", action="store_true", dest="as_json")

    score_parser = subparsers.add_parser("score", help="Score a candidate world and choose lawful actions.")
    score_parser.add_argument("candidate_world")
    score_parser.add_argument("--json", action="store_true", dest="as_json")

    simulate_parser = subparsers.add_parser("simulate", help="Run the minimal motion automaton over a candidate world.")
    simulate_parser.add_argument("candidate_world")
    simulate_parser.add_argument("--json", action="store_true", dest="as_json")

    route_parser = subparsers.add_parser("route-table", help="Emit OrganCurrentRouteTable.v0.")
    route_parser.add_argument("--json", action="store_true", dest="as_json")

    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def replace_or_append_section(text: str, heading: str, body_lines: list[str]) -> str:
    block = "\n".join([heading, "", *body_lines]).rstrip()
    pattern = re.compile(rf"\n{re.escape(heading)}\n(?:.*?)(?=\n## |\Z)", re.S)
    if heading in text:
        return pattern.sub("\n" + block + "\n", text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def ensure_line_after_anchor(text: str, anchor: str, line_to_add: str) -> str:
    if line_to_add in text:
        return text
    if anchor in text:
        return text.replace(anchor, anchor + "\n" + line_to_add, 1)
    return text.rstrip() + "\n" + line_to_add + "\n"


def live_docs_error() -> str:
    if not LIVE_DOCS_GATE_PATH.exists():
        return "Error: Missing OAuth client file: credentials.json"
    for line in LIVE_DOCS_GATE_PATH.read_text(encoding="utf-8").splitlines():
        if "Missing OAuth client file" in line:
            return line.strip()
    return "Google Docs preflight blocked."


def source_basis() -> list[dict[str, str]]:
    return [
        {
            "label": "user_packet",
            "path": "(thread packet :: MotionConstitution_L1 Dual-Track Build)",
            "truth": TRUTH_STATE,
            "role": "primary derived specification source",
        },
        {
            "label": "git_brain_mirror",
            "path": str(PROJECT_ROOT.parent / "Athena FLEET" / "GIT BRAIN.4d.md"),
            "truth": "NEAR",
            "role": "local mirror for immune architecture and governance framing",
        },
        {
            "label": "git_brain_capsule",
            "path": str(
                PROJECT_ROOT.parent
                / "Athena FLEET"
                / "FLEET_MYCELIUM_NETWORK"
                / "CAPSULES"
                / "LOCAL"
                / "F09_git_brain.md"
            ),
            "truth": "derived-local",
            "role": "local capsule witness for governance cortex and quarantine tensions",
        },
        {
            "label": "pulse_retro_weaving_mirror",
            "path": str(
                PROJECT_ROOT.parent
                / "MATH"
                / "FINAL FORM"
                / "COMPLETE TOMES"
                / "ATHENA"
                / "funtional"
                / "PULSE RETRO WEAVING.4d.md"
            ),
            "truth": "NEAR",
            "role": "local mirror for retro weaving, continuation, and successor-seed return",
        },
        {
            "label": "athena_core_contribution",
            "path": "(packet-derived; no stronger local mirror located)",
            "truth": TRUTH_STATE,
            "role": "brainstem formula O = (G, Π, Ω, I, R)",
        },
        {
            "label": "athena_fleet_contribution",
            "path": "(packet-derived; no stronger local mirror located)",
            "truth": TRUTH_STATE,
            "role": "scheduler law using closure gain, heart need, replay readiness, cost, risk, and failure debt",
        },
    ]


def motion_constitution_object() -> dict[str, Any]:
    return {
        "id": "joint-atlas.motion-constitution@0.1.0",
        "version": "0.1.0",
        "status": STATUS,
        "truth": TRUTH_STATE,
        "role": "lawful action-selection layer between governance and execution",
        "constitutional_spine": {
            "sigma": ["AppA", "AppI", "AppM"],
            "laws": [
                "no motion outside Sigma-preserving routes",
                "no activation without typed state",
                "no sharp move without witness burden known",
                "no public-grade closure without replay",
                "no contradiction deletion; only type, scope, quarantine, repair",
                "every terminal motion emits next lawful artifact or continuation seed",
            ],
        },
        "brainstem_state": {
            "formula": "O = (G, Pi, Omega, I, R)",
            "fields": {
                "G": "route graph / mycelium structure / addressable memory",
                "Pi": "pressure field / salience gradients / unfinished-work vectors",
                "Omega": "legality projector",
                "I": "immune state",
                "R": "replay/witness memory",
            },
        },
        "candidate_world": {
            "source_queues": ALLOWED_SOURCE_QUEUES,
            "candidate_unit": {
                "fields": [
                    "id",
                    "title",
                    "source_queue",
                    "role_family",
                    "source_organ",
                    "target_organ",
                    "current_family",
                    "truth_burden",
                    "packet_type_expected",
                    "continuation_seed",
                    "dependencies",
                    "blockers",
                    "axes",
                    "flags",
                ]
            },
        },
        "score_axes": SCORE_AXES,
        "action_alphabet": ACTION_ALPHABET,
        "hard_overrides": [
            "if blockers intersect quarantine or unresolved-failure classes, ACTIVATE_NOW forbidden",
            "if Omega denies, ACTIVATE_NOW forbidden",
            "if replay requirement exceeds available replay capability, ACTIVATE_NOW forbidden",
            "if truth burden exceeds carrier/agent envelope, ACTIVATE_NOW forbidden",
            "if branch burden exceeds stewardship limit, SPLIT/BRANCH forbidden unless committee-approved",
        ],
        "default_parameters": {
            "weights": DEFAULT_WEIGHTS,
            "beta": DEFAULT_BETA,
            "activate_threshold": ACTIVATE_THRESHOLD,
            "truth_threshold": TRUTH_THRESHOLD,
            "replay_threshold": REPLAY_THRESHOLD,
            "branch_limit": BRANCH_LIMIT,
        },
        "outputs": [
            "ActionClass",
            "Receipt",
            "NextSeed",
            "UpdatedPressure",
            "QueueMutation",
        ],
    }


def organ_current_route_table() -> dict[str, Any]:
    return {
        "id": "joint-atlas.organ-current-route-table@0.1.0",
        "version": "0.1.0",
        "status": STATUS,
        "truth": TRUTH_STATE,
        "organ_classes": [
            {
                "organ_id": "BrainstemChamber",
                "kind": "governance-runtime organ",
                "zone": "brainstem_internal",
                "duty": "scores, gates, and routes candidate motion",
            },
            {
                "organ_id": "QuestBoard",
                "kind": "source queue",
                "zone": "brainstem_internal",
                "duty": "holds open quest packets awaiting lawful motion",
            },
            {
                "organ_id": "AgentRegistry",
                "kind": "source queue",
                "zone": "brainstem_internal",
                "duty": "advertises role families and help envelopes",
            },
            {
                "organ_id": "CommitteeChamber",
                "kind": "governance membrane",
                "zone": "committee_internal",
                "duty": "handles stewardship, merge, and branch-limit decisions",
            },
            {
                "organ_id": "ImmuneScheduler",
                "kind": "immune organ",
                "zone": "immune_runtime",
                "duty": "surfaces quarantine and unresolved-failure pressure",
            },
            {
                "organ_id": "ReplayKernel",
                "kind": "verification organ",
                "zone": "replay_lab",
                "duty": "executes replay-first obligations and receipt verification",
            },
            {
                "organ_id": "QuarantineManifold",
                "kind": "immune containment organ",
                "zone": "quarantine_zone",
                "duty": "contains contradiction and failure classes that cannot circulate",
            },
            {
                "organ_id": "ContinuationSeedVault",
                "kind": "memory organ",
                "zone": "seed_store",
                "duty": "stores lawful continuation seeds when circulation must pause",
            },
            {
                "organ_id": "PublicCommitSurface",
                "kind": "publication membrane",
                "zone": "public_grade",
                "duty": "receives only replay-cleared closure artifacts",
            },
        ],
        "current_classes": [
            {"current_id": "governance", "meaning": "committee, role, and stewardship traffic"},
            {"current_id": "truth", "meaning": "witness, admissibility, and legality traffic"},
            {"current_id": "replay", "meaning": "verification and deterministic rerun traffic"},
            {"current_id": "immune", "meaning": "quarantine, refusal, and failure-class traffic"},
            {"current_id": "continuation", "meaning": "seed emission and successor-seed return"},
            {"current_id": "transport", "meaning": "ordinary lawful movement between organs"},
        ],
        "zone_classes": [
            {"zone_id": "brainstem_internal", "law": "scoring and gating allowed; no public closure"},
            {"zone_id": "committee_internal", "law": "collective governance required before escalation resolves"},
            {"zone_id": "replay_lab", "law": "replay obligations may execute without public promotion"},
            {"zone_id": "quarantine_zone", "law": "contained contradiction may persist; export forbidden"},
            {"zone_id": "seed_store", "law": "continuation seeds may persist while forward motion is paused"},
            {"zone_id": "public_grade", "law": "only replay-cleared closure artifacts may enter"},
        ],
        "packet_families": [
            "quest_packet",
            "witness_request",
            "help_request",
            "replay_job",
            "committee_escalation",
            "quarantine_packet",
            "continuation_seed",
            "action_receipt",
            "refusal_receipt",
        ],
        "admissible_movement_rules": [
            {
                "route": "QuestBoard -> BrainstemChamber",
                "current": "governance",
                "packet_family": "quest_packet",
                "law": "all candidate motion enters the brainstem through typed queues",
            },
            {
                "route": "AgentRegistry -> BrainstemChamber",
                "current": "governance",
                "packet_family": "help_request",
                "law": "role mismatch may be converted into lawful help requests",
            },
            {
                "route": "ImmuneScheduler -> BrainstemChamber",
                "current": "immune",
                "packet_family": "quarantine_packet",
                "law": "immune pressure may veto activation before execution",
            },
            {
                "route": "BrainstemChamber -> ReplayKernel",
                "current": "replay",
                "packet_family": "replay_job",
                "law": "replay-first obligations leave the brainstem through ReplayKernel",
            },
            {
                "route": "BrainstemChamber -> CommitteeChamber",
                "current": "governance",
                "packet_family": "committee_escalation",
                "law": "branch-limit and stewardship violations require committee routing",
            },
            {
                "route": "BrainstemChamber -> QuarantineManifold",
                "current": "immune",
                "packet_family": "quarantine_packet",
                "law": "forbidden contradiction classes are routed to containment instead of activation",
            },
            {
                "route": "BrainstemChamber -> ContinuationSeedVault",
                "current": "continuation",
                "packet_family": "continuation_seed",
                "law": "blocked motion with preserved continuation value emits a successor seed",
            },
            {
                "route": "BrainstemChamber -> PublicCommitSurface",
                "current": "transport",
                "packet_family": "action_receipt",
                "law": "public-grade closure is lawful only when replay obligations are already satisfied",
            },
            {
                "route": "ReplayKernel -> ContinuationSeedVault",
                "current": "continuation",
                "packet_family": "continuation_seed",
                "law": "verified replay may crystallize into a successor seed for the next lawful pass",
            },
        ],
        "forbidden_routes": [
            {
                "route": "QuarantineManifold -> PublicCommitSurface",
                "law": "quarantined contradiction cannot be promoted as public closure",
            },
            {
                "route": "BrainstemChamber -> PublicCommitSurface",
                "law": "forbidden when replay readiness is below threshold or Omega denies",
            },
            {
                "route": "QuestBoard -> PublicCommitSurface",
                "law": "no direct public promotion without brainstem scoring and replay",
            },
            {
                "route": "QuarantineManifold -> BrainstemChamber",
                "law": "recent quarantine may not reactivate until trust or replay improves",
            },
            {
                "route": "BrainstemChamber -> parallel_conflicting_commit",
                "law": "committee-pending items suppress parallel conflicting commits",
            },
        ],
        "committee_required_routes": [
            {
                "route": "BrainstemChamber -> CommitteeChamber",
                "trigger": "branch burden exceeds stewardship limit",
            },
            {
                "route": "BrainstemChamber -> CommitteeChamber",
                "trigger": "multi-agent merge or governance membrane required",
            },
            {
                "route": "BrainstemChamber -> CommitteeChamber",
                "trigger": "carrier envelope exceeded for current truth burden",
            },
        ],
        "seed_fallback_routes": [
            {
                "route": "BrainstemChamber -> ContinuationSeedVault",
                "trigger": "continuation value remains but lawful forward motion does not",
            },
            {
                "route": "ReplayKernel -> ContinuationSeedVault",
                "trigger": "replay clarifies the next lawful seed even if activation stays blocked",
            },
        ],
    }


def initial_hysteresis_state() -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": TRUTH_STATE,
        "recently_refused": {},
        "recently_quarantined": {},
        "committee_pending_routes": [],
        "history": [],
    }


def candidate_world_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "MotionConstitution_L1 Candidate World",
        "type": "object",
        "required": ["brainstem_state", "candidates"],
        "properties": {
            "brainstem_state": {
                "type": "object",
                "required": ["G", "Pi", "Omega", "I", "R"],
                "properties": {
                    "G": {"type": "string"},
                    "Pi": {"type": "string"},
                    "Omega": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "denied_packet_ids": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "I": {
                        "type": "object",
                        "properties": {
                            "quarantine_classes": {"type": "array", "items": {"type": "string"}},
                            "unresolved_failure_classes": {"type": "array", "items": {"type": "string"}},
                            "committee_pending_routes": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "R": {
                        "type": "object",
                        "properties": {
                            "replay_capacity": {"type": "number"},
                            "replay_memory_quality": {"type": "number"},
                        },
                    },
                },
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "weights": {"type": "object"},
                    "beta": {"type": "number"},
                },
            },
            "hysteresis_state_path": {"type": "string"},
            "candidates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "id",
                        "title",
                        "source_queue",
                        "source_organ",
                        "target_organ",
                        "current_family",
                        "packet_type_expected",
                        "axes",
                    ],
                    "properties": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "source_queue": {"type": "string", "enum": ALLOWED_SOURCE_QUEUES},
                        "role_family": {"type": "string"},
                        "source_organ": {"type": "string"},
                        "target_organ": {"type": "string"},
                        "current_family": {"type": "string"},
                        "truth_burden": {"type": "string"},
                        "packet_type_expected": {"type": "string"},
                        "continuation_seed": {"type": "string"},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "blockers": {"type": "array", "items": {"type": "string"}},
                        "blocker_classes": {"type": "array", "items": {"type": "string"}},
                        "axes": {
                            "type": "object",
                            "properties": {axis: {"type": "number"} for axis in SCORE_AXES},
                        },
                        "flags": {"type": "object"},
                    },
                },
            },
        },
    }


def all_action_fixture() -> dict[str, Any]:
    def axes(**overrides: float) -> dict[str, float]:
        base = {
            "truth_readiness": 0.8,
            "integration_yield": 0.8,
            "replay_cost": 0.2,
            "contradiction_heat": 0.1,
            "pressure_gradient": 0.5,
            "organ_adjacency": 0.8,
            "branch_burden": 0.2,
            "seed_value": 0.7,
            "closure_gain": 0.8,
            "heart_need": 0.7,
            "replay_readiness": 0.8,
            "failure_debt": 0.1,
            "risk": 0.2,
            "cost": 0.2,
        }
        base.update(overrides)
        return base

    candidates = [
        {
            "id": "Q_ACTIVATE",
            "title": "Promote a replay-ready lawful packet",
            "source_queue": "QuestBoard",
            "role_family": "governance",
            "source_organ": "QuestBoard",
            "target_organ": "BrainstemChamber",
            "current_family": "transport",
            "truth_burden": "moderate",
            "packet_type_expected": "quest_packet",
            "continuation_seed": "seed_activate",
            "dependencies": [],
            "blockers": [],
            "blocker_classes": [],
            "axes": axes(pressure_gradient=0.6),
            "flags": {},
        },
        {
            "id": "Q_HOLD",
            "title": "Keep a lawful packet in timing hold",
            "source_queue": "QuestBoard",
            "role_family": "governance",
            "source_organ": "QuestBoard",
            "target_organ": "BrainstemChamber",
            "current_family": "transport",
            "truth_burden": "moderate",
            "packet_type_expected": "quest_packet",
            "continuation_seed": "seed_hold",
            "dependencies": ["upstream_window"],
            "blockers": [],
            "blocker_classes": [],
            "axes": axes(pressure_gradient=0.3, closure_gain=0.5, heart_need=0.4),
            "flags": {"timing_not_lawful": True},
        },
        {
            "id": "Q_WITNESS",
            "title": "Require additional witnesses before motion",
            "source_queue": "QuestBoard",
            "role_family": "truth",
            "source_organ": "QuestBoard",
            "target_organ": "BrainstemChamber",
            "current_family": "truth",
            "truth_burden": "heavy",
            "packet_type_expected": "quest_packet",
            "continuation_seed": "seed_witness",
            "dependencies": [],
            "blockers": ["missing_primary_witness"],
            "blocker_classes": [],
            "axes": axes(truth_readiness=0.35, replay_readiness=0.7, seed_value=0.8),
            "flags": {"truth_burden_unsatisfied": True},
        },
        {
            "id": "Q_HELP",
            "title": "Reroute a packet to another role family",
            "source_queue": "AgentRegistry",
            "role_family": "agent-support",
            "source_organ": "AgentRegistry",
            "target_organ": "BrainstemChamber",
            "current_family": "governance",
            "truth_burden": "light",
            "packet_type_expected": "help_request",
            "continuation_seed": "seed_help",
            "dependencies": [],
            "blockers": ["role_current_mismatch"],
            "blocker_classes": [],
            "axes": axes(closure_gain=0.45, organ_adjacency=0.5, heart_need=0.5),
            "flags": {"role_mismatch": True},
        },
        {
            "id": "Q_REPLAY",
            "title": "Replay before attempting closure",
            "source_queue": "Immune scheduler outputs",
            "role_family": "replay",
            "source_organ": "ImmuneScheduler",
            "target_organ": "BrainstemChamber",
            "current_family": "replay",
            "truth_burden": "moderate",
            "packet_type_expected": "replay_job",
            "continuation_seed": "seed_replay",
            "dependencies": ["replay_capsule"],
            "blockers": ["replay_not_yet_executed"],
            "blocker_classes": [],
            "axes": axes(replay_readiness=0.25, replay_cost=0.8, closure_gain=0.75, pressure_gradient=0.7),
            "flags": {"replay_dependency_unresolved": True},
        },
        {
            "id": "Q_QUARANTINE",
            "title": "Contain a forbidden contradiction packet",
            "source_queue": "Immune scheduler outputs",
            "role_family": "immune",
            "source_organ": "ImmuneScheduler",
            "target_organ": "BrainstemChamber",
            "current_family": "immune",
            "truth_burden": "moderate",
            "packet_type_expected": "quarantine_packet",
            "continuation_seed": "seed_quarantine",
            "dependencies": [],
            "blockers": ["contradiction_heat_spike"],
            "blocker_classes": ["quarantine:contradiction", "unresolved-failure:route"],
            "axes": axes(contradiction_heat=0.95, failure_debt=0.8, risk=0.9, pressure_gradient=0.9),
            "flags": {},
        },
        {
            "id": "Q_COMPRESS",
            "title": "Compress a blocked branch into a continuation seed",
            "source_queue": "Continuation seeds",
            "role_family": "continuation",
            "source_organ": "ContinuationSeedVault",
            "target_organ": "BrainstemChamber",
            "current_family": "continuation",
            "truth_burden": "light",
            "packet_type_expected": "continuation_seed",
            "continuation_seed": "seed_compress",
            "dependencies": [],
            "blockers": ["circulation_window_closed"],
            "blocker_classes": [],
            "axes": axes(truth_readiness=0.65, seed_value=0.95, closure_gain=0.35, heart_need=0.3),
            "flags": {"circulation_blocked": True, "continuation_value_remaining": True},
        },
        {
            "id": "Q_ESCALATE",
            "title": "Escalate a stewardship-heavy branch",
            "source_queue": "Committee outputs",
            "role_family": "committee",
            "source_organ": "CommitteeChamber",
            "target_organ": "BrainstemChamber",
            "current_family": "governance",
            "truth_burden": "heavy",
            "packet_type_expected": "committee_escalation",
            "continuation_seed": "seed_escalate",
            "dependencies": [],
            "blockers": ["branch_limit"],
            "blocker_classes": [],
            "axes": axes(branch_burden=0.92, closure_gain=0.8, heart_need=0.8, seed_value=0.8),
            "flags": {"committee_required": True},
        },
        {
            "id": "Q_REFUSE",
            "title": "Refuse an inadmissible public-scope move",
            "source_queue": "QuestBoard",
            "role_family": "public",
            "source_organ": "QuestBoard",
            "target_organ": "PublicCommitSurface",
            "current_family": "transport",
            "truth_burden": "heavy",
            "packet_type_expected": "quest_packet",
            "continuation_seed": "seed_refuse",
            "dependencies": [],
            "blockers": ["omega_denied"],
            "blocker_classes": [],
            "axes": axes(truth_readiness=0.6, replay_readiness=0.6, closure_gain=0.9, heart_need=0.9),
            "flags": {"omega_denied": True, "inadmissible_scope": True},
        },
    ]

    return {
        "brainstem_state": {
            "G": "quest-board graph plus committee and replay addresses",
            "Pi": "mixed pressure field over closure, heart need, and unfinished routes",
            "Omega": {
                "status": "MIXED",
                "denied_packet_ids": ["Q_REFUSE"],
            },
            "I": {
                "quarantine_classes": ["quarantine:contradiction"],
                "unresolved_failure_classes": ["unresolved-failure:route"],
                "committee_pending_routes": [],
            },
            "R": {
                "replay_capacity": 0.7,
                "replay_memory_quality": 0.82,
            },
        },
        "parameters": {
            "weights": DEFAULT_WEIGHTS,
            "beta": DEFAULT_BETA,
        },
        "candidates": candidates,
    }


def load_hysteresis_state(path: Path | None = None) -> dict[str, Any]:
    target = path or HYSTERESIS_STATE_PATH
    if target.exists():
        return load_json(target)
    state = initial_hysteresis_state()
    write_json(target, state)
    return state


def normalize_axes(raw_axes: dict[str, Any]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for axis in SCORE_AXES:
        normalized[axis] = max(0.0, float(raw_axes.get(axis, 0.0)))
    return normalized


def route_signature(candidate: dict[str, Any]) -> str:
    return (
        f"{candidate.get('source_organ', '?')}->{candidate.get('target_organ', '?')}:"
        f"{candidate.get('current_family', '?')}:{candidate.get('packet_type_expected', '?')}"
    )


def validate_candidate_world(candidate_world: dict[str, Any]) -> None:
    if "brainstem_state" not in candidate_world or "candidates" not in candidate_world:
        raise ValueError("Candidate world must include brainstem_state and candidates.")
    for candidate in candidate_world["candidates"]:
        queue = candidate.get("source_queue")
        if queue not in ALLOWED_SOURCE_QUEUES:
            raise ValueError(f"Unsupported source_queue {queue!r}. Allowed queues: {ALLOWED_SOURCE_QUEUES}")


def base_score(axes: dict[str, float], weights: dict[str, float], beta: float) -> dict[str, float]:
    numerator = (
        axes["closure_gain"] * weights["closure_gain"]
        * axes["heart_need"] * weights["heart_need"]
        * axes["replay_readiness"] * weights["replay_readiness"]
        * axes["integration_yield"] * weights["integration_yield"]
        * axes["organ_adjacency"] * weights["organ_adjacency"]
        * axes["seed_value"] * weights["seed_value"]
    )
    denominator = (
        axes["cost"] * weights["cost"]
        + axes["replay_cost"] * weights["replay_cost"]
        + axes["risk"] * weights["risk"]
        + axes["failure_debt"] * weights["failure_debt"]
        + axes["branch_burden"] * weights["branch_burden"]
        + axes["contradiction_heat"] * weights["contradiction_heat"]
    )
    denominator = max(denominator, 1e-6)
    priority_score = numerator / denominator
    urgency_modulated_score = priority_score * (1.0 + (beta * axes["pressure_gradient"]))
    return {
        "numerator": numerator,
        "denominator": denominator,
        "priority_score": priority_score,
        "urgency_modulated_score": urgency_modulated_score,
    }


def apply_hysteresis(
    candidate: dict[str, Any],
    axes: dict[str, float],
    hysteresis_state: dict[str, Any],
    duplicate_count: int,
) -> dict[str, Any]:
    route = route_signature(candidate)
    candidate_id = candidate["id"]
    refused = hysteresis_state.get("recently_refused", {}).get(candidate_id, {})
    quarantined = hysteresis_state.get("recently_quarantined", {}).get(route, {})
    committee_pending = route in hysteresis_state.get("committee_pending_routes", [])

    refusal_count = int(refused.get("count", 0))
    if refusal_count:
        axes["truth_readiness"] = max(0.0, axes["truth_readiness"] - min(0.3, refusal_count * 0.05))

    if quarantined and not candidate.get("flags", {}).get("trust_improved", False):
        axes["replay_readiness"] = max(0.0, axes["replay_readiness"] - 0.2)
        axes["truth_readiness"] = max(0.0, axes["truth_readiness"] - 0.15)

    if duplicate_count > 1:
        axes["branch_burden"] += 0.1 * (duplicate_count - 1)

    seed_rich_witness_poor = axes["seed_value"] >= 0.8 and axes["truth_readiness"] < TRUTH_THRESHOLD

    if committee_pending:
        candidate.setdefault("flags", {})
        candidate["flags"]["conflicting_commit_pending"] = True

    return {
        "refusal_count": refusal_count,
        "recently_quarantined": bool(quarantined),
        "committee_pending": committee_pending,
        "duplicate_count": duplicate_count,
        "seed_rich_witness_poor": seed_rich_witness_poor,
    }


def lawful_actions_for_candidate(
    candidate: dict[str, Any],
    axes: dict[str, float],
    brainstem_state: dict[str, Any],
    modifiers: dict[str, Any],
) -> tuple[list[str], dict[str, bool]]:
    flags = candidate.get("flags", {})
    blocker_classes = set(candidate.get("blocker_classes", []))
    immune = brainstem_state.get("I", {})
    quarantine_classes = set(immune.get("quarantine_classes", []))
    unresolved_failure_classes = set(immune.get("unresolved_failure_classes", []))
    forbidden_intersection = bool(blocker_classes & (quarantine_classes | unresolved_failure_classes))
    omega_denied = flags.get("omega_denied", False) or candidate["id"] in brainstem_state.get("Omega", {}).get(
        "denied_packet_ids", []
    )
    inadmissible_scope = flags.get("inadmissible_scope", False)
    replay_blocked = flags.get("replay_dependency_unresolved", False) or axes["replay_readiness"] < REPLAY_THRESHOLD
    truth_unsatisfied = flags.get("truth_burden_unsatisfied", False) or axes["truth_readiness"] < TRUTH_THRESHOLD
    branch_over_limit = flags.get("branch_limit_exceeded", False) or axes["branch_burden"] > BRANCH_LIMIT
    committee_required = flags.get("committee_required", False) or flags.get("conflicting_commit_pending", False)
    role_mismatch = flags.get("role_mismatch", False)
    circulation_blocked = flags.get("circulation_blocked", False)
    continuation_value_remaining = flags.get("continuation_value_remaining", False) or axes["seed_value"] > 0.75
    timing_not_lawful = flags.get("timing_not_lawful", False) or bool(candidate.get("dependencies"))
    activate_forbidden = any(
        (
            forbidden_intersection,
            omega_denied,
            inadmissible_scope,
            replay_blocked,
            truth_unsatisfied,
            branch_over_limit,
        )
    )

    lawful = list(ACTION_ALPHABET)
    if activate_forbidden and "ACTIVATE_NOW" in lawful:
        lawful.remove("ACTIVATE_NOW")
    if omega_denied or inadmissible_scope:
        lawful = ["REFUSE_INADMISSIBLE"]

    gating = {
        "forbidden_intersection": forbidden_intersection,
        "omega_denied": omega_denied,
        "inadmissible_scope": inadmissible_scope,
        "replay_blocked": replay_blocked,
        "truth_unsatisfied": truth_unsatisfied,
        "branch_over_limit": branch_over_limit,
        "committee_required": committee_required,
        "role_mismatch": role_mismatch,
        "circulation_blocked": circulation_blocked,
        "continuation_value_remaining": continuation_value_remaining,
        "timing_not_lawful": timing_not_lawful,
        "activate_forbidden": activate_forbidden,
        "seed_rich_witness_poor": modifiers["seed_rich_witness_poor"],
    }
    return lawful, gating


def choose_action(
    lawful_actions: list[str],
    gating: dict[str, bool],
    score_payload: dict[str, float],
) -> tuple[str, str]:
    if "REFUSE_INADMISSIBLE" in lawful_actions and (gating["omega_denied"] or gating["inadmissible_scope"]):
        return "REFUSE_INADMISSIBLE", "Omega or corridor policy denies this motion at the current scope."
    if gating["forbidden_intersection"]:
        return "QUARANTINE", "Quarantine or unresolved-failure classes intersect the packet blockers."
    if gating["replay_blocked"]:
        return "REPLAY_FIRST", "Replay dependency remains unresolved, so motion must pass through ReplayKernel first."
    if gating["truth_unsatisfied"]:
        return "REQUEST_WITNESSES", "Truth burden is not yet satisfied at the current witness envelope."
    if gating["branch_over_limit"] or gating["committee_required"]:
        return "ESCALATE_TO_COMMITTEE", "Stewardship or branch-limit law requires committee routing."
    if gating["role_mismatch"]:
        return "REQUEST_HELP", "The packet is locally blocked by a role/current mismatch."
    if gating["circulation_blocked"] and gating["continuation_value_remaining"]:
        return "COMPRESS_TO_SEED", "Forward circulation is blocked, but continuation value remains high enough to seed the next lawful pass."
    if gating["timing_not_lawful"]:
        return "HOLD", "The packet has value, but timing or dependency order is not yet lawful."
    if score_payload["urgency_modulated_score"] >= ACTIVATE_THRESHOLD and "ACTIVATE_NOW" in lawful_actions:
        return "ACTIVATE_NOW", "This packet is the highest lawful motion under the current score and override regime."
    if gating["continuation_value_remaining"]:
        return "COMPRESS_TO_SEED", "Activation is not yet lawful, but the packet still preserves continuation value."
    return "HOLD", "No override fires, but the score does not yet justify activation."


def obligations_for_action(action: str) -> list[str]:
    obligations = {
        "ACTIVATE_NOW": [
            "emit typed runtime receipt",
            "write replay/store obligation",
            "mutate queue state",
            "emit successor seed",
        ],
        "HOLD": [
            "preserve queue entry",
            "re-evaluate after dependency or pressure change",
        ],
        "REQUEST_WITNESSES": [
            "request primary witnesses",
            "keep ambiguity explicit until burden is met",
        ],
        "REQUEST_HELP": [
            "route to AgentRegistry or peer organ",
            "attach role/current mismatch note",
        ],
        "REPLAY_FIRST": [
            "schedule replay job in ReplayKernel",
            "block public closure until replay receipt returns",
        ],
        "QUARANTINE": [
            "route packet into QuarantineManifold",
            "attach contradiction and failure-class labels",
        ],
        "COMPRESS_TO_SEED": [
            "emit continuation seed",
            "store seed in ContinuationSeedVault",
        ],
        "ESCALATE_TO_COMMITTEE": [
            "prepare committee escalation packet",
            "suppress parallel conflicting commit paths",
        ],
        "REFUSE_INADMISSIBLE": [
            "emit refusal receipt",
            "preserve reason and corridor denial scope",
        ],
    }
    return obligations[action]


def make_successor_seed(candidate: dict[str, Any], action: str, score_payload: dict[str, float]) -> dict[str, Any]:
    base_seed = candidate.get("continuation_seed") or slugify(candidate["title"])
    return {
        "seed_id": f"{base_seed}__{action.lower()}",
        "seed_value": round(candidate.get("axes", {}).get("seed_value", 0.0), 4),
        "origin_candidate_id": candidate["id"],
        "origin_action": action,
        "route_signature": route_signature(candidate),
        "next_lawful_attempt": {
            "ACTIVATE_NOW": "replay_store_and_commit",
            "HOLD": "re-score_after_dependency_shift",
            "REQUEST_WITNESSES": "collect_primary_witnesses",
            "REQUEST_HELP": "handoff_to_role_match",
            "REPLAY_FIRST": "replay_then_re-score",
            "QUARANTINE": "repair_or_scope_isolate",
            "COMPRESS_TO_SEED": "restore_under_lawful_window",
            "ESCALATE_TO_COMMITTEE": "committee_decision_then_re-enter",
            "REFUSE_INADMISSIBLE": "return_to_scope_with_new_packet",
        }[action],
        "priority_score": round(score_payload["urgency_modulated_score"], 6),
    }


def evaluate_candidate_world(candidate_world: dict[str, Any]) -> dict[str, Any]:
    validate_candidate_world(candidate_world)
    constitution = motion_constitution_object()
    parameters = dict(constitution["default_parameters"])
    parameters.update(candidate_world.get("parameters", {}))
    weights = dict(DEFAULT_WEIGHTS)
    weights.update(parameters.get("weights", {}))
    beta = float(parameters.get("beta", DEFAULT_BETA))
    brainstem_state = candidate_world["brainstem_state"]

    hysteresis_state_path = Path(candidate_world.get("hysteresis_state_path", HYSTERESIS_STATE_PATH))
    hysteresis_state = load_hysteresis_state(hysteresis_state_path)

    route_counts: dict[str, int] = {}
    for candidate in candidate_world["candidates"]:
        route = route_signature(candidate)
        route_counts[route] = route_counts.get(route, 0) + 1

    results = []
    for candidate in candidate_world["candidates"]:
        candidate = dict(candidate)
        candidate.setdefault("flags", {})
        candidate.setdefault("blockers", [])
        candidate.setdefault("blocker_classes", [])
        axes = normalize_axes(candidate.get("axes", {}))
        modifiers = apply_hysteresis(candidate, axes, hysteresis_state, route_counts[route_signature(candidate)])
        scores = base_score(axes, weights, beta)
        lawful_actions, gating = lawful_actions_for_candidate(candidate, axes, brainstem_state, modifiers)
        action, reason = choose_action(lawful_actions, gating, scores)
        next_seed = make_successor_seed(candidate, action, scores)
        results.append(
            {
                "candidate_id": candidate["id"],
                "title": candidate["title"],
                "source_queue": candidate["source_queue"],
                "route_signature": route_signature(candidate),
                "score_vector": {
                    "axes": axes,
                    "numerator": round(scores["numerator"], 6),
                    "denominator": round(scores["denominator"], 6),
                    "priority_score": round(scores["priority_score"], 6),
                    "urgency_modulated_score": round(scores["urgency_modulated_score"], 6),
                },
                "lawful_actions": lawful_actions,
                "chosen_action": action,
                "reason": reason,
                "blockers": candidate["blockers"],
                "blocker_classes": candidate["blocker_classes"],
                "gating": gating,
                "hysteresis_modifiers": modifiers,
                "obligations": obligations_for_action(action),
                "next_seed": next_seed,
            }
        )

    results.sort(key=lambda item: item["score_vector"]["urgency_modulated_score"], reverse=True)
    return {
        "generated_at": utc_now(),
        "truth": TRUTH_STATE,
        "live_docs_blocked": True,
        "weights": weights,
        "beta": beta,
        "brainstem_state": brainstem_state,
        "candidate_count": len(results),
        "results": results,
        "hysteresis_state_path": str(hysteresis_state_path),
    }


def update_hysteresis_state(
    hysteresis_state: dict[str, Any],
    evaluation: dict[str, Any],
    path: Path,
) -> dict[str, Any]:
    updated = dict(hysteresis_state)
    recently_refused = dict(updated.get("recently_refused", {}))
    recently_quarantined = dict(updated.get("recently_quarantined", {}))
    committee_pending = list(updated.get("committee_pending_routes", []))
    history = list(updated.get("history", []))

    for result in evaluation["results"]:
        candidate_id = result["candidate_id"]
        route = result["route_signature"]
        action = result["chosen_action"]
        if action == "REFUSE_INADMISSIBLE":
            entry = dict(recently_refused.get(candidate_id, {}))
            entry["count"] = int(entry.get("count", 0)) + 1
            entry["last_action"] = action
            entry["updated_at"] = utc_now()
            recently_refused[candidate_id] = entry
        elif candidate_id in recently_refused:
            recently_refused.pop(candidate_id, None)

        if action == "QUARANTINE":
            recently_quarantined[route] = {
                "last_action": action,
                "updated_at": utc_now(),
            }
        elif route in recently_quarantined and action in {"ACTIVATE_NOW", "REPLAY_FIRST"}:
            recently_quarantined.pop(route, None)

        if action == "ESCALATE_TO_COMMITTEE" and route not in committee_pending:
            committee_pending.append(route)
        elif route in committee_pending and action in {"ACTIVATE_NOW", "COMPRESS_TO_SEED", "REFUSE_INADMISSIBLE"}:
            committee_pending.remove(route)

        history.append(
            {
                "candidate_id": candidate_id,
                "action": action,
                "route_signature": route,
                "priority_score": result["score_vector"]["urgency_modulated_score"],
                "timestamp": utc_now(),
            }
        )

    updated["generated_at"] = utc_now()
    updated["recently_refused"] = recently_refused
    updated["recently_quarantined"] = recently_quarantined
    updated["committee_pending_routes"] = committee_pending
    updated["history"] = history[-200:]
    write_json(path, updated)
    return updated


def simulate_candidate_world(candidate_world: dict[str, Any]) -> dict[str, Any]:
    evaluation = evaluate_candidate_world(candidate_world)
    hysteresis_state = load_hysteresis_state(Path(evaluation["hysteresis_state_path"]))
    updated_hysteresis_state = update_hysteresis_state(
        hysteresis_state, evaluation, Path(evaluation["hysteresis_state_path"])
    )
    traces = []
    for result in evaluation["results"]:
        action = result["chosen_action"]
        trace = [
            {
                "state": "OBSERVE",
                "guard": "candidate packet visible",
                "output": {
                    "candidate_id": result["candidate_id"],
                    "route_signature": result["route_signature"],
                },
            },
            {
                "state": "SCORE",
                "guard": "feature vector ready",
                "output": result["score_vector"],
            },
            {
                "state": "GATE",
                "guard": "lawful actions filtered through Omega, immune state, and burden limits",
                "output": {
                    "lawful_actions": result["lawful_actions"],
                    "chosen_action": action,
                },
            },
        ]
        if action == "ACTIVATE_NOW":
            trace.append(
                {
                    "state": "ACT",
                    "guard": "Omega pass and no hard override",
                    "output": {
                        "action": action,
                        "reason": result["reason"],
                    },
                }
            )
        trace.extend(
            [
                {
                    "state": "RECEIPT",
                    "guard": "typed motion result emitted",
                    "output": {
                        "action": action,
                        "reason": result["reason"],
                        "obligations": result["obligations"],
                    },
                },
                {
                    "state": "REPLAY_STORE",
                    "guard": "receipt emitted",
                    "output": {
                        "obligations": result["obligations"],
                        "hysteresis_state_path": evaluation["hysteresis_state_path"],
                    },
                },
                {
                    "state": "SEED",
                    "guard": "next lawful continuation determined",
                    "output": result["next_seed"],
                },
            ]
        )
        traces.append(
            {
                "candidate_id": result["candidate_id"],
                "chosen_action": action,
                "trace": trace,
            }
        )

    return {
        "generated_at": utc_now(),
        "truth": TRUTH_STATE,
        "live_docs_blocked": True,
        "candidate_count": evaluation["candidate_count"],
        "results": evaluation["results"],
        "traces": traces,
        "updated_hysteresis_state": updated_hysteresis_state,
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_motion_spec_markdown(constitution: dict[str, Any]) -> str:
    laws = "\n".join(f"- {law}" for law in constitution["constitutional_spine"]["laws"])
    score_axes = "\n".join(f"- `{axis}`" for axis in constitution["score_axes"])
    actions = "\n".join(f"- `{action}`" for action in constitution["action_alphabet"])
    sources = "\n".join(
        f"- `{item['label']}` :: `{item['truth']}` :: `{item['path']}` :: {item['role']}" for item in source_basis()
    )
    return f"""# MotionConstitution_L1

Truth state: `{TRUTH_STATE}`

## Constitutional Spine

The smallest lawful action-selection organ is frozen here as:

$$
\\text{{MotionConstitution}}_{{L1}} = (\\mathcal O,\\mathcal Q,\\mathcal S,\\mathcal A,\\mathcal H,\\Sigma^+)
$$

with

$$
\\mathcal O = (G, \\Pi, \\Omega, \\mathcal I, \\mathcal R).
$$

The constitutional membrane is rooted in `Sigma = {{AppA, AppI, AppM}}`.

{laws}

## Brainstem State

- `G`: route graph, mycelium structure, and addressable memory
- `Pi`: pressure field, salience gradients, and unfinished-work vectors
- `Omega`: legality projector
- `I`: immune state
- `R`: replay and witness memory

## Candidate World

The `v0` source queues are:

{chr(10).join(f"- `{queue}`" for queue in ALLOWED_SOURCE_QUEUES)}

Each candidate packet remains typed by source organ, target organ, current family, truth burden, expected packet type, dependencies, blockers, and continuation seed.

## Score Axes

{score_axes}

## Action Alphabet

{actions}

## Hard Overrides

{chr(10).join(f"- {rule}" for rule in constitution["hard_overrides"])}

## Minimal Automaton

`OBSERVE -> SCORE -> GATE -> ACT/RECEIPT -> REPLAY_STORE -> SEED`

## Source Basis

{sources}
"""


def render_score_law_markdown() -> str:
    return f"""# MotionConstitution_L1 Score Law

Truth state: `{TRUTH_STATE}`

The fused scheduler law is frozen as:

$$
\\Pi(q)=
\\frac{{
\\mathrm{{ClosureGain}}(q)\\cdot
\\mathrm{{HeartNeed}}(q)\\cdot
\\mathrm{{ReplayReadiness}}(q)\\cdot
\\mathrm{{IntegrationYield}}(q)\\cdot
\\mathrm{{OrganAdjacency}}(q)\\cdot
\\mathrm{{SeedValue}}(q)
}}{{\\mathrm{{Cost}}(q)+\\mathrm{{ReplayCost}}(q)+\\mathrm{{Risk}}(q)+\\mathrm{{FailureDebt}}(q)+\\mathrm{{BranchBurden}}(q)+\\mathrm{{ContradictionHeat}}(q)}}
$$

Urgency is modulated but never allowed to override legality:

$$
\\Pi^*(q)=\\Pi(q)\\cdot(1+\\beta\\cdot\\mathrm{{PressureGradient}}(q)), \\qquad \\beta={DEFAULT_BETA}.
$$

Default parameterization:

- all score weights begin at `1.0`
- `beta = {DEFAULT_BETA}`
- `truth_threshold = {TRUTH_THRESHOLD}`
- `replay_threshold = {REPLAY_THRESHOLD}`
- `branch_limit = {BRANCH_LIMIT}`
- `activate_threshold = {ACTIVATE_THRESHOLD}`

Truth readiness is carried as a gate rather than a numerator term. `v0` treats it as the membrane deciding whether witness burden has been satisfied strongly enough for activation.
"""


def render_action_rules_markdown() -> str:
    rows = [
        ["ACTIVATE_NOW", "Highest lawful motion; no override fires; replay and truth burdens satisfied."],
        ["HOLD", "Value exists, but timing or dependency order is not yet lawful."],
        ["REQUEST_WITNESSES", "Truth burden is unsatisfied at the current witness envelope."],
        ["REQUEST_HELP", "Role/current mismatch blocks local execution."],
        ["REPLAY_FIRST", "Replay dependency remains unresolved."],
        ["QUARANTINE", "Forbidden contradiction or unresolved-failure classes intersect blockers."],
        ["COMPRESS_TO_SEED", "Continuation value remains while lawful forward motion does not."],
        ["ESCALATE_TO_COMMITTEE", "Stewardship or branch-limit law requires governance membrane routing."],
        ["REFUSE_INADMISSIBLE", "Omega or corridor policy forbids the move at this scope."],
    ]
    overrides = [
        "hard blockers and Omega denial always forbid `ACTIVATE_NOW`",
        "`QUARANTINE` outranks every non-refusal action when forbidden classes intersect",
        "`REPLAY_FIRST` outranks `REQUEST_HELP` and `REQUEST_WITNESSES` when replay is the primary dependency",
        "`REQUEST_WITNESSES` outranks `REQUEST_HELP` when truth burden is the primary blocker",
        "`ESCALATE_TO_COMMITTEE` outranks `COMPRESS_TO_SEED` when stewardship or branch-limit law fires",
        "`COMPRESS_TO_SEED` wins only when continuation value remains but lawful forward motion does not",
    ]
    return f"""# Action Alphabet and Hard Overrides

{markdown_table(["ActionClass", "Routing law"], rows)}

## Override Order

{chr(10).join(f"- {item}" for item in overrides)}
"""


def render_hysteresis_markdown() -> str:
    rules = [
        "recently refused packets require stronger evidence before reactivation",
        "recently quarantined routes cannot reactivate without trust or replay improvement",
        "duplicate nearby quests with the same route class increase branch burden and lower activation priority",
        "seed-rich but witness-poor branches prefer `COMPRESS_TO_SEED` over `ACTIVATE_NOW`",
        "committee-pending items suppress parallel conflicting commits",
    ]
    return f"""# Hysteresis and Inhibition

Truth state: `{TRUTH_STATE}`

The inhibition layer exists because the organism has repeatedly shown the failure modes named by the runtime packet: over-eagerness, under-prioritization, elegant but low-yield recursion, duplication, silent contradiction, and unbounded branching.

## Rules

{chr(10).join(f"- {rule}" for rule in rules)}

The persisted local ledger at `09_hysteresis_state.json` is therefore not optional bookkeeping. It is the memory surface that lets the brainstem become self-stabilizing instead of merely clever.
"""


def render_route_table_markdown(route_table: dict[str, Any]) -> str:
    admissible_rows = [
        [item["route"], item["current"], item["packet_family"], item["law"]]
        for item in route_table["admissible_movement_rules"]
    ]
    forbidden_rows = [[item["route"], item["law"]] for item in route_table["forbidden_routes"]]
    committee_rows = [[item["route"], item["trigger"]] for item in route_table["committee_required_routes"]]
    seed_rows = [[item["route"], item["trigger"]] for item in route_table["seed_fallback_routes"]]
    return f"""# OrganCurrentRouteTable.v0

Truth state: `{TRUTH_STATE}`

## Admissible Routes

{markdown_table(["Route", "Current", "Packet family", "Law"], admissible_rows)}

## Forbidden Routes

{markdown_table(["Route", "Law"], forbidden_rows)}

## Committee-Required Routes

{markdown_table(["Route", "Trigger"], committee_rows)}

## Seed Fallback Routes

{markdown_table(["Route", "Trigger"], seed_rows)}
"""


def render_motion_readme(manifest: dict[str, Any]) -> str:
    return f"""# Motion Constitution Layer

This layer freezes `MotionConstitution_L1` as the first action-selection bridge between governance and execution.

## Core outputs

- `00_motion_constitution_l1.md`
- `01_motion_constitution_l1.json`
- `02_score_law.md`
- `03_action_alphabet_and_overrides.md`
- `04_hysteresis_inhibition.md`
- `05_organ_current_route_table_v0.md`
- `06_organ_current_route_table_v0.json`
- `07_candidate_world_schema.json`
- `08_action_fixture_all_classes.json`
- `09_hysteresis_state.json`

## CLI

```powershell
python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\motion_constitution_cli.py" build
python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\motion_constitution_cli.py" route-table
python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\motion_constitution_cli.py" score "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\15_MOTION_CONSTITUTION\\08_action_fixture_all_classes.json"
python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\motion_constitution_cli.py" simulate "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\15_MOTION_CONSTITUTION\\08_action_fixture_all_classes.json"
```

## State

- Truth: `{manifest['truth']}`
- Live Google Docs: `{'BLOCKED' if manifest['live_docs_blocked'] else 'PASS'}`
- Supplements entries: `{', '.join(manifest['supplement_entry_ids'])}`
- Runtime manifest: `06_RUNTIME/16_motion_constitution_manifest.json`
"""


def render_motion_supplement(constitution: dict[str, Any], manifest: dict[str, Any]) -> str:
    return f"""# Motion Constitution L1: The Lawful Action-Selection Engine

MotionConstitution_L1 is the smallest organ that can decide what should move now without collapsing governance, immunity, and replay into one undifferentiated impulse. It sits between lawful structure and lawful execution and freezes the brainstem state as

$$
\\mathcal O=(G,\\Pi,\\Omega,\\mathcal I,\\mathcal R),
$$

where `G` is the route graph and addressable memory, `Pi` is the pressure field, `Omega` is the legality projector, `I` is the immune state, and `R` is replay and witness memory. The constitutional membrane is `Sigma = {{AppA, AppI, AppM}}`, so no motion is admissible unless it preserves address grammar, truth corridors, and replay obligations together.

The candidate world of `v0` is intentionally modest. Packets arrive only from `QuestBoard`, `AgentRegistry`, `Committee outputs`, `Immune scheduler outputs`, and `Continuation seeds`. Each candidate is typed by source organ, target organ, current family, truth burden, expected packet type, continuation seed, dependencies, blockers, and a score vector. This does not create a live scheduler daemon. It creates an offline evaluator that can score, gate, and simulate action decisions honestly while the live queue runtime is still absent.

The score law is frozen as a ratio of closure gain, heart need, replay readiness, integration yield, organ adjacency, and seed value against cost, replay cost, risk, failure debt, branch burden, and contradiction heat. Pressure gradient modulates urgency with `beta = {DEFAULT_BETA}` but does not override legality. Truth readiness remains a membrane variable rather than a numerator term because the system must still know whether witness burden has actually been met before it moves.

The action alphabet is finite and constitutional: `ACTIVATE_NOW`, `HOLD`, `REQUEST_WITNESSES`, `REQUEST_HELP`, `REPLAY_FIRST`, `QUARANTINE`, `COMPRESS_TO_SEED`, `ESCALATE_TO_COMMITTEE`, and `REFUSE_INADMISSIBLE`. `Omega` denial or scope inadmissibility immediately forces refusal. Forbidden contradiction or unresolved-failure classes force quarantine ahead of all non-refusal motions. Replay dependency outranks help and witness requests when replay is the primary gap. Witness requests outrank help when truth burden is the real blocker. Committee escalation outranks seed compression when stewardship or branch-limit law fires. Seed compression wins only when forward circulation is blocked but continuation value remains alive.

The minimal automaton is `OBSERVE -> SCORE -> GATE -> ACT/RECEIPT -> REPLAY_STORE -> SEED`. That automaton is the action chamber itself. It observes a candidate packet, computes a lawful score, gates the packet against constitutional and immune rules, emits either a performed action or a typed receipt, stores replay obligations, and finally emits a successor seed. The successor seed is not decorative. It is the guarantee that every terminal motion returns a lawful continuation surface instead of a dead end.

The final stabilizer is hysteresis. Recently refused packets require stronger evidence before reactivation. Recently quarantined routes cannot reactivate without trust or replay improvement. Duplicate nearby quests increase branch burden. Seed-rich but witness-poor branches prefer seed compression over activation. Committee-pending items suppress conflicting commits. Without these rules the system would remain clever but metabolically wasteful.

The present object is frozen as `{manifest['truth']}` because live Google Docs access remains blocked and the strongest current witness basis is the user packet plus local mirrors of `GIT BRAIN` and `PULSE RETRO WEAVING`. The law is now explicit. The remaining frontier is parameterization: exact weights, long-session hysteresis tuning, and future live routing into a real quest board when the queue runtime exists.

SUPPLEMENT - MOTION CONSTITUTION L1
"""


def render_route_supplement(route_table: dict[str, Any], manifest: dict[str, Any]) -> str:
    organ_list = ", ".join(item["organ_id"] for item in route_table["organ_classes"])
    current_list = ", ".join(item["current_id"] for item in route_table["current_classes"])
    zone_list = ", ".join(item["zone_id"] for item in route_table["zone_classes"])
    packet_list = ", ".join(route_table["packet_families"])
    return f"""# Organ Current Route Table v0

OrganCurrentRouteTable.v0 is the first admissible movement atlas for the motion constitution. It names the organs that lawful packets may traverse, the currents that characterize those movements, the zones that constrain them, and the packet families the system is actually allowed to circulate in `v0`.

The current organ basis is {organ_list}. These organs are not interchangeable. `BrainstemChamber` scores and gates motion. `QuestBoard` and `AgentRegistry` surface candidate work and role envelopes. `CommitteeChamber` handles stewardship and branch-limit governance. `ImmuneScheduler` injects quarantine pressure. `ReplayKernel` handles replay-first obligations. `QuarantineManifold` contains contradiction and unresolved failure classes. `ContinuationSeedVault` stores lawful successor seeds. `PublicCommitSurface` is the membrane for replay-cleared closure only.

The current basis is {current_list}. Governance current carries escalation and stewardship decisions. Truth current carries witness and admissibility work. Replay current carries deterministic rerun obligations. Immune current carries quarantine and refusal traffic. Continuation current carries successor seeds. Transport current carries ordinary lawful movement once the membrane conditions are already met.

The zone basis is {zone_list}. `brainstem_internal` is where scoring and gating happen but public closure is still forbidden. `committee_internal` is where collective governance resolves branch pressure. `replay_lab` is where replay may run without public promotion. `quarantine_zone` contains contradiction safely. `seed_store` preserves lawful continuation while movement pauses. `public_grade` accepts only replay-cleared closure artifacts.

The packet basis is {packet_list}. This finite packet family is the discipline that keeps `v0` small enough to govern honestly. Every packet family has admissible routes, forbidden routes, committee-required routes, and seed fallback routes rather than a single undifferentiated path.

The admissible rules establish the lawful trunk: quest packets enter the brainstem through typed queues, help requests come through the registry, immune pressure enters from the scheduler, replay jobs leave through `ReplayKernel`, committee escalations leave through `CommitteeChamber`, quarantine packets enter `QuarantineManifold`, continuation seeds enter `ContinuationSeedVault`, and public closure reaches `PublicCommitSurface` only after replay conditions are already met.

The forbidden rules define the membrane. Quarantine may not export directly into public closure. Quest packets may not bypass the brainstem. Brainstem packets may not reach public-grade closure when replay readiness is still below threshold or `Omega` denies. Recently quarantined routes may not reactivate without improvement. Committee-pending routes may not fork into conflicting parallel commits.

Committee-required routes are explicitly named rather than inferred. They fire when branch burden exceeds stewardship limit, when multi-agent governance is required, or when a packet's truth burden exceeds its current carrier envelope. Seed fallback routes are also explicit: when lawful forward motion is blocked but continuation value remains, the system must write a seed instead of pretending that silence is resolution.

This table is frozen as `{manifest['truth']}`. It is not yet a live scheduler routing map, but it is the correct first admissibility atlas for the new action-selection organ. It gives the constitution a movement membrane instead of leaving lawful action as an abstract intention.

SUPPLEMENT - ORGAN CURRENT ROUTE TABLE V0
"""


def update_active_readme(manifest: dict[str, Any]) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    text = ensure_line_after_anchor(
        text,
        "- `14_PARALLEL_PLANS`: materialized `4^4` frontier plan lattice for `Ch03`, `Ch10`, `Ch12`, and `Ch14`, including execution tiers and dependency routes. Manifest: `14_PARALLEL_PLANS/04_plan_manifest.json`.",
        "- `15_MOTION_CONSTITUTION`: offline action-selection organ, score law, hysteresis ledger, route table, and motion supplements bridge. Manifest: `06_RUNTIME/16_motion_constitution_manifest.json`.",
    )
    old_scaffold = "- Canonical scaffold: `21 chapters + 16 appendices + source capsules + metro maps + civilization governance stack + deep synthesis + deeper neural net + queryable local neural routing + chapter frontier compiler + 4^4 parallel frontier plan lattice`"
    new_scaffold = "- Canonical scaffold: `21 chapters + 16 appendices + source capsules + metro maps + civilization governance stack + deep synthesis + deeper neural net + queryable local neural routing + chapter frontier compiler + 4^4 parallel frontier plan lattice + motion constitution layer`"
    if old_scaffold in text:
        text = text.replace(old_scaffold, new_scaffold, 1)
    elif "motion constitution layer" not in text:
        text = text.replace("## Rebuild", new_scaffold + "\n\n## Rebuild", 1)

    body = [
        f"- Truth: `{manifest['truth']}`",
        f"- Status: `{manifest['status']}`",
        f"- Live Google Docs: `{'BLOCKED' if manifest['live_docs_blocked'] else 'PASS'}`",
        "- Motion layer root: `15_MOTION_CONSTITUTION`",
        "- Runtime manifest: `06_RUNTIME/16_motion_constitution_manifest.json`",
        f"- Supplements added: `{', '.join(manifest['supplement_entry_ids'])}`",
        f"- Route-table file: `{ROUTE_TABLE_JSON.relative_to(ACTIVE_ROOT).as_posix()}`",
    ]
    text = replace_or_append_section(text, "## Motion Constitution State", body)
    write_text(README_PATH, text)


def update_full_stack_manifest(manifest: dict[str, Any]) -> None:
    full_stack = load_json(FULL_STACK_MANIFEST_PATH)
    full_stack["generated_at"] = utc_now()
    full_stack["live_docs_blocked"] = True
    full_stack.setdefault("layers", {})
    full_stack["layers"]["motion_constitution_l1"] = {
        "manifest": "06_RUNTIME/16_motion_constitution_manifest.json",
        "layer_root": "15_MOTION_CONSTITUTION",
        "truth": manifest["truth"],
        "status": manifest["status"],
        "route_table_json": "15_MOTION_CONSTITUTION/06_organ_current_route_table_v0.json",
        "hysteresis_state_json": "15_MOTION_CONSTITUTION/09_hysteresis_state.json",
        "supplement_entry_ids": manifest["supplement_entry_ids"],
        "supplement_paths": manifest["supplement_paths"],
        "live_docs_blocked": True,
    }
    write_json(FULL_STACK_MANIFEST_PATH, full_stack)


def build_motion_constitution() -> dict[str, Any]:
    constitution = motion_constitution_object()
    route_table = organ_current_route_table()
    manifest = {
        "generated_at": utc_now(),
        "id": constitution["id"],
        "version": constitution["version"],
        "status": constitution["status"],
        "truth": constitution["truth"],
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error(),
        "source_basis": source_basis(),
        "layer_root": str(MOTION_ROOT),
        "motion_spec_markdown": str(MOTION_SPEC_MD),
        "motion_spec_json": str(MOTION_SPEC_JSON),
        "score_law_markdown": str(SCORE_LAW_MD),
        "action_rules_markdown": str(ACTION_RULES_MD),
        "hysteresis_markdown": str(HYSTERESIS_MD),
        "route_table_markdown": str(ROUTE_TABLE_MD),
        "route_table_json": str(ROUTE_TABLE_JSON),
        "candidate_world_schema": str(CANDIDATE_WORLD_SCHEMA_PATH),
        "fixture_path": str(ALL_ACTION_FIXTURE_PATH),
        "hysteresis_state_path": str(HYSTERESIS_STATE_PATH),
        "supplement_entry_ids": ["Supp07", "Supp08"],
        "supplement_paths": [
            str(MOTION_SUPPLEMENT_PATH),
            str(ROUTE_SUPPLEMENT_PATH),
        ],
        "manuscript_outputs": {
            "spine": str(SPINE_OUTPUT_PATH),
            "supplements": str(SUPPLEMENTS_OUTPUT_PATH),
        },
    }

    MOTION_ROOT.mkdir(parents=True, exist_ok=True)
    write_text(MOTION_SPEC_MD, render_motion_spec_markdown(constitution))
    write_json(MOTION_SPEC_JSON, constitution)
    write_text(SCORE_LAW_MD, render_score_law_markdown())
    write_text(ACTION_RULES_MD, render_action_rules_markdown())
    write_text(HYSTERESIS_MD, render_hysteresis_markdown())
    write_text(ROUTE_TABLE_MD, render_route_table_markdown(route_table))
    write_json(ROUTE_TABLE_JSON, route_table)
    write_json(CANDIDATE_WORLD_SCHEMA_PATH, candidate_world_schema())
    write_json(ALL_ACTION_FIXTURE_PATH, all_action_fixture())
    if not HYSTERESIS_STATE_PATH.exists():
        write_json(HYSTERESIS_STATE_PATH, initial_hysteresis_state())
    write_text(MOTION_README_PATH, render_motion_readme(manifest))
    write_text(MOTION_SUPPLEMENT_PATH, render_motion_supplement(constitution, manifest))
    write_text(ROUTE_SUPPLEMENT_PATH, render_route_supplement(route_table, manifest))

    build_manuscript_volumes(DEFAULT_MANIFEST)
    spine_receipt = audit_manuscript(DEFAULT_MANIFEST, build_first=False)
    write_json(AUDIT_RECEIPT_PATH, spine_receipt)
    update_spine_readme(spine_receipt)
    update_spine_manifest(spine_receipt)
    update_active_readme(manifest)
    update_full_stack_manifest(manifest)
    write_json(MANIFEST_PATH, manifest)
    return manifest


def build_if_missing() -> None:
    if not MANIFEST_PATH.exists():
        build_motion_constitution()


def load_candidate_world_from_arg(raw_path: str) -> dict[str, Any]:
    path = Path(raw_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return load_json(path)


def render_score_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# MotionConstitution_L1 Score Report",
        "",
        f"- Truth: `{result['truth']}`",
        f"- Live Google Docs: `{'BLOCKED' if result['live_docs_blocked'] else 'PASS'}`",
        f"- Candidate count: `{result['candidate_count']}`",
        "",
    ]
    for item in result["results"]:
        lines.extend(
            [
                f"## {item['candidate_id']} - {item['title']}",
                "",
                f"- Chosen action: `{item['chosen_action']}`",
                f"- Lawful actions: `{', '.join(item['lawful_actions'])}`",
                f"- Priority score: `{item['score_vector']['priority_score']}`",
                f"- Urgency-modulated score: `{item['score_vector']['urgency_modulated_score']}`",
                f"- Reason: {item['reason']}",
                f"- Route signature: `{item['route_signature']}`",
                f"- Obligations: `{'; '.join(item['obligations'])}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_simulation_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# MotionConstitution_L1 Simulation Report",
        "",
        f"- Truth: `{result['truth']}`",
        f"- Live Google Docs: `{'BLOCKED' if result['live_docs_blocked'] else 'PASS'}`",
        f"- Candidate count: `{result['candidate_count']}`",
        "",
    ]
    for trace in result["traces"]:
        lines.extend(
            [
                f"## {trace['candidate_id']} -> {trace['chosen_action']}",
                "",
            ]
        )
        for step in trace["trace"]:
            lines.append(f"- `{step['state']}` :: {step['guard']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_route_table_output(route_table: dict[str, Any]) -> str:
    lines = [
        "# OrganCurrentRouteTable.v0",
        "",
        f"- Truth: `{route_table['truth']}`",
        f"- Organ classes: `{len(route_table['organ_classes'])}`",
        f"- Current classes: `{len(route_table['current_classes'])}`",
        f"- Zone classes: `{len(route_table['zone_classes'])}`",
        f"- Packet families: `{len(route_table['packet_families'])}`",
        "",
        "## Admissible Routes",
        "",
    ]
    for item in route_table["admissible_movement_rules"]:
        lines.append(f"- `{item['route']}` :: {item['law']}")
    lines.append("")
    lines.append("## Forbidden Routes")
    lines.append("")
    for item in route_table["forbidden_routes"]:
        lines.append(f"- `{item['route']}` :: {item['law']}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def source_basis() -> list[dict[str, str]]:
    return [
        {
            "label": "user_packet",
            "path": "(thread packet :: MotionConstitution_L1 Dual-Track Build)",
            "truth": TRUTH_STATE,
            "role": "primary derived specification source",
        },
        {
            "label": "git_brain_mirror",
            "path": str(PROJECT_ROOT.parent / "Athena FLEET" / "GIT BRAIN.4d.md"),
            "truth": "NEAR",
            "role": "local mirror for immune architecture and governance framing",
        },
        {
            "label": "git_brain_capsule",
            "path": str(
                PROJECT_ROOT.parent
                / "Athena FLEET"
                / "FLEET_MYCELIUM_NETWORK"
                / "CAPSULES"
                / "LOCAL"
                / "F09_git_brain.md"
            ),
            "truth": "derived-local",
            "role": "local capsule witness for governance cortex and quarantine tensions",
        },
        {
            "label": "pulse_retro_weaving_mirror",
            "path": str(
                PROJECT_ROOT.parent
                / "MATH"
                / "FINAL FORM"
                / "COMPLETE TOMES"
                / "ATHENA"
                / "funtional"
                / "PULSE RETRO WEAVING.4d.md"
            ),
            "truth": "NEAR",
            "role": "local mirror for retro weaving, continuation, and successor-seed return",
        },
        {
            "label": "athena_core_contribution",
            "path": "(packet-derived; no stronger local mirror located)",
            "truth": TRUTH_STATE,
            "role": "brainstem formula O = (G, Pi, Omega, I, R)",
        },
        {
            "label": "athena_fleet_contribution",
            "path": "(packet-derived; no stronger local mirror located)",
            "truth": TRUTH_STATE,
            "role": "scheduler law using closure gain, heart need, replay readiness, cost, risk, and failure debt",
        },
    ]


def main() -> int:
    args = parse_args()
    if args.command == "build":
        manifest = build_motion_constitution()
        if args.as_json:
            print(json.dumps(manifest, indent=2))
        else:
            print(f"Wrote motion constitution layer: {MOTION_ROOT}")
            print(f"Wrote runtime manifest: {MANIFEST_PATH}")
            print(f"Updated supplements volume: {SUPPLEMENTS_OUTPUT_PATH}")
            print(f"Truth: {manifest['truth']}")
            print("Live Google Docs: BLOCKED")
        return 0

    build_if_missing()

    if args.command == "route-table":
        route_table = organ_current_route_table()
        if args.as_json:
            print(json.dumps(route_table, indent=2))
        else:
            print(render_route_table_output(route_table), end="")
        return 0

    candidate_world = load_candidate_world_from_arg(args.candidate_world)
    if args.command == "score":
        result = evaluate_candidate_world(candidate_world)
        if args.as_json:
            print(json.dumps(result, indent=2))
        else:
            print(render_score_markdown(result), end="")
        return 0

    if args.command == "simulate":
        result = simulate_candidate_world(candidate_world)
        if args.as_json:
            print(json.dumps(result, indent=2))
        else:
            print(render_simulation_markdown(result), end="")
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

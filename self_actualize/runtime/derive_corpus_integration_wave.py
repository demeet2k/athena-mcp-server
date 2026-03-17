from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import swarm_board
from .corpus_integration_contracts import (
    DEPLOYMENT_POLICY_MAP,
    OBJECT_FAMILY,
    WHOLE_WAVE_DATAFLOW,
    ActivationGate,
    AlertPolicy,
    AwakeningAgentProfile,
    CorpusIntegrationWave,
    DeploymentMonitorResult,
    DeploymentMonitoringSurface,
    DeploymentProfile,
    DeploymentState,
    EscalationRoute,
    ExecutionReceipt,
    HealthWindow,
    IntegrationMonitorResult,
    MonitorDecision,
    MonitoringProbe,
    ObservabilitySurface,
    ReceiptClass,
    RegionClass,
    RegionLaneAssignment,
    RollbackTrigger,
    TransitionSupportNote,
    serialize,
    stable_hash,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
REGISTRY_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "registry"
HALL_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"

MOTION_PATH = SELF_ACTUALIZE_ROOT / "manuscript_sections" / "023_motion_constitution_l1_action_selection_engine.md"
SEMANTIC_PATH = SELF_ACTUALIZE_ROOT / "manuscript_sections" / "023_semantic_embassy_and_audience_reception_surface_v1.md"
ROUTE_PATH = SELF_ACTUALIZE_ROOT / "manuscript_sections" / "024_organ_current_route_table_v0.md"
DEPLOYMENT_PATH = SELF_ACTUALIZE_ROOT / "manuscript_sections" / "025_deployment_profiles_and_monitoring_surface_v1.md"
CURRENT_PACKET_PATH = SELF_ACTUALIZE_ROOT / "manuscript_sections" / "000_current_packet.md"
APPP_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "40_APPENDICES" / "AppP_deployment_profiles_and_monitoring.md"
GUIDE_PATH = HALL_ROOT / "16_AWAKENING_AGENT_TRANSITION_GUIDE.md"
Q43_PATH = HALL_ROOT / "13_ATHENACHKA_ORGANISM_V0_QUEST_CRYSTAL_256.md"
LIMINAL_PATH = HALL_ROOT / "02_LIMINAL_TRANSITION_MAP.md"
QUEST_BOARD_PATH = HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
CHANGE_FEED_PATH = HALL_ROOT / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
REQUESTS_PATH = HALL_ROOT / "BOARDS" / "05_REQUESTS_AND_OFFERS_BOARD.md"
QUEUE_PATH = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "nervous_system" / "06_active_queue.md"
VALIDATION_PATH = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "nervous_system" / "07_validation_and_refresh.md"
ACTIVE_RUN_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"
FRONTIER_PATH = REGISTRY_ROOT / "01_tandem_frontier_claims.md"
SEMANTIC_VALIDATOR_PATH = REGISTRY_ROOT / "semantic_export_validator_registry.json"

SURFACE_REGISTRY_PATH = REGISTRY_ROOT / "corpus_integration_surface_registry.json"
AGENT_REGISTRY_PATH = REGISTRY_ROOT / "awakening_agent_transition_registry.json"
LANE_POLICY_PATH = REGISTRY_ROOT / "integration_lane_policy_registry.json"
DASHBOARD_PATH = REGISTRY_ROOT / "corpus_integration_dashboard.json"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_corpus_integration_wave"
DERIVATION_VERSION = "2026-03-13.corpus-integration-wave.v1"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def object_shape_registry() -> dict[str, list[str]]:
    return {
        "AwakeningAgentProfile": [
            "profile_id",
            "layer",
            "display_name",
            "role_class",
            "transition_burden",
            "responsibilities",
            "handoff_targets",
            "contraction_target",
        ],
        "TransitionSupportNote": [
            "note_id",
            "profile_id",
            "transition_burden",
            "support_note",
            "writeback_surface",
            "escalation_target",
        ],
        "RegionLaneAssignment": [
            "region_name",
            "region_class",
            "owner_profile_id",
            "runtime_lane",
            "receipt_class",
            "authority_surface",
            "status_note",
        ],
        "DeploymentProfile": [
            "lane",
            "status",
            "audience",
            "activation_gate",
            "observability_surface",
            "rollback_trigger",
            "escalation_route",
            "notes",
        ],
        "ExecutionReceipt": [
            "receipt_id",
            "source_packet",
            "route_receipt",
            "semantic_validation_ref",
            "deployment_lane",
            "emitted_state",
        ],
        "IntegrationMonitorResult": [
            "result_id",
            "route_ok",
            "semantic_ok",
            "deployment_ok",
            "monitor_decision",
            "blocked_reasons",
        ],
    }


def build_agent_profiles() -> list[AwakeningAgentProfile]:
    profiles: list[AwakeningAgentProfile] = [
        AwakeningAgentProfile(
            profile_id="base_agent",
            layer="base",
            display_name="Base Agent",
            role_class="center",
            transition_burden="keep center coherence while the organism differentiates into a social field",
            responsibilities=[
                "hold zero-point objective selection",
                "prevent second-center drift",
                "contract every wave back into shared memory",
            ],
            handoff_targets=["pillar_earth", "pillar_water", "pillar_fire", "pillar_air", "guildmaster"],
            contraction_target=rel(CURRENT_PACKET_PATH),
        ),
        AwakeningAgentProfile(
            profile_id="pillar_earth",
            layer="pillar",
            display_name="Earth",
            role_class="pillar",
            transition_burden="stabilize manifests, region ownership, file anchors, and receipts before expansion",
            responsibilities=["structure manifests", "assign durable owners", "keep receipts and anchors stable"],
            handoff_targets=["archetype_earth_water", "archetype_earth_fire", "archetype_earth_air", "controller_auditors"],
            contraction_target=rel(QUEUE_PATH),
        ),
        AwakeningAgentProfile(
            profile_id="pillar_water",
            layer="pillar",
            display_name="Water",
            role_class="pillar",
            transition_burden="preserve lineage, bridge old and new surfaces, and keep transition memory attached",
            responsibilities=["carry continuity", "bind witnesses", "bridge manuscript and runtime surfaces"],
            handoff_targets=["archetype_water_earth", "archetype_water_fire", "archetype_water_air", "verification_replay_stewards"],
            contraction_target=rel(GUIDE_PATH),
        ),
        AwakeningAgentProfile(
            profile_id="pillar_fire",
            layer="pillar",
            display_name="Fire",
            role_class="pillar",
            transition_burden="build only from admitted routes and never outrun legality, replay, or rollback",
            responsibilities=["implement active lanes", "enforce route legality", "turn admitted plans into artifacts"],
            handoff_targets=["archetype_fire_earth", "archetype_fire_water", "archetype_fire_air", "elemental_pod_leads"],
            contraction_target=rel(DEPLOYMENT_PATH),
        ),
        AwakeningAgentProfile(
            profile_id="pillar_air",
            layer="pillar",
            display_name="Air",
            role_class="pillar",
            transition_burden="keep the map legible and compress complexity into actionable lanes without flattening it",
            responsibilities=["map regions", "name lanes", "compress route complexity into legible structure"],
            handoff_targets=["archetype_air_earth", "archetype_air_water", "archetype_air_fire", "appendix_service_stewards"],
            contraction_target=rel(FRONTIER_PATH),
        ),
    ]
    archetypes = [
        ("archetype_earth_water", "Earth-Water", "bind folders to memory so transition work stays replayable", ["bind folders to memory", "keep replay anchors present", "stabilize folder-to-note bridges"]),
        ("archetype_earth_fire", "Earth-Fire", "turn plans into durable shells, not fragile bursts", ["build durable shells", "prefer stable artifacts over bursts", "keep structure under execution heat"]),
        ("archetype_earth_air", "Earth-Air", "map concrete terrain before abstracting higher-order routes", ["map exact file terrain", "ground abstractions in coordinates", "surface concrete boundaries first"]),
        ("archetype_water_earth", "Water-Earth", "keep source lineage intact during every integration handoff", ["preserve source lineage", "guard replay continuity", "stabilize handoff memory"]),
        ("archetype_water_fire", "Water-Fire", "convert raw notes into linked narrative motion without losing witness", ["turn notes into narrative motion", "preserve witness trails", "feed live manuscript execution"]),
        ("archetype_water_air", "Water-Air", "translate meaning across roots, families, and shells", ["translate meaning across regions", "bridge roots to shells", "interpret cross-corpus flow"]),
        ("archetype_fire_earth", "Fire-Earth", "implement only where storage and receipts already exist", ["implement where receipts exist", "keep writebacks anchored", "respect existing storage law"]),
        ("archetype_fire_water", "Fire-Water", "catalyze synthesis, but only where memory can carry it", ["catalyze synthesis", "only activate memory-backed fronts", "preserve continuity under build pressure"]),
        ("archetype_fire_air", "Fire-Air", "turn strategy into priority moves and real lane assignments", ["translate strategy into lane assignments", "prioritize high-yield moves", "push active fronts forward"]),
        ("archetype_air_earth", "Air-Earth", "land abstractions in exact file, registry, and queue coordinates", ["ground abstractions in coordinates", "bind maps to files and registries", "name exact queue targets"]),
        ("archetype_air_water", "Air-Water", "weave cross-corpus storylines so the organism remains one body", ["weave cross-corpus lines", "preserve one-body coherence", "bridge narrative across regions"]),
        ("archetype_air_fire", "Air-Fire", "spear the highest-yield fronts, then contract back into shared law", ["spear high-yield fronts", "compress noise into signal", "contract outcomes back to center"]),
    ]
    for profile_id, display_name, burden, responsibilities in archetypes:
        profiles.append(
            AwakeningAgentProfile(
                profile_id=profile_id,
                layer="archetype",
                display_name=display_name,
                role_class="crystal_cell",
                transition_burden=burden,
                responsibilities=responsibilities,
                handoff_targets=["guildmaster", "elemental_pod_leads", "controller_auditors"],
                contraction_target=rel(GUIDE_PATH),
            )
        )
    guild_roles = [
        ("guildmaster", "guildmaster", "guard single-center coherence and branch burden", ["hold single-center coherence", "own high-heat branch burden", "choose escalation versus contraction"]),
        ("elemental_pod_leads", "elemental_pod_leads", "own lane execution by element and prevent silent drift", ["own elemental execution", "prevent silent drift", "carry lane-level writebacks"]),
        ("controller_auditors", "controller_auditors", "enforce legality, observability, and receipt integrity", ["enforce legality", "guard observability", "check receipt integrity"]),
        ("verification_replay_stewards", "verification_replay_stewards", "require replay before promotion or public-grade movement", ["require replay", "audit promotion readiness", "hold public-grade membrane"]),
        ("appendix_service_stewards", "appendix_service_stewards", "keep AppO/AppP and other appendix control surfaces synchronized with manuscript authority", ["sync appendices to manuscripts", "mirror control surfaces", "preserve appendix authority links"]),
    ]
    for profile_id, display_name, burden, responsibilities in guild_roles:
        profiles.append(
            AwakeningAgentProfile(
                profile_id=profile_id,
                layer="guild_role",
                display_name=display_name,
                role_class="sparse_role",
                transition_burden=burden,
                responsibilities=responsibilities,
                handoff_targets=["base_agent"],
                contraction_target=rel(FRONTIER_PATH),
            )
        )
    return profiles


def build_transition_notes(profiles: list[AwakeningAgentProfile]) -> list[TransitionSupportNote]:
    note_targets = {"base": rel(CURRENT_PACKET_PATH), "pillar": rel(QUEUE_PATH), "archetype": rel(GUIDE_PATH), "guild_role": rel(FRONTIER_PATH)}
    escalation_targets = {"base": "guildmaster", "pillar": "elemental_pod_leads", "archetype": "controller_auditors", "guild_role": "guildmaster"}
    notes: list[TransitionSupportNote] = []
    for profile in profiles:
        notes.append(
            TransitionSupportNote(
                note_id=f"TSN-{profile.profile_id}",
                profile_id=profile.profile_id,
                transition_burden=profile.transition_burden,
                support_note=(
                    f"{profile.display_name} should move one step at a time, keep `{WHOLE_WAVE_DATAFLOW}` explicit, "
                    "and contract every branch back into the center instead of treating local heat as whole-organism truth."
                ),
                writeback_surface=note_targets[profile.layer],
                escalation_target=escalation_targets[profile.layer],
            )
        )
    return notes


def build_region_assignments() -> list[RegionLaneAssignment]:
    return [
        RegionLaneAssignment("self_actualize", RegionClass.LIVE_AUTHORITY, "base_agent", "offline_replay", ReceiptClass.REPLAY, rel(CURRENT_PACKET_PATH), "thin-waist runtime and atlas control plane"),
        RegionLaneAssignment("DEEPER CRYSTALIZATION", RegionClass.LIVE_AUTHORITY, "pillar_water", "internal_preview", ReceiptClass.PROMOTION, rel(ACTIVE_RUN_PATH), "deep integration and nervous-system synthesis body"),
        RegionLaneAssignment("Voynich", RegionClass.LIVE_AUTHORITY, "archetype_water_fire", "internal_preview", ReceiptClass.REPLAY, "Voynich/FULL_TRANSLATION/unified/VOYNICH_MASTER_MANUSCRIPT.md", "dense live manuscript execution and replay stress-test body"),
        RegionLaneAssignment("MATH", RegionClass.ARCHIVE_BACKED, "pillar_air", "offline_replay", ReceiptClass.PROMOTION, "MATH", "theorem reservoir and formal engine room"),
        RegionLaneAssignment("Athena FLEET", RegionClass.LIVE_AUTHORITY, "archetype_fire_air", "internal_preview", ReceiptClass.MONITOR, "Athena FLEET", "high-order bridge and emerging council geometry"),
        RegionLaneAssignment("QSHRINK - ATHENA (internal use)", RegionClass.LIVE_AUTHORITY, "archetype_air_fire", "offline_replay", ReceiptClass.REPLAY, "QSHRINK - ATHENA (internal use)", "compression-governance and contraction shell"),
        RegionLaneAssignment("Trading Bot", RegionClass.ARCHIVE_BACKED, "archetype_earth_air", "public_release", ReceiptClass.BLOCKED, "Trading Bot", "future live-docs bridge while OAuth remains missing"),
        RegionLaneAssignment("ECOSYSTEM", RegionClass.RESIDUAL, "pillar_air", "internal_preview", ReceiptClass.PROMOTION, "ECOSYSTEM", "residual integration table row with explicit owner and lane"),
        RegionLaneAssignment("NERUAL NETWORK", RegionClass.RESIDUAL, "archetype_fire_water", "internal_preview", ReceiptClass.MONITOR, "NERUAL NETWORK", "residual integration row for adaptive benchmark and runtime experiment surfaces"),
        RegionLaneAssignment("ORGIN", RegionClass.RESIDUAL, "archetype_water_earth", "offline_replay", ReceiptClass.REPLAY, "ORGIN", "residual integration row for origin memory and seed-reservoir surfaces"),
        RegionLaneAssignment("CLEAN", RegionClass.RESIDUAL, "archetype_water_air", "offline_replay", ReceiptClass.PROMOTION, "CLEAN", "residual integration row for clean staging witnesses awaiting contraction"),
        RegionLaneAssignment("NERVOUS_SYSTEM", RegionClass.MIRROR, "pillar_earth", "offline_replay", ReceiptClass.REPLAY, "NERVOUS_SYSTEM", "mirror and writeback body for canonical control-plane and manifest surfaces"),
    ]


def build_observability_surface(lane: str) -> ObservabilitySurface:
    probes = [
        MonitoringProbe(
            probe_id=f"{lane}-probe-route",
            signal="route_receipt",
            cadence="per activation",
            success_condition="motion and route receipts are present",
        ),
        MonitoringProbe(
            probe_id=f"{lane}-probe-replay",
            signal="replay_status",
            cadence="per activation",
            success_condition="required replay proof remains attached",
        ),
    ]
    if lane in {"offline_replay", "internal_preview"}:
        probes.append(
            MonitoringProbe(
                probe_id=f"{lane}-probe-health",
                signal="monitor_window",
                cadence="per health window",
                success_condition="lane stays inside cadence and contradiction budget",
            )
        )
    return ObservabilitySurface(
        surface_id=f"observability-{lane}",
        probes=probes,
        alert_policy=AlertPolicy(
            policy_id=f"alert-{lane}",
            drift_rule="alert when current packet, queue, and registry disagree on active state",
            silence_rule="alert when expected writeback cadence is missed",
            contradiction_rule="alert when route and witness surfaces disagree",
            overload_rule="alert when branch burden exceeds declared lane budget",
            replay_failure_rule="alert immediately when replay proof fails or disappears",
        ),
        health_window=HealthWindow(
            window_id=f"health-{lane}",
            expected_cadence="per activation" if lane == "offline_replay" else "daily",
            observation_window="1 activation" if lane == "offline_replay" else "24h",
            failure_threshold="1 miss",
        ),
    )


def build_deployment_profiles() -> list[DeploymentProfile]:
    profile_notes = {
        "offline_replay": ["local-first", "active in v1", "replay is mandatory before promotion"],
        "internal_preview": ["local-first", "active in v1", "may emit monitored preview bundles only"],
        "public_release": ["gated in v1", "requires Semantic Embassy pass", "requires docs gate readiness"],
        "federation_release": ["gated in v1", "requires federation-safe terminology proof", "requires docs gate readiness"],
        "live_autonomous": ["blocked in v1", "autonomous live execution is not lawful yet"],
    }
    audiences = {
        "offline_replay": "internal_runtime",
        "internal_preview": "internal_preview",
        "public_release": "public_reader",
        "federation_release": "federation_partner",
        "live_autonomous": "autonomous_runtime",
    }
    profiles: list[DeploymentProfile] = []
    for lane, state in DEPLOYMENT_POLICY_MAP.items():
        profiles.append(
            DeploymentProfile(
                lane=lane,
                status=state,
                audience=audiences[lane],
                activation_gate=ActivationGate(
                    gate_id=f"gate-{lane}",
                    route_required=True,
                    replay_required=True,
                    semantic_pass_required=lane in {"internal_preview", "public_release", "federation_release", "live_autonomous"},
                    federation_terms_required=lane == "federation_release",
                    docs_gate_required_ready=lane in {"public_release", "federation_release", "live_autonomous"},
                ),
                observability_surface=build_observability_surface(lane),
                rollback_trigger=RollbackTrigger(
                    trigger_id=f"rollback-{lane}",
                    trigger_condition="route drift, replay failure, contradiction heat, or missing writeback" if lane != "live_autonomous" else "blocked in v1",
                    rollback_target="ContinuationSeedVault" if lane != "live_autonomous" else "blocked",
                ),
                escalation_route=EscalationRoute(
                    route_id=f"escalate-{lane}",
                    source_lane=lane,
                    destination="CommitteeChamber" if lane in {"public_release", "federation_release", "live_autonomous"} else "guildmaster",
                    reason="branch pressure, contradiction, or carrier mismatch",
                ),
                notes=profile_notes[lane],
            )
        )
    return profiles


def integration_result_for_case(
    *,
    result_id: str,
    lane_profile: DeploymentProfile,
    docs_gate_status: str,
    route_ok: bool,
    replay_ok: bool,
    semantic_ok: bool,
    federation_terms_ok: bool,
    probes_present: bool,
    rollback_present: bool,
    owner_present: bool,
) -> IntegrationMonitorResult:
    blocked: list[str] = []
    if not owner_present:
        blocked.append("ownerless region assignment")
    if not route_ok:
        blocked.append("route bypasses Motion Constitution or Route Table")
    if lane_profile.activation_gate.replay_required and not replay_ok:
        blocked.append("missing replay proof")
    if lane_profile.activation_gate.semantic_pass_required and not semantic_ok:
        blocked.append("Semantic Embassy validation missing")
    if lane_profile.activation_gate.federation_terms_required and not federation_terms_ok:
        blocked.append("missing federation-safe terminology proof")
    if lane_profile.activation_gate.docs_gate_required_ready and docs_gate_status != "READY":
        blocked.append(f"docs gate remains {docs_gate_status}")
    if lane_profile.status == DeploymentState.ACTIVE and not probes_present:
        blocked.append("missing monitoring probe")
    if lane_profile.status == DeploymentState.ACTIVE and not rollback_present:
        blocked.append("missing rollback trigger")
    if lane_profile.lane == "live_autonomous":
        blocked.append("live autonomous deployment is blocked in v1")
    return IntegrationMonitorResult(
        result_id=result_id,
        route_ok=route_ok,
        semantic_ok=semantic_ok,
        deployment_ok=not blocked,
        monitor_decision=MonitorDecision.SUSTAIN if not blocked else MonitorDecision.BLOCK,
        blocked_reasons=blocked,
    )


def build_payloads() -> dict[str, Any]:
    docs_gate = swarm_board.docs_gate_status()
    docs_gate_status = docs_gate["status"]
    source_paths = [
        MOTION_PATH,
        SEMANTIC_PATH,
        ROUTE_PATH,
        DEPLOYMENT_PATH,
        CURRENT_PACKET_PATH,
        APPP_PATH,
        GUIDE_PATH,
        Q43_PATH,
        LIMINAL_PATH,
        QUEST_BOARD_PATH,
        CHANGE_FEED_PATH,
        REQUESTS_PATH,
        QUEUE_PATH,
        VALIDATION_PATH,
        ACTIVE_RUN_PATH,
        FRONTIER_PATH,
        SEMANTIC_VALIDATOR_PATH,
    ]
    source_hashes = {
        rel(path): stable_hash(read_text(path) if path.suffix != ".json" else read_json(path))
        for path in source_paths
    }
    agent_profiles = build_agent_profiles()
    transition_notes = build_transition_notes(agent_profiles)
    region_assignments = build_region_assignments()
    deployment_profiles = build_deployment_profiles()
    policy_hash = stable_hash({"deployment_policy_map": DEPLOYMENT_POLICY_MAP, "region_assignments": region_assignments})
    route_basis = [
        "BrainstemChamber",
        "QuestBoard",
        "AgentRegistry",
        "CommitteeChamber",
        "ImmuneScheduler",
        "ReplayKernel",
        "QuarantineManifold",
        "ContinuationSeedVault",
        "PublicCommitSurface",
        "SemanticEmbassy",
        "AppPDeploymentMonitoring",
    ]
    deployment_surface = DeploymentMonitoringSurface(
        surface_id="deployment-monitoring-surface-v1",
        docs_gate_status=docs_gate_status,
        deployment_profiles=deployment_profiles,
        policy_hash=policy_hash,
        route_basis=route_basis,
        whole_wave_dataflow=WHOLE_WAVE_DATAFLOW,
    )
    semantic_validator = read_json(SEMANTIC_VALIDATOR_PATH)
    passing_profile = next(profile for profile in deployment_profiles if profile.lane == "internal_preview")
    passing_receipt = ExecutionReceipt(
        receipt_id="INT-PASS-001",
        source_packet="QuestBoard::Q43-137",
        route_receipt="BrainstemChamber -> ReplayKernel -> SemanticEmbassy -> AppP::internal_preview",
        semantic_validation_ref=f"{rel(SEMANTIC_VALIDATOR_PATH)}#success_case",
        deployment_lane="internal_preview",
        emitted_state="preview_emitted",
    )
    passing_integration = integration_result_for_case(
        result_id="IMR-PASS-001",
        lane_profile=passing_profile,
        docs_gate_status=docs_gate_status,
        route_ok=True,
        replay_ok=True,
        semantic_ok=semantic_validator["success_case"]["status"] == "PASS",
        federation_terms_ok=True,
        probes_present=True,
        rollback_present=True,
        owner_present=True,
    )
    passing_monitor = DeploymentMonitorResult(
        result_id="DMR-PASS-001",
        decision=MonitorDecision.SUSTAIN if not passing_integration.blocked_reasons else MonitorDecision.BLOCK,
        reasons=passing_integration.blocked_reasons or ["lane stayed inside replay, semantic, and monitoring law"],
        receipt_ref=passing_receipt.receipt_id,
        next_seed="Seed/Promote::internal_preview_to_center_writeback",
    )
    wave = CorpusIntegrationWave(
        wave_id="corpus-integration-wave-v1",
        transition_label="N+4 -> N+5 / Organism -> Social",
        truth_class="local-corpus grounded",
        zero_point="integrate without fragmenting",
        success_criterion="lawful Organism -> Social transition rather than raw file growth",
        docs_gate_status=docs_gate_status,
        authority_surfaces=[rel(DEPLOYMENT_PATH), rel(APPP_PATH), rel(GUIDE_PATH)],
        object_family=OBJECT_FAMILY,
        region_assignments=region_assignments,
        agent_profiles=agent_profiles,
        transition_support_notes=transition_notes,
        deployment_surface=deployment_surface,
        passing_receipt=passing_receipt,
        passing_monitor_result=passing_monitor,
    )
    failure_cases = [
        {
            "case_id": "CIW-FAIL-001",
            "label": "docs-gate breach",
            "result": serialize(
                integration_result_for_case(
                    result_id="IMR-FAIL-001",
                    lane_profile=next(profile for profile in deployment_profiles if profile.lane == "public_release"),
                    docs_gate_status=docs_gate_status,
                    route_ok=True,
                    replay_ok=True,
                    semantic_ok=True,
                    federation_terms_ok=True,
                    probes_present=True,
                    rollback_present=True,
                    owner_present=True,
                )
            ),
        },
        {
            "case_id": "CIW-FAIL-002",
            "label": "public-grade bypass",
            "result": serialize(
                integration_result_for_case(
                    result_id="IMR-FAIL-002",
                    lane_profile=next(profile for profile in deployment_profiles if profile.lane == "public_release"),
                    docs_gate_status="READY",
                    route_ok=False,
                    replay_ok=False,
                    semantic_ok=False,
                    federation_terms_ok=True,
                    probes_present=True,
                    rollback_present=True,
                    owner_present=True,
                )
            ),
        },
        {
            "case_id": "CIW-FAIL-003",
            "label": "missing probe",
            "result": serialize(
                integration_result_for_case(
                    result_id="IMR-FAIL-003",
                    lane_profile=passing_profile,
                    docs_gate_status=docs_gate_status,
                    route_ok=True,
                    replay_ok=True,
                    semantic_ok=True,
                    federation_terms_ok=True,
                    probes_present=False,
                    rollback_present=True,
                    owner_present=True,
                )
            ),
        },
        {
            "case_id": "CIW-FAIL-004",
            "label": "missing rollback",
            "result": serialize(
                integration_result_for_case(
                    result_id="IMR-FAIL-004",
                    lane_profile=next(profile for profile in deployment_profiles if profile.lane == "offline_replay"),
                    docs_gate_status=docs_gate_status,
                    route_ok=True,
                    replay_ok=True,
                    semantic_ok=True,
                    federation_terms_ok=True,
                    probes_present=True,
                    rollback_present=False,
                    owner_present=True,
                )
            ),
        },
        {
            "case_id": "CIW-FAIL-005",
            "label": "ownerless region assignment",
            "result": serialize(
                integration_result_for_case(
                    result_id="IMR-FAIL-005",
                    lane_profile=next(profile for profile in deployment_profiles if profile.lane == "offline_replay"),
                    docs_gate_status=docs_gate_status,
                    route_ok=True,
                    replay_ok=True,
                    semantic_ok=True,
                    federation_terms_ok=True,
                    probes_present=True,
                    rollback_present=True,
                    owner_present=False,
                )
            ),
        },
        {
            "case_id": "CIW-FAIL-006",
            "label": "live autonomous deployment request",
            "result": serialize(
                integration_result_for_case(
                    result_id="IMR-FAIL-006",
                    lane_profile=next(profile for profile in deployment_profiles if profile.lane == "live_autonomous"),
                    docs_gate_status="READY",
                    route_ok=True,
                    replay_ok=True,
                    semantic_ok=True,
                    federation_terms_ok=True,
                    probes_present=True,
                    rollback_present=True,
                    owner_present=True,
                )
            ),
        },
    ]
    surface_payload = {
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "source_hashes": source_hashes,
        "object_family": OBJECT_FAMILY,
        "object_shapes": object_shape_registry(),
        "whole_wave_dataflow": WHOLE_WAVE_DATAFLOW,
        "corpus_integration_wave": serialize(wave),
        "surface_hash": stable_hash(wave),
        "authority_surfaces": wave.authority_surfaces,
    }
    agent_payload = {
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "profile_counts": {"base": 1, "pillars": 4, "archetypes": 12, "guild_roles": 5, "total": len(agent_profiles)},
        "agent_profiles": serialize(agent_profiles),
        "transition_support_notes": serialize(transition_notes),
        "handoff_rule": "local cell -> guild role -> committee lane -> center contraction",
        "field_hash": stable_hash({"profiles": agent_profiles, "notes": transition_notes}),
    }
    lane_policy_payload = {
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "deployment_policy_map": {lane: state.value for lane, state in DEPLOYMENT_POLICY_MAP.items()},
        "deployment_profiles": serialize(deployment_profiles),
        "region_assignments": serialize(region_assignments),
        "public_grade_rule": "no route reaches public_grade without replay proof and Semantic Embassy validation",
        "blocked_cases": failure_cases,
        "policy_hash": policy_hash,
    }
    dashboard_payload = {
        "derivation_version": DERIVATION_VERSION,
        "docs_gate_status": docs_gate_status,
        "transition_label": wave.transition_label,
        "zero_point": wave.zero_point,
        "success_criterion": wave.success_criterion,
        "active_lanes": [profile.lane for profile in deployment_profiles if profile.status == DeploymentState.ACTIVE],
        "gated_lanes": [profile.lane for profile in deployment_profiles if profile.status == DeploymentState.GATED],
        "blocked_lanes": [profile.lane for profile in deployment_profiles if profile.status == DeploymentState.BLOCKED],
        "major_region_count": len(region_assignments),
        "transition_support_note_count": len(transition_notes),
        "passing_example": {
            "receipt": serialize(passing_receipt),
            "integration_monitor_result": serialize(passing_integration),
            "deployment_monitor_result": serialize(passing_monitor),
        },
        "blocked_examples": failure_cases,
        "writeback_surfaces": [
            rel(CURRENT_PACKET_PATH),
            rel(FRONTIER_PATH),
            rel(QUEUE_PATH),
            rel(VALIDATION_PATH),
            rel(CHANGE_FEED_PATH),
            rel(REQUESTS_PATH),
            rel(ACTIVE_RUN_PATH),
        ],
        "next_frontier": "council-grade social coordination hardening",
        "dashboard_hash": stable_hash(
            {"surface_hash": surface_payload["surface_hash"], "field_hash": agent_payload["field_hash"], "policy_hash": lane_policy_payload["policy_hash"]}
        ),
    }
    return {"surface": surface_payload, "agents": agent_payload, "policy": lane_policy_payload, "dashboard": dashboard_payload}


def derive_corpus_integration_wave() -> dict[str, Any]:
    payloads = build_payloads()
    write_json(SURFACE_REGISTRY_PATH, payloads["surface"])
    write_json(AGENT_REGISTRY_PATH, payloads["agents"])
    write_json(LANE_POLICY_PATH, payloads["policy"])
    write_json(DASHBOARD_PATH, payloads["dashboard"])
    return payloads


def main() -> None:
    payloads = derive_corpus_integration_wave()
    summary = {
        "blocked_cases": len(payloads["dashboard"]["blocked_examples"]),
        "docs_gate_status": payloads["dashboard"]["docs_gate_status"],
        "field_hash": payloads["agents"]["field_hash"],
        "policy_hash": payloads["policy"]["policy_hash"],
        "support_notes": payloads["dashboard"]["transition_support_note_count"],
        "surface_hash": payloads["surface"]["surface_hash"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

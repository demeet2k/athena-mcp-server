from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import swarm_board
from .semantic_embassy_contracts import (
    AUDIENCE_REGISTER_POLICY,
    OBJECT_FAMILY,
    RENDER_POLICY_MAP,
    AudienceFacingBundle,
    AudienceProfile,
    AudienceType,
    ClaimClass,
    ClaimSurface,
    DomainPack,
    InterfaceContract,
    KairosAssessment,
    MessageEnvelope,
    RegisterName,
    RegisterProfile,
    ReleaseBundle,
    RenderMode,
    RhetoricalPreview,
    SafeWordingBundle,
    SemanticEmbassySurface,
    TranslationSurface,
    ValidationStatus,
    apply_safe_wording,
    serialize,
    stable_hash,
    validate_semantic_export,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
REGISTRY_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "registry"
MANUSCRIPT_PATH = SELF_ACTUALIZE_ROOT / "manuscript_sections" / "023_semantic_embassy_and_audience_reception_surface_v1.md"
APPO_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "40_APPENDICES" / "AppO_publication_importexport_bundles.md"
CURRENT_PACKET_PATH = SELF_ACTUALIZE_ROOT / "manuscript_sections" / "000_current_packet.md"
FRONTIER_PATH = REGISTRY_ROOT / "01_tandem_frontier_claims.md"

SURFACE_REGISTRY_PATH = REGISTRY_ROOT / "semantic_embassy_surface_registry.json"
VALIDATOR_REGISTRY_PATH = REGISTRY_ROOT / "semantic_export_validator_registry.json"
RENDER_POLICY_PATH = REGISTRY_ROOT / "semantic_render_policy_registry.json"
DASHBOARD_PATH = REGISTRY_ROOT / "semantic_embassy_dashboard.json"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_semantic_embassy_surface"
DERIVATION_VERSION = "2026-03-12.semantic-embassy.v1"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def object_shape_registry() -> dict[str, list[str]]:
    return {
        "ClaimSurface": [
            "attested_meaning",
            "claim_class",
            "claim_ceiling",
            "burden_class",
            "support_refs",
            "forbidden_claims",
            "replay_refs",
        ],
        "AudienceProfile": [
            "audience_type",
            "burden_tolerance",
            "vocabulary_constraints",
            "prior_context",
            "trust_sensitivity",
            "allowed_registers",
        ],
        "RegisterProfile": [
            "name",
            "public_allowed",
            "rhetorical_enabled",
            "description",
        ],
        "InterfaceContract": [
            "contract_id",
            "allowed_audience",
            "allowed_register",
            "required_support_refs",
            "required_replay_refs",
            "safe_wording_required",
        ],
        "MessageEnvelope": [
            "envelope_id",
            "target_surface",
            "audience_type",
            "register",
            "replay_surface",
        ],
        "TranslationSurface": [
            "surface_id",
            "render_mode",
            "wording",
            "benchmark_names",
            "federation_terms",
            "export_refs",
        ],
        "DomainPack": [
            "domain_name",
            "allowed_terms",
            "blocked_terms",
            "benchmark_safe_names",
            "federation_safe_terms",
        ],
        "ReleaseBundle": [
            "bundle_id",
            "recertification_pack_ref",
            "release_trust_pack_ref",
            "public_claim_ceiling",
            "signed_by",
            "allowed_claim_classes",
        ],
        "SafeWordingBundle": [
            "bundle_id",
            "allowed_phrases",
            "blocked_phrases",
            "benchmark_safe_names",
            "federation_safe_names",
            "downgrade_replacements",
        ],
        "KairosAssessment": [
            "receptivity",
            "attention",
            "timing_window",
            "recommended_action",
            "rationale",
        ],
        "RhetoricalPreview": [
            "ethos_gain",
            "pathos_gain",
            "logos_gain",
            "catharsis_mode",
            "style_register",
            "preview_only",
        ],
        "SemanticExportValidatorResult": [
            "status",
            "public_allowed",
            "blocked_reasons",
            "downgraded_phrases",
            "replay_refs",
            "claim_ceiling_proof",
            "normalized_hash",
        ],
    }


def build_success_surface(docs_gate_status: str) -> tuple[SemanticEmbassySurface, dict[str, Any]]:
    claim_surface = ClaimSurface(
        attested_meaning="The Semantic Embassy translates an attested local claim into audience-safe public language without exceeding release trust.",
        claim_class=ClaimClass.PUBLIC_CLAIM,
        claim_ceiling=ClaimClass.PUBLIC_CLAIM,
        burden_class="release_safe_local",
        support_refs=[
            "CLEAN/INFORMATION FROM THE VOID MANI.docx#Chapter14",
            "CLEAN/INFORMATION FROM THE VOID MANI.docx#Chapter15",
            "CLEAN/INFORMATION FROM THE VOID MANI.docx#Chapter20",
            "MATH/FINAL FORM/MYTH - MATH/Philosophy/Philosophy/THE RHETORICAL-POETIC OUTPUT DRIVERS.docx",
            "Athena FLEET/FLEET_MYCELIUM_NETWORK/MIRRORS/LOCAL/F05_neuraltransitmap.md",
        ],
        forbidden_claims=[
            "live-docs verified",
            "fully proven across all shells",
            "externally cleared rhetorical release",
        ],
        replay_refs=[
            "RecertificationPack:semantic-embassy-local-2026-03-12",
            "ReleaseTrustPack:semantic-embassy-local-2026-03-12",
        ],
    )
    audience_profile = AudienceProfile(
        audience_type=AudienceType.PUBLIC_READER,
        burden_tolerance="moderate",
        vocabulary_constraints=["plain language", "no hidden escalation", "no federation overclaim"],
        prior_context="release-notary passed; docs gate blocked",
        trust_sensitivity="high",
        allowed_registers=AUDIENCE_REGISTER_POLICY[AudienceType.PUBLIC_READER],
    )
    register_profile = RegisterProfile(
        name=RegisterName.DIPLOMATIC,
        public_allowed=True,
        rhetorical_enabled=False,
        description="Audience-safe diplomatic export with claim ceilings preserved.",
    )
    interface_contract = InterfaceContract(
        contract_id="iface-semantic-embassy-v1",
        allowed_audience=AudienceType.PUBLIC_READER,
        allowed_register=RegisterName.DIPLOMATIC,
        required_support_refs=3,
        required_replay_refs=2,
        safe_wording_required=True,
    )
    message_envelope = MessageEnvelope(
        envelope_id="env-public-diplomatic-v1",
        target_surface="public_release_note",
        audience_type=AudienceType.PUBLIC_READER,
        register=RegisterName.DIPLOMATIC,
        replay_surface="public_release_note.replay.json",
    )
    domain_pack = DomainPack(
        domain_name="semantic_embassy_public_release",
        allowed_terms=[
            "attested",
            "replay-linked",
            "locally grounded",
            "diplomatic export",
            "release trust",
            "docs-gate blocked",
        ],
        blocked_terms=[
            "universally proven",
            "live-docs verified",
            "externally cleared rhetoric",
        ],
        benchmark_safe_names=["semantic export validator", "release trust pack", "claim surface"],
        federation_safe_terms=["shared-law", "attested bundle", "verified replay"],
    )
    safe_wording_bundle = SafeWordingBundle(
        bundle_id="safe-wording-semantic-embassy-v1",
        allowed_phrases=[
            "attested within the current witness stack",
            "locally grounded",
            "replay-linked",
            "release-safe",
            "docs-gate blocked",
        ],
        blocked_phrases=[
            "fully proven",
            "live-docs verified",
            "rhetorically cleared for public release",
        ],
        benchmark_safe_names=["semantic export validator", "release trust pack", "claim surface"],
        federation_safe_names=["shared-law", "attested bundle", "verified replay"],
        downgrade_replacements={
            "fully proven": "attested within the current witness stack",
            "globally confirmed": "not yet globally replayed",
            "rhetorically cleared for public release": "available only as internal rhetorical preview",
        },
    )
    raw_wording = (
        "This post-attestation surface is fully proven for public release, "
        "but because the docs gate is blocked it is presented as a locally grounded, replay-linked diplomatic export."
    )
    wording, downgraded = apply_safe_wording(raw_wording, safe_wording_bundle)
    translation_surface = TranslationSurface(
        surface_id="translation-public-diplomatic-v1",
        render_mode=RenderMode.DIPLOMATIC,
        wording=wording,
        benchmark_names=[],
        federation_terms=[],
        export_refs=["023_semantic_embassy_and_audience_reception_surface_v1.md", "AppO_publication_importexport_bundles.md"],
    )
    kairos_assessment = KairosAssessment(
        receptivity="ready",
        attention="stable",
        timing_window="now",
        recommended_action="emit_now",
        rationale="The public audience can receive a bounded diplomatic claim that explicitly states the docs gate remains blocked.",
    )
    rhetorical_preview = RhetoricalPreview(
        ethos_gain=0.4,
        pathos_gain=0.2,
        logos_gain=0.9,
        catharsis_mode="none_public",
        style_register="diplomatic_plain",
        preview_only=True,
    )
    validator_result = validate_semantic_export(
        claim_surface=claim_surface,
        audience_profile=audience_profile,
        register_profile=register_profile,
        interface_contract=interface_contract,
        message_envelope=message_envelope,
        translation_surface=translation_surface,
        domain_pack=domain_pack,
        safe_wording_bundle=safe_wording_bundle,
        rhetorical_preview=rhetorical_preview,
    )
    validator_result.downgraded_phrases = downgraded
    audience_bundle = AudienceFacingBundle(
        bundle_id="audience-public-diplomatic-v1",
        target_surface=message_envelope.target_surface,
        audience_type=audience_profile.audience_type,
        register=register_profile.name,
        wording=translation_surface.wording,
        emitted=validator_result.status == ValidationStatus.PASS and kairos_assessment.recommended_action == "emit_now",
        validator_status=validator_result.status,
    )
    surface = SemanticEmbassySurface(
        surface_id="semantic-embassy-surface-v1",
        docs_gate_status=docs_gate_status,
        authority_surfaces=[
            "self_actualize/manuscript_sections/023_semantic_embassy_and_audience_reception_surface_v1.md",
            "NERVOUS_SYSTEM/40_APPENDICES/AppO_publication_importexport_bundles.md",
        ],
        public_mode=RenderMode.DIPLOMATIC,
        claim_surface=claim_surface,
        audience_profile=audience_profile,
        register_profile=register_profile,
        interface_contract=interface_contract,
        message_envelope=message_envelope,
        translation_surface=translation_surface,
        domain_pack=domain_pack,
        release_bundle=ReleaseBundle(
            bundle_id="release-bundle-semantic-embassy-v1",
            recertification_pack_ref="RecertificationPack:semantic-embassy-local-2026-03-12",
            release_trust_pack_ref="ReleaseTrustPack:semantic-embassy-local-2026-03-12",
            public_claim_ceiling=ClaimClass.PUBLIC_CLAIM,
            signed_by="local-corpus-attestation",
            allowed_claim_classes=[
                ClaimClass.EXPLANATORY,
                ClaimClass.BENCHMARK_SAFE,
                ClaimClass.RELEASE_SAFE,
                ClaimClass.PUBLIC_CLAIM,
            ],
        ),
        safe_wording_bundle=safe_wording_bundle,
        kairos_assessment=kairos_assessment,
        rhetorical_preview=rhetorical_preview,
        validator_result=validator_result,
        audience_facing_bundle=audience_bundle,
    )
    replay = {
        "input_flow": "RecertificationPack/ReleaseTrustPack -> ClaimSurface -> AudienceProfile + RegisterProfile -> SafeWordingBundle -> TranslationSurface -> SemanticExportValidatorResult -> AudienceFacingBundle",
        "downgraded_phrases": downgraded,
        "final_wording": translation_surface.wording,
        "validator_status": validator_result.status.value,
        "audience_emit": audience_bundle.emitted,
    }
    return surface, replay


def build_failure_case(
    case_id: str,
    label: str,
    claim_surface: ClaimSurface,
    audience_profile: AudienceProfile,
    register_profile: RegisterProfile,
    interface_contract: InterfaceContract,
    message_envelope: MessageEnvelope,
    translation_surface: TranslationSurface,
    domain_pack: DomainPack,
    safe_wording_bundle: SafeWordingBundle,
    rhetorical_preview: RhetoricalPreview,
) -> dict[str, Any]:
    result = validate_semantic_export(
        claim_surface=claim_surface,
        audience_profile=audience_profile,
        register_profile=register_profile,
        interface_contract=interface_contract,
        message_envelope=message_envelope,
        translation_surface=translation_surface,
        domain_pack=domain_pack,
        safe_wording_bundle=safe_wording_bundle,
        rhetorical_preview=rhetorical_preview,
    )
    return {
        "case_id": case_id,
        "label": label,
        "status": result.status.value,
        "blocked_reasons": result.blocked_reasons,
        "hash": result.normalized_hash,
    }


def build_failure_matrix(base_surface: SemanticEmbassySurface) -> list[dict[str, Any]]:
    claim = base_surface.claim_surface
    audience = base_surface.audience_profile
    register = base_surface.register_profile
    contract = base_surface.interface_contract
    envelope = base_surface.message_envelope
    translation = base_surface.translation_surface
    domain = base_surface.domain_pack
    safe = base_surface.safe_wording_bundle
    preview = base_surface.rhetorical_preview

    failures = []
    failures.append(
        build_failure_case(
            case_id="SEV1-001",
            label="rhetorical/public render requested in v1",
            claim_surface=ClaimSurface(
                attested_meaning=claim.attested_meaning,
                claim_class=ClaimClass.RHETORICAL,
                claim_ceiling=ClaimClass.PUBLIC_CLAIM,
                burden_class=claim.burden_class,
                support_refs=list(claim.support_refs),
                forbidden_claims=list(claim.forbidden_claims),
                replay_refs=list(claim.replay_refs),
            ),
            audience_profile=AudienceProfile(
                audience_type=AudienceType.PUBLIC_READER,
                burden_tolerance=audience.burden_tolerance,
                vocabulary_constraints=list(audience.vocabulary_constraints),
                prior_context=audience.prior_context,
                trust_sensitivity=audience.trust_sensitivity,
                allowed_registers=list(audience.allowed_registers),
            ),
            register_profile=RegisterProfile(
                name=RegisterName.RHETORICAL,
                public_allowed=False,
                rhetorical_enabled=True,
                description="Preview-only rhetorical rendering.",
            ),
            interface_contract=InterfaceContract(
                contract_id="iface-rhetorical-public-v1",
                allowed_audience=AudienceType.PUBLIC_READER,
                allowed_register=RegisterName.RHETORICAL,
                required_support_refs=3,
                required_replay_refs=2,
                safe_wording_required=True,
            ),
            message_envelope=MessageEnvelope(
                envelope_id="env-public-rhetorical-v1",
                target_surface="public_release_note",
                audience_type=AudienceType.PUBLIC_READER,
                register=RegisterName.RHETORICAL,
                replay_surface=envelope.replay_surface,
            ),
            translation_surface=TranslationSurface(
                surface_id="translation-rhetorical-public-v1",
                render_mode=RenderMode.PREVIEW_ONLY,
                wording="A radiant rhetorical release.",
                benchmark_names=[],
                federation_terms=[],
                export_refs=list(translation.export_refs),
            ),
            domain_pack=domain,
            safe_wording_bundle=safe,
            rhetorical_preview=RhetoricalPreview(
                ethos_gain=0.8,
                pathos_gain=0.8,
                logos_gain=0.6,
                catharsis_mode="public",
                style_register="rhetorical",
                preview_only=True,
            ),
        )
    )
    failures.append(
        build_failure_case(
            case_id="SEV1-002",
            label="public wording exceeds benchmark or release support",
            claim_surface=claim,
            audience_profile=audience,
            register_profile=register,
            interface_contract=contract,
            message_envelope=envelope,
            translation_surface=TranslationSurface(
                surface_id="translation-overclaim-v1",
                render_mode=RenderMode.DIPLOMATIC,
                wording="This surface is live-docs verified and fully proven across all shells.",
                benchmark_names=[],
                federation_terms=[],
                export_refs=list(translation.export_refs),
            ),
            domain_pack=domain,
            safe_wording_bundle=safe,
            rhetorical_preview=preview,
        )
    )
    failures.append(
        build_failure_case(
            case_id="SEV1-003",
            label="missing replay refs",
            claim_surface=ClaimSurface(
                attested_meaning=claim.attested_meaning,
                claim_class=claim.claim_class,
                claim_ceiling=claim.claim_ceiling,
                burden_class=claim.burden_class,
                support_refs=list(claim.support_refs),
                forbidden_claims=list(claim.forbidden_claims),
                replay_refs=[],
            ),
            audience_profile=audience,
            register_profile=register,
            interface_contract=contract,
            message_envelope=envelope,
            translation_surface=translation,
            domain_pack=domain,
            safe_wording_bundle=safe,
            rhetorical_preview=preview,
        )
    )
    failures.append(
        build_failure_case(
            case_id="SEV1-004",
            label="missing downgrade replacements",
            claim_surface=claim,
            audience_profile=audience,
            register_profile=register,
            interface_contract=contract,
            message_envelope=envelope,
            translation_surface=translation,
            domain_pack=domain,
            safe_wording_bundle=SafeWordingBundle(
                bundle_id="safe-wording-empty-v1",
                allowed_phrases=list(safe.allowed_phrases),
                blocked_phrases=list(safe.blocked_phrases),
                benchmark_safe_names=list(safe.benchmark_safe_names),
                federation_safe_names=list(safe.federation_safe_names),
                downgrade_replacements={},
            ),
            rhetorical_preview=preview,
        )
    )
    failures.append(
        build_failure_case(
            case_id="SEV1-005",
            label="benchmark-facing surface with non-benchmark-safe names",
            claim_surface=ClaimSurface(
                attested_meaning=claim.attested_meaning,
                claim_class=ClaimClass.BENCHMARK_SAFE,
                claim_ceiling=ClaimClass.BENCHMARK_SAFE,
                burden_class="benchmark",
                support_refs=list(claim.support_refs),
                forbidden_claims=list(claim.forbidden_claims),
                replay_refs=list(claim.replay_refs),
            ),
            audience_profile=AudienceProfile(
                audience_type=AudienceType.BENCHMARK_READER,
                burden_tolerance="low",
                vocabulary_constraints=["benchmark-safe naming only"],
                prior_context="benchmark surface",
                trust_sensitivity="high",
                allowed_registers=AUDIENCE_REGISTER_POLICY[AudienceType.BENCHMARK_READER],
            ),
            register_profile=RegisterProfile(
                name=RegisterName.MINIMAL,
                public_allowed=True,
                rhetorical_enabled=False,
                description="Minimal benchmark-safe wording.",
            ),
            interface_contract=InterfaceContract(
                contract_id="iface-benchmark-minimal-v1",
                allowed_audience=AudienceType.BENCHMARK_READER,
                allowed_register=RegisterName.MINIMAL,
                required_support_refs=3,
                required_replay_refs=2,
                safe_wording_required=True,
            ),
            message_envelope=MessageEnvelope(
                envelope_id="env-benchmark-minimal-v1",
                target_surface="benchmark_note",
                audience_type=AudienceType.BENCHMARK_READER,
                register=RegisterName.MINIMAL,
                replay_surface="benchmark_note.replay.json",
            ),
            translation_surface=TranslationSurface(
                surface_id="translation-benchmark-unsafe-name-v1",
                render_mode=RenderMode.MINIMAL,
                wording="Benchmark summary with unsafe label.",
                benchmark_names=["unsafe label"],
                federation_terms=[],
                export_refs=list(translation.export_refs),
            ),
            domain_pack=domain,
            safe_wording_bundle=safe,
            rhetorical_preview=preview,
        )
    )
    failures.append(
        build_failure_case(
            case_id="SEV1-006",
            label="federation-facing surface with missing federation-safe terms",
            claim_surface=ClaimSurface(
                attested_meaning=claim.attested_meaning,
                claim_class=ClaimClass.FEDERATION_CLAIM,
                claim_ceiling=ClaimClass.FEDERATION_CLAIM,
                burden_class="federation",
                support_refs=list(claim.support_refs),
                forbidden_claims=list(claim.forbidden_claims),
                replay_refs=list(claim.replay_refs),
            ),
            audience_profile=AudienceProfile(
                audience_type=AudienceType.FEDERATION_PARTNER,
                burden_tolerance="low",
                vocabulary_constraints=["federation-safe terminology required"],
                prior_context="shared-law corridor",
                trust_sensitivity="very_high",
                allowed_registers=AUDIENCE_REGISTER_POLICY[AudienceType.FEDERATION_PARTNER],
            ),
            register_profile=RegisterProfile(
                name=RegisterName.DIPLOMATIC,
                public_allowed=True,
                rhetorical_enabled=False,
                description="Diplomatic federation-safe wording.",
            ),
            interface_contract=InterfaceContract(
                contract_id="iface-federation-diplomatic-v1",
                allowed_audience=AudienceType.FEDERATION_PARTNER,
                allowed_register=RegisterName.DIPLOMATIC,
                required_support_refs=3,
                required_replay_refs=2,
                safe_wording_required=True,
            ),
            message_envelope=MessageEnvelope(
                envelope_id="env-federation-diplomatic-v1",
                target_surface="federation_release_note",
                audience_type=AudienceType.FEDERATION_PARTNER,
                register=RegisterName.DIPLOMATIC,
                replay_surface="federation_release_note.replay.json",
            ),
            translation_surface=TranslationSurface(
                surface_id="translation-federation-missing-terms-v1",
                render_mode=RenderMode.DIPLOMATIC,
                wording="Federation release note without the required shared-law vocabulary.",
                benchmark_names=[],
                federation_terms=[],
                export_refs=list(translation.export_refs),
            ),
            domain_pack=domain,
            safe_wording_bundle=safe,
            rhetorical_preview=preview,
        )
    )
    return failures


def build_payloads() -> dict[str, Any]:
    docs_gate = swarm_board.docs_gate_status()
    docs_gate_status = docs_gate["status"]
    surface, replay = build_success_surface(docs_gate_status)
    failure_matrix = build_failure_matrix(surface)
    render_policy_records = [
        {
            "claim_class": claim_class.value,
            "render_mode": RENDER_POLICY_MAP[claim_class].value,
            "public_allowed": claim_class != ClaimClass.RHETORICAL,
            "notes": (
                "federation-safe terminology required"
                if claim_class == ClaimClass.FEDERATION_CLAIM
                else "preview only in v1"
                if claim_class == ClaimClass.RHETORICAL
                else "active public mode"
            ),
        }
        for claim_class in [
            ClaimClass.EXPLANATORY,
            ClaimClass.BENCHMARK_SAFE,
            ClaimClass.RELEASE_SAFE,
            ClaimClass.PUBLIC_CLAIM,
            ClaimClass.FEDERATION_CLAIM,
            ClaimClass.RHETORICAL,
        ]
    ]
    render_policy_payload = {
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "authority_surfaces": [
            "self_actualize/manuscript_sections/023_semantic_embassy_and_audience_reception_surface_v1.md",
            "NERVOUS_SYSTEM/40_APPENDICES/AppO_publication_importexport_bundles.md",
        ],
        "render_policy": render_policy_records,
        "audience_register_policy": {
            audience.value: [register.value for register in AUDIENCE_REGISTER_POLICY[audience]]
            for audience in [
                AudienceType.INTERNAL_RESEARCH,
                AudienceType.BENCHMARK_READER,
                AudienceType.PUBLIC_READER,
                AudienceType.FEDERATION_PARTNER,
            ]
        },
        "policy_hash": stable_hash(render_policy_records),
    }
    validator_rules = [
        "reject wording that exceeds the claim ceiling",
        "reject rhetorical/public outputs in v1",
        "reject missing replay refs",
        "reject missing support refs",
        "reject missing downgrade replacements",
        "reject undeclared register/audience pairings",
        "require benchmark-safe naming for benchmark-facing surfaces",
        "require federation-safe terminology for federation-facing surfaces",
    ]
    validator_payload = {
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "validator_rules": validator_rules,
        "success_case": {
            "status": surface.validator_result.status.value,
            "claim_ceiling_proof": surface.validator_result.claim_ceiling_proof,
            "normalized_hash": surface.validator_result.normalized_hash,
        },
        "failure_cases": failure_matrix,
        "failure_hash": stable_hash(failure_matrix),
    }
    surface_payload = {
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "source_surfaces": {
            "manuscript": "self_actualize/manuscript_sections/023_semantic_embassy_and_audience_reception_surface_v1.md",
            "appo": "NERVOUS_SYSTEM/40_APPENDICES/AppO_publication_importexport_bundles.md",
            "current_packet": "self_actualize/manuscript_sections/000_current_packet.md",
            "frontier_ledger": "self_actualize/mycelium_brain/registry/01_tandem_frontier_claims.md",
        },
        "source_hashes": {
            "manuscript": stable_hash(read_text(MANUSCRIPT_PATH)),
            "appo": stable_hash(read_text(APPO_PATH)),
            "current_packet": stable_hash(read_text(CURRENT_PACKET_PATH)),
            "frontier_ledger": stable_hash(read_text(FRONTIER_PATH)),
        },
        "object_family": OBJECT_FAMILY,
        "object_shapes": object_shape_registry(),
        "frozen_dataflow": "RecertificationPack/ReleaseTrustPack -> ClaimSurface -> AudienceProfile + RegisterProfile -> SafeWordingBundle -> TranslationSurface -> SemanticExportValidatorResult -> AudienceFacingBundle",
        "semantic_embassy_surface": serialize(surface),
        "surface_hash": stable_hash(surface),
    }
    dashboard_payload = {
        "derivation_version": DERIVATION_VERSION,
        "docs_gate_status": docs_gate_status,
        "truth_class": "local-corpus grounded",
        "authority_surfaces": surface.authority_surfaces,
        "public_mode": surface.public_mode.value,
        "object_count": len(OBJECT_FAMILY),
        "validator_rule_count": len(validator_rules),
        "render_policy_hash": render_policy_payload["policy_hash"],
        "surface_hash": surface_payload["surface_hash"],
        "replay_example": replay,
        "failure_summary": {
            "total_cases": len(failure_matrix),
            "case_labels": [record["label"] for record in failure_matrix],
        },
        "frontier_registration": {
            "current_packet": "Semantic Embassy is registered after Release Notary / public-claim attestation.",
            "frontier_ledger": "TF-010 records the surface as the post-attestation audience-reception frontier.",
        },
    }
    return {
        "surface": surface_payload,
        "validator": validator_payload,
        "policy": render_policy_payload,
        "dashboard": dashboard_payload,
    }


def derive_semantic_embassy_surface() -> dict[str, Any]:
    payloads = build_payloads()
    write_json(SURFACE_REGISTRY_PATH, payloads["surface"])
    write_json(VALIDATOR_REGISTRY_PATH, payloads["validator"])
    write_json(RENDER_POLICY_PATH, payloads["policy"])
    write_json(DASHBOARD_PATH, payloads["dashboard"])
    return payloads


def main() -> None:
    payloads = derive_semantic_embassy_surface()
    summary = {
        "docs_gate_status": payloads["dashboard"]["docs_gate_status"],
        "public_mode": payloads["dashboard"]["public_mode"],
        "surface_hash": payloads["surface"]["surface_hash"],
        "render_policy_hash": payloads["policy"]["policy_hash"],
        "failure_cases": payloads["dashboard"]["failure_summary"]["total_cases"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

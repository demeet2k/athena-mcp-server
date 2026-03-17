from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any


class ClaimClass(str, Enum):
    EXPLANATORY = "explanatory"
    BENCHMARK_SAFE = "benchmark_safe"
    RELEASE_SAFE = "release_safe"
    PUBLIC_CLAIM = "public_claim"
    FEDERATION_CLAIM = "federation_claim"
    RHETORICAL = "rhetorical"


class RegisterName(str, Enum):
    MINIMAL = "minimal"
    DIPLOMATIC = "diplomatic"
    RHETORICAL = "rhetorical"


class RenderMode(str, Enum):
    MINIMAL = "minimal"
    DIPLOMATIC = "diplomatic"
    PREVIEW_ONLY = "preview_only"


class AudienceType(str, Enum):
    INTERNAL_RESEARCH = "internal_research"
    BENCHMARK_READER = "benchmark_reader"
    PUBLIC_READER = "public_reader"
    FEDERATION_PARTNER = "federation_partner"


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


OBJECT_FAMILY = [
    "SemanticEmbassySurface",
    "ClaimSurface",
    "AudienceProfile",
    "RegisterProfile",
    "InterfaceContract",
    "MessageEnvelope",
    "TranslationSurface",
    "DomainPack",
    "ReleaseBundle",
    "SafeWordingBundle",
    "KairosAssessment",
    "RhetoricalPreview",
    "SemanticExportValidatorResult",
]

RENDER_POLICY_MAP = {
    ClaimClass.EXPLANATORY: RenderMode.MINIMAL,
    ClaimClass.BENCHMARK_SAFE: RenderMode.MINIMAL,
    ClaimClass.RELEASE_SAFE: RenderMode.DIPLOMATIC,
    ClaimClass.PUBLIC_CLAIM: RenderMode.DIPLOMATIC,
    ClaimClass.FEDERATION_CLAIM: RenderMode.DIPLOMATIC,
    ClaimClass.RHETORICAL: RenderMode.PREVIEW_ONLY,
}

AUDIENCE_REGISTER_POLICY = {
    AudienceType.INTERNAL_RESEARCH: [RegisterName.MINIMAL, RegisterName.DIPLOMATIC, RegisterName.RHETORICAL],
    AudienceType.BENCHMARK_READER: [RegisterName.MINIMAL],
    AudienceType.PUBLIC_READER: [RegisterName.MINIMAL, RegisterName.DIPLOMATIC],
    AudienceType.FEDERATION_PARTNER: [RegisterName.DIPLOMATIC],
}


def serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize(item) for item in value]
    return value


def stable_json(value: Any) -> str:
    return json.dumps(serialize(value), indent=2, sort_keys=True)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


@dataclass
class ClaimSurface:
    attested_meaning: str
    claim_class: ClaimClass
    claim_ceiling: ClaimClass
    burden_class: str
    support_refs: list[str]
    forbidden_claims: list[str]
    replay_refs: list[str]


@dataclass
class AudienceProfile:
    audience_type: AudienceType
    burden_tolerance: str
    vocabulary_constraints: list[str]
    prior_context: str
    trust_sensitivity: str
    allowed_registers: list[RegisterName]


@dataclass
class RegisterProfile:
    name: RegisterName
    public_allowed: bool
    rhetorical_enabled: bool
    description: str


@dataclass
class InterfaceContract:
    contract_id: str
    allowed_audience: AudienceType
    allowed_register: RegisterName
    required_support_refs: int
    required_replay_refs: int
    safe_wording_required: bool


@dataclass
class MessageEnvelope:
    envelope_id: str
    target_surface: str
    audience_type: AudienceType
    register: RegisterName
    replay_surface: str


@dataclass
class TranslationSurface:
    surface_id: str
    render_mode: RenderMode
    wording: str
    benchmark_names: list[str]
    federation_terms: list[str]
    export_refs: list[str]


@dataclass
class DomainPack:
    domain_name: str
    allowed_terms: list[str]
    blocked_terms: list[str]
    benchmark_safe_names: list[str]
    federation_safe_terms: list[str]


@dataclass
class ReleaseBundle:
    bundle_id: str
    recertification_pack_ref: str
    release_trust_pack_ref: str
    public_claim_ceiling: ClaimClass
    signed_by: str
    allowed_claim_classes: list[ClaimClass]


@dataclass
class SafeWordingBundle:
    bundle_id: str
    allowed_phrases: list[str]
    blocked_phrases: list[str]
    benchmark_safe_names: list[str]
    federation_safe_names: list[str]
    downgrade_replacements: dict[str, str]


@dataclass
class KairosAssessment:
    receptivity: str
    attention: str
    timing_window: str
    recommended_action: str
    rationale: str


@dataclass
class RhetoricalPreview:
    ethos_gain: float
    pathos_gain: float
    logos_gain: float
    catharsis_mode: str
    style_register: str
    preview_only: bool


@dataclass
class SemanticExportValidatorResult:
    status: ValidationStatus
    public_allowed: bool
    blocked_reasons: list[str]
    downgraded_phrases: list[str]
    replay_refs: list[str]
    claim_ceiling_proof: str
    normalized_hash: str


@dataclass
class AudienceFacingBundle:
    bundle_id: str
    target_surface: str
    audience_type: AudienceType
    register: RegisterName
    wording: str
    emitted: bool
    validator_status: ValidationStatus


@dataclass
class SemanticEmbassySurface:
    surface_id: str
    docs_gate_status: str
    authority_surfaces: list[str]
    public_mode: RenderMode
    claim_surface: ClaimSurface
    audience_profile: AudienceProfile
    register_profile: RegisterProfile
    interface_contract: InterfaceContract
    message_envelope: MessageEnvelope
    translation_surface: TranslationSurface
    domain_pack: DomainPack
    release_bundle: ReleaseBundle
    safe_wording_bundle: SafeWordingBundle
    kairos_assessment: KairosAssessment
    rhetorical_preview: RhetoricalPreview
    validator_result: SemanticExportValidatorResult
    audience_facing_bundle: AudienceFacingBundle


def render_mode_for_claim_class(claim_class: ClaimClass) -> RenderMode:
    return RENDER_POLICY_MAP[claim_class]


def apply_safe_wording(raw_text: str, safe_wording_bundle: SafeWordingBundle) -> tuple[str, list[str]]:
    wording = raw_text
    downgraded: list[str] = []
    for source, replacement in safe_wording_bundle.downgrade_replacements.items():
        if source in wording:
            wording = wording.replace(source, replacement)
            downgraded.append(f"{source} -> {replacement}")
    return wording, downgraded


def validate_semantic_export(
    claim_surface: ClaimSurface,
    audience_profile: AudienceProfile,
    register_profile: RegisterProfile,
    interface_contract: InterfaceContract,
    message_envelope: MessageEnvelope,
    translation_surface: TranslationSurface,
    domain_pack: DomainPack,
    safe_wording_bundle: SafeWordingBundle,
    rhetorical_preview: RhetoricalPreview,
) -> SemanticExportValidatorResult:
    blocked: list[str] = []
    expected_mode = render_mode_for_claim_class(claim_surface.claim_class)
    if translation_surface.render_mode != expected_mode:
        blocked.append(
            f"render mode drift: expected {expected_mode.value}, received {translation_surface.render_mode.value}"
        )
    if claim_surface.claim_class == ClaimClass.RHETORICAL:
        blocked.append("rhetorical claim class is preview-only in v1")
    if register_profile.name not in audience_profile.allowed_registers:
        blocked.append(
            f"register {register_profile.name.value} is not admissible for audience {audience_profile.audience_type.value}"
        )
    if audience_profile.audience_type != interface_contract.allowed_audience:
        blocked.append("audience does not match interface contract")
    if register_profile.name != interface_contract.allowed_register:
        blocked.append("register does not match interface contract")
    if len(claim_surface.support_refs) < interface_contract.required_support_refs:
        blocked.append("missing support refs")
    if len(claim_surface.replay_refs) < interface_contract.required_replay_refs:
        blocked.append("missing replay refs")
    if not safe_wording_bundle.downgrade_replacements:
        blocked.append("missing downgrade replacements")
    if not message_envelope.replay_surface:
        blocked.append("message envelope is missing replay surface")
    lowered_wording = translation_surface.wording.lower()
    blocked_phrases = safe_wording_bundle.blocked_phrases + claim_surface.forbidden_claims + domain_pack.blocked_terms
    for phrase in blocked_phrases:
        if phrase.lower() in lowered_wording:
            blocked.append(f"wording exceeds allowed ceiling via phrase: {phrase}")
    if audience_profile.audience_type != AudienceType.INTERNAL_RESEARCH and register_profile.name == RegisterName.RHETORICAL:
        blocked.append("rhetorical/public renders are blocked in v1")
    if not rhetorical_preview.preview_only:
        blocked.append("rhetorical preview lost preview-only status")
    if audience_profile.audience_type == AudienceType.BENCHMARK_READER:
        if not translation_surface.benchmark_names:
            blocked.append("benchmark-facing surface is missing benchmark-safe names")
        elif not set(translation_surface.benchmark_names).issubset(set(safe_wording_bundle.benchmark_safe_names)):
            blocked.append("benchmark-facing surface uses non-benchmark-safe names")
    if audience_profile.audience_type == AudienceType.FEDERATION_PARTNER:
        if not translation_surface.federation_terms:
            blocked.append("federation-facing surface is missing federation-safe terms")
        elif not set(translation_surface.federation_terms).issubset(set(safe_wording_bundle.federation_safe_names)):
            blocked.append("federation-facing surface uses non-federation-safe terms")
    proof = (
        f"claim={claim_surface.claim_class.value}; ceiling={claim_surface.claim_ceiling.value}; "
        f"mode={translation_surface.render_mode.value}; audience={audience_profile.audience_type.value}; "
        f"register={register_profile.name.value}; replay_refs={len(claim_surface.replay_refs)}; "
        f"support_refs={len(claim_surface.support_refs)}"
    )
    payload = {
        "claim_surface": claim_surface,
        "audience_profile": audience_profile,
        "register_profile": register_profile,
        "interface_contract": interface_contract,
        "message_envelope": message_envelope,
        "translation_surface": translation_surface,
        "domain_pack": domain_pack,
        "safe_wording_bundle": safe_wording_bundle,
        "rhetorical_preview": rhetorical_preview,
        "blocked_reasons": blocked,
        "claim_ceiling_proof": proof,
    }
    return SemanticExportValidatorResult(
        status=ValidationStatus.PASS if not blocked else ValidationStatus.FAIL,
        public_allowed=not blocked,
        blocked_reasons=blocked,
        downgraded_phrases=[],
        replay_refs=list(claim_surface.replay_refs),
        claim_ceiling_proof=proof,
        normalized_hash=stable_hash(payload),
    )

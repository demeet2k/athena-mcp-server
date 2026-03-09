from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Verdict(str, Enum):
    OK = "OK"
    NEAR = "NEAR"
    AMBIG = "AMBIG"
    FAIL = "FAIL"


class Mode(str, Enum):
    ROUTE = "ROUTE"
    OBSERVE_IMAGE = "OBSERVE_IMAGE"
    OBSERVE_AUDIO = "OBSERVE_AUDIO"
    OBSERVE_DOC = "OBSERVE_DOC"
    PLAN_TOOL = "PLAN_TOOL"
    VERIFY = "VERIFY"
    PATCH = "PATCH"
    ABSTAIN = "ABSTAIN"
    ESCALATE = "ESCALATE"


@dataclass
class QueryBody:
    raw_input: str
    canonical_problem: str
    task_class: str
    output_type: str
    required_fields: List[str] = field(default_factory=list)


@dataclass
class ZeroPointNormalization:
    anchor: str = "balanced"
    assumptions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class CandidateRoute:
    route_id: str
    lens: str
    steps: List[str]
    score: float = 0.0
    evidence_record_ids: List[str] = field(default_factory=list)
    admissible: bool = True
    risks: List[str] = field(default_factory=list)


@dataclass
class EvidenceRef:
    record_id: str
    relative_path: str
    kind: str
    score: float
    locator: str = ""
    excerpt: str = ""
    heading: str = ""
    sha256: str = ""
    text_hash: str = ""


@dataclass
class WitnessBundle:
    evidence_trace: List[str] = field(default_factory=list)
    evidence_refs: List[EvidenceRef] = field(default_factory=list)
    contradiction_free: bool = True
    invariants: Dict[str, bool] = field(default_factory=dict)
    replay_hash: str = ""


@dataclass
class CollapseRecord:
    strategy: str = "witness_gated_collapse"
    selected_route_id: Optional[str] = None
    verdict: Verdict = Verdict.AMBIG
    rationale: str = ""
    residuals: List[str] = field(default_factory=list)


@dataclass
class TriLockSection:
    identity_lock: bool = False
    admissibility_lock: bool = False
    replay_lock: bool = False


@dataclass
class PrimeSealSection:
    stability_runs: int = 0
    pass_count: int = 0
    tolerance: float = 0.02


@dataclass
class PatchDelta:
    additions: List[str] = field(default_factory=list)
    updates: List[str] = field(default_factory=list)
    removals: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class SkillObservation:
    name: str
    role: str
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    corpus_fit: float = 0.0


@dataclass
class ImprovementOpportunity:
    title: str
    priority: str
    target: str
    rationale: str
    suggested_skill: str = ""
    suggested_artifact: str = ""


@dataclass
class RoutePacket:
    packet_id: str
    created_at: str
    source_atlas: str
    task_class: str
    mode: Mode
    query: QueryBody
    zero_point_normalization: ZeroPointNormalization
    lens_init: Dict[str, Any]
    candidate_routes: List[CandidateRoute] = field(default_factory=list)
    witness: WitnessBundle = field(default_factory=WitnessBundle)
    collapse: CollapseRecord = field(default_factory=CollapseRecord)
    tri_lock: TriLockSection = field(default_factory=TriLockSection)
    prime_seal: PrimeSealSection = field(default_factory=PrimeSealSection)
    patch: Optional[PatchDelta] = None
    skill_synthesis: List[SkillObservation] = field(default_factory=list)
    improvement_opportunities: List[ImprovementOpportunity] = field(default_factory=list)
    next_self_prompt: str = ""

    @staticmethod
    def new(
        raw_input: str,
        canonical_problem: str,
        task_class: str = "framework_build",
        output_type: str = "structured_markdown",
        source_atlas: str = "athena_agent_workspace",
        mode: Mode = Mode.ROUTE,
    ) -> "RoutePacket":
        query = QueryBody(
            raw_input=raw_input,
            canonical_problem=canonical_problem,
            task_class=task_class,
            output_type=output_type,
            required_fields=[
                "QueryBody",
                "CandidateRoutes",
                "WitnessBundle",
                "CollapseRecord",
                "PatchDelta_or_Abstention",
                "SkillSynthesis",
                "ImprovementOpportunities",
                "NextSelfPrompt",
            ],
        )
        return RoutePacket(
            packet_id=str(uuid.uuid4()),
            created_at=utc_now_iso(),
            source_atlas=source_atlas,
            task_class=task_class,
            mode=mode,
            query=query,
            zero_point_normalization=ZeroPointNormalization(),
            lens_init={},
        )

    def compute_replay_hash(self) -> str:
        payload = {
            "source_atlas": self.source_atlas,
            "query": asdict(self.query),
            "routes": [asdict(r) for r in self.candidate_routes],
            "witness_evidence_refs": [asdict(ref) for ref in self.witness.evidence_refs],
            "collapse": asdict(self.collapse),
            "patch": asdict(self.patch) if self.patch else None,
        }
        blob = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

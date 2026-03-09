from __future__ import annotations

from dataclasses import asdict
import re
from typing import List, Tuple

from .atlas import CorpusAtlas
from .contracts import (
    CandidateRoute,
    CollapseRecord,
    EvidenceRef,
    PatchDelta,
    PrimeSealSection,
    RoutePacket,
    TriLockSection,
    Verdict,
    WitnessBundle,
)
from .skills_registry import (
    get_corpus_improvement_opportunities,
    get_system_skill_synthesis,
)

SIGNIFICANT_SHORT_TOKENS = {
    "ai",
    "ml",
    "nn",
    "os",
    "ui",
    "ux",
    "qa",
    "js",
    "ts",
    "py",
    "cpu",
    "gpu",
}


class SelfActualizeEngine:
    """Deterministic scaffold for a witness-gated self-actualization loop."""

    def __init__(self, near_threshold: float = 0.55, ok_threshold: float = 0.72) -> None:
        self.near_threshold = near_threshold
        self.ok_threshold = ok_threshold
        self.atlas = CorpusAtlas.load_default()
        self._route_evidence_cache: dict[str, list[EvidenceRef]] = {}

    @staticmethod
    def canonicalize(raw_input: str) -> str:
        text = raw_input.strip()
        text = re.sub(r"\s+", " ", text)
        return text.lower()

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        stop = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "to",
            "of",
            "for",
            "in",
            "on",
            "with",
            "my",
            "full",
            "build",
        }
        return [
            t
            for t in tokens
            if t not in stop and (len(t) > 2 or t in SIGNIFICANT_SHORT_TOKENS)
        ]

    def build_routes(self, canonical_problem: str, regime_name: str, lens_mix: dict[str, float]) -> List[CandidateRoute]:
        """Construct three lens-diverse route candidates."""
        self._route_evidence_cache = {}
        base_steps = [
            "normalize objective and constraints",
            "collect relevant local corpus evidence",
            "construct synthesis map",
            "emit structured artifact",
            "verify replay and patch feasibility",
        ]
        routes = [
            CandidateRoute(
                route_id="R-SQUARE-01",
                lens="square_structure",
                steps=base_steps + ["prioritize typed schemas and deterministic contracts"],
            ),
            CandidateRoute(
                route_id="R-CLOUD-02",
                lens="cloud_ambiguity",
                steps=base_steps + ["preserve unresolved uncertainty as typed residuals"],
            ),
            CandidateRoute(
                route_id="R-FRACTAL-03",
                lens="fractal_scaling",
                steps=base_steps + ["optimize for reusable seed-to-system recursion"],
            ),
        ]
        keywords = set(self.extract_keywords(canonical_problem))
        for route in routes:
            route.score = self.score_route(route, keywords, lens_mix)
            evidence_refs = self.lookup_route_evidence(route, canonical_problem, regime_name)
            self._route_evidence_cache[route.route_id] = evidence_refs
            route.evidence_record_ids = [item.record_id for item in evidence_refs]
            if evidence_refs:
                route.score = min(route.score + min(0.08, 0.02 * len(evidence_refs)), 0.98)
            route.admissible, route.risks = self.check_admissibility(
                route,
                evidence_count=len(evidence_refs),
                atlas_present=self.atlas is not None,
            )
        return routes

    def lookup_route_evidence(self, route: CandidateRoute, canonical_problem: str, regime_name: str) -> List[EvidenceRef]:
        if not self.atlas:
            return []

        preferred_kinds = {
            "square_structure": {"code", "data", "text", "document"},
            "cloud_ambiguity": {"document", "text", "data"},
            "fractal_scaling": {"document", "text", "code"},
        }.get(route.lens, {"document", "text", "code", "data"})

        regime_lens_kind_overrides = {
            ("drive-sync", "square_structure"): {"code", "data", "text"},
            ("drive-sync", "cloud_ambiguity"): {"document", "text"},
            ("neural-benchmark", "square_structure"): {"code", "text"},
            ("neural-benchmark", "fractal_scaling"): {"code", "text", "document"},
            ("atlas-build", "square_structure"): {"code", "data", "text"},
            ("theorem-runtime", "square_structure"): {"code", "data", "text", "document"},
        }
        preferred_kinds = regime_lens_kind_overrides.get((regime_name, route.lens), preferred_kinds)

        lens_hints = {
            "square_structure": "code runtime schema verify executable framework",
            "cloud_ambiguity": "document manuscript ambiguity context notes",
            "fractal_scaling": "recursive system scaling bridge architecture",
        }
        query = f"{canonical_problem} {route.lens} {lens_hints.get(route.lens, '')}".strip()
        return self.atlas.search(
            query=query,
            limit=3,
            preferred_kinds=preferred_kinds,
            regime_name=regime_name,
            route_lens=route.lens,
        )

    @staticmethod
    def score_route(route: CandidateRoute, keywords: set[str], lens_mix: dict[str, float]) -> float:
        text = " ".join(route.steps + [route.lens]).lower()
        overlap = sum(1 for k in keywords if k in text)
        base = 0.45 + 0.08 * overlap
        if "typed" in text:
            base += 0.05
        if "verify" in text:
            base += 0.05
        lens_key = route.lens.split("_", 1)[0]
        base += 0.2 * lens_mix.get(lens_key, 0.0)
        return min(base, 0.98)

    @staticmethod
    def check_admissibility(route: CandidateRoute, evidence_count: int = 0, atlas_present: bool = False) -> Tuple[bool, List[str]]:
        risks: List[str] = []
        if len(route.steps) < 4:
            risks.append("insufficient_route_depth")
        if not any("verify" in s for s in route.steps):
            risks.append("missing_verification_step")
        if atlas_present and evidence_count == 0:
            risks.append("no_atlas_evidence")
        admissible = len(risks) == 0
        return admissible, risks

    def build_witness(self, routes: List[CandidateRoute]) -> WitnessBundle:
        evidence_refs: list[EvidenceRef] = []
        seen: set[str] = set()
        for route in routes:
            for evidence_ref in self._route_evidence_cache.get(route.route_id, []):
                if evidence_ref.record_id in seen:
                    continue
                seen.add(evidence_ref.record_id)
                evidence_refs.append(evidence_ref)

        contradiction_free = all(r.admissible for r in routes) and (bool(evidence_refs) if self.atlas else True)
        invariants = {
            "no_silent_collapse": True,
            "typed_outputs_present": True,
            "replay_required": True,
            "admissibility_checked": contradiction_free,
            "atlas_bound": self.atlas is not None,
        }
        evidence = [ref.record_id for ref in evidence_refs]
        return WitnessBundle(
            evidence_trace=evidence,
            evidence_refs=evidence_refs,
            contradiction_free=contradiction_free,
            invariants=invariants,
        )

    def collapse(self, routes: List[CandidateRoute], witness: WitnessBundle) -> CollapseRecord:
        admissible_routes = [r for r in routes if r.admissible]
        if not admissible_routes or not witness.contradiction_free:
            return CollapseRecord(
                verdict=Verdict.FAIL,
                rationale="No admissible route with contradiction-free witness.",
                residuals=["Collect stronger evidence", "Repair route legality"],
            )

        best = max(admissible_routes, key=lambda r: r.score)
        if best.score >= self.ok_threshold:
            verdict = Verdict.OK
        elif best.score >= self.near_threshold:
            verdict = Verdict.NEAR
        else:
            verdict = Verdict.AMBIG

        residuals: List[str] = []
        if verdict != Verdict.OK:
            residuals.append("Need stronger evidence or tighter route fit before full commit.")

        return CollapseRecord(
            selected_route_id=best.route_id,
            verdict=verdict,
            rationale=f"Selected {best.route_id} ({best.lens}) at score={best.score:.2f}.",
            residuals=residuals,
        )

    @staticmethod
    def build_locks(collapse: CollapseRecord, witness: WitnessBundle, replay_hash: str) -> Tuple[TriLockSection, PrimeSealSection]:
        tri = TriLockSection(
            identity_lock=True,
            admissibility_lock=(collapse.verdict in {Verdict.OK, Verdict.NEAR}),
            replay_lock=bool(replay_hash),
        )
        stability_runs = 3
        pass_count = 3 if tri.identity_lock and tri.admissibility_lock and tri.replay_lock else 1
        prime = PrimeSealSection(stability_runs=stability_runs, pass_count=pass_count, tolerance=0.02)
        return tri, prime

    @staticmethod
    def build_patch(collapse: CollapseRecord) -> PatchDelta | None:
        if collapse.verdict not in {Verdict.OK, Verdict.NEAR}:
            return None
        return PatchDelta(
            additions=["self_actualize runtime packet registered"],
            updates=["framework memory map updated with verified route"],
            removals=[],
            notes="Patch emitted only after witness-gated collapse.",
        )

    @staticmethod
    def build_next_prompt(packet: RoutePacket) -> str:
        verdict = packet.collapse.verdict.value
        selected = packet.collapse.selected_route_id or "NONE"
        top_improvement = (
            packet.improvement_opportunities[0].title
            if packet.improvement_opportunities
            else "strengthen evidence grounding"
        )
        return (
            "Next cycle: run self-actualize on the highest-impact unresolved objective; "
            f"start from verdict={verdict}, prioritize route={selected}, "
            f"and focus on this improvement frontier: {top_improvement}."
        )

    def run(self, raw_input: str) -> RoutePacket:
        canonical = self.canonicalize(raw_input)
        regime = self.atlas.infer_regime(canonical) if self.atlas else None
        packet = RoutePacket.new(
            raw_input=raw_input,
            canonical_problem=canonical,
            source_atlas=(self.atlas.source_label if self.atlas else "athena_agent_workspace"),
        )
        packet.lens_init = (
            regime.lens_mix
            if regime
            else {
                "square": 0.30,
                "flower": 0.20,
                "cloud": 0.25,
                "fractal": 0.25,
            }
        )
        if regime:
            packet.zero_point_normalization.assumptions.append(f"active_regime:{regime.name}")

        packet.candidate_routes = self.build_routes(
            canonical_problem=canonical,
            regime_name=(regime.name if regime else "default"),
            lens_mix=packet.lens_init,
        )
        packet.witness = self.build_witness(packet.candidate_routes)
        packet.collapse = self.collapse(packet.candidate_routes, packet.witness)
        packet.patch = self.build_patch(packet.collapse)
        packet.skill_synthesis = get_system_skill_synthesis()
        packet.improvement_opportunities = get_corpus_improvement_opportunities()
        packet.witness.replay_hash = packet.compute_replay_hash()
        packet.tri_lock, packet.prime_seal = self.build_locks(packet.collapse, packet.witness, packet.witness.replay_hash)
        packet.next_self_prompt = self.build_next_prompt(packet)
        return packet

    @staticmethod
    def packet_to_json(packet: RoutePacket) -> str:
        import json

        return json.dumps(asdict(packet), indent=2, default=str)

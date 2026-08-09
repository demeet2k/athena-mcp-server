from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable

from .cohesion_matchmaking import CohesionMatchmakingRuntime

EVIDENCE_GUARD_VERSION = "COHESION.EVIDENCE.GUARD.1"
EVIDENCE_GUARD_LAW = "PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE != SUFFICIENT_COMPARATIVE_EVIDENCE"


class CohesionEvidenceGuardRuntime(CohesionMatchmakingRuntime):
    """Fail-closed evidence coverage for SOLO-versus-PARTY comparison.

    This guard adds no causal or promotion authority. It only prevents a matched
    descriptive rule from passing when the supplied mission set is incompletely
    paired or when one evidence reference is reused across distinct missions.
    """

    @staticmethod
    def _evidence_usage(samples: Iterable[Dict[str, Any]]) -> Dict[str, set[str]]:
        usage: Dict[str, set[str]] = defaultdict(set)
        for sample in samples:
            mission_id = str(sample.get("mission_id") or "")
            for ref in sample.get("evidence_refs") or []:
                value = str(ref).strip()
                if value:
                    usage[value].add(mission_id)
        return usage

    def _compare_samples(
        self,
        solo_samples: Iterable[Dict[str, Any]],
        party_samples: Iterable[Dict[str, Any]],
        decision_rule: Dict[str, Any],
    ) -> Dict[str, Any]:
        solo_rows = [dict(row) for row in solo_samples]
        party_rows = [dict(row) for row in party_samples]
        result = super()._compare_samples(solo_rows, party_rows, decision_rule)

        additional_reasons = []
        unmatched = sorted(
            set(result.get("unmatched_solo_keys") or [])
            | set(result.get("unmatched_party_keys") or [])
        )
        if unmatched:
            additional_reasons.append("UNMATCHED_MISSION_KEYS")

        usage = self._evidence_usage([*solo_rows, *party_rows])
        reused = sorted(ref for ref, mission_ids in usage.items() if len(mission_ids) > 1)
        if reused:
            additional_reasons.append("DUPLICATE_EVIDENCE_REF")

        reasons = sorted(set(result.get("quality_reasons") or []) | set(additional_reasons))
        result["quality_reasons"] = reasons
        result["evidence_guard"] = {
            "version": EVIDENCE_GUARD_VERSION,
            "complete_match_coverage": not bool(unmatched),
            "unmatched_match_keys": unmatched,
            "unique_evidence_across_missions": not bool(reused),
            "reused_evidence_refs": reused,
            "law": EVIDENCE_GUARD_LAW,
        }
        if reasons:
            result["decision"] = "UNKNOWN_INSUFFICIENT_EVIDENCE"
            result["rule_pass"] = None
            result["standing"] = "UNDERDETERMINED"
        result["causal_effect"] = "UNKNOWN"
        result["promotion_authority"] = False
        return result

    def resource(self) -> Dict[str, Any]:
        value = dict(super().resource())
        laws = list(value.get("laws") or [])
        if EVIDENCE_GUARD_LAW not in laws:
            laws.append(EVIDENCE_GUARD_LAW)
        value["laws"] = laws
        value["evidence_guard_version"] = EVIDENCE_GUARD_VERSION
        value["evidence_guard"] = {
            "unmatched_mission_keys": "UNKNOWN_INSUFFICIENT_EVIDENCE",
            "reused_evidence_ref_across_missions": "UNKNOWN_INSUFFICIENT_EVIDENCE",
            "causal_effect": "UNKNOWN",
            "promotion_authority": False,
        }
        return value

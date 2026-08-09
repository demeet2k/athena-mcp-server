from __future__ import annotations

import unittest

from athena_mcp.cohesion_evidence_guard import CohesionEvidenceGuardRuntime


class CohesionEvidenceGuardTests(unittest.TestCase):
    def setUp(self):
        self.runtime = CohesionEvidenceGuardRuntime(None)

    @staticmethod
    def sample(mission_id, match_key, evidence_ref, verified_delta=10, cost=10):
        return {
            "mission_id": mission_id,
            "match_key": match_key,
            "evidence_refs": [evidence_ref],
            "productive_transition_count": verified_delta,
            "verified_delta": verified_delta,
            "cost": cost,
            "duplicate_actions": 0,
            "stale_actions": 0,
            "human_interrupts": 0,
            "merge_debt": 0,
            "meta_overhead": 0,
            "closure": True,
            "stop_class": "SUCCESS_CLOSED",
            "authority_evidence_violations": 0,
            "wasted_overrun": 0,
        }

    @staticmethod
    def rule(min_pairs=2):
        return {
            "rule_ref": "Athena#192/frozen-evidence-guard-v1",
            "frozen_before_results": True,
            "min_pairs": min_pairs,
            "min_primary_effect": 0.1,
            "max_duplicate_regression": 0,
            "max_stale_regression": 0,
            "max_human_interrupt_regression": 0,
            "max_meta_overhead_regression": 0,
        }

    def test_unmatched_mission_keys_force_unknown_even_when_matched_subset_passes(self):
        solo = [
            self.sample("solo-1", "m1", "receipt://solo-1", 10, 10),
            self.sample("solo-2", "m2", "receipt://solo-2", 10, 10),
        ]
        party = [
            self.sample("party-1", "m1", "receipt://party-1", 20, 10),
            self.sample("party-2", "m2", "receipt://party-2", 20, 10),
            self.sample("party-cherry", "m3", "receipt://party-3", 30, 10),
        ]
        result = self.runtime._compare_samples(solo, party, self.rule(min_pairs=2))
        self.assertEqual(result["decision"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        self.assertIsNone(result["rule_pass"])
        self.assertIn("UNMATCHED_MISSION_KEYS", result["quality_reasons"])
        self.assertEqual(result["evidence_guard"]["unmatched_match_keys"], ["m3"])
        self.assertFalse(result["evidence_guard"]["complete_match_coverage"])
        self.assertEqual(result["causal_effect"], "UNKNOWN")
        self.assertFalse(result["promotion_authority"])

    def test_reused_evidence_across_distinct_missions_forces_unknown(self):
        solo = [
            self.sample("solo-1", "m1", "receipt://shared", 10, 10),
            self.sample("solo-2", "m2", "receipt://solo-2", 10, 10),
        ]
        party = [
            self.sample("party-1", "m1", "receipt://party-1", 20, 10),
            self.sample("party-2", "m2", "receipt://shared", 20, 10),
        ]
        result = self.runtime._compare_samples(solo, party, self.rule(min_pairs=2))
        self.assertEqual(result["decision"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        self.assertIn("DUPLICATE_EVIDENCE_REF", result["quality_reasons"])
        self.assertEqual(result["evidence_guard"]["reused_evidence_refs"], ["receipt://shared"])
        self.assertFalse(result["evidence_guard"]["unique_evidence_across_missions"])
        self.assertEqual(result["causal_effect"], "UNKNOWN")

    def test_complete_unique_evidence_preserves_descriptive_rule_pass(self):
        solo = [
            self.sample("solo-1", "m1", "receipt://solo-1", 10, 10),
            self.sample("solo-2", "m2", "receipt://solo-2", 10, 10),
        ]
        party = [
            self.sample("party-1", "m1", "receipt://party-1", 20, 10),
            self.sample("party-2", "m2", "receipt://party-2", 20, 10),
        ]
        result = self.runtime._compare_samples(solo, party, self.rule(min_pairs=2))
        self.assertEqual(result["decision"], "PARTY_RULE_PASS_DESCRIPTIVE")
        self.assertTrue(result["rule_pass"])
        self.assertEqual(result["quality_reasons"], [])
        self.assertTrue(result["evidence_guard"]["complete_match_coverage"])
        self.assertTrue(result["evidence_guard"]["unique_evidence_across_missions"])
        self.assertEqual(result["causal_effect"], "UNKNOWN")
        self.assertFalse(result["promotion_authority"])


if __name__ == "__main__":
    unittest.main()

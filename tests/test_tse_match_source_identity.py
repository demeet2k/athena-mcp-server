from __future__ import annotations

import unittest

from athena_mcp.tse_telemetry_proxy import TseHelixTelemetryProxy


class TseMatchSourceIdentityTests(unittest.TestCase):
    def test_advisory_match_identity_ignores_observer_head_drift(self):
        def packet(head):
            return TseHelixTelemetryProxy._stable_source_kwargs(
                {
                    "source_kind": "COHESION_ADVISORY_MATCH",
                    "source_ref": f"MATCH-OLD-{head}",
                    "attempt_ref": f"MATCH-OLD-{head}",
                    "source_payload": {
                        "selected_match": {
                            "agent_id": "beta",
                            "offer_id": "OFFER.1",
                            "score": 7.0,
                            "coordination_treatment": "NO_EXACT_COLLISION",
                            "reason_codes": ["FULL_CAPABILITY_FIT"],
                            "match_git_head": head,
                        },
                        "need_id": "NEED.1",
                        "match_git_head": head,
                        "route": {
                            "route_id": "TSE.ROUTE.1",
                            "route_digest": "sha256:" + "a" * 64,
                            "hatch_id": "HATCH.1",
                            "hatch_digest": "sha256:" + "b" * 64,
                            "parent_checkpoint_digest": "sha256:" + "c" * 64,
                        },
                    },
                    "source_git_head": head,
                }
            )

        left = packet("HEAD-A")
        right = packet("HEAD-B")
        self.assertEqual(left["source_payload"], right["source_payload"])
        self.assertEqual(left["source_ref"], right["source_ref"])
        self.assertEqual(left["attempt_ref"], right["attempt_ref"])
        self.assertTrue(left["source_ref"].startswith("MATCH-"))
        self.assertIsNone(left["source_git_head"])
        self.assertIsNone(right["source_git_head"])


if __name__ == "__main__":
    unittest.main()

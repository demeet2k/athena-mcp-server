from __future__ import annotations

import unittest

from athena_mcp import protocol
from athena_mcp.synapse_observer import TOOL_NAME, build_synapse_map


class SynapseObserverTests(unittest.TestCase):
    def test_tool_surface_is_registered(self):
        names = {tool["name"] for tool in protocol.TOOLS}
        self.assertIn(TOOL_NAME, names)

    def test_cross_plane_join_preserves_identity_boundary(self):
        board = {
            "status": "OK",
            "shared_frontier_verified": True,
            "active": [
                {
                    "agent_id": "alpha",
                    "claim_id": "MBC-1",
                    "mode": "PRIMARY",
                    "task": "build synapse",
                    "work_key": "synapse",
                    "targets": ["x.py"],
                    "expires_at": "later",
                }
            ],
            "exact_overlaps": [],
            "potential_overlaps": [],
        }
        liminal = {
            "active_presence": [
                {
                    "agent_id": "alpha",
                    "instance_id": "proc-9",
                    "session_epoch": "epoch-2",
                    "activity": "WORKING",
                    "focus": "tool:x",
                    "work_refs": ["work_key:synapse"],
                }
            ]
        }
        result = build_synapse_map(board, liminal)
        self.assertEqual(result["agents"][0]["standing"], "CROSS_PLANE_VISIBLE")
        self.assertEqual(result["agents"][0]["identity_join"], "AGENT_ID_ONLY_NOT_PROCESS_IDENTITY")
        self.assertEqual(result["metrics"]["cross_plane_visible"], 1)

    def test_liminal_only_is_gap_not_proof_of_unclaimed_work(self):
        result = build_synapse_map(
            {"status": "OK", "shared_frontier_verified": True, "active": []},
            {"active_presence": [{"agent_id": "alpha", "activity": "WORKING"}]},
        )
        gap = result["observability_gaps"][0]
        self.assertEqual(gap["kind"], "EPHEMERAL_ONLY_NO_DURABLE_CLAIM")
        self.assertIn("does not prove", gap["interpretation"])
        self.assertEqual(result["metrics"]["liminal_only"], 1)

    def test_durable_only_is_unobserved_not_process_absence(self):
        result = build_synapse_map(
            {
                "status": "OK",
                "shared_frontier_verified": True,
                "active": [{"agent_id": "alpha", "claim_id": "MBC-1"}],
            },
            {"active_presence": []},
        )
        gap = result["observability_gaps"][0]
        self.assertEqual(gap["kind"], "DURABLE_CLAIM_NO_OBSERVED_LIMINAL_PRESENCE")
        self.assertIn("unobserved", gap["interpretation"])
        self.assertEqual(result["metrics"]["durable_only"], 1)

    def test_liminal_topology_edges_are_typed_and_non_authoritative(self):
        result = build_synapse_map(
            {"status": "OK", "shared_frontier_verified": True, "active": []},
            {
                "active_presence": [
                    {
                        "agent_id": "alpha",
                        "object_refs": ["OID:Shared"],
                        "semantic_tags": ["proof"],
                    },
                    {
                        "agent_id": "beta",
                        "object_refs": [" oid:shared "],
                        "semantic_tags": ["different"],
                    },
                ]
            },
        )
        edge = result["liminal_topology_edges"][0]
        self.assertEqual(edge["agents"], ["alpha", "beta"])
        self.assertIn("object_refs:oid:shared", edge["shared_route_atoms"])
        self.assertEqual(edge["standing"], "TOPOLOGICAL_RENDEZVOUS_POTENTIAL_ONLY")

    def test_selected_unread_messages_are_not_globalized(self):
        board = {
            "status": "OK",
            "shared_frontier_verified": True,
            "active": [],
            "unread_messages": [{"event_id": "MBE-9"}],
        }
        selected = build_synapse_map(board, {"active_presence": []}, agent_id="alpha")
        global_view = build_synapse_map(board, {"active_presence": []})
        self.assertEqual(selected["metrics"]["selected_unread"], 1)
        self.assertEqual(global_view["selected_unread_messages"], [])

    def test_unverified_durable_frontier_qualifies_observer_status(self):
        result = build_synapse_map(
            {
                "status": "OK_UNVERIFIED",
                "shared_frontier_verified": False,
                "active": [],
            },
            {"active_presence": []},
        )
        self.assertFalse(result["shared_frontier_verified"])
        self.assertEqual(result["durable_view_status"], "OK_UNVERIFIED")
        self.assertEqual(result["status"], "OK")
        self.assertIn("SHARED_FRONTIER_UNVERIFIED => DURABLE_VIEW_QUALIFIED", result["laws"])

    def test_synapse_return_metrics_are_projected_without_receipt_payloads(self):
        result = build_synapse_map(
            {"status": "OK", "shared_frontier_verified": True, "active": []},
            {
                "active_presence": [],
                "synapse_return": {
                    "bridge_receipt_count": 7,
                    "bridge_receipts": [{"secret": "not projected"}],
                    "cross_restart_deduplication": False,
                },
            },
        )
        self.assertEqual(result["synapse_return"]["bridge_receipt_count"], 7)
        self.assertNotIn("bridge_receipts", result["synapse_return"])


if __name__ == "__main__":
    unittest.main()

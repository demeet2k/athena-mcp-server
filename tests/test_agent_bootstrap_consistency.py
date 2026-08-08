from __future__ import annotations

import unittest

from athena_mcp.agent_bootstrap_consistency import (
    _selection_from_packet,
    install_bootstrap_consistency,
)


class AgentBootstrapConsistencyTests(unittest.TestCase):
    def test_selection_is_bound_to_exact_returned_frontier_digest(self):
        frontier = {
            "status": "HYDRATED",
            "frontier_digest": "frontier-v1",
            "ready_work": [
                {
                    "node_id": "dominant",
                    "priority": 100,
                    "dependency_release": 3,
                    "attempts_remaining": 2,
                },
                {
                    "node_id": "dominated",
                    "priority": 50,
                    "dependency_release": 1,
                    "attempts_remaining": 1,
                },
            ],
        }
        selected = _selection_from_packet(frontier)
        self.assertEqual(selected["status"], "SELECTED")
        self.assertEqual(selected["selected"]["node_id"], "dominant")
        self.assertEqual(selected["bound_frontier_digest"], "frontier-v1")

    def test_installer_replaces_mixed_snapshot_selection(self):
        class DummyRuntime:
            def bootstrap(self, *args, **kwargs):
                return {
                    "frontier": {
                        "status": "HYDRATED",
                        "frontier_digest": "packet-frontier",
                        "ready_work": [
                            {
                                "node_id": "packet-node",
                                "priority": 1,
                                "dependency_release": 0,
                                "attempts_remaining": 1,
                            }
                        ],
                    },
                    "next_frontier": {
                        "status": "SELECTED",
                        "selected": {"node_id": "different-fetch-node"},
                    },
                    "laws": [],
                }

        install_bootstrap_consistency(DummyRuntime)
        packet = DummyRuntime().bootstrap()
        self.assertEqual(packet["next_frontier"]["selected"]["node_id"], "packet-node")
        self.assertEqual(packet["selection_snapshot_digest"], "packet-frontier")
        self.assertIn(
            "NEXT_FRONTIER_SELECTION_BOUND_TO_RETURNED_FRONTIER_DIGEST",
            packet["laws"],
        )


if __name__ == "__main__":
    unittest.main()

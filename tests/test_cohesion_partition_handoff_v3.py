from __future__ import annotations

import unittest

from athena_mcp.cohesion_duplicate_guard import _partition_packet
from athena_mcp.cohesion_partition_handoff_v3 import CohesionPartitionHandoffRuntimeV3


class CohesionPartitionHandoffV3Tests(unittest.TestCase):
    def test_shared_sink_partition_projects_structurally_valid_c3_proof(self):
        partition = {
            "partition_id":"PART.C3",
            "packets":[
                {
                    "packet_id":"A",
                    "targets":["src/a.py#f","src/index.py#registry"],
                    "shared_sinks":["src/index.py#registry"],
                    "exact_refs":["git://a","test://a"],
                },
                {
                    "packet_id":"B",
                    "targets":["src/b.py#g","src/index.py#registry"],
                    "shared_sinks":["src/index.py#registry"],
                    "exact_refs":["git://b","test://b"],
                },
            ],
            "proof":{
                "serialization_edges":[{
                    "from":"A","to":"B","shared_sinks":["src/index.py#registry"]
                }]
            },
        }
        adapters = CohesionPartitionHandoffRuntimeV3._c3_adapters(partition)
        self.assertEqual(len(adapters),1)
        adapter = adapters[0]
        self.assertTrue(adapter["eligible"],adapter)
        self.assertFalse(adapter["independently_verified"])
        proof = adapter["partition_proof"]
        c3 = _partition_packet(proof,["src/index.py#registry"])
        self.assertTrue(c3["structurally_valid"],c3)
        self.assertTrue(c3["covers_all_target_collisions"],c3)
        self.assertTrue(c3["eligible_for_target_partition"],c3)
        self.assertFalse(c3["independently_verified"])
        self.assertEqual(
            c3["disjoint_targets"],
            ["src/a.py#f","src/b.py#g"],
        )

    def test_adapter_refuses_to_overstate_weak_partition(self):
        partition = {
            "partition_id":"PART.WEAK",
            "packets":[
                {"packet_id":"A","targets":["sink"],"exact_refs":[]},
                {"packet_id":"B","targets":["sink"],"exact_refs":[]},
            ],
            "proof":{"serialization_edges":[{"from":"A","to":"B","shared_sinks":["sink"]}]},
        }
        adapter = CohesionPartitionHandoffRuntimeV3._c3_adapters(partition)[0]
        self.assertFalse(adapter["eligible"])
        self.assertIn("C3_ADAPTER_REQUIRES_TWO_DISJOINT_TARGETS",adapter["reason_codes"])
        self.assertIn("C3_ADAPTER_REQUIRES_EVIDENCE_REFS",adapter["reason_codes"])
        c3 = _partition_packet(adapter["partition_proof"],["sink"])
        self.assertFalse(c3["structurally_valid"])
        self.assertFalse(c3["eligible_for_target_partition"])

    def test_resource_names_party_v3_and_never_claims_independent_verification(self):
        runtime = CohesionPartitionHandoffRuntimeV3(None)
        resource = runtime.resource()
        bridge = resource["partition_handoff_v3_bridge"]
        self.assertIn("PARTY.REWARD.PROVENANCE.3",bridge["party_context"])
        self.assertIn("independently_verified=false",bridge["c3_adapter"])
        self.assertIn("PARTITION_PROOF != CLEAR_EXACT_WORK_IDENTITY",resource["laws"])


if __name__ == "__main__":
    unittest.main()

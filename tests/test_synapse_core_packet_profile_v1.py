from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from athena_mcp.synapse_liminal_adapter import SynapseLiminalError, synapse_to_liminal_ingress_plan

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "athena_core_synapse_packet_envelope_v1.json"


class CoreSynapsePacketIngressTests(unittest.TestCase):
    def vector(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def plan(self, envelope=None, *, agent_id="agent-mcp"):
        vector = self.vector()
        return synapse_to_liminal_ingress_plan(
            copy.deepcopy(envelope if envelope is not None else vector["envelope"]),
            agent_id=agent_id,
        )

    def test_core_packet_profile_compiles_to_expected_proposal_only_plan(self):
        vector = self.vector()
        plan = self.plan(vector["envelope"])
        expected = vector["expected_ingress"]
        emit = plan["emit_args"]
        self.assertEqual(expected["schema"], plan["schema"])
        self.assertEqual(expected["source_event_id"], plan["source_event_id"])
        self.assertEqual(expected["standing"], plan["standing"])
        for field in (
            "agent_id", "message_class", "goal_ref", "payload_ref", "dependency_refs",
            "causal_refs", "object_refs", "recipients", "visibility", "evidence_ceiling",
        ):
            self.assertEqual(expected[field], emit[field], field)

    def test_core_target_domains_do_not_become_local_recipients(self):
        vector = self.vector()
        self.assertEqual(["coord.guild", "transport.mcp"], vector["envelope"]["routing"]["route_keys"])
        plan = self.plan(vector["envelope"])
        self.assertEqual([], plan["emit_args"]["recipients"])
        self.assertNotIn("coord.guild", plan["emit_args"]["recipients"])
        self.assertNotIn("transport.mcp", plan["emit_args"]["recipients"])

    def test_core_return_routes_remain_dependency_refs(self):
        vector = self.vector()
        plan = self.plan(vector["envelope"])
        self.assertEqual(
            vector["envelope"]["routing"]["return_routes"],
            plan["emit_args"]["dependency_refs"],
        )

    def test_foreign_parent_event_ids_become_causal_refs_not_native_parent_fields(self):
        vector = self.vector()
        plan = self.plan(vector["envelope"])
        expected_refs = [f"synapse:{ref}" for ref in vector["envelope"]["causality"]["parent_ids"]]
        self.assertEqual(sorted(expected_refs), plan["emit_args"]["causal_refs"])
        self.assertNotIn("parent_ids", plan["emit_args"])
        self.assertNotIn("reply_to", plan["emit_args"])
        self.assertNotIn("correction_of", plan["emit_args"])
        self.assertNotIn("retraction_of", plan["emit_args"])

    def test_foreign_event_identity_is_source_and_object_ref_not_local_packet_identity(self):
        vector = self.vector()
        event_id = vector["envelope"]["event_id"]
        plan = self.plan(vector["envelope"])
        self.assertEqual(event_id, plan["source_event_id"])
        self.assertEqual([f"synapse:{event_id}"], plan["emit_args"]["object_refs"])
        self.assertNotIn("packet_id", plan["emit_args"])
        self.assertIn("INGRESS_IS_NEW_LIMINAL_SIGNAL_NOT_SOURCE_EVENT_IDENTITY", plan["residuals"])

    def test_core_authority_does_not_raise_liminal_evidence_ceiling(self):
        vector = self.vector()
        self.assertEqual("ZERO_AUTHORITY_INTEROP", vector["envelope"]["semantics"]["authority_class"])
        plan = self.plan(vector["envelope"])
        self.assertEqual("SYNAPSE_ENVELOPE_ROUTING_STATE_ONLY", plan["emit_args"]["evidence_ceiling"])
        self.assertIn("FOREIGN_AUTHORITY != LOCAL_EXECUTION_AUTHORITY", plan["laws"])
        self.assertEqual("PROPOSAL_ONLY_NO_RUNTIME_MUTATION", plan["standing"])

    def test_null_foreign_visibility_normalizes_to_colony(self):
        vector = self.vector()
        self.assertIsNone(vector["envelope"]["routing"]["visibility"])
        plan = self.plan(vector["envelope"])
        self.assertEqual("COLONY", plan["emit_args"]["visibility"])
        self.assertEqual("PROPOSAL_ONLY_NO_RUNTIME_MUTATION", plan["standing"])

    def test_payload_body_tamper_is_rejected_before_ingress_plan(self):
        vector = self.vector()
        bad = copy.deepcopy(vector["envelope"])
        bad["payload"]["body"]["packet"]["oid"] = "OID-forged"
        with self.assertRaisesRegex(SynapseLiminalError, "body digest"):
            self.plan(bad)

    def test_bridge_event_id_tamper_is_rejected_before_ingress_plan(self):
        vector = self.vector()
        bad = copy.deepcopy(vector["envelope"])
        bad["event_id"] = "SYN-forged"
        with self.assertRaisesRegex(SynapseLiminalError, "bridge identity"):
            self.plan(bad)

    def test_empty_target_agent_is_rejected(self):
        with self.assertRaisesRegex(SynapseLiminalError, "target agent_id"):
            self.plan(agent_id="")

    def test_foreign_recipient_namespace_is_never_adopted(self):
        vector = self.vector()
        foreign = copy.deepcopy(vector["envelope"])
        foreign["routing"]["recipients"] = ["athena-core", "foreign:agent"]
        plan = self.plan(foreign)
        self.assertEqual([], plan["emit_args"]["recipients"])
        self.assertIn("FOREIGN_RECIPIENT_NAMESPACE_NOT_ASSUMED", plan["residuals"])

    def test_fixture_nonclaims_match_ingress_standing(self):
        vector = self.vector()
        self.assertEqual(
            {
                "runtime_mutation": False,
                "source_event_consumed": False,
                "execution_authority_minted": False,
            },
            vector["nonclaims"],
        )
        plan = self.plan(vector["envelope"])
        self.assertEqual("PROPOSAL_ONLY_NO_RUNTIME_MUTATION", plan["standing"])


if __name__ == "__main__":
    unittest.main()

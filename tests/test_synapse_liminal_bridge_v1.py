from __future__ import annotations

import copy
import unittest

from athena_mcp import protocol
from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime
from athena_mcp.synapse_liminal_adapter import (
    PACKET_PROFILE,
    RECEIPT_PROFILE,
    SynapseLiminalError,
    liminal_capsule_from_synapse,
    liminal_capsule_to_synapse,
    liminal_receipt_to_synapse,
    synapse_to_liminal_ingress_plan,
)
from athena_mcp.synapse_liminal_extension import SynapseLiminalRuntime
from athena_mcp.synapse_liminal_protocol import SYNAPSE_LIMINAL_TOOL_NAMES

REV = "3dd49cd045c6ae166d17bf224962efbd194dccca"


class FakeClock:
    def __init__(self, value=1000.0):
        self.value = float(value)

    def __call__(self):
        return self.value


class DummyServer:
    git = None


class SynapseLiminalBridgeTests(unittest.TestCase):
    def runtime(self):
        server = DummyServer()
        mesh = LiminalBeaconMeshRuntime(server, clock=FakeClock())
        server._liminal_beacon_mesh_runtime_v1 = mesh
        return server, mesh

    def packet(self, mesh, *, message_class="DISCOVERY", **kwargs):
        mesh.touch("alpha", instance_id="ia", session_epoch="ea", work_refs=["work:mesh"])
        return mesh.emit(
            "alpha",
            message_class,
            kwargs.pop("summary", "cross-repo discovery"),
            work_refs=["work:mesh"],
            **kwargs,
        )["packet"]

    def export(self, capsule, revision=REV, observed="2026-08-24T08:40:00Z"):
        return liminal_capsule_to_synapse(
            capsule,
            source_revision=revision,
            bridge_observed_at=observed,
        )

    def test_manual_surface_is_registered(self):
        names = {tool["name"] for tool in protocol.TOOLS}
        self.assertTrue(SYNAPSE_LIMINAL_TOOL_NAMES <= names)

    def test_public_capsule_projection_declares_full_packet_loss(self):
        _, mesh = self.runtime()
        capsule = self.packet(mesh)
        env = self.export(capsule)
        self.assertEqual(PACKET_PROFILE, env["projection"]["profile"])
        self.assertEqual("LOSSY_AUX", env["projection"]["loss_class"])
        self.assertIn("capabilities", env["projection"]["lost"])
        self.assertIn("_route_keys", env["projection"]["lost"])
        self.assertEqual(capsule, liminal_capsule_from_synapse(env))
        self.assertEqual("UNKNOWN", env["frontier"]["semantics"])

    def test_bridge_identity_ignores_observation_time_but_binds_source_revision(self):
        _, mesh = self.runtime()
        capsule = self.packet(mesh)
        a = self.export(capsule, observed="2026-08-24T08:40:00Z")
        b = self.export(capsule, observed="2030-01-01T00:00:00Z")
        c = self.export(capsule, revision="different-revision")
        self.assertEqual(a["event_id"], b["event_id"])
        self.assertNotEqual(a["event_id"], c["event_id"])

    def test_native_parent_reply_and_correction_become_cross_repo_causal_ids(self):
        _, mesh = self.runtime()
        parent = self.packet(mesh)
        child = mesh.emit(
            "alpha",
            "CORRECTION",
            "parent was wrong",
            work_refs=["work:mesh"],
            parent_ids=[parent["packet_id"]],
            reply_to=parent["packet_id"],
            correction_of=parent["packet_id"],
        )["packet"]
        parent_env = self.export(parent)
        child_env = self.export(child)
        self.assertEqual("CONTRADICTION", child_env["event_type"])
        self.assertEqual([parent_env["event_id"]], child_env["causality"]["parent_ids"])
        self.assertEqual(parent_env["event_id"], child_env["causality"]["reply_to"])
        self.assertEqual(parent_env["event_id"], child_env["causality"]["correction_of"])

    def test_receipt_export_encodes_native_stage_ladder_as_explicit_causality(self):
        _, mesh = self.runtime()
        packet = self.packet(mesh, message_class="DELTA")
        mesh.touch("beta", work_refs=["work:mesh"])
        mesh.rendezvous("beta", scout_quota=0)
        presented = dict(mesh._receipts[("beta", packet["packet_id"])])
        consumed = mesh.receipt("beta", packet["packet_id"], "CONSUMED", consumer_ref="beta:event:1")["receipt"]
        p_env = liminal_receipt_to_synapse(presented, source_revision=REV, bridge_observed_at="2026-08-24T08:41:00Z")
        c_env = liminal_receipt_to_synapse(consumed, source_revision=REV, bridge_observed_at="2020-01-01T00:00:00Z")
        packet_env = self.export(packet)
        self.assertEqual(RECEIPT_PROFILE, c_env["projection"]["profile"])
        self.assertEqual("LOSSLESS", c_env["projection"]["loss_class"])
        self.assertIn(packet_env["event_id"], c_env["causality"]["parent_ids"])
        self.assertIn(p_env["event_id"], c_env["causality"]["parent_ids"])
        self.assertEqual("CONSUMED", c_env["receipt"]["stage"])

    def test_receipt_stage_index_disagreement_is_rejected(self):
        bad = {
            "agent_id": "beta",
            "packet_id": "LBM.x",
            "stage": "CONSUMED",
            "stage_index": 0,
            "updated_at": 1000.0,
            "disposition": None,
            "consumer_ref": None,
            "residual": None,
            "propagation_refs": [],
            "outcome_ref": None,
        }
        with self.assertRaisesRegex(SynapseLiminalError, "stage_index"):
            liminal_receipt_to_synapse(bad, source_revision=REV, bridge_observed_at="2026-08-24T08:42:00Z")

    def test_ingress_plan_does_not_mutate_or_assume_foreign_recipient_namespace(self):
        _, source = self.runtime()
        foreign = self.export(self.packet(source))
        foreign = copy.deepcopy(foreign)
        foreign["routing"]["recipients"] = ["foreign-agent"]
        before = source.state()["packet_count"]
        plan = synapse_to_liminal_ingress_plan(foreign, agent_id="receiver")
        self.assertEqual(before, source.state()["packet_count"])
        self.assertEqual([], plan["emit_args"]["recipients"])
        self.assertIn("FOREIGN_RECIPIENT_NAMESPACE_NOT_ASSUMED", plan["residuals"])
        self.assertEqual("PROPOSAL_ONLY_NO_RUNTIME_MUTATION", plan["standing"])

    def test_foreign_correction_target_is_not_inverted_into_local_packet_parent(self):
        _, source = self.runtime()
        parent = self.packet(source)
        correction = source.emit(
            "alpha", "CORRECTION", "fix", work_refs=["work:mesh"], correction_of=parent["packet_id"]
        )["packet"]
        env = self.export(correction)
        plan = synapse_to_liminal_ingress_plan(env, agent_id="receiver")
        self.assertNotIn("parent_ids", plan["emit_args"])
        self.assertNotIn("correction_of", plan["emit_args"])
        self.assertTrue(any(ref.startswith("synapse:SYN-") for ref in plan["emit_args"]["causal_refs"]))
        self.assertIn("FOREIGN_TARGET_NOT_INVERTED_TO_LOCAL_LIMINAL_PACKET_ID", plan["residuals"])

    def test_tampered_export_body_is_rejected(self):
        _, mesh = self.runtime()
        env = self.export(self.packet(mesh))
        env["payload"]["body"]["summary"] = "tampered"
        with self.assertRaisesRegex(SynapseLiminalError, "digest"):
            liminal_capsule_from_synapse(env)

    def test_export_tool_requires_explicit_source_revision_provenance(self):
        server, mesh = self.runtime()
        packet = self.packet(mesh)
        runtime = SynapseLiminalRuntime(server)
        with self.assertRaisesRegex(ValueError, "SOURCE_REVISION_REQUIRED_HOLD"):
            runtime.call_tool("athena_synapse_liminal_export_packet", {"packet_id": packet["packet_id"]})
        result = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet["packet_id"], "source_revision": REV},
        )
        self.assertEqual("SYNAPSE_PACKET_EXPORTED", result["status"])
        self.assertEqual(REV, result["envelope"]["origin"]["source_revision"])

    def test_export_receipt_tool_reads_without_advancing_native_stage(self):
        server, mesh = self.runtime()
        packet = self.packet(mesh, message_class="DELTA")
        mesh.touch("beta", work_refs=["work:mesh"])
        mesh.rendezvous("beta", scout_quota=0)
        before = dict(mesh._receipts[("beta", packet["packet_id"])])
        result = SynapseLiminalRuntime(server).call_tool(
            "athena_synapse_liminal_export_receipt",
            {"agent_id": "beta", "packet_id": packet["packet_id"], "source_revision": REV},
        )
        after = dict(mesh._receipts[("beta", packet["packet_id"])])
        self.assertEqual(before, after)
        self.assertEqual("PRESENTED", result["envelope"]["receipt"]["stage"])

    def test_plan_is_read_only_but_explicit_ingest_emits_into_existing_liminal_runtime(self):
        _, source = self.runtime()
        env = self.export(self.packet(source))
        target_server, target = self.runtime()
        target.touch("receiver", work_refs=["work:mesh"])
        runtime = SynapseLiminalRuntime(target_server)

        before = target.state()["packet_count"]
        plan = runtime.call_tool("athena_synapse_liminal_plan_ingress", {"agent_id": "receiver", "envelope": env})
        self.assertEqual(before, target.state()["packet_count"])
        self.assertEqual("PROPOSAL_ONLY_NO_RUNTIME_MUTATION", plan["standing"])

        result = runtime.call_tool("athena_synapse_liminal_ingest", {"agent_id": "receiver", "envelope": env})
        self.assertEqual(before + 1, target.state()["packet_count"])
        self.assertEqual("SYNAPSE_INGESTED_TO_LIMINAL", result["status"])
        self.assertEqual("NEW_EPHEMERAL_COORDINATION_SIGNAL_ONLY", result["standing"])


if __name__ == "__main__":
    unittest.main()

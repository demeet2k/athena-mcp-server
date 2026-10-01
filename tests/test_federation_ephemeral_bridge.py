from __future__ import annotations
import unittest

from athena_mcp.federation_ephemeral_bridge import (
    FederationEphemeralBridge,
    FederationEphemeralBridgeSurface,
    assess_advisory_snapshot,
    build_consumption_witness,
    decode_handoff_ref,
    encode_handoff_ref,
    project_post_args,
)
from athena_mcp.federation_ephemeral_bridge_protocol import FEDERATION_EPHEMERAL_RESOURCE,FEDERATION_EPHEMERAL_TOOLS

H="sha256:"+"a"*64
C="sha256:"+"b"*64
A="sha256:"+"c"*64

class FakeRuntime:
    def __init__(self):
        self.last_post=None
        self.poll_result={"packets":[],"next_cursor":0,"cursor_floor":0,"replay_truncated":False,"authority":"NONE"}
    def post(self,args):
        self.last_post=args
        return {"packet_id":"epkt_1","route_state":"ROUTED","cursor":7,"authority":"NONE"}
    def poll(self,args):
        return self.poll_result

class FederationEphemeralBridgeTests(unittest.TestCase):
    def test_ref_roundtrip_preserves_both_digests(self):
        ref=encode_handoff_ref(H,C)
        p=decode_handoff_ref(ref)
        self.assertEqual(p.handoff_digest,H); self.assertEqual(p.source_cursor_digest,C)
        self.assertEqual(p.loss_class,"LOSSY_AUX"); self.assertFalse(p.source_currentness_proven)

    def test_bad_digest_rejected(self):
        with self.assertRaises(ValueError): encode_handoff_ref("sha256:x",C)

    def test_projection_does_not_smuggle_cursor_into_causal_parents(self):
        post,p=project_post_args({"sender_aid":"a","recipient_aids":["b"],"handoff_digest":H,"source_cursor_digest":C,"lamport":4,"causal_parents":["event:1"]})
        self.assertEqual(post["causal_parents"],["event:1"])
        self.assertEqual(post["packet_digest_or_ref"],p.transport_ref)

    def test_bridge_post_routes_but_does_not_admit(self):
        rt=FakeRuntime(); b=FederationEphemeralBridge(rt)
        out=b.post({"sender_aid":"a","recipient_aids":["b"],"handoff_digest":H,"source_cursor_digest":C,"lamport":4})
        self.assertEqual(out["standing"],"ROUTED_REQUIRES_DESTINATION_FEDERATION_CURSOR_ADMISSION")
        self.assertFalse(out["source_currentness_proven"])
        self.assertEqual(rt.last_post["delivery_class"],"MATERIAL_CANDIDATE")

    def test_poll_extracts_only_federation_packets(self):
        rt=FakeRuntime(); rt.poll_result={"packets":[
            {"packet_id":"p1","sender_aid":"a","cursor":5,"route_state":"ROUTED","receipt_stage":None,"packet_digest_or_ref":encode_handoff_ref(H,C)},
            {"packet_id":"p2","sender_aid":"a","cursor":6,"route_state":"ROUTED","receipt_stage":None,"packet_digest_or_ref":"ordinary:ref"},
        ],"next_cursor":6,"cursor_floor":1,"replay_truncated":False,"authority":"NONE"}
        out=FederationEphemeralBridge(rt).poll({"aid":"b","after_cursor":0})
        self.assertEqual(len(out["handoffs"]),1); self.assertEqual(out["non_federation_packet_count"],1)
        self.assertEqual(out["handoffs"][0]["handoff_digest"],H)
        self.assertEqual(out["history_standing"],"BOUNDED_TRANSPORT_SUFFIX_OBSERVED")

    def test_poll_truncation_is_explicit_hold(self):
        rt=FakeRuntime(); rt.poll_result={"packets":[],"next_cursor":10,"cursor_floor":8,"replay_truncated":True,"authority":"NONE"}
        out=FederationEphemeralBridge(rt).poll({"aid":"b","after_cursor":1})
        self.assertEqual(out["history_standing"],"HOLD_TRANSPORT_REPLAY_TRUNCATED")

    def test_snapshot_cursor_never_promotes_to_source_cursor(self):
        a=assess_advisory_snapshot({"authority":"NONE","advisory":True,"next_cursor":11,"cursor_floor":4,"replay_truncated":False})
        self.assertEqual(a["standing"],"ADVISORY_TRANSPORT_CURSOR_ONLY")
        self.assertFalse(a["source_prefix_identity_proven"]); self.assertFalse(a["source_currentness_proven"])

    def test_snapshot_truncation_holds(self):
        a=assess_advisory_snapshot({"authority":"NONE","advisory":True,"next_cursor":11,"cursor_floor":4,"replay_truncated":True})
        self.assertEqual(a["standing"],"HOLD_TRANSPORT_REPLAY_TRUNCATED")

    def test_consumption_witness_requires_external_admission(self):
        w=build_consumption_witness({"handoff_digest":H,"source_cursor_digest":C,"federation_admission_receipt_digest":A,"consumer_ref":"agent:b"})
        self.assertEqual(w["federation_admission_receipt_digest"],A)
        self.assertEqual(w["authority"],"NONE")

    def test_consumption_witness_rejects_free_text_admission(self):
        with self.assertRaises(ValueError):
            build_consumption_witness({"handoff_digest":H,"source_cursor_digest":C,"federation_admission_receipt_digest":"trusted","consumer_ref":"agent:b"})

    def test_surface_routes_three_bridge_tools(self):
        rt=FakeRuntime(); s=FederationEphemeralBridgeSurface(rt)
        handled,out=s.call_tool("athena_ephemeral_federation_post",{"sender_aid":"a","recipient_aids":["b"],"handoff_digest":H,"source_cursor_digest":C,"lamport":4})
        self.assertTrue(handled); self.assertEqual(out["authority"],"NONE")
        handled,_=s.call_tool("not-a-tool",{})
        self.assertFalse(handled)

    def test_protocol_tools_unique_and_resource_bound(self):
        names=[x["name"] for x in FEDERATION_EPHEMERAL_TOOLS]
        self.assertEqual(len(names),3); self.assertEqual(len(names),len(set(names)))
        self.assertTrue(FEDERATION_EPHEMERAL_RESOURCE["uri"].endswith("/v1"))

if __name__=="__main__":unittest.main()

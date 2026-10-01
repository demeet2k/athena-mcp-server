from __future__ import annotations

import tempfile
import unittest

from athena_mcp.ephemeral_coordination import EphemeralCoordinationRuntime
from athena_mcp.federation_ephemeral_bridge import FederationEphemeralBridge,build_consumption_witness
from athena_mcp.store import Store

H="sha256:"+"a"*64
C="sha256:"+"b"*64
A="sha256:"+"c"*64


class FederationEphemeralBridgeRuntimeTests(unittest.TestCase):
    def _runtime(self,**kwargs):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup)
        store=Store(f"{td.name}/athena.db");self.addCleanup(store.close)
        now=[1000.0]
        runtime=EphemeralCoordinationRuntime(store,clock=lambda:now[0],**kwargs)
        return runtime,now

    def _present(self,runtime,aid="producer"):
        return runtime.present({"aid":aid,"epoch":"e1","ttl_ms":60000,"capabilities":["federation-bridge"],"need_offer_summary":{},"lamport":1,"causal_parents":[],"source_digest":"caller:opaque"})

    def test_real_runtime_route_poll_and_consumption_witness(self):
        runtime,_=self._runtime();self._present(runtime)
        bridge=FederationEphemeralBridge(runtime)
        routed=bridge.post({"sender_aid":"producer","recipient_aids":["consumer"],"handoff_digest":H,"source_cursor_digest":C,"lamport":2,"delivery_class":"NUDGE"})
        self.assertEqual(routed["transport"]["route_state"],"ROUTED")
        observed=bridge.poll({"aid":"consumer","after_cursor":0,"max_items":10,"salience_budget":2.0})
        self.assertEqual(len(observed["handoffs"]),1)
        row=observed["handoffs"][0]
        self.assertEqual(row["handoff_digest"],H);self.assertEqual(row["source_cursor_digest"],C)
        self.assertFalse(row["source_currentness_proven"])
        packet_id=row["packet_id"]
        runtime.receipt({"packet_id":packet_id,"aid":"consumer","stage":"DELIVERED"})
        runtime.receipt({"packet_id":packet_id,"aid":"consumer","stage":"PRESENTED"})
        witness=build_consumption_witness({"handoff_digest":H,"source_cursor_digest":C,"federation_admission_receipt_digest":A,"consumer_ref":"agent:consumer"})
        consumed=runtime.receipt({"packet_id":packet_id,"aid":"consumer","stage":"CONSUMED","witness":witness})
        self.assertEqual(consumed["receipt_standing"],"CALLER_ATTESTED_RUNTIME_RECEIPT")
        self.assertEqual(consumed["authority"],"NONE")

    def test_real_runtime_gc_truncation_remains_transport_hold(self):
        runtime,_=self._runtime(max_events=3);self._present(runtime)
        bridge=FederationEphemeralBridge(runtime)
        for i in range(5):
            h="sha256:"+format(i,"064x")
            bridge.post({"sender_aid":"producer","recipient_aids":["consumer"],"handoff_digest":h,"source_cursor_digest":C,"lamport":i+2,"delivery_class":"NUDGE","salience":0.1})
        observed=bridge.poll({"aid":"consumer","after_cursor":1,"max_items":10,"salience_budget":5.0})
        self.assertTrue(observed["transport_replay_truncated"])
        self.assertEqual(observed["history_standing"],"HOLD_TRANSPORT_REPLAY_TRUNCATED")
        self.assertTrue(all(not row["source_currentness_proven"] for row in observed["handoffs"]))


if __name__=="__main__":unittest.main()

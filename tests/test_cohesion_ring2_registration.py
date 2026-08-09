from __future__ import annotations

import json
import tempfile
import unittest

from athena_mcp.server import Server


class CohesionRing2RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db')
        self.server=Server(self.tmp.name)
        self.seq=0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self,method,params=None):
        self.seq+=1
        message={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:message['params']=params
        return self.server.handle(message)

    def test_ring2_tools_are_additive_over_current_cohesion_and_party_v3(self):
        names={row['name'] for row in self.rpc('tools/list')['result']['tools']}
        for name in [
            'athena_message_board',
            'athena_party_message',
            'athena_party_result',
            'athena_cohesion_request_offer',
            'athena_cohesion_matchmake',
            'athena_cohesion_coalition',
            'athena_cohesion_solo_party_compare',
            'athena_cohesion_duplicate_guard',
            'athena_cohesion_partition',
            'athena_cohesion_handoff',
            'athena_impossible_open',
            'athena_transport_aor_to_collective',
        ]:
            self.assertIn(name,names)

    def test_cohesion_resource_exposes_all_active_membranes(self):
        payload=json.loads(
            self.rpc('resources/read',{'uri':'athena://cohesion/v1'})
            ['result']['contents'][0]['text']
        )
        self.assertEqual(payload['duplicate_guard_version'],'COHESION.DUPLICATE.GUARD.1')
        self.assertEqual(payload['evidence_guard_version'],'COHESION.EVIDENCE.GUARD.1')
        self.assertEqual(
            payload['partition_handoff']['version'],
            'COHESION.PARTITION.HANDOFF.1',
        )
        self.assertEqual(
            payload['partition_handoff_v3_bridge']['version'],
            'COHESION.PARTITION.HANDOFF.V3BRIDGE.1',
        )
        for name in ['athena_cohesion_partition','athena_cohesion_handoff','athena_cohesion_duplicate_guard']:
            self.assertIn(name,payload['tools'])
        laws='\n'.join(payload['laws'])
        for law in [
            'PARTITION_PROPOSAL != ASSIGNMENT',
            'SHARED_SINK => SERIALIZE_UNLESS_PROVEN_DISJOINT',
            'HANDOFF_ROUTE != CONSUMPTION',
            'PARTITION_PROOF != CLEAR_EXACT_WORK_IDENTITY',
            'PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE != SUFFICIENT_COMPARATIVE_EVIDENCE',
        ]:
            self.assertIn(law,laws)


if __name__=='__main__':
    unittest.main()

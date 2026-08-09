import json
import tempfile
import unittest
from pathlib import Path

from athena_mcp.coordination_inventory import COORDINATION_INVENTORY_VERSION,PARTY_REWARD_VERSION
from athena_mcp.coordination_manifest import EFFECTIVE_UNIFIED_MANIFEST_VERSION
from athena_mcp.server import Server
from athena_mcp.unified_manifest import UNIFIED_MANIFEST_VERSION

ROOT=Path(__file__).resolve().parents[1]


class ExactHeadArchitectureConsistencyTests(unittest.TestCase):
    def test_checked_out_release_brain_matches_runtime_coordinates(self):
        notes=(ROOT/'release'/'v3.2.0.md').read_text(encoding='utf-8')
        self.assertIn('UNIFIED.9',notes)
        self.assertIn('UNIFIED.10',notes)
        self.assertIn('ORGAN_INVENTORY.1.1',notes)
        self.assertIn('Party V3.2',notes)
        self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.9')
        self.assertEqual(EFFECTIVE_UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.10')
        self.assertEqual(COORDINATION_INVENTORY_VERSION,'ATHENA.ORGAN.INVENTORY.1.1')
        self.assertEqual(PARTY_REWARD_VERSION,'PARTY.REWARD.PROVENANCE.3.2')

    def test_live_promotion_resource_preserves_trust_and_drift_boundaries(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            try:
                response=srv.handle({'jsonrpc':'2.0','id':1,'method':'resources/read','params':{'uri':'athena://promotion'}})
                payload=json.loads(response['result']['contents'][0]['text'])
                boundary=payload['boundary']
                self.assertIn('MCP caller witness packets',boundary)
                self.assertIn('never independently verified',boundary)
                self.assertIn('architecture drift blocks local promotion readiness',boundary)
                self.assertEqual(payload['architecture_drift']['status'],'PASS',payload['architecture_drift'])
                self.assertEqual(payload['architecture_drift']['organ_inventory_version'],'ATHENA.ORGAN.INVENTORY.1.1')
            finally:
                srv.store.close()

    def test_effective_manifest_extends_scientific_base_on_same_checkout(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            try:
                effective=srv.call_tool('athena_runtime_manifest',{})
                base=json.loads(srv.handle({'jsonrpc':'2.0','id':2,'method':'resources/read','params':{'uri':'athena://manifest'}})['result']['contents'][0]['text'])
                self.assertEqual(base['artifact'],'ATHENA.RUNTIME.UNIFIED.9')
                self.assertEqual(effective['artifact'],'ATHENA.RUNTIME.UNIFIED.10')
                self.assertTrue(set(base['layers']).issubset(set(effective['layers'])))
                self.assertIn('PARTY_REWARD_PROVENANCE_V3_2',effective['layers'])
                self.assertNotIn('PARTY_REWARD_PROVENANCE_V3_2',base['layers'])
            finally:
                srv.store.close()


if __name__=='__main__':unittest.main()

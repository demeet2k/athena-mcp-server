import json,tempfile,unittest
import athena_mcp
from athena_mcp.coordination_inventory import COORDINATION_INVENTORY_VERSION,PARTY_REWARD_VERSION
from athena_mcp.server import Server

class V14ArchitectureDriftTests(unittest.TestCase):
    def test_v14_synthesis_survives_coordination_overlay(self):
        self.assertEqual(athena_mcp.__version__,'3.3.0')
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            try:
                manifest=srv.call_tool('athena_runtime_manifest',{})
                self.assertEqual(manifest['artifact'],'ATHENA.RUNTIME.UNIFIED.11',manifest)
                for layer in ('COLLECTIVE_SYNTHESIS_V14','MESSAGE_BOARD_V1','COHESION_MESH_V1','PARTY_REWARD_PROVENANCE_V3_2','ORGAN_INVENTORY.1','ARCHITECTURE_DRIFT_AUDIT.1'):self.assertIn(layer,manifest['layers'])
                self.assertIn('ATHENA.RUNTIME.UNIFIED.10',manifest['artifact_compat'])
                self.assertIn('collective_v14',manifest['organs']);self.assertIn('coordination',manifest['organs'])
                self.assertEqual(manifest['organs']['coordination']['inventory_version'],COORDINATION_INVENTORY_VERSION)
                self.assertEqual(manifest['organs']['coordination']['party_reward_current'],PARTY_REWARD_VERSION)
            finally:srv.store.close()
    def test_surface_and_drift_are_promotion_relevant(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            try:
                audit=srv.aor_development.integrity.surface_audit(True)
                self.assertEqual(audit['status'],'PASS',audit);self.assertEqual(audit['architecture_drift']['status'],'PASS',audit)
                self.assertEqual(audit['architecture_drift']['organ_inventory_version'],'ATHENA.ORGAN.INVENTORY.1.1')
                ids={r['id'] for r in audit['architecture_drift']['organs'] if r['status']=='PASS'}
                self.assertIn('PARTY_REWARD_PROVENANCE_V3_2',ids)
            finally:srv.store.close()
    def test_architecture_resources_are_visible_and_omega_has_coordination(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            try:
                resources={x['uri'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'resources/list'})['result']['resources']}
                self.assertIn('athena://architecture/inventory',resources);self.assertIn('athena://architecture/drift',resources)
                inv=json.loads(srv.handle({'jsonrpc':'2.0','id':2,'method':'resources/read','params':{'uri':'athena://architecture/inventory'}})['result']['contents'][0]['text']);self.assertEqual(inv['version'],'ATHENA.ORGAN.INVENTORY.1.1')
                omega=srv.aor_development.integrity.state_foundation.omega();self.assertIn('coordination',omega);self.assertEqual(omega['coordination']['party_reward_current'],'PARTY.REWARD.PROVENANCE.3.2')
            finally:srv.store.close()
if __name__=='__main__':unittest.main()

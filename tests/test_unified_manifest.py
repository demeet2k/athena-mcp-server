import json
import tempfile
import unittest

from athena_mcp.server import Server


class UnifiedManifestTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_live_manifest_reports_single_server_full_layers_and_unresolved_boundaries(self):
        manifest=self.tool('athena_runtime_manifest');self.assertEqual(manifest['artifact'],'ATHENA.RUNTIME.UNIFIED.1');self.assertEqual(manifest['runtime_class'],'Server')
        for layer in ['COLLECTIVE_MEMORY_V2','AOR.3','AUTHORITY_Y1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1','AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','SURFACE.2','COMPOSITION.2','PROMOTION.1']:
            self.assertIn(layer,manifest['layers'])
        joined='\n'.join(manifest['invariants']);self.assertIn('UNKNOWN != 0',joined);self.assertIn('pheromone/reuse/popularity != evidence',joined);self.assertIn('reachability/navigation closure != logical or causal proof',joined);self.assertIn('semantic VID CAS != Git HEAD CAS != topology version CAS',joined)
        unresolved={x['id']:x for x in manifest['unresolved']};self.assertEqual(unresolved['QHUG_SEMANTICS']['status'],'UNRESOLVED_UNLESS_REGISTERED_AND_WITNESSED');self.assertIn('directed reachability',unresolved['STRONGER_CLOSURE']['boundary'])
        self.assertEqual(manifest['schema']['target'],2);self.assertEqual(manifest['startup']['status'],'DEGRADED_SCHEMA')

    def test_manifest_updates_live_schema_state_after_migration(self):
        before=self.tool('athena_runtime_manifest');self.assertFalse(before['schema']['up_to_date']);self.tool('athena_schema_migrate');after=self.tool('athena_runtime_manifest');self.assertTrue(after['schema']['up_to_date']);self.assertEqual(after['schema']['current'],2);self.assertEqual(after['startup']['status'],'READY_LOCAL')

    def test_maxdev_law_contains_operational_not_decorative_boundaries(self):
        law=self.tool('athena_maxdev_law')['text']
        for phrase in ['RECONSTRUCT through RECONRUN + canonical OMEGA','pheromone/reuse/consensus never become evidence or Y authority','PLANNED != executed','FIELD assembles real residual work','UNKNOWN != 0 and KNOWN != COMPARABLE','AOR ranks eligible comparable candidates','COLLECTIVE organizes HOW','real executor/receipt','semantic VID, Git HEAD and topology version are distinct transaction domains','PROMOTE only the exact head']:
            self.assertIn(phrase,law)

    def test_manifest_resources_are_part_of_surface2(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']};self.assertIn('athena_runtime_manifest',names);self.assertIn('athena_maxdev_law',names);self.assertIn('athena://runtime/unified-manifest',uris);self.assertIn('athena://runtime/maxdev',uris)
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://runtime/unified-manifest'})['result']['contents'][0]['text']);self.assertEqual(payload['artifact'],'ATHENA.RUNTIME.UNIFIED.1');audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['manifest']['status'],'PASS')


if __name__=='__main__':unittest.main()

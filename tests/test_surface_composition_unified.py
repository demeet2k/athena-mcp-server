import json
import tempfile
import unittest

from athena_mcp.composition_integrity import COMPOSITION_VERSION,composition_certificate
from athena_mcp.server import Server
from athena_mcp.surface_contract import REQUIRED_RESOURCES,REQUIRED_TOOLS,SURFACE_VERSION,audit_surface,contract_manifest


class SurfaceCompositionUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_full_mature_union_is_discoverable(self):
        tools={x['name'] for x in self.rpc('tools/list')['result']['tools']};resources={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for group,required in REQUIRED_TOOLS.items():
            self.assertTrue(required<=tools,(group,sorted(required-tools)))
        for group,required in REQUIRED_RESOURCES.items():
            self.assertTrue(required<=resources,(group,sorted(required-resources)))
        manifest=contract_manifest();self.assertEqual(manifest['version'],SURFACE_VERSION);self.assertEqual(manifest['tool_count'],len(set().union(*REQUIRED_TOOLS.values())))

    def test_runtime_surface_audit_passes_with_composition_certificate(self):
        audit=self.tool('athena_surface_audit',{})
        self.assertEqual(audit['version'],SURFACE_VERSION);self.assertEqual(audit['surface_status'],'PASS',audit);self.assertEqual(audit['composition']['version'],COMPOSITION_VERSION);self.assertEqual(audit['composition']['status'],'PASS',audit);self.assertEqual(audit['status'],'PASS',audit)
        self.assertEqual(audit['composition']['runtime_class']['observed_mro'][:2],['Server','object'])
        self.assertTrue(audit['promotion_ready_locally'])

    def test_composition_certificate_requires_single_server_and_every_organ(self):
        cert=composition_certificate(self.server,run_probes=True);self.assertEqual(cert['status'],'PASS',cert)
        self.assertEqual(cert['runtime_class']['expected'],'Server -> object');self.assertEqual(cert['direct_organs']['missing'],[]);self.assertEqual(cert['development_organs']['missing'],[]);self.assertEqual(cert['governance_organs']['missing'],[]);self.assertEqual(cert['probe_status'],'PASS')
        for name in ['collective','collective_memory','branch','authority','equivalence','extraction','retrieval','hug','gap','field','transport','promotion']:
            self.assertEqual(cert['read_only_probes'][name]['status'],'PASS',(name,cert))

    def test_pure_surface_audit_fails_closed_on_missing_mature_tool(self):
        tools=[x['name'] for x in self.rpc('tools/list')['result']['tools']];resources=[x['uri'] for x in self.rpc('resources/list')['result']['resources']]
        tools.remove('athena_topology_apply');audit=audit_surface(tools,resources)
        self.assertEqual(audit['status'],'FAIL');self.assertIn('athena_topology_apply',audit['missing_tools']);self.assertEqual(audit['groups']['collective_v2']['status'],'FAIL')

    def test_surface_resource_contains_contract_and_live_audit(self):
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://surface'})['result']['contents'][0]['text'])
        self.assertEqual(payload['contract']['version'],SURFACE_VERSION);self.assertEqual(payload['audit']['status'],'PASS',payload);self.assertIn('COMPOSITION.2',json.dumps(payload['audit']))
        self.assertIn('necessary but not sufficient',payload['law'])

    def test_benchmark_contains_every_major_metabolism_and_promotion(self):
        bench=self.tool('athena_benchmark',{})
        for key in ['collective_runtime','collective_growth','collective_memory','orchestration_runs','branches','authority_claims','equivalence_pairs','extraction_runs','retrieval_runs','hug_implementations','gap_runs','field_runs','transport_runs','promotion_runs']:
            self.assertIn(key,bench)


if __name__=='__main__':unittest.main()

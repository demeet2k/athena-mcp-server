import json
import tempfile
import unittest

from athena_mcp.field_server import FieldServer
from athena_mcp.surface_contract import REQUIRED_RESOURCES,REQUIRED_TOOLS,SURFACE_VERSION,audit_surface,contract_manifest


class SurfaceContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=FieldServer(self.tmp.name);self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)

    def test_promoted_composed_candidate_satisfies_surface_contract(self):
        tools={x['name'] for x in self.rpc('tools/list')['result']['tools']}
        resources={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        audit=audit_surface(tools,resources)
        self.assertEqual(audit['version'],SURFACE_VERSION)
        self.assertEqual(audit['status'],'PASS',audit)
        self.assertEqual(audit['missing_tools'],[])
        self.assertEqual(audit['missing_resources'],[])
        for group,state in audit['groups'].items():self.assertEqual(state['status'],'PASS',(group,state))

    def test_runtime_surface_audit_matches_direct_audit(self):
        result=self.rpc('tools/call',{'name':'athena_surface_audit','arguments':{}})['result']
        self.assertFalse(result.get('isError'),result)
        audit=result['structuredContent'];self.assertEqual(audit['status'],'PASS',audit)
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://surface'})['result']['contents'][0]['text'])
        self.assertEqual(payload['contract']['version'],SURFACE_VERSION)
        self.assertEqual(payload['audit']['status'],'PASS')
        self.assertEqual(payload['audit']['observed_tool_count'],audit['observed_tool_count'])

    def test_contract_is_grouped_and_additive(self):
        manifest=contract_manifest()
        self.assertGreaterEqual(len(REQUIRED_TOOLS),9)
        self.assertGreaterEqual(len(REQUIRED_RESOURCES),9)
        self.assertEqual(manifest['tool_count'],len(set().union(*REQUIRED_TOOLS.values())))
        self.assertEqual(manifest['resource_count'],len(set().union(*REQUIRED_RESOURCES.values())))
        self.assertIn('field',manifest['required_tools'])
        self.assertIn('aor',manifest['required_resources'])

    def test_missing_mature_organ_fails_audit(self):
        tools={x['name'] for x in self.rpc('tools/list')['result']['tools']};tools.remove('athena_branch_observe')
        resources={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        audit=audit_surface(tools,resources)
        self.assertEqual(audit['status'],'FAIL')
        self.assertIn('athena_branch_observe',audit['missing_tools'])
        self.assertEqual(audit['groups']['branch']['status'],'FAIL')

if __name__=='__main__':unittest.main()

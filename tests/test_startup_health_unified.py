import json
import tempfile
import unittest

from athena_mcp.server import Server


class StartupHealthUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_fresh_runtime_is_explicitly_degraded_schema_but_readable(self):
        health=self.tool('athena_startup_health');self.assertEqual(health['status'],'DEGRADED_SCHEMA',health);self.assertEqual(health['read_policy'],'READS_ALLOWED_WHILE_DEGRADED');self.assertIn('NOT_ENFORCED',health['write_policy'])
        # Compatibility behavior remains explicit: the health classifier does not
        # silently rewrite the mutation policy before such a gate is separately designed.
        self.assertIsNotNone(self.tool('athena_omega_state')['omega_id'])
        self.assertTrue(self.rpc('tools/list')['result']['tools'])

    def test_migration_moves_runtime_to_ready_local(self):
        self.tool('athena_schema_migrate');health=self.tool('athena_startup_health',{'run_replay_samples':True});self.assertEqual(health['status'],'READY_LOCAL',health);self.assertEqual(health['gates']['schema'],'PASS');self.assertEqual(health['gates']['self_test'],'PASS');self.assertIn('external CI/smoke',health['boundary'])

    def test_startup_resource_and_surface_are_composed(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']};self.assertIn('athena_startup_health',names);self.assertIn('athena://startup-health',uris)
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://startup-health'})['result']['contents'][0]['text']);self.assertEqual(payload['version'],'ATHENA.STARTUP.1');self.assertEqual(payload['latest']['status'],'DEGRADED_SCHEMA');audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['startup']['status'],'PASS')


if __name__=='__main__':unittest.main()

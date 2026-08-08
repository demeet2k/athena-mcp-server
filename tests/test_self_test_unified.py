import json
import tempfile
import unittest

from athena_mcp.server import Server


class SelfTestUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_self_test_is_degraded_before_schema_migration_but_surface_is_wired(self):
        health=self.tool('athena_self_test',{'replay_limit':5})
        self.assertEqual(health['gates']['surface'],'PASS',health);self.assertEqual(health['gates']['composition'],'PASS',health);self.assertEqual(health['gates']['schema'],'FAIL',health);self.assertEqual(health['gates']['replay'],'PASS',health);self.assertEqual(health['status'],'DEGRADED');self.assertEqual(health['promotion_eligibility'],'BLOCKED_BY_LOCAL_HEALTH')
        self.assertTrue(all(v['status']=='N/A' for v in health['replay_samples'].values()))

    def test_self_test_passes_local_gates_after_additive_migration(self):
        self.tool('athena_schema_migrate')
        health=self.tool('athena_self_test',{'replay_limit':5})
        self.assertEqual(health['status'],'PASS',health);self.assertEqual(health['gates'],{'surface':'PASS','composition':'PASS','schema':'PASS','omega':'PASS','replay':'PASS'});self.assertEqual(health['promotion_eligibility'],'LOCAL_GATES_READY_EXTERNAL_ATTESTATIONS_STILL_REQUIRED');self.assertIn('does not replace external CI/smoke',health['boundary'])

    def test_persisted_runs_are_sampled_and_replayed(self):
        self.tool('athena_schema_migrate')
        aor=self.tool('athena_orchestrate',{'seed':'S','candidates':[]});field=self.tool('athena_field_compile',{'seed_ref':'seed://selftest','module_outputs':{}});transport=self.tool('athena_transport_alarm_to_gap',{'alarm_ref':'A','alarm_nodes':[{'node':'N'}]});recon=self.tool('athena_reconstruct_state',{'task_ref':'task://selftest','source_refs':['db://local']});cycle=self.tool('athena_cycle_start',{'task_ref':'task://selftest','seed':'S'})
        health=self.tool('athena_self_test',{'replay_limit':10});self.assertEqual(health['status'],'PASS',health)
        self.assertEqual(health['replay_samples']['aor']['status'],'PASS');self.assertEqual(health['replay_samples']['field']['status'],'PASS');self.assertEqual(health['replay_samples']['transport']['status'],'PASS');self.assertEqual(health['replay_samples']['reconstruction']['status'],'PASS');self.assertEqual(health['replay_samples']['cycle']['status'],'PASS')
        self.assertEqual(health['replay_failures'],[])

    def test_real_replay_digest_mismatch_degrades_health(self):
        self.tool('athena_schema_migrate');run=self.tool('athena_transport_alarm_to_gap',{'alarm_ref':'A','alarm_nodes':[{'node':'N'}]})
        with self.server.store.db:self.server.store.db.execute("UPDATE transport_runs SET transport_digest='corrupted' WHERE run_id=?",(run['run_id'],))
        health=self.tool('athena_self_test',{'replay_limit':10});self.assertEqual(health['gates']['replay'],'FAIL',health);self.assertEqual(health['status'],'DEGRADED');self.assertIn('transport',health['replay_failures']);self.assertEqual(health['replay_samples']['transport']['status'],'FAIL')

    def test_self_test_resource_and_surface_contract_are_composed(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']};self.assertIn('athena_self_test',names);self.assertIn('athena://self-test',uris)
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://self-test'})['result']['contents'][0]['text']);self.assertEqual(payload['version'],'ATHENA.SELFTEST.1');self.assertEqual(payload['description']['mode'],'READ_ONLY')
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['self_test']['status'],'PASS');self.assertEqual(audit['composition']['governance_organs']['status'],'PASS');self.assertEqual(audit['composition']['read_only_probes']['self_test']['status'],'PASS')


if __name__=='__main__':unittest.main()

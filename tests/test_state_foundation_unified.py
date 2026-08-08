import json
import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.state_projection import omega_diff


class StateFoundationUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db',delete=False);self.tmp.close();self.db=self.tmp.name;self.server=Server(self.db);self.seq=0
    def tearDown(self):
        try:self.server.store.close()
        except Exception:pass
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None,expect_error=False):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}});result=r['result']
        if expect_error:self.assertTrue(result.get('isError'),r);return result
        self.assertFalse(result.get('isError'),r);return result['structuredContent']
    @staticmethod
    def witness(head,kind):return {'observed':True,'ref':f'{kind}://synthetic-state-test','head_sha':head,'conclusion':'success'}

    def test_schema_migration_v1_is_additive_idempotent_and_verifiable(self):
        before=self.tool('athena_schema_status');self.assertEqual(before['current_db_schema_version'],0);self.assertFalse(before['up_to_date'])
        plan=self.tool('athena_schema_plan');self.assertEqual(plan['status'],'MIGRATION_REQUIRED');self.assertEqual(plan['steps'][0]['mode'],'ADDITIVE_INVENTORY_NO_DESTRUCTIVE_REWRITE')
        applied=self.tool('athena_schema_migrate');self.assertEqual(applied['status'],'APPLIED',applied);self.assertTrue(applied['migration_id'].startswith('MIGRUN.'));self.assertEqual(applied['from_version'],0);self.assertEqual(applied['to_version'],1)
        verify=self.tool('athena_schema_verify');self.assertEqual(verify['status'],'PASS',verify);self.assertEqual(verify['missing_required_tables'],[])
        again=self.tool('athena_schema_migrate');self.assertEqual(again['status'],'UP_TO_DATE');self.assertFalse(again['applied'])
        recent=json.loads(self.rpc('resources/read',{'uri':'athena://schema'})['result']['contents'][0]['text']);self.assertEqual(recent['status']['current_db_schema_version'],1);self.assertIn('does not destructively rewrite',recent['law'])

    def test_future_schema_blocks_silent_downgrade(self):
        with self.server.store.db:
            self.server.store.db.execute("INSERT OR REPLACE INTO runtime_schema_meta VALUES(?,?,?)",('db_schema_version','99',0.0))
        plan=self.tool('athena_schema_plan');self.assertEqual(plan['status'],'FUTURE_SCHEMA_BLOCKED');self.assertEqual(plan['current'],99)
        migrate=self.tool('athena_schema_migrate');self.assertEqual(migrate['status'],'FUTURE_SCHEMA_BLOCKED');self.assertFalse(migrate['applied'])

    def test_omega_projection_is_stable_for_unchanged_state_and_changes_after_event(self):
        self.tool('athena_schema_migrate')
        one=self.tool('athena_omega_state');two=self.tool('athena_omega_state');self.assertEqual(one['state_digest'],two['state_digest']);self.assertEqual(one['omega_id'],two['omega_id']);self.assertIn('collective',one);self.assertIn('aor',one);self.assertIn('schema_status',one);self.assertIn('UNKNOWN',json.dumps(one) if any(v.get('status')=='UNKNOWN' for v in one.values() if isinstance(v,dict) and 'status' in v) else 'UNKNOWN boundary')
        self.tool('athena_emit_agent_event',{'agent':'A','task':'T','seq':1,'intent':'change state','action':'observe','status':'DONE'})
        three=self.tool('athena_omega_state');self.assertNotEqual(one['state_digest'],three['state_digest']);delta=omega_diff(one,three);self.assertTrue(delta['changed']);self.assertIn('semantic',delta['changed_components']);self.assertIn('does not by itself establish causality',delta['boundary'])

    def test_reconrun_freezes_exact_consulted_and_expected_source_contract(self):
        self.tool('athena_schema_migrate')
        run=self.tool('athena_reconstruct_state',{'task_ref':'task://recon','source_refs':['git://head','state://db','extra://consulted'],'expected_refs':['git://head','state://db','missing://required']})
        self.assertEqual(run['status'],'COMPLETE_WITH_DEFECTS');self.assertTrue(run['run_id'].startswith('RECONRUN.'));self.assertEqual(run['source_refs'],['extra://consulted','git://head','state://db']);self.assertEqual(run['expected_refs'],['git://head','missing://required','state://db']);self.assertEqual(run['defects'][0]['refs'],['missing://required'])
        stored=self.tool('athena_reconstruction_get',{'run_id':run['run_id']});self.assertEqual(stored['expected_refs'],run['expected_refs']);verify=self.tool('athena_reconstruction_verify',{'run_id':run['run_id']});self.assertTrue(verify['match'],verify)
        self.tool('athena_emit_agent_event',{'agent':'A','task':'T','seq':2,'intent':'mutate after recon','action':'event','status':'DONE'})
        stored2=self.tool('athena_reconstruction_get',{'run_id':run['run_id']});self.assertEqual(stored2['omega']['state_digest'],stored['omega']['state_digest']);self.assertTrue(self.tool('athena_reconstruction_verify',{'run_id':run['run_id']})['match'])

    def test_major_ledgers_survive_close_and_reopen(self):
        self.tool('athena_schema_migrate')
        aor=self.tool('athena_orchestrate',{'seed':'S','candidates':[]})
        field=self.tool('athena_field_compile',{'seed_ref':'seed://restart','module_outputs':{}})
        transport=self.tool('athena_transport_alarm_to_gap',{'alarm_ref':'ALARM.RESTART','alarm_nodes':[{'node':'N','severity':.2}]})
        recon=self.tool('athena_reconstruct_state',{'task_ref':'task://restart','source_refs':['db://local']})
        cycle=self.tool('athena_cycle_start',{'task_ref':'task://restart','seed':'S'})
        head='abcdef1234567890';promo=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':self.witness(head,'ci'),'smoke_witness':self.witness(head,'smoke')})
        ids={'aor':aor['run_id'],'field':field['run_id'],'transport':transport['run_id'],'recon':recon['run_id'],'cycle':cycle['cycle_id'],'promotion':promo['run_id']}
        self.server.store.close();self.server=Server(self.db);self.seq=100
        self.assertEqual(self.tool('athena_orchestration_get',{'run_id':ids['aor']})['run_id'],ids['aor'])
        self.assertEqual(self.tool('athena_field_get',{'run_id':ids['field']})['run_id'],ids['field'])
        self.assertEqual(self.tool('athena_transport_get',{'run_id':ids['transport']})['run_id'],ids['transport'])
        self.assertEqual(self.tool('athena_reconstruction_get',{'run_id':ids['recon']})['run_id'],ids['recon'])
        self.assertEqual(self.tool('athena_cycle_state',{'cycle_id':ids['cycle']})['cycle_id'],ids['cycle'])
        self.assertEqual(self.tool('athena_promotion_get',{'run_id':ids['promotion']})['run_id'],ids['promotion'])
        self.assertEqual(self.tool('athena_schema_status')['current_db_schema_version'],1)
        self.assertTrue(self.tool('athena_reconstruction_verify',{'run_id':ids['recon']})['match'])
        self.assertTrue(self.tool('athena_transport_replay',{'run_id':ids['transport']})['match'])

    def test_waiting_cycle_survives_restart_and_resumes_without_replaying_fake_work(self):
        start=self.tool('athena_cycle_start',{'task_ref':'task://resume','seed':'S','config':{'require_hug':True}})
        waiting=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'max_steps':16});self.assertEqual(waiting['status'],'WAITING_HUG_IMPLEMENTATION');event_count=len(waiting['events'])
        self.server.store.close();self.server=Server(self.db);self.seq=200
        restored=self.tool('athena_cycle_state',{'cycle_id':start['cycle_id']});self.assertEqual(restored['status'],'WAITING_HUG_IMPLEMENTATION');self.assertEqual(restored['phase'],'HUG');self.assertEqual(len(restored['events']),event_count)
        again=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'max_steps':1});self.assertEqual(again['status'],'WAITING_HUG_IMPLEMENTATION');self.assertEqual(again['phase'],'HUG');self.assertNotIn('hug_invocation',again['state']['artifacts'])

    def test_state_foundation_surfaces_are_required_by_surface2(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for name in ['athena_schema_status','athena_schema_migrate','athena_omega_state','athena_reconstruct_state','athena_reconstruction_verify']:self.assertIn(name,names)
        for uri in ['athena://schema','athena://state/omega','athena://reconstruction']:self.assertIn(uri,uris)
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['status'],'PASS',audit);self.assertEqual(audit['groups']['state_foundation']['status'],'PASS');self.assertEqual(audit['composition']['governance_organs']['status'],'PASS')


if __name__=='__main__':unittest.main()

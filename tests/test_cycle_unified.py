import json
import tempfile
import unittest

from athena_mcp.server import Server


class CycleUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args,expect_error=False):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result']
        if expect_error:self.assertTrue(result.get('isError'),r);return result
        self.assertFalse(result.get('isError'),r);return result['structuredContent']
    @staticmethod
    def measured_candidate():
        return {
            'kind':'IMPLEMENT','operation':'build_verified_component','target_ref':'tool:X','payload':{},'source_refs':['seed://cycle'],
            'readiness':1,'gain':2,'independence':1,'bridge':1,'cost':1,'resource_cost':1,
            'delta_j':2,'information_gain':1,'option_value':1,'evidence':1,'connection':1,'replay':1,'navigation':1,
            'reconstruction':1,'implementation':1,'novelty':1,'duplicate':0,'fake':0,'bloat':0,'unsupported':0,'unhandled_contradiction':0,'coordinate_loss':0,
            'required_capabilities':['analysis'],
            'collective_metrics':{'utility':.9,'gap':.5,'bridge_value':.8,'saturation':.1,'urgency':.7},
        }
    @staticmethod
    def workers():return [{'id':'W1','capabilities':['analysis'],'load':0}]

    def test_empty_cycle_does_not_invent_work_and_stops_without_successor(self):
        start=self.tool('athena_cycle_start',{'task_ref':'task://empty','seed':{'q':'empty'}})
        state=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'max_steps':64})
        self.assertEqual(state['status'],'WAITING_CONTROL');self.assertEqual(state['phase'],'AOR');self.assertIsNone(state['state']['artifacts']['aor_run'].get('next'))
        operations=[e['operation'] for e in state['events']];self.assertIn('SKIP',operations);self.assertIn('FIELD_COMPILE',operations);self.assertIn('WAIT',operations)

    def test_required_hug_without_registered_implementation_waits_fail_closed(self):
        start=self.tool('athena_cycle_start',{'task_ref':'task://hug','seed':'S','config':{'require_hug':True}})
        state=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'max_steps':16})
        self.assertEqual(state['status'],'WAITING_HUG_IMPLEMENTATION');self.assertEqual(state['phase'],'HUG');self.assertIn('HUG implementation',state['state']['wait']['reason'])

    def test_generated_gap_work_stops_at_measurement_before_aor_ranking(self):
        gap={'sources':{'S':['seed']},'edges':[],'targets':[{'id':'T','node':'missing','severity':1,'leverage':1,'information_gain':1,'cost':1}],'policy':{'traversable_relations':[]}}
        start=self.tool('athena_cycle_start',{'task_ref':'task://measure','seed':'S','config':{'gap':gap}})
        state=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'max_steps':64})
        self.assertEqual(state['status'],'WAITING_MEASUREMENT');self.assertEqual(state['phase'],'MEASURE');self.assertTrue(state['state']['artifacts']['field_run']['unmeasured_candidate_ids']);self.assertNotIn('aor_run',state['state']['artifacts'])

    def test_full_internal_flow_stops_at_executor_then_test_then_completes(self):
        config={'field_explicit_candidates':[self.measured_candidate()],'workers':self.workers(),'collective_signals':{'hardness':.5,'uncertainty':.2,'divisibility':.5,'coupling':.2,'volatility':.1,'risk':.2,'migration':0,'repetition':.1,'reuse':.4,'innovation':.6,'latency_sensitivity':.2,'evidence_sensitivity':.8}}
        start=self.tool('athena_cycle_start',{'task_ref':'task://full','seed':{'goal':'build'},'config':config})
        at_exec=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'max_steps':64})
        self.assertEqual(at_exec['status'],'WAITING_EXECUTOR',at_exec);self.assertEqual(at_exec['phase'],'EXECUTE');self.assertEqual(at_exec['state']['artifacts']['aor_run']['next']['source']['target_ref'],'tool:X');self.assertIn('collective_allocation',at_exec['state']['artifacts'])
        self.assertNotIn('test_packet',at_exec['state']['artifacts'])
        at_test=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'inputs':{'execution_receipt':{'verified':True,'ref':'exec://cycle','status':'COMPLETED','result':{'built':True}}},'max_steps':16})
        self.assertEqual(at_test['status'],'WAITING_TEST',at_test);self.assertEqual(at_test['phase'],'VERIFY');self.assertEqual(at_test['state']['artifacts']['execution_receipt']['ref'],'exec://cycle')
        done=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'inputs':{'test_packet':{'procedure':'run component check','observation':'component executed','result':'pass','witness':{'verified':True,'ref':'test://cycle'}}},'max_steps':32})
        self.assertEqual(done['status'],'COMPLETE',done);self.assertEqual(done['phase'],'COMPLETE');self.assertEqual(done['state']['return']['next'],done['state']['artifacts']['aor_run']['next']['id']);self.assertIn('successor',done['state']['return'])
        replay=self.tool('athena_cycle_replay',{'cycle_id':start['cycle_id']});self.assertTrue(replay['match'],replay);self.assertEqual(replay['cycle_status'],'COMPLETE');self.assertIn('aor',replay['child_checks']);self.assertIn('field',replay['child_checks']);self.assertIn('transport',replay['child_checks'])

    def test_failed_execution_routes_to_unmeasured_repair_not_fake_retry(self):
        config={'field_explicit_candidates':[self.measured_candidate()],'workers':self.workers(),'collective_signals':{}}
        start=self.tool('athena_cycle_start',{'task_ref':'task://fail','seed':'S','config':config});state=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'max_steps':64});self.assertEqual(state['status'],'WAITING_EXECUTOR')
        failed=self.tool('athena_cycle_advance',{'cycle_id':start['cycle_id'],'inputs':{'execution_receipt':{'verified':True,'ref':'exec://failed','status':'FAILED'},'failure_antibody_matches':[{'antibody_id':'AB.1','repair':{'operator':'repair-X'},'target_ref':'tool:X'}]},'max_steps':8})
        self.assertEqual(failed['status'],'WAITING_REPAIR');repair=failed['state']['artifacts']['repair_transport']['field_candidates'][0];self.assertEqual(repair['metric_state'],'UNMEASURED');self.assertNotIn('readiness',repair)

    def test_cycle_resource_surface_and_benchmark_are_composed(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};self.assertIn('athena_cycle_start',names);self.assertIn('athena_surface_audit',names);self.assertIn('athena_promotion_evaluate',names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://cycle',uris)
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://cycle'})['result']['contents'][0]['text']);self.assertEqual(resource['version'],'ATHENA.CYCLE.1');self.assertIn('WAITING_*',resource['law'])
        bench=self.tool('athena_benchmark',{});self.assertIn('cycle_runs',bench);self.assertIn('promotion_runs',bench);self.assertIn('transport_runs',bench)


if __name__=='__main__':unittest.main()

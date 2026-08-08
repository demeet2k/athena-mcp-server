import json
import tempfile
import unittest

from athena_mcp.server import Server


class AorCollectiveTransportTests(unittest.TestCase):
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
    def aor_candidate(ident,collective_metrics=None):
        row={'id':ident,'readiness':1,'gain':2,'independence':1,'bridge':1,'cost':1,'resource_cost':1,'delta_j':2,'information_gain':1,'option_value':1,'evidence':1,'connection':1,'replay':1,'navigation':1,'reconstruction':1,'implementation':1,'novelty':1,'duplicate':0,'fake':0,'bloat':0,'unsupported':0,'unhandled_contradiction':0,'coordinate_loss':0,'required_capabilities':['analysis']}
        if collective_metrics is not None:row['collective_metrics']=collective_metrics
        return row

    def test_transport_surface_is_composed_without_removing_mature_organs(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']}
        for name in ['athena_transport_pheromone_attention','athena_transport_aor_to_collective','athena_transport_replay','athena_field_compile','athena_gap_compile','athena_orchestrate','athena_collective_allocate','athena_pheromone_reinforce']:
            self.assertIn(name,names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://aor-collective/transport',uris)

    def test_pheromone_attention_has_empty_evidence_authority_and_rag_patches(self):
        self.tool('athena_pheromone_reinforce',{'route_key':'source://popular','observations':{'quality':1,'reuse':1,'evidence':1}})
        packet=self.tool('athena_transport_pheromone_attention',{'route_keys':['source://popular'],'persist':False})
        self.assertEqual(packet['transport_kind'],'PHEROMONE_TO_ATTENTION');p=packet['packets'][0]
        self.assertEqual(p['rag_metric_patch'],{});self.assertEqual(p['authority_patch'],{});self.assertEqual(p['evidence_patch'],{})
        self.assertIn('does not populate relevance',p['boundary'])
        # A high-memory route with a missing RAG measurement remains UNKNOWN.
        candidate={'id':'popular','source_ref':'source://popular','measurements':{'source_authority':{'value':1,'method':'m','witness_ref':'w'},'cross_value':{'value':1,'method':'m','witness_ref':'w'},'decision_relevance':{'value':1,'method':'m','witness_ref':'w'}},'source_time':100,'cost':1}
        rag=self.tool('athena_retrieval_compile',{'query_ref':'q://popular','query':{'as_of':100,'freshness_half_life':10},'candidates':[candidate],'persist':False})
        self.assertEqual(rag['rows'][0]['score']['status'],'UNKNOWN');self.assertTrue(any(d['metric']=='relevance' for d in rag['measurement_plan'][0]['defects']))

    def test_alarm_transport_creates_gap_pressure_not_proof(self):
        packet=self.tool('athena_transport_alarm_to_gap',{'alarm_ref':'ALARM.1','alarm_nodes':[{'node':'N1','severity':.8}],'persist':False})
        self.assertEqual(packet['targets'][0]['node'],'N1');self.assertIn('does not prove',packet['boundary'])
        gap=self.tool('athena_gap_compile',{'task_ref':'task://alarm','sources':{'S':['origin']},'edges':[],'targets':packet['targets'],'policy':{'traversable_relations':[]},'persist':False})
        self.assertEqual(gap['gap_target_ids'],[packet['targets'][0]['id']]);self.assertEqual(gap['gap'][0]['residual_score']['status'],'UNKNOWN');self.assertTrue(gap['measurement_plan'])

    def test_aor_frontier_to_collective_preserves_identity_and_requires_explicit_collective_metrics(self):
        ready={'utility':.9,'gap':.4,'bridge_value':.7,'saturation':.1,'urgency':.6}
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[self.aor_candidate('ready',ready),self.aor_candidate('unmeasured') ]})
        packet=self.tool('athena_transport_aor_to_collective',{'run_id':run['run_id'],'persist':False})
        by={t['id']:t for t in packet['tasks']};self.assertEqual(by['ready']['candidate_ref'],'ready');self.assertEqual(by['ready']['allocation_state'],'READY');self.assertEqual(by['unmeasured']['allocation_state'],'UNMEASURED')
        self.assertIn('unmeasured',[x['candidate'] for x in packet['measurement_plan']]);self.assertIn('ready',packet['allocation_ready_ids'])
        # Transport does not mutate the stored AOR score/decision.
        replay=self.tool('athena_orchestration_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay)

    def test_observed_rgo_same_outcome_is_not_auto_summed_with_delta_j(self):
        packet=self.tool('athena_transport_rgo_to_reward',{'outcome_ref':'OUT.1','observed_rgo':1.2,'witness_ref':'obs://rgo','delta_j':2.0,'delta_outcome_ref':'OUT.1','persist':False})
        self.assertEqual(packet['double_count_guard'],'SAME_OUTCOME_DO_NOT_SUM');self.assertEqual(packet['aor_reward_patch'],{});self.assertEqual(packet['authority_patch'],{});self.assertIn('must not be counted twice',packet['boundary'])

    def test_bridge_transport_requires_explicit_economics_and_feeds_collective_accounting(self):
        economics={'expected_future_uses':10,'route_saving_per_use':2,'quality_gain':3,'resilience_gain':1,'build_cost':4,'maintenance_cost':1,'locked_capacity_cost':1}
        packet=self.tool('athena_transport_bridge_to_collective',{'candidate_ref':'bridge-candidate','economics':economics,'persist':False})
        self.assertEqual(packet['bridge'],economics);self.assertIn('does not derive',packet['boundary'])
        result=self.tool('athena_bridge_account',{'bridge':packet['bridge']});self.assertIn('decision',result)
        bad=dict(economics);bad.pop('maintenance_cost');self.tool('athena_transport_bridge_to_collective',{'candidate_ref':'b','economics':bad},expect_error=True)

    def test_antibody_match_becomes_unmeasured_repair_candidate_not_execution(self):
        packet=self.tool('athena_transport_antibody_to_repair',{'failure_ref':'FAIL.1','matches':[{'antibody_id':'AB.1','repair':{'operator':'retry-with-fix'},'target_ref':'tool:X'}],'persist':False})
        candidate=packet['field_candidates'][0];self.assertEqual(candidate['kind'],'REPAIR');self.assertEqual(candidate['metric_state'],'UNMEASURED');self.assertNotIn('readiness',candidate);self.assertIn('not auto-executed',packet['boundary'])
        field=self.tool('athena_field_compile',{'seed_ref':'seed://antibody','module_outputs':{},'explicit_candidates':packet['field_candidates'],'persist':False})
        self.assertEqual(field['candidates'][0]['metric_state'],'UNMEASURED');aor=self.tool('athena_orchestrate',{'seed':'S','candidates':field['handoff_to_aor'],'persist':False});self.assertIsNone(aor['next'])

    def test_transport_receipt_replays_frozen_source_snapshot(self):
        run=self.tool('athena_transport_alarm_to_gap',{'alarm_ref':'ALARM.REPLAY','alarm_nodes':[{'node':'N','severity':.5}]})
        self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('TRANSPORTRUN.'))
        replay=self.tool('athena_transport_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay);self.assertEqual(replay['kind'],'ALARM_TO_GAP')

    def test_transport_resource_and_benchmark_declare_firewalls(self):
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://aor-collective/transport'})['result']['contents'][0]['text'])
        self.assertIn('AOR chooses WHAT',resource['laws'][2]);self.assertTrue(any('antibody match' in law for law in resource['laws']))
        bench=self.tool('athena_benchmark',{});self.assertIn('transport_runs',bench);self.assertIn('collective_memory',bench);self.assertIn('orchestration_runs',bench)


if __name__=='__main__':unittest.main()

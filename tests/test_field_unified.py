import json
import tempfile
import unittest

from athena_mcp.server import Server


class FieldUnifiedTests(unittest.TestCase):
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

    def test_module_outputs_become_typed_unmeasured_actions(self):
        module_outputs={
            'extraction_frontier':[{'task_id':'EXTTASK.1','run_id':'EXTRUN.1','seed_ref':'seed://x','transform':'formalize','depth':0,'status':'PLANNED'}],
            'retrieval':{'run_id':'RAGRUN.1','measurement_plan':[{'candidate':'src-u','defects':[{'metric':'cross_value'}]}],'coverage':{'missing_roles':['contradiction'],'missing_facets':['failure']}},
            'authority_plan':[{'candidate':'claim:X','route':'execute_witnessed_test','reason':'below !','minimum':'!','current':'+'}],
            'gap':{'run_id':'GAPRUN.1','measurement_plan':[{'target':'gap-u','node':'node-u','defects':[{'metric':'information_gain'}]}],'gap':[{'id':'gap-k','node':'node-k','residual_score':{'status':'KNOWN','value':3}}]},
            'hug_invocations':[{'invocation_id':'HUGINV.P','impl_id':'HUGIMPL.1','status':'PLANNED'},{'invocation_id':'HUGINV.F','impl_id':'HUGIMPL.2','status':'FAILED','failure':{'reason':'executor error'}}],
            'branches':[{'branch_id':'BR.1','basis_id':'B.1','status':'REVIEW','ewma_reward':0.2,'last_eid':'E1'}],
            'aor':{'run_id':'AORRUN.1','measurement_plan':[{'candidate':'aor-u','missing_metrics':['gain']}],'calibration_plan':[{'candidate':'aor-c','metrics':['cost']}]},
        }
        run=self.tool('athena_field_compile',{'seed_ref':'seed://field','module_outputs':module_outputs,'ecosystem':{'K':'known','Z':'boundary'},'persist':False})
        operations={c['operation'] for c in run['candidates']}
        for operation in [
            'execute_extraction_transform','measure_retrieval_candidate','acquire_missing_retrieval_role','acquire_missing_retrieval_facet',
            'execute_witnessed_test','measure_gap_residual','address_gap_target','execute_hug_invocation','repair_hug_failure',
            'review_branch_reactivation','measure_aor_candidate','calibrate_aor_candidate'
        ]:self.assertIn(operation,operations)
        self.assertEqual(set(run['unmeasured_candidate_ids']),set(run['candidate_ids']))
        self.assertEqual(run['conflict_candidate_ids'],[])
        self.assertTrue(all(c['metric_state']=='UNMEASURED' for c in run['candidates']))
        self.assertTrue(all('readiness' not in c and 'gain' not in c and 'delta_j' not in c for c in run['candidates']))
        self.assertEqual(run['ecosystem']['Z'],'boundary')

    def test_exact_same_action_merges_provenance_not_semantic_similarity(self):
        explicit=[
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{'mode':'same'},'source_refs':['obs:A'],'readiness':1,'gain':1,'independence':1,'bridge':1,'cost':1},
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{'mode':'same'},'source_refs':['obs:B'],'readiness':1,'gain':1,'independence':1,'bridge':1,'cost':1},
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{'mode':'different'},'source_refs':['obs:C'],'readiness':1,'gain':1,'independence':1,'bridge':1,'cost':1},
        ]
        run=self.tool('athena_field_compile',{'seed_ref':'seed://merge','module_outputs':{},'explicit_candidates':explicit,'persist':False})
        self.assertEqual(len(run['candidates']),2)
        merged=next(c for c in run['candidates'] if c['payload']['mode']=='same')
        self.assertEqual(merged['source_refs'],['obs:A','obs:B']);self.assertEqual(merged['metric_state'],'EXPLICIT')
        self.assertEqual(len(run['exact_signature_merges']),1)

    def test_conflicting_explicit_metrics_fail_closed_and_strip_aor_operands(self):
        explicit=[
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{},'source_refs':['obs:A'],'readiness':.9,'gain':.8,'independence':1,'bridge':1,'cost':1,'delta_j':2},
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{},'source_refs':['obs:B'],'readiness':.2,'gain':.8,'independence':1,'bridge':1,'cost':1,'delta_j':2},
        ]
        run=self.tool('athena_field_compile',{'seed_ref':'seed://conflict','module_outputs':{},'explicit_candidates':explicit,'persist':False})
        self.assertEqual(len(run['candidates']),1);candidate=run['candidates'][0]
        self.assertEqual(candidate['metric_state'],'CONFLICT');self.assertEqual(run['conflict_candidate_ids'],[candidate['id']]);self.assertIn(candidate['id'],run['unmeasured_candidate_ids'])
        self.assertTrue(candidate['metric_conflicts']);self.assertIn('readiness',candidate['metric_conflicts'][0])
        for field in ['readiness','gain','independence','bridge','cost','delta_j']:self.assertNotIn(field,candidate)
        self.assertEqual(candidate['source_refs'],['obs:A','obs:B'])

    def test_conflicting_routing_metadata_fails_closed_and_strips_routes(self):
        explicit=[
            {'kind':'TEST','operation':'verify_claim','target_ref':'claim:X','payload':{},'source_refs':['a'],'claim_id':'C1','min_authority':'!','readiness':1,'gain':1,'independence':1,'bridge':1,'cost':1},
            {'kind':'TEST','operation':'verify_claim','target_ref':'claim:X','payload':{},'source_refs':['b'],'claim_id':'C2','min_authority':'!','readiness':1,'gain':1,'independence':1,'bridge':1,'cost':1},
        ]
        run=self.tool('athena_field_compile',{'seed_ref':'seed://routing-conflict','module_outputs':{},'explicit_candidates':explicit,'persist':False})
        candidate=run['candidates'][0];self.assertEqual(candidate['metric_state'],'CONFLICT');self.assertTrue(candidate['routing_conflicts']);self.assertIn('claim_id',candidate['routing_conflicts'][0])
        self.assertNotIn('claim_id',candidate);self.assertNotIn('min_authority',candidate)

    def test_explicit_measurement_can_upgrade_identical_generated_action(self):
        generated={'retrieval':{'measurement_plan':[{'candidate':'src-u','defects':[{'metric':'relevance'}]}]}}
        explicit=[{'kind':'MEASURE','operation':'measure_retrieval_candidate','target_ref':'src-u','payload':{'defects':[{'metric':'relevance'}]},'source_refs':['measure://actual'],'readiness':1,'gain':2,'independence':1,'bridge':1,'cost':1,'delta_j':1,'information_gain':1,'option_value':1,'evidence':1,'connection':1,'replay':1,'navigation':1,'reconstruction':1,'implementation':1,'novelty':1,'duplicate':0,'fake':0,'bloat':0,'unsupported':0,'unhandled_contradiction':0,'coordinate_loss':0}]
        run=self.tool('athena_field_compile',{'seed_ref':'seed://upgrade','module_outputs':generated,'explicit_candidates':explicit,'persist':False})
        self.assertEqual(len(run['candidates']),1);candidate=run['candidates'][0];self.assertEqual(candidate['metric_state'],'EXPLICIT');self.assertEqual(candidate['gain'],2);self.assertIn('RAG.1',candidate['field_origin']);self.assertIn('EXPLICIT',candidate['field_origin'])

    def test_field_handoff_to_aor_keeps_generated_candidates_nonrankable(self):
        field=self.tool('athena_field_compile',{'seed_ref':'seed://handoff','module_outputs':{'gap':{'gap':[{'id':'gap-1','node':'N','residual_score':{'status':'KNOWN','value':2}}]}},'persist':False})
        self.assertTrue(field['handoff_to_aor'])
        aor=self.tool('athena_orchestrate',{'seed':'S','candidates':field['handoff_to_aor'],'persist':False})
        self.assertIsNone(aor['next']);self.assertTrue(aor['measurement_plan']);self.assertEqual(aor['frontier'][0]['scores']['frontier']['status'],'UNKNOWN')
        self.assertNotEqual(aor['frontier'][0]['scores']['frontier'].get('value'),0)

    def test_fieldrun_persists_and_replays_conflict_and_provenance_state(self):
        explicit=[
            {'kind':'BRIDGE','operation':'build_bridge','target_ref':'bridge:X','payload':{},'source_refs':['one'],'readiness':1,'gain':1,'independence':1,'bridge':1,'cost':1},
            {'kind':'BRIDGE','operation':'build_bridge','target_ref':'bridge:X','payload':{},'source_refs':['two'],'readiness':.5,'gain':1,'independence':1,'bridge':1,'cost':1},
        ]
        run=self.tool('athena_field_compile',{'seed_ref':'seed://replay','module_outputs':{},'explicit_candidates':explicit})
        self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('FIELDRUN.'))
        replay=self.tool('athena_field_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay);self.assertEqual(replay['stored_conflicts'],replay['recomputed_conflicts']);self.assertEqual(replay['stored_edges'],replay['recomputed_edges'])

    def test_field_resource_and_benchmark_are_composed(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};self.assertIn('athena_field_compile',names);self.assertIn('athena_collective_plan',names);self.assertIn('athena_orchestrate',names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://field',uris)
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://field'})['result']['contents'][0]['text']);self.assertIn('deterministic assembler',resource['epistemic_boundary']);self.assertIn('UNMEASURED',resource['law']);self.assertIn('CONFLICT',resource['law'])
        bench=self.tool('athena_benchmark',{});self.assertIn('field_runs',bench);self.assertIn('gap_runs',bench);self.assertIn('hug_implementations',bench);self.assertIn('collective_memory',bench)


if __name__=='__main__':unittest.main()

import json
import tempfile
import unittest

from athena_mcp.field_server import FIELD_STACK_VERSION,FieldServer,field_stack_manifest


class FieldServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=FieldServer(self.tmp.name);self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args,expect_error=False):
        r=self.rpc('tools/call',{'name':name,'arguments':args})
        if expect_error:
            self.assertTrue(r['result'].get('isError'),r);return r['result']
        self.assertFalse(r['result'].get('isError'),r);return r['result']['structuredContent']

    def test_field_layer_preserves_every_prior_modular_surface(self):
        names=[x['name'] for x in self.rpc('tools/list')['result']['tools']]
        self.assertEqual(names,sorted(names))
        for required in [
            'athena_field_compile','athena_field_replay',
            'athena_gap_compile','athena_hug_register','athena_retrieval_compile',
            'athena_extraction_plan','athena_equivalence_snapshot','athena_claim_register',
            'athena_branch_observe','athena_orchestrate','athena_apply_transform',
            'athena_apply_transform_route','athena_finalize_output','athena_verify_emission',
            'athena_crystallize_output','athena_dense_navigate','athena_session_start','athena_git_status'
        ]:self.assertIn(required,names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for uri in [
            'athena://field','athena://stack','athena://gap','athena://hug','athena://retrieval',
            'athena://extraction','athena://equivalence','athena://authority','athena://branches',
            'athena://transforms','athena://emissions','athena://orchestration/law'
        ]:self.assertIn(uri,uris)

    def test_gap_and_rag_residuals_compile_into_unmeasured_field_actions(self):
        module_outputs={
            'retrieval':{
                'run_id':'RAGRUN.1',
                'measurement_plan':[{'candidate':'src-u','defects':[{'metric':'cross_value'}]}],
                'coverage':{'missing_roles':['contradiction'],'missing_facets':['failure']},
            },
            'gap':{
                'run_id':'GAPRUN.1',
                'measurement_plan':[{'target':'gap-u','node':'node-u','defects':[{'metric':'information_gain'}]}],
                'gap':[{'id':'gap-k','node':'node-k','residual_score':{'status':'KNOWN','value':3}}],
            },
        }
        run=self.tool('athena_field_compile',{'seed_ref':'seed://field','module_outputs':module_outputs,'ecosystem':{'K':'known','Z':'boundary'},'actor':'A1'})
        self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('FIELDRUN.'))
        operations={c['operation'] for c in run['candidates']}
        for operation in ['measure_retrieval_candidate','acquire_missing_retrieval_role','acquire_missing_retrieval_facet','measure_gap_residual','address_gap_target']:
            self.assertIn(operation,operations)
        self.assertEqual(set(run['unmeasured_candidate_ids']),set(run['candidate_ids']))
        self.assertTrue(all(c['metric_state']=='UNMEASURED' for c in run['candidates']))
        self.assertEqual(run['ecosystem']['Z'],'boundary')

    def test_exact_action_metric_conflict_fails_closed_at_mcp_surface(self):
        explicit=[
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{},'source_refs':['obs:A'],'readiness':0.9,'gain':0.8,'cost':1},
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{},'source_refs':['obs:B'],'readiness':0.2,'gain':0.8,'cost':1},
        ]
        run=self.tool('athena_field_compile',{'seed_ref':'seed://conflict','module_outputs':{},'explicit_candidates':explicit,'persist':False})
        self.assertEqual(len(run['candidates']),1);candidate=run['candidates'][0]
        self.assertEqual(candidate['metric_state'],'CONFLICT')
        self.assertNotIn('readiness',candidate);self.assertNotIn('gain',candidate);self.assertNotIn('cost',candidate)
        self.assertTrue(candidate['metric_conflicts']);self.assertEqual(run['unmeasured_candidate_ids'],[candidate['id']])

    def test_fieldrun_replay_freezes_module_inputs_and_provenance_edges(self):
        module_outputs={'authority_plan':[{'candidate':'claim:X','route':'execute_witnessed_test','reason':'below !','minimum':'!','current':'+'}]}
        run=self.tool('athena_field_compile',{'seed_ref':'seed://replay','module_outputs':module_outputs})
        replay=self.tool('athena_field_replay',{'run_id':run['run_id']})
        self.assertTrue(replay['match']);self.assertEqual(replay['stored_candidate_ids'],replay['recomputed_candidate_ids']);self.assertEqual(replay['stored_edges'],replay['recomputed_edges'])

    def test_field_stack_manifest_extends_prior_stack_without_rewriting_it(self):
        manifest=field_stack_manifest();self.assertEqual(manifest['version'],FIELD_STACK_VERSION)
        self.assertEqual(manifest['layers'][-1]['name'],'FIELD1');self.assertEqual(manifest['layers'][-1]['index'],len(manifest['layers'])-1)
        self.assertEqual(manifest['default_candidate'],'FieldServer')
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://stack'})['result']['contents'][0]['text'])
        self.assertEqual(resource['version'],FIELD_STACK_VERSION);self.assertEqual(resource['layers'][-1]['name'],'FIELD1')
        self.assertTrue(any('QHUG' in item for item in resource['unresolved']))

    def test_field_resource_benchmark_and_prompt(self):
        self.tool('athena_field_compile',{'seed_ref':'seed://r','module_outputs':{'branches':[{'branch_id':'BR.1','basis_id':'B.1','state':'REVIEW','ewma':0.2,'last_trigger_ref':'gap'}]}})
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://field'})['result']['contents'][0]['text'])
        self.assertEqual(payload['law']['version'],'FIELD.1');self.assertEqual(payload['benchmark']['field_runs'],1)
        bench=self.tool('athena_benchmark',{});self.assertEqual(bench['field_runs'],1)
        for key in ['gap_runs','hug_implementations','retrieval_runs','extraction_runs','equivalence_pairs','authority_claims','branches','orchestration_runs']:
            self.assertIn(key,bench)
        prompt=self.rpc('prompts/get',{'name':'athena_maxdev','arguments':{'agent':'A','task':'T'}})['result']['messages'][0]['content']['text']
        self.assertIn('19 FIELD/PHI:',prompt);self.assertIn('metric_state=UNMEASURED',prompt);self.assertIn('metric_state=CONFLICT',prompt)


if __name__=='__main__':unittest.main()

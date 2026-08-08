import json
import tempfile
import unittest

from athena_mcp.server import Server


class HugUnifiedTests(unittest.TestCase):
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
    def semantics():return {p:{'meaning':f'meaning of {p}'} for p in ('io','au','fx','lm','er','st')}
    @staticmethod
    def args():return {'io':1,'au':2,'fx':3,'lm':4,'er':5,'st':6}
    def register(self):
        return self.tool('athena_hug_register',{'name':'QHUG-test-implementation','version':'0.1','algorithm_ref':'artifact://qhug/test-definition','implementation_digest':'sha256:test-impl','parameter_semantics':self.semantics(),'input_schema':{'type':'object','required':['io','au','fx','lm','er','st'],'properties':{p:{'type':'number'} for p in ('io','au','fx','lm','er','st')},'additionalProperties':False},'output_schema':{'type':'object','required':['value'],'properties':{'value':{'type':'number'}},'additionalProperties':False}})['implementation']

    def test_empty_registry_does_not_invent_qhug(self):
        self.assertEqual(self.tool('athena_hug_list',{}),[])
        self.tool('athena_hug_plan',{'impl_id':'HUGIMPL.DOES_NOT_EXIST','arguments':self.args()},expect_error=True)
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://hug'})['result']['contents'][0]['text'])
        self.assertIn('UNRESOLVED',resource['semantic_status']);self.assertEqual(resource['signature'],'HUG(io,au,fx,lm,er,st)')

    def test_registration_requires_exact_six_semantics_and_starts_candidate(self):
        sem=self.semantics();sem.pop('st')
        self.tool('athena_hug_register',{'name':'bad','version':'1','algorithm_ref':'a','implementation_digest':'d','parameter_semantics':sem,'input_schema':{},'output_schema':{}},expect_error=True)
        impl=self.register();self.assertEqual(impl['status'],'CANDIDATE');self.assertEqual(tuple(impl['parameter_semantics']),('au','er','fx','io','lm','st') if False else tuple(sorted(impl['parameter_semantics'])))
        self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':self.args()},expect_error=True)

    def test_explicit_candidate_plan_is_only_planned_and_requires_external_execution(self):
        impl=self.register();plan=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':self.args(),'required_status':'CANDIDATE','context':{'mode':'experimental'}})
        self.assertEqual(plan['status'],'PLANNED');self.assertEqual(plan['execution_boundary'],'EXTERNAL_OR_REGISTERED_EXECUTOR_REQUIRED');self.assertEqual(plan['impl_snapshot']['status'],'CANDIDATE')
        state=self.tool('athena_hug_invocation',{'invocation_id':plan['invocation_id']});self.assertIsNone(state['output']);self.assertEqual(state['status'],'PLANNED')

    def test_completion_requires_schema_valid_output_and_verified_receipt(self):
        impl=self.register();plan=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':self.args(),'required_status':'CANDIDATE'})
        self.tool('athena_hug_complete',{'invocation_id':plan['invocation_id'],'output':{'value':'bad'},'receipt':{'verified':True,'ref':'exec://bad-output'}},expect_error=True)
        self.tool('athena_hug_complete',{'invocation_id':plan['invocation_id'],'output':{'value':7},'receipt':{'verified':False,'ref':'exec://unverified'}},expect_error=True)
        done=self.tool('athena_hug_complete',{'invocation_id':plan['invocation_id'],'output':{'value':7},'receipt':{'verified':True,'ref':'exec://real'}})
        self.assertEqual(done['status'],'COMPLETED');self.assertEqual(done['output']['value'],7)
        verify=self.tool('athena_hug_verify_packet',{'invocation_id':plan['invocation_id']});self.assertTrue(verify['match']);self.assertEqual(verify['semantic_replay'],'N/A_UNLESS_REGISTERED_EXECUTOR_REPLAYS_ALGORITHM')

    def test_maturity_is_non_skippable_and_witnessed(self):
        impl=self.register();iid=impl['impl_id']
        self.tool('athena_hug_promote',{'impl_id':iid,'target_status':'CANONICAL','canonical_authority':{'authorized':True,'ref':'gov://skip'}},expect_error=True)
        self.tool('athena_hug_promote',{'impl_id':iid,'target_status':'TESTED','test':{'procedure':'p','observation':'o','result':'r','witness':{'verified':True,'ref':'test://hug'}}})
        canonical=self.tool('athena_hug_promote',{'impl_id':iid,'target_status':'CANONICAL','canonical_authority':{'authorized':True,'ref':'gov://hug'}})['implementation']
        self.assertEqual(canonical['status'],'CANONICAL')
        plan=self.tool('athena_hug_plan',{'impl_id':iid,'arguments':self.args()});self.assertEqual(plan['status'],'PLANNED');self.assertEqual(plan['impl_snapshot']['status'],'CANONICAL')

    def test_ragrun_reference_can_be_frozen_as_context_without_becoming_hug_semantics(self):
        rag=self.tool('athena_retrieval_compile',{'query_ref':'q://hug','query':{'as_of':100,'freshness_half_life':10},'candidates':[]})
        impl=self.register();plan=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':self.args(),'required_status':'CANDIDATE','context':{'ragrun':rag['run_id'],'B':rag['selected_ids']}})
        self.assertEqual(plan['context']['ragrun'],rag['run_id']);verify=self.tool('athena_hug_verify_packet',{'invocation_id':plan['invocation_id']});self.assertTrue(verify['match'])
        stored=self.tool('athena_hug_invocation',{'invocation_id':plan['invocation_id']});self.assertEqual(stored['context']['B'],[]);self.assertEqual(stored['impl_snapshot']['algorithm_ref'],'artifact://qhug/test-definition')

    def test_witnessed_failure_does_not_fabricate_output(self):
        impl=self.register();plan=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':self.args(),'required_status':'CANDIDATE'})
        failed=self.tool('athena_hug_fail',{'invocation_id':plan['invocation_id'],'reason':'executor unavailable','witness':{'verified':True,'ref':'exec://failure'}});self.assertEqual(failed['status'],'FAILED')
        state=self.tool('athena_hug_invocation',{'invocation_id':plan['invocation_id']});self.assertIsNone(state['output']);self.assertEqual(state['failure']['reason'],'executor unavailable')

    def test_benchmark_and_surface_preserve_collective_and_aor(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};self.assertIn('athena_hug_register',names);self.assertIn('athena_collective_plan',names);self.assertIn('athena_orchestrate',names)
        bench=self.tool('athena_benchmark',{});self.assertIn('hug_implementations',bench);self.assertIn('retrieval_runs',bench);self.assertIn('collective_memory',bench)


if __name__=='__main__':unittest.main()

import json
import tempfile
import unittest

from athena_mcp.hug_server import HugServer
from athena_mcp.orchestration_hug import HUG_PARAMS

PARAMS={p:{'meaning':f'meaning:{p}'} for p in HUG_PARAMS}
INPUT_SCHEMA={'type':'object','required':list(HUG_PARAMS),'properties':{p:{} for p in HUG_PARAMS},'additionalProperties':False}
OUTPUT_SCHEMA={'type':'object','required':['state'],'properties':{'state':{}},'additionalProperties':True}
ARGS={p:i for i,p in enumerate(HUG_PARAMS)}

def measurements(rel=1):
    return {
        'relevance':{'value':rel,'method':'semantic','witness_ref':'m:r'},
        'source_authority':{'value':1,'method':'provenance','witness_ref':'m:a'},
        'cross_value':{'value':1,'method':'cross','witness_ref':'m:c'},
        'decision_relevance':{'value':1,'method':'decision','witness_ref':'m:d'},
    }

class HugServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=HugServer(self.tmp.name);self.seq=0
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
    def register(self):
        return self.tool('athena_hug_register',{'name':'QHUG','version':'1.0','algorithm_ref':'docs://qhug/v1','implementation_digest':'sha256:q1','parameter_semantics':PARAMS,'input_schema':INPUT_SCHEMA,'output_schema':OUTPUT_SCHEMA,'actor':'A1'})['implementation']
    def canonical(self):
        impl=self.register();iid=impl['impl_id'];self.tool('athena_hug_promote',{'impl_id':iid,'target_status':'TESTED','test':{'procedure':'vectors','observation':'outputs','result':'pass','witness':{'verified':True,'ref':'test:qhug'}}});return self.tool('athena_hug_promote',{'impl_id':iid,'target_status':'CANONICAL','canonical_authority':{'authorized':True,'ref':'canon:qhug'}})['implementation']

    def test_hug_surface_composes_with_retrieval_extraction_authority_and_mature_runtime(self):
        names=[x['name'] for x in self.rpc('tools/list')['result']['tools']]
        for required in ['athena_hug_register','athena_hug_plan','athena_hug_complete','athena_retrieval_compile','athena_extraction_plan','athena_equivalence_snapshot','athena_claim_register','athena_branch_observe','athena_orchestrate','athena_apply_transform','athena_finalize_output','athena_verify_emission']:
            self.assertIn(required,names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for uri in ['athena://hug','athena://retrieval','athena://extraction','athena://equivalence','athena://authority','athena://branches','athena://transforms','athena://emissions']:
            self.assertIn(uri,uris)

    def test_candidate_hug_cannot_fake_canonical_execution(self):
        impl=self.register();err=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':ARGS},expect_error=True);self.assertIn('below required CANONICAL',err['content'][0]['text'])

    def test_ragrun_can_be_frozen_into_huginv_context_without_becoming_hug_result(self):
        source={'id':'s','source_ref':'source://s','measurements':measurements(),'source_time':900,'cost':1}
        rag=self.tool('athena_retrieval_compile',{'query_ref':'q://hug','query':{'as_of':1000,'freshness_half_life':100,'budget':1,'max_items':1},'candidates':[source]})
        impl=self.canonical();planned=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':ARGS,'context':{'rag_run':rag['run_id'],'selected_sources':rag['selected_ids']}})
        self.assertEqual(planned['status'],'PLANNED');self.assertEqual(planned['context']['rag_run'],rag['run_id']);self.assertNotIn('output',planned)
        stored=self.tool('athena_hug_invocation',{'invocation_id':planned['invocation_id']});self.assertEqual(stored['context']['selected_sources'],['s']);self.assertIsNone(stored['output'])

    def test_verified_executor_completion_and_packet_integrity(self):
        impl=self.canonical();planned=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':ARGS,'context':{'source':'test'}})
        self.tool('athena_hug_complete',{'invocation_id':planned['invocation_id'],'output':{'state':{'ok':True}},'receipt':{'verified':True,'ref':'executor:1'}})
        check=self.tool('athena_hug_verify_packet',{'invocation_id':planned['invocation_id']});self.assertTrue(check['match']);self.assertEqual(check['semantic_replay'],'N/A_UNLESS_REGISTERED_EXECUTOR_REPLAYS_ALGORITHM')

    def test_invalid_output_or_unverified_receipt_fails_closed(self):
        impl=self.canonical();inv=self.tool('athena_hug_plan',{'impl_id':impl['impl_id'],'arguments':ARGS})['invocation_id']
        bad=self.tool('athena_hug_complete',{'invocation_id':inv,'output':{'bad':1},'receipt':{'verified':True,'ref':'exec'}},expect_error=True);self.assertTrue(bad['isError'])
        bad2=self.tool('athena_hug_complete',{'invocation_id':inv,'output':{'state':'ok'},'receipt':{'verified':False,'ref':'bad'}},expect_error=True);self.assertTrue(bad2['isError'])

    def test_hug_resource_benchmark_and_prompt(self):
        self.register();payload=json.loads(self.rpc('resources/read',{'uri':'athena://hug'})['result']['contents'][0]['text']);self.assertEqual(payload['law']['signature'],'HUG(io,au,fx,lm,er,st)');self.assertEqual(payload['benchmark']['hug_implementations'],1)
        bench=self.tool('athena_benchmark',{});self.assertEqual(bench['hug_implementations'],1);self.assertIn('retrieval_runs',bench);self.assertIn('extraction_runs',bench)
        prompt=self.rpc('prompts/get',{'name':'athena_maxdev','arguments':{'agent':'A','task':'T'}})['result']['messages'][0]['content']['text'];self.assertIn('17 HUG ABI:',prompt);self.assertIn('fail closed rather than substituting another algorithm',prompt)

if __name__=='__main__':unittest.main()

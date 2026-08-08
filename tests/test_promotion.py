import json
import tempfile
import unittest

from athena_mcp.field_server import FieldServer
from athena_mcp.promotion import evaluate_promotion


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db')
        self.server=FieldServer(self.tmp.name)
        self.seq=0

    def tearDown(self):
        self.server.store.close();self.tmp.close()

    def rpc(self,method,params=None):
        self.seq+=1
        message={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:message['params']=params
        return self.server.handle(message)

    def tool(self,name,args,expect_error=False):
        response=self.rpc('tools/call',{'name':name,'arguments':args})
        result=response['result']
        if expect_error:
            self.assertTrue(result.get('isError'),response);return result
        self.assertFalse(result.get('isError'),response);return result['structuredContent']

    @staticmethod
    def witness(head,ref='ci://run'):
        return {'observed':True,'ref':ref,'head_sha':head,'conclusion':'success'}

    def test_surface_and_composition_include_promotion(self):
        audit=self.tool('athena_surface_audit',{})
        self.assertEqual(audit['status'],'PASS',audit)
        self.assertEqual(audit['groups']['promotion']['status'],'PASS')
        self.assertEqual(audit['composition']['organs']['promotion']['status'],'PASS')
        self.assertEqual(audit['composition']['read_only_probes']['promotion']['status'],'PASS')
        resources={row['uri'] for row in self.rpc('resources/list')['result']['resources']}
        self.assertIn('athena://promotion',resources)

    def test_direct_evaluator_blocks_missing_or_mismatched_external_witness(self):
        surface=self.tool('athena_surface_audit',{})
        head='abcdef1234567890'
        blocked=evaluate_promotion('FieldServer',head,surface,
            {'observed':False,'ref':'','head_sha':head,'conclusion':'success'},
            self.witness(head,'smoke://ok'))
        self.assertEqual(blocked['status'],'BLOCKED')
        self.assertIn('not_observed',blocked['gates']['ci']['defects'])
        mismatch=evaluate_promotion('FieldServer',head,surface,
            self.witness('deadbeef','ci://bad-head'),self.witness(head,'smoke://ok'))
        self.assertEqual(mismatch['status'],'BLOCKED')
        self.assertIn('head_mismatch',mismatch['gates']['ci']['defects'])

    def test_mcp_promotion_qualifies_only_on_exact_attested_head_and_replays(self):
        head='1234567890abcdef1234567890abcdef12345678'
        run=self.tool('athena_promotion_evaluate',{
            'git_head':head,
            'ci_witness':self.witness(head,'ci://exact-head'),
            'smoke_witness':self.witness(head,'smoke://exact-head'),
            'actor':'TEST',
        })
        self.assertEqual(run['status'],'QUALIFIED',run)
        self.assertTrue(run['promotion_allowed'])
        self.assertTrue(run['persisted'])
        self.assertTrue(run['run_id'].startswith('PROMRUN.'))
        self.assertIn('caller',run['gates']['ci']['boundary'])
        stored=self.tool('athena_promotion_get',{'run_id':run['run_id']})
        self.assertEqual(stored['git_head'],head)
        replay=self.tool('athena_promotion_replay',{'run_id':run['run_id']})
        self.assertTrue(replay['match'],replay)
        self.assertEqual(replay['status'],'REPLAY_MATCH')
        recent=self.tool('athena_promotion_recent',{})
        self.assertEqual(recent[0]['run_id'],run['run_id'])

    def test_schema_rejects_invalid_success_attestation(self):
        head='1234567890abcdef'
        result=self.tool('athena_promotion_evaluate',{
            'git_head':head,
            'ci_witness':{'observed':True,'ref':'ci://x','head_sha':head,'conclusion':'failure'},
            'smoke_witness':self.witness(head,'smoke://x'),
        },expect_error=True)
        self.assertTrue(result['isError'])

    def test_promotion_resource_and_benchmark(self):
        resource=self.rpc('resources/read',{'uri':'athena://promotion'})['result']['contents'][0]
        payload=json.loads(resource['text'])
        self.assertEqual(payload['version'],'ATHENA.PROMOTION.1')
        bench=self.tool('athena_benchmark',{})
        self.assertIn('promotion_runs',bench)
        self.assertEqual(bench['surface_audit'],'PASS')
        self.assertEqual(bench['composition_audit'],'PASS')


if __name__=='__main__':unittest.main()

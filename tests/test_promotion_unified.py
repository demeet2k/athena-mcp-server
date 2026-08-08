import json
import tempfile
import unittest

from athena_mcp.promotion import evaluate_promotion
from athena_mcp.server import Server


class PromotionUnifiedTests(unittest.TestCase):
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
    def witness(head,kind='ci'):
        # Synthetic unit-test attestation. This exercises the promotion predicate;
        # it is not claimed to be a real GitHub Actions witness.
        return {'observed':True,'ref':f'{kind}://synthetic-test','head_sha':head,'conclusion':'success'}

    def test_exact_same_head_synthetic_attestations_can_qualify_when_local_git_disabled(self):
        head='abcdef1234567890'
        run=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':self.witness(head,'ci'),'smoke_witness':self.witness(head,'smoke'),'persist':False})
        self.assertEqual(run['status'],'QUALIFIED',run);self.assertTrue(run['promotion_allowed']);self.assertEqual(run['gates']['surface']['status'],'PASS');self.assertEqual(run['gates']['composition']['status'],'PASS')
        self.assertFalse(run['gates']['local_git']['enabled']);self.assertIn('external attestation',run['gates']['ci']['boundary'])

    def test_mismatched_ci_head_blocks_without_weakening_external_attestation_contract(self):
        head='abcdef1234567890';other='fedcba0987654321'
        run=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':self.witness(other,'ci'),'smoke_witness':self.witness(head,'smoke'),'persist':False})
        self.assertEqual(run['status'],'BLOCKED');self.assertFalse(run['promotion_allowed']);self.assertIn('head_mismatch',run['gates']['ci']['defects']);self.assertEqual(run['gates']['smoke']['status'],'PASS')

    def test_pure_predicate_blocks_surface_or_composition_failure(self):
        head='abcdef1234567890';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke')
        surface={'status':'FAIL','surface_status':'FAIL','composition':{'status':'PASS'}}
        result=evaluate_promotion('Server',head,surface,ci,smoke,{'enabled':False});self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['gates']['surface']['status'],'FAIL')
        surface={'status':'FAIL','surface_status':'PASS','composition':{'status':'FAIL'}}
        result=evaluate_promotion('Server',head,surface,ci,smoke,{'enabled':False});self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['gates']['composition']['status'],'FAIL')

    def test_local_git_mismatch_blocks_when_git_is_configured(self):
        head='abcdef1234567890';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke');surface={'status':'PASS','surface_status':'PASS','composition':{'status':'PASS'}}
        result=evaluate_promotion('Server',head,surface,ci,smoke,{'enabled':True,'head':'different1234567'})
        self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['gates']['local_git']['status'],'FAIL');self.assertIn('local_head_mismatch',result['gates']['local_git']['defects'])

    def test_promrun_persists_and_replays_frozen_certificates(self):
        head='abcdef1234567890'
        run=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':self.witness(head,'ci'),'smoke_witness':self.witness(head,'smoke')})
        self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('PROMRUN.'));self.assertEqual(run['status'],'QUALIFIED')
        stored=self.tool('athena_promotion_get',{'run_id':run['run_id']});self.assertEqual(stored['git_head'],head);self.assertEqual(stored['status'],'QUALIFIED')
        replay=self.tool('athena_promotion_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay);self.assertEqual(replay['stored_status'],'QUALIFIED');self.assertEqual(replay['recomputed_status'],'QUALIFIED')
        recent=self.tool('athena_promotion_recent',{'limit':5});self.assertTrue(any(row['run_id']==run['run_id'] for row in recent))

    def test_old_promrun_does_not_automatically_qualify_a_new_head(self):
        old='aaaaaaaaaaaaaaa1';new='bbbbbbbbbbbbbbb2'
        oldrun=self.tool('athena_promotion_evaluate',{'git_head':old,'ci_witness':self.witness(old,'ci'),'smoke_witness':self.witness(old,'smoke')})
        replay=self.tool('athena_promotion_replay',{'run_id':oldrun['run_id']});self.assertTrue(replay['match']);self.assertEqual(replay['git_head'],old)
        blocked=self.tool('athena_promotion_evaluate',{'git_head':new,'ci_witness':self.witness(old,'ci'),'smoke_witness':self.witness(old,'smoke'),'persist':False})
        self.assertEqual(blocked['status'],'BLOCKED');self.assertEqual(blocked['git_head'],new)

    def test_promotion_resource_states_epistemic_boundary(self):
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://promotion'})['result']['contents'][0]['text'])
        self.assertEqual(payload['version'],'ATHENA.PROMOTION.1');self.assertIn('external attestations',payload['boundary']);self.assertIn('same exact head',payload['law'])
        bench=self.tool('athena_benchmark',{});self.assertIn('promotion_runs',bench)


if __name__=='__main__':unittest.main()

import json
import tempfile
import unittest

from athena_mcp.identity import digest
from athena_mcp.promotion import PROMOTION_V1_VERSION,PROMOTION_VERSION,evaluate_promotion,evaluate_promotion_v1
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
        return {'observed':True,'ref':f'{kind}://synthetic-test','head_sha':head,'conclusion':'success'}
    @staticmethod
    def surface(status='PASS',composition='PASS'):
        return {'status':status,'surface_status':status,'composition':{'status':composition}}
    @staticmethod
    def trusted(head,ci,smoke):
        return {'observed':True,'verifier':'TEST.TRUSTED.HOST','verification_ref':'trusted://promotion-test','head_sha':head,'ci_ref':ci['ref'],'smoke_ref':smoke['ref']}

    def test_caller_attestations_reach_attested_ready_not_qualified(self):
        head='abcdef1234567890'
        run=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':self.witness(head,'ci'),'smoke_witness':self.witness(head,'smoke'),'persist':False})
        self.assertEqual(run['version'],PROMOTION_VERSION)
        self.assertEqual(run['status'],'ATTESTED_READY',run);self.assertFalse(run['promotion_allowed']);self.assertTrue(run['external_verification_required'])
        self.assertEqual(run['attestation_level'],'CALLER_BOUND');self.assertEqual(run['gates']['ci']['trust_class'],'CALLER_ATTESTED');self.assertEqual(run['gates']['external_verification']['status'],'MISSING');self.assertIn('trusted host bridge',run['boundary'])

    def test_mcp_schema_does_not_allow_caller_to_inject_trusted_verification(self):
        head='abcdef1234567890';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke')
        result=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':ci,'smoke_witness':smoke,'trusted_external_verification':self.trusted(head,ci,smoke),'persist':False},expect_error=True);self.assertTrue(result['isError'])

    def test_host_internal_trusted_verifier_can_qualify_pure_predicate(self):
        head='abcdef1234567890';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke')
        result=evaluate_promotion('Server',head,self.surface(),ci,smoke,{'enabled':False},self.trusted(head,ci,smoke))
        self.assertEqual(result['status'],'QUALIFIED',result);self.assertTrue(result['promotion_allowed']);self.assertFalse(result['external_verification_required']);self.assertEqual(result['attestation_level'],'EXTERNALLY_VERIFIED');self.assertEqual(result['gates']['external_verification']['status'],'PASS')

    def test_untrusted_or_mismatched_trusted_verifier_blocks(self):
        head='abcdef1234567890';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke');trusted=self.trusted(head,ci,smoke);trusted['ci_ref']='ci://wrong'
        result=evaluate_promotion('Server',head,self.surface(),ci,smoke,{'enabled':False},trusted)
        self.assertEqual(result['status'],'BLOCKED');self.assertFalse(result['promotion_allowed']);self.assertIn('verification_ci_ref_mismatch',result['gates']['external_verification']['defects'])

    def test_mismatched_ci_head_blocks_before_trusted_qualification(self):
        head='abcdef1234567890';other='fedcba0987654321'
        run=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':self.witness(other,'ci'),'smoke_witness':self.witness(head,'smoke'),'persist':False})
        self.assertEqual(run['status'],'BLOCKED');self.assertFalse(run['promotion_allowed']);self.assertIn('head_mismatch',run['gates']['ci']['defects']);self.assertEqual(run['gates']['smoke']['status'],'PASS')

    def test_pure_predicate_blocks_surface_or_composition_failure(self):
        head='abcdef1234567890';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke')
        result=evaluate_promotion('Server',head,self.surface('FAIL','PASS'),ci,smoke,{'enabled':False});self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['gates']['surface']['status'],'FAIL')
        result=evaluate_promotion('Server',head,self.surface('PASS','FAIL'),ci,smoke,{'enabled':False});self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['gates']['composition']['status'],'FAIL')

    def test_local_git_mismatch_blocks_when_git_is_configured(self):
        head='abcdef1234567890';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke')
        result=evaluate_promotion('Server',head,self.surface(),ci,smoke,{'enabled':True,'head':'different1234567'})
        self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['gates']['local_git']['status'],'FAIL');self.assertIn('local_head_mismatch',result['gates']['local_git']['defects'])

    def test_promrun_persists_attested_ready_and_replays_frozen_inputs(self):
        head='abcdef1234567890';run=self.tool('athena_promotion_evaluate',{'git_head':head,'ci_witness':self.witness(head,'ci'),'smoke_witness':self.witness(head,'smoke')})
        self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('PROMRUN.'));self.assertEqual(run['status'],'ATTESTED_READY')
        stored=self.tool('athena_promotion_get',{'run_id':run['run_id']});self.assertEqual(stored['git_head'],head);self.assertEqual(stored['status'],'ATTESTED_READY');self.assertEqual(stored['certificate']['version'],PROMOTION_VERSION)
        replay=self.tool('athena_promotion_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay);self.assertEqual(replay['stored_status'],'ATTESTED_READY');self.assertEqual(replay['recomputed_status'],'ATTESTED_READY');self.assertEqual(replay['version'],PROMOTION_VERSION)
        recent=self.tool('athena_promotion_recent',{'limit':5});self.assertTrue(any(row['run_id']==run['run_id'] for row in recent))

    def test_historical_v1_qualified_receipt_remains_replayable_but_separate(self):
        head='legacyabcdef1234';ci=self.witness(head,'ci');smoke=self.witness(head,'smoke');inputs={'candidate_server':'Server','git_head':head,'surface_audit':self.surface(),'ci_witness':ci,'smoke_witness':smoke,'local_git_status':{'enabled':False}}
        cert=evaluate_promotion_v1(**inputs);self.assertEqual(cert['version'],PROMOTION_V1_VERSION);self.assertEqual(cert['status'],'QUALIFIED')
        payload={'version':cert['version'],'candidate_server':cert['candidate_server'],'git_head':cert['git_head'],'status':cert['status'],'gates':cert['gates']};dd=digest(payload,64);run_id='PROMRUN.LEGACY.TEST'
        with self.server.store.db:self.server.store.db.execute('INSERT INTO promotion_runs VALUES(?,?,?,?,?,?,?,?,?)',(run_id,'Server',head,'QUALIFIED',json.dumps(inputs,sort_keys=True),json.dumps(cert,sort_keys=True),dd,'EID.LEGACY.PROMOTION',0.0))
        replay=self.tool('athena_promotion_replay',{'run_id':run_id});self.assertTrue(replay['match'],replay);self.assertEqual(replay['version'],PROMOTION_V1_VERSION);self.assertEqual(replay['stored_status'],'QUALIFIED');self.assertEqual(replay['recomputed_status'],'QUALIFIED')
        bench=self.tool('athena_benchmark',{});self.assertEqual(bench['promotion_v1_qualified_historical'],1);self.assertEqual(bench['promotion_qualified'],0)

    def test_old_promrun_does_not_promote_new_head(self):
        old='aaaaaaaaaaaaaaa1';new='bbbbbbbbbbbbbbb2';oldrun=self.tool('athena_promotion_evaluate',{'git_head':old,'ci_witness':self.witness(old,'ci'),'smoke_witness':self.witness(old,'smoke')})
        replay=self.tool('athena_promotion_replay',{'run_id':oldrun['run_id']});self.assertTrue(replay['match']);self.assertEqual(replay['git_head'],old)
        blocked=self.tool('athena_promotion_evaluate',{'git_head':new,'ci_witness':self.witness(old,'ci'),'smoke_witness':self.witness(old,'smoke'),'persist':False});self.assertEqual(blocked['status'],'BLOCKED');self.assertEqual(blocked['git_head'],new)

    def test_promotion_resource_and_benchmark_state_current_trust_boundary(self):
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://promotion'})['result']['contents'][0]['text'])
        self.assertEqual(payload['version'],PROMOTION_VERSION);self.assertIn(PROMOTION_V1_VERSION,payload['compat']);self.assertIn('ATTESTED_READY',payload['law']);self.assertIn('trusted verifier',payload['law']);self.assertIn('caller witness packets',payload['boundary'])
        bench=self.tool('athena_benchmark',{})
        self.assertIn('promotion_attested_ready',bench);self.assertIn('promotion_v1_qualified_historical',bench);self.assertEqual(bench['promotion_version'],PROMOTION_VERSION)
        self.assertEqual(bench['unified_manifest_version'],'ATHENA.RUNTIME.UNIFIED.8')


if __name__=='__main__':unittest.main()

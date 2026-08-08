import tempfile
import unittest

from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION,GithubPromotionVerifier,REQUIRED_CHECKS
from athena_mcp.server import Server

HEAD='a'*40
REPO='demeet2k/athena-mcp-server'
RUN_ID='123456789'

def check(name,suite=77,run_id=RUN_ID,status='completed',conclusion='success',app='github-actions',head=HEAD,check_id=None):
    cid=check_id or {'syntax':1,'unit':2,'critical-invariants':3,'smoke':4}.get(name,99)
    return {'id':cid,'name':name,'status':status,'conclusion':conclusion,'head_sha':head,'html_url':f'https://github.com/{REPO}/actions/runs/{run_id}/job/{cid}','details_url':f'https://github.com/{REPO}/actions/runs/{run_id}/job/{cid}','check_suite':{'id':suite},'app':{'slug':app},'started_at':'2026-08-08T00:00:00Z','completed_at':'2026-08-08T00:01:00Z'}

def payload(rows):return {'total_count':len(rows),'check_runs':list(rows)}

class GithubPromotionVerifierTests(unittest.TestCase):
    def verifier(self,rows,env=None):
        merged={'ATHENA_GITHUB_REPOSITORY':REPO,'ATHENA_GITHUB_RUN_ID':RUN_ID}
        if env is not None:merged.update(env)
        return GithubPromotionVerifier(env=merged,fetch_json=lambda url,headers,timeout:payload(rows))

    def test_one_coherent_exact_run_is_verified(self):
        out=self.verifier([check(name) for name in REQUIRED_CHECKS]).verify(HEAD)
        self.assertEqual(out['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertEqual(out['status'],'VERIFIED');self.assertTrue(out['verified']);self.assertEqual(out['repository'],REPO);self.assertEqual(out['run_id'],RUN_ID);self.assertEqual(out['check_suite_id'],'77');self.assertEqual(set(out['checks']),set(REQUIRED_CHECKS));self.assertEqual(out['trusted_external_verification']['verifier'],'GITHUB_CHECK_RUNS_API/github-actions');self.assertEqual(out['trusted_external_verification']['ci_ref'],out['ci_witness']['ref']);self.assertEqual(out['trusted_external_verification']['smoke_ref'],out['smoke_witness']['ref'])

    def test_checks_from_different_suites_are_never_spliced(self):
        rows=[check('syntax',suite=10),check('unit',suite=10),check('critical-invariants',suite=11),check('smoke',suite=11)]
        out=self.verifier(rows).verify(HEAD);self.assertEqual(out['status'],'NO_QUALIFYING_CHECK_SUITE');self.assertFalse(out['verified']);self.assertIn('checks from different suites/runs are never spliced',out['boundary'])

    def test_host_run_binding_rejects_another_actions_run(self):
        rows=[check(name,run_id='999999999') for name in REQUIRED_CHECKS]
        out=self.verifier(rows).verify(HEAD);self.assertEqual(out['status'],'NO_QUALIFYING_CHECK_SUITE');self.assertFalse(out['verified']);self.assertEqual(out['run_id'],RUN_ID)

    def test_wrong_app_head_or_failed_check_cannot_qualify(self):
        self.assertEqual(self.verifier([check('syntax'),check('unit'),check('critical-invariants',app='other-app'),check('smoke')]).verify(HEAD)['status'],'NO_QUALIFYING_CHECK_SUITE')
        self.assertEqual(self.verifier([check('syntax'),check('unit'),check('critical-invariants'),check('smoke',conclusion='failure')]).verify(HEAD)['status'],'NO_QUALIFYING_CHECK_SUITE')
        self.assertEqual(self.verifier([check(name,head='b'*40) for name in REQUIRED_CHECKS]).verify(HEAD)['status'],'NO_QUALIFYING_CHECK_SUITE')

    def test_trusted_repository_is_host_config_not_caller_input(self):
        out=GithubPromotionVerifier(env={},fetch_json=lambda *args:payload([])).verify(HEAD);self.assertEqual(out['status'],'VERIFIER_UNAVAILABLE');self.assertFalse(out['verified']);self.assertIn('trusted_repository_not_configured',out['defects']);self.assertFalse(out['configuration']['configured'])

    def test_invalid_head_fails_before_network(self):
        called=[];out=GithubPromotionVerifier(env={'ATHENA_GITHUB_REPOSITORY':REPO},fetch_json=lambda *args:called.append(args)).verify('not-a-sha');self.assertEqual(out['status'],'INVALID_HEAD');self.assertFalse(called)

    def test_runtime_github_tool_creates_trusted_qualified_promrun_and_replays(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.aor_development.integrity.github_promotion_verifier=self.verifier([check(name) for name in REQUIRED_CHECKS])
            result=srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'athena_promotion_verify_github','arguments':{'git_head':HEAD}}})['result']['structuredContent']
            self.assertEqual(result['status'],'QUALIFIED',result);self.assertTrue(result['promotion_allowed']);self.assertEqual(result['attestation_level'],'EXTERNALLY_VERIFIED');self.assertTrue(result['persisted']);self.assertTrue(result['run_id'].startswith('PROMRUN.'));self.assertEqual(result['github_verification']['status'],'VERIFIED')
            replay=srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'athena_promotion_replay','arguments':{'run_id':result['run_id']}}})['result']['structuredContent'];self.assertTrue(replay['match'],replay);self.assertEqual(replay['stored_status'],'QUALIFIED');self.assertEqual(replay['recomputed_status'],'QUALIFIED')
            bench=srv.handle({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'athena_benchmark','arguments':{}}})['result']['structuredContent'];self.assertEqual(bench['promotion_v2_qualified'],1);self.assertEqual(bench['github_promotion_verifier_version'],GITHUB_PROMOTION_VERIFIER_VERSION);srv.store.close()

    def test_runtime_failed_verifier_creates_no_promrun(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.aor_development.integrity.github_promotion_verifier=self.verifier([check('syntax')])
            result=srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'athena_promotion_verify_github','arguments':{'git_head':HEAD}}})['result']['structuredContent'];self.assertEqual(result['status'],'NO_QUALIFYING_CHECK_SUITE');self.assertFalse(result['promotion_allowed']);self.assertEqual(srv.aor_development.integrity.promotion.benchmark()['promotion_runs'],0);srv.store.close()

if __name__=='__main__':unittest.main()

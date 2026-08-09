import json
import re
import tomllib
import unittest
from pathlib import Path

from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.promotion import PROMOTION_VERSION
from athena_mcp.unified_manifest import UNIFIED_MANIFEST_VERSION


class ReleaseDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.manifest=json.loads((cls.root/'release'/'v3.5.0.json').read_text(encoding='utf-8'))
        cls.notes=(cls.root/'release'/'v3.5.0.md').read_text(encoding='utf-8')
        cls.project=tomllib.loads((cls.root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        cls.workflow=(cls.root/'.github'/'workflows'/'release-v3.5.yml').read_text(encoding='utf-8')
        cls.gitignore=(cls.root/'.gitignore').read_text(encoding='utf-8')

    def test_release_identity_matches_current_package_and_runtime(self):
        m=self.manifest
        self.assertEqual(m['schema'],'ATHENA.RELEASE.DISTRIBUTION.2')
        self.assertEqual(m['version'],self.project['version']);self.assertEqual(m['version'],'3.5.0');self.assertEqual(m['tag'],'v3.5.0')
        self.assertEqual(m['package']['name'],self.project['name']);self.assertEqual(m['package']['entrypoint'],self.project['scripts']['athena-mcp']);self.assertEqual(m['package']['entrypoint'],'athena_mcp.server:main')
        self.assertEqual(m['runtime']['manifest'],UNIFIED_MANIFEST_VERSION);self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.12')
        self.assertEqual(m['runtime']['collective_frontier'],'COLLECTIVE_GENERALIZED_V16');self.assertEqual(m['runtime']['deployment_frontier'],'ATHENA.DEPLOYMENT.2')
        self.assertEqual(m['runtime']['promotion'],PROMOTION_VERSION);self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2');self.assertEqual(m['runtime']['trusted_verifier'],GITHUB_PROMOTION_VERIFIER_VERSION)

    def test_source_policy_requires_exact_master_and_all_five_gates(self):
        p=self.manifest['source_policy'];self.assertEqual(p['repository'],'demeet2k/athena-mcp-server');self.assertEqual(p['branch'],'master')
        self.assertTrue(p['publication_requires_exact_current_master']);self.assertTrue(p['publication_requires_clean_checkout']);self.assertTrue(p['publication_requires_five_stage_qualification']);self.assertTrue(p['exact_commit_is_bound_in_release_attestation'])
        self.assertTrue(p['critical_test_selectors_must_resolve_to_real_files'])
        self.assertTrue(p['validation_runs_on_master_push']);self.assertTrue(p['validation_runs_on_every_master_push']);self.assertTrue(p['master_push_validation_is_nonpublishing']);self.assertTrue(p['publication_requires_manual_workflow_dispatch']);self.assertTrue(p['non_pr_validation_requires_exact_current_master_at_package_readiness'])
        self.assertEqual(p['qualification_checks'],['syntax','unit','critical-invariants','smoke','promotion-qualification'])

    def test_required_assets_match_current_distribution(self):
        assets=set(self.manifest['release']['required_assets'])
        self.assertEqual(assets,{'athena_canonical_mcp-3.5.0-py3-none-any.whl','promotion-receipt.json','release-manifest.json','release-attestation.json','SHA256SUMS'})
        self.assertNotIn('athena_canonical_mcp-3.4.0-py3-none-any.whl',' '.join(sorted(assets)))

    def test_current_v16_v15_and_deployment_surface_is_explicit(self):
        tools=set(self.manifest['runtime']['required_tools'])
        for name in ('athena_structural_reliability_calibrate','athena_multistage_tv_dro_plan','athena_ordered_dag_posterior','athena_longitudinal_dr_multistage_crossfit','athena_gaussian_mixture_update','athena_approx_error_field','athena_coupled_model_robust_policy','athena_deployment_manifest','athena_deployment_validate','athena_deployment_activation_plan','athena_deployment_assess_canary','athena_deployment_verify_receipt','athena_promotion_evaluate','athena_promotion_verify_github'):
            self.assertIn(name,tools)
        resources=set(self.manifest['runtime']['required_resources'])
        for uri in ('athena://manifest','athena://runtime/unified-manifest','athena://promotion','athena://collective/v14','athena://collective/v15','athena://collective/v16','athena://deployment','athena://deployment/security','athena://deployment/rollout','athena://deployment/evidence'):
            self.assertIn(uri,resources)
        contracts=' '.join(self.manifest['runtime']['v16_contracts']).lower()
        for phrase in ('caller-topological-order-constrained','one to six binary treatment stages','finite gaussian-mixture','held-out residual quantile','one model is fixed','model/science/control state'):
            self.assertIn(phrase,contracts)

    def test_release_validation_runs_on_master_push_but_publish_remains_manual(self):
        w=self.workflow
        for fragment in (
            'pull_request:','push:','branches: [master]','workflow_dispatch:','package-readiness:','promotion-qualification:',
            "if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/master'",
            'RELEASE_HEAD: ${{ github.event.pull_request.head.sha || github.sha }}','git rev-parse origin/master',
            'scripts/qualify_github_head.py','actions/download-artifact@v5','actions/upload-artifact@v4',
            'release-candidate-v3.5.0-${{ env.RELEASE_HEAD }}','promotion-receipt-${{ env.RELEASE_HEAD }}',
            'python -m pip wheel --no-deps . -w dist','athena_mcp.server','ATHENA.RUNTIME.UNIFIED.12','COLLECTIVE_GENERALIZED_V16',
            'V16 generalized bounded models and authority boundaries','Deployment V2 composition and authority boundaries',
            'gh release create','--verify-tag','refs/tags/$TAG','TAG_TARGET','(cd dist && sha256sum -c SHA256SUMS)',
            'release-attestation.json','trusted_promotion',"if [ \"${{ github.event_name }}\" != \"pull_request\" ]; then",
            "'publication_performed':False",
        ):
            self.assertIn(fragment,w)
        self.assertNotRegex(w,re.compile(r'continue-on-error:\s*true'))
        publish=w[w.index('\n  publish:'):]
        self.assertIn("if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/master'",publish)
        self.assertNotIn("github.event_name == 'push'",publish)

    def test_every_master_push_is_validation_scoped_and_self_triggering(self):
        w=self.workflow;trigger=w[:w.index('\npermissions:')]
        self.assertIn('push:\n    branches: [master]',trigger);self.assertNotIn('paths:',trigger);self.assertNotIn('paths-ignore:',trigger)
        package=w[w.index('\n  package-readiness:'):w.index('\n  publish:')]
        self.assertIn('git fetch origin master --no-tags',package);self.assertIn('test "$(git rev-parse origin/master)" = "$RELEASE_HEAD"',package)

    def test_critical_test_patterns_select_real_nonempty_witnesses(self):
        critical=self.workflow[self.workflow.index('\n  critical-invariants:'):self.workflow.index('\n  smoke:')]
        patterns=re.findall(r"-p '([^']+)'",critical)
        self.assertGreaterEqual(len(patterns),13,patterns)
        for pattern in patterns:
            matches=list((self.root/'tests').glob(pattern));self.assertEqual(len(matches),1,(pattern,[path.name for path in matches]));self.assertTrue(matches[0].is_file(),pattern)
        for pattern in ('test_collective_v16.py','test_collective_v16_adversarial.py','test_collective_v16_unified.py'):
            self.assertIn(pattern,patterns)

    def test_job_level_env_blocks_use_contexts_legal_at_job_env_scope(self):
        lines=self.workflow.splitlines();in_job_env=False
        for line in lines:
            if line=='    env:':in_job_env=True;continue
            if in_job_env and not line.startswith('      '):in_job_env=False
            if in_job_env:self.assertNotIn('${{ env.',line,line)
        self.assertIn('ATHENA_PROMOTION_HEAD: ${{ github.event.pull_request.head.sha || github.sha }}',self.workflow)

    def test_package_readiness_preserves_clean_checkout_receipt_and_v16_surface(self):
        w=self.workflow;package=w[w.index('\n  package-readiness:'):w.index('\n  publish:')]
        ignored={line.strip() for line in self.gitignore.splitlines() if line.strip() and not line.lstrip().startswith('#')}
        self.assertIn('promotion-input/',ignored);self.assertIn('path: promotion-input',package);self.assertIn('test -z "$(git status --porcelain)"',package)
        for fragment in ('test "$(git rev-parse HEAD)" = "$RELEASE_HEAD"',"assert promotion['git_head']==os.environ['RELEASE_HEAD']","assert promotion['promotion']['status']=='QUALIFIED'","'release_commit':os.environ['RELEASE_HEAD']","'promrun':promotion['promotion']['run_id']","'verification_ref':promotion['verification_ref']","'receipt_sha256':sha(promo)",'athena_ordered_dag_posterior','athena_coupled_model_robust_policy',"assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.12'","assert manifest['collective_generalized']['version']=='COLLECTIVE_RUNTIME_V16'",'test "$TAG_TARGET" = "$RELEASE_HEAD"'):
            self.assertIn(fragment,w)

    def test_release_workflow_uses_least_privilege_until_manual_publish(self):
        w=self.workflow;self.assertIn('permissions:\n  contents: read\n  actions: read\n  checks: read',w);publish=w[w.index('\n  publish:'):]
        self.assertIn('permissions:\n      contents: write\n      actions: read\n      checks: read',publish);self.assertEqual(w.count('contents: write'),1,w);self.assertNotIn('contents: write',w[:w.index('\n  publish:')])

    def test_release_notes_preserve_v16_claim_ceilings(self):
        n=self.notes
        for phrase in ('ATHENA 3.5.0','Collective Generalized V16','UNIFIED.12','Deployment.2','ORDER_CONSTRAINED_DAG_POSTERIOR != GENERAL_CAUSAL_GRAPH_POSTERIOR','CALLER_ORDER != DISCOVERED_CAUSAL_ORDER','BOUNDED_MULTISTAGE_CROSS_FITTED_DR != ARBITRARY_HORIZON_LONGITUDINAL_THEOREM','FINITE_GAUSSIAN_MIXTURE != GENERAL_NON_GAUSSIAN_BAYES','CV_RESIDUAL_QUANTILE != DISTRIBUTION_FREE_ERROR_CERTIFICATE','FINITE_FIXED_MODEL_FAMILY_POLICY_EVALUATION != GENERAL_NONRECTANGULAR_DRO_OPTIMIZATION','ZERO_TEST_SELECTION != PROOF','AUTOMATIC_VALIDATION != AUTOMATIC_PUBLICATION','BRANCH_RECEIPT != MERGED_HEAD_RECEIPT'):
            self.assertIn(phrase,n)

    def test_authority_boundaries_do_not_collapse_v16_distribution_into_truth_or_execution(self):
        boundaries=' '.join(self.manifest['authority_boundaries']).lower()
        for phrase in ('not deployment','not empirical truth','not a general causal graph posterior','does not establish arbitrary-horizon','not general non-gaussian bayes','not a distribution-free','not general non-rectangular dro','not github administrative hardening','does not authorize treatment execution','external-control planning','v3.4 release attestation'):
            self.assertIn(phrase,boundaries)

    def test_v34_release_artifacts_remain_historical_not_current(self):
        old=json.loads((self.root/'release'/'v3.4.0.json').read_text())
        self.assertEqual(old['version'],'3.4.0');self.assertEqual(old['runtime']['manifest'],'ATHENA.RUNTIME.UNIFIED.11');self.assertEqual(old['runtime']['collective_frontier'],'COLLECTIVE_CALIBRATED_V15')
        self.assertTrue((self.root/'.github/workflows/release-v3.4.yml').exists())
        self.assertNotEqual(old['version'],self.manifest['version'])


if __name__=='__main__':unittest.main()

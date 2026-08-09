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
        cls.manifest=json.loads((cls.root/'release'/'v3.4.0.json').read_text(encoding='utf-8'))
        cls.notes=(cls.root/'release'/'v3.4.0.md').read_text(encoding='utf-8')
        cls.project=tomllib.loads((cls.root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        cls.workflow=(cls.root/'.github'/'workflows'/'release-v3.4.yml').read_text(encoding='utf-8')
        cls.gitignore=(cls.root/'.gitignore').read_text(encoding='utf-8')

    def test_release_identity_matches_current_package_and_runtime(self):
        m=self.manifest
        self.assertEqual(m['schema'],'ATHENA.RELEASE.DISTRIBUTION.2')
        self.assertEqual(m['version'],self.project['version']);self.assertEqual(m['version'],'3.4.0');self.assertEqual(m['tag'],'v3.4.0')
        self.assertEqual(m['package']['name'],self.project['name']);self.assertEqual(m['package']['entrypoint'],self.project['scripts']['athena-mcp']);self.assertEqual(m['package']['entrypoint'],'athena_mcp.server:main')
        self.assertEqual(m['runtime']['manifest'],UNIFIED_MANIFEST_VERSION);self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.11')
        self.assertEqual(m['runtime']['collective_frontier'],'COLLECTIVE_CALIBRATED_V15');self.assertEqual(m['runtime']['deployment_frontier'],'ATHENA.DEPLOYMENT.2')
        self.assertEqual(m['runtime']['promotion'],PROMOTION_VERSION);self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2');self.assertEqual(m['runtime']['trusted_verifier'],GITHUB_PROMOTION_VERIFIER_VERSION)

    def test_source_policy_requires_exact_master_and_all_five_gates(self):
        p=self.manifest['source_policy'];self.assertEqual(p['repository'],'demeet2k/athena-mcp-server');self.assertEqual(p['branch'],'master')
        self.assertTrue(p['publication_requires_exact_current_master']);self.assertTrue(p['publication_requires_clean_checkout']);self.assertTrue(p['publication_requires_five_stage_qualification']);self.assertTrue(p['exact_commit_is_bound_in_release_attestation'])
        self.assertTrue(p['critical_test_selectors_must_resolve_to_real_files'])
        self.assertEqual(p['qualification_checks'],['syntax','unit','critical-invariants','smoke','promotion-qualification'])

    def test_required_assets_match_current_distribution(self):
        assets=set(self.manifest['release']['required_assets'])
        self.assertEqual(assets,{'athena_canonical_mcp-3.4.0-py3-none-any.whl','promotion-receipt.json','release-manifest.json','release-attestation.json','SHA256SUMS'})
        self.assertNotIn('athena_canonical_mcp-3.3.0-py3-none-any.whl',' '.join(sorted(assets)))

    def test_current_v15_and_deployment_surface_is_explicit_in_manifest(self):
        tools=set(self.manifest['runtime']['required_tools'])
        for name in ('athena_structural_reliability_calibrate','athena_longitudinal_tmle_crossfit','athena_sequential_dr_policy_crossfit','athena_joint_gaussian_update','athena_joint_gaussian_control','athena_approx_error_transport','athena_multistage_tv_dro_plan','athena_deployment_manifest','athena_deployment_validate','athena_deployment_activation_plan','athena_deployment_assess_canary','athena_deployment_verify_receipt','athena_promotion_evaluate','athena_promotion_verify_github'):
            self.assertIn(name,tools)
        resources=set(self.manifest['runtime']['required_resources'])
        for uri in ('athena://manifest','athena://runtime/unified-manifest','athena://promotion','athena://collective/v14','athena://collective/v15','athena://deployment','athena://deployment/security','athena://deployment/rollout','athena://deployment/evidence'):
            self.assertIn(uri,resources)
        contracts=' '.join(self.manifest['runtime']['v15_contracts']).lower()
        for phrase in ('duplicate-pooled','stage-2 tmle','a1 dynamic policy uses baseline only','unknown gaussian coefficient','radius-eligible local certificate','rectangular tv-dro'):
            self.assertIn(phrase,contracts)

    def test_release_workflow_is_pr_testable_but_publish_is_manual_master_only(self):
        w=self.workflow
        for fragment in ('pull_request:','workflow_dispatch:','package-readiness:','promotion-qualification:',"if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/master'",'RELEASE_HEAD: ${{ github.event.pull_request.head.sha || github.sha }}','git rev-parse origin/master','scripts/qualify_github_head.py','actions/download-artifact@v5','actions/upload-artifact@v4','release-candidate-v3.4.0-${{ env.RELEASE_HEAD }}','promotion-receipt-${{ env.RELEASE_HEAD }}','python -m pip wheel --no-deps . -w dist','athena_mcp.server','ATHENA.RUNTIME.UNIFIED.11','COLLECTIVE_CALIBRATED_V15','V15 calibrated continuous control and authority boundaries','Deployment V2 composition and authority boundaries','gh release create','--verify-tag','refs/tags/$TAG','TAG_TARGET','(cd dist && sha256sum -c SHA256SUMS)','release-attestation.json','trusted_promotion'):
            self.assertIn(fragment,w)
        self.assertNotRegex(w,re.compile(r'(?m)^\s*push:\s*$'));self.assertNotRegex(w,re.compile(r'continue-on-error:\s*true'))

    def test_critical_test_patterns_select_real_nonempty_witnesses(self):
        critical=self.workflow[self.workflow.index('\n  critical-invariants:'):self.workflow.index('\n  smoke:')]
        patterns=re.findall(r"-p '([^']+)'",critical)
        self.assertGreaterEqual(len(patterns),16,patterns)
        for pattern in patterns:
            matches=list((self.root/'tests').glob(pattern))
            self.assertEqual(len(matches),1,(pattern,[path.name for path in matches]))
            self.assertTrue(matches[0].is_file(),pattern)

    def test_job_level_env_blocks_use_contexts_legal_at_job_env_scope(self):
        lines=self.workflow.splitlines();in_job_env=False
        for line in lines:
            if line=='    env:':in_job_env=True;continue
            if in_job_env and not line.startswith('      '):in_job_env=False
            if in_job_env:self.assertNotIn('${{ env.',line,line)
        self.assertIn('ATHENA_PROMOTION_HEAD: ${{ github.event.pull_request.head.sha || github.sha }}',self.workflow)

    def test_package_readiness_preserves_clean_checkout_receipt_and_wheel_surface(self):
        w=self.workflow;package=w[w.index('\n  package-readiness:'):w.index('\n  publish:')]
        ignored={line.strip() for line in self.gitignore.splitlines() if line.strip() and not line.lstrip().startswith('#')}
        self.assertIn('promotion-input/',ignored);self.assertIn('path: promotion-input',package);self.assertIn('test -z "$(git status --porcelain)"',package)
        for fragment in ('test "$(git rev-parse HEAD)" = "$RELEASE_HEAD"',"assert promotion['git_head']==os.environ['RELEASE_HEAD']","assert promotion['promotion']['status']=='QUALIFIED'","'release_commit':os.environ['RELEASE_HEAD']","'promrun':promotion['promotion']['run_id']","'verification_ref':promotion['verification_ref']","'receipt_sha256':sha(promo)",'athena_structural_reliability_calibrate','athena_deployment_manifest',"assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.11'",'test "$TAG_TARGET" = "$RELEASE_HEAD"'):
            self.assertIn(fragment,w)

    def test_release_workflow_uses_least_privilege_until_manual_publish(self):
        w=self.workflow;self.assertIn('permissions:\n  contents: read\n  actions: read\n  checks: read',w);publish=w[w.index('\n  publish:'):]
        self.assertIn('permissions:\n      contents: write\n      actions: read\n      checks: read',publish);self.assertEqual(w.count('contents: write'),1,w);self.assertNotIn('contents: write',w[:w.index('\n  publish:')])

    def test_release_notes_preserve_v15_deployment_and_trust_claim_ceilings(self):
        n=self.notes
        for phrase in (
            'ATHENA 3.4.0','Collective Calibrated V15','UNIFIED.11','Deployment.2','GITHUB_PROMOTION_VERIFIER.1',
            'OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR',
            'IDENTICAL_CALIBRATION_COORDINATE != MULTIPLE_FITTED_VALUES',
            'CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM',
            'STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION',
            'CROSS_FITTED_SEQUENTIAL_DR != GENERAL_OFF_POLICY_CAUSAL_VALUE',
            'DECISION_TIME_HISTORY != FULL_ROW_STATE',
            'LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES',
            'UNKNOWN_COEFFICIENT != ZERO_COEFFICIENT',
            'NONFINITE_NUMERIC_STATE != MODEL_COORDINATE',
            'DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH',
            'GEOMETRIC_NEAREST_WITNESS != TIGHTEST_ERROR_ENVELOPE_WITNESS',
            'GLOBAL_ENVELOPE != RADIUS_ELIGIBLE_LOCAL_CERTIFICATE',
            'RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO',
            'UNKNOWN_STATE_COORDINATE != UNUSED_METADATA',
            'NONFINITE_TRANSITION != PROBABILITY_MODEL',
            'ZERO_TEST_SELECTION != PROOF',
            'one coherent trusted Actions suite',
            'This release certifies repository/package/distribution state. It is not a production deployment',
        ):self.assertIn(phrase,n)

    def test_authority_boundaries_do_not_collapse_distribution_into_truth_admin_or_deployment(self):
        boundaries=' '.join(self.manifest['authority_boundaries']).lower()
        for phrase in ('not deployment','not empirical truth','do not become y1 authority','does not prove causal identification','are rejected','not github administrative hardening','does not authorize treatment execution','external-control planning','v3.3.0 release attestation is not evidence for v3.4.0 bytes'):
            self.assertIn(phrase,boundaries)


if __name__=='__main__':unittest.main()

import tomllib
import unittest
from pathlib import Path

import athena_mcp
from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.promotion import PROMOTION_VERSION
from athena_mcp.unified_manifest import UNIFIED_MANIFEST_VERSION

ROOT=Path(__file__).resolve().parents[1]

def text(path):return (ROOT/path).read_text(encoding='utf-8')


class DocumentationConsistencyTests(unittest.TestCase):
    def test_current_v16_release_brain_coordinates_agree(self):
        project=tomllib.loads(text('pyproject.toml'))['project']
        self.assertEqual(project['version'],'3.5.0');self.assertEqual(athena_mcp.__version__,'3.5.0');self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.12')
        self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2');self.assertEqual(GITHUB_PROMOTION_VERIFIER_VERSION,'ATHENA.GITHUB.PROMOTION.VERIFIER.1')
        readme=text('README.md')
        for phrase in ('# ATHENA Canonical MCP v3.5','Collective V1–V16','ATHENA.RUNTIME.UNIFIED.12','COLLECTIVE_GENERALIZED=<OG,MH,GM,EF,NR,L>','athena://collective/v16','athena-canonical-mcp 3.5.0','athena_ordered_dag_posterior','athena_longitudinal_dr_multistage_crossfit','athena_gaussian_mixture_update','athena_approx_error_field','athena_coupled_model_robust_policy','ORDER_CONSTRAINED_DAG_POSTERIOR != GENERAL_CAUSAL_GRAPH_POSTERIOR','BOUNDED_MULTISTAGE_CROSS_FITTED_DR != ARBITRARY_HORIZON_LONGITUDINAL_THEOREM','FINITE_GAUSSIAN_MIXTURE != GENERAL_NON_GAUSSIAN_BAYES','CV_RESIDUAL_QUANTILE != DISTRIBUTION_FREE_ERROR_CERTIFICATE','FINITE_FIXED_MODEL_FAMILY_POLICY_EVALUATION != GENERAL_NONRECTANGULAR_DRO_OPTIMIZATION','ATHENA.DEPLOYMENT.2','GITHUB_PROMOTION_VERIFIER.1','ATTESTED_READY','promotion-qualification','Historical architecture'):
            self.assertIn(phrase,readme)

    def test_v16_versioned_architecture_and_migration_preserve_v15_history(self):
        architecture=text('spec/ARCHITECTURE_V16.md')
        for phrase in ('ATHENA ARCHITECTURE V16','COLLECTIVE_GENERALIZED=<OG,MH,GM,EF,NR,L>','bounded subsets','ORDER_CONSTRAINED_DAG_POSTERIOR != GENERAL_CAUSAL_GRAPH_POSTERIOR','V16_RUNTIME_INTEGRATION = HOLD'):
            self.assertIn(phrase,architecture)
        migration=text('spec/MIGRATION_V16.md')
        for phrase in ('MIGRATION TO COLLECTIVE GENERALIZED V16','3.4.0 -> 3.5.0','ATHENA.RUNTIME.UNIFIED.11 -> ATHENA.RUNTIME.UNIFIED.12','NEW_SUCCESSOR != REPLAY_OLD_BASE','OLD_RELEASE_RECEIPT != NEW_RELEASE_EVIDENCE','BRANCH_RECEIPT != MERGED_HEAD_RECEIPT'):
            self.assertIn(phrase,migration)
        unified=text('spec/ATHENA_UNIFIED_V16.md')
        for phrase in ('athena-canonical-mcp@3.5.0','ATHENA.RUNTIME.UNIFIED.12','COLLECTIVE_GENERALIZED=<OG,MH,GM,EF,NR,L>','athena://collective/v16','V16_TOOL_SET ∩ INHERITED_TOOL_SET = ∅','V16_PACKAGE_RELEASE_IDENTITY = HOLD'):
            self.assertIn(phrase,unified)
        runtime=text('spec/COLLECTIVE_RUNTIME_V16.md')
        for phrase in ('COLLECTIVE RUNTIME V16','EXACT_ORDER_CONSTRAINED_LINEAR_GAUSSIAN_DAG_POSTERIOR','BOUNDED_MULTISTAGE_CROSS_FITTED_SEQUENTIAL_DR','EXACT_FINITE_GAUSSIAN_MIXTURE_LINEAR_OBSERVATION_UPDATE','CV_CALIBRATED_RBF_APPROXIMATION_ERROR_FIELD','EXACT_SUPPLIED_POLICY_SET_COUPLED_MODEL_FAMILY_ROBUST_EVALUATION'):
            self.assertIn(phrase,runtime)
        for historical in ('spec/ARCHITECTURE_V15.md','spec/MIGRATION_V15.md','spec/ATHENA_UNIFIED_V15.md','spec/COLLECTIVE_RUNTIME_V15.md'):
            self.assertTrue((ROOT/historical).exists(),historical)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.11',text('spec/ATHENA_UNIFIED_V15.md'))

    def test_v16_runtime_specs_preserve_bounded_claim_ceilings(self):
        joined='\n'.join(text(path) for path in ('spec/ARCHITECTURE_V16.md','spec/ATHENA_UNIFIED_V16.md','spec/COLLECTIVE_RUNTIME_V16.md'))
        for phrase in ('ORDER_CONSTRAINED_DAG_POSTERIOR != GENERAL_CAUSAL_GRAPH_POSTERIOR','BOUNDED_MULTISTAGE_CROSS_FITTED_DR != ARBITRARY_HORIZON_LONGITUDINAL_THEOREM','FINITE_GAUSSIAN_MIXTURE != GENERAL_NON_GAUSSIAN_BAYES','CV_RESIDUAL_QUANTILE != DISTRIBUTION_FREE_ERROR_CERTIFICATE','FINITE_FIXED_MODEL_FAMILY_POLICY_EVALUATION != GENERAL_NONRECTANGULAR_DRO_OPTIMIZATION','COLLECTIVE_GENERALIZED != DEPLOYMENT_AUTHORITY','MODEL_STATE != COORDINATION_AUTHORITY'):
            self.assertIn(phrase,joined)

    def test_executable_witnesses_name_v16_deployment_and_host_bound_qualification(self):
        smoke=text('smoke.py')
        for phrase in ("init['serverInfo']['version']=='3.5.0'","manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.12'",'athena_ordered_dag_posterior','athena_longitudinal_dr_multistage_crossfit','athena_gaussian_mixture_update','athena_approx_error_field','athena_coupled_model_robust_policy','athena_deployment_manifest',"promotion['status']=='ATTESTED_READY'",'ATHENA.GITHUB.PROMOTION.VERIFIER.1'):
            self.assertIn(phrase,smoke)
        ci=text('.github/workflows/ci.yml')
        for phrase in ('V16 generalized bounded models and authority boundaries','test_collective_v16.py','test_collective_v16_adversarial.py','test_collective_v16_unified.py','GitHub trusted promotion verifier','promotion-qualification','scripts/qualify_github_head.py'):
            self.assertIn(phrase,ci)
        release=text('.github/workflows/release-v3.5.yml')
        for phrase in ('Release Distribution V3.5','V16 generalized bounded models and authority boundaries',"test_collective_v16_unified.py",'promotion-qualification','release-candidate-v3.5.0-${{ env.RELEASE_HEAD }}','ATHENA.RUNTIME.UNIFIED.12','COLLECTIVE_GENERALIZED_V16'):
            self.assertIn(phrase,release)

        for historical in ('.github/workflows/release-v3.3.yml','.github/workflows/release-v3.4.yml'):
            self.assertTrue((ROOT/historical).exists(),historical)
        self.assertIn('Release Distribution V3.4',text('.github/workflows/release-v3.4.yml'))
        self.assertIn('release/v3.4.0.json',text('.github/workflows/release-v3.4.yml'))
        self.assertNotIn('release/v3.5.0.json',text('.github/workflows/release-v3.4.yml'))

        verifier=text('athena_mcp/github_promotion_verifier.py')
        for phrase in ('ATHENA.GITHUB.PROMOTION.VERIFIER.1',"REQUIRED_CHECKS=('syntax','unit','critical-invariants','smoke')",'github-actions','checks from different suites/runs are never spliced','ATHENA_GITHUB_REPOSITORY','ATHENA_GITHUB_RUN_ID'):
            self.assertIn(phrase,verifier)


if __name__=='__main__':unittest.main()

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
    def test_current_v15_release_brain_coordinates_agree(self):
        project=tomllib.loads(text('pyproject.toml'))['project']
        self.assertEqual(project['version'],'3.4.0');self.assertEqual(athena_mcp.__version__,'3.4.0');self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.11')
        self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2');self.assertEqual(GITHUB_PROMOTION_VERIFIER_VERSION,'ATHENA.GITHUB.PROMOTION.VERIFIER.1')
        readme=text('README.md')
        for phrase in ('# ATHENA Canonical MCP v3.4','Collective V1–V15','ATHENA.RUNTIME.UNIFIED.11','COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>','athena://collective/v15','athena-canonical-mcp 3.4.0','athena_structural_reliability_calibrate','athena_longitudinal_tmle_crossfit','athena_sequential_dr_policy_crossfit','athena_joint_gaussian_update','athena_joint_gaussian_control','athena_approx_error_transport','athena_multistage_tv_dro_plan','OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR','CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM','LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES','DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH','RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO','ATHENA.DEPLOYMENT.2','GITHUB_PROMOTION_VERIFIER.1','ATTESTED_READY','promotion-qualification','Historical architecture'):
            self.assertIn(phrase,readme)

    def test_v15_versioned_architecture_and_migration_preserve_v14_history(self):
        architecture=text('spec/ARCHITECTURE_V15.md')
        for phrase in ('ATHENA ARCHITECTURE V15','COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>','FIBER_MOTION != BASE_CANON_MUTATION','CROSS_FITTING != IDENTIFICATION','COLLECTIVE_CALIBRATED != DEPLOYMENT_AUTHORITY != COORDINATION_AUTHORITY'):
            self.assertIn(phrase,architecture)
        migration=text('spec/MIGRATION_V15.md')
        for phrase in ('MIGRATION TO V15','3.3.0 -> 3.4.0','ATHENA.RUNTIME.UNIFIED.10 -> ATHENA.RUNTIME.UNIFIED.11','NEW_SUCCESSOR != REPLAY_OLD_BASE','true two-parent Git braid','Deployment.2','OLD_RELEASE_RECEIPT != NEW_RELEASE_EVIDENCE'):
            self.assertIn(phrase,migration)
        for historical in ('spec/ARCHITECTURE_V14.md','spec/MIGRATION_V14.md','spec/ATHENA_UNIFIED_V14.md','spec/COLLECTIVE_RUNTIME_V14.md'):
            self.assertTrue((ROOT/historical).exists(),historical)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.10',text('spec/ARCHITECTURE_V14.md'))

    def test_v15_runtime_specs_preserve_claim_ceilings(self):
        unified=text('spec/ATHENA_UNIFIED_V15.md')
        for phrase in ('athena-canonical-mcp@3.4.0','ATHENA.RUNTIME.UNIFIED.11','COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>','athena://collective/v15','Deployment.2','COLLECTIVE_CALIBRATED != DEPLOYMENT_AUTHORITY','VERIFIER_IMPLEMENTED != HEAD_QUALIFIED'):
            self.assertIn(phrase,unified)
        runtime=text('spec/COLLECTIVE_RUNTIME_V15.md')
        for phrase in ('COLLECTIVE RUNTIME V15','OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR','CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM','CROSS_FITTED_SEQUENTIAL_DR != GENERAL_OFF_POLICY_CAUSAL_VALUE','LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES','GAUSSIAN_LINEAR_CONTROL != GENERAL_BELIEF_MDP','DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH','RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO','V15_STATE != Y1_AUTHORITY'):
            self.assertIn(phrase,runtime)

    def test_executable_witnesses_name_v15_deployment_and_host_bound_qualification(self):
        smoke=text('smoke.py')
        for phrase in ("init['serverInfo']['version']=='3.4.0'","manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.11'",'athena_structural_reliability_calibrate','athena_longitudinal_tmle_crossfit','athena_sequential_dr_policy_crossfit','athena_joint_gaussian_update','athena_approx_error_transport','athena_multistage_tv_dro_plan','athena_deployment_manifest',"promotion['status']=='ATTESTED_READY'",'ATHENA.GITHUB.PROMOTION.VERIFIER.1'):
            self.assertIn(phrase,smoke)
        ci=text('.github/workflows/ci.yml')
        for phrase in ('V15 calibrated continuous control and authority boundaries','GitHub trusted promotion verifier','promotion-qualification','scripts/qualify_github_head.py'):
            self.assertIn(phrase,ci)
        release=text('.github/workflows/release-v3.4.yml')
        for phrase in ('Release Distribution V3.4','V15 calibrated continuous control and authority boundaries','Deployment V2 composition and authority boundaries',"test_collective_v15_unified.py",'promotion-qualification','release-candidate-v3.4.0-${{ env.RELEASE_HEAD }}','ATHENA.RUNTIME.UNIFIED.11','COLLECTIVE_CALIBRATED_V15'):
            self.assertIn(phrase,release)

        # V3.3 is no longer the current package identity, but live master retains
        # its immutable manual publication workflow because the already-published
        # V3.3 OCI activation/relay contract references that historical authority.
        historical=ROOT/'.github/workflows/release-v3.3.yml'
        self.assertTrue(historical.exists())
        historical_text=historical.read_text(encoding='utf-8')
        self.assertIn('Release Distribution V3.3',historical_text)
        self.assertIn('release/v3.3.0.json',historical_text)
        self.assertIn('workflow_dispatch:',historical_text)
        self.assertNotIn('release/v3.4.0.json',historical_text)

        verifier=text('athena_mcp/github_promotion_verifier.py')
        for phrase in ('ATHENA.GITHUB.PROMOTION.VERIFIER.1',"REQUIRED_CHECKS=('syntax','unit','critical-invariants','smoke')",'github-actions','checks from different suites/runs are never spliced','ATHENA_GITHUB_REPOSITORY','ATHENA_GITHUB_RUN_ID'):
            self.assertIn(phrase,verifier)


if __name__=='__main__':unittest.main()

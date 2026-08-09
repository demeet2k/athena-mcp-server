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
    def test_current_v14_release_brain_coordinates_agree(self):
        project=tomllib.loads(text('pyproject.toml'))['project']
        self.assertEqual(project['version'],'3.3.0')
        self.assertEqual(athena_mcp.__version__,'3.3.0')
        self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.10')
        self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2')
        self.assertEqual(GITHUB_PROMOTION_VERIFIER_VERSION,'ATHENA.GITHUB.PROMOTION.VERIFIER.1')
        readme=text('README.md')
        for phrase in (
            '# ATHENA Canonical MCP v3.3','Collective V1–V14','ATHENA.RUNTIME.UNIFIED.10','COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>',
            'athena://collective/v14','athena-canonical-mcp 3.3.0','athena_joint_factor_belief','athena_structural_bootstrap_ensemble','athena_joint_science_evi',
            'athena_sequential_dr_policy_value','athena_joint_policy_robust','athena_gp_resolution_route','athena_two_stage_resource_plan',
            'FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR','BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR',
            'STAGE2_POLICY_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_POLICY_EVALUATION',
            'QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE','FINITE_TWO_STAGE_SCENARIO_RECOURSE != GENERAL_MULTISTAGE_STOCHASTIC_PROGRAM',
            'GITHUB_PROMOTION_VERIFIER.1','ATTESTED_READY != QUALIFIED','CHECKS_FROM_DIFFERENT_SUITES_OR_RUNS != ONE_TRUSTED_QUALIFICATION','promotion-qualification',
            'prompt/frontier','Message Board/cohesion','Historical architecture',
        ):self.assertIn(phrase,readme)

    def test_v14_versioned_architecture_and_migration_preserve_history(self):
        architecture=text('spec/ARCHITECTURE_V14.md')
        for phrase in ('ATHENA Architecture V14','athena-canonical-mcp 3.3.0','ATHENA.RUNTIME.UNIFIED.10','COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>','FIBER_MOTION != BASE_CANON_MUTATION','QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE','GITHUB_PROMOTION_VERIFIER.1','prompt/frontier'):
            self.assertIn(phrase,architecture)
        migration=text('spec/MIGRATION_V14.md')
        for phrase in ('ATHENA Migration V14','UNIFIED.9 → UNIFIED.10','975d68c04b113e2b02899406216c4f327621f5f8','hundreds of commits beyond Ω13','_init_v32_legacy.py','OLD_MODEL_STATE != IMPLICIT_JOINT_POSTERIOR','BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR','VERIFIER_IMPLEMENTATION_EXISTS != THIS_HEAD_IS_QUALIFIED','OLD_RELEASE_RECEIPT != NEW_RELEASE_EVIDENCE'):
            self.assertIn(phrase,migration)
        historical_arch=text('ARCHITECTURE.md');historical_migration=text('MIGRATION.md')
        self.assertIn('Collective V1–V13',historical_arch)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.9',historical_arch)
        self.assertIn('Collective V1–V13',historical_migration)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.9',historical_migration)

    def test_v14_runtime_specs_preserve_claim_ceilings(self):
        unified=text('spec/ATHENA_UNIFIED_V14.md')
        for phrase in ('athena-canonical-mcp 3.3.0','ATHENA.RUNTIME.UNIFIED.10','athena_claim_*','athena_discovery_claim_*','athena_joint_factor_belief','athena_structural_bootstrap_ensemble','athena_joint_science_evi','athena_sequential_dr_policy_value','athena_joint_policy_robust','athena_gp_resolution_route','athena_two_stage_resource_plan','cross_fitted=false','ATTESTED_READY != QUALIFIED','CHECKS_FROM_DIFFERENT_SUITES_OR_RUNS != ONE_TRUSTED_QUALIFICATION'):
            self.assertIn(phrase,unified)
        runtime=text('spec/COLLECTIVE_RUNTIME_V14.md')
        for phrase in ('ATHENA COLLECTIVE RUNTIME V14','COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>','FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR','BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR','JOINT_SCIENCE_EVI != OBSERVATION_OR_EVIDENCE','SEQUENTIAL_DR_POLICY_VALUE != GENERAL_LONGITUDINAL_CAUSAL_VALUE_THEOREM','FINITE_SCENARIO_ROBUST_POLICY != GENERAL_ROBUST_CONTROL','QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE','FINITE_TWO_STAGE_SCENARIO_RECOURSE != GENERAL_MULTISTAGE_STOCHASTIC_PROGRAM'):
            self.assertIn(phrase,runtime)

    def test_executable_witnesses_name_v14_and_host_bound_qualification(self):
        smoke=text('smoke.py')
        for phrase in ("init['serverInfo']['version']=='3.3.0'","manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.10'",'athena_joint_factor_belief','athena_structural_bootstrap_ensemble','athena_joint_science_evi','athena_sequential_dr_policy_value','athena_joint_policy_robust','athena_gp_resolution_route','athena_two_stage_resource_plan',"promotion['status']=='ATTESTED_READY'",'ATHENA.GITHUB.PROMOTION.VERIFIER.1'):
            self.assertIn(phrase,smoke)
        ci=text('.github/workflows/ci.yml')
        for phrase in ('Documentation and repository-brain consistency','GitHub trusted promotion verifier','Promotion trust and exact-head predicate','promotion-qualification','scripts/qualify_github_head.py'):
            self.assertIn(phrase,ci)
        release=text('.github/workflows/release-v3.3.yml')
        for phrase in ('Release Distribution V3.3','V14 joint posterior synthesis and authority boundaries',"test_collective_v14_unified.py",'promotion-qualification','release-candidate-v3.3.0-${{ env.RELEASE_HEAD }}','ATHENA.RUNTIME.UNIFIED.10','COLLECTIVE_SYNTHESIS_V14'):
            self.assertIn(phrase,release)
        verifier=text('athena_mcp/github_promotion_verifier.py')
        for phrase in ('ATHENA.GITHUB.PROMOTION.VERIFIER.1',"REQUIRED_CHECKS=('syntax','unit','critical-invariants','smoke')",'github-actions','checks from different suites/runs are never spliced','ATHENA_GITHUB_REPOSITORY','ATHENA_GITHUB_RUN_ID'):
            self.assertIn(phrase,verifier)


if __name__=='__main__':unittest.main()

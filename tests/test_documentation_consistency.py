import tomllib
import unittest
from pathlib import Path

import athena_mcp
from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.promotion import PROMOTION_VERSION
from athena_mcp.unified_manifest import UNIFIED_MANIFEST_VERSION


ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class DocumentationConsistencyTests(unittest.TestCase):
    def test_release_manifest_and_current_brain_coordinates_agree(self):
        project = tomllib.loads(text('pyproject.toml'))['project']
        self.assertEqual(project['version'], '3.2.0')
        self.assertEqual(athena_mcp.__version__, '3.2.0')
        self.assertEqual(UNIFIED_MANIFEST_VERSION, 'ATHENA.RUNTIME.UNIFIED.9')
        self.assertEqual(PROMOTION_VERSION, 'ATHENA.PROMOTION.2')
        self.assertEqual(GITHUB_PROMOTION_VERIFIER_VERSION,'ATHENA.GITHUB.PROMOTION.VERIFIER.1')

        readme = text('README.md')
        for phrase in ('# ATHENA Canonical MCP v3.2','Collective V1–V13','ATHENA.RUNTIME.UNIFIED.9','PROMOTION.2','GITHUB_PROMOTION_VERIFIER.1','ATTESTED_READY != QUALIFIED','CHECKS_FROM_DIFFERENT_SUITES_OR_RUNS != ONE_TRUSTED_QUALIFICATION','athena://collective/v13','athena-canonical-mcp 3.2.0','COLLECTIVE_ROBUST=<HB,FG,JD,FC,LT,DP,DR,L>','athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select','QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES','STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION','promotion-qualification','External control-plane boundary'):
            self.assertIn(phrase, readme)
        self.assertNotIn('# ATHENA Canonical MCP v3.1 — AΩR × Collective V1–V12 Unified Runtime', readme)

        architecture = text('ARCHITECTURE.md')
        for phrase in ('# ATHENA Unified Architecture — AΩR × Collective V1–V13','Robust Continuous/Causal V13','COLLECTIVE(V1–V13)','ATHENA.RUNTIME.UNIFIED.9','GITHUB_PROMOTION_VERIFIER.1','COLLECTIVE_ROBUST=<HB,FG,JD,FC,LT,DP,DR,L>','FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM','STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION','PROMOTION.2','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','CHECKS_FROM_DIFFERENT_SUITES_OR_RUNS --X--> QUALIFICATION','promotion-qualification'):
            self.assertIn(phrase, architecture)
        self.assertNotIn('# ATHENA Unified Architecture — AΩR × Collective V1–V12', architecture)

        migration = text('MIGRATION.md')
        for phrase in ('# ATHENA Unified Migration Law — v3.2 / Collective V1–V13','athena-canonical-mcp 3.2.0','ATHENA.RUNTIME.UNIFIED.9','V12 -> V13','UNIFIED.8 -> UNIFIED.9','GITHUB_PROMOTION_VERIFIER.1','QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES','STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION','PROMOTION.2','ATTESTED_READY != QUALIFIED','FOUR_GATE_PASS != LIVE TRUSTED PROMRUN','CHECKS_FROM_DIFFERENT_RUNS_OR_SUITES != ONE_TRUSTED_QUALIFICATION','promotion-qualification','TRUSTED_RUNTIME_QUALIFICATION != GITHUB_ADMIN_HARDENING'):
            self.assertIn(phrase, migration)
        self.assertNotIn('# ATHENA Unified Migration Law — v3.1 / Collective V1–V12', migration)

    def test_historical_contracts_and_current_v13_preserve_boundaries(self):
        v11 = text('spec/ATHENA_UNIFIED_V11.md')
        for phrase in ('PROMOTION.2 trust contract','ATTESTED_READY','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','EXTERNAL_PROMOTION_VERIFIER'):
            self.assertIn(phrase, v11)
        v12 = text('spec/ATHENA_UNIFIED_V12.md')
        for phrase in ('PROMOTION.2 trust contract','ATTESTED_READY','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','CI_PASS != LIVE_TRUSTED_PROMRUN'):
            self.assertIn(phrase, v12)
        v13 = text('spec/ATHENA_UNIFIED_V13.md')
        for phrase in ('athena-canonical-mcp 3.2.0','ATHENA.RUNTIME.UNIFIED.9','GITHUB_PROMOTION_VERIFIER.1','athena_claim_*','athena_discovery_claim_*','athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select','STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION','ATTESTED_READY != QUALIFIED','CHECKS_FROM_DIFFERENT_SUITES_OR_RUNS != ONE_TRUSTED_QUALIFICATION','promotion-qualification','FOUR_GATE_PASS != LIVE_TRUSTED_PROMRUN','TRUSTED_RUNTIME_QUALIFICATION != GITHUB_ADMIN_HARDENING','non-GitHub trusted promotion-verifier integrations'):
            self.assertIn(phrase, v13)

        upstream = text('spec/COLLECTIVE_RUNTIME_V13.md')
        for phrase in ('ATHENA COLLECTIVE RUNTIME V13','COLLECTIVE_ROBUST=<HB,FG,JD,FC,LT,DP,DR,L>','athena_gp_hyperqmc','FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM','BOUNDED_FCI_LITE != FCI_RFCI_PAG_THEOREM','TWO_TIMEPOINT_SEQUENTIAL_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM_OR_IDENTIFICATION_PROOF','DYNAMIC_GFORMULA_POLICY_VALUE != GENERAL_OFF_POLICY_CAUSAL_VALUE','ELLIPSOIDAL_GAUSSIAN_ROBUST_PLAN != GENERAL_DISTRIBUTIONALLY_ROBUST_OPTIMIZATION'):
            self.assertIn(phrase, upstream)

    def test_executable_witnesses_name_current_release_v13_and_trusted_qualification(self):
        smoke = text('smoke.py')
        for phrase in ("init['serverInfo']['version']=='3.2.0'",'V13 QMC/FITC/JOINT-DESIGN/FCI-LITE/LONGITUDINAL-TMLE/DYNAMIC-POLICY/ROBUST-RESOURCE',"manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.9'",'athena_gp_hyperqmc','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dro_resource_select','athena_promotion_verify_github',"promotion['status']=='ATTESTED_READY'","promotion['promotion_allowed'] is False"):
            self.assertIn(phrase, smoke)

        ci = text('.github/workflows/ci.yml')
        for phrase in ('Documentation and repository-brain consistency',"test_documentation_consistency.py",'GitHub trusted promotion verifier',"test_github_promotion_verifier.py",'V13 robust continuous-bayes causal-control and authority boundaries',"test_collective_v13_unified.py",'Promotion trust and exact-head predicate','promotion-qualification','scripts/qualify_github_head.py','ATHENA_GITHUB_RUN_ID','promotion-receipt-${{ github.event.pull_request.head.sha || github.sha }}'):
            self.assertIn(phrase, ci)

        script=text('scripts/qualify_github_head.py')
        for phrase in ('ATHENA_PROMOTION_HEAD','athena_promotion_verify_github','promotion-receipt.json','athena_promotion_replay','QUALIFIED'):
            self.assertIn(phrase,script)

        verifier=text('athena_mcp/github_promotion_verifier.py')
        for phrase in ('ATHENA.GITHUB.PROMOTION.VERIFIER.1',"REQUIRED_CHECKS=('syntax','unit','critical-invariants','smoke')",'github-actions','checks from different suites/runs are never spliced','ATHENA_GITHUB_REPOSITORY','ATHENA_GITHUB_RUN_ID'):
            self.assertIn(phrase,verifier)


if __name__ == '__main__':
    unittest.main()

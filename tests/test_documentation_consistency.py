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
        self.assertEqual(project['version'], '3.1.0')
        self.assertEqual(athena_mcp.__version__, '3.1.0')
        self.assertEqual(UNIFIED_MANIFEST_VERSION, 'ATHENA.RUNTIME.UNIFIED.8')
        self.assertEqual(PROMOTION_VERSION, 'ATHENA.PROMOTION.2')
        self.assertEqual(GITHUB_PROMOTION_VERIFIER_VERSION,'ATHENA.GITHUB.PROMOTION.VERIFIER.1')

        readme = text('README.md')
        for phrase in ('# ATHENA Canonical MCP v3.1','Collective V1–V12','ATHENA.RUNTIME.UNIFIED.8','PROMOTION.2','GITHUB_PROMOTION_VERIFIER.1','ATTESTED_READY != QUALIFIED','CHECKS_FROM_DIFFERENT_SUITES_OR_RUNS != ONE_TRUSTED_QUALIFICATION','athena://collective/v12','athena-canonical-mcp 3.1.0','COLLECTIVE_JOINT=<HP,BM,SG,PG,LC,JV,CC,L>','athena_gp_hyperposterior','athena_gp_bma_predict','athena_gp_sparse_predict','athena_gp_bma_decision_evsi','athena_pag_candidate_discover','athena_longitudinal_gformula','athena_chance_resource_select','promotion-qualification','External control-plane boundary'):
            self.assertIn(phrase, readme)
        self.assertNotIn('# ATHENA Canonical MCP v3.0 — AΩR × Collective V1–V11 Unified Runtime', readme)

        architecture = text('ARCHITECTURE.md')
        for phrase in ('# ATHENA Unified Architecture — AΩR × Collective V1–V12','Joint Structural World-Model Belief','COLLECTIVE(V1–V12)','ATHENA.RUNTIME.UNIFIED.8','GITHUB_PROMOTION_VERIFIER.1','FINITE_GRID_HYPERPOSTERIOR != CONTINUOUS_HYPERPARAMETER_BAYES','BMA_GP_POSTERIOR != WORLD_TRUTH','SUBSET_GP_APPROXIMATION != FULL_GP_POSTERIOR','BOUNDED_PAG_CANDIDATE != FCI_RFCI_PAG_THEOREM','TWO_TIMEPOINT_GFORMULA != LONGITUDINAL_TMLE_OR_IDENTIFICATION_PROOF','GAUSSIAN_INDEPENDENT_CHANCE_CERTIFICATE != DISTRIBUTION_FREE_RESOURCE_GUARANTEE','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','CHECKS_FROM_DIFFERENT_SUITES_OR_RUNS --X--> QUALIFICATION','promotion-qualification'):
            self.assertIn(phrase, architecture)
        self.assertNotIn('# ATHENA Unified Architecture — AΩR × Collective V1–V11', architecture)

        migration = text('MIGRATION.md')
        for phrase in ('# ATHENA Unified Migration Law — v3.1 / Collective V1–V12','athena-canonical-mcp 3.1.0','ATHENA.RUNTIME.UNIFIED.8','V11 → V12','UNIFIED.7 → UNIFIED.8','GITHUB_PROMOTION_VERIFIER.1','ATTESTED_READY != QUALIFIED','FOUR_GATE_PASS != LIVE TRUSTED PROMRUN','CHECKS_FROM_DIFFERENT_RUNS_OR_SUITES != ONE_TRUSTED_QUALIFICATION','promotion-qualification','TRUSTED_RUNTIME_QUALIFICATION != GITHUB_ADMIN_HARDENING'):
            self.assertIn(phrase, migration)
        self.assertNotIn('# ATHENA Unified Migration Law — v3.0 / Collective V1–V11', migration)

    def test_v11_history_and_current_v12_contract_preserve_boundaries(self):
        v11 = text('spec/ATHENA_UNIFIED_V11.md')
        for phrase in ('PROMOTION.2 trust contract','ATTESTED_READY','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','EXTERNAL_PROMOTION_VERIFIER'):
            self.assertIn(phrase, v11)
        v12 = text('spec/ATHENA_UNIFIED_V12.md')
        for phrase in ('athena-canonical-mcp 3.1.0','ATHENA.RUNTIME.UNIFIED.8','GITHUB_PROMOTION_VERIFIER.1','athena_claim_*','athena_discovery_claim_*','athena_gp_hyperposterior','athena_gp_bma_predict','athena_gp_sparse_predict','athena_gp_bma_decision_evsi','athena_pag_candidate_discover','athena_longitudinal_gformula','athena_chance_resource_select','ATTESTED_READY','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','CROSS_SUITE_CHECK_SPLICING --X--> QUALIFICATION','promotion-qualification','FOUR_GATE_PASS != LIVE_TRUSTED_PROMRUN','TRUSTED_RUNTIME_QUALIFICATION != GITHUB_ADMIN_HARDENING','NON-GITHUB'):
            self.assertIn(phrase, v12)

        upstream = text('spec/COLLECTIVE_RUNTIME_V12.md')
        for phrase in ('ATHENA COLLECTIVE RUNTIME V12','athena_gp_hyperposterior','BOUNDED_PAG_CANDIDATE != FCI_RFCI_PAG_THEOREM','TWO_TIMEPOINT_GFORMULA != LONGITUDINAL_TMLE_OR_IDENTIFICATION_PROOF','GAUSSIAN_INDEPENDENT_CHANCE_CERTIFICATE != DISTRIBUTION_FREE_RESOURCE_GUARANTEE'):
            self.assertIn(phrase, upstream)

    def test_executable_witnesses_name_current_release_v12_and_trusted_qualification(self):
        smoke = text('smoke.py')
        for phrase in ("init['serverInfo']['version']=='3.1.0'",'V12 JOINT',"manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.8'",'athena_gp_hyperposterior','athena_longitudinal_gformula','athena_chance_resource_select','athena_promotion_verify_github',"promotion['status']=='ATTESTED_READY'","promotion['promotion_allowed'] is False"):
            self.assertIn(phrase, smoke)

        ci = text('.github/workflows/ci.yml')
        for phrase in ('Documentation and repository-brain consistency',"test_documentation_consistency.py",'GitHub trusted promotion verifier',"test_github_promotion_verifier.py",'V12 joint-model constructive adversarial and authority boundaries',"test_collective_v12_unified.py",'Promotion trust and exact-head predicate','promotion-qualification','scripts/qualify_github_head.py','ATHENA_GITHUB_RUN_ID','promotion-receipt-${{ github.event.pull_request.head.sha || github.sha }}'):
            self.assertIn(phrase, ci)

        script=text('scripts/qualify_github_head.py')
        for phrase in ('ATHENA_PROMOTION_HEAD','athena_promotion_verify_github','promotion-receipt.json','athena_promotion_replay','QUALIFIED'):
            self.assertIn(phrase,script)

        verifier=text('athena_mcp/github_promotion_verifier.py')
        for phrase in ('ATHENA.GITHUB.PROMOTION.VERIFIER.1',"REQUIRED_CHECKS=('syntax','unit','critical-invariants','smoke')",'github-actions','checks from different suites/runs are never spliced','ATHENA_GITHUB_REPOSITORY','ATHENA_GITHUB_RUN_ID'):
            self.assertIn(phrase,verifier)


if __name__ == '__main__':
    unittest.main()

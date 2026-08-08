import tomllib
import unittest
from pathlib import Path

import athena_mcp
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
        self.assertEqual(UNIFIED_MANIFEST_VERSION, 'ATHENA.RUNTIME.UNIFIED.7')
        self.assertEqual(PROMOTION_VERSION, 'ATHENA.PROMOTION.2')

        readme = text('README.md')
        for phrase in ('# ATHENA Canonical MCP v3.1','Collective V1–V12','ATHENA.RUNTIME.UNIFIED.7','PROMOTION.2','ATTESTED_READY != QUALIFIED','athena://collective/v12','athena-canonical-mcp 3.1.0','COLLECTIVE_JOINT=<HP,BM,SG,PG,LC,JV,CC,L>','External control-plane boundary'):
            self.assertIn(phrase, readme)
        self.assertNotIn('# ATHENA Canonical MCP v3.0 — AΩR × Collective V1–V11 Unified Runtime', readme)

        architecture = text('ARCHITECTURE.md')
        for phrase in ('# ATHENA Unified Architecture — AΩR × Collective V1–V12','Joint Structural World-Model Belief','COLLECTIVE(V1–V12)','ATHENA.RUNTIME.UNIFIED.7','FINITE_GRID_HYPERPOSTERIOR != CONTINUOUS_HYPERPARAMETER_BAYES','PROMOTION.2','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER'):
            self.assertIn(phrase, architecture)
        self.assertNotIn('# ATHENA Unified Architecture — AΩR × Collective V1–V11', architecture)

        migration = text('MIGRATION.md')
        for phrase in ('# ATHENA Unified Migration Law — v3.1 / Collective V1–V12','athena-canonical-mcp 3.1.0','ATHENA.RUNTIME.UNIFIED.7','V11 → V12','PROMOTION.2','ATTESTED_READY != QUALIFIED','CI PASS != LIVE TRUSTED PROMRUN','External GitHub control-plane boundary'):
            self.assertIn(phrase, migration)
        self.assertNotIn('# ATHENA Unified Migration Law — v3.0 / Collective V1–V11', migration)

    def test_v11_and_v12_contracts_preserve_boundaries(self):
        v11 = text('spec/ATHENA_UNIFIED_V11.md')
        for phrase in ('PROMOTION.2 trust contract','ATTESTED_READY','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','EXTERNAL_PROMOTION_VERIFIER'):
            self.assertIn(phrase, v11)
        v12 = text('spec/ATHENA_UNIFIED_V12.md')
        for phrase in ('athena-canonical-mcp 3.1.0','ATHENA.RUNTIME.UNIFIED.7','athena_claim_*','athena_discovery_claim_*','athena_gp_hyperposterior','athena_pag_candidate_discover','athena_longitudinal_gformula','athena_chance_resource_select','PROMOTION.2 trust contract','ATTESTED_READY','CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER','CI_PASS != LIVE_TRUSTED_PROMRUN','External control-plane boundary','UNRESOLVED_EXTERNAL_CONTROL_PLANE'):
            self.assertIn(phrase, v12)

        upstream = text('spec/COLLECTIVE_RUNTIME_V12.md')
        for phrase in ('ATHENA COLLECTIVE RUNTIME V12','athena_gp_hyperposterior','BOUNDED_PAG_CANDIDATE != FCI_RFCI_PAG_THEOREM','TWO_TIMEPOINT_GFORMULA != LONGITUDINAL_TMLE_OR_IDENTIFICATION_PROOF','GAUSSIAN_INDEPENDENT_CHANCE_CERTIFICATE != DISTRIBUTION_FREE_RESOURCE_GUARANTEE'):
            self.assertIn(phrase, upstream)

    def test_executable_witnesses_name_current_release_v12_and_promotion2(self):
        smoke = text('smoke.py')
        for phrase in ("init['serverInfo']['version']=='3.1.0'",'V12 JOINT',"manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.7'",'athena_gp_hyperposterior','athena_longitudinal_gformula','athena_chance_resource_select',"promotion['status']=='ATTESTED_READY'","promotion['promotion_allowed'] is False"):
            self.assertIn(phrase, smoke)

        ci = text('.github/workflows/ci.yml')
        for phrase in ('Documentation and repository-brain consistency',"test_documentation_consistency.py",'V12 joint-model constructive adversarial and authority boundaries',"test_collective_v12_unified.py",'Promotion trust and exact-head predicate'):
            self.assertIn(phrase, ci)


if __name__ == '__main__':
    unittest.main()

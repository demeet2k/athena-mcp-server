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
        self.assertEqual(project['version'], '3.0.0')
        self.assertEqual(athena_mcp.__version__, '3.0.0')
        self.assertEqual(UNIFIED_MANIFEST_VERSION, 'ATHENA.RUNTIME.UNIFIED.7')
        self.assertEqual(PROMOTION_VERSION, 'ATHENA.PROMOTION.2')

        readme = text('README.md')
        self.assertIn('# ATHENA Canonical MCP v3.0', readme)
        self.assertIn('Collective V1–V11', readme)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.7', readme)
        self.assertIn('PROMOTION.2', readme)
        self.assertIn('ATTESTED_READY != QUALIFIED', readme)
        self.assertIn('athena://collective/v11', readme)
        self.assertIn('athena-canonical-mcp 3.0.0', readme)
        self.assertIn('External control-plane boundary', readme)
        self.assertNotIn('# ATHENA Canonical MCP v2.9 — AΩR × Collective V1–V10 Unified Runtime', readme)
        self.assertNotIn('Package: `athena-canonical-mcp 2.9.0`', readme)
        self.assertNotIn('live architecture: `ATHENA.RUNTIME.UNIFIED.6`', readme)

        architecture = text('ARCHITECTURE.md')
        self.assertIn('# ATHENA Unified Architecture — AΩR × Collective V1–V11', architecture)
        self.assertIn('Adaptive World Model V11', architecture)
        self.assertIn('COLLECTIVE(V1–V11)', architecture)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.7', architecture)
        self.assertIn('### PROMOTION.2', architecture)
        self.assertIn('CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER', architecture)
        self.assertNotIn('# ATHENA Unified Architecture — AΩR × Collective V1–V10', architecture)

        migration = text('MIGRATION.md')
        self.assertIn('# ATHENA Unified Migration Law — v3.0 / Collective V1–V11', migration)
        self.assertIn('athena-canonical-mcp 3.0.0', migration)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.7', migration)
        self.assertIn('V10 → V11', migration)
        self.assertIn('PROMOTION.1 → PROMOTION.2 trust migration', migration)
        self.assertIn('ATTESTED_READY != QUALIFIED', migration)
        self.assertIn('External GitHub/control-plane boundary', migration)
        self.assertNotIn('# ATHENA Unified Migration Law — v2.9 / Collective V1–V10', migration)

    def test_current_v11_contract_and_upstream_spec_preserve_boundaries(self):
        unified = text('spec/ATHENA_UNIFIED_V11.md')
        for phrase in (
            'athena-canonical-mcp 3.0.0',
            'ATHENA.RUNTIME.UNIFIED.7',
            'athena_claim_*',
            'athena_discovery_claim_*',
            'athena_gp_hyperfit',
            'athena_bapomdp_solve',
            'PROMOTION.2 trust contract',
            'ATTESTED_READY',
            'CALLER_ATTESTATION --X--> QUALIFIED_WITHOUT_TRUSTED_VERIFIER',
            'EXTERNAL_PROMOTION_VERIFIER',
            'External control-plane boundary',
            'UNRESOLVED_EXTERNAL_CONTROL_PLANE',
        ):
            self.assertIn(phrase, unified)

        upstream = text('spec/COLLECTIVE_RUNTIME_V11.md')
        self.assertIn('ATHENA COLLECTIVE RUNTIME V11', upstream)
        self.assertIn('athena_gp_hyperfit', upstream)
        self.assertIn('FINITE_MODEL_BAPOMDP != GENERAL_BAYES_ADAPTIVE_CONTROL', upstream)
        self.assertIn('SUPPLIED_DAG_LATENT_PROJECTION != DATA_DISCOVERED_PAG', upstream)

    def test_executable_witnesses_name_current_release_manifest_and_promotion(self):
        smoke = text('smoke.py')
        self.assertIn("init['serverInfo']['version']=='3.0.0'", smoke)
        self.assertIn('V11 ADAPTIVE', smoke)
        self.assertIn("manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.7'", smoke)
        self.assertIn("promotion['status']=='ATTESTED_READY'", smoke)
        self.assertIn("promotion['promotion_allowed'] is False", smoke)

        ci = text('.github/workflows/ci.yml')
        self.assertIn('Documentation and repository-brain consistency', ci)
        self.assertIn("test_documentation_consistency.py", ci)
        self.assertIn('V11 adaptive constructive adversarial and authority boundaries', ci)
        self.assertIn('Promotion trust and exact-head predicate', ci)


if __name__ == '__main__':
    unittest.main()

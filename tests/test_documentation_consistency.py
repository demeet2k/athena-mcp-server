import tomllib
import unittest
from pathlib import Path

import athena_mcp
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

        readme = text('README.md')
        self.assertIn('# ATHENA Canonical MCP v3.1', readme)
        self.assertIn('Collective V1–V12', readme)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.7', readme)
        self.assertIn('athena://collective/v12', readme)
        self.assertIn('athena-canonical-mcp 3.1.0', readme)
        self.assertIn('COLLECTIVE_JOINT=<HP,BM,SG,PG,LC,JV,CC,L>', readme)
        self.assertIn('External control-plane boundary', readme)
        self.assertNotIn('# ATHENA Canonical MCP v3.0 — AΩR × Collective V1–V11 Unified Runtime', readme)

        architecture = text('ARCHITECTURE.md')
        self.assertIn('# ATHENA Unified Architecture — AΩR × Collective V1–V12', architecture)
        self.assertIn('Joint Structural World-Model Belief', architecture)
        self.assertIn('COLLECTIVE(V1–V12)', architecture)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.7', architecture)
        self.assertIn('FINITE_GRID_HYPERPOSTERIOR != CONTINUOUS_HYPERPARAMETER_BAYES', architecture)
        self.assertNotIn('# ATHENA Unified Architecture — AΩR × Collective V1–V11', architecture)

        migration = text('MIGRATION.md')
        self.assertIn('# ATHENA Unified Migration Law — v3.1 / Collective V1–V12', migration)
        self.assertIn('athena-canonical-mcp 3.1.0', migration)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.7', migration)
        self.assertIn('V11 → V12', migration)
        self.assertIn('CI PASS != LIVE PROMRUN', migration)
        self.assertIn('External GitHub control-plane boundary', migration)
        self.assertNotIn('# ATHENA Unified Migration Law — v3.0 / Collective V1–V11', migration)

    def test_current_v12_contract_and_upstream_spec_preserve_boundaries(self):
        unified = text('spec/ATHENA_UNIFIED_V12.md')
        for phrase in (
            'athena-canonical-mcp 3.1.0',
            'ATHENA.RUNTIME.UNIFIED.7',
            'athena_claim_*',
            'athena_discovery_claim_*',
            'athena_gp_hyperposterior',
            'athena_pag_candidate_discover',
            'athena_longitudinal_gformula',
            'athena_chance_resource_select',
            'CI_PASS != LIVE_PROMRUN',
            'External control-plane boundary',
            'UNRESOLVED_EXTERNAL_CONTROL_PLANE',
        ):
            self.assertIn(phrase, unified)

        upstream = text('spec/COLLECTIVE_RUNTIME_V12.md')
        self.assertIn('ATHENA COLLECTIVE RUNTIME V12', upstream)
        self.assertIn('athena_gp_hyperposterior', upstream)
        self.assertIn('BOUNDED_PAG_CANDIDATE != FCI_RFCI_PAG_THEOREM', upstream)
        self.assertIn('TWO_TIMEPOINT_GFORMULA != LONGITUDINAL_TMLE_OR_IDENTIFICATION_PROOF', upstream)
        self.assertIn('GAUSSIAN_INDEPENDENT_CHANCE_CERTIFICATE != DISTRIBUTION_FREE_RESOURCE_GUARANTEE', upstream)

    def test_executable_witnesses_name_current_release_and_v12(self):
        smoke = text('smoke.py')
        self.assertIn("init['serverInfo']['version']=='3.1.0'", smoke)
        self.assertIn('V12 JOINT', smoke)
        self.assertIn("manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.7'", smoke)
        self.assertIn('athena_gp_hyperposterior', smoke)
        self.assertIn('athena_longitudinal_gformula', smoke)
        self.assertIn('athena_chance_resource_select', smoke)

        ci = text('.github/workflows/ci.yml')
        self.assertIn('Documentation and repository-brain consistency', ci)
        self.assertIn("test_documentation_consistency.py", ci)
        self.assertIn('V12 joint-model constructive adversarial and authority boundaries', ci)
        self.assertIn("test_collective_v12_unified.py", ci)


if __name__ == '__main__':
    unittest.main()

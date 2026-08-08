import tempfile
import tomllib
import unittest
from pathlib import Path

from athena_mcp.protocol import SERVER_INFO
from athena_mcp.server import Server


class MetadataConsistencyTests(unittest.TestCase):
    def test_package_and_server_versions_match(self):
        root=Path(__file__).resolve().parents[1]
        project=tomllib.loads((root/'pyproject.toml').read_text())['project']
        self.assertEqual(project['version'],SERVER_INFO['version'])
        self.assertEqual(project['name'],SERVER_INFO['name'])
        self.assertEqual(project['version'],'2.9.0')

    def test_v10_is_exposed_by_mcp(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            init=srv.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}})['result']
            self.assertEqual(init['serverInfo']['version'],'2.9.0')
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']}
            for name in (
                'athena_bandit_select','athena_topology_project_jspace','athena_bayes_predict','athena_experiment_design',
                'athena_ood_score','athena_causal_identify','athena_uncertainty_decompose','athena_dual_control_plan',
                'athena_belief_register','athena_decision_evi','athena_causal_effect_estimate','athena_evidence_spectral',
                'athena_gaussian_belief_register','athena_gaussian_belief_state','athena_gaussian_belief_observe',
                'athena_decision_evpi','athena_decision_evsi','athena_belief_policy_multistage','athena_causal_aipw',
                'athena_causal_robustness','athena_structure_partial','athena_evidence_dependence_probability',
                'athena_gp_register','athena_gp_state','athena_gp_observe','athena_gp_predict',
                'athena_pc_stable_discover','athena_causal_tmle_binary','athena_sensitivity_evalue','athena_pomdp_solve',
                'athena_evidence_dependence_observe','athena_evidence_dependence_fit','athena_evidence_dependence_predict',
            ):
                self.assertIn(name,names)
            uris={x['uri'] for x in srv.handle({'jsonrpc':'2.0','id':3,'method':'resources/list'})['result']['resources']}
            for uri in ('athena://collective/v4','athena://collective/v5','athena://collective/v6','athena://collective/v7','athena://collective/v8','athena://collective/v9','athena://collective/v10'):
                self.assertIn(uri,uris)
            for i,uri in enumerate(('athena://collective/v8','athena://collective/v9','athena://collective/v10'),start=4):
                read=srv.handle({'jsonrpc':'2.0','id':i,'method':'resources/read','params':{'uri':uri}})
                self.assertIn('result',read)
                self.assertEqual(read['result']['contents'][0]['mimeType'],'application/json')
            srv.store.close()


if __name__=='__main__': unittest.main()

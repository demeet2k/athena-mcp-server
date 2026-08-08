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
        self.assertEqual(project['version'],'2.7.0')

    def test_v8_is_exposed_by_mcp(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            init=srv.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}})['result']
            self.assertEqual(init['serverInfo']['version'],'2.7.0')
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']}
            for name in (
                'athena_bandit_select','athena_topology_project_jspace','athena_bayes_predict','athena_experiment_design',
                'athena_schedule_multiperiod','athena_pareto_frontier','athena_projection_compensate',
                'athena_ood_score','athena_experiment_generate','athena_causal_identify','athena_mpc_plan',
                'athena_schedule_certified','athena_claim_state',
                'athena_uncertainty_decompose','athena_prequential_interval','athena_causal_skeleton_discover',
                'athena_state_transition_model','athena_scenario_evaluate','athena_dual_control_plan',
                'athena_causal_identify_extended','athena_replication_independence','athena_replication_design',
                'athena_belief_register','athena_belief_state','athena_belief_observe','athena_decision_evi',
                'athena_belief_dual_control','athena_causal_effect_estimate','athena_causal_structure_bootstrap',
                'athena_contingent_policy','athena_evidence_spectral',
            ):
                self.assertIn(name,names)
            uris={x['uri'] for x in srv.handle({'jsonrpc':'2.0','id':3,'method':'resources/list'})['result']['resources']}
            for uri in ('athena://collective/v4','athena://collective/v5','athena://collective/v6','athena://collective/v7','athena://collective/v8'):
                self.assertIn(uri,uris)
            for i,uri in enumerate(('athena://collective/v5','athena://collective/v6','athena://collective/v7','athena://collective/v8'),start=4):
                read=srv.handle({'jsonrpc':'2.0','id':i,'method':'resources/read','params':{'uri':uri}})
                self.assertIn('result',read)
                self.assertEqual(read['result']['contents'][0]['mimeType'],'application/json')
            srv.store.close()


if __name__=='__main__': unittest.main()

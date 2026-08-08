import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.git_backend import GitStaleHead


class CollectiveRuntimeV4AdversarialTests(unittest.TestCase):
    def test_cross_regime_transfer_retains_uncertainty(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for _ in range(4):
                srv.call_tool('athena_bandit_observe', {
                    'arm_id':'A','reward':1,'features':{'novelty':1},'regime':'REGIME/ONE',
                })
            out=srv.call_tool('athena_bandit_select', {
                'arms':[{'id':'A','features':{'novelty':1}}],
                'context':{},'regime':'REGIME/TWO','exploration_alpha':.2,
            })
            arm=out['ranked_arms'][0]
            self.assertEqual(arm['source'],'GLOBAL_TRANSFER')
            self.assertEqual(arm['local_n'],0)
            self.assertGreater(arm['global_n'],0)
            self.assertGreater(arm['uncertainty'],0)
            srv.store.close()

    def test_unknown_worker_cost_is_not_treated_as_zero_cost(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_worker_cost_observe', {
                'worker_id':'known','task_id':'past','resources':{'tokens':2},'budget':{'tokens':10},'useful_output':1,
            })
            out=srv.call_tool('athena_budget_schedule', {
                'tasks':[{'id':'t','utility':1,'gap':1,'bridge_value':1,'required_capabilities':['x']}],
                'workers':[{'id':'known','capabilities':['x']},{'id':'unknown','capabilities':['x']}],
                'remaining_budget':{'tokens':5},
            })
            self.assertEqual(out['assignments'][0]['worker'],'known')
            unknown_profile=srv.collective_ecology._worker_profile({'id':'unknown'},'global')
            self.assertEqual(unknown_profile['cost_source'],'UNKNOWN')
            self.assertEqual(unknown_profile['estimate'],{})
            srv.store.close()

    def test_regression_runner_rejects_command_like_refs(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            ab=srv.call_tool('athena_failure_antibody_register', {
                'signature':'bad ref fixture',
                'detector':{'keywords':['bad','ref']},
                'repair':{'action':'none'},
                'regression_refs':['tests/test_runtime.py;echo pwned::RuntimeTests::test_registry_stale_text_simplex'],
            })
            out=srv.call_tool('athena_antibody_execute_regressions', {'antibody_id':ab['antibody_id'],'record_outcome':False})
            self.assertEqual(out['status'],'FAIL')
            self.assertEqual(out['runs'][0]['status'],'INVALID_REF')
            self.assertIsNone(out['runs'][0]['returncode'])
            srv.store.close()

    def test_diffusion_is_shrunk_and_not_instantly_extreme(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            prior=srv.collective_ecology.diffusion_coefficient('token','system')
            one=srv.call_tool('athena_diffusion_observe', {
                'source_scale':'token','target_scale':'system','transfer_utility':1,
                'evidence_weight':1,'causal_confidence':0,
            })
            self.assertGreater(one['coefficient'], prior['coefficient'])
            self.assertLess(one['coefficient'],1)
            self.assertLess(one['reliability'],.5)
            self.assertEqual(one['causal_weight'],0)
            srv.store.close()

    def test_projection_semantic_failure_is_journaled_for_compensation(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_topology_apply', {
                'topology_id':'T','expected_version':0,'operation':'INIT',
                'payload':{'state':{'modules':{'M1':{'id':'M1','active':True},'M2':{'id':'M2','active':True}},'bridges':[]}},
            })
            eid=srv.store.head('global')['eid']
            original=srv.core.add_edge
            calls={'n':0}
            def flaky(src,relation,dst,actor='agent',attrs=None):
                calls['n']+=1
                if calls['n']>=2:
                    raise RuntimeError('injected edge failure')
                return original(src,relation,dst,actor,attrs)
            srv.core.add_edge=flaky
            with self.assertRaises(RuntimeError):
                srv.call_tool('athena_topology_project_jspace', {
                    'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid,
                })
            row=srv.store.one("SELECT projection_id FROM collective_projection_sagas ORDER BY created_at DESC LIMIT 1")
            status=srv.call_tool('athena_projection_status', {'projection_id':row['projection_id']})
            self.assertEqual(status['status'],'COMPENSATION_REQUIRED')
            self.assertIn('injected edge failure',status['error'])
            self.assertEqual(srv.store.one("SELECT COUNT(*) AS n FROM edges WHERE attrs_json LIKE '%projection_id%'")['n'],1)
            srv.store.close()

    def test_projection_git_preflight_rejects_without_semantic_writes(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_topology_apply', {
                'topology_id':'T','expected_version':0,'operation':'INIT',
                'payload':{'state':{'modules':{'M':{'id':'M','active':True}},'bridges':[]}},
            })
            eid=srv.store.head('global')['eid']
            before=srv.store.one('SELECT COUNT(*) AS n FROM edges')['n']
            with self.assertRaises(ValueError):
                srv.call_tool('athena_topology_project_jspace', {
                    'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid,
                    'checkpoint_git':True,'expected_git_head':'deadbeef',
                })
            after=srv.store.one('SELECT COUNT(*) AS n FROM edges')['n']
            self.assertEqual(before,after)
            srv.store.close()


if __name__=='__main__': unittest.main()

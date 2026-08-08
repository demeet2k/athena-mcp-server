import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV7AdversarialTests(unittest.TestCase):
    def test_diagnostics_and_plans_do_not_train_their_models(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); regime='REGIME/V7/ADV'
            for x in (-.2,-.1,0,.1,.2):
                srv.call_tool('athena_nonlinear_observe',{'features':{'x':x},'reward':.4+x*x,'regime':regime,'arm_id':'A'})
            b1=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_bayes_observations")['n']
            o1=srv.store.one("SELECT n FROM collective_v6_ood_models WHERE scope='global' AND regime=?",(regime,))['n']
            srv.call_tool('athena_uncertainty_decompose',{'features':{'x':.8},'regime':regime,'arm_id':'A'})
            srv.call_tool('athena_prequential_interval',{'features':{'x':.8},'regime':regime,'arm_id':'A','min_scores':2})
            self.assertEqual(b1,srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_bayes_observations")['n'])
            self.assertEqual(o1,srv.store.one("SELECT n FROM collective_v6_ood_models WHERE scope='global' AND regime=?",(regime,))['n'])
            t1=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n']
            srv.call_tool('athena_dual_control_plan',{'initial_context':{'x':0},'actions':[{'id':'UNSEEN','base_reward':.5}]})
            srv.call_tool('athena_scenario_evaluate',{'initial_context':{'x':0},'actions':[{'id':'UNSEEN','base_reward':.5}],'trajectories':[{'actions':['UNSEEN']}]})
            self.assertEqual(t1,srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n'])
            srv.store.close()

    def test_skeleton_never_mutates_canonical_registry(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            before=srv.store.one("SELECT COUNT(*) AS n FROM objects")['n']
            samples=[{'x':i,'y':2*i,'z':(-1)**i} for i in range(10)]
            out=srv.call_tool('athena_causal_skeleton_discover',{'samples':samples})
            self.assertEqual(out['status'],'HEURISTIC_ASSOCIATION_SKELETON')
            self.assertEqual(before,srv.store.one("SELECT COUNT(*) AS n FROM objects")['n'])
            srv.store.close()

    def test_frontdoor_and_instrument_fail_when_criteria_fail(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            fd=srv.call_tool('athena_causal_identify_extended',{
                'method':'FRONTDOOR','treatment':'T','outcome':'Y','mediators':['M'],
                'edges':[{'src':'T','dst':'M'},{'src':'M','dst':'Y'},{'src':'T','dst':'Y'}],
                'observed_nodes':['T','M','Y'],
            })
            self.assertEqual(fd['status'],'UNIDENTIFIED_FRONTDOOR_CRITERIA')
            iv=srv.call_tool('athena_causal_identify_extended',{
                'method':'INSTRUMENT','treatment':'T','outcome':'Y','instruments':['Z'],
                'edges':[{'src':'Z','dst':'T'},{'src':'T','dst':'Y'},{'src':'U','dst':'Z'},{'src':'U','dst':'Y'}],
                'observed_nodes':['Z','T','Y','U'],
            })
            self.assertEqual(iv['status'],'UNIDENTIFIED_NO_VALID_INSTRUMENT')
            latent=srv.call_tool('athena_causal_identify_extended',{
                'method':'INSTRUMENT','treatment':'T','outcome':'Y','instruments':['Z'],
                'edges':[{'src':'Z','dst':'T'},{'src':'T','dst':'Y'}],
                'observed_nodes':['Z','T','Y'],'assumptions':{'latent_confounding_possible':True},
            })
            self.assertEqual(latent['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            srv.store.close()

    def test_duplicate_replications_do_not_inflate_effective_n(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            cid=srv.call_tool('athena_claim_register',{'claim_key':'ADV7','statement':'same pipeline repeats'})['claim_id']
            evidence={'dataset':'D','implementation':'I','method':'M','operator':'O','environment':'E','seed_family':'S'}
            for key in ('nominal1','nominal2','nominal3'):
                srv.call_tool('athena_claim_witness',{'claim_id':cid,'kind':'REPLICATION','result':'SUPPORTS','independence_key':key,'confidence':1,'evidence':evidence})
            ind=srv.call_tool('athena_replication_independence',{'claim_id':cid})
            self.assertAlmostEqual(ind['support']['effective_n'],1.0,places=6)
            srv.store.close()

    def test_unseen_state_model_does_not_fabricate_dynamics(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            out=srv.call_tool('athena_state_transition_model',{'action_id':'NEVER','context':{'progress':.4}})
            self.assertEqual(out['status'],'UNSEEN_ACTION')
            self.assertEqual(out['mean_delta'],{})
            self.assertEqual(out['next_mean'],{'progress':.4})
            srv.store.close()

    def test_prequential_band_fails_openly_when_history_is_too_small(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); regime='SMALL'
            srv.call_tool('athena_nonlinear_observe',{'features':{'x':0},'reward':.5,'regime':regime,'arm_id':'A'})
            out=srv.call_tool('athena_prequential_interval',{'features':{'x':.1},'regime':regime,'arm_id':'A','min_scores':8})
            self.assertEqual(out['status'],'INSUFFICIENT_PREQUENTIAL_SCORES')
            self.assertIn('without a conformal-style coverage claim',out['law'])
            srv.store.close()


if __name__=='__main__': unittest.main()

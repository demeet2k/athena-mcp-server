import tempfile
import unittest
from athena_mcp.server import Server

class CollectiveRuntimeV6EarlyDiagnostics(unittest.TestCase):
    def test_named_v6_organs_first(self):
        failures=[]
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            def run(name,fn):
                try:fn();print(f'::notice title=V6_{name}::PASS')
                except Exception as e:failures.append((name,e));print(f'::error title=V6_{name}::{type(e).__name__}: {e}')
            run('OOD',lambda:(srv.call_tool('athena_ood_observe',{'features':{'x':0},'regime':'R'}),srv.call_tool('athena_ood_score',{'features':{'x':1},'regime':'R'})))
            run('EXPERIMENT',lambda:srv.call_tool('athena_experiment_generate',{'hypotheses':[{'id':'H1','prior':.5,'base_p':.5,'factor_effects':{'dose=high':.4}},{'id':'H2','prior':.5,'base_p':.5,'factor_effects':{'dose=high':-.4}}],'factors':[{'name':'dose','levels':['low','high']}]}))
            run('CAUSAL',lambda:srv.call_tool('athena_causal_identify',{'treatment':'T','outcome':'Y','edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],'observed_nodes':['T','Y','Z']}))
            def ix():
                rows=[]
                for a in (0,1):
                    for b in (0,1):
                        for c in (0,1):rows.append({'interventions':[x for x,v in [('A',a),('B',b),('C',c)] if v],'outcome':.1*a+.2*b+.3*c+.5*a*b*c})
                out=srv.call_tool('athena_interaction_higher_order',{'experiments':rows,'max_order':3,'design_confidence':1});assert abs(next(x for x in out['interactions'] if x['term']=='A*B*C')['effect']-.5)<1e-6
            run('INTERACTION',ix)
            def tr():
                srv.call_tool('athena_transition_observe',{'action_id':'A','before':{'x':0},'after':{'x':.2}});srv.call_tool('athena_transition_distribution',{'action_id':'A','context':{'x':.2}});srv.call_tool('athena_mpc_plan',{'initial_context':{'x':.2},'actions':[{'id':'A','base_reward':.8}],'horizon':2})
            run('TRANSITION_MPC',tr)
            run('SCHEDULE',lambda:srv.call_tool('athena_schedule_certified',{'tasks':[{'id':'A','duration':1,'utility':1,'resource_cost':{'tokens':1}}],'workers':[{'id':'W'}],'budget':{'tokens':1},'horizon':2}))
            run('WITNESS',lambda:srv.call_tool('athena_witness_capsule',{'regression_ref':'tests/test_runtime.py::RuntimeTests::test_registry_stale_text_simplex'}))
            run('PARETO',lambda:srv.call_tool('athena_pareto_bandit_select',{'candidates':[{'id':'A','metrics':{'q':{'mean':.8,'sigma':.1}}},{'id':'B','metrics':{'q':{'mean':.7,'sigma':.01}}}]}))
            def cl():
                c=srv.call_tool('athena_discovery_claim_register',{'claim_key':'D','statement':'diag'});srv.call_tool('athena_discovery_claim_witness',{'claim_id':c['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':'r1'});srv.call_tool('athena_discovery_claim_state',{'claim_id':c['claim_id']})
            run('REPLICATION',cl);srv.store.close()
        if failures:self.fail('; '.join(f'{n}: {e}' for n,e in failures))

if __name__=='__main__': unittest.main()

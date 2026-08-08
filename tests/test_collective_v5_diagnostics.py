import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV5Diagnostics(unittest.TestCase):
    def test_named_v5_probes(self):
        failures=[]

        def probe(name, fn):
            try:
                fn()
                print(f"::notice title=V5_DIAG_{name}::PASS", flush=True)
            except Exception as e:
                failures.append(f"{name}:{type(e).__name__}:{e}")
                print(f"::error title=V5_DIAG_{name}::{type(e).__name__}: {e}", flush=True)

        def with_server(fn):
            with tempfile.NamedTemporaryFile(suffix='.db') as f:
                srv=Server(f.name)
                try: fn(srv)
                finally: srv.store.close()

        def bayes(srv):
            pre=srv.call_tool('athena_bayes_predict',{'features':{'x':.8,'y':.8},'regime':'R','arm_id':'A'})
            for _ in range(3):
                srv.call_tool('athena_bayes_observe',{'features':{'x':.8,'y':.8},'reward':.9,'regime':'R','arm_id':'A'})
                srv.call_tool('athena_bayes_observe',{'features':{'x':-.8,'y':-.8},'reward':.1,'regime':'R','arm_id':'A'})
            post=srv.call_tool('athena_bayes_predict',{'features':{'x':.8,'y':.8},'regime':'R','arm_id':'A'})
            assert post['n']==6, post
            assert post['mean']>.5, post
            assert post['sigma']<pre['sigma'], (pre,post)
            assert abs(post['posterior_covariance'][1][2])>1e-9, post['posterior_covariance']

        def design(srv):
            out=srv.call_tool('athena_experiment_design',{
                'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],
                'experiments':[{'id':'diagnostic','positive_probability':{'H1':.95,'H2':.05},'cost':.1,'risk':.1,'ethical':True}, {'id':'weak','positive_probability':{'H1':.55,'H2':.45},'cost':.1,'risk':.1,'ethical':True}],
            })
            assert out['winner']=='diagnostic', out

        def interaction(srv):
            ex=[]
            for _ in range(2):
                ex += [{'interventions':[],'outcome_delta':.1,'design_confidence':.9},{'interventions':['A'],'outcome_delta':.2,'design_confidence':.9},{'interventions':['B'],'outcome_delta':.2,'design_confidence':.9},{'interventions':['A','B'],'outcome_delta':.8,'design_confidence':.9}]
            out=srv.call_tool('athena_interaction_credit',{'analysis_key':'factorial','experiments':ex})
            pair=next(x for x in out['terms'] if x['term']=='A×B')
            assert abs(pair['effect']-.5)<1e-8, pair

        def transition(srv):
            for _ in range(3): srv.call_tool('athena_transition_observe',{'action_id':'FOCUS','before':{'progress':.1,'risk':.4},'after':{'progress':.5,'risk':.3}})
            p=srv.call_tool('athena_transition_predict',{'action_id':'FOCUS','context':{'progress':.2,'risk':.4}})
            assert p['delta_mean']['progress']>0, p
            assert p['delta_mean']['risk']<0, p

        def scheduler(srv):
            out=srv.call_tool('athena_schedule_multiperiod',{
                'tasks':[{'id':'A','utility':1,'duration':2,'required_capabilities':['math'],'resource_cost':{'tokens':2}}, {'id':'B','utility':1,'duration':1,'dependencies':['A'],'required_capabilities':['math'],'resource_cost':{'tokens':2}}, {'id':'C','utility':.7,'duration':1,'required_capabilities':['code'],'resource_cost':{'tokens':2}}],
                'workers':[{'id':'w1','capabilities':['math']},{'id':'w2','capabilities':['code']}], 'horizon':6,'budget':{'tokens':6},'beam_width':64,
            })
            by={x['task']:x for x in out['schedule']}
            assert set(by)=={'A','B','C'}, out
            assert by['B']['start']>=by['A']['finish'], by

        def witness(srv):
            out=srv.call_tool('athena_witness_cell',{'regression_ref':'tests/test_runtime.py::RuntimeTests::test_registry_stale_text_simplex','timeout_s':20})
            assert out['status']=='PASS', out

        def pareto(srv):
            pf=srv.call_tool('athena_pareto_frontier',{'candidates':[{'id':'A','metrics':{'quality':.9,'cost':.8}},{'id':'B','metrics':{'quality':.8,'cost':.2}},{'id':'C','metrics':{'quality':.7,'cost':.9}}], 'directions':{'quality':'max','cost':'min'}})
            assert {x['id'] for x in pf['frontier']}=={'A','B'}, pf
            assert any(x['id']=='C' for x in pf['dominated']), pf

        def compensation(srv):
            srv.call_tool('athena_topology_apply',{'topology_id':'T','expected_version':0,'operation':'INIT','payload':{'state':{'modules':{'M':{'id':'M','active':True}},'bridges':[]}}})
            eid=srv.store.head('global')['eid']
            p=srv.call_tool('athena_topology_project_jspace',{'topology_id':'T','expected_topology_version':1,'expected_semantic_eid':eid})
            head=srv.store.head('global')['eid']
            c=srv.call_tool('athena_projection_compensate',{'projection_id':p['projection']['projection_id'],'expected_semantic_eid':head})
            assert c['status']=='SEMANTIC_COMPENSATED', c

        for name,fn in [('BAYES',bayes),('DESIGN',design),('INTERACTION',interaction),('TRANSITION',transition),('SCHEDULER',scheduler),('WITNESS',witness),('PARETO',pareto),('COMPENSATION',compensation)]:
            probe(name, lambda fn=fn: with_server(fn))

        self.assertFalse(failures, ' | '.join(failures))


if __name__=='__main__': unittest.main()

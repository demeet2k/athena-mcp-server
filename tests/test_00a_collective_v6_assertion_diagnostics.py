import tempfile
import unittest
from athena_mcp.server import Server

class CollectiveRuntimeV6AssertionDiagnostics(unittest.TestCase):
    def test_v6_assertions_named(self):
        failures=[]
        def probe(name,fn):
            try:fn();print(f'::notice title=V6A_{name}::PASS')
            except Exception as e:failures.append((name,e));print(f'::error title=V6A_{name}::{type(e).__name__}: {e}')
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);R='REGIME/T'
            def p_ood():
                for x in (-.2,-.1,0,.1,.2):srv.call_tool('athena_nonlinear_observe',{'features':{'x':x},'reward':x*x,'regime':R,'arm_id':'A'})
                n=srv.call_tool('athena_ood_score',{'features':{'x':.1},'regime':R});q=srv.call_tool('athena_ood_score',{'features':{'x':1},'regime':R});assert n['ood_score']<q['ood_score'],(n,q)
            probe('OOD_ORDER',p_ood)
            def p_exp():
                o=srv.call_tool('athena_experiment_generate',{'hypotheses':[{'id':'H1','prior':.5,'base_p':.5,'factor_effects':{'dose=high':.4}},{'id':'H2','prior':.5,'base_p':.5,'factor_effects':{'dose=high':-.4}}],'factors':[{'name':'dose','levels':['low','high']}]});assert o['winner'] is not None,o;assert any(x.get('status')=='ELIGIBLE' for x in o['ranked_experiments']),o
            probe('EXPERIMENT_ELIGIBLE',p_exp)
            def p_causal():
                o=srv.call_tool('athena_causal_identify',{'treatment':'T','outcome':'Y','edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],'observed_nodes':['T','Y','Z']});assert ['Z'] in o['minimal_adjustment_sets'],o
            probe('BACKDOOR_SET',p_causal)
            def p_schedule():
                o=srv.call_tool('athena_schedule_certified',{'tasks':[{'id':'A','duration':1,'utility':1,'resource_cost':{'tokens':1},'required_capabilities':['x']},{'id':'B','duration':1,'utility':1,'dependencies':['A'],'resource_cost':{'tokens':1},'required_capabilities':['x']}],'workers':[{'id':'W','capabilities':['x']}],'budget':{'tokens':2},'horizon':3});assert o['certificate']=='EXACT_ENUMERATION_CERTIFIED',o;assert [x['task'] for x in o['schedule']]==['A','B'],o
            probe('SCHEDULE_EXACT',p_schedule)
            def p_claim():
                c=srv.call_tool('athena_discovery_claim_register',{'claim_key':'C','statement':'s'});[srv.call_tool('athena_discovery_claim_witness',{'claim_id':c['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':k}) for k in ('r1','r2')];assert srv.call_tool('athena_discovery_claim_state',{'claim_id':c['claim_id']})['status']=='REPLICATED_SUPPORT';srv.call_tool('athena_discovery_claim_witness',{'claim_id':c['claim_id'],'kind':'FALSIFIER','result':'FALSIFIES','independence_key':'red'});assert srv.call_tool('athena_discovery_claim_state',{'claim_id':c['claim_id']})['status']=='CONTESTED'
            probe('CLAIM_STATES',p_claim)
            def p_block():
                o=srv.call_tool('athena_experiment_generate',{'hypotheses':[{'id':'H1','prior':.5,'base_p':.5,'factor_effects':{'dose=high':.4}},{'id':'H2','prior':.5,'base_p':.5,'factor_effects':{'dose=high':-.4}}],'factors':[{'name':'dose','levels':['low','high'],'forbidden_levels':['high']}]});b=[x for x in o['ranked_experiments'] if x['id'].endswith('dose=high')];assert b and b[0]['status']=='ETHICS_BLOCK',o
            probe('ETHICS_BLOCK',p_block);srv.store.close()
        if failures:self.fail('; '.join(f'{n}: {e}' for n,e in failures))

if __name__=='__main__':unittest.main()

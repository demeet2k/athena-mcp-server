import math
import tempfile
import unittest

from athena_mcp.orchestration_robustness import elasticity_packet, successor_robustness
from athena_mcp.server import Server


def row(ident,score):
    return {'id':ident,'scores':{'successor':{'status':'KNOWN','value':score}}}

BASE={
 'readiness':1,'gain':1,'independence':1,'bridge':1,'cost':1,
 'delta_j':1,'information_gain':1,'option_value':1,
 'evidence':1,'connection':1,'replay':1,'navigation':1,
 'reconstruction':1,'implementation':1,'novelty':1,
 'duplicate':0,'fake':0,'bloat':0,'unsupported':0,
 'unhandled_contradiction':0,'coordinate_loss':0,
}

class RobustnessUnitTests(unittest.TestCase):
    def test_critical_radius_matches_closed_form(self):
        out=successor_robustness([row('a',32),row('b',1)],0.10)
        expected=(2-1)/(2+1)  # (32/1)^(1/5)=2
        self.assertAlmostEqual(out['critical_relative_perturbation'],expected)
        self.assertEqual(out['status'],'STABLE')
        self.assertTrue(out['stable_under_tested_perturbation'])

    def test_near_tie_is_fragile(self):
        out=successor_robustness([row('a',1.01),row('b',1.0)],0.01)
        self.assertEqual(out['status'],'FRAGILE')
        self.assertFalse(out['stable_under_tested_perturbation'])
        self.assertLess(out['critical_relative_perturbation'],0.01)

    def test_exact_tie_has_zero_radius(self):
        out=successor_robustness([row('a',1),row('b',1)],0)
        self.assertEqual(out['status'],'TIE_FRAGILE')
        self.assertEqual(out['critical_relative_perturbation'],0)

    def test_unknown_and_single_candidate_are_not_overclaimed(self):
        unknown={'id':'u','scores':{'successor':{'status':'UNKNOWN','value':None}}}
        out=successor_robustness([unknown])
        self.assertEqual(out['status'],'UNKNOWN')
        one=successor_robustness([row('a',1),unknown])
        self.assertEqual(one['status'],'SINGLE_CANDIDATE')
        self.assertIsNone(one['stable_under_tested_perturbation'])

    def test_elasticities_match_successor_formula(self):
        e=elasticity_packet(row('a',3))
        self.assertEqual(e['elasticities']['delta_j'],1)
        self.assertEqual(e['elasticities']['cost'],-1)

class RobustnessServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db'); self.server=Server(self.tmp.name); self.seq=0
    def tearDown(self):
        self.server.store.close(); self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1; m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args}); self.assertFalse(r['result'].get('isError'),r); return r['result']['structuredContent']

    def test_tool_and_resource_are_composed(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']}
        self.assertIn('athena_orchestration_robustness',names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        self.assertIn('athena://orchestration/robustness',uris)

    def test_persisted_run_robustness_links_decision_digest(self):
        a={'id':'a',**{**BASE,'delta_j':4}}
        b={'id':'b',**BASE}
        run=self.tool('athena_orchestrate',{'seed':'s','candidates':[a,b],'task':'robust'})
        robust=self.tool('athena_orchestration_robustness',{'run_id':run['run_id'],'relative_perturbation':0.01})
        self.assertEqual(robust['winner'],'a')
        self.assertEqual(robust['decision_digest'],run['decision_digest'])
        self.assertEqual(robust['run_id'],run['run_id'])
        self.assertGreater(robust['critical_relative_perturbation'],0)

if __name__=='__main__':unittest.main()

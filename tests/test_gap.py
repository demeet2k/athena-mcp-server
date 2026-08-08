import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_gap import GapLedger, compile_gap

POLICY={'traversable_relations':['derive','support','bridge','implement'],'max_depth':4,'require_witness':True,'allowed_statuses':['ACTIVE']}

def edge(eid,src,dst,relation='derive',verified=True,witness='w'):
    return {'id':eid,'src':src,'dst':dst,'relation':relation,'verified':verified,'witness_ref':witness,'status':'ACTIVE'}

def target(ident,node,severity=1,leverage=1,information_gain=1,cost=1):
    return {'id':ident,'node':node,'severity':severity,'leverage':leverage,'information_gain':information_gain,'cost':cost}

class GapCompilerTests(unittest.TestCase):
    def test_witnessed_directed_reachability_and_path_provenance(self):
        out=compile_gap({'S':['a'],'H':['h']},[edge('e1','a','b'),edge('e2','b','c','support'),edge('e3','h','x','bridge')],[target('tc','c'),target('tx','x')],POLICY)
        self.assertEqual(out['closure_kind'],'WITNESSED_DIRECTED_REACHABILITY_NOT_LOGICAL_PROOF')
        self.assertEqual(out['covered_target_ids'],['tc','tx']);self.assertEqual(out['gap_target_ids'],[])
        self.assertEqual(out['closure_paths']['c']['nodes'],['a','b','c']);self.assertEqual(out['closure_paths']['c']['edges'],['e1','e2']);self.assertEqual(out['closure_paths']['c']['origin_groups'],['S'])
        self.assertIn('logical/causal entailment',out['epistemic_boundary'])

    def test_unverified_or_disallowed_edges_do_not_enter_closure(self):
        edges=[edge('good','a','b'),edge('unverified','b','c',verified=False),edge('contra','b','d','contradict'),{**edge('blocked','b','e'), 'status':'BLOCKED'}]
        out=compile_gap({'S':['a']},edges,[target('b','b'),target('c','c'),target('d','d'),target('e','e')],POLICY)
        self.assertEqual(out['covered_target_ids'],['b']);self.assertEqual(out['gap_target_ids'],['c','d','e']);defects={x['id']:x['defects'] for x in out['rejected_edges']}
        self.assertIn('edge_not_verified',defects['unverified']);self.assertIn('relation_not_traversable',defects['contra']);self.assertIn('status_not_allowed',defects['blocked'])

    def test_max_depth_bounds_closure(self):
        out=compile_gap({'S':['a']},[edge('1','a','b'),edge('2','b','c'),edge('3','c','d')],[target('c','c'),target('d','d')],{**POLICY,'max_depth':2})
        self.assertIn('c',out['closure_nodes']);self.assertNotIn('d',out['closure_nodes']);self.assertEqual(out['gap_target_ids'],['d'])

    def test_gap_growth_is_unknown_safe(self):
        known=target('known','k',severity=2,leverage=3,information_gain=4,cost=2)
        missing=target('missing','m');del missing['information_gain']
        out=compile_gap({'S':['a']},[],[known,missing],POLICY)
        self.assertEqual(out['grow']['id'],'known');self.assertEqual(out['grow']['residual_score']['value'],12)
        self.assertEqual(out['measurement_plan'][0]['target'],'missing');missing_row=next(x for x in out['gap'] if x['id']=='missing');self.assertEqual(missing_row['residual_score']['status'],'UNKNOWN');self.assertIsNone(missing_row['residual_score']['value'])

    def test_covered_target_does_not_need_residual_metrics(self):
        out=compile_gap({'B':['z']},[],[{'id':'z','node':'z'}],POLICY)
        row=out['targets'][0];self.assertTrue(row['covered']);self.assertEqual(row['residual_score']['status'],'N/A_COVERED');self.assertEqual(out['measurement_plan'],[])

    def test_traversable_relation_policy_is_explicit(self):
        with self.assertRaises(ValueError):compile_gap({'S':['a']},[],[],{'traversable_relations':['magic']})
        out=compile_gap({'S':['a']},[edge('e','a','b','derive')],[target('b','b')],{'traversable_relations':[],'require_witness':True})
        self.assertEqual(out['gap_target_ids'],['b']);self.assertIn('relation_not_traversable',out['rejected_edges'][0]['defects'])

    def test_cycles_terminate_by_visited_closure(self):
        out=compile_gap({'S':['a']},[edge('ab','a','b'),edge('ba','b','a'),edge('bc','b','c')],[target('c','c')],POLICY)
        self.assertEqual(out['covered_target_ids'],['c']);self.assertEqual(sorted(out['closure_nodes']),['a','b','c'])

class GapLedgerTests(unittest.TestCase):
    def test_persist_and_replay_freezes_graph_snapshot(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
            store=Store(tmp.name);core=AthenaCore(store);ledger=GapLedger(core)
            run=ledger.compile('task://gap',{'S':['a']},[edge('ab','a','b')],[target('b','b'),target('c','c',2,2,2,1)],POLICY,actor='A1')
            self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('GAPRUN.'));self.assertEqual(run['gap_target_ids'],['c']);self.assertEqual(run['grow']['id'],'c')
            replay=ledger.replay(run['run_id']);self.assertTrue(replay['match']);self.assertEqual(replay['stored_gap'],replay['recomputed_gap']);self.assertEqual(replay['stored_closure_nodes'],replay['recomputed_closure_nodes'])
            bench=ledger.benchmark();self.assertEqual(bench['gap_runs'],1);self.assertEqual(bench['gap_replay_match_rate'],1.0);store.close()

if __name__=='__main__':unittest.main()

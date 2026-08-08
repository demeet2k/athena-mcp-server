import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_retrieval import RetrievalLedger, compile_selection, score_candidate


def measurements(relevance=1,source_authority=1,cross_value=1,decision_relevance=1):
    return {
        'relevance':{'value':relevance,'method':'semantic-test','witness_ref':'m:rel'},
        'source_authority':{'value':source_authority,'method':'provenance-test','witness_ref':'m:auth'},
        'cross_value':{'value':cross_value,'method':'bridge-test','witness_ref':'m:cross'},
        'decision_relevance':{'value':decision_relevance,'method':'decision-test','witness_ref':'m:decision'},
    }


def candidate(ident,score=1,cost=1,roles=None,facets=None,source_time=900,coords=None,lineages=None):
    return {
        'id':ident,
        'source_ref':f'source://{ident}',
        'measurements':measurements(score,1,1,1),
        'source_time':source_time,
        'cost':cost,
        'roles':roles or [],
        'facets':facets or [],
        'coordinate_keys':coords or [],
        'lineage_keys':lineages or [],
    }


QUERY={
    'as_of':1000,
    'freshness_half_life':100,
    'budget':10,
    'max_items':10,
}


class RetrievalCompilerTests(unittest.TestCase):
    def test_score_is_replayable_and_freshness_is_half_life(self):
        row=candidate('x',score=0.8,cost=2,source_time=900)
        score=score_candidate(row,QUERY)
        self.assertEqual(score['status'],'KNOWN')
        self.assertAlmostEqual(score['components']['freshness'],0.5,places=9)
        self.assertAlmostEqual(score['value'],0.8*0.5/2,places=9)

    def test_missing_measurement_is_unknown_not_zero(self):
        row=candidate('missing')
        del row['measurements']['cross_value']
        out=compile_selection(QUERY,[row,candidate('known',score=0.1)])
        self.assertEqual(out['selected_ids'],['known'])
        req=next(x for x in out['measurement_plan'] if x['candidate']=='missing')
        self.assertEqual(req['defects'][0]['metric'],'cross_value')
        missing=next(x for x in out['rows'] if x['id']=='missing')
        self.assertEqual(missing['score']['status'],'UNKNOWN')
        self.assertIsNone(missing['score']['value'])

    def test_metric_measurements_require_method_witness_and_unit_interval(self):
        bad=candidate('bad')
        bad['measurements']['relevance']={'value':1.2,'method':'x','witness_ref':'w'}
        score=score_candidate(bad,QUERY)
        self.assertEqual(score['status'],'UNKNOWN')
        self.assertEqual(score['defects'][0]['reason'],'outside_0_1_contract')
        bad2=candidate('bad2');bad2['measurements']['relevance']={'value':0.9}
        score2=score_candidate(bad2,QUERY)
        self.assertEqual(score2['status'],'UNKNOWN')
        self.assertEqual(score2['defects'][0]['reason'],'missing_method_or_witness_ref')

    def test_coordinate_and_lineage_fit_are_query_conditioned(self):
        q={**QUERY,'preferred_coordinates':['KC:1','KC:2'],'preferred_lineages':['L:A']}
        full=candidate('full',coords=['KC:1','KC:2'],lineages=['L:A'])
        partial=candidate('partial',coords=['KC:1'],lineages=['L:B'])
        fs=score_candidate(full,q);ps=score_candidate(partial,q)
        self.assertEqual(fs['components']['coordinate_fit'],1.0)
        self.assertEqual(fs['components']['lineage_fit'],1.0)
        self.assertEqual(ps['components']['coordinate_fit'],0.5)
        self.assertEqual(ps['components']['lineage_fit'],0.0)
        self.assertGreater(fs['value'],ps['value'])

    def test_coverage_can_select_lower_similarity_source_when_role_is_required(self):
        q={**QUERY,'budget':1,'max_items':1,'required_roles':['contradiction'],'role_coverage_weight':3}
        direct=candidate('direct',score=1,cost=1,roles=['direct'])
        contra=candidate('contra',score=0.2,cost=1,roles=['contradiction'])
        out=compile_selection(q,[direct,contra])
        self.assertEqual(out['selected_ids'],['contra'])
        self.assertEqual(out['coverage']['covered_roles'],['contradiction'])
        self.assertEqual(out['coverage']['missing_roles'],[])
        self.assertEqual(out['solver'],'EXACT_ENUMERATION')
        self.assertEqual(out['optimality'],'PROVEN_FOR_DECLARED_UTILITY')

    def test_required_facets_surface_gap_when_budget_cannot_cover_all(self):
        q={**QUERY,'budget':1,'max_items':1,'required_facets':['physics','failure']}
        a=candidate('a',score=1,cost=1,facets=['physics'])
        b=candidate('b',score=0.5,cost=1,facets=['failure'])
        out=compile_selection(q,[a,b])
        self.assertEqual(len(out['selected_ids']),1)
        self.assertEqual(len(out['coverage']['missing_facets']),1)

    def test_eq_snapshot_collapses_only_safe_group_and_chooses_best_retrieval_representative(self):
        low=candidate('a',score=0.2)
        high=candidate('b',score=1.0)
        c=candidate('c',score=0.8)
        eq={'groups':[
            {'group_id':'EQG.1','members':['a','b'],'representative':'a','collapse_allowed':True,'status':'EQUIVALENT'},
            {'group_id':'EQG.2','members':['c'],'representative':'c','collapse_allowed':False,'status':'SINGLETON'},
        ],'pair_conflicts':[],'transitive_conflicts':[]}
        out=compile_selection(QUERY,[low,high,c],eq)
        self.assertIn('a',out['equivalence']['suppressed'])
        group=next(g for g in out['equivalence']['groups'] if g['eq_group_id']=='EQG.1')
        self.assertEqual(group['retrieval_representative'],'b')
        self.assertNotIn('a',out['rankable_ids'])
        self.assertIn('b',out['rankable_ids'])

    def test_conflicted_eq_snapshot_preserves_candidates(self):
        eq={'groups':[
            {'group_id':'EQG.a','members':['a'],'representative':'a','collapse_allowed':False,'status':'PRESERVE_ALL_CONFLICT'},
            {'group_id':'EQG.b','members':['b'],'representative':'b','collapse_allowed':False,'status':'PRESERVE_ALL_CONFLICT'},
        ],'pair_conflicts':[{'left_id':'a','right_id':'b'}],'transitive_conflicts':[]}
        out=compile_selection(QUERY,[candidate('a'),candidate('b')],eq)
        self.assertEqual(out['equivalence']['suppressed'],[])
        self.assertEqual(sorted(out['rankable_ids']),['a','b'])
        self.assertEqual(len(out['equivalence']['pair_conflicts']),1)

    def test_large_frontier_labels_greedy_as_heuristic(self):
        rows=[candidate(f'c{i:02d}',score=(i+1)/20,cost=1) for i in range(19)]
        out=compile_selection({**QUERY,'budget':3,'max_items':3},rows)
        self.assertEqual(out['solver'],'GREEDY_MARGINAL_UTILITY')
        self.assertEqual(out['optimality'],'HEURISTIC_NOT_PROVEN')
        self.assertEqual(len(out['selected_ids']),3)

    def test_source_authority_is_numeric_retrieval_measurement_not_claim_y(self):
        row=candidate('x')
        self.assertIn('source_authority',row['measurements'])
        self.assertNotIn('y',row['measurements'])
        out=compile_selection(QUERY,[row])
        self.assertEqual(out['selected_ids'],['x'])


class RetrievalLedgerTests(unittest.TestCase):
    def test_persist_get_replay_and_benchmark(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
            store=Store(tmp.name);core=AthenaCore(store);ledger=RetrievalLedger(core)
            run=ledger.compile('query://1',QUERY,[candidate('a',roles=['direct']),candidate('b',roles=['contradiction'])],actor='A1',task='retrieve')
            self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('RAGRUN.'))
            stored=ledger.get(run['run_id']);self.assertEqual(stored['decision_digest'],run['decision_digest'])
            replay=ledger.replay(run['run_id']);self.assertTrue(replay['match']);self.assertEqual(replay['stored_selected'],replay['recomputed_selected'])
            bench=ledger.benchmark();self.assertEqual(bench['retrieval_runs'],1);self.assertEqual(bench['retrieval_replay_match_rate'],1.0)
            store.close()


if __name__=='__main__':unittest.main()

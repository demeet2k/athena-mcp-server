import json
import tempfile
import unittest

from athena_mcp.server import Server


class GapUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args,expect_error=False):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result']
        if expect_error:self.assertTrue(result.get('isError'),r);return result
        self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_verified_path_covers_target_with_explicit_origin_path(self):
        run=self.tool('athena_gap_compile',{'task_ref':'task://path','sources':{'S':['seed']},'edges':[{'id':'e1','src':'seed','dst':'mid','relation':'derive','verified':True,'witness_ref':'edge://1'},{'id':'e2','src':'mid','dst':'target','relation':'bridge','verified':True,'witness_ref':'edge://2'}],'targets':[{'id':'T','node':'target'}],'policy':{'traversable_relations':['derive','bridge'],'max_depth':3,'require_witness':True},'persist':False})
        self.assertEqual(run['closure_kind'],'WITNESSED_DIRECTED_REACHABILITY_NOT_LOGICAL_PROOF');self.assertEqual(run['covered_target_ids'],['T']);self.assertEqual(run['gap_target_ids'],[])
        target=run['targets'][0];self.assertEqual(target['closure_path']['edges'],['e1','e2']);self.assertEqual(target['closure_path']['origin_groups'],['S']);self.assertIn('not logical or causal',run['epistemic_boundary'].replace('/',' or ').lower())

    def test_unverified_or_nontraversable_edges_are_rejected_not_silently_used(self):
        run=self.tool('athena_gap_compile',{'task_ref':'task://reject','sources':{'S':['seed']},'edges':[{'id':'bad1','src':'seed','dst':'A','relation':'derive','verified':False,'witness_ref':'edge://bad'},{'id':'bad2','src':'seed','dst':'B','relation':'support','verified':True,'witness_ref':'edge://2'}],'targets':[{'id':'TA','node':'A','severity':1,'leverage':1,'information_gain':1,'cost':1},{'id':'TB','node':'B','severity':1,'leverage':1,'information_gain':1,'cost':1}],'policy':{'traversable_relations':['derive'],'require_witness':True},'persist':False})
        self.assertEqual(set(run['gap_target_ids']),{'TA','TB'});by={row['id']:row for row in run['rejected_edges']};self.assertIn('edge_not_verified',by['bad1']['defects']);self.assertIn('relation_not_traversable',by['bad2']['defects'])

    def test_missing_residual_metric_routes_to_measurement_not_zero(self):
        run=self.tool('athena_gap_compile',{'task_ref':'task://unknown','sources':{'S':['seed']},'edges':[],'targets':[{'id':'unknown','node':'U','severity':1,'leverage':1,'cost':1},{'id':'known','node':'K','severity':.5,'leverage':1,'information_gain':1,'cost':1}],'policy':{'traversable_relations':[]},'persist':False})
        unknown=next(row for row in run['gap'] if row['id']=='unknown');self.assertEqual(unknown['residual_score']['status'],'UNKNOWN');self.assertIsNone(unknown['residual_score']['value']);self.assertTrue(any(d['metric']=='information_gain' for d in run['measurement_plan'][0]['defects']));self.assertEqual(run['grow']['id'],'known')

    def test_grow_is_highest_known_uncovered_residual_only(self):
        run=self.tool('athena_gap_compile',{'task_ref':'task://grow','sources':{'S':['covered']},'edges':[],'targets':[{'id':'covered','node':'covered','severity':100,'leverage':100,'information_gain':100,'cost':1},{'id':'low','node':'L','severity':1,'leverage':1,'information_gain':1,'cost':1},{'id':'high','node':'H','severity':2,'leverage':3,'information_gain':4,'cost':2}],'policy':{'traversable_relations':[]},'persist':False})
        self.assertEqual(run['grow']['id'],'high');self.assertEqual(run['ranked_gap_ids'][0],'high');covered=next(row for row in run['targets'] if row['id']=='covered');self.assertEqual(covered['residual_score']['status'],'N/A_COVERED')

    def test_max_depth_is_part_of_frozen_closure_policy(self):
        edges=[{'id':'e1','src':'S','dst':'A','relation':'derive','verified':True,'witness_ref':'w1'},{'id':'e2','src':'A','dst':'B','relation':'derive','verified':True,'witness_ref':'w2'}]
        run=self.tool('athena_gap_compile',{'task_ref':'task://depth','sources':{'S':['S']},'edges':edges,'targets':[{'id':'B','node':'B','severity':1,'leverage':1,'information_gain':1,'cost':1}],'policy':{'traversable_relations':['derive'],'max_depth':1,'require_witness':True},'persist':False})
        self.assertIn('A',run['closure_nodes']);self.assertNotIn('B',run['closure_nodes']);self.assertEqual(run['gap_target_ids'],['B'])

    def test_gaprun_replay_is_frozen_against_later_jspace_mutation(self):
        run=self.tool('athena_gap_compile',{'task_ref':'task://replay','sources':{'S':['seed']},'edges':[{'id':'e1','src':'seed','dst':'old','relation':'derive','verified':True,'witness_ref':'edge://old'}],'targets':[{'id':'new','node':'new','severity':1,'leverage':1,'information_gain':1,'cost':1}],'policy':{'traversable_relations':['derive'],'require_witness':True}})
        self.assertEqual(run['gap_target_ids'],['new'])
        self.tool('athena_add_edge',{'src':'seed','relation':'derive','dst':'new','attrs':{'verified':True,'witness_ref':'later://jspace'}})
        replay=self.tool('athena_gap_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay);self.assertEqual(replay['stored_gap'],['new']);self.assertEqual(replay['recomputed_gap'],['new'])

    def test_gap_resource_benchmark_and_collective_alarm_remain_distinct(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};self.assertIn('athena_gap_compile',names);self.assertIn('athena_jspace_alarm',names)
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://gap'})['result']['contents'][0]['text']);self.assertEqual(resource['closure_kind'],'WITNESSED_DIRECTED_REACHABILITY_NOT_LOGICAL_PROOF');self.assertIn('not logical or causal entailment',resource['epistemic_boundary'])
        bench=self.tool('athena_benchmark',{});self.assertIn('gap_runs',bench);self.assertIn('collective_memory',bench)


if __name__=='__main__':unittest.main()

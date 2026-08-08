import json
import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.orchestration_equivalence import REQUIRED_SAMENESS


def measurements(relevance=1,source_authority=1,cross_value=1,decision_relevance=1):
    return {
        'relevance':{'value':relevance,'method':'semantic-test','witness_ref':'m:rel'},
        'source_authority':{'value':source_authority,'method':'provenance-test','witness_ref':'m:auth'},
        'cross_value':{'value':cross_value,'method':'bridge-test','witness_ref':'m:cross'},
        'decision_relevance':{'value':decision_relevance,'method':'decision-test','witness_ref':'m:decision'},
    }

def candidate(ident,score=1,cost=1,roles=None,facets=None,source_time=900,coords=None,lineages=None):
    return {'id':ident,'source_ref':f'source://{ident}','measurements':measurements(score,1,1,1),'source_time':source_time,'cost':cost,'roles':roles or [],'facets':facets or [],'coordinate_keys':coords or [],'lineage_keys':lineages or []}

QUERY={'as_of':1000,'freshness_half_life':100,'budget':10,'max_items':10}

class RetrievalUnifiedTests(unittest.TestCase):
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
    @staticmethod
    def same():return {name:True for name in REQUIRED_SAMENESS}

    def test_missing_measurement_survives_mcp_validation_and_routes_to_measurement(self):
        bad=candidate('missing');bad['measurements'].pop('cross_value')
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://unknown','query':QUERY,'candidates':[bad,candidate('known',score=.1)],'persist':False})
        self.assertEqual(run['selected_ids'],['known'])
        req=next(x for x in run['measurement_plan'] if x['candidate']=='missing')
        self.assertTrue(any(d['metric']=='cross_value' for d in req['defects']))
        missing=next(x for x in run['rows'] if x['id']=='missing');self.assertEqual(missing['score']['status'],'UNKNOWN');self.assertIsNone(missing['score']['value'])

    def test_present_measurement_is_strictly_validated(self):
        bad=candidate('bad');bad['measurements']['relevance']={'value':2,'method':'m','witness_ref':'w'}
        self.tool('athena_retrieval_compile',{'query_ref':'q://bad','query':QUERY,'candidates':[bad]},expect_error=True)
        unwitnessed=candidate('unwitnessed');unwitnessed['measurements']['relevance']={'value':.5,'method':'m','witness_ref':''}
        self.tool('athena_retrieval_compile',{'query_ref':'q://bad2','query':QUERY,'candidates':[unwitnessed]},expect_error=True)

    def test_required_contradiction_role_can_outweigh_higher_similarity(self):
        q={**QUERY,'budget':1,'max_items':1,'required_roles':['contradiction'],'role_coverage_weight':3}
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://roles','query':q,'candidates':[candidate('direct',1,1,['direct']),candidate('contra',.2,1,['contradiction'])],'persist':False})
        self.assertEqual(run['selected_ids'],['contra']);self.assertEqual(run['coverage']['missing_roles'],[]);self.assertEqual(run['solver'],'EXACT_ENUMERATION')

    def test_equivalence_context_is_frozen_before_selection_and_replay(self):
        a=candidate('a',.2);b=candidate('b',1);c=candidate('c',.8)
        self.tool('athena_equivalence_observe',{'context_id':'rag-eq','left_id':'a','right_id':'b','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq://rag'},'same':self.same()})
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://eq','query':QUERY,'candidates':[a,b,c],'equivalence_context':'rag-eq'})
        self.assertIn('a',run['equivalence']['suppressed']);self.assertIn('b',run['selected_ids']);self.assertTrue(run['run_id'].startswith('RAGRUN.'))
        self.tool('athena_equivalence_observe',{'context_id':'rag-eq','left_id':'b','right_id':'c','relation':'DISTINCT','witness':{'verified':True,'ref':'eq://later-distinct'},'different':['lineage']})
        replay=self.tool('athena_retrieval_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay);self.assertEqual(replay['stored_equivalence'],replay['recomputed_equivalence'])

    def test_source_authority_is_not_y_authority(self):
        self.tool('athena_claim_register',{'claim_id':'CLAIM.RAG','source_ref':'source://claim'})
        state=self.tool('athena_claim_state',{'claim_id':'CLAIM.RAG'});self.assertEqual(state['y'],'?')
        row=candidate('source');row['claim_id']='CLAIM.RAG';row['measurements']['source_authority']={'value':1,'method':'publisher-provenance','witness_ref':'prov://1'}
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://authority','query':QUERY,'candidates':[row],'persist':False})
        self.assertEqual(run['selected_ids'],['source']);self.assertEqual(self.tool('athena_claim_state',{'claim_id':'CLAIM.RAG'})['y'],'?')

    def test_pheromone_does_not_fill_missing_rag_measurements(self):
        self.tool('athena_pheromone_reinforce',{'route_key':'source://popular','observations':{'quality':1,'reuse':1,'evidence':1}})
        row=candidate('popular');row['source_ref']='source://popular';row['measurements'].pop('relevance')
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://pheromone','query':QUERY,'candidates':[row],'persist':False})
        self.assertEqual(run['selected_ids'],[]);self.assertEqual(run['rows'][0]['score']['status'],'UNKNOWN');self.assertTrue(any(d['metric']=='relevance' for d in run['measurement_plan'][0]['defects']))
        field=self.tool('athena_pheromone_field',{'route_key':'source://popular'});self.assertTrue(field)

    def test_large_frontier_is_labeled_heuristic_not_proven(self):
        rows=[candidate(f'c{i:02d}',(i+1)/20,1) for i in range(19)]
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://large','query':{**QUERY,'budget':3,'max_items':3},'candidates':rows,'persist':False})
        self.assertEqual(run['solver'],'GREEDY_MARGINAL_UTILITY');self.assertEqual(run['optimality'],'HEURISTIC_NOT_PROVEN');self.assertEqual(len(run['selected_ids']),3)

    def test_resource_benchmark_and_persisted_replay(self):
        run=self.tool('athena_retrieval_compile',{'query_ref':'q://persist','query':QUERY,'candidates':[candidate('a',['direct'] if False else 1),candidate('b',.5)]})
        replay=self.tool('athena_retrieval_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay)
        uris={r['uri'] for r in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://retrieval',uris)
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://retrieval'})['result']['contents'][0]['text']);self.assertEqual(resource['law']['version'],'RAG.1');self.assertIn('not Y1 authority',resource['boundary'])
        bench=self.tool('athena_benchmark',{});self.assertIn('retrieval_runs',bench);self.assertIn('extraction_runs',bench);self.assertIn('equivalence_pairs',bench)


if __name__=='__main__':unittest.main()

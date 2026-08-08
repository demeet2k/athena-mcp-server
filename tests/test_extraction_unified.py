import json
import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.orchestration_equivalence import REQUIRED_SAMENESS


class ExtractionUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
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

    def test_plan_creates_work_contracts_not_semantic_outputs(self):
        run=self.tool('athena_extraction_plan',{'seed_ref':'seed://sx','seed':{'x':1},'transforms':['decompose','falsify'],'max_depth':1,'max_tasks_per_generation':2})
        self.assertTrue(run['run_id'].startswith('EXTRUN.'));self.assertEqual(len(run['tasks']),2)
        self.assertTrue(all(task['status']=='PLANNED' for task in run['tasks']))
        self.assertTrue(all(run['transform_manifest'][task['transform']]['status']=='TASK_GENERATOR_NOT_SEMANTIC_EXECUTOR' for task in run['tasks']))
        frontier=self.tool('athena_extraction_frontier',{'run_id':run['run_id']});self.assertEqual(len(frontier),2)

    def test_completion_is_witness_gated_and_creates_addressable_result(self):
        run=self.tool('athena_extraction_plan',{'seed_ref':'seed://complete','seed':'S','transforms':['formalize']})
        task=run['tasks'][0]
        self.tool('athena_extraction_complete',{'task_id':task['task_id'],'outputs':[{'equation':'x=1'}],'witness':{'verified':False,'ref':'bad'}},expect_error=True)
        completed=self.tool('athena_extraction_complete',{'task_id':task['task_id'],'outputs':[{'equation':'x=1'}],'witness':{'verified':True,'ref':'exec://formalize'}})
        self.assertEqual(completed['status'],'COMPLETED');self.assertEqual(len(completed['result_refs']),1)
        result=self.tool('athena_extraction_result',{'result_id':completed['result_refs'][0]});self.assertEqual(result['payload']['equation'],'x=1');self.assertTrue(result['witness']['verified'])
        self.tool('athena_extraction_complete',{'task_id':task['task_id'],'outputs':[{'second':True}],'witness':{'verified':True,'ref':'dup'}},expect_error=True)

    def test_recursive_expansion_obeys_depth_and_fanout_bounds(self):
        run=self.tool('athena_extraction_plan',{'seed_ref':'seed://depth','seed':'S','transforms':['decompose'],'max_depth':1,'max_tasks_per_generation':2})
        first=self.tool('athena_extraction_complete',{'task_id':run['tasks'][0]['task_id'],'outputs':[{'child':'A'}],'witness':{'verified':True,'ref':'exec://d0'}})
        expansion=self.tool('athena_extraction_expand_result',{'result_id':first['result_refs'][0],'transforms':['formalize','fail','edge']})
        self.assertEqual(expansion['status'],'EXPANDED');self.assertEqual(len(expansion['tasks']),2);self.assertTrue(all(task['depth']==1 for task in expansion['tasks']))
        second=self.tool('athena_extraction_complete',{'task_id':expansion['tasks'][0]['task_id'],'outputs':[{'child':'B'}],'witness':{'verified':True,'ref':'exec://d1'}})
        limit=self.tool('athena_extraction_expand_result',{'result_id':second['result_refs'][0],'transforms':['edge']})
        self.assertEqual(limit['status'],'DEPTH_LIMIT');self.assertEqual(limit['tasks'],[])

    def test_witnessed_failure_records_failure_without_result(self):
        run=self.tool('athena_extraction_plan',{'seed_ref':'seed://fail','seed':'S','transforms':['invert']})
        task=run['tasks'][0]
        failed=self.tool('athena_extraction_fail',{'task_id':task['task_id'],'reason':'inverse undefined on supplied domain','witness':{'verified':True,'ref':'exec://failure'}})
        self.assertEqual(failed['status'],'FAILED')
        state=self.tool('athena_extraction_task',{'task_id':task['task_id']});self.assertEqual(state['status'],'FAILED');self.assertEqual(state['result_refs'],[])

    def test_sx_outputs_remain_distinct_until_eq1_witnesses_equivalence(self):
        run=self.tool('athena_extraction_plan',{'seed_ref':'seed://eq','seed':'S','transforms':['decompose']})
        completed=self.tool('athena_extraction_complete',{'task_id':run['tasks'][0]['task_id'],'outputs':[{'value':'A'},{'value':'A'}],'witness':{'verified':True,'ref':'exec://two-outputs'}})
        a,b=completed['result_refs'];self.assertNotEqual(a,b)
        unknown=self.tool('athena_equivalence_snapshot',{'context_id':'sx-results','candidates':[{'id':a},{'id':b}]})
        self.assertEqual(unknown['suppressed'],[])
        self.tool('athena_equivalence_observe',{'context_id':'sx-results','left_id':a,'right_id':b,'relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq://same-results'},'same':self.same()})
        proven=self.tool('athena_equivalence_snapshot',{'context_id':'sx-results','candidates':[{'id':a},{'id':b}]})
        self.assertEqual(len(proven['suppressed']),1)

    def test_extraction_resource_and_benchmark_are_composed(self):
        names={row['name'] for row in self.rpc('tools/list')['result']['tools']};self.assertIn('athena_extraction_plan',names);self.assertIn('athena_extraction_expand_result',names)
        uris={row['uri'] for row in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://extraction',uris)
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://extraction'})['result']['contents'][0]['text']);self.assertIn('planning creates typed PLANNED transform work only',resource['law']);self.assertEqual(resource['dedup_route'],'use athena_equivalence_snapshot separately when witnessed EQ1 relations exist')
        bench=self.tool('athena_benchmark',{});self.assertIn('extraction_runs',bench);self.assertIn('equivalence_pairs',bench)


if __name__=='__main__':unittest.main()

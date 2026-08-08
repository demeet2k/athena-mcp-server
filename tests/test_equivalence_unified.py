import json
import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.orchestration_equivalence import REQUIRED_SAMENESS


class EquivalenceUnifiedTests(unittest.TestCase):
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

    def test_unknown_sameness_preserves_identity(self):
        snapshot=self.tool('athena_equivalence_snapshot',{'context_id':'D1','candidates':[{'id':'A'},{'id':'B'}]})
        self.assertEqual(snapshot['suppressed'],[])
        self.assertEqual(len(snapshot['groups']),2)
        self.assertTrue(all(not group['collapse_allowed'] for group in snapshot['groups']))

    def test_equivalent_requires_every_preservation_dimension(self):
        partial=self.same();partial.pop('failure_role')
        self.tool('athena_equivalence_observe',{'context_id':'D2','left_id':'A','right_id':'B','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq://partial'},'same':partial},expect_error=True)
        observed=self.tool('athena_equivalence_observe',{'context_id':'D2','left_id':'A','right_id':'B','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq://full'},'same':self.same()})
        self.assertEqual(observed['status'],'ACTIVE')
        snapshot=self.tool('athena_equivalence_snapshot',{'context_id':'D2','candidates':[{'id':'A'},{'id':'B'}]})
        self.assertEqual(snapshot['suppressed'],['B']);self.assertEqual(snapshot['groups'][0]['representative'],'A')

    def test_distinct_or_conflicting_witness_preserves_all(self):
        self.tool('athena_equivalence_observe',{'context_id':'D3','left_id':'A','right_id':'B','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq://yes'},'same':self.same()})
        conflict=self.tool('athena_equivalence_observe',{'context_id':'D3','left_id':'A','right_id':'B','relation':'DISTINCT','witness':{'verified':True,'ref':'eq://no'},'different':['boundary']})
        self.assertEqual(conflict['status'],'CONFLICT')
        snapshot=self.tool('athena_equivalence_snapshot',{'context_id':'D3','candidates':[{'id':'A'},{'id':'B'}]})
        self.assertEqual(snapshot['suppressed'],[]);self.assertEqual(len(snapshot['pair_conflicts']),1)
        self.assertTrue(all(group['status']=='PRESERVE_ALL_CONFLICT' for group in snapshot['groups']))

    def test_authorized_resolution_selects_existing_witnessed_side(self):
        self.tool('athena_equivalence_observe',{'context_id':'D4','left_id':'A','right_id':'B','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq://yes'},'same':self.same()})
        self.tool('athena_equivalence_observe',{'context_id':'D4','left_id':'A','right_id':'B','relation':'DISTINCT','witness':{'verified':True,'ref':'eq://no'},'different':['lineage']})
        resolved=self.tool('athena_equivalence_resolve_conflict',{'context_id':'D4','left_id':'A','right_id':'B','relation':'DISTINCT','authority':{'authorized':True,'ref':'gov://eq'}})
        self.assertEqual(resolved['status'],'ACTIVE');self.assertEqual(resolved['relation'],'DISTINCT')
        snapshot=self.tool('athena_equivalence_snapshot',{'context_id':'D4','candidates':[{'id':'A'},{'id':'B'}]})
        self.assertEqual(snapshot['suppressed'],[]);self.assertEqual(len(snapshot['distinct_edges']),1)

    def test_equivalence_resource_and_benchmark_are_composed(self):
        names={row['name'] for row in self.rpc('tools/list')['result']['tools']};self.assertIn('athena_equivalence_snapshot',names)
        uris={row['uri'] for row in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://equivalence',uris)
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://equivalence'})['result']['contents'][0]['text']);self.assertIn('UNKNOWN sameness preserves identity',resource['law'])
        bench=self.tool('athena_benchmark',{});self.assertIn('equivalence_pairs',bench)


if __name__=='__main__':unittest.main()

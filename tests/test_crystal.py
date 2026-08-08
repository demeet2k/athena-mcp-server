import json, tempfile, unittest
from athena_mcp.store import Store
from athena_mcp.core import AthenaCore
from athena_mcp.bootstrap import bootstrap
from athena_mcp.crystal_runtime import CrystalRuntime

class CrystalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db'); self.s=Store(self.tmp.name); self.c=AthenaCore(self.s); bootstrap(self.c); self.x=CrystalRuntime(self.c)
    def tearDown(self): self.s.close(); self.tmp.close()
    def semantic(self):
        return {'kind':'ARTIFACT','domain':'OUTPUT','verb':'DEVELOP','object_name':'POLYCOORDINATE_CRYSTAL','method':'MAXDEV','input_contract':{'task':'string'},'output_contract':{'text':'string'}}
    def test_full_crystal(self):
        target=self.c.register('MODEL','TEST','HOST','TARGET','FIXTURE',{}, {})
        result=self.x.crystallize_output(
            self.semantic(),
            'Define x. Then x maps to y.',
            'memory://response/1',
            'A1','crystal-test',1,
            edges=[{'relation':'DEPENDS_ON','dst':target['object']['oid']}],
            hyperedges=[{'relation':'COHERE','members':[target['object']['oid'],'OID.EXTERNAL']}],
            math_objects=[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y','assumptions':['typed domain/codomain']}],
            coordinates={'BR21':{'status':'RESOLVED','value':{'operator':'T'},'source':'test'},'KC27':{'status':'N/A','note':'fixture is not a qutrit state'}},
            cut_lm={'status':'PARTIAL','residual':['LIVE_DEPLOYMENT']},
            evidence={'status':'PARTIAL','basis':'unit fixture'}
        )
        m=result['manifest']
        self.assertTrue(result['crystal_id'].startswith('CRYS.'))
        self.assertEqual(m['coordinates']['KC144']['status'],'RESOLVED')
        self.assertEqual(m['coordinates']['BR21']['status'],'RESOLVED')
        self.assertEqual(m['coordinates']['KC27']['status'],'N/A')
        self.assertEqual(m['coordinates']['RIEMANN']['status'],'UNKNOWN')
        self.assertEqual(m['coordinates']['SCALE']['value']['highest'],'S2')
        self.assertEqual(len(m['mathematics']),1)
        self.assertEqual(m['graph_delta']['jspace_after']['out_degree'],1)
        self.assertGreater(m['envelope']['header_token_count'],0)
        self.assertIn('TAI',m['coordinates']['TIME']['value'])
        self.assertIn('TT',m['coordinates']['TIME']['value'])
        dense=self.x.dense_navigate(result['crystal_id'])
        self.assertEqual(dense['type'],'CRYSTAL')
        oid=m['identity']['OID']; objdense=self.x.dense_navigate(oid)
        self.assertTrue(objdense['crystals'])
        self.assertTrue(objdense['math_objects'])
    def test_repeat_is_new_version_not_duplicate_identity(self):
        r1=self.x.crystallize_output(self.semantic(),'v1','memory://1','A1','t',1)
        r2=self.x.crystallize_output(self.semantic(),'v2','memory://2','A1','t',2,expected_vid=r1['manifest']['identity']['VID'])
        self.assertEqual(r1['manifest']['identity']['OID'],r2['manifest']['identity']['OID'])
        self.assertNotEqual(r1['manifest']['identity']['VID'],r2['manifest']['identity']['VID'])
        self.assertEqual(r2['manifest']['lineage']['depth'],2) # register genesis + two output manifestations
    def test_transform_matrix_holonomy_and_path(self):
        a=self.c.register('MODEL','COORD','HOST','A','FIXTURE',{}, {})
        b=self.c.register('MODEL','COORD','HOST','B','FIXTURE',{}, {})
        self.c.add_edge(a['object']['oid'],'MAPS_TO',b['object']['oid'])
        path=self.x.graph_path(a['object']['oid'],b['object']['oid']); self.assertTrue(path['found']); self.assertEqual(path['length'],1)
        for src,dst in [('KC144','JSPACE'),('JSPACE','SCALE'),('SCALE','KC144')]: self.x.register_transform(src,dst,status='FORMALIZED')
        # crystallize so KC144/JSPACE/SCALE are resolved on a subject
        r=self.x.crystallize_output(self.semantic(),'x','memory://x','A1','x',1)
        oid=r['manifest']['identity']['OID']
        mat=self.x.coordinate_matrix(oid); self.assertGreater(mat['transform_coverage'],0); self.assertTrue(mat['closed_triangles'])
        h=self.x.record_holonomy(oid,['CHART.KC144','CHART.JSPACE','CHART.SCALE','CHART.KC144'],{'x':1},{'x':1},{'norm':0},0.0)
        self.assertEqual(h['status'],'MEASURED')
    def test_mcp_tool_surface(self):
        from athena_mcp.server import Server
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            names=[x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']]
            for n in ['athena_crystallize_output','athena_dense_navigate','athena_add_hyperedge','athena_register_transform','athena_coordinate_matrix','athena_record_holonomy','athena_graph_path']:
                self.assertIn(n,names)
            resources=srv.handle({'jsonrpc':'2.0','id':2,'method':'resources/list'})['result']['resources']
            uris={r['uri'] for r in resources}
            self.assertIn('athena://coordinate/charts',uris); self.assertIn('athena://crystals',uris); self.assertIn('athena://math',uris)
            srv.store.close()
if __name__=='__main__': unittest.main()

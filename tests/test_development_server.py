import json
import tempfile
import unittest

from athena_mcp.development_server import DevelopmentServer
from athena_mcp.orchestration_equivalence import REQUIRED_SAMENESS

SAME={name:True for name in REQUIRED_SAMENESS}

class DevelopmentServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db')
        self.server=DevelopmentServer(self.tmp.name)
        self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});self.assertFalse(r['result'].get('isError'),r);return r['result']['structuredContent']

    def test_composition_preserves_all_mature_surfaces(self):
        names=[t['name'] for t in self.rpc('tools/list')['result']['tools']]
        self.assertEqual(names,sorted(names))
        for required in [
            'athena_extraction_plan','athena_extraction_complete','athena_extraction_expand_result',
            'athena_equivalence_observe','athena_equivalence_snapshot','athena_equivalence_resolve_conflict',
            'athena_claim_register','athena_claim_promote','athena_branch_observe','athena_orchestrate',
            'athena_apply_transform','athena_apply_transform_route','athena_finalize_output','athena_verify_emission',
            'athena_crystallize_output','athena_dense_navigate','athena_session_start','athena_git_status'
        ]:self.assertIn(required,names)
        uris={r['uri'] for r in self.rpc('resources/list')['result']['resources']}
        for uri in ['athena://extraction','athena://equivalence','athena://authority','athena://branches','athena://transforms','athena://emissions','athena://orchestration/law']:
            self.assertIn(uri,uris)

    def test_extraction_to_witnessed_result_to_safe_equivalence_snapshot(self):
        plan=self.tool('athena_extraction_plan',{'seed_ref':'seed://demo','seed':{'claim':'x'},'transforms':['decompose','formalize'],'max_depth':1})
        self.assertEqual(len(plan['tasks']),2)
        task=plan['tasks'][0]
        stored=self.tool('athena_extraction_task',{'task_id':task['task_id']})
        self.assertEqual(stored['status'],'PLANNED');self.assertEqual(stored['result_refs'],[])
        done=self.tool('athena_extraction_complete',{'task_id':task['task_id'],'outputs':[{'component':'A'},{'component':'A'}],'witness':{'verified':True,'ref':'worker:demo'}})
        self.assertEqual(len(done['result_refs']),2)
        left,right=done['result_refs']
        eq=self.tool('athena_equivalence_observe',{'context_id':'SX.DEMO','left_id':left,'right_id':right,'relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq:demo'},'same':SAME})
        self.assertEqual(eq['status'],'ACTIVE')
        snap=self.tool('athena_equivalence_snapshot',{'context_id':'SX.DEMO','candidates':[{'id':left},{'id':right}]})
        self.assertEqual(snap['suppressed'],[max(left,right)])
        self.assertEqual(len([g for g in snap['groups'] if g['collapse_allowed']]),1)

    def test_conflicting_dedup_witnesses_preserve_all(self):
        self.tool('athena_equivalence_observe',{'context_id':'C','left_id':'a','right_id':'b','relation':'EQUIVALENT','witness':{'verified':True,'ref':'eq:ab'},'same':SAME})
        conflict=self.tool('athena_equivalence_observe',{'context_id':'C','left_id':'a','right_id':'b','relation':'DISTINCT','witness':{'verified':True,'ref':'d:ab'},'different':['lineage']})
        self.assertEqual(conflict['status'],'CONFLICT')
        snap=self.tool('athena_equivalence_snapshot',{'context_id':'C','candidates':[{'id':'a'},{'id':'b'}]})
        self.assertEqual(snap['suppressed'],[]);self.assertEqual(len(snap['pair_conflicts']),1)
        self.assertTrue(all(g['status']=='PRESERVE_ALL_CONFLICT' for g in snap['groups']))

    def test_recursive_extraction_obeys_run_limits(self):
        plan=self.tool('athena_extraction_plan',{'seed_ref':'seed://r','seed':{'x':1},'transforms':['decompose'],'max_depth':1,'max_tasks_per_generation':1})
        first=self.tool('athena_extraction_complete',{'task_id':plan['tasks'][0]['task_id'],'outputs':[{'part':'p'}],'witness':{'verified':True,'ref':'w:1'}})
        expanded=self.tool('athena_extraction_expand_result',{'result_id':first['result_refs'][0],'transforms':['formalize','falsify']})
        self.assertEqual(len(expanded['tasks']),1);self.assertEqual(expanded['tasks'][0]['transform'],'formalize')
        second=self.tool('athena_extraction_complete',{'task_id':expanded['tasks'][0]['task_id'],'outputs':[{'symbol':'p'}],'witness':{'verified':True,'ref':'w:2'}})
        stop=self.tool('athena_extraction_expand_result',{'result_id':second['result_refs'][0],'transforms':['successor']})
        self.assertEqual(stop['status'],'DEPTH_LIMIT');self.assertEqual(stop['tasks'],[])

    def test_resources_and_benchmark_surface_new_organs(self):
        extraction=json.loads(self.rpc('resources/read',{'uri':'athena://extraction'})['result']['contents'][0]['text'])
        equivalence=json.loads(self.rpc('resources/read',{'uri':'athena://equivalence'})['result']['contents'][0]['text'])
        self.assertIn('dual',extraction['transform_manifest'])
        self.assertEqual(equivalence['law']['default'],'UNKNOWN equivalence preserves identity')
        bench=self.tool('athena_benchmark',{})
        for key in ['extraction_runs','extraction_tasks','equivalence_pairs','authority_claims','branches','orchestration_runs']:
            self.assertIn(key,bench)

    def test_maxdev_prompt_contains_authority_and_extraction_equivalence_laws(self):
        prompt=self.rpc('prompts/get',{'name':'athena_maxdev','arguments':{'agent':'A','task':'T'}})
        text=prompt['result']['messages'][0]['content']['text']
        self.assertIn('14 AUTHORITY:',text);self.assertIn('15 EXTRACTION/EQUIVALENCE:',text)
        self.assertIn('PLANNED != EXECUTED',text);self.assertIn('PRESERVE_ALL_CONFLICT',text)

if __name__=='__main__':unittest.main()

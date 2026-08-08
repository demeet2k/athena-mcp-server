import json
import tempfile
import unittest

from athena_mcp.stack_server import STACK_LAYERS, STACK_VERSION, StackServer, stack_manifest


class StackServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=StackServer(self.tmp.name);self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)

    def test_stack_manifest_is_ordered_and_explicit_about_unresolved_semantics(self):
        manifest=stack_manifest();self.assertEqual(manifest['version'],STACK_VERSION);self.assertEqual([x['index'] for x in STACK_LAYERS],list(range(len(STACK_LAYERS))))
        self.assertEqual(STACK_LAYERS[-1]['name'],'GAP1');self.assertIn('canonical semantic QHUG',manifest['unresolved'][0]);self.assertIn('logical/causal closure',manifest['unresolved'][1])

    def test_stack_resource_is_added_without_removing_prior_resources(self):
        resources=self.rpc('resources/list')['result']['resources'];uris={x['uri'] for x in resources}
        for uri in ['athena://stack','athena://gap','athena://hug','athena://retrieval','athena://extraction','athena://equivalence','athena://authority','athena://branches','athena://transforms','athena://emissions','athena://orchestration/law']:
            self.assertIn(uri,uris)
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://stack'})['result']['contents'][0]['text']);self.assertEqual(payload['version'],STACK_VERSION);self.assertEqual(payload['layers'][0]['name'],'BASE_RUNTIME')

    def test_stack_tools_preserve_cross_organ_surface(self):
        names=[x['name'] for x in self.rpc('tools/list')['result']['tools']]
        self.assertEqual(names,sorted(names))
        for required in ['athena_gap_compile','athena_hug_register','athena_retrieval_compile','athena_extraction_plan','athena_equivalence_observe','athena_claim_register','athena_branch_observe','athena_orchestrate','athena_apply_transform','athena_apply_transform_route','athena_finalize_output','athena_verify_emission','athena_crystallize_output','athena_dense_navigate','athena_session_start','athena_git_status']:
            self.assertIn(required,names)

    def test_stack_boot_benchmark_has_each_persistent_organ(self):
        response=self.rpc('tools/call',{'name':'athena_benchmark','arguments':{}});self.assertFalse(response['result'].get('isError'),response);bench=response['result']['structuredContent']
        for key in ['orchestration_runs','branches','authority_claims','equivalence_pairs','extraction_runs','retrieval_runs','hug_implementations','gap_runs']:
            self.assertIn(key,bench)

    def test_maxdev_prompt_contains_all_new_modular_sections(self):
        text=self.rpc('prompts/get',{'name':'athena_maxdev','arguments':{'agent':'A','task':'T'}})['result']['messages'][0]['content']['text']
        for marker in ['14 AUTHORITY:','15 EXTRACTION/EQUIVALENCE:','16 RETRIEVAL/RAG.1:','17 HUG ABI:','18 GAP/CLOSURE:']:
            self.assertIn(marker,text)

if __name__=='__main__':unittest.main()

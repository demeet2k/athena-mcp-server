import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_hug import HUG_PARAMS, HugRegistry

PARAMS={p:{'meaning':f'canonical meaning of {p}'} for p in HUG_PARAMS}
INPUT_SCHEMA={'type':'object','required':list(HUG_PARAMS),'properties':{p:{} for p in HUG_PARAMS},'additionalProperties':False}
OUTPUT_SCHEMA={'type':'object','required':['state'],'properties':{'state':{}},'additionalProperties':True}
ARGS={p:i for i,p in enumerate(HUG_PARAMS)}

class HugRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.store=Store(self.tmp.name);self.core=AthenaCore(self.store);self.hug=HugRegistry(self.core)
    def tearDown(self):
        self.store.close();self.tmp.close()
    def register(self):
        return self.hug.register('QHUG','1.0','docs://qhug/v1','sha256:implementation',PARAMS,INPUT_SCHEMA,OUTPUT_SCHEMA,actor='A1')['implementation']
    def canonical(self):
        impl=self.register();self.hug.promote(impl['impl_id'],'TESTED',test={'procedure':'run vectors','observation':'observed outputs','result':'pass','witness':{'verified':True,'ref':'test:qhug'}});return self.hug.promote(impl['impl_id'],'CANONICAL',canonical_authority={'authorized':True,'ref':'canon:qhug'})['implementation']

    def test_registration_requires_exact_six_parameter_semantics(self):
        bad=dict(PARAMS);bad.pop('st')
        with self.assertRaises(ValueError):self.hug.register('QHUG','1.0','docs://qhug','d',bad,INPUT_SCHEMA,OUTPUT_SCHEMA)
        extra={**PARAMS,'xx':{'meaning':'extra'}}
        with self.assertRaises(ValueError):self.hug.register('QHUG','1.0','docs://qhug','d',extra,INPUT_SCHEMA,OUTPUT_SCHEMA)
        impl=self.register();self.assertEqual(tuple(impl['parameter_semantics']),HUG_PARAMS);self.assertEqual(impl['status'],'CANDIDATE')

    def test_promotion_is_non_skippable_and_witnessed(self):
        impl=self.register();iid=impl['impl_id']
        with self.assertRaises(ValueError):self.hug.promote(iid,'CANONICAL',canonical_authority={'authorized':True,'ref':'canon'})
        with self.assertRaises(ValueError):self.hug.promote(iid,'TESTED',test={'procedure':'p','observation':'o','result':'r'})
        tested=self.hug.promote(iid,'TESTED',test={'procedure':'p','observation':'o','result':'r','witness':{'verified':True,'ref':'test:1'}});self.assertEqual(tested['implementation']['status'],'TESTED')
        with self.assertRaises(ValueError):self.hug.promote(iid,'CANONICAL',canonical_authority={'authorized':False,'ref':'bad'})
        canonical=self.hug.promote(iid,'CANONICAL',canonical_authority={'authorized':True,'ref':'canon:1'});self.assertEqual(canonical['implementation']['status'],'CANONICAL')

    def test_candidate_cannot_be_invoked_when_canonical_required(self):
        impl=self.register()
        with self.assertRaises(ValueError):self.hug.plan(impl['impl_id'],ARGS,required_status='CANONICAL')
        tested=self.hug.promote(impl['impl_id'],'TESTED',test={'procedure':'p','observation':'o','result':'r','witness':{'verified':True,'ref':'test'}})['implementation']
        planned=self.hug.plan(tested['impl_id'],ARGS,required_status='TESTED');self.assertEqual(planned['status'],'PLANNED');self.assertEqual(planned['execution_boundary'],'EXTERNAL_OR_REGISTERED_EXECUTOR_REQUIRED')

    def test_invocation_requires_exact_six_arguments_and_input_schema(self):
        impl=self.canonical();iid=impl['impl_id']
        missing=dict(ARGS);missing.pop('io')
        with self.assertRaises(ValueError):self.hug.plan(iid,missing)
        extra={**ARGS,'xx':1}
        with self.assertRaises(ValueError):self.hug.plan(iid,extra)
        planned=self.hug.plan(iid,ARGS,context={'rag_run':'RAGRUN.1'});self.assertTrue(planned['invocation_id'].startswith('HUGINV.'));self.assertEqual(planned['context']['rag_run'],'RAGRUN.1')

    def test_completion_requires_output_schema_and_verified_receipt(self):
        impl=self.canonical();planned=self.hug.plan(impl['impl_id'],ARGS);inv=planned['invocation_id']
        with self.assertRaises(ValueError):self.hug.complete(inv,{'wrong':1},{'verified':True,'ref':'exec:1'})
        with self.assertRaises(ValueError):self.hug.complete(inv,{'state':'ok'},{'verified':False,'ref':'bad'})
        done=self.hug.complete(inv,{'state':'ok'},{'verified':True,'ref':'exec:1'});self.assertEqual(done['status'],'COMPLETED');stored=self.hug.invocation(inv);self.assertEqual(stored['output']['state'],'ok');self.assertEqual(stored['receipt']['ref'],'exec:1')
        with self.assertRaises(ValueError):self.hug.complete(inv,{'state':'again'},{'verified':True,'ref':'exec:2'})

    def test_failed_invocation_is_witnessed_and_not_completed(self):
        impl=self.canonical();inv=self.hug.plan(impl['impl_id'],ARGS)['invocation_id']
        with self.assertRaises(ValueError):self.hug.fail(inv,'executor fault',{'verified':False,'ref':'bad'})
        failed=self.hug.fail(inv,'executor fault',{'verified':True,'ref':'failure:1'});self.assertEqual(failed['status'],'FAILED');stored=self.hug.invocation(inv);self.assertIsNone(stored['output']);self.assertEqual(stored['failure']['reason'],'executor fault')

    def test_packet_integrity_replays_without_claiming_semantic_algorithm_replay(self):
        impl=self.canonical();inv=self.hug.plan(impl['impl_id'],ARGS,context={'B':'RAGRUN.X'})['invocation_id'];check=self.hug.verify_packet(inv);self.assertTrue(check['match']);self.assertEqual(check['status'],'PACKET_MATCH');self.assertEqual(check['semantic_replay'],'N/A_UNLESS_REGISTERED_EXECUTOR_REPLAYS_ALGORITHM')

    def test_name_version_collision_cannot_silently_replace_implementation(self):
        self.register()
        with self.assertRaises(ValueError):self.hug.register('QHUG','1.0','docs://qhug/v2','different-digest',PARAMS,INPUT_SCHEMA,OUTPUT_SCHEMA)

    def test_benchmark_separates_implementation_and_invocation_states(self):
        impl=self.canonical();self.hug.plan(impl['impl_id'],ARGS);bench=self.hug.benchmark();self.assertEqual(bench['hug_implementations'],1);self.assertEqual(bench['hug_implementation_status']['CANONICAL'],1);self.assertEqual(bench['hug_invocations'],1);self.assertEqual(bench['hug_invocation_status']['PLANNED'],1)

if __name__=='__main__':unittest.main()

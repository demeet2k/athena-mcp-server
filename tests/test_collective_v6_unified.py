import json
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV6UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_v6_tools_are_advertised_with_unique_names(self):
        tools=self.rpc('tools/list')['result']['tools'];names=[t['name'] for t in tools]
        self.assertEqual(len(names),len(set(names)))
        for name in ['athena_ood_observe','athena_ood_score','athena_nonlinear_predict','athena_experiment_generate','athena_causal_identify','athena_mpc_plan','athena_schedule_certified','athena_pareto_bandit_select','athena_discovery_claim_register','athena_discovery_claim_witness','athena_discovery_claim_state']:
            self.assertIn(name,names)
        self.assertIn('athena_claim_register',names);self.assertIn('athena_claim_state',names)

    def test_y1_and_discovery_claim_registries_are_disjoint_in_schema_and_state(self):
        tools={t['name']:t for t in self.rpc('tools/list')['result']['tools']}
        self.assertEqual(tools['athena_claim_register']['inputSchema']['required'],['claim_id','source_ref'])
        self.assertEqual(tools['athena_discovery_claim_register']['inputSchema']['required'],['claim_key','statement'])
        y=self.tool('athena_claim_register',{'claim_id':'CLAIM.CANON','source_ref':'source://canonical'})
        before=self.tool('athena_claim_state',{'claim_id':'CLAIM.CANON'});self.assertEqual(before['y'],'?')
        shadow=self.tool('athena_discovery_claim_register',{'claim_key':'shadow:k','statement':'candidate science statement'})
        self.tool('athena_discovery_claim_witness',{'claim_id':shadow['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':'lab:A','confidence':.9})
        self.tool('athena_discovery_claim_witness',{'claim_id':shadow['claim_id'],'kind':'TEST','result':'SUPPORTS','independence_key':'lab:B','confidence':.9})
        shadow_state=self.tool('athena_discovery_claim_state',{'claim_id':shadow['claim_id'],'min_independent_support':2});self.assertEqual(shadow_state['status'],'REPLICATED_SUPPORT')
        after=self.tool('athena_claim_state',{'claim_id':'CLAIM.CANON'});self.assertEqual(after['y'],'?');self.assertEqual(after['status'],'ACTIVE');self.assertEqual(before['claim_id'],after['claim_id'])

    def test_discovery_falsification_metadata_does_not_demote_y1(self):
        self.tool('athena_claim_register',{'claim_id':'CLAIM.Y1','source_ref':'source://y1'})
        self.tool('athena_claim_promote',{'claim_id':'CLAIM.Y1','target_y':'+','evidence':[{'kind':'support','verified':True,'ref':'ev://support'}]})
        shadow=self.tool('athena_discovery_claim_register',{'claim_key':'shadow:f','statement':'separate discovery hypothesis'})
        self.tool('athena_discovery_claim_witness',{'claim_id':shadow['claim_id'],'kind':'FALSIFIER','result':'FALSIFIES','independence_key':'lab:C','confidence':1.0})
        shadow_state=self.tool('athena_discovery_claim_state',{'claim_id':shadow['claim_id']});self.assertEqual(shadow_state['status'],'FALSIFICATION_SIGNAL')
        canonical=self.tool('athena_claim_state',{'claim_id':'CLAIM.Y1'});self.assertEqual(canonical['y'],'+');self.assertEqual(canonical['status'],'ACTIVE')

    def test_v6_resource_exposes_model_and_namespace_boundaries(self):
        uris={r['uri'] for r in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://collective/v6',uris)
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://collective/v6'})['result']['contents'][0]['text'])
        self.assertEqual(payload['runtime']['version'],'COLLECTIVE_RUNTIME_V6')
        self.assertEqual(payload['claim_namespace']['canonical_authority_prefix'],'athena_claim_')
        self.assertEqual(payload['claim_namespace']['discovery_shadow_prefix'],'athena_discovery_claim_')
        self.assertIn('never mutates Y1',payload['boundary'])

    def test_ood_read_without_reference_is_explicit_not_false_certainty(self):
        out=self.tool('athena_ood_score',{'features':{'x':.5},'regime':'R'})
        self.assertEqual(out['status'],'NO_REFERENCE_DISTRIBUTION');self.assertEqual(out['reliability'],0.0);self.assertEqual(out['ood_score'],1.0)
        self.tool('athena_ood_observe',{'features':{'x':.1},'regime':'R'})
        observed=self.tool('athena_ood_score',{'features':{'x':.1},'regime':'R'});self.assertIn(observed['status'],{'IN_DISTRIBUTION','SHIFT_WARNING','OOD'});self.assertIn('not evidence that the claim itself is false',observed['law'])


if __name__=='__main__':unittest.main()

import json
import tempfile
import unittest

from athena_mcp.server import Server


class AuthorityCollectiveBraidTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args,expect_error=False):
        response=self.rpc('tools/call',{'name':name,'arguments':args});result=response['result']
        if expect_error:self.assertTrue(result.get('isError'),response);return result
        self.assertFalse(result.get('isError'),response);return result['structuredContent']
    @staticmethod
    def candidate(ident,claim=None,minimum=None,scale=1.0):
        row={'id':ident,'readiness':1,'gain':2*scale,'independence':1,'bridge':1,'cost':1,'delta_j':2*scale,'information_gain':1,'option_value':1,'evidence':1,'connection':1,'replay':1,'navigation':1,'reconstruction':1,'implementation':1,'novelty':1,'duplicate':0,'fake':0,'bloat':0,'unsupported':0,'unhandled_contradiction':0,'coordinate_loss':0}
        if claim:row['claim_id']=claim
        if minimum is not None:row['min_authority']=minimum
        return row

    def test_authority_surface_is_present_in_unified_runtime(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']}
        for name in ['athena_claim_register','athena_claim_promote','athena_claim_challenge','athena_orchestrate','athena_collective_quorum']:
            self.assertIn(name,names)
        uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://authority',uris)

    def test_collective_unanimity_does_not_promote_unknown_claim(self):
        self.tool('athena_claim_register',{'claim_id':'C1','source_ref':'source://c1'})
        quorum=self.tool('athena_collective_quorum',{'candidates':[{'id':'C1','support':1,'evidence_quality':1,'inhibition':0,'contradiction':0}]})
        self.assertIn('decision',quorum)
        state=self.tool('athena_claim_state',{'claim_id':'C1'})
        self.assertEqual(state['y'],'?')
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[self.candidate('candidate','C1','+')]})
        self.assertIsNone(run['next'])
        self.assertEqual(run['authority_plan'][0]['route'],'gather_verified_support')

    def test_verified_evidence_promotes_exactly_one_step_and_unlocks_minimum(self):
        self.tool('athena_claim_register',{'claim_id':'C2','source_ref':'source://c2'})
        self.tool('athena_claim_promote',{'claim_id':'C2','target_y':'+','evidence':[{'kind':'support','verified':True,'ref':'ev://1'}]})
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[self.candidate('candidate','C2','+')]})
        self.assertEqual(run['next']['id'],'candidate')
        self.assertEqual(run['authority_snapshot']['candidate']['authority_state']['y'],'+')
        self.tool('athena_claim_promote',{'claim_id':'C2','target_y':'!'},expect_error=True)

    def test_aorrun_replay_uses_frozen_authority_after_live_challenge(self):
        self.tool('athena_claim_register',{'claim_id':'C3','source_ref':'source://c3'})
        self.tool('athena_claim_promote',{'claim_id':'C3','target_y':'+','evidence':[{'kind':'derive','verified':True,'ref':'ev://3'}]})
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[self.candidate('candidate','C3','+') ]})
        self.assertEqual(run['next']['id'],'candidate')
        self.tool('athena_claim_challenge',{'claim_id':'C3','witness':{'verified':True,'ref':'challenge://3'},'reason':'material counterevidence'})
        live=self.tool('athena_claim_state',{'claim_id':'C3'});self.assertEqual(live['status'],'CHALLENGED')
        replay=self.tool('athena_orchestration_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay)
        self.assertEqual(replay['stored_authority_snapshot']['candidate']['authority_state']['y'],'+')
        newrun=self.tool('athena_orchestrate',{'seed':'S2','candidates':[self.candidate('candidate2','C3','+') ]})
        self.assertIsNone(newrun['next']);self.assertEqual(newrun['authority_plan'][0]['route'],'resolve_challenge')

    def test_canonical_challenge_remains_hash_but_blocks_routing_until_governance(self):
        self.tool('athena_claim_register',{'claim_id':'C4','source_ref':'source://c4'})
        self.tool('athena_claim_promote',{'claim_id':'C4','target_y':'+','evidence':[{'kind':'support','verified':True,'ref':'ev://4'}]})
        self.tool('athena_claim_promote',{'claim_id':'C4','target_y':'!','test':{'procedure':'p','observation':'o','result':'r','witness':{'verified':True,'ref':'test://4'}}})
        self.tool('athena_claim_promote',{'claim_id':'C4','target_y':'#','canonical_authority':{'authorized':True,'ref':'gov://4'}})
        challenged=self.tool('athena_claim_challenge',{'claim_id':'C4','witness':{'verified':True,'ref':'challenge://4'},'reason':'new contradiction'})['claim']
        self.assertEqual(challenged['y'],'#');self.assertEqual(challenged['status'],'CANONICAL_CHALLENGED')
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[self.candidate('candidate','C4','#')]});self.assertIsNone(run['next'])
        resolved=self.tool('athena_claim_resolve_canonical_challenge',{'claim_id':'C4','decision':'UPHOLD','authority':{'authorized':True,'ref':'gov://resolve'}})['claim']
        self.assertEqual(resolved['status'],'ACTIVE');self.assertEqual(resolved['y'],'#')

    def test_manifest_and_authority_resource_state_firewall(self):
        manifest=json.loads(self.rpc('resources/read',{'uri':'athena://manifest'})['result']['contents'][0]['text'])
        self.assertIn('AUTHORITY_Y1',manifest['layers']);self.assertIn('consensus/pheromone/reward are never typed authority',manifest['braid_law'])
        resource=json.loads(self.rpc('resources/read',{'uri':'athena://authority'})['result']['contents'][0]['text'])
        self.assertIn('authority != confidence != consensus != reward',resource['law'])


if __name__=='__main__':unittest.main()

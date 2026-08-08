import json
import tempfile
import unittest

from athena_mcp.server import Server


class PartyCoordinationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db')
        self.server=Server(self.tmp.name)
        self.seq=0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self,method,params=None):
        self.seq+=1
        message={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:message['params']=params
        return self.server.handle(message)

    def tool(self,name,args,expect_error=False):
        response=self.rpc('tools/call',{'name':name,'arguments':args})
        result=response['result']
        if expect_error:
            self.assertTrue(result.get('isError'),response)
            return result
        self.assertFalse(result.get('isError'),response)
        return result['structuredContent']

    @staticmethod
    def form_args():
        return {
            'party_id':'PARTY.TEST',
            'task_ref':'task://multi-goal',
            'leader':'agent.alpha',
            'purpose':'coordinate two complementary goals',
            'capacity':4,
            'goals':[
                {'goal_id':'goal.analysis','required_capabilities':['analysis']},
                {'goal_id':'goal.code','required_capabilities':['code']},
            ],
            'channels':['issue://party-test'],
            'capabilities':['analysis'],
            'claim_refs':['claim.analysis'],
        }

    def form(self):
        return self.tool('athena_party_form',self.form_args())

    def join_beta(self):
        return self.tool('athena_party_join',{
            'party_id':'PARTY.TEST',
            'agent':'agent.beta',
            'channel_ref':'issue://party-test',
            'task_relation':'COMMUTATIVE',
            'coordination_mode':'PARALLEL_COMPLEMENT',
            'capabilities':['code'],
            'claim_refs':['claim.code'],
        })

    def post_work(self,post_id,agent,goal,claim):
        return self.tool('athena_party_board_post',{
            'post_id':post_id,
            'party_id':'PARTY.TEST',
            'agent':agent,
            'kind':'WORKING_ON',
            'channel_ref':'issue://party-test',
            'body':f'working on {goal}',
            'goal_refs':[goal],
            'claim_refs':[claim],
        })

    def test_party_surface_is_registered_without_displacing_transport(self):
        names={tool['name'] for tool in self.rpc('tools/list')['result']['tools']}
        for name in [
            'athena_party_form','athena_party_join','athena_party_board_post',
            'athena_party_state','athena_party_list','athena_party_observe',
            'athena_transport_aor_to_collective','athena_orchestrate'
        ]:
            self.assertIn(name,names)
        uris={item['uri'] for item in self.rpc('resources/list')['result']['resources']}
        self.assertIn('athena://party-coordination/v1',uris)
        self.assertIn('athena://aor-collective/transport',uris)

    def test_form_join_and_duplicate_claim_guards(self):
        formed=self.form()
        self.assertEqual(formed['event'],'PARTY_FORMED')
        self.assertEqual(len(formed['members']),1)
        self.assertFalse(formed['execution_authority'])
        joined=self.join_beta()
        self.assertEqual(joined['event'],'PARTY_JOINED')
        self.assertEqual(len(joined['members']),2)
        again=self.join_beta()
        self.assertTrue(again['idempotent'])

        self.tool('athena_party_join',{
            'party_id':'PARTY.TEST',
            'agent':'agent.duplicate',
            'channel_ref':'issue://party-test',
            'task_relation':'COMMUTATIVE',
            'claim_refs':['claim.analysis'],
        },expect_error=True)
        self.tool('athena_party_join',{
            'party_id':'PARTY.TEST',
            'agent':'agent.conflict',
            'channel_ref':'issue://party-test',
            'task_relation':'CONFLICT',
        },expect_error=True)
        self.tool('athena_party_join',{
            'party_id':'PARTY.TEST',
            'agent':'agent.identical',
            'channel_ref':'issue://party-test',
            'task_relation':'IDENTICAL',
        },expect_error=True)

    def test_identical_work_is_allowed_only_as_explicit_independent_verification(self):
        self.form()
        joined=self.tool('athena_party_join',{
            'party_id':'PARTY.TEST',
            'agent':'agent.verifier',
            'channel_ref':'issue://party-test',
            'task_relation':'IDENTICAL',
            'coordination_mode':'INDEPENDENT_VERIFY',
            'claim_refs':['claim.analysis'],
        })
        verifier=next(m for m in joined['members'] if m['agent']=='agent.verifier')
        self.assertEqual(verifier['coordination_mode'],'INDEPENDENT_VERIFY')
        self.assertTrue(joined['score']['diagnostics']['duplicate_only'])

    def test_board_is_member_scoped_channel_scoped_and_result_witnessed(self):
        self.form()
        self.join_beta()
        self.tool('athena_party_board_post',{
            'post_id':'post.bad-member',
            'party_id':'PARTY.TEST',
            'agent':'agent.outsider',
            'kind':'WORKING_ON',
            'channel_ref':'issue://party-test',
            'body':'duplicate attempt',
            'goal_refs':['goal.analysis'],
        },expect_error=True)
        self.tool('athena_party_board_post',{
            'post_id':'post.bad-result',
            'party_id':'PARTY.TEST',
            'agent':'agent.alpha',
            'kind':'RESULT',
            'channel_ref':'issue://party-test',
            'body':'result without witness',
            'goal_refs':['goal.analysis'],
        },expect_error=True)
        posted=self.post_work('post.alpha','agent.alpha','goal.analysis','claim.analysis')
        self.assertEqual(posted['event'],'PARTY_BOARD_POSTED')
        duplicate=self.post_work('post.alpha','agent.alpha','goal.analysis','claim.analysis')
        self.assertTrue(duplicate['idempotent'])

    def test_xp_bonus_requires_observed_synergy_and_is_small_receipt_gated(self):
        self.form()
        self.join_beta()
        self.post_work('post.alpha','agent.alpha','goal.analysis','claim.analysis')
        self.post_work('post.beta','agent.beta','goal.code','claim.code')

        early=self.tool('athena_party_observe',{
            'observation_id':'OBS.EARLY',
            'party_id':'PARTY.TEST',
            'observer':'observer.meta',
            'base_xp':100,
            'advanced_goal_ids':['goal.analysis','goal.code'],
            'witness_ref':'obs://early',
        })
        self.assertEqual(early['status'],'HOLD')
        self.assertEqual(early['coordination_bonus_xp'],0)
        self.assertIn('NEED_WITNESSED_RESULT_POST',early['hold_reasons'])

        self.tool('athena_party_board_post',{
            'post_id':'post.result',
            'party_id':'PARTY.TEST',
            'agent':'agent.alpha',
            'kind':'RESULT',
            'channel_ref':'issue://party-test',
            'body':'analysis and implementation integrated',
            'goal_refs':['goal.analysis','goal.code'],
            'claim_refs':['claim.analysis','claim.code'],
            'witness_ref':'test://integration',
        })
        award=self.tool('athena_party_observe',{
            'observation_id':'OBS.SUCCESS',
            'party_id':'PARTY.TEST',
            'observer':'observer.meta',
            'base_xp':100,
            'advanced_goal_ids':['goal.analysis','goal.code'],
            'witness_ref':'obs://success',
        })
        self.assertEqual(award['status'],'AWARDED')
        self.assertGreater(award['coordination_bonus_xp'],0)
        self.assertLessEqual(award['coordination_bonus_rate'],0.05)
        self.assertFalse(award['xp_patch']['apply_to_global_xp'])
        self.assertEqual(
            award['score']['big3_cycle'],
            ['Q-LEARN','Q-SEAR','Q-ARSI','Q-LEARN'],
        )
        self.assertEqual(
            award['score']['qarsi_phase_order'],
            ['symphony','recursive','ultra_fine','hyper_fine'],
        )

        replayed=self.tool('athena_party_observe',{
            'observation_id':'OBS.SUCCESS',
            'party_id':'PARTY.TEST',
            'observer':'observer.meta',
            'base_xp':100,
            'advanced_goal_ids':['goal.analysis','goal.code'],
            'witness_ref':'obs://success',
        })
        self.assertTrue(replayed['idempotent'])
        self.assertEqual(replayed['coordination_bonus_xp'],award['coordination_bonus_xp'])

        duplicate_witness=self.tool('athena_party_observe',{
            'observation_id':'OBS.REUSE-WITNESS',
            'party_id':'PARTY.TEST',
            'observer':'observer.meta',
            'base_xp':100,
            'advanced_goal_ids':['goal.analysis','goal.code'],
            'witness_ref':'obs://success',
        })
        self.assertEqual(duplicate_witness['status'],'HOLD')
        self.assertIn('WITNESS_ALREADY_REWARDED',duplicate_witness['hold_reasons'])
        self.assertEqual(duplicate_witness['coordination_bonus_xp'],0)

    def test_resource_and_benchmark_expose_coordination_firewalls(self):
        self.form()
        resource=json.loads(
            self.rpc('resources/read',{'uri':'athena://party-coordination/v1'})
            ['result']['contents'][0]['text']
        )
        self.assertEqual(resource['xp']['membership_bonus'],0)
        self.assertEqual(resource['xp']['max_bonus_rate'],0.05)
        self.assertTrue(any('authority grant' in law for law in resource['laws']))
        bench=self.tool('athena_benchmark',{})
        self.assertEqual(bench['party_count'],1)
        self.assertIn('transport_runs',bench)


if __name__=='__main__':
    unittest.main()

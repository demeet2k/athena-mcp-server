from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _fixture(base: Path):
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    (local / "seed.txt").write_text("seed\n", encoding="utf-8")
    _run(local, "add", ".");_run(local, "commit", "-m", "seed")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "master")

    clone = base / "clone"
    proc = subprocess.run(["git", "clone", str(origin), str(clone)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(clone, "config", "user.name", "clone")
    _run(clone, "config", "user.email", "clone@example.invalid")
    return local, clone


class PartyCoordinationTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory();self.addCleanup(self.td.cleanup)
        local, clone = _fixture(Path(self.td.name))
        self.db_a = str(Path(self.td.name) / "a.db")
        self.db_b = str(Path(self.td.name) / "b.db")
        self.a = Server(self.db_a, git_root=local)
        self.b = Server(self.db_b, git_root=clone)
        self.addCleanup(self.a.store.close);self.addCleanup(self.b.store.close)
        self.board_a = MessageBoardRuntime(self.a.git)
        self.board_b = MessageBoardRuntime(self.b.git)
        self.seq = 0

    def rpc(self, server, method, params=None):
        self.seq += 1
        message = {'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:message['params'] = params
        return server.handle(message)

    def tool(self, server, name, args, expect_error=False):
        response = self.rpc(server, 'tools/call', {'name':name,'arguments':args})
        result = response['result']
        if expect_error:
            self.assertTrue(result.get('isError'), response);return result
        self.assertFalse(result.get('isError'), response)
        return result['structuredContent']

    @staticmethod
    def form_args():
        return {
            'party_id':'PARTY.TEST',
            'leader':'alpha',
            'purpose':'advance analysis and implementation together',
            'goals':[
                {'goal_id':'goal.analysis','required_capabilities':['analysis']},
                {'goal_id':'goal.code','required_capabilities':['code']},
            ],
            'leader_goal_refs':['goal.analysis'],
            'role':'LEAD',
            'capabilities':['analysis'],
            'capacity':4,
        }

    @staticmethod
    def results(suffix=''):
        return [
            {'goal_id':'goal.analysis','agent_id':'alpha','witness_ref':f'result://analysis{suffix}'},
            {'goal_id':'goal.code','agent_id':'beta','witness_ref':f'result://code{suffix}'},
        ]

    def seed_party(self):
        present = self.board_a.present(
            agent_id='alpha',task='Analyze coordination protocol',work_key='goal-analysis',
            targets=['analysis.txt']
        )
        self.assertEqual(present['status'],'PRESENT')
        formed = self.tool(self.a,'athena_party_form',self.form_args())
        self.assertEqual(formed['status'],'PARTY_FORMED')
        self.assertEqual(formed['xp_bonus'],0)

        beta = self.board_b.present(
            agent_id='beta',task='Implement coordination runtime',work_key='goal-code',
            targets=['runtime.py']
        )
        self.assertEqual(beta['status'],'PRESENT')
        joined = self.tool(self.b,'athena_party_join',{
            'party_id':'PARTY.TEST','agent':'beta','goal_refs':['goal.code'],
            'task_relation':'COMMUTATIVE','role':'BUILDER','capabilities':['code'],
        })
        self.assertEqual(joined['status'],'PARTY_JOINED')
        self.assertEqual(joined['xp_bonus'],0)
        return formed, joined

    def party_message(self, suffix=''):
        posted=self.tool(self.a,'athena_party_message',{
            'party_id':'PARTY.TEST','sender':'alpha','recipients':['beta'],
            'goal_refs':['goal.analysis','goal.code'],'message_kind':'HANDOFF',
            'message':f'Analysis and implementation contract are synchronized{suffix}.',
        })
        self.assertEqual(posted['status'],'POSTED')
        self.assertEqual(posted['xp_bonus'],0)
        message_id=posted['message_event']['event_id']
        acked=self.board_b.ack(agent_id='beta',message_id=message_id)
        self.assertEqual(acked['status'],'ACKED')
        return message_id

    def test_tools_and_resource_register_without_displacing_message_board(self):
        tools={row['name'] for row in self.rpc(self.a,'tools/list')['result']['tools']}
        for name in [
            'athena_message_board','athena_party_form','athena_party_join','athena_party_message',
            'athena_party_state','athena_party_list','athena_party_observe','athena_transport_aor_to_collective'
        ]:
            self.assertIn(name,tools)
        resources={row['uri'] for row in self.rpc(self.a,'resources/list')['result']['resources']}
        self.assertIn('athena://party-coordination/v1',resources)
        self.assertIn('athena://aor-collective/transport',resources)

    def test_form_requires_shared_board_presence_and_is_git_shared(self):
        held=self.tool(self.a,'athena_party_form',self.form_args())
        self.assertEqual(held['status'],'LEADER_NOT_PRESENT_HOLD')
        self.board_a.present(agent_id='alpha',task='Analyze coordination protocol',work_key='goal-analysis')
        formed=self.tool(self.a,'athena_party_form',self.form_args())
        self.assertTrue(formed['durable_return'])
        state=self.tool(self.b,'athena_party_state',{'party_id':'PARTY.TEST'})
        self.assertEqual(state['status'],'OK')
        self.assertTrue(state['board']['shared_frontier_verified'])
        self.assertEqual(state['party']['leader'],'alpha')
        self.assertEqual([row['agent_id'] for row in state['members']],['alpha'])

    def test_join_on_second_clone_is_shared_and_identical_requires_board_declaration(self):
        self.seed_party()
        state=self.tool(self.a,'athena_party_state',{'party_id':'PARTY.TEST'})
        self.assertEqual({row['agent_id'] for row in state['members']},{'alpha','beta'})
        self.assertTrue(all(row['board_active'] for row in state['members']))

        gamma=self.board_a.present(agent_id='gamma',task='Independent third lane',work_key='gamma')
        self.assertEqual(gamma['status'],'PRESENT')
        self.tool(self.a,'athena_party_join',{
            'party_id':'PARTY.TEST','agent':'gamma','goal_refs':['goal.analysis'],
            'task_relation':'IDENTICAL','capabilities':['analysis'],
        },expect_error=True)

    def test_ambient_board_chat_cannot_unlock_party_bonus(self):
        self.seed_party()
        posted=self.board_a.post(
            agent_id='alpha',recipients=['beta'],message_kind='UPDATE',
            message='Generic board chat with no party or goal envelope.'
        )
        self.board_b.ack(agent_id='beta',message_id=posted['message_event']['event_id'])
        held=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.AMBIENT','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-ambient'),'witness_ref':'outcome://ambient',
        })
        self.assertEqual(held['status'],'HOLD')
        self.assertIn('NEED_ACKNOWLEDGED_PARTY_COMMUNICATION',held['hold_reasons'])
        self.assertEqual(held['coordination_bonus_xp'],0)
        self.assertEqual(held['communication']['party_scoped_message_count_total'],0)

    def test_acknowledged_party_channel_gates_bonus_and_big3(self):
        self.seed_party()
        early=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.EARLY','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-early'),'witness_ref':'outcome://early',
        })
        self.assertEqual(early['status'],'HOLD')
        self.assertIn('NEED_ACKNOWLEDGED_PARTY_COMMUNICATION',early['hold_reasons'])
        self.assertEqual(early['coordination_bonus_xp'],0)

        self.party_message()
        award=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.SUCCESS','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-v2'),'witness_ref':'outcome://success',
        })
        self.assertEqual(award['status'],'AWARDED')
        self.assertGreater(award['coordination_bonus_xp'],0)
        self.assertLessEqual(award['coordination_bonus_rate'],0.05)
        self.assertFalse(award['xp_patch']['apply_to_global_xp'])
        self.assertEqual(award['score']['big3_cycle'],['Q-LEARN','Q-SEAR','Q-ARSI','Q-LEARN'])
        self.assertEqual(award['score']['big3_version'],'PARTY.BIG3.BOARD.CHANNEL.2')
        self.assertEqual(award['score']['qarsi_phase_order'],['symphony','recursive','ultra_fine','hyper_fine'])
        self.assertGreaterEqual(award['communication']['participant_count'],2)
        self.assertTrue(award['communication']['multi_goal_channel'])
        self.assertEqual(award['communication']['acknowledged_goal_count'],2)
        self.assertEqual(award['communication']['goal_coverage'],1.0)

        replay=self.tool(self.b,'athena_party_observe',{
            'observation_id':'OBS.SUCCESS','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-v2'),'witness_ref':'outcome://success',
        })
        self.assertTrue(replay['idempotent'])
        self.assertEqual(replay['receipt_digest'],award['receipt_digest'])

        duplicate=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.REUSE','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-v3'),'witness_ref':'outcome://success',
        })
        self.assertEqual(duplicate['status'],'HOLD')
        self.assertIn('WITNESS_ALREADY_REWARDED',duplicate['hold_reasons'])
        self.assertEqual(duplicate['coordination_bonus_xp'],0)

    def test_successful_award_resets_communication_reward_window(self):
        self.seed_party()
        first_message=self.party_message('-first')
        first=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.FIRST','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-first'),'witness_ref':'outcome://first',
        })
        self.assertEqual(first['status'],'AWARDED')

        held=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.SECOND.HELD','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-second-held'),'witness_ref':'outcome://second-held',
        })
        self.assertEqual(held['status'],'HOLD')
        self.assertIn('NEED_ACKNOWLEDGED_PARTY_COMMUNICATION',held['hold_reasons'])
        self.assertEqual(held['communication']['message_count'],0)
        self.assertEqual(held['communication']['party_scoped_message_count_total'],1)
        self.assertNotIn(first_message,{edge['message_id'] for edge in held['communication']['acknowledged_edges']})

        second_message=self.party_message('-second')
        self.assertNotEqual(first_message,second_message)
        second=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.SECOND','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':self.results('-second'),'witness_ref':'outcome://second',
        })
        self.assertEqual(second['status'],'AWARDED')
        self.assertGreater(second['coordination_bonus_xp'],0)
        self.assertEqual(second['communication']['acknowledged_message_count'],1)

    def test_result_must_cover_assigned_goals_from_two_party_members(self):
        self.seed_party()
        self.party_message('-bad-result')
        held=self.tool(self.a,'athena_party_observe',{
            'observation_id':'OBS.BAD','party_id':'PARTY.TEST','observer':'meta','base_xp':100,
            'results':[
                {'goal_id':'goal.analysis','agent_id':'alpha','witness_ref':'r://1'},
                {'goal_id':'goal.code','agent_id':'alpha','witness_ref':'r://2'},
            ],
            'witness_ref':'outcome://bad',
        })
        self.assertEqual(held['status'],'HOLD')
        self.assertIn('RESULT_GOAL_NOT_ASSIGNED:alpha:goal.code',held['hold_reasons'])
        self.assertIn('NEED_TWO_RESULT_AGENTS',held['hold_reasons'])

    def test_resource_declares_message_board_as_only_transport(self):
        resource=json.loads(
            self.rpc(self.a,'resources/read',{'uri':'athena://party-coordination/v1'})
            ['result']['contents'][0]['text']
        )
        self.assertEqual(resource['transport'],'ATHENA Message Board V1')
        self.assertEqual(resource['channel']['tool'],'athena_party_message')
        self.assertEqual(resource['channel']['transport'],'ATHENA Message Board V1')
        self.assertEqual(resource['xp']['membership_bonus'],0)
        self.assertEqual(resource['xp']['max_bonus_rate'],0.05)
        self.assertFalse(resource['xp']['global_xp_mutation'])
        self.assertFalse(resource['xp']['ambient_board_chat_eligible'])
        self.assertFalse(resource['xp']['communication_reuse'])
        self.assertEqual(resource['big3']['reiterative_loop'],['Q-LEARN','Q-SEAR','Q-ARSI','Q-LEARN'])
        self.assertTrue(any('sole presence/claim/message transport' in law for law in resource['laws']))


if __name__=='__main__':
    unittest.main()

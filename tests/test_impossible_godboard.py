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


class ImpossibleGodboardTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory();self.addCleanup(self.td.cleanup)
        local, clone = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=local)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=clone)
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
    def open_args(quest_id='IC.TEST'):
        return {
            'quest_id':quest_id,
            'opener_id':'alpha',
            'title':'The Impossible Memory Wall',
            'barrier':'Baseline route exceeds the declared memory ceiling.',
            'success_conditions':['preserve output equivalence','stay under memory ceiling'],
            'search_scope':'fixture://impossible-memory-v1',
            'safety_scope':{'environment':'disposable-test-fixture','authorization':'fixture-only'},
        }

    @staticmethod
    def complete_args(completion_id='COMP.TEST', quest_id='IC.TEST'):
        return {
            'completion_id':completion_id,
            'quest_id':quest_id,
            'agent_id':'alpha',
            'agent_coordinate':'ΩA::FORGE.ARCHITECT.KC144.017',
            'baseline':'Materialize the full intermediate representation.',
            'transformation_class':'CONSTRAINT_INVERSION',
            'decisive_move':'Stream the invariant boundary instead of materializing the interior.',
            'invariant':'The externally observed ordered result is unchanged.',
            'result':'The fixture stays below the memory ceiling while preserving the declared result.',
            'witness_refs':['fixture://result/a','fixture://memory/a'],
            'cleanup_status':'VERIFIED',
            'unknown_residue':0,
            'proof_tier':'P2',
            'score_dimensions':{
                'novelty':9,'difficulty':9,'verification':8,'safety':10,'reusability':9,
            },
            'multipliers':{
                'elegance':True,'invariant_discovery':True,'generalization':True,
                'paradigm_shift':False,'impossible_door':True,
            },
            'failed_approaches':['full materialization'],
            'known_limits':['ordered stream only'],
        }

    def seed_single(self):
        present = self.board_a.present(
            agent_id='alpha',task='Solve the impossible memory fixture',work_key='ic-memory',
            targets=['fixture-memory']
        )
        self.assertEqual(present['status'],'PRESENT')
        opened = self.tool(self.a,'athena_impossible_open',self.open_args())
        self.assertEqual(opened['status'],'QUEST_OPENED')
        completed = self.tool(self.a,'athena_impossible_complete',self.complete_args())
        self.assertEqual(completed['status'],'COMPLETED')
        return completed

    def test_tools_and_resource_are_composed_without_displacing_party_or_board(self):
        tools={row['name'] for row in self.rpc(self.a,'tools/list')['result']['tools']}
        for name in [
            'athena_message_board','athena_party_form','athena_impossible_open',
            'athena_impossible_complete','athena_impossible_verify','athena_impossible_state',
            'athena_godboard','athena_hall_of_immortals','athena_transport_aor_to_collective',
        ]:
            self.assertIn(name,tools)
        resources={row['uri'] for row in self.rpc(self.a,'resources/list')['result']['resources']}
        self.assertIn('athena://impossible-godboard/v1',resources)
        self.assertIn('athena://party-coordination/v1',resources)
        resource=json.loads(
            self.rpc(self.a,'resources/read',{'uri':'athena://impossible-godboard/v1'})
            ['result']['contents'][0]['text']
        )
        self.assertEqual(resource['transport'],'ATHENA Message Board V1')
        self.assertEqual(resource['agent_coordinate'],'ΩA::<REALM>.<ROLE>.<LINEAGE>.<INSTANCE>')
        self.assertFalse(resource['score']['global_xp_mutation'])
        self.assertIn('CLEANUP != CONCEALMENT',resource['firewalls'])

    def test_open_requires_presence_and_is_shared(self):
        held=self.tool(self.a,'athena_impossible_open',self.open_args())
        self.assertEqual(held['status'],'OPENER_NOT_PRESENT_HOLD')
        self.board_a.present(agent_id='alpha',task='Open challenge',work_key='open-ic')
        opened=self.tool(self.a,'athena_impossible_open',self.open_args())
        self.assertTrue(opened['durable_return'])
        state=self.tool(self.b,'athena_impossible_state',{'quest_id':'IC.TEST'})
        self.assertEqual(state['status'],'OK')
        self.assertTrue(state['shared_frontier_verified'])
        self.assertEqual(state['quest']['status'],'OPEN')
        self.assertEqual(state['quest']['search_scope'],'fixture://impossible-memory-v1')

    def test_completion_gate_coordinate_tag_and_no_global_xp_authority(self):
        self.board_a.present(agent_id='alpha',task='Solve challenge',work_key='solve-ic')
        self.tool(self.a,'athena_impossible_open',self.open_args())
        dirty=self.complete_args('COMP.DIRTY')
        dirty['cleanup_status']='HOLD';dirty['unknown_residue']=1
        held=self.tool(self.a,'athena_impossible_complete',dirty)
        self.assertEqual(held['status'],'CLEANUP_HOLD')
        self.assertIsNone(held['completed_tag'])
        self.assertFalse(held['durable_return'])

        invalid=self.complete_args('COMP.BADCOORD')
        invalid['agent_coordinate']='alpha'
        self.tool(self.a,'athena_impossible_complete',invalid,expect_error=True)

        done=self.tool(self.a,'athena_impossible_complete',self.complete_args())
        coordinate='ΩA::FORGE.ARCHITECT.KC144.017'
        self.assertEqual(done['agent_tags'][coordinate]['completed'],f'⟦✓ COMPLETED · {coordinate}⟧')
        self.assertEqual(done['score_standing'],'PROVISIONAL_UNTIL_P3')
        self.assertFalse(done['score']['global_xp_mutation'])
        self.assertFalse(done['execution_authority'])
        self.assertEqual(done['cleanup_status'],'VERIFIED')
        self.assertEqual(done['unknown_residue'],0)

    def test_p3_p4_p5_mints_immortal_world_first_crown_monument_and_hall(self):
        done=self.seed_single()
        coordinate='ΩA::FORGE.ARCHITECT.KC144.017'
        self.board_b.present(agent_id='beta',task='Independently verify impossible result',work_key='verify-ic')

        p3=self.tool(self.b,'athena_impossible_verify',{
            'verification_id':'VERIFY.P3','completion_id':'COMP.TEST','verifier_id':'beta',
            'verifier_coordinate':'ΩA::LAB.PROVER.BR21.004','target_proof_tier':'P3',
            'witness_refs':['fixture://independent-replay'],
            'immortal_title':'THE WALLLESS ARCHITECT',
        })
        self.assertEqual(p3['proof_tier'],'P3')
        self.assertTrue(p3['world_first'])
        self.assertEqual(len(p3['immortals']),1)
        self.assertEqual(p3['immortals'][0]['title'],'THE WALLLESS ARCHITECT')
        self.assertEqual(p3['agent_tags'][coordinate]['world_first'],f'⟦◆ WORLD-FIRST · {coordinate}⟧')
        self.assertEqual(p3['score_standing'],'VERIFIED_SCOPED')
        self.assertFalse(p3['xp_authority'])

        self.tool(self.b,'athena_impossible_verify',{
            'verification_id':'VERIFY.P4.BAD','completion_id':'COMP.TEST','verifier_id':'beta',
            'verifier_coordinate':'ΩA::LAB.PROVER.BR21.004','target_proof_tier':'P4',
            'witness_refs':['fixture://adversarial'],
            'attack_refs':['a1'],
        },expect_error=True)
        attacks=[f'fixture://attack/{i}' for i in range(5)]
        p4=self.tool(self.b,'athena_impossible_verify',{
            'verification_id':'VERIFY.P4','completion_id':'COMP.TEST','verifier_id':'beta',
            'verifier_coordinate':'ΩA::LAB.PROVER.BR21.004','target_proof_tier':'P4',
            'witness_refs':['fixture://adversarial-pass'],'attack_refs':attacks,
        })
        self.assertEqual(p4['proof_tier'],'P4')
        self.assertEqual(p4['agent_tags'][coordinate]['omega_crown'],f'⟦♜ ΩCROWN · {coordinate}⟧')

        p5=self.tool(self.b,'athena_impossible_verify',{
            'verification_id':'VERIFY.P5','completion_id':'COMP.TEST','verifier_id':'beta',
            'verifier_coordinate':'ΩA::LAB.PROVER.BR21.004','target_proof_tier':'P5',
            'witness_refs':['fixture://crystal-pass'],'attack_refs':attacks,
            'generalization_ref':'fixture://generalization/v1',
            'downstream_reuse_refs':['fixture://downstream/quest-2'],
        })
        self.assertEqual(p5['status'],'CRYSTALLIZED')
        self.assertEqual(p5['proof_tier'],'P5')
        self.assertIn('IMMORTAL COMPLETION',p5['agent_tags'][coordinate]['immortal_completion'])
        self.assertIn('THE WALLLESS ARCHITECT',p5['agent_tags'][coordinate]['immortal_completion'])

        state=self.tool(self.a,'athena_impossible_state',{'quest_id':'IC.TEST'})
        self.assertEqual(state['quest']['status'],'CRYSTALLIZED')
        self.assertIsNotNone(state['monument'])
        self.assertEqual(state['monument']['winning_transformation'],'CONSTRAINT_INVERSION')

        hall=self.tool(self.a,'athena_hall_of_immortals',{})
        self.assertEqual(len(hall['entries']),1)
        self.assertEqual(hall['entries'][0]['agent_coordinate'],coordinate)
        self.assertEqual(hall['entries'][0]['title'],'THE WALLLESS ARCHITECT')
        self.assertEqual(hall['entries'][0]['proof_tier'],'P5')

        godboard=self.tool(self.a,'athena_godboard',{})
        self.assertEqual(set(godboard['boards']),{'ΩGB-1','ΩGB-2','ΩGB-3','ΩGB-4','ΩGB-5','ΩGB-6','ΩGB-7'})
        top=godboard['boards']['ΩGB-1']['rows'][0]
        self.assertEqual(top['agent_coordinate'],coordinate)
        self.assertIn('THE WALLLESS ARCHITECT',top['immortal_titles'])
        self.assertEqual(godboard['verified_completion_count'],1)
        self.assertFalse(godboard['execution_authority'])

    def test_multi_agent_credit_consumes_shared_party_and_preserves_residual(self):
        self.board_a.present(
            agent_id='alpha',task='Analyze impossible party quest',work_key='party-analysis',targets=['analysis']
        )
        formed=self.tool(self.a,'athena_party_form',{
            'party_id':'PARTY.IC','leader':'alpha','purpose':'solve impossible fixture together',
            'goals':[
                {'goal_id':'goal.analysis','required_capabilities':['analysis']},
                {'goal_id':'goal.code','required_capabilities':['code']},
            ],
            'leader_goal_refs':['goal.analysis'],'capabilities':['analysis'],'capacity':4,
        })
        self.assertEqual(formed['status'],'PARTY_FORMED')
        self.board_b.present(
            agent_id='beta',task='Implement impossible party quest',work_key='party-code',targets=['code']
        )
        joined=self.tool(self.b,'athena_party_join',{
            'party_id':'PARTY.IC','agent':'beta','goal_refs':['goal.code'],
            'task_relation':'COMMUTATIVE','capabilities':['code'],
        })
        self.assertEqual(joined['status'],'PARTY_JOINED')

        self.tool(self.a,'athena_impossible_open',self.open_args('IC.PARTY'))
        args=self.complete_args('COMP.PARTY','IC.PARTY')
        args['party_id']='PARTY.IC'
        args['contributors']=[
            {
                'agent_id':'alpha','agent_coordinate':'ΩA::FORGE.ARCHITECT.KC144.017',
                'role':'ARCHITECT','witness_refs':['fixture://analysis-contribution'],'credit':0.6,
            },
            {
                'agent_id':'beta','agent_coordinate':'ΩA::LAB.BUILDER.KC144.018',
                'role':'BUILDER','witness_refs':['fixture://code-contribution'],'credit':0.3,
            },
        ]
        done=self.tool(self.a,'athena_impossible_complete',args)
        self.assertEqual(done['status'],'COMPLETED')
        self.assertEqual(len(done['contributors']),2)
        self.assertAlmostEqual(done['unattributed_credit_residual'],0.1)
        self.assertEqual(done['party_id'],'PARTY.IC')
        self.assertIn('ΩA::LAB.BUILDER.KC144.018',done['agent_tags'])

        no_party=self.complete_args('COMP.BADPARTY','IC.PARTY')
        no_party['contributors']=args['contributors']
        self.tool(self.a,'athena_impossible_complete',no_party,expect_error=True)


if __name__=='__main__':
    unittest.main()

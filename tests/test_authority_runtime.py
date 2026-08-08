import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_authority import AuthorityLedger
from athena_mcp.orchestration_authority_runtime import AuthorityOrchestrationRuntime


BASE = {
    'readiness': 1,
    'gain': 2,
    'independence': 1,
    'bridge': 1,
    'cost': 1,
    'delta_j': 2,
    'information_gain': 1,
    'option_value': 1,
    'evidence': 1,
    'connection': 1,
    'replay': 1,
    'navigation': 1,
    'reconstruction': 1,
    'implementation': 1,
    'novelty': 1,
    'duplicate': 0,
    'fake': 0,
    'bloat': 0,
    'unsupported': 0,
    'unhandled_contradiction': 0,
    'coordinate_loss': 0,
}


class AuthorityRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        self.authority = AuthorityLedger(self.core)
        self.runtime = AuthorityOrchestrationRuntime(self.core, authority=self.authority)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def _canonicalize(self, claim_id):
        self.authority.promote(claim_id, '+', evidence=[{'kind': 'support', 'verified': True, 'ref': f'ev:{claim_id}'}])
        self.authority.promote(claim_id, '!', test={'procedure': 'p', 'observation': 'o', 'result': 'r', 'witness': {'verified': True, 'ref': f'test:{claim_id}'}})
        self.authority.promote(claim_id, '#', canonical_authority={'authorized': True, 'ref': f'canon:{claim_id}'})

    def test_persisted_input_contains_authority_snapshot(self):
        self.authority.register('CLAIM.P', 'source://p')
        self.authority.promote('CLAIM.P', '+', evidence=[{'kind': 'derive', 'verified': True, 'ref': 'proof:p'}])
        run = self.runtime.compile(
            'seed',
            candidates=[{'id': 'work', 'claim_id': 'CLAIM.P', 'min_authority': '+', **BASE}],
            actor='A1',
            task='authority-persist',
        )
        self.assertTrue(run['persisted'])
        self.assertTrue(run['run_id'].startswith('AORRUN.'))
        self.assertEqual(run['next']['id'], 'work')

        stored = self.runtime.get(run['run_id'])
        snap = stored['input']['candidates'][0]['authority_state']
        self.assertEqual(snap['claim_id'], 'CLAIM.P')
        self.assertEqual(snap['y'], '+')
        self.assertEqual(snap['status'], 'ACTIVE')
        self.assertEqual(stored['decision_digest'], run['decision_digest'])

    def test_challenge_after_run_does_not_change_replay(self):
        self.authority.register('CLAIM.H', 'source://h')
        self._canonicalize('CLAIM.H')
        candidate = {'id': 'route', 'claim_id': 'CLAIM.H', 'min_authority': '#', **BASE}

        active_run = self.runtime.compile('seed', candidates=[candidate], actor='A1', task='active')
        self.assertEqual(active_run['next']['id'], 'route')

        self.authority.challenge(
            'CLAIM.H', {'verified': True, 'ref': 'challenge:h'}, 'new contradiction'
        )
        challenged_run = self.runtime.compile('seed', candidates=[candidate], actor='A1', task='challenged')
        self.assertIsNone(challenged_run['next'])
        self.assertNotEqual(active_run['decision_digest'], challenged_run['decision_digest'])

        replay_active = self.runtime.replay(active_run['run_id'])
        replay_challenged = self.runtime.replay(challenged_run['run_id'])
        self.assertTrue(replay_active['match'])
        self.assertTrue(replay_challenged['match'])
        self.assertEqual(replay_active['stored_next'], 'route')
        self.assertIsNone(replay_challenged['stored_next'])

        self.authority.resolve_canonical_challenge(
            'CLAIM.H', 'UPHOLD', {'authorized': True, 'ref': 'resolver:h'}
        )
        resolved_run = self.runtime.compile('seed', candidates=[candidate], actor='A1', task='resolved')
        self.assertEqual(resolved_run['next']['id'], 'route')

        # Both historical decisions remain stable after present authority changes.
        self.assertTrue(self.runtime.replay(active_run['run_id'])['match'])
        self.assertTrue(self.runtime.replay(challenged_run['run_id'])['match'])
        self.assertEqual(
            self.runtime.replay(challenged_run['run_id'])['stored_authority_snapshot']['route']['authority_state']['status'],
            'CANONICAL_CHALLENGED'
        )

    def test_benchmark_replays_authority_runs(self):
        self.authority.register('CLAIM.B', 'source://b')
        self.runtime.compile('seed', candidates=[{'id': 'b', 'claim_id': 'CLAIM.B', **BASE}])
        bench = self.runtime.benchmark()
        self.assertEqual(bench['orchestration_runs'], 1)
        self.assertEqual(bench['replay_sample'], 1)
        self.assertEqual(bench['replay_matches'], 1)
        self.assertEqual(bench['replay_match_rate'], 1.0)


if __name__ == '__main__':
    unittest.main()

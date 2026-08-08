import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_authority import AuthorityLedger
from athena_mcp.orchestration_authority_compile import compile_authority_orchestration


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


class AuthorityAwareCompilerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        self.auth = AuthorityLedger(self.core)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def _compile(self, candidate):
        snapshot = self.auth.enrich_candidates([candidate])
        return compile_authority_orchestration('seed', snapshot)

    def _canonicalize(self, claim_id):
        self.auth.promote(claim_id, '+', evidence=[{'kind': 'support', 'verified': True, 'ref': f'ev:{claim_id}'}])
        self.auth.promote(claim_id, '!', test={'procedure': 'p', 'observation': 'o', 'result': 'r', 'witness': {'verified': True, 'ref': f'test:{claim_id}'}})
        self.auth.promote(claim_id, '#', canonical_authority={'authorized': True, 'ref': f'canon:{claim_id}'})

    def test_minimum_authority_blocks_until_lawful_promotion(self):
        self.auth.register('CLAIM.MIN', 'source://min')
        candidate = {'id': 'work', 'claim_id': 'CLAIM.MIN', 'min_authority': '+', **BASE}

        unresolved = self._compile(candidate)
        self.assertIsNone(unresolved['next'])
        row = unresolved['frontier'][0]
        self.assertEqual(row['gate']['gates']['authority']['reason'], 'authority_below_minimum')
        self.assertEqual(row['allocation'], ['gather_verified_support'])
        self.assertEqual(unresolved['authority_plan'][0]['minimum'], '+')

        self.auth.promote('CLAIM.MIN', '+', evidence=[{'kind': 'derive', 'verified': True, 'ref': 'proof:min'}])
        supported = self._compile(candidate)
        self.assertEqual(supported['next']['id'], 'work')
        self.assertEqual(supported['frontier'][0]['gate']['gates']['authority']['status'], 'PASS')

    def test_missing_persistent_claim_blocks_declared_minimum(self):
        candidate = {'id': 'missing', 'claim_id': 'CLAIM.NONE', 'min_authority': '!', **BASE}
        out = self._compile(candidate)
        self.assertIsNone(out['next'])
        gate = out['frontier'][0]['gate']['gates']['authority']
        self.assertEqual(gate['reason'], 'missing_authority_state')
        self.assertEqual(gate['route'], 'resolve_or_register_claim')

    def test_unlinked_or_unrestricted_hypothesis_can_be_explored(self):
        self.auth.register('CLAIM.HYP', 'source://hyp')
        linked = self._compile({'id': 'linked', 'claim_id': 'CLAIM.HYP', **BASE})
        self.assertEqual(linked['next']['id'], 'linked')
        self.assertEqual(linked['frontier'][0]['gate']['gates']['authority']['route'], 'explore')

        unlinked = compile_authority_orchestration('seed', [{'id': 'free', **BASE}])
        self.assertEqual(unlinked['next']['id'], 'free')

    def test_challenged_canonical_blocks_even_when_minimum_is_met(self):
        self.auth.register('CLAIM.CANON', 'source://canon')
        self._canonicalize('CLAIM.CANON')
        candidate = {'id': 'canonical-work', 'claim_id': 'CLAIM.CANON', 'min_authority': '#', **BASE}
        before = self._compile(candidate)
        self.assertEqual(before['next']['id'], 'canonical-work')

        self.auth.challenge(
            'CLAIM.CANON',
            {'verified': True, 'ref': 'challenge:canon'},
            'new contradiction'
        )
        blocked = self._compile(candidate)
        self.assertIsNone(blocked['next'])
        gate = blocked['frontier'][0]['gate']['gates']['authority']
        self.assertEqual(gate['authority_status'], 'CANONICAL_CHALLENGED')
        self.assertEqual(gate['route'], 'resolve_canonical_challenge')
        self.assertIn('gate:authority', blocked['decision_explanation']['rejected'][0]['reasons'])

    def test_authority_snapshot_replay_isolated_from_later_resolution(self):
        self.auth.register('CLAIM.REPLAY', 'source://replay')
        self._canonicalize('CLAIM.REPLAY')
        candidate = {'id': 'route', 'claim_id': 'CLAIM.REPLAY', 'min_authority': '#', **BASE}
        self.auth.challenge(
            'CLAIM.REPLAY',
            {'verified': True, 'ref': 'challenge:replay'},
            'challenge at decision time'
        )

        frozen_candidates = self.auth.enrich_candidates([candidate])
        frozen = compile_authority_orchestration('seed', frozen_candidates)
        self.assertIsNone(frozen['next'])
        frozen_digest = frozen['decision_digest']
        self.assertEqual(
            frozen['authority_snapshot']['route']['authority_state']['status'],
            'CANONICAL_CHALLENGED'
        )

        self.auth.resolve_canonical_challenge(
            'CLAIM.REPLAY', 'UPHOLD', {'authorized': True, 'ref': 'resolver:replay'}
        )

        # Historical snapshot recompilation is unchanged after live authority moves.
        replayed = compile_authority_orchestration('seed', frozen_candidates)
        self.assertEqual(replayed['decision_digest'], frozen_digest)
        self.assertIsNone(replayed['next'])

        current = self._compile(candidate)
        self.assertEqual(current['next']['id'], 'route')
        self.assertNotEqual(current['decision_digest'], frozen_digest)
        self.assertEqual(
            current['authority_snapshot']['route']['authority_state']['status'],
            'ACTIVE'
        )

    def test_challenged_noncanonical_claim_blocks_until_new_evidence_path(self):
        self.auth.register('CLAIM.SUP', 'source://sup')
        self.auth.promote('CLAIM.SUP', '+', evidence=[{'kind': 'support', 'verified': True, 'ref': 'ev:sup'}])
        candidate = {'id': 'supported-work', 'claim_id': 'CLAIM.SUP', 'min_authority': '+', **BASE}
        self.assertEqual(self._compile(candidate)['next']['id'], 'supported-work')

        self.auth.challenge('CLAIM.SUP', {'verified': True, 'ref': 'challenge:sup'}, 'support defect')
        out = self._compile(candidate)
        self.assertIsNone(out['next'])
        gate = out['frontier'][0]['gate']['gates']['authority']
        self.assertEqual(gate['authority_status'], 'CHALLENGED')
        self.assertEqual(gate['route'], 'resolve_challenge')


if __name__ == '__main__':
    unittest.main()

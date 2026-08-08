import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_authority import AuthorityLedger


class AuthorityLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        self.auth = AuthorityLedger(self.core)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def test_non_skippable_witnessed_promotion_chain(self):
        created = self.auth.register('CLAIM.A', 'source://claim/a', actor='A1')
        self.assertEqual(created['claim']['y'], '?')
        self.assertEqual(created['claim']['status'], 'ACTIVE')

        with self.assertRaises(ValueError):
            self.auth.promote('CLAIM.A', '!', actor='A1')
        with self.assertRaises(ValueError):
            self.auth.promote('CLAIM.A', '+', evidence=[{'kind': 'support', 'verified': False, 'ref': 'ev:bad'}], actor='A1')

        supported = self.auth.promote(
            'CLAIM.A', '+',
            evidence=[{'kind': 'support', 'verified': True, 'ref': 'ev:1'}],
            actor='A1'
        )
        self.assertEqual(supported['transition'], '?->+')
        self.assertEqual(supported['claim']['y'], '+')
        self.assertEqual(supported['claim']['evidence'][0]['ref'], 'ev:1')

        with self.assertRaises(ValueError):
            self.auth.promote(
                'CLAIM.A', '!',
                test={'procedure': 'p', 'observation': 'o', 'result': 'r'},
                actor='A1'
            )

        executed = self.auth.promote(
            'CLAIM.A', '!',
            test={
                'procedure': 'p',
                'observation': 'o',
                'result': 'r',
                'witness': {'verified': True, 'ref': 'test:1'},
            },
            actor='A1'
        )
        self.assertEqual(executed['transition'], '+->!')
        self.assertEqual(executed['claim']['y'], '!')

        with self.assertRaises(ValueError):
            self.auth.promote('CLAIM.A', '#', canonical_authority={'authorized': False, 'ref': 'canon:bad'}, actor='A1')

        canonical = self.auth.promote(
            'CLAIM.A', '#',
            canonical_authority={'authorized': True, 'ref': 'canon:1'},
            actor='A1'
        )
        self.assertEqual(canonical['transition'], '!->#')
        self.assertEqual(canonical['claim']['y'], '#')
        self.assertEqual(canonical['claim']['canonical_ref'], 'canon:1')

    def test_challenge_semantics_preserve_canonical_until_authorized_resolution(self):
        self.auth.register('CLAIM.C', 'source://claim/c')
        self.auth.promote('CLAIM.C', '+', evidence=[{'kind': 'derive', 'verified': True, 'ref': 'proof:c'}])
        self.auth.promote('CLAIM.C', '!', test={'procedure': 'p', 'observation': 'o', 'result': 'r', 'witness': {'verified': True, 'ref': 'test:c'}})
        self.auth.promote('CLAIM.C', '#', canonical_authority={'authorized': True, 'ref': 'canon:c'})

        with self.assertRaises(ValueError):
            self.auth.challenge('CLAIM.C', {'verified': False, 'ref': 'challenge:bad'}, 'bad witness')

        challenged = self.auth.challenge(
            'CLAIM.C',
            {'verified': True, 'ref': 'challenge:1'},
            'new contradictory evidence'
        )
        self.assertEqual(challenged['claim']['y'], '#')
        self.assertEqual(challenged['claim']['status'], 'CANONICAL_CHALLENGED')

        with self.assertRaises(ValueError):
            self.auth.resolve_canonical_challenge(
                'CLAIM.C', 'DEMOTE', {'authorized': False, 'ref': 'resolver:bad'}
            )

        resolved = self.auth.resolve_canonical_challenge(
            'CLAIM.C', 'DEMOTE', {'authorized': True, 'ref': 'resolver:1'}
        )
        self.assertEqual(resolved['claim']['y'], '!')
        self.assertEqual(resolved['claim']['status'], 'ACTIVE')
        self.assertEqual(resolved['decision'], 'DEMOTE')

    def test_noncanonical_challenge_returns_to_unknown(self):
        self.auth.register('CLAIM.N', 'source://claim/n')
        self.auth.promote('CLAIM.N', '+', evidence=[{'kind': 'reproduce', 'verified': True, 'ref': 'rep:n'}])
        challenged = self.auth.challenge(
            'CLAIM.N', {'verified': True, 'ref': 'challenge:n'}, 'replication defect'
        )
        self.assertEqual(challenged['claim']['y'], '?')
        self.assertEqual(challenged['claim']['status'], 'CHALLENGED')

    def test_candidate_enrichment_is_snapshot_only(self):
        self.auth.register('CLAIM.S', 'source://claim/s')
        self.auth.promote('CLAIM.S', '+', evidence=[{'kind': 'support', 'verified': True, 'ref': 'ev:s'}])
        enriched = self.auth.enrich_candidates([
            {'id': 'with-claim', 'claim_id': 'CLAIM.S'},
            {'id': 'without-claim'},
            {'id': 'unknown-claim', 'claim_id': 'CLAIM.MISSING'},
        ])
        self.assertEqual(enriched[0]['authority_state']['claim_id'], 'CLAIM.S')
        self.assertEqual(enriched[0]['authority_state']['y'], '+')
        self.assertEqual(enriched[0]['authority_state']['status'], 'ACTIVE')
        self.assertNotIn('authority_state', enriched[1])
        self.assertNotIn('authority_state', enriched[2])

    def test_benchmark_and_list_count_typed_states(self):
        self.auth.register('CLAIM.1', 'source://1')
        self.auth.register('CLAIM.2', 'source://2')
        self.auth.promote('CLAIM.2', '+', evidence=[{'kind': 'support', 'verified': True, 'ref': 'ev:2'}])
        bench = self.auth.benchmark()
        self.assertEqual(bench['authority_claims'], 2)
        self.assertEqual(bench['authority_unknown'], 1)
        self.assertEqual(bench['authority_supported'], 1)
        self.assertEqual(len(self.auth.list(y='+')), 1)


if __name__ == '__main__':
    unittest.main()

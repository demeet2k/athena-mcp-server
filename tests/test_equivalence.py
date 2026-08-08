import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_equivalence import EquivalenceLedger, REQUIRED_SAMENESS


SAME = {name: True for name in REQUIRED_SAMENESS}


class EquivalenceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        self.eq = EquivalenceLedger(self.core)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def witness(self, ref):
        return {'verified': True, 'ref': ref}

    def test_equivalent_requires_all_preservation_dimensions(self):
        incomplete = dict(SAME)
        incomplete['proof_route'] = False
        with self.assertRaises(ValueError):
            self.eq.observe('SX', 'a', 'b', 'EQUIVALENT', self.witness('eq:bad'), same=incomplete)
        with self.assertRaises(ValueError):
            self.eq.observe('SX', 'a', 'b', 'EQUIVALENT', {'verified': False, 'ref': 'eq:bad'}, same=SAME)

    def test_distinct_requires_explicit_difference(self):
        with self.assertRaises(ValueError):
            self.eq.observe('SX', 'a', 'b', 'DISTINCT', self.witness('d:bad'))
        out = self.eq.observe('SX', 'a', 'b', 'DISTINCT', self.witness('d:1'), different=['lineage'])
        self.assertEqual(out['relation'], 'DISTINCT')
        self.assertEqual(out['status'], 'ACTIVE')

    def test_transitive_equivalence_forms_one_collapse_safe_group(self):
        self.eq.observe('SX', 'a', 'b', 'EQUIVALENT', self.witness('eq:ab'), same=SAME)
        self.eq.observe('SX', 'b', 'c', 'EQUIVALENT', self.witness('eq:bc'), same=SAME)
        snap = self.eq.snapshot('SX', [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}, {'id': 'd'}])
        groups = {tuple(group['members']): group for group in snap['groups']}
        abc = groups[('a', 'b', 'c')]
        self.assertTrue(abc['collapse_allowed'])
        self.assertEqual(abc['representative'], 'a')
        self.assertEqual(abc['status'], 'EQUIVALENT')
        self.assertEqual(snap['suppressed'], ['b', 'c'])
        self.assertEqual(groups[('d',)]['status'], 'SINGLETON')

    def test_direct_conflicting_observation_blocks_collapse(self):
        self.eq.observe('SX', 'a', 'b', 'EQUIVALENT', self.witness('eq:ab'), same=SAME)
        conflict = self.eq.observe('SX', 'a', 'b', 'DISTINCT', self.witness('d:ab'), different=['carrier'])
        self.assertEqual(conflict['status'], 'CONFLICT')
        snap = self.eq.snapshot('SX', [{'id': 'a'}, {'id': 'b'}])
        self.assertEqual(len(snap['pair_conflicts']), 1)
        self.assertEqual(snap['suppressed'], [])
        self.assertTrue(all(not group['collapse_allowed'] for group in snap['groups']))
        self.assertTrue(all(group['status'] == 'PRESERVE_ALL_CONFLICT' for group in snap['groups']))

    def test_transitive_distinctness_conflict_preserves_entire_component(self):
        self.eq.observe('SX', 'a', 'b', 'EQUIVALENT', self.witness('eq:ab'), same=SAME)
        self.eq.observe('SX', 'b', 'c', 'EQUIVALENT', self.witness('eq:bc'), same=SAME)
        self.eq.observe('SX', 'a', 'c', 'DISTINCT', self.witness('d:ac'), different=['boundary'])
        snap = self.eq.snapshot('SX', [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}])
        self.assertEqual(len(snap['transitive_conflicts']), 1)
        self.assertEqual(snap['suppressed'], [])
        self.assertEqual(sorted(group['members'][0] for group in snap['groups']), ['a', 'b', 'c'])
        self.assertTrue(all(group['status'] == 'PRESERVE_ALL_CONFLICT' for group in snap['groups']))

    def test_conflict_resolution_requires_authority_and_restores_selected_relation(self):
        self.eq.observe('SX', 'a', 'b', 'EQUIVALENT', self.witness('eq:ab'), same=SAME)
        self.eq.observe('SX', 'a', 'b', 'DISTINCT', self.witness('d:ab'), different=['lineage'])
        with self.assertRaises(ValueError):
            self.eq.resolve_conflict('SX', 'a', 'b', 'DISTINCT', {'authorized': False, 'ref': 'bad'})
        resolved = self.eq.resolve_conflict('SX', 'a', 'b', 'DISTINCT', {'authorized': True, 'ref': 'resolver:eq'})
        self.assertEqual(resolved['status'], 'ACTIVE')
        self.assertEqual(resolved['relation'], 'DISTINCT')
        snap = self.eq.snapshot('SX', [{'id': 'a'}, {'id': 'b'}])
        self.assertEqual(snap['pair_conflicts'], [])
        self.assertEqual(snap['suppressed'], [])
        self.assertEqual(len(snap['distinct_edges']), 1)

    def test_contexts_are_isolated(self):
        self.eq.observe('SX.A', 'a', 'b', 'EQUIVALENT', self.witness('eq:a'), same=SAME)
        snap_a = self.eq.snapshot('SX.A', [{'id': 'a'}, {'id': 'b'}])
        snap_b = self.eq.snapshot('SX.B', [{'id': 'a'}, {'id': 'b'}])
        self.assertEqual(snap_a['suppressed'], ['b'])
        self.assertEqual(snap_b['suppressed'], [])

    def test_benchmark_counts_conflicts_and_events(self):
        self.eq.observe('SX', 'a', 'b', 'EQUIVALENT', self.witness('eq:ab'), same=SAME)
        self.eq.observe('SX', 'a', 'b', 'DISTINCT', self.witness('d:ab'), different=['failure_role'])
        bench = self.eq.benchmark()
        self.assertEqual(bench['equivalence_pairs'], 1)
        self.assertEqual(bench['equivalence_conflicts'], 1)
        self.assertEqual(bench['equivalence_events'], 2)


if __name__ == '__main__':
    unittest.main()

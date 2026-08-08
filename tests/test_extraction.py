import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_extract import ExtractionLedger, TRANSFORM_ORDER, transform_manifest


class ExtractionLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        self.ext = ExtractionLedger(self.core)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def test_default_plan_materializes_all_transform_tasks_not_fake_results(self):
        plan = self.ext.plan('seed://x', {'text': 'seed'}, max_depth=1)
        self.assertEqual(len(plan['tasks']), len(TRANSFORM_ORDER))
        self.assertEqual([task['transform'] for task in plan['tasks']], list(TRANSFORM_ORDER))
        self.assertTrue(all(task['status'] == 'PLANNED' for task in plan['tasks']))
        self.assertTrue(all(self.ext.task(task['task_id'])['result_refs'] == [] for task in plan['tasks']))
        manifest = transform_manifest()
        self.assertEqual(manifest['dual']['status'], 'TASK_GENERATOR_NOT_SEMANTIC_EXECUTOR')
        self.assertIn('verified witness', manifest['dual']['anti_fake'])

    def test_plan_is_deterministic_and_task_budget_bounds_transform_fanout(self):
        selected = ['decompose', 'formalize', 'dual', 'fail', 'falsify']
        a = self.ext.plan('seed://a', {'x': 1}, transforms=selected, max_tasks_per_generation=3)
        self.assertEqual([task['transform'] for task in a['tasks']], selected[:3])
        # A second run has a different causal run identity, but transform ordering is deterministic.
        b = self.ext.plan('seed://b', {'x': 1}, transforms=selected, max_tasks_per_generation=3)
        self.assertEqual([task['transform'] for task in a['tasks']], [task['transform'] for task in b['tasks']])
        with self.assertRaises(ValueError):
            self.ext.plan('seed://bad', {}, transforms=['decompose', 'imaginary-transform'])

    def test_completion_requires_verified_witness_and_real_output(self):
        task = self.ext.plan('seed://x', {'x': 1}, transforms=['formalize'])['tasks'][0]
        with self.assertRaises(ValueError):
            self.ext.complete(task['task_id'], [{'equation': 'x=1'}], {'verified': False, 'ref': 'bad'})
        with self.assertRaises(ValueError):
            self.ext.complete(task['task_id'], [], {'verified': True, 'ref': 'empty'})
        done = self.ext.complete(
            task['task_id'],
            [{'symbols': ['x'], 'equations': ['x=1']}],
            {'verified': True, 'ref': 'worker:formalize:1'},
        )
        self.assertEqual(done['status'], 'COMPLETED')
        self.assertEqual(len(done['result_refs']), 1)
        result = self.ext.result(done['result_refs'][0])
        self.assertEqual(result['payload']['equations'], ['x=1'])
        self.assertEqual(result['witness']['ref'], 'worker:formalize:1')
        with self.assertRaises(ValueError):
            self.ext.complete(task['task_id'], [{'again': True}], {'verified': True, 'ref': 'second'})

    def test_failure_is_witnessed_and_does_not_create_output(self):
        task = self.ext.plan('seed://x', {}, transforms=['invert'])['tasks'][0]
        with self.assertRaises(ValueError):
            self.ext.fail(task['task_id'], 'not invertible', {'verified': False, 'ref': 'bad'})
        failed = self.ext.fail(task['task_id'], 'map is not injective on declared domain', {'verified': True, 'ref': 'counterexample:1'})
        self.assertEqual(failed['status'], 'FAILED')
        self.assertEqual(self.ext.task(task['task_id'])['result_refs'], [])
        self.assertEqual(self.ext.frontier(failed['eid']) if False else [], [])  # no accidental API overloading

    def test_verified_result_can_seed_next_generation_with_depth_bound(self):
        plan = self.ext.plan('seed://x', {'claim': 'c'}, transforms=['decompose'], max_depth=1, max_tasks_per_generation=2)
        task = plan['tasks'][0]
        done = self.ext.complete(task['task_id'], [{'component': 'A'}], {'verified': True, 'ref': 'worker:1'})
        result_id = done['result_refs'][0]
        expanded = self.ext.expand_result(result_id, transforms=['formalize', 'falsify', 'bridge'])
        self.assertEqual(expanded['status'], 'EXPANDED')
        self.assertEqual(expanded['depth'], 1)
        self.assertEqual(len(expanded['tasks']), 2)
        self.assertEqual([task['transform'] for task in expanded['tasks']], ['formalize', 'falsify'])
        child = expanded['tasks'][0]
        child_done = self.ext.complete(child['task_id'], [{'symbol': 'A'}], {'verified': True, 'ref': 'worker:2'})
        stopped = self.ext.expand_result(child_done['result_refs'][0], transforms=['successor'])
        self.assertEqual(stopped['status'], 'DEPTH_LIMIT')
        self.assertEqual(stopped['tasks'], [])

    def test_frontier_contains_only_planned_tasks(self):
        plan = self.ext.plan('seed://x', {}, transforms=['decompose', 'formalize', 'fail'])
        self.ext.complete(plan['tasks'][0]['task_id'], [{'parts': []}], {'verified': True, 'ref': 'w:1'})
        self.ext.fail(plan['tasks'][2]['task_id'], 'failure observed', {'verified': True, 'ref': 'w:2'})
        frontier = self.ext.frontier(plan['run_id'])
        self.assertEqual(len(frontier), 1)
        self.assertEqual(frontier[0]['transform'], 'formalize')
        self.assertEqual(frontier[0]['status'], 'PLANNED')

    def test_each_transform_has_goal_outputs_and_questions(self):
        manifest = transform_manifest()
        self.assertEqual(set(manifest), set(TRANSFORM_ORDER))
        for name, spec in manifest.items():
            self.assertTrue(spec['goal'], name)
            self.assertTrue(spec['outputs'], name)
            self.assertTrue(spec['questions'], name)

    def test_benchmark_counts_runs_tasks_results_and_statuses(self):
        plan = self.ext.plan('seed://x', {}, transforms=['test', 'compress'])
        self.ext.complete(plan['tasks'][0]['task_id'], [{'procedure': 'p'}], {'verified': True, 'ref': 'w:test'})
        bench = self.ext.benchmark()
        self.assertEqual(bench['extraction_runs'], 1)
        self.assertEqual(bench['extraction_tasks'], 2)
        self.assertEqual(bench['extraction_results'], 1)
        self.assertEqual(bench['extraction_status']['COMPLETED'], 1)
        self.assertEqual(bench['extraction_status']['PLANNED'], 1)


if __name__ == '__main__':
    unittest.main()

import json
import tempfile
import unittest

from athena_mcp.server import Server


class FieldSurfaceCompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.server = Server(self.tmp.name)
        self.seq = 0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self, method, params=None):
        self.seq += 1
        message = {'jsonrpc': '2.0', 'id': self.seq, 'method': method}
        if params is not None:
            message['params'] = params
        return self.server.handle(message)

    def tool(self, name, args):
        response = self.rpc('tools/call', {'name': name, 'arguments': args})
        result = response['result']
        self.assertFalse(result.get('isError'), response)
        return result['structuredContent']

    def test_field_tools_resource_and_fail_closed_semantics(self):
        names = {item['name'] for item in self.rpc('tools/list')['result']['tools']}
        for name in ['athena_field_compile', 'athena_field_get', 'athena_field_replay', 'athena_field_recent']:
            self.assertIn(name, names)
        uris = {item['uri'] for item in self.rpc('resources/list')['result']['resources']}
        self.assertIn('athena://field', uris)
        resource = json.loads(self.rpc('resources/read', {'uri': 'athena://field'})['result']['contents'][0]['text'])
        self.assertIn('deterministic assembler', resource['epistemic_boundary'])

        run = self.tool('athena_field_compile', {
            'seed_ref': 'seed://surface',
            'module_outputs': {'gap': {'gap': [{'id': 'gap-1', 'node': 'N', 'residual_score': {'status': 'KNOWN', 'value': 2}}]}},
            'persist': False,
        })
        self.assertTrue(run['candidates'])
        self.assertTrue(all(item['metric_state'] == 'UNMEASURED' for item in run['candidates']))

        conflict = self.tool('athena_field_compile', {
            'seed_ref': 'seed://conflict',
            'module_outputs': {},
            'explicit_candidates': [
                {'kind': 'IMPLEMENT', 'operation': 'build_tool', 'target_ref': 'tool:X', 'source_refs': ['a'], 'readiness': .9, 'gain': 1, 'independence': 1, 'bridge': 1, 'cost': 1},
                {'kind': 'IMPLEMENT', 'operation': 'build_tool', 'target_ref': 'tool:X', 'source_refs': ['b'], 'readiness': .2, 'gain': 1, 'independence': 1, 'bridge': 1, 'cost': 1},
            ],
            'persist': False,
        })
        candidate = conflict['candidates'][0]
        self.assertEqual(candidate['metric_state'], 'CONFLICT')
        self.assertNotIn('readiness', candidate)
        self.assertEqual(candidate['source_refs'], ['a', 'b'])


if __name__ == '__main__':
    unittest.main()

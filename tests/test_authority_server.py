import json
import tempfile
import unittest

from athena_mcp.authority_server import AuthorityServer


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


class AuthorityServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.server = AuthorityServer(self.tmp.name)
        self.rpc_id = 0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self, method, params=None):
        self.rpc_id += 1
        message = {'jsonrpc': '2.0', 'id': self.rpc_id, 'method': method}
        if params is not None:
            message['params'] = params
        return self.server.handle(message)

    def tool(self, name, arguments):
        response = self.rpc('tools/call', {'name': name, 'arguments': arguments})
        self.assertFalse(response['result'].get('isError'), response)
        return response['result']['structuredContent']

    def _canonicalize(self, claim_id):
        self.tool('athena_claim_promote', {
            'claim_id': claim_id,
            'target_y': '+',
            'evidence': [{'kind': 'support', 'verified': True, 'ref': f'ev:{claim_id}'}],
        })
        self.tool('athena_claim_promote', {
            'claim_id': claim_id,
            'target_y': '!',
            'test': {
                'procedure': 'p',
                'observation': 'o',
                'result': 'r',
                'witness': {'verified': True, 'ref': f'test:{claim_id}'},
            },
        })
        self.tool('athena_claim_promote', {
            'claim_id': claim_id,
            'target_y': '#',
            'canonical_authority': {'authorized': True, 'ref': f'canon:{claim_id}'},
        })

    def test_tools_and_resources_compose_without_removing_mature_organs(self):
        tools = self.rpc('tools/list')['result']['tools']
        names = [tool['name'] for tool in tools]
        self.assertEqual(names, sorted(names))
        for required in [
            'athena_claim_register',
            'athena_claim_promote',
            'athena_claim_challenge',
            'athena_claim_resolve_canonical_challenge',
            'athena_orchestrate',
            'athena_orchestration_replay',
            'athena_branch_observe',
            'athena_apply_transform',
            'athena_apply_transform_route',
            'athena_finalize_output',
            'athena_verify_emission',
            'athena_crystallize_output',
            'athena_dense_navigate',
        ]:
            self.assertIn(required, names)

        resources = self.rpc('resources/list')['result']['resources']
        uris = {item['uri'] for item in resources}
        for uri in ['athena://authority', 'athena://branches', 'athena://transforms', 'athena://emissions', 'athena://orchestration/law']:
            self.assertIn(uri, uris)

    def test_mcp_authority_gate_changes_orchestration(self):
        self.tool('athena_claim_register', {'claim_id': 'CLAIM.MCP', 'source_ref': 'source://mcp'})
        candidate = {'id': 'work', 'claim_id': 'CLAIM.MCP', 'min_authority': '+', **BASE}

        blocked = self.tool('athena_orchestrate', {
            'seed': 's',
            'candidates': [candidate],
            'actor': 'A1',
            'task': 'blocked',
        })
        self.assertIsNone(blocked['next'])
        self.assertEqual(blocked['authority_plan'][0]['route'], 'gather_verified_support')

        self.tool('athena_claim_promote', {
            'claim_id': 'CLAIM.MCP',
            'target_y': '+',
            'evidence': [{'kind': 'support', 'verified': True, 'ref': 'ev:mcp'}],
        })
        allowed = self.tool('athena_orchestrate', {
            'seed': 's',
            'candidates': [candidate],
            'actor': 'A1',
            'task': 'allowed',
        })
        self.assertEqual(allowed['next']['id'], 'work')
        self.assertEqual(allowed['authority_snapshot']['work']['authority_state']['y'], '+')

    def test_canonical_challenge_blocks_and_historical_replay_survives_resolution(self):
        self.tool('athena_claim_register', {'claim_id': 'CLAIM.C', 'source_ref': 'source://c'})
        self._canonicalize('CLAIM.C')
        candidate = {'id': 'canonical-route', 'claim_id': 'CLAIM.C', 'min_authority': '#', **BASE}

        active = self.tool('athena_orchestrate', {
            'seed': 's', 'candidates': [candidate], 'actor': 'A1', 'task': 'active'
        })
        self.assertEqual(active['next']['id'], 'canonical-route')

        self.tool('athena_claim_challenge', {
            'claim_id': 'CLAIM.C',
            'witness': {'verified': True, 'ref': 'challenge:c'},
            'reason': 'contradictory result',
        })
        challenged = self.tool('athena_orchestrate', {
            'seed': 's', 'candidates': [candidate], 'actor': 'A1', 'task': 'challenged'
        })
        self.assertIsNone(challenged['next'])
        self.assertEqual(
            challenged['authority_snapshot']['canonical-route']['authority_state']['status'],
            'CANONICAL_CHALLENGED'
        )

        self.tool('athena_claim_resolve_canonical_challenge', {
            'claim_id': 'CLAIM.C',
            'decision': 'UPHOLD',
            'authority': {'authorized': True, 'ref': 'resolver:c'},
        })
        resolved = self.tool('athena_orchestrate', {
            'seed': 's', 'candidates': [candidate], 'actor': 'A1', 'task': 'resolved'
        })
        self.assertEqual(resolved['next']['id'], 'canonical-route')

        replay_active = self.tool('athena_orchestration_replay', {'run_id': active['run_id']})
        replay_challenged = self.tool('athena_orchestration_replay', {'run_id': challenged['run_id']})
        self.assertTrue(replay_active['match'])
        self.assertTrue(replay_challenged['match'])
        self.assertEqual(replay_active['stored_next'], 'canonical-route')
        self.assertIsNone(replay_challenged['stored_next'])
        self.assertEqual(
            replay_challenged['stored_authority_snapshot']['canonical-route']['authority_state']['status'],
            'CANONICAL_CHALLENGED'
        )

    def test_authority_resource_and_benchmark_are_live(self):
        self.tool('athena_claim_register', {'claim_id': 'CLAIM.R', 'source_ref': 'source://r'})
        resource = self.rpc('resources/read', {'uri': 'athena://authority'})
        payload = json.loads(resource['result']['contents'][0]['text'])
        self.assertEqual(payload['benchmark']['authority_claims'], 1)
        self.assertEqual(payload['claims'][0]['claim_id'], 'CLAIM.R')
        benchmark = self.tool('athena_benchmark', {})
        self.assertEqual(benchmark['authority_claims'], 1)
        self.assertIn('branches', benchmark)
        self.assertIn('orchestration_runs', benchmark)

    def test_maxdev_prompt_contains_authority_law(self):
        prompt = self.rpc('prompts/get', {
            'name': 'athena_maxdev',
            'arguments': {'agent': 'A1', 'task': 'test'},
        })
        text = prompt['result']['messages'][0]['content']['text']
        self.assertIn('14 AUTHORITY:', text)
        self.assertIn('?->+', text)
        self.assertIn('CANONICAL_CHALLENGED', text)


if __name__ == '__main__':
    unittest.main()

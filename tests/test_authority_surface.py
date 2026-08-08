import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.validate import validate
from athena_mcp.orchestration_authority import AuthorityLedger
from athena_mcp.orchestration_authority_protocol import AUTHORITY_RESOURCE, AUTHORITY_TOOLS, authority_candidate_schema_fragment
from athena_mcp.orchestration_authority_surface import AUTHORITY_TOOL_NAMES, authority_resource_value, call_authority_tool


class AuthoritySurfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db')
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        self.ledger = AuthorityLedger(self.core)
        self.tools = {tool['name']: tool for tool in AUTHORITY_TOOLS}

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    def test_protocol_and_dispatch_names_are_identical(self):
        self.assertEqual(set(self.tools), AUTHORITY_TOOL_NAMES)
        self.assertEqual(AUTHORITY_RESOURCE['uri'], 'athena://authority')
        fragment = authority_candidate_schema_fragment()
        self.assertIn('claim_id', fragment)
        self.assertEqual(fragment['min_authority']['enum'], ['?', '+', '!', '#'])

    def test_schema_rejects_unverified_evidence_before_dispatch(self):
        promote = self.tools['athena_claim_promote']['inputSchema']
        with self.assertRaises(ValueError):
            validate(promote, {
                'claim_id': 'C',
                'target_y': '+',
                'evidence': [{'kind': 'support', 'verified': False, 'ref': 'bad'}],
            })

    def test_full_surface_flow(self):
        register = {'claim_id': 'CLAIM.UI', 'source_ref': 'source://ui', 'actor': 'A1'}
        validate(self.tools['athena_claim_register']['inputSchema'], register)
        created = call_authority_tool(self.ledger, 'athena_claim_register', register)
        self.assertEqual(created['claim']['y'], '?')

        promote_support = {
            'claim_id': 'CLAIM.UI',
            'target_y': '+',
            'evidence': [{'kind': 'support', 'verified': True, 'ref': 'ev:ui'}],
        }
        validate(self.tools['athena_claim_promote']['inputSchema'], promote_support)
        supported = call_authority_tool(self.ledger, 'athena_claim_promote', promote_support)
        self.assertEqual(supported['claim']['y'], '+')

        promote_execution = {
            'claim_id': 'CLAIM.UI',
            'target_y': '!',
            'test': {
                'procedure': 'p',
                'observation': 'o',
                'result': 'r',
                'witness': {'verified': True, 'ref': 'test:ui'},
            },
        }
        validate(self.tools['athena_claim_promote']['inputSchema'], promote_execution)
        executed = call_authority_tool(self.ledger, 'athena_claim_promote', promote_execution)
        self.assertEqual(executed['claim']['y'], '!')

        promote_canonical = {
            'claim_id': 'CLAIM.UI',
            'target_y': '#',
            'canonical_authority': {'authorized': True, 'ref': 'canon:ui'},
        }
        validate(self.tools['athena_claim_promote']['inputSchema'], promote_canonical)
        canonical = call_authority_tool(self.ledger, 'athena_claim_promote', promote_canonical)
        self.assertEqual(canonical['claim']['y'], '#')

        challenge = {
            'claim_id': 'CLAIM.UI',
            'witness': {'verified': True, 'ref': 'challenge:ui'},
            'reason': 'new contradiction',
        }
        validate(self.tools['athena_claim_challenge']['inputSchema'], challenge)
        challenged = call_authority_tool(self.ledger, 'athena_claim_challenge', challenge)
        self.assertEqual(challenged['claim']['status'], 'CANONICAL_CHALLENGED')

        resolve = {
            'claim_id': 'CLAIM.UI',
            'decision': 'UPHOLD',
            'authority': {'authorized': True, 'ref': 'resolver:ui'},
        }
        validate(self.tools['athena_claim_resolve_canonical_challenge']['inputSchema'], resolve)
        upheld = call_authority_tool(self.ledger, 'athena_claim_resolve_canonical_challenge', resolve)
        self.assertEqual(upheld['claim']['y'], '#')
        self.assertEqual(upheld['claim']['status'], 'ACTIVE')

        state = call_authority_tool(self.ledger, 'athena_claim_state', {'claim_id': 'CLAIM.UI'})
        self.assertEqual(state['canonical_ref'], 'resolver:ui')
        listed = call_authority_tool(self.ledger, 'athena_claim_list', {'y': '#', 'limit': 10})
        self.assertEqual(len(listed), 1)
        resource = authority_resource_value(self.ledger)
        self.assertEqual(resource['benchmark']['authority_canonical'], 1)
        self.assertEqual(resource['claims'][0]['claim_id'], 'CLAIM.UI')

    def test_missing_claim_state_is_explicit(self):
        missing = call_authority_tool(self.ledger, 'athena_claim_state', {'claim_id': 'NONE'})
        self.assertEqual(missing, {'found': False, 'claim_id': 'NONE'})


if __name__ == '__main__':
    unittest.main()

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from athena_mcp.wiki_git_review import WikiGitReview
from tests import test_wiki_git_draft as fixtures


class ReviewTests(unittest.TestCase):
    setUp = fixtures.DraftTests.setUp
    tearDown = fixtures.DraftTests.tearDown
    git = fixtures.DraftTests.git
    fake_compile = fixtures.DraftTests.fake_compile
    stage = fixtures.DraftTests.stage

    def read(self, draft, **options):
        # Deliberately omit a store: the draft must be self-contained in Git.
        return WikiGitReview(SimpleNamespace(git=self.server.git)).review(
            action='READ', ref=draft['ref'], expected_commit=draft['commit'], **options)

    def test_read_after_head_advances_without_database_or_repository_execution(self):
        draft = self.stage()
        self.git('commit', '--allow-empty', '-qm', 'A later independent checkpoint')
        before = self.server.git.status()
        with patch('athena_mcp.wiki_git.GitWikiCompiler.compile', side_effect=AssertionError('No repository execution')):
            result = self.read(draft, include_source=True)
        self.assertEqual(result['standing'], 'VERIFIED_DRAFT_BYTES')
        self.assertEqual(result['binding']['base'], self.head)
        self.assertNotEqual(result['configured_head'], self.head)
        self.assertEqual(result['source_carrier']['document']['source_text'], 'Exact source\r\nwith uncertainty Ω')
        self.assertEqual(result['original_claim_labels'], ['UNK'])
        self.assertEqual(result['semantic_lint'], 'NOT_RUN')
        self.assertFalse(result['producer_authenticated'])
        self.assertFalse(result['mutation_applied'])
        self.assertEqual(self.server.git.status(), before)
        self.assertEqual(self.git('diff', '--cached'), '')

    def test_inventory_is_paginated_and_does_not_call_foreign_ref_verified(self):
        self.git('update-ref', 'refs/heads/codex/wiki-draft-' + '1' * 32, self.head)
        self.git('update-ref', 'refs/heads/codex/wiki-draft-' + '2' * 32, self.head)
        reader = WikiGitReview(self.server)
        first = reader.review(action='LIST', limit=1)
        second = reader.review(action='LIST', limit=1, offset=first['next_offset'])
        self.assertTrue(first['truncated'])
        self.assertFalse(second['truncated'])
        self.assertNotEqual(first['drafts'][0]['ref'], second['drafts'][0]['ref'])
        self.assertFalse(first['drafts'][0]['verified'])
        with self.assertRaisesRegex(ValueError, 'DRAFT_BINDING_REQUIRED'):
            reader.review(action='READ', ref=first['drafts'][0]['ref'], expected_commit=self.head)

    def test_stale_and_symbolic_refs_fail_without_writes(self):
        draft = self.stage()
        with self.assertRaisesRegex(ValueError, 'STALE_REF'):
            self.read({**draft, 'commit': self.head})
        alias = 'refs/heads/codex/wiki-draft-' + 'f' * 32
        self.git('symbolic-ref', alias, draft['ref'])
        with self.assertRaisesRegex(ValueError, 'SYMBOLIC_REF_FORBIDDEN'):
            self.read({**draft, 'ref': alias})
        self.assertEqual(self.git('rev-parse', draft['ref']).strip(), draft['commit'])

    def amend(self, draft, path):
        self.git('checkout', '--detach', draft['commit'])
        target = self.server.git.root / path
        target.write_bytes(target.read_bytes() + b'\nUnexpected change\n' if target.exists() else b'Outside the Wiki\n')
        self.git('add', '--', path)
        self.git('commit', '--amend', '--no-edit', '--quiet')
        changed = self.git('rev-parse', 'HEAD').strip()
        self.git('update-ref', draft['ref'], changed, draft['commit'])
        return {**draft, 'commit': changed}

    def test_changed_wiki_bytes_cannot_reuse_the_original_binding(self):
        draft = self.amend(self.stage(), 'knowledge/wiki/log.md')
        with self.assertRaisesRegex(ValueError, 'PLAN_DIGEST_MISMATCH'):
            self.read(draft)

    def test_non_wiki_changes_cannot_hide_behind_a_valid_carrier(self):
        draft = self.amend(self.stage(), 'outside.txt')
        with self.assertRaisesRegex(ValueError, 'UNEXPECTED_CHANGED_PATHS'):
            self.read(draft)

    def test_replacement_objects_do_not_change_the_committed_observation(self):
        draft = self.stage()
        self.git('replace', draft['commit'], self.head)
        result = self.read(draft)
        self.assertEqual(result['commit'], draft['commit'])
        self.assertEqual(result['binding']['base'], self.head)
        self.assertFalse(result['source_included'])
        self.assertNotIn('source_carrier', result)

    def test_surface_dispatch_and_argument_boundaries(self):
        from athena_mcp.protocol import TOOLS
        tool = next(t for t in TOOLS if t['name'] == 'athena_wiki_git_review')
        self.assertTrue(tool['annotations']['readOnlyHint'])
        with patch.object(WikiGitReview, 'review', return_value={'standing': 'fixture'}) as read:
            self.assertEqual(self.server.call_tool(tool['name'], {'action': 'LIST'}), {'standing': 'fixture'})
            read.assert_called_once_with(action='LIST')
        for args in ({'action': 'READ'}, {'action': 'LIST', 'include_source': True},
                     {'action': 'LIST', 'limit': True}, {'action': 'LIST', 'offset': -1}):
            with self.assertRaises(ValueError):
                WikiGitReview(self.server).review(**args)


if __name__ == '__main__':
    unittest.main()

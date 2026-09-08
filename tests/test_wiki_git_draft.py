import json
from unittest.mock import patch
import unittest

from athena_mcp.wiki_git_draft import WikiGitDraft
from athena_mcp.wiki_git_ingest import WikiGitIngest
from tests import test_wiki_git_ingest as fixtures


class DraftTests(unittest.TestCase):
    # Reuse the independent fixture, not its test methods. Semantic compiler
    # integration is separately exercised in the private paired workflow.
    setUp = fixtures.IngestTests.setUp
    tearDown = fixtures.IngestTests.tearDown
    git = fixtures.IngestTests.git

    def fake_compile(self, *, expected_git_head, request):
        if expected_git_head != self.head:
            self.assertEqual(request['operation'], 'LINT')
            self.assertEqual(len(request['pages']), 2)
            return {'standing': 'COMPLETE', 'wiki_standing': 'READY',
                    'mutation_applied': False, 'git_head': expected_git_head}
        return fixtures.IngestTests.fake_compile(self, expected_git_head=expected_git_head, request=request)

    def stage(self, **overrides):
        with patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile', side_effect=self.fake_compile):
            proposal = WikiGitIngest(self.server).compile(**self.arguments)
            return WikiGitDraft(self.server).stage(**self.arguments,
                **{'expected_plan_sha256': proposal['plan_sha256'], **overrides})

    def refs(self):
        return self.git('for-each-ref', '--format=%(refname)', 'refs/heads/codex/wiki-draft-*')

    def test_durable_draft_preserves_source_checkout_and_exact_carrier(self):
        before = self.server.git.status()
        result = self.stage()
        self.assertEqual(result['standing'], 'READY_LOCAL_DRAFT')
        self.assertEqual(self.server.git.status(), before)
        self.assertEqual(self.git('rev-parse', result['ref']).strip(), result['commit'])
        carrier = json.loads(self.git('show', result['commit'] + ':knowledge/raw/drive/' + self.doc + '.json'))
        self.assertEqual(carrier['document']['source_text'], 'Exact source\r\nwith uncertainty Ω')
        self.assertEqual(carrier['records']['claims'][0]['EPI'], 'UNK')
        self.assertFalse(result['shared_state_applied'])
        self.assertFalse(result['pushed'])
        self.assertTrue(result['source_checkout_unchanged'])
        self.assertEqual(self.git('diff', '--cached').strip(), '')

    def test_retry_reuses_the_verified_commit(self):
        first = self.stage()
        second = self.stage()
        self.assertEqual(first['commit'], second['commit'])
        self.assertEqual(first['ref'], second['ref'])
        self.assertFalse(first['reused'])
        self.assertTrue(second['reused'])

    def test_reviewed_plan_mismatch_cannot_create_ref(self):
        with self.assertRaisesRegex(ValueError, 'REVIEWED_PLAN_CHANGED'):
            self.stage(expected_plan_sha256='0' * 64)
        self.assertEqual(self.refs(), '')

    def test_composed_tool_requires_review_digest_and_declares_local_mutation(self):
        from athena_mcp.protocol import TOOLS
        from athena_mcp import unified_manifest
        tools = [tool for tool in TOOLS if tool['name'] == 'athena_wiki_git_stage']
        self.assertEqual(len(tools), 1)
        self.assertFalse(tools[0]['annotations']['readOnlyHint'])
        self.assertTrue(tools[0]['annotations']['idempotentHint'])
        with self.assertRaises(ValueError):
            self.server.call_tool('athena_wiki_git_stage', self.arguments)
        organ = unified_manifest.build_unified_manifest(self.server)['organs']['git_wiki']
        self.assertTrue(organ['mutation_apply'])
        self.assertEqual(organ['mutation_scope'], 'LOCAL_DRAFT_REF_ONLY')
        self.assertFalse(organ['shared_branch_apply'])
        with patch('athena_mcp.wiki_git_draft.WikiGitDraft.stage', return_value={'standing': 'fixture'}) as stage:
            arguments = {**self.arguments, 'expected_plan_sha256': 'a' * 64}
            self.assertEqual(self.server.call_tool('athena_wiki_git_stage', arguments), {'standing': 'fixture'})
            stage.assert_called_once_with(**arguments)

    def test_committed_lint_hold_cannot_publish_ref(self):
        original = self.fake_compile
        def compile(**kwargs):
            if kwargs['expected_git_head'] != self.head:
                return {'standing': 'HOLD', 'wiki_standing': 'HOLD'}
            return original(**kwargs)
        with patch.object(self, 'fake_compile', side_effect=compile):
            with self.assertRaisesRegex(ValueError, 'COMMITTED_LINT_NOT_READY'):
                self.stage()
        self.assertEqual(self.refs(), '')
        self.assertFalse(self.server.git.status()['dirty'])

    def test_foreign_ref_is_never_overwritten(self):
        first = self.stage()
        self.git('update-ref', first['ref'], self.head, first['commit'])
        with self.assertRaisesRegex(ValueError, 'REF_PARENT_MISMATCH'):
            self.stage()
        self.assertEqual(self.git('rev-parse', first['ref']).strip(), self.head)

    def test_concurrent_source_change_preserves_that_change_and_publishes_nothing(self):
        original = self.fake_compile
        def compile(**kwargs):
            result = original(**kwargs)
            if kwargs['expected_git_head'] != self.head:
                self.git('commit', '--allow-empty', '-qm', 'Independent concurrent work')
            return result
        with patch.object(self, 'fake_compile', side_effect=compile):
            with self.assertRaisesRegex(ValueError, 'SOURCE_CHANGED_BEFORE_PUBLICATION'):
                self.stage()
        self.assertNotEqual(self.git('rev-parse', 'HEAD').strip(), self.head)
        self.assertEqual(self.refs(), '')

    def test_ref_race_does_not_replace_the_winning_writer(self):
        from athena_mcp import wiki_git_draft
        original = wiki_git_draft._git
        raced = []
        def git(root, *args, **kwargs):
            if args[:2] == ('update-ref', '--no-deref'):
                ref = args[2]
                self.git('update-ref', ref, self.head)
                raced.append(ref)
            return original(root, *args, **kwargs)
        with patch.object(wiki_git_draft, '_git', side_effect=git):
            with self.assertRaisesRegex(ValueError, 'WIKI_DRAFT_GIT_FAILED'):
                self.stage()
        self.assertEqual(len(raced), 1)
        self.assertEqual(self.git('rev-parse', raced[0]).strip(), self.head)


if __name__ == '__main__':
    unittest.main()

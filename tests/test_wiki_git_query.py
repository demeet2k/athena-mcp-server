import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from athena_mcp.server import Server
from athena_mcp.wiki_git import canonical
from athena_mcp.wiki_git_query import WikiGitQuery
from athena_mcp.wiki_git_snapshot import sha
from tests.test_wiki_git_ingest import scaffold, page_text


class CommittedWikiQueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.files = scaffold()
        self.files.update({'knowledge/wiki/sources/first.md': page_text('first'),
                           'knowledge/wiki/sources/second.md': page_text('second'),
                           'knowledge/raw/source.bin': b'\x00\xff\r\n'})
        self.claims = [{'claim_id': 'first', 'statement': 'Old hypothesis', 'epistemic_status': 'HYP'},
                       {'claim_id': 'second', 'statement': 'Benefit remains unknown', 'epistemic_status': 'UNK'}]
        self.files['knowledge/wiki/_meta/claims.jsonl'] = ''.join(json.dumps(c)+'\n' for c in self.claims)
        self.sources = [{'source_id': 'source', 'raw_path': 'knowledge/raw/source.bin',
                         'content_sha256': sha(self.files['knowledge/raw/source.bin'])}]
        self.files['knowledge/wiki/_meta/sources.jsonl'] = json.dumps(self.sources[0])+'\n'
        self.contradictions = [{'claim_ids': ['first', 'second'], 'state': 'OPEN'}]
        self.files['knowledge/wiki/_meta/contradictions.jsonl'] = json.dumps(self.contradictions[0])+'\n'
        for path, value in self.files.items():
            self.write(path, value)
        self.write('untrusted_data_commit.py', 'raise RuntimeError("DATA_CODE_MUST_NOT_RUN")\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'historical data')
        self.data_head = self.git('rev-parse', 'HEAD').strip()
        self.git('rm', '-rq', 'knowledge', 'untrusted_data_commit.py')
        self.write('trusted.txt', 'Configured compiler checkout\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'configured compiler')
        self.head = self.git('rev-parse', 'HEAD').strip()
        self.server = Server(str(Path(self.tmp.name)/'db.sqlite'), git_root=str(self.root))
        self.args = dict(expected_git_head=self.head, wiki_commit=self.data_head, query='benefit')

    def tearDown(self):
        self.server.store.close()
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args],
                                       text=True, encoding='utf-8', stderr=subprocess.DEVNULL)

    def write(self, path, value):
        target = self.root/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value if isinstance(value, bytes) else value.encode('utf-8'))

    def compile(self, *, expected_git_head, request):
        self.assertEqual(expected_git_head, self.head)
        self.assertEqual(self.git('rev-parse', 'HEAD').strip(), self.head)
        self.assertFalse((self.root/'knowledge').exists())
        self.assertFalse((self.root/'untrusted_data_commit.py').exists())
        self.assertEqual(request['operation'], 'QUERY')
        self.assertEqual({p['page_id'] for p in request['pages']}, {'first', 'second'})
        self.assertEqual(request['claims'], self.claims)
        self.assertEqual(request['sources'], self.sources)
        self.assertEqual(request['contradictions'], self.contradictions)
        return {'standing': 'COMPLETE', 'wiki_standing': 'REVIEW',
                'request_sha256': hashlib.sha256(canonical(request)).hexdigest(),
                'execution_receipt': {'outputs': [{'result': {'standing': 'REVIEW'}}]}}

    def invoke(self, **changes):
        return self.server.call_tool('athena_wiki_git_query', {**self.args, **changes})

    def changed_data(self, path, value):
        self.git('checkout', '-q', '--detach', self.data_head)
        self.write(path, value)
        self.git('add', '.')
        self.git('commit', '-qm', 'changed data')
        head = self.git('rev-parse', 'HEAD').strip()
        self.git('checkout', '-q', '--detach', self.head)
        return head

    def test_complete_historical_snapshot_bound_without_checkout_or_database_import(self):
        before = self.git('for-each-ref', '--format=%(refname) %(objectname)')
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile', side_effect=self.compile):
            result = self.invoke()
        self.assertEqual(result['wiki_commit'], self.data_head)
        self.assertEqual(result['compiler_commit'], self.head)
        self.assertEqual(result['readset'], {p: sha(b) for p, b in self.files.items()})
        self.assertEqual(result['readset_sha256'], hashlib.sha256(canonical(result['readset'])).hexdigest())
        self.assertEqual(result['snapshot_counts'], dict(pages=2, claims=2, sources=1, contradictions=1))
        self.assertEqual(result['wiki_standing'], 'REVIEW')
        self.assertEqual(before, self.git('for-each-ref', '--format=%(refname) %(objectname)'))
        self.assertEqual(self.git('status', '--porcelain'), '')
        tables = {r[0] for r in self.server.store.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table in ('wiki_documents_v1', 'wiki_snapshots_v1'):
            if table in tables:
                self.assertEqual(self.server.store.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0], 0)

    def test_missing_wiki_is_not_silently_an_empty_snapshot(self):
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile') as compiler:
            with self.assertRaisesRegex(ValueError, 'MALFORMED_COMMITTED_WIKI'):
                self.invoke(wiki_commit=self.head)
            compiler.assert_not_called()

    def test_untyped_page_or_changed_raw_source_fails_before_execution(self):
        for path, content, error in [('knowledge/wiki/sources/hidden.md', '# untyped', 'METADATA_REQUIRED'),
                                     ('knowledge/raw/source.bin', b'changed', 'RAW_CARRIER_MISMATCH')]:
            head = self.changed_data(path, content)
            with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile') as compiler:
                with self.assertRaisesRegex(ValueError, error):
                    self.invoke(wiki_commit=head)
                compiler.assert_not_called()

    def test_replacement_objects_cannot_substitute_the_data_commit(self):
        self.git('replace', self.data_head, self.head)
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile', side_effect=self.compile):
            result = self.invoke()
        self.assertEqual(result['readset'], {p: sha(b) for p, b in self.files.items()})

    def test_blob_oid_is_not_a_commit(self):
        blob = self.git('rev-parse', 'HEAD:trusted.txt').strip()
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile') as compiler:
            with self.assertRaisesRegex(ValueError, 'DATA_COMMIT_REQUIRED'):
                self.invoke(wiki_commit=blob)
            compiler.assert_not_called()

    def test_stale_and_dirty_configured_checkout_stop_before_execution(self):
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile') as compiler:
            with self.assertRaisesRegex(ValueError, 'CLEAN_EXPECTED_HEAD_REQUIRED'):
                self.invoke(expected_git_head=self.data_head)
            self.write('dirty.txt', 'not committed')
            with self.assertRaisesRegex(ValueError, 'CLEAN_EXPECTED_HEAD_REQUIRED'):
                self.invoke()
            compiler.assert_not_called()

    def test_state_drift_during_query_is_rejected(self):
        def drift(**args):
            result = self.compile(**args)
            self.write('external.txt', 'concurrent change')
            return result
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile', side_effect=drift):
            with self.assertRaisesRegex(ValueError, 'CONFIGURED_STATE_CHANGED'):
                self.invoke()

    def test_hold_is_preserved_without_promoting_execution_or_truth(self):
        receipt = {'standing': 'HOLD', 'wiki_standing': 'NOT_EXECUTED', 'execution_receipt': {'holds': ['source mismatch']}}
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile', return_value=receipt):
            result = self.invoke()
        self.assertEqual(result['standing'], 'HOLD')
        self.assertEqual(result['compiler_receipt'], receipt)
        for field in ('mutation_applied', 'data_checkout_materialized', 'producer_authenticated'):
            self.assertIs(result[field], False)
        self.assertEqual(result['behavioral_gain'], 'UNKNOWN')

    def test_callers_cannot_supply_evidence_code_paths_or_unbounded_queries(self):
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile') as compiler:
            for change in ({'pages': []}, {'claims': []}, {'wiki': {}}, {'module': 'other'},
                           {'query': ''}, {'query': '   '}, {'query': 'x'*4097},
                           {'limit': True}, {'limit': 0}, {'limit': 51},
                           {'wiki_commit': 'HEAD'}, {'expected_git_head': '--help'}):
                with self.subTest(change=change), self.assertRaises(ValueError):
                    self.invoke(**change)
            compiler.assert_not_called()


if __name__ == '__main__':
    unittest.main()

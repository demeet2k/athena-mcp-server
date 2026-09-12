import base64
import hashlib
import json
import unittest
from unittest.mock import patch

from athena_mcp.wiki_git import canonical
from athena_mcp.wiki_git_snapshot import sha
from tests import test_wiki_git_query as _fixture


class CommittedWikiSourceTests(unittest.TestCase):
    setUp = _fixture.CommittedWikiQueryTests.setUp
    tearDown = _fixture.CommittedWikiQueryTests.tearDown
    git = _fixture.CommittedWikiQueryTests.git
    write = _fixture.CommittedWikiQueryTests.write
    changed_data = _fixture.CommittedWikiQueryTests.changed_data

    def invoke(self, **changes):
        args = dict(wiki_commit=self.data_head, source_id='source',
                    expected_content_sha256=self.sources[0]['content_sha256'])
        return self.server.call_tool('athena_wiki_git_source', {**args, **changes})

    def test_binary_source_without_checkout_draft_database_or_compiler(self):
        before = (self.git('status', '--porcelain'), self.git('show-ref'))
        with patch('athena_mcp.wiki_git_query.GitWikiCompiler.compile') as compiler:
            result = self.invoke()
            compiler.assert_not_called()
        self.assertEqual(result['content_encoding'], 'base64')
        self.assertEqual(base64.b64decode(result['content']), b'\x00\xff\r\n')
        self.assertEqual(result['content_bytes'], 4)
        self.assertEqual(result['content_sha256'], sha(b'\x00\xff\r\n'))
        self.assertEqual(result['source'], self.sources[0])
        self.assertEqual(result['wiki_commit'], self.data_head)
        self.assertEqual(result['wiki_tree'], self.git('rev-parse', self.data_head+'^{tree}').strip())
        self.assertEqual(result['readset'], {p:sha(v) for p,v in self.files.items()})
        self.assertEqual(result['readset_sha256'], hashlib.sha256(canonical(result['readset'])).hexdigest())
        self.assertEqual(before, (self.git('status', '--porcelain'), self.git('show-ref')))
        self.assertFalse((self.root/'knowledge').exists())
        self.assertFalse((self.root/'untrusted_data_commit.py').exists())
        for field in ('repository_code_executed','data_checkout_materialized','mutation_applied',
                      'database_imported','draft_binding_verified','producer_authenticated'):
            self.assertIs(result[field], False)
        for table in ('wiki_documents_v1', 'wiki_snapshots_v1'):
            if self.server.store.db.execute("SELECT name FROM sqlite_master WHERE name=?",(table,)).fetchone():
                self.assertEqual(self.server.store.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0],0)

    def test_utf8_crlf_and_uncertainty_are_exact(self):
        self.git('checkout','-q','--detach',self.data_head)
        text = 'Source EPI=UNK\r\n\u03a9, \U0001f30d\n'
        self.write('knowledge/raw/source.bin',text)
        source = {**self.sources[0], 'content_sha256':sha(text)}
        self.write('knowledge/wiki/_meta/sources.jsonl',json.dumps(source)+'\n')
        self.git('add','.');self.git('commit','-qm','text carrier')
        commit=self.git('rev-parse','HEAD').strip()
        self.git('checkout','-q','--detach',self.head)
        result=self.invoke(wiki_commit=commit,expected_content_sha256=sha(text))
        self.assertEqual(result['content_encoding'],'utf-8')
        self.assertEqual(result['content'],text)
        self.assertEqual(result['content_bytes'],len(text.encode('utf-8')))

    def test_dirty_current_checkout_and_replacement_cannot_substitute_committed_source(self):
        self.write('knowledge/raw/source.bin',b'working tree substitute')
        self.git('replace',self.data_head,self.head)
        before=self.git('status','--porcelain')
        result=self.invoke()
        self.assertEqual(base64.b64decode(result['content']),b'\x00\xff\r\n')
        self.assertEqual(self.git('status','--porcelain'),before)

    def test_missing_source_and_mismatched_citation_fail(self):
        for changes,error in [({'source_id':'absent'},'SOURCE_NOT_FOUND'),
                              ({'expected_content_sha256':'sha256:'+'0'*64},'CITATION_DIGEST_MISMATCH')]:
            with self.subTest(changes=changes),self.assertRaisesRegex(ValueError,error):
                self.invoke(**changes)

    def test_duplicate_source_identity_and_tampered_raw_fail(self):
        for path,value,error in [('knowledge/wiki/_meta/sources.jsonl',(json.dumps(self.sources[0])+'\n')*2,'AMBIGUOUS_SOURCE_IDENTITIES'),
                                 ('knowledge/raw/source.bin',b'forged','RAW_CARRIER_MISMATCH'),
                                 ('knowledge/wiki/sources/hidden.md','# untyped','METADATA_REQUIRED')]:
            commit=self.changed_data(path,value)
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,error):
                self.invoke(wiki_commit=commit)

    def test_noncommit_or_missing_snapshot_fails(self):
        blob=self.git('rev-parse','HEAD:trusted.txt').strip()
        for commit,error in [(blob,'DATA_COMMIT_REQUIRED'),(self.head,'MALFORMED_COMMITTED_WIKI')]:
            with self.subTest(commit=commit),self.assertRaisesRegex(ValueError,error):
                self.invoke(wiki_commit=commit)

    def test_response_bound_does_not_truncate_content(self):
        with patch('athena_mcp.wiki_git_source.MAX_RESPONSE_BYTES',16):
            with self.assertRaisesRegex(ValueError,'RESPONSE_TOO_LARGE'):
                self.invoke()

    def test_no_caller_path_evidence_or_unbounded_identity(self):
        for change in ({'raw_path':'../../secret'},{'sources':[]},{'module':'malicious'},
                       {'wiki_commit':'HEAD'},{'source_id':''},{'source_id':' '},
                       {'source_id':'x'*513},{'expected_content_sha256':'0'*64}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.invoke(**change)


if __name__=='__main__':
    unittest.main()

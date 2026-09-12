import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from athena_mcp.server import Server
from athena_mcp.wiki_memory import digest
from athena_mcp.wiki_git_ingest import WikiGitIngest
from athena_mcp.wiki_git_snapshot import decode_snapshot, parse_page, read_snapshot, sha, simulate
from tests.test_wiki_memory import fixture


def scaffold():
    schema={'schema':'ATHENA.INTERNAL.WIKI.SCHEMA.V1','version':'1.0.0','name':'Fixture Wiki','domain':'Tests',
            'layers':{'raw':{'path':'knowledge/raw'},'wiki':{'path':'knowledge/wiki'},'schema':{'path':'knowledge/WIKI.schema.json'}},
            'page_types':{'source':'sources','concept':'concepts'},
            'special_files':{'index':'knowledge/wiki/index.md','log':'knowledge/wiki/log.md','sources':'knowledge/wiki/_meta/sources.jsonl','claims':'knowledge/wiki/_meta/claims.jsonl','contradictions':'knowledge/wiki/_meta/contradictions.jsonl'}}
    return {'knowledge/WIKI.schema.json':json.dumps(schema), 'knowledge/wiki/index.md':'# Fixture index\n',
            'knowledge/wiki/log.md':'# Fixture log\n', 'knowledge/wiki/_meta/sources.jsonl':'',
            'knowledge/wiki/_meta/claims.jsonl':'','knowledge/wiki/_meta/contradictions.jsonl':''}


def page_text(page_id='page.existing',title='Existing \\[title\\]'):
    metadata=dict(page_id=page_id,page_type='source',created_at='2026-09-08T12:00:00Z',updated_at='2026-09-08T12:00:00Z',source_ids=[],claim_ids=[],tags=[],links=[])
    return '<!-- ATHENA-WIKI-META\n'+json.dumps(metadata)+'\n-->\n\n# '+title+'\n\nFixture summary\n'


class SnapshotTests(unittest.TestCase):
    def test_unknown_page_cannot_silently_disappear_from_reindex(self):
        files=scaffold();files['knowledge/wiki/sources/untyped.md']='# No metadata'
        with self.assertRaisesRegex(ValueError,'METADATA_REQUIRED'): decode_snapshot(files)

    def test_metadata_parser_retains_identity_and_reverses_title_escaping(self):
        row=parse_page('knowledge/wiki/sources/old.md',page_text())
        self.assertEqual(row['title'],'Existing [title]')
        self.assertEqual(row['page_id'],'page.existing')

    def test_binary_raw_carriers_are_verified_without_text_conversion(self):
        files=scaffold();files['knowledge/raw/binary.dat']=b'\x00\xff\r\n'
        files['knowledge/wiki/_meta/sources.jsonl']=json.dumps({'source_id':'binary','raw_path':'knowledge/raw/binary.dat','content_sha256':sha(files['knowledge/raw/binary.dat'])})+'\n'
        self.assertEqual(len(decode_snapshot(files)['sources']),1)
        files['knowledge/raw/binary.dat']+=b'!'
        with self.assertRaisesRegex(ValueError,'RAW_CARRIER_MISMATCH'): decode_snapshot(files)

    def test_plan_rejects_overwrite_drift_escape_duplicate_and_unknown_action(self):
        files={'knowledge/raw/source.json':'old','knowledge/wiki/index.md':'index','knowledge/wiki/_meta/claims.jsonl':'{"claim_id":"one"}\n'}
        plans=[{'action':'CREATE','path':'knowledge/raw/source.json','content':'new'},
               {'action':'REPLACE_IF_DIGEST','path':'knowledge/wiki/index.md','expected_sha256':sha('wrong'),'content':'new'},
               {'action':'REPLACE_IF_DIGEST','path':'knowledge/raw/source.json','expected_sha256':sha('old'),'content':'new'},
               {'action':'APPEND','path':'knowledge/raw/source.json','content':'new'},
               {'action':'CREATE','path':'knowledge/../outside','content':'bad'},
               {'action':'APPEND_UNIQUE_JSONL','path':'knowledge/wiki/_meta/claims.jsonl','identity_field':'claim_id','record':{'claim_id':'one'}},
               {'action':'SHELL','path':'knowledge/anything'}]
        for plan in plans:
            with self.subTest(plan=plan),self.assertRaises(ValueError):simulate(files,[plan])
        self.assertEqual(files['knowledge/raw/source.json'],'old')


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'git';self.root.mkdir()
        self.files=scaffold();self.files['knowledge/wiki/sources/existing.md']=page_text()
        for path,text in self.files.items():
            dest=self.root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8',newline='\n')
        self.git('init','-q');self.git('config','user.name','Test');self.git('config','user.email','test@example.invalid');self.git('config','core.autocrlf','false');self.git('add','.');self.git('commit','-qm','fixture')
        self.head=self.git('rev-parse','HEAD').strip()
        self.server=Server(str(Path(self.tmp.name)/'state.db'),git_root=str(self.root))
        memory=fixture().replace(',OBS,',',UNK,')
        self.sid=self.server.call_tool('athena_wiki_import_registry',dict(source_id='registry',observed_at='2026-09-08T12:00:00Z',text=memory,expected_sha256=digest(memory),expected_snapshot_id=None))['snapshot_id']
        self.doc=self.server.call_tool('athena_wiki_import_document',dict(snapshot_id=self.sid,page_id='page.router',source_file_id='drive-page',source_revision='revision-1',text='Exact source\r\nwith uncertainty Ω',expected_sha256=digest('Exact source\r\nwith uncertainty Ω'),expected_document_id=None))['document_id']
        self.arguments=dict(expected_git_head=self.head,snapshot_id=self.sid,page_id='page.router',document_id=self.doc)
        self.requests=[]

    def git(self,*args):return subprocess.check_output(['git','-C',str(self.root),*args],text=True,encoding='utf-8',stderr=subprocess.DEVNULL)

    def tearDown(self):self.server.store.close();self.tmp.cleanup()

    def fake_compile(self,*,expected_git_head,request):
        self.assertEqual(expected_git_head,self.head);self.requests.append(copy.deepcopy(request))
        op=request['operation']
        if op=='INGEST':
            source=request['source'];path='knowledge/wiki/sources/imported.md'
            metadata=dict(page_id='page.imported',page_type='source',created_at=source['observed_at'],updated_at=source['observed_at'],source_ids=[source['source_id']],claim_ids=[c['claim_id'] for c in request['claims']],tags=[],links=[])
            text='<!-- ATHENA-WIKI-META\n'+json.dumps(metadata)+'\n-->\n\n# Imported\n\nImported observation\n'
            plan=[{'action':'VERIFY_EXISTING_IMMUTABLE','path':source['raw_path'],'expected_sha256':source['content_sha256']},
                  {'action':'CREATE','path':path,'content':text},
                  {'action':'APPEND_UNIQUE_JSONL','path':'knowledge/wiki/_meta/sources.jsonl','identity_field':'source_id','record':source}]
            plan += [{'action':'APPEND_UNIQUE_JSONL','path':'knowledge/wiki/_meta/claims.jsonl','identity_field':'claim_id','record':c} for c in request['claims']]
            inner={'standing':'READY','mutation_plan':plan}
        elif op=='REINDEX':
            self.assertEqual({p['page_id'] for p in request['pages']},{'page.existing','page.imported'})
            inner={'standing':'READY','mutation_plan':[{'action':'REPLACE_IF_DIGEST','path':'knowledge/wiki/index.md','expected_sha256':request['expected_index_sha256'],'content':'# Index\nExisting and imported\n'}]}
        else:
            self.assertEqual(op,'LINT');self.assertEqual(len(request['pages']),2)
            inner={'standing':'READY','severity_counts':{'ERROR':0,'WARNING':0}}
        return {'standing':'COMPLETE','wiki_standing':inner['standing'],'mutation_applied':False,'execution_receipt':{'outputs':[{'result':inner}]}}

    def test_complete_committed_snapshot_and_source_labels_survive_without_write(self):
        with patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile',side_effect=self.fake_compile):
            result=self.server.call_tool('athena_wiki_git_ingest',self.arguments)
        self.assertEqual(result['standing'],'READY_PROPOSAL')
        self.assertEqual([r['operation'] for r in self.requests],['INGEST','REINDEX','LINT'])
        self.assertEqual(result['original_claim_labels'],['UNK'])
        claim=self.requests[0]['claims'][0]
        self.assertEqual(claim['epistemic_status'],'RET');self.assertIn('source EPI=UNK',claim['statement'])
        carrier=json.loads(next(p['content'] for p in result['mutation_plan'] if p['path']==result['carrier_path']))
        self.assertEqual(carrier['document']['source_text'],'Exact source\r\nwith uncertainty Ω')
        self.assertEqual(carrier['records']['claims'][0]['EPI'],'UNK')
        self.assertEqual(carrier['records']['conflicts'][0]['STATE'],'OPEN')
        self.assertFalse(result['mutation_applied']);self.assertFalse(self.server.git.status()['dirty'])

    def test_replay_is_deterministic_and_historical_latest_flag_not_carrier_identity(self):
        with patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile',side_effect=self.fake_compile):
            a=WikiGitIngest(self.server).compile(**self.arguments)
            newer=fixture('Newer registry')
            self.server.call_tool('athena_wiki_import_registry',dict(source_id='registry',observed_at='2026-09-08T13:00:00Z',text=newer,expected_sha256=digest(newer),expected_snapshot_id=self.sid))
            b=WikiGitIngest(self.server).compile(**self.arguments)
        self.assertEqual(a['plan_sha256'],b['plan_sha256'])
        self.assertEqual(a['carrier_sha256'],b['carrier_sha256'])
        self.assertTrue(a['is_latest_local_snapshot']);self.assertFalse(b['is_latest_local_snapshot'])

    def test_counterevidence_survives_into_immutable_ingestion_carrier(self):
        from tests.test_wiki_counterevidence import registry
        text=registry()
        sid=self.server.call_tool('athena_wiki_import_registry',dict(source_id='registry',observed_at='2026-09-08T13:00:00Z',text=text,expected_sha256=digest(text),expected_snapshot_id=self.sid))['snapshot_id']
        body='Counterevidence stays attached.\r\nΩ'
        doc=self.server.call_tool('athena_wiki_import_document',dict(snapshot_id=sid,page_id='page.a',source_file_id='source.a',source_revision='revision-counter',text=body,expected_sha256=digest(body),expected_document_id=None))['document_id']
        with patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile',side_effect=self.fake_compile):
            result=self.server.call_tool('athena_wiki_git_ingest',dict(expected_git_head=self.head,snapshot_id=sid,page_id='page.a',document_id=doc))
        carrier=json.loads(next(p['content'] for p in result['mutation_plan'] if p['path']==result['carrier_path']))
        evidence={r['EVIDENCE_ID']:r for r in carrier['records']['evidence']}
        self.assertEqual(set(evidence),{'evidence.support','evidence.counter','evidence.mixed'})
        self.assertEqual(evidence['evidence.counter']['CONTRADICTS_CLAIMS'],'claim.a')
        self.assertEqual(carrier['document']['source_text'],body)
        self.assertEqual(self.requests[0]['claims'][0]['epistemic_status'],'RET')
        self.assertEqual(result['original_claim_labels'],['HYP'])

    def test_tampered_document_fails_before_any_git_compiler_call(self):
        with self.server.store.db:
            self.server.store.db.execute('UPDATE wiki_documents_v1 SET source_text=? WHERE document_id=?',('tampered',self.doc))
        with patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile') as compiler:
            with self.assertRaisesRegex(ValueError,'DIGEST_MISMATCH'):WikiGitIngest(self.server).compile(**self.arguments)
            compiler.assert_not_called()

    def test_truncated_context_cannot_be_exported_as_complete(self):
        from athena_mcp.wiki_memory import WikiMemory
        context=WikiMemory(self.server.store).context(snapshot_id=self.sid,page_id='page.router',document_id=self.doc)
        context['truncated']=True
        with patch.object(WikiMemory,'context',return_value=context),patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile') as compiler:
            with self.assertRaisesRegex(ValueError,'COMPLETE_IMPORTED_CONTEXT_REQUIRED'):WikiGitIngest(self.server).compile(**self.arguments)
            compiler.assert_not_called()

    def test_stale_or_dirty_git_stops_before_compiler(self):
        with patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile') as compiler:
            with self.assertRaises(ValueError):WikiGitIngest(self.server).compile(**{**self.arguments,'expected_git_head':'0'*40})
            (self.root/'untracked').write_text('changed')
            with self.assertRaises(ValueError):WikiGitIngest(self.server).compile(**self.arguments)
            compiler.assert_not_called()

    def test_lint_hold_cannot_yield_ready_mutation_plan(self):
        def compile(**kwargs):
            result=self.fake_compile(**kwargs)
            if kwargs['request']['operation']=='LINT':result['wiki_standing']='HOLD'
            return result
        with patch('athena_mcp.wiki_git_ingest.GitWikiCompiler.compile',side_effect=compile):
            result=WikiGitIngest(self.server).compile(**self.arguments)
        self.assertEqual(result['standing'],'HOLD');self.assertNotIn('mutation_plan',result)

    def test_pinned_blob_reader_rejects_git_symlink_even_on_windows(self):
        oid=self.git('hash-object','knowledge/wiki/index.md').strip()
        self.git('update-index','--add','--cacheinfo','120000,'+oid+',knowledge/wiki/unsafe.md')
        self.git('commit','-qm','symlink fixture')
        with self.assertRaisesRegex(ValueError,'NONREGULAR'):read_snapshot(self.server.git,self.git('rev-parse','HEAD').strip())


if __name__=='__main__':unittest.main()

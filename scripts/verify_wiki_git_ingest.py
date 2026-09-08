"""Replay observation ingestion and apply only in a disposable Git clone.

With --db and explicit source identities, reads an existing local observation.
Otherwise creates a synthetic observation in a temporary database. It never
pushes commits or modifies the supplied semantic checkout.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--semantic-root',required=True)
    parser.add_argument('--expected-head',required=True)
    parser.add_argument('--db')
    parser.add_argument('--snapshot-id')
    parser.add_argument('--page-id')
    parser.add_argument('--document-id')
    parser.add_argument('--output')
    parser.add_argument('--stage', action='store_true', help='Exercise durable local draft publication and retry before inspection.')
    args=parser.parse_args()
    if args.db and not all((args.snapshot_id,args.page_id,args.document_id)):
        parser.error('--db requires all three source identities')
    runtime=Path(__file__).resolve().parent.parent
    env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(runtime)}
    original=Path(args.semantic_root).resolve()
    def git(root,*values):
        return subprocess.check_output(['git','-C',str(root),*values],env=env).decode('utf-8').strip()
    assert git(original,'rev-parse','HEAD')==args.expected_head
    assert not git(original,'status','--porcelain','--untracked-files=all')
    with tempfile.TemporaryDirectory() as temporary:
        directory=Path(temporary)
        target=directory/'semantic'
        subprocess.run(['git','-c','core.autocrlf=false','clone','--quiet','--no-hardlinks',str(original),str(target)],check=True,env=env)
        subprocess.run(['git','-C',str(target),'checkout','--quiet','--detach',args.expected_head],check=True,env=env)
        db=Path(args.db).resolve() if args.db else directory/'state.db'
        def call(name,arguments):
            m={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':name,'arguments':arguments}}
            p=subprocess.run([sys.executable,'-B','-m','athena_mcp','--db',str(db),'--git-root',str(target)],input=json.dumps(m)+'\n',text=True,encoding='utf-8',capture_output=True,cwd=runtime,env=env,timeout=660)
            assert p.returncode==0,p.stderr
            response=json.loads(p.stdout)
            assert 'error' not in response and not response['result'].get('isError'),response
            return response['result']['structuredContent']
        def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
        if args.db:
            sid,page,did=args.snapshot_id,args.page_id,args.document_id
        else:
            tables=[(['PAGE_ID','TITLE','DRIVE_FILE_ID'],[['fixture.page','Uncertainty test','fixture.file']]),
                    (['CLAIM_ID','PAGE_ID','CLAIM_SUMMARY','EPI'],[['fixture.claim','fixture.page','Benefit remains unknown','UNK']]),
                    (['EVIDENCE_ID','KIND','SOURCE_REF'],[]),(['TASK_ID','PAGE_ID','SUCCESS_TEST'],[]),(['CONFLICT_ID','PAGE_ID','BRANCH_A'],[])]
            sections=[]
            for header,rows in tables:
                out=io.StringIO();writer=csv.writer(out);writer.writerow(header);writer.writerows(rows);sections.append(out.getvalue())
            registry='\f'.join(sections)
            sid=call('athena_wiki_import_registry',dict(source_id='fixture.registry',observed_at='2026-09-08T12:00:00Z',text=registry,expected_sha256=digest(registry),expected_snapshot_id=None))['snapshot_id']
            page='fixture.page';source='Fixture only: benefit is unknown.\r\nPreserve Ω and line endings.\n'
            did=call('athena_wiki_import_document',dict(snapshot_id=sid,page_id=page,source_file_id='fixture.file',source_revision='fixture-revision-1',text=source,expected_sha256=digest(source),expected_document_id=None))['document_id']
        original_context=call('athena_wiki_context',dict(snapshot_id=sid,page_id=page,document_id=did,max_records=500))
        proposal=call('athena_wiki_git_ingest',dict(expected_git_head=args.expected_head,snapshot_id=sid,page_id=page,document_id=did))
        assert proposal['standing']=='READY_PROPOSAL',proposal
        assert not proposal['mutation_applied']
        encoded_plan=json.dumps(proposal['mutation_plan'],ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
        assert hashlib.sha256(encoded_plan).hexdigest()==proposal['plan_sha256']
        assert [r['operation'] for r in proposal['receipts']]==['INGEST','REINDEX','LINT']
        assert not git(target,'status','--porcelain','--untracked-files=all')
        print('Three actual compiler stages passed; applying only in disposable checkout.',flush=True)
        # Validate all preconditions before creating a file. The disposable clone
        # has no concurrent writer; this helper is not a production transaction.
        for path,expected in proposal['base_readset'].items():
            assert 'sha256:'+hashlib.sha256((target/path).read_bytes()).hexdigest()==expected,path
        for item in proposal['mutation_plan']:
            dest=(target/item['path']).resolve()
            assert dest.is_relative_to(target.resolve()) and item['path'].startswith('knowledge/')
            if item['action']=='CREATE':assert not dest.exists()
            else:assert 'sha256:'+hashlib.sha256(dest.read_bytes()).hexdigest()==item['expected_sha256']
            assert 'sha256:'+digest(item['content'])==item['content_sha256']
        draft=None
        if args.stage:
            arguments=dict(expected_git_head=args.expected_head,snapshot_id=sid,page_id=page,document_id=did,expected_plan_sha256=proposal['plan_sha256'])
            draft=call('athena_wiki_git_stage',arguments)
            assert draft['standing']=='READY_LOCAL_DRAFT' and draft['source_checkout_unchanged'],draft
            assert draft['mutation_scope']=='LOCAL_DRAFT_REF_ONLY' and not draft['pushed'] and not draft['shared_state_applied']
            assert git(target,'rev-parse','HEAD')==args.expected_head
            assert git(target,'rev-parse',draft['ref'])==draft['commit']
            again=call('athena_wiki_git_stage',arguments)
            assert again['reused'] and again['commit']==draft['commit'] and again['ref']==draft['ref']
            draft['retry_reused']=True
            git(target,'checkout','--quiet','--detach',draft['commit'])
        else:
            for item in proposal['mutation_plan']:
                dest=target/item['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(item['content'].encode('utf-8'))
            git(target,'-c','user.name=Wiki replay','-c','user.email=wiki-replay@example.invalid','add','knowledge')
            git(target,'-c','user.name=Wiki replay','-c','user.email=wiki-replay@example.invalid','commit','-qm','Disposable observation ingestion replay')
        for item in proposal['mutation_plan']:
            assert 'sha256:'+hashlib.sha256((target/item['path']).read_bytes()).hexdigest()==item['content_sha256']
        applied_head=git(target,'rev-parse','HEAD')
        sys.path.insert(0,str(runtime))
        from athena_mcp.git_backend import GitBackend
        from athena_mcp.wiki_git_snapshot import decode_snapshot,read_snapshot
        state=decode_snapshot(read_snapshot(GitBackend(target),applied_head))
        lint=call('athena_git_wiki_compile',dict(expected_git_head=applied_head,request={'operation':'LINT','wiki':state['config'],**{k:state[k] for k in ('pages','sources','claims','contradictions')},'index_paths':[p['path'] for p in state['pages']]}))
        assert lint['wiki_standing']=='READY',lint
        carrier=json.loads((target/proposal['carrier_path']).read_bytes())
        assert carrier['document']['source_text']==original_context['document']['source_text']
        assert carrier['records']==original_context['records']
        assert not git(target,'status','--porcelain','--untracked-files=all')
        assert git(original,'rev-parse','HEAD')==args.expected_head and not git(original,'status','--porcelain','--untracked-files=all')
        report=dict(standing='PASS',source_kind='EXPLICIT_LOCAL_OBSERVATION' if args.db else 'SYNTHETIC_FIXTURE',semantic_base=args.expected_head,disposable_applied_head=applied_head,source_snapshot=sid,source_document=did,carrier_sha256=proposal['carrier_sha256'],plan_sha256=proposal['plan_sha256'],proposed_file_count=len(proposal['mutation_plan']),source_text_and_records_preserved=True,real_compiler_stages=['INGEST','REINDEX','LINT'],applied_only_to_disposable_clone=True,fresh_committed_lint='READY',original_checkout_unchanged=True,live_currentness='UNVERIFIED',behavioral_gain='UNKNOWN',proposal=proposal)
        if draft:report['local_draft']={k:v for k,v in draft.items() if k!='committed_lint'}
        if args.output:Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='proposal'},indent=2),flush=True)


if __name__=='__main__':main()

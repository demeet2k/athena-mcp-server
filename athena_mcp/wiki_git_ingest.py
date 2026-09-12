"""Compile an immutable local Drive observation into the configured Git Wiki.

The Git Wiki's current committed pages and ledgers are retained. Only retrieved
statements are emitted; original epistemic labels, conflicts and source text
remain in an exact JSON carrier. No plan is applied by this interface.
"""
import hashlib
import re
from urllib.parse import quote

from .wiki_git import GitWikiCompiler, canonical
from .wiki_memory import WikiMemory
from .wiki_git_snapshot import MAX_BYTES, decode_snapshot, read_snapshot, sha, simulate

ARTIFACT='ATHENA.MCP.WIKI_GIT_INGEST.V1'


class WikiGitIngest:
    def __init__(self, server):
        self.server=server

    def compile(self, *, expected_git_head, snapshot_id, page_id, document_id):
        if type(expected_git_head) is not str or not re.fullmatch(r'[0-9a-f]{40}',expected_git_head):
            raise ValueError('GIT_WIKI_EXACT_COMMIT_REQUIRED')
        git=self.server.git
        if not git.enabled: raise ValueError('GIT_WIKI_ROOT_NOT_CONFIGURED')
        initial=git.status()
        if initial['head']!=expected_git_head or initial['dirty']:
            raise ValueError('WIKI_BRIDGE_CLEAN_EXPECTED_HEAD_REQUIRED')
        context=WikiMemory(self.server.store).context(snapshot_id=snapshot_id,page_id=page_id,document_id=document_id,max_records=500)
        if context['truncated'] or context['document'] is None:
            raise ValueError('WIKI_BRIDGE_COMPLETE_IMPORTED_CONTEXT_REQUIRED')
        binding={key:context[key] for key in ('snapshot_id','source_id','observed_at','source_sha256')}
        carrier={'artifact':'ATHENA.DRIVE.WIKI.OBSERVATION.CARRIER.V1',
                 'registry_observation':binding,'page':context['page'],
                 'document':context['document'],'records':context['records'],
                 'unresolved_refs':context['unresolved_refs'],
                 'unresolved_evidence_refs':context['unresolved_evidence_refs'],
                 'scope':'EXACT_DOCUMENT_AND_PAGE_CONTEXT_NOT_COMPLETE_REGISTRY',
                 'live_currentness':'UNVERIFIED','source_claims_independently_verified':False}
        content=canonical(carrier).decode('utf-8')+'\n'
        if len(content.encode('utf-8'))>MAX_BYTES:
            raise ValueError('WIKI_BRIDGE_CARRIER_TOO_LARGE')
        raw_path='knowledge/raw/drive/'+document_id+'.json'
        source_id='drive.'+document_id
        before=read_snapshot(git,expected_git_head)
        base=decode_snapshot(before)
        if raw_path in before or any(s['source_id']==source_id for s in base['sources']):
            raise ValueError('WIKI_BRIDGE_OBSERVATION_ALREADY_PRESENT')
        when=context['observed_at']
        source={'source_id':source_id,'title':context['page']['TITLE'],
                'source_type':'drive_observation',
                'locator':'https://drive.google.com/file/d/'+quote(context['page']['DRIVE_FILE_ID'],safe='')+'/view#observation='+document_id,
                'content_sha256':sha(content),'observed_at':when,
                'summary':'Retrieved Drive Wiki observation; source labels are retained, not independently verified.',
                'raw_path':raw_path,'tags':['drive-observation','source-reported','snapshot:'+snapshot_id]}
        claims=[]
        for row in context['records']['claims']:
            token=hashlib.sha256(canonical([document_id,row['CLAIM_ID']])).hexdigest()
            label=row.get('EPI','UNSPECIFIED')
            claims.append({'claim_id':'driveclaim.'+token,
                           'statement':'Registry claim '+row['CLAIM_ID']+' [source EPI='+label+']: '+row['CLAIM_SUMMARY'],
                           'epistemic_status':'RET','observed_at':when,
                           'scope':'Report of an imported registry claim; original status, evidence and relations remain in the immutable carrier.',
                           'source_refs':[{'source_id':source_id,'locator':'records.claims:'+row['CLAIM_ID']}],
                           'tags':['source-epi:'+label,'source-claim:'+row['CLAIM_ID']]})
        receipts=[]
        compiler=GitWikiCompiler(git)
        def execute(request):
            result=compiler.compile(expected_git_head=expected_git_head,request={**request,'wiki':base['config']})
            receipts.append(result)
            if result['standing']!='COMPLETE' or result.get('wiki_standing')!='READY':
                return None
            return result['execution_receipt']['outputs'][0]['result']
        def held(stage):
            return {'artifact':ARTIFACT,'standing':'HOLD','stage':stage,'git_head':expected_git_head,
                    'snapshot_id':snapshot_id,'document_id':document_id,'receipts':receipts,
                    'mutation_applied':False,'behavioral_gain':'UNKNOWN'}
        ingested=execute({'operation':'INGEST','source':source,'claims':claims,
                          'existing':{'source_ids':[r['source_id'] for r in base['sources']],
                                      'claim_ids':[r['claim_id'] for r in base['claims']],
                                      'page_paths':[r['path'] for r in base['pages']]}})
        if ingested is None: return held('INGEST')
        landed=simulate(before,[{'action':'CREATE','path':raw_path,'content':content}])
        projected=simulate(landed,ingested['mutation_plan'])
        state=decode_snapshot(projected)
        reindexed=execute({'operation':'REINDEX','pages':state['pages'],'snapshot_complete':True,
                          'index_exists':True,'expected_index_sha256':sha(before[base['config']['index_path']])})
        if reindexed is None: return held('REINDEX')
        projected=simulate(projected,reindexed['mutation_plan'])
        lint=execute({'operation':'LINT',**{k:state[k] for k in ('pages','sources','claims','contradictions')},
                      'index_paths':[p['path'] for p in state['pages']]})
        if lint is None: return held('LINT')
        if git.status()!=initial:
            raise ValueError('WIKI_BRIDGE_GIT_CHANGED_DURING_COMPILE')
        files=[]
        for path,value in sorted(projected.items()):
            if value==before.get(path): continue
            if type(value) is not str: raise ValueError('WIKI_BRIDGE_UNEXPECTED_BINARY_MUTATION')
            files.append({'action':'REPLACE_IF_DIGEST' if path in before else 'CREATE','path':path,
                          'expected_sha256':sha(before[path]) if path in before else None,
                          'content':value,'content_sha256':sha(value)})
        result={'artifact':ARTIFACT,'standing':'READY_PROPOSAL','git_head':expected_git_head,
                'snapshot_id':snapshot_id,'document_id':document_id,'page_id':page_id,
                'source_revision':context['document']['source_revision'],
                'source_content_sha256':context['document']['source_sha256'],
                'carrier_path':raw_path,'carrier_sha256':sha(content),
                'base_readset':{p:sha(v) for p,v in sorted(before.items())},
                'mutation_plan':files,'plan_sha256':hashlib.sha256(canonical(files)).hexdigest(),
                'receipts':receipts,'complete_committed_wiki_retained':True,
                'original_claim_labels':[r.get('EPI','UNSPECIFIED') for r in context['records']['claims']],
                'emitted_claim_epistemic_status':'RET','mutation_applied':False,
                'is_latest_local_snapshot':context['is_latest_local_snapshot'],
                'live_currentness':'UNVERIFIED','behavioral_gain':'UNKNOWN',
                'verification_scope':'LINT_OF_COMPLETE_PROPOSED_WIKI; FILESYSTEM_APPLICATION_NOT_OBSERVED'}
        if len(canonical(result))>MAX_BYTES: raise ValueError('WIKI_BRIDGE_PROPOSAL_TOO_LARGE')
        return result

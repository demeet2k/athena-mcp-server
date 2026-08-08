from __future__ import annotations
import json,sys
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION,SERVER_INFO,TOOLS,PROMPTS
from .timebundle import TIME_PROVENANCE
from .orchestration import orchestration_law
from .orchestration_robustness import SUCCESSOR_FACTOR_COUNT
from .aor_development_surface import AOR_DEVELOPMENT_RESOURCES,AOR_DEVELOPMENT_RESOURCE_URIS

def handle(server,m):
    mid=m.get('id');method=m.get('method');params=m.get('params') or {}
    if method=='initialize':
        pv=params.get('protocolVersion',PROTOCOL_VERSION)
        return server.result(mid,{'protocolVersion':PROTOCOL_VERSION if pv!=PROTOCOL_VERSION else pv,'capabilities':{'tools':{'listChanged':False},'resources':{'listChanged':False},'prompts':{'listChanged':False}},'serverInfo':SERVER_INFO})
    if method in ('notifications/initialized','notifications/cancelled'):return None
    if method=='ping':return server.result(mid,{})
    if method=='tools/list':return server.result(mid,{'tools':sorted(TOOLS,key=lambda x:x['name'])})
    if method=='tools/call':
        name=params.get('name');args=params.get('arguments') or {}
        if not server.rate.allow(name):return server.result(mid,{'content':[{'type':'text','text':'Rate limit exceeded; retry later.'}],'isError':True})
        try:
            td=next((t for t in TOOLS if t['name']==name),None)
            if td is None:raise KeyError(name)
            validate(td['inputSchema'],args);value=server.call_tool(name,args)
            return server.result(mid,{'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}],'structuredContent':value,'isError':False})
        except StaleTarget as e:return server.result(mid,{'content':[{'type':'text','text':str(e)}],'structuredContent':{'status':'STALE_TARGET','detail':str(e)},'isError':True})
        except GitStaleHead as e:return server.result(mid,{'content':[{'type':'text','text':str(e)}],'structuredContent':{'status':'STALE_GIT_HEAD','detail':str(e)},'isError':True})
        except (ValueError,KeyError) as e:return server.result(mid,{'content':[{'type':'text','text':str(e)}],'isError':True})
        except Exception as e:
            print(f'tool error {name}: {e}',file=sys.stderr);return server.error(mid,-32603,'Internal error')
    if method=='resources/list':
        rs=[
            {'uri':'athena://manifest','name':'ATHENA Unified Runtime Manifest','mimeType':'application/json'},
            {'uri':'athena://kc144/stations','name':'KC144 12x12 Station Registry','mimeType':'application/json'},
            {'uri':'athena://state/head','name':'Canonical State Head','mimeType':'application/json'},
            {'uri':'athena://registry','name':'Canonical Capability Registry','mimeType':'application/json'},
            {'uri':'athena://jspace','name':'JSPACE Graph/Hypergraph','mimeType':'application/json'},
            {'uri':'athena://scale','name':'SCALE Representation Ladder','mimeType':'application/json'},
            {'uri':'athena://coordinate/charts','name':'Open-world Polycoordinate Chart Registry','mimeType':'application/json'},
            {'uri':'athena://crystals','name':'Crystallized Output Registry','mimeType':'application/json'},
            {'uri':'athena://math','name':'Mathematical Object Registry','mimeType':'application/json'},
            {'uri':'athena://time/provenance','name':'Atomic/Civil Time Provenance','mimeType':'application/json'},
            {'uri':'athena://transforms','name':'Coordinate Transform Registry / Execution History','mimeType':'application/json'},
            {'uri':'athena://emissions','name':'Final Crystal Emission Registry','mimeType':'application/json'},
            {'uri':'athena://collective/runtime','name':'Collective Intelligence Runtime / HIVE-SWARM-PACK-FLOCK-HERD-POD','mimeType':'application/json'},
            {'uri':'athena://collective/growth','name':'Collective Growth Operators / allocation-bridges-fission-alarms-lifecycle','mimeType':'application/json'},
            {'uri':'athena://collective/v2','name':'Collective Runtime V2 / persistent stigmergy-JSPACE alarms-RGO calibration-transactional topology-failure antibodies','mimeType':'application/json'},
            {'uri':'athena://orchestration/law','name':'AOR Developmental Decision Cortex Law','mimeType':'application/json'},
            {'uri':'athena://orchestration/recent','name':'Recent Persisted AORRUN Receipts','mimeType':'application/json'},
            {'uri':'athena://orchestration/robustness','name':'AOR Successor Robustness Law','mimeType':'application/json'},
            {'uri':'athena://branches','name':'AOR Branch Lifecycle Ledger','mimeType':'application/json'},
            {'uri':'athena://authority','name':'Typed Claim Authority Registry Y1','mimeType':'application/json'},
        ]
        known={r['uri'] for r in rs}
        rs.extend(r for r in AOR_DEVELOPMENT_RESOURCES if r['uri'] not in known)
        return server.result(mid,{'resources':rs})
    if method=='resources/read':
        uri=params.get('uri');c=server.core
        if uri in AOR_DEVELOPMENT_RESOURCE_URIS:val=server.aor_development.read_resource(uri)
        elif uri=='athena://manifest':val={'name':'ATHENA','protocol':PROTOCOL_VERSION,'layers':['GIT_LEDGER','CCR','JSPACE','SCALE','KC144','POLYCOORDINATE_ATLAS','MATH_REGISTRY','COLLECTIVE_RUNTIME','COLLECTIVE_GROWTH','COLLECTIVE_MEMORY_V2','AOR_DECISION_CORTEX','BRANCH_EVOLUTION','AUTHORITY_Y1','EQUIVALENCE_EQ1','RUNTIME'],'identity':'SID!=OID!=MID!=VID!=CID!=EID!=CRYS!=AORRUN','mutation':'EXPECTED_VID==CURRENT_VID else STALE_TARGET; collective topology has independent expected-version CAS','output_law':'VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY)','transform_law':'LOOKUP != DERIVATION','braid_law':'AOR chooses developmental frontier; Collective organizes scarce execution capacity; Y1 governs claim promotion; EQ1 allows collapse only from witnessed contradiction-free equivalence; consensus/pheromone/reward are never typed authority or evidence by themselves'}
        elif uri=='athena://kc144/stations':val=json.loads(station_manifest())
        elif uri=='athena://state/head':val=c.s.head('global') or {}
        elif uri=='athena://registry':val=c.s.rows('SELECT * FROM objects ORDER BY canonical_name')
        elif uri=='athena://jspace':val={'edges':c.s.rows('SELECT * FROM edges ORDER BY created_at DESC LIMIT 1000'),'hyperedges':c.s.rows('SELECT * FROM hyperedges ORDER BY created_at DESC LIMIT 1000')}
        elif uri=='athena://scale':val={'levels':{'S0':'RAW_EVENT','S1':'STATE_DELTA','S2':'RELATION_DELTA','S3':'MOTIF','S4':'GENERATOR','S5':'ORGAN_NATIVE_LAW'}}
        elif uri=='athena://coordinate/charts':val=c.s.rows('SELECT * FROM coordinate_charts ORDER BY name')
        elif uri=='athena://crystals':val=c.s.rows('SELECT crystal_id,oid,vid,mid,header,created_at FROM crystals ORDER BY created_at DESC LIMIT 1000')
        elif uri=='athena://math':val=c.s.rows('SELECT * FROM math_objects ORDER BY created_at DESC LIMIT 1000')
        elif uri=='athena://time/provenance':val=TIME_PROVENANCE
        elif uri=='athena://transforms':val={'transforms':c.s.rows('SELECT t.*,p.mode,p.program_json,p.metric_json FROM transforms t LEFT JOIN transform_programs p ON p.transform_id=t.transform_id ORDER BY t.created_at DESC LIMIT 1000'),'executions':c.s.rows('SELECT * FROM transform_executions ORDER BY created_at DESC LIMIT 1000')}
        elif uri=='athena://emissions':val=c.s.rows('SELECT envelope_id,crystal_id,emission_mid,visible_digest,created_at FROM emissions ORDER BY created_at DESC LIMIT 1000')
        elif uri=='athena://collective/runtime':val=server.collective.describe()
        elif uri=='athena://collective/growth':val=server.collective_growth.describe()
        elif uri=='athena://collective/v2':val=server.collective_memory.describe()
        elif uri=='athena://orchestration/law':val={**orchestration_law(),'authority_law':'Y in {?,+,!,#} is persistent, non-skippable and distinct from score/confidence/consensus/reward; linked candidates snapshot Y state into AORRUN','dedup_law':'UNKNOWN sameness preserves identity; only witnessed contradiction-free EQ1 components may collapse'}
        elif uri=='athena://orchestration/recent':val=server.orchestration.recent(50)
        elif uri=='athena://orchestration/robustness':val={'version':'AOR.3.2','successor_factor_count':SUCCESSOR_FACTOR_COUNT,'law':'q*((1-eps)/(1+eps))^5; eps*=(q^(1/5)-1)/(q^(1/5)+1)','boundary':'rank sensitivity, not truth probability or causal evidence'}
        elif uri=='athena://branches':val={'benchmark':server.branches.benchmark(),'recent':server.branches.list(limit=100),'law':'branch lifecycle is basis-specific witnessed EWMA state; hibernate != erase; resurrection requires new evidence/gap/bridge pressure plus policy thresholds'}
        elif uri=='athena://authority':val={'benchmark':server.authority.benchmark(),'claims':server.authority.list(limit=100),'law':'?->+ verified evidence; +->! witnessed execution; !-># explicit authorized canonicalization; challenges block automatic routing; authority != confidence != consensus != reward'}
        else:return server.error(mid,-32002,'Resource not found',{'uri':uri})
        return server.result(mid,{'contents':[{'uri':uri,'mimeType':'application/json','text':json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list':return server.result(mid,{'prompts':PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev':return server.error(mid,-32602,'Unknown prompt')
        a=params.get('arguments') or {};task=a.get('task','');agent=a.get('agent','ATHENA')
        text='ATHENA UNIFIED AOR×COLLECTIVE MAXDEV\nAGENT='+str(agent)+'\nTASK='+str(task)+'''\n1 HYDRATE canonical semantic/Git heads, JSPACE/SCALE/KC144/polycoordinates, Collective-V2 memory, Y1 authority heads and pending global mutations. UNKNOWN != N/A != 0.
2 RECONSTRUCT causal ancestry. Pheromone and antibody memory are routing/history signals only: pheromone priority != evidence; reuse/popularity != authority.
3 EXTRACT candidate work before collapse. Dedup is not textual similarity: use EQ1 only when witnessed sameness holds across semantic object, functional role, proof route, carrier, lineage, boundary and failure role. UNKNOWN/conflict preserves identities.
4 RETRIEVE/GRAPH/GAP with explicit provenance and typed dependency semantics. Missing measurements remain UNKNOWN and route to measurement/calibration instead of zero.
5 AUTHORITY: linked claims carry persistent Y∈{?,+,!,#}. Authority is not confidence, score, consensus or reward. ?->+ requires verified support/derive/reproduce evidence; +->! requires procedure+observation+result+witness; !-># requires explicit authorized canonicalization. CHALLENGED/CANONICAL_CHALLENGED blocks automatic routing. AORRUN freezes authority snapshots so later changes cannot rewrite history.
6 FIELD/CANDIDATES: consequential work becomes explicit candidate objects. AOR evaluates developmental value; Collective does not decide truth or authority.
7 AOR FRONTIER: call athena_orchestrate with explicit candidate/residual metrics and declared basis for cross-candidate arithmetic. Dependencies, Y minimums, claimed test/persistence, coordinates and fake/unsupported/contradiction gates fail closed. Preserve Pareto and robustness state.
8 COLLECTIVE ORGANIZATION: call athena_collective_plan/allocate after the developmental frontier exists. AOR answers WHAT deserves resources; Collective answers HOW scarce workers/topology/reserve execute it. Consensus != evidence and predicted RGO != observed RGO.
9 EXECUTE reachable selected work. Record branch reward only with witnessed calibrated observations. HIBERNATED != erased; resurrection requires explicit pressure.
10 TEST/OBSERVE/REPAIR/RETEST. Claimed test requires procedure+observation+result+witness. Persistence requires commit+receipt+verify. Diagnosed failures should enter antibody memory with regression evidence.
11 REWARD/REALLOCATE. Positive verified developmental reward may deepen/replicate/braid; low-value duplicate work may hibernate. Do not double-count RGO and DeltaJ for one outcome.
12 MEMORY: record observed RGO after execution; reinforce reusable routes only as attention/routing state. Contradiction/staleness evaporates inherited priority.
13 SUCCESSOR: NEXT comes from unresolved eligible frontier, not textual order. If no executable branch exists, route measurement>calibration>authority/dependency repair>residual before quiescence.
14 FINALIZE exact visible output through athena_finalize_output; do not mutate signed emission bytes afterward. Preserve RETURN/navigation and governing run references.
15 COMMIT only against current semantic VID/Git HEAD; topology has separate CAS. Rehydrate and continue while actionable pressure remains.
'''
        return server.result(mid,{'description':'Unified AOR decision cortex × Y1 authority × EQ1 dedup × Collective execution metabolism cycle','messages':[{'role':'user','content':{'type':'text','text':text}}]})
    return server.error(mid,-32601,'Method not found')

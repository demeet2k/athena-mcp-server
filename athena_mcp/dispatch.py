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
        ];return server.result(mid,{'resources':rs})
    if method=='resources/read':
        uri=params.get('uri');c=server.core
        if uri=='athena://manifest':val={'name':'ATHENA','protocol':PROTOCOL_VERSION,'layers':['GIT_LEDGER','CCR','JSPACE','SCALE','KC144','POLYCOORDINATE_ATLAS','MATH_REGISTRY','COLLECTIVE_RUNTIME','COLLECTIVE_GROWTH','COLLECTIVE_MEMORY_V2','AOR_DECISION_CORTEX','BRANCH_EVOLUTION','RUNTIME'],'identity':'SID!=OID!=MID!=VID!=CID!=EID!=CRYS!=AORRUN','mutation':'EXPECTED_VID==CURRENT_VID else STALE_TARGET; collective topology has independent expected-version CAS','output_law':'VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY)','transform_law':'LOOKUP != DERIVATION','braid_law':'AOR chooses developmental frontier; Collective organizes scarce execution capacity; pheromone/consensus never become evidence or typed authority'}
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
        elif uri=='athena://orchestration/law':val=orchestration_law()
        elif uri=='athena://orchestration/recent':val=server.orchestration.recent(50)
        elif uri=='athena://orchestration/robustness':val={'version':'AOR.3.2','successor_factor_count':SUCCESSOR_FACTOR_COUNT,'law':'q*((1-eps)/(1+eps))^5; eps*=(q^(1/5)-1)/(q^(1/5)+1)','boundary':'rank sensitivity, not truth probability or causal evidence'}
        elif uri=='athena://branches':val={'benchmark':server.branches.benchmark(),'recent':server.branches.list(limit=100),'law':'branch lifecycle is basis-specific witnessed EWMA state; hibernate != erase; resurrection requires new evidence/gap/bridge pressure plus policy thresholds'}
        else:return server.error(mid,-32002,'Resource not found',{'uri':uri})
        return server.result(mid,{'contents':[{'uri':uri,'mimeType':'application/json','text':json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list':return server.result(mid,{'prompts':PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev':return server.error(mid,-32602,'Unknown prompt')
        a=params.get('arguments') or {};task=a.get('task','');agent=a.get('agent','ATHENA')
        text=f"""ATHENA UNIFIED AOR×COLLECTIVE MAXDEV
AGENT={agent}
TASK={task}
1 HYDRATE canonical semantic/Git heads, JSPACE/SCALE/KC144/polycoordinates, Collective-V2 memory and pending global mutations. UNKNOWN != N/A != 0.
2 RECONSTRUCT causal ancestry. Query pheromone and failure-antibody memory as routing/history signals only: pheromone priority != evidence; reuse/popularity != authority.
3 EXTRACT candidate work before collapse. Do not silently dedup independent proof, lineage, boundary, contradiction or failure branches.
4 RETRIEVE/GRAPH/GAP with explicit provenance and typed dependency semantics. Missing measurements remain UNKNOWN and must enter measurement/calibration pressure rather than score as zero.
5 FIELD/CANDIDATES: consequential work becomes explicit candidate objects. AOR evaluates developmental value; Collective does not decide truth or authority.
6 AOR FRONTIER: call athena_orchestrate with explicit candidate/residual metrics and a declared metric basis when cross-candidate arithmetic is used. Dependencies, claimed test/persistence, coordinate requirements and fake/unsupported/contradiction gates fail closed. Preserve Pareto alternatives and robustness state.
7 COLLECTIVE ORGANIZATION: use athena_collective_plan/allocate only after the developmental frontier exists. AOR answers WHAT deserves resources; Collective answers HOW scarce workers/topology/reserve should execute it. Consensus != evidence and predicted RGO != observed RGO.
8 EXECUTE reachable selected work. For branch reward changes, record witnessed calibrated observations with athena_branch_observe. HIBERNATED != erased; resurrection requires explicit new_evidence/new_gap/bridge_demand pressure.
9 TEST/OBSERVE/REPAIR/RETEST. A claimed test requires procedure+observation+result+witness. A persistence claim requires commit+receipt+verify. Diagnosed failures should be matched/registered as antibodies with regression evidence.
10 REWARD/REALLOCATE. Positive verified developmental reward may deepen/replicate/braid; low-value duplicate work may hibernate. Do not double-count observed RGO and DeltaJ as independent evidence for the same outcome.
11 MEMORY: record observed RGO after execution; reinforce reusable routes with pheromone only as attention/routing state. Contradiction/staleness must evaporate inherited priority.
12 SUCCESSOR: NEXT comes from unresolved eligible developmental frontier, not textual order. If no executable branch exists, route measurement>calibration>dependency repair>residual before declaring quiescence.
13 FINALIZE exact visible output through athena_finalize_output; do not mutate signed emission bytes afterward. Preserve RETURN/navigation and any materially governing collective/AOR run references.
14 COMMIT only against current semantic VID/Git HEAD; topology has separate CAS. Rehydrate after mutation and continue while actionable pressure remains.
"""
        return server.result(mid,{'description':'Unified AOR decision cortex × Collective execution metabolism cycle','messages':[{'role':'user','content':{'type':'text','text':text}}]})
    return server.error(mid,-32601,'Method not found')

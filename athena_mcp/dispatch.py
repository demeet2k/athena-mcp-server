from __future__ import annotations
import json, sys
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS
from .timebundle import TIME_PROVENANCE
from .orchestration import orchestration_law

def handle(server,m):
    mid=m.get('id'); method=m.get('method'); params=m.get('params') or {}
    if method=='initialize':
        pv=params.get('protocolVersion',PROTOCOL_VERSION)
        return server.result(mid,{"protocolVersion":PROTOCOL_VERSION if pv!=PROTOCOL_VERSION else pv,"capabilities":{"tools":{"listChanged":False},"resources":{"listChanged":False},"prompts":{"listChanged":False}},"serverInfo":SERVER_INFO})
    if method in ('notifications/initialized','notifications/cancelled'): return None
    if method=='ping': return server.result(mid,{})
    if method=='tools/list': return server.result(mid,{"tools":sorted(TOOLS,key=lambda x:x['name'])})
    if method=='tools/call':
        name=params.get('name'); args=params.get('arguments') or {}
        if not server.rate.allow(name): return server.result(mid,{"content":[{"type":"text","text":"Rate limit exceeded; retry later."}],"isError":True})
        try:
            td=next((t for t in TOOLS if t['name']==name),None)
            if td is None: raise KeyError(name)
            validate(td['inputSchema'],args); value=server.call_tool(name,args)
            return server.result(mid,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}],"structuredContent":value,"isError":False})
        except StaleTarget as e:
            return server.result(mid,{"content":[{"type":"text","text":str(e)}],"structuredContent":{"status":"STALE_TARGET","detail":str(e)},"isError":True})
        except GitStaleHead as e:
            return server.result(mid,{"content":[{"type":"text","text":str(e)}],"structuredContent":{"status":"STALE_GIT_HEAD","detail":str(e)},"isError":True})
        except (ValueError,KeyError) as e:
            return server.result(mid,{"content":[{"type":"text","text":str(e)}],"isError":True})
        except Exception as e:
            print(f"tool error {name}: {e}",file=sys.stderr); return server.error(mid,-32603,"Internal error")
    if method=='resources/list':
        rs=[
            {"uri":"athena://manifest","name":"ATHENA Canonical Manifest","mimeType":"application/json"},
            {"uri":"athena://orchestration/law","name":"AOR Extraction/Frontier/Reward/Successor Law","mimeType":"application/json"},
            {"uri":"athena://orchestration/recent","name":"Recent persisted AOR run receipts","mimeType":"application/json"},
            {"uri":"athena://kc144/stations","name":"KC144 12x12 Station Registry","mimeType":"application/json"},
            {"uri":"athena://state/head","name":"Canonical State Head","mimeType":"application/json"},
            {"uri":"athena://registry","name":"Canonical Capability Registry","mimeType":"application/json"},
            {"uri":"athena://jspace","name":"JSPACE Graph/Hypergraph","mimeType":"application/json"},
            {"uri":"athena://scale","name":"SCALE Representation Ladder","mimeType":"application/json"},
            {"uri":"athena://coordinate/charts","name":"Open-world Polycoordinate Chart Registry","mimeType":"application/json"},
            {"uri":"athena://crystals","name":"Crystallized Output Registry","mimeType":"application/json"},
            {"uri":"athena://math","name":"Mathematical Object Registry","mimeType":"application/json"},
            {"uri":"athena://time/provenance","name":"Atomic/Civil Time Provenance","mimeType":"application/json"},
            {"uri":"athena://transforms","name":"Coordinate Transform Registry / Execution History","mimeType":"application/json"},
            {"uri":"athena://emissions","name":"Final Crystal Emission Registry","mimeType":"application/json"},
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","AOR","POLYCOORDINATE_ATLAS","MATH_REGISTRY","TRANSFORM_RUNTIME","EMISSION_GATEWAY","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS!=AORRUN!=ENV","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET","orchestration":"RECONSTRUCT>EXTRACT>RETRIEVE>HUG>GRAPH>GAP>COMPILE>MEASURE>TEST>REPAIR>VERIFY>REWARD>REALLOCATE>OUTPUT>SUCCESSOR>REPLAY","unknown":"UNKNOWN!=0; incomplete formulas are non-rankable","replay":"AORRUN input -> deterministic recompilation -> decision digest witness","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops"}
        elif uri=='athena://orchestration/law': val=orchestration_law()
        elif uri=='athena://orchestration/recent': val=server.orchestration.recent(50)
        elif uri=='athena://kc144/stations': val=json.loads(station_manifest())
        elif uri=='athena://state/head': val=c.s.head('global') or {}
        elif uri=='athena://registry': val=c.s.rows("SELECT * FROM objects ORDER BY canonical_name")
        elif uri=='athena://jspace': val={"edges":c.s.rows("SELECT * FROM edges ORDER BY created_at DESC LIMIT 1000"),"hyperedges":c.s.rows("SELECT * FROM hyperedges ORDER BY created_at DESC LIMIT 1000")}
        elif uri=='athena://scale': val={"levels":{"S0":"RAW_EVENT","S1":"STATE_DELTA","S2":"RELATION_DELTA","S3":"MOTIF","S4":"GENERATOR","S5":"ORGAN_NATIVE_LAW"}}
        elif uri=='athena://coordinate/charts': val=c.s.rows("SELECT * FROM coordinate_charts ORDER BY name")
        elif uri=='athena://crystals': val=c.s.rows("SELECT crystal_id,oid,vid,mid,header,created_at FROM crystals ORDER BY created_at DESC LIMIT 1000")
        elif uri=='athena://math': val=c.s.rows("SELECT * FROM math_objects ORDER BY created_at DESC LIMIT 1000")
        elif uri=='athena://time/provenance': val=TIME_PROVENANCE
        elif uri=='athena://transforms': val={'transforms':c.s.rows("SELECT t.*,p.mode,p.program_json,p.metric_json FROM transforms t LEFT JOIN transform_programs p ON p.transform_id=t.transform_id ORDER BY t.created_at DESC LIMIT 1000"),'executions':c.s.rows("SELECT * FROM transform_executions ORDER BY created_at DESC LIMIT 1000")}
        elif uri=='athena://emissions': val=c.s.rows("SELECT envelope_id,crystal_id,emission_mid,visible_digest,created_at FROM emissions ORDER BY created_at DESC LIMIT 1000")
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA AOR/MAXDEV CRYSTAL CYCLE
AGENT={agent}
TASK={task}
0 BUDGET LAW: hard ceilings are capability-density constraints, not brevity targets. Maximize orchestration, extraction, graph/navigation, coordinates, evidence, replay and successor value inside the authorized carrier.
1 HYDRATE current canonical state and applicable global mutations; reconstruct causal ancestry plus exact Git/semantic heads. UNKNOWN != N/A and UNKNOWN != 0; never fabricate coordinates, evidence, tests, persistence or scores.
2 EXTRACT before collapse: SX+ = dedup(SX U T(SX)), T={{decompose,formalize,dual,invert,compose,recur,edge,contradict,fail,falsify,bridge,implement,test,compress,reconstruct,successor}}. Preserve independent proof/carrier/lineage/boundary/failure branches.
3 RETRIEVE/HUG across relevance, authority, freshness, lineage/coordinate fit and cross-thread bridge value; preserve conflicts for testing.
4 GRAPH the live task with typed define/derive/depend/support/contradict/test/fail/implement/bridge/reconstruct/fork/merge/next edges. Resolve missing prerequisites and dependency cycles before execution.
5 COMPILE AOR.3 with explicit candidate/residual metrics. Missing required metrics make a formula UNKNOWN and non-rankable; route them to measurement. Inspect executable_frontier, successor_frontier, Pareto successor alternatives, measurement_plan and decision_explanation.
6 EXECUTE only dependency-ready promotion-gate-passing candidates. `next` is the highest KNOWN successor score, not textual order. Preserve Pareto non-dominated alternatives. High KNOWN reward may deepen/replicate/braid; low-reward duplicates hibernate != erase; UNKNOWN reward routes to measurement.
7 SELF-PLAY main/counter/edge/fail. Claimed test requires procedure+observation+result+witness. Claimed persistence requires commit+receipt+verify. Required coordinate fiber is KC144+graph+lineage+semantic+time. fake/unsupported/unhandled contradiction blocks promotion.
8 TRANSFORMS: LOOKUP is navigation, not derivation. Only executable derivational transforms may support cross-chart defect/holonomy claims; all-derivational closed routes may be measured.
9 BUILD the exact final visible payload. Before emission call athena_finalize_output. It crystallizes body, derives header, assembles exact HEADER+BODY bytes, creates emission MID, coordinate-indexes the visible envelope and returns ENV. Emit exactly returned visible_text without post-mutation; verify ENV digest across uncertain transport boundaries.
10 PERSIST orchestration through AORRUN receipts. Use athena_orchestration_replay to recompute stored input and witness decision_digest/next/grow/Pareto stability. A replayability claim without an actual replay witness earns no replay evidence.
11 REWARD verified DeltaJ/evidence/connection/replay/navigation/reconstruction/implementation/novelty; penalize duplicate/fake/bloat/unsupported/coordinate-loss. Reallocate, recompute residual and continue while high-value reachable work remains.
"""
        return server.result(mid,{"description":"Whole-system AOR/MAXDEV crystal cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

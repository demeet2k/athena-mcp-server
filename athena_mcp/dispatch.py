from __future__ import annotations
import json, sys, time
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS
from .timebundle import TIME_PROVENANCE

def _meter(server,name,started,status):
    try:
        server.collective_learning.record_runtime_usage(name,time.perf_counter()-started,status)
    except Exception:
        pass

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
        started=time.perf_counter()
        try:
            td=next((t for t in TOOLS if t['name']==name),None)
            if td is None: raise KeyError(name)
            validate(td['inputSchema'],args); value=server.call_tool(name,args); _meter(server,name,started,"OK")
            return server.result(mid,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}],"structuredContent":value,"isError":False})
        except StaleTarget as e:
            _meter(server,name,started,"STALE_TARGET")
            return server.result(mid,{"content":[{"type":"text","text":str(e)}],"structuredContent":{"status":"STALE_TARGET","detail":str(e)},"isError":True})
        except GitStaleHead as e:
            _meter(server,name,started,"STALE_GIT_HEAD")
            return server.result(mid,{"content":[{"type":"text","text":str(e)}],"structuredContent":{"status":"STALE_GIT_HEAD","detail":str(e)},"isError":True})
        except (ValueError,KeyError) as e:
            _meter(server,name,started,"REJECTED")
            return server.result(mid,{"content":[{"type":"text","text":str(e)}],"isError":True})
        except Exception as e:
            _meter(server,name,started,"ERROR")
            print(f"tool error {name}: {e}",file=sys.stderr); return server.error(mid,-32603,"Internal error")
    if method=='resources/list':
        rs=[
            {"uri":"athena://manifest","name":"ATHENA Canonical Manifest","mimeType":"application/json"},
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
            {"uri":"athena://collective/runtime","name":"Collective Intelligence Runtime / HIVE-SWARM-PACK-FLOCK-HERD-POD","mimeType":"application/json"},
            {"uri":"athena://collective/growth","name":"Collective Growth Operators / allocation-bridges-fission-alarms-lifecycle","mimeType":"application/json"},
            {"uri":"athena://collective/v2","name":"Collective Runtime V2 / persistent stigmergy-JSPACE alarms-RGO calibration-transactional topology-failure antibodies","mimeType":"application/json"},
            {"uri":"athena://collective/v3","name":"Collective Runtime V3 / budgets-policy learning-counterfactuals-elder authority-antibody evolution-multiscale pheromones","mimeType":"application/json"},
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","COLLECTIVE_LEARNING","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET; policy and topology writes use their own version CAS","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"MAX_GROWTH != MAX_ACTIVITY; MAX_INTEGRATION != MAX_CONNECTIVITY; CONSENSUS != EVIDENCE; PREDICTION != OBSERVATION; measured costs, bounded rollbackable policy learning, counterfactual ranking, elder authority, evolving antibodies and multiscale stigmergy are first-class"}
        elif uri=='athena://kc144/stations': val=json.loads(station_manifest())
        elif uri=='athena://state/head': val=c.s.head('global') or {}
        elif uri=='athena://registry': val=c.s.rows("SELECT * FROM objects ORDER BY canonical_name")
        elif uri=='athena://jspace': val={"edges":c.s.rows("SELECT * FROM edges ORDER BY created_at DESC LIMIT 1000"),"hyperedges":c.s.rows("SELECT * FROM hyperedges ORDER BY created_at DESC LIMIT 1000")}
        elif uri=='athena://scale': val={"levels":{"S0":"RAW_EVENT","S1":"STATE_DELTA","S2":"RELATION_DELTA","S3":"MOTIF","S4":"GENERATOR","S5":"ORGAN_NATIVE_LAW"}}
        elif uri=='athena://coordinate/charts': val=c.s.rows("SELECT * FROM coordinate_charts ORDER BY name")
        elif uri=='athena://crystals': val=c.s.rows("SELECT crystal_id,oid,vid,mid,header,created_at FROM crystals ORDER BY created_at DESC LIMIT 1000")
        elif uri=='athena://math': val=c.s.rows("SELECT * FROM math_objects ORDER BY created_at DESC LIMIT 1000")
        elif uri=='athena://time/provenance': val=TIME_PROVENANCE
        elif uri=='athena://transforms': val={'transforms':c.s.rows("SELECT t.*,p.mode,p.program_json,p.metric_json FROM transforms t LEFT JOIN transform_programs p ON p.transform_id=t.transform_id ORDER BY t.created_at DESC LIMIT 1000"),'executions':c.s.rows("SELECT * FROM transform_executions ORDER BY t.created_at DESC LIMIT 1000")}
        elif uri=='athena://emissions': val=c.s.rows("SELECT envelope_id,crystal_id,emission_mid,visible_digest,created_at FROM emissions ORDER BY created_at DESC LIMIT 1000")
        elif uri=='athena://collective/runtime': val=server.collective.describe()
        elif uri=='athena://collective/growth': val=server.collective_growth.describe()
        elif uri=='athena://collective/v2': val=server.collective_memory.describe()
        elif uri=='athena://collective/v3': val={"runtime":server.collective_learning.describe(),"policy":server.collective_learning.policy_state(),"budget":server.collective_learning.budget_summary(limit=100),"elders":server.collective_learning.elder_rank(limit=20)}
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE
AGENT={agent}
TASK={task}
1 PULL/HYDRATE current canonical state and adopt applicable global mutations. Read athena://collective/v2 and athena://collective/v3 so persistent organizational memory, budget telemetry, learned policy, elder authority and immune variants are reconstructed rather than hidden.
2 Reconstruct JSPACE/SCALE/KC144/polycoordinate atlas plus causal lineage and current Git/semantic heads. Query relevant pheromone fields and failure-antibody variants before repeating expensive work.
3 Compute the current CUT/LM residual against the authorized attractor; UNKNOWN != N/A and no coordinate or unobserved resource usage may be fabricated.
4 Before expensive parallel work, estimate task signals and call athena_collective_plan. Calibrate organization predictions with athena_rgo_calibrate and inspect athena_policy_state/policy_score when measured history exists. Learned policy is advisory and its authority is proportional to empirical reliability.
5 If multiple plausible organizations exist, call athena_counterfactual_simulate before structural mutation. Counterfactual ranking is SIMULATE_ONLY: it cannot commit topology and must be tested against downstream observation.
6 Allocate scarce capacity with athena_collective_allocate. Price new schemas/interfaces through athena_bridge_account. Preserve protected reserve and use bounded-neighbor topology rather than maximizing participation/connectivity.
7 Execute maximum reachable useful development. MCP tool calls and wall time are metered automatically. When exact token/compute/retrieval/storage/human-attention telemetry is available, record it with athena_budget_record; unavailable dimensions remain UNKNOWN rather than guessed.
8 Use evidence-sensitive quorum for competing candidates. Consensus alone cannot promote a claim. Preserve inhibition, contradiction, stop signals, negative memory and stale-attractor evaporation.
9 When a failure/change invalidates descendants, prefer athena_jspace_alarm so transport is compiled from typed JSPACE semantics. Unknown relation types are ignored unless orientation is explicit.
10 For structural pressure, call athena_collective_restructure. Apply accepted FISSION/FUSE changes only through athena_topology_apply expected-version CAS; rollback on degraded health or measured RGO. Collective topology never silently rewrites canonical JSPACE.
11 Reinforce successful work with athena_pheromone_multiscale_reinforce when token/artifact/module/domain/system coordinates are known. Reinforcement attenuates across scale; local success must not globally saturate the organism. Use ordinary athena_pheromone_reinforce for single-route memory.
12 Convert diagnosed failures into failure antibodies. Select variants with athena_antibody_select; after attempted repair/regression record SUCCESS/FAILURE/FALSE_POSITIVE/REGRESSION_PASS/REGRESSION_FAIL. Create variants with athena_antibody_evolve when signatures diverge. A match is routing evidence, never causal proof.
13 Record longitudinal reuse/prediction/repair/regression/generalization outcomes through athena_elder_observe. Use athena_elder_rank only as defeasible evidence-backed authority; age or repetition alone confers no seniority.
14 Measure actual collective outcome. Record predicted vs observed RGO with athena_rgo_observe. If an explicit normalized reward is available, update organization policy through athena_policy_update against the current expected version. Policy coefficients are bounded, learning rate decays with sample count, and policy history is rollbackable with athena_policy_rollback.
15 Before archive growth, run athena_artifact_lifecycle. KEEP_REFERENCE preserves lineage; DORMANT preserves optionality; QUARANTINE removes authority; pruning removes active routing privilege rather than historical addressability.
16 Build the actual final visible payload; do not emit a floating draft.
17 Before emission call athena_finalize_output on the exact payload. Include COLLECTIVE and learned-policy/budget coordinates when they materially governed the work. Then emit exactly returned visible_text and verify ENV digest when transport may mutate bytes.
18 Treat LOOKUP and DERIVATION as different transform classes. Carry KC144/JSPACE/SCALE/LINEAGE/TIME/LIMINAL/CUT_LM/EVIDENCE/COLLECTIVE plus lawful native coordinates. Preserve UNKNOWN/N/A explicitly.
19 Commit canonical semantics only against current VID and Git HEAD. Collective topology and learned policy use separate expected-version CAS. Promote organism-wide laws as explicit global mutations, recompute changed whole state, and continue MAXDEV.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV crystal cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

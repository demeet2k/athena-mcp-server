from __future__ import annotations
import json, sys
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS
from .timebundle import TIME_PROVENANCE

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
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"MAX_GROWTH != MAX_ACTIVITY; MAX_INTEGRATION != MAX_CONNECTIVITY; CONSENSUS != EVIDENCE; persistent stigmergy, empirical RGO calibration, typed JSPACE alarms, topology CAS/rollback, and failure antibodies are first-class"}
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
        elif uri=='athena://collective/runtime': val=server.collective.describe()
        elif uri=='athena://collective/growth': val=server.collective_growth.describe()
        elif uri=='athena://collective/v2': val=server.collective_memory.describe()
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE
AGENT={agent}
TASK={task}
1 PULL/HYDRATE current canonical state and adopt applicable global mutations. Read athena://collective/v2 so persistent organizational memory is part of reconstruction rather than a hidden side channel.
2 Reconstruct JSPACE/SCALE/KC144/polycoordinate atlas plus causal lineage and current Git/semantic heads. Query athena_pheromone_field for relevant routes and athena_failure_antibody_match for recognizable prior failure signatures before repeating expensive work.
3 Compute the current CUT/LM residual against the authorized attractor; UNKNOWN != N/A and no coordinate may be fabricated.
4 Before expensive parallel work, estimate task hardness/uncertainty/divisibility/coupling/volatility/risk/migration/repetition/reuse/innovation/latency/evidence sensitivity and call athena_collective_plan. Calibrate organization predictions with athena_rgo_calibrate when observational history exists. Use the returned HIVE/SWARM/PACK/FLOCK/HERD/POD geometry, active-worker limit, role allocation, bounded-neighbor topology, reserve, quorum, inhibition, evaporation and marginal stop threshold.
5 If there are multiple tasks/workers, call athena_collective_allocate so scarce capacity follows demand × capability fit × availability rather than equal participation. If a new schema/interface/bridge is proposed, call athena_bridge_account before building it.
6 Execute maximum reachable useful development now within that collective envelope. Repeated cognition must be searched in CCR and reused/upgraded/compiled rather than re-described.
7 For competing candidates use evidence-sensitive quorum logic: consensus alone cannot promote a claim. Preserve cross-inhibition, contradiction, stop signals, negative memory and stale-attractor evaporation.
8 When a failure/change invalidates descendants, prefer athena_jspace_alarm so transport is compiled from typed JSPACE dependency semantics. Unknown relation types are ignored unless their orientation is explicitly supplied; never manufacture dependency direction.
9 When coordination/duplication pressure is structural, call athena_collective_restructure. A FISSION/FUSE result is advisory until an exact topology transaction is supplied. Apply durable changes through athena_topology_apply with expected-version CAS; if downstream health or RGO degrades, use athena_topology_rollback. Never mutate canonical JSPACE implicitly through the collective control plane.
10 Reinforce successful reusable artifacts/routes with athena_pheromone_reinforce and let age/staleness/contradiction evaporate inherited priority. Before growing the archive, use athena_artifact_lifecycle for KEEP_ACTIVE/KEEP_REFERENCE/DORMANT/QUARANTINE/PRUNE_REFERENCE; pruning never destroys required lineage.
11 Convert material diagnosed failures into athena_failure_antibody_register entries containing detector, repair, evidence and regression/replay references. A future antibody match should reuse the repair and rerun its witness rather than rediscovering the failure from scratch.
12 Measure actual collective outcome after execution. Record predicted versus observed Return-on-Group-Organization with athena_rgo_observe so future organization selection is empirically calibrated instead of self-certifying.
13 Build the actual final visible payload; do not emit a floating draft.
14 Before emission call athena_finalize_output on the exact payload. Include the returned COLLECTIVE coordinate in coordinates when the collective plan materially governed the work. It MUST crystallize the body, derive the header, assemble exact HEADER+BODY bytes, create an emission MID, and coordinate-index the whole visible envelope.
15 Emit exactly the returned visible_text. Do not modify it afterward. Verify the ENV digest when a transport/client boundary may have mutated the bytes.
16 Treat LOOKUP and DERIVATION as different transform classes. Carry KC144/JSPACE/SCALE/LINEAGE/TIME/LIMINAL/CUT_LM/EVIDENCE/COLLECTIVE plus native coordinates whenever lawfully resolved. Preserve UNKNOWN or N/A explicitly.
17 Commit only against current VID/Git HEAD. Collective topology uses its own expected-version CAS; semantic and Git CAS remain authoritative for canonical state. Promote organism-wide laws as global mutations, recompute the changed whole state, and continue MAXDEV.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV crystal cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

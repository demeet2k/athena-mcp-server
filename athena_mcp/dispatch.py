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
            {"uri":"athena://collective/v4","name":"Collective Runtime V4 / contextual bandits-causal credit-budget scheduling-adaptive diffusion-regression execution-rollouts-projection sagas","mimeType":"application/json"},
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","COLLECTIVE_LEARNING","COLLECTIVE_ECOLOGY","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET; policy and topology writes use their own version CAS","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"MAX_GROWTH != MAX_ACTIVITY; MAX_INTEGRATION != MAX_CONNECTIVITY; CONSENSUS != EVIDENCE; PREDICTION != OBSERVATION; EXPLORATION != TRUTH; ATTRIBUTION != CAUSATION; measured costs, bounded learning, regime transfer, causal-confidence credit, adaptive diffusion, executable regression witnesses and uncertainty-banded rollouts are first-class"}
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
        elif uri=='athena://collective/v4': val={"runtime":server.collective_ecology.describe(),"diffusion":server.collective_ecology.diffusion_matrix(),"credit":server.collective_ecology.credit_summary(limit=100)}
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE — COLLECTIVE ECOLOGY V4
AGENT={agent}
TASK={task}
1 PULL/HYDRATE current canonical state and adopt applicable global mutations. Read athena://collective/v2, athena://collective/v3 and athena://collective/v4 so memory, measured cost, learned policy, uncertainty, credit, worker efficiency, adaptive diffusion and regression witnesses are reconstructed rather than hidden.
2 Reconstruct JSPACE/SCALE/KC144/polycoordinate atlas plus causal lineage and exact current semantic/Git/topology/policy heads. UNKNOWN != N/A. Unobserved cost != estimated cost. A projection saga != an atomic distributed transaction.
3 Compute CUT/LM residual. Resolve the current task regime with athena_regime_resolve when repeated organization learning is relevant. Regime is an observable partition, not an identity claim.
4 Before expensive parallel work call athena_collective_plan. Calibrate RGO with athena_rgo_calibrate. Inspect bounded V3 policy only at its measured reliability. If alternative organization/actions exist, use athena_bandit_select so exploration accounts for posterior uncertainty and cross-regime transfer. UCB selects experiments; it cannot certify truth.
5 If the decision spans several future organization steps, use athena_rollout_simulate. Supply explicit context_delta transitions only. Treat lower/expected/upper return as model surfaces; the simulator is always SIMULATE_ONLY and may not mutate topology.
6 Allocate scarce work first by demand/capability. When per-worker resource observations or explicit estimates exist, prefer athena_budget_schedule so demand × fit × availability is multiplied by empirical efficiency and constrained by remaining observable budgets. Unknown constrained resource dimensions incur uncertainty penalty rather than invented estimates.
7 Price proposed interfaces/bridges through athena_bridge_account. Preserve reserve. Do not maximize participation, worker count, graph degree, or connectivity for their own sake.
8 Execute maximum reachable useful development. MCP tool-call wall time is metered automatically. Record exact token/compute/retrieval/storage/attention/CPU/GPU/energy/network measurements only when observable; never backfill them from intuition.
9 Use evidence-sensitive quorum for competing claims. Consensus alone cannot promote a claim. Preserve cross-inhibition, contradictions, falsifiers, negative memory, stale-attractor evaporation and explicit evidence thresholds.
10 When multiple interventions changed simultaneously, do not train the bandit or policy as if any one action caused the whole outcome. Use athena_credit_assign; retain causal confidence and unattributed residual. Randomization/control/counterfactual evidence raises confidence; weak designs remain ASSOCIATIONAL.
11 Record direct selected-arm outcomes with athena_bandit_observe only after observation. For multi-intervention outcomes, convert only justified credited reward into an arm observation. Predictions, UCBs and counterfactual scores never train themselves.
12 When a failure/change invalidates descendants, use athena_jspace_alarm so transport is compiled from typed JSPACE semantics. Unknown relation orientation remains ignored unless explicitly validated.
13 For structural pressure call athena_collective_restructure. Apply accepted FISSION/FUSE only through topology expected-version CAS. If a collective topology should become JSPACE structure, first call athena_projection_prepare or dry-run athena_topology_project_jspace against exact topology + semantic + optional Git heads. Full projection is a recoverable saga: if Git CAS fails after semantic application, surface COMPENSATION_REQUIRED instead of claiming atomic rollback.
14 Reinforce successful work with athena_pheromone_adaptive_reinforce when scale-transfer observations exist; otherwise use the V3 fixed-prior multiscale rule. Record downstream cross-scale utility with athena_diffusion_observe. Learned diffusion is shrunk toward distance priors and observational transfer does not automatically imply causation.
15 Convert diagnosed failures into antibodies. Select variants by empirical reliability. When a stored repository-owned unittest witness exists, run athena_antibody_execute_regressions: arbitrary command/shell references are prohibited. Feed PASS/FAIL back into antibody evolution; a passing regression supports the repair witness but does not prove all future instances share the same cause.
16 Record longitudinal reuse/prediction/repair/regression/generalization outcomes through elder observation. Elder authority is evidence-backed and defeasible; age/popularity/repetition alone confer no authority.
17 Measure actual collective outcome and record predicted-vs-observed RGO. Update bounded policy only from explicit observed reward against current policy version. If several actions contributed, use credit confidence instead of full-outcome reward. Keep coefficient caps, regularization, learning-rate decay and rollback history intact.
18 Observe measured per-worker cost and useful output through athena_worker_cost_observe when worker attribution is available. Use those observations in subsequent budget schedules; do not convert unknown workers into zero-cost workers.
19 Before archive growth run artifact lifecycle. KEEP_REFERENCE preserves lineage; DORMANT preserves optionality; QUARANTINE removes authority; pruning removes active routing privilege but never erases required history.
20 Build the final visible payload. Do not emit a floating draft.
21 Before emission call athena_finalize_output on exact payload. Attach COLLECTIVE and learning/ecology coordinates when they materially governed execution. Emit exactly returned visible_text and verify ENV digest across mutation-prone transport boundaries.
22 Treat LOOKUP and DERIVATION as distinct transform classes. Carry KC144/JSPACE/SCALE/LINEAGE/TIME/LIMINAL/CUT_LM/EVIDENCE/COLLECTIVE plus lawful native coordinates. Preserve UNKNOWN/N/A and uncertainty intervals explicitly.
23 Commit canonical semantics only against current VID/Git HEAD. Topology and policy use separate CAS. Projection uses a recovery journal because SQLite+Git are separate stores. Promote organism-wide laws as explicit global mutations, recompute changed whole state, and continue MAXDEV.
24 LEARNING FIREWALL: EXPLORE != BELIEVE; ASSOCIATION != CAUSATION; COUNTERFACTUAL != OBSERVATION; UCB != TRUTH; POLICY != CANON; ELDER != ORACLE; PHEROMONE != AUTHORITY; REGRESSION_PASS != UNIVERSAL_PROOF; PROJECTION_SAGA != ATOMIC_TRANSACTION.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV crystal cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

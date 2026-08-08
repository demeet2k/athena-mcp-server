from __future__ import annotations
import json, sys, time
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS
from .timebundle import TIME_PROVENANCE
from .collective_science import CollectiveScienceRuntime

def _meter(server,name,started,status):
    try:
        server.collective_learning.record_runtime_usage(name,time.perf_counter()-started,status)
    except Exception:
        pass

def _science(server):
    return CollectiveScienceRuntime(server.store,server.collective,server.collective_growth,server.collective_memory,server.collective_learning,server.collective_ecology)

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
            {"uri":"athena://collective/v5","name":"Collective Runtime V5 / Bayesian calibration-active experiment design-interaction credit-transition dynamics-multiperiod scheduling-Pareto-compensation","mimeType":"application/json"},
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","COLLECTIVE_LEARNING","COLLECTIVE_ECOLOGY","COLLECTIVE_SCIENCE","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET; policy/topology/projection writes retain separate CAS/recovery authority","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"MAX_GROWTH != MAX_ACTIVITY; PREDICTION != OBSERVATION; POSTERIOR != TRUTH; CALIBRATION != MODEL_VALIDITY; EIG != EVIDENCE; INTERACTION != CAUSALITY WITHOUT IDENTIFICATION; TRANSITION_MODEL != WORLD_TRUTH; ROLLOUT != EXECUTION; PARETO_FRONTIER != SINGLE_BEST; SEMANTIC_COMPENSATION != GIT_ROLLBACK"}
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
        elif uri=='athena://collective/v3': val={"runtime":server.collective_learning.describe(),"policy":server.collective_learning.policy_state(),"budget":server.collective_learning.budget_summary(limit=100),"elders":server.collective_learning.elder_rank(limit=20)}
        elif uri=='athena://collective/v4': val={"runtime":server.collective_ecology.describe(),"diffusion":server.collective_ecology.diffusion_matrix(),"credit":server.collective_ecology.credit_summary(limit=100)}
        elif uri=='athena://collective/v5': val={"runtime":_science(server).describe(),"delayed_credit":_science(server).delayed_credit_summary(limit=100),"learned_regime_geometry":_science(server).regime_geometry_resolve({},top_k=10)}
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE — CAUSAL EXPERIMENTAL OS V5
AGENT={agent}
TASK={task}
1 HYDRATE exact canonical state and required global mutations. Read collective V2/V3/V4/V5 resources when organizational memory/learning/science materially govern the task.
2 Reconstruct JSPACE/SCALE/KC144/polycoordinate atlas, lineage, semantic/Git/topology/policy heads, active antibodies/elders, measured budgets, V4 bandit state, and V5 Bayesian/calibration/transition/regime state. UNKNOWN != N/A; unobserved != zero.
3 Compute CUT/LM. Resolve coarse regime and, when history exists, learned regime neighbors. Learned regime geometry controls transfer/routing only; it never changes semantic identity.
4 Maintain explicit live hypotheses for materially uncertain design choices. When multiple experiments could distinguish them, use athena_experiment_design. Prefer expected information gain per feasible cost/risk while respecting ethics. DESIGN_ONLY never becomes evidence.
5 For action/organization reward prediction, use the V5 full-covariance posterior when correlated feature uncertainty matters; inspect empirical interval calibration. POSTERIOR != TRUTH and COVERAGE_CALIBRATION != MODEL_VALIDITY, especially under regime/distribution shift.
6 Preserve V4 UCB for exploration selection, but never feed UCB/counterfactual/rollout predictions back as observations. Only measured outcomes update V4/V5 learning state.
7 When alternatives remain genuinely multiobjective, call athena_pareto_frontier before forcing scalar collapse. Retain non-dominated tradeoffs and use robust interval dominance when uncertainty materially changes selection.
8 Plan scarce work with the V4 budget scheduler for one-step allocation or athena_schedule_multiperiod when dependencies, durations, deadlines or horizon budgets matter. The V5 scheduler is bounded beam search and carries no global optimality proof.
9 Execute maximum reachable useful development and meter lawful resource dimensions. Preserve reserve and reversibility. Unknown constrained worker cost incurs uncertainty rather than becoming free capacity.
10 Falsify/verify. Use stored antibodies and repository-owned witnesses. Use athena_witness_cell when stronger process/resource constraints help, but do not call it OS-hermetic; native/hostile execution still requires stronger containment.
11 After observation, separate direct effects from interactions. For pair interactions use athena_interaction_credit and require all factorial cells; missing contrasts remain UNIDENTIFIED. Do not relabel numerical interactions as causal without sufficient design confidence.
12 For outcomes arriving many cycles after an action, use athena_delayed_credit_record with explicit causal confidence and temporal discount. Temporal proximity/delay alone never identifies cause.
13 Feed only justified observed/credited reward into Bayesian/bandit/policy updates. Retain pre-update predictions so interval calibration remains out-of-sample rather than measuring itself after learning the answer.
14 Record observed action-conditioned context changes through athena_transition_observe. Use athena_transition_predict and athena_rollout_learned only as shrinkage model surfaces. Rollouts are SIMULATE_ONLY and cannot create their own transition observations.
15 Update worker costs, RGO, diffusion/pheromone, elder evidence and antibody outcomes from measured consequences. Routing utility remains separate from causal dependency.
16 Apply structural topology changes only through topology CAS. Projection to JSPACE requires its V4 saga/preflight. If a projection must be semantically reversed, use athena_projection_compensate against the exact current semantic head; it may retract only active edges owned by that projection. Git history is a separate compensation surface.
17 Before archive growth run artifact lifecycle. Preserve lineage, optionality, negative memory and failure witnesses.
18 Build the exact visible payload; then finalize and verify it. Attach COLLECTIVE, COLLECTIVE_LEARNING, COLLECTIVE_ECOLOGY, and COLLECTIVE_SCIENCE fibers only when those states materially governed execution.
19 Commit semantics only under their authority surfaces. Promote organism-wide laws explicitly; recompute whole state and reattack residuals.
20 SCIENCE FIREWALL: POSTERIOR != TRUTH; CALIBRATION != VALIDITY; EIG != EVIDENCE; DESIGN != RESULT; INTERACTION != CAUSATION WITHOUT IDENTIFICATION; DELAY != CAUSATION; TRANSITION_MODEL != WORLD; ROLLOUT != EXECUTION; BOUNDED_SCHEDULE != GLOBAL_OPTIMUM; WITNESS_CELL != HERMETIC_SANDBOX; LEARNED_REGIME != IDENTITY; PARETO_FRONTIER != SINGLE_BEST; SEMANTIC_COMPENSATION != GIT_ROLLBACK.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV causal experimental cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

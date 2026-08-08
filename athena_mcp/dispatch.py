from __future__ import annotations
import json, sys, time
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS
from .timebundle import TIME_PROVENANCE
from .collective_science import CollectiveScienceRuntime
from .collective_discovery import CollectiveDiscoveryRuntime
from .collective_dual_control import CollectiveDualControlRuntime

def _meter(server,name,started,status):
    try:
        server.collective_learning.record_runtime_usage(name,time.perf_counter()-started,status)
    except Exception:
        pass

def _science(server):
    return CollectiveScienceRuntime(server.store,server.collective,server.collective_growth,server.collective_memory,server.collective_learning,server.collective_ecology)

def _discovery(server):
    return CollectiveDiscoveryRuntime(_science(server))

def _dual(server):
    return CollectiveDualControlRuntime(_discovery(server))

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
            {"uri":"athena://collective/v6","name":"Collective Runtime V6 / nonlinear-OOD-experiment generation-causal ID-higher interactions-stochastic control-certificates-science shadows","mimeType":"application/json"},
            {"uri":"athena://collective/v7","name":"Collective Runtime V7 / uncertainty decomposition-prequential bands-causal skeleton-state models-scenarios-dual control-frontdoor-IV-replication independence","mimeType":"application/json"},
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","COLLECTIVE_LEARNING","COLLECTIVE_ECOLOGY","COLLECTIVE_SCIENCE","COLLECTIVE_DISCOVERY","COLLECTIVE_DUAL_CONTROL","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET; policy/topology/projection writes retain separate CAS/recovery authority; V7 diagnostic/planning state has no independent canonical mutation authority","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"MAX_GROWTH != MAX_ACTIVITY; PREDICTION != OBSERVATION; POSTERIOR != TRUTH; OOD != FALSEHOOD; GENERATED_EXPERIMENT != RESULT; ASSOCIATION_SKELETON != CAUSAL_DAG; BACKDOOR/FRONTDOOR/IV identification is conditional on supplied graph assumptions; STATE_MODEL != WORLD; SCENARIO != FUTURE; DUAL_CONTROL_PROXY != EXACT_BAYES_CONTROL; REPLICATION_INDEPENDENCE_ESTIMATE != PROOF; REPLICATION_DESIGN != RESULT"}
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
        elif uri=='athena://collective/v6': val={"runtime":_discovery(server).describe()}
        elif uri=='athena://collective/v7': val={"runtime":_dual(server).describe()}
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE — DUAL CONTROL + CONDITIONAL CAUSAL DISCOVERY V7
AGENT={agent}
TASK={task}
1 HYDRATE exact canonical state and required global mutations. Read only the collective layers that materially govern the task; maximum capability does not require maximum machinery on every task.
2 Reconstruct JSPACE/SCALE/KC144/polycoordinate lineage and exact semantic/Git/topology/policy heads. UNKNOWN != N/A; UNKNOWN_COST != ZERO_COST; predictive or science-shadow state never outranks canonical authority.
3 Compute CUT/LM and choose the minimum sufficient runtime depth. V1 organization, V4 experiment selection, V5 science, V6 discovery, and V7 dual-control tools are hierarchical options rather than mandatory ceremony.
4 When inherited predictive confidence matters, inspect V6 OOD and optionally V7 athena_uncertainty_decompose. Treat aleatoric/epistemic/shift/calibration components as diagnostic proxies, not uniquely identifiable physical sources.
5 When enough retained pre-update errors exist, athena_prequential_interval may add empirical sequential coverage evidence. If history is insufficient, preserve that insufficiency; PREQUENTIAL_BAND != DISTRIBUTION_FREE_CONFORMAL_GUARANTEE under arbitrary shift.
6 If observational data suggests structure but no trusted DAG exists, athena_causal_skeleton_discover may generate an undirected association skeleton/v-structure hypotheses. Do not promote this to a causal DAG. Use it to generate competing graph hypotheses or experiments.
7 Maintain explicit live causal hypotheses. Use V6 back-door or V7 athena_causal_identify_extended for BACKDOOR/FRONTDOOR/INSTRUMENT checks only against an explicit supplied DAG and assumptions. Identification is conditional; latent-confounding risk blocks promotion.
8 Generate/rank experiments with V5/V6 when useful. Generated designs and replication designs are DESIGN_ONLY. Preserve ethics, feasibility, cost, risk and missing-likelihood boundaries.
9 For state dynamics, prefer V7 athena_state_transition_model when current state materially changes expected action deltas. It derives ridge state-dependent multivariate dynamics only from actual V5 before/after observations. Unseen actions remain unmodeled.
10 Use athena_scenario_evaluate when lower-tail trajectory risk matters. Scenario trees are finite moment approximations and SIMULATE_ONLY; they are not observed futures or exact contingent policies.
11 Use athena_dual_control_plan when an action's information value materially competes with immediate control reward. Score control + information - risk, but treat the result as a bounded proxy. Execute only the first authorized action, observe reality, record, and replan.
12 Preserve multiobjective options and exact scheduling certificate scope using V5/V6 Pareto/scheduler laws. Do not collapse plural values or incomplete constraint models into false optimality.
13 Query antibodies and science-shadow claims before expensive repetitions. Use V7 athena_replication_independence to detect correlated witness families; effective-N is metadata-based evidence geometry, not formal statistical independence.
14 When additional evidence is needed, athena_replication_design may choose a diverse replication/falsifier candidate by expected power, novelty, feasibility, cost and risk. A selected design becomes evidence only after independent execution and measurement.
15 Execute maximum reachable useful work and meter consequences. Preserve reserve, reversibility and negative evidence. Model/planning calls never train themselves.
16 After observation, perform justified direct/interaction/delayed credit and update Bayesian/bandit/policy/transition/OOD/reference state only from actual observations. Preserve residual and failed-model evidence.
17 Update worker cost, RGO, diffusion/pheromone, elder and immune state only from measured downstream consequences. Routing usefulness remains distinct from causal truth.
18 Apply topology and projection mutations only through their established CAS/recovery surfaces. V7 adds no shortcut around semantic authority.
19 Finalize exact visible payload and verify it. Attach COLLECTIVE_DUAL_CONTROL=<UD,PI,CG,SM,SC,DC,CX,RI,RD,L> only when V7 materially governed execution; otherwise omit it.
20 V7 FIREWALL: UNCERTAINTY_DECOMPOSITION != UNIQUE_TRUTH; PREQUENTIAL_BAND != UNIVERSAL_COVERAGE; ASSOCIATION_SKELETON != CAUSAL_DAG; STATE_MODEL != WORLD; SCENARIO_TREE != FUTURE; DUAL_CONTROL_PROXY != EXACT_BAYES_CONTROL; FRONTDOOR/IV_CHECK != CAUSAL_TRUTH OUTSIDE SUPPLIED DAG; ESTIMATED_REPLICATION_INDEPENDENCE != PROOF; REPLICATION_DESIGN != RESULT.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV dual-control/conditional-causal-discovery cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

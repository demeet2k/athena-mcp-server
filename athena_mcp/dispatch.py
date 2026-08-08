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
from .collective_belief import CollectiveBeliefRuntime
from .collective_inference import CollectiveInferenceRuntime

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

def _belief(server):
    return CollectiveBeliefRuntime(_dual(server))

def _inference(server):
    return CollectiveInferenceRuntime(_belief(server))

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
            {"uri":"athena://collective/v8","name":"Collective Runtime V8 / finite beliefs-EVI-belief dual control-effect estimates-bootstrap graph-contingent policy-spectral evidence diversity","mimeType":"application/json"},
            {"uri":"athena://collective/v9","name":"Collective Runtime V9 / Gaussian beliefs-EVPI-EVSI-multistage belief policies-AIPW-robustness-partial graphs-evidence dependence","mimeType":"application/json"},
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","COLLECTIVE_LEARNING","COLLECTIVE_ECOLOGY","COLLECTIVE_SCIENCE","COLLECTIVE_DISCOVERY","COLLECTIVE_DUAL_CONTROL","COLLECTIVE_BELIEF","COLLECTIVE_INFERENCE","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET; policy/topology/projection writes retain separate CAS/recovery authority; V7-V9 belief, estimator, graph-hypothesis, scenario and planning state has no independent canonical mutation authority","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"PREDICTION != OBSERVATION; POSTERIOR/BELIEF != TRUTH; GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES; EVPI/EVSI are model-conditional Monte Carlo estimates; AIPW != IDENTIFICATION_PROOF; HEURISTIC_PARTIAL_GRAPH != PAG/FCI THEOREM; EVIDENCE_DEPENDENCE_MODEL != FORMAL_INDEPENDENCE; PLAN != EXECUTION"}
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
        elif uri=='athena://collective/v8': val={"runtime":_belief(server).describe()}
        elif uri=='athena://collective/v9': val={"runtime":_inference(server).describe()}
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE — CONTINUOUS INFERENCE + ROBUST CAUSAL DECISION VALUE V9
AGENT={agent}
TASK={task}
1 HYDRATE exact canonical state and choose the minimum sufficient runtime depth. V9 is optional high-depth machinery, not default ceremony.
2 Preserve identity/authority: model beliefs, simulations, estimators and graph hypotheses never mutate canon without the existing semantic CAS/evidence path.
3 Use V8 finite belief/EVI when the live uncertainty is a small discrete model set. Use V9 Gaussian belief only when a finite-dimensional continuous linear parameter posterior is materially useful.
4 Update athena_gaussian_belief_observe only from an explicit observed target with a complete feature vector. EVPI, EVSI and planning calls are read-only.
5 Use athena_decision_evpi as an approximate upper value ceiling under the declared Gaussian utility model; retain Monte-Carlo error and seed. EVPI is not universal truth value.
6 Use athena_decision_evsi to price a specific linear measurement design. It remains DESIGN_ONLY; ethics, cost, risk and feasibility are independent gates.
7 Use athena_belief_policy_multistage only for small finite model/outcome horizons <=3. It is a contingent design tree, not execution history or a general POMDP solution.
8 Keep causal identification separate from estimation. Use athena_causal_aipw only for binary treatment under explicit identification/positivity/consistency assumptions. AIPW returns an estimate, influence-function SE and interval; declared latent confounding fails closed.
9 Use athena_causal_robustness as an observed-specification perturbation diagnostic only; leave-one-adjustment sensitivity is not a hidden-confounding bound.
10 Use athena_structure_partial to preserve o-o endpoint uncertainty around stable association hypotheses. HEURISTIC_PARTIAL_GRAPH != PAG/FCI/CPDAG theorem and never mutates JSPACE.
11 Use athena_evidence_dependence_probability only with a visible declared metadata model. Its probabilities are model outputs, not formal independence facts; missing metadata does not imply independence.
12 Preserve V5-V8 OOD, prequential, EVI, Pareto, scenario, replication and evidence firewalls; higher numeric resolution does not grant higher semantic authority.
13 Execute only authorized real actions/experiments, then observe and explicitly update the corresponding model/belief/evidence state. Plans never train themselves.
14 Finalize/verify exact visible output and attach COLLECTIVE_INFERENCE=<GB,EVPI,EVSI,MP,AIPW,RB,PG,ED,L> only when V9 materially governed execution.
15 V9 FIREWALL: GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES; MONTE_CARLO_EVPI_EVSI != EXACT_VALUE; MULTISTAGE_FINITE_BELIEF_POLICY != GENERAL_POMDP; AIPW_ESTIMATE != IDENTIFICATION_PROOF; ROBUSTNESS_PERTURBATION != HIDDEN_CONFOUNDING_BOUND; HEURISTIC_PARTIAL_GRAPH != PAG_OR_FCI_THEOREM; DEPENDENCE_PROBABILITY_MODEL != FORMAL_INDEPENDENCE.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV continuous-inference/robust-causal cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

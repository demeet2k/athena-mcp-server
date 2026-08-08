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
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","COLLECTIVE_LEARNING","COLLECTIVE_ECOLOGY","COLLECTIVE_SCIENCE","COLLECTIVE_DISCOVERY","COLLECTIVE_DUAL_CONTROL","COLLECTIVE_BELIEF","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET; policy/topology/projection writes retain separate CAS/recovery authority; V7/V8 belief, estimator, structure-bootstrap, scenario and planning state has no independent canonical mutation authority","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"MAX_GROWTH != MAX_ACTIVITY; PREDICTION != OBSERVATION; POSTERIOR/BELIEF != TRUTH; OOD != FALSEHOOD; EIG/EVI DESIGN != EVIDENCE; ASSOCIATION/BOOTSTRAP STABILITY != CAUSAL DAG; CAUSAL ESTIMATE != IDENTIFICATION PROOF; BACKDOOR/FRONTDOOR/IV identification is conditional on supplied graph assumptions; STATE_MODEL != WORLD; SCENARIO/CONTINGENT POLICY != OBSERVED HISTORY; DUAL_CONTROL/BELIEF_CONTROL != EXACT BAYES-ADAPTIVE CONTROL; EVIDENCE EFFECTIVE-RANK != INDEPENDENCE PROOF"}
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
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE — FINITE BELIEF STATE + DECISION VALUE V8
AGENT={agent}
TASK={task}
1 HYDRATE exact canonical state and applicable global mutations. Select the minimum sufficient runtime depth; maximum capability does not require maximum machinery on every task.
2 Reconstruct JSPACE/SCALE/KC144/polycoordinate lineage and exact semantic/Git/topology/policy heads. UNKNOWN != N/A; UNKNOWN_COST != ZERO_COST; model belief never outranks canonical semantic authority.
3 Compute CUT/LM. Use V1–V7 when sufficient. Enter V8 only when explicit competing model beliefs, decision value of information, assumption-scoped effect estimation, structure stability, contingent action design or evidence redundancy materially changes the next decision.
4 For explicit model uncertainty, register/read `athena_belief_register` / `athena_belief_state`. Belief probabilities are a finite model state, not canonical truth.
5 Update belief only after an actual declared observation with `athena_belief_observe`, supplying a likelihood for every model and retaining an evidence reference. Planning/EVI/contingent-policy calls never update belief themselves.
6 When the purpose of an experiment is downstream decision improvement, use `athena_decision_evi` rather than entropy alone. EVI = expected optimal post-information utility minus current optimal utility, under the supplied finite model/action/outcome assumptions. DESIGN_ONLY; ethics, cost, risk and feasibility remain separate gates.
7 Use `athena_belief_dual_control` only when immediate utility, future decision utility and information value genuinely trade off. It is a depth-1 finite-belief proxy, PLAN_ONLY, not a Bayes-adaptive POMDP solution.
8 Use V6/V7 causal identification before causal estimation. `athena_causal_effect_estimate` may estimate BACKDOOR_LINEAR, IV_WALD or FRONTDOOR_LINEAR effects only under explicit assumptions. Estimation does not establish identification; latent-confounding risk fails closed.
9 Use `athena_causal_structure_bootstrap` to measure resampling stability of V7 association-skeleton/v-structure hypotheses. Bootstrap support is procedural stability, not causal edge probability, FCI/PAG truth or permission to mutate JSPACE.
10 Use `athena_contingent_policy` when one experiment has discrete outcomes that would justify different next actions. Returned outcome→posterior→action branches are DESIGN_ONLY and do not become observed history until an outcome is actually measured.
11 Use `athena_evidence_spectral` to detect redundant witness pipelines. Effective-N and participation ratio are metadata-similarity diagnostics; missing metadata never creates independence and spectral diversity is not a formal statistical-independence theorem.
12 Preserve V7 OOD/prequential/dual-control boundaries. A finite belief can coexist with OOD, state-dynamic and scenario uncertainty; do not collapse all uncertainty into one scalar when the distinction affects action.
13 Preserve V5/V6 Pareto and scheduling scope. A belief-aware decision may still have plural objectives and resource constraints; EVI does not authorize hidden scalarization or unmeasured cost.
14 Execute the first authorized real action only after design/authority gates. Observe real outcomes, meter consequences and update the appropriate belief/model/evidence state explicitly.
15 Query antibodies and science shadows before repeating expensive work. Replication counts, effective-N and spectral rank route evidence acquisition but never silently promote or delete canonical claims.
16 After observations, perform justified causal/direct/interaction/delayed credit and update Bayesian/bandit/policy/transition/OOD/belief state only from actual measurements. Preserve failed hypotheses and residual uncertainty.
17 Apply topology/JSPACE/Git changes only through established CAS/recovery/compensation surfaces. V8 adds no semantic mutation shortcut.
18 Run lifecycle and preserve lineage, negative evidence, model history and effect-estimator assumptions.
19 Finalize and verify the exact visible payload. Attach COLLECTIVE_BELIEF=<BS,EVI,BD,CE,CB,CP,ER,L> only when V8 materially governed execution; omit it otherwise.
20 V8 FIREWALL: BELIEF_POSTERIOR != CANONICAL_TRUTH; LIKELIHOOD_MODEL != OBSERVATION; EVI_DESIGN != RESULT; BELIEF_DUAL_CONTROL != EXACT_BAYES_ADAPTIVE_POMDP; CAUSAL_ESTIMATE != IDENTIFICATION_PROOF; BOOTSTRAP_STABILITY != CAUSAL_EDGE_PROBABILITY; CONTINGENT_POLICY != EXECUTION_HISTORY; SPECTRAL_EVIDENCE_DIVERSITY != FORMAL_INDEPENDENCE.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV finite-belief/decision-value cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

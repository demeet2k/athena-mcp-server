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

def _meter(server,name,started,status):
    try:
        server.collective_learning.record_runtime_usage(name,time.perf_counter()-started,status)
    except Exception:
        pass

def _science(server):
    return CollectiveScienceRuntime(server.store,server.collective,server.collective_growth,server.collective_memory,server.collective_learning,server.collective_ecology)

def _discovery(server):
    return CollectiveDiscoveryRuntime(_science(server))

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
        ]; return server.result(mid,{"resources":rs})
    if method=='resources/read':
        uri=params.get('uri'); c=server.core
        if uri=='athena://manifest': val={"name":"ATHENA","protocol":PROTOCOL_VERSION,"layers":["GIT_LEDGER","CCR","JSPACE","SCALE","KC144","POLYCOORDINATE_ATLAS","MATH_REGISTRY","COLLECTIVE_RUNTIME","COLLECTIVE_GROWTH","COLLECTIVE_MEMORY","COLLECTIVE_LEARNING","COLLECTIVE_ECOLOGY","COLLECTIVE_SCIENCE","COLLECTIVE_DISCOVERY","RUNTIME"],"identity":"SID!=OID!=MID!=VID!=CID!=EID!=CRYS","mutation":"EXPECTED_VID==CURRENT_VID else STALE_TARGET; policy/topology/projection writes retain separate CAS/recovery authority","output_law":"VISIBLE_OUTPUT -> FINALIZE_OUTPUT -> ENV(HEADER+BODY) with exact addressable emission manifestation","transform_law":"LOOKUP != DERIVATION; holonomy only promotes all-derivational loops","collective_law":"MAX_GROWTH != MAX_ACTIVITY; PREDICTION != OBSERVATION; POSTERIOR != TRUTH; OOD != FALSEHOOD; GENERATED_EXPERIMENT != RESULT; BACKDOOR_ID is conditional on supplied DAG; HIGHER_ORDER_CONTRAST != CAUSALITY WITHOUT IDENTIFICATION; TRANSITION_MODEL != WORLD_TRUTH; MPC_PLAN != EXECUTION; CERTIFICATE scope must be explicit; HERMETIC_CAPSULE fails closed; PARETO_EXPERIMENT != SINGLE_BEST; REPLICATION_STATE != CANON"}
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
        else:return server.error(mid,-32002,"Resource not found",{"uri":uri})
        return server.result(mid,{"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list': return server.result(mid,{"prompts":PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev': return server.error(mid,-32602,"Unknown prompt")
        a=params.get('arguments') or {}; task=a.get('task',''); agent=a.get('agent','ATHENA')
        text=f"""ATHENA MAXDEV CRYSTAL CYCLE — ACTIVE DISCOVERY + STOCHASTIC CONTROL V6
AGENT={agent}
TASK={task}
1 HYDRATE exact canonical state and required global mutations. Read collective V2/V3/V4/V5/V6 resources when organizational memory, learning, science, OOD, causal identification or control state materially govern the task.
2 Reconstruct JSPACE/SCALE/KC144/polycoordinate atlas, lineage and exact semantic/Git/topology/policy heads. UNKNOWN != N/A; UNKNOWN_COST != ZERO_COST; model state never outranks canonical authority.
3 Compute CUT/LM. Resolve coarse/learned task regimes. When inherited model history is used, inspect OOD pressure first; distribution shift downgrades transfer/calibration authority but does not itself falsify a claim.
4 For nonlinear reward structure use athena_nonlinear_predict/observe only as the declared degree-2 basis model. Do not label it GP/neural/universal inference. Prediction never trains itself.
5 Maintain explicit live hypotheses. If useful candidate experiments are not already supplied, generate them only from a declared finite factor/effect space with athena_experiment_generate. Rank by information gain/cost/risk/ethics. Generated designs are DESIGN_ONLY.
6 When making a causal claim from an explicit DAG, call athena_causal_identify. Treat back-door identification as conditional on graph correctness, observed variables and causal-sufficiency assumptions. Latent-confounding uncertainty blocks promotion.
7 For interacting interventions use V5 pairwise or V6 higher-order factorial contrasts. Require every 2^k cell; missing cells remain UNIDENTIFIED. Numerical contrast is not causal interaction without identifying design.
8 Preserve multiobjective tradeoffs. Use V5 frontier for static tradeoffs and athena_pareto_bandit_select when uncertainty on the possible frontier should guide the next experiment. Selection for measurement does not create a single universal ordering.
9 Plan immediate resources with V4, multiperiod heuristic schedules with V5, or athena_schedule_certified for small fully declared finite models. Exact certification is allowed only when exhaustive enumeration completes and every constrained cost dimension is declared.
10 Execute maximum reachable useful work and measure consequences. Preserve reserve/reversibility. Unknown resource dimensions remain explicit.
11 Store real before/after organizational context transitions only after execution. Use athena_transition_distribution for multivariate empirical uncertainty and athena_mpc_plan for receding-horizon planning. Execute only the first authorized action, observe reality, then replan. MPC never self-trains.
12 Query antibodies and science-shadow claims before repeating expensive tests. Use athena_witness_capsule only when stronger OS namespace isolation is requested; if bubblewrap is unavailable it must fail closed rather than silently falling back.
13 Record replication/falsification witnesses with explicit independence keys. REPLICATED_SUPPORT/FALSIFICATION_SIGNAL/CONTESTED are science-shadow evidence states; they do not silently rewrite canonical semantic objects.
14 After measured outcome, perform justified direct/interaction/delayed credit and update Bayesian/bandit/policy/transition state only from actual observations. Preserve residual uncertainty and calibration witnesses.
15 Update worker cost, RGO, diffusion/pheromone, elder and immune state from measured downstream consequences. Routing utility remains distinct from causal dependency.
16 Apply topology changes only under topology CAS. Projection and semantic compensation retain V4/V5 recovery laws; Git remains a separate causal store.
17 Run artifact lifecycle before archive growth. Preserve negative evidence, falsifiers, lineage and supersession history.
18 Build exact visible payload; finalize and verify. Attach COLLECTIVE, COLLECTIVE_LEARNING, COLLECTIVE_ECOLOGY, COLLECTIVE_SCIENCE and COLLECTIVE_DISCOVERY fibers only when materially governing execution.
19 Commit only under the relevant authority surfaces. Promote organism-wide laws explicitly and reattack remaining uncertainty rather than declaring residuals solved by adjacency.
20 DISCOVERY FIREWALL: NONLINEAR_BASIS != UNIVERSAL_INFERENCE; OOD != FALSEHOOD; GENERATED_EXPERIMENT != RESULT; BACKDOOR_SET != CAUSAL_TRUTH OUTSIDE SUPPLIED DAG; HIGHER_ORDER_CONTRAST != CAUSATION; STOCHASTIC_MODEL != WORLD; MPC_PLAN != EXECUTION; CERTIFIED_SCHEDULE != UNIVERSAL_OPTIMUM; HERMETIC_CAPSULE != KERNEL_SECURITY_PROOF; PARETO_EXPERIMENT != SINGLE_BEST; REPLICATION_STATE != CANON.
"""
        return server.result(mid,{"description":"Whole-system MAXDEV active discovery/control cycle","messages":[{"role":"user","content":{"type":"text","text":text}}]})
    return server.error(mid,-32601,"Method not found")

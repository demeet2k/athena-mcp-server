from __future__ import annotations

from typing import Any,Dict

UNIFIED_MANIFEST_VERSION='ATHENA.RUNTIME.UNIFIED.7'

LAYERS=[
 'CCR','JSPACE','SCALE','KC144','POLYCOORDINATE_ATLAS','CRYSTAL_OUTPUT_ABI',
 'COLLECTIVE_RUNTIME_V1','COLLECTIVE_GROWTH_V1','COLLECTIVE_MEMORY_V2','COLLECTIVE_LEARNING_V3','COLLECTIVE_ECOLOGY_V4','COLLECTIVE_SCIENCE_V5','COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11',
 'AOR_DECISION_CORTEX','AOR.3','BRANCH_EVOLUTION','AUTHORITY_Y1','EQ.1','SX.1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1',
 'AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','STARTUP.1','SURFACE.2','COMPOSITION.2','PROMOTION.2',
 'GIT_LEDGER','SOURCE_RETURN',
]

INVARIANTS=[
 'UNKNOWN != 0 and UNKNOWN != N/A','KNOWN != COMPARABLE','consensus != evidence','pheromone/reuse/popularity != evidence != Y authority',
 'authority != confidence != truth probability','planning != execution','attempted write != verified persistence',
 'claimed test requires procedure+observation+result+witness','claimed persistence requires commit+receipt+verify',
 'reachability/navigation closure != logical or causal proof','HUG plan/packet integrity != semantic QHUG execution/replay',
 'AOR chooses WHAT is developmentally eligible; Collective organizes HOW capacity is assigned',
 'FIELD generated candidate = UNMEASURED; explicit metric/routing conflict = CONFLICT and non-rankable','hibernate != erase',
 'semantic VID CAS != Git HEAD CAS != topology version CAS',
 'caller-supplied CI/smoke attestation != externally verified promotion qualification',
 'PROMOTION.2 ATTESTED_READY != QUALIFIED; QUALIFIED requires a host-internal trusted verifier receipt bound to the exact head and CI/smoke refs',
 'V3 policy/elder/runtime-usage learning != evidence or canonical authority','V4 UCB/counterfactual/credit/diffusion != observation and != causal proof without identification',
 'V5 POSTERIOR != TRUTH; CALIBRATION != MODEL_VALIDITY; EIG != EVIDENCE; ROLLOUT != EXECUTION; PARETO_FRONTIER != SINGLE_BEST',
 'V6 OOD/nonlinear/causal/scheduling/discovery outputs remain model-conditional; causal identification is conditional on supplied DAG/assumptions',
 'V7 uncertainty decomposition proxies != physical decomposition; prequential interval != distribution-free coverage guarantee; causal skeleton != DAG',
 'V7 scenario tree != future; DUAL_CONTROL_PROXY_PLAN_ONLY != exact Bayesian belief-state dual control and != execution',
 'V8 BELIEF_POSTERIOR != CANONICAL_TRUTH; EVI/DESIGN != RESULT; belief dual-control/contingent policy != execution history',
 'V8 linear causal estimate != identification proof; bootstrap association stability != causal-edge probability; spectral evidence diversity != formal independence',
 'V9 GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES; MONTE_CARLO_EVPI_EVSI != EXACT_ANALYTIC_VALUE',
 'V9 multistage finite-belief policy != general POMDP; AIPW estimate != identification proof; robustness perturbation != hidden-confounding bound',
 'V9 heuristic partial graph != FCI/PAG/CPDAG theorem; dependence-probability model != formal evidence independence',
 'V10 FIXED_KERNEL_GP != GENERAL_WORLD_TRUTH; GP prediction != observation and never self-trains',
 'V10 BOUNDED_PC_STABLE != FCI_OR_HIDDEN_CONFOUNDER_DISCOVERY; PC graph hypothesis != canonical JSPACE mutation',
 'V10 TMLE estimate != identification proof; E-value != universal hidden-confounding bound',
 'V10 finite POMDP certificate != infinite-horizon or real-world optimality; learned dependence model != formal independence proof',
 'V11 marginal-likelihood optimum != true kernel; GP decision EVSI != observation and cannot self-train',
 'V11 supplied-DAG latent projection != data-discovered PAG and does not mutate canonical JSPACE',
 'V11 stacked TMLE != super-learner theorem; RR bias-factor surface != universal hidden-confounding bound',
 'V11 finite-model BAPOMDP != general Bayes-adaptive control; node truncation removes exact certification',
 'V11 Laplace dependence interval != calibrated coverage guarantee and interval reads cannot create labels',
 'athena_claim_* = Y1 canonical authority; athena_discovery_claim_* = V6-V11 science-shadow replication/falsification metadata; namespaces must never alias',
]

CYCLE='HYDRATE -> RECONRUN/OMEGA -> MEMORY -> EXTRACT -> RETRIEVE -> HUG -> GAP -> FIELD -> MEASURE -> AUTHORITY/AOR -> COLLECTIVE(V1-V11) -> EXECUTE -> VERIFY -> LEARN -> SUCCESSOR -> COMPLETE'
BRAID_LAW='AOR chooses developmental frontier/WHAT; Collective V1-V11 organizes HOW scarce execution/science/control/inference/adaptation capacity is used; Y1 governs canonical claim authority; EQ1 governs witnessed collapse; consensus/pheromone/reward are never typed authority or evidence by themselves; model posterior/replication shadow are also never typed authority or evidence by themselves; caller-bound CI/smoke packets are not trusted external verification.'


def build_unified_manifest(server)->Dict[str,Any]:
    dev=server.aor_development;integrity=dev.integrity;schema=integrity.state_foundation.schema.status();startup=integrity.startup.evaluate(False);git=server.git.status()
    return {
        'artifact':UNIFIED_MANIFEST_VERSION,'artifact_compat':['ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2','ATHENA.RUNTIME.UNIFIED.3','ATHENA.RUNTIME.UNIFIED.4','ATHENA.RUNTIME.UNIFIED.5','ATHENA.RUNTIME.UNIFIED.6'],'role':'live machine-readable runtime architecture projection','runtime_class':type(server).__name__,
        'layers':list(LAYERS),'navigation':'KC144 <-> SCALE <-> JSPACE <-> AOR <-> Collective(V1-V11) <-> Git/MCP <-> Source/RETURN','cycle':CYCLE,'invariants':list(INVARIANTS),'braid_law':BRAID_LAW,
        'identity_law':'SID != OID != MID != VID != CID != EID != CRYS != ENV != AORRUN != RAGRUN != EXTRUN != EXTTASK != EXTRES != HUGIMPL != HUGINV != GAPRUN != FIELDRUN != TRANSPORTRUN != CYCLE != CYCLEEV != PROMRUN != MIGRUN != OMEGA != RECONRUN',
        'claim_namespace_law':'athena_claim_* is canonical Y1 authority; athena_discovery_claim_* is V6-V11 science-shadow/evidence state; no RPC-name aliasing or implicit promotion/demotion is permitted',
        'cas_law':'CAS_OMEGA = CAS_semantic(VID) x CAS_git(HEAD) x CAS_topology(version); staleness in one domain must not mutate the others',
        'schema':{'ledger_version':schema['version'],'current':schema['current_db_schema_version'],'target':schema['target_db_schema_version'],'up_to_date':schema['up_to_date']},
        'startup':{'version':startup['version'],'status':startup['status'],'gates':startup['gates']},'git':git,
        'organs':{
            'collective':{
                'runtime_v1':server.collective.describe(),'growth_v1':server.collective_growth.describe(),'memory_v2':server.collective_memory.describe(),
                'learning_v3':server.collective_learning.describe(),'ecology_v4':server.collective_ecology.describe(),
                'science_v5':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'posterior/calibration/EIG/transition/rollout surfaces remain model-conditional'},
                'discovery_v6':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'OOD/nonlinear/causal/discovery/shadow-claim surfaces never self-promote into Y1 authority'},
                'dual_control_v7':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'uncertainty decomposition, causal skeleton, state-dependent transition/scenario/dual-control, extended identification and replication geometry remain diagnostic/model/science-shadow surfaces'},
                'belief_v8':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'finite belief, EVI, belief-control, effect-estimate, bootstrap graph, contingent-policy and spectral-evidence surfaces remain model/science-shadow state'},
                'inference_v9':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'Gaussian belief, EVPI/EVSI, multistage policy, AIPW/robustness, partial-graph and dependence-probability surfaces remain model-conditional state'},
                'probabilistic_v10':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'fixed-kernel GP, bounded PC-stable, TMLE, E-value, finite POMDP and empirically fitted evidence-dependence surfaces remain model/assumption-scoped state'},
                'adaptive_v11':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'GP hyperfit/EVSI, supplied-DAG latent projection, stacked TMLE, RR sensitivity, finite-model BAPOMDP and dependence intervals remain bounded model/assumption-scoped state'},
            },
            'aor':server.orchestration.benchmark(),'development':dev.benchmark(),
        },
        'unresolved':[
            {'id':'QHUG_SEMANTICS','status':'UNRESOLVED_UNLESS_REGISTERED_AND_WITNESSED','boundary':'HUG.ABI.1 remains operational/fail-closed without inventing canonical QHUG equations or six-parameter semantics'},
            {'id':'STRONGER_CLOSURE','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'GAP.1 implements witnessed directed reachability only; logical/causal/deductive closure require separately registered sound semantics'},
            {'id':'MODEL_TO_AUTHORITY_BRIDGE','status':'EXPLICIT_WITNESS_REQUIRED','boundary':'V3-V11 predictions, beliefs, estimates, experiments, discovery claims, replication diagnostics and control plans cannot enter Y1/AOR evidence lanes without explicit observed/witnessed transport and authority gating'},
            {'id':'GENERAL_BELIEF_CONTROL','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V8-V11 belief/control is bounded finite/discrete, finite-dimensional Gaussian-linear, exact only for supplied bounded POMDP trees, or finite static-model BAPOMDP; general Bayes-adaptive control is not claimed'},
            {'id':'FORMAL_CAUSAL_DISCOVERY','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V8/V9 bootstrap/partial graphs, V10 bounded PC-stable, and V11 supplied-DAG ADMG projection are assumption-scoped graph surfaces, not hidden-confounder-complete causal discovery'},
            {'id':'GENERAL_NONLINEAR_BAYES','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V10/V11 GP machinery is small-data RBF with finite-grid hyperparameter search; general kernel learning, scalable sparse GP, neural Bayesian inference, and world truth are not claimed'},
            {'id':'EXTERNAL_PROMOTION_VERIFIER','status':'UNRESOLVED_CONTROL_PLANE_BRIDGE','boundary':'PROMOTION.2 MCP caller packets stop at ATTESTED_READY; QUALIFIED requires a host-internal trusted verification receipt bound to the exact CI/smoke refs and head'},
        ],
        'promotion':'PROMOTION.2 MCP evaluations may reach ATTESTED_READY from exact-head caller-bound CI/smoke packets only; QUALIFIED additionally requires a host-internal trusted verifier receipt bound to that same head and the exact CI/smoke references. Historical PROMOTION.1 receipts remain versioned/replayable but are not counted as current trusted qualification.',
    }


def maxdev_law()->str:
    return '''ATHENA UNIFIED MAXDEV V11\n1 HYDRATE current semantic/Git/topology heads; apply no hidden assumptions.\n2 RECONSTRUCT through RECONRUN + canonical OMEGA; declare consulted/expected sources and preserve missing refs as defects.\n3 MEMORY may guide attention/repair lookup only: pheromone/reuse/consensus never become evidence or Y authority.\n4 EXTRACT with SX.1 typed work contracts; planning != semantic execution.\n5 RETRIEVE only supplied/fetched provenance records; missing measurements stay UNKNOWN and source_authority != Y authority.\n6 HUG through exact HUG(io,au,fx,lm,er,st) ABI; unresolved implementation fails closed; PLANNED != executed.\n7 GAP uses explicit witnessed reachability policy; reachability != logical/causal proof.\n8 FIELD assembles real residual work; generated candidates are UNMEASURED and explicit conflicts become CONFLICT.\n9 MEASURE/CALIBRATE before arithmetic; UNKNOWN != 0 and KNOWN != COMPARABLE.\n10 AUTHORITY Y in {?,+,!,#} is non-skippable and orthogonal to confidence/popularity/reward/model state. V6-V11 science-shadow/model evidence never aliases this registry.\n11 AOR ranks eligible comparable candidates, preserves Pareto alternatives, budgets resources, and chooses structured successor; no textual-order fallback.\n12 COLLECTIVE organizes HOW available capacity executes AOR-selected WHAT. V1-V2 provide execution capacity/memory; V3 learning may adapt policy from observed reward only; learned elders/policy are not evidence.\n13 V4-V10 model/science/control operators remain observation-gated: counterfactual/posterior/EIG/rollout/scenario/belief/control/replication-design output never trains or authorizes itself.\n14 V11 GP hyperfit is DESIGN_ONLY unless apply=true with expected_observation_count CAS matching the live GP dataset. Marginal-likelihood optimum is conditional on the finite grid/RBF family/observations, not the true kernel.\n15 V11 GP decision EVSI values hypothetical measurements under the current GP and never appends observations.\n16 V11 latent ADMG projection operates only on a caller-supplied acyclic DAG plus declared latent/observed nodes; it creates no canonical JSPACE edges and is not data-discovered PAG/FCI output.\n17 V11 stacked binary TMLE remains identification-assumption scoped; latent-confounding risk fails closed. Validation-weighted nuisance stacking is not a super-learner theorem.\n18 V11 RR bias-factor surface is a declared two-dimensional sensitivity grid, not a universal hidden-confounding bound.\n19 V11 finite-model BAPOMDP returns exact certification only for the supplied static model set/state/action/observation tree and bounded horizon after complete search; node truncation removes certification. Policy remains PLAN_ONLY.\n20 V11 dependence intervals are Laplace/Hessian model-conditional diagnostics around an externally labelled fitted model; interval reads never create labels and coverage is not guaranteed.\n21 EXECUTE only through a real executor/receipt; no generic semantic-execution fiction.\n22 VERIFY with witnessed tests; failed execution routes to explicit unmeasured repair work/antibody suggestions.\n23 LEARN only from observed/witnessed outcomes; never feed predictions/beliefs/simulations/plans/designs back as observations or Y authority.\n24 PERSIST with domain-specific CAS and readback; semantic VID, Git HEAD and topology version are distinct transaction domains.\n25 REPLAY deterministic child receipts; replay mismatch is a defect and should generate repair/regression work.\n26 SELFTEST local organism health; local PASS does not substitute for external CI/smoke, causal validity, model validity, or authority.\n27 PROMOTE through PROMOTION.2: exact-head caller-bound CI/smoke packets may reach ATTESTED_READY only; QUALIFIED requires a host-internal trusted verifier receipt binding the same head and exact CI/smoke refs.\n28 CONTINUE while actionable successor/residual/measurement/calibration/dependency/repair/experiment pressure remains; otherwise return exact continuation/RETURN state.'''

from __future__ import annotations

from typing import Any,Dict

UNIFIED_MANIFEST_VERSION='ATHENA.RUNTIME.UNIFIED.9'

LAYERS=[
 'CCR','JSPACE','SCALE','KC144','POLYCOORDINATE_ATLAS','CRYSTAL_OUTPUT_ABI',
 'COLLECTIVE_RUNTIME_V1','COLLECTIVE_GROWTH_V1','COLLECTIVE_MEMORY_V2','COLLECTIVE_LEARNING_V3','COLLECTIVE_ECOLOGY_V4','COLLECTIVE_SCIENCE_V5','COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11','COLLECTIVE_JOINT_V12','COLLECTIVE_ROBUST_V13',
 'AOR_DECISION_CORTEX','AOR.3','BRANCH_EVOLUTION','AUTHORITY_Y1','EQ.1','SX.1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1',
 'AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','STARTUP.1','SURFACE.2','COMPOSITION.2','PROMOTION.2','GITHUB_PROMOTION_VERIFIER.1',
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
 'GitHub trusted qualification requires syntax+unit+critical-invariants+smoke completed success in one coherent host-bound GitHub Actions run/check-suite on the exact head; checks from different suites/runs are never spliced',
 'trusted GitHub repository/API/run context comes from host environment, not MCP caller input',
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
 'V12 finite-grid GP hyperposterior != continuous hyperparameter Bayes; BMA GP posterior != world truth',
 'V12 subset-of-data GP approximation != full GP posterior or sparse variational GP theorem',
 'V12 bounded PAG candidate != FCI/RFCI PAG theorem and never mutates canonical JSPACE',
 'V12 two-timepoint parametric g-formula != longitudinal TMLE or identification proof',
 'V12 BMA GP EVSI != observation; hypothetical kernel/model updates never self-train',
 'V12 independent-Gaussian chance certificate != distribution-free resource guarantee; greedy fallback has no optimality certificate',
 'V13 QMC continuous-domain hyperposterior != exact continuous hyperparameter Bayes and finite quadrature does not reveal a true kernel',
 'V13 FITC inducing GP != full GP posterior or variational optimum; query error witness != global approximation theorem',
 'V13 joint hypermodel information/decision design != observation or evidence and never self-trains',
 'V13 bounded FCI-lite != FCI/RFCI PAG theorem; missing complete possible-d-sep/discriminating paths remain explicit',
 'V13 sequential two-timepoint TMLE != general longitudinal TMLE theorem or identification proof; targeting history must preserve observed A1/L1 before stage-1 intervention',
 'V13 dynamic two-timepoint g-formula policy value != general off-policy causal value or execution authorization',
 'V13 correlated-Gaussian ellipsoidal-mean robust certificate != general distributionally robust optimization; large-n greedy fallback has no optimality certificate',
 'athena_claim_* = Y1 canonical authority; athena_discovery_claim_* = V6-V13 science-shadow replication/falsification metadata; namespaces must never alias',
]

CYCLE='HYDRATE -> RECONRUN/OMEGA -> MEMORY -> EXTRACT -> RETRIEVE -> HUG -> GAP -> FIELD -> MEASURE -> AUTHORITY/AOR -> COLLECTIVE(V1-V13) -> EXECUTE -> VERIFY -> LEARN -> SUCCESSOR -> COMPLETE'
BRAID_LAW='AOR chooses developmental frontier/WHAT; Collective V1-V13 organizes HOW scarce execution/science/control/inference/adaptation/joint-model/robust capacity is used; Y1 governs canonical claim authority; EQ1 governs witnessed collapse; consensus/pheromone/reward are never typed authority or evidence by themselves; model posterior/replication shadow are also never typed authority or evidence by themselves; caller-bound CI/smoke packets are not trusted external verification; GitHub qualification is trusted only after host-bound independent check-suite observation.'


def build_unified_manifest(server)->Dict[str,Any]:
    dev=server.aor_development;integrity=dev.integrity;schema=integrity.state_foundation.schema.status();startup=integrity.startup.evaluate(False);git=server.git.status();verifier=integrity.github_promotion_verifier.describe()
    return {
        'artifact':UNIFIED_MANIFEST_VERSION,'artifact_compat':['ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2','ATHENA.RUNTIME.UNIFIED.3','ATHENA.RUNTIME.UNIFIED.4','ATHENA.RUNTIME.UNIFIED.5','ATHENA.RUNTIME.UNIFIED.6','ATHENA.RUNTIME.UNIFIED.7','ATHENA.RUNTIME.UNIFIED.8'],'role':'live machine-readable runtime architecture projection','runtime_class':type(server).__name__,
        'layers':list(LAYERS),'navigation':'KC144 <-> SCALE <-> JSPACE <-> AOR <-> Collective(V1-V13) <-> Git/MCP <-> Source/RETURN','cycle':CYCLE,'invariants':list(INVARIANTS),'braid_law':BRAID_LAW,
        'identity_law':'SID != OID != MID != VID != CID != EID != CRYS != ENV != AORRUN != RAGRUN != EXTRUN != EXTTASK != EXTRES != HUGIMPL != HUGINV != GAPRUN != FIELDRUN != TRANSPORTRUN != CYCLE != CYCLEEV != PROMRUN != MIGRUN != OMEGA != RECONRUN',
        'claim_namespace_law':'athena_claim_* is canonical Y1 authority; athena_discovery_claim_* is V6-V13 science-shadow/evidence state; no RPC-name aliasing or implicit promotion/demotion is permitted',
        'cas_law':'CAS_OMEGA = CAS_semantic(VID) x CAS_git(HEAD) x CAS_topology(version); staleness in one domain must not mutate the others; V11 GP observed-row CAS remains a separate model-state mutation guard',
        'schema':{'ledger_version':schema['version'],'current':schema['current_db_schema_version'],'target':schema['target_db_schema_version'],'up_to_date':schema['up_to_date']},
        'startup':{'version':startup['version'],'status':startup['status'],'gates':startup['gates']},'git':git,'promotion_verifier':verifier,
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
                'joint_v12':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'finite-grid GP hyperposterior/BMA, subset-GP approximation, bounded PAG candidate, two-timepoint g-formula, BMA GP EVSI and independent-Gaussian chance planning remain bounded model/assumption-scoped state'},
                'robust_v13':{'construction':'LAZY_ON_TOOL_OR_RESOURCE_ACCESS','boundary':'QMC continuous-domain GP hyperbelief, FITC inducing approximation, joint hypermodel information/decision design, bounded FCI-lite, history-preserving two-timepoint sequential TMLE, dynamic two-timepoint g-formula policies and correlated-Gaussian ellipsoidal-mean robust resource planning remain bounded model/assumption-scoped state'},
            },
            'aor':server.orchestration.benchmark(),'development':dev.benchmark(),
        },
        'unresolved':[
            {'id':'QHUG_SEMANTICS','status':'UNRESOLVED_UNLESS_REGISTERED_AND_WITNESSED','boundary':'HUG.ABI.1 remains operational/fail-closed without inventing canonical QHUG equations or six-parameter semantics'},
            {'id':'STRONGER_CLOSURE','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'GAP.1 implements witnessed directed reachability only; logical/causal/deductive closure require separately registered sound semantics'},
            {'id':'MODEL_TO_AUTHORITY_BRIDGE','status':'EXPLICIT_WITNESS_REQUIRED','boundary':'V3-V13 predictions, beliefs, estimates, experiments, graph hypotheses, discovery claims, replication diagnostics and control/resource plans cannot enter Y1/AOR evidence lanes without explicit observed/witnessed transport and authority gating'},
            {'id':'GENERAL_BELIEF_CONTROL','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V8-V13 control remains bounded finite/discrete, finite-dimensional Gaussian-linear, bounded GP/BMA/QMC, exact only for supplied finite POMDP/BAPOMDP trees, or finite decision-value designs; general continuous Bayes-adaptive control is not claimed'},
            {'id':'FORMAL_CAUSAL_DISCOVERY','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V13 adds global bounded observed-variable conditioning and limited FCI-inspired propagation, but complete possible-d-sep, discriminating paths, full FCI/RFCI PAG semantics, selection bias and calibrated structural posteriors remain unresolved'},
            {'id':'GENERAL_NONLINEAR_BAYES','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V13 adds log-space Halton QMC hyperparameter quadrature and deterministic FITC inducing inference; exact continuous hyperposterior integration/MCMC, optimized variational inducing distributions, neural Bayesian inference and world truth remain unresolved'},
            {'id':'LONGITUDINAL_CAUSAL_POLICY','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V13 adds history-preserving two-stage logistic targeting for static regimes and deterministic two-timepoint g-formula policy value; cross-fitted longitudinal TMLE, stochastic/dynamic regimes beyond two times, doubly robust off-policy value and identification proofs remain unresolved'},
            {'id':'STOCHASTIC_RESOURCE_CONTROL','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V13 admits correlated Gaussian covariance and ellipsoidal mean ambiguity in small finite exact enumeration; general Wasserstein/f-divergence ambiguity, non-Gaussian tails, multistage resource dynamics and general distributionally robust control remain unresolved'},
            {'id':'NON_GITHUB_PROMOTION_VERIFIERS','status':'UNRESOLVED_OPTIONAL_INTEGRATION','boundary':'GITHUB_PROMOTION_VERIFIER.1 implements trusted GitHub Actions verification; other external CI providers require separately registered trusted host verifiers rather than caller assertions'},
        ],
        'promotion':'PROMOTION.2 caller packets may reach ATTESTED_READY only. QUALIFIED requires trusted external verification. GITHUB_PROMOTION_VERIFIER.1 provides a host-bound path: independently fetch GitHub check-runs, require syntax+unit+critical-invariants+smoke completed success in one coherent exact-head Actions run/check-suite, then internally bind those refs into the trusted PROMRUN. Historical PROMOTION.1 receipts remain replayable but separate from current trusted qualification.',
    }


def maxdev_law()->str:
    return '''ATHENA UNIFIED MAXDEV V13
1 HYDRATE current semantic/Git/topology heads; apply no hidden assumptions.
2 RECONSTRUCT through RECONRUN + canonical OMEGA; declare consulted/expected sources and preserve missing refs as defects.
3 MEMORY may guide attention/repair lookup only: pheromone/reuse/consensus never become evidence or Y authority.
4 EXTRACT with SX.1 typed work contracts; planning != semantic execution.
5 RETRIEVE only supplied/fetched provenance records; missing measurements stay UNKNOWN and source_authority != Y authority.
6 HUG through exact HUG(io,au,fx,lm,er,st) ABI; unresolved implementation fails closed; PLANNED != executed.
7 GAP uses explicit witnessed reachability policy; reachability != logical/causal proof.
8 FIELD assembles real residual work; generated candidates are UNMEASURED and explicit conflicts become CONFLICT.
9 MEASURE/CALIBRATE before arithmetic; UNKNOWN != 0 and KNOWN != COMPARABLE.
10 AUTHORITY Y in {?,+,!,#} is non-skippable and orthogonal to confidence/popularity/reward/model state. V6-V13 science-shadow/model evidence never aliases this registry.
11 AOR ranks eligible comparable candidates, preserves Pareto alternatives, budgets resources, and chooses structured successor; no textual-order fallback.
12 COLLECTIVE organizes HOW available capacity executes AOR-selected WHAT. Choose the shallowest sufficient V1-V13 layer.
13 V4-V10 model/science/control operators remain observation-gated: counterfactual/posterior/EIG/rollout/scenario/belief/control/replication-design output never trains or authorizes itself.
14 V11 GP hyperfit remains DESIGN_ONLY unless apply=true with expected_observation_count CAS matching the live GP dataset; marginal-likelihood optimum remains model conditional.
15 V12 finite-grid hyperposterior/BMA/subset-GP/PAG/g-formula/BMA-EVSI/chance surfaces retain their existing no-self-training, no-JSPACE and assumption/certificate boundaries.
16 V13 GP hyper-QMC integrates a declared positive log-hyperparameter box with deterministic Halton particles; QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES.
17 V13 FITC uses deterministic inducing points plus diagonal conditional residual and always exposes query-level error against the exact current bounded GP; FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM.
18 V13 joint GP design scores downstream decision EVSI plus expected hypermodel entropy reduction. Simulated measurements/model reweights remain DESIGN_ONLY and never append observations.
19 V13 FCI-lite conditions on all observed-variable subsets only up to the declared bound and applies only limited orientation propagation. It is not full possible-d-sep/discriminating-path FCI/RFCI and never writes JSPACE.
20 V13 sequential TMLE is restricted to binary A1-L1-A2-Y and static two-timepoint regimes. Stage-2 pseudo outcomes preserve observed A1/L1 histories before stage-1 intervention evaluation. Declared latent confounding fails closed.
21 V13 dynamic policy value admits deterministic static/linear-threshold A1(X), A2(X,A1,L1) rules through the bounded parametric g-formula only; it is not general off-policy causal value or execution authorization.
22 V13 robust resource selection uses declared covariance plus ellipsoidal mean uncertainty and one-sided Gaussian chance bounds. Exact enumeration certifies only the declared finite ambiguity/model; large-n greedy fallback remains uncertified.
23 EXECUTE only through a real executor/receipt; no generic semantic-execution fiction.
24 VERIFY with witnessed tests; failed execution routes to explicit unmeasured repair work/antibody suggestions.
25 LEARN only from observed/witnessed outcomes; never feed predictions/beliefs/simulations/plans/designs back as observations or Y authority.
26 PERSIST with domain-specific CAS and readback; semantic VID, Git HEAD and topology version are distinct transaction domains.
27 REPLAY deterministic child receipts; replay mismatch is a defect and should generate repair/regression work.
28 SELFTEST local organism health; local PASS does not substitute for external CI/smoke, causal validity, model validity, or authority.
29 PROMOTION.2 caller-bound packets stop at ATTESTED_READY.
30 When host GitHub trust is configured, prefer athena_promotion_verify_github: independently require one coherent exact-head Actions run/check-suite with syntax+unit+critical-invariants+smoke success before persisting QUALIFIED. Never splice checks across runs/suites or accept caller-selected trust roots.
31 CONTINUE while actionable successor/residual/measurement/calibration/dependency/repair/experiment pressure remains; otherwise return exact continuation/RETURN state.'''

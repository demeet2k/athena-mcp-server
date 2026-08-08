from __future__ import annotations

from typing import Any,Dict

UNIFIED_MANIFEST_VERSION='ATHENA.RUNTIME.UNIFIED.3'

LAYERS=[
 'CCR','JSPACE','SCALE','KC144','POLYCOORDINATE_ATLAS','CRYSTAL_OUTPUT_ABI',
 'COLLECTIVE_RUNTIME_V1','COLLECTIVE_GROWTH_V1','COLLECTIVE_MEMORY_V2','COLLECTIVE_LEARNING_V3','COLLECTIVE_ECOLOGY_V4','COLLECTIVE_SCIENCE_V5','COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7',
 'AOR_DECISION_CORTEX','AOR.3','BRANCH_EVOLUTION','AUTHORITY_Y1','EQ.1','SX.1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1',
 'AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','STARTUP.1','SURFACE.2','COMPOSITION.2','PROMOTION.1',
 'GIT_LEDGER','SOURCE_RETURN',
]

INVARIANTS=[
 'UNKNOWN != 0 and UNKNOWN != N/A','KNOWN != COMPARABLE','consensus != evidence','pheromone/reuse/popularity != evidence != Y authority',
 'authority != confidence != truth probability','planning != execution','attempted write != verified persistence',
 'claimed test requires procedure+observation+result+witness','claimed persistence requires commit+receipt+verify',
 'reachability/navigation closure != logical or causal proof','HUG plan/packet integrity != semantic QHUG execution/replay',
 'AOR chooses WHAT is developmentally eligible; Collective organizes HOW capacity is assigned',
 'FIELD generated candidate = UNMEASURED; explicit metric/routing conflict = CONFLICT and non-rankable','hibernate != erase',
 'semantic VID CAS != Git HEAD CAS != topology version CAS','promotion requires exact-head local gates plus external CI and smoke attestations',
 'V3 policy/elder/runtime-usage learning != evidence or canonical authority','V4 UCB/counterfactual/credit/diffusion != observation and != causal proof without identification',
 'V5 POSTERIOR != TRUTH; CALIBRATION != MODEL_VALIDITY; EIG != EVIDENCE; ROLLOUT != EXECUTION; PARETO_FRONTIER != SINGLE_BEST',
 'V6 OOD/nonlinear/causal/scheduling/discovery outputs remain model-conditional; causal identification is conditional on supplied DAG/assumptions',
 'V7 uncertainty decomposition proxies != physical decomposition; prequential interval != distribution-free coverage guarantee; causal skeleton != DAG',
 'V7 scenario tree != future; DUAL_CONTROL_PROXY_PLAN_ONLY != exact Bayesian belief-state dual control and != execution',
 'V7 extended FRONTDOOR/INSTRUMENT identification remains conditional on the supplied DAG/observed-node/assumption semantics',
 'V7 replication effective_n != formal independence proof; replication/falsifier design != replication/falsification result',
 'athena_claim_* = Y1 canonical authority; athena_discovery_claim_* = V6/V7 science-shadow replication/falsification metadata; namespaces must never alias',
]

CYCLE='HYDRATE -> RECONRUN/OMEGA -> MEMORY -> EXTRACT -> RETRIEVE -> HUG -> GAP -> FIELD -> MEASURE -> AUTHORITY/AOR -> COLLECTIVE(V1-V7) -> EXECUTE -> VERIFY -> LEARN -> SUCCESSOR -> COMPLETE'
BRAID_LAW='AOR chooses developmental frontier/WHAT; Collective V1-V7 organizes HOW scarce execution/science/control capacity is used; Y1 governs canonical claim authority; EQ1 governs witnessed collapse; consensus/pheromone/reward are never typed authority or evidence by themselves; model posterior/replication shadow are also never typed authority or evidence by themselves.'


def build_unified_manifest(server)->Dict[str,Any]:
    dev=server.aor_development;integrity=dev.integrity;schema=integrity.state_foundation.schema.status();startup=integrity.startup.evaluate(False);git=server.git.status()
    return {
        'artifact':UNIFIED_MANIFEST_VERSION,'artifact_compat':['ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2'],'role':'live machine-readable runtime architecture projection','runtime_class':type(server).__name__,
        'layers':list(LAYERS),'navigation':'KC144 <-> SCALE <-> JSPACE <-> AOR <-> Collective(V1-V7) <-> Git/MCP <-> Source/RETURN','cycle':CYCLE,'invariants':list(INVARIANTS),'braid_law':BRAID_LAW,
        'identity_law':'SID != OID != MID != VID != CID != EID != CRYS != ENV != AORRUN != RAGRUN != EXTRUN != EXTTASK != EXTRES != HUGIMPL != HUGINV != GAPRUN != FIELDRUN != TRANSPORTRUN != CYCLE != CYCLEEV != PROMRUN != MIGRUN != OMEGA != RECONRUN',
        'claim_namespace_law':'athena_claim_* is canonical Y1 authority; athena_discovery_claim_* is V6/V7 science-shadow state; no RPC-name aliasing or implicit promotion/demotion is permitted',
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
            },
            'aor':server.orchestration.benchmark(),'development':dev.benchmark(),
        },
        'unresolved':[
            {'id':'QHUG_SEMANTICS','status':'UNRESOLVED_UNLESS_REGISTERED_AND_WITNESSED','boundary':'HUG.ABI.1 remains operational/fail-closed without inventing canonical QHUG equations or six-parameter semantics'},
            {'id':'STRONGER_CLOSURE','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'GAP.1 implements witnessed directed reachability only; logical/causal/deductive closure require separately registered sound semantics'},
            {'id':'MODEL_TO_AUTHORITY_BRIDGE','status':'EXPLICIT_WITNESS_REQUIRED','boundary':'V3-V7 predictions, credits, posteriors, experiments, discovery claims, replication diagnostics and control plans cannot enter Y1/AOR evidence lanes without explicit observed/witnessed transport and authority gating'},
            {'id':'EXACT_DUAL_CONTROL','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'V7 dual-control is an explicit proxy over learned transitions, information leverage and risk; exact Bayesian belief-state control is not claimed'},
        ],
        'promotion':'local READY_LOCAL is necessary but not sufficient; exact-head external CI+smoke attestations are required for PROMRUN.QUALIFIED',
    }


def maxdev_law()->str:
    return '''ATHENA UNIFIED MAXDEV V7\n1 HYDRATE current semantic/Git/topology heads; apply no hidden assumptions.\n2 RECONSTRUCT through RECONRUN + canonical OMEGA; declare consulted/expected sources and preserve missing refs as defects.\n3 MEMORY may guide attention/repair lookup only: pheromone/reuse/consensus never become evidence or Y authority.\n4 EXTRACT with SX.1 typed work contracts; planning != semantic execution.\n5 RETRIEVE only supplied/fetched provenance records; missing measurements stay UNKNOWN and source_authority != Y authority.\n6 HUG through exact HUG(io,au,fx,lm,er,st) ABI; unresolved implementation fails closed; PLANNED != executed.\n7 GAP uses explicit witnessed reachability policy; reachability != logical/causal proof.\n8 FIELD assembles real residual work; generated candidates are UNMEASURED and explicit conflicts become CONFLICT.\n9 MEASURE/CALIBRATE before arithmetic; UNKNOWN != 0 and KNOWN != COMPARABLE.\n10 AUTHORITY Y in {?,+,!,#} is non-skippable and orthogonal to confidence/popularity/reward/model state. V6/V7 science-shadow claims use athena_discovery_claim_* and never alias this registry.\n11 AOR ranks eligible comparable candidates, preserves Pareto alternatives, budgets resources, and chooses structured successor; no textual-order fallback.\n12 COLLECTIVE organizes HOW available capacity executes AOR-selected WHAT. V1-V2 provide execution capacity/memory; V3 learning may adapt policy from observed reward only; learned elders/policy are not evidence.\n13 V4 ecology may use UCB, credit, diffusion, scheduling and projection sagas; predictions/counterfactuals/rollouts never train themselves as observations.\n14 V5 science may use Bayesian prediction, empirical calibration, EIG experiment design, delayed/interaction credit, transition models, multiperiod scheduling and Pareto frontiers. POSTERIOR != TRUTH; CALIBRATION != VALIDITY; EIG != EVIDENCE; ROLLOUT != EXECUTION.\n15 V6 discovery may use OOD inflation, nonlinear basis models, factor experiment generation, conditional back-door identification, higher-order interactions, stochastic transition surfaces, MPC, certified small scheduling and science-shadow replication claims. These remain model/metadata surfaces until explicit observation/witness.\n16 V7 dual-control may decompose uncertainty diagnostically, construct prequential residual bands, generate heuristic causal skeletons, fit state-dependent transition models, evaluate finite scenario trees, plan proxy dual-control sequences, test BACKDOOR/FRONTDOOR/INSTRUMENT criteria under supplied DAGs, and estimate/rank replication diversity. Every output retains its model/conditional/design label: proxy != physical decomposition, band != distribution-free guarantee, skeleton != DAG, simulation != future, plan != execution, identification != unconditional causal truth, effective_n != formal independence proof, design != result.\n17 EXECUTE only through a real executor/receipt; no generic semantic-execution fiction.\n18 VERIFY with witnessed tests; failed execution routes to explicit unmeasured repair work/antibody suggestions.\n19 LEARN only from observed/witnessed outcomes; do not double-count RGO/DeltaJ/credit for the same outcome and never feed predictions/simulations/plans back as observations.\n20 PERSIST with domain-specific CAS and readback; semantic VID, Git HEAD and topology version are distinct transaction domains.\n21 REPLAY deterministic child receipts; replay mismatch is a defect and should generate repair/regression work.\n22 SELFTEST local organism health; local PASS does not substitute for external CI/smoke, causal validity, model validity, or authority.\n23 PROMOTE only the exact head with SURFACE.2 + COMPOSITION.2 + schema/SELFTEST/local Git gates plus exact external CI/smoke attestations.\n24 CONTINUE while actionable successor/residual/measurement/calibration/dependency/repair/experiment pressure remains; otherwise return exact continuation/RETURN state.'''

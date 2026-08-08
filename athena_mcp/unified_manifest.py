from __future__ import annotations

from typing import Any,Dict

UNIFIED_MANIFEST_VERSION='ATHENA.RUNTIME.UNIFIED.1'

LAYERS=[
 'CCR','JSPACE','SCALE','KC144','POLYCOORDINATE_ATLAS','CRYSTAL_OUTPUT_ABI',
 'COLLECTIVE_RUNTIME_V1','COLLECTIVE_GROWTH_V1','COLLECTIVE_MEMORY_V2',
 'AOR.3','BRANCH_EVOLUTION','AUTHORITY_Y1','EQ.1','SX.1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1',
 'AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','SURFACE.2','COMPOSITION.2','PROMOTION.1',
 'GIT_LEDGER','SOURCE_RETURN',
]

INVARIANTS=[
 'UNKNOWN != 0 and UNKNOWN != N/A',
 'KNOWN != COMPARABLE',
 'consensus != evidence',
 'pheromone/reuse/popularity != evidence != Y authority',
 'authority != confidence != truth probability',
 'planning != execution',
 'attempted write != verified persistence',
 'claimed test requires procedure+observation+result+witness',
 'claimed persistence requires commit+receipt+verify',
 'reachability/navigation closure != logical or causal proof',
 'HUG plan/packet integrity != semantic QHUG execution/replay',
 'AOR chooses WHAT is developmentally eligible; Collective organizes HOW capacity is assigned',
 'FIELD generated candidate = UNMEASURED; explicit metric/routing conflict = CONFLICT and non-rankable',
 'hibernate != erase',
 'semantic VID CAS != Git HEAD CAS != topology version CAS',
 'promotion requires exact-head local gates plus external CI and smoke attestations',
]

CYCLE='HYDRATE -> RECONRUN/OMEGA -> MEMORY -> EXTRACT -> RETRIEVE -> HUG -> GAP -> FIELD -> MEASURE -> AOR -> COLLECTIVE -> EXECUTE -> VERIFY -> LEARN -> SUCCESSOR -> COMPLETE'


def build_unified_manifest(server)->Dict[str,Any]:
    dev=server.aor_development;integrity=dev.integrity;schema=integrity.state_foundation.schema.status();startup=integrity.startup.evaluate(False);git=server.git.status()
    return {
        'artifact':UNIFIED_MANIFEST_VERSION,
        'role':'live machine-readable runtime architecture projection',
        'runtime_class':type(server).__name__,
        'layers':list(LAYERS),
        'navigation':'KC144 <-> SCALE <-> JSPACE <-> AOR <-> Collective <-> Git/MCP <-> Source/RETURN',
        'cycle':CYCLE,
        'invariants':list(INVARIANTS),
        'identity_law':'SID != OID != MID != VID != CID != EID != CRYS != ENV != AORRUN != RAGRUN != EXTRUN != EXTTASK != EXTRES != HUGIMPL != HUGINV != GAPRUN != FIELDRUN != TRANSPORTRUN != CYCLE != CYCLEEV != PROMRUN != MIGRUN != OMEGA != RECONRUN',
        'cas_law':'CAS_OMEGA = CAS_semantic(VID) x CAS_git(HEAD) x CAS_topology(version); staleness in one domain must not mutate the others',
        'schema':{'ledger_version':schema['version'],'current':schema['current_db_schema_version'],'target':schema['target_db_schema_version'],'up_to_date':schema['up_to_date']},
        'startup':{'version':startup['version'],'status':startup['status'],'gates':startup['gates']},
        'git':git,
        'organs':{
            'collective':{'runtime':server.collective.describe(),'growth':server.collective_growth.describe(),'memory':server.collective_memory.describe()},
            'aor':server.orchestration.benchmark(),
            'development':dev.benchmark(),
        },
        'unresolved':[
            {'id':'QHUG_SEMANTICS','status':'UNRESOLVED_UNLESS_REGISTERED_AND_WITNESSED','boundary':'HUG.ABI.1 remains fully operational/fail-closed without inventing canonical QHUG equations or six-parameter semantics'},
            {'id':'STRONGER_CLOSURE','status':'UNRESOLVED_OPTIONAL_RESEARCH','boundary':'GAP.1 implements witnessed directed reachability only; logical/causal/deductive closure require separately registered sound semantics'},
        ],
        'promotion':'local READY_LOCAL is necessary but not sufficient; exact-head external CI+smoke attestations are required for PROMRUN.QUALIFIED',
    }


def maxdev_law()->str:
    return '''ATHENA UNIFIED MAXDEV\n1 HYDRATE current semantic/Git/topology heads; apply no hidden assumptions.\n2 RECONSTRUCT through RECONRUN + canonical OMEGA; declare consulted/expected sources and preserve missing refs as defects.\n3 MEMORY may guide attention/repair lookup only: pheromone/reuse/consensus never become evidence or Y authority.\n4 EXTRACT with SX.1 typed work contracts; planning != semantic execution.\n5 RETRIEVE only supplied/fetched provenance records; missing measurements stay UNKNOWN and source_authority != Y authority.\n6 HUG through exact HUG(io,au,fx,lm,er,st) ABI; unresolved implementation fails closed; PLANNED != executed.\n7 GAP uses explicit witnessed reachability policy; reachability != logical/causal proof.\n8 FIELD assembles real residual work; generated candidates are UNMEASURED and explicit conflicts become CONFLICT.\n9 MEASURE/CALIBRATE before arithmetic; UNKNOWN != 0 and KNOWN != COMPARABLE.\n10 AUTHORITY Y in {?,+,!,#} is non-skippable and orthogonal to confidence/popularity/reward.\n11 AOR ranks eligible comparable candidates, preserves Pareto alternatives, budgets resources, and chooses structured successor; no textual-order fallback.\n12 COLLECTIVE organizes HOW available capacity executes AOR-selected WHAT; preserve reserve and explicit bridge economics.\n13 EXECUTE only through a real executor/receipt; no generic semantic-execution fiction.\n14 VERIFY with witnessed tests; failed execution routes to explicit unmeasured repair work/antibody suggestions.\n15 LEARN only from observed/witnessed outcomes; do not double-count RGO and DeltaJ for the same outcome.\n16 PERSIST with domain-specific CAS and readback; semantic VID, Git HEAD and topology version are distinct transaction domains.\n17 REPLAY deterministic child receipts; replay mismatch is a defect and should generate repair/regression work.\n18 SELFTEST local organism health; local PASS does not substitute for external CI/smoke.\n19 PROMOTE only the exact head with SURFACE.2 + COMPOSITION.2 + schema/SELFTEST/local Git gates plus exact external CI/smoke attestations.\n20 CONTINUE while actionable successor/residual/measurement/calibration/dependency/repair pressure remains; otherwise return exact continuation/RETURN state.'''

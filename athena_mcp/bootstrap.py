from .frontier_claim import (
    FRONTIER_CLAIM_TOOLS,
    FRONTIER_CLAIM_TOOL_NAMES,
    install_frontier_claim_extension,
)
from .frontier_runtime import FrontierRuntime, FRONTIER_TOOLS, FRONTIER_TOOL_NAMES
from .prompt_runtime import PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES

# Additive claim-preparation registration. server.py imports this module after
# package initialization and before dispatch is loaded, so mutating the existing
# tool lists/sets in place is visible to both the already-installed frontier
# wrapper and dispatch's canonical prompt-tool union without rewriting __init__.
install_frontier_claim_extension(FrontierRuntime, FRONTIER_TOOLS)
FRONTIER_TOOL_NAMES.update(FRONTIER_CLAIM_TOOL_NAMES)
for _tool in FRONTIER_CLAIM_TOOLS:
    if _tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
        PROMPT_RUNTIME_TOOLS.append(_tool)
        PROMPT_RUNTIME_TOOL_NAMES.add(_tool["name"])

GENESIS=[
('TOOL','IDENTITY','RESOLVE','CAPABILITY','CANONICAL_SIGNATURE',{'need':'functional signature'},{'oid':'string','cid':'string','canonical_name':'string'}),
('TOOL','NAVIGATION','RESOLVE','OBJECT','KC144_JSPACE',{'identifier':'OID|CID|name'},{'coordinate':'polycoordinate','edges':'graph'}),
('TOOL','STATE','MUTATE','CANONICAL_OBJECT','EXPECTED_VID_CAS',{'oid':'string','expected_vid':'VID','delta':'object'},{'status':'COMMITTED|STALE_TARGET'}),
('TOOL','TEXT','INDEX','MANIFESTATION','EXACT_LEXEME_COORDINATES',{'text':'string','oid':'OID','vid':'VID'},{'mid':'MID','token_coordinates':'array'}),
('TOOL','SWARM','EMIT','AGENT_PROGRESS','LIMINAL_TELEMETRY',{'agent':'string','event':'public telemetry'},{'eid':'EID','liminal_coordinate':'string'}),
('ALGO','SWARM','REPRESENT','N_WAY_INTERACTION','LAZY_SIMPLEX',{'participants':'2..60'},{'dimension':'n-1','faces':'lazy'}),
('TOOL','SWARM','MATCH','HELP','NEED_OFFER_COMPLEMENTARITY',{'agent':'string'},{'matches':'ranked peers'}),
('POLICY','SWARM','ADOPT','GLOBAL_MUTATION','NEXT_CYCLE_REQUIRED',{'mutation':'global class'},{'adoption_receipt':'EID'}),
('HARNESS','DEVELOPMENT','MAXIMIZE','WHOLE_SYSTEM_DELTA','MAXDEV_SELFPLAY',{'task':'whole objective'},{'crystal_delta':'integrated output'}),
('BENCH','PERFORMANCE','MEASURE','MAXDEV','FRONTIER_VECTOR',{'run':'metrics'},{'pareto_record':'vector'}),
('MODEL','REPRESENTATION','LIFT','EVENTS_TO_ORGAN','SCALE_S0_S5',{'events':'ledger'},{'representation':'S0..S5'}),
('INDEX','GRAPH','PROJECT','CAUSAL_LEDGER','JSPACE',{'events':'ledger'},{'graph':'typed multigraph'}),
('HARNESS','OPTIMIZATION','SOLVE','BOOLEAN_PARETO_KERNEL','QHUG_V23_2',{'patches':'boolean patch resources','invalid':'forced false','conflicts':'pair exclusions','dependencies':'OR-of-AND prerequisites','mode':'governed|neutral'},{'components':'exact factors','model_count':'integer','pareto_frontier':'nondominated resource vectors','optimum':'all ties'}),
('TOOL','OPTIMIZATION','ANALYZE','BOOLEAN_KERNEL','QHUG_COMPONENT_FACTOR_V23_2',{'patches':'boolean patch kernel','constraints':'validity/dependency/conflict'},{'primal_graph':'components','structural_free':'coordinates','component_enumeration_work':'integer'}),
('TOOL','GRAPH','VERIFY','TREE_DECOMPOSITION','QHUG_TREEWIDTH_CERT_V23_2',{'bags':'tree decomposition','factor_scopes':'QHUG constraints'},{'factor_coverage':'bool','running_intersection':'bool','width_upper_bound':'integer','clique_lower_bound':'integer','exact_treewidth_certified':'bool'})]
def bootstrap(core):
    if core.s.one('SELECT COUNT(*) n FROM objects')['n']: return
    for kind,domain,verb,obj,method,inp,out in GENESIS:
        core.register(kind,domain,verb,obj,method,inp,out,actor='GENESIS',status='CANONICAL')

from __future__ import annotations

from typing import Any,Dict

from .orchestration_equivalence import EquivalenceLedger
from .orchestration_equivalence_protocol import EQUIVALENCE_RESOURCE,EQUIVALENCE_TOOLS
from .orchestration_extract import ExtractionLedger,transform_manifest
from .orchestration_extract_protocol import EXTRACTION_RESOURCE,EXTRACTION_TOOLS
from .orchestration_retrieval import RetrievalLedger,retrieval_law
from .orchestration_retrieval_protocol import RETRIEVAL_RESOURCE,RETRIEVAL_TOOLS
from .orchestration_hug import HugRegistry,HUG_PARAMS
from .orchestration_hug_protocol import HUG_RESOURCE,HUG_TOOLS

AOR_DEVELOPMENT_TOOLS=list(EQUIVALENCE_TOOLS)+list(EXTRACTION_TOOLS)+list(RETRIEVAL_TOOLS)+list(HUG_TOOLS)
AOR_DEVELOPMENT_RESOURCES=[EQUIVALENCE_RESOURCE,EXTRACTION_RESOURCE,RETRIEVAL_RESOURCE,HUG_RESOURCE]
AOR_DEVELOPMENT_TOOL_NAMES={tool['name'] for tool in AOR_DEVELOPMENT_TOOLS}
AOR_DEVELOPMENT_RESOURCE_URIS={resource['uri'] for resource in AOR_DEVELOPMENT_RESOURCES}

class AorDevelopmentSurface:
    """Composition boundary for modular developmental organs.

    EQ1 owns conservative identity collapse. SX1 creates bounded witnessed work.
    RAG1 ranks only supplied records and freezes EQ state. HUG.ABI.1 preserves
    HUG(io,au,fx,lm,er,st) but refuses semantic execution until an exact
    implementation identity has been registered and witnessed to the required
    maturity. No development organ may fabricate another organ's evidence.
    """
    def __init__(self,server):
        self.server=server;self.core=server.core
        self.equivalence=EquivalenceLedger(self.core)
        self.extraction=ExtractionLedger(self.core)
        self.retrieval=RetrievalLedger(self.core)
        self.hug=HugRegistry(self.core)

    def _retrieval_eq_snapshot(self,args):
        if args.get('eq_snapshot') is not None:return dict(args['eq_snapshot'])
        context=str(args.get('equivalence_context') or '').strip()
        if not context:return None
        return self.equivalence.snapshot(context,args['candidates'])

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_equivalence_observe':return True,self.equivalence.observe(args['context_id'],args['left_id'],args['right_id'],args['relation'],args['witness'],args.get('same'),args.get('different'),args.get('actor','agent'))
        if name=='athena_equivalence_state':return True,self.equivalence.state(args['context_id'],args['left_id'],args['right_id'])
        if name=='athena_equivalence_resolve_conflict':return True,self.equivalence.resolve_conflict(args['context_id'],args['left_id'],args['right_id'],args['relation'],args['authority'],args.get('actor','agent'))
        if name=='athena_equivalence_snapshot':return True,self.equivalence.snapshot(args['context_id'],args['candidates'])
        if name=='athena_extraction_plan':return True,self.extraction.plan(args['seed_ref'],args['seed'],args.get('transforms'),args.get('max_depth',1),args.get('max_tasks_per_generation',16),args.get('actor','agent'))
        if name=='athena_extraction_task':return True,self.extraction.task(args['task_id'])
        if name=='athena_extraction_complete':return True,self.extraction.complete(args['task_id'],args['outputs'],args['witness'],args.get('actor','agent'))
        if name=='athena_extraction_fail':return True,self.extraction.fail(args['task_id'],args['reason'],args['witness'],args.get('actor','agent'))
        if name=='athena_extraction_result':return True,self.extraction.result(args['result_id'])
        if name=='athena_extraction_expand_result':return True,self.extraction.expand_result(args['result_id'],args.get('transforms'),args.get('actor','agent'))
        if name=='athena_extraction_frontier':return True,self.extraction.frontier(args['run_id'])
        if name=='athena_extraction_run':return True,self.extraction.run(args['run_id'])
        if name=='athena_retrieval_compile':return True,self.retrieval.compile(args['query_ref'],args['query'],args['candidates'],self._retrieval_eq_snapshot(args),args.get('actor','agent'),args.get('task',''),args.get('persist',True))
        if name=='athena_retrieval_get':return True,self.retrieval.get(args['run_id'])
        if name=='athena_retrieval_replay':return True,self.retrieval.replay(args['run_id'])
        if name=='athena_retrieval_recent':return True,self.retrieval.recent(args.get('limit',50))
        if name=='athena_hug_register':return True,self.hug.register(args['name'],args['version'],args['algorithm_ref'],args['implementation_digest'],args['parameter_semantics'],args['input_schema'],args['output_schema'],args.get('actor','agent'))
        if name=='athena_hug_state':return True,self.hug.state(args['impl_id'])
        if name=='athena_hug_list':return True,self.hug.list(args.get('status'),args.get('limit',100))
        if name=='athena_hug_promote':return True,self.hug.promote(args['impl_id'],args['target_status'],args.get('test'),args.get('canonical_authority'),args.get('actor','agent'))
        if name=='athena_hug_plan':return True,self.hug.plan(args['impl_id'],args['arguments'],args.get('context'),args.get('required_status','CANONICAL'),args.get('actor','agent'))
        if name=='athena_hug_complete':return True,self.hug.complete(args['invocation_id'],args['output'],args['receipt'],args.get('actor','agent'))
        if name=='athena_hug_fail':return True,self.hug.fail(args['invocation_id'],args['reason'],args['witness'],args.get('actor','agent'))
        if name=='athena_hug_invocation':return True,self.hug.invocation(args['invocation_id'])
        if name=='athena_hug_verify_packet':return True,self.hug.verify_packet(args['invocation_id'])
        return False,None

    def read_resource(self,uri:str):
        if uri==EQUIVALENCE_RESOURCE['uri']:
            return {'law':'UNKNOWN sameness preserves identity; collapse only witnessed contradiction-free EQUIVALENT components; DISTINCT/conflict preserve identities','preservation_dimensions':['semantic_object','functional_role','proof_route','carrier','lineage','boundary','failure_role'],'benchmark':self.equivalence.benchmark()}
        if uri==EXTRACTION_RESOURCE['uri']:
            return {'law':'planning creates typed PLANNED transform work only; completion/failure requires verified witness; witnessed results may seed bounded later generations; extraction never implies equivalence or automatic dedup','transform_manifest':transform_manifest(),'benchmark':self.extraction.benchmark(),'dedup_route':'use athena_equivalence_snapshot separately when witnessed EQ1 relations exist'}
        if uri==RETRIEVAL_RESOURCE['uri']:
            return {'law':retrieval_law(),'benchmark':self.retrieval.benchmark(),'eq_integration':'equivalence_context freezes current EQ1 snapshot before selection; explicit eq_snapshot may be supplied for replay/transport','boundary':'RAG1 ranks only supplied candidate records; source_authority is retrieval provenance quality, not Y1 authority; pheromone priority is not injected as evidence or score'}
        if uri==HUG_RESOURCE['uri']:
            return {'version':'HUG.ABI.1','signature':'HUG(io,au,fx,lm,er,st)','parameters':list(HUG_PARAMS),'benchmark':self.hug.benchmark(),'law':'registered implementation identity + exact six parameter meanings + schemas are required; registration=CANDIDATE; CANDIDATE->TESTED requires witnessed test; TESTED->CANONICAL explicit authority; HUGINV plan is not execution; completion requires real output plus verified receipt','semantic_status':'CANONICAL_QHUG_ALGORITHM_UNRESOLVED_UNLESS_AN_ACTUAL_IMPLEMENTATION_IS_REGISTERED_AND_WITNESSED','replay_boundary':'athena_hug_verify_packet proves frozen packet integrity only; semantic replay requires a real executor'}
        raise KeyError(uri)

    def benchmark(self):
        result={};result.update(self.equivalence.benchmark());result.update(self.extraction.benchmark());result.update(self.retrieval.benchmark());result.update(self.hug.benchmark());return result

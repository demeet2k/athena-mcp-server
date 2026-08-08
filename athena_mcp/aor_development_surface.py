from __future__ import annotations

from typing import Any,Dict

from .orchestration_equivalence import EquivalenceLedger
from .orchestration_equivalence_protocol import EQUIVALENCE_RESOURCE,EQUIVALENCE_TOOLS
from .orchestration_extract import ExtractionLedger,transform_manifest
from .orchestration_extract_protocol import EXTRACTION_RESOURCE,EXTRACTION_TOOLS

AOR_DEVELOPMENT_TOOLS=list(EQUIVALENCE_TOOLS)+list(EXTRACTION_TOOLS)
AOR_DEVELOPMENT_RESOURCES=[EQUIVALENCE_RESOURCE,EXTRACTION_RESOURCE]
AOR_DEVELOPMENT_TOOL_NAMES={tool['name'] for tool in AOR_DEVELOPMENT_TOOLS}
AOR_DEVELOPMENT_RESOURCE_URIS={resource['uri'] for resource in AOR_DEVELOPMENT_RESOURCES}

class AorDevelopmentSurface:
    """Composition boundary for modular developmental organs.

    EQ1 owns conservative witnessed identity collapse. SX1 creates bounded work
    contracts/results but never performs implicit dedup. Later RAG/HUG/GAP/FIELD
    extend this registry while base Collective/AOR/Y surfaces remain stable.
    """
    def __init__(self,server):
        self.server=server;self.core=server.core
        self.equivalence=EquivalenceLedger(self.core)
        self.extraction=ExtractionLedger(self.core)

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
        return False,None

    def read_resource(self,uri:str):
        if uri==EQUIVALENCE_RESOURCE['uri']:
            return {'law':'UNKNOWN sameness preserves identity; collapse only witnessed contradiction-free EQUIVALENT components; DISTINCT/conflict preserve identities','preservation_dimensions':['semantic_object','functional_role','proof_route','carrier','lineage','boundary','failure_role'],'benchmark':self.equivalence.benchmark()}
        if uri==EXTRACTION_RESOURCE['uri']:
            return {'law':'planning creates typed PLANNED transform work only; completion/failure requires verified witness; witnessed results may seed bounded later generations; extraction never implies equivalence or automatic dedup','transform_manifest':transform_manifest(),'benchmark':self.extraction.benchmark(),'dedup_route':'use athena_equivalence_snapshot separately when witnessed EQ1 relations exist'}
        raise KeyError(uri)

    def benchmark(self):
        result={};result.update(self.equivalence.benchmark());result.update(self.extraction.benchmark());return result

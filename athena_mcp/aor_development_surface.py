from __future__ import annotations

import json
from typing import Any, Dict

from .orchestration_equivalence import EquivalenceLedger
from .orchestration_equivalence_protocol import EQUIVALENCE_RESOURCE,EQUIVALENCE_TOOLS,EQUIVALENCE_TOOL_NAMES

AOR_DEVELOPMENT_TOOLS=list(EQUIVALENCE_TOOLS)
AOR_DEVELOPMENT_RESOURCES=[EQUIVALENCE_RESOURCE]
AOR_DEVELOPMENT_TOOL_NAMES={tool['name'] for tool in AOR_DEVELOPMENT_TOOLS}
AOR_DEVELOPMENT_RESOURCE_URIS={resource['uri'] for resource in AOR_DEVELOPMENT_RESOURCES}

class AorDevelopmentSurface:
    """Composition boundary for modular AOR development organs.

    New extraction/retrieval/HUG/GAP/FIELD organs extend this registry instead of
    growing the base Server dispatch chain. Existing base/Collective/AOR/Y tools
    remain owned by their native surfaces.
    """
    def __init__(self,server):
        self.server=server;self.core=server.core;self.equivalence=EquivalenceLedger(self.core)

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_equivalence_observe':return True,self.equivalence.observe(args['context_id'],args['left_id'],args['right_id'],args['relation'],args['witness'],args.get('same'),args.get('different'),args.get('actor','agent'))
        if name=='athena_equivalence_state':return True,self.equivalence.state(args['context_id'],args['left_id'],args['right_id'])
        if name=='athena_equivalence_resolve_conflict':return True,self.equivalence.resolve_conflict(args['context_id'],args['left_id'],args['right_id'],args['relation'],args['authority'],args.get('actor','agent'))
        if name=='athena_equivalence_snapshot':return True,self.equivalence.snapshot(args['context_id'],args['candidates'])
        return False,None

    def read_resource(self,uri:str):
        if uri==EQUIVALENCE_RESOURCE['uri']:
            return {'law':'UNKNOWN sameness preserves identity; collapse only witnessed contradiction-free EQUIVALENT components; DISTINCT/conflict preserve identities','preservation_dimensions':['semantic_object','functional_role','proof_route','carrier','lineage','boundary','failure_role'],'benchmark':self.equivalence.benchmark()}
        raise KeyError(uri)

    def benchmark(self):
        return self.equivalence.benchmark()

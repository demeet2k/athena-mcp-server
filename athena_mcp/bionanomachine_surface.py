from __future__ import annotations

from typing import Any,Dict

from .bionanomachine_protocol import BIONANO_RESOURCE,BIONANO_TOOLS,BIONANO_TOOL_NAMES,BIONANO_VERSION
from .bionanomachine_evidence_runtime import EvidenceBionanomachineRuntime

BIONANOMACHINE_TOOLS=list(BIONANO_TOOLS)
BIONANOMACHINE_RESOURCES=[BIONANO_RESOURCE]
BIONANOMACHINE_TOOL_NAMES=set(BIONANO_TOOL_NAMES)
BIONANOMACHINE_RESOURCE_URIS={BIONANO_RESOURCE['uri']}


class BionanomachineSurface:
    def __init__(self):self.runtime=EvidenceBionanomachineRuntime()

    def call_tool(self,name:str,args:Dict[str,Any]):
        r=self.runtime
        if name=='athena_bionano_catalog':return True,r.catalog(args.get('include_atlas',False),args.get('include_evidence',False))
        if name=='athena_bionano_compile':return True,r.compile(args['machine_id'])
        if name=='athena_bionano_transfer':return True,r.transfer(args['machine_id'],args['target'],args.get('constraints'))
        if name=='athena_bionano_interface_match':return True,r.interface_match(args['producer'],args['consumer'])
        if name=='athena_bionano_convergence_gate':return True,r.convergence_gate(**args)
        if name=='athena_bionano_assembly':return True,r.assembly(args['machine_id'])
        return False,None

    def read_resource(self,uri:str):
        if uri!=BIONANO_RESOURCE['uri']:raise KeyError(uri)
        return {
            'version':BIONANO_VERSION,
            'catalog':self.runtime.catalog(False,False),
            'benchmark':self.runtime.benchmark(),
            'laws':[
                'BIOLOGICAL_MECHANISM != SOFTWARE_IMPLEMENTATION',
                'MECHANISTIC_ANALOGY != CAUSAL_EQUIVALENCE',
                'USER_SEED != VERIFIED_EMPIRICAL_CONSTANT',
                'PRIMARY_SOURCE != UNIVERSAL_CONSTANT',
                'INTERFACE_MATCH_PROXY != PHYSICAL_IMPEDANCE',
                'AVAILABLE_TEST != APPLICABLE_TEST',
                'PARTS_LIST != ASSEMBLED_CAPABILITY',
                'ASSEMBLY_GRAPH != FUNCTION_GRAPH',
                'ROUTE_EXISTS != INTERFACE_MATCHED',
            ],
            'authority':'PRIMARY_SOURCE_CONDITIONED_MECHANISM_LIBRARY; COMPUTATIONAL_TRANSFER_REMAINS_ANALOGY_ONLY'
        }

    def benchmark(self):return self.runtime.benchmark()

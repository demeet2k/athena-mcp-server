from __future__ import annotations

from typing import Any,Dict

from .bionanomachine_protocol import BIONANO_RESOURCE,BIONANO_TOOLS,BIONANO_TOOL_NAMES,BIONANO_VERSION
from .bionanomachine_evidence_runtime import EvidenceBionanomachineRuntime
from .mythic_computation_surface import (
    MythicComputationSurface,
    MYTHIC_COMPUTATION_RESOURCES,
    MYTHIC_COMPUTATION_TOOLS,
    MYTHIC_COMPUTATION_TOOL_NAMES,
    MYTHIC_COMPUTATION_RESOURCE_URIS,
)

# Compatibility seam: AorDevelopmentSurface already composes this extension bundle.
# Preserve the MCK tool/resource union exactly while switching only the BNMK runtime
# behind the stable six-tool ABI to the tested source-backed V2 implementation.
BIONANOMACHINE_TOOLS=list(BIONANO_TOOLS)+list(MYTHIC_COMPUTATION_TOOLS)
BIONANOMACHINE_RESOURCES=[BIONANO_RESOURCE]+list(MYTHIC_COMPUTATION_RESOURCES)
BIONANOMACHINE_TOOL_NAMES=set(BIONANO_TOOL_NAMES)|set(MYTHIC_COMPUTATION_TOOL_NAMES)
BIONANOMACHINE_RESOURCE_URIS={BIONANO_RESOURCE['uri']}|set(MYTHIC_COMPUTATION_RESOURCE_URIS)


class BionanomachineSurface:
    def __init__(self):
        self.runtime=EvidenceBionanomachineRuntime()
        self.mck=MythicComputationSurface()

    def call_tool(self,name:str,args:Dict[str,Any]):
        handled,value=self.mck.call_tool(name,args)
        if handled:return True,value
        r=self.runtime
        if name=='athena_bionano_catalog':return True,r.catalog(args.get('include_atlas',False),args.get('include_evidence',False))
        if name=='athena_bionano_compile':return True,r.compile(args['machine_id'])
        if name=='athena_bionano_transfer':return True,r.transfer(args['machine_id'],args['target'],args.get('constraints'))
        if name=='athena_bionano_interface_match':return True,r.interface_match(args['producer'],args['consumer'])
        if name=='athena_bionano_convergence_gate':return True,r.convergence_gate(**args)
        if name=='athena_bionano_assembly':return True,r.assembly(args['machine_id'])
        return False,None

    def read_resource(self,uri:str):
        if uri in MYTHIC_COMPUTATION_RESOURCE_URIS:
            return self.mck.read_resource(uri)
        if uri!=BIONANO_RESOURCE['uri']:raise KeyError(uri)
        return {
            'version':BIONANO_VERSION,
            'evidence_version':'BNMK.ADAPTER20.V2',
            'catalog':self.runtime.catalog(False,False),
            'benchmark':self.runtime.benchmark(),
            'laws':[
                'BIOLOGICAL_MECHANISM != SOFTWARE_IMPLEMENTATION',
                'MECHANISTIC_ANALOGY != CAUSAL_EQUIVALENCE',
                'USER_SEED != VERIFIED_EMPIRICAL_CONSTANT',
                'PRIMARY_SOURCE != UNIVERSAL_CONSTANT',
                'PRIMARY_SOURCE_SUPPORT != EXECUTION_AUTHORITY',
                'INTERFACE_MATCH_PROXY != PHYSICAL_IMPEDANCE',
                'AVAILABLE_TEST != APPLICABLE_TEST',
                'PARTS_LIST != ASSEMBLED_CAPABILITY',
                'ASSEMBLY_GRAPH != FUNCTION_GRAPH',
                'ROUTE_EXISTS != INTERFACE_MATCHED',
            ],
            'authority':'PRIMARY_SOURCE_CONDITIONED_MECHANISM_LIBRARY; COMPUTATIONAL_TRANSFER_REMAINS_ANALOGY_ONLY'
        }

    def benchmark(self):
        result={}
        result.update(self.runtime.benchmark())
        result.update(self.mck.benchmark())
        return result

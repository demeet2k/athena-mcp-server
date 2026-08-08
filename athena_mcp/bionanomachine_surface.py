from __future__ import annotations

from typing import Any,Dict

from .bionanomachine_protocol import BIONANO_RESOURCE,BIONANO_TOOLS,BIONANO_TOOL_NAMES,BIONANO_VERSION
from .bionanomachine_runtime import BionanomachineRuntime
from .mythic_computation_surface import (
    MythicComputationSurface,
    MYTHIC_COMPUTATION_RESOURCES,
    MYTHIC_COMPUTATION_TOOLS,
    MYTHIC_COMPUTATION_TOOL_NAMES,
    MYTHIC_COMPUTATION_RESOURCE_URIS,
)
from .mythic_strata_surface import (
    MythicStrataSurface,
    MYTHIC_STRATA_RESOURCES,
    MYTHIC_STRATA_TOOLS,
    MYTHIC_STRATA_TOOL_NAMES,
    MYTHIC_STRATA_RESOURCE_URIS,
)

# Compatibility seam: AorDevelopmentSurface already composes this extension bundle.
# Preserve historical export names while unioning independently named MCK surfaces.
# The strata membrane is additive: the original six MCK tools remain unchanged.
BIONANOMACHINE_TOOLS=list(BIONANO_TOOLS)+list(MYTHIC_COMPUTATION_TOOLS)+list(MYTHIC_STRATA_TOOLS)
BIONANOMACHINE_RESOURCES=[BIONANO_RESOURCE]+list(MYTHIC_COMPUTATION_RESOURCES)+list(MYTHIC_STRATA_RESOURCES)
BIONANOMACHINE_TOOL_NAMES=set(BIONANO_TOOL_NAMES)|set(MYTHIC_COMPUTATION_TOOL_NAMES)|set(MYTHIC_STRATA_TOOL_NAMES)
BIONANOMACHINE_RESOURCE_URIS={BIONANO_RESOURCE['uri']}|set(MYTHIC_COMPUTATION_RESOURCE_URIS)|set(MYTHIC_STRATA_RESOURCE_URIS)


class BionanomachineSurface:
    def __init__(self):
        self.runtime=BionanomachineRuntime()
        self.mck=MythicComputationSurface()
        self.strata=MythicStrataSurface()

    def call_tool(self,name:str,args:Dict[str,Any]):
        handled,value=self.strata.call_tool(name,args)
        if handled:return True,value
        handled,value=self.mck.call_tool(name,args)
        if handled:return True,value
        r=self.runtime
        if name=='athena_bionano_catalog':return True,r.catalog(args.get('include_atlas',False))
        if name=='athena_bionano_compile':return True,r.compile(args['machine_id'])
        if name=='athena_bionano_transfer':return True,r.transfer(args['machine_id'],args['target'],args.get('constraints'))
        if name=='athena_bionano_interface_match':return True,r.interface_match(args['producer'],args['consumer'])
        if name=='athena_bionano_convergence_gate':return True,r.convergence_gate(**args)
        if name=='athena_bionano_assembly':return True,r.assembly(args['machine_id'])
        return False,None

    def read_resource(self,uri:str):
        if uri in MYTHIC_STRATA_RESOURCE_URIS:
            return self.strata.read_resource(uri)
        if uri in MYTHIC_COMPUTATION_RESOURCE_URIS:
            return self.mck.read_resource(uri)
        if uri!=BIONANO_RESOURCE['uri']:raise KeyError(uri)
        return {
            'version':BIONANO_VERSION,
            'catalog':self.runtime.catalog(False),
            'benchmark':self.runtime.benchmark(),
            'laws':[
                'BIOLOGICAL_MECHANISM != SOFTWARE_IMPLEMENTATION',
                'MECHANISTIC_ANALOGY != CAUSAL_EQUIVALENCE',
                'USER_SEED != VERIFIED_EMPIRICAL_CONSTANT',
                'INTERFACE_MATCH_PROXY != PHYSICAL_IMPEDANCE',
                'AVAILABLE_TEST != APPLICABLE_TEST',
                'PARTS_LIST != ASSEMBLED_CAPABILITY',
                'ROUTE_EXISTS != INTERFACE_MATCHED',
            ],
            'authority':'MODELED_OPERATOR_LIBRARY_ONLY'
        }

    def benchmark(self):
        result={}
        result.update(self.runtime.benchmark())
        result.update(self.mck.benchmark())
        result['mck_strata']=self.strata.benchmark()
        return result

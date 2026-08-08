from __future__ import annotations

from typing import Any,Dict

from .mythic_strata_protocol import STRATA_RESOURCE,STRATA_TOOLS,STRATA_TOOL_NAMES,STRATA_VERSION
from .mythic_strata_runtime import MythicStrataRuntime

MYTHIC_STRATA_TOOLS=list(STRATA_TOOLS)
MYTHIC_STRATA_RESOURCES=[STRATA_RESOURCE]
MYTHIC_STRATA_TOOL_NAMES=set(STRATA_TOOL_NAMES)
MYTHIC_STRATA_RESOURCE_URIS={STRATA_RESOURCE["uri"]}


class MythicStrataSurface:
    def __init__(self):
        self.runtime=MythicStrataRuntime()

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name!="athena_mck_strata_transport":
            return False,None
        return True,self.runtime.transport(
            args["source"],args["target"],args["operation"],
            args.get("risk_class","NONE"),args.get("target_model_class",""),args.get("explicit_bridge")
        )

    def read_resource(self,uri:str):
        if uri!=STRATA_RESOURCE["uri"]:
            raise KeyError(uri)
        bench=self.runtime.benchmark()
        return {
            "version":STRATA_VERSION,
            "object":"K12 x STRATA transport membrane",
            "benchmark":bench,
            "authority":"PRE_TRANSPORT_GUARD_ONLY",
            "mck_v2_promotion":False,
            "practitioner_review":"HOLD_EXTERNAL_REVIEW",
        }

    def benchmark(self):
        return self.runtime.benchmark()

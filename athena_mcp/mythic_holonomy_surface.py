from __future__ import annotations

from typing import Any,Dict

from .mythic_holonomy_protocol import HOLONOMY_RESOURCE,HOLONOMY_TOOLS,HOLONOMY_TOOL_NAMES,HOLONOMY_VERSION
from .mythic_holonomy_runtime import MythicHolonomyRuntime

MYTHIC_HOLONOMY_TOOLS=list(HOLONOMY_TOOLS)
MYTHIC_HOLONOMY_RESOURCES=[HOLONOMY_RESOURCE]
MYTHIC_HOLONOMY_TOOL_NAMES=set(HOLONOMY_TOOL_NAMES)
MYTHIC_HOLONOMY_RESOURCE_URIS={HOLONOMY_RESOURCE["uri"]}


class MythicHolonomySurface:
    def __init__(self):
        self.runtime=MythicHolonomyRuntime()

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name!="athena_mck_holonomy_evaluate":
            return False,None
        return True,self.runtime.evaluate(
            args["packet"],args.get("source_packet_ref",""),args.get("source_packet_blob_sha","")
        )

    def read_resource(self,uri:str):
        if uri!=HOLONOMY_RESOURCE["uri"]:
            raise KeyError(uri)
        return {
            "version":HOLONOMY_VERSION,
            "object":"held-out semantic transport/holonomy evaluator",
            "arms":["A0_UNSCOPED_REFERENCE","A1_EDGEWISE_STRATA","A2_COMPOSED_HOLONOMY"],
            "distance_vector":[
                "role_delta","decoder_delta","ontology_delta","authority_delta",
                "standing_delta","provenance_delta","invariant_violations","unaccounted_loss"
            ],
            "scalarization":"DISABLED_V0",
            "authority":"READ_ONLY_REPRESENTATION_BENCHMARK_ONLY",
            "practitioner_review":"HOLD_EXTERNAL_REVIEW",
            "mck_v2_promotion":False,
            "laws":[
                "H_gamma != METAPHYSICAL_QUANTITY",
                "SEMANTIC_DRIFT != ERROR_BY_DEFAULT",
                "SOURCE_DERIVED_FEATURE_ENCODING != OBJECTIVE_SEMANTIC_GROUND_TRUTH",
                "SELF_GENERATED_SCORE != INDEPENDENT_WITNESS",
                "BENCHMARK_GAIN != MCK_V2_PROMOTION",
            ],
        }

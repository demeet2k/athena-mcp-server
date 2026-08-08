from __future__ import annotations

from typing import Any,Dict

from .mythic_holonomy_protocol import HOLONOMY_RESOURCE,HOLONOMY_TOOLS,HOLONOMY_TOOL_NAMES,HOLONOMY_VERSION
from .mythic_holonomy_runtime import MythicHolonomyRuntime
from .mythic_holonomy_standing import apply_projection_standing
from .mythic_holonomy_connection_v1 import (
    CONNECTION_RESOURCE,
    CONNECTION_RESOURCES,
    CONNECTION_RESOURCE_URIS,
    CONNECTION_TOOLS,
    CONNECTION_TOOL_NAMES,
    CONNECTION_VERSION,
    ClosedHolonomyConnectionRuntime,
    connection_resource_payload,
)

MYTHIC_HOLONOMY_TOOLS=list(HOLONOMY_TOOLS)+list(CONNECTION_TOOLS)
MYTHIC_HOLONOMY_RESOURCES=[HOLONOMY_RESOURCE]+list(CONNECTION_RESOURCES)
MYTHIC_HOLONOMY_TOOL_NAMES=set(HOLONOMY_TOOL_NAMES)|set(CONNECTION_TOOL_NAMES)
MYTHIC_HOLONOMY_RESOURCE_URIS={HOLONOMY_RESOURCE["uri"]}|set(CONNECTION_RESOURCE_URIS)


class MythicHolonomySurface:
    def __init__(self):
        self.runtime=MythicHolonomyRuntime()
        self.connection_v1=ClosedHolonomyConnectionRuntime()

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=="athena_mck_closed_holonomy_evaluate":
            return True,self.connection_v1.evaluate(args["packet"])
        if name!="athena_mck_holonomy_evaluate":
            return False,None
        raw=self.runtime.evaluate(
            args["packet"],args.get("source_packet_ref",""),args.get("source_packet_blob_sha","")
        )
        return True,apply_projection_standing(args["packet"],raw)

    def read_resource(self,uri:str):
        if uri==CONNECTION_RESOURCE["uri"]:
            return connection_resource_payload()
        if uri!=HOLONOMY_RESOURCE["uri"]:
            raise KeyError(uri)
        return {
            "version":HOLONOMY_VERSION,
            "object":"held-out semantic transport evaluator with V0 open-path representation-drift proxy",
            "arms":["A0_UNSCOPED_REFERENCE","A1_EDGEWISE_STRATA","A2_COMPOSED_HOLONOMY"],
            "distance_vector":[
                "role_delta","decoder_delta","ontology_delta","authority_delta",
                "standing_delta","provenance_delta","invariant_violations","unaccounted_loss"
            ],
            "scalarization":"DISABLED_V0",
            "loop_vector_standing":"OPEN_PATH_DRIFT_PROXY_NO_PROJECTION_BACK_OPERATOR_V0",
            "projection_back_executed":False,
            "projection_back_operator":"UNDEFINED_V0",
            "closed_loop_holonomy":"UNKNOWN_NO_TYPED_PROJECTION_BACK_OPERATOR_V0",
            "connection_v1_resource":CONNECTION_RESOURCE["uri"],
            "connection_v1_version":CONNECTION_VERSION,
            "authority":"READ_ONLY_REPRESENTATION_BENCHMARK_ONLY",
            "practitioner_review":"HOLD_EXTERNAL_REVIEW",
            "mck_v2_promotion":False,
            "laws":[
                "H_gamma != METAPHYSICAL_QUANTITY",
                "SEMANTIC_DRIFT != ERROR_BY_DEFAULT",
                "SOURCE_DERIVED_FEATURE_ENCODING != OBJECTIVE_SEMANTIC_GROUND_TRUTH",
                "SELF_GENERATED_SCORE != INDEPENDENT_WITNESS",
                "BENCHMARK_GAIN != MCK_V2_PROMOTION",
                "OPEN_PATH_ENDPOINT_DRIFT != CLOSED_LOOP_HOLONOMY",
                "PROJECTION_BACK_LABEL != EXECUTED_PROJECTION_OPERATOR",
                "CLOSED_ENDPOINT_IDENTITY != PATH_STATE_TRANSPORT",
                "V0_OPEN_PATH_PROXY != V1_CLOSED_LOOP_OPERATOR_WITNESS",
            ],
        }

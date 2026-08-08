from __future__ import annotations

from typing import Any, Dict

from .mythic_computation_protocol import MCK_RESOURCE, MCK_TOOLS, MCK_TOOL_NAMES, MCK_VERSION
from .mythic_computation_runtime import MythicComputationRuntime

MYTHIC_COMPUTATION_TOOLS = list(MCK_TOOLS)
MYTHIC_COMPUTATION_RESOURCES = [MCK_RESOURCE]
MYTHIC_COMPUTATION_TOOL_NAMES = set(MCK_TOOL_NAMES)
MYTHIC_COMPUTATION_RESOURCE_URIS = {MCK_RESOURCE["uri"]}


class MythicComputationSurface:
    def __init__(self):
        self.runtime = MythicComputationRuntime()

    def call_tool(self, name: str, args: Dict[str, Any]):
        r = self.runtime
        if name == "athena_mck_symbolic_address":
            return True, r.symbolic_address(args["query"], args["address_space"], args.get("context", ""))
        if name == "athena_mck_correspondence_route":
            return True, r.correspondence_route(args["src"], args["dst"], args["edges"], args.get("max_depth", 8))
        if name == "athena_mck_oracle_decode":
            return True, r.oracle_decode(
                args["query"], args["codebook"], args.get("sample"), args.get("seed"), args.get("use_case", "GENERAL")
            )
        if name == "athena_mck_protocol_machine":
            return True, r.protocol_machine(
                args["boundary"],
                args["phase"],
                args["steps"],
                args.get("mode", "TRANSFORMING"),
                args.get("risk_class", "NONE"),
                args.get("witness"),
            )
        if name == "athena_mck_model_bridge":
            return True, r.model_bridge(
                args["source_model"],
                args["target_model"],
                args["field_map"],
                args.get("invariants"),
                args.get("source_ref"),
                args.get("target_ref"),
            )
        if name == "athena_mck_epistemic_split":
            return True, r.epistemic_split(
                args["items"], args.get("requested_promotion"), args.get("use_case", "GENERAL")
            )
        return False, None

    def read_resource(self, uri: str):
        if uri != MCK_RESOURCE["uri"]:
            raise KeyError(uri)
        benchmark = self.runtime.benchmark()
        return {
            "version": MCK_VERSION,
            "operators": [
                "SAC_SYMBOLIC_ADDRESS_COMPILER",
                "CGR_CORRESPONDENCE_GRAPH_ROUTER",
                "OSD_ORACLE_SAMPLER_DECODER",
                "RSM_PROTOCOL_STATE_MACHINE",
                "MMTB_MODEL_BRIDGE",
                "ESCPF_EPISTEMIC_SPLITTER",
            ],
            "kernel12": ["Q", "OMEGA", "SIGMA", "GAMMA", "B", "THETA", "PI", "R", "W", "D", "U", "M"],
            "stable_spine": ["Q", "SIGMA", "PI", "W", "M"],
            "high_variance": ["B", "THETA", "R", "D"],
            "benchmark": benchmark,
            "laws": list(benchmark["laws"]) + [
                "TRADITION_INTERNAL != EMPIRICAL_CAUSATION",
                "SYMBOLIC_CORRESPONDENCE != PHYSICAL_CAUSAL_EDGE",
                "R != W != D != INTERPRETATION",
                "W != D != U",
                "MODEL_BRIDGE != CULTURAL_IDENTITY",
            ],
            "authority": "BOUNDED_SYMBOLIC_COMPUTATION_ONLY",
        }

    def benchmark(self):
        return self.runtime.benchmark()

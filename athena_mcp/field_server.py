from __future__ import annotations

import argparse
import json
import os
import sys

from .composition_integrity import composition_certificate
from .stack_server import STACK_LAYERS,STACK_VERSION,StackServer,stack_manifest
from .orchestration_field import FieldLedger
from .orchestration_field_protocol import FIELD_RESOURCE,FIELD_TOOLS
from .orchestration_field_surface import FIELD_TOOL_NAMES,call_field_tool,field_resource_value
from .promotion import PromotionLedger
from .promotion_protocol import PROMOTION_RESOURCE,PROMOTION_TOOLS,PROMOTION_TOOL_NAMES
from .surface_contract import audit_surface,contract_manifest
from .surface_protocol import SURFACE_RESOURCE,SURFACE_TOOLS,SURFACE_TOOL_NAMES
from .validate import validate

FIELD_STACK_VERSION="AOR.STACK.3+FIELD.1+AOR.3.5"


def field_stack_manifest():
    base=stack_manifest()
    layers=list(base["layers"])+[
        {
            "index":len(base["layers"]),
            "name":"FIELD1",
            "server":"FieldServer",
            "role":"provenance-preserving module-residual/action-candidate assembly; generated metrics remain unmeasured",
            "epistemic_status":"EXECUTABLE_ASSEMBLY_NOT_IDEA_OR_METRIC_GENERATOR",
        },
        {
            "index":len(base["layers"])+1,
            "name":"ROBUSTNESS1",
            "server":"FieldServer/base surface",
            "role":"persisted AORRUN successor rank-sensitivity certificate",
            "epistemic_status":"RANK_SENSITIVITY_NOT_TRUTH_PROBABILITY",
        },
        {
            "index":len(base["layers"])+2,
            "name":"SURFACE1",
            "server":"FieldServer",
            "role":"mature-organ discovery contract and anti-regression audit",
            "epistemic_status":"DISCOVERY_COMPOSITION_AUDIT",
        },
        {
            "index":len(base["layers"])+3,
            "name":"COMPOSITION1",
            "server":"FieldServer",
            "role":"MRO + organ-instance + representative read-only dispatch certificate",
            "epistemic_status":"RUNTIME_WIRING_NOT_SEMANTIC_PROOF",
        },
        {
            "index":len(base["layers"])+4,
            "name":"PROMOTION1",
            "server":"FieldServer",
            "role":"persistent exact-head promotion receipt binding local surface/composition certificates to explicit external CI/smoke attestations",
            "epistemic_status":"PROMOTION_PREDICATE_NOT_SEMANTIC_PROOF",
        },
    ]
    return {
        **base,
        "version":FIELD_STACK_VERSION,
        "layers":layers,
        "default_candidate":"FieldServer",
        "promotion_gate":"PROMRUN.QUALIFIED iff local surface+composition PASS and explicit CI+smoke success attestations bind to the exact candidate Git head",
    }


class FieldServer(StackServer):
    """Promoted fully composed AOR runtime with persistent promotion receipts."""
    def __init__(self,db,git_root=None):
        super().__init__(db,git_root)
        self.field=FieldLedger(self.core)
        self.promotion=PromotionLedger(self.core)
        self._field_tools={tool["name"]:tool for tool in FIELD_TOOLS}
        self._surface_tools={tool["name"]:tool for tool in SURFACE_TOOLS}
        self._promotion_tools={tool["name"]:tool for tool in PROMOTION_TOOLS}

    def _discovered_surface(self):
        tools=self.handle({"jsonrpc":"2.0","id":"surface-tools","method":"tools/list"})["result"]["tools"]
        resources=self.handle({"jsonrpc":"2.0","id":"surface-resources","method":"resources/list"})["result"]["resources"]
        return [tool["name"] for tool in tools],[resource["uri"] for resource in resources]

    def surface_audit(self,run_probes=True):
        tool_names,resource_uris=self._discovered_surface()
        surface=audit_surface(tool_names,resource_uris)
        composition=composition_certificate(self,run_probes=run_probes)
        surface["surface_status"]=surface["status"]
        surface["composition"]=composition
        surface["status"]="PASS" if surface["surface_status"]=="PASS" and composition["status"]=="PASS" else "FAIL"
        return surface

    def call_tool(self,name,args):
        if name in FIELD_TOOL_NAMES:return call_field_tool(self.field,name,args)
        if name=="athena_surface_audit":return self.surface_audit()
        if name=="athena_promotion_evaluate":
            return self.promotion.evaluate(
                "FieldServer",
                args["git_head"],
                self.surface_audit(),
                args["ci_witness"],
                args["smoke_witness"],
                args.get("actor","agent"),
                args.get("persist",True),
            )
        if name=="athena_promotion_get":return self.promotion.get(args["run_id"])
        if name=="athena_promotion_replay":return self.promotion.replay(args["run_id"])
        if name=="athena_promotion_recent":return self.promotion.recent(args.get("limit",20))
        if name=="athena_benchmark":
            result=super().call_tool(name,args)
            result.update(self.field.benchmark())
            result.update(self.promotion.benchmark())
            audit=self.surface_audit()
            result["surface_audit"]=audit["status"]
            result["composition_audit"]=audit["composition"]["status"]
            return result
        return super().call_tool(name,args)

    def handle(self,message):
        method=message.get("method");params=message.get("params") or {};mid=message.get("id")
        if method=="tools/list":
            base=super().handle(message)
            tools=list(base["result"]["tools"])+list(FIELD_TOOLS)+list(SURFACE_TOOLS)+list(PROMOTION_TOOLS)
            base["result"]["tools"]=sorted({tool["name"]:tool for tool in tools}.values(),key=lambda x:x["name"])
            return base
        if method=="tools/call" and params.get("name") in FIELD_TOOL_NAMES|SURFACE_TOOL_NAMES|PROMOTION_TOOL_NAMES:
            name=params["name"];args=params.get("arguments") or {};tool_map={**self._field_tools,**self._surface_tools,**self._promotion_tools}
            if not self.rate.allow(name):return self.result(mid,{"content":[{"type":"text","text":"Rate limit exceeded; retry later."}],"isError":True})
            try:
                validate(tool_map[name]["inputSchema"],args);value=self.call_tool(name,args)
                return self.result(mid,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}],"structuredContent":value,"isError":False})
            except (ValueError,KeyError) as exc:
                return self.result(mid,{"content":[{"type":"text","text":str(exc)}],"isError":True})
        if method=="resources/list":
            base=super().handle(message);resources=list(base["result"]["resources"])
            for resource in (FIELD_RESOURCE,SURFACE_RESOURCE,PROMOTION_RESOURCE):
                if resource["uri"] not in {r["uri"] for r in resources}:resources.append(resource)
            base["result"]["resources"]=resources;return base
        if method=="resources/read" and params.get("uri")==FIELD_RESOURCE["uri"]:
            value=field_resource_value(self.field)
            return self.result(mid,{"contents":[{"uri":FIELD_RESOURCE["uri"],"mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=="resources/read" and params.get("uri")==SURFACE_RESOURCE["uri"]:
            value={"contract":contract_manifest(),"audit":self.surface_audit()}
            return self.result(mid,{"contents":[{"uri":SURFACE_RESOURCE["uri"],"mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=="resources/read" and params.get("uri")==PROMOTION_RESOURCE["uri"]:
            value={"version":"ATHENA.PROMOTION.1","recent":self.promotion.recent(20),"benchmark":self.promotion.benchmark(),"law":"promotion is exact-head state: local surface/composition certificates plus explicit externally-attested CI/smoke success on the same Git SHA"}
            return self.result(mid,{"contents":[{"uri":PROMOTION_RESOURCE["uri"],"mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=="resources/read" and params.get("uri")=="athena://stack":
            value=field_stack_manifest()
            return self.result(mid,{"contents":[{"uri":"athena://stack","mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=="prompts/get" and params.get("name")=="athena_maxdev":
            base=super().handle(message);messages=base.get("result",{}).get("messages",[])
            if messages:
                content=messages[0].get("content",{})
                content["text"]=content.get("text","")+"""
19 FIELD/PHI: `Phi=maxSX(q,B,C,eco{K,H,S,a,Z})` is not a license for a magic idea generator. FIELD.1 assembles actual unresolved work emitted by SX.1, RAG.1, Y.1, GAP.1, HUG.ABI.1, branch REVIEW and AOR measurement/calibration into typed action candidates with exact source receipts and dependency edges. Generated actions are `metric_state=UNMEASURED`; do not invent readiness/gain/cost/DeltaJ/etc. Exact identical action signatures may merge provenance. If explicit measurements disagree on an exact action, mark `metric_state=CONFLICT`, strip disputed AOR operands and route to remeasurement/adjudication. Preserve ecosystem constraints as data, then hand FIELD candidates to AOR only after lawful measurement/calibration/gating. Persist exact module inputs and candidate/provenance graph as FIELDRUN for replay.
20 SURFACE/PROMOTION: the package default may claim a mature organ only when the composed runtime exposes it under ATHENA.SURFACE.1. A new organ extends the surface; it does not silently replace unrelated tools/resources. Robustness certificates remain post-decision rank sensitivity bound to AORRUN decision_digest, not hidden NEXT score terms.
21 COMPOSITION/ABI: discovery is necessary but not sufficient. COMPOSITION verifies expected server MRO, initialized mature organ instances, and representative read-only calls through BRANCH/Y/RAG/HUG/GAP/FIELD/PROMOTION. Composition PASS certifies wiring/dispatch reachability, not semantic truth.
22 PROMOTION/RECEIPT: runtime promotion is persistent exact-head state. `PROMRUN.QUALIFIED` requires candidate_server=FieldServer, local SurfacePass, local CompositionPass, CI witness `{observed:true,ref,head_sha=git_head,conclusion:success}`, and an independent smoke witness with the same exact head. External CI/smoke packets remain caller-supplied attestations; storing them does not relabel them as independently fetched evidence. Any code change invalidates promotion for the new head until a new exact-head receipt is produced.
"""
            return base
        return super().handle(message)


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument("--db",default=os.getenv("ATHENA_DB","./state/athena.db"));parser.add_argument("--git-root",default=os.getenv("ATHENA_GIT_ROOT"));args=parser.parse_args(argv);server=FieldServer(args.db,args.git_root)
    for raw in sys.stdin:
        raw=raw.strip()
        if not raw:continue
        try:message=json.loads(raw);response=server.handle(message)
        except Exception as exc:response={"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":f"Parse error: {exc}"}}
        if response is not None:sys.stdout.write(json.dumps(response,separators=(",",":"),ensure_ascii=False)+"\n");sys.stdout.flush()


if __name__=="__main__":main()

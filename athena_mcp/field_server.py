from __future__ import annotations

import argparse
import json
import os
import sys

from .stack_server import STACK_LAYERS,STACK_VERSION,StackServer,stack_manifest
from .orchestration_field import FieldLedger
from .orchestration_field_protocol import FIELD_RESOURCE,FIELD_TOOLS
from .orchestration_field_surface import FIELD_TOOL_NAMES,call_field_tool,field_resource_value
from .validate import validate

FIELD_STACK_VERSION="AOR.STACK.3+FIELD.1"


def field_stack_manifest():
    base=stack_manifest()
    layers=list(base["layers"])+[
        {
            "index":len(base["layers"]),
            "name":"FIELD1",
            "server":"FieldServer",
            "role":"provenance-preserving module-residual/action-candidate assembly; generated metrics remain unmeasured",
            "epistemic_status":"EXECUTABLE_ASSEMBLY_NOT_IDEA_OR_METRIC_GENERATOR",
        }
    ]
    return {
        **base,
        "version":FIELD_STACK_VERSION,
        "layers":layers,
        "default_candidate":"FieldServer",
    }


class FieldServer(StackServer):
    """Top staged AOR composition candidate: StackServer + FIELD.1.

    This class is intentionally not the package default until the whole-suite
    regression/promotion gate is witnessed on the exact head.
    """
    def __init__(self,db,git_root=None):
        super().__init__(db,git_root)
        self.field=FieldLedger(self.core)
        self._field_tools={tool["name"]:tool for tool in FIELD_TOOLS}

    def call_tool(self,name,args):
        if name in FIELD_TOOL_NAMES:return call_field_tool(self.field,name,args)
        if name=="athena_benchmark":
            result=super().call_tool(name,args);result.update(self.field.benchmark());return result
        return super().call_tool(name,args)

    def handle(self,message):
        method=message.get("method");params=message.get("params") or {};mid=message.get("id")
        if method=="tools/list":
            base=super().handle(message);tools=list(base["result"]["tools"])+list(FIELD_TOOLS)
            base["result"]["tools"]=sorted({tool["name"]:tool for tool in tools}.values(),key=lambda x:x["name"]);return base
        if method=="tools/call" and params.get("name") in FIELD_TOOL_NAMES:
            name=params["name"];args=params.get("arguments") or {}
            if not self.rate.allow(name):return self.result(mid,{"content":[{"type":"text","text":"Rate limit exceeded; retry later."}],"isError":True})
            try:
                validate(self._field_tools[name]["inputSchema"],args);value=self.call_tool(name,args)
                return self.result(mid,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}],"structuredContent":value,"isError":False})
            except (ValueError,KeyError) as exc:
                return self.result(mid,{"content":[{"type":"text","text":str(exc)}],"isError":True})
        if method=="resources/list":
            base=super().handle(message);resources=list(base["result"]["resources"])
            if FIELD_RESOURCE["uri"] not in {r["uri"] for r in resources}:resources.append(FIELD_RESOURCE)
            base["result"]["resources"]=resources;return base
        if method=="resources/read" and params.get("uri")==FIELD_RESOURCE["uri"]:
            value=field_resource_value(self.field)
            return self.result(mid,{"contents":[{"uri":FIELD_RESOURCE["uri"],"mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=="resources/read" and params.get("uri")=="athena://stack":
            value=field_stack_manifest()
            return self.result(mid,{"contents":[{"uri":"athena://stack","mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=="prompts/get" and params.get("name")=="athena_maxdev":
            base=super().handle(message);messages=base.get("result",{}).get("messages",[])
            if messages:
                content=messages[0].get("content",{})
                content["text"]=content.get("text","")+"""
19 FIELD/PHI: `Phi=maxSX(q,B,C,eco{K,H,S,a,Z})` is not a license for a magic idea generator. FIELD.1 assembles actual unresolved work emitted by SX.1, RAG.1, Y.1, GAP.1, HUG.ABI.1, branch REVIEW and AOR measurement/calibration into typed action candidates with exact source receipts and dependency edges. Generated actions are `metric_state=UNMEASURED`; do not invent readiness/gain/cost/DeltaJ/etc. Exact identical action signatures may merge provenance. If explicit measurements disagree on an exact action, mark `metric_state=CONFLICT`, strip disputed AOR operands and route to remeasurement/adjudication. Preserve ecosystem constraints as data, then hand FIELD candidates to AOR only after lawful measurement/calibration/gating. Persist exact module inputs and candidate/provenance graph as FIELDRUN for replay.
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

from __future__ import annotations

import argparse
import json
import os
import sys

from .hug_server import HugServer
from .orchestration_gap import GapLedger
from .orchestration_gap_protocol import GAP_RESOURCE,GAP_TOOLS
from .orchestration_gap_surface import GAP_TOOL_NAMES,call_gap_tool,gap_resource_value
from .validate import validate


class GapServer(HugServer):
    """HugServer + witnessed reachability closure / target residual compiler."""
    def __init__(self,db,git_root=None):
        super().__init__(db,git_root);self.gap=GapLedger(self.core);self._gap_tools={tool['name']:tool for tool in GAP_TOOLS}

    def call_tool(self,name,args):
        if name in GAP_TOOL_NAMES:return call_gap_tool(self.gap,name,args)
        if name=='athena_benchmark':
            result=super().call_tool(name,args);result.update(self.gap.benchmark());return result
        return super().call_tool(name,args)

    def handle(self,message):
        method=message.get('method');params=message.get('params') or {};mid=message.get('id')
        if method=='tools/list':
            base=super().handle(message);tools=list(base['result']['tools'])+list(GAP_TOOLS);base['result']['tools']=sorted({t['name']:t for t in tools}.values(),key=lambda x:x['name']);return base
        if method=='tools/call' and params.get('name') in GAP_TOOL_NAMES:
            name=params['name'];args=params.get('arguments') or {}
            if not self.rate.allow(name):return self.result(mid,{'content':[{'type':'text','text':'Rate limit exceeded; retry later.'}],'isError':True})
            try:
                validate(self._gap_tools[name]['inputSchema'],args);value=self.call_tool(name,args);return self.result(mid,{'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}],'structuredContent':value,'isError':False})
            except (ValueError,KeyError) as exc:return self.result(mid,{'content':[{'type':'text','text':str(exc)}],'isError':True})
        if method=='resources/list':
            base=super().handle(message);resources=list(base['result']['resources'])
            if GAP_RESOURCE['uri'] not in {r['uri'] for r in resources}:resources.append(GAP_RESOURCE)
            base['result']['resources']=resources;return base
        if method=='resources/read' and params.get('uri')==GAP_RESOURCE['uri']:
            value=gap_resource_value(self.gap);return self.result(mid,{'contents':[{'uri':GAP_RESOURCE['uri'],'mimeType':'application/json','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=='prompts/get' and params.get('name')=='athena_maxdev':
            base=super().handle(message);messages=base.get('result',{}).get('messages',[])
            if messages:
                content=messages[0].get('content',{});content['text']=content.get('text','')+"""
18 GAP/CLOSURE: `gap = Target - Closure(S,H,B,C,G)` must name the closure operator. GAP.1 currently implements witnessed directed reachability only, not logical or causal entailment. Freeze explicit source groups S/H/B/C (and any additional named groups), typed edges, traversable relation set, allowed statuses, witness requirement, and max depth. Only admissible edges enter closure; rejected edges surface defects. Every reached target carries its path witness back to an origin group. Uncovered targets become residuals. `grow=max severity*leverage*information_gain/cost` only when all operands are KNOWN; missing metrics route to measurement_plan, never zero. Persist sources+edges+targets+policy as GAPRUN; replay uses the frozen graph snapshot, so later graph mutation cannot rewrite historical gap/grow decisions. Do not call reachability proof.
"""
            return base
        return super().handle(message)


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--db',default=os.getenv('ATHENA_DB','./state/athena.db'));parser.add_argument('--git-root',default=os.getenv('ATHENA_GIT_ROOT'));args=parser.parse_args(argv);server=GapServer(args.db,args.git_root)
    for raw in sys.stdin:
        raw=raw.strip()
        if not raw:continue
        try:message=json.loads(raw);response=server.handle(message)
        except Exception as exc:response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':f'Parse error: {exc}'}}
        if response is not None:sys.stdout.write(json.dumps(response,separators=(',',':'),ensure_ascii=False)+'\n');sys.stdout.flush()

if __name__=='__main__':main()

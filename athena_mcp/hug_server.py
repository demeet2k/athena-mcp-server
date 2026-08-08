from __future__ import annotations

import argparse
import json
import os
import sys

from .retrieval_server import RetrievalServer
from .orchestration_hug import HugRegistry
from .orchestration_hug_protocol import HUG_RESOURCE,HUG_TOOLS
from .orchestration_hug_surface import HUG_TOOL_NAMES,call_hug_tool,hug_resource_value
from .validate import validate


class HugServer(RetrievalServer):
    """RetrievalServer + fail-closed registered HUG execution ABI."""
    def __init__(self,db,git_root=None):
        super().__init__(db,git_root);self.hug=HugRegistry(self.core);self._hug_tools={tool['name']:tool for tool in HUG_TOOLS}

    def call_tool(self,name,args):
        if name in HUG_TOOL_NAMES:return call_hug_tool(self.hug,name,args)
        if name=='athena_benchmark':
            result=super().call_tool(name,args);result.update(self.hug.benchmark());return result
        return super().call_tool(name,args)

    def handle(self,message):
        method=message.get('method');params=message.get('params') or {};mid=message.get('id')
        if method=='tools/list':
            base=super().handle(message);tools=list(base['result']['tools'])+list(HUG_TOOLS);base['result']['tools']=sorted({t['name']:t for t in tools}.values(),key=lambda x:x['name']);return base
        if method=='tools/call' and params.get('name') in HUG_TOOL_NAMES:
            name=params['name'];args=params.get('arguments') or {}
            if not self.rate.allow(name):return self.result(mid,{'content':[{'type':'text','text':'Rate limit exceeded; retry later.'}],'isError':True})
            try:
                validate(self._hug_tools[name]['inputSchema'],args);value=self.call_tool(name,args);return self.result(mid,{'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}],'structuredContent':value,'isError':False})
            except (ValueError,KeyError) as exc:return self.result(mid,{'content':[{'type':'text','text':str(exc)}],'isError':True})
        if method=='resources/list':
            base=super().handle(message);resources=list(base['result']['resources'])
            if HUG_RESOURCE['uri'] not in {r['uri'] for r in resources}:resources.append(HUG_RESOURCE)
            base['result']['resources']=resources;return base
        if method=='resources/read' and params.get('uri')==HUG_RESOURCE['uri']:
            value=hug_resource_value(self.hug);return self.result(mid,{'contents':[{'uri':HUG_RESOURCE['uri'],'mimeType':'application/json','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=='prompts/get' and params.get('name')=='athena_maxdev':
            base=super().handle(message);messages=base.get('result',{}).get('messages',[])
            if messages:
                content=messages[0].get('content',{});content['text']=content.get('text','')+"""
17 HUG ABI: do not invent or paraphrase HUG(io,au,fx,lm,er,st) when the canonical algorithm is unresolved. A HUG implementation becomes callable only after exact algorithm_ref + implementation_digest + meanings for all six parameters + input/output schemas are registered. Registration=CANDIDATE, not execution. CANDIDATE->TESTED requires procedure+observation+result+witness; TESTED->CANONICAL requires explicit authorized ref; skips fail. HUGINV freezes implementation snapshot, exactly six arguments, context (including RAGRUN/B refs when relevant), and input digest. HUG plan returns PLANNED only; a real external/registered executor must produce output and verified execution receipt before COMPLETED. Packet digest replay proves invocation integrity, not semantic algorithm replay. Until a canonical QHUG implementation is actually recovered/registered, fail closed rather than substituting another algorithm.
"""
            return base
        return super().handle(message)


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--db',default=os.getenv('ATHENA_DB','./state/athena.db'));parser.add_argument('--git-root',default=os.getenv('ATHENA_GIT_ROOT'));args=parser.parse_args(argv);server=HugServer(args.db,args.git_root)
    for raw in sys.stdin:
        raw=raw.strip()
        if not raw:continue
        try:message=json.loads(raw);response=server.handle(message)
        except Exception as exc:response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':f'Parse error: {exc}'}}
        if response is not None:sys.stdout.write(json.dumps(response,separators=(',',':'),ensure_ascii=False)+'\n');sys.stdout.flush()

if __name__=='__main__':main()

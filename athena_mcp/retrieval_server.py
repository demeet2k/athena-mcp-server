from __future__ import annotations

import argparse
import json
import os
import sys

from .development_server import DevelopmentServer
from .orchestration_retrieval import RetrievalLedger
from .orchestration_retrieval_protocol import RETRIEVAL_RESOURCE, RETRIEVAL_TOOLS
from .orchestration_retrieval_surface import RETRIEVAL_TOOL_NAMES, call_retrieval_tool, retrieval_resource_value
from .validate import validate


class RetrievalServer(DevelopmentServer):
    """DevelopmentServer + replayable RAG.1 source-selection organ."""

    def __init__(self, db, git_root=None):
        super().__init__(db, git_root)
        self.retrieval = RetrievalLedger(self.core)
        self._retrieval_tools = {tool['name']: tool for tool in RETRIEVAL_TOOLS}

    def call_tool(self, name, args):
        if name in RETRIEVAL_TOOL_NAMES:
            return call_retrieval_tool(self.retrieval, name, args, self.equivalence)
        if name == 'athena_benchmark':
            result = super().call_tool(name, args)
            result.update(self.retrieval.benchmark())
            return result
        return super().call_tool(name, args)

    def handle(self, message):
        method = message.get('method')
        params = message.get('params') or {}
        mid = message.get('id')

        if method == 'tools/list':
            base = super().handle(message)
            tools = list(base['result']['tools']) + list(RETRIEVAL_TOOLS)
            base['result']['tools'] = sorted({tool['name']: tool for tool in tools}.values(), key=lambda x: x['name'])
            return base

        if method == 'tools/call' and params.get('name') in RETRIEVAL_TOOL_NAMES:
            name = params['name']; args = params.get('arguments') or {}
            if not self.rate.allow(name):
                return self.result(mid, {'content':[{'type':'text','text':'Rate limit exceeded; retry later.'}],'isError':True})
            try:
                validate(self._retrieval_tools[name]['inputSchema'], args)
                value = self.call_tool(name, args)
                return self.result(mid, {'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}],'structuredContent':value,'isError':False})
            except (ValueError, KeyError) as exc:
                return self.result(mid, {'content':[{'type':'text','text':str(exc)}],'isError':True})

        if method == 'resources/list':
            base = super().handle(message)
            resources = list(base['result']['resources'])
            if RETRIEVAL_RESOURCE['uri'] not in {r['uri'] for r in resources}:
                resources.append(RETRIEVAL_RESOURCE)
            base['result']['resources'] = resources
            return base

        if method == 'resources/read' and params.get('uri') == RETRIEVAL_RESOURCE['uri']:
            value = retrieval_resource_value(self.retrieval)
            return self.result(mid, {'contents':[{'uri':RETRIEVAL_RESOURCE['uri'],'mimeType':'application/json','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}]})

        if method == 'prompts/get' and params.get('name') == 'athena_maxdev':
            base = super().handle(message)
            messages = base.get('result', {}).get('messages', [])
            if messages:
                content = messages[0].get('content', {})
                content['text'] = content.get('text', '') + """
16 RETRIEVAL/RAG.1: B=RAG(q,SX,kappa;rel*auth*fresh*cross/cost) means decision-conditioned selection over actual supplied/retrieved provenance records, never a claim that unseen sources were searched. Require witnessed 0..1 measurements for relevance, source_authority, cross_value and decision_relevance; source_authority is retrieval provenance quality, not Y claim authority. Compute freshness from frozen as_of/source_time/half-life, and coordinate/lineage fit from explicit query preferences. Missing measurements/timestamps/cost remain UNKNOWN and enter measurement_plan. Select under carrier/resource cost with required role/facet coverage; exact subset enumeration <=18 rankable candidates may claim PROVEN_FOR_DECLARED_UTILITY, larger fallback must say HEURISTIC_NOT_PROVEN. If EQ.1 context is supplied, snapshot it before selection; only contradiction-free witnessed equivalence may collapse source alternatives, while conflict/UNKNOWN preserves identity. Persist query+candidates+EQ snapshot+selection as RAGRUN and replay from frozen input.
"""
            return base

        return super().handle(message)


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--db',default=os.getenv('ATHENA_DB','./state/athena.db'));parser.add_argument('--git-root',default=os.getenv('ATHENA_GIT_ROOT'));args=parser.parse_args(argv)
    server=RetrievalServer(args.db,args.git_root)
    for raw in sys.stdin:
        raw=raw.strip()
        if not raw:continue
        try:message=json.loads(raw);response=server.handle(message)
        except Exception as exc:response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':f'Parse error: {exc}'}}
        if response is not None:sys.stdout.write(json.dumps(response,separators=(',',':'),ensure_ascii=False)+'\n');sys.stdout.flush()


if __name__=='__main__':main()

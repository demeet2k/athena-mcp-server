from __future__ import annotations

import argparse
import json
import os
import sys

from .gap_server import GapServer

STACK_VERSION="AOR.STACK.3"
STACK_LAYERS=[
    {"index":0,"name":"BASE_RUNTIME","server":"Server","role":"CCR/JSPACE/SCALE/KC144/crystals/transforms/emissions/sessions/Git-CAS"},
    {"index":1,"name":"BRANCH_EVOLUTION","role":"basis-specific witnessed ACTIVE/HIBERNATED/REVIEW lifecycle"},
    {"index":2,"name":"AUTHORITY_Y1","server":"AuthorityServer","role":"non-skippable ?->+->!-># typed claim authority"},
    {"index":3,"name":"EQ1_SX1","server":"DevelopmentServer","role":"witnessed equivalence quotient + bounded recursive extraction tasks"},
    {"index":4,"name":"RAG1","server":"RetrievalServer","role":"decision-conditioned coverage/EQ-safe retrieval selection + RAGRUN"},
    {"index":5,"name":"HUG_ABI1","server":"HugServer","role":"fail-closed registered HUG implementation/invocation ABI","semantic_status":"CANONICAL_QHUG_ALGORITHM_UNRESOLVED_UNTIL_REGISTERED"},
    {"index":6,"name":"GAP1","server":"GapServer","role":"witnessed directed reachability closure + target residual/GAPRUN","epistemic_status":"REACHABILITY_NOT_LOGICAL_PROOF"},
]


def stack_manifest():
    return {
        "version":STACK_VERSION,
        "layers":STACK_LAYERS,
        "composition":"each layer subclasses/delegates to the previous layer; unknown tools/resources flow downward",
        "anti_regression":"adding an organ must preserve unrelated mature surfaces unless explicit supersession/migration is declared and tested",
        "default_candidate":"StackServer",
        "unresolved":[
            "canonical semantic QHUG implementation/equations/parameter meanings",
            "logical/causal closure operator beyond witnessed graph reachability",
        ],
    }


class StackServer(GapServer):
    """Named top-level composition candidate for the modular AOR.3 stack."""
    def handle(self,message):
        method=message.get('method');params=message.get('params') or {};mid=message.get('id')
        if method=='resources/list':
            base=super().handle(message);resources=list(base['result']['resources'])
            if 'athena://stack' not in {r['uri'] for r in resources}:resources.append({'uri':'athena://stack','name':'AOR.3 Modular Runtime Stack Manifest','mimeType':'application/json'})
            base['result']['resources']=resources;return base
        if method=='resources/read' and params.get('uri')=='athena://stack':
            value=stack_manifest();return self.result(mid,{'contents':[{'uri':'athena://stack','mimeType':'application/json','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        return super().handle(message)


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--db',default=os.getenv('ATHENA_DB','./state/athena.db'));parser.add_argument('--git-root',default=os.getenv('ATHENA_GIT_ROOT'));args=parser.parse_args(argv);server=StackServer(args.db,args.git_root)
    for raw in sys.stdin:
        raw=raw.strip()
        if not raw:continue
        try:message=json.loads(raw);response=server.handle(message)
        except Exception as exc:response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':f'Parse error: {exc}'}}
        if response is not None:sys.stdout.write(json.dumps(response,separators=(',',':'),ensure_ascii=False)+'\n');sys.stdout.flush()

if __name__=='__main__':main()

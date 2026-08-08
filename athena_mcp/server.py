from __future__ import annotations
import argparse, json, os, sys, time
from collections import defaultdict, deque
from .store import Store
from .core import AthenaCore, StaleTarget
from .kc144 import station_manifest
from .validate import validate
from .bootstrap import bootstrap
from .git_backend import GitBackend, GitStaleHead, GitStateError
from .crystal_runtime import CrystalRuntime
from .orchestration_branch import BranchLedger
from .orchestration_branch_protocol import BRANCH_RESOURCE, BRANCH_TOOLS, BRANCH_TOOL_NAMES
from .orchestration_robustness import successor_robustness
from .orchestration_robustness_protocol import ROBUSTNESS_RESOURCE, ROBUSTNESS_TOOLS, ROBUSTNESS_TOOL_NAMES
from .orchestration_runtime import OrchestrationRuntime

from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS

class RateLimiter:
    def __init__(self,limit=240,window=60): self.limit=limit; self.window=window; self.h=defaultdict(deque)
    def allow(self,key):
        now=time.time(); q=self.h[key]
        while q and q[0]<now-self.window:q.popleft()
        if len(q)>=self.limit:return False
        q.append(now); return True

class Server:
    def __init__(self,db,git_root=None):
        self.store=Store(db); self.core=AthenaCore(self.store); bootstrap(self.core); self.crystal=CrystalRuntime(self.core); self.branches=BranchLedger(self.core); self.orchestration=OrchestrationRuntime(self.core,self.branches); self.rate=RateLimiter()
        self.git=GitBackend(git_root or os.getenv('ATHENA_GIT_ROOT'), autocommit=False)
        self._branch_tools={tool['name']:tool for tool in BRANCH_TOOLS}; self._robustness_tools={tool['name']:tool for tool in ROBUSTNESS_TOOLS}
    def result(self,id,result): return {"jsonrpc":"2.0","id":id,"result":result}
    def error(self,id,code,msg,data=None):
        e={"code":code,"message":msg};
        if data is not None:e['data']=data
        return {"jsonrpc":"2.0","id":id,"error":e}
    def call_tool(self,name,a):
        c=self.core
        if name=='athena_register': return c.register(a['kind'],a['domain'],a['verb'],a['object_name'],a['method'],a['input_contract'],a['output_contract'],a.get('constraints'),a.get('payload'),a.get('actor','agent'))
        if name=='athena_resolve': return c.navigate(a['identifier'])
        if name=='athena_search': return c.s.search(a['query'],a.get('limit',20))
        if name=='athena_commit_delta': return c.commit_delta(a['oid'],a.get('expected_vid'),a['delta'],a.get('actor','agent'),a.get('status','CANDIDATE'))
        if name=='athena_ingest_text': return c.ingest_text(a['oid'],a.get('expected_vid'),a['text'],a['native_locator'],a.get('carrier','text/plain'),a.get('actor','agent'))
        if name=='athena_add_edge': return c.add_edge(a['src'],a['relation'],a['dst'],a.get('actor','agent'),a.get('attrs'))
        if name=='athena_emit_agent_event': return c.emit_agent_event(a)
        if name=='athena_match_help': return c.help_matches(a['agent'],a.get('limit',10))
        if name=='athena_form_simplex': return c.form_simplex(a['participants'],a['task'],a['topic'],a.get('packet_refs'))
        if name=='athena_promote_mutation': return c.promote_mutation(a['mutation_class'],a['payload'],a['source_eid'],a.get('actor','agent'))
        if name=='athena_pending_mutations': return c.pending_mutations(a['agent'])
        if name=='athena_adopt_mutation': return c.adopt_mutation(a['agent'],a['mutation_id'])
        if name=='athena_hydrate': return c.hydrate(a.get('agent'))
        if name=='athena_branch_observe': return self.branches.observe(a['branch_id'],a['basis_id'],a['reward'],a['witness'],a.get('policy'),a.get('triggers'),a.get('metadata'),a.get('actor','agent'))
        if name=='athena_branch_state': return self.branches.state(a['branch_id'],a.get('basis_id'))
        if name=='athena_branch_list': return self.branches.list(a.get('status'),a.get('limit',100))
        if name=='athena_branch_review': return self.branches.review(a['branch_id'],a['basis_id'],a['trigger'],a.get('actor','agent'))
        if name=='athena_orchestrate': return self.orchestration.compile(seed=a['seed'],candidates=a.get('candidates'),residuals=a.get('residuals'),budget=a.get('budget'),metric_contract=a.get('metric_contract'),actor=a.get('actor','agent'),task=a.get('task',''),session_id=a.get('session_id'),persist=a.get('persist',True))
        if name=='athena_orchestration_get': return self.orchestration.get(a['run_id'])
        if name=='athena_orchestration_replay': return self.orchestration.replay(a['run_id'])
        if name=='athena_orchestration_robustness':
            stored=self.orchestration.get(a['run_id']); rows=stored['output'].get('budgeted_successor_frontier') or stored['output'].get('successor_frontier') or []
            result=successor_robustness(rows,a.get('relative_perturbation',0.05)); result['run_id']=a['run_id']; result['decision_digest']=stored['decision_digest']; return result
        if name=='athena_session_start': return c.session_start(a['agent'],a['task'],self.git.head() if self.git.enabled else None)
        if name=='athena_session_end':
            gh=self.git.head() if self.git.enabled else None
            result=c.session_end(a['session_id'],a['summary'],gh)
            if a.get('checkpoint_git'):
                expected=a.get('expected_git_head')
                if expected is None: raise ValueError('expected_git_head required when checkpoint_git=true')
                ev=c.event(result['end_eid']); result['git']=self.git.checkpoint(expected,ev,c.hydrate(),actor='ATHENA',message=f"athena session {a['session_id']}")
            return result
        if name=='athena_git_status': return self.git.status()
        if name=='athena_add_hyperedge': return self.crystal.add_hyperedge(a['relation'],a['members'],a.get('actor','agent'),a.get('attrs'))
        if name=='athena_crystallize_output': return self.crystal.crystallize_output(a['semantic'],a['text'],a['native_locator'],a['agent'],a['task'],a['seq'],a.get('expected_vid'),a.get('carrier','text/plain'),a.get('edges'),a.get('hyperedges'),a.get('math_objects'),a.get('coordinates'),a.get('cut_lm'),a.get('evidence'),a.get('scale_promotions'),a.get('session_id'),a.get('ephemeris'),a.get('status','CRYSTALLIZED'))
        if name=='athena_dense_navigate': return self.crystal.dense_navigate(a['identifier'])
        if name=='athena_register_transform': return self.crystal.register_transform(a['src_chart'],a['dst_chart'],a.get('operator_oid'),a.get('operator_vid'),a.get('status','FORMALIZED'),a.get('loss_model'),a.get('actor','agent'),a.get('mode','LOOKUP'),a.get('program'),a.get('metric'))
        if name=='athena_apply_transform': return self.crystal.apply_transform(a['subject_id'],a['src_chart'],a['dst_chart'],a.get('source_value'),a.get('persist',False),a.get('actor','agent'))
        if name=='athena_apply_transform_route': return self.crystal.apply_transform_route(a['subject_id'],a['route'],a.get('source_value'),a.get('actor','agent'))
        if name=='athena_coordinate_matrix': return self.crystal.coordinate_matrix(a.get('subject_id'))
        if name=='athena_record_holonomy': return self.crystal.record_holonomy(a['subject_id'],a['route'],a['start'],a['returned'],a['defect'],a.get('metric'),a.get('status','MEASURED'),a.get('actor','agent'))
        if name=='athena_graph_path': return self.crystal.graph_path(a['src'],a['dst'],a.get('relations'),a.get('max_depth',12))
        if name=='athena_finalize_output': return self.crystal.finalize_output(semantic=a['semantic'],text=a['text'],native_locator=a['native_locator'],agent=a['agent'],task=a['task'],seq=a['seq'],expected_vid=a.get('expected_vid'),carrier=a.get('carrier','text/plain'),edges=a.get('edges'),hyperedges=a.get('hyperedges'),math_objects=a.get('math_objects'),coordinates=a.get('coordinates'),cut_lm=a.get('cut_lm'),evidence=a.get('evidence'),scale_promotions=a.get('scale_promotions'),session_id=a.get('session_id'),ephemeris=a.get('ephemeris'),status=a.get('status','CRYSTALLIZED'))
        if name=='athena_verify_emission': return self.crystal.verify_emission(a['envelope_id'],a.get('visible_text'))
        if name=='athena_benchmark':
            r=c.benchmark(); r.update(self.crystal.benchmark_extension()); r.update(self.orchestration.benchmark()); r.update(self.branches.benchmark()); r['git']=self.git.status(); return r
        raise KeyError(name)
    def _branch_resource_value(self):
        return {"law":{"statuses":["ACTIVE","HIBERNATED","REVIEW"],"observation":"calibrated reward + verified witness","triggers":["new_evidence","new_gap","bridge_demand"],"hibernate_is_erase":False,"resurrection":"HIBERNATED -> REVIEW on verified trigger; REVIEW/HIBERNATED -> ACTIVE only after witnessed reward threshold"},"branches":self.branches.list(limit=200),"benchmark":self.branches.benchmark()}
    def _robustness_resource_value(self):
        return {"version":"ROBUSTNESS.1","score_law":"S=delta_j*information_gain*bridge*option_value/cost","critical_perturbation":"eps*=(q^(1/5)-1)/(q^(1/5)+1), q=S1/S2 for positive top-two scores","boundary":"local rank sensitivity only; no truth probability or causal claim"}
    def handle(self,m):
        from .dispatch import handle
        method=m.get('method'); params=m.get('params') or {}; mid=m.get('id')
        if method=='tools/list':
            base=handle(self,m); tools=list(base['result']['tools'])+list(BRANCH_TOOLS)+list(ROBUSTNESS_TOOLS); base['result']['tools']=sorted({tool['name']:tool for tool in tools}.values(),key=lambda x:x['name']); return base
        if method=='tools/call' and params.get('name') in BRANCH_TOOL_NAMES|ROBUSTNESS_TOOL_NAMES:
            name=params['name']; args=params.get('arguments') or {}; schemas={**self._branch_tools,**self._robustness_tools}
            if not self.rate.allow(name): return self.result(mid,{"content":[{"type":"text","text":"Rate limit exceeded; retry later."}],"isError":True})
            try:
                validate(schemas[name]['inputSchema'],args); value=self.call_tool(name,args)
                return self.result(mid,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}],"structuredContent":value,"isError":False})
            except (ValueError,KeyError) as exc: return self.result(mid,{"content":[{"type":"text","text":str(exc)}],"isError":True})
        if method=='resources/list':
            base=handle(self,m); resources=list(base['result']['resources']); known={r['uri'] for r in resources}
            for resource in (BRANCH_RESOURCE,ROBUSTNESS_RESOURCE):
                if resource['uri'] not in known: resources.append(resource)
            base['result']['resources']=resources; return base
        if method=='resources/read' and params.get('uri')==BRANCH_RESOURCE['uri']:
            value=self._branch_resource_value(); return self.result(mid,{"contents":[{"uri":BRANCH_RESOURCE['uri'],"mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        if method=='resources/read' and params.get('uri')==ROBUSTNESS_RESOURCE['uri']:
            value=self._robustness_resource_value(); return self.result(mid,{"contents":[{"uri":ROBUSTNESS_RESOURCE['uri'],"mimeType":"application/json","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}]})
        return handle(self,m)

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--db',default=os.getenv('ATHENA_DB','./state/athena.db')); ap.add_argument('--git-root',default=os.getenv('ATHENA_GIT_ROOT')); args=ap.parse_args(argv)
    srv=Server(args.db,args.git_root)
    for raw in sys.stdin:
        raw=raw.strip()
        if not raw: continue
        try:m=json.loads(raw); r=srv.handle(m)
        except Exception as e:r={"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":f"Parse error: {e}"}}
        if r is not None:
            sys.stdout.write(json.dumps(r,separators=(",",":"),ensure_ascii=False)+"\n"); sys.stdout.flush()

if __name__=='__main__': main()

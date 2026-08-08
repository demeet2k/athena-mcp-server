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
        self.store=Store(db); self.core=AthenaCore(self.store); bootstrap(self.core); self.crystal=CrystalRuntime(self.core); self.rate=RateLimiter()
        self.git=GitBackend(git_root or os.getenv('ATHENA_GIT_ROOT'), autocommit=False)
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
            r=c.benchmark(); r.update(self.crystal.benchmark_extension()); r['git']=self.git.status(); return r
        raise KeyError(name)
    def handle(self,m):
        from .dispatch import handle
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

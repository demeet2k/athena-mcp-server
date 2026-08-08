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
from .collective_runtime import CollectiveRuntime
from .collective_growth import CollectiveGrowthRuntime
from .collective_memory import CollectiveMemoryRuntime
from .collective_learning import CollectiveLearningRuntime
from .collective_v3_dispatch import call as call_collective_v3

from .protocol import PROTOCOL_VERSION, SERVER_INFO, TOOLS, PROMPTS
from .collective_protocol import COLLECTIVE_TOOLS
from .collective_growth_protocol import COLLECTIVE_GROWTH_TOOLS
from .collective_v2_protocol import COLLECTIVE_V2_TOOLS
from .collective_v3_protocol import COLLECTIVE_V3_TOOLS

_existing_tool_names={t['name'] for t in TOOLS}
TOOLS.extend(t for t in COLLECTIVE_TOOLS + COLLECTIVE_GROWTH_TOOLS + COLLECTIVE_V2_TOOLS + COLLECTIVE_V3_TOOLS if t['name'] not in _existing_tool_names)
COLLECTIVE_V3_NAMES={t['name'] for t in COLLECTIVE_V3_TOOLS}

class RateLimiter:
    def __init__(self,limit=240,window=60): self.limit=limit; self.window=window; self.h=defaultdict(deque)
    def allow(self,key):
        now=time.time(); q=self.h[key]
        while q and q[0]<now-self.window:q.popleft()
        if len(q)>=self.limit:return False
        q.append(now); return True

class Server:
    def __init__(self,db,git_root=None):
        self.store=Store(db); self.core=AthenaCore(self.store); bootstrap(self.core); self.crystal=CrystalRuntime(self.core); self.collective=CollectiveRuntime(); self.collective_growth=CollectiveGrowthRuntime(); self.collective_memory=CollectiveMemoryRuntime(self.store,self.collective,self.collective_growth); self.collective_learning=CollectiveLearningRuntime(self.store,self.collective,self.collective_memory); self.rate=RateLimiter()
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
        if name=='athena_collective_plan': return self.collective.plan(a['signals'],a.get('max_workers',12),a.get('reserve_fraction',0.17),a.get('unit_cost',0.08),a.get('lineage'))
        if name=='athena_collective_evaluate': return self.collective.evaluate(a['configuration'])
        if name=='athena_collective_quorum': return self.collective.quorum(a['candidates'],a.get('risk',0.3),a.get('evidence_sensitivity',0.7),a.get('inhibition_gain'))
        if name=='athena_stigmergy_update': return self.collective.stigmergy_update(a['current_score'],a['observations'],a.get('age',1.0),a.get('evaporation_rate',0.08),a.get('deposit_gain',0.35))
        if name=='athena_collective_health': return self.collective.health(a['metrics'])
        if name=='athena_collective_allocate': return self.collective_growth.demand_allocate(a['tasks'],a['workers'],a.get('max_assignments_per_worker',1),a.get('alpha',1.0),a.get('beta',1.0))
        if name=='athena_bridge_account': return self.collective_growth.bridge_account(a['bridge'])
        if name=='athena_collective_restructure': return self.collective_growth.restructure(a['metrics'])
        if name=='athena_dependency_alarm': return self.collective_growth.dependency_alarm(a['seeds'],a['edges'],a.get('max_hops',6),a.get('hop_decay',0.82),a.get('threshold',0.08))
        if name=='athena_artifact_lifecycle': return self.collective_growth.artifact_lifecycle(a['artifacts'])
        if name=='athena_pheromone_reinforce': return self.collective_memory.pheromone_reinforce(a['route_key'],a['observations'],a.get('age'),a.get('evaporation_rate',0.08),a.get('deposit_gain',0.35),a.get('actor','agent'))
        if name=='athena_pheromone_field': return self.collective_memory.pheromone_field(a.get('route_key'),a.get('limit',100),a.get('min_score',0.0))
        if name=='athena_jspace_alarm': return self.collective_memory.jspace_dependency_alarm(a['seeds'],a.get('relation_modes'),a.get('max_hops',6),a.get('hop_decay',0.82),a.get('threshold',0.08))
        if name=='athena_rgo_observe': return self.collective_memory.record_rgo_observation(a['plan_key'],a['predicted_rgo'],a['observed_rgo'],a.get('features'),a.get('scope','global'),a.get('actor','agent'))
        if name=='athena_rgo_calibrate': return self.collective_memory.calibrate_rgo(a['predicted_rgo'],a.get('scope','global'))
        if name=='athena_topology_get': return self.collective_memory.topology_get(a['topology_id'])
        if name=='athena_topology_apply': return self.collective_memory.topology_apply(a['topology_id'],a['expected_version'],a['operation'],a['payload'],a.get('actor','agent'))
        if name=='athena_topology_rollback': return self.collective_memory.topology_rollback(a['topology_id'],a['txid'],a['expected_version'],a.get('actor','agent'))
        if name=='athena_failure_antibody_register': return self.collective_memory.register_failure_antibody(a['signature'],a.get('trigger'),a.get('detector'),a.get('repair'),a.get('evidence'),a.get('regression_refs'),a.get('scope','global'),a.get('actor','agent'))
        if name=='athena_failure_antibody_match': return self.collective_memory.match_failure_antibodies(a['event'],a.get('tags'),a.get('scope'),a.get('threshold',0.35),a.get('limit',10),a.get('record_hits',True))
        if name in COLLECTIVE_V3_NAMES: return call_collective_v3(self.collective_learning,name,a)
        if name=='athena_benchmark':
            r=c.benchmark(); r.update(self.crystal.benchmark_extension()); r['git']=self.git.status(); r['collective_runtime']=self.collective.describe()['version']; r['collective_growth']=self.collective_growth.describe()['version']; r['collective_memory']=self.collective_memory.describe(); r['collective_learning']=self.collective_learning.describe(); return r
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

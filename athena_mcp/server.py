from __future__ import annotations
import argparse,json,os,sys,time
from collections import defaultdict,deque
from .store import Store
from .core import AthenaCore,StaleTarget
from .validate import validate
from .bootstrap import bootstrap
from .git_backend import GitBackend,GitStaleHead,GitStateError
from .crystal_runtime import CrystalRuntime
from .collective_runtime import CollectiveRuntime
from .collective_growth import CollectiveGrowthRuntime
from .collective_memory import CollectiveMemoryRuntime
from .orchestration_branch import BranchLedger
from .orchestration_authority import AuthorityLedger
from .orchestration_authority_runtime import AuthorityOrchestrationRuntime
from .orchestration_robustness import successor_robustness,elasticity_packet
from .orchestration import orchestration_law

from .protocol import PROTOCOL_VERSION,SERVER_INFO,TOOLS,PROMPTS
from .collective_protocol import COLLECTIVE_TOOLS
from .collective_growth_protocol import COLLECTIVE_GROWTH_TOOLS
from .collective_v2_protocol import COLLECTIVE_V2_TOOLS
from .aor_protocol import AOR_TOOLS
from .orchestration_branch_protocol import BRANCH_TOOLS
from .orchestration_authority_protocol import AUTHORITY_TOOLS
from .orchestration_robustness_protocol import ROBUSTNESS_TOOLS

_existing_tool_names={t['name'] for t in TOOLS}
for tool in COLLECTIVE_TOOLS+COLLECTIVE_GROWTH_TOOLS+COLLECTIVE_V2_TOOLS+AOR_TOOLS+BRANCH_TOOLS+AUTHORITY_TOOLS+ROBUSTNESS_TOOLS:
    if tool['name'] not in _existing_tool_names:
        TOOLS.append(tool);_existing_tool_names.add(tool['name'])

class RateLimiter:
    def __init__(self,limit=240,window=60):self.limit=limit;self.window=window;self.h=defaultdict(deque)
    def allow(self,key):
        now=time.time();q=self.h[key]
        while q and q[0]<now-self.window:q.popleft()
        if len(q)>=self.limit:return False
        q.append(now);return True

class Server:
    def __init__(self,db,git_root=None):
        self.store=Store(db);self.core=AthenaCore(self.store);bootstrap(self.core);self.crystal=CrystalRuntime(self.core)
        self.collective=CollectiveRuntime();self.collective_growth=CollectiveGrowthRuntime();self.collective_memory=CollectiveMemoryRuntime(self.store,self.collective,self.collective_growth)
        self.branches=BranchLedger(self.core);self.authority=AuthorityLedger(self.core);self.orchestration=AuthorityOrchestrationRuntime(self.core,self.branches,self.authority);self.rate=RateLimiter();self.git=GitBackend(git_root or os.getenv('ATHENA_GIT_ROOT'),autocommit=False)
    def result(self,id,result):return {'jsonrpc':'2.0','id':id,'result':result}
    def error(self,id,code,msg,data=None):
        e={'code':code,'message':msg}
        if data is not None:e['data']=data
        return {'jsonrpc':'2.0','id':id,'error':e}
    def call_tool(self,name,a):
        c=self.core
        if name=='athena_register':return c.register(a['kind'],a['domain'],a['verb'],a['object_name'],a['method'],a['input_contract'],a['output_contract'],a.get('constraints'),a.get('payload'),a.get('actor','agent'))
        if name=='athena_resolve':return c.navigate(a['identifier'])
        if name=='athena_search':return c.s.search(a['query'],a.get('limit',20))
        if name=='athena_commit_delta':return c.commit_delta(a['oid'],a.get('expected_vid'),a['delta'],a.get('actor','agent'),a.get('status','CANDIDATE'))
        if name=='athena_ingest_text':return c.ingest_text(a['oid'],a.get('expected_vid'),a['text'],a['native_locator'],a.get('carrier','text/plain'),a.get('actor','agent'))
        if name=='athena_add_edge':return c.add_edge(a['src'],a['relation'],a['dst'],a.get('actor','agent'),a.get('attrs'))
        if name=='athena_emit_agent_event':return c.emit_agent_event(a)
        if name=='athena_match_help':return c.help_matches(a['agent'],a.get('limit',10))
        if name=='athena_form_simplex':return c.form_simplex(a['participants'],a['task'],a['topic'],a.get('packet_refs'))
        if name=='athena_promote_mutation':return c.promote_mutation(a['mutation_class'],a['payload'],a['source_eid'],a.get('actor','agent'))
        if name=='athena_pending_mutations':return c.pending_mutations(a['agent'])
        if name=='athena_adopt_mutation':return c.adopt_mutation(a['agent'],a['mutation_id'])
        if name=='athena_hydrate':return c.hydrate(a.get('agent'))
        if name=='athena_orchestrate':return self.orchestration.compile(a['seed'],a.get('candidates'),a.get('residuals'),a.get('budget'),a.get('metric_contract'),a.get('actor','agent'),a.get('task',''),a.get('session_id'),a.get('persist',True))
        if name=='athena_orchestration_get':return self.orchestration.get(a['run_id'])
        if name=='athena_orchestration_replay':return self.orchestration.replay(a['run_id'])
        if name=='athena_orchestration_recent':return self.orchestration.recent(a.get('limit',20))
        if name=='athena_orchestration_robustness':
            stored=self.orchestration.get(a['run_id']);rows=stored['output'].get('budgeted_successor_frontier') or stored['output'].get('successor_frontier') or [];cert=successor_robustness(rows,a.get('relative_perturbation',0.05));cert['run_id']=a['run_id'];cert['decision_digest']=stored['decision_digest'];cert['winner_elasticity']=elasticity_packet(next((r for r in rows if str(r.get('id'))==str(cert.get('winner'))),{})) if cert.get('winner') else None;return cert
        if name=='athena_branch_observe':return self.branches.observe(a['branch_id'],a['basis_id'],a['reward'],a['witness'],a.get('policy'),a.get('triggers'),a.get('metadata'),a.get('actor','agent'))
        if name=='athena_branch_state':return self.branches.state(a['branch_id'],a.get('basis_id'))
        if name=='athena_branch_list':return self.branches.list(a.get('status'),a.get('limit',100))
        if name=='athena_branch_review':return self.branches.review(a['branch_id'],a['basis_id'],a['trigger'],a.get('actor','agent'))
        if name=='athena_claim_register':return self.authority.register(a['claim_id'],a['source_ref'],a.get('actor','agent'))
        if name=='athena_claim_state':return self.authority.state(a['claim_id'])
        if name=='athena_claim_list':return self.authority.list(a.get('y'),a.get('status'),a.get('limit',100))
        if name=='athena_claim_promote':return self.authority.promote(a['claim_id'],a['target_y'],a.get('evidence'),a.get('test'),a.get('canonical_authority'),a.get('actor','agent'))
        if name=='athena_claim_challenge':return self.authority.challenge(a['claim_id'],a['witness'],a['reason'],a.get('actor','agent'))
        if name=='athena_claim_resolve_canonical_challenge':return self.authority.resolve_canonical_challenge(a['claim_id'],a['decision'],a['authority'],a.get('actor','agent'))
        if name=='athena_session_start':return c.session_start(a['agent'],a['task'],self.git.head() if self.git.enabled else None)
        if name=='athena_session_end':
            gh=self.git.head() if self.git.enabled else None;result=c.session_end(a['session_id'],a['summary'],gh)
            if a.get('checkpoint_git'):
                expected=a.get('expected_git_head')
                if expected is None:raise ValueError('expected_git_head required when checkpoint_git=true')
                ev=c.event(result['end_eid']);result['git']=self.git.checkpoint(expected,ev,c.hydrate(),actor='ATHENA',message=f"athena session {a['session_id']}")
            return result
        if name=='athena_git_status':return self.git.status()
        if name=='athena_add_hyperedge':return self.crystal.add_hyperedge(a['relation'],a['members'],a.get('actor','agent'),a.get('attrs'))
        if name=='athena_crystallize_output':return self.crystal.crystallize_output(a['semantic'],a['text'],a['native_locator'],a['agent'],a['task'],a['seq'],a.get('expected_vid'),a.get('carrier','text/plain'),a.get('edges'),a.get('hyperedges'),a.get('math_objects'),a.get('coordinates'),a.get('cut_lm'),a.get('evidence'),a.get('scale_promotions'),a.get('session_id'),a.get('ephemeris'),a.get('status','CRYSTALLIZED'))
        if name=='athena_dense_navigate':return self.crystal.dense_navigate(a['identifier'])
        if name=='athena_register_transform':return self.crystal.register_transform(a['src_chart'],a['dst_chart'],a.get('operator_oid'),a.get('operator_vid'),a.get('status','FORMALIZED'),a.get('loss_model'),a.get('actor','agent'),a.get('mode','LOOKUP'),a.get('program'),a.get('metric'))
        if name=='athena_apply_transform':return self.crystal.apply_transform(a['subject_id'],a['src_chart'],a['dst_chart'],a.get('source_value'),a.get('persist',False),a.get('actor','agent'))
        if name=='athena_apply_transform_route':return self.crystal.apply_transform_route(a['subject_id'],a['route'],a.get('source_value'),a.get('actor','agent'))
        if name=='athena_coordinate_matrix':return self.crystal.coordinate_matrix(a.get('subject_id'))
        if name=='athena_record_holonomy':return self.crystal.record_holonomy(a['subject_id'],a['route'],a['start'],a['returned'],a['defect'],a.get('metric'),a.get('status','MEASURED'),a.get('actor','agent'))
        if name=='athena_graph_path':return self.crystal.graph_path(a['src'],a['dst'],a.get('relations'),a.get('max_depth',12))
        if name=='athena_finalize_output':return self.crystal.finalize_output(semantic=a['semantic'],text=a['text'],native_locator=a['native_locator'],agent=a['agent'],task=a['task'],seq=a['seq'],expected_vid=a.get('expected_vid'),carrier=a.get('carrier','text/plain'),edges=a.get('edges'),hyperedges=a.get('hyperedges'),math_objects=a.get('math_objects'),coordinates=a.get('coordinates'),cut_lm=a.get('cut_lm'),evidence=a.get('evidence'),scale_promotions=a.get('scale_promotions'),session_id=a.get('session_id'),ephemeris=a.get('ephemeris'),status=a.get('status','CRYSTALLIZED'))
        if name=='athena_verify_emission':return self.crystal.verify_emission(a['envelope_id'],a.get('visible_text'))
        if name=='athena_collective_plan':return self.collective.plan(a['signals'],a.get('max_workers',12),a.get('reserve_fraction',0.17),a.get('unit_cost',0.08),a.get('lineage'))
        if name=='athena_collective_evaluate':return self.collective.evaluate(a['configuration'])
        if name=='athena_collective_quorum':return self.collective.quorum(a['candidates'],a.get('risk',0.3),a.get('evidence_sensitivity',0.7),a.get('inhibition_gain'))
        if name=='athena_stigmergy_update':return self.collective.stigmergy_update(a['current_score'],a['observations'],a.get('age',1.0),a.get('evaporation_rate',0.08),a.get('deposit_gain',0.35))
        if name=='athena_collective_health':return self.collective.health(a['metrics'])
        if name=='athena_collective_allocate':return self.collective_growth.demand_allocate(a['tasks'],a['workers'],a.get('max_assignments_per_worker',1),a.get('alpha',1.0),a.get('beta',1.0))
        if name=='athena_bridge_account':return self.collective_growth.bridge_account(a['bridge'])
        if name=='athena_collective_restructure':return self.collective_growth.restructure(a['metrics'])
        if name=='athena_dependency_alarm':return self.collective_growth.dependency_alarm(a['seeds'],a['edges'],a.get('max_hops',6),a.get('hop_decay',0.82),a.get('threshold',0.08))
        if name=='athena_artifact_lifecycle':return self.collective_growth.artifact_lifecycle(a['artifacts'])
        if name=='athena_pheromone_reinforce':return self.collective_memory.pheromone_reinforce(a['route_key'],a['observations'],a.get('age'),a.get('evaporation_rate',0.08),a.get('deposit_gain',0.35),a.get('actor','agent'))
        if name=='athena_pheromone_field':return self.collective_memory.pheromone_field(a.get('route_key'),a.get('limit',100),a.get('min_score',0.0))
        if name=='athena_jspace_alarm':return self.collective_memory.jspace_dependency_alarm(a['seeds'],a.get('relation_modes'),a.get('max_hops',6),a.get('hop_decay',0.82),a.get('threshold',0.08))
        if name=='athena_rgo_observe':return self.collective_memory.record_rgo_observation(a['plan_key'],a['predicted_rgo'],a['observed_rgo'],a.get('features'),a.get('scope','global'),a.get('actor','agent'))
        if name=='athena_rgo_calibrate':return self.collective_memory.calibrate_rgo(a['predicted_rgo'],a.get('scope','global'))
        if name=='athena_topology_get':return self.collective_memory.topology_get(a['topology_id'])
        if name=='athena_topology_apply':return self.collective_memory.topology_apply(a['topology_id'],a['expected_version'],a['operation'],a['payload'],a.get('actor','agent'))
        if name=='athena_topology_rollback':return self.collective_memory.topology_rollback(a['topology_id'],a['txid'],a['expected_version'],a.get('actor','agent'))
        if name=='athena_failure_antibody_register':return self.collective_memory.register_failure_antibody(a['signature'],a.get('trigger'),a.get('detector'),a.get('repair'),a.get('evidence'),a.get('regression_refs'),a.get('scope','global'),a.get('actor','agent'))
        if name=='athena_failure_antibody_match':return self.collective_memory.match_failure_antibodies(a['event'],a.get('tags'),a.get('scope'),a.get('threshold',0.35),a.get('limit',10),a.get('record_hits',True))
        if name=='athena_benchmark':
            r=c.benchmark();r.update(self.crystal.benchmark_extension());r.update(self.branches.benchmark());r.update(self.authority.benchmark());r.update(self.orchestration.benchmark());r['git']=self.git.status();r['collective_runtime']=self.collective.describe()['version'];r['collective_growth']=self.collective_growth.describe()['version'];r['collective_memory']=self.collective_memory.describe();r['aor_law']=orchestration_law()['version'];return r
        raise KeyError(name)
    def handle(self,m):
        from .dispatch import handle
        return handle(self,m)

def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--db',default=os.getenv('ATHENA_DB','./state/athena.db'));ap.add_argument('--git-root',default=os.getenv('ATHENA_GIT_ROOT'));args=ap.parse_args(argv);srv=Server(args.db,args.git_root)
    for raw in sys.stdin:
        raw=raw.strip()
        if not raw:continue
        try:m=json.loads(raw);r=srv.handle(m)
        except Exception as e:r={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':f'Parse error: {e}'}}
        if r is not None:sys.stdout.write(json.dumps(r,separators=(',',':'),ensure_ascii=False)+'\n');sys.stdout.flush()

if __name__=='__main__':main()

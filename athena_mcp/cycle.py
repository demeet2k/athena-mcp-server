from __future__ import annotations

import hashlib
import json
import time
from typing import Any,Dict,Mapping,Optional

from .identity import digest,event_id

CYCLE_VERSION='ATHENA.CYCLE.1'
PHASES=(
    'HYDRATE','RECONSTRUCT','MEMORY','EXTRACT','RETRIEVE','HUG','GAP','FIELD',
    'MEASURE','AOR','COLLECTIVE','EXECUTE','VERIFY','LEARN','SUCCESSOR','COMPLETE',
)
TERMINAL={'COMPLETE','FAILED'}
WAITING={
    'WAITING_INPUT','WAITING_MEASUREMENT','WAITING_CALIBRATION','WAITING_AUTHORITY',
    'WAITING_HUG_IMPLEMENTATION','WAITING_COLLECTIVE_MEASUREMENT','WAITING_WORKERS',
    'WAITING_EXECUTOR','WAITING_TEST','WAITING_REPAIR','WAITING_CONTROL',
}
CYCLE_SCHEMA='''
CREATE TABLE IF NOT EXISTS cycle_runs(
 cycle_id TEXT PRIMARY KEY,
 task_ref TEXT NOT NULL,
 actor TEXT NOT NULL,
 phase TEXT NOT NULL,
 status TEXT NOT NULL,
 state_json TEXT NOT NULL,
 state_digest TEXT NOT NULL,
 last_eid TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cycle_events(
 cycle_event_id TEXT PRIMARY KEY,
 cycle_id TEXT NOT NULL,
 seq INTEGER NOT NULL,
 phase TEXT NOT NULL,
 operation TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 state_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_cycle_event_seq ON cycle_events(cycle_id,seq);
CREATE INDEX IF NOT EXISTS idx_cycle_runs_updated ON cycle_runs(updated_at);
'''


def _json_digest(value):
    raw=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    return hashlib.sha256(raw.encode()).hexdigest()


def _deep_merge(base:Dict[str,Any],patch:Mapping[str,Any]):
    for key,value in dict(patch or {}).items():
        if isinstance(value,Mapping) and isinstance(base.get(key),dict):_deep_merge(base[key],value)
        else:base[key]=value
    return base


def _verified_ref(value,label):
    if isinstance(value,str):
        if value.strip():return value.strip()
        raise ValueError(f'{label} requires nonempty ref')
    value=dict(value or {})
    if value.get('verified') is not True:raise ValueError(f'{label} requires verified=true')
    ref=str(value.get('ref') or '').strip()
    if not ref:raise ValueError(f'{label} requires ref')
    return ref


def _verified_test(packet):
    packet=dict(packet or {});missing=[n for n in ('procedure','observation','result','witness') if not packet.get(n)]
    if missing:return False,{'missing':missing}
    try:_verified_ref(packet['witness'],'cycle test witness')
    except ValueError as exc:return False,{'error':str(exc)}
    return True,packet


class CycleRuntime:
    """Resumable whole-organism workflow with explicit semantic wait states.

    CYCLE.1 never claims a semantic transform, measurement, external execution,
    test, or persistence happened unless a corresponding organ receipt/witness is
    actually present. Internal deterministic orchestration may advance; semantic
    boundaries return WAITING_* and preserve an exact continuation state.
    """

    def __init__(self,server,development):
        self.server=server;self.dev=development;self.core=server.core;self.s=server.store
        with self.s.db:self.s.db.executescript(CYCLE_SCHEMA)
        self.core.register('TOOL','RUNTIME','ORCHESTRATE','WHOLE_CYCLE','RESUMABLE_FAIL_CLOSED_CYCLE1',
            {'seed':'task seed','config':'phase contracts','supplies':'witnessed external inputs'},
            {'cycle_id':'CYCLE','phase':'typed','status':'ACTIVE|WAITING_*|COMPLETE','artifacts':'run receipts'},
            actor='GENESIS.CYCLE.1',status='CANONICAL')

    def _row(self,cycle_id):
        row=self.s.one('SELECT * FROM cycle_runs WHERE cycle_id=?',(cycle_id,))
        if not row:raise KeyError('unknown cycle')
        out=dict(row);out['state']=json.loads(out.pop('state_json'));return out

    def get(self,cycle_id):
        row=self._row(cycle_id);row['events']=self.s.rows('SELECT cycle_event_id,seq,phase,operation,state_digest,eid,created_at FROM cycle_events WHERE cycle_id=? ORDER BY seq',(cycle_id,));return row

    def recent(self,limit=50):
        limit=max(1,min(int(limit),500));return self.s.rows('SELECT cycle_id,task_ref,actor,phase,status,state_digest,last_eid,created_at,updated_at FROM cycle_runs ORDER BY updated_at DESC LIMIT ?',(limit,))

    def _persist_state(self,cycle_id,state,phase,status,eid):
        sd=_json_digest(state);now=time.time()
        with self.s.db:self.s.db.execute('UPDATE cycle_runs SET phase=?,status=?,state_json=?,state_digest=?,last_eid=?,updated_at=? WHERE cycle_id=?',(phase,status,json.dumps(state,sort_keys=True,ensure_ascii=False),sd,eid,now,cycle_id))
        return sd

    def _event(self,cycle_id,state,phase,operation,payload,actor,status=None,next_phase=None):
        seq=self.s.one('SELECT COUNT(*) n FROM cycle_events WHERE cycle_id=?',(cycle_id,))['n']+1
        phase2=next_phase or phase;status2=status or 'ACTIVE';parent=self.s.head('global');pe=parent['eid'] if parent else None
        public={'cycle_id':cycle_id,'seq':seq,'phase':phase,'operation':operation,'status':status2,'next_phase':phase2,'payload':payload}
        eid=event_id('CYCLE_EVENT',actor,pe,public);ed=digest(public,32);sd=self._persist_state(cycle_id,state,phase2,status2,eid);ceid='CYCLEEV.'+digest({'cycle':cycle_id,'seq':seq,'eid':eid},24)
        with self.s.db:self.s.db.execute('INSERT INTO cycle_events VALUES(?,?,?,?,?,?,?,?,?)',(ceid,cycle_id,seq,phase,operation,json.dumps(public,sort_keys=True,ensure_ascii=False),sd,eid,time.time()))
        self.s.put_event(eid,'CYCLE_EVENT',actor,pe,public,ed);self.s.set_head('global',None,None,eid,ed)
        return {'cycle_event_id':ceid,'eid':eid,'state_digest':sd,'phase':phase2,'status':status2}

    def start(self,task_ref,seed,config=None,actor='agent'):
        task_ref=str(task_ref or '').strip()
        if not task_ref:raise ValueError('task_ref required')
        config=dict(config or {});created=time.time();seed_digest=_json_digest(seed);cycle_id='CYCLE.'+digest({'task_ref':task_ref,'seed_digest':seed_digest,'nonce':time.time_ns()},24)
        state={'version':CYCLE_VERSION,'task_ref':task_ref,'seed':seed,'seed_digest':seed_digest,'config':config,'supplied':{},'artifacts':{},'wait':None,'errors':[],'return':{}}
        parent=self.s.head('global');pe=parent['eid'] if parent else None;payload={'operation':'CYCLE_START','cycle_id':cycle_id,'task_ref':task_ref,'seed_digest':seed_digest};eid=event_id('CYCLE_START',actor,pe,payload);ed=digest(payload,32);sd=_json_digest(state)
        with self.s.db:self.s.db.execute('INSERT INTO cycle_runs VALUES(?,?,?,?,?,?,?,?,?,?)',(cycle_id,task_ref,actor,'HYDRATE','ACTIVE',json.dumps(state,sort_keys=True,ensure_ascii=False),sd,eid,created,created))
        self.s.put_event(eid,'CYCLE_START',actor,pe,payload,ed);self.s.set_head('global',None,None,eid,ed)
        return {'cycle_id':cycle_id,'task_ref':task_ref,'phase':'HYDRATE','status':'ACTIVE','seed_digest':seed_digest,'state_digest':sd,'eid':eid}

    def _cfg(self,state,name,default=None):
        if name in state['supplied']:return state['supplied'][name]
        return state['config'].get(name,default)

    def _wait(self,cycle_id,state,phase,status,reason,requirements,actor):
        state['wait']={'status':status,'phase':phase,'reason':reason,'requirements':requirements};return self._event(cycle_id,state,phase,'WAIT',state['wait'],actor,status=status,next_phase=phase)

    def _step(self,cycle_id,row):
        state=row['state'];phase=row['phase'];actor=row['actor'];a=state['artifacts'];state['wait']=None
        if phase=='HYDRATE':
            a['hydrate']=self.server.core.hydrate(actor);return self._event(cycle_id,state,phase,'HYDRATE',{'head':a['hydrate'].get('head')},actor,next_phase='RECONSTRUCT')
        if phase=='RECONSTRUCT':
            projection={'global_head':self.s.head('global'),'git':self.server.git.status(),'collective':self.server.collective.describe(),'collective_growth':self.server.collective_growth.describe(),'collective_memory':self.server.collective_memory.describe(),'branches':self.server.branches.benchmark(),'authority':self.server.authority.benchmark(),'development':self.dev.benchmark()}
            projection['reconstruct_digest']=_json_digest(projection);projection['boundary']='runtime-state projection with exact current heads/organ summaries; not a claim that unseen external sources were reconstructed'
            a['reconstruct']=projection;return self._event(cycle_id,state,phase,'RECONSTRUCT',{'reconstruct_digest':projection['reconstruct_digest']},actor,next_phase='MEMORY')
        if phase=='MEMORY':
            routes=list(self._cfg(state,'memory_route_keys',[]) or []);pheromone={str(key):self.server.collective_memory.pheromone_field(str(key),1,0.0) for key in routes};failure=self._cfg(state,'failure_memory_query')
            antibodies=None
            if isinstance(failure,Mapping) and failure.get('event'):
                antibodies=self.server.collective_memory.match_failure_antibodies(failure['event'],failure.get('tags'),failure.get('scope'),failure.get('threshold',0.35),failure.get('limit',10),False)
            a['memory']={'pheromone':pheromone,'antibodies':antibodies,'boundary':'memory snapshot guides attention/repair lookup only; memory != evidence or Y authority'}
            return self._event(cycle_id,state,phase,'MEMORY_SNAPSHOT',{'route_count':len(routes),'antibody_query':bool(failure)},actor,next_phase='EXTRACT')
        if phase=='EXTRACT':
            cfg=self._cfg(state,'extraction')
            if cfg is None:
                if state['config'].get('require_extraction'):return self._wait(cycle_id,state,phase,'WAITING_INPUT','extraction configuration required',['extraction'],actor)
                a['extraction']={'status':'SKIPPED_NOT_CONFIGURED'};return self._event(cycle_id,state,phase,'SKIP',a['extraction'],actor,next_phase='RETRIEVE')
            if not a.get('extraction_run'):
                cfg=dict(cfg);run=self.dev.extraction.plan(cfg.get('seed_ref',state['task_ref']),cfg.get('seed',state['seed']),cfg.get('transforms'),cfg.get('max_depth',1),cfg.get('max_tasks_per_generation',16),actor);a['extraction_run']=run
            return self._event(cycle_id,state,phase,'EXTRACTION_PLAN',{'run_id':a['extraction_run']['run_id'],'task_count':len(a['extraction_run']['tasks'])},actor,next_phase='RETRIEVE')
        if phase=='RETRIEVE':
            cfg=self._cfg(state,'retrieval')
            if cfg is None:
                if state['config'].get('require_retrieval'):return self._wait(cycle_id,state,phase,'WAITING_INPUT','retrieval configuration required',['retrieval'],actor)
                a['retrieval']={'status':'SKIPPED_NOT_CONFIGURED'};return self._event(cycle_id,state,phase,'SKIP',a['retrieval'],actor,next_phase='HUG')
            if not a.get('retrieval_run'):
                cfg=dict(cfg);eq=None
                if cfg.get('equivalence_context'):eq=self.dev.equivalence.snapshot(cfg['equivalence_context'],cfg.get('candidates') or [])
                run=self.dev.retrieval.compile(cfg.get('query_ref',state['task_ref']),cfg.get('query') or {},cfg.get('candidates') or [],eq,actor,state['task_ref'],True);a['retrieval_run']=run
            return self._event(cycle_id,state,phase,'RAG_COMPILE',{'run_id':a['retrieval_run']['run_id'],'selected':a['retrieval_run']['selected_ids'],'measurement_count':len(a['retrieval_run']['measurement_plan'])},actor,next_phase='HUG')
        if phase=='HUG':
            cfg=self._cfg(state,'hug')
            if cfg is None:
                if state['config'].get('require_hug'):return self._wait(cycle_id,state,phase,'WAITING_HUG_IMPLEMENTATION','HUG implementation/invocation required',['hug'],actor)
                a['hug']={'status':'SKIPPED_NO_IMPLEMENTATION_CONFIGURED'};return self._event(cycle_id,state,phase,'SKIP',a['hug'],actor,next_phase='GAP')
            if not a.get('hug_invocation'):
                cfg=dict(cfg)
                try:plan=self.dev.hug.plan(cfg['impl_id'],cfg['arguments'],cfg.get('context'),cfg.get('required_status','CANONICAL'),actor)
                except (KeyError,ValueError) as exc:return self._wait(cycle_id,state,phase,'WAITING_HUG_IMPLEMENTATION',str(exc),['registered HUG implementation at required maturity'],actor)
                a['hug_invocation']=plan
            return self._event(cycle_id,state,phase,'HUG_PLAN',{'invocation_id':a['hug_invocation']['invocation_id'],'status':a['hug_invocation']['status'],'boundary':a['hug_invocation']['execution_boundary']},actor,next_phase='GAP')
        if phase=='GAP':
            cfg=self._cfg(state,'gap')
            if cfg is None:
                if state['config'].get('require_gap'):return self._wait(cycle_id,state,phase,'WAITING_INPUT','GAP sources/edges/targets/policy required',['gap'],actor)
                a['gap']={'status':'SKIPPED_NOT_CONFIGURED'};return self._event(cycle_id,state,phase,'SKIP',a['gap'],actor,next_phase='FIELD')
            if not a.get('gap_run'):
                cfg=dict(cfg);run=self.dev.gap.compile(cfg.get('task_ref',state['task_ref']),cfg.get('sources') or {},cfg.get('edges') or [],cfg.get('targets') or [],cfg.get('policy') or {'traversable_relations':[]},actor,True);a['gap_run']=run
            return self._event(cycle_id,state,phase,'GAP_COMPILE',{'run_id':a['gap_run']['run_id'],'gap':a['gap_run']['gap_target_ids'],'grow':(a['gap_run'].get('grow') or {}).get('id')},actor,next_phase='FIELD')
        if phase=='FIELD':
            modules={}
            if a.get('extraction_run'):modules['extraction_frontier']=self.dev.extraction.frontier(a['extraction_run']['run_id'])
            if a.get('retrieval_run'):modules['retrieval']={**a['retrieval_run'],'run_id':a['retrieval_run']['run_id']}
            if a.get('gap_run'):modules['gap']={**a['gap_run'],'run_id':a['gap_run']['run_id']}
            if a.get('hug_invocation'):modules['hug_invocations']=[self.dev.hug.invocation(a['hug_invocation']['invocation_id'])]
            modules['branches']=self.server.branches.list(status='REVIEW',limit=100)
            _deep_merge(modules,self._cfg(state,'field_module_outputs',{}) or {})
            explicit=list(self._cfg(state,'field_explicit_candidates',[]) or [])
            run=self.dev.field.compile(state['task_ref'],modules,explicit,self._cfg(state,'ecosystem',{}) or {},actor,True);a['field_modules']=modules;a['field_run']=run
            return self._event(cycle_id,state,phase,'FIELD_COMPILE',{'run_id':run['run_id'],'candidate_count':len(run['candidate_ids']),'unmeasured':run['unmeasured_candidate_ids'],'conflicts':run['conflict_candidate_ids']},actor,next_phase='MEASURE')
        if phase=='MEASURE':
            field=a['field_run'];measured=self._cfg(state,'measured_candidates')
            if field.get('unmeasured_candidate_ids') or field.get('conflict_candidate_ids'):
                if not measured:return self._wait(cycle_id,state,phase,'WAITING_MEASUREMENT','FIELD candidates require explicit measurements/adjudication',{'unmeasured':field.get('unmeasured_candidate_ids',[]),'conflicts':field.get('conflict_candidate_ids',[])},actor)
                rerun=self.dev.field.compile(state['task_ref'],a['field_modules'],list(measured),self._cfg(state,'ecosystem',{}) or {},actor,True);a['field_run']=rerun;field=rerun
                if field.get('unmeasured_candidate_ids') or field.get('conflict_candidate_ids'):
                    return self._wait(cycle_id,state,phase,'WAITING_MEASUREMENT','supplied measurements do not resolve all FIELD candidates',{'unmeasured':field.get('unmeasured_candidate_ids',[]),'conflicts':field.get('conflict_candidate_ids',[])},actor)
            return self._event(cycle_id,state,phase,'MEASUREMENTS_READY',{'field_run_id':field['run_id'],'candidate_count':len(field['candidate_ids'])},actor,next_phase='AOR')
        if phase=='AOR':
            field=a['field_run'];gap=a.get('gap_run') or {};run=self.server.orchestration.compile(state['seed'],field['handoff_to_aor'],gap.get('gap') or [],self._cfg(state,'aor_budget',{}) or {},self._cfg(state,'metric_contract',{}) or {},actor,state['task_ref'],None,True);a['aor_run']=run
            if not run.get('next'):
                if run.get('authority_plan'):return self._wait(cycle_id,state,phase,'WAITING_AUTHORITY','AOR candidates blocked by typed authority',run['authority_plan'],actor)
                if run.get('measurement_plan'):return self._wait(cycle_id,state,phase,'WAITING_MEASUREMENT','AOR candidate metrics incomplete',run['measurement_plan'],actor)
                if run.get('calibration_plan'):return self._wait(cycle_id,state,phase,'WAITING_CALIBRATION','AOR metric basis/calibration incomplete',run['calibration_plan'],actor)
                return self._wait(cycle_id,state,phase,'WAITING_CONTROL','no executable AOR successor',{'explanation':run.get('decision_explanation'),'dependency_cycles':run.get('dependency_graph',{}).get('cycles',[])},actor)
            return self._event(cycle_id,state,phase,'AOR_DECIDE',{'run_id':run['run_id'],'next':run['next']['id'],'pareto':run.get('pareto_successor_frontier',[])},actor,next_phase='COLLECTIVE')
        if phase=='COLLECTIVE':
            aor=a['aor_run'];transport=self.dev.transport.runtime.aor_to_collective(aor['run_id'],actor,True);a['aor_collective_transport']=transport
            tasks=list(self._cfg(state,'collective_tasks',[]) or transport.get('tasks') or []);next_id=aor['next']['id'];next_task=next((t for t in tasks if str(t.get('id'))==str(next_id)),None)
            if next_task is None or next_task.get('allocation_state')=='UNMEASURED':
                return self._wait(cycle_id,state,phase,'WAITING_COLLECTIVE_MEASUREMENT','selected AOR successor lacks explicit Collective allocation metrics',{'next':next_id,'measurement_plan':transport.get('measurement_plan',[])},actor)
            workers=list(self._cfg(state,'workers',[]) or [])
            if not workers:return self._wait(cycle_id,state,phase,'WAITING_WORKERS','Collective worker/capability state required',['workers'],actor)
            signals=dict(self._cfg(state,'collective_signals',{}) or {});plan=self.server.collective.plan(signals,self._cfg(state,'max_workers',12),self._cfg(state,'reserve_fraction',.17),self._cfg(state,'unit_cost',.08),state['task_ref']);allocation=self.server.collective_growth.demand_allocate(tasks,workers,self._cfg(state,'max_assignments_per_worker',1),self._cfg(state,'allocation_alpha',1.0),self._cfg(state,'allocation_beta',1.0));a['collective_plan']=plan;a['collective_allocation']=allocation
            return self._event(cycle_id,state,phase,'COLLECTIVE_ALLOCATE',{'next':next_id,'form':plan.get('form'),'allocation':allocation},actor,next_phase='EXECUTE')
        if phase=='EXECUTE':
            receipt=self._cfg(state,'execution_receipt')
            if not receipt:return self._wait(cycle_id,state,phase,'WAITING_EXECUTOR','CYCLE.1 has no generic semantic executor; an actual execution receipt is required',{'candidate':a['aor_run']['next']['id'],'allocation':a.get('collective_allocation')},actor)
            receipt=dict(receipt)
            try:ref=_verified_ref(receipt,'execution receipt')
            except ValueError as exc:return self._wait(cycle_id,state,phase,'WAITING_EXECUTOR',str(exc),['verified execution_receipt'],actor)
            status=str(receipt.get('status') or 'COMPLETED').upper();receipt['ref']=ref;a['execution_receipt']=receipt
            if status not in {'COMPLETED','FAILED'}:return self._wait(cycle_id,state,phase,'WAITING_EXECUTOR','execution receipt status must be COMPLETED or FAILED',['execution_receipt.status'],actor)
            if status=='FAILED':
                matches=self._cfg(state,'failure_antibody_matches') or [];repair=self.dev.transport.runtime.antibody_to_repair(a['aor_run']['next']['id'],matches,actor,True);a['repair_transport']=repair
                return self._wait(cycle_id,state,phase,'WAITING_REPAIR','execution failed; repair remains explicit unmeasured work',{'execution_ref':ref,'repair_candidates':repair.get('field_candidates',[])},actor)
            return self._event(cycle_id,state,phase,'EXECUTION_RECEIVED',{'candidate':a['aor_run']['next']['id'],'receipt_ref':ref},actor,next_phase='VERIFY')
        if phase=='VERIFY':
            test=self._cfg(state,'test_packet');ok,detail=_verified_test(test)
            if not ok:return self._wait(cycle_id,state,phase,'WAITING_TEST','witnessed test packet required after execution',detail,actor)
            a['test_packet']=dict(test);return self._event(cycle_id,state,phase,'TEST_VERIFIED',{'witness':test.get('witness'),'result':test.get('result')},actor,next_phase='LEARN')
        if phase=='LEARN':
            learning={};reward=self._cfg(state,'branch_reward')
            if isinstance(reward,Mapping):
                learning['branch']=self.server.branches.observe(reward['branch_id'],reward['basis_id'],reward['reward'],reward['witness'],reward.get('policy'),reward.get('triggers'),reward.get('metadata'),actor)
            rgo=self._cfg(state,'rgo_observation')
            if isinstance(rgo,Mapping):
                learning['rgo']=self.server.collective_memory.record_rgo_observation(rgo['plan_key'],rgo['predicted_rgo'],rgo['observed_rgo'],rgo.get('features'),rgo.get('scope','global'),actor)
            pher=self._cfg(state,'pheromone_observation')
            if isinstance(pher,Mapping):
                learning['pheromone']=self.server.collective_memory.pheromone_reinforce(pher['route_key'],pher['observations'],pher.get('age'),pher.get('evaporation_rate',.08),pher.get('deposit_gain',.35),actor)
            a['learning']=learning;return self._event(cycle_id,state,phase,'LEARN',{'updates':sorted(learning)},actor,next_phase='SUCCESSOR')
        if phase=='SUCCESSOR':
            successor=a['aor_run'].get('successor') or {'status':'READY','primary':a['aor_run']['next']['id']};state['return']={'next':a['aor_run']['next']['id'],'successor':successor,'aor_run_id':a['aor_run']['run_id'],'cycle_id':cycle_id};a['successor']=successor
            return self._event(cycle_id,state,phase,'SUCCESSOR',state['return'],actor,next_phase='COMPLETE')
        if phase=='COMPLETE':
            return self._event(cycle_id,state,phase,'COMPLETE',state['return'],actor,status='COMPLETE',next_phase='COMPLETE')
        raise ValueError(f'unknown cycle phase {phase}')

    def advance(self,cycle_id,inputs=None,max_steps=8):
        row=self._row(cycle_id)
        if row['status'] in TERMINAL:return self.get(cycle_id)
        state=row['state'];_deep_merge(state['supplied'],dict(inputs or {}));self._persist_state(cycle_id,state,row['phase'],'ACTIVE',row['last_eid'])
        try:limit=max(1,min(int(max_steps),64))
        except (TypeError,ValueError):raise ValueError('max_steps must be integer')
        steps=[]
        for _ in range(limit):
            row=self._row(cycle_id);event=self._step(cycle_id,row);steps.append(event);row=self._row(cycle_id)
            if row['status'] in WAITING|TERMINAL:break
        result=self.get(cycle_id);result['advance_events']=steps;return result

    def replay(self,cycle_id):
        row=self._row(cycle_id);stored=_json_digest(row['state']);checks={};a=row['state'].get('artifacts',{})
        def check(name,fn):
            try:result=fn();checks[name]={'status':'PASS' if result.get('match',True) else 'FAIL','detail':result}
            except Exception as exc:checks[name]={'status':'FAIL','error':f'{type(exc).__name__}: {exc}'}
        if a.get('retrieval_run',{}).get('run_id'):check('retrieval',lambda:self.dev.retrieval.replay(a['retrieval_run']['run_id']))
        if a.get('hug_invocation',{}).get('invocation_id'):check('hug_packet',lambda:self.dev.hug.verify_packet(a['hug_invocation']['invocation_id']))
        if a.get('gap_run',{}).get('run_id'):check('gap',lambda:self.dev.gap.replay(a['gap_run']['run_id']))
        if a.get('field_run',{}).get('run_id'):check('field',lambda:self.dev.field.replay(a['field_run']['run_id']))
        if a.get('aor_run',{}).get('run_id'):check('aor',lambda:self.server.orchestration.replay(a['aor_run']['run_id']))
        if a.get('aor_collective_transport',{}).get('run_id'):check('transport',lambda:self.dev.transport.runtime.replay(a['aor_collective_transport']['run_id']))
        match=stored==row['state_digest'] and all(v['status']=='PASS' for v in checks.values())
        return {'cycle_id':cycle_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_state_digest':row['state_digest'],'recomputed_state_digest':stored,'child_checks':checks,'phase':row['phase'],'cycle_status':row['status']}

    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM cycle_runs')['n'];statuses={r['status']:r['n'] for r in self.s.rows('SELECT status,COUNT(*) n FROM cycle_runs GROUP BY status')};return {'cycle_runs':count,'cycle_status':statuses,'cycle_events':self.s.one('SELECT COUNT(*) n FROM cycle_events')['n']}

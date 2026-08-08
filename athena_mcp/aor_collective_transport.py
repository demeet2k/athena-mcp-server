from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any, Iterable, Mapping

from .identity import digest,event_id

TRANSPORT_VERSION='AORCOLL.TRANSPORT.1'
TRANSPORT_SCHEMA='''
CREATE TABLE IF NOT EXISTS transport_runs(
 run_id TEXT PRIMARY KEY,
 kind TEXT NOT NULL,
 actor TEXT NOT NULL,
 input_json TEXT NOT NULL,
 output_json TEXT NOT NULL,
 transport_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transport_runs_created ON transport_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_transport_runs_kind ON transport_runs(kind,created_at);
'''


def _finite(value):
    if isinstance(value,bool):return None
    try:out=float(value)
    except (TypeError,ValueError):return None
    return out if math.isfinite(out) else None


def _digest(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def _extract_pheromone_score(snapshot):
    rows=[]
    if isinstance(snapshot,list):rows=snapshot
    elif isinstance(snapshot,Mapping):
        if isinstance(snapshot.get('routes'),list):rows=snapshot['routes']
        elif isinstance(snapshot.get('field'),list):rows=snapshot['field']
        else:rows=[snapshot]
    for row in rows:
        if not isinstance(row,Mapping):continue
        for key in ('score','pheromone_score','priority','value'):
            value=_finite(row.get(key))
            if value is not None:return value
    return None


def pheromone_attention_packet(route_key,snapshot):
    score=_extract_pheromone_score(snapshot)
    return {
        'transport_kind':'PHEROMONE_TO_ATTENTION','route_key':str(route_key),'attention_priority':score,
        'pheromone_snapshot':snapshot,'rag_metric_patch':{},'authority_patch':{},'evidence_patch':{},
        'boundary':'pheromone/reuse is an attention-routing prior only; it does not populate relevance, source_authority, evidence, confidence, Y authority, or truth',
    }


def alarm_gap_packet(alarm_ref,alarm_nodes):
    targets=[]
    for index,raw in enumerate(alarm_nodes or []):
        row=dict(raw);node=str(row.get('node') or '').strip()
        if not node:raise ValueError('alarm node requires node')
        severity=_finite(row.get('severity'));target={'id':str(row.get('id') or f'alarm:{index:04d}:{node}'),'node':node,'alarm_ref':str(alarm_ref)}
        if severity is not None and severity>=0:target['severity']=severity
        targets.append(target)
    return {
        'transport_kind':'ALARM_TO_GAP','alarm_ref':str(alarm_ref),'targets':targets,
        'measurement_required':['leverage','information_gain','cost'],
        'boundary':'alarm transport identifies revalidation/repair pressure; it does not prove the alarmed node is false, invalid, causally downstream, or logically entailed beyond the alarm system’s own typed semantics',
    }


def aor_collective_task_packet(aor_run):
    output=dict((aor_run or {}).get('output') or aor_run or {});rows=output.get('budgeted_successor_frontier') or output.get('successor_frontier') or [];tasks=[];measurement=[]
    required=('utility','gap','bridge_value','saturation','urgency')
    for row in rows:
        ident=str(row.get('id'));source=dict(row.get('source') or {});metrics=dict(source.get('collective_metrics') or {});task={'id':ident,'candidate_ref':ident,'required_capabilities':list(source.get('required_capabilities') or [])};missing=[]
        for name in required:
            value=_finite(metrics.get(name))
            if value is None or not 0<=value<=1:missing.append(name)
            else:task[name]=value
        task['allocation_state']='READY' if not missing else 'UNMEASURED';tasks.append(task)
        if missing:measurement.append({'candidate':ident,'missing_collective_metrics':missing})
    return {
        'transport_kind':'AOR_FRONTIER_TO_COLLECTIVE_TASKS','aor_run_id':(aor_run or {}).get('run_id'),'tasks':tasks,
        'allocation_ready_ids':[t['id'] for t in tasks if t['allocation_state']=='READY'],'measurement_plan':measurement,
        'boundary':'AOR selects WHAT is developmentally eligible; this transport does not invent worker-allocation utility. Collective metrics must be explicit before automatic allocation; Collective decides HOW capacity is assigned and does not change AOR score/Y authority',
    }


def rgo_reward_packet(outcome_ref,observed_rgo,witness_ref,delta_j=None,delta_outcome_ref=None):
    rgo=_finite(observed_rgo)
    if rgo is None:raise ValueError('observed_rgo must be finite')
    witness=str(witness_ref or '').strip()
    if not witness:raise ValueError('observed RGO requires witness_ref')
    dj=_finite(delta_j) if delta_j is not None else None;same=bool(dj is not None and str(delta_outcome_ref or '')==str(outcome_ref))
    return {
        'transport_kind':'OBSERVED_RGO_TO_REWARD_OBSERVATION','outcome_ref':str(outcome_ref),'observed_rgo':rgo,'witness_ref':witness,
        'delta_j':dj,'delta_outcome_ref':delta_outcome_ref,'double_count_guard':'SAME_OUTCOME_DO_NOT_SUM' if same else 'SEPARATE_OR_UNSPECIFIED_OUTCOME',
        'aor_reward_patch':{},'authority_patch':{},
        'boundary':'observed RGO is an outcome observation, not automatic AOR DeltaJ/evidence/authority. A mapping into reward requires an explicit calibrated policy; the same outcome must not be counted twice merely because it appears under RGO and DeltaJ labels',
    }


def bridge_account_packet(candidate_ref,economics):
    economics=dict(economics or {});required=('expected_future_uses','route_saving_per_use','quality_gain','resilience_gain','build_cost','maintenance_cost','locked_capacity_cost');missing=[];packet={}
    for name in required:
        value=_finite(economics.get(name))
        if value is None or value<0:missing.append(name)
        else:packet[name]=value
    if missing:raise ValueError(f'bridge economics require nonnegative explicit values for {missing}')
    return {
        'transport_kind':'AOR_BRIDGE_TO_COLLECTIVE_ACCOUNT','candidate_ref':str(candidate_ref),'bridge':packet,
        'boundary':'bridge value in AOR and bridge economics in Collective are distinct measurements; this adapter carries explicit economics and does not derive them from an AOR bridge score',
    }


def antibody_repair_packet(failure_ref,matches):
    candidates=[]
    for index,raw in enumerate(matches or []):
        row=dict(raw);aid=str(row.get('antibody_id') or row.get('id') or f'antibody:{index:04d}');repair=row.get('repair')
        if repair in (None,{},''):continue
        target=str(row.get('target_ref') or failure_ref);signature={'kind':'REPAIR','operation':'apply_antibody_repair','target_ref':target,'payload':{'antibody_id':aid,'repair':repair},'dependencies':[]}
        cid='PHI.'+_digest(signature)[:24]
        candidates.append({**signature,'id':cid,'source_refs':[str(failure_ref),aid],'field_origin':['COLLECTIVE_ANTIBODY'],'metric_state':'UNMEASURED'})
    return {
        'transport_kind':'ANTIBODY_TO_REPAIR_CANDIDATE','failure_ref':str(failure_ref),'field_candidates':candidates,
        'boundary':'antibody matches suggest reusable repair candidates only; they are not auto-executed, are not evidence that repair will work here, and require FIELD/AOR measurement plus witnessed testing before promotion',
    }


class TransportRuntime:
    def __init__(self,server):
        self.server=server;self.core=server.core;self.s=server.store
        with self.s.db:self.s.db.executescript(TRANSPORT_SCHEMA)
        self.core.register('TOOL','INTEGRATION','TRANSPORT','AOR_COLLECTIVE','TYPED_FIREWALLED_BRIDGES',
            {'source':'AOR|Collective organ receipt','transport_kind':'typed'},{'packet':'typed','authority_patch':'empty by default','evidence_patch':'empty by default'},
            actor='GENESIS.AORCOLL.1',status='CANONICAL')

    def _persist(self,kind,inputs,output,actor,persist):
        carrier={'version':TRANSPORT_VERSION,'kind':kind,'input':inputs,'output':output};td=_digest(carrier)
        if not persist:return {**output,'version':TRANSPORT_VERSION,'transport_digest':td,'persisted':False}
        parent=self.s.head('global');pe=parent['eid'] if parent else None;payload={'operation':'TRANSPORT','kind':kind,'transport_digest':td};eid=event_id('AOR_COLLECTIVE_TRANSPORT',actor,pe,payload);ed=digest(payload,32);run_id='TRANSPORTRUN.'+digest({'eid':eid,'transport_digest':td},24)
        with self.s.db:self.s.db.execute('INSERT INTO transport_runs VALUES(?,?,?,?,?,?,?,?)',(run_id,kind,actor,json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(output,sort_keys=True,ensure_ascii=False),td,eid,time.time()))
        self.s.put_event(eid,'AOR_COLLECTIVE_TRANSPORT',actor,pe,payload,ed);self.s.set_head('global',None,None,eid,ed)
        return {**output,'version':TRANSPORT_VERSION,'transport_digest':td,'persisted':True,'run_id':run_id,'eid':eid}

    def pheromone_attention(self,route_keys,actor='agent',persist=True):
        snapshots=[];packets=[]
        for key in route_keys:
            snapshot=self.server.collective_memory.pheromone_field(str(key),1,0.0);snapshots.append({'route_key':str(key),'snapshot':snapshot});packets.append(pheromone_attention_packet(key,snapshot))
        return self._persist('PHEROMONE_TO_ATTENTION',{'route_keys':[str(x) for x in route_keys],'snapshots':snapshots},{'transport_kind':'PHEROMONE_TO_ATTENTION','packets':packets,'boundary':'no RAG/Y/evidence field is populated by this transport'},actor,persist)

    def alarm_to_gap(self,alarm_ref,alarm_nodes,actor='agent',persist=True):
        inputs={'alarm_ref':str(alarm_ref),'alarm_nodes':[dict(x) for x in alarm_nodes]};return self._persist('ALARM_TO_GAP',inputs,alarm_gap_packet(**inputs),actor,persist)

    def aor_to_collective(self,run_id,actor='agent',persist=True):
        aor=self.server.orchestration.get(run_id);inputs={'run_id':run_id,'decision_digest':aor['decision_digest'],'aor_output':aor['output']};return self._persist('AOR_FRONTIER_TO_COLLECTIVE_TASKS',inputs,aor_collective_task_packet(aor),actor,persist)

    def rgo_to_reward(self,outcome_ref,observed_rgo,witness_ref,delta_j=None,delta_outcome_ref=None,actor='agent',persist=True):
        inputs={'outcome_ref':str(outcome_ref),'observed_rgo':observed_rgo,'witness_ref':str(witness_ref),'delta_j':delta_j,'delta_outcome_ref':delta_outcome_ref};return self._persist('OBSERVED_RGO_TO_REWARD_OBSERVATION',inputs,rgo_reward_packet(**inputs),actor,persist)

    def bridge_to_collective(self,candidate_ref,economics,actor='agent',persist=True):
        inputs={'candidate_ref':str(candidate_ref),'economics':dict(economics)};return self._persist('AOR_BRIDGE_TO_COLLECTIVE_ACCOUNT',inputs,bridge_account_packet(**inputs),actor,persist)

    def antibody_to_repair(self,failure_ref,matches,actor='agent',persist=True):
        inputs={'failure_ref':str(failure_ref),'matches':[dict(x) for x in matches]};return self._persist('ANTIBODY_TO_REPAIR_CANDIDATE',inputs,antibody_repair_packet(**inputs),actor,persist)

    def get(self,run_id):
        row=self.s.one('SELECT * FROM transport_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown transport run')
        return {'run_id':row['run_id'],'kind':row['kind'],'actor':row['actor'],'input':json.loads(row['input_json']),'output':json.loads(row['output_json']),'transport_digest':row['transport_digest'],'eid':row['eid'],'created_at':row['created_at']}

    def replay(self,run_id):
        stored=self.get(run_id);kind=stored['kind'];inp=stored['input']
        if kind=='PHEROMONE_TO_ATTENTION':out={'transport_kind':'PHEROMONE_TO_ATTENTION','packets':[pheromone_attention_packet(x['route_key'],x['snapshot']) for x in inp['snapshots']],'boundary':'no RAG/Y/evidence field is populated by this transport'}
        elif kind=='ALARM_TO_GAP':out=alarm_gap_packet(inp['alarm_ref'],inp['alarm_nodes'])
        elif kind=='AOR_FRONTIER_TO_COLLECTIVE_TASKS':out=aor_collective_task_packet({'run_id':inp['run_id'],'output':inp['aor_output']})
        elif kind=='OBSERVED_RGO_TO_REWARD_OBSERVATION':out=rgo_reward_packet(inp['outcome_ref'],inp['observed_rgo'],inp['witness_ref'],inp.get('delta_j'),inp.get('delta_outcome_ref'))
        elif kind=='AOR_BRIDGE_TO_COLLECTIVE_ACCOUNT':out=bridge_account_packet(inp['candidate_ref'],inp['economics'])
        elif kind=='ANTIBODY_TO_REPAIR_CANDIDATE':out=antibody_repair_packet(inp['failure_ref'],inp['matches'])
        else:raise ValueError(f'unknown stored transport kind {kind}')
        td=_digest({'version':TRANSPORT_VERSION,'kind':kind,'input':inp,'output':out});match=td==stored['transport_digest']
        return {'run_id':run_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_transport_digest':stored['transport_digest'],'recomputed_transport_digest':td,'kind':kind}

    def recent(self,limit=50):
        limit=max(1,min(int(limit),500));return self.s.rows('SELECT run_id,kind,actor,transport_digest,eid,created_at FROM transport_runs ORDER BY created_at DESC LIMIT ?',(limit,))

    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM transport_runs')['n'];by={r['kind']:r['n'] for r in self.s.rows('SELECT kind,COUNT(*) n FROM transport_runs GROUP BY kind')}
        return {'transport_runs':count,'transport_by_kind':by}

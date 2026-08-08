from __future__ import annotations

import json,time
from typing import Any,Mapping,Optional
from .identity import digest,event_id
from .orchestration_authority_compile import compile_authority_orchestration
from .orchestration_runtime import ORCHESTRATION_SCHEMA

class AuthorityOrchestrationRuntime:
    def __init__(self,core,branches=None,authority=None):
        self.core=core;self.s=core.s;self.branches=branches;self.authority=authority
        with self.s.db:self.s.db.executescript(ORCHESTRATION_SCHEMA)
    def _snapshot_candidates(self,candidates,metric_contract):
        rows=list(candidates or []);basis_id=str((metric_contract or {}).get('basis_id') or 'RAW.UNDECLARED')
        if self.branches is not None:rows=self.branches.enrich_candidates(rows,basis_id)
        if self.authority is not None:rows=self.authority.enrich_candidates(rows)
        return rows
    def compile(self,seed:Any,candidates=None,residuals=None,budget:Optional[Mapping[str,Any]]=None,metric_contract:Optional[Mapping[str,Any]]=None,actor:str='agent',task:str='',session_id:Optional[str]=None,persist:bool=True):
        metric_contract=dict(metric_contract or {});inputs={'seed':seed,'candidates':self._snapshot_candidates(candidates,metric_contract),'residuals':list(residuals or []),'budget':dict(budget or {}),'metric_contract':metric_contract};output=compile_authority_orchestration(**inputs)
        if not persist:return {**output,'persisted':False}
        parent=self.s.head('global');pe=parent['eid'] if parent else None;payload={'operation':'AOR_COMPILE_AUTHORITY','actor':actor,'task':task,'session_id':session_id,'metric_basis':output.get('metric_contract',{}).get('basis_id'),'metric_strict':output.get('metric_contract',{}).get('strict'),'allocation':output.get('allocation_plan',{}).get('selected',[]),'authority_claims':sorted(s.get('claim_id') for s in output.get('authority_snapshot',{}).values() if s.get('claim_id')),'decision_digest':output['decision_digest'],'next':output['next']['id'] if output.get('next') else None,'grow':output['grow']['id'] if output.get('grow') else None,'pareto':output.get('pareto_successor_frontier',[])};eid=event_id('AOR_COMPILE_AUTHORITY',actor,pe,payload);ed=digest(payload,32);run_id='AORRUN.'+digest({'eid':eid,'decision':output['decision_digest']},24)
        with self.s.db:self.s.db.execute('INSERT INTO orchestration_runs VALUES(?,?,?,?,?,?,?,?,?)',(run_id,actor,task,session_id,json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(output,sort_keys=True,ensure_ascii=False),output['decision_digest'],eid,time.time()))
        self.s.put_event(eid,'AOR_COMPILE_AUTHORITY',actor,pe,payload,ed);self.s.set_head('global',None,None,eid,ed);return {**output,'persisted':True,'run_id':run_id,'eid':eid}
    def get(self,run_id):
        row=self.s.one('SELECT * FROM orchestration_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown orchestration run')
        return {'run_id':row['run_id'],'actor':row['actor'],'task':row['task'],'session_id':row['session_id'],'input':json.loads(row['input_json']),'output':json.loads(row['output_json']),'decision_digest':row['decision_digest'],'eid':row['eid'],'created_at':row['created_at']}
    def recent(self,limit=20):
        limit=max(1,min(int(limit),200));return self.s.rows('SELECT run_id,actor,task,session_id,decision_digest,eid,created_at FROM orchestration_runs ORDER BY created_at DESC LIMIT ?',(limit,))
    def replay(self,run_id):
        stored=self.get(run_id);recomputed=compile_authority_orchestration(**stored['input']);match=recomputed['decision_digest']==stored['decision_digest']
        return {'run_id':run_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_decision_digest':stored['decision_digest'],'recomputed_decision_digest':recomputed['decision_digest'],'stored_authority_snapshot':stored['output'].get('authority_snapshot',{}),'recomputed_authority_snapshot':recomputed.get('authority_snapshot',{}),'stored_allocation':stored['output'].get('allocation_plan',{}).get('selected',[]),'recomputed_allocation':recomputed.get('allocation_plan',{}).get('selected',[]),'stored_next':(stored['output'].get('next') or {}).get('id'),'recomputed_next':(recomputed.get('next') or {}).get('id'),'stored_grow':(stored['output'].get('grow') or {}).get('id'),'recomputed_grow':(recomputed.get('grow') or {}).get('id'),'stored_pareto':stored['output'].get('pareto_successor_frontier',[]),'recomputed_pareto':recomputed.get('pareto_successor_frontier',[])}
    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM orchestration_runs')['n'];checked=0;matches=0
        for row in self.s.rows('SELECT run_id FROM orchestration_runs ORDER BY created_at DESC LIMIT 20'):
            checked+=1
            if self.replay(row['run_id'])['match']:matches+=1
        return {'orchestration_runs':count,'replay_sample':checked,'replay_matches':matches,'replay_match_rate':matches/checked if checked else None}

from __future__ import annotations

import json,time
from typing import Any,Mapping,Optional
from .identity import digest,event_id
from .orchestration import compile_orchestration

ORCHESTRATION_SCHEMA='''
CREATE TABLE IF NOT EXISTS orchestration_runs(
 run_id TEXT PRIMARY KEY,
 actor TEXT NOT NULL,
 task TEXT NOT NULL,
 session_id TEXT,
 input_json TEXT NOT NULL,
 output_json TEXT NOT NULL,
 decision_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orchestration_runs_created ON orchestration_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_orchestration_runs_session ON orchestration_runs(session_id);
'''

class OrchestrationRuntime:
    def __init__(self,core,branches=None):
        self.core=core;self.s=core.s;self.branches=branches
        with self.s.db:self.s.db.executescript(ORCHESTRATION_SCHEMA)
        seeds=[('ALGO','DEVELOPMENT','COMPILE','ORCHESTRATION_FRONTIER','AOR3_UNKNOWN_SAFE',{'seed':'any','candidates':'explicit metrics + lifecycle snapshot','residuals':'explicit metrics','metric_contract':'basis/scales'},{'frontier':'ranked','measurement_frontier':'unknown-safe','calibration_frontier':'basis-safe','budget_allocation':'typed','pareto_frontier':'ids','next':'candidate|none','decision_digest':'sha256'}),('TOOL','REPLAY','VERIFY','ORCHESTRATION_RUN','AOR_DECISION_DIGEST',{'run_id':'AORRUN'},{'status':'REPLAY_MATCH|REPLAY_DIVERGED','stored_digest':'sha256','recomputed_digest':'sha256'})]
        for args in seeds:self.core.register(*args,actor='GENESIS.AOR.3',status='CANONICAL')
    def compile(self,seed:Any,candidates=None,residuals=None,budget:Optional[Mapping[str,Any]]=None,metric_contract:Optional[Mapping[str,Any]]=None,actor:str='agent',task:str='',session_id:Optional[str]=None,persist:bool=True):
        metric_contract=dict(metric_contract or {});basis_id=str(metric_contract.get('basis_id') or 'RAW.UNDECLARED');rows=list(candidates or [])
        if self.branches is not None:rows=self.branches.enrich_candidates(rows,basis_id)
        inputs={'seed':seed,'candidates':rows,'residuals':list(residuals or []),'budget':dict(budget or {}),'metric_contract':metric_contract};output=compile_orchestration(**inputs)
        if not persist:return {**output,'persisted':False}
        parent=self.s.head('global');parent_eid=parent['eid'] if parent else None;event_payload={'operation':'AOR_COMPILE','actor':actor,'task':task,'session_id':session_id,'metric_basis':output.get('metric_contract',{}).get('basis_id'),'metric_strict':output.get('metric_contract',{}).get('strict'),'allocation':output.get('allocation_plan',{}).get('selected',[]),'decision_digest':output['decision_digest'],'next':output['next']['id'] if output.get('next') else None,'grow':output['grow']['id'] if output.get('grow') else None,'pareto':output.get('pareto_successor_frontier',[])}
        eid=event_id('AOR_COMPILE',actor,parent_eid,event_payload);ed=digest(event_payload,32);run_id='AORRUN.'+digest({'eid':eid,'decision':output['decision_digest']},24)
        with self.s.db:self.s.db.execute('INSERT INTO orchestration_runs VALUES(?,?,?,?,?,?,?,?,?)',(run_id,actor,task,session_id,json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(output,sort_keys=True,ensure_ascii=False),output['decision_digest'],eid,time.time()))
        self.s.put_event(eid,'AOR_COMPILE',actor,parent_eid,event_payload,ed);self.s.set_head('global',None,None,eid,ed)
        return {**output,'persisted':True,'run_id':run_id,'eid':eid}
    def get(self,run_id:str):
        row=self.s.one('SELECT * FROM orchestration_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown orchestration run')
        return {'run_id':row['run_id'],'actor':row['actor'],'task':row['task'],'session_id':row['session_id'],'input':json.loads(row['input_json']),'output':json.loads(row['output_json']),'decision_digest':row['decision_digest'],'eid':row['eid'],'created_at':row['created_at']}
    def recent(self,limit:int=20):
        limit=max(1,min(int(limit),200));return self.s.rows('SELECT run_id,actor,task,session_id,decision_digest,eid,created_at FROM orchestration_runs ORDER BY created_at DESC LIMIT ?',(limit,))
    def replay(self,run_id:str):
        stored=self.get(run_id);recomputed=compile_orchestration(**stored['input']);match=recomputed['decision_digest']==stored['decision_digest']
        return {'run_id':run_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','stored_decision_digest':stored['decision_digest'],'recomputed_decision_digest':recomputed['decision_digest'],'match':match,'stored_metric_basis':stored['output'].get('metric_contract'),'recomputed_metric_basis':recomputed.get('metric_contract'),'stored_allocation':stored['output'].get('allocation_plan',{}).get('selected',[]),'recomputed_allocation':recomputed.get('allocation_plan',{}).get('selected',[]),'stored_next':(stored['output'].get('next') or {}).get('id'),'recomputed_next':(recomputed.get('next') or {}).get('id'),'stored_grow':(stored['output'].get('grow') or {}).get('id'),'recomputed_grow':(recomputed.get('grow') or {}).get('id'),'stored_pareto':stored['output'].get('pareto_successor_frontier',[]),'recomputed_pareto':recomputed.get('pareto_successor_frontier',[])}
    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM orchestration_runs')['n'];matches=0;checked=0
        for row in self.s.rows('SELECT run_id FROM orchestration_runs ORDER BY created_at DESC LIMIT 20'):
            checked+=1
            if self.replay(row['run_id'])['match']:matches+=1
        return {'orchestration_runs':count,'replay_sample':checked,'replay_matches':matches,'replay_match_rate':matches/checked if checked else None}

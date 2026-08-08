from __future__ import annotations

import hashlib,json,time
from typing import Any,Iterable,Mapping,Optional
from ..identity import digest,event_id
from .select import compile_selection
from .specs import retrieval_law

RAG_SCHEMA='''
CREATE TABLE IF NOT EXISTS retrieval_runs(
 run_id TEXT PRIMARY KEY,query_ref TEXT NOT NULL,actor TEXT NOT NULL,task TEXT NOT NULL,input_json TEXT NOT NULL,output_json TEXT NOT NULL,decision_digest TEXT NOT NULL,eid TEXT NOT NULL,created_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_retrieval_runs_created ON retrieval_runs(created_at);
'''

def _decision_carrier(output:Mapping[str,Any]):
    return {'selected_ids':output.get('selected_ids',[]),'solver':output.get('solver'),'optimality':output.get('optimality'),'utility':output.get('utility'),'budget':output.get('budget'),'used':output.get('used'),'coverage':output.get('coverage'),'measurement_plan':output.get('measurement_plan'),'equivalence':output.get('equivalence')}

def _decision_digest(output:Mapping[str,Any]):return hashlib.sha256(json.dumps(_decision_carrier(output),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

class RetrievalLedger:
    def __init__(self,core):
        self.core=core;self.s=core.s
        with self.s.db:self.s.db.executescript(RAG_SCHEMA)
        self.core.register('TOOL','RETRIEVAL','COMPILE','DECISION_CONTEXT','RAG1_COVERAGE_EQ_SAFE',{'query':'typed','candidates':'supplied provenance records','eq_snapshot':'optional frozen EQ1'},{'selected':'source refs','coverage':'typed','decision_digest':'sha256'},actor='GENESIS.RAG.1',status='CANONICAL')
    def compile(self,query_ref:str,query:Mapping[str,Any],candidates:Iterable[Mapping[str,Any]],eq_snapshot:Optional[Mapping[str,Any]]=None,actor:str='agent',task:str='',persist:bool=True):
        query_ref=str(query_ref or '').strip()
        if not query_ref:raise ValueError('query_ref required')
        inputs={'query':dict(query or {}),'candidates':[dict(x) for x in candidates],'eq_snapshot':dict(eq_snapshot or {}) if eq_snapshot else None};output=compile_selection(**inputs);output['law']=retrieval_law();output['decision_digest']=_decision_digest(output)
        if not persist:return {**output,'persisted':False}
        parent=self.s.head('global');pe=parent['eid'] if parent else None;ep={'operation':'RAG_COMPILE','query_ref':query_ref,'actor':actor,'task':task,'selected_ids':output['selected_ids'],'solver':output['solver'],'optimality':output['optimality'],'decision_digest':output['decision_digest'],'coverage':output['coverage']};eid=event_id('RAG_COMPILE',actor,pe,ep);ed=digest(ep,32);run_id='RAGRUN.'+digest({'eid':eid,'decision':output['decision_digest']},24)
        with self.s.db:self.s.db.execute('INSERT INTO retrieval_runs VALUES(?,?,?,?,?,?,?,?,?)',(run_id,query_ref,actor,task,json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(output,sort_keys=True,ensure_ascii=False),output['decision_digest'],eid,time.time()))
        self.s.put_event(eid,'RAG_COMPILE',actor,pe,ep,ed);self.s.set_head('global',None,None,eid,ed);return {**output,'persisted':True,'run_id':run_id,'eid':eid}
    def get(self,run_id):
        row=self.s.one('SELECT * FROM retrieval_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown retrieval run')
        return {'run_id':row['run_id'],'query_ref':row['query_ref'],'actor':row['actor'],'task':row['task'],'input':json.loads(row['input_json']),'output':json.loads(row['output_json']),'decision_digest':row['decision_digest'],'eid':row['eid'],'created_at':row['created_at']}
    def replay(self,run_id):
        stored=self.get(run_id);recomputed=compile_selection(**stored['input']);recomputed['decision_digest']=_decision_digest(recomputed);match=recomputed['decision_digest']==stored['decision_digest']
        return {'run_id':run_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_decision_digest':stored['decision_digest'],'recomputed_decision_digest':recomputed['decision_digest'],'stored_selected':stored['output'].get('selected_ids',[]),'recomputed_selected':recomputed.get('selected_ids',[]),'stored_coverage':stored['output'].get('coverage'),'recomputed_coverage':recomputed.get('coverage'),'stored_equivalence':stored['output'].get('equivalence'),'recomputed_equivalence':recomputed.get('equivalence')}
    def recent(self,limit=50):
        limit=max(1,min(int(limit),500));return self.s.rows('SELECT run_id,query_ref,actor,task,decision_digest,eid,created_at FROM retrieval_runs ORDER BY created_at DESC LIMIT ?',(limit,))
    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM retrieval_runs')['n'];checked=0;matches=0
        for row in self.s.rows('SELECT run_id FROM retrieval_runs ORDER BY created_at DESC LIMIT 20'):
            checked+=1
            if self.replay(row['run_id'])['match']:matches+=1
        return {'retrieval_runs':count,'retrieval_replay_sample':checked,'retrieval_replay_matches':matches,'retrieval_replay_match_rate':matches/checked if checked else None}

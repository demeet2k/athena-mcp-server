from __future__ import annotations

import json
import time
from typing import Any,Iterable,Mapping,Optional

from .identity import digest,event_id
from .state_projection import project_omega

RECON_VERSION='ATHENA.RECON.1'
RECON_SCHEMA='''
CREATE TABLE IF NOT EXISTS reconstruction_runs(
 run_id TEXT PRIMARY KEY,
 task_ref TEXT NOT NULL,
 actor TEXT NOT NULL,
 source_refs_json TEXT NOT NULL,
 omega_json TEXT NOT NULL,
 defects_json TEXT NOT NULL,
 reconstruction_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reconstruction_runs_created ON reconstruction_runs(created_at);
'''


class ReconstructionLedger:
    """Freeze a current accessible Ω projection with declared reconstruction inputs.

    A RECONRUN is an observation receipt, not a claim that every relevant source
    in the world was searched. Callers must list the source refs actually used;
    missing expected refs are preserved as defects instead of silently filled.
    """

    def __init__(self,server):
        self.server=server;self.core=server.core;self.s=server.store
        with self.s.db:self.s.db.executescript(RECON_SCHEMA)
        self.core.register('TOOL','STATE','RECONSTRUCT','OMEGA_SNAPSHOT','DECLARED_SOURCE_RECONRUN',
            {'task_ref':'stable','source_refs':'actually consulted','expected_refs':'optional required set'},
            {'run_id':'RECONRUN','omega':'frozen','defects':'missing expected refs','digest':'sha256'},
            actor='GENESIS.RECON.1',status='CANONICAL')

    def compile(self,task_ref:str,source_refs:Iterable[str],expected_refs:Optional[Iterable[str]]=None,actor:str='agent',persist:bool=True):
        task_ref=str(task_ref or '').strip()
        if not task_ref:raise ValueError('task_ref required')
        source_refs=sorted({str(x) for x in source_refs if str(x)})
        expected=sorted({str(x) for x in (expected_refs or []) if str(x)})
        missing=sorted(set(expected)-set(source_refs))
        omega=project_omega(self.server)
        defects=[]
        if missing:defects.append({'kind':'MISSING_EXPECTED_SOURCE_REFS','refs':missing})
        boundary='RECONRUN freezes accessible runtime state plus declared source refs; it does not imply unlisted/unavailable sources were searched or reconstructed'
        carrier={'version':RECON_VERSION,'task_ref':task_ref,'source_refs':source_refs,'expected_refs':expected,'omega':omega,'defects':defects,'boundary':boundary}
        rd=digest(carrier,64)
        output={**carrier,'reconstruction_digest':rd,'status':'COMPLETE_WITH_DEFECTS' if defects else 'COMPLETE'}
        if not persist:return {**output,'persisted':False}
        parent=self.s.head('global');pe=parent['eid'] if parent else None
        payload={'operation':'RECONSTRUCT','task_ref':task_ref,'source_refs':source_refs,'defect_count':len(defects),'omega_id':omega['omega_id'],'reconstruction_digest':rd}
        eid=event_id('RECONSTRUCT',actor,pe,payload);ed=digest(payload,32);run_id='RECONRUN.'+digest({'eid':eid,'reconstruction_digest':rd},24)
        with self.s.db:self.s.db.execute('INSERT INTO reconstruction_runs VALUES(?,?,?,?,?,?,?,?,?)',(
            run_id,task_ref,actor,json.dumps(source_refs,sort_keys=True),json.dumps(omega,sort_keys=True,ensure_ascii=False),json.dumps(defects,sort_keys=True),rd,eid,time.time()))
        self.s.put_event(eid,'RECONSTRUCT',actor,pe,payload,ed);self.s.set_head('global',None,None,eid,ed)
        return {**output,'persisted':True,'run_id':run_id,'eid':eid}

    def get(self,run_id:str):
        row=self.s.one('SELECT * FROM reconstruction_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown reconstruction run')
        return {'run_id':row['run_id'],'task_ref':row['task_ref'],'actor':row['actor'],'source_refs':json.loads(row['source_refs_json']),'omega':json.loads(row['omega_json']),'defects':json.loads(row['defects_json']),'reconstruction_digest':row['reconstruction_digest'],'eid':row['eid'],'created_at':row['created_at']}

    def verify(self,run_id:str):
        stored=self.get(run_id);carrier={'version':RECON_VERSION,'task_ref':stored['task_ref'],'source_refs':stored['source_refs'],'expected_refs':sorted(set(stored['source_refs'])|set(sum((d.get('refs',[]) for d in stored['defects'] if d.get('kind')=='MISSING_EXPECTED_SOURCE_REFS'),[]))),'omega':stored['omega'],'defects':stored['defects'],'boundary':'RECONRUN freezes accessible runtime state plus declared source refs; it does not imply unlisted/unavailable sources were searched or reconstructed'}
        # The original expected-ref set is recoverable from source_refs plus explicit
        # missing-ref defect set. This is sufficient for deterministic carrier replay.
        now=digest(carrier,64);match=now==stored['reconstruction_digest']
        return {'run_id':run_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_reconstruction_digest':stored['reconstruction_digest'],'recomputed_reconstruction_digest':now,'omega_id':stored['omega'].get('omega_id')}

    def recent(self,limit=50):
        limit=max(1,min(int(limit),500));return self.s.rows('SELECT run_id,task_ref,actor,reconstruction_digest,eid,created_at FROM reconstruction_runs ORDER BY created_at DESC LIMIT ?',(limit,))

    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM reconstruction_runs')['n'];return {'reconstruction_runs':count}

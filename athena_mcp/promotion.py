from __future__ import annotations

import json
import time
from typing import Any, Dict, Mapping, Optional

from .identity import digest,event_id

PROMOTION_VERSION="ATHENA.PROMOTION.1"
PROMOTION_SCHEMA='''
CREATE TABLE IF NOT EXISTS promotion_runs(
 run_id TEXT PRIMARY KEY,
 candidate_server TEXT NOT NULL,
 git_head TEXT NOT NULL,
 status TEXT NOT NULL,
 input_json TEXT NOT NULL,
 certificate_json TEXT NOT NULL,
 decision_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_promotion_runs_created ON promotion_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_promotion_runs_head ON promotion_runs(git_head);
'''


def _witness(packet: Mapping[str,Any],expected_head: str,label: str) -> Dict[str,Any]:
    observed=bool(packet.get('observed'))
    ref=str(packet.get('ref') or '')
    head=str(packet.get('head_sha') or '')
    conclusion=str(packet.get('conclusion') or '')
    defects=[]
    if not observed:defects.append('not_observed')
    if not ref:defects.append('missing_ref')
    if head!=expected_head:defects.append('head_mismatch')
    if conclusion!='success':defects.append('conclusion_not_success')
    return {
        'kind':label,
        'status':'PASS' if not defects else 'FAIL',
        'observed':observed,
        'ref':ref or None,
        'head_sha':head or None,
        'conclusion':conclusion or None,
        'defects':defects,
        'boundary':'external witness packet supplied by caller; receipt preserves the attestation and exact reference but does not independently fetch the external system',
    }


def evaluate_promotion(candidate_server: str,git_head: str,surface_audit: Mapping[str,Any],ci_witness: Mapping[str,Any],smoke_witness: Mapping[str,Any]) -> Dict[str,Any]:
    candidate_server=str(candidate_server);git_head=str(git_head)
    surface_status=str(surface_audit.get('surface_status') or surface_audit.get('status') or 'UNKNOWN')
    composition=(surface_audit.get('composition') or {})
    composition_status=str(composition.get('status') or 'UNKNOWN')
    ci=_witness(ci_witness,git_head,'CI')
    smoke=_witness(smoke_witness,git_head,'SMOKE')
    gates={
        'candidate_server':{'status':'PASS' if candidate_server=='FieldServer' else 'FAIL','observed':candidate_server},
        'surface':{'status':surface_status},
        'composition':{'status':composition_status},
        'ci':ci,
        'smoke':smoke,
    }
    qualified=all(gate.get('status')=='PASS' for gate in gates.values())
    return {
        'version':PROMOTION_VERSION,
        'status':'QUALIFIED' if qualified else 'BLOCKED',
        'candidate_server':candidate_server,
        'git_head':git_head,
        'gates':gates,
        'surface_certificate':dict(surface_audit),
        'promotion_allowed':qualified,
        'law':'QUALIFIED iff candidate_server=FieldServer AND SurfacePass AND CompositionPass AND CI witness success on exact head AND smoke witness success on exact head',
        'boundary':'QUALIFIED is a runtime promotion predicate, not semantic proof that every organ is correct',
    }


class PromotionLedger:
    def __init__(self,core):
        self.core=core;self.s=core.s
        with self.s.db:self.s.db.executescript(PROMOTION_SCHEMA)
        self.core.register('TOOL','RUNTIME','CERTIFY','DEFAULT_PROMOTION','AOR_PROMOTION_RECEIPT',{'candidate_server':'string','git_head':'sha','surface':'local','ci':'external witness','smoke':'external witness'},{'status':'QUALIFIED|BLOCKED','decision_digest':'sha256','run_id':'PROMRUN'},actor='GENESIS.AOR.3.5',status='CANONICAL')

    def evaluate(self,candidate_server:str,git_head:str,surface_audit:Mapping[str,Any],ci_witness:Mapping[str,Any],smoke_witness:Mapping[str,Any],actor:str='agent',persist:bool=True):
        inputs={'candidate_server':candidate_server,'git_head':git_head,'ci_witness':dict(ci_witness),'smoke_witness':dict(smoke_witness)}
        certificate=evaluate_promotion(candidate_server,git_head,surface_audit,ci_witness,smoke_witness)
        decision_payload={'version':PROMOTION_VERSION,'candidate_server':candidate_server,'git_head':git_head,'status':certificate['status'],'gates':certificate['gates']}
        decision_digest=digest(decision_payload,64)
        if not persist:return {**certificate,'persisted':False,'decision_digest':decision_digest}
        parent=self.s.head('global');parent_eid=parent['eid'] if parent else None
        event_payload={'operation':'PROMOTION_EVALUATE','candidate_server':candidate_server,'git_head':git_head,'status':certificate['status'],'decision_digest':decision_digest}
        eid=event_id('PROMOTION_EVALUATE',actor,parent_eid,event_payload);ed=digest(event_payload,32);run_id='PROMRUN.'+digest({'eid':eid,'decision':decision_digest},24)
        with self.s.db:self.s.db.execute('INSERT INTO promotion_runs VALUES(?,?,?,?,?,?,?,?,?)',(run_id,candidate_server,git_head,certificate['status'],json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(certificate,sort_keys=True,ensure_ascii=False),decision_digest,eid,time.time()))
        self.s.put_event(eid,'PROMOTION_EVALUATE',actor,parent_eid,event_payload,ed);self.s.set_head('global',None,None,eid,ed)
        return {**certificate,'persisted':True,'run_id':run_id,'decision_digest':decision_digest,'eid':eid}

    def get(self,run_id:str):
        row=self.s.one('SELECT * FROM promotion_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown promotion run')
        return {'run_id':row['run_id'],'candidate_server':row['candidate_server'],'git_head':row['git_head'],'status':row['status'],'input':json.loads(row['input_json']),'certificate':json.loads(row['certificate_json']),'decision_digest':row['decision_digest'],'eid':row['eid'],'created_at':row['created_at']}

    def recent(self,limit:int=20):
        limit=max(1,min(int(limit),200));return self.s.rows('SELECT run_id,candidate_server,git_head,status,decision_digest,eid,created_at FROM promotion_runs ORDER BY created_at DESC LIMIT ?',(limit,))

    def replay(self,run_id:str):
        stored=self.get(run_id);c=stored['certificate'];inp=stored['input']
        recomputed=evaluate_promotion(inp['candidate_server'],inp['git_head'],c['surface_certificate'],inp['ci_witness'],inp['smoke_witness'])
        payload={'version':PROMOTION_VERSION,'candidate_server':inp['candidate_server'],'git_head':inp['git_head'],'status':recomputed['status'],'gates':recomputed['gates']}
        recomputed_digest=digest(payload,64);match=recomputed_digest==stored['decision_digest']
        return {'run_id':run_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_decision_digest':stored['decision_digest'],'recomputed_decision_digest':recomputed_digest,'stored_status':stored['status'],'recomputed_status':recomputed['status'],'git_head':stored['git_head']}

    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM promotion_runs')['n'];qualified=self.s.one("SELECT COUNT(*) n FROM promotion_runs WHERE status='QUALIFIED'")['n']
        return {'promotion_runs':count,'promotion_qualified':qualified,'promotion_blocked':count-qualified}

from __future__ import annotations

import json
import time
from typing import Any,Mapping

from .identity import digest,event_id

PROMOTION_VERSION='ATHENA.PROMOTION.1'
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


def _witness(packet:Mapping[str,Any],expected_head:str,label:str):
    packet=dict(packet or {});observed=packet.get('observed') is True;ref=str(packet.get('ref') or '');head=str(packet.get('head_sha') or '');conclusion=str(packet.get('conclusion') or '');defects=[]
    if not observed:defects.append('not_observed')
    if not ref:defects.append('missing_ref')
    if head!=expected_head:defects.append('head_mismatch')
    if conclusion!='success':defects.append('conclusion_not_success')
    return {'kind':label,'status':'PASS' if not defects else 'FAIL','observed':observed,'ref':ref or None,'head_sha':head or None,'conclusion':conclusion or None,'defects':defects,
        'boundary':'external attestation supplied by caller; receipt binds the exact reference/head/conclusion but does not independently fetch or re-verify the external CI system'}


def evaluate_promotion(candidate_server,git_head,surface_audit,ci_witness,smoke_witness,local_git_status=None):
    candidate_server=str(candidate_server);git_head=str(git_head);surface=dict(surface_audit or {});composition=dict(surface.get('composition') or {});ci=_witness(ci_witness,git_head,'CI');smoke=_witness(smoke_witness,git_head,'SMOKE');local=dict(local_git_status or {})
    local_enabled=bool(local.get('enabled'));local_head=str(local.get('head') or '')
    local_gate={'status':'PASS','enabled':local_enabled,'observed_head':local_head or None,'boundary':'local Git observation is enforced when configured; otherwise exact-head qualification relies on the bound external CI/smoke attestations'}
    if local_enabled and local_head!=git_head:local_gate['status']='FAIL';local_gate['defects']=['local_head_mismatch']
    gates={
        'candidate_server':{'status':'PASS' if candidate_server=='Server' else 'FAIL','observed':candidate_server},
        'surface':{'status':str(surface.get('surface_status') or surface.get('status') or 'UNKNOWN')},
        'composition':{'status':str(composition.get('status') or 'UNKNOWN')},
        'local_git':local_gate,'ci':ci,'smoke':smoke,
    }
    qualified=all(g.get('status')=='PASS' for g in gates.values())
    return {'version':PROMOTION_VERSION,'status':'QUALIFIED' if qualified else 'BLOCKED','candidate_server':candidate_server,'git_head':git_head,'gates':gates,'surface_certificate':surface,'promotion_allowed':qualified,
        'law':'QUALIFIED iff candidate_server=Server AND SurfacePass AND CompositionPass AND local Git matches when configured AND CI+smoke attest success on the exact same head',
        'boundary':'promotion qualification certifies runtime integration/witness gates for this exact head; it is not semantic proof that every algorithmic claim is true'}


class PromotionLedger:
    def __init__(self,core):
        self.core=core;self.s=core.s
        with self.s.db:self.s.db.executescript(PROMOTION_SCHEMA)
        self.core.register('TOOL','RUNTIME','CERTIFY','DEFAULT_PROMOTION','UNIFIED_EXACT_HEAD_RECEIPT',{'server':'Server','surface':'local','composition':'local','ci':'external attestation','smoke':'external attestation'},{'status':'QUALIFIED|BLOCKED','run_id':'PROMRUN','decision_digest':'sha256'},actor='GENESIS.PROMOTION.1',status='CANONICAL')

    def evaluate(self,candidate_server,git_head,surface_audit,ci_witness,smoke_witness,local_git_status=None,actor='agent',persist=True):
        inputs={'candidate_server':str(candidate_server),'git_head':str(git_head),'surface_audit':dict(surface_audit),'ci_witness':dict(ci_witness),'smoke_witness':dict(smoke_witness),'local_git_status':dict(local_git_status or {})}
        cert=evaluate_promotion(**inputs);payload={'version':PROMOTION_VERSION,'candidate_server':cert['candidate_server'],'git_head':cert['git_head'],'status':cert['status'],'gates':cert['gates']};dd=digest(payload,64)
        if not persist:return {**cert,'persisted':False,'decision_digest':dd}
        parent=self.s.head('global');pe=parent['eid'] if parent else None;event_payload={'operation':'PROMOTION_EVALUATE','candidate_server':cert['candidate_server'],'git_head':cert['git_head'],'status':cert['status'],'decision_digest':dd};eid=event_id('PROMOTION_EVALUATE',actor,pe,event_payload);ed=digest(event_payload,32);run_id='PROMRUN.'+digest({'eid':eid,'decision':dd},24)
        with self.s.db:self.s.db.execute('INSERT INTO promotion_runs VALUES(?,?,?,?,?,?,?,?,?)',(run_id,cert['candidate_server'],cert['git_head'],cert['status'],json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(cert,sort_keys=True,ensure_ascii=False),dd,eid,time.time()))
        self.s.put_event(eid,'PROMOTION_EVALUATE',actor,pe,event_payload,ed);self.s.set_head('global',None,None,eid,ed)
        return {**cert,'persisted':True,'run_id':run_id,'decision_digest':dd,'eid':eid}

    def get(self,run_id):
        row=self.s.one('SELECT * FROM promotion_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown promotion run')
        return {'run_id':row['run_id'],'candidate_server':row['candidate_server'],'git_head':row['git_head'],'status':row['status'],'input':json.loads(row['input_json']),'certificate':json.loads(row['certificate_json']),'decision_digest':row['decision_digest'],'eid':row['eid'],'created_at':row['created_at']}

    def replay(self,run_id):
        stored=self.get(run_id);recomputed=evaluate_promotion(**stored['input']);payload={'version':PROMOTION_VERSION,'candidate_server':recomputed['candidate_server'],'git_head':recomputed['git_head'],'status':recomputed['status'],'gates':recomputed['gates']};now=digest(payload,64);match=now==stored['decision_digest']
        return {'run_id':run_id,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_decision_digest':stored['decision_digest'],'recomputed_decision_digest':now,'stored_status':stored['status'],'recomputed_status':recomputed['status'],'git_head':stored['git_head']}

    def recent(self,limit=20):
        limit=max(1,min(int(limit),200));return self.s.rows('SELECT run_id,candidate_server,git_head,status,decision_digest,eid,created_at FROM promotion_runs ORDER BY created_at DESC LIMIT ?',(limit,))

    def benchmark(self):
        count=self.s.one('SELECT COUNT(*) n FROM promotion_runs')['n'];qualified=self.s.one("SELECT COUNT(*) n FROM promotion_runs WHERE status='QUALIFIED'")['n'];return {'promotion_runs':count,'promotion_qualified':qualified,'promotion_blocked':count-qualified}

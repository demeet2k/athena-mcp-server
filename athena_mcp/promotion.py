from __future__ import annotations

import json
import time
from typing import Any,Mapping

from .identity import digest,event_id

PROMOTION_V1_VERSION='ATHENA.PROMOTION.1'
PROMOTION_VERSION='ATHENA.PROMOTION.2'
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


def _witness_v1(packet:Mapping[str,Any],expected_head:str,label:str):
    packet=dict(packet or {});observed=packet.get('observed') is True;ref=str(packet.get('ref') or '');head=str(packet.get('head_sha') or '');conclusion=str(packet.get('conclusion') or '');defects=[]
    if not observed:defects.append('not_observed')
    if not ref:defects.append('missing_ref')
    if head!=expected_head:defects.append('head_mismatch')
    if conclusion!='success':defects.append('conclusion_not_success')
    return {'kind':label,'status':'PASS' if not defects else 'FAIL','observed':observed,'ref':ref or None,'head_sha':head or None,'conclusion':conclusion or None,'defects':defects,
        'boundary':'external attestation supplied by caller; receipt binds the exact reference/head/conclusion but does not independently fetch or re-verify the external CI system'}


def evaluate_promotion_v1(candidate_server,git_head,surface_audit,ci_witness,smoke_witness,local_git_status=None):
    """Historical PROMOTION.1 predicate kept only so frozen V1 receipts remain replayable."""
    candidate_server=str(candidate_server);git_head=str(git_head);surface=dict(surface_audit or {});composition=dict(surface.get('composition') or {});ci=_witness_v1(ci_witness,git_head,'CI');smoke=_witness_v1(smoke_witness,git_head,'SMOKE');local=dict(local_git_status or {})
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
    return {'version':PROMOTION_V1_VERSION,'status':'QUALIFIED' if qualified else 'BLOCKED','candidate_server':candidate_server,'git_head':git_head,'gates':gates,'surface_certificate':surface,'promotion_allowed':qualified,
        'law':'QUALIFIED iff candidate_server=Server AND SurfacePass AND CompositionPass AND local Git matches when configured AND CI+smoke attest success on the exact same head',
        'boundary':'promotion qualification certifies runtime integration/witness gates for this exact head; it is not semantic proof that every algorithmic claim is true'}


def _caller_witness(packet:Mapping[str,Any],expected_head:str,label:str):
    packet=dict(packet or {});observed=packet.get('observed') is True;ref=str(packet.get('ref') or '');head=str(packet.get('head_sha') or '');conclusion=str(packet.get('conclusion') or '');defects=[]
    if not observed:defects.append('not_observed')
    if not ref:defects.append('missing_ref')
    if head!=expected_head:defects.append('head_mismatch')
    if conclusion!='success':defects.append('conclusion_not_success')
    return {
        'kind':label,'status':'PASS' if not defects else 'FAIL','observed':observed,'ref':ref or None,'head_sha':head or None,'conclusion':conclusion or None,'defects':defects,
        'trust_class':'CALLER_ATTESTED',
        'boundary':'caller-supplied packet proves only that the caller supplied a self-consistent exact-head success claim; this runtime did not independently query or verify the external CI provider',
    }


def _trusted_external_verification(packet:Mapping[str,Any] | None,expected_head:str,ci:Mapping[str,Any],smoke:Mapping[str,Any]):
    packet=dict(packet or {})
    if not packet:
        return {
            'status':'MISSING','trusted':False,'verifier':None,'verification_ref':None,'head_sha':None,'defects':['trusted_external_verification_missing'],
            'boundary':'QUALIFIED requires a host-internal trusted verifier receipt; this receipt is intentionally not accepted through the MCP promotion-evaluate input schema',
        }
    observed=packet.get('observed') is True;verifier=str(packet.get('verifier') or '');verification_ref=str(packet.get('verification_ref') or '');head=str(packet.get('head_sha') or '');ci_ref=str(packet.get('ci_ref') or '');smoke_ref=str(packet.get('smoke_ref') or '');defects=[]
    if not observed:defects.append('verification_not_observed')
    if not verifier:defects.append('missing_verifier')
    if not verification_ref:defects.append('missing_verification_ref')
    if head!=expected_head:defects.append('verification_head_mismatch')
    if ci_ref!=str(ci.get('ref') or ''):defects.append('verification_ci_ref_mismatch')
    if smoke_ref!=str(smoke.get('ref') or ''):defects.append('verification_smoke_ref_mismatch')
    return {
        'status':'PASS' if not defects else 'FAIL','trusted':not defects,'observed':observed,'verifier':verifier or None,'verification_ref':verification_ref or None,'head_sha':head or None,'ci_ref':ci_ref or None,'smoke_ref':smoke_ref or None,'defects':defects,
        'boundary':'host-internal verifier receipt binds the externally checked head and exact CI/smoke references; MCP callers cannot supply this field through athena_promotion_evaluate',
    }


def evaluate_promotion(candidate_server,git_head,surface_audit,ci_witness,smoke_witness,local_git_status=None,trusted_external_verification=None):
    candidate_server=str(candidate_server);git_head=str(git_head);surface=dict(surface_audit or {});composition=dict(surface.get('composition') or {});ci=_caller_witness(ci_witness,git_head,'CI');smoke=_caller_witness(smoke_witness,git_head,'SMOKE');local=dict(local_git_status or {})
    local_enabled=bool(local.get('enabled'));local_head=str(local.get('head') or '')
    local_gate={'status':'PASS','enabled':local_enabled,'observed_head':local_head or None,'boundary':'local Git observation is enforced when configured; otherwise exact-head readiness still requires caller-bound CI/smoke packets and separate trusted external verification for qualification'}
    if local_enabled and local_head!=git_head:local_gate['status']='FAIL';local_gate['defects']=['local_head_mismatch']
    base_gates={
        'candidate_server':{'status':'PASS' if candidate_server=='Server' else 'FAIL','observed':candidate_server},
        'surface':{'status':str(surface.get('surface_status') or surface.get('status') or 'UNKNOWN')},
        'composition':{'status':str(composition.get('status') or 'UNKNOWN')},
        'local_git':local_gate,'ci':ci,'smoke':smoke,
    }
    verification=_trusted_external_verification(trusted_external_verification,git_head,ci,smoke)
    gates={**base_gates,'external_verification':verification}
    base_ready=all(g.get('status')=='PASS' for g in base_gates.values())
    if not base_ready or verification['status']=='FAIL':status='BLOCKED'
    elif verification['status']=='PASS':status='QUALIFIED'
    else:status='ATTESTED_READY'
    qualified=status=='QUALIFIED'
    return {
        'version':PROMOTION_VERSION,'status':status,'candidate_server':candidate_server,'git_head':git_head,'gates':gates,'surface_certificate':surface,
        'promotion_allowed':qualified,'external_verification_required':status=='ATTESTED_READY','attestation_level':'EXTERNALLY_VERIFIED' if qualified else ('CALLER_BOUND' if status=='ATTESTED_READY' else 'BLOCKED'),
        'law':'ATTESTED_READY iff Server + SURFACE + COMPOSITION + configured local-Git exact-head gate + caller-bound CI/smoke packets all PASS; QUALIFIED additionally requires a host-internal trusted verifier receipt binding the same head and exact CI/smoke refs',
        'boundary':'caller-supplied CI/smoke packets can never mint PROMOTION.2 QUALIFIED through the MCP surface; qualification is reserved for a trusted host bridge, and neither status proves every algorithmic or semantic claim true',
    }


class PromotionLedger:
    def __init__(self,core):
        self.core=core;self.s=core.s
        with self.s.db:self.s.db.executescript(PROMOTION_SCHEMA)
        self.core.register('TOOL','RUNTIME','CERTIFY','DEFAULT_PROMOTION','UNIFIED_EXACT_HEAD_RECEIPT',{'server':'Server','surface':'local','composition':'local','ci':'caller attestation','smoke':'caller attestation','external_verification':'host-internal trusted bridge only'},{'status':'QUALIFIED|ATTESTED_READY|BLOCKED','run_id':'PROMRUN','decision_digest':'sha256'},actor='GENESIS.PROMOTION.2',status='CANONICAL')

    def evaluate(self,candidate_server,git_head,surface_audit,ci_witness,smoke_witness,local_git_status=None,actor='agent',persist=True,trusted_external_verification=None):
        inputs={'candidate_server':str(candidate_server),'git_head':str(git_head),'surface_audit':dict(surface_audit),'ci_witness':dict(ci_witness),'smoke_witness':dict(smoke_witness),'local_git_status':dict(local_git_status or {}),'trusted_external_verification':dict(trusted_external_verification or {})}
        cert=evaluate_promotion(**inputs);payload={'version':PROMOTION_VERSION,'candidate_server':cert['candidate_server'],'git_head':cert['git_head'],'status':cert['status'],'gates':cert['gates']};dd=digest(payload,64)
        if not persist:return {**cert,'persisted':False,'decision_digest':dd}
        parent=self.s.head('global');pe=parent['eid'] if parent else None;event_payload={'operation':'PROMOTION_EVALUATE','candidate_server':cert['candidate_server'],'git_head':cert['git_head'],'status':cert['status'],'decision_digest':dd,'promotion_version':PROMOTION_VERSION};eid=event_id('PROMOTION_EVALUATE',actor,pe,event_payload);ed=digest(event_payload,32);run_id='PROMRUN.'+digest({'eid':eid,'decision':dd},24)
        with self.s.db:self.s.db.execute('INSERT INTO promotion_runs VALUES(?,?,?,?,?,?,?,?,?)',(run_id,cert['candidate_server'],cert['git_head'],cert['status'],json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(cert,sort_keys=True,ensure_ascii=False),dd,eid,time.time()))
        self.s.put_event(eid,'PROMOTION_EVALUATE',actor,pe,event_payload,ed);self.s.set_head('global',None,None,eid,ed)
        return {**cert,'persisted':True,'run_id':run_id,'decision_digest':dd,'eid':eid}

    def get(self,run_id):
        row=self.s.one('SELECT * FROM promotion_runs WHERE run_id=?',(run_id,))
        if not row:raise KeyError('unknown promotion run')
        return {'run_id':row['run_id'],'candidate_server':row['candidate_server'],'git_head':row['git_head'],'status':row['status'],'input':json.loads(row['input_json']),'certificate':json.loads(row['certificate_json']),'decision_digest':row['decision_digest'],'eid':row['eid'],'created_at':row['created_at']}

    def replay(self,run_id):
        stored=self.get(run_id);version=str(stored['certificate'].get('version') or PROMOTION_V1_VERSION);inputs=dict(stored['input'])
        if version==PROMOTION_V1_VERSION:
            inputs.pop('trusted_external_verification',None);recomputed=evaluate_promotion_v1(**inputs)
        elif version==PROMOTION_VERSION:
            recomputed=evaluate_promotion(**inputs)
        else:
            return {'run_id':run_id,'version':version,'status':'REPLAY_UNSUPPORTED_VERSION','match':False,'stored_decision_digest':stored['decision_digest'],'recomputed_decision_digest':None,'stored_status':stored['status'],'recomputed_status':None,'git_head':stored['git_head']}
        payload={'version':recomputed['version'],'candidate_server':recomputed['candidate_server'],'git_head':recomputed['git_head'],'status':recomputed['status'],'gates':recomputed['gates']};now=digest(payload,64);match=now==stored['decision_digest']
        return {'run_id':run_id,'version':version,'status':'REPLAY_MATCH' if match else 'REPLAY_DIVERGED','match':match,'stored_decision_digest':stored['decision_digest'],'recomputed_decision_digest':now,'stored_status':stored['status'],'recomputed_status':recomputed['status'],'git_head':stored['git_head']}

    def recent(self,limit=20):
        limit=max(1,min(int(limit),200));return self.s.rows('SELECT run_id,candidate_server,git_head,status,decision_digest,eid,created_at FROM promotion_runs ORDER BY created_at DESC LIMIT ?',(limit,))

    def benchmark(self):
        rows=self.s.rows('SELECT status,certificate_json FROM promotion_runs');v1q=0;v2q=0;ready=0;blocked=0;unknown=0
        for row in rows:
            try:version=str(json.loads(row['certificate_json']).get('version') or PROMOTION_V1_VERSION)
            except Exception:version='UNKNOWN'
            status=str(row['status'])
            if version==PROMOTION_V1_VERSION and status=='QUALIFIED':v1q+=1
            elif version==PROMOTION_VERSION and status=='QUALIFIED':v2q+=1
            elif version==PROMOTION_VERSION and status=='ATTESTED_READY':ready+=1
            elif status=='BLOCKED':blocked+=1
            else:unknown+=1
        return {'promotion_runs':len(rows),'promotion_qualified':v2q,'promotion_v2_qualified':v2q,'promotion_attested_ready':ready,'promotion_v1_qualified_historical':v1q,'promotion_blocked':blocked,'promotion_unknown':unknown}

from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, Mapping, Optional

from .identity import digest, event_id

AUTHORITY_ORDER={"?":0,"+":1,"!":2,"#":3}
AUTHORITY_SCHEMA='''
CREATE TABLE IF NOT EXISTS authority_claims(
 claim_id TEXT PRIMARY KEY,
 source_ref TEXT NOT NULL,
 y TEXT NOT NULL,
 status TEXT NOT NULL,
 evidence_json TEXT NOT NULL,
 test_json TEXT NOT NULL,
 canonical_ref TEXT,
 last_eid TEXT NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS authority_events(
 authority_event_id TEXT PRIMARY KEY,
 claim_id TEXT NOT NULL,
 operation TEXT NOT NULL,
 from_y TEXT,
 to_y TEXT,
 payload_json TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_authority_status ON authority_claims(y,status,updated_at);
CREATE INDEX IF NOT EXISTS idx_authority_events_claim ON authority_events(claim_id,created_at);
'''


def _verified_ref(value: Mapping[str,Any], label: str) -> str:
    value=dict(value or {})
    if value.get("verified") is not True: raise ValueError(f"{label} requires verified=true")
    ref=str(value.get("ref") or "").strip()
    if not ref: raise ValueError(f"{label} requires ref")
    return ref


def _evidence(items: Optional[Iterable[Mapping[str,Any]]]) -> list[Dict[str,Any]]:
    result=[]
    for item in items or []:
        item=dict(item); kind=str(item.get("kind") or "support"); ref=_verified_ref(item,"evidence")
        if kind not in {"support","derive","reproduce"}: raise ValueError(f"unsupported evidence kind {kind}")
        result.append({**item,"kind":kind,"ref":ref,"verified":True})
    return result


def _verified_test(test: Mapping[str,Any]) -> Dict[str,Any]:
    test=dict(test or {}); missing=[name for name in ("procedure","observation","result","witness") if not test.get(name)]
    if missing: raise ValueError(f"verified execution test missing {missing}")
    witness=test.get("witness")
    if isinstance(witness,Mapping): _verified_ref(witness,"test witness")
    else:
        if not str(witness).strip(): raise ValueError("test witness required")
    return test


def _canonical_authority(value: Mapping[str,Any]) -> str:
    value=dict(value or {})
    if value.get("authorized") is not True: raise ValueError("canonicalization requires authorized=true")
    ref=str(value.get("ref") or "").strip()
    if not ref: raise ValueError("canonicalization requires authority ref")
    return ref


class AuthorityLedger:
    def __init__(self,core):
        self.core=core; self.s=core.s
        with self.s.db:self.s.db.executescript(AUTHORITY_SCHEMA)
        self.core.register("TOOL","AUTHORITY","PROMOTE","CLAIM_STATE","Y_TYPED_WITNESS_GATES",{"claim":"stable","target":"?+!#","witnesses":"typed"},{"y":"?+!#","status":"typed","history":"events"},actor="GENESIS.AOR.3",status="CANONICAL")

    def _event(self,claim_id:str,operation:str,from_y:Optional[str],to_y:Optional[str],payload:Mapping[str,Any],actor:str):
        parent=self.s.head("global"); pe=parent["eid"] if parent else None; ep={"claim_id":claim_id,"operation":operation,"from_y":from_y,"to_y":to_y,**dict(payload)}
        eid=event_id(f"AUTHORITY_{operation}",actor,pe,ep); ed=digest(ep,32); aeid="AUTH."+digest({"eid":eid,"claim":claim_id,"op":operation},24)
        self.s.put_event(eid,f"AUTHORITY_{operation}",actor,pe,ep,ed); self.s.set_head("global",None,None,eid,ed)
        with self.s.db:self.s.db.execute("INSERT INTO authority_events VALUES(?,?,?,?,?,?,?,?)",(aeid,claim_id,operation,from_y,to_y,json.dumps(ep,sort_keys=True),eid,time.time()))
        return aeid,eid

    def register(self,claim_id:str,source_ref:str,actor:str="agent"):
        claim_id=str(claim_id).strip(); source_ref=str(source_ref).strip()
        if not claim_id or not source_ref: raise ValueError("claim_id and source_ref are required")
        existing=self.s.one("SELECT * FROM authority_claims WHERE claim_id=?",(claim_id,))
        if existing:return {"action":"REUSE","claim":self._decode(existing)}
        aeid,eid=self._event(claim_id,"REGISTER",None,"?",{"source_ref":source_ref},actor)
        with self.s.db:self.s.db.execute("INSERT INTO authority_claims VALUES(?,?,?,?,?,?,?,?,?)",(claim_id,source_ref,"?","ACTIVE","[]","{}",None,eid,time.time()))
        return {"action":"CREATED","authority_event_id":aeid,"claim":self.state(claim_id)}

    def state(self,claim_id:str):
        row=self.s.one("SELECT * FROM authority_claims WHERE claim_id=?",(claim_id,))
        return self._decode(row) if row else None

    def _decode(self,row):
        if not row:return None
        out=dict(row); out["evidence"]=json.loads(out.pop("evidence_json")); out["test"]=json.loads(out.pop("test_json")); return out

    def promote(self,claim_id:str,target_y:str,evidence=None,test=None,canonical_authority=None,actor:str="agent"):
        target_y=str(target_y); row=self.s.one("SELECT * FROM authority_claims WHERE claim_id=?",(claim_id,))
        if not row: raise KeyError("unknown claim")
        current=row["y"]
        if target_y not in AUTHORITY_ORDER: raise ValueError("target_y must be one of ?,+,!,#")
        if AUTHORITY_ORDER[target_y] != AUTHORITY_ORDER[current]+1: raise ValueError(f"authority promotion must advance exactly one step: {current}->{target_y} invalid")
        prior_evidence=json.loads(row["evidence_json"]); prior_test=json.loads(row["test_json"]); canonical_ref=row["canonical_ref"]
        payload={}
        if current=="?" and target_y=="+":
            new=_evidence(evidence)
            if not new: raise ValueError("?->+ requires at least one verified support/derive/reproduce evidence item")
            prior_evidence.extend(new); payload["evidence_refs"]=[x["ref"] for x in new]
        elif current=="+" and target_y=="!":
            prior_test=_verified_test(test or {}); payload["test_witness"]=prior_test.get("witness")
        elif current=="!" and target_y=="#":
            canonical_ref=_canonical_authority(canonical_authority or {}); payload["canonical_ref"]=canonical_ref
        aeid,eid=self._event(claim_id,"PROMOTE",current,target_y,payload,actor)
        with self.s.db:self.s.db.execute("UPDATE authority_claims SET y=?,status='ACTIVE',evidence_json=?,test_json=?,canonical_ref=?,last_eid=?,updated_at=? WHERE claim_id=?",(target_y,json.dumps(prior_evidence,sort_keys=True),json.dumps(prior_test,sort_keys=True),canonical_ref,eid,time.time(),claim_id))
        return {"authority_event_id":aeid,"transition":f"{current}->{target_y}","claim":self.state(claim_id)}

    def challenge(self,claim_id:str,witness:Mapping[str,Any],reason:str,actor:str="agent"):
        row=self.s.one("SELECT * FROM authority_claims WHERE claim_id=?",(claim_id,))
        if not row: raise KeyError("unknown claim")
        ref=_verified_ref(witness,"challenge witness"); reason=str(reason or "").strip()
        if not reason: raise ValueError("challenge reason required")
        current=row["y"]
        if current=="#": new_y="#"; status="CANONICAL_CHALLENGED"
        else:new_y="?"; status="CHALLENGED"
        aeid,eid=self._event(claim_id,"CHALLENGE",current,new_y,{"witness_ref":ref,"reason":reason,"status":status},actor)
        with self.s.db:self.s.db.execute("UPDATE authority_claims SET y=?,status=?,last_eid=?,updated_at=? WHERE claim_id=?",(new_y,status,eid,time.time(),claim_id))
        return {"authority_event_id":aeid,"claim":self.state(claim_id),"witness_ref":ref,"reason":reason}

    def resolve_canonical_challenge(self,claim_id:str,decision:str,authority:Mapping[str,Any],actor:str="agent"):
        row=self.s.one("SELECT * FROM authority_claims WHERE claim_id=?",(claim_id,))
        if not row: raise KeyError("unknown claim")
        if row["status"]!="CANONICAL_CHALLENGED": raise ValueError("claim is not a challenged canonical")
        ref=_canonical_authority(authority); decision=str(decision).upper()
        if decision not in {"UPHOLD","DEMOTE"}: raise ValueError("decision must be UPHOLD or DEMOTE")
        new_y="#" if decision=="UPHOLD" else "!"; status="ACTIVE"
        aeid,eid=self._event(claim_id,"RESOLVE_CANONICAL_CHALLENGE","#",new_y,{"decision":decision,"authority_ref":ref},actor)
        with self.s.db:self.s.db.execute("UPDATE authority_claims SET y=?,status=?,canonical_ref=?,last_eid=?,updated_at=? WHERE claim_id=?",(new_y,status,ref,eid,time.time(),claim_id))
        return {"authority_event_id":aeid,"decision":decision,"claim":self.state(claim_id)}

    def enrich_candidates(self,candidates:Iterable[Mapping[str,Any]]):
        enriched=[]
        for candidate in candidates:
            item=dict(candidate); claim_id=str(item.get("claim_id") or "").strip()
            if claim_id:
                state=self.state(claim_id)
                if state:item["authority_state"]={"claim_id":claim_id,"y":state["y"],"status":state["status"],"last_eid":state["last_eid"]}
            enriched.append(item)
        return enriched

    def list(self,y:Optional[str]=None,status:Optional[str]=None,limit:int=100):
        limit=max(1,min(int(limit),500)); clauses=[];args=[]
        if y is not None:
            if y not in AUTHORITY_ORDER: raise ValueError("invalid y")
            clauses.append("y=?");args.append(y)
        if status is not None:clauses.append("status=?");args.append(str(status))
        where=(" WHERE "+" AND ".join(clauses)) if clauses else "";args.append(limit)
        return [self._decode(row) for row in self.s.rows(f"SELECT * FROM authority_claims{where} ORDER BY updated_at DESC LIMIT ?",tuple(args))]

    def benchmark(self):
        q=lambda y:self.s.one("SELECT COUNT(*) n FROM authority_claims WHERE y=?",(y,))["n"]
        return {"authority_claims":self.s.one("SELECT COUNT(*) n FROM authority_claims")["n"],"authority_events":self.s.one("SELECT COUNT(*) n FROM authority_events")["n"],"authority_unknown":q("?"),"authority_supported":q("+"),"authority_executed":q("!"),"authority_canonical":q("#")}

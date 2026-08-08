from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, Mapping, Optional

from .identity import digest, event_id
from .orchestration_score import finite_number

BRANCH_SCHEMA = '''
CREATE TABLE IF NOT EXISTS orchestration_branches(
 branch_id TEXT NOT NULL,
 basis_id TEXT NOT NULL,
 status TEXT NOT NULL,
 ewma_reward REAL,
 observations INTEGER NOT NULL,
 last_reward REAL,
 last_witness_ref TEXT,
 last_eid TEXT,
 policy_json TEXT NOT NULL,
 metadata_json TEXT NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(branch_id,basis_id)
);
CREATE TABLE IF NOT EXISTS branch_observations(
 observation_id TEXT PRIMARY KEY,
 branch_id TEXT NOT NULL,
 basis_id TEXT NOT NULL,
 reward REAL,
 witness_json TEXT NOT NULL,
 triggers_json TEXT NOT NULL,
 transition TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_branch_status ON orchestration_branches(status,updated_at);
CREATE INDEX IF NOT EXISTS idx_branch_obs_branch ON branch_observations(branch_id,basis_id,created_at);
'''

DEFAULT_POLICY = {
    "alpha": 0.30,
    "min_observations": 3,
    "hibernate_below": 0.0,
    "resurrect_above": 0.5,
}
ALLOWED_STATUS = {"ACTIVE", "HIBERNATED", "REVIEW"}
ALLOWED_TRIGGERS = {"new_evidence", "new_gap", "bridge_demand"}


def _policy(value: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    p = {**DEFAULT_POLICY, **dict(value or {})}
    alpha = finite_number(p.get("alpha")); hb = finite_number(p.get("hibernate_below")); ra = finite_number(p.get("resurrect_above"))
    try: minimum = int(p.get("min_observations"))
    except (TypeError, ValueError): minimum = 0
    if alpha is None or not (0 < alpha <= 1): raise ValueError("branch policy alpha must be in (0,1]")
    if hb is None or ra is None: raise ValueError("branch thresholds must be finite numbers")
    if minimum < 1: raise ValueError("min_observations must be >=1")
    if ra <= hb: raise ValueError("resurrect_above must be greater than hibernate_below")
    return {"alpha":alpha,"min_observations":minimum,"hibernate_below":hb,"resurrect_above":ra}


def _verified_witness(witness: Mapping[str, Any]) -> str:
    witness = dict(witness or {})
    if witness.get("verified") is not True: raise ValueError("branch observation requires witness.verified=true")
    ref = str(witness.get("ref") or "").strip()
    if not ref: raise ValueError("branch observation requires witness.ref")
    return ref


def _verified_triggers(triggers: Optional[Iterable[Mapping[str, Any]]]) -> list[Dict[str, str]]:
    result=[]
    for item in triggers or []:
        item=dict(item); kind=str(item.get("type") or ""); ref=str(item.get("ref") or "").strip()
        if kind not in ALLOWED_TRIGGERS: raise ValueError(f"unsupported branch trigger {kind}")
        if not ref: raise ValueError("branch trigger requires ref")
        result.append({"type":kind,"ref":ref})
    return result


class BranchLedger:
    def __init__(self, core):
        self.core=core; self.s=core.s
        with self.s.db: self.s.db.executescript(BRANCH_SCHEMA)
        self.core.register(
            "TOOL","DEVELOPMENT","EVOLVE","BRANCH_LIFECYCLE","WITNESSED_EWMA_HIBERNATION",
            {"branch_id":"stable","basis_id":"metric basis","reward":"calibrated","witness":"verified","triggers":"verified refs"},
            {"status":"ACTIVE|HIBERNATED|REVIEW","ewma_reward":"number","transition":"typed"},
            actor="GENESIS.AOR.3",status="CANONICAL"
        )

    def state(self, branch_id: str, basis_id: Optional[str]=None):
        if basis_id is not None:
            row=self.s.one("SELECT * FROM orchestration_branches WHERE branch_id=? AND basis_id=?",(branch_id,basis_id))
            return self._decode(row) if row else None
        return [self._decode(row) for row in self.s.rows("SELECT * FROM orchestration_branches WHERE branch_id=? ORDER BY updated_at DESC",(branch_id,))]

    def list(self,status:Optional[str]=None,limit:int=100):
        limit=max(1,min(int(limit),500))
        if status is not None:
            status=status.upper()
            if status not in ALLOWED_STATUS: raise ValueError("invalid branch status")
            rows=self.s.rows("SELECT * FROM orchestration_branches WHERE status=? ORDER BY updated_at DESC LIMIT ?",(status,limit))
        else:
            rows=self.s.rows("SELECT * FROM orchestration_branches ORDER BY updated_at DESC LIMIT ?",(limit,))
        return [self._decode(row) for row in rows]

    def _decode(self,row):
        if not row: return None
        out=dict(row); out["policy"]=json.loads(out.pop("policy_json")); out["metadata"]=json.loads(out.pop("metadata_json")); return out

    def observe(self,branch_id:str,basis_id:str,reward:Any,witness:Mapping[str,Any],policy:Optional[Mapping[str,Any]]=None,triggers:Optional[Iterable[Mapping[str,Any]]]=None,metadata:Optional[Mapping[str,Any]]=None,actor:str="agent"):
        branch_id=str(branch_id).strip(); basis_id=str(basis_id).strip()
        if not branch_id or not basis_id: raise ValueError("branch_id and basis_id are required")
        reward_value=finite_number(reward)
        if reward_value is None: raise ValueError("branch reward must be a finite calibrated number")
        witness_ref=_verified_witness(witness); trigger_rows=_verified_triggers(triggers); p=_policy(policy)
        previous=self.s.one("SELECT * FROM orchestration_branches WHERE branch_id=? AND basis_id=?",(branch_id,basis_id))
        prior_status=previous["status"] if previous else "ACTIVE"; prior_ewma=previous["ewma_reward"] if previous else None; prior_n=int(previous["observations"]) if previous else 0
        ewma=reward_value if prior_ewma is None else p["alpha"]*reward_value+(1-p["alpha"])*float(prior_ewma)
        observations=prior_n+1; status=prior_status; transition="OBSERVE"

        if prior_status=="HIBERNATED" and trigger_rows:
            status="REVIEW"; transition="HIBERNATED->REVIEW"
        if status in {"HIBERNATED","REVIEW"} and observations>=p["min_observations"] and ewma>=p["resurrect_above"]:
            status="ACTIVE"; transition=f"{prior_status}->ACTIVE"
        elif status=="ACTIVE" and observations>=p["min_observations"] and ewma<=p["hibernate_below"]:
            status="HIBERNATED"; transition="ACTIVE->HIBERNATED"

        parent=self.s.head("global"); pe=parent["eid"] if parent else None
        event_payload={"operation":"BRANCH_OBSERVE","branch_id":branch_id,"basis_id":basis_id,"reward":reward_value,"ewma_reward":ewma,"observations":observations,"prior_status":prior_status,"status":status,"transition":transition,"witness_ref":witness_ref,"triggers":trigger_rows,"policy":p}
        eid=event_id("BRANCH_OBSERVE",actor,pe,event_payload); ed=digest(event_payload,32); observation_id="BROBS."+digest({"eid":eid,"branch":branch_id,"basis":basis_id},24)
        merged_metadata={**(json.loads(previous["metadata_json"]) if previous else {}),**dict(metadata or {})}
        with self.s.db:
            self.s.db.execute("INSERT OR REPLACE INTO orchestration_branches VALUES(?,?,?,?,?,?,?,?,?,?,?)",(branch_id,basis_id,status,ewma,observations,reward_value,witness_ref,eid,json.dumps(p,sort_keys=True),json.dumps(merged_metadata,sort_keys=True),time.time()))
            self.s.db.execute("INSERT INTO branch_observations VALUES(?,?,?,?,?,?,?,?,?)",(observation_id,branch_id,basis_id,reward_value,json.dumps(dict(witness),sort_keys=True),json.dumps(trigger_rows,sort_keys=True),transition,eid,time.time()))
        self.s.put_event(eid,"BRANCH_OBSERVE",actor,pe,event_payload,ed); self.s.set_head("global",None,None,eid,ed)
        return {"observation_id":observation_id,"eid":eid,"branch_id":branch_id,"basis_id":basis_id,"prior_status":prior_status,"status":status,"transition":transition,"reward":reward_value,"ewma_reward":ewma,"observations":observations,"policy":p,"witness_ref":witness_ref,"triggers":trigger_rows}

    def review(self,branch_id:str,basis_id:str,trigger:Mapping[str,Any],actor:str="agent"):
        trigger_rows=_verified_triggers([trigger]); row=self.s.one("SELECT * FROM orchestration_branches WHERE branch_id=? AND basis_id=?",(branch_id,basis_id))
        if not row: raise KeyError("unknown branch")
        prior=row["status"]
        if prior!="HIBERNATED": return {"branch_id":branch_id,"basis_id":basis_id,"status":prior,"transition":"NOOP","reason":"branch is not hibernated"}
        parent=self.s.head("global"); pe=parent["eid"] if parent else None
        payload={"operation":"BRANCH_REVIEW","branch_id":branch_id,"basis_id":basis_id,"prior_status":prior,"status":"REVIEW","trigger":trigger_rows[0]}
        eid=event_id("BRANCH_REVIEW",actor,pe,payload); ed=digest(payload,32)
        with self.s.db: self.s.db.execute("UPDATE orchestration_branches SET status='REVIEW',last_eid=?,updated_at=? WHERE branch_id=? AND basis_id=?",(eid,time.time(),branch_id,basis_id))
        self.s.put_event(eid,"BRANCH_REVIEW",actor,pe,payload,ed); self.s.set_head("global",None,None,eid,ed)
        return {"branch_id":branch_id,"basis_id":basis_id,"status":"REVIEW","transition":"HIBERNATED->REVIEW","eid":eid,"trigger":trigger_rows[0]}

    def enrich_candidates(self,candidates:Iterable[Mapping[str,Any]],basis_id:str):
        enriched=[]
        for candidate in candidates:
            item=dict(candidate); branch_id=str(item.get("branch_id") or "").strip()
            if branch_id:
                state=self.s.one("SELECT * FROM orchestration_branches WHERE branch_id=? AND basis_id=?",(branch_id,basis_id))
                if state:
                    item["lifecycle"]={"branch_id":branch_id,"basis_id":basis_id,"status":state["status"],"ewma_reward":state["ewma_reward"],"observations":state["observations"],"last_eid":state["last_eid"]}
            enriched.append(item)
        return enriched

    def benchmark(self):
        q=lambda status:self.s.one("SELECT COUNT(*) n FROM orchestration_branches WHERE status=?",(status,))["n"]
        return {"branches":self.s.one("SELECT COUNT(*) n FROM orchestration_branches")["n"],"branch_observations":self.s.one("SELECT COUNT(*) n FROM branch_observations")["n"],"branches_active":q("ACTIVE"),"branches_hibernated":q("HIBERNATED"),"branches_review":q("REVIEW")}

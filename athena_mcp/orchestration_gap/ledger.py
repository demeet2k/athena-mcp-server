from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Iterable, Mapping

from ..identity import digest, event_id
from .compiler import compile_gap

GAP_SCHEMA='''
CREATE TABLE IF NOT EXISTS gap_runs(
 run_id TEXT PRIMARY KEY,
 task_ref TEXT NOT NULL,
 actor TEXT NOT NULL,
 input_json TEXT NOT NULL,
 output_json TEXT NOT NULL,
 decision_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_gap_runs_created ON gap_runs(created_at);
'''


def _carrier(output):
    return {
        "closure_kind":output.get("closure_kind"),
        "policy":output.get("policy"),
        "closure_nodes":output.get("closure_nodes"),
        "admissible_edge_ids":output.get("admissible_edge_ids"),
        "rejected_edges":output.get("rejected_edges"),
        "covered_target_ids":output.get("covered_target_ids"),
        "gap_target_ids":output.get("gap_target_ids"),
        "ranked_gap_ids":output.get("ranked_gap_ids"),
        "grow":(output.get("grow") or {}).get("id"),
        "measurement_plan":output.get("measurement_plan"),
    }


def decision_digest(output):
    raw=json.dumps(_carrier(output),sort_keys=True,ensure_ascii=False,separators=(",",":"));return hashlib.sha256(raw.encode()).hexdigest()


class GapLedger:
    def __init__(self,core):
        self.core=core;self.s=core.s
        with self.s.db:self.s.db.executescript(GAP_SCHEMA)
        self.core.register("TOOL","GRAPH","COMPILE","TARGET_RESIDUAL","WITNESSED_REACHABILITY_GAP",{"sources":"S/H/B/C node groups","edges":"typed+witnessed","targets":"explicit nodes"},{"closure":"paths","gap":"residuals","grow":"ranked"},actor="GENESIS.GAP.1",status="CANONICAL")

    def compile(self,task_ref:str,sources:Mapping[str,Iterable[str]],edges:Iterable[Mapping[str,Any]],targets:Iterable[Mapping[str,Any]],policy:Mapping[str,Any],actor:str="agent",persist:bool=True):
        task_ref=str(task_ref or "").strip()
        if not task_ref:raise ValueError("task_ref required")
        inputs={"sources":{str(k):list(v or []) for k,v in dict(sources or {}).items()},"edges":[dict(x) for x in edges or []],"targets":[dict(x) for x in targets or []],"policy":dict(policy or {})}
        output=compile_gap(**inputs);output["decision_digest"]=decision_digest(output)
        if not persist:return {**output,"persisted":False}
        parent=self.s.head("global");pe=parent["eid"] if parent else None
        ep={"operation":"GAP_COMPILE","task_ref":task_ref,"actor":actor,"closure_count":len(output["closure_nodes"]),"gap_ids":output["gap_target_ids"],"grow":(output.get("grow") or {}).get("id"),"decision_digest":output["decision_digest"]};eid=event_id("GAP_COMPILE",actor,pe,ep);ed=digest(ep,32);run_id="GAPRUN."+digest({"eid":eid,"decision":output["decision_digest"]},24)
        with self.s.db:self.s.db.execute("INSERT INTO gap_runs VALUES(?,?,?,?,?,?,?,?)",(run_id,task_ref,actor,json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(output,sort_keys=True,ensure_ascii=False),output["decision_digest"],eid,time.time()))
        self.s.put_event(eid,"GAP_COMPILE",actor,pe,ep,ed);self.s.set_head("global",None,None,eid,ed)
        return {**output,"persisted":True,"run_id":run_id,"eid":eid}

    def get(self,run_id:str):
        row=self.s.one("SELECT * FROM gap_runs WHERE run_id=?",(run_id,))
        if not row:raise KeyError("unknown gap run")
        return {"run_id":row["run_id"],"task_ref":row["task_ref"],"actor":row["actor"],"input":json.loads(row["input_json"]),"output":json.loads(row["output_json"]),"decision_digest":row["decision_digest"],"eid":row["eid"],"created_at":row["created_at"]}

    def replay(self,run_id:str):
        stored=self.get(run_id);recomputed=compile_gap(**stored["input"]);digest_now=decision_digest(recomputed);match=digest_now==stored["decision_digest"]
        return {"run_id":run_id,"status":"REPLAY_MATCH" if match else "REPLAY_DIVERGED","match":match,"stored_decision_digest":stored["decision_digest"],"recomputed_decision_digest":digest_now,"stored_gap":stored["output"].get("gap_target_ids"),"recomputed_gap":recomputed.get("gap_target_ids"),"stored_grow":(stored["output"].get("grow") or {}).get("id"),"recomputed_grow":(recomputed.get("grow") or {}).get("id"),"stored_closure_nodes":stored["output"].get("closure_nodes"),"recomputed_closure_nodes":recomputed.get("closure_nodes")}

    def recent(self,limit:int=50):
        limit=max(1,min(int(limit),500));return self.s.rows("SELECT run_id,task_ref,actor,decision_digest,eid,created_at FROM gap_runs ORDER BY created_at DESC LIMIT ?",(limit,))

    def benchmark(self):
        count=self.s.one("SELECT COUNT(*) n FROM gap_runs")["n"];checked=matches=0
        for row in self.s.rows("SELECT run_id FROM gap_runs ORDER BY created_at DESC LIMIT 20"):
            checked+=1
            if self.replay(row["run_id"])["match"]:matches+=1
        return {"gap_runs":count,"gap_replay_sample":checked,"gap_replay_matches":matches,"gap_replay_match_rate":(matches/checked) if checked else None}

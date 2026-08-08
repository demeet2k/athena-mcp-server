from __future__ import annotations

import json
import time
from typing import Any, Iterable, Mapping, Optional

from ..identity import digest, event_id
from .specs import TRANSFORM_ORDER, TRANSFORM_SPECS, transform_manifest

EXTRACTION_SCHEMA='''
CREATE TABLE IF NOT EXISTS extraction_runs(
 run_id TEXT PRIMARY KEY,
 seed_ref TEXT NOT NULL,
 seed_json TEXT NOT NULL,
 max_depth INTEGER NOT NULL,
 max_tasks_per_generation INTEGER NOT NULL,
 actor TEXT NOT NULL,
 start_eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS extraction_tasks(
 task_id TEXT PRIMARY KEY,
 run_id TEXT NOT NULL,
 parent_task_id TEXT,
 seed_ref TEXT NOT NULL,
 seed_json TEXT NOT NULL,
 transform TEXT NOT NULL,
 depth INTEGER NOT NULL,
 ordinal INTEGER NOT NULL,
 status TEXT NOT NULL,
 result_refs_json TEXT NOT NULL,
 last_eid TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS extraction_results(
 result_id TEXT PRIMARY KEY,
 task_id TEXT NOT NULL,
 run_id TEXT NOT NULL,
 output_index INTEGER NOT NULL,
 payload_json TEXT NOT NULL,
 witness_json TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_extract_tasks_run ON extraction_tasks(run_id,depth,status,ordinal);
CREATE INDEX IF NOT EXISTS idx_extract_results_task ON extraction_results(task_id,output_index);
'''


def _verified_witness(witness: Mapping[str,Any]) -> str:
    witness=dict(witness or {})
    if witness.get("verified") is not True:raise ValueError("extraction completion/failure requires witness.verified=true")
    ref=str(witness.get("ref") or "").strip()
    if not ref:raise ValueError("extraction witness requires ref")
    return ref


class ExtractionLedger:
    def __init__(self,core):
        self.core=core;self.s=core.s
        with self.s.db:self.s.db.executescript(EXTRACTION_SCHEMA)
        self.core.register("TOOL","DEVELOPMENT","PLAN","SEED_TRANSFORM_FRONTIER","AOR3_WITNESSED_EXTRACTION",{"seed":"payload","transforms":"typed bank","depth":"bounded"},{"tasks":"planned","results":"witnessed","recursive_frontier":"bounded"},actor="GENESIS.AOR.3",status="CANONICAL")

    def _event(self,operation,payload,actor):
        parent=self.s.head("global");pe=parent["eid"] if parent else None
        eid=event_id(f"EXTRACTION_{operation}",actor,pe,payload);ed=digest(payload,32)
        self.s.put_event(eid,f"EXTRACTION_{operation}",actor,pe,payload,ed);self.s.set_head("global",None,None,eid,ed)
        return eid

    def plan(self,seed_ref:str,seed:Any,transforms:Optional[Iterable[str]]=None,max_depth:int=1,max_tasks_per_generation:int=16,actor:str="agent"):
        seed_ref=str(seed_ref).strip()
        if not seed_ref:raise ValueError("seed_ref required")
        try:max_depth=int(max_depth);max_tasks_per_generation=int(max_tasks_per_generation)
        except (TypeError,ValueError):raise ValueError("depth/task limits must be integers")
        if max_depth<0:raise ValueError("max_depth must be >=0")
        if max_tasks_per_generation<1:raise ValueError("max_tasks_per_generation must be >=1")
        chosen=list(transforms or TRANSFORM_ORDER);unknown=[name for name in chosen if name not in TRANSFORM_SPECS]
        if unknown:raise ValueError(f"unknown transforms {unknown}")
        chosen=list(dict.fromkeys(chosen))[:max_tasks_per_generation]
        payload={"operation":"PLAN","seed_ref":seed_ref,"transforms":chosen,"max_depth":max_depth,"max_tasks_per_generation":max_tasks_per_generation}
        start_eid=self._event("PLAN",payload,actor);run_id="EXTRUN."+digest({"seed_ref":seed_ref,"seed":seed,"eid":start_eid},24)
        with self.s.db:self.s.db.execute("INSERT INTO extraction_runs VALUES(?,?,?,?,?,?,?,?)",(run_id,seed_ref,json.dumps(seed,sort_keys=True,ensure_ascii=False),max_depth,max_tasks_per_generation,actor,start_eid,time.time()))
        tasks=self._create_tasks(run_id,None,seed_ref,seed,chosen,0,actor)
        return {"run_id":run_id,"seed_ref":seed_ref,"max_depth":max_depth,"max_tasks_per_generation":max_tasks_per_generation,"tasks":tasks,"transform_manifest":{name:transform_manifest()[name] for name in chosen}}

    def _create_tasks(self,run_id,parent_task_id,seed_ref,seed,transforms,depth,actor):
        tasks=[];now=time.time()
        for ordinal,name in enumerate(transforms):
            task_id="EXTTASK."+digest({"run":run_id,"parent":parent_task_id,"seed_ref":seed_ref,"transform":name,"depth":depth,"ordinal":ordinal},24)
            payload={"operation":"TASK_CREATE","task_id":task_id,"run_id":run_id,"parent_task_id":parent_task_id,"seed_ref":seed_ref,"transform":name,"depth":depth,"ordinal":ordinal}
            eid=self._event("TASK_CREATE",payload,actor)
            with self.s.db:self.s.db.execute("INSERT OR IGNORE INTO extraction_tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(task_id,run_id,parent_task_id,seed_ref,json.dumps(seed,sort_keys=True,ensure_ascii=False),name,depth,ordinal,"PLANNED","[]",eid,now,now))
            tasks.append({"task_id":task_id,"transform":name,"depth":depth,"ordinal":ordinal,"status":"PLANNED","seed_ref":seed_ref,"contract":TRANSFORM_SPECS[name]})
        return tasks

    def task(self,task_id:str):
        row=self.s.one("SELECT * FROM extraction_tasks WHERE task_id=?",(task_id,))
        if not row:return None
        out=dict(row);out["seed"]=json.loads(out.pop("seed_json"));out["result_refs"]=json.loads(out.pop("result_refs_json"));out["contract"]=TRANSFORM_SPECS[out["transform"]];return out

    def complete(self,task_id:str,outputs:Iterable[Any],witness:Mapping[str,Any],actor:str="agent"):
        row=self.s.one("SELECT * FROM extraction_tasks WHERE task_id=?",(task_id,))
        if not row:raise KeyError("unknown extraction task")
        if row["status"]!="PLANNED":raise ValueError("only PLANNED task may complete")
        witness_ref=_verified_witness(witness);outputs=list(outputs or [])
        if not outputs:raise ValueError("completion requires at least one output")
        result_refs=[];payload={"operation":"COMPLETE","task_id":task_id,"transform":row["transform"],"output_count":len(outputs),"witness_ref":witness_ref};eid=self._event("COMPLETE",payload,actor)
        with self.s.db:
            for index,output in enumerate(outputs):
                result_id="EXTRES."+digest({"task":task_id,"index":index,"payload":output,"eid":eid},24);result_refs.append(result_id)
                self.s.db.execute("INSERT INTO extraction_results VALUES(?,?,?,?,?,?,?,?)",(result_id,task_id,row["run_id"],index,json.dumps(output,sort_keys=True,ensure_ascii=False),json.dumps(dict(witness),sort_keys=True),eid,time.time()))
            self.s.db.execute("UPDATE extraction_tasks SET status='COMPLETED',result_refs_json=?,last_eid=?,updated_at=? WHERE task_id=?",(json.dumps(result_refs),eid,time.time(),task_id))
        return {"task_id":task_id,"status":"COMPLETED","transform":row["transform"],"result_refs":result_refs,"witness_ref":witness_ref,"eid":eid}

    def fail(self,task_id:str,reason:str,witness:Mapping[str,Any],actor:str="agent"):
        row=self.s.one("SELECT * FROM extraction_tasks WHERE task_id=?",(task_id,))
        if not row:raise KeyError("unknown extraction task")
        if row["status"]!="PLANNED":raise ValueError("only PLANNED task may fail")
        reason=str(reason or "").strip()
        if not reason:raise ValueError("failure reason required")
        witness_ref=_verified_witness(witness);payload={"operation":"FAIL","task_id":task_id,"transform":row["transform"],"reason":reason,"witness_ref":witness_ref};eid=self._event("FAIL",payload,actor)
        with self.s.db:self.s.db.execute("UPDATE extraction_tasks SET status='FAILED',last_eid=?,updated_at=? WHERE task_id=?",(eid,time.time(),task_id))
        return {"task_id":task_id,"status":"FAILED","reason":reason,"witness_ref":witness_ref,"eid":eid}

    def result(self,result_id:str):
        row=self.s.one("SELECT * FROM extraction_results WHERE result_id=?",(result_id,))
        if not row:return None
        out=dict(row);out["payload"]=json.loads(out.pop("payload_json"));out["witness"]=json.loads(out.pop("witness_json"));return out

    def expand_result(self,result_id:str,transforms:Optional[Iterable[str]]=None,actor:str="agent"):
        result=self.result(result_id)
        if not result:raise KeyError("unknown extraction result")
        parent=self.s.one("SELECT * FROM extraction_tasks WHERE task_id=?",(result["task_id"],));run=self.s.one("SELECT * FROM extraction_runs WHERE run_id=?",(result["run_id"],));depth=int(parent["depth"])+1
        if depth>int(run["max_depth"]):return {"run_id":result["run_id"],"result_id":result_id,"status":"DEPTH_LIMIT","depth":depth,"tasks":[]}
        chosen=list(transforms or TRANSFORM_ORDER);unknown=[name for name in chosen if name not in TRANSFORM_SPECS]
        if unknown:raise ValueError(f"unknown transforms {unknown}")
        chosen=list(dict.fromkeys(chosen))[:int(run["max_tasks_per_generation"])]
        tasks=self._create_tasks(result["run_id"],result["task_id"],result_id,result["payload"],chosen,depth,actor)
        return {"run_id":result["run_id"],"result_id":result_id,"status":"EXPANDED","depth":depth,"tasks":tasks}

    def frontier(self,run_id:str):
        return self.s.rows("SELECT task_id,run_id,parent_task_id,seed_ref,transform,depth,ordinal,status,last_eid,created_at,updated_at FROM extraction_tasks WHERE run_id=? AND status='PLANNED' ORDER BY depth,ordinal,task_id",(run_id,))

    def run(self,run_id:str):
        run=self.s.one("SELECT * FROM extraction_runs WHERE run_id=?",(run_id,))
        if not run:return None
        out=dict(run);out["seed"]=json.loads(out.pop("seed_json"));tasks=[]
        for row in self.s.rows("SELECT task_id,parent_task_id,seed_ref,transform,depth,ordinal,status,result_refs_json,last_eid FROM extraction_tasks WHERE run_id=? ORDER BY depth,ordinal,task_id",(run_id,)):
            item=dict(row);item["result_refs"]=json.loads(item.pop("result_refs_json"));tasks.append(item)
        out["tasks"]=tasks;return out

    def benchmark(self):
        q=lambda table:self.s.one(f"SELECT COUNT(*) n FROM {table}")["n"]
        statuses={row["status"]:row["n"] for row in self.s.rows("SELECT status,COUNT(*) n FROM extraction_tasks GROUP BY status")}
        return {"extraction_runs":q("extraction_runs"),"extraction_tasks":q("extraction_tasks"),"extraction_results":q("extraction_results"),"extraction_status":statuses}

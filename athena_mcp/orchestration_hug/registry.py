from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Mapping, Optional

from ..identity import digest, event_id
from ..validate import validate

HUG_PARAMS=("io","au","fx","lm","er","st")
HUG_STATUS_ORDER={"CANDIDATE":0,"TESTED":1,"CANONICAL":2}

HUG_SCHEMA='''
CREATE TABLE IF NOT EXISTS hug_implementations(
 impl_id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 version TEXT NOT NULL,
 algorithm_ref TEXT NOT NULL,
 implementation_digest TEXT NOT NULL,
 parameter_semantics_json TEXT NOT NULL,
 input_schema_json TEXT NOT NULL,
 output_schema_json TEXT NOT NULL,
 status TEXT NOT NULL,
 test_packet_json TEXT NOT NULL,
 canonical_ref TEXT,
 last_eid TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_hug_impl_name_version ON hug_implementations(name,version);
CREATE TABLE IF NOT EXISTS hug_invocations(
 invocation_id TEXT PRIMARY KEY,
 impl_id TEXT NOT NULL,
 impl_snapshot_json TEXT NOT NULL,
 arguments_json TEXT NOT NULL,
 context_json TEXT NOT NULL,
 input_digest TEXT NOT NULL,
 status TEXT NOT NULL,
 output_json TEXT,
 receipt_json TEXT NOT NULL,
 failure_json TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_hug_inv_status ON hug_invocations(status,created_at);
'''


def _nonempty(value,label):
    text=str(value or "").strip()
    if not text:raise ValueError(f"{label} required")
    return text


def _verified_ref(packet:Mapping[str,Any],label:str):
    packet=dict(packet or {})
    if packet.get("verified") is not True:raise ValueError(f"{label} requires verified=true")
    ref=_nonempty(packet.get("ref"),f"{label}.ref")
    return ref


def _canonical_ref(packet:Mapping[str,Any]):
    packet=dict(packet or {})
    if packet.get("authorized") is not True:raise ValueError("canonical promotion requires authorized=true")
    return _nonempty(packet.get("ref"),"canonical authority ref")


def _test_packet(packet:Mapping[str,Any]):
    packet=dict(packet or {});missing=[name for name in ("procedure","observation","result","witness") if not packet.get(name)]
    if missing:raise ValueError(f"HUG test packet missing {missing}")
    witness=packet["witness"]
    if isinstance(witness,Mapping):_verified_ref(witness,"HUG test witness")
    elif not str(witness).strip():raise ValueError("HUG test witness required")
    return packet


def _parameter_semantics(value:Mapping[str,Any]):
    value=dict(value or {});missing=[p for p in HUG_PARAMS if p not in value];extra=sorted(set(value)-set(HUG_PARAMS))
    if missing or extra:raise ValueError(f"HUG parameter semantics must define exactly {list(HUG_PARAMS)}; missing={missing}, extra={extra}")
    out={}
    for key in HUG_PARAMS:
        packet=value[key]
        if isinstance(packet,str):packet={"meaning":packet}
        if not isinstance(packet,Mapping):raise ValueError(f"HUG parameter {key} semantics must be object/string")
        packet=dict(packet);packet["meaning"]=_nonempty(packet.get("meaning"),f"HUG parameter {key}.meaning")
        out[key]=packet
    return out


def _snapshot(row):
    return {
        "impl_id":row["impl_id"],"name":row["name"],"version":row["version"],"algorithm_ref":row["algorithm_ref"],"implementation_digest":row["implementation_digest"],
        "parameter_semantics":json.loads(row["parameter_semantics_json"]),"input_schema":json.loads(row["input_schema_json"]),"output_schema":json.loads(row["output_schema_json"]),"status":row["status"],"canonical_ref":row["canonical_ref"],"last_eid":row["last_eid"]
    }


class HugRegistry:
    def __init__(self,core):
        self.core=core;self.s=core.s
        with self.s.db:self.s.db.executescript(HUG_SCHEMA)
        self.core.register("TOOL","ALGORITHM","INVOKE","HUG_ABI","REGISTERED_IMPL_ONLY",{"params":list(HUG_PARAMS),"implementation":"registered+witnessed"},{"invocation":"HUGINV","completion":"receipt-bearing"},actor="GENESIS.HUG.ABI",status="CANONICAL")

    def _event(self,op,payload,actor):
        parent=self.s.head("global");pe=parent["eid"] if parent else None
        eid=event_id(f"HUG_{op}",actor,pe,payload);ed=digest(payload,32);self.s.put_event(eid,f"HUG_{op}",actor,pe,payload,ed);self.s.set_head("global",None,None,eid,ed);return eid

    def register(self,name:str,version:str,algorithm_ref:str,implementation_digest:str,parameter_semantics:Mapping[str,Any],input_schema:Mapping[str,Any],output_schema:Mapping[str,Any],actor:str="agent"):
        name=_nonempty(name,"HUG name");version=_nonempty(version,"HUG version");algorithm_ref=_nonempty(algorithm_ref,"algorithm_ref");implementation_digest=_nonempty(implementation_digest,"implementation_digest");sem=_parameter_semantics(parameter_semantics)
        if not isinstance(input_schema,Mapping) or not isinstance(output_schema,Mapping):raise ValueError("HUG input/output schemas must be objects")
        identity={"name":name,"version":version,"algorithm_ref":algorithm_ref,"implementation_digest":implementation_digest,"parameter_semantics":sem,"input_schema":dict(input_schema),"output_schema":dict(output_schema)}
        impl_id="HUGIMPL."+digest(identity,24)
        existing=self.s.one("SELECT * FROM hug_implementations WHERE impl_id=?",(impl_id,))
        if existing:return {"action":"REUSE","implementation":self.state(impl_id)}
        collision=self.s.one("SELECT impl_id FROM hug_implementations WHERE name=? AND version=?",(name,version))
        if collision:raise ValueError("HUG name/version already registered with different implementation identity")
        payload={"operation":"REGISTER","impl_id":impl_id,"name":name,"version":version,"algorithm_ref":algorithm_ref,"implementation_digest":implementation_digest};eid=self._event("REGISTER",payload,actor);now=time.time()
        with self.s.db:self.s.db.execute("INSERT INTO hug_implementations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(impl_id,name,version,algorithm_ref,implementation_digest,json.dumps(sem,sort_keys=True),json.dumps(dict(input_schema),sort_keys=True),json.dumps(dict(output_schema),sort_keys=True),"CANDIDATE","{}",None,eid,now,now))
        return {"action":"CREATED","implementation":self.state(impl_id)}

    def state(self,impl_id:str):
        row=self.s.one("SELECT * FROM hug_implementations WHERE impl_id=?",(impl_id,))
        if not row:return None
        out=_snapshot(row);out["test_packet"]=json.loads(row["test_packet_json"]);out["created_at"]=row["created_at"];out["updated_at"]=row["updated_at"];return out

    def list(self,status:Optional[str]=None,limit:int=100):
        limit=max(1,min(int(limit),500));args=[];where=""
        if status is not None:
            status=str(status).upper()
            if status not in HUG_STATUS_ORDER:raise ValueError("invalid HUG status")
            where=" WHERE status=?";args.append(status)
        args.append(limit);return [self.state(row["impl_id"]) for row in self.s.rows(f"SELECT impl_id FROM hug_implementations{where} ORDER BY updated_at DESC LIMIT ?",tuple(args))]

    def promote(self,impl_id:str,target_status:str,test:Optional[Mapping[str,Any]]=None,canonical_authority:Optional[Mapping[str,Any]]=None,actor:str="agent"):
        row=self.s.one("SELECT * FROM hug_implementations WHERE impl_id=?",(impl_id,))
        if not row:raise KeyError("unknown HUG implementation")
        current=row["status"];target=str(target_status).upper()
        if target not in HUG_STATUS_ORDER:raise ValueError("invalid HUG target status")
        if HUG_STATUS_ORDER[target]!=HUG_STATUS_ORDER[current]+1:raise ValueError(f"HUG promotion must advance exactly one step: {current}->{target} invalid")
        test_packet=json.loads(row["test_packet_json"]);canonical_ref=row["canonical_ref"]
        if current=="CANDIDATE" and target=="TESTED":test_packet=_test_packet(test or {})
        elif current=="TESTED" and target=="CANONICAL":canonical_ref=_canonical_ref(canonical_authority or {})
        payload={"operation":"PROMOTE","impl_id":impl_id,"from":current,"to":target,"test_witness":test_packet.get("witness"),"canonical_ref":canonical_ref};eid=self._event("PROMOTE",payload,actor)
        with self.s.db:self.s.db.execute("UPDATE hug_implementations SET status=?,test_packet_json=?,canonical_ref=?,last_eid=?,updated_at=? WHERE impl_id=?",(target,json.dumps(test_packet,sort_keys=True),canonical_ref,eid,time.time(),impl_id))
        return {"transition":f"{current}->{target}","implementation":self.state(impl_id)}

    def plan(self,impl_id:str,arguments:Mapping[str,Any],context:Optional[Mapping[str,Any]]=None,required_status:str="CANONICAL",actor:str="agent"):
        row=self.s.one("SELECT * FROM hug_implementations WHERE impl_id=?",(impl_id,))
        if not row:raise KeyError("unknown HUG implementation")
        required=str(required_status).upper()
        if required not in HUG_STATUS_ORDER:raise ValueError("invalid required HUG status")
        if HUG_STATUS_ORDER[row["status"]]<HUG_STATUS_ORDER[required]:raise ValueError(f"HUG implementation status {row['status']} below required {required}")
        args=dict(arguments or {});missing=[p for p in HUG_PARAMS if p not in args];extra=sorted(set(args)-set(HUG_PARAMS))
        if missing or extra:raise ValueError(f"HUG invocation arguments must be exactly {list(HUG_PARAMS)}; missing={missing}, extra={extra}")
        validate(json.loads(row["input_schema_json"]),args)
        snap=_snapshot(row);input_packet={"implementation":snap,"arguments":args,"context":dict(context or {})};raw=json.dumps(input_packet,sort_keys=True,ensure_ascii=False,separators=(",",":"));input_digest=hashlib.sha256(raw.encode()).hexdigest()
        invocation_id="HUGINV."+digest({"impl":impl_id,"input_digest":input_digest,"nonce":time.time_ns()},24);payload={"operation":"PLAN","invocation_id":invocation_id,"impl_id":impl_id,"required_status":required,"input_digest":input_digest};eid=self._event("PLAN",payload,actor);now=time.time()
        with self.s.db:self.s.db.execute("INSERT INTO hug_invocations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(invocation_id,impl_id,json.dumps(snap,sort_keys=True,ensure_ascii=False),json.dumps(args,sort_keys=True,ensure_ascii=False),json.dumps(dict(context or {}),sort_keys=True,ensure_ascii=False),input_digest,"PLANNED",None,"{}","{}",eid,now,now))
        return {"invocation_id":invocation_id,"impl_snapshot":snap,"arguments":args,"context":dict(context or {}),"input_digest":input_digest,"status":"PLANNED","execution_boundary":"EXTERNAL_OR_REGISTERED_EXECUTOR_REQUIRED","eid":eid}

    def complete(self,invocation_id:str,output:Any,receipt:Mapping[str,Any],actor:str="agent"):
        row=self.s.one("SELECT * FROM hug_invocations WHERE invocation_id=?",(invocation_id,))
        if not row:raise KeyError("unknown HUG invocation")
        if row["status"]!="PLANNED":raise ValueError("only PLANNED HUG invocation may complete")
        receipt_ref=_verified_ref(receipt,"HUG execution receipt");impl=json.loads(row["impl_snapshot_json"]);validate(impl["output_schema"],output)
        payload={"operation":"COMPLETE","invocation_id":invocation_id,"impl_id":row["impl_id"],"receipt_ref":receipt_ref};eid=self._event("COMPLETE",payload,actor)
        with self.s.db:self.s.db.execute("UPDATE hug_invocations SET status='COMPLETED',output_json=?,receipt_json=?,eid=?,updated_at=? WHERE invocation_id=?",(json.dumps(output,sort_keys=True,ensure_ascii=False),json.dumps(dict(receipt),sort_keys=True),eid,time.time(),invocation_id))
        return {"invocation_id":invocation_id,"status":"COMPLETED","output":output,"receipt_ref":receipt_ref,"eid":eid}

    def fail(self,invocation_id:str,reason:str,witness:Mapping[str,Any],actor:str="agent"):
        row=self.s.one("SELECT * FROM hug_invocations WHERE invocation_id=?",(invocation_id,))
        if not row:raise KeyError("unknown HUG invocation")
        if row["status"]!="PLANNED":raise ValueError("only PLANNED HUG invocation may fail")
        reason=_nonempty(reason,"HUG failure reason");ref=_verified_ref(witness,"HUG failure witness");failure={"reason":reason,"witness":dict(witness)};payload={"operation":"FAIL","invocation_id":invocation_id,"impl_id":row["impl_id"],"reason":reason,"witness_ref":ref};eid=self._event("FAIL",payload,actor)
        with self.s.db:self.s.db.execute("UPDATE hug_invocations SET status='FAILED',failure_json=?,eid=?,updated_at=? WHERE invocation_id=?",(json.dumps(failure,sort_keys=True),eid,time.time(),invocation_id))
        return {"invocation_id":invocation_id,"status":"FAILED","reason":reason,"witness_ref":ref,"eid":eid}

    def invocation(self,invocation_id:str):
        row=self.s.one("SELECT * FROM hug_invocations WHERE invocation_id=?",(invocation_id,))
        if not row:return None
        out=dict(row);out["impl_snapshot"]=json.loads(out.pop("impl_snapshot_json"));out["arguments"]=json.loads(out.pop("arguments_json"));out["context"]=json.loads(out.pop("context_json"));out["output"]=json.loads(out.pop("output_json")) if out.get("output_json") else None;out.pop("output_json",None);out["receipt"]=json.loads(out.pop("receipt_json"));out["failure"]=json.loads(out.pop("failure_json"));return out

    def verify_packet(self,invocation_id:str):
        row=self.invocation(invocation_id)
        if not row:raise KeyError("unknown HUG invocation")
        packet={"implementation":row["impl_snapshot"],"arguments":row["arguments"],"context":row["context"]};raw=json.dumps(packet,sort_keys=True,ensure_ascii=False,separators=(",",":"));recomputed=hashlib.sha256(raw.encode()).hexdigest();match=recomputed==row["input_digest"]
        return {"invocation_id":invocation_id,"status":"PACKET_MATCH" if match else "PACKET_DIVERGED","match":match,"stored_input_digest":row["input_digest"],"recomputed_input_digest":recomputed,"semantic_replay":"N/A_UNLESS_REGISTERED_EXECUTOR_REPLAYS_ALGORITHM"}

    def benchmark(self):
        counts={row["status"]:row["n"] for row in self.s.rows("SELECT status,COUNT(*) n FROM hug_implementations GROUP BY status")};inv={row["status"]:row["n"] for row in self.s.rows("SELECT status,COUNT(*) n FROM hug_invocations GROUP BY status")}
        return {"hug_implementations":sum(counts.values()),"hug_implementation_status":counts,"hug_invocations":sum(inv.values()),"hug_invocation_status":inv}

from __future__ import annotations

import hashlib,json,threading,time
from typing import Any,Mapping

VERSION="ATHENA.EPHEMERAL.COORDINATION.MEMBRANE.V0"
RECEIPT_STAGES=("DELIVERED","PRESENTED","CONSUMED","INCORPORATED","DECISION_CHANGED")
RECEIPT_RANK={x:i for i,x in enumerate(RECEIPT_STAGES,1)}
DELIVERY_CLASSES=("RENDEZVOUS","NEED_OFFER","NUDGE","BLOCKER","MATERIAL_CANDIDATE")
SCHEMA='''
CREATE TABLE IF NOT EXISTS ephemeral_presence(aid TEXT PRIMARY KEY,presence_id TEXT NOT NULL,epoch TEXT NOT NULL,capabilities_json TEXT NOT NULL,need_offer_summary_json TEXT NOT NULL,lamport INTEGER NOT NULL,causal_parents_json TEXT NOT NULL,source_digest TEXT NOT NULL,accepted_at REAL NOT NULL,expires_at REAL NOT NULL,cursor INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS ephemeral_packets(packet_id TEXT PRIMARY KEY,sender_aid TEXT NOT NULL,delivery_class TEXT NOT NULL,salience REAL NOT NULL,ttl_ms INTEGER NOT NULL,packet_digest_or_ref TEXT NOT NULL,lamport INTEGER NOT NULL,causal_parents_json TEXT NOT NULL,coalesce_key TEXT NOT NULL,created_at REAL NOT NULL,expires_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_ephemeral_packets_coalesce ON ephemeral_packets(coalesce_key,expires_at);
CREATE TABLE IF NOT EXISTS ephemeral_deliveries(packet_id TEXT NOT NULL,recipient_aid TEXT NOT NULL,cursor INTEGER NOT NULL,route_state TEXT NOT NULL,created_at REAL NOT NULL,expires_at REAL NOT NULL,PRIMARY KEY(packet_id,recipient_aid),FOREIGN KEY(packet_id) REFERENCES ephemeral_packets(packet_id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS idx_ephemeral_deliveries_recipient ON ephemeral_deliveries(recipient_aid,cursor);
CREATE TABLE IF NOT EXISTS ephemeral_receipts(packet_id TEXT NOT NULL,aid TEXT NOT NULL,stage TEXT NOT NULL,stage_rank INTEGER NOT NULL,witness_json TEXT NOT NULL,cursor INTEGER NOT NULL,created_at REAL NOT NULL,PRIMARY KEY(packet_id,aid,stage),FOREIGN KEY(packet_id) REFERENCES ephemeral_packets(packet_id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS ephemeral_events(cursor INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT NOT NULL,subject_id TEXT NOT NULL,aid TEXT NOT NULL,payload_json TEXT NOT NULL,created_at REAL NOT NULL);
'''

def _j(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _h(v):return hashlib.sha256(_j(v).encode()).hexdigest()
def _t(v,n):
    x=str(v or "").strip()
    if not x:raise ValueError(f"{n} must be non-empty")
    return x
def _i(v,n,lo,hi):
    try:x=int(v)
    except (TypeError,ValueError):raise ValueError(f"{n} must be an integer") from None
    if not lo<=x<=hi:raise ValueError(f"{n} must be between {lo} and {hi}")
    return x
def _f(v,n,lo,hi):
    try:x=float(v)
    except (TypeError,ValueError):raise ValueError(f"{n} must be numeric") from None
    if not lo<=x<=hi:raise ValueError(f"{n} must be between {lo} and {hi}")
    return x
def _ss(v,n,limit):
    if v is None:return []
    if not isinstance(v,(list,tuple)):raise ValueError(f"{n} must be an array")
    out=[]
    for raw in v:
        x=_t(raw,n)
        if x not in out:out.append(x)
        if len(out)>limit:raise ValueError(f"{n} exceeds {limit} unique items")
    return out

class EphemeralCoordinationRuntime:
    """Bounded request/poll coordination over one process-local SQLite store; authority is always NONE."""
    def __init__(self,store,*,clock=None,per_aid_queue_limit=128,sender_active_salience_limit=32.0,global_active_salience_limit=256.0,max_active_packets=4096,max_events=8192):
        self.store=store;self.db=store.db;self._lock=getattr(store,"_lock",threading.RLock());self.clock=clock or time.time
        self.per_aid_queue_limit=int(per_aid_queue_limit);self.sender_active_salience_limit=float(sender_active_salience_limit);self.global_active_salience_limit=float(global_active_salience_limit);self.max_active_packets=int(max_active_packets);self.max_events=int(max_events)
        if min(self.per_aid_queue_limit,self.max_active_packets,self.max_events)<=0:raise ValueError("limits must be positive")
        with self._lock,self.db:self.db.executescript(SCHEMA)
    def _now(self):return float(self.clock())
    def _event(self,kind,subject,aid,payload,now):
        cur=self.db.execute("INSERT INTO ephemeral_events(event_type,subject_id,aid,payload_json,created_at) VALUES(?,?,?,?,?)",(kind,subject,aid,_j(payload),now));c=int(cur.lastrowid);floor=max(0,c-self.max_events)
        if floor:self.db.execute("DELETE FROM ephemeral_events WHERE cursor<=?",(floor,))
        return c
    def _cursor(self,fn):return int(self.db.execute(f"SELECT {fn}(cursor) FROM ephemeral_events").fetchone()[0] or 0)
    def _gc(self,now):
        p=self.db.execute("SELECT COUNT(*) FROM ephemeral_presence WHERE expires_at<=?",(now,)).fetchone()[0];d=self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE expires_at<=?",(now,)).fetchone()[0]
        self.db.execute("DELETE FROM ephemeral_presence WHERE expires_at<=?",(now,));self.db.execute("DELETE FROM ephemeral_deliveries WHERE expires_at<=?",(now,))
        where="expires_at<=? OR NOT EXISTS(SELECT 1 FROM ephemeral_deliveries d WHERE d.packet_id=ephemeral_packets.packet_id)";q=self.db.execute(f"SELECT COUNT(*) FROM ephemeral_packets WHERE {where}",(now,)).fetchone()[0];self.db.execute(f"DELETE FROM ephemeral_packets WHERE {where}",(now,))
        return {"presence_expired":int(p),"deliveries_expired":int(d),"packets_expired_or_empty":int(q)}
    def _live(self,aid,now):return self.db.execute("SELECT 1 FROM ephemeral_presence WHERE aid=? AND expires_at>?",(aid,now)).fetchone()
    def present(self,a:Mapping[str,Any]):
        aid=_t(a.get("aid"),"aid");epoch=_t(a.get("epoch"),"epoch");ttl=_i(a.get("ttl_ms"),"ttl_ms",250,300000);caps=_ss(a.get("capabilities",[]),"capabilities",64);summary=a.get("need_offer_summary") or {}
        if not isinstance(summary,Mapping):raise ValueError("need_offer_summary must be an object")
        lam=_i(a.get("lamport",0),"lamport",0,2**63-1);parents=_ss(a.get("causal_parents",[]),"causal_parents",32);src=_t(a.get("source_digest"),"source_digest");now=self._now();exp=now+ttl/1000;pid="epres_"+_h({"aid":aid,"epoch":epoch,"source_digest":src})[:32]
        with self._lock,self.db:
            gc=self._gc(now);c=self._event("PRESENT",pid,aid,{"epoch":epoch,"ttl_ms":ttl,"lamport":lam},now)
            self.db.execute("INSERT INTO ephemeral_presence VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(aid) DO UPDATE SET presence_id=excluded.presence_id,epoch=excluded.epoch,capabilities_json=excluded.capabilities_json,need_offer_summary_json=excluded.need_offer_summary_json,lamport=excluded.lamport,causal_parents_json=excluded.causal_parents_json,source_digest=excluded.source_digest,accepted_at=excluded.accepted_at,expires_at=excluded.expires_at,cursor=excluded.cursor",(aid,pid,epoch,_j(caps),_j(dict(summary)),lam,_j(parents),src,now,exp,c))
        return {"presence_id":pid,"accepted_at":now,"expires_at":exp,"cursor":c,"gc":gc,"standing":"PROCESS_LOCAL_EPHEMERAL_PRESENCE","source_digest_standing":"CALLER_SUPPLIED_OPAQUE_REFERENCE","authority":"NONE","laws":["PRESENCE!=CLAIM","PRESENCE!=HOST_LIVENESS_PROOF","FAST_CHANNEL!=TRUTH"]}
    def _recipients(self,s):
        if not isinstance(s,Mapping) or set(s)-{"aids"}:raise ValueError("recipient_selector supports only explicit aids")
        out=sorted(set(_ss(s.get("aids"),"recipient_selector.aids",32)))
        if not out:raise ValueError("recipient_selector.aids must be non-empty")
        return out
    def _salience(self,now,sender=None):
        sql="SELECT COALESCE(SUM(p.salience),0) FROM ephemeral_deliveries d JOIN ephemeral_packets p ON p.packet_id=d.packet_id WHERE d.expires_at>?";args=[now]
        if sender is not None:sql+=" AND p.sender_aid=?";args.append(sender)
        return float(self.db.execute(sql,tuple(args)).fetchone()[0] or 0)
    def post(self,a:Mapping[str,Any]):
        sender=_t(a.get("sender_aid"),"sender_aid");recips=self._recipients(a.get("recipient_selector"));kind=_t(a.get("delivery_class"),"delivery_class")
        if kind not in DELIVERY_CLASSES:raise ValueError(f"delivery_class must be one of {list(DELIVERY_CLASSES)}")
        sal=_f(a.get("salience"),"salience",0,1);ttl=_i(a.get("ttl_ms"),"ttl_ms",250,300000);ref=_t(a.get("packet_digest_or_ref"),"packet_digest_or_ref");lam=_i(a.get("lamport",0),"lamport",0,2**63-1);parents=_ss(a.get("causal_parents",[]),"causal_parents",32);now=self._now();exp=now+ttl/1000
        key=_h({"sender":sender,"recipients":recips,"delivery_class":kind,"ref":ref});pid="epkt_"+_h({"coalesce_key":key,"lamport":lam,"parents":parents})[:32]
        with self._lock,self.db:
            gc=self._gc(now)
            if not self._live(sender,now):raise ValueError("sender_aid must have unexpired process-local presence")
            old=self.db.execute("SELECT packet_id FROM ephemeral_packets WHERE coalesce_key=? AND expires_at>? ORDER BY created_at DESC LIMIT 1",(key,now)).fetchone()
            if old:return {"packet_id":old["packet_id"],"route_state":"COALESCED_ACTIVE","cursor":self._cursor("MAX"),"coalesced":True,"gc":gc,"authority":"NONE","durable_escalation_required":kind=="MATERIAL_CANDIDATE"}
            if self.db.execute("SELECT COUNT(*) FROM ephemeral_packets WHERE expires_at>?",(now,)).fetchone()[0]>=self.max_active_packets:raise ValueError("GLOBAL_ACTIVE_PACKET_BACKPRESSURE")
            added=sal*len(recips)
            if self._salience(now,sender)+added>self.sender_active_salience_limit:raise ValueError("SENDER_SALIENCE_BACKPRESSURE")
            if self._salience(now)+added>self.global_active_salience_limit:raise ValueError("GLOBAL_SALIENCE_BACKPRESSURE")
            for aid in recips:
                if self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE recipient_aid=? AND expires_at>?",(aid,now)).fetchone()[0]>=self.per_aid_queue_limit:raise ValueError(f"RECIPIENT_QUEUE_BACKPRESSURE aid={aid}")
            c=self._event("POST",pid,sender,{"recipients":recips,"delivery_class":kind,"salience":sal},now);self.db.execute("INSERT INTO ephemeral_packets VALUES(?,?,?,?,?,?,?,?,?,?,?)",(pid,sender,kind,sal,ttl,ref,lam,_j(parents),key,now,exp));self.db.executemany("INSERT INTO ephemeral_deliveries VALUES(?,?,?,?,?,?)",[(pid,x,c,"ROUTED",now,exp) for x in recips])
        return {"packet_id":pid,"route_state":"ROUTED","cursor":c,"coalesced":False,"recipient_count":len(recips),"gc":gc,"authority":"NONE","durable_escalation_required":kind=="MATERIAL_CANDIDATE","durable_escalation_contract":{"performed":False,"target":"ROOM_OR_GIT_MESSAGE_BOARD","law":"MATERIAL_ESCALATION_IS_EXPLICIT_CALLER_WORK_NOT_HIDDEN_BACKGROUND_EXECUTION"}}
    def _stage(self,pid,aid):
        r=self.db.execute("SELECT stage FROM ephemeral_receipts WHERE packet_id=? AND aid=? ORDER BY stage_rank DESC LIMIT 1",(pid,aid)).fetchone();return r["stage"] if r else None
    def poll(self,a:Mapping[str,Any]):
        aid=_t(a.get("aid"),"aid");after=_i(a.get("after_cursor",0),"after_cursor",0,2**63-1);limit=_i(a.get("max_items",20),"max_items",1,100);budget=_f(a.get("salience_budget",8),"salience_budget",0,32);now=self._now()
        with self._lock,self.db:
            gc=self._gc(now);floor=self._cursor("MIN");rows=self.db.execute("SELECT d.cursor,d.route_state,d.expires_at,p.* FROM ephemeral_deliveries d JOIN ephemeral_packets p ON p.packet_id=d.packet_id WHERE d.recipient_aid=? AND d.cursor>? AND d.expires_at>? ORDER BY d.cursor ASC LIMIT ?",(aid,after,now,limit+1)).fetchall();items=[];spent=0.;blocked=False
            for r in rows:
                sal=float(r["salience"])
                if len(items)>=limit:break
                if spent+sal>budget:blocked=True;break
                spent+=sal;items.append({"cursor":int(r["cursor"]),"packet_id":r["packet_id"],"sender_aid":r["sender_aid"],"delivery_class":r["delivery_class"],"salience":sal,"packet_digest_or_ref":r["packet_digest_or_ref"],"lamport":int(r["lamport"]),"causal_parents":json.loads(r["causal_parents_json"]),"route_state":r["route_state"],"created_at":float(r["created_at"]),"expires_at":float(r["expires_at"]),"receipt_stage":self._stage(r["packet_id"],aid)})
            queued=int(self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE recipient_aid=? AND expires_at>?",(aid,now)).fetchone()[0])
        return {"packets":items,"next_cursor":int(items[-1]["cursor"]) if items else after,"cursor_floor":floor,"replay_truncated":bool(after and floor and after<floor),"salience_spent":spent,"queue_pressure":{"queued":queued,"limit":self.per_aid_queue_limit,"ratio":min(1.,queued/self.per_aid_queue_limit)},"dropped_or_coalesced_counts":{"expired_dropped":gc["deliveries_expired"],"budget_blocked":int(blocked),"coalesced_in_this_poll":0},"ordering":"MONOTONIC_PROCESS_CURSOR;LAMPORT_IS_PACKET_METADATA_NOT_GLOBAL_TOTAL_ORDER","authority":"NONE","law":"POLL_IS_EXPLICIT_RUNTIME_WORK_NOT_BACKGROUND_PUSH"}
    def receipt(self,a:Mapping[str,Any]):
        pid=_t(a.get("packet_id"),"packet_id");aid=_t(a.get("aid"),"aid");stage=_t(a.get("stage"),"stage")
        if stage not in RECEIPT_RANK:raise ValueError(f"stage must be one of {list(RECEIPT_STAGES)}")
        witness=a.get("witness") or {}
        if not isinstance(witness,Mapping):raise ValueError("witness must be an object")
        if RECEIPT_RANK[stage]>=RECEIPT_RANK["CONSUMED"] and not witness:raise ValueError(f"{stage} requires a non-empty typed witness object")
        now=self._now()
        with self._lock,self.db:
            gc=self._gc(now)
            if not self.db.execute("SELECT 1 FROM ephemeral_deliveries WHERE packet_id=? AND recipient_aid=? AND expires_at>?",(pid,aid,now)).fetchone():raise ValueError("receipt requires an unexpired packet routed to aid")
            old=self.db.execute("SELECT cursor,created_at,witness_json FROM ephemeral_receipts WHERE packet_id=? AND aid=? AND stage=?",(pid,aid,stage)).fetchone()
            if old:return {"packet_id":pid,"aid":aid,"stage":stage,"cursor":int(old["cursor"]),"created_at":float(old["created_at"]),"idempotent":True,"witness":json.loads(old["witness_json"]),"authority":"NONE","receipt_standing":"CALLER_ATTESTED_RUNTIME_RECEIPT"}
            high=int(self.db.execute("SELECT COALESCE(MAX(stage_rank),0) FROM ephemeral_receipts WHERE packet_id=? AND aid=?",(pid,aid)).fetchone()[0] or 0);expected=high+1
            if RECEIPT_RANK[stage]!=expected:raise ValueError(f"RECEIPT_STAGE_GAP expected={RECEIPT_STAGES[expected-1] if expected<=len(RECEIPT_STAGES) else 'NONE'} got={stage}")
            c=self._event("RECEIPT",pid,aid,{"stage":stage,"witness":dict(witness)},now);self.db.execute("INSERT INTO ephemeral_receipts VALUES(?,?,?,?,?,?,?)",(pid,aid,stage,RECEIPT_RANK[stage],_j(dict(witness)),c,now))
        return {"packet_id":pid,"aid":aid,"stage":stage,"cursor":c,"created_at":now,"idempotent":False,"gc":gc,"authority":"NONE","receipt_standing":"CALLER_ATTESTED_RUNTIME_RECEIPT","law":"RECEIPT_STAGE_DOES_NOT_MINT_CAUSAL_GAIN_OR_DURABLE_AUTHORITY"}
    def snapshot(self,a:Mapping[str,Any]):
        scope=_t(a.get("scope","global"),"scope");cursor=_i(a.get("cursor",0),"cursor",0,2**63-1);bound=_i(a.get("freshness_bound_ms",60000),"freshness_bound_ms",250,300000);now=self._now();fresh=now-bound/1000
        with self._lock,self.db:
            gc=self._gc(now);floor=self._cursor("MIN")
            if scope=="global":rows=self.db.execute("SELECT * FROM ephemeral_presence WHERE expires_at>? AND accepted_at>=? ORDER BY cursor",(now,fresh)).fetchall()
            elif scope.startswith("aid:"):rows=self.db.execute("SELECT * FROM ephemeral_presence WHERE aid=? AND expires_at>? AND accepted_at>=? ORDER BY cursor",(_t(scope[4:],"scope aid"),now,fresh)).fetchall()
            else:raise ValueError("scope must be 'global' or 'aid:<AID>'")
            presence=[];need=[];pressure=[]
            for r in rows:
                aid=r["aid"];summary=json.loads(r["need_offer_summary_json"]);queued=int(self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE recipient_aid=? AND expires_at>?",(aid,now)).fetchone()[0]);presence.append({"aid":aid,"presence_id":r["presence_id"],"epoch":r["epoch"],"capabilities":json.loads(r["capabilities_json"]),"lamport":int(r["lamport"]),"causal_parents":json.loads(r["causal_parents_json"]),"source_digest":r["source_digest"],"accepted_at":float(r["accepted_at"]),"expires_at":float(r["expires_at"]),"cursor":int(r["cursor"])});pressure.append({"aid":aid,"queued":queued,"limit":self.per_aid_queue_limit,"ratio":min(1.,queued/self.per_aid_queue_limit)})
                if summary:need.append({"aid":aid,"summary":summary,"expires_at":float(r["expires_at"])})
            nxt=self._cursor("MAX")
        return {"scope":scope,"fresh_presence":presence,"need_offer_index":need,"queue_pressure":pressure,"cursor":cursor,"cursor_floor":floor,"next_cursor":nxt,"changed_since_cursor":bool(nxt>cursor),"replay_truncated":bool(cursor and floor and cursor<floor),"gc":gc,"advisory":True,"shared_deployment_proven":False,"product_exposure_proven":False,"authority":"NONE","laws":["SNAPSHOT!=DURABLE_TRUTH","PROCESS_LOCAL_SQLITE!=SHARED_CROSS_AGENT_DEPLOYMENT","REPOSITORY_IMPLEMENTATION!=LIVE_TOOL_EXPOSURE","UNKNOWN!=ZERO"]}
    def describe(self):return {"version":VERSION,"transport":"REQUEST_POLL_PROCESS_LOCAL_SQLITE","operations":["athena_ephemeral_present","athena_ephemeral_post","athena_ephemeral_poll","athena_ephemeral_receipt","athena_ephemeral_snapshot"],"delivery_classes":list(DELIVERY_CLASSES),"receipt_stages":list(RECEIPT_STAGES),"limits":{"per_aid_queue_limit":self.per_aid_queue_limit,"sender_active_salience_limit":self.sender_active_salience_limit,"global_active_salience_limit":self.global_active_salience_limit,"max_active_packets":self.max_active_packets,"max_events":self.max_events},"authority":"NONE","deployment_standing":"SOURCE_IMPLEMENTATION_ONLY_SHARED_DEPLOYMENT_UNKNOWN","product_exposure":"UNKNOWN","behavioral_gain":"UNKNOWN","causal_gain":"UNKNOWN"}
    def benchmark(self):
        now=self._now()
        with self._lock,self.db:
            self._gc(now);p=int(self.db.execute("SELECT COUNT(*) FROM ephemeral_presence WHERE expires_at>?",(now,)).fetchone()[0]);q=int(self.db.execute("SELECT COUNT(*) FROM ephemeral_packets WHERE expires_at>?",(now,)).fetchone()[0]);d=int(self.db.execute("SELECT COUNT(*) FROM ephemeral_deliveries WHERE expires_at>?",(now,)).fetchone()[0]);r=int(self.db.execute("SELECT COUNT(*) FROM ephemeral_receipts").fetchone()[0])
        return {"ephemeral_coordination_version":VERSION,"ephemeral_presence_live":p,"ephemeral_packets_live":q,"ephemeral_deliveries_live":d,"ephemeral_receipts_live":r}

class EphemeralCoordinationSurface:
    def __init__(self,store,*,clock=None):self.runtime=EphemeralCoordinationRuntime(store,clock=clock)
    def call_tool(self,name:str,args:Mapping[str,Any]):
        f={"athena_ephemeral_present":self.runtime.present,"athena_ephemeral_post":self.runtime.post,"athena_ephemeral_poll":self.runtime.poll,"athena_ephemeral_receipt":self.runtime.receipt,"athena_ephemeral_snapshot":self.runtime.snapshot}.get(name)
        return (True,f(args)) if f else (False,None)
    def read_resource(self,uri:str):
        from .ephemeral_coordination_protocol import EPHEMERAL_COORDINATION_RESOURCE
        if uri!=EPHEMERAL_COORDINATION_RESOURCE["uri"]:raise KeyError(uri)
        return self.runtime.describe()
    def benchmark(self):return self.runtime.benchmark()

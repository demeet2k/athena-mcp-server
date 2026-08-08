from __future__ import annotations
import hashlib, json, time, math
from collections import defaultdict
from .identity import capability_signature, canonical_identity, version_id, manifestation_id, event_id, digest
from .kc144 import coordinate_text, station, stable_gid, stations

GLOBAL_CLASSES={"SCALE","COORDINATE_LAW","PROMPT_LAW","HARNESS_LAW","TOOL","ATTRACTOR","CONSTITUTION"}
SCALE_LEVELS={0:"RAW_EVENT",1:"STATE_DELTA",2:"RELATION_DELTA",3:"MOTIF",4:"GENERATOR",5:"ORGAN_NATIVE_LAW"}

class StaleTarget(Exception): pass

class AthenaCore:
    def __init__(self,store): self.s=store
    def register(self, kind, domain, verb, object_name, method, input_contract, output_contract, constraints=None, payload=None, actor='system', status='CANDIDATE'):
        sig=capability_signature(kind,domain,verb,object_name,method,input_contract,output_contract,constraints)
        cid,name,oid=canonical_identity(sig)
        existing=self.s.one("SELECT * FROM objects WHERE cid=?",(cid,))
        if existing:
            return {"action":"REUSE","object":existing,"head":self.s.head(f"object:{oid}")}
        rec={"cid":cid,"canonical_name":name,"oid":oid,"kind":sig['kind'],"domain":sig['domain'],"verb":sig['verb'],"object":sig['object'],"method":sig['method'],"signature":sig}
        self.s.put_object(rec)
        payload=payload or {"signature":sig}
        vid=version_id(oid,payload,None)
        ver=self.s.put_version(vid,oid,None,payload,status)
        ep={"operation":"REGISTER","oid":oid,"cid":cid,"vid":vid,"canonical_name":name}
        parent=self.s.head('global'); pe=parent['eid'] if parent else None
        eid=event_id('REGISTER',actor,pe,ep); ed=digest(ep,32)
        self.s.put_event(eid,'REGISTER',actor,pe,ep,ed)
        self.s.set_head(f"object:{oid}",oid,vid,eid,ed); self.s.set_head('global',oid,vid,eid,ed)
        gid=stable_gid(name); st=station(gid)
        return {"action":"CREATED","object":rec,"version":ver,"event":eid,"kc144":st.__dict__}
    def commit_delta(self, oid, expected_vid, delta, actor='agent', status='CANDIDATE', move_head=True):
        obj=self.s.one("SELECT * FROM objects WHERE oid=?",(oid,));
        if not obj: raise KeyError("unknown oid")
        head=self.s.head(f"object:{oid}")
        current=head['vid'] if head else None
        if current != expected_vid:
            raise StaleTarget(json.dumps({"status":"STALE_TARGET","expected":expected_vid,"current":current,"oid":oid}))
        parent_payload={}
        if current:
            row=self.s.one("SELECT payload_json FROM versions WHERE vid=?",(current,)); parent_payload=json.loads(row['payload_json']) if row else {}
        payload={"base":parent_payload,"delta":delta}
        vid=version_id(oid,payload,current); ver=self.s.put_version(vid,oid,current,payload,status)
        ep={"operation":"COMMIT_DELTA","oid":oid,"parent_vid":current,"vid":vid,"delta":delta}
        pe=head['eid'] if head else None; eid=event_id('COMMIT_DELTA',actor,pe,ep); ed=digest(ep,32)
        self.s.put_event(eid,'COMMIT_DELTA',actor,pe,ep,ed)
        if move_head:
            self.s.set_head(f"object:{oid}",oid,vid,eid,ed); self.s.set_head('global',oid,vid,eid,ed)
        return {"status":"COMMITTED","version":ver,"event":eid,"head_moved":move_head}
    def ingest_text(self, oid, expected_vid, text, native_locator, carrier='text/plain', actor='agent'):
        head=self.s.head(f"object:{oid}"); current=head['vid'] if head else None
        if current != expected_vid: raise StaleTarget(json.dumps({"status":"STALE_TARGET","expected":expected_vid,"current":current,"oid":oid}))
        content_digest=hashlib.sha256(text.encode()).hexdigest()
        payload={"content_digest":content_digest,"native_locator":native_locator,"carrier":carrier,"chars":len(text)}
        result=self.commit_delta(oid,expected_vid,payload,actor=actor,status='TESTED')
        vid=result['version']['vid']; obj=self.s.one("SELECT canonical_name FROM objects WHERE oid=?",(oid,))
        mid=manifestation_id(vid,carrier,native_locator,content_digest)
        self.s.put_manifestation(mid,vid,carrier,native_locator,content_digest,text)
        toks=coordinate_text(text,oid,vid,mid,obj['canonical_name']); self.s.put_tokens(mid,toks)
        result.update({"mid":mid,"content_digest":content_digest,"token_count":len(toks),"first_coordinate":toks[0]['coordinate'] if toks else None,"last_coordinate":toks[-1]['coordinate'] if toks else None})
        return result
    def navigate(self, ident):
        obj=self.s.one("SELECT * FROM objects WHERE oid=? OR cid=? OR canonical_name=?",(ident,ident,ident))
        if not obj: return {"found":False,"query":ident}
        oid=obj['oid']; head=self.s.head(f"object:{oid}");
        return {"found":True,"object":obj,"head":head,"outgoing":self.s.rows("SELECT * FROM edges WHERE src=?",(oid,)),"incoming":self.s.rows("SELECT * FROM edges WHERE dst=?",(oid,)),"versions":self.s.rows("SELECT vid,parent_vid,status,created_at FROM versions WHERE oid=? ORDER BY created_at",(oid,)),"kc144":station(stable_gid(obj['canonical_name'])).__dict__}
    def add_edge(self,src,relation,dst,actor='agent',attrs=None):
        attrs=attrs or {}; parent=self.s.head('global'); pe=parent['eid'] if parent else None
        ep={"src":src,"relation":relation,"dst":dst,"attrs":attrs}; eid=event_id('EDGE',actor,pe,ep); ed=digest(ep,32)
        self.s.put_event(eid,'EDGE',actor,pe,ep,ed); edge_id="EDGE."+digest(ep,20); self.s.put_edge(edge_id,src,relation,dst,eid,attrs); self.s.set_head('global',None,None,eid,ed)
        return {"edge_id":edge_id,"event":eid}
    def emit_agent_event(self,p):
        required=['agent','task','seq','intent','action','status']
        miss=[x for x in required if x not in p]
        if miss: raise ValueError(f"missing {miss}")
        parent=self.s.head('global'); pe=parent['eid'] if parent else None
        eid=event_id('AGENT_EVENT',p['agent'],pe,p); ed=digest(p,32)
        self.s.put_event(eid,'AGENT_EVENT',p['agent'],pe,p,ed); self.s.put_agent_event(eid,p); self.s.set_head('global',None,None,eid,ed)
        return {"eid":eid,"liminal_coordinate":f"LIMINAL/{p['agent']}/{p['task']}/SEQ:{int(p['seq']):06d}","jspace_node":eid,"scale":"S0:RAW_EVENT"}
    def help_matches(self,agent,limit=10):
        rows=self.s.rows("SELECT agent,payload_json FROM agent_events WHERE agent<>? ORDER BY created_at DESC LIMIT 200",(agent,))
        me=self.s.one("SELECT payload_json FROM agent_events WHERE agent=? ORDER BY created_at DESC",(agent,));
        if not me:return []
        mp=json.loads(me['payload_json']); needs=set(map(str.upper,mp.get('needs',[])+mp.get('blockers',[])))
        scores=[]
        for r in rows:
            p=json.loads(r['payload_json']); offers=set(map(str.upper,p.get('offers',[])+p.get('capability_delta',[])))
            score=len(needs & offers)
            if score:scores.append({"agent":r['agent'],"score":score,"matches":sorted(needs&offers)})
        best={}
        for x in scores:
            if x['agent'] not in best or x['score']>best[x['agent']]['score']: best[x['agent']]=x
        return sorted(best.values(),key=lambda x:(-x['score'],x['agent']))[:limit]
    def form_simplex(self,participants,task,topic,packet_refs=None):
        p=sorted(set(participants)); n=len(p)
        if n<2: raise ValueError('need at least 2 participants')
        sid="SIMPLEX."+digest({"participants":p,"task":task,"topic":topic},20)
        return {"simplex_id":sid,"arity":n,"dimension":n-1,"participants":p,"task":task,"topic":topic,"packet_refs":packet_refs or [],"face_policy":"LAZY","proper_face_count":2**n-2 if n<=60 else "UNMATERIALIZED"}
    def promote_mutation(self,mutation_class,payload,source_eid,actor='agent'):
        cls=mutation_class.upper(); mid="MUT."+digest({"class":cls,"payload":payload,"source":source_eid},20)
        with self.s.db:
            self.s.db.execute("INSERT OR IGNORE INTO mutations VALUES(?,?,?,?,?,?)",(mid,cls,json.dumps(payload,sort_keys=True),source_eid,1 if cls in GLOBAL_CLASSES else 0,time.time()))
        return {"mutation_id":mid,"class":cls,"global_required":cls in GLOBAL_CLASSES}
    def pending_mutations(self,agent):
        return self.s.rows("SELECT m.* FROM mutations m LEFT JOIN adoptions a ON a.mutation_id=m.mutation_id AND a.agent=? WHERE a.mutation_id IS NULL ORDER BY m.created_at",(agent,))
    def adopt_mutation(self,agent,mutation_id):
        m=self.s.one("SELECT * FROM mutations WHERE mutation_id=?",(mutation_id,));
        if not m: raise KeyError('unknown mutation')
        p={"agent":agent,"mutation_id":mutation_id,"class":m['class']}; parent=self.s.head('global'); pe=parent['eid'] if parent else None
        eid=event_id('ADOPT_MUTATION',agent,pe,p); ed=digest(p,32); self.s.put_event(eid,'ADOPT_MUTATION',agent,pe,p,ed)
        with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO adoptions VALUES(?,?,?,?)",(mutation_id,agent,eid,time.time()))
        self.s.set_head('global',None,None,eid,ed); return {"status":"ADOPTED","eid":eid}
    def hydrate(self,agent=None):
        return {"global_head":self.s.head('global'),"objects":self.s.rows("SELECT oid,cid,canonical_name,kind,domain FROM objects ORDER BY canonical_name"),"recent_events":self.s.rows("SELECT eid,event_type,actor,parent_eid,digest,created_at FROM events ORDER BY created_at DESC LIMIT 50"),"pending_mutations":self.pending_mutations(agent) if agent else [],"scale_levels":SCALE_LEVELS,"kc144":{"topology":"12x12","stations":144},"jspace":{"nodes":self.s.one("SELECT COUNT(*) n FROM objects")['n'],"edges":self.s.one("SELECT COUNT(*) n FROM edges")['n']}}
    def session_start(self, agent, task, git_head=None):
        payload={"agent":agent,"task":task,"git_head":git_head}
        parent=self.s.head('global'); pe=parent['eid'] if parent else None
        eid=event_id('SESSION_START',agent,pe,payload); ed=digest(payload,32)
        self.s.put_event(eid,'SESSION_START',agent,pe,payload,ed); self.s.set_head('global',None,None,eid,ed)
        sid="SESSION."+digest({"agent":agent,"task":task,"start":eid},20)
        with self.s.db:self.s.db.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?,?,?)",(sid,agent,task,eid,git_head,time.time(),None,None,None,'OPEN'))
        return {"session_id":sid,"start_eid":eid,"git_head":git_head,"hydrate":self.hydrate(agent)}
    def session_end(self, session_id, summary, git_head=None):
        row=self.s.one("SELECT * FROM sessions WHERE session_id=?",(session_id,))
        if not row: raise KeyError('unknown session')
        if row['status']!='OPEN': raise ValueError('session already closed')
        payload={"session_id":session_id,"agent":row['agent'],"task":row['task'],"summary":summary,"git_head":git_head}
        parent=self.s.head('global'); pe=parent['eid'] if parent else None
        eid=event_id('SESSION_END',row['agent'],pe,payload); ed=digest(payload,32)
        self.s.put_event(eid,'SESSION_END',row['agent'],pe,payload,ed); self.s.set_head('global',None,None,eid,ed)
        with self.s.db:self.s.db.execute("UPDATE sessions SET end_eid=?,end_git_head=?,end_time=?,status='CLOSED' WHERE session_id=?",(eid,git_head,time.time(),session_id))
        return {"session_id":session_id,"end_eid":eid,"summary":summary}
    def event(self,eid):
        r=self.s.one("SELECT * FROM events WHERE eid=?",(eid,))
        if r and 'payload_json' in r:r['payload']=json.loads(r.pop('payload_json'))
        return r
    def benchmark(self):
        q=lambda table:self.s.one(f"SELECT COUNT(*) n FROM {table}")['n']
        stale=0
        return {"objects":q('objects'),"versions":q('versions'),"events":q('events'),"edges":q('edges'),"manifestations":q('manifestations'),"tokens":q('tokens'),"agent_events":q('agent_events'),"mutations":q('mutations'),"adoptions":q('adoptions'),"stale_reject_metric":"instrumented_by_exception","global_head":self.s.head('global')}

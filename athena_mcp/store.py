from __future__ import annotations
import json, sqlite3, threading, time, hashlib
from pathlib import Path

SCHEMA='''
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS objects(
 oid TEXT PRIMARY KEY,cid TEXT UNIQUE NOT NULL,canonical_name TEXT UNIQUE NOT NULL,kind TEXT NOT NULL,
 domain TEXT NOT NULL,verb TEXT NOT NULL,object_name TEXT NOT NULL,method TEXT NOT NULL,signature_json TEXT NOT NULL,
 created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS versions(
 vid TEXT PRIMARY KEY,oid TEXT NOT NULL,parent_vid TEXT,payload_json TEXT NOT NULL,payload_digest TEXT NOT NULL,
 status TEXT NOT NULL,created_at REAL NOT NULL,FOREIGN KEY(oid) REFERENCES objects(oid));
CREATE TABLE IF NOT EXISTS heads(scope TEXT PRIMARY KEY,oid TEXT,vid TEXT,eid TEXT,digest TEXT,updated_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS manifestations(
 mid TEXT PRIMARY KEY,vid TEXT NOT NULL,carrier TEXT NOT NULL,native_locator TEXT NOT NULL,content_digest TEXT NOT NULL,
 content TEXT,created_at REAL NOT NULL,FOREIGN KEY(vid) REFERENCES versions(vid));
CREATE TABLE IF NOT EXISTS tokens(
 mid TEXT NOT NULL,ordinal INTEGER NOT NULL,token TEXT NOT NULL,char_start INTEGER NOT NULL,char_end INTEGER NOT NULL,
 paragraph INTEGER NOT NULL,sentence INTEGER NOT NULL,coordinate TEXT NOT NULL,gid INTEGER NOT NULL,row INTEGER NOT NULL,col INTEGER NOT NULL,
 band TEXT NOT NULL,PRIMARY KEY(mid,ordinal),FOREIGN KEY(mid) REFERENCES manifestations(mid));
CREATE TABLE IF NOT EXISTS events(
 eid TEXT PRIMARY KEY,event_type TEXT NOT NULL,actor TEXT NOT NULL,parent_eid TEXT,payload_json TEXT NOT NULL,digest TEXT NOT NULL,
 created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS edges(
 edge_id TEXT PRIMARY KEY,src TEXT NOT NULL,relation TEXT NOT NULL,dst TEXT NOT NULL,eid TEXT NOT NULL,attrs_json TEXT NOT NULL,
 created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS agent_events(
 eid TEXT PRIMARY KEY,agent TEXT NOT NULL,task TEXT NOT NULL,seq INTEGER NOT NULL,intent TEXT,action TEXT,status TEXT,
 progress REAL,pressure REAL,uncertainty REAL,payload_json TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS mutations(
 mutation_id TEXT PRIMARY KEY,class TEXT NOT NULL,payload_json TEXT NOT NULL,source_eid TEXT NOT NULL,global_required INTEGER NOT NULL,
 created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS adoptions(
 mutation_id TEXT NOT NULL,agent TEXT NOT NULL,adopted_eid TEXT NOT NULL,created_at REAL NOT NULL,
 PRIMARY KEY(mutation_id,agent));
CREATE TABLE IF NOT EXISTS sessions(
 session_id TEXT PRIMARY KEY,agent TEXT NOT NULL,task TEXT NOT NULL,start_eid TEXT NOT NULL,start_git_head TEXT,start_time REAL NOT NULL,end_eid TEXT,end_git_head TEXT,end_time REAL,status TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_objects_kind_domain ON objects(kind,domain);
CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src); CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);
CREATE INDEX IF NOT EXISTS idx_tokens_coord ON tokens(coordinate);
'''

class Store:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self._lock=threading.RLock(); self.db=sqlite3.connect(str(self.path),check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        with self.db: self.db.executescript(SCHEMA)
    def close(self): self.db.close()
    def rows(self,sql,args=()): return [dict(r) for r in self.db.execute(sql,args).fetchall()]
    def one(self,sql,args=()):
        r=self.db.execute(sql,args).fetchone(); return dict(r) if r else None
    def put_object(self, rec):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO objects VALUES(?,?,?,?,?,?,?,?,?,?)",
                (rec['oid'],rec['cid'],rec['canonical_name'],rec['kind'],rec['domain'],rec['verb'],rec['object'],rec['method'],json.dumps(rec['signature'],sort_keys=True),time.time()))
        return self.one("SELECT * FROM objects WHERE cid=?",(rec['cid'],))
    def put_version(self, vid, oid, parent_vid, payload, status='CANDIDATE'):
        pj=json.dumps(payload,sort_keys=True,ensure_ascii=False); pd=hashlib.sha256(pj.encode()).hexdigest()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO versions VALUES(?,?,?,?,?,?,?)",(vid,oid,parent_vid,pj,pd,status,time.time()))
        return self.one("SELECT * FROM versions WHERE vid=?",(vid,))
    def head(self,scope='global'): return self.one("SELECT * FROM heads WHERE scope=?",(scope,))
    def set_head(self,scope,oid,vid,eid,digest):
        now=time.time()
        with self.db:
            self.db.execute("INSERT INTO heads VALUES(?,?,?,?,?,?) ON CONFLICT(scope) DO UPDATE SET oid=excluded.oid,vid=excluded.vid,eid=excluded.eid,digest=excluded.digest,updated_at=excluded.updated_at",(scope,oid,vid,eid,digest,now))
    def put_event(self,eid,event_type,actor,parent_eid,payload,digest):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO events VALUES(?,?,?,?,?,?,?)",(eid,event_type,actor,parent_eid,json.dumps(payload,sort_keys=True,ensure_ascii=False),digest,time.time()))
        return self.one("SELECT * FROM events WHERE eid=?",(eid,))
    def put_manifestation(self,mid,vid,carrier,locator,content_digest,content):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO manifestations VALUES(?,?,?,?,?,?,?)",(mid,vid,carrier,locator,content_digest,content,time.time()))
    def put_tokens(self,mid,tokens):
        with self.db:
            self.db.executemany("INSERT OR REPLACE INTO tokens VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",[
                (mid,t['ordinal'],t['token'],t['char_start'],t['char_end'],t['paragraph'],t['sentence'],t['coordinate'],t['gid'],t['row'],t['col'],t['band']) for t in tokens])
    def put_edge(self,edge_id,src,relation,dst,eid,attrs):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO edges VALUES(?,?,?,?,?,?,?)",(edge_id,src,relation,dst,eid,json.dumps(attrs,sort_keys=True),time.time()))
    def put_agent_event(self,eid,p):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO agent_events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (eid,p['agent'],p.get('task',''),int(p.get('seq',0)),p.get('intent',''),p.get('action',''),p.get('status',''),float(p.get('progress',0)),float(p.get('pressure',0)),float(p.get('uncertainty',0)),json.dumps(p,sort_keys=True,ensure_ascii=False),time.time()))
    def search(self,q,limit=20):
        like=f"%{q}%"
        objs=self.rows("SELECT oid,cid,canonical_name,kind,domain,verb,object_name,method FROM objects WHERE canonical_name LIKE ? OR signature_json LIKE ? LIMIT ?",(like,like,limit))
        return objs

"""KC144 v1.3 compact federated mycelium harness for the live MCP server.

Navigation and local replay have truth_effect=NONE and preserve E=<0,86,0,1,0>.
"""
from __future__ import annotations
import collections, hashlib, json, re, sqlite3, zipfile
from pathlib import Path
from typing import Any, Iterable
from kc144_meta_v12 import compile_query, compress_seed, reconstruct_seed, pareto_route, route

VERSION="1.3.0"
ADDRESS="amc://github/kc144-federated-harness/kc144-federated-harness@1.3.0?lens=10#tool"
E=(0,86,0,1,0)
HARNESS_MAPS=(
 "artifact-occurrence","artifact-version-lineage","container-topology","source-fiber",
 "claim-evidence-fiber","tool-capability","harness-action-dag","harness-run-ledger",
 "cross-synthesis-consensus","cross-synthesis-defect","cover-overlap","holonomy-defect",
 "depth-lattice","tunnel-nexus","replay-causality","content-addressable-store",
 "negative-knowledge","hydration-frontier",
)
TOOLS=("KC144.META.COMPILER","KC144.FEDERATED.HARNESS","KC144.ARTIFACT.SHADOW","KC144.SOURCE.FIBER","KC144.CROSS.SYNTHESIS","KC144.DEPTH.CALCULUS")

def digest(value:Any)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def file_sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1<<20),b""):h.update(block)
 return h.hexdigest()
def norm_name(name:str)->str:
 stem=Path(name).stem.lower();stem=re.sub(r"(?:[-_. ]v?(?:ersion)?\d+(?:\.\d+)*)+$","",stem);return re.sub(r"[^a-z0-9]+","-",stem).strip("-") or stem
def classify(path:Path)->str:
 ext=path.suffix.lower()
 if ext in {".zip",".whl",".pyz"}:return "BUNDLE_OR_CONTAINER"
 if ext in {".json",".jsonl",".csv",".yaml",".yml",".toml"}:return "REGISTRY_OR_DATA"
 if ext in {".py",".js",".ts",".rs",".go",".c",".cpp",".h"}:return "CODE_BODY"
 return "DOCUMENT_BODY"
def body(path:Path,limit:int=300_000)->tuple[str|None,str|None]:
 ext=path.suffix.lower()
 try:
  if ext==".docx":
   import xml.etree.ElementTree as ET
   with zipfile.ZipFile(path) as z:raw=z.read("word/document.xml")
   root=ET.fromstring(raw);return " ".join((x.text or "") for x in root.iter() if x.tag.endswith("}t"))[:limit],None
  if ext in {".zip",".whl",".pyz"}:
   rows=[]
   with zipfile.ZipFile(path) as z:
    for info in z.infolist()[:1000]:
     rows.append(f"{info.filename}\t{info.file_size}")
     if info.file_size<=80_000 and Path(info.filename).suffix.lower() in {".md",".txt",".json",".py",".toml"}:
      try:rows.append(z.read(info).decode("utf-8")[:4000])
      except Exception:pass
   return "\n".join(rows)[:limit],None
  return path.read_text(encoding="utf-8",errors="replace")[:limit],None
 except Exception as exc:return None,f"{type(exc).__name__}: {exc}"
def shadow(path:str|Path)->dict[str,Any]:
 p=Path(path).expanduser().resolve();st=p.stat();sha=file_sha(p);occurrence=hashlib.sha256(f"{p}|{st.st_dev}|{st.st_ino}".encode()).hexdigest();version=hashlib.sha256(f"{sha}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest();text,error=body(p)
 return {"aid":"AID."+sha[:24],"occurrence_id":"OID."+occurrence[:24],"version_id":"VID."+version[:24],"name":p.name,"normalized_name":norm_name(p.name),"path":str(p),"locator":p.as_uri(),"media_type":p.suffix.lower(),"source_class":classify(p),"content_sha256":sha,"bytes":st.st_size,"modified_ns":st.st_mtime_ns,"body_available":text is not None,"body":text,"error":error,"truth_effect":"NONE"}
def scan(paths:Iterable[str|Path],recursive:bool=True,max_files:int=20000)->dict[str,Any]:
 candidates=[]
 for raw in paths:
  p=Path(raw).expanduser()
  if p.is_file():candidates.append(p)
  elif p.is_dir():candidates.extend(x for x in (p.rglob("*") if recursive else p.glob("*")) if x.is_file() and ".git" not in x.parts and "__pycache__" not in x.parts)
 rows=[];errors=[]
 for p in sorted(set(candidates),key=lambda x:str(x))[:max_files]:
  try:rows.append(shadow(p))
  except Exception as exc:errors.append({"path":str(p),"error":f"{type(exc).__name__}: {exc}"})
 by_sha=collections.defaultdict(list);by_name=collections.defaultdict(list)
 for x in rows:by_sha[x["content_sha256"]].append(x["occurrence_id"]);by_name[x["normalized_name"]].append(x["version_id"])
 registry={"schema":"KC144-ARTIFACT-SHADOW-REGISTRY-1.3","artifacts":[{k:v for k,v in x.items() if k!="body"} for x in rows],"count":len(rows),"body_count":sum(x["body_available"] for x in rows),"duplicate_content_classes":[{"content_sha256":k,"occurrences":v} for k,v in sorted(by_sha.items()) if len(v)>1],"divergent_name_classes":[{"normalized_name":k,"versions":sorted(set(v))} for k,v in sorted(by_name.items()) if len(set(v))>1],"errors":errors,"truth_effect":"NONE"};registry["registry_digest"]=digest(registry)
 return {"registry":registry,"bodies":{x["occurrence_id"]:x["body"] for x in rows if x["body_available"]}}

class Store:
 def __init__(self,path:str|Path=":memory:"):
  self.db=sqlite3.connect(str(path));self.db.row_factory=sqlite3.Row;self.db.executescript("CREATE TABLE IF NOT EXISTS artifacts(oid TEXT PRIMARY KEY,aid TEXT,vid TEXT,name TEXT,normalized_name TEXT,path TEXT,sha TEXT,body TEXT,data TEXT);CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY,query TEXT,data TEXT);CREATE TABLE IF NOT EXISTS ledger(seq INTEGER PRIMARY KEY,prev TEXT,event_hash TEXT,kind TEXT,refs TEXT,payload TEXT);");self.db.commit()
 def ingest(self,result:dict[str,Any])->dict[str,Any]:
  with self.db:
   for x in result["registry"]["artifacts"]:self.db.execute("INSERT OR REPLACE INTO artifacts VALUES(?,?,?,?,?,?,?,?,?)",(x["occurrence_id"],x["aid"],x["version_id"],x["name"],x["normalized_name"],x["path"],x["content_sha256"],result["bodies"].get(x["occurrence_id"]),json.dumps(x,sort_keys=True)))
  return {"artifacts":self.db.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]}
 def artifacts(self)->list[dict[str,Any]]:return [json.loads(r[0])|{"body":r[1]} for r in self.db.execute("SELECT data,body FROM artifacts ORDER BY oid")]
 def search(self,q:str,limit:int=24)->list[dict[str,Any]]:
  tokens=[x for x in re.findall(r"[a-z0-9]+",q.lower()) if len(x)>2];out=[]
  for x in self.artifacts():
   hay=(json.dumps(x,ensure_ascii=False)+" "+(x.get("body") or "")).lower();score=sum(hay.count(t) for t in tokens)
   if score:out.append({"score":score,**{k:v for k,v in x.items() if k!="body"}})
  return sorted(out,key=lambda x:(-x["score"],x["occurrence_id"]))[:limit]
 def save_run(self,run:dict[str,Any]):
  with self.db:self.db.execute("INSERT OR REPLACE INTO runs VALUES(?,?,?)",(run["run_id"],run["query"],json.dumps(run,sort_keys=True)))
 def load_run(self,run_id:str)->dict[str,Any]:
  row=self.db.execute("SELECT data FROM runs WHERE run_id=?",(run_id,)).fetchone()
  if not row:raise KeyError(run_id)
  return json.loads(row[0])
 def append(self,kind:str,refs:list[str],payload:dict[str,Any])->dict[str,Any]:
  row=self.db.execute("SELECT seq,event_hash FROM ledger ORDER BY seq DESC LIMIT 1").fetchone();seq=row[0]+1 if row else 1;prev=row[1] if row else "0"*64;material={"seq":seq,"prev":prev,"kind":kind,"refs":refs,"payload":payload};eh=digest(material)
  with self.db:self.db.execute("INSERT INTO ledger VALUES(?,?,?,?,?,?)",(seq,prev,eh,kind,json.dumps(refs),json.dumps(payload,sort_keys=True)))
  return material|{"event_hash":eh}
 def verify(self)->dict[str,Any]:
  prev="0"*64;errors=[]
  for r in self.db.execute("SELECT * FROM ledger ORDER BY seq"):
   material={"seq":r["seq"],"prev":r["prev"],"kind":r["kind"],"refs":json.loads(r["refs"]),"payload":json.loads(r["payload"])}
   if r["prev"]!=prev or digest(material)!=r["event_hash"]:errors.append(r["seq"])
   prev=r["event_hash"]
  return {"pass":not errors,"errors":errors,"head":prev}

def source_fiber(artifacts:list[dict[str,Any]])->dict[str,Any]:
 groups=collections.defaultdict(list)
 for x in artifacts:groups[x["normalized_name"]].append(x)
 resources=[];counts=collections.Counter()
 for name,rows in sorted(groups.items()):
  aids={x["aid"] for x in rows};vids={x["version_id"] for x in rows};bodies=sum(x["body_available"] for x in rows);state="CONSISTENT" if len(aids)==1 and bodies==len(rows) else "PARTIAL" if bodies<len(rows) else "DIVERGED" if len(vids)>1 else "UNRESOLVED";counts[state]+=1;resources.append({"resource":name,"state":state,"occurrences":[x["occurrence_id"] for x in rows],"aids":sorted(aids),"versions":sorted(vids)})
 out={"schema":"KC144-SOURCE-FIBER-1.3","resources":resources,"state_counts":dict(counts),"truth_effect":"NONE"};out["digest"]=digest(out);return out
def depth(max_depth:int=12)->dict[str,Any]:return {"schema":"KC144-DEPTH-CALCULUS-1.3","laws":{"BR(n)":"1 + 20·4^n","KC(n)":"27^(n+1)","A(n)":"360·10^n"},"rows":[{"depth":n,"br":1+20*4**n,"kc":27**(n+1),"angle":360*10**n} for n in range(max_depth+1)],"truth_effect":"NONE"}
def tunnel(system:str,address:dict[str,Any],target_depth:int,child_digit:int=0)->dict[str,Any]:
 system=system.upper();trace=[]
 if system=="KC":
  ds=list(address["digits"])
  while len(ds)-1<target_depth:ds.append(child_digit%27);trace.append(list(ds))
  while len(ds)-1>target_depth:ds.pop();trace.append(list(ds))
  output={"digits":ds,"depth":len(ds)-1}
 elif system=="BR":
  path=list(address.get("path",[]));sector=address.get("sector",address.get("target_sector",1))
  while len(path)<target_depth:path.append(child_digit%4);trace.append(list(path))
  while len(path)>target_depth:path.pop();trace.append(list(path))
  output={"sector":sector,"path":path,"depth":len(path)}
 elif system=="ANGLE":
  tick=int(address["tick"]);zoom=int(address["zoom"])
  while zoom<target_depth:tick=tick*10+child_digit%10;zoom+=1;trace.append({"tick":tick,"zoom":zoom})
  while zoom>target_depth:tick//=10;zoom-=1;trace.append({"tick":tick,"zoom":zoom})
  output={"tick":tick,"zoom":zoom,"degrees":tick/10**zoom}
 else:raise KeyError(system)
 out={"system":system,"input":address,"target_depth":target_depth,"trace":trace,"output":output,"truth_effect":"NONE"};out["receipt"]=digest(out);return out

def synthesis(query:str,compiled:dict[str,Any],hits:list[dict[str,Any]],artifacts:list[dict[str,Any]],maps:list[str])->dict[str,Any]:
 votes=collections.Counter(x["gid"] for x in compiled["candidates"])
 for hit in hits:
  text=(hit["name"]+" "+hit["path"]).lower()
  for word,g in (("quaternion",49),("branch",50),("proof",89),("compress",119),("return",144),("source",5),("artifact",133)):votes[g]+=1+hit["score"]
 ranked=[{"gid":g,"score":s} for g,s in votes.most_common(24)];bodies=sum(x["body_available"] for x in artifacts);coverage=bodies/len(artifacts) if artifacts else 0
 out={"schema":"KC144-CROSS-SYNTHESIS-1.3","query":query,"ranked_stations":ranked,"maps":sorted(set(maps+compiled.get("maps",[])+list(HARNESS_MAPS))),"artifact_hits":hits,"diagnostics":{"artifact_body_coverage":coverage,"projection_count":len(compiled["candidates"])+len(hits)},"claim_ceiling":"SOURCE_BOUND_SYNTHESIS" if hits else "STRUCTURAL_SYNTHESIS","truth_effect":"NONE"};out["digest"]=digest(out);return out

def merkle(leaves:list[dict[str,Any]])->str:
 level=[bytes.fromhex(digest(x)) for x in leaves] or [hashlib.sha256(b"").digest()]
 while len(level)>1:
  if len(level)%2:level.append(level[-1])
  level=[hashlib.sha256(level[i]+level[i+1]).digest() for i in range(0,len(level),2)]
 return level[0].hex()
def federated_seed(query:str,core:dict[str,Any],syn:dict[str,Any],fiber:dict[str,Any],artifacts:list[dict[str,Any]])->dict[str,Any]:
 leaves=[{"aid":x["aid"],"oid":x["occurrence_id"],"vid":x["version_id"],"sha256":x["content_sha256"]} for x in artifacts];out={"schema":"KC144-FEDERATED-HOLOGRAPHIC-SEED-1.3","version":VERSION,"query_sha256":hashlib.sha256(query.encode()).hexdigest(),"core_seed":core,"cross_synthesis_digest":syn["digest"],"source_fiber_digest":fiber["digest"],"artifact_leaves":leaves,"artifact_merkle_root":merkle(leaves),"return_station":"M12","claim_ceiling":"NAVIGATION_AND_SOURCE_BINDING_ONLY","truth_effect":"NONE"};out["seed_id"]="FHS."+digest(out)[:24];out["digest"]=digest(out);return out
def verify_seed(seed:dict[str,Any])->dict[str,Any]:
 material={k:v for k,v in seed.items() if k!="digest"}
 if digest(material)!=seed["digest"]:raise ValueError("seed digest")
 if merkle(seed["artifact_leaves"])!=seed["artifact_merkle_root"]:raise ValueError("artifact Merkle")
 core=reconstruct_seed(seed["core_seed"]);return {"verified":True,"seed_id":seed["seed_id"],"core_station_count":len(core["gids"]),"return_station":"M12","truth_effect":"NONE"}

class Harness:
 def __init__(self,store_path:str|Path=":memory:"):self.store=Store(store_path);self.last=None
 def run(self,query:str,paths:Iterable[str|Path]=(),maps:list[str]|None=None)->dict[str,Any]:
  compiled=compile_query(query);scanned=scan(paths);self.store.ingest(scanned);arts=self.store.artifacts();hits=self.store.search(query);fiber=source_fiber(arts);syn=synthesis(query,compiled,hits,arts,maps or []);gids=[x["gid"] for x in syn["ranked_stations"]] or [119];core=compress_seed(gids,syn["maps"],"FEDERATED-HARNESS");seed=federated_seed(query,core,syn,fiber,[x for x in arts if any(h["aid"]==x["aid"] for h in hits)]);replay=verify_seed(seed);material={"query":query,"registry":scanned["registry"]["registry_digest"],"fiber":fiber["digest"],"synthesis":syn["digest"],"seed":seed["digest"],"E":E};run_id="RUN."+digest(material)[:24]
  run={"schema":"KC144-FEDERATED-MYCELIUM-HARNESS-RUN-1.3","run_id":run_id,"query":query,"artifact_registry":scanned["registry"],"source_fiber":fiber,"cross_synthesis":syn,"route_frontier":pareto_route(6,gids[0]),"return_route":route(gids[0],144,"return"),"depth_calculus":depth(12),"federated_seed":seed,"replay":replay,"merge_receipt":digest(material),"return_packet":{"station":"M12","run_id":run_id,"seed_id":seed["seed_id"],"production_evidence":list(E),"i10_receipt":None,"authority_effect":"NONE","truth_effect":"NONE"}}
  self.store.save_run(run);event=self.store.append("FEDERATED_HARNESS_RETURN",[run_id,seed["seed_id"],"M12"],{"merge_receipt":run["merge_receipt"],"production_evidence":list(E),"authority_effect":"NONE"});run["return_packet"]["ledger_event"]=event;self.store.save_run(run);self.last=run;return run
 def replay(self,run_id:str)->dict[str,Any]:
  run=self.store.load_run(run_id);seed=verify_seed(run["federated_seed"]);ledger=self.store.verify();return {"schema":"KC144-FEDERATED-HARNESS-REPLAY-1.3","run_id":run_id,"seed":seed,"ledger":ledger,"verified":seed["verified"] and ledger["pass"],"return_station":"M12","truth_effect":"NONE"}
 def status(self)->dict[str,Any]:return {"version":VERSION,"address":ADDRESS,"maps":72,"tools":list(TOOLS),"artifact_occurrences":len(self.store.artifacts()),"last_run":self.last["run_id"] if self.last else None,"production_evidence":list(E),"m12":"HOLD","i10_receipt":None,"qshrink":"NOT_REACHED","truth_effect":"NONE"}

def validate()->dict[str,Any]:
 failures=[]
 if len(HARNESS_MAPS)!=18:failures.append("harness_maps")
 if depth(3)["rows"][-1]["kc"]!=27**4:failures.append("depth")
 if tunnel("KC",{"digits":[13]},4,2)["output"]["depth"]!=4:failures.append("tunnel")
 return {"status":"PASS" if not failures else "FAIL","failures":failures,"maps":72,"tool_bus_organs":6,"production_evidence":list(E),"truth_effect":"NONE"}

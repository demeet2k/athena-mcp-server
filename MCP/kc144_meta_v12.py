"""KC144 v1.2 live calculus: coordinates, transforms, routing, seeds, parallel waves.
All operations are navigation-only and preserve E=<0,86,0,1,0>.
"""
from __future__ import annotations
import base64, collections, concurrent.futures, hashlib, heapq, json, math, re
from typing import Any
VERSION="1.2.0"; TOOL="KC144.META.COMPILER"; ADDRESS="amc://github/kc144/kc144-meta-compiler@1.2.0?lens=11#root"; E=(0,86,0,1,0)
BANDS=(("H6",1,6),("X16",7,22),("BR21",23,43),("F37",44,80),("IC10",81,90),("KC15",91,105),("KC27",106,132),("SSN12",133,144))
BASE=("coordinate-grid","band-partition","station-atlas","math144","dual-coordinate","metro","grid-geometry","mycelium","x16","br21-rails","br21-mirror","f37","ic10","kc15","kc27","ssn12","return-arm","returns","evidence-poset","status-space","claim-ceiling","authority-boundary","action-dag","workstreams","barrier-frontier","source-resolution","source-to-action","repo-federation","repo-planes","repo-collisions","provenance","query-compiler","engagement-pipeline","activation-wave","map-of-maps","cold-reentry","contradiction-quarantine")
ADV=("angle-360","octave-lift","d4-symmetry","ternary-translation","boolean-support-algebra","transform-calculus","nexus-hypergraph","pareto-routing","compression-seeds","reconstruction-coverage","parallel-wave-v2","cognitive-telemetry","coordinate-functor","map-overlap-matrix","holonomy-signatures","transformation-groupoid","merkle-return-tree")
MAPS=BASE+ADV
KEY={"address":1,"source":5,"activate":6,"admit":23,"navigate":29,"compress":38,"return":43,"quaternion":49,"branch":50,"jet":51,"math":71,"evidence":86,"proof":89,"promote":90,"support":105,"route":119,"qshrink":119,"codec":119,"quarantine":138,"defect":139,"repair":140,"replay":142,"successor":144,"m12":144}
MASKS={91:8,92:4,93:2,94:1,95:12,96:10,97:9,98:6,99:5,100:3,101:14,102:13,103:11,104:7,105:15}; BYMASK={v:k for k,v in MASKS.items()}
def grid(g:int)->tuple[int,int]:
 if not 1<=g<=144: raise ValueError("GID must be 1..144")
 return divmod(g-1,12)[0]+1,divmod(g-1,12)[1]+1
def gid(r:int,c:int)->int:
 if not(1<=r<=12 and 1<=c<=12): raise ValueError("grid must be 1..12")
 return 12*(r-1)+c
def band(g:int)->str:
 return next(b for b,a,z in BANDS if a<=g<=z)
def station(g:int)->dict[str,Any]:
 r,c=grid(g); b=band(g)
 if b=="H6": code=f"H{g:02d}"
 elif b=="X16": i=g-7; code=f"X-{('11','10','00','01')[i//4]}-{('SQ','FL','CL','FR')[i%4]}"
 elif b=="BR21": code=f"B{g-22:02d}"
 elif b=="F37": code=f"F{g-43:02d}"
 elif b=="IC10": code=f"I{g-80:02d}"
 elif b=="KC15": code=f"K{g-90:02d}"
 elif b=="KC27": code=f"P{g-106:02d}"
 else: code=f"M{g-132:02d}"
 return {"gid":g,"grid":f"R{r:02d}C{c:02d}","row":r,"column":c,"band":b,"station":code}
def resolve(x:str|int)->int:
 if isinstance(x,int): grid(x); return x
 k=str(x).strip().lower(); fixed={"h06":6,"m12":144,"p13":119,"i10":90,"root":1}
 if k in fixed:return fixed[k]
 m=re.fullmatch(r"(?:gid)?0*([1-9]\d{0,2})",k)
 if m:return resolve(int(m.group(1)))
 m=re.fullmatch(r"r(\d{1,2})c(\d{1,2})",k)
 if m:return gid(int(m.group(1)),int(m.group(2)))
 for g in range(1,145):
  s=station(g)
  if k in (s["grid"].lower(),s["station"].lower()):return g
 raise KeyError(x)
def coordinate(x:str|int,octave:int=0,zoom:int=0)->dict[str,Any]:
 g=resolve(x); s=station(g); theta=2.5*(g-1); local={"system":s["band"]}
 if s["band"]=="X16": i=g-7;local|={"pole":i//4,"lens":i%4}
 elif s["band"]=="BR21": i=g-23;local|={"family":i//3,"orientation":i%3}
 elif s["band"]=="KC15": local|={"mask":f"{MASKS[g]:04b}","support":MASKS[g].bit_count()}
 elif s["band"]=="KC27": n=g-106;local|={"x":n//9,"y":n//3%3,"z":n%3}
 else: local["index"]=g-next(a for b,a,z in BANDS if b==s["band"])+1
 return s|{"theta":theta,"octave":octave,"scale":2**octave,"zoom":zoom,"tick":round(theta*10**zoom),"circumference":360*10**zoom,"band_local":local,"address":f"KC144::GID{g:03d}::{s['grid']}::{s['band']}::{s['station']}"}
def _d4(r:int,c:int,rot:int=0,ref:bool=False)->tuple[int,int]:
 if ref:c=13-c
 for _ in range(rot%4):r,c=c,13-r
 return r,c
def transform(x:str|int,name:str,**p:Any)->dict[str,Any]:
 g=resolve(x); k=name.replace("_","-").lower(); out=g; inv=None
 d4={"grid-rotate-90":(1,0),"grid-rotate-180":(2,0),"grid-rotate-270":(3,0),"grid-reflect-vertical":(0,1),"grid-reflect-horizontal":(2,1),"grid-reflect-main":(3,1),"grid-reflect-anti":(1,1)}
 dinv={"grid-rotate-90":"grid-rotate-270","grid-rotate-180":"grid-rotate-180","grid-rotate-270":"grid-rotate-90","grid-reflect-vertical":"grid-reflect-vertical","grid-reflect-horizontal":"grid-reflect-horizontal","grid-reflect-main":"grid-reflect-main","grid-reflect-anti":"grid-reflect-anti"}
 if k in d4:
  r,c=grid(g); r,c=_d4(r,c,*d4[k]);out=gid(r,c);inv={"name":dinv[k]}
 elif k=="angle-shift": n=int(p.get("steps",0));out=(g-1+n)%144+1;inv={"name":k,"parameters":{"steps":-n}}
 elif k=="kc27-translate":
  if band(g)!="KC27":raise ValueError("KC27 only")
  n=g-106;x,y,z=n//9,n//3%3,n%3;dx,dy,dz=(int(p.get(q,0)) for q in("dx","dy","dz"));out=106+((x+dx)%3)*9+((y+dy)%3)*3+(z+dz)%3;inv={"name":k,"parameters":{"dx":-dx,"dy":-dy,"dz":-dz}}
 elif k=="kc15-xor":
  if band(g)!="KC15":raise ValueError("KC15 only")
  m=MASKS[g]^int(p.get("mask",0))
  if m==0:raise ValueError("empty support excluded")
  out=BYMASK[m];inv={"name":k,"parameters":{"mask":int(p.get("mask",0))}}
 elif k in("octave-jump","zoom-jump"):
  return {"input":coordinate(g,int(p.get("delta",0)) if k=="octave-jump" else 0,int(p.get("delta",0)) if k=="zoom-jump" else 0),"output_gid":g,"transform":k,"inverse":{"name":k,"parameters":{"delta":-int(p.get("delta",0))}},"truth_effect":"NONE"}
 else:raise KeyError(k)
 return {"input":coordinate(g),"output":coordinate(out),"output_gid":out,"transform":k,"parameters":p,"inverse":inv,"truth_effect":"NONE"}
def compose(x:str|int,specs:list[dict[str,Any]])->dict[str,Any]:
 cur=resolve(x);trace=[]
 for spec in specs:
  t=transform(cur,spec["name"],**spec.get("parameters",{}));trace.append(t);cur=t["output_gid"]
 return {"input_gid":resolve(x),"output_gid":cur,"trace":trace,"truth_effect":"NONE"}
def _graph()->dict[int,list[tuple[int,str,float]]]:
 a=collections.defaultdict(list)
 def e(x,y,l,w=1.0):a[x].append((y,l,w));a[y].append((x,l,w))
 for b,lo,hi in BANDS:
  for g in range(lo,hi):e(g,g+1,"native")
 for g in range(1,145):
  r,c=grid(g)
  if c<12:e(g,gid(r,c+1),"grid",1.2)
  if r<12:e(g,gid(r+1,c),"grid",1.2)
 for rail in range(3):
  ns=[23+rail+3*i for i in range(7)]
  for x,y in zip(ns,ns[1:]):e(x,y,"br21",.8)
 co={(n//9,n//3%3,n%3):106+n for n in range(27)}
 for q,g in co.items():
  for ax in range(3):
   if q[ax]<2:t=list(q);t[ax]+=1;e(g,co[tuple(t)],"kc27",.7)
 arm=(41,42,43,*range(81,91),119,144,1)
 for x,y in zip(arm,arm[1:]):e(x,y,"return",.5)
 return a
G=_graph()
def route(src:str|int,dst:str|int,objective:str="shortest")->dict[str,Any]:
 s,t=resolve(src),resolve(dst);q=[(0.0,s)];dist={s:0.0};par={s:None}
 while q:
  d,u=heapq.heappop(q)
  if u==t:break
  if d!=dist[u]:continue
  for v,l,w in G[u]:
   cost=1 if objective=="shortest" else w
   if d+cost<dist.get(v,1e99):dist[v]=d+cost;par[v]=(u,l,w);heapq.heappush(q,(d+cost,v))
 if t not in par:return {"status":"NO_ROUTE"}
 ns=[t];es=[]
 while ns[-1]!=s:u,l,w=par[ns[-1]];es.append({"from":u,"to":ns[-1],"layer":l,"weight":w});ns.append(u)
 ns.reverse();es.reverse();digest=hashlib.sha256(json.dumps(es,sort_keys=True).encode()).hexdigest()
 return {"status":"ROUTE_FOUND","objective":objective,"nodes":[station(g) for g in ns],"edges":es,"hops":len(es),"cost":dist[t],"digest":digest,"truth_effect":"NONE"}
def pareto_route(src:str|int,dst:str|int,limit:int=12)->dict[str,Any]:
 rows=[route(src,dst,o) for o in("shortest","preserve","return")];uniq={r.get("digest"):r for r in rows if r.get("status")=="ROUTE_FOUND"}
 return {"frontier":list(uniq.values())[:limit],"count":len(uniq),"truth_effect":"NONE"}
def _bits(gs:list[int])->bytes:
 n=0
 for g in gs:n|=1<<(g-1)
 return n.to_bytes(18,"little")
def _merkle(gs:list[int])->str:
 h=[hashlib.sha256(f"GID{g:03d}".encode()).digest() for g in gs]
 if not h:return hashlib.sha256(b"").hexdigest()
 while len(h)>1:
  if len(h)%2:h.append(h[-1])
  h=[hashlib.sha256(h[i]+h[i+1]).digest() for i in range(0,len(h),2)]
 return h[0].hex()
def compress_seed(addresses:list[str|int],maps:list[str]|None=None,label:str|None=None)->dict[str,Any]:
 gs=sorted({resolve(x) for x in addresses});material={"schema":"KC144-HOLOGRAPHIC-SEED-1.2","version":VERSION,"selector":base64.b64encode(_bits(gs)).decode(),"count":len(gs),"maps":sorted(set(maps or [])),"merkle_root":_merkle(gs),"return_station":"M12","claim_ceiling":"NAVIGATION_ONLY","truth_effect":"NONE","label":label};material["seed_id"]=hashlib.sha256(json.dumps(material,sort_keys=True).encode()).hexdigest()[:24];material["digest"]=hashlib.sha256(json.dumps(material,sort_keys=True).encode()).hexdigest();return material
def reconstruct_seed(seed:dict[str,Any])->dict[str,Any]:
 m=dict(seed);d=m.pop("digest")
 if hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()!=d:raise ValueError("seed digest mismatch")
 n=int.from_bytes(base64.b64decode(seed["selector"]),"little");gs=[i+1 for i in range(144) if n>>i&1]
 if _merkle(gs)!=seed["merkle_root"]:raise ValueError("Merkle mismatch")
 return {"gids":gs,"stations":[coordinate(g) for g in gs],"verified":True,"truth_effect":"NONE"}
def nexus(x:str|int|None=None,top:int=20)->dict[str,Any]:
 def member(name,g):
  ranges={"x16":(7,22),"br21-rails":(23,43),"f37":(44,80),"ic10":(81,90),"kc15":(91,105),"kc27":(106,132),"ssn12":(133,144)}
  return ranges.get(name,(1,144))[0]<=g<=ranges.get(name,(1,144))[1]
 if x is not None:
  g=resolve(x);ms=[m for m in MAPS if member(m,g)];return {"station":coordinate(g),"maps":ms,"degree":len(ms),"truth_effect":"NONE"}
 rows=sorted(((sum(member(m,g) for m in MAPS),g) for g in range(1,145)),reverse=True)
 return {"top":[{"gid":g,"degree":d} for d,g in rows[:top]],"truth_effect":"NONE"}
def locate(query:str="kc144")->dict[str,Any]:
 tok=set(re.findall(r"[a-z0-9]+",query.lower()));v=set(re.findall(r"[a-z0-9]+"," ".join(MAPS+(TOOL,"mental compiler","mycelium","holographic calculus")).lower()));hit=sorted(tok&v)
 return {"tool_found":bool(hit or not tok),"tool_id":TOOL,"version":VERSION,"address":ADDRESS,"matched":hit,"maps":list(MAPS),"capabilities":["compile","parallel","coordinate","transform","compose","route","pareto-route","nexus","compress","reconstruct","map","status","validate"],"truth_effect":"NONE"}
def compile_query(query:str)->dict[str,Any]:
 lo=query.lower();c=collections.Counter({g:sum(k in lo for k,x in KEY.items() if x==g) for g in set(KEY.values())});gs=[g for g,n in c.most_common() if n] or [119];p=gs[0]
 return {"schema":"KC144-COMPILE-1.2","query":query,"candidates":[coordinate(g) for g in gs],"activation":route(6,p,"preserve"),"return":route(p,144,"return"),"maps":["query-compiler","transform-calculus","nexus-hypergraph","compression-seeds"],"production_evidence":list(E),"truth_effect":"NONE"}
def parallel_wave(query:str,workers:int=8)->dict[str,Any]:
 c=compile_query(query);gs=[x["gid"] for x in c["candidates"]];p=gs[0];jobs={"coordinates":lambda:[coordinate(g) for g in gs],"routes":lambda:pareto_route(6,p),"nexus":lambda:nexus(p),"compression":lambda:compress_seed(gs,["parallel-wave-v2"],"QUERY"),"return":lambda:route(p,144,"return"),"status":status}
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:f={k:ex.submit(v) for k,v in jobs.items()};out={k:f[k].result() for k in sorted(f)}
 bands=collections.Counter(station(g)["band"] for g in gs);tot=sum(bands.values());ent=-sum((n/tot)*math.log2(n/tot) for n in bands.values()) if tot else 0;tele={"lanes":len(out),"candidates":len(gs),"band_entropy":ent,"observable_only":True};receipt=hashlib.sha256(json.dumps({"q":query,"g":gs,"t":tele,"e":E},sort_keys=True).encode()).hexdigest();return {"schema":"KC144-PARALLEL-WAVE-1.2","lanes":out,"telemetry":tele,"receipt":receipt,"return_station":"M12","production_evidence":list(E),"truth_effect":"NONE"}
def map_payload(name:str)->dict[str,Any]:
 k=name.lower()
 if k not in MAPS:
  m=[x for x in MAPS if k in x]
  if len(m)!=1:raise KeyError(name)
  k=m[0]
 out={"map":k,"truth_effect":"NONE"}
 if k in("coordinate-grid","station-atlas","math144","angle-360","coordinate-functor"):out["stations"]=[coordinate(g) for g in range(1,145)]
 elif k=="band-partition":out["bands"]=[{"band":b,"start":a,"end":z} for b,a,z in BANDS]
 elif k=="map-of-maps":out["maps"]=list(MAPS)
 elif k=="nexus-hypergraph":out|=nexus()
 elif k=="pareto-routing":out|=pareto_route(6,144)
 else:out["description"]=f"Executable {k} projection"
 return out
def status()->dict[str,Any]:return {"tool_id":TOOL,"version":VERSION,"address":ADDRESS,"stations":144,"maps":len(MAPS),"production_evidence":list(E),"m12":"HOLD","i10_receipt":None,"qshrink":"NOT_REACHED","truth_effect":"NONE"}
def validate()->dict[str,Any]:
 fail=[]
 if len(MAPS)!=54:fail.append("map_count")
 if len({station(g)["grid"] for g in range(1,145)})!=144:fail.append("grid")
 if route(6,144)["status"]!="ROUTE_FOUND":fail.append("route")
 s=compress_seed(list(range(1,145)))
 if reconstruct_seed(s)["gids"]!=list(range(1,145)):fail.append("seed")
 if parallel_wave("quaternion proof return",4)["receipt"]!=parallel_wave("quaternion proof return",4)["receipt"]:fail.append("parallel")
 return {"status":"PASS" if not fail else "FAIL","failures":fail,"maps":len(MAPS),"stations":144,"production_evidence":list(E)}
def dispatch(op:str,**kw:Any)->dict[str,Any]:
 op=op.replace("_","-").lower()
 return {"locate":lambda:locate(kw.get("query","kc144")),"compile":lambda:compile_query(kw.get("query","")),"parallel":lambda:parallel_wave(kw.get("query",""),int(kw.get("workers",8))),"coordinate":lambda:coordinate(kw.get("address",119),int(kw.get("octave",0)),int(kw.get("zoom",0))),"transform":lambda:transform(kw["address"],kw["transform"],**kw.get("parameters",{})),"compose":lambda:compose(kw["address"],kw["specs"]),"route":lambda:route(kw.get("source",6),kw.get("target",144),kw.get("objective","shortest")),"pareto-route":lambda:pareto_route(kw.get("source",6),kw.get("target",144),int(kw.get("limit",12))),"nexus":lambda:nexus(kw.get("address"),int(kw.get("top",20))),"compress":lambda:compress_seed(kw["addresses"],kw.get("maps"),kw.get("label")),"reconstruct":lambda:reconstruct_seed(kw["seed"]),"map":lambda:map_payload(kw.get("name","map-of-maps")),"status":status,"validate":validate}[op]()

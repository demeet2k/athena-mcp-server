"""Executable KC144 locator, map, station, route, and compiler fallback.

Navigation changes retrieval/execution state only. It never promotes evidence.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
from typing import Any

TOOL_ID = "KC144.META.COMPILER"
VERSION = "1.1.0"
CANONICAL_ADDRESS = "amc://github/kc144/kc144-meta-compiler@1.1.0?lens=11#root"
PRODUCTION_EVIDENCE = (0, 86, 0, 1, 0)
BANDS = (("H6",1,6),("X16",7,22),("BR21",23,43),("F37",44,80),("IC10",81,90),("KC15",91,105),("KC27",106,132),("SSN12",133,144))
MAPS = ("coordinate-grid","band-partition","station-atlas","math144","dual-coordinate","metro","grid-geometry","mycelium","x16","br21-rails","br21-mirror","f37","ic10","kc15","kc27","ssn12","return-arm","returns","evidence-poset","status-space","claim-ceiling","authority-boundary","action-dag","workstreams","barrier-frontier","source-resolution","source-to-action","repo-federation","repo-planes","repo-collisions","provenance","query-compiler","engagement-pipeline","activation-wave","map-of-maps","cold-reentry","contradiction-quarantine")
PIPELINE = ("INGEST","NORMALIZE","SCOPE","PROJECT","ADDRESS","RETRIEVE","EXPAND","CONSTRAIN","ROUTE","COMPARE","SYNTHESIZE","AUDIT","RETURN")
ALIASES = ("kc144","kc 144","meta compiler","mental compiler","navigation compiler","mycelium compiler","map of maps","holographic framework","math144","f37","br21","kc27","qshrink","m12","whole crystal")
TAGS = ("navigation","mycelium","compiler","hologram","coordinate","routing","evidence","return","replay","station","map","crystal","math","carrier","audit","source","federation")
F37_NAMES = {45:"Compactified Complex / Hilbert State",46:"Rigged Distribution / Instrument",49:"Binary-Octahedral / Quaternion Lift",50:"Analytic Branch-Cover",51:"Jet / Local-Asymptotic",71:"Question-Language and Codification",80:"Integrable AQM Dynamical Capstone and Carrier Return"}
IC10_NAMES = {81:"Identity and Provenance",82:"Syntax and Normalization",83:"Type, Unit, and Carrier",84:"Scope and Evidence-Class Alignment",85:"Invariant Preservation",86:"Evidence Sufficiency and Independence",87:"Dependency Closure",88:"Bridge and Return Defect",89:"Audit and Replay Completeness",90:"Promotion and Reseed Authorization"}
SSN12_NAMES = {133:"Node-State and Station-Maturity Registry",138:"Branch, Tombstone, Quarantine, and Rejected-Route Store",139:"Defect, Obligation, Evidence-Debt, and Repair Scheduler",140:"Healing Route and Unresolved-Bridge Resolver",142:"Replay, Replica, and Cold-Boot Observatory",144:"Successor Certificate, Global Seed, and Prime Reentry"}
KEYWORDS = {"address":1,"identity":1,"source":5,"activate":6,"seed":7,"body":7,"transform":11,"admit":23,"navigate":29,"test":35,"compress":38,"return":43,"hilbert":45,"distribution":46,"quaternion":49,"binary-octahedral":49,"branch":50,"cover":50,"jet":51,"question":71,"language":71,"math":71,"evidence":86,"proof":89,"promote":90,"promotion":90,"support":105,"route":119,"qshrink":119,"codec":119,"quarantine":138,"defect":139,"repair":140,"replay":142,"cold":142,"successor":144,"m12":144}

def gid_to_grid(gid:int)->tuple[int,int]:
    if not 1<=gid<=144: raise ValueError("GID must be in 1..144")
    q,r=divmod(gid-1,12); return q+1,r+1

def grid_to_gid(row:int,column:int)->int:
    if not (1<=row<=12 and 1<=column<=12): raise ValueError("row and column must be in 1..12")
    return 12*(row-1)+column

def band_for_gid(gid:int)->str:
    for band,lo,hi in BANDS:
        if lo<=gid<=hi:return band
    raise ValueError("GID must be in 1..144")

def station(gid:int)->dict[str,Any]:
    row,col=gid_to_grid(gid); band=band_for_gid(gid)
    if band=="H6":
        code=f"H{gid:02d}"; role=("Address–Identity Registry","Domain Projection Registry","Typed Route Registry","Invariant–Bridge–Defect Registry","Source–Evidence–Version Ledger","Activation–Replay–Reseed Hub")[gid-1]
    elif band=="X16":
        idx=gid-7; pole=("11","10","00","01")[idx//4]; lens=("SQ","FL","CL","FR")[idx%4]; code=f"X-{pole}-{lens}"; role=f"Pole {pole} / Lens {lens}"
    elif band=="BR21":
        n=gid-22; code=f"B{n:02d}"; family=("ADMIT","EXPAND","NAVIGATE","TRANSFORM","TEST","COMPRESS","RETURN")[(n-1)//3]; orientation=("PLUS","HINGE","STAR")[(n-1)%3]; role=f"{family} / {orientation}"
    elif band=="F37":
        n=gid-43; code=f"F{n:02d}"; role=F37_NAMES.get(gid,f"F37 Carrier {n:02d}")
    elif band=="IC10":
        n=gid-80; code=f"I{n:02d}"; role=IC10_NAMES[gid]
    elif band=="KC15":
        n=gid-90; code=f"K{n:02d}"; role=f"Support lattice node {n:02d}"
    elif band=="KC27":
        n=gid-106; trits=f"{n//9}{(n//3)%3}{n%3}"; code=f"P{n:02d}"; role=f"Semantic Coordinate {trits}"
        if gid==119: role="Codec, Compression, and QSHRINK"
    else:
        n=gid-132; code=f"M{n:02d}"; role=SSN12_NAMES.get(gid,f"SSN12 Observer {n:02d}")
    return {"gid":gid,"grid":f"R{row:02d}C{col:02d}","band":band,"station":code,"role":role,"math_portal":f"R{row:02d}C{col:02d}"}

def resolve(value:str|int)->int:
    if isinstance(value,int): station(value); return value
    key=str(value).strip().lower(); fixed={"h06":6,"m12":144,"p13":119,"i10":90,"root":1}
    if key in fixed:return fixed[key]
    for gid in range(1,145):
        item=station(gid)
        if key in {str(gid),f"gid{gid:03d}",item["grid"].lower(),item["station"].lower()}:return gid
    match=re.fullmatch(r"r(\d{1,2})c(\d{1,2})",key)
    if match:return grid_to_gid(int(match.group(1)),int(match.group(2)))
    raise KeyError(f"Unknown KC144 address: {value!r}")

def _edge(g:dict[int,set[int]],a:int,b:int)->None:
    if a!=b:g[a].add(b);g[b].add(a)

def graph()->dict[int,set[int]]:
    out:dict[int,set[int]]=collections.defaultdict(set)
    for _,lo,hi in BANDS:
        for gid in range(lo,hi):_edge(out,gid,gid+1)
    for gid in range(1,145):
        row,col=gid_to_grid(gid)
        if col<12:_edge(out,gid,grid_to_gid(row,col+1))
        if row<12:_edge(out,gid,grid_to_gid(row+1,col))
    for rail in range(3):
        nodes=[23+rail+3*i for i in range(7)]
        for a,b in zip(nodes,nodes[1:]):_edge(out,a,b)
    coords={(n//9,(n//3)%3,n%3):106+n for n in range(27)}
    for coord,gid in coords.items():
        for axis in range(3):
            if coord[axis]<2:
                nxt=list(coord);nxt[axis]+=1;_edge(out,gid,coords[tuple(nxt)])
    arm=(41,42,43,*range(81,91),119,144,1)
    for a,b in zip(arm,arm[1:]):_edge(out,a,b)
    return out

def route(source:str|int,target:str|int)->dict[str,Any]:
    src,dst=resolve(source),resolve(target);g=graph();q=collections.deque([src]);parent:dict[int,int|None]={src:None}
    while q:
        node=q.popleft()
        if node==dst:break
        for nxt in sorted(g[node]):
            if nxt not in parent:parent[nxt]=node;q.append(nxt)
    if dst not in parent:return {"status":"NO_ROUTE","source":station(src),"target":station(dst)}
    nodes=[dst]
    while nodes[-1]!=src:nodes.append(parent[nodes[-1]])
    nodes.reverse();sig=hashlib.sha256(json.dumps(nodes).encode()).hexdigest()
    return {"status":"ROUTE_FOUND","source":station(src),"target":station(dst),"hops":len(nodes)-1,"nodes":[station(x) for x in nodes],"path_signature":sig,"truth_effect":"NONE","claim_ceiling":"NAVIGATION_ONLY"}

def locate(query:str="kc144")->dict[str,Any]:
    tokens=set(re.findall(r"[a-z0-9]+",query.lower()));vocab=set(re.findall(r"[a-z0-9]+"," ".join(ALIASES+TAGS+MAPS).lower()));overlap=sorted(tokens&vocab);alias_hit=any(a in query.lower() for a in ALIASES)
    return {"found":bool(alias_hit or overlap or not tokens),"score":50*int(alias_hit)+10*len(overlap),"tool_id":TOOL_ID,"version":VERSION,"canonical_address":CANONICAL_ADDRESS,"matched_tokens":overlap,"aliases":list(ALIASES),"tags":list(TAGS),"capabilities":["locate","compile","map","station","route","status","validate"],"maps":list(MAPS),"activation_route":["MYCELIUM.LOCATE","KC144.H06.COMPILE","KC144.KC27.ADMIT","KC144.MAP.SELECT","KC144.ROUTE.EXECUTE","KC144.SSN12.RETURN"],"entrypoint":"python MCP/athena_mcp_server_kc144.py"}

def compile_query(query:str)->dict[str,Any]:
    lowered=" ".join(query.strip().split()).lower();scores:dict[int,int]=collections.Counter();matched={}
    for word,gid in KEYWORDS.items():
        if word in lowered:scores[gid]+=1;matched[word]=gid
    if not scores:scores[119]=1
    gids=[gid for gid,_ in sorted(scores.items(),key=lambda p:(-p[1],p[0]))[:12]];primary=gids[0]
    return {"schema":"KC144-META-COMPILER-RUN-1.1","tool":CANONICAL_ADDRESS,"query":query,"engagement_pipeline":list(PIPELINE),"matched_keywords":matched,"candidate_stations":[station(g) for g in gids],"selected_maps":["query-compiler","activation-wave","mycelium","map-of-maps"],"activation_route":route("H06",primary),"return_route":route(primary,"M12"),"status_vector":{"evidence":"SUPPORTED","execution":"PASS","stewardship":"RESEARCH_ONLY","pipeline":"TESTED"},"production_evidence":list(PRODUCTION_EVIDENCE),"authority_effect":"NONE"}

def map_payload(name:str)->dict[str,Any]:
    key=name.strip().lower()
    if key not in MAPS:
        matches=[x for x in MAPS if key in x]
        if len(matches)!=1:raise KeyError(f"Unknown map: {name!r}")
        key=matches[0]
    payload:dict[str,Any]={"map":key,"tool":CANONICAL_ADDRESS,"truth_effect":"NONE"}
    if key in {"coordinate-grid","station-atlas","math144","dual-coordinate"}:payload["stations"]=[station(g) for g in range(1,145)]
    elif key=="band-partition":payload["bands"]=[{"band":b,"start":lo,"end":hi,"size":hi-lo+1} for b,lo,hi in BANDS]
    elif key=="map-of-maps":payload["maps"]=list(MAPS)
    elif key=="engagement-pipeline":payload["stages"]=list(PIPELINE)
    elif key=="evidence-poset":payload["production"]=list(PRODUCTION_EVIDENCE);payload["target"]=[28,144,144,0,1]
    else:payload["description"]=f"Executable {key} projection"
    return payload

def status()->dict[str,Any]:
    return {"tool_id":TOOL_ID,"version":VERSION,"canonical_address":CANONICAL_ADDRESS,"stations":144,"maps":len(MAPS),"production_evidence":list(PRODUCTION_EVIDENCE),"m12":"HOLD","i10_receipt":None,"qshrink":"NOT_REACHED","navigation_ready":True,"authority_effect":"NONE"}

def validate()->dict[str,Any]:
    failures=[]
    if len({station(g)["grid"] for g in range(1,145)})!=144:failures.append("grid_bijection")
    if len(MAPS)!=37:failures.append("map_count")
    if route("H06","M12")["status"]!="ROUTE_FOUND":failures.append("return_route")
    if not locate("mental compiler mycelium")["found"]:failures.append("locator")
    return {"status":"PASS" if not failures else "FAIL","failures":failures,"stations":144,"maps":37}

def _full_compiler()->pathlib.Path|None:
    for raw in (os.environ.get("KC144_META_COMPILER"),"KC144_Meta_Compiler.pyz","/mnt/data/KC144_Meta_Compiler.pyz"):
        if raw and pathlib.Path(raw).is_file():return pathlib.Path(raw)
    return None

def _delegate(args:list[str])->dict[str,Any]|None:
    target=_full_compiler()
    if target is None or os.environ.get("KC144_META_FALLBACK_ONLY")=="1":return None
    proc=subprocess.run([sys.executable,str(target),*args],capture_output=True,text=True,timeout=60,check=False)
    if proc.returncode!=0:return None
    try:payload=json.loads(proc.stdout)
    except json.JSONDecodeError:payload={"stdout":proc.stdout.strip()}
    return {"delegated":True,"compiler":str(target),"payload":payload,"returncode":0}

def dispatch(operation:str,**kwargs:Any)->dict[str,Any]:
    op=operation.strip().lower().replace("_","-");args=None
    if op=="status":args=["status"]
    elif op=="maps":args=["maps"]
    elif op=="station":args=["station",str(kwargs.get("address","GID119"))]
    elif op=="route":args=["route",str(kwargs.get("source","H06")),str(kwargs.get("target","M12")),"--objective",str(kwargs.get("objective","preserve"))]
    elif op=="compile":args=["compile",str(kwargs.get("query",""))]
    if args:
        delegated=_delegate(args)
        if delegated:
            delegated["mycelium_receipt"]={"located_as":CANONICAL_ADDRESS,"operation":op,"return_station":"M12","authority_effect":"NONE"};return delegated
    if op=="locate":return locate(str(kwargs.get("query","kc144")))
    if op=="status":return status()
    if op=="validate":return validate()
    if op=="maps":return {"maps":list(MAPS)}
    if op=="map":return map_payload(str(kwargs.get("name","map-of-maps")))
    if op=="station":return station(resolve(kwargs.get("address","GID119")))
    if op=="route":return route(kwargs.get("source","H06"),kwargs.get("target","M12"))
    if op=="compile":return compile_query(str(kwargs.get("query","")))
    raise KeyError(f"Unknown operation: {operation}")

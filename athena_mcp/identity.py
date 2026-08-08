from __future__ import annotations
import hashlib, json, re

def canon(v):
    if isinstance(v,dict): return {k:canon(v[k]) for k in sorted(v)}
    if isinstance(v,list): return [canon(x) for x in v]
    if isinstance(v,str): return re.sub(r'\s+',' ',v.strip()).upper()
    return v

def digest(obj,n=16):
    raw=json.dumps(canon(obj),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest().upper()[:n]

def capability_signature(kind,domain,verb,obj,method,input_contract,output_contract,constraints=None):
    return canon({'kind':kind,'domain':domain,'verb':verb,'object':obj,'method':method,'input':input_contract,'output':output_contract,'constraints':constraints or {}})

def canonical_identity(sig):
    cid='CID.'+digest(sig,20)
    name='ATHENA::{kind}::{domain}::{verb}::{object}::{method}::{cid}'.format(kind=sig['kind'],domain=sig['domain'],verb=sig['verb'],object=sig['object'],method=sig['method'],cid=cid)
    oid='OID.'+digest({'canonical':name},20)
    return cid,name,oid

def version_id(oid,payload,parent_vid=None): return 'VID.'+digest({'oid':oid,'parent':parent_vid,'payload':payload},24)
def manifestation_id(vid,carrier,native_locator,content_digest): return 'MID.'+digest({'vid':vid,'carrier':carrier,'locator':native_locator,'digest':content_digest},24)
def event_id(event_type,actor,parent,payload): return 'EID.'+digest({'type':event_type,'actor':actor,'parent':parent,'payload':payload},24)

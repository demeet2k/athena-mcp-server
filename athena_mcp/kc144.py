from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass, asdict
BANDS=[('H6',1,6),('X16',7,22),('BR21',23,43),('F37',44,80),('IC10',81,90),('KC15',91,105),('KC27',106,132),('SSN12',133,144)]
@dataclass(frozen=True)
class Station: sid:str; gid:int; row:int; col:int; band:str
def station(gid):
    if not 1<=gid<=144: raise ValueError('gid must be 1..144')
    row=(gid-1)//12+1; col=(gid-1)%12+1; band=next(n for n,lo,hi in BANDS if lo<=gid<=hi)
    return Station(f'KC144.SID.{gid:03d}',gid,row,col,band)
def stations(): return [asdict(station(g)) for g in range(1,145)]
def stable_gid(key): return 1+int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'big')%144
TOKEN_RE=re.compile(r'\w+|[^\w\s]',re.UNICODE); SENTENCE_END={'.','!','?'}
def coordinate_text(text,oid,vid,mid,canonical_name):
    s=station(stable_gid(canonical_name)); out=[]; paragraph=1; sentence=1; last_end=0
    for ordinal,m in enumerate(TOKEN_RE.finditer(text),start=1):
        paragraph+=text[last_end:m.start()].count('\n\n'); tok=m.group(0)
        coord=(f'KC144.G{s.gid:03d}.R{s.row:02d}.C{s.col:02d}/OID:{oid}/VID:{vid}/MID:{mid}/P:{paragraph:05d}/S:{sentence:05d}/T:{ordinal:07d}/C:{m.start():09d}-{m.end():09d}')
        out.append({'ordinal':ordinal,'token':tok,'char_start':m.start(),'char_end':m.end(),'paragraph':paragraph,'sentence':sentence,'coordinate':coord,'gid':s.gid,'row':s.row,'col':s.col,'band':s.band})
        if tok in SENTENCE_END: sentence+=1
        last_end=m.end()
    return out
def station_manifest(): return json.dumps({'topology':'12x12','count':144,'bands':BANDS,'stations':stations()},indent=2)

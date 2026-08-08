from __future__ import annotations
import json
from .identity import digest
from .timebundle import bundle as time_bundle
from .polycoord import atlas as build_atlas

MATH_KINDS={"DEFINITION","THEOREM","LEMMA","COROLLARY","OPERATOR","INVARIANT","EQUATION","CONJECTURE","MODEL","ALGORITHM","METRIC","FALSIFIER"}

def scale_state(*, has_text=True, edge_count=0, hyperedge_count=0, declared=None):
    active=[]
    if has_text: active.append({"level":"S0","name":"RAW_EVENT","basis":"manifestation"})
    active.append({"level":"S1","name":"STATE_DELTA","basis":"new VID/MID"})
    if edge_count or hyperedge_count: active.append({"level":"S2","name":"RELATION_DELTA","basis":{"edges":edge_count,"hyperedges":hyperedge_count}})
    for x in declared or []:
        if x not in {"S3","S4","S5"}: continue
        active.append({"level":x,"name":{"S3":"MOTIF","S4":"GENERATOR","S5":"ORGAN_NATIVE_LAW"}[x],"basis":"caller-declared; requires independent promotion evidence"})
    return {"active":active,"highest":active[-1]["level"],"promotion_ceiling":"S2" if not declared else active[-1]["level"]}

def crystal_id(manifest):
    return "CRYS."+digest(manifest,24)

def render_header(manifest):
    i=manifest["identity"]; k=manifest["coordinates"]["KC144"]["value"]; t=manifest["coordinates"]["TIME"]["value"]
    j=manifest["coordinates"]["JSPACE"]["value"]; s=manifest["coordinates"]["SCALE"]["value"]
    return (
      f"⟦ATHENA::CRYSTAL::{manifest['crystal_id']}⟧\n"
      f"OID={i['OID']} VID={i['VID']} MID={i['MID']} CID={i['CID']}\n"
      f"KC144=G{k['gid']:03d}/R{k['row']:02d}/C{k['col']:02d}/{k['band']} SID={k['sid']}\n"
      f"JSPACE=IN:{j['in_degree']} OUT:{j['out_degree']} H:{j['hyperedge_count']} SCALE={s['highest']}\n"
      f"UTC={t['UTC']} TAI={t['TAI']} TT={t['TT']} JD={t['JULIAN_DATE_UTC']:.8f}\n"
      f"RETURN={manifest['RETURN']}\n"
      f"⟦/ATHENA::CRYSTAL⟧"
    )

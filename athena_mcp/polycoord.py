from __future__ import annotations
from dataclasses import dataclass, asdict
from .kc144 import station, stable_gid

# Open-world coordinate atlas. Built-ins are always represented; only lawful values are resolved.
CHARTS = {
    "KC144": {"family":"CRYSTAL_HOST","applicability":"UNIVERSAL"},
    "JSPACE": {"family":"SEMANTIC_GRAPH","applicability":"UNIVERSAL"},
    "SCALE": {"family":"REPRESENTATION_SCALE","applicability":"UNIVERSAL"},
    "LINEAGE": {"family":"CAUSAL_TEMPORAL","applicability":"UNIVERSAL"},
    "TIME": {"family":"CLOCK_BUNDLE","applicability":"UNIVERSAL"},
    "LIMINAL": {"family":"AGENT_TRAJECTORY","applicability":"CONDITIONAL"},
    "CUT_LM": {"family":"PHASE_RESIDUAL","applicability":"CONDITIONAL"},
    "EVIDENCE_AUTHORITY": {"family":"EPISTEMIC","applicability":"CONDITIONAL"},
    "KC27": {"family":"QUTRIT_AFFINE_STATE","applicability":"CONDITIONAL"},
    "KC54": {"family":"CONJUGATE_EXECUTION","applicability":"CONDITIONAL"},
    "BR21": {"family":"OPERATOR_PROCESS","applicability":"CONDITIONAL"},
    "F37": {"family":"CARRIER","applicability":"CONDITIONAL"},
    "DLS": {"family":"RECURSIVE","applicability":"CONDITIONAL"},
    "FRACTAL_4x3N": {"family":"OCTAVE_RECURSION","applicability":"CONDITIONAL"},
    "SQUARE_FLOWER_CLOUD_FRACTAL": {"family":"MULTIVIEW_GEOMETRY","applicability":"CONDITIONAL"},
    "HILBERT": {"family":"HILBERT_SPACE","applicability":"CONDITIONAL"},
    "RIEMANN": {"family":"RIEMANN_SPHERE_COMPLEX","applicability":"CONDITIONAL"},
    "DISCIPLINE_NATIVE": {"family":"NATIVE_DOMAIN","applicability":"CONDITIONAL"},
}

VALID_STATUS={"RESOLVED","UNKNOWN","N/A","PARTIAL","HOLD"}

def slot(system, status="UNKNOWN", value=None, source=None, transform=None, loss=None, note=None):
    if status not in VALID_STATUS: raise ValueError(f"invalid coordinate status {status}")
    out={"system":system,"family":CHARTS.get(system,{}).get("family","EXTENSION"),"status":status}
    if value is not None: out["value"]=value
    if source is not None: out["source"]=source
    if transform is not None: out["transform"]=transform
    if loss is not None: out["loss"]=loss
    if note is not None: out["note"]=note
    return out

def atlas(*, canonical_name, oid, vid, mid, jspace, scale, lineage, time_bundle, liminal=None, cut_lm=None, evidence=None, supplied=None):
    supplied=supplied or {}
    st=station(stable_gid(canonical_name))
    resolved={
      "KC144": slot("KC144","RESOLVED",{"sid":st.sid,"gid":st.gid,"row":st.row,"col":st.col,"band":st.band,"oid":oid,"vid":vid,"mid":mid}),
      "JSPACE": slot("JSPACE","RESOLVED",jspace),
      "SCALE": slot("SCALE","RESOLVED",scale),
      "LINEAGE": slot("LINEAGE","RESOLVED",lineage),
      "TIME": slot("TIME","RESOLVED",time_bundle),
      "LIMINAL": slot("LIMINAL","RESOLVED",liminal) if liminal else slot("LIMINAL","UNKNOWN",note="No agent trajectory coordinate supplied."),
      "CUT_LM": slot("CUT_LM",cut_lm.get("status","PARTIAL"),cut_lm) if cut_lm else slot("CUT_LM","UNKNOWN",note="No measured phase/residual coordinate supplied."),
      "EVIDENCE_AUTHORITY": slot("EVIDENCE_AUTHORITY",evidence.get("status","PARTIAL"),evidence) if evidence else slot("EVIDENCE_AUTHORITY","UNKNOWN"),
    }
    for name,meta in CHARTS.items():
        if name in resolved: continue
        if name in supplied:
            raw=supplied[name]
            if isinstance(raw,dict) and "status" in raw:
                resolved[name]=slot(name,raw.get("status","RESOLVED"),raw.get("value"),raw.get("source"),raw.get("transform"),raw.get("loss"),raw.get("note"))
            else:
                resolved[name]=slot(name,"RESOLVED",raw,source="caller")
        else:
            resolved[name]=slot(name,"UNKNOWN",note="Applicable only when a lawful chart adapter or native coordinate is supplied.")
    # Open-world extensions are admitted, never silently dropped.
    for name,raw in supplied.items():
        if name in resolved: continue
        if isinstance(raw,dict) and "status" in raw:
            resolved[name]=slot(name,raw.get("status","RESOLVED"),raw.get("value"),raw.get("source"),raw.get("transform"),raw.get("loss"),raw.get("note"))
        else: resolved[name]=slot(name,"RESOLVED",raw,source="caller")
    return resolved

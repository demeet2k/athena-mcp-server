from __future__ import annotations

from copy import deepcopy
from typing import Any,Dict,List,Tuple,Sequence

from .mythic_holonomy_protocol import HOLONOMY_VERSION
from .mythic_strata_runtime import MythicStrataRuntime

RANK={
    "UNKNOWN":0,
    "MODERN_RECONSTRUCTION":1,
    "TRADITION_INTERNAL":1,
    "SECONDARY_SCHOLARSHIP":2,
    "LIVING_TRADITION_SOURCE":2,
    "PRIMARY_EVIDENCE":3,
}
RANK_INV={v:k for k,v in RANK.items()}
VECTOR_KEYS=[
    "role_delta","decoder_delta","ontology_delta","authority_delta",
    "standing_delta","provenance_delta","invariant_violations","unaccounted_loss",
]

LAWS=[
    "HELD_OUT_SOURCE_CASE != PRACTITIONER_VALIDATION",
    "SEMANTIC_DRIFT != ERROR_BY_DEFAULT",
    "CONTINUITY != IDENTITY",
    "TRANSLATION != LOSSLESS_EQUIVALENCE",
    "COMMENTARY != ORIGINAL_LAYER",
    "H_gamma != METAPHYSICAL_QUANTITY",
    "SOURCE_DERIVED_FEATURE_ENCODING != OBJECTIVE_SEMANTIC_GROUND_TRUTH",
    "SELF_GENERATED_SCORE != INDEPENDENT_WITNESS",
    "BENCHMARK_GAIN != MCK_V2_PROMOTION",
    "CALLER_PACKET_REF != VERIFIED_REMOTE_READ",
    "ADAPTER_DEFAULT != SOURCE_EVIDENCE",
    "DERIVED_BRIDGE_STANDING != SOURCE_ATTESTED_BRIDGE_STANDING",
    "UNTYPED_LOSS_TEXT != TYPED_FEATURE_COVERAGE",
    "STRING_INVARIANT_RETENTION != SEMANTIC_INVARIANT_VALIDATION",
    "EXPECTED_CLASS != RAW_EDGE_SUPPORT",
]


def _uniq(items):
    out=[];seen=set()
    for x in items:
        key=str(x)
        if key not in seen:
            seen.add(key);out.append(x)
    return out


def _jaccard(a,b)->float:
    a=set(a or []);b=set(b or [])
    if not a and not b:return 0.0
    return round(1.0-len(a&b)/len(a|b),8)


def _auth_for_strata(value:str)->str:
    v=str(value or "").upper()
    if "INITIAT" in v:return "INITIATORY"
    if "RESTRICT" in v:return "RESTRICTED"
    if "ROLE" in v or "GRADE" in v:return "ROLE_GATED"
    if "MIXED" in v:return "MIXED"
    if not v or "UNKNOWN" in v:return "UNKNOWN"
    return "PUBLIC"


def _strata_layer(layer:Dict[str,Any])->Dict[str,Any]:
    return {
        "adapter_id":str(layer.get("family_id") or layer.get("adapter_id") or ""),
        "layer_id":layer["layer_id"],
        "standing":layer.get("standing","UNKNOWN"),
        "category_scope":layer.get("category_scope","COMPOSITE"),
        "corpus_mutability":layer.get("corpus_mutability","LAYERED"),
        "authorization_scope":layer.get("authorization_scope") or _auth_for_strata(layer.get("authority_scope","")),
        "source_scope":layer.get("source_language_or_text_layer","") or layer.get("source_scope",""),
    }


def _strata_projection_assumptions(layer:Dict[str,Any],side:str)->List[Dict[str,Any]]:
    out=[]
    if "category_scope" not in layer:
        out.append({"side":side,"field":"category_scope","value":"COMPOSITE","basis":"ADAPTER_DEFAULT"})
    if "corpus_mutability" not in layer:
        out.append({"side":side,"field":"corpus_mutability","value":"LAYERED","basis":"ADAPTER_DEFAULT"})
    if not layer.get("authorization_scope"):
        out.append({
            "side":side,"field":"authorization_scope",
            "value":_auth_for_strata(layer.get("authority_scope","")),
            "basis":"DERIVED_FROM_AUTHORITY_SCOPE",
        })
    return out


def _min_standing(a:str,b:str)->str:
    rank=min(RANK.get(a,0),RANK.get(b,0))
    for x in (a,b,"UNKNOWN"):
        if RANK.get(x,0)==rank:return x
    return RANK_INV.get(rank,"UNKNOWN")


def _bridge(case:Dict[str,Any],source:Dict[str,Any],target:Dict[str,Any])->Dict[str,Any]:
    refs=list(case.get("source_refs") or [])
    invariants=list(case.get("bridge_invariants") or []) or ["preserve explicit layer identity"]
    losses=list(case.get("declared_loss") or []) or ["cross-layer semantic/context difference remains explicit"]
    return {
        "source_ref":refs[0] if refs else "source://heldout-unspecified",
        "evidence_standing":_min_standing(source.get("standing","UNKNOWN"),target.get("standing","UNKNOWN")),
        "invariants":invariants,
        "transform_loss":losses,
        "authority":"SCHOLARLY_MAPPING",
    }


def _bridge_projection_assumptions(case:Dict[str,Any],bridge:Dict[str,Any])->List[Dict[str,Any]]:
    out=[{
        "field":"evidence_standing","value":bridge.get("evidence_standing"),
        "basis":"DERIVED_MIN_ENDPOINT_STANDING_NOT_SOURCE_ATTESTED",
    },{
        "field":"authority","value":bridge.get("authority"),
        "basis":"ADAPTER_CONSTANT_NOT_SOURCE_AUTHORITY",
    }]
    if not case.get("source_refs"):
        out.append({"field":"source_ref","value":bridge.get("source_ref"),"basis":"ADAPTER_FALLBACK"})
    if not case.get("bridge_invariants"):
        out.append({"field":"invariants","value":bridge.get("invariants"),"basis":"ADAPTER_FALLBACK"})
    if not case.get("declared_loss"):
        out.append({"field":"transform_loss","value":bridge.get("transform_loss"),"basis":"ADAPTER_FALLBACK"})
    return out


def _typed_loss_coverage(loss_ledger:Sequence[Any])->set[str]:
    covered:set[str]=set()
    for item in loss_ledger or []:
        if isinstance(item,dict):
            covers=item.get("covers") or item.get("typed_feature_covers") or []
            if isinstance(covers,str):covers=[covers]
            covered.update(str(x) for x in covers)
    return covered


def _distance(start:Dict[str,Any],end:Dict[str,Any],required_prov:List[str],ledger_prov:List[str],ledger_invariants:List[str],required_invariants:List[str],loss_ledger:List[Any])->Dict[str,Any]:
    role_delta=int(start.get("semantic_role")!=end.get("semantic_role"))
    decoder_delta=int(start.get("decoder_role")!=end.get("decoder_role"))
    ontology_delta=_jaccard(start.get("ontology_tags",[]),end.get("ontology_tags",[]))
    authority_delta=int(start.get("authority_scope")!=end.get("authority_scope"))
    standing_delta=max(0,RANK.get(end.get("standing","UNKNOWN"),0)-RANK.get(start.get("standing","UNKNOWN"),0))
    required=set(required_prov or []);have=set(ledger_prov or [])
    provenance_delta=0.0 if not required else round(len(required-have)/len(required),8)
    invariant_violations=sum(1 for x in required_invariants or [] if x not in set(ledger_invariants or []))
    base={
        "role_delta":role_delta,
        "decoder_delta":decoder_delta,
        "ontology_delta":ontology_delta,
        "authority_delta":authority_delta,
        "standing_delta":standing_delta,
        "provenance_delta":provenance_delta,
        "invariant_violations":invariant_violations,
    }
    changed={k for k,v in base.items() if k!="invariant_violations" and isinstance(v,(int,float)) and float(v)!=0.0}
    covered=_typed_loss_coverage(loss_ledger)
    if not changed:
        unaccounted_loss:Any=0
    elif covered:
        unaccounted_loss=len(changed-covered)
    else:
        unaccounted_loss=None
    return {**base,"unaccounted_loss":unaccounted_loss}


def _unaccounted_loss_standing(vector:Dict[str,Any])->str:
    value=vector.get("unaccounted_loss")
    if value is None:return "UNKNOWN_UNTYPED_LOSS_LEDGER"
    return "KNOWN_TYPED_OR_ZERO_CHANGE"


def _nonzero_vector(v:Dict[str,Any])->bool:
    return any(isinstance(x,(int,float)) and float(x)!=0.0 for x in v.values())


def _zero_vector()->Dict[str,int]:
    return {k:0 for k in VECTOR_KEYS}


def _assay_pass(case:Dict[str,Any],result:Dict[str,Any])->bool:
    """Score only after raw arm behavior exists; expected_class never controls raw transport."""
    expected=case.get("expected_class")
    if expected=="ALLOW_WITH_LOSS":
        return case.get("operation")=="SEMANTIC_TRANSPORT" and bool(result.get("allowed"))
    if expected=="HOLD_EQUIVALENCE":
        return case.get("operation")=="SEMANTIC_EQUIVALENCE" and not bool(result.get("allowed"))
    if expected=="ZERO_HOLONOMY_CONTROL":
        return result.get("holonomy_nonzero") is False
    if expected=="NONZERO_HOLONOMY_EXPECTED":
        return result.get("holonomy_nonzero") is True
    if expected=="NONCOMMUTATIVE_EXPECTED":
        return bool(result.get("allowed")) and bool(result.get("path_order_sensitive"))
    return False


class MythicHolonomyRuntime:
    def __init__(self):
        self.strata=MythicStrataRuntime()

    def _validate(self,packet:Dict[str,Any])->Tuple[bool,List[str]]:
        errors=[]
        if packet.get("artifact")!="ATHENA.MYTHIC.HOLONOMY.HELDOUT.V0":errors.append("artifact")
        if packet.get("version")!="MCK.HOLONOMY.BENCH.V0":errors.append("version")
        if len(packet.get("families") or [])<3:errors.append("families<3")
        if len(packet.get("cases") or [])<12:errors.append("cases<12")
        dist=packet.get("distance_semantics") or {}
        if dist.get("scalarization")!="DISABLED_V0":errors.append("scalarization_not_disabled")
        if len(dist.get("vector") or [])<8:errors.append("distance_vector<8")
        return not errors,errors

    def _index(self,packet:Dict[str,Any]):
        families={};layers={}
        for fam in packet.get("families") or []:
            families[fam["family_id"]]=fam
            for raw in fam.get("layers") or []:
                layer=deepcopy(raw);layer["family_id"]=fam["family_id"]
                layers[layer["layer_id"]]=layer
        return families,layers

    def _lawful_transport_edges(self,cases:List[Dict[str,Any]])->Dict[str,set]:
        """Raw support graph comes from frozen transport operations, never expected_class."""
        edges:Dict[str,set]={}
        for case in cases:
            if case.get("operation")!="SEMANTIC_TRANSPORT":continue
            path=list(case.get("path") or [])
            if len(path)<2:continue
            bucket=edges.setdefault(str(case.get("family_id") or ""),set())
            bucket.update(zip(path,path[1:]))
        return edges

    def _transport(self,src:Dict[str,Any],dst:Dict[str,Any],case:Dict[str,Any],operation:str)->Tuple[Dict[str,Any],Dict[str,Any]|None]:
        bridge=None
        if src.get("layer_id")==dst.get("layer_id"):
            receipt=self.strata.transport(_strata_layer(src),_strata_layer(dst),operation)
        else:
            bridge=_bridge(case,src,dst)
            receipt=self.strata.transport(_strata_layer(src),_strata_layer(dst),operation,explicit_bridge=bridge)
        receipt=deepcopy(receipt)
        assumptions=[]
        assumptions.extend(_strata_projection_assumptions(src,"source"))
        assumptions.extend(_strata_projection_assumptions(dst,"target"))
        if bridge is not None:assumptions.extend(_bridge_projection_assumptions(case,bridge))
        receipt["projection_assumptions"]=_uniq(assumptions)
        receipt["projection_assumption_standing"]="SYNTHETIC_ADAPTER_METADATA_NOT_SOURCE_EVIDENCE"
        return receipt,bridge

    def _edgewise(self,path:List[str],case:Dict[str,Any],layers:Dict[str,Dict[str,Any]])->Dict[str,Any]:
        receipts=[];allowed=True
        for a,b in zip(path,path[1:]):
            receipt,_=self._transport(layers[a],layers[b],case,"SEMANTIC_TRANSPORT")
            receipts.append(receipt)
            if not receipt.get("allowed"):allowed=False
        return {"allowed":allowed,"receipts":receipts}

    def _a0(self,case:Dict[str,Any],layers:Dict[str,Dict[str,Any]])->Dict[str,Any]:
        op=case["operation"]
        if op=="SEMANTIC_EQUIVALENCE":
            return {"status":"UNSCOPED_EQUIVALENCE_ADMITTED","allowed":True,"equivalence_claimed":True}
        if op=="HOLONOMY_LOOP":
            return {"status":"UNSCOPED_LOOP_COLLAPSED","allowed":True,"holonomy_vector":_zero_vector(),"holonomy_nonzero":False}
        if op=="PATH_ORDER_COMPARE":
            return {"status":"UNSCOPED_ORDER_COLLAPSED","allowed":True,"path_order_sensitive":False}
        if op=="SAME_LAYER_CONTROL":
            return {"status":"UNSCOPED_SAME_LAYER","allowed":True,"holonomy_vector":_zero_vector(),"holonomy_nonzero":False}
        return {"status":"UNSCOPED_TRANSPORT_ADMITTED","allowed":True}

    def _a1(self,case:Dict[str,Any],layers:Dict[str,Dict[str,Any]])->Dict[str,Any]:
        op=case["operation"];path=list(case["path"])
        if op=="SEMANTIC_EQUIVALENCE":
            receipt,_=self._transport(layers[path[0]],layers[path[-1]],case,"SEMANTIC_EQUIVALENCE")
            return {"status":receipt["status"],"allowed":receipt.get("allowed",False),"receipt":receipt}
        if op=="HOLONOMY_LOOP":
            forward=path[:-1] if len(path)>1 and path[-1]==path[0] else path
            edge=self._edgewise(forward,case,layers)
            return {"status":"EDGEWISE_ONLY_NO_HOLONOMY","allowed":edge["allowed"],"receipts":edge["receipts"],"holonomy_nonzero":None}
        if op=="PATH_ORDER_COMPARE":
            edge=self._edgewise(path,case,layers)
            return {"status":"EDGEWISE_ONLY_NO_ORDER_LEDGER","allowed":edge["allowed"],"receipts":edge["receipts"],"path_order_sensitive":False}
        edge=self._edgewise(path,case,layers)
        if op=="SAME_LAYER_CONTROL":
            return {"status":"EDGEWISE_SAME_LAYER","allowed":edge["allowed"],"receipts":edge["receipts"],"holonomy_vector":_zero_vector(),"holonomy_nonzero":False}
        return {"status":"EDGEWISE_TRANSPORT","allowed":edge["allowed"],"receipts":edge["receipts"]}

    def _compose(self,path:List[str],case:Dict[str,Any],layers:Dict[str,Dict[str,Any]])->Dict[str,Any]:
        provenance=[];losses=[];invariants=[];receipts=[]
        if not path:return {"allowed":False,"status":"HOLD_EMPTY_PATH"}
        provenance.extend(layers[path[0]].get("provenance") or [])
        for a,b in zip(path,path[1:]):
            src=layers[a];dst=layers[b]
            receipt,bridge=self._transport(src,dst,case,"SEMANTIC_TRANSPORT")
            if bridge is not None:
                provenance.append(bridge["source_ref"])
                losses.extend(bridge.get("transform_loss") or [])
                invariants.extend(bridge.get("invariants") or [])
            receipts.append(receipt)
            provenance.extend(dst.get("provenance") or [])
            losses.extend(dst.get("declared_loss") or [])
            if not receipt.get("allowed"):
                return {"allowed":False,"status":receipt["status"],"receipts":receipts,"provenance":_uniq(provenance),"loss_ledger":_uniq(losses),"invariant_ledger":_uniq(invariants)}
        return {"allowed":True,"status":"COMPOSED","receipts":receipts,"provenance":_uniq(provenance),"loss_ledger":_uniq(losses),"invariant_ledger":_uniq(invariants),"end_layer":layers[path[-1]]}

    def _a2(self,case:Dict[str,Any],layers:Dict[str,Dict[str,Any]],lawful_edges:Dict[str,set])->Dict[str,Any]:
        op=case["operation"];path=list(case["path"])
        if op=="SEMANTIC_EQUIVALENCE":
            receipt,_=self._transport(layers[path[0]],layers[path[-1]],case,"SEMANTIC_EQUIVALENCE")
            return {"status":receipt["status"],"allowed":receipt.get("allowed",False),"receipt":receipt}
        if op=="PATH_ORDER_COMPARE":
            canonical=self._compose(path,case,layers)
            canonical_edges=list(zip(path,path[1:]))
            permuted=[path[0],path[-1]]+path[1:-1] if len(path)>=3 else list(reversed(path))
            permuted_edges=list(zip(permuted,permuted[1:]))
            evidence_edges=set(lawful_edges.get(str(case.get("family_id") or ""),set()))
            canonical_supported=bool(canonical_edges) and all(edge in evidence_edges for edge in canonical_edges)
            permuted_supported=bool(permuted_edges) and all(edge in evidence_edges for edge in permuted_edges)
            order_sensitive=(permuted!=path) and canonical_supported and not permuted_supported
            return {
                "status":"PATH_ORDER_EVALUATED","allowed":canonical.get("allowed",False),
                "canonical_path":path,"permuted_path":permuted,"canonical_composition":canonical,
                "frozen_transport_edges":[list(edge) for edge in sorted(evidence_edges)],
                "canonical_supported_by_frozen_transport_cases":canonical_supported,
                "permuted_supported_by_frozen_transport_cases":permuted_supported,
                "path_order_sensitive":order_sensitive,
                "law":"PATH_ORDER_CLAIM_REQUIRES_INDEPENDENT_FROZEN_TRANSPORT_EDGE_SUPPORT",
            }
        if op=="HOLONOMY_LOOP":
            if len(path)<2 or path[-1]!=path[0]:
                return {"status":"HOLD_LOOP_NOT_CLOSED","allowed":False}
            forward=path[:-1]
            composed=self._compose(forward,case,layers)
            if not composed.get("allowed"):
                return {"status":composed.get("status"),"allowed":False,"composition":composed}
            start=layers[path[0]];end=layers[forward[-1]]
            required=_uniq(list(case.get("source_refs") or [])+list(start.get("provenance") or [])+list(end.get("provenance") or []))
            vector=_distance(start,end,required,composed.get("provenance",[]),composed.get("invariant_ledger",[]),case.get("bridge_invariants",[]),composed.get("loss_ledger",[]))
            nonzero=_nonzero_vector(vector)
            return {
                "status":"HOLONOMY_VECTOR_COMPUTED","allowed":True,"composition":composed,
                "projection_back_to":path[0],"holonomy_vector":vector,"holonomy_nonzero":nonzero,
                "unaccounted_loss_standing":_unaccounted_loss_standing(vector),
                "law":"H_gamma_IS_REPRESENTATION_DRIFT_VECTOR_NOT_METAPHYSICAL_QUANTITY",
            }
        composed=self._compose(path,case,layers)
        if not composed.get("allowed"):
            return {"status":composed.get("status"),"allowed":False,"composition":composed}
        if op=="SAME_LAYER_CONTROL":
            start=layers[path[0]];end=layers[path[-1]]
            required=_uniq(list(case.get("source_refs") or [])+list(start.get("provenance") or []))
            vector=_distance(start,end,required,composed.get("provenance",[]),composed.get("invariant_ledger",[]),case.get("bridge_invariants",[]),composed.get("loss_ledger",[]))
            zero=not _nonzero_vector(vector)
            return {
                "status":"SAME_LAYER_CONTROL_EVALUATED","allowed":True,"composition":composed,
                "holonomy_vector":vector,"holonomy_nonzero":not zero,
                "unaccounted_loss_standing":_unaccounted_loss_standing(vector),
            }
        return {"status":"COMPOSED_TRANSPORT_ALLOWED","allowed":True,"composition":composed}

    def _attach_assay(self,case:Dict[str,Any],raw:Dict[str,Any])->Dict[str,Any]:
        out=deepcopy(raw);out["expected_pass"]=_assay_pass(case,raw);return out

    def _result_receipts(self,r:Dict[str,Any])->List[Dict[str,Any]]:
        out=[]
        if isinstance(r.get("receipt"),dict):out.append(r["receipt"])
        out.extend(x for x in r.get("receipts",[]) if isinstance(x,dict))
        comp=r.get("composition") or r.get("canonical_composition")
        if isinstance(comp,dict):out.extend(x for x in comp.get("receipts",[]) if isinstance(x,dict))
        return out

    def _summarize(self,arm:str,results:List[Dict[str,Any]],cases:List[Dict[str,Any]])->Dict[str,Any]:
        expected_pass=sum(1 for r in results if r.get("expected_pass"))
        equivalence_cases=[i for i,c in enumerate(cases) if c.get("operation")=="SEMANTIC_EQUIVALENCE"]
        lawful=[i for i,c in enumerate(cases) if c.get("operation")=="SEMANTIC_TRANSPORT"]
        false_eq=sum(1 for i in equivalence_cases if results[i].get("allowed") or results[i].get("equivalence_claimed"))
        lawful_retained=sum(1 for i in lawful if results[i].get("allowed"))
        false_holds=len(lawful)-lawful_retained
        standing_violations=0;authority_violations=0;prov_ok=0;loss_ok=0;composed_n=0
        vectors=[];projection_receipts=0
        for r in results:
            comp=r.get("composition") or r.get("canonical_composition")
            if isinstance(comp,dict) and comp.get("allowed"):
                composed_n+=1;prov_ok+=int(bool(comp.get("provenance")))
                path_loss=bool(comp.get("loss_ledger"))
                loss_ok+=int(path_loss or r.get("status")=="SAME_LAYER_CONTROL_EVALUATED")
            vec=r.get("holonomy_vector") or {}
            if isinstance(vec,dict) and vec:vectors.append(vec)
            standing_violations+=int(isinstance(vec.get("standing_delta"),(int,float)) and float(vec.get("standing_delta",0))>0)
            for rec in self._result_receipts(r):
                authority_violations+=int(rec.get("execution_authority") not in {None,"NONE"})
                projection_receipts+=int(bool(rec.get("projection_assumptions")))
        ua_known=[v.get("unaccounted_loss") for v in vectors if isinstance(v.get("unaccounted_loss"),(int,float))]
        ua_unknown=sum(v.get("unaccounted_loss") is None for v in vectors)
        invariant_violations=sum(int(v.get("invariant_violations",0)) for v in vectors if isinstance(v.get("invariant_violations"),(int,float)))
        return {
            "arm":arm,"cases":len(cases),"expected_class_passed":expected_pass,
            "false_equivalence_claims":false_eq,"lawful_bridges_retained":lawful_retained,
            "lawful_bridge_total":len(lawful),"false_holds_on_lawful_transport":false_holds,
            "standing_amplification_violations":standing_violations,
            "authority_minting_violations":authority_violations,"composed_paths":composed_n,
            "composed_paths_with_provenance":prov_ok,
            "composed_paths_with_loss_or_same_layer_exemption":loss_ok,
            "invariant_violations":invariant_violations,
            "textual_invariant_checks_unknown":sum(len(c.get("bridge_invariants") or []) for c in cases),
            "holonomy_vector_unaccounted_loss_known_total":sum(ua_known),
            "holonomy_vector_unaccounted_loss_unknown_cases":ua_unknown,
            "path_order_sensitive_cases":sum(bool(r.get("path_order_sensitive")) for r in results),
            "projection_assumption_receipts":projection_receipts,
        }

    def evaluate(self,packet:Dict[str,Any],source_packet_ref:str="",source_packet_blob_sha:str="")->Dict[str,Any]:
        ok,errors=self._validate(packet)
        if not ok:
            return {"version":HOLONOMY_VERSION,"status":"HOLD_INVALID_PACKET","errors":errors,"authority":"NONE","laws":list(LAWS)}
        families,layers=self._index(packet);cases=list(packet.get("cases") or [])
        missing=[]
        for case in cases:
            if case.get("family_id") not in families:missing.append(f"family:{case.get('family_id')}")
            for lid in case.get("path") or []:
                if lid not in layers:missing.append(f"layer:{lid}")
        if missing:
            return {"version":HOLONOMY_VERSION,"status":"HOLD_UNRESOLVED_PACKET_REFERENCES","errors":_uniq(missing),"authority":"NONE","laws":list(LAWS)}
        lawful_edges=self._lawful_transport_edges(cases)
        a0=[self._attach_assay(c,self._a0(c,layers)) for c in cases]
        a1=[self._attach_assay(c,self._a1(c,layers)) for c in cases]
        a2=[self._attach_assay(c,self._a2(c,layers,lawful_edges)) for c in cases]
        return {
            "version":HOLONOMY_VERSION,"status":"HELD_OUT_PACKET_EVALUATED",
            "source_packet_ref":source_packet_ref,"source_packet_blob_sha":source_packet_blob_sha,
            "source_packet_ref_verified":False,
            "packet_identity":{"artifact":packet.get("artifact"),"version":packet.get("version"),"families":len(families),"cases":len(cases)},
            "distance_semantics":deepcopy(packet.get("distance_semantics")),"scalarization":"DISABLED_V0",
            "classification_answer_key_firewall":"EXPECTED_CLASS_USED_ONLY_AFTER_RAW_ARM_EXECUTION_FOR_ASSAY; RAW_EDGE_SUPPORT_USES_OPERATION_PATH_ONLY",
            "projection_policy":{
                "standing":"SYNTHETIC_ADAPTER_METADATA_NOT_SOURCE_EVIDENCE",
                "category_scope_default":"COMPOSITE",
                "corpus_mutability_default":"LAYERED",
                "authorization_scope":"DERIVED_FROM_AUTHORITY_SCOPE_WHEN_ABSENT",
                "bridge_evidence_standing":"DERIVED_MIN_ENDPOINT_STANDING_NOT_SOURCE_ATTESTED",
                "bridge_authority":"ADAPTER_CONSTANT_NOT_SOURCE_AUTHORITY",
                "invariant_evaluation":"STRUCTURAL_STRING_RETENTION_ONLY_NOT_SEMANTIC_VALIDATION",
                "unaccounted_loss":"UNKNOWN_WHEN_CHANGED_DIMENSIONS_HAVE_ONLY_UNTYPED_PROSE_LOSS_LEDGER",
            },
            "arms":{
                "A0_UNSCOPED_REFERENCE":{"summary":self._summarize("A0",a0,cases),"results":a0},
                "A1_EDGEWISE_STRATA":{"summary":self._summarize("A1",a1,cases),"results":a1},
                "A2_COMPOSED_HOLONOMY":{"summary":self._summarize("A2",a2,cases),"results":a2},
            },
            "authority":"READ_ONLY_REPRESENTATION_BENCHMARK_ONLY",
            "practitioner_review":"HOLD_EXTERNAL_REVIEW","mck_v2_promotion":False,
            "general_effectiveness":"UNKNOWN","laws":list(LAWS),
        }

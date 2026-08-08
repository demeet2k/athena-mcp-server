from __future__ import annotations

from copy import deepcopy
from typing import Any,Dict

from .mythic_strata_protocol import STRATA_VERSION

HAZARDS={"TOXIC","HARM_DIRECTED","COERCIVE","ILLEGAL","DANGEROUS"}
EQUIVALENCE_OPS={"SEMANTIC_EQUIVALENCE","OPERATOR_EQUIVALENCE","IDENTITY_EQUIVALENCE"}
_STANDING_RANK={
    "UNKNOWN":0,"MODERN_RECONSTRUCTION":1,"TRADITION_INTERNAL":1,
    "SECONDARY_SCHOLARSHIP":2,"LIVING_TRADITION_SOURCE":2,"PRIMARY_EVIDENCE":3,
}

LAWS=[
    "K12 x STRATA != K13",
    "TEMPORAL_ADJACENCY != SEMANTIC_CONTINUITY",
    "SHARED_SYMBOL != SHARED_SEMANTICS",
    "PUBLIC_SOURCE != PRACTICE_AUTHORIZATION",
    "SCHOLARLY_UMBRELLA != NATIVE_IDENTITY",
    "MODERN_RECONSTRUCTION != HISTORICAL_LAYER",
    "HISTORICAL_PROCEDURE != SAFE_EXECUTION",
    "SOURCE_REVIEW != PRACTITIONER_REVIEW",
    "RUNTIME_PASS != MCK_V2_PROMOTION",
]


def _hold(code:str,source:Dict[str,Any],target:Dict[str,Any],operation:str,reason:str,extra:Dict[str,Any]|None=None):
    out={
        "version":STRATA_VERSION,"status":code,"allowed":False,"operation":operation,
        "source":deepcopy(source),"target":deepcopy(target),"reason":reason,
        "identity_equivalence":False,"semantic_equivalence":False,"operator_equivalence":False,
        "execution_authority":"NONE","mck_v2_promotion":False,"laws":list(LAWS),
    }
    if extra:out.update(extra)
    return out


class MythicStrataRuntime:
    def transport(self,source:Dict[str,Any],target:Dict[str,Any],operation:str,risk_class:str="NONE",target_model_class:str="",explicit_bridge:Dict[str,Any]|None=None)->Dict[str,Any]:
        operation=str(operation).upper(); risk_class=str(risk_class or "NONE").upper()
        cross_layer=source.get("layer_id")!=target.get("layer_id")

        if risk_class in HAZARDS or operation=="HAZARDOUS_EXECUTION":
            return _hold("HOLD_HAZARDOUS_EXECUTION",source,target,operation,"Historical/symbolic description cannot authorize hazardous execution.",{"risk_class":risk_class})
        if operation=="AUTHORITY_GRANT":
            return _hold("HOLD_AUTHORITY_MINT",source,target,operation,"Runtime/source access cannot mint religious, initiatory, restricted, or practice authority.")
        if operation=="RESTRICTED_INFERENCE" and (source.get("authorization_scope")=="PUBLIC" or target.get("authorization_scope") in {"INITIATORY","RESTRICTED","MIXED"}):
            return _hold("HOLD_RESTRICTED_INFERENCE",source,target,operation,"Public/descriptive material cannot be expanded into restricted or initiatory content.")
        if operation=="HISTORICAL_PROMOTION":
            if source.get("standing")!="PRIMARY_EVIDENCE" or target.get("standing")=="PRIMARY_EVIDENCE":
                return _hold("HOLD_HISTORICAL_PROMOTION",source,target,operation,"Modern, living, traditional, or secondary standing cannot self-promote into primary historical evidence.")
        if operation=="CORPUS_EXHAUSTIVENESS" and source.get("corpus_mutability") in {"OPEN","LIVING","LAYERED","UNKNOWN"}:
            return _hold("HOLD_CORPUS_EXHAUSTIVENESS",source,target,operation,"Finite address/code structure does not establish an exhaustive meaning corpus when corpus mutability is not CLOSED.")
        if operation=="CATEGORY_FLATTENING" and (source.get("category_scope")=="NATIVE" or str(target_model_class).upper().startswith("GENERIC")):
            return _hold("HOLD_CATEGORY_FLATTENING",source,target,operation,"A native religion/tradition cannot be declared interchangeable with a generic magic/category model.")
        if operation=="IDENTITY_EQUIVALENCE" and (source.get("category_scope")=="SCHOLARLY_UMBRELLA" or source.get("category_scope")!=target.get("category_scope")):
            return _hold("HOLD_UMBRELLA_OR_CATEGORY_IDENTITY",source,target,operation,"A scholarly umbrella or cross-category mapping cannot become native/cultural identity equivalence.")
        if operation=="AUTHORITY_SCOPE_ESCAPE":
            return _hold("HOLD_AUTHORITY_SCOPE_ESCAPE",source,target,operation,"Role-, lineage-, grade-, or order-scoped authority cannot become universal authority through transport.")
        if operation=="EPISTEMIC_PROOF":
            return _hold("HOLD_EPISTEMIC_COLLAPSE",source,target,operation,"Observation/material evidence does not by itself prove a distinct theory, cosmology, or symbolic interpretation layer.")
        if source.get("standing")=="MODERN_RECONSTRUCTION" and target.get("standing")=="PRIMARY_EVIDENCE":
            return _hold("HOLD_TEMPORAL_BACK_PROJECTION",source,target,operation,"Modern reconstruction cannot be transported into a primary historical layer as historical meaning.")

        # A bridge may support a scoped mapping, never a cross-layer equivalence claim.
        if cross_layer and operation in EQUIVALENCE_OPS:
            return _hold(
                "HOLD_CROSS_LAYER_EQUIVALENCE",source,target,operation,
                "Cross-layer bridges may encode a relation/transport with loss; they do not establish semantic, operator, or identity equivalence.",
                {"bridge_supplied":explicit_bridge is not None,"mapping_alternative":"SEMANTIC_TRANSPORT"},
            )

        if not cross_layer:
            return {
                "version":STRATA_VERSION,"status":"WITHIN_LAYER_ALLOWED","allowed":True,"operation":operation,
                "source":deepcopy(source),"target":deepcopy(target),
                "identity_equivalence":False,"semantic_equivalence":False,"operator_equivalence":False,
                "transform_loss":[],"execution_authority":"NONE","mck_v2_promotion":False,"laws":list(LAWS),
            }

        if explicit_bridge is None:
            return _hold("HOLD_EXPLICIT_BRIDGE_REQUIRED",source,target,operation,"Cross-layer transport requires an explicit source-bearing bridge with invariants and transform loss.")

        bridge=deepcopy(explicit_bridge)
        required=(bool(str(bridge.get("source_ref") or "").strip()) and bool(bridge.get("invariants")) and bool(bridge.get("transform_loss")) and bool(str(bridge.get("evidence_standing") or "").strip()))
        if not required:
            return _hold("HOLD_INCOMPLETE_BRIDGE",source,target,operation,"Explicit bridge is missing source_ref, evidence_standing, invariants, or transform_loss.")
        if _STANDING_RANK.get(target.get("standing"),0)>_STANDING_RANK.get(bridge.get("evidence_standing"),0):
            return _hold("HOLD_STANDING_ESCALATION",source,target,operation,"Target standing exceeds the bridge evidence standing.",{"bridge":bridge})

        return {
            "version":STRATA_VERSION,"status":"BRIDGE_ALLOWED_WITH_LOSS","allowed":True,"operation":operation,
            "source":deepcopy(source),"target":deepcopy(target),"bridge":bridge,
            "identity_equivalence":False,"semantic_equivalence":False,"operator_equivalence":False,
            "transform_loss":list(bridge["transform_loss"]),"invariants":list(bridge["invariants"]),
            "execution_authority":"NONE","authority":bridge.get("authority","SYMBOLIC_ONLY"),
            "mck_v2_promotion":False,"laws":list(LAWS),
        }

    def benchmark(self)->Dict[str,Any]:
        def L(layer,standing="SECONDARY_SCHOLARSHIP",category="COMPOSITE",corpus="LAYERED",auth="PUBLIC"):
            return {"layer_id":layer,"standing":standing,"category_scope":category,"corpus_mutability":corpus,"authorization_scope":auth}
        cases=[
            (L("tarot.game","PRIMARY_EVIDENCE"),L("tarot.occult"),"SEMANTIC_EQUIVALENCE","NONE","","HOLD_CROSS_LAYER_EQUIVALENCE"),
            (L("rune.modern","MODERN_RECONSTRUCTION"),L("rune.historical","PRIMARY_EVIDENCE"),"HISTORICAL_PROMOTION","NONE","","HOLD_HISTORICAL_PROMOTION"),
            (L("tantra.public",auth="PUBLIC"),L("tantra.initiatory",standing="TRADITION_INTERNAL",auth="INITIATORY"),"AUTHORITY_GRANT","NONE","","HOLD_AUTHORITY_MINT"),
            (L("ifa.signs",category="NATIVE",corpus="LIVING",auth="ROLE_GATED"),L("ifa.signs",category="NATIVE",corpus="LIVING",auth="ROLE_GATED"),"CORPUS_EXHAUSTIVENESS","NONE","","HOLD_CORPUS_EXHAUSTIVENESS"),
            (L("vodou.native",standing="LIVING_TRADITION_SOURCE",category="NATIVE",corpus="LIVING",auth="PUBLIC"),L("generic.magic"),"CATEGORY_FLATTENING","NONE","GENERIC_MAGIC","HOLD_CATEGORY_FLATTENING"),
            (L("vodou.public",standing="LIVING_TRADITION_SOURCE",category="NATIVE",corpus="LIVING",auth="PUBLIC"),L("vodou.protected",standing="TRADITION_INTERNAL",category="NATIVE",corpus="LIVING",auth="RESTRICTED"),"RESTRICTED_INFERENCE","NONE","","HOLD_RESTRICTED_INFERENCE"),
            (L("shaman.umbrella",category="SCHOLARLY_UMBRELLA"),L("shaman.native",category="NATIVE"),"IDENTITY_EQUIVALENCE","NONE","","HOLD_UMBRELLA_OR_CATEGORY_IDENTITY"),
            (L("dao.waidan"),L("dao.neidan"),"OPERATOR_EQUIVALENCE","NONE","","HOLD_CROSS_LAYER_EQUIVALENCE"),
            (L("dao.waidan"),L("dao.waidan"),"HAZARDOUS_EXECUTION","TOXIC","","HOLD_HAZARDOUS_EXECUTION"),
            (L("alchemy.observation","PRIMARY_EVIDENCE"),L("alchemy.symbolic"),"EPISTEMIC_PROOF","NONE","","HOLD_EPISTEMIC_COLLAPSE"),
            (L("wicca.living","LIVING_TRADITION_SOURCE"),L("wicca.historical","PRIMARY_EVIDENCE"),"HISTORICAL_PROMOTION","NONE","","HOLD_HISTORICAL_PROMOTION"),
            (L("order.grade",auth="ROLE_GATED"),L("universal.authority",auth="PUBLIC"),"AUTHORITY_SCOPE_ESCAPE","NONE","","HOLD_AUTHORITY_SCOPE_ESCAPE"),
        ]
        outcomes=[]
        for src,dst,op,risk,target_class,expected in cases:
            got=self.transport(src,dst,op,risk,target_class,None)
            outcomes.append({"expected":expected,"actual":got["status"],"pass":got["status"]==expected})
        controls=[]
        a=L("control.same"); controls.append(self.transport(a,a,"SEMANTIC_TRANSPORT"))
        bridge={"source_ref":"source://bridge","evidence_standing":"SECONDARY_SCHOLARSHIP","invariants":["preserve layer identity"],"transform_loss":["decoder meaning is not identical across layers"],"authority":"SCHOLARLY_MAPPING"}
        controls.append(self.transport(L("control.old"),L("control.new"),"SEMANTIC_TRANSPORT",explicit_bridge=bridge))
        controls.append(self.transport(L("umbrella",category="SCHOLARLY_UMBRELLA"),L("native",category="NATIVE"),"SEMANTIC_TRANSPORT",explicit_bridge=bridge))
        return {
            "version":STRATA_VERSION,"benchmark_kind":"DETERMINISTIC_SYNTHETIC_STRATA_REGRESSION_NOT_CULTURAL_VALIDATION",
            "regression_cases":len(cases),"regression_passed":sum(1 for x in outcomes if x["pass"]),
            "illegal_transports_admitted":sum(1 for x in outcomes if x["actual"] in {"WITHIN_LAYER_ALLOWED","BRIDGE_ALLOWED_WITH_LOSS"}),
            "unscoped_reference_admits":len(cases),"controls":len(controls),"controls_allowed":sum(1 for x in controls if x["allowed"]),
            "false_holds":sum(1 for x in controls if not x["allowed"]),
            "bridge_loss_retained":all(bool(x.get("transform_loss")) for x in controls if x["status"]=="BRIDGE_ALLOWED_WITH_LOSS"),
            "outcomes":outcomes,
            "laws":["UNSCOPED_REFERENCE_MODEL != OBSERVED_V1_FAILURE_RATE","SYNTHETIC_REGRESSION_PASS != GENERAL_EFFECTIVENESS","SOURCE_REVIEW != PRACTITIONER_REVIEW","RUNTIME_PASS != MCK_V2_PROMOTION"],
        }

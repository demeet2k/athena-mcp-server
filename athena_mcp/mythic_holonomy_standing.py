from __future__ import annotations

from copy import deepcopy
from typing import Any,Dict,List


PROXY_STANDING="OPEN_PATH_DRIFT_PROXY_NO_PROJECTION_BACK_OPERATOR_V0"
CLOSED_LOOP_STANDING="UNKNOWN_NO_TYPED_PROJECTION_BACK_OPERATOR_V0"
PROJECTION_OPERATOR="UNDEFINED_V0"

STANDING_LAWS=[
    "OPEN_PATH_ENDPOINT_DRIFT != CLOSED_LOOP_HOLONOMY",
    "PROJECTION_BACK_LABEL != EXECUTED_PROJECTION_OPERATOR",
    "CLOSED_ENDPOINT_IDENTITY != PATH_STATE_TRANSPORT",
    "FROZEN_EXPECTED_CLASS_MATCH != TRUE_CLOSED_LOOP_HOLONOMY_WITNESS",
]


def _loop_indexes(packet:Dict[str,Any])->List[int]:
    return [i for i,case in enumerate(packet.get("cases") or []) if case.get("operation")=="HOLONOMY_LOOP"]


def apply_projection_standing(packet:Dict[str,Any],result:Dict[str,Any])->Dict[str,Any]:
    """Annotate V0 loop outputs without inventing a missing projection operator.

    The underlying runtime computes a representation-drift vector from the loop's
    start layer to the final non-return layer. V0 has no transported semantic state
    plus connection/back-map that would make this a closed-loop holonomy operator.
    Preserve the raw vector and frozen-oracle assay for compatibility, but type its
    standing explicitly and report true closed-loop holonomy as UNKNOWN.
    """
    out=deepcopy(result)
    if out.get("status")!="HELD_OUT_PACKET_EVALUATED":
        return out

    loop_indexes=_loop_indexes(packet)
    a2=(out.get("arms") or {}).get("A2_COMPOSED_HOLONOMY") or {}
    rows=a2.get("results") or []
    proxy_count=0
    for i in loop_indexes:
        if i>=len(rows):
            continue
        row=rows[i]
        raw_vector=deepcopy(row.get("holonomy_vector"))
        raw_nonzero=row.get("holonomy_nonzero")
        row["raw_runtime_status"]=row.get("status")
        row["status"]="OPEN_PATH_DRIFT_PROXY_COMPUTED"
        row["representation_drift_proxy_vector"]=raw_vector
        row["representation_drift_proxy_nonzero"]=raw_nonzero
        row["holonomy_vector_standing"]=PROXY_STANDING
        row["holonomy_nonzero_standing"]=PROXY_STANDING
        row["projection_back_to_declared"]=row.get("projection_back_to")
        row["projection_back_executed"]=False
        row["projection_back_operator"]=PROJECTION_OPERATOR
        row["closed_loop_holonomy"]="UNKNOWN"
        row["closed_loop_holonomy_standing"]=CLOSED_LOOP_STANDING
        row["expected_class_assay_standing"]="FROZEN_ORACLE_MATCH_USING_OPEN_PATH_PROXY_NOT_TRUE_CLOSED_LOOP_WITNESS"
        proxy_count+=1

    summary=a2.get("summary")
    if isinstance(summary,dict):
        summary["open_path_drift_proxy_cases"]=proxy_count
        summary["true_closed_loop_projection_executed_cases"]=0
        summary["closed_loop_holonomy_unknown_cases"]=proxy_count
        summary["closed_loop_holonomy_standing"]=CLOSED_LOOP_STANDING
        summary["frozen_expected_class_assay_uses_proxy_for_loop_cases"]=proxy_count

    out["holonomy_standing"]={
        "v0_loop_vector":PROXY_STANDING,
        "projection_back_executed":False,
        "projection_back_operator":PROJECTION_OPERATOR,
        "closed_loop_holonomy":CLOSED_LOOP_STANDING,
        "reason":"V0_RUNTIME_HAS_RELATIONAL_TRANSPORT_RECEIPTS_BUT_NO_TYPED_TRANSPORTED_STATE_PLUS_CONNECTION_BACK_MAP",
        "compatibility":"RAW_HOLONOMY_VECTOR_AND_EXPECTED_PASS_RETAINED_WITH_DOWNGRADED_STANDING",
    }
    out["laws"]=list(out.get("laws") or [])+[x for x in STANDING_LAWS if x not in set(out.get("laws") or [])]
    return out

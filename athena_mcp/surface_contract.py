from __future__ import annotations

from typing import Any, Dict, Iterable

SURFACE_VERSION="ATHENA.SURFACE.1"

REQUIRED_TOOLS={
    "base":{
        "athena_register","athena_resolve","athena_search","athena_commit_delta","athena_ingest_text",
        "athena_add_edge","athena_add_hyperedge","athena_hydrate","athena_session_start","athena_session_end",
        "athena_git_status","athena_benchmark","athena_crystallize_output","athena_finalize_output",
        "athena_verify_emission","athena_dense_navigate","athena_register_transform","athena_apply_transform",
        "athena_apply_transform_route","athena_coordinate_matrix","athena_record_holonomy","athena_graph_path",
    },
    "aor":{
        "athena_orchestrate","athena_orchestration_get","athena_orchestration_replay","athena_orchestration_robustness",
    },
    "branch":{"athena_branch_observe","athena_branch_state","athena_branch_list","athena_branch_review"},
    "authority":{"athena_claim_register","athena_claim_state","athena_claim_list","athena_claim_promote","athena_claim_challenge","athena_claim_resolve_canonical_challenge"},
    "development":{
        "athena_equivalence_observe","athena_equivalence_snapshot","athena_extraction_plan",
    },
    "retrieval":{"athena_retrieval_compile","athena_retrieval_get","athena_retrieval_replay","athena_retrieval_recent"},
    "hug":{"athena_hug_register","athena_hug_state","athena_hug_list","athena_hug_promote","athena_hug_plan","athena_hug_complete","athena_hug_invocation","athena_hug_replay"},
    "gap":{"athena_gap_compile","athena_gap_get","athena_gap_replay","athena_gap_recent"},
    "field":{"athena_field_compile","athena_field_get","athena_field_replay","athena_field_recent"},
}

REQUIRED_RESOURCES={
    "base":{
        "athena://manifest","athena://kc144/stations","athena://state/head","athena://registry","athena://jspace",
        "athena://scale","athena://coordinate/charts","athena://crystals","athena://math","athena://time/provenance",
        "athena://transforms","athena://emissions",
    },
    "aor":{"athena://orchestration/law","athena://orchestration/robustness"},
    "branch":{"athena://branches"},
    "authority":{"athena://authority"},
    "development":{"athena://equivalence","athena://extraction"},
    "retrieval":{"athena://retrieval"},
    "hug":{"athena://hug"},
    "gap":{"athena://gap"},
    "field":{"athena://field","athena://stack"},
}


def _flatten(groups: Dict[str,set[str]]) -> set[str]:
    out=set()
    for values in groups.values(): out.update(values)
    return out


def contract_manifest() -> Dict[str,Any]:
    return {
        "version":SURFACE_VERSION,
        "required_tools":{k:sorted(v) for k,v in REQUIRED_TOOLS.items()},
        "required_resources":{k:sorted(v) for k,v in REQUIRED_RESOURCES.items()},
        "tool_count":len(_flatten(REQUIRED_TOOLS)),
        "resource_count":len(_flatten(REQUIRED_RESOURCES)),
        "law":"the promoted default runtime must preserve every mature required tool/resource unless explicit versioned supersession changes this contract",
    }


def audit_surface(tool_names: Iterable[str], resource_uris: Iterable[str]) -> Dict[str,Any]:
    tools=set(tool_names); resources=set(resource_uris)
    required_tools=_flatten(REQUIRED_TOOLS); required_resources=_flatten(REQUIRED_RESOURCES)
    missing_tools=sorted(required_tools-tools); missing_resources=sorted(required_resources-resources)
    group_status={}
    for group in sorted(set(REQUIRED_TOOLS)|set(REQUIRED_RESOURCES)):
        mt=sorted(REQUIRED_TOOLS.get(group,set())-tools)
        mr=sorted(REQUIRED_RESOURCES.get(group,set())-resources)
        group_status[group]={"status":"PASS" if not mt and not mr else "FAIL","missing_tools":mt,"missing_resources":mr}
    return {
        "version":SURFACE_VERSION,
        "status":"PASS" if not missing_tools and not missing_resources else "FAIL",
        "missing_tools":missing_tools,
        "missing_resources":missing_resources,
        "extra_tools":sorted(tools-required_tools),
        "extra_resources":sorted(resources-required_resources),
        "groups":group_status,
        "observed_tool_count":len(tools),
        "observed_resource_count":len(resources),
    }

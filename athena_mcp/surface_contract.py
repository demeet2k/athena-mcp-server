from __future__ import annotations

from typing import Any,Dict,Iterable

from .collective_protocol import COLLECTIVE_TOOLS
from .collective_growth_protocol import COLLECTIVE_GROWTH_TOOLS
from .collective_v2_protocol import COLLECTIVE_V2_TOOLS
from .aor_protocol import AOR_TOOLS
from .orchestration_branch_protocol import BRANCH_TOOLS
from .orchestration_authority_protocol import AUTHORITY_TOOLS
from .orchestration_robustness_protocol import ROBUSTNESS_TOOLS
from .orchestration_equivalence_protocol import EQUIVALENCE_RESOURCE,EQUIVALENCE_TOOLS
from .orchestration_extract_protocol import EXTRACTION_RESOURCE,EXTRACTION_TOOLS
from .orchestration_retrieval_protocol import RETRIEVAL_RESOURCE,RETRIEVAL_TOOLS
from .orchestration_hug_protocol import HUG_RESOURCE,HUG_TOOLS
from .orchestration_gap_protocol import GAP_RESOURCE,GAP_TOOLS
from .orchestration_field_protocol import FIELD_RESOURCE,FIELD_TOOLS
from .aor_collective_transport_protocol import TRANSPORT_RESOURCE,TRANSPORT_TOOLS
from .surface_protocol import SURFACE_RESOURCE,SURFACE_TOOLS
from .promotion_protocol import PROMOTION_RESOURCE,PROMOTION_TOOLS

SURFACE_VERSION='ATHENA.SURFACE.2'

BASE_REQUIRED={
 'athena_register','athena_resolve','athena_search','athena_commit_delta','athena_ingest_text','athena_add_edge','athena_emit_agent_event',
 'athena_match_help','athena_form_simplex','athena_promote_mutation','athena_pending_mutations','athena_adopt_mutation','athena_hydrate',
 'athena_session_start','athena_session_end','athena_git_status','athena_add_hyperedge','athena_crystallize_output','athena_dense_navigate',
 'athena_register_transform','athena_apply_transform','athena_apply_transform_route','athena_coordinate_matrix','athena_record_holonomy','athena_graph_path',
 'athena_finalize_output','athena_verify_emission','athena_benchmark',
}

def _names(tools):return {tool['name'] for tool in tools}

REQUIRED_TOOLS={
 'base':BASE_REQUIRED,
 'collective_v1':_names(COLLECTIVE_TOOLS),
 'collective_growth':_names(COLLECTIVE_GROWTH_TOOLS),
 'collective_v2':_names(COLLECTIVE_V2_TOOLS),
 'aor_core':_names(AOR_TOOLS)|_names(ROBUSTNESS_TOOLS),
 'branch':_names(BRANCH_TOOLS),
 'authority':_names(AUTHORITY_TOOLS),
 'equivalence':_names(EQUIVALENCE_TOOLS),
 'extraction':_names(EXTRACTION_TOOLS),
 'retrieval':_names(RETRIEVAL_TOOLS),
 'hug':_names(HUG_TOOLS),
 'gap':_names(GAP_TOOLS),
 'field':_names(FIELD_TOOLS),
 'transport':_names(TRANSPORT_TOOLS),
 'surface':_names(SURFACE_TOOLS),
 'promotion':_names(PROMOTION_TOOLS),
}

REQUIRED_RESOURCES={
 'base':{'athena://manifest','athena://kc144/stations','athena://state/head','athena://registry','athena://jspace','athena://scale','athena://coordinate/charts','athena://crystals','athena://math','athena://time/provenance','athena://transforms','athena://emissions'},
 'collective':{'athena://collective/runtime','athena://collective/growth','athena://collective/v2'},
 'aor_core':{'athena://orchestration/law','athena://orchestration/recent','athena://orchestration/robustness','athena://branches','athena://authority'},
 'development':{EQUIVALENCE_RESOURCE['uri'],EXTRACTION_RESOURCE['uri'],RETRIEVAL_RESOURCE['uri'],HUG_RESOURCE['uri'],GAP_RESOURCE['uri'],FIELD_RESOURCE['uri']},
 'transport':{TRANSPORT_RESOURCE['uri']},
 'surface':{SURFACE_RESOURCE['uri']},
 'promotion':{PROMOTION_RESOURCE['uri']},
}


def _flatten(groups):
    out=set()
    for values in groups.values():out.update(values)
    return out


def contract_manifest()->Dict[str,Any]:
    return {
        'version':SURFACE_VERSION,
        'required_tools':{k:sorted(v) for k,v in REQUIRED_TOOLS.items()},
        'required_resources':{k:sorted(v) for k,v in REQUIRED_RESOURCES.items()},
        'tool_count':len(_flatten(REQUIRED_TOOLS)),'resource_count':len(_flatten(REQUIRED_RESOURCES)),
        'law':'the promoted unified runtime must preserve every mature base + Collective + AOR + transport + governance surface unless an explicit versioned supersession/migration changes this contract',
    }


def audit_surface(tool_names:Iterable[str],resource_uris:Iterable[str])->Dict[str,Any]:
    tools=set(tool_names);resources=set(resource_uris);req_tools=_flatten(REQUIRED_TOOLS);req_resources=_flatten(REQUIRED_RESOURCES)
    missing_tools=sorted(req_tools-tools);missing_resources=sorted(req_resources-resources);groups={}
    for group in sorted(set(REQUIRED_TOOLS)|set(REQUIRED_RESOURCES)):
        mt=sorted(REQUIRED_TOOLS.get(group,set())-tools);mr=sorted(REQUIRED_RESOURCES.get(group,set())-resources)
        groups[group]={'status':'PASS' if not mt and not mr else 'FAIL','missing_tools':mt,'missing_resources':mr}
    return {
        'version':SURFACE_VERSION,'status':'PASS' if not missing_tools and not missing_resources else 'FAIL',
        'missing_tools':missing_tools,'missing_resources':missing_resources,
        'extra_tools':sorted(tools-req_tools),'extra_resources':sorted(resources-req_resources),
        'groups':groups,'observed_tool_count':len(tools),'observed_resource_count':len(resources),
    }

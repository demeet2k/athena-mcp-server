from __future__ import annotations
from pathlib import PurePosixPath
from typing import Any,Iterable,Mapping,Sequence

ARCHITECTURE_DRIFT_VERSION='ATHENA.ARCHITECTURE.DRIFT.1'

def _set(values):return {str(v) for v in (values or []) if str(v)}
def _ci_mentions(ci,path):
    if not ci:return True
    p=str(path);return p in ci or PurePosixPath(p).name in ci

def audit_architecture(*,observed_tools:Iterable[str],observed_resources:Iterable[str],manifest_layers:Iterable[str],surface_required_tools:Iterable[str],surface_required_resources:Iterable[str],omega_components:Iterable[str],organs:Sequence[Mapping[str,Any]],organ_inventory_version:str,ci_text:str='',available_paths:Iterable[str]|None=None,classified_tool_baseline:Iterable[str]|None=None,classified_resource_baseline:Iterable[str]|None=None)->dict[str,Any]:
    tools=_set(observed_tools);resources=_set(observed_resources);layers=_set(manifest_layers);surface_tools=_set(surface_required_tools);surface_resources=_set(surface_required_resources);omega=_set(omega_components);paths=_set(available_paths);ci=str(ci_text or '');rows=[];defects=[];declared_tools=set();declared_resources=set()
    for raw in organs:
        organ=dict(raw);oid=str(organ['id']);rt=_set(organ.get('tools'));rr=_set(organ.get('resources'));declared_tools|=rt;declared_resources|=rr;od=[]
        checks=(('RUNTIME_TOOL_MISSING',sorted(rt-tools)),('RUNTIME_RESOURCE_MISSING',sorted(rr-resources)),('SURFACE_TOOL_MISSING',sorted(rt-surface_tools)),('SURFACE_RESOURCE_MISSING',sorted(rr-surface_resources)),('CRITICAL_WITNESS_MISSING',sorted(p for p in organ.get('critical_tests') or [] if not _ci_mentions(ci,p))),('SOURCE_OR_SPEC_MISSING',sorted(p for p in list(organ.get('source_refs') or [])+list(organ.get('spec_refs') or []) if paths and p not in paths)))
        for kind,vals in checks:
            if vals:od.append({'kind':kind,'values':vals})
        if str(organ.get('manifest_layer')) not in layers:od.append({'kind':'MANIFEST_LAYER_MISSING','values':[organ.get('manifest_layer')]})
        if str(organ.get('omega_key')) not in omega:od.append({'kind':'OMEGA_COORDINATE_MISSING','values':[organ.get('omega_key')]})
        rows.append({'id':oid,'version':organ.get('version'),'integration_class':organ.get('integration_class'),'authority_plane':organ.get('authority_plane'),'status':'PASS' if not od else 'DRIFT','defects':od,'laws':list(organ.get('laws') or [])});defects.extend({'organ_id':oid,**d} for d in od)
    base_tools=_set(classified_tool_baseline) or surface_tools;base_resources=_set(classified_resource_baseline) or surface_resources
    extra_tools=sorted(tools-base_tools-declared_tools);extra_resources=sorted(resources-base_resources-declared_resources)
    return {'version':ARCHITECTURE_DRIFT_VERSION,'status':'PASS' if not defects else 'ARCHITECTURE_DRIFT','organ_inventory_version':organ_inventory_version,'organ_count':len(rows),'drift_count':sum(r['status']!='PASS' for r in rows),'organs':rows,'defects':defects,'unclassified_surface':{'tools':extra_tools,'resources':extra_resources,'count':len(extra_tools)+len(extra_resources),'status':'OBSERVE_EXPANSION_FRONTIER' if extra_tools or extra_resources else 'EMPTY'},'law':'declared mature organ integration requires runtime discovery + SURFACE + effective manifest + OMEGA; repository qualification additionally requires named critical witnesses and source/spec presence','boundary':'unclassified extras remain recursive review pressure and never become mature by file/tool existence alone'}

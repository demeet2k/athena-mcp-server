from __future__ import annotations

from pathlib import Path
from typing import Any

from .architecture_drift import ARCHITECTURE_DRIFT_VERSION,audit_architecture
from .architecture_drift_protocol import ARCHITECTURE_DRIFT_RESOURCES
from .coordination_inventory import COORDINATION_INVENTORY_VERSION,PARTY_REWARD_VERSION,inventory_manifest,mature_organs

COORDINATION_ARCHITECTURE_VERSION='ATHENA.COORDINATION.ARCHITECTURE.1'
EFFECTIVE_MANIFEST='ATHENA.RUNTIME.UNIFIED.11'
COORDINATION_LAYERS=['MESSAGE_BOARD_V1','COHESION_MESH_V1','COHESION_DUPLICATE_GUARD_V1','COHESION_EVIDENCE_GUARD_V1','AGENT_BOOT_COHESION_TREATMENT_V1','PARTY_COORDINATION_V1','PARTY_CHANNEL_V2','PARTY_REWARD_PROVENANCE_V3_2','ORGAN_INVENTORY.1','ARCHITECTURE_DRIFT_AUDIT.1']
COORDINATION_LAWS=['Y1_SEMANTIC_CLAIM_AUTHORITY != MESSAGE_BOARD_COORDINATION_PRESENCE_CLAIM_AUTHORITY','MESSAGE_BOARD = SOLE_PRESENCE_CLAIM_MESSAGE_AUTHORITY; BOARD_STATE != EXECUTION_AUTHORITY != WORLD_TRUTH','COHESION != CLAIM_AUTHORITY != ASSIGNMENT_AUTHORITY != EXECUTION_AUTHORITY','FUZZY_SIMILARITY != DUPLICATE_PROOF; TREATMENT_OPTION != TREATMENT_EXECUTION','PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE != SUFFICIENT_COMPARATIVE_EVIDENCE; CAUSAL_EFFECT = UNKNOWN','PARTY_RESULT != RESULT_TRUTH; PARTY_REWARD_PROVENANCE != GLOBAL_XP_AUTHORITY','V3_PACKET_VERSION_REQUIRED; INNER_RESULT_VERIFY_MUST_MATCH_OUTER_MESSAGE_BOARD_ROLE','BASE_XP_MUST_BE_FINITE_NON_BOOLEAN_BEFORE_PARTY_REWARD_PROCESSING','FINITE_NUMERIC_VALIDATION != UPSTREAM_XP_VERIFICATION_OR_MINT_AUTHORITY','MATURE_ORGAN_CODE_OR_TOOL_EXISTENCE != CONSTITUTIONAL_INTEGRATION']

def _flatten(groups):
    out=set()
    for vals in groups.values():out.update(vals)
    return out

def _observed(server):
    tools=server.handle({'jsonrpc':'2.0','id':'drift-tools','method':'tools/list'})['result']['tools'];resources=server.handle({'jsonrpc':'2.0','id':'drift-res','method':'resources/list'})['result']['resources'];return [x['name'] for x in tools],[x['uri'] for x in resources]

def install_coordination_architecture(namespace:dict[str,Any])->None:
    if namespace.get('_ATHENA_COORDINATION_ARCHITECTURE_INSTALLED'):return
    from . import unified_manifest as um,surface_contract as sc,state_projection as sp,runtime_integrity_surface as ris,aor_development_surface as ads,state_foundation_surface as sfs
    organs=mature_organs();organ_tools={n for o in organs for n in o.get('tools') or []};organ_resources={u for o in organs for u in o.get('resources') or []}
    sc.REQUIRED_TOOLS['coordination']=set(organ_tools);sc.REQUIRED_RESOURCES['coordination']=set(organ_resources);sc.REQUIRED_RESOURCES['architecture_drift']={r['uri'] for r in ARCHITECTURE_DRIFT_RESOURCES}
    old_contract=sc.contract_manifest
    def contract():
        p=old_contract();p['coordination_inventory_version']=COORDINATION_INVENTORY_VERSION;p['coordination_party_reward_version']=PARTY_REWARD_VERSION;p['law']=str(p.get('law',''))+' Declared coordination organs and architecture-drift resources are mandatory promotion surfaces.';return p
    sc.contract_manifest=contract
    old_build=um.build_unified_manifest;old_maxdev=um.maxdev_law;um.UNIFIED_MANIFEST_VERSION=EFFECTIVE_MANIFEST
    def build(server):
        p=old_build(server);compat=list(p.get('artifact_compat') or []);prior=str(p.get('artifact') or 'ATHENA.RUNTIME.UNIFIED.10')
        if prior not in compat:compat.append(prior)
        p['artifact']=EFFECTIVE_MANIFEST;p['artifact_compat']=compat;p['layers']=list(dict.fromkeys(list(p.get('layers') or [])+COORDINATION_LAYERS));p['invariants']=list(dict.fromkeys(list(p.get('invariants') or [])+COORDINATION_LAWS));p['navigation']=str(p.get('navigation',''))+' <-> MessageBoard/Cohesion/PartyCoordination';org=dict(p.get('organs') or {});inv=inventory_manifest();org['coordination']={'version':COORDINATION_ARCHITECTURE_VERSION,'inventory_version':COORDINATION_INVENTORY_VERSION,'party_reward_current':PARTY_REWARD_VERSION,'organs':[{'id':o['id'],'version':o['version'],'integration_class':o['integration_class'],'authority_plane':o['authority_plane'],'manifest_layer':o['manifest_layer']} for o in inv['organs']]};p['organs']=org;p['architecture_drift']={'version':ARCHITECTURE_DRIFT_VERSION,'inventory_version':COORDINATION_INVENTORY_VERSION};un=list(p.get('unresolved') or []);un=[x for x in un if x.get('id')!='ORGAN_INVENTORY_EXPANSION'];un.append({'id':'ORGAN_INVENTORY_EXPANSION','status':'ACTIVE_RECURSIVE_FRONTIER','boundary':'Message Board/Cohesion/Party V1-V3.2 are declared mature; Freshness Train and additional Frontier/Rehydration/Campaign/QHUG/Mythic/Bionano post-V14 extension families require separate authority/mutation classification before maturity.'});p['unresolved']=un;return p
    def maxdev():return old_maxdev()+"\nCOORDINATION ARCHITECTURE: Message Board coordination authority != Y1 semantic authority; Cohesion is advisory/read-only; Party V3.2 is provenance/numeric membrane only; declared architecture drift blocks promotion; unclassified extras remain recursive review pressure."
    um.build_unified_manifest=build;um.maxdev_law=maxdev

    # OMEGA descriptor overlay. V14 intentionally does not expose a static
    # OMEGA_COMPONENTS registry, so the drift audit derives coordinates from the
    # actual projected state instead of maintaining a second schema by hand.
    old_project=sp.project_omega
    def project(server):
        p=old_project(server);inv=inventory_manifest();p['coordination']={'status':'KNOWN','inventory_version':COORDINATION_INVENTORY_VERSION,'party_reward_current':PARTY_REWARD_VERSION,'organs':[{'id':o['id'],'version':o['version'],'integration_class':o['integration_class'],'authority_plane':o['authority_plane']} for o in inv['organs']],'boundary':'descriptor-only projection; no Message Board/Cohesion/Party Git sync while observing OMEGA'};import hashlib,json;src={k:v for k,v in p.items() if k not in {'omega_id','state_digest'}};d=hashlib.sha256(json.dumps(src,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();p['state_digest']=d;p['omega_id']='OMEGA.'+d[:24];return p
    sp.project_omega=project;sfs.project_omega=project

    # Runtime integrity drift gate wraps already-installed V14 manifest/surface.
    old_surface=ris.RuntimeIntegritySurface.surface_audit;old_read=ris.RuntimeIntegritySurface.read_resource;old_bench=ris.RuntimeIntegritySurface.benchmark
    def drift(self,repository=False):
        tool_names,resource_uris=_observed(self.server);contract=sc.contract_manifest();reqt=_flatten(contract['required_tools']);reqr=_flatten(contract['required_resources']);ci='';paths=None
        if repository:
            root=Path(__file__).resolve().parents[1];cip=root/'.github/workflows/ci.yml';ci=cip.read_text(encoding='utf-8',errors='replace') if cip.exists() else '';expected={p for o in organs for p in list(o.get('source_refs') or [])+list(o.get('spec_refs') or [])};paths={p for p in expected if (root/p).exists()}
        omega_components=set(sp.project_omega(self.server).keys())
        return audit_architecture(observed_tools=tool_names,observed_resources=resource_uris,manifest_layers=um.build_unified_manifest(self.server)['layers'],surface_required_tools=reqt,surface_required_resources=reqr,omega_components=omega_components,organs=organs,organ_inventory_version=COORDINATION_INVENTORY_VERSION,ci_text=ci,available_paths=paths,classified_tool_baseline=reqt,classified_resource_baseline=reqr)
    def surface(self,run_probes=True):
        p=old_surface(self,run_probes);d=drift(self,False);p['architecture_drift']=d;p['status']='PASS' if p.get('status')=='PASS' and d['status']=='PASS' else 'FAIL';p['promotion_ready_locally']=p['status']=='PASS';return p
    def read(self,uri):
        if uri=='athena://architecture/inventory':return inventory_manifest()
        if uri=='athena://architecture/drift':return {'inventory':inventory_manifest(),'latest':drift(self,False),'law':'declared mature organs must agree across runtime discovery, SURFACE, effective manifest and OMEGA'}
        if uri=='athena://promotion':
            p=old_read(self,uri);p['architecture_drift']=drift(self,False);p['boundary']=str(p.get('boundary',''))+' Declared architecture drift blocks local promotion readiness; unclassified extras remain non-authoritative review pressure.';return p
        return old_read(self,uri)
    def bench(self):
        p=old_bench(self);d=drift(self,False);p.update({'unified_manifest_version':EFFECTIVE_MANIFEST,'organ_inventory_version':COORDINATION_INVENTORY_VERSION,'architecture_drift_version':ARCHITECTURE_DRIFT_VERSION,'architecture_drift_status':d['status'],'architecture_drift_count':d['drift_count'],'unclassified_surface_count':d['unclassified_surface']['count']});return p
    ris.RuntimeIntegritySurface.architecture_drift_audit=drift;ris.RuntimeIntegritySurface.surface_audit=surface;ris.RuntimeIntegritySurface.read_resource=read;ris.RuntimeIntegritySurface.benchmark=bench;ris.build_unified_manifest=um.build_unified_manifest;ris.maxdev_law=um.maxdev_law;ris.UNIFIED_MANIFEST_VERSION=EFFECTIVE_MANIFEST

    # Architecture resources must be visible through AOR development.
    for r in ARCHITECTURE_DRIFT_RESOURCES:
        if r['uri'] not in {x['uri'] for x in ads.AOR_DEVELOPMENT_RESOURCES}:ads.AOR_DEVELOPMENT_RESOURCES.append(dict(r))
        ads.AOR_DEVELOPMENT_RESOURCE_URIS.add(r['uri']);ris.INTEGRITY_RESOURCES.append(dict(r));ris.INTEGRITY_RESOURCE_URIS.add(r['uri'])
    namespace['_ATHENA_COORDINATION_ARCHITECTURE_INSTALLED']=True

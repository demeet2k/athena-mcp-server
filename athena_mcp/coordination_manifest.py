from __future__ import annotations

from typing import Any,Dict

from .architecture_drift import ARCHITECTURE_DRIFT_VERSION,ORGAN_INVENTORY_VERSION,inventory_manifest
from .unified_manifest import LAYERS as BASE_LAYERS,UNIFIED_MANIFEST_VERSION as BASE_MANIFEST_VERSION,build_unified_manifest,maxdev_law

EFFECTIVE_UNIFIED_MANIFEST_VERSION='ATHENA.RUNTIME.UNIFIED.10'
COORDINATION_LAYERS=[
    'MESSAGE_BOARD_V1','COHESION_MESH_V1','COHESION_DUPLICATE_GUARD_V1','COHESION_EVIDENCE_GUARD_V1',
    'AGENT_BOOT_COHESION_TREATMENT_V1','PARTY_COORDINATION_V1','PARTY_CHANNEL_V2','PARTY_REWARD_PROVENANCE_V3',
    'ORGAN_INVENTORY.1','ARCHITECTURE_DRIFT_AUDIT.1',
]
COORDINATION_INVARIANTS=[
    'Y1_SEMANTIC_CLAIM_AUTHORITY != MESSAGE_BOARD_COORDINATION_PRESENCE_CLAIM_AUTHORITY',
    'MESSAGE_BOARD = SOLE_PRESENCE_CLAIM_MESSAGE_AUTHORITY; BOARD_STATE != EXECUTION_AUTHORITY != WORLD_TRUTH',
    'COHESION != CLAIM_AUTHORITY != ASSIGNMENT_AUTHORITY != EXECUTION_AUTHORITY',
    'FUZZY_SIMILARITY != DUPLICATE_PROOF; TREATMENT_OPTION != TREATMENT_EXECUTION',
    'PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE != SUFFICIENT_COMPARATIVE_EVIDENCE; CAUSAL_EFFECT = UNKNOWN',
    'PARTY_RESULT != RESULT_TRUTH; PARTY_REWARD_PROVENANCE != GLOBAL_XP_AUTHORITY',
    'MATURE_ORGAN_CODE_OR_TOOL_EXISTENCE != CONSTITUTIONAL_INTEGRATION',
]


def effective_layers():
    return list(dict.fromkeys(list(BASE_LAYERS)+COORDINATION_LAYERS))


def build_effective_manifest(server)->Dict[str,Any]:
    base=dict(build_unified_manifest(server));inventory=inventory_manifest()
    compat=list(base.get('artifact_compat') or [])+[str(base.get('artifact') or BASE_MANIFEST_VERSION)]
    base['artifact']=EFFECTIVE_UNIFIED_MANIFEST_VERSION
    base['artifact_compat']=list(dict.fromkeys(compat))
    base['layers']=effective_layers()
    base['invariants']=list(dict.fromkeys(list(base.get('invariants') or [])+COORDINATION_INVARIANTS))
    base['navigation']=str(base.get('navigation') or '')+' <-> MessageBoard/Cohesion/PartyCoordination'
    organs=dict(base.get('organs') or {})
    organs['coordination']={
        'inventory_version':ORGAN_INVENTORY_VERSION,
        'architecture_drift_version':ARCHITECTURE_DRIFT_VERSION,
        'organs':[{
            'id':organ['id'],'version':organ['version'],'integration_class':organ['integration_class'],
            'authority_plane':organ['authority_plane'],'manifest_layer':organ['manifest_layer'],
        } for organ in inventory['organs']],
        'law':'coordination maturity is explicit; Message Board coordination claims never alias Y1 semantic authority; Cohesion and Party reward remain advisory/provenance planes',
    }
    base['organs']=organs
    unresolved=list(base.get('unresolved') or [])
    unresolved=[row for row in unresolved if row.get('id')!='ORGAN_INVENTORY_EXPANSION']
    unresolved.append({
        'id':'ORGAN_INVENTORY_EXPANSION','status':'ACTIVE_RECURSIVE_FRONTIER',
        'boundary':'initial inventory covers Message Board, Cohesion, bootstrap treatment and Party V1-V3; additional post-V13 extension families such as Frontier/Rehydration/Campaign/QHUG/Mythic/Bionano must be classified explicitly before architecture maturity is claimed',
    })
    base['unresolved']=unresolved
    base['architecture_drift']={
        'version':ARCHITECTURE_DRIFT_VERSION,'inventory_version':ORGAN_INVENTORY_VERSION,
        'law':'promotion local readiness requires every declared mature organ to agree across live surface, SURFACE contract, effective manifest and OMEGA; repository CI/source witnesses are enforced separately',
    }
    base['braid_law']=str(base.get('braid_law') or '')+' Message Board coordination authority is separate from Y1 semantic authority; declared organ drift blocks local promotion readiness.'
    return base


def effective_maxdev_law()->str:
    return maxdev_law()+'''\n31 COORDINATION AUTHORITY: Message Board owns presence/coordination claims and messages; Y1 owns canonical semantic claims. Never alias these planes.\n32 COHESION: matchmaking, duplicate treatment and evidence coverage are advisory/read-only membranes; options/comparisons do not execute assignments, claims, truth or XP.\n33 PARTY: party messages/results use Message Board transport; reward provenance is bounded and cannot create result truth or global XP authority.\n34 ARCHITECTURE DRIFT: before promotion, require every declared mature organ to exist in the live runtime surface, SURFACE contract, effective manifest and OMEGA coordinate.\n35 INVENTORY EXPANSION: expose unclassified live tools/resources as recursive maturity-review pressure; do not auto-canonicalize them by file/tool existence.'''

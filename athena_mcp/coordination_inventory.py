from __future__ import annotations

from typing import Any

from .architecture_drift import ORGAN_INVENTORY_VERSION as BASE_INVENTORY_VERSION,MATURE_ORGANS as BASE_MATURE_ORGANS

COORDINATION_INVENTORY_VERSION='ATHENA.ORGAN.INVENTORY.1.1'
PARTY_REWARD_VERSION='PARTY.REWARD.PROVENANCE.3.2'

PARTY_REWARD_V32={
    'id':'PARTY_REWARD_PROVENANCE_V3_2','version':PARTY_REWARD_VERSION,
    'integration_class':'PUBLIC_PROVENANCE_AND_NUMERIC_MEMBRANE','authority_plane':'PARTY_REWARD_PROVENANCE_ONLY',
    'manifest_layer':'PARTY_REWARD_PROVENANCE_V3_2','omega_key':'coordination',
    'tools':['athena_party_result'],'resources':[],
    'critical_tests':['tests/test_party_reward_provenance.py','tests/test_party_reward_v3_1.py','tests/test_party_reward_v3_2.py'],
    'spec_refs':[],
    'source_refs':['athena_mcp/party_coordination_v3.py','athena_mcp/party_coordination_v3_1.py','athena_mcp/party_coordination_v3_2.py','athena_mcp/party_coordination_v3_protocol.py'],
    'laws':[
        'PARTY_RESULT != RESULT_TRUTH','PARTY_RESULT != GLOBAL_XP_AUTHORITY','SOURCE_XP_REUSE != NEW_REWARD','ROOT_WORK_DIVERSITY_REQUIRED',
        'V3_PACKET_VERSION_REQUIRED','INNER_RESULT_VERIFY_MUST_MATCH_OUTER_MESSAGE_BOARD_ROLE',
        'BASE_XP_MUST_BE_FINITE_NON_BOOLEAN_BEFORE_PARTY_REWARD_PROCESSING','FINITE_NUMERIC_VALIDATION != UPSTREAM_XP_VERIFICATION_OR_MINT_AUTHORITY',
    ],
}


def mature_organs()->tuple[dict[str,Any],...]:
    rows=[]
    for raw in BASE_MATURE_ORGANS:
        row=dict(raw)
        if row.get('id')=='PARTY_REWARD_PROVENANCE_V3':rows.append(dict(PARTY_REWARD_V32))
        else:rows.append(row)
    return tuple(rows)


def inventory_manifest()->dict[str,Any]:
    organs=mature_organs()
    return {
        'version':COORDINATION_INVENTORY_VERSION,'base_inventory_version':BASE_INVENTORY_VERSION,'organs':[dict(row) for row in organs],
        'law':'effective coordination maturity overlays the current Party reward membrane onto the stable explicit organ registry; historical descriptor identity is preserved in the base registry while one active descriptor owns each public maturity surface',
        'party_reward_current':PARTY_REWARD_VERSION,
    }

from __future__ import annotations

ARCHITECTURE_CANDIDATE_VERSION='ATHENA.ARCHITECTURE.CANDIDATES.1'

CANDIDATES=(
    {
        'id':'FRESHNESS_TRAIN_V1',
        'status':'CANDIDATE_NOT_YET_MATURE',
        'integration_class':'INTERNAL_READ_ONLY_REQUALIFICATION_PLANNER',
        'authority_plane':'PLANNING_EVIDENCE_ONLY',
        'public_tools':[],
        'public_resources':[],
        'source_refs':['athena_mcp/freshness_train.py'],
        'critical_tests':['tests/test_freshness_train.py','tests/test_freshness_train_extended.py'],
        'laws':[
            'FRESHNESS_CLASSIFICATION != MERGE_AUTHORITY',
            'FRESHNESS_CLASSIFICATION != PROMOTION_AUTHORITY',
            'HISTORICAL_CI_PASS != CURRENT_INTEGRATION_PASS',
            'UNKNOWN_FRONTIER_OR_DEPENDENCY_STATE -> HOLD_OR_REQUALIFY',
            'FRESHNESS_ANALYSIS = READ_ONLY',
        ],
        'missing_maturity_requirements':[
            'prove a current production/runtime workflow consumes the classifier output in a typed way',
            'prove that consumption cannot mutate Git, Message Board, Y1, XP, or execution authority by adjacency',
            'add an explicit OMEGA/manifest coordinate only after integration exists',
            'add a named critical-CI witness for the actual consuming path, not only the classifier unit tests',
        ],
        'admission_rule':'do not add to mature coordination inventory until every missing_maturity_requirement has a witnessed implementation',
    },
)


def candidate_manifest():
    return {
        'version':ARCHITECTURE_CANDIDATE_VERSION,
        'candidates':[dict(row) for row in CANDIDATES],
        'law':'candidate registration makes residual architecture visible without granting maturity, authority, promotion eligibility, or runtime surface requirements',
    }

from __future__ import annotations

RETRIEVAL_VERSION='RAG.1'
RETRIEVAL_ROLES=('direct','ancestor','sibling','contradiction','bridge','precedent','failed_attempt','witness','successor')
REQUIRED_MEASUREMENTS=('relevance','source_authority','cross_value','decision_relevance')
MEASUREMENT_RANGE=(0.0,1.0)
EXACT_SELECTION_LIMIT=18

def retrieval_law():
    return {'version':RETRIEVAL_VERSION,'boundary':'compiler ranks only supplied candidate provenance records; it never claims unseen search/retrieval','score':'relevance * source_authority * freshness * cross_value * coordinate_fit * lineage_fit * decision_relevance / cost','unknown':'missing required measurement/timestamp/cost => non-rankable + measurement_plan','freshness':'exp(-ln(2)*age/half_life); timeless candidates may explicitly declare timeless=true','authority_separation':'source_authority is measured retrieval provenance quality, not typed claim Y authority','coverage':'selection utility combines normalized source score with explicit required role/facet coverage','equivalence':'only supplied EQ1 collapse-safe groups may suppress candidates; unknown/conflict preserves identity','exact_limit':EXACT_SELECTION_LIMIT,'large_frontier':'deterministic marginal-utility greedy; HEURISTIC_NOT_PROVEN','replay':'RAGRUN stores query spec + supplied candidate records + frozen EQ snapshot + compiler output + decision digest','memory_firewall':'pheromone/reuse may guide which candidates are supplied upstream, but is not inserted as relevance/evidence/source_authority automatically'}

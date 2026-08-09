import tomllib
import unittest
from pathlib import Path

import athena_mcp
from athena_mcp.coordination_inventory import COORDINATION_INVENTORY_VERSION,PARTY_REWARD_VERSION
from athena_mcp.coordination_manifest import EFFECTIVE_UNIFIED_MANIFEST_VERSION
from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.promotion import PROMOTION_VERSION
from athena_mcp.unified_manifest import UNIFIED_MANIFEST_VERSION

ROOT=Path(__file__).resolve().parents[1]
def text(path:str)->str:return (ROOT/path).read_text(encoding='utf-8')


class DocumentationConsistencyTests(unittest.TestCase):
    def test_release_base_and_effective_architecture_coordinates_agree(self):
        project=tomllib.loads(text('pyproject.toml'))['project']
        self.assertEqual(project['version'],'3.2.0');self.assertEqual(athena_mcp.__version__,'3.2.0')
        self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.9');self.assertEqual(EFFECTIVE_UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.10')
        self.assertEqual(COORDINATION_INVENTORY_VERSION,'ATHENA.ORGAN.INVENTORY.1.1');self.assertEqual(PARTY_REWARD_VERSION,'PARTY.REWARD.PROVENANCE.3.2')
        self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2');self.assertEqual(GITHUB_PROMOTION_VERIFIER_VERSION,'ATHENA.GITHUB.PROMOTION.VERIFIER.1')

        for path in ('README.md','ARCHITECTURE.md','MIGRATION.md','spec/ATHENA_UNIFIED_V13.md'):
            body=text(path);self.assertIn('3.2',body);self.assertIn('UNIFIED.9',body)
        self.assertIn('COLLECTIVE_ROBUST=<HB,FG,JD,FC,LT,DP,DR,L>',text('README.md'))
        self.assertIn('STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION',text('ARCHITECTURE.md'))

        current=text('CURRENT_ARCHITECTURE.md')
        for phrase in ('ATHENA.RUNTIME.UNIFIED.10','UNIFIED.10 = UNIFIED.9 + COORDINATION_ARCHITECTURE_V1','MESSAGE_BOARD_V1','COHESION_MESH_V1','PARTY_REWARD_PROVENANCE_V3_2','ATHENA.ORGAN.INVENTORY.1.1','V3.1','V3.2','FINITE_NUMERIC_VALIDATION != UPSTREAM_XP_VERIFICATION_OR_MINT_AUTHORITY','Freshness Train','unclassified_surface'):
            self.assertIn(phrase,current)
        coord=text('spec/ATHENA_COORDINATION_ARCHITECTURE_V1.md')
        for phrase in ('Y1 != MB','FUZZY_SIMILARITY != DUPLICATE_PROOF','CAUSAL_EFFECT = UNKNOWN','PARTY_RESULT != RESULT_TRUTH','V3_PACKET_VERSION_REQUIRED','BASE_XP_MUST_BE_FINITE_NON_BOOLEAN_BEFORE_PARTY_REWARD_PROCESSING','ATHENA.ORGAN.INVENTORY.1.1','ARCHITECTURE_DRIFT.1','OBSERVE_EXPANSION_FRONTIER','Freshness Train'):
            self.assertIn(phrase,coord)

    def test_v13_scientific_contract_is_preserved_under_overlay(self):
        v13=text('spec/ATHENA_UNIFIED_V13.md')
        for phrase in ('athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select','STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION'):
            self.assertIn(phrase,v13)
        upstream=text('spec/COLLECTIVE_RUNTIME_V13.md')
        for phrase in ('ATHENA COLLECTIVE RUNTIME V13','FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM','BOUNDED_FCI_LITE != FCI_RFCI_PAG_THEOREM','DYNAMIC_GFORMULA_POLICY_VALUE != GENERAL_OFF_POLICY_CAUSAL_VALUE'):
            self.assertIn(phrase,upstream)

    def test_executable_witnesses_cover_scientific_and_coordination_planes(self):
        ci=text('.github/workflows/ci.yml')
        for phrase in ('Documentation and repository-brain consistency','Coordination organ inventory and architecture drift','test_architecture_drift.py','test_message_board_registration.py','test_cohesion_evidence_guard.py','test_party_reward_provenance.py','test_party_reward_v3_1.py','test_party_reward_v3_2.py','V13 robust continuous-bayes causal-control and authority boundaries','Promotion trust and exact-head predicate','promotion-qualification'):
            self.assertIn(phrase,ci)
        drift=text('athena_mcp/architecture_drift.py')
        for phrase in ('ATHENA.ORGAN.INVENTORY.1','ATHENA.ARCHITECTURE.DRIFT.1','MESSAGE_BOARD_V1','COHESION_EVIDENCE_GUARD_V1','unclassified_surface'):
            self.assertIn(phrase,drift)
        overlay=text('athena_mcp/coordination_inventory.py')
        for phrase in ('ATHENA.ORGAN.INVENTORY.1.1','PARTY.REWARD.PROVENANCE.3.2','V3_PACKET_VERSION_REQUIRED','BASE_XP_MUST_BE_FINITE_NON_BOOLEAN_BEFORE_PARTY_REWARD_PROCESSING'):
            self.assertIn(phrase,overlay)
        effective=text('athena_mcp/coordination_manifest.py')
        for phrase in ('ATHENA.RUNTIME.UNIFIED.10','MESSAGE_BOARD_V1','PARTY_REWARD_PROVENANCE_V3_2','ARCHITECTURE_DRIFT_AUDIT.1','ORGAN_INVENTORY_EXPANSION','Freshness Train'):
            self.assertIn(phrase,effective)


if __name__=='__main__':unittest.main()

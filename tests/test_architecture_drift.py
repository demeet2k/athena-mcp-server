import tempfile
import unittest
from pathlib import Path

from athena_mcp.architecture_drift import MATURE_ORGANS,audit_architecture,inventory_manifest
from athena_mcp.server import Server


class ArchitectureDriftTests(unittest.TestCase):
    def test_declared_mature_organ_missing_surface_or_coordinate_fails(self):
        organ=MATURE_ORGANS[0]
        out=audit_architecture(
            observed_tools=[],observed_resources=[],manifest_layers=[],surface_required_tools=[],surface_required_resources=[],omega_components=[],
            organs=[organ],
        )
        self.assertEqual(out['status'],'ARCHITECTURE_DRIFT')
        kinds={row['kind'] for row in out['defects']}
        self.assertIn('RUNTIME_TOOL_MISSING',kinds);self.assertIn('MANIFEST_LAYER_MISSING',kinds);self.assertIn('OMEGA_COORDINATE_MISSING',kinds)

    def test_internal_membranes_do_not_require_fake_rpc_surfaces(self):
        by_id={row['id']:row for row in MATURE_ORGANS}
        for oid in ('COHESION_EVIDENCE_GUARD_V1','AGENT_BOOT_COHESION_TREATMENT_V1'):
            self.assertEqual(by_id[oid]['tools'],[]);self.assertEqual(by_id[oid]['resources'],[])
        self.assertIn('PROMOTION_AUTHORITY = FALSE',by_id['COHESION_EVIDENCE_GUARD_V1']['laws'])

    def test_semantic_and_coordination_claim_authority_are_distinct_planes(self):
        board=next(row for row in MATURE_ORGANS if row['id']=='MESSAGE_BOARD_V1')
        self.assertEqual(board['authority_plane'],'COORDINATION_PRESENCE_CLAIM_MESSAGE')
        self.assertIn('MESSAGE_BOARD != Y1_CANONICAL_SEMANTIC_AUTHORITY',board['laws'])

    def test_live_server_passes_declared_runtime_drift_and_exposes_expansion_frontier(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            try:
                audit=srv.aor_development.integrity.architecture_drift_audit(False)
                self.assertEqual(audit['status'],'PASS',audit)
                ids={row['id'] for row in audit['organs'] if row['status']=='PASS'}
                for expected in ('MESSAGE_BOARD_V1','COHESION_MESH_V1','COHESION_DUPLICATE_GUARD_V1','COHESION_EVIDENCE_GUARD_V1','PARTY_COORDINATION_V1','PARTY_CHANNEL_V2','PARTY_REWARD_PROVENANCE_V3'):
                    self.assertIn(expected,ids)
                # Extra surfaces are a deterministic follow-on inventory frontier,
                # not automatic maturity and not a reason to hide the current PASS.
                self.assertIn(audit['unclassified_surface']['status'],{'EMPTY','OBSERVE_EXPANSION_FRONTIER'})
                self.assertEqual(audit['drift_count'],0)
            finally:srv.store.close()

    def test_repository_witness_audit_passes_current_declared_inventory(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            try:
                audit=srv.aor_development.integrity.architecture_drift_audit(True)
                self.assertEqual(audit['status'],'PASS',audit)
            finally:srv.store.close()

    def test_inventory_is_explicit_and_not_filesystem_discovery(self):
        inv=inventory_manifest();self.assertEqual(inv['version'],'ATHENA.ORGAN.INVENTORY.1')
        ids=[row['id'] for row in inv['organs']]
        self.assertEqual(len(ids),len(set(ids)));self.assertGreaterEqual(len(ids),8)
        self.assertTrue(all(row.get('integration_class') and row.get('authority_plane') for row in inv['organs']))


if __name__=='__main__':unittest.main()

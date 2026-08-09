import unittest

from athena_mcp.deployment import (
    ACTIVATION_RECEIPT_VERSION,
    HTTP_ADAPTER_VERSION,
    activation_plan,
    assess_canary,
    validate_bundle,
    validate_image_ref,
    verify_activation_receipt,
)

IMAGE = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "a" * 64
CURRENT_IMAGE = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "b" * 64
SOURCE = "c" * 40
SNAPSHOT_DIGEST = "sha256:" + "d" * 64


class DeploymentContractV2Tests(unittest.TestCase):
    def test_image_and_bundle_are_exact_and_source_bound(self):
        self.assertTrue(validate_image_ref(IMAGE)["immutable"])
        with self.assertRaises(ValueError):
            validate_image_ref("ghcr.io/demeet2k/athena-mcp-server:latest")
        bundle = {
            "schema": "ATHENA.DEPLOYMENT.BUNDLE.2",
            "image_ref": IMAGE,
            "expected_current_image_ref": CURRENT_IMAGE,
            "source_head": SOURCE,
            "image_source_head": SOURCE,
            "transport": HTTP_ADAPTER_VERSION,
            "state_mode": "SINGLE_WRITER",
            "replicas": 1,
            "token_secret_ref": "secret-ref://athena/http-token",
            "allow_insecure_http": False,
            "database_backup_witness": "backup-ref://pre-cutover",
            "state_snapshot_ref": "snapshot-ref://pre-cutover",
            "state_snapshot_digest": SNAPSHOT_DIGEST,
            "release_attestation_ref": "attestation-ref://exact-head",
            "sbom_ref": "sbom-ref://application-spdx",
        }
        result = validate_bundle(bundle)
        self.assertEqual(result["status"], "PASS", result)
        bundle["image_source_head"] = "e" * 40
        result = validate_bundle(bundle)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("image_source_head", {item["field"] for item in result["defects"]})

    def test_canary_requires_complete_and_sufficient_observation(self):
        baseline = {"error_rate": 0.01, "p95_ms": 100.0, "restart_count": 0}
        self.assertEqual(assess_canary(baseline, {})["decision"], "HOLD")
        thin = assess_canary(
            baseline,
            {
                "error_rate": 0.01,
                "p95_ms": 105.0,
                "restart_count": 0,
                "ready": True,
                "schema_up_to_date": True,
                "replay_match": True,
                "sample_count": 5,
                "observation_window_seconds": 10,
            },
        )
        self.assertEqual(thin["decision"], "ROLLBACK")
        self.assertIn("sample_count", thin["failed_gates"])
        passed = assess_canary(
            baseline,
            {
                "error_rate": 0.01,
                "p95_ms": 105.0,
                "restart_count": 0,
                "ready": True,
                "schema_up_to_date": True,
                "replay_match": True,
                "sample_count": 50,
                "observation_window_seconds": 120,
            },
        )
        self.assertEqual(passed["decision"], "PROMOTE", passed)

    def test_plan_and_receipt_replay_bind_every_coordinate(self):
        plan = activation_plan(
            IMAGE,
            source_head=SOURCE,
            state_snapshot_ref="snapshot-ref://pre-cutover",
            state_snapshot_digest=SNAPSHOT_DIGEST,
            token_secret_ref="secret-ref://athena/http-token",
            release_attestation_ref="attestation-ref://exact-head",
            sbom_ref="sbom-ref://application-spdx",
            expected_current_image_ref=CURRENT_IMAGE,
        )
        receipt = {
            "schema": ACTIVATION_RECEIPT_VERSION,
            "status": "ACTIVATED",
            "plan_digest": plan["plan_digest"],
            "image_ref": IMAGE,
            "source_head": SOURCE,
            "state_snapshot_ref": "snapshot-ref://pre-cutover",
            "state_snapshot_digest": SNAPSHOT_DIGEST,
            "cutover_authority_ref": "authority-ref://production-cutover-42",
            "executor_receipt_ref": "executor-ref://cluster-receipt-42",
            "observed_at": "2026-08-08T00:00:00Z",
            "observations": {"ready": True, "replay_match": True},
        }
        kwargs = {
            "expected_plan_digest": plan["plan_digest"],
            "expected_image_ref": IMAGE,
            "expected_source_head": SOURCE,
            "expected_state_snapshot_ref": "snapshot-ref://pre-cutover",
            "expected_state_snapshot_digest": SNAPSHOT_DIGEST,
        }
        self.assertTrue(verify_activation_receipt(receipt, **kwargs)["verified"])
        receipt["image_ref"] = CURRENT_IMAGE
        rejected = verify_activation_receipt(receipt, **kwargs)
        self.assertFalse(rejected["verified"])
        self.assertEqual(rejected["checks"]["image_ref"], "FAIL")


if __name__ == "__main__":
    unittest.main()

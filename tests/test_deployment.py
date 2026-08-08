import unittest

from athena_mcp.deployment import (
    HTTP_ADAPTER_VERSION,
    activation_plan,
    assess_canary,
    manifest,
    validate_bundle,
    validate_image_ref,
)


class DeploymentContractTests(unittest.TestCase):
    def setUp(self):
        self.image = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "a" * 64

    def test_manifest_preserves_transport_state_and_authority_boundaries(self):
        value = manifest()
        self.assertEqual(value["version"], "ATHENA.DEPLOYMENT.1")
        self.assertEqual(value["runtime"]["adapter"], HTTP_ADAPTER_VERSION)
        self.assertEqual(value["persistence"]["mode"], "SINGLE_WRITER")
        self.assertFalse(value["persistence"]["active_active_supported"])
        self.assertIn("not proof", value["authority_boundary"])
        self.assertRegex(value["manifest_digest"], r"^[0-9a-f]{64}$")

    def test_production_image_requires_digest(self):
        value = validate_image_ref(self.image)
        self.assertTrue(value["immutable"])
        self.assertEqual(value["status"], "PASS")
        with self.assertRaises(ValueError):
            validate_image_ref("ghcr.io/demeet2k/athena-mcp-server:3.1.0")
        tagged = validate_image_ref(
            "ghcr.io/demeet2k/athena-mcp-server:3.1.0", require_digest=False
        )
        self.assertFalse(tagged["immutable"])

    def test_bundle_and_activation_plan_fail_closed(self):
        bundle = {
            "schema": "ATHENA.DEPLOYMENT.BUNDLE.1",
            "image_ref": self.image,
            "transport": HTTP_ADAPTER_VERSION,
            "state_mode": "SINGLE_WRITER",
            "token_secret_ref": "secret://athena-http-auth/token",
            "allow_insecure_http": False,
            "database_backup_witness": "backup://snapshot-1",
        }
        self.assertEqual(validate_bundle(bundle)["status"], "PASS")
        broken = dict(bundle, allow_insecure_http=True)
        self.assertEqual(validate_bundle(broken)["status"], "FAIL")
        plan = activation_plan(
            self.image,
            state_snapshot_ref="backup://snapshot-1",
            token_secret_ref="secret://athena-http-auth/token",
        )
        self.assertEqual(plan["status"], "PLAN_ONLY")
        self.assertEqual(plan["replicas"], 1)
        self.assertEqual(plan["stages"][1]["name"], "ISOLATED_CANARY")
        with self.assertRaises(ValueError):
            activation_plan(
                self.image,
                replicas=2,
                state_snapshot_ref="backup://snapshot-1",
                token_secret_ref="secret://athena-http-auth/token",
            )

    def test_canary_missing_observation_holds_and_failed_gate_rolls_back(self):
        hold = assess_canary({}, {})
        self.assertEqual(hold["decision"], "HOLD")
        baseline = {"error_rate": 0.01, "p95_ms": 100, "restart_count": 0}
        healthy = {
            "error_rate": 0.015,
            "p95_ms": 110,
            "restart_count": 0,
            "ready": True,
            "schema_up_to_date": True,
            "replay_match": True,
        }
        self.assertEqual(assess_canary(baseline, healthy)["decision"], "PROMOTE")
        failed = dict(healthy, replay_match=False)
        result = assess_canary(baseline, failed)
        self.assertEqual(result["decision"], "ROLLBACK")
        self.assertIn("replay", result["failed_gates"])


if __name__ == "__main__":
    unittest.main()

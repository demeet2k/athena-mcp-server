import pathlib
import unittest

from athena_mcp.deployment import assess_canary
from deploy.canary_observer import (
    COMPARISON_KIND,
    MINIMUM_OBSERVATION_WINDOW_SECONDS,
    MINIMUM_SAMPLE_COUNT,
    OBSERVER_VERSION,
    WITNESS_VERSION,
    compile_witness,
    inventory_digest,
    observe_pair,
    percentile,
    summarize_samples,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMAGE = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "a" * 64
SOURCE = "b" * 40
WORKFLOW_HEAD = "c" * 40


def catalog(seed: str = "same") -> dict:
    return {
        "tool_count": 3,
        "tool_inventory_digest": inventory_digest(["a", "b", seed]),
        "resource_count": 2,
        "resource_inventory_digest": inventory_digest(["x", seed]),
        "deployment_manifest_digest": "sha256:" + "d" * 64,
        "deployment_version": "ATHENA.DEPLOYMENT.2",
    }


def synthetic_samples(count: int, latency: float = 10.0, failures: int = 0) -> list[dict]:
    values = []
    for index in range(count):
        success = index >= failures
        values.append(
            {
                "sample_id": f"s-{index}",
                "success": success,
                "latency_ms": latency + index / 100.0,
                "ready_status": "READY" if success else None,
                "deployment_manifest_digest": "sha256:" + "d" * 64 if success else None,
                "error": None if success else "synthetic failure",
            }
        )
    return values


class DeploymentCanaryObserverV3Tests(unittest.TestCase):
    def test_percentile_is_deterministic_and_validated(self):
        self.assertEqual(percentile([1.0], 0.95), 1.0)
        self.assertAlmostEqual(percentile([1.0, 2.0, 3.0, 4.0], 0.5), 2.5)
        self.assertAlmostEqual(percentile([1.0, 2.0, 3.0, 4.0], 0.95), 3.85)
        with self.assertRaises(ValueError):
            percentile([], 0.95)
        with self.assertRaises(ValueError):
            percentile([1.0], 1.1)

    def test_sample_summary_distinguishes_planned_from_unexpected_restart(self):
        summary = summarize_samples(
            synthetic_samples(31, failures=1),
            raw_restart_count=1,
            planned_restart_count=1,
        )
        self.assertEqual(summary["sample_count"], 31)
        self.assertEqual(summary["failed_samples"], 1)
        self.assertAlmostEqual(summary["error_rate"], 1 / 31)
        self.assertEqual(summary["restart_count"], 0)
        self.assertEqual(summary["raw_restart_count"], 1)
        self.assertFalse(summary["all_ready"])

    def test_complete_same_digest_observation_can_reach_bounded_promote(self):
        baseline_summary = summarize_samples(
            synthetic_samples(31, latency=10.0),
            raw_restart_count=1,
            planned_restart_count=1,
        )
        canary_summary = summarize_samples(
            synthetic_samples(31, latency=10.5),
            raw_restart_count=1,
            planned_restart_count=1,
        )
        baseline = {
            "error_rate": baseline_summary["error_rate"],
            "p95_ms": baseline_summary["p95_ms"],
            "restart_count": baseline_summary["restart_count"],
        }
        candidate = {
            "error_rate": canary_summary["error_rate"],
            "p95_ms": canary_summary["p95_ms"],
            "restart_count": canary_summary["restart_count"],
            "ready": True,
            "schema_up_to_date": True,
            "replay_match": True,
            "sample_count": 31,
            "observation_window_seconds": 63,
        }
        assessment = assess_canary(baseline, candidate)
        self.assertEqual(assessment["decision"], "PROMOTE", assessment)
        self.assertEqual(assessment["status"], "PASS")

    def test_replay_failure_or_latency_regression_rolls_back(self):
        baseline = {"error_rate": 0.0, "p95_ms": 10.0, "restart_count": 0}
        candidate = {
            "error_rate": 0.0,
            "p95_ms": 20.0,
            "restart_count": 0,
            "ready": True,
            "schema_up_to_date": True,
            "replay_match": False,
            "sample_count": 31,
            "observation_window_seconds": 63,
        }
        assessment = assess_canary(baseline, candidate)
        self.assertEqual(assessment["decision"], "ROLLBACK")
        self.assertIn("latency", assessment["failed_gates"])
        self.assertIn("replay", assessment["failed_gates"])

    def test_witness_binds_all_release_coordinates_and_denies_cutover(self):
        control_catalog = catalog()
        canary_catalog = catalog()
        baseline = {
            "error_rate": 0.0,
            "p95_ms": 10.0,
            "restart_count": 0,
            "sample_count": 31,
            "all_ready": True,
        }
        candidate = {
            "error_rate": 0.0,
            "p95_ms": 10.2,
            "restart_count": 0,
            "sample_count": 31,
            "all_ready": True,
            "ready": True,
            "schema_up_to_date": True,
            "replay_match": True,
            "observation_window_seconds": 63,
        }
        assessment = assess_canary(
            {key: baseline[key] for key in ("error_rate", "p95_ms", "restart_count")},
            {
                key: candidate[key]
                for key in (
                    "error_rate",
                    "p95_ms",
                    "restart_count",
                    "ready",
                    "schema_up_to_date",
                    "replay_match",
                    "sample_count",
                    "observation_window_seconds",
                )
            },
        )
        witness = compile_witness(
            image_ref=IMAGE,
            source_head=SOURCE,
            release_tag="v3.3.0",
            release_run_id="31297502454",
            oci_run_id="31298729440",
            workflow_run_id="999",
            workflow_head=WORKFLOW_HEAD,
            control_catalog=control_catalog,
            canary_catalog=canary_catalog,
            state_witness={"oid": "oid:1", "registered": True, "matched": True},
            baseline_metrics=baseline,
            canary_metrics=candidate,
            assessment=assessment,
            observation_window_seconds=63,
            observed_at="2026-08-09T07:00:00Z",
        )
        self.assertEqual(witness["schema"], WITNESS_VERSION)
        self.assertEqual(witness["observer"], OBSERVER_VERSION)
        self.assertEqual(witness["comparison_kind"], COMPARISON_KIND)
        self.assertEqual(witness["image_ref"], IMAGE)
        self.assertEqual(witness["source_head"], SOURCE)
        self.assertEqual(witness["release_run_id"], "31297502454")
        self.assertEqual(witness["oci_run_id"], "31298729440")
        self.assertTrue(all(witness["structural_match"].values()))
        self.assertTrue(witness["witness_digest"].startswith("sha256:"))
        self.assertEqual(
            witness["authority"],
            {
                "cutover_authorized": False,
                "cluster_apply_authorized": False,
                "traffic_activation_authorized": False,
                "production_secret_provisioned": False,
                "production_state_contacted": False,
            },
        )
        self.assertNotIn("token", str(witness).lower())

    def test_structural_mismatch_is_preserved_not_hidden(self):
        assessment = {
            "version": "ATHENA.CANARY.ASSESSMENT.2",
            "decision": "ROLLBACK",
            "status": "FAIL",
        }
        witness = compile_witness(
            image_ref=IMAGE,
            source_head=SOURCE,
            release_tag="v3.3.0",
            release_run_id="1",
            oci_run_id="2",
            workflow_run_id="3",
            workflow_head=WORKFLOW_HEAD,
            control_catalog=catalog("control"),
            canary_catalog=catalog("canary"),
            state_witness={"matched": False},
            baseline_metrics={"error_rate": 0.0, "p95_ms": 1.0, "restart_count": 0},
            canary_metrics={"error_rate": 1.0, "p95_ms": 2.0, "restart_count": 1},
            assessment=assessment,
            observation_window_seconds=63,
            observed_at="2026-08-09T07:00:00Z",
        )
        self.assertFalse(witness["structural_match"]["tool_inventory"])
        self.assertFalse(witness["structural_match"]["resource_inventory"])
        self.assertFalse(witness["structural_match"]["state_restart_replay"])

    def test_observer_rejects_thin_window_before_network_contact(self):
        with self.assertRaises(ValueError):
            observe_pair(
                "http://127.0.0.1:1",
                "control-token",
                "http://127.0.0.1:2",
                "canary-token",
                sample_count=MINIMUM_SAMPLE_COUNT - 1,
                interval_seconds=1.0,
                timeout=0.01,
            )
        self.assertEqual(MINIMUM_SAMPLE_COUNT, 30)
        self.assertEqual(MINIMUM_OBSERVATION_WINDOW_SECONDS, 60)

    def test_workflow_is_one_shot_isolated_and_release_bound(self):
        workflow = (ROOT / ".github" / "workflows" / "canary-v3.3.yml").read_text()
        for fragment in (
            "Observe ATHENA v3.3.0 isolated canary",
            "11211341adf599ae78784cce4ded39f21ee71ef7",
            "31297502454",
            "31298729440",
            "sha256:d7eada158c5f202dd7a061218188d0c00b7317c867bedc742857a7b90298d8be",
            "REPLICATED_SAME_DIGEST_STATE_RESTART",
            "--sample-count 31",
            "--interval-seconds 2.1",
            "--minimum-window-seconds 60",
            "athena-v3-control-state:/var/lib/athena",
            "athena-v3-canary-state:/var/lib/athena",
            "canary-witness.v3.3.0.json",
            "SHA256SUMS.canary",
            "gh release upload",
        ):
            self.assertIn(fragment, workflow)
        for forbidden in (
            "kubectl apply",
            "helm upgrade",
            "docker service update",
            "terraform apply",
            "cutover_authorized':True",
        ):
            self.assertNotIn(forbidden, workflow)
        observe = workflow[workflow.index("\n  observe:") :]
        self.assertIn("contents: write", observe)
        prefix = workflow[: workflow.index("\n  observe:")]
        self.assertNotIn("contents: write", prefix)


if __name__ == "__main__":
    unittest.main()

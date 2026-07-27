from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.p10_contract import IMAGE, SOURCE_COMMIT
from scripts.p10_persistent_observation_window import (
    MINIMUM_INTERVAL_SECONDS,
    REQUIRED_SAMPLE_CHECKS,
    build_window_receipt,
)
from scripts.p10_provider_evidence import (
    IMAGE_DIGEST,
    RUNTIME_P09_HEAD,
    SCHEMA,
    validate_provider_evidence,
)
from tests.test_p10_deployment_capsule import authorized_target


ROOT = Path(__file__).resolve().parents[1]


def provider_evidence(target: dict) -> dict:
    return {
        "schema": SCHEMA,
        "provider_id": "authorized-provider",
        "provider_account_scope": "logical-account-scope",
        "deployment_id": "deployment-123",
        "target_id": target["target_id"],
        "authorization_ref": target["authorization"]["ref"],
        "deployed_image": IMAGE,
        "image_digest": IMAGE_DIGEST,
        "source_commit": SOURCE_COMMIT,
        "runtime_p09_head": RUNTIME_P09_HEAD,
        "endpoint": target["endpoint"],
        "persistent_service": True,
        "deployment_observed_at": "2026-07-27T05:00:00Z",
        "secret_store_ref": target["secret"]["provider_ref"],
        "secret_material_recorded": False,
        "evidence_url": "https://provider.example/deployments/deployment-123",
    }


def passing_sample(target: dict) -> dict:
    return {
        "schema": "athena.persistent-mcp-witness/v1",
        "verdict": "PASS_LIVE_PERSISTENT_ENDPOINT_NOT_PROMOTED",
        "observed_at": "2026-07-27T05:00:00Z",
        "target": {
            "target_id": target["target_id"],
            "target_digest": "sha256:" + "1" * 64,
            "endpoint": target["endpoint"],
            "persistence_class": target["persistence"]["class"],
            "authorization_ref": target["authorization"]["ref"],
        },
        "deployment": {
            "image": target["image"],
            "image_selection_attestation": "authorized-target-contract",
            "source_commit": target["source_commit"],
            "source_commit_attestation": "host-health-build-locked-file",
            "transport": "streamable-http",
            "authentication": "bearer-present-value-not-recorded",
            "persistent_endpoint": True,
        },
        "checks": {key: True for key in REQUIRED_SAMPLE_CHECKS},
        "catalog": {
            "required_tools_present": True,
            "required_resources_present": True,
        },
        "answer_provenance": {
            "v2_route": {
                "return_plan": [
                    "edge.runtime-to-control",
                    "edge.control-to-q-shrink",
                ]
            },
            "v1_fallback": {
                "answered_by": "athena-108d-v1",
                "fallback_used": True,
            },
        },
        "workflow_run": "https://github.com/demeet2k/athena-mcp-server/actions/runs/1",
        "promotion_ready": False,
        "promotion_claimed": False,
    }


class ProviderEvidenceTests(unittest.TestCase):
    def test_exact_secret_free_evidence_is_admitted(self) -> None:
        target = authorized_target()
        evidence = provider_evidence(target)
        self.assertEqual(validate_provider_evidence(evidence, target), evidence)

    def test_wrong_digest_and_target_binding_fail_closed(self) -> None:
        target = authorized_target()
        for field, value in (
            ("image_digest", "sha256:" + "0" * 64),
            ("target_id", "another-target"),
            ("endpoint", "https://other.example/mcp"),
            ("secret_store_ref", "provider://wrong-secret"),
        ):
            evidence = provider_evidence(target)
            evidence[field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_provider_evidence(evidence, target)

    def test_unknown_or_secret_bearing_fields_fail_closed(self) -> None:
        target = authorized_target()
        for field in ("token", "password", "client_secret", "notes"):
            evidence = provider_evidence(target)
            evidence[field] = "must-never-enter-a-receipt"
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_provider_evidence(evidence, target)

    def test_committed_example_contains_no_claimed_target(self) -> None:
        example = json.loads(
            (ROOT / "deploy/p10/provider-evidence.example.json").read_text()
        )
        self.assertIsNone(example["provider_id"])
        self.assertIsNone(example["endpoint"])
        self.assertFalse(example["secret_material_recorded"])
        encoded = json.dumps(example)
        self.assertNotIn("must-never-enter-a-receipt", encoded)


class ObservationWindowTests(unittest.TestCase):
    def test_window_requires_three_samples_and_twenty_seconds(self) -> None:
        target = authorized_target()
        evidence = validate_provider_evidence(provider_evidence(target), target)
        sample = passing_sample(target)
        with self.assertRaises(ValueError):
            build_window_receipt(
                target, evidence, [sample, sample], MINIMUM_INTERVAL_SECONDS
            )
        with self.assertRaises(ValueError):
            build_window_receipt(
                target, evidence, [sample, sample, sample], 19.9
            )

    def test_window_preserves_return_fallback_and_nonpromotion(self) -> None:
        target = authorized_target()
        evidence = validate_provider_evidence(provider_evidence(target), target)
        samples = [copy.deepcopy(passing_sample(target)) for _ in range(3)]
        receipt = build_window_receipt(
            target, evidence, samples, MINIMUM_INTERVAL_SECONDS
        )
        self.assertEqual(
            receipt["verdict"],
            "PASS_LIVE_PERSISTENT_ENDPOINT_WINDOW_NOT_PROMOTED",
        )
        self.assertEqual(receipt["observation_window"]["sample_count"], 3)
        self.assertEqual(
            receipt["observation_window"]["minimum_elapsed_seconds"], 40.0
        )
        self.assertFalse(receipt["promotion_claimed"])
        encoded = json.dumps(receipt)
        self.assertIn("edge.control-to-q-shrink", encoded)
        self.assertIn("athena-108d-v1", encoded)
        self.assertNotIn("must-never-enter-a-receipt", encoded)

    def test_any_failed_sample_blocks_window_receipt(self) -> None:
        target = authorized_target()
        evidence = validate_provider_evidence(provider_evidence(target), target)
        samples = [copy.deepcopy(passing_sample(target)) for _ in range(3)]
        samples[1]["checks"]["reciprocal_return_answered"] = False
        with self.assertRaises(ValueError):
            build_window_receipt(
                target, evidence, samples, MINIMUM_INTERVAL_SECONDS
            )


if __name__ == "__main__":
    unittest.main()

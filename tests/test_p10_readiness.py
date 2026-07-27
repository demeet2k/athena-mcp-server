from __future__ import annotations

import json
import unittest

from scripts.p10_persistent_witness import (
    MINIMUM_INTERVAL_SECONDS,
    PROVIDER_EVIDENCE_SCHEMA,
    RUNTIME_P09_HEAD,
    SELECTED_IMAGE,
    SELECTED_IMAGE_DIGEST,
    SOURCE_COMMIT,
    build_witness_receipt,
    validate_endpoint,
    validate_provider_evidence,
)


ENDPOINT = "https://athena.example/mcp"


def valid_evidence() -> dict:
    return {
        "schema": PROVIDER_EVIDENCE_SCHEMA,
        "provider_id": "authorized-provider",
        "provider_account_scope": "logical-account-scope",
        "deployment_id": "deployment-123",
        "deployed_image": SELECTED_IMAGE,
        "image_digest": SELECTED_IMAGE_DIGEST,
        "source_commit": SOURCE_COMMIT,
        "runtime_p09_head": RUNTIME_P09_HEAD,
        "endpoint": ENDPOINT,
        "persistent_service": True,
        "deployment_observed_at": "2026-07-27T00:00:00Z",
        "secret_store_ref": "provider://logical-secret-reference",
        "secret_material_recorded": False,
        "evidence_url": "https://provider.example/deployments/deployment-123",
    }


class P10ReadinessTests(unittest.TestCase):
    def test_endpoint_requires_exact_https_mcp_path(self):
        self.assertEqual(validate_endpoint(ENDPOINT), ENDPOINT)
        for invalid in (
            "http://athena.example/mcp",
            "https://athena.example/",
            "https://athena.example/mcp/child",
            "https://athena.example/mcp?token=bad",
            "https://user:password@athena.example/mcp",
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    validate_endpoint(invalid)

    def test_provider_evidence_pins_exact_image_and_source(self):
        normalized = validate_provider_evidence(valid_evidence(), ENDPOINT)
        self.assertEqual(normalized["deployed_image"], SELECTED_IMAGE)
        self.assertEqual(normalized["image_digest"], SELECTED_IMAGE_DIGEST)
        self.assertEqual(normalized["source_commit"], SOURCE_COMMIT)
        self.assertFalse(normalized["secret_material_recorded"])

    def test_provider_evidence_rejects_wrong_digest(self):
        evidence = valid_evidence()
        evidence["image_digest"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            validate_provider_evidence(evidence, ENDPOINT)

    def test_provider_evidence_rejects_secret_or_unknown_fields(self):
        for key in ("token", "password", "client_secret", "notes"):
            evidence = valid_evidence()
            evidence[key] = "must-not-enter-receipt"
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    validate_provider_evidence(evidence, ENDPOINT)

    def test_provider_evidence_requires_persistent_service(self):
        evidence = valid_evidence()
        evidence["persistent_service"] = False
        with self.assertRaises(ValueError):
            validate_provider_evidence(evidence, ENDPOINT)

    def test_witness_preserves_return_v1_and_nonpromotion_boundaries(self):
        evidence = validate_provider_evidence(valid_evidence(), ENDPOINT)
        sample = {
            "observed_at": "2026-07-27T00:00:00Z",
            "checks": {
                "reciprocal_return_answered": True,
                "v1_fallback_answered": True,
                "promotion_boundary": True,
            },
            "health": {
                "status": "ready",
                "deployed_commit": SOURCE_COMMIT,
                "promotion_ready": False,
            },
            "answer_provenance": {
                "v2_route": {
                    "return_plan": [
                        "edge.runtime-to-control",
                        "edge.control-to-q-shrink",
                    ]
                },
                "v1_fallback": {"answered_by": "athena-108d-v1"},
            },
        }
        receipt = build_witness_receipt(
            ENDPOINT,
            evidence,
            [sample, sample, sample],
            MINIMUM_INTERVAL_SECONDS,
        )
        encoded = json.dumps(receipt)
        self.assertEqual(
            receipt["verdict"],
            "PASS_PERSISTENT_ENDPOINT_WITNESSED_NOT_PROMOTED",
        )
        self.assertFalse(receipt["authority"]["promotion_claimed"])
        self.assertNotIn("must-not-enter-receipt", encoded)


if __name__ == "__main__":
    unittest.main()

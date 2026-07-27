from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.p10_activation_packet import (
    AUTHORIZED_STATE,
    CANONICAL_HARDENING_HEAD,
    HANDOFF_SCHEMA,
    INTERVAL_SECONDS,
    MINIMUM_SPAN_SECONDS,
    SAMPLE_COUNT,
    SCHEMA,
    WITNESS_ENVIRONMENT,
    WITNESS_SECRET_NAME,
    compile_activation_packet,
    validate_activation_packet,
    validate_unresolved_template,
)
from scripts.p10_contract import IMAGE, SOURCE_COMMIT
from scripts.p10_provider_evidence import RUNTIME_P09_HEAD


ROOT = Path(__file__).resolve().parents[1]


def authorized_packet() -> dict:
    return {
        "schema": SCHEMA,
        "state": AUTHORIZED_STATE,
        "canonical_hardening_head": CANONICAL_HARDENING_HEAD,
        "source_commit": SOURCE_COMMIT,
        "runtime_p09_head": RUNTIME_P09_HEAD,
        "image": IMAGE,
        "provider": {
            "id": "authorized-provider",
            "account_scope": "logical-account-scope",
            "deployment_id": "deployment-123",
            "deployment_observed_at": "2026-07-27T06:00:00Z",
            "evidence_url": (
                "https://provider.example/deployments/deployment-123"
            ),
        },
        "target": {
            "id": "athena-p10-production",
            "endpoint": "https://athena.example/mcp",
            "persistence_class": "managed-service",
            "secret_store_ref": "provider://secrets/athena-p10-bearer",
        },
        "authorization": {
            "ref": "change-control:approved-123",
            "actor": "authorized-operator",
            "authorized_at": "2026-07-27T05:55:00Z",
        },
        "witness": {
            "environment": WITNESS_ENVIRONMENT,
            "secret_name": WITNESS_SECRET_NAME,
            "sample_count": SAMPLE_COUNT,
            "interval_seconds": INTERVAL_SECONDS,
            "minimum_span_seconds": MINIMUM_SPAN_SECONDS,
        },
        "authority": {
            "live_witness_authorized": True,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        },
        "secret_material_recorded": False,
    }


class ActivationPacketTests(unittest.TestCase):
    def test_authorized_packet_compiles_bound_artifacts(self) -> None:
        packet = authorized_packet()
        target, evidence, receipt = compile_activation_packet(packet)
        self.assertEqual(target["endpoint"], packet["target"]["endpoint"])
        self.assertEqual(evidence["deployment_id"], "deployment-123")
        self.assertEqual(receipt["schema"], HANDOFF_SCHEMA)
        self.assertEqual(
            receipt["verdict"],
            "PASS_AUTHORIZED_WITNESS_HANDOFF_NOT_EXECUTED",
        )
        self.assertFalse(receipt["persistent_endpoint_witnessed"])
        self.assertIsNone(receipt["persistent_witness"])

    def test_committed_template_is_valid_but_not_executable(self) -> None:
        template = json.loads(
            (
                ROOT / "deploy/p10/activation-packet.example.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(validate_unresolved_template(template), template)
        with self.assertRaises(ValueError):
            validate_activation_packet(template)
        self.assertNotIn(
            "must-never-enter-a-receipt",
            json.dumps(template),
        )

    def test_unknown_or_secret_bearing_fields_fail_closed(self) -> None:
        for path, field in (
            ((), "token"),
            (("provider",), "password"),
            (("target",), "client_secret"),
            (("authorization",), "notes"),
        ):
            packet = authorized_packet()
            container = packet
            for segment in path:
                container = container[segment]
            container[field] = "must-never-enter-a-receipt"
            with self.subTest(path=path, field=field):
                with self.assertRaises(ValueError):
                    validate_activation_packet(packet)

    def test_immutable_lineage_mismatch_fails_closed(self) -> None:
        for field, value in (
            ("canonical_hardening_head", "0" * 40),
            ("source_commit", "1" * 40),
            ("runtime_p09_head", "2" * 40),
            ("image", IMAGE.replace("31458783", "00000000")),
        ):
            packet = authorized_packet()
            packet[field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_activation_packet(packet)

    def test_witness_plan_cannot_be_weakened(self) -> None:
        for field, value in (
            ("sample_count", 2),
            ("interval_seconds", 19),
            ("minimum_span_seconds", 39),
            ("environment", "unprotected"),
            ("secret_name", "INLINE_TOKEN"),
        ):
            packet = authorized_packet()
            packet["witness"][field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_activation_packet(packet)

    def test_nonpromotion_boundary_cannot_be_crossed(self) -> None:
        for field, value in (
            ("live_witness_authorized", False),
            ("runtime_can_promote", True),
            ("promotion_claimed", True),
            ("merge_claimed", True),
            ("ic10_required", False),
        ):
            packet = authorized_packet()
            packet["authority"][field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_activation_packet(packet)

    def test_receipt_preserves_return_fallback_and_secret_exclusion(self) -> None:
        _, _, receipt = compile_activation_packet(authorized_packet())
        encoded = json.dumps(receipt)
        self.assertIn("edge.runtime-to-control", encoded)
        self.assertIn("edge.control-to-q-shrink", encoded)
        self.assertIn("athena-108d-v1", encoded)
        self.assertNotIn("must-never-enter-a-receipt", encoded)
        self.assertFalse(receipt["secret_material_recorded"])


if __name__ == "__main__":
    unittest.main()

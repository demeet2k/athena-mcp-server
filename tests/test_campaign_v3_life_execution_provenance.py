from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from athena_mcp.campaign_v3_life_execution_provenance import (
    HOST_ATTESTED,
    PROVENANCE_HOLD,
    RECOGNIZED_EXECUTOR_PROFILES,
    SUPPLIED_UNPROVEN,
    classify_execution_provenance,
    make_untrusted_receipt_shape,
)


class CampaignLifeExecutionProvenanceTests(unittest.TestCase):
    def test_v1_has_no_recognized_executor_profiles(self):
        self.assertEqual({}, RECOGNIZED_EXECUTOR_PROFILES)

    def test_plain_supplied_event_is_explicitly_unproven(self):
        out = classify_execution_provenance(execution_event_id="EVENT-1")
        self.assertEqual("SUPPLIED_EXECUTION_EVENT_UNPROVEN", out["status"])
        self.assertEqual(SUPPLIED_UNPROVEN, out["evidence_class"])
        self.assertFalse(out["semantic_execution_proven"])
        self.assertFalse(out["execution_authority"])

    def test_same_supplied_event_is_deterministic_across_retries(self):
        a = classify_execution_provenance(execution_event_id="EVENT-1")
        b = classify_execution_provenance(execution_event_id="EVENT-1")
        self.assertEqual(a["provenance_digest"], b["provenance_digest"])
        self.assertEqual(a["execution_event_id"], b["execution_event_id"])

    def test_renamed_supplied_event_is_not_proof_of_new_execution(self):
        a = classify_execution_provenance(execution_event_id="EVENT-1")
        b = classify_execution_provenance(execution_event_id="EVENT-2")
        self.assertNotEqual(a["provenance_digest"], b["provenance_digest"])
        self.assertEqual(SUPPLIED_UNPROVEN, a["evidence_class"])
        self.assertEqual(SUPPLIED_UNPROVEN, b["evidence_class"])
        self.assertFalse(a["semantic_execution_proven"])
        self.assertFalse(b["semantic_execution_proven"])

    def test_self_consistent_fake_host_receipt_cannot_upgrade_evidence(self):
        receipt = make_untrusted_receipt_shape(
            executor_id="SELF-CLAIMED-HOST",
            execution_event_id="EVENT-1",
            evidence_ref="request:1",
        )
        out = classify_execution_provenance(
            execution_event_id="EVENT-1",
            executor_receipt=receipt,
        )
        self.assertEqual("HOLD_UNPROVEN_EXECUTOR_ATTESTATION", out["status"])
        self.assertEqual(PROVENANCE_HOLD, out["evidence_class"])
        self.assertIn("unrecognized_executor_profile", out["errors"])
        self.assertFalse(out["semantic_execution_proven"])
        self.assertNotEqual(HOST_ATTESTED, out["evidence_class"])

    def test_transport_or_ledger_labels_do_not_bypass_executor_registry(self):
        for executor_id in ("AOR_COLLECTIVE_TRANSPORT", "CAMPAIGN_V3_LEDGER"):
            receipt = make_untrusted_receipt_shape(
                executor_id=executor_id,
                execution_event_id="EVENT-1",
                evidence_ref=f"{executor_id}:receipt",
            )
            out = classify_execution_provenance(
                execution_event_id="EVENT-1",
                executor_receipt=receipt,
            )
            self.assertEqual("HOLD_UNPROVEN_EXECUTOR_ATTESTATION", out["status"])
            self.assertIn("unrecognized_executor_profile", out["errors"])
            self.assertFalse(out["semantic_execution_proven"])

    def test_bad_receipt_digest_holds(self):
        receipt = make_untrusted_receipt_shape(
            executor_id="SELF-CLAIMED-HOST",
            execution_event_id="EVENT-1",
            evidence_ref="request:1",
        )
        receipt["receipt_digest"] = "0" * 64
        out = classify_execution_provenance(
            execution_event_id="EVENT-1", executor_receipt=receipt
        )
        self.assertIn("executor_receipt_digest", out["errors"])
        self.assertFalse(out["semantic_execution_proven"])

    def test_receipt_event_mismatch_holds(self):
        receipt = make_untrusted_receipt_shape(
            executor_id="SELF-CLAIMED-HOST",
            execution_event_id="EVENT-OTHER",
            evidence_ref="request:1",
        )
        out = classify_execution_provenance(
            execution_event_id="EVENT-1", executor_receipt=receipt
        )
        self.assertIn("executor_receipt_execution_event_id_mismatch", out["errors"])

    @patch(
        "athena_mcp.campaign_v3_life_execution_provenance.validate_campaign_v3_life_attempt_identity",
        return_value=[],
    )
    def test_identity_envelope_event_mismatch_holds(self, _validate):
        envelope = {"execution_event_id": "EVENT-OTHER", "envelope_digest": "digest"}
        out = classify_execution_provenance(
            execution_event_id="EVENT-1", attempt_identity_envelope=envelope
        )
        self.assertEqual("HOLD_EXECUTION_EVENT_ID_MISMATCH", out["status"])
        self.assertFalse(out["semantic_execution_proven"])

    @patch(
        "athena_mcp.campaign_v3_life_execution_provenance.validate_campaign_v3_life_attempt_identity",
        return_value=["semantic_replay_extension_stale_pr"],
    )
    def test_invalid_identity_envelope_holds(self, _validate):
        out = classify_execution_provenance(
            execution_event_id="EVENT-1",
            attempt_identity_envelope={"execution_event_id": "EVENT-1"},
        )
        self.assertEqual("HOLD_INVALID_ATTEMPT_IDENTITY", out["status"])
        self.assertIn("semantic_replay_extension_stale_pr", out["errors"])

    def test_empty_event_id_holds(self):
        out = classify_execution_provenance(execution_event_id="   ")
        self.assertEqual("HOLD_EXECUTION_EVENT_ID_REQUIRED", out["status"])
        self.assertFalse(out["semantic_execution_proven"])


if __name__ == "__main__":
    unittest.main()

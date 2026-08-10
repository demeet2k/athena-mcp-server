from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

import athena_mcp  # noqa: F401 - installs current additive runtime treatments
from athena_mcp import protocol
from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime
from athena_mcp.liminal_beacon_shadow import (
    LiminalBeaconShadowRuntime,
    carrier_snapshot,
    output_digest,
)
from athena_mcp.liminal_beacon_shadow_extension import shadow_mode
from athena_mcp.liminal_beacon_shadow_protocol import LIMINAL_BEACON_SHADOW_TOOL_NAMES


class Clock:
    def __init__(self):
        self.value = 1000.0

    def __call__(self):
        return self.value

    def tick(self, seconds=1.0):
        self.value += float(seconds)


class FakeServer:
    pass


class LiminalBeaconShadowV1Tests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.server = FakeServer()
        self.shadow = LiminalBeaconShadowRuntime(self.server, clock=self.clock)

    def cross(self, tool, arguments, structured):
        token = self.shadow.begin_crossing(tool, arguments)
        domain = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [{"type": "text", "text": json.dumps(structured, sort_keys=True)}],
                "structuredContent": structured,
                "isError": False,
            },
        }
        before = output_digest(domain)
        record = self.shadow.end_crossing(token, tool, arguments, structured, domain, successful=True)
        self.assertEqual(before, output_digest(domain))
        return record, domain

    def test_s0_shadow_mode_is_off_by_default_and_contamination_holds(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(shadow_mode(), "OFF")
        with patch.dict(os.environ, {"ATHENA_LIMINAL_SHADOW": "1"}, clear=True):
            self.assertEqual(shadow_mode(), "SHADOW")
        with patch.dict(
            os.environ,
            {"ATHENA_LIMINAL_SHADOW": "1", "ATHENA_LIMINAL_AUTOHOOK": "1"},
            clear=True,
        ):
            self.assertEqual(shadow_mode(), "HOLD_AUTOHOOK_ACTIVE")

    def test_s1_output_is_digest_identical_and_full_result_is_not_stored(self):
        record, domain = self.cross(
            "tool.alpha",
            {"agent_id": "A", "task": "shared-work"},
            {"status": "OK", "secret_blob": "DO-NOT-COPY-FULL-RESULT" * 20},
        )
        self.assertTrue(record["output_preserved"])
        self.assertNotIn("_liminal_beacon", domain["result"]["structuredContent"])
        status_text = json.dumps(self.shadow.status(include_records=True), sort_keys=True)
        self.assertNotIn("DO-NOT-COPY-FULL-RESULT", status_text)

    def test_s2_source_shadow_has_zero_receipts_and_zero_live_cursors(self):
        self.cross("tool.producer", {"agent_id": "A", "task": "shared"}, {"status": "OK"})
        record, _ = self.cross("tool.consumer", {"agent_id": "B", "task": "shared"}, {"status": "OK"})
        self.assertGreaterEqual(record["would_present_count"], 1)
        source = carrier_snapshot(self.shadow.source)
        self.assertEqual(source["receipt_count"], 0)
        self.assertEqual(source["cursor_nonzero_count"], 0)
        self.assertGreaterEqual(self.shadow.status()["would_present_ledger_count"], 1)

    def test_s3_projection_preview_matches_direct_disposable_v11_projection(self):
        source = self.shadow.source
        source.touch("A", work_refs=["W"], semantic_tags=["route"])
        source.touch("B", work_refs=["W"], semantic_tags=["route"])
        source.emit("A", "RESULT", "bounded result", work_refs=["W"], semantic_tags=["route"])

        direct_projection = self.shadow._projection()
        direct = direct_projection.rendezvous(
            "B", threshold=0.35, context_budget=2400, scout_quota=0, critical_quota=1
        )
        direct_packets = {
            packet["packet_id"] for packet in direct.get("packets") or []
        }
        preview = self.shadow.preview_rendezvous(
            "B", threshold=0.35, context_budget=2400, scout_quota=0, critical_quota=1
        )
        preview_digests = set(preview.get("would_packet_digests") or [])
        expected_digests = {
            __import__("hashlib").sha256(packet_id.encode("utf-8")).hexdigest()[:16]
            for packet_id in direct_packets
        }
        self.assertEqual(preview_digests, expected_digests)
        self.assertEqual(preview["source_receipt_count"], 0)
        self.assertEqual(preview["source_cursor_nonzero_count"], 0)

    def test_s4_would_present_ledger_suppresses_duplicate_without_real_receipt(self):
        self.cross("tool.producer", {"agent_id": "A", "task": "shared"}, {"status": "OK"})
        first, _ = self.cross("tool.consumer", {"agent_id": "B", "task": "shared"}, {"status": "OK"})
        second, _ = self.cross("tool.consumer", {"agent_id": "B", "task": "shared"}, {"status": "OK"})
        self.assertGreaterEqual(first["before"]["new_would_presented"], 1)
        self.assertEqual(second["before"]["new_would_presented"], 0)
        self.assertEqual(len(self.shadow.source._receipts), 0)

    def test_s5_critical_reserve_is_bounded_in_preview_only(self):
        source = self.shadow.source
        source.touch("A", work_refs=["W"])
        source.touch("B", work_refs=["W"])
        for index in range(4):
            source.emit(
                "A",
                "BLOCKER",
                f"blocked-{index}",
                work_refs=["W"],
                urgency=0.0,
                novelty=0.0,
            )
        preview = self.shadow.preview_rendezvous(
            "B",
            threshold=0.95,
            context_budget=4096,
            scout_quota=0,
            critical_quota=1,
        )
        self.assertLessEqual(preview["critical_reserve_would_use"], 1)
        self.assertGreaterEqual(preview["critical_reserve_would_use"], 1)
        self.assertEqual(len(source._receipts), 0)

    def test_s6_tiny_context_is_hard_budget_and_never_creates_receipt(self):
        source = self.shadow.source
        source.touch("A", work_refs=["W"])
        source.touch("B", work_refs=["W"])
        source.emit(
            "A",
            "BLOCKER",
            "X" * 1200,
            work_refs=["W"],
            urgency=0.0,
            novelty=0.0,
        )
        preview = self.shadow.preview_rendezvous(
            "B",
            threshold=0.95,
            context_budget=256,
            scout_quota=0,
            critical_quota=1,
        )
        self.assertLessEqual(int(preview["context_used"]), 256)
        self.assertGreaterEqual(preview["context_budget_filtered_count"], 1)
        self.assertEqual(len(source._receipts), 0)

    def test_s7_typed_semantic_valid_and_malformed_hold_without_domain_mutation(self):
        valid, valid_domain = self.cross(
            "tool.semantic",
            {"agent_id": "A", "task": "semantic"},
            {
                "status": "OK",
                "_liminal_publish": {
                    "message_class": "RESULT",
                    "summary": "typed bounded result",
                    "changed_refs": ["ref:1"],
                },
            },
        )
        self.assertEqual(valid["semantic_state"], "VALID")
        self.assertIn("_liminal_publish", valid_domain["result"]["structuredContent"])

        malformed, malformed_domain = self.cross(
            "tool.semantic",
            {"agent_id": "B", "task": "semantic"},
            {
                "status": "OK",
                "_liminal_publish": {
                    "message_class": "RESULT",
                    "summary": "bad",
                    "evidence_ceiling": "FORGED",
                },
            },
        )
        self.assertEqual(malformed["semantic_state"], "HOLD")
        self.assertTrue(malformed["output_preserved"])
        self.assertEqual(malformed_domain["result"]["structuredContent"]["_liminal_publish"]["evidence_ceiling"], "FORGED")

    def test_s9_existing_live_carrier_is_byte_digest_unchanged(self):
        live = LiminalBeaconMeshRuntime(self.server, clock=self.clock)
        live.touch("LIVE", work_refs=["L"])
        live.emit("LIVE", "RESULT", "live packet", work_refs=["L"])
        self.server._liminal_beacon_mesh_runtime_v1 = live
        before = carrier_snapshot(live)
        record, _ = self.cross("tool.shadow", {"agent_id": "A", "task": "S"}, {"status": "OK"})
        after = carrier_snapshot(live)
        self.assertEqual(before, after)
        self.assertTrue(record["live_carrier_unchanged"])

    def test_s10_observer_error_is_hold_not_domain_content(self):
        row = self.shadow.record_error("AFTER", ValueError("synthetic"), tool_name="tool.x")
        self.assertEqual(row["standing"], "SHADOW_HOLD")
        status = self.shadow.status()
        self.assertEqual(status["metrics"]["holds"], 1)

    def test_s11_restart_state_is_process_local_and_hidden_counts_unknown(self):
        self.cross("tool.one", {"agent_id": "A", "task": "W"}, {"status": "OK"})
        first = self.shadow.status()
        restarted = LiminalBeaconShadowRuntime(FakeServer(), clock=self.clock)
        second = restarted.status()
        self.assertGreaterEqual(first["crossing_count"], 1)
        self.assertEqual(second["crossing_count"], 0)
        self.assertEqual(second["hidden_process_count"], "UNKNOWN")
        self.assertEqual(second["independent_process_count"], "UNKNOWN")

    def test_protocol_surface_is_read_only_and_registered(self):
        names = {tool["name"] for tool in protocol.TOOLS}
        self.assertTrue(LIMINAL_BEACON_SHADOW_TOOL_NAMES <= names)
        self.assertEqual(LIMINAL_BEACON_SHADOW_TOOL_NAMES, {"athena_liminal_beacon_shadow_status"})


if __name__ == "__main__":
    unittest.main()

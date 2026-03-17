from __future__ import annotations

import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from self_actualize.runtime.command_membrane_v1 import COORD12_KEYS, ROUTE_POLICY, WATCH_MODE_DEGRADED, CommandMembraneConfig, CommandMembraneService, parse_iso


class CommandMembraneTests(unittest.TestCase):
    def make_service(self) -> CommandMembraneService:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        workspace = Path(tempdir.name) / "workspace"
        command_root = workspace / "GLOBAL COMMAND"
        self_root = workspace / "self_actualize"
        hall_path = self_root / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL" / "20_COMMAND_MEMBRANE_PROTOCOL.md"
        temple_path = self_root / "mycelium_brain" / "ATHENA TEMPLE" / "11_COMMAND_MEMBRANE_DECREE.md"
        docs_gate = self_root / "live_docs_gate_status.md"
        docs_gate.parent.mkdir(parents=True, exist_ok=True)
        docs_gate.write_text("# Live Docs Gate Status\n\n- Command status: `BLOCKED`\n", encoding="utf-8")
        command_root.mkdir(parents=True, exist_ok=True)
        config = CommandMembraneConfig(
            workspace_root=workspace,
            command_root=command_root,
            docs_gate_path=docs_gate,
            protocol_json_path=self_root / "command_membrane_protocol.json",
            packet_schema_path=self_root / "command_membrane_packet_schema.json",
            capillary_law_path=self_root / "command_membrane_capillary_law.json",
            runtime_state_path=self_root / "command_membrane_runtime_state.json",
            packet_ledger_path=self_root / "command_membrane_packets.jsonl",
            route_ledger_path=self_root / "command_membrane_routes.jsonl",
            claim_ledger_path=self_root / "command_membrane_claims.jsonl",
            capillary_graph_path=self_root / "command_membrane_capillary_graph.json",
            projection_ledger_path=self_root / "command_membrane_projections.jsonl",
            event_store_root=self_root / "command_membrane_events",
            hall_protocol_path=hall_path,
            temple_decree_path=temple_path,
            runtime_region="TEST_RUNTIME",
            earth_geo_anchor="TEST_GEO",
        )
        return CommandMembraneService(config=config)

    def test_protocol_artifacts_freeze_expected_defaults(self) -> None:
        service = self.make_service()
        payload = service.build()
        protocol = json.loads(service.config.protocol_json_path.read_text(encoding="utf-8"))
        schema = json.loads(service.config.packet_schema_path.read_text(encoding="utf-8"))
        hall_text = service.config.hall_protocol_path.read_text(encoding="utf-8")
        temple_text = service.config.temple_decree_path.read_text(encoding="utf-8")

        self.assertEqual(payload["docs_gate"]["status"], "BLOCKED")
        self.assertEqual(protocol["routing_policy"]["policy"], ROUTE_POLICY)
        self.assertEqual(protocol["routing_policy"]["topk"], 5)
        self.assertEqual(protocol["routing_policy"]["lease_ms"], 1200)
        self.assertEqual(schema["coord12_keys"], COORD12_KEYS)
        self.assertIn("Docs gate: `BLOCKED`", hall_text)
        self.assertIn("event-driven watch is canonical", temple_text)

    def test_emit_packet_populates_required_fields_and_coord12(self) -> None:
        service = self.make_service()
        target = service.config.command_root / "ATHENA" / "protocol.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("alpha", encoding="utf-8")

        first = service.emit_manual(path=str(target), event_kind="created")
        target.write_text("beta", encoding="utf-8")
        second = service.emit_manual(path=str(target), event_kind="modified")

        first_payload = json.loads(service.event_store_path(first["event_id"]).read_text(encoding="utf-8"))["packet"]
        second_payload = json.loads(service.event_store_path(second["event_id"]).read_text(encoding="utf-8"))["packet"]

        for field in (
            "event_id", "source_root", "relative_path", "event_kind", "tag", "goal", "change", "priority",
            "confidence", "earth_ts", "liminal_ts", "coord12", "delta_tau", "velocity_tau", "parent",
            "ttl", "pheromone", "state_hash", "route_class", "lineage", "claim_state",
        ):
            self.assertIn(field, first_payload)
        self.assertEqual(set(first_payload["coord12"]), set(COORD12_KEYS))
        self.assertGreaterEqual(second_payload["delta_tau"], 0.0)
        self.assertGreaterEqual(second_payload["velocity_tau"], 0.0)

    def test_route_is_deterministic_for_same_packet(self) -> None:
        service = self.make_service()
        target = service.config.command_root / "ATHENA" / "runtime.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("print('x')", encoding="utf-8")
        packet = service.emit_manual(path=str(target), event_kind="created")
        record = json.loads(service.event_store_path(packet["event_id"]).read_text(encoding="utf-8"))

        first = service.compute_route_for_packet(record["packet"])
        second = service.compute_route_for_packet(record["packet"])

        self.assertEqual(first, second)
        self.assertEqual(len(first), 5)

    def test_first_lease_rejects_duplicate_and_expiry_requeues(self) -> None:
        service = self.make_service()
        target = service.config.command_root / "ATHENA" / "task.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("claim me", encoding="utf-8")
        packet = service.emit_manual(path=str(target), event_kind="created")
        route = service.route_event(packet["event_id"])
        lease = service.claim_event(packet["event_id"], ant_id=route["selected_targets"][0])

        with self.assertRaises(RuntimeError):
            service.claim_event(packet["event_id"], ant_id="WORKER-02")

        service.sweep_expired_claims(now=parse_iso(lease["expires_at"]) + timedelta(milliseconds=1))
        claim_rows = service.config.claim_ledger_path.read_text(encoding="utf-8")
        route_rows = service.config.route_ledger_path.read_text(encoding="utf-8")
        self.assertIn("claim_expired", claim_rows)
        self.assertIn("requeue_required", route_rows)

    def test_reinforcement_promotes_capillary_and_vein(self) -> None:
        service = self.make_service()
        target = service.config.command_root / "ATHENA" / "dense.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("dense", encoding="utf-8")
        packet = service.emit_manual(path=str(target), event_kind="created")
        route = service.route_event(packet["event_id"])
        service.claim_event(packet["event_id"], ant_id=route["selected_targets"][0])
        service.commit_event(packet["event_id"], worker_id=route["selected_targets"][0], result="success", summary="ok")

        first = service.load_event_record(packet["event_id"])["reinforcement"]
        self.assertEqual(first["state_class"], "ephemeral")
        self.assertGreater(first["score"], 0.0)

        service.reinforce_event(packet["event_id"], result="success", latency_score=0.0, noise_penalty=0.4, allow_uncommitted=True)
        self.assertEqual(service.load_event_record(packet["event_id"])["reinforcement"]["state_class"], "capillary")

        service.reinforce_event(packet["event_id"], result="success", latency_score=1.0, noise_penalty=0.0, allow_uncommitted=True)
        self.assertEqual(service.load_event_record(packet["event_id"])["reinforcement"]["state_class"], "vein")

    def test_compute_changes_detects_rename_and_noise_is_ignored(self) -> None:
        service = self.make_service()
        a = service.config.command_root / "alpha.md"
        b = service.config.command_root / "beta.md"
        temp = service.config.command_root / "~$draft.docx"
        a.write_text("same", encoding="utf-8")
        temp.write_text("noise", encoding="utf-8")
        previous = service.snapshot_directory()
        b.write_text("same", encoding="utf-8")
        a.unlink()
        current = service.snapshot_directory()
        changes = service.compute_changes(previous, current)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["event_kind"], "renamed")
        self.assertEqual(changes[0]["lineage"]["from"], "alpha.md")
        self.assertEqual(changes[0]["lineage"]["to"], "beta.md")

    def test_degraded_watch_mode_is_labeled_honestly(self) -> None:
        service = self.make_service()
        target = service.config.command_root / "ATHENA" / "poll.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("poll", encoding="utf-8")
        results = service.watch(mode=WATCH_MODE_DEGRADED, interval=0.01, timeout_secs=1, max_events=1)

        self.assertTrue(results)
        self.assertEqual(results[0]["watch_mode"], WATCH_MODE_DEGRADED)


if __name__ == "__main__":
    unittest.main()


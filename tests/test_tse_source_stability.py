from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server
from athena_mcp.tse_population import _digest
from athena_mcp.tse_telemetry_proxy import TseHelixTelemetryProxy


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _fixture(base: Path):
    a = base / "a"
    a.mkdir()
    _run(a, "init", "-b", "master")
    _run(a, "config", "user.name", "a")
    _run(a, "config", "user.email", "a@example.invalid")
    (a / "seed.txt").write_text("seed\n", encoding="utf-8")
    _run(a, "add", ".")
    _run(a, "commit", "-m", "seed")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(a, "remote", "add", "origin", str(origin))
    _run(a, "push", "-u", "origin", "master")

    b = base / "b"
    proc = subprocess.run(["git", "clone", str(origin), str(b)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(b, "config", "user.name", "b")
    _run(b, "config", "user.email", "b@example.invalid")
    return a, b


def hatch():
    checkpoint = {
        "residual": ["execute stable TSE child"],
        "acceptance": ["source identity stable", "exact envelope bound"],
    }
    checkpoint["checkpoint_digest"] = _digest(checkpoint)
    value = {
        "schema_version": "ATHENA.TSE.HATCH.V2",
        "hatch_id": "HATCH.STABLE.1",
        "parent_checkpoint_digest": checkpoint["checkpoint_digest"],
        "parent_checkpoint": checkpoint,
        "child_quest": {"id": "Q-STABLE-CHILD", "version": "1"},
        "status": "CHILD_ACTIVE",
        "platform_counter_reset_claimed": False,
    }
    value["hatch_digest"] = _digest(value)
    return value


class TseSourceCoordinateStabilityTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        a, b = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=a)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=b)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.board_a = MessageBoardRuntime(self.a.git)
        self.board_b = MessageBoardRuntime(self.b.git)
        self.seq = 0
        self.mission = "MISSION-STABLE-1"

    def rpc(self, server, method, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return server.handle(message)

    def tool(self, server, name, args):
        response = self.rpc(server, "tools/call", {"name": name, "arguments": args})
        result = response["result"]
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def open_args(self):
        return {
            "mission_id": self.mission,
            "hatch": hatch(),
            "parent_agent_id": "alpha",
            "capabilities": ["code", "tests"],
            "actor_id": "observer",
            "witnesses": ["test:stable-hatch"],
            "cost": {"known": True, "total": 1.0},
            "targets": ["child.py"],
            "dependencies": ["api.ready"],
            "role": "BUILDER",
            "life_policy": "STAY_IN_GAME_LIFE_LOOP_V1",
            "clear_condition_digest": "sha256:criterion",
        }

    def open(self):
        return self.tool(self.a, "athena_tse_helix_open", self.open_args())

    def advance(self, operation, route, parent_event_id, **extra):
        args = {
            "mission_id": self.mission,
            "operation": operation,
            "route": route,
            "parent_event_id": parent_event_id,
            "actor_id": "observer",
            "witnesses": [f"test:{operation}"],
            "cost": {"known": True, "total": 1.0},
        }
        args.update(extra)
        return self.tool(self.a, "athena_tse_helix_advance", args)

    def prepare_handoff(self):
        opened = self.open()
        self.assertEqual("TSE_HELIX_OPEN", opened["status"], opened)
        present = self.board_a.present(
            agent_id="alpha",
            task="Stable parent TSE lane",
            work_key="stable-parent",
            targets=["parent.py"],
        )
        self.assertEqual("PRESENT", present["status"], present)
        published = self.advance("PUBLISH", opened["route"], opened["root_event_id"])
        self.assertEqual("TSE_HELIX_ADVANCED", published["status"], published)

        beta = self.board_b.present(
            agent_id="beta",
            task="Stable child offer",
            work_key="stable-offer",
            targets=["offer.py"],
        )
        self.assertEqual("PRESENT", beta["status"], beta)
        offered = self.tool(
            self.b,
            "athena_cohesion_request_offer",
            {
                "request_id": "OFFER.STABLE.BETA",
                "agent_id": "beta",
                "kind": "OFFER",
                "capabilities": ["code", "tests"],
                "goal_ref": "offer.stable",
                "role": "BUILDER",
                "provides": ["api.ready"],
                "capacity_units": 2,
            },
        )
        self.assertEqual("COHESION_OFFER_PUBLISHED", offered["status"], offered)
        matched = self.advance("MATCH", published["route"], published["event_id"], min_score=1)
        self.assertEqual("TSE_HELIX_ADVANCED", matched["status"], matched)
        handed = self.advance("HANDOFF", matched["route"], matched["event_id"])
        self.assertEqual("TSE_HELIX_ADVANCED", handed["status"], handed)
        return handed

    def _mutate_handoff_envelope(self, message_id: str, field: str, value):
        root = Path(self.a.git.root)
        target = None
        data = None
        for path in root.glob("runtime/message_board/v1/events/**/*.json"):
            candidate = json.loads(path.read_text(encoding="utf-8"))
            if candidate.get("event_id") == message_id:
                target = path
                data = candidate
                break
        self.assertIsNotNone(target, message_id)
        envelope = json.loads(data["payload"]["message"])
        envelope[field] = value
        data["payload"]["message"] = json.dumps(
            envelope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rel = str(target.relative_to(root)).replace("\\", "/")
        _run(root, "add", "--", rel)
        _run(root, "commit", "-m", "tamper handoff envelope fixture")
        _run(root, "push", "origin", "master")

    def test_hatch_reobservation_is_idempotent_after_telemetry_moves_head(self):
        first = self.open()
        self.assertEqual("TSE_HELIX_OPEN", first["status"], first)
        first_event = first["root_event_id"]

        noise = self.tool(
            self.a,
            "athena_tse_telemetry_record",
            {
                "mission_id": self.mission,
                "route_id": "R-NOISE",
                "hatch_id": "H-NOISE",
                "transition": "HATCH_CREATED",
                "actor_id": "observer",
                "witnesses": ["noise"],
                "cost": {"known": True, "total": 0.1},
                "attempt_ref": "noise-1",
            },
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_DECLARED", noise["status"], noise)

        replay = self.open()
        self.assertEqual("TSE_HELIX_OPEN", replay["status"], replay)
        self.assertEqual(first_event, replay["root_event_id"])
        self.assertEqual("TSE_TELEMETRY_ALREADY_RECORDED", replay["telemetry"]["status"])

    def test_proxy_removes_observer_git_drift_from_match_and_claim_sources(self):
        left = TseHelixTelemetryProxy._stable_source_kwargs(
            {
                "source_kind": "COHESION_ADVISORY_MATCH",
                "source_payload": {
                    "selected_match": {"agent_id": "beta", "offer_id": "O1", "match_git_head": "HEAD-A"},
                    "match_git_head": "HEAD-A",
                    "need_id": "N1",
                },
                "source_git_head": "HEAD-A",
            }
        )
        right = TseHelixTelemetryProxy._stable_source_kwargs(
            {
                "source_kind": "COHESION_ADVISORY_MATCH",
                "source_payload": {
                    "selected_match": {"agent_id": "beta", "offer_id": "O1", "match_git_head": "HEAD-B"},
                    "match_git_head": "HEAD-B",
                    "need_id": "N1",
                },
                "source_git_head": "HEAD-B",
            }
        )
        self.assertEqual(left["source_payload"], right["source_payload"])
        self.assertIsNone(left["source_git_head"])
        self.assertIsNone(right["source_git_head"])

        claim_left = TseHelixTelemetryProxy._stable_source_kwargs(
            {
                "source_kind": "MESSAGE_BOARD_CHILD_CLAIM",
                "source_payload": {
                    "child_claim": {"claim_id": "C1", "claim_base_head": "CLAIM-BASE"},
                    "message_board_git_head": "BOARD-A",
                },
                "source_git_head": "BOARD-A",
            }
        )
        claim_right = TseHelixTelemetryProxy._stable_source_kwargs(
            {
                "source_kind": "MESSAGE_BOARD_CHILD_CLAIM",
                "source_payload": {
                    "child_claim": {"claim_id": "C1", "claim_base_head": "CLAIM-BASE"},
                    "message_board_git_head": "BOARD-B",
                },
                "source_git_head": "BOARD-B",
            }
        )
        self.assertEqual(claim_left, claim_right)
        self.assertEqual("CLAIM-BASE", claim_left["source_git_head"])

    def test_valid_exact_envelope_and_ack_is_consumption_only(self):
        handed = self.prepare_handoff()
        route = handed["route"]
        ack = self.board_b.ack(agent_id="beta", message_id=route["handoff_message_id"])
        self.assertEqual("ACKED", ack["status"], ack)
        consumed = self.tool(
            self.a,
            "athena_tse_helix_observe_consumption",
            {
                "mission_id": self.mission,
                "route": route,
                "parent_event_id": handed["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:exact-envelope"],
                "cost": {"known": True, "total": 1.0},
            },
        )
        self.assertEqual("TSE_HELIX_HANDOFF_CONSUMED", consumed["status"], consumed)
        self.assertTrue(consumed["handoff_envelope_bound"])
        self.assertFalse(consumed["claim_authority"])

    def test_tampered_envelope_with_real_ack_fails_before_consumption(self):
        handed = self.prepare_handoff()
        route = handed["route"]
        self._mutate_handoff_envelope(
            route["handoff_message_id"],
            "child_work_key",
            "TSE.CHILD.TAMPERED",
        )
        ack = self.board_b.ack(agent_id="beta", message_id=route["handoff_message_id"])
        self.assertEqual("ACKED", ack["status"], ack)
        held = self.tool(
            self.a,
            "athena_tse_helix_observe_consumption",
            {
                "mission_id": self.mission,
                "route": route,
                "parent_event_id": handed["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:tampered-envelope"],
                "cost": {"known": True, "total": 1.0},
            },
        )
        self.assertEqual("TSE_HELIX_HANDOFF_ENVELOPE_HOLD", held["status"], held)
        self.assertEqual("EVIDENCE_HOLD", held["hold"])
        self.assertEqual("handoff_envelope_binding_mismatch", held["reason"])
        self.assertIn("child_work_key", held["mismatches"])

    def test_invalid_json_envelope_fails_closed(self):
        handed = self.prepare_handoff()
        route = handed["route"]
        root = Path(self.a.git.root)
        target = None
        data = None
        for path in root.glob("runtime/message_board/v1/events/**/*.json"):
            candidate = json.loads(path.read_text(encoding="utf-8"))
            if candidate.get("event_id") == route["handoff_message_id"]:
                target = path
                data = candidate
                break
        self.assertIsNotNone(target)
        data["payload"]["message"] = "{not-json"
        target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rel = str(target.relative_to(root)).replace("\\", "/")
        _run(root, "add", "--", rel)
        _run(root, "commit", "-m", "break handoff envelope json fixture")
        _run(root, "push", "origin", "master")
        ack = self.board_b.ack(agent_id="beta", message_id=route["handoff_message_id"])
        self.assertEqual("ACKED", ack["status"], ack)
        held = self.tool(
            self.a,
            "athena_tse_helix_observe_consumption",
            {
                "mission_id": self.mission,
                "route": route,
                "parent_event_id": handed["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:invalid-json"],
                "cost": {"known": True, "total": 1.0},
            },
        )
        self.assertEqual("handoff_envelope_invalid_json", held["reason"])
        self.assertEqual("EVIDENCE_HOLD", held["hold"])


if __name__ == "__main__":
    unittest.main()

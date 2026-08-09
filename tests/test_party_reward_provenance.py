from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _fixture(base: Path):
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    (local / "seed.txt").write_text("seed\n", encoding="utf-8")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "master")

    clone = base / "clone"
    proc = subprocess.run(["git", "clone", str(origin), str(clone)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(clone, "config", "user.name", "clone")
    _run(clone, "config", "user.email", "clone@example.invalid")
    return local, clone


class PartyRewardProvenanceV3Tests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        local, clone = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=local)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=clone)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.board_a = MessageBoardRuntime(self.a.git)
        self.board_b = MessageBoardRuntime(self.b.git)
        self.seq = 0

    def rpc(self, server, method, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return server.handle(message)

    def tool(self, server, name, args, expect_error=False):
        response = self.rpc(server, "tools/call", {"name": name, "arguments": args})
        result = response["result"]
        if expect_error:
            self.assertTrue(result.get("isError"), response)
            return result
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    @staticmethod
    def goals(suffix=""):
        return [
            {"goal_id": f"goal.analysis{suffix}", "required_capabilities": ["analysis"]},
            {"goal_id": f"goal.code{suffix}", "required_capabilities": ["code"]},
        ]

    def ensure_independent_presence(self):
        if not self.board_a.read(agent_id="alpha").get("self"):
            self.assertEqual(
                self.board_a.present(
                    agent_id="alpha",
                    task="Analyze party provenance",
                    work_key="work-alpha",
                    targets=["analysis.txt"],
                )["status"],
                "PRESENT",
            )
        if not self.board_b.read(agent_id="beta").get("self"):
            self.assertEqual(
                self.board_b.present(
                    agent_id="beta",
                    task="Implement party provenance",
                    work_key="work-beta",
                    targets=["runtime.py"],
                )["status"],
                "PRESENT",
            )

    def form_party(self, party_id="PARTY.TEST", suffix=""):
        formed = self.tool(
            self.a,
            "athena_party_form",
            {
                "party_id": party_id,
                "leader": "alpha",
                "purpose": "verify party reward provenance",
                "goals": self.goals(suffix),
                "leader_goal_refs": [f"goal.analysis{suffix}"],
                "role": "LEAD",
                "capabilities": ["analysis"],
                "capacity": 4,
            },
        )
        self.assertIn(formed["status"], {"PARTY_FORMED", "ALREADY_FORMED"})
        joined = self.tool(
            self.b,
            "athena_party_join",
            {
                "party_id": party_id,
                "agent": "beta",
                "goal_refs": [f"goal.code{suffix}"],
                "task_relation": "COMMUTATIVE",
                "role": "BUILDER",
                "capabilities": ["code"],
            },
        )
        self.assertIn(joined["status"], {"PARTY_JOINED", "ALREADY_JOINED"})
        return f"goal.analysis{suffix}", f"goal.code{suffix}"

    def seed_party(self, party_id="PARTY.TEST", suffix=""):
        self.ensure_independent_presence()
        goals = self.form_party(party_id, suffix)
        self.party_message(party_id, goals)
        return goals

    def party_message(self, party_id, goals, suffix=""):
        posted = self.tool(
            self.a,
            "athena_party_message",
            {
                "party_id": party_id,
                "sender": "alpha",
                "recipients": ["beta"],
                "goal_refs": list(goals),
                "message_kind": "HANDOFF",
                "message": f"Current party goals are coordinated{suffix}",
            },
        )
        self.assertEqual(posted["status"], "POSTED")
        self.assertEqual(posted["xp_bonus"], 0)
        message_id = posted["message_event"]["event_id"]
        self.assertEqual(self.board_b.ack(agent_id="beta", message_id=message_id)["status"], "ACKED")
        return message_id

    def party_result(self, server, ack_board, *, party_id, sender, recipient, goal_id, suffix="", ack=True):
        posted = self.tool(
            server,
            "athena_party_result",
            {
                "party_id": party_id,
                "sender": sender,
                "recipients": [recipient],
                "goal_id": goal_id,
                "result_ref": f"result://{sender}/{goal_id}{suffix}",
                "witness_ref": f"witness://{sender}/{goal_id}{suffix}",
                "evidence_kind": "RESULT",
            },
        )
        self.assertEqual(posted["status"], "POSTED")
        self.assertEqual(posted["xp_bonus"], 0)
        event_id = posted["message_event"]["event_id"]
        if ack:
            self.assertEqual(ack_board.ack(agent_id=recipient, message_id=event_id)["status"], "ACKED")
        return {
            "goal_id": goal_id,
            "agent_id": sender,
            "witness_ref": f"witness://{sender}/{goal_id}{suffix}",
            "result_event_ref": event_id,
        }

    def valid_results(self, party_id, goal_a, goal_b, suffix=""):
        first = self.party_result(
            self.a,
            self.board_b,
            party_id=party_id,
            sender="alpha",
            recipient="beta",
            goal_id=goal_a,
            suffix=suffix,
        )
        second = self.party_result(
            self.b,
            self.board_a,
            party_id=party_id,
            sender="beta",
            recipient="alpha",
            goal_id=goal_b,
            suffix=suffix,
        )
        return [first, second]

    def observe_args(self, party_id, results, suffix="", source_xp_ref=None):
        return {
            "observation_id": f"OBS{suffix or '.ONE'}".replace("/", "-"),
            "party_id": party_id,
            "observer": "meta",
            "base_xp": 100,
            "source_xp_ref": source_xp_ref or f"xp://source{suffix or '/one'}",
            "source_xp_witness_ref": f"xp-witness://source{suffix or '/one'}",
            "results": results,
            "witness_ref": f"observation-witness://{party_id}{suffix or '/one'}",
        }

    def test_valid_provenance_awards_bounded_bonus_without_truth_or_xp_authority(self):
        goal_a, goal_b = self.seed_party()
        results = self.valid_results("PARTY.TEST", goal_a, goal_b)
        award = self.tool(self.a, "athena_party_observe", self.observe_args("PARTY.TEST", results))
        self.assertEqual(award["status"], "AWARDED")
        self.assertGreater(award["coordination_bonus_xp"], 0)
        self.assertLessEqual(award["coordination_bonus_rate"], 0.05)
        self.assertFalse(award["xp_patch"]["apply_to_global_xp"])
        self.assertFalse(award["source_xp_external_verification"])
        self.assertFalse(award["result_truth_verified"])
        self.assertFalse(award["independent_result_verification"])
        self.assertTrue(award["result_provenance_complete"])
        self.assertEqual(award["root_work_diversity"], 2)
        self.assertTrue(all(row["provenance_validated"] for row in award["result_provenance"]))

        replay = self.tool(self.b, "athena_party_observe", self.observe_args("PARTY.TEST", results))
        self.assertTrue(replay["idempotent"])
        self.assertEqual(replay["receipt_digest"], award["receipt_digest"])

    def test_legacy_observe_without_provenance_holds_instead_of_awarding(self):
        goal_a, goal_b = self.seed_party()
        held = self.tool(
            self.a,
            "athena_party_observe",
            {
                "observation_id": "OBS.LEGACY",
                "party_id": "PARTY.TEST",
                "observer": "meta",
                "base_xp": 100,
                "results": [
                    {"goal_id": goal_a, "agent_id": "alpha", "witness_ref": "legacy-a"},
                    {"goal_id": goal_b, "agent_id": "beta", "witness_ref": "legacy-b"},
                ],
                "witness_ref": "legacy-observation",
            },
        )
        self.assertEqual(held["status"], "HOLD")
        self.assertIn("SOURCE_XP_REF_REQUIRED", held["hold_reasons"])
        self.assertIn("SOURCE_XP_WITNESS_REQUIRED", held["hold_reasons"])
        self.assertTrue(any(reason.startswith("RESULT_EVENT_REF_REQUIRED") for reason in held["hold_reasons"]))
        self.assertEqual(held["coordination_bonus_xp"], 0)

    def test_unacknowledged_result_event_cannot_unlock_award(self):
        goal_a, goal_b = self.seed_party()
        first = self.party_result(
            self.a,
            self.board_b,
            party_id="PARTY.TEST",
            sender="alpha",
            recipient="beta",
            goal_id=goal_a,
            ack=False,
        )
        second = self.party_result(
            self.b,
            self.board_a,
            party_id="PARTY.TEST",
            sender="beta",
            recipient="alpha",
            goal_id=goal_b,
        )
        held = self.tool(self.a, "athena_party_observe", self.observe_args("PARTY.TEST", [first, second], ".UNACK"))
        self.assertEqual(held["status"], "HOLD")
        self.assertTrue(any(reason.startswith("RESULT_EVENT_UNACKNOWLEDGED") for reason in held["hold_reasons"]))
        self.assertEqual(held["coordination_bonus_xp"], 0)

    def test_result_agent_must_still_hold_frozen_claim(self):
        goal_a, goal_b = self.seed_party()
        results = self.valid_results("PARTY.TEST", goal_a, goal_b)
        self.assertEqual(self.board_b.release(agent_id="beta", release_status="DONE")["status"], "RELEASED")
        held = self.tool(self.a, "athena_party_observe", self.observe_args("PARTY.TEST", results, ".STALE"))
        self.assertEqual(held["status"], "HOLD")
        self.assertIn("RESULT_AGENT_NOT_ACTIVE_HOLD:beta", held["hold_reasons"])

    def test_switched_primary_claim_is_not_current_party_work(self):
        goal_a, goal_b = self.seed_party()
        results = self.valid_results("PARTY.TEST", goal_a, goal_b)
        self.assertEqual(self.board_b.release(agent_id="beta", release_status="DONE")["status"], "RELEASED")
        self.assertEqual(
            self.board_b.present(
                agent_id="beta",
                task="Different work after party join",
                work_key="work-beta-new",
                targets=["other.py"],
            )["status"],
            "PRESENT",
        )
        held = self.tool(self.a, "athena_party_observe", self.observe_args("PARTY.TEST", results, ".SWITCH"))
        self.assertEqual(held["status"], "HOLD")
        self.assertIn("RESULT_AGENT_STALE_CLAIM_HOLD:beta", held["hold_reasons"])

    def test_result_event_must_match_agent_goal_claim_and_witness(self):
        goal_a, goal_b = self.seed_party()
        alpha = self.party_result(
            self.a,
            self.board_b,
            party_id="PARTY.TEST",
            sender="alpha",
            recipient="beta",
            goal_id=goal_a,
        )
        # Deliberately claim alpha's exact event as beta's code result.
        forged_beta = {
            "goal_id": goal_b,
            "agent_id": "beta",
            "witness_ref": alpha["witness_ref"],
            "result_event_ref": alpha["result_event_ref"],
        }
        held = self.tool(self.a, "athena_party_observe", self.observe_args("PARTY.TEST", [alpha, forged_beta], ".FORGED"))
        self.assertEqual(held["status"], "HOLD")
        self.assertTrue(any("AUTHOR_MISMATCH" in reason or "GOAL_MISMATCH" in reason for reason in held["hold_reasons"]))
        self.assertIn("RESULT_PROVENANCE_INCOMPLETE_HOLD", held["hold_reasons"])

    def test_same_source_xp_cannot_receive_second_award_in_same_party(self):
        goal_a, goal_b = self.seed_party()
        first_results = self.valid_results("PARTY.TEST", goal_a, goal_b, "-first")
        source_ref = "xp://global/reused"
        first = self.tool(
            self.a,
            "athena_party_observe",
            self.observe_args("PARTY.TEST", first_results, ".FIRST", source_xp_ref=source_ref),
        )
        self.assertEqual(first["status"], "AWARDED")

        self.party_message("PARTY.TEST", (goal_a, goal_b), "-fresh")
        second_results = self.valid_results("PARTY.TEST", goal_a, goal_b, "-second")
        held = self.tool(
            self.a,
            "athena_party_observe",
            self.observe_args("PARTY.TEST", second_results, ".SECOND", source_xp_ref=source_ref),
        )
        self.assertEqual(held["status"], "HOLD")
        self.assertIn("SOURCE_XP_ALREADY_PARTY_CREDITED_HOLD", held["hold_reasons"])
        self.assertEqual(held["coordination_bonus_xp"], 0)

    def test_source_xp_reuse_is_global_across_parties(self):
        goal_a, goal_b = self.seed_party()
        source_ref = "xp://global/across-parties"
        first_results = self.valid_results("PARTY.TEST", goal_a, goal_b, "-p1")
        first = self.tool(
            self.a,
            "athena_party_observe",
            self.observe_args("PARTY.TEST", first_results, ".P1", source_xp_ref=source_ref),
        )
        self.assertEqual(first["status"], "AWARDED")

        goal_a2, goal_b2 = self.form_party("PARTY.TWO", ".two")
        self.party_message("PARTY.TWO", (goal_a2, goal_b2), "-p2")
        second_results = self.valid_results("PARTY.TWO", goal_a2, goal_b2, "-p2")
        held = self.tool(
            self.a,
            "athena_party_observe",
            self.observe_args("PARTY.TWO", second_results, ".P2", source_xp_ref=source_ref),
        )
        self.assertEqual(held["status"], "HOLD")
        self.assertIn("SOURCE_XP_ALREADY_PARTY_CREDITED_HOLD", held["hold_reasons"])

    def test_duplicate_collaborator_work_root_cannot_manufacture_diversity(self):
        self.assertEqual(
            self.board_a.present(
                agent_id="alpha",
                task="Shared implementation lane",
                work_key="shared-work",
                targets=["shared.py"],
            )["status"],
            "PRESENT",
        )
        self.tool(
            self.a,
            "athena_party_form",
            {
                "party_id": "PARTY.TEST",
                "leader": "alpha",
                "goals": self.goals(),
                "leader_goal_refs": ["goal.analysis"],
                "capabilities": ["analysis"],
            },
        )
        joined_board = self.board_b.join(
            agent_id="beta",
            join_agent_id="alpha",
            task="Collaborate on shared implementation lane",
        )
        self.assertEqual(joined_board["status"], "JOINED")
        joined_party = self.tool(
            self.b,
            "athena_party_join",
            {
                "party_id": "PARTY.TEST",
                "agent": "beta",
                "goal_refs": ["goal.code"],
                "task_relation": "IDENTICAL",
                "capabilities": ["code"],
            },
        )
        self.assertEqual(joined_party["status"], "PARTY_JOINED")
        self.party_message("PARTY.TEST", ("goal.analysis", "goal.code"))
        results = self.valid_results("PARTY.TEST", "goal.analysis", "goal.code")
        held = self.tool(self.a, "athena_party_observe", self.observe_args("PARTY.TEST", results, ".DUPROOT"))
        self.assertEqual(held["status"], "HOLD")
        self.assertIn("DUPLICATE_ONLY_PARTY_HOLD", held["hold_reasons"])
        self.assertEqual(held["root_work_diversity"], 1)

    def test_result_tool_itself_rejects_stale_member_claim(self):
        goal_a, goal_b = self.seed_party()
        self.assertEqual(self.board_b.release(agent_id="beta", release_status="DONE")["status"], "RELEASED")
        self.assertEqual(
            self.board_b.present(
                agent_id="beta",
                task="New unrelated lane",
                work_key="new-beta-work",
            )["status"],
            "PRESENT",
        )
        held = self.tool(
            self.b,
            "athena_party_result",
            {
                "party_id": "PARTY.TEST",
                "sender": "beta",
                "recipients": ["alpha"],
                "goal_id": goal_b,
                "result_ref": "result://new-beta",
                "witness_ref": "witness://new-beta",
            },
        )
        self.assertEqual(held["status"], "PARTY_RESULT_STALE_CLAIM_HOLD")
        self.assertEqual(held["xp_bonus"], 0)

    def test_v3_tools_and_resource_preserve_authority_boundaries(self):
        names = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        for name in (
            "athena_message_board",
            "athena_party_message",
            "athena_party_result",
            "athena_party_observe",
            "athena_impossible_complete",
            "athena_transport_aor_to_collective",
        ):
            self.assertIn(name, names)
        resource = self.rpc(self.a, "resources/read", {"uri": "athena://party-coordination/v1"})
        text = resource["result"]["contents"][0]["text"]
        self.assertIn("PARTY.REWARD.PROVENANCE.3", text)
        self.assertIn("source_xp_ref_required_for_award", text)
        self.assertIn("truth_authority", text)


if __name__ == "__main__":
    unittest.main()

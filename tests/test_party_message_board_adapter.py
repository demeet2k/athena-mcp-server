from __future__ import annotations

import json
import unittest

from athena_mcp.party_message_board_adapter import (
    ENVELOPE_ARTIFACT,
    build_envelope,
    message_board_post_args,
    project_snapshot,
)


class PartyMessageBoardAdapterTests(unittest.TestCase):
    def _event(
        self,
        *,
        event_id="MBE-1",
        author="A",
        claim_id="MBC-A",
        recipients=("B",),
        party_id="P1",
        cycle_id="C1",
        channel="ops",
        kind="HANDOFF",
        witness_ref=None,
        outer_kind=None,
    ):
        message = build_envelope(
            party_id=party_id,
            cycle_id=cycle_id,
            channel=channel,
            kind=kind,
            body="handoff payload",
            goal_refs=["G1"],
            claim_refs=[claim_id],
            witness_ref=witness_ref,
        )
        return {
            "artifact": "ATHENA.MESSAGE.BOARD.EVENT.V1",
            "event_id": event_id,
            "kind": "MESSAGE",
            "agent_id": author,
            "created_at": "2026-08-08T23:00:00+00:00",
            "payload": {
                "message_kind": outer_kind or ("HANDOFF" if kind == "HANDOFF" else "INFO"),
                "message": message,
                "claim_id": claim_id,
            },
            "recipients": list(recipients),
        }

    def _snapshot(self, events=None, verified=True, active=None):
        return {
            "artifact": "ATHENA.MESSAGE.BOARD.SNAPSHOT.V1",
            "git_head": "abc123",
            "shared_frontier_verified": verified,
            "active": active
            if active is not None
            else [
                {"agent_id": "A", "claim_id": "MBC-A", "status": "ACTIVE"},
                {"agent_id": "B", "claim_id": "MBC-B", "status": "ACTIVE"},
            ],
            "recent_events": list(events or []),
        }

    def test_build_envelope_is_canonical_and_typed(self):
        raw = build_envelope(
            party_id="P1",
            cycle_id="C1",
            channel="ops",
            kind="OFFER",
            body="help available",
            goal_refs=["G2", "G1", "G1"],
        )
        value = json.loads(raw)
        self.assertEqual(value["artifact"], ENVELOPE_ARTIFACT)
        self.assertEqual(value["goal_refs"], ["G1", "G2"])
        self.assertEqual(value["kind"], "OFFER")

    def test_decision_result_verify_require_witness(self):
        for kind in ("DECISION", "RESULT", "VERIFY"):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(ValueError, "WITNESS_REQUIRED"):
                    build_envelope(
                        party_id="P1",
                        cycle_id="C1",
                        channel="ops",
                        kind=kind,
                        body="x",
                    )

    def test_post_args_use_existing_message_board_post_surface(self):
        args = message_board_post_args(
            agent_id="A",
            recipients=["B"],
            party_id="P1",
            cycle_id="C1",
            channel="ops",
            kind="RESULT",
            body="done",
            goal_refs=["G1"],
            witness_ref="W1",
        )
        self.assertEqual(args["action"], "post")
        self.assertEqual(args["message_kind"], "INFO")
        self.assertEqual(args["recipients"], ["B"])
        self.assertEqual(json.loads(args["message"])["witness_ref"], "W1")

    def test_party_post_requires_explicit_recipients(self):
        with self.assertRaisesRegex(ValueError, "explicit recipient"):
            message_board_post_args(
                agent_id="A",
                recipients=[],
                party_id="P1",
                cycle_id="C1",
                channel="ops",
                kind="HANDOFF",
                body="x",
            )

    def test_unverified_shared_frontier_holds(self):
        result = project_snapshot(
            self._snapshot([self._event()], verified=False),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["status"], "MESSAGE_BOARD_SHARED_FRONTIER_HOLD")
        self.assertEqual(result["messages"], [])

    def test_current_board_event_projects_with_source_identity(self):
        result = project_snapshot(
            self._snapshot([self._event()]),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["source_event_count"], 1)
        self.assertEqual(result["messages"][0]["source_event_id"], "MBE-1")
        self.assertTrue(result["messages"][0]["projection_only"])
        self.assertEqual(result["active_members"], ["A", "B"])

    def test_prior_cycle_message_is_ignored(self):
        result = project_snapshot(
            self._snapshot([self._event(cycle_id="C0")]),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["source_event_count"], 0)

    def test_inactive_author_is_ineligible(self):
        result = project_snapshot(
            self._snapshot(
                [self._event()],
                active=[{"agent_id": "B", "claim_id": "MBC-B", "status": "ACTIVE"}],
            ),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["ineligible"][0]["reason"], "AUTHOR_NOT_ACTIVE_ON_MESSAGE_BOARD")

    def test_stale_claim_binding_is_ineligible(self):
        result = project_snapshot(
            self._snapshot([self._event(claim_id="MBC-OLD")]),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["ineligible"][0]["reason"], "MESSAGE_CLAIM_NOT_CURRENT")

    def test_recipient_outside_party_is_ineligible(self):
        result = project_snapshot(
            self._snapshot([self._event(recipients=("C",))]),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["ineligible"][0]["reason"], "RECIPIENT_OUTSIDE_PARTY")

    def test_outer_kind_mismatch_is_ineligible(self):
        result = project_snapshot(
            self._snapshot([self._event(outer_kind="BLOCKER")]),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["ineligible"][0]["reason"], "OUTER_MESSAGE_KIND_MISMATCH")

    def test_multirecipient_projection_keeps_one_source_event(self):
        snapshot = self._snapshot(
            [self._event(recipients=("B", "C"))],
            active=[
                {"agent_id": "A", "claim_id": "MBC-A", "status": "ACTIVE"},
                {"agent_id": "B", "claim_id": "MBC-B", "status": "ACTIVE"},
                {"agent_id": "C", "claim_id": "MBC-C", "status": "ACTIVE"},
            ],
        )
        result = project_snapshot(
            snapshot,
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B", "C"],
            party_channels=["ops"],
        )
        self.assertEqual(result["source_event_count"], 1)
        self.assertEqual(len(result["messages"]), 2)
        self.assertEqual(
            {row["source_event_id"] for row in result["messages"]}, {"MBE-1"}
        )

    def test_source_event_replay_does_not_count_twice(self):
        event = self._event()
        result = project_snapshot(
            self._snapshot([event, dict(event)]),
            party_id="P1",
            cycle_id="C1",
            party_members=["A", "B"],
            party_channels=["ops"],
        )
        self.assertEqual(result["source_event_count"], 1)
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["ineligible"][-1]["reason"], "SOURCE_EVENT_REPLAY")


if __name__ == "__main__":
    unittest.main()

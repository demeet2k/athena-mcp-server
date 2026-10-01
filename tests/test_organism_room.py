import importlib.util
import json
import pathlib
import unittest


MODULE = pathlib.Path(__file__).parents[1] / "athena_mcp" / "organism_room.py"
SPEC = importlib.util.spec_from_file_location("organism_room", MODULE)
room = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(room)


class FakeGit:
    def __init__(self, head="a" * 40):
        self.value = head

    def head(self):
        return self.value


class FakeBoard:
    def __init__(self):
        self.git = FakeGit()
        self.rows = {}
        self.events = []
        self.counter = 0

    def snapshot(self, agent_id=None, include_stale=False):
        active = [row for row in self.rows.values() if row["status"] == "ACTIVE"]
        return {"active": active, "self": self.rows.get(agent_id), "recent_events": list(self.events)}

    def read(self, **kwargs):
        value = self.snapshot(kwargs.get("agent_id"), kwargs.get("include_stale", False))
        value.update({"status": "OK", "git_head": self.git.head(), "remote_sync": {"shared_frontier_verified": True}})
        return value

    def present(self, **kwargs):
        if kwargs["agent_id"] in self.rows and self.rows[kwargs["agent_id"]]["status"] == "ACTIVE":
            return {"status": "AGENT_ALREADY_PRESENT_HOLD", "presence": self.rows[kwargs["agent_id"]]}
        self.counter += 1
        row = {
            "agent_id": kwargs["agent_id"],
            "claim_id": f"claim-{self.counter}",
            "status": "ACTIVE",
            "task": kwargs["task"],
            "work_key": kwargs.get("work_key"),
            "targets": kwargs.get("targets", []),
            "details": kwargs.get("details"),
            "expires_at": "2099-01-01T00:00:00+00:00",
        }
        self.rows[kwargs["agent_id"]] = row
        self.events.append({"kind": "PRESENT", "agent_id": kwargs["agent_id"]})
        return {"status": "PRESENT", "presence": row}

    def post(self, **kwargs):
        event = {"kind": "MESSAGE", **kwargs}
        self.events.append(event)
        return {"status": "POSTED", "message_event": event}

    def heartbeat(self, **kwargs):
        if self.rows.get(kwargs["agent_id"], {}).get("status") != "ACTIVE":
            return {"status": "NOT_ACTIVE_HOLD"}
        self.events.append({"kind": "HEARTBEAT", **kwargs})
        return {"status": "HEARTBEAT", "presence": self.rows[kwargs["agent_id"]]}

    def release(self, **kwargs):
        self.rows[kwargs["agent_id"]].update({"status": "RELEASED", "outcome": kwargs.get("outcome")})
        self.events.append({"kind": "RELEASE", **kwargs})
        return {"status": "RELEASED", "presence": self.rows[kwargs["agent_id"]]}


class AllocationTests(unittest.TestCase):
    def test_hamilton_conserves(self):
        for seats in range(1, 101):
            q = room.hamilton(seats, room.DOMAIN_PRIOR)
            self.assertEqual(sum(q.values()), seats)

    def test_hamilton_deterministic_tie_break(self):
        self.assertEqual(room.hamilton(1, {"B": 0.5, "A": 0.5}), {"B": 0, "A": 1})

    def test_floor_validation(self):
        with self.assertRaises(ValueError):
            room.hamilton(2, room.WAVE_PRIOR, {"W0": 1, "W1": 1, "W2": 1})

    def test_zero_population_is_truthful(self):
        plan = room.allocation_plan(0)
        self.assertEqual(plan["assignments"], [])
        self.assertEqual(plan["standing"], "NO_PRESENT_WORKERS")

    def test_n1_time_slices_exact_wave_ratio(self):
        schedule = room.allocation_plan(1)["assignments"][0]["wave_schedule"]
        self.assertEqual({wave: schedule.count(wave) for wave in room.WAVES}, {"W0": 5, "W1": 3, "W2": 2})

    def test_n1_does_not_claim_parallelism(self):
        plan = room.allocation_plan(1)
        self.assertEqual(len(plan["assignments"]), 1)
        self.assertIn("NO_FICTIONAL_CONCURRENCY", plan["standing"])

    def test_n2_maps_root_and_explorer(self):
        plan = room.allocation_plan(2)
        self.assertEqual([x["function"] for x in plan["assignments"]], ["ROOT_DELIVERY_INTEGRATOR", "MATH_NAV_LIMITS_EXPLORER"])

    def test_n3_preserves_all_waves(self):
        self.assertEqual(room.allocation_plan(3)["wave_quota"], {"W0": 1, "W1": 1, "W2": 1})

    def test_n4_has_two_delivery_seats(self):
        self.assertEqual(room.allocation_plan(4)["wave_quota"], {"W0": 2, "W1": 1, "W2": 1})

    def test_n5_installs_homeostasis_function(self):
        functions = [x["function"] for x in room.allocation_plan(5)["assignments"]]
        self.assertIn("HOMEOSTASIS_ADVERSARIAL_SCOUT", functions)

    def test_n20_matches_domain_prior(self):
        self.assertEqual(room.allocation_plan(20)["domain_quota"], {key: int(value * 20) for key, value in room.DOMAIN_PRIOR.items()})

    def test_pressure_increases_target_share(self):
        base = room._normalize_shares(room.DOMAIN_PRIOR)
        raised = room._normalize_shares(room.DOMAIN_PRIOR, {"MYTH": 1.0})
        self.assertGreater(raised["MYTH"], base["MYTH"])

    def test_ineligible_domain_gets_no_quota(self):
        plan = room.allocation_plan(10, eligible_domains=["GIT", "MATH"])
        self.assertEqual(set(plan["domain_quota"]), {"GIT", "MATH"})

    def test_unknown_domain_rejected(self):
        with self.assertRaises(ValueError):
            room.allocation_plan(4, eligible_domains=["FAKE"])

    def test_percentages_are_targets_not_authority(self):
        self.assertIn("POSITIVE_FEASIBLE", room.allocation_plan(8)["standing"])


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.board = FakeBoard()
        self.runtime = room.OrganismRoomRuntime(self.board)
        self.base = {
            "agent_id": "root",
            "session_id": "run-1",
            "expected_head": "a" * 40,
            "prompt_stack_digest": "sha256:" + "b" * 64,
            "task": "build organism room",
        }

    def enter(self):
        result = self.runtime.enter(self.base)
        self.base["claim_id"] = result["presence"]["claim_id"]
        return result

    def test_enter_requires_fresh_head(self):
        with self.assertRaisesRegex(ValueError, "STALE_GIT_HEAD"):
            self.runtime.enter({**self.base, "expected_head": "c" * 40})

    def test_enter_binds_prompt_digest_and_session(self):
        result = self.enter()
        details = json.loads(result["presence"]["details"])
        self.assertEqual(details["session_id"], "run-1")
        self.assertEqual(details["prompt_stack_digest"], self.base["prompt_stack_digest"])

    def test_read_separates_census_types(self):
        self.enter()
        census = self.runtime.read({"agent_id": "root", "declared_population": 9})["census"]
        self.assertEqual(census["N_declared"], 9)
        self.assertEqual(census["N_present"], 1)
        self.assertEqual(census["N_execution_observed"], "UNKNOWN")

    def test_work_before_enter_fails(self):
        with self.assertRaisesRegex(ValueError, "NOT_PRESENT"):
            self.runtime.emit({**self.base, "claim_id": "none", "event_kind": "WORK", "payload": {}})

    def test_old_claim_cannot_emit(self):
        self.enter()
        with self.assertRaisesRegex(ValueError, "STALE_CLAIM"):
            self.runtime.emit({**self.base, "claim_id": "old", "event_kind": "DELTA", "payload": {}})

    def test_old_session_cannot_emit(self):
        self.enter()
        with self.assertRaisesRegex(ValueError, "STALE_SESSION"):
            self.runtime.emit({**self.base, "session_id": "run-old", "event_kind": "DELTA", "payload": {}})

    def test_work_event_is_fenced_and_digest_bound(self):
        self.enter()
        result = self.runtime.emit({**self.base, "event_kind": "WORK", "wave": "W0", "domain": "GIT", "payload": {"target": "file"}})
        event = result["room_event"]
        self.assertEqual(event["claim_id"], self.base["claim_id"])
        self.assertTrue(event["semantic_digest"].startswith("sha256:"))

    def test_invalid_wave_rejected(self):
        self.enter()
        with self.assertRaises(ValueError):
            self.runtime.emit({**self.base, "event_kind": "WORK", "wave": "W9", "payload": {}})

    def test_invalid_domain_rejected(self):
        self.enter()
        with self.assertRaises(ValueError):
            self.runtime.emit({**self.base, "event_kind": "WORK", "domain": "FAKE", "payload": {}})

    def test_heartbeat_is_fenced(self):
        self.enter()
        result = self.runtime.heartbeat(self.base)
        self.assertEqual(result["room_event"], "HEARTBEAT")

    def test_signout_without_result_is_not_completion(self):
        self.enter()
        with self.assertRaisesRegex(ValueError, "RESULT_REFERENCE"):
            self.runtime.signout({**self.base, "stop_class": "COMPLETED"})

    def test_blocked_signout_requires_residual(self):
        self.enter()
        with self.assertRaisesRegex(ValueError, "REQUIRES_RESIDUAL"):
            self.runtime.signout({**self.base, "stop_class": "BLOCKED"})

    def test_completed_signout_releases_only_this_session(self):
        self.enter()
        result = self.runtime.signout({**self.base, "stop_class": "COMPLETED", "result_refs": ["commit:123"], "residual_portfolio": []})
        self.assertEqual(result["status"], "RELEASED")
        self.assertEqual(self.board.rows["root"]["status"], "RELEASED")

    def test_post_signout_heartbeat_fails(self):
        self.enter()
        self.runtime.signout({**self.base, "stop_class": "COMPLETED", "result_refs": ["commit:123"]})
        with self.assertRaisesRegex(ValueError, "NOT_PRESENT"):
            self.runtime.heartbeat(self.base)

    def test_signout_ceiling_is_explicit(self):
        self.enter()
        result = self.runtime.signout({**self.base, "stop_class": "COMPLETED", "result_refs": ["commit:123"]})
        self.assertIn("SIGNOUT_TERMINATES_SESSION_NOT_PROOF_OF_RESULT", result["presence"]["outcome"])

    def test_event_digest_is_deterministic(self):
        args = dict(kind="DELTA", agent_id="a", session_id="s", claim_id="c", expected_head="h", wave="W0", domain="GIT", payload={"x": 1})
        self.assertEqual(room._room_packet(**args), room._room_packet(**args))

    def test_unknown_action_rejected(self):
        with self.assertRaises(ValueError):
            self.runtime.call_tool(room.TOOL_NAME, {"action": "pretend"})

    def test_room_never_claims_execution_authority(self):
        self.enter()
        self.assertIn("PRESENCE != HOST_EXECUTION != EXECUTION_AUTHORITY", self.runtime.read({})["laws"])


if __name__ == "__main__":
    unittest.main()

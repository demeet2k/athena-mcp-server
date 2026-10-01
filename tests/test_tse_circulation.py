from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.server import Server
from athena_mcp.tse_population import _digest
from athena_mcp.tse_telemetry import TseHelixTelemetryRuntime


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _write(root: Path, rel: str, value) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture(base: Path):
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"], "BUILD": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    }
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    }
    _write(local, "prompts/PROMPT.manifest.json", manifest)
    _write(local, "prompts/state/ACTIVE.json", active)
    _write(local, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(local, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _write(local, "seed.txt", "seed\n")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed prompt brain")
    parent = _run(local, "rev-parse", "HEAD")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "master")

    _run(local, "checkout", "-b", "child-one")
    _write(local, "child-one.txt", "first verified child delta\n")
    _run(local, "add", "child-one.txt")
    _run(local, "commit", "-m", "first child work")
    child = _run(local, "rev-parse", "HEAD")
    _run(local, "checkout", "master")
    return local, parent, child


class TseCirculationTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        local, self.parent_one, self.child_one = _fixture(Path(self.td.name))
        self.server = Server(str(Path(self.td.name) / "athena.db"), git_root=local)
        self.addCleanup(self.server.store.close)
        self.seq = 0
        self.mission = "MISSION-CIRCULATION-1"

        self.hatch_one = self.make_hatch("HATCH.CYCLE.1", "Q-CYCLE-1", self.parent_one)
        self.route_one = self.make_route(self.hatch_one, "CLAIM.CYCLE.ONE")
        return_one = self.make_return_chain(self.route_one, "CLAIM.CYCLE.ONE", self.child_one, "ONE", 5.0)
        applied_one = self.merge_child_and_apply(
            branch="child-one",
            route=self.route_one,
            hatch=self.hatch_one,
            parent_head=self.parent_one,
            child_head=self.child_one,
            return_event=return_one,
            apply_id="APPLY.CYCLE.1",
        )
        self.origin_s7 = applied_one["return_applied_event_id"]
        self.origin_applied_head = applied_one["applied_head"]

        self.reentry_id = "REENTRY.CYCLE.1"
        self.reentry_started = self.start_reentry()
        self.loop_id = self.reentry_started["rehydration"]["loop_id"]
        self.productive_receipt = self.advance_productive_rehydration()
        self.next_parent = self.server.git.head()

        root = Path(self.server.git.root)
        _run(root, "checkout", "-b", "child-two")
        _write(root, "child-two.txt", "second verified child delta\n")
        _run(root, "add", "child-two.txt")
        _run(root, "commit", "-m", "second child work")
        self.child_two = _run(root, "rev-parse", "HEAD")
        _run(root, "checkout", "master")

        self.hatch_two = self.make_hatch("HATCH.CYCLE.2", "Q-CYCLE-2", self.next_parent)
        self.route_two = self.make_route(self.hatch_two, "CLAIM.CYCLE.TWO")
        return_two = self.make_return_chain(self.route_two, "CLAIM.CYCLE.TWO", self.child_two, "TWO", 9.0)
        applied_two = self.merge_child_and_apply(
            branch="child-two",
            route=self.route_two,
            hatch=self.hatch_two,
            parent_head=self.next_parent,
            child_head=self.child_two,
            return_event=return_two,
            apply_id="APPLY.CYCLE.2",
        )
        self.next_s7 = applied_two["return_applied_event_id"]
        self.next_applied_head = applied_two["applied_head"]

    def rpc(self, method, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return self.server.handle(message)

    def tool(self, name, args):
        response = self.rpc("tools/call", {"name": name, "arguments": args})
        result = response["result"]
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def make_hatch(self, hatch_id, quest_id, parent_head):
        gp = {
            "repo": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/master",
            "head": parent_head,
        }
        checkpoint = {
            "residual": [f"continue {quest_id} through one verified child"],
            "acceptance": [f"{quest_id} child Return is shared-adopted"],
            "git_position": gp,
        }
        checkpoint["checkpoint_digest"] = _digest(checkpoint)
        hatch = {
            "schema_version": "ATHENA.TSE.HATCH.V2",
            "hatch_id": hatch_id,
            "parent_checkpoint_digest": checkpoint["checkpoint_digest"],
            "parent_checkpoint": checkpoint,
            "parent_git_position": gp,
            "child_quest": {"id": quest_id, "version": "1"},
            "status": "CHILD_ACTIVE",
            "platform_counter_reset_claimed": False,
        }
        hatch["hatch_digest"] = _digest(hatch)
        return hatch

    def make_route(self, hatch, claim_id):
        planned = self.tool(
            "athena_tse_population_plan",
            {
                "hatch": hatch,
                "parent_agent_id": "alpha",
                "capabilities": ["code", "tests"],
                "targets": ["*.txt"],
                "role": "BUILDER",
            },
        )
        self.assertEqual("TSE_POPULATION_NEED_READY", planned["status"], planned)
        route = copy.deepcopy(planned["route"])
        route["status"] = "SUBTASK_CLAIMED"
        route["child_claim"] = {
            "agent_id": "beta",
            "claim_id": claim_id,
            "work_key": route["child_work_key"],
            "mode": "PRIMARY",
            "join_of": None,
            "claim_base_head": hatch["parent_git_position"]["head"],
            "binding": "EXACT_CHILD_WORK_KEY",
        }
        return route

    def source_event(
        self,
        route,
        claim_id,
        transition,
        *,
        parent=None,
        ref=None,
        child=False,
        source_kind=None,
        source_git_head=None,
        delta=None,
    ):
        runtime = TseHelixTelemetryRuntime(self.server)
        ref = ref or f"SRC-{transition}"
        out = runtime.record_source_bound(
            mission_id=self.mission,
            route_id=route["route_id"],
            hatch_id=route["hatch_id"],
            transition=transition,
            actor_id="observer",
            witnesses=[f"witness:{transition}"],
            cost={"known": True, "total": 0.1},
            source_kind=source_kind or f"TEST_{transition}",
            source_ref=ref,
            source_payload={"transition": transition, "ref": ref, "route_id": route["route_id"]},
            source_git_head=source_git_head,
            source_authority="TEST_SOURCE",
            parent_event_id=parent,
            child_agent_id="beta" if child else None,
            child_claim_id=claim_id if child else None,
            verified_delta=delta,
            attempt_ref=ref,
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", out["status"], out)
        return out["event"]

    def make_return_chain(self, route, claim_id, child_head, suffix, delta):
        root = self.source_event(route, claim_id, "HATCH_CREATED", ref=f"{suffix}.0")
        published = self.source_event(route, claim_id, "HATCH_NEED_PUBLISHED", parent=root["event_id"], ref=f"{suffix}.1")
        matched = self.source_event(route, claim_id, "MATCH_FOUND", parent=published["event_id"], ref=f"{suffix}.2")
        routed = self.source_event(route, claim_id, "HANDOFF_ROUTED", parent=matched["event_id"], ref=f"{suffix}.3")
        claimed = self.source_event(route, claim_id, "CHILD_CLAIMED", parent=routed["event_id"], ref=f"{suffix}.4", child=True)
        return self.source_event(
            route,
            claim_id,
            "CHILD_VERIFIED_RETURN",
            parent=claimed["event_id"],
            ref=f"{suffix}.5",
            child=True,
            source_kind="TSE_RETURN_CHECK",
            source_git_head=child_head,
            delta=delta,
        )

    def merge_child_and_apply(self, *, branch, route, hatch, parent_head, child_head, return_event, apply_id):
        root = Path(self.server.git.root)
        _run(root, "merge", "--no-ff", branch, "-m", f"apply {branch}")
        applied = _run(root, "rev-parse", "HEAD")
        _run(root, "push", "origin", "master")
        result = self.tool(
            "athena_tse_helix_advance",
            {
                "mission_id": self.mission,
                "operation": "APPLY",
                "route": route,
                "parent_event_id": return_event["event_id"],
                "actor_id": "observer",
                "witnesses": [f"test:{apply_id}"],
                "cost": {"known": True, "total": 1.0},
                "child_return": {
                    "hatch": hatch,
                    "apply_receipt": {
                        "schema_version": "ATHENA.TSE.KNOT.APPLY.RECEIPT.V1",
                        "apply_id": apply_id,
                        "mode": "ANCESTRY_ADOPTION",
                        "parent_head": parent_head,
                        "child_head": child_head,
                        "applied_head": applied,
                        "apply_witnesses": ["git:merge", "test:child-pass"],
                        "platform_counter_reset_claimed": False,
                    },
                },
            },
        )
        self.assertEqual("TSE_KNOT_APPLY_OBSERVED", result["status"], result)
        return result

    @staticmethod
    def metrics(value=0.7):
        return {
            "utility": value,
            "dependency_unblocking": value,
            "uncertainty_reduction": value,
            "novelty": value,
            "risk": 0.1,
            "cost": 0.1,
            "repetition": 0.0,
        }

    def start_reentry(self):
        result = self.tool(
            "athena_tse_helix_advance",
            {
                "mission_id": self.mission,
                "operation": "REENTRY_START",
                "route": self.route_one,
                "parent_event_id": self.origin_s7,
                "actor_id": "observer",
                "witnesses": ["test:reentry-start"],
                "cost": {"known": True, "total": 0.2},
                "child_return": {
                    "hatch": self.hatch_one,
                    "reentry": {
                        "schema_version": "ATHENA.TSE.REENTRY.PACKET.V1",
                        "reentry_id": self.reentry_id,
                        "goal": "Continue from the first incorporated Return",
                        "successor_candidates": [
                            {"task": "Perform one bounded productive rehydration step", "metrics": self.metrics()}
                        ],
                        "profile": "BUILD",
                        "use_frontier": False,
                        "fetch": False,
                        "required_passes": ["reconstruct", "execute", "verify"],
                        "max_steps": 8,
                        "max_no_progress": 2,
                        "platform_counter_reset_claimed": False,
                    },
                },
                "shared_remote_mode": "REQUIRED",
            },
        )
        self.assertEqual("TSE_REENTRY_STARTED", result["status"], result)
        return result

    def advance_productive_rehydration(self):
        loop_result = self.reentry_started["rehydration"]
        root = Path(self.server.git.root)
        _write(root, "reentry-work.txt", "observed bounded productive work\n")
        _run(root, "add", "reentry-work.txt")
        _run(root, "commit", "-m", "perform productive reentry work")
        _run(root, "push", "origin", "master")

        loop = self.server.aor_development.transport.tse_helix.reentry._loop_runtime()
        result = loop.advance(
            loop_id=loop_result["loop_id"],
            expected_checkpoint_head=loop_result["checkpoint_head"],
            expected_state_digest=loop_result["state_digest"],
            expected_prompt_digest=loop_result["prompt_digest"],
            actor="observer",
            completion={
                "status": "PARTIAL",
                "observed": True,
                "terminal": False,
                "hard_hold": False,
                "summary": "one bounded productive rehydration step completed",
                "progress_delta": 1.0,
                "passes": [
                    {"kind": "reconstruct", "summary": "reconstructed exact shared coordinates", "evidence_refs": []},
                    {"kind": "execute", "summary": "committed bounded work", "evidence_refs": ["git:reentry-work"]},
                    {"kind": "verify", "summary": "observed work commit and push", "evidence_refs": ["git:shared"]},
                ],
                "tests": [{"name": "fixture", "status": "PASS", "evidence_ref": "test:fixture"}],
                "evidence_refs": ["git:reentry-work"],
                "residuals": ["spawn next bounded child"],
                "next_task": "spawn next bounded child",
                "handoff_to": None,
            },
            shared_remote_mode="REQUIRED",
        )
        self.assertEqual("ACTIVE", result["status"], result)
        self.assertFalse(result["no_progress_count"])
        return result

    def observe_args(self, cycle_id="CYCLE.1", **overrides):
        args = {
            "cycle_id": cycle_id,
            "mission_id": self.mission,
            "origin_route": self.route_one,
            "origin_hatch": self.hatch_one,
            "origin_return_applied_event_id": self.origin_s7,
            "reentry_id": self.reentry_id,
            "rehydration_loop_id": self.loop_id,
            "next_route": self.route_two,
            "next_hatch": self.hatch_two,
            "next_return_applied_event_id": self.next_s7,
            "actor_id": "observer",
            "witnesses": ["test:closed-cycle"],
        }
        args.update(overrides)
        return args

    def test_closed_cycle_is_sequence_bound_and_not_causal(self):
        result = self.tool("athena_tse_circulation_observe", self.observe_args())
        self.assertEqual("TSE_CIRCULATION_OBSERVED", result["status"], result)
        receipt = result["receipt"]
        self.assertEqual("CLOSED_SEQUENCE_BOUND", receipt["status"])
        self.assertEqual(self.origin_s7, receipt["origin"]["return_applied_event_id"])
        self.assertEqual(self.next_s7, receipt["next"]["return_applied_event_id"])
        self.assertEqual(self.reentry_id, receipt["reentry"]["reentry_id"])
        self.assertEqual(self.loop_id, receipt["reentry"]["loop_id"])
        self.assertGreaterEqual(receipt["productive_rehydration_steps"], 1)
        self.assertGreaterEqual(receipt["rehydration_steps_total"], 1)
        self.assertIn("reentry-work.txt", receipt["material_work_paths_unique"])
        self.assertEqual(9.0, receipt["verified_incorporated_delta"])
        self.assertGreater(receipt["known_source_bound_tse_cost_total"], 0)
        self.assertFalse(receipt["cost_complete"])
        self.assertEqual("UNKNOWN", receipt["incorporated_delta_per_total_cost"])
        self.assertEqual("UNKNOWN", receipt["causal_effect"])
        self.assertFalse(receipt["execution_authority"])

    def test_exact_cycle_replay_is_idempotent(self):
        first = self.tool("athena_tse_circulation_observe", self.observe_args(cycle_id="CYCLE.REPLAY"))
        head = self.server.git.head()
        replay = self.tool("athena_tse_circulation_observe", self.observe_args(cycle_id="CYCLE.REPLAY"))
        self.assertEqual("TSE_CIRCULATION_ALREADY_OBSERVED", replay["status"], replay)
        self.assertEqual(first["receipt"]["semantic_digest"], replay["receipt"]["semantic_digest"])
        self.assertEqual(head, self.server.git.head())
        self.assertFalse(replay["current_shared_frontier_revalidated"])

    def test_wrong_reentry_identity_fails_closed(self):
        result = self.tool(
            "athena_tse_circulation_observe",
            self.observe_args(cycle_id="CYCLE.WRONG.REENTRY", reentry_id="REENTRY.WRONG"),
        )
        self.assertEqual("TSE_CIRCULATION_HOLD", result["status"], result)
        self.assertEqual("reentry_id_loop_marker_mismatch", result["reason"])

    def test_same_origin_and_next_event_rejected(self):
        args = self.observe_args(cycle_id="CYCLE.SAME")
        args["next_return_applied_event_id"] = self.origin_s7
        result = self.tool("athena_tse_circulation_observe", args)
        self.assertEqual("origin_and_next_return_applied_events_must_differ", result["reason"])

    def test_report_does_not_invent_pending_denominator_or_total_cost(self):
        self.tool("athena_tse_circulation_observe", self.observe_args(cycle_id="CYCLE.REPORT"))
        report = self.tool("athena_tse_circulation_report", {"mission_id": self.mission})
        self.assertEqual("TSE_CIRCULATION_REPORT", report["status"], report)
        self.assertEqual(1, report["closed_cycles"])
        self.assertEqual("UNKNOWN", report["pending_cycles"])
        self.assertEqual("UNKNOWN", report["closure_rate"])
        self.assertEqual("UNKNOWN", report["incorporated_delta_per_total_cost"])
        self.assertFalse(report["cost_complete"])
        self.assertEqual("UNKNOWN", report["causal_effect"])

    def test_tools_and_resource_are_registered(self):
        tools = {row["name"] for row in self.rpc("tools/list")["result"]["tools"]}
        self.assertIn("athena_tse_circulation_observe", tools)
        self.assertIn("athena_tse_circulation_report", tools)
        resources = {row["uri"] for row in self.rpc("resources/list")["result"]["resources"]}
        self.assertIn("athena://tse-circulation/v1", resources)
        resource = self.rpc("resources/read", {"uri": "athena://tse-circulation/v1"})["result"]["contents"][0]
        payload = json.loads(resource["text"])
        self.assertEqual("MEASUREMENT_ONLY", payload["authority"])
        self.assertEqual("UNKNOWN", payload["causal_effect"])


if __name__ == "__main__":
    unittest.main()

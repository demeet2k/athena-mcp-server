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
        "modules": {
            "core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}
        },
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

    _run(local, "checkout", "-b", "child")
    _write(local, "child.txt", "verified child delta\n")
    _run(local, "add", "child.txt")
    _run(local, "commit", "-m", "child work")
    child = _run(local, "rev-parse", "HEAD")
    _run(local, "checkout", "master")
    return local, parent, child


class TseReentryTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        local, self.parent_head, self.child_head = _fixture(Path(self.td.name))
        self.server = Server(str(Path(self.td.name) / "athena.db"), git_root=local)
        self.addCleanup(self.server.store.close)
        self.seq = 0
        self.mission = "MISSION-REENTRY-1"
        self.hatch = self.make_hatch()
        self.route = self.make_route()
        self.return_event = self.make_return_chain()
        self.applied_head, self.applied_event_id, self.post_s7_head = self.make_applied()

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

    def make_hatch(self):
        gp = {
            "repo": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/master",
            "head": self.parent_head,
        }
        checkpoint = {
            "residual": ["recompute the post-adoption frontier"],
            "acceptance": ["start the next bounded cycle only from shared current state"],
            "git_position": gp,
        }
        checkpoint["checkpoint_digest"] = _digest(checkpoint)
        hatch = {
            "schema_version": "ATHENA.TSE.HATCH.V2",
            "hatch_id": "HATCH.REENTRY.1",
            "parent_checkpoint_digest": checkpoint["checkpoint_digest"],
            "parent_checkpoint": checkpoint,
            "parent_git_position": gp,
            "child_quest": {"id": "Q-REENTRY-CHILD", "version": "1"},
            "status": "CHILD_ACTIVE",
            "platform_counter_reset_claimed": False,
        }
        hatch["hatch_digest"] = _digest(hatch)
        return hatch

    def make_route(self):
        planned = self.tool(
            "athena_tse_population_plan",
            {
                "hatch": self.hatch,
                "parent_agent_id": "alpha",
                "capabilities": ["code", "tests"],
                "targets": ["child.txt"],
                "role": "BUILDER",
            },
        )
        self.assertEqual("TSE_POPULATION_NEED_READY", planned["status"], planned)
        route = copy.deepcopy(planned["route"])
        route["status"] = "SUBTASK_CLAIMED"
        route["child_claim"] = {
            "agent_id": "beta",
            "claim_id": "CLAIM.REENTRY.BETA",
            "work_key": route["child_work_key"],
            "mode": "PRIMARY",
            "join_of": None,
            "claim_base_head": self.parent_head,
            "binding": "EXACT_CHILD_WORK_KEY",
        }
        return route

    def source_event(
        self,
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
            route_id=self.route["route_id"],
            hatch_id=self.route["hatch_id"],
            transition=transition,
            actor_id="observer",
            witnesses=[f"witness:{transition}"],
            cost={"known": True, "total": 0.1},
            source_kind=source_kind or f"TEST_{transition}",
            source_ref=ref,
            source_payload={"transition": transition, "ref": ref, "route_id": self.route["route_id"]},
            source_git_head=source_git_head,
            source_authority="TEST_SOURCE",
            parent_event_id=parent,
            child_agent_id="beta" if child else None,
            child_claim_id="CLAIM.REENTRY.BETA" if child else None,
            verified_delta=delta,
            attempt_ref=ref,
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_SOURCE_BOUND", out["status"], out)
        return out["event"]

    def make_return_chain(self):
        root = self.source_event("HATCH_CREATED", ref="R0")
        published = self.source_event("HATCH_NEED_PUBLISHED", parent=root["event_id"], ref="R1")
        matched = self.source_event("MATCH_FOUND", parent=published["event_id"], ref="R2")
        routed = self.source_event("HANDOFF_ROUTED", parent=matched["event_id"], ref="R3")
        claimed = self.source_event("CHILD_CLAIMED", parent=routed["event_id"], ref="R4", child=True)
        return self.source_event(
            "CHILD_VERIFIED_RETURN",
            parent=claimed["event_id"],
            ref="RETURN.REENTRY.1",
            child=True,
            source_kind="TSE_RETURN_CHECK",
            source_git_head=self.child_head,
            delta=7.0,
        )

    def make_applied(self):
        root = Path(self.server.git.root)
        _run(root, "merge", "--no-ff", "child", "-m", "apply verified child")
        applied = _run(root, "rev-parse", "HEAD")
        _run(root, "push", "origin", "master")
        result = self.tool(
            "athena_tse_helix_advance",
            {
                "mission_id": self.mission,
                "operation": "APPLY",
                "route": self.route,
                "parent_event_id": self.return_event["event_id"],
                "actor_id": "observer",
                "witnesses": ["test:shared-adoption"],
                "cost": {"known": True, "total": 1.0},
                "child_return": {
                    "hatch": self.hatch,
                    "apply_receipt": {
                        "schema_version": "ATHENA.TSE.KNOT.APPLY.RECEIPT.V1",
                        "apply_id": "APPLY.REENTRY.1",
                        "mode": "ANCESTRY_ADOPTION",
                        "parent_head": self.parent_head,
                        "child_head": self.child_head,
                        "applied_head": applied,
                        "apply_witnesses": ["git:merge", "test:child-pass"],
                        "platform_counter_reset_claimed": False,
                    },
                },
            },
        )
        self.assertEqual("TSE_KNOT_APPLY_OBSERVED", result["status"], result)
        return applied, result["return_applied_event_id"], self.server.git.head()

    @staticmethod
    def metrics(value=0.5):
        return {
            "utility": value,
            "dependency_unblocking": value,
            "uncertainty_reduction": value,
            "novelty": value,
            "risk": value,
            "cost": value,
            "repetition": value,
        }

    def packet(self, *, reentry_id="REENTRY.1", candidates=None, **updates):
        reentry = {
            "schema_version": "ATHENA.TSE.REENTRY.PACKET.V1",
            "reentry_id": reentry_id,
            "goal": "Continue the mission from the verified incorporated child state",
            "successor_candidates": candidates
            if candidates is not None
            else [{"task": "Audit the incorporated child and select the next residual", "metrics": self.metrics(0.7)}],
            "successor_policy": {},
            "profile": "BUILD",
            "use_frontier": False,
            "fetch": False,
            "allow_parent_residual_fallback": False,
            "allow_ambiguity_resolution": False,
            "terminal_request": False,
            "max_steps": 8,
            "max_no_progress": 2,
            "depth_mode": "deep",
            "platform_counter_reset_claimed": False,
        }
        reentry.update(updates)
        return {"hatch": copy.deepcopy(self.hatch), "reentry": reentry}

    def helix(self, operation, packet, *, event_id=None):
        return self.tool(
            "athena_tse_helix_advance",
            {
                "mission_id": self.mission,
                "operation": operation,
                "route": self.route,
                "parent_event_id": event_id or self.applied_event_id,
                "actor_id": "observer",
                "witnesses": [f"test:{operation.lower()}"],
                "cost": {"known": True, "total": 0.2},
                "child_return": packet,
                "shared_remote_mode": "REQUIRED",
            },
        )

    def test_preview_separates_semantic_apply_head_from_continuation_head(self):
        before = self.server.git.head()
        preview = self.helix("REENTRY_PREVIEW", self.packet())
        after = self.server.git.head()
        self.assertEqual("TSE_REENTRY_READY", preview["status"], preview)
        self.assertEqual(self.applied_head, preview["applied_semantic_head"])
        self.assertEqual(self.post_s7_head, preview["continuation_shared_head"])
        self.assertNotEqual(preview["applied_semantic_head"], preview["continuation_shared_head"])
        self.assertEqual(before, after)
        self.assertFalse(preview["reentry_started"])
        self.assertFalse(preview["background_execution"])
        self.assertEqual("ROUTING_ONLY", preview["routing"]["authority"])

    def test_start_delegates_to_existing_rehydration_loop_and_replay_is_idempotent(self):
        packet = self.packet()
        started = self.helix("REENTRY_START", packet)
        self.assertEqual("TSE_REENTRY_STARTED", started["status"], started)
        self.assertTrue(started["reentry_started"])
        self.assertFalse(started["background_execution"])
        self.assertEqual("STARTED", started["rehydration"]["status"])
        self.assertEqual(self.post_s7_head, started["continuation_shared_head_before_start"])
        self.assertIn("CYCLE != BACKGROUND_EXECUTION", started["rehydration"]["compiled_self_prompt"])
        head_after_start = self.server.git.head()
        replay = self.helix("REENTRY_START", packet)
        self.assertEqual("TSE_REENTRY_ALREADY_STARTED", replay["status"], replay)
        self.assertEqual(started["rehydration"]["loop_id"], replay["existing_loop"]["loop_id"])
        self.assertEqual(head_after_start, self.server.git.head())

    def test_changed_same_reentry_id_conflicts(self):
        first = self.helix("REENTRY_START", self.packet(reentry_id="REENTRY.CONFLICT"))
        self.assertEqual("TSE_REENTRY_STARTED", first["status"], first)
        changed = self.packet(
            reentry_id="REENTRY.CONFLICT",
            candidates=[{"task": "Different successor semantics", "metrics": self.metrics(0.9)}],
        )
        held = self.helix("REENTRY_START", changed)
        self.assertEqual("TSE_REENTRY_HOLD", held["status"], held)
        self.assertEqual("changed_same_reentry_id_conflict", held["reason"])

    def test_ambiguity_is_preserved_until_explicit_resolution_permission(self):
        candidates = [
            {"task": "Path Alpha", "metrics": self.metrics(0.5)},
            {"task": "Path Beta", "metrics": self.metrics(0.5)},
        ]
        packet = self.packet(reentry_id="REENTRY.AMB", candidates=candidates)
        preview = self.helix("REENTRY_PREVIEW", packet)
        self.assertEqual("TSE_REENTRY_AMBIGUOUS", preview["status"], preview)
        self.assertEqual(2, len(preview["routing"]["ties"]))
        held = self.helix("REENTRY_START", packet)
        self.assertEqual("successor_ambiguity_requires_explicit_resolution_permission", held["reason"])
        permitted = self.packet(
            reentry_id="REENTRY.AMB",
            candidates=candidates,
            allow_ambiguity_resolution=True,
        )
        started = self.helix("REENTRY_START", permitted)
        self.assertEqual("TSE_REENTRY_STARTED", started["status"], started)
        self.assertIn("Path Alpha", started["selected_task"])
        self.assertIn("Path Beta", started["selected_task"])

    def test_terminal_request_blocks_start_and_mints_no_execution_authority(self):
        before = self.server.git.head()
        packet = self.packet(
            reentry_id="REENTRY.STOP",
            terminal_request=True,
            terminal_witnesses=["human:closure-request"],
        )
        result = self.helix("REENTRY_START", packet)
        self.assertEqual("TSE_REENTRY_STOP_REQUESTED", result["status"], result)
        self.assertFalse(result["reentry_started"])
        self.assertFalse(result["execution_authority"])
        self.assertEqual(before, self.server.git.head())

    def test_declared_only_return_applied_is_rejected(self):
        runtime = TseHelixTelemetryRuntime(self.server)
        out = runtime.record(
            mission_id=self.mission,
            route_id=self.route["route_id"],
            hatch_id=self.route["hatch_id"],
            transition="RETURN_APPLIED",
            actor_id="caller",
            witnesses=["caller:declared"],
            cost={"known": True, "total": 0.1},
            parent_event_id=self.return_event["event_id"],
            child_agent_id="beta",
            child_claim_id="CLAIM.REENTRY.BETA",
            verified_delta=7.0,
            attempt_ref="DECLARED.REENTRY.APPLY",
        )
        self.assertEqual("TSE_TELEMETRY_RECORDED_DECLARED", out["status"], out)
        held = self.helix(
            "REENTRY_PREVIEW",
            self.packet(reentry_id="REENTRY.DECLARED"),
            event_id=out["event"]["event_id"],
        )
        self.assertEqual("return_applied_event_not_source_bound_shared_adoption", held["reason"])

    def test_reentry_requires_shared_remote_mode_required_and_reset_claim_fails_closed(self):
        packet = self.packet(reentry_id="REENTRY.MODE")
        result = self.tool(
            "athena_tse_helix_advance",
            {
                "mission_id": self.mission,
                "operation": "REENTRY_PREVIEW",
                "route": self.route,
                "parent_event_id": self.applied_event_id,
                "actor_id": "observer",
                "witnesses": ["test:mode"],
                "cost": {"known": True, "total": 0.2},
                "child_return": packet,
                "shared_remote_mode": "DISABLED",
            },
        )
        self.assertEqual("reentry_requires_shared_remote_mode_required", result["reason"])

        reset = self.packet(reentry_id="REENTRY.RESET")
        reset["reentry"]["platform_counter_reset_claimed"] = True
        held = self.helix("REENTRY_PREVIEW", reset)
        self.assertEqual("platform_counter_reset_claimed_must_be_false", held["reason"])

    def test_reentry_operations_registered(self):
        tools = {row["name"]: row for row in self.rpc("tools/list")["result"]["tools"]}
        enum = tools["athena_tse_helix_advance"]["inputSchema"]["properties"]["operation"]["enum"]
        self.assertIn("REENTRY_PREVIEW", enum)
        self.assertIn("REENTRY_START", enum)


if __name__ == "__main__":
    unittest.main()

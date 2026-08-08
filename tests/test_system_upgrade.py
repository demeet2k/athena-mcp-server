import json
import os
import tempfile
import unittest

from athena_mcp.hub_server import HubServer


class SystemUpgradeTests(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        handle.close()
        self.db = handle.name
        self.server = HubServer(self.db)
        self.seq = 0

    def tearDown(self):
        try:
            self.server.store.close()
        except Exception:
            pass
        try:
            os.unlink(self.db)
        except Exception:
            pass

    def rpc(self, method, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return self.server.handle(message)

    def tool(self, name, args=None, expect_error=False):
        response = self.rpc(
            "tools/call",
            {"name": name, "arguments": args or {}},
        )
        result = response["result"]
        if expect_error:
            self.assertTrue(result.get("isError"), response)
            return result
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    @staticmethod
    def task_witness(ref="test://task", head=None, result="PASS"):
        packet = {
            "observed": True,
            "ref": ref,
            "procedure": {"runner": "unittest", "command": "deterministic probe"},
            "observation": {"returncode": 0, "stdout": "PASS"},
            "result": result,
            "independence_key": "unit:test-system-upgrade",
        }
        if head is not None:
            packet["head_sha"] = head
        return packet

    @staticmethod
    def external_witness(head, kind):
        return {
            "observed": True,
            "ref": f"{kind}://synthetic-system-upgrade-test",
            "head_sha": head,
            "conclusion": "success",
        }

    def migrate_and_plan(self, head="abc123exacthead"):
        migration = self.tool("athena_schema_migrate")
        self.assertIn(migration["status"], {"APPLIED", "UP_TO_DATE"})
        plan = self.tool(
            "athena_system_upgrade_plan",
            {
                "objective": "upgrade the complete runtime",
                "target_version": "2.6.0",
                "expected_git_head": head,
            },
        )
        return plan

    def test_surface_manifest_and_measured_local_ic10(self):
        names = {
            item["name"]
            for item in self.rpc("tools/list")["result"]["tools"]
        }
        for name in (
            "athena_system_upgrade_manifest",
            "athena_system_upgrade_plan",
            "athena_system_upgrade_observe",
            "athena_system_upgrade_replay",
            "athena_system_release_certificate",
            "athena_system_release_replay",
        ):
            self.assertIn(name, names)
        uris = {
            item["uri"]
            for item in self.rpc("resources/list")["result"]["resources"]
        }
        for uri in (
            "athena://system/upgrade",
            "athena://system/upgrade/frontier",
            "athena://system/release",
        ):
            self.assertIn(uri, uris)

        plan = self.migrate_and_plan()
        self.assertTrue(plan["run_id"].startswith("UPGRUN."))
        self.assertTrue(plan["athena_ready_local"], plan)
        self.assertEqual(
            plan["gate_states"],
            {key: "PASS" for key in "CIEPRVOMSX"},
        )
        self.assertEqual(
            plan["frontier"]["frontier"][0]["task_id"],
            "TASK.000",
        )
        manifest = self.tool("athena_system_upgrade_manifest")
        self.assertEqual(manifest["source_tasks"]["count"], 126)
        self.assertIn("system_release_certificates", manifest["tables"])

    def test_witnessed_cas_observation_and_replay(self):
        plan = self.migrate_and_plan()
        first_task = plan["frontier"]["frontier"][0]["task_id"]
        observed = self.tool(
            "athena_system_upgrade_observe",
            {
                "run_id": plan["run_id"],
                "task_id": first_task,
                "expected_state_digest": plan["state_digest"],
                "refresh_local": False,
                "witness": self.task_witness(),
            },
        )
        self.assertEqual(observed["source_completion"]["completed"], 1)
        self.assertEqual(observed["seq"], 1)
        replay = self.tool(
            "athena_system_upgrade_replay",
            {"run_id": plan["run_id"]},
        )
        self.assertTrue(replay["match"], replay)
        self.assertEqual(replay["event_count"], 2)

        stale = self.tool(
            "athena_system_upgrade_refresh",
            {
                "run_id": plan["run_id"],
                "expected_state_digest": plan["state_digest"],
            },
            expect_error=True,
        )
        self.assertIn("STALE_UPGRADE_STATE", json.dumps(stale))

    def test_invalid_witness_and_blocked_dependency_fail_closed(self):
        plan = self.migrate_and_plan()
        first_task = plan["frontier"]["frontier"][0]["task_id"]
        invalid = self.tool(
            "athena_system_upgrade_observe",
            {
                "run_id": plan["run_id"],
                "task_id": first_task,
                "expected_state_digest": plan["state_digest"],
                "witness": self.task_witness(result="FAIL"),
            },
            expect_error=True,
        )
        self.assertIn("INVALID_WITNESS", json.dumps(invalid))

        blocked_task_id = "TASK.001"
        dependency_error = self.tool(
            "athena_system_upgrade_observe",
            {
                "run_id": plan["run_id"],
                "task_id": blocked_task_id,
                "expected_state_digest": plan["state_digest"],
                "witness": self.task_witness(),
            },
            expect_error=True,
        )
        self.assertIn("TASK_BLOCKED", json.dumps(dependency_error))

    def test_exact_head_release_certificate_and_replay(self):
        head = "feedface1234567890"
        plan = self.migrate_and_plan(head)
        blocked = self.tool(
            "athena_system_release_certificate",
            {
                "run_id": plan["run_id"],
                "git_head": "different-head",
                "ci_witness": self.external_witness("different-head", "ci"),
                "smoke_witness": self.external_witness("different-head", "smoke"),
            },
        )
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertEqual(blocked["gates"]["expected_head"]["status"], "FAIL")

        qualified = self.tool(
            "athena_system_release_certificate",
            {
                "run_id": plan["run_id"],
                "git_head": head,
                "ci_witness": self.external_witness(head, "ci"),
                "smoke_witness": self.external_witness(head, "smoke"),
                "require_source_completion": False,
            },
        )
        self.assertEqual(qualified["status"], "QUALIFIED", qualified)
        self.assertTrue(qualified["release_allowed"])
        self.assertTrue(qualified["certificate_id"].startswith("RELCERT."))
        replay = self.tool(
            "athena_system_release_replay",
            {"certificate_id": qualified["certificate_id"]},
        )
        self.assertTrue(replay["match"], replay)

    def test_upgrade_run_survives_restart(self):
        plan = self.migrate_and_plan()
        run_id = plan["run_id"]
        digest = plan["state_digest"]
        self.server.store.close()
        self.server = HubServer(self.db)
        self.seq = 100
        restored = self.tool(
            "athena_system_upgrade_state", {"run_id": run_id}
        )
        self.assertEqual(restored["state_digest"], digest)
        self.assertTrue(
            self.tool(
                "athena_system_upgrade_replay", {"run_id": run_id}
            )["match"]
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

import athena_mcp
from athena_mcp import agent_bootstrap as _boot
from athena_mcp.capability_basis import BASIS_ADDRESS_KEY if False else derive_operational_basis
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES


class _Prompt:
    available = True

    def compile(self, task="", profile=None, include_text=False):
        return {
            "profile": profile or "MAXDEV",
            "selected_modules": ["core", "git_organism"],
            "selected_overlays": [],
            "git_head": "brain-head",
            "prompt_stack_digest": "prompt-digest",
            "ancestry": {"core": "blob-core", "git_organism": "blob-git"},
        }


class _Frontier:
    def hydrate(self, **kwargs):
        return {
            "status": "HYDRATED",
            "source_ref": kwargs.get("source_ref"),
            "resolved_ref": "refs/remotes/origin/runtime",
            "source_head": "frontier-head",
            "frontier_digest": "frontier-digest",
            "ready_work": [],
            "claims": [],
            "claim_readiness_suppressed": [],
            "residuals": [],
            "source_coverage": {"events": True},
            "sched_contract": {"status": "PASS", "contracts": {}},
            "remote_checked": True,
            "fetch_error": None,
        }

    def select(self, **kwargs):
        return {
            "status": "NO_REPLAYABLE_READY_WORK",
            "selected": None,
            "pareto_front": [],
        }


class _Issues:
    def snapshot(self, **kwargs):
        return {
            "status": "FRESH",
            "fresh": True,
            "repo": "demeet2k/Athena",
            "relevant": [],
            "digest": "issue-digest",
            "witness": {"provider": "test"},
        }


class _Loop:
    def index(self, **kwargs):
        return {
            "status": "OK",
            "loops": [],
            "shared_frontier_verified": False,
            "freshness_law": "TEST",
            "remote_sync": {"status": "DISABLED"},
        }


class _Handoff:
    def derive(self, *args, **kwargs):
        raise AssertionError("derive should not run when no active loop exists")


class CapabilityBasisBootstrapTests(unittest.TestCase):
    def _runtime(self):
        runtime = athena_mcp.AgentBootstrapRuntime(
            GitBackend(),
            prompt_runtime=_Prompt(),
            frontier_runtime=_Frontier(),
            issue_provider=_Issues(),
        )
        runtime._agent_bootstrap_rehydration_loop_v1 = _Loop()
        runtime._agent_bootstrap_handoff_runtime_v1 = _Handoff()
        return runtime

    def test_public_read_only_basis_is_registered_and_dispatchable(self):
        self.assertIn("athena_capability_basis", athena_mcp.PROMPT_RUNTIME_TOOL_NAMES)
        self.assertIn("athena_capability_basis", athena_mcp.AGENT_BOOT_TOOL_NAMES)
        tool = next(row for row in athena_mcp.PROMPT_RUNTIME_TOOLS if row["name"] == "athena_capability_basis")
        self.assertEqual((tool["inputSchema"].get("properties") or {}), {})

        prompt_runtime = athena_mcp.PromptRuntime(GitBackend())
        basis = prompt_runtime.call_tool("athena_capability_basis", {})
        self.assertEqual(basis["status"], "PASS")
        self.assertEqual(basis["runtime_identity"], "IN_PROCESS_REGISTERED_SURFACE")
        self.assertIn("athena_capability_basis", {
            row["operation"] for row in basis["descriptors"]
        })

    def test_bootstrap_binds_basis_as_independent_address_coordinate(self):
        runtime = self._runtime()
        packet = runtime.bootstrap(
            agent_id="agent-a",
            task="capability negotiation",
            source_ref="runtime",
            continuation_shared_remote_mode="DISABLED",
        )
        basis = packet["operational_basis"]
        self.assertEqual(basis["status"], "PASS")
        self.assertEqual(
            packet["address"]["operational_basis_digest"],
            basis["basis_digest"],
        )
        self.assertEqual(
            packet["execution_surface"]["operational_basis_digest"],
            basis["basis_digest"],
        )
        self.assertEqual(packet["status"], "BOOTSTRAPPED")
        self.assertEqual(
            runtime._sessions[packet["session_id"]]["address"]["operational_basis_digest"],
            basis["basis_digest"],
        )

    def test_new_unclassified_negotiated_operation_holds_bootstrap_and_refreshes_basis_cone(self):
        runtime = self._runtime()
        first = runtime.bootstrap(
            agent_id="agent-a",
            task="capability negotiation",
            source_ref="runtime",
            continuation_shared_remote_mode="DISABLED",
        )
        session_id = first["session_id"]
        fake_name = "athena_frontier_unclassified_test"
        self.assertNotIn(fake_name, PROMPT_RUNTIME_TOOL_NAMES)
        PROMPT_RUNTIME_TOOL_NAMES.add(fake_name)
        try:
            second = runtime.refresh(
                session_id=session_id,
                continuation_shared_remote_mode="DISABLED",
            )
        finally:
            PROMPT_RUNTIME_TOOL_NAMES.discard(fake_name)

        self.assertEqual(second["status"], "BOOTSTRAP_HOLD")
        self.assertIn("HOLD_UNCLASSIFIED_CAPABILITY", second["holds"])
        self.assertIn(fake_name, second["operational_basis"]["unclassified"])
        self.assertTrue(second["refresh"]["changed"]["operational_basis_digest"])
        self.assertTrue(second["refresh"]["operational_basis_changed"])
        self.assertIn("operational_basis", second["refresh"]["affected_dependency_cone"])
        self.assertTrue(second["refresh"]["requires_replan"])

    def test_basis_content_identity_stays_separate_from_runtime_witness(self):
        names = set(PROMPT_RUNTIME_TOOL_NAMES)
        a = derive_operational_basis(names, runtime_identity="runtime-a")
        b = derive_operational_basis(names, runtime_identity="runtime-b")
        self.assertEqual(a["basis_digest"], b["basis_digest"])
        self.assertNotEqual(a["runtime_identity"], b["runtime_identity"])

    def test_address_key_is_registered_without_rewriting_prompt_or_frontier_identity(self):
        self.assertIn("operational_basis_digest", _boot._ADDRESS_KEYS)
        runtime = self._runtime()
        packet = runtime.bootstrap(
            agent_id="agent-a",
            task="x",
            source_ref="runtime",
            continuation_shared_remote_mode="DISABLED",
        )
        self.assertEqual(packet["address"]["prompt_stack_digest"], "prompt-digest")
        self.assertEqual(packet["address"]["frontier_digest"], "frontier-digest")
        self.assertIsNotNone(packet["address"]["operational_basis_digest"])


if __name__ == "__main__":
    unittest.main()

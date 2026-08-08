from __future__ import annotations

import unittest

from athena_mcp.agent_bootstrap import AgentBootstrapRuntime
from athena_mcp.operational_basis import TOOL_NAME, build_operational_basis, install
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES
from athena_mcp import protocol


install()


class OperationalBasisV1Tests(unittest.TestCase):
    def test_basis_is_registered_deterministic_and_surface_derived(self):
        first = build_operational_basis()
        second = build_operational_basis()
        self.assertEqual(first["artifact"], "OPERATIONAL_BASIS_V1")
        self.assertEqual(first["basis_digest"], second["basis_digest"])
        self.assertIn(TOOL_NAME, PROMPT_RUNTIME_TOOL_NAMES)
        self.assertTrue(any(tool.get("name") == TOOL_NAME for tool in protocol.TOOLS))
        descriptor_names = {row["operation"] for row in first["descriptors"]}
        self.assertEqual(descriptor_names, set(PROMPT_RUNTIME_TOOL_NAMES))
        self.assertEqual(first["source_witness"]["registered_count"], len(descriptor_names))

    def test_current_bootstrap_and_prompt_write_effects_remain_distinct(self):
        rows = {row["operation"]: row for row in build_operational_basis()["descriptors"]}
        self.assertEqual(rows["athena_agent_bootstrap"]["capability_class"], "BOOTSTRAP_REFRESH")
        self.assertEqual(rows["athena_agent_bootstrap"]["effect"], "READ_ONLY")
        self.assertTrue(rows["athena_agent_bootstrap"]["auto_select"])
        self.assertEqual(rows["athena_prompt_propose"]["effect"], "REPOSITORY_CANDIDATE_WRITE")
        self.assertFalse(rows["athena_prompt_propose"]["auto_select"])
        self.assertEqual(rows["athena_prompt_promote"]["effect"], "CANONICAL_PROMOTION_GATED_WRITE")
        self.assertEqual(rows["athena_prompt_promote"]["authority_class"], "CANONICAL_PROMOTION_GATED")

    def test_feature_branch_claim_is_not_current_exposure(self):
        basis = build_operational_basis()
        names = {row["operation"] for row in basis["descriptors"]}
        self.assertNotIn("athena_frontier_claim", names)
        self.assertFalse(any(row["capability_class"] == "CLAIM_EXECUTION" for row in basis["descriptors"]))

    def test_new_registered_operation_changes_basis_without_prompt_rewrite(self):
        synthetic = {
            "name": "athena_frontier_observe_future",
            "description": "synthetic future read-only frontier operation",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        }
        before = build_operational_basis()["basis_digest"]
        PROMPT_RUNTIME_TOOLS.append(synthetic)
        PROMPT_RUNTIME_TOOL_NAMES.add(synthetic["name"])
        try:
            basis = build_operational_basis()
            row = {x["operation"]: x for x in basis["descriptors"]}[synthetic["name"]]
            self.assertEqual(row["capability_class"], "FRONTIER_READ_SELECT")
            self.assertEqual(row["effect"], "READ_ONLY")
            self.assertNotEqual(before, basis["basis_digest"])
        finally:
            PROMPT_RUNTIME_TOOL_NAMES.discard(synthetic["name"])
            PROMPT_RUNTIME_TOOLS[:] = [x for x in PROMPT_RUNTIME_TOOLS if x.get("name") != synthetic["name"]]

    def test_unclassified_future_operation_fails_closed(self):
        synthetic = {
            "name": "athena_future_unclassified_write",
            "description": "synthetic write-capable operation with no semantic class",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        }
        PROMPT_RUNTIME_TOOLS.append(synthetic)
        PROMPT_RUNTIME_TOOL_NAMES.add(synthetic["name"])
        try:
            basis = build_operational_basis()
            row = {x["operation"]: x for x in basis["descriptors"]}[synthetic["name"]]
            self.assertEqual(row["capability_class"], "UNCLASSIFIED")
            self.assertEqual(row["authority_class"], "UNCLASSIFIED_HOLD")
            self.assertFalse(row["auto_select"])
            self.assertEqual(basis["status"], "OPERATIONAL_BASIS_HOLD")
        finally:
            PROMPT_RUNTIME_TOOL_NAMES.discard(synthetic["name"])
            PROMPT_RUNTIME_TOOLS[:] = [x for x in PROMPT_RUNTIME_TOOLS if x.get("name") != synthetic["name"]]

    def test_basis_digest_is_bound_into_boot_address_and_refresh_delta(self):
        packet = {
            "prompt": {"git_head": "H", "prompt_stack_digest": "P"},
            "frontier": {"source_head": "S", "frontier_digest": "F"},
            "contract_digest": "C",
            "issue_pressure": {"digest": "I"},
            "execution_surface": {},
            "witnesses": {},
            "laws": [],
        }
        address = AgentBootstrapRuntime._address(packet)
        self.assertIn("operational_basis_digest", address)
        self.assertEqual(address["operational_basis_digest"], packet["execution_surface"]["operational_basis_digest"])
        self.assertTrue(packet["execution_surface"]["capability_descriptors"])
        self.assertIn("operational_basis", packet["witnesses"])

        prior = dict(address)
        current = dict(address)
        current["operational_basis_digest"] = "changed"
        changed = AgentBootstrapRuntime._changed(prior, current)
        self.assertTrue(changed["operational_basis_digest"])
        self.assertFalse(changed["git_head"])
        self.assertFalse(changed["prompt_stack_digest"])

    def test_basis_witness_contains_no_checkout_path_or_credentials(self):
        basis = build_operational_basis()
        witness = basis["source_witness"]
        self.assertEqual(set(witness), {
            "surface", "registered_count", "registered_names_digest", "registered_schema_digest"
        })
        text = str(basis).lower()
        self.assertNotIn("github_token", text)
        self.assertNotIn("private_chain_of_thought", text)


if __name__ == "__main__":
    unittest.main()

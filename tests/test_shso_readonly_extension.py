from __future__ import annotations

import pathlib
import unittest

import athena_mcp
from athena_mcp import protocol
from athena_mcp.aor_development_surface import (
    AOR_DEVELOPMENT_RESOURCES,
    AOR_DEVELOPMENT_RESOURCE_URIS,
    AorDevelopmentSurface,
)
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES, PROMPT_RUNTIME_TOOLS, PromptRuntime
from athena_mcp.shso_readonly import SHSO_READONLY_VERSION
from athena_mcp.shso_readonly_extension import ShsoReadonlyRuntime, install_shso_readonly_extension
from athena_mcp.shso_readonly_protocol import (
    SHSO_READONLY_RESOURCE_URI,
    SHSO_READONLY_TOOL_NAME,
)


def health(phase="RESPONSIVE"):
    return {
        "kind": "HEALTH_ADVISORY",
        "diagnostic_phase": phase,
        "criticality_proven": False,
        "phase_is_heuristic": True,
        "behavioral_gain_proven": False,
        "execution_authority_granted": False,
    }


def ecology(status="CLASSIFIED"):
    return {
        "kind": "ECOLOGY_ADVISORY",
        "status": status,
        "world_truth_proven": False,
        "morphology_mutation_performed": False,
    }


def args(**overrides):
    value = {
        "health_advisory": health(),
        "ecology_advisory": ecology(),
        "ready_build_exists": False,
        "previous_transition_classes": [],
        "verification_barrier_due": False,
        "verification_barrier_mandatory": False,
    }
    value.update(overrides)
    return value


class ShsoReadonlyExtensionTests(unittest.TestCase):
    def test_tool_registered_in_prompt_runtime_and_protocol(self):
        self.assertIn(SHSO_READONLY_TOOL_NAME, PROMPT_RUNTIME_TOOL_NAMES)
        self.assertEqual(
            sum(tool["name"] == SHSO_READONLY_TOOL_NAME for tool in PROMPT_RUNTIME_TOOLS),
            1,
        )
        self.assertEqual(
            sum(tool["name"] == SHSO_READONLY_TOOL_NAME for tool in protocol.TOOLS),
            1,
        )

    def test_resource_registered_in_development_surface(self):
        self.assertIn(SHSO_READONLY_RESOURCE_URI, AOR_DEVELOPMENT_RESOURCE_URIS)
        self.assertEqual(
            sum(resource["uri"] == SHSO_READONLY_RESOURCE_URI for resource in AOR_DEVELOPMENT_RESOURCES),
            1,
        )

    def test_prompt_runtime_dispatches_read_only_tool_without_git(self):
        runtime = PromptRuntime(None)
        value = runtime.call_tool(
            SHSO_READONLY_TOOL_NAME,
            args(
                ready_build_exists=True,
                previous_transition_classes=["VERIFY", "META"],
            ),
        )
        self.assertEqual(value["primary_pressure"], "BUILD_PIVOT_ADVISORY")
        self.assertFalse(value["execution_authority_granted"])
        self.assertFalse(value["scheduler_mutation_performed"])

    def test_development_surface_resource_wrapper_is_readable_without_constructor(self):
        surface = object.__new__(AorDevelopmentSurface)
        value = surface.read_resource(SHSO_READONLY_RESOURCE_URI)
        self.assertEqual(value["version"], SHSO_READONLY_VERSION)
        self.assertEqual(value["standing"], "READ_ONLY_RUNTIME_EXTENSION_CANDIDATE")
        self.assertFalse(value["behavioral_gain_proven"])

    def test_direct_runtime_resource_and_benchmark(self):
        runtime = ShsoReadonlyRuntime()
        value = runtime.read_resource(SHSO_READONLY_RESOURCE_URI)
        self.assertEqual(value["private_semantic_contract"], "ATHENA.SHSO.READONLY.BRIDGE.V1")
        self.assertTrue(all(runtime.benchmark().values()))

    def test_installer_is_idempotent(self):
        before_tools = len([t for t in protocol.TOOLS if t["name"] == SHSO_READONLY_TOOL_NAME])
        before_resources = len([r for r in AOR_DEVELOPMENT_RESOURCES if r["uri"] == SHSO_READONLY_RESOURCE_URI])
        install_shso_readonly_extension()
        install_shso_readonly_extension()
        after_tools = len([t for t in protocol.TOOLS if t["name"] == SHSO_READONLY_TOOL_NAME])
        after_resources = len([r for r in AOR_DEVELOPMENT_RESOURCES if r["uri"] == SHSO_READONLY_RESOURCE_URI])
        self.assertEqual(before_tools, after_tools)
        self.assertEqual(before_resources, after_resources)
        self.assertEqual(after_tools, 1)
        self.assertEqual(after_resources, 1)

    def test_init_installs_shso_before_final_v15_identity(self):
        source = pathlib.Path(athena_mcp.__file__).read_text(encoding="utf-8")
        shso_pos = source.index("install_shso_readonly_extension()")
        v15_pos = source.index("_install_release_v15(globals())")
        self.assertLess(shso_pos, v15_pos)

    def test_manifest_extension_code_is_additive(self):
        source = pathlib.Path(athena_mcp.__file__).with_name("shso_readonly_extension.py").read_text(encoding="utf-8")
        self.assertIn('value["shso_readonly"] = shso_manifest()', source)
        self.assertIn('marker = "SHSO_READONLY_RUNTIME_V1"', source)
        self.assertNotIn("value['artifact'] =", source)
        self.assertNotIn('value["artifact"] =', source)

    def test_tool_descriptor_is_read_only_and_closed(self):
        tool = next(t for t in protocol.TOOLS if t["name"] == SHSO_READONLY_TOOL_NAME)
        self.assertFalse(tool["inputSchema"]["additionalProperties"])
        self.assertIn("cannot dispatch", tool["description"])
        self.assertIn("cannot", tool["description"])


if __name__ == "__main__":
    unittest.main()

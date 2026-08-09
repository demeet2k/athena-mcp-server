from __future__ import annotations

"""Additive CUTOVER_HOLD registration over the canonical DEPLOYMENT.2 organ."""

import json
from typing import Any

from .deployment_cutover import (
    assess_single_writer_quiescence,
    benchmark as cutover_benchmark,
    compile_cutover_hold,
    manifest as cutover_manifest,
    verify_cutover_hold,
)
from .deployment_cutover_protocol import (
    DEPLOYMENT_CUTOVER_PROMPT,
    DEPLOYMENT_CUTOVER_RESOURCES,
    DEPLOYMENT_CUTOVER_RESOURCE_URIS,
    DEPLOYMENT_CUTOVER_TOOLS,
    DEPLOYMENT_CUTOVER_TOOL_NAMES,
)


class DeploymentCutoverRuntime:
    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "athena_deployment_assess_quiescence":
            return assess_single_writer_quiescence(
                arguments["observation"],
                expected_current_image_ref=arguments["expected_current_image_ref"],
                expected_state_snapshot_ref=arguments["expected_state_snapshot_ref"],
                expected_state_snapshot_digest=arguments["expected_state_snapshot_digest"],
            )
        if name == "athena_deployment_cutover_hold":
            return compile_cutover_hold(
                arguments["plan"],
                arguments["canary_witness"],
                arguments["quiescence_observation"],
                cutover_authority_ref=arguments.get("cutover_authority_ref"),
            )
        if name == "athena_deployment_verify_cutover_hold":
            return verify_cutover_hold(
                arguments["packet"],
                expected_plan_digest=arguments["expected_plan_digest"],
                expected_image_ref=arguments["expected_image_ref"],
                expected_source_head=arguments["expected_source_head"],
                expected_current_image_ref=arguments["expected_current_image_ref"],
                expected_state_snapshot_ref=arguments["expected_state_snapshot_ref"],
                expected_state_snapshot_digest=arguments["expected_state_snapshot_digest"],
                expected_canary_witness_digest=arguments["expected_canary_witness_digest"],
                expected_quiescence_assessment_digest=arguments[
                    "expected_quiescence_assessment_digest"
                ],
                expected_cutover_authority_ref=arguments["expected_cutover_authority_ref"],
            )
        raise KeyError(name)

    def read_resource(self, uri: str) -> dict[str, Any]:
        if uri == "athena://deployment/cutover-hold":
            return cutover_manifest()
        raise KeyError(uri)

    def benchmark(self) -> dict[str, Any]:
        return cutover_benchmark()

    def prompt(self, objective: str, environment: str, actor: str) -> str:
        return f"""ATHENA DEPLOYMENT CUTOVER_HOLD V1
ACTOR={actor}
ENVIRONMENT={environment}
OBJECTIVE={objective}
1 HYDRATE athena://deployment, /rollout, /evidence, /cutover-hold, and the exact current runtime manifest.
2 REQUIRE ATHENA.ACTIVATION.PLAN.2 status PLAN_ONLY with a valid plan digest, exact target image/source, expected-current-image CAS, and witnessed snapshot coordinates.
3 VERIFY the supplied ATHENA.ISOLATED.CANARY.WITNESS.1 and its embedded assessment/witness digests. PROMOTE means bounded canary PASS only.
4 ASSESS ATHENA.SINGLE.WRITER.QUIESCENCE.OBSERVATION.1. Require zero active writers, previous writer stopped, candidate not started, active write fence, post-fence verified snapshot, and exact CAS coordinates.
5 TREAT missing current-image observation as HOLD, malformed observation as HOLD, and a mismatch as HOLD_STALE_ACTIVATION_BASE. Never coerce UNKNOWN to PASS.
6 BIND cutover_authority_ref as an unverified reference. AUTHORITY_REFERENCE_BOUND != AUTHORITY_VERIFIED.
7 COMPILE ATHENA.CUTOVER.HOLD.1 with all execution, cluster, state-mutation, secret, and traffic authority bits false.
8 REPLAY packet_digest and every expected plan/image/source/current-image/snapshot/canary/quiescence/authority-reference binding.
9 STOP AT CUTOVER_HOLD. CUTOVER_HOLD != SINGLE_WRITER_CUTOVER != ACTIVATION_RECEIPT.
10 A separately authorized effectful executor must freshly re-observe CAS and quiescence, independently validate authority, and issue its own activation receipt.
"""


def install_deployment_cutover_extension() -> None:
    from . import protocol as protocol
    from .aor_development_surface import (
        AOR_DEVELOPMENT_RESOURCES,
        AOR_DEVELOPMENT_RESOURCE_URIS,
        AorDevelopmentSurface,
    )
    from .prompt_runtime import (
        PROMPT_RUNTIME_TOOLS,
        PROMPT_RUNTIME_TOOL_NAMES,
        PromptRuntime,
    )

    if getattr(PromptRuntime, "_athena_deployment_cutover_hold_v1_registered", False):
        return

    for tool in DEPLOYMENT_CUTOVER_TOOLS:
        if tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
            PROMPT_RUNTIME_TOOLS.append(tool)
            PROMPT_RUNTIME_TOOL_NAMES.add(tool["name"])
        if not any(existing["name"] == tool["name"] for existing in protocol.TOOLS):
            protocol.TOOLS.append(tool)

    known_resources = {resource["uri"] for resource in AOR_DEVELOPMENT_RESOURCES}
    for resource in DEPLOYMENT_CUTOVER_RESOURCES:
        if resource["uri"] not in known_resources:
            AOR_DEVELOPMENT_RESOURCES.append(resource)
            known_resources.add(resource["uri"])
        AOR_DEVELOPMENT_RESOURCE_URIS.add(resource["uri"])

    if not any(
        prompt.get("name") == DEPLOYMENT_CUTOVER_PROMPT["name"]
        for prompt in protocol.PROMPTS
    ):
        protocol.PROMPTS.append(DEPLOYMENT_CUTOVER_PROMPT)

    previous_prompt_call = PromptRuntime.call_tool

    def prompt_call_with_cutover_hold(self, name, arguments):
        if name in DEPLOYMENT_CUTOVER_TOOL_NAMES:
            runtime = getattr(self, "_athena_deployment_cutover_runtime_v1", None)
            if runtime is None:
                runtime = DeploymentCutoverRuntime()
                self._athena_deployment_cutover_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return previous_prompt_call(self, name, arguments)

    PromptRuntime.call_tool = prompt_call_with_cutover_hold

    previous_resource_read = AorDevelopmentSurface.read_resource

    def resource_read_with_cutover_hold(self, uri):
        if uri in DEPLOYMENT_CUTOVER_RESOURCE_URIS:
            runtime = getattr(self, "_athena_deployment_cutover_runtime_v1", None)
            if runtime is None:
                runtime = DeploymentCutoverRuntime()
                self._athena_deployment_cutover_runtime_v1 = runtime
            return runtime.read_resource(uri)
        return previous_resource_read(self, uri)

    AorDevelopmentSurface.read_resource = resource_read_with_cutover_hold

    previous_benchmark = AorDevelopmentSurface.benchmark

    def benchmark_with_cutover_hold(self):
        result = previous_benchmark(self)
        result.update(DeploymentCutoverRuntime().benchmark())
        return result

    AorDevelopmentSurface.benchmark = benchmark_with_cutover_hold

    from . import dispatch

    previous_handle = dispatch.handle

    def handle_with_cutover_hold(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        if (
            method == "prompts/get"
            and params.get("name") == DEPLOYMENT_CUTOVER_PROMPT["name"]
        ):
            args = params.get("arguments") or {}
            runtime = DeploymentCutoverRuntime()
            return server.result(
                mid,
                {
                    "description": DEPLOYMENT_CUTOVER_PROMPT["description"],
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": runtime.prompt(
                                    str(args.get("objective") or ""),
                                    str(args.get("environment") or "production"),
                                    str(args.get("actor") or "ATHENA"),
                                ),
                            },
                        }
                    ],
                },
            )
        result = previous_handle(server, message)
        if not result or "result" not in result:
            return result
        if method == "resources/read" and params.get("uri") == "athena://manifest":
            contents = result["result"].get("contents") or []
            if contents:
                value = json.loads(contents[0]["text"])
                value["deployment_cutover_hold"] = cutover_manifest()
                extensions = list(value.get("extensions") or [])
                marker = "DEPLOYMENT_CUTOVER_HOLD_V1"
                if marker not in extensions:
                    extensions.append(marker)
                value["extensions"] = extensions
                contents[0]["text"] = json.dumps(
                    value, ensure_ascii=False, sort_keys=True
                )
        return result

    dispatch.handle = handle_with_cutover_hold
    PromptRuntime._athena_deployment_cutover_hold_v1_registered = True


__all__ = ["DeploymentCutoverRuntime", "install_deployment_cutover_extension"]

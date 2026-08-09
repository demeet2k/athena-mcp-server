from __future__ import annotations

"""Additive DEPLOYMENT.2 registration for the current canonical runtime.

The installer composes through existing PromptRuntime and AorDevelopmentSurface
seams.  It does not subclass, replace, or nest athena_mcp.server.Server.
"""

import json
from typing import Any

from .deployment import (
    HTTP_ADAPTER_VERSION,
    activation_plan,
    assess_canary,
    benchmark as deployment_benchmark,
    manifest as deployment_manifest,
    validate_bundle,
    verify_activation_receipt,
)
from .deployment_protocol import (
    DEPLOYMENT_PROMPT,
    DEPLOYMENT_RESOURCES,
    DEPLOYMENT_RESOURCE_URIS,
    DEPLOYMENT_TOOLS,
    DEPLOYMENT_TOOL_NAMES,
)


class DeploymentRuntime:
    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "athena_deployment_manifest":
            return deployment_manifest()
        if name == "athena_deployment_validate":
            return validate_bundle(arguments["bundle"])
        if name == "athena_deployment_activation_plan":
            return activation_plan(
                arguments["image_ref"],
                source_head=arguments["source_head"],
                state_snapshot_ref=arguments["state_snapshot_ref"],
                state_snapshot_digest=arguments["state_snapshot_digest"],
                token_secret_ref=arguments["token_secret_ref"],
                release_attestation_ref=arguments["release_attestation_ref"],
                sbom_ref=arguments["sbom_ref"],
                expected_current_image_ref=arguments.get("expected_current_image_ref"),
                replicas=arguments.get("replicas", 1),
                canary_percent=arguments.get("canary_percent", 10),
                actor=arguments.get("actor", "agent"),
            )
        if name == "athena_deployment_assess_canary":
            return assess_canary(
                arguments["baseline"],
                arguments["canary"],
                arguments.get("thresholds"),
            )
        if name == "athena_deployment_verify_receipt":
            return verify_activation_receipt(
                arguments["receipt"],
                expected_plan_digest=arguments["expected_plan_digest"],
                expected_image_ref=arguments["expected_image_ref"],
                expected_source_head=arguments["expected_source_head"],
                expected_state_snapshot_ref=arguments["expected_state_snapshot_ref"],
                expected_state_snapshot_digest=arguments["expected_state_snapshot_digest"],
            )
        raise KeyError(name)

    def read_resource(self, uri: str) -> dict[str, Any]:
        value = deployment_manifest()
        if uri == "athena://deployment":
            return value
        if uri == "athena://deployment/security":
            return {
                "version": value["version"],
                "state": value["state"],
                "runtime": value["runtime"],
                "security": value["security"],
                "supply_chain": value["supply_chain"],
                "authority_boundary": value["authority_boundary"],
            }
        if uri == "athena://deployment/rollout":
            return {
                "version": value["version"],
                "state": value["state"],
                "persistence": value["persistence"],
                "rollout": value["rollout"],
                "receipt": value["receipt"],
                "authority_boundary": value["authority_boundary"],
            }
        if uri == "athena://deployment/evidence":
            return {
                "version": value["version"],
                "state": value["state"],
                "supply_chain": value["supply_chain"],
                "receipt": value["receipt"],
                "authority_boundary": value["authority_boundary"],
                "law": "ATTESTATION != ACTIVATION; RECEIPT_BINDING_PASS != INDEPENDENT_WORLD_OBSERVATION",
            }
        raise KeyError(uri)

    def benchmark(self) -> dict[str, Any]:
        return deployment_benchmark()

    def prompt(self, objective: str, environment: str, actor: str) -> str:
        return f"""ATHENA DEPLOYMENT.2 ACTIVATION CONTROL
ACTOR={actor}
ENVIRONMENT={environment}
OBJECTIVE={objective}
1 HYDRATE athena://deployment, /security, /rollout, /evidence and the exact current runtime manifest.
2 BIND source_head to the image attestation source head. A tag, digest, build, or attestation alone is not activation.
3 VERIFY the SBOM, release attestation, state snapshot reference, and state snapshot SHA-256 before planning cutover.
4 COMPILE PLAN_ONLY with expected-current-image CAS. PLAN_ONLY != EXECUTION != CUTOVER AUTHORITY.
5 RUN an isolated canary with zero production writes and an independent database or snapshot clone.
6 REQUIRE readiness, schema currency, deterministic replay, bounded error/latency/restart deltas, >=30 samples, and >=60 observed seconds.
7 HOLD on missing observations; ROLLBACK on failed or thin evidence; PROMOTE only means the bounded canary policy passed.
8 REQUIRE explicit cutover_authority_ref and single-writer quiescence before changing production ownership.
9 CUT OVER with exactly one writable SQLite owner; then verify RPC, schema, replay, latency, errors, and restarts.
10 RETURN ATHENA.ACTIVATION.RECEIPT.1 bound to plan digest, image digest, source head, snapshot, executor receipt, observations, and authority.
11 REPLAY the receipt bindings. Never represent receipt-shape verification as an independent cluster observation.
12 ON ANY MISMATCH restore the previous exact image and witnessed pre-cutover snapshot; never auto-rewrite state.
"""


def install_deployment_extension() -> None:
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

    if getattr(PromptRuntime, "_athena_deployment_v2_registered", False):
        return

    for tool in DEPLOYMENT_TOOLS:
        if tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
            PROMPT_RUNTIME_TOOLS.append(tool)
            PROMPT_RUNTIME_TOOL_NAMES.add(tool["name"])
        if not any(existing["name"] == tool["name"] for existing in protocol.TOOLS):
            protocol.TOOLS.append(tool)

    known_resources = {resource["uri"] for resource in AOR_DEVELOPMENT_RESOURCES}
    for resource in DEPLOYMENT_RESOURCES:
        if resource["uri"] not in known_resources:
            AOR_DEVELOPMENT_RESOURCES.append(resource)
            known_resources.add(resource["uri"])
        AOR_DEVELOPMENT_RESOURCE_URIS.add(resource["uri"])

    if not any(prompt.get("name") == DEPLOYMENT_PROMPT["name"] for prompt in protocol.PROMPTS):
        protocol.PROMPTS.append(DEPLOYMENT_PROMPT)

    previous_prompt_call = PromptRuntime.call_tool

    def prompt_call_with_deployment(self, name, arguments):
        if name in DEPLOYMENT_TOOL_NAMES:
            runtime = getattr(self, "_athena_deployment_runtime_v2", None)
            if runtime is None:
                runtime = DeploymentRuntime()
                self._athena_deployment_runtime_v2 = runtime
            return runtime.call_tool(name, arguments)
        return previous_prompt_call(self, name, arguments)

    PromptRuntime.call_tool = prompt_call_with_deployment

    previous_resource_read = AorDevelopmentSurface.read_resource

    def resource_read_with_deployment(self, uri):
        if uri in DEPLOYMENT_RESOURCE_URIS:
            runtime = getattr(self, "_athena_deployment_runtime_v2", None)
            if runtime is None:
                runtime = DeploymentRuntime()
                self._athena_deployment_runtime_v2 = runtime
            return runtime.read_resource(uri)
        return previous_resource_read(self, uri)

    AorDevelopmentSurface.read_resource = resource_read_with_deployment

    previous_benchmark = AorDevelopmentSurface.benchmark

    def benchmark_with_deployment(self):
        result = previous_benchmark(self)
        result.update(DeploymentRuntime().benchmark())
        return result

    AorDevelopmentSurface.benchmark = benchmark_with_deployment

    # Dispatch is imported only after the registry objects above are updated, so
    # its module-level aliases observe the same mutable tool/resource collections.
    from . import dispatch

    previous_handle = dispatch.handle

    def handle_with_deployment(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        if method == "prompts/get" and params.get("name") == DEPLOYMENT_PROMPT["name"]:
            args = params.get("arguments") or {}
            runtime = DeploymentRuntime()
            return server.result(
                mid,
                {
                    "description": DEPLOYMENT_PROMPT["description"],
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
        if method == "initialize":
            info = dict(result["result"].get("serverInfo") or {})
            dep = deployment_manifest()
            info["deployment"] = {
                "version": dep["version"],
                "state": dep["state"],
                "adapter": HTTP_ADAPTER_VERSION,
                "manifestDigest": dep["manifest_digest"],
            }
            result["result"]["serverInfo"] = info
        elif method == "resources/read" and params.get("uri") == "athena://manifest":
            contents = result["result"].get("contents") or []
            if contents:
                value = json.loads(contents[0]["text"])
                value["deployment"] = deployment_manifest()
                extensions = list(value.get("extensions") or [])
                marker = "DEPLOYMENT2_SOURCE_BOUND_CAS_ACTIVATION"
                if marker not in extensions:
                    extensions.append(marker)
                value["extensions"] = extensions
                contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
        return result

    dispatch.handle = handle_with_deployment
    PromptRuntime._athena_deployment_v2_registered = True


__all__ = ["DeploymentRuntime", "install_deployment_extension"]

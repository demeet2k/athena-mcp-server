from __future__ import annotations

"""Canonical ATHENA runtime with the DEPLOYMENT.1 organ composed at the root.

The existing HubServer remains import-compatible. This module is the package
entrypoint for release 3.1+ and extends, rather than nests, that canonical
runtime. Tool/resource discovery proves only surface availability; deployment
execution still requires an external witnessed controller.
"""

import argparse
import json
import os
import sys
from typing import Any

from .command_hub import KC144CommandHub
from .deployment import (
    HTTP_ADAPTER_VERSION,
    activation_plan,
    assess_canary,
    benchmark as deployment_benchmark,
    manifest as deployment_manifest,
    validate_bundle,
)
from .deployment_protocol import (
    DEPLOYMENT_PROMPT,
    DEPLOYMENT_RESOURCES,
    DEPLOYMENT_TOOLS,
)
from .hub_server import HubServer
from .protocol import TOOLS

_DEPLOYMENT_URIS = {item["uri"] for item in DEPLOYMENT_RESOURCES}


def _deployment_resource(uri: str) -> dict[str, Any]:
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
            "authority_boundary": value["authority_boundary"],
        }
    raise KeyError(uri)


def _deployment_prompt(objective: str, environment: str, actor: str) -> str:
    return f"""ATHENA DEPLOYMENT.1 ACTIVATION CONTROL
ACTOR={actor}
ENVIRONMENT={environment}
OBJECTIVE={objective}
1 HYDRATE athena://deployment, athena://deployment/security, athena://deployment/rollout and athena://system/release.
2 REQUIRE an exact OCI digest; a mutable tag, release name, or successful build is not activation evidence.
3 VALIDATE one ATHENA.DEPLOYMENT.BUNDLE.1 with external secret ref, explicit backup witness, SINGLE_WRITER state, and insecure HTTP disabled.
4 BUILD an activation plan only. PLAN_ONLY != infrastructure mutation != traffic cutover.
5 CANARY against an isolated fresh or snapshot-cloned database. Production writes to the canary are forbidden.
6 MEASURE readiness, schema currency, replay integrity, error rate, p95 latency, and restart count from external observations.
7 PROMOTE only when every canary gate passes and a separate cutover authority exists.
8 CUT OVER with exactly one active SQLite writer. Stop the old writer before the new writer receives production writes.
9 ROLLBACK on readiness, schema, replay, error-budget, latency, or restart regression; restore the previous digest and witnessed snapshot.
10 RETURN image digest, state snapshot, secret ref, observations, decision, and external execution receipt. Never claim deployment from this prompt alone.
"""


class DeploymentHubServer(HubServer):
    """Single canonical runtime root with the typed deployment organ."""

    def __init__(self, db: str, git_root: str | None = None) -> None:
        super().__init__(db, git_root)
        # The deployment surface is instance-scoped. Importing this module must
        # not mutate the base HubServer's global tool, prompt, or organ registry.
        self.command_hub = KC144CommandHub(
            tool_names=self._all_tool_names,
            runtime_probe=self._runtime_probe,
            resource_uris=self._all_resource_uris,
        )

    @staticmethod
    def _all_tool_names() -> list[str]:
        return sorted(
            {
                item["name"]
                for item in (*tuple(TOOLS), *tuple(DEPLOYMENT_TOOLS))
            }
        )

    def _all_resource_uris(self) -> list[str]:
        return sorted(
            set((*super()._all_resource_uris(), *tuple(_DEPLOYMENT_URIS)))
        )

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "athena_deployment_manifest":
            return deployment_manifest()
        if name == "athena_deployment_validate":
            return validate_bundle(arguments["bundle"])
        if name == "athena_deployment_activation_plan":
            return activation_plan(
                arguments["image_ref"],
                replicas=arguments.get("replicas", 1),
                canary_percent=arguments.get("canary_percent", 10),
                state_snapshot_ref=arguments["state_snapshot_ref"],
                token_secret_ref=arguments["token_secret_ref"],
                actor=arguments.get("actor", "agent"),
            )
        if name == "athena_deployment_assess_canary":
            return assess_canary(
                arguments["baseline"],
                arguments["canary"],
                thresholds=arguments.get("thresholds"),
            )

        if name in {
            "athena_kc144_hub_status",
            "athena_kc144_hub_manifest",
            "athena_kc144_hub_readiness",
            "athena_kc144_hub_validate",
        }:
            result = super().call_tool(name, arguments)
            result["deployment"] = deployment_manifest()
            return result
        if name == "athena_benchmark":
            result = super().call_tool(name, arguments)
            result["deployment"] = deployment_benchmark()
            return result
        return super().call_tool(name, arguments)

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")

        if method == "initialize":
            result = super().handle(message)
            if result and "result" in result:
                info = dict(result["result"].get("serverInfo") or {})
                dep = deployment_manifest()
                info.update(
                    {
                        "httpAdapter": HTTP_ADAPTER_VERSION,
                        "deployment": {
                            "version": dep["version"],
                            "state": dep["state"],
                            "manifestDigest": dep["manifest_digest"],
                        },
                    }
                )
                result["result"]["serverInfo"] = info
            return result

        if method == "tools/list":
            result = super().handle(message)
            if not result or "result" not in result:
                return result
            tools = list(result["result"].get("tools") or [])
            seen = {item["name"] for item in tools}
            tools.extend(
                item for item in DEPLOYMENT_TOOLS if item["name"] not in seen
            )
            result["result"]["tools"] = sorted(
                tools, key=lambda item: item["name"]
            )
            return result

        if method == "resources/list":
            result = super().handle(message)
            if not result or "result" not in result:
                return result
            resources = list(result["result"].get("resources") or [])
            seen = {item["uri"] for item in resources}
            resources.extend(
                item for item in DEPLOYMENT_RESOURCES if item["uri"] not in seen
            )
            result["result"]["resources"] = sorted(
                resources, key=lambda item: item["uri"]
            )
            return result

        if method == "prompts/list":
            result = super().handle(message)
            if not result or "result" not in result:
                return result
            prompts = list(result["result"].get("prompts") or [])
            if DEPLOYMENT_PROMPT["name"] not in {
                item["name"] for item in prompts
            }:
                prompts.append(DEPLOYMENT_PROMPT)
            result["result"]["prompts"] = sorted(
                prompts, key=lambda item: item["name"]
            )
            return result

        if method == "resources/read" and params.get("uri") in _DEPLOYMENT_URIS:
            uri = params["uri"]
            return self.result(
                mid,
                {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(
                                _deployment_resource(uri),
                                ensure_ascii=False,
                                sort_keys=True,
                            ),
                        }
                    ]
                },
            )

        if method == "resources/read" and params.get("uri") == "athena://manifest":
            result = super().handle(message)
            if result and "result" in result:
                content = result["result"]["contents"][0]
                value = json.loads(content["text"])
                layers = list(value.get("layers") or [])
                layer = "DEPLOYMENT1_DIGEST_PINNED_ACTIVATION"
                if layer not in layers:
                    layers.append(layer)
                value["layers"] = layers
                value["deployment"] = deployment_manifest()
                content["text"] = json.dumps(
                    value, ensure_ascii=False, sort_keys=True
                )
            return result

        if method == "prompts/get" and params.get("name") == DEPLOYMENT_PROMPT["name"]:
            args = params.get("arguments") or {}
            return self.result(
                mid,
                {
                    "description": DEPLOYMENT_PROMPT["description"],
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": _deployment_prompt(
                                    args.get("objective", ""),
                                    args.get("environment", "production"),
                                    args.get("actor", "ATHENA"),
                                ),
                            },
                        }
                    ],
                },
            )

        return super().handle(message)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db", default=os.getenv("ATHENA_DB", "./state/athena.db")
    )
    parser.add_argument("--git-root", default=os.getenv("ATHENA_GIT_ROOT"))
    args = parser.parse_args(argv)
    server = DeploymentHubServer(args.db, args.git_root)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            response = server.handle(json.loads(raw))
        except Exception as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {exc}",
                },
            }
        if response is not None:
            sys.stdout.write(
                json.dumps(
                    response,
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
                + "\n"
            )
            sys.stdout.flush()


if __name__ == "__main__":
    main()

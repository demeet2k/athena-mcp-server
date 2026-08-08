from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from .server import Server as UnifiedServer
from .protocol import TOOLS, PROMPTS
from .aor_development_surface import AOR_DEVELOPMENT_RESOURCES
from .command_hub import KC144CommandHub
from .command_hub_protocol import HUB_PROMPT, HUB_RESOURCES, HUB_TOOLS

_existing_tools = {item["name"] for item in TOOLS}
for tool in HUB_TOOLS:
    if tool["name"] not in _existing_tools:
        TOOLS.append(tool)
        _existing_tools.add(tool["name"])

_existing_prompts = {item["name"] for item in PROMPTS}
if HUB_PROMPT["name"] not in _existing_prompts:
    PROMPTS.append(HUB_PROMPT)


class HubServer(UnifiedServer):
    """Authoritative composition surface for the current unified runtime plus KC144 hub."""

    def __init__(self, db: str, git_root: str | None = None) -> None:
        super().__init__(db, git_root)
        self.command_hub = KC144CommandHub(
            tool_names=lambda: [item["name"] for item in TOOLS],
            runtime_probe=self._runtime_probe,
            resource_uris=[item["uri"] for item in AOR_DEVELOPMENT_RESOURCES + HUB_RESOURCES],
        )

    def _runtime_probe(self) -> dict[str, Any]:
        try:
            base = super().call_tool("athena_benchmark", {})
        except Exception as exc:  # status surfaces failure; it never invents a pass.
            return {"state": "PROBE_FAILED", "error_type": type(exc).__name__}
        return {"state": "PROBED", "benchmark": base}

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        hub = self.command_hub
        if name == "athena_kc144_hub_status":
            return hub.status()
        if name == "athena_kc144_hub_manifest":
            return hub.manifest(arguments.get("include_edges", False), arguments.get("include_dynamic_inventory", True))
        if name == "athena_kc144_hub_seat":
            return hub.seat(arguments["gid"], arguments.get("include_fibres", True))
        if name == "athena_kc144_hub_inventory":
            return hub.inventory(arguments.get("kind"), arguments.get("state"), arguments.get("gid"), arguments.get("query"), arguments.get("limit", 1000))
        if name == "athena_kc144_hub_graph":
            return hub.graph(arguments["name"], arguments.get("include_edges", True))
        if name == "athena_kc144_hub_route":
            return hub.route(arguments["src"], arguments["dst"], arguments.get("graphs") or ["physical_grid"])
        if name == "athena_kc144_hub_datasets":
            return hub.datasets(arguments.get("kind"), arguments.get("state"))
        if name == "athena_kc144_hub_communication":
            return hub.communication()
        if name == "athena_kc144_hub_readiness":
            return hub.readiness()
        if name == "athena_kc144_hub_validate":
            return hub.validate()
        if name == "athena_benchmark":
            result = super().call_tool(name, arguments)
            result["kc144_command_hub"] = hub.status()
            return result
        return super().call_tool(name, arguments)

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        from .hub_dispatch import handle
        return handle(self, message)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=os.getenv("ATHENA_DB", "./state/athena.db"))
    parser.add_argument("--git-root", default=os.getenv("ATHENA_GIT_ROOT"))
    args = parser.parse_args(argv)
    server = HubServer(args.db, args.git_root)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
            response = server.handle(message)
        except Exception as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":"), ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

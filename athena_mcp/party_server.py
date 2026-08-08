from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Mapping

from .party_protocol import PARTY_RESOURCE, PARTY_TOOL_NAMES, PARTY_TOOLS
from .party_runtime import PartyRuntime
from .server import Server
from .validate import validate


class PartyServer(Server):
    """Thin default-server extension for durable agent parties.

    Existing Server behavior is delegated unchanged. Only party tool/resource
    names are intercepted, minimizing the merge surface against the active
    orchestration runtime.
    """

    def __init__(self, db: str, git_root: str | None = None):
        super().__init__(db, git_root)
        self.party = PartyRuntime(self)

    def _party_call(self, name: str, a: Mapping[str, Any]) -> Any:
        if name == "athena_party_form":
            return self.party.form(
                a["leader"],
                a["goals"],
                a["channels"],
                a.get("capabilities"),
                a.get("name"),
                a.get("policy"),
            )
        if name == "athena_party_join":
            return self.party.join(
                a["party_id"],
                a["agent"],
                a.get("capabilities"),
                a.get("role", "MEMBER"),
            )
        if name == "athena_party_message":
            return self.party.message(
                a["party_id"],
                a["author"],
                a["channel"],
                a["target"],
                a["kind"],
                a["body"],
                a.get("refs"),
            )
        if name == "athena_party_steer":
            return self.party.steer(
                a["party_id"],
                a.get("actor", "agent"),
                a.get("persist", True),
            )
        if name == "athena_party_credit":
            return self.party.credit(
                a["party_id"],
                a["cycle_id"],
                a["outcomes"],
                a["xp_receipts"],
                a.get("actor", "agent"),
            )
        if name == "athena_party_state":
            return self.party.state(a["party_id"])
        if name == "athena_party_list":
            return self.party.list(a.get("status"), a.get("limit", 100))
        raise KeyError(name)

    def handle(self, m: Mapping[str, Any]):
        method = m.get("method")
        params = m.get("params") or {}
        mid = m.get("id")

        if method == "tools/list":
            base = super().handle(dict(m))
            tools = list((base or {}).get("result", {}).get("tools") or [])
            known = {tool["name"] for tool in tools}
            tools.extend(tool for tool in PARTY_TOOLS if tool["name"] not in known)
            return self.result(mid, {"tools": sorted(tools, key=lambda x: x["name"])})

        if method == "tools/call" and params.get("name") in PARTY_TOOL_NAMES:
            name = str(params["name"])
            args = params.get("arguments") or {}
            if not self.rate.allow(name):
                return self.result(
                    mid,
                    {
                        "content": [{"type": "text", "text": "Rate limit exceeded; retry later."}],
                        "isError": True,
                    },
                )
            started = time.perf_counter()
            try:
                td = next(tool for tool in PARTY_TOOLS if tool["name"] == name)
                validate(td["inputSchema"], args)
                value = self._party_call(name, args)
                try:
                    self.collective_learning.record_runtime_usage(
                        name, time.perf_counter() - started, "OK"
                    )
                except Exception:
                    pass
                return self.result(
                    mid,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(value, ensure_ascii=False, sort_keys=True),
                            }
                        ],
                        "structuredContent": value,
                        "isError": False,
                    },
                )
            except (ValueError, KeyError) as exc:
                try:
                    self.collective_learning.record_runtime_usage(
                        name, time.perf_counter() - started, "REJECTED"
                    )
                except Exception:
                    pass
                return self.result(
                    mid,
                    {
                        "content": [{"type": "text", "text": str(exc)}],
                        "isError": True,
                    },
                )
            except Exception as exc:
                try:
                    self.collective_learning.record_runtime_usage(
                        name, time.perf_counter() - started, "ERROR"
                    )
                except Exception:
                    pass
                print(f"party tool error {name}: {exc}", file=sys.stderr)
                return self.error(mid, -32603, "Internal error")

        if method == "resources/list":
            base = super().handle(dict(m))
            resources = list((base or {}).get("result", {}).get("resources") or [])
            if PARTY_RESOURCE["uri"] not in {r["uri"] for r in resources}:
                resources.append(PARTY_RESOURCE)
            return self.result(mid, {"resources": resources})

        if method == "resources/read" and params.get("uri") == PARTY_RESOURCE["uri"]:
            value = {
                "runtime": self.party.benchmark(),
                "parties": self.party.list(limit=100),
                "laws": {
                    "presence_xp": 0,
                    "party_bonus_rate_max": 0.05,
                    "credit": "witnessed contribution only",
                    "authority": "party coordination/bonus ledger is not canonical truth authority",
                },
            }
            return self.result(
                mid,
                {
                    "contents": [
                        {
                            "uri": PARTY_RESOURCE["uri"],
                            "mimeType": "application/json",
                            "text": json.dumps(value, ensure_ascii=False, sort_keys=True),
                        }
                    ]
                },
            )

        return super().handle(dict(m))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=os.getenv("ATHENA_DB", "./state/athena.db"))
    parser.add_argument("--git-root", default=os.getenv("ATHENA_GIT_ROOT"))
    args = parser.parse_args(argv)
    srv = PartyServer(args.db, args.git_root)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
            result = srv.handle(message)
        except Exception as exc:
            result = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
        if result is not None:
            sys.stdout.write(json.dumps(result, separators=(",", ":"), ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

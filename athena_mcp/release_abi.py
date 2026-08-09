from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

ABI_SCHEMA="ATHENA.MCP.PUBLIC_ABI.1"
ABI_ALGORITHM="SHA256_CANONICAL_JSON_V1"


def _canonical(value: Any):
    if isinstance(value,dict):
        return {str(k):_canonical(value[k]) for k in sorted(value,key=str)}
    if isinstance(value,list):
        return [_canonical(v) for v in value]
    if isinstance(value,tuple):
        return [_canonical(v) for v in value]
    if isinstance(value,(str,int,float,bool)) or value is None:
        return value
    raise TypeError(f"unsupported ABI value type: {type(value).__name__}")


def _json_bytes(value: Any) -> bytes:
    return json.dumps(_canonical(value),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest().upper()


def _sort_surface(rows: list[dict], key: str) -> list[dict]:
    return sorted((copy.deepcopy(row) for row in rows),key=lambda row:(str(row.get(key,"")),_sha(row)))


def _rpc_list(server,method: str,key: str) -> list[dict]:
    response=server.handle({"jsonrpc":"2.0","id":1,"method":method,"params":{}})
    if response.get("error"):
        raise RuntimeError(f"{method} failed: {response['error']}")
    result=response.get("result") or {}
    rows=result.get(key)
    if not isinstance(rows,list):
        raise RuntimeError(f"{method} did not return list field {key!r}")
    if not all(isinstance(row,dict) for row in rows):
        raise RuntimeError(f"{method}.{key} contains non-object entries")
    return rows


def observe_live_surface() -> dict:
    """Observe the public MCP interface through the same dispatch path clients use.

    A throwaway SQLite state store is used only to instantiate the server. No Git
    root is configured and no semantic or release mutation is performed.
    """
    from .protocol import PROTOCOL_VERSION, SERVER_INFO
    from .server import Server

    with tempfile.TemporaryDirectory(prefix="athena-release-abi-") as td:
        server=Server(str(Path(td)/"abi.sqlite"),git_root=None)
        try:
            tools=_rpc_list(server,"tools/list","tools")
            resources=_rpc_list(server,"resources/list","resources")
            prompts=_rpc_list(server,"prompts/list","prompts")
        finally:
            db=getattr(getattr(server,"store",None),"db",None)
            if db is not None:
                try:db.close()
                except Exception:pass

    return {
        "protocol_version":PROTOCOL_VERSION,
        "server_info":copy.deepcopy(SERVER_INFO),
        "tools":_sort_surface(tools,"name"),
        "resources":_sort_surface(resources,"uri"),
        "prompts":_sort_surface(prompts,"name"),
    }


def fingerprint_from_surface(surface: dict) -> dict:
    required=("protocol_version","server_info","tools","resources","prompts")
    missing=[key for key in required if key not in surface]
    if missing:raise ValueError(f"missing ABI surface keys: {missing}")

    normalized={
        "protocol_version":surface["protocol_version"],
        "server_info":copy.deepcopy(surface["server_info"]),
        "tools":_sort_surface(list(surface["tools"]),"name"),
        "resources":_sort_surface(list(surface["resources"]),"uri"),
        "prompts":_sort_surface(list(surface["prompts"]),"name"),
    }
    sections={
        "protocol_server":_sha({"protocol_version":normalized["protocol_version"],"server_info":normalized["server_info"]}),
        "tools":_sha(normalized["tools"]),
        "resources":_sha(normalized["resources"]),
        "prompts":_sha(normalized["prompts"]),
    }
    digest=_sha({"schema":ABI_SCHEMA,"algorithm":ABI_ALGORITHM,"surface":normalized})
    return {
        "schema":ABI_SCHEMA,
        "algorithm":ABI_ALGORITHM,
        "digest":digest,
        "counts":{
            "tools":len(normalized["tools"]),
            "resources":len(normalized["resources"]),
            "prompts":len(normalized["prompts"]),
        },
        "section_digests":sections,
        "surface":normalized,
        "laws":[
            "PACKAGE_VERSION_IDENTITY != ABI_IDENTITY",
            "SAME_VERSION_REQUIRES_SAME_FROZEN_ABI",
            "ABI_CHANGE_REQUIRES_VERSIONED_RELEASE_COORDINATE",
            "ABI_FINGERPRINT != PROMOTION_AUTHORITY",
        ],
    }


@lru_cache(maxsize=1)
def compute_public_abi() -> dict:
    return fingerprint_from_surface(observe_live_surface())


def compact_abi(record: dict) -> dict:
    return {k:copy.deepcopy(record[k]) for k in ("schema","algorithm","digest","counts","section_digests","laws")}


def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description="Compute the exact advertised ATHENA MCP public ABI fingerprint.")
    ap.add_argument("--full",action="store_true",help="Include the full canonicalized public interface instead of the compact fingerprint.")
    args=ap.parse_args(argv)
    record=compute_public_abi()
    print(json.dumps(record if args.full else compact_abi(record),indent=2,sort_keys=True,ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())

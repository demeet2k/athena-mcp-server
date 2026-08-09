from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _rpc(base_url: str, token: str, method: str, params: dict, request_id: int) -> dict:
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
    ).encode()
    request = Request(
        base_url.rstrip("/") + "/mcp",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    response = json.loads(urlopen(request, timeout=10).read())
    if response.get("error"):
        raise RuntimeError(response)
    return response["result"]


def _call(base_url: str, token: str, name: str, arguments: dict, request_id: int) -> dict:
    result = _rpc(
        base_url,
        token,
        "tools/call",
        {"name": name, "arguments": arguments},
        request_id,
    )
    if result.get("isError"):
        raise RuntimeError(result)
    return result["structuredContent"]


def _wait_ready(base_url: str, attempts: int = 60) -> dict:
    last = None
    for _ in range(attempts):
        try:
            last = json.loads(
                urlopen(base_url.rstrip("/") + "/readyz", timeout=3).read()
            )
            if last.get("ready"):
                return last
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = {"error": str(exc)}
        time.sleep(1)
    raise RuntimeError({"status": "NOT_READY", "last": last})


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18765")
    parser.add_argument("--token", required=True)
    parser.add_argument("--state-file", type=Path, required=True)
    parser.add_argument("--mode", choices=("write", "verify"), required=True)
    args = parser.parse_args(argv)

    ready = _wait_ready(args.base_url)
    init = _rpc(
        args.base_url,
        args.token,
        "initialize",
        {"protocolVersion": "2025-11-25"},
        1,
    )
    assert init["serverInfo"]["deployment"]["version"] == "ATHENA.DEPLOYMENT.2", init
    manifest = _call(args.base_url, args.token, "athena_deployment_manifest", {}, 2)
    assert manifest["version"] == "ATHENA.DEPLOYMENT.2", manifest

    if args.mode == "write":
        registered = _call(
            args.base_url,
            args.token,
            "athena_register",
            {
                "kind": "ARTIFACT",
                "domain": "DEPLOYMENT_CI",
                "verb": "VERIFY",
                "object_name": "PERSISTENT_RESTART_WITNESS",
                "method": "HTTP_CONTAINER_SMOKE",
                "input_contract": {},
                "output_contract": {},
                "actor": "DEPLOYMENT_CI",
            },
            3,
        )
        oid = registered["oid"]
        args.state_file.write_text(json.dumps({"oid": oid}) + "\n")
        result = {"status": "WRITE_PASS", "oid": oid}
    else:
        oid = json.loads(args.state_file.read_text())["oid"]
        resolved = _call(
            args.base_url,
            args.token,
            "athena_resolve",
            {"identifier": oid},
            3,
        )
        assert resolved["object"]["oid"] == oid, resolved
        result = {"status": "RESTART_READBACK_PASS", "oid": oid}

    print(
        json.dumps(
            {
                **result,
                "ready_status": ready["status"],
                "deployment_manifest_digest": manifest["manifest_digest"],
                "boundary": "Container smoke proves this observed process/volume path only; it is not production activation.",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

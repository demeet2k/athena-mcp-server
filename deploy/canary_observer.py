from __future__ import annotations

"""Observe two isolated instances of one immutable ATHENA release image.

The observer performs a replicated same-digest canary: a control instance and a
candidate instance run the exact same OCI digest on independent SQLite volumes.
The candidate receives a semantic witness, both instances undergo a planned
restart, and the witness must survive before the bounded observation window
begins.  The resulting assessment is evidence about this isolated runner path;
it is never cutover authority and it never contacts a production cluster.
"""

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from athena_mcp.deployment import assess_canary, validate_image_ref

OBSERVER_VERSION = "ATHENA.ISOLATED.CANARY.OBSERVER.1"
WITNESS_VERSION = "ATHENA.ISOLATED.CANARY.WITNESS.1"
OBSERVATIONS_VERSION = "ATHENA.ISOLATED.CANARY.OBSERVATIONS.1"
COMPARISON_KIND = "REPLICATED_SAME_DIGEST_STATE_RESTART"
MINIMUM_SAMPLE_COUNT = 30
MINIMUM_OBSERVATION_WINDOW_SECONDS = 60
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _nonempty(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    return text


def _git_sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    if not _GIT_SHA.fullmatch(text):
        raise ValueError(f"{field} must be a full 40-character Git SHA")
    return text


def percentile(values: Iterable[float], quantile: float) -> float:
    """Return a deterministic linearly interpolated percentile."""

    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("percentile requires at least one value")
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be between zero and one")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def inventory_digest(names: Iterable[str]) -> str:
    return _digest(sorted(str(name) for name in names))


def _request_json(
    url: str,
    *,
    token: str | None = None,
    payload: Mapping[str, Any] | None = None,
    timeout: float = 10.0,
) -> tuple[dict[str, Any], float]:
    body = None if payload is None else json.dumps(dict(payload)).encode("utf-8")
    headers = {"Accept": "application/json"}
    method = "GET"
    if body is not None:
        method = "POST"
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, data=body, headers=headers, method=method)
    started = time.perf_counter()
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    decoded = json.loads(raw)
    if not isinstance(decoded, dict):
        raise RuntimeError(f"{url} did not return a JSON object")
    return decoded, elapsed_ms


def _rpc(
    base_url: str,
    token: str,
    method: str,
    params: Mapping[str, Any] | None,
    request_id: int | str,
    *,
    timeout: float = 10.0,
) -> tuple[dict[str, Any], float]:
    response, elapsed_ms = _request_json(
        base_url.rstrip("/") + "/mcp",
        token=token,
        payload={
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": dict(params or {}),
        },
        timeout=timeout,
    )
    if response.get("error"):
        raise RuntimeError(response["error"])
    result = response.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"RPC {method} did not return an object result")
    return result, elapsed_ms


def _call(
    base_url: str,
    token: str,
    name: str,
    arguments: Mapping[str, Any],
    request_id: int | str,
    *,
    timeout: float = 10.0,
) -> tuple[dict[str, Any], float]:
    result, elapsed_ms = _rpc(
        base_url,
        token,
        "tools/call",
        {"name": name, "arguments": dict(arguments)},
        request_id,
        timeout=timeout,
    )
    if result.get("isError"):
        raise RuntimeError(result)
    structured = result.get("structuredContent")
    if not isinstance(structured, dict):
        raise RuntimeError(f"tool {name} did not return structuredContent")
    return structured, elapsed_ms


def wait_ready(
    base_url: str,
    *,
    attempts: int = 90,
    delay_seconds: float = 1.0,
    timeout: float = 3.0,
) -> dict[str, Any]:
    last: dict[str, Any] | None = None
    for _ in range(attempts):
        try:
            last, _ = _request_json(
                base_url.rstrip("/") + "/readyz",
                timeout=timeout,
            )
            if last.get("ready") is True:
                return last
        except (OSError, HTTPError, URLError, json.JSONDecodeError, RuntimeError) as exc:
            last = {"error": str(exc), "error_type": type(exc).__name__}
        time.sleep(delay_seconds)
    raise RuntimeError({"status": "NOT_READY", "base_url": base_url, "last": last})


def initialize(base_url: str, token: str, *, request_id: str) -> dict[str, Any]:
    result, _ = _rpc(
        base_url,
        token,
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "athena-isolated-canary", "version": "1"},
        },
        request_id,
    )
    server_info = result.get("serverInfo")
    if not isinstance(server_info, dict) or not server_info.get("name") or not server_info.get("version"):
        raise RuntimeError("initialize did not return a complete serverInfo")
    return result


def catalog_snapshot(base_url: str, token: str, *, prefix: str) -> dict[str, Any]:
    tools, _ = _rpc(base_url, token, "tools/list", {}, f"{prefix}-tools")
    resources, _ = _rpc(base_url, token, "resources/list", {}, f"{prefix}-resources")
    manifest, _ = _call(
        base_url,
        token,
        "athena_deployment_manifest",
        {},
        f"{prefix}-manifest",
    )
    tool_items = tools.get("tools")
    resource_items = resources.get("resources")
    if not isinstance(tool_items, list) or not isinstance(resource_items, list):
        raise RuntimeError("catalog response shape is incomplete")
    tool_names = sorted(
        str(item.get("name"))
        for item in tool_items
        if isinstance(item, dict) and item.get("name")
    )
    resource_uris = sorted(
        str(item.get("uri"))
        for item in resource_items
        if isinstance(item, dict) and item.get("uri")
    )
    if manifest.get("version") != "ATHENA.DEPLOYMENT.2":
        raise RuntimeError("deployment manifest version mismatch")
    return {
        "tool_count": len(tool_names),
        "tool_inventory_digest": inventory_digest(tool_names),
        "resource_count": len(resource_uris),
        "resource_inventory_digest": inventory_digest(resource_uris),
        "deployment_manifest_digest": manifest.get("manifest_digest"),
        "deployment_version": manifest.get("version"),
    }


def seed_state(
    base_url: str,
    token: str,
    *,
    witness_name: str,
) -> dict[str, Any]:
    result, _ = _call(
        base_url,
        token,
        "athena_register",
        {
            "kind": "ARTIFACT",
            "domain": "ISOLATED_CANARY",
            "verb": "VERIFY",
            "object_name": witness_name,
            "method": "REPLICATED_SAME_DIGEST_STATE_RESTART",
            "input_contract": {},
            "output_contract": {},
            "actor": "ATHENA_CANARY_OBSERVER",
        },
        "canary-seed-state",
    )
    obj = result.get("object")
    if not isinstance(obj, dict) or not obj.get("oid"):
        raise RuntimeError("athena_register did not return an object OID")
    return {"oid": str(obj["oid"]), "registered": True}


def verify_state(base_url: str, token: str, *, oid: str) -> dict[str, Any]:
    result, _ = _call(
        base_url,
        token,
        "athena_resolve",
        {"identifier": oid},
        "canary-verify-state",
    )
    obj = result.get("object")
    matched = isinstance(obj, dict) and obj.get("oid") == oid
    return {"oid": oid, "matched": matched}


def docker_restart(container_name: str) -> None:
    subprocess.run(
        ["docker", "restart", container_name],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def docker_restart_count(container_name: str) -> int:
    completed = subprocess.run(
        ["docker", "inspect", "--format", "{{.RestartCount}}", container_name],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    value = completed.stdout.strip()
    if not value.isdigit():
        raise RuntimeError(f"unexpected Docker restart count for {container_name}: {value!r}")
    return int(value)


def probe_sample(
    base_url: str,
    token: str,
    *,
    sample_id: str,
    timeout: float,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        ready, _ = _request_json(
            base_url.rstrip("/") + "/readyz",
            timeout=timeout,
        )
        manifest, _ = _call(
            base_url,
            token,
            "athena_deployment_manifest",
            {},
            sample_id,
            timeout=timeout,
        )
        success = ready.get("ready") is True and manifest.get("version") == "ATHENA.DEPLOYMENT.2"
        error = None if success else "readiness or deployment-version mismatch"
        ready_status = ready.get("status")
        manifest_digest = manifest.get("manifest_digest")
    except Exception as exc:  # The bounded observer records failures as measurements.
        success = False
        error = f"{type(exc).__name__}: {exc}"
        ready_status = None
        manifest_digest = None
    return {
        "sample_id": sample_id,
        "success": success,
        "latency_ms": (time.perf_counter() - started) * 1000.0,
        "ready_status": ready_status,
        "deployment_manifest_digest": manifest_digest,
        "error": error,
    }


def summarize_samples(
    samples: list[Mapping[str, Any]],
    *,
    raw_restart_count: int,
    planned_restart_count: int,
) -> dict[str, Any]:
    if not samples:
        raise ValueError("at least one sample is required")
    failures = sum(1 for item in samples if item.get("success") is not True)
    latencies = [float(item["latency_ms"]) for item in samples]
    unexpected = max(0, int(raw_restart_count) - int(planned_restart_count))
    return {
        "error_rate": failures / len(samples),
        "p95_ms": percentile(latencies, 0.95),
        "restart_count": unexpected,
        "raw_restart_count": int(raw_restart_count),
        "planned_restart_count": int(planned_restart_count),
        "sample_count": len(samples),
        "successful_samples": len(samples) - failures,
        "failed_samples": failures,
        "all_ready": failures == 0,
    }


def observe_pair(
    control_url: str,
    control_token: str,
    canary_url: str,
    canary_token: str,
    *,
    sample_count: int,
    interval_seconds: float,
    timeout: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float]:
    if sample_count < MINIMUM_SAMPLE_COUNT:
        raise ValueError(f"sample_count must be at least {MINIMUM_SAMPLE_COUNT}")
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than zero")
    control_samples: list[dict[str, Any]] = []
    canary_samples: list[dict[str, Any]] = []
    window_started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for index in range(sample_count):
            scheduled = window_started + index * interval_seconds
            remaining = scheduled - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            control_future = pool.submit(
                probe_sample,
                control_url,
                control_token,
                sample_id=f"control-{index + 1:03d}",
                timeout=timeout,
            )
            canary_future = pool.submit(
                probe_sample,
                canary_url,
                canary_token,
                sample_id=f"canary-{index + 1:03d}",
                timeout=timeout,
            )
            control_samples.append(control_future.result())
            canary_samples.append(canary_future.result())
    observed_window = time.monotonic() - window_started
    return control_samples, canary_samples, observed_window


def compile_witness(
    *,
    image_ref: str,
    source_head: str,
    release_tag: str,
    release_run_id: str,
    oci_run_id: str,
    workflow_run_id: str,
    workflow_head: str,
    control_catalog: Mapping[str, Any],
    canary_catalog: Mapping[str, Any],
    state_witness: Mapping[str, Any],
    baseline_metrics: Mapping[str, Any],
    canary_metrics: Mapping[str, Any],
    assessment: Mapping[str, Any],
    observation_window_seconds: int,
    observed_at: str | None = None,
) -> dict[str, Any]:
    image = validate_image_ref(image_ref, require_digest=True)
    source = _git_sha(source_head, "source_head")
    workflow_source = _git_sha(workflow_head, "workflow_head")
    if assessment.get("version") != "ATHENA.CANARY.ASSESSMENT.2":
        raise ValueError("assessment version mismatch")
    structural_match = {
        "tool_inventory": control_catalog.get("tool_inventory_digest")
        == canary_catalog.get("tool_inventory_digest"),
        "resource_inventory": control_catalog.get("resource_inventory_digest")
        == canary_catalog.get("resource_inventory_digest"),
        "deployment_manifest": control_catalog.get("deployment_manifest_digest")
        == canary_catalog.get("deployment_manifest_digest"),
        "state_restart_replay": state_witness.get("matched") is True,
    }
    witness: dict[str, Any] = {
        "schema": WITNESS_VERSION,
        "observer": OBSERVER_VERSION,
        "comparison_kind": COMPARISON_KIND,
        "repository": "demeet2k/athena-mcp-server",
        "release_tag": _nonempty(release_tag, "release_tag"),
        "release_run_id": _nonempty(release_run_id, "release_run_id"),
        "oci_run_id": _nonempty(oci_run_id, "oci_run_id"),
        "workflow_run_id": _nonempty(workflow_run_id, "workflow_run_id"),
        "workflow_head": workflow_source,
        "image_ref": image["image_ref"],
        "image_digest": image["digest"],
        "source_head": source,
        "observed_at": observed_at or _utc_now(),
        "observation_window_seconds": int(observation_window_seconds),
        "instances": {
            "control": {"image_ref": image["image_ref"], "catalog": dict(control_catalog)},
            "canary": {"image_ref": image["image_ref"], "catalog": dict(canary_catalog)},
        },
        "state_witness": dict(state_witness),
        "structural_match": structural_match,
        "baseline_metrics": dict(baseline_metrics),
        "canary_metrics": dict(canary_metrics),
        "assessment": dict(assessment),
        "authority": {
            "cutover_authorized": False,
            "cluster_apply_authorized": False,
            "traffic_activation_authorized": False,
            "production_secret_provisioned": False,
            "production_state_contacted": False,
        },
        "boundary": (
            "This same-digest replicated canary witnesses isolated container, HTTP, catalog, and SQLite restart behavior. "
            "It does not compare a different release, apply cluster objects, provision production secrets, authorize "
            "cutover, activate traffic, establish production health, or promote empirical/Y1 authority."
        ),
    }
    witness["witness_digest"] = _digest(witness)
    return witness


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    image = validate_image_ref(args.image_ref, require_digest=True)
    source_head = _git_sha(args.source_head, "source_head")
    control_token = _nonempty(os.environ.get(args.control_token_env), args.control_token_env)
    canary_token = _nonempty(os.environ.get(args.canary_token_env), args.canary_token_env)
    if control_token == canary_token:
        raise ValueError("control and canary tokens must be distinct")
    if args.sample_count < MINIMUM_SAMPLE_COUNT:
        raise ValueError(f"sample_count must be at least {MINIMUM_SAMPLE_COUNT}")
    if args.minimum_window_seconds < MINIMUM_OBSERVATION_WINDOW_SECONDS:
        raise ValueError(
            f"minimum_window_seconds must be at least {MINIMUM_OBSERVATION_WINDOW_SECONDS}"
        )

    wait_ready(args.control_url)
    wait_ready(args.canary_url)
    initialize(args.control_url, control_token, request_id="control-initialize-before")
    initialize(args.canary_url, canary_token, request_id="canary-initialize-before")
    control_before = catalog_snapshot(args.control_url, control_token, prefix="control-before")
    canary_before = catalog_snapshot(args.canary_url, canary_token, prefix="canary-before")
    if control_before != canary_before:
        raise RuntimeError({"status": "PRE_RESTART_CATALOG_MISMATCH", "control": control_before, "canary": canary_before})

    state = seed_state(
        args.canary_url,
        canary_token,
        witness_name=f"V3_3_ISOLATED_CANARY_{args.workflow_run_id}",
    )
    docker_restart(args.control_container)
    docker_restart(args.canary_container)
    wait_ready(args.control_url)
    wait_ready(args.canary_url)
    initialize(args.control_url, control_token, request_id="control-initialize-after")
    initialize(args.canary_url, canary_token, request_id="canary-initialize-after")
    state_readback = verify_state(args.canary_url, canary_token, oid=state["oid"])
    if state_readback["matched"] is not True:
        raise RuntimeError({"status": "STATE_REPLAY_MISMATCH", "state": state_readback})

    control_catalog = catalog_snapshot(args.control_url, control_token, prefix="control-after")
    canary_catalog = catalog_snapshot(args.canary_url, canary_token, prefix="canary-after")
    control_samples, canary_samples, observed_window = observe_pair(
        args.control_url,
        control_token,
        args.canary_url,
        canary_token,
        sample_count=args.sample_count,
        interval_seconds=args.interval_seconds,
        timeout=args.timeout,
    )
    observed_window_seconds = int(math.floor(observed_window))
    if observed_window_seconds < args.minimum_window_seconds:
        raise RuntimeError(
            {
                "status": "OBSERVATION_WINDOW_TOO_SHORT",
                "observed": observed_window_seconds,
                "required": args.minimum_window_seconds,
            }
        )

    control_raw_restarts = docker_restart_count(args.control_container)
    canary_raw_restarts = docker_restart_count(args.canary_container)
    baseline = summarize_samples(
        control_samples,
        raw_restart_count=control_raw_restarts,
        planned_restart_count=1,
    )
    candidate_summary = summarize_samples(
        canary_samples,
        raw_restart_count=canary_raw_restarts,
        planned_restart_count=1,
    )
    structural_match = (
        control_catalog.get("tool_inventory_digest")
        == canary_catalog.get("tool_inventory_digest")
        and control_catalog.get("resource_inventory_digest")
        == canary_catalog.get("resource_inventory_digest")
        and control_catalog.get("deployment_manifest_digest")
        == canary_catalog.get("deployment_manifest_digest")
    )
    canary = {
        **candidate_summary,
        "ready": candidate_summary["all_ready"] is True,
        "schema_up_to_date": (
            canary_catalog.get("deployment_version") == "ATHENA.DEPLOYMENT.2"
            and canary_catalog.get("deployment_manifest_digest")
            == canary_before.get("deployment_manifest_digest")
        ),
        "replay_match": structural_match and state_readback["matched"] is True,
        "observation_window_seconds": observed_window_seconds,
    }
    baseline_for_policy = {
        "error_rate": baseline["error_rate"],
        "p95_ms": baseline["p95_ms"],
        "restart_count": baseline["restart_count"],
    }
    canary_for_policy = {
        "error_rate": canary["error_rate"],
        "p95_ms": canary["p95_ms"],
        "restart_count": canary["restart_count"],
        "ready": canary["ready"],
        "schema_up_to_date": canary["schema_up_to_date"],
        "replay_match": canary["replay_match"],
        "sample_count": canary["sample_count"],
        "observation_window_seconds": canary["observation_window_seconds"],
    }
    assessment = assess_canary(baseline_for_policy, canary_for_policy)
    observations = {
        "schema": OBSERVATIONS_VERSION,
        "observer": OBSERVER_VERSION,
        "image_ref": image["image_ref"],
        "source_head": source_head,
        "control_samples": control_samples,
        "canary_samples": canary_samples,
        "observed_window_seconds": observed_window_seconds,
        "control_raw_restart_count": control_raw_restarts,
        "canary_raw_restart_count": canary_raw_restarts,
        "boundary": "Raw samples describe only the two isolated workflow containers and contain no bearer tokens.",
    }
    observations["observations_digest"] = _digest(observations)
    witness = compile_witness(
        image_ref=image["image_ref"],
        source_head=source_head,
        release_tag=args.release_tag,
        release_run_id=args.release_run_id,
        oci_run_id=args.oci_run_id,
        workflow_run_id=args.workflow_run_id,
        workflow_head=args.workflow_head,
        control_catalog=control_catalog,
        canary_catalog=canary_catalog,
        state_witness={**state, **state_readback},
        baseline_metrics=baseline,
        canary_metrics=canary,
        assessment=assessment,
        observation_window_seconds=observed_window_seconds,
    )

    output = Path(args.output_dir)
    _write_json(output / "canary-observations.v3.3.0.json", observations)
    _write_json(output / "canary-assessment.v3.3.0.json", assessment)
    _write_json(output / "canary-witness.v3.3.0.json", witness)
    if assessment.get("decision") != "PROMOTE":
        raise RuntimeError(
            {
                "status": "CANARY_NOT_PROMOTABLE",
                "decision": assessment.get("decision"),
                "failed_gates": assessment.get("failed_gates"),
            }
        )
    return witness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-ref", required=True)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--release-run-id", required=True)
    parser.add_argument("--oci-run-id", required=True)
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--workflow-head", required=True)
    parser.add_argument("--control-url", default="http://127.0.0.1:18765")
    parser.add_argument("--canary-url", default="http://127.0.0.1:18766")
    parser.add_argument("--control-token-env", default="ATHENA_CONTROL_TOKEN")
    parser.add_argument("--canary-token-env", default="ATHENA_CANARY_TOKEN")
    parser.add_argument("--control-container", default="athena-v3-control")
    parser.add_argument("--canary-container", default="athena-v3-canary")
    parser.add_argument("--sample-count", type=int, default=31)
    parser.add_argument("--interval-seconds", type=float, default=2.1)
    parser.add_argument("--minimum-window-seconds", type=int, default=60)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output-dir", default="dist/canary")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    witness = run(args)
    print(
        json.dumps(
            {
                "status": "PASS_ISOLATED_SAME_DIGEST_CANARY",
                "decision": witness["assessment"]["decision"],
                "image_ref": witness["image_ref"],
                "witness_digest": witness["witness_digest"],
                "cutover_authorized": witness["authority"]["cutover_authorized"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

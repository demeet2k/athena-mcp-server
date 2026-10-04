"""A local multi-process RET carrier slice through the existing MCP Wiki tool.

No broker, provider revision assertion, scheduler, or source promotion. Operator
supplied digests anchor saved artifacts; self-rehashed records are not authority.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from .wiki_git import _run_bounded, canonical

TOOL = "athena_git_wiki_compile"
ARTIFACT = "ATHENA.BRAIN.LOCAL_SLICE.V1"
MAX_SNAPSHOT_BYTES = 8_000_000
HARNESS = "ATHENA.HARNESS.INTERNAL.WIKI.V1"
SKILL = "ATHENA.SKILL.INTERNAL.WIKI.V1"
NATIVE_TOOL = "ATHENA.TOOL.INTERNAL.WIKI.V1"
NATIVE_PATH = "TOOLS/KC144/GID027_R03C03_INTERNAL_WIKI_V1/internal_wiki_v1.py"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_file(path, limit):
    with Path(path).open("rb") as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("SLICE_SAVED_ARTIFACT_TOO_LARGE")
    return raw


def read_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("SLICE_DUPLICATE_KEY")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("SLICE_NONFINITE")))


def code_pin(root, head, *, clean=True):
    root = Path(root).resolve()
    actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().strip()
    dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"])
    if actual != head or (clean and dirty):
        raise ValueError("SLICE_CODE_DRIFT")
    # Clean ancestor trees bind all tracked data; record all runtime Python.
    paths = {p for p in root.rglob("*.py") if ".git" not in p.parts and "__pycache__" not in p.parts}
    if not clean:
        # MCP may contain an explicitly authorized uncommitted repair. Bind every
        # tracked source/config/document byte as well as new Python modules.
        names = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
        paths.update(root / name.decode("utf-8") for name in names.split(b"\0") if name)
    readset = {}
    for path in sorted(paths):
        if path.is_symlink():
            raise ValueError("SLICE_SYMLINK_CODE")
        readset[path.relative_to(root).as_posix()] = sha(path.read_bytes())
    tree = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD^{tree}"]).decode().strip()
    return {"head": actual, "tree": tree, "source_readset": readset}


def snapshot_readset(root):
    root = Path(root)
    resolved = root.resolve()
    if root.is_symlink() or (root / "objects").is_symlink():
        raise ValueError("SLICE_SOURCE_PATH")
    paths = [root / "manifest.json", *sorted((root / "objects").glob("*.json"))]
    result = {}
    total = 0
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(resolved):
            raise ValueError("SLICE_SOURCE_PATH")
        with path.open("rb") as handle:
            raw = handle.read(MAX_SNAPSHOT_BYTES - total + 1)
        total += len(raw)
        if total > MAX_SNAPSHOT_BYTES:
            raise ValueError("SLICE_SOURCE_TOO_LARGE")
        result[path.relative_to(root).as_posix()] = sha(raw)
    return result


def brain_query(spec, snapshot_root):
    request = {key: spec[key] for key in ("brain_root", "brain_head", "snapshot_digest", "state_root", "query")}
    request["snapshot_root"] = str(Path(snapshot_root).resolve())
    result = _run_bounded([sys.executable, "-I", "-B", str(Path(__file__).with_name("brain_snapshot_worker.py"))],
                          input=canonical(request), cwd=spec["brain_root"], timeout=30, max_output_bytes=500_000)
    if result.returncode:
        raise ValueError("SLICE_BRAIN_FAILED:" + result.stderr.decode(errors="replace")[-1000:])
    return read_json(result.stdout)


def project(answer, *, query, snapshot_digest, state_root, observed_at):
    if not re.fullmatch("[0-9a-f]{64}", snapshot_digest):
        raise ValueError("SLICE_SNAPSHOT_NAMESPACE")
    if (answer.get("question") != query or answer.get("snapshot_digest") != snapshot_digest
            or answer.get("state_root") != state_root or answer.get("epistemic_class") != "RET"
            or answer.get("promotion_eligible") is not False
            or answer.get("source_instructions_executable") is not False):
        raise ValueError("SLICE_ANSWER_BINDING")
    raw = canonical(answer)
    if len(raw) > 262144:
        raise ValueError("SLICE_ANSWER_TOO_LARGE")
    identity = sha(raw)
    source_id = "brain-answer-" + identity
    locator = "urn:athenachka:snapshot:" + snapshot_digest + ":answer:" + identity
    text = raw.decode("utf-8")
    return {"operation": "QUERY", "query": query, "limit": 1, "pages": [], "contradictions": [],
            "sources": [{"source_id": source_id, "title": query, "source_type": "snapshot_carrier",
                         "locator": locator, "content_sha256": "sha256:" + identity,
                         "observed_at": observed_at, "summary": text,
                         "raw_path": "knowledge/raw/brain-answer-" + identity + ".json", "tags": ["RET"]}],
            "claims": [{"claim_id": "brain-retrieval-" + identity, "statement": query,
                        "epistemic_status": "RET", "observed_at": observed_at,
                        "scope": "Immutable offline answer carrier; nested holds and conflicts remain source data.",
                        "source_refs": [{"source_id": source_id, "locator": locator}],
                        "derivation_refs": [], "method_ref": "", "contradicts": [], "supersedes": [],
                        "superseded_by": [], "page_refs": [], "tags": []}]}


def validate_spec(spec):
    required = {"brain_root", "brain_head", "mcp_root", "mcp_head", "athena_root", "athena_head",
                "snapshot_root", "snapshot_digest", "state_root", "query", "observed_at"}
    if type(spec) is not dict or set(spec) != required:
        raise ValueError("SLICE_SPEC_SCHEMA_NO_DEPENDENCIES_OR_FOREIGN_CALLS")
    if any(type(value) is not str or not value for value in spec.values()):
        raise ValueError("SLICE_SPEC_STRING_REQUIRED")
    for name in ("brain", "mcp", "athena"):
        if not re.fullmatch("[0-9a-f]{40}", spec[name + "_head"]):
            raise ValueError("SLICE_EXACT_COMMIT_REQUIRED")
    if not re.fullmatch("[0-9a-f]{64}", spec["snapshot_digest"]):
        raise ValueError("SLICE_SNAPSHOT_NAMESPACE")
    if len(spec["query"].encode("utf-8")) > 4096 or len(spec["state_root"].encode("utf-8")) > 512:
        raise ValueError("SLICE_SPEC_TOO_LARGE")


def pins(spec):
    if Path(spec["mcp_root"]).resolve() != Path(__file__).resolve().parents[1]:
        raise ValueError("SLICE_MCP_ROOT_MISMATCH")
    return {name: code_pin(spec[name + "_root"], spec[name + "_head"], clean=name != "mcp")
            for name in ("brain", "mcp", "athena")}


def immutable(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        import os
        os.fsync(handle.fileno())


def dispatch(spec, request, directory):
    from .server import Server
    server = Server(str(Path(directory) / "dispatch.sqlite"), git_root=spec["athena_root"])
    try:
        raw_request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": TOOL, "arguments": {"expected_git_head": spec["athena_head"], "request": request}}}
        return raw_request, server.handle(raw_request)
    finally:
        server.store.close()


def run(spec, directory):
    validate_spec(spec)
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    code = pins(spec)
    source = Path(spec["snapshot_root"])
    source_files = snapshot_readset(source)
    saved = directory / "snapshot"
    for name, expected in source_files.items():
        path = source / name
        if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):
            raise ValueError("SLICE_SOURCE_PATH")
        with path.open("rb") as handle:
            raw = handle.read(MAX_SNAPSHOT_BYTES + 1)
        if len(raw) > MAX_SNAPSHOT_BYTES or sha(raw) != expected:
            raise ValueError("SLICE_SOURCE_CHANGED")
        immutable(saved / name, raw)
    answer = brain_query(spec, saved)
    request = project(answer, **{k: spec[k] for k in ("query", "snapshot_digest", "state_root", "observed_at")})
    task = {"artifact": ARTIFACT, "allowed_tool": TOOL, "operation": "QUERY", "spec": spec,
            "code": code, "source_readset": source_files, "brain_answer_sha256": sha(canonical(answer)),
            "query_sha256": sha(canonical(spec["query"])), "request": request,
            "mcp_snapshot_id": None, "standing": "RET", "promotion_eligible": False,
            "source_instructions_executable": False}
    task_raw = canonical(task)
    if len(task_raw) > 4_000_000:
        raise ValueError("SLICE_TASK_TOO_LARGE")
    immutable(directory / "task.json", task_raw)
    immutable(directory / "brain-answer.json", canonical(answer))
    if pins(spec) != code:
        raise ValueError("SLICE_CODE_DRIFT")
    immutable(directory / "PENDING", sha(task_raw).encode())
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": TOOL, "arguments": {"expected_git_head": spec["athena_head"], "request": request}}}
    immutable(directory / "rpc-request.json", canonical(rpc))
    dispatched_rpc, result = dispatch(spec, request, directory)
    if dispatched_rpc != rpc:
        raise ValueError("SLICE_DISPATCH_CHANGED")
    immutable(directory / "rpc-result.json", canonical(result))
    if pins(spec) != code:
        raise ValueError("SLICE_CODE_DRIFT")
    verify_result(task, result)
    receipt = {"artifact": ARTIFACT, "task_sha256": sha(task_raw), "result_sha256": sha(canonical(result)),
               "rpc_request_sha256": sha(canonical(rpc)), "standing": "COMPLETE_LOCAL_QUERY",
               "source_holds": answer["holds"], "promotion_eligible": False,
               "source_instructions_executable": False, "external_broker_operation": False}
    immutable(directory / "receipt.json", canonical(receipt))
    return {"task_sha256": sha(task_raw), "receipt_sha256": sha(canonical(receipt)), "receipt": receipt}


def verify_result(task, result):
    if (result.get("jsonrpc") != "2.0" or type(result.get("id")) is not int or result.get("id") != 1
            or "error" in result or set(task["request"]) !=
               {"operation", "query", "limit", "pages", "contradictions", "sources", "claims"}
            or task["request"].get("operation") != "QUERY"):
        raise ValueError("SLICE_RPC_RESULT_NAMESPACE")
    outer = result.get("result", {})
    value = outer.get("structuredContent", {})
    content = outer.get("content", [])
    if (value.get("artifact") != "ATHENA.MCP.GIT_WIKI.V1" or value.get("operation") != "QUERY"
            or len(content) != 1 or content[0].get("type") != "text"
            or read_json(content[0].get("text", "")) != value):
        raise ValueError("SLICE_RPC_RESULT_NAMESPACE")
    if (outer.get("isError") is not False or value.get("git_head") != task["spec"]["athena_head"]
            or value.get("request_sha256") != sha(canonical(task["request"]))
            or value.get("mutation_applied") is not False or value.get("standing") != "COMPLETE"
            or not value.get("execution_receipt", {}).get("outputs")):
        raise ValueError("SLICE_EXECUTION_NOT_VERIFIED")
    receipt = value["execution_receipt"]
    outputs = receipt["outputs"]
    if (len(outputs) != 1 or receipt.get("standing") != "COMPLETE"
            or receipt.get("artifact") != "ATHENA.REPOSITORY.SKILL.EXECUTOR.RECEIPT.V1"
            or receipt.get("harness_id") != HARNESS
            or receipt.get("input_digest") != "sha256:" + sha(canonical({"wiki_request": task["request"]}))
            or {k: outputs[0].get(k) for k in ("operation", "skill_id", "tool_id")} !=
               {"operation": "repository_apply", "skill_id": SKILL, "tool_id": NATIVE_TOOL}):
        raise ValueError("SLICE_EXECUTION_NOT_VERIFIED")
    audit = receipt.get("audit", [])
    source_hash = task["code"]["athena"]["source_readset"][NATIVE_PATH]
    if (len(audit) != 1 or audit[0].get("operation") != "repository_apply"
            or audit[0].get("skill_id") != SKILL or audit[0].get("tool_id") != NATIVE_TOOL
            or audit[0].get("projection") != ["wiki_request"]
            or audit[0].get("standing") != "EXECUTED_PUBLIC_JSON_UNARY"
            or audit[0].get("source_sha256") != "sha256:" + source_hash):
        raise ValueError("SLICE_EXECUTOR_ROUTING_MISMATCH")
    native = outputs[0].get("result", {})
    cone = native.get("minimum_decision_cone", {})
    sources = cone.get("sources", [])
    claims = cone.get("claims", [])
    expected = task["request"]["sources"][0]
    if (native.get("artifact") != "ATHENA.INTERNAL.WIKI.RECEIPT.V1" or native.get("tool_id") != NATIVE_TOOL
            or native.get("version") != "1.0.0" or native.get("input_digest") != "sha256:" + sha(canonical(task["request"]))
            or native.get("operation") != "QUERY" or native.get("standing") not in ("READY", "REVIEW")
            or len(sources) != 1 or len(claims) != 1
            or native.get("query") != task["request"]["query"].strip()
            or sources[0] != expected
            or {k: v for k, v in claims[0].items() if k not in
                ("query_score", "current", "relation_context_only", "closure_context_only")} != task["request"]["claims"][0]):
        raise ValueError("SLICE_NATIVE_CARRIER_NOT_VERIFIED")


def reconstruct(directory, *, expected_task_sha256, expected_receipt_sha256):
    directory = Path(directory).resolve()
    task_raw = read_file(directory / "task.json", 4_000_000)
    if sha(task_raw) != expected_task_sha256:
        raise ValueError("SLICE_TASK_TAMPER")
    task = read_json(task_raw)
    task_fields = {"artifact", "allowed_tool", "operation", "spec", "code", "source_readset", "brain_answer_sha256",
                   "query_sha256", "request", "mcp_snapshot_id", "standing", "promotion_eligible", "source_instructions_executable"}
    if (set(task) != task_fields or task.get("artifact") != ARTIFACT or task.get("allowed_tool") != TOOL
            or task.get("operation") != "QUERY" or task.get("mcp_snapshot_id") is not None
            or task.get("standing") != "RET" or task.get("promotion_eligible") is not False
            or task.get("source_instructions_executable") is not False):
        raise ValueError("SLICE_TASK_NAMESPACE")
    spec = task["spec"]
    validate_spec(spec)
    if task.get("query_sha256") != sha(canonical(spec["query"])):
        raise ValueError("SLICE_QUERY_BINDING")
    if pins(spec) != task["code"]:
        raise ValueError("SLICE_CODE_DRIFT")
    if snapshot_readset(directory / "snapshot") != task["source_readset"]:
        raise ValueError("SLICE_SOURCE_TAMPER")
    answer = brain_query(spec, directory / "snapshot")
    if (canonical(answer) != read_file(directory / "brain-answer.json", 262_144)
            or sha(canonical(answer)) != task["brain_answer_sha256"]
            or project(answer, **{k: spec[k] for k in ("query", "snapshot_digest", "state_root", "observed_at")}) != task["request"]):
        raise ValueError("SLICE_PROJECTION_TAMPER")
    pending = directory / "PENDING"
    if not pending.exists() or read_file(pending, 64) != expected_task_sha256.encode():
        raise ValueError("SLICE_PENDING_BINDING")
    path = directory / "receipt.json"
    if not path.exists():
        raise ValueError("SLICE_AMBIGUOUS_PENDING_NO_REEXECUTION")
    receipt_raw = read_file(path, 262_144)
    if sha(receipt_raw) != expected_receipt_sha256:
        raise ValueError("SLICE_RECEIPT_TAMPER")
    receipt = read_json(receipt_raw)
    raw_result = read_file(directory / "rpc-result.json", 8_010_000)
    raw_request = read_file(directory / "rpc-request.json", 1_010_000)
    if (receipt["task_sha256"] != expected_task_sha256 or receipt["result_sha256"] != sha(raw_result)
            or receipt["rpc_request_sha256"] != sha(raw_request)):
        raise ValueError("SLICE_RESULT_TAMPER")
    expected_rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": TOOL,
                    "arguments": {"expected_git_head": spec["athena_head"], "request": task["request"]}}}
    if read_json(raw_request) != expected_rpc:
        raise ValueError("SLICE_RPC_ROUTING_MISMATCH")
    if (receipt.get("artifact") != ARTIFACT or receipt.get("standing") != "COMPLETE_LOCAL_QUERY"
            or receipt.get("source_holds") != answer["holds"] or receipt.get("promotion_eligible") is not False
            or receipt.get("source_instructions_executable") is not False
            or receipt.get("external_broker_operation") is not False):
        raise ValueError("SLICE_RECEIPT_FLAGS_MISMATCH")
    verify_result(task, read_json(raw_result))
    return {"standing": "RECONSTRUCTED_FROM_SAVED_BYTES", "handler_calls": 0,
            "task_sha256": expected_task_sha256, "receipt_sha256": expected_receipt_sha256,
            "source_holds": answer["holds"], "promotion_eligible": False}

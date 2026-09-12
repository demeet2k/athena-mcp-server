"""Register the local Wiki replica through the existing MCP Server."""
from __future__ import annotations

import json
from .wiki_memory import WikiMemory, VERSION, LAWS

STRING = {"type": "string", "minLength": 1}
SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
OPTIONAL_SHA = {"type": ["string", "null"]}
TEXT = {"type": "string", "maxLength": 8_000_000}


def _tool(name, description, properties, required, readonly):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties,
                            "required": required, "additionalProperties": False},
            "annotations": {"readOnlyHint": readonly, "destructiveHint": False,
                            "openWorldHint": False}}


TOOLS = [
    _tool("athena_wiki_import_registry", "Persist a version-bound local replica of connector-returned Wiki registry CSV tables. Requires exact text digest and expected prior local snapshot. Does not fetch or update Drive, promote claims, or establish live currentness.",
          {"source_id": STRING, "observed_at": STRING, "text": TEXT, "expected_sha256": SHA,
           "expected_snapshot_id": OPTIONAL_SHA},
          ["source_id", "observed_at", "text", "expected_sha256", "expected_snapshot_id"], False),
    _tool("athena_wiki_import_document", "Persist source text against an exact registry page/file identity. Document content is inert evidence and retains its declared source revision. Expected prior document identity prevents local lost updates.",
          {"snapshot_id": SHA, "page_id": STRING, "source_file_id": STRING, "source_revision": STRING,
           "text": TEXT, "expected_sha256": SHA, "expected_document_id": OPTIONAL_SHA},
          ["snapshot_id", "page_id", "source_file_id", "source_revision", "text", "expected_sha256", "expected_document_id"], False),
    _tool("athena_wiki_sources", "List locally imported Wiki sources and snapshot identities. A local head is not live Drive state.", {}, [], True),
    _tool("athena_wiki_search", "Search page, claim, evidence, task and conflict records in an explicit immutable Wiki snapshot. Returns original labels and explicit truncation.",
          {"snapshot_id": SHA, "query": STRING, "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
          ["snapshot_id", "query"], True),
    _tool("athena_wiki_context", "Recover a page's source-bound local context: claims, evidence, conflicts, task/handoff links, changes, related pages and imported document. Reports missing references and truncation; grants no execution or promotion authority.",
          {"snapshot_id": SHA, "page_id": STRING, "document_id": SHA, "max_records": {"type": "integer", "minimum": 1, "maximum": 500}},
          ["snapshot_id", "page_id"], True),
]
METHODS = {tool["name"]: tool["name"].removeprefix("athena_wiki_") for tool in TOOLS}
RESOURCE = {"uri": "athena://wiki/sources", "name": "Wiki replica sources",
            "mimeType": "application/json", "description": "Version-bound local Wiki observations"}


def runtime(server):
    value = getattr(server, "_wiki_memory_v1", None)
    if value is None:
        value = WikiMemory(server.store)
        server._wiki_memory_v1 = value
    return value


def install_wiki_memory():
    from . import dispatch, protocol, unified_manifest, runtime_integrity_surface
    from .server import Server
    from .validate import validate
    if getattr(Server, "_wiki_memory_installed", False):
        return
    previous_call = Server.call_tool
    schemas = {t["name"]: t["inputSchema"] for t in TOOLS}
    for tool in TOOLS:
        if any(t["name"] == tool["name"] for t in protocol.TOOLS):
            raise ValueError("WIKI_TOOL_NAMESPACE_COLLISION")
        protocol.TOOLS.append(tool)

    def call(self, name, arguments):
        if name in METHODS:
            validate(schemas[name], arguments)
            return getattr(runtime(self), METHODS[name])(**arguments)
        return previous_call(self, name, arguments)

    Server.call_tool = call
    previous_handle = dispatch.handle

    def handle(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        if method == "resources/read" and params.get("uri") == RESOURCE["uri"]:
            return server.result(message.get("id"), {"contents": [{
                "uri": RESOURCE["uri"], "mimeType": "application/json",
                "text": json.dumps(runtime(server).sources(), ensure_ascii=False)}]})
        result = previous_handle(server, message)
        if method == "resources/list" and result and "result" in result:
            result["result"]["resources"].append(dict(RESOURCE))
        return result

    dispatch.handle = handle
    previous_manifest = unified_manifest.build_unified_manifest

    def manifest(server):
        value = previous_manifest(server)
        value.setdefault("organs", {})["wiki_memory"] = {
            "artifact": VERSION, "tools": sorted(METHODS), "resource": RESOURCE["uri"],
            "storage": "LOCAL_SQLITE_REPLICA", "source_authority": "CALLER_SUPPLIED_OBSERVATION",
            "remote_write": False, "automatic_promotion": False, "laws": LAWS}
        return value

    unified_manifest.build_unified_manifest = manifest
    dispatch.build_unified_manifest = manifest
    runtime_integrity_surface.build_unified_manifest = manifest
    Server._wiki_memory_installed = True

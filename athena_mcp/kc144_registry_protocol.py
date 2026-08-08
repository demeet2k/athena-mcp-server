from __future__ import annotations

from .kc144_registry_pack import REGISTRIES, SEARCH_REGISTRIES

_REGISTRY_NAMES = sorted(REGISTRIES)
_SEARCH_NAMES = sorted(SEARCH_REGISTRIES)

REGISTRY_TOOLS = [
    {
        "name": "athena_kc144_registry_status",
        "description": "Return the immutable KC144 registry-pack identity, package-data carrier, manifest digest, declared counts, lens inventory, and optional full verification receipt.",
        "inputSchema": {
            "type": "object",
            "properties": {"verify": {"type": "boolean"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_registry_catalog",
        "description": "List every KC144 registry, archive member, format, declared record count, member presence, and uncompressed byte size.",
        "inputSchema": {"type": "object", "additionalProperties": False},
    },
    {
        "name": "athena_kc144_registry_query",
        "description": "Perform a bounded deterministic query over one named cell, maths, coordinate, graph, harness, tool, skill, dataset, source, transport, completion, hold, or receipt registry. Exact filters support dotted paths such as address.gid.",
        "inputSchema": {
            "type": "object",
            "required": ["registry"],
            "properties": {
                "registry": {"type": "string", "enum": _REGISTRY_NAMES},
                "query": {"type": "string"},
                "filters": {"type": "object"},
                "offset": {"type": "integer", "minimum": 0},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_registry_cross_search",
        "description": "Search multiple typed KC144 registries with exact case-folded lexical matching. Ranking is deterministic occurrence count, never semantic authority or evidentiary strength.",
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "registries": {"type": "array", "items": {"type": "string", "enum": _SEARCH_NAMES}, "uniqueItems": True},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                "per_registry": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_registry_source_bundle",
        "description": "Resolve one exact source_id into its source and dataset identities plus every linked maths, graph, coordinate, harness, skill and tool record, preserving source-bound authority.",
        "inputSchema": {
            "type": "object",
            "required": ["source_id"],
            "properties": {
                "source_id": {"type": "string", "minLength": 1},
                "limit_per_registry": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_registry_cell_bundle",
        "description": "Hydrate one immutable GID cell with all stored coordinates, hosted object identities/counts, HOLDs, and exact host/semantic completion-task links.",
        "inputSchema": {
            "type": "object",
            "required": ["gid"],
            "properties": {
                "gid": {"type": "integer", "minimum": 1, "maximum": 144},
                "task_limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_completion_frontier",
        "description": "Project the ready and blocked frontier of the complete 0..125 task dependency snapshot from an explicit set of completed task IDs. This is a pure projection, not a live-state mutation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "completed_task_ids": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_registry_verify",
        "description": "Read and reconstruct the complete KC144 registry archive, verify the outer SHA-256, parse every required member, and compare all declared counts without promoting authority.",
        "inputSchema": {
            "type": "object",
            "properties": {"deep": {"type": "boolean"}},
            "additionalProperties": False,
        },
    },
]

REGISTRY_RESOURCES = [
    {"uri": "athena://kc144/registry/status", "name": "KC144 Authoritative Registry Pack Status", "mimeType": "application/json"},
    {"uri": "athena://kc144/registry/catalog", "name": "KC144 Authoritative Registry Catalog", "mimeType": "application/json"},
    {"uri": "athena://kc144/registry/manifest", "name": "KC144 Embedded Crystal Manifest", "mimeType": "application/json"},
    {"uri": "athena://kc144/registry/verification", "name": "KC144 Registry Reconstruction Verification", "mimeType": "application/json"},
    {"uri": "athena://kc144/completion/frontier", "name": "KC144 Source-Bound Completion Frontier", "mimeType": "application/json"},
]

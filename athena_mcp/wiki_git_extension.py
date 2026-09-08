"""Expose the semantic repository's fixed Wiki compiler over MCP."""
from .wiki_git import ARTIFACT, GitWikiCompiler, OPERATIONS

TOOL = {
    "name": "athena_git_wiki_compile",
    "description": "Execute the fixed Internal Wiki compiler from the trusted configured Git repository at an explicit clean commit. Supports INIT, INGEST, QUERY, REINDEX and LINT through Gate0, static admission and the typed harness. Returns original receipts and mutation proposals without applying them. Runs repository Python in a fresh interpreter; does not establish Room admission or research gain.",
    "inputSchema": {
        "type": "object", "additionalProperties": False,
        "required": ["expected_git_head", "request"],
        "properties": {
            "expected_git_head": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
            "request": {
                "type": "object", "required": ["operation"], "additionalProperties": False,
                "properties": {
                    "operation": {"type": "string", "enum": list(OPERATIONS)},
                    "wiki": {"type": "object"}, "observed_at": {"type": "string"},
                    "query": {"type": "string"}, "limit": {"type": "integer"},
                    "pages": {"type": "array"}, "claims": {"type": "array"},
                    "sources": {"type": "array"}, "contradictions": {"type": "array"},
                    "source": {"type": "object"}, "existing": {"type": "object"},
                    "page_updates": {"type": "array"},
                    "snapshot_complete": {"type": "boolean"}, "index_exists": {"type": "boolean"},
                    "index_paths": {"type": "array"},
                    "expected_index_sha256": {"type": "string"},
                },
            },
        },
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
}

INGEST_TOOL = {
    'name':'athena_wiki_git_ingest',
    'description':'Compile an explicitly identified imported Drive observation into the committed semantic Git Wiki. Reads all committed Wiki pages and ledgers; returns an immutable source carrier plus guarded INGEST, REINDEX and LINT proposal. Preserves original source labels as data and emits retrieval claims only. Does not fetch Drive or apply writes.',
    'inputSchema':{'type':'object','additionalProperties':False,
                   'required':['expected_git_head','snapshot_id','page_id','document_id'],
                   'properties':{'expected_git_head':{'type':'string','pattern':'^[0-9a-f]{40}$'},
                                 'snapshot_id':{'type':'string','pattern':'^[0-9a-f]{64}$'},
                                 'document_id':{'type':'string','pattern':'^[0-9a-f]{64}$'},
                                 'page_id':{'type':'string','minLength':1}}},
    'annotations':{'readOnlyHint':True,'destructiveHint':False,'openWorldHint':False},
}


def install_git_wiki():
    from . import dispatch, protocol, unified_manifest, runtime_integrity_surface
    from .server import Server
    from .validate import validate
    if getattr(Server, "_git_wiki_installed", False):
        return
    if any(t["name"] in (TOOL["name"], INGEST_TOOL['name']) for t in protocol.TOOLS):
        raise ValueError("GIT_WIKI_TOOL_NAMESPACE_COLLISION")
    protocol.TOOLS.append(TOOL)
    protocol.TOOLS.append(INGEST_TOOL)
    previous_call = Server.call_tool

    def call(self, name, arguments):
        if name == INGEST_TOOL['name']:
            from .wiki_git_ingest import WikiGitIngest
            validate(INGEST_TOOL['inputSchema'], arguments)
            return WikiGitIngest(self).compile(**arguments)
        if name == TOOL["name"]:
            validate(TOOL["inputSchema"], arguments)
            return GitWikiCompiler(self.git).compile(**arguments)
        return previous_call(self, name, arguments)

    Server.call_tool = call
    previous_manifest = unified_manifest.build_unified_manifest

    def manifest(server):
        result = previous_manifest(server)
        result.setdefault("organs", {})["git_wiki"] = {
            "artifact": ARTIFACT, "tools": [TOOL["name"], INGEST_TOOL['name']],
            "source": "EXPLICIT_CLEAN_CONFIGURED_GIT_COMMIT",
            "mutation_apply": False, "room_admission": False,
            "process_isolation": "FRESH_PYTHON_INTERPRETER_NOT_OS_SANDBOX",
        }
        return result

    unified_manifest.build_unified_manifest = manifest
    dispatch.build_unified_manifest = manifest
    runtime_integrity_surface.build_unified_manifest = manifest
    Server._git_wiki_installed = True

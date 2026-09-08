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

STAGE_TOOL = {
    'name': 'athena_wiki_git_stage',
    'description': 'Materialize an explicitly reviewed Wiki ingestion plan as a verified local draft commit. Reconstructs the source-bound proposal, requires its reviewed plan digest, and fresh-lints the actual commit before creating a dedicated codex/wiki-draft branch. Preserves the configured checkout and index. Retries verify and reuse the same draft. Does not push, update shared branches, grant Room ownership or promote research claims.',
    'inputSchema': {'type': 'object', 'additionalProperties': False,
        'required': [*INGEST_TOOL['inputSchema']['required'], 'expected_plan_sha256'],
        'properties': {**INGEST_TOOL['inputSchema']['properties'],
                       'expected_plan_sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}}},
    'annotations': {'readOnlyHint': False, 'destructiveHint': False,
                    'idempotentHint': True, 'openWorldHint': False},
}

REVIEW_TOOL = {
    'name': 'athena_wiki_git_review',
    'description': 'List local Wiki draft refs or read one pinned to an exact commit, including after the configured checkout advances. READ verifies the internal binding, parent, complete changed-file plan, carrier and source identities without checkout, database import or repository-code execution. LIST is unverified inventory. Optionally returns the exact source carrier. Does not repeat semantic LINT, authenticate a producer, establish live Drive currentness or promote research claims.',
    'inputSchema': {'type': 'object', 'additionalProperties': False, 'required': ['action'],
        'properties': {'action': {'type': 'string', 'enum': ['LIST', 'READ']},
                       'ref': {'type': 'string', 'pattern': '^refs/heads/codex/wiki-draft-[0-9a-f]{32}$'},
                       'expected_commit': {'type': 'string', 'pattern': '^[0-9a-f]{40}$'},
                       'limit': {'type': 'integer', 'minimum': 1, 'maximum': 100},
                       'offset': {'type': 'integer', 'minimum': 0, 'maximum': 10000},
                       'include_source': {'type': 'boolean'}}},
    'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False},
}


QUERY_TOOL = {
    'name': 'athena_wiki_git_query',
    'description': 'Query the complete Wiki from an exact local Git data commit using the trusted compiler at the explicit clean configured HEAD. Reads and verifies committed source bytes itself; accepts no caller-supplied evidence collections. Returns both commit identities, complete input hashes and original semantic receipts, including HOLD and uncertainty. Executes only the configured compiler checkout; creates no data checkout. Does not import a database observation, authenticate a producer or establish currentness or research gain.',
    'inputSchema': {'type': 'object', 'additionalProperties': False,
        'required': ['expected_git_head', 'wiki_commit', 'query'],
        'properties': {'expected_git_head': {'type': 'string', 'pattern': '^[0-9a-f]{40}$'},
                       'wiki_commit': {'type': 'string', 'pattern': '^[0-9a-f]{40}$'},
                       'query': {'type': 'string', 'minLength': 1, 'maxLength': 4096},
                       'limit': {'type': 'integer', 'minimum': 1, 'maximum': 50}}},
    'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False},
}


def install_git_wiki():
    from . import dispatch, protocol, unified_manifest, runtime_integrity_surface
    from .server import Server
    from .validate import validate
    if getattr(Server, "_git_wiki_installed", False):
        return
    if any(t["name"] in (TOOL["name"], INGEST_TOOL['name'], STAGE_TOOL['name'], REVIEW_TOOL['name'], QUERY_TOOL['name']) for t in protocol.TOOLS):
        raise ValueError("GIT_WIKI_TOOL_NAMESPACE_COLLISION")
    protocol.TOOLS.append(TOOL)
    protocol.TOOLS.append(INGEST_TOOL)
    protocol.TOOLS.append(STAGE_TOOL)
    protocol.TOOLS.append(REVIEW_TOOL)
    protocol.TOOLS.append(QUERY_TOOL)
    previous_call = Server.call_tool

    def call(self, name, arguments):
        if name == QUERY_TOOL['name']:
            from .wiki_git_query import WikiGitQuery
            validate(QUERY_TOOL['inputSchema'], arguments)
            return WikiGitQuery(self).query(**arguments)
        if name == REVIEW_TOOL['name']:
            from .wiki_git_review import WikiGitReview
            validate(REVIEW_TOOL['inputSchema'], arguments)
            return WikiGitReview(self).review(**arguments)
        if name == STAGE_TOOL['name']:
            from .wiki_git_draft import WikiGitDraft
            validate(STAGE_TOOL['inputSchema'], arguments)
            return WikiGitDraft(self).stage(**arguments)
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
            "artifact": ARTIFACT, "tools": [TOOL["name"], INGEST_TOOL['name'], STAGE_TOOL['name'], REVIEW_TOOL['name'], QUERY_TOOL['name']],
            "source": "EXPLICIT_CLEAN_CONFIGURED_GIT_COMMIT",
            "mutation_apply": True, "mutation_scope": "LOCAL_DRAFT_REF_ONLY",
            "shared_branch_apply": False, "push": False, "room_admission": False,
            "process_isolation": "FRESH_PYTHON_INTERPRETER_NOT_OS_SANDBOX",
            "historical_draft_review": "COMMITTED_BYTES_WITHOUT_CHECKOUT_OR_DATABASE",
            "committed_wiki_query": "EXPLICIT_DATA_COMMIT_WITH_CONFIGURED_TRUSTED_COMPILER",
        }
        return result

    unified_manifest.build_unified_manifest = manifest
    dispatch.build_unified_manifest = manifest
    runtime_integrity_surface.build_unified_manifest = manifest
    Server._git_wiki_installed = True

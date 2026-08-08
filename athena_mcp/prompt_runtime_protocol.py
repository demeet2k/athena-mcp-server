PROMPT_RUNTIME_TOOLS = [
    {
        "name": "athena_prompt_hydrate",
        "description": (
            "Hydrate the configured Athena Git prompt brain at one exact clean HEAD. Returns profile, deterministic task-sensitive module selection, "
            "per-body digests, revision-bound source capsule, explicit frontier refs, matching scoped overlays and prompt/runtime changes since an optional prior HEAD. "
            "Fails explicitly when ATHENA_GIT_ROOT, manifest bodies, dependency/order laws or clean HEAD binding are unavailable."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "minLength": 1},
                "scope": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
                "task": {"type": "string", "minLength": 1},
                "include_text": {"type": "boolean"},
                "since_git_head": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_compile",
        "description": (
            "Compile a deterministic repository prompt addendum from profile/active modules + mandatory modules + task-selector matches + dependency closure, "
            "then strict unique order -> policy/modules -> applicable ACTIVE_SCOPED overlays. The result includes exact Git HEAD, selection reasons, "
            "frontier refs, stack/source-capsule digests and authority ceiling. An optional task overlay is ephemeral and never written."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "minLength": 1},
                "scope": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
                "task": {"type": "string", "minLength": 1},
                "task_overlay": {"type": "string", "minLength": 1},
                "since_git_head": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_freshness",
        "description": (
            "Compare a caller's last hydrated Git HEAD with the current clean Athena brain HEAD. Returns ancestry relation, material prompt/frontier file changes, "
            "affected scope and a typed rehydration requirement. This is an invalidation detector only; it performs no fetch, mutation, push or promotion."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["last_git_head"],
            "properties": {
                "last_git_head": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_propose",
        "description": (
            "Create an immutable CANDIDATE prompt module plus append-only PROMPT_PROPOSAL event on a local Git descendant. "
            "Requires exact expected HEAD, measured defect/effect contract, metrics, tests and rollback. Proposal never activates or promotes itself."
        ),
        "inputSchema": {
            "type": "object",
            "required": [
                "expected_git_head", "module_id", "version", "scope", "content", "defect", "expected_effect", "metrics", "tests", "rollback"
            ],
            "properties": {
                "expected_git_head": {"type": "string", "minLength": 1},
                "module_id": {"type": "string", "minLength": 1},
                "version": {"type": "string", "minLength": 1},
                "scope": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True},
                "content": {"type": "string", "minLength": 1},
                "defect": {"type": "string", "minLength": 1},
                "expected_effect": {"type": "string", "minLength": 1},
                "metrics": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True},
                "tests": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True},
                "rollback": {"type": "string", "minLength": 1},
                "depends_on": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
                "triggers": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
                "actor": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_experiment",
        "description": (
            "Append a prompt experiment record and PROMPT_TEST event at exact Git HEAD. PLANNED/RUNNING records may not masquerade as observations; "
            "PASSED/FAILED/INCONCLUSIVE require explicit observed rows and an execution witness. The active/canonical prompt state is not mutated."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["expected_git_head", "experiment_id", "candidate_path", "hypothesis", "protocol", "result_status"],
            "properties": {
                "expected_git_head": {"type": "string", "minLength": 1},
                "experiment_id": {"type": "string", "minLength": 1},
                "candidate_path": {"type": "string", "minLength": 1},
                "hypothesis": {"type": "string", "minLength": 1},
                "protocol": {"type": "object", "minProperties": 1},
                "result_status": {"enum": ["PLANNED", "RUNNING", "PASSED", "FAILED", "INCONCLUSIVE"]},
                "observations": {"type": "array", "items": {"type": "object"}},
                "witness": {"type": "object"},
                "actor": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_activate",
        "description": (
            "Activate a tested candidate only within an explicit scope. Requires exact HEAD, PASSED witnessed experiment refs and an ACTIVATE_SCOPED authority witness. "
            "The mutation changes only prompts/state/ACTIVE.json; ACTIVE_SCOPED remains non-canonical."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["expected_git_head", "candidate_path", "scope", "experiment_refs", "witness"],
            "properties": {
                "expected_git_head": {"type": "string", "minLength": 1},
                "candidate_path": {"type": "string", "minLength": 1},
                "scope": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True},
                "experiment_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True},
                "witness": {
                    "type": "object",
                    "required": ["authority", "decision", "approved_by"],
                    "properties": {
                        "authority": {"type": "string", "minLength": 1},
                        "decision": {"const": "ACTIVATE_SCOPED"},
                        "approved_by": {"type": "string", "minLength": 1},
                    },
                    "additionalProperties": True,
                },
                "expires_at": {"type": "string", "minLength": 1},
                "actor": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_prompt_promote",
        "description": (
            "Promote a candidate into an existing canonical repository module under exact Git-head and candidate-base CAS. "
            "Requires PASSED witnessed experiments, evidence refs, explicit PROMOTE authority witness and rollback plan. Candidate history is preserved; host authority is unchanged."
        ),
        "inputSchema": {
            "type": "object",
            "required": [
                "expected_git_head", "candidate_path", "target_module_id", "experiment_refs", "evidence_refs", "witness"
            ],
            "properties": {
                "expected_git_head": {"type": "string", "minLength": 1},
                "candidate_path": {"type": "string", "minLength": 1},
                "target_module_id": {"type": "string", "minLength": 1},
                "experiment_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True},
                "evidence_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True},
                "witness": {
                    "type": "object",
                    "required": ["authority", "decision", "approved_by"],
                    "properties": {
                        "authority": {"type": "string", "minLength": 1},
                        "decision": {"const": "PROMOTE"},
                        "approved_by": {"type": "string", "minLength": 1},
                    },
                    "additionalProperties": True,
                },
                "actor": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
]

PROMPT_RUNTIME_TOOL_NAMES = {tool["name"] for tool in PROMPT_RUNTIME_TOOLS}
PROMPT_RUNTIME_RESOURCE = {
    "uri": "athena://prompt/runtime",
    "name": "ATHENA Git-Governed Prompt Runtime V1",
    "mimeType": "application/json",
}

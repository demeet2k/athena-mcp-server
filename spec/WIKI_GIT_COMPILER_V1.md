# Git Wiki compiler through MCP

`athena_git_wiki_compile` connects the configured semantic Git repository to
the existing MCP server. It composes with the five local Wiki memory tools.

The memory tools preserve a source observation. This compiler runs the
repository's declared Internal Wiki interface against public JSON supplied by
the caller. There is no automatic conversion of Drive labels into Git claims,
and no automatic application of the returned mutation proposals.

## Call

1. Read `athena_git_status` and select the intended exact commit. The configured
   repository must be trusted and clean, including untracked files.
2. Follow that repository's `TOOLS/KC144/GID027_R03C03_INTERNAL_WIKI_V1/SKILL.md`
   and schema for the selected operation. Supply the metadata snapshot needed
   by QUERY/LINT/REINDEX. INGEST requires an independently verified, immutable
   raw source and current collision/replacement information.
3. Call the compiler with `expected_git_head` and `request`. The commit must be
   the full 40-character lowercase Git object ID, not a branch name.
4. Inspect `execution_receipt` and `wiki_standing`. A completed invocation can
   contain a Wiki HOLD or REVIEW. Lexical rank is not truth or canonicality.
5. Apply a proposed change only through an explicitly authorized write workflow
   with its expected digests, then reindex, lint and verify the affected files.

Request shape, with the actual commit substituted for the placeholder:

```json
{
  "expected_git_head": "<40-character configured Git commit>",
  "request": {
    "operation": "QUERY",
    "query": "replication",
    "pages": [],
    "sources": [],
    "claims": []
  }
}
```

An empty snapshot does not retrieve the repository automatically and should
return the Wiki's missing-evidence HOLD. Supported operations are INIT, INGEST,
QUERY, REINDEX and LINT. INIT can compile a separate scoped scaffold without
writing it. The request cannot select a module, function, command or harness.

## Execution and evidence

The adapter launches a fresh Python interpreter with `-I -B`, compiles Gate0,
validates static entrance admission and calls `RepositorySkillExecutor.execute`
with the fixed `ATHENA.HARNESS.INTERNAL.WIKI.V1` harness. This preserves the
repository's source-binding, ABI, state-projection and runtime-hold checks.
The request is passed as JSON through stdin, never interpolated into Python or
shell code. The response binds the request SHA-256, Git commit and tree to the
original receipts. Request/response limits are 1/4 million bytes; execution has
a 180-second timeout. The checkout is checked before and after execution.

The configured Git repository is executable trusted code. A fresh interpreter
is not an OS security sandbox. The adapter does not apply Wiki plans or grant
Room, scheduling, promotion or external mutation authority. Static admission
does not establish an actual Room check-in. Research gain remains UNKNOWN.

The clean-checkout requirement prevents a dirty implementation from being
reported as its committed source. It is not an atomic lock against an external
writer; use an isolated checkout and avoid concurrent mutation during a call.

## Reproduction

```text
python -m unittest tests.test_wiki_git tests.test_wiki_memory -v
python scripts/verify_wiki_git_mcp.py --semantic-root PATH --expected-head COMMIT
```

The real integration replay checks scoped INIT, historical hypothesis versus
current UNK, and an unanswered query through fresh MCP and compiler processes.
Its claim fixtures are synthetic test data, not research evidence. Linux and
Windows CI pin semantic repository commit
`84960d027ff06f85de9f62af1a2da000cc2824c6`, the tested repair candidate in Athena
PR 3596. Runtime smoke and promotion qualification wait for this integration
job. This fixture pin does not claim that the semantic candidate is merged.

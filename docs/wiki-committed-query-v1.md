# Query a committed Wiki

`athena_wiki_git_query` loads the complete Wiki at an explicit local data commit
and runs QUERY through the trusted compiler at the clean configured HEAD.
Callers supply `expected_git_head`, `wiki_commit`, `query`, and optionally
`limit` (1–50; default 12). Commit identifiers must be full 40-character SHA-1
IDs. Query text must be nonblank and at most 4,096 characters.

The two commits have different roles. `expected_git_head` selects the configured
compiler code. `wiki_commit` selects the evidence bytes. They may be equal, or
the data may come from a historical local draft whose checkout is no longer
current. No data checkout is created. Only the configured compiler checkout is
executed, through the existing fresh interpreter, Gate0, static admission and
typed Wiki executor. This requires trusting that configured repository; the
interpreter is not an OS sandbox.

The tool accepts no caller-supplied pages, claims, sources, contradictions,
schema, repository path or executable. It reads all committed Wiki pages and
ledgers, checks source hashes against raw bytes, and rejects missing schemas,
untyped pages, nonregular files and malformed snapshots. Git replacement objects
cannot substitute the evidence commit. The existing 8 MB snapshot, 1 MB compiler
request and 4 MB response bounds apply; oversized input fails explicitly.

The response contains `compiler_commit`, `wiki_commit`, `wiki_tree`, a complete
file `readset`, its canonical SHA-256 digest, inventory counts and the original
`compiler_receipt`. `standing` retains the executor's result; `wiki_standing`
retains the Wiki's retrieval judgment. The query result is under
`compiler_receipt.execution_receipt.outputs[0].result` when execution completes.
Its decision cone includes claim/source identities, historical relationships,
contradictions and evidence gaps. Limits can produce REVIEW rather than silently
claiming complete retrieval. No matching evidence produces HOLD.

Complete input loading does not prove the source claims true or the retrieval
answer sufficient. The tool preserves epistemic labels; it does not convert
HYP, UNK or retrieved statements into verified observations. Neither the commit
nor its readset authenticates a producer or establishes live Drive currentness.
Behavioral gain remains UNKNOWN. No observation is imported into the database,
and the configured checkout, index and refs are not changed.

Use `athena_wiki_git_review` when the question is whether a particular draft
matches its declared source/plan binding. Committed QUERY also accepts general
Wiki commits and does not assert that they were produced by the draft tool.
Use `athena_git_wiki_compile` for explicitly supplied hypothetical collections;
such a call does not carry this tool's committed-input provenance.

The public paired replay (`scripts/verify_wiki_git_ingest.py --stage`) exercises
historical querying from an advanced compiler checkout and an empty database.
Its synthetic uncertainty record is a transport fixture, not research evidence.

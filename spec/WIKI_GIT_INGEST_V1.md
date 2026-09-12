# Drive observation ingestion through MCP

`athena_wiki_git_ingest` connects persistent local Wiki observations to the
configured semantic Git Wiki. It takes four explicit identities:

```json
{
  "expected_git_head": "<40-character committed semantic HEAD>",
  "snapshot_id": "<64-character registry observation ID>",
  "page_id": "<registered semantic page ID>",
  "document_id": "<64-character imported document ID>"
}
```

Import the registry and document using the [memory protocol](../docs/wiki-memory-v1.md)
first. The bridge never fetches Drive or treats a local latest observation as
current remote state. Historical observations may be explicitly selected.

## Source and claim semantics

The immutable JSON carrier retains the exact document string, document identity
and source revision, registry observation binding, selected page records,
original epistemic labels, conflicts, changes, evidence references and unresolved
references. This is the complete bounded page context, not the complete registry.
Truncated context and missing imported documents are rejected.
The required compiler timestamp is the stored registry observation time. The
document's declared revision is preserved separately; the memory format does
not independently record or establish the document's live retrieval time.

Each emitted Git claim is RET: a report of what the registry says. Its statement
and tags retain the original claim ID and source EPI label. An imported OBS does
not become a new direct observation by the importing agent. A source UNK remains
visible as an unknown inside the reported assertion. Original relations remain
in the carrier; the bridge does not invent native claim contradictions or
supersession edges from ambiguous registry prose. It does not promote a research
claim, verify a source's conclusion or establish independent reproduction.

## Complete target state

The bridge reads the committed canonical `knowledge/WIKI.schema.json`, raw
carriers and Wiki tree at the expected clean HEAD. It verifies existing source
carrier hashes, decodes every typed Markdown page and retains existing ledgers.
An untyped Markdown page is an error rather than an omitted index entry. Git
symlinks, submodules, colliding case-insensitive paths and unsafe paths fail.
Existing binary raw carriers are hashed as bytes, without text conversion.

The fixed typed executor compiles INGEST, then REINDEX over the complete proposed
page set, then LINT over the complete proposed Wiki. Each call retains its original
Gate0, admission, execution and Wiki receipt. Non-READY Wiki results return HOLD
without a final mutation plan. The target checkout remains unchanged.

The result identifies the source observation, carrier digest, base file digests,
guarded final file replacements/creations, and plan digest. Existing pages remain
in the index. Immutable source carriers cannot be overwritten. Repeated compilation
of the same observation against the same committed base yields the same carrier
and plan, even after that local observation ceases to be latest. An observation
already present in the target Wiki is rejected explicitly; it is not appended twice.

## Application boundary

READY_PROPOSAL means the complete proposed Wiki passed the declared compiler and
lint checks. It is not an applied transaction. The bridge itself changes no Git
files, commits, branches, remote state, Room state, or schedules. An applying owner
must recheck the expected HEAD, complete readset, per-file preconditions and plan
digest, and satisfy the repository's write/coordination contract. Pre/post checks
are not an operating-system sandbox or an atomic multiwriter lock.

The fixed compiler executes trusted configured repository Python. Its interpreter
isolation is documented in [the compiler contract](WIKI_GIT_COMPILER_V1.md).
Committed Wiki bytes, carrier bytes and returned proposal bytes are bounded to
8 MB each; individual compiler requests retain the compiler's 1 MB input bound.

## Verification

Unit tests cover complete-index retention, exact source and original-label
preservation, historical replay, tampering, truncation, missing metadata, binary
carriers, symlink rejection, stale/dirty Git, unsafe writes and lint HOLD propagation.

`python scripts/verify_wiki_git_ingest.py --semantic-root <clean-checkout> --expected-head <commit>`
runs the real sequence through fresh MCP processes, applies the guarded result
only in a disposable clone, commits there, then reopens the committed Wiki and
lint-checks it through a fresh compiler process. The supplied checkout is verified
unchanged and nothing is pushed. The default source is explicitly synthetic.
Optional `--db`, `--snapshot-id`, `--page-id` and `--document-id` select a real
existing local observation; source outputs must remain within its access scope.

The paired workflow resides in the private semantic repository and reads a pinned
public runtime. The public runtime tests do not need or copy private source code.

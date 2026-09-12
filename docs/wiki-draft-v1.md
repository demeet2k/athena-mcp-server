# Local Wiki review commits

`athena_wiki_git_stage` turns a reviewed `athena_wiki_git_ingest` proposal into a durable local draft commit. It is useful when a successor needs to inspect the actual Git result after the producing process has ended.

First call `athena_wiki_git_ingest` with the explicit clean semantic commit, registry snapshot, page and document observation. Review its complete file plan and `plan_sha256`. Then call `athena_wiki_git_stage` with those same four identities and `expected_plan_sha256` set to the reviewed digest. The stage tool reconstructs the proposal; it accepts no caller-supplied files, commands, target directories or branch names.

The implementation checks the complete Wiki readset and every planned digest, builds the commit in an owned temporary clone, verifies the committed bytes and changed paths, and runs the fixed semantic compiler's LINT against that actual commit in a fresh interpreter. Only after READY does it import the immutable objects and create a dedicated `refs/heads/codex/wiki-draft-*` ref using an absent-ref compare-and-swap. The configured checkout, index, HEAD and current branch remain untouched by the operation.

The draft ref is derived from the full source/commit/plan binding. A retry reconstructs and verifies the same binding and actual commit, fresh-lints it, and reuses the existing ref. A different occupant, changed plan, source-head drift, failed lint, symbolic ref or competing ref writer causes an error without overwriting that writer. A failed publication can leave unreachable Git objects for normal Git maintenance, but does not publish a partial file tree. An external change after publication is reported separately from the immutable draft result.

The response contains the exact commit, base commit, local ref, changed paths, source identities and original committed-lint receipt. `mutation_scope` is `LOCAL_DRAFT_REF_ONLY`; `shared_state_applied`, `pushed` and `room_admission` remain false. Original source epistemic labels are preserved by ingestion and emitted claims remain RET. Research gain and live Drive currentness remain unknown/unverified.

Inspect a returned commit with `git show <commit>` or compare it with its returned base. Publishing a draft or applying it to a shared branch is a separate operation governed by the repository's current ownership and admission contract. This tool cannot claim ownership, contact another worker, push a branch or merge a change.

Validation uses independently constructed public fixtures for transaction behavior and private paired replay for the real semantic executor. A mocked compiler test alone is not evidence that the semantic pipeline accepted the actual draft commit.

# Prompt Runtime V1 — explicit shared Git transport

The prompt brain now has a circulation boundary distinct from hydration, compilation, experimentation and promotion.

## Separation law

`LOCAL_REPOSITORY_STATE != FRESH_SHARED_REMOTE_FRONTIER`.

Hydration and compilation remain network-silent local reads. A local mutation produces a local Git descendant only. Cross-agent delivery requires a later explicit publication operation and a fresh post-push equality witness.

## Tools

- `athena_prompt_remote_status`: observe local/tracking-ref relation; `fetch=true` is an explicit noninteractive, timeout-bounded fetch that never changes local HEAD.
- `athena_prompt_sync`: exact-head CAS + clean worktree + fresh fetch + fast-forward only + post-operation fresh-fetch verification.
- `athena_prompt_publish`: exact-head CAS + clean worktree + fresh remote ancestry proof + ordinary non-force push + post-push fresh-fetch equality.

## Fail-closed states

Transport holds on:

- disabled or invalid Git root;
- detached HEAD;
- invalid remote identifier;
- missing remote or remote branch;
- dirty worktree;
- stale expected local HEAD;
- failed or timed-out fetch;
- local-ahead state during sync;
- local-behind state during publish;
- divergence;
- failed fast-forward;
- failed push;
- failed post-operation verification.

No tool performs reset, rebase, force push, automatic merge, automatic branch creation, automatic publication after mutation, or implicit fetch during hydration/compilation.

## Concurrency

Fetch, fast-forward and publish use the same repository-local prompt-runtime lock as prompt mutations. Exact-head CAS is rechecked around network transitions. This coordinates MCP writers in one checkout while still treating unrelated external processes as possible stale-head causes.

## Remote-name and process hardening

Remote identifiers are constrained to a conservative name grammar. Git network subprocesses run without terminal credential prompts, with Git Credential Manager interaction disabled and a fixed timeout. Arguments are never evaluated through a shell.

## Acceptance

The regression suite creates one bare Git remote and two independent MCP instances/checkouts. It proves:

1. hydration does not silently receive sibling commits;
2. explicit sync fast-forwards and verifies shared equality;
3. a prompt proposal remains local before publication;
4. explicit publication makes the exact candidate commit remotely durable;
5. a sibling can explicitly sync and reconstruct that candidate;
6. divergence holds without merge, reset or push;
7. failed fetch, dirty worktree, stale expected head and hostile remote syntax fail closed.

## Authority boundary

`REMOTE_EQUALITY` is a delivery witness, not proof that the delivered content is correct, canonical, deployed or empirically true. Candidate/experiment/activation/promotion gates remain independent.

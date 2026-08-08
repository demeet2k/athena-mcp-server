# ATHENA Prompt Runtime V1 — executable Git/MCP bridge

## Purpose

The Athena semantic repository contains a modular prompt constitution; the MCP repository contains the executable nervous system. This implementation makes that relationship operational without collapsing their authority or identity:

`ATHENA semantic Git brain != MCP runtime != host instruction authority`.

The runtime operates only on the configured local `ATHENA_GIT_ROOT` checkout. It never fetches arbitrary repositories, pushes branches, deploys code, rewrites host instructions, or self-promotes a prompt candidate.

## Composition

The read path is deterministic and exact-head bound:

1. require a clean Git checkout;
2. read `prompts/PROMPT.manifest.json` and verify `ATHENA.PROMPT.RUNTIME.V1`;
3. read active state and select the active or explicitly requested profile;
4. add mandatory modules;
5. order bootstrap, policy and modules by manifest order;
6. include only non-expired `ACTIVE_SCOPED` overlays whose declared scope intersects the requested scope;
7. optionally append an ephemeral task overlay;
8. re-read HEAD and reject if it moved;
9. emit per-body SHA-256 digests, a sealed source capsule, stack digest and compiled digest.

Every Git body is represented by `(path, exact HEAD, digest, byte length, role)`. Snippets or remembered summaries are not treated as source bodies.

## Tools

- `athena_prompt_hydrate`: exact-head profile/module/source reconstruction, with optional changed-file report since a prior head.
- `athena_prompt_compile`: deterministic repository addendum with explicit authority ceiling.
- `athena_prompt_propose`: immutable candidate and append-only proposal event under Git-head CAS.
- `athena_prompt_experiment`: append-only planned or observed experiment record; observed outcomes require a witness.
- `athena_prompt_activate`: scoped activation after passed witnessed experiments; only `prompts/state/ACTIVE.json` changes.
- `athena_prompt_promote`: canonical repository-module replacement after exact-head CAS, candidate-base digest CAS, passed witnessed experiments, evidence, authority witness and rollback plan.

Resource: `athena://prompt/runtime`.

## Two-dimensional freshness

Mutations require:

`expected_git_head == current_git_head`.

Canonical promotion additionally requires:

`candidate.base_digest == current_target_digest`.

The first protects causal repository history. The second prevents a candidate tested against an old canonical module from overwriting a newer module merely because the caller refreshed HEAD.

## Mutation transaction

Prompt writes use a process lock, clean-worktree precondition, exact-head recheck, atomic file replacement, exact-path staging and one local Git commit. Failures restore touched files and unstage the attempted delta. The runtime never pushes; integration remains a branch/PR/CI decision.

## Epistemic and authority firewalls

- `PROMPT_RUNTIME != HOST_SYSTEM_PROMPT`
- `PROMPT_PROPOSAL != PROMPT_ACTIVATION`
- `ACTIVE_SCOPED != CANONICAL`
- `PLANNED_EXPERIMENT != OBSERVATION`
- `PASSED` requires observed rows plus an execution witness
- `GIT_STATE != WORLD_TRUTH`
- `LATEST_PROMPT != BEST_PROMPT`
- `PROMOTE != ERASE_HISTORY`

Candidate files and experiment records remain in Git after promotion. Promotion records previous and new digests, evidence, tests, witness and rollback plan in an append-only event.

## Acceptance witnesses

The test suite covers:

- tool/resource discoverability through the unified AOR composition surface;
- deterministic exact-head hydration and compilation;
- source-capsule body binding;
- explicit missing-manifest and dirty-worktree failure;
- proposal -> passed experiment -> scoped activation -> canonical promotion;
- activation changing only `ACTIVE.json`;
- stale expected HEAD rejection;
- witness-required experiment outcomes;
- stale candidate-base rejection;
- candidate-history preservation and no automatic push.

CI and Git ancestry—not this document—determine `TESTED` and `MERGED` state.

## Residual frontier

This runtime closes the prompt-stack execution gap. It does not by itself close the broader `NEXT_WORK_ORDER` mission compiler, provider backpressure, external Drive source-capsule ingestion, or live Charlie-free acceptance cohort. Those remain separate work orders and should consume this exact-head/source-capsule primitive rather than duplicate it.

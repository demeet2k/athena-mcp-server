# ATHENA Prompt Runtime V1 — executable Git brain expansion

Target brain contract: `demeet2k/Athena::prompts/PROMPT.manifest.json`.

The compact external seed is a bootloader. The configured `ATHENA_GIT_ROOT` checkout contains the mutable modular runtime addendum. V1 exposes tools to hydrate and compile that stack and to persist prompt candidates, experiments, scoped activation and canonical repository-policy promotion under exact Git-head compare-and-swap.

Authority boundary:

`repository prompt runtime < host platform/system/developer/current-user authority`.

Executable tools:

- `athena_prompt_hydrate`
- `athena_prompt_compile`
- `athena_prompt_propose`
- `athena_prompt_experiment`
- `athena_prompt_activate`
- `athena_prompt_promote`

Resource:

- `athena://prompt/runtime`

Hydration and compilation require a clean checkout and bind every complete source body to exact Git HEAD plus SHA-256 digest. The compiler emits a sealed source capsule, ordered stack digest and explicit authority ceiling. Optional task overlays are ephemeral and never written.

All writes are local versioned Git descendants and reject stale expected HEAD. Canonical promotion also rejects a stale candidate base digest. Prompt proposals and experiments never self-promote. `ACTIVE_SCOPED != CANONICAL`. Observed experiment outcomes require explicit observations and a witness. Canonical promotion requires passed witnessed experiments, evidence, rollback and an explicit promotion witness; candidate history remains.

The runtime does not fetch arbitrary remote repositories, push, deploy, mutate host instructions, or convert Git state into world truth. See `PROMPT_RUNTIME_V1_IMPLEMENTATION.md` for transaction, source-capsule and acceptance details.

# ATHENA Prompt Runtime V1 — executable Git brain expansion

Target brain contract: `demeet2k/Athena::prompts/PROMPT.manifest.json`.

The compact external seed is a bootloader. The configured `ATHENA_GIT_ROOT` checkout contains the mutable modular runtime addendum. V1 adds tools to hydrate/compile that stack and to persist prompt candidates, experiments and scoped activation under exact Git-head CAS.

Authority boundary:

`repository prompt runtime < host platform/system/developer/current-user authority`.

Tools planned in this implementation:

- `athena_prompt_hydrate`
- `athena_prompt_compile`
- `athena_prompt_propose`
- `athena_prompt_experiment`
- `athena_prompt_activate`
- `athena_prompt_promote`

All writes are versioned Git descendants and reject stale expected HEAD. Prompt proposals/experiments never self-promote. `ACTIVE_SCOPED != CANONICAL`. Canonical promotion requires explicit witness inputs and remains a repository operating-policy mutation only.

The runtime does not fetch arbitrary remote repositories: it operates only on the configured canonical `ATHENA_GIT_ROOT` checkout.
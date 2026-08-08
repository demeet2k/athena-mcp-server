# Prompt Runtime V1 — selection, dependency and freshness contract

This extension closes the cold-session reconstruction gap without turning the prompt brain into an automatic authority.

## Deterministic selection

For one exact clean Git head, profile and task string, module selection is:

1. profile modules, or active-state modules when no profile override is supplied;
2. all manifest modules marked `mandatory`;
3. modules whose declared `selectors` occur in the task string, case-insensitively;
4. recursive closure over declared `depends_on` edges;
5. cycle rejection;
6. strict ordering by integer `order`;
7. rejection of any two selected modules occupying the same order level.

The runtime returns selection reasons, matched selectors, dependency edges and the final order. It does not silently concatenate same-level laws.

## Frontier references

Goal, pressure and work-order references are returned only when explicitly declared by active state through `goal_refs`/`goals`, `pressure_refs`/`pressures`, or `work_refs`/`work_orders`/`workorder_refs`. Missing declarations return `UNDECLARED`; filenames are not promoted into authority by inference.

## Freshness and invalidation

`athena_prompt_freshness(last_git_head)` compares one caller-known head with the current clean checkout. It reports ancestry, changed prompt/frontier files, material categories, affected scope and whether rehydration is required.

Material paths include `AGENTS.md`, `prompts/`, `policies/`, `schemas/`, `registry/`, `goals/`, `pressures/`, `tasks/`, `workorders/` and `work_orders/`.

The tool is read-only. It does not fetch, mutate, push, activate or promote. A stale or diverged result is an invalidation signal for the consumer, not a claim that any later commit is automatically canonical.

## Cross-session acceptance

The regression suite uses two independent MCP server instances with separate SQLite state and one shared Git checkout. Both reconstruct the same stack at the same head. One session writes an authorized candidate commit; the other detects the exact Git delta and rehydrates without using hidden chat state.

## Firewalls retained

- `GIT_HEAD_CHANGE -> REHYDRATE`, not automatic trust.
- `TASK_SELECTOR_MATCH -> MODULE_CANDIDATE_SELECTION`, not higher authority.
- `DEPENDENCY_EDGE -> COMPOSITION_REQUIREMENT`, not empirical entailment.
- `FRONTIER_REF -> EXPLICIT POINTER`, not world truth.
- `FRESHNESS_DETECTION != MUTATION_AUTHORITY`.
- No automatic push or deployment path exists.

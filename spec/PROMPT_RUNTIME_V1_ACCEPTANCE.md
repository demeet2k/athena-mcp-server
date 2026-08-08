# Prompt Runtime V1 Acceptance

1. Configured Git brain with prompt manifest compiles deterministic ordered stack.
2. Compile output includes exact Git HEAD, profile, module paths and digest.
3. Missing Git root/manifest fails explicitly; no fake hydration.
4. Candidate proposal with current expected HEAD creates versioned Git commit.
5. Same proposal against stale HEAD is rejected.
6. Experiment records do not mutate active/canonical prompt state.
7. Scoped activation changes only `prompts/state/ACTIVE.json` and records overlay scope/witness.
8. Canonical promotion requires explicit promotion witness and current HEAD; candidate history remains.
9. Host instruction authority is never represented as modified by repository operations.
10. Existing MCP tools/tests remain unaffected.
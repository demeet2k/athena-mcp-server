# Prompt Runtime Git Law

All prompt-runtime mutations use the same canonical Git freshness principle as semantic/session checkpointing:

`expected_git_head == current_git_head`.

Else reject `STALE_GIT_HEAD` and require rehydration/rebase/branch. Do not overwrite a newer prompt state from a stale compiled stack.

Prompt rollback is a new Git commit/revert, never historical erasure.
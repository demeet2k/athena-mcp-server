# Meta Machine Learning Game MCP integration

The authoritative 144-goal registry is maintained in `demeet2k/Athena` on branch `agent/athena-git-brain-v2` under `meta_ml_game/`.

Configure:

```bash
export ATHENA_META_ML_ROOT=/path/to/Athena
python MCP/athena_mcp_server_meta_ml.py
```

Installed tools:

- `meta_ml_list_goals`
- `meta_ml_next_quest`
- `meta_ml_goal`

Installed resources:

- `athena://meta-ml-game/v1`
- `athena://meta-ml-game/goals`

This is a read-only adapter. Experiment, policy, and promotion writes remain in the Athena control plane and require independent witnesses, safety/privacy gates, and rollback receipts. The adapter cannot change source truth, user authority, or foundation-model weights.

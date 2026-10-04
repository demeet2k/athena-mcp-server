# Local brain snapshot carrier proof

This optional script connects an explicitly pinned, clean Athenachka brain
checkout and offline snapshot to the existing MCP JSON-RPC Wiki tool and a
clean pinned Athena compiler checkout. It executes only the fixed QUERY
harness; it adds no scheduler, authenticated broker, Room admission or source
promotion. Brain snapshot digests are not MCP WikiMemory snapshot IDs.

Prepare an operator-controlled JSON specification outside the repository with
`brain_root`, `brain_head`, `mcp_root`, `mcp_head`, `athena_root`, `athena_head`,
`snapshot_root`, `snapshot_digest`, `state_root`, `query` and `observed_at`.
The date is the local retrieval observation time; all original source metadata
remain inside the preserved answer. Roots identify trusted Python checkouts;
`-I -B` interpreter isolation is not an operating-system sandbox.

    python -I -B scripts/brain_local_slice.py run --spec /private/spec.json --directory /private/new-receipt

Keep the returned task and receipt SHA-256 values in trusted operator storage.
Cold reconstruction requires these external anchors, not hashes recalculated
from potentially changed receipt files:

    python -I -B scripts/brain_local_slice.py reconstruct --directory /private/new-receipt --task-digest TASK_SHA256 --receipt-digest RECEIPT_SHA256

The first invocation durably saves the source snapshot, raw brain answer,
typed task, raw JSON-RPC request before execution, raw result and verified
receipt. The entire answer is retained as one immutable RET source carrier;
all nested conflicts, holds and inert source instructions survive unchanged.
Every tracked MCP source byte plus new Python modules is recorded; clean
ancestor Git trees and their Python readsets bind brain and Athena code.

Reconstruction loads saved source bytes into another fresh brain interpreter,
rebuilds the projection, verifies exact native claim/source and executor route,
and returns without invoking the MCP handler. An incomplete PENDING record
holds for operator reconciliation and never triggers automatic execution.
Replay prevents another handler call within the same saved receipt directory.
A new directory starts a new query execution; this slice provides no global
duplicate registry or exactly-once guarantee across directories.
These hashes provide integrity relative to trusted external anchors; they are
not producer signatures. Keep private snapshots and receipts in authorized
local/private storage. Public tests use synthetic source data only.

Output streams share an enforced 4 MB budget and Athena execution has a
180-second timeout; brain output has a 500 KB budget and 30-second timeout.
The supervisor kills and reaps the direct worker, not an arbitrary descendant
process tree. Snapshot copying is capped at 8 MB before allocation.

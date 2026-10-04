# Reproduce the bounded local Athena route

This runs an offline source query through a typed task, an MCP JSON-RPC tool call, Athena's existing repository skill executor, a verified receipt, and reconstruction in a fresh Python process. The supplied fixture is explicitly synthetic; its nested claim is `SIM`, and the retrieved answer carrier is `RET`. Successful execution verifies the route and receipt, not the truth of a scientific claim or admission of a worker.

## Exact source pins

| Checkout | Commit | Review branch |
|---|---|---|
| AthenachkaCollective/athenachka-brain | `9d46dafb8d17a5afaae31fd6eb9501a70fa43867` | [existing PR 1](https://github.com/AthenachkaCollective/athenachka-brain/pull/1) |
| demeet2k/athena-mcp-server | explicit `$McpHead` delivery commit | [draft PR 394](https://github.com/demeet2k/athena-mcp-server/pull/394) |
| demeet2k/Athena | `32e7eb9b8da14987bc37dc1af62a126b6c92abe5` | main at qualification |

The adapter baseline is `cacc660071da1c9ba5513b950f94742563f0b13a`; the delivery commit containing this runbook and example must be supplied separately as `$McpHead` from the final qualification report. The helper validates that immutable SHA before imports or writes. Fetching the PR only obtains commits; it does not authorize executing a mutable branch head.

The adapter baseline's [exact pinned CI](https://github.com/demeet2k/athena-mcp-server/actions/runs/37225545058) passed Linux and Windows tests, source canary, and release qualification; publication was skipped. The integration qualification also passed cold replay and missing-source, stale-state, conflict-preservation, tamper and duplicate-directory checks. The brain and Athena pins remain fixed as other repair branches evolve; the MCP delivery pin is recorded in the generated spec and task anchors.

## Setup (PowerShell, Python 3.12, Git)

Use a new directory. Access to the private brain repository must already be authorized. These commands do not create credentials. The helper is checked into `examples/athena_local_demo.py`; adjust the initial path and immutable delivery SHA. All three Python paths used here are standard-library only; no GPU training, service deployment, or background daemon is needed.

```powershell
$RouteRoot = 'C:\AthenaLocalRoute'
$McpHead = '<exact published delivery SHA from the qualification report>'
if ($McpHead -cnotmatch '^[0-9a-f]{40}$') { throw 'Supply an immutable full MCP delivery SHA' }
New-Item -ItemType Directory -Path $RouteRoot -ErrorAction Stop
Set-Location $RouteRoot
python --version # verified environment: Python 3.12
python -c "import sys; assert sys.version_info[:2] == (3, 12), 'Use Python 3.12 for this qualification'"
if ($LASTEXITCODE -ne 0) { throw 'Python version check failed' }
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }
$Python = Join-Path $RouteRoot '.venv\Scripts\python.exe'
function Invoke-GitChecked { & git @args; if ($LASTEXITCODE -ne 0) { throw 'Git command failed' } }

Invoke-GitChecked clone https://github.com/AthenachkaCollective/athenachka-brain.git brain
Invoke-GitChecked -C brain fetch origin refs/pull/1/head
Invoke-GitChecked -C brain checkout --detach 9d46dafb8d17a5afaae31fd6eb9501a70fa43867
Invoke-GitChecked clone https://github.com/demeet2k/athena-mcp-server.git mcp
Invoke-GitChecked -C mcp fetch origin refs/pull/394/head
Invoke-GitChecked -C mcp checkout --detach $McpHead
Invoke-GitChecked clone https://github.com/demeet2k/Athena.git athena
Invoke-GitChecked -C athena checkout --detach 32e7eb9b8da14987bc37dc1af62a126b6c92abe5

Invoke-GitChecked -C brain rev-parse HEAD
Invoke-GitChecked -C mcp rev-parse HEAD
Invoke-GitChecked -C athena rev-parse HEAD
Invoke-GitChecked -C brain status --porcelain
Invoke-GitChecked -C mcp status --porcelain
Invoke-GitChecked -C athena status --porcelain
```

Stop if a command fails, a pin differs, or tracked source has edits. Do not force/reset an existing checkout. The route itself validates the exact heads and relevant source bytes.

The helper uses the equivalent timestamp `2026-10-03T20:00:00-04:00` for the task carrier because the pinned Athena Wiki configuration normalizes timestamps to that timezone. The capture retains `2026-10-04T00:00:00Z`. This avoids a representation mismatch in the byte-exact receipt verifier; it does not change the observation instant.

## Execute once, then reconstruct

```powershell
& $Python -I -B (Join-Path $RouteRoot 'mcp\examples\athena_local_demo.py') `
  --brain (Join-Path $RouteRoot 'brain') `
  --mcp (Join-Path $RouteRoot 'mcp') --mcp-head $McpHead `
  --athena (Join-Path $RouteRoot 'athena') `
  --output (Join-Path $RouteRoot 'demo')
if ($LASTEXITCODE -ne 0) { throw 'Fixture creation failed' }

$Slice = Join-Path $RouteRoot 'mcp\scripts\brain_local_slice.py'
$Receipt = Join-Path $RouteRoot 'demo\receipt'
$RunJson = & $Python -I -B $Slice run `
  --spec (Join-Path $RouteRoot 'demo\spec.json') --directory $Receipt
if ($LASTEXITCODE -ne 0) { throw 'Route failed; retain the directory for diagnosis' }
$RunJson
$Run = $RunJson | ConvertFrom-Json
# Keep these anchors outside the receipt directory, in storage you trust.
$RunJson | Set-Content -Encoding utf8 (Join-Path $RouteRoot 'demo-anchors.json')

& $Python -I -B $Slice reconstruct --directory $Receipt `
  --task-digest $Run.task_sha256 --receipt-digest $Run.receipt_sha256
if ($LASTEXITCODE -ne 0) { throw 'Reconstruction failed' }
```

Expected reconstruction: `standing=RECONSTRUCTED_FROM_SAVED_BYTES`, `handler_calls=0`, matching task/receipt hashes, and `promotion_eligible=false`. It reads saved artifacts and verifies source/code pins without executing the MCP handler again. Synthetic snapshot digest is `3a0172f1a4b115e3bae0a27a72d244adabe10e4f6fb6406af02a9fe364777dd8`; task and receipt hashes depend on your absolute paths.

The synthetic fixture was previously qualified on Python 3.12 using the fixed brain and Athena pins and the `cacc660` adapter baseline. That historical result does not qualify a newer delivery commit; require its exact-head CI, query execution and cold reconstruction results in the delivery report. A separate process reconstructed it with zero handler calls; the SQLite file's SHA-256 was identical before and after. A duplicate run against the same receipt directory exited with an error and left SQLite unchanged. The clone commands are setup instructions; the qualification used already authorized isolated checkouts rather than cloning the private repository again.

The receipt directory contains `task.json`, `brain-answer.json`, copied snapshot objects, JSON-RPC request/result, `receipt.json`, and the `PENDING` execution marker. Retain all of them. Running again against the same directory must fail before another handler call. If execution leaves `PENDING` without a receipt, treat the outcome as ambiguous and reconcile it manually; do not delete the marker or auto-retry.

## Existing source captures

For a real authorized offline capture, use the brain CLI `wiki-import --capture ... --output ...` and `wiki-verify --snapshot ... --digest ...`, with its `src` directory on the process import path. The capture must declare all five tables, exact headers, complete census/tails, and `revision_bound=false`. Set the route spec's `snapshot_root`, `snapshot_digest`, `state_root`, `query`, and `observed_at` from that verified observation; keep the six code root/head fields bound to the checkouts and immutable delivery SHA above. The spec accepts exactly these eleven string keys. Do not insert executable dependencies or an alternative tool name. Source holds/conflicts remain attached to the retrieved carrier and cannot authorize promotion.

```powershell
$PreviousPythonPath = $env:PYTHONPATH
$Capture = 'C:\Path\To\Authorized\capture.json'
$Snapshot = Join-Path $RouteRoot 'authorized-snapshot'
try {
  $env:PYTHONPATH = Join-Path $RouteRoot 'brain\src'
  $ImportedJson = & $Python -B -m athenachka_brain.cli wiki-import `
    --capture $Capture --output $Snapshot
  if ($LASTEXITCODE -ne 0) { throw 'Capture rejected' }
  $Imported = $ImportedJson | ConvertFrom-Json
  & $Python -B -m athenachka_brain.cli wiki-verify `
    --snapshot $Snapshot --digest $Imported.snapshot_digest
  if ($LASTEXITCODE -ne 0) { throw 'Snapshot rejected' }
} finally { $env:PYTHONPATH = $PreviousPythonPath }
```

The brain CLI uses the explicit process import path, so these two commands omit `-I`; the route and replay commands above retain it. The shell's previous import path is restored even on failure. This optional import requires your own authorized capture and is separate from the included synthetic qualification.

## Scope and limits

This is a local, bounded, read-only `QUERY`. It does not activate guild workers, establish federation-wide exactly-once delivery, provide producer signatures, or deploy four elemental services. Duplicate protection applies to the same receipt directory. Externally trusted digest anchors are required for reconstruction integrity. Python isolation flags are not an OS security sandbox.

The route bounds brain querying to 30 seconds/500 KB output and Athena execution to 180 seconds/4 MB output; snapshot copying is bounded at 8 MB. Direct worker timeout handling kills/reaps that worker, with no claim of descendant-process containment. No credentials, provider document identifiers, private source text, or internal planning notes are included in this demonstration.

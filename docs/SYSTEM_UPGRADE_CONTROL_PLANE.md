# ATHENA SYSTEM.UPGRADE.1 — Complete Runtime Control Plane

`SYSTEM.UPGRADE.1` is the persistent control plane for whole-organism upgrades in the canonical `HubServer`.

It closes the gap between:

- a large collection of individually tested organs;
- the current measured runtime state;
- the source-bound 126-task completion graph;
- exact-head CI and subprocess smoke witnesses;
- a replayable release decision.

## Terminal equation

```text
ATHENA_READY iff C & I & E & P & R & V & O & M & S & X are all PASS
```

The ten gates are measured from the live runtime:

| Gate | Meaning |
|---|---|
| C | required capabilities are discoverable |
| I | one composed runtime owns the organs and dispatch |
| E | the fail-closed developmental/upgrade loops are executable |
| P | consequential state persists in valid ledgers |
| R | stored decisions and state transitions replay |
| V | local validation procedures return witnessed PASS results |
| O | current accessible state and failures are observable |
| M | additive migration and critical schema preservation pass |
| S | surface, composition, schema and SQLite integrity all pass |
| X | typed cross-organ transports are live with their authority firewalls |

`READY_LOCAL` is necessary but not sufficient for release.

## Identities

```text
UPGRUN  persistent whole-system upgrade run
UPGEV   immutable upgrade state-transition receipt
RELCERT exact-head release qualification certificate
PROMRUN exact-head promotion receipt used by RELCERT
```

These identities do not collapse:

```text
UPGRUN != UPGEV != RELCERT != PROMRUN != Git commit != deployment
```

## Upgrade transaction

1. `athena_system_upgrade_plan` captures the measured local runtime, opens `UPGRUN`, imports only valid ordered completion witnesses, and computes the deterministic source-task frontier.
2. `athena_system_upgrade_observe` advances one ready source task. It requires:
   - `observed=true`;
   - a non-empty provenance `ref`;
   - a real `procedure`;
   - a concrete `observation`;
   - a PASS result;
   - the exact Git head when the observation declares or requires head binding.
3. Every mutation requires `expected_state_digest`. Stale writers fail closed.
4. `athena_system_upgrade_refresh` re-measures C/I/E/P/R/V/O/M/S/X without rewriting prior task witnesses.
5. `athena_system_upgrade_replay` verifies the complete event chain and final state digest. It does not re-simulate external work.

## Source completion

The embedded authoritative registry provides exactly 126 completion tasks (`TASK.000` through `TASK.125`).

Source completion and runtime readiness are deliberately separate:

- local gates may pass while historical/source tasks remain incomplete;
- a task cannot become complete because a module exists, a plan mentions it, or a graph reaches it;
- dependencies must already be complete;
- imported completion witnesses are processed in explicit order;
- rejected observations remain visible.

A release policy may require all 126 tasks, but that requirement is explicit rather than silently assumed.

## Exact-head release

`athena_system_release_certificate` produces `RELCERT`.

Qualification requires:

```text
local IC10 gates PASS
AND UPGRUN replay matches
AND expected Git head matches
AND optional source-completion policy passes
AND PROMOTION.1 qualifies CI and smoke on that same exact head
```

A qualified certificate means the exact repository head satisfied the encoded integration predicate. It does **not**:

- merge a pull request;
- deploy a service;
- establish empirical truth;
- prove unresolved QHUG semantics;
- turn model output into Y1 authority;
- grant production authority.

## MCP surface

### Tools

- `athena_system_upgrade_manifest`
- `athena_system_upgrade_plan`
- `athena_system_upgrade_state`
- `athena_system_upgrade_observe`
- `athena_system_upgrade_refresh`
- `athena_system_upgrade_replay`
- `athena_system_upgrade_recent`
- `athena_system_release_certificate`
- `athena_system_release_get`
- `athena_system_release_replay`
- `athena_system_release_recent`

### Resources

- `athena://system/upgrade`
- `athena://system/upgrade/frontier`
- `athena://system/release`

### Prompt

- `athena_system_upgrade`

## Persistence

The runtime owns three additive SQLite tables:

- `system_upgrade_runs`
- `system_upgrade_events`
- `system_release_certificates`

The schema is created idempotently when the canonical HubServer starts. Existing schema migrations remain non-destructive; the upgrade runtime separately verifies its own required tables and SQLite integrity.

## Runtime truth repair

The structural KC144 crystal retains its historical source snapshot. Current liveness is overlaid from actual tool/resource discovery.

This repairs the prior contradiction where live transports and governance organs remained labeled:

```text
REQUIRED_NOT_MECHANIZED
STAGED_SOURCE
HOLD
```

The measured layer now reports:

- live organs;
- live typed transports;
- missing tools/resources;
- local IC10 gate evidence;
- exact residual blockers;
- external promotion boundary.

The source snapshot is preserved rather than rewritten, so history and current truth remain distinct.

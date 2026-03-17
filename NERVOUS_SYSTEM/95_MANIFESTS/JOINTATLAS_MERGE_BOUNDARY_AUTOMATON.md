# JOINTATLAS MERGE BOUNDARY AUTOMATON

Date: `2026-03-13`
Truth: `OK`
Docs gate: `blocked-by-missing-credentials`
Version: `0.1.0`

## Purpose

Install the first typed collective adjudication membrane between packet transport and promotion law.

## Merge States

- `PROPOSED, BUNDLED, DISSENT_SURFACED, VERIFY_PENDING, GOVERNANCE_PENDING, DECIDED_COMMIT, DECIDED_DEFER_NEAR, DECIDED_DEFER_AMBIG, DECIDED_REFUSE, DECIDED_QUARANTINE`

## Lawful Destinations

- `COMMIT, DEFER_NEAR, DEFER_AMBIG, REFUSE, QUARANTINE_FAIL`

## Transition Graph

- `PROPOSED -> BUNDLED`: candidate_deltas_exist AND packet_ids_valid
- `BUNDLED -> DISSENT_SURFACED`: dissent_slots_materialized
- `DISSENT_SURFACED -> VERIFY_PENDING`: witness_refs_attached AND replay_refs_attached
- `VERIFY_PENDING -> GOVERNANCE_PENDING`: route_witness_sufficient AND replay_closure_sufficient
- `VERIFY_PENDING -> DECIDED_DEFER_NEAR`: bounded_residual AND continuation_seed_present
- `VERIFY_PENDING -> DECIDED_DEFER_AMBIG`: underdetermined_conflict AND continuation_seed_present
- `VERIFY_PENDING -> DECIDED_QUARANTINE`: hard_contradiction OR replay_divergence OR policy_breach
- `GOVERNANCE_PENDING -> DECIDED_COMMIT`: governance_approval_true AND ledger_appendable AND continuation_seed_present
- `GOVERNANCE_PENDING -> DECIDED_REFUSE`: governance_approval_false AND continuation_seed_present

## Artifact Requirements

- `PROPOSED`: `CommitteePack`
- `BUNDLED`: `CommitteePack`
- `DISSENT_SURFACED`: `CommitteePack, DissentPacket`
- `VERIFY_PENDING`: `CommitteePack, WitnessPack, ReplayPack`
- `GOVERNANCE_PENDING`: `CommitteePack, GovernanceApproval`
- `DECIDED_COMMIT`: `CommitteePack, DeltaPacket, MergeLedgerEntry, ContinuationSeed`
- `DECIDED_DEFER_NEAR`: `CommitteePack, NearPack, MergeLedgerEntry, ContinuationSeed`
- `DECIDED_DEFER_AMBIG`: `CommitteePack, AmbigPack, MergeLedgerEntry, ContinuationSeed`
- `DECIDED_REFUSE`: `CommitteePack, FailPack, MergeLedgerEntry, ContinuationSeed`
- `DECIDED_QUARANTINE`: `CommitteePack, FailPack, ConflictPacket, MergeLedgerEntry, ContinuationSeed`

## Witness Basis

- `Athena FLEET\FLEET_MYCELIUM_NETWORK\MIRRORS\LOCAL\F09_git_brain.md`
- `self_actualize\mycelium_brain\nervous_system\22_control_plane_grammar.md`
- `self_actualize\mycelium_brain\GLOBAL_EMERGENT_GUILD_HALL\06_GUILD_PROMOTION_PROTOCOL.md`
- `self_actualize\mycelium_brain\ATHENA TEMPLE\02_TEMPLE_GOVERNANCE_LAWS.md`
- `self_actualize\mycelium_brain\nervous_system\ledgers\LEDGER_2026-03-13_q39_contradiction_packets.md`
- `self_actualize\mycelium_brain\ATHENA TEMPLE\QUESTS\TQ06_INSTALL_THE_PACKET_FED_GUILDMASTER_COUPLING_LOOP.md`

## Restart Seed

`MotionConstitution_L1`

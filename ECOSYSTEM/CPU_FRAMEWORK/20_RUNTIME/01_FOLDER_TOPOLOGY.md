# FOLDER TOPOLOGY

## 1. Purpose

The CPU runtime needs a predictable folder map so documents, packets, wave outputs, and
governance records can be reopened without guesswork.

## 2. CPU Framework Topology

Recommended structure under this directory:

```text
CPU_FRAMEWORK/
  README.md
  00_FOUNDATIONS/
  10_MATH/
  20_RUNTIME/
  30_GOVERNANCE/
  40_EXEMPLARS/
  50_TEMPLATES/
```

Recommended future operational structure for live runs:

```text
CPU_RUNS/
  inbox/
  tasks/
  waves/
  packets/
  syntheses/
  ledgers/
  releases/
```

## 3. Folder Roles

- `inbox/`
  - raw task seeds waiting for compile
- `tasks/`
  - normalized kernel task packets
- `waves/`
  - one folder per expansion wave
- `packets/`
  - worker, archetype, pillar, and final packets
- `syntheses/`
  - contracted outputs promoted for reuse
- `ledgers/`
  - witness, ambiguity, and conflict logs
- `releases/`
  - publication-ready artifacts

## 4. Naming Rules

- task packet:
  - `TASK_<date>_<slug>.md`
- wave folder:
  - `WAVE_<task_id>_<stage>_<n>/`
- worker packet:
  - `PKT_<task_id>_<addr>.md`
- final synthesis:
  - `SYN_<task_id>.md`
- witness ledger:
  - `LEDGER_<task_id>.md`

## 5. Minimal Runtime Discipline

Every live task should generate at least:

1. one kernel task packet,
2. one wave ledger,
3. one final synthesis packet,
4. one witness summary.

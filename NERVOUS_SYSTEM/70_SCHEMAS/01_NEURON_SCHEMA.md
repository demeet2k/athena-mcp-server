# NEURON SCHEMA

## 1. Definition

A neuron file represents one promoted unit in the nervous system.

## 2. YAML Schema

```yaml
neuron_id: N-0001
title: short name
region: R1
source_paths:
  - absolute path
seed_claim: compressed core claim
operator_family:
  - route
  - compare
  - compress
  - expand
metro_lines:
  - Line A
status: AMBIG
witness:
  direct_support:
    - path
  replay_hint: short rerun note
next_synapses:
  - S-0001
```

## 3. Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `neuron_id` | string | yes | Unique ID: `N-XXXX` |
| `title` | string | yes | Short name for the neuron |
| `region` | string | yes | Primary corpus region (R1-R8) |
| `source_paths` | list | yes | Absolute paths to source documents |
| `seed_claim` | string | yes | Compressed core claim (1-2 sentences) |
| `operator_family` | list | yes | Operators this neuron performs |
| `metro_lines` | list | yes | Which metro lines carry this neuron |
| `status` | enum | yes | Truth class: OK, NEAR, AMBIG, FAIL |
| `witness` | object | yes | Evidence for the truth class |
| `next_synapses` | list | no | Synapse IDs connecting to other neurons |

## 4. Promotion Rule

Promote a source shard to a neuron only when:

1. its core claim can be compressed into one stable seed,
2. at least one metro line can carry it,
3. at least one synapse can be stated without guessing,
4. its witness surface is recorded.

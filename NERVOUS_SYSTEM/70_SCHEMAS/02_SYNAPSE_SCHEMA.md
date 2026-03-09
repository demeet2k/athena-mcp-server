# SYNAPSE SCHEMA

## 1. Definition

A synapse records a lawful relation between two neurons.

## 2. YAML Schema

```yaml
synapse_id: S-0001
src: N-0001
dst: N-0002
kind: REF | EQUIV | MIGRATE | DUAL | GEN | INST | IMPL | PROOF | CONFLICT
why_it_exists: short justification
metro_line: Line A
status: NEAR
witness:
  direct_support:
    - absolute path
  replay_hint: short rerun note
```

## 3. Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `synapse_id` | string | yes | Unique ID: `S-XXXX` |
| `src` | string | yes | Source neuron ID |
| `dst` | string | yes | Destination neuron ID |
| `kind` | enum | yes | Edge kind from closed basis K |
| `why_it_exists` | string | yes | Short justification |
| `metro_line` | string | yes | Primary metro line carrying this relation |
| `status` | enum | yes | Truth class: OK, NEAR, AMBIG, FAIL |
| `witness` | object | yes | Evidence for the relation |

## 4. Nervous-System Packet Rule

Every future nervous-system packet should include:

- target regions,
- chosen metro line,
- expected contraction target,
- truth class,
- witness summary.

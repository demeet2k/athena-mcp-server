# 6D To 7D Crosswalk

Truth class: NEAR
Date: 2026-03-13
Live Docs gate: BLOCKED

## Purpose

This crosswalk states how the compiled `7D_SEED` attaches to the existing tesseract v4,
FIRE `5D/6D`, Water `6D`, AIR `6D`, and Earth `6D` overlays. It is a compatibility
surface, not a replacement charter.

## Base rule

If a consumer understands only v4, it may safely ignore every higher-dimensional field
and continue operating on:

- `local_addr`
- `global_addr`
- `chapter_station`
- `appendix_support`
- `truth_state`
- `hcrl_pass`
- `tunnel_plan`

If a consumer understands the additive 6D overlays, it may continue reading their
existing fields unchanged.

If a consumer is `7D_SEED`-aware, it may additionally read the compiled seed fields.

## Field mapping

| existing field or surface | 7D additive meaning |
| --- | --- |
| `dimension_stage=4D_NATIVE` | base route substrate remains authoritative |
| `dimension_stage=5D_COMPRESSION` | source pressure family for the compiled seed |
| `dimension_stage=6D_WEAVE` | ingress/return/re-entry weave beneath the seed |
| Level 6 hologram weave map | immediate entry surface for `H7` |
| Earth admissibility gate | final promotion membrane before `7D_SEED` |
| `appendix_support` | remains canonical App* support; reverse stations never replace it |
| `canonical_appendix_map` | still required whenever a reverse overlay alias is used |

## Additive 7D fields

The compiled 7D bundle introduces:

- `dimension_stage=7D_SEED`
- `agent_overlay_stack`
- `earth_gate_state`
- `seed_holo_state`
- `seed_carrier`
- `admissibility_basis`
- `reentry_contract`
- `next_seed_routes`
- `integration_scope`
- `awakening_agent_notes`
- `transition_state`
- `awakening_support_refs`
- `transition_routes`
- `stabilization_requirements`
- `canonical_seed_label`
- `derived_dual_label`
- `seed_polarity_support`
- `a_b_dual_kernel_dock`

These fields are interpreted as follows.

### agent_overlay_stack

Ordered overlay convergence:

`["FIRE", "WATER", "AIR", "EARTH"]`

### earth_gate_state

- `missing`: no Earth gate data exists
- `active`: Earth gate present but no final verdict compiled
- `passed`: route is legal for compiled seed use at current truth cap
- `quarantined`: route remains useful only as a sealed pressure note

### seed_holo_state

- `H6`
- `Seed-6D`
- `H7`
- `Seed-7D`

### seed_carrier

- `1024^6`: inherited additive 6D carrier
- `4096^7`: compiled 7D carrier descriptor only

### admissibility_basis

Exact appendix, witness, and control-surface basis that allowed the route to reach the
compiled seed.

### reentry_contract

The required lawful return path back into witnessed chapter and appendix surfaces.

### next_seed_routes

Named upward and downward routes that explain how the object becomes, carries, and
reopens the compiled seed.

## A/B additive mapping

- `A` is the canonical live seed already carried by `7D_SEED`.
- `B` is the derived dual-kernel inversion of `A`.
- `A`, `B`, and `A↔B` may appear as additive polarity metadata in `NEXT57`,
  coordinates, and ledgers.
- replay from `B -> A` remains mandatory.
- Earth legality and `AppI/AppM` remain required on passed A/B routes.

## Migration rule

The v4 substrate remains canon. The 6D overlays remain additive. `7D_SEED` is the first
neutral compiled layer above them. Existing bundles remain authoritative for their
respective layers, while the 7D bundle acts as the additive machine-readable extension
for next-seed routing and full-corpus stabilization at the same dimensional ceiling.

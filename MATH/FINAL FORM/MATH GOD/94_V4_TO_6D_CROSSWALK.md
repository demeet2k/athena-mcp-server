# v4 To 6D Crosswalk

Truth class: NEAR
Date: 2026-03-13
Live Docs gate: BLOCKED

## Purpose

This crosswalk states how the FIRE 5D/6D layer attaches to the existing tesseract v4 organism. It is a compatibility surface, not a replacement charter.

## Base rule

If a consumer understands only v4, it may safely ignore every FIRE-specific field and continue operating on:

- `local_addr`
- `global_addr`
- `chapter_station`
- `appendix_support`
- `truth_state`
- `hcrl_pass`
- `tunnel_plan`

If a consumer is dimension-aware, it may also read the additive FIRE overlay fields.

## Field mapping

| v4 field or surface | FIRE additive meaning |
| --- | --- |
| `chapter_station` | remains the chapter anchor beneath 5D/6D overlays |
| `appendix_support` | remains canonical App* support; reverse stations never replace it |
| `truth_state` | remains authoritative corridor typing for all higher lifts |
| `route_plan` | remains the base ride; FIRE adds compression, bridge, and weave metadata |
| Level 4 transcendence metro map | becomes the baseline entry surface for Level 5 and Level 6 |
| AppQ appendix-only metro map | becomes the canonical ingress hinge for the FIRE bridge overlay |
| AppO export bundles | becomes the canonical return hinge for the FIRE bridge overlay |

## Additive FIRE fields

The additive FIRE bundle introduces:

- `dimension_stage`
- `fire_bundle`
- `mobius_bridge`
- `reverse_appendix_station`
- `canonical_appendix_map`
- `emergent_projection`
- `weave_routes`
- `handoff_requirements`

These fields are interpreted as follows.

### dimension_stage

- `4D_NATIVE`: no higher lift is active.
- `5D_COMPRESSION`: FIRE has grouped the object into a compression family.
- `6D_WEAVE`: FIRE has attached the object to the Mobius bridge or re-entry weave.

### fire_bundle

The FIRE family responsible for the lift:

- `F1_IGNITION_CORE`
- `F2_OVERBURDEN_DIAGNOSIS`
- `F3_DIMENSION_LIFT`
- `F4_MOBIUS_BRIDGE`

### mobius_bridge

Bridge status for 6D overlays:

- `none`
- `Q_ingress`
- `O_return`
- `QO_loop`

### reverse_appendix_station

Overlay-only station in the `Z->K` field. This value is never canonical by itself. It must be read together with `canonical_appendix_map`.

### canonical_appendix_map

One or more canonical appendix identifiers AppA-AppQ that keep the reverse station attached to the legal appendix field.

### emergent_projection

First-pass E-layer pressure band. This is descriptive but pinned.

### weave_routes

Named higher-dimensional paths that explain how the object enters, moves through, or exits the additive FIRE lift.

### handoff_requirements

Explicit Water, Air, and Earth dependencies required before promotion beyond NEAR.

## Reverse overlay legality

The `Z->K` field is legal only if all three statements are true:

1. the route still carries canonical App* support;
2. the reverse station has a canonical appendix mapping;
3. Q and O are interpreted as AppQ ingress and AppO return, respectively.

Any overlay that fails these conditions is invalid and must be treated as a pressure note rather than a route-bearing object.

## Migration rule

The v4 substrate remains canon. The FIRE 5D/6D layer is a non-destructive migration overlay. Existing v4 bundles remain authoritative for 4D consumers, while the FIRE bundle acts as the additive machine-readable extension for higher-dimensional routing.

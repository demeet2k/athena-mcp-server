# LP-57Omega R/Q/T Transfer Signature and Metro Witness Registry

This supplement freezes the first witness-bearing enrichment pass over the dense shell.

## Scope

- Raw shell records remain canonical for `P` and `S`.
- Only `R`, `Q`, and `T` receive explicit `Z* / AETHER / WitnessPtr / ReplayPtr` payloads in this pass.
- `R` records keep one logical row with `plus` and `minus` phase bindings; `Q` keeps a `spin` binding and `T` keeps an `antispin` binding.

## Registry Law

- Truth status: `NEAR-derived`
- Sigma path: `AppA -> AppI -> AppM`
- All operator-family bindings are pinned to the Flower lens and remain local-only while the docs gate is blocked: `60` phase bindings across `45` logical rows.
- Every enriched record keeps the legacy summary strings and now derives them from explicit `phase_bindings` and full field-level pointer payloads.
- `R` rows expose `plus` and `minus`; `Q` rows expose `spin`; `T` rows expose `antispin` with explicit hidden-pole and `Residual` slot law.

## Route Witness Anchors

- `R` records anchor to `03_METRO/00_core_metro_map.md :: Ch07<0012>`
- `Q` records anchor to `03_METRO/00_core_metro_map.md :: Ch08<0013>`
- `T` records anchor to `04_CHAPTERS/Ch11_0022_void_book_and_restart_token_tunneling.md`

## Canonical Runtime Surfaces

- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/14_rqt_transfer_signature_registry.json`
- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/15_rqt_transfer_signature_and_metro_witness.md`
- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/16_aether_witness_replay_pointer_registry.json`
- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/17_aether_witness_replay_pointer_witness.md`
- `ACTIVE_NERVOUS_SYSTEM/18_LP_57OMEGA_PROTOCOL/18_aether_witness_replay_pointer_schema.json`

The registry is supplements-facing documentation of the runtime shell object and is not part of the strict spine.

# A/B Dual-Kernel Crosswalk

Truth class: NEAR
Date: 2026-03-13
Live Docs gate: BLOCKED

## Purpose

This crosswalk states how the additive A/B dock attaches to the current `7D_SEED`,
`NEXT57`, and appendix-governed replay surfaces.

## Mapping

| surface | additive A/B meaning |
| --- | --- |
| `7D_SEED` bundle | `A` is the canonical live seed; `B` is the derived dual |
| `NEXT57` state | seed polarity support is exposed as `A`, `B`, `A↔B` |
| `NEXT57` prime protocol | the dual-kernel operator and replay law are exposed |
| coordinate registry | touched nodes may carry additive `polarity_state` metadata |
| ledger schema | entries may carry additive `polarity_state` metadata |
| Guild Hall tree | practical `A -> B` bridge / proof / replay dock |
| Temple tree | zero-point / aether / replay ratification dock |
| appendix legality | passed routes still require Earth gate plus `AppI/AppM` |

## Canonical references

- `A` source bundle: `atlas/math_7d_synthesis_seed_bundle.json`
- `B` dock bundle: `atlas/math_ab_dual_kernel_dock_bundle.json`
- `NEXT57` state: `self_actualize/next57_four_agent_corpus_cycle_state.json`
- `NEXT57` protocol: `self_actualize/next57_prime_loop_protocol.json`

## Additive field contract

The A/B dock introduces additive fields and metadata only:

- `canonical_seed_label`
- `derived_dual_label`
- `seed_polarity_support`
- `a_b_dual_kernel_dock`
- additive `polarity_state` metadata on coordinates and ledgers

Consumers that understand only v4 or pre-A/B 7D fields may ignore these additions and
continue operating on the existing canon surfaces unchanged.

## Replay and legality

- `A` remains the source seed.
- `B` may not act as an independent root.
- Replay from `B -> A` is mandatory.
- Earth legality is required where promotion occurs.
- `AppI` and `AppM` remain required support on passed A/B routes.
- `AppQ` and `AppO` remain overlay-only and do not become a new appendix namespace.

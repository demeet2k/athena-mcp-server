# AIR 6D Overlay Registry

AIR owns naming, topology, schema stability, and route legibility for the additive 6D layer.

## Registry tuple

`AIROverlay6D = (NSCoord, SigmaNode, SpinKernel, RotationFamily, DualKernel, CompressionCarrier, MobiusMode, HoloState, OverlayTruth, DocsGate)`

- `SigmaNode`: `Sigma01` through `Sigma15`
- `SpinKernel`: `SP+` or `SP-`
- `RotationFamily`: `R-SigmaNN`, `CR-SigmaNN`, `AR-SigmaNN`, or `ACR-SigmaNN`
- `DualKernel`: `Z0` or `AE0`
- `CompressionCarrier`: `4D+`
- `MobiusMode`: `M-FIX`, `M-CAR`, or `M-MUT`
- `HoloState`: `H6` or `Seed-6D`
- `OverlayTruth`: `{OK, NEAR, AMBIG, FAIL}`
- `DocsGate`: `BLOCKED` until OAuth material exists

## Registry laws

- Overlay labels never rename or replace `ChXX<dddd>...`, `AppA` through `AppP`, or `AppQ`.
- The same basis set, truth state, and docs-gate state must replay to the same overlay labels and appendix stack.
- `Q` docks only through `AppQ`.
- Reverse-field `O` is a transport alias only and may not be promoted into a canonical appendix identity.
- `AppA/AppB/AppC` own address and symmetry legality, `AppE/AppF/AppH` own transport and topology legality, and `AppI/AppM/AppN/AppQ` own truth, replay, seed, and ingress legality.

## Control surfaces consumed here

- `03_AIR/07_registryschemas.md`
- `03_AIR/15_distillation.md`
- `03_AIR/16_dimensionlift.md`
- `07_METRO_STACK/06_level_6_hologram_weave_map.md`
- `08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md`

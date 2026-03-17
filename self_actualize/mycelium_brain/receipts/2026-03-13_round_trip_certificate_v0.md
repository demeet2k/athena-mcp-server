# 2026-03-13 RoundTripCertificate v0

## Constitutional Law

A conversion is valid only if it preserves law or explicitly names the loss.

## Protected Invariant Bundle

- `gate, route_min, truth, overlay_debt, terminal_type, receipt_debt`
- required route minimum: `AppA, AppI, AppM`

## Governed Fronts

- `Q42` :: class=`law_equivalent` :: lawful=`True` :: transform=`automaton_to_wall_chart`
- `Q46` :: class=`law_equivalent` :: lawful=`True` :: transform=`sigil_to_schema`
- `TQ04` :: class=`exact` :: lawful=`True` :: transform=`schema_to_automaton`

## Transform Laws

- `myth_to_sigil` :: allowed=`law_equivalent`
- `sigil_to_schema` :: allowed=`exact, law_equivalent`
- `schema_to_automaton` :: allowed=`exact`
- `automaton_to_wall_chart` :: allowed=`law_equivalent`
- `pocket_card_or_poster` :: allowed=`residualized`

## Illegal Loss Tests

- `route_min_sigma_loss` :: Fail if AppA, AppI, or AppM drop out of the route minimum during conversion.
- `ambig_without_evidence_plan` :: Fail if AMBIG survives conversion without an EvidencePlan debt.
- `near_without_residual_ledger` :: Fail if NEAR survives conversion without a ResidualLedger debt.
- `ok_without_replay_or_witness` :: Fail if OK is claimed without replay and witness receipts.
- `publish_without_parity_or_appo` :: Fail if publish-class output lacks parity or AppO attestation.
- `semantic_change_without_migrate` :: Fail if semantic drift is declared without MIGRATE receipts.
- `corridor_widening_without_attestation` :: Fail if corridor widening occurs without attestation.

## Gate Honesty

- docs gate: `BLOCKED`
- local evidence only while OAuth files remain missing

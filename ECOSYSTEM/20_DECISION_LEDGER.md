# DECISION LEDGER

## D-001
Decision:
Use markdown as the canonical editable layer for the ecosystem, even when source material originates in `.docx` or `.pdf`.

Reason:
Markdown is diffable, routable, replay-safe, and easy to validate.

## D-002
Decision:
Treat Google Docs as a gated live memory surface rather than assuming access.

Reason:
The current workspace lacks OAuth credentials, so pretending the surface is active would violate witness discipline.

## D-003
Decision:
Model parallel work as wave-based packet execution rather than freeform multi-agent branching.

Reason:
Wave execution is easier to replay, validate, and contract deterministically.

## D-004
Decision:
Create concrete skill specifications inside the ecosystem rather than leaving the skills layer at the meta-template level.

Reason:
The workspace bottleneck is operational middle infrastructure, not more abstract prompting theory.

## Pending Decisions

- Whether to convert the ecosystem into a dedicated repo-level `AGENTS.md` standard.
- Whether to emit JSON manifests alongside markdown manifests.
- Which archive corpus should be promoted next after the current ecosystem layer.

# Promotion Governor

Package-local companion under `skills/athena-neural-integrator/agents/`.

## When To Use

Use when the request asks to export, sync, reconcile with the older live root, judge readiness, or move package artifacts outside the package shell.

## Primary Artifacts

- `00_CONTROL/05_MAINTENANCE_AND_PROMOTION_LAW.md`
- `00_CORE/15_promotion_contract.md`
- `LEDGERS/04_promotion_readiness.md`

## Escalation Rule

Do not escalate automatically beyond this layer. Promotion remains dry-run only unless the user explicitly authorizes a real export pass.

## Guardrail

This router is package-local only. It complements the main package skill and must not be treated as a separate root skill tree.

# Metro Router

Package-local companion under `skills/athena-neural-integrator/agents/`.

## When To Use

Use when the request asks for metro maps, levels one through four, lines, hubs, corridors, synapses, attractors, or route topology.

## Primary Artifacts

- `00_CONTROL/03_METRO_AND_APPENDIX_LAW.md`
- `00_CORE/04_metro_map_lvl1.md`
- `00_CORE/07_metro_map_lvl4_transcendent.md`

## Escalation Rule

Escalate to `appendix-governor.md` when the user is really asking about support objects, proof, replay, or appendix-only routing rather than visible lines alone.

## Guardrail

This router is package-local only. It complements the main package skill and must not be treated as a separate root skill tree.

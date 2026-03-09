# WAVE COMPILER

## 1. Purpose

The wave compiler converts one task seed into a 64-worker crystal and defines how those
workers are assigned, routed, and recombined.

## 2. Compile Depth

Default:

- `depth = 3`
- `workers = 4^3 = 64`

Optional extension:

- `depth = 4`
- `workers = 4^4 = 256`

The framework uses `64` as the standard productive wave because it maximizes coverage
without forcing unnecessary coordination cost.

## 3. Compile Algorithm

Algorithm 3.1 (Compile64).

Input:

- task seed `T`
- corpus slice `C`

Output:

- worker set `W64`

Procedure:

1. Create the kernel packet.
2. Generate four pillar packets: `E`, `W`, `F`, `A`.
3. Expand each pillar into four archetype packets.
4. Expand each archetype into four worker packets.
5. Assign each worker:
   - one source shard,
   - one extraction mode,
   - one witness obligation,
   - one contraction target.

## 4. Worker Packet Formula

Each worker packet is

`worker = (addr, shard, question, output_type, witness_rule, parent)`

Examples:

- `E-A-F`: build a feasible schema from a mapped novelty shard
- `W-F-A`: synthesize a high-energy connection into a usable map
- `A-E-W`: audit reality fit and rewrite it for continuity

## 5. Default Wave Types

The CPU uses four wave types:

1. `source wave`
   - read and index source cells
2. `pattern wave`
   - extract operators, structures, and recurring logic
3. `synthesis wave`
   - merge patterns into framework objects
4. `contraction wave`
   - decide what becomes canonical

## 6. Contraction Order

Workers contract in three passes:

1. workers -> archetypes,
2. archetypes -> pillars,
3. pillars -> kernel artifact.

Every pass must produce:

- retained outputs,
- discarded outputs,
- unresolved contradictions,
- next-seed candidates.

## 7. Cost Guardrail

The compiler should not expand beyond the point where

`expected_gain < coordination_cost`.

This makes the CPU adaptive instead of mechanically maximalist.

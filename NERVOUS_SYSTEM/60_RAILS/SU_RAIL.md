# SU RAIL (Sulfur)

## Role

The sulfur rail handles **commitment, decisive routing, and irreversible structure changes**. When the system must choose, cut, or finalize, traffic moves on the Su rail.

## Stations

| Order | Chapter | Station Code | Arc | Rot | ω |
|-------|---------|-------------|-----|-----|---|
| 1 | Ch01 - Kernel and Entry Law | `<0000>` | 0 | 0 | 0 |
| 2 | Ch06 - Documents-as-Theories | `<0011>` | 1 | 1 | 5 |
| 3 | Ch08 - Synchronization Calculus | `<0013>` | 2 | 2 | 7 |
| 4 | Ch10 - Multi-Lens Solution Construction | `<0021>` | 3 | 0 | 9 |
| 5 | Ch15 - CUT Architecture | `<0032>` | 4 | 1 | 14 |
| 6 | Ch17 - Deployment and Bounded Agency | `<0100>` | 5 | 2 | 16 |
| 7 | Ch19 - Convergence and Fixed Points | `<0102>` | 6 | 0 | 18 |

## Traffic Types

- Final draft commits
- Chapter order decisions
- Release locks
- Route freezes
- Architecture finalizations
- Deployment locks

## Rail Edges

```
Ch01<0000> -> Ch06<0011> -> Ch08<0013> -> Ch10<0021> -> Ch15<0032> -> Ch17<0100> -> Ch19<0102> -> Ch01<0000>
```

## Current Use

Use this rail when the system must choose, cut, or finalize.

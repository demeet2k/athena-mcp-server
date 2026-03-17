# Level 3 Metro Map - Deeper Neural Map

Level 3 maps families, swarm layers, chapter agents, and appendix governors as a neural manifold rather than a chapter list.

```mermaid
flowchart TB
FamVoid["Family Void/Collapse"] --> Ch04["Ch04"]
FamVoid --> Ch11
FamVoid --> Ch19
FamTransport["Family Transport/Runtime"] --> Ch07["Ch07"]
FamTransport --> Ch15
FamTransport --> Ch16
FamTransport --> Ch18
FamOrch["Family Live Orchestration"] --> Ch09["Ch09"]
FamOrch --> Ch20
FamOrch --> Ch21
FamGov["Family Civilization/Governance"] --> Ch17["Ch17"]
FamGov --> Ch18
FamGov --> Ch20
FamGov --> Ch21
Helix["Helical Engine"] --> Ch11
Helix --> Ch18
Helix --> Ch20
Helix --> Ch21
L0["L0 Leaf Readers"] --> L1["L1 Family Synths"] --> L2["L2 Chapter Weavers"] --> L3["L3 Appendix Governors"] --> L4["L4 Lane Mediators"] --> L5["L5 Collective Relay"] --> L6["L6 Council Mesh"] --> L7["L7 Civilization Kernel"]
L1 --> FamVoid
L1 --> FamTransport
L1 --> FamOrch
L1 --> FamGov
AppF["AppF Transport"]
AppG["AppG Control"]
AppI["AppI Corridors"]
AppM["AppM Replay"]
Ch11 --> AppF
Ch11 --> AppM
Ch18 --> AppG
Ch18 --> AppI
Ch20 --> AppG
Ch21 --> AppM
```

## Neural interpretation

- Family synths feed chapter agents instead of bypassing them.
- The helical engine sits as a recurrent attractor over `Ch11`, `Ch18`, `Ch20`, and `Ch21`.
- `AppF`, `AppG`, `AppI`, and `AppM` form the deepest helical governor braid: transport, control, witness, replay.

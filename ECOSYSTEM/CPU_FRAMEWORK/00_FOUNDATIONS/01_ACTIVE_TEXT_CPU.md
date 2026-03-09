# ACTIVE TEXT CPU

## 1. Definition

Definition 1.1 (Crystalline Processing Unit).
A Crystalline Processing Unit is the tuple

`CPU = (K, C, A, O, X, Kappa, P, W, G)`

where:

- `K` is the kernel coordinator,
- `C` is the source corpus,
- `A` is the address lattice,
- `O` is the operator registry,
- `X` is the expansion law,
- `Kappa` is the contraction law,
- `P` is the packet family,
- `W` is the witness ledger,
- `G` is the governance regime.

The CPU does not treat text as inert storage. It treats text as a field of executable
cells that can be addressed, routed, expanded, tested, and recombined.

## 2. Primitive Objects

Definition 2.1 (Text Cell).
A text cell is the minimal executable unit

`cell = (addr, seed, operators, links, witness, status)`

with:

- `addr`: canonical location,
- `seed`: compressed statement or symbol group,
- `operators`: actions the cell permits,
- `links`: lawful outgoing and incoming routes,
- `witness`: evidence for promotion,
- `status`: one of `OK`, `NEAR`, `AMBIG`, `FAIL`.

Definition 2.2 (Task Seed).
A task seed is a short packet that names:

- target outcome,
- admissibility bounds,
- required sources,
- expected output type,
- stop conditions.

Definition 2.3 (Active Text).
Text is active when a task seed can be injected into the corpus and compiled into a
finite sequence of agent waves with deterministic contraction targets.

## 3. The One-to-Many-to-One Law

The CPU obeys the law:

`Seed -> Pillars -> Archetypes -> Workers -> Synthesis`

Expanded form:

`1 -> 4 -> 16 -> 64 -> 1`

The coordinator does not solve the task directly. It compiles the task into a crystal,
routes the crystal through the corpus, and contracts the resulting outputs into one
witnessed artifact.

## 4. Elemental Pillars

- `Earth`: feasibility, grounding, integration, implementation realism
- `Water`: synthesis, continuity, memory retention, cross-part coherence
- `Fire`: novelty, ambition, search pressure, expansion energy
- `Air`: abstraction, mapping, decomposition, routing clarity

No task may bypass an element. Missing an element yields a structurally incomplete CPU pass.

## 5. Address Law

The CPU uses lineage addresses:

`CPUAddr := P1-P2-P3`

where each `Pk` is one of:

- `E`
- `W`
- `F`
- `A`

Examples:

- `E-A-F`
- `W-W-E`
- `F-A-W`

Default production depth uses three elemental decisions after the kernel:

- Level 1: pillar
- Level 2: archetype
- Level 3: worker

This yields `4^3 = 64` worker addresses.

## 6. Compile Pipeline

Algorithm 6.1 (CPU Compile).

Input:

- corpus `C`
- task seed `T`
- depth `d = 3` by default

Output:

- one final synthesis packet

Procedure:

1. normalize `T` into a kernel task packet;
2. split `T` across `Earth`, `Water`, `Fire`, `Air`;
3. split each pillar again into four second-order lenses;
4. split each archetype into four worker modes;
5. route workers through source cells;
6. collect worker packets into archetype packets;
7. contract archetypes into pillar packets;
8. contract pillar packets into one final packet;
9. update witness and governance ledgers.

## 7. Why Text Can Compute

The CPU is built on a simple invariance claim:

If a corpus has stable addressing, lawful transforms, recursive compression,
and witness-bearing replay, then it can function as a computational surface
even when its substrate is markdown, prose, diagrams, or encoded symbolic text.

That is the governing interpretation of the active-text documents in this workspace.

# 06 — Compiler Judgment

## The Judgment Form

```
Sigma |- A_s ==[ Gamma | C, m ]=> A_t => O_m
```

Read: "Under context Sigma, source address A_s is transformed by move string Gamma with certificate C in mode m to target address A_t, producing output artifact O_m."

| Symbol | Meaning |
|--------|---------|
| Sigma | The context — the current state of the organism, including all loaded documents, active routes, and resolved seeds |
| A_s | Source address — where the compiler begins |
| Gamma | Move string — the sequence of opcodes to execute |
| C | Certificate — proof of route validity |
| m | Mode — one of {P, R, E, A} |
| A_t | Target address — where the compiler arrives |
| O_m | Output artifact — the product of compilation, whose class depends on mode m |

---

## The D/Q/I Compiler Stack

The compiler executes in three sequential phases. Each phase transforms the route toward executable form.

### Phase 1: D — Differentiate

Differentiate the route. Decompose the move string Gamma into its constituent opcodes. Resolve each opcode against the current context Sigma. Identify all layer transitions, torsion crossings, dimensional lifts, and weave patterns. Produce a fully resolved route graph.

**Input**: raw move string Gamma
**Output**: differentiated route graph G_d with all opcodes resolved

### Phase 2: Q — Qualify and Normalize

Qualify the differentiated route. Check all three validity conditions (AddressCoherent, LayerLegal, AdmissibleWeave). Normalize any redundant opcode sequences (INV;INV -> identity, LIFT;DROP -> identity). Verify all torsion certificates. Produce a qualified route or reject with diagnostic.

**Input**: differentiated route graph G_d
**Output**: qualified and normalized route G_q, or rejection with certificate of failure

### Phase 3: I — Instantiate

Instantiate one artifact of the class determined by mode m. The qualified route G_q is executed against the organism state Sigma, producing the target address A_t and the output artifact O_m.

**Input**: qualified route G_q + mode m
**Output**: (A_t, O_m)

---

## The 4 Modes

| Mode | Name | Artifact Class | Description |
|------|------|----------------|-------------|
| **P** | Proof | Truth-bearing statement | The compiler produces a certified proposition: a statement with a proof certificate attached. Used for verification, theorem generation, and truth-corridor traversal. |
| **R** | Replay | Reproducibility record | The compiler produces a replay log: a complete record of the route execution that can be re-executed by any agent to obtain the same result. Used for audit, regeneration, and persistence. |
| **E** | Edit | Manuscript patch | The compiler produces a diff: a precise modification to the organism state Sigma. Used for manuscript editing, document updates, and state mutation. |
| **A** | Action | Live execution trace | The compiler produces a side effect: an action in the external world (write a file, send a message, trigger an event). Used for deployment, live operations, and bounded agency. |

---

## Mode Composition

Modes can be composed when a single route requires multiple artifact types:

```
P + R = Certified Replay    (prove it, then make it replayable)
P + E = Certified Edit       (prove the edit is correct, then apply it)
R + A = Replayable Action    (execute, but keep a replay log)
P + R + E + A = Full Stack   (prove, record, patch, and execute)
```

The full stack mode is the organism's maximum compilation: every route is proven correct, recorded for replay, applied as a patch, and executed live. This is the mode used for crown-level operations.

---

## Judgment Examples

### Example 1: Proof mode — verify a chapter claim
```
Sigma |- Ms0001::6.CH.W3.Su.1[B_Su]::Ch01.thm3
        ==[ LOC ; LOC ; LOC | C_proof, P ]=>
        Ms0001::6.CH.W3.Su.1[B_Su]::Ch01.thm3.qed
        => proof_certificate
```

### Example 2: Replay mode — record a traversal
```
Sigma |- Ms0001::6.CH.W3.Su.7[B_Su]::Ch07
        ==[ TURN ; POS ; POS | C_replay, R ]=>
        Ms0001::6.CH.W3.Me.2[B_Me]::Ch09
        => replay_log
```

### Example 3: Edit mode — patch a document
```
Sigma |- Ms0001::12.LP.W5.Su.1[Aplus_star]::AppA.s3
        ==[ LOC | C_edit, E ]=>
        Ms0001::12.LP.W5.Su.1[Aplus_star]::AppA.s3'
        => diff_patch
```

### Example 4: Action mode — execute a live operation
```
Sigma |- Ms0001::108.EM.W9.Su.1[A_Su_star]::E1
        ==[ ZTUN ; LIFT ; WEAVE | C_action, A ]=>
        Ms0001::1.RM.W1.0.Omega[Omega_star]::E10
        => execution_trace
```

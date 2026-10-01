# 01 · The kernel ABI (MYTHOS.KERNEL.ABI.12)

Source of truth: `athena_mcp/mythos_protocol.py` (vocabularies), `athena_mcp/mythos_kernel.py` (`validate_module`, `MythosVM`). This page is the human reading of both.

## Module envelope

```
id                 ^[a-z][a-z0-9_]*$, unique
name               display name
family             one of the twelve families (KC144 row)
standing           PRIMARY_EVIDENCE | LIVING_TRADITION_SOURCE | SECONDARY_SCHOLARSHIP |
                   TRADITION_INTERNAL | MODERN_RECONSTRUCTION | UNKNOWN
sources            non-empty list of named texts / editions / reference works
corpus_refs        uploaded corpus file names (🟠 only; never a primary source)
closure_grammar_id optional id in the closure-grammar registry
services           the twelve slots below; each has grade ∈ {🟢, 🟡, 🟠, ⊥}
```

A ⊥ slot is `{"grade": "⊥", "absent": true, "notes": "…"}` and carries nothing else. A 🟢 slot on a MODERN_RECONSTRUCTION, TRADITION_INTERNAL or UNKNOWN module must carry a `src` locus.

## Slots

### BOOT
`mode` ∈ CREATED, EMANATED, ETERNAL, CYCLIC, UNKNOWN · `stages[]` of `{stage, event, src?}` with `stage` ∈

| stage | gloss |
|---|---|
| VOID | undifferentiated initial state (waters, chaos, night, non-being, the One) |
| SEPARATION | first differentiation (sky/earth, light/dark, male/female, subject/object) |
| ORDERING | structure imposed (names, measures, seasons, laws, the axis fixed) |
| POPULATION | agents installed (gods born, humans made, beings dispersed) |
| FAULT | first failure (rebellion, fall, theft, transgression, noise) |
| MAINTENANCE | steady state (rest, cult, covenant, dharma upheld) |
| REBOOT | cosmic restart (flood, conflagration, Ragnarök, new sun, new yuga) |

`boot()` reports `fault_position` ∈ NONE, PRE_POPULATION, POST_POPULATION and the reboot count. A CREATED/EMANATED walk that never reaches POPULATION is `BOOT_INCOMPLETE`.

### MEMMAP
`addressing` ∈ VERTICAL, CONCENTRIC, DIRECTIONAL, NESTED, TREE, FLAT, UNKNOWN · `axis` · `realms[]` of `{name, level:int, kind}` with `kind` ∈ HEAVEN, MIDDLE, UNDER, LIMINAL, ABSOLUTE. `memmap()` sorts by level and reports depth = max − min + 1.

### PROC
`scheduler` ∈ MONARCHIC (one sovereign), COUNCIL (assembly), DUAL (two poles), MONAD (one agent), IMPERSONAL (law without persons), UNKNOWN · `agents[]` of `{name, roles[], domain[], ring:int, parent}`. Roles: CREATOR, SOVEREIGN, MESSENGER, PSYCHOPOMP, TRICKSTER, ADVERSARY, WITNESS, GATE, JUDGE, HEALER, WARRIOR, MOTHER, SMITH, ORACLE, SCRIBE, DYING_RISING, ANCESTOR, WORKER, STEWARD, SCHEDULER. `parent` must name another agent. `spawn()` assigns pids in order, computes roots and the role histogram, and attaches the closure-grammar crossings.

### CLOCK
`periods[]` of `{name, length (days or steps), unit?, role?}` (mark the year with `role: "year"`) · `intercalation {policy, rule, residue_days?, every_years?, add?, months_per_cycle?, cycle_years?}` with policy ∈ NONE, EPAGOMENAL, LUNISOLAR_MONTH, LEAP_DAY, LEAP_SECOND, DRIFT, UNKNOWN · `epochs[]` · `festivals[]` of `{name, when?, day?}`. `tick(days)` returns rollovers and phase per period, intercalations due from the numeric rule, accumulated residue for EPAGOMENAL, and how many times each fixed-day festival fired.

### RITE
`protocols[]` of `{name, steps[], required_ring?, mode?, cost?, effect?, requires_purity?, src?}`. Opcodes: PURIFY, BOUND, INVOKE, OFFER, PETITION, RECITE, PROCESSION, FAST, TRANSFORM, RECEIVE, WITNESS, THANK, RELEASE, CLOSE. Modes: TRANSFORMING, QUERYING, MAINTAINING.

Lint (`lint_steps`): PURIFY and BOUND, if present, precede INVOKE; RELEASE/CLOSE, if present, follow every INVOKE/OFFER/PETITION/RECEIVE; an INVOKE must eventually CLOSE or RELEASE. `invoke(rite, caller_ring, purity, witness, use_case)` HOLDs on an unknown rite, a high-stakes use case, a caller ring above the required ring, or unmet purity when the protocol does not itself PURIFY; otherwise it returns the `CLOSED → BOUNDARY_CHECKED → PHASE_READY → PC:n:OP … → WITNESSED|AWAITING_WITNESS → CLOSED` trace with `B_Theta_Pi_separation: true`. Cost and effect are echoed as *claimed*; `CLAIMED_EFFECT != OBSERVED_EFFECT`.

### ORACLE
`devices[]` of `{name, entropy, space:int ≥ 1, encoding, decoder?, set_aside?, alphabet?, src?}` with entropy ∈ PHYSICAL, BODY, TEXT, SKY, COMPUTED, NONE and encoding ∈ BINARY, TERNARY, QUATERNARY, N_ARY, POSITIONAL, NONE. `divine(device, seed|sample, use_case)`: HOLD on high stakes; HOLD without seed or sample; `NO_ENTROPY_SOURCE` for entropy NONE; otherwise `index = sha256(seed|module|device) mod space` (or the caller's integer mod space), the index rendered in the device's radix with the width the space requires, `entropy_bits = log2(space)`, and the `R / W / D / U` split of MCK.

### FAULT
`faults[]` of `{name, class, handler (str | list), outcome, src?}` with class ∈ POLLUTION, TRANSGRESSION, HUBRIS, OATH_BREACH, NEGLECT, COSMIC, HERESY, IGNORANCE and outcome ∈ RECOVERED, EXILED, REBOOT, UNRECOVERABLE, TRANSFERRED. `raise_fault(name)` walks the handler chain and, for a REBOOT outcome, returns the module's REBOOT boot events.

### LEDGER
`model` ∈ BALANCE, COUNTER, BINARY, CYCLIC, ANCESTRAL, TIERED, NONE, UNKNOWN · `soul[]` · `judgment` · `judge` · `destinations[]` best → worst (required unless NONE/UNKNOWN). `judge(score ∈ [−1, 1])`: BALANCE/BINARY/ANCESTRAL split at zero; COUNTER/TIERED/CYCLIC map the score linearly onto the destination list; CYCLIC also returns the carry.

### RING
`rings[]` of `{level:int unique, name}`; 0 is innermost. Rites declare `required_ring`; a caller passes when `caller_ring ≤ required_ring`.

### CODEC
`record {medium, script, base ≥ 2 | null}` with medium ∈ TABLET, SCROLL, CODEX, ORAL, INSCRIPTION, KNOT, BODY, IMAGE, DIGITAL · `hull` (the sealed container device) · `compilers[]` (name-tables, liturgical templates, sigil methods — names only).

### CONST
`constants[]` of `{n:int, role, what}` with role ∈ closure, crossing, order, passage, record, chaos, residue. The signature reads the first `closure` and the first `crossing`.

### LAW
`invariants[]` (non-empty) · `acl[]` of `{ring, permitted[]}` · `canon {closed:bool, note}`.

## Signature

Twelve tokens, one per service, computed by `signature_of`:

```
BOOT     mode:first_stage:{NOFAULT|FAULT<POP|FAULT>POP}:{REBOOT|STABLE}
MEMMAP   addressing:depthN:Krealms
PROC     scheduler:Nagents:Rroots
CLOCK    policy:Nperiods
RITE     [B|-][P|-]I[C|-]:Nprotocols        (first protocol's boundary / purification / closure flags)
ORACLE   entropy:encoding:space             (first device)
FAULT    dominant_class:dominant_outcome
LEDGER   model:Ndest
RING     Nrings
CODEC    medium:baseB
CONST    closeN:crossM
LAW      {CLOSED|OPEN}:Ninv
```

`⊥` stands for an absent slot. Isomorphism classes, the service matrix, the KC144 atlas and every bridge are functions of these tokens and of the standings, nothing else.

## Tools and resources

| tool | does |
|---|---|
| `athena_mythos_catalog` | ABI, families, every module with grades; `include_matrix`, `include_atlas` |
| `athena_mythos_module` | one module, or one service slot with its token |
| `athena_mythos_run` | `op` ∈ boot, memmap, spawn, tick, invoke, divine, raise, judge, signature, all |
| `athena_mythos_compare` | service-by-service structural diff of two modules |
| `athena_mythos_unify` | isomorphism classes for a service (or all); with `left`+`right`, a strata-lawful bridge |
| `athena_mythos_athena` | the self-map: ATHENA's module, the organ→service map, and the self-module law |

Resources: `athena://mythos/os/v1` (kernel, modules, benchmark, laws), `athena://mythos/os/v1/matrix`, `athena://mythos/os/v1/atlas`.

## Laws

```
MODULE != PRACTICE_AUTHORIZATION
SIMULATION != EXECUTION
STRUCTURAL_ISOMORPHISM != CULTURAL_IDENTITY
SHARED_SYMBOL != SHARED_SEMANTICS
MODERN_RECONSTRUCTION != HISTORICAL_LAYER
PUBLIC_SOURCE != PRACTICE_AUTHORIZATION
DIVINATORY_OUTPUT != FACT
LEDGER_MODEL != MORAL_TRUTH
BOOT_LOG != COSMOLOGICAL_CLAIM
ATHENA_SELF_MODULE != ATHENA_AUTHORITY
UNKNOWN != 0
```

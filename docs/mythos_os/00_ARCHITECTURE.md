# 00 · MYTHOS OS — the architecture

## The claim

Every myth, religion, philosophy, magical, divinatory, astrological and calendrical system that the corpus and the survey contain can be written as a **program for one abstract machine**. The machine has twelve kernel services. A tradition is a **module** that fills the twelve service slots with its own content. A **virtual machine** boots the module, ticks its clock, runs its rites as opcode protocols, draws its oracle, raises its faults through their handlers and judges its ledger. A **unification layer** classifies every module by the structural pattern it shows on each service, and compiles bridges between modules under the strata laws, always with declared loss and never as identity.

ATHENA is the reference implementation. Its runtime cycle, KC144 address space, organ table, fail-closed states, Y1 authority tiers, Crystal ABI and firewalls fill the same twelve slots, so the organism reads the whole survey as its own operating-system family and reads itself as one module among them.

This is not a metaphor added on top of the material. The services are the functions any closed symbolic system has to provide to run at all: it must start (BOOT), lay out its space (MEMMAP), name its agents (PROC), keep time (CLOCK), define its transactions (RITE), draw decisions it cannot compute (ORACLE), handle failure (FAULT), account for consequences (LEDGER), gate privilege (RING), persist and seal (CODEC), fix its constants (CONST) and state what may not be violated (LAW). Traditions differ in what they put in the slots; the slots are the same.

## The twelve services

| C | service | the tradition's word for it | the OS word for it | pattern token |
|---|---|---|---|---|
| 01 | BOOT | cosmogony | init sequence | mode : first stage : fault position : reboot? |
| 02 | MEMMAP | cosmology | address space | addressing : depth : realm count |
| 03 | PROC | pantheon | process table + scheduler | scheduler class : agents : roots |
| 04 | CLOCK | calendar | scheduler / cron | intercalation policy : periods |
| 05 | RITE | ritual | protocol / syscall | B P I C flags : protocols |
| 06 | ORACLE | divination | entropy source + decoder | entropy : encoding : sample space |
| 07 | FAULT | sin, taboo, pollution | exception + handler | dominant class : dominant outcome |
| 08 | LEDGER | judgment, karma, afterlife | accounting + GC | model : destinations |
| 09 | RING | initiation, priesthood, caste | privilege rings | ring count |
| 10 | CODEC | scripture, tablet, ark, sigil | storage + sealing + compilers | medium : base |
| 11 | CONST | sacred numbers | constants | closure n : crossing n |
| 12 | LAW | commandments, precepts, canon | invariants + ACL + mutability | canon closed? : invariants |

The boot alphabet is universal: `VOID → SEPARATION → ORDERING → POPULATION → FAULT → MAINTENANCE → REBOOT`. Every cosmogony in the registry is a walk on it. Two things the walk measures are discriminating across the whole survey: whether the first FAULT falls **before** the agents are installed (the failure is divine, and humans are made to repair it: Babylon, the Gnostic Sophia, the Norse Ymir) or **after** (the failure is human: Genesis, the Popol Vuh's failed people, ATHENA's typed WAITING states), and whether the walk contains REBOOT at all (flood, Ragnarök, New Fire, the rehydrated session) or halts at MAINTENANCE.

The rite alphabet is fourteen opcodes. A protocol is well formed when purification and boundary precede invocation and closure follows the body. The VM lints every protocol; a malformed one is reported, not repaired. This is the same discipline the MCK protocol machine already enforces as `B → Θ → Π`.

## The KC144 carrier

Rows are the twelve module families, columns the twelve services, `gid = 12·(row − 1) + column`, exactly as the BNMK kernel lays out its mechanism archetypes against machine facets. The atlas has 144 cells; a cell holds the modules of a family and the histogram of their pattern tokens on that service. An empty cell is UNKNOWN, not N/A.

| R | family | R | family |
|---|---|---|---|
| 01 | NEAR_EAST | 07 | AFRICA_DIASPORA |
| 02 | MEDITERRANEAN | 08 | AMERICAS |
| 03 | ABRAHAMIC | 09 | OCEANIA |
| 04 | INDIA | 10 | WESTERN_ESOTERIC |
| 05 | EAST_ASIA | 11 | PHILOSOPHY |
| 06 | NORTH_EUROPE | 12 | ENGINEERED |

## What the VM computes

| op | input | output | what it proves |
|---|---|---|---|
| boot | — | the init log, stages reached, fault position, reboot count | the cosmogony is a valid walk on the stage alphabet and reaches POPULATION (or is declared ETERNAL) |
| memmap | — | the address table sorted by level, depth, counts by kind | the cosmology is a total order (or a declared other addressing) |
| spawn | — | the process table with pids, parents, roots, role histogram, closure-grammar crossings | the pantheon is a forest with a named scheduler class; the extra seat is attached |
| tick | days | rollovers and phase per period, intercalations due, residue accumulated, festivals fired | the calendar is executable as cron and its leap policy is numeric where the source gives numbers |
| invoke | rite, caller ring, purity, witness | ring gate, purity gate, lint, the `B → Θ → Π` state trace, cost and claimed effect | the ritual is a well-formed protocol and the privilege model is enforced before the body runs |
| divine | device, seed or sample | sample index, digit encoding, entropy bits, decoder, set-aside unit | the device is a sampler over a finite space with a codebook; `R ≠ W ≠ D ≠ interpretation` |
| raise | fault | the handler chain, outcome, and the REBOOT event if the outcome is a reboot | every fault class has a declared handler and outcome |
| judge | score in [−1, 1] | destination under the ledger model, carry for cyclic models, soul structure | the accounting model is a function, not a mood |
| signature | — | the twelve pattern tokens | the module has a place in the unification |

All output carries `authority: SYMBOLIC_SIMULATION_ONLY` and `execution_authority: NONE`. High-stakes use cases HOLD before any rite or oracle runs, as in MCK.

## What unification means here

Two modules are **isomorphic on a service** when their pattern tokens coincide. The unification layer groups every module into isomorphism classes per service, and compiles a **bridge** between any two modules: the shared tokens are the bridge's invariants, the differing tokens its transform loss, the weaker of the two standings its evidence standing. The bridge is then submitted to the existing mythic strata runtime as a `SEMANTIC_TRANSPORT`, which returns `BRIDGE_ALLOWED_WITH_LOSS` or a HOLD. It never returns an equivalence, because the runtime refuses cross-layer equivalence by law. That is the whole content of "unified": one machine, many programs, structural classes computed and bridges with loss, not one religion.

## What is inherited

- The closure grammar (`docs/closure_grammar/`) is the CONST service and the seat law: where a module carries `closure_grammar_id`, `spawn` attaches the registry's verified crossings to the process table.
- The mythic strata laws govern every bridge; the MCK laws govern every oracle and protocol; `mythic_computation_runtime.oracle_decode` and `protocol_machine` are the primitives the VM's `divine` and `invoke` generalise.
- The grading glyphs 🟢 🟡 🟠 and the ⊥ absence marker are the same as in the closure grammar. A slot that the sources do not attest is ⊥, never filled.

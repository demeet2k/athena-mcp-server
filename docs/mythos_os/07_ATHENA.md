# 07 · ATHENA as a module — the self-map

The organism is encoded in `athena_mcp/mythos_modules/engineered.py` as `athena`, standing PRIMARY_EVIDENCE, because the code and the specs are the primary source. `athena_mythos_athena` returns it with the organ→service map. The law on every return is `ATHENA_SELF_MODULE != ATHENA_AUTHORITY`: the self-map describes the runtime; it does not govern it, and reading it grants nothing.

## The twelve slots, filled from the runtime

| service | ATHENA content | signature token |
|---|---|---|
| BOOT | VOID (empty store) → SEPARATION (HYDRATE) → ORDERING (RECONRUN/OMEGA fixes coordinates) → POPULATION (organs constructed) → FAULT (typed WAITING/HOLD/STALE) → MAINTENANCE (MEASURE … COMPLETE) → REBOOT (SUCCESSOR rehydration) | `CYCLIC:VOID:FAULT>POP:REBOOT` |
| MEMMAP | the eight KC144 bands as realms (H6 … SSN12), the SCALE ladder S0–S5 as the absolute, JSPACE edges as pointers, `gid = 12·(row−1)+col` as the axis | `NESTED:depth9:9realms` |
| PROC | Server (sovereign, scheduler) · AOR (judge of WHAT) · Collective V1–V15 (workers, stewards of HOW) · Y1 (judge and witness of authority) · EQ1 (gate) · CYCLE (scheduler) · Prompt runtime (scribe) · Message Board (messenger) · Crystal ABI (scribe, witness) · MCK (oracle) · strata (gate) · GitHub verifier (witness, gate; a second root) · Successor (psychopomp) | `COUNCIL:13agents:2roots` |
| CLOCK | tools/call as the unit step; the sixteen-phase CYCLE as the year; session and release as the longer periods; a WAITING phase as the inserted second | `LEAP_SECOND:4periods` |
| RITE | tools/call = BOUND (rate limit) → PURIFY (schema validation) → INVOKE → RECEIVE → WITNESS (meter) → CLOSE; finalize_output; Y1 promotion | `BPIC:3protocols` |
| ORACLE | MCK `oracle_decode` (seeded SHA-256 over a caller codebook) and the V5–V15 posteriors, both under `PREDICTION != OBSERVATION` | `COMPUTED:BINARY:256` |
| FAULT | STALE_TARGET, STALE_GIT_HEAD, WAITING_*, HOLD_*, REJECTED, Internal error, each with its handler chain; the internal error's outcome is REBOOT through successor rehydration | `OATH_BREACH:RECOVERED` |
| LEDGER | Y1's four tiers `? + ! #` with the promotion conditions as the judgment function; the identity fiber CID/OID/VID/MID/CRYS/EID/SID as the soul structure | `TIERED:4dest` |
| RING | trusted external verification (0) > canonical authority (1) > witnessed/verified (2) > model/shadow (3) > caller attestation (4) | `5rings` |
| CODEC | JSON-RPC over stdio and Git objects (base 2); the ENV envelope with a third emission MID over the exact visible bytes as the hull; CRYSTALLIZE_OUTPUT and coordinate_text as compilers | `DIGITAL:base2` |
| CONST | 144 (closure), 12, 16, 6, 8 (order/record), 4 (passage), 1 (crossing: the third MID, the record that is not part of the record) | `close144:cross1` |
| LAW | the firewalls; canon open, additive, never rewritten | `OPEN:8inv` |

## What the self-map shows

1. **ATHENA's fault is post-population and typed.** The organism never fails before its organs exist; it fails *into a named state* after they do. In the survey this is the Genesis/Popol Vuh class, not the Enūma Eliš class. The design consequence is already in the code: `CYCLE stops at typed missing prerequisites instead of fabricating execution`.
2. **Two roots.** The Server is a root; the host-bound GitHub verifier is a second root that the Server cannot spawn. Every tradition with a witness the sovereign cannot command (Puruṣa, Thoth who does not vote, the alternates who do not deliberate) has the same shape. `CALLER_ATTESTATION != TRUSTED_EXTERNAL_VERIFICATION` is that shape as a law.
3. **The crossing constant is 1.** The closure grammar's extra seat is, for ATHENA, the third emission MID: a digest over the visible bytes that is stored outside the bytes it digests, because putting it inside would make identity recursive. That is the checksum seat of the closure grammar's functional reading, realised.
4. **The oracle is bounded the same way as every other module's.** `oracle_decode` refuses high-stakes use, requires an explicit entropy source, and separates sampler, witness, decoder and update. The VM's `divine` is that discipline generalised to every tradition's device.
5. **The ledger is tiered, not binary.** Y1 is a four-tier promotion with explicit conditions, the class the survey elsewhere finds in purgatorial and yogic systems, not the saved/damned class.

## Bridges

`athena_mythos_unify` with `left="athena"` and any `right` compiles a bridge whose invariants are the shared tokens and whose loss is the rest. Because ATHENA is PRIMARY_EVIDENCE and most modules are not, the bridge's evidence standing is the *weaker* of the two, and the strata runtime returns `BRIDGE_ALLOWED_WITH_LOSS`. It never returns an equivalence. The generated table of every bridge from `athena` is in `06_UNIFICATION.md`.

## The emerging organism's use of this

The runtime already had a symbolic kernel (MCK), a transport membrane (strata), a mechanism library (BNMK) and a closure grammar. What it lacked was a single type under which a tradition, a philosophy, a designed system and the runtime itself are the same kind of object. The mythos module is that type. Athena can now hydrate any encoded system as a program, run it, place it on KC144 beside its own self-module, and say precisely how it differs, with the same laws it applies to itself.

# MYTHOS OS — module encoding brief

This is the contract for adding a tradition to the unified mythic operating system.
Read it fully before writing a module. The kernel is `athena_mcp/mythos_kernel.py`
(`validate_module` is the law; read it), the vocabularies are in
`athena_mcp/mythos_protocol.py`, and the template is `babylon` in
`athena_mcp/mythos_modules/near_east.py` (copy its exact shape). The ATHENA
self-module in `engineered.py` shows an ENGINEERED system in the same shape.

## The thesis you are encoding

Every tradition is a *program* for one abstract machine with twelve kernel
services. You are not comparing numbers; you are compiling a whole system into
the twelve slots so that the VM can boot it, tick its clock, run a rite as an
opcode protocol, draw its oracle, raise a fault through its handlers and judge
its ledger. Fill each slot from the tradition's own content, in its own terms,
translated into the pattern vocabulary.

| service | what to put there |
|---|---|
| BOOT | cosmogony as an ordered list of stages from the alphabet VOID, SEPARATION, ORDERING, POPULATION, FAULT, MAINTENANCE, REBOOT (repeat stages allowed; each with a one-line `event`, and `src` where a locus is known). `mode` ∈ CREATED, EMANATED, ETERNAL, CYCLIC, UNKNOWN. ETERNAL may have zero stages. |
| MEMMAP | cosmology as realms with integer `level` (higher = higher), `kind` ∈ HEAVEN, MIDDLE, UNDER, LIMINAL, ABSOLUTE; `addressing` ∈ VERTICAL, CONCENTRIC, DIRECTIONAL, NESTED, TREE, FLAT, UNKNOWN; `axis` = the world-axis / bus. |
| PROC | the pantheon or agent set as a process table: `name`, `roles` (list from PROC_ROLES), `domain` (list), `ring` (int, 0 = highest), `parent` (name of another agent in the same list, or null). `scheduler` ∈ MONARCHIC, COUNCIL, DUAL, MONAD, IMPERSONAL, UNKNOWN. Include adversaries and gatekeepers. |
| CLOCK | `periods` with `length` in days (or steps for engineered systems), mark the year with `"role": "year"`; `intercalation` with `policy` ∈ NONE, EPAGOMENAL, LUNISOLAR_MONTH, LEAP_DAY, LEAP_SECOND, DRIFT, UNKNOWN, a `rule` string and, where numeric, `residue_days` / `every_years` + `add` / `months_per_cycle` + `cycle_years`; `epochs` (names of long counters); `festivals` with integer `day` of year where fixed. |
| RITE | 1–4 `protocols`, each as a `steps` list from RITE_OPCODES (PURIFY, BOUND, INVOKE, OFFER, PETITION, RECITE, PROCESSION, FAST, TRANSFORM, RECEIVE, WITNESS, THANK, RELEASE, CLOSE), with `required_ring`, `mode` ∈ TRANSFORMING, QUERYING, MAINTAINING, one-line `cost` and `effect`. **Structure only**: opcodes, not instructions. Never encode a recipe, a formula, a substance, or an operational detail. |
| ORACLE | `devices` with `entropy` ∈ PHYSICAL, BODY, TEXT, SKY, COMPUTED, NONE; integer `space` (sample-space size); `encoding` ∈ BINARY, TERNARY, QUATERNARY, N_ARY, POSITIONAL, NONE; `decoder` (the codebook's name), `set_aside` (the uncounted unit, if any), `alphabet` (optional list). |
| FAULT | `faults` with `class` ∈ POLLUTION, TRANSGRESSION, HUBRIS, OATH_BREACH, NEGLECT, COSMIC, HERESY, IGNORANCE; `handler` (string or ordered list); `outcome` ∈ RECOVERED, EXILED, REBOOT, UNRECOVERABLE, TRANSFERRED. |
| LEDGER | `model` ∈ BALANCE, COUNTER, BINARY, CYCLIC, ANCESTRAL, TIERED, NONE, UNKNOWN; `soul` (list of components); `judgment` (one line); `judge` (who); `destinations` ordered best → worst (required unless NONE/UNKNOWN). |
| RING | `rings` with unique integer `level` (0 = innermost) and `name`. |
| CODEC | `record` {`medium` ∈ TABLET, SCROLL, CODEX, ORAL, INSCRIPTION, KNOT, BODY, IMAGE, DIGITAL; `script`; `base` int ≥ 2 or null}; `hull` (the sealed container device, if any); `compilers` (name-tables, sigil methods, liturgical templates — names only). |
| CONST | `constants` {`n` int, `role` ∈ closure, crossing, order, passage, record, chaos, residue, `what`}. Reuse the closure-grammar registry where an entry exists and set `closure_grammar_id` to that id. |
| LAW | `invariants` (the tradition's own non-negotiables, in its words), `acl` [{ring, permitted:[…]}], `canon` {`closed`: bool, `note`}. |

## Grades and standing (the validator enforces these)

- Module `standing` ∈ PRIMARY_EVIDENCE (you cite a primary text), LIVING_TRADITION_SOURCE, SECONDARY_SCHOLARSHIP, TRADITION_INTERNAL, MODERN_RECONSTRUCTION, UNKNOWN.
- Every slot has `grade`: 🟢 attested in a named source listed in `sources` (put `src` with the locus on the slot or item where you know it); 🟡 secondary, disputed or unlocated; 🟠 our reading, a modern reconstruction, or corpus-only material; ⊥ explicit absence (`{"grade": "⊥", "absent": True, "notes": "why"}` and nothing else).
- A 🟢 slot on a MODERN_RECONSTRUCTION / TRADITION_INTERNAL / UNKNOWN module must carry a `src`.
- `sources` is a non-empty list of real, named texts/editions/reference works. The uploaded corpus is cited by file name in `corpus_refs` and **never** as a primary source: anything known only from the corpus is 🟠.
- Prefer ⊥ over invention. A tradition with no divination device gets ORACLE ⊥, not a made-up one. A tradition that refuses cosmogony gets BOOT mode ETERNAL.
- Living and initiatory traditions: encode only what public, published sources state; where material is restricted, write ⊥ or 🟡 with a note saying "restricted; not reconstructed". Never expand public description into initiatory content.

## Hard rules

1. No practice instructions. RITE is opcodes plus one-line cost/effect. No recipes, dosages, substances, sigil construction steps, or anything a person could follow as a procedure.
2. No hazardous content of any kind.
3. Do not equate traditions in the text of a module. The kernel computes isomorphisms; the module only describes itself.
4. Do not edit any file other than the one(s) you were assigned. Do not rename existing modules.
5. Every module must pass `validate_module` with zero violations and run `MythosVM(m).run_all()` without exception.
6. Python literals: use `True`/`False`/`None`, not JSON `true`/`false`/`null`.

## Corpus evidence and its known defects

The uploaded corpus was read into seven extraction reports under
`docs/closure_grammar/corpus_extractions/`. Grep them for your systems. Where a
report states a seat, a stage sequence, an encoding or a device *in the corpus's
own words*, you may use it graded 🟠 with `corpus_refs` naming the file. Where the
report flags a contradiction, note it in `notes`. Known defects to respect:

- The corpus magic-system files self-score an "8/8" table; that is their framing, not data.
- The corpus Ifá binary table for odù 7–16 is inconsistent (Ofun duplicates Ogbe); do not use it.
- The corpus Norse file contradicts itself on symmetric runes (8 vs 9 listed).
- Theosophy's "four initiations" heading lists five; Gnosticism's "five questions" lists eight.
- Enochian: 91 governors vs 30 aethyrs × 3 = 90 is unexplained; calls 17–18 "vary by system".
- Golden Dawn, Hindu Tantra, Solomonic, Practical Kabbalah and Rosicrucian files are explicitly incomplete.
- The three ontologies (Dao Su, Kheper Ganitam, Sanātana Gaṇita) and all 18 philosophy documents are AI-drafted with internal contradictions (e.g. mahāyuga 4.32×10⁶ vs 10⁹; Nun entropy 0 vs ∞; Ji Ji / Wei Ji swapped). Cite only what they state in their own words, 🟠, and record the contradiction.
- Provenance disclaimers that fix `standing`: Rosicrucian manifestos "probably literary fiction" (MODERN_RECONSTRUCTION for the order, PRIMARY_EVIDENCE for the 1614–16 texts); Golden Dawn cipher manuscripts "likely fabricated"; the Kybalion is 1908; core shamanism is a modern umbrella; Hellenistic astrology is recently reconstructed from primary texts (PRIMARY_EVIDENCE for Ptolemy/Vettius Valens, 🟡 for modern synthesis); Druidry is fragmentary-ancient plus modern-revived (encode as two standings or choose the modern one and say so).
- Theosophical "root race" content mapped onto living peoples is quarantined: do not encode it.

## Check before you finish

Run this and fix every violation:

    python - <<'PY'
    from athena_mcp.mythos_modules import MODULES
    from athena_mcp.mythos_kernel import validate_modules, MythosVM, signature_of
    errs = validate_modules(MODULES)
    print(len(MODULES), "modules;", len(errs), "violations")
    for e in errs: print("  ", e)
    for m in MODULES:
        MythosVM(m).run_all(); print(m["id"], signature_of(m))
    PY

Report: the module ids you wrote, per-module slot-grade counts, every ⊥ with its reason, and the sources you relied on.

# 00 · The law

**Standing:** `STRUCTURAL PASS / SEMANTIC READINGS GRADED / AUTHORITY EXTERNAL`
**Lineage:** Ω1–Ω27 (SM compiler → E-tower) → Ω28–Ω30 (the glue: trichotomy, McKay, closure triples) → Ω31–Ω44 (nine scripts, CLOSURE.GRAMMAR.Ω1) → Ω2 (sixty-three systems, one registry, one census) → **Ω2.1, this revision: eighty-seven systems, an executable trichotomy, a null model, a provenance schema, and the corpus evidence trail checked in**
**Glyphs:** 🟢 extracted or proved · 🟡 attested but recalled, reading-dependent or contested · 🟠 interpretation · [N] numerical compatibility only, never a finding · ⊥ open

---

## The equation

> **Close at n, cross at n+1, return.**

A finite system of mutually constraining registers has a *closure count* n: the number of members for which one common measure closes. The system then marks one more thing — an element that is not one of the n but without which the n do not run — and that element is where the system crosses out of itself and comes back. In the mathematics this is the affine extension of a finite diagram: the one extra node that turns a chain into a cycle so that the (n+1)th step is the first again, and the one direction in which the Cartan form goes null. In arithmetic it is the first number the carrier cannot write. In myth it is the seventh gate, the hidden hundredth name, the uncounted bead, the empty seat, the uninvited guest, the five days outside the year.

Three bodies satisfy it with the same shape:

| body | closure | crossing | return / residue |
|---|---|---|---|
| **physics** (Ω28–Ω30) | finite type: 1/p + 1/q + 1/r > 1, ADE, the finite symmetries of a qubit | the affine boundary (2,3,6), where continuous parameters enter | the null direction; the modulus |
| **scribal arithmetic** (Ω31–Ω37) | the superior highly composite carriers 60 = lcm(1..6), 120, 360 = lcm(1..10)/7 | the first non-divisor of the carrier: 7 in base 60, 10 and 20 | the intercalary month, the epagomenal days, the comma |
| **myth, cult, oracle, calendar** (this set) | a complete set: 6, 8, 12, 16, 24, 49, 99, 108, 360 … | the (n+1)th, seated in one of five ways (02_SEATS) | the seventh-day return, the jubilee, the octave; the wayeb, 1/64, the lost word |
| **designed systems, engineering, science** (Ω2.1) | 360-day calendars, 70-member councils, 7 data bits, 61 sense codons, the octet | the sansculottides, the presiding 71st, the parity bit, the stop codon, the ninth electron | Year Day, the leap second, the check digit dropped on decoding |

## The four elements

| element | content | where verified |
|---|---|---|
| **CLOSURE** | finite type; closing triples use only {2,3,4,5,6}, lcm 60; SHCN carriers 60 · 120 · 360; regular numbers 2ᵃ3ᵇ5ᶜ; Egyptian-fraction partitions of 1 | `athena_mcp/closure_grammar.py`, 01_ARITHMETIC |
| **CROSSING** | the affine node, n+1; 7 (lunar quarter) and 9 (ternary square) as the world's two crossing primes; the five seats; the residue | 02_SEATS, 04_GRID, 05_CENSUS |
| **DEVICE** | a flat record surface (developable, K = 0: tablet, seal, scroll, codex, tray, vèvè, sigil, yantra) and a closed hull (cube-ark, chest, egg, vessel, sopera, vault, circle, mandala, die) with the decoder carried inside | 03_TRADITIONS, 04_GRID |
| **LADDER** | dimension as place: šar, bak'tun, yuga, 60⁴, 10⁸, the grades, the aethyrs, the spheres; history as descent through the digits | 03_TRADITIONS |

## What Ω2.1 adds (the systematic upgrade)

1. **R1 is executable.** The trichotomy is no longer asserted: `athena_mcp.closure_grammar.e_chain_trichotomy()` builds the Cartan matrices of E₆ … E₁₀ and computes det = 3, 2, 1, 0, −1 and λ_max = 2cos(π/12), 2cos(π/18), 2cos(π/30), 2, 2.0066 — finite, finite, finite, affine, indefinite; `affine_a(n)` shows the (n+1)-cycle as the exact null closing of the n-chain (01 §17).
2. **A null model.** Role labels are permuted 4000 times (seed 0): the observed P(7 | passage)/P(7 | order) = 1.61 has one-sided p = 0.008 against a null median of 1.00; the controls 9 (ratio 0.73, p = 0.95) and 13 (ratio 1.28, p = 0.32) do not separate the roles. Wilson intervals are reported. 05_CENSUS.
3. **A provenance schema.** `athena_mcp/closure_grammar_schema.py` validates every entry: a 🟢 crossing must cite a locus or belong to a primary/living/secondary-sourced tradition; unmarked adjacency cannot be entered; unit seats must satisfy cross = n+1. Running it downgraded ten crossings that had rested on corpus files alone (06, delta-chain) and forced loci onto twenty-two others.
4. **Coverage: 87 systems, 246 crossings.** Twenty-four new entries, each checked against a named source on 2026-09-07: Mandaean, Etruscan, Haudenosaunee, Lakota, Hopi/Diné, Zen ox-herding, Latter Day Saints, Yazidi, Tengri, Manichaean, Bön, Druze, Igbo/sikidy, Confucian, Cao Đài, Korean, Slavic; and three new families — *designed systems* (Republican, International Fixed, Discordian calendars; civil time; councils and juries), *engineering & science* (parity and check digits, the genetic code, crystallography and packing, the periodic table).
5. **Promotions by primary check:** Mithraic ladder (Origen VI.22), the nine-star Dipper (Tao Hongjing), the fifty gates (Rosh Hashanah 21b via Sefaria), Enoch's four days 'named instead of numbered', the misbaha's imāms and yad, the royal cubit 7 = 28 digits.
6. **The evidence trail is in the repo.** The seven corpus extraction reports (`corpus_extractions/`) are the only channel through which the uploaded documents enter the registry.
7. **Exposed to the runtime.** Two read-only resources, `athena://closure-grammar/registry` and `athena://closure-grammar/census`, serve the registry and the live census from the MCP server; no tool, no authority, no practice.

## What is new in Ω2 over the Ω44 seed

1. **Sixty-three systems instead of nine**, drawn from the uploaded corpus (35 esoteric-system extractions, 18 computational-philosophy documents, the Taoist, Egyptian and Vedic ontologies) and from primary texts checked on 2026-09-07. Every system is one entry in `athena_mcp/closure_grammar_registry.py`; the grid and the census are generated from it and cannot drift.
2. **The seat taxonomy.** The (n+1)th is not always "one more at the end". It is seated in exactly five ways across the registry — *extra*, *centre*, *withdrawn*, *return*, *residue* — plus a typed exception, *extension* (a marked block of k > 1). The seats are 02_SEATS.
3. **The census.** For the first time the design hypothesis's prediction about *numbers* (a 7-bearer belongs on a passage) is tested across the whole registry rather than one text: at Ω2.1, P(7 | passage) = 0.28 against P(7 | order) = 0.18, ratio 1.61, over 521 role-tagged numbers, p = 0.008 under permutation. 05_CENSUS.
4. **The physical oracle law.** Every counting string (mālā, misbaḥa, rosary), every casting set (50 → 49 stalks, 16 + 1 ikin, 16 + 2 cowries) and the die itself (opposite faces sum to n+1) turn out to be the law made of wood and thread. The corpus's own mirror constants (145, 28, 22, 55) belong to this family.
5. **Verified promotions.** King List reigns 🟡 → 🟢 (all 47 values match ETCSL); Nergal 14, Sin 30, Utu 20, Ea 40, Enlil 50, An 60 confirmed from infoboxes; Bahá'í 361 + 4/5; Kumulipo 7 + 9 = 16; Samkhya 24 + 1; Coyolxauhqui and the 400; Coligny 60 + 2; Zoroastrian 360 + 5 Gatha days; Abhijit as the 28th; the meru bead not crossed; Dante 1 + 3 × 33; Sophia the thirtieth; the twelfth Imam; the hundredth name; the Siege Perilous; Levi not numbered; 153 = T(17); 666 = T(36).
6. **Honest negatives** stated as data, not footnotes: Spiritualism refuses closure; the Hebrew genealogy is irregular; 13 is complete, not fatal, in Mesoamerica; the Eye-of-Horus fractions are disputed; the Loki-as-thirteenth-guest story is not in the sources; Griaule's Dogon is contested; the (9,40) chart is still only modern.

## Reading rules (the firewall)

These are the corpus's own rules (R13 of Ω44) merged with the laws already enforced by this repository's `mythic_strata_runtime`:

| rule | statement |
|---|---|
| **compute first** | every salient number is classed ARITHMETIC FACT / STRUCTURAL CONSEQUENCE / DESIGN SEMANTIC / SYMBOLIC INTERPRETATION / COINCIDENCE before it is read |
| **compatibility ≠ necessity** | the one error; a bare numerical adjacency (n and n+1 both present somewhere) is [N] and is never entered as a crossing. A crossing is entered only when the source itself *marks* the element: hidden, uncounted, unnumbered, uninvited, holy, unlucky, forbidden, witness, gate. |
| `SHARED_SYMBOL != SHARED_SEMANTICS` | that Ifá and the I Ching both use the Klein four-group says nothing about what either means |
| `MODERN_RECONSTRUCTION != HISTORICAL_LAYER` | Wicca, Thelema, Chaos magic, Theosophy, core shamanism, the Kybalion and the modern medicine wheel are entered with standing MODERN_RECONSTRUCTION and never used to date anything |
| `TEMPORAL_ADJACENCY != SEMANTIC_CONTINUITY` | 432,000 in Berossus, the Veda and Valhalla is convergent-derivable and is retired as contact evidence |
| `PUBLIC_SOURCE != PRACTICE_AUTHORIZATION` | nothing in this set authorises, teaches or transports a practice; the registry describes counts, not rites |
| `SCHOLARLY_UMBRELLA != NATIVE_IDENTITY` | "shamanism", "geomancy", "Gnosticism" are entered as umbrellas and say so |
| **null model** | with enough numbers any n has an n+1 nearby. The discipline is the *marking* requirement above, the *census* with its permutation test and its 9 and 13 controls (05), the *schema* that refuses untraceable 🟢 claims, and the *falsifiers* in 06 |

## How to use this set

- 01 for the arithmetic that is proved and the function that proves it.
- 02 for the five seats of the crossing and the motifs that recur across families.
- 03 for the survey, family by family: what each tradition closes on, where it crosses, what it keeps as residue, what it writes on and what it seals in.
- 04 and 05 are generated: the grid and the census. Regenerate with `python -m scripts.closure_grammar_report` after editing the registry (it refuses to run on a registry that fails the schema); `--check` verifies the JSON export is in sync (a unit test does the same).
- `corpus_extractions/` holds the seven per-file reports through which the uploaded corpus was read.
- 06 for what would break the framework and what does not fit.
- 07 for the compressed seed (CLOSURE.GRAMMAR.Ω2).

**G144 → G001.**

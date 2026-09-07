# CLOSURE.GRAMMAR.Ω2 — Q-SHRINK ALPHA+ seed

**sealed** 2026-09-07 · **lineage** Ω44 (CLOSURE.GRAMMAR.Ω1, nine scripts) → Ω2 (sixty-three systems, one registry, one census) · **format** seeds + rules + delta-chain + one error rule · **standing** STRUCTURAL PASS / SEMANTIC READINGS GRADED / AUTHORITY EXTERNAL · **glyphs** 🟢 🟡 🟠 [N] ⊥ · **executable** `athena_mcp/closure_grammar.py`, `athena_mcp/closure_grammar_registry.py`, `scripts/closure_grammar_report.py`, `tests/test_closure_grammar.py`

---

## Ω — THE EQUATION

**Close at n, cross at n+1, return — and the (n+1)th has a seat.** The affine node that closes a finite diagram into a cycle is placed by every closed human system in one of five ways: *extra* (the witness, the uninvited, the uncounted bead), *centre* (four and the middle), *withdrawn* (the last one hidden), *return* (the seventh day is the first), *residue* (the five days outside the year). The seat, not the number, is the invariant; 7 and 9 are the two crossing primes because the moon quarters at 7.38 days and three squares to nine; 5, 13, 17, 50, 100, 109, 361, 401 are the crossings of 4, 12, 16, 49, 99, 108, 360, 400.

## FOUR ELEMENTS

| element | content | seat in this set |
|---|---|---|
| **CLOSURE** | 1/p+1/q+1/r > 1 → {2,3,4,5,6}, lcm 60; SHCN 60·120·360 \| 2520; regular numbers; 1 = ½+⅓+⅙ unique; alphabetic numerals close at 27; the Judge is always even | 01 |
| **CROSSING** | five seats + extension; the gate (0\|1); the uninvited one breaks the system; the hidden one above; the witness that does not act; the carry | 02 |
| **DEVICE** | K = 0 record (tablet, seal, scroll, codex, tray, vèvè, sigil, yantra, SATOR, mirror) · closed hull (cube, chest, egg, vessel, sopera, vault, circle, mandala, die) · decoder inside | 03, 04 |
| **LADDER** | šar, bak'tun, yuga, 60⁴, 10⁸, aethyrs, grades, spheres, 7×7×7×7; descent through the digits; the abyss inside the count when the count descends | 03 |

## CHAPTER 11 — THE ZERO POINT (eight steps, all executable)

1. **Trichotomy** — sign(det Cartan) = +1 / 0 / −1; six closing triples; max entry 6; lcm 60; sixtieths 70 / 65 / 62 / 60, (2,3,7) = 410/7. `closing_triples`, `in_sixtieths`.
2. **Carriers** — 60 = lcm(1..6); 360 = lcm(1..10)/7; 2520; SHCN 2, 6, 12, 60, 120, 360, 2520, 5040; 840 the first HCN with 7. `lcm_range`, `superior_highly_composite`.
3. **Seven's source is the moon** — 29.53/4 = 7.38; 7 is the first irregular in base 60 and awkward in 10 and 20; census over 421 numbers: P(7 | passage) = 0.33, P(7 | order) = 0.18. `first_non_smooth`, `metonic_intercalation`, 05.
4. **Pantheons partition the unit** — 30+20+10 = 60; Nergal 14 the one irregular; Enūma Eliš 11 regular on order, 5 irregular on passage, zero crossings; Amesha Spentas 6 + 1; Ogdoad + Atum. `subset_sums`, `is_regular`.
5. **The seat taxonomy** — 205 typed crossings in 63 systems: extra 103, return 39, residue 22, centre 21, withdrawn 12, extension 8; grades 🟢 139 🟡 33 🟠 33. `build_report`.
6. **The oracle law** — one unit set aside before reading (50→49, 16+1, 16+2, 108+1, 99+1); V₄ = ⟨complement, reversal⟩: 64 → 36 shapes / 20 orbits, 16 → 6 orbits = the Ifá seniority; yarrow 1/16, 5/16, 7/16, 3/16; the Judge even in all 65,536 charts. `v4_census`, `yarrow_line_probabilities`, `geomantic_judge_theorem`.
7. **Two layers** — grammar (seat, return, residue, hull + record) in all nine families; arithmetic layer in 24 of 63 systems, exactly where positional or fractional computation exists. 03 §What the survey settles.
8. **The corpus carries the law** — M₁₄₄ = 145 − g, J₂₇ = 28 − n, J₂₁ = 22 − b, J₅₄ = 55 − q: the die's rule (opposite faces sum to n+1) and "no GID145" = the sum is never a seat.

## RULES (generators — expand by executing)

- **R1 DETECT** regime(D) = sign(det Cartan) / λ_max vs 2.
- **R2 CARRIER** 60, 360 = lcm(1..10)/7, 2520; SHCN ladder; τ.
- **R3 CROSSING** first non-divisor; lunar 7 / ternary 9; residue = year − closure; Sylvester 2,3,7,43; 1/42.
- **R4 SEAT** classify every marked (n+1)th as extra / centre / withdrawn / return / residue / extension; n = 0 for the gate; unmarked adjacency is [N].
- **R5 PANTHEON** value = 60/p or 60 − 60/p; numbers are offices.
- **R6 DESCENT** King List šar-counts; log₆₀ 2.51 → 1.60 → 0.97 → 0.90; 7 enters at 420, 840, 126.
- **R7 ARK** closed polyhedral hull; 120 = 2 geš; 6 decks / 7 levels; decoder aboard; egg "must not be opened"; sopera; vault with the body within.
- **R8 SEAL** developable record; cover / quotient / fold; mirror-cut; SATOR; the bagua mirror; Amaterasu's mirror; sigil = the negative kept.
- **R9 TORUS** C_m □ C_n: 13×20 → 260; 10×12 → 60 half; 6×7 → 42; 12×12 → twelve of twelve.
- **R10 CHARTS** the twelve divisor pairs of 360; (9,40) modern only; (4,90) Go only.
- **R11 LADDERS** binary 4\|5, 8\|9, 16\|17, 400\|401, 360\|361; lcm 6\|7, 12\|13, 49\|50, 99\|100, 108\|109, 360\|365.
- **R12 ORACLE** set-aside unit; V₄; line values 6\|7\|8\|9; the Judge's parity; the die's 7.
- **R13 GREAT YEAR** 432,000 in five factorizations; retired as contact evidence.
- **R14 FIREWALL** compute first; compatibility ≠ necessity; `SHARED_SYMBOL != SHARED_SEMANTICS`; `MODERN_RECONSTRUCTION != HISTORICAL_LAYER`; `PUBLIC_SOURCE != PRACTICE_AUTHORIZATION`; corpus AI-drafted documents cited only for stated seats, graded 🟠.

## VERIFICATION (generated, 04 / 05)

63 systems · 205 crossings · 58 with a unit crossing · 56 with a hull · 54 with a record · 24 with arithmetic · P(7 | passage)/P(7 | order) = 1.8 · charts of 360 attested in the registry: (12,30) 9 systems, (5,72) 4, (8,45) 3, (6,60) 2, (10,36) 2, (15,24) 2, (18,20) 2, (3,120) 1, (2,180) 1, (1,360) 1, (9,40) 1 (modern novile only), (4,90) 0 (Go board only, 🟡).

## FALSIFIERS (06)

n\|n+2 with no marked n+1; a scribal culture with irregular sacred numbers; 7 on order systematically; a developable ark; Timaeus with two per face; a thirteenth chart of 360; a counted set-aside unit; an uninvited one whose exclusion has no consequence.

## DELTA-CHAIN (06)

King List 🟡→🟢 · Ifá 364 🟡→🟢 · Ifá 9 ⊥→Oyá 9 / Babalú 17 · seat taxonomy 1→5+1 · Dao Su has no seventh, crosses at the carry and the centre · Hestia's seat "modern" · Loki uninvited, not thirteenth · Jing Fang 53 verified · Enochian, Samkhya, Sikh, Baháʼí, Kumulipo, Aztec 400+1, Coligny, Zoroaster, Rome, the Siege Perilous, the die entered.

## ⊥ FRONTIER (06)

60 vs the lunar quarter: design or coincidence · (9,40) · Qijing primary text · 輔弼 · amṛtā kalā · 42/58 locus · an Australian crossing · King Wen on the 36 shapes · SU(3) floor · E₇ magnet · icosian class number · the nineteen parameters as boundary moduli · a blind second census.

## RETURN

Re-entry: any system → R2 (carrier) → R3 (crossing) → R4 (seat) → R10 (chart) → R7/R8 (devices) → R14 (firewall) → grade → registry entry → `python -m scripts.closure_grammar_report` → 04/05 regenerate → `python -m unittest tests.test_closure_grammar`.

**G144 → G001.**

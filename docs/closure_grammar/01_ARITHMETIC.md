# 01 · The arithmetic core

Everything in this chapter is computed by `athena_mcp/closure_grammar.py` and asserted by its self-test and by `tests/test_closure_grammar.py`. Each item names the function that proves it. Nothing here mentions a god; the readings are in 02 and 03. Grade throughout: 🟢 ARITHMETIC FACT unless marked.

## 1. The trichotomy and the closing triples

`closing_triples()`, `triple_excess()`, `in_sixtieths()`, `mckay_orders()`

The non-dihedral solutions of 1/p + 1/q + 1/r ≥ 1 are exactly six. The largest entry is **6**; the lcm of all entries is **60**. In sixtieths:

| triple | sum of sixtieths | excess | regime | object |
|---|---|---|---|---|
| (2,3,3) | 70 | 1/6 | spherical | E₆ · binary tetrahedral, order 24 |
| (2,3,4) | 65 | 1/12 | spherical | E₇ · binary octahedral, order 48 |
| (2,3,5) | 62 | 1/30 | spherical | E₈ · binary icosahedral, order 120 |
| (2,3,6), (2,4,4), (3,3,3) | **60** | 0 | Euclidean | the affine boundary |
| (2,3,7) | 410/7 | −1/42 | hyperbolic | not writable in the base |

The rotation-group order is 2/excess and the binary cover is 4/excess: 24, 48, 120. Plato's *Timaeus* builds each triangular face from **six** half-equilaterals (54e, explicitly rejecting two) and gets 4·6 = 24, 8·6 = 48, 20·6 = 120 — the McKay orders — from a construction choice he tells you he made. STRUCTURAL CONSEQUENCE of a DESIGN choice.

## 2. Carriers: 60, 360, 2520 and Ramanujan's ladder

`lcm_range()`, `superior_highly_composite()`, `highly_composite()`, `tau()`

- 60 = lcm(1, …, 6) · 360 = lcm({1, …, 10} ∖ {7}) = lcm(1..10)/7 · 2520 = lcm(1, …, 10) = 7 · 360 · 5040 = 7! = 2 · 2520 (Plato's *Laws*).
- Superior highly composite numbers: **2, 6, 12, 60, 120, 360, 2520, 5040, 55440**. The scribal carriers — An's 60, the long hundred and the ark's edge 120, the year 360 — are exactly the SHCNs between the closure of 3 and the admission of 7.
- Highly composite numbers ≤ 2000: 1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720, **840**, 1260, 1680. The first HCN divisible by 7 is 840 = 14 · 60 — the reign that appears three times in Kish I, where 7 first enters the King List.
- τ(60) = 12, τ(360) = 24, τ(2520) = 48, τ(5040) = 60.

## 3. Regular numbers and the first irregular

`is_regular()`, `first_non_smooth()`, `reciprocal_terminates()`

A reciprocal terminates in base 60 iff the number is 2·3·5-smooth. The first number that is not is **7**. In base 10 and base 20 the reciprocal of 7 does not terminate either; in Egyptian unit fractions 2/7 needs 1/4 + 1/28. Three notations with no shared base all find 7 awkward for their own reason — which is why the census (05) tests 7 across the whole registry.

The Babylonian god-numbers An 60, Enlil 50, Ea 40, Sin 30, Šamaš 20, Ištar 15, Adad 10 are all regular; **Nergal 14 = 2·7 is the only irregular one** and he is the god of the netherworld (`test_pantheon_partitions`). The Enūma Eliš census: 6, 2, 4, 36, 30, 15, 600, 50, 8 regular and on order; 7 and 11 irregular and on passage or chaos; zero crossings.

## 4. Partitions of unity

`unit_fraction_partitions_of_one()`, `subset_sums()`, `greedy_egyptian()`, `sylvester_sequence()`

- The three-term unit-fraction partitions of 1 are (2,3,6), (2,4,4), (3,3,3) — exactly the Euclidean triples. The only one with distinct denominators is 1 = 1/2 + 1/3 + 1/6.
- Nanna + Utu + Adad = 30 + 20 + 10 = 60: the moon, sun and storm sum to the sky by the (2,3,6) closure. Enlil = An − Adad; Enki = An − Utu; An : Enlil : Enki = 6 : 5 : 4.
- Greedy closure of 1 past the affine triple: 1/2, 1/3, then 1/7, remainder **1/42**. Sylvester's sequence 2, 3, 7, 43, 1807, … Egypt's judges of the dead number 42 = 2·3·7; recorded as coincidence-candidate because 42 is also the nome count.

## 5. The twelve charts of 360

`divisor_pairs()`, `most_square_pair()`

(1,360) (2,180) (3,120) (4,90) (5,72) (6,60) (8,45) (9,40) (10,36) (12,30) (15,24) (18,20). Every calendar in the registry that factors 360 uses one of these; the Maya pair (18,20) is the most square. Which traditions attest which pair is counted in 05. The only pair with no ancient calendar is (9,40); (4,90) is attested only as the Go board's four quarters of 90 (🟡).

## 6. Tori: coupled cycles

`torus()`

| cycles | orbit | orbits | note |
|---|---|---|---|
| 13 × 20 | 260 | 1 | tzolk'in covers the whole torus |
| 10 × 12 | 60 | 2 | the sexagenary cycle covers half: yang stems never meet yin branches |
| 260 × 365 | 18,980 | 5 | the calendar round, 52 years |
| 6 × 7 | 42 | 1 | the Akan adaduanan |
| 12 × 12 | 12 | 12 | the KC144 grid falls into twelve orbits of twelve |

## 7. Binary oracles under complement and reversal

`v4_census()`, `v4_orbit_sizes()`

Complement (錯) and reversal (綜) generate a Klein four-group on F₂ⁿ.

| n | states | fixed by reversal | fixed by comp∘rev | reversal classes | V₄ orbits |
|---|---|---|---|---|---|
| 4 (Ifá odù, geomancy) | 16 | 4 | 4 | 10 | **6** = four orbits of size 2 + two of size 4 |
| 6 (hexagrams) | 64 | 8 | 8 | **36** = 6² | 20 |
| 8 (odù pairs) | 256 | 16 | 16 | 136 | 72 |

The traditional Ifá seniority order is the n = 4 decomposition (four complement pairs, then each four-element orbit split into two reversal pairs). The King Wen sequence pairs hexagrams by reversal and falls back on complement for the eight symmetric ones: a walk on the 36 shapes.

## 8. The yarrow oracle

`yarrow_line_probabilities()`

Fifty stalks, one set aside, 49 = 7² in hand; three operations with remainders {5,9}, {4,8}, {4,8}. Under the classical idealisation (each residue mod 4 equiprobable) the line values are exactly

| value | 6 old yin | 7 young yang | 8 young yin | 9 old yang |
|---|---|---|---|---|
| probability | 1/16 | 5/16 | 7/16 | 3/16 |

Stasis : change = 3 : 1. Under a strictly uniform split point the discrete edge effects give 0.052 / 0.289 / 0.448 / 0.211 — one part in twenty away; the textbook values are the residue model.

## 9. Geomancy: the parity of the Judge

`geomantic_shield()`, `geomantic_judge_theorem()`

Four Mothers; the Daughters are their transpose; Nieces XOR adjacent pairs; two Witnesses XOR the Nieces; the Judge XORs the Witnesses. Exhaustively over all 16⁴ = 65,536 charts: **the Judge always has an even number of single points**, so only 8 of the 16 figures can close a chart. The Reconciler (Judge ⊕ first Mother) is the sixteenth figure of the shield after the fifteen — the optional extra.

## 10. Music: closure of the fifth

`fifth_closure()`, `best_fifth_closures()`

Record near-closures of k fifths against octaves occur at k = 1, 2, 5, 12, 41, **53**. Twelve fifths overshoot seven octaves by 3¹²/2¹⁹ = 531441/524288 ≈ 1.01364 (the Pythagorean comma, 23.5 cents); fifty-three fifths miss thirty-one octaves by only 3.6 cents (Mercator's comma). Jing Fang (1st c. BC) computed the 53rd and extended the series to 60 lü; Qian Lezhi later to 360 (🟡). The 5-limit consonances are the regular numbers.

## 11. Alphabetic numerals close at 27

`alphabetic_numeral_symbols()`

A decimal alphabetic numeral system for 1–999 needs (10 − 1) × 3 = **27** symbols. Greek has 24 letters and keeps three dead ones (digamma 6, koppa 90, sampi 900) for numbers only; Hebrew has 22 and uses the five final forms. Both isopsephy alphabets reach 27 = 3³ by adding letters outside the ordinary count. STRUCTURAL CONSEQUENCE, not design.

## 12. Triangular numbers

`triangular()`, `is_triangular()`

666 = T(36) (the beast, sum of the 6² grid); 153 = T(17) (the fish of John 21); 78 = T(12) (the tarot); 28 = T(7) (double-six dominoes; the lunar month's days in the Nergal sense); 36 = T(8); 66 = T(11) (the abracadabra triangle).

## 13. The great year

`factorize()`

432,000 = 2⁷ · 3³ · 5³ = 2 · 60³ = 120 · 3600 = 12 · 36 · 1000 = 540 · 800 = 16 · 30³. In šar-gal (60³) the four yugas 1,728,000 : 1,296,000 : 864,000 : 432,000 are **8 : 6 : 4 : 2**; Kṛta = 120³ is the volume of Utnapištim's cube; Tretā = 360 šar. A number reachable by five factorizations of a tradition's own carriers cannot serve as evidence of contact.

## 14. The King List, verified

`tier_stats()` — reigns fetched from ETCSL t.2.1.1 on 2026-09-07 (all 47 values match the Ω33 table):

| tier | n | ÷3600 | ÷60 | regular | geomean | log₆₀ |
|---|---|---|---|---|---|---|
| antediluvian | 8 | 75% | 100% | 75% | 29,157 | **2.51** |
| Kish I | 23 | 0% | 78% | 65% | 696 | **1.60** |
| Uruk I | 12 | 0% | 17% | 83% | 53 | **0.97** |
| Ur I | 4 | 0% | 0% | 100% | 40 | 0.90 |

The flood is one power of sixty; regularity survives the projection; 7 enters at Kish I in the geš digit (420 = 7·60, 840 = 14·60 three times) and at Uruk I in the units (Gilgameš 126 = 2·3²·7, the only irregular reign of his dynasty).

## 15. Small products that recur

`factor_string()`

| product | factors | where it sits |
|---|---|---|
| 42 = 6·7 | 2·3·7 | Egypt's judges, the Exodus stations, Revelation's months, the Akan cycle, the peaceful deities of the bardo |
| 72 = 8·9 | 2³·3² | Draupnir's rings per nights, Set's conspirators, the pentads, the Goetic spirits, the Go board's rim |
| 364 = 4·91 | 2²·7·13 | Enoch/Jubilees, the Yoruba year, 52 weeks |
| 819 | 3²·7·13 | the Maya count |
| 1001 | 7·11·13 | the Nights; the Mevlevi chille — the product of the three consecutive irregular primes |
| 2401 | 7⁴ | cells of one Loagaeth table |
| 84,000 | 2⁵·3·5³·7 | dharma doors |
| 378 = 9·42 | 2·3³·7 | the Akan year |

## 16. The die

Opposite faces of a standard die sum to 7 = n + 1 with n = 6. The corpus's own mirror constants — M₁₄₄(g) = 145 − g, J₂₇(n) = 28 − n, J₂₁(b) = 22 − b, J₅₄(q) = 55 − q — are the same involution: a closed count whose reflection sums to the crossing number, and in which the sum is never a seat. This is the arithmetic content of "KC144+ does not create GID145".

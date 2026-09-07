"""CLOSURE GRAMMAR — computational witnesses.

Pure, dependency-free arithmetic behind the cross-tradition "closure grammar"
(close at n, cross at n+1, return).  Nothing here is interpretation: every
function computes a number-theoretic, group-theoretic or combinatorial fact
that the documentation in ``docs/closure_grammar/`` cites.  The firewall
between ARITHMETIC FACT and SYMBOLIC READING is kept by construction —
this module never mentions a god.

The module is not registered with the MCP server; it is a library plus a
self-test (``python -m athena_mcp.closure_grammar``).
"""
from __future__ import annotations

from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from math import gcd, isqrt, log
from typing import Dict, Iterable, List, Sequence, Tuple

# --------------------------------------------------------------------------
# elementary number theory
# --------------------------------------------------------------------------

def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def lcm_range(lo: int, hi: int, exclude: Iterable[int] = ()) -> int:
    ex = set(exclude)
    return reduce(lcm, (k for k in range(lo, hi + 1) if k not in ex), 1)


def factorize(n: int) -> Dict[int, int]:
    n = abs(int(n))
    out: Dict[int, int] = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def factor_string(n: int) -> str:
    f = factorize(n)
    if not f:
        return str(n)
    return "·".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))


def divisors(n: int) -> List[int]:
    small, large = [], []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            small.append(d)
            if d * d != n:
                large.append(n // d)
    return small + large[::-1]


def tau(n: int) -> int:
    return len(divisors(n))


def is_smooth(n: int, primes: Sequence[int] = (2, 3, 5)) -> bool:
    """A "regular number" in the Babylonian sense: reciprocal terminates in base 60."""
    if n <= 0:
        return False
    for p in primes:
        while n % p == 0:
            n //= p
    return n == 1


is_regular = is_smooth


def first_non_smooth(primes: Sequence[int] = (2, 3, 5)) -> int:
    k = 2
    while is_smooth(k, primes):
        k += 1
    return k


def carries(n: int, p: int) -> bool:
    return n % p == 0


def reciprocal_terminates(n: int, base: int) -> bool:
    """1/n has a finite expansion in the given base iff every prime of n divides base."""
    return all(base % p == 0 for p in factorize(n))


def triangular(k: int) -> int:
    return k * (k + 1) // 2


def is_triangular(n: int) -> int | None:
    """Return k with T(k) == n, else None."""
    k = (isqrt(8 * n + 1) - 1) // 2
    return k if triangular(k) == n else None


# --------------------------------------------------------------------------
# highly composite / superior highly composite numbers
# --------------------------------------------------------------------------

def highly_composite(limit: int) -> List[int]:
    """All highly composite numbers <= limit (record-setters of tau)."""
    best, out = 0, []
    for n in range(1, limit + 1):
        t = tau(n)
        if t > best:
            best = t
            out.append(n)
    return out


def _primes_upto(n: int) -> List[int]:
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, isqrt(n) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [i for i in range(n + 1) if sieve[i]]


def superior_highly_composite(limit: int) -> List[int]:
    """Ramanujan's superior highly composite numbers <= limit.

    For each ε>0 the maximiser of τ(n)/n^ε is  ∏_p p^{⌊1/(p^ε−1)⌋};
    sweeping ε produces exactly the SHCN sequence 2, 6, 12, 60, 120, 360,
    2520, 5040, 55440, ...
    """
    primes = _primes_upto(200)
    found = set()
    eps = 3.0
    while eps > 0.02:
        n = 1
        for p in primes:
            e = int(1 / (p ** eps - 1))
            if e <= 0:
                break
            n *= p ** e
            if n > limit:
                break
        if n <= limit and n > 1:
            found.add(n)
        eps -= 0.0005
    return sorted(found)


# --------------------------------------------------------------------------
# closure triples: 1/p + 1/q + 1/r  vs 1   (spherical / Euclidean / hyperbolic)
# --------------------------------------------------------------------------

def triple_excess(p: int, q: int, r: int) -> Fraction:
    return Fraction(1, p) + Fraction(1, q) + Fraction(1, r) - 1


def triple_regime(p: int, q: int, r: int) -> str:
    e = triple_excess(p, q, r)
    return "spherical" if e > 0 else ("euclidean" if e == 0 else "hyperbolic")


ADE_NAMES = {(2, 3, 3): "E6", (2, 3, 4): "E7", (2, 3, 5): "E8"}


def closing_triples(max_entry: int = 12, dihedral: bool = False) -> List[Tuple[int, int, int]]:
    """All 2<=p<=q<=r<=max_entry with 1/p+1/q+1/r >= 1.  Without the dihedral
    family (2,2,n) exactly six remain; the largest entry is 6, the lcm 60."""
    out = []
    for p in range(2, max_entry + 1):
        for q in range(p, max_entry + 1):
            for r in range(q, max_entry + 1):
                if triple_excess(p, q, r) >= 0:
                    if not dihedral and p == 2 and q == 2:
                        continue
                    out.append((p, q, r))
    return out


def polyhedral_group_order(p: int, q: int, r: int) -> int:
    """|G| = 2/excess for a spherical triple (rotation group); binary cover is 4/excess."""
    e = triple_excess(p, q, r)
    if e <= 0:
        raise ValueError("not spherical")
    return int(2 / e)


def mckay_orders() -> Dict[str, int]:
    return {ADE_NAMES[t]: 2 * polyhedral_group_order(*t) for t in ADE_NAMES}


def in_sixtieths(p: int, q: int, r: int) -> Fraction:
    return 60 * (Fraction(1, p) + Fraction(1, q) + Fraction(1, r))


# --------------------------------------------------------------------------
# Egyptian fractions / partitions of unity
# --------------------------------------------------------------------------

def unit_fraction_partitions_of_one(k: int, max_den: int = 60) -> List[Tuple[int, ...]]:
    """All k-term sums of unit fractions equal to 1 (non-decreasing denominators)."""
    out = []

    def rec(prefix: List[int], remaining: Fraction, start: int, terms: int):
        if terms == 0:
            if remaining == 0:
                out.append(tuple(prefix))
            return
        for d in range(start, max_den + 1):
            f = Fraction(1, d)
            if f * terms < remaining:
                break
            if f > remaining:
                continue
            rec(prefix + [d], remaining - f, d, terms - 1)

    rec([], Fraction(1), 2, k)
    return out


def sylvester_sequence(n: int) -> List[int]:
    out, s = [], 2
    for _ in range(n):
        out.append(s)
        s = s * s - s + 1
    return out


def greedy_egyptian(x: Fraction) -> List[int]:
    out = []
    while x > 0:
        d = -(-x.denominator // x.numerator)
        out.append(d)
        x -= Fraction(1, d)
    return out


def subset_sums(values: Dict[str, int], target: int, min_size: int = 2, max_size: int = 4) -> List[Tuple[str, ...]]:
    names = list(values)
    hits = []
    for k in range(min_size, max_size + 1):
        for combo in combinations(names, k):
            if sum(values[c] for c in combo) == target:
                hits.append(combo)
    return hits


# --------------------------------------------------------------------------
# divisor charts of the closed year
# --------------------------------------------------------------------------

def divisor_pairs(n: int) -> List[Tuple[int, int]]:
    return [(d, n // d) for d in divisors(n) if d * d <= n]


def most_square_pair(n: int) -> Tuple[int, int]:
    return max(divisor_pairs(n), key=lambda dq: dq[0])


# --------------------------------------------------------------------------
# tori: coupled cycles
# --------------------------------------------------------------------------

def torus(m: int, n: int) -> Dict[str, int]:
    """Coupled counters (i mod m, j mod n) advancing together: orbit length and
    number of orbits (fraction of the torus one orbit covers = 1/gcd)."""
    return {"orbit": lcm(m, n), "orbits": gcd(m, n), "points": m * n}


# --------------------------------------------------------------------------
# binary oracles: F_2^n under complement and reversal (Klein four-group)
# --------------------------------------------------------------------------

def _rev(x: int, n: int) -> int:
    return int(format(x, f"0{n}b")[::-1], 2)


def _comp(x: int, n: int) -> int:
    return x ^ ((1 << n) - 1)


def v4_census(n: int) -> Dict[str, int]:
    """Fixed points and orbit counts of <complement, reversal> acting on F_2^n."""
    N = 1 << n
    fix_rev = sum(1 for x in range(N) if _rev(x, n) == x)
    fix_comp = sum(1 for x in range(N) if _comp(x, n) == x)
    fix_cr = sum(1 for x in range(N) if _comp(_rev(x, n), n) == x)
    seen, orbits_v4, orbits_rev = set(), 0, 0
    for x in range(N):
        if x in seen:
            continue
        orbit = {x, _rev(x, n), _comp(x, n), _comp(_rev(x, n), n)}
        seen |= orbit
        orbits_v4 += 1
    seen = set()
    for x in range(N):
        if x in seen:
            continue
        seen |= {x, _rev(x, n)}
        orbits_rev += 1
    return {
        "states": N,
        "fixed_by_reversal": fix_rev,
        "fixed_by_complement": fix_comp,
        "fixed_by_comp_rev": fix_cr,
        "reversal_classes": orbits_rev,
        "v4_orbits": orbits_v4,
        "burnside": (N + fix_rev + fix_comp + fix_cr) // 4,
    }


def v4_orbit_sizes(n: int) -> Dict[int, int]:
    N = 1 << n
    seen: set = set()
    sizes: Dict[int, int] = {}
    for x in range(N):
        if x in seen:
            continue
        orbit = {x, _rev(x, n), _comp(x, n), _comp(_rev(x, n), n)}
        seen |= orbit
        sizes[len(orbit)] = sizes.get(len(orbit), 0) + 1
    return sizes


# --------------------------------------------------------------------------
# yarrow-stalk oracle: exact line probabilities
# --------------------------------------------------------------------------

def _yarrow_remainder(total: int, model: str = "residue") -> Dict[int, int]:
    """One operation on `total` stalks.  Split the heap, take one stalk from the
    right between the fingers, count each heap by fours, keep the remainders
    (4 if divisible).  Returns {stalks removed: weight}.

    model="residue": the classical idealisation — the left heap's residue mod 4
    is equiprobable (this is what yields the textbook 1/16, 5/16, 7/16, 3/16).
    model="uniform_split": every split point with both heaps non-empty after the
    finger stalk is taken is equiprobable; the discrete edge effects then shift
    the probabilities by about one part in twenty."""
    out: Dict[int, int] = {}
    if model == "residue":
        for a in range(4):
            left = a if a else 4
            right = ((total - 1 - a) % 4) or 4
            removed = 1 + left + right
            out[removed] = out.get(removed, 0) + 1
        return out
    for left in range(1, total - 1):
        right = total - left - 1
        rl = left % 4 or 4
        rr = right % 4 or 4
        removed = 1 + rl + rr
        out[removed] = out.get(removed, 0) + 1
    return out


def yarrow_line_probabilities(stalks: int = 49, model: str = "residue") -> Dict[int, Fraction]:
    """Exact distribution of line values 6,7,8,9 (three operations on 49 stalks)."""
    dist: Dict[Tuple[int, int, int], Fraction] = {}
    first = _yarrow_remainder(stalks, model)
    tot1 = sum(first.values())
    for r1, c1 in first.items():
        s2 = stalks - r1
        second = _yarrow_remainder(s2, model)
        tot2 = sum(second.values())
        for r2, c2 in second.items():
            s3 = s2 - r2
            third = _yarrow_remainder(s3, model)
            tot3 = sum(third.values())
            for r3, c3 in third.items():
                pr = Fraction(c1, tot1) * Fraction(c2, tot2) * Fraction(c3, tot3)
                dist[(r1, r2, r3)] = dist.get((r1, r2, r3), 0) + pr
    lines: Dict[int, Fraction] = {}
    for (r1, r2, r3), pr in dist.items():
        # a heap of 5 or 4 removed counts 3 ("small"), of 9 or 8 counts 2 ("large")
        val = sum(3 if r in (4, 5) else 2 for r in (r1, r2, r3))
        lines[val] = lines.get(val, 0) + pr
    return dict(sorted(lines.items()))


# --------------------------------------------------------------------------
# geomancy: the shield chart and the parity of the Judge
# --------------------------------------------------------------------------

def geomantic_shield(mothers: Sequence[int]) -> Dict[str, object]:
    """Four mothers as 4-bit integers (bit i = line i, 1 = single point / odd).
    Daughters are the transpose; nieces XOR adjacent pairs; witnesses XOR the
    nieces; the Judge XORs the witnesses; the Reconciler XORs Judge with the
    first mother.  Returns the whole chart and the Judge's parity."""
    M = [[(m >> i) & 1 for i in range(4)] for m in mothers]
    D = [[M[j][i] for j in range(4)] for i in range(4)]
    to_int = lambda bits: sum(b << i for i, b in enumerate(bits))
    mothers_i = [to_int(r) for r in M]
    daughters_i = [to_int(r) for r in D]
    seq = mothers_i + daughters_i
    nieces = [seq[0] ^ seq[1], seq[2] ^ seq[3], seq[4] ^ seq[5], seq[6] ^ seq[7]]
    witnesses = [nieces[0] ^ nieces[1], nieces[2] ^ nieces[3]]
    judge = witnesses[0] ^ witnesses[1]
    reconciler = judge ^ mothers_i[0]
    return {
        "mothers": mothers_i,
        "daughters": daughters_i,
        "nieces": nieces,
        "witnesses": witnesses,
        "judge": judge,
        "reconciler": reconciler,
        "judge_points": 8 - bin(judge).count("1"),  # single point = 1, double = 2 → total points
        "judge_even": (bin(judge).count("1") % 2) == 0,
    }


def geomantic_judge_theorem() -> Dict[str, object]:
    """Exhaustively verify that the Judge always has an even number of single
    points (so only 8 of the 16 figures can be Judge)."""
    judges = set()
    for mothers in product(range(16), repeat=4):
        s = geomantic_shield(mothers)
        if not s["judge_even"]:
            return {"holds": False, "counterexample": mothers}
        judges.add(s["judge"])
    return {"holds": True, "possible_judges": len(judges), "charts": 16 ** 4}


# --------------------------------------------------------------------------
# music: closure of the fifth
# --------------------------------------------------------------------------

def fifth_closure(k: int) -> Tuple[int, float]:
    """k fifths reduced into the octave: returns (octaves spanned, comma ratio)."""
    ratio = Fraction(3, 2) ** k
    octaves = 0
    while ratio >= 2:
        ratio /= 2
        octaves += 1
    return octaves, float(ratio)


def best_fifth_closures(limit: int = 70) -> List[Tuple[int, float]]:
    """Fifth-counts whose comma is a new record minimum: 5, 7, 12, 41, 53 ..."""
    best, out = 10.0, []
    for k in range(1, limit + 1):
        _, r = fifth_closure(k)
        comma = min(r, 2 / r) - 1 if r < 1.5 else min(r - 1, 2 - r)
        dev = abs(log(r)) if r < 1.4142 else abs(log(r / 2))
        if dev < best:
            best = dev
            out.append((k, r))
    return out


# --------------------------------------------------------------------------
# alphabetic numerals
# --------------------------------------------------------------------------

def alphabetic_numeral_symbols(base: int = 10, places: int = 3) -> int:
    """Symbols needed to write every integer < base**places one-letter-per-digit-value
    (1..9, 10..90, 100..900): (base-1)*places = 27 for decimal, three places."""
    return (base - 1) * places


# --------------------------------------------------------------------------
# calendar arithmetic
# --------------------------------------------------------------------------

SYNODIC_MONTH = 29.530589
TROPICAL_YEAR = 365.24219
SIDEREAL_MONTH = 27.321661


def metonic_intercalation(years: int = 19) -> Dict[str, float]:
    months = years * TROPICAL_YEAR / SYNODIC_MONTH
    return {"months": months, "intercalary": round(months) - 12 * years, "rounded": round(months)}


def lunar_quarter() -> float:
    return SYNODIC_MONTH / 4


# --------------------------------------------------------------------------
# the King List: log_60 tiers
# --------------------------------------------------------------------------

def geomean(xs: Sequence[float]) -> float:
    return float(reduce(lambda a, b: a * b, (float(x) for x in xs), 1.0) ** (1.0 / len(xs)))


def tier_stats(reigns: Sequence[int]) -> Dict[str, float]:
    n = len(reigns)
    return {
        "n": n,
        "frac_sar": sum(1 for r in reigns if r % 3600 == 0) / n,
        "frac_ges": sum(1 for r in reigns if r % 60 == 0) / n,
        "frac_regular": sum(1 for r in reigns if is_regular(r)) / n,
        "geomean": geomean(reigns),
        "log60": log(geomean(reigns)) / log(60),
    }


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def self_test() -> Dict[str, object]:
    r: Dict[str, object] = {}
    trip = closing_triples()
    r["closing_triples"] = trip
    assert trip == [(2, 3, 3), (2, 3, 4), (2, 3, 5), (2, 3, 6), (2, 4, 4), (3, 3, 3)]
    assert max(max(t) for t in trip) == 6
    assert reduce(lcm, {x for t in trip for x in t}) == 60
    assert [int(in_sixtieths(*t)) for t in trip[:3]] == [70, 65, 62]
    assert all(in_sixtieths(*t) == 60 for t in trip[3:])
    assert in_sixtieths(2, 3, 7) == Fraction(410, 7)
    assert triple_excess(2, 3, 7) == Fraction(-1, 42)
    assert mckay_orders() == {"E6": 24, "E7": 48, "E8": 120}
    r["mckay"] = mckay_orders()
    assert lcm_range(1, 6) == 60 and lcm_range(1, 10) == 2520
    assert lcm_range(1, 10, exclude=(7,)) == 360
    assert first_non_smooth() == 7
    assert superior_highly_composite(6000) == [2, 6, 12, 60, 120, 360, 2520, 5040]
    r["shcn"] = superior_highly_composite(60000)
    hc = highly_composite(1000)
    assert 840 in hc and min(x for x in hc if x % 7 == 0) == 840
    assert tau(360) == 24 and tau(60) == 12 and tau(5040) == 60
    assert len(divisor_pairs(360)) == 12 and most_square_pair(360) == (18, 20)
    assert unit_fraction_partitions_of_one(3) == [(2, 3, 6), (2, 4, 4), (3, 3, 3)]
    assert sylvester_sequence(5) == [2, 3, 7, 43, 1807]
    assert Fraction(1) - Fraction(1, 2) - Fraction(1, 3) - Fraction(1, 7) == Fraction(1, 42)
    assert v4_census(6) == {
        "states": 64, "fixed_by_reversal": 8, "fixed_by_complement": 0,
        "fixed_by_comp_rev": 8, "reversal_classes": 36, "v4_orbits": 20, "burnside": 20,
    }
    assert v4_census(4)["v4_orbits"] == 6 and v4_orbit_sizes(4) == {2: 4, 4: 2}
    assert yarrow_line_probabilities() == {6: Fraction(1, 16), 7: Fraction(5, 16), 8: Fraction(7, 16), 9: Fraction(3, 16)}
    r["yarrow"] = {k: str(v) for k, v in yarrow_line_probabilities().items()}
    gj = geomantic_judge_theorem()
    assert gj["holds"] and gj["possible_judges"] == 8
    r["geomancy"] = gj
    assert triangular(36) == 666 and triangular(17) == 153 and triangular(12) == 78 and triangular(7) == 28
    assert torus(13, 20) == {"orbit": 260, "orbits": 1, "points": 260}
    assert torus(10, 12)["orbit"] == 60 and torus(10, 12)["orbits"] == 2
    assert torus(260, 365)["orbit"] == 18980
    assert alphabetic_numeral_symbols() == 27
    assert 19 * 19 == 361 and 4 * 19 - 4 == 72
    assert [k for k, _ in best_fifth_closures(60)] == [1, 2, 5, 12, 41, 53]
    assert 7 * 11 * 13 == 1001 and factorize(1001) == {7: 1, 11: 1, 13: 1}
    assert metonic_intercalation()["intercalary"] == 7
    assert 6.9 < lunar_quarter() < 7.5
    for fn in _SELF_TEST_EXTRA:
        fn()
    r["e_chain"] = e_chain_trichotomy()
    return r


if __name__ == "__main__":  # pragma: no cover
    import json

    print(json.dumps(self_test(), indent=1, default=str))


# --------------------------------------------------------------------------
# R1 DETECT, executable: Cartan matrices of the E-chain and the trichotomy
# --------------------------------------------------------------------------

def _tree_cartan(edges: Sequence[Tuple[int, int]], n: int) -> List[List[int]]:
    """Simply-laced Cartan matrix 2I − A for a graph on n nodes."""
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        m[i][i] = 2
    for a, b in edges:
        m[a][b] -= 1
        m[b][a] -= 1
    return m


def dynkin_e(n: int) -> List[List[int]]:
    """Cartan matrix of E_n for n >= 6 as the T(2, 3, n−3) tree: legs of lengths 1, 2, n−4
    from a branch node.  E6, E7, E8 are finite; E9 = affine E8; E10 hyperbolic."""
    if n < 6:
        raise ValueError("E_n needs n >= 6")
    edges: List[Tuple[int, int]] = []
    branch = 0
    node = 1
    for leg in (1, 2, n - 4):
        prev = branch
        for _ in range(leg):
            edges.append((prev, node))
            prev = node
            node += 1
    return _tree_cartan(edges, n)


def dynkin_a(n: int) -> List[List[int]]:
    return _tree_cartan([(i, i + 1) for i in range(n - 1)], n)


def dynkin_d(n: int) -> List[List[int]]:
    edges = [(i, i + 1) for i in range(n - 2)] + [(n - 3, n - 1)]
    return _tree_cartan(edges, n)


def affine_a(n: int) -> List[List[int]]:
    """Affine Ã_n: the (n+1)-cycle — the chain with the one extra node that closes it."""
    edges = [(i, (i + 1) % (n + 1)) for i in range(n + 1)]
    return _tree_cartan(edges, n + 1)


def determinant(m: Sequence[Sequence[int]]) -> int:
    """Exact integer determinant (Bareiss)."""
    a = [list(map(int, row)) for row in m]
    n = len(a)
    sign, prev = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            swap = next((r for r in range(k + 1, n) if a[r][k] != 0), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def spectral_radius(adjacency: Sequence[Sequence[int]], tol: float = 1e-13, max_iterations: int = 200000) -> float:
    """Largest eigenvalue of a connected non-negative symmetric matrix.  Power
    iteration on A + 2I (the shift removes the bipartite oscillation of a tree's
    adjacency spectrum, which is symmetric about zero), iterated to convergence."""
    n = len(adjacency)
    v = [1.0] * n
    lam = 0.0
    for _ in range(max_iterations):
        w = [sum(adjacency[i][j] * v[j] for j in range(n)) + 2.0 * v[i] for i in range(n)]
        norm = sum(x * x for x in w) ** 0.5
        if norm == 0:
            return 0.0
        v_new = [x / norm for x in w]
        lam_new = norm  # Rayleigh quotient of the unit vector v: v·(A+2I)v = |w| when v is normalised
        if abs(lam_new - lam) < tol:
            lam = lam_new
            break
        v, lam = v_new, lam_new
    return lam - 2.0


def regime(cartan: Sequence[Sequence[int]]) -> Dict[str, object]:
    """The trichotomy on a simply-laced diagram: det > 0 finite, = 0 affine, < 0 indefinite;
    equivalently the adjacency spectral radius λ_max < 2, = 2, > 2."""
    det = determinant(cartan)
    n = len(cartan)
    adjacency = [[-cartan[i][j] if i != j else 0 for j in range(n)] for i in range(n)]
    lam = spectral_radius(adjacency)
    return {"det": det, "lambda_max": round(lam, 6), "regime": "finite" if det > 0 else ("affine" if det == 0 else "indefinite")}


def e_chain_trichotomy() -> Dict[str, Dict[str, object]]:
    """det Cartan(E6, E7, E8) = 3, 2, 1; E9 = 0; E10 = −1."""
    return {f"E{n}": regime(dynkin_e(n)) for n in range(6, 11)}


def _self_test_cartan() -> None:
    chain = e_chain_trichotomy()
    assert [chain[f"E{n}"]["det"] for n in range(6, 11)] == [3, 2, 1, 0, -1], chain
    assert chain["E8"]["regime"] == "finite" and chain["E9"]["regime"] == "affine" and chain["E10"]["regime"] == "indefinite"
    assert abs(chain["E9"]["lambda_max"] - 2.0) < 1e-6 and chain["E8"]["lambda_max"] < 2.0 < chain["E10"]["lambda_max"]
    assert determinant(dynkin_a(5)) == 6 and determinant(dynkin_d(5)) == 4
    assert determinant(affine_a(5)) == 0 and abs(regime(affine_a(5))["lambda_max"] - 2.0) < 1e-6
    # a 7-cycle: the affine closing of A6 — six nodes plus the one extra node
    assert len(affine_a(6)) == 7 and regime(affine_a(6))["regime"] == "affine"


_SELF_TEST_EXTRA = [_self_test_cartan]

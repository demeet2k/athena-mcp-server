"""Closure-grammar census core (package side; no scripts/ dependency).

Consumed by scripts/closure_grammar_report.py (renderer) and by the read-only
MCP resource athena://closure-grammar/census.
"""
from __future__ import annotations

import math
import random
from collections import Counter
from typing import Any, Dict

from . import closure_grammar as cg

PASSAGE_ROLES = {"passage", "chaos", "residue"}
ORDER_ROLES = {"order", "closure", "record"}


def wilson(k: int, n: int, z: float = 1.96):
    """Wilson score interval for a proportion."""
    if n == 0:
        return None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round(centre - half, 3), round(centre + half, 3)]


def census_table(tagged):
    """Per-role counts of p-bearers for p in 7, 9, 13, and of regular numbers."""
    out = {}
    for bucket in ("passage", "order"):
        ns = [n for b, n in tagged if b == bucket]
        row = {"total": len(ns), "regular": sum(1 for n in ns if cg.is_regular(n))}
        row["regular_frac"] = round(row["regular"] / len(ns), 3) if ns else None
        for p in (7, 9, 13):
            k = sum(1 for n in ns if n % p == 0)
            row[f"div{p}"] = k
            row[f"div{p}_frac"] = round(k / len(ns), 3) if ns else None
            row[f"div{p}_wilson95"] = wilson(k, len(ns))
        # keep the legacy keys for 7
        row["seven"], row["seven_frac"] = row["div7"], row["div7_frac"]
        row["nine"] = row["div9"]
        out[bucket] = row
    for p in (7, 9, 13):
        a = out["passage"].get(f"div{p}_frac") or 0.0
        b = out["order"].get(f"div{p}_frac") or 0.0
        out[f"ratio{p}_passage_over_order"] = round(a / b, 2) if b else None
    out["seven_ratio_passage_over_order"] = out["ratio7_passage_over_order"]
    return out


def permutation_null(tagged, primes=(7, 9, 13), rounds: int = 4000, seed: int = 0):
    """Shuffle the role labels over the numbers and recompute the passage/order
    ratio of p-divisibility.  The p-value is the fraction of shuffles whose ratio
    is at least the observed one (one-sided).  Deterministic for a given seed;
    the observed ratio is always taken from the unshuffled labels."""
    rng = random.Random(seed)
    original = [b for b, _ in tagged]
    values = [n for _, n in tagged]
    n_pass = sum(1 for b in original if b == "passage")
    n_ord = len(original) - n_pass
    result = {"rounds": rounds, "seed": seed, "tagged_numbers": len(tagged)}
    for p in primes:
        hits = [1 if n % p == 0 else 0 for n in values]

        def ratio(lbls):
            kp = sum(h for h, b in zip(hits, lbls) if b == "passage")
            ko = sum(h for h, b in zip(hits, lbls) if b == "order")
            fp = kp / n_pass if n_pass else 0.0
            fo = ko / n_ord if n_ord else 0.0
            return (fp / fo) if fo else float("inf")

        observed = ratio(original)
        work = list(original)
        at_least = 0
        sample = []
        for _ in range(rounds):
            rng.shuffle(work)
            r = ratio(work)
            sample.append(r)
            if r >= observed:
                at_least += 1
        sample.sort()
        result[f"p{p}"] = {
            "observed_ratio": round(observed, 3) if observed != float("inf") else None,
            "p_value_one_sided": round(at_least / rounds, 4),
            "null_ratio_median": round(sample[len(sample) // 2], 3),
            "null_ratio_95pct": round(sample[int(0.95 * len(sample))], 3),
        }
    return result


def build_report(data: Dict[str, Any]) -> Dict[str, Any]:
    trads = data["traditions"]
    seat_counts = Counter(c["seat"] for t in trads for c in t.get("crossings", []))
    grade_counts = Counter(c["grade"] for t in trads for c in t.get("crossings", []))
    family_counts = Counter(t["family"] for t in trads)
    standing_counts = Counter(t["standing"] for t in trads)

    # closure counts n and crossing numbers n+1, by seat
    n_values = Counter()
    cross_values = Counter()
    for t in trads:
        for c in t.get("crossings", []):
            if c["seat"] in ("extra", "return", "centre", "withdrawn"):
                n_values[c["n"]] += 1
                cross_values[c["cross"]] += 1

    # the census: among role-tagged numbers, is a p-bearer more often on passage than on order?
    tagged = []  # (bucket, n)
    per_tradition = []
    for t in trads:
        pt = {"id": t["id"], "passage7": 0, "passage": 0, "order7": 0, "order": 0}
        for num in t.get("numbers", []):
            n = int(num["n"])
            if n <= 0:
                continue
            bucket = "passage" if num["role"] in PASSAGE_ROLES else ("order" if num["role"] in ORDER_ROLES else None)
            if bucket is None:
                continue
            tagged.append((bucket, n))
            pt[bucket] += 1
            if n % 7 == 0:
                pt[bucket + "7"] += 1
        per_tradition.append(pt)
    census = census_table(tagged)
    null = permutation_null(tagged, primes=(7, 9, 13), rounds=4000, seed=0)
    census["null_model"] = null

    # calendar charts of 360 attested
    charts = Counter()
    for t in trads:
        cal = t.get("calendar") or {}
        for pair in cal.get("charts", []):
            if len(pair) == 2 and pair[0] * pair[1] == 360:
                charts[tuple(sorted(pair))] += 1
    all_pairs = cg.divisor_pairs(360)
    chart_table = [{"pair": list(p), "attested_in": charts.get(p, 0)} for p in all_pairs]

    # devices
    hull = sum(1 for t in trads if t["devices"]["hull"])
    record = sum(1 for t in trads if t["devices"]["record"])
    arithmetic = sum(1 for t in trads if t["arithmetic"]["present"])
    with_grammar = sum(1 for t in trads if any(c["seat"] in ("extra", "return", "centre", "withdrawn") for c in t["crossings"]))

    return {
        "tradition_count": len(trads),
        "crossing_count": sum(seat_counts.values()),
        "seat_counts": dict(seat_counts),
        "grade_counts": dict(grade_counts),
        "family_counts": dict(family_counts),
        "standing_counts": dict(standing_counts),
        "closure_n_histogram": dict(sorted(n_values.items())),
        "crossing_histogram": dict(sorted(cross_values.items())),
        "census": census,
        "per_tradition_census": per_tradition,
        "charts_of_360": chart_table,
        "with_unit_crossing": with_grammar,
        "with_hull": hull,
        "with_record": record,
        "with_arithmetic_layer": arithmetic,
    }



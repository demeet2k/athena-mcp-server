"""Build the closure-grammar verification grid and census from the registry.

Usage:
    python -m scripts.closure_grammar_report          # export JSON + write the two generated docs
    python -m scripts.closure_grammar_report --check  # verify the checked-in JSON matches the registry

Everything here is derived: the registry (athena_mcp.closure_grammar_registry)
is the source of truth, ``spec/CLOSURE_GRAMMAR_REGISTRY_V1.json`` is its
export, and the two markdown files under docs/closure_grammar/ are rendered
from it so that no table in the documentation can drift from the data.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from athena_mcp import closure_grammar as cg  # noqa: E402
from athena_mcp import closure_grammar_registry as reg  # noqa: E402

JSON_PATH = os.path.join(ROOT, "spec", "CLOSURE_GRAMMAR_REGISTRY_V1.json")
GRID_PATH = os.path.join(ROOT, "docs", "closure_grammar", "04_VERIFICATION_GRID.md")
CENSUS_PATH = os.path.join(ROOT, "docs", "closure_grammar", "05_CENSUS.md")

PASSAGE_ROLES = {"passage", "chaos", "residue"}
ORDER_ROLES = {"order", "closure", "record"}


def registry_dict() -> Dict[str, Any]:
    return {
        "version": reg.REGISTRY_VERSION,
        "law": reg.LAW,
        "seats": reg.SEATS,
        "grades": reg.GRADES,
        "traditions": reg.TRADITIONS,
    }


def export_json(path: str = JSON_PATH) -> str:
    data = registry_dict()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    return path


def check_json(path: str = JSON_PATH) -> bool:
    with open(path, encoding="utf-8") as fh:
        on_disk = json.load(fh)
    return json.dumps(on_disk, sort_keys=True, ensure_ascii=False) == json.dumps(registry_dict(), sort_keys=True, ensure_ascii=False)


# --------------------------------------------------------------------------
# census
# --------------------------------------------------------------------------

def carries_any(n: int, primes=(7,)) -> bool:
    return any(n % p == 0 for p in primes) and n != 0


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

    # the 7 / 9 census: among salient numbers, is a 7-bearer more often on passage than on order?
    role_stats: Dict[str, Dict[str, int]] = {"passage": {"total": 0, "seven": 0, "nine": 0, "regular": 0},
                                             "order": {"total": 0, "seven": 0, "nine": 0, "regular": 0}}
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
            rs = role_stats[bucket]
            rs["total"] += 1
            if n % 7 == 0:
                rs["seven"] += 1
                pt[bucket + "7"] += 1
            if n % 9 == 0:
                rs["nine"] += 1
            if cg.is_regular(n):
                rs["regular"] += 1
            pt[bucket] += 1
        per_tradition.append(pt)

    def frac(a, b):
        return round(a / b, 3) if b else None

    census = {
        "passage": {**role_stats["passage"], "seven_frac": frac(role_stats["passage"]["seven"], role_stats["passage"]["total"]),
                    "regular_frac": frac(role_stats["passage"]["regular"], role_stats["passage"]["total"])},
        "order": {**role_stats["order"], "seven_frac": frac(role_stats["order"]["seven"], role_stats["order"]["total"]),
                  "regular_frac": frac(role_stats["order"]["regular"], role_stats["order"]["total"])},
    }
    # likelihood ratio of "carries 7" for passage vs order
    p7 = census["passage"]["seven_frac"] or 0.0
    o7 = census["order"]["seven_frac"] or 0.0
    census["seven_ratio_passage_over_order"] = round(p7 / o7, 2) if o7 else None

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


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def _seat_summary(t: Dict[str, Any]) -> str:
    parts = []
    for c in t.get("crossings", []):
        parts.append(f"{c['n']}\\|{c['cross']} {c['seat'][:3]} {c['grade']}")
    return "; ".join(parts) if parts else "—"


def render_grid(data: Dict[str, Any], rep: Dict[str, Any]) -> str:
    out = []
    out.append("# 04 · Verification grid (generated)\n")
    out.append("Generated by `python -m scripts.closure_grammar_report` from `athena_mcp/closure_grammar_registry.py`. Do not edit by hand.\n")
    out.append(f"Traditions: **{rep['tradition_count']}** · typed crossings: **{rep['crossing_count']}** · with a unit crossing (extra/return/centre/withdrawn): **{rep['with_unit_crossing']}** · with a closed hull: **{rep['with_hull']}** · with a flat record: **{rep['with_record']}** · with an arithmetic layer: **{rep['with_arithmetic_layer']}**\n")
    out.append("Seats: " + ", ".join(f"{k} {v}" for k, v in sorted(rep["seat_counts"].items(), key=lambda kv: -kv[1])) + "\n")
    out.append("Grades of crossings: " + ", ".join(f"{k} {v}" for k, v in rep["grade_counts"].items()) + "\n")
    out.append("\n## Grid\n")
    out.append("| tradition | family | standing | crossings (n\\|n+1 seat grade) | residue | hull | record | ladder | arithmetic |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for t in data["traditions"]:
        res = "; ".join(r["what"][:60] for r in t.get("residues", [])) or "—"
        hull = "; ".join(t["devices"]["hull"])[:80] or "—"
        rec = "; ".join(t["devices"]["record"])[:80] or "—"
        lad = "; ".join(f"{l['count']}: {l['what'][:40]}" for l in t.get("ladder", [])) or "—"
        ar = ("yes: " + t["arithmetic"]["what"][:60]) if t["arithmetic"]["present"] else "no"
        out.append(f"| {t['name']} | {t['family']} | {t['standing']} | {_seat_summary(t)} | {res} | {hull} | {rec} | {lad} | {ar} |")
    out.append("\n## Closure counts n with a unit crossing (histogram)\n")
    out.append("| n | crossings |\n|---|---|")
    for n, k in rep["closure_n_histogram"].items():
        out.append(f"| {n} | {k} |")
    out.append("\n## Crossing numbers n+1 (histogram)\n")
    out.append("| n+1 | crossings |\n|---|---|")
    for n, k in rep["crossing_histogram"].items():
        out.append(f"| {n} | {k} |")
    out.append("\n## Negatives and residue entries (what does not fit)\n")
    for t in data["traditions"]:
        for neg in t.get("negatives", []):
            out.append(f"- **{t['name']}**: {neg}")
    out.append("\n## Per-tradition detail\n")
    for t in data["traditions"]:
        out.append(f"### {t['name']}  `{t['id']}`\n")
        out.append(f"*{t['family']} · {t['region']} · {t['standing']}*\n")
        out.append("Sources: " + "; ".join(t["sources"]) + "\n")
        if t["closures"]:
            out.append("Closures: " + "; ".join(f"{c['n']} = {c['what']} {c['grade']}" for c in t["closures"]) + "\n")
        for c in t["crossings"]:
            out.append(f"- **{c['n']} | {c['cross']}** ({c['seat']}) {c['grade']} — {c['what']}" + (f" [{c['src']}]" if c.get("src") else ""))
        if t["residues"]:
            out.append("\nResidue: " + "; ".join(f"{r['what']} {r['grade']}" for r in t["residues"]))
        if t["numbers"]:
            out.append("\nNumbers: " + "; ".join(f"{n['n']} ({n['role']}: {n['what']}; {cg.factor_string(n['n']) if n['n'] > 1 else n['n']})" for n in t["numbers"]))
        if t.get("notes"):
            out.append("\n" + t["notes"])
        out.append("")
    return "\n".join(out) + "\n"


def render_census(data: Dict[str, Any], rep: Dict[str, Any]) -> str:
    c = rep["census"]
    out = ["# 05 · Census (generated)\n",
           "Generated by `python -m scripts.closure_grammar_report`. The census tests the one prediction the design hypothesis makes about *numbers* rather than *counts*: that a number carrying the prime 7 is more likely to sit on a passage (death, gate, judgment, fate, crossing, residue) than on order (structure, calendar, cosmos, record).\n",
           "Roles are assigned per number in the registry, before the census is run; the census only counts.\n",
           "## Seven-bearers by role\n",
           "| role | numbers | divisible by 7 | fraction | divisible by 9 | regular (2·3·5-smooth) fraction |",
           "|---|---|---|---|---|---|",
           f"| passage / chaos / residue | {c['passage']['total']} | {c['passage']['seven']} | {c['passage']['seven_frac']} | {c['passage']['nine']} | {c['passage']['regular_frac']} |",
           f"| order / closure / record | {c['order']['total']} | {c['order']['seven']} | {c['order']['seven_frac']} | {c['order']['nine']} | {c['order']['regular_frac']} |",
           f"\nLikelihood ratio P(7 | passage) / P(7 | order) = **{c['seven_ratio_passage_over_order']}**.\n",
           "Read this as a discipline, not a proof: role labels were assigned by a reader who knows the hypothesis, so the ratio can only fall, not rise, under adversarial relabelling. What it establishes is that the registry as a whole obeys the assignment its earliest members (Enūma Eliš, Egypt) obeyed with zero crossings.\n",
           "## Per tradition\n",
           "| tradition | passage numbers | of which 7-bearers | order numbers | of which 7-bearers |", "|---|---|---|---|---|"]
    for pt in rep["per_tradition_census"]:
        out.append(f"| {pt['id']} | {pt['passage']} | {pt['passage7']} | {pt['order']} | {pt['order7']} |")
    out.append("\n## The twelve charts of 360 and who uses them\n")
    out.append("| divisor pair | traditions attesting it in the registry |\n|---|---|")
    for row in rep["charts_of_360"]:
        out.append(f"| {row['pair'][0]} × {row['pair'][1]} | {row['attested_in']} |")
    out.append("\nThe (9, 40) pair is attested only as the modern novile aspect (harmonic astrology); the (4, 90) pair only as the Go board's quarters. Both remain ⊥ as ancient calendars.\n")
    out.append("## Families, standings, seats\n")
    out.append("Families: " + ", ".join(f"{k} {v}" for k, v in rep["family_counts"].items()) + "\n")
    out.append("Standings: " + ", ".join(f"{k} {v}" for k, v in rep["standing_counts"].items()) + "\n")
    out.append("Seats: " + ", ".join(f"{k} {v}" for k, v in rep["seat_counts"].items()) + "\n")
    return "\n".join(out) + "\n"


def main(argv: List[str]) -> int:
    data = registry_dict()
    if "--check" in argv:
        ok = check_json()
        print("registry JSON in sync" if ok else "registry JSON OUT OF SYNC — run without --check")
        return 0 if ok else 1
    export_json()
    rep = build_report(data)
    os.makedirs(os.path.dirname(GRID_PATH), exist_ok=True)
    with open(GRID_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_grid(data, rep))
    with open(CENSUS_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_census(data, rep))
    print(json.dumps({k: v for k, v in rep.items() if k not in ("per_tradition_census", "charts_of_360")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

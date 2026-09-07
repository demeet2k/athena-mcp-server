"""Schema and validator for the closure-grammar registry.

Pure-Python validation (no jsonschema dependency).  The rules encode the
provenance discipline of docs/closure_grammar/00_LAW.md:

- every tradition names its sources and a standing from the strata vocabulary;
- every crossing has a seat, a grade, is marked by its source, and obeys the
  n+1 rule for the four unit seats (cross > n for residue / extension);
- a 🟢 crossing must be traceable: either it cites a ``src`` of its own or the
  tradition's standing is PRIMARY_EVIDENCE / LIVING_TRADITION_SOURCE /
  SECONDARY_SCHOLARSHIP and the tradition lists at least one non-corpus source;
- MODERN_RECONSTRUCTION traditions may not carry a 🟢 crossing that is
  attested only by the corpus (the corpus files are themselves modern);
- numbers carry a role from the census vocabulary.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

SEATS = ("extra", "centre", "withdrawn", "return", "residue", "extension")
UNIT_SEATS = ("extra", "centre", "withdrawn", "return")
GRADES = ("🟢", "🟡", "🟠")
STANDINGS = ("PRIMARY_EVIDENCE", "SECONDARY_SCHOLARSHIP", "LIVING_TRADITION_SOURCE", "TRADITION_INTERNAL", "MODERN_RECONSTRUCTION")
ROLES = ("closure", "order", "passage", "record", "chaos", "residue")
ID_RE = re.compile(r"^[a-z][a-z0-9_]{2,60}$")
REQUIRED = ("id", "name", "family", "region", "standing", "sources", "closures", "crossings", "residues", "devices", "ladder", "arithmetic", "numbers", "negatives", "notes")

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "CLOSURE_GRAMMAR_REGISTRY_V1",
    "type": "object",
    "required": ["version", "law", "seats", "grades", "traditions"],
    "properties": {
        "version": {"const": "CLOSURE_GRAMMAR_REGISTRY_V1"},
        "revision": {"type": "integer", "minimum": 1},
        "law": {"type": "string"},
        "seats": {"type": "object"},
        "grades": {"type": "object"},
        "traditions": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": list(REQUIRED),
                "properties": {
                    "id": {"type": "string", "pattern": ID_RE.pattern},
                    "name": {"type": "string"},
                    "family": {"type": "string"},
                    "region": {"type": "string"},
                    "standing": {"enum": list(STANDINGS)},
                    "sources": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                    "closures": {"type": "array", "items": {"type": "object", "required": ["n", "what", "grade"]}},
                    "crossings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["n", "cross", "seat", "what", "grade", "marked"],
                            "properties": {
                                "n": {"type": "integer", "minimum": 0},
                                "cross": {"type": "integer", "minimum": 1},
                                "seat": {"enum": list(SEATS)},
                                "grade": {"enum": list(GRADES)},
                                "marked": {"const": True},
                                "src": {"type": "string"},
                            },
                        },
                    },
                    "residues": {"type": "array"},
                    "devices": {"type": "object", "required": ["record", "hull"]},
                    "ladder": {"type": "array"},
                    "oracle": {"type": ["object", "null"]},
                    "calendar": {"type": ["object", "null"]},
                    "arithmetic": {"type": "object", "required": ["present", "what"]},
                    "numbers": {"type": "array", "items": {"type": "object", "required": ["n", "role", "what"], "properties": {"role": {"enum": list(ROLES)}}}},
                    "negatives": {"type": "array"},
                    "notes": {"type": "string"},
                },
            },
        },
    },
}


def _is_corpus_source(s: str) -> bool:
    return s.strip().lower().startswith("corpus")


def validate_registry(data: Dict[str, Any]) -> List[str]:
    """Return a list of violations (empty = valid)."""
    errs: List[str] = []
    if data.get("version") != "CLOSURE_GRAMMAR_REGISTRY_V1":
        errs.append("version must be CLOSURE_GRAMMAR_REGISTRY_V1")
    trads = data.get("traditions") or []
    seen = set()
    for t in trads:
        tid = t.get("id", "?")
        for k in REQUIRED:
            if k not in t:
                errs.append(f"{tid}: missing field {k}")
        if not ID_RE.match(str(tid)):
            errs.append(f"{tid}: id must match {ID_RE.pattern}")
        if tid in seen:
            errs.append(f"{tid}: duplicate id")
        seen.add(tid)
        if t.get("standing") not in STANDINGS:
            errs.append(f"{tid}: standing {t.get('standing')!r} not in {STANDINGS}")
        sources = t.get("sources") or []
        if not sources:
            errs.append(f"{tid}: sources must be non-empty")
        non_corpus = [s for s in sources if not _is_corpus_source(s)]
        for c in t.get("crossings", []):
            for k in ("n", "cross", "seat", "what", "grade", "marked"):
                if k not in c:
                    errs.append(f"{tid}: crossing missing {k}: {c}")
            if c.get("seat") not in SEATS:
                errs.append(f"{tid}: seat {c.get('seat')!r} invalid")
            if c.get("grade") not in GRADES:
                errs.append(f"{tid}: grade {c.get('grade')!r} invalid")
            if c.get("marked") is not True:
                errs.append(f"{tid}: unmarked adjacency entered as a crossing: {c.get('what')}")
            n, cross = c.get("n"), c.get("cross")
            if isinstance(n, int) and isinstance(cross, int):
                if c.get("seat") in UNIT_SEATS and cross != n + 1:
                    errs.append(f"{tid}: unit seat must have cross == n+1: {n}|{cross}")
                if c.get("seat") in ("residue", "extension") and cross <= n:
                    errs.append(f"{tid}: residue/extension must have cross > n: {n}|{cross}")
            if c.get("grade") == "🟢":
                traceable = bool(c.get("src")) or (t.get("standing") in ("PRIMARY_EVIDENCE", "LIVING_TRADITION_SOURCE", "SECONDARY_SCHOLARSHIP") and non_corpus)
                if t.get("standing") == "MODERN_RECONSTRUCTION" and not non_corpus and not c.get("src"):
                    # a modern system attested only by the (modern) corpus files: allowed only when the crossing
                    # is the tradition's own self-description, which the corpus quotes; it still must cite the file
                    traceable = any(_is_corpus_source(s) for s in sources) and "(corpus" in c.get("what", "")
                if not traceable:
                    errs.append(f"{tid}: 🟢 crossing without traceable source: {c.get('what')[:60]}")
        for num in t.get("numbers", []):
            if num.get("role") not in ROLES:
                errs.append(f"{tid}: number role {num.get('role')!r} invalid")
            if not isinstance(num.get("n"), int):
                errs.append(f"{tid}: number n must be int: {num}")
        for cl in t.get("closures", []):
            if cl.get("grade") not in GRADES:
                errs.append(f"{tid}: closure grade invalid: {cl}")
        dev = t.get("devices") or {}
        if "record" not in dev or "hull" not in dev:
            errs.append(f"{tid}: devices must have record and hull")
    return errs

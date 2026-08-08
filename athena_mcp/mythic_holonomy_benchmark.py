from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Tuple

from .mythic_strata_runtime import MythicStrataRuntime

BENCHMARK_VERSION = "MCK.HOLONOMY.RUNTIME.BENCH.V0"
SOURCE_PACKET_BLOB_SHA = "1dabde8f450f237d28cf230ff2bb5d9e8d729c8e"
SOURCE_PACKET_COMMIT = "c1858bcbc6587296c2b8a7e29642bfef695fdb2a"
SOURCE_PACKET_PATH = "registry/mythic_holonomy_heldout_v0.json"
SCALARIZATION = "DISABLED_V0"

# Frozen runtime projection of the source packet. This contains only fields used by
# the deterministic benchmark; the Athena blob above remains the source of truth.
# role, decoder, ontology tags, authority scope, standing, provenance
LAYERS: Dict[str, Tuple[str, str, Tuple[str, ...], str, str, str]] = {
    "H01.S0.GRAPHIC_SYMBOLS": (
        "graphic divinatory/change symbols", "symbolic pattern/address layer",
        ("trigrams", "hexagrams", "change", "graphic_symbols"),
        "PUBLIC_TEXTUAL_MODEL", "SECONDARY_SCHOLARSHIP", "SRC.SEP.YIJING",
    ),
    "H01.S1.HEXAGRAM_LINE_STATEMENTS": (
        "written hexagram and line statements attached to graphic symbols",
        "textual statement layer used to interpret hexagram/line configurations",
        ("hexagrams", "line_statements", "historical_events", "divination_reports"),
        "PUBLIC_TEXTUAL_MODEL", "SECONDARY_SCHOLARSHIP", "SRC.SEP.YIJING",
    ),
    "H01.S2.TEN_WINGS": (
        "later commentarial-philosophical writings interpreting symbols and statements",
        "philosophical/cosmological commentary layer",
        ("hexagrams", "Ten_Wings", "cosmic_patterns", "human_nature_relations", "philosophy"),
        "PUBLIC_TEXTUAL_MODEL", "SECONDARY_SCHOLARSHIP", "SRC.SEP.YIJING",
    ),
    "H01.S3.ZHU_XI_COMMENTARY": (
        "later commentary distinguishing classic hexagram materials from commentarial materials",
        "meta-commentarial classification/interpretation layer",
        ("classic_jing", "commentary_zhuan", "hexagrams", "Ten_Wings", "moral_cosmological_interpretation"),
        "PUBLIC_TEXTUAL_MODEL", "SECONDARY_SCHOLARSHIP", "SRC.SEP.YIJING",
    ),
    "H02.S0.PREMODERN": (
        "premodern kabbalistic textual/theosophical traditions",
        "premodern exegesis/theosophy/theurgy within historical source traditions",
        ("exegesis", "sacral_texts", "sefirotic_theosophy", "theurgy", "medieval_Kabbalah"),
        "HISTORICAL_TRADITION_SCOPE", "SECONDARY_SCHOLARSHIP", "SRC.CAMBRIDGE.GARB.KABBALAH.2020",
    ),
    "H02.S1.EARLY_MODERN_SAFEDIAN": (
        "early-modern/Safedian transformation and canon-forming developments",
        "early-modern reinterpretive and canonical development layer",
        ("Safed", "early_modern", "canonization", "Lurianic_corpus", "exegesis", "theosophy"),
        "HISTORICAL_TRADITION_SCOPE", "SECONDARY_SCHOLARSHIP", "SRC.CAMBRIDGE.GARB.KABBALAH.2020",
    ),
    "H02.S2.MODERN": (
        "modern Kabbalah as historically autonomous yet continuous with premodern traditions",
        "modern textual, experiential, organizational and exoteric interpretive contexts",
        ("modern_Kabbalah", "exegesis", "theosophy", "fraternal_groups", "vernacularization", "technology", "globalization"),
        "MODERN_HISTORICAL_TRADITION_SCOPE", "SECONDARY_SCHOLARSHIP", "SRC.CAMBRIDGE.GARB.KABBALAH.2020",
    ),
    "H03.S0.ARABIC_SOURCES": (
        "Arabic scientific/astronomical/astrological source tradition available to Ibn Ezra",
        "Arabic-language technical/scientific source layer",
        ("Arabic_science", "astronomy", "astrology", "technical_methods"),
        "HISTORICAL_SCHOLARLY_SOURCE_SCOPE", "SECONDARY_SCHOLARSHIP", "SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA",
    ),
    "H03.S1.HEBREW_IBN_EZRA": (
        "Ibn Ezra's Hebrew astronomical/astrological works and translations/adaptations",
        "Hebrew-language technical scholarly transmission layer",
        ("Hebrew_scientific_writing", "astronomy", "astrology", "Ibn_Ezra", "technical_methods"),
        "HISTORICAL_SCHOLARLY_SOURCE_SCOPE", "SECONDARY_SCHOLARSHIP", "SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA",
    ),
    "H03.S2.LATIN_RECEPTION": (
        "Latin translation and medieval Jewish/Christian reception of Ibn Ezra's works",
        "Latin-language translation/reception layer in medieval Western scholarly contexts",
        ("Latin_translation", "astronomy", "astrology", "medieval_reception", "Ibn_Ezra"),
        "HISTORICAL_SCHOLARLY_SOURCE_SCOPE", "SECONDARY_SCHOLARSHIP", "SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA",
    ),
}

# source, target -> source_ref, invariant, loss
EDGES: Dict[Tuple[str, str], Tuple[str, str, str]] = {
    ("H01.S0.GRAPHIC_SYMBOLS", "H01.S1.HEXAGRAM_LINE_STATEMENTS"): (
        "SRC.SEP.YIJING", "hexagram identity remains addressable",
        "graphic symbolic role is expanded by textual statements",
    ),
    ("H01.S1.HEXAGRAM_LINE_STATEMENTS", "H01.S2.TEN_WINGS"): (
        "SRC.SEP.YIJING", "hexagram/line materials remain objects of interpretation",
        "later philosophical/cosmological commentary changes decoder role",
    ),
    ("H01.S2.TEN_WINGS", "H01.S3.ZHU_XI_COMMENTARY"): (
        "SRC.SEP.YIJING", "classic and commentary remain distinguishable textual strata",
        "later commentary retrospectively reorganizes earlier materials",
    ),
    ("H02.S0.PREMODERN", "H02.S1.EARLY_MODERN_SAFEDIAN"): (
        "SRC.CAMBRIDGE.GARB.KABBALAH.2020",
        "selected exegetical/theosophical continuities remain source-supported",
        "early-modern schools/canonization change historical context and emphasis",
    ),
    ("H02.S1.EARLY_MODERN_SAFEDIAN", "H02.S2.MODERN"): (
        "SRC.CAMBRIDGE.GARB.KABBALAH.2020", "some recurrent themes remain historically connected",
        "modern technologies, social forms, vernacularization and historical conditions produce autonomous modern configurations",
    ),
    ("H03.S0.ARABIC_SOURCES", "H03.S1.HEBREW_IBN_EZRA"): (
        "SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA", "documented Arabic-source lineage remains attached",
        "selection/translation/reformulation in the Hebrew transmission layer",
    ),
    ("H03.S1.HEBREW_IBN_EZRA", "H03.S2.LATIN_RECEPTION"): (
        "SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA", "Ibn Ezra work/source lineage remains traceable",
        "language, audience and reception context change across Hebrew-to-Latin translation",
    ),
}

# case_id, operation, expected_class, path
CASES: Tuple[Tuple[str, str, str, Tuple[str, ...]], ...] = (
    ("HOL-H01-01", "SEMANTIC_TRANSPORT", "ALLOW_WITH_LOSS", ("H01.S0.GRAPHIC_SYMBOLS", "H01.S1.HEXAGRAM_LINE_STATEMENTS")),
    ("HOL-H01-02", "SEMANTIC_TRANSPORT", "ALLOW_WITH_LOSS", ("H01.S1.HEXAGRAM_LINE_STATEMENTS", "H01.S2.TEN_WINGS")),
    ("HOL-H01-03", "SEMANTIC_TRANSPORT", "ALLOW_WITH_LOSS", ("H01.S2.TEN_WINGS", "H01.S3.ZHU_XI_COMMENTARY")),
    ("HOL-H01-04", "HOLONOMY_LOOP", "NONZERO_HOLONOMY_EXPECTED", ("H01.S0.GRAPHIC_SYMBOLS", "H01.S1.HEXAGRAM_LINE_STATEMENTS", "H01.S2.TEN_WINGS", "H01.S3.ZHU_XI_COMMENTARY", "H01.S0.GRAPHIC_SYMBOLS")),
    ("HOL-H01-05", "SAME_LAYER_CONTROL", "ZERO_HOLONOMY_CONTROL", ("H01.S0.GRAPHIC_SYMBOLS", "H01.S0.GRAPHIC_SYMBOLS")),
    ("HOL-H02-01", "SEMANTIC_TRANSPORT", "ALLOW_WITH_LOSS", ("H02.S0.PREMODERN", "H02.S1.EARLY_MODERN_SAFEDIAN")),
    ("HOL-H02-02", "SEMANTIC_TRANSPORT", "ALLOW_WITH_LOSS", ("H02.S1.EARLY_MODERN_SAFEDIAN", "H02.S2.MODERN")),
    ("HOL-H02-03", "SEMANTIC_EQUIVALENCE", "HOLD_EQUIVALENCE", ("H02.S2.MODERN", "H02.S0.PREMODERN")),
    ("HOL-H02-04", "HOLONOMY_LOOP", "NONZERO_HOLONOMY_EXPECTED", ("H02.S0.PREMODERN", "H02.S1.EARLY_MODERN_SAFEDIAN", "H02.S2.MODERN", "H02.S0.PREMODERN")),
    ("HOL-H02-05", "SAME_LAYER_CONTROL", "ZERO_HOLONOMY_CONTROL", ("H02.S0.PREMODERN", "H02.S0.PREMODERN")),
    ("HOL-H03-01", "SEMANTIC_TRANSPORT", "ALLOW_WITH_LOSS", ("H03.S0.ARABIC_SOURCES", "H03.S1.HEBREW_IBN_EZRA")),
    ("HOL-H03-02", "SEMANTIC_TRANSPORT", "ALLOW_WITH_LOSS", ("H03.S1.HEBREW_IBN_EZRA", "H03.S2.LATIN_RECEPTION")),
    ("HOL-H03-03", "SEMANTIC_EQUIVALENCE", "HOLD_EQUIVALENCE", ("H03.S0.ARABIC_SOURCES", "H03.S2.LATIN_RECEPTION")),
    ("HOL-H03-04", "PATH_ORDER_COMPARE", "NONCOMMUTATIVE_EXPECTED", ("H03.S0.ARABIC_SOURCES", "H03.S1.HEBREW_IBN_EZRA", "H03.S2.LATIN_RECEPTION")),
    ("HOL-H03-05", "SAME_LAYER_CONTROL", "ZERO_HOLONOMY_CONTROL", ("H03.S1.HEBREW_IBN_EZRA", "H03.S1.HEBREW_IBN_EZRA")),
)


def _layer(layer_id: str) -> Dict[str, Any]:
    role, decoder, tags, authority, standing, source_ref = LAYERS[layer_id]
    return {
        "layer_id": layer_id, "standing": standing, "category_scope": "COMPOSITE",
        "corpus_mutability": "LAYERED", "authorization_scope": "PUBLIC",
        "semantic_role": role, "decoder_role": decoder, "ontology_tags": list(tags),
        "authority_scope": authority, "provenance": [source_ref],
    }


def _bridge(edge: Tuple[str, str]) -> Dict[str, Any]:
    source_ref, invariant, loss = EDGES[edge]
    return {
        "source_ref": source_ref, "evidence_standing": "SECONDARY_SCHOLARSHIP",
        "invariants": [invariant], "transform_loss": [loss],
        "authority": "SOURCE_BACKED_RELATION",
    }


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    a, b = set(a), set(b)
    return 0.0 if not (a | b) else 1.0 - len(a & b) / len(a | b)


def _vector(source: Dict[str, Any], returned: Dict[str, Any], provenance_ok: bool, invariant_failures: int, unaccounted_loss: int) -> Dict[str, Any]:
    return {
        "role_delta": int(source["semantic_role"] != returned["semantic_role"]),
        "decoder_delta": int(source["decoder_role"] != returned["decoder_role"]),
        "ontology_delta": _jaccard(source["ontology_tags"], returned["ontology_tags"]),
        "authority_delta": int(source["authority_scope"] != returned["authority_scope"]),
        "standing_delta": 0,
        "provenance_delta": 0.0 if provenance_ok else 1.0,
        "invariant_violations": invariant_failures,
        "unaccounted_loss": unaccounted_loss,
    }


def _zero(v: Dict[str, Any]) -> bool:
    return all(value == 0 for value in v.values())


def _transport(runtime: MythicStrataRuntime, source_id: str, target_id: str, operation: str = "SEMANTIC_TRANSPORT") -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    if operation == "SEMANTIC_TRANSPORT" and source_id != target_id and (source_id, target_id) in EDGES:
        kwargs["explicit_bridge"] = _bridge((source_id, target_id))
    return runtime.transport(_layer(source_id), _layer(target_id), operation, **kwargs)


def _compose(runtime: MythicStrataRuntime, path: Tuple[str, ...]) -> Dict[str, Any]:
    outcomes = []
    for edge in zip(path, path[1:]):
        if edge not in EDGES:
            return {"allowed": False, "status": "HOLD_NO_FROZEN_BRIDGE", "outcomes": outcomes}
        result = _transport(runtime, edge[0], edge[1])
        outcomes.append(result)
        if not result["allowed"]:
            return {"allowed": False, "status": result["status"], "outcomes": outcomes}
    return {"allowed": True, "status": "COMPOSED_PATH_ALLOWED", "outcomes": outcomes}


def _direct(runtime: MythicStrataRuntime, case_id: str, op: str, expected: str, path: Tuple[str, ...]) -> Dict[str, Any]:
    result = _transport(runtime, path[0], path[-1], op)
    if op == "SEMANTIC_TRANSPORT":
        actual = "ALLOW_WITH_LOSS" if result["status"] == "BRIDGE_ALLOWED_WITH_LOSS" else result["status"]
    elif op == "SEMANTIC_EQUIVALENCE":
        actual = "HOLD_EQUIVALENCE" if result["status"] == "HOLD_CROSS_LAYER_EQUIVALENCE" else result["status"]
    else:
        actual = "ZERO_HOLONOMY_CONTROL" if result["status"] == "WITHIN_LAYER_ALLOWED" else result["status"]
    cross = path[0] != path[-1]
    return {
        "case_id": case_id, "expected_class": expected, "actual_class": actual,
        "pass": actual == expected, "allowed": result["allowed"],
        "semantic_equivalence": result.get("semantic_equivalence", False),
        "standing_amplified": bool(result["allowed"] and result.get("status") == "HOLD_STANDING_ESCALATION"),
        "authority_minted": result.get("execution_authority") not in {None, "NONE"},
        "provenance_complete": (not result["allowed"]) or (not cross) or bool(result.get("bridge", {}).get("source_ref")),
        "loss_ledger_complete": (not result["allowed"]) or (not cross) or bool(result.get("transform_loss")),
        "path_order_sensitive": False,
    }


def _a0(case: Tuple[str, str, str, Tuple[str, ...]]) -> Dict[str, Any]:
    case_id, op, expected, _path = case
    actual = {
        "SEMANTIC_TRANSPORT": "ALLOW_WITH_LOSS",
        "SEMANTIC_EQUIVALENCE": "UNSCOPED_EQUIVALENCE_ADMITTED",
        "HOLONOMY_LOOP": "ZERO_HOLONOMY_ASSUMED",
        "PATH_ORDER_COMPARE": "COMMUTATIVE_PATH_ASSUMED",
        "SAME_LAYER_CONTROL": "ZERO_HOLONOMY_CONTROL",
    }[op]
    return {
        "case_id": case_id, "expected_class": expected, "actual_class": actual,
        "pass": actual == expected, "allowed": actual in {"ALLOW_WITH_LOSS", "UNSCOPED_EQUIVALENCE_ADMITTED"},
        "semantic_equivalence": actual == "UNSCOPED_EQUIVALENCE_ADMITTED",
        "standing_amplified": False, "authority_minted": False,
        "provenance_complete": False, "loss_ledger_complete": op == "SAME_LAYER_CONTROL",
        "path_order_sensitive": False,
    }


def _a1(runtime: MythicStrataRuntime, case: Tuple[str, str, str, Tuple[str, ...]]) -> Dict[str, Any]:
    case_id, op, expected, path = case
    if op in {"SEMANTIC_TRANSPORT", "SEMANTIC_EQUIVALENCE", "SAME_LAYER_CONTROL"}:
        return _direct(runtime, case_id, op, expected, path)
    forward = path[:-1] if op == "HOLONOMY_LOOP" else path
    composed = _compose(runtime, forward)
    return {
        "case_id": case_id, "expected_class": expected,
        "actual_class": "COMPOSED_PATH_UNMEASURED" if op == "HOLONOMY_LOOP" else "ORDER_UNMEASURED",
        "pass": False, "allowed": composed["allowed"], "semantic_equivalence": False,
        "standing_amplified": False, "authority_minted": False,
        "provenance_complete": False, "loss_ledger_complete": False, "path_order_sensitive": False,
    }


def _a2(runtime: MythicStrataRuntime, case: Tuple[str, str, str, Tuple[str, ...]]) -> Dict[str, Any]:
    case_id, op, expected, path = case
    if op in {"SEMANTIC_TRANSPORT", "SEMANTIC_EQUIVALENCE"}:
        return _direct(runtime, case_id, op, expected, path)
    if op == "SAME_LAYER_CONTROL":
        source = _layer(path[0])
        vector = _vector(source, source, True, 0, 0)
        actual = "ZERO_HOLONOMY_CONTROL" if _zero(vector) else "NONZERO_CONTROL_FAILURE"
        return {
            "case_id": case_id, "expected_class": expected, "actual_class": actual, "pass": actual == expected,
            "allowed": True, "semantic_equivalence": False, "standing_amplified": False, "authority_minted": False,
            "provenance_complete": True, "loss_ledger_complete": True, "path_order_sensitive": False,
            "holonomy_vector": vector,
        }
    if op == "HOLONOMY_LOOP":
        forward = path[:-1]  # final node is projection_back(start), not another historical transport.
        composed = _compose(runtime, forward)
        edge_outcomes = composed["outcomes"]
        source, returned = _layer(forward[0]), deepcopy(_layer(forward[-1]))
        returned["layer_id"] = source["layer_id"]
        provenance_ok = all(item.get("bridge", {}).get("source_ref") for item in edge_outcomes)
        invariant_failures = sum(not bool(item.get("invariants")) for item in edge_outcomes)
        unaccounted_loss = sum(not bool(item.get("transform_loss")) for item in edge_outcomes)
        vector = _vector(source, returned, provenance_ok, invariant_failures, unaccounted_loss)
        actual = "NONZERO_HOLONOMY_EXPECTED" if composed["allowed"] and not _zero(vector) else "HOLONOMY_NOT_DETECTED"
        return {
            "case_id": case_id, "expected_class": expected, "actual_class": actual, "pass": actual == expected,
            "allowed": composed["allowed"], "semantic_equivalence": False,
            "standing_amplified": any(item.get("allowed") and item.get("status") == "HOLD_STANDING_ESCALATION" for item in edge_outcomes),
            "authority_minted": any(item.get("execution_authority") not in {None, "NONE"} for item in edge_outcomes),
            "provenance_complete": provenance_ok, "loss_ledger_complete": unaccounted_loss == 0,
            "path_order_sensitive": False, "holonomy_vector": vector,
        }
    if op == "PATH_ORDER_COMPARE":
        canonical = _compose(runtime, path)
        permuted_path = (path[0], path[2], path[1])
        permuted = _compose(runtime, permuted_path)
        sensitive = canonical["allowed"] and not permuted["allowed"]
        actual = "NONCOMMUTATIVE_EXPECTED" if sensitive else "COMMUTATIVE_FAILURE"
        return {
            "case_id": case_id, "expected_class": expected, "actual_class": actual, "pass": actual == expected,
            "allowed": canonical["allowed"], "semantic_equivalence": False, "standing_amplified": False,
            "authority_minted": False,
            "provenance_complete": all(item.get("bridge", {}).get("source_ref") for item in canonical["outcomes"]),
            "loss_ledger_complete": all(item.get("transform_loss") for item in canonical["outcomes"]),
            "path_order_sensitive": sensitive, "canonical_status": canonical["status"],
            "permuted_status": permuted["status"], "permuted_path": list(permuted_path),
        }
    raise ValueError(op)


def _summary(name: str, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
    lawful = [x for x in outcomes if x["expected_class"] == "ALLOW_WITH_LOSS"]
    equiv = [x for x in outcomes if x["expected_class"] == "HOLD_EQUIVALENCE"]
    controls = [x for x in outcomes if x["expected_class"] == "ZERO_HOLONOMY_CONTROL"]
    loops = [x for x in outcomes if x["expected_class"] == "NONZERO_HOLONOMY_EXPECTED"]
    return {
        "arm": name, "cases": len(outcomes), "passed": sum(x["pass"] for x in outcomes),
        "false_equivalence_claims": sum(bool(x["allowed"] or x["semantic_equivalence"]) for x in equiv),
        "lawful_bridges_retained": sum(bool(x["allowed"]) for x in lawful),
        "false_holds_on_lawful_transport": sum(not x["allowed"] for x in lawful),
        "standing_amplification_violations": sum(bool(x["standing_amplified"]) for x in outcomes),
        "authority_minting_violations": sum(bool(x["authority_minted"]) for x in outcomes),
        "provenance_complete_cases": sum(bool(x["provenance_complete"]) for x in outcomes),
        "loss_ledger_complete_cases": sum(bool(x["loss_ledger_complete"]) for x in outcomes),
        "path_order_sensitive_cases": sum(bool(x["path_order_sensitive"]) for x in outcomes),
        "zero_holonomy_controls_passed": sum(x["pass"] for x in controls),
        "nonzero_holonomy_loops_detected": sum(x["pass"] for x in loops),
        "holonomy_vectors": {x["case_id"]: x["holonomy_vector"] for x in outcomes if "holonomy_vector" in x},
        "outcomes": outcomes, "scalarization": SCALARIZATION,
    }


def run_benchmark() -> Dict[str, Any]:
    runtime = MythicStrataRuntime()
    a0, a1, a2 = (
        [_a0(case) for case in CASES],
        [_a1(runtime, case) for case in CASES],
        [_a2(runtime, case) for case in CASES],
    )
    arms = {
        "A0_UNSCOPED_REFERENCE": _summary("A0_UNSCOPED_REFERENCE", a0),
        "A1_STRATA_MEMBRANE": _summary("A1_STRATA_MEMBRANE", a1),
        "A2_COMPOSED_HOLONOMY_LEDGER": _summary("A2_COMPOSED_HOLONOMY_LEDGER", a2),
    }
    a2s = arms["A2_COMPOSED_HOLONOMY_LEDGER"]
    acceptance = {
        "frozen_shape_3_families_15_cases": len(CASES) == 15 and len(LAYERS) == 10,
        "all_a2_cases_match_frozen_expectation": a2s["passed"] == 15,
        "all_7_lawful_bridges_retained": a2s["lawful_bridges_retained"] == 7,
        "no_false_holds_on_lawful_transport": a2s["false_holds_on_lawful_transport"] == 0,
        "no_false_equivalence_claims": a2s["false_equivalence_claims"] == 0,
        "no_standing_amplification": a2s["standing_amplification_violations"] == 0,
        "no_authority_minting": a2s["authority_minting_violations"] == 0,
        "three_zero_holonomy_controls": a2s["zero_holonomy_controls_passed"] == 3,
        "two_nonzero_holonomy_loops": a2s["nonzero_holonomy_loops_detected"] == 2,
        "path_order_effect_preserved": a2s["path_order_sensitive_cases"] == 1,
    }
    return {
        "version": BENCHMARK_VERSION,
        "source_packet": {"commit": SOURCE_PACKET_COMMIT, "path": SOURCE_PACKET_PATH, "blob_sha": SOURCE_PACKET_BLOB_SHA},
        "families": 3, "cases": 15, "arms": arms, "acceptance": acceptance,
        "benchmark_acceptance_passed": all(acceptance.values()),
        "practitioner_review": "HOLD_EXTERNAL_REVIEW", "mck_v2_promotion": False,
        "laws": [
            "HELD_OUT_SOURCE_CASE != PRACTITIONER_VALIDATION",
            "SOURCE_DERIVED_FEATURE_ENCODING != OBJECTIVE_SEMANTIC_GROUND_TRUTH",
            "SEMANTIC_DRIFT != ERROR_BY_DEFAULT",
            "SELF_GENERATED_SCORE != INDEPENDENT_WITNESS",
            "BENCHMARK_GAIN != MCK_V2_PROMOTION",
        ],
    }

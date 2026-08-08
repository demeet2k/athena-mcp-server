"""AQ-001 production-runtime characterization probe.

This probe replays the frozen 15-case geometry from Athena blob
1dabde8f450f237d28cf230ff2bb5d9e8d729c8e against the actual
MythicStrataRuntime at the branch base. It intentionally changes no runtime
behavior. Frozen expected labels are consulted only in the post-execution
assay test; probe_case/probe_all do not read EXPECTED.

The packet's richer authority strings are preserved as source_scope while the
runtime-native authorization_scope is UNKNOWN rather than guessed.
"""
from __future__ import annotations

import copy
import json
import unittest
from unittest.mock import patch

from athena_mcp.mythic_strata_protocol import BRIDGE, OPERATIONS, STRATA_VERSION
from athena_mcp.mythic_strata_runtime import MythicStrataRuntime


ATHENA_PACKET_BLOB = "1dabde8f450f237d28cf230ff2bb5d9e8d729c8e"
MCP_BASE_HEAD = "c2ada312c6d670f3b829bb8aa95f6be06bbaf6f2"
RUNTIME_BLOB = "20fcb814ba9c66547ed28be53a30c0fa82ce68bc"

LAYER_SOURCE_SCOPES = {
    "H01.S0.GRAPHIC_SYMBOLS": "PUBLIC_TEXTUAL_MODEL",
    "H01.S1.HEXAGRAM_LINE_STATEMENTS": "PUBLIC_TEXTUAL_MODEL",
    "H01.S2.TEN_WINGS": "PUBLIC_TEXTUAL_MODEL",
    "H01.S3.ZHU_XI_COMMENTARY": "PUBLIC_TEXTUAL_MODEL",
    "H02.S0.PREMODERN": "HISTORICAL_TRADITION_SCOPE",
    "H02.S1.EARLY_MODERN_SAFEDIAN": "HISTORICAL_TRADITION_SCOPE",
    "H02.S2.MODERN": "MODERN_HISTORICAL_TRADITION_SCOPE",
    "H03.S0.ARABIC_SOURCES": "HISTORICAL_SCHOLARLY_SOURCE_SCOPE",
    "H03.S1.HEBREW_IBN_EZRA": "HISTORICAL_SCHOLARLY_SOURCE_SCOPE",
    "H03.S2.LATIN_RECEPTION": "HISTORICAL_SCHOLARLY_SOURCE_SCOPE",
}

# Raw case inputs transcribed from the frozen packet. No expected labels live here.
CASES = [
    {
        "case_id": "HOL-H01-01",
        "path": ["H01.S0.GRAPHIC_SYMBOLS", "H01.S1.HEXAGRAM_LINE_STATEMENTS"],
        "operation": "SEMANTIC_TRANSPORT",
        "source_refs": ["SRC.SEP.YIJING"],
        "bridge_invariants": ["hexagram identity remains addressable"],
        "declared_loss": ["graphic symbolic role is expanded by textual statements"],
    },
    {
        "case_id": "HOL-H01-02",
        "path": ["H01.S1.HEXAGRAM_LINE_STATEMENTS", "H01.S2.TEN_WINGS"],
        "operation": "SEMANTIC_TRANSPORT",
        "source_refs": ["SRC.SEP.YIJING"],
        "bridge_invariants": ["hexagram/line materials remain objects of interpretation"],
        "declared_loss": ["later philosophical/cosmological commentary changes decoder role"],
    },
    {
        "case_id": "HOL-H01-03",
        "path": ["H01.S2.TEN_WINGS", "H01.S3.ZHU_XI_COMMENTARY"],
        "operation": "SEMANTIC_TRANSPORT",
        "source_refs": ["SRC.SEP.YIJING"],
        "bridge_invariants": ["classic and commentary remain distinguishable textual strata"],
        "declared_loss": ["later commentary retrospectively reorganizes earlier materials"],
    },
    {
        "case_id": "HOL-H01-04",
        "path": [
            "H01.S0.GRAPHIC_SYMBOLS",
            "H01.S1.HEXAGRAM_LINE_STATEMENTS",
            "H01.S2.TEN_WINGS",
            "H01.S3.ZHU_XI_COMMENTARY",
            "H01.S0.GRAPHIC_SYMBOLS",
        ],
        "operation": "HOLONOMY_LOOP",
        "source_refs": ["SRC.SEP.YIJING"],
        "bridge_invariants": ["original graphic address remains identifiable"],
        "declared_loss": ["statement, philosophical and meta-commentarial role changes cannot be projected back as original-role identity"],
    },
    {
        "case_id": "HOL-H01-05",
        "path": ["H01.S0.GRAPHIC_SYMBOLS", "H01.S0.GRAPHIC_SYMBOLS"],
        "operation": "SAME_LAYER_CONTROL",
        "source_refs": ["SRC.SEP.YIJING"],
    },
    {
        "case_id": "HOL-H02-01",
        "path": ["H02.S0.PREMODERN", "H02.S1.EARLY_MODERN_SAFEDIAN"],
        "operation": "SEMANTIC_TRANSPORT",
        "source_refs": ["SRC.CAMBRIDGE.GARB.KABBALAH.2020"],
        "bridge_invariants": ["selected exegetical/theosophical continuities remain source-supported"],
        "declared_loss": ["early-modern schools/canonization change historical context and emphasis"],
    },
    {
        "case_id": "HOL-H02-02",
        "path": ["H02.S1.EARLY_MODERN_SAFEDIAN", "H02.S2.MODERN"],
        "operation": "SEMANTIC_TRANSPORT",
        "source_refs": ["SRC.CAMBRIDGE.GARB.KABBALAH.2020"],
        "bridge_invariants": ["some recurrent themes remain historically connected"],
        "declared_loss": ["modern technologies, social forms, vernacularization and historical conditions produce autonomous modern configurations"],
    },
    {
        "case_id": "HOL-H02-03",
        "path": ["H02.S2.MODERN", "H02.S0.PREMODERN"],
        "operation": "SEMANTIC_EQUIVALENCE",
        "source_refs": ["SRC.CAMBRIDGE.GARB.KABBALAH.2020"],
    },
    {
        "case_id": "HOL-H02-04",
        "path": [
            "H02.S0.PREMODERN",
            "H02.S1.EARLY_MODERN_SAFEDIAN",
            "H02.S2.MODERN",
            "H02.S0.PREMODERN",
        ],
        "operation": "HOLONOMY_LOOP",
        "source_refs": ["SRC.CAMBRIDGE.GARB.KABBALAH.2020"],
        "bridge_invariants": ["preserve explicitly source-backed continuities"],
        "declared_loss": ["autonomy and modern transformations prevent lossless return to premodern role/context"],
    },
    {
        "case_id": "HOL-H02-05",
        "path": ["H02.S0.PREMODERN", "H02.S0.PREMODERN"],
        "operation": "SAME_LAYER_CONTROL",
        "source_refs": ["SRC.CAMBRIDGE.GARB.KABBALAH.2020"],
    },
    {
        "case_id": "HOL-H03-01",
        "path": ["H03.S0.ARABIC_SOURCES", "H03.S1.HEBREW_IBN_EZRA"],
        "operation": "SEMANTIC_TRANSPORT",
        "source_refs": ["SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"],
        "bridge_invariants": ["documented Arabic-source lineage remains attached"],
        "declared_loss": ["selection/translation/reformulation in the Hebrew transmission layer"],
    },
    {
        "case_id": "HOL-H03-02",
        "path": ["H03.S1.HEBREW_IBN_EZRA", "H03.S2.LATIN_RECEPTION"],
        "operation": "SEMANTIC_TRANSPORT",
        "source_refs": ["SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"],
        "bridge_invariants": ["Ibn Ezra work/source lineage remains traceable"],
        "declared_loss": ["language, audience and reception context change across Hebrew-to-Latin translation"],
    },
    {
        "case_id": "HOL-H03-03",
        "path": ["H03.S0.ARABIC_SOURCES", "H03.S2.LATIN_RECEPTION"],
        "operation": "SEMANTIC_EQUIVALENCE",
        "source_refs": ["SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"],
    },
    {
        "case_id": "HOL-H03-04",
        "path": ["H03.S0.ARABIC_SOURCES", "H03.S1.HEBREW_IBN_EZRA", "H03.S2.LATIN_RECEPTION"],
        "operation": "PATH_ORDER_COMPARE",
        "source_refs": ["SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"],
        "bridge_invariants": ["documented transmission order is part of provenance"],
        "declared_loss": ["permuting Arabic->Hebrew->Latin order destroys the documented transmission path"],
    },
    {
        "case_id": "HOL-H03-05",
        "path": ["H03.S1.HEBREW_IBN_EZRA", "H03.S1.HEBREW_IBN_EZRA"],
        "operation": "SAME_LAYER_CONTROL",
        "source_refs": ["SRC.CAMBRIDGE.GOLDSTEIN.IBN_EZRA"],
    },
]

# Frozen labels are intentionally physically separate from probe inputs.
EXPECTED = {
    "HOL-H01-01": "ALLOW_WITH_LOSS",
    "HOL-H01-02": "ALLOW_WITH_LOSS",
    "HOL-H01-03": "ALLOW_WITH_LOSS",
    "HOL-H01-04": "NONZERO_HOLONOMY_EXPECTED",
    "HOL-H01-05": "ZERO_HOLONOMY_CONTROL",
    "HOL-H02-01": "ALLOW_WITH_LOSS",
    "HOL-H02-02": "ALLOW_WITH_LOSS",
    "HOL-H02-03": "HOLD_EQUIVALENCE",
    "HOL-H02-04": "NONZERO_HOLONOMY_EXPECTED",
    "HOL-H02-05": "ZERO_HOLONOMY_CONTROL",
    "HOL-H03-01": "ALLOW_WITH_LOSS",
    "HOL-H03-02": "ALLOW_WITH_LOSS",
    "HOL-H03-03": "HOLD_EQUIVALENCE",
    "HOL-H03-04": "NONCOMMUTATIVE_EXPECTED",
    "HOL-H03-05": "ZERO_HOLONOMY_CONTROL",
}


def layer(layer_id: str) -> dict:
    return {
        "layer_id": layer_id,
        "standing": "SECONDARY_SCHOLARSHIP",
        "category_scope": "UNKNOWN",
        "corpus_mutability": "UNKNOWN",
        "authorization_scope": "UNKNOWN",
        "source_scope": LAYER_SOURCE_SCOPES[layer_id],
    }


def bridge_for(case: dict) -> dict:
    return {
        "source_ref": "|".join(case["source_refs"]),
        "evidence_standing": "SECONDARY_SCHOLARSHIP",
        "invariants": list(case["bridge_invariants"]),
        "transform_loss": list(case["declared_loss"]),
        "authority": "SCHOLARLY_MAPPING",
    }


def compact(receipt: dict) -> dict:
    return {
        "status": receipt["status"],
        "allowed": receipt["allowed"],
        "source_layer": receipt["source"]["layer_id"],
        "target_layer": receipt["target"]["layer_id"],
        "transform_loss": list(receipt.get("transform_loss", [])),
        "execution_authority": receipt["execution_authority"],
        "mck_v2_promotion": receipt["mck_v2_promotion"],
    }


def run_edges(runtime: MythicStrataRuntime, path: list[str], bridge: dict) -> list[dict]:
    return [
        compact(
            runtime.transport(
                layer(a),
                layer(b),
                "SEMANTIC_TRANSPORT",
                explicit_bridge=copy.deepcopy(bridge),
            )
        )
        for a, b in zip(path, path[1:])
    ]


def probe_case(runtime: MythicStrataRuntime, case: dict) -> dict:
    path = list(case["path"])
    operation = case["operation"]

    if operation == "SEMANTIC_TRANSPORT":
        receipt = compact(
            runtime.transport(
                layer(path[0]),
                layer(path[-1]),
                "SEMANTIC_TRANSPORT",
                explicit_bridge=bridge_for(case),
            )
        )
        classification = "ALLOW_WITH_LOSS" if receipt["status"] == "BRIDGE_ALLOWED_WITH_LOSS" else receipt["status"]
        return {"case_id": case["case_id"], "classification": classification, "receipts": [receipt]}

    if operation == "SEMANTIC_EQUIVALENCE":
        receipt = compact(runtime.transport(layer(path[0]), layer(path[-1]), "SEMANTIC_EQUIVALENCE"))
        classification = "HOLD_EQUIVALENCE" if receipt["status"] == "HOLD_CROSS_LAYER_EQUIVALENCE" else receipt["status"]
        return {"case_id": case["case_id"], "classification": classification, "receipts": [receipt]}

    if operation == "SAME_LAYER_CONTROL":
        receipt = compact(runtime.transport(layer(path[0]), layer(path[-1]), "SEMANTIC_TRANSPORT"))
        classification = "ZERO_HOLONOMY_CONTROL" if receipt["status"] == "WITHIN_LAYER_ALLOWED" else receipt["status"]
        return {
            "case_id": case["case_id"],
            "classification": classification,
            "receipts": [receipt],
            "holonomy_vector": None,
        }

    if operation == "HOLONOMY_LOOP":
        receipts = run_edges(runtime, path, bridge_for(case))
        all_admitted = all(r["status"] == "BRIDGE_ALLOWED_WITH_LOSS" for r in receipts)
        return {
            "case_id": case["case_id"],
            "classification": "PATH_COMPOSITION_UNAVAILABLE" if all_admitted and "HOLONOMY_LOOP" not in OPERATIONS else "LOOP_EDGE_HOLD",
            "receipts": receipts,
            "holonomy_vector": None,
            "native_holonomy_operation": "HOLONOMY_LOOP" in OPERATIONS,
        }

    if operation == "PATH_ORDER_COMPARE":
        b = bridge_for(case)
        canonical = run_edges(runtime, path, b)
        # Deliberately permute Arabic -> Hebrew -> Latin into Arabic -> Latin -> Hebrew.
        permuted_path = [path[0], path[2], path[1]]
        permuted = run_edges(runtime, permuted_path, b)
        canonical_admitted = all(r["status"] == "BRIDGE_ALLOWED_WITH_LOSS" for r in canonical)
        permuted_admitted = all(r["status"] == "BRIDGE_ALLOWED_WITH_LOSS" for r in permuted)
        order_sensitive = canonical_admitted != permuted_admitted
        return {
            "case_id": case["case_id"],
            "classification": "NONCOMMUTATIVE_DETECTED" if order_sensitive else "ORDER_NOT_COMPOSED",
            "receipts": canonical,
            "permuted_receipts": permuted,
            "canonical_admitted": canonical_admitted,
            "permuted_admitted": permuted_admitted,
            "path_order_sensitive": order_sensitive,
            "native_path_order_operation": "PATH_ORDER_COMPARE" in OPERATIONS,
        }

    raise AssertionError(f"unhandled operation: {operation}")


def probe_all() -> dict[str, dict]:
    runtime = MythicStrataRuntime()
    return {case["case_id"]: probe_case(runtime, case) for case in CASES}


def canonical_raw(raw: dict[str, dict]) -> str:
    return json.dumps(raw, sort_keys=True, separators=(",", ":"))


def all_receipts(result: dict) -> list[dict]:
    return list(result.get("receipts", [])) + list(result.get("permuted_receipts", []))


class MythicHolonomyProductionRuntimeProbeTests(unittest.TestCase):
    def test_frozen_geometry_replays_all_15_case_ids(self):
        raw = probe_all()
        self.assertEqual(len(CASES), 15)
        self.assertEqual(set(raw), set(EXPECTED))
        self.assertEqual(ATHENA_PACKET_BLOB, "1dabde8f450f237d28cf230ff2bb5d9e8d729c8e")
        self.assertEqual(STRATA_VERSION, "MCK.STRATA.RUNTIME.V0")

    def test_post_execution_assay_exposes_exact_a1_boundary(self):
        raw = probe_all()
        matches = {case_id for case_id, result in raw.items() if result["classification"] == EXPECTED[case_id]}
        mismatches = set(raw) - matches
        self.assertEqual(len(matches), 12)
        self.assertEqual(mismatches, {"HOL-H01-04", "HOL-H02-04", "HOL-H03-04"})

    def test_answer_key_mutation_cannot_change_raw_runtime_receipts(self):
        before = canonical_raw(probe_all())
        poisoned = {case_id: "DELIBERATELY_WRONG" for case_id in EXPECTED}
        with patch.dict(EXPECTED, poisoned, clear=True):
            after = canonical_raw(probe_all())
        self.assertEqual(before, after)

    def test_native_protocol_has_no_loop_or_path_order_operation(self):
        self.assertNotIn("HOLONOMY_LOOP", OPERATIONS)
        self.assertNotIn("PATH_ORDER_COMPARE", OPERATIONS)
        raw = probe_all()
        self.assertIsNone(raw["HOL-H01-04"]["holonomy_vector"])
        self.assertIsNone(raw["HOL-H02-04"]["holonomy_vector"])

    def test_bridge_contract_is_not_endpoint_bound(self):
        properties = BRIDGE["properties"]
        self.assertNotIn("source_layer_id", properties)
        self.assertNotIn("target_layer_id", properties)

        h03_order = next(c for c in CASES if c["case_id"] == "HOL-H03-04")
        b = bridge_for(h03_order)
        runtime = MythicStrataRuntime()
        noncanonical = run_edges(
            runtime,
            ["H03.S0.ARABIC_SOURCES", "H03.S2.LATIN_RECEPTION", "H03.S1.HEBREW_IBN_EZRA"],
            b,
        )
        self.assertTrue(all(r["status"] == "BRIDGE_ALLOWED_WITH_LOSS" for r in noncanonical))

    def test_h03_canonical_and_permuted_paths_are_not_distinguished(self):
        raw = probe_all()["HOL-H03-04"]
        self.assertTrue(raw["canonical_admitted"])
        self.assertTrue(raw["permuted_admitted"])
        self.assertFalse(raw["path_order_sensitive"])
        self.assertEqual(raw["classification"], "ORDER_NOT_COMPOSED")

    def test_runtime_never_mints_execution_authority_or_v2_promotion(self):
        raw = probe_all()
        receipts = [receipt for result in raw.values() for receipt in all_receipts(result)]
        self.assertGreater(len(receipts), 15)
        self.assertTrue(all(r["execution_authority"] == "NONE" for r in receipts))
        self.assertTrue(all(r["mck_v2_promotion"] is False for r in receipts))
        self.assertFalse(any(r["status"] == "HOLD_STANDING_ESCALATION" for r in receipts))

    def test_direct_transport_loss_is_retained_on_all_seven_lawful_cases(self):
        raw = probe_all()
        direct_ids = [c["case_id"] for c in CASES if c["operation"] == "SEMANTIC_TRANSPORT"]
        self.assertEqual(len(direct_ids), 7)
        for case_id in direct_ids:
            receipt = raw[case_id]["receipts"][0]
            self.assertEqual(receipt["status"], "BRIDGE_ALLOWED_WITH_LOSS")
            self.assertTrue(receipt["transform_loss"])


if __name__ == "__main__":
    unittest.main()

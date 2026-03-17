"""
test_roundtrip.py -- Roundtrip integration tests for the Athena Process Language Compiler.

Tests the full compilation pipeline from raw EVA text through tokenisation,
parsing, IR construction, rendering (all 4 backends), verification, and
packaging.  Uses actual Voynich manuscript data from folio f106v.

Run with:
    python -m pytest athena_process_compiler/tests/test_roundtrip.py -v
    python -m unittest athena_process_compiler.tests.test_roundtrip -v
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

# Ensure the rosetta_machine directory is on sys.path so imports resolve.
_ROSETTA_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROSETTA_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROSETTA_ROOT))

from athena_process_compiler.parsers.eva_tokenizer import tokenize, split_eva_line
from athena_process_compiler.parsers.vml_slot_parser import SlotParser, parse_token
from athena_process_compiler.parsers.ambiguity import resolve_candidates
from athena_process_compiler.compilers.ir_builder import IRBuilder, build_ir
from athena_process_compiler.compilers.corridor_router import CorridorRouter, route
from athena_process_compiler.renderers import RENDERERS
from athena_process_compiler.renderers.english import EnglishRenderer
from athena_process_compiler.renderers.chemistry import ChemistryRenderer
from athena_process_compiler.renderers.math_native import MathNativeRenderer
from athena_process_compiler.renderers.music_native import MusicNativeRenderer
from athena_process_compiler.verifiers.consistency import check_consistency
from athena_process_compiler.schemas.tokens import RawToken, ParsedToken, ParseCandidate
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle

# Import the MVP entry point.
from athena_vml_mvp import AthenaCompiler


# ---------------------------------------------------------------------------
# Test data from Voynich manuscript folio f106v
# ---------------------------------------------------------------------------

# Actual EVA transcription lines from f106v (pharmaceutical section, Book V).
F106V_LINE_1 = "fshedy.qokeedy.ol.kaiin.shor.oky"
F106V_LINE_2 = "shedy.qokeedy.chol.daiin"
F106V_LINE_3 = "otedy.shedy.qokaiin.chedy.dal"

F106V_CONTEXT = {
    "folio": "f106v",
    "paragraph": "P.1",
    "book": "V",
    "section": "pharmaceutical",
}

# Individual EVA tokens known to appear in f106v.
KNOWN_TOKENS = [
    "kaiin",    # seal family (S) -- one of the most common VMS words
    "daiin",    # checkpoint family (Q)
    "shor",     # contains heat/drive root 'sho' (H)
    "ol",       # common short word
    "dal",      # fix family (D)
    "chol",     # contains 'ch' prefix
    "oky",      # contains recirculate root 'ok' (R)
]


# ===========================================================================
# Test: EVA tokenisation
# ===========================================================================

class TestEVATokenisation(unittest.TestCase):
    """Tests for the EVA tokenizer stage."""

    def test_split_eva_line_dot_delimited(self):
        """split_eva_line correctly splits dot-delimited EVA text."""
        words = split_eva_line("fshedy.qokeedy.ol.kaiin.shor.oky")
        self.assertEqual(words, ["fshedy", "qokeedy", "ol", "kaiin", "shor", "oky"])

    def test_split_eva_line_space_delimited(self):
        """split_eva_line handles space-delimited text."""
        words = split_eva_line("fshedy qokeedy ol")
        self.assertEqual(words, ["fshedy", "qokeedy", "ol"])

    def test_split_eva_line_mixed_delimiters(self):
        """split_eva_line handles mixed dots and spaces."""
        words = split_eva_line("fshedy.qokeedy ol.kaiin")
        self.assertEqual(words, ["fshedy", "qokeedy", "ol", "kaiin"])

    def test_split_empty_string(self):
        """split_eva_line returns empty list for empty input."""
        self.assertEqual(split_eva_line(""), [])
        self.assertEqual(split_eva_line("   "), [])

    def test_tokenize_produces_raw_tokens(self):
        """tokenize() returns RawToken objects with correct metadata."""
        tokens = tokenize(
            "kaiin.daiin.dal",
            folio="f106v",
            paragraph="P.1",
            line="01",
        )
        self.assertEqual(len(tokens), 3)
        self.assertIsInstance(tokens[0], RawToken)
        self.assertEqual(tokens[0].text, "kaiin")
        self.assertEqual(tokens[0].folio, "f106v")
        self.assertEqual(tokens[0].paragraph, "P.1")
        self.assertEqual(tokens[0].line, "01")

    def test_tokenize_source_ids_are_unique(self):
        """Each token receives a unique source_id."""
        tokens = tokenize("kaiin.daiin.dal.ol", folio="f106v", line="01")
        source_ids = [t.source_id for t in tokens]
        self.assertEqual(len(source_ids), len(set(source_ids)))

    def test_tokenize_f106v_line_1(self):
        """Tokenise the actual first line of f106v."""
        tokens = tokenize(F106V_LINE_1, folio="f106v", paragraph="P.1", line="01")
        self.assertEqual(len(tokens), 6)
        texts = [t.text for t in tokens]
        self.assertEqual(texts, ["fshedy", "qokeedy", "ol", "kaiin", "shor", "oky"])


# ===========================================================================
# Test: Morphological parsing
# ===========================================================================

class TestMorphologicalParsing(unittest.TestCase):
    """Tests for the VML slot parser and ambiguity resolution."""

    def setUp(self):
        self.parser = SlotParser()

    def test_parse_known_root_kaiin(self):
        """'kaiin' is an exact match for seal family (S)."""
        raw = RawToken(
            text="kaiin", folio="f106v", paragraph="P.1",
            line="01", source_id="f106v:P.1:01:0003",
        )
        parsed = self.parser.parse(raw)
        self.assertIsInstance(parsed, ParsedToken)
        self.assertGreater(len(parsed.candidates), 0)
        # kaiin should match the S (seal) family with high confidence.
        top = parsed.candidates[0]
        self.assertEqual(top.root, "kaiin")
        self.assertGreaterEqual(top.confidence, 0.80)

    def test_parse_known_root_daiin(self):
        """'daiin' is an exact match for checkpoint family (Q)."""
        raw = RawToken(
            text="daiin", folio="f106v", paragraph="P.1",
            line="01", source_id="f106v:P.1:01:0003",
        )
        parsed = self.parser.parse(raw)
        top = parsed.candidates[0]
        self.assertEqual(top.root, "daiin")
        self.assertGreaterEqual(top.confidence, 0.80)

    def test_parse_generates_candidates(self):
        """Parser produces at least one candidate for any input."""
        raw = RawToken(
            text="fshedy", folio="f106v", paragraph="P.1",
            line="01", source_id="f106v:P.1:01:0000",
        )
        parsed = self.parser.parse(raw)
        self.assertGreater(len(parsed.candidates), 0)
        self.assertIsNotNone(parsed.selected)

    def test_parse_unknown_token_gets_fallback(self):
        """A completely unknown glyph-word still receives a candidate."""
        raw = RawToken(
            text="zzzzxxx", folio="test", paragraph="P0",
            line="00", source_id="test:P0:00:0000",
        )
        parsed = self.parser.parse(raw)
        self.assertGreater(len(parsed.candidates), 0)
        # Fallback should have low confidence.
        self.assertLessEqual(parsed.candidates[0].confidence, 0.50)

    def test_parse_status_assigned(self):
        """Every parsed token has a truth status set."""
        for word in KNOWN_TOKENS:
            raw = RawToken(
                text=word, folio="f106v", paragraph="P.1",
                line="01", source_id="f106v:P.1:01:test",
            )
            parsed = self.parser.parse(raw)
            self.assertIn(parsed.status, ("OK", "NEAR", "AMBIG", "FAIL"))

    def test_ambiguity_resolution(self):
        """resolve_candidates processes a token sequence without error."""
        tokens = tokenize(F106V_LINE_1, folio="f106v", paragraph="P.1", line="01")
        parsed = self.parser.parse_many(tokens)
        resolved = resolve_candidates(parsed)
        self.assertEqual(len(resolved), len(tokens))
        for pt in resolved:
            self.assertIsNotNone(pt.selected_index)

    def test_candidates_sorted_by_confidence(self):
        """Candidates are always sorted by descending confidence."""
        raw = RawToken(
            text="qokeedy", folio="f106v", paragraph="P.1",
            line="01", source_id="f106v:P.1:01:0001",
        )
        parsed = self.parser.parse(raw)
        confidences = [c.confidence for c in parsed.candidates]
        self.assertEqual(confidences, sorted(confidences, reverse=True))


# ===========================================================================
# Test: IR construction
# ===========================================================================

class TestIRConstruction(unittest.TestCase):
    """Tests for the IR builder and corridor router."""

    def _make_ir_chain(self, eva_line: str) -> list[OperatorIR]:
        """Helper: run tokenise -> parse -> build_ir on a line."""
        tokens = tokenize(eva_line, folio="f106v", paragraph="P.1", line="01")
        parser = SlotParser()
        parsed = parser.parse_many(tokens)
        resolved = resolve_candidates(parsed)
        return build_ir(resolved, book="V", lens="pharmaceutical")

    def test_build_ir_produces_operator_nodes(self):
        """build_ir returns OperatorIR objects for every parsed token."""
        ir = self._make_ir_chain(F106V_LINE_1)
        self.assertEqual(len(ir), 6)
        for node in ir:
            self.assertIsInstance(node, OperatorIR)

    def test_ir_addresses_sequential(self):
        """Crystal addresses have sequential position counters."""
        ir = self._make_ir_chain("kaiin.daiin.dal")
        positions = [node.address.split(".")[-1] for node in ir]
        self.assertEqual(positions, ["0000", "0001", "0002"])

    def test_ir_elements_assigned(self):
        """Every IR node has a non-empty element."""
        ir = self._make_ir_chain(F106V_LINE_1)
        for node in ir:
            self.assertIn(
                node.element,
                ("earth", "water", "fire", "air", "void"),
            )

    def test_ir_corridor_tags_present(self):
        """Every IR node has at least one corridor tag."""
        ir = self._make_ir_chain(F106V_LINE_1)
        for node in ir:
            self.assertGreater(len(node.corridor_tags), 0)

    def test_ir_burden_assigned(self):
        """Every IR node has a valid burden level."""
        ir = self._make_ir_chain(F106V_LINE_1)
        for node in ir:
            self.assertIn(node.burden, ("OK", "NEAR", "AMBIG", "FAIL"))

    def test_corridor_router_returns_routed_tokens(self):
        """Corridor router returns RoutedToken objects with routing metadata."""
        ir = self._make_ir_chain(F106V_LINE_1)
        routed = route(ir)
        self.assertEqual(len(routed), len(ir))
        # Each routed token should have an ir attribute with an OperatorIR.
        for rt in routed:
            self.assertIsInstance(rt.ir, OperatorIR)
            self.assertTrue(hasattr(rt, "crystal_address"))
            self.assertTrue(hasattr(rt, "element"))
            self.assertTrue(hasattr(rt, "corridor_id"))

    def test_ir_builder_book_and_lens(self):
        """IRBuilder respects the book and lens parameters."""
        tokens = tokenize("kaiin", folio="f106v", paragraph="P.1", line="01")
        parser = SlotParser()
        parsed = parser.parse_many(tokens)
        ir = build_ir(parsed, book="V", lens="pharmaceutical")
        self.assertTrue(ir[0].address.startswith("V."))
        self.assertEqual(ir[0].lens, "pharmaceutical")


# ===========================================================================
# Test: All 4 renderers produce output
# ===========================================================================

class TestRenderers(unittest.TestCase):
    """Tests that all four rendering backends produce valid NativeRender output."""

    @classmethod
    def setUpClass(cls):
        """Build a shared IR chain for all renderer tests."""
        tokens = tokenize(F106V_LINE_1, folio="f106v", paragraph="P.1", line="01")
        parser = SlotParser()
        parsed = parser.parse_many(tokens)
        resolved = resolve_candidates(parsed)
        cls.ir_chain = build_ir(resolved, book="V", lens="pharmaceutical")

    def test_registry_has_four_backends(self):
        """The RENDERERS registry contains all four backends."""
        self.assertIn("english", RENDERERS)
        self.assertIn("chemistry", RENDERERS)
        self.assertIn("math", RENDERERS)
        self.assertIn("music", RENDERERS)

    def test_english_renderer_chain(self):
        """EnglishRenderer.render_chain produces a NativeRender with content."""
        renderer = EnglishRenderer()
        result = renderer.render_chain(self.ir_chain)
        self.assertIsInstance(result, NativeRender)
        self.assertEqual(result.backend, "english")
        self.assertIsInstance(result.content, str)
        self.assertGreater(len(result.content), 0)
        self.assertIn(result.status, ("OK", "NEAR", "AMBIG", "FAIL"))

    def test_chemistry_renderer_chain(self):
        """ChemistryRenderer.render_chain produces a NativeRender with content."""
        renderer = ChemistryRenderer()
        result = renderer.render_chain(self.ir_chain)
        self.assertIsInstance(result, NativeRender)
        self.assertEqual(result.backend, "chemistry")
        self.assertGreater(len(result.content), 0)

    def test_math_renderer_chain(self):
        """MathNativeRenderer.render_chain produces a NativeRender with content."""
        renderer = MathNativeRenderer()
        result = renderer.render_chain(self.ir_chain)
        self.assertIsInstance(result, NativeRender)
        self.assertEqual(result.backend, "math")
        self.assertGreater(len(result.content), 0)

    def test_music_renderer_chain(self):
        """MusicNativeRenderer.render_chain produces a NativeRender with content."""
        renderer = MusicNativeRenderer()
        result = renderer.render_chain(self.ir_chain)
        self.assertIsInstance(result, NativeRender)
        self.assertEqual(result.backend, "music")
        self.assertGreater(len(result.content), 0)

    def test_all_renderers_produce_invariants(self):
        """Every renderer populates the invariants dict with the operator skeleton."""
        for name, cls in RENDERERS.items():
            renderer = cls()
            result = renderer.render_chain(self.ir_chain)
            self.assertIn("operators", result.invariants, msg=f"{name} missing operators")
            self.assertIn("carriers", result.invariants, msg=f"{name} missing carriers")
            self.assertIn("elements", result.invariants, msg=f"{name} missing elements")
            self.assertIn("chain_len", result.invariants, msg=f"{name} missing chain_len")
            self.assertEqual(
                result.invariants["chain_len"], len(self.ir_chain),
                msg=f"{name} chain_len mismatch",
            )

    def test_render_one_per_node(self):
        """Each backend's render_one produces output for individual nodes."""
        for name, cls in RENDERERS.items():
            renderer = cls()
            for node in self.ir_chain:
                result = renderer.render_one(node)
                self.assertIsInstance(result, NativeRender, msg=f"{name} render_one failed")
                self.assertGreater(len(str(result.content)), 0, msg=f"{name} empty content")

    def test_empty_chain_does_not_crash(self):
        """Renderers handle empty chains gracefully."""
        for name, cls in RENDERERS.items():
            renderer = cls()
            result = renderer.render_chain([])
            self.assertIsInstance(result, NativeRender, msg=f"{name} crashed on empty chain")


# ===========================================================================
# Test: Verification produces bundles
# ===========================================================================

class TestVerification(unittest.TestCase):
    """Tests for the cross-backend verification stage."""

    @classmethod
    def setUpClass(cls):
        """Build a shared IR chain and per-node renders for verification tests."""
        tokens = tokenize(F106V_LINE_1, folio="f106v", paragraph="P.1", line="01")
        parser = SlotParser()
        parsed = parser.parse_many(tokens)
        resolved = resolve_candidates(parsed)
        cls.ir_chain = build_ir(resolved, book="V", lens="pharmaceutical")

        # Build per-node renders for each backend.
        cls.per_node_renders: list[dict[str, NativeRender]] = []
        for node in cls.ir_chain:
            node_renders: dict[str, NativeRender] = {}
            for name, renderer_cls in RENDERERS.items():
                renderer = renderer_cls()
                node_renders[name] = renderer.render_one(node)
            cls.per_node_renders.append(node_renders)

    def test_check_consistency_returns_bundle(self):
        """check_consistency returns a VerificationBundle."""
        node = self.ir_chain[0]
        renders = self.per_node_renders[0]
        bundle = check_consistency(node, renders)
        self.assertIsInstance(bundle, VerificationBundle)

    def test_bundle_has_ir_id(self):
        """Each verification bundle references the correct IR token_id."""
        for idx, node in enumerate(self.ir_chain):
            bundle = check_consistency(node, self.per_node_renders[idx])
            self.assertEqual(bundle.ir_id, node.token_id)

    def test_bundle_consistency_score_in_range(self):
        """Cross-backend consistency score is in [0.0, 1.0]."""
        for idx, node in enumerate(self.ir_chain):
            bundle = check_consistency(node, self.per_node_renders[idx])
            self.assertGreaterEqual(bundle.cross_backend_consistency, 0.0)
            self.assertLessEqual(bundle.cross_backend_consistency, 1.0)

    def test_bundle_status_valid(self):
        """Each bundle has a valid truth status."""
        for idx, node in enumerate(self.ir_chain):
            bundle = check_consistency(node, self.per_node_renders[idx])
            self.assertIn(bundle.status, ("OK", "NEAR", "AMBIG", "FAIL"))

    def test_all_nodes_verified(self):
        """Verification produces one bundle per IR node."""
        bundles = []
        for idx, node in enumerate(self.ir_chain):
            bundles.append(check_consistency(node, self.per_node_renders[idx]))
        self.assertEqual(len(bundles), len(self.ir_chain))


# ===========================================================================
# Test: compile_chain end-to-end
# ===========================================================================

class TestCompileChainEndToEnd(unittest.TestCase):
    """Tests the AthenaCompiler.compile_chain() one-shot pipeline."""

    @classmethod
    def setUpClass(cls):
        """Run compile_chain once and share the result across tests."""
        cls.compiler = AthenaCompiler()
        cls.result = cls.compiler.compile_chain(
            raw_text=F106V_LINE_1,
            context=F106V_CONTEXT,
            backends=["english", "chemistry", "math", "music"],
        )

    def test_result_has_all_keys(self):
        """The result dict contains all expected top-level keys."""
        expected_keys = {
            "input", "context", "tokens", "parsed", "ir",
            "renders", "verification", "package",
        }
        self.assertTrue(expected_keys.issubset(self.result.keys()))

    def test_input_preserved(self):
        """The original input text is preserved in the result."""
        self.assertEqual(self.result["input"], F106V_LINE_1)

    def test_token_count_matches_words(self):
        """Token count matches the number of dot-delimited words."""
        expected = len(split_eva_line(F106V_LINE_1))
        self.assertEqual(len(self.result["tokens"]), expected)

    def test_parsed_count_matches_tokens(self):
        """Parsed token count matches raw token count."""
        self.assertEqual(len(self.result["parsed"]), len(self.result["tokens"]))

    def test_ir_count_matches_parsed(self):
        """IR node count matches parsed token count."""
        self.assertEqual(len(self.result["ir"]), len(self.result["parsed"]))

    def test_all_four_backends_in_renders(self):
        """All four requested backends appear in the renders dict."""
        self.assertIn("english", self.result["renders"])
        self.assertIn("chemistry", self.result["renders"])
        self.assertIn("math", self.result["renders"])
        self.assertIn("music", self.result["renders"])

    def test_each_backend_has_renders(self):
        """Each backend produced at least one NativeRender (the chain render)."""
        for name, renders in self.result["renders"].items():
            self.assertGreater(len(renders), 0, msg=f"{name} produced no renders")
            self.assertIsInstance(renders[0], NativeRender, msg=f"{name} type mismatch")

    def test_verification_count(self):
        """Verification produced one bundle per IR node."""
        self.assertEqual(
            len(self.result["verification"]),
            len(self.result["ir"]),
        )

    def test_verification_bundles_valid(self):
        """Each verification bundle has valid status and score."""
        for v in self.result["verification"]:
            self.assertIsInstance(v, VerificationBundle)
            self.assertIn(v.status, ("OK", "NEAR", "AMBIG", "FAIL"))
            self.assertGreaterEqual(v.cross_backend_consistency, 0.0)

    def test_package_contains_counts(self):
        """The package bundle has correct artifact counts."""
        pkg = self.result["package"]
        self.assertEqual(pkg["ir_count"], len(self.result["ir"]))
        self.assertEqual(pkg["backend_count"], len(self.result["renders"]))
        self.assertEqual(pkg["verification_count"], len(self.result["verification"]))

    def test_package_has_fingerprint(self):
        """The package bundle has a non-empty fingerprint."""
        self.assertIsInstance(self.result["package"]["fingerprint"], str)
        self.assertGreater(len(self.result["package"]["fingerprint"]), 0)

    def test_compile_chain_second_line(self):
        """compile_chain works on a different f106v line."""
        result = self.compiler.compile_chain(
            raw_text=F106V_LINE_2,
            context=F106V_CONTEXT,
            backends=["english", "chemistry"],
        )
        self.assertEqual(len(result["tokens"]), len(split_eva_line(F106V_LINE_2)))
        self.assertIn("english", result["renders"])
        self.assertIn("chemistry", result["renders"])

    def test_compile_chain_third_line(self):
        """compile_chain works on a third f106v line."""
        result = self.compiler.compile_chain(
            raw_text=F106V_LINE_3,
            context=F106V_CONTEXT,
            backends=["math", "music"],
        )
        self.assertEqual(len(result["tokens"]), len(split_eva_line(F106V_LINE_3)))
        self.assertIn("math", result["renders"])
        self.assertIn("music", result["renders"])

    def test_compile_chain_default_backends(self):
        """compile_chain defaults to all four backends when none specified."""
        compiler = AthenaCompiler()
        result = compiler.compile_chain(
            raw_text="kaiin.dal",
            context={"folio": "f106v", "paragraph": "P.1"},
        )
        self.assertEqual(len(result["renders"]), 4)


# ===========================================================================
# Test: Individual pipeline stages via AthenaCompiler
# ===========================================================================

class TestIndividualStages(unittest.TestCase):
    """Tests that individual AthenaCompiler methods work in isolation."""

    def setUp(self):
        self.compiler = AthenaCompiler()

    def test_ingest_returns_raw_tokens(self):
        """ingest() returns a list of RawToken objects."""
        tokens = self.compiler.ingest("kaiin.dal", {"folio": "f106v"})
        self.assertEqual(len(tokens), 2)
        self.assertIsInstance(tokens[0], RawToken)

    def test_parse_returns_parsed_tokens(self):
        """parse() returns a list of ParsedToken objects."""
        tokens = self.compiler.ingest("kaiin.dal.shor", {"folio": "f106v"})
        parsed = self.compiler.parse(tokens)
        self.assertEqual(len(parsed), 3)
        self.assertIsInstance(parsed[0], ParsedToken)

    def test_build_ir_returns_operator_ir(self):
        """build_ir() returns a list of OperatorIR objects."""
        tokens = self.compiler.ingest("kaiin.dal", {"folio": "f106v"})
        parsed = self.compiler.parse(tokens)
        ir = self.compiler.build_ir(parsed, F106V_CONTEXT)
        self.assertEqual(len(ir), 2)
        self.assertIsInstance(ir[0], OperatorIR)

    def test_render_returns_dict_of_lists(self):
        """render() returns a dict mapping backend names to render lists."""
        tokens = self.compiler.ingest("kaiin", {"folio": "f106v"})
        parsed = self.compiler.parse(tokens)
        ir = self.compiler.build_ir(parsed)
        renders = self.compiler.render(ir, ["english"])
        self.assertIn("english", renders)
        self.assertGreater(len(renders["english"]), 0)

    def test_verify_returns_bundles(self):
        """verify() returns VerificationBundle objects."""
        tokens = self.compiler.ingest("kaiin", {"folio": "f106v"})
        parsed = self.compiler.parse(tokens)
        ir = self.compiler.build_ir(parsed)
        renders = self.compiler.render(ir, ["english", "chemistry"])
        verification = self.compiler.verify(ir, renders)
        self.assertEqual(len(verification), len(ir))
        self.assertIsInstance(verification[0], VerificationBundle)

    def test_package_serialises_cleanly(self):
        """package() returns a JSON-serialisable dict."""
        tokens = self.compiler.ingest("kaiin", {"folio": "f106v"})
        parsed = self.compiler.parse(tokens)
        ir = self.compiler.build_ir(parsed)
        renders = self.compiler.render(ir, ["english"])
        verification = self.compiler.verify(ir, renders)
        pkg = self.compiler.package(ir, renders, verification)

        # Must be JSON-serialisable without error.
        serialised = json.dumps(pkg)
        self.assertIsInstance(serialised, str)
        self.assertGreater(len(serialised), 0)


if __name__ == "__main__":
    unittest.main()

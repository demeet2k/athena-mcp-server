"""
athena_vml_mvp.py -- First Runnable Target for the Athena Process Language Compiler.

This is the unified entry point that wires together every stage of the
compilation pipeline:

    raw EVA text
      -> ingest    (tokenise)
      -> parse     (morphological slot decomposition + ambiguity resolution)
      -> build_ir  (lower to OperatorIR with crystal addresses and corridors)
      -> render    (project through domain-native backends)
      -> verify    (cross-backend consistency check)
      -> package   (bundle into a single artifact dict)
      -> store     (persist to GAWM -- optional)

The compile_chain() method runs the entire pipeline in one call.

Usage:
    python athena_vml_mvp.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Guarded imports -- degrade gracefully if submodules have issues
# ---------------------------------------------------------------------------

try:
    from athena_process_compiler.parsers.eva_tokenizer import tokenize
except ImportError as e:
    print(f"[warn] eva_tokenizer import failed: {e}", file=sys.stderr)
    tokenize = None  # type: ignore[assignment]

try:
    from athena_process_compiler.parsers.vml_slot_parser import SlotParser
except ImportError as e:
    print(f"[warn] vml_slot_parser import failed: {e}", file=sys.stderr)
    SlotParser = None  # type: ignore[assignment, misc]

try:
    from athena_process_compiler.parsers.ambiguity import resolve_candidates
except ImportError as e:
    print(f"[warn] ambiguity import failed: {e}", file=sys.stderr)
    resolve_candidates = None  # type: ignore[assignment]

try:
    from athena_process_compiler.compilers.ir_builder import IRBuilder
except ImportError as e:
    print(f"[warn] ir_builder import failed: {e}", file=sys.stderr)
    IRBuilder = None  # type: ignore[assignment, misc]

try:
    from athena_process_compiler.compilers.corridor_router import CorridorRouter
except ImportError as e:
    print(f"[warn] corridor_router import failed: {e}", file=sys.stderr)
    CorridorRouter = None  # type: ignore[assignment, misc]

try:
    from athena_process_compiler.renderers import RENDERERS, render_all_backends
except ImportError as e:
    print(f"[warn] renderers import failed: {e}", file=sys.stderr)
    RENDERERS = {}  # type: ignore[assignment]
    render_all_backends = None  # type: ignore[assignment]

try:
    from athena_process_compiler.verifiers.consistency import check_consistency
except ImportError as e:
    print(f"[warn] consistency import failed: {e}", file=sys.stderr)
    check_consistency = None  # type: ignore[assignment]

try:
    from athena_process_compiler.storage.gawm_writer import (
        write_ir,
        write_render,
        write_verification,
        fingerprint,
    )
except ImportError as e:
    print(f"[warn] gawm_writer import failed: {e}", file=sys.stderr)
    write_ir = None  # type: ignore[assignment]
    write_render = None  # type: ignore[assignment]
    write_verification = None  # type: ignore[assignment]
    fingerprint = None  # type: ignore[assignment]

try:
    from athena_process_compiler.schemas.tokens import RawToken, ParsedToken
    from athena_process_compiler.schemas.ir import OperatorIR
    from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
except ImportError as e:
    print(f"[warn] schemas import failed: {e}", file=sys.stderr)
    RawToken = None  # type: ignore[assignment, misc]
    ParsedToken = None  # type: ignore[assignment, misc]
    OperatorIR = None  # type: ignore[assignment, misc]
    NativeRender = None  # type: ignore[assignment, misc]
    VerificationBundle = None  # type: ignore[assignment, misc]


# ---------------------------------------------------------------------------
# Book mapping for Voynich sections
# ---------------------------------------------------------------------------

_SECTION_TO_BOOK: dict[str, str] = {
    "herbal_a": "I",
    "herbal_b": "II",
    "pharmaceutical": "V",
    "biological": "III",
    "astronomical": "IV",
    "cosmological": "IV",
    "recipes": "VI",
    "stars": "IV",
}


# ---------------------------------------------------------------------------
# AthenaCompiler
# ---------------------------------------------------------------------------

class AthenaCompiler:
    """Unified compiler pipeline for the Athena Process Language.

    Each public method corresponds to one stage of the pipeline.  The
    compile_chain() method runs all stages in sequence and returns a
    single result dict.
    """

    def __init__(self) -> None:
        self._slot_parser = SlotParser() if SlotParser else None
        self._ir_builder: IRBuilder | None = None
        self._corridor_router = CorridorRouter() if CorridorRouter else None

    # -- Stage 1: Ingest (tokenise) -----------------------------------------

    def ingest(self, raw_text: str, context: dict) -> list:
        """Tokenise raw EVA text into RawToken objects.

        Args:
            raw_text: A dot-delimited EVA transcription string.
            context:  Dict with keys 'folio', 'paragraph', 'book', 'section',
                      and optionally 'line' and 'diagram_context'.

        Returns:
            A list of RawToken objects, one per glyph-word.
        """
        if tokenize is None:
            raise RuntimeError("eva_tokenizer module not available")

        folio = context.get("folio", "unknown")
        paragraph = context.get("paragraph", "P0")
        line = context.get("line", "01")
        diagram_context = context.get("diagram_context")

        return tokenize(
            raw_text,
            folio=folio,
            paragraph=paragraph,
            line=line,
            diagram_context=diagram_context,
        )

    # -- Stage 2: Parse (morphological decomposition) ----------------------

    def parse(self, tokens: list) -> list:
        """Parse RawTokens into ParsedTokens with ranked morphological candidates.

        Runs the slot parser to generate candidates, then applies the
        ambiguity resolver to select the best candidate for each token
        using elemental continuity, morphological economy, and bigram
        affinity signals.

        Args:
            tokens: A list of RawToken objects.

        Returns:
            A list of ParsedToken objects with candidates ranked and selected.
        """
        if self._slot_parser is None:
            raise RuntimeError("vml_slot_parser module not available")

        parsed = self._slot_parser.parse_many(tokens)

        # Apply ambiguity resolution if available.
        if resolve_candidates is not None:
            parsed = resolve_candidates(parsed)

        return parsed

    # -- Stage 3: Build IR (lower to OperatorIR) ---------------------------

    def build_ir(self, parsed: list, context: dict | None = None) -> list:
        """Lower ParsedTokens into OperatorIR nodes.

        Assigns crystal addresses, operator families, element quadrants,
        corridor tags, and burden levels.  Optionally routes through the
        corridor router for legality checking.

        Args:
            parsed:  A list of ParsedToken objects.
            context: Optional dict with 'book', 'section', 'lens' keys
                     to control address generation and lens assignment.

        Returns:
            A list of OperatorIR nodes.
        """
        if IRBuilder is None:
            raise RuntimeError("ir_builder module not available")

        context = context or {}
        section = context.get("section", "")
        book = context.get("book", _SECTION_TO_BOOK.get(section, "I"))
        lens = context.get("lens", section or "default")

        self._ir_builder = IRBuilder(book=book, lens=lens)
        ir_nodes = self._ir_builder.build(parsed)

        # Run corridor routing if available.
        # The router returns RoutedToken wrappers — extract enriched IR nodes.
        if self._corridor_router is not None:
            routed = self._corridor_router.route(ir_nodes)
            ir_nodes = []
            for rt in routed:
                node = rt.ir
                node.address = str(rt.crystal_address)
                node.element = rt.element
                if rt.corridor_id:
                    node.corridor_tags = [rt.corridor_id] + node.corridor_tags
                ir_nodes.append(node)

        return ir_nodes

    # -- Stage 4: Render (project through backends) ------------------------

    def render(self, ir: list, backends: list[str] | None = None) -> dict:
        """Render OperatorIR nodes through one or more domain-native backends.

        Each backend produces a NativeRender that expresses the operator
        chain in its own language (English, chemistry, math, music).

        Args:
            ir:       A list of OperatorIR nodes.
            backends: Optional list of backend names to use.  If None,
                      all registered backends are used.

        Returns:
            A dict mapping backend name to a list of NativeRender objects.
            Each backend produces one chain-level render plus per-node renders.
        """
        if not RENDERERS:
            raise RuntimeError("renderers module not available")

        target_backends = backends or list(RENDERERS.keys())
        result: dict[str, list] = {}

        for name in target_backends:
            if name not in RENDERERS:
                continue
            renderer_cls = RENDERERS[name]
            renderer = renderer_cls()

            renders: list = []

            # Chain-level render (the primary output).
            chain_render = renderer.render_chain(ir)
            renders.append(chain_render)

            # Per-node renders for fine-grained inspection.
            for node in ir:
                renders.append(renderer.render_one(node))

            result[name] = renders

        return result

    # -- Stage 5: Verify (cross-backend consistency) -----------------------

    def verify(self, ir: list, renders: dict) -> list:
        """Verify cross-backend consistency for each OperatorIR node.

        Compares each backend's per-node render against the canonical IR
        skeleton to compute a consistency score and aggregate truth verdict.

        Args:
            ir:      A list of OperatorIR nodes.
            renders: The dict returned by render(), mapping backend name
                     to lists of NativeRender objects.

        Returns:
            A list of VerificationBundle objects, one per IR node.
        """
        if check_consistency is None:
            raise RuntimeError("consistency verifier not available")

        bundles: list = []

        for idx, node in enumerate(ir):
            # Collect per-node renders across backends (skip chain-level at [0]).
            per_node_renders: dict = {}
            for backend_name, render_list in renders.items():
                # render_list[0] is the chain render; [1..] are per-node.
                node_idx = idx + 1  # offset past chain render
                if node_idx < len(render_list):
                    per_node_renders[backend_name] = render_list[node_idx]

            bundle = check_consistency(node, per_node_renders)
            bundles.append(bundle)

        return bundles

    # -- Stage 6: Package (assemble artifact bundle) -----------------------

    def package(self, ir: list, renders: dict, verification: list) -> dict:
        """Package all compilation artifacts into a single bundle dict.

        The bundle is a self-contained record of the entire compilation,
        suitable for storage or transmission.

        Args:
            ir:           List of OperatorIR nodes.
            renders:      Dict of backend name -> NativeRender lists.
            verification: List of VerificationBundle objects.

        Returns:
            A dict containing the full artifact bundle with serialised
            IR, renders, and verification data.
        """
        ir_dicts = [node.to_dict() for node in ir]

        render_dicts: dict[str, list] = {}
        for backend_name, render_list in renders.items():
            render_dicts[backend_name] = [r.to_dict() for r in render_list]

        verification_dicts = [v.to_dict() for v in verification]

        # Compute a bundle fingerprint from the IR.
        fp = ""
        if fingerprint is not None:
            fp = fingerprint({"ir": ir_dicts})

        return {
            "fingerprint": fp,
            "ir": ir_dicts,
            "renders": render_dicts,
            "verification": verification_dicts,
            "ir_count": len(ir),
            "backend_count": len(renders),
            "verification_count": len(verification),
        }

    # -- Stage 7: Store (persist to GAWM) ----------------------------------

    def store(self, artifact_bundle: dict, destination: str = "GAWM") -> str:
        """Persist the artifact bundle to the GAWM directory structure.

        Writes IR nodes, renders, and verification bundles as individual
        content-addressed JSON files.

        Args:
            artifact_bundle: The dict returned by package().
            destination:     Storage target label (currently only 'GAWM').

        Returns:
            The bundle fingerprint string.
        """
        if write_ir is None or write_render is None or write_verification is None:
            raise RuntimeError("gawm_writer module not available")

        if destination != "GAWM":
            raise ValueError(f"Unknown storage destination: {destination!r}")

        # Reconstruct and write IR nodes.
        for ir_dict in artifact_bundle.get("ir", []):
            node = OperatorIR.from_dict(ir_dict)
            write_ir(node, tags=["mvp", "compile_chain"])

        # Write renders.
        for backend_name, render_dicts in artifact_bundle.get("renders", {}).items():
            for rd in render_dicts:
                render = NativeRender.from_dict(rd)
                write_render(render, tags=["mvp", backend_name])

        # Write verification bundles.
        for vd in artifact_bundle.get("verification", []):
            vb = VerificationBundle.from_dict(vd)
            write_verification(vb, tags=["mvp", "verification"])

        return artifact_bundle.get("fingerprint", "")

    # -- One-shot pipeline -------------------------------------------------

    def compile_chain(
        self,
        raw_text: str,
        context: dict,
        backends: list[str] | None = None,
    ) -> dict:
        """Run the full compilation pipeline from raw EVA text to packaged artifacts.

        This is the primary entry point for end-to-end compilation.

        Args:
            raw_text: A dot-delimited EVA transcription string.
            context:  Dict with keys 'folio', 'paragraph', 'book', 'section'.
            backends: Optional list of backend names. Defaults to all four:
                      ['english', 'chemistry', 'math', 'music'].

        Returns:
            A dict containing:
                input        -- the original raw text
                context      -- the context dict
                tokens       -- list of RawToken objects
                parsed       -- list of ParsedToken objects
                ir           -- list of OperatorIR nodes
                renders      -- dict of backend name -> NativeRender lists
                verification -- list of VerificationBundle objects
                package      -- the full artifact bundle dict
        """
        if backends is None:
            backends = ["english", "chemistry", "math", "music"]

        # Stage 1: Ingest
        tokens = self.ingest(raw_text, context)

        # Stage 2: Parse
        parsed = self.parse(tokens)

        # Stage 3: Build IR
        ir = self.build_ir(parsed, context)

        # Stage 4: Render
        renders = self.render(ir, backends)

        # Stage 5: Verify
        verification = self.verify(ir, renders)

        # Stage 6: Package
        bundle = self.package(ir, renders, verification)

        return {
            "input": raw_text,
            "context": context,
            "tokens": tokens,
            "parsed": parsed,
            "ir": ir,
            "renders": renders,
            "verification": verification,
            "package": bundle,
        }


# ---------------------------------------------------------------------------
# __main__ -- demonstrate compiling an actual f106v EVA line
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    compiler = AthenaCompiler()

    # Example: first line of f106v
    result = compiler.compile_chain(
        raw_text="fshedy.qokeedy.ol.kaiin.shor.oky",
        context={
            "folio": "f106v",
            "paragraph": "P.1",
            "book": "V",
            "section": "pharmaceutical",
        },
        backends=["english", "chemistry", "math", "music"],
    )

    # Print results
    print("=== ATHENA PROCESS LANGUAGE COMPILER ===")
    print(f"Input: {result['input']}")
    print(f"Tokens: {len(result['tokens'])}")
    print(f"IR Objects: {len(result['ir'])}")
    print()
    for backend, renders in result["renders"].items():
        print(f"--- {backend.upper()} ---")
        for r in renders:
            print(f"  {r.content}")
    print()
    print(f"Verification: {len(result['verification'])} bundles")
    for v in result["verification"]:
        print(f"  {v.ir_id}: {v.status} (consistency: {v.cross_backend_consistency:.2f})")

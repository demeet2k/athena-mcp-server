#!/usr/bin/env python3
"""
AtlasForge Installation Verification Script

Run this to verify the framework is correctly installed and functional.
"""

import sys
import math
import tempfile


def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║               ATLAS FORGE - Installation Verification                         ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    errors = []
    
    # Test 1: Import main package
    print("1. Testing main package import...", end=" ")
    try:
        import atlasforge
        print(f"✓ v{atlasforge.__version__}")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("import", str(e)))
        return 1
    
    # Test 2: Import all symbols
    print("2. Testing symbol exports...", end=" ")
    try:
        count = len(atlasforge.__all__)
        print(f"✓ {count} symbols")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("symbols", str(e)))
    
    # Test 3: Core types
    print("3. Testing core types...", end=" ")
    try:
        from atlasforge import Interval, Pole, CertificateLevel
        I = Interval.closed(0, 1)
        assert I.contains(0.5)
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("core", str(e)))
    
    # Test 4: Solvers
    print("4. Testing solvers...", end=" ")
    try:
        from atlasforge import BrentSolver, Interval
        H = lambda x: x**2 - 2
        solver = BrentSolver(tol=1e-12)
        result = solver.solve(H, Interval.closed(1, 2))
        assert abs(result.solution - math.sqrt(2)) < 1e-10
        print(f"✓ √2 = {result.solution:.10f}")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("solvers", str(e)))
    
    # Test 5: Lenses
    print("5. Testing lenses...", end=" ")
    try:
        from atlasforge import LogLens
        log = LogLens()
        x = 10.0
        assert abs(log.inverse(log.forward(x)) - x) < 1e-10
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("lenses", str(e)))
    
    # Test 6: Certificates
    print("6. Testing certificates...", end=" ")
    try:
        from atlasforge import CertificateFactory, Interval
        cert = CertificateFactory.enclosure(1.414, Interval.closed(1.41, 1.42), 1e-6, True)
        assert cert.verify()
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("certificates", str(e)))
    
    # Test 7: Recipe Pipeline
    print("7. Testing recipe pipeline...", end=" ")
    try:
        from atlasforge import RootConstraint, Interval, Blueprint, RecipeExecutor
        H = lambda x: x**2 - 2
        constraint = RootConstraint(H=H, domain=Interval.closed(1, 2))
        blueprint = Blueprint(constraint=constraint)
        executor = RecipeExecutor()
        recipe = executor.execute(blueprint)
        assert recipe.success
        print(f"✓ success={recipe.success}")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("recipes", str(e)))
    
    # Test 8: Crystal Combat
    print("8. Testing Crystal Combat...", end=" ")
    try:
        from atlasforge import CrystalSolver, Interval
        H = lambda x: x**2 - 2
        solver = CrystalSolver(tolerance=1e-8, max_turns=100)
        result = solver.solve(H, x0=1.5, domain=Interval.closed(1, 2))
        print(f"✓ turns={result.turns}")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("crystal", str(e)))
    
    # Test 9: Hybrid System
    print("9. Testing hybrid system...", end=" ")
    try:
        from atlasforge import LinearFlow, HybridState
        flow = LinearFlow(a=-1.0, b=0.0)
        x1 = flow.integrate(1.0, 0.0, 1.0)
        assert abs(x1 - math.exp(-1)) < 1e-6
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("hybrid", str(e)))
    
    # Test 10: Utils
    print("10. Testing utilities...", end=" ")
    try:
        from atlasforge import golden_ratio, fibonacci, derivative
        phi = golden_ratio()
        assert abs(phi**2 - phi - 1) < 1e-10
        assert fibonacci(10) == 55
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("utils", str(e)))

    # Test 11: Memory bank
    print("11. Testing memory bank...", end=" ")
    try:
        from atlasforge import MemoryStore
        with tempfile.TemporaryDirectory() as td:
            store = MemoryStore(td)
            h = store.remember("test", "hello world", tags=["demo"])
            hits = store.search("hello", tags=["demo"])
            assert any(e.content_hash() == h for e in hits)
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("memory", str(e)))

    # Test 12: Atlas orchestrator
    print("12. Testing Atlas orchestrator...", end=" ")
    try:
        from atlasforge import Atlas, AtlasConfig, RootConstraint, Interval
        with tempfile.TemporaryDirectory() as td:
            atlas = Atlas(AtlasConfig(memory_dir=td))
            bp = atlas.blueprint(
                name="sqrt2",
                constraint=RootConstraint(H=lambda x: x*x - 2, domain=Interval.closed(1, 2)),
            )
            recipe = atlas.solve(bp, verified=True)
            assert recipe.success
            # We should be able to recall the stored recipe log by name
            hits = atlas.recall("sqrt2")
            assert len(hits) >= 1
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("atlas", str(e)))
    
    # Test 13: Knowledge schema + book compiler
    print("13. Testing knowledge schema + book compiler...", end=" ")
    try:
        from atlasforge import MemoryStore, AtlasBookBuilder, AtlasBookConfig
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            store = MemoryStore(td)
            h_def = store.define(
                title="Real numbers (definition)",
                statement="A real number is an element of an ordered complete field.",
                tags=["analysis"],
            )
            hits = store.search(query="ordered complete field", kind="definition", limit=10)
            assert any(e.content_hash() == h_def for e in hits)

            builder = AtlasBookBuilder(store)
            cfg = AtlasBookConfig(title="Test Atlas", include_graph_edges=True, include_crystal_map=True)
            out_md = Path(td) / "atlas.md"
            builder.export_markdown(out_md, cfg)
            assert out_md.exists()
            assert "# Test Atlas" in out_md.read_text(encoding="utf-8")

            # DOCX export
            out_docx = Path(td) / "atlas.docx"
            builder.export_docx(out_docx, cfg)
            assert out_docx.exists()

            # LaTeX export
            out_tex = Path(td) / "atlas.tex"
            builder.export_tex(out_tex, cfg)
            assert out_tex.exists()
            assert "\\documentclass" in out_tex.read_text(encoding="utf-8")

            # Crystal navigator sanity check (address parsing)
            from atlasforge import CrystalNavigator
            nav = CrystalNavigator(store)
            cell0 = nav.cell("D·□·OBJECTS·0")  # parse string -> index
            # The test data may or may not include addressed entries; just ensure no crash.
            assert cell0 is None or isinstance(cell0.index, int)
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        errors.append(("book", str(e)))


    print()
    print("=" * 60)
    
    if errors:
        print(f"VERIFICATION FAILED: {len(errors)} error(s)")
        for name, err in errors:
            print(f"  - {name}: {err}")
        return 1
    else:
        print("VERIFICATION PASSED: All systems operational!")
        print("=" * 60)
        return 0




if __name__ == "__main__":
    sys.exit(main())

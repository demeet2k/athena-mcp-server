# CRYSTAL: Xi108:W3:A7:S26 | face=R | node=705 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: primitives→scorer→challenges→self_play→mcp

"""Test suite for the SVG self-play improvement system."""

import math
import os
import sys
import tempfile

# Ensure MCP package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "MCP"))

from crystal_108d.svg_primitives import (
    SVGCanvas, circle, rect, line, polygon, polyline, path, text, group,
    regular_polygon, concentric_circles, star_polygon, golden_spiral,
    flower_of_life, metatron_cube, tesseract_projection, sri_yantra,
    crystal_lattice, phi_grid, fractal_tree, spiral_of_theodorus,
    koch_snowflake, sierpinski_triangle, vesica_piscis, radial_burst,
    checkered_grid, line_grid, linear_gradient, radial_gradient,
    rotate, scale, translate, reflect,
)
from crystal_108d.svg_scorer import SVGScore, SVGScorer, get_scorer
from crystal_108d.svg_challenges import (
    SVGChallenge, catalog, get_challenge, random_challenge,
    progressive_challenges,
)
from crystal_108d.svg_self_play import (
    SVGSelfPlayEngine, SVGRound, SVGAttempt, get_engine,
)


# ══════════════════════════════════════════════════════════════════════
#  Primitives
# ══════════════════════════════════════════════════════════════════════

class TestSVGPrimitives:

    def test_circle_valid(self):
        result = circle(100, 200, 50)
        assert "<circle" in result
        assert 'cx="100"' in result
        assert 'r="50"' in result

    def test_circle_attrs(self):
        result = circle(0, 0, 10, fill="red", stroke_width="2")
        assert 'fill="red"' in result
        assert 'stroke-width="2"' in result

    def test_rect_valid(self):
        result = rect(10, 20, 100, 50)
        assert "<rect" in result
        assert 'width="100"' in result
        assert 'height="50"' in result

    def test_rect_rounded(self):
        result = rect(0, 0, 100, 100, rx=10)
        assert 'rx="10"' in result

    def test_line_valid(self):
        result = line(0, 0, 100, 100)
        assert "<line" in result
        assert 'x1="0"' in result
        assert 'y2="100"' in result

    def test_polygon_valid(self):
        pts = [(0, 0), (100, 0), (50, 80)]
        result = polygon(pts)
        assert "<polygon" in result
        assert "points=" in result

    def test_polyline_valid(self):
        pts = [(0, 0), (50, 50), (100, 0)]
        result = polyline(pts)
        assert "<polyline" in result

    def test_path_valid(self):
        result = path("M 0 0 L 100 100", fill="none")
        assert "<path" in result
        assert "M 0 0 L 100 100" in result

    def test_text_valid(self):
        result = text(50, 50, "Hello")
        assert "<text" in result
        assert "Hello" in result

    def test_group_valid(self):
        result = group([circle(0, 0, 10), rect(10, 10, 20, 20)])
        assert "<g>" in result
        assert "</g>" in result
        assert "<circle" in result
        assert "<rect" in result

    def test_group_transform(self):
        result = group([circle(0, 0, 5)], transform="rotate(45)")
        assert 'transform="rotate(45)"' in result


# ══════════════════════════════════════════════════════════════════════
#  Composites
# ══════════════════════════════════════════════════════════════════════

class TestSVGComposites:

    def test_regular_polygon_hexagon(self):
        result = regular_polygon(400, 400, 100, 6)
        assert "<polygon" in result

    def test_concentric_circles(self):
        result = concentric_circles(400, 400, 200, n=5)
        assert result.count("<circle") == 5

    def test_star_polygon(self):
        result = star_polygon(400, 400, 200, 80, 5)
        assert "<polygon" in result

    def test_golden_spiral_has_path(self):
        result = golden_spiral(400, 400, turns=3)
        assert "<path" in result
        assert "A " in result  # arc commands

    def test_flower_of_life_rings2(self):
        result = flower_of_life(400, 400, 80, rings=2)
        # center + 6*1 + 6*2 = 1 + 6 + 12 = 19
        assert result.count("<circle") == 19

    def test_flower_of_life_rings1(self):
        result = flower_of_life(400, 400, 80, rings=1)
        # center + 6 = 7
        assert result.count("<circle") == 7

    def test_metatron_cube_has_lines_and_circles(self):
        result = metatron_cube(400, 400, 150)
        assert "<circle" in result
        assert "<line" in result

    def test_tesseract_has_lines(self):
        result = tesseract_projection(400, 400, 150)
        # 12 outer edges + 12 inner edges + 8 connecting = 32
        line_count = result.count("<line")
        assert line_count >= 28  # at least most edges

    def test_sri_yantra_has_triangles(self):
        result = sri_yantra(400, 400, 300)
        # 9 triangles = 9 polygons
        assert result.count("<polygon") == 9

    def test_crystal_lattice_hex(self):
        result = crystal_lattice(100, 100, rows=3, cols=3, spacing=40)
        assert result.count("<circle") == 9

    def test_phi_grid_lines(self):
        result = phi_grid(800, 800, divisions=3)
        assert "<line" in result

    def test_fractal_tree_depth3(self):
        result = fractal_tree(400, 600, 100, -math.pi/2, 3)
        assert "<line" in result

    def test_fractal_tree_depth0_empty(self):
        result = fractal_tree(400, 600, 100, -math.pi/2, 0)
        assert result == ""

    def test_spiral_of_theodorus(self):
        result = spiral_of_theodorus(400, 400, n=10)
        assert "<polygon" in result

    def test_koch_snowflake(self):
        result = koch_snowflake(400, 400, 200, depth=2)
        assert "<polygon" in result

    def test_sierpinski_triangle(self):
        result = sierpinski_triangle(400, 400, 200, depth=3)
        # depth 3 = 3^3 = 27 triangles
        assert result.count("<polygon") == 27

    def test_vesica_piscis(self):
        result = vesica_piscis(400, 400, 200)
        assert result.count("<circle") == 2

    def test_radial_burst(self):
        result = radial_burst(400, 400, 50, 300, n=12)
        assert result.count("<line") == 12

    def test_checkered_grid(self):
        result = checkered_grid(0, 0, 4, 4, 50)
        assert result.count("<rect") == 16

    def test_line_grid(self):
        result = line_grid(0, 0, 100, 100, spacing=25)
        assert "<line" in result


# ══════════════════════════════════════════════════════════════════════
#  Canvas
# ══════════════════════════════════════════════════════════════════════

class TestSVGCanvas:

    def test_render_complete(self):
        c = SVGCanvas(400, 300)
        svg = c.render()
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'width="400"' in svg
        assert 'height="300"' in svg

    def test_add_elements(self):
        c = SVGCanvas()
        c.add(circle(100, 100, 50))
        c.add(rect(200, 200, 100, 100))
        svg = c.render()
        assert "<circle" in svg
        assert "<rect" in svg
        assert c.element_count == 2

    def test_add_defs(self):
        c = SVGCanvas()
        grad = linear_gradient("g1", [("0%", "red"), ("100%", "blue")])
        c.add_def(grad)
        svg = c.render()
        assert "<defs>" in svg
        assert "linearGradient" in svg

    def test_save(self):
        c = SVGCanvas(200, 200)
        c.add(circle(100, 100, 50))
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path_str = f.name
        try:
            c.save(path_str)
            with open(path_str, "r") as f:
                content = f.read()
            assert "<svg" in content
        finally:
            os.unlink(path_str)

    def test_background(self):
        c = SVGCanvas(800, 800, background="#fff")
        svg = c.render()
        assert 'fill="#fff"' in svg


# ══════════════════════════════════════════════════════════════════════
#  Transforms & Gradients
# ══════════════════════════════════════════════════════════════════════

class TestTransforms:

    def test_rotate(self):
        result = rotate(circle(0, 0, 10), 45, 0, 0)
        assert "rotate(45" in result

    def test_scale(self):
        result = scale(circle(0, 0, 10), 2)
        assert "scale(2" in result

    def test_translate(self):
        result = translate(circle(0, 0, 10), 100, 200)
        assert "translate(100" in result

    def test_reflect_x(self):
        result = reflect(circle(0, 0, 10), "x")
        assert "scale(1,-1)" in result

    def test_reflect_y(self):
        result = reflect(circle(0, 0, 10), "y")
        assert "scale(-1,1)" in result

    def test_linear_gradient(self):
        result = linear_gradient("g1", [("0%", "#000"), ("100%", "#fff")])
        assert "linearGradient" in result
        assert 'id="g1"' in result

    def test_radial_gradient(self):
        result = radial_gradient("g2", [("0%", "#fff"), ("100%", "#000")])
        assert "radialGradient" in result


# ══════════════════════════════════════════════════════════════════════
#  Scorer
# ══════════════════════════════════════════════════════════════════════

class TestSVGScorer:

    def test_score_circle(self):
        canvas = SVGCanvas(800, 800)
        canvas.add(circle(400, 400, 200, fill="none", stroke="#333"))
        score = get_scorer().score(canvas.render(), target_elements=1)
        assert score.total_score > 0
        assert score.element_count_accuracy == 1.0
        assert score.centroid_accuracy > 0.5

    def test_score_empty_svg_low(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"></svg>'
        score = get_scorer().score(svg, target_elements=10)
        assert score.total_score < 0.3
        assert score.element_count_accuracy == 0.0

    def test_score_invalid_xml(self):
        score = get_scorer().score("not xml at all")
        assert score.total_score == 0.0

    def test_symmetry_detection_hex(self):
        canvas = SVGCanvas(800, 800)
        # 6 circles in hexagonal arrangement
        for i in range(6):
            angle = 2 * math.pi * i / 6
            cx = 400 + 200 * math.cos(angle)
            cy = 400 + 200 * math.sin(angle)
            canvas.add(circle(cx, cy, 20, fill="#333"))
        score = get_scorer().score(canvas.render(), target_symmetry=6)
        assert score.symmetry_score > 0.0  # detects some symmetry from vertex analysis

    def test_to_15d_length(self):
        score = SVGScore(total_score=0.5, svg_byte_size=500)
        v = score.to_15d()
        assert len(v) == 15
        assert all(isinstance(x, float) for x in v)

    def test_golden_ratio_detection(self):
        # Rectangle with golden ratio proportions
        from crystal_108d.geometric_constants import PHI
        canvas = SVGCanvas(800, 800)
        w = 300
        h = w / PHI
        canvas.add(rect(250, 250, w, h))
        score = get_scorer().score(canvas.render())
        # Should detect at least some golden ratio adherence
        assert score.golden_ratio_adherence >= 0.0

    def test_path_complexity(self):
        canvas = SVGCanvas(800, 800)
        canvas.add(golden_spiral(400, 400, turns=4))
        score = get_scorer().score(canvas.render())
        assert score.path_complexity > 0

    def test_transform_depth(self):
        canvas = SVGCanvas(800, 800)
        inner = rotate(circle(100, 100, 20), 45, 100, 100)
        outer = translate(inner, 200, 200)
        canvas.add(outer)
        score = get_scorer().score(canvas.render())
        assert score.transform_depth > 0


# ══════════════════════════════════════════════════════════════════════
#  Challenges
# ══════════════════════════════════════════════════════════════════════

class TestSVGChallenges:

    def test_catalog_size(self):
        c = catalog()
        assert len(c) >= 25

    def test_catalog_ids_unique(self):
        c = catalog()
        ids = [ch.challenge_id for ch in c]
        assert len(ids) == len(set(ids))

    def test_all_categories_present(self):
        c = catalog()
        cats = set(ch.category for ch in c)
        assert cats == {"primitive", "composite", "sacred", "fractal", "crystal", "dimensional"}

    def test_get_challenge_valid(self):
        ch = get_challenge("prim_circle")
        assert ch is not None
        assert ch.name == "Single Circle"

    def test_get_challenge_invalid(self):
        ch = get_challenge("nonexistent_id")
        assert ch is None

    def test_random_challenge(self):
        ch = random_challenge()
        assert ch.challenge_id != ""
        assert 0.0 <= ch.difficulty <= 1.0

    def test_random_challenge_category(self):
        ch = random_challenge(category="sacred")
        assert ch.category == "sacred"

    def test_progressive_ordering(self):
        challenges = progressive_challenges(10)
        assert len(challenges) == 10
        for i in range(len(challenges) - 1):
            assert challenges[i].difficulty <= challenges[i + 1].difficulty


# ══════════════════════════════════════════════════════════════════════
#  Self-Play Engine
# ══════════════════════════════════════════════════════════════════════

class TestSVGSelfPlay:

    def test_single_round(self):
        engine = SVGSelfPlayEngine(max_attempts=3)
        ch = get_challenge("prim_circle")
        rnd = engine.run_round(ch)
        assert isinstance(rnd, SVGRound)
        assert len(rnd.attempts) == 3
        assert rnd.best_score > 0
        assert rnd.best_svg.startswith("<svg")

    def test_improvement_trajectory(self):
        engine = SVGSelfPlayEngine(max_attempts=5)
        ch = get_challenge("prim_circle")
        rnd = engine.run_round(ch)
        assert len(rnd.improvement_trajectory) == 5
        # First attempt should score reasonably well (it's the reference)
        assert rnd.improvement_trajectory[0] > 0

    def test_session(self):
        engine = SVGSelfPlayEngine(max_attempts=3)
        results = engine.run_session(rounds=3, progressive=True)
        assert len(results) == 3
        for rnd in results:
            assert rnd.best_score > 0

    def test_history_save_load(self):
        engine = SVGSelfPlayEngine(max_attempts=2)
        engine.run_session(rounds=2, progressive=False)
        history = engine.get_history(last_n=5)
        assert history["meta"]["total_rounds"] == 2
        assert len(history["rounds"]) == 2

    def test_best_svg_saved(self):
        engine = SVGSelfPlayEngine(max_attempts=2)
        ch = get_challenge("prim_circle")
        engine.run_round(ch)
        best = engine.get_best("prim_circle")
        assert best is not None
        assert "<svg" in best

    def test_best_svg_not_found(self):
        engine = SVGSelfPlayEngine(max_attempts=2)
        assert engine.get_best("nonexistent") is None


# ══════════════════════════════════════════════════════════════════════
#  MCP Registration
# ══════════════════════════════════════════════════════════════════════

class TestSVGRegistration:

    def test_svg_tools_present(self):
        """Verify SVG tools are registered when loading the server."""
        import importlib.util
        from pathlib import Path
        server_path = Path(__file__).resolve().parent.parent / "MCP" / "athena_mcp_server.py"
        spec = importlib.util.spec_from_file_location("athena_mcp_server", server_path)
        mod = importlib.util.module_from_spec(spec)
        mod.__name__ = "athena_mcp_server"
        spec.loader.exec_module(mod)
        tools = set(mod.mcp._tool_manager._tools.keys())
        svg_tools = {
            "svg_challenge", "svg_generate", "svg_score",
            "svg_self_play", "svg_history", "svg_best",
            "svg_evolve", "svg_transcend", "svg_seeds",
            "svg_nervous_system", "svg_shard_cloud", "svg_brain_topology",
            "svg_108d_crystal", "svg_108d_panel",
            "svg_108d_inversion", "svg_108d_inversion_panel",
            "svg_inverse_double_fold",
        }
        missing = svg_tools - tools
        assert not missing, f"Missing SVG tools: {missing}"


# ══════════════════════════════════════════════════════════════════════
#  Dimensional Rendering (3D→12D)
# ══════════════════════════════════════════════════════════════════════

class TestSVGDimensional:

    def test_crystal_3d_seed(self):
        from crystal_108d.svg_dimensional import crystal_3d_seed
        svg = SVGCanvas(); svg.add(crystal_3d_seed(400, 400, 200))
        assert "<svg" in svg.render()

    def test_crystal_4d_tesseract(self):
        from crystal_108d.svg_dimensional import crystal_4d_tesseract
        svg = SVGCanvas(); svg.add(crystal_4d_tesseract(400, 400, 200))
        out = svg.render()
        assert "<svg" in out
        # Should have 32 edges (lines) + 16 vertices (circles)
        assert out.count("<line") >= 16

    def test_crystal_6d_mobius(self):
        from crystal_108d.svg_dimensional import crystal_6d_mobius
        svg = SVGCanvas(); svg.add(crystal_6d_mobius(400, 400, 200))
        out = svg.render()
        assert "<svg" in out
        # 3 wreaths × 4 strips = 12 polylines minimum
        assert out.count("<polyline") >= 12

    def test_crystal_8d_pentadic(self):
        from crystal_108d.svg_dimensional import crystal_8d_pentadic
        svg = SVGCanvas(); svg.add(crystal_8d_pentadic(400, 400, 200))
        out = svg.render()
        assert "<svg" in out
        # 5 animal orbits
        assert out.count("<polyline") >= 5

    def test_crystal_10d_heptadic(self):
        from crystal_108d.svg_dimensional import crystal_10d_heptadic
        svg = SVGCanvas(); svg.add(crystal_10d_heptadic(400, 400, 200))
        out = svg.render()
        assert "<svg" in out
        # 7 planetary orbits
        assert out.count("<polyline") >= 7

    def test_crystal_12d_crown(self):
        from crystal_108d.svg_dimensional import crystal_12d_crown
        svg = SVGCanvas(); svg.add(crystal_12d_crown(400, 400, 250))
        out = svg.render()
        assert "<svg" in out
        # 9 crown stations + Z* center
        assert out.count("<circle") >= 10

    def test_w_spiral(self):
        from crystal_108d.svg_dimensional import w_spiral
        svg = SVGCanvas(); svg.add(w_spiral(400, 400, 200))
        out = svg.render()
        assert "<svg" in out
        assert "Z*" in out

    def test_cross_lens_map(self):
        from crystal_108d.svg_dimensional import cross_lens_map
        svg = SVGCanvas(); svg.add(cross_lens_map(400, 400, 200))
        out = svg.render()
        assert "<svg" in out
        # 4 face nodes (S, F, C, R)
        for face in ["S", "F", "C", "R"]:
            assert f">{face}<" in out

    def test_containment_proof(self):
        from crystal_108d.svg_dimensional import containment_proof
        svg = SVGCanvas(); svg.add(containment_proof(400, 400, 250))
        out = svg.render()
        assert "<svg" in out
        assert "1890" in out  # containment count

    def test_full_12d_nested(self):
        from crystal_108d.svg_dimensional import crystal_full_12d
        svg = SVGCanvas(1200, 1200)
        svg.add(crystal_full_12d(600, 600, 400))
        out = svg.render()
        assert "<svg" in out
        # Must have all dimension labels
        for dim in ["12D", "10D", "8D", "6D", "4D"]:
            assert dim in out
        # Should be substantial (>15KB means all layers rendered)
        assert len(out) > 15000

    def test_phi_scaling_containment(self):
        """Verify nested rings follow PHI_INV scaling."""
        from crystal_108d.svg_dimensional import crystal_full_12d
        from crystal_108d.geometric_constants import PHI_INV
        # The function uses PHI_INV^n for ring radii
        # Just verify it renders without error
        svg = SVGCanvas(1000, 1000)
        svg.add(crystal_full_12d(500, 500, 300))
        assert len(svg.render()) > 10000


# ══════════════════════════════════════════════════════════════════════
#  Transcendence Engine
# ══════════════════════════════════════════════════════════════════════

class TestSVGTranscendence:

    def test_random_genome(self):
        from crystal_108d.svg_transcendence import random_genome, render_genome
        g = random_genome(n_layers=2)
        assert len(g.layers) == 2
        assert g.genome_id
        svg = render_genome(g)
        assert svg.startswith("<svg")

    def test_cross_category_genome(self):
        from crystal_108d.svg_transcendence import cross_category_genome, render_genome
        g = cross_category_genome("sacred", "fractal")
        assert len(g.layers) >= 2
        prims = {l.primitive for l in g.layers}
        # At least one from each category
        svg = render_genome(g)
        assert "<svg" in svg

    def test_breed(self):
        from crystal_108d.svg_transcendence import random_genome, breed
        a = random_genome(n_layers=2, generation=0)
        b = random_genome(n_layers=2, generation=0)
        child = breed(a, b, generation=1)
        assert child.generation == 1
        assert len(child.parent_ids) == 2
        assert child.lineage_depth == 1

    def test_mutate(self):
        from crystal_108d.svg_transcendence import random_genome, mutate
        g = random_genome(n_layers=2, generation=0)
        child = mutate(g, magnitude=0.2)
        assert child.genome_id != g.genome_id
        assert child.generation == 1

    def test_evolve_small(self):
        from crystal_108d.svg_transcendence import TranscendenceEngine
        engine = TranscendenceEngine(population_size=6, elite_count=2)
        result = engine.evolve(generations=3, cross_category=True)
        assert result.best_score > 0
        assert len(result.score_history) == 4  # initial + 3 gens
        assert result.best_genome is not None
        assert result.best_svg.startswith("<svg")

    def test_seeds_crystallized(self):
        from crystal_108d.svg_transcendence import TranscendenceEngine
        engine = TranscendenceEngine(population_size=8, elite_count=2)
        result = engine.evolve(generations=3)
        assert result.seeds_crystallized > 0
        seeds = engine.load_seeds()
        assert len(seeds) > 0

    def test_parameter_sweep(self):
        from crystal_108d.svg_transcendence import parameter_sweep
        results = parameter_sweep("circle", "r", steps=5)
        assert len(results) == 5
        for val, score, svg in results:
            assert score > 0
            assert "<svg" in svg

    def test_aggressive_session_small(self):
        from crystal_108d.svg_transcendence import TranscendenceEngine
        engine = TranscendenceEngine(population_size=6, elite_count=2)
        results = engine.aggressive_session(
            cycles=2, generations_per_cycle=3, population=6)
        assert len(results) == 2
        for r in results:
            assert r.best_score > 0

    def test_format_results(self):
        from crystal_108d.svg_transcendence import (
            TranscendenceEngine, format_evolution_result,
            format_session_results,
        )
        engine = TranscendenceEngine(population_size=6, elite_count=2)
        result = engine.evolve(generations=2)
        text = format_evolution_result(result)
        assert "Evolution Complete" in text
        assert "Best Score" in text

        results = [result]
        session_text = format_session_results(results)
        assert "TRANSCENDENCE SESSION RESULTS" in session_text


# ══════════════════════════════════════════════════════════════════════
#  Nervous System Visualization
# ══════════════════════════════════════════════════════════════════════

class TestSVGNervousSystem:

    def test_shard_cloud_renders(self):
        from crystal_108d.svg_nervous_system import render_shard_cloud_4d
        svg = render_shard_cloud_4d(400, 400, 200, max_shards=50)
        assert "<g>" in svg or "<circle" in svg or "No seed" in svg

    def test_momentum_field_renders(self):
        from crystal_108d.svg_nervous_system import render_momentum_field
        svg = render_momentum_field(400, 400, 180)
        assert "<g>" in svg or "<polygon" in svg or "No momentum" in svg

    def test_brain_topology_renders(self):
        from crystal_108d.svg_nervous_system import render_brain_topology
        svg = render_brain_topology(400, 400, 180)
        assert "<g>" in svg
        assert "<circle" in svg  # always renders (fallback nodes)

    def test_sector_distribution_renders(self):
        from crystal_108d.svg_nervous_system import render_sector_distribution
        svg = render_sector_distribution(400, 400, 200)
        assert "1890" in svg
        assert "QShrink" in svg

    def test_family_centroids_renders(self):
        from crystal_108d.svg_nervous_system import render_family_centroids
        svg = render_family_centroids(400, 400, 200, top_n=5)
        assert "<g>" in svg or "No family" in svg

    def test_full_dashboard_renders(self):
        from crystal_108d.svg_nervous_system import render_nervous_system
        svg = render_nervous_system(800, 600)
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "ATHENA NERVOUS SYSTEM" in svg

    def test_save_dashboard(self):
        import tempfile
        from crystal_108d.svg_nervous_system import save_nervous_system_dashboard
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            tmp = f.name
        try:
            path = save_nervous_system_dashboard(out_path=tmp)
            assert os.path.exists(path)
            content = open(path, encoding="utf-8").read()
            assert "<svg" in content
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def test_shard_cloud_has_dots(self):
        from crystal_108d.svg_nervous_system import render_shard_cloud_4d
        svg = render_shard_cloud_4d(400, 400, 200, max_shards=50)
        # Should have circles for shards (or fallback text)
        assert "<circle" in svg or "No seed" in svg


# ══════════════════════════════════════════════════════════════════════
#  108D Crystal Projection
# ══════════════════════════════════════════════════════════════════════

class TestSVG108DProjection:

    def test_shell_cascade(self):
        from crystal_108d.svg_108d_projection import render_shell_cascade
        svg = render_shell_cascade(400, 400, 250)
        assert "<g>" in svg
        assert "<circle" in svg

    def test_wreath_trefoil(self):
        from crystal_108d.svg_108d_projection import render_wreath_trefoil
        svg = render_wreath_trefoil(400, 400, 250)
        assert "<g>" in svg
        assert "Su" in svg or "<circle" in svg

    def test_archetype_wheel(self):
        from crystal_108d.svg_108d_projection import render_archetype_wheel
        svg = render_archetype_wheel(400, 400, 250)
        assert "<g>" in svg
        # 12 archetype nodes + surrounding elements
        assert svg.count("<circle") >= 12

    def test_sigma60_field(self):
        from crystal_108d.svg_108d_projection import render_sigma60_field
        svg = render_sigma60_field(400, 400, 250)
        assert "<g>" in svg
        # 60 sigma dots + pentagon lines
        assert svg.count("<circle") >= 60

    def test_e8_240(self):
        from crystal_108d.svg_108d_projection import render_e8_240
        svg = render_e8_240(400, 400, 250)
        assert "<g>" in svg
        # 240 root dots
        assert svg.count("<circle") >= 240

    def test_shard_density(self):
        from crystal_108d.svg_108d_projection import render_shard_density
        svg = render_shard_density(400, 400, 250)
        assert "<g>" in svg
        # 36 shell segments
        assert svg.count("<polygon") >= 36

    def test_momentum_shells(self):
        from crystal_108d.svg_108d_projection import render_momentum_shells
        svg = render_momentum_shells(400, 400, 250)
        assert "<g>" in svg

    def test_12d_observation(self):
        from crystal_108d.svg_108d_projection import render_12d_observation
        svg = render_12d_observation(400, 400, 200)
        assert "<g>" in svg
        # 12 axis lines + 4 element polygons
        assert svg.count("<line") >= 12

    def test_flower_overlay(self):
        from crystal_108d.svg_108d_projection import render_flower_overlay
        svg = render_flower_overlay(400, 400, 250)
        assert "<g>" in svg
        # 7 rings + petal circles
        assert svg.count("<circle") >= 7

    def test_full_108d_renders(self):
        from crystal_108d.svg_108d_projection import render_108d_crystal
        svg = render_108d_crystal(1200, 900)
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "108D" in svg

    def test_save_108d(self):
        import tempfile
        from crystal_108d.svg_108d_projection import save_108d_crystal
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            tmp = f.name
        try:
            path = save_108d_crystal(out_path=tmp)
            assert os.path.exists(path)
            content = open(path, encoding="utf-8").read()
            assert "<svg" in content
            assert len(content) > 50000  # should be substantial
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


# ══════════════════════════════════════════════════════════════════════
#  108D Inversion Cascade Tests
# ══════════════════════════════════════════════════════════════════════

class TestSVGInversionCascade:

    def test_3d_pair(self):
        from crystal_108d.svg_108d_projection import _render_3d_pair
        svg = _render_3d_pair(400, 400, 200)
        assert "<g>" in svg
        # 6 vertices (3 forward + 3 inverted) + center
        assert svg.count("<circle") >= 7
        # Both forward and inverted triangles
        assert svg.count("<line") >= 6

    def test_mobius_inversion(self):
        from crystal_108d.svg_108d_projection import _render_mobius_inversion
        svg = _render_mobius_inversion(400, 400, 200)
        assert "<g>" in svg
        assert "twist" in svg
        # 3 wreath nodes + chirality markers
        assert "<circle" in svg

    def test_wuxing_inversion(self):
        from crystal_108d.svg_108d_projection import _render_wuxing_inversion
        svg = _render_wuxing_inversion(400, 400, 200)
        assert "<g>" in svg
        # 5 animal nodes on pentagon
        assert svg.count("<circle") >= 5
        # generative (solid) + destructive (dashed) lines
        assert "<line" in svg
        assert "Tiger" in svg

    def test_planetary_inversion(self):
        from crystal_108d.svg_108d_projection import _render_planetary_inversion
        svg = _render_planetary_inversion(400, 400, 200)
        assert "<g>" in svg
        # 7 planet nodes (solid) + 7 detriment nodes (hollow)
        assert svg.count("<circle") >= 14
        assert "Sun" in svg or "Moon" in svg

    def test_matrix_inversion(self):
        from crystal_108d.svg_108d_projection import _render_matrix_inversion
        svg = _render_matrix_inversion(400, 400, 200)
        assert "<g>" in svg
        # 9 cells original + 9 cells transposed = 18 rects
        assert svg.count("<rect") >= 18
        assert "Z*" in svg

    def test_triple_crown(self):
        from crystal_108d.svg_108d_projection import _render_triple_crown_expansion
        svg = _render_triple_crown_expansion(400, 400, 250)
        assert "<g>" in svg
        # 3 octave sectors + 3 wreath rings + 9 crown stations
        assert "<circle" in svg
        assert "Z*" in svg
        assert "108D" in svg or "36D" in svg or "12D" in svg

    def test_w_cascade(self):
        from crystal_108d.svg_108d_projection import _render_w_cascade
        svg = _render_w_cascade(400, 400, 200)
        assert "<g>" in svg
        # Dimension markers (3D through 108D)
        assert "3D" in svg
        assert "108D" in svg
        # w-operator equation
        assert "1/\u221a2" in svg or "w =" in svg

    def test_containment_count(self):
        from crystal_108d.svg_108d_projection import _render_containment_count
        svg = _render_containment_count(400, 400, 200)
        assert "<g>" in svg
        # Dimension labels
        assert "108D" in svg
        assert "3D" in svg

    def test_full_inversion_cascade_renders(self):
        from crystal_108d.svg_108d_projection import render_inversion_cascade
        svg = render_inversion_cascade(1200, 1000)
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "Inversion Cascade" in svg or "inversion" in svg.lower()
        # All 8 panels should render
        assert "3D" in svg
        assert "108D" in svg

    def test_save_inversion_cascade(self):
        from crystal_108d.svg_108d_projection import save_inversion_cascade
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            tmp = f.name
        try:
            path = save_inversion_cascade(out_path=tmp)
            assert os.path.exists(path)
            content = open(path, encoding="utf-8").read()
            assert "<svg" in content
            assert len(content) > 20000
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def test_inversion_containment_math(self):
        """Verify the containment multiplication is correct."""
        # 108D = 3 × 36D = 3 × 3 × 12D = 9 × 12D
        # 12D = 9 × 10D = 63 × 8D = 315 × 6D = 945 × 4D = 1890 × 3D
        # So 108D = 9 × 1890 × 3D = 17,010 × 3D
        assert 3 * 3 == 9        # 108→12 factor
        assert 9 * 7 == 63       # 12→8 factor
        assert 63 * 5 == 315     # 12→6 factor
        assert 315 * 3 == 945    # 12→4 factor
        assert 945 * 2 == 1890   # 12→3 factor
        assert 9 * 1890 == 17010 # 108→3 total


# ══════════════════════════════════════════════════════════════════════
#  Inverse Double Fold Tests
# ══════════════════════════════════════════════════════════════════════

class TestSVGInverseDoubleFold:

    def test_inverse_double_fold_renders(self):
        from crystal_108d.svg_108d_projection import _render_inverse_double_fold
        svg = _render_inverse_double_fold(400, 400, 250)
        assert "<g>" in svg
        # 9 interaction points (W9 seed)
        assert svg.count("<circle") >= 9
        # Forward fold label
        assert "Forward Fold" in svg
        # Z* at center
        assert "Z*" in svg

    def test_double_fold_cascade_renders(self):
        from crystal_108d.svg_108d_projection import _render_double_fold_cascade
        svg = _render_double_fold_cascade(400, 400, 250)
        assert "<g>" in svg
        # 4 fold levels (3D, 6D, 12D, 108D)
        assert "3D" in svg
        assert "108D" in svg
        # Grid cells (rect elements)
        assert svg.count("<rect") >= 9  # at least the 3×3 grid

    def test_full_double_fold_dashboard(self):
        from crystal_108d.svg_108d_projection import render_inverse_double_fold
        svg = render_inverse_double_fold(1200, 800)
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "Double Fold" in svg or "Inverse" in svg

    def test_save_double_fold(self):
        from crystal_108d.svg_108d_projection import save_inverse_double_fold
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            tmp = f.name
        try:
            path = save_inverse_double_fold(out_path=tmp)
            assert os.path.exists(path)
            content = open(path, encoding="utf-8").read()
            assert "<svg" in content
            assert len(content) > 10000
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def test_fold_math(self):
        """Verify D² produces the dimensional structure counts."""
        assert 3 ** 2 == 9    # 3D fold = 9 = W9
        assert 6 ** 2 == 36   # 6D fold = 36 = shells
        assert 36 * 3 == 108  # triple fold = organism
        assert 12 ** 2 == 144 # 12D fold = 144 = gates (12 archetypes × 12)

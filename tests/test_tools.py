"""Smoke tests for all crystal_108d tools — each called with known-good inputs."""

from crystal_108d.shells import query_shell, query_superphase, query_archetype, read_hologram_chapter
from crystal_108d.dimensions import resolve_dimensional_body, dimensional_lift, query_containment
from crystal_108d.organs import query_organ
from crystal_108d.address import navigate_108d
from crystal_108d.live_lock import compute_live_lock
from crystal_108d.clock import query_clock_beat
from crystal_108d.moves import check_route_legality
from crystal_108d.metro_lines import query_metro_line
from crystal_108d.z_points import resolve_z_point
from crystal_108d.conservation import query_conservation
from crystal_108d.overlays import query_overlay, query_sigma15
from crystal_108d.transport import query_transport_stack
from crystal_108d.mobius_lenses import query_mobius_lens, query_sfcr_station
from crystal_108d.stage_codes import query_stage_code
from crystal_108d.angel import query_angel
from crystal_108d.brain import query_brain_network, compute_bridge_weight, route_brain
from crystal_108d.live_cell import query_live_cell
from crystal_108d.emergence import query_emergence


class TestShellTools:
    def test_query_shell(self):
        result = query_shell(1)
        assert "Shell 1" in result
        assert len(result) > 50

    def test_query_shell_last(self):
        result = query_shell(36)
        assert "Shell 36" in result

    def test_query_shell_invalid(self):
        result = query_shell(0)
        assert "Invalid" in result or "invalid" in result.lower()

    def test_query_superphase_sulfur(self):
        result = query_superphase("sulfur")
        assert "Sulfur" in result

    def test_query_superphase_code(self):
        result = query_superphase("Me")
        assert "Mercury" in result

    def test_query_archetype(self):
        result = query_archetype(1)
        assert "Apex Seed" in result

    def test_query_archetype_all_wreaths(self):
        result = query_archetype(7)
        assert "3" in result  # appears in 3 shells

    def test_read_hologram_chapter(self):
        result = read_hologram_chapter(1)
        assert "Chapter 1" in result

    def test_read_hologram_chapter_last(self):
        result = read_hologram_chapter(21)
        assert "Chapter 21" in result


class TestDimensionTools:
    def test_resolve_3d(self):
        result = resolve_dimensional_body(3)
        assert "3D" in result

    def test_resolve_12d(self):
        result = resolve_dimensional_body(12)
        assert "12D" in result

    def test_dimensional_lift(self):
        result = dimensional_lift(4, 12)
        assert "4D" in result
        assert "12D" in result

    def test_query_containment(self):
        result = query_containment(12)
        assert "Weave" in result or "B_12" in result


class TestOrganTool:
    def test_query_by_name(self):
        result = query_organ("Identity")
        assert "Identity" in result

    def test_query_by_dyad_index(self):
        result = query_organ("1")
        assert "Dyad" in result

    def test_query_crown_closure(self):
        result = query_organ("7")
        assert "Crown" in result or "Petal" in result


class TestNavigationTools:
    def test_navigate_by_shell(self):
        result = navigate_108d(shell=5)
        assert "Shell 5" in result

    def test_navigate_by_address(self):
        result = navigate_108d(address="Xi108:S5")
        assert "Shell 5" in result

    def test_navigate_by_wreath(self):
        result = navigate_108d(wreath="Su")
        assert "Sulfur" in result or "Su" in result


class TestLiveLockTool:
    def test_compute(self):
        result = compute_live_lock("3", "5")
        assert "Lock" in result or "lock" in result.lower()


class TestClockTool:
    def test_beat_0(self):
        result = query_clock_beat(0)
        assert "Beat 0" in result

    def test_beat_210(self):
        result = query_clock_beat(210)
        assert "Beat 210" in result


class TestMovesTool:
    def test_list_primitives(self):
        result = check_route_legality("list")
        assert "STEP_SHELL" in result

    def test_check_route(self):
        route = '[{"type": "STEP_SHELL", "from": 1, "to": 2, "delta": 1}]'
        result = check_route_legality(route)
        assert "Legality" in result or "Move" in result


class TestMetroTool:
    def test_overview(self):
        result = query_metro_line("all")
        assert "Metro" in result or "Shell" in result

    def test_wreath_line(self):
        result = query_metro_line("wreath", 0)
        assert "Sulfur" in result or "Su" in result

    def test_archetype_column(self):
        result = query_metro_line("archetype_column", 1)
        assert "Archetype" in result or "Apex" in result


class TestZPointTool:
    def test_hierarchy(self):
        result = resolve_z_point("all")
        assert "Z" in result

    def test_global(self):
        result = resolve_z_point("global")
        assert "Z*" in result or "Global" in result or "global" in result.lower()


class TestConservationTool:
    def test_list_laws(self):
        result = query_conservation("list")
        assert "Conservation" in result or "Shell" in result

    def test_check_motion(self):
        motion = '{"shell_deltas": [1, -1], "zoom_deltas": [0], "wreath_rotations": [0], "face_shifts": [0], "mobius_flips": 0}'
        result = query_conservation(motion)
        assert "PASS" in result


class TestOverlayTools:
    def test_overview(self):
        result = query_overlay("all")
        assert "Overlay" in result or "Registry" in result

    def test_lens_registry(self):
        result = query_overlay("lens")
        assert "Square" in result

    def test_sigma15(self):
        result = query_sigma15(15)
        assert "SFCR" in result


class TestTransportTool:
    def test_full_stack(self):
        result = query_transport_stack(0)
        assert "Transport" in result

    def test_dimension_3(self):
        result = query_transport_stack(3)
        assert "3D" in result


class TestMobiusLensTools:
    def test_overview(self):
        result = query_mobius_lens("all")
        assert "Möbius" in result or "Lens" in result

    def test_kernel(self):
        result = query_mobius_lens("kernel")
        assert "Kernel" in result or "4×4" in result

    def test_square(self):
        result = query_mobius_lens("square")
        assert "Square" in result

    def test_flower(self):
        result = query_mobius_lens("flower")
        assert "Flower" in result

    def test_cloud(self):
        result = query_mobius_lens("cloud")
        assert "Cloud" in result

    def test_fractal(self):
        result = query_mobius_lens("fractal")
        assert "Fractal" in result

    def test_laws(self):
        result = query_mobius_lens("laws")
        assert "Law" in result or "Kernel" in result

    def test_lattice(self):
        result = query_mobius_lens("lattice")
        assert "SFCR" in result or "15" in result

    def test_cockpit(self):
        result = query_mobius_lens("cockpit")
        assert "96" in result or "Cockpit" in result

    def test_sfcr_station(self):
        result = query_sfcr_station("SF")
        assert "SF" in result

    def test_sfcr_by_mask(self):
        result = query_sfcr_station("15")
        assert "SFCR" in result


class TestStageCodeTool:
    def test_all(self):
        result = query_stage_code("all")
        assert "Stage" in result or "S3" in result

    def test_specific(self):
        result = query_stage_code("S4")
        assert "4D" in result

    def test_s12(self):
        result = query_stage_code("S12")
        assert "12D" in result or "Crown" in result

    def test_zeros(self):
        result = query_stage_code("zeros")
        assert "Z" in result

    def test_sigma60(self):
        result = query_stage_code("sigma60")
        assert "60" in result


class TestAngelTool:
    def test_overview(self):
        result = query_angel("all")
        assert "Angel" in result

    def test_pieces(self):
        result = query_angel("pieces")
        assert "12" in result or "Σ" in result or "Token" in result

    def test_observability(self):
        result = query_angel("observability")
        assert "Square" in result or "probe" in result.lower()

    def test_selves(self):
        result = query_angel("selves")
        assert "Hidden" in result or "Canonical" in result

    def test_modes(self):
        result = query_angel("modes")
        assert "committed" in result.lower() or "flowing" in result.lower()


class TestBrainTools:
    def test_overview(self):
        result = query_brain_network("all")
        assert "Brain" in result

    def test_elements(self):
        result = query_brain_network("elements")
        assert "Square" in result and "Flower" in result

    def test_bridges(self):
        result = query_brain_network("bridges")
        assert "SF" in result or "Bridge" in result

    def test_closures(self):
        result = query_brain_network("closures")
        assert "SFC" in result or "Triangle" in result

    def test_aether(self):
        result = query_brain_network("aether")
        assert "SFCR" in result

    def test_routing(self):
        result = query_brain_network("routing")
        assert "Z-Point" in result or "Layer" in result

    def test_weights(self):
        result = query_brain_network("weights")
        assert "Golden" in result or "0.618" in result

    def test_forks(self):
        result = query_brain_network("forks")
        assert "athena-square-earth" in result

    def test_element_square(self):
        result = query_brain_network("element:S")
        assert "Earth" in result

    def test_element_flower(self):
        result = query_brain_network("element:F")
        assert "Fire" in result

    def test_element_cloud(self):
        result = query_brain_network("element:C")
        assert "Water" in result

    def test_element_fractal(self):
        result = query_brain_network("element:R")
        assert "Air" in result

    def test_bridge_sf(self):
        result = query_brain_network("bridge:SF")
        assert "Square" in result or "Flower" in result

    def test_bridge_cr(self):
        result = query_brain_network("bridge:CR")
        assert "Cloud" in result or "Fractal" in result

    def test_bridge_weight_sf(self):
        result = compute_bridge_weight("S", "F", "L3", "L5")
        assert "Bridge Weight" in result

    def test_bridge_weight_cr(self):
        result = compute_bridge_weight("C", "R")
        assert "Bridge Weight" in result

    def test_bridge_weight_self(self):
        result = compute_bridge_weight("S", "S")
        assert "Self-Loop" in result

    def test_route_sf(self):
        result = route_brain("S", "F")
        assert "Brain Route" in result

    def test_route_sr(self):
        result = route_brain("S", "R")
        assert "Brain Route" in result

    def test_route_self(self):
        result = route_brain("C", "C")
        assert "self-loop" in result

    def test_all_routes(self):
        for s in "SFCR":
            for t in "SFCR":
                result = route_brain(s, t)
                assert len(result) > 50


class TestLiveCellTool:
    def test_all(self):
        result = query_live_cell("all")
        assert "Live Cell" in result or "NEXT" in result

    def test_schemas(self):
        result = query_live_cell("schemas")
        assert "BoardStateRow" in result

    def test_specific_schema(self):
        result = query_live_cell("schema:BoardStateRow")
        assert "thread_id" in result or "clock_beat" in result

    def test_trace_cert(self):
        result = query_live_cell("schema:TraceCert")
        assert "cert" in result.lower() or "hash" in result.lower()

    def test_metro(self):
        result = query_live_cell("metro")
        assert "M00" in result

    def test_station(self):
        result = query_live_cell("station:M60")
        assert "A+" in result or "Threshold" in result

    def test_liminal(self):
        result = query_live_cell("liminal")
        assert "0.618" in result or "phi" in result.lower()

    def test_soul(self):
        result = query_live_cell("soul")
        assert "Soul" in result or "stamp" in result.lower()

    def test_route(self):
        result = query_live_cell("route")
        assert "ROOT" in result or "LOOP" in result

    def test_unknown(self):
        result = query_live_cell("nonsense")
        assert "Unknown" in result


class TestEmergenceTool:
    def test_all(self):
        result = query_emergence("all")
        assert "Emergence" in result

    def test_phases(self):
        result = query_emergence("phases")
        assert "4D" in result and "6D" in result

    def test_specific_phase(self):
        result = query_emergence("phase:3")
        assert "6D" in result or "Holographic" in result

    def test_phase_by_name(self):
        result = query_emergence("phase:4D->6D")
        assert "6x6" in result or "DLS" in result or "weave" in result

    def test_kernel(self):
        result = query_emergence("kernel")
        assert "Theta" in result or "embedding" in result.lower()

    def test_lenses(self):
        result = query_emergence("lenses")
        assert "Square" in result and "Flower" in result

    def test_lens_at(self):
        result = query_emergence("lens:6D")
        assert "6x6" in result

    def test_bodies(self):
        result = query_emergence("bodies")
        assert "4D" in result or "TESSERACT" in result

    def test_unknown(self):
        result = query_emergence("nonsense")
        assert "Unknown" in result


# ── New tools (Hologram / Angel Geometry / Inverse Crystal) ──────────

from crystal_108d.hologram_reading import query_hologram, query_hologram_rosetta
from crystal_108d.angel_geometry import query_angel_geometry, query_angel_conservation
from crystal_108d.inverse_seed import query_4d_seed, query_3d_crystal
from crystal_108d.inverse_octave import query_octave_stage, query_crown_transform
from crystal_108d.inverse_complete import query_projection_stack, query_weave_operator


class TestHologramTools:
    def test_hologram_all(self):
        result = query_hologram("all")
        assert "Hologram" in result
        assert "Seed" in result

    def test_hologram_faces(self):
        result = query_hologram("faces")
        assert "Perception" in result
        assert "270" in result

    def test_hologram_seed(self):
        result = query_hologram("seed")
        assert "(1+i)/2" in result

    def test_hologram_grammar(self):
        result = query_hologram("grammar")
        assert "W" in result

    def test_hologram_storage(self):
        result = query_hologram("storage")
        assert "Storage" in result or "formula" in result.lower()

    def test_hologram_compression(self):
        result = query_hologram("compression")
        assert "Compression" in result

    def test_hologram_layers(self):
        result = query_hologram("layers")
        assert "Layer" in result

    def test_hologram_body(self):
        result = query_hologram("body")
        assert "Body" in result or "12" in result

    def test_hologram_unknown(self):
        result = query_hologram("nonsense")
        assert "Unknown" in result or "unknown" in result.lower()

    def test_rosetta_all(self):
        result = query_hologram_rosetta("all")
        assert "Rosetta" in result
        assert "Egypt" in result

    def test_rosetta_quaternary(self):
        result = query_hologram_rosetta("quaternary")
        assert "Maya" in result
        assert "Sanskrit" in result

    def test_rosetta_triadic(self):
        result = query_hologram_rosetta("triadic")
        assert "kar" in result

    def test_rosetta_wheel(self):
        result = query_hologram_rosetta("wheel")
        assert "360" in result

    def test_rosetta_surface(self):
        result = query_hologram_rosetta("surface")
        assert "Latin" in result or "holographic" in result.lower()

    def test_rosetta_sigma60(self):
        result = query_hologram_rosetta("sigma60")
        assert "60" in result

    def test_rosetta_voynich(self):
        result = query_hologram_rosetta("voynich")
        assert "Voynich" in result


class TestAngelGeometryTools:
    def test_geometry_all(self):
        result = query_angel_geometry("all")
        assert "Geometric" in result or "geometric" in result

    def test_geometry_manifold(self):
        result = query_angel_geometry("manifold")
        assert "Manifold" in result or "M_Sq" in result

    def test_geometry_metric(self):
        result = query_angel_geometry("metric")
        assert "metric" in result.lower() or "Metric" in result

    def test_geometry_bundle(self):
        result = query_angel_geometry("bundle")
        assert "bundle" in result.lower() or "Bundle" in result

    def test_geometry_curvature(self):
        result = query_angel_geometry("curvature")
        assert "curvature" in result.lower() or "holonomy" in result.lower()

    def test_geometry_symmetry(self):
        result = query_angel_geometry("symmetry")
        assert "symmetry" in result.lower() or "group" in result.lower()

    def test_geometry_sheaf(self):
        result = query_angel_geometry("sheaf")
        assert "sheaf" in result.lower() or "coherent" in result.lower()

    def test_geometry_axioms(self):
        result = query_angel_geometry("axioms")
        assert "A1" in result
        assert "A7" in result

    def test_geometry_self_def(self):
        result = query_angel_geometry("self_definition")
        assert "fixed" in result.lower() or "recursive" in result.lower()

    def test_conservation_all(self):
        result = query_angel_conservation("all")
        assert "invariant" in result.lower() or "Conservation" in result

    def test_conservation_exact(self):
        result = query_angel_conservation("exact")
        assert "Normalization" in result or "normalization" in result.lower()

    def test_conservation_quasi(self):
        result = query_angel_conservation("quasi")
        assert "quasi" in result.lower() or "Quasi" in result

    def test_conservation_holonomy(self):
        result = query_angel_conservation("holonomy")
        assert "holonomy" in result.lower() or "residue" in result.lower()

    def test_conservation_potential(self):
        result = query_angel_conservation("potential")
        assert "potential" in result.lower() or "Phi" in result


class TestInverseSeedTools:
    def test_4d_seed_all(self):
        result = query_4d_seed("all")
        assert "256" in result or "4D" in result

    def test_4d_seed_faces(self):
        result = query_4d_seed("faces")
        assert "Square" in result or "Flower" in result

    def test_4d_seed_registers(self):
        result = query_4d_seed("registers")
        assert "Body" in result or "Route" in result

    def test_4d_seed_invariants(self):
        result = query_4d_seed("invariants")
        assert "(1+i)/2" in result or "w=" in result

    def test_3d_crystal_all(self):
        result = query_3d_crystal("all")
        assert "3D" in result or "seed" in result.lower()

    def test_3d_crystal_boundary(self):
        result = query_3d_crystal("boundary")
        assert "boundary" in result.lower() or "2D" in result

    def test_3d_crystal_encoding(self):
        result = query_3d_crystal("encoding")
        assert "holographic" in result.lower() or "encoding" in result.lower()


class TestInverseOctaveTools:
    def test_octave_all(self):
        result = query_octave_stage("all")
        assert "S00" in result

    def test_octave_s03(self):
        result = query_octave_stage("S03")
        assert "6D" in result or "Mobius" in result or "triadic" in result.lower()

    def test_octave_s12(self):
        result = query_octave_stage("S12")
        assert "108" in result or "36D" in result

    def test_crown_all(self):
        result = query_crown_transform("all")
        assert "Crown" in result or "crown" in result

    def test_crown_step1(self):
        result = query_crown_transform("1")
        assert "Zero" in result or "tunnel" in result.lower() or "Z" in result


class TestInverseCompleteTools:
    def test_projection_all(self):
        result = query_projection_stack("all")
        assert "Projection" in result or "projection" in result

    def test_projection_up(self):
        result = query_projection_stack("up")
        assert "3D" in result or "108" in result

    def test_projection_down(self):
        result = query_projection_stack("down")
        assert "3D" in result or "SHRINK" in result.lower() or "shrink" in result.lower()

    def test_weave_all(self):
        result = query_weave_operator("all")
        assert "Weave" in result or "Triadic" in result

    def test_weave_w3(self):
        result = query_weave_operator("W3")
        assert "Su" in result or "Me" in result or "Sa" in result

    def test_weave_w5(self):
        result = query_weave_operator("W5")
        assert "5" in result

    def test_weave_w7(self):
        result = query_weave_operator("W7")
        assert "7" in result

    def test_weave_controls(self):
        result = query_weave_operator("controls")
        assert "C7" in result or "C9" in result or "control" in result.lower()

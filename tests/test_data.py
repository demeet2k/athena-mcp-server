"""Validate all JSON data files for structural integrity."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "MCP" / "data"


def _load(filename: str) -> dict:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


class TestJsonFilesLoad:
    """Every JSON data file must parse without errors."""

    def test_shell_registry(self):
        data = _load("shell_registry.json")
        assert "meta" in data
        assert "shells" in data

    def test_hologram_chapters(self):
        data = _load("hologram_chapters.json")
        assert "chapters" in data

    def test_dimensional_ladder(self):
        data = _load("dimensional_ladder.json")
        assert "dimensions" in data

    def test_organ_atlas(self):
        data = _load("organ_atlas.json")
        assert "dyads" in data

    def test_live_lock_registry(self):
        data = _load("live_lock_registry.json")
        assert "classes" in data

    def test_clock_projections(self):
        data = _load("clock_projections.json")
        assert "projections" in data

    def test_move_primitives(self):
        data = _load("move_primitives.json")
        assert "primitives" in data

    def test_metro_lines(self):
        data = _load("metro_lines.json")
        assert "shell_ascent" in data

    def test_z_point_hierarchy(self):
        data = _load("z_point_hierarchy.json")
        assert "types" in data

    def test_conservation_laws(self):
        data = _load("conservation_laws.json")
        assert "laws" in data

    def test_overlay_registries(self):
        data = _load("overlay_registries.json")
        assert "4_lens" in data

    def test_transport_stacks(self):
        data = _load("transport_stacks.json")
        assert "layers" in data

    def test_mobius_lenses(self):
        data = _load("mobius_lenses.json")
        assert "kernel_4x4" in data
        assert "lenses" in data

    def test_stage_codes(self):
        data = _load("stage_codes.json")
        assert "stages" in data

    def test_angel_object(self):
        data = _load("angel_object.json")
        assert "structural_pieces" in data

    def test_brain_network(self):
        data = _load("brain_network.json")
        assert "elements" in data
        assert "bridges" in data
        assert "closures" in data
        assert "aether" in data

    def test_live_cell_constitution(self):
        data = _load("live_cell_constitution.json")
        assert "meta" in data
        assert "cell_schema" in data
        assert "metro_map" in data
        assert "liminal_coordinates" in data
        assert "soul_stamp_schema" in data

    def test_dimensional_emergence(self):
        data = _load("dimensional_emergence.json")
        assert "meta" in data
        assert "emergence_phases" in data
        assert "kernel_embedding" in data
        assert "cross_lens_upgrade_sequence" in data

    def test_hologram_reading(self):
        data = _load("hologram_reading.json")
        assert "meta" in data
        assert "four_face_protocol" in data
        assert "seed_equation" in data
        assert "process_grammar" in data
        assert "storage_law" in data

    def test_hologram_rosetta(self):
        data = _load("hologram_rosetta.json")
        assert "meta" in data
        assert "quaternary_basis" in data
        assert "triadic_motor" in data
        assert "carrier_wheel_360" in data

    def test_angel_geometry(self):
        data = _load("angel_geometry.json")
        assert "meta" in data
        assert "geometric_object" in data
        assert "state_manifold" in data
        assert "seven_axioms" in data

    def test_angel_conservation(self):
        data = _load("angel_conservation.json")
        assert "meta" in data
        assert "exact_invariants" in data
        assert "quasi_invariants" in data
        assert "potential_landscape" in data

    def test_inverse_crystal_seed(self):
        data = _load("inverse_crystal_seed.json")
        assert "meta" in data
        assert "phase_I_4D_seed" in data
        assert "three_d_seed" in data
        assert "two_d_boundary" in data

    def test_inverse_crystal_octave(self):
        data = _load("inverse_crystal_octave.json")
        assert "meta" in data
        assert "octave_stages" in data
        assert "crown_transform" in data

    def test_inverse_crystal_complete(self):
        data = _load("inverse_crystal_complete.json")
        assert "meta" in data
        assert "projection_stack" in data
        assert "weave_operators" in data
        assert "control_shells" in data


class TestDataIntegrity:
    """Cross-check meta counts against actual data."""

    def test_shell_count(self):
        data = _load("shell_registry.json")
        assert data["meta"]["total_shells"] == 36
        assert len(data["shells"]) == 36

    def test_node_count(self):
        data = _load("shell_registry.json")
        assert data["meta"]["total_nodes"] == 666
        assert sum(s["nodes"] for s in data["shells"]) == 666

    def test_hologram_chapter_count(self):
        data = _load("hologram_chapters.json")
        assert len(data["chapters"]) == 21

    def test_organ_dyad_count(self):
        data = _load("organ_atlas.json")
        assert data["meta"]["dyads"] == 6
        assert len(data["dyads"]) == 6

    def test_conservation_law_count(self):
        data = _load("conservation_laws.json")
        assert data["meta"]["total_laws"] == 6
        assert len(data["laws"]) == 6

    def test_live_lock_class_count(self):
        data = _load("live_lock_registry.json")
        assert data["meta"]["total_classes"] == 7
        assert len(data["classes"]) == 7

    def test_move_primitive_count(self):
        data = _load("move_primitives.json")
        assert len(data["primitives"]) == 10

    def test_transport_layer_count(self):
        data = _load("transport_stacks.json")
        assert len(data["layers"]) == 9

    def test_overlay_registry_count(self):
        data = _load("overlay_registries.json")
        assert data["meta"]["total_registries"] == 4
        assert len(data["4_lens"]["entries"]) == 4
        assert len(data["7_alchemy"]["entries"]) == 7
        assert len(data["5_animal"]["entries"]) == 5
        assert len(data["9_completion"]["entries"]) == 9

    def test_sfcr_station_count(self):
        data = _load("mobius_lenses.json")
        assert data["sfcr_lattice"]["total_stations"] == 15
        assert len(data["sfcr_lattice"]["stations"]) == 15

    def test_cross_lens_law_count(self):
        data = _load("mobius_lenses.json")
        assert len(data["cross_lens_laws"]) == 6

    def test_stage_count(self):
        data = _load("stage_codes.json")
        assert len(data["stages"]) == 16

    def test_angel_piece_count(self):
        data = _load("angel_object.json")
        assert len(data["structural_pieces"]) == 12

    def test_dimensional_ladder_dimensions(self):
        data = _load("dimensional_ladder.json")
        dims = [d["dimension"] for d in data["dimensions"]]
        assert 3 in dims
        assert 12 in dims
        assert len(dims) == 10  # 3D through 12D

    def test_brain_element_count(self):
        data = _load("brain_network.json")
        assert data["meta"]["elements"] == 4
        assert len(data["elements"]) == 4

    def test_brain_bridge_count(self):
        data = _load("brain_network.json")
        assert data["meta"]["bridges"] == 6
        assert len(data["bridges"]) == 6

    def test_brain_closure_count(self):
        data = _load("brain_network.json")
        assert data["meta"]["closures"] == 4
        assert len(data["closures"]) == 4

    def test_live_cell_schema_count(self):
        data = _load("live_cell_constitution.json")
        assert data["meta"]["total_schemas"] == 6
        assert len(data["cell_schema"]) == 6

    def test_live_cell_metro_count(self):
        data = _load("live_cell_constitution.json")
        assert data["meta"]["metro_stations"] == 14
        assert len(data["metro_map"]["stations"]) == 14

    def test_emergence_phase_count(self):
        data = _load("dimensional_emergence.json")
        assert data["meta"]["total_phases"] == 7
        assert len(data["emergence_phases"]) == 7

    def test_emergence_lens_stages(self):
        data = _load("dimensional_emergence.json")
        stages = [r["stage"] for r in data["cross_lens_upgrade_sequence"]]
        assert "3D" in stages
        assert "12D" in stages
        assert len(stages) == 7

    def test_brain_total_stations(self):
        data = _load("brain_network.json")
        assert data["meta"]["total_stations"] == 15
        # 4 elements + 6 bridges + 4 closures + 1 aether = 15
        total = len(data["elements"]) + len(data["bridges"]) + len(data["closures"]) + len(data["aether"])
        assert total == 15

    def test_hologram_face_count(self):
        data = _load("hologram_reading.json")
        assert len(data["four_face_protocol"]["faces"]) == 4

    def test_rosetta_civilization_count(self):
        data = _load("hologram_rosetta.json")
        assert len(data["quaternary_basis"]["civilizations"]) == 4

    def test_angel_geometry_axiom_count(self):
        data = _load("angel_geometry.json")
        assert len(data["seven_axioms"]) == 7

    def test_angel_geometry_chart_count(self):
        data = _load("angel_geometry.json")
        assert len(data["state_manifold"]["charts"]) == 6

    def test_angel_conservation_exact_count(self):
        data = _load("angel_conservation.json")
        assert len(data["exact_invariants"]) == 4

    def test_octave_stage_count(self):
        data = _load("inverse_crystal_octave.json")
        assert len(data["octave_stages"]) == 14

    def test_crown_transform_step_count(self):
        data = _load("inverse_crystal_octave.json")
        assert len(data["crown_transform"]["steps"]) == 6

    def test_seed_invariant_count(self):
        data = _load("inverse_crystal_seed.json")
        assert len(data["phase_I_4D_seed"]["invariants"]) == 10

    def test_projection_stack_up(self):
        data = _load("inverse_crystal_complete.json")
        assert len(data["projection_stack"]["up"]) >= 10

    def test_weave_operator_count(self):
        data = _load("inverse_crystal_complete.json")
        # W3, W5, W7, master_clock
        assert "W3" in data["weave_operators"]
        assert "W5" in data["weave_operators"]
        assert "W7" in data["weave_operators"]

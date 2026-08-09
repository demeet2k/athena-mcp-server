import tempfile
import unittest

from athena_mcp.bootstrap import bootstrap
from athena_mcp.cell_closure import CellClosureCompiler, frozen_constitution_manifest
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.inner_constitution import block_counts, seat, seats
from athena_mcp.store import Store


class CellClosureCompilerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.store = Store(self.tmp.name)
        self.core = AthenaCore(self.store)
        bootstrap(self.core)
        self.crystal = CrystalRuntime(self.core)
        self.h6 = H6RootRuntime(self.core, self.crystal)
        self.compiler = CellClosureCompiler(self.core, self.crystal, self.h6)

    def tearDown(self):
        self.store.close()
        self.tmp.close()

    @staticmethod
    def semantic(name):
        return {
            "kind": "ARTIFACT", "domain": "CELL_CLOSURE", "verb": "POPULATE",
            "object_name": name, "method": "FIXTURE",
            "input_contract": {}, "output_contract": {},
        }

    def test_constitution_is_exactly_144_and_expected_blocks(self):
        values = seats()
        self.assertEqual(len(values), 144)
        self.assertEqual([x["gid"] for x in values], list(range(1, 145)))
        self.assertEqual(
            block_counts(),
            {"H6": 6, "X16": 16, "BR21": 21, "F37": 37, "IC10": 10, "KC15": 15, "KC27": 27, "SSN12": 12},
        )
        manifest = frozen_constitution_manifest()
        self.assertEqual(manifest["seat_count"], 144)
        self.assertTrue(manifest["constitution_id"].startswith("INNERCONST."))

    def test_known_f37_holds_are_explicit_not_erased(self):
        expected = {
            73: "GRADED_MEMORY_PARTIAL_EXACTIFICATION",
            77: "MOTIVIC_COMPARISON_DEBT",
            78: "HIGHER_COHERENCE_COMPOSITION_WITNESS",
            79: "DERIVED_SINGULARITY_AND_EMPIRICAL_CLOSURE",
        }
        for gid, obligation in expected.items():
            self.assertIn(obligation, seat(gid)["known_obligations"])
            packet = self.compiler.packet(gid)
            self.assertEqual(packet["closure"]["evidence_status"], "HOLD")
            self.assertEqual(packet["closure"]["overall_state"], "HOLD")

    def test_empty_census_is_typed_not_fake_complete(self):
        matrix = self.compiler.matrix()
        self.assertEqual(matrix["seat_count"], 144)
        self.assertEqual(matrix["dimension_counts"]["constitution_status"], {"CLOSED": 144})
        self.assertEqual(matrix["dimension_counts"]["registry_status"], {"CLOSED": 144})
        self.assertEqual(matrix["dimension_counts"]["population_status"], {"UNKNOWN": 144})
        self.assertEqual(matrix["dimension_counts"]["execution_status"], {"UNKNOWN": 144})
        self.assertEqual(matrix["dimension_counts"]["return_status"], {"UNKNOWN": 144})
        self.assertNotIn("CLOSED", matrix["overall_counts"])
        self.assertEqual(len(matrix["packets"]), 144)
        for packet in matrix["packets"]:
            self.assertNotEqual(packet["closure"]["next_required_witness"], "NONE")

    def test_hash_projection_never_counts_as_population(self):
        made = self.crystal.crystallize_output(
            self.semantic("HASH_ONLY"), "hash-only projection", "memory://cell/hash-only",
            "CELL.CLOSURE", "hash-only", 1)
        gid = made["manifest"]["coordinates"]["KC144"]["value"]["gid"]
        packet = self.compiler.packet(gid)
        self.assertTrue(packet["population"]["projection_observations"])
        self.assertFalse(packet["population"]["projection_observations_are_population"])
        self.assertEqual(packet["closure"]["population_status"], "UNKNOWN")
        self.assertEqual(packet["closure"]["next_required_witness"], "BIND_SOURCE_BACKED_CONSTITUTIONAL_POPULATION")

    def test_explicit_evidence_backed_constitutional_binding_closes_population_only(self):
        made = self.crystal.crystallize_output(
            self.semantic("BOUND"), "bound object", "memory://cell/bound",
            "CELL.CLOSURE", "bound", 1)
        oid = made["manifest"]["identity"]["OID"]
        packet = self.compiler.packet(
            1,
            seat_bindings={1: [{"oid": oid, "authority": "CONSTITUTIONAL_SEAT", "evidence_refs": ["CONST.WITNESS.1"]}]},
        )
        self.assertEqual(packet["closure"]["population_status"], "CLOSED")
        self.assertEqual(packet["closure"]["execution_status"], "UNKNOWN")
        self.assertEqual(packet["closure"]["evidence_status"], "UNKNOWN")
        self.assertEqual(packet["closure"]["return_status"], "UNKNOWN")
        self.assertEqual(packet["closure"]["overall_state"], "OPEN_TYPED")
        self.assertEqual(packet["closure"]["next_required_witness"], "BIND_EXECUTABLE_RUNTIME_OR_DORMANT_STATUS")

    def test_invalid_binding_authority_fails_closed(self):
        made = self.crystal.crystallize_output(
            self.semantic("BAD_BIND"), "bad binding", "memory://cell/bad-bind",
            "CELL.CLOSURE", "bad-bind", 1)
        oid = made["manifest"]["identity"]["OID"]
        packet = self.compiler.packet(
            1,
            seat_bindings={1: [{"oid": oid, "authority": "PROJECTION_ONLY", "evidence_refs": ["E1"]}]},
        )
        self.assertEqual(packet["closure"]["population_status"], "HOLD")
        self.assertEqual(packet["closure"]["overall_state"], "HOLD")
        self.assertEqual(packet["population"]["binding_defects"][0]["defect"], "BINDING_AUTHORITY_NOT_CONSTITUTIONAL")
        self.assertEqual(packet["closure"]["next_required_witness"], "REPAIR_CONSTITUTIONAL_SEAT_BINDING")

    def test_full_evidence_bundle_can_close_one_seat_without_implying_neighbors(self):
        made = self.crystal.crystallize_output(
            self.semantic("FULL_SEAT"), "full seat", "memory://cell/full-seat",
            "CELL.CLOSURE", "full-seat", 1)
        oid = made["manifest"]["identity"]["OID"]
        matrix = self.compiler.matrix(
            seat_bindings={1: [{"oid": oid, "authority": "CONSTITUTIONAL_SEAT", "evidence_refs": ["CONST.E1"]}]},
            runtime_evidence={1: {"status": "CLOSED", "operator_ids": ["H6.H01"], "evidence_level": "E4_EXACT_HEAD_CI"}},
            evidence_evidence={1: {"status": "CLOSED", "evidence_level": "E4_EXACT_HEAD_CI"}},
            return_evidence={1: {"status": "CLOSED", "receipt_id": "RETURN.H01"}},
        )
        self.assertEqual(matrix["packets"][0]["closure"]["overall_state"], "CLOSED")
        self.assertEqual(matrix["packets"][0]["closure"]["next_required_witness"], "NONE")
        self.assertNotEqual(matrix["packets"][1]["closure"]["overall_state"], "CLOSED")
        self.assertEqual(matrix["overall_counts"].get("CLOSED"), 1)


if __name__ == "__main__":
    unittest.main()

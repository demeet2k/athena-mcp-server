import copy
import unittest

from athena_mcp.mythic_holonomy_connection_v1 import (
    CONNECTION_RESOURCE,
    CONNECTION_VERSION,
    OPERATOR_STANDING,
    PACKET_ARTIFACT,
    PACKET_VERSION,
    ClosedHolonomyConnectionRuntime,
)
from athena_mcp.mythic_holonomy_protocol import HOLONOMY_RESOURCE
from athena_mcp.mythic_holonomy_surface import (
    MYTHIC_HOLONOMY_RESOURCE_URIS,
    MYTHIC_HOLONOMY_TOOL_NAMES,
    MythicHolonomySurface,
)


def edge(cid, source, target, matrix, offset):
    return {
        "connection_id": cid,
        "source_layer": source,
        "target_layer": target,
        "matrix": matrix,
        "offset": offset,
        "operator_standing": OPERATOR_STANDING,
        "operator_source_ref": f"fixture://{cid}",
        "provenance": ["TEST_FIXTURE_PREDECLARED_BEFORE_EXECUTION"],
        "declared_loss": [],
    }


def identity_packet():
    return {
        "artifact": PACKET_ARTIFACT,
        "version": PACKET_VERSION,
        "packet_id": "HOLV1.IDENTITY",
        "state_space": {
            "basis_id": "BASIS.TEST.R2",
            "dimension": 2,
            "initial_state": [1, 2],
            "state_semantics": ["u", "v"],
        },
        "connections": [
            edge("A_B", "A", "B", [[1, 0], [0, 1]], [1, 0]),
            edge("B_A", "B", "A", [[1, 0], [0, 1]], [-1, 0]),
        ],
        "loop": {
            "loop_id": "L.IDENTITY",
            "start_layer": "A",
            "connection_ids": ["A_B", "B_A"],
        },
    }


class TypedConnectionHolonomyV1Tests(unittest.TestCase):
    def setUp(self):
        self.runtime = ClosedHolonomyConnectionRuntime()

    def test_identity_round_trip_executes_return_edge_and_is_zero(self):
        result = self.runtime.evaluate(identity_packet())
        self.assertEqual(result["status"], "CLOSED_LOOP_HOLONOMY_COMPUTED_V1")
        loop = result["primary_loop"]
        self.assertTrue(loop["all_edges_executed"])
        self.assertTrue(loop["return_edge_executed"])
        self.assertTrue(result["projection_back_executed"])
        self.assertEqual(loop["layer_route"], ["A", "B", "A"])
        self.assertEqual(len(loop["transport_receipts"]), 2)
        self.assertEqual(loop["closed_loop_holonomy_vector"], [0, 0])
        self.assertFalse(loop["closed_loop_holonomy_nonzero"])
        self.assertFalse(loop["operator_holonomy_nonidentity"])

    def test_closed_endpoint_does_not_force_zero_holonomy(self):
        packet = identity_packet()
        packet["packet_id"] = "HOLV1.NONZERO"
        packet["connections"][1]["offset"] = [0, 0]
        result = self.runtime.evaluate(packet)
        loop = result["primary_loop"]
        self.assertEqual(loop["layer_route"][0], loop["layer_route"][-1])
        self.assertEqual(loop["closed_loop_holonomy_vector"], [1, 0])
        self.assertTrue(loop["closed_loop_holonomy_nonzero"])
        self.assertTrue(loop["operator_holonomy_nonidentity"])

    def test_composition_order_is_observable_at_operator_level(self):
        packet = {
            "artifact": PACKET_ARTIFACT,
            "version": PACKET_VERSION,
            "packet_id": "HOLV1.NONCOMMUTE",
            "state_space": {
                "basis_id": "BASIS.TEST.R2",
                "dimension": 2,
                "initial_state": [1, 1],
            },
            "connections": [
                edge("P", "A", "A", [[1, 1], [0, 1]], [0, 0]),
                edge("Q", "A", "A", [[1, 0], [1, 1]], [0, 0]),
            ],
            "loop": {
                "loop_id": "L.PQ",
                "start_layer": "A",
                "connection_ids": ["P", "Q"],
            },
            "comparison_loop": {
                "loop_id": "L.QP",
                "start_layer": "A",
                "connection_ids": ["Q", "P"],
            },
        }
        result = self.runtime.evaluate(packet)
        self.assertTrue(result["path_order_sensitive"])
        self.assertTrue(result["path_order_effect_observed_on_initial_state"])
        self.assertNotEqual(
            result["primary_loop"]["composed_operator"],
            result["comparison_loop"]["composed_operator"],
        )

    def test_missing_return_connection_holds_instead_of_inference(self):
        packet = identity_packet()
        packet["loop"]["connection_ids"] = ["A_B", "MISSING_RETURN"]
        result = self.runtime.evaluate(packet)
        self.assertEqual(result["status"], "HOLD_INVALID_CONNECTION_PACKET")
        self.assertFalse(result["projection_back_executed"])
        self.assertEqual(result["closed_loop_holonomy"], "UNKNOWN")
        self.assertTrue(any("missing_connection:MISSING_RETURN" in e for e in result["errors"]))

    def test_open_path_holds_even_when_endpoint_metadata_exists(self):
        packet = identity_packet()
        packet["loop"]["connection_ids"] = ["A_B"]
        result = self.runtime.evaluate(packet)
        self.assertEqual(result["status"], "HOLD_INVALID_CONNECTION_PACKET")
        self.assertTrue(any("not_closed" in e for e in result["errors"]))
        self.assertFalse(result["projection_back_executed"])

    def test_oracle_coupling_is_rejected(self):
        packet = identity_packet()
        packet["expected_class"] = "NONZERO_HOLONOMY_EXPECTED"
        result = self.runtime.evaluate(packet)
        self.assertEqual(result["status"], "HOLD_ORACLE_COUPLED_PACKET")
        self.assertIn("oracle_coupled_packet", result["errors"])

    def test_operator_must_be_predeclared_and_dimension_valid(self):
        packet = identity_packet()
        packet["connections"][0]["operator_standing"] = "INFERRED_FROM_EXPECTED_LABEL"
        packet["connections"][1]["matrix"] = [[1, 0, 0], [0, 1, 0]]
        result = self.runtime.evaluate(packet)
        self.assertEqual(result["status"], "HOLD_INVALID_CONNECTION_PACKET")
        self.assertTrue(any("operator_standing" in e for e in result["errors"]))
        self.assertTrue(any("matrix_dimension" in e for e in result["errors"]))

    def test_surface_exposes_v0_proxy_and_v1_connection_as_distinct_tools(self):
        surface = MythicHolonomySurface()
        self.assertIn("athena_mck_holonomy_evaluate", MYTHIC_HOLONOMY_TOOL_NAMES)
        self.assertIn("athena_mck_closed_holonomy_evaluate", MYTHIC_HOLONOMY_TOOL_NAMES)
        self.assertIn(HOLONOMY_RESOURCE["uri"], MYTHIC_HOLONOMY_RESOURCE_URIS)
        self.assertIn(CONNECTION_RESOURCE["uri"], MYTHIC_HOLONOMY_RESOURCE_URIS)

        v0 = surface.read_resource(HOLONOMY_RESOURCE["uri"])
        self.assertFalse(v0["projection_back_executed"])
        self.assertIn("OPEN_PATH_DRIFT_PROXY", v0["loop_vector_standing"])

        v1 = surface.read_resource(CONNECTION_RESOURCE["uri"])
        self.assertEqual(v1["version"], CONNECTION_VERSION)
        self.assertEqual(v1["missing_connection_behavior"], "HOLD")
        self.assertEqual(v1["oracle_coupling_behavior"], "HOLD")
        self.assertFalse(v1["mck_v2_promotion"])

        handled, result = surface.call_tool(
            "athena_mck_closed_holonomy_evaluate",
            {"packet": identity_packet()},
        )
        self.assertTrue(handled)
        self.assertEqual(result["status"], "CLOSED_LOOP_HOLONOMY_COMPUTED_V1")


if __name__ == "__main__":
    unittest.main()

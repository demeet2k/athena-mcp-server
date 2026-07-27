from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve()
MODULE_PATH = HERE.parents[1] / "MCP/crystal_108d/federation_v2.py"
SPEC = importlib.util.spec_from_file_location("athena_federation_v2", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
FrozenFederation = MODULE.FrozenFederation
FederationSnapshotError = MODULE.FederationSnapshotError


class FakeMCP:
    def __init__(self) -> None:
        self.tools = {}
        self.resources = {}

    def tool(self):
        def decorator(function):
            self.tools[function.__name__] = function
            return function

        return decorator

    def resource(self, uri):
        def decorator(function):
            self.resources[uri] = function
            return function

        return decorator


class FederationV2ConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_root = (
            HERE.parents[1] / "MCP/data/athena_federation_v2"
        )
        cls.consumer = FrozenFederation.load(cls.data_root)

    def test_snapshot_is_exact_and_verified(self) -> None:
        status = self.consumer.status()
        self.assertEqual(status["verdict"], "READY")
        self.assertEqual(status["resource_versions"], 14)
        self.assertEqual(status["identifiers"], 56)
        self.assertEqual(status["edges"], 26)
        self.assertEqual(
            status["control_commit"],
            "13cda0bed07a881d42446e3a282eb1ba84ea9b45",
        )
        self.assertEqual(
            status["release_candidate"], "KC144.MYC.P05.RC1"
        )
        self.assertEqual(
            status["selected_contract_lineage"], "git-brain-v2"
        )
        self.assertEqual(
            status["cold_replay"],
            "PASS[CANONICAL_COLD_REPLAY_10_OF_10]",
        )
        self.assertFalse(status["promotion_ready"])
        self.assertEqual(
            status["graph_digest"],
            "sha256:82a3f9e2369394f39080b795476342688b95e35dcfcda3fe6a8be0212618d8d1",
        )

    def test_legacy_amc_address_rebounds_to_exact_v2_identity(self) -> None:
        result = self.consumer.resolve(
            "amc://github/compression/repo-q-shrink@0.1.0?lens=11#codec"
        )
        self.assertEqual(result["verdict"], "FOUND")
        self.assertEqual(result["answered_by"], "athena-federation-v2")
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["resource"]["rid"], "athena.repo.q-shrink")

    def test_cross_repository_route_has_return_plan(self) -> None:
        receipt = self.consumer.route(
            "athena.repo.q-shrink",
            "athena.runtime.route-compiler",
            created_at="2026-07-27T04:00:00Z",
        )
        self.assertEqual(receipt["verdict"], "FOUND")
        self.assertEqual(receipt["answered_by"], "athena-federation-v2")
        self.assertEqual(
            receipt["hops"],
            ["edge.q-shrink-to-control", "edge.control-to-runtime"],
        )
        self.assertEqual(
            receipt["return_plan"],
            ["edge.runtime-to-control", "edge.control-to-q-shrink"],
        )

    def test_cutover_receipt_witnesses_forward_return_fallback_and_rollback(
        self,
    ) -> None:
        receipt = self.consumer.cutover_receipt(
            observed_at="2026-07-27T04:00:00Z"
        )
        self.assertEqual(receipt["verdict"], "PASS_LOCAL_NOT_DEPLOYED")
        self.assertEqual(
            receipt["forward_return"]["hops"],
            ["edge.q-shrink-to-control", "edge.control-to-runtime"],
        )
        self.assertEqual(
            receipt["forward_return"]["return_plan"],
            ["edge.runtime-to-control", "edge.control-to-q-shrink"],
        )
        self.assertEqual(
            receipt["v1_fallback"]["answered_by"], "athena-108d-v1"
        )
        self.assertTrue(receipt["v1_fallback"]["fallback_used"])
        self.assertEqual(
            receipt["rollback"]["predecessor_commit"],
            "0ee038011295873ba037a3cac25de18544439293",
        )
        self.assertFalse(receipt["promotion_claimed"])
        self.assertIsNone(receipt["deployment_witness"])

    def test_registered_legacy_resource_uses_explicit_v1_fallback(self) -> None:
        result = self.consumer.resolve("athena://crystal-108d")
        self.assertEqual(result["verdict"], "FOUND_LEGACY")
        self.assertEqual(result["answered_by"], "athena-108d-v1")
        self.assertTrue(result["fallback_used"])

    def test_unknown_identifier_does_not_fuzzy_match(self) -> None:
        result = self.consumer.resolve("KC144")
        self.assertEqual(result["verdict"], "INVALID_ADDRESS")
        self.assertFalse(result["fallback_used"])

    def test_manuscript_fork_remains_distinct(self) -> None:
        canonical = self.consumer.resolve("athena.repo.manuscript-being")
        legacy = self.consumer.resolve("athena.repo.manscript-being")
        self.assertEqual(canonical["verdict"], "FOUND")
        self.assertEqual(legacy["verdict"], "FOUND")
        self.assertNotEqual(
            canonical["resource"]["rid"], legacy["resource"]["rid"]
        )
        self.assertEqual(legacy["resource"]["state"], "IDENTITY_FORK_HOLD")

    def test_mcp_registration_is_additive(self) -> None:
        fake = FakeMCP()
        MODULE.register_federation_v2(fake)
        self.assertEqual(
            set(fake.tools),
            {
                "athena_federation_status",
                "resolve_athena_identity",
                "route_athena_federation",
                "athena_federation_cutover_receipt",
            },
        )
        self.assertEqual(
            set(fake.resources),
            {
                "athena://federation-v2",
                "athena://federation-v2/cutover",
                "athena://federation-v2/lock",
            },
        )


if __name__ == "__main__":
    unittest.main()

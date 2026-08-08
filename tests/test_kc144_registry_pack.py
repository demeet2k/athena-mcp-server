import unittest

from athena_mcp.kc144_registry_pack import (
    catalog,
    cell_bundle,
    completion_frontier,
    cross_search,
    manifest,
    query_registry,
    source_bundle,
    status,
    verify_pack,
)


class KC144RegistryPackTests(unittest.TestCase):
    def test_pack_verifies_and_preserves_declared_counts(self):
        receipt = verify_pack(deep=True)
        self.assertEqual(receipt["status"], "PASS", receipt)
        self.assertEqual(receipt["observed_counts"]["cells"], 144)
        self.assertEqual(receipt["observed_counts"]["completion"], 126)
        self.assertEqual(receipt["observed_counts"]["math"], 9771)
        self.assertEqual(receipt["observed_counts"]["graphs"], 3210)
        self.assertEqual(receipt["observed_counts"]["harnesses"], 728)

    def test_manifest_catalog_and_package_state(self):
        self.assertEqual(manifest()["counts"]["tools"], 120)
        names = {item["name"] for item in catalog()["registries"]}
        for name in ("cells", "coordinates", "datasets", "graphs", "harnesses", "math", "skills", "tools"):
            self.assertIn(name, names)
        packet = status()
        self.assertEqual(packet["state"], "DIGEST_BOUND_PACKAGE_DATA")
        self.assertEqual(packet["carrier_count"], 1)

    def test_bounded_query_and_nested_filter(self):
        result = query_registry("math", query="prime", limit=5)
        self.assertLessEqual(result["returned"], 5)
        self.assertEqual(result["registry"], "math")
        found = query_registry("cells", filters={"address.gid": 1}, limit=10)
        self.assertEqual(found["returned"], 1)
        self.assertEqual(found["items"][0]["address"]["sid"], "KC144.SID.001")

    def test_cross_search_is_bounded_and_deterministic(self):
        first = cross_search("prime", registries=["math", "graphs"], limit=8, per_registry=5)
        second = cross_search("prime", registries=["graphs", "math"], limit=8, per_registry=5)
        self.assertLessEqual(first["returned"], 8)
        self.assertEqual(first["result_digest"], second["result_digest"])
        self.assertEqual(first["ranking_law"], second["ranking_law"])

    def test_exact_source_and_cell_lenses(self):
        bundle = source_bundle("GDOC.ATHENA.DISTRIBUTED_BRAIN_8", limit_per_registry=10)
        self.assertTrue(bundle["source_found"])
        self.assertGreaterEqual(bundle["counts"]["datasets"], 1)
        cell = cell_bundle(1)
        self.assertEqual(cell["cell"]["address"]["gid"], 1)
        self.assertIn("hosted_counts", cell["cell"])

    def test_completion_frontier_projection(self):
        root = completion_frontier(limit=10)
        self.assertEqual(root["ready_total"], 1)
        self.assertEqual(root["frontier"][0]["task_id"], "TASK.000")
        advanced = completion_frontier(completed_task_ids=["TASK.000"], limit=10)
        self.assertEqual(advanced["frontier"][0]["task_id"], "TASK.001")
        self.assertEqual(advanced["unknown_completed_task_ids"], [])


if __name__ == "__main__":
    unittest.main()

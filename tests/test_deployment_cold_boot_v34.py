import importlib.util
import pathlib
import unittest


def load_module():
    path = pathlib.Path(__file__).resolve().parents[1] / "deploy" / "cold_boot_v34.py"
    spec = importlib.util.spec_from_file_location("cold_boot_v34", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ColdBootV34ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_identity_constants_are_exact_and_nonpublishing(self):
        self.assertEqual(self.mod.EXPECTED_VERSION, "3.4.0")
        self.assertEqual(self.mod.EXPECTED_MANIFEST, "ATHENA.RUNTIME.UNIFIED.11")
        self.assertEqual(self.mod.EXPECTED_COLLECTIVE, "COLLECTIVE_CALIBRATED_V15")
        self.assertEqual(self.mod.EXPECTED_COORDINATE, "COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>")
        self.assertTrue(self.mod.AUTHORITY_FALSE)
        self.assertTrue(all(value is False for value in self.mod.AUTHORITY_FALSE.values()))

    def test_cross_instance_accepts_semantic_match_with_physical_difference(self):
        semantic = {"oid": "O", "vid": "V", "head_digest": "D"}
        a = {
            "manifest_semantic_digest": "M",
            "semantic_after_restart": semantic,
            "semantic_restart_match": True,
            "physical_events": {"eid": "A"},
        }
        b = {
            "manifest_semantic_digest": "M",
            "semantic_after_restart": semantic,
            "semantic_restart_match": True,
            "physical_events": {"eid": "B"},
        }
        result = self.mod.validate_cross_instance(a, b)
        self.assertTrue(all(result.values()))

    def test_cross_instance_rejects_semantic_drift(self):
        a = {
            "manifest_semantic_digest": "M1",
            "semantic_after_restart": {"vid": "V1"},
            "semantic_restart_match": True,
            "physical_events": {"eid": "A"},
        }
        b = {
            "manifest_semantic_digest": "M2",
            "semantic_after_restart": {"vid": "V2"},
            "semantic_restart_match": True,
            "physical_events": {"eid": "B"},
        }
        with self.assertRaises(AssertionError):
            self.mod.validate_cross_instance(a, b)

    def test_cross_instance_requires_independent_physical_history(self):
        semantic = {"vid": "V"}
        a = {
            "manifest_semantic_digest": "M",
            "semantic_after_restart": semantic,
            "semantic_restart_match": True,
            "physical_events": {"eid": "SAME"},
        }
        b = dict(a)
        with self.assertRaises(AssertionError):
            self.mod.validate_cross_instance(a, b)


if __name__ == "__main__":
    unittest.main()

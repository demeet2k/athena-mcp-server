from __future__ import annotations

import types
import unittest
from unittest import mock

from athena_mcp import synapse_observer_extension as extension


class SynapseObserverExtensionTests(unittest.TestCase):
    def test_missing_companion_adapter_is_optional_not_failure(self):
        original = extension.importlib.import_module

        def missing(name):
            if name == "athena_mcp.synapse_liminal_adapter":
                exc = ModuleNotFoundError("missing optional adapter")
                exc.name = name
                raise exc
            return original(name)

        with mock.patch.object(extension.importlib, "import_module", side_effect=missing):
            status = extension._synapse_abi_status()
        self.assertFalse(status["adapter_installed"])
        self.assertEqual(status["expected_schema"], extension.EXPECTED_SYNAPSE_SCHEMA)
        self.assertEqual(status["standing"], "OPTIONAL_COMPANION_UNOBSERVED")

    def test_companion_adapter_match_projects_profiles_without_dependency(self):
        fake = types.SimpleNamespace(
            SYNAPSE_SCHEMA=extension.EXPECTED_SYNAPSE_SCHEMA,
            PACKET_PROFILE="LIMINAL_BEACON_CAPSULE_V1",
            RECEIPT_PROFILE="LIMINAL_BEACON_RECEIPT_V1",
        )
        with mock.patch.object(extension.importlib, "import_module", return_value=fake):
            status = extension._synapse_abi_status()
        self.assertTrue(status["adapter_installed"])
        self.assertTrue(status["schema_match"])
        self.assertEqual(status["standing"], "COMPANION_SCHEMA_MATCH")
        self.assertEqual(status["packet_profile"], "LIMINAL_BEACON_CAPSULE_V1")
        self.assertEqual(status["receipt_profile"], "LIMINAL_BEACON_RECEIPT_V1")
        self.assertEqual(status["law"], "BRIDGE_RECEIPT_TOKEN != SYNAPSE_PROJECTION_RETURN_TOKEN")

    def test_companion_schema_drift_holds(self):
        fake = types.SimpleNamespace(
            SYNAPSE_SCHEMA="ATHENA.SYNAPSE.ENVELOPE.V2",
            PACKET_PROFILE="future",
            RECEIPT_PROFILE="future",
        )
        with mock.patch.object(extension.importlib, "import_module", return_value=fake):
            status = extension._synapse_abi_status()
        self.assertTrue(status["adapter_installed"])
        self.assertFalse(status["schema_match"])
        self.assertEqual(status["standing"], "COMPANION_SCHEMA_MISMATCH_HOLD")

    def test_decorate_preserves_observer_payload_and_adds_abi_status(self):
        fake = types.SimpleNamespace(
            SYNAPSE_SCHEMA=extension.EXPECTED_SYNAPSE_SCHEMA,
            PACKET_PROFILE="p",
            RECEIPT_PROFILE="r",
        )
        with mock.patch.object(extension.importlib, "import_module", return_value=fake):
            value = extension._decorate({"artifact": "x", "status": "OK"})
        self.assertEqual(value["artifact"], "x")
        self.assertEqual(value["status"], "OK")
        self.assertTrue(value["cross_repository_synapse_abi"]["schema_match"])


if __name__ == "__main__":
    unittest.main()

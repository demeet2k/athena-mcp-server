from __future__ import annotations

import copy
import unittest

from athena_mcp.release_abi import ABI_ALGORITHM, ABI_SCHEMA, compute_public_abi, fingerprint_from_surface


class ReleaseAbiFingerprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.abi=compute_public_abi()
        print("ATHENA_RELEASE_ABI",cls.abi["digest"],cls.abi["counts"],flush=True)

    def test_record_is_complete_and_deterministic(self):
        abi=self.abi
        self.assertEqual(abi["schema"],ABI_SCHEMA)
        self.assertEqual(abi["algorithm"],ABI_ALGORITHM)
        self.assertRegex(abi["digest"],r"^[0-9A-F]{64}$")
        self.assertGreater(abi["counts"]["tools"],100)
        self.assertGreater(abi["counts"]["resources"],20)
        self.assertGreaterEqual(abi["counts"]["prompts"],1)
        self.assertEqual(compute_public_abi()["digest"],abi["digest"])

    def test_surface_names_are_unique(self):
        surface=self.abi["surface"]
        for key,name_key in (("tools","name"),("resources","uri"),("prompts","name")):
            names=[row[name_key] for row in surface[key]]
            self.assertEqual(len(names),len(set(names)),f"duplicate {key} interface identity")

    def test_input_order_does_not_change_digest(self):
        surface=copy.deepcopy(self.abi["surface"])
        changed=copy.deepcopy(surface)
        changed["tools"].reverse();changed["resources"].reverse();changed["prompts"].reverse()
        self.assertEqual(fingerprint_from_surface(surface)["digest"],fingerprint_from_surface(changed)["digest"])

    def test_tool_schema_change_changes_abi(self):
        surface=copy.deepcopy(self.abi["surface"])
        mutated=copy.deepcopy(surface)
        mutated["tools"][0]["inputSchema"]={"type":"object","properties":{"abi_probe":{"type":"string"}},"additionalProperties":False}
        changed=fingerprint_from_surface(mutated)
        self.assertNotEqual(changed["digest"],self.abi["digest"])
        self.assertNotEqual(changed["section_digests"]["tools"],self.abi["section_digests"]["tools"])
        self.assertEqual(changed["section_digests"]["resources"],self.abi["section_digests"]["resources"])

    def test_resource_change_changes_abi(self):
        surface=copy.deepcopy(self.abi["surface"])
        mutated=copy.deepcopy(surface)
        mutated["resources"][0]["name"]="ABI probe changed resource name"
        changed=fingerprint_from_surface(mutated)
        self.assertNotEqual(changed["digest"],self.abi["digest"])
        self.assertNotEqual(changed["section_digests"]["resources"],self.abi["section_digests"]["resources"])

    def test_prompt_contract_change_changes_abi(self):
        surface=copy.deepcopy(self.abi["surface"])
        mutated=copy.deepcopy(surface)
        mutated["prompts"][0]["arguments"]=list(mutated["prompts"][0].get("arguments",[]))+[{"name":"abi_probe","required":False}]
        changed=fingerprint_from_surface(mutated)
        self.assertNotEqual(changed["digest"],self.abi["digest"])
        self.assertNotEqual(changed["section_digests"]["prompts"],self.abi["section_digests"]["prompts"])

    def test_laws_separate_abi_from_release_authority(self):
        self.assertIn("PACKAGE_VERSION_IDENTITY != ABI_IDENTITY",self.abi["laws"])
        self.assertIn("SAME_VERSION_REQUIRES_SAME_FROZEN_ABI",self.abi["laws"])
        self.assertIn("ABI_FINGERPRINT != PROMOTION_AUTHORITY",self.abi["laws"])


if __name__=="__main__":unittest.main()

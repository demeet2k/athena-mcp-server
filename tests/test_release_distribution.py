import json
import re
import tomllib
import unittest
from pathlib import Path


class ReleaseDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.manifest = json.loads(
            (cls.root / "release" / "v3.0.0.json").read_text()
        )
        cls.project = tomllib.loads(
            (cls.root / "pyproject.toml").read_text()
        )["project"]
        cls.workflow = (
            cls.root / ".github" / "workflows" / "release.yml"
        ).read_text()

    def test_release_identity_matches_package(self):
        self.assertEqual(self.manifest["schema"], "ATHENA.RELEASE.DISTRIBUTION.1")
        self.assertEqual(self.manifest["version"], "3.0.0")
        self.assertEqual(self.manifest["tag"], "v3.0.0")
        self.assertEqual(self.project["version"], self.manifest["version"])
        self.assertEqual(self.project["name"], self.manifest["package"]["name"])
        self.assertEqual(
            self.project["scripts"]["athena-mcp"],
            self.manifest["package"]["entrypoint"],
        )

    def test_source_and_assets_are_explicit(self):
        source = self.manifest["source"]
        self.assertEqual(source["target_branch"], "agent/aor-collective-unified")
        self.assertRegex(source["integration_commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(source["integration_tree"], r"^[0-9a-f]{40}$")
        self.assertEqual(source["post_merge_unit_tests"], 311)
        assets = set(self.manifest["release"]["required_assets"])
        self.assertEqual(
            assets,
            {
                "athena_canonical_mcp-3.0.0-py3-none-any.whl",
                "kc144-core-registries.tar.xz",
                "release-manifest.json",
                "release-attestation.json",
                "SHA256SUMS",
            },
        )

    def test_release_workflow_is_exact_head_and_fail_closed(self):
        required_fragments = (
            "permissions:\n  contents: write",
            "agent/aor-collective-unified",
            "python -m unittest discover -s tests -v",
            "python -m pip wheel --no-deps . -w dist",
            "athena_mcp.hub_server",
            "gh release create",
            "--verify-tag",
            "refs/tags/$TAG",
            "TAG_TARGET",
            "SHA256SUMS",
        )
        for fragment in required_fragments:
            self.assertIn(fragment, self.workflow)
        self.assertNotRegex(self.workflow, re.compile(r"continue-on-error:\s*true"))

    def test_boundary_does_not_collapse_distribution_into_deployment(self):
        boundaries = " ".join(self.manifest["authority_boundaries"]).lower()
        for phrase in (
            "not deployment",
            "not empirical truth",
            "do not become y1 authority",
            "does not authorize production",
        ):
            self.assertIn(phrase, boundaries)


if __name__ == "__main__":
    unittest.main()

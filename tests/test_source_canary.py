import json
import unittest

from athena_mcp.deployment import validate_image_ref
from deploy.canary_observer import build_parser, compile_witness, run
from deploy.source_canary import digest, verify_artifact


class SourceCanaryTests(unittest.TestCase):
    def fixture(self):
        source = "b" * 40
        config = {"config": {"User": "65532:65532", "Labels": {
            "org.opencontainers.image.revision": source}}}
        config_raw = json.dumps(config).encode()
        manifest_raw = json.dumps({"schemaVersion": 2, "layers": [], "config": {
            "digest": digest(config_raw)}}).encode()
        image = "127.0.0.1:15000/athena-candidate@" + digest(manifest_raw)
        return dict(image_ref=image, source_head=source, manifest_raw=manifest_raw,
                    config_raw=config_raw, image_inspect={"Id": digest(config_raw),
                    "RepoDigests": [image], "Config": config["config"]},
                    expected_files={"server.py": "a" * 64},
                    installed_files={"server.py": "a" * 64})

    def test_manifest_config_and_python_bind_independently(self):
        values = self.fixture()
        result = verify_artifact(**values)
        self.assertNotEqual(result["manifest_digest"], result["config_digest"])
        self.assertEqual(result["python_file_count"], 1)
        self.assertFalse(result["publication_performed"])

    def test_config_digest_cannot_masquerade_as_manifest(self):
        values = self.fixture()
        values["image_ref"] = "127.0.0.1:15000/athena-candidate@" + digest(values["config_raw"])
        with self.assertRaisesRegex(ValueError, "manifest bytes"):
            verify_artifact(**values)

    def test_matching_label_does_not_excuse_different_code(self):
        for changed in ({"server.py": "f" * 64}, {}, {"server.py": "a" * 64, "extra.py": "e" * 64}):
            with self.subTest(changed=changed):
                values = self.fixture()
                values["installed_files"] = changed
                with self.assertRaisesRegex(ValueError, "installed Python"):
                    verify_artifact(**values)

    def test_other_image_or_missing_repo_digest_fails(self):
        for key, value in (("Id", "sha256:" + "f" * 64), ("RepoDigests", [])):
            with self.subTest(key=key):
                values = self.fixture()
                values["image_inspect"][key] = value
                with self.assertRaises(ValueError):
                    verify_artifact(**values)

    def test_source_label_and_config_bytes_cannot_be_substituted(self):
        values = self.fixture()
        values["source_head"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "revision label"):
            verify_artifact(**values)
        values = self.fixture()
        values["config_raw"] += b" "
        with self.assertRaisesRegex(ValueError, "config bytes"):
            verify_artifact(**values)

    def test_registry_ports_are_validated_without_resolving(self):
        for port in (1, 15000, 65535):
            image = f"127.0.0.1:{port}/athena@sha256:" + "a" * 64
            self.assertEqual(validate_image_ref(image)["image_ref"], image)
        for host in ("127.0.0.1:0", "127.0.0.1:65536", "127.0.0.1:abc", "https://host:5000"):
            with self.assertRaises(ValueError):
                validate_image_ref(host + "/athena@sha256:" + "a" * 64)

    def test_candidate_witness_has_no_release_claims(self):
        witness = compile_witness(image_ref=self.fixture()["image_ref"], source_head="b" * 40,
            release_tag=None, release_run_id=None, oci_run_id=None, workflow_run_id="123",
            workflow_head="b" * 40, control_catalog={}, canary_catalog={},
            state_witness={"matched": True}, baseline_metrics={}, canary_metrics={},
            assessment={"version": "ATHENA.CANARY.ASSESSMENT.2", "decision": "HOLD"},
            observation_window_seconds=63, source_candidate=True)
        self.assertEqual(witness["subject_kind"], "UNPUBLISHED_SOURCE_CANDIDATE")
        self.assertIsNone(witness["release_tag"])
        self.assertIsNone(witness["release_run_id"])
        self.assertIsNone(witness["oci_run_id"])
        self.assertFalse(witness["publication_performed"])
        self.assertFalse(any(witness["authority"].values()))

    def test_mixed_or_missing_release_coordinates_fail_before_contact(self):
        base = ["--image-ref", self.fixture()["image_ref"], "--source-head", "b" * 40,
                "--workflow-run-id", "123", "--workflow-head", "b" * 40]
        for extra in ([], ["--source-candidate", "--release-tag", "v3.3.0"]):
            with self.assertRaisesRegex(ValueError, "release"):
                run(build_parser().parse_args(base + extra))


if __name__ == "__main__":
    unittest.main()

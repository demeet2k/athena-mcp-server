import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class DeploymentArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.dockerfile = (cls.root / "Dockerfile").read_text()
        cls.compose = (cls.root / "deploy" / "compose.yaml").read_text()
        cls.template = (
            cls.root / "deploy" / "kubernetes" / "athena.yaml.tmpl"
        ).read_text()

    def test_container_is_non_root_fail_closed_and_persistent(self):
        for fragment in (
            "USER 65532:65532",
            "VOLUME [\"/var/lib/athena\"]",
            "ENTRYPOINT [\"athena-mcp-http\"]",
            "ATHENA_SCHEMA_MIGRATE=true",
            "/readyz",
        ):
            self.assertIn(fragment, self.dockerfile)
        self.assertNotIn("ATHENA_HTTP_TOKEN=", self.dockerfile)

    def test_compose_and_kubernetes_preserve_single_writer_security(self):
        for fragment in (
            'user: "65532:65532"',
            "read_only: true",
            "no-new-privileges:true",
            "cap_drop:",
            "127.0.0.1:",
        ):
            self.assertIn(fragment, self.compose)
        for fragment in (
            "replicas: 1",
            "type: Recreate",
            "ReadWriteOnce",
            "runAsNonRoot: true",
            "readOnlyRootFilesystem: true",
            "allowPrivilegeEscalation: false",
            "automountServiceAccountToken: false",
            "@@IMAGE@@",
        ):
            self.assertIn(fragment, self.template)

    def test_renderer_rejects_tag_and_binds_one_digest(self):
        digest = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "b" * 64
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "athena.yaml"
            receipt = Path(directory) / "receipt.json"
            subprocess.run(
                [
                    sys.executable,
                    "deploy/render.py",
                    "--image",
                    digest,
                    "--output",
                    str(output),
                    "--receipt",
                    str(receipt),
                ],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
            rendered = output.read_text()
            self.assertEqual(rendered.count(digest), 1)
            self.assertNotIn("@@IMAGE@@", rendered)
            self.assertEqual(json.loads(receipt.read_text())["status"], "PASS")
            failed = subprocess.run(
                [
                    sys.executable,
                    "deploy/render.py",
                    "--image",
                    "ghcr.io/demeet2k/athena-mcp-server:3.1.0",
                    "--output",
                    str(output),
                ],
                cwd=self.root,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(failed.returncode, 0)


if __name__ == "__main__":
    unittest.main()

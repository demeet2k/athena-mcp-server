"""Qualify an unpublished source candidate in an ephemeral loopback registry.

Run only on a disposable Docker host. This creates its own containers/volumes,
exports the image and evidence, and removes only those temporary resources.
It never switches an installed runtime, reads production state, or publishes a release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import urllib.request

from athena_mcp.deployment import validate_image_ref
from deploy import canary_observer

SCHEMA = "ATHENA.SOURCE.CANARY.ARTIFACT.1"
INVENTORY_PROGRAM = """import hashlib,json,pathlib,athena_mcp
p=pathlib.Path(athena_mcp.__file__).parent
print(json.dumps({str(f.relative_to(p)).replace(chr(92),'/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*.py')},sort_keys=True))
"""


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def command(*args: str, env: dict | None = None, timeout: int = 600) -> str:
    result = subprocess.run(args, check=True, capture_output=True, text=True,
                            encoding="utf-8", env=env, timeout=timeout)
    return result.stdout.strip()


def write_json(path: Path, value: dict | list) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_artifact(*, image_ref: str, source_head: str, manifest_raw: bytes,
                    config_raw: bytes, image_inspect: dict,
                    expected_files: dict, installed_files: dict) -> dict:
    """Cross-check raw registry bytes, Docker inspection and installed Python files.

    Inputs are observations from the calling host, not signed remote attestation.
    The caller preserves them for independent replay.
    """
    image = validate_image_ref(image_ref)
    if digest(manifest_raw) != image["digest"]:
        raise ValueError("registry manifest bytes do not match image reference")
    manifest = json.loads(manifest_raw)
    config = json.loads(config_raw)
    if manifest.get("schemaVersion") != 2 or "layers" not in manifest:
        raise ValueError("expected a single-platform image manifest, not an index")
    config_digest = digest(config_raw)
    if manifest.get("config", {}).get("digest") != config_digest:
        raise ValueError("config bytes do not match manifest descriptor")
    if image_inspect.get("Id") != config_digest:
        raise ValueError("Docker config identity does not match registry config")
    if image_ref not in image_inspect.get("RepoDigests", []):
        raise ValueError("Docker inspection lacks the exact repository digest")
    if len(source_head) != 40 or any(c not in "0123456789abcdef" for c in source_head):
        raise ValueError("expected full source SHA")
    for cfg in (config.get("config", {}), image_inspect.get("Config", {})):
        if cfg.get("Labels", {}).get("org.opencontainers.image.revision") != source_head:
            raise ValueError("source revision label mismatch")
        if cfg.get("User") != "65532:65532":
            raise ValueError("expected non-root runtime")
    if not expected_files or expected_files != installed_files:
        raise ValueError("installed Python package files differ from source inventory")
    return {
        "schema": SCHEMA, "source_head": source_head, "image_ref": image_ref,
        "manifest_digest": image["digest"], "config_digest": config_digest,
        "python_file_count": len(installed_files),
        "python_inventory_digest": digest(json.dumps(installed_files, sort_keys=True,
                                                     separators=(",", ":")).encode()),
        "identity_scope": "REGISTRY_MANIFEST_CONFIG_AND_INSTALLED_PYTHON_BYTES",
        "publication_performed": False,
        "boundary": "Host-observed candidate identity, not signed provenance, a reproducible base-image claim, a release, or production activation.",
    }


def registry_get(url: str, *, accept: str | None = None) -> tuple[bytes, dict]:
    headers = {"Accept": accept} if accept else {}
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as response:
        return response.read(), dict(response.headers)


def run(source_head: str, workflow_run_id: str, output: Path) -> dict:
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    if command("git", "rev-parse", "HEAD") != source_head:
        raise ValueError("checkout does not match requested source head")
    if command("git", "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("candidate checkout must be clean before build")
    source_files = command("git", "ls-files", "athena_mcp").splitlines()
    expected = {str(Path(f).relative_to("athena_mcp")).replace("\\", "/"):
                hashlib.sha256(Path(f).read_bytes()).hexdigest()
                for f in source_files if f.endswith(".py")}
    output.mkdir(parents=True, exist_ok=True)
    prefix = "athena-candidate-" + secrets.token_hex(6)
    registry = prefix + "-registry"
    names = [prefix + "-control", prefix + "-canary"]
    volumes = [name + "-state" for name in names]
    tokens = [secrets.token_urlsafe(36), secrets.token_urlsafe(36)]
    repository = "127.0.0.1:15000/athena-candidate"
    tag = repository + ":" + source_head
    try:
        command("docker", "run", "-d", "--name", registry,
                "-p", "127.0.0.1:15000:5000", "registry:2")
        for attempt in range(40):
            try:
                registry_get("http://127.0.0.1:15000/v2/")
                break
            except OSError:
                if attempt == 39:
                    raise
                time.sleep(0.25)
        command("docker", "build", "--label", "org.opencontainers.image.revision=" + source_head,
                "-t", tag, ".")
        command("docker", "push", tag)
        manifest_raw, headers = registry_get(
            "http://127.0.0.1:15000/v2/athena-candidate/manifests/" + source_head,
            accept="application/vnd.docker.distribution.manifest.v2+json")
        manifest_digest = digest(manifest_raw)
        observed_header = next((v for k, v in headers.items()
                                if k.lower() == "docker-content-digest"), None)
        if observed_header != manifest_digest:
            raise ValueError("registry digest header differs from raw manifest")
        image_ref = repository + "@" + manifest_digest
        config_descriptor = json.loads(manifest_raw)["config"]["digest"]
        config_raw, _ = registry_get("http://127.0.0.1:15000/v2/athena-candidate/blobs/" + config_descriptor)
        command("docker", "pull", image_ref)
        inspection = json.loads(command("docker", "image", "inspect", image_ref))[0]
        installed = json.loads(command("docker", "run", "--rm", "--network", "none",
                                      "--read-only", "--entrypoint", "python", image_ref,
                                      "-c", INVENTORY_PROGRAM))
        binding = verify_artifact(image_ref=image_ref, source_head=source_head,
                                  manifest_raw=manifest_raw, config_raw=config_raw,
                                  image_inspect=inspection, expected_files=expected,
                                  installed_files=installed)
        binding["workflow_run_id"] = workflow_run_id
        (output / "registry-manifest.json").write_bytes(manifest_raw)
        (output / "registry-config.json").write_bytes(config_raw)
        write_json(output / "image-inspect.json", inspection)
        write_json(output / "source-python-files.json", expected)
        write_json(output / "installed-python-files.json", installed)
        write_json(output / "artifact-binding.json", binding)
        safe_instances = []
        for index, (name, volume, token) in enumerate(zip(names, volumes, tokens)):
            command("docker", "volume", "create", volume)
            command("docker", "run", "-d", "--name", name, "--read-only",
                    "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges", "--cpus", "1", "--memory", "512m",
                    "-e", "ATHENA_HTTP_TOKEN", "-p", f"127.0.0.1:{18765 + index}:8765",
                    "-v", volume + ":/var/lib/athena", image_ref,
                    env={**os.environ, "ATHENA_HTTP_TOKEN": token})
            observed = json.loads(command("docker", "inspect", name))[0]
            if (observed["Image"] != binding["config_digest"] or
                    observed["Config"]["Image"] != image_ref or
                    observed["HostConfig"]["ReadonlyRootfs"] is not True):
                raise ValueError("running container identity or read-only root mismatch")
            # Exclude Config.Env, which contains the ephemeral bearer token.
            safe_instances.append({"name": name, "container_id": observed["Id"],
                                   "image_config_digest": observed["Image"], "image_ref": image_ref,
                                   "mounts": observed["Mounts"], "read_only_root": True})
        write_json(output / "instances.json", safe_instances)
        args = canary_observer.build_parser().parse_args([
            "--source-candidate", "--image-ref", image_ref, "--source-head", source_head,
            "--workflow-run-id", workflow_run_id, "--workflow-head", source_head,
            "--control-container", names[0], "--canary-container", names[1],
            "--output-dir", str(output)])
        previous = {key: os.environ.get(key) for key in (args.control_token_env, args.canary_token_env)}
        try:
            os.environ[args.control_token_env], os.environ[args.canary_token_env] = tokens
            witness = canary_observer.run(args)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        if not all(witness["structural_match"].values()):
            raise ValueError("canary structural witnesses differ")
        archive = output / "candidate-image.tar"
        command("docker", "image", "save", "--output", str(archive), tag)
        with archive.open("rb") as stream:
            archive_digest = "sha256:" + hashlib.file_digest(stream, "sha256").hexdigest()
        result = {"schema": "ATHENA.SOURCE.CANARY.RESULT.1", "status": "PASS_ISOLATED_CANDIDATE",
                  "source_head": source_head, "workflow_run_id": workflow_run_id,
                  "image_ref": image_ref, "image_archive_sha256": archive_digest,
                  "artifact_binding_sha256": digest((output / "artifact-binding.json").read_bytes()),
                  "canary_witness_digest": witness["witness_digest"],
                  "cutover_performed": False, "publication_performed": False,
                  "boundary": "Loopback registry will be removed. The saved image archive is a transport artifact; its SHA256 is not an OCI manifest digest. Re-load and verify before reuse."}
        write_json(output / "result.json", result)
        return result
    finally:
        for name in [*names, registry]:
            subprocess.run(["docker", "rm", "-f", "-v", name], capture_output=True, timeout=30)
        for volume in volumes:
            subprocess.run(["docker", "volume", "rm", volume], capture_output=True, timeout=30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--output-dir", default="dist/source-canary")
    args = parser.parse_args()
    print(json.dumps(run(args.source_head, args.workflow_run_id, Path(args.output_dir).resolve()), sort_keys=True))

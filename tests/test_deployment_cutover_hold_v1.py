import copy
import json
import pathlib
import tempfile
import unittest

from athena_mcp.deployment import activation_plan
from athena_mcp.deployment_cutover import (
    CUTOVER_HOLD_VERSION,
    QUIESCENCE_OBSERVATION_VERSION,
    assess_single_writer_quiescence,
    compile_cutover_hold,
    validate_canary_witness,
    verify_cutover_hold,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "deployment" / "canary-witness.v3.3.0.json"
IMAGE = (
    "ghcr.io/demeet2k/athena-mcp-server@sha256:"
    "d7eada158c5f202dd7a061218188d0c00b7317c867bedc742857a7b90298d8be"
)
SOURCE = "11211341adf599ae78784cce4ded39f21ee71ef7"
CURRENT_IMAGE = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "b" * 64
STALE_IMAGE = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "c" * 64
SNAPSHOT_REF = "snapshot-ref://production/pre-cutover-20260809"
SNAPSHOT_DIGEST = "sha256:" + "d" * 64
AUTHORITY_REF = "authority-ref://production/cutover-hold-20260809"


def load_canary() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def make_plan() -> dict:
    return activation_plan(
        IMAGE,
        source_head=SOURCE,
        state_snapshot_ref=SNAPSHOT_REF,
        state_snapshot_digest=SNAPSHOT_DIGEST,
        token_secret_ref="secret-ref://athena/production/http-token",
        release_attestation_ref="release-ref://v3.3.0/release-attestation.json",
        sbom_ref="release-ref://v3.3.0/application-sbom.spdx.json",
        expected_current_image_ref=CURRENT_IMAGE,
        actor="ATHENA_CUTOVER_HOLD_COMPILER",
    )


def make_quiescence(current_image: str = CURRENT_IMAGE) -> dict:
    return {
        "schema": QUIESCENCE_OBSERVATION_VERSION,
        "observed_current_image_ref": current_image,
        "active_writer_count": 0,
        "previous_writer_stopped": True,
        "candidate_writer_started": False,
        "write_fence_active": True,
        "write_fence_ref": "write-fence-ref://production/20260809T100000Z",
        "snapshot_after_write_fence": True,
        "state_snapshot_verified": True,
        "state_snapshot_ref": SNAPSHOT_REF,
        "state_snapshot_digest": SNAPSHOT_DIGEST,
        "observer_ref": "observer-ref://external/single-writer-quiescence-1",
        "observed_at": "2026-08-09T10:00:00Z",
    }


class DeploymentCutoverHoldPureTests(unittest.TestCase):
    def test_real_v330_canary_witness_is_checksum_valid_and_hold_compatible(self):
        canary = load_canary()
        validation = validate_canary_witness(
            canary,
            expected_image_ref=IMAGE,
            expected_source_head=SOURCE,
        )
        self.assertEqual(validation["status"], "PASS", validation)
        self.assertEqual(validation["failed_checks"], [])
        self.assertEqual(
            validation["witness_digest"],
            "sha256:53b4236273a6db8d1c80335ba07f3e8927a47d5596ae5bd1efcee9dc145bac87",
        )

        plan = make_plan()
        packet = compile_cutover_hold(
            plan,
            canary,
            make_quiescence(),
            cutover_authority_ref=AUTHORITY_REF,
        )
        self.assertEqual(packet["version"], CUTOVER_HOLD_VERSION)
        self.assertEqual(packet["status"], "CUTOVER_HOLD", packet)
        self.assertEqual(packet["decision"], "BOUND_AT_CUTOVER_HOLD")
        self.assertTrue(packet["binding_complete"])
        self.assertEqual(packet["hold_reasons"], [])
        self.assertTrue(packet["cas"]["current_image_match"])
        self.assertTrue(packet["cas"]["state_snapshot_ref_match"])
        self.assertTrue(packet["cas"]["state_snapshot_digest_match"])
        self.assertFalse(packet["cutover_authority"]["independently_verified"])
        self.assertFalse(packet["cutover_authority"]["authorizes_this_packet"])
        self.assertFalse(any(packet["execution_authority"].values()))
        self.assertFalse(packet["next_transition"]["allowed_by_this_packet"])
        self.assertNotIn("secret-ref://athena/production/http-token", json.dumps(packet))

        replay = verify_cutover_hold(
            packet,
            expected_plan_digest=plan["plan_digest"],
            expected_image_ref=IMAGE,
            expected_source_head=SOURCE,
            expected_current_image_ref=CURRENT_IMAGE,
            expected_state_snapshot_ref=SNAPSHOT_REF,
            expected_state_snapshot_digest=SNAPSHOT_DIGEST,
            expected_canary_witness_digest=canary["witness_digest"],
            expected_quiescence_assessment_digest=packet["evidence"][
                "quiescence_assessment_digest"
            ],
            expected_cutover_authority_ref=AUTHORITY_REF,
        )
        self.assertTrue(replay["verified"], replay)
        self.assertEqual(replay["failed_checks"], [])

    def test_stale_or_missing_current_image_fails_closed(self):
        stale = compile_cutover_hold(
            make_plan(),
            load_canary(),
            make_quiescence(STALE_IMAGE),
            cutover_authority_ref=AUTHORITY_REF,
        )
        self.assertEqual(stale["status"], "HOLD")
        self.assertIn("HOLD_STALE_ACTIVATION_BASE", stale["hold_reasons"])
        self.assertFalse(stale["binding_complete"])

        missing_observation = make_quiescence()
        missing_observation.pop("observed_current_image_ref")
        missing = compile_cutover_hold(
            make_plan(),
            load_canary(),
            missing_observation,
            cutover_authority_ref=AUTHORITY_REF,
        )
        self.assertIn(
            "HOLD_MISSING_CURRENT_IMAGE_OBSERVATION", missing["hold_reasons"]
        )

    def test_writer_fence_snapshot_and_authority_are_independent_holds(self):
        active = make_quiescence()
        active["active_writer_count"] = 1
        active["previous_writer_stopped"] = False
        active["write_fence_active"] = False
        active["snapshot_after_write_fence"] = False
        held = compile_cutover_hold(
            make_plan(),
            load_canary(),
            active,
            cutover_authority_ref=AUTHORITY_REF,
        )
        self.assertIn("HOLD_SINGLE_WRITER_NOT_QUIESCENT", held["hold_reasons"])

        no_authority = compile_cutover_hold(
            make_plan(), load_canary(), make_quiescence()
        )
        self.assertIn(
            "HOLD_MISSING_CUTOVER_AUTHORITY_REFERENCE",
            no_authority["hold_reasons"],
        )
        self.assertFalse(no_authority["cutover_authority"]["reference_bound"])

    def test_canary_or_packet_tamper_is_detected(self):
        canary = load_canary()
        canary["workflow_run_id"] = "tampered"
        held = compile_cutover_hold(
            make_plan(),
            canary,
            make_quiescence(),
            cutover_authority_ref=AUTHORITY_REF,
        )
        self.assertIn("HOLD_CANARY_WITNESS_INVALID", held["hold_reasons"])

        plan = make_plan()
        canary = load_canary()
        packet = compile_cutover_hold(
            plan,
            canary,
            make_quiescence(),
            cutover_authority_ref=AUTHORITY_REF,
        )
        tampered = copy.deepcopy(packet)
        tampered["target"]["source_head"] = "0" * 40
        replay = verify_cutover_hold(
            tampered,
            expected_plan_digest=plan["plan_digest"],
            expected_image_ref=IMAGE,
            expected_source_head=SOURCE,
            expected_current_image_ref=CURRENT_IMAGE,
            expected_state_snapshot_ref=SNAPSHOT_REF,
            expected_state_snapshot_digest=SNAPSHOT_DIGEST,
            expected_canary_witness_digest=canary["witness_digest"],
            expected_quiescence_assessment_digest=packet["evidence"][
                "quiescence_assessment_digest"
            ],
            expected_cutover_authority_ref=AUTHORITY_REF,
        )
        self.assertFalse(replay["verified"])
        self.assertIn("packet_digest", replay["failed_checks"])
        self.assertIn("source_head", replay["failed_checks"])

    def test_quiescence_assessment_never_claims_effectful_observation(self):
        result = assess_single_writer_quiescence(
            make_quiescence(),
            expected_current_image_ref=CURRENT_IMAGE,
            expected_state_snapshot_ref=SNAPSHOT_REF,
            expected_state_snapshot_digest=SNAPSHOT_DIGEST,
        )
        self.assertEqual(result["decision"], "QUIESCENT")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("did not stop a writer", result["boundary"])

    def test_new_cutover_organ_contains_no_effect_adapter(self):
        paths = [
            ROOT / "athena_mcp" / "deployment_cutover.py",
            ROOT / "athena_mcp" / "deployment_cutover_protocol.py",
            ROOT / "athena_mcp" / "deployment_cutover_extension.py",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        for forbidden in (
            "kubectl apply",
            "helm upgrade",
            "terraform apply",
            "docker service update",
            "gh release upload",
            "subprocess.run",
            "urlopen(",
            "requests.",
        ):
            self.assertNotIn(forbidden, text)


class DeploymentCutoverHoldRuntimeIntegrationTests(unittest.TestCase):
    def setUp(self):
        from athena_mcp.server import Server

        self.temp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.temp.name)

    def tearDown(self):
        self.server.store.close()
        self.temp.close()

    def test_tools_resource_prompt_manifest_and_benchmark_are_live(self):
        tools = {
            item["name"]
            for item in self.server.handle(
                {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
            )["result"]["tools"]
        }
        expected = {
            "athena_deployment_assess_quiescence",
            "athena_deployment_cutover_hold",
            "athena_deployment_verify_cutover_hold",
        }
        self.assertTrue(expected <= tools)

        resources = {
            item["uri"]
            for item in self.server.handle(
                {"jsonrpc": "2.0", "id": 2, "method": "resources/list"}
            )["result"]["resources"]
        }
        self.assertIn("athena://deployment/cutover-hold", resources)
        resource = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/read",
                "params": {"uri": "athena://deployment/cutover-hold"},
            }
        )["result"]["contents"][0]["text"]
        self.assertIn(CUTOVER_HOLD_VERSION, resource)
        self.assertIn("CUTOVER_HOLD != SINGLE_WRITER_CUTOVER", resource)

        prompt = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "prompts/get",
                "params": {
                    "name": "athena_deployment_cutover_hold",
                    "arguments": {"objective": "bind the post-canary hold packet"},
                },
            }
        )["result"]["messages"][0]["content"]["text"]
        self.assertIn("STOP AT CUTOVER_HOLD", prompt)
        self.assertIn("UNKNOWN to PASS", prompt)

        manifest = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {"uri": "athena://manifest"},
            }
        )["result"]["contents"][0]["text"]
        self.assertIn("DEPLOYMENT_CUTOVER_HOLD_V1", manifest)
        self.assertIn("deployment_cutover_hold", manifest)

        call = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "athena_deployment_assess_quiescence",
                    "arguments": {
                        "observation": make_quiescence(),
                        "expected_current_image_ref": CURRENT_IMAGE,
                        "expected_state_snapshot_ref": SNAPSHOT_REF,
                        "expected_state_snapshot_digest": SNAPSHOT_DIGEST,
                    },
                },
            }
        )["result"]
        self.assertFalse(call["isError"], call)
        self.assertEqual(call["structuredContent"]["status"], "PASS")

        benchmark = self.server.call_tool("athena_benchmark", {})
        self.assertEqual(benchmark["cutover_hold_version"], CUTOVER_HOLD_VERSION)
        self.assertTrue(benchmark["cutover_execution_external"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest

from athena_mcp import omega29_operate as omega
from athena_mcp.server import Server

H = hashlib.sha256(b"target").hexdigest()
E = hashlib.sha256(b"evidence").hexdigest()
P = hashlib.sha256(b"prompt-stack").hexdigest()
S = hashlib.sha256(b"source-snapshot").hexdigest()
A = "40c3a2fa43f4cc971c0a7bfb8b22794710c62707"
R = "efde1186d305113b8f05863f0a509fc53ac8a2ac"
RUN = "RMO24-V17-RUNTIME-CANDIDATE"
INV = "INV-V17-RUNTIME-TEST"


def binding(*, athena_head=A, runtime_head=R):
    body = {
        "schema": omega.BINDING_SCHEMA,
        "run_id": RUN,
        "invocation_id": INV,
        "athena": {
            "repository": "demeet2k/Athena", "ref": "main", "object_format": "sha1",
            "head": athena_head, "observation_id": "TEST-ATHENA-OBS",
        },
        "runtime": {
            "repository": "demeet2k/athena-mcp-server", "ref": "master", "object_format": "sha1",
            "head": runtime_head, "observation_id": "TEST-RUNTIME-OBS",
        },
        "source_snapshot_digest": S,
        "prompt_stack_digest": P,
        "standing": "EXACT_EXTERNAL_READBACK_INPUT_UNVERIFIED_BY_REDUCER",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD",
        "external_effects": 0,
    }
    result = {**body, "binding_digest": omega.digest(body)}
    omega.validate_source_binding(result)
    return result


def context(b=None, *, now=110):
    b = b or binding()
    body = {
        "schema": omega.RUNTIME_CONTEXT_SCHEMA,
        "run_id": b["run_id"], "invocation_id": b["invocation_id"],
        "now": now, "clock_domain": "UTC_UNIX_SECONDS",
        "clock_observation_id": f"TEST-CLOCK-{now}",
        "source_binding_digest": b["binding_digest"],
        "standing": "CALLER_SUPPLIED_RUNTIME_OBSERVATION_UNVERIFIED_BY_REDUCER",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD",
        "external_effects": 0,
    }
    return {**body, "context_digest": omega.digest(body)}


def packet(b=None, c=None):
    b = b or binding(); c = c or context(b)
    required = ["observed-target"]
    receipt = {
        "source_binding_digest": b["binding_digest"], "object_id": "Q121",
        "plan_version": "P1", "target_digest": H,
        "required_postcondition_spec_digest": omega.digest(required),
        "result_digest": H,
        "postconditions": [{"id": "observed-target", "passed": True, "evidence_digest": E}],
    }
    return {
        "schema": omega.INPUT_SCHEMA, "run_id": RUN, "invocation_id": INV,
        "source_binding_digest": b["binding_digest"], "runtime_context_digest": c["context_digest"],
        "source_heads": {"athena": b["athena"]["head"], "runtime": b["runtime"]["head"]},
        "plan_state": {"object_id": "Q121", "version": "P1", "target_digest": H,
                       "required_postcondition_ids": required, "completion_requested": True},
        "execution_state": {"object_id": "Q121", "plan_version": "P1", "result_digest": H,
                            "receipt_sha256": omega.digest(receipt), "exit_code": 0, "retryable": False},
        "world_state": {"object_id": "Q121", "observed_digest": H, "observed_at": 100,
                        "max_age_seconds": 60},
        "receipt": receipt,
        "health": {"status": "HEALTHY", "unresolved_incidents": []},
        "retry": {"count": 0, "limit": 3},
        "capabilities": {"retry": True, "rebind": True, "repair": True,
                         "rollback": False, "replan": True, "escalate": True},
        "mata_guide": {"guide_id": "G1", "directive": "VERIFY", "standing": "EVIDENCE_ONLY"},
    }


def decide(b=None, c=None, p=None):
    b = b or binding(); c = c or context(b); p = p or packet(b, c)
    return omega.decide(p, source_binding=b, runtime_context=c)


class Omega29OperateV2Tests(unittest.TestCase):
    def test_binding_relative_complete_has_explicit_claim_ceiling(self):
        result = decide()
        self.assertEqual(result["transition"], "COMPLETE")
        self.assertEqual(result["source_freshness_claim"], "NOT_ESTABLISHED_BY_REDUCER")
        self.assertEqual((result["authority"], result["admission"], result["promotion"], result["external_effects"]),
                         ("NONE", "UNADMITTED", "HOLD", 0))

    def test_deterministic_and_key_order_invariant(self):
        b = binding(); c = context(b); p = packet(b, c)
        reordered = dict(reversed(list(copy.deepcopy(p).items())))
        self.assertEqual(decide(b, c, p), decide(copy.deepcopy(b), copy.deepcopy(c), reordered))

    def test_source_binding_mismatch_rebinds_without_claiming_currentness(self):
        b = binding(); c = context(b); p = packet(b, c)
        p["source_heads"]["runtime"] = "a" * 40
        result = decide(b, c, p)
        self.assertEqual((result["transition"], result["incident"]), ("REBIND", "SOURCE_BINDING_MISMATCH"))
        self.assertEqual(result["source_freshness_claim"], "NOT_ESTABLISHED_BY_REDUCER")

    def test_stale_world_observation_uses_caller_context_clock(self):
        b = binding(); c = context(b, now=171); p = packet(b, c)
        self.assertEqual((decide(b, c, p)["transition"], decide(b, c, p)["incident"]),
                         ("REBIND", "OBSERVATION_STALE"))

    def test_packet_controlled_clock_is_rejected(self):
        b = binding(); c = context(b); p = packet(b, c); p["world_state"]["now"] = 1
        with self.assertRaises(omega.OperateRejected): decide(b, c, p)

    def test_rehashed_authority_expansion_is_rejected(self):
        b = binding(); body = {k: v for k, v in b.items() if k != "binding_digest"}
        body["authority"] = "WRITER"; tampered = {**body, "binding_digest": omega.digest(body)}
        with self.assertRaises(omega.OperateRejected): omega.validate_source_binding(tampered)

    def test_nested_claim_bearing_key_is_rejected(self):
        b = binding(); c = context(b); p = packet(b, c); p["world_state"]["protected_accepted"] = True
        with self.assertRaises(omega.OperateRejected): decide(b, c, p)

    def test_receipt_replay_across_object_is_rejected(self):
        b = binding(); c = context(b); p = packet(b, c); p["plan_state"]["object_id"] = "Q999"
        with self.assertRaises(omega.OperateRejected): decide(b, c, p)

    def test_failed_postcondition_repairs_when_capability_exists(self):
        b = binding(); c = context(b); p = packet(b, c)
        p["receipt"]["postconditions"][0]["passed"] = False
        p["execution_state"]["receipt_sha256"] = omega.digest(p["receipt"])
        self.assertEqual(decide(b, c, p)["transition"], "REPAIR")

    def test_false_rebind_capability_falls_back_to_hold(self):
        b = binding(); c = context(b); p = packet(b, c)
        p["source_heads"]["runtime"] = "a" * 40; p["capabilities"]["rebind"] = False
        self.assertEqual(decide(b, c, p)["transition"], "HOLD")

    def test_rpc_round_trip_preserves_read_only_claim_ceiling(self):
        b = binding(); c = context(b); p = packet(b, c)
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            server = Server(f.name)
            response = server.handle({
                "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": "athena_omega29_operate",
                           "arguments": {"packet": p, "source_binding": b, "runtime_context": c}},
            })
            value = response["result"]["structuredContent"]
            self.assertEqual(value["transition"], "COMPLETE")
            self.assertEqual(value["claim_ceiling"], "LOCAL_CLASSIFICATION_AGAINST_CALLER_SUPPLIED_BINDING_ONLY")
            self.assertEqual(value["external_effects"], 0)
            server.store.close()


if __name__ == "__main__":
    unittest.main()

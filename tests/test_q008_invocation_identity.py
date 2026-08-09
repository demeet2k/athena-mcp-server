from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest

from athena_mcp import omega29_operate as omega
from athena_mcp.omega29_q008_bridge import BridgeRejected, bridge
from athena_mcp import q008_invocation_identity as q
from athena_mcp.server import Server

H = hashlib.sha256(b"target").hexdigest()
E = hashlib.sha256(b"evidence").hexdigest()
P = hashlib.sha256(b"prompt-stack").hexdigest()
S = hashlib.sha256(b"source-snapshot").hexdigest()
PAYLOAD = hashlib.sha256(b"q008-payload").hexdigest()
REQ = hashlib.sha256(b"provider-request").hexdigest()
OBS = hashlib.sha256(b"provider-observation").hexdigest()
A = "40c3a2fa43f4cc971c0a7bfb8b22794710c62707"
R = "efde1186d305113b8f05863f0a509fc53ac8a2ac"
RUN = "RMO24-Q008-IDENTITY-CANDIDATE"
INV = "INV-OMEGA29-SOURCE"
CONSUMER_INV = "INV-Q008-CONSUMER-0002"


def binding():
    body = {
        "schema": omega.BINDING_SCHEMA, "run_id": RUN, "invocation_id": INV,
        "athena": {"repository": "demeet2k/Athena", "ref": "main", "object_format": "sha1", "head": A, "observation_id": "TEST-ATHENA-OBS"},
        "runtime": {"repository": "demeet2k/athena-mcp-server", "ref": "master", "object_format": "sha1", "head": R, "observation_id": "TEST-RUNTIME-OBS"},
        "source_snapshot_digest": S, "prompt_stack_digest": P,
        "standing": "EXACT_EXTERNAL_READBACK_INPUT_UNVERIFIED_BY_REDUCER",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD", "external_effects": 0,
    }
    return {**body, "binding_digest": omega.digest(body)}


def context(b=None, *, now=110):
    b = b or binding()
    body = {
        "schema": omega.RUNTIME_CONTEXT_SCHEMA, "run_id": b["run_id"], "invocation_id": b["invocation_id"],
        "now": now, "clock_domain": "UTC_UNIX_SECONDS", "clock_observation_id": f"TEST-CLOCK-{now}",
        "source_binding_digest": b["binding_digest"],
        "standing": "CALLER_SUPPLIED_RUNTIME_OBSERVATION_UNVERIFIED_BY_REDUCER",
        "authority": "NONE", "admission": "UNADMITTED", "promotion": "HOLD", "external_effects": 0,
    }
    return {**body, "context_digest": omega.digest(body)}


def packet(b=None, c=None):
    b = b or binding(); c = c or context(b); required = ["observed-target"]
    receipt = {
        "source_binding_digest": b["binding_digest"], "object_id": "Q008", "plan_version": "P1",
        "target_digest": H, "required_postcondition_spec_digest": omega.digest(required), "result_digest": H,
        "postconditions": [{"id": "observed-target", "passed": True, "evidence_digest": E}],
    }
    return {
        "schema": omega.INPUT_SCHEMA, "run_id": RUN, "invocation_id": INV,
        "source_binding_digest": b["binding_digest"], "runtime_context_digest": c["context_digest"],
        "source_heads": {"athena": A, "runtime": R},
        "plan_state": {"object_id": "Q008", "version": "P1", "target_digest": H, "required_postcondition_ids": required, "completion_requested": True},
        "execution_state": {"object_id": "Q008", "plan_version": "P1", "result_digest": H, "receipt_sha256": omega.digest(receipt), "exit_code": 0, "retryable": False},
        "world_state": {"object_id": "Q008", "observed_digest": H, "observed_at": 100, "max_age_seconds": 60},
        "receipt": receipt, "health": {"status": "HEALTHY", "unresolved_incidents": []},
        "retry": {"count": 0, "limit": 3},
        "capabilities": {"retry": True, "rebind": True, "repair": True, "rollback": False, "replan": True, "escalate": True},
        "mata_guide": {"guide_id": "G1", "directive": "VERIFY", "standing": "EVIDENCE_ONLY"},
    }


def source_bridge():
    b = binding(); c = context(b); p = packet(b, c); d = omega.decide(p, source_binding=b, runtime_context=c)
    return bridge(
        omega_packet=p, source_binding=b, runtime_context=c, omega_decision=d,
        q008_terminal="READY_TO_CLOSE", terminal_attempt=True,
        cursor={"invocation_index": 1, "segment_index": 2, "checkpoint_index": 4},
        run_id=RUN, invocation_id=INV,
    )


def provider_obs():
    return {"provider": "GITHUB", "provider_operation_id": "RUN-123", "observation_id": "OBS-123", "request_digest": REQ, "observation_digest": OBS, "observed_state": "COMPLETED"}


def bundle(**overrides):
    args = {
        "bridge": source_bridge(), "consumer_invocation_id": CONSUMER_INV,
        "move": "CHECKPOINT", "event_index": 0, "event_type": "CHECKPOINT_RECORDED",
        "payload_digest": PAYLOAD, "decision": "CONTINUE", "abort_reasons": (),
        "provider_observation": provider_obs(),
    }
    args.update(overrides)
    return q.compile_transition(**args)


class Q008InvocationIdentityTests(unittest.TestCase):
    def test_bridge_is_pending_and_does_not_advance_cursor(self):
        out = source_bridge()
        self.assertEqual(out["consumption_state"], "PENDING_IDEMPOTENT_CONSUMER")
        self.assertFalse(out["consume_inside_same_invocation"])
        self.assertEqual(out["cursor"], {"invocation_index": 1, "segment_index": 2, "checkpoint_index": 4})
        self.assertEqual((out["authority"], out["admission"], out["promotion"], out["external_mutations"]), ("NONE", "UNADMITTED", "HOLD", 0))

    def test_bridge_rejects_forged_decision(self):
        b = binding(); c = context(b); p = packet(b, c); d = omega.decide(p, source_binding=b, runtime_context=c); d = dict(d); d["reason"] = "forged"
        with self.assertRaises(BridgeRejected):
            bridge(omega_packet=p, source_binding=b, runtime_context=c, omega_decision=d, q008_terminal="READY_TO_CLOSE", terminal_attempt=True, cursor={"invocation_index": 1, "segment_index": 2, "checkpoint_index": 4}, run_id=RUN, invocation_id=INV)

    def test_bridge_rejects_boolean_cursor(self):
        b = binding(); c = context(b); p = packet(b, c); d = omega.decide(p, source_binding=b, runtime_context=c)
        with self.assertRaises(BridgeRejected):
            bridge(omega_packet=p, source_binding=b, runtime_context=c, omega_decision=d, q008_terminal="READY_TO_CLOSE", terminal_attempt=True, cursor={"invocation_index": False, "segment_index": 2, "checkpoint_index": 4}, run_id=RUN, invocation_id=INV)

    def test_same_invocation_consumer_is_rejected(self):
        br = source_bridge()
        with self.assertRaises(q.Q008IdentityRejected): q.open_consumer(br, consumer_invocation_id=br["invocation_id"])

    def test_new_consumer_invocation_preserves_source_ancestry(self):
        br = source_bridge(); env = q.open_consumer(br, consumer_invocation_id=CONSUMER_INV)
        self.assertEqual(env["run_id"], br["run_id"])
        self.assertNotEqual(env["invocation_id"], br["invocation_id"])
        self.assertEqual(env["source_invocation_id"], br["invocation_id"])
        self.assertEqual(env["initial_cursor"]["invocation_index"], br["cursor"]["invocation_index"] + 1)

    def test_all_transition_surfaces_share_consumer_identity(self):
        out = bundle(abort_reasons=["NO_EFFECT"]); env = out["envelope"]
        for name in ("cursor_after", "event", "receipt", "abort_set", "provider_receipt", "closure"):
            row = out[name]
            self.assertEqual((row["run_id"], row["invocation_id"], row["operation_id"]), (env["run_id"], env["invocation_id"], env["operation_id"]), name)

    def test_cursor_checkpoint_move_is_exact_and_invocation_fixed(self):
        out = bundle()
        self.assertEqual(out["cursor_after"]["checkpoint_index"], out["cursor_before"]["checkpoint_index"] + 1)
        self.assertEqual(out["cursor_after"]["segment_index"], out["cursor_before"]["segment_index"])
        self.assertEqual(out["cursor_after"]["invocation_index"], out["cursor_before"]["invocation_index"])

    def test_cursor_cannot_regress_even_when_rehashed(self):
        out = bundle(); env = out["envelope"]; cursor = copy.deepcopy(out["cursor_after"])
        body = {k: v for k, v in cursor.items() if k != "cursor_digest"}; body["checkpoint_index"] = env["initial_cursor"]["checkpoint_index"] - 1
        cursor = {**body, "cursor_digest": q.digest(body)}
        with self.assertRaises(q.Q008IdentityRejected): q.validate_cursor(cursor, envelope=env)

    def test_cross_invocation_cursor_replay_rejected_even_when_rehashed(self):
        out = bundle(); env = out["envelope"]; cursor = copy.deepcopy(out["cursor_after"])
        body = {k: v for k, v in cursor.items() if k != "cursor_digest"}; body["invocation_id"] = "OTHER"
        cursor = {**body, "cursor_digest": q.digest(body)}
        with self.assertRaises(q.Q008IdentityRejected): q.validate_cursor(cursor, envelope=env)

    def test_cross_run_event_substitution_rejected_even_when_rehashed(self):
        out = bundle(); env = out["envelope"]; event = copy.deepcopy(out["event"])
        body = {k: v for k, v in event.items() if k != "event_digest"}; body["run_id"] = "OTHER"
        event = {**body, "event_digest": q.digest(body)}
        with self.assertRaises(q.Q008IdentityRejected): q.validate_event(event, envelope=env)

    def test_receipt_cannot_upgrade_completion_claim(self):
        out = bundle(); env = out["envelope"]; receipt = copy.deepcopy(out["receipt"])
        body = {k: v for k, v in receipt.items() if k != "receipt_digest"}; body["q008_completion_claim"] = "ESTABLISHED"
        receipt = {**body, "receipt_digest": q.digest(body)}
        with self.assertRaises(q.Q008IdentityRejected): q.validate_receipt(receipt, envelope=env)

    def test_abort_row_cross_invocation_rejected(self):
        out = bundle(abort_reasons=["A"]); env = out["envelope"]; abort_set = copy.deepcopy(out["abort_set"])
        abort_set["aborts"][0]["invocation_id"] = "OTHER"; body = {k: v for k, v in abort_set.items() if k != "abort_set_digest"}; abort_set["abort_set_digest"] = q.digest(body)
        with self.assertRaises(q.Q008IdentityRejected): q.validate_abort_set(abort_set, envelope=env)

    def test_provider_receipt_bound_to_exact_event_and_cursor(self):
        out = bundle(); pr = out["provider_receipt"]
        self.assertEqual(pr["event_digest"], out["event"]["event_digest"])
        self.assertEqual(pr["cursor_digest"], out["cursor_after"]["cursor_digest"])
        self.assertEqual(pr["provider_effect_claim"], "NOT_ESTABLISHED_BY_Q008_IDENTITY_COMPILER")

    def test_provider_event_substitution_fails_closure(self):
        out = bundle(); pr = copy.deepcopy(out["provider_receipt"])
        body = {k: v for k, v in pr.items() if k != "provider_receipt_digest"}; body["event_digest"] = "0" * 64; pr = {**body, "provider_receipt_digest": q.digest(body)}
        with self.assertRaises(q.Q008IdentityRejected): q.validate_closure(envelope=out["envelope"], cursor=out["cursor_after"], event=out["event"], receipt=out["receipt"], abort_set=out["abort_set"], provider_receipt=pr)

    def test_boolean_external_mutation_is_not_integer_zero(self):
        out = bundle(); env = out["envelope"]; receipt = copy.deepcopy(out["receipt"])
        body = {k: v for k, v in receipt.items() if k != "receipt_digest"}; body["external_mutations"] = False; receipt = {**body, "receipt_digest": q.digest(body)}
        with self.assertRaises(q.Q008IdentityRejected): q.validate_receipt(receipt, envelope=env)

    def test_identity_closure_explicitly_does_not_claim_execution(self):
        closure = bundle()["closure"]
        self.assertTrue(closure["identity_closed"])
        self.assertEqual(closure["q008_execution_claim"], "NOT_ESTABLISHED")
        self.assertEqual(closure["provider_effect_claim"], "NOT_ESTABLISHED")
        self.assertEqual((closure["authority"], closure["admission"], closure["promotion"], closure["external_mutations"]), ("NONE", "UNADMITTED", "HOLD", 0))

    def test_same_inputs_are_deterministic(self):
        self.assertEqual(bundle(), bundle())

    def test_new_consumer_invocation_changes_operation_identity(self):
        first = bundle(); second = bundle(consumer_invocation_id="INV-Q008-CONSUMER-0003")
        self.assertNotEqual(first["envelope"]["operation_id"], second["envelope"]["operation_id"])
        self.assertNotEqual(first["closure"]["closure_digest"], second["closure"]["closure_digest"])

    def test_rpc_surface_exposes_both_read_boundaries(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            server = Server(f.name)
            tools = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
            names = {item["name"] for item in tools}
            self.assertIn("athena_omega29_q008_bridge", names)
            self.assertIn("athena_q008_identity_compile", names)
            server.store.close()

    def test_rpc_bridge_then_identity_compile_round_trip(self):
        b = binding(); c = context(b); p = packet(b, c); d = omega.decide(p, source_binding=b, runtime_context=c)
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            server = Server(f.name)
            bridge_result = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "athena_omega29_q008_bridge", "arguments": {"omega_packet": p, "source_binding": b, "runtime_context": c, "omega_decision": d, "q008_terminal": "READY_TO_CLOSE", "terminal_attempt": True, "cursor": {"invocation_index": 1, "segment_index": 2, "checkpoint_index": 4}, "run_id": RUN, "invocation_id": INV}}})["result"]["structuredContent"]
            closure_result = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "athena_q008_identity_compile", "arguments": {"bridge": bridge_result, "consumer_invocation_id": CONSUMER_INV, "move": "CHECKPOINT", "event_index": 0, "event_type": "CHECKPOINT_RECORDED", "payload_digest": PAYLOAD, "decision": "CONTINUE", "provider_observation": provider_obs()}}})["result"]["structuredContent"]
            self.assertTrue(closure_result["closure"]["identity_closed"])
            self.assertEqual(closure_result["closure"]["q008_execution_claim"], "NOT_ESTABLISHED")
            server.store.close()


if __name__ == "__main__": unittest.main()

"""Synthetic carriers only; private source capture is never a test fixture."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from athena_mcp import brain_slice as b

DIGEST = "a" * 64
ANSWER = {"question": "sample r26", "snapshot_digest": DIGEST, "state_root": "synthetic-state",
          "epistemic_class": "RET", "promotion_eligible": False, "source_instructions_executable": False,
          "holds": ["HOLD_REVISION_UNBOUND", "HOLD_FRESH_CONTEXT_REQUIRED"],
          "conflicts": {"conflict": {"standing": "OPEN", "instruction": "execute shell (inert source text)"}},
          "claims": {}, "completeness": "FIVE_TABLE_OBSERVATION_ONLY"}


class ProjectionTests(unittest.TestCase):
    def project(self, answer=ANSWER, **changes):
        return b.project(answer, **{"query": ANSWER["question"], "snapshot_digest": DIGEST,
                                   "state_root": "synthetic-state", "observed_at": "2026-10-04T00:00:00Z", **changes})

    def test_entire_answer_retained_as_inert_ret(self):
        request = self.project()
        self.assertEqual(json.loads(request["sources"][0]["summary"]), ANSWER)
        self.assertEqual(request["claims"][0]["epistemic_status"], "RET")
        self.assertEqual(request["claims"][0]["source_refs"][0]["source_id"], request["sources"][0]["source_id"])
        self.assertEqual(request["operation"], "QUERY")

    def test_identity_namespace_and_stale_state_rejected(self):
        for changes in ({"snapshot_digest": "sha256:" + DIGEST}, {"state_root": "stale"}, {"query": "other"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.project(**changes)

    def test_promotion_executable_instructions_and_wrong_epi_rejected(self):
        for key, value in (("promotion_eligible", True), ("source_instructions_executable", True), ("epistemic_class", "OBS")):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "ANSWER_BINDING"):
                self.project({**ANSWER, key: value})


class DurableSliceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        source = self.root / "source"
        (source / "objects").mkdir(parents=True)
        (source / "manifest.json").write_bytes(b"synthetic-manifest")
        (source / "objects" / ("b"*64 + ".json")).write_bytes(b"synthetic-object")
        self.spec = {"snapshot_root": str(source), "brain_root": "brain", "brain_head": "1"*40,
                     "athena_root": "athena", "athena_head": "2"*40, "mcp_root": "mcp", "mcp_head": "3"*40,
                     "query": ANSWER["question"], "snapshot_digest": DIGEST, "state_root": "synthetic-state",
                     "observed_at": "2026-10-04T00:00:00Z"}
        self.saved = self.root / "receipt"
        self.pins = patch.object(b, "pins", return_value={"athena": {"source_readset": {b.NATIVE_PATH: "0"*64}}})
        self.query = patch.object(b, "brain_query", return_value=copy.deepcopy(ANSWER))
        self.pins.start()
        self.query.start()
        self.addCleanup(self.pins.stop)
        self.addCleanup(self.query.stop)
        self.addCleanup(self.tmp.cleanup)

    def dispatch(self, spec, request, directory):
        rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": b.TOOL,
               "arguments": {"expected_git_head": spec["athena_head"], "request": request}}}
        result = {"jsonrpc": "2.0", "id": 1, "result": {"isError": False, "structuredContent": {
                  "artifact": "ATHENA.MCP.GIT_WIKI.V1", "operation": "QUERY", "git_head": spec["athena_head"],
                  "request_sha256": b.sha(b.canonical(request)), "mutation_applied": False,
                  "standing": "COMPLETE", "execution_receipt": {"artifact": "ATHENA.REPOSITORY.SKILL.EXECUTOR.RECEIPT.V1", "standing": "COMPLETE", "harness_id": b.HARNESS,
                  "input_digest": "sha256:" + b.sha(b.canonical({"wiki_request": request})),
                  "audit": [{"operation": "repository_apply", "skill_id": b.SKILL, "tool_id": b.NATIVE_TOOL,
                             "projection": ["wiki_request"], "standing": "EXECUTED_PUBLIC_JSON_UNARY", "source_sha256": "sha256:"+"0"*64}],
                  "outputs": [{"operation": "repository_apply", "skill_id": b.SKILL, "tool_id": b.NATIVE_TOOL, "result": {
                  "artifact": "ATHENA.INTERNAL.WIKI.RECEIPT.V1", "tool_id": b.NATIVE_TOOL, "version": "1.0.0",
                  "input_digest": "sha256:" + b.sha(b.canonical(request)),
                  "standing": "READY", "operation": "QUERY", "query": request["query"], "minimum_decision_cone": {
                  "sources": request["sources"], "claims": request["claims"]}}}]}}}}
        result["result"]["content"] = [{"type": "text", "text": json.dumps(result["result"]["structuredContent"])}]
        return rpc, result

    def produce(self):
        with patch.object(b, "dispatch", side_effect=self.dispatch) as handler:
            result = b.run(self.spec, self.saved)
            self.assertEqual(handler.call_count, 1)
            return result

    def rebuild(self, produced):
        return b.reconstruct(self.saved, expected_task_sha256=produced["task_sha256"],
                             expected_receipt_sha256=produced["receipt_sha256"])

    def test_replay_reconstructs_and_never_calls_handler(self):
        produced = self.produce()
        with patch.object(b, "dispatch", side_effect=AssertionError("must not repeat effect")):
            for _ in range(2):
                rebuilt = self.rebuild(produced)
                self.assertEqual(rebuilt["handler_calls"], 0)
                self.assertEqual(rebuilt["source_holds"], ANSWER["holds"])
        self.assertIsNone(json.loads((self.saved / "task.json").read_bytes())["mcp_snapshot_id"])

    def test_recomputed_outer_receipt_hash_cannot_override_trusted_anchor(self):
        produced = self.produce()
        receipt = json.loads((self.saved / "receipt.json").read_bytes())
        result = json.loads((self.saved / "rpc-result.json").read_bytes())
        result["result"]["structuredContent"]["execution_receipt"]["outputs"] = []
        raw = b.canonical(result)
        (self.saved / "rpc-result.json").write_bytes(raw)
        receipt["result_sha256"] = b.sha(raw)
        (self.saved / "receipt.json").write_bytes(b.canonical(receipt))
        with self.assertRaisesRegex(ValueError, "RECEIPT_TAMPER"):
            self.rebuild(produced)

    def test_task_namespace_swap_cannot_override_task_anchor(self):
        produced = self.produce()
        task = json.loads((self.saved / "task.json").read_bytes())
        task["mcp_snapshot_id"] = DIGEST
        (self.saved / "task.json").write_bytes(b.canonical(task))
        with self.assertRaisesRegex(ValueError, "TASK_TAMPER"):
            self.rebuild(produced)

    def test_source_tamper_or_missing_source_blocks_cold_consumer(self):
        produced = self.produce()
        manifest = self.saved / "snapshot" / "manifest.json"
        manifest.write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError, "SOURCE_TAMPER"):
            self.rebuild(produced)
        manifest.unlink()
        with self.assertRaises(OSError):
            self.rebuild(produced)

    def test_code_drift_blocks_before_any_handler(self):
        produced = self.produce()
        with patch.object(b, "pins", return_value={"new_code": True}), self.assertRaisesRegex(ValueError, "CODE_DRIFT"):
            self.rebuild(produced)

    def test_code_drift_between_prepare_and_invoke_prevents_handler(self):
        with patch.object(b, "pins", side_effect=[{"old": True}, {"new": True}]), patch.object(b, "dispatch") as call:
            with self.assertRaisesRegex(ValueError, "CODE_DRIFT"):
                b.run(self.spec, self.saved)
            call.assert_not_called()

    def test_native_receipt_must_retain_the_exact_ret_carrier(self):
        request = b.project(ANSWER, **{k: self.spec[k] for k in ("query", "snapshot_digest", "state_root", "observed_at")})
        _, result = self.dispatch(self.spec, request, self.saved)
        task = {"spec": self.spec, "request": request, "code": b.pins(self.spec)}
        for change in ("summary", "epistemic_status"):
            altered = copy.deepcopy(result)
            cone = altered["result"]["structuredContent"]["execution_receipt"]["outputs"][0]["result"]["minimum_decision_cone"]
            if change == "summary":
                cone["sources"][0]["summary"] = "dropped inner holds"
            else:
                cone["claims"][0]["epistemic_status"] = "OBS"
            altered["result"]["content"][0]["text"] = json.dumps(altered["result"]["structuredContent"])
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "NATIVE_CARRIER"):
                b.verify_result(task, altered)

    def test_rehashed_outer_records_still_require_exact_inner_routing(self):
        produced = self.produce()
        original_result = (self.saved / "rpc-result.json").read_bytes()
        original_request = (self.saved / "rpc-request.json").read_bytes()
        original_receipt = (self.saved / "receipt.json").read_bytes()
        for alteration in ("claim", "harness", "rpc", "holds"):
            with self.subTest(alteration=alteration):
                (self.saved / "rpc-result.json").write_bytes(original_result)
                (self.saved / "rpc-request.json").write_bytes(original_request)
                receipt = json.loads(original_receipt)
                result = json.loads(original_result)
                if alteration == "claim":
                    result["result"]["structuredContent"]["execution_receipt"]["outputs"][0]["result"]["minimum_decision_cone"]["claims"][0]["statement"] = "forged claim"
                elif alteration == "harness":
                    result["result"]["structuredContent"]["execution_receipt"]["harness_id"] = "FOREIGN.HARNESS"
                elif alteration == "rpc":
                    rpc = json.loads(original_request)
                    rpc["params"]["name"] = "athena_wiki_git_ingest"
                    (self.saved / "rpc-request.json").write_bytes(b.canonical(rpc))
                else:
                    receipt["source_holds"] = []
                result["result"]["content"][0]["text"] = json.dumps(result["result"]["structuredContent"])
                (self.saved / "rpc-result.json").write_bytes(b.canonical(result))
                receipt["result_sha256"] = b.sha((self.saved / "rpc-result.json").read_bytes())
                receipt["rpc_request_sha256"] = b.sha((self.saved / "rpc-request.json").read_bytes())
                raw = b.canonical(receipt)
                (self.saved / "receipt.json").write_bytes(raw)
                # Recompute even the operator's outer hash to isolate semantic
                # route validation from the independently required hash anchor.
                with self.assertRaises(ValueError):
                    self.rebuild({**produced, "receipt_sha256": b.sha(raw)})

    def test_pending_digest_and_task_flags_are_checked_independently(self):
        produced = self.produce()
        (self.saved / "PENDING").write_bytes(b"0"*64)
        with self.assertRaisesRegex(ValueError, "PENDING_BINDING"):
            self.rebuild(produced)
        task = json.loads((self.saved / "task.json").read_bytes())
        task["promotion_eligible"] = True
        raw = b.canonical(task)
        (self.saved / "task.json").write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "TASK_NAMESPACE"):
            self.rebuild({**produced, "task_sha256": b.sha(raw)})

    def test_dependency_edges_and_foreign_calls_rejected_before_execution(self):
        for field, value in (("dependencies", ["foreign-task"]), ("snapshot_id", DIGEST),
                             ("allowed_tool", "athena_wiki_git_ingest"), ("sources", [])):
            with self.subTest(field=field), patch.object(b, "dispatch") as call:
                with self.assertRaisesRegex(ValueError, "SPEC_SCHEMA"):
                    b.run({**self.spec, field: value}, self.saved)
                call.assert_not_called()
        self.assertFalse(self.saved.exists())

    def test_rpc_namespace_and_text_carrier_must_match_structured_result(self):
        request = b.project(ANSWER, **{k: self.spec[k] for k in ("query", "snapshot_digest", "state_root", "observed_at")})
        _, result = self.dispatch(self.spec, request, self.saved)
        task = {"spec": self.spec, "request": request, "code": b.pins(self.spec)}
        for field, value in (("jsonrpc", "foreign"), ("id", 2), ("error", {})):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "RESULT_NAMESPACE"):
                b.verify_result(task, {**result, field: value})
        altered = copy.deepcopy(result)
        altered["result"]["content"][0]["text"] = "{}"
        with self.assertRaisesRegex(ValueError, "RESULT_NAMESPACE"):
            b.verify_result(task, altered)
        for field, value in (("artifact", "FOREIGN"), ("operation", "INGEST")):
            altered = copy.deepcopy(result)
            altered["result"]["structuredContent"][field] = value
            altered["result"]["content"][0]["text"] = json.dumps(altered["result"]["structuredContent"])
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "RESULT_NAMESPACE"):
                b.verify_result(task, altered)

    def test_oversized_saved_artifact_rejected_before_json_or_hash_validation(self):
        produced = self.produce()
        (self.saved / "task.json").write_bytes(b"x" * 4_000_001)
        with self.assertRaisesRegex(ValueError, "ARTIFACT_TOO_LARGE"):
            self.rebuild(produced)

    def test_pending_crash_is_held_and_never_reexecuted(self):
        with patch.object(b, "dispatch", side_effect=RuntimeError("ambiguous crash")), self.assertRaises(RuntimeError):
            b.run(self.spec, self.saved)
        task_digest = b.sha((self.saved / "task.json").read_bytes())
        self.assertTrue((self.saved / "rpc-request.json").exists())
        with patch.object(b, "dispatch", side_effect=AssertionError("must not retry")), self.assertRaisesRegex(ValueError, "AMBIGUOUS_PENDING"):
            b.reconstruct(self.saved, expected_task_sha256=task_digest, expected_receipt_sha256="0"*64)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Dict, Mapping, Sequence


class ToolActivationError(RuntimeError):
    pass


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class CanonicalToolActivationConsumer:
    """Execute one cycle-selected MCP tool and bind its observed result back into CYCLE.1.

    The consumer deliberately reuses the public JSON-RPC ``tools/call`` path instead of
    calling implementation objects directly. Therefore ordinary schema validation,
    server dispatch and the dispatch layer's tool-specific metering policy stay on the
    same canonical path as an external MCP caller.

    This module does not grant scheduler, promotion or external-attestation authority.
    Its witnesses mean only that this process observed the call/result/test sequence.
    """

    def __init__(self, server: Any):
        self.server = server
        self._seq = 0

    def _rpc(self, method: str, params: Mapping[str, Any] | None = None) -> Dict[str, Any]:
        self._seq += 1
        message: Dict[str, Any] = {"jsonrpc": "2.0", "id": f"activation:{self._seq}", "method": method}
        if params is not None:
            message["params"] = dict(params)
        response = self.server.handle(message)
        if "error" in response:
            raise ToolActivationError(f"RPC {method} failed: {response['error']}")
        return response

    def _tool(self, name: str, arguments: Mapping[str, Any]) -> Any:
        response = self._rpc("tools/call", {"name": name, "arguments": dict(arguments)})
        result = response.get("result") or {}
        if result.get("isError"):
            content = result.get("content") or []
            detail = content[0].get("text") if content and isinstance(content[0], Mapping) else result
            raise ToolActivationError(f"tool {name} failed: {detail}")
        if "structuredContent" not in result:
            raise ToolActivationError(f"tool {name} returned no structuredContent")
        return result["structuredContent"]

    def _registered_tools(self) -> set[str]:
        response = self._rpc("tools/list")
        return {str(tool["name"]) for tool in response["result"]["tools"]}

    @staticmethod
    def _selected_target(state: Mapping[str, Any]) -> tuple[str, str]:
        try:
            selected = state["state"]["artifacts"]["aor_run"]["next"]
            return str(selected["id"]), str(selected["source"]["target_ref"])
        except (KeyError, TypeError) as exc:
            raise ToolActivationError("cycle did not expose a selected AOR candidate") from exc

    def activate(
        self,
        *,
        task_ref: str,
        seed: Any,
        candidate: Mapping[str, Any],
        tool_name: str,
        tool_arguments: Mapping[str, Any],
        workers: Sequence[Mapping[str, Any]],
        collective_signals: Mapping[str, Any] | None = None,
        verify_result: Callable[[Any], bool | Mapping[str, Any]] | None = None,
        replay_safe: bool = False,
        config: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        tool_name = str(tool_name).strip()
        if not tool_name:
            raise ValueError("tool_name must not be empty")
        if tool_name.startswith("athena_cycle_"):
            raise ValueError("cycle tools cannot recursively execute themselves through the activation consumer")

        registered = self._registered_tools()
        if tool_name not in registered:
            raise ToolActivationError(f"tool is not installed on the observed MCP surface: {tool_name}")

        candidate = dict(candidate)
        expected_target = f"tool:{tool_name}"
        if str(candidate.get("target_ref")) != expected_target:
            raise ToolActivationError(
                f"candidate/tool binding mismatch: target_ref={candidate.get('target_ref')!r} expected={expected_target!r}"
            )

        cfg = dict(config or {})
        protected = {"field_explicit_candidates", "workers", "collective_signals"}
        collision = protected & set(cfg)
        if collision:
            raise ValueError(f"config must not override activation-owned keys: {sorted(collision)}")
        cfg.update(
            {
                "field_explicit_candidates": [candidate],
                "workers": [dict(worker) for worker in workers],
                "collective_signals": dict(collective_signals or {}),
            }
        )

        start = self._tool("athena_cycle_start", {"task_ref": task_ref, "seed": seed, "config": cfg})
        cycle_id = str(start["cycle_id"])
        at_executor = self._tool("athena_cycle_advance", {"cycle_id": cycle_id, "max_steps": 64})
        if at_executor.get("status") != "WAITING_EXECUTOR" or at_executor.get("phase") != "EXECUTE":
            raise ToolActivationError(
                f"cycle did not reach executor boundary: status={at_executor.get('status')} phase={at_executor.get('phase')}"
            )
        selected_id, selected_target = self._selected_target(at_executor)
        if selected_target != expected_target:
            raise ToolActivationError(
                f"selected candidate target changed: selected={selected_target!r} expected={expected_target!r}"
            )

        arguments = dict(tool_arguments)
        arguments_digest = _digest(arguments)
        result = self._tool(tool_name, arguments)
        result_digest = _digest(result)
        execution_basis = {
            "cycle_id": cycle_id,
            "candidate_id": selected_id,
            "target_ref": selected_target,
            "tool_name": tool_name,
            "arguments_digest": arguments_digest,
            "result_digest": result_digest,
        }
        execution_ref = f"exec://canonical-tool/{_digest(execution_basis)}"
        execution_receipt = {
            "verified": True,
            "ref": execution_ref,
            "status": "COMPLETED",
            "candidate_id": selected_id,
            "target_ref": selected_target,
            "tool_name": tool_name,
            "arguments_digest": arguments_digest,
            "result_digest": result_digest,
            "result_bound": True,
            "result": result,
            "authority": "IN_PROCESS_MCP_OBSERVATION_ONLY",
        }
        at_test = self._tool(
            "athena_cycle_advance",
            {"cycle_id": cycle_id, "inputs": {"execution_receipt": execution_receipt}, "max_steps": 16},
        )
        if at_test.get("status") != "WAITING_TEST" or at_test.get("phase") != "VERIFY":
            raise ToolActivationError(
                f"cycle did not consume execution receipt into VERIFY: status={at_test.get('status')} phase={at_test.get('phase')}"
            )

        replay_digest = None
        if replay_safe:
            replay_result = self._tool(tool_name, arguments)
            replay_digest = _digest(replay_result)
            if replay_digest != result_digest:
                raise ToolActivationError(
                    f"safe replay diverged for {tool_name}: first={result_digest} replay={replay_digest}"
                )

        verification = None
        done = None
        if verify_result is not None:
            observed = verify_result(result)
            if isinstance(observed, Mapping):
                passed = bool(observed.get("passed"))
                observation = str(observed.get("observation") or observed)
                verification = dict(observed)
            else:
                passed = bool(observed)
                observation = "verification callback returned true" if passed else "verification callback returned false"
                verification = {"passed": passed, "observation": observation}
            if not passed:
                raise ToolActivationError(f"result verification failed: {observation}")
            test_basis = {
                "execution_ref": execution_ref,
                "result_digest": result_digest,
                "observation": observation,
            }
            test_packet = {
                "procedure": f"consumer verification of observed {tool_name} result",
                "observation": observation,
                "result": "pass",
                "witness": {
                    "verified": True,
                    "ref": f"test://canonical-tool/{_digest(test_basis)}",
                    "tool_name": tool_name,
                    "result_digest": result_digest,
                    "authority": "IN_PROCESS_CONSUMER_ASSERTION_NOT_EXTERNAL_CI",
                },
            }
            done = self._tool(
                "athena_cycle_advance",
                {"cycle_id": cycle_id, "inputs": {"test_packet": test_packet}, "max_steps": 32},
            )
            if done.get("status") != "COMPLETE":
                raise ToolActivationError(
                    f"cycle did not complete after witnessed test: status={done.get('status')} phase={done.get('phase')}"
                )

        usage = self.server.collective_learning.budget_summary(scope="global", limit=500)
        usage_observed = tool_name in usage.get("tool_wall_time_s", {})
        replay_reused = bool(replay_safe and replay_digest == result_digest)
        lifecycle = {
            "REGISTERED": True,
            "INSTALLED": True,
            "SELECTED": selected_target == expected_target,
            "REACHABLE": True,
            "EXECUTED": True,
            "RESULT_BOUND": at_test["state"]["artifacts"]["execution_receipt"].get("result_digest") == result_digest,
            "CONSUMED": at_test.get("phase") == "VERIFY",
            "WITNESSED": bool(done and done.get("status") == "COMPLETE"),
            "REUSED": replay_reused,
        }
        return {
            "version": "ATHENA.TOOL-ACTIVATION-CONSUMER.1",
            "cycle_id": cycle_id,
            "tool_name": tool_name,
            "selected_candidate_id": selected_id,
            "selected_target_ref": selected_target,
            "arguments_digest": arguments_digest,
            "result": result,
            "result_digest": result_digest,
            "execution_receipt": execution_receipt,
            "at_test": at_test,
            "final_cycle": done,
            "verification": verification,
            "replay_result_digest": replay_digest,
            "runtime_usage_observed": usage_observed,
            "reuse_evidence": {
                "requested": bool(replay_safe),
                "stable_result_digest": replay_reused,
                "runtime_usage_observed": usage_observed,
                "law": "REPLAY_REUSE != RUNTIME_METERING; deterministic reuse is witnessed by result identity, while metering follows the dispatch layer's independent tool-specific policy",
            },
            "lifecycle": lifecycle,
            "boundary": "local MCP execution/result/test/replay evidence only; no claim of external CI, hosted deployment, causal gain or promotion authority",
        }

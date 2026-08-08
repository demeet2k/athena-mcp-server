from __future__ import annotations

from .frontier_claim import FrontierClaimRuntime, _safe_id


def install_frontier_claim_internal_compat(runtime_cls=FrontierClaimRuntime) -> None:
    """Keep direct Python callers compatible while MCP remains deterministic.

    The public MCP schema requires operation_at and call_tool always supplies it.
    Some internal/tests call claim_prepare directly. If they omit operation_at,
    preserve the original no-write preparation semantics using the existing
    helper methods. This path is deliberately not reachable through the MCP tool
    schema and therefore does not weaken the external retry contract.
    """

    if getattr(runtime_cls, "_athena_claim_internal_compat_v1_registered", False):
        return
    deterministic = runtime_cls.claim_prepare

    def claim_prepare_compatible(
        self,
        *,
        expected_source_head: str,
        expected_frontier_digest: str,
        expected_prompt_stack_digest: str,
        expected_claim_contract_digest: str,
        run_id: str,
        node_id: str,
        operation_at: str | None = None,
        worker_role: str | None = None,
        lease_seconds: int = 900,
        **kwargs,
    ) -> dict:
        if operation_at is not None:
            return deterministic(
                self,
                expected_source_head=expected_source_head,
                expected_frontier_digest=expected_frontier_digest,
                expected_prompt_stack_digest=expected_prompt_stack_digest,
                expected_claim_contract_digest=expected_claim_contract_digest,
                run_id=run_id,
                node_id=node_id,
                operation_at=operation_at,
                worker_role=worker_role,
                lease_seconds=lease_seconds,
                **kwargs,
            )

        kwargs = dict(kwargs)
        kwargs["fetch"] = True
        packet = self.frontier.hydrate(**kwargs)
        contract = self._contract(packet["source_head"])
        expected = {
            "source_head": expected_source_head,
            "frontier_digest": expected_frontier_digest,
            "prompt_stack_digest": expected_prompt_stack_digest,
            "claim_contract_digest": expected_claim_contract_digest,
        }
        changed = self._changed(expected, packet, contract)
        if any(changed.values()):
            return {
                "status": "CLAIM_STALE_ADDRESS_HOLD",
                "changed": changed,
                "current": {
                    "source_head": packet.get("source_head"),
                    "frontier_digest": packet.get("frontier_digest"),
                    "prompt_stack_digest": packet.get("prompt_stack_digest"),
                    "claim_contract_digest": contract.get("claim_contract_digest"),
                    "remote_checked": packet.get("remote_checked"),
                },
                "law": "STALE_H_P_F_C_W -> REHYDRATE_BEFORE_PROVIDER_EFFECT",
            }
        if packet.get("status") != "HYDRATED":
            return {"status": "CLAIM_FRONTIER_HOLD", "reason": packet.get("status"), "claim_contract": contract}
        if contract.get("status") != "PASS":
            return {
                "status": "CLAIM_CONTRACT_HOLD",
                "claim_contract": contract,
                "law": "UNMERGED_OR_DRIFTED_JOURNAL_CONTRACT != EXECUTION_AUTHORITY",
            }
        safe_run = _safe_id(run_id, "run_id")
        safe_node = _safe_id(node_id, "node_id")
        claimable = next(
            (
                x for x in packet.get("claimable_work") or []
                if str(x.get("run_id")) == safe_run and str(x.get("node_id")) == safe_node
            ),
            None,
        )
        if claimable is None:
            routing = next(
                (
                    x for x in packet.get("routing_ready_work") or []
                    if str(x.get("run_id")) == safe_run and str(x.get("node_id")) == safe_node
                ),
                None,
            )
            if routing is not None:
                return {
                    "status": "EVENT_READY_REQUIRED_HOLD",
                    "run_id": safe_run,
                    "node_id": safe_node,
                    "reducer_state": routing.get("reducer_state"),
                    "readiness_prerequisite": self._readiness_event_prepare(packet, safe_run, safe_node),
                    "law": "INFERRED_READY != EVENT_READY; persist and rehydrate NODE_READY before claim preparation",
                }
            return {
                "status": "CLAIM_NODE_NOT_EVENT_READY_HOLD",
                "run_id": safe_run,
                "node_id": safe_node,
                "law": "CLAIM_PREPARE_REQUIRES_EVENT_READY",
            }
        prepared = self._claim_effect_prepare(packet, safe_run, safe_node, worker_role, lease_seconds)
        prepared["address"] = {
            "source_head": packet.get("source_head"),
            "frontier_digest": packet.get("frontier_digest"),
            "prompt_stack_digest": packet.get("prompt_stack_digest"),
            "claim_contract_digest": contract.get("claim_contract_digest"),
            "remote_checked": packet.get("remote_checked"),
        }
        prepared["claim_contract"] = contract
        prepared["compatibility_mode"] = "DIRECT_PYTHON_NONDETERMINISTIC_PREPARE"
        return prepared

    runtime_cls.claim_prepare = claim_prepare_compatible
    runtime_cls._athena_claim_internal_compat_v1_registered = True

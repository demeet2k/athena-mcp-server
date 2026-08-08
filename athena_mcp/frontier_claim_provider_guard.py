from __future__ import annotations

from .frontier_claim import FrontierClaimRuntime
from . import frontier_claim_provider as provider


def install_frontier_claim_provider_guard(runtime_cls=FrontierClaimRuntime) -> None:
    """Install execution-only antibodies around the bounded provider membrane.

    PG-001: GitHub Contents create-if-absent is accepted only on HTTP 201.
    PG-002: after a newly created claim provider effect is observed, revalidate
    the exact scheduler contract on the fresh source head before preparing
    CLAIM_ACQUIRED. Reconciliation already performs its full expected-address
    check before its only provider effect, so it requires current contract PASS
    but does not manufacture a second unavailable prepared-address coordinate.
    FBR-COMPAT: preserve the explicit `excludes source_head` digest-basis contract
    while adding routing-ready/event-ready claim coordinates.
    """

    if getattr(runtime_cls, "_athena_claim_provider_guard_v1_registered", False):
        return

    original_create = provider.GitHubContentsCreateProvider.create
    original_claim_event_prepare = provider._claim_event_prepare
    original_augment_packet = runtime_cls.augment_packet

    def create_strict(self, *, repo: str, branch: str, packet: dict) -> dict:
        result = original_create(self, repo=repo, branch=branch, packet=packet)
        if result.get("status") == "CREATED" and int(result.get("http_status") or 0) != 201:
            return {
                "status": "PROVIDER_HOLD",
                "http_status": result.get("http_status"),
                "path": result.get("path"),
                "kind": result.get("kind"),
                "reason": "create-if-absent requires HTTP 201; update-like success is not accepted",
                "law": "HTTP_200_UPDATE_SEMANTICS != CREATE_IF_ABSENT_SUCCESS",
            }
        return result

    def claim_event_prepare_guarded(runtime, packet: dict, prepared: dict) -> dict:
        contract = runtime._contract(packet["source_head"])
        expected = ((prepared.get("address") or {}).get("claim_contract_digest"))
        current = contract.get("claim_contract_digest")
        drifted_new_claim = expected is not None and current != expected
        if contract.get("status") != "PASS" or drifted_new_claim:
            return {
                "status": "CLAIM_EFFECT_UNJOURNALED_HOLD",
                "run_id": prepared.get("run_id"),
                "node_id": prepared.get("node_id"),
                "claim_path": prepared.get("claim_path"),
                "reason": "scheduler interpretation contract changed after claim creation" if expected is not None else "scheduler interpretation contract is not currently valid for reconciliation",
                "expected_claim_contract_digest": expected,
                "current_claim_contract_digest": current,
                "claim_contract": contract,
                "law": "CLAIM_CREATED + CONTRACT_DRIFT => HOLD; DO_NOT_APPEND_CLAIM_ACQUIRED",
            }
        return original_claim_event_prepare(runtime, packet, prepared)

    def augment_packet_with_explicit_clock_exclusion(self, packet: dict) -> dict:
        out = original_augment_packet(self, packet)
        basis = str(out.get("frontier_digest_basis") or "")
        if "excludes source_head" not in basis:
            suffix = "excludes source_head and nested repository clocks from frontier content identity"
            out["frontier_digest_basis"] = f"{basis}; {suffix}" if basis else suffix
        return out

    provider.GitHubContentsCreateProvider.create = create_strict
    provider._claim_event_prepare = claim_event_prepare_guarded
    runtime_cls.augment_packet = augment_packet_with_explicit_clock_exclusion
    runtime_cls._athena_claim_provider_guard_v1_registered = True

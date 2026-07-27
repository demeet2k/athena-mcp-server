"""KC144 W17 evidence-provenance and protected-dispatch decision gate.

W17 binds an external provenance claim to the exact W16 packet/evidence
adjunction.  Structural binding is not external verification: this runtime has
no provider credential, trust adapter, protected secret, network fetch, or
workflow-dispatch capability.  It can therefore construct and audit a dispatch
candidate, but it must hold the candidate until a provider-specific verifier
and the protected P10 workflow satisfy the remaining gates.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from .replay_authority_ledger import (
    FrozenReplayAuthorityLedger,
    WITNESS_PLAN,
    _assert_secret_free,
    _bounded_text,
    _digest,
    _exact_object,
    _https_url,
    _parsed_timestamp,
    _timestamp,
    _validate_activation_packet,
    _validate_provider_evidence,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "w17_evidence_provenance_gate.json"
SCHEMA = "athena.xnav-w17-evidence-provenance-dispatch-gate/v1"
PHASE = "KC144.XNAV.W17"
PROVENANCE_SCHEMA = "athena.provider-evidence-provenance/v1"
SHA256_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")

PROVENANCE_FIELDS = {
    "schema",
    "evidence_digest",
    "retrieval",
    "verifier",
    "authorization",
    "trust_anchor",
    "assertions",
    "attestation_digest",
}
RETRIEVAL_FIELDS = {
    "mode",
    "evidence_url",
    "retrieved_at",
    "content_digest",
}
VERIFIER_FIELDS = {"identity", "method", "witness_ref", "verified_at"}
AUTHORIZATION_FIELDS = {"ref", "actor", "authorized_at"}
TRUST_ANCHOR_FIELDS = {"kind", "reference", "fingerprint"}
ASSERTION_FIELDS = {
    "provider_evidence_fetched",
    "external_evidence_verified",
    "authorization_externally_verified",
    "secret_material_recorded",
}


class EvidenceProvenanceGateError(RuntimeError):
    """Raised when the frozen W17 policy or a submitted witness is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvidenceProvenanceGateError(f"{path.name} must contain an object")
    return value


def _attestation_material(witness: dict[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(value)
        for key, value in witness.items()
        if key != "attestation_digest"
    }


def provenance_attestation_digest(witness: dict[str, Any]) -> str:
    """Return the canonical digest for a provenance witness."""
    return _digest(_attestation_material(witness))


class FrozenEvidenceProvenanceGate:
    """Exact W17 provenance policy and nondispatching decision engine."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        predecessor: FrozenReplayAuthorityLedger,
    ) -> None:
        self.snapshot = snapshot
        self.predecessor = predecessor

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        predecessor: FrozenReplayAuthorityLedger | None = None,
    ) -> "FrozenEvidenceProvenanceGate":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise EvidenceProvenanceGateError("unexpected W17 schema or phase")
        predecessor = predecessor or FrozenReplayAuthorityLedger.load()
        w16 = predecessor.status()
        lineage = snapshot.get("predecessor")
        expected_lineage = {
            "repository": "demeet2k/athena-mcp-server",
            "pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w16_head": "97f7bdc917a29fe1f54192fdcd37e3704be736cd",
            "w16_schema": "athena.xnav-w16-replay-authority-ledger/v1",
            "w16_ledger_root": w16["ledger_root"],
            "w16_fixture_adjunction_digest": (
                "sha256:3d46b448882d608a3666a15fd5502aeba7e3b36f018792dabe023314bd5923b6"
            ),
            "w16_typed_replay_ledger_digest": (
                "sha256:5e95cfc3abc537b7108451c38c90cf9a4d99e39068e72c818343a4224fac2a35"
            ),
            "activation_handoff_pull_request": 11,
            "activation_handoff_head": (
                "8bc9072fe2fa9ac9b2998653c7656ae92428be4c"
            ),
            "canonical_hardening_head": (
                "b4e24de38788ecdf30f43514ece279d1270b998b"
            ),
        }
        if lineage != expected_lineage:
            raise EvidenceProvenanceGateError("W17 predecessor lineage mismatch")

        contract = snapshot.get("evidence_provenance_contract")
        expected_contract = {
            "schema": PROVENANCE_SCHEMA,
            "required_class": "EXTERNALLY_VERIFIED_PROVIDER_EVIDENCE",
            "runtime_output_class": (
                "STRUCTURALLY_BOUND_EXTERNAL_PROVENANCE_CLAIM"
            ),
            "allowed_retrieval_modes": [
                "provider-api-read",
                "provider-signed-attestation",
            ],
            "allowed_verification_methods": [
                "credentialed-provider-api",
                "provider-signature",
            ],
            "attestation_digest_algorithm": "sha256-canonical-json",
            "trust_anchor_required": True,
            "provider_specific_adapter_required": True,
            "runtime_has_provider_adapter": False,
            "runtime_fetches_provider_evidence": False,
            "runtime_verifies_external_authority": False,
            "submitted_inputs_persisted": False,
        }
        if contract != expected_contract:
            raise EvidenceProvenanceGateError("W17 provenance contract drift")

        dispatch = snapshot.get("protected_dispatch_contract")
        expected_dispatch = {
            "workflow_path": ".github/workflows/p10-host-readiness.yml",
            "workflow_ref_policy": "EXACT_CANDIDATE_HEAD_REQUIRED",
            "protected_environment": WITNESS_PLAN["environment"],
            "protected_secret_name": WITNESS_PLAN["secret_name"],
            "sample_count": WITNESS_PLAN["sample_count"],
            "interval_seconds": WITNESS_PLAN["interval_seconds"],
            "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
            "execute_live_witness_default": False,
            "required_gates": [
                "activation_packet_structurally_valid",
                "provider_evidence_structurally_valid",
                "packet_evidence_fields_match",
                "provenance_claim_structurally_valid",
                "provider_trust_anchor_verified",
                "authorization_externally_verified",
                "protected_environment_approved",
                "bearer_secret_available_at_job_runtime",
                "explicit_live_witness_dispatch",
            ],
            "runtime_dispatch_capability": "NONE",
            "runtime_can_promote": False,
            "ic10_required": True,
        }
        if dispatch != expected_dispatch:
            raise EvidenceProvenanceGateError("W17 protected dispatch drift")
        boundaries = snapshot.get("boundaries")
        expected_boundaries = {
            "live_provider_fetch_executed": False,
            "trust_anchor_verified": False,
            "authorization_externally_verified": False,
            "submitted_inputs_persisted": False,
            "secret_material_accepted": False,
            "secret_material_recorded": False,
            "endpoint_contacted": False,
            "workflow_dispatched": False,
            "persistent_witness_executed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if boundaries != expected_boundaries:
            raise EvidenceProvenanceGateError("W17 boundaries must all remain false")
        if snapshot.get("successor") != (
            "KC144.XNAV.W18::"
            "PROVIDER-ADAPTER-TRUST-ANCHOR-AND-PERSISTENT-WITNESS-RETURN"
        ):
            raise EvidenceProvenanceGateError("W17 successor drift")

        contract_material = {
            key: deepcopy(value)
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
        if snapshot.get("contract_digest") != _digest(contract_material):
            raise EvidenceProvenanceGateError("W17 contract digest mismatch")
        return cls(snapshot, predecessor)

    @classmethod
    def load(
        cls, path: Path = DATA_PATH
    ) -> "FrozenEvidenceProvenanceGate":
        return cls.from_snapshot(_load_json(path))

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "EVIDENCE_PROVENANCE_GATE_READY__"
                "PROTECTED_DISPATCH_FAIL_CLOSED"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "contract_digest": self.snapshot["contract_digest"],
            "w16_ledger_root": self.snapshot["predecessor"]["w16_ledger_root"],
            "evidence_provenance_contract": deepcopy(
                self.snapshot["evidence_provenance_contract"]
            ),
            "protected_dispatch_contract": deepcopy(
                self.snapshot["protected_dispatch_contract"]
            ),
            "cross_navigation_state": (
                "SOURCE_REPLAY_LEDGER_AND_PROVENANCE_SCHEMA_CLOSED__"
                "TRUST_ANCHOR_AND_PERSISTENT_WITNESS_OPEN"
            ),
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "successor": self.snapshot["successor"],
        }

    def build_provenance_template(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
    ) -> dict[str, Any]:
        """Build a content-bound but explicitly unresolved witness template."""
        try:
            packet, evidence = self._packet_evidence(
                activation_packet_json, provider_evidence_json
            )
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return self._rejected(str(error))
        evidence_digest = _digest(evidence)
        witness = {
            "schema": PROVENANCE_SCHEMA,
            "evidence_digest": evidence_digest,
            "retrieval": {
                "mode": "provider-api-read",
                "evidence_url": evidence["evidence_url"],
                "retrieved_at": None,
                "content_digest": evidence_digest,
            },
            "verifier": {
                "identity": None,
                "method": "credentialed-provider-api",
                "witness_ref": None,
                "verified_at": None,
            },
            "authorization": deepcopy(packet["authorization"]),
            "trust_anchor": {
                "kind": None,
                "reference": None,
                "fingerprint": None,
            },
            "assertions": {
                "provider_evidence_fetched": False,
                "external_evidence_verified": False,
                "authorization_externally_verified": False,
                "secret_material_recorded": False,
            },
            "attestation_digest": None,
        }
        return {
            "status": "UNRESOLVED_EXTERNAL_PROVENANCE_WITNESS_TEMPLATE",
            "template": witness,
            "activation_packet_digest": _digest(packet),
            "provider_evidence_digest": evidence_digest,
            "submitted_inputs_persisted": False,
            "provider_evidence_fetched": False,
            "external_evidence_verified": False,
            "dispatch_allowed": False,
        }

    def _packet_evidence(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if (
            not isinstance(activation_packet_json, str)
            or not isinstance(provider_evidence_json, str)
            or len(activation_packet_json) > 32768
            or len(provider_evidence_json) > 32768
        ):
            raise ValueError("packet and evidence must be bounded JSON strings")
        packet = _validate_activation_packet(json.loads(activation_packet_json))
        evidence = _validate_provider_evidence(
            json.loads(provider_evidence_json), packet
        )
        return packet, evidence

    def _validate_provenance(
        self,
        value: Any,
        packet: dict[str, Any],
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        _assert_secret_free(value, "provenance_witness")
        witness = _exact_object(value, PROVENANCE_FIELDS, "provenance witness")
        if witness.get("schema") != PROVENANCE_SCHEMA:
            raise ValueError(f"provenance schema must be {PROVENANCE_SCHEMA}")
        evidence_digest = _bounded_text(
            witness.get("evidence_digest"), "evidence_digest"
        )
        if evidence_digest != _digest(evidence):
            raise ValueError("provenance witness does not bind exact provider evidence")

        contract = self.snapshot["evidence_provenance_contract"]
        retrieval = _exact_object(
            witness.get("retrieval"), RETRIEVAL_FIELDS, "retrieval"
        )
        mode = _bounded_text(retrieval.get("mode"), "retrieval.mode")
        if mode not in contract["allowed_retrieval_modes"]:
            raise ValueError("retrieval.mode is not admitted")
        normalized_retrieval = {
            "mode": mode,
            "evidence_url": _https_url(
                retrieval.get("evidence_url"), "retrieval.evidence_url"
            ),
            "retrieved_at": _timestamp(
                retrieval.get("retrieved_at"), "retrieval.retrieved_at"
            ),
            "content_digest": _bounded_text(
                retrieval.get("content_digest"), "retrieval.content_digest"
            ),
        }
        if (
            normalized_retrieval["evidence_url"] != evidence["evidence_url"]
            or normalized_retrieval["content_digest"] != evidence_digest
        ):
            raise ValueError("retrieval does not bind evidence URL and content")

        verifier = _exact_object(
            witness.get("verifier"), VERIFIER_FIELDS, "verifier"
        )
        method = _bounded_text(verifier.get("method"), "verifier.method")
        if method not in contract["allowed_verification_methods"]:
            raise ValueError("verifier.method is not admitted")
        normalized_verifier = {
            "identity": _bounded_text(
                verifier.get("identity"), "verifier.identity"
            ),
            "method": method,
            "witness_ref": _https_url(
                verifier.get("witness_ref"), "verifier.witness_ref"
            ),
            "verified_at": _timestamp(
                verifier.get("verified_at"), "verifier.verified_at"
            ),
        }

        authorization = _exact_object(
            witness.get("authorization"),
            AUTHORIZATION_FIELDS,
            "authorization",
        )
        normalized_authorization = {
            "ref": _bounded_text(authorization.get("ref"), "authorization.ref"),
            "actor": _bounded_text(
                authorization.get("actor"), "authorization.actor"
            ),
            "authorized_at": _timestamp(
                authorization.get("authorized_at"),
                "authorization.authorized_at",
            ),
        }
        if normalized_authorization != packet["authorization"]:
            raise ValueError("provenance authorization does not match packet")

        trust = _exact_object(
            witness.get("trust_anchor"), TRUST_ANCHOR_FIELDS, "trust_anchor"
        )
        normalized_trust = {
            "kind": _bounded_text(trust.get("kind"), "trust_anchor.kind"),
            "reference": _https_url(
                trust.get("reference"), "trust_anchor.reference"
            ),
            "fingerprint": _bounded_text(
                trust.get("fingerprint"), "trust_anchor.fingerprint"
            ),
        }
        if not SHA256_VALUE.fullmatch(normalized_trust["fingerprint"]):
            raise ValueError("trust_anchor.fingerprint must be sha256:<64 hex>")

        assertions = _exact_object(
            witness.get("assertions"), ASSERTION_FIELDS, "assertions"
        )
        expected_assertions = {
            "provider_evidence_fetched": True,
            "external_evidence_verified": True,
            "authorization_externally_verified": True,
            "secret_material_recorded": False,
        }
        if assertions != expected_assertions:
            raise ValueError("provenance assertions must describe a complete witness")

        deployment_at = _parsed_timestamp(evidence["deployment_observed_at"])
        authorization_at = _parsed_timestamp(
            normalized_authorization["authorized_at"]
        )
        retrieved_at = _parsed_timestamp(normalized_retrieval["retrieved_at"])
        verified_at = _parsed_timestamp(normalized_verifier["verified_at"])
        if not authorization_at <= deployment_at <= retrieved_at <= verified_at:
            raise ValueError("provenance timestamps are not causally ordered")

        normalized = {
            "schema": PROVENANCE_SCHEMA,
            "evidence_digest": evidence_digest,
            "retrieval": normalized_retrieval,
            "verifier": normalized_verifier,
            "authorization": normalized_authorization,
            "trust_anchor": normalized_trust,
            "assertions": expected_assertions,
            "attestation_digest": _bounded_text(
                witness.get("attestation_digest"), "attestation_digest"
            ),
        }
        if normalized["attestation_digest"] != provenance_attestation_digest(
            normalized
        ):
            raise ValueError("provenance attestation digest mismatch")
        return normalized

    def inspect_provenance(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> dict[str, Any]:
        try:
            if (
                not isinstance(provenance_witness_json, str)
                or len(provenance_witness_json) > 32768
            ):
                raise ValueError("provenance witness must be bounded JSON text")
            packet, evidence = self._packet_evidence(
                activation_packet_json, provider_evidence_json
            )
            provenance = self._validate_provenance(
                json.loads(provenance_witness_json), packet, evidence
            )
            packet_digest = _digest(packet)
            evidence_digest = _digest(evidence)
            provenance_digest = _digest(provenance)
            binding_digest = _digest(
                {
                    "schema": SCHEMA,
                    "phase": PHASE,
                    "activation_packet_digest": packet_digest,
                    "provider_evidence_digest": evidence_digest,
                    "provenance_witness_digest": provenance_digest,
                    "contract_digest": self.snapshot["contract_digest"],
                    "classification": (
                        "STRUCTURALLY_BOUND_EXTERNAL_PROVENANCE_CLAIM"
                    ),
                }
            )
            return {
                "status": (
                    "PASS_STRUCTURAL_EVIDENCE_PROVENANCE_BINDING__"
                    "TRUST_ANCHOR_UNVERIFIED"
                ),
                "activation_packet_digest": packet_digest,
                "provider_evidence_digest": evidence_digest,
                "provenance_witness_digest": provenance_digest,
                "provenance_binding_digest": binding_digest,
                "provenance_claim_structurally_valid": True,
                "evidence_class": (
                    "STRUCTURALLY_BOUND_EXTERNAL_PROVENANCE_CLAIM"
                ),
                "trust_anchor_claim_present": True,
                "provider_trust_anchor_verified_by_runtime": False,
                "authorization_externally_verified_by_runtime": False,
                "submitted_inputs_persisted": False,
                "provider_evidence_fetched_by_runtime": False,
                "secret_material_accepted": False,
                "endpoint_contacted": False,
                "workflow_dispatched": False,
                "persistent_witness_executed": False,
                "dispatch_allowed": False,
                "runtime_can_promote": False,
                "ic10_required": True,
            }
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def evaluate_dispatch(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> dict[str, Any]:
        provenance = self.inspect_provenance(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
        )
        if not provenance["status"].startswith(
            "PASS_STRUCTURAL_EVIDENCE_PROVENANCE_BINDING"
        ):
            return {
                **provenance,
                "dispatch_status": "REJECTED_PROTECTED_DISPATCH_CANDIDATE",
            }
        gates = {
            "activation_packet_structurally_valid": True,
            "provider_evidence_structurally_valid": True,
            "packet_evidence_fields_match": True,
            "provenance_claim_structurally_valid": True,
            "provider_trust_anchor_verified": False,
            "authorization_externally_verified": False,
            "protected_environment_approved": False,
            "bearer_secret_available_at_job_runtime": False,
            "explicit_live_witness_dispatch": False,
        }
        candidate_digest = _digest(
            {
                "schema": SCHEMA,
                "phase": PHASE,
                "contract_digest": self.snapshot["contract_digest"],
                "provenance_binding_digest": provenance[
                    "provenance_binding_digest"
                ],
                "workflow_path": self.snapshot["protected_dispatch_contract"][
                    "workflow_path"
                ],
                "workflow_ref_policy": self.snapshot[
                    "protected_dispatch_contract"
                ]["workflow_ref_policy"],
                "protected_environment": WITNESS_PLAN["environment"],
                "witness_plan": WITNESS_PLAN,
                "gates": gates,
            }
        )
        return {
            "status": (
                "HOLD_PROTECTED_DISPATCH__"
                "EXTERNAL_TRUST_AND_ENVIRONMENT_APPROVAL_OPEN"
            ),
            "dispatch_candidate_digest": candidate_digest,
            "provenance_binding_digest": provenance[
                "provenance_binding_digest"
            ],
            "gates": gates,
            "passed_gates": [name for name, passed in gates.items() if passed],
            "open_gates": [name for name, passed in gates.items() if not passed],
            "workflow": deepcopy(self.snapshot["protected_dispatch_contract"]),
            "required_external_transition": [
                "verify the witness through a provider-specific trust adapter",
                "verify authorization outside the submitted JSON values",
                "approve the exact candidate head in p10-persistent-host",
                "provision the bearer only at protected job runtime",
                "explicitly request the three-sample persistent witness",
            ],
            "submitted_inputs_persisted": False,
            "provider_evidence_fetched_by_runtime": False,
            "secret_material_accepted": False,
            "endpoint_contacted": False,
            "workflow_dispatched": False,
            "persistent_witness_executed": False,
            "dispatch_allowed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }

    @staticmethod
    def _rejected(reason: str) -> dict[str, Any]:
        return {
            "status": "HOLD_EVIDENCE_PROVENANCE_REJECTED",
            "error": reason,
            "provenance_claim_structurally_valid": False,
            "provider_trust_anchor_verified_by_runtime": False,
            "authorization_externally_verified_by_runtime": False,
            "submitted_inputs_persisted": False,
            "provider_evidence_fetched_by_runtime": False,
            "secret_material_accepted": False,
            "endpoint_contacted": False,
            "workflow_dispatched": False,
            "persistent_witness_executed": False,
            "dispatch_allowed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_evidence_provenance_gate(mcp: Any) -> None:
    """Register W17 evidence-provenance and protected-dispatch surfaces."""

    gate = FrozenEvidenceProvenanceGate.load()

    @mcp.tool()
    def athena_w17_evidence_provenance_status() -> str:
        """Report W17 provenance readiness and open trust/dispatch gates."""
        return _render(gate.status())

    @mcp.tool()
    def build_athena_w17_provenance_witness_template(
        activation_packet_json: str,
        provider_evidence_json: str,
    ) -> str:
        """Build an unresolved, secret-free witness template bound to W16."""
        return _render(
            gate.build_provenance_template(
                activation_packet_json, provider_evidence_json
            )
        )

    @mcp.tool()
    def inspect_athena_w17_evidence_provenance(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> str:
        """Audit a provenance claim without trusting or persisting it."""
        return _render(
            gate.inspect_provenance(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
        )

    @mcp.tool()
    def evaluate_athena_w17_protected_dispatch_gate(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> str:
        """Compute a fail-closed dispatch decision; never dispatch a workflow."""
        return _render(
            gate.evaluate_dispatch(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
        )

    @mcp.resource("athena://w17-evidence-provenance-gate")
    def evidence_provenance_gate_resource() -> str:
        """Expose the frozen W17 provenance and dispatch-gate contract."""
        return _render(gate.status())

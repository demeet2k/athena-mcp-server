#!/usr/bin/env python3
"""
PackLinter.v1 — Receipt Verifier and Linter

Required/forbidden field matrix, lint failure codes,
and receipt-chain integrity verification.
"""

from typing import Dict, List, Tuple

from .constants import RECEIPT_TYPES, RECEIPT_PHASES
from .types import (
    Truth4,
    ClaimPack, WitnessBundle, ReplayBundle,
    ReceiptEntry, ReceiptRegistry, SealedReceiptBundle,
)
from .receipt_engine import sha256_hex, chain_digest


# ═══════════════════════════════════════════════════════════════
# LINT FAILURE CODES
# ═══════════════════════════════════════════════════════════════

# Code → description
LINT_CODES = {
    "L001": "ClaimPack missing pack_id",
    "L002": "ClaimPack missing truth_record",
    "L003": "ClaimPack missing payload_root",
    "L004": "ClaimPack missing scope_digest",
    "L005": "WitnessBundle missing witness_digest",
    "L006": "WitnessBundle missing claims",
    "L007": "ReplayBundle missing replay_digest",
    "L008": "ReplayBundle missing env_fingerprint",
    "L009": "ReceiptEntry invalid receipt_type",
    "L010": "ReceiptEntry missing receipt_digest",
    "L011": "ReceiptRegistry chain root mismatch",
    "L012": "ReceiptRegistry empty",
    "L013": "ReceiptRegistry entries out of order",
    "L014": "SealedBundle digest_root mismatch",
    "L015": "SealedBundle missing claim_packs",
    "L016": "SealedBundle missing receipt_registry_ref",
    "L020": "FAIL truth in OK-only context",
    "L021": "AMBIG truth with publish_intent",
}


# ═══════════════════════════════════════════════════════════════
# CLAIM PACK LINT
# ═══════════════════════════════════════════════════════════════

def lint_claim_pack(cp: ClaimPack) -> List[str]:
    """Lint a ClaimPack, returning list of failure codes."""
    failures = []
    if not cp.pack_id:
        failures.append("L001")
    if cp.truth_record is None:
        failures.append("L002")
    if not cp.payload_root:
        failures.append("L003")
    if not cp.scope_digest:
        failures.append("L004")
    return failures


# ═══════════════════════════════════════════════════════════════
# WITNESS BUNDLE LINT
# ═══════════════════════════════════════════════════════════════

def lint_witness_bundle(wb: WitnessBundle) -> List[str]:
    failures = []
    if not wb.witness_digest:
        failures.append("L005")
    if not wb.claims:
        failures.append("L006")
    return failures


# ═══════════════════════════════════════════════════════════════
# REPLAY BUNDLE LINT
# ═══════════════════════════════════════════════════════════════

def lint_replay_bundle(rb: ReplayBundle) -> List[str]:
    failures = []
    if not rb.replay_digest:
        failures.append("L007")
    if not rb.env_fingerprint:
        failures.append("L008")
    return failures


# ═══════════════════════════════════════════════════════════════
# RECEIPT ENTRY LINT
# ═══════════════════════════════════════════════════════════════

def lint_receipt_entry(re: ReceiptEntry) -> List[str]:
    failures = []
    if re.receipt_type not in RECEIPT_TYPES:
        failures.append("L009")
    if not re.receipt_digest:
        failures.append("L010")
    return failures


# ═══════════════════════════════════════════════════════════════
# RECEIPT REGISTRY LINT
# ═══════════════════════════════════════════════════════════════

def lint_receipt_registry(reg: ReceiptRegistry) -> List[str]:
    failures = []
    if not reg.receipt_entries:
        failures.append("L012")
        return failures

    # Check ordering
    for i in range(len(reg.receipt_entries) - 1):
        a = reg.receipt_entries[i]
        b = reg.receipt_entries[i + 1]
        if (a.phase_rank, a.type_rank) > (b.phase_rank, b.type_rank):
            failures.append("L013")
            break

    # Verify chain root
    computed_root = chain_digest(reg.receipt_entries)
    if computed_root != reg.receipt_chain_root:
        failures.append("L011")

    # Lint individual entries
    for entry in reg.receipt_entries:
        failures.extend(lint_receipt_entry(entry))

    return failures


# ═══════════════════════════════════════════════════════════════
# SEALED BUNDLE LINT
# ═══════════════════════════════════════════════════════════════

def lint_sealed_bundle(bundle: SealedReceiptBundle) -> List[str]:
    failures = []
    if not bundle.claim_packs:
        failures.append("L015")
    if not bundle.receipt_registry_ref:
        failures.append("L016")

    # Verify digest root
    digest_parts = [
        bundle.route_profile_id,
        bundle.policy_digest,
        bundle.receipt_registry_ref or "",
    ]
    digest_parts.extend(bundle.claim_packs)
    digest_parts.extend(bundle.witness_bundles)
    digest_parts.extend(bundle.replay_bundles)
    computed = sha256_hex(*digest_parts)

    if computed != bundle.digest_root:
        failures.append("L014")

    return failures


# ═══════════════════════════════════════════════════════════════
# FULL LINT
# ═══════════════════════════════════════════════════════════════

def full_lint(
    claim_packs: List[ClaimPack],
    witness_bundles: List[WitnessBundle],
    replay_bundles: List[ReplayBundle],
    registry: ReceiptRegistry,
    sealed: SealedReceiptBundle,
) -> Dict[str, List[str]]:
    """
    Run full lint across all receipt components.
    Returns dict of component_id → list of failure codes.
    """
    results: Dict[str, List[str]] = {}

    for cp in claim_packs:
        f = lint_claim_pack(cp)
        if f:
            results[f"ClaimPack:{cp.pack_id[:8]}"] = f

    for wb in witness_bundles:
        f = lint_witness_bundle(wb)
        if f:
            results[f"WitnessBundle:{wb.bundle_id[:8]}"] = f

    for rb in replay_bundles:
        f = lint_replay_bundle(rb)
        if f:
            results[f"ReplayBundle:{rb.bundle_id[:8]}"] = f

    f = lint_receipt_registry(registry)
    if f:
        results["ReceiptRegistry"] = f

    f = lint_sealed_bundle(sealed)
    if f:
        results["SealedBundle"] = f

    return results

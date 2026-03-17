#!/usr/bin/env python3
"""
ReceiptEngine.v1 — Receipt Bundle Builders

ClaimPack, WitnessBundle, ReplayBundle, ReceiptRegistry,
and SealedReceiptBundle assembly.
"""

import hashlib
from typing import Dict, List, Optional

from .constants import RECEIPT_PHASES, RECEIPT_TYPES
from .types import (
    Truth4, Ptr,
    ClaimPack, WitnessBundle, ReplayBundle,
    ReceiptEntry, ReceiptRegistry,
    ReleaseManifest, SealedReceiptBundle,
    TruthRecord,
)


# ═══════════════════════════════════════════════════════════════
# DIGEST HELPERS
# ═══════════════════════════════════════════════════════════════

def sha256_hex(*parts: str) -> str:
    """Compute SHA-256 hex digest of concatenated parts."""
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
    return h.hexdigest()


def chain_digest(entries: List[ReceiptEntry]) -> str:
    """Compute chain root digest from ordered receipt entries."""
    if not entries:
        return sha256_hex("empty_chain")
    running = entries[0].receipt_digest
    for e in entries[1:]:
        running = sha256_hex(running, e.receipt_digest)
    return running


# ═══════════════════════════════════════════════════════════════
# CLAIM PACK BUILDER
# ═══════════════════════════════════════════════════════════════

def build_claim_pack(
    route_profile_id: str,
    policy_digest: str,
    ms_id: str,
    local_addr: str,
    global_addr: str,
    truth: Truth4,
    payload_root: str,
) -> ClaimPack:
    """Build a ClaimPack from route output."""
    scope_digest = sha256_hex(ms_id, local_addr, global_addr)
    corridor_digest = sha256_hex(route_profile_id, policy_digest)
    pack_id = sha256_hex("ClaimPack", scope_digest, corridor_digest, payload_root)

    return ClaimPack(
        pack_id=pack_id,
        route_profile_id=route_profile_id,
        policy_digest=policy_digest,
        ms_id=ms_id,
        local_addr=local_addr,
        global_addr=global_addr,
        scope_digest=scope_digest,
        corridor_digest=corridor_digest,
        truth_record=TruthRecord(truth=truth),
        payload_root=payload_root,
    )


# ═══════════════════════════════════════════════════════════════
# WITNESS BUNDLE BUILDER
# ═══════════════════════════════════════════════════════════════

def build_witness_bundle(
    target_addr: str,
    wkind: List[str],
    claims: List[str],
    derivations: List[str],
) -> WitnessBundle:
    """Build a WitnessBundle from claims and derivations."""
    witness_digest = sha256_hex(
        target_addr, ",".join(wkind),
        ",".join(claims), ",".join(derivations),
    )
    bundle_id = sha256_hex("WitnessBundle", witness_digest)

    return WitnessBundle(
        bundle_id=bundle_id,
        target_addr=target_addr,
        wkind=wkind,
        claims=claims,
        derivations=derivations,
        witness_digest=witness_digest,
    )


# ═══════════════════════════════════════════════════════════════
# REPLAY BUNDLE BUILDER
# ═══════════════════════════════════════════════════════════════

def build_replay_bundle(
    target_addr: str,
    plan_ref: str,
    inputs_ref: str,
    outputs_ref: str,
    env_fingerprint: str,
    determinism_mode: str = "strict",
) -> ReplayBundle:
    """Build a ReplayBundle for deterministic verification."""
    replay_digest = sha256_hex(
        target_addr, plan_ref, inputs_ref, outputs_ref, env_fingerprint,
    )
    bundle_id = sha256_hex("ReplayBundle", replay_digest)

    return ReplayBundle(
        bundle_id=bundle_id,
        target_addr=target_addr,
        plan_ref=plan_ref,
        inputs_ref=inputs_ref,
        outputs_ref=outputs_ref,
        env_fingerprint=env_fingerprint,
        determinism_mode=determinism_mode,
        replay_digest=replay_digest,
    )


# ═══════════════════════════════════════════════════════════════
# RECEIPT REGISTRY BUILDER
# ═══════════════════════════════════════════════════════════════

def build_receipt_entry(
    receipt_type: str,
    target_addr: str,
    source_digest: str,
    phase: str,
) -> ReceiptEntry:
    """Build a single receipt entry."""
    phase_rank = RECEIPT_PHASES.index(phase) if phase in RECEIPT_PHASES else 99
    type_rank = RECEIPT_TYPES.index(receipt_type) if receipt_type in RECEIPT_TYPES else 99
    receipt_digest = sha256_hex(receipt_type, target_addr, source_digest)

    feeds = {
        "replay": "D_replay",
        "audit": "D_proof",
        "promotion": "D_seal",
        "publish": "D_seal",
        "chain": "D_rcpt",
    }.get(phase, "D_unknown")

    return ReceiptEntry(
        receipt_type=receipt_type,
        target_addr=target_addr,
        source_digest=source_digest,
        receipt_digest=receipt_digest,
        feeds_digest=feeds,
        phase_rank=phase_rank,
        type_rank=type_rank,
    )


def build_receipt_registry(entries: List[ReceiptEntry]) -> ReceiptRegistry:
    """Build an ordered receipt registry with chain root."""
    sorted_entries = sorted(entries, key=lambda e: (e.phase_rank, e.type_rank))
    root = chain_digest(sorted_entries)

    return ReceiptRegistry(
        receipt_entries=sorted_entries,
        receipt_chain_root=root,
    )


# ═══════════════════════════════════════════════════════════════
# SEALED BUNDLE BUILDER
# ═══════════════════════════════════════════════════════════════

def build_sealed_bundle(
    route_profile_id: str,
    policy_digest: str,
    claim_packs: List[ClaimPack],
    witness_bundles: List[WitnessBundle],
    replay_bundles: List[ReplayBundle],
    registry: ReceiptRegistry,
) -> SealedReceiptBundle:
    """Assemble the top-level SealedReceiptBundle."""
    digest_parts = [
        route_profile_id,
        policy_digest,
        registry.receipt_chain_root,
    ]
    for cp in claim_packs:
        digest_parts.append(cp.pack_id)
    for wb in witness_bundles:
        digest_parts.append(wb.bundle_id)
    for rb in replay_bundles:
        digest_parts.append(rb.bundle_id)

    digest_root = sha256_hex(*digest_parts)
    bundle_id = sha256_hex("SealedReceiptBundle", digest_root)

    return SealedReceiptBundle(
        bundle_id=bundle_id,
        route_profile_id=route_profile_id,
        policy_digest=policy_digest,
        digest_root=digest_root,
        receipt_registry_ref=registry.receipt_chain_root,
        claim_packs=[cp.pack_id for cp in claim_packs],
        witness_bundles=[wb.bundle_id for wb in witness_bundles],
        replay_bundles=[rb.bundle_id for rb in replay_bundles],
    )

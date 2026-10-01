from __future__ import annotations

"""Loss-aware garbage collection for process-local Liminal Beacon state.

The base mesh already expires packets from the routing index.  This additive
collector removes process-local state that becomes non-actionable once those
packets disappear, while deliberately preserving the reverse-consumer index
needed to route later corrections/retractions to prior consumers.
"""

from typing import Any

VERSION = "LIMINAL.GC.1"
ARTIFACT = "ATHENA.LIMINAL.GC.V1.CANDIDATE"

LAWS = [
    "EXPIRED_PACKET_RECEIPT_DETAIL_MAY_COMPACT_AFTER_PACKET_BECOMES_NON_ACTIONABLE",
    "REVERSE_CONSUMER_INDEX_SURVIVES_RECEIPT_DETAIL_COMPACTION",
    "LIVE_PACKET_OR_ACTIVE_EPOCH_STATE_MUST_NOT_BE_COLLECTED",
    "GC_COUNT != PROOF_OF_MEMORY_PRESSURE",
    "PROCESS_LOCAL_GC != DURABLE_HISTORY_DELETION",
]


def install_liminal_gc(runtime_cls: type) -> None:
    if getattr(runtime_cls, "_athena_liminal_gc_v1_registered", False):
        return

    previous_prune = runtime_cls._prune
    previous_manifest = runtime_cls.manifest
    previous_state = runtime_cls.state

    def prune_with_gc(self):
        previous_prune(self)
        live_packet_ids = set(getattr(self, "_packets", {}))

        receipts = getattr(self, "_receipts", {})
        dead_receipt_keys = [key for key in receipts if key[1] not in live_packet_ids]
        for key in dead_receipt_keys:
            receipts.pop(key, None)
        if dead_receipt_keys:
            self._metrics["gc_receipt_details"] += len(dead_receipt_keys)

        bridge_ledger = getattr(self, "_synapse_return_ledger_v1", None)
        dead_bridge_keys = []
        if isinstance(bridge_ledger, dict):
            dead_bridge_keys = [key for key in bridge_ledger if key[0] not in live_packet_ids]
            for key in dead_bridge_keys:
                bridge_ledger.pop(key, None)
            if dead_bridge_keys:
                self._metrics["gc_bridge_receipts"] += len(dead_bridge_keys)

        active_epochs = {
            (str(row.get("agent_id")), str(row.get("session_epoch")))
            for row in getattr(self, "_presence", {}).values()
            if row.get("liveness") == "ACTIVE"
        }
        live_packet_epochs = {
            (str(row.get("sender_id")), str(row.get("session_epoch")))
            for row in getattr(self, "_packets", {}).values()
        }
        sender_seq = getattr(self, "_sender_seq", {})
        dead_sender_epochs = [
            key
            for key in sender_seq
            if key not in active_epochs and key not in live_packet_epochs
        ]
        for key in dead_sender_epochs:
            sender_seq.pop(key, None)
        if dead_sender_epochs:
            self._metrics["gc_sender_epochs"] += len(dead_sender_epochs)

    def manifest(self):
        value = dict(previous_manifest(self))
        value["garbage_collection"] = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "standing": "CANDIDATE_LOSS_AWARE_PROCESS_LOCAL_GC",
            "compacts": ["expired_packet_receipt_detail", "expired_bridge_receipt", "inactive_sender_epoch_sequence"],
            "preserves": ["reverse_consumer_index", "durable_git_history", "live_packet_state", "active_sender_epoch"],
            "laws": list(LAWS),
        }
        return value

    def state(self, agent_id: str | None = None, include_packets: bool = False, limit: int = 50):
        # Existing state() already invokes _prune; call through first so the
        # collector has run before reporting its counters.
        value = dict(previous_state(self, agent_id=agent_id, include_packets=include_packets, limit=limit))
        metrics = value.get("metrics") if isinstance(value.get("metrics"), dict) else {}
        value["garbage_collection"] = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "receipt_details_compacted": int(metrics.get("gc_receipt_details") or 0),
            "bridge_receipts_compacted": int(metrics.get("gc_bridge_receipts") or 0),
            "sender_epochs_compacted": int(metrics.get("gc_sender_epochs") or 0),
            "reverse_consumer_entries": sum(
                len(values) for values in getattr(self, "_reverse_consumers", {}).values()
            ),
            "laws": list(LAWS),
        }
        return value

    runtime_cls._prune = prune_with_gc
    runtime_cls.manifest = manifest
    runtime_cls.state = state
    runtime_cls._athena_liminal_gc_v1_registered = True


__all__ = ["VERSION", "ARTIFACT", "LAWS", "install_liminal_gc"]

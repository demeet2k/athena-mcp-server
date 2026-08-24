from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Mapping

VERSION = "ATHENA.FEDERATION.EPHEMERAL.CURSOR.BRIDGE.V1"
REF_PREFIX = "athena-federation-handoff-v1"
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_ALLOWED_CLASSES = {"RENDEZVOUS", "NEED_OFFER", "NUDGE", "BLOCKER", "MATERIAL_CANDIDATE"}


def _digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{field} must be sha256:<64 lowercase hex>")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty string")
    return value.strip()


def _int(value: Any, field: str, low: int, high: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be integer")
    try:
        out = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be integer") from None
    if not low <= out <= high:
        raise ValueError(f"{field} must be between {low} and {high}")
    return out


def _float(value: Any, field: str, low: float, high: float) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be numeric") from None
    if not low <= out <= high:
        raise ValueError(f"{field} must be between {low} and {high}")
    return out


def _strings(value: Any, field: str, limit: int) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be array")
    out: list[str] = []
    for item in value:
        text = _text(item, field)
        if text not in out:
            out.append(text)
        if len(out) > limit:
            raise ValueError(f"{field} exceeds {limit} unique items")
    return tuple(out)


@dataclass(frozen=True)
class FederationTransportProjection:
    handoff_digest: str
    source_cursor_digest: str
    transport_ref: str
    loss_class: str = "LOSSY_AUX"
    reconstruction_token: str | None = None
    authority: str = "NONE"

    def validate(self) -> None:
        _digest(self.handoff_digest, "handoff_digest")
        _digest(self.source_cursor_digest, "source_cursor_digest")
        if self.transport_ref != encode_handoff_ref(self.handoff_digest, self.source_cursor_digest):
            raise ValueError("transport_ref does not roundtrip projection")
        if self.loss_class != "LOSSY_AUX":
            raise ValueError("ephemeral projection must remain LOSSY_AUX")
        if self.reconstruction_token != self.handoff_digest:
            raise ValueError("reconstruction_token must be canonical handoff digest")
        if self.authority != "NONE":
            raise ValueError("ephemeral projection authority must remain NONE")

    @property
    def source_currentness_proven(self) -> bool:
        return False


def encode_handoff_ref(handoff_digest: str, source_cursor_digest: str) -> str:
    h = _digest(handoff_digest, "handoff_digest")
    c = _digest(source_cursor_digest, "source_cursor_digest")
    return f"{REF_PREFIX}:{h[7:]}:{c[7:]}"


def decode_handoff_ref(value: str) -> FederationTransportProjection:
    text = _text(value, "packet_digest_or_ref")
    parts = text.split(":")
    if len(parts) != 3 or parts[0] != REF_PREFIX:
        raise ValueError("not an ATHENA federation ephemeral handoff ref")
    handoff = "sha256:" + parts[1]
    cursor = "sha256:" + parts[2]
    _digest(handoff, "handoff_digest")
    _digest(cursor, "source_cursor_digest")
    projection = FederationTransportProjection(
        handoff_digest=handoff,
        source_cursor_digest=cursor,
        transport_ref=text,
        reconstruction_token=handoff,
    )
    projection.validate()
    return projection


def project_post_args(args: Mapping[str, Any]) -> tuple[dict[str, Any], FederationTransportProjection]:
    if not isinstance(args, Mapping):
        raise ValueError("args must be object")
    sender = _text(args.get("sender_aid"), "sender_aid")
    recipients = _strings(args.get("recipient_aids"), "recipient_aids", 32)
    if not recipients:
        raise ValueError("recipient_aids must be non-empty")
    handoff = _digest(args.get("handoff_digest"), "handoff_digest")
    cursor = _digest(args.get("source_cursor_digest"), "source_cursor_digest")
    kind = _text(args.get("delivery_class", "MATERIAL_CANDIDATE"), "delivery_class")
    if kind not in _ALLOWED_CLASSES:
        raise ValueError("invalid delivery_class")
    salience = _float(args.get("salience", 0.8), "salience", 0.0, 1.0)
    ttl_ms = _int(args.get("ttl_ms", 30000), "ttl_ms", 250, 300000)
    lamport = _int(args.get("lamport", 0), "lamport", 0, 2**63 - 1)
    parents = _strings(args.get("causal_parents", []), "causal_parents", 32)
    projection = FederationTransportProjection(
        handoff_digest=handoff,
        source_cursor_digest=cursor,
        transport_ref=encode_handoff_ref(handoff, cursor),
        reconstruction_token=handoff,
    )
    projection.validate()
    return ({
        "sender_aid": sender,
        "recipient_selector": {"aids": list(recipients)},
        "delivery_class": kind,
        "salience": salience,
        "ttl_ms": ttl_ms,
        "packet_digest_or_ref": projection.transport_ref,
        "lamport": lamport,
        "causal_parents": list(parents),
    }, projection)


def assess_advisory_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, Mapping):
        raise ValueError("snapshot must be object")
    if snapshot.get("authority") != "NONE" or snapshot.get("advisory") is not True:
        raise ValueError("snapshot is not a zero-authority advisory MCP snapshot")
    cursor = _int(snapshot.get("next_cursor", 0), "next_cursor", 0, 2**63 - 1)
    floor = _int(snapshot.get("cursor_floor", 0), "cursor_floor", 0, 2**63 - 1)
    truncated = bool(snapshot.get("replay_truncated", False))
    return {
        "process_cursor": cursor,
        "cursor_floor": floor,
        "replay_truncated": truncated,
        "standing": "HOLD_TRANSPORT_REPLAY_TRUNCATED" if truncated else "ADVISORY_TRANSPORT_CURSOR_ONLY",
        "projection_grade": "M",
        "loss_class": "LOSSY_AUX",
        "source_prefix_identity_proven": False,
        "source_currentness_proven": False,
        "authority": "NONE",
        "laws": [
            "MCP_PROCESS_CURSOR!=FEDERATION_SOURCE_CURSOR",
            "SNAPSHOT_CHANGED_SINCE_CURSOR!=SOURCE_PREFIX_PROOF",
            "TRANSPORT_FRESHNESS!=PROVIDER_CURRENTNESS",
        ],
    }


def build_consumption_witness(args: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(args, Mapping):
        raise ValueError("args must be object")
    handoff = _digest(args.get("handoff_digest"), "handoff_digest")
    cursor = _digest(args.get("source_cursor_digest"), "source_cursor_digest")
    admission = _digest(args.get("federation_admission_receipt_digest"), "federation_admission_receipt_digest")
    consumer = _text(args.get("consumer_ref"), "consumer_ref")
    return {
        "consumer_ref": consumer,
        "federation_handoff_digest": handoff,
        "federation_source_cursor_digest": cursor,
        "federation_admission_receipt_digest": admission,
        "projection_loss_class": "LOSSY_AUX",
        "authority": "NONE",
        "law": "MCP_CONSUMED_RECEIPT_REQUIRES_EXTERNAL_FEDERATION_CURSOR_ADMISSION",
    }


class FederationEphemeralBridge:
    def __init__(self, runtime):
        self.runtime = runtime

    def post(self, args: Mapping[str, Any]) -> dict[str, Any]:
        post_args, projection = project_post_args(args)
        transport = self.runtime.post(post_args)
        return {
            "transport": transport,
            "projection": asdict(projection),
            "standing": "ROUTED_REQUIRES_DESTINATION_FEDERATION_CURSOR_ADMISSION",
            "source_currentness_proven": False,
            "authority": "NONE",
            "laws": [
                "MCP_ROUTE!=FEDERATION_ADMISSION",
                "MCP_PROCESS_CURSOR!=FEDERATION_SOURCE_CURSOR",
                "ROUTED!=DELIVERED!=CONSUMED!=APPLIED",
            ],
        }

    def poll(self, args: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(args, Mapping):
            raise ValueError("args must be object")
        transport = self.runtime.poll(dict(args))
        handoffs: list[dict[str, Any]] = []
        non_federation = 0
        for packet in transport.get("packets", []):
            try:
                projection = decode_handoff_ref(packet.get("packet_digest_or_ref"))
            except (TypeError, ValueError):
                non_federation += 1
                continue
            handoffs.append({
                "packet_id": packet.get("packet_id"),
                "sender_aid": packet.get("sender_aid"),
                "transport_cursor": packet.get("cursor"),
                "route_state": packet.get("route_state"),
                "receipt_stage": packet.get("receipt_stage"),
                "handoff_digest": projection.handoff_digest,
                "source_cursor_digest": projection.source_cursor_digest,
                "reconstruction_token": projection.reconstruction_token,
                "loss_class": projection.loss_class,
                "standing": "TRANSPORT_OBSERVED_REQUIRES_FEDERATION_CURSOR_ADMISSION",
                "source_currentness_proven": False,
                "authority": "NONE",
            })
        replay_truncated = bool(transport.get("replay_truncated", False))
        return {
            "handoffs": handoffs,
            "non_federation_packet_count": non_federation,
            "next_transport_cursor": transport.get("next_cursor", args.get("after_cursor", 0)),
            "transport_cursor_floor": transport.get("cursor_floor", 0),
            "transport_replay_truncated": replay_truncated,
            "history_standing": "HOLD_TRANSPORT_REPLAY_TRUNCATED" if replay_truncated else "BOUNDED_TRANSPORT_SUFFIX_OBSERVED",
            "transport": transport,
            "authority": "NONE",
            "laws": [
                "OBSERVED_EPHEMERAL_PACKET!=FEDERATION_CURSOR_ADMISSION",
                "TRANSPORT_REPLAY_CONTINUITY!=SOURCE_PREFIX_CONTINUITY",
            ],
        }

    def witness(self, args: Mapping[str, Any]) -> dict[str, Any]:
        return build_consumption_witness(args)

    def describe(self) -> dict[str, Any]:
        return {
            "version": VERSION,
            "projection": "FEDERATION_CURSOR_BOUND_HANDOFF->MCP_PROCESS_LOCAL_EPHEMERAL_PACKET",
            "loss_class": "LOSSY_AUX",
            "reconstruction": "canonical handoff digest required",
            "authority": "NONE",
            "source_currentness_proven": False,
            "operations": [
                "athena_ephemeral_federation_post",
                "athena_ephemeral_federation_poll",
                "athena_ephemeral_federation_witness",
            ],
            "laws": [
                "MCP_PROCESS_CURSOR!=FEDERATION_SOURCE_CURSOR",
                "MCP_ROUTE!=FEDERATION_ADMISSION",
                "MCP_RECEIPT!=SOURCE_CURRENTNESS",
            ],
        }

    def benchmark(self) -> dict[str, Any]:
        return {
            "federation_ephemeral_bridge_version": VERSION,
            "federation_ephemeral_bridge_authority": "NONE",
            "federation_ephemeral_bridge_loss_class": "LOSSY_AUX",
        }


class FederationEphemeralBridgeSurface:
    def __init__(self, runtime):
        self.bridge = FederationEphemeralBridge(runtime)

    def call_tool(self, name: str, args: Mapping[str, Any]):
        fn = {
            "athena_ephemeral_federation_post": self.bridge.post,
            "athena_ephemeral_federation_poll": self.bridge.poll,
            "athena_ephemeral_federation_witness": self.bridge.witness,
        }.get(name)
        return (True, fn(args)) if fn else (False, None)

    def read_resource(self, uri: str):
        from .federation_ephemeral_bridge_protocol import FEDERATION_EPHEMERAL_RESOURCE
        if uri != FEDERATION_EPHEMERAL_RESOURCE["uri"]:
            raise KeyError(uri)
        return self.bridge.describe()

    def benchmark(self):
        return self.bridge.benchmark()

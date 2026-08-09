from __future__ import annotations

"""Strict typed semantic autohook treatment for Liminal Beacon Mesh V1.1.

The treatment never infers semantic lineage from prose or arbitrary result fields.
A tool must explicitly return a bounded ``_liminal_publish`` envelope.  Absence of
that envelope preserves V1 generic metadata sharing exactly; malformed envelopes
fail the communication side closed without changing the underlying tool result.
"""

from typing import Any

ALLOWED_KEYS = {
    "message_class",
    "summary",
    "payload_ref",
    "changed_refs",
    "affected_refs",
    "reply_to",
    "correction_of",
    "retraction_of",
}
ALLOWED_CLASSES = {
    "DISCOVERY",
    "RESULT",
    "BLOCKER",
    "QUESTION",
    "ANSWER",
    "CORRECTION",
    "RETRACTION",
    "HANDOFF",
    "NEED",
    "OFFER",
}


def _text(value: Any, *, maximum: int, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise ValueError("missing required text")
        return None
    if not isinstance(value, str):
        raise ValueError("semantic text fields must be strings")
    value = value.strip()
    if required and not value:
        raise ValueError("required semantic text field is empty")
    if not value:
        return None
    return value[:maximum]


def _refs(value: Any, *, maximum_items: int = 16) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("semantic reference collections must be arrays")
    if len(value) > maximum_items:
        raise ValueError("semantic reference collection exceeds bound")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("semantic references must be nonempty strings")
        ref = item.strip()[:256]
        if ref not in out:
            out.append(ref)
    return out


def _validate(self, raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("_liminal_publish must be an object")
    extra = set(raw) - ALLOWED_KEYS
    if extra:
        raise ValueError("unknown semantic envelope keys: " + ",".join(sorted(extra)))

    message_class = _text(raw.get("message_class"), maximum=32, required=True).upper()
    if message_class not in ALLOWED_CLASSES:
        raise ValueError("unsupported semantic message_class")
    summary = _text(raw.get("summary"), maximum=512, required=True)
    payload_ref = _text(raw.get("payload_ref"), maximum=512)
    reply_to = _text(raw.get("reply_to"), maximum=160)
    correction_of = _text(raw.get("correction_of"), maximum=160)
    retraction_of = _text(raw.get("retraction_of"), maximum=160)

    if message_class == "CORRECTION":
        if not correction_of or retraction_of:
            raise ValueError("CORRECTION requires only correction_of")
    elif correction_of:
        raise ValueError("correction_of requires message_class=CORRECTION")

    if message_class == "RETRACTION":
        if not retraction_of or correction_of:
            raise ValueError("RETRACTION requires only retraction_of")
    elif retraction_of:
        raise ValueError("retraction_of requires message_class=RETRACTION")

    with self._lock:
        if correction_of and correction_of not in self._packets:
            raise ValueError("correction_of packet is not present in local carrier")
        if retraction_of and retraction_of not in self._packets:
            raise ValueError("retraction_of packet is not present in local carrier")

    return {
        "message_class": message_class,
        "summary": summary,
        "payload_ref": payload_ref,
        "changed_refs": _refs(raw.get("changed_refs")),
        "affected_refs": _refs(raw.get("affected_refs")),
        "reply_to": reply_to,
        "correction_of": correction_of,
        "retraction_of": retraction_of,
    }


def install_liminal_beacon_semantic_v11(runtime_cls) -> None:
    if getattr(runtime_cls, "_athena_liminal_semantic_v11_registered", False):
        return

    previous_auto_after_tool = runtime_cls.auto_after_tool

    def auto_after_tool_semantic(self, name: str, arguments: dict[str, Any], value: Any):
        if not isinstance(value, dict) or "_liminal_publish" not in value:
            return previous_auto_after_tool(self, name, arguments, value)

        agent_id = self.infer_agent_id(arguments)
        if not agent_id:
            return {
                "emitted": None,
                "semantic_error": "SEMANTIC_ENVELOPE_AGENT_ID_UNKNOWN_HOLD",
                "law": "SEMANTIC_ENVELOPE != HIDDEN_IDENTITY_INFERENCE",
            }

        try:
            envelope = _validate(self, value.get("_liminal_publish"))
        except Exception as exc:
            # The communication organ fails closed while the extension wrapper
            # keeps the already-completed underlying tool call fail-open.
            return {
                "emitted": None,
                "semantic_error": f"SEMANTIC_ENVELOPE_HOLD:{type(exc).__name__}:{exc}",
                "rendezvous": self.rendezvous(
                    agent_id,
                    limit=4,
                    threshold=0.35,
                    context_budget=2400,
                    scout_quota=1,
                ),
                "law": "MALFORMED_SEMANTIC_SHARE != TOOL_EXECUTION_FAILURE",
            }

        work, objects, deps = self._refs_from_call(arguments)
        status = str(value.get("status") or value.get("pre_dispatch") or "").strip()
        changed = list(envelope["changed_refs"])
        for key in (
            "event",
            "eid",
            "run_id",
            "claim_id",
            "head",
            "git_head",
            "routing_digest",
            "decision_digest",
        ):
            raw = value.get(key)
            if raw not in (None, ""):
                ref = f"{key}:{raw}"[:256]
                if ref not in changed:
                    changed.append(ref)

        message_class = envelope["message_class"]
        critical = message_class in {"BLOCKER", "CORRECTION", "RETRACTION", "HANDOFF"}
        tags = [f"tool:{name}", "semantic:typed-v1.1"]
        if status:
            tags.append(f"status:{status}"[:160])

        emitted = self.emit(
            agent_id,
            message_class,
            envelope["summary"],
            work_refs=work,
            object_refs=objects,
            dependency_refs=deps,
            semantic_tags=tags,
            changed_refs=changed,
            affected_refs=envelope["affected_refs"],
            payload_ref=envelope["payload_ref"],
            reply_to=envelope["reply_to"],
            correction_of=envelope["correction_of"],
            retraction_of=envelope["retraction_of"],
            urgency=0.95 if critical else 0.55,
            novelty=0.60,
            ttl_seconds=300,
            evidence_ceiling="RUNTIME_METADATA_ONLY",
        )
        return {
            "emitted": emitted.get("packet"),
            "rendezvous": self.rendezvous(
                agent_id,
                limit=4,
                threshold=0.35,
                context_budget=2400,
                scout_quota=1,
            ),
            "semantic_envelope": "VALIDATED_TYPED_V1_1",
            "law": (
                "STRUCTURED_SEMANTIC_ENVELOPE != TRUTH; "
                "AUTOHOOK != PROSE_INFERENCE; "
                "SEMANTIC_SHARE != FULL_TOOL_RESULT_BROADCAST"
            ),
        }

    runtime_cls.auto_after_tool = auto_after_tool_semantic
    runtime_cls._athena_liminal_semantic_v11_registered = True


__all__ = ["install_liminal_beacon_semantic_v11"]

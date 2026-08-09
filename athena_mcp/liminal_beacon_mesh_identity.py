from __future__ import annotations

"""Session-epoch treatment for Liminal Beacon Mesh V1.

Callers are not required to possess a trustworthy process-instance identifier.
When they do not provide a session epoch, the runtime creates an explicitly
unwitnessed process-local epoch so restart/rebind cannot silently reuse the same
sender-epoch sequence namespace.
"""

import uuid


def install_liminal_beacon_identity(runtime_cls) -> None:
    if getattr(runtime_cls, "_athena_liminal_identity_v1_registered", False):
        return

    previous_init = runtime_cls.__init__
    previous_touch = runtime_cls.touch

    def init_with_runtime_epoch(self, *args, **kwargs):
        previous_init(self, *args, **kwargs)
        self._liminal_runtime_epoch = "LBEPOCH." + uuid.uuid4().hex

    def touch_with_runtime_epoch(
        self,
        agent_id,
        *,
        instance_id=None,
        session_epoch=None,
        **kwargs,
    ):
        existing = self._presence.get(str(agent_id or "").strip()) or {}
        prior_instance = str(existing.get("instance_id") or "")
        supplied_instance = str(instance_id).strip() if instance_id else ""

        if session_epoch is None:
            if existing and supplied_instance and prior_instance and supplied_instance != prior_instance:
                # An exposed instance rebind is an epoch boundary even inside the
                # same server process. It receives a new local epoch namespace.
                session_epoch = "LBEPOCH." + uuid.uuid4().hex
            else:
                session_epoch = existing.get("session_epoch") or self._liminal_runtime_epoch

        if instance_id is None:
            instance_id = existing.get("instance_id") or "UNWITNESSED"

        result = previous_touch(
            self,
            agent_id,
            instance_id=instance_id,
            session_epoch=session_epoch,
            **kwargs,
        )
        result["identity_standing"] = (
            "EXPLICIT_INSTANCE_WITNESS" if str(instance_id) != "UNWITNESSED" else "PROCESS_INSTANCE_UNKNOWN"
        )
        result["epoch_law"] = "RESTART_OR_REBIND_REQUIRES_NEW_SENDER_EPOCH_NAMESPACE"
        return result

    runtime_cls.__init__ = init_with_runtime_epoch
    runtime_cls.touch = touch_with_runtime_epoch
    runtime_cls._athena_liminal_identity_v1_registered = True


__all__ = ["install_liminal_beacon_identity"]

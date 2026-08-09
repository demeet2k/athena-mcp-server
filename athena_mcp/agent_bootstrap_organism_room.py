
from __future__ import annotations

from .organism_room import OrganismRoomRuntime

ARTIFACT = "ATHENA.AGENT.BOOT.ORGANISM.ROOM.V1"
_LAWS = [
    "EVERY_MATERIAL_BOOT_ENTER_ROOM_BEFORE_EXECUTION",
    "ROOM_ENTRY != WORK_CLAIM",
    "BOOT_RETURN_REQUIRES_ROOM_SIGNOUT_OR_PENDING_SIGNOUT",
    "ROOM_FAILURE => PRE_DISPATCH_HOLD",
]


def install_agent_bootstrap_organism_room(runtime_cls) -> None:
    """Make room occupancy a mandatory post-hydration pre-dispatch witness.

    The existing Message Board wrapper remains sole work-claim authority. This
    wrapper enters the same Git-backed coordination namespace and binds any
    already-created work claim to the boot session before returning execution.
    """

    if getattr(runtime_cls, "_athena_boot_organism_room_v1_registered", False):
        return

    original_bootstrap = runtime_cls.bootstrap

    def _attach(self, packet: dict, *, lease_seconds: int, remote: str) -> dict:
        if not isinstance(packet, dict) or not packet.get("agent_id") or not packet.get("session_id"):
            return packet
        room = getattr(self, "_agent_boot_organism_room_v1", None)
        if room is None:
            room = OrganismRoomRuntime(self.git)
            self._agent_boot_organism_room_v1 = room
        prompt = packet.get("prompt") or {}
        expected_head = self.git.head()
        existing = next(
            (
                row
                for row in room.snapshot().get("active", [])
                if row.get("agent_id") == packet["agent_id"]
            ),
            None,
        )
        room_session_id = (
            existing.get("session_id") if existing else packet["session_id"]
        )
        entry = room.enter(
            agent_id=packet["agent_id"],
            session_id=room_session_id,
            expected_head=expected_head,
            prompt_stack_digest=str(prompt.get("prompt_stack_digest") or "UNKNOWN"),
            capabilities=sorted(set((packet.get("execution_surface") or {}).get("frontier_tools") or [])),
            waves=["W0", "W1", "W2"],
            domains=["GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META"],
            authority_witnesses=[
                str((packet.get("execution_surface") or {}).get("standing") or "UNKNOWN")
            ],
            lease_seconds=lease_seconds,
            remote=remote,
        )
        room_packet = {
            "artifact": ARTIFACT,
            "entry": entry,
            "pre_dispatch": "ALLOW" if entry.get("status") in {"ENTERED", "ALREADY_ENTERED"} else "HOLD",
            "signout_required": True,
            "post_room_head": self.git.head(),
            "laws": list(_LAWS),
        }
        coordination = packet.get("coordination") or {}
        presence = coordination.get("presence") or {}
        claim_id = presence.get("claim_id")
        if room_packet["pre_dispatch"] == "ALLOW" and claim_id:
            binding = room.bind(
                agent_id=packet["agent_id"],
                expected_session_id=room_session_id,
                expected_claim_id=claim_id,
                remote=remote,
            )
            room_packet["claim_binding"] = binding
            room_packet["post_room_head"] = self.git.head()
            if binding.get("status") != "BOUND":
                room_packet["pre_dispatch"] = "HOLD"
        packet["organism_room"] = room_packet
        packet.setdefault("witnesses", {})["organism_room"] = {
            "entry_status": entry.get("status"),
            "room_session_id": room_session_id,
            "boot_session_id": packet["session_id"],
            "post_room_head": room_packet["post_room_head"],
            "claim_binding_status": (room_packet.get("claim_binding") or {}).get("status"),
        }
        packet.setdefault("return_contract", {})["organism_room_signout_required"] = True
        laws = packet.setdefault("laws", [])
        for law in _LAWS:
            if law not in laws:
                laws.append(law)
        if room_packet["pre_dispatch"] == "HOLD":
            holds = set(str(x) for x in packet.get("holds") or [])
            holds.add("ORGANISM_ROOM_PRE_DISPATCH_HOLD")
            holds.add(str(entry.get("status") or "ROOM_ENTRY_HOLD"))
            packet["holds"] = sorted(holds)
            packet["status"] = "BOOTSTRAP_HOLD"
        return packet

    def bootstrap_with_room(self, *args, organism_room_lease_seconds=1800, **kwargs):
        packet = original_bootstrap(self, *args, **kwargs)
        return _attach(
            self,
            packet,
            lease_seconds=int(organism_room_lease_seconds or 1800),
            remote=kwargs.get("remote", "origin"),
        )

    runtime_cls.bootstrap = bootstrap_with_room
    runtime_cls._athena_boot_organism_room_v1_registered = True

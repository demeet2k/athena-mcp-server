from __future__ import annotations


def verify_boundary(contradictions: dict[str, object], state) -> dict[str, object]:
    quarantined = bool(contradictions.get("quarantined"))
    boundary = {
        "hausdorff_boundary": "sealed" if quarantined else "open",
        "logic_wall": "strict",
        "quarantine_flux": 0.0,
        "paraconsistent_zone": "active" if quarantined else "dormant",
        "checkpoint_id": state.checkpoint_id,
    }
    return boundary

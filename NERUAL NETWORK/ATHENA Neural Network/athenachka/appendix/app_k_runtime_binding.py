TITLE = "Appendix K - Runtime Binding Contract"
ACTIVE = True


def describe_service(mode: str, phase_plan: list[str]) -> dict[str, object]:
    return {
        "code": "K",
        "title": TITLE,
        "active": ACTIVE,
        "mode": mode,
        "phase_plan": list(phase_plan),
    }

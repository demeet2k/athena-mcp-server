TITLE = "Appendix E - Neutral Synthesis Grammar"
ACTIVE = True


def describe_service(trace: dict[str, object] | None = None) -> dict[str, object]:
    trace = trace or {}
    return {
        "code": "E",
        "title": TITLE,
        "active": ACTIVE,
        "neutral_summary": {
            "prediction": trace.get("legacy_prediction"),
            "confidence": trace.get("legacy_confidence"),
            "candidate_count": len(trace.get("hypotheses", [])),
        },
    }

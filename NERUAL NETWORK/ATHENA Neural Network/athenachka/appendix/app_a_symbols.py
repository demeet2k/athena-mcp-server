TITLE = "Appendix A - Symbol Registry"
ACTIVE = True


def describe_service() -> dict[str, object]:
    return {
        "code": "A",
        "title": TITLE,
        "symbols": ["C", "P", "G", "M", "B", "R", "OK", "NEAR", "AMBIG", "FAIL"],
    }

TITLE = "Appendix M - Whole-Body Scan Guide"
ACTIVE = True


def describe_service() -> dict[str, object]:
    return {
        "code": "M",
        "title": TITLE,
        "active": ACTIVE,
        "scan_order": ["corpus", "process", "growth", "metrics", "bridges", "replay"],
    }

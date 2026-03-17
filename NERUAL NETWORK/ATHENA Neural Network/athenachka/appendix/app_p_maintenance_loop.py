TITLE = "Appendix P - Maintenance Loop"
ACTIVE = True


def describe_service() -> dict[str, object]:
    return {
        "code": "P",
        "title": TITLE,
        "active": ACTIVE,
        "maintenance_steps": ["scan", "audit", "prune", "compress", "restart"],
    }

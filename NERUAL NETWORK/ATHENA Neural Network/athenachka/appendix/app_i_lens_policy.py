TITLE = "Appendix I - Lens Invocation Policy"
ACTIVE = True


def describe_service(mode: str = "fast") -> dict[str, object]:
    return {
        "code": "I",
        "title": TITLE,
        "active": ACTIVE,
        "mode": mode,
        "lenses": ["Square", "Flower", "Cloud", "Fractal"] if mode == "full" else ["Square", "Cloud"],
    }

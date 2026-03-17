TITLE = "Appendix Q - Appendix Topology Metro Routing"
ACTIVE = True


def describe_service() -> dict[str, object]:
    return {
        "code": "Q",
        "title": TITLE,
        "active": ACTIVE,
        "metro_map": ["A->E", "E->I", "I->K", "K->L", "L->M", "M->P", "P->Q"],
    }

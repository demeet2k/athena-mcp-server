from __future__ import annotations

from typing import Any, Dict, Mapping

TEST_REQUIRED = ("procedure", "observation", "result", "witness")
PERSIST_REQUIRED = ("commit", "receipt", "verify")


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def validate_test_claim(test: Any) -> Dict[str, Any]:
    """Validate public test evidence without inferring hidden execution.

    Absence means NOT_CLAIMED. Presence means the claim is checked fail-closed:
    procedure + observation + result + witness are all required.
    """
    if test in (None, False):
        return {"status": "NOT_CLAIMED", "claimed": False, "missing": [], "promotion_allowed": True}
    if not isinstance(test, Mapping):
        return {
            "status": "BLOCKED",
            "claimed": True,
            "missing": list(TEST_REQUIRED),
            "promotion_allowed": False,
            "reason": "test claim must be an object containing public evidence fields",
        }
    missing = [field for field in TEST_REQUIRED if not _present(test.get(field))]
    return {
        "status": "PASS" if not missing else "BLOCKED",
        "claimed": True,
        "missing": missing,
        "promotion_allowed": not missing,
        "witness_count": len(test.get("witness", [])) if isinstance(test.get("witness"), list) else (1 if _present(test.get("witness")) else 0),
    }


def validate_persistence_claim(transaction: Any) -> Dict[str, Any]:
    """Validate a persistence claim as commit + receipt + readback/verify.

    The validator never treats an attempted write as persistence.
    """
    if transaction in (None, False):
        return {"status": "NOT_CLAIMED", "claimed": False, "missing": [], "promotion_allowed": True}
    if not isinstance(transaction, Mapping):
        return {
            "status": "BLOCKED",
            "claimed": True,
            "missing": list(PERSIST_REQUIRED),
            "promotion_allowed": False,
            "reason": "persistence claim must be an object containing commit/receipt/verify",
        }
    claimed = bool(transaction.get("persisted", True))
    if not claimed:
        return {"status": "NOT_CLAIMED", "claimed": False, "missing": [], "promotion_allowed": True}
    missing = [field for field in PERSIST_REQUIRED if not _present(transaction.get(field))]
    return {
        "status": "PASS" if not missing else "BLOCKED",
        "claimed": True,
        "missing": missing,
        "promotion_allowed": not missing,
        "rollback_available": _present(transaction.get("rollback")),
    }


def adversarial_branch_plan(item: Mapping[str, Any]) -> Dict[str, Any]:
    """Compile the mandatory main/counter/edge/fail test surface."""
    pressure = []
    if item.get("unsupported"):
        pressure.append("unsupported")
    if item.get("unhandled_contradiction"):
        pressure.append("contradiction")
    if item.get("fake"):
        pressure.append("fake_claim")
    if item.get("coordinate_loss"):
        pressure.append("coordinate_loss")
    return {
        "branches": ["main", "counter", "edge", "fail"],
        "pressure": pressure,
        "required": bool(pressure),
        "route": ["branch", "test", "observe", "repair", "retest"] if pressure else ["test", "observe"],
    }


def validation_bundle(item: Mapping[str, Any]) -> Dict[str, Any]:
    test = validate_test_claim(item.get("test"))
    persistence = validate_persistence_claim(item.get("transaction"))
    adversarial = adversarial_branch_plan(item)
    blocked = test["status"] == "BLOCKED" or persistence["status"] == "BLOCKED"
    return {
        "test": test,
        "persistence": persistence,
        "adversarial": adversarial,
        "status": "BLOCKED" if blocked else "PASS",
        "promotion_allowed": not blocked,
    }

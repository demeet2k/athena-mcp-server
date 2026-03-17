from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
PROMOTED_ROOT = SELF_ACTUALIZE_ROOT / "promoted_live_roots" / "atlasforge_framework"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_atlasforge_runtime_lane"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_promoted_root() -> None:
    promoted_root_str = str(PROMOTED_ROOT)
    if promoted_root_str not in sys.path:
        sys.path.insert(0, promoted_root_str)


def run_check(label: str, fn) -> dict:
    try:
        details = fn()
        return {
            "label": label,
            "status": "OK",
            "details": details,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "label": label,
            "status": "FAIL",
            "details": str(exc),
        }


def verify_lane() -> dict:
    ensure_promoted_root()
    import atlasforge  # noqa: WPS433

    checks = []

    def import_check() -> dict:
        return {
            "version": getattr(atlasforge, "__version__", "<unknown>"),
            "package_root": str(PROMOTED_ROOT / "atlasforge"),
        }

    def symbol_export_check() -> dict:
        return {"symbol_count": len(getattr(atlasforge, "__all__", []))}

    def solver_check() -> dict:
        from atlasforge import BrentSolver, Interval  # noqa: WPS433

        solver = BrentSolver(tol=1e-12)
        result = solver.solve(lambda x: x**2 - 2, Interval.closed(1, 2))
        return {
            "solution": round(result.solution, 12),
            "target": round(math.sqrt(2), 12),
        }

    def lens_check() -> dict:
        from atlasforge import LogLens  # noqa: WPS433

        lens = LogLens()
        x = 10.0
        round_trip = lens.inverse(lens.forward(x))
        return {"round_trip_error": abs(round_trip - x)}

    def recipe_check() -> dict:
        from atlasforge import Blueprint, Interval, RecipeExecutor, RootConstraint  # noqa: WPS433

        constraint = RootConstraint(H=lambda x: x**2 - 2, domain=Interval.closed(1, 2))
        recipe = RecipeExecutor().execute(Blueprint(constraint=constraint))
        return {
            "success": bool(recipe.success),
            "steps": len(getattr(recipe, "steps", []) or []),
        }

    def crystal_check() -> dict:
        from atlasforge import CrystalSolver, Interval  # noqa: WPS433

        result = CrystalSolver(tolerance=1e-8, max_turns=100).solve(
            lambda x: x**2 - 2,
            x0=1.5,
            domain=Interval.closed(1, 2),
        )
        return {"turns": getattr(result, "turns", None)}

    for label, fn in [
        ("import", import_check),
        ("symbol_export", symbol_export_check),
        ("solver", solver_check),
        ("lens", lens_check),
        ("recipe", recipe_check),
        ("crystal", crystal_check),
    ]:
        checks.append(run_check(label, fn))

    failed = [check for check in checks if check["status"] != "OK"]
    truth = "OK" if not failed else "NEAR"

    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-09.q27.runtime",
        "derivation_command": DERIVATION_COMMAND,
        "promoted_root": str(PROMOTED_ROOT),
        "truth": truth,
        "checks": checks,
        "failed_checks": [check["label"] for check in failed],
        "lane_law": "narrow replay-safe import and solver lane only; excludes sqlite-backed memory cleanup paths",
    }


def main() -> int:
    payload = verify_lane()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote ATLAS FORGE runtime lane json: {OUTPUT_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from typing import Callable

from .rehydration_loop import RehydrationLoopRuntime
from .tse_circulation import TseCirculationRuntime
from .tse_helix_integrity import TseHelixIntegrityRuntime
from .tse_reentry import TseReentryRuntime

SIGNATURE_COMPAT_VERSION = "TSE.COST.CARRIER.SIGNATURE.COMPAT.1"


def _restore_wrapped_signature(fn: Callable, freevar_name: str) -> bool:
    """Expose the exact wrapped callable to inspect.signature.

    Cost Carrier composes by runtime wrapping rather than by replacing the
    underlying transaction ABI. Python's inspect.signature follows __wrapped__,
    so binding it to the captured pre-extension callable preserves the exact
    public transaction parameters while the additive carrier still executes.
    """
    names = tuple(getattr(fn, "__code__", None).co_freevars or ()) if getattr(fn, "__code__", None) else ()
    closure = tuple(getattr(fn, "__closure__", None) or ())
    for name, cell in zip(names, closure):
        if name != freevar_name:
            continue
        try:
            original = cell.cell_contents
        except ValueError:
            return False
        if not callable(original):
            return False
        fn.__wrapped__ = original
        return True
    return False


def install_tse_cost_carrier_signature_compat() -> None:
    if getattr(RehydrationLoopRuntime, "_athena_tse_cost_carrier_signature_compat_v1_registered", False):
        return

    targets = (
        (RehydrationLoopRuntime, "start", "original_loop_start"),
        (RehydrationLoopRuntime, "advance", "original_loop_advance"),
        (TseReentryRuntime, "start", "original_reentry_start"),
        (TseHelixIntegrityRuntime, "advance", "original_helix_advance"),
        (TseCirculationRuntime, "observe", "original_circulation_observe"),
        (TseCirculationRuntime, "report", "original_circulation_report"),
        (TseCirculationRuntime, "resource", "original_circulation_resource"),
    )
    failures = []
    for cls, method_name, freevar_name in targets:
        fn = getattr(cls, method_name)
        if not _restore_wrapped_signature(fn, freevar_name):
            failures.append(f"{cls.__name__}.{method_name}:{freevar_name}")

    if failures:
        raise RuntimeError("TSE cost carrier signature restoration failed: " + ",".join(failures))

    RehydrationLoopRuntime._athena_tse_cost_carrier_signature_compat_v1_registered = True

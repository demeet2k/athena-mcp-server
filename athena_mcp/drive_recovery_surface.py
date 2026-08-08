from __future__ import annotations

from typing import Any, Dict

from .drive_recovery_registry_v2 import DriveRecoveryRegistryRuntime
from .drive_recovery_protocol import RECOVERY_RESOURCE


class DriveRecoverySurface:
    def __init__(self):
        self.runtime = DriveRecoveryRegistryRuntime()

    def call_tool(self, name: str, args: Dict[str, Any]):
        if name == "athena_recovery_organs":
            return True, self.runtime.list(
                status=args.get("status"),
                family=args.get("family"),
                query=args.get("query"),
                limit=args.get("limit", 100),
            )
        if name == "athena_recovery_organ":
            return True, self.runtime.get(args["organ_id"])
        if name == "athena_recovery_holoaddress":
            return True, self.runtime.holoaddress(args["organ_id"])
        if name == "athena_recovery_frontier":
            return True, self.runtime.frontier(
                limit=args.get("limit", 10),
                include_theory=bool(args.get("include_theory", False)),
            )
        return False, None

    def read_resource(self, uri: str):
        if uri != RECOVERY_RESOURCE["uri"]:
            raise KeyError(uri)
        return {
            **self.runtime.describe(),
            "frontier": self.runtime.frontier(limit=10, include_theory=False)["frontier"],
        }

    def benchmark(self):
        state = self.runtime.describe()
        return {
            "drive_recovery_registry": {
                "version": state["version"],
                "organ_count": state["organ_count"],
                "revision_pinned_count": state["revision_pinned_count"],
                "formal_residual_issue": state["formal_residual_issue"],
            }
        }

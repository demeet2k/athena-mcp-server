from __future__ import annotations

from .tse_telemetry import TseHelixTelemetryRuntime


class TseHelixTelemetryProxy:
    """Late-bind TSE telemetry until Server has installed its GitBackend.

    Server constructs the AOR development surface before assigning `server.git`.
    Most existing transport organs defer Git access until tool execution. TSE
    telemetry follows the same constructor law through this transparent proxy,
    avoiding a global Server boot-order change.
    """

    def __init__(self, server):
        self.server = server
        self._runtime = None

    def _get(self):
        runtime = self._runtime
        if runtime is None:
            if not hasattr(self.server, "git"):
                raise RuntimeError("TSE_TELEMETRY_GIT_NOT_READY")
            runtime = TseHelixTelemetryRuntime(self.server)
            self._runtime = runtime
        return runtime

    def __getattr__(self, name):
        return getattr(self._get(), name)

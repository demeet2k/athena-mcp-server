from __future__ import annotations

from .tse_telemetry import TseHelixTelemetryRuntime


class TseHelixTelemetryProxy:
    """Late-bind TSE telemetry until Server has installed its GitBackend."""

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

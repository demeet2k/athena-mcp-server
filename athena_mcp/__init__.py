"""ATHENA canonical MCP package release identity.

`protocol.py` remains the mature schema registry. Package initialization owns the
release identity and patches the compatibility `protocol.SERVER_INFO` value
before dispatch or external submodule imports observe it.
"""

__version__ = "3.1.0"

from . import protocol as _protocol

SERVER_INFO = {
    "name": "athena-canonical-mcp",
    "version": __version__,
    "description": (
        "Canonical Collective V11 × KC144 developmental control with secure "
        "JSON-RPC HTTP hosting, digest-pinned OCI activation, canary rollback, "
        "adaptive probabilistic inference, causal sensitivity, and finite belief-state planning"
    ),
}

_protocol.SERVER_INFO = dict(SERVER_INFO)

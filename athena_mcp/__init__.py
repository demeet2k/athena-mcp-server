"""ATHENA canonical MCP package release identity.

`protocol.py` remains the mature schema registry. Package initialization owns the
release identity and patches the compatibility `protocol.SERVER_INFO` value
before dispatch or external submodule imports observe it. This avoids rewriting
the large schema registry for release-only metadata changes.
"""

__version__ = "3.2.0"

from . import protocol as _protocol

SERVER_INFO = {
    "name": "athena-canonical-mcp",
    "version": __version__,
    "description": "Canonical KC144/JSPACE/SCALE developmental control with QMC/FITC probabilistic inference, bounded FCI-lite and longitudinal policy inference, and correlated robust resource planning",
}

_protocol.SERVER_INFO = dict(SERVER_INFO)

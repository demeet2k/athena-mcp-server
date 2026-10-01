"""Current-master AOR transport body plus additive qualified TSE V4 forward port.

The exact current-master body is preserved byte-for-byte in
`_aor_collective_transport_surface_master_301547.py` and executed in this module
namespace so existing class/module identity remains stable. TSE integration is
installed only after that body has reconstructed current-master behavior.
"""

from pathlib import Path as _Path

_current_master_body = _Path(__file__).with_name(
    "_aor_collective_transport_surface_master_301547.py"
)
exec(
    compile(
        _current_master_body.read_text(encoding="utf-8"),
        str(_current_master_body),
        "exec",
    ),
    globals(),
    globals(),
)
del _current_master_body

from .tse_forward_port_adapter import install_tse_forward_port as _install_tse_forward_port

_install_tse_forward_port(globals())
del _install_tse_forward_port

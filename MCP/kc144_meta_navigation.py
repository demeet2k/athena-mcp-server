"""FastMCP registration adapter for the executable KC144 Meta-Compiler."""
from __future__ import annotations

import json
from typing import Any

from kc144_meta_runtime import dispatch, locate, map_payload, resolve, station, status

_REGISTERED: set[int] = set()


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_kc144_meta_navigation(mcp: Any) -> Any:
    identity = id(mcp)
    if identity in _REGISTERED:
        return mcp
    _REGISTERED.add(identity)

    @mcp.tool()
    def locate_kc144(query: str = "KC144 meta compiler") -> str:
        """Locate the executable KC144 compiler through the Athena mycelium."""
        return _dump(locate(query))

    @mcp.tool()
    def use_kc144(query: str, operation: str = "compile") -> str:
        """Invoke the located compiler and emit an M12-bound return receipt."""
        if operation == "compile":
            result = dispatch("compile", query=query)
        elif operation == "locate":
            result = dispatch("locate", query=query)
        else:
            result = dispatch(operation, query=query)
        return _dump(result)

    @mcp.tool()
    def kc144_station(address: str = "GID119") -> str:
        """Resolve a GID, grid address, or station code."""
        return _dump(station(resolve(address)))

    @mcp.tool()
    def kc144_route(source: str = "H06", target: str = "M12", objective: str = "preserve") -> str:
        """Route through KC144 without treating reachability as evidence."""
        return _dump(dispatch("route", source=source, target=target, objective=objective))

    @mcp.tool()
    def kc144_map(name: str = "map-of-maps") -> str:
        """Materialize one of the 37 executable KC144 navigation maps."""
        return _dump(map_payload(name))

    @mcp.tool()
    def kc144_status() -> str:
        """Return navigation readiness and the unchanged production boundary."""
        return _dump(status())

    @mcp.tool()
    def kc144_validate() -> str:
        """Validate coordinates, maps, locator, and H06-to-M12 return."""
        return _dump(dispatch("validate"))

    return mcp

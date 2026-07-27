"""Production-facing Streamable HTTP adapter for the Athena MCP runtime."""
from __future__ import annotations

import contextlib

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from athena_mcp_server import mcp
from http_security import MCPHTTPBoundary, deployment_health


async def healthz(_: Request) -> JSONResponse:
    status, body = deployment_health()
    return JSONResponse(body, status_code=status, headers={"Cache-Control": "no-store"})


@contextlib.asynccontextmanager
async def lifespan(_: Starlette):
    async with mcp.session_manager.run():
        yield


secured_mcp = MCPHTTPBoundary(mcp.streamable_http_app())
app = Starlette(
    routes=[
        Route("/healthz", healthz, methods=["GET"]),
        Mount("/", app=secured_mcp),
    ],
    lifespan=lifespan,
)

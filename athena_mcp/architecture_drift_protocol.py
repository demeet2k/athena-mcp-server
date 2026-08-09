# Architecture inventory/drift is intentionally resource-first. The existing
# athena_surface_audit tool is already a non-self-metering introspection path and
# embeds the drift certificate. Adding redundant MCP tools here would create a
# second introspection call path that dispatch could meter into learning state.
ARCHITECTURE_DRIFT_TOOLS=[]
ARCHITECTURE_DRIFT_TOOL_NAMES=set()
ARCHITECTURE_DRIFT_RESOURCES=[
    {'uri':'athena://architecture/inventory','name':'ATHENA Mature Organ Inventory','mimeType':'application/json'},
    {'uri':'athena://architecture/drift','name':'ATHENA Architecture Drift Audit','mimeType':'application/json'},
]
ARCHITECTURE_DRIFT_RESOURCE_URIS={row['uri'] for row in ARCHITECTURE_DRIFT_RESOURCES}

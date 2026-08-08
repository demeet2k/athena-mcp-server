SURFACE_TOOLS=[
 {"name":"athena_surface_audit","description":"Audit the promoted runtime's discovered tool/resource surface against the canonical mature-organ contract.","inputSchema":{"type":"object","additionalProperties":False}}
]
SURFACE_TOOL_NAMES={tool['name'] for tool in SURFACE_TOOLS}
SURFACE_RESOURCE={"uri":"athena://surface","name":"ATHENA Mature Runtime Surface Contract","mimeType":"application/json"}

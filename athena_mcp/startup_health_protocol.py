STARTUP_HEALTH_TOOLS=[
 {'name':'athena_startup_health','description':'Return ATHENA.STARTUP.1 local readiness: mature surface, composition, schema currency and optional SELFTEST replay health. Reads remain allowed while degraded; this tool does not silently change mutation semantics.','inputSchema':{'type':'object','properties':{'run_replay_samples':{'type':'boolean'}},'additionalProperties':False}},
]
STARTUP_HEALTH_TOOL_NAMES={tool['name'] for tool in STARTUP_HEALTH_TOOLS}
STARTUP_HEALTH_RESOURCE={'uri':'athena://startup-health','name':'ATHENA.STARTUP.1 Runtime Readiness','mimeType':'application/json'}

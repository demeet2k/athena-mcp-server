UNIFIED_MANIFEST_TOOLS=[
 {'name':'athena_runtime_manifest','description':'Return the live ATHENA.RUNTIME.UNIFIED.1 architecture manifest derived from the running Server, schema/startup state, Collective/AOR organs, unresolved semantics and exact Git status.','inputSchema':{'type':'object','additionalProperties':False}},
 {'name':'athena_maxdev_law','description':'Return the canonical unified MAXDEV execution law covering RECON/Omega, memory firewall, SX/RAG/HUG/GAP/FIELD, measurement/Y/AOR/Collective, execution/test/learning, CAS/replay/self-test/promotion and continuation.','inputSchema':{'type':'object','additionalProperties':False}},
]
UNIFIED_MANIFEST_TOOL_NAMES={tool['name'] for tool in UNIFIED_MANIFEST_TOOLS}
UNIFIED_MANIFEST_RESOURCES=[
 {'uri':'athena://runtime/unified-manifest','name':'ATHENA Unified Runtime Manifest','mimeType':'application/json'},
 {'uri':'athena://runtime/maxdev','name':'ATHENA Unified MAXDEV Law','mimeType':'text/plain'},
]
UNIFIED_MANIFEST_RESOURCE_URIS={resource['uri'] for resource in UNIFIED_MANIFEST_RESOURCES}

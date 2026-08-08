SURFACE_TOOLS=[
 {'name':'athena_surface_audit','description':'Audit the promoted unified runtime against the complete mature tool/resource contract and executable composition certificate. Missing mature surfaces or organ/probe failures return FAIL.','inputSchema':{'type':'object','properties':{'run_probes':{'type':'boolean'}},'additionalProperties':False}},
]
SURFACE_TOOL_NAMES={tool['name'] for tool in SURFACE_TOOLS}
SURFACE_RESOURCE={'uri':'athena://surface','name':'ATHENA Unified Mature Surface + Composition Certificate','mimeType':'application/json'}

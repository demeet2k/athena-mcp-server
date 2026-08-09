ARCHITECTURE_DRIFT_TOOLS=[
    {
        'name':'athena_organ_inventory',
        'description':'Return the explicit mature-organ inventory. Maturity is declared; it is never inferred from file existence or extra MCP registration.',
        'inputSchema':{'type':'object','properties':{},'additionalProperties':False},
    },
    {
        'name':'athena_architecture_drift_audit',
        'description':'Audit declared mature organs against the live MCP surface, SURFACE contract, live manifest, OMEGA projection, and optionally repository CI/path witnesses. Unclassified extras are reported as expansion pressure, not silently promoted to maturity.',
        'inputSchema':{
            'type':'object',
            'properties':{
                'include_repository_witnesses':{'type':'boolean'},
            },
            'additionalProperties':False,
        },
    },
]
ARCHITECTURE_DRIFT_TOOL_NAMES={tool['name'] for tool in ARCHITECTURE_DRIFT_TOOLS}
ARCHITECTURE_DRIFT_RESOURCES=[
    {'uri':'athena://architecture/inventory','name':'ATHENA Mature Organ Inventory','mimeType':'application/json'},
    {'uri':'athena://architecture/drift','name':'ATHENA Architecture Drift Audit','mimeType':'application/json'},
]
ARCHITECTURE_DRIFT_RESOURCE_URIS={row['uri'] for row in ARCHITECTURE_DRIFT_RESOURCES}

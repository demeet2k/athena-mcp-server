SELF_TEST_TOOLS=[
 {'name':'athena_self_test','description':'Run the read-only ATHENA.SELFTEST.1 local health synthesis: SURFACE.2, COMPOSITION.2, schema migration health, Ω projection and deterministic replay samples. PASS does not substitute for external CI/smoke attestations or semantic proof.','inputSchema':{'type':'object','properties':{'replay_limit':{'type':'integer','minimum':1,'maximum':50},'run_composition_probes':{'type':'boolean'}},'additionalProperties':False}},
]
SELF_TEST_TOOL_NAMES={tool['name'] for tool in SELF_TEST_TOOLS}
SELF_TEST_RESOURCE={'uri':'athena://self-test','name':'ATHENA.SELFTEST.1 Local Organism Health','mimeType':'application/json'}

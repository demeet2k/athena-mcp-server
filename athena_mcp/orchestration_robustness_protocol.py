ROBUSTNESS_TOOLS=[
 {'name':'athena_orchestration_robustness','description':'Compute successor rank sensitivity for one persisted orchestration run.','inputSchema':{'type':'object','required':['run_id'],'properties':{'run_id':{'type':'string','minLength':1},'relative_perturbation':{'type':'number','minimum':0,'exclusiveMaximum':1}},'additionalProperties':False}}
]
ROBUSTNESS_TOOL_NAMES={tool['name'] for tool in ROBUSTNESS_TOOLS}
ROBUSTNESS_RESOURCE={'uri':'athena://orchestration/robustness','name':'AOR Successor Robustness Law','mimeType':'application/json'}

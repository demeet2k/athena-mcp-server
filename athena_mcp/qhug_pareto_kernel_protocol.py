PATCH_SCHEMA={
 'type':'object','required':['id'],'properties':{
  'id':{'type':'string','minLength':1},'value':{'type':'number'},'proof_cost':{'type':'number','minimum':0},'governance':{'type':'number','minimum':0}
 },'additionalProperties':False
}
DEPENDENCY_SCHEMA={
 'type':'object','required':['patch','alternatives'],'properties':{
  'patch':{'type':'string','minLength':1},
  'alternatives':{'type':'array','minItems':1,'items':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True}}
 },'additionalProperties':False
}
BASE_PROPERTIES={
 'patches':{'type':'array','minItems':1,'items':PATCH_SCHEMA},
 'invalid':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
 'conflicts':{'type':'array','items':{'type':'array','minItems':2,'maxItems':2,'items':{'type':'string','minLength':1}}},
 'dependencies':{'type':'array','items':DEPENDENCY_SCHEMA},
 'neutral_excluded':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
}
QHUG_PARETO_KERNEL_TOOLS=[
 {'name':'athena_qhug_kernel_analyze','description':'Analyze a Boolean QHUG patch kernel into exact primal-graph components and structural-free coordinates. No optimization is invented.','inputSchema':{'type':'object','required':['patches'],'properties':BASE_PROPERTIES,'additionalProperties':False}},
 {'name':'athena_qhug_pareto_solve','description':'Exactly solve a supported disconnected Boolean QHUG kernel by local component enumeration plus Pareto-pruned Minkowski convolution; preserves every scalar-policy tie.','inputSchema':{'type':'object','required':['patches'],'properties':{**BASE_PROPERTIES,
   'mode':{'type':'string','enum':['governed','neutral']},
   'max_component_size':{'type':'integer','minimum':1,'maximum':24},
   'policy':{'type':'object','properties':{
      'lambda_patch':{'type':'number','minimum':0},'mu_proof_cost':{'type':'number','minimum':0},'nu_governance':{'type':'number','minimum':0}
    },'additionalProperties':False}
 },'additionalProperties':False}},
 {'name':'athena_qhug_decomposition_verify','description':'Verify a supplied tree decomposition against QHUG conflict/dependency factor scopes; certify factor coverage, running intersection, width upper bound, and an exact treewidth value when a matching clique lower bound is present.','inputSchema':{'type':'object','required':['patches','bags'],'properties':{**BASE_PROPERTIES,
   'bags':{'type':'array','minItems':1,'items':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True}},
   'bag_edges':{'type':'array','items':{'type':'array','minItems':2,'maxItems':2,'items':{'type':'integer','minimum':0}}}
 },'additionalProperties':False}}
]
QHUG_PARETO_KERNEL_TOOL_NAMES={tool['name'] for tool in QHUG_PARETO_KERNEL_TOOLS}
QHUG_PARETO_KERNEL_RESOURCE={
 'uri':'athena://qhug/pareto-kernel/v23.2',
 'name':'QHUG Pareto Kernel V23.2',
 'mimeType':'application/json'
}

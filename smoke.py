import json, math, os, subprocess, sys, tempfile
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
tmle_rows=[]
for i in range(160):
 x=((i*17)%101)/100.0-.5; t=1 if i%4 in (1,2) else 0; py=max(.05,min(.95,.15+.50*t+.08*x)); y=1 if ((i*37)%100)/100.0<py else 0
 tmle_rows.append({'T':t,'Y':y,'X':x})
pomdp_actions=[
 {'id':'act','reward_by_state':{'G':1.0,'B':0.0},'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},'observation':{'G':{'n':1.0},'B':{'n':1.0}}},
 {'id':'sense','reward_by_state':{'G':0.0,'B':0.0},'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},'observation':{'G':{'g':.9,'b':.1},'B':{'g':.1,'b':.9}}},
]
msgs=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://manifest'}},
 {'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':'athena://collective/v8'}},
 {'jsonrpc':'2.0','id':5,'method':'resources/read','params':{'uri':'athena://collective/v9'}},
 {'jsonrpc':'2.0','id':6,'method':'resources/read','params':{'uri':'athena://collective/v10'}},
 {'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'athena_gaussian_belief_register','arguments':{'context_key':'SMOKE_GAUSS','parameters':['theta'],'mean':{'theta':0},'prior_variance':4.0,'noise_variance':.25}}},
 {'jsonrpc':'2.0','id':8,'method':'tools/call','params':{'name':'athena_gaussian_belief_observe','arguments':{'context_key':'SMOKE_GAUSS','features':{'theta':1},'target':1.5,'evidence_ref':'smoke://continuous'}}},
 {'jsonrpc':'2.0','id':9,'method':'tools/call','params':{'name':'athena_decision_evsi','arguments':{'context_key':'SMOKE_GAUSS','actions':[{'id':'plus','utility_linear':{'theta':1}},{'id':'minus','utility_linear':{'theta':-1}}],'experiments':[{'id':'measure','design':{'theta':1},'noise_variance':.1}],'samples':80,'seed':8,'cost_weight':0,'risk_weight':0}}},
 {'jsonrpc':'2.0','id':10,'method':'tools/call','params':{'name':'athena_gp_register','arguments':{'context_key':'SMOKE_GP','features':['x'],'length_scale':.6,'signal_variance':1.0,'noise_variance':.01}}},
 {'jsonrpc':'2.0','id':11,'method':'tools/call','params':{'name':'athena_gp_observe','arguments':{'context_key':'SMOKE_GP','features':{'x':0.0},'target':0.0,'evidence_ref':'smoke://gp0'}}},
 {'jsonrpc':'2.0','id':12,'method':'tools/call','params':{'name':'athena_gp_observe','arguments':{'context_key':'SMOKE_GP','features':{'x':1.0},'target':1.0,'evidence_ref':'smoke://gp1'}}},
 {'jsonrpc':'2.0','id':13,'method':'tools/call','params':{'name':'athena_gp_predict','arguments':{'context_key':'SMOKE_GP','features':{'x':1.0},'include_observation_noise':False}}},
 {'jsonrpc':'2.0','id':14,'method':'tools/call','params':{'name':'athena_causal_tmle_binary','arguments':{'samples':tmle_rows,'treatment':'T','outcome':'Y','adjustment':['X'],'propensity_clip':.05}}},
 {'jsonrpc':'2.0','id':15,'method':'tools/call','params':{'name':'athena_sensitivity_evalue','arguments':{'risk_ratio':2.0,'ci_limit':1.5}}},
 {'jsonrpc':'2.0','id':16,'method':'tools/call','params':{'name':'athena_pomdp_solve','arguments':{'states':['G','B'],'initial_belief':{'G':.5,'B':.5},'actions':pomdp_actions,'horizon':2,'discount':.95,'max_nodes':5000}}},
 {'jsonrpc':'2.0','id':17,'method':'tools/call','params':{'name':'athena_finalize_output','arguments':{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}}}}
]
for m in msgs:p.stdin.write(json.dumps(m)+'\n')
p.stdin.flush()
responses=[]
for _ in range(17):
 r=json.loads(p.stdout.readline()); assert r.get('error') is None,r; responses.append(r)
init=responses[0]['result']; assert init['serverInfo']['version']=='2.9.0',init
names={x['name'] for x in responses[1]['result']['tools']}
for n in ('athena_gaussian_belief_register','athena_decision_evsi','athena_gp_register','athena_gp_observe','athena_gp_predict','athena_pc_stable_discover','athena_causal_tmle_binary','athena_sensitivity_evalue','athena_pomdp_solve','athena_evidence_dependence_fit'): assert n in names,n
v8=json.loads(responses[3]['result']['contents'][0]['text']); assert v8['runtime']['version']=='COLLECTIVE_RUNTIME_V8',v8
v9=json.loads(responses[4]['result']['contents'][0]['text']); assert v9['runtime']['version']=='COLLECTIVE_RUNTIME_V9',v9
v10=json.loads(responses[5]['result']['contents'][0]['text']); assert v10['runtime']['version']=='COLLECTIVE_RUNTIME_V10',v10
gauss=responses[7]['result']['structuredContent']; assert gauss['status']=='GAUSSIAN_LINEAR_BELIEF' and gauss['observation_count']==1,gauss
evsi=responses[8]['result']['structuredContent']; assert evsi['decision']=='MONTE_CARLO_EVSI_DESIGN_ONLY',evsi
gp=responses[12]['result']['structuredContent']; assert gp['status']=='GP_POSTERIOR_PREDICTION' and gp['mean']>.8 and gp['observation_count']==2,gp
tmle=responses[13]['result']['structuredContent']; assert tmle['status']=='TMLE_BINARY_ESTIMATED_UNDER_ASSUMPTIONS' and tmle['standard_error']>=0,tmle
ev=responses[14]['result']['structuredContent']; assert ev['status']=='E_VALUE_SENSITIVITY_METRIC' and abs(ev['evalue_point']-(2+math.sqrt(2)))<1e-6,ev
pomdp=responses[15]['result']['structuredContent']; assert pomdp['status']=='FINITE_POMDP_EXACT_HORIZON_CERTIFIED' and pomdp['certificate']=='EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON',pomdp
em=responses[16]['result']['structuredContent']; assert em['envelope_id'].startswith('ENV.'); assert em['emission_mid'].startswith('MID.'); assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.'); assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
p.stdin.write(json.dumps({'jsonrpc':'2.0','id':18,'method':'tools/call','params':{'name':'athena_verify_emission','arguments':{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']}}})+'\n');p.stdin.flush();v=json.loads(p.stdout.readline());assert v['result']['structuredContent']['verified'] is True
p.terminate(); print('SMOKE PASS: V10 GP/TMLE/POMDP + V9 INFERENCE + FINALIZE_OUTPUT + VERIFY_EMISSION')

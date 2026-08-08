import json, os, subprocess, sys, tempfile
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
aipw_rows=[]
for i in range(80):
 z=((i*13)%37)/36.0; t=1 if i%4 in (1,2) else 0; y=2.0*t+1.5*z+((i%5)-2)*.01
 aipw_rows.append({'T':t,'Y':y,'Z':z})
msgs=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://manifest'}},
 {'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':'athena://collective/v7'}},
 {'jsonrpc':'2.0','id':5,'method':'resources/read','params':{'uri':'athena://collective/v8'}},
 {'jsonrpc':'2.0','id':6,'method':'resources/read','params':{'uri':'athena://collective/v9'}},
 {'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'athena_belief_register','arguments':{'context_key':'SMOKE_FINITE','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]}}},
 {'jsonrpc':'2.0','id':8,'method':'tools/call','params':{'name':'athena_belief_observe','arguments':{'context_key':'SMOKE_FINITE','outcome':'positive','likelihoods':{'M1':.9,'M2':.1},'evidence_ref':'smoke://finite'}}},
 {'jsonrpc':'2.0','id':9,'method':'tools/call','params':{'name':'athena_decision_evi','arguments':{'context_key':'SMOKE_FINITE','actions':[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}],'experiments':[{'id':'strong','outcomes':{'yes':{'M1':.95,'M2':.05},'no':{'M1':.05,'M2':.95}}}]}}},
 {'jsonrpc':'2.0','id':10,'method':'tools/call','params':{'name':'athena_gaussian_belief_register','arguments':{'context_key':'SMOKE_GAUSS','parameters':['theta'],'mean':{'theta':0},'prior_variance':4.0,'noise_variance':.25}}},
 {'jsonrpc':'2.0','id':11,'method':'tools/call','params':{'name':'athena_gaussian_belief_observe','arguments':{'context_key':'SMOKE_GAUSS','features':{'theta':1},'target':1.5,'evidence_ref':'smoke://continuous'}}},
 {'jsonrpc':'2.0','id':12,'method':'tools/call','params':{'name':'athena_decision_evpi','arguments':{'context_key':'SMOKE_GAUSS','actions':[{'id':'plus','utility_linear':{'theta':1}},{'id':'minus','utility_linear':{'theta':-1}}],'samples':80,'seed':7}}},
 {'jsonrpc':'2.0','id':13,'method':'tools/call','params':{'name':'athena_decision_evsi','arguments':{'context_key':'SMOKE_GAUSS','actions':[{'id':'plus','utility_linear':{'theta':1}},{'id':'minus','utility_linear':{'theta':-1}}],'experiments':[{'id':'measure','design':{'theta':1},'noise_variance':.1}],'samples':80,'seed':8,'cost_weight':0,'risk_weight':0}}},
 {'jsonrpc':'2.0','id':14,'method':'tools/call','params':{'name':'athena_causal_aipw','arguments':{'samples':aipw_rows,'treatment':'T','outcome':'Y','adjustment':['Z']}}},
 {'jsonrpc':'2.0','id':15,'method':'tools/call','params':{'name':'athena_finalize_output','arguments':{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}}}}
]
for m in msgs:p.stdin.write(json.dumps(m)+'\n')
p.stdin.flush()
responses=[]
for _ in range(15):
 r=json.loads(p.stdout.readline()); assert r.get('error') is None,r; responses.append(r)
init=responses[0]['result']; assert init['serverInfo']['version']=='2.8.0',init
names={x['name'] for x in responses[1]['result']['tools']}
for n in ('athena_belief_register','athena_decision_evi','athena_gaussian_belief_register','athena_gaussian_belief_observe','athena_decision_evpi','athena_decision_evsi','athena_belief_policy_multistage','athena_causal_aipw','athena_structure_partial','athena_evidence_dependence_probability'): assert n in names,n
v7=json.loads(responses[3]['result']['contents'][0]['text']); assert v7['runtime']['version']=='COLLECTIVE_RUNTIME_V7',v7
v8=json.loads(responses[4]['result']['contents'][0]['text']); assert v8['runtime']['version']=='COLLECTIVE_RUNTIME_V8',v8
v9=json.loads(responses[5]['result']['contents'][0]['text']); assert v9['runtime']['version']=='COLLECTIVE_RUNTIME_V9',v9
finite=responses[7]['result']['structuredContent']; assert finite['status']=='BELIEF_STATE' and finite['information_gain_bits']>0,finite
evi=responses[8]['result']['structuredContent']; assert evi['decision']=='DESIGN_ONLY' and evi['winner']=='strong',evi
gauss=responses[10]['result']['structuredContent']; assert gauss['status']=='GAUSSIAN_LINEAR_BELIEF' and gauss['observation_count']==1,gauss
evpi=responses[11]['result']['structuredContent']; assert evpi['status']=='MONTE_CARLO_EVPI_ESTIMATE',evpi
evsi=responses[12]['result']['structuredContent']; assert evsi['decision']=='MONTE_CARLO_EVSI_DESIGN_ONLY',evsi
aipw=responses[13]['result']['structuredContent']; assert aipw['status']=='AIPW_CROSS_FIT_ESTIMATE' and abs(aipw['estimate']-2.0)<.3,aipw
em=responses[14]['result']['structuredContent']; assert em['envelope_id'].startswith('ENV.'); assert em['emission_mid'].startswith('MID.'); assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.'); assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
p.stdin.write(json.dumps({'jsonrpc':'2.0','id':16,'method':'tools/call','params':{'name':'athena_verify_emission','arguments':{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']}}})+'\n');p.stdin.flush();v=json.loads(p.stdout.readline());assert v['result']['structuredContent']['verified'] is True
p.terminate(); print('SMOKE PASS: V9 CONTINUOUS INFERENCE + V8 BELIEF + FINALIZE_OUTPUT + VERIFY_EMISSION')

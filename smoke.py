import json, math, os, subprocess, sys, tempfile
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
tmle_rows=[]
for i in range(160):
 x=((i*17)%101)/100.0-.5; t=1 if i%4 in (1,2) else 0; py=max(.05,min(.95,.15+.50*t+.08*x*x)); y=1 if ((i*37)%100)/100.0<py else 0
 tmle_rows.append({'T':t,'Y':y,'X':x})
def ba_actions(model):
 if model=='M1': probe={'x':.9,'y':.1}; left=.6; right=0.0
 else: probe={'x':.1,'y':.9}; left=0.0; right=.6
 return [
  {'id':'left','reward_by_state':{'S':left},'transition':{'S':{'S':1.0}},'observation':{'S':{'n':1.0}}},
  {'id':'right','reward_by_state':{'S':right},'transition':{'S':{'S':1.0}},'observation':{'S':{'n':1.0}}},
  {'id':'probe','reward_by_state':{'S':0.0},'transition':{'S':{'S':1.0}},'observation':{'S':probe}},
 ]
msgs=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://manifest'}},
 {'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':'athena://collective/v9'}},
 {'jsonrpc':'2.0','id':5,'method':'resources/read','params':{'uri':'athena://collective/v10'}},
 {'jsonrpc':'2.0','id':6,'method':'resources/read','params':{'uri':'athena://collective/v11'}},
 {'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'athena_gp_register','arguments':{'context_key':'SMOKE_GP','features':['x'],'length_scale':1.5,'signal_variance':.5,'noise_variance':.05}}},
 {'jsonrpc':'2.0','id':8,'method':'tools/call','params':{'name':'athena_gp_observe','arguments':{'context_key':'SMOKE_GP','features':{'x':0.0},'target':0.0,'evidence_ref':'smoke://gp0'}}},
 {'jsonrpc':'2.0','id':9,'method':'tools/call','params':{'name':'athena_gp_observe','arguments':{'context_key':'SMOKE_GP','features':{'x':.5},'target':.25,'evidence_ref':'smoke://gp05'}}},
 {'jsonrpc':'2.0','id':10,'method':'tools/call','params':{'name':'athena_gp_observe','arguments':{'context_key':'SMOKE_GP','features':{'x':1.0},'target':1.0,'evidence_ref':'smoke://gp1'}}},
 {'jsonrpc':'2.0','id':11,'method':'tools/call','params':{'name':'athena_gp_hyperfit','arguments':{'context_key':'SMOKE_GP','length_scales':[.25,.5,1.0],'signal_variances':[.5,1.0],'noise_variances':[.01,.05]}}},
 {'jsonrpc':'2.0','id':12,'method':'tools/call','params':{'name':'athena_gp_decision_evsi','arguments':{'context_key':'SMOKE_GP','actions':[{'id':'left','features':{'x':.2}},{'id':'right','features':{'x':.8}}],'experiments':[{'id':'middle','features':{'x':.5},'noise_variance':.01},{'id':'edge','features':{'x':.9},'noise_variance':.01}],'samples':80,'seed':5,'cost_weight':0,'risk_weight':0}}},
 {'jsonrpc':'2.0','id':13,'method':'tools/call','params':{'name':'athena_latent_project_admg','arguments':{'edges':[{'src':'U','dst':'X'},{'src':'U','dst':'Y'},{'src':'X','dst':'Z'}],'latent_nodes':['U'],'observed_nodes':['X','Y','Z']}}},
 {'jsonrpc':'2.0','id':14,'method':'tools/call','params':{'name':'athena_causal_tmle_ensemble','arguments':{'samples':tmle_rows,'treatment':'T','outcome':'Y','adjustment':['X'],'propensity_clip':.05}}},
 {'jsonrpc':'2.0','id':15,'method':'tools/call','params':{'name':'athena_sensitivity_rr_surface','arguments':{'observed_rr':2.0,'exposure_confounder_rrs':[1.0,2.0,3.5],'outcome_confounder_rrs':[1.0,2.0,3.5]}}},
 {'jsonrpc':'2.0','id':16,'method':'tools/call','params':{'name':'athena_bapomdp_solve','arguments':{'states':['S'],'initial_state_belief':{'S':1.0},'models':[{'id':'M1','prior':.5,'actions':ba_actions('M1')},{'id':'M2','prior':.5,'actions':ba_actions('M2')}],'horizon':3,'discount':.95,'max_nodes':100000}}},
 {'jsonrpc':'2.0','id':17,'method':'tools/call','params':{'name':'athena_finalize_output','arguments':{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}}}}
]
for m in msgs:p.stdin.write(json.dumps(m)+'\n')
p.stdin.flush()
responses=[]
for _ in range(17):
 r=json.loads(p.stdout.readline()); assert r.get('error') is None,r; responses.append(r)
init=responses[0]['result']; assert init['serverInfo']['version']=='3.0.0',init
names={x['name'] for x in responses[1]['result']['tools']}
for n in ('athena_gp_register','athena_gp_hyperfit','athena_gp_decision_evsi','athena_latent_project_admg','athena_causal_tmle_ensemble','athena_sensitivity_rr_surface','athena_bapomdp_solve','athena_evidence_dependence_interval'): assert n in names,n
v9=json.loads(responses[3]['result']['contents'][0]['text']); assert v9['runtime']['version']=='COLLECTIVE_RUNTIME_V9',v9
v10=json.loads(responses[4]['result']['contents'][0]['text']); assert v10['runtime']['version']=='COLLECTIVE_RUNTIME_V10',v10
v11=json.loads(responses[5]['result']['contents'][0]['text']); assert v11['runtime']['version']=='COLLECTIVE_RUNTIME_V11',v11
fit=responses[10]['result']['structuredContent']; assert fit['status']=='GP_HYPERPARAMETER_DESIGN_ONLY' and fit['candidate_count']>0,fit
gpevsi=responses[11]['result']['structuredContent']; assert gpevsi['decision']=='GP_DECISION_EVSI_DESIGN_ONLY' and len(gpevsi['ranked'])==2,gpevsi
latent=responses[12]['result']['structuredContent']; assert latent['status']=='RESTRICTED_LATENT_PROJECTION_ADMG' and any(e['a']=='X' and e['b']=='Y' for e in latent['bidirected_edges']),latent
tmle=responses[13]['result']['structuredContent']; assert tmle['status']=='TMLE_STACKED_ENSEMBLE_ESTIMATED_UNDER_ASSUMPTIONS' and tmle['standard_error']>=0,tmle
sens=responses[14]['result']['structuredContent']; assert sens['status']=='RR_BIAS_FACTOR_SENSITIVITY_SURFACE' and sens['minimum_grid_explain_away'] is not None,sens
ba=responses[15]['result']['structuredContent']; assert ba['status']=='FINITE_MODEL_BAYES_ADAPTIVE_POMDP_EXACT_HORIZON_CERTIFIED' and ba['certificate']=='EXACT_FOR_SUPPLIED_STATIC_MODEL_SET_STATE_SPACE_ACTIONS_OBSERVATIONS_AND_HORIZON',ba
em=responses[16]['result']['structuredContent']; assert em['envelope_id'].startswith('ENV.'); assert em['emission_mid'].startswith('MID.'); assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.'); assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
p.stdin.write(json.dumps({'jsonrpc':'2.0','id':18,'method':'tools/call','params':{'name':'athena_verify_emission','arguments':{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']}}})+'\n');p.stdin.flush();v=json.loads(p.stdout.readline());assert v['result']['structuredContent']['verified'] is True
p.terminate(); print('SMOKE PASS: V11 ADAPTIVE GP/LATENT/TMLE/BAPOMDP + FINALIZE_OUTPUT + VERIFY_EMISSION')

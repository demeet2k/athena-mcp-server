import json, os, subprocess, sys, tempfile
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
msgs=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://manifest'}},
 {'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':'athena://collective/v5'}},
 {'jsonrpc':'2.0','id':5,'method':'resources/read','params':{'uri':'athena://collective/v6'}},
 {'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'athena_experiment_design','arguments':{
   'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],
   'experiments':[{'id':'E1','positive_probability':{'H1':.9,'H2':.1},'ethical':True,'cost':.1,'risk':.1}],
   'sample_size':10
 }}},
 {'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'athena_bayes_predict','arguments':{'features':{'uncertainty':.8},'regime':'SMOKE','arm_id':'A'}}},
 {'jsonrpc':'2.0','id':8,'method':'tools/call','params':{'name':'athena_experiment_generate','arguments':{
   'hypotheses':[{'id':'H1','prior':.5,'base_p':.5,'factor_effects':{'dose=high':.4}},{'id':'H2','prior':.5,'base_p':.5,'factor_effects':{'dose=high':-.4}}],
   'factors':[{'name':'dose','levels':['low','high']}], 'sample_size':10
 }}},
 {'jsonrpc':'2.0','id':9,'method':'tools/call','params':{'name':'athena_causal_identify','arguments':{
   'treatment':'T','outcome':'Y','edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],'observed_nodes':['T','Y','Z']
 }}},
 {'jsonrpc':'2.0','id':10,'method':'tools/call','params':{'name':'athena_finalize_output','arguments':{
   'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,
   'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],
   'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}
 }}}
]
for m in msgs:p.stdin.write(json.dumps(m)+'\n')
p.stdin.flush()
responses=[]
for _ in range(10):
 r=json.loads(p.stdout.readline()); assert r.get('error') is None,r; responses.append(r)
init=responses[0]['result']; assert init['serverInfo']['version']=='2.5.0',init
names={x['name'] for x in responses[1]['result']['tools']}
for n in ('athena_bayes_predict','athena_experiment_design','athena_projection_compensate','athena_ood_score','athena_experiment_generate','athena_causal_identify','athena_mpc_plan','athena_schedule_certified','athena_claim_state'): assert n in names,n
v5=json.loads(responses[3]['result']['contents'][0]['text']); assert v5['runtime']['version']=='COLLECTIVE_RUNTIME_V5',v5
v6=json.loads(responses[4]['result']['contents'][0]['text']); assert v6['runtime']['version']=='COLLECTIVE_RUNTIME_V6',v6
design=responses[5]['result']['structuredContent']; assert design['decision']=='DESIGN_ONLY' and design['winner']=='E1',design
bayes=responses[6]['result']['structuredContent']; assert 'posterior_covariance' in bayes and bayes['n']==0,bayes
generated=responses[7]['result']['structuredContent']; assert generated['decision']=='DESIGN_ONLY' and generated['generated_count']==2 and generated['winner'] is not None,generated
causal=responses[8]['result']['structuredContent']; assert causal['status']=='IDENTIFIED_BACKDOOR' and ['Z'] in causal['minimal_adjustment_sets'],causal
em=responses[9]['result']['structuredContent']; assert em['envelope_id'].startswith('ENV.'); assert em['emission_mid'].startswith('MID.'); assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.'); assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
p.stdin.write(json.dumps({'jsonrpc':'2.0','id':11,'method':'tools/call','params':{'name':'athena_verify_emission','arguments':{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']}}})+'\n');p.stdin.flush();v=json.loads(p.stdout.readline());assert v['result']['structuredContent']['verified'] is True
p.terminate(); print('SMOKE PASS: V6 ACTIVE DISCOVERY + V5 SCIENCE + FINALIZE_OUTPUT + VERIFY_EMISSION')

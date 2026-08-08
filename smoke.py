import json, os, subprocess, sys, tempfile

fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)

def rpc(method,params=None,request_id=1):
    msg={'jsonrpc':'2.0','id':request_id,'method':method}
    if params is not None:msg['params']=params
    p.stdin.write(json.dumps(msg)+'\n');p.stdin.flush();r=json.loads(p.stdout.readline());assert r.get('error') is None,r;return r['result']

def call(name,args,request_id):
    result=rpc('tools/call',{'name':name,'arguments':args},request_id);assert result.get('isError') is not True,result;return result['structuredContent']

def resource(uri,request_id):return json.loads(rpc('resources/read',{'uri':uri},request_id)['contents'][0]['text'])

init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'6'}},1);assert init['serverInfo']['version']=='2.9.0',init
p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
tools=rpc('tools/list',{},2)['tools'];names={x['name'] for x in tools}
for n in ('athena_orchestrate','athena_cycle_start','athena_self_test','athena_schema_migrate','athena_experiment_design','athena_causal_identify','athena_dual_control_plan','athena_belief_register','athena_decision_evi','athena_gaussian_belief_register','athena_decision_evpi','athena_structure_partial','athena_gp_register','athena_gp_predict','athena_pc_stable_discover','athena_causal_tmle_binary','athena_pomdp_solve','athena_gp_hyperfit','athena_gp_decision_evsi','athena_latent_project_admg','athena_bapomdp_solve','athena_discovery_claim_register','athena_claim_register','athena_finalize_output'):
    assert n in names,n
manifest=resource('athena://manifest',3);assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.6',manifest
for layer in ('COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11','AOR_DECISION_CORTEX'):assert layer in manifest['layers'],layer
v6=resource('athena://collective/v6',4);assert v6['runtime']['version']=='COLLECTIVE_RUNTIME_V6',v6;assert v6['claim_namespace']['discovery_shadow_prefix']=='athena_discovery_claim_'
v8=resource('athena://collective/v8',5);assert v8['runtime']['version']=='COLLECTIVE_RUNTIME_V8',v8
v9=resource('athena://collective/v9',6);assert v9['runtime']['version']=='COLLECTIVE_RUNTIME_V9',v9
v10=resource('athena://collective/v10',7);assert v10['runtime']['version']=='COLLECTIVE_RUNTIME_V10',v10
v11=resource('athena://collective/v11',8);assert v11['runtime']['version']=='COLLECTIVE_RUNTIME_V11',v11;assert 'Y1 authority' in v11['boundary']
migration=call('athena_schema_migrate',{},9);assert migration['status'] in {'APPLIED','UP_TO_DATE'},migration
health=call('athena_self_test',{'replay_limit':5},10);assert health['status']=='PASS',health
aor=call('athena_orchestrate',{'seed':'SMOKE','candidates':[]},11);assert aor['run_id'].startswith('AORRUN.'),aor;assert aor['next'] is None
cycle=call('athena_cycle_start',{'task_ref':'task://smoke','seed':'SMOKE','config':{'require_hug':True}},12);assert cycle['cycle_id'].startswith('CYCLE.'),cycle
waiting=call('athena_cycle_advance',{'cycle_id':cycle['cycle_id'],'max_steps':16},13);assert waiting['status']=='WAITING_HUG_IMPLEMENTATION',waiting;assert waiting['phase']=='HUG',waiting
design=call('athena_experiment_design',{'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],'experiments':[{'id':'E1','positive_probability':{'H1':.9,'H2':.1},'ethical':True,'cost':.1,'risk':.1}],'sample_size':10},14);assert design['decision']=='DESIGN_ONLY' and design['winner']=='E1',design
causal=call('athena_causal_identify',{'treatment':'T','outcome':'Y','edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],'observed_nodes':['T','Y','Z']},15);assert causal['status']=='IDENTIFIED_BACKDOOR' and ['Z'] in causal['minimal_adjustment_sets'],causal
transition=call('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}},16);assert transition['status']=='UNSEEN_ACTION',transition
dual=call('athena_dual_control_plan',{'initial_context':{'x':0.0},'actions':[{'id':'A','base_reward':.4},{'id':'B','base_reward':.6}],'horizon':2},17);assert dual['decision']=='DUAL_CONTROL_PROXY_PLAN_ONLY',dual
transition_after=call('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}},18);assert transition_after['status']=='UNSEEN_ACTION',transition_after
call('athena_belief_register',{'context_key':'SMOKE.B8','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]},19)
b8_before=call('athena_belief_state',{'context_key':'SMOKE.B8'},20)
actions8=[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}]
evi=call('athena_decision_evi',{'context_key':'SMOKE.B8','actions':actions8,'experiments':[{'id':'E','outcomes':{'yes':{'M1':.9,'M2':.1},'no':{'M1':.1,'M2':.9}}}]},21);assert evi['decision']=='DESIGN_ONLY',evi
b8_after=call('athena_belief_state',{'context_key':'SMOKE.B8'},22);assert b8_before['models']==b8_after['models']
greg=call('athena_gaussian_belief_register',{'context_key':'SMOKE.G9','parameters':['theta'],'prior_variance':2.0,'noise_variance':.5},23);assert greg['status']=='GAUSSIAN_LINEAR_BELIEF',greg
g9_before=call('athena_gaussian_belief_state',{'context_key':'SMOKE.G9'},24)
evpi=call('athena_decision_evpi',{'context_key':'SMOKE.G9','actions':[{'id':'p','utility_linear':{'theta':1}},{'id':'m','utility_linear':{'theta':-1}}],'samples':60,'seed':1},25);assert evpi['status']=='MONTE_CARLO_EVPI_ESTIMATE',evpi
g9_after=call('athena_gaussian_belief_state',{'context_key':'SMOKE.G9'},26);assert g9_before['observation_count']==g9_after['observation_count'];assert g9_before['mean']==g9_after['mean']
call('athena_gp_register',{'context_key':'SMOKE.GP10','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.02},27)
gp_prior=call('athena_gp_predict',{'context_key':'SMOKE.GP10','features':{'x':.5},'include_observation_noise':False},28);assert gp_prior['status']=='GP_PRIOR_PREDICTION';assert gp_prior['observation_count']==0
for x,y,rid in ((0.0,0.0,29),(0.5,.25,30),(1.0,1.0,31)):
    call('athena_gp_observe',{'context_key':'SMOKE.GP10','features':{'x':x},'target':y,'evidence_ref':'smoke://gp'},rid)
gp_post=call('athena_gp_predict',{'context_key':'SMOKE.GP10','features':{'x':.5},'include_observation_noise':False},32);assert gp_post['status']=='GP_POSTERIOR_PREDICTION';assert gp_post['observation_count']==3
gp_before=call('athena_gp_state',{'context_key':'SMOKE.GP10'},33);assert gp_before['observation_count']==3
hyper=call('athena_gp_hyperfit',{'context_key':'SMOKE.GP10','length_scales':[.4,.7,1.0],'signal_variances':[.7,1.0],'noise_variances':[.01,.02],'apply':False},34);assert hyper['status']=='GP_HYPERPARAMETER_DESIGN_ONLY',hyper
gevsi=call('athena_gp_decision_evsi',{'context_key':'SMOKE.GP10','actions':[{'id':'left','features':{'x':0.0}},{'id':'right','features':{'x':1.0}}],'experiments':[{'id':'center','features':{'x':.5},'noise_variance':.02}],'samples':60,'seed':3,'cost_weight':0,'risk_weight':0},35);assert gevsi['decision']=='GP_DECISION_EVSI_DESIGN_ONLY',gevsi
gp_after=call('athena_gp_state',{'context_key':'SMOKE.GP10'},36);assert gp_before['observation_count']==gp_after['observation_count'];assert gp_before['length_scale']==gp_after['length_scale']
js_before=resource('athena://jspace',37);proj=call('athena_latent_project_admg',{'edges':[{'src':'L','dst':'X'},{'src':'L','dst':'Y'},{'src':'X','dst':'Y'}],'latent_nodes':['L'],'observed_nodes':['X','Y']},38);assert proj['status']=='RESTRICTED_LATENT_PROJECTION_ADMG',proj
js_after=resource('athena://jspace',39);assert len(js_before['edges'])==len(js_after['edges']);assert len(js_before['hyperedges'])==len(js_after['hyperedges'])
states=['G','B'];pomdp_actions=[{'id':'safe','reward_by_state':{'G':.4,'B':.4},'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},'observation':{'G':{'n':1.0},'B':{'n':1.0}}}]
pomdp=call('athena_pomdp_solve',{'states':states,'initial_belief':{'G':.5,'B':.5},'actions':pomdp_actions,'horizon':2,'max_nodes':5000},40);assert pomdp['certificate']=='EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON',pomdp
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
em=call('athena_finalize_output',{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}},41)
assert em['envelope_id'].startswith('ENV.');assert em['emission_mid'].startswith('MID.');assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.');assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
verified=call('athena_verify_emission',{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']},42);assert verified['verified'] is True
p.terminate(); print('SMOKE PASS: V6 DISCOVERY + V7 DUAL-CONTROL + V8 BELIEF + V9 INFERENCE + V10 PROBABILISTIC + V11 ADAPTIVE + SCHEMA/SELFTEST + AOR + FAIL-CLOSED CYCLE + FINAL EMISSION')

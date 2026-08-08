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

init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'5'}},1);assert init['serverInfo']['version']=='2.9.0',init
p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
tools=rpc('tools/list',{},2)['tools'];names={x['name'] for x in tools}
for n in ('athena_orchestrate','athena_cycle_start','athena_self_test','athena_schema_migrate','athena_experiment_design','athena_causal_identify','athena_dual_control_plan','athena_belief_register','athena_decision_evi','athena_gaussian_belief_register','athena_decision_evpi','athena_structure_partial','athena_gp_register','athena_gp_predict','athena_pc_stable_discover','athena_causal_tmle_binary','athena_pomdp_solve','athena_discovery_claim_register','athena_claim_register','athena_finalize_output'):
    assert n in names,n
manifest=resource('athena://manifest',3);assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.5',manifest
for layer in ('COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','AOR_DECISION_CORTEX'):assert layer in manifest['layers'],layer
v6=resource('athena://collective/v6',4);assert v6['runtime']['version']=='COLLECTIVE_RUNTIME_V6',v6;assert v6['claim_namespace']['discovery_shadow_prefix']=='athena_discovery_claim_'
v8=resource('athena://collective/v8',5);assert v8['runtime']['version']=='COLLECTIVE_RUNTIME_V8',v8
v9=resource('athena://collective/v9',6);assert v9['runtime']['version']=='COLLECTIVE_RUNTIME_V9',v9
v10=resource('athena://collective/v10',7);assert v10['runtime']['version']=='COLLECTIVE_RUNTIME_V10',v10;assert 'model/assumption scoped' in v10['boundary']
migration=call('athena_schema_migrate',{},8);assert migration['status'] in {'APPLIED','UP_TO_DATE'},migration
health=call('athena_self_test',{'replay_limit':5},9);assert health['status']=='PASS',health
aor=call('athena_orchestrate',{'seed':'SMOKE','candidates':[]},10);assert aor['run_id'].startswith('AORRUN.'),aor;assert aor['next'] is None
cycle=call('athena_cycle_start',{'task_ref':'task://smoke','seed':'SMOKE','config':{'require_hug':True}},11);assert cycle['cycle_id'].startswith('CYCLE.'),cycle
waiting=call('athena_cycle_advance',{'cycle_id':cycle['cycle_id'],'max_steps':16},12);assert waiting['status']=='WAITING_HUG_IMPLEMENTATION',waiting;assert waiting['phase']=='HUG',waiting
design=call('athena_experiment_design',{'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],'experiments':[{'id':'E1','positive_probability':{'H1':.9,'H2':.1},'ethical':True,'cost':.1,'risk':.1}],'sample_size':10},13);assert design['decision']=='DESIGN_ONLY' and design['winner']=='E1',design
causal=call('athena_causal_identify',{'treatment':'T','outcome':'Y','edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],'observed_nodes':['T','Y','Z']},14);assert causal['status']=='IDENTIFIED_BACKDOOR' and ['Z'] in causal['minimal_adjustment_sets'],causal
transition=call('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}},15);assert transition['status']=='UNSEEN_ACTION',transition
dual=call('athena_dual_control_plan',{'initial_context':{'x':0.0},'actions':[{'id':'A','base_reward':.4},{'id':'B','base_reward':.6}],'horizon':2},16);assert dual['decision']=='DUAL_CONTROL_PROXY_PLAN_ONLY',dual
transition_after=call('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}},17);assert transition_after['status']=='UNSEEN_ACTION',transition_after
call('athena_belief_register',{'context_key':'SMOKE.B8','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]},18)
b8_before=call('athena_belief_state',{'context_key':'SMOKE.B8'},19)
actions8=[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}]
evi=call('athena_decision_evi',{'context_key':'SMOKE.B8','actions':actions8,'experiments':[{'id':'E','outcomes':{'yes':{'M1':.9,'M2':.1},'no':{'M1':.1,'M2':.9}}}]},20);assert evi['decision']=='DESIGN_ONLY',evi
b8_after=call('athena_belief_state',{'context_key':'SMOKE.B8'},21);assert b8_before['models']==b8_after['models']
greg=call('athena_gaussian_belief_register',{'context_key':'SMOKE.G9','parameters':['theta'],'prior_variance':2.0,'noise_variance':.5},22);assert greg['status']=='GAUSSIAN_LINEAR_BELIEF',greg
g9_before=call('athena_gaussian_belief_state',{'context_key':'SMOKE.G9'},23)
evpi=call('athena_decision_evpi',{'context_key':'SMOKE.G9','actions':[{'id':'p','utility_linear':{'theta':1}},{'id':'m','utility_linear':{'theta':-1}}],'samples':60,'seed':1},24);assert evpi['status']=='MONTE_CARLO_EVPI_ESTIMATE',evpi
g9_after=call('athena_gaussian_belief_state',{'context_key':'SMOKE.G9'},25);assert g9_before['observation_count']==g9_after['observation_count'];assert g9_before['mean']==g9_after['mean']
call('athena_gp_register',{'context_key':'SMOKE.GP10','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.02},26)
gp_prior=call('athena_gp_predict',{'context_key':'SMOKE.GP10','features':{'x':.5},'include_observation_noise':False},27);assert gp_prior['status']=='GP_PRIOR_PREDICTION';assert gp_prior['observation_count']==0
for x,y in ((0.0,0.0),(1.0,1.0)):
    call('athena_gp_observe',{'context_key':'SMOKE.GP10','features':{'x':x},'target':y,'evidence_ref':'smoke://gp'},28 if x==0.0 else 29)
gp_post=call('athena_gp_predict',{'context_key':'SMOKE.GP10','features':{'x':.5},'include_observation_noise':False},30);assert gp_post['status']=='GP_POSTERIOR_PREDICTION';assert gp_post['observation_count']==2
assert call('athena_gp_state',{'context_key':'SMOKE.GP10'},31)['observation_count']==2
states=['G','B'];pomdp_actions=[{'id':'safe','reward_by_state':{'G':.4,'B':.4},'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},'observation':{'G':{'n':1.0},'B':{'n':1.0}}}]
pomdp=call('athena_pomdp_solve',{'states':states,'initial_belief':{'G':.5,'B':.5},'actions':pomdp_actions,'horizon':2,'max_nodes':5000},32);assert pomdp['certificate']=='EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON',pomdp
rows=[{'X':i/20,'Y':2*i/20+((i%3)-1)*.01,'Z':((i*7)%11)/11} for i in range(20)]
partial=call('athena_structure_partial',{'samples':rows,'variables':['X','Y','Z'],'association_threshold':.4,'resamples':10,'support_threshold':.5,'seed':2},33);assert partial['status']=='HEURISTIC_PARTIAL_GRAPH',partial
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
em=call('athena_finalize_output',{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}},34)
assert em['envelope_id'].startswith('ENV.');assert em['emission_mid'].startswith('MID.');assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.');assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
verified=call('athena_verify_emission',{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']},35);assert verified['verified'] is True
p.terminate(); print('SMOKE PASS: V6 DISCOVERY + V7 DUAL-CONTROL + V8 BELIEF + V9 INFERENCE + V10 PROBABILISTIC + SCHEMA/SELFTEST + AOR + FAIL-CLOSED CYCLE + FINAL EMISSION')

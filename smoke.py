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

init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'8'}},1);assert init['serverInfo']['version']=='3.1.0',init
p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
tools=rpc('tools/list',{},2)['tools'];names={x['name'] for x in tools}
for n in ('athena_orchestrate','athena_cycle_start','athena_self_test','athena_schema_migrate','athena_experiment_design','athena_causal_identify','athena_dual_control_plan','athena_belief_register','athena_decision_evi','athena_gaussian_belief_register','athena_decision_evpi','athena_structure_partial','athena_gp_register','athena_gp_predict','athena_pc_stable_discover','athena_causal_tmle_binary','athena_pomdp_solve','athena_gp_hyperfit','athena_gp_decision_evsi','athena_latent_project_admg','athena_bapomdp_solve','athena_gp_hyperposterior','athena_gp_bma_predict','athena_gp_sparse_predict','athena_gp_bma_decision_evsi','athena_pag_candidate_discover','athena_longitudinal_gformula','athena_chance_resource_select','athena_discovery_claim_register','athena_claim_register','athena_promotion_evaluate','athena_finalize_output'):
    assert n in names,n
manifest=resource('athena://manifest',3);assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.7',manifest;assert 'PROMOTION.2' in manifest['layers']
for layer in ('COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11','COLLECTIVE_JOINT_V12','AOR_DECISION_CORTEX'):assert layer in manifest['layers'],layer
v6=resource('athena://collective/v6',4);assert v6['runtime']['version']=='COLLECTIVE_RUNTIME_V6',v6;assert v6['claim_namespace']['discovery_shadow_prefix']=='athena_discovery_claim_'
v10=resource('athena://collective/v10',5);assert v10['runtime']['version']=='COLLECTIVE_RUNTIME_V10',v10
v11=resource('athena://collective/v11',6);assert v11['runtime']['version']=='COLLECTIVE_RUNTIME_V11',v11
v12=resource('athena://collective/v12',7);assert v12['runtime']['version']=='COLLECTIVE_RUNTIME_V12',v12;assert 'Y1 authority' in v12['boundary']
migration=call('athena_schema_migrate',{},8);assert migration['status'] in {'APPLIED','UP_TO_DATE'},migration
health=call('athena_self_test',{'replay_limit':5},9);assert health['status']=='PASS',health
aor=call('athena_orchestrate',{'seed':'SMOKE','candidates':[]},10);assert aor['run_id'].startswith('AORRUN.'),aor;assert aor['next'] is None
cycle=call('athena_cycle_start',{'task_ref':'task://smoke','seed':'SMOKE','config':{'require_hug':True}},11);assert cycle['cycle_id'].startswith('CYCLE.'),cycle
waiting=call('athena_cycle_advance',{'cycle_id':cycle['cycle_id'],'max_steps':16},12);assert waiting['status']=='WAITING_HUG_IMPLEMENTATION',waiting;assert waiting['phase']=='HUG',waiting
design=call('athena_experiment_design',{'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],'experiments':[{'id':'E1','positive_probability':{'H1':.9,'H2':.1},'ethical':True,'cost':.1,'risk':.1}],'sample_size':10},13);assert design['decision']=='DESIGN_ONLY' and design['winner']=='E1',design
causal=call('athena_causal_identify',{'treatment':'T','outcome':'Y','edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],'observed_nodes':['T','Y','Z']},14);assert causal['status']=='IDENTIFIED_BACKDOOR' and ['Z'] in causal['minimal_adjustment_sets'],causal
dual=call('athena_dual_control_plan',{'initial_context':{'x':0.0},'actions':[{'id':'A','base_reward':.4},{'id':'B','base_reward':.6}],'horizon':2},15);assert dual['decision']=='DUAL_CONTROL_PROXY_PLAN_ONLY',dual
call('athena_belief_register',{'context_key':'SMOKE.B8','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]},16)
b8_before=call('athena_belief_state',{'context_key':'SMOKE.B8'},17)
evi=call('athena_decision_evi',{'context_key':'SMOKE.B8','actions':[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}],'experiments':[{'id':'E','outcomes':{'yes':{'M1':.9,'M2':.1},'no':{'M1':.1,'M2':.9}}}]},18);assert evi['decision']=='DESIGN_ONLY',evi
b8_after=call('athena_belief_state',{'context_key':'SMOKE.B8'},19);assert b8_before['models']==b8_after['models']
call('athena_gaussian_belief_register',{'context_key':'SMOKE.G9','parameters':['theta'],'prior_variance':2.0,'noise_variance':.5},20)
evpi=call('athena_decision_evpi',{'context_key':'SMOKE.G9','actions':[{'id':'p','utility_linear':{'theta':1}},{'id':'m','utility_linear':{'theta':-1}}],'samples':60,'seed':1},21);assert evpi['status']=='MONTE_CARLO_EVPI_ESTIMATE',evpi
call('athena_gp_register',{'context_key':'SMOKE.GP','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.02},22)
for x,y,rid in ((0.0,0.0,23),(0.25,.0625,24),(0.5,.25,25),(0.75,.5625,26),(1.0,1.0,27)):
    call('athena_gp_observe',{'context_key':'SMOKE.GP','features':{'x':x},'target':y,'evidence_ref':'smoke://gp'},rid)
gp_before=call('athena_gp_state',{'context_key':'SMOKE.GP'},28);assert gp_before['observation_count']==5
hyperfit=call('athena_gp_hyperfit',{'context_key':'SMOKE.GP','length_scales':[.4,.7,1.0],'signal_variances':[.7,1.0],'noise_variances':[.01,.02],'apply':False},29);assert hyperfit['status']=='GP_HYPERPARAMETER_DESIGN_ONLY',hyperfit
hp=call('athena_gp_hyperposterior',{'context_key':'SMOKE.GP','candidates':[{'length_scale':.4,'signal_variance':1,'noise_variance':.02,'prior':1},{'length_scale':.7,'signal_variance':1,'noise_variance':.02,'prior':1},{'length_scale':1.0,'signal_variance':1,'noise_variance':.02,'prior':1}]},30);assert hp['status']=='FINITE_GRID_GP_HYPERPOSTERIOR';assert abs(sum(x['posterior_weight'] for x in hp['posterior'])-1)<1e-8
bma=call('athena_gp_bma_predict',{'context_key':'SMOKE.GP','features':{'x':.6},'candidates':hp['posterior']},31);assert bma['status']=='FINITE_GRID_GP_BAYESIAN_MODEL_AVERAGE';assert bma['predictive_variance']>=bma['within_model_variance']
sparse=call('athena_gp_sparse_predict',{'context_key':'SMOKE.GP','features':{'x':.6},'inducing_count':3},32);assert sparse['status']=='SUBSET_OF_DATA_GP_APPROXIMATION';assert sparse['inducing_count']==3
bma_evsi=call('athena_gp_bma_decision_evsi',{'context_key':'SMOKE.GP','actions':[{'id':'left','features':{'x':.1}},{'id':'right','features':{'x':.9}}],'experiments':[{'id':'mid','features':{'x':.55},'noise_variance':.02}],'samples':50,'seed':7,'cost_weight':0,'risk_weight':0},33);assert bma_evsi['decision']=='FINITE_GRID_BMA_GP_EVSI_DESIGN_ONLY'
gp_after=call('athena_gp_state',{'context_key':'SMOKE.GP'},34);assert gp_before['observation_count']==gp_after['observation_count'];assert gp_before['length_scale']==gp_after['length_scale']
js_before=resource('athena://jspace',35)
proj=call('athena_latent_project_admg',{'edges':[{'src':'L','dst':'X'},{'src':'L','dst':'Y'},{'src':'X','dst':'Y'}],'latent_nodes':['L'],'observed_nodes':['X','Y']},36);assert proj['status']=='RESTRICTED_LATENT_PROJECTION_ADMG',proj
pag_rows=[]
for i in range(80):
    x=((i*13)%79)/39.0-1;y=((i*29)%83)/41.0-1;z=.9*x-.7*y+((i*7)%11-5)/300
    pag_rows.append({'X':x,'Y':y,'Z':z})
pag=call('athena_pag_candidate_discover',{'samples':pag_rows,'variables':['X','Y','Z'],'alpha':.02,'max_conditioning':1},37);assert pag['status']=='BOUNDED_PAG_CANDIDATE'
js_after=resource('athena://jspace',38);assert len(js_before['edges'])==len(js_after['edges']);assert len(js_before['hyperedges'])==len(js_after['hyperedges'])
long_rows=[]
for i in range(120):
    x=((i*17)%101)/100-.5;a1=i%2;l1=1 if ((i*31)%100)/100<max(.05,min(.95,.25+.3*a1+.1*x)) else 0;a2=1 if i%4 in (1,2) else 0;y=1 if ((i*47)%100)/100<max(.03,min(.97,.08+.12*a1+.16*l1+.4*a2+.05*x)) else 0
    long_rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
gf=call('athena_longitudinal_gformula',{'samples':long_rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X']},39);assert gf['status']=='TWO_TIMEPOINT_PARAMETRIC_GFORMULA_ESTIMATED_UNDER_ASSUMPTIONS';assert gf['risk_contrast']>=0
chance=call('athena_chance_resource_select',{'candidates':[{'id':'A','value':5,'resources':{'tokens':{'mean':4,'std':.2}}},{'id':'B','value':4,'resources':{'tokens':{'mean':3,'std':.2}}},{'id':'C','value':2,'resources':{'tokens':{'mean':2,'std':.1}}}],'budgets':{'tokens':8},'alpha':.05},40);assert chance['status']=='CHANCE_CONSTRAINED_EXACT_ENUMERATION_CERTIFIED';assert set(chance['selected'])=={'A','B'}
states=['G','B'];pomdp_actions=[{'id':'safe','reward_by_state':{'G':.4,'B':.4},'transition':{'G':{'G':1.0,'B':0.0},'B':{'G':0.0,'B':1.0}},'observation':{'G':{'n':1.0},'B':{'n':1.0}}}]
pomdp=call('athena_pomdp_solve',{'states':states,'initial_belief':{'G':.5,'B':.5},'actions':pomdp_actions,'horizon':2,'max_nodes':5000},41);assert pomdp['certificate']=='EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON',pomdp
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
em=call('athena_finalize_output',{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}},42)
assert em['envelope_id'].startswith('ENV.');assert em['emission_mid'].startswith('MID.');assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.');assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
verified=call('athena_verify_emission',{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']},43);assert verified['verified'] is True
git_state=call('athena_git_status',{},44);promotion_head=git_state.get('head') or 'smokehead1234567'
ci_packet={'observed':True,'ref':'ci://smoke-caller-attestation','head_sha':promotion_head,'conclusion':'success'}
smoke_packet={'observed':True,'ref':'smoke://smoke-caller-attestation','head_sha':promotion_head,'conclusion':'success'}
promotion=call('athena_promotion_evaluate',{'git_head':promotion_head,'ci_witness':ci_packet,'smoke_witness':smoke_packet,'persist':False},45)
assert promotion['status']=='ATTESTED_READY',promotion;assert promotion['promotion_allowed'] is False;assert promotion['gates']['external_verification']['status']=='MISSING'
p.terminate(); print('SMOKE PASS: V6 DISCOVERY + V7 DUAL-CONTROL + V8 BELIEF + V9 INFERENCE + V10 PROBABILISTIC + V11 ADAPTIVE + V12 JOINT + PROMOTION.2 CALLER-BOUND READINESS + SCHEMA/SELFTEST + AOR + FAIL-CLOSED CYCLE + FINAL EMISSION')

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

init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'9'}},1);assert init['serverInfo']['version']=='3.2.0',init
p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
tools=rpc('tools/list',{},2)['tools'];names={x['name'] for x in tools}
for n in ('athena_orchestrate','athena_cycle_start','athena_self_test','athena_schema_migrate','athena_experiment_design','athena_causal_identify','athena_dual_control_plan','athena_belief_register','athena_decision_evi','athena_gaussian_belief_register','athena_decision_evpi','athena_gp_register','athena_gp_predict','athena_gp_hyperfit','athena_gp_hyperposterior','athena_gp_bma_predict','athena_gp_sparse_predict','athena_pag_candidate_discover','athena_longitudinal_gformula','athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select','athena_discovery_claim_register','athena_claim_register','athena_promotion_evaluate','athena_finalize_output'):
    assert n in names,n
manifest=resource('athena://manifest',3);assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.8',manifest;assert 'PROMOTION.2' in manifest['layers'];assert 'COLLECTIVE_ROBUST_V13' in manifest['layers']
v13=resource('athena://collective/v13',4);assert v13['runtime']['version']=='COLLECTIVE_RUNTIME_V13',v13;assert 'Y1 authority' in v13['boundary'];assert 'trusted promotion verification' in v13['boundary']
migration=call('athena_schema_migrate',{},5);assert migration['status'] in {'APPLIED','UP_TO_DATE'},migration
health=call('athena_self_test',{'replay_limit':5},6);assert health['status']=='PASS',health
aor=call('athena_orchestrate',{'seed':'SMOKE','candidates':[]},7);assert aor['run_id'].startswith('AORRUN.'),aor;assert aor['next'] is None
cycle=call('athena_cycle_start',{'task_ref':'task://smoke','seed':'SMOKE','config':{'require_hug':True}},8);waiting=call('athena_cycle_advance',{'cycle_id':cycle['cycle_id'],'max_steps':16},9);assert waiting['status']=='WAITING_HUG_IMPLEMENTATION' and waiting['phase']=='HUG',waiting
call('athena_belief_register',{'context_key':'SMOKE.B8','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]},10);b8_before=call('athena_belief_state',{'context_key':'SMOKE.B8'},11);evi=call('athena_decision_evi',{'context_key':'SMOKE.B8','actions':[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}],'experiments':[{'id':'E','outcomes':{'yes':{'M1':.9,'M2':.1},'no':{'M1':.1,'M2':.9}}}]},12);assert evi['decision']=='DESIGN_ONLY';b8_after=call('athena_belief_state',{'context_key':'SMOKE.B8'},13);assert b8_before['models']==b8_after['models']
call('athena_gp_register',{'context_key':'SMOKE.GP','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.02},14)
for x,y,rid in ((0.0,0.0,15),(0.2,.04,16),(0.4,.16,17),(0.6,.36,18),(0.8,.64,19),(1.0,1.0,20)):
    call('athena_gp_observe',{'context_key':'SMOKE.GP','features':{'x':x},'target':y,'evidence_ref':'smoke://gp'},rid)
gp_before=call('athena_gp_state',{'context_key':'SMOKE.GP'},21);assert gp_before['observation_count']==6
hp=call('athena_gp_hyperposterior',{'context_key':'SMOKE.GP','candidates':[{'length_scale':.4,'signal_variance':1,'noise_variance':.02,'prior':1},{'length_scale':.7,'signal_variance':1,'noise_variance':.02,'prior':1},{'length_scale':1.0,'signal_variance':1,'noise_variance':.02,'prior':1}]},22);assert hp['status']=='FINITE_GRID_GP_HYPERPOSTERIOR'
qmc=call('athena_gp_hyperqmc',{'context_key':'SMOKE.GP','samples':40,'seed':2},23);assert qmc['status']=='QMC_CONTINUOUS_GP_HYPERPOSTERIOR_APPROXIMATION';assert qmc['effective_sample_size']>=1
fitc=call('athena_gp_fitc_predict',{'context_key':'SMOKE.GP','features':{'x':.55},'inducing_count':3},24);assert fitc['status']=='FITC_INDUCING_GP_APPROXIMATION';assert fitc['inducing_count']==3
joint=call('athena_gp_joint_design',{'context_key':'SMOKE.GP','actions':[{'id':'left','features':{'x':.1}},{'id':'right','features':{'x':.9}}],'experiments':[{'id':'mid','features':{'x':.5},'cost':0}],'hyper_samples':40,'mc_samples':80,'seed':4,'cost_weight':0},25);assert joint['decision']=='JOINT_HYPERMODEL_GP_DESIGN_ONLY' and joint['winner']=='mid'
gp_after=call('athena_gp_state',{'context_key':'SMOKE.GP'},26);assert gp_before['observation_count']==gp_after['observation_count'];assert gp_before['length_scale']==gp_after['length_scale']
js_before=resource('athena://jspace',27);fci_rows=[]
for i in range(120):
    x=((i*13)%101)/50-1;y=((i*31)%103)/51-1;z=.9*x-.8*y+((i*7)%13-6)/500
    fci_rows.append({'X':x,'Y':y,'Z':z})
fci=call('athena_fci_lite_discover',{'samples':fci_rows,'variables':['X','Y','Z'],'alpha':.02,'max_conditioning':1},28);assert fci['status']=='BOUNDED_FCI_LITE_CANDIDATE'
js_after=resource('athena://jspace',29);assert len(js_before['edges'])==len(js_after['edges']);assert len(js_before['hyperedges'])==len(js_after['hyperedges'])
long_rows=[]
for i in range(180):
    x=((i*17)%101)/100-.5;pa1=max(.1,min(.9,.45+.15*x));a1=1 if ((i*29)%100)/100<pa1 else 0;pl=max(.08,min(.92,.2+.35*a1+.15*x));l1=1 if ((i*37)%100)/100<pl else 0;pa2=max(.08,min(.92,.3+.15*a1+.25*l1+.1*x));a2=1 if ((i*41)%100)/100<pa2 else 0;py=max(.03,min(.97,.07+.1*a1+.16*l1+.48*a2+.08*x));y=1 if ((i*53)%100)/100<py else 0
    long_rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
tmle=call('athena_longitudinal_tmle',{'samples':long_rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X']},30);assert tmle['status']=='TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE_ESTIMATED_UNDER_ASSUMPTIONS';assert tmle['targeting_history'].startswith('OBSERVED_A1_L1_RETAINED')
pv=call('athena_dynamic_policy_value',{'samples':long_rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'policies':[{'id':'never','a1':0,'a2':0},{'id':'always','a1':1,'a2':1},{'id':'adaptive','a1':1,'a2':{'coefficients':{'L1':2},'threshold':1}}]},31);assert pv['status']=='DYNAMIC_TWO_TIMEPOINT_GFORMULA_POLICY_VALUE_UNDER_ASSUMPTIONS';assert pv['winner'] in {'always','adaptive','never'}
robust=call('athena_dro_resource_select',{'candidates':[{'id':'A','value':5,'resources':{'tokens':{'mean':3,'mean_uncertainty':.2}}},{'id':'B','value':4,'resources':{'tokens':{'mean':2,'mean_uncertainty':.2}}},{'id':'C','value':2,'resources':{'tokens':{'mean':1,'mean_uncertainty':.2}}}],'budgets':{'tokens':6.5},'covariances':{'tokens':[[.04,.01,0],[.01,.04,.01],[0,.01,.04]]},'ambiguity_radius':.5,'alpha':.05},32);assert robust['status']=='CORRELATED_GAUSSIAN_ELLIPSOIDAL_MEAN_ROBUST_EXACT_ENUMERATION';assert robust['certificate']=='EXACT_ENUMERATION_UNDER_DECLARED_CORRELATED_GAUSSIAN_COVARIANCE_AND_ELLIPSOIDAL_MEAN_AMBIGUITY'
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
em=call('athena_finalize_output',{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}},33);verified=call('athena_verify_emission',{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']},34);assert verified['verified'] is True
git_state=call('athena_git_status',{},35);promotion_head=git_state.get('head') or 'smokehead1234567';ci_packet={'observed':True,'ref':'ci://smoke-caller-attestation','head_sha':promotion_head,'conclusion':'success'};smoke_packet={'observed':True,'ref':'smoke://smoke-caller-attestation','head_sha':promotion_head,'conclusion':'success'}
promotion=call('athena_promotion_evaluate',{'git_head':promotion_head,'ci_witness':ci_packet,'smoke_witness':smoke_packet,'persist':False},36);assert promotion['status']=='ATTESTED_READY',promotion;assert promotion['promotion_allowed'] is False;assert promotion['gates']['external_verification']['status']=='MISSING'
p.terminate(); print('SMOKE PASS: V8 BELIEF + V10/V12 GP + V13 QMC/FITC/JOINT-DESIGN/FCI-LITE/LONGITUDINAL-TMLE/DYNAMIC-POLICY/ROBUST-RESOURCE + PROMOTION.2 CALLER-BOUND READINESS + SCHEMA/SELFTEST + AOR + FAIL-CLOSED CYCLE + FINAL EMISSION')

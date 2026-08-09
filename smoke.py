import json, os, random, subprocess, sys, tempfile

fd,path=tempfile.mkstemp(suffix='.db');os.close(fd);os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)


def rpc(method,params=None,request_id=1):
    msg={'jsonrpc':'2.0','id':request_id,'method':method}
    if params is not None:msg['params']=params
    p.stdin.write(json.dumps(msg)+'\n');p.stdin.flush();r=json.loads(p.stdout.readline());assert r.get('error') is None,r;return r['result']


def call(name,args,request_id):
    result=rpc('tools/call',{'name':name,'arguments':args},request_id);assert result.get('isError') is not True,result;return result['structuredContent']


def resource(uri,request_id):return json.loads(rpc('resources/read',{'uri':uri},request_id)['contents'][0]['text'])

init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'15'}},1);assert init['serverInfo']['version']=='3.4.0',init
p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
names={x['name'] for x in rpc('tools/list',{},2)['tools']};uris={x['uri'] for x in rpc('resources/list',{},3)['resources']}
for name in (
    'athena_schema_migrate','athena_self_test','athena_joint_factor_belief','athena_gp_resolution_route',
    'athena_structural_reliability_calibrate','athena_longitudinal_tmle_crossfit','athena_sequential_dr_policy_crossfit',
    'athena_joint_gaussian_update','athena_joint_gaussian_control','athena_approx_error_transport','athena_multistage_tv_dro_plan',
    'athena_deployment_manifest','athena_deployment_validate','athena_deployment_activation_plan','athena_deployment_assess_canary','athena_deployment_verify_receipt',
    'athena_claim_register','athena_claim_state','athena_promotion_evaluate','athena_promotion_verify_github','athena_finalize_output','athena_verify_emission',
):assert name in names,name
for uri in ('athena://manifest','athena://collective/v14','athena://collective/v15','athena://deployment','athena://deployment/security','athena://deployment/rollout','athena://deployment/evidence','athena://promotion'):
    assert uri in uris,uri

manifest=resource('athena://manifest',4);assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.11',manifest;assert 'COLLECTIVE_CALIBRATED_V15' in manifest['layers']
v15=resource('athena://collective/v15',5);assert v15['runtime']['version']=='COLLECTIVE_RUNTIME_V15';assert v15['runtime']['coordinate']=='COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>'
deployment=resource('athena://deployment',6);assert 'ATHENA.DEPLOYMENT.2' in json.dumps(deployment)
promotion_resource=resource('athena://promotion',7);assert promotion_resource['github_verifier']['version']=='ATHENA.GITHUB.PROMOTION.VERIFIER.1'

migration=call('athena_schema_migrate',{},8);assert migration['status'] in {'APPLIED','UP_TO_DATE'},migration
health=call('athena_self_test',{'replay_limit':5},9);assert health['status']=='PASS',health

# V15 calibration/model/control calls must remain outside Y1 authority.
call('athena_claim_register',{'claim_id':'SMOKE.V15','source_ref':'smoke://v15'},10);y_before=call('athena_claim_state',{'claim_id':'SMOKE.V15'},11)
examples=[]
for support,correct in ((.2,0),(.4,0),(.7,1),(.9,1)):examples.extend({'support':support,'correct':correct} for _ in range(12))
cal=call('athena_structural_reliability_calibrate',{'calibration_examples':examples,'supports':[.3,.8],'folds':3,'seed':2},12);assert cal['status']=='OUT_OF_FOLD_WEIGHTED_ISOTONIC_STRUCTURAL_RELIABILITY';assert cal['unique_support_coordinates']==4
update=call('athena_joint_gaussian_update',{'variables':['x','y'],'mean':[0,0],'covariance':[[1,.25],[.25,1]],'observation':{'coefficients':{'x':1},'value':.8,'noise_variance':.2}},13);assert update['status']=='EXACT_LINEAR_GAUSSIAN_JOINT_UPDATE'
control=call('athena_joint_gaussian_control',{'variables':['x','y'],'mean':update['posterior_mean'],'covariance':update['posterior_covariance'],'actions':[{'id':'long','coefficients':{'x':1}},{'id':'short','coefficients':{'x':-1}}],'risk_weight':.2},14);assert control['decision']=='GAUSSIAN_LINEAR_JOINT_CONTROL_PLAN_ONLY';assert control['winner']=='long'
transport=call('athena_approx_error_transport',{'feature_order':['x'],'witnesses':[{'features':{'x':0},'absolute_error':.1},{'features':{'x':1},'absolute_error':.2}],'queries':[{'id':'mid','features':{'x':.5},'decision_margin':.8}],'lipschitz_bound':.2,'max_transport_radius':1,'margin_safety':.5},15);assert transport['status']=='DECLARED_LIPSCHITZ_APPROXIMATION_ERROR_TRANSPORT';assert transport['queries'][0]['decision_preserving_under_bound'] is True;assert transport['queries'][0]['nearest_witness_distance']==.5
dro=call('athena_multistage_tv_dro_plan',{'states':['G','B'],'initial_state':'G','horizon':3,'tv_radius':.2,'actions_by_state':{'G':[{'id':'safe','reward':1,'transitions':{'G':.95,'B':.05}},{'id':'risky','reward':2,'transitions':{'G':.5,'B':.5}}],'B':[{'id':'recover','reward':-1,'transitions':{'G':.8,'B':.2}},{'id':'stuck','reward':-4,'transitions':{'G':.1,'B':.9}}]}},16);assert dro['status']=='FINITE_HORIZON_RECTANGULAR_TV_DRO_DYNAMIC_PROGRAM_CERTIFIED';assert dro['policy']['0']['G']=='safe'
y_after=call('athena_claim_state',{'claim_id':'SMOKE.V15'},17);assert y_before==y_after

# Cross-fitted longitudinal methods execute through the real stdio boundary.
rng=random.Random(17);rows=[]
for _ in range(210):
    x=rng.uniform(-1,1);p1=max(.1,min(.9,.45+.12*x));a1=1 if rng.random()<p1 else 0;pl=max(.05,min(.95,.2+.42*a1+.08*x));l1=1 if rng.random()<pl else 0;p2=max(.1,min(.9,.42+.12*l1-.05*x));a2=1 if rng.random()<p2 else 0;py=max(.03,min(.97,.06+.16*a1+.09*l1+.5*a2+.05*x));y=1 if rng.random()<py else 0;rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
tmle=call('athena_longitudinal_tmle_crossfit',{'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'folds':2,'seed':3},18);assert tmle['cross_fitted'] is True;assert tmle['history_invariant']=='STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION'
dr=call('athena_sequential_dr_policy_crossfit',{'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'folds':2,'seed':4,'policies':[{'id':'none','a1':0,'a2':0},{'id':'both','a1':1,'a2':1}]},19);assert dr['cross_fitted'] is True;assert dr['history_invariant']=='A1_POLICY_USES_BASELINE_ONLY__A2_POLICY_USES_BASELINE_A1_L1_ONLY';assert dr['policy_history_firewall']['a2_available_features']==['X','A1','L1']

# Caller attestations remain below trusted host qualification.
git_state=call('athena_git_status',{},20);promotion_head=git_state.get('head') or 'smokehead1234567';ci_packet={'observed':True,'ref':'ci://smoke-caller','head_sha':promotion_head,'conclusion':'success'};smoke_packet={'observed':True,'ref':'smoke://smoke-caller','head_sha':promotion_head,'conclusion':'success'}
promotion=call('athena_promotion_evaluate',{'git_head':promotion_head,'ci_witness':ci_packet,'smoke_witness':smoke_packet,'persist':False},21);assert promotion['status']=='ATTESTED_READY';assert promotion['promotion_allowed'] is False

semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
em=call('athena_finalize_output',{'semantic':semantic,'text':'Smoke V15 crystal T: x maps to y.','native_locator':'memory://smoke/v15','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'KC144':{'status':'RESOLVED','value':{'operator':'T'}}}},22);verified=call('athena_verify_emission',{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']},23);assert verified['verified'] is True

p.terminate();p.wait(timeout=5);print('SMOKE PASS: 3.4.0 / UNIFIED.11 / V15 WEIGHTED-CALIBRATION+HISTORY-SAFE-CROSS-FIT+STRICT-GAUSSIAN+LOCAL-ERROR-TRANSPORT+TV-DRO / DEPLOYMENT.2 / Y1+TRUST FIREWALLS')

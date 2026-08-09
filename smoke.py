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

init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'14'}},1);assert init['serverInfo']['version']=='3.3.0',init
p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
tools=rpc('tools/list',{},2)['tools'];names={x['name'] for x in tools}
for n in (
    'athena_orchestrate','athena_cycle_start','athena_self_test','athena_schema_migrate',
    'athena_belief_register','athena_decision_evi','athena_gp_register','athena_gp_predict',
    'athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover',
    'athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select',
    'athena_joint_factor_belief','athena_structural_bootstrap_ensemble','athena_joint_science_evi',
    'athena_sequential_dr_policy_value','athena_joint_policy_robust','athena_gp_resolution_route',
    'athena_two_stage_resource_plan','athena_discovery_claim_register','athena_claim_register',
    'athena_promotion_evaluate','athena_promotion_verify_github','athena_finalize_output',
):assert n in names,n

manifest=resource('athena://manifest',3);assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.10',manifest;assert 'COLLECTIVE_SYNTHESIS_V14' in manifest['layers'];assert 'GITHUB_PROMOTION_VERIFIER.1' in manifest['layers']
v14=resource('athena://collective/v14',4);assert v14['runtime']['version']=='COLLECTIVE_RUNTIME_V14';assert v14['runtime']['coordinate']=='COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>'

migration=call('athena_schema_migrate',{},5);assert migration['status'] in {'APPLIED','UP_TO_DATE'},migration
health=call('athena_self_test',{'replay_limit':5},6);assert health['status']=='PASS',health
aor=call('athena_orchestrate',{'seed':'SMOKE','candidates':[]},7);assert aor['run_id'].startswith('AORRUN.') and aor['next'] is None
cycle=call('athena_cycle_start',{'task_ref':'task://smoke','seed':'SMOKE','config':{'require_hug':True}},8);waiting=call('athena_cycle_advance',{'cycle_id':cycle['cycle_id'],'max_steps':16},9);assert waiting['status']=='WAITING_HUG_IMPLEMENTATION' and waiting['phase']=='HUG',waiting

# Finite joint science twin + EVI + robust policy remain read-only.
call('athena_claim_register',{'claim_id':'SMOKE.V14','source_ref':'smoke://v14'},10)
y_before=call('athena_claim_state',{'claim_id':'SMOKE.V14'},11)
joint=call('athena_joint_factor_belief',{'axes':{'M':[{'id':'M1','weight':.6},{'id':'M2','weight':.4}],'G':[{'id':'G1','weight':.5},{'id':'G2','weight':.5}]},'compatibility':[{'assignments':{'M':'M1','G':'G1'},'multiplier':2.0}]},12);assert joint['status']=='FINITE_JOINT_FACTOR_BELIEF';assert joint['state_count']==4
state_ids=[s['id'] for s in joint['states']]
evi=call('athena_joint_science_evi',{'joint_states':joint['states'],'actions':[{'id':'left','utility_by_state':{sid:(1 if 'M=M1' in sid else 0) for sid in state_ids}},{'id':'right','utility_by_state':{sid:(0 if 'M=M1' in sid else 1) for sid in state_ids}}],'experiments':[{'id':'probe','outcomes':{'yes':{sid:(.85 if 'M=M1' in sid else .15) for sid in state_ids},'no':{sid:(.15 if 'M=M1' in sid else .85) for sid in state_ids}}}]},13);assert evi['decision']=='FINITE_JOINT_SCIENCE_EVI_DESIGN_ONLY' and evi['winner']=='probe'
robpol=call('athena_joint_policy_robust',{'joint_states':joint['states'],'policies':[{'id':'stable','utility_by_state':{sid:.6 for sid in state_ids}},{'id':'spiky','utility_by_state':{sid:(1 if 'G=G1' in sid else 0) for sid in state_ids}}]},14);assert robpol['decision']=='FINITE_JOINT_SCENARIO_ROBUST_POLICY_PLAN_ONLY'
y_after=call('athena_claim_state',{'claim_id':'SMOKE.V14'},15);assert y_before==y_after

# GP V13 + V14 decision-relative zoom, with no self-training.
call('athena_gp_register',{'context_key':'SMOKE.GP','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.02},16)
for x,y,rid in ((0.0,0.0,17),(0.2,.04,18),(0.4,.16,19),(0.6,.36,20),(0.8,.64,21),(1.0,1.0,22)):
    call('athena_gp_observe',{'context_key':'SMOKE.GP','features':{'x':x},'target':y,'evidence_ref':'smoke://gp'},rid)
gp_before=call('athena_gp_state',{'context_key':'SMOKE.GP'},23);assert gp_before['observation_count']==6
qmc=call('athena_gp_hyperqmc',{'context_key':'SMOKE.GP','samples':40,'seed':2},24);assert qmc['status']=='QMC_CONTINUOUS_GP_HYPERPOSTERIOR_APPROXIMATION'
fitc=call('athena_gp_fitc_predict',{'context_key':'SMOKE.GP','features':{'x':.55},'inducing_count':3},25);assert fitc['status']=='FITC_INDUCING_GP_APPROXIMATION'
route=call('athena_gp_resolution_route',{'context_key':'SMOKE.GP','actions':[{'id':'low','features':{'x':.2}},{'id':'high','features':{'x':.9}}],'inducing_counts':[2,3,4,6],'margin_safety':.5},26);assert route['decision']=='GP_DECISION_RELATIVE_RESOLUTION_ROUTE';assert route['exact_winner']=='high';assert route['selected']['decision_preserving_on_queried_action_set'] is True
gp_after=call('athena_gp_state',{'context_key':'SMOKE.GP'},27);assert gp_before['observation_count']==gp_after['observation_count'];assert gp_before['length_scale']==gp_after['length_scale']

# Bootstrap structural ensemble remains outside JSPACE.
js_before=resource('athena://jspace',28);fci_rows=[]
for i in range(120):
    x=((i*13)%101)/50-1;y=((i*31)%103)/51-1;z=.9*x-.8*y+((i*7)%13-6)/500;fci_rows.append({'X':x,'Y':y,'Z':z})
ensemble=call('athena_structural_bootstrap_ensemble',{'samples':fci_rows,'variables':['X','Y','Z'],'bootstrap_runs':8,'alpha':.02,'max_conditioning':1,'seed':4},29);assert ensemble['status']=='BOOTSTRAP_FCI_LITE_STRUCTURAL_ENSEMBLE';assert ensemble['valid_runs']>=8
js_after=resource('athena://jspace',30);assert js_before['edges']==js_after['edges'];assert js_before['hyperedges']==js_after['hyperedges']

# Sequential DR policy value preserves temporal history and remains assumption-scoped.
long_rows=[]
for i in range(180):
    x=((i*17)%101)/100-.5;pa1=max(.1,min(.9,.45+.15*x));a1=1 if ((i*29)%100)/100<pa1 else 0;pl=max(.08,min(.92,.2+.35*a1+.15*x));l1=1 if ((i*37)%100)/100<pl else 0;pa2=max(.08,min(.92,.3+.15*a1+.25*l1+.1*x));a2=1 if ((i*41)%100)/100<pa2 else 0;py=max(.03,min(.97,.07+.1*a1+.16*l1+.48*a2+.08*x));y=1 if ((i*53)%100)/100<py else 0;long_rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
dr=call('athena_sequential_dr_policy_value',{'samples':long_rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'policies':[{'id':'never','a1':0,'a2':0},{'id':'always','a1':1,'a2':1}]},31);assert dr['status']=='TWO_TIMEPOINT_SEQUENTIAL_AIPW_POLICY_VALUE_UNDER_ASSUMPTIONS';assert dr['cross_fitted'] is False;assert 'OBSERVED_A1_L1' in dr['history_invariant']

# Finite two-stage recourse certificate.
recourse=call('athena_two_stage_resource_plan',{'first_stage':[{'id':'A','value':5,'resources':{'tokens':2}},{'id':'B','value':4,'resources':{'tokens':2}}],'scenarios':[{'id':'S1','probability':.5,'budgets':{'tokens':5},'recourse_options':[{'id':'R1','value':2,'resources':{'tokens':1}}]},{'id':'S2','probability':.5,'budgets':{'tokens':4},'recourse_options':[]}]},32);assert recourse['status']=='TWO_STAGE_RESOURCE_EXACT_ENUMERATION_CERTIFIED';assert recourse['certificate']=='EXACT_ENUMERATION_FOR_SUPPLIED_FINITE_TWO_STAGE_SCENARIO_MODEL'

# Final emission and trust separation.
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
em=call('athena_finalize_output',{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}},33);verified=call('athena_verify_emission',{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']},34);assert verified['verified'] is True
git_state=call('athena_git_status',{},35);promotion_head=git_state.get('head') or 'smokehead1234567';ci_packet={'observed':True,'ref':'ci://smoke-caller-attestation','head_sha':promotion_head,'conclusion':'success'};smoke_packet={'observed':True,'ref':'smoke://smoke-caller-attestation','head_sha':promotion_head,'conclusion':'success'}
promotion=call('athena_promotion_evaluate',{'git_head':promotion_head,'ci_witness':ci_packet,'smoke_witness':smoke_packet,'persist':False},36);assert promotion['status']=='ATTESTED_READY';assert promotion['promotion_allowed'] is False;assert promotion['gates']['external_verification']['status']=='MISSING'
promotion_resource=resource('athena://promotion',37);assert promotion_resource['github_verifier']['version']=='ATHENA.GITHUB.PROMOTION.VERIFIER.1';assert promotion_resource['github_verifier']['required_checks']==['syntax','unit','critical-invariants','smoke']

p.terminate();print('SMOKE PASS: V14 JOINT-BELIEF/STRUCTURAL-ENSEMBLE/JOINT-EVI/SEQUENTIAL-DR/ROBUST-POLICY/ADAPTIVE-ZOOM/TWO-STAGE-RECOURSE + V13 QMC/FITC + Y1/JSPACE/GP FIREWALLS + PROMOTION.2 HOST-BOUND VERIFIER SURFACE + SCHEMA/SELFTEST + AOR + FAIL-CLOSED CYCLE + FINAL EMISSION')

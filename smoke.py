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

init=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'3'}},1);assert init['serverInfo']['version']=='2.5.0',init
p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
tools=rpc('tools/list',{},2)['tools'];names={x['name'] for x in tools}
for n in ('athena_orchestrate','athena_cycle_start','athena_self_test','athena_schema_migrate','athena_bayes_predict','athena_experiment_design','athena_ood_score','athena_experiment_generate','athena_causal_identify','athena_dual_control_plan','athena_replication_independence','athena_discovery_claim_register','athena_claim_register','athena_finalize_output'):
    assert n in names,n
manifest=resource('athena://manifest',3);assert manifest['artifact']=='ATHENA.RUNTIME.UNIFIED.3',manifest;assert 'COLLECTIVE_DISCOVERY_V6' in manifest['layers'];assert 'COLLECTIVE_DUAL_CONTROL_V7' in manifest['layers'];assert 'AOR_DECISION_CORTEX' in manifest['layers']
v5=resource('athena://collective/v5',4);assert v5['runtime']['version']=='COLLECTIVE_RUNTIME_V5',v5
v6=resource('athena://collective/v6',5);assert v6['runtime']['version']=='COLLECTIVE_RUNTIME_V6',v6;assert v6['claim_namespace']['discovery_shadow_prefix']=='athena_discovery_claim_'
v7=resource('athena://collective/v7',6);assert v7['runtime']['version']=='COLLECTIVE_RUNTIME_V7',v7;assert 'plans/simulations are not execution' in v7['boundary']
migration=call('athena_schema_migrate',{},7);assert migration['status'] in {'APPLIED','UP_TO_DATE'},migration
health=call('athena_self_test',{'replay_limit':5},8);assert health['status']=='PASS',health
aor=call('athena_orchestrate',{'seed':'SMOKE','candidates':[]},9);assert aor['run_id'].startswith('AORRUN.'),aor;assert aor['next'] is None
cycle=call('athena_cycle_start',{'task_ref':'task://smoke','seed':'SMOKE','config':{'require_hug':True}},10);assert cycle['cycle_id'].startswith('CYCLE.'),cycle
waiting=call('athena_cycle_advance',{'cycle_id':cycle['cycle_id'],'max_steps':16},11);assert waiting['status']=='WAITING_HUG_IMPLEMENTATION',waiting;assert waiting['phase']=='HUG',waiting
design=call('athena_experiment_design',{'hypotheses':[{'id':'H1','prior':.5},{'id':'H2','prior':.5}],'experiments':[{'id':'E1','positive_probability':{'H1':.9,'H2':.1},'ethical':True,'cost':.1,'risk':.1}],'sample_size':10},12);assert design['decision']=='DESIGN_ONLY' and design['winner']=='E1',design
causal=call('athena_causal_identify',{'treatment':'T','outcome':'Y','edges':[{'src':'Z','dst':'T'},{'src':'Z','dst':'Y'},{'src':'T','dst':'Y'}],'observed_nodes':['T','Y','Z']},13);assert causal['status']=='IDENTIFIED_BACKDOOR' and ['Z'] in causal['minimal_adjustment_sets'],causal
transition=call('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}},14);assert transition['status']=='UNSEEN_ACTION',transition
dual=call('athena_dual_control_plan',{'initial_context':{'x':0.0},'actions':[{'id':'A','base_reward':.4},{'id':'B','base_reward':.6}],'horizon':2},15);assert dual['decision']=='DUAL_CONTROL_PROXY_PLAN_ONLY',dual;assert dual['first_action'] in {'A','B'};assert 'observe reality, and replan' in dual['law']
transition_after=call('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}},16);assert transition_after['status']=='UNSEEN_ACTION',transition_after
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
em=call('athena_finalize_output',{'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}},17)
assert em['envelope_id'].startswith('ENV.');assert em['emission_mid'].startswith('MID.');assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.');assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
verified=call('athena_verify_emission',{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']},18);assert verified['verified'] is True
p.terminate(); print('SMOKE PASS: V5 SCIENCE + V6 DISCOVERY + V7 DUAL-CONTROL + SCHEMA/SELFTEST + AOR + FAIL-CLOSED CYCLE + FINAL EMISSION')

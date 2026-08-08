import json, os, subprocess, sys, tempfile
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
semantic={'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'FINAL_EMISSION','input_contract':{},'output_contract':{}}
msgs=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://manifest'}},
 {'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':'athena://collective/v4'}},
 {'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'athena_regime_resolve','arguments':{'signals':{'uncertainty':.8,'volatility':.7,'divisibility':.8,'coupling':.2}}}},
 {'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'athena_finalize_output','arguments':{
   'semantic':semantic,'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,
   'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],
   'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}
 }}}
]
for m in msgs:p.stdin.write(json.dumps(m)+'\n')
p.stdin.flush()
responses=[]
for _ in range(6):
 r=json.loads(p.stdout.readline()); assert r.get('error') is None,r; responses.append(r)
init=responses[0]['result']; assert init['serverInfo']['version']=='2.3.0',init
names={x['name'] for x in responses[1]['result']['tools']}; assert 'athena_bandit_select' in names; assert 'athena_topology_project_jspace' in names
v4=json.loads(responses[3]['result']['contents'][0]['text']); assert v4['runtime']['version']=='COLLECTIVE_RUNTIME_V4',v4
regime=responses[4]['result']['structuredContent']; assert regime['regime'].startswith('REGIME/'),regime
em=responses[-1]['result']['structuredContent']; assert em['envelope_id'].startswith('ENV.'); assert em['emission_mid'].startswith('MID.'); assert em['visible_text'].startswith('⟦ATHENA::CRYSTAL::CRYS.'); assert em['manifest']['coordinates']['BR21']['status']=='RESOLVED'
p.stdin.write(json.dumps({'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'athena_verify_emission','arguments':{'envelope_id':em['envelope_id'],'visible_text':em['visible_text']}}})+'\n');p.stdin.flush();v=json.loads(p.stdout.readline());assert v['result']['structuredContent']['verified'] is True
p.terminate(); print('SMOKE PASS: V4 MCP + FINALIZE_OUTPUT + VERIFY_EMISSION')

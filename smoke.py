import json, os, subprocess, sys, tempfile
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
msgs=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://manifest'}},
 {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'athena_crystallize_output','arguments':{
   'semantic':{'kind':'ARTIFACT','domain':'SMOKE','verb':'TEST','object_name':'OUTPUT','method':'CRYSTAL','input_contract':{},'output_contract':{}},
   'text':'Smoke crystal T: x maps to y.','native_locator':'memory://smoke','agent':'SMOKE','task':'ci','seq':1,
   'math_objects':[{'kind':'OPERATOR','symbol':'T','latex':'T:x\\mapsto y'}],
   'coordinates':{'BR21':{'status':'RESOLVED','value':{'operator':'T'}}}
 }}}
]
for m in msgs:p.stdin.write(json.dumps(m)+'\n')
p.stdin.flush()
responses=[]
for _ in range(4):
 r=json.loads(p.stdout.readline()); assert r.get('error') is None,r; responses.append(r)
cr=responses[-1]['result']['structuredContent']; assert cr['crystal_id'].startswith('CRYS.'); assert 'KC144=' in cr['header']; assert cr['manifest']['coordinates']['BR21']['status']=='RESOLVED'
p.terminate(); print('SMOKE PASS: CRYSTALLIZE_OUTPUT')

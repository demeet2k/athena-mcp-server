import json, os, subprocess, sys, tempfile
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd); os.unlink(path)
p=subprocess.Popen([sys.executable,'-m','athena_mcp','--db',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
msgs=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'smoke','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'resources/read','params':{'uri':'athena://manifest'}}]
for m in msgs:p.stdin.write(json.dumps(m)+'\n')
p.stdin.flush()
for _ in range(3):
 r=json.loads(p.stdout.readline()); assert r.get('error') is None,r
p.terminate(); print('SMOKE PASS')

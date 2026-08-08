import os, subprocess, tempfile, unittest
from pathlib import Path
from athena_mcp.store import Store
from athena_mcp.core import AthenaCore, StaleTarget
from athena_mcp.server import Server
class RuntimeTests(unittest.TestCase):
 def test_registry_stale_text_simplex(self):
  with tempfile.NamedTemporaryFile(suffix='.db') as f:
   s=Store(f.name); c=AthenaCore(s); r=c.register('TOOL','TEST','MEASURE','STATE','EXACT',{},{}); self.assertEqual(c.register('TOOL','TEST','MEASURE','STATE','EXACT',{}, {})['action'],'REUSE'); oid=r['object']['oid']; vid=r['version']['vid']; c.commit_delta(oid,vid,{'x':1});
   with self.assertRaises(StaleTarget): c.commit_delta(oid,vid,{'x':2})
   r2=c.register('ARTIFACT','TEXT','INDEX','OUTPUT','LEXEME_COORDS',{},{}); x=c.ingest_text(r2['object']['oid'],r2['version']['vid'],'Hello, world. Again!','memory://demo'); self.assertIn('/C:',x['first_coordinate']); self.assertEqual(c.form_simplex(['a','b','c'],'t','x')['dimension'],2); s.close()
 def test_mcp_and_bootstrap(self):
  with tempfile.NamedTemporaryFile(suffix='.db') as f:
   srv=Server(f.name); self.assertEqual(srv.core.benchmark()['objects'],12); r=srv.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}}); self.assertEqual(r['result']['protocolVersion'],'2025-11-25'); names=[x['name'] for x in srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']]; self.assertEqual(names,sorted(names)); srv.store.close()
 def test_git_cas(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'brain'; root.mkdir(); subprocess.run(['git','init','-b','main',root],check=True,capture_output=True); (root/'README.md').write_text('x'); subprocess.run(['git','-C',root,'add','.'],check=True); env=os.environ|{'GIT_AUTHOR_NAME':'t','GIT_AUTHOR_EMAIL':'t@x','GIT_COMMITTER_NAME':'t','GIT_COMMITTER_EMAIL':'t@x'}; subprocess.run(['git','-C',root,'commit','-m','genesis'],check=True,capture_output=True,env=env); srv=Server(str(Path(td)/'a.db'),str(root)); head=srv.git.head(); ss=srv.core.session_start('A1','task',head); end=srv.core.session_end(ss['session_id'],{'delta':'ok'},head); out=srv.git.checkpoint(head,srv.core.event(end['end_eid']),srv.core.hydrate(),actor='A1'); self.assertEqual(out['status'],'COMMITTED');
   with self.assertRaises(Exception): srv.git.checkpoint(head,srv.core.event(end['end_eid']),srv.core.hydrate(),actor='A1')
   srv.store.close()
if __name__=='__main__': unittest.main()

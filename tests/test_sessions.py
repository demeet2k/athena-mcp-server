import os, subprocess, tempfile, unittest
from pathlib import Path
from athena_mcp.server import Server

class SessionTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(); root=Path(self.t.name)/'brain'; root.mkdir(); subprocess.run(['git','init','-b','main',root],check=True,capture_output=True)
        (root/'README.md').write_text('x')
        subprocess.run(['git','-C',root,'add','.'],check=True)
        env=os.environ|{'GIT_AUTHOR_NAME':'t','GIT_AUTHOR_EMAIL':'t@x','GIT_COMMITTER_NAME':'t','GIT_COMMITTER_EMAIL':'t@x'}
        subprocess.run(['git','-C',root,'commit','-m','genesis'],check=True,capture_output=True,env=env)
        self.server=Server(str(Path(self.t.name)/'a.db'),str(root)); self.root=root
    def tearDown(self): self.server.store.close(); self.t.cleanup()
    def test_bootstrap_and_git_cas(self):
        b=self.server.core.benchmark(); self.assertGreaterEqual(b['objects'],16); caps=[r['canonical_name'] for r in self.server.core.s.search('CRYSTAL_EMISSION_GATEWAY',20)]; self.assertTrue(any('CRYSTAL_EMISSION_GATEWAY' in n for n in caps))
        st=self.server.git.status(); self.assertTrue(st['enabled']); head=st['head']
        ss=self.server.core.session_start('A1','task',head)
        end=self.server.core.session_end(ss['session_id'],{'delta':'ok'},head)
        ev=self.server.core.event(end['end_eid'])
        out=self.server.git.checkpoint(head,ev,self.server.core.hydrate(),actor='A1'); self.assertEqual(out['status'],'COMMITTED')
        with self.assertRaises(Exception): self.server.git.checkpoint(head,ev,self.server.core.hydrate(),actor='A1')

if __name__=='__main__': unittest.main()

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.core import StaleTarget
from athena_mcp.server import Server


class ThreeDomainCASUnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name);self.db=str(root/'athena.db');self.git_root=root/'brain';self.git_root.mkdir()
        subprocess.run(['git','init','-b','main',str(self.git_root)],check=True,capture_output=True)
        (self.git_root/'README.md').write_text('genesis\n')
        subprocess.run(['git','-C',str(self.git_root),'add','.'],check=True)
        self.git_env=os.environ|{'GIT_AUTHOR_NAME':'ATHENA TEST','GIT_AUTHOR_EMAIL':'athena@example.invalid','GIT_COMMITTER_NAME':'ATHENA TEST','GIT_COMMITTER_EMAIL':'athena@example.invalid'}
        subprocess.run(['git','-C',str(self.git_root),'commit','-m','genesis'],check=True,capture_output=True,env=self.git_env)
        self.server=Server(self.db,str(self.git_root))
        registered=self.server.core.register('ARTIFACT','CAS','TRACK','OBJECT','THREE_DOMAIN',{}, {},actor='TEST')
        self.oid=registered['object']['oid'];self.initial_vid=registered['version']['vid']
        self.initial_topology=self.server.collective_memory.topology_apply('TOPO.CAS',0,'INIT',{'modules':[{'id':'M1','role':'test'}],'edges':[]},'TEST')
    def tearDown(self):
        try:self.server.store.close()
        except Exception:pass
        self.tmp.cleanup()

    def semantic_head(self):
        nav=self.server.core.navigate(self.oid);self.assertTrue(nav['found']);return nav['head']['vid']
    def topology_state(self):return self.server.collective_memory.topology_get('TOPO.CAS')
    def git_head(self):return self.server.git.head()

    def test_stale_semantic_vid_does_not_mutate_git_or_topology(self):
        git_before=self.git_head();topo_before=self.topology_state();ok=self.server.core.commit_delta(self.oid,self.initial_vid,{'step':1},actor='TEST');self.assertNotEqual(ok['version']['vid'],self.initial_vid)
        git_after_success=self.git_head();topo_after_success=self.topology_state();self.assertEqual(git_before,git_after_success);self.assertEqual(topo_before,topo_after_success)
        with self.assertRaises(StaleTarget):self.server.core.commit_delta(self.oid,self.initial_vid,{'step':2},actor='TEST')
        self.assertEqual(self.git_head(),git_after_success);self.assertEqual(self.topology_state(),topo_after_success);self.assertEqual(self.semantic_head(),ok['version']['vid'])

    def test_stale_topology_version_does_not_mutate_semantic_or_git(self):
        semantic_before=self.semantic_head();git_before=self.git_head();before=self.topology_state();current_version=before['version']
        with self.assertRaises(Exception):self.server.collective_memory.topology_apply('TOPO.CAS',0,'REPLACE',{'modules':[{'id':'M2','role':'stale'}],'edges':[]},'TEST')
        self.assertEqual(self.topology_state(),before);self.assertEqual(self.semantic_head(),semantic_before);self.assertEqual(self.git_head(),git_before);self.assertGreaterEqual(current_version,1)

    def test_stale_git_head_does_not_mutate_semantic_or_topology(self):
        semantic_before=self.semantic_head();topo_before=self.topology_state();head=self.git_head();session=self.server.core.session_start('CAS.AGENT','git mutation',head);ended=self.server.core.session_end(session['session_id'],{'delta':'first'},head);event=self.server.core.event(ended['end_eid'])
        committed=self.server.git.checkpoint(head,event,self.server.core.hydrate(),actor='CAS.AGENT',message='first checkpoint');self.assertEqual(committed['status'],'COMMITTED');new_head=self.git_head();self.assertNotEqual(new_head,head)
        semantic_after_commit=self.semantic_head();topo_after_commit=self.topology_state();self.assertEqual(semantic_after_commit,semantic_before);self.assertEqual(topo_after_commit,topo_before)
        with self.assertRaises(Exception):self.server.git.checkpoint(head,event,self.server.core.hydrate(),actor='CAS.AGENT',message='stale checkpoint')
        self.assertEqual(self.git_head(),new_head);self.assertEqual(self.semantic_head(),semantic_after_commit);self.assertEqual(self.topology_state(),topo_after_commit)

    def test_domains_can_advance_independently_when_each_cas_is_current(self):
        semantic=self.server.core.commit_delta(self.oid,self.initial_vid,{'semantic':1},actor='TEST');semantic_vid=semantic['version']['vid'];topo_before=self.topology_state();topo_version=topo_before['version'];self.server.collective_memory.topology_apply('TOPO.CAS',topo_version,'REPLACE',{'modules':[{'id':'M2','role':'current'}],'edges':[]},'TEST');head=self.git_head();session=self.server.core.session_start('CAS.AGENT','independent current writes',head);ended=self.server.core.session_end(session['session_id'],{'delta':'git'},head);git=self.server.git.checkpoint(head,self.server.core.event(ended['end_eid']),self.server.core.hydrate(),actor='CAS.AGENT',message='independent checkpoint')
        self.assertEqual(self.semantic_head(),semantic_vid);self.assertGreater(self.topology_state()['version'],topo_version);self.assertEqual(git['status'],'COMMITTED');self.assertNotEqual(self.git_head(),head)


if __name__=='__main__':unittest.main()

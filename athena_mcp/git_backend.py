from __future__ import annotations
import json, os, subprocess
from pathlib import Path
class GitStateError(RuntimeError): pass
class GitStaleHead(GitStateError): pass
class GitBackend:
    def __init__(self,root=None,autocommit=False):
        self.root=Path(root).resolve() if root else None; self.autocommit=bool(autocommit)
        if self.root and not (self.root/'.git').exists(): raise GitStateError(f'ATHENA_GIT_ROOT is not a git checkout: {self.root}')
    @property
    def enabled(self): return self.root is not None
    def _git(self,*args):
        p=subprocess.run(['git','-C',str(self.root),*args],text=True,capture_output=True)
        if p.returncode: raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return p.stdout.strip()
    def head(self): return self._git('rev-parse','HEAD') if self.enabled else None
    def status(self):
        if not self.enabled:return {'enabled':False}
        return {'enabled':True,'root':str(self.root),'head':self.head(),'branch':self._git('branch','--show-current'),'dirty':bool(self._git('status','--porcelain'))}
    def checkpoint(self,expected_head,event,snapshot,actor='ATHENA',message=None):
        if not self.enabled:return {'status':'DISABLED'}
        current=self.head()
        if current!=expected_head: raise GitStaleHead(json.dumps({'status':'STALE_GIT_HEAD','expected':expected_head,'current':current}))
        eid=event['eid']; evdir=self.root/'ledger'/'events'/eid[:8]; evdir.mkdir(parents=True,exist_ok=True)
        (evdir/f'{eid}.json').write_text(json.dumps(event,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
        statedir=self.root/'ledger'/'state'; statedir.mkdir(parents=True,exist_ok=True)
        (statedir/'HEAD.json').write_text(json.dumps(snapshot,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
        self._git('add','ledger')
        if not self._git('status','--porcelain'): return {'status':'NO_CHANGES','head':current}
        env=os.environ.copy(); env.setdefault('GIT_AUTHOR_NAME',actor); env.setdefault('GIT_AUTHOR_EMAIL','athena@local'); env.setdefault('GIT_COMMITTER_NAME',actor); env.setdefault('GIT_COMMITTER_EMAIL','athena@local')
        p=subprocess.run(['git','-C',str(self.root),'commit','-m',message or f'athena event {eid}'],text=True,capture_output=True,env=env)
        if p.returncode: raise GitStateError(p.stderr.strip() or p.stdout.strip())
        return {'status':'COMMITTED','head':self.head(),'previous_head':current}

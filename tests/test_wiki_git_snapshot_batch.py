import hashlib
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from athena_mcp.wiki_git_draft import _git
from athena_mcp.wiki_git_snapshot import read_snapshot


def oid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def fixture(paths):
    objects={oid(raw):raw for raw in paths.values()}
    tree=b''.join(f'100644 blob {oid(raw)} {len(raw)}\t{path}'.encode()+b'\0'
                  for path,raw in paths.items())
    batch=b''.join(f'{key} blob {len(raw)}\n'.encode()+raw+b'\n' for key,raw in objects.items())
    return tree,batch


class BatchSnapshotTests(unittest.TestCase):
    def read(self,tree,batch):
        calls=[]
        def run(*args,input=None):
            calls.append((args,input))
            return tree if args[0]=='ls-tree' else batch
        result=read_snapshot(SimpleNamespace(root='unused'),'HEAD',run=run)
        return result,calls

    def test_binary_delimiters_empty_and_shared_objects_are_exact(self):
        paths={'knowledge/raw/a':b'\0\xff\n\r\n', 'knowledge/raw/b':b'',
               'knowledge/raw/shared':b'\0\xff\n\r\n', 'knowledge/wiki/note.md':'\u03a9\r\n'.encode()}
        result,calls=self.read(*fixture(paths))
        self.assertEqual(result,{**paths,'knowledge/wiki/note.md':'\u03a9\r\n'})
        self.assertEqual(len(calls),2)
        self.assertEqual(calls[1][1].splitlines(),[key.encode() for key in dict.fromkeys(oid(x) for x in paths.values())])

    def test_total_path_size_is_checked_before_any_payload_read(self):
        tree,batch=fixture({'knowledge/raw/a':b'ab','knowledge/raw/b':b'ab'})
        called=[]
        def run(*args,**kwargs):
            called.append(args)
            self.assertEqual(args[0],'ls-tree')
            return tree
        with patch('athena_mcp.wiki_git_snapshot.MAX_BYTES',3),self.assertRaisesRegex(ValueError,'SNAPSHOT_TOO_LARGE'):
            read_snapshot(SimpleNamespace(root='unused'),'HEAD',run=run)
        self.assertEqual(len(called),1)

    def test_empty_tree_never_starts_batch_reader(self):
        result,calls=self.read(b'',b'')
        self.assertEqual(result,{})
        self.assertEqual(len(calls),1)

    def test_batch_identity_content_and_framing_fail_closed(self):
        tree,batch=fixture({'knowledge/raw/a':b'abc'})
        cases=[(batch.replace(oid(b'abc').encode(),b'0'*40),'BATCH_OBJECT'),
               (batch.replace(b' blob ',b' tree '),'BATCH_OBJECT'),
               (batch.replace(b'blob 3\n',b'blob 4\n'),'BATCH_OBJECT'),
               (batch.replace(b'abc',b'abd'),'BLOB_OBJECT'),
               (batch[:-2],'BLOB_SIZE'),(batch[:-1]+b'x','BLOB_SIZE'),
               (batch+b'extra','BATCH_TRAILING'),(b'missing\n','BATCH_OBJECT')]
        for damaged,error in cases:
            with self.subTest(error=error,damaged=damaged),self.assertRaisesRegex(ValueError,error):
                self.read(tree,damaged)

    def test_unsafe_or_ambiguous_tree_is_rejected_before_batch(self):
        tree,batch=fixture({'knowledge/raw/a':b'x'})
        cases=[(tree.replace(b'100644',b'120000'),'NONREGULAR'),
               (tree+tree.replace(b'/a\0',b'/A\0'),'COLLIDING'),
               (tree.replace(b'knowledge/raw/a',b'knowledge/raw/../a'),'UNSAFE'),
               (tree.replace(b' 1\t',b' -1\t'),'MALFORMED_TREE'),
               (tree.replace(oid(b'x').encode(),b'not-an-object'),'MALFORMED_TREE')]
        for damaged,error in cases:
            with self.subTest(error=error),self.assertRaisesRegex(ValueError,error):
                self.read(damaged,batch)

    def test_real_git_many_files_and_default_replacement_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def git(*args):
                return _git(root,*args).stdout.decode('ascii').strip()
            git('init','-q');git('config','user.email','fixture@example.invalid');git('config','user.name','Fixture')
            git('config','core.autocrlf','false')
            paths={f'knowledge/raw/file-{i}':bytes([i])+b'\0\r\n' for i in range(32)}
            paths['knowledge/raw/space \u03a9']=b'\xff\n'
            for path,raw in paths.items():
                p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            git('add','.');git('commit','-qm','original');head=git('rev-parse','HEAD')
            (root/'knowledge/raw/file-0').write_bytes(b'substitute')
            git('add','.');git('commit','-qm','later');later=git('rev-parse','HEAD')
            git('replace',head,later)
            calls=[]
            def run(*args,**kwargs):
                calls.append(args)
                return _git(root,*args,**kwargs).stdout
            before=git('status','--porcelain'),git('show-ref')
            self.assertEqual(read_snapshot(SimpleNamespace(root=root),head,run=run),paths)
            self.assertEqual(len(calls),2)
            with patch.dict(os.environ,{'GIT_DIR':str(root/'absent'),'GIT_NO_REPLACE_OBJECTS':'0'}):
                self.assertEqual(read_snapshot(SimpleNamespace(root=root),head),paths)
            self.assertEqual(before,(git('status','--porcelain'),git('show-ref')))


if __name__=='__main__':
    unittest.main()

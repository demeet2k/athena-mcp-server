"""Read a complete committed Wiki and simulate guarded mutation plans."""
import hashlib
import json
from pathlib import PurePosixPath
import re
import subprocess

MAX_BYTES = 8_000_000


def sha(text):
    return 'sha256:' + hashlib.sha256(text if type(text) is bytes else text.encode('utf-8')).hexdigest()


def safe_path(path):
    if (type(path) is not str or not path.startswith('knowledge/')
            or '\\' in path or ':' in path or any(ord(c)<32 for c in path)
            or any(p in ('', '.', '..') for p in path.split('/'))):
        raise ValueError('WIKI_BRIDGE_UNSAFE_PATH')
    return path


def parse_page(path, text):
    """Read the declared metadata carrier; never guess an untyped page's fields."""
    match = re.match(r'\A<!-- ATHENA-WIKI-META\r?\n(.*?)\r?\n-->\r?\n\r?\n# ([^\r\n]+)\r?\n\r?\n([^\r\n]+)', text, re.S)
    if not match:
        raise ValueError('WIKI_BRIDGE_PAGE_METADATA_REQUIRED:'+path)
    meta = json.loads(match[1])
    allowed = {'page_id','page_type','created_at','updated_at','source_ids','claim_ids','tags','links'}
    if type(meta) is not dict or set(meta)!=allowed:
        raise ValueError('WIKI_BRIDGE_PAGE_METADATA_SHAPE:'+path)
    return {**meta, 'path':path, 'title':match[2].replace('\\[','[').replace('\\]',']'), 'summary':match[3]}


def config_from_schema(schema):
    if schema.get('schema')!='ATHENA.INTERNAL.WIKI.SCHEMA.V1' or schema.get('version')!='1.0.0':
        raise ValueError('WIKI_BRIDGE_SCHEMA_UNSUPPORTED')
    config = {'name':schema['name'],'domain':schema['domain'],'root':'knowledge',
              'raw_root':schema['layers']['raw']['path'],'wiki_root':schema['layers']['wiki']['path'],
              'schema_path':schema['layers']['schema']['path'],'page_types':schema['page_types']}
    for key, field in [('index_path','index'),('log_path','log'),('source_ledger_path','sources'),('claim_ledger_path','claims'),('contradiction_ledger_path','contradictions')]:
        config[key]=safe_path(schema['special_files'][field])
    config['meta_root']=str(PurePosixPath(config['source_ledger_path']).parent)
    if config['raw_root']!='knowledge/raw' or config['wiki_root']!='knowledge/wiki' or config['schema_path']!='knowledge/WIKI.schema.json':
        raise ValueError('WIKI_BRIDGE_CANONICAL_ROOT_REQUIRED')
    return config


def decode_snapshot(files):
    config=config_from_schema(json.loads(files['knowledge/WIKI.schema.json']))
    def ledger(key):
        rows=[json.loads(line) for line in files[config[key]].splitlines() if line.strip()]
        if any(type(row) is not dict for row in rows):
            raise ValueError('WIKI_BRIDGE_LEDGER_OBJECT_REQUIRED')
        return rows
    sources,claims,contradictions=[ledger(k) for k in ('source_ledger_path','claim_ledger_path','contradiction_ledger_path')]
    special={config['index_path'],config['log_path'],config['meta_root']+'/README.md'}
    pages=[]
    for path,text in sorted(files.items()):
        if path.startswith(config['wiki_root']+'/') and path.endswith('.md') and path not in special:
            pages.append(parse_page(path,text))
    for source in sources:
        path=safe_path(source['raw_path'])
        if not path.startswith(config['raw_root']+'/') or path not in files or sha(files[path])!=source['content_sha256']:
            raise ValueError('WIKI_BRIDGE_RAW_CARRIER_MISMATCH:'+path)
    return dict(config=config,pages=pages,sources=sources,claims=claims,contradictions=contradictions)


def read_snapshot(git, head):
    def run(*args):
        return subprocess.check_output(['git','-C',str(git.root),*args],timeout=30)
    tree=run('ls-tree','-r','-z',head,'--','knowledge/WIKI.schema.json','knowledge/raw','knowledge/wiki')
    files={}; folded=set(); total=0
    for entry in tree.split(b'\0'):
        if not entry: continue
        record,raw_path=entry.split(b'\t',1)
        mode,kind,oid=record.decode('ascii').split()
        path=safe_path(raw_path.decode('utf-8'))
        if kind!='blob' or mode not in ('100644','100755') or path.casefold() in folded:
            raise ValueError('WIKI_BRIDGE_NONREGULAR_OR_COLLIDING_PATH')
        folded.add(path.casefold())
        size=int(run('cat-file','-s',oid))
        total+=size
        if total>MAX_BYTES: raise ValueError('WIKI_BRIDGE_SNAPSHOT_TOO_LARGE')
        raw=run('cat-file','blob',oid)
        if len(raw)!=size: raise ValueError('WIKI_BRIDGE_BLOB_SIZE_MISMATCH')
        # Binary immutable carriers are valid. Keep bytes separately and decode
        # only semantic text; source-carrier verification uses exact raw bytes.
        files[path]=raw
    text_files={p:b.decode('utf-8') for p,b in files.items() if not p.startswith('knowledge/raw/')}
    # decode_snapshot receives raw carriers as bytes when they are binary.
    text_files.update({p:b for p,b in files.items() if p.startswith('knowledge/raw/')})
    return text_files


def simulate(files, plan):
    out=dict(files)
    for step in plan:
        path=safe_path(step['path']); action=step['action']; old=out.get(path)
        if action=='REINDEX_REQUIRED': continue
        if path.startswith('knowledge/raw/') and old is not None and action not in ('VERIFY_EXISTING_IMMUTABLE','CREATE_IF_ABSENT'):
            raise ValueError('WIKI_BRIDGE_RAW_IMMUTABLE')
        if action=='VERIFY_EXISTING_IMMUTABLE':
            if old is None or sha(old)!=step['expected_sha256']: raise ValueError('WIKI_BRIDGE_RAW_VERIFY_FAILED')
        elif action in ('CREATE','CREATE_IF_ABSENT'):
            if old is not None and (action=='CREATE' or old!=step['content']): raise ValueError('WIKI_BRIDGE_CREATE_CONFLICT')
            out[path]=step['content']
        elif action=='REPLACE_IF_DIGEST':
            if old is None or sha(old)!=step['expected_sha256']: raise ValueError('WIKI_BRIDGE_REPLACE_CONFLICT')
            if path.startswith('knowledge/raw/'): raise ValueError('WIKI_BRIDGE_RAW_IMMUTABLE')
            out[path]=step['content']
        elif action=='APPEND':
            if type(old) is not str: raise ValueError('WIKI_BRIDGE_APPEND_TARGET_MISSING')
            out[path]=old+step['content']
        elif action=='APPEND_UNIQUE_JSONL':
            if type(old) is not str: raise ValueError('WIKI_BRIDGE_LEDGER_TARGET_MISSING')
            key=step['identity_field']; record=step['record']
            if any(json.loads(line).get(key)==record[key] for line in old.splitlines() if line.strip()):
                raise ValueError('WIKI_BRIDGE_LEDGER_ID_EXISTS')
            out[path]=old+('' if not old or old.endswith('\n') else '\n')+json.dumps(record,sort_keys=True,ensure_ascii=False)+'\n'
        else: raise ValueError('WIKI_BRIDGE_ACTION_UNSUPPORTED:'+action)
    return out

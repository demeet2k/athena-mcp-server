from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from athena_mcp.server import Server


def git_head(root: str) -> str:
    return subprocess.check_output(['git','-C',root,'rev-parse','HEAD'],text=True).strip()


def main(argv=None):
    parser=argparse.ArgumentParser(description='Create and replay one host-verified GitHub PROMOTION.2 receipt for the exact checked-out head.')
    parser.add_argument('--git-root',default='.')
    parser.add_argument('--db')
    parser.add_argument('--output',default='promotion-receipt.json')
    parser.add_argument('--actor',default='GITHUB.ACTIONS.PROMOTION.VERIFIER')
    parser.add_argument('--attempts',type=int,default=8)
    parser.add_argument('--retry-delay',type=float,default=3.0)
    args=parser.parse_args(argv)
    root=str(Path(args.git_root).resolve());head=str(os.getenv('ATHENA_PROMOTION_HEAD') or os.getenv('GITHUB_SHA') or git_head(root)).strip();checkout=git_head(root)
    if checkout!=head:raise SystemExit(f'checked-out Git head does not match trusted promotion head: checkout={checkout} requested={head}')
    if not (os.getenv('ATHENA_GITHUB_REPOSITORY') or os.getenv('GITHUB_REPOSITORY')):raise SystemExit('trusted GitHub repository environment is required')
    if args.db:db=args.db
    else:
        fd,db=tempfile.mkstemp(suffix='.db');os.close(fd);os.unlink(db)
    server=Server(db,git_root=root)
    try:
        qualified=None;history=[]
        for attempt in range(1,max(1,args.attempts)+1):
            qualified=server.call_tool('athena_promotion_verify_github',{'git_head':head,'actor':args.actor,'persist':True})
            history.append({'attempt':attempt,'status':qualified.get('status'),'github_status':(qualified.get('github_verification') or {}).get('status')})
            if qualified.get('status')=='QUALIFIED' and qualified.get('promotion_allowed') is True:break
            if attempt<max(1,args.attempts):time.sleep(max(0.0,args.retry_delay))
        if qualified is None or qualified.get('status')!='QUALIFIED' or qualified.get('promotion_allowed') is not True:raise SystemExit('trusted GitHub qualification failed: '+json.dumps({'history':history,'last':qualified},sort_keys=True))
        run_id=qualified.get('run_id')
        if not run_id:raise SystemExit('qualified promotion did not persist PROMRUN')
        replay=server.call_tool('athena_promotion_replay',{'run_id':run_id})
        if replay.get('match') is not True or replay.get('stored_status')!='QUALIFIED' or replay.get('recomputed_status')!='QUALIFIED':raise SystemExit('trusted promotion replay failed: '+json.dumps(replay,sort_keys=True))
        receipt={'artifact':'ATHENA.GITHUB.PROMOTION.RECEIPT.1','repository':qualified['github_verification']['repository'],'git_head':head,'github_run_id':qualified['github_verification'].get('run_id'),'check_suite_id':qualified['github_verification'].get('check_suite_id'),'verification_ref':qualified['github_verification'].get('verification_ref'),'observation_attempts':history,'promotion':qualified,'replay':replay,'law':'receipt was produced only after the runtime independently fetched the host-configured GitHub check data and observed one coherent exact-head run/suite with syntax, unit, critical-invariants and smoke completed success; retries only tolerate check-index propagation and never weaken the coherent-suite requirement'}
        Path(args.output).write_text(json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps({'status':'QUALIFIED','run_id':run_id,'git_head':head,'output':args.output,'verification_ref':receipt['verification_ref'],'attempts':len(history)},sort_keys=True))
    finally:server.store.close()

if __name__=='__main__':main()

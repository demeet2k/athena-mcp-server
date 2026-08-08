from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import Any,Callable,Mapping

GITHUB_PROMOTION_VERIFIER_VERSION='ATHENA.GITHUB.PROMOTION.VERIFIER.1'
REQUIRED_CHECKS=('syntax','unit','critical-invariants','smoke')
_REPO_RE=re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
_SHA_RE=re.compile(r'^[0-9a-fA-F]{7,64}$')


class GithubPromotionVerifier:
    """Host-bound independent GitHub check-suite verifier for PROMOTION.2."""

    def __init__(self,env:Mapping[str,str] | None=None,fetch_json:Callable[...,Any] | None=None):
        self.env=dict(os.environ if env is None else env)
        self._fetch_json=fetch_json or self._network_fetch_json

    def _repository(self)->str | None:
        value=str(self.env.get('ATHENA_GITHUB_REPOSITORY') or self.env.get('GITHUB_REPOSITORY') or '').strip()
        return value if _REPO_RE.fullmatch(value) else None

    def _api_base(self)->str:
        value=str(self.env.get('ATHENA_GITHUB_API_URL') or self.env.get('GITHUB_API_URL') or 'https://api.github.com').strip().rstrip('/')
        if not value.startswith('https://'):raise ValueError('trusted GitHub API URL must use https')
        return value

    def _token(self)->str:
        return str(self.env.get('ATHENA_GITHUB_TOKEN') or self.env.get('GITHUB_TOKEN') or '').strip()

    def _run_id(self)->str | None:
        value=str(self.env.get('ATHENA_GITHUB_RUN_ID') or self.env.get('GITHUB_RUN_ID') or '').strip()
        return value or None

    def describe(self)->dict[str,Any]:
        repo=self._repository();run_id=self._run_id()
        return {
            'version':GITHUB_PROMOTION_VERIFIER_VERSION,'configured':repo is not None,'repository':repo,
            'api_base':self._api_base() if repo else None,'run_id_bound':run_id is not None,'run_id':run_id,
            'required_checks':list(REQUIRED_CHECKS),'trusted_app_slug':'github-actions','token_configured':bool(self._token()),
            'law':'trusted repository/API/run context comes from host environment; caller supplies only target head; qualification requires one coherent GitHub Actions run/check-suite whose syntax, unit, critical-invariants and smoke checks all completed success on that exact head',
        }

    @staticmethod
    def _network_fetch_json(url:str,headers:Mapping[str,str],timeout_s:float)->Any:
        req=urllib.request.Request(url,headers=dict(headers),method='GET')
        try:
            with urllib.request.urlopen(req,timeout=timeout_s) as response:return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as exc:
            if exc.code in {401,403} and 'Authorization' in headers:
                fallback={k:v for k,v in headers.items() if k!='Authorization'}
                req2=urllib.request.Request(url,headers=fallback,method='GET')
                with urllib.request.urlopen(req2,timeout=timeout_s) as response:return json.loads(response.read().decode('utf-8'))
            raise

    @staticmethod
    def _snapshot(run:Mapping[str,Any])->dict[str,Any]:
        app=dict(run.get('app') or {});suite=dict(run.get('check_suite') or {})
        return {'id':run.get('id'),'name':run.get('name'),'status':run.get('status'),'conclusion':run.get('conclusion'),'head_sha':run.get('head_sha'),'html_url':run.get('html_url'),'details_url':run.get('details_url'),'check_suite_id':suite.get('id'),'app_slug':app.get('slug'),'started_at':run.get('started_at'),'completed_at':run.get('completed_at')}

    def verify(self,git_head:str,timeout_s:float=12.0)->dict[str,Any]:
        head=str(git_head).strip()
        if not _SHA_RE.fullmatch(head):return {'version':GITHUB_PROMOTION_VERIFIER_VERSION,'status':'INVALID_HEAD','verified':False,'head_sha':head,'defects':['head_must_be_hex_sha']}
        repo=self._repository()
        if not repo:return {'version':GITHUB_PROMOTION_VERIFIER_VERSION,'status':'VERIFIER_UNAVAILABLE','verified':False,'head_sha':head,'defects':['trusted_repository_not_configured'],'configuration':self.describe()}
        try:base=self._api_base()
        except Exception as exc:return {'version':GITHUB_PROMOTION_VERIFIER_VERSION,'status':'VERIFIER_UNAVAILABLE','verified':False,'head_sha':head,'defects':[f'api_configuration:{type(exc).__name__}:{exc}'],'configuration':self.describe()}
        owner,name=repo.split('/',1);url=f"{base}/repos/{urllib.parse.quote(owner,safe='')}/{urllib.parse.quote(name,safe='')}/commits/{head}/check-runs?per_page=100"
        headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'athena-promotion-verifier/1'};token=self._token()
        if token:headers['Authorization']=f'Bearer {token}'
        try:payload=self._fetch_json(url,headers,float(timeout_s))
        except Exception as exc:return {'version':GITHUB_PROMOTION_VERIFIER_VERSION,'status':'VERIFIER_ERROR','verified':False,'repository':repo,'head_sha':head,'defects':[f'github_fetch:{type(exc).__name__}:{exc}'],'url':url}
        trusted=[]
        for raw in list((payload or {}).get('check_runs') or []):
            snap=self._snapshot(raw)
            if str(snap.get('head_sha') or '')!=head or str(snap.get('app_slug') or '')!='github-actions':continue
            trusted.append(snap)
        run_id=self._run_id()
        if run_id:
            needle=f'/actions/runs/{run_id}/';trusted=[r for r in trusted if needle in str(r.get('details_url') or '') or needle in str(r.get('html_url') or '')]
        by_suite=defaultdict(list)
        for row in trusted:
            sid=row.get('check_suite_id')
            if sid is not None:by_suite[str(sid)].append(row)
        qualifying=[]
        for sid,rows in by_suite.items():
            by_name=defaultdict(list)
            for row in rows:by_name[str(row.get('name') or '')].append(row)
            chosen={};defects=[]
            for required in REQUIRED_CHECKS:
                good=[r for r in by_name.get(required,[]) if r.get('status')=='completed' and r.get('conclusion')=='success']
                if not good:defects.append(f'{required}_not_success')
                else:chosen[required]=sorted(good,key=lambda r:(str(r.get('completed_at') or ''),int(r.get('id') or 0)),reverse=True)[0]
            if not defects:qualifying.append((sid,chosen))
        if not qualifying:
            return {'version':GITHUB_PROMOTION_VERIFIER_VERSION,'status':'NO_QUALIFYING_CHECK_SUITE','verified':False,'repository':repo,'head_sha':head,'required_checks':list(REQUIRED_CHECKS),'trusted_app_slug':'github-actions','run_id':run_id,'defects':['no_single_trusted_suite_has_all_required_checks_completed_success'],'boundary':'checks from different suites/runs are never spliced together to manufacture qualification'}
        qualifying.sort(key=lambda item:int(item[0]) if str(item[0]).isdigit() else str(item[0]),reverse=True);suite_id,chosen=qualifying[0];smoke=chosen['smoke']
        verification_ref=f'github-check-suite://{repo}/{suite_id}'
        if run_id:verification_ref=f'github-actions-run://{repo}/{run_id}/suite/{suite_id}'
        ci_ref=verification_ref;smoke_ref=str(smoke.get('html_url') or smoke.get('details_url') or f'github-check-run://{smoke.get("id")}')
        ci={'observed':True,'ref':ci_ref,'head_sha':head,'conclusion':'success','source':'GITHUB_CHECK_RUNS_API','suite_id':suite_id,'run_id':run_id,'checks':{name:chosen[name] for name in REQUIRED_CHECKS if name!='smoke'}}
        sw={'observed':True,'ref':smoke_ref,'head_sha':head,'conclusion':'success','source':'GITHUB_CHECK_RUNS_API','suite_id':suite_id,'run_id':run_id,'check':smoke}
        receipt={'observed':True,'verifier':'GITHUB_CHECK_RUNS_API/github-actions','verification_ref':verification_ref,'head_sha':head,'ci_ref':ci_ref,'smoke_ref':smoke_ref,'repository':repo,'suite_id':suite_id,'run_id':run_id,'required_checks':list(REQUIRED_CHECKS)}
        return {'version':GITHUB_PROMOTION_VERIFIER_VERSION,'status':'VERIFIED','verified':True,'repository':repo,'head_sha':head,'run_id':run_id,'check_suite_id':suite_id,'required_checks':list(REQUIRED_CHECKS),'checks':chosen,'ci_witness':ci,'smoke_witness':sw,'trusted_external_verification':receipt,'verification_ref':verification_ref,'law':'one coherent host-trusted GitHub Actions suite independently observed all required checks completed success on the exact requested head'}

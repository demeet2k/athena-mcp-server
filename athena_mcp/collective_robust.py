from __future__ import annotations

import itertools
import json
import math
import random
import statistics
from typing import Any, Mapping, Sequence

from .collective_joint import CollectiveJointRuntime, _normal_logpdf, _softmax_logweights, _binary_value
from .collective_probabilistic import (
    _dot,
    _fit_logistic,
    _fisher_p,
    _logit,
    _mat_vec,
    _mean,
    _partial_corr,
    _predict_logistic,
    _rbf,
    _sigmoid,
)
from .collective_discovery import _inverse


def _vdc(index: int, base: int) -> float:
    n=max(1,int(index)); denom=1.0; out=0.0
    while n:
        n,rem=divmod(n,base);denom*=base;out+=rem/denom
    return out


def _qmc_loguniform(index: int, base: int, lo: float, hi: float) -> float:
    if lo<=0 or hi<=lo: raise ValueError('hyperparameter bounds require 0 < low < high')
    u=_vdc(index,base);return math.exp(math.log(lo)+u*(math.log(hi)-math.log(lo)))


def _weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    return sum(float(v)*float(w) for v,w in zip(values,weights))


def _fluctuation_epsilon(outcomes: Sequence[float], offsets: Sequence[float], clever: Sequence[float], iterations: int = 50) -> float:
    eps=0.0
    for _ in range(max(1,int(iterations))):
        score=0.0;info=0.0
        for y,o,h in zip(outcomes,offsets,clever):
            p=_sigmoid(float(o)+eps*float(h));score+=float(h)*(float(y)-p);info+=float(h)*float(h)*p*(1-p)
        if info<=1e-12: break
        step=max(-1.0,min(1.0,score/info));eps+=step
        if abs(step)<1e-9: break
    return max(-8.0,min(8.0,eps))


def _policy_action(spec: Any, row: Mapping[str, Any], label: str) -> int:
    if isinstance(spec,(int,float)):
        return int(_binary_value(spec,label))
    if not isinstance(spec,Mapping): raise ValueError(f'{label} policy must be binary or an object')
    score=float(spec.get('intercept',0.0));coefs=spec.get('coefficients') or {}
    if not isinstance(coefs,Mapping): raise ValueError(f'{label} coefficients must be an object')
    for k,v in coefs.items():
        if str(k) not in row: raise ValueError(f'{label} policy references missing feature {k}')
        score+=float(v)*float(row[str(k)])
    return 1 if score>=float(spec.get('threshold',0.0)) else 0


def _cov_psd(matrix: Sequence[Sequence[float]], tol: float = 1e-8) -> bool:
    n=len(matrix);L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            s=float(matrix[i][j])-sum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                if s < -tol: return False
                L[i][j]=math.sqrt(max(0.0,s))
            elif L[j][j]>tol:
                L[i][j]=s/L[j][j]
            elif abs(s)>tol:
                return False
    return True


class CollectiveRobustRuntime:
    """V13 continuous-domain approximation / robust causal-control layer.

    V13 deliberately does not claim unrestricted continuous Bayes, full FCI/RFCI,
    general longitudinal TMLE, general off-policy value, or general DRO. It adds
    bounded executable approximations with explicit model/authority firewalls.
    """

    def __init__(self, joint: CollectiveJointRuntime):
        self.joint=joint;self.adaptive=joint.adaptive;self.probabilistic=joint.probabilistic;self.s=joint.s

    def describe(self) -> dict[str,Any]:
        return {
            'version':'COLLECTIVE_RUNTIME_V13','persistent_surfaces':{},
            'operators':['gp_hyperqmc','gp_fitc_predict','gp_joint_design','fci_lite_discover','longitudinal_tmle','dynamic_policy_value','dro_resource_select'],
            'laws':[
                'QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES',
                'FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM',
                'JOINT_MODEL_INFORMATION_DESIGN != OBSERVATION',
                'BOUNDED_FCI_LITE != FCI_RFCI_PAG_THEOREM',
                'TWO_TIMEPOINT_SEQUENTIAL_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM_OR_IDENTIFICATION_PROOF',
                'DYNAMIC_GFORMULA_POLICY_VALUE != GENERAL_OFF_POLICY_CAUSAL_VALUE',
                'ELLIPSOIDAL_GAUSSIAN_ROBUST_PLAN != GENERAL_DISTRIBUTIONALLY_ROBUST_OPTIMIZATION',
            ],
        }

    # ---------- quasi-Monte-Carlo approximation to continuous GP hyperparameter Bayes ----------
    def gp_hyperqmc(self, context_key: str, bounds: Mapping[str,Any] | None = None, samples: int = 96, seed: int = 0) -> dict[str,Any]:
        row=self.probabilistic._gp_row(context_key);obs=json.loads(row['observations_json'])
        if len(obs)<3: raise ValueError('GP hyper-QMC requires at least three observed rows')
        cur={'length_scale':float(row['length_scale']),'signal_variance':float(row['signal_variance']),'noise_variance':float(row['noise_variance'])}
        b=dict(bounds or {})
        def interval(name,lo_factor=.25,hi_factor=4.0):
            raw=b.get(name,[cur[name]*lo_factor,cur[name]*hi_factor])
            if not isinstance(raw,Sequence) or isinstance(raw,(str,bytes)) or len(raw)!=2: raise ValueError(f'{name} bound must be [low,high]')
            lo=float(raw[0]);hi=float(raw[1])
            if lo<=0 or hi<=lo: raise ValueError(f'{name} bound requires 0 < low < high')
            return lo,hi
        bls=interval('length_scale');bsv=interval('signal_variance');bnv=interval('noise_variance')
        n=max(32,min(int(samples),512));offset=max(0,int(seed))*17+1;scored=[]
        for j in range(n):
            idx=offset+j
            ls=_qmc_loguniform(idx,2,*bls);sv=_qmc_loguniform(idx,3,*bsv);nv=_qmc_loguniform(idx,5,*bnv)
            try:lml=self.joint._lml(obs,ls,sv,nv)
            except Exception:continue
            scored.append({'length_scale':ls,'signal_variance':sv,'noise_variance':nv,'log_marginal_likelihood':lml})
        if len(scored)<8: raise ValueError('too few numerically valid hyper-QMC particles')
        weights=_softmax_logweights([r['log_marginal_likelihood'] for r in scored])
        for r,w in zip(scored,weights):r['posterior_weight']=w
        ess=1.0/sum(w*w for w in weights);entropy=-sum(w*math.log(max(w,1e-300),2) for w in weights)
        moments={}
        for k in ('length_scale','signal_variance','noise_variance'):
            vals=[float(r[k]) for r in scored];logs=[math.log(v) for v in vals];mu=_weighted_mean(vals,weights);lmu=_weighted_mean(logs,weights)
            moments[k]={'mean':round(mu,10),'geometric_mean':round(math.exp(lmu),10),'log_variance':round(_weighted_mean([(x-lmu)**2 for x in logs],weights),10)}
        top=sorted(scored,key=lambda r:r['posterior_weight'],reverse=True)[:min(64,len(scored))]
        return {'status':'QMC_CONTINUOUS_GP_HYPERPOSTERIOR_APPROXIMATION','context_key':str(context_key),'observation_count':len(obs),'sample_count':len(scored),'effective_sample_size':round(ess,10),'entropy_bits':round(entropy,10),'bounds':{'length_scale':list(bls),'signal_variance':list(bsv),'noise_variance':list(bnv)},'moments':moments,'particles':[{k:round(v,12) for k,v in r.items()} for r in top],
                'law':'Halton log-space quadrature approximates a continuous-domain log-uniform hyperparameter posterior over the declared box; finite QMC particles are not exact continuous Bayes or proof of the true kernel'}

    # ---------- FITC inducing-point GP approximation ----------
    def _inducing_indices(self, obs: Sequence[Mapping[str,Any]], m: int) -> list[int]:
        xs=[o['x'] for o in obs];m=max(1,min(int(m),min(48,len(xs))))
        if len(xs)<=m:return list(range(len(xs)))
        d=len(xs[0]);centroid=[sum(float(x[j]) for x in xs)/len(xs) for j in range(d)]
        def d2(a,b):return sum((float(a[j])-float(b[j]))**2 for j in range(d))
        first=max(range(len(xs)),key=lambda i:(d2(xs[i],centroid),-i));sel=[first];remaining=set(range(len(xs)))-{first}
        while len(sel)<m:
            nxt=max(remaining,key=lambda i:(min(d2(xs[i],xs[j]) for j in sel),-i));sel.append(nxt);remaining.remove(nxt)
        return sel

    def gp_fitc_predict(self, context_key: str, features: Mapping[str,Any], inducing_count: int = 16, include_observation_noise: bool = True) -> dict[str,Any]:
        row=self.probabilistic._gp_row(context_key);order=json.loads(row['feature_order_json']);obs=json.loads(row['observations_json'])
        if any(k not in features for k in order):raise ValueError('feature value required for every GP feature')
        if not obs:return {**self.probabilistic.gp_predict(context_key,features,include_observation_noise),'status':'FITC_GP_PRIOR','inducing_indices':[]}
        xq=[float(features[k]) for k in order];ls=float(row['length_scale']);sv=float(row['signal_variance']);nv=float(row['noise_variance'])
        sel=self._inducing_indices(obs,inducing_count);Z=[obs[i]['x'] for i in sel];m=len(Z);n=len(obs)
        Kmm=[[_rbf(Z[i],Z[j],ls,sv) for j in range(m)] for i in range(m)]
        for i in range(m):Kmm[i][i]+=1e-8
        Kmmi=_inverse(Kmm);Knm=[[_rbf(obs[i]['x'],Z[j],ls,sv) for j in range(m)] for i in range(n)]
        lam=[]
        for i in range(n):
            qii=_dot(Knm[i],_mat_vec(Kmmi,Knm[i]));lam.append(max(1e-9,sv-qii+nv))
        A=[row_[:] for row_ in Kmm];b=[0.0]*m
        for i in range(n):
            invl=1.0/lam[i];yi=float(obs[i]['y'])
            for a in range(m):
                b[a]+=Knm[i][a]*yi*invl
                for c in range(m):A[a][c]+=Knm[i][a]*Knm[i][c]*invl
        Ai=_inverse(A);alpha=_mat_vec(Ai,b);kxm=[_rbf(xq,Z[j],ls,sv) for j in range(m)];mean=_dot(kxm,alpha)
        qxx=_dot(kxm,_mat_vec(Kmmi,kxm));latent=max(0.0,sv-qxx+_dot(kxm,_mat_vec(Ai,kxm)));pred=latent+(nv if include_observation_noise else 0.0)
        exact=self.probabilistic.gp_predict(context_key,features,include_observation_noise)
        return {'status':'FITC_INDUCING_GP_APPROXIMATION','context_key':str(context_key),'observation_count':n,'inducing_count':m,'inducing_indices':sel,'mean':round(mean,10),'latent_variance':round(latent,10),'predictive_variance':round(pred,10),'std':round(math.sqrt(max(0.0,pred)),10),'complexity_proxy':{'full_gp':f'O({n}^3)','fitc':f'O({n}*{m}^2+{m}^3)'},'exact_reference':{'mean':exact.get('mean'),'predictive_variance':exact.get('predictive_variance'),'absolute_mean_error':round(abs(mean-float(exact.get('mean',0.0))),10),'absolute_variance_error':round(abs(pred-float(exact.get('predictive_variance',0.0))),10)},
                'law':'deterministic inducing-point FITC approximation preserves a diagonal conditional residual and exposes query-level exact-reference error; it is not the full GP posterior, a variational optimum, or a global error guarantee'}

    # ---------- joint model-discrimination + decision value ----------
    def gp_joint_design(self, context_key: str, actions: Sequence[Mapping[str,Any]], experiments: Sequence[Mapping[str,Any]], bounds: Mapping[str,Any] | None = None, hyper_samples: int = 64, mc_samples: int = 200, seed: int = 0, information_weight: float = 1.0, decision_weight: float = 1.0, cost_weight: float = 1.0, risk_weight: float = 1.0) -> dict[str,Any]:
        if not actions or not experiments:raise ValueError('actions and experiments must not be empty')
        if len(actions)>24 or len(experiments)>48:raise ValueError('too many joint GP actions/experiments')
        hp=self.gp_hyperqmc(context_key,bounds,hyper_samples,seed);row=self.probabilistic._gp_row(context_key);particles=hp['particles']
        weights=[float(p['posterior_weight']) for p in particles];z=sum(weights);weights=[w/z for w in weights]
        points=[a.get('features') or {} for a in actions]+[e.get('features') or {} for e in experiments];na=len(actions);models=[]
        for p,w in zip(particles,weights):
            means,cov=self.joint._gp_joint_model(row,points,float(p['length_scale']),float(p['signal_variance']),float(p['noise_variance']))
            models.append({'weight':w,'means':means,'cov':cov,'noise':float(p['noise_variance'])})
        def util(aidx:int, means_by_model:Sequence[float], ws:Sequence[float]):
            a=actions[aidx];mu=sum(float(ws[k])*float(means_by_model[k]) for k in range(len(ws)));return float(a.get('utility_offset',0.0))+float(a.get('utility_scale',1.0))*mu
        current_utils=[]
        for ai in range(na):current_utils.append(util(ai,[m['means'][ai] for m in models],weights))
        current_best=max(current_utils);prior_h=-sum(w*math.log(max(w,1e-300),2) for w in weights);rng=random.Random(int(seed));draws=max(80,min(int(mc_samples),1200));ranked=[]
        cumulative=[];s=0.0
        for w in weights:s+=w;cumulative.append(s)
        for ej,e in enumerate(experiments):
            idx=na+ej;gain=0.0;ig=0.0
            for _ in range(draws):
                u=rng.random();mi=next((k for k,c in enumerate(cumulative) if u<=c),len(cumulative)-1);md=models[mi];obsvar=max(1e-12,float(md['cov'][idx][idx])+float(e.get('noise_variance',md['noise'])));y=rng.gauss(float(md['means'][idx]),math.sqrt(obsvar))
                logs=[]
                for m,w in zip(models,weights):
                    vv=max(1e-12,float(m['cov'][idx][idx])+float(e.get('noise_variance',m['noise'])));logs.append(math.log(max(w,1e-300))+_normal_logpdf(y,float(m['means'][idx]),vv))
                post=_softmax_logweights(logs);post_h=-sum(w*math.log(max(w,1e-300),2) for w in post);ig+=prior_h-post_h
                updated=[]
                for ai in range(na):
                    mus=[]
                    for m in models:
                        vv=max(1e-12,float(m['cov'][idx][idx])+float(e.get('noise_variance',m['noise'])));mus.append(float(m['means'][ai])+float(m['cov'][ai][idx])/vv*(y-float(m['means'][idx])))
                    updated.append(util(ai,mus,post))
                gain+=max(updated)-current_best
            evsi=gain/draws;model_ig=max(0.0,ig/draws);cost=float(e.get('cost',0.0));risk=float(e.get('risk',0.0));feas=max(0.0,min(1.0,float(e.get('feasibility',1.0))));ethical=bool(e.get('ethical',True));score=feas*(float(decision_weight)*evsi+float(information_weight)*model_ig)-float(cost_weight)*cost-float(risk_weight)*risk
            ranked.append({'id':str(e.get('id',f'E{ej}')),'status':'ELIGIBLE' if ethical and feas>0 else 'BLOCKED','decision_evsi':round(evsi,10),'model_information_gain_bits':round(model_ig,10),'cost':cost,'risk':risk,'feasibility':feas,'score':round(score,10)})
        ranked.sort(key=lambda r:(r['score'],r['decision_evsi'],r['model_information_gain_bits'],r['id']),reverse=True);eligible=[r for r in ranked if r['status']=='ELIGIBLE']
        return {'decision':'JOINT_HYPERMODEL_GP_DESIGN_ONLY','context_key':str(context_key),'hyperposterior_status':hp['status'],'hyper_effective_sample_size':hp['effective_sample_size'],'current_best_expected_utility':round(current_best,10),'winner':eligible[0]['id'] if eligible else None,'ranked':ranked,
                'law':'joint design values both downstream decision improvement and expected reduction of QMC hypermodel entropy; all measurements and posterior updates are hypothetical and never become GP observations, evidence, or canonical authority'}

    # ---------- bounded FCI-lite structural candidate ----------
    def fci_lite_discover(self, samples: Sequence[Mapping[str,Any]], variables: Sequence[str] | None = None, alpha: float = .05, max_conditioning: int = 2) -> dict[str,Any]:
        if len(samples)<30:raise ValueError('FCI-lite requires at least thirty samples')
        vars_=[str(v) for v in (variables or sorted(samples[0].keys()))]
        if len(vars_)<3 or len(vars_)>8:raise ValueError('FCI-lite supports 3..8 variables')
        data={v:[] for v in vars_}
        for row in samples:
            for v in vars_:
                if v not in row:raise ValueError(f'missing variable {v}')
                data[v].append(float(row[v]))
        a=max(1e-6,min(.5,float(alpha)));mc=max(0,min(int(max_conditioning),3));edges={tuple(sorted((x,y))) for i,x in enumerate(vars_) for y in vars_[i+1:]};sep={};tests=0
        for x,y in sorted(list(edges)):
            others=[z for z in vars_ if z not in (x,y)];removed=False
            for k in range(mc+1):
                for cond in itertools.combinations(others,k):
                    r=_partial_corr(data[x],data[y],[data[z] for z in cond]);p=_fisher_p(r,len(samples),len(cond));tests+=1
                    if p>a:
                        edges.discard(tuple(sorted((x,y))));sep[(x,y)]=list(cond);sep[(y,x)]=list(cond);removed=True;break
                if removed:break
        marks={e:{e[0]:'circle',e[1]:'circle'} for e in edges};colliders=[]
        def adjacent(x,y):return tuple(sorted((x,y))) in edges
        for z in vars_:
            nbr=[x for x in vars_ if x!=z and adjacent(x,z)]
            for x,y in itertools.combinations(nbr,2):
                if adjacent(x,y):continue
                if z not in sep.get((x,y),[]):
                    ex=tuple(sorted((x,z)));ey=tuple(sorted((y,z)));marks[ex][z]='arrowhead';marks[ey][z]='arrowhead';colliders.append({'left':x,'middle':z,'right':y})
        changed=True;prop=0
        while changed and prop<32:
            changed=False;prop+=1
            for x,z,y in itertools.permutations(vars_,3):
                if len({x,z,y})<3 or adjacent(x,y) or not adjacent(x,z) or not adjacent(z,y):continue
                ex=tuple(sorted((x,z)));ey=tuple(sorted((z,y)))
                if marks[ex][z]=='arrowhead' and marks[ey][z]=='circle':
                    marks[ey][z]='tail';marks[ey][y]='arrowhead';changed=True
        out=[]
        for e in sorted(edges):out.append({'a':e[0],'b':e[1],'endpoint_a':marks[e][e[0]],'endpoint_b':marks[e][e[1]]})
        return {'status':'BOUNDED_FCI_LITE_CANDIDATE','n':len(samples),'variables':vars_,'alpha':a,'max_conditioning':mc,'ci_tests':tests,'conditioning_scope':'ALL_OBSERVED_VARIABLE_SUBSETS_UP_TO_BOUND','edges':out,'collider_candidates':colliders,'separation_sets':[{'a':x,'b':y,'conditioning':c} for (x,y),c in sorted(sep.items()) if x<y],
                'law':'global bounded observed-variable conditioning plus collider/R1 propagation is an FCI-inspired candidate only; it omits complete possible-d-sep, discriminating paths, full PAG rules, selection-bias semantics and completeness guarantees, and never mutates canonical JSPACE'}

    # ---------- two-timepoint sequential logistic TMLE ----------
    def _longitudinal_rows(self, samples, treatment1, intermediate, treatment2, outcome, baseline):
        base=[str(x) for x in (baseline or [])];rows=[]
        for src in samples:
            r={k:float(src[k]) for k in base};r['A1']=_binary_value(src[treatment1],treatment1);r['L1']=_binary_value(src[intermediate],intermediate);r['A2']=_binary_value(src[treatment2],treatment2);r['Y']=_binary_value(src[outcome],outcome);rows.append(r)
        return base,rows

    def longitudinal_tmle(self, samples: Sequence[Mapping[str,Any]], treatment1: str, intermediate: str, treatment2: str, outcome: str, baseline: Sequence[str] | None = None, regimes: Sequence[Mapping[str,Any]] | None = None, assumptions: Mapping[str,Any] | None = None, propensity_clip: float = .05) -> dict[str,Any]:
        if len(samples)<100:raise ValueError('two-timepoint sequential TMLE requires at least one hundred samples')
        assumptions=dict(assumptions or {})
        if assumptions.get('latent_confounding_possible') is True:return {'status':'UNIDENTIFIED_LATENT_CONFOUNDING_RISK','method':'TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE','assumptions':assumptions,'law':'declared latent confounding fails closed before effect estimation'}
        base,rows=self._longitudinal_rows(samples,treatment1,intermediate,treatment2,outcome,baseline);clip=max(.01,min(.25,float(propensity_clip)))
        g1=_fit_logistic(rows,'A1',base);g2=_fit_logistic(rows,'A2',base+['A1','L1']);q2=_fit_logistic(rows,'Y',base+['A1','L1','A2'])
        regs=list(regimes or [{'id':'00','a1':0,'a2':0},{'id':'01','a1':0,'a2':1},{'id':'10','a1':1,'a2':0},{'id':'11','a1':1,'a2':1}])
        if not regs or len(regs)>16:raise ValueError('regimes must contain 1..16 static treatment plans')
        results=[]
        for ri,reg in enumerate(regs):
            a1=_binary_value(reg.get('a1'),'regime a1');a2=_binary_value(reg.get('a2'),'regime a2');ys=[];offs=[];h2=[];q2_target=[]
            for r in rows:
                p1=_predict_logistic(g1,r,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));p2=_predict_logistic(g2,r,base+['A1','L1']);g2a=max(clip,min(1-clip,p2 if a2==1 else 1-p2));qobs=max(1e-7,min(1-1e-7,_predict_logistic(q2,r,base+['A1','L1','A2'])));ys.append(r['Y']);offs.append(_logit(qobs));h2.append((1.0 if r['A1']==a1 and r['A2']==a2 else 0.0)/(g1a*g2a))
            eps2=_fluctuation_epsilon(ys,offs,h2)
            pseudo=[]
            for r in rows:
                cf={**{k:r[k] for k in base},'A1':a1,'L1':r['L1'],'A2':a2};p1=_predict_logistic(g1,cf,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));p2=_predict_logistic(g2,cf,base+['A1','L1']);g2a=max(clip,min(1-clip,p2 if a2==1 else 1-p2));q=max(1e-7,min(1-1e-7,_predict_logistic(q2,cf,base+['A1','L1','A2'])));qt=_sigmoid(_logit(q)+eps2/(g1a*g2a));pseudo.append({**{k:r[k] for k in base},'A1':r['A1'],'Q':qt});q2_target.append(qt)
            q1=_fit_logistic(pseudo,'Q',base+['A1']);offs1=[];h1=[]
            for r,qt in zip(rows,q2_target):
                p1=_predict_logistic(g1,r,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));q=max(1e-7,min(1-1e-7,_predict_logistic(q1,{**{k:r[k] for k in base},'A1':r['A1']},base+['A1'])));offs1.append(_logit(q));h1.append((1.0 if r['A1']==a1 else 0.0)/g1a)
            eps1=_fluctuation_epsilon(q2_target,offs1,h1);vals=[]
            for r in rows:
                cf={**{k:r[k] for k in base},'A1':a1};p1=_predict_logistic(g1,cf,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));q=max(1e-7,min(1-1e-7,_predict_logistic(q1,cf,base+['A1'])));vals.append(_sigmoid(_logit(q)+eps1/g1a))
            results.append({'id':str(reg.get('id',f'R{ri}')),'a1':int(a1),'a2':int(a2),'estimated_risk':round(_mean(vals),10),'epsilon_stage2':round(eps2,10),'epsilon_stage1':round(eps1,10)})
        results.sort(key=lambda r:(r['estimated_risk'],r['id']),reverse=True);best=results[0];worst=results[-1]
        return {'status':'TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE_ESTIMATED_UNDER_ASSUMPTIONS','method':'TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE','n':len(rows),'baseline':base,'regimes':results,'highest_risk_regime':best['id'],'lowest_risk_regime':worst['id'],'risk_contrast':round(best['estimated_risk']-worst['estimated_risk'],10),'propensity_clip':clip,'assumptions':assumptions,
                'law':'two sequential logistic targeting steps provide a bounded two-timepoint static-regime TMLE implementation under sequential exchangeability/positivity/consistency/model conditions; this is not a general longitudinal-TMLE theorem, cross-fitted efficiency proof, randomized evidence, or identification proof'}

    # ---------- deterministic dynamic regime value through longitudinal g-formula ----------
    def dynamic_policy_value(self, samples: Sequence[Mapping[str,Any]], treatment1: str, intermediate: str, treatment2: str, outcome: str, policies: Sequence[Mapping[str,Any]], baseline: Sequence[str] | None = None, assumptions: Mapping[str,Any] | None = None) -> dict[str,Any]:
        if len(samples)<80:raise ValueError('dynamic policy value requires at least eighty samples')
        assumptions=dict(assumptions or {})
        if assumptions.get('latent_confounding_possible') is True:return {'status':'UNIDENTIFIED_LATENT_CONFOUNDING_RISK','method':'DYNAMIC_TWO_TIMEPOINT_GFORMULA','assumptions':assumptions,'law':'declared latent confounding fails closed before policy valuation'}
        if not policies or len(policies)>32:raise ValueError('policies must contain 1..32 policy objects')
        base,rows=self._longitudinal_rows(samples,treatment1,intermediate,treatment2,outcome,baseline);lfit=_fit_logistic(rows,'L1',base+['A1']);yfit=_fit_logistic(rows,'Y',base+['A1','L1','A2']);out=[]
        for pi,p in enumerate(policies):
            vals=[];a1ones=0;a2ones=0
            for r in rows:
                xb={k:r[k] for k in base};a1=_policy_action(p.get('a1',0),xb,'a1');a1ones+=a1;lr={**xb,'A1':a1};pL=_predict_logistic(lfit,lr,base+['A1']);v=0.0
                for l,pl in ((0,1-pL),(1,pL)):
                    hist={**xb,'A1':a1,'L1':l};a2=_policy_action(p.get('a2',0),hist,'a2');a2ones+=pl*a2;yr={**hist,'A2':a2};v+=pl*_predict_logistic(yfit,yr,base+['A1','L1','A2'])
                vals.append(v)
            out.append({'id':str(p.get('id',f'P{pi}')),'estimated_value':round(_mean(vals),10),'a1_rate':round(a1ones/len(rows),10),'expected_a2_rate':round(a2ones/len(rows),10)})
        out.sort(key=lambda r:(r['estimated_value'],r['id']),reverse=True)
        return {'status':'DYNAMIC_TWO_TIMEPOINT_GFORMULA_POLICY_VALUE_UNDER_ASSUMPTIONS','method':'DYNAMIC_TWO_TIMEPOINT_PARAMETRIC_GFORMULA','n':len(rows),'baseline':base,'winner':out[0]['id'],'policies':out,'assumptions':assumptions,
                'law':'deterministic threshold/linear policies are valued through the same bounded two-timepoint parametric longitudinal model; this is not general off-policy causal evaluation, dynamic-regime identification proof, or execution authorization'}

    # ---------- correlated Gaussian + ellipsoidal mean ambiguity resource control ----------
    def dro_resource_select(self, candidates: Sequence[Mapping[str,Any]], budgets: Mapping[str,Any], covariances: Mapping[str,Any], ambiguity_radius: float = 0.0, alpha: float = .05, exact_limit: int = 18) -> dict[str,Any]:
        items=list(candidates);n=len(items)
        if n<1 or n>24:raise ValueError('robust resource selector supports 1..24 candidates')
        resources=[str(r) for r in budgets]
        if not resources:raise ValueError('budgets must not be empty')
        z=statistics.NormalDist().inv_cdf(1-max(1e-6,min(.49,float(alpha))));rho=max(0.0,float(ambiguity_radius));means={};unc={};cov={}
        for r in resources:
            means[r]=[];unc[r]=[]
            for item in items:
                spec=(item.get('resources') or {}).get(r)
                if not isinstance(spec,Mapping) or 'mean' not in spec:raise ValueError(f'every candidate requires resource mean for {r}')
                means[r].append(float(spec['mean']));unc[r].append(max(0.0,float(spec.get('mean_uncertainty',0.0))))
            raw=(covariances or {}).get(r)
            if not isinstance(raw,Sequence) or len(raw)!=n or any(not isinstance(row,Sequence) or len(row)!=n for row in raw):raise ValueError(f'covariance for {r} must be an n x n matrix')
            mat=[[float(raw[i][j]) for j in range(n)] for i in range(n)]
            for i in range(n):
                if mat[i][i]<0:raise ValueError(f'covariance diagonal for {r} must be nonnegative')
                for j in range(n):
                    if abs(mat[i][j]-mat[j][i])>1e-8:raise ValueError(f'covariance for {r} must be symmetric')
            if not _cov_psd(mat):raise ValueError(f'covariance for {r} must be positive semidefinite')
            cov[r]=mat
        def evaluate(sel):
            detail={};ok=True
            for r in resources:
                mu=sum(means[r][i] for i in sel);delta=rho*math.sqrt(sum(unc[r][i]**2 for i in sel));var=sum(cov[r][i][j] for i in sel for j in sel);sd=math.sqrt(max(0.0,var));bound=mu+delta+z*sd;budget=float(budgets[r]);detail[r]={'mean':round(mu,10),'robust_mean_shift':round(delta,10),'std':round(sd,10),'one_sided_bound':round(bound,10),'budget':budget,'feasible':bound<=budget+1e-12};ok=ok and detail[r]['feasible']
            return ok,detail
        limit=max(1,min(int(exact_limit),18));best=None;checked=0
        if n<=limit:
            for mask in range(1<<n):
                sel=[i for i in range(n) if mask>>i&1];ok,detail=evaluate(sel);checked+=1
                if not ok:continue
                value=sum(float(items[i].get('value',0.0)) for i in sel);key=(value,-len(sel),tuple(str(items[i].get('id',i)) for i in sel))
                if best is None or key>best[0]:best=(key,sel,detail)
            sel=best[1] if best else [];detail=best[2] if best else evaluate([])[1];status='CORRELATED_GAUSSIAN_ELLIPSOIDAL_MEAN_ROBUST_EXACT_ENUMERATION';certificate='EXACT_ENUMERATION_UNDER_DECLARED_CORRELATED_GAUSSIAN_COVARIANCE_AND_ELLIPSOIDAL_MEAN_AMBIGUITY'
        else:
            order=sorted(range(n),key=lambda i:(float(items[i].get('value',0.0))/(1+sum(abs(means[r][i])+rho*unc[r][i] for r in resources)),-i),reverse=True);sel=[]
            for i in order:
                ok,_=evaluate(sel+[i])
                if ok:sel.append(i)
            detail=evaluate(sel)[1];status='CORRELATED_GAUSSIAN_ROBUST_GREEDY_NO_OPTIMALITY_CERTIFICATE';certificate=None;checked=None
        return {'status':status,'selected':[str(items[i].get('id',i)) for i in sel],'value':round(sum(float(items[i].get('value',0.0)) for i in sel),10),'alpha':float(alpha),'z':round(z,10),'ambiguity_radius':rho,'resources':detail,'checked_subsets':checked,'certificate':certificate,
                'law':'correlated Gaussian covariance plus ellipsoidal mean uncertainty yields a bounded robust chance approximation; exact enumeration is exact only for the declared finite ambiguity/model, while the large-n greedy fallback has no optimality certificate and neither is general distributionally robust optimization or execution'}

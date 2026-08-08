from __future__ import annotations

from typing import Any, Mapping, Sequence

from .collective_joint import _binary_value
from .collective_probabilistic import _fit_logistic,_logit,_mean,_predict_logistic,_sigmoid
from .collective_robust import _fluctuation_epsilon


def longitudinal_tmle(robust, samples: Sequence[Mapping[str,Any]], treatment1: str, intermediate: str, treatment2: str, outcome: str, baseline: Sequence[str] | None = None, regimes: Sequence[Mapping[str,Any]] | None = None, assumptions: Mapping[str,Any] | None = None, propensity_clip: float = .05) -> dict[str,Any]:
    """Two-timepoint sequential logistic targeting with history-preserving pseudo outcomes.

    Stage 2 is trained on observed histories. For a target static regime (a1,a2),
    Q2* is evaluated at A2=a2 while retaining each row's observed A1,L1 history;
    the stage-2 fluctuation clever covariate is zero for rows whose observed A1 is
    incompatible with target a1. Stage 1 then learns the targeted pseudo outcome
    against observed A1 before evaluating the final intervention A1=a1.
    """
    if len(samples)<100:raise ValueError('two-timepoint sequential TMLE requires at least one hundred samples')
    assumptions=dict(assumptions or {})
    if assumptions.get('latent_confounding_possible') is True:return {'status':'UNIDENTIFIED_LATENT_CONFOUNDING_RISK','method':'TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE','assumptions':assumptions,'law':'declared latent confounding fails closed before effect estimation'}
    base,rows=robust._longitudinal_rows(samples,treatment1,intermediate,treatment2,outcome,baseline);clip=max(.01,min(.25,float(propensity_clip)))
    g1=_fit_logistic(rows,'A1',base);g2=_fit_logistic(rows,'A2',base+['A1','L1']);q2=_fit_logistic(rows,'Y',base+['A1','L1','A2'])
    regs=list(regimes or [{'id':'00','a1':0,'a2':0},{'id':'01','a1':0,'a2':1},{'id':'10','a1':1,'a2':0},{'id':'11','a1':1,'a2':1}])
    if not regs or len(regs)>16:raise ValueError('regimes must contain 1..16 static treatment plans')
    results=[]
    for ri,reg in enumerate(regs):
        a1=_binary_value(reg.get('a1'),'regime a1');a2=_binary_value(reg.get('a2'),'regime a2');ys=[];offs=[];h2=[]
        for r in rows:
            p1=_predict_logistic(g1,r,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));p2=_predict_logistic(g2,r,base+['A1','L1']);g2a=max(clip,min(1-clip,p2 if a2==1 else 1-p2));qobs=max(1e-7,min(1-1e-7,_predict_logistic(q2,r,base+['A1','L1','A2'])));ys.append(r['Y']);offs.append(_logit(qobs));h2.append((1.0 if r['A1']==a1 and r['A2']==a2 else 0.0)/(g1a*g2a))
        eps2=_fluctuation_epsilon(ys,offs,h2)
        pseudo=[];q2_target=[]
        for r in rows:
            # Preserve observed first-stage history for stage-1 pseudo-outcome training.
            hist={**{k:r[k] for k in base},'A1':r['A1'],'L1':r['L1']}
            p1=_predict_logistic(g1,hist,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));p2=_predict_logistic(g2,hist,base+['A1','L1']);g2a=max(clip,min(1-clip,p2 if a2==1 else 1-p2));cf2={**hist,'A2':a2};q=max(1e-7,min(1-1e-7,_predict_logistic(q2,cf2,base+['A1','L1','A2'])));hcf=(1.0 if r['A1']==a1 else 0.0)/(g1a*g2a);qt=_sigmoid(_logit(q)+eps2*hcf);pseudo.append({**{k:r[k] for k in base},'A1':r['A1'],'Q':qt});q2_target.append(qt)
        q1=_fit_logistic(pseudo,'Q',base+['A1']);offs1=[];h1=[]
        for r in rows:
            p1=_predict_logistic(g1,r,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));q=max(1e-7,min(1-1e-7,_predict_logistic(q1,{**{k:r[k] for k in base},'A1':r['A1']},base+['A1'])));offs1.append(_logit(q));h1.append((1.0 if r['A1']==a1 else 0.0)/g1a)
        eps1=_fluctuation_epsilon(q2_target,offs1,h1);vals=[]
        for r in rows:
            cf1={**{k:r[k] for k in base},'A1':a1};p1=_predict_logistic(g1,cf1,base);g1a=max(clip,min(1-clip,p1 if a1==1 else 1-p1));q=max(1e-7,min(1-1e-7,_predict_logistic(q1,cf1,base+['A1'])));vals.append(_sigmoid(_logit(q)+eps1/g1a))
        results.append({'id':str(reg.get('id',f'R{ri}')),'a1':int(a1),'a2':int(a2),'estimated_risk':round(_mean(vals),10),'epsilon_stage2':round(eps2,10),'epsilon_stage1':round(eps1,10),'targeting_history':'STAGE2_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION'})
    results.sort(key=lambda r:(r['estimated_risk'],r['id']),reverse=True);best=results[0];worst=results[-1]
    return {'status':'TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE_ESTIMATED_UNDER_ASSUMPTIONS','method':'TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE','n':len(rows),'baseline':base,'regimes':results,'highest_risk_regime':best['id'],'lowest_risk_regime':worst['id'],'risk_contrast':round(best['estimated_risk']-worst['estimated_risk'],10),'propensity_clip':clip,'assumptions':assumptions,'targeting_history':'OBSERVED_A1_L1_RETAINED_FOR_STAGE2_PSEUDO_OUTCOME; A1_INTERVENTION_APPLIED_AT_STAGE1_EVALUATION',
            'law':'two sequential logistic targeting steps preserve observed first-stage histories when constructing stage-2 pseudo outcomes and then target/evaluate the first-stage intervention; the implementation remains a bounded two-timepoint static-regime estimator under sequential exchangeability/positivity/consistency/model conditions, not a general longitudinal-TMLE theorem, cross-fitted efficiency proof, randomized evidence, or identification proof'}

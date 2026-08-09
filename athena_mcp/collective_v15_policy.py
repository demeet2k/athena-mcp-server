from __future__ import annotations

from typing import Any, Mapping, Sequence

from .collective_calibrated import _fold_assignment, _std_error
from .collective_probabilistic import _fit_logistic, _mean, _predict_logistic
from .collective_v15_history import (
    policy_action_from_history,
    validate_longitudinal_baseline,
    validate_longitudinal_sample_values,
    validate_propensity_clip,
)


def sequential_dr_policy_crossfit(
    runtime,
    samples: Sequence[Mapping[str, Any]],
    treatment1: str,
    intermediate: str,
    treatment2: str,
    outcome: str,
    policies: Sequence[Mapping[str, Any]],
    baseline: Sequence[str] | None = None,
    assumptions: Mapping[str, Any] | None = None,
    propensity_clip: float = 0.05,
    folds: int = 2,
    seed: int = 0,
) -> dict[str, Any]:
    if len(samples) < 180:
        raise ValueError("cross-fitted sequential DR policy value requires at least one hundred eighty samples")
    if not policies or len(policies) > 32:
        raise ValueError("policies must contain 1..32 dynamic policies")
    assumptions=dict(assumptions or {})
    if assumptions.get("latent_confounding_possible") is True:
        return {
            "status":"UNIDENTIFIED_LATENT_CONFOUNDING_RISK",
            "method":"CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_AIPW",
            "assumptions":assumptions,
            "law":"declared latent confounding fails closed before policy valuation",
        }

    base=validate_longitudinal_baseline(baseline,treatment1,intermediate,treatment2,outcome)
    validate_longitudinal_sample_values(samples,base)
    _,rows=runtime._longitudinal_rows(samples,treatment1,intermediate,treatment2,outcome,base)
    clip=validate_propensity_clip(propensity_clip)
    assignment=_fold_assignment(len(rows),folds,seed)
    k=max(assignment)+1
    out=[]

    stage1_history=list(base)
    stage2_history=list(base)+["A1","L1"]
    policy_ids=[]

    for pi,policy in enumerate(policies):
        if not isinstance(policy,Mapping):
            raise ValueError("each dynamic policy must be an object")
        pid=str(policy.get("id",f"P{pi}"))
        if not pid:
            raise ValueError("policy ids must be non-empty")
        policy_ids.append(pid)
        if "a1" not in policy or "a2" not in policy:
            raise ValueError("each dynamic policy requires a1 and a2")

        # Validate the policy feature graph before fitting any nuisance model.
        # One representative row is sufficient because validation concerns names;
        # the helper then projects every actual row to the same history surface.
        policy_action_from_history(policy["a1"],rows[0],"a1",stage1_history)
        policy_action_from_history(policy["a2"],rows[0],"a2",stage2_history)

        psi_all: list[float | None]=[None]*len(rows)
        for fold in range(k):
            train=[rows[i] for i in range(len(rows)) if assignment[i]!=fold]
            test_idx=[i for i in range(len(rows)) if assignment[i]==fold]
            if len(train)<90 or not test_idx:
                raise ValueError("cross-fitting fold too small")

            g1=_fit_logistic(train,"A1",base)
            g2=_fit_logistic(train,"A2",base+["A1","L1"])
            q2=_fit_logistic(train,"Y",base+["A1","L1","A2"])

            pseudo=[]
            for row in train:
                a2pi=policy_action_from_history(policy["a2"],row,"a2",stage2_history)
                cf2={**row,"A2":a2pi}
                q2pi=max(0.0,min(1.0,_predict_logistic(q2,cf2,base+["A1","L1","A2"])))
                pseudo.append({**{name:row[name] for name in base},"A1":row["A1"],"Q":q2pi})
            q1=_fit_logistic(pseudo,"Q",base+["A1"])

            for i in test_idx:
                row=rows[i]
                a1pi=policy_action_from_history(policy["a1"],row,"a1",stage1_history)
                a2pi=policy_action_from_history(policy["a2"],row,"a2",stage2_history)

                p1=_predict_logistic(g1,row,base)
                g1obs=max(clip,min(1-clip,p1 if row["A1"]==1 else 1-p1))
                p2=_predict_logistic(g2,row,base+["A1","L1"])
                g2obs=max(clip,min(1-clip,p2 if row["A2"]==1 else 1-p2))

                q2obs=_predict_logistic(q2,row,base+["A1","L1","A2"])
                q2pi=_predict_logistic(q2,{**row,"A2":a2pi},base+["A1","L1","A2"])
                q1obs=_predict_logistic(q1,{**{name:row[name] for name in base},"A1":row["A1"]},base+["A1"])
                q1pi=_predict_logistic(q1,{**{name:row[name] for name in base},"A1":a1pi},base+["A1"])

                h1=(1.0 if row["A1"]==a1pi else 0.0)/g1obs
                h2=(1.0 if row["A1"]==a1pi and row["A2"]==a2pi else 0.0)/(g1obs*g2obs)
                psi_all[i]=q1pi+h1*(q2pi-q1obs)+h2*(row["Y"]-q2obs)

        if any(value is None for value in psi_all):
            raise RuntimeError("cross-fitted sequential DR assignment is incomplete")
        values=[float(value) for value in psi_all]
        estimate=_mean(values)
        se=_std_error(values)
        out.append({
            "id":pid,
            "estimated_value":round(estimate,10),
            "standard_error":round(se,10),
            "interval95":[round(estimate-1.96*se,10),round(estimate+1.96*se,10)],
        })

    if len(set(policy_ids))!=len(policy_ids):
        raise ValueError("policy ids must be unique")
    out.sort(key=lambda row:(row["estimated_value"],row["id"]),reverse=True)
    return {
        "status":"CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_AIPW_POLICY_VALUE_UNDER_ASSUMPTIONS",
        "method":"CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_AIPW",
        "n":len(rows),
        "folds":k,
        "cross_fitted":True,
        "baseline":base,
        "policy_history_firewall":{
            "a1_available_features":stage1_history,
            "a2_available_features":stage2_history,
            "forbidden_future_state":["A2","Y"],
        },
        "policies":out,
        "winner":out[0]["id"],
        "assumptions":assumptions,
        "propensity_clip":clip,
        "history_invariant":"A1_POLICY_USES_BASELINE_ONLY__A2_POLICY_USES_BASELINE_A1_L1_ONLY",
        "law":"out-of-fold nuisance predictions feed a bounded two-timepoint sequential AIPW score; policy actions are projected onto finite information available before each treatment, so cross-fitting cannot be bypassed by future/outcome look-ahead; sequential exchangeability, positivity, consistency/interference and general off-policy identification remain separate assumptions",
    }

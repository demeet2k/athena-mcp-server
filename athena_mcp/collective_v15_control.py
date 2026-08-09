from __future__ import annotations

import math
from typing import Any, Mapping, Sequence


def _finite(value: Any, label: str) -> float:
    x=float(value)
    if not math.isfinite(x):
        raise ValueError(f"{label} must be finite")
    return x


def _validate_gaussian_inputs(
    variables: Sequence[str],
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
) -> list[str]:
    names=[str(name) for name in variables]
    if not 1<=len(names)<=16 or len(set(names))!=len(names) or any(not name for name in names):
        raise ValueError("continuous joint Gaussian belief requires 1..16 unique non-empty variables")
    if len(mean)!=len(names):
        raise ValueError("mean length must match variables")
    for index,value in enumerate(mean):
        _finite(value,f"mean[{index}]")
    if len(covariance)!=len(names) or any(len(row)!=len(names) for row in covariance):
        raise ValueError("covariance must be square and match variables")
    for i,row in enumerate(covariance):
        for j,value in enumerate(row):
            _finite(value,f"covariance[{i}][{j}]")
    return names


def joint_gaussian_update(
    runtime,
    variables: Sequence[str],
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    observation: Mapping[str, Any],
) -> dict[str, Any]:
    names=_validate_gaussian_inputs(variables,mean,covariance)
    if not isinstance(observation,Mapping):
        raise ValueError("linear Gaussian observation must be an object")
    coefficients=observation.get("coefficients") or {}
    if not isinstance(coefficients,Mapping) or not coefficients:
        raise ValueError("linear Gaussian observation requires coefficients")
    unknown=sorted(str(name) for name in coefficients if str(name) not in set(names))
    if unknown:
        raise ValueError("observation coefficients reference unknown variables: "+", ".join(unknown))
    for name,value in coefficients.items():
        _finite(value,f"observation coefficient {name}")
    _finite(observation["value"],"observation value")
    noise=_finite(observation.get("noise_variance",0.0),"observation noise_variance")
    if noise<=0:
        raise ValueError("observation noise_variance must be positive")
    return runtime.joint_gaussian_update(variables,mean,covariance,observation)


def joint_gaussian_control(
    runtime,
    variables: Sequence[str],
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    actions: Sequence[Mapping[str, Any]],
    cvar_alpha: float=0.1,
    risk_weight: float=1.0,
    cost_weight: float=1.0,
) -> dict[str, Any]:
    names=_validate_gaussian_inputs(variables,mean,covariance)
    known=set(names)
    if not actions or len(actions)>64:
        raise ValueError("Gaussian control supports 1..64 linear actions")
    alpha=_finite(cvar_alpha,"cvar_alpha")
    if not 0.0<alpha<=0.5:
        raise ValueError("cvar_alpha must lie in (0,0.5]")
    rw=_finite(risk_weight,"risk_weight")
    cw=_finite(cost_weight,"cost_weight")
    if rw<0 or cw<0:
        raise ValueError("risk_weight and cost_weight must be non-negative")
    ids=[]
    for index,action in enumerate(actions):
        if not isinstance(action,Mapping):
            raise ValueError("Gaussian control action rows must be objects")
        aid=str(action.get("id",f"A{index}"))
        if not aid:
            raise ValueError("Gaussian control action ids must be non-empty")
        ids.append(aid)
        coefficients=action.get("coefficients") or {}
        if not isinstance(coefficients,Mapping):
            raise ValueError("action coefficients must be an object")
        unknown=sorted(str(name) for name in coefficients if str(name) not in known)
        if unknown:
            raise ValueError(f"action {aid} coefficients reference unknown variables: "+", ".join(unknown))
        for name,value in coefficients.items():
            _finite(value,f"action {aid} coefficient {name}")
        _finite(action.get("offset",0.0),f"action {aid} offset")
        cost=_finite(action.get("cost",0.0),f"action {aid} cost")
        if cost<0:
            raise ValueError("Gaussian control action cost must be non-negative")
    if len(set(ids))!=len(ids):
        raise ValueError("Gaussian control action ids must be unique")
    return runtime.joint_gaussian_control(variables,mean,covariance,actions,alpha,rw,cw)


def multistage_tv_dro_plan(
    runtime,
    states: Sequence[str],
    initial_state: str,
    actions_by_state: Mapping[str, Any],
    horizon: int,
    tv_radius: float,
    discount: float=1.0,
) -> dict[str, Any]:
    names=[str(state) for state in states]
    if not 1<=len(names)<=24 or len(set(names))!=len(names) or any(not state for state in names):
        raise ValueError("multistage TV-DRO requires 1..24 unique non-empty states")
    if str(initial_state) not in set(names):
        raise ValueError("initial_state must be in states")
    if not isinstance(actions_by_state,Mapping):
        raise ValueError("actions_by_state must be an object")
    extra=sorted(str(state) for state in actions_by_state if str(state) not in set(names))
    if extra:
        raise ValueError("actions_by_state contains unknown states: "+", ".join(extra))
    rho=_finite(tv_radius,"tv_radius")
    gamma=_finite(discount,"discount")
    if not 0.0<=rho<=1.0:
        raise ValueError("tv_radius must lie in [0,1]")
    if not 0.0<=gamma<=1.0:
        raise ValueError("discount must lie in [0,1]")

    known=set(names)
    for state in names:
        actions=actions_by_state.get(state)
        if not isinstance(actions,Sequence) or isinstance(actions,(str,bytes)) or not actions or len(actions)>16:
            raise ValueError(f"state {state} requires 1..16 actions")
        ids=[]
        for index,action in enumerate(actions):
            if not isinstance(action,Mapping):
                raise ValueError("action rows must be objects")
            aid=str(action.get("id",f"{state}.A{index}"))
            if not aid:
                raise ValueError("robust action ids must be non-empty")
            ids.append(aid)
            _finite(action.get("reward",0.0),f"reward for {state}/{aid}")
            transitions=action.get("transitions") or {}
            if not isinstance(transitions,Mapping):
                raise ValueError("action transitions must be an object")
            unknown=sorted(str(next_state) for next_state in transitions if str(next_state) not in known)
            if unknown:
                raise ValueError(f"action {state}/{aid} references unknown successor states: "+", ".join(unknown))
            probabilities=[]
            for next_state in names:
                p=_finite(transitions.get(next_state,0.0),f"transition {state}/{aid}->{next_state}")
                if p<0:
                    raise ValueError("transition probabilities must be non-negative")
                probabilities.append(p)
            if abs(sum(probabilities)-1.0)>1e-8:
                raise ValueError("each action transition distribution must sum to one")
        if len(set(ids))!=len(ids):
            raise ValueError(f"state {state} action ids must be unique")

    return runtime.multistage_tv_dro_plan(states,initial_state,actions_by_state,horizon,rho,gamma)

from __future__ import annotations

def call(runtime, name, a):
    if name == "athena_budget_record":
        return runtime.record_budget(a["run_key"], a["resources"], a.get("budget"), a.get("outcome"), a.get("scope", "global"), a.get("actor", "agent"))
    if name == "athena_budget_summary":
        return runtime.budget_summary(a.get("scope", "global"), a.get("limit", 200))
    if name == "athena_policy_state":
        return runtime.policy_state(a.get("scope", "global"))
    if name == "athena_policy_score":
        return runtime.policy_score(a["features"], a.get("scope", "global"))
    if name == "athena_policy_update":
        return runtime.policy_update(a["expected_version"], a["features"], a["observed_reward"], a.get("scope", "global"), a.get("actor", "agent"), a.get("learning_rate"), a.get("l2"))
    if name == "athena_policy_rollback":
        return runtime.policy_rollback(a["txid"], a["expected_version"], a.get("scope", "global"), a.get("actor", "agent"))
    if name == "athena_counterfactual_simulate":
        return runtime.counterfactual_simulate(a["candidates"], a.get("context"), a.get("scope", "global"))
    if name == "athena_elder_observe":
        return runtime.elder_observe(a["entity_id"], a["outcomes"], a.get("scope", "global"), a.get("actor", "agent"))
    if name == "athena_elder_rank":
        return runtime.elder_rank(a.get("scope", "global"), a.get("limit", 50), a.get("min_observations", 1))
    if name == "athena_antibody_record_outcome":
        return runtime.antibody_record_outcome(a["antibody_id"], a["outcome"], a.get("actor", "agent"))
    if name == "athena_antibody_evolve":
        return runtime.antibody_evolve(a["parent_id"], a["signature"], a["detector"], a["repair"], a.get("trigger"), a.get("evidence"), a.get("regression_refs"), a.get("ttl_hours"), a.get("scope", "global"), a.get("actor", "agent"))
    if name == "athena_antibody_select":
        return runtime.antibody_select(a["event"], a.get("tags"), a.get("scope"), a.get("threshold", 0.25), a.get("limit", 10))
    if name == "athena_pheromone_multiscale_reinforce":
        return runtime.pheromone_multiscale_reinforce(a["source_scale"], a["coordinates"], a["observations"], a.get("upward_decay", 0.72), a.get("downward_decay", 0.55), a.get("age"), a.get("evaporation_rate", 0.08), a.get("deposit_gain", 0.35), a.get("actor", "agent"))
    if name == "athena_pheromone_multiscale_field":
        return runtime.pheromone_multiscale_field(a.get("min_score", 0.0), a.get("limit", 500))
    raise KeyError(name)

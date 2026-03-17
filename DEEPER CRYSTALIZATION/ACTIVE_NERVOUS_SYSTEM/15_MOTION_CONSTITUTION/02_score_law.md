# MotionConstitution_L1 Score Law

Truth state: `NEAR-derived`

The fused scheduler law is frozen as:

$$
\Pi(q)=
\frac{
\mathrm{ClosureGain}(q)\cdot
\mathrm{HeartNeed}(q)\cdot
\mathrm{ReplayReadiness}(q)\cdot
\mathrm{IntegrationYield}(q)\cdot
\mathrm{OrganAdjacency}(q)\cdot
\mathrm{SeedValue}(q)
}{\mathrm{Cost}(q)+\mathrm{ReplayCost}(q)+\mathrm{Risk}(q)+\mathrm{FailureDebt}(q)+\mathrm{BranchBurden}(q)+\mathrm{ContradictionHeat}(q)}
$$

Urgency is modulated but never allowed to override legality:

$$
\Pi^*(q)=\Pi(q)\cdot(1+\beta\cdot\mathrm{PressureGradient}(q)), \qquad \beta=0.5.
$$

Default parameterization:

- all score weights begin at `1.0`
- `beta = 0.5`
- `truth_threshold = 0.55`
- `replay_threshold = 0.55`
- `branch_limit = 0.75`
- `activate_threshold = 0.12`

Truth readiness is carried as a gate rather than a numerator term. `v0` treats it as the membrane deciding whether witness burden has been satisfied strongly enough for activation.

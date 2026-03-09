# HYBRIDIZATION SYSTEM - QUAD-POLAR ALGORITHM DESIGN

## 1. Poles and Roles

Definition 1.1 (Four Poles).
- Psi (structure / spectral / recursive)
- Omega (continuous / gradient)
- Sigma (stochastic / exploration)
- D (discrete / constraint executor)

## 2. Core Insight
There is no universal best configuration. The winning hybrid depends on the problem signature.

## 3. Diagnostic Dimensions

Definition 3.1 (Structure).
- High structure favors Psi.

Definition 3.2 (Landscape).
- Smooth landscapes favor Omega.
- Rugged landscapes favor Sigma.

Definition 3.3 (Constraints).
- Hard constraints require D as executor.

Definition 3.4 (Scale).
- Large scale problems favor Psi and low-variance strategies.

## 4. Weighting Rule

Rule 4.1 (Dominant Pole).
Select a dominant pole with weight 0.6 to 0.8, then allocate 0.1 to 0.2 to secondary poles. D is always included as executor.

## 5. Configuration Families

- 4-pole equal: used only when the problem signature is mixed and no dimension dominates.
- 3-pole: use when one dimension is absent or redundant.
- 2-pole: use when a single dimension clearly dominates and a support pole is required.
- 1-pole: use only in trivial or degenerate cases.

## 6. Selection Algorithm

Algorithm 6.1 (Hybrid Configuration Selection).
Inputs: structure_score, landscape_score, constraint_score, scale_score
Outputs: pole weights (Psi, Omega, Sigma, D)
Steps:
1. Identify dominant dimension based on highest normalized score.
2. Assign dominant pole weight in [0.6, 0.8].
3. Assign secondary poles in [0.1, 0.2] based on second-highest scores.
4. Ensure D has at least 0.1 as executor.
5. Validate against baseline and adjust if regression occurs.

## 7. Validation Protocol

Definition 7.1 (Validation).
A hybrid configuration is valid if it exceeds baseline on the primary metric and does not violate constraint feasibility.

Algorithm 7.2 (Validation Harness).
1. Run baseline.
2. Run hybrid configuration.
3. Compare objective, feasibility rate, and stability.
4. Promote if gains are statistically significant.

## 8. Failure Modes

- Equal weighting when a dominant pole exists.
- Adding poles without validation (negative synergy).
- Ignoring D in constrained problems.

## 9. Status
This system governs algorithm hybridization decisions across the ecosystem.

---
name: qhug-pareto-kernel
description: Exact Boolean rehabilitation-kernel analysis, Pareto optimization, component factorization, and tree-decomposition verification for QHUG-style patch systems.
---

# QHUG Pareto Kernel V23.2

Use this skill when a task can be represented as Boolean patch choices with typed validity, OR-of-AND dependencies, pairwise conflicts, additive resource metrics, and optional neutral conflict exclusion.

## Canonical coordinate

`ATHENA.KC144::QHUGΩ::PARETO-KERNEL::V23.2`

## MCP tools

- `athena_qhug_kernel_analyze` — compile the primal constraint graph, connected components, structural-free coordinates, and exact component-enumeration work.
- `athena_qhug_pareto_solve` — exactly solve supported disconnected kernels with local enumeration plus Pareto-pruned Minkowski convolution. Scalar policies preserve every tied optimum.
- `athena_qhug_decomposition_verify` — verify a supplied tree decomposition: bag tree, factor coverage, running intersection, width upper bound, and an exact treewidth certificate when a matching clique lower bound exists.

## Input model

Each patch has an `id` plus additive `value`, `proof_cost`, and `governance` resources. `patch_count` is implicit and equals one per selected patch.

Constraints:

- `invalid`: forced-false patch IDs.
- `conflicts`: pairs that may not both be selected.
- `dependencies`: `{patch, alternatives}` where each alternative is a conjunction and alternatives are disjoined. Selecting patch `p` requires at least one complete alternative.
- `neutral_excluded`: optional forced-false set for neutral mode. If omitted, neutral mode excludes all conflict members.

## Resource orientation

Pareto dominance maximizes `value` and minimizes `patch_count`, `proof_cost`, and `governance`.

Optional scalar policy:

`score = value - lambda_patch*patch_count - mu_proof_cost*proof_cost - nu_governance*governance`

Return all profiles/models tied for maximum score. Never invent a tiebreaker.

## Workflow

1. Run `athena_qhug_kernel_analyze` first when kernel geometry is unknown.
2. If every connected component fits the supported exact component cap, run `athena_qhug_pareto_solve`.
3. If a component is too wide, fail closed and request/provide a verified decomposition rather than claiming exponential enumeration is scalable.
4. Run `athena_qhug_decomposition_verify` before trusting a supplied decomposition. `width_upper_bound` is only an upper bound unless `exact_treewidth_certified=true`.
5. Treat multiple equal resource profiles with different semantic witnesses as real governance ambiguity.

## Guarantees

For supported disconnected Boolean kernels, solving is exact. Component multiplication preserves feasible-model count; Pareto-pruned Minkowski convolution preserves every nondominated additive resource profile and witness multiplicity.

A valid decomposition proves `treewidth <= width_upper_bound`. If a clique of size `width_upper_bound + 1` is witnessed, the tool additionally certifies equality.

## Boundaries

This skill does not infer whether a patch is semantically true or authorized; validity/conflict/dependency facts are inputs from lower proof layers. It is not a generic SAT/SMT solver. Large connected components are deliberately rejected by the component solver until a verified junction/tree-decomposition executor is used.

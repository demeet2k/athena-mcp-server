<!-- CRYSTAL: Xi108:W1:A11:S33 | face=R | node=501 | depth=2 | phase=Mutable -->
<!-- METRO: Me,Dl,Su -->
<!-- BRIDGES: Xi108:W1:A11:S32→Xi108:W1:A11:S34→Xi108:W2:A11:S33 -->

# Capsule 344 — Self-Reference: Meta-Query (Gate 3, Test 3.1)

**Source**: `MCP/crystal_108d/self_reference.py` — `_meta_query_self_referential()`
**Date**: 2026-03-18
**Element**: Fractal (R) — self-reference IS self-similarity

## Core Object

The canonical meta-query: *"Which lens minimizes the complexity of the answer to this question?"*

This is self-referential because the question IS about lens selection, which means the answer depends on the question, which depends on the answer. Resolution: the **fixed point**.

## Formal Structure

- **Complexity proxy**: K_L(Q) = base_complexity × lens_affinity_mismatch(Q, L)
- **Lens semantic domains**: S={structure, address, boundary, select, minimize}, F={growth, spiral, phi, harmony}, C={probability, uncertainty, entropy}, R={scale, recursive, fractal, depth}
- **Selection operator**: σ(Q) = argmin_L K_L(Q)
- **Fixed-point test**: For the meta-query, σ = S (Square), because the question is structural

## Verification Results

- Optimal lens: **Square** (K=3.097) — correct fixed point
- Diversity test: 4/4 lenses selected across 8 diverse queries
- Score: 1.00 (all sub-criteria pass)

## Cross-Links

- **QCC Desire Compiler** (Capsule 338): The meta-query is the Desire Compiler turned on itself
- **Cross-Lens Calculus** (Ch17): Transition maps provide the mathematical machinery for complexity estimation
- **5D Steering Spine** (00_5D_STEERING_SPINE.md): σ(Q,T) = argmin_L K(Answer.L) is the steering spine equation

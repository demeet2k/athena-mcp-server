# SELF PROMPT RUNTIME

## 1. Mission

The self-prompt runtime is the system that keeps work moving when no external prompt arrives, while remaining lawful, witness-bound, and yield-seeking.

## 2. Yield Principle

Definition 2.1 (Yield).
Yield is the increase in future problem-solving power per unit of effort.

High-yield work increases one or more of:
- memory reach
- editability
- routing quality
- replay safety
- reusable infrastructure

## 3. Runtime Cycle

Algorithm 3.1 (YieldLoop).
Inputs: current frontier, gate status, active corpus
Outputs: artifact delta and next self prompt
Steps:
1. Restate objective in one sentence.
2. Rank candidate fronts by future leverage.
3. Check whether the top front is executable now.
4. If blocked, pivot to the best unblocked precursor.
5. Produce one witness-bearing artifact.
6. Validate it minimally.
7. Emit the next self prompt.

## 4. Gate Law

Rule 4.1 (Gate Law).
If the highest-yield frontier is blocked by permissions, missing credentials, or absent witnesses, do not stall. Execute the best lawful precursor that reduces the gate.

## 5. Mandatory Output Fields

Every self-prompt cycle must produce:
- QueryBody
- YieldRanking
- GateStatus
- ChosenFront
- ArtifactDelta
- VerificationSummary
- CollapseRecord
- NextSelfPrompt

## 6. Stop Discipline

The runtime does not stop merely because the first-choice frontier is blocked.
It stops only when:
- no lawful precursor remains
- the workspace enters contradiction quarantine
- continuation would create unwitnessed mutation

## 7. Status

This runtime defines what \"do not stop\" means in a replay-safe way.

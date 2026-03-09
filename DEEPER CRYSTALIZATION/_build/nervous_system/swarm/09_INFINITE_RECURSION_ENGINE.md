# INFINITE RECURSION ENGINE

## Purpose

This file defines the restart law for the nervous system. The system is not allowed to "finish" in the ordinary sense. Each completed pass must contract into a sharper frontier and then restart from the beginning.

## Core Law

Completion without re-entry is invalid.

Every pass must end by generating:
1. a stronger witness state than the pass inherited, or
2. a deeper scale choice than the pass inherited, or
3. a new frontier that reopens the corpus from the gate check

If none of these occur, the pass is shallow repetition.

## Pass Object

Represent each pass as:

`Pass_n = <Gate, AtlasWitness, Scale, Body, Family, Route, Truth, Delta, Frontier_{n+1}>`

Where:
- `Gate` = live Docs status
- `AtlasWitness` = current local evidence state
- `Scale` = golden, silver, bronze, or copper
- `Body` = current macro or active body
- `Family` = current manuscript or source family
- `Route` = rail and hub path
- `Truth` = OK, NEAR, AMBIG, or FAIL
- `Delta` = concrete artifacts produced this pass
- `Frontier_{n+1}` = the next starting point

## Engine Cycle

### Step 1: Gate Check
- test whether Google Docs credentials exist
- if blocked, record the blocker and continue locally

### Step 2: Atlas Witness Check
- prefer live atlas counts over stale summaries
- refresh body and family assumptions from actual indexed evidence

### Step 3: Scale Selection
- start at inherited scale
- if dissatisfaction <= 4/10, unresolved bodies remain collapsed, or no stronger witness is gained, escalate one scale level

### Step 4: Body Selection
- choose the highest-yield body at the active scale
- current bronze bodies come from `families\\CORPUS_BODY_TENSOR.md`

### Step 5: Family Selection
- choose one family inside the active body
- prefer families closest to the active manuscript frontier

### Step 6: Concrete Artifact Move
- create or update at least one routed markdown artifact
- the move must change the nervous system, not merely restate its intent

### Step 7: Verification
- confirm the gate result
- confirm the live witness used
- confirm the route placement
- confirm the restart frontier

### Step 8: Contraction
- write the pass delta into manifests and ledgers
- reduce the pass to the smallest viable restart seed

### Step 9: Re-entry
- begin again from Step 1 using the new frontier

## Dissatisfaction Escalation Law

User dissatisfaction is a valid control variable.

Interpretation:
- `8-10/10`: refine within current scale
- `5-7/10`: add witness or routing specificity
- `0-4/10`: the current scale is too shallow; deepen before polishing

Current inherited verdict:
- 2/10

Current consequence:
- bronze scale is active
- new swarm and restart artifacts are mandatory before summary refinement

## Non-Termination Discipline

The engine is infinite in intention but bounded in each pass.

A lawful pass may stop only at a clean boundary if it leaves:
1. updated manifests
2. updated ledgers
3. a specific next frontier
4. no false claim of completed total synthesis

## Shallow Loop Detector

The loop is degraded if any of the following hold:
1. the same family is named repeatedly without new witness
2. the same summary is rephrased without a new artifact
3. higher-dimensional language appears without a scale or address consequence
4. the pass ends with "done" but no `Frontier_{n+1}`

## Current Engine Verdict

The previous system had recursion language but not full restart mechanics. This engine fixes that by making every pass produce its own next beginning, grounded in live witness and explicit scale choice.

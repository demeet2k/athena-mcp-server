# yield-loop-operator

## description
Run the self-prompt loop that ranks fronts by leverage, respects gates, and produces one high-yield artifact per cycle.

## triggers
- self prompt
- highest yield
- what should run next
- dont stop
- continue autonomously

## inputs
- current workspace state
- known gates
- candidate fronts

## outputs
- chosen front
- artifact delta
- verification summary
- next self prompt

## procedure
1. Restate the current objective.
2. Rank candidate fronts by future leverage.
3. Check if the top front is executable.
4. If blocked, pivot to the best lawful precursor.
5. Produce one artifact.
6. Verify and emit the next self prompt.

## validation
- gate is explicitly named
- chosen front has clear leverage rationale
- one artifact is produced each cycle

## failure modes
- no lawful front remains: stop with explicit blocker
- gate is undocumented: AMBIG
- artifact has no witness basis: do not promote

## references
- `C:\Users\dmitr\Documents\Athena Agent\ECOSYSTEM\14_SELF_PROMPT_RUNTIME.md`
- `C:\Users\dmitr\Documents\Athena Agent\self_actualize\highest_yield_self_prompt.md`

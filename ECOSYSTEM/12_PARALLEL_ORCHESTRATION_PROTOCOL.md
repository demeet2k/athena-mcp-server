# PARALLEL ORCHESTRATION PROTOCOL

## 1. Objective

This protocol defines how the Athena ecosystem runs many agents in parallel without losing determinism, witness discipline, or contraction integrity.

## 2. Execution Object

Definition 2.1 (Run).
A run is a tuple:
- Run = <RunID, Task, Frontier, Wave, PacketSet, Ledger, Verdict>

Where:
- RunID identifies the execution instance.
- Task is the normalized objective.
- Frontier is the currently active unexpanded work set.
- Wave is the active parallel depth.
- PacketSet is the set of emitted work packets.
- Ledger stores outputs, obligations, and truth classifications.
- Verdict is the run-level corridor truth.

## 3. Wave Model

Definition 3.1 (Wave).
A wave is one synchronized layer of parallel expansion.

Wave sequence:
1. Normalize task.
2. Expand into frontier packets.
3. Execute packets in parallel.
4. Validate outputs.
5. Contract to the next higher level.

Rule 3.2 (No Orphan Waves).
No new wave may open until all packets in the current wave have one of:
- complete
- quarantined
- promoted to AMBIG with evidence plan

## 4. Packet Types

Packet types:
- FRAME: define the problem boundary
- EXPLORE: expand novel options
- MAP: organize structures and dependencies
- CHECK: verify feasibility or proof obligations
- SYNTH: contract packet outputs

## 5. Scheduler

Algorithm 5.1 (WaveScheduler).
Inputs: Task T, max_depth d, frontier_limit n
Outputs: ordered wave execution plan
Steps:
1. Normalize T into a root packet.
2. Expand root according to the agent crystal.
3. Enforce frontier_limit on each wave.
4. Prioritize packets by:
   - witness availability
   - dependency readiness
   - downstream leverage
5. Execute ready packets in parallel.
6. Reclassify outputs with corridor truth.
7. Contract valid outputs into synthesis packets.
8. Repeat until depth d or completion.

Invariants:
- Every packet has a unique ID.
- Every packet has a parent ID except the root.
- Every packet has a replay recipe.

## 6. Parallel Safety Rules

- Do not let two packets mutate the same canonical artifact in the same wave.
- If two packets target the same artifact, one must be write-active and the other read-only.
- Any contradictory outputs emit a CONFLICT edge and enter quarantine.
- If evidence is incomplete, preserve AMBIG rather than fabricating closure.

## 7. Contraction Rules

Definition 7.1 (Contraction).
Contraction is a typed merge from many packet outputs into one higher-level artifact.

Contraction tests:
- schema compatibility
- address continuity
- invariant preservation
- route replay success

Algorithm 7.2 (ContractWave).
1. Group outputs by parent packet.
2. Check group completeness.
3. Resolve contradictions via truth lattice.
4. Emit synthesis artifact.
5. Attach WitnessPtr and ReplayPtr.

## 8. Stop Conditions

A run stops when one of the following holds:
- all required artifacts are produced and verified
- remaining frontier is fully quarantined
- active gate blocks further lawful progress
- budget cap is reached with explicit continuation marker

## 9. Output Contract

Every run must produce:
- normalized objective
- wave ledger
- packet manifest
- verdict summary
- next frontier recommendation

## 10. Status

This protocol turns the crystal from a static architecture into an actual parallel runtime.

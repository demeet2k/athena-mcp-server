# Packet Schema

`WorkerPacket = { packet_id, lineage_addr, root_cell, task_body, input_refs, output_targets, truth_class, witness_ptrs, contraction_target }`

Every swarm packet must bind back to:

- one root cell
- one metro line
- one contraction target
- one restart seed

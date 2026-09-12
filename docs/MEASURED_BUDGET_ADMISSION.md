# Measured resource estimates and scheduler admission

Cost observations retain absent dimensions as unknown. A sample measuring only CPU does not measure tokens. Budget pressure and useful-output efficiency remain unknown unless all supplied budget dimensions were observed. A zero cap is a real cap: zero use has zero pressure, positive use saturates pressure.

Worker profiles replay immutable observation rows, using a separate sample count for each resource. This corrects legacy aggregate dilution without editing historical observations or changing existing table columns. A worker measured once at CPU=10 and once at tokens=100 has means CPU=10 and tokens=100, not CPU=5 and tokens=50. The worker/scope index supports streaming replay; profile calculation is linear in that worker's observation history and uses bounded aggregate memory. Historical stored pressure/efficiency fields remain original observations; current profile efficiency is recomputed from complete measurement/budget pairs.

Explicit partial estimates override their dimensions and retain observed estimates for other dimensions. Profiles report per-resource sample counts. A mean is an estimate, not an execution ceiling. Caller-supplied telemetry is not independently authenticated by this API; bind real measurements to their source receipts before using them for operational decisions.

All three bounded scheduler routes require every declared required capability and a known estimate for every constrained resource. Missing costs cannot pass even a positive budget, and a score penalty cannot establish feasibility. Explicit zero cost is distinct from missing cost. Duplicate task/worker identities are rejected. Unknown dimensions, negative/non-finite numbers and booleans fail validation instead of becoming free resources.

The V5 profile bridge now reads the actual cost_reliability field rather than dropping measured history after a missing-key exception. Task-level cost overrides are identified in the schedule receipt. The exact V6 scheduler certifies only its explicitly supplied finite cost model and rejects missing constrained costs; it does not turn cost estimates into measured runtime outcomes.

These outputs remain plans. Actual task admission still needs the execution contract, current native ownership, resource reservations/ceilings, cancellation and provider readback. Source qualification does not install this change into an existing MCP process.

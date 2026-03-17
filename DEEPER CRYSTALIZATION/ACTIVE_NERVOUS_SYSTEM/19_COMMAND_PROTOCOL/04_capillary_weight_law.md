# Capillary Weight Update Law

For each directed edge `i -> j`, the command protocol updates route strength as:

`C_next = rho * C_now + alpha * U + beta * F - gamma * D - delta * N`

Where:

- `rho = 0.92`
- `alpha = 0.35`
- `beta = 0.2`
- `gamma = 0.15`
- `delta = 0.1`

Interpretation:

- useful, frequent, low-latency paths strengthen
- noisy, duplicate, or slow paths decay

Maturity classes:

- `weak edge` below `0.75`
- `capillary` from `0.75` to below `1.75`
- `vein` at or above `1.75`

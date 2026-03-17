# Command Packet Schema

- Docs gate: `BLOCKED`
- Routing policy: `goal+salience+pheromone+coord`
- Claim mode: `first-lease (1200 ms)`

| Field | Status |
| --- | --- |
| event_id | required |
| ant_id | required |
| tag | required |
| goal | required |
| change | required |
| priority | required |
| confidence | required |
| earth_ts | required |
| liminal_ts | required |
| coord12 | required |
| parent | required |
| ttl | required |
| pheromone | required |
| state_hash | required |
| route_class | required |

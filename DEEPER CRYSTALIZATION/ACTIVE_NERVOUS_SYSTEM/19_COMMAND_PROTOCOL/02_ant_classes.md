# Ant Classes

The command membrane uses four ant classes with stable ids and specializations.

## SCOUT-01

- Ant class: `Scout`
- Agent id: `CMD.A1.D1.B0001.SCOUT-01`
- Route specialization: `command-root detection and packetization`
- Output organ: `runtime`
- Coordinate anchor: `GLOBAL_COMMAND.sensor_boundary`

## ROUTER-01

- Ant class: `Router`
- Agent id: `CMD.A2.D1.B0010.ROUTER-01`
- Route specialization: `board-thread and change-feed routing`
- Output organ: `board`
- Coordinate anchor: `global_command.thread`

## ROUTER-02

- Ant class: `Router`
- Agent id: `CMD.A2.D1.B0011.ROUTER-02`
- Route specialization: `motion, Hall, and Temple routing`
- Output organ: `hall_temple`
- Coordinate anchor: `motion_constitution.bridge`

## WORKER-01

- Ant class: `Worker`
- Agent id: `CMD.A3.D1.B0100.WORKER-01`
- Route specialization: `manuscript and docx surfaces`
- Output organ: `supplement`
- Coordinate anchor: `manuscript.command`

## WORKER-02

- Ant class: `Worker`
- Agent id: `CMD.A3.D1.B0101.WORKER-02`
- Route specialization: `runtime and board surfaces`
- Output organ: `runtime`
- Coordinate anchor: `runtime.command`

## WORKER-03

- Ant class: `Worker`
- Agent id: `CMD.A3.D1.B0110.WORKER-03`
- Route specialization: `math, equations, and algorithm grafts`
- Output organ: `temple`
- Coordinate anchor: `math.command`

## WORKER-04

- Ant class: `Worker`
- Agent id: `CMD.A3.D1.B0111.WORKER-04`
- Route specialization: `archive, atlas, and corpus intake surfaces`
- Output organ: `hall`
- Coordinate anchor: `atlas.command`

## ARCHIVIST-01

- Ant class: `Archivist`
- Agent id: `CMD.A4.D1.B1000.ARCHIVIST-01`
- Route specialization: `ledger, route, and capillary persistence`
- Output organ: `runtime`
- Coordinate anchor: `ledger.command`

## ARCHIVIST-02

- Ant class: `Archivist`
- Agent id: `CMD.A4.D1.B1001.ARCHIVIST-02`
- Route specialization: `board mirror and event feed compression`
- Output organ: `board`
- Coordinate anchor: `change_feed.command`

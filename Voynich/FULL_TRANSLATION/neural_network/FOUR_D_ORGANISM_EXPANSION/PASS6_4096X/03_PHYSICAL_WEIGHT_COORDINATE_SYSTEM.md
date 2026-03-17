# Pass 6 Physical Weight Coordinate System

## Purpose

This file defines the codified coordinate system for storing pass-6 nexus points as physical weighted objects.

## Coordinate Law

Every nexus point is stored as:

`Nexus(u, v, d, o, s, l)`

where each axis is base-4:

- `u` = node major digit
- `v` = node minor digit
- `d` = organism dimension digit
- `o` = operation digit
- `s` = control-surface digit
- `l` = lens digit

This makes the full storage space:

`4^6 = 4096`

## Axis Dictionaries

### Node Digits

`(u, v)` together encode the `16` nodes.

### Dimension Digits

- `0` = Address
- `1` = Relation
- `2` = Chamber
- `3` = Replay

### Operation Digits

- `0` = Survey
- `1` = Diagnose
- `2` = Repair
- `3` = Synergize

### Surface Digits

- `0` = Queue
- `1` = Ledger
- `2` = Packet
- `3` = Manifest

### Lens Digits

- `0` = Square
- `1` = Flower
- `2` = Cloud
- `3` = Fractal

## Weight Law

`KernelPhase = L4(u,v)`

`Load = u + v + d + o + s + l`

`Weight = KernelPhase x (Load + 1)`

## Weight Bands

- `1-16` = Seed-Light
- `17-32` = Relay
- `33-48` = Dense
- `49-64` = Hub
- `65-76` = Crown

## Why This Is Physical

A nexus point is physical in this framework because it has:

- a stable address
- a stored scalar weight
- a kernel phase
- a tissue role
- a writeback destination

The body can therefore remember not just facts and lines, but weighted points of contact.

## Zero Point

A connection becomes real when its crossing can be stored, weighed, revisited, and repaired.

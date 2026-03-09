# SYNAPSE LEDGER

## Purpose
Tracks all declared synapses (lawful relations between neurons) in the nervous system.

## Active Synapses

(none declared yet -- synapses will be created as neurons are promoted from capsules)

## Schema

See `70_SCHEMAS/02_SYNAPSE_SCHEMA.md` for the synapse YAML template.

## Rules

1. A synapse requires two existing neurons (src and dst)
2. The edge kind must be from the closed basis K
3. At least one metro line must carry the synapse
4. Truth class defaults to AMBIG until witness evidence promotes it

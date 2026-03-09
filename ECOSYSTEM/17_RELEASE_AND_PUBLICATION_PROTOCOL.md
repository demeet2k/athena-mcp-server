# RELEASE AND PUBLICATION PROTOCOL

## 1. Release Objective

A release packages a coherent, validated slice of the ecosystem for reuse, distribution, or downstream execution.

## 2. Release Conditions

A release candidate must satisfy:
- canonical addressing intact
- validation run completed
- migration notes included for changed semantics
- registry updated
- unresolved FAIL states excluded or quarantined

## 3. Publication Intents

Publication modes:
- internal working release
- external shareable release
- canonical reference release

Each mode determines whether `AppO` is included in route plans.

## 4. Release Checklist

1. verify file set completeness
2. check route determinism
3. ensure WitnessPtr and ReplayPtr coverage
4. update skill and version registries
5. emit release notes and known obligations

## 5. Handoff Packet

Every release should include:
- manifest
- source list
- validation summary
- migration summary
- next known obligations

## 6. Status

This protocol turns the ecosystem from a draft archive into a releasable system.

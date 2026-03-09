# CAPSULE SCHEMA

## 1. Definition

A corpus capsule is a markdown mirror of one indexed source document. It maps the source to the nervous system's chapters, regions, and metro lines.

## 2. Template

```markdown
# [Source Title]

capsule_id: CC-XXXX
source_path: [relative path from project root to original file]
source_type: docx | md | pdf | py | json | zip
domain: DEEPER CRYSTALIZATION | MATH | Voynich | NERUAL NETWORK | ECOSYSTEM | ...
family: [manuscript family from SOURCE_SURFACE_ATLAS]
region: R1 | R2 | ... | R8

## Core claim

[1-3 sentence summary of what this source contributes]

## Chapter mappings

[list of ChXX entries this source feeds into, with specific crystal tile slots]

## Key operators/concepts

[bullet list of the main ideas or operators this source introduces]

## Metro lines

[which metro lines this capsule rides on]

## Truth class

AMBIG | NEAR | OK

## Witness

[path(s) to supporting evidence or verification]
```

## 3. Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `capsule_id` | string | yes | Unique ID: `CC-XXXX` |
| `source_path` | string | yes | Relative path from project root |
| `source_type` | enum | yes | File format |
| `domain` | string | yes | Which project subdirectory |
| `family` | string | yes | Manuscript family grouping |
| `region` | string | yes | Primary corpus region (R1-R8) |
| Core claim | text | yes | Compressed contribution summary |
| Chapter mappings | list | yes | ChXX addresses this source feeds |
| Key operators | list | yes | Concepts introduced |
| Metro lines | list | yes | Which lines carry this content |
| Truth class | enum | yes | {OK, NEAR, AMBIG, FAIL} |
| Witness | list | no | Evidence paths |

## 4. Capsule Creation Rules

1. Create capsules only for **major surfaces** — significant documents, not every individual file.
2. Group related files (e.g., all AQM tomes) into one family capsule with sub-entries.
3. Every capsule must map to at least one chapter tile slot.
4. Default truth class is `AMBIG` until evidence promotes it.
5. Source paths must resolve to real files.

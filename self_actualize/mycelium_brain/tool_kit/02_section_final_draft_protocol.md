# Section Final Draft Protocol

## Mission

Take one user-supplied section and return only the final draft of that exact section.

## Drafting Law

The user input is a suggestion, not a ceiling.
The output must increase:

- rigor
- density
- sequencing
- internal theorem order
- algorithmic clarity
- routing clarity

## Mandatory Workflow

1. Attempt live Docs search first.
2. If blocked, record the exact gate.
3. Read strongest local mirrors only as needed.
4. Draft only the requested section.
5. Do not skip ahead.
6. End with the chapter or appendix name on its own line.

## Output Contract

The output must be:

- mathematically rigorous
- framework rigorous
- code or algorithm rigorous when appropriate
- final-draft only
- free of informal assistant commentary

## Section Surfaces

When a section becomes stable enough for local storage:

- place or update it in `self_actualize/manuscript_sections/`
- rebuild the master manuscript only after the section is ready for writeback

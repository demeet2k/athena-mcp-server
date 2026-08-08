# Prompt Runtime Module Model

The compiler consumes the brain-side manifest and module files; it does not duplicate their semantics inside MCP code. MCP provides mechanics: freshness, loading, ordering, digesting, CAS mutation, experiment persistence and activation/promotion.

This keeps the runtime generic while the Git brain remains free to add/retire/change cognitive modules without a new MCP release for every prompt edit.
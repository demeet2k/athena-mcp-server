from __future__ import annotations

from .orchestration_extract import TRANSFORM_ORDER

VERIFIED_WITNESS_SCHEMA={"type":"object","required":["verified","ref"],"properties":{"verified":{"const":True},"ref":{"type":"string","minLength":1}},"additionalProperties":True}
TRANSFORM_SCHEMA={"enum":list(TRANSFORM_ORDER)}

EXTRACTION_TOOLS=[
{"name":"athena_extraction_plan","description":"Create a bounded AOR SX.1 extraction run. Planning creates typed PLANNED work contracts only; it never fabricates semantic transform results.","inputSchema":{"type":"object","required":["seed_ref","seed"],"properties":{"seed_ref":{"type":"string","minLength":1},"seed":{},"transforms":{"type":"array","items":TRANSFORM_SCHEMA,"uniqueItems":True},"max_depth":{"type":"integer","minimum":0},"max_tasks_per_generation":{"type":"integer","minimum":1},"actor":{"type":"string"}},"additionalProperties":False}},
{"name":"athena_extraction_task","description":"Fetch one extraction task with its seed, transform contract, status and result refs.","inputSchema":{"type":"object","required":["task_id"],"properties":{"task_id":{"type":"string","minLength":1}},"additionalProperties":False}},
{"name":"athena_extraction_complete","description":"Complete one PLANNED extraction task with one or more actual outputs and a verified witness. Each output becomes an addressable EXTRES result; completion never implies those outputs are mutually equivalent.","inputSchema":{"type":"object","required":["task_id","outputs","witness"],"properties":{"task_id":{"type":"string","minLength":1},"outputs":{"type":"array","minItems":1},"witness":VERIFIED_WITNESS_SCHEMA,"actor":{"type":"string"}},"additionalProperties":False}},
{"name":"athena_extraction_fail","description":"Record a witnessed extraction-task failure with explicit reason. Failure creates evidence; it does not fabricate output.","inputSchema":{"type":"object","required":["task_id","reason","witness"],"properties":{"task_id":{"type":"string","minLength":1},"reason":{"type":"string","minLength":1},"witness":VERIFIED_WITNESS_SCHEMA,"actor":{"type":"string"}},"additionalProperties":False}},
{"name":"athena_extraction_result","description":"Fetch one witnessed extraction result payload and provenance.","inputSchema":{"type":"object","required":["result_id"],"properties":{"result_id":{"type":"string","minLength":1}},"additionalProperties":False}},
{"name":"athena_extraction_expand_result","description":"Use one witnessed EXTRES payload as a next-generation seed, bounded by the parent EXTRUN depth and task-per-generation limits. Expansion creates work contracts, not semantic results.","inputSchema":{"type":"object","required":["result_id"],"properties":{"result_id":{"type":"string","minLength":1},"transforms":{"type":"array","items":TRANSFORM_SCHEMA,"uniqueItems":True},"actor":{"type":"string"}},"additionalProperties":False}},
{"name":"athena_extraction_frontier","description":"Return only currently PLANNED tasks for an extraction run, ordered by depth/ordinal/id.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string","minLength":1}},"additionalProperties":False}},
{"name":"athena_extraction_run","description":"Fetch one extraction run and all task heads for replay/navigation.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string","minLength":1}},"additionalProperties":False}},
]
EXTRACTION_TOOL_NAMES={tool['name'] for tool in EXTRACTION_TOOLS}
EXTRACTION_RESOURCE={"uri":"athena://extraction","name":"AOR SX.1 Recursive Extraction Transform Bank","mimeType":"application/json"}

from __future__ import annotations

PROJECT_ATLAS_RESOURCE={
    "uri":"athena://project-atlas",
    "name":"KC144 Project Atlas V2 Query Surface",
    "mimeType":"application/json",
}

_HEAD={
    "type":["string","null"],
    "pattern":"^[0-9a-fA-F]{40}$",
}
_LIMIT={"type":"integer","minimum":1,"maximum":100}
_OFFSET={"type":"integer","minimum":0}
_COMMON_HEADS={
    "expected_head":_HEAD,
    "expected_runtime_head":_HEAD,
}

PROJECT_ATLAS_TOOLS=[
    {
        "name":"athena_project_atlas_summary",
        "description":"Return a bounded federated summary of configured Git, runtime-source Git and MCP coordinates with separate exact-head CAS.",
        "inputSchema":{
            "type":"object",
            "properties":dict(_COMMON_HEADS),
            "additionalProperties":False,
        },
    },
    {
        "name":"athena_project_resolve",
        "description":"Resolve one exact federated Project Atlas identifier (POID, Git path, full address, MCP name/locator, or native RETURN URI). Ambiguity and stale heads fail closed.",
        "inputSchema":{
            "type":"object",
            "required":["identifier"],
            "properties":{
                "identifier":{"type":"string","minLength":1,"maxLength":4096},
                **_COMMON_HEADS,
            },
            "additionalProperties":False,
        },
    },
    {
        "name":"athena_project_list",
        "description":"List a bounded deterministic page of federated Project Atlas records filtered by Git plane, native type, KC144 coordinates, directory, MCP kind, or POID prefix.",
        "inputSchema":{
            "type":"object",
            "properties":{
                **_COMMON_HEADS,
                "source":{"type":"string","enum":["all","git","configured_git","runtime_git","mcp"]},
                "path_prefix":{"type":"string","minLength":1,"maxLength":4096},
                "git_type":{"type":"string","minLength":1,"maxLength":128},
                "project_gid":{"type":"integer","minimum":1,"maximum":144},
                "project_row":{"type":"integer","minimum":1,"maximum":12},
                "project_col":{"type":"integer","minimum":1,"maximum":12},
                "reference_gid":{"type":"integer","minimum":1,"maximum":144},
                "directory":{"type":"string","maxLength":4096},
                "mcp_kind":{"type":"string","enum":["tool","prompt"]},
                "poid_prefix":{"type":"string","minLength":1,"maxLength":64},
                "offset":_OFFSET,
                "limit":_LIMIT,
            },
            "additionalProperties":False,
        },
    },
    {
        "name":"athena_project_route",
        "description":"Resolve exact source/destination records across configured Git, runtime Git and MCP planes, then return normal/toroidal KC144 navigation plus native RETURN witnesses.",
        "inputSchema":{
            "type":"object",
            "required":["src","dst"],
            "properties":{
                "src":{"type":"string","minLength":1,"maxLength":4096},
                "dst":{"type":"string","minLength":1,"maxLength":4096},
                "wrap":{"type":"boolean"},
                **_COMMON_HEADS,
            },
            "additionalProperties":False,
        },
    },
]

PROJECT_ATLAS_TOOL_NAMES={tool["name"] for tool in PROJECT_ATLAS_TOOLS}

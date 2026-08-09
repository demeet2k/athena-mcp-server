from __future__ import annotations

PROJECT_ATLAS_RESOURCE={
    "uri":"athena://project-atlas",
    "name":"KC144 Project Atlas V2 Query Surface",
    "mimeType":"application/json",
}

_HEAD={"type":["string","null"]}
_LIMIT={"type":"integer","minimum":1,"maximum":100}
_OFFSET={"type":"integer","minimum":0}

PROJECT_ATLAS_TOOLS=[
    {
        "name":"athena_project_atlas_summary",
        "description":"Return a bounded exact-head summary of the current Git/KC144/MCP Project Atlas without returning the full atlas.",
        "inputSchema":{
            "type":"object",
            "properties":{"expected_head":_HEAD},
            "additionalProperties":False,
        },
    },
    {
        "name":"athena_project_resolve",
        "description":"Resolve one exact Project Atlas identifier (POID, Git path, full address, MCP name/locator, or native RETURN URI). Ambiguity and stale heads fail closed.",
        "inputSchema":{
            "type":"object",
            "required":["identifier"],
            "properties":{
                "identifier":{"type":"string","minLength":1,"maxLength":4096},
                "expected_head":_HEAD,
            },
            "additionalProperties":False,
        },
    },
    {
        "name":"athena_project_list",
        "description":"List a bounded deterministic page of Project Atlas records filtered by native path/type, KC144 coordinates, directory, MCP kind, or POID prefix.",
        "inputSchema":{
            "type":"object",
            "properties":{
                "expected_head":_HEAD,
                "source":{"type":"string","enum":["all","git","mcp"]},
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
        "description":"Resolve exact source/destination Project Atlas records and return a deterministic normal or toroidal KC144 station route plus both native RETURN witnesses.",
        "inputSchema":{
            "type":"object",
            "required":["src","dst"],
            "properties":{
                "src":{"type":"string","minLength":1,"maxLength":4096},
                "dst":{"type":"string","minLength":1,"maxLength":4096},
                "wrap":{"type":"boolean"},
                "expected_head":_HEAD,
            },
            "additionalProperties":False,
        },
    },
]

PROJECT_ATLAS_TOOL_NAMES={tool["name"] for tool in PROJECT_ATLAS_TOOLS}
